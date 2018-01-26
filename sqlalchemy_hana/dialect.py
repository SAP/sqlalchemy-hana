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

from sqlalchemy import sql, types, util
from sqlalchemy.engine import default, reflection
from sqlalchemy.sql import compiler
from sqlalchemy.sql.elements import quoted_name
from sqlalchemy import exc
from sqlalchemy_hana import types as hana_types


RESERVED_WORDS = {
    'all', 'alter', 'as', 'before', 'begin', 'both', 'case', 'char',
    'condition', 'connect', 'cross', 'cube', 'current_connection',
    'current_date', 'current_schema', 'current_time', 'current_timestamp',
    'current_transaction_isolation_level', 'current_user', 'current_utcdate',
    'current_utctime', 'current_utctimestamp', 'currval', 'cursor',
    'declare', 'distinct', 'else', 'elseif', 'end', 'except', 'exception',
    'exec', 'false', 'for', 'from', 'full', 'group', 'having', 'if', 'in',
    'inner', 'inout', 'intersect', 'into', 'is', 'join', 'leading', 'left',
    'limit', 'loop', 'minus', 'natural', 'nchar', 'nextval', 'null', 'on',
    'order', 'out', 'prior', 'return', 'returns', 'reverse', 'right',
    'rollup', 'rowid', 'select', 'session_user', 'set', 'sql', 'start',
    'sysuuid', 'tablesample', 'top', 'trailing', 'true', 'union', 'unknown',
    'using', 'utctimestamp', 'values', 'when', 'where', 'while', 'with'
}


class HANAIdentifierPreparer(compiler.IdentifierPreparer):

    reserved_words = RESERVED_WORDS


class HANAStatementCompiler(compiler.SQLCompiler):

    def visit_sequence(self, seq):
        return self.dialect.identifier_preparer.format_sequence(seq) + ".NEXTVAL"

    def default_from(self):
        return " FROM DUMMY"

    def limit_clause(self, select, **kw):
        text = ""
        if select._limit_clause is not None:
            text += "\n LIMIT " + self.process(select._limit_clause, **kw)
        if select._offset_clause is not None:
            if select._limit_clause is None:
                # Dirty Hack but HANA only support OFFSET with LIMIT <integer>
                text += "\n LIMIT 999999"
            text += " OFFSET " + self.process(select._offset_clause, **kw)
        return text

    def for_update_clause(self, select, **kw):
        tmp = " FOR UPDATE"

        if select._for_update_arg.of:
            tmp += " OF " + ", ".join(
                self.process(elem, **kw) for elem
                in select._for_update_arg.of
            )

        if select._for_update_arg.nowait:
            tmp += " NOWAIT"

        return tmp


class HANATypeCompiler(compiler.GenericTypeCompiler):

    def visit_boolean(self, type_):
        return self.visit_TINYINT(type_)

    def visit_NUMERIC(self, type_):
        return self.visit_DECIMAL(type_)

    def visit_TINYINT(self, type_):
        return "TINYINT"

    def visit_DOUBLE(self, type_):
        return "DOUBLE"

    def visit_unicode(self, type_, **kw):
        return self.visit_NVARCHAR(type_, **kw)

    def visit_text(self, type_, **kw):
        return self.visit_CLOB(type_, **kw)

    def visit_large_binary(self, type_, **kw):
        return self.visit_BLOB(type_, **kw)

    def visit_unicode_text(self, type_, **kw):
        return self.visit_NCLOB(type_, **kw)


class HANADDLCompiler(compiler.DDLCompiler):
    def visit_unique_constraint(self, constraint):
        if len(constraint) == 0:
            return ''

        text = ""
        if constraint.name is not None:
            formatted_name = self.preparer.format_constraint(constraint)
            if formatted_name is not None:
                text += "CONSTRAINT %s " % formatted_name
        text += "UNIQUE (%s)" % (
            ', '.join(self.preparer.quote(c.name)
                      for c in constraint))
        text += self.define_constraint_deferrability(constraint)
        return text

    def visit_create_table(self, create):
        table = create.element

        # The table._prefixes list outlives the current compilation, meaning changing the list
        # will change it globally. To prevent adding the same prefix multiple times, it is
        # removed again after the super-class'es visit_create_table call, which consumes the
        # table prefixes.

        table_type = table.kwargs.get('hana_table_type')
        appended_index = None
        if table_type:
            appended_index = len(table._prefixes)
            table._prefixes.append(table_type.upper())

        result = super(HANADDLCompiler, self).visit_create_table(create)

        if appended_index is not None:
            table._prefixes.pop(appended_index)

        return result

