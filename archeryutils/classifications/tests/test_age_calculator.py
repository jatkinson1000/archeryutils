"""Tests for age_calculator functions."""

import datetime

import pytest

from archeryutils.classifications.AGB_data import AGB_ages
from archeryutils.classifications.age_calculator import calculate_age_group


class TestAgeCalculator:
    """Tests for the age_calculator functions."""

    def test_adult(self) -> None:
        """Check adults are marked as such."""
        year_of_birth = 1989
        year_of_event = 2025

        assert calculate_age_group(year_of_birth, year_of_event) == AGB_ages.AGE_ADULT

    def test_adult_default_date(self) -> None:
        """Check adults are marked as such for default year_of_event."""
        assert (
            calculate_age_group(datetime.datetime.now().year - 21) == AGB_ages.AGE_ADULT
        )
        assert (
            calculate_age_group(datetime.datetime.now().year - 49) == AGB_ages.AGE_ADULT
        )

    def test_juniors(self) -> None:
        """Explicitly check all junior age groups for 2025."""
        assert calculate_age_group(2014, 2025) == AGB_ages.AGE_UNDER_12
        assert calculate_age_group(2013, 2025) == AGB_ages.AGE_UNDER_14
        assert calculate_age_group(2012, 2025) == AGB_ages.AGE_UNDER_14
        assert calculate_age_group(2011, 2025) == AGB_ages.AGE_UNDER_15
        assert calculate_age_group(2010, 2025) == AGB_ages.AGE_UNDER_16
        assert calculate_age_group(2009, 2025) == AGB_ages.AGE_UNDER_18
        assert calculate_age_group(2008, 2025) == AGB_ages.AGE_UNDER_18
        assert calculate_age_group(2007, 2025) == AGB_ages.AGE_UNDER_21
        assert calculate_age_group(2006, 2025) == AGB_ages.AGE_UNDER_21
        assert calculate_age_group(2005, 2025) == AGB_ages.AGE_UNDER_21
        assert calculate_age_group(2004, 2025) == AGB_ages.AGE_ADULT

    def test_juniors_default_date(self) -> None:
        """Check missing year_of_event."""
        # If born today, then will be Under 12.
        assert (
            calculate_age_group(datetime.datetime.now().year) == AGB_ages.AGE_UNDER_12
        )
        assert (
            calculate_age_group(datetime.datetime.now().year - 17)
            == AGB_ages.AGE_UNDER_18
        )
        assert (
            calculate_age_group(datetime.datetime.now().year - 18)
            == AGB_ages.AGE_UNDER_21
        )

    def test_masters(self) -> None:
        """Explicitly check around the 50+ group for 2025."""
        assert calculate_age_group(1976, 2025) == AGB_ages.AGE_ADULT
        assert calculate_age_group(1975, 2025) == AGB_ages.AGE_50_PLUS
        assert calculate_age_group(1950, 2025) == AGB_ages.AGE_50_PLUS

    def test_masters_default_date(self) -> None:
        """Check around the 50+ group for default year_of_event."""
        assert (
            calculate_age_group(datetime.datetime.now().year - 49) == AGB_ages.AGE_ADULT
        )
        assert (
            calculate_age_group(datetime.datetime.now().year - 50)
            == AGB_ages.AGE_50_PLUS
        )
        assert (
            calculate_age_group(datetime.datetime.now().year - 75)
            == AGB_ages.AGE_50_PLUS
        )
