"""Tests for classification utilities."""

import numpy as np
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
                AGB_genders.OPEN,
                "ADULT_OPEN_BAREBOW",
            ),
            (
                AGB_bowstyles.BAREBOW,
                AGB_ages.UNDER_18,
                AGB_genders.OPEN,
                "UNDER_18_OPEN_BAREBOW",
            ),
            (
                AGB_bowstyles.RECURVE,
                AGB_ages.UNDER_18,
                AGB_genders.FEMALE,
                "UNDER_18_FEMALE_RECURVE",
            ),
            # Check English Longbow becomes Longbow
            (
                AGB_bowstyles.ENGLISHLONGBOW,
                AGB_ages.ADULT,
                AGB_genders.FEMALE,
                "ADULT_FEMALE_LONGBOW",
            ),
            (
                # Check backwards compatibility of Male category
                AGB_bowstyles.BAREBOW,
                AGB_ages.ADULT,
                AGB_genders.MALE,
                "ADULT_OPEN_BAREBOW",
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


class TestScoreFixing:
    """Tests for the score fixing utilities."""

    @pytest.mark.parametrize(
        "scores,max_score,expected",
        [
            # Test case 1: No repeated scores
            (
                [100, 95, 90, 85, 80],
                100,
                [100, 95, 90, 85, 80],
            ),
            # Test case 2: Repeated scores in middle
            (
                [100, 95, 90, 90, 80],
                100,
                [100, 95, 91, 90, 80],
            ),
            # Test case 3: Multiple repeated scores
            (
                [100, 95, 90, 90, 90, 80],
                100,
                [100, 95, 92, 91, 90, 80],
            ),
            # Test case 4: Repeated max scores
            (
                [100, 100, 100, 95, 90],
                100,
                [-9999, -9999, 100, 95, 90],
            ),
            # Test case 5: All same scores
            (
                [80, 80, 80, 80],
                100,
                [83, 82, 81, 80],
            ),
            # Test case 6: Scores at max
            (
                [100, 100, 100],
                100,
                [-9999, -9999, 100],
            ),
            # Test case 7: Single score
            (
                [90],
                100,
                [90],
            ),
            # Test case 8: Two identical scores
            (
                [85, 85],
                100,
                [86, 85],
            ),
            # Test case 9: Real example that caught edge case in the code
            (
                [500, 499, 498, 497, 496, 425, 343, 259, 185],
                500,
                [500, 499, 498, 497, 496, 425, 343, 259, 185],
            ),
        ],
    )
    def test_fix_repeated_scores(
        self,
        scores: list[int],
        max_score: float,
        expected: list[int],
    ) -> None:
        """Test that fix_repeated_scores() correctly handles repeated scores."""
        result = class_utils.fix_repeated_scores(scores, max_score)

        assert result == expected
