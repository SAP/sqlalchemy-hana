"""SQLAlchemy requirements for testing."""

from __future__ import annotations

from alembic.testing.requirements import SuiteRequirements as AlembicRequirements
from sqlalchemy.testing import exclusions
from sqlalchemy.testing.config import Config
from sqlalchemy.testing.exclusions import compound
from sqlalchemy.testing.requirements import SuiteRequirements as SQLAlchemyRequirements


class Requirements(SQLAlchemyRequirements, AlembicRequirements):
    @property
    def views(self) -> compound:
        return exclusions.open()

    @property
    def view_reflection(self) -> compound:
        return exclusions.open()

    @property
    def reflects_pk_names(self) -> compound:
        return exclusions.open()

    @property
    def datetime_literals(self) -> compound:
        """HANA has the function to_date, to_time, to_timestamp."""
        return exclusions.open()

    @property
    def time_microseconds(self) -> compound:
        # SAP HANA does not support microseconds in TIME
        return exclusions.closed()

    @property
    def datetime_historic(self) -> compound:
        return exclusions.open()

    @property
    def date_historic(self) -> compound:
        return exclusions.open()

    @property
    def percent_schema_names(self) -> compound:
        return exclusions.open()

    @property
    def selectone(self) -> compound:
        # SAP HANA doesn't support 'SELECT 1' without 'FROM DUMMY'
        return exclusions.closed()

    @property
    def two_phase_transactions(self) -> compound:
        return exclusions.open()

    @property
    def autoincrement_without_sequence(self) -> compound:
        return exclusions.open()

    @property
    def isolation_level(self) -> compound:
        return exclusions.open()

    def get_isolation_levels(self, config: Config) -> dict[str, str | list[str]]:
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
    def autocommit(self) -> compound:
        return exclusions.open()

    @property
    def comment_reflection(self) -> compound:
        return exclusions.open()

    @property
    def sequences_optional(self) -> compound:
        return exclusions.open()

    @property
    def timestamp_microseconds(self) -> compound:
        return exclusions.open()

    @property
    def temp_table_names(self) -> compound:
        return exclusions.open()

    @property
    def tuple_in(self) -> compound:
        return exclusions.open()

    @property
    def foreign_key_constraint_option_reflection_ondelete(self) -> compound:
        return exclusions.open()

    @property
    def foreign_key_constraint_option_reflection_onupdate(self) -> compound:
        return exclusions.open()

    @property
    def check_constraint_reflection(self) -> compound:
        return exclusions.open()

    @property
    def expressions_against_unbounded_text(self) -> compound:
        # not supported by SAP HANA
        return exclusions.closed()

    @property
    def independent_readonly_connections(self) -> compound:
        # Not supported by sqlalchemy-hana
        return exclusions.closed()

    @property
    def sql_expression_limit_offset(self) -> compound:
        # SAP HANA does not support expressions in LIMIT or OFFSET
        return exclusions.closed()

    @property
    def array_type(self) -> compound:
        # Not yet supported, #119
        return exclusions.closed()

    @property
    def unbounded_varchar(self) -> compound:
        # SAP HANA requires a length vor (N)VARCHAR
        return exclusions.closed()

    @property
    def unique_index_reflect_as_unique_constraints(self) -> compound:
        # SAP HANA reflects unique indexes as unique constraints
        return exclusions.open()

    @property
    def unique_constraints_reflect_as_index(self) -> compound:
        # SAP HANA reflects unique constraints as indexes
        return exclusions.open()

    @property
    def intersect(self) -> compound:
        return exclusions.open()

    @property
    def except_(self) -> compound:
        return exclusions.open()

    @property
    def window_functions(self) -> compound:
        return exclusions.open()

    @property
    def comment_reflection_full_unicode(self) -> compound:
        return exclusions.open()

    @property
    def foreign_key_constraint_name_reflection(self) -> compound:
        return exclusions.open()

    @property
    def cross_schema_fk_reflection(self) -> compound:
        return exclusions.open()

    @property
    def fk_constraint_option_reflection_onupdate_restrict(self) -> compound:
        return exclusions.open()

    @property
    def fk_constraint_option_reflection_ondelete_restrict(self) -> compound:
        return exclusions.open()

    @property
    def schema_create_delete(self) -> compound:
        return exclusions.open()

    @property
    def savepoints(self) -> compound:
        return exclusions.open()

    @property
    def has_temp_table(self) -> compound:  # noqa: FTP093
        return exclusions.open()

    @property
    def unicode_ddl(self) -> compound:
        return exclusions.open()

    @property
    def update_from(self) -> compound:
        return exclusions.open()

    @property
    def delete_from(self) -> compound:
        return exclusions.open()

    @property
    def mod_operator_as_percent_sign(self) -> compound:
        return exclusions.open()

    @property
    def order_by_label_with_expression(self) -> compound:
        return exclusions.open()

    @property
    def graceful_disconnects(self) -> compound:
        return exclusions.open()

    @property
    def uuid_data_type(self) -> compound:
        return exclusions.closed()

    @property
    def regexp_match(self) -> compound:
        return exclusions.open()

    @property
    def regexp_replace(self) -> compound:
        return exclusions.open()

    @property
    def precision_numerics_general(self) -> compound:
        return exclusions.open()

    @property
    def precision_numerics_enotation_small(self) -> compound:
        return exclusions.open()

    @property
    def precision_numerics_many_significant_digits(self) -> compound:
        return exclusions.open()

    @property
    def boolean_col_expressions(self) -> compound:
        return exclusions.open()

    @property
    def ctes(self) -> compound:
        return exclusions.open()

    @property
    def ctes_with_update_delete(self) -> compound:
        return exclusions.closed()

    @property
    def fk_ondelete_noaction(self) -> compound:
        return exclusions.closed()

    @property
    def autocommit_isolation(self) -> compound:
        return exclusions.open()

    @property
    def unique_constraint_reflection(self) -> compound:
        return exclusions.open()

    @property
    def reflects_fk_options(self) -> compound:
        return exclusions.open()

    @property
    def fk_ondelete_is_reflected(self) -> compound:
        return exclusions.open()

    @property
    def fk_onupdate_is_reflected(self) -> compound:
        return exclusions.open()

    @property
    def computed_reflects_as_server_default(self) -> compound:
        return exclusions.closed()

    @property
    def computed_doesnt_reflect_as_server_default(self) -> compound:
        return exclusions.closed()

    @property
    def computed_columns(self) -> compound:
        return exclusions.open()

    @property
    def computed_columns_stored(self) -> compound:
        # not supported by SAP HANA
        return exclusions.open()

    @property
    def computed_columns_virtual(self) -> compound:
        # not supported by SAP HANA
        return exclusions.open()

    @property
    def computed_columns_default_persisted(self) -> compound:
        return exclusions.open()

    @property
    def computed_columns_reflect_persisted(self) -> compound:
        return exclusions.open()

    @property
    def identity_columns(self) -> compound:
        return exclusions.open()

    @property
    def identity_columns_alter(self) -> compound:
        # SAP HANA does not return the semantics of an identity column
        # Therefore, no diff can be calculated
        return exclusions.closed()

    @property
    def identity_columns_standard(self) -> compound:
        return exclusions.open()

    @property
    def autoincrement_insert(self) -> compound:
        return exclusions.open()

    @property
    def json_type(self) -> compound:
        return exclusions.open()

    @property
    def nvarchar_types(self) -> compound:
        return exclusions.open()

    @property
    def skip_autocommit_rollback(self) -> compound:
        return exclusions.closed()

    @property
    def ctes_with_values(self) -> compound:
        return exclusions.closed()

    @property
    def temp_table_comment_reflection(self) -> compound:
        return exclusions.open()
