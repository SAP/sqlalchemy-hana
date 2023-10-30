"""SQLAlchemy requirements for testing."""

from __future__ import annotations

from sqlalchemy.testing import exclusions, requirements


class Requirements(requirements.SuiteRequirements):
    @property
    def views(self):
        return exclusions.open()

    @property
    def reflects_pk_names(self):
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
        # SAP HANA does not support microseconds in TIME
        return exclusions.closed()

    @property
    def datetime_historic(self):
        return exclusions.open()

    @property
    def date_historic(self):
        return exclusions.open()

    @property
    def percent_schema_names(self):
        return exclusions.open()

    @property
    def selectone(self):
        # SAP HANA doesn't support 'SELECT 1' without 'FROM DUMMY'
        return exclusions.closed()

    @property
    def two_phase_transactions(self):
        return exclusions.open()

    @property
    def autoincrement_without_sequence(self):
        # Not supported yet
        return exclusions.closed()

    @property
    def isolation_level(self):
        return exclusions.open()

    def get_isolation_levels(self, config):
        return {
            "default": "READ COMMITTED",
            "supported": [
                "READ COMMITTED",
                "SERIALIZABLE",
                "REPEATABLE READ",
                "AUTOCOMMIT",
            ],
        }

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
        return exclusions.open()

    @property
    def temp_table_names(self):
        return exclusions.open()

    @property
    def tuple_in(self):
        return exclusions.open()

    @property
    def foreign_key_constraint_option_reflection_ondelete(self):
        # TODO fix
        return exclusions.closed()

    @property
    def foreign_key_constraint_option_reflection_onupdate(self):
        # TODO fix
        return exclusions.closed()

    @property
    def check_constraint_reflection(self):
        # TODO fix
        return exclusions.closed()

    @property
    def expressions_against_unbounded_text(self):
        # not supported by SAP HANA
        return exclusions.closed()

    @property
    def independent_readonly_connections(self):
        # TODO check if supported
        return exclusions.closed()

    @property
    def sql_expression_limit_offset(self):
        # SAP HANA does not support expressions in LIMIT or OFFSET
        return exclusions.closed()

    @property
    def array_type(self):
        # Not yet supported, #119
        return exclusions.closed()

    @property
    def unbounded_varchar(self):
        # SAP HANA requires a length vor (N)VARCHAR
        return exclusions.closed()

    @property
    def unique_index_reflect_as_unique_constraints(self):
        # SAP HANA reflects unique indexes as unique constraints
        return exclusions.open()

    @property
    def unique_constraints_reflect_as_index(self):
        # SAP HANA reflects unique constraints as indexes
        return exclusions.open()

    @property
    def intersect(self):
        return exclusions.open()

    @property
    def except_(self):
        return exclusions.open()

    @property
    def window_functions(self):
        return exclusions.open()

    @property
    def comment_reflection_full_unicode(self):
        return exclusions.open()

    @property
    def foreign_key_constraint_name_reflection(self):
        return exclusions.open()

    @property
    def cross_schema_fk_reflection(self):
        return exclusions.open()

    @property
    def fk_constraint_option_reflection_onupdate_restrict(self):
        # TODO fix
        return exclusions.closed()

    @property
    def fk_constraint_option_reflection_ondelete_restrict(self):
        # TODO fix
        return exclusions.closed()

    @property
    def schema_create_delete(self):
        return exclusions.open()

    @property
    def savepoints(self):
        return exclusions.open()

    @property
    def has_temp_table(self):
        return exclusions.open()

    @property
    def unicode_ddl(self):
        return exclusions.open()

    @property
    def update_from(self):
        return exclusions.open()

    @property
    def delete_from(self):
        return exclusions.open()

    @property
    def mod_operator_as_percent_sign(self):
        return exclusions.open()

    @property
    def order_by_label_with_expression(self):
        return exclusions.open()

    @property
    def graceful_disconnects(self):
        return exclusions.open()
