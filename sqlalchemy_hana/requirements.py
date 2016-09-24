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
from sqlalchemy.testing import exclusions, requirements


class Requirements(requirements.SuiteRequirements):

    @property
    def temporary_tables(self):
        # TODO: HANA supports temporty table but only with GLOBAL or LOCAL specification
        return exclusions.closed()

    @property
    def temp_table_reflection(self):
        return exclusions.closed()

    @property
    def views(self):
        return exclusions.open()

    @property
    def deferrable_or_no_constraints(self):
        """Target database must support derferable constraints."""
        return exclusions.closed()

    @property
    def named_constraints(self):
        """target database must support names for constraints."""
        return exclusions.closed()

    @property
    def unique_constraint_reflection(self):
        return exclusions.open()

    @property
    def reflects_pk_names(self):
        return exclusions.open()

    @property
    def self_referential_foreign_keys(self):
        """SAP HANA doen't support self-referential foreign keys."""
        return exclusions.closed()

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
        return exclusions.open()

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
        """No support for microseconds in datetime"""
        return exclusions.closed()

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
        return exclusions.closed()

    @property
    def savepoints(self):
        """No support for savepoints in transactions"""
        return exclusions.closed()

    @property
    def selectone(self):
        """HANA doesn't support 'SELECT 1' without 'FROM DUMMY'"""
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
        return exclusions.closed()

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
        return exclusions.closed()

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
