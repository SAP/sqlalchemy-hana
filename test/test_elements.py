"""test sqlalchemy.elements."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Table, inspect, select
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.testing.config import fixture
from sqlalchemy.testing.fixtures import TablesTest

from sqlalchemy_hana.elements import CreateView, DropView, upsert, view


class TestViews(TablesTest):
    @classmethod
    def define_tables(cls, metadata):
        Table(
            "test_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("value", String(10)),
        )

    @classmethod
    def insert_data(cls, connection):
        connection.execute(
            cls.tables.test_table.insert(),
            [
                {"id": 1, "value": "data1"},
                {"id": 2, "value": "data2"},
                {"id": 3, "value": "data1"},
            ],
        )

    @fixture(autouse=True)
    def define_views(self, connection_no_trans, selectable):
        ddl = CreateView("my_view", selectable)
        with connection_no_trans.begin():
            connection_no_trans.execute(ddl)
        yield

        with connection_no_trans.begin():
            for view_name in inspect(connection_no_trans).get_view_names():
                connection_no_trans.execute(DropView(view_name))

    @fixture
    def selectable(self):
        table = self.tables.test_table
        return select(table.c.id, table.c.value).where(table.c.value == "data1")

    def test_select(self, connection, selectable):
        my_view = view("my_view", selectable)
        assert my_view.primary_key == [my_view.c.id]

        assert connection.execute(select(my_view.c.id, my_view.c.value)).all() == [
            (1, "data1"),
            (3, "data1"),
        ]

    def test_drop(self, connection):
        ddl = DropView("my_view")
        connection.execute(ddl)
        assert not inspect(connection).get_view_names()

    def test_orm(self, connection, metadata, selectable):
        # pylint: disable=invalid-name
        my_view = view("my_view", selectable)
        Base = declarative_base(metadata=metadata)

        class MyModel(Base):
            __table__ = my_view

        result = Session(connection).query(MyModel).all()
        assert result[0].id == 1
        assert result[1].id == 3


class TestUpsert(TablesTest):
    @classmethod
    def define_tables(cls, metadata):
        Table(
            "test_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("value", String(10)),
        )

    @classmethod
    def insert_data(cls, connection):
        connection.execute(
            cls.tables.test_table.insert(),
            [
                {"id": 1, "value": "data1"},
                {"id": 2, "value": "data2"},
                {"id": 3, "value": "data3"},
            ],
        )

    def test_upsert_as_insert(self, connection):
        table = self.tables.test_table
        connection.execute(upsert(table).values(id=4, value="data4").filter_by(id=4))

        select_stmt = select(table.c.id, table.c.value).order_by(table.c.id)
        assert connection.execute(select_stmt).all() == [
            (1, "data1"),
            (2, "data2"),
            (3, "data3"),
            (4, "data4"),
        ]

    def test_upsert_as_update(self, connection):
        table = self.tables.test_table
        connection.execute(upsert(table).values(id=2, value="dataX").filter_by(id=2))

        select_stmt = select(table.c.id, table.c.value).order_by(table.c.id)
        assert connection.execute(select_stmt).all() == [
            (1, "data1"),
            (2, "dataX"),
            (3, "data3"),
        ]
