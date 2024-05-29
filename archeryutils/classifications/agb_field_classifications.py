"""
Code for calculating Archery GB Field classifications.

Routine Listings
----------------
_make_agb_field_classification_dict
calculate_agb_field_classification
agb_field_classification_scores
"""

from typing import Any, TypedDict

import numpy as np
import numpy.typing as npt

import archeryutils.classifications.classification_utils as cls_funcs
import archeryutils.handicaps as hc
from archeryutils import load_rounds

ALL_FIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ]
)


class GroupData(TypedDict):
    """Structure for AGB Field classification data."""

    classes: list[str]
    classes_long: list[str]
    class_HC: npt.NDArray[np.float64]
    dists: list[int]


def _make_agb_field_classification_dict() -> dict[str, GroupData]:
    """
    Generate AGB field classification data.

    Generate a dictionary of dictionaries providing handicaps for each
    classification band and a list prestige rounds for each category from data files.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    None

    Returns
    -------
    classification_dict : dict of str : GroupData
        dictionary indexed on group name (e.g 'adult_female_barebow')
        containing list of handicaps associated with each classification,
        a list of prestige rounds eligible for that group, and a list of
        the maximum distances available to that group

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # Read in age group info as list of dicts
    agb_ages_full = cls_funcs.read_ages_json()
    # Restrict Age groups to those for field
    agb_ages: list[cls_funcs.AGBAgeData] = [
        item
        for item in agb_ages_full
        if item["age_group"].lower().replace(" ", "") not in ["under21"]
    ]
    # Read in bowstyleclass info as list of dicts
    agb_bowstyles = cls_funcs.read_bowstyles_json()
    # Read in gender info as list of dicts
    agb_genders = cls_funcs.read_genders_json()
    # Read in classification names as dict
    agb_classes_info_field = cls_funcs.read_classes_json("agb_field")
    agb_classes_field = agb_classes_info_field["classes"]
    agb_classes_field_long = agb_classes_info_field["classes_long"]

    # Generate dict of classifications
    # loop over bowstyles
    # loop over genders
    # loop over ages
    classification_dict = {}
    for bowstyle in agb_bowstyles:
        for gender in agb_genders:
            for age in agb_ages:
                groupname = cls_funcs.get_groupname(
                    bowstyle["bowstyle"], gender, age["age_group"]
                )

                # set step from datum based on age and gender steps required
                delta_hc_age_gender = cls_funcs.get_age_gender_step(
                    gender,
                    age["step"],
                    bowstyle["ageStep_field"],
                    bowstyle["genderStep_field"],
                )

                classifications_count = len(agb_classes_field)

                class_hc = np.empty(classifications_count)

                for i in range(classifications_count):
                    # Assign handicap for this classification
                    class_hc[i] = (
                        bowstyle["datum_field"]
                        + delta_hc_age_gender
                        + (i - 2) * bowstyle["classStep_field"]
                    )

                groupdata: GroupData = {
                    "classes": agb_classes_field,
                    "classes_long": agb_classes_field_long,
                    "class_HC": class_hc,
                    "dists": _assign_dists(bowstyle["bowstyle"], age),
                }

                classification_dict[groupname] = groupdata

    return classification_dict


def _assign_dists(
    bowstyle: str,
    age: cls_funcs.AGBAgeData,
) -> list[int]:
    """
    Assign appropriate minimum distance required for a category and classification.

    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    bowstyle : str,
        string defining bowstyle
    age : dict[str, any],
        dict containing age group data

    Returns
    -------
    dists : list[float]
        [minimum, maximum] distances required for this classification

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    World Archery Rulebook
    """
    # WA
    # Red - R/C/CL
    # Blue - Barebow, U18 R/C
    # Yellow - U18 BB
    # AGB
    #
    # U18 R/C/CL Red, Others Blue
    # U15 All Blue, R/C Red, Others White
    # U12 R/C/CL Red, All Blue, All White,
    if bowstyle.lower().replace(" ", "") in ("compound", "recurve", "compoundlimited"):
        return age["red"]
    return age["blue"]


agb_field_classifications = _make_agb_field_classification_dict()

del _make_agb_field_classification_dict


def calculate_agb_field_classification(
    score: float, roundname: str, bowstyle: str, gender: str, age_group: str
) -> str:
    """
    Calculate AGB field classification from score.

    Calculate a classification from a score given suitable inputs.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    score : int
        numerical score on the round to calculate classification for
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : str
        archer's bowstyle under AGB field target rules
    gender : str
        archer's gender under AGB field target rules
    age_group : str
        archer's age group under AGB field target rules

    Returns
    -------
    classification_from_score : str
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # Check score is valid
    if score < 0 or score > ALL_FIELD_ROUNDS[roundname].max_score():
        msg = (
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_FIELD_ROUNDS[roundname].max_score()}."
        )
        raise ValueError(msg)

    # Enforce unmarked/mixed being same score as marked
    roundname = roundname.replace("unmarked", "marked")
    roundname = roundname.replace("mixed", "marked")

    # Check round is long enough (no classifications for 12-target passes)
    if "12" in roundname:
        return "UC"

    group_data = agb_field_classifications[
        cls_funcs.get_groupname(bowstyle, gender, age_group)
    ]

    # Check if this round is an appropriate distance
    round_max_dist = ALL_FIELD_ROUNDS[roundname].max_distance().value
    if round_max_dist < group_data["dists"][0]:
        return "UC"
    if round_max_dist > group_data["dists"][1]:
        return "UC"

    # Get scores required on this round for each classification
    # Enforcing full size face and compound scoring (for compounds)
    all_class_scores = agb_field_classification_scores(
        roundname,
        bowstyle,
        gender,
        age_group,
    )

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_field_classifications[groupname]
    class_data = dict(zip(group_data["classes"], all_class_scores, strict=True))

    # Of the classes remaining, what is the highest classification this score gets?
    # < 0 handles max scores, > score handles higher classifications
    for classname, classscore in class_data.items():
        if classscore < 0 or classscore > score:
            continue
        else:
            return classname
    return "UC"


def agb_field_classification_scores(
    roundname: str, bowstyle: str, gender: str, age_group: str
) -> list[int]:
    """
    Calculate AGB field classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : str
        archer's bowstyle under AGB field target rules
    gender : str
        archer's gender under AGB field target rules
    age_group : str
        archer's age group under AGB field target rules

    Returns
    -------
    classification_scores : ndarray
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_field_classifications[groupname]

    # Enforce unmarked/mixed being same score as marked
    roundname = roundname.replace("unmarked", "marked")
    roundname = roundname.replace("mixed", "marked")

    hc_scheme = "AGB"

    # Get scores required on this round for each classification
    class_scores = [
        hc.score_for_round(
            group_data["class_HC"][i],
            ALL_FIELD_ROUNDS[roundname],
            hc_scheme,
            rounded_score=True,
        )
        for i in range(len(group_data["classes"]))
    ]

    # Reduce list based on other criteria besides handicap
    # What classes are eligible based on category and distance
    # Check round is long enough (24 targets)
    round_max_dist = ALL_FIELD_ROUNDS[roundname].max_distance().value
    for i, _ in enumerate(class_scores):
        if "12" in roundname:
            class_scores[i] = -9999
        if (
            round_max_dist < group_data["dists"][0]
            or round_max_dist > group_data["dists"][1]
        ):
            class_scores[i] = -9999

    # Make sure that hc.eq.score_for_round did not return array to satisfy mypy
    if any(isinstance(x, np.ndarray) for x in class_scores):
        msg = "score_for_round is attempting to return an array when float expected."
        raise TypeError(msg)
    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
