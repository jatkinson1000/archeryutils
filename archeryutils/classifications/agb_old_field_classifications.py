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

from typing import TypedDict

import archeryutils.classifications.classification_utils as cls_funcs
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

ALL_AGBFIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ],
)

AGB_FIELD_CLASSES = [
    "GMB",
    "MB",
    "B",
    "1C",
    "2C",
    "3C",
]
UNCLASSIFIED = "UC"

old_field_bowstyles = (
    AGB_bowstyles.COMPOUND
    | AGB_bowstyles.RECURVE
    | AGB_bowstyles.BAREBOW
    | AGB_bowstyles.ENGLISHLONGBOW
    | AGB_bowstyles.TRADITIONAL
    | AGB_bowstyles.FLATBOW
    | AGB_bowstyles.COMPOUNDLIMITED
    | AGB_bowstyles.COMPOUNDBAREBOW
)

sighted_bowstyles = (
    AGB_bowstyles.COMPOUND | AGB_bowstyles.RECURVE | AGB_bowstyles.COMPOUNDLIMITED
)

old_field_ages = AGB_ages.ADULT | AGB_ages.U18


class GroupData(TypedDict):
    """Structure for AGB Field classification data."""

    classes: list[str]
    class_scores: list[int]


def _get_old_field_groupname(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Wrap function to generate string id for a particular category with old field guards.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        archer's bowstyle under old AGB field rules
    gender : AGB_genders
        archer's gender under old AGB field rules
    age_group : AGB_ages
        archer's age group under old AGB field rules

    Returns
    -------
    groupname : str
        single str id for this category
    """
    if bowstyle not in AGB_bowstyles or bowstyle not in old_field_bowstyles:
        msg = (
            f"{bowstyle} is not a recognised bowstyle for old field classifications. "
            f"Please select from {old_field_bowstyles}."
        )
        raise ValueError(msg)
    if gender not in AGB_genders:
        msg = (
            f"{gender} is not a recognised gender group for old field "
            "classifications. Please select from `archeryutils.AGB_genders`."
        )
        raise ValueError(msg)
    if age_group not in AGB_ages or age_group not in old_field_ages:
        msg = (
            f"{age_group} is not a recognised age group for old field "
            f"classifications. Please select from {old_field_ages}."
        )
        raise ValueError(msg)
    return cls_funcs.get_groupname(bowstyle, gender, age_group)


def _make_agb_old_field_classification_dict() -> dict[str, GroupData]:
    """
    Generate old (pre-2025) AGB field classification data.

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
    agb_field_scores = {
        (AGB_bowstyles.COMPOUND, AGB_genders.MALE, AGB_ages.ADULT): [
            393,
            377,
            344,
            312,
            279,
            247,
        ],
        (AGB_bowstyles.COMPOUND, AGB_genders.FEMALE, AGB_ages.ADULT): [
            376,
            361,
            330,
            299,
            268,
            237,
        ],
        (AGB_bowstyles.RECURVE, AGB_genders.MALE, AGB_ages.ADULT): [
            338,
            317,
            288,
            260,
            231,
            203,
        ],
        (AGB_bowstyles.RECURVE, AGB_genders.FEMALE, AGB_ages.ADULT): [
            322,
            302,
            275,
            247,
            220,
            193,
        ],
        (AGB_bowstyles.BAREBOW, AGB_genders.MALE, AGB_ages.ADULT): [
            328,
            307,
            279,
            252,
            224,
            197,
        ],
        (AGB_bowstyles.BAREBOW, AGB_genders.FEMALE, AGB_ages.ADULT): [
            303,
            284,
            258,
            233,
            207,
            182,
        ],
        (AGB_bowstyles.LONGBOW, AGB_genders.MALE, AGB_ages.ADULT): [
            201,
            188,
            171,
            155,
            137,
            121,
        ],
        (AGB_bowstyles.LONGBOW, AGB_genders.FEMALE, AGB_ages.ADULT): [
            152,
            142,
            129,
            117,
            103,
            91,
        ],
        (AGB_bowstyles.TRADITIONAL, AGB_genders.MALE, AGB_ages.ADULT): [
            262,
            245,
            223,
            202,
            178,
            157,
        ],
        (AGB_bowstyles.TRADITIONAL, AGB_genders.FEMALE, AGB_ages.ADULT): [
            197,
            184,
            167,
            152,
            134,
            118,
        ],
        (AGB_bowstyles.FLATBOW, AGB_genders.MALE, AGB_ages.ADULT): [
            262,
            245,
            223,
            202,
            178,
            157,
        ],
        (AGB_bowstyles.FLATBOW, AGB_genders.FEMALE, AGB_ages.ADULT): [
            197,
            184,
            167,
            152,
            134,
            118,
        ],
        (AGB_bowstyles.COMPOUNDLIMITED, AGB_genders.MALE, AGB_ages.ADULT): [
            338,
            317,
            288,
            260,
            231,
            203,
        ],
        (AGB_bowstyles.COMPOUNDLIMITED, AGB_genders.FEMALE, AGB_ages.ADULT): [
            322,
            302,
            275,
            247,
            220,
            193,
        ],
        (AGB_bowstyles.COMPOUNDBAREBOW, AGB_genders.MALE, AGB_ages.ADULT): [
            328,
            307,
            279,
            252,
            224,
            197,
        ],
        (AGB_bowstyles.COMPOUNDBAREBOW, AGB_genders.FEMALE, AGB_ages.ADULT): [
            303,
            284,
            258,
            233,
            207,
            182,
        ],
        (AGB_bowstyles.COMPOUND, AGB_genders.MALE, AGB_ages.U18): [
            385,
            369,
            337,
            306,
            273,
            242,
        ],
        (AGB_bowstyles.COMPOUND, AGB_genders.FEMALE, AGB_ages.U18): [
            357,
            343,
            314,
            284,
            255,
            225,
        ],
        (AGB_bowstyles.RECURVE, AGB_genders.MALE, AGB_ages.U18): [
            311,
            292,
            265,
            239,
            213,
            187,
        ],
        (AGB_bowstyles.RECURVE, AGB_genders.FEMALE, AGB_ages.U18): [
            280,
            263,
            239,
            215,
            191,
            168,
        ],
        (AGB_bowstyles.BAREBOW, AGB_genders.MALE, AGB_ages.U18): [
            298,
            279,
            254,
            229,
            204,
            179,
        ],
        (AGB_bowstyles.BAREBOW, AGB_genders.FEMALE, AGB_ages.U18): [
            251,
            236,
            214,
            193,
            172,
            151,
        ],
        (AGB_bowstyles.LONGBOW, AGB_genders.MALE, AGB_ages.U18): [
            161,
            150,
            137,
            124,
            109,
            96,
        ],
        (AGB_bowstyles.LONGBOW, AGB_genders.FEMALE, AGB_ages.U18): [
            122,
            114,
            103,
            94,
            83,
            73,
        ],
        (AGB_bowstyles.TRADITIONAL, AGB_genders.MALE, AGB_ages.U18): [
            210,
            196,
            178,
            161,
            143,
            126,
        ],
        (AGB_bowstyles.TRADITIONAL, AGB_genders.FEMALE, AGB_ages.U18): [
            158,
            147,
            134,
            121,
            107,
            95,
        ],
        (AGB_bowstyles.FLATBOW, AGB_genders.MALE, AGB_ages.U18): [
            210,
            196,
            178,
            161,
            143,
            126,
        ],
        (AGB_bowstyles.FLATBOW, AGB_genders.FEMALE, AGB_ages.U18): [
            158,
            147,
            134,
            121,
            107,
            95,
        ],
        (AGB_bowstyles.COMPOUNDLIMITED, AGB_genders.MALE, AGB_ages.U18): [
            311,
            292,
            265,
            239,
            213,
            187,
        ],
        (AGB_bowstyles.COMPOUNDLIMITED, AGB_genders.FEMALE, AGB_ages.U18): [
            280,
            263,
            239,
            215,
            191,
            168,
        ],
        (AGB_bowstyles.COMPOUNDBAREBOW, AGB_genders.MALE, AGB_ages.U18): [
            298,
            279,
            254,
            229,
            204,
            179,
        ],
        (AGB_bowstyles.COMPOUNDBAREBOW, AGB_genders.FEMALE, AGB_ages.U18): [
            251,
            236,
            214,
            193,
            172,
            151,
        ],
    }

    # Generate dict of classifications
    classification_dict = {}

    for group, scores in agb_field_scores.items():
        groupdata: GroupData = {"classes": AGB_FIELD_CLASSES, "class_scores": scores}
        groupname = _get_old_field_groupname(*group)
        classification_dict[groupname] = groupdata

    return classification_dict


old_agb_field_classifications = _make_agb_old_field_classification_dict()

del _make_agb_old_field_classification_dict


def calculate_agb_old_field_classification(
    roundname: str,
    score: float,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Calculate old (pre-2025) AGB field classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.

    Parameters
    ----------
    score : float
        numerical score on the round to calculate classification for
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : AGB_bowstyles
        archer's bowstyle under old AGB field rules
    gender : AGB_genders
        archer's gender under old AGB field rules
    age_group : AGB_ages
        archer's age group under old AGB field rules

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
    >>> class_func.calculate_agb_old_field_classification(
    ...     247,
    ...     "wa_field_24_red_marked",
    ...     class_func.AGB_bowstyles.RECURVE,
    ...     class_func.AGB_genders.MALE,
    ...     class_func.AGB_ages.ADULT,
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

    groupname = _get_old_field_groupname(bowstyle, gender, age_group)

    # Get scores required on this round for each classification
    group_data = old_agb_field_classifications[groupname]

    # Check Round is appropriate:
    # Sighted can have any Red 24, unsighted can have any blue 24
    if bowstyle in sighted_bowstyles and "wa_field_24_red_" not in roundname:
        return UNCLASSIFIED
    if bowstyle not in sighted_bowstyles and "wa_field_24_blue_" not in roundname:
        return UNCLASSIFIED

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
    return UNCLASSIFIED


def agb_old_field_classification_scores(
    roundname: str,  # noqa: ARG001 - Unused argument for consistency with other classification schemes
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> list[int]:
    """
    Calculate old (pre-2025) AGB field classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate ArcheryGB age groups and classifications.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : AGB_bowstyles
        archer's bowstyle under old AGB field rules
    gender : AGB_genders
        archer's gender under old AGB field rules
    age_group : AGB_ages
        archer's age group under old AGB field rules

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
    >>> class_func.agb_old_field_classification_scores(
    ...     "wa_field_24_red_marked",
    ...     class_func.AGB_bowstyles.RECURVE,
    ...     class_func.AGB_genders.MALE,
    ...     class_func.AGB_ages.ADULT,
    ... )
    [338, 317, 288, 260, 231, 203]

    """
    groupname = _get_old_field_groupname(bowstyle, gender, age_group)
    group_data = old_agb_field_classifications[groupname]

    # Get scores required on this round for each classification
    return group_data["class_scores"]
