"""Tests for field classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds

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
                "adult",
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                "wa_field_24_blue_marked",
                "50+",
                [321, 294, 263, 227, 188, 149, 114, 84, 60],
            ),
            (
                "wa_field_24_blue_marked",
                "Under 21",
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                "wa_field_24_blue_marked",
                "Under 18",
                [305, 275, 241, 203, 164, 127, 94, 68, 48],
            ),
            (
                "wa_field_24_blue_marked",
                "Under 12",
                [224, 185, 146, 111, 82, 58, 41, 28, 19],
            ),
        ],
    )
    def test_agb_field_classification_scores_ages(
        self,
        roundname: str,
        age_group: str,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_field_classification_scores(
            roundname=roundname,
            bowstyle="barebow",
            gender="male",
            age_group=age_group,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "roundname,gender,age_group,scores_expected",
        [
            (
                "wa_field_24_blue_marked",
                "male",
                "adult",
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                "wa_field_24_blue_marked",
                "female",
                "adult",
                [315, 287, 255, 218, 179, 140, 106, 78, 55],
            ),
            (
                "wa_field_24_blue_marked",
                "male",
                "Under 18",
                [305, 275, 241, 203, 164, 127, 94, 68, 48],
            ),
            (
                "wa_field_24_blue_marked",
                "female",
                "Under 18",
                [280, 247, 209, 170, 132, 99, 72, 51, 35],
            ),
        ],
    )
    def test_agb_field_classification_scores_genders(
        self,
        roundname: str,
        gender: str,
        age_group: str,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_field_classification_scores(
            roundname=roundname,
            bowstyle="barebow",
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
                "compound",
                [408, 391, 369, 345, 318, 286, 248, 204, 157],
            ),
            (
                "wa_field_12_red_unmarked",
                "compound",
                [-9999, -9999, -9999, 173, 159, 143, 124, 102, 79],
            ),
            (
                "wa_field_24_red_marked",
                "compound limited",
                [369, 347, 322, 293, 259, 219, 176, 133, 96],
            ),
            (
                "wa_field_24_blue_marked",
                "compound barebow",
                [343, 321, 296, 268, 235, 200, 164, 129, 99],
            ),
            (
                "wa_field_24_red_marked",
                "recurve",
                [369, 343, 314, 279, 237, 189, 139, 96, 62],
            ),
            (
                "wa_field_24_blue_marked",
                "barebow",
                [336, 311, 283, 249, 212, 173, 135, 101, 74],
            ),
            (
                "wa_field_24_blue_marked",
                "traditional",
                [309, 283, 252, 218, 182, 146, 114, 86, 63],
            ),
            (
                "wa_field_24_blue_marked",
                "flatbow",
                [273, 244, 212, 179, 146, 116, 90, 68, 51],
            ),
            (
                "wa_field_24_blue_marked",
                "longbow",
                [241, 209, 176, 143, 114, 88, 67, 49, 36],
            ),
            (
                "wa_field_24_blue_marked",
                "english longbow",
                [241, 209, 176, 143, 114, 88, 67, 49, 36],
            ),
        ],
    )
    def test_agb_field_classification_scores_bowstyles(
        self,
        roundname: str,
        bowstyle: str,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_field_classification_scores(
            roundname=roundname,
            bowstyle=bowstyle,
            gender="male",
            age_group="adult",
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,age_group",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                "wa_field_24_red_marked",
                "invalidbowstyle",
                "male",
                "adult",
            ),
            (
                "wa_field_24_red_marked",
                "recurve",
                "invalidgender",
                "adult",
            ),
            (
                "wa_field_24_blue_marked",
                "barebow",
                "male",
                "invalidage",
            ),
        ],
    )
    def test_agb_field_classification_scores_invalid(
        self,
        roundname: str,
        bowstyle: str,
        gender: str,
        age_group: str,
    ) -> None:
        """Check that field classification returns expected value for a case."""
        with pytest.raises(
            KeyError,
            match=(
                f"{age_group.lower().replace(' ', '')}_"
                f"{gender.lower()}_{bowstyle.lower()}"
            ),
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
                "adult",
                "compound",
                "GMB",
            ),
            (  # Bowman classifications only on 12-target rounds
                "wa_field_12_red_marked",
                200,
                "adult",
                "compound",
                "B1",
            ),
            (  # Archer classifications only on shorter rounds - A1
                "wa_field_24_blue_marked",
                400,
                "adult",
                "compound",
                "A1",
            ),
            (  # Archer classifications only on shorter rounds - A2
                "wa_field_24_yellow_marked",
                400,
                "adult",
                "compound",
                "A2",
            ),
            (  # Archer classifications only on shorter rounds - A3
                "wa_field_24_white_marked",
                400,
                "adult",
                "compound",
                "A3",
            ),
            (
                "wa_field_24_red_marked",
                337,
                "50+",
                "recurve",
                "GMB",
            ),
            (
                "wa_field_24_blue_marked",
                306,
                "under21",
                "barebow",
                "MB",
            ),
            (
                "wa_field_24_red_marked",
                306,
                "under21",
                "barebow",
                "UC",
            ),
            (
                "wa_field_24_blue_marked",
                177,
                "Under 18",
                "traditional",
                "B1",
            ),
            (
                "wa_field_24_red_marked",
                177,
                "Under 18",
                "traditional",
                "UC",
            ),
            (  # Bowman classifications only on 12-target rounds
                "wa_field_12_blue_marked",
                88,
                "Under 18",
                "traditional",
                "B1",
            ),
            (  # Archer classifications only on shorter rounds - Junior
                "wa_field_24_yellow_marked",
                400,
                "Under 18",
                "traditional",
                "A1",
            ),
            (  # Archer classifications only on shorter rounds - Junior
                "wa_field_24_white_marked",
                400,
                "Under 18",
                "traditional",
                "A2",
            ),
            (
                "wa_field_24_blue_marked",
                143,
                "Under 12",
                "flatbow",
                "EMB",
            ),
            (
                "wa_field_24_blue_marked",
                96,
                "Under 12",
                "longbow",
                "EMB",
            ),
            (
                "wa_field_24_blue_marked",
                1,
                "Under 12",
                "longbow",
                "UC",
            ),
            (
                "wa_field_24_blue_marked",
                1,
                "Under 12",
                "english longbow",
                "UC",
            ),
        ],
    )
    def test_calculate_agb_field_classification(
        self,
        roundname: str,
        score: float,
        age_group: str,
        bowstyle: str,
        class_expected: str,
    ) -> None:
        """Check that field classification returns expected value for a few cases."""
        class_returned = class_funcs.calculate_agb_field_classification(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender="male",
            age_group=age_group,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "roundname,score,bowstyle,class_expected",
        [
            (
                "wa_field_24_red_unmarked",
                400,
                "english longbow",
                "UC",
            ),
            (
                "wa_field_24_red_marked",
                337,
                "barebow",
                "UC",
            ),
        ],
    )
    def test_calculate_agb_field_classification_invalid_rounds(
        self,
        roundname: str,
        score: float,
        bowstyle: str,
        class_expected: str,
    ) -> None:
        """Check field classification returns unclassified for inappropriate rounds."""
        class_returned = class_funcs.calculate_agb_field_classification(
            roundname=roundname,
            score=score,
            bowstyle=bowstyle,
            gender="male",
            age_group="adult",
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
                bowstyle="barebow",
                gender="male",
                age_group="adult",
            )
