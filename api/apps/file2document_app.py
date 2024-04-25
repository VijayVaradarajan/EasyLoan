#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
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
#  limitations under the License
#
from elasticsearch_dsl import Q

from api.db.db_models import File2Document
from api.db.services.file2document_service import File2DocumentService
from api.db.services.file_service import FileService

from flask import request
from flask_login import login_required, current_user
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.utils.api_utils import server_error_response, get_data_error_result, validate_request
from api.utils import get_uuid
from api.db import FileType
from api.db.services.document_service import DocumentService
from api.settings import RetCode
from api.utils.api_utils import get_json_result
from rag.nlp import search
from rag.utils import ELASTICSEARCH


@manager.route('/convert', methods=['POST'])
@login_required
@validate_request("file_ids", "kb_ids")
def convert():
    req = request.json
    kb_ids = req["kb_ids"]
    file_ids = req["file_ids"]
    file2documents = []
    # if not kb_ids:
    #     return get_json_result(
    #         data=False, retmsg='Lack of "KB ID"', retcode=RetCode.ARGUMENT_ERROR)
    try:
        for file_id in file_ids:
            File2DocumentService.delete_by_file_id(file_id)
            for kb_id in kb_ids:
                e, kb = KnowledgebaseService.get_by_id(kb_id)
                if not e:
                    return get_data_error_result(
                        retmsg="Can't find this knowledgebase!")
                e, file = FileService.get_by_id(file_id)
                if not e:
                    return get_data_error_result(
                        retmsg="Can't find this file!")

                doc = DocumentService.insert({
                    "id": get_uuid(),
                    "kb_id": kb.id,
                    "parser_id": kb.parser_id,
                    "parser_config": kb.parser_config,
                    "created_by": current_user.id,
                    "type": FileType.VIRTUAL,
                    "name": file.name,
                    "location": "",
                    "size": 0
                })
                file2document = File2DocumentService.insert({
                    "id": get_uuid(),
                    "file_id": file_id,
                    "document_id": doc.id,
                })
                file2documents.append(file2document.to_json())
        return get_json_result(data=file2documents)
    except Exception as e:
        return server_error_response(e)


@manager.route('/rm', methods=['POST'])
@login_required
@validate_request("file_ids")
def rm():
    req = request.json
    file_ids = req["file_ids"]
    if not file_ids:
        return get_json_result(
            data=False, retmsg='Lack of "Files ID"', retcode=RetCode.ARGUMENT_ERROR)
    try:
        for file_id in file_ids:
            informs = File2DocumentService.get_by_file_id(file_id)
            if not informs:
                return get_data_error_result(retmsg="Inform not found!")
            for inform in informs:
                if not inform:
                    return get_data_error_result(retmsg="Inform not found!")
                File2DocumentService.delete_by_file_id(file_id)
                doc_id = inform.document_id
                e, doc = DocumentService.get_by_id(doc_id)
                if not e:
                    return get_data_error_result(retmsg="Document not found!")
                tenant_id = DocumentService.get_tenant_id(doc_id)
                if not tenant_id:
                    return get_data_error_result(retmsg="Tenant not found!")
                ELASTICSEARCH.deleteByQuery(
                    Q("match", doc_id=doc.id), idxnm=search.index_name(tenant_id))
                DocumentService.increment_chunk_num(
                    doc.id, doc.kb_id, doc.token_num * -1, doc.chunk_num * -1, 0)
                if not DocumentService.delete(doc):
                    return get_data_error_result(
                        retmsg="Database error (Document removal)!")
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)
