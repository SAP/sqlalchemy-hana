# Copyright 2015 SAP SE.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from sqlalchemy import types

class TINYINT(types.TypeEngine):

    __visit_name__ = "TINYINT"

class DOUBLE(types.Float):

    __visit_name__ = "DOUBLE"

class BOOLEAN(types.Boolean):

    def get_dbapi_type(self, dbapi):
        return dbapi.NUMBER

class DATE(types.Date):

    def literal_processor(self, dialect):
        bp = self.bind_processor(dialect)

        def process(value):
            return "to_date('%s')" % value
        return process

class TIME(types.Time):

    def literal_processor(self, dialect):
        bp = self.bind_processor(dialect)

        def process(value):
            return "to_time('%s')" % value
        return process

class TIMESTAMP(types.DateTime):

    def literal_processor(self, dialect):
        bp = self.bind_processor(dialect)

        def process(value):
            return "to_timestamp('%s')" % value
        return process
