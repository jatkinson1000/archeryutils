"""
Code for calculating old Archery GB classifications.

Extended Summary
----------------
Code to add functionality to the basic handicap equations code
in handicap_equations.py including inverse function and display.

Routine Listings
----------------
_make_old_agb_field_classification_dict
calculate_old_agb_field_classification
old_agb_field_classification_scores

"""

import re
from typing import TypedDict

import archeryutils.classifications.classification_utils as cls_funcs
from archeryutils import load_rounds

ALL_AGBFIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ],
)


class GroupData(TypedDict):
    """Structure for AGB Field classification data."""

    classes: list[str]
    class_scores: list[int]


def _make_old_agb_field_classification_dict() -> dict[str, GroupData]:
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
        containing list of scores associated with each classification

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    """
    agb_field_classes = [
        "Grand Master Bowman",
        "Master Bowman",
        "Bowman",
        "1st Class",
        "2nd Class",
        "3rd Class",
    ]

    agb_field_scores = {
        ("Compound", "Male", "Adult"): [393, 377, 344, 312, 279, 247],
        ("Compound", "Female", "Adult"): [376, 361, 330, 299, 268, 237],
        ("Recurve", "Male", "Adult"): [338, 317, 288, 260, 231, 203],
        ("Recurve", "Female", "Adult"): [322, 302, 275, 247, 220, 193],
        ("Barebow", "Male", "Adult"): [328, 307, 279, 252, 224, 197],
        ("Barebow", "Female", "Adult"): [303, 284, 258, 233, 207, 182],
        ("Longbow", "Male", "Adult"): [201, 188, 171, 155, 137, 121],
        ("Longbow", "Female", "Adult"): [152, 142, 129, 117, 103, 91],
        ("Traditional", "Male", "Adult"): [262, 245, 223, 202, 178, 157],
        ("Traditional", "Female", "Adult"): [197, 184, 167, 152, 134, 118],
        ("Flatbow", "Male", "Adult"): [262, 245, 223, 202, 178, 157],
        ("Flatbow", "Female", "Adult"): [197, 184, 167, 152, 134, 118],
        ("Compound Limited", "Male", "Adult"): [338, 317, 288, 260, 231, 203],
        ("Compound Limited", "Female", "Adult"): [322, 302, 275, 247, 220, 193],
        ("Compound Barebow", "Male", "Adult"): [328, 307, 279, 252, 224, 197],
        ("Compound Barebow", "Female", "Adult"): [303, 284, 258, 233, 207, 182],
        ("Compound", "Male", "Under 18"): [385, 369, 337, 306, 273, 242],
        ("Compound", "Female", "Under 18"): [357, 343, 314, 284, 255, 225],
        ("Recurve", "Male", "Under 18"): [311, 292, 265, 239, 213, 187],
        ("Recurve", "Female", "Under 18"): [280, 263, 239, 215, 191, 168],
        ("Barebow", "Male", "Under 18"): [298, 279, 254, 229, 204, 179],
        ("Barebow", "Female", "Under 18"): [251, 236, 214, 193, 172, 151],
        ("Longbow", "Male", "Under 18"): [161, 150, 137, 124, 109, 96],
        ("Longbow", "Female", "Under 18"): [122, 114, 103, 94, 83, 73],
        ("Traditional", "Male", "Under 18"): [210, 196, 178, 161, 143, 126],
        ("Traditional", "Female", "Under 18"): [158, 147, 134, 121, 107, 95],
        ("Flatbow", "Male", "Under 18"): [210, 196, 178, 161, 143, 126],
        ("Flatbow", "Female", "Under 18"): [158, 147, 134, 121, 107, 95],
        ("Compound Limited", "Male", "Under 18"): [311, 292, 265, 239, 213, 187],
        ("Compound Limited", "Female", "Under 18"): [280, 263, 239, 215, 191, 168],
        ("Compound Barebow", "Male", "Under 18"): [298, 279, 254, 229, 204, 179],
        ("Compound Barebow", "Female", "Under 18"): [251, 236, 214, 193, 172, 151],
    }

    # Generate dict of classifications
    classification_dict = {}

    for group, scores in agb_field_scores.items():
        groupdata: GroupData = {"classes": agb_field_classes, "class_scores": scores}
        groupname = cls_funcs.get_groupname(*group)
        classification_dict[groupname] = groupdata

    return classification_dict


old_agb_field_classifications = _make_old_agb_field_classification_dict()

del _make_old_agb_field_classification_dict


def calculate_old_agb_field_classification(
    roundname: str, score: float, bowstyle: str, gender: str, age_group: str
) -> str:
    """
    Calculate AGB field classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.

    Parameters
    ----------
    score : float
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
    classification_from_score : str
        the classification appropriate for this score

    Raises
    ------
    ValueError
        If an invalid score for the requested round is provided

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> class_func.calculate_agb_field_classification(
    ...     247,
    ...     "wa_field_24_red_marked",
    ...     "recurve",
    ...     "male",
    ...     "adult",
    ... )
    '2nd Class'

    """
    # Check score is valid
    if score < 0 or score > ALL_AGBFIELD_ROUNDS[roundname].max_score():
        msg = (
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_AGBFIELD_ROUNDS[roundname].max_score()}."
        )
        raise ValueError(msg)

    # deal with reduced categories:
    if age_group.lower().replace(" ", "") in ("adult", "50+", "under21"):
        age_group = "Adult"
    elif re.compile("under(18|16|15|14|12)").match(age_group.lower().replace(" ", "")):
        age_group = "Under 18"

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)

    # Get scores required on this round for each classification
    group_data = old_agb_field_classifications[groupname]

    # Check Round is appropriate:
    # Sighted can have any Red 24, unsighted can have any blue 24
    if (
        bowstyle.lower().replace(" ", "") in ("compound", "recurve")
        and "wa_field_24_red_" not in roundname
    ):
        return "unclassified"
    if (
        bowstyle.lower().replace(" ", "")
        in (
            "barebow",
            "longbow",
            "traditional",
            "flatbow",
            "compoundlimited",
            "compoundbarebow",
        )
        and "wa_field_24_blue_" not in roundname
    ):
        return "unclassified"

    # What is the highest classification this score gets?
    class_scores = dict(
        zip(group_data["classes"], group_data["class_scores"], strict=True)
    )
    for classification, classification_score in class_scores.items():
        if classification_score > score:
            continue
        else:
            return classification

    # if lower than 3rd class score return "UC"
    return "unclassified"


def old_agb_field_classification_scores(
    roundname: str,  # noqa: ARG001 - Unused argument for consistency with other classification schemes
    bowstyle: str,
    gender: str,
    age_group: str,
) -> list[int]:
    """
    Calculate AGB field classification scores for category.

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

    Returns
    -------
    classification_scores : list of int
        scores required for each classification in descending order

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> class_func.agb_field_classification_scores(
    ...     "wa_field_24_red_marked",
    ...     "recurve",
    ...     "male",
    ...     "adult",
    ... )
    [338, 317, 288, 260, 231, 203]

    """
    # deal with reduced categories:
    if age_group.lower().replace(" ", "") in ("adult", "50+", "under21"):
        age_group = "Adult"
    elif re.compile("under(18|16|15|14|12)").match(age_group.lower().replace(" ", "")):
        age_group = "Under 18"

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = old_agb_field_classifications[groupname]

    # Get scores required on this round for each classification
    return group_data["class_scores"]
