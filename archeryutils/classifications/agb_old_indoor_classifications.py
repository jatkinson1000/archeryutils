"""
Code for calculating old Archery GB indoor classifications.

Routine Listings
----------------
_make_AGB_old_indoor_classification_dict
calculate_AGB_old_indoor_classification
AGB_old_indoor_classification_scores
"""
from typing import List, Dict, Any
import numpy as np

from archeryutils import load_rounds
from archeryutils.handicaps import handicap_equations as hc_eq
import archeryutils.classifications.classification_utils as cls_funcs


def _make_agb_old_indoor_classification_dict() -> Dict[str, Dict[str, Any]]:
    """
    Generate AGB outdoor classification data.

    Generate a dictionary of dictionaries providing handicaps for
    each classification band.

    Parameters
    ----------
    None

    Returns
    -------
    classification_dict : dict of str : dict of str: list
        dictionary indexed on group name (e.g 'adult_female_recurve')
        containing list of handicaps associated with each classification

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    agb_indoor_classes = ["A", "B", "C", "D", "E", "F", "G", "H"]

    # Generate dict of classifications
    # for both bowstyles, for both genders
    classification_dict = {}
    classification_dict[cls_funcs.get_groupname("Compound", "Male", "Adult")] = {
        "classes": agb_indoor_classes,
        "class_HC": [5, 12, 24, 37, 49, 62, 73, 79],
    }
    classification_dict[cls_funcs.get_groupname("Compound", "Female", "Adult")] = {
        "classes": agb_indoor_classes,
        "class_HC": [12, 18, 30, 43, 55, 67, 79, 83],
    }
    classification_dict[cls_funcs.get_groupname("Recurve", "Male", "Adult")] = {
        "classes": agb_indoor_classes,
        "class_HC": [14, 21, 33, 46, 58, 70, 80, 85],
    }
    classification_dict[cls_funcs.get_groupname("Recurve", "Female", "Adult")] = {
        "classes": agb_indoor_classes,
        "class_HC": [21, 27, 39, 51, 64, 75, 85, 90],
    }

    return classification_dict


agb_old_indoor_classifications = _make_agb_old_indoor_classification_dict()

del _make_agb_old_indoor_classification_dict


def calculate_agb_old_indoor_classification(
    roundname: str,
    score: float,
    bowstyle: str,
    gender: str,
    age_group: str,
    hc_scheme: str = "AGBold",
) -> str:
    """
    Calculate AGB indoor classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json
    score : int
        numerical score on the round to calculate classification for
    bowstyle : str
        archer's bowstyle under AGB outdoor target rules
    gender : str
        archer's gender under AGB outdoor target rules
    age_group : str
        archer's age group under AGB outdoor target rules
    hc_scheme : str
        handicap scheme to be used for legacy purposes. Default AGBold

    Returns
    -------
    classification_from_score : str
        the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # TODO: Need routines to sanitise/deal with variety of user inputs

    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_indoor_rounds = load_rounds.read_json_to_round_dict(
        [
            "AGB_indoor.json",
            "WA_indoor.json",
        ]
    )

    # deal with reduced categories:
    age_group = "Adult"
    if bowstyle.lower() not in ("compound"):
        bowstyle = "Recurve"

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_old_indoor_classifications[groupname]

    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    class_scores = [
        hc_eq.score_for_round(
            all_indoor_rounds[roundname],
            group_data["class_HC"][i],
            hc_scheme,
            hc_params,
            round_score_up=True,
        )[0]
        for i, class_i in enumerate(group_data["classes"])
    ]

    class_data: Dict[str, Any] = dict(zip(group_data["classes"], class_scores))

    # What is the highest classification this score gets?
    to_del = []
    for classname, classscore in class_data.items():
        if classscore > score:
            to_del.append(classname)
    for del_class in to_del:
        del class_data[del_class]

    # NB No fiddle for Worcester required with this logic...
    # Beware of this later on, however, if we wish to rectify the 'anomaly'

    try:
        classification_from_score = list(class_data.keys())[0]
        return classification_from_score
    except IndexError:
        # return "UC"
        return "unclassified"


def agb_old_indoor_classification_scores(
    roundname: str,
    bowstyle: str,
    gender: str,
    age_group: str,
    hc_scheme: str = "AGBold",
) -> List[int]:
    """
    Calculate AGB indoor classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate ArcheryGB age groups and classifications.

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
    hc_scheme : str
        handicap scheme to be used for legacy purposes. Default AGBold

    Returns
    -------
    classification_scores : ndarray
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7
    """
    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_indoor_rounds = load_rounds.read_json_to_round_dict(
        [
            "AGB_indoor.json",
            "WA_indoor.json",
        ]
    )

    # deal with reduced categories:
    age_group = "Adult"
    if bowstyle.lower() not in ("compound"):
        bowstyle = "Recurve"

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_old_indoor_classifications[groupname]

    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    class_scores = [
        hc_eq.score_for_round(
            all_indoor_rounds[roundname],
            group_data["class_HC"][i],
            hc_scheme,
            hc_params,
            round_score_up=True,
        )[0]
        for i, class_i in enumerate(group_data["classes"])
    ]

    # Make sure that hc.eq.score_for_round did not return array to satisfy mypy
    if any(isinstance(x, np.ndarray) for x in class_scores):
        raise TypeError(
            "score_for_round is attempting to return an array when float expected."
        )
    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
