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
#  limitations under the License.
#
import re

from flask import request
from flask_login import login_required
from api.db.services.dialog_service import DialogService, ConversationService
from api.db import LLMType
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.llm_service import LLMService, LLMBundle
from api.settings import access_logger
from api.utils.api_utils import server_error_response, get_data_error_result, validate_request
from api.utils import get_uuid
from api.utils.api_utils import get_json_result
from rag.llm import ChatModel
from rag.nlp import retrievaler
from rag.nlp.search import index_name
from rag.utils import num_tokens_from_string, encoder


@manager.route('/set', methods=['POST'])
@login_required
@validate_request("dialog_id")
def set():
    req = request.json
    conv_id = req.get("conversation_id")
    if conv_id:
        del req["conversation_id"]
        try:
            if not ConversationService.update_by_id(conv_id, req):
                return get_data_error_result(retmsg="Conversation not found!")
            e, conv = ConversationService.get_by_id(conv_id)
            if not e:
                return get_data_error_result(
                    retmsg="Fail to update a conversation!")
            conv = conv.to_dict()
            return get_json_result(data=conv)
        except Exception as e:
            return server_error_response(e)

    try:
        e, dia = DialogService.get_by_id(req["dialog_id"])
        if not e:
            return get_data_error_result(retmsg="Dialog not found")
        conv = {
            "id": get_uuid(),
            "dialog_id": req["dialog_id"],
            "name": "New conversation",
            "message": [{"role": "assistant", "content": dia.prompt_config["prologue"]}]
        }
        ConversationService.save(**conv)
        e, conv = ConversationService.get_by_id(conv["id"])
        if not e:
            return get_data_error_result(retmsg="Fail to new a conversation!")
        conv = conv.to_dict()
        return get_json_result(data=conv)
    except Exception as e:
        return server_error_response(e)


@manager.route('/get', methods=['GET'])
@login_required
def get():
    conv_id = request.args["conversation_id"]
    try:
        e, conv = ConversationService.get_by_id(conv_id)
        if not e:
            return get_data_error_result(retmsg="Conversation not found!")
        conv = conv.to_dict()
        return get_json_result(data=conv)
    except Exception as e:
        return server_error_response(e)


@manager.route('/rm', methods=['POST'])
@login_required
def rm():
    conv_ids = request.json["conversation_ids"]
    try:
        for cid in conv_ids:
            ConversationService.delete_by_id(cid)
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)

@manager.route('/list', methods=['GET'])
@login_required
def list():
    dialog_id = request.args["dialog_id"]
    try:
        convs = ConversationService.query(dialog_id=dialog_id)
        convs = [d.to_dict() for d in convs]
        return get_json_result(data=convs)
    except Exception as e:
        return server_error_response(e)


def message_fit_in(msg, max_length=4000):
    def count():
        nonlocal msg
        tks_cnts = []
        for m in msg:tks_cnts.append({"role": m["role"], "count": num_tokens_from_string(m["content"])})
        total = 0
        for m in tks_cnts: total += m["count"]
        return total

    c = count()
    if c < max_length: return c, msg
    msg = [m for m in msg if m.role in ["system", "user"]]
    c = count()
    if c < max_length:return c, msg
    msg_ = [m for m in msg[:-1] if m.role == "system"]
    msg_.append(msg[-1])
    msg = msg_
    c = count()
    if c < max_length:return c, msg
    ll = num_tokens_from_string(msg_[0].content)
    l = num_tokens_from_string(msg_[-1].content)
    if ll/(ll + l) > 0.8:
        m = msg_[0].content
        m = encoder.decode(encoder.encode(m)[:max_length-l])
        msg[0].content = m
        return max_length, msg

    m = msg_[1].content
    m = encoder.decode(encoder.encode(m)[:max_length-l])
    msg[1].content = m
    return max_length, msg


@manager.route('/completion', methods=['POST'])
@login_required
@validate_request("dialog_id", "messages")
def completion():
    req = request.json
    msg = []
    for m in req["messages"]:
        if m["role"] == "system":continue
        if m["role"] == "assistant" and not msg:continue
        msg.append({"role": m["role"], "content": m["content"]})
    try:
        e, dia = DialogService.get_by_id(req["dialog_id"])
        if not e:
            return get_data_error_result(retmsg="Dialog not found!")
        del req["dialog_id"]
        del req["messages"]
        return get_json_result(data=chat(dia, msg, **req))
    except Exception as e:
        return server_error_response(e)


