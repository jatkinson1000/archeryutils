"""
Regression tests for classifications.

Makes use of syrupy to compare to previously calculated values.
Loops over all eligible rounds, ages, genders, bowstyles for each classification type.
"""

import json
import re

import pytest

import archeryutils.classifications as cf
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

ALL_INDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_indoor.json",
        "WA_indoor.json",
    ],
)
ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ],
)
ALL_FIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ]
)

field_ages = (
    AGB_ages.AGE_50_PLUS
    | AGB_ages.AGE_ADULT
    | AGB_ages.AGE_UNDER_18
    | AGB_ages.AGE_UNDER_16
    | AGB_ages.AGE_UNDER_15
    | AGB_ages.AGE_UNDER_14
    | AGB_ages.AGE_UNDER_12
)

target_bowstyles = (
    AGB_bowstyles.COMPOUND
    | AGB_bowstyles.RECURVE
    | AGB_bowstyles.BAREBOW
    | AGB_bowstyles.LONGBOW
)


@pytest.mark.parametrize("bowstyle", target_bowstyles)
@pytest.mark.parametrize("gender", AGB_genders)
@pytest.mark.parametrize("age", AGB_ages)
def test_indoor_classification_scores(snapshot, bowstyle, gender, age) -> None:
    """Loop over indoor target rounds and parameters to snapshot test."""
    actual_scores = {}
    for archery_round in ALL_INDOOR_ROUNDS.values():
        actual_scores[archery_round.codename] = cf.agb_indoor_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age,
        )

    assert json.dumps(actual_scores) == snapshot


@pytest.mark.parametrize("bowstyle", target_bowstyles)
@pytest.mark.parametrize("gender", AGB_genders)
@pytest.mark.parametrize("age", AGB_ages)
def test_outdoor_classification_scores(snapshot, bowstyle, gender, age) -> None:
    """Loop over outdoor target rounds and parameters to snapshot test."""
    actual_scores = {}
    for archery_round in ALL_OUTDOOR_ROUNDS.values():
        actual_scores[archery_round.codename] = cf.agb_outdoor_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age,
        )

    assert json.dumps(actual_scores) == snapshot


@pytest.mark.parametrize("bowstyle", AGB_bowstyles)
@pytest.mark.parametrize("gender", AGB_genders)
@pytest.mark.parametrize("age", field_ages)
def test_field_classification_scores(snapshot, bowstyle, gender, age) -> None:
    """Loop over field rounds and parameters to snapshot test."""
    actual_scores = {}
    for archery_round in ALL_FIELD_ROUNDS.values():
        actual_scores[archery_round.codename] = cf.agb_field_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age,
        )

    assert json.dumps(actual_scores) == snapshot


@pytest.mark.parametrize("bowstyle", AGB_bowstyles.COMPOUND | AGB_bowstyles.RECURVE)
@pytest.mark.parametrize("gender", AGB_genders)
def test_old_indoor_classification_scores(snapshot, bowstyle, gender) -> None:
    """Loop over indoor target rounds and parameters to snapshot test."""
    actual_scores = {}
    for archery_round in ALL_INDOOR_ROUNDS.values():
        actual_scores[archery_round.codename] = cf.agb_old_indoor_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=AGB_ages.AGE_ADULT,
        )

    assert json.dumps(actual_scores) == snapshot


@pytest.mark.parametrize("bowstyle", AGB_bowstyles)
@pytest.mark.parametrize("gender", AGB_genders)
@pytest.mark.parametrize("age", AGB_ages.AGE_ADULT | AGB_ages.AGE_UNDER_18)
def test_old_field_classification_scores(snapshot, bowstyle, gender, age) -> None:
    """Loop over field rounds and parameters to snapshot test."""
    actual_scores = {}
    for archery_round in ALL_FIELD_ROUNDS.values():
        actual_scores[archery_round.codename] = cf.agb_old_field_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age,
        )

    assert json.dumps(actual_scores) == snapshot
