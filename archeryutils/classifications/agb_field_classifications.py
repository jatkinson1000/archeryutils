"""
Code for calculating Archery GB Field classifications.

Routine Listings
----------------
_make_agb_field_classification_dict
calculate_agb_field_classification
agb_field_classification_scores
"""

from typing import List, Dict, Any
from collections import OrderedDict
import numpy as np

from archeryutils import load_rounds
import archeryutils.handicaps as hc
import archeryutils.classifications.classification_utils as cls_funcs


ALL_FIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ]
)


def _make_agb_field_classification_dict() -> Dict[str, Dict[str, Any]]:
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
    classification_dict : dict of str : dict of str: list, list, list
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
    agb_ages = cls_funcs.read_ages_json()
    # Restrict Age groups to those for field
    agb_ages = [
        item
        for item in agb_ages
        if item["age_group"].lower().replace(" ", "")
        in ["50+", "adult", "under21", "under18", "under15", "under12"]
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

                classification_dict[groupname] = {
                    "classes": agb_classes_field,
                    "classes_long": agb_classes_field_long,
                }

                # set step from datum based on age and gender steps required
                delta_hc_age_gender = cls_funcs.get_age_gender_step(
                    gender,
                    age["step"],
                    bowstyle["ageStep_field"],
                    bowstyle["genderStep_field"],
                )

                classification_dict[groupname]["class_HC"] = np.empty(
                    len(agb_classes_field)
                )
                classification_dict[groupname]["min_dists"] = np.empty(
                    len(agb_classes_field)
                )
                for i in range(len(agb_classes_field)):
                    # Assign handicap for this classification
                    classification_dict[groupname]["class_HC"][i] = (
                        bowstyle["datum_field"]
                        + delta_hc_age_gender
                        + (i - 2) * bowstyle["classStep_field"]
                    )

                # Get [min, max] dists for category from json file data
                classification_dict[groupname]["dists"] = assign_dists(
                    bowstyle["bowstyle"], age
                )

    return classification_dict


def assign_dists(
    bowstyle: str,
    age: Dict[str, Any],
) -> Any:
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
    if bowstyle.lower() in ("compound", "recurve", "compound limited"):
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
        raise ValueError(
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_FIELD_ROUNDS[roundname].max_score()}."
        )

    # Enforce unmarked/mixed being same score as marked
    roundname = roundname.replace("unmarked", "marked")
    roundname = roundname.replace("mixed", "marked")

    # Check round is long enough
    if "12" in roundname:
        return "UC"

    # Check if this round is an appropriate distance
    round_max_dist = ALL_FIELD_ROUNDS[roundname].max_distance()
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

    group_data = agb_field_classifications[
        cls_funcs.get_groupname(bowstyle, gender, age_group)
    ]

    # We iterate over class_data keys, so convert use OrderedDict
    class_data: OrderedDict[str, Dict[str, Any]] = OrderedDict([])
    for i, class_i in enumerate(group_data["classes"]):
        class_data[class_i] = {
            "score": all_class_scores[i],
        }

    # Of the classes remaining, what is the highest classification this score gets?
    to_del = []
    for classname, classdata in class_data.items():
        if classdata["score"] > score:
            to_del.append(classname)
    for item in to_del:
        del class_data[item]

    try:
        return list(class_data.keys())[0]
    except IndexError:
        return "UC"


def agb_field_classification_scores(
    roundname: str, bowstyle: str, gender: str, age_group: str
) -> List[int]:
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
    round_max_dist = ALL_FIELD_ROUNDS[roundname].max_distance()
    for i, _ in enumerate(class_scores):
        if "12" in roundname:
            class_scores[i] = -9999
        if round_max_dist < group_data["dists"][0]:
            class_scores[i] = -9999
        elif round_max_dist > group_data["dists"][1]:
            class_scores[i] = -9999

    # Make sure that hc.eq.score_for_round did not return array to satisfy mypy
    if any(isinstance(x, np.ndarray) for x in class_scores):
        raise TypeError(
            "score_for_round is attempting to return an array when float expected."
        )
    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
