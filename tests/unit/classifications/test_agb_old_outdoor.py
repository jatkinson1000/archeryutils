"""Tests for old agb outdoor classification functions."""

import re

import pytest

import archeryutils.classifications as cf
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders
from archeryutils.rounds import Pass, Round

ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ],
)


class TestAgbOldOutdoorClassificationScores:
    """Tests for the old_outdoor classification scores function."""

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,age_group,scores_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [1259, 1190, 1065, 885, 716, 481],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.RECURVE,
                AGB_genders.FEMALE,
                AGB_ages.AGE_ADULT,
                [1242, 1169, 1037, 817, 602, 364],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.COMPOUND,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [1352, 1311, 1248, 1134, 1026, 774],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.COMPOUND,
                AGB_genders.FEMALE,
                AGB_ages.AGE_ADULT,
                [1342, 1298, 1220, 1092, 845, 634],
            ),
        ],
    )
    def test_agb_old_outdoor_classification_scores(
        self,
        archery_round: Round | str,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """
        Check that old_outdoor classification returns expected value for a case.

        Checking across age groups, genders and bowstyles.
        """
        scores = cf.agb_old_outdoor_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age_group,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "archery_round,scores_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["york"],
                [1146, 1065, 913, 698, 511, 283],
            ),
            (
                ALL_OUTDOOR_ROUNDS["hereford"],
                [-9999, -9999, -9999, 884, 723, 477],
            ),
            (
                ALL_OUTDOOR_ROUNDS["bristol_ii"],
                [-9999, -9999, -9999, -9999, 911, 695],
            ),
            (
                ALL_OUTDOOR_ROUNDS["bristol_iii"],
                [-9999, -9999, -9999, -9999, -9999, 860],
            ),
        ],
    )
    def test_agb_old_outdoor_classification_distance_limits(
        self,
        archery_round: Round | str,
        scores_expected: list[int],
    ) -> None:
        """
        Check that old_outdoor classification returns expected value for a case.

        Checking across age groups, genders and bowstyles.
        """
        scores = cf.agb_old_outdoor_classification_scores(
            archery_round=archery_round,
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,age_group,msg",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                "invalidbowstyle",
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                (
                    "invalidbowstyle is not a recognised bowstyle for old outdoor "
                    "classifications. Please select from "
                    "`AGB_bowstyles.COMPOUND|RECURVE|BAREBOW|LONGBOW`."
                ),
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.RECURVE,
                "invalidgender",
                AGB_ages.AGE_ADULT,
                (
                    "invalidgender is not a recognised gender group for old outdoor "
                    "classifications. Please select from `archeryutils.AGB_genders`."
                ),
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                "invalidage",
                (
                    "invalidage is not a recognised age group for old outdoor "
                    "classifications. Please select from "
                    "`AGB_ages.AGE_ADULT|AGE_UNDER_18|AGE_UNDER_16|AGE_UNDER_14|AGE_UNDER_12`."
                ),
            ),
        ],
    )
    def test_agb_old_outdoor_classification_scores_invalid(
        self,
        archery_round: Round | str,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        age_group: AGB_ages,
        msg: str,
    ) -> None:
        """Check that old outdoor classification raises errors for invalid categories."""
        with pytest.raises(
            ValueError,
            match=msg,
        ):
            _ = cf.agb_old_outdoor_classification_scores(
                archery_round=archery_round,
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )

    def test_agb_old_outdoor_classification_scores_invalid_round(
        self,
    ) -> None:
        """Check that old outdoor classification raises error for invalid round."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    "This round is not recognised for the purposes of "
                    "outdoor classification.\n"
                    "Please select an appropriate option using "
                    "`archeryutils.load_rounds`."
                )
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = cf.agb_old_outdoor_classification_scores(
                archery_round=my_round,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_old_outdoor_classification_scores_invalid_string_round(
        self,
    ) -> None:
        """Check that outdoor classification raises error for invalid string round."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    "This round is not recognised for the purposes of "
                    "outdoor classification.\n"
                    "Please select an appropriate option using "
                    "`archeryutils.load_rounds`."
                )
            ),
        ):
            _ = cf.agb_old_outdoor_classification_scores(
                archery_round="invalid_roundname",
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_old_outdoor_classification_scores_string_round(
        self,
    ) -> None:
        """Check that outdoor classification can process a string roundname."""
        scores = cf.agb_old_outdoor_classification_scores(
            archery_round="wa1440_90",
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == [1352, 1311, 1248, 1134, 1026, 774]


class TestCalculateAgbOldOutdoorClassification:
    """Tests for the old_outdoor classification function."""

    @pytest.mark.parametrize(
        "archery_round,score,age_group,bowstyle,class_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                1353,  # 1 above GMB
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "GMB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                1351,  # 1 below GMB - Senior
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "GMB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                900,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                "JMB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                600,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                "JB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                400,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                "1ST",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                300,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                "2ND",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                200,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                "3RD",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                1,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                "UC",
            ),
        ],
    )
    def test_calculate_agb_old_outdoor_classification(
        self,
        score: float,
        archery_round: Round | str,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check old outdoor classification returns expected value for a few cases."""
        class_returned = cf.calculate_agb_old_outdoor_classification(
            archery_round=archery_round,
            score=score,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )
        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "score",
        [1000, 901, -1, -100],
    )
    def test_calculate_agb_old_outdoor_classification_invalid_scores(
        self,
        score: float,
    ) -> None:
        """Check that old outdoor classification fails for inappropriate scores."""
        archery_round = ALL_OUTDOOR_ROUNDS["wa900"]
        with pytest.raises(
            ValueError,
            match=(
                f"Invalid score of {score} for a "
                f"{archery_round.name}. "
                f"Should be in range 0-{archery_round.max_score()}."
            ),
        ):
            _ = cf.calculate_agb_old_outdoor_classification(
                score=score,
                archery_round=archery_round,
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_old_outdoor_classification_invalid_round(
        self,
    ) -> None:
        """Check that old outdoor classification raises error for invalid round."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    "This round is not recognised for the purposes of "
                    "outdoor classification.\n"
                    "Please select an appropriate option using "
                    "`archeryutils.load_rounds`."
                )
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = cf.calculate_agb_old_outdoor_classification(
                archery_round=my_round,
                score=666,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_old_outdoor_classification_scores_invalid_string_round(
        self,
    ) -> None:
        """Check that old outdoor classification raises error for invalid string round."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    "This round is not recognised for the purposes of "
                    "outdoor classification.\n"
                    "Please select an appropriate option using "
                    "`archeryutils.load_rounds`."
                )
            ),
        ):
            _ = cf.calculate_agb_old_outdoor_classification(
                archery_round="invalid_roundname",
                score=666,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_outdoor_classification_scores_string_round(
        self,
    ) -> None:
        """Check that outdoor classification can process a string roundname."""
        my_class = cf.calculate_agb_old_outdoor_classification(
            archery_round="hereford",
            score=500,
            bowstyle=AGB_bowstyles.LONGBOW,
            gender=AGB_genders.FEMALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert my_class == "GMB"
