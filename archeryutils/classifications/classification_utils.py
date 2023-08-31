"""
Utils for classifications.

Extended Summary
----------------
Utilities to assist in calculations of classifications.

Routine Listings
----------------
read_ages_json
read_bowstyles_json
read_genders_json
read_classes_out_json
get_groupname
strip_spots
get_compound_codename

"""
import json
from pathlib import Path
from typing import List, Dict, Any


def read_ages_json(
    age_file: Path = Path(__file__).parent / "AGB_ages.json",
) -> List[Dict[str, Any]]:
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
    if isinstance(ages, list):
        return ages
    raise TypeError(
        f"Unexpected ages input when reading from json file. "
        f"Expected list(dict()) but got {type(ages)}. Check {age_file}."
    )


def read_bowstyles_json(
    bowstyles_file: Path = Path(__file__).parent / "AGB_bowstyles.json",
) -> List[Dict[str, Any]]:
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
    if isinstance(bowstyles, list):
        return bowstyles
    raise TypeError(
        f"Unexpected bowstyles input when reading from json file. "
        f"Expected list(dict()) but got {type(bowstyles)}. Check {bowstyles_file}."
    )


def read_genders_json(
    genders_file: Path = Path(__file__).parent / "AGB_genders.json",
) -> List[str]:
    """
    Read AGB genders in from neighbouring json file to list of dict.

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
    if isinstance(genders, list):
        return genders
    raise TypeError(
        f"Unexpected genders input when reading from json file. "
        f"Expected list() but got {type(genders)}. Check {genders_file}."
    )


def read_classes_json(
    class_system: str,
) -> Dict[str, Any]:
    """
    Read AGB classes in from neighbouring json file to dict.

    Parameters
    ----------
    class_system : str
        string specifying class system to read:
        'agb_indoor', 'agb_outdoor', 'agb_field'

    Returns
    -------
    classes : dict
        AGB classes data from file

    References
    ----------
    Archery GB Rules of Shooting
    """
    if class_system == "agb_indoor":
        filename = "AGB_classes_in.json"
    elif class_system == "agb_outdoor":
        filename = "AGB_classes_out.json"
    # elif class_system == 'agb_field':
    #     filename = "AGB_classes_field.json"
    else:
        raise ValueError(
            "Unexpected classification system specified. "
            "Expected one of 'agb_indoor', 'agb_outdoor', 'aqb_field'."
        )

    classes_file = Path(__file__).parent / filename

    # Read in classification names as dict
    with open(classes_file, encoding="utf-8") as json_file:
        classes = json.load(json_file)
    if isinstance(classes, dict):
        return classes
    raise TypeError(
        f"Unexpected classes input when reading from json file. "
        f"Expected dict() but got {type(classes)}. Check {classes_file}."
    )


def get_groupname(bowstyle: str, gender: str, age_group: str) -> str:
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


def get_age_gender_step(
    gender: str,
    age_cat: int,
    age_step: float,
    gender_step: float,
) -> float:
    """
    Calculate AGB indoor age and gender step for classification dictionaries.

    Contains a tricky fiddle for aligning Male and Female under 15 scores and below,
    and a necessary check to ensure that gender step doesnt overtake age step when
    doing this.

    Parameters
    ----------
    gender : str
        gender this classification applies to
    age_cat : int
        age category as an integer (number of age steps below adult e.g. 50+=1, U14=5)
    age_step : float
        age group handicap step for this category
    gender_step : float
        gender handicap step for this category

    Returns
    -------
    delta_hc_age_gender : float
        age and gender handicap step for this category's MB relative to datum
    """
    # There is a danger that gender step overtakes age step at U15/U16
    # interface. If this happens set to age step to align U16 with U16
    if gender.lower() == "female" and age_cat == 3 and age_step < gender_step:
        return age_cat * age_step + age_step

    # For females <=3 (Under 16 or older) apply gender step and age steps
    if gender.lower() == "female" and age_cat <= 3:
        return gender_step + age_cat * age_step

    # Default case for males, and females aged >3 (Under 15 or younger) apply age steps
    return age_cat * age_step


def strip_spots(
    roundname: str,
) -> str:
    """
    Calculate AGB indoor classification from score.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json

    Returns
    -------
    roundname : str
        name of round shot as given by 'codename' in json
    """
    roundname = roundname.replace("_triple", "")
    roundname = roundname.replace("_5_centre", "")
    roundname = roundname.replace("_small", "")
    return roundname


def get_compound_codename(round_codename: str) -> str:
    """
    Convert any indoor rounds with special compound scoring to the compound format.

    Parameters
    ----------
    round_codenames : str
        str round codename to check

    Returns
    -------
    round_codename : str
        amended round codename for compound
    """
    convert_dict = {
        "bray_i": "bray_i_compound",
        "bray_i_triple": "bray_i_compound_triple",
        "bray_ii": "bray_ii_compound",
        "bray_ii_triple": "bray_ii_compound_triple",
        "stafford": "stafford_compound",
        "portsmouth": "portsmouth_compound",
        "portsmouth_triple": "portsmouth_compound_triple",
        "vegas": "vegas_compound",
        "wa18": "wa18_compound",
        "wa18_triple": "wa18_compound_triple",
        "wa25": "wa25_compound",
        "wa25_triple": "wa25_compound_triple",
    }

    if convert_dict.get(round_codename) is not None:
        round_codename = convert_dict[round_codename]

    return round_codename
