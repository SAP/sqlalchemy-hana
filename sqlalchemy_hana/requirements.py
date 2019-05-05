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

import sys

import sqlalchemy
from sqlalchemy.testing import exclusions, requirements


class Requirements(requirements.SuiteRequirements):

    @property
    def temporary_tables(self):
        return exclusions.open()

    @property
    def temp_table_reflection(self):
        return exclusions.open()

    @property
    def views(self):
        return exclusions.open()

    @property
    def deferrable_or_no_constraints(self):
        """Target database must support derferable constraints."""
        return exclusions.closed()

    @property
    def named_constraints(self):
        return exclusions.open()

    @property
    def unique_constraint_reflection(self):
        return exclusions.open()

    @property
    def reflects_pk_names(self):
        return exclusions.open()

    @property
    def self_referential_foreign_keys(self):
        return exclusions.open()

    @property
    def empty_inserts(self):
        """Empty value tuple in INSERT statement is not allowed"""
        return exclusions.closed()

    @property
    def precision_numerics_enotation_large(self):
        return exclusions.open()

    @property
    def precision_numerics_many_significant_digits(self):
        return exclusions.open()

    @property
    def precision_numerics_retains_significant_digits(self):
        return exclusions.closed()

    @property
    def datetime_literals(self):
        """HANA has the function to_date, to_time, to_timestamp"""
        return exclusions.open()

    @property
    def time_microseconds(self):
        """No support for microseconds in datetime"""
        return exclusions.closed()

    @property
    def datetime_microseconds(self):
        return exclusions.skip_if('hana+pyhdb')

    @property
    def datetime_historic(self):
        return exclusions.open()

    @property
    def date_historic(self):
        return exclusions.open()

    @property
    def text_type(self):
        """Currently not supported by PYHDB"""
        return exclusions.open()

    @property
    def schemas(self):
        return exclusions.open()

    @property
    def percent_schema_names(self):
        return exclusions.open()

    @property
    def savepoints(self):
        """No support for savepoints in transactions"""
        return exclusions.closed()

    @property
    def selectone(self):
        """HANA doesn't support 'SELECT 1' without 'FROM DUMMY'"""
        return exclusions.closed()

    @property
    def order_by_col_from_union(self):
        return exclusions.open()

    @property
    def broken_cx_oracle6_numerics(self):
        return exclusions.closed()

    @property
    def mysql_zero_date(self):
        return exclusions.closed()

    @property
    def mysql_non_strict(self):
        return exclusions.closed()

    @property
    def two_phase_transactions(self):
        """Not supported by PYHDB"""
        return exclusions.closed()

    @property
    def predictable_gc(self):
        return exclusions.open()

    @property
    def cpython(self):
        return exclusions.closed()

    @property
    def python3(self):
        if sys.version_info < (3,):
            return exclusions.closed()
        return exclusions.open()

    @property
    def identity(self):
        return exclusions.closed()

    @property
    def sane_rowcount(self):
        return exclusions.closed()

    @property
    def sane_multi_rowcount(self):
        return exclusions.closed()

    @property
    def check_constraints(self):
        return exclusions.open()

    @property
    def update_nowait(self):
        return exclusions.closed()

    @property
    def independent_connections(self):
        return exclusions.open()

    @property
    def non_broken_pickle(self):
        return exclusions.closed()

    @property
    def independent_cursors(self):
        return exclusions.open()

    @property
    def cross_schema_fk_reflection(self):
        return exclusions.closed()

    @property
    def updateable_autoincrement_pks(self):
        return exclusions.closed()

    @property
    def bound_limit_offset(self):
        return exclusions.open()

    @property
    def isolation_level(self):
        # TODO: Check support in pyhdb
        return exclusions.closed()

    # Disable mysql tests
    @property
    def mssql_freetds(self):
        return exclusions.closed()

    # Disable postgresql tests
    @property
    def postgresql_utf8_server_encoding(self):
        return exclusions.closed()

    @property
    def range_types(self):
        return exclusions.closed()

    @property
    def hstore(self):
        return exclusions.closed()

    @property
    def array_type(self):
        return exclusions.closed()

    @property
    def psycopg2_compatibility(self):
        return exclusions.closed()

    @property
    def postgresql_jsonb(self):
        return exclusions.closed()

    @property
    def savepoints_w_release(self):
        return exclusions.closed()

    @property
    def non_broken_binary(self):
        return exclusions.closed()

    @property
    def oracle5x(self):
        return exclusions.closed()

    @property
    def psycopg2_or_pg8000_compatibility(self):
        return exclusions.closed()

    @property
    def psycopg2_native_hstore(self):
        return exclusions.closed()

    @property
    def psycopg2_native_json(self):
        return exclusions.closed()

    @property
    def two_phase_recovery(self):
        return exclusions.closed()

    @property
    def enforces_check_constraints(self):
        return exclusions.closed()

    @property
    def implicitly_named_constraints(self):
        return exclusions.open()

    @property
    def autocommit(self):
        return exclusions.open()

    @property
    def comment_reflection(self):
        return exclusions.open()

    @property
    def sequences_optional(self):
        return exclusions.open()

    @property
    def timestamp_microseconds(self):
        return exclusions.skip_if('hana+pyhdb')

    @property
    def temp_table_names(self):
        return exclusions.open()

    @property
    def tuple_in(self):
        return exclusions.open()

    @property
    def foreign_key_constraint_option_reflection(self):
        return exclusions.open()

    @property
    def check_constraint_reflection(self):
        if sqlalchemy.__version__.startswith('1.1.'):
            # Skip reflection tests in SQLAlchemy~=1.1.0 due missing normalization
            return exclusions.closed()
        return exclusions.open()

    @property
    def implicit_decimal_binds(self):
        # See SQLAlchemy ticket 4036
        return exclusions.closed()

    @property
    def expressions_against_unbounded_text(self):
        return exclusions.closed()
