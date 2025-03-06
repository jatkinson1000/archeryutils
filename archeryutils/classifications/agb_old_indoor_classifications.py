"""
Code for calculating old (pre-2023) Archery GB indoor classifications.

Routine Listings
----------------
calculate_AGB_old_indoor_classification
AGB_old_indoor_classification_scores
"""

from typing import TypedDict

import archeryutils.classifications.classification_utils as cls_funcs
import archeryutils.handicaps as hc
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

ALL_INDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_indoor.json",
        "WA_indoor.json",
    ],
)

old_indoor_bowstyles = AGB_bowstyles.COMPOUND | AGB_bowstyles.RECURVE
old_indoor_ages = AGB_ages.AGE_ADULT


class GroupData(TypedDict):
    """Structure for old AGB Indoor classification data."""

    classes: list[str]
    class_HC: list[int]


def _get_old_indoor_groupname(
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
    if bowstyle not in AGB_bowstyles or bowstyle not in old_indoor_bowstyles:
        msg = (
            f"{bowstyle} is not a recognised bowstyle for old indoor classifications. "
            f"Please select from `{old_indoor_bowstyles}`."
        )
        raise ValueError(msg)
    if gender not in AGB_genders:
        msg = (
            f"{gender} is not a recognised gender group for old indoor "
            "classifications. Please select from `archeryutils.AGB_genders`."
        )
        raise ValueError(msg)
    if age_group not in AGB_ages or age_group not in old_indoor_ages:
        msg = (
            f"{age_group} is not a recognised age group for old indoor "
            f"classifications. Please select from `{old_indoor_ages}`."
        )
        raise ValueError(msg)
    return cls_funcs.get_groupname(bowstyle, gender, age_group)


def coax_old_indoor_group(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,  # noqa: ARG001 - Unused argument for consistency with other classification schemes
) -> cls_funcs.AGBCategory:
    """
    Coax category not conforming to old indoor classification rules to one that does.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        archer's bowstyle
    gender : AGB_genders
        archer's gender under AGB
    age_group : AGB_ages
        archer's age group

    Returns
    -------
    TypedDict
        typed dict of archer's bowstyle, gender, and age_group under AGB coaxed to
        old indoor rules
    """
    if bowstyle in (
        AGB_bowstyles.COMPOUND
        | AGB_bowstyles.COMPOUNDLIMITED
        | AGB_bowstyles.COMPOUNDBAREBOW
    ):
        coax_bowstyle = AGB_bowstyles.COMPOUND
    else:
        coax_bowstyle = AGB_bowstyles.RECURVE

    coax_gender = gender

    coax_age_group = AGB_ages.AGE_ADULT

    return {
        "bowstyle": coax_bowstyle,
        "gender": coax_gender,
        "age_group": coax_age_group,
    }


def _make_agb_old_indoor_classification_dict() -> dict[str, GroupData]:
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
    compound_male_adult: GroupData = {
        "classes": agb_indoor_classes,
        "class_HC": [5, 12, 24, 37, 49, 62, 73, 79],
    }
    compound_female_adult: GroupData = {
        "classes": agb_indoor_classes,
        "class_HC": [12, 18, 30, 43, 55, 67, 79, 83],
    }
    recurve_male_adult: GroupData = {
        "classes": agb_indoor_classes,
        "class_HC": [14, 21, 33, 46, 58, 70, 80, 85],
    }
    recurve_female_adult: GroupData = {
        "classes": agb_indoor_classes,
        "class_HC": [21, 27, 39, 51, 64, 75, 85, 90],
    }

    classification_dict = {
        _get_old_indoor_groupname(
            AGB_bowstyles.COMPOUND, AGB_genders.MALE, AGB_ages.AGE_ADULT
        ): compound_male_adult,
        _get_old_indoor_groupname(
            AGB_bowstyles.COMPOUND, AGB_genders.FEMALE, AGB_ages.AGE_ADULT
        ): compound_female_adult,
        _get_old_indoor_groupname(
            AGB_bowstyles.RECURVE, AGB_genders.MALE, AGB_ages.AGE_ADULT
        ): recurve_male_adult,
        _get_old_indoor_groupname(
            AGB_bowstyles.RECURVE, AGB_genders.FEMALE, AGB_ages.AGE_ADULT
        ): recurve_female_adult,
    }

    return classification_dict


agb_old_indoor_classifications = _make_agb_old_indoor_classification_dict()

del _make_agb_old_indoor_classification_dict


def calculate_agb_old_indoor_classification(
    score: float,
    roundname: str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Calculate AGB indoor classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    score : int
        numerical score on the round to calculate classification for
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB indoor target rules
    gender : AGB_genders
        archer's gender under AGB indoor target rules
    age_group : AGB_ages
        archer's age group under AGB indoor target rules

    Returns
    -------
    classification_from_score : str
        the classification appropriate for this score

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (pre-2023)

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> class_func.calculate_agb_old_indoor_classification(
    ...     547,
    ...     "wa18",
    ...     AGB_bowstyles.COMPOUND,
    ...     AGB_genders.MALE,
    ...     AGB_ages.AGE_ADULT,
    ... )
    'C'

    """
    # Check score is valid
    if score < 0 or score > ALL_INDOOR_ROUNDS[roundname].max_score():
        msg = (
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_INDOOR_ROUNDS[roundname].max_score()}."
        )
        raise ValueError(msg)

    # Get scores required on this round for each classification
    class_scores = agb_old_indoor_classification_scores(
        roundname,
        bowstyle,
        gender,
        age_group,
    )

    groupname = _get_old_indoor_groupname(bowstyle, gender, age_group)
    group_data = agb_old_indoor_classifications[groupname]
    class_data = dict(zip(group_data["classes"], class_scores, strict=True))

    # What is the highest classification this score gets?
    # < 0 handles max scores, > score handles higher classifications
    # NB No fiddle for Worcester required with this logic...
    # Beware of this later on, however, if we wish to rectify the 'anomaly'
    for classname, classscore in class_data.items():
        if classscore > score:
            continue
        else:
            return classname
    return "UC"


def agb_old_indoor_classification_scores(
    roundname: str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> list[int]:
    """
    Calculate AGB indoor classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate ArcheryGB age groups and classifications.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB indoor target rules
    gender : AGB_genders
        archer's gender under AGB indoor target rules
    age_group : AGB_ages
        archer's age group under AGB indoor target rules

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
    >>> from archeryutils import classifications as class_func
    >>> class_func.agb_old_indoor_classification_scores(
    ...     "portsmouth",
    ...     AGB_bowstyles.BAREBOW,
    ...     AGB_genders.MALE,
    ...     AGB_ages.AGE_UNDER_12,
    ... )
    [592, 582, 554, 505, 432, 315, 195, 139]


    """
    # enforce compound scoring
    if bowstyle is AGB_bowstyles.COMPOUND:
        roundname = cls_funcs.get_compound_codename(roundname)

    groupname = _get_old_indoor_groupname(bowstyle, gender, age_group)
    group_data = agb_old_indoor_classifications[groupname]

    # Get scores required on this round for each classification
    class_scores = [
        hc.score_for_round(
            group_data["class_HC"][i],
            ALL_INDOOR_ROUNDS[roundname],
            "AGBold",
            rounded_score=True,
        )
        for i in range(len(group_data["classes"]))
    ]

    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
