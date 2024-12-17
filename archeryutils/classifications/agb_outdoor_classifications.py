"""
Code for calculating Archery GB outdoor classifications.

Routine Listings
----------------
calculate_agb_outdoor_classification
agb_outdoor_classification_scores
"""

import itertools
from typing import Any, Literal, TypedDict, cast

import numpy as np
import numpy.typing as npt

import archeryutils.classifications.classification_utils as cls_funcs
import archeryutils.handicaps as hc
from archeryutils import load_rounds

ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ],
)


class GroupData(TypedDict):
    """Structure for AGB Outdoor classification data."""

    classes: list[str]
    max_distance: list[int]
    classes_long: list[str]
    class_HC: npt.NDArray[np.float64]
    min_dists: npt.NDArray[np.int64]
    prestige_rounds: list[str]


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
    agb_ages = cls_funcs.read_ages_json()
    # Read in bowstyleclass info as list of dicts
    agb_bowstyles = cls_funcs.read_bowstyles_json()
    # Read in gender info as list of dicts
    agb_genders = cls_funcs.read_genders_json()
    # Read in classification names as dict
    agb_classes_info_out = cls_funcs.read_classes_json("agb_outdoor")
    agb_classes_out = agb_classes_info_out["classes"]
    agb_classes_out_long = agb_classes_info_out["classes_long"]

    # Generate dict of classifications
    # loop over all bowstyles, genders, ages
    classification_dict = {}
    for bowstyle, gender, age in itertools.product(
        agb_bowstyles, agb_genders, agb_ages
    ):
        groupname = cls_funcs.get_groupname(
            bowstyle["bowstyle"],
            gender,
            age["age_group"],
        )

        # Get max dists for category from json file data
        # Use metres as corresponding yards >= metric
        gender_key = cast(Literal["male", "female"], gender.lower())
        max_dist = age[gender_key]

        # set step from datum based on age and gender steps required
        delta_hc_age_gender = cls_funcs.get_age_gender_step(
            gender,
            age["step"],
            bowstyle["ageStep_out"],
            bowstyle["genderStep_out"],
        )

        # set handicap threshold values for all classifications in the category
        class_hc = (
            bowstyle["datum_out"]
            + delta_hc_age_gender
            + (np.arange(len(agb_classes_out)) - 2) * bowstyle["classStep_out"]
        ).astype(np.float64)

        # get minimum distances to be shot for all classifications in the category
        min_dists = _assign_min_dist(
            gender=gender, age_group=age["age_group"], max_dists=max_dist
        )

        # Assign prestige rounds for the category
        prestige_rounds = _assign_outdoor_prestige(
            bowstyle=bowstyle["bowstyle"],
            age=age["age_group"],
            gender=gender,
            max_dist=max_dist,
        )

        groupdata: GroupData = {
            "classes": agb_classes_out,
            "max_distance": max_dist,
            "classes_long": agb_classes_out_long,
            "class_HC": class_hc,
            "min_dists": min_dists,
            "prestige_rounds": prestige_rounds,
        }

        classification_dict[groupname] = groupdata

    return classification_dict


