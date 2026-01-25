"""Tests for field classification functions."""

import re

import pytest

import archeryutils.classifications as cf
from archeryutils import Pass, Round, load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

ALL_AGBFIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ],
)

CUSTOM_ROUND = Round(
    "My Custom Round",
    [
        Pass.at_target(30, "WA_field", 80, (48.5, "m"), indoor=False),
        Pass.at_target(30, "WA_field", 60, (46.3, "m"), indoor=False),
        Pass.at_target(30, "WA_field", 40, (23.25, "m"), indoor=False),
        Pass.at_target(30, "WA_field", 20, (12.75, "m"), indoor=False),
    ],
    location="Field",
)


class TestAgbFieldClassificationScores:
    """Tests for the field classification scores function."""

    @pytest.mark.parametrize(
        "archery_round,age_group,scores_expected",
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_ages.AGE_ADULT,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_ages.AGE_50_PLUS,
                [321, 294, 263, 227, 188, 149, 114, 84, 60],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_ages.AGE_UNDER_18,
                [305, 275, 241, 203, 164, 127, 94, 68, 48],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_ages.AGE_UNDER_12,
                [224, 185, 146, 111, 82, 58, 41, 28, 19],
            ),
        ],
    )
    def test_agb_field_classification_scores_ages(
        self,
        archery_round: str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = cf.agb_field_classification_scores(
            archery_round=archery_round,
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "archery_round,age_group,scores_expected",
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_ages.AGE_UNDER_21,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_ages.AGE_ADULT,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
                id="Test valid values pass through coaxing unchanged",
            ),
        ],
    )
    def test_agb_field_classification_scores_nonages(
        self,
        archery_round: str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        coaxed_vals = cf.coax_field_group(
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )
        scores = cf.agb_field_classification_scores(
            archery_round=archery_round,
            **coaxed_vals,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "archery_round,gender,age_group,scores_expected",
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_genders.FEMALE,
                AGB_ages.AGE_ADULT,
                [315, 287, 255, 218, 179, 140, 106, 78, 55],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_genders.MALE,
                AGB_ages.AGE_UNDER_18,
                [305, 275, 241, 203, 164, 127, 94, 68, 48],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_genders.FEMALE,
                AGB_ages.AGE_UNDER_18,
                [280, 247, 209, 170, 132, 99, 72, 51, 35],
            ),
        ],
    )
    def test_agb_field_classification_scores_genders(
        self,
        archery_round: str,
        gender: AGB_genders,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = cf.agb_field_classification_scores(
            archery_round=archery_round,
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=gender,
            age_group=age_group,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "archery_round,bowstyle,scores_expected",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                AGB_bowstyles.COMPOUND,
                [408, 391, 369, 345, 318, 286, 248, 204, 157],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_12_red_unmarked"],
                AGB_bowstyles.COMPOUND,
                [-9999, -9999, -9999, 173, 159, 143, 124, 102, 79],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                AGB_bowstyles.COMPOUNDLIMITED,
                [369, 347, 322, 293, 259, 219, 176, 133, 96],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_bowstyles.COMPOUNDBAREBOW,
                [343, 321, 296, 268, 235, 200, 164, 129, 99],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                AGB_bowstyles.RECURVE,
                [369, 343, 314, 279, 237, 189, 139, 96, 62],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_bowstyles.BAREBOW,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_bowstyles.TRADITIONAL,
                [309, 283, 252, 218, 182, 146, 114, 86, 63],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_bowstyles.FLATBOW,
                [273, 244, 212, 179, 146, 116, 90, 68, 51],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_bowstyles.LONGBOW,
                [241, 209, 176, 143, 114, 88, 67, 49, 36],
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_bowstyles.ENGLISHLONGBOW,
                [241, 209, 176, 143, 114, 88, 67, 49, 36],
            ),
        ],
    )
    def test_agb_field_classification_scores_bowstyles(
        self,
        archery_round: str,
        bowstyle: AGB_bowstyles,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = cf.agb_field_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,age_group,msg",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                "invalidbowstyle",
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                (
                    "invalidbowstyle is not a recognised bowstyle for field "
                    "classifications. Please select from "
                    "`AGB_bowstyles.COMPOUND|RECURVE|BAREBOW|ENGLISHLONGBOW|TRADITIONAL"
                    "|FLATBOW|COMPOUNDLIMITED|COMPOUNDBAREBOW`."
                ),
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                AGB_bowstyles.RECURVE,
                "invalidgender",
                AGB_ages.AGE_ADULT,
                (
                    "invalidgender is not a recognised gender group for field "
                    "classifications. Please select from `archeryutils.AGB_genders`."
                ),
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                "invalidage",
                (
                    "invalidage is not a recognised age group for field "
                    "classifications. Please select from "
                    "`AGB_ages.AGE_50_PLUS|AGE_ADULT|AGE_UNDER_18|AGE_UNDER_16|"
                    "AGE_UNDER_15|AGE_UNDER_14|AGE_UNDER_12`."
                ),
            ),
        ],
    )
    def test_agb_field_classification_scores_invalid(
        self,
        archery_round: str,
        bowstyle: AGB_bowstyles,
        gender: AGB_genders,
        age_group: AGB_ages,
        msg: str,
    ) -> None:
        """Check that field classification returns expected value for a case."""
        with pytest.raises(
            ValueError,
            match=msg,
        ):
            _ = cf.agb_field_classification_scores(
                archery_round=archery_round,
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )

    def test_agb_field_classification_scores_invalid_round(
        self,
    ) -> None:
        """Check that field classification raises error for invalid round."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    "This round is not recognised for the purposes of "
                    "field classification.\n"
                    "Please select an appropriate option using "
                    "`archeryutils.load_rounds`."
                )
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = cf.agb_field_classification_scores(
                archery_round=my_round,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_field_classification_scores_invalid_string_round(
        self,
    ) -> None:
        """Check that field classification raises error for invalid string round."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    "This round is not recognised for the purposes of "
                    "field classification.\n"
                    "Please select an appropriate option using "
                    "`archeryutils.load_rounds`."
                )
            ),
        ):
            _ = cf.agb_field_classification_scores(
                archery_round="invalid_roundname",
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_field_classification_scores_string_round(
        self,
    ) -> None:
        """Check that field classification can process a string roundname."""
        scores = cf.agb_field_classification_scores(
            archery_round="wa_field_24_blue_marked",
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == [336, 311, 283, 249, 212, 173, 135, 101, 74]

    @pytest.mark.parametrize(
        "archery_round,expected_scores",
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_12_white_marked"],
                [184, 174, 162, 149, 134, 116, 97, 77, 58],
            ),
            (
                CUSTOM_ROUND,
                [480, 426, 364, 296, 228, 167, 118, 80, 54],
            ),
            (
                load_rounds.WA_outdoor.wa1440_90,
                [1042, 926, 793, 652, 514, 389, 283, 199, 136],
            ),
        ],
    )
    def test_agb_field_classification_scores_non_strict(
        self, archery_round, expected_scores
    ) -> None:
        """
        Check that field classification returns expected value for non strict.

        Non-strict rounds and distance so all scores should always be returned.
        """
        scores = cf.agb_field_classification_scores(
            archery_round=archery_round,
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=AGB_genders.FEMALE,
            age_group=AGB_ages.AGE_ADULT,
            strict_rounds=False,
            strict_distance=False,
        )

        assert scores == expected_scores

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,age_group,expected_scores",
        [
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [-9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999],
                id="Check red-peg returns no classifications for unsighted.",
            ),
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_24_yellow_marked"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [-9999, -9999, -9999, -9999, -9999, -9999, 178, 140, 106],
                id="Check wrong 24-target returns distance-limited classifications.",
            ),
            pytest.param(
                CUSTOM_ROUND,
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [-9999, -9999, -9999, -9999, -9999, -9999, -9999, 167, 108],
                id="Check custom round (48.5m) returns up to A2.",
            ),
            pytest.param(
                load_rounds.misc.frostbite,
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [-9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, 128],
                id="Check frostbite returns A3.",
            ),
            pytest.param(
                load_rounds.misc.frostbite,
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_UNDER_12,
                [286, 256, 217, 170, 123, 82, 52, 32, 19],
                id="Check frostbite returns all for U12.",
            ),
            pytest.param(
                load_rounds.AGB_indoor.portsmouth,
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [-9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999],
                id="Check 20y returns nothing.",
            ),
            pytest.param(
                load_rounds.WA_outdoor.wa1440_60,
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [-9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999],
                id="Check 60m 1440 returns nothing for unsighted.",
            ),
            pytest.param(
                load_rounds.WA_outdoor.wa1440_60,
                AGB_bowstyles.COMPOUND,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [1423, 1400, 1366, 1322, 1264, 1189, 1091, 965, 810],
                id="Check 60m 1440 returns scores for sighted.",
            ),
        ],
    )
    def test_agb_field_classification_scores_non_strict_round(
        self,
        archery_round,
        bowstyle,
        gender,
        age_group,
        expected_scores,
    ) -> None:
        """Check that classification returns expected scores for non strict rounds."""
        scores = cf.agb_field_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age_group,
            strict_rounds=False,
            strict_distance=True,
        )

        assert scores == expected_scores

    @pytest.mark.parametrize(
        "archery_round",
        ["wa_field_24_red_marked", "fake_round", ""],
    )
    def test_agb_field_classification_scores_non_strict_round_string(
        self,
        archery_round,
    ) -> None:
        """Check that field classification errors for non strict string rounds."""
        with pytest.raises(
            TypeError,
            match=(
                r"strict_rounds is False so archery_round must be explicitly specified "
                "as a Round type instead of a string."
            ),
        ):
            scores = cf.agb_field_classification_scores(
                archery_round=archery_round,
                bowstyle=AGB_bowstyles.COMPOUND,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
                strict_rounds=False,
            )

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,age_group,expected_scores",
        [
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [306, 277, 243, 204, 164, 125, 91, 64, 44],
                id="Check red-peg returns scores for unsighted.",
            ),
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_12_red_marked"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [-9999, -9999, -9999, 102, 82, 63, 46, 32, 22],
                id="Check 12-target red-peg returns B1 scores for unsighted.",
            ),
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_24_yellow_marked"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [360, 338, 313, 285, 253, 217, 178, 140, 106],
                id="Check short peg 24-target returns all scores.",
            ),
        ],
    )
    def test_agb_field_classification_scores_non_strict_distance(
        self,
        archery_round,
        bowstyle,
        gender,
        age_group,
        expected_scores,
    ) -> None:
        """Check that classification returns expected scores for non strict dist."""
        scores = cf.agb_field_classification_scores(
            archery_round=archery_round,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age_group,
            strict_rounds=True,
            strict_distance=False,
        )

        assert scores == expected_scores


