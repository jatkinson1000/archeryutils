"""
Code for calculating Archery GB outdoor classifications.

Routine Listings
----------------
calculate_agb_outdoor_classification
agb_outdoor_classification_scores
"""

import itertools
import warnings
from typing import Any, Literal, TypedDict, cast

import numpy as np
import numpy.typing as npt

import archeryutils.classifications.classification_utils as cls_funcs
import archeryutils.handicaps as hc
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders
from archeryutils.rounds import Round

ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ],
)

outdoor_bowstyles = (
    AGB_bowstyles.COMPOUND
    | AGB_bowstyles.RECURVE
    | AGB_bowstyles.BAREBOW
    | AGB_bowstyles.LONGBOW
)


class GroupData(TypedDict):
    """Structure for AGB Outdoor classification data."""

    classes: list[str]
    max_distances: list[float]
    classes_long: list[str]
    class_HC: npt.NDArray[np.float64]
    min_dists: npt.NDArray[np.float64]
    prestige_rounds: list[str]


def _get_outdoor_groupname(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Wrap function to generate string id for a particular category with outdoor guards.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB outdoor target rules
    gender : AGB_genders
        archer's gender under AGB outdoor target rules
    age_group : AGB_ages
        archer's age group under AGB outdoor target rules

    Returns
    -------
    groupname : str
        single str id for this category
    """
    if bowstyle not in AGB_bowstyles or bowstyle not in outdoor_bowstyles:
        msg = (
            f"{bowstyle} is not a recognised bowstyle for outdoor classifications. "
            f"Please select from `{outdoor_bowstyles}`."
        )
        raise ValueError(msg)
    if gender not in AGB_genders:
        msg = (
            f"{gender} is not a recognised gender group for outdoor classifications. "
            "Please select from `archeryutils.AGB_genders`."
        )
        raise ValueError(msg)
    if age_group not in AGB_ages:
        msg = (
            f"{age_group} is not a recognised age group for outdoor classifications. "
            "Please select from `archeryutils.AGB_ages`."
        )
        raise ValueError(msg)
    return cls_funcs.get_groupname(bowstyle, gender, age_group)


def coax_outdoor_group(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> cls_funcs.AGBCategory:
    """
    Coax category not conforming to outdoor classification rules to one that does.

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
    dict[str, AGB_bowstyles | AGB_genders | AGB_ages]
        dict of archer's bowstyle, gender, and age_group under AGB coaxed to outdoor
        target rules
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


def _make_agb_outdoor_classification_dict() -> dict[str, GroupData]:
    """
    Generate AGB outdoor classification data.

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
    agb_age_data = cls_funcs.read_ages_json()
    # Read in bowstyleclass info as list of dicts
    agb_bowstyle_data = cls_funcs.read_bowstyles_json()
    # Read in classification names as dict
    agb_classes_info_out = cls_funcs.read_classes_json("agb_outdoor")
    agb_classes_out = agb_classes_info_out["classes"]
    agb_classes_out_long = agb_classes_info_out["classes_long"]

    # Generate dict of classifications
    # loop over all bowstyles, genders, ages
    classification_dict = {}
    for bowstyle, gender, age in itertools.product(
        outdoor_bowstyles, AGB_genders, AGB_ages
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
        groupname = _get_outdoor_groupname(bowstyle, gender, age)

        # Get max dists for category from json file data
        # Use metres as corresponding yards >= metric
        gender_key = cast(Literal["male", "female"], gender.name.lower())
        max_dists = agb_age_data[age.name][gender_key]

        # set step from datum based on age and gender steps required
        delta_hc_age_gender = cls_funcs.get_age_gender_step(
            gender,
            agb_age_data[age.name]["step"],
            agb_bowstyle_data[bowstyle.name]["ageStep_out"],
            agb_bowstyle_data[bowstyle.name]["genderStep_out"],
        )

        # set handicap threshold values for all classifications in the category
        class_hc = (
            agb_bowstyle_data[bowstyle.name]["datum_out"]
            + delta_hc_age_gender
            + (np.arange(len(agb_classes_out)) - 2)
            * agb_bowstyle_data[bowstyle.name]["classStep_out"]
        ).astype(np.float64)

        # get minimum distances to be shot for all classifications in the category
        min_dists = _assign_min_dist(
            gender=gender,
            age_group=age,
            max_dists=max_dists,
        )

        # Assign prestige rounds for the category
        prestige_rounds = _assign_outdoor_prestige(
            bowstyle=bowstyle,
            age=age,
            gender=gender,
            max_dists=max_dists,
        )

        groupdata: GroupData = {
            "classes": agb_classes_out,
            "max_distances": max_dists,
            "classes_long": agb_classes_out_long,
            "class_HC": class_hc,
            "min_dists": min_dists,
            "prestige_rounds": prestige_rounds,
        }

        classification_dict[groupname] = groupdata

    return classification_dict


def _assign_min_dist(
    gender: AGB_genders,
    age_group: AGB_ages,
    max_dists: list[float],
) -> npt.NDArray[np.float64]:
    """
    Assign appropriate minimum distance required for a category and classification.

    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    gender : str
        string defining gender
    age_group : str,
        string defining age group
    max_dists: List[float]
        list of integers defining the maximum distances for category

    Returns
    -------
    min_dists : array of int
        minimum distance [m] required by category for each classification (EMB -> A3)

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    """
    # List of maximum distances for use in assigning maximum distance [metres]
    # Use metres because corresponding yards distances are >= metric ones
    dists = [90, 70, 60, 50, 40, 30, 20, 15]

    max_dist_index = dists.index(np.min(max_dists))

    # Age group trickery:
    # U15 males and younger step down for B2 and below to align with female scores/hcs
    if (
        gender is AGB_genders.MALE
        and age_group
        not in AGB_ages.AGE_UNDER_15 | AGB_ages.AGE_UNDER_14 | AGB_ages.AGE_UNDER_12
    ):
        idxs = np.array([0, 0, 0, 0, 1, 2, 3, 4, 5])

    # All other categories require max dist for B1 and B2 then step down
    else:
        idxs = np.array([0, 0, 0, 0, 0, 1, 2, 3, 4])

    # Extract relevant distances for each classification from the dists array
    return np.take(dists, idxs + max_dist_index, mode="clip")


def _assign_outdoor_prestige(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age: AGB_ages,
    max_dists: list[float],
) -> list[str]:
    """
    Assign appropriate outdoor prestige rounds for a category.

    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        enum defining bowstyle
    gender : AGB_genders
        enum defining gender
    age : AGB_ages,
        enum defining age group
    max_dists: List[int]
        list of integers defining the maximum distances for category in [m] and [yds]

    Returns
    -------
    prestige_rounds : list of str
        list of perstige rounds for category defined by inputs

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # Lists of prestige rounds defined by 'codename' of 'Round' class
    # WARNING: do not change these without also addressing the prestige round code.
    prestige_imperial = [
        "york",
        "hereford",
        "bristol_i",
        "bristol_ii",
        "bristol_iii",
        "bristol_iv",
        "bristol_v",
    ]
    prestige_metric = [
        "wa1440_90",
        "wa1440_90_small",
        "wa1440_70",
        "wa1440_70_small",
        "wa1440_60",
        "wa1440_60_small",
        "metric_i",
        "metric_ii",
        "metric_iii",
        "metric_iv",
        "metric_v",
    ]
    prestige_720 = [
        "wa720_70",
        "wa720_60",
        "metric_122_50",
        "metric_122_40",
        "metric_122_30",
    ]
    prestige_720_compound = [
        "wa720_50_c",
        "metric_80_40",
        "metric_80_30",
    ]
    prestige_720_barebow = [
        "wa720_50_b",
        "metric_122_50",
        "metric_122_40",
        "metric_122_30",
    ]

    # Assign prestige rounds for the category
    #  - check bowstyle, distance, and age
    prestige_rounds = []
    distance_check: list[str] = []

    # 720 rounds - bowstyle dependent
    if bowstyle is AGB_bowstyles.COMPOUND:
        # Everyone gets the 'adult' 720
        prestige_rounds.append(prestige_720_compound[0])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720_compound[1:]

    elif bowstyle is AGB_bowstyles.BAREBOW:
        # Everyone gets the 'adult' 720
        prestige_rounds.append(prestige_720_barebow[0])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720_barebow[1:]

    else:
        # Everyone gets the 'adult' 720
        prestige_rounds.append(prestige_720[0])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720[1:]

        # Additional fix for Male 50+, U18, and U16 recurve/longbow
        if gender is AGB_genders.MALE:
            if age in AGB_ages.AGE_50_PLUS | AGB_ages.AGE_UNDER_18:
                prestige_rounds.append(prestige_720[1])  # 60m
            elif age is AGB_ages.AGE_UNDER_16:
                prestige_rounds.append(prestige_720[2])  # 50m

    # Imperial and 1440 rounds - Check based on distance
    distance_check = distance_check + prestige_imperial
    distance_check = distance_check + prestige_metric

    # Check all other rounds based on distance
    for roundname in distance_check:
        if ALL_OUTDOOR_ROUNDS[roundname].max_distance().value >= np.min(max_dists):
            prestige_rounds.append(roundname)

    return prestige_rounds


agb_outdoor_classifications = _make_agb_outdoor_classification_dict()

del _make_agb_outdoor_classification_dict


def calculate_agb_outdoor_classification(
    score: float,
    archery_round: Round | str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Calculate AGB outdoor classification from score.

    Calculate a classification from a score given suitable inputs.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    score : int
        numerical score on the round to calculate classification for
    archery_round : Round | str
        an archeryutils Round object as suitable for this scheme
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB outdoor target rules
    gender : AGB_genders
        archer's gender under AGB outdoor target rules
    age_group : AGB_ages
        archer's age group under AGB outdoor target rules

    Returns
    -------
    classification_from_score : str
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    Raises
    ------
    ValueError
        If an invalid score for the requested round is provided

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> from archeryutils import load_rounds
    >>> agb_outdoor = load_rounds.AGB_outdoor_imperial
    >>> class_func.calculate_agb_outdoor_classification(
    ...     858,
    ...     agb_outdoor.hereford,
    ...     class_func.AGB_bowstyles.RECURVE,
    ...     class_func.AGB_genders.FEMALE,
    ...     class_func.AGB_ages.AGE_UNDER_18,
    ... )
    'B1'

    """
    if isinstance(archery_round, str) and archery_round in ALL_OUTDOOR_ROUNDS:
        warnings.warn(
            "Passing a string as 'archery_round' is deprecated and will be removed "
            "in a future version.\n"
            "Please pass an archeryutils `Round` instead.",
            FutureWarning,
            stacklevel=2,
        )
        roundname = archery_round
        archery_round = ALL_OUTDOOR_ROUNDS[roundname]
    elif (
        isinstance(archery_round, Round)
        and archery_round in ALL_OUTDOOR_ROUNDS.values()
    ):
        # Get string key for this round:
        roundname = list(ALL_OUTDOOR_ROUNDS.keys())[
            list(ALL_OUTDOOR_ROUNDS.values()).index(archery_round)
        ]
    else:
        error = (
            "This round is not recognised for the purposes of outdoor classification.\n"
            "Please select an appropriate option using `archeryutils.load_rounds`."
        )
        raise ValueError(error)

    # Check score is valid
    if score < 0 or score > ALL_OUTDOOR_ROUNDS[roundname].max_score():
        msg = (
            f"Invalid score of {score} for a {ALL_OUTDOOR_ROUNDS[roundname].name}. "
            f"Should be in range 0-{ALL_OUTDOOR_ROUNDS[roundname].max_score()}."
        )
        raise ValueError(msg)

    # Get scores required on this round for each classification
    # Enforcing full size face and compound scoring (for compounds)
    all_class_scores = agb_outdoor_classification_scores(
        archery_round,
        bowstyle,
        gender,
        age_group,
    )

    groupname = _get_outdoor_groupname(bowstyle, gender, age_group)
    group_data = agb_outdoor_classifications[groupname]

    # dictionary ordering guaranteed in python 3.7+
    class_data = {}
    for i, class_i in enumerate(group_data["classes"]):
        class_data[class_i] = {
            "min_dist": group_data["min_dists"][i],
            "score": all_class_scores[i],
        }

    # Check if this is a prestige round and appropriate distances
    # remove ineligible classes from class_data
    class_data = _check_prestige_distance(roundname, groupname, class_data)

    # Of the classes remaining, what is the highest classification this score gets?
    # < 0 handles max scores, > score handles higher classifications
    for classname, classdata in class_data.items():
        if classdata["score"] > score:
            continue
        else:
            return classname
    return "UC"


def _check_prestige_distance(
    roundname: str,
    groupname: str,
    class_data: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Check available classifications for eligibility based on distance and prestige..

    Remove MB tier if not a prestige round.
    Remove any classifications where round is not far enough.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json
    groupname : str
        identifier for the category
    class_data : dict
        classification information for each category.

    Returns
    -------
    class_data : dict
        updated classification information for each category.

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # is it a prestige round? If not remove MB as an option
    if roundname not in agb_outdoor_classifications[groupname]["prestige_rounds"]:
        for mb_class in list(class_data.keys())[0:3]:
            del class_data[mb_class]

        # If not prestige, what classes are ineligible based on distance
        to_del: list[str] = []
        round_max_dist = ALL_OUTDOOR_ROUNDS[roundname].max_distance().value
        for class_i_name, class_i_data in class_data.items():
            if class_i_data["min_dist"] > round_max_dist:
                to_del.append(class_i_name)
        for class_i in to_del:
            del class_data[class_i]

    return class_data


def agb_outdoor_classification_scores(
    archery_round: Round | str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> list[int]:
    """
    Calculate AGB outdoor classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    archery_round : Round | str
        an archeryutils Round object as suitable for this scheme
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB outdoor target rules
    gender : AGB_genders
        archer's gender under AGB outdoor target rules
    age_group : AGB_ages
        archer's age group under AGB outdoor target rules

    Returns
    -------
    classification_scores : ndarray
        scores required for each classification in descending order

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> from archeryutils import load_rounds
    >>> agb_outdoor = load_rounds.AGB_outdoor_imperial
    >>> class_func.agb_outdoor_classification_scores(
    ...     agb_outdoor.hereford,
    ...     class_func.AGB_bowstyles.RECURVE,
    ...     class_func.AGB_genders.FEMALE,
    ...     class_func.AGB_ages.AGE_ADULT,
    ... )
    [1232, 1178, 1107, 1015, 900, 763, 614, 466, 336]

    If a classification cannot be achieved a fill value of `-9999` is returned:

    >>> class_func.agb_outdoor_classification_scores(
    ...     agb_outdoor.bristol_ii,
    ...     class_func.AGB_bowstyles.RECURVE,
    ...     class_func.AGB_genders.FEMALE,
    ...     class_func.AGB_ages.AGE_ADULT,
    ... )
    [-9999, -9999, -9999, -9999, -9999, 931, 797, 646, 493]

    """
    if isinstance(archery_round, str) and archery_round in ALL_OUTDOOR_ROUNDS:
        warnings.warn(
            "Passing a string as 'archery_round' is deprecated and will be removed "
            "in a future version.\n"
            "Please pass an archeryutils `Round` instead.",
            FutureWarning,
            stacklevel=2,
        )
        roundname = archery_round
    elif (
        isinstance(archery_round, Round)
        and archery_round in ALL_OUTDOOR_ROUNDS.values()
    ):
        # Get string key for this round:
        roundname = list(ALL_OUTDOOR_ROUNDS.keys())[
            list(ALL_OUTDOOR_ROUNDS.values()).index(archery_round)
        ]
    else:
        error = (
            "This round is not recognised for the purposes of outdoor classification.\n"
            "Please select an appropriate option using `archeryutils.load_rounds`."
        )
        raise ValueError(error)

    groupname = _get_outdoor_groupname(bowstyle, gender, age_group)
    group_data = agb_outdoor_classifications[groupname]

    # Get scores required on this round for each classification
    class_scores = [
        hc.score_for_round(
            group_data["class_HC"][i],
            ALL_OUTDOOR_ROUNDS[cls_funcs.strip_spots(roundname)],
            "AGB",
            rounded_score=True,
        )
        for i in range(len(group_data["classes"]))
    ]

    # Reduce list based on other criteria besides handicap
    # is it a prestige round? If not remove MB scores
    if roundname not in agb_outdoor_classifications[groupname]["prestige_rounds"]:
        class_scores[0:3] = [-9999] * 3

        # If not prestige, what classes are eligible based on category and distance
        round_max_dist = ALL_OUTDOOR_ROUNDS[roundname].max_distance().value
        for i in range(3, len(class_scores)):
            if group_data["min_dists"][i] > round_max_dist:
                class_scores[i] = -9999

    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