def chat(dialog, messages, **kwargs):
    assert messages[-1]["role"] == "user", "The last content of this conversation is not from user."
    llm = LLMService.query(llm_name=dialog.llm_id)
    if not llm:
        raise LookupError("LLM(%s) not found"%dialog.llm_id)
    llm = llm[0]
    question = messages[-1]["content"]
    embd_mdl = LLMBundle(dialog.tenant_id, LLMType.EMBEDDING)
    chat_mdl = LLMBundle(dialog.tenant_id, LLMType.CHAT, dialog.llm_id)

    field_map = KnowledgebaseService.get_field_map(dialog.kb_ids)
    ## try to use sql if field mapping is good to go
    if field_map:
        markdown_tbl,chunks = use_sql(question, field_map, dialog.tenant_id, chat_mdl)
        if markdown_tbl:
            return {"answer": markdown_tbl, "retrieval": {"chunks": chunks}}

    prompt_config = dialog.prompt_config
    for p in prompt_config["parameters"]:
        if p["key"] == "knowledge":continue
        if p["key"] not in kwargs and not p["optional"]:raise KeyError("Miss parameter: " + p["key"])
        if p["key"] not in kwargs:
            prompt_config["system"] = prompt_config["system"].replace("{%s}"%p["key"], " ")

    kbinfos = retrievaler.retrieval(question, embd_mdl, dialog.tenant_id, dialog.kb_ids, 1, dialog.top_n, dialog.similarity_threshold,
                        dialog.vector_similarity_weight, top=1024, aggs=False)
    knowledges = [ck["content_with_weight"] for ck in kbinfos["chunks"]]

    if not knowledges and prompt_config["empty_response"]:
        return {"answer": prompt_config["empty_response"], "retrieval": kbinfos}

    kwargs["knowledge"] = "\n".join(knowledges)
    gen_conf = dialog.llm_setting[dialog.llm_setting_type]
    msg = [{"role": m["role"], "content": m["content"]} for m in messages if m["role"] != "system"]
    used_token_count, msg = message_fit_in(msg, int(llm.max_tokens * 0.97))
    if "max_tokens" in gen_conf:
        gen_conf["max_tokens"] = min(gen_conf["max_tokens"], llm.max_tokens - used_token_count)
    answer = chat_mdl.chat(prompt_config["system"].format(**kwargs), msg, gen_conf)

    answer = retrievaler.insert_citations(answer,
                                 [ck["content_ltks"] for ck in kbinfos["chunks"]],
                                 [ck["vector"] for ck in kbinfos["chunks"]],
                                 embd_mdl,
                                 tkweight=1-dialog.vector_similarity_weight,
                                 vtweight=dialog.vector_similarity_weight)
    for c in kbinfos["chunks"]:
        if c.get("vector"):del c["vector"]
    return {"answer": answer, "retrieval": kbinfos}


def use_sql(question,field_map, tenant_id, chat_mdl):
    sys_prompt = "你是一个DBA。你需要这对以下表的字段结构，根据我的问题写出sql。"
    user_promt = """
表名：{}；
数据库表字段说明如下：
{}

问题：{}
请写出SQL。
""".format(
        index_name(tenant_id),
        "\n".join([f"{k}: {v}" for k,v in field_map.items()]),
        question
    )
    sql = chat_mdl.chat(sys_prompt, [{"role": "user", "content": user_promt}], {"temperature": 0.1})
    sql = re.sub(r".*?select ", "select ", sql, flags=re.IGNORECASE)
    sql = re.sub(r" +", " ", sql)
    if sql[:len("select ")].lower() != "select ":
        return None, None
    if sql[:len("select *")].lower() != "select *":
        sql = "select doc_id,docnm_kwd," + sql[6:]

    tbl = retrievaler.sql_retrieval(sql)
    if not tbl: return None, None

    docid_idx = set([ii for ii, c in enumerate(tbl["columns"]) if c["name"] == "doc_id"])
    docnm_idx = set([ii for ii, c in enumerate(tbl["columns"]) if c["name"] == "docnm_kwd"])
    clmn_idx = [ii for ii in range(len(tbl["columns"])) if ii not in (docid_idx|docnm_idx)]

    clmns = "|".join([re.sub(r"/.*", "", field_map.get(tbl["columns"][i]["name"], f"C{i}")) for i in clmn_idx]) + "|原文"
    line = "|".join(["------" for _ in range(len(clmn_idx))]) + "|------"
    rows = ["|".join([str(r[i]) for i in clmn_idx])+"|" for r in tbl["rows"]]
    if not docid_idx or not docnm_idx:
        access_logger.error("SQL missing field: " + sql)
        return "\n".join([clmns, line, "\n".join(rows)]), []

    rows = "\n".join([r+f"##{ii}$$" for ii,r in enumerate(rows)])
    docid_idx = list(docid_idx)[0]
    docnm_idx = list(docnm_idx)[0]
    return "\n".join([clmns, line, rows]), [{"doc_id": r[docid_idx], "docnm_kwd": r[docnm_idx]} for r in tbl["rows"]]