class TestCalculateAgbFieldClassification:
    """Tests for the field classification function."""

    @pytest.mark.parametrize(
        "archery_round,score,age_group,bowstyle,class_expected",
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                400,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "GMB",
            ),
            (  # Bowman classifications only on 12-target rounds
                ALL_AGBFIELD_ROUNDS["wa_field_12_red_marked"],
                200,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "B1",
            ),
            (  # Archer classifications only on shorter rounds - A1
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                400,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "A1",
            ),
            (  # Archer classifications only on shorter rounds - A2
                ALL_AGBFIELD_ROUNDS["wa_field_24_yellow_marked"],
                400,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "A2",
            ),
            (  # Archer classifications only on shorter rounds - A3
                ALL_AGBFIELD_ROUNDS["wa_field_24_white_marked"],
                400,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "A3",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                337,
                AGB_ages.AGE_50_PLUS,
                AGB_bowstyles.RECURVE,
                "GMB",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                177,
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.TRADITIONAL,
                "B1",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                177,
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.TRADITIONAL,
                "UC",
            ),
            (  # Bowman classifications only on 12-target rounds
                ALL_AGBFIELD_ROUNDS["wa_field_12_blue_marked"],
                88,
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.TRADITIONAL,
                "B1",
            ),
            (  # Archer classifications only on shorter rounds - Junior
                ALL_AGBFIELD_ROUNDS["wa_field_24_yellow_marked"],
                400,
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.TRADITIONAL,
                "A1",
            ),
            (  # Archer classifications only on shorter rounds - Junior
                ALL_AGBFIELD_ROUNDS["wa_field_24_white_marked"],
                400,
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.TRADITIONAL,
                "A2",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                143,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.FLATBOW,
                "EMB",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                96,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "EMB",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                1,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "UC",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                1,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.ENGLISHLONGBOW,
                "UC",
            ),
        ],
    )
    def test_calculate_agb_field_classification(
        self,
        archery_round: str,
        score: float,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that field classification returns expected value for a few cases."""
        class_returned = cf.calculate_agb_field_classification(
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
                ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                306,
                AGB_ages.AGE_UNDER_21,
                AGB_bowstyles.BAREBOW,
                "MB",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                306,
                AGB_ages.AGE_UNDER_21,
                AGB_bowstyles.BAREBOW,
                "UC",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                306,
                AGB_ages.AGE_UNDER_21,
                AGB_bowstyles.RECURVE,
                "B1",
            ),
        ],
    )
    def test_calculate_agb_field_classification_nonages(
        self,
        archery_round: str,
        score: float,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that field classification returns expected value for non-field ages."""
        coaxed_vals = cf.coax_field_group(
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )
        class_returned = cf.calculate_agb_field_classification(
            archery_round=archery_round,
            score=score,
            **coaxed_vals,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "archery_round,score,bowstyle,class_expected",
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_unmarked"],
                400,
                AGB_bowstyles.ENGLISHLONGBOW,
                "UC",
            ),
            (
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                337,
                AGB_bowstyles.BAREBOW,
                "UC",
            ),
        ],
    )
    def test_calculate_agb_field_classification_invalid_rounds(
        self,
        archery_round: str,
        score: float,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check field classification returns unclassified for inappropriate rounds."""
        class_returned = cf.calculate_agb_field_classification(
            archery_round=archery_round,
            score=score,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "score",
        [1000, 433, -1, -100],
    )
    def test_calculate_agb_field_classification_invalid_scores(
        self,
        score: float,
    ) -> None:
        """Check that field classification fails for inappropriate scores."""
        with pytest.raises(
            ValueError,
            match=(
                f"Invalid score of {score} for a "
                f"{ALL_AGBFIELD_ROUNDS['wa_field_24_blue_marked'].name}. "
                "Should be in range "
                f"0-{ALL_AGBFIELD_ROUNDS['wa_field_24_blue_marked'].max_score()}."
            ),
        ):
            _ = cf.calculate_agb_field_classification(
                score=score,
                archery_round=ALL_AGBFIELD_ROUNDS["wa_field_24_blue_marked"],
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_field_classification_invalid_round(
        self,
    ) -> None:
        """Check that field classification raises error for invalid round."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    "This round is not recognised for the purposes of "
                    "field classification.\n"
                    "Please select an appropriate option using "
                    "`archeryutils.load_rounds`."
                )
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = cf.calculate_agb_field_classification(
                archery_round=my_round,
                score=333,
                bowstyle=AGB_bowstyles.RECURVE,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_field_classification_scores_invalid_string_round(
        self,
    ) -> None:
        """Check that field classification raises error for invalid string round."""
        with pytest.raises(
            ValueError,
            match=(
                re.escape(
                    "This round is not recognised for the purposes of "
                    "field classification.\n"
                    "Please select an appropriate option using "
                    "`archeryutils.load_rounds`."
                )
            ),
        ):
            _ = cf.calculate_agb_field_classification(
                archery_round="invalid_roundname",
                score=333,
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_field_classification_scores_string_round(
        self,
    ) -> None:
        """Check that field classification can process a string roundname."""
        my_class = cf.calculate_agb_field_classification(
            archery_round="wa_field_24_blue_marked",
            score=252,
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert my_class == "B1"

    @pytest.mark.parametrize(
        "archery_round,score,expected_class",
        [
            (
                ALL_AGBFIELD_ROUNDS["wa_field_12_white_marked"],
                214,
                "MB",
            ),
            (
                CUSTOM_ROUND,
                500,
                "B3",
            ),
            (
                load_rounds.misc.frostbite,
                358,
                "GMB",
            ),
            (
                load_rounds.AGB_indoor.portsmouth,
                595,
                "MB",
            ),
        ],
    )
    def test_agb_field_classification_non_strict(
        self, archery_round, score, expected_class
    ) -> None:
        """Check that field classification returns expected value for non-strict."""
        frostbite = load_rounds.misc.frostbite
        my_class = cf.calculate_agb_field_classification(
            archery_round=archery_round,
            score=score,
            bowstyle=AGB_bowstyles.COMPOUND,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
            strict_rounds=False,
            strict_distance=False,
        )

        assert my_class == expected_class

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,age_group,score,expected_class",
        [
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_12_red_marked"],
                AGB_bowstyles.COMPOUND,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                214,
                "EMB",
                id="Check non-24 target red peg can give MB.",
            ),
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_24_yellow_marked"],
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                412,
                "A2",
                id="Check short 24-target prestige limited to A.",
            ),
            pytest.param(
                CUSTOM_ROUND,
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                720,
                "A2",
                id="Check custom round (48.5m) returns max A2.",
            ),
            pytest.param(
                load_rounds.misc.frostbite,
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                300,
                "A3",
                id="Check frostbite returns A3.",
            ),
            pytest.param(
                load_rounds.AGB_indoor.portsmouth,
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                600,
                "UC",
                id="Check indoor 20y returns nothing.",
            ),
            pytest.param(
                load_rounds.WA_outdoor.wa1440_60,
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                1100,
                "UC",
                id="Check 60m 1440 returns UC for unsighted.",
            ),
            pytest.param(
                load_rounds.WA_outdoor.wa1440_60,
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                1400,
                "EMB",
                id="Check 60m 1440 returns MB for sighted.",
            ),
        ],
    )
    def test_agb_field_classification_non_strict_round(
        self,
        archery_round,
        bowstyle,
        gender,
        age_group,
        score,
        expected_class,
    ) -> None:
        """Check that expected classification returned for non strict rounds."""
        my_class = cf.calculate_agb_field_classification(
            archery_round=archery_round,
            score=score,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age_group,
            strict_rounds=False,
            strict_distance=True,
        )

        assert my_class == expected_class

    @pytest.mark.parametrize(
        "archery_round",
        ["wa_field_24_red_marked", "fake_round", ""],
    )
    def test_agb_field_classification_non_strict_round_string(
        self,
        archery_round,
    ) -> None:
        """Check that field classification errors for non strict string rounds."""
        with pytest.raises(
            TypeError,
            match=(
                r"strict_rounds is False so archery_round must be explicitly specified "
                "as a Round type instead of a string."
            ),
        ):
            scores = cf.calculate_agb_field_classification(
                archery_round=archery_round,
                score=123,
                bowstyle=AGB_bowstyles.COMPOUND,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
                strict_rounds=False,
            )

    @pytest.mark.parametrize(
        "archery_round,bowstyle,gender,age_group,score,expected_class",
        [
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_24_red_marked"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                360,
                "EMB",
                id="Check red-peg returns MB scores for unsighted.",
            ),
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_12_red_marked"],
                AGB_bowstyles.RECURVE,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                175,
                "B1",
                id="Check 12-target red-peg returns B1 for unsighted.",
            ),
            pytest.param(
                ALL_AGBFIELD_ROUNDS["wa_field_24_yellow_marked"],
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                340,
                "GMB",
                id="Check short peg 24-target returns MB.",
            ),
        ],
    )
    def test_agb_field_classification_non_strict_distance(
        self,
        archery_round,
        bowstyle,
        gender,
        age_group,
        score,
        expected_class,
    ) -> None:
        """Check that expected classification returned for non strict dist."""
        my_class = cf.calculate_agb_field_classification(
            archery_round=archery_round,
            score=score,
            bowstyle=bowstyle,
            gender=gender,
            age_group=age_group,
            strict_rounds=True,
            strict_distance=False,
        )

        assert my_class == expected_class
