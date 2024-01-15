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
from flask import request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user, login_user, logout_user
from web_server.utils.api_utils import server_error_response, validate_request
from web_server.utils import get_uuid, get_format_time, decrypt, download_img
from web_server.db import UserTenantRole
from web_server.settings import RetCode, GITHUB_OAUTH, CHAT_MDL, EMBEDDING_MDL, ASR_MDL, IMAGE2TEXT_MDL, PARSERS
from web_server.db.services.user_service import UserService, TenantService, UserTenantService
from web_server.settings import stat_logger
from web_server.utils.api_utils import get_json_result, cors_reponse


@manager.route('/login', methods=['POST', 'GET'])
def login():
    userinfo = None
    login_channel = "password"
    if session.get("access_token"):
        login_channel = session["access_token_from"]
        if session["access_token_from"] == "github":
            userinfo = user_info_from_github(session["access_token"])
    elif not request.json:
        return get_json_result(data=False, retcode=RetCode.AUTHENTICATION_ERROR,
                               retmsg='Unautherized!')

    email = request.json.get('email') if not userinfo else userinfo["email"]
    users = UserService.query(email=email)
    if not users:
        if request.json is not None:
            return get_json_result(data=False, retcode=RetCode.AUTHENTICATION_ERROR, retmsg=f'This Email is not registered!')
        avatar = ""
        try:
            avatar = download_img(userinfo["avatar_url"])
        except Exception as e:
            stat_logger.exception(e)
        try:
            users = user_register({
                "access_token": session["access_token"],
                "email": userinfo["email"],
                "avatar": avatar,
                "nickname": userinfo["login"],
                "login_channel": login_channel,
                "last_login_time": get_format_time(),
                "is_superuser": False,
            })
            if not users: raise Exception('Register user failure.')
            if len(users) > 1: raise Exception('Same E-mail exist!')
            user = users[0]
            login_user(user)
            return cors_reponse(data=user.to_json(), auth=user.get_id(), retmsg="Welcome back!")
        except Exception as e:
            stat_logger.exception(e)
            return server_error_response(e)
    elif not request.json:
        login_user(users[0])
        return cors_reponse(data=users[0].to_json(), auth=users[0].get_id(), retmsg="Welcome back!")

    password = request.json.get('password')
    try:
        password = decrypt(password)
    except:
        return get_json_result(data=False, retcode=RetCode.SERVER_ERROR, retmsg='Fail to crypt password')

    user = UserService.query_user(email, password)
    if user:
        response_data = user.to_json()
        user.access_token = get_uuid()
        login_user(user)
        user.save()
        msg = "Welcome back!"
        return cors_reponse(data=response_data, auth=user.get_id(), retmsg=msg)
    else:
        return get_json_result(data=False, retcode=RetCode.AUTHENTICATION_ERROR, retmsg='Email and Password do not match!')


@manager.route('/github_callback', methods=['GET'])
def github_callback():
    try:
        import requests
        res = requests.post(GITHUB_OAUTH.get("url"), data={
            "client_id": GITHUB_OAUTH.get("client_id"),
            "client_secret":  GITHUB_OAUTH.get("secret_key"),
            "code": request.args.get('code')
        },headers={"Accept": "application/json"})
        res = res.json()
        if "error" in res:
            return get_json_result(data=False, retcode=RetCode.AUTHENTICATION_ERROR,
                                   retmsg=res["error_description"])

        if "user:email" not in res["scope"].split(","):
            return get_json_result(data=False, retcode=RetCode.AUTHENTICATION_ERROR, retmsg='user:email not in scope')

        session["access_token"] = res["access_token"]
        session["access_token_from"] = "github"
        return redirect(url_for("user.login"),  code=307)

    except Exception as e:
        stat_logger.exception(e)
        return server_error_response(e)


def user_info_from_github(access_token):
    import requests
    headers = {"Accept": "application/json", 'Authorization': f"token {access_token}"}
    res = requests.get(f"https://api.github.com/user?access_token={access_token}", headers=headers)
    user_info = res.json()
    email_info = requests.get(f"https://api.github.com/user/emails?access_token={access_token}", headers=headers).json()
    user_info["email"] = next((email for email in email_info if email['primary'] == True), None)["email"]
    return user_info


@manager.route("/logout", methods=['GET'])
@login_required
def log_out():
    current_user.access_token = ""
    current_user.save()
    logout_user()
    return get_json_result(data=True)


@manager.route("/setting", methods=["POST"])
@login_required
def setting_user():
    update_dict = {}
    request_data = request.json
    if request_data.get("password"):
        new_password = request_data.get("new_password")
        if not check_password_hash(current_user.password, decrypt(request_data["password"])):
            return get_json_result(data=False, retcode=RetCode.AUTHENTICATION_ERROR, retmsg='Password error!')

        if new_password: update_dict["password"] = generate_password_hash(decrypt(new_password))

    for k in request_data.keys():
        if k in ["password", "new_password"]:continue
        update_dict[k] = request_data[k]

    try:
        UserService.update_by_id(current_user.id, update_dict)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='Update failure!', retcode=RetCode.EXCEPTION_ERROR)


@manager.route("/info", methods=["GET"])
@login_required
def user_info():
    return get_json_result(data=current_user.to_dict())


def user_register(user):
    user_id = get_uuid()
    user["id"] = user_id
    tenant = {
        "id": user_id,
        "name": user["nickname"] + "‘s Kingdom",
        "llm_id": CHAT_MDL,
        "embd_id": EMBEDDING_MDL,
        "asr_id": ASR_MDL,
        "parser_ids": PARSERS,
        "img2txt_id": IMAGE2TEXT_MDL
    }
    usr_tenant = {
        "tenant_id": user_id,
        "user_id": user_id,
        "invited_by": user_id,
        "role": UserTenantRole.OWNER
    }

    if not UserService.save(**user):return
    TenantService.save(**tenant)
    UserTenantService.save(**usr_tenant)
    return UserService.query(email=user["email"])


@manager.route("/register", methods=["POST"])
@validate_request("nickname", "email", "password")
def user_add():
    req = request.json
    if UserService.query(email=req["email"]):
        return get_json_result(data=False, retmsg=f'Email: {req["email"]} has already registered!', retcode=RetCode.OPERATING_ERROR)

    user_dict = {
        "access_token": get_uuid(),
        "email": req["email"],
        "nickname": req["nickname"],
        "password": decrypt(req["password"]),
        "login_channel": "password",
        "last_login_time": get_format_time(),
        "is_superuser": False,
    }
    try:
        users = user_register(user_dict)
        if not users: raise Exception('Register user failure.')
        if len(users) > 1: raise Exception('Same E-mail exist!')
        user = users[0]
        login_user(user)
        return cors_reponse(data=user.to_json(), auth=user.get_id(), retmsg="Welcome aboard!")
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='User registration failure!', retcode=RetCode.EXCEPTION_ERROR)



@manager.route("/tenant_info", methods=["GET"])
@login_required
def tenant_info():
    try:
        tenants = TenantService.get_by_user_id(current_user.id)
        return get_json_result(data=tenants)
    except Exception as e:
        return server_error_response(e)
