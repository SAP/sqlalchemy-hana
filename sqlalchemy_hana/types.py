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

from sqlalchemy import types as sqltypes
from sqlalchemy.util import compat

class TINYINT(sqltypes.TypeEngine):

    __visit_name__ = "TINYINT"


class DOUBLE(sqltypes.Float):

    __visit_name__ = "DOUBLE"


class BOOLEAN(sqltypes.Boolean):

    def get_dbapi_type(self, dbapi):
        return dbapi.NUMBER


class DATE(sqltypes.Date):

    def literal_processor(self, dialect):
        self.bind_processor(dialect)

        def process(value):
            return "to_date('%s')" % value
        return process


class TIME(sqltypes.Time):

    def literal_processor(self, dialect):
        self.bind_processor(dialect)

        def process(value):
            return "to_time('%s')" % value
        return process


class TIMESTAMP(sqltypes.DateTime):

    def literal_processor(self, dialect):
        self.bind_processor(dialect)

        def process(value):
            return "to_timestamp('%s')" % value
        return process


class _LOBMixin(object):

    def result_processor(self, dialect, coltype):
        if not dialect.auto_convert_lobs:
            # Disable processor and return raw DBAPI LOB type
            return None

        def process(value):
            if value is None:
                return None
            if isinstance(value, compat.string_types):
                return value
            if isinstance(value, memoryview):
                return value.obj
            if compat.py2k and isinstance(value, buffer):
                return value
            if hasattr(value, "read"):
                return value.read()
            raise NotImplementedError
        return process


class HanaText(_LOBMixin, sqltypes.Text):
    def get_dbapi_type(self, dbapi):
        return dbapi.CLOB


class HanaUnicodeText(_LOBMixin, sqltypes.UnicodeText):
    def get_dbapi_type(self, dbapi):
        return dbapi.NCLOB

    def result_processor(self, dialect, coltype):
        lob_processor = _LOBMixin.result_processor(self, dialect, coltype)
        if lob_processor is None:
            return None

        string_processor = sqltypes.UnicodeText.result_processor(
            self, dialect, coltype)

        if string_processor is None:
            return lob_processor
        else:
            def process(value):
                return string_processor(lob_processor(value))
            return process


class HanaBinary(_LOBMixin, sqltypes.LargeBinary):
    def get_dbapi_type(self, dbapi):
        return dbapi.BLOB

    def bind_processor(self, dialect):
        return None


class NCLOB(sqltypes.Text):
    __visit_name__ = 'NCLOB'
