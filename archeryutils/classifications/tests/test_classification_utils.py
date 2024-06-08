"""Tests for classification utilities."""

import pytest

import archeryutils.classifications.classification_utils as class_utils


class TestStringUtils:
    """Tests for the string formatting utils of classifications code."""

    @pytest.mark.parametrize(
        "bowstyle,age_group,gender,groupname_expected",
        # Check all systems, different distances, negative and large handicaps.
        [
            ("barebow", "adult", "male", "adult_male_barebow"),
            ("Barebow", "Adult", "Male", "adult_male_barebow"),
            ("Barebow", "Under 18", "Male", "under18_male_barebow"),
            ("RECURVE", "UnDeR 18", "femaLe", "under18_female_recurve"),
        ],
    )
    def test_get_groupname(
        self,
        age_group: str,
        gender: str,
        bowstyle: str,
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
        # Check all systems, different distances, negative and large handicaps.
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
