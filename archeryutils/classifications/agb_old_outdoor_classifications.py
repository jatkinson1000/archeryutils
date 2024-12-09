"""
Code for calculating old (pre-2023) Archery GB outdoor classifications.

Routine Listings
----------------
calculate_agb_old_outdoor_classification
agb_old_outdoor_classification_scores
"""

from typing import TypedDict

import numpy as np
import numpy.typing as npt

import archeryutils.classifications.classification_utils as cls_funcs
import archeryutils.handicaps as hc
from archeryutils import load_rounds

ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ],
)

P = 50 #placeholder
FACTORS = np.linspace(0.1, 1.9, 6) # temporary scaling factors to produce different scores for testing

class GroupData(TypedDict):
    """Structure for old AGB Outdoor classification data."""

    classes: list[str]
    class_HC: npt.NDArray[np.float64]
    min_dists: npt.NDArray[np.float64]

def _make_agb_old_outdoor_classification_dict():
    # CHECK: happy with abbreviations, correct label for junior bowman?
    agb_outdoor_adult_classes = ["GMB", "MB", "B", "1ST", "2ND", "3RD"]
    agb_outdoor_junior_classes = ["JMB", "JB", "1ST", "2ND", "3RD"]

    bowstyles = ["Compound", "Recurve", "Barebow", "Longbow"]
    age_groups = ["Adult", "Under 18", "Under 16", "Under 14", "Under 12"]

    # explicit construction
    # no systematic generation of handicap thresholds in the old system,
    # all were set manually by attempting to fit to data

    handicap_thresholds = {
        ("Compound", "Male", "Adult"): [P, P, P, P, P, P],
        ("Compound", "Female", "Adult"): [P, P, P, P, P, P],
        ("Recurve", "Male", "Adult"):  [P, P, P, P, P, P],
        ("Recurve", "Female", "Adult"):  [P, P, P, P, P, P],
        ("Barebow", "Male", "Adult"):  [P, P, P, P, P, P],
        ("Barebow", "Female", "Adult"):  [P, P, P, P, P, P],
        ("Longbow", "Male", "Adult"):  [P, P, P, P, P, P],
        ("Longbow", "Female", "Adult"):  [P, P, P, P, P, P],
        ("Compound", "Male", "Under 18"): [P, P, P, P, P],
        ("Compound", "Female", "Under 18"): [P, P, P, P, P],
        ("Compound", "Male", "Under 16"): [P, P, P, P, P],
        ("Compound", "Female", "Under 16"): [P, P, P, P, P],
        ("Compound", "Male", "Under 14"): [P, P, P, P, P],
        ("Compound", "Female", "Under 14"): [P, P, P, P, P],
        ("Compound", "Male", "Under 12"): [P, P, P, P, P],
        ("Compound", "Female", "Under 12"): [P, P, P, P, P],
        ("Recurve", "Male", "Under 18"): [P, P, P, P, P],
        ("Recurve", "Female", "Under 18"): [P, P, P, P, P],
        ("Recurve", "Male", "Under 16"): [P, P, P, P, P],
        ("Recurve", "Female", "Under 16"): [P, P, P, P, P],
        ("Recurve", "Male", "Under 14"): [P, P, P, P, P],
        ("Recurve", "Female", "Under 14"): [P, P, P, P, P],
        ("Recurve", "Male", "Under 12"): [P, P, P, P, P],
        ("Recurve", "Female", "Under 12"): [P, P, P, P, P],
        ("Barebow", "Male", "Under 18"): [P, P, P, P, P],
        ("Barebow", "Female", "Under 18"): [P, P, P, P, P],
        ("Barebow", "Male", "Under 16"): [P, P, P, P, P],
        ("Barebow", "Female", "Under 16"): [P, P, P, P, P],
        ("Barebow", "Male", "Under 14"): [P, P, P, P, P],
        ("Barebow", "Female", "Under 14"): [P, P, P, P, P],
        ("Barebow", "Male", "Under 12"): [P, P, P, P, P],
        ("Barebow", "Female", "Under 12"): [P, P, P, P, P],
        ("Longbow", "Male", "Under 18"): [P, P, P, P, P],
        ("Longbow", "Female", "Under 18"): [P, P, P, P, P],
        ("Longbow", "Male", "Under 16"): [P, P, P, P, P],
        ("Longbow", "Female", "Under 16"): [P, P, P, P, P],
        ("Longbow", "Male", "Under 14"): [P, P, P, P, P],
        ("Longbow", "Female", "Under 14"): [P, P, P, P, P],
        ("Longbow", "Male", "Under 12"): [P, P, P, P, P],
        ("Longbow", "Female", "Under 12"): [P, P, P, P, P],
    }

    min_distances = {
        ("Male", "Adult"): [90, 90, 90, 70, 60, 50],
        ("Female", "Adult"): [70, 70, 70, 60, 50, 40],
        ("Male", "Under 18"): [70, 70, 70, 60, 50, 40],
        ("Female", "Under 18"): [60, 60, 60, 50, 40, 30],
        ("Male", "Under 16"): [60, 60, 60, 50, 40, 30],
        ("Female", "Under 16"): [50, 50, 50, 40, 30, 20],
        ("Male", "Under 14"): [50, 50, 50, 40, 30, 20],
        ("Female", "Under 14"): [40, 40, 40, 30, 20, 15],
        ("Male", "Under 12"): [40, 40, 40, 30, 20, 15],
        ("Female", "Under 12"): [30, 30, 30 ,20 ,15 ,10], #Not sure if 10 is necessary here
    }

    classification_dict = {}

    for (bowstyle, gender, age_group), handicaps in handicap_thresholds.items():
        groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
        class_names = agb_outdoor_adult_classes if age_group == "Adult" else agb_outdoor_junior_classes

        # temporary factor adjustment for placeholder handicaps, remove
        factors = FACTORS if age_group == "Adult" else FACTORS[:5]

        groupdata: GroupData = {
            "classes": class_names,
            "class_HC": np.array(handicaps) * factors,
            "min_dists": np.array(min_distances[(gender, age_group)]),
        }

        classification_dict[groupname] = groupdata

    return classification_dict


