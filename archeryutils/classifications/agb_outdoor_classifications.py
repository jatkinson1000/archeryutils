"""
Code for calculating Archery GB outdoor classifications.

Routine Listings
----------------
_make_agb_outdoor_classification_dict
calculate_agb_outdoor_classification
agb_outdoor_classification_scores
"""
from typing import List, Dict, Any
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
    # Lists of prestige rounds defined by 'codename' of 'Round' class
    # TODO: convert this to json?
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

    # List of maximum distances for use in assigning maximum distance [metres]
    # Use metres because corresponding yards distances are >= metric ones
    dists = [90, 70, 60, 50, 40, 30, 20, 15]
    padded_dists = [90, 90] + dists

    # Read in age group info as list of dicts
    agb_ages = cls_funcs.read_ages_json()
    # Read in bowstyleclass info as list of dicts
    agb_bowstyles = cls_funcs.read_bowstyles_json()
    # Read in gender info as list of dicts
    agb_genders = cls_funcs.read_genders_json()
    # Read in classification names as dict
    agb_classes_info_out = cls_funcs.read_classes_out_json()
    agb_classes_out = agb_classes_info_out["classes"]
    agb_classes_out_long = agb_classes_info_out["classes_long"]

    # Generate dict of classifications
    # loop over bowstyles
    # loop over ages
    # loop over genders
    classification_dict = {}
    for bowstyle in agb_bowstyles:
        for age in agb_ages:
            for gender in agb_genders:
                # Get age steps from Adult
                age_steps = age["step"]

                # Get number of gender steps required
                # Perform fiddle in age steps where genders diverge at U15/U16
                if gender.lower() == "female" and age["step"] <= 3:
                    gender_steps = 1
                else:
                    gender_steps = 0

                groupname = cls_funcs.get_groupname(
                    bowstyle["bowstyle"], gender, age["age_group"]
                )

                # Get max dists for category from json file data
                # Use metres as corresponding yards >= metric
                max_dist = age[gender.lower()]
                max_dist_index = dists.index(min(max_dist))

                class_hc = np.empty(len(agb_classes_out))
                min_dists = np.empty((len(agb_classes_out), 3))
                for i in range(len(agb_classes_out)):
                    # Assign handicap for this classification
                    class_hc[i] = (
                        bowstyle["datum_out"]
                        + age_steps * bowstyle["ageStep_out"]
                        + gender_steps * bowstyle["genderStep_out"]
                        + (i - 2) * bowstyle["classStep_out"]
                    )

                    # Assign minimum distance [metres] for this classification
                    if i <= 3:
                        # All MB and B1 require max distance for everyone:
                        min_dists[i, :] = padded_dists[
                            max_dist_index : max_dist_index + 3
                        ]
                    else:
                        try:
                            # Age group trickery:
                            # U16 males and above step down for B2 and beyond
                            if gender.lower() in ("male") and age[
                                "age_group"
                            ].lower().replace(" ", "") in (
                                "adult",
                                "50+",
                                "under21",
                                "under18",
                                "under16",
                            ):
                                min_dists[i, :] = padded_dists[
                                    max_dist_index + i - 3 : max_dist_index + i
                                ]
                            # All other categories require max dist for B1 and B2 then step down
                            else:
                                try:
                                    min_dists[i, :] = padded_dists[
                                        max_dist_index + i - 4 : max_dist_index + i - 1
                                    ]
                                except ValueError:
                                    # Distances stack at the bottom end
                                    min_dists[i, :] = padded_dists[-3:]
                        except IndexError as err:
                            # Shouldn't really get here...
                            print(
                                f"{err} cannot select minimum distances for "
                                f"{gender} and {age['age_group']}"
                            )
                            min_dists[i, :] = dists[-3:]

                # Assign prestige rounds for the category
                #  - check bowstyle, distance, and age
                prestige_rounds = []

                # 720 rounds - bowstyle dependent
                if bowstyle["bowstyle"].lower() == "compound":
                    # Everyone gets the 'adult' 720
                    prestige_rounds.append(prestige_720_compound[0])
                    # Check for junior eligible shorter rounds
                    for roundname in prestige_720_compound[1:]:
                        if ALL_OUTDOOR_ROUNDS[roundname].max_distance() >= min(
                            max_dist
                        ):
                            prestige_rounds.append(roundname)
                elif bowstyle["bowstyle"].lower() == "barebow":
                    # Everyone gets the 'adult' 720
                    prestige_rounds.append(prestige_720_barebow[0])
                    # Check for junior eligible shorter rounds
                    for roundname in prestige_720_barebow[1:]:
                        if ALL_OUTDOOR_ROUNDS[roundname].max_distance() >= min(
                            max_dist
                        ):
                            prestige_rounds.append(roundname)
                else:
                    # Everyone gets the 'adult' 720
                    prestige_rounds.append(prestige_720[0])
                    # Check for junior eligible shorter rounds
                    for roundname in prestige_720[1:]:
                        if ALL_OUTDOOR_ROUNDS[roundname].max_distance() >= min(
                            max_dist
                        ):
                            prestige_rounds.append(roundname)
                    # Additional fix for Male 50+, U18, and U16
                    if gender.lower() == "male":
                        if age["age_group"].lower() in ("50+", "under 18"):
                            prestige_rounds.append(prestige_720[1])
                        elif age["age_group"].lower() == "under 16":
                            prestige_rounds.append(prestige_720[2])

                # Imperial and 1440 rounds
                for roundname in prestige_imperial + prestige_metric:
                    # Compare round dist
                    if ALL_OUTDOOR_ROUNDS[roundname].max_distance() >= min(max_dist):
                        prestige_rounds.append(roundname)

                # TODO: class names and long are duplicated many times here
                #   Consider a method to reduce this (affects other code)
                classification_dict[groupname] = {
                    "classes": agb_classes_out,
                    "class_HC": class_hc,
                    "prestige_rounds": prestige_rounds,
                    "max_distance": max_dist,
                    "min_dists": min_dists,
                    "classes_long": agb_classes_out_long,
                }

    return classification_dict


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
    if bowstyle.lower() in ("traditional", "flatbow", "asiatic"):
        bowstyle = "Barebow"

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

    class_data: Dict[str, Dict[str, Any]] = {}
    for i, class_i in enumerate(group_data["classes"]):
        class_data[class_i] = {
            "min_dists": group_data["min_dists"][i, :],
            "score": all_class_scores[i],
        }

    # is it a prestige round? If not remove MB as an option
    if roundname not in agb_outdoor_classifications[groupname]["prestige_rounds"]:
        # TODO: a list of dictionary keys is super dodgy python...
        #   can this be improved?
        for MB_class in list(class_data.keys())[0:3]:
            del class_data[MB_class]

        # If not prestige, what classes are eligible based on category and distance
        to_del = []
        round_max_dist = ALL_OUTDOOR_ROUNDS[roundname].max_distance()
        for class_i in class_data.items():
            if class_i[1]["min_dists"][-1] > round_max_dist:
                to_del.append(class_i[0])
        for class_i in to_del:
            del class_data[class_i]

    # Classification based on score - accounts for fractional HC
    # TODO Make this its own function for later use in generating tables?
    # Of those classes remaining, what is the highest classification this score gets?
    to_del = []
    for classname, classdata in class_data.items():
        if classdata["score"] > score:
            to_del.append(classname)
    for item in to_del:
        del class_data[item]

    try:
        classification_from_score = list(class_data.keys())[0]
        return classification_from_score
    except IndexError:
        return "UC"


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
            ALL_OUTDOOR_ROUNDS[roundname],
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
            if min(group_data["min_dists"][i, :]) > round_max_dist:
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
