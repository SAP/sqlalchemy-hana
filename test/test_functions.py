"""SQL function tests."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.testing.assertions import eq_
from sqlalchemy.testing.fixtures import TestBase

from sqlalchemy_hana.functions import (
    cardinality,
    cosine_similarity,
    l2distance,
    to_real_vector,
)


class FunctionTest(TestBase):

    def test_cardinality(self, connection):
        res = connection.execute(select(cardinality(to_real_vector("[1, 2, 3]")))).one()
        eq_(res, (3,))

    def test_cosine_similarity(self, connection):
        res = connection.execute(
            select(
                cosine_similarity(
                    to_real_vector("[1, 0, 0]"), to_real_vector("[0.5, 0.8660254, 0]")
                )
            )
        ).one()
        eq_(res, (0.5,))

    def test_l2distance(self, connection):
        res = connection.execute(
            select(l2distance(to_real_vector("[2, 3, 5]"), to_real_vector("[6, 6, 5]")))
        ).one()
        eq_(res, (5,))
