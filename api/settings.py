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
import os

from enum import IntEnum, Enum

from api.utils import get_base_config,decrypt_database_config
from api.utils.file_utils import get_project_base_directory
from api.utils.log_utils import LoggerFactory, getLogger


# Server
API_VERSION = "v1"
RAG_FLOW_SERVICE_NAME = "ragflow"
SERVER_MODULE = "rag_flow_server.py"
TEMP_DIRECTORY = os.path.join(get_project_base_directory(), "temp")
RAG_FLOW_CONF_PATH = os.path.join(get_project_base_directory(), "conf")

SUBPROCESS_STD_LOG_NAME = "std.log"

ERROR_REPORT = True
ERROR_REPORT_WITH_PATH = False

MAX_TIMESTAMP_INTERVAL = 60
SESSION_VALID_PERIOD = 7 * 24 * 60 * 60 * 1000

REQUEST_TRY_TIMES = 3
REQUEST_WAIT_SEC = 2
REQUEST_MAX_WAIT_SEC = 300

USE_REGISTRY = get_base_config("use_registry")

LLM = get_base_config("llm", {})
CHAT_MDL = LLM.get("chat_model", "gpt-3.5-turbo")
EMBEDDING_MDL = LLM.get("embedding_model", "text-embedding-ada-002")
ASR_MDL = LLM.get("asr_model", "whisper-1")
PARSERS = LLM.get("parsers", "general:General,resume:esume,laws:Laws,manual:Manual,book:Book,paper:Paper,qa:Q&A,presentation:Presentation")
IMAGE2TEXT_MDL = LLM.get("image2text_model", "gpt-4-vision-preview")

# distribution
DEPENDENT_DISTRIBUTION = get_base_config("dependent_distribution", False)
RAG_FLOW_UPDATE_CHECK = False

HOST = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("host", "127.0.0.1")
HTTP_PORT = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("http_port")

SECRET_KEY = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("secret_key", "infiniflow")
TOKEN_EXPIRE_IN = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("token_expires_in", 3600)

NGINX_HOST = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("nginx", {}).get("host") or HOST
NGINX_HTTP_PORT = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("nginx", {}).get("http_port") or HTTP_PORT

RANDOM_INSTANCE_ID = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("random_instance_id", False)

PROXY = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("proxy")
PROXY_PROTOCOL = get_base_config(RAG_FLOW_SERVICE_NAME, {}).get("protocol")

DATABASE = decrypt_database_config()

# Logger
LoggerFactory.set_directory(os.path.join(get_project_base_directory(), "logs", "api"))
# {CRITICAL: 50, FATAL:50, ERROR:40, WARNING:30, WARN:30, INFO:20, DEBUG:10, NOTSET:0}
LoggerFactory.LEVEL = 10

stat_logger = getLogger("stat")
access_logger = getLogger("access")
database_logger = getLogger("database")

# Switch
# upload
UPLOAD_DATA_FROM_CLIENT = True

# authentication
AUTHENTICATION_CONF = get_base_config("authentication", {})

# client
CLIENT_AUTHENTICATION = AUTHENTICATION_CONF.get("client", {}).get("switch", False)
HTTP_APP_KEY = AUTHENTICATION_CONF.get("client", {}).get("http_app_key")
GITHUB_OAUTH = get_base_config("oauth", {}).get("github")
WECHAT_OAUTH = get_base_config("oauth", {}).get("wechat")

# site
SITE_AUTHENTICATION = AUTHENTICATION_CONF.get("site", {}).get("switch", False)

# permission
PERMISSION_CONF = get_base_config("permission", {})
PERMISSION_SWITCH = PERMISSION_CONF.get("switch")
COMPONENT_PERMISSION = PERMISSION_CONF.get("component")
DATASET_PERMISSION = PERMISSION_CONF.get("dataset")

HOOK_MODULE = get_base_config("hook_module")
HOOK_SERVER_NAME = get_base_config("hook_server_name")

ENABLE_MODEL_STORE = get_base_config('enable_model_store', False)
# authentication
USE_AUTHENTICATION = False
USE_DATA_AUTHENTICATION = False
AUTOMATIC_AUTHORIZATION_OUTPUT_DATA = True
USE_DEFAULT_TIMEOUT = False
AUTHENTICATION_DEFAULT_TIMEOUT = 30 * 24 * 60 * 60 # s
PRIVILEGE_COMMAND_WHITELIST = []
CHECK_NODES_IDENTITY = False

class CustomEnum(Enum):
    @classmethod
    def valid(cls, value):
        try:
            cls(value)
            return True
        except:
            return False

    @classmethod
    def values(cls):
        return [member.value for member in cls.__members__.values()]

    @classmethod
    def names(cls):
        return [member.name for member in cls.__members__.values()]


class PythonDependenceName(CustomEnum):
    Rag_Source_Code = "python"
    Python_Env = "miniconda"


class ModelStorage(CustomEnum):
    REDIS = "redis"
    MYSQL = "mysql"


class RetCode(IntEnum, CustomEnum):
    SUCCESS = 0
    NOT_EFFECTIVE = 10
    EXCEPTION_ERROR = 100
    ARGUMENT_ERROR = 101
    DATA_ERROR = 102
    OPERATING_ERROR = 103
    CONNECTION_ERROR = 105
    RUNNING = 106
    PERMISSION_ERROR = 108
    AUTHENTICATION_ERROR = 109
    SERVER_ERROR = 500
