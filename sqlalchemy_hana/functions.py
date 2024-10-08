# pylint: disable=invalid-name
"""Custom SQL functions for SAP HANA."""

from __future__ import annotations

from typing import Generic

from sqlalchemy import Float, Integer
from sqlalchemy.sql.functions import GenericFunction

from sqlalchemy_hana.types import _RV, REAL_VECTOR


class cardinality(GenericFunction[int]):
    type = Integer()
    inherit_cache = True
    _has_args = True


class cosine_similarity(GenericFunction[float]):
    type = Float()
    inherit_cache = True
    _has_args = True


class l2distance(GenericFunction[float]):
    type = Float()
    inherit_cache = True
    _has_args = True


class to_real_vector(GenericFunction[_RV], Generic[_RV]):
    type = REAL_VECTOR[_RV]()
    inherit_cache = True
    _has_args = True


__all__ = ("cardinality", "cosine_similarity", "l2distance", "to_real_vector")
