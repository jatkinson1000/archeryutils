"""Tests for AGB classification data."""

import pytest

from archeryutils.classifications import AGB_ages


class TestAges:
    """Tests for the age groups of classifications code."""

    @pytest.mark.parametrize(
        "deprecated_age_group,age_group",
        [
            ("AGE_50_PLUS", "OVER_50"),
            ("AGE_ADULT", "ADULT"),
            ("AGE_UNDER_21", "UNDER_21"),
            ("AGE_UNDER_18", "UNDER_18"),
            ("AGE_UNDER_16", "UNDER_16"),
            ("AGE_UNDER_15", "UNDER_15"),
            ("AGE_UNDER_14", "UNDER_14"),
            ("AGE_UNDER_12", "UNDER_12"),
        ],
    )
    def test_deprecation_warning(
        self,
        deprecated_age_group: str,
        age_group: str,
    ) -> None:
        """Check legacy age group raises a deprecation warning and defaults to new."""
        with pytest.warns(
            DeprecationWarning, match=rf"{deprecated_age_group}.*{age_group}"
        ):
            actual_AGB_age = getattr(AGB_ages, deprecated_age_group)

        assert actual_AGB_age.name == age_group
