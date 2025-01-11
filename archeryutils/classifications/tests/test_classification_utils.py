"""Tests for classification utilities."""

import pytest

import archeryutils.classifications.classification_utils as class_utils
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders


class TestStringUtils:
    """Tests for the string formatting utils of classifications code."""

    @pytest.mark.parametrize(
        "bowstyle,age_group,gender,groupname_expected",
        [
            (
                AGB_bowstyles.BAREBOW,
                AGB_ages.ADULT,
                AGB_genders.MALE,
                "ADULT_MALE_BAREBOW",
            ),
            (
                AGB_bowstyles.BAREBOW,
                AGB_ages.ADULT,
                AGB_genders.MALE,
                "ADULT_MALE_BAREBOW",
            ),
            (AGB_bowstyles.BAREBOW, AGB_ages.U18, AGB_genders.MALE, "U18_MALE_BAREBOW"),
            (
                AGB_bowstyles.RECURVE,
                AGB_ages.U18,
                AGB_genders.FEMALE,
                "U18_FEMALE_RECURVE",
            ),
            # Check English Longbow becomes Longbow
            (
                AGB_bowstyles.ENGLISHLONGBOW,
                AGB_ages.ADULT,
                AGB_genders.FEMALE,
                "ADULT_FEMALE_LONGBOW",
            ),
        ],
    )
    def test_get_groupname(
        self,
        bowstyle: AGB_bowstyles,
        age_group: AGB_ages,
        gender: AGB_genders,
        groupname_expected: str,
    ) -> None:
        """Check get_groupname(handicap=float) returns expected value for a case."""
        groupname = class_utils.get_groupname(
            bowstyle=bowstyle,
            gender=gender,
            age_group=age_group,
        )

        assert groupname == groupname_expected

    @pytest.mark.parametrize(
        "roundname,strippedname_expected",
        [
            ("portsmouth", "portsmouth"),
            ("portsmouth_triple", "portsmouth"),
            ("portsmouth_compound", "portsmouth_compound"),
            ("portsmouth_compound_triple", "portsmouth_compound"),
            ("portsmouth_triple_compound", "portsmouth_compound"),
            ("worcester_5_centre", "worcester"),
        ],
    )
    def test_strip_spots(
        self,
        roundname: str,
        strippedname_expected: str,
    ) -> None:
        """Check that strip_spots() returns expected value for a round."""
        strippedname = class_utils.strip_spots(roundname)

        assert strippedname == strippedname_expected
