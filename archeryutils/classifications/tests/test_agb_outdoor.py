"""Tests for agb outdoor classification functions."""

import re

import pytest

import archeryutils.classifications as class_funcs
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


class TestAgbOutdoorClassificationScores:
    """
    Tests for the agb outdoor classification scores function.

    This will implicitly check the dictionary creation.
    Provided sufficient options are covered across bowstyles, genders, and ages.
    """

    @pytest.mark.parametrize(
        "archery_round,age_group,scores_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_ages.AGE_ADULT,
                [426, 566, 717, 866, 999, 1110, 1197, 1266, 1320],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_ages.AGE_50_PLUS,
                [364, 503, 659, 817, 960, 1079, 1173, 1247, 1305],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_ages.AGE_UNDER_21,
                [313, 435, 577, 728, 877, 1008, 1117, 1203, 1270],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_ages.AGE_UNDER_18,
                [259, 373, 514, 671, 828, 969, 1086, 1179, 1252],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_60"],
                AGB_ages.AGE_UNDER_16,
                [227, 335, 474, 635, 799, 946, 1068, 1165, 1241],
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                AGB_ages.AGE_UNDER_15,
                [270, 389, 534, 693, 849, 988, 1101, 1191, 1261],
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iv"],
                AGB_ages.AGE_UNDER_14,
                [396, 524, 666, 814, 952, 1070, 1166, 1242, 1301],
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_v"],
                AGB_ages.AGE_UNDER_12,
                [406, 550, 706, 858, 992, 1104, 1193, 1263, 1317],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_ages(
        self,
        archery_round: Round | str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that  classification returns expected value for a case."""
        scores = class_funcs.agb_outdoor_classification_scores(
            archery_round=archery_round,
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "archery_round,age_group,scores_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_ages.AGE_ADULT,
                [392, 536, 693, 849, 988, 1101, 1191, 1261, 1316],
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                AGB_ages.AGE_UNDER_16,
                [293, 418, 567, 727, 881, 1014, 1122, 1207, 1274],
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_iii"],
                AGB_ages.AGE_UNDER_15,
                [270, 389, 534, 693, 849, 988, 1101, 1191, 1261],
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_v"],
                AGB_ages.AGE_UNDER_12,
                [406, 550, 706, 858, 992, 1104, 1193, 1263, 1317],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_genders(
        self,
        archery_round: Round | str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """
        Check that outdoor classification returns expected value for a case.

        Male equivalents already checked above.
        Also checks that compound rounds are being enforced.
        """
        scores = class_funcs.agb_outdoor_classification_scores(
            archery_round=archery_round,
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.FEMALE,
            age_group=age_group,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,scores_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.COMPOUND,
                AGB_genders.MALE,
                [866, 982, 1081, 1162, 1229, 1283, 1327, 1362, 1389],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.COMPOUND,
                AGB_genders.FEMALE,
                [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                [290, 380, 484, 598, 717, 835, 945, 1042, 1124],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.FEMALE,
                [252, 338, 441, 558, 682, 806, 921, 1023, 1108],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.LONGBOW,
                AGB_genders.MALE,
                [85, 124, 177, 248, 337, 445, 566, 696, 825],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.LONGBOW,
                AGB_genders.FEMALE,
                [64, 94, 136, 195, 274, 373, 493, 625, 761],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.ENGLISHLONGBOW,
                AGB_genders.FEMALE,
                [64, 94, 136, 195, 274, 373, 493, 625, 761],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_bowstyles(
        self,
        archery_round: Round | str,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        scores_expected: list[int],
    ) -> None:
        """Check that outdoor classification returns expected value for a case."""
        scores = class_funcs.agb_outdoor_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,scores_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.FLATBOW,
                AGB_genders.MALE,
                [290, 380, 484, 598, 717, 835, 945, 1042, 1124],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.TRADITIONAL,
                AGB_genders.FEMALE,
                [252, 338, 441, 558, 682, 806, 921, 1023, 1108],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.COMPOUNDBAREBOW,
                AGB_genders.FEMALE,
                [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392],
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.COMPOUNDLIMITED,
                AGB_genders.FEMALE,
                [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392],
            ),
            # Check coaxing and a valid bowstyle
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                AGB_bowstyles.COMPOUND,
                AGB_genders.FEMALE,
                [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_nonbowstyles(
        self,
        archery_round: Round | str,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        scores_expected: list[int],
    ) -> None:
        """Check that appropriate scores returned for valid non-outdoor bowstyles."""
        coaxed_vals = class_funcs.coax_outdoor_group(
            bowstyle=bowstyle,
            gender=gender,
            age_group=AGB_ages.AGE_ADULT,
        )
        scores = class_funcs.agb_outdoor_classification_scores(
            archery_round=archery_round,
            **coaxed_vals,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "archery_round,scores_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90_small"],
                [866, 982, 1081, 1162, 1229, 1283, 1327, 1362, 1389],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_small_faces(
        self,
        archery_round: Round | str,
        scores_expected: list[int],
    ) -> None:
        """Check that outdoor classification returns single face scores only."""
        scores = class_funcs.agb_outdoor_classification_scores(
            archery_round=archery_round,
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,age_group,msg",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                "invalidbowstyle",
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                (
                    "invalidbowstyle is not a recognised bowstyle for outdoor "
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
                    "invalidgender is not a recognised gender group for outdoor "
                    "classifications. Please select from `archeryutils.AGB_genders`."
                ),
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                "invalidage",
                (
                    "invalidage is not a recognised age group for outdoor "
                    "classifications. Please select from `archeryutils.AGB_ages`."
                ),
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_invalid(
        self,
        archery_round: Round | str,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        age_group: AGB_ages,
        msg: str,
    ) -> None:
        """Check that outdoor classification returns expected value for a case."""
        with pytest.raises(
            ValueError,
            match=msg,
        ):
            _ = class_funcs.agb_outdoor_classification_scores(
                archery_round=archery_round,
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )

    def test_agb_outdoor_classification_scores_invalid_round(
        self,
    ) -> None:
        """Check that outdoor classification raises error for invalid round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of "
                "outdoor classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = class_funcs.agb_outdoor_classification_scores(
                archery_round=my_round,
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_outdoor_classification_scores_invalid_string_round(
        self,
    ) -> None:
        """Check that outdoor classification raises error for invalid string round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of "
                "outdoor classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            _ = class_funcs.agb_outdoor_classification_scores(
                archery_round="invalid_roundname",
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_outdoor_classification_scores_string_round(
        self,
    ) -> None:
        """Check that outdoor classification can process a string roundname."""
        scores = class_funcs.agb_outdoor_classification_scores(
            archery_round="wa1440_70",
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.FEMALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392][::-1]


class TestCalculateAgbOutdoorClassification:
    """Tests for the outdoor classification function."""

    @pytest.mark.parametrize(
        "archery_round,score,age_group,bowstyle,class_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                1390,  # 1 above EMB
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "EMB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                1382,  # 1 below EMB
                AGB_ages.AGE_50_PLUS,
                AGB_bowstyles.COMPOUND,
                "GMB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_90"],
                900,  # midway MB
                AGB_ages.AGE_UNDER_21,
                AGB_bowstyles.BAREBOW,
                "MB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                1269,  # 1 below MB
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.COMPOUND,
                "B1",
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa1440_70"],
                969,  # boundary value
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.RECURVE,
                "B1",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_v"],
                992,  # Boundary
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                "B2",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_v"],
                222,  # Midway
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "A1",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_v"],
                91,  # On boundary
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "UC",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_v"],
                1,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "UC",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_v"],
                250,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "A1",
            ),
        ],
    )
    def test_calculate_agb_outdoor_classification(
        self,
        score: float,
        archery_round: Round | str,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that outdoor classification returns expected value for a few cases."""
        class_returned = class_funcs.calculate_agb_outdoor_classification(
            archery_round=archery_round,
            score=score,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "archery_round,score,age_group,bowstyle,class_expected",
        [
            (
                ALL_OUTDOOR_ROUNDS["wa720_70"],  # Not prestige only 70m => B2
                720,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "B2",
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa720_50_b"],  # Not prestige only 50m => A1
                720,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "A1",
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa720_50_c"],  # Prestige => EMB
                720,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "EMB",
            ),
            (
                ALL_OUTDOOR_ROUNDS[
                    "metric_80_30"
                ],  # This and next 2 check Prestige by age
                720,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "A3",  # 30m for adults gets A3
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_80_30"],
                720,
                AGB_ages.AGE_UNDER_14,
                AGB_bowstyles.COMPOUND,
                "B3",  # Max dist reqd. for B1 and B2
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_80_30"],
                720,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.COMPOUND,
                "EMB",  # Age appropriate
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_122_50"],
                720,
                AGB_ages.AGE_UNDER_16,
                AGB_bowstyles.COMPOUND,
                "B2",  # Under 16+ Max dist reqd. for B1 (not B2)
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa720_60"],  # Recurve 50+ get 60m 720
                720,
                AGB_ages.AGE_50_PLUS,
                AGB_bowstyles.RECURVE,
                "EMB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["wa720_60"],  # Recurve U18 get 60m 720
                720,
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.RECURVE,
                "EMB",
            ),
            (
                ALL_OUTDOOR_ROUNDS["metric_122_50"],  # Recurve U18 get 50m Metric 122
                720,
                AGB_ages.AGE_UNDER_16,
                AGB_bowstyles.RECURVE,
                "EMB",
            ),
        ],
    )
    def test_calculate_agb_outdoor_classification_prestige_dist(
        self,
        score: float,
        archery_round: Round | str,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that prestige and distanec limitations are working for a few cases."""
        class_returned = class_funcs.calculate_agb_outdoor_classification(
            archery_round=archery_round,
            score=score,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert class_returned == class_expected

    def test_calculate_agb_outdoor_classification_invalid_round(
        self,
    ) -> None:
        """Check outdoor classification returns unclassified for inappropriate round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of outdoor "
                "classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            _ = class_funcs.calculate_agb_outdoor_classification(
                archery_round="invalid_roundname",
                score=400,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    @pytest.mark.parametrize("score", [3000, 1441, -1, -100])
    def test_calculate_agb_outdoor_classification_invalid_scores(
        self,
        score: float,
    ) -> None:
        """Check that outdoor classification fails for inappropriate scores."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    f"Invalid score of {score} for a "
                    f"{ALL_OUTDOOR_ROUNDS['wa1440_90'].name}. "
                    f"Should be in range "
                    f"0-{ALL_OUTDOOR_ROUNDS['wa1440_90'].max_score()}."
                )
            ),
        ):
            _ = class_funcs.calculate_agb_outdoor_classification(
                score=score,
                archery_round=ALL_OUTDOOR_ROUNDS["wa1440_90"],
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_outdoor_classification_invalid_round(
        self,
    ) -> None:
        """Check that outdoor classification raises error for invalid round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of "
                "outdoor classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = class_funcs.calculate_agb_outdoor_classification(
                archery_round=my_round,
                score=666,
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_outdoor_classification_invalid_string_round(
        self,
    ) -> None:
        """Check that outdoor classification raises error for invalid string round."""
        with pytest.raises(
            ValueError,
            match=(
                "This round is not recognised for the purposes of "
                "outdoor classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            _ = class_funcs.calculate_agb_outdoor_classification(
                archery_round="invalid_roundname",
                score=666,
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_outdoor_classification_string_round(
        self,
    ) -> None:
        """Check that outdoor classification can process a string roundname."""
        my_class = class_funcs.calculate_agb_outdoor_classification(
            archery_round="wa1440_70",
            score=1200,
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.FEMALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert my_class == "B3"
