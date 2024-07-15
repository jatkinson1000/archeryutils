"""Tests for agb outdoor classification functions."""

import pytest

import archeryutils as au
import archeryutils.classifications as class_funcs
from archeryutils import load_rounds

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
                "adult",
                [426, 566, 717, 866, 999, 1110, 1197, 1266, 1320],
            ),
            (
                "wa1440_70",
                "50+",
                [364, 503, 659, 817, 960, 1079, 1173, 1247, 1305],
            ),
            (
                "wa1440_90",
                "under21",
                [313, 435, 577, 728, 877, 1008, 1117, 1203, 1270],
            ),
            (
                "wa1440_70",
                "Under 18",
                [259, 373, 514, 671, 828, 969, 1086, 1179, 1252],
            ),
            (
                "wa1440_60",
                "Under 16",
                [227, 335, 474, 635, 799, 946, 1068, 1165, 1241],
            ),
            (
                "metric_iii",
                "Under 15",
                [270, 389, 534, 693, 849, 988, 1101, 1191, 1261],
            ),
            (
                "metric_iv",
                "Under 14",
                [396, 524, 666, 814, 952, 1070, 1166, 1242, 1301],
            ),
            (
                "metric_v",
                "Under 12",
                [406, 550, 706, 858, 992, 1104, 1193, 1263, 1317],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_ages(
        self,
        roundname: str,
        age_group: str,
        scores_expected: list[int],
    ) -> None:
        """Check that  classification returns expected value for a case."""
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle="recurve",
            gender="male",
            age_group=age_group,
        )

        assert scores == pytest.approx(scores_expected[::-1])

    @pytest.mark.parametrize(
        "roundname,age_group,scores_expected",
        [
            (
                "wa1440_70",
                "adult",
                [392, 536, 693, 849, 988, 1101, 1191, 1261, 1316],
            ),
            (
                "metric_iii",
                "Under 16",
                [293, 418, 567, 727, 881, 1014, 1122, 1207, 1274],
            ),
            (
                "metric_iii",
                "Under 15",
                [270, 389, 534, 693, 849, 988, 1101, 1191, 1261],
            ),
            (
                "metric_v",
                "Under 12",
                [406, 550, 706, 858, 992, 1104, 1193, 1263, 1317],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_genders(
        self,
        roundname: str,
        age_group: str,
        scores_expected: list[int],
    ) -> None:
        """
        Check that outdoor classification returns expected value for a case.

        Male equivalents already checked above.
        Also checks that compound rounds are being enforced.
        """
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle="recurve",
            gender="female",
            age_group=age_group,
        )

        assert scores == pytest.approx(scores_expected[::-1])

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,scores_expected",
        [
            (
                "wa1440_90",
                "compound",
                "male",
                [866, 982, 1081, 1162, 1229, 1283, 1327, 1362, 1389],
            ),
            (
                "wa1440_70",
                "compound",
                "female",
                [870, 988, 1086, 1167, 1233, 1286, 1330, 1364, 1392],
            ),
            (
                "wa1440_90",
                "barebow",
                "male",
                [290, 380, 484, 598, 717, 835, 945, 1042, 1124],
            ),
            (
                "wa1440_70",
                "barebow",
                "female",
                [252, 338, 441, 558, 682, 806, 921, 1023, 1108],
            ),
            (
                "wa1440_90",
                "longbow",
                "male",
                [85, 124, 177, 248, 337, 445, 566, 696, 825],
            ),
            (
                "wa1440_70",
                "longbow",
                "female",
                [64, 94, 136, 195, 274, 373, 493, 625, 761],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_bowstyles(
        self,
        roundname: str,
        bowstyle: str,
        gender: str,
        scores_expected: list[int],
    ) -> None:
        """Check that outdoor classification returns expected value for a case."""
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle=bowstyle,
            gender=gender,
            age_group="adult",
        )

        assert scores == pytest.approx(scores_expected[::-1])

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,scores_expected",
        [
            (
                "wa1440_90",
                "flatbow",
                "male",
                [290, 380, 484, 598, 717, 835, 945, 1042, 1124],
            ),
            (
                "wa1440_70",
                "traditional",
                "female",
                [252, 338, 441, 558, 682, 806, 921, 1023, 1108],
            ),
            (
                "wa1440_70",
                "asiatic",
                "female",
                [252, 338, 441, 558, 682, 806, 921, 1023, 1108],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_nonbowstyles(
        self,
        roundname: str,
        bowstyle: str,
        gender: str,
        scores_expected: list[int],
    ) -> None:
        """Check that barebow scores returned for valid but non-outdoor bowstyles."""
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle=bowstyle,
            gender=gender,
            age_group="adult",
        )

        assert scores == pytest.approx(scores_expected[::-1])

    @pytest.mark.parametrize(
        "roundname,scores_expected",
        [
            (
                "wa1440_90_small",
                [866, 982, 1081, 1162, 1229, 1283, 1327, 1362, 1389],
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_triple_faces(
        self,
        roundname: str,
        scores_expected: list[int],
    ) -> None:
        """
        Check that outdoor classification returns single face scores only.

        Includes check that Worcester returns null above max score.
        """
        scores = class_funcs.agb_outdoor_classification_scores(
            roundname=roundname,
            bowstyle="compound",
            gender="male",
            age_group="adult",
        )

        assert scores == pytest.approx(scores_expected[::-1])

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,age_group",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                "wa1440_90",
                "invalidbowstyle",
                "male",
                "adult",
            ),
            (
                "wa1440_90",
                "recurve",
                "invalidgender",
                "adult",
            ),
            (
                "wa1440_90",
                "barebow",
                "male",
                "invalidage",
            ),
        ],
    )
    def test_agb_outdoor_classification_scores_invalid(
        self,
        roundname: str,
        bowstyle: str,
        gender: str,
        age_group: str,
    ) -> None:
        """Check that outdoor classification returns expected value for a case."""
        with pytest.raises(
            KeyError,
            match=(
                f"{age_group.lower().replace(' ','')}_"
                f"{gender.lower()}_{bowstyle.lower()}"
            ),
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
                bowstyle="barebow",
                gender="female",
                age_group="adult",
            )


class TestCalculateAgbOutdoorClassification:
    """Tests for the outdoor classification function."""

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,class_expected",
        [
            (
                "wa1440_90",
                1390,  # 1 above EMB
                "adult",
                "compound",
                "EMB",
            ),
            (
                "wa1440_70",
                1382,  # 1 below EMB
                "50+",
                "compound",
                "GMB",
            ),
            (
                "wa1440_90",
                900,  # midway MB
                "under21",
                "barebow",
                "MB",
            ),
            (
                "wa1440_70",
                1269,  # 1 below MB
                "Under 18",
                "compound",
                "B1",
            ),
            (
                "wa1440_70",
                969,  # boundary value
                "Under 18",
                "recurve",
                "B1",
            ),
            (
                "metric_v",
                992,  # Boundary
                "Under 12",
                "recurve",
                "B2",
            ),
            (
                "metric_v",
                222,  # Midway
                "Under 12",
                "longbow",
                "A1",
            ),
            (
                "metric_v",
                91,  # On boundary
                "Under 12",
                "longbow",
                "UC",
            ),
            (
                "metric_v",
                1,
                "Under 12",
                "longbow",
                "UC",
            ),
        ],
    )
    def test_calculate_agb_outdoor_classification(  # noqa: PLR0913 Too many arguments
        self,
        score: float,
        roundname: str,
        age_group: str,
        bowstyle: str,
        class_expected: str,
    ) -> None:
        """Check that outdoor classification returns expected value for a few cases."""
        class_returned = class_funcs.calculate_agb_outdoor_classification(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender="male",
            age_group=age_group,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,class_expected",
        [
            (
                "wa720_70",  # Not prestige only 70m => B2
                720,
                "adult",
                "compound",
                "B2",
            ),
            (
                "wa720_50_b",  # Not prestige only 50m => A1
                720,
                "adult",
                "compound",
                "A1",
            ),
            (
                "wa720_50_c",  # Prestige => EMB
                720,
                "adult",
                "compound",
                "EMB",
            ),
            (
                "metric_80_30",  # This and next 2 check Prestige by age
                720,
                "adult",
                "compound",
                "A3",  # 30m for adults gets A3
            ),
            (
                "metric_80_30",
                720,
                "Under 14",
                "compound",
                "B3",  # Max dist reqd. for B1 and B2
            ),
            (
                "metric_80_30",
                720,
                "Under 12",
                "compound",
                "EMB",  # Age appropriate
            ),
            (
                "metric_122_50",
                720,
                "Under 16",
                "compound",
                "B2",  # Under 16+ Max dist reqd. for B1 (not B2)
            ),
            (
                "wa720_60",  # Recurve 50+ get 60m 720
                720,
                "50+",
                "recurve",
                "EMB",
            ),
            (
                "wa720_60",  # Recurve U18 get 60m 720
                720,
                "Under 18",
                "recurve",
                "EMB",
            ),
            (
                "metric_122_50",  # Recurve U18 get 50m Metric 122
                720,
                "Under 16",
                "recurve",
                "EMB",
            ),
        ],
    )
    def test_calculate_agb_outdoor_classification_prestige_dist(  # noqa: PLR0913 Too many arguments
        self,
        score: float,
        roundname: str,
        age_group: str,
        bowstyle: str,
        class_expected: str,
    ) -> None:
        """Check that prestige and distanec limitations are working for a few cases."""
        class_returned = class_funcs.calculate_agb_outdoor_classification(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender="male",
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
                bowstyle="recurve",
                gender="male",
                age_group="adult",
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
                bowstyle="barebow",
                gender="male",
                age_group="adult",
            )


class TestCalculateAgbOutdoorClassificationFraction:
    """Class to test the outdoor classification fraction function."""

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,frac_expected",
        [
            (
                "wa720_70",
                450,
                "adult",
                "compound",
                0.3906252368174717,
            ),
            (
                "wa720_50_b",
                425,
                "adult",
                "barebow",
                0.11099804827974227,
            ),
            (
                "wa720_50_c",
                450,
                "adult",
                "compound",
                0.42456775138238356,
            ),
            (
                "wa720_60",
                620,
                "Under 18",
                "recurve",
                0.7257808930669505,
            ),
        ],
    )
    def test_agb_outdoor_classification_fraction(  # noqa: PLR0913 many args
        self,
        score: float,
        roundname: str,
        age_group: str,
        bowstyle: str,
        frac_expected: float,
    ) -> None:
        """Check that classification fraction is as expected."""
        frac_returned = class_funcs.agb_outdoor_classification_fraction(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender="male",
            age_group=age_group,
        )

        assert frac_returned == pytest.approx(frac_expected)

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,frac_expected",
        [
            (
                "wa720_70",
                1,
                "adult",
                "compound",
                0.0,
            ),
            (
                "wa720_50_b",
                20,
                "adult",
                "barebow",
                0.0,
            ),
            (
                "wa720_50_c",
                30,
                "adult",
                "compound",
                0.0,
            ),
            (
                "wa720_60",
                1,
                "Under 18",
                "recurve",
                0.0,
            ),
        ],
    )
    def test_agb_outdoor_classification_fraction_low(  # noqa: PLR0913 many args
        self,
        score: float,
        roundname: str,
        age_group: str,
        bowstyle: str,
        frac_expected: float,
    ) -> None:
        """Check that classification fraction below lowest classification is 0.0."""
        frac_returned = class_funcs.agb_outdoor_classification_fraction(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender="male",
            age_group=age_group,
        )

        assert frac_returned == pytest.approx(frac_expected)

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,frac_expected",
        [
            (
                "wa720_70",
                720,
                "adult",
                "compound",
                1.0,
            ),
            (
                "wa720_50_b",
                650,
                "adult",
                "barebow",
                1.0,
            ),
            (
                "wa720_50_c",
                718,
                "adult",
                "compound",
                1.0,
            ),
            (
                "wa720_60",
                650,
                "under 18",
                "recurve",
                1.0,
            ),
        ],
    )
    def test_agb_outdoor_classification_fraction_high(  # noqa: PLR0913 many args
        self,
        score: float,
        roundname: str,
        age_group: str,
        bowstyle: str,
        frac_expected: float,
    ) -> None:
        """Check that classification fraction above highest classification is 1.0."""
        frac_returned = class_funcs.agb_outdoor_classification_fraction(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender="male",
            age_group=age_group,
        )

        assert frac_returned == pytest.approx(frac_expected)

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,frac_expected",
        [
            (
                "wa720_70",
                613,
                "adult",
                "compound",
                1.0,
            ),
            (
                "wa720_50_b",
                626,
                "adult",
                "barebow",
                1.0,
            ),
            (
                "wa720_50_c",
                640,
                "adult",
                "compound",
                0.0,
            ),
            (
                "wa720_60",
                338,
                "under 18",
                "recurve",
                0.0,
            ),
        ],
    )
    def test_agb_outdoor_classification_fraction_boundary(  # noqa: PLR0913 many args
        self,
        score: float,
        roundname: str,
        age_group: str,
        bowstyle: str,
        frac_expected: float,
    ) -> None:
        """Check that classification fraction above highest classification is 1.0."""
        frac_returned = class_funcs.agb_outdoor_classification_fraction(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender="male",
            age_group=age_group,
        )

        assert frac_returned == pytest.approx(frac_expected)

    def test_agb_outdoor_classification_fraction_restrict(
        self,
    ) -> None:
        """Check that classification fraction functions with restrict."""
        frac_restricted = class_funcs.agb_outdoor_classification_fraction(
            score=620,
            roundname="national",
            bowstyle="recurve",
            gender="male",
            age_group="adult",
        )
        assert frac_restricted == 1.0

        frac_unrestricted = class_funcs.agb_outdoor_classification_fraction(
            score=620,
            roundname="national",
            bowstyle="recurve",
            gender="male",
            age_group="adult",
            restrict=False,
        )

        assert frac_unrestricted == pytest.approx(0.4541258975704667)

    def test_agb_outdoor_classification_fraction_unrestrict_large(
        self,
    ) -> None:
        """Check classification fraction unrestricted for large scores."""
        frac_unrestricted = class_funcs.agb_outdoor_classification_fraction(
            score=646,
            roundname="national",
            bowstyle="recurve",
            gender="male",
            age_group="adult",
            restrict=False,
        )

        assert frac_unrestricted == pytest.approx(1.0)
