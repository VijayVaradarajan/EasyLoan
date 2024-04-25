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
from datetime import datetime

from api.db.db_models import DB
from api.db.db_models import File, Document, File2Document
from api.db.services.common_service import CommonService
from api.utils import current_timestamp, datetime_format


class File2DocumentService(CommonService):
    model = File2Document

    @classmethod
    @DB.connection_context()
    def get_by_file_id(cls, file_id):
        objs = cls.model.select().where(cls.model.file_id == file_id)
        return objs

    @classmethod
    @DB.connection_context()
    def get_by_document_id(cls, document_id):
        obj = cls.model.select().where(cls.model.document_id == document_id)
        if obj.count():
            e, obj = cls.get_by_id(obj[0].id)
            if not e:
                raise RuntimeError("Database error (Inform doesn't exist)!")
        else:
            raise RuntimeError("Database error (Inform doesn't exist)!")
        return obj

    @classmethod
    @DB.connection_context()
    def insert(cls, obj):
        if not cls.save(**obj):
            raise RuntimeError("Database error (File)!")
        e, obj = cls.get_by_id(obj["id"])
        if not e:
            raise RuntimeError("Database error (File retrieval)!")
        return obj

    @classmethod
    @DB.connection_context()
    def delete_by_file_id(cls, file_id):
        return cls.model.delete().where(cls.model.file_id == file_id).execute()

    @classmethod
    @DB.connection_context()
    def update_by_file_id(cls, file_id, obj):
        obj["update_time"] = current_timestamp()
        obj["update_date"] = datetime_format(datetime.now())
        num = cls.model.update(obj).where(cls.model.id == file_id).execute()
        e, obj = cls.get_by_id(cls.model.id)
        return obj
