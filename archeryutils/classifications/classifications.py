import numpy as np
import json
from pathlib import Path

from archeryutils import rounds


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
    classification_dict : dict of str : dict of str: list, list
        dictionary indexed on group name (e.g 'adult_female_barebow')
        containing list of handicaps associated with each classification
        and a list of prestige rounds eligible for that group

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
    age_file = Path(__file__).parent / "AGB_ages.json"
    with open(age_file) as json_file:
        AGB_ages = json.load(json_file)

    # Read in bowstyleclass info as list of dicts
    bowstyles_file = Path(__file__).parent / "AGB_bowstyles.json"
    with open(bowstyles_file) as json_file:
        AGB_bowstyles = json.load(json_file)

    # Read in gender info as list of dicts
    gender_file = Path(__file__).parent / "AGB_genders.json"
    with open(gender_file) as json_file:
        AGB_genders = json.load(json_file)["AGB_genders"]

    # Read in classification names as dict
    classes_file = Path(__file__).parent / "AGB_classes.json"
    with open(classes_file) as json_file:
        AGB_classes = json.load(json_file)["classes"]

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
                    # Additional fix for Masters and U18 Males
                    if gender.lower() == "male" and (
                        age["age_group"].lower() == "50+"
                        or age["age_group"].lower() == "under 18"
                    ):
                        prestige_rounds.append(prestige_720[1])

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
                }

    return classification_dict


AGB_outdoor_classifications = _make_AGB_outdoor_classification_dict()

del _make_AGB_outdoor_classification_dict


if __name__ == "__main__":

    for item in AGB_outdoor_classifications:
        print(item, AGB_outdoor_classifications[item]["prestige_rounds"])
