"""
Code for calculating Archery GB indoor classifications.

Routine Listings
----------------
calculate_agb_indoor_classification
agb_indoor_classification_scores
"""

import itertools
import warnings
from typing import TypedDict

import numpy as np
import numpy.typing as npt

import archeryutils.classifications.classification_utils as cls_funcs
import archeryutils.handicaps as hc
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders
from archeryutils.rounds import Round

ALL_INDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_indoor.json",
        "WA_indoor.json",
    ],
)

indoor_bowstyles = (
    AGB_bowstyles.COMPOUND
    | AGB_bowstyles.RECURVE
    | AGB_bowstyles.BAREBOW
    | AGB_bowstyles.LONGBOW
)


class GroupData(TypedDict):
    """Structure for AGB Indoor classification data."""

    classes: list[str]
    classes_long: list[str]
    class_HC: npt.NDArray[np.float64]


def _get_indoor_groupname(
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
    if bowstyle not in AGB_bowstyles or bowstyle not in indoor_bowstyles:
        msg = (
            f"{bowstyle} is not a recognised bowstyle for indoor classifications. "
            f"Please select from `{indoor_bowstyles}`."
        )
        raise ValueError(msg)
    if gender not in AGB_genders:
        msg = (
            f"{gender} is not a recognised gender group for indoor classifications. "
            "Please select from `archeryutils.AGB_genders`."
        )
        raise ValueError(msg)
    if age_group not in AGB_ages:
        msg = (
            f"{age_group} is not a recognised age group for indoor classifications. "
            "Please select from `archeryutils.AGB_ages`."
        )
        raise ValueError(msg)
    return cls_funcs.get_groupname(bowstyle, gender, age_group)


def coax_indoor_group(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> cls_funcs.AGBCategory:
    """
    Coax category not conforming to indoor classification rules to one that does.

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
        indoor target rules
    """
    if bowstyle in (AGB_bowstyles.FLATBOW | AGB_bowstyles.TRADITIONAL):
        coax_bowstyle = AGB_bowstyles.BAREBOW
    elif bowstyle in (AGB_bowstyles.COMPOUNDLIMITED | AGB_bowstyles.COMPOUNDBAREBOW):
        coax_bowstyle = AGB_bowstyles.COMPOUND
    else:
        coax_bowstyle = bowstyle

    coax_gender = gender

    coax_age_group = age_group

    return {
        "bowstyle": coax_bowstyle,
        "gender": coax_gender,
        "age_group": coax_age_group,
    }


def _make_agb_indoor_classification_dict() -> dict[str, GroupData]:
    """
    Generate new (2023) AGB indoor classification data.

    Generate a dictionary of dictionaries providing handicaps for each
    classification band and a list of prestige rounds for each category from data files.
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
    # For score purposes in classifications we use the full face, not the triple.
    # Option of having triple is handled in get classification function
    # Compound version of rounds is handled below.

    # Read in age group info as list of dicts
    agb_age_data = cls_funcs.read_ages_json()
    # Read in bowstyleclass info as list of dicts
    agb_bowstyle_data = cls_funcs.read_bowstyles_json()
    # Read in classification names as dict
    agb_classes_info_in = cls_funcs.read_classes_json("agb_indoor")
    agb_classes_in = agb_classes_info_in["classes"]
    agb_classes_in_long = agb_classes_info_in["classes_long"]

    # Generate dict of classifications
    # loop over all bowstyles, genders, ages
    classification_dict = {}
    for bowstyle, gender, age in itertools.product(
        indoor_bowstyles, AGB_genders, AGB_ages
    ):
        # Generate groupname
        # The following satisfies mypy that names are all valid strings
        # Cannot currently be reached, so ignore for coverage
        if gender.name is None:  # pragma: no cover
            errmsg = f"Gender {gender} does not have a name."
            raise ValueError(errmsg)
        if age.name is None:  # pragma: no cover
            errmsg = f"Age {age} does not have a name."
            raise ValueError(errmsg)
        if bowstyle.name is None:  # pragma: no cover
            errmsg = f"Bowstyle {bowstyle} does not have a name."
            raise ValueError(errmsg)
        groupname = _get_indoor_groupname(bowstyle, gender, age)

        # set step from datum based on age and gender steps required
        delta_hc_age_gender = cls_funcs.get_age_gender_step(
            gender,
            agb_age_data[age.name]["step"],
            agb_bowstyle_data[bowstyle.name]["ageStep_in"],
            agb_bowstyle_data[bowstyle.name]["genderStep_in"],
        )

        # set handicap threshold values for all classifications in the category
        class_hc = (
            agb_bowstyle_data[bowstyle.name]["datum_in"]
            + delta_hc_age_gender
            + (np.arange(len(agb_classes_in)) - 1)
            * agb_bowstyle_data[bowstyle.name]["classStep_in"]
        ).astype(np.float64)

        groupdata: GroupData = {
            "classes": agb_classes_in,
            "classes_long": agb_classes_in_long,
            "class_HC": class_hc,
        }
        classification_dict[groupname] = groupdata

    return classification_dict


agb_indoor_classifications = _make_agb_indoor_classification_dict()

del _make_agb_indoor_classification_dict


def calculate_agb_indoor_classification(
    score: float,
    archery_round: Round | str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Calculate new (2023) AGB indoor classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    score : int
        numerical score on the round to calculate classification for
    archery_round : Round | str
        an archeryutils Round object as suitable for this scheme
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
    >>> from archeryutils import load_rounds
    >>> agb_indoor = load_rounds.AGB_indoor
    >>> class_func.calculate_agb_indoor_classification(
    ...     547,
    ...     agb_indoor.wa18,
    ...     class_func.AGB_bowstyles.COMPOUND,
    ...     class_func.AGB_genders.MALE,
    ...     class_func.AGB_ages.AGE_50_PLUS,
    ... )
    'I-B2'

    """
    if isinstance(archery_round, str) and archery_round in ALL_INDOOR_ROUNDS:
        warnings.warn(
            "Passing a string as 'archery_round' is deprecated and will be removed "
            "in a future version.\n"
            "Please pass an archeryutils `Round` instead.",
            FutureWarning,
            stacklevel=2,
        )
        roundname = archery_round
    elif (
        isinstance(archery_round, Round) and archery_round in ALL_INDOOR_ROUNDS.values()
    ):
        # Get string key for this round:
        roundname = list(ALL_INDOOR_ROUNDS.keys())[
            list(ALL_INDOOR_ROUNDS.values()).index(archery_round)
        ]
    else:
        error = (
            "This round is not recognised for the purposes of indoor classification.\n"
            "Please select an appropriate option using `archeryutils.load_rounds`."
        )
        raise ValueError(error)

    # Check score is valid
    if score < 0 or score > ALL_INDOOR_ROUNDS[roundname].max_score():
        msg = (
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_INDOOR_ROUNDS[roundname].max_score()}."
        )
        raise ValueError(msg)

    # Get scores required on this round for each classification
    # Enforcing full size face and compound scoring (for compounds)
    all_class_scores = agb_indoor_classification_scores(
        roundname,
        bowstyle,
        gender,
        age_group,
    )

    groupname = _get_indoor_groupname(bowstyle, gender, age_group)
    group_data = agb_indoor_classifications[groupname]
    class_data = dict(zip(group_data["classes"], all_class_scores, strict=True))

    # What is the highest classification this score gets?
    # < 0 handles max scores, > score handles higher classifications
    for classname, classscore in class_data.items():
        if classscore < 0 or classscore > score:
            continue
        else:
            return classname
    return "UC"


def agb_indoor_classification_scores(
    archery_round: Round | str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> list[int]:
    """
    Calculate 2023 AGB indoor classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate ArcheryGB age groups and classifications.

    Parameters
    ----------
    archery_round : Round | str
        an archeryutils Round object as suitable for this scheme
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
    >>> from archeryutils import load_rounds
    >>> agb_outdoor = load_rounds.AGB_indoor
    >>> class_func.agb_indoor_classification_scores(
    ...     agb_indoor.portsmouth,
    ...     class_func.AGB_bowstyles.BAREBOW,
    ...     class_func.AGB_genders.MALE,
    ...     class_func.AGB_ages.AGE_UNDER_12,
    ... )
    [411, 360, 301, 240, 183, 134, 95, 66]

    If a classification cannot be achieved a fill value of `-9999` is returned:

    >>> class_func.agb_indoor_classification_scores(
    ...     agb_indoor.worcester,
    ...     class_func.AGB_bowstyles.COMPOUND,
    ...     class_func.AGB_genders.FEMALE,
    ...     class_func.AGB_ages.AGE_ADULT,
    ... )
    [-9999, -9999, 298, 289, 276, 257, 233, 200]

    """
    if isinstance(archery_round, str) and archery_round in ALL_INDOOR_ROUNDS:
        warnings.warn(
            "Passing a string as 'archery_round' is deprecated and will be removed "
            "in a future version.\n"
            "Please pass an archeryutils `Round` instead.",
            FutureWarning,
            stacklevel=2,
        )
        roundname = archery_round
    elif (
        isinstance(archery_round, Round) and archery_round in ALL_INDOOR_ROUNDS.values()
    ):
        # Get string key for this round:
        roundname = list(ALL_INDOOR_ROUNDS.keys())[
            list(ALL_INDOOR_ROUNDS.values()).index(archery_round)
        ]
    else:
        error = (
            "This round is not recognised for the purposes of indoor classification.\n"
            "Please select an appropriate option using `archeryutils.load_rounds`."
        )
        raise ValueError(error)

    groupname = _get_indoor_groupname(bowstyle, gender, age_group)
    group_data = agb_indoor_classifications[groupname]

    hc_scheme = "AGB"

    # enforce compound scoring
    if bowstyle is AGB_bowstyles.COMPOUND:
        roundname = cls_funcs.get_compound_codename(roundname)

    # Get scores required on this round for each classification
    # Enforce full size face
    class_scores = [
        hc.score_for_round(
            group_data["class_HC"][i],
            ALL_INDOOR_ROUNDS[cls_funcs.strip_spots(roundname)],
            hc_scheme,
            rounded_score=True,
        )
        for i in range(len(group_data["classes"]))
    ]

    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    # Handle possibility of gaps in the tables or max scores by checking 1 HC point
    # above current (floored to handle 0.5) and amending accordingly
    for i, (score, handicap) in enumerate(
        zip(int_class_scores, group_data["class_HC"], strict=True),
    ):
        next_score = hc.score_for_round(
            np.floor(handicap) + 1,
            ALL_INDOOR_ROUNDS[cls_funcs.strip_spots(roundname)],
            hc_scheme,
            rounded_score=True,
        )
        if next_score == score:
            # If already at max score this classification is impossible
            if score == ALL_INDOOR_ROUNDS[roundname].max_score():
                int_class_scores[i] = -9999
            # If gap in table increase to next score
            # (we assume here that no two classifications are only 1 point apart...)
            else:
                int_class_scores[i] += 1

    return int_class_scores
