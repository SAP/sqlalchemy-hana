"""Custom SQL elements for SAP HANA."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import table
from sqlalchemy.sql.ddl import DDLElement
from sqlalchemy.sql.selectable import Select, TableClause

if TYPE_CHECKING:
    AnySelect = Select[Any]


class CreateView(DDLElement):
    """CREATE VIEW element for SAP HANA."""

    __visit_name__ = "create_view"

    def __init__(self, name: str, selectable: AnySelect):
        self.name = name
        self.selectable = selectable


class DropView(DDLElement):
    """DROP VIEW element for SAP HANA."""

    __visit_name__ = "drop_view"

    def __init__(self, name: str):
        self.name = name


def view(name: str, selectable: AnySelect) -> TableClause:
    """Helper function to create a view clause element."""
    clause = table(name)
    clause._columns._populate_separate_keys(
        col._make_proxy(clause) for col in selectable.selected_columns
    )
    return clause


__all__ = ("CreateView", "DropView", "view")
