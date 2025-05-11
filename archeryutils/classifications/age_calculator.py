"""
Utilities to calculate the age group an athlete is in.

Routine Listings
----------------
get_age_group
"""

import datetime

from archeryutils.classifications.AGB_data import AGB_ages
from archeryutils.classifications.classification_utils import read_ages_json, AGBAgeData


def calculate_age_group(year_of_birth: int, year_of_event: int = None, ages_json: dict[str, AGBAgeData] = None) -> AGB_ages:
    """
    Calculate the age group for an athlete.

    Parameters
    ----------
    year_of_birth : int
        The year that the athelete was born in
    year_of_event : int | None
        The year that the event is taking place in. Defaults to the current year as per datetime.datetime.now()
    ages_json : dict[str, AGBAgeData]
        The available age groups. Defaults to those found in the "./AGB_ages.json"

    Returns
    -------
    age_group : AGB_ages
        The relevant age group from the AGB_ages enum

    References
    ----------
    Archery GB Rules of Shooting
    """
    if ages_json is None:
        ages_json = read_ages_json()

    if year_of_event is None:
        year_of_event = datetime.datetime.now().year

    # Order any age groups with a min_age flag, with the oldest first
    over_ages = filter(lambda age: age[1].get("min_age"), ages_json.items())
    over_ages = sorted(over_ages, key=lambda age: age[1]["min_age"], reverse=True)

    # Order any age groups with a max_age flag, with the youngest first
    under_ages = filter(lambda age: age[1].get("max_age"), ages_json.items())
    under_ages = sorted(under_ages, key=lambda age: age[1]["max_age"])

    # If no min or max age is hit, assume the first unmarked category
    adult_age_key = next(filter(lambda age: not age[1].get("max_age") and not age[1].get("min_age"), ages_json.items()))[0]

    birthday_this_year = year_of_event - year_of_birth

    for age_key, age_data in over_ages:
        if birthday_this_year >= age_data["min_age"]:
            return AGB_ages[age_key]

    for age_key, age_data in under_ages:
        if birthday_this_year <= age_data["max_age"]:
            return AGB_ages[age_key]

    return AGB_ages[adult_age_key]
