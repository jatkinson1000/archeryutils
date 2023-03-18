"""
Code for calculating Archery GB classifications.

Extended Summary
----------------
Code to add functionality to the basic handicap equations code
in handicap_equations.py including inverse function and display.

Routine Listings
----------------
read_ages_json
read_bowstyles_json
read_genders_json
read_classes_json
get_groupname
_make_AGB_outdoor_classification_dict
_make_AGB_indoor_classification_dict
_make_AGB_field_classification_dict
calculate_AGB_outdoor_classification
AGB_outdoor_classification_scores
calculate_AGB_indoor_classification
AGB_indoor_classification_scores
calculate_AGB_field_classification
AGB_field_classification_scores

"""
import json
from pathlib import Path
import numpy as np

from archeryutils import load_rounds
from archeryutils.handicaps import handicap_equations as hc_eq


def read_ages_json(age_file=Path(__file__).parent / "AGB_ages.json"):
    """
    Read AGB age categories in from neighbouring json file to list of dicts.

    Parameters
    ----------
    age_file : Path
        path to json file

    Returns
    -------
    ages : list of dict
        AGB age category data from file

    References
    ----------
    Archery GB Rules of Shooting
    """
    with open(age_file, encoding="utf-8") as json_file:
        ages = json.load(json_file)
    return ages


def read_bowstyles_json(bowstyles_file=Path(__file__).parent / "AGB_bowstyles.json"):
    """
    Read AGB  bowstyles in from neighbouring json file to list of dicts.

    Parameters
    ----------
    bowstyles_file : Path
        path to json file

    Returns
    -------
    bowstyles : list of dict
        AGB bowstyle category data from file

    References
    ----------
    Archery GB Rules of Shooting
    """
    with open(bowstyles_file, encoding="utf-8") as json_file:
        bowstyles = json.load(json_file)
    return bowstyles


def read_genders_json(genders_file=Path(__file__).parent / "AGB_genders.json"):
    """
    Read AGB genders in from neighbouring json file to list of dicts.

    Parameters
    ----------
    genders_file : Path
        path to json file

    Returns
    -------
    genders : list of dict
        AGB gender data from file

    References
    ----------
    Archery GB Rules of Shooting
    """
    # Read in gender info as list
    with open(genders_file, encoding="utf-8") as json_file:
        genders = json.load(json_file)["genders"]
    return genders


def read_classes_json(classes_file=Path(__file__).parent / "AGB_classes.json"):
    """
    Read AGB classes in from neighbouring json file to list of dicts.

    Parameters
    ----------
    classes_file : Path
        path to json file

    Returns
    -------
    classes : list of dict
        AGB classes data from file

    References
    ----------
    Archery GB Rules of Shooting
    """
    # Read in classification names as dict
    with open(classes_file, encoding="utf-8") as json_file:
        classes = json.load(json_file)
    return classes


def get_groupname(bowstyle, gender, age_group):
    """
    Generate a single string id for a particular category.

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
    """
    groupname = (
        f"{age_group.lower().replace(' ', '')}_"
        f"{gender.lower()}_"
        f"{bowstyle.lower()}"
    )

    return groupname


