"""
Code for calculating Archery GB Field classifications.

Routine Listings
----------------
_make_agb_field_classification_dict
calculate_agb_field_classification
agb_field_classification_scores
"""

import itertools
from typing import TypedDict

import numpy as np
import numpy.typing as npt

import archeryutils.classifications.classification_utils as cls_funcs
import archeryutils.handicaps as hc
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

ALL_FIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ]
)

field_bowstyles = (
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

field_ages = (
    AGB_ages.P50
    | AGB_ages.ADULT
    | AGB_ages.U18
    | AGB_ages.U16
    | AGB_ages.U15
    | AGB_ages.U14
    | AGB_ages.U12
)


class GroupData(TypedDict):
    """Structure for AGB Field classification data."""

    classes: list[str]
    classes_long: list[str]
    class_HC: npt.NDArray[np.float64]
    max_distance: float
    min_dists: npt.NDArray[np.float64]


def _get_field_groupname(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Wrap function to generate string id for a particular category with field guards.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB field target rules
    gender : AGB_genders
        archer's gender under AGB field target rules
    age_group : AGB_ages
        archer's age group under AGB field target rules

    Returns
    -------
    groupname : str
        single str id for this category
    """
    if bowstyle not in AGB_bowstyles or bowstyle not in field_bowstyles:
        msg = (
            f"{bowstyle} is not a recognised bowstyle for field classifications. "
            f"Please select from {field_bowstyles}."
        )
        raise ValueError(msg)
    if gender not in AGB_genders:
        msg = (
            f"{gender} is not a recognised gender group for field classifications. "
            "Please select from `archeryutils.AGB_genders`."
        )
        raise ValueError(msg)
    if age_group not in AGB_ages or age_group not in field_ages:
        msg = (
            f"{age_group} is not a recognised age group for field classifications. "
            f"Please select from {field_ages}."
        )
        raise ValueError(msg)
    return cls_funcs.get_groupname(bowstyle, gender, age_group)


def _make_agb_field_classification_dict() -> dict[str, GroupData]:
    """
    Generate AGB field classification data.

    Generate a dictionary of dictionaries providing handicaps for each
    classification band and a list prestige rounds for each category from data files.
    Appropriate for 2025 ArcheryGB age groups and classifications.

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
    ArcheryGB 2025 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2025)
    """
    # Read in age group info as list of dicts
    agb_age_data = cls_funcs.read_ages_json()
    # Read in bowstyleclass info as list of dicts
    agb_bowstyle_data = cls_funcs.read_bowstyles_json()
    # Read in classification names as dict
    agb_classes_info_field = cls_funcs.read_classes_json("agb_field")
    agb_classes_field = agb_classes_info_field["classes"]
    agb_classes_field_long = agb_classes_info_field["classes_long"]

    # Generate dict of classifications
    # loop over all bowstyles, genders, ages
    classification_dict = {}
    for bowstyle, gender, age in itertools.product(
        field_bowstyles, AGB_genders, field_ages
    ):
        # Generate groupname
        # use assert checks to satisfy mypy that names are all valid
        if gender.name is None:
            errmsg = f"Gender {gender} does not have a name."
            raise ValueError(errmsg)
        if age.name is None:
            errmsg = f"Age {age} does not have a name."
            raise ValueError(errmsg)
        if bowstyle.name is None:
            errmsg = f"Bowstyle {bowstyle} does not have a name."
            raise ValueError(errmsg)
        groupname = _get_field_groupname(bowstyle, gender, age)

        # Get max dists for category from json file data
        # Use metres as corresponding yards >= metric
        min_dists, max_distance = _assign_dists(bowstyle, agb_age_data[age.name])

        # set step from datum based on age and gender steps required
        delta_hc_age_gender = cls_funcs.get_age_gender_step(
            gender.name,
            agb_age_data[age.name]["step"],
            agb_bowstyle_data[bowstyle.name]["ageStep_field"],
            agb_bowstyle_data[bowstyle.name]["genderStep_field"],
        )

        # set handicap threshold values for all classifications in the category
        class_hc = (
            agb_bowstyle_data[bowstyle.name]["datum_field"]
            + delta_hc_age_gender
            + (np.arange(len(agb_classes_field)) - 2)
            * agb_bowstyle_data[bowstyle.name]["classStep_field"]
        ).astype(np.float64)

        groupdata: GroupData = {
            "classes": agb_classes_field,
            "classes_long": agb_classes_field_long,
            "class_HC": class_hc,
            "max_distance": max_distance,
            "min_dists": min_dists,
        }

        classification_dict[groupname] = groupdata

    return classification_dict


def _assign_dists(
    bowstyle: AGB_bowstyles,
    age: cls_funcs.AGBAgeData,
) -> tuple[npt.NDArray[np.float64], float]:
    """
    Assign appropriate distance required for a category and classification.

    Appropriate for 2025 ArcheryGB field age groups and classifications.

    Parameters
    ----------
    bowstyle : str,
        string defining bowstyle
    age : dict[str, any],
        Typed dict containing age group data

    Returns
    -------
    tuple
        ndarray of minimum distances required for each classification for this bowstyle
        int of maximum distance that is shot by this bowstyle

    References
    ----------
    ArcheryGB 2024 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2024)
    World Archery Rulebook
    """
    # WA
    # Red - R/C/CL
    # Blue - Barebow, U18 R/C
    # Yellow - U18 BB
    #
    # AGB
    # U18 R/C/CL Red, Others Blue
    # U15 All Blue, R/C Red, Others White
    # U12 R/C/CL Red, All Blue, All White,
    if bowstyle in sighted_bowstyles:
        min_d, max_d = age["sighted"]
    else:
        min_d, max_d = age["unsighted"]

    n_classes: int = 9  # [EMB, GMB, MB, B1, B2, B3, A1, A2, A3]

    # EMB to bowman requires a minimum appropriate distance
    # Archer tiers can be shot at shorter pegs (min dist reduced by 10m for each tier)
    min_dists = np.zeros(n_classes, dtype=np.float64)
    min_dists[0:6] = min_d
    min_dists[6:9] = np.maximum(min_d - 10 * np.arange(1, 4), 30)

    return min_dists, max_d


agb_field_classifications = _make_agb_field_classification_dict()

del _make_agb_field_classification_dict


def calculate_agb_field_classification(
    score: float,
    roundname: str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Calculate AGB field classification from score.

    Calculate a classification from a score given suitable inputs.
    Appropriate for 2025 ArcheryGB age groups and classifications.

    Parameters
    ----------
    score : int
        numerical score on the round to calculate classification for
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB field rules
    gender : AGB_genders
        archer's gender under AGB field rules
    age_group : AGB_ages
        archer's age group under AGB field rules

    Returns
    -------
    classification_from_score : str
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB 2025 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2025)

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> class_func.calculate_agb_field_classification(
    ...     177,
    ...     "wa_field_24_blue_marked",
    ...     class_func.AGB_bowstyles.TRADITIONAL,
    ...     class_func.AGB_genders.MALE,
    ...     class_func.AGB_ages.U18,
    ... )
    'B1'

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

    groupname = _get_field_groupname(bowstyle, gender, age_group)
    group_data = agb_field_classifications[groupname]

    # Get scores required on this round for each classification
    all_class_scores = agb_field_classification_scores(
        roundname,
        bowstyle,
        gender,
        age_group,
    )

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
    roundname: str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> list[int]:
    """
    Calculate AGB field classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate for 2025 ArcheryGB age groups and classifications.

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
    ArcheryGB 2025 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2025)

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> class_func.agb_field_classification_scores(
    ...     "wa_field_24_red_marked",
    ...     class_func.AGB_bowstyles.COMPOUND,
    ...     class_func.AGB_genders.MALE,
    ...     class_func.AGB_ages.ADULT,
    ... )
    [408, 391, 369, 345, 318, 286, 248, 204, 157]

    If a classification cannot be achieved a fill value of `-9999` is returned:

    >>> class_func.agb_field_classification_scores(
    ...     "wa_field_12_red_unmarked",
    ...     class_func.AGB_bowstyles.COMPOUND,
    ...     class_func.AGB_genders.MALE,
    ...     class_func.AGB_ages.ADULT,
    ... )
    [-9999, -9999, -9999, 173, 159, 143, 124, 102, 79],

    """
    groupname = _get_field_groupname(bowstyle, gender, age_group)
    print(groupname)
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
    print(class_scores)

    # Reduce list based on other criteria besides handicap
    # What classes are eligible based on category and distance
    round_max_dist = ALL_FIELD_ROUNDS[roundname].max_distance().value
    for i in range(len(class_scores)):
        # What classes are eligible based on category and distance
        # Is round too short?
        if group_data["min_dists"][i] > round_max_dist:
            class_scores[i] = -9999
            print("short", group_data["min_dists"][i], round_max_dist)
        # Is peg too long (i.e. red peg for unsighted)?
        if group_data["max_distance"] < round_max_dist:
            class_scores[i] = -9999
            print("long", group_data["max_distance"], round_max_dist)
    # What classes are eligible based on round length (24 targets)
    if "12" in roundname:
        class_scores[0:3] = [-9999] * 3

    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
