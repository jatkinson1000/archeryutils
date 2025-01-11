"""Tests for field classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders

ALL_AGBFIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ],
)


class TestAgbFieldClassificationScores:
    """Tests for the field classification scores function."""

    @pytest.mark.parametrize(
        "roundname,age_group,scores_expected",
        [
            (
                "wa_field_24_blue_marked",
                AGB_ages.ADULT,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_ages.P50,
                [321, 294, 263, 227, 188, 149, 114, 84, 60],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_ages.U21,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_ages.U18,
                [305, 275, 241, 203, 164, 127, 94, 68, 48],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_ages.U12,
                [224, 185, 146, 111, 82, 58, 41, 28, 19],
            ),
        ],
    )
    def test_agb_field_classification_scores_ages(
        self,
        roundname: str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_field_classification_scores(
            roundname=roundname,
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "roundname,gender,age_group,scores_expected",
        [
            (
                "wa_field_24_blue_marked",
                AGB_genders.MALE,
                AGB_ages.ADULT,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_genders.FEMALE,
                AGB_ages.ADULT,
                [315, 287, 255, 218, 179, 140, 106, 78, 55],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_genders.MALE,
                AGB_ages.U18,
                [305, 275, 241, 203, 164, 127, 94, 68, 48],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_genders.FEMALE,
                AGB_ages.U18,
                [280, 247, 209, 170, 132, 99, 72, 51, 35],
            ),
        ],
    )
    def test_agb_field_classification_scores_genders(
        self,
        roundname: str,
        gender: AGB_genders,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_field_classification_scores(
            roundname=roundname,
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=gender,
            age_group=age_group,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "roundname,bowstyle,scores_expected",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                "wa_field_24_red_marked",
                AGB_bowstyles.COMPOUND,
                [408, 391, 369, 345, 318, 286, 248, 204, 157],
            ),
            (
                "wa_field_12_red_unmarked",
                AGB_bowstyles.COMPOUND,
                [-9999, -9999, -9999, 173, 159, 143, 124, 102, 79],
            ),
            (
                "wa_field_24_red_marked",
                AGB_bowstyles.COMPOUNDLIMITED,
                [369, 347, 322, 293, 259, 219, 176, 133, 96],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.COMPOUNDBAREBOW,
                [343, 321, 296, 268, 235, 200, 164, 129, 99],
            ),
            (
                "wa_field_24_red_marked",
                AGB_bowstyles.RECURVE,
                [369, 343, 314, 279, 237, 189, 139, 96, 62],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.BAREBOW,
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.TRADITIONAL,
                [309, 283, 252, 218, 182, 146, 114, 86, 63],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.FLATBOW,
                [273, 244, 212, 179, 146, 116, 90, 68, 51],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.LONGBOW,
                [241, 209, 176, 143, 114, 88, 67, 49, 36],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.ENGLISHLONGBOW,
                [241, 209, 176, 143, 114, 88, 67, 49, 36],
            ),
        ],
    )
    def test_agb_field_classification_scores_bowstyles(
        self,
        roundname: str,
        bowstyle: AGB_bowstyles,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_field_classification_scores(
            roundname=roundname,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.ADULT,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,age_group,msg",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                "wa_field_24_red_marked",
                "invalidbowstyle",
                AGB_genders.MALE,
                AGB_ages.ADULT,
                (
                    "invalidbowstyle is not a recognised bowstyle for field "
                    "classifications. Please select from "
                    "AGB_bowstyles.COMPOUND|RECURVE|BAREBOW|ENGLISHLONGBOW|TRADITIONAL"
                    "|FLATBOW|COMPOUNDLIMITED|COMPOUNDBAREBOW."
                ),
            ),
            (
                "wa_field_24_red_marked",
                AGB_bowstyles.RECURVE,
                "invalidgender",
                AGB_ages.ADULT,
                (
                    "invalidgender is not a recognised gender group for field "
                    "classifications. Please select from `archeryutils.AGB_genders`."
                ),
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                "invalidage",
                (
                    "invalidage is not a recognised age group for field "
                    "classifications. Please select from "
                    "AGB_ages.P50|ADULT|U18|U16|U15|U14|U12."
                ),
            ),
        ],
    )
    def test_agb_field_classification_scores_invalid(
        self,
        roundname: str,
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
            _ = class_funcs.agb_field_classification_scores(
                roundname=roundname,
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )


class TestCalculateAgbFieldClassification:
    """Tests for the field classification function."""

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,class_expected",
        [
            (
                "wa_field_24_red_marked",
                400,
                AGB_ages.ADULT,
                AGB_bowstyles.COMPOUND,
                "GMB",
            ),
            (  # Bowman classifications only on 12-target rounds
                "wa_field_12_red_marked",
                200,
                AGB_ages.ADULT,
                AGB_bowstyles.COMPOUND,
                "B1",
            ),
            (  # Archer classifications only on shorter rounds - A1
                "wa_field_24_blue_marked",
                400,
                AGB_ages.ADULT,
                AGB_bowstyles.COMPOUND,
                "A1",
            ),
            (  # Archer classifications only on shorter rounds - A2
                "wa_field_24_yellow_marked",
                400,
                AGB_ages.ADULT,
                AGB_bowstyles.COMPOUND,
                "A2",
            ),
            (  # Archer classifications only on shorter rounds - A3
                "wa_field_24_white_marked",
                400,
                AGB_ages.ADULT,
                AGB_bowstyles.COMPOUND,
                "A3",
            ),
            (
                "wa_field_24_red_marked",
                337,
                AGB_ages.P50,
                AGB_bowstyles.RECURVE,
                "GMB",
            ),
            (
                "wa_field_24_blue_marked",
                306,
                AGB_ages.U21,
                AGB_bowstyles.BAREBOW,
                "MB",
            ),
            (
                "wa_field_24_red_marked",
                306,
                AGB_ages.U21,
                AGB_bowstyles.BAREBOW,
                "UC",
            ),
            (
                "wa_field_24_blue_marked",
                177,
                AGB_ages.U18,
                AGB_bowstyles.TRADITIONAL,
                "B1",
            ),
            (
                "wa_field_24_red_marked",
                177,
                AGB_ages.U18,
                AGB_bowstyles.TRADITIONAL,
                "UC",
            ),
            (  # Bowman classifications only on 12-target rounds
                "wa_field_12_blue_marked",
                88,
                AGB_ages.U18,
                AGB_bowstyles.TRADITIONAL,
                "B1",
            ),
            (  # Archer classifications only on shorter rounds - Junior
                "wa_field_24_yellow_marked",
                400,
                AGB_ages.U18,
                AGB_bowstyles.TRADITIONAL,
                "A1",
            ),
            (  # Archer classifications only on shorter rounds - Junior
                "wa_field_24_white_marked",
                400,
                AGB_ages.U18,
                AGB_bowstyles.TRADITIONAL,
                "A2",
            ),
            (
                "wa_field_24_blue_marked",
                143,
                AGB_ages.U12,
                AGB_bowstyles.FLATBOW,
                "EMB",
            ),
            (
                "wa_field_24_blue_marked",
                96,
                AGB_ages.U12,
                AGB_bowstyles.LONGBOW,
                "EMB",
            ),
            (
                "wa_field_24_blue_marked",
                1,
                AGB_ages.U12,
                AGB_bowstyles.LONGBOW,
                "UC",
            ),
            (
                "wa_field_24_blue_marked",
                1,
                AGB_ages.U12,
                AGB_bowstyles.ENGLISHLONGBOW,
                "UC",
            ),
        ],
    )
    def test_calculate_agb_field_classification(
        self,
        roundname: str,
        score: float,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that field classification returns expected value for a few cases."""
        class_returned = class_funcs.calculate_agb_field_classification(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "roundname,score,bowstyle,class_expected",
        [
            (
                "wa_field_24_red_unmarked",
                400,
                AGB_bowstyles.ENGLISHLONGBOW,
                "UC",
            ),
            (
                "wa_field_24_red_marked",
                337,
                AGB_bowstyles.BAREBOW,
                "UC",
            ),
        ],
    )
    def test_calculate_agb_field_classification_invalid_rounds(
        self,
        roundname: str,
        score: float,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check field classification returns unclassified for inappropriate rounds."""
        class_returned = class_funcs.calculate_agb_field_classification(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.ADULT,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "roundname,score",
        [
            (
                "wa_field_24_blue_marked",
                1000,
            ),
            (
                "wa_field_24_blue_marked",
                433,
            ),
            (
                "wa_field_24_blue_marked",
                -1,
            ),
            (
                "wa_field_24_blue_marked",
                -100,
            ),
        ],
    )
    def test_calculate_agb_field_classification_invalid_scores(
        self,
        roundname: str,
        score: float,
    ) -> None:
        """Check that field classification fails for inappropriate scores."""
        with pytest.raises(
            ValueError,
            match=(
                f"Invalid score of {score} for a {roundname}. "
                f"Should be in range 0-{ALL_AGBFIELD_ROUNDS[roundname].max_score()}."
            ),
        ):
            _ = class_funcs.calculate_agb_field_classification(
                score=score,
                roundname=roundname,
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.ADULT,
            )
