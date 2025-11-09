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
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ],
)

old_outdoor_bowstyles = (
    AGB_bowstyles.COMPOUND
    | AGB_bowstyles.RECURVE
    | AGB_bowstyles.BAREBOW
    | AGB_bowstyles.LONGBOW
)
old_outdoor_ages = AGB_ages.AGE_ADULT

P = 50  # placeholder
FACTORS = np.linspace(
    0.1, 1.9, 6
)  # temporary scaling factors to produce different scores for testing


class GroupData(TypedDict):
    """Structure for old AGB Outdoor classification data."""

    classes: list[str]
    class_HC: npt.NDArray[np.float64]
    min_dists: npt.NDArray[np.float64]
    min_dozens: npt.NDArray[np.float64]


def _get_old_outdoor_groupname(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Wrap function to generate string id for a particular category with indoor guards.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB indoor target rules
    gender : AGB_genders
        archer's gender under AGB indoor target rules
    age_group : AGB_ages
        archer's age group under AGB indoor target rules

    Returns
    -------
    groupname : str
        single str id for this category
    """
    return cls_funcs.get_groupname(bowstyle, gender, age_group)

def _make_agb_old_outdoor_classification_dict() -> dict[str, GroupData]:
    # CHECK: happy with abbreviations, correct label for junior bowman?
    agb_outdoor_adult_classes = ["GMB", "MB", "B", "1ST", "2ND", "3RD"]
    agb_outdoor_junior_classes = ["JMB", "JB", "1ST", "2ND", "3RD"]

    bowstyles = ["Compound", "Recurve", "Barebow", "Longbow"]
    age_groups = ["Adult", "Under 18", "Under 16", "Under 14", "Under 12"]

    # explicit construction
    # no systematic generation of handicap thresholds in the old system,
    # all were set manually by attempting to fit to data
    B = AGB_bowstyles
    G = AGB_genders
    A = AGB_ages

    handicap_thresholds = {
        (B.COMPOUND, G.MALE, A.AGE_ADULT):[10, 16, 23, 32, 38, 48],
        (B.COMPOUND, G.FEMALE, A.AGE_ADULT):[15, 21, 29, 38, 49, 56],
        (B.RECURVE, G.MALE, A.AGE_ADULT):[22, 28, 36, 44, 50, 58],
        (B.RECURVE, G.FEMALE, A.AGE_ADULT):[27, 33, 41, 50, 57, 65],
        (B.BAREBOW, G.MALE, A.AGE_ADULT):[40, 45, 49, 56, 64, 71],
        (B.BAREBOW, G.FEMALE, A.AGE_ADULT):[49, 51, 57, 64, 71, 78],
        (B.LONGBOW, G.MALE, A.AGE_ADULT):[52, 55, 60, 65, 69, 74],
        (B.LONGBOW, G.FEMALE, A.AGE_ADULT):[59, 62, 65, 70, 73, 82],
        (B.COMPOUND, G.MALE, A.AGE_UNDER_18): [23, 32, 38, 48, 56],
        (B.COMPOUND, G.FEMALE, A.AGE_UNDER_18): [29, 38, 49, 56, 66],
        (B.COMPOUND, G.MALE, A.AGE_UNDER_16): [32, 38, 48, 56, 61],
        (B.COMPOUND, G.FEMALE, A.AGE_UNDER_16): [38, 49, 56, 66, 74],
        (B.COMPOUND, G.MALE, A.AGE_UNDER_14): [38, 48, 56, 61, 69],
        (B.COMPOUND, G.FEMALE, A.AGE_UNDER_14): [46, 55, 65, 75, 84],
        (B.COMPOUND, G.MALE, A.AGE_UNDER_12): [48, 56, 61, 71, 79],
        (B.COMPOUND, G.FEMALE, A.AGE_UNDER_12): [54, 63, 73, 83, 91],
        (B.RECURVE, G.MALE, A.AGE_UNDER_18): [31, 39, 50, 58, 68],
        (B.RECURVE, G.FEMALE, A.AGE_UNDER_18): [41, 48, 57, 64, 70],
        (B.RECURVE, G.MALE, A.AGE_UNDER_16): [40, 48, 56, 62, 71],
        (B.RECURVE, G.FEMALE, A.AGE_UNDER_16): [50, 58, 66, 72, 76],
        (B.RECURVE, G.MALE, A.AGE_UNDER_14): [50, 58, 66, 71, 79],
        (B.RECURVE, G.FEMALE, A.AGE_UNDER_14): [56, 64, 73, 80, 87],
        (B.RECURVE, G.MALE, A.AGE_UNDER_12): [61, 69, 77, 83, 92],
        (B.RECURVE, G.FEMALE, A.AGE_UNDER_12): [65, 70, 78, 87, 93],
        (B.BAREBOW, G.MALE, A.AGE_UNDER_18): [50, 57, 62, 68, 73],
        (B.BAREBOW, G.FEMALE, A.AGE_UNDER_18): [54, 59, 64, 69, 73],
        (B.BAREBOW, G.MALE, A.AGE_UNDER_16): [53, 60, 65, 70, 75],
        (B.BAREBOW, G.FEMALE, A.AGE_UNDER_16): [59, 65, 70, 74, 79],
        (B.BAREBOW, G.MALE, A.AGE_UNDER_14): [60, 67, 72, 77, 83],
        (B.BAREBOW, G.FEMALE, A.AGE_UNDER_14): [67, 72, 77, 83, 90],
        (B.BAREBOW, G.MALE, A.AGE_UNDER_12): [69, 75, 81, 88, 95],
        (B.BAREBOW, G.FEMALE, A.AGE_UNDER_12): [73, 78, 84, 90, 96],
        (B.LONGBOW, G.MALE, A.AGE_UNDER_18): [56, 62, 67, 73, 79],
        (B.LONGBOW, G.FEMALE, A.AGE_UNDER_18): [61, 64, 68, 73, 77],
        (B.LONGBOW, G.MALE, A.AGE_UNDER_16): [60, 65, 70, 75, 81],
        (B.LONGBOW, G.FEMALE, A.AGE_UNDER_16): [66, 70, 74, 78, 83],
        (B.LONGBOW, G.MALE, A.AGE_UNDER_14): [66, 72, 77, 82, 87],
        (B.LONGBOW, G.FEMALE, A.AGE_UNDER_14): [72, 77, 82, 87, 95],
        (B.LONGBOW, G.MALE, A.AGE_UNDER_12): [75, 81, 87, 93, 99],
        (B.LONGBOW, G.FEMALE, A.AGE_UNDER_12): [78, 83, 88, 94, 99],
    }

    prerequisites = {
        (G.MALE, A.AGE_ADULT): {
            "min_dist": [90, 90, 90, 70, 60, 50],
            "min_dozen": [12, 12, 0, 0, 0, 0],
        },
        (G.FEMALE, A.AGE_ADULT): {
            "min_dist": [70, 70, 70, 60, 50, 40],
            "min_dozen": [12, 12, 0, 0, 0, 0],
        },
        (G.MALE, A.AGE_UNDER_18): {
            "min_dist": [70, 70, 60, 50, 40],
            "min_dozen": [12, 0, 0, 0, 0],
        },
        (G.FEMALE, A.AGE_UNDER_18): {
            "min_dist": [60, 60, 50, 40, 30],
            "min_dozen": [12, 0, 0, 0, 0],
        },
        (G.MALE, A.AGE_UNDER_16): {
            "min_dist": [60, 60, 50, 40, 30],
            "min_dozen": [12, 0, 0, 0, 0],
        },
        (G.FEMALE, A.AGE_UNDER_16): {
            "min_dist": [50, 50, 40, 30, 20],
            "min_dozen": [12, 0, 0, 0, 0],
        },
        (G.MALE, A.AGE_UNDER_14): {
            "min_dist": [50, 50, 40, 30, 20],
            "min_dozen": [12, 0, 0, 0, 0],
        },
        (G.FEMALE, A.AGE_UNDER_14): {
            "min_dist": [40, 40, 30, 20, 15],
            "min_dozen": [12, 0, 0, 0, 0],
        },
        (G.MALE, A.AGE_UNDER_12): {
            "min_dist": [40, 40, 30, 20, 15],
            "min_dozen": [12, 0, 0, 0, 0],
        },
        (G.FEMALE, A.AGE_UNDER_12): {
            "min_dist": [30, 30, 20, 15, 10],
            "min_dozen": [12, 0, 0, 0, 0],
        },
    }

    classification_dict = {}

    for (bowstyle, gender, age), handicaps in handicap_thresholds.items():
        groupname = _get_old_outdoor_groupname(bowstyle, gender, age)
        class_names = (
            agb_outdoor_adult_classes
            if age == "Adult"
            else agb_outdoor_junior_classes
        )

        requirements = prerequisites[(gender, age)]
        groupdata: GroupData = {
            "classes": class_names,
            "class_HC": np.array(handicaps),
            "min_dists": np.array(requirements["min_dist"]),
            "min_dozens": np.array(requirements["min_dozen"]),
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
    """
    Calculate AGB outdoor classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.
    Appropriate ArcheryGB age groups and classifications pre 2023.

    Parameters
    ----------
    score : int
        numerical score on the round to calculate classification for
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : str
        archer's bowstyle under AGB outdoor target rules
    gender : str
        archer's gender under AGB outdoor target rules
    age_group : str
        archer's age group under AGB outdoor target rules

    Returns
    -------
    classification_scores : ndarray
        scores required for each classification in descending order

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7

    Examples
    --------
    TBC

    """
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
    """
    Calculate AGB outdoor classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate ArcheryGB age groups and classifications pre 2023.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : str
        archer's bowstyle under AGB outdoor target rules
    gender : str
        archer's gender under AGB outdoor target rules
    age_group : str
        archer's age group under AGB outdoor target rules

    Returns
    -------
    classification_scores : ndarray
        scores required for each classification in descending order

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7

    Examples
    --------
    TBC

    """
    # map newer age categories to supported subset
    if (age := age_group.lower().replace(" ", "")) in ("adult", "50+", "under21"):
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

    # Check distance and round length requirements
    n_class = len(class_scores)
    round_max_dist = (
        ALL_OUTDOOR_ROUNDS[cls_funcs.strip_spots(roundname)].max_distance().value
    )
    round_n_dozen = (
        ALL_OUTDOOR_ROUNDS[cls_funcs.strip_spots(roundname)].n_arrows() // 12
    )

    for i in range(len(class_scores)):
        if (
            # must hit minimum distance
            group_data["min_dists"][i] > round_max_dist
            or
            # senior MB/GMB requires 12 doz. JMB??
            group_data["min_dozens"][i] > round_n_dozen
        ):
            class_scores[i] = -9999

    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
