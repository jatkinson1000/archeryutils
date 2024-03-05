"""Module providing various handicap functionalities."""

from .handicap_functions import (
    arrow_score,
    handicap_from_score,
    handicap_scheme,
    score_for_passes,
    score_for_round,
)
from .handicap_scheme import FloatArray, HandicapScheme
from .handicap_scheme_aa import HandicapAA, HandicapAA2
from .handicap_scheme_agb import HandicapAGB, HandicapAGBold
from .handicap_tables import HandicapTable

__all__ = [
    "FloatArray",
    "HandicapTable",
    "handicap_scheme",
    "arrow_score",
    "score_for_passes",
    "score_for_round",
    "handicap_from_score",
    "HandicapScheme",
    "HandicapAGB",
    "HandicapAGBold",
    "HandicapAA",
    "HandicapAA2",
]
