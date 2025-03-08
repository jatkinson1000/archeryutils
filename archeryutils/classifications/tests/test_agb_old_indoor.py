"""Tests for old agb indoor classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders
from archeryutils.rounds import Pass, Round

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
            archery_round=ALL_INDOOR_ROUNDS["portsmouth"],
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "age_group,bowstyle,scores_expected",
        [
            (
                AGB_ages.AGE_50_PLUS,
                AGB_bowstyles.RECURVE,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                AGB_ages.AGE_UNDER_21,
                AGB_bowstyles.RECURVE,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.RECURVE,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.BAREBOW,
                [592, 582, 554, 505, 432, 315, 195, 139],
            ),
            (
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUNDLIMITED,
                [581, 570, 554, 529, 484, 396, 279, 206],
            ),
        ],
    )
    def test_agb_old_indoor_classification_scores_coaxed(
        self,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        scores_expected: list[int],
    ) -> None:
        """Check old indoor classification returns expected value for a coaxed case."""
        coaxed_vals = class_funcs.coax_old_indoor_group(
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )
        scores = class_funcs.agb_old_indoor_classification_scores(
            archery_round=ALL_INDOOR_ROUNDS["portsmouth"],
            **coaxed_vals,
        )

        assert scores == scores_expected

    def test_agb_old_indoor_classification_scores_genders(
        self,
    ) -> None:
        """Check that old_indoor classification returns expected value for a case."""
        scores = class_funcs.agb_old_indoor_classification_scores(
            archery_round=ALL_INDOOR_ROUNDS["portsmouth"],
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
            archery_round=ALL_INDOOR_ROUNDS["portsmouth"],
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
            archery_round=ALL_INDOOR_ROUNDS["worcester"],
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == [300, 299, 289, 264, 226, 162, 96, 65]

    @pytest.mark.parametrize(
        "bowstyle,gender,age_group,msg",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                AGB_bowstyles.RECURVE,
                "invalidgender",
                AGB_ages.AGE_ADULT,
                (
                    "invalidgender is not a recognised gender group for old indoor "
                    "classifications. Please select from `archeryutils.AGB_genders`."
                ),
            ),
            (
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                (
                    "AGB_bowstyles.BAREBOW is not a recognised bowstyle for old indoor "
                    "classifications. "
                    "Please select from `AGB_bowstyles.COMPOUND|RECURVE`."
                ),
            ),
            (
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_UNDER_12,
                (
                    "AGB_ages.AGE_UNDER_12 is not a recognised age group for "
                    "old indoor classifications. "
                    "Please select from `AGB_ages.AGE_ADULT`."
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
                archery_round=ALL_INDOOR_ROUNDS["portsmouth"],
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )

    def test_agb_old_indoor_classification_scores_invalid_round(
        self,
    ) -> None:
        """Check that indoor classification raises error for invalid round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of "
                "indoor classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = class_funcs.agb_old_indoor_classification_scores(
                archery_round=my_round,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_old_indoor_classification_scores_invalid_string_round(
        self,
    ) -> None:
        """Check that indoor classification raises error for invalid string round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of "
                "indoor classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            _ = class_funcs.agb_old_indoor_classification_scores(
                archery_round="invalid_roundname",
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_old_indoor_classification_scores_string_round(
        self,
    ) -> None:
        """Check that indoor classification can process a string roundname."""
        scores = class_funcs.agb_old_indoor_classification_scores(
            archery_round="portsmouth",
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == [581, 570, 554, 529, 484, 396, 279, 206]


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
            archery_round=ALL_INDOOR_ROUNDS["portsmouth"],
            bowstyle=AGB_bowstyles.RECURVE,
            gender=gender,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "score",
        [1000, 601, -1, -100],
    )
    def test_calculate_agb_old_indoor_classification_invalid_scores(
        self,
        score: float,
    ) -> None:
        """Check that old_indoor classification fails for inappropriate scores."""
        with pytest.raises(
            ValueError,
            match=(
                f"Invalid score of {score} for a "
                f"{ALL_INDOOR_ROUNDS['portsmouth'].name}. "
                f"Should be in range 0-{ALL_INDOOR_ROUNDS['portsmouth'].max_score()}."
            ),
        ):
            _ = class_funcs.calculate_agb_old_indoor_classification(
                score=score,
                archery_round=ALL_INDOOR_ROUNDS["portsmouth"],
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_indoor_classification_invalid_round(
        self,
    ) -> None:
        """Check that indoor classification raises error for invalid round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of "
                "indoor classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = class_funcs.calculate_agb_old_indoor_classification(
                archery_round=my_round,
                score=666,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_indoor_classification_scores_invalid_string_round(
        self,
    ) -> None:
        """Check that indoor classification raises error for invalid string round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of "
                "indoor classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            _ = class_funcs.calculate_agb_old_indoor_classification(
                archery_round="invalid_roundname",
                score=666,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_indoor_classification_scores_string_round(
        self,
    ) -> None:
        """Check that indoor classification can process a string roundname."""
        my_class = class_funcs.calculate_agb_old_indoor_classification(
            archery_round="portsmouth",
            score=578,
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert my_class == "B"