class HANAExecutionContext(default.DefaultExecutionContext):
    def fire_sequence(self, seq, type_):
        seq = self.dialect.identifier_preparer.format_sequence(seq)
        return self._execute_scalar("SELECT %s.NEXTVAL FROM DUMMY" % seq, type_)


# ischema_names = {
#     'BLOB': hana_types.BLOB,
#     'CLOB': hana_types.CLOB,
#     'NCLOB': hana_types.NCLOB,
# }
class HANAInspector(reflection.Inspector):

    def get_table_oid(self, table_name, schema=None):
        return self.dialect.get_table_oid(self.bind, table_name, schema, info_cache=self.info_cache)


class HANABaseDialect(default.DefaultDialect):
    name = "hana"
    default_paramstyle = 'format'

    statement_compiler = HANAStatementCompiler
    type_compiler = HANATypeCompiler
    ddl_compiler = HANADDLCompiler
    preparer = HANAIdentifierPreparer
    execution_ctx_cls = HANAExecutionContext
    inspector = HANAInspector

    encoding = "cesu-8"
    convert_unicode = True
    supports_unicode_statements = True
    supports_unicode_binds = True
    requires_name_normalize = True

    supports_sequences = True
    supports_native_decimal = True

    supports_comments = True

    # ischema_names can be empty dict, not needed for reading lobs...
    ischema_names = {}  # ischema_names
    colspecs = {
        types.Boolean: hana_types.BOOLEAN,
        types.Date: hana_types.DATE,
        types.Time: hana_types.TIME,
        types.DateTime: hana_types.TIMESTAMP,
        types.LargeBinary: hana_types.HanaBinary,
        types.Text: hana_types.HanaText,
        types.UnicodeText: hana_types.HanaUnicodeText
    }

    postfetch_lastrowid = False
    implicit_returning = False
    supports_empty_insert = False
    supports_native_boolean = False
    supports_default_values = False
    supports_sane_multi_rowcount = False

    def __init__(self, auto_convert_lobs=True, **kwargs):
        super(HANABaseDialect, self).__init__(**kwargs)
        self.auto_convert_lobs = auto_convert_lobs

    def on_connect(self):
        return None

    def _get_server_version_info(self, connection):
        pass

    def _get_default_schema_name(self, connection):
        return self.normalize_name(connection.engine.url.username.upper())

    def _check_unicode_returns(self, connection):
        return True

    def _check_unicode_description(self, connection):
        return True

    def normalize_name(self, name):
        if name is None:
            return None

        if name.upper() == name and not \
           self.identifier_preparer._requires_quotes(name.lower()):
            name = name.lower()
        elif name.lower() == name:
            return quoted_name(name, quote=True)

        return name

    def denormalize_name(self, name):
        if name is None:
            return None

        if name.lower() == name and not \
           self.identifier_preparer._requires_quotes(name.lower()):
            name = name.upper()
        return name

    def has_table(self, connection, table_name, schema=None):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT 1 FROM TABLES "
                "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table",
            ).bindparams(
                schema=self.denormalize_name(schema),
                table=self.denormalize_name(table_name)
            )
        )
        return bool(result.first())

    def has_sequence(self, connection, sequence_name, schema=None):
        schema = schema or self.default_schema_name
        result = connection.execute(
            sql.text(
                "SELECT 1 FROM SEQUENCES "
                "WHERE SCHEMA_NAME=:schema AND SEQUENCE_NAME=:sequence",
            ).bindparams(
                schema=self.denormalize_name(schema),
                sequence=self.denormalize_name(sequence_name)
            )
        )
        return bool(result.first())

    def get_schema_names(self, connection, **kwargs):
        result = connection.execute(
            sql.text("SELECT SCHEMA_NAME FROM SCHEMAS")
        )

        return list([
            self.normalize_name(name) for name, in result.fetchall()
        ])

    def get_table_names(self, connection, schema=None, **kwargs):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT TABLE_NAME, IS_TEMPORARY FROM TABLES WHERE SCHEMA_NAME=:schema",
            ).bindparams(
                schema=self.denormalize_name(schema),
            )
        )

        tables = list([
            self.normalize_name(row[0]) for row in result.fetchall() if row[1] == "FALSE"
        ])
        return tables

    def get_temp_table_names(self, connection, schema=None, **kw):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT TABLE_NAME FROM M_TEMPORARY_TABLES ORDER BY NAME",
            ).bindparams(
                schema=self.denormalize_name(schema),
            )
        )

        temp_table_names = list([
            self.normalize_name(row[0]) for row in result.fetchall()
        ])
        return temp_table_names

    def get_view_names(self, connection, schema=None, **kwargs):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT VIEW_NAME FROM VIEWS WHERE SCHEMA_NAME=:schema",
            ).bindparams(
                schema=self.denormalize_name(schema),
            )
        )

        views = list([
            self.normalize_name(row[0]) for row in result.fetchall()
        ])
        return views

    def get_view_definition(self, connection, view_name, schema=None, **kwargs):
        schema = schema or self.default_schema_name

        return connection.execute(
            sql.text(
                "SELECT DEFINITION FROM VIEWS WHERE VIEW_NAME=:view_name AND SCHEMA_NAME=:schema LIMIT 1",
            ).bindparams(
                view_name=self.denormalize_name(view_name),
                schema=self.denormalize_name(schema),
            )
        ).scalar()

    def get_columns(self, connection, table_name, schema=None, **kwargs):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                """SELECT COLUMN_NAME, DATA_TYPE_NAME, DEFAULT_VALUE, IS_NULLABLE, LENGTH, SCALE, COMMENTS FROM (
    SELECT SCHEMA_NAME, TABLE_NAME, COLUMN_NAME, POSITION, DATA_TYPE_NAME, DEFAULT_VALUE, IS_NULLABLE, LENGTH, SCALE, 
    COMMENTS FROM SYS.TABLE_COLUMNS 
    UNION ALL
    SELECT SCHEMA_NAME, VIEW_NAME AS TABLE_NAME, COLUMN_NAME, POSITION, DATA_TYPE_NAME, DEFAULT_VALUE, IS_NULLABLE, LENGTH, SCALE, COMMENTS FROM SYS.VIEW_COLUMNS
) AS COLUMS
WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table
ORDER BY POSITION"""
            ).bindparams(
                schema=self.denormalize_name(schema),
                table=self.denormalize_name(table_name)
            )
        )

        columns = []
        for row in result.fetchall():
            column = {
                'name': self.normalize_name(row[0]),
                'default': row[2],
                'nullable': row[3] == "TRUE",
                'comment': row[6]

            }

            if hasattr(types, row[1]):
                column['type'] = getattr(types, row[1])
            elif hasattr(hana_types, row[1]):
                column['type'] = getattr(hana_types, row[1])
            else:
                util.warn("Did not recognize type '%s' of column '%s'" % (
                    row[1], column['name']
                ))
                column['type'] = types.NULLTYPE

            if column['type'] == types.DECIMAL:
                column['type'] = types.DECIMAL(row[4], row[5])
            elif column['type'] == types.VARCHAR:
                column['type'] = types.VARCHAR(row[4])

            columns.append(column)

        return columns

    def get_foreign_keys(self, connection, table_name, schema=None, **kwargs):
        lookup_schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT  CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_SCHEMA_NAME, "
                "REFERENCED_TABLE_NAME,  REFERENCED_COLUMN_NAME, UPDATE_RULE, DELETE_RULE "
                "FROM REFERENTIAL_CONSTRAINTS "
                "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table "
                "ORDER BY CONSTRAINT_NAME, POSITION"
            ).bindparams(
                schema=self.denormalize_name(lookup_schema),
                table=self.denormalize_name(table_name)
            )
        )
        foreign_keys = []

        for row in result:

            foreign_key = {
                "name": self.normalize_name(row[0]),
                "constrained_columns": [self.normalize_name(row[1])],
                "referred_schema": schema,
                "referred_table": self.normalize_name(row[3]),
                "referred_columns": [self.normalize_name(row[4])],
                "options": {"onupdate": row[5],
                            "ondelete": row[6]}
            }

            if row[2] != self.denormalize_name(self.default_schema_name):
                foreign_key["referred_schema"] = self.normalize_name(row[2])

            foreign_keys.append(foreign_key)

        return foreign_keys

    def get_indexes(self, connection, table_name, schema=None, **kwargs):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                'SELECT "INDEX_NAME", "COLUMN_NAME", "CONSTRAINT" '
                "FROM INDEX_COLUMNS "
                "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table "
                "ORDER BY POSITION"
            ).bindparams(
                schema=self.denormalize_name(schema),
                table=self.denormalize_name(table_name)
            )
        )

        indexes = {}
        for name, column, constraint in result.fetchall():
            if name.startswith("_SYS"):
                continue

            name = self.normalize_name(name)
            column = self.normalize_name(column)

            if name not in indexes:
                indexes[name] = {
                    "name": name,
                    "unique": False,
                    "column_names": [column]
                }

                if constraint is not None:
                    indexes[name]["unique"] = "UNIQUE" in constraint.upper()

            else:
                indexes[name]["column_names"].append(column)

        return list(indexes.values())

    def get_pk_constraint(self, connection, table_name, schema=None, **kwargs):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT CONSTRAINT_NAME, COLUMN_NAME FROM CONSTRAINTS "
                "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table AND "
                "IS_PRIMARY_KEY='TRUE' "
                "ORDER BY POSITION"
            ).bindparams(
                schema=self.denormalize_name(schema),
                table=self.denormalize_name(table_name)
            )
        )

        constraint_name = None
        constrained_columns = []
        for row in result.fetchall():
            constraint_name = row[0]
            constrained_columns.append(self.normalize_name(row[1]))

        return {
            "name": self.normalize_name(constraint_name),
            "constrained_columns": constrained_columns
        }

    def get_unique_constraints(self, connection, table_name, schema=None, **kwargs):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT CONSTRAINT_NAME, COLUMN_NAME FROM CONSTRAINTS "
                "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table AND "
                "IS_UNIQUE_KEY='TRUE' "
                "ORDER BY CONSTRAINT_NAME, POSITION"
            ).bindparams(
                schema=self.denormalize_name(schema),
                table=self.denormalize_name(table_name)
            )
        )

        constraints = []
        parsing_constraint = None
        for constraint_name, column_name in result.fetchall():
            if parsing_constraint != constraint_name:
                # Start with new constraint
                parsing_constraint = constraint_name

                constraint = {'name': None, 'column_names': []}
                if not constraint_name.startswith('_SYS'):
                    # Constraint has user-defined name
                    constraint['name'] = self.normalize_name(constraint_name)
                constraints.append(constraint)
            constraint['column_names'].append(self.normalize_name(column_name))

        return constraints

    def get_check_constraints(self, connection, table_name, schema=None, **kw):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT CONSTRAINT_NAME, CHECK_CONDITION FROM CONSTRAINTS "
                "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table AND "
                "CHECK_CONDITION IS NOT NULL"
            ).bindparams(
                schema=self.denormalize_name(schema),
                table=self.denormalize_name(table_name)
            )
        )

        check_conditions = []

        for row in result.fetchall():
            check_condition = {
                "name": self.normalize_name(row[0]),
                "sqltext": self.normalize_name(row[1])
            }
            check_conditions.append(check_condition)

        return check_conditions

    def set_isolation_level(self, connection, level):
        if level == "AUTOCOMMIT":
            connection.setautocommit(True)
        else:
            connection.setautocommit(False)

    def get_table_oid(self, connection, table_name, schema=None, **kw):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT TABLE_OID FROM TABLES "
                "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table"
            ).bindparams(
                schema=self.denormalize_name(schema),
                table=self.denormalize_name(table_name)
            )
        )

        table_oid = (result.fetchone())[0]
        return table_oid

    def get_table_comment(self, connection, table_name, schema=None, **kw):
        schema = schema or self.default_schema_name

        result = connection.execute(
            sql.text(
                "SELECT COMMENTS FROM TABLES WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table"
            ).bindparams(
                schema=self.denormalize_name(schema),
                table=self.denormalize_name(table_name),
            )
        )

        return {"text" : (result.fetchone())[0]}

