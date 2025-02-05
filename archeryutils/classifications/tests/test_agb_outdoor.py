"""Tests for agb outdoor classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

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
        "roundname,age_group,scores_expected",
        [
            (
                "wa1440_90",
                AGB_ages.AGE_ADULT,
                [426, 566, 717, 866, 999, 1110, 1197, 1266, 1320],
            ),
            (
                "wa1440_70",
                AGB_ages.AGE_50_PLUS,
                [364, 503, 659, 817, 960, 1079, 1173, 1247, 1305],
            ),
            (
                "wa1440_90",
                AGB_ages.AGE_UNDER_21,
                [313, 435, 577, 728, 877, 1008, 1117, 1203, 1270],
            ),
            (
                "wa1440_70",
                AGB_ages.AGE_UNDER_18,
                [259, 373, 514, 671, 828, 969, 1086, 1179, 1252],
            ),
            (
                "wa1440_60",
                AGB_ages.AGE_UNDER_16,
                [227, 335, 474, 635, 799, 946, 1068, 1165, 1241],
            ),
            (
                "metric_iii",
                AGB_ages.AGE_UNDER_15,
                [270, 389, 534, 693, 849, 988, 1101, 1191, 1261],
            ),
            (
                "metric_iv",
                AGB_ages.AGE_UNDER_14,
                [396, 524, 666, 814, 952, 1070, 1166, 1242, 1301],
            ),
            (
                "metric_v",
                AGB_ages.AGE_UNDER_12,
                [406, 550, 706, 858, 992, 1104, 1193, 1263, 1317],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_ages(
        self,
        roundname: str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that  classification returns expected value for a case."""
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "roundname,age_group,scores_expected",
        [
            (
                "wa1440_70",
                AGB_ages.AGE_ADULT,
                [392, 536, 693, 849, 988, 1101, 1191, 1261, 1316],
            ),
            (
                "metric_iii",
                AGB_ages.AGE_UNDER_16,
                [293, 418, 567, 727, 881, 1014, 1122, 1207, 1274],
            ),
            (
                "metric_iii",
                AGB_ages.AGE_UNDER_15,
                [270, 389, 534, 693, 849, 988, 1101, 1191, 1261],
            ),
            (
                "metric_v",
                AGB_ages.AGE_UNDER_12,
                [406, 550, 706, 858, 992, 1104, 1193, 1263, 1317],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_genders(
        self,
        roundname: str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """
        Check that outdoor classification returns expected value for a case.

        Male equivalents already checked above.
        Also checks that compound rounds are being enforced.
        """
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle=AGB_bowstyles.RECURVE,
            gender=AGB_genders.FEMALE,
            age_group=age_group,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,scores_expected",
        [
            (
                "wa1440_90",
                AGB_bowstyles.COMPOUND,
                AGB_genders.MALE,
                [866, 982, 1081, 1162, 1229, 1283, 1327, 1362, 1389],
            ),
            (
                "wa1440_70",
                AGB_bowstyles.COMPOUND,
                AGB_genders.FEMALE,
                [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392],
            ),
            (
                "wa1440_90",
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                [290, 380, 484, 598, 717, 835, 945, 1042, 1124],
            ),
            (
                "wa1440_70",
                AGB_bowstyles.BAREBOW,
                AGB_genders.FEMALE,
                [252, 338, 441, 558, 682, 806, 921, 1023, 1108],
            ),
            (
                "wa1440_90",
                AGB_bowstyles.LONGBOW,
                AGB_genders.MALE,
                [85, 124, 177, 248, 337, 445, 566, 696, 825],
            ),
            (
                "wa1440_70",
                AGB_bowstyles.LONGBOW,
                AGB_genders.FEMALE,
                [64, 94, 136, 195, 274, 373, 493, 625, 761],
            ),
            (
                "wa1440_70",
                AGB_bowstyles.ENGLISHLONGBOW,
                AGB_genders.FEMALE,
                [64, 94, 136, 195, 274, 373, 493, 625, 761],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_bowstyles(
        self,
        roundname: str,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        scores_expected: list[int],
    ) -> None:
        """Check that outdoor classification returns expected value for a case."""
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle=bowstyle,
            gender=gender,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,scores_expected",
        [
            (
                "wa1440_90",
                AGB_bowstyles.FLATBOW,
                AGB_genders.MALE,
                [290, 380, 484, 598, 717, 835, 945, 1042, 1124],
            ),
            (
                "wa1440_70",
                AGB_bowstyles.TRADITIONAL,
                AGB_genders.FEMALE,
                [252, 338, 441, 558, 682, 806, 921, 1023, 1108],
            ),
            (
                "wa1440_70",
                AGB_bowstyles.COMPOUNDBAREBOW,
                AGB_genders.FEMALE,
                [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392],
            ),
            (
                "wa1440_70",
                AGB_bowstyles.COMPOUNDLIMITED,
                AGB_genders.FEMALE,
                [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_nonbowstyles(
        self,
        roundname: str,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        scores_expected: list[int],
    ) -> None:
        """Check that appropriate scores returned for valid non-outdoor bowstyles."""
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle=bowstyle,
            gender=gender,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "roundname,scores_expected",
        [
            (
                "wa1440_90_small",
                [866, 982, 1081, 1162, 1229, 1283, 1327, 1362, 1389],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_small_faces(
        self,
        roundname: str,
        scores_expected: list[int],
    ) -> None:
        """Check that outdoor classification returns single face scores only."""
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,age_group,msg",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                "wa1440_90",
                "invalidbowstyle",
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                (
                    "invalidbowstyle is not a recognised bowstyle for outdoor "
                    "classifications. Please select from "
                    "AGB_bowstyles.COMPOUND|RECURVE|BAREBOW|LONGBOW."
                ),
            ),
            (
                "wa1440_90",
                AGB_bowstyles.RECURVE,
                "invalidgender",
                AGB_ages.AGE_ADULT,
                (
                    "invalidgender is not a recognised gender group for outdoor "
                    "classifications. Please select from `archeryutils.AGB_genders`."
                ),
            ),
            (
                "wa1440_90",
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
        roundname: str,
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
                roundname=roundname,
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )

    def test_agb_outdoor_classification_scores_invalid_round(
        self,
    ) -> None:
        """Check that outdoor classification raises error for invalid round."""
        with pytest.raises(
            KeyError,
            match=("invalid_roundname"),
        ):
            _ = class_funcs.agb_outdoor_classification_scores(
                roundname="invalid_roundname",
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )


class TestCalculateAgbOutdoorClassification:
    """Tests for the outdoor classification function."""

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,class_expected",
        [
            (
                "wa1440_90",
                1390,  # 1 above EMB
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "EMB",
            ),
            (
                "wa1440_70",
                1382,  # 1 below EMB
                AGB_ages.AGE_50_PLUS,
                AGB_bowstyles.COMPOUND,
                "GMB",
            ),
            (
                "wa1440_90",
                900,  # midway MB
                AGB_ages.AGE_UNDER_21,
                AGB_bowstyles.BAREBOW,
                "MB",
            ),
            (
                "wa1440_70",
                1269,  # 1 below MB
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.COMPOUND,
                "B1",
            ),
            (
                "wa1440_70",
                969,  # boundary value
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.RECURVE,
                "B1",
            ),
            (
                "metric_v",
                992,  # Boundary
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.RECURVE,
                "B2",
            ),
            (
                "metric_v",
                222,  # Midway
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "A1",
            ),
            (
                "metric_v",
                91,  # On boundary
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "UC",
            ),
            (
                "metric_v",
                1,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "UC",
            ),
            (
                "metric_v",
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
        roundname: str,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that outdoor classification returns expected value for a few cases."""
        class_returned = class_funcs.calculate_agb_outdoor_classification(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,class_expected",
        [
            (
                "wa720_70",  # Not prestige only 70m => B2
                720,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "B2",
            ),
            (
                "wa720_50_b",  # Not prestige only 50m => A1
                720,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "A1",
            ),
            (
                "wa720_50_c",  # Prestige => EMB
                720,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "EMB",
            ),
            (
                "metric_80_30",  # This and next 2 check Prestige by age
                720,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "A3",  # 30m for adults gets A3
            ),
            (
                "metric_80_30",
                720,
                AGB_ages.AGE_UNDER_14,
                AGB_bowstyles.COMPOUND,
                "B3",  # Max dist reqd. for B1 and B2
            ),
            (
                "metric_80_30",
                720,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.COMPOUND,
                "EMB",  # Age appropriate
            ),
            (
                "metric_122_50",
                720,
                AGB_ages.AGE_UNDER_16,
                AGB_bowstyles.COMPOUND,
                "B2",  # Under 16+ Max dist reqd. for B1 (not B2)
            ),
            (
                "wa720_60",  # Recurve 50+ get 60m 720
                720,
                AGB_ages.AGE_50_PLUS,
                AGB_bowstyles.RECURVE,
                "EMB",
            ),
            (
                "wa720_60",  # Recurve U18 get 60m 720
                720,
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.RECURVE,
                "EMB",
            ),
            (
                "metric_122_50",  # Recurve U18 get 50m Metric 122
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
        roundname: str,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that prestige and distanec limitations are working for a few cases."""
        class_returned = class_funcs.calculate_agb_outdoor_classification(
            roundname=roundname,
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
            KeyError,
            match=("invalid_roundname"),
        ):
            _ = class_funcs.calculate_agb_outdoor_classification(
                roundname="invalid_roundname",
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
                f"Invalid score of {score} for a wa1440_90. "
                f"Should be in range 0-{ALL_OUTDOOR_ROUNDS['wa1440_90'].max_score()}."
            ),
        ):
            _ = class_funcs.calculate_agb_outdoor_classification(
                score=score,
                roundname="wa1440_90",
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
            )
