import numpy as np
import json
from pathlib import Path

from archeryutils import rounds
from archeryutils.handicaps import handicap_equations as hc_eq
from archeryutils.handicaps import handicap_functions as hc_func


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
    AGB_classes = read_classes_json()["classes"]

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

                class_HC = np.empty(len(AGB_classes))
                for i, classification in enumerate(AGB_classes):
                    class_HC[i] = (
                        bowstyle["datum"]
                        + age_steps * bowstyle["ageStep"]
                        + gender_steps * bowstyle["genderStep"]
                        + (i - 2) * bowstyle["classStep"]
                    )

                # Assign prestige rounds for the category
                #  - check bowstyle, distance, and age
                prestige_rounds = []
                max_dist = age[gender.lower()]

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

                dictkey = (
                    f"{age['age_group'].lower().replace(' ', '')}_"
                    f"{gender.lower()}_{bowstyle['bowstyle'].lower()}"
                )
                classification_dict[dictkey] = {
                    "class_HC": class_HC,
                    "prestige_rounds": prestige_rounds,
                    "max_distance": max_dist,
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

    groupname = (
        f"{age_group.lower().replace(' ', '')}_"
        f"{gender.lower()}_"
        f"{bowstyle.lower()}"
    )

    # Dict mapping handicaps to classifications with min dist for each classification
    classes_file = Path(__file__).parent / "AGB_classes.json"
    with open(classes_file) as json_file:
        AGB_classes = json.load(json_file)["classes"]
    dists = [90, 70, 60, 50, 40, 30]
    max_dist_index = dists.index(
        min(AGB_outdoor_classifications[groupname]["max_distance"])
    )

    # TODO: This could perhaps be made it's own function if useful elsewhere...
    # Might require significant restructure of this function (which is overly large...)
    # print(f'max_dist req. for {groupname} is {dists[max_dist_index]}')

    # MB and B1 all require max distance:
    dist_req = [dists[max_dist_index]] * 3
    for i in range(6):
        try:
            dist_req = dist_req + [dists[max_dist_index + i]]
        except IndexError:
            dist_req = dist_req + [dists[-1]]
    HC2class = dict(
        zip(
            AGB_outdoor_classifications[groupname]["class_HC"],
            zip(AGB_classes, dist_req),
        )
    )

    # calculate handicap
    hc_params = hc_eq.HcParams()
    hc_from_score = hc_func.handicap_from_score(
        score, all_outdoor_rounds[roundname], "AGB", hc_params, int_prec=True
    )

    #print(hc_from_score)

    # is it a prestige round? If not remove MB as an option
    if roundname not in AGB_outdoor_classifications[groupname]["prestige_rounds"]:
        # TODO: a list of dictionary keys is super dodgy python...
        #   can this be improved?
        for item in list(HC2class.keys())[0:3]:
            del HC2class[item]

        # If not prestige, what classes are eligible based on category and distance
        to_del = []
        for item in HC2class:
            round_max_dist = all_outdoor_rounds[roundname].max_distance()
            if HC2class[item][1] > round_max_dist:
                to_del.append(item)
        for item in to_del:
            del HC2class[item]

    # Of those remaining, what is the highest classification this score gets?
    # Loop over dict of HC to class name
    to_del = []
    for item in HC2class:
        if item < hc_from_score:
            to_del.append(item)
    for item in to_del:
        del HC2class[item]

    try:
        classification_from_score = HC2class[list(HC2class.keys())[0]][0]
        return classification_from_score
    except IndexError:
        return 'UC' 


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
