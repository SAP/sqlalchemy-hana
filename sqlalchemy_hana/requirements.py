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

from sqlalchemy.testing import exclusions, requirements

class Requirements(requirements.SuiteRequirements):

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
        """There is no way to define a constraint name."""
        return exclusions.closed()

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
    def text_type(self):
        """Currently not supported by PYHDB"""
        return exclusions.closed()

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
