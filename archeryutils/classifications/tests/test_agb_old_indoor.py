"""Tests for old agb indoor classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds

ALL_INDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_indoor.json",
        "AGB_indoor.json",
    ],
)


class TestAgbOldIndoorClassificationScores:
    """Tests for the old_indoor classification scores function."""

    @pytest.mark.parametrize(
        "age_group,scores_expected",
        [
            (
                "adult",
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                "50+",
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                "under21",
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                "Under 18",
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                "Under 12",
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
        ],
    )
    def test_agb_old_indoor_classification_scores_ages(
        self,
        age_group: str,
        scores_expected: list[int],
    ) -> None:
        """
        Check that old_indoor classification returns expected value for a case.

        ALl ages should return the same values.
        """
        scores = class_funcs.agb_old_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle="recurve",
            gender="male",
            age_group=age_group,
        )

        assert scores == scores_expected

    def test_agb_old_indoor_classification_scores_genders(
        self,
    ) -> None:
        """Check that old_indoor classification returns expected value for a case."""
        scores = class_funcs.agb_old_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle="recurve",
            gender="female",
            age_group="adult",
        )

        assert scores == [582, 569, 534, 479, 380, 255, 139, 93]

    @pytest.mark.parametrize(
        "bowstyle,gender,scores_expected",
        [
            (
                "compound",
                "male",
                [581, 570, 554, 529, 484, 396, 279, 206],
            ),
            (
                "compound",
                "female",
                [570, 562, 544, 509, 449, 347, 206, 160],
            ),
        ],
    )
    def test_agb_old_indoor_classification_scores_bowstyles(
        self,
        bowstyle: str,
        gender: str,
        scores_expected: list[int],
    ) -> None:
        """
        Check that old_indoor classification returns expected value for a case.

        Also checks that compound scoring is enforced.
        """
        scores = class_funcs.agb_old_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle=bowstyle,
            gender=gender,
            age_group="adult",
        )

        assert scores == scores_expected

    def test_agb_old_indoor_classification_scores_gent_compound_worcester(
        self,
    ) -> None:
        """Check gent compound worcester supposed loophole."""
        scores = class_funcs.agb_old_indoor_classification_scores(
            roundname="worcester",
            bowstyle="compound",
            gender="male",
            age_group="adult",
        )

        assert scores == [300, 299, 289, 264, 226, 162, 96, 65]

    @pytest.mark.parametrize(
        "bowstyle,gender,age_group",
        # Check all systems, different distances, negative and large handicaps.
        [
            # No invalid bowstyle as anything non-compound returns non-compound.
            # No invalid age as only one table for all ages.
            (
                "recurve",
                "invalidgender",
                "adult",
            ),
        ],
    )
    def test_agb_old_indoor_classification_scores_invalid(
        self,
        bowstyle: str,
        gender: str,
        age_group: str,
    ) -> None:
        """Check that old_indoor classification returns expected value for a case."""
        with pytest.raises(
            KeyError,
            match=(
                f"{age_group.lower().replace(' ', '')}_"
                f"{gender.lower()}_{bowstyle.lower()}"
            ),
        ):
            _ = class_funcs.agb_old_indoor_classification_scores(
                roundname="portsmouth",
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )


class TestCalculateAgbOldIndoorClassification:
    """Tests for the old_indoor classification function."""

    @pytest.mark.parametrize(
        "score,gender,class_expected",
        [
            (
                400,
                "male",
                "F",
            ),
            (
                337,
                "female",
                "F",
            ),
            (
                592,
                "male",
                "A",
            ),
            (
                582,
                "female",
                "A",
            ),
            (
                581,
                "male",
                "C",
            ),
            (
                120,
                "male",
                "UC",
            ),
            (
                1,
                "male",
                "UC",
            ),
        ],
    )
    def test_calculate_agb_old_indoor_classification(
        self,
        score: float,
        gender: str,
        class_expected: str,
    ) -> None:
        """Check old_indoor classification returns expected value for a few cases."""
        class_returned = class_funcs.calculate_agb_old_indoor_classification(
            score=score,
            roundname="portsmouth",
            bowstyle="recurve",
            gender=gender,
            age_group="adult",
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "roundname,score",
        [
            (
                "portsmouth",
                1000,
            ),
            (
                "portsmouth",
                601,
            ),
            (
                "portsmouth",
                -1,
            ),
            (
                "portsmouth",
                -100,
            ),
        ],
    )
    def test_calculate_agb_old_indoor_classification_invalid_scores(
        self,
        roundname: str,
        score: float,
    ) -> None:
        """Check that old_indoor classification fails for inappropriate scores."""
        with pytest.raises(
            ValueError,
            match=(
                f"Invalid score of {score} for a {roundname}. "
                f"Should be in range 0-{ALL_INDOOR_ROUNDS[roundname].max_score()}."
            ),
        ):
            _ = class_funcs.calculate_agb_old_indoor_classification(
                score=score,
                roundname=roundname,
                bowstyle="barebow",
                gender="male",
                age_group="adult",
            )
