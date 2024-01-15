#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import pathlib

from elasticsearch_dsl import Q
from flask import request
from flask_login import login_required, current_user

from rag.nlp import search
from rag.utils import ELASTICSEARCH
from web_server.db.services import duplicate_name
from web_server.db.services.kb_service import KnowledgebaseService
from web_server.db.services.user_service import TenantService
from web_server.utils.api_utils import server_error_response, get_data_error_result, validate_request
from web_server.utils import get_uuid, get_format_time
from web_server.db import StatusEnum, FileType
from web_server.db.services.document_service import DocumentService
from web_server.settings import RetCode
from web_server.utils.api_utils import get_json_result
from rag.utils.minio_conn import MINIO
from web_server.utils.file_utils import filename_type


@manager.route('/upload', methods=['POST'])
@login_required
@validate_request("kb_id")
def upload():
    kb_id = request.form.get("kb_id")
    if not kb_id:
        return get_json_result(
            data=False, retmsg='Lack of "KB ID"', retcode=RetCode.ARGUMENT_ERROR)
    if 'file' not in request.files:
        return get_json_result(
            data=False, retmsg='No file part!', retcode=RetCode.ARGUMENT_ERROR)
    file = request.files['file']
    if file.filename == '':
        return get_json_result(
            data=False, retmsg='No file selected!', retcode=RetCode.ARGUMENT_ERROR)

    try:
        e, kb = KnowledgebaseService.get_by_id(kb_id)
        if not e:
            return get_data_error_result(
                retmsg="Can't find this knowledgebase!")

        filename = duplicate_name(
            DocumentService.query,
            name=file.filename,
            kb_id=kb.id)
        location = filename
        while MINIO.obj_exist(kb_id, location):
            location += "_"
        blob = request.files['file'].read()
        MINIO.put(kb_id, filename, blob)
        doc = DocumentService.insert({
            "id": get_uuid(),
            "kb_id": kb.id,
            "parser_id": kb.parser_id,
            "created_by": current_user.id,
            "type": filename_type(filename),
            "name": filename,
            "location": location,
            "size": len(blob)
        })
        return get_json_result(data=doc.to_json())
    except Exception as e:
        return server_error_response(e)


@manager.route('/create', methods=['POST'])
@login_required
@validate_request("name", "kb_id")
def create():
    req = request.json
    kb_id = req["kb_id"]
    if not kb_id:
        return get_json_result(
            data=False, retmsg='Lack of "KB ID"', retcode=RetCode.ARGUMENT_ERROR)

    try:
        e, kb = KnowledgebaseService.get_by_id(kb_id)
        if not e:
            return get_data_error_result(
                retmsg="Can't find this knowledgebase!")

        if DocumentService.query(name=req["name"], kb_id=kb_id):
            return get_data_error_result(
                retmsg="Duplicated document name in the same knowledgebase.")

        doc = DocumentService.insert({
            "id": get_uuid(),
            "kb_id": kb.id,
            "parser_id": kb.parser_id,
            "created_by": current_user.id,
            "type": FileType.VIRTUAL,
            "name": req["name"],
            "location": "",
            "size": 0
        })
        return get_json_result(data=doc.to_json())
    except Exception as e:
        return server_error_response(e)


@manager.route('/list', methods=['GET'])
@login_required
def list():
    kb_id = request.args.get("kb_id")
    if not kb_id:
        return get_json_result(
            data=False, retmsg='Lack of "KB ID"', retcode=RetCode.ARGUMENT_ERROR)
    keywords = request.args.get("keywords", "")

    page_number = request.args.get("page", 1)
    items_per_page = request.args.get("page_size", 15)
    orderby = request.args.get("orderby", "create_time")
    desc = request.args.get("desc", True)
    try:
        docs = DocumentService.get_by_kb_id(
            kb_id, page_number, items_per_page, orderby, desc, keywords)
        return get_json_result(data=docs)
    except Exception as e:
        return server_error_response(e)


@manager.route('/change_status', methods=['POST'])
@login_required
@validate_request("doc_id", "status")
def change_status():
    req = request.json
    if str(req["status"]) not in ["0", "1"]:
        get_json_result(
            data=False,
            retmsg='"Status" must be either 0 or 1!',
            retcode=RetCode.ARGUMENT_ERROR)

    try:
        e, doc = DocumentService.get_by_id(req["doc_id"])
        if not e:
            return get_data_error_result(retmsg="Document not found!")
        e, kb = KnowledgebaseService.get_by_id(doc.kb_id)
        if not e:
            return get_data_error_result(
                retmsg="Can't find this knowledgebase!")

        if not DocumentService.update_by_id(
                req["doc_id"], {"status": str(req["status"])}):
            return get_data_error_result(
                retmsg="Database error (Document update)!")

        if str(req["status"]) == "0":
            ELASTICSEARCH.updateScriptByQuery(Q("term", doc_id=req["doc_id"]),
                                              scripts="""
                                           if(ctx._source.kb_id.contains('%s'))
                                             ctx._source.kb_id.remove(
                                                 ctx._source.kb_id.indexOf('%s')
                                           );
                                        """ % (doc.kb_id, doc.kb_id),
                                              idxnm=search.index_name(
                                                  kb.tenant_id)
                                              )
        else:
            ELASTICSEARCH.updateScriptByQuery(Q("term", doc_id=req["doc_id"]),
                                              scripts="""
                                           if(!ctx._source.kb_id.contains('%s'))
                                             ctx._source.kb_id.add('%s');
                                        """ % (doc.kb_id, doc.kb_id),
                                              idxnm=search.index_name(
                                                  kb.tenant_id)
                                              )
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route('/rm', methods=['POST'])
@login_required
@validate_request("doc_id")
def rm():
    req = request.json
    try:
        e, doc = DocumentService.get_by_id(req["doc_id"])
        if not e:
            return get_data_error_result(retmsg="Document not found!")
        if not DocumentService.delete_by_id(req["doc_id"]):
            return get_data_error_result(
                retmsg="Database error (Document removal)!")
        e, kb = KnowledgebaseService.get_by_id(doc.kb_id)
        MINIO.rm(kb.id, doc.location)
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route('/rename', methods=['POST'])
@login_required
@validate_request("doc_id", "name", "old_name")
def rename():
    req = request.json
    if pathlib.Path(req["name"].lower()).suffix != pathlib.Path(
            req["old_name"].lower()).suffix:
        get_json_result(
            data=False,
            retmsg="The extension of file can't be changed",
            retcode=RetCode.ARGUMENT_ERROR)

    try:
        e, doc = DocumentService.get_by_id(req["doc_id"])
        if not e:
            return get_data_error_result(retmsg="Document not found!")
        if DocumentService.query(name=req["name"], kb_id=doc.kb_id):
            return get_data_error_result(
                retmsg="Duplicated document name in the same knowledgebase.")

        if not DocumentService.update_by_id(
                req["doc_id"], {"name": req["name"]}):
            return get_data_error_result(
                retmsg="Database error (Document rename)!")

        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)
