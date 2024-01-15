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
import peewee
from werkzeug.security import generate_password_hash, check_password_hash

from web_server.db import TenantPermission
from web_server.db.db_models import DB, UserTenant
from web_server.db.db_models import Knowledgebase
from web_server.db.services.common_service import CommonService
from web_server.utils import get_uuid, get_format_time
from web_server.db.db_utils import StatusEnum


class KnowledgebaseService(CommonService):
    model = Knowledgebase

    @classmethod
    @DB.connection_context()
    def get_by_tenant_ids(cls, joined_tenant_ids, user_id, page_number, items_per_page, orderby, desc):
        kbs = cls.model.select().where(
            ((cls.model.tenant_id.in_(joined_tenant_ids) & (cls.model.permission == TenantPermission.TEAM.value)) | (cls.model.tenant_id == user_id))
            & (cls.model.status==StatusEnum.VALID.value)
        )
        if desc: kbs = kbs.order_by(cls.model.getter_by(orderby).desc())
        else: kbs = kbs.order_by(cls.model.getter_by(orderby).asc())

        kbs = kbs.paginate(page_number, items_per_page)

        return list(kbs.dicts())

