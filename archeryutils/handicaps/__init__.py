"""Module providing various handicap functionalities."""

from .handicap_functions import (
    arrow_score,
    handicap_from_score,
    handicap_scheme,
    score_for_passes,
    score_for_round,
)
from .handicap_scheme import FloatArray
from .handicap_tables import HandicapTable

__all__ = [
    "FloatArray",
    "HandicapTable",
    "handicap_scheme",
    "arrow_score",
    "score_for_passes",
    "score_for_round",
    "handicap_from_score",
]
