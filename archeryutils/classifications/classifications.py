import numpy as np
import json
from pathlib import Path

from archeryutils import rounds
from archeryutils.handicaps import handicap_equations as hc_eq


def read_ages_json(age_file=Path(__file__).parent / "AGB_ages.json"):
    # Read in age group info as list of dicts
    with open(age_file) as json_file:
        ages = json.load(json_file)
    return ages


def read_bowstyles_json(bowstyles_file=Path(__file__).parent / "AGB_bowstyles.json"):
    # Read in bowstyleclass info as list of dicts
    with open(bowstyles_file) as json_file:
        bowstyles = json.load(json_file)
    return bowstyles


def read_genders_json(genders_file=Path(__file__).parent / "AGB_genders.json"):
    # Read in gender info as list
    with open(genders_file) as json_file:
        genders = json.load(json_file)["genders"]
    return genders


def read_classes_json(classes_file=Path(__file__).parent / "AGB_classes.json"):
    # Read in classification names as dict
    with open(classes_file) as json_file:
        classes = json.load(json_file)
    return classes


def get_groupname(bowstyle, gender, age_group):
    """
    Subroutine to generate a single string id for a particular category

    Parameters
    ----------
    bowstyle : str
        archer's bowstyle under AGB outdoor target rules
    gender : str
        archer's gender under AGB outdoor target rules
    age_group : str
        archer's age group under AGB outdoor target rules

    Returns
    -------
    groupname : str
        single, lower case str id for this category

    References
    ----------
    """

    groupname = (
        f"{age_group.lower().replace(' ', '')}_"
        f"{gender.lower()}_"
        f"{bowstyle.lower()}"
    )
    
    return groupname


