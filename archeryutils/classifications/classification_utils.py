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


def read_classes_out_json(
    classes_file: Path = Path(__file__).parent / "AGB_classes_out.json",
) -> Dict[str, Any]:
    """
    Read AGB outdoor classes in from neighbouring json file to dict.

    Parameters
    ----------
    classes_file : Path
        path to json file

    Returns
    -------
    classes : dict
        AGB classes data from file

    References
    ----------
    Archery GB Rules of Shooting
    """
    # Read in classification names as dict
    with open(classes_file, encoding="utf-8") as json_file:
        classes = json.load(json_file)
    if isinstance(classes, dict):
        return classes
    raise TypeError(
        f"Unexpected classes input when reading from json file. "
        f"Expected dict() but got {type(classes)}. Check {classes_file}."
    )


# TODO This could (should) be condensed into one method with the above function
def read_classes_in_json(
    classes_file: Path = Path(__file__).parent / "AGB_classes_in.json",
) -> Dict[str, Any]:
    """
    Read AGB indoor classes in from neighbouring json file to dict.

    Parameters
    ----------
    classes_file : Path
        path to json file

    Returns
    -------
    classes : dict
        AGB classes data from file

    References
    ----------
    Archery GB Rules of Shooting
    """
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
    return roundname


def get_compound_codename(round_codenames):
    """
    Convert any indoor rounds with special compound scoring to the compound format.

    Parameters
    ----------
    round_codenames : str or list of str
        list of str round codenames to check

    Returns
    -------
    round_codenames : str or list of str
        list of amended round codenames for compound
    """
    notlistflag = False
    if not isinstance(round_codenames, list):
        round_codenames = [round_codenames]
        notlistflag = True

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

    for i, codename in enumerate(round_codenames):
        if codename in convert_dict:
            round_codenames[i] = convert_dict[codename]
    if notlistflag:
        return round_codenames[0]
    return round_codenames