class HANAPyHDBDialect(HANABaseDialect):

    driver = 'pyhdb'
    default_paramstyle = 'qmark'

    @classmethod
    def dbapi(cls):
        import pyhdb
        pyhdb.paramstyle = cls.default_paramstyle
        return pyhdb

    def create_connect_args(self, url):
        kwargs = url.translate_connect_args(username="user")

        if kwargs.get("database"):
            raise NotImplementedError("no support for database parameter")

        kwargs.setdefault("port", 30015)
        return (), kwargs

    def is_disconnect(self, error, connection, cursor):
        if connection is None:
            return True
        return connection.closed


class HANAHDBCLIDialect(HANABaseDialect):

    driver = 'hdbcli'
    default_paramstyle = 'qmark'

    @classmethod
    def dbapi(cls):
        import hdbcli.dbapi
        hdbcli.dbapi.paramstyle = cls.default_paramstyle
        return hdbcli.dbapi

    def create_connect_args(self, url):
        kwargs = url.translate_connect_args(host="address", username="user", database="databaseName")

        port = 30015
        if kwargs.get("databaseName"):
            port = 30013

        kwargs.setdefault("port", port)

        return (), kwargs

    def connect(self, *args, **kwargs):
        connection = super(HANAHDBCLIDialect, self).connect(*args, **kwargs)
        connection.setautocommit(False)
        return connection

    def is_disconnect(self, error, connection, cursor):
        if connection:
            return not connection.isconnected()
        if isinstance(error, self.dbapi.Error):
            if error.errorcode == -10709:
                return True
        return super(HANAHDBCLIDialect, self).is_disconnect(error, connection, cursor)