def _make_AGB_outdoor_classification_dict():
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

    all_outdoor_rounds = load_rounds.read_json_to_round_dict(
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
                # Get age steps from Adult
                age_steps = age["step"]

                # Get number of gender steps required
                # Perform fiddle in age steps where genders diverge at U15/U16
                if gender.lower() == "female" and age["step"] <= 3:
                    gender_steps = 1
                else:
                    gender_steps = 0

                groupname = get_groupname(
                    bowstyle["bowstyle"], gender, age["age_group"]
                )

                # Get max dists for category from json file data
                # Use metres as corresponding yards >= metric
                max_dist = age[gender.lower()]
                max_dist_index = dists.index(min(max_dist))

                class_HC = np.empty(len(AGB_classes))
                min_dists = np.empty((len(AGB_classes), 3))
                for i in range(len(AGB_classes)):
                    # Assign handicap for this classification
                    class_HC[i] = (
                        bowstyle["datum"]
                        + age_steps * bowstyle["ageStep"]
                        + gender_steps * bowstyle["genderStep"]
                        + (i - 2) * bowstyle["classStep"]
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
                        except IndexError as e:
                            # Shouldn't really get here...
                            print(
                                f"{e} cannot select minimum distances for "
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
                        if age["age_group"].lower() in ("50+", "under 18"):
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


def _make_AGB_indoor_classification_dict():
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
    AGB_indoor_classes = ["A", "B", "C", "D", "E", "F", "G", "H"]

    # Generate dict of classifications
    # for both bowstyles, for both genders
    classification_dict = {}
    classification_dict[get_groupname("Compound", "Male", "Adult")] = {
        "classes": AGB_indoor_classes,
        "class_HC": [5, 12, 24, 37, 49, 62, 73, 79],
    }
    classification_dict[get_groupname("Compound", "Female", "Adult")] = {
        "classes": AGB_indoor_classes,
        "class_HC": [12, 18, 30, 43, 55, 67, 79, 83],
    }
    classification_dict[get_groupname("Recurve", "Male", "Adult")] = {
        "classes": AGB_indoor_classes,
        "class_HC": [14, 21, 33, 46, 58, 70, 80, 85],
    }
    classification_dict[get_groupname("Recurve", "Female", "Adult")] = {
        "classes": AGB_indoor_classes,
        "class_HC": [21, 27, 39, 51, 64, 75, 85, 90],
    }

    return classification_dict


def _make_AGB_field_classification_dict():
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
    AGB_field_classes = [
        "Grand Master Bowman",
        "Master Bowman",
        "Bowman",
        "1st Class",
        "2nd Class",
        "3rd Class",
    ]

    # Generate dict of classifications
    # for both bowstyles, for both genders
    classification_dict = {}
    classification_dict[get_groupname("Compound", "Male", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [393, 377, 344, 312, 279, 247],
    }
    classification_dict[get_groupname("Compound", "Female", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [376, 361, 330, 299, 268, 237],
    }
    classification_dict[get_groupname("Recurve", "Male", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [338, 317, 288, 260, 231, 203],
    }
    classification_dict[get_groupname("Recurve", "Female", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [322, 302, 275, 247, 220, 193],
    }
    classification_dict[get_groupname("Barebow", "Male", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [328, 307, 279, 252, 224, 197],
    }
    classification_dict[get_groupname("Barebow", "Female", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [303, 284, 258, 233, 207, 182],
    }
    classification_dict[get_groupname("Longbow", "Male", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [201, 188, 171, 155, 137, 121],
    }
    classification_dict[get_groupname("Longbow", "Female", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [303, 284, 258, 233, 207, 182],
    }
    classification_dict[get_groupname("Traditional", "Male", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [262, 245, 223, 202, 178, 157],
    }
    classification_dict[get_groupname("Traditional", "Female", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [197, 184, 167, 152, 134, 118],
    }
    classification_dict[get_groupname("Flatbow", "Male", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [262, 245, 223, 202, 178, 157],
    }
    classification_dict[get_groupname("Flatbow", "Female", "Adult")] = {
        "classes": AGB_field_classes,
        "class_scores": [197, 184, 167, 152, 134, 118],
    }

    # Juniors
    classification_dict[get_groupname("Compound", "Male", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [385, 369, 337, 306, 273, 242],
    }

    classification_dict[get_groupname("Compound", "Female", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [357, 343, 314, 284, 255, 225],
    }

    classification_dict[get_groupname("Recurve", "Male", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [311, 292, 265, 239, 213, 187],
    }

    classification_dict[get_groupname("Recurve", "Female", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [280, 263, 239, 215, 191, 168],
    }

    classification_dict[get_groupname("Barebow", "Male", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [298, 279, 254, 229, 204, 179],
    }

    classification_dict[get_groupname("Barebow", "Female", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [251, 236, 214, 193, 172, 151],
    }

    classification_dict[get_groupname("Longbow", "Male", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [161, 150, 137, 124, 109, 96],
    }

    classification_dict[get_groupname("Longbow", "Female", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [122, 114, 103, 94, 83, 73],
    }

    classification_dict[get_groupname("Traditional", "Male", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [210, 196, 178, 161, 143, 126],
    }

    classification_dict[get_groupname("Traditional", "Female", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [158, 147, 134, 121, 107, 95],
    }

    classification_dict[get_groupname("Flatbow", "Male", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [210, 196, 178, 161, 143, 126],
    }

    classification_dict[get_groupname("Flatbow", "Female", "Under 18")] = {
        "classes": AGB_field_classes,
        "class_scores": [158, 147, 134, 121, 107, 95],
    }

    return classification_dict


AGB_outdoor_classifications = _make_AGB_outdoor_classification_dict()
AGB_indoor_classifications = _make_AGB_indoor_classification_dict()
AGB_field_classifications = _make_AGB_field_classification_dict()

del _make_AGB_outdoor_classification_dict
del _make_AGB_indoor_classification_dict
del _make_AGB_field_classification_dict


def calculate_AGB_outdoor_classification(roundname, score, bowstyle, gender, age_group):
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
    # TODO: Need routines to sanitise/deal with variety of user inputs

    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_outdoor_rounds = load_rounds.read_json_to_round_dict(
        [
            "AGB_outdoor_imperial.json",
            "AGB_outdoor_metric.json",
            "WA_outdoor.json",
        ]
    )

    if bowstyle.lower() in ("traditional", "flatbow"):
        bowstyle = "Barebow"

    groupname = get_groupname(bowstyle, gender, age_group)
    group_data = AGB_outdoor_classifications[groupname]

    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    class_scores = [
        hc_eq.score_for_round(
            all_outdoor_rounds[roundname],
            group_data["class_HC"][i],
            "AGB",
            hc_params,
            round_score_up=True,
        )[0]
        for i, class_i in enumerate(group_data["classes"])
    ]
    # class_data = dict(
    #    zip(group_data["classes"], zip(group_data["min_dists"], class_scores))
    # )
    class_data = {}
    for i, class_i in enumerate(group_data["classes"]):
        class_data[class_i] = {
            "min_dists": group_data["min_dists"][i, :],
            "score": class_scores[i],
        }

    # is it a prestige round? If not remove MB as an option
    if roundname not in AGB_outdoor_classifications[groupname]["prestige_rounds"]:
        # TODO: a list of dictionary keys is super dodgy python...
        #   can this be improved?
        for MB_class in list(class_data.keys())[0:3]:
            del class_data[MB_class]

        # If not prestige, what classes are eligible based on category and distance
        to_del = []
        round_max_dist = all_outdoor_rounds[roundname].max_distance()
        for class_i in class_data.items():
            if class_i[1]["min_dists"][-1] > round_max_dist:
                to_del.append(class_i[0])
        for class_i in to_del:
            del class_data[class_i]

    # Classification based on score - accounts for fractional HC
    # TODO Make this its own function for later use in geberating tables?
    # Of those classes remaining, what is the highest classification this score gets?
    to_del = []
    for item in class_data.items():
        if item[1]["score"] > score:
            to_del.append(item[0])
    for item in to_del:
        del class_data[item]

    try:
        classification_from_score = list(class_data.keys())[0]
        return classification_from_score
    except IndexError:
        return "UC"


def AGB_outdoor_classification_scores(roundname, bowstyle, gender, age_group):
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
    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_outdoor_rounds = load_rounds.read_json_to_round_dict(
        [
            "AGB_outdoor_imperial.json",
            "AGB_outdoor_metric.json",
            "WA_outdoor.json",
            "Custom.json",
        ]
    )

    groupname = get_groupname(bowstyle, gender, age_group)
    group_data = AGB_outdoor_classifications[groupname]

    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    class_scores = [
        hc_eq.score_for_round(
            all_outdoor_rounds[roundname],
            group_data["class_HC"][i],
            "AGB",
            hc_params,
            round_score_up=True,
        )[0]
        for i in range(len(group_data["classes"]))
    ]

    # Reduce list based on other criteria besides handicap
    # is it a prestige round? If not remove MB scores
    if roundname not in AGB_outdoor_classifications[groupname]["prestige_rounds"]:
        class_scores[0:3] = [-9999] * 3

        # If not prestige, what classes are eligible based on category and distance
        round_max_dist = all_outdoor_rounds[roundname].max_distance()
        for i in range(3, len(class_scores)):
            if min(group_data["min_dists"][i, :]) > round_max_dist:
                class_scores[i] = -9999

    return class_scores


def calculate_AGB_indoor_classification(
    roundname, score, bowstyle, gender, age_group, hc_scheme="AGBold"
):
    """
    Calculate AGB indoor classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.
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
    hc_scheme : str
        handicap scheme to be used for legacy purposes. Default AGBold

    Returns
    -------
    classification_from_score : str
        the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # TODO: Need routines to sanitise/deal with variety of user inputs

    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_indoor_rounds = load_rounds.read_json_to_round_dict(
        [
            "AGB_indoor.json",
            "WA_indoor.json",
        ]
    )

    # deal with reduced categories:
    age_group = "Adult"
    if bowstyle.lower() not in ("compound"):
        bowstyle = "Recurve"

    groupname = get_groupname(bowstyle, gender, age_group)
    group_data = AGB_indoor_classifications[groupname]

    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    class_scores = [
        hc_eq.score_for_round(
            all_indoor_rounds[roundname],
            group_data["class_HC"][i],
            hc_scheme,
            hc_params,
            round_score_up=True,
        )[0]
        for i, class_i in enumerate(group_data["classes"])
    ]

    class_data = dict(zip(group_data["classes"], class_scores))

    # What is the highest classification this score gets?
    to_del = []
    for score_bound in class_data:
        if class_data[score_bound] > score:
            to_del.append(score_bound)
    for del_class in to_del:
        del class_data[del_class]

    # NB No fiddle for Worcester required with this logic...
    # Beware of this later on, however, if we wish to rectify the 'anomaly'

    try:
        classification_from_score = list(class_data.keys())[0]
        return classification_from_score
    except IndexError:
        # return "UC"
        return "unclassified"


def AGB_indoor_classification_scores(
    roundname, bowstyle, gender, age_group, hc_scheme="AGBold"
):
    """
    Calculate AGB indoor classification scores for category.

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
    hc_scheme : str
        handicap scheme to be used for legacy purposes. Default AGBold

    Returns
    -------
    classification_scores : ndarray
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7
    """
    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_indoor_rounds = load_rounds.read_json_to_round_dict(
        [
            "AGB_indoor.json",
            "WA_indoor.json",
        ]
    )

    # deal with reduced categories:
    age_group = "Adult"
    if bowstyle.lower() not in ("compound"):
        bowstyle = "Recurve"

    groupname = get_groupname(bowstyle, gender, age_group)
    group_data = AGB_indoor_classifications[groupname]

    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    class_scores = [
        hc_eq.score_for_round(
            all_indoor_rounds[roundname],
            group_data["class_HC"][i],
            hc_scheme,
            hc_params,
            round_score_up=True,
        )[0]
        for i, class_i in enumerate(group_data["classes"])
    ]

    return class_scores


def calculate_AGB_field_classification(roundname, score, bowstyle, gender, age_group):
    """
    Calculate AGB field classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.

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
        the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # TODO: Need routines to sanitise/deal with variety of user inputs

    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_field_rounds = load_rounds.read_json_to_round_dict(
        [
            "WA_field.json",
        ]
    )

    # deal with reduced categories:
    if age_group.lower().replace(" ", "") in ("adult", "50+", "under21"):
        age_group = "Adult"
    else:
        age_group = "Under 18"

    groupname = get_groupname(bowstyle, gender, age_group)

    # Get scores required on this round for each classification
    group_data = AGB_field_classifications[groupname]

    # Check Round is appropriate:
    # Sighted can have any Red 24, unsightes can have any blue 24
    if bowstyle.lower() in ["compound", "recurve"] and "wa_field_24_red_" not in roundname:
        return "unclassified"
    if (
        bowstyle.lower() in ["barebow", "longbow", "traditional", "flatbow"]
        and "wa_field_24_blue_" not in roundname):
        return "unclassified"

    # What is the highest classification this score gets?
    class_scores = dict(zip(group_data["classes"], group_data["class_scores"]))
    for item in class_scores:
        if class_scores[item] > score:
            pass
        else:
            return item

    # if lower than 3rd class score return "UC"
    return "unclassified"


def AGB_field_classification_scores(roundname, bowstyle, gender, age_group):
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
    classification_scores : ndarray
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7
    """
    # TODO: Should this be defined outside the function to reduce I/O or does
    #   it have no effect?
    all_field_rounds = load_rounds.read_json_to_round_dict(
        [
            "WA_field.json",
        ]
    )

    # deal with reduced categories:
    if age_group.lower().replace(" ", "") in ("adult", "50+", "under21"):
        age_group = "Adult"
    else:
        age_group = "Under 18"

    groupname = get_groupname(bowstyle, gender, age_group)
    group_data = AGB_field_classifications[groupname]

    # Get scores required on this round for each classification
    return group_data["class_scores"]


if __name__ == "__main__":
    for classification in AGB_outdoor_classifications.items():
        print(
            classification[0],
            classification[1]["prestige_rounds"],
        )

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
