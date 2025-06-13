"""
Utilities to calculate the age group an athlete is in.

Routine Listings
----------------
get_age_group
"""

import datetime

from archeryutils.classifications.AGB_data import AGB_ages
from archeryutils.classifications.classification_utils import AGBAgeData, read_ages_json


def calculate_age_group(
    year_of_birth: int,
    year_of_event: int | None = None,
) -> AGB_ages:
    """
    Calculate the age group for an athlete given birth year.

    Parameters
    ----------
    year_of_birth : int
        The year that the athlete was born in
    year_of_event : int | None, default = None
        The year that the event is taking place in
        Defaults to the current year as per datetime.datetime.now()

    Returns
    -------
    age_group : AGB_ages
        The relevant age group from the AGB_ages enum

    References
    ----------
    Archery GB Rules of Shooting (2023)
    """
    ages_json = read_ages_json()

    if year_of_event is None:
        year_of_event = datetime.datetime.now().year

    age_this_year = year_of_event - year_of_birth

    # Extract appropriate age group.
    # Note some mypy ignores are required after filtering out `None` min/max ages

    # Order any age groups with a non-None min_age, sort oldest first
    over_ages = sorted(
        ((key, data) for key, data in ages_json.items() if data["min_age"] is not None),
        key=lambda data: data[1]["min_age"],  # type: ignore[arg-type, return-value]
        reverse=True,
    )

    # Order any age groups with a non-None max_age, sort youngest first
    under_ages = sorted(
        ((key, data) for key, data in ages_json.items() if data["max_age"] is not None),
        key=lambda data: data[1]["max_age"],  # type: ignore[arg-type, return-value]
    )

    # Filter out the maximum upper age group to which archer can belong
    for age_key, age_data in over_ages:
        if age_this_year >= age_data["min_age"]:  # type: ignore[operator]
            return AGB_ages[age_key]

    # Filter out the minimum lower age group to which archer can belong
    for age_key, age_data in under_ages:
        if age_this_year <= age_data["max_age"]:  # type: ignore[operator]
            return AGB_ages[age_key]

    # If no min or max age is hit, assume adult
    return AGB_ages.AGE_ADULT
