"""
Code for calculating Archery GB outdoor classifications.

Routine Listings
----------------
_make_agb_outdoor_classification_dict
calculate_agb_outdoor_classification
agb_outdoor_classification_scores
"""
# Due to structure of similar classification schemes they may trigger duplicate code.
# => disable for classification files and tests
# pylint: disable=duplicate-code

from typing import List, Dict, Any
from collections import OrderedDict
import numpy as np

from archeryutils import load_rounds
from archeryutils.handicaps import handicap_equations as hc_eq
import archeryutils.classifications.classification_utils as cls_funcs


ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ]
)


def _make_agb_outdoor_classification_dict() -> Dict[str, Dict[str, Any]]:
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

                # Get max dists for category from json file data
                # Use metres as corresponding yards >= metric
                max_dist = age[gender.lower()]

                classification_dict[groupname] = {
                    "classes": agb_classes_out,
                    "max_distance": max_dist,
                    "classes_long": agb_classes_out_long,
                }

                # set step from datum based on age and gender steps required
                delta_hc_age_gender = cls_funcs.get_age_gender_step(
                    gender,
                    age["step"],
                    bowstyle["ageStep_out"],
                    bowstyle["genderStep_out"],
                )

                classification_dict[groupname]["class_HC"] = np.empty(
                    len(agb_classes_out)
                )
                classification_dict[groupname]["min_dists"] = np.empty(
                    len(agb_classes_out)
                )
                for i in range(len(agb_classes_out)):
                    # Assign handicap for this classification
                    classification_dict[groupname]["class_HC"][i] = (
                        bowstyle["datum_out"]
                        + delta_hc_age_gender
                        + (i - 2) * bowstyle["classStep_out"]
                    )

                    # Get minimum distance that must be shot for this classification
                    classification_dict[groupname]["min_dists"][i] = assign_min_dist(
                        n_class=i,
                        gender=gender,
                        age_group=age["age_group"],
                        max_dists=max_dist,
                    )

                # Assign prestige rounds for the category
                classification_dict[groupname][
                    "prestige_rounds"
                ] = assign_outdoor_prestige(
                    bowstyle=bowstyle["bowstyle"],
                    age=age["age_group"],
                    gender=gender,
                    max_dist=max_dist,
                )

    return classification_dict


def assign_min_dist(
    n_class: int,
    gender: str,
    age_group: str,
    max_dists: List[int],
) -> int:
    """
    Assign appropriate minimum distance required for a category and classification.

    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    n_class : int
        integer corresponding to classification [0=EMB, 8=A3]
    gender : str
        string defining gender
    age_group : str,
        string defining age group
    max_dists: List[int]
        list of integers defining the maximum distances for category

    Returns
    -------
    min_dist : int
        minimum distance [m] required for this classification

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # List of maximum distances for use in assigning maximum distance [metres]
    # Use metres because corresponding yards distances are >= metric ones
    dists = [90, 70, 60, 50, 40, 30, 20, 15]

    max_dist_index = dists.index(np.min(max_dists))

    # B1 and above
    if n_class <= 3:
        # All MB and B1 require max distance for everyone:
        return dists[max_dist_index]

    # Below B1
    # Age group trickery:
    # U16 males and above step down for B2 and beyond
    if gender.lower() in ("male") and age_group.lower().replace(" ", "") in (
        "adult",
        "50+",
        "under21",
        "under18",
        "under16",
    ):
        return dists[max_dist_index + (n_class - 3)]

    # All other categories require max dist for B1 and B2 then step down
    try:
        return dists[max_dist_index + (n_class - 3) - 1]
    except IndexError:
        # Distances stack at the bottom end as we can't go below 15m
        return dists[-1]


def assign_outdoor_prestige(
    bowstyle: str,
    gender: str,
    age: str,
    max_dist: List[int],
) -> List[str]:
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
    distance_check: List[str] = []

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
        if ALL_OUTDOOR_ROUNDS[roundname].max_distance() >= np.min(max_dist):
            prestige_rounds.append(roundname)

    return prestige_rounds


agb_outdoor_classifications = _make_agb_outdoor_classification_dict()

del _make_agb_outdoor_classification_dict


def calculate_agb_outdoor_classification(
    roundname: str, score: float, bowstyle: str, gender: str, age_group: str
) -> str:
    """
    Calculate AGB outdoor classification from score.

    Calculate a classification from a score given suitable inputs.
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
    if score < 0 or score > ALL_OUTDOOR_ROUNDS[roundname].max_score():
        raise ValueError(
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_OUTDOOR_ROUNDS[roundname].max_score()}."
        )

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

    # We iterate over class_data keys, so convert use OrderedDict
    class_data: OrderedDict[str, Dict[str, Any]] = OrderedDict([])
    for i, class_i in enumerate(group_data["classes"]):
        class_data[class_i] = {
            "min_dist": group_data["min_dists"][i],
            "score": all_class_scores[i],
        }

    # Check if this is a prestige round and appropriate distances
    # remove ineligible classes from class_data
    class_data = check_prestige_distance(roundname, groupname, class_data)

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


def check_prestige_distance(
    roundname: str, groupname: str, class_data: OrderedDict[str, Dict[str, Any]]
) -> OrderedDict[str, Dict[str, Any]]:
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
    class_data : OrderedDict
        classification information for each category.

    Returns
    -------
    class_data : OrderedDict
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
        to_del: List[str] = []
        round_max_dist = ALL_OUTDOOR_ROUNDS[roundname].max_distance()
        for class_i_name, class_i_data in class_data.items():
            if class_i_data["min_dist"] > round_max_dist:
                to_del.append(class_i_name)
        for class_i in to_del:
            del class_data[class_i]

    return class_data


def agb_outdoor_classification_scores(
    roundname: str, bowstyle: str, gender: str, age_group: str
) -> List[int]:
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
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    if bowstyle.lower() in ("traditional", "flatbow", "asiatic"):
        bowstyle = "Barebow"

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_outdoor_classifications[groupname]

    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    class_scores = [
        hc_eq.score_for_round(
            ALL_OUTDOOR_ROUNDS[cls_funcs.strip_spots(roundname)],
            group_data["class_HC"][i],
            "AGB",
            hc_params,
            round_score_up=True,
        )[0]
        for i in range(len(group_data["classes"]))
    ]

    # Reduce list based on other criteria besides handicap
    # is it a prestige round? If not remove MB scores
    if roundname not in agb_outdoor_classifications[groupname]["prestige_rounds"]:
        class_scores[0:3] = [-9999] * 3

        # If not prestige, what classes are eligible based on category and distance
        round_max_dist = ALL_OUTDOOR_ROUNDS[roundname].max_distance()
        for i in range(3, len(class_scores)):
            if group_data["min_dists"][i] > round_max_dist:
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