agb_old_outdoor_classifications = _make_agb_old_outdoor_classification_dict()

del _make_agb_old_outdoor_classification_dict

def calculate_agb_old_outdoor_classification(
    score: float,
    roundname: str,
    bowstyle: str,
    gender: str,
    age_group: str,
) -> str:

    # Check score is valid
    if score < 0 or score > ALL_OUTDOOR_ROUNDS[roundname].max_score():
        msg = (
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_OUTDOOR_ROUNDS[roundname].max_score()}.",
        )
        raise ValueError(msg)

    # Get scores required on this round for each classification
    class_scores = agb_old_outdoor_classification_scores(
        roundname,
        bowstyle,
        gender,
        age_group,
    )

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_old_outdoor_classifications[groupname]
    class_data = dict(zip(group_data["classes"], class_scores, strict=True))


    for classname, classscore in class_data.items():
        if classscore > score:
            continue
        else:
            return classname
    return "UC"


def agb_old_outdoor_classification_scores(
    roundname: str,
    bowstyle: str,
    gender: str,
    age_group: str,
) -> list[int]:

    # map newer age categories to supported subset
    if (age:= age_group.lower().replace(" ","")) in ("adult", "50+", "under21"):
        age = "Adult"
    elif age == "under15":
        age = "Under 16"

    groupname = cls_funcs.get_groupname(bowstyle, gender, age)
    group_data = agb_old_outdoor_classifications[groupname]

    # Get scores required on this round for each classification
    class_scores = [
        hc.score_for_round(
                handicap=group_data["class_HC"][i],
                rnd=ALL_OUTDOOR_ROUNDS[cls_funcs.strip_spots(roundname)],
                handicap_sys="AGBold",
                rounded_score=True,
            )
        for i, class_i in enumerate(group_data["classes"])
    ]

    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