def _make_AGB_outdoor_classification_dict():
    """
    Subroutine to generate a dictionary of dictionaries providing handicaps for
    each classification band and a list prestige rounds for each category from
    data files.
    Appropriate for 2023 ArcheryGB age groups and classifications

    Parameters
    ----------

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
    dists = [90, 70, 60, 50, 40, 30]
    
    all_outdoor_rounds = rounds.read_json_to_round_dict(
        [
            "AGB_outdoor_imperial.json",
            "AGB_outdoor_metric.json",
            # "AGB_indoor.json",
            "WA_outdoor.json",
            # "WA_indoor.json",
            # "Custom.json",
        ]
    )

    # Read in age group info as list of dicts
    AGB_ages = read_ages_json()
    # Read in bowstyleclass info as list of dicts
    AGB_bowstyles = read_bowstyles_json()
    # Read in gender info as list of dicts
    AGB_genders = read_genders_json()
    # Read in classification names as dict
    AGB_classes_info = read_classes_json()
    AGB_classes = AGB_classes_info["classes"]
    AGB_classes_long = AGB_classes_info["classes_long"]

    # Generate dict of classifications
    # loop over bowstyles
    # loop over ages
    # loop over genders
    classification_dict = {}
    for bowstyle in AGB_bowstyles:
        for age in AGB_ages:
            for gender in AGB_genders:
                # Perform fiddle in age steps where genders diverge at U15/U16
                if gender.lower() == "female" and age["step"] >= 4:
                    age_steps = age["step"] - 1
                else:
                    age_steps = age["step"]

                if gender.lower() == "female":
                    gender_steps = 1
                else:
                    gender_steps = 0

                groupname = get_groupname(bowstyle['bowstyle'], gender, age['age_group'])

                # Get max dists for category from json file data
                # Use metres as corresponding yards >= metric
                max_dist = age[gender.lower()]
                max_dist_index = dists.index(min(max_dist))

                class_HC = np.empty(len(AGB_classes))
                min_dists = np.empty(len(AGB_classes))
                for i, classification in enumerate(AGB_classes):
                    # Assign handicap for this classification
                    class_HC[i] = (
                        bowstyle["datum"]
                        + age_steps * bowstyle["ageStep"]
                        + gender_steps * bowstyle["genderStep"]
                        + (i - 2) * bowstyle["classStep"]
                    )

                    # Assign minimum distance [metres] for this classification
                    if i <= 2:
                        # MB all require max distance:
                        min_dists[i] = dists[max_dist_index]
                    else:
                        # Step down min dist from max at B1
                        try:
                            min_dists[i] = dists[max_dist_index + i - 3]
                        except IndexError:
                            min_dists[i] = dists[-1]

                # Assign prestige rounds for the category
                #  - check bowstyle, distance, and age
                prestige_rounds = []

                # 720 rounds - bowstyle dependent
                if bowstyle["bowstyle"].lower() == "compound":
                    # Everyone gets the 'adult' 720
                    prestige_rounds.append(prestige_720_compound[0])
                    # Check for junior eligible shorter rounds
                    for roundname in prestige_720_compound[1:]:
                        if all_outdoor_rounds[roundname].max_distance() >= min(
                            max_dist
                        ):
                            prestige_rounds.append(roundname)
                elif bowstyle["bowstyle"].lower() == "barebow":
                    # Everyone gets the 'adult' 720
                    prestige_rounds.append(prestige_720_barebow[0])
                    # Check for junior eligible shorter rounds
                    for roundname in prestige_720_barebow[1:]:
                        if all_outdoor_rounds[roundname].max_distance() >= min(
                            max_dist
                        ):
                            prestige_rounds.append(roundname)
                else:
                    # Everyone gets the 'adult' 720
                    prestige_rounds.append(prestige_720[0])
                    # Check for junior eligible shorter rounds
                    for roundname in prestige_720[1:]:
                        if all_outdoor_rounds[roundname].max_distance() >= min(
                            max_dist
                        ):
                            prestige_rounds.append(roundname)
                    # Additional fix for Male 50+, U18, and U16
                    if gender.lower() == "male":
                        if (
                            age["age_group"].lower() == "50+"
                            or age["age_group"].lower() == "under 18"
                        ):
                            prestige_rounds.append(prestige_720[1])
                        elif age["age_group"].lower() == "under 16":
                            prestige_rounds.append(prestige_720[2])

                # Imperial and 1440 rounds
                for roundname in prestige_imperial + prestige_metric:
                    # Compare round dist
                    if all_outdoor_rounds[roundname].max_distance() >= min(max_dist):
                        prestige_rounds.append(roundname)

                # TODO: class names and long are duplicated many times here
                #   Consider a method to reduce this (affects other code)
                classification_dict[groupname] = {
                    "classes": AGB_classes,
                    "class_HC": class_HC,
                    "prestige_rounds": prestige_rounds,
                    "max_distance": max_dist,
                    "min_dists": min_dists,
                    "classes_long": AGB_classes_long,
                }

    return classification_dict


AGB_outdoor_classifications = _make_AGB_outdoor_classification_dict()

del _make_AGB_outdoor_classification_dict


def calculate_AGB_outdoor_classification(roundname, score, bowstyle, gender, age_group):
    """
    Subroutine to calculate a classification from a score given suitable inputs
    Appropriate for 2023 ArcheryGB age groups and classifications

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

    # TODO: Need routines to sanitise/deal with variety of user inputs

    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_outdoor_rounds = rounds.read_json_to_round_dict(
        [
            "AGB_outdoor_imperial.json",
            "AGB_outdoor_metric.json",
            "WA_outdoor.json",
        ]
    )

    groupname = get_groupname(bowstyle, gender, age_group)
    group_data = AGB_outdoor_classifications[groupname]

    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    class_scores = []
    for i, class_i in enumerate(group_data["classes"]):
        class_scores.append(hc_eq.score_for_round(
            all_outdoor_rounds[roundname],
            group_data["class_HC"][i],
            "AGB",
            hc_params,
            round_score_up=True,
        )[0])

    #
    class_data = dict(zip(group_data["classes"], zip(group_data["min_dists"], class_scores)))

    # is it a prestige round? If not remove MB as an option
    if roundname not in AGB_outdoor_classifications[groupname]["prestige_rounds"]:
        # TODO: a list of dictionary keys is super dodgy python...
        #   can this be improved?
        for item in list(class_data.keys())[0:3]:
            del class_data[item]

        # If not prestige, what classes are eligible based on category and distance
        to_del = []
        for item in class_data:
            round_max_dist = all_outdoor_rounds[roundname].max_distance()
            if class_data[item][0] > round_max_dist:
                to_del.append(item)
        for item in to_del:
            del class_data[item]

    # Classification based on score - accounts for fractional HC
    # TODO Make this its own function for later use in geberating tables?
    # Of those classes remaining, what is the highest classification this score gets?
    to_del = []
    for item in class_data:
        if class_data[item][1] > score:
            to_del.append(item)
    for item in to_del:
        del class_data[item]

    try:
        classification_from_score = list(class_data.keys())[0]
        return classification_from_score
    except IndexError:
        return "UC"


if __name__ == "__main__":

    for item in AGB_outdoor_classifications:
        print(item, AGB_outdoor_classifications[item]["prestige_rounds"])

    print(
        calculate_AGB_outdoor_classification(
            "bristol_ii", 1200, "compound", "male", "adult"
        )
    )
    print(
        calculate_AGB_outdoor_classification(
            "bristol_ii", 1200, "compound", "male", "under15"
        )
    )
    print(
        calculate_AGB_outdoor_classification(
            "bristol_ii", 1200, "compound", "male", "under12"
        )
    )
