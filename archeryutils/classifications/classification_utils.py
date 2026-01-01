"""
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
from functools import cache
from pathlib import Path
from typing import Literal, TypedDict

from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders


class AGBCategory(TypedDict):
    """Structure for AGB category data (bowstyle, gender, age_group)."""

    bowstyle: AGB_bowstyles
    gender: AGB_genders
    age_group: AGB_ages


class AGBAgeData(TypedDict):
    """Structure for AGB age group data."""

    desc: str
    age_group: str
    male: list[float]
    female: list[float]
    sighted: list[float]
    unsighted: list[float]
    step: int


@cache
def read_ages_json() -> dict[str, AGBAgeData]:
    """
    Read AGB age categories in from neighbouring json file to list of dicts.

    Returns
    -------
    ages : list of dict
        AGB age category data from file

    Raises
    ------
    TypeError
        If the contents of the data file can't be read properly

    References
    ----------
    Archery GB Rules of Shooting
    """
    age_file = Path(__file__).parent.joinpath("data", "AGB_ages.json")
    ages = json.loads(age_file.read_text(encoding="utf-8"))

    if not isinstance(ages, dict):
        msg = (
            f"Unexpected ages input when reading from json file. "
            f"Expected dict() but got {type(ages)}. Check {age_file}."
        )
        raise TypeError(msg)

    return ages


class AGBBowstyleData(TypedDict):
    """Structure for AGB bowstyle data."""

    bowstyle: str
    datum_out: float
    classStep_out: float
    genderStep_out: float
    ageStep_out: float
    datum_in: float
    classStep_in: float
    genderStep_in: float
    ageStep_in: float
    datum_field: float
    classStep_field: float
    genderStep_field: float
    ageStep_field: float


@cache
def read_bowstyles_json() -> dict[str, AGBBowstyleData]:
    """
    Read AGB  bowstyles in from neighbouring json file to list of dicts.

    Returns
    -------
    bowstyles : list of dict
        AGB bowstyle category data from file

    Raises
    ------
    TypeError
        If the contents of the data file can't be read properly

    References
    ----------
    Archery GB Rules of Shooting
    """
    bowstyles_file = Path(__file__).parent.joinpath("data", "AGB_bowstyles.json")
    bowstyles = json.loads(bowstyles_file.read_text(encoding="utf-8"))

    if not isinstance(bowstyles, dict):
        msg = (
            f"Unexpected bowstyles input when reading from json file. "
            f"Expected dict() but got {type(bowstyles)}. Check {bowstyles_file}."
        )
        raise TypeError(msg)

    return bowstyles


@cache
def read_genders_json() -> list[Literal["Male", "Female"]]:
    """
    Read AGB genders in from neighbouring json file to list of dict.

    Returns
    -------
    genders : list of str
        AGB gender data from file

    Raises
    ------
    TypeError
        If the contents of the data file can't be read properly

    References
    ----------
    Archery GB Rules of Shooting
    """
    # Read in gender info as list
    genders_file = Path(__file__).parent.joinpath("data", "AGB_genders.json")
    genders = json.loads(genders_file.read_text(encoding="utf-8"))["genders"]

    if not isinstance(genders, list):
        msg = (
            f"Unexpected genders input when reading from json file. "
            f"Expected list() but got {type(genders)}. Check {genders_file}."
        )
        raise TypeError(msg)

    return genders


class AGBClassificationData(TypedDict):
    """Structure for AGB classification name data."""

    location: str
    classes: list[str]
    classes_long: list[str]


@cache
def read_classes_json(
    class_system: str,
) -> AGBClassificationData:
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

    Raises
    ------
    ValueError
        If an unknown classification system is specified
    TypeError
        If the contents of the data file can't be read properly

    References
    ----------
    Archery GB Rules of Shooting
    """
    match class_system:
        case "agb_indoor":
            filename = "AGB_classes_in"
        # Field classifications are same as outdoor
        case "agb_outdoor" | "agb_field":
            filename = "AGB_classes_out"
        case _:
            msg = (
                "Unexpected classification system specified. "
                "Expected one of 'agb_indoor', 'agb_outdoor', 'agb_field'."
            )
            raise ValueError(msg)

    classes_file = Path(__file__).parent.joinpath("data", filename).with_suffix(".json")

    # Read in classification names as dict
    with open(classes_file, encoding="utf-8") as json_file:
        classes: AGBClassificationData = json.load(json_file)
    if isinstance(classes, dict):
        return classes
    msg = (
        f"Unexpected classes input when reading from json file. "
        f"Expected dict() but got {type(classes)}. Check {classes_file}."
    )
    raise TypeError(msg)


def get_groupname(
    bowstyle: AGB_bowstyles, gender: AGB_genders, age_group: AGB_ages
) -> str:
    """
    Generate a single string id for a particular category.

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
    groupname = f"{age_group.name}_{gender.name}_{bowstyle.name}"

    return groupname


def get_age_gender_step(
    gender: AGB_genders,
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
    gender : AGB_genders
        gender this classification applies to
    age_cat : int
        age category as an integer (number of age steps below adult e.g. 50+=1, U14=5)
    age_step : float
        age group handicap step for this category
    gender_step : float
        gender handicap step for this category

    Returns
    -------
    float
        age and gender handicap step for this category's MB relative to datum
    """
    under_16_int = 3  # U16 is the fourth age category after 50+, adult, and U18

    # There is a danger that gender step overtakes age step at U15/U16
    # interface. If this happens set to age step to align U16 with U16
    if (
        gender is AGB_genders.FEMALE
        and age_cat == under_16_int
        and age_step < gender_step
    ):
        return age_cat * age_step + age_step

    # For females under 16 or older apply gender step and age steps
    if gender is AGB_genders.FEMALE and age_cat <= under_16_int:
        return gender_step + age_cat * age_step

    # Default case for males, and females aged U15 or younger - apply only age steps
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
    round_codename : str
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
