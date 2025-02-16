"""Tests for old agb indoor classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

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
                AGB_ages.AGE_ADULT,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
        ],
    )
    def test_agb_old_indoor_classification_scores_ages(
        self,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """
        Check that old_indoor classification returns expected value for a case.

        ALl ages should return the same values.
        """
        scores = class_funcs.agb_old_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "age_group,scores_expected",
        [
            (
                AGB_ages.AGE_50_PLUS,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                AGB_ages.AGE_UNDER_21,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                AGB_ages.AGE_UNDER_18,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                AGB_ages.AGE_UNDER_12,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
        ],
    )
    def test_agb_old_indoor_classification_scores_coaxed_ages(
        self,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a coaxed case."""
        coaxed_vals = class_funcs.coax_old_indoor_group(
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )
        scores = class_funcs.agb_old_indoor_classification_scores(
            roundname="portsmouth",
            **coaxed_vals,
        )

        assert scores == scores_expected

    def test_agb_old_indoor_classification_scores_genders(
        self,
    ) -> None:
        """Check that old_indoor classification returns expected value for a case."""
        scores = class_funcs.agb_old_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.FEMALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == [582, 569, 534, 479, 380, 255, 139, 93]

    @pytest.mark.parametrize(
        "bowstyle,gender,scores_expected",
        [
            (
                AGB_bowstyles.COMPOUND,
                AGB_genders.MALE,
                [581, 570, 554, 529, 484, 396, 279, 206],
            ),
            (
                AGB_bowstyles.COMPOUND,
                AGB_genders.FEMALE,
                [570, 562, 544, 509, 449, 347, 206, 160],
            ),
        ],
    )
    def test_agb_old_indoor_classification_scores_bowstyles(
        self,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
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
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == scores_expected

    def test_agb_old_indoor_classification_scores_gent_compound_worcester(
        self,
    ) -> None:
        """Check gent compound worcester supposed loophole."""
        scores = class_funcs.agb_old_indoor_classification_scores(
            roundname="worcester",
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == [300, 299, 289, 264, 226, 162, 96, 65]

    @pytest.mark.parametrize(
        "bowstyle,gender,age_group,msg",
        # Check all systems, different distances, negative and large handicaps.
        [
            # No invalid bowstyle as anything non-compound returns non-compound.
            # No invalid age as only one table for all ages.
            (
                AGB_bowstyles.RECURVE,
                "invalidgender",
                AGB_ages.AGE_ADULT,
                (
                    "invalidgender is not a recognised gender group for old indoor "
                    "classifications. Please select from `archeryutils.AGB_genders`."
                ),
            ),
        ],
    )
    def test_agb_old_indoor_classification_scores_invalid(
        self,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        age_group: AGB_ages,
        msg: str,
    ) -> None:
        """Check that old_indoor classification returns expected value for a case."""
        with pytest.raises(
            ValueError,
            match=msg,
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
                AGB_genders.MALE,
                "F",
            ),
            (
                337,
                AGB_genders.FEMALE,
                "F",
            ),
            (
                592,
                AGB_genders.MALE,
                "A",
            ),
            (
                582,
                AGB_genders.FEMALE,
                "A",
            ),
            (
                581,
                AGB_genders.MALE,
                "C",
            ),
            (
                120,
                AGB_genders.MALE,
                "UC",
            ),
            (
                1,
                AGB_genders.MALE,
                "UC",
            ),
        ],
    )
    def test_calculate_agb_old_indoor_classification(
        self,
        score: float,
        gender: AGB_genders,
        class_expected: str,
    ) -> None:
        """Check old_indoor classification returns expected value for a few cases."""
        class_returned = class_funcs.calculate_agb_old_indoor_classification(
            score=score,
            roundname="portsmouth",
            bowstyle=AGB_bowstyles.RECURVE,
            gender=gender,
            age_group=AGB_ages.AGE_ADULT,
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
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
            )