def _assign_min_dist(
    gender: str,
    age_group: str,
    max_dists: list[int],
) -> npt.NDArray[np.int64]:
    """
    Assign appropriate minimum distance required for a category and classification.

    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    gender : str
        string defining gender
    age_group : str,
        string defining age group
    max_dists: List[int]
        list of integers defining the maximum distances for category

    Returns
    -------
    min_dists : array of int
        minimum distance [m] required for this category

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
    n_classes: int = 9  # [EMB, GMB, MB, B1, B2, B3, A1, A2, A3]

    max_dist_index = dists.index(np.min(max_dists))

    # Age group trickery:
    # U16 males and above step down for B2 and less
    if gender.lower() in ("male") and age_group.lower().replace(" ", "") in (
        "adult",
        "50+",
        "under21",
        "under18",
        "under16",
    ):
        idxs = np.array([0, 0, 0, 0, 1, 2, 3, 4, 5])

    # All other categories require max dist for B1 and B2 then step down
    else:
        idxs = np.array([0, 0, 0, 0, 0, 1, 2, 3, 4])

    return np.take(dists, idxs + max_dist_index, mode="clip")


def _assign_outdoor_prestige(
    bowstyle: str,
    gender: str,
    age: str,
    max_dist: list[int],
) -> list[str]:
    """
    Assign appropriate outdoor prestige rounds for a category.

    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    bowstyle : str
        string defining bowstyle
    gender : str
        string defining gender
    age : str,
        string defining age group
    max_dist: List[int]
        list of integers defining the maximum distances for category

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
    if bowstyle.lower() == "compound":
        # Everyone gets the 'adult' 720
        prestige_rounds.append(prestige_720_compound[0])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720_compound[1:]

    elif bowstyle.lower() == "barebow":
        # Everyone gets the 'adult' 720
        prestige_rounds.append(prestige_720_barebow[0])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720_barebow[1:]

    else:
        # Everyone gets the 'adult' 720
        prestige_rounds.append(prestige_720[0])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720[1:]

        # Additional fix for Male 50+, U18, and U16 recurve
        if gender.lower() == "male":
            if age.lower() in ("50+", "under 18"):
                prestige_rounds.append(prestige_720[1])  # 60m
            elif age.lower() == "under 16":
                prestige_rounds.append(prestige_720[2])  # 50m

    # Imperial and 1440 rounds - Check based on distance
    distance_check = distance_check + prestige_imperial
    distance_check = distance_check + prestige_metric

    # Check all other rounds based on distance
    for roundname in distance_check:
        if ALL_OUTDOOR_ROUNDS[roundname].max_distance().value >= np.min(max_dist):
            prestige_rounds.append(roundname)

    return prestige_rounds


agb_outdoor_classifications = _make_agb_outdoor_classification_dict()

del _make_agb_outdoor_classification_dict


def calculate_agb_outdoor_classification(
    score: float,
    roundname: str,
    bowstyle: str,
    gender: str,
    age_group: str,
) -> str:
    """
    Calculate AGB outdoor classification from score.

    Calculate a classification from a score given suitable inputs.
    Appropriate for 2023 ArcheryGB age groups and classifications.

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
    >>> class_func.calculate_agb_outdoor_classification(
    ...     858,
    ...     "hereford",
    ...     "recurve",
    ...     "female",
    ...     "under 18",
    ... )
    'B1'

    """
    # Check score is valid
    if score < 0 or score > ALL_OUTDOOR_ROUNDS[roundname].max_score():
        msg = (
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_OUTDOOR_ROUNDS[roundname].max_score()}.",
        )
        raise ValueError(msg)

    # Get scores required on this round for each classification
    # Enforcing full size face and compound scoring (for compounds)
    all_class_scores = agb_outdoor_classification_scores(
        roundname,
        bowstyle,
        gender,
        age_group,
    )

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
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
    roundname: str,
    bowstyle: str,
    gender: str,
    age_group: str,
) -> list[int]:
    """
    Calculate AGB outdoor classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate for 2023 ArcheryGB age groups and classifications.

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
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> class_func.agb_outdoor_classification_scores(
    ...     "hereford",
    ...     "recurve",
    ...     "female",
    ...     "adult",
    ... )
    [1232, 1178, 1107, 1015, 900, 763, 614, 466, 336]

    If a classification cannot be achieved a fill value of `-9999` is returned:

    >>> class_func.agb_outdoor_classification_scores(
    ...     "bristol_ii",
    ...     "recurve",
    ...     "female",
    ...     "adult",
    ... )
    [-9999, -9999, -9999, -9999, -9999, 931, 797, 646, 493]

    """
    if bowstyle.lower() in ("traditional", "flatbow", "asiatic"):
        bowstyle = "Barebow"
    elif bowstyle.lower() in ("compound barebow", "compound longbow"):
        bowstyle = "Compound"

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
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
