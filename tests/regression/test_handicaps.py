"""
Regression tests for handicaps.

Makes use of syrupy to compare to previously calculated values.
Loops over many rounds for each handicap scheme.
Also serves as a regression test for default rounds.
"""

import json
import re

import numpy as np
import pytest

import archeryutils.handicaps as hc
from archeryutils import load_rounds

ALL_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_indoor.json",
        "WA_indoor.json",
        "AA_indoor.json",
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
        "WA_experimental.json",
        "AA_outdoor_metric.json",
        "WA_field.json",
        "AA_field.json",
        "IFAA_field.json",
        "AGB_VI.json",
        "WA_VI.json",
        "Miscellaneous.json",
    ]
)

SUBSET_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_indoor.json",
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ]
)


@pytest.mark.parametrize("scheme", ["AGB", "AGBold", "AA", "AA2"])
def test_handicap_schemes_rounds(snapshot, capsys, scheme) -> None:
    """
    Loop over handicap schemes generating handicap tables for all rounds.

    Generate integer precision tables displaying as int with gaps.
    Use captured print as snapshot.
    """
    handicap_array = np.arange(-10, 151, 1)

    table = hc.HandicapTable(
        scheme,
        handicap_array,
        ALL_ROUNDS.values(),
        int_prec=True,
        rounded_scores=True,
        clean_gaps=True,
    )
    table.print()
    captured = capsys.readouterr()

    assert captured.out == snapshot


@pytest.mark.parametrize("scheme", ["AGB", "AGBold", "AA", "AA2"])
def test_handicap_schemes_float(snapshot, capsys, scheme) -> None:
    """
    Loop over handicap schemes generating handicap tables for all rounds.

    Use floats for handicaps and scores.
    Check a reduced range of rounds and handicaps.
    """
    handicap_array = np.arange(0, 10, 0.1)

    table = hc.HandicapTable(
        scheme,
        handicap_array,
        SUBSET_ROUNDS.values(),
        int_prec=False,
        rounded_scores=False,
        clean_gaps=False,
    )
    table.print()
    captured = capsys.readouterr()

    assert captured.out == snapshot
