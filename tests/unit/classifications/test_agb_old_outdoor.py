"""Tests for old agb outdoor classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds

ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ],
)


class TestAgbOldIndoorClassificationScores:
    """Tests for the old_indoor classification scores function."""
    pass