"""Tests for agb field classification functions"""

# Due to structure of similar classification schemes they may trigger duplicate code.
# => disable for classification files and tests
# pylint: disable=duplicate-code

from typing import List
import pytest

from archeryutils import load_rounds
import archeryutils.classifications as class_funcs


ALL_AGBFIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ]
)


class TestAgbFieldClassificationScores:
    """
    Class to test the field classification scores function.

    Methods
    -------
    test_agb_field_classification_scores_ages()
        test if expected scores returned for different ages
    test_agb_field_classification_scores_genders()
        test if expected scores returned for different genders
    test_agb_field_classification_scores_bowstyles()
        test if expected scores returned for different bowstyles
    test_agb_field_classification_scores_invalid()
        test invalid inputs
    """

    @pytest.mark.parametrize(
        "roundname,age_group,scores_expected",
        [
            (
                "wa_field_24_blue_marked",
                "adult",
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                "50+",
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                "under21",
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                "Under 18",
                [298, 279, 254, 229, 204, 179],
            ),
            (
                "wa_field_24_blue_marked",
                "Under 12",
                [298, 279, 254, 229, 204, 179],
            ),
        ],
    )
    def test_agb_field_classification_scores_ages(
        self,
        roundname: str,
        age_group: str,
        scores_expected: List[int],
    ) -> None:
        """
        Check that field classification returns expected value for a case.
        """
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
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                "female",
                "adult",
                [303, 284, 258, 233, 207, 182],
            ),
            (
                "wa_field_24_blue_marked",
                "male",
                "Under 18",
                [298, 279, 254, 229, 204, 179],
            ),
            (
                "wa_field_24_blue_marked",
                "female",
                "Under 18",
                [251, 236, 214, 193, 172, 151],
            ),
        ],
    )
    def test_agb_field_classification_scores_genders(
        self,
        roundname: str,
        gender: str,
        age_group: str,
        scores_expected: List[int],
    ) -> None:
        """
        Check that field classification returns expected value for a case.
        """
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
                [393, 377, 344, 312, 279, 247],
            ),
            (
                "wa_field_24_red_marked",
                "recurve",
                [338, 317, 288, 260, 231, 203],
            ),
            (
                "wa_field_24_blue_marked",
                "barebow",
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                "traditional",
                [262, 245, 223, 202, 178, 157],
            ),
            (
                "wa_field_24_blue_marked",
                "flatbow",
                [262, 245, 223, 202, 178, 157],
            ),
            (
                "wa_field_24_blue_marked",
                "longbow",
                [201, 188, 171, 155, 137, 121],
            ),
        ],
    )
    def test_agb_field_classification_scores_bowstyles(
        self,
        roundname: str,
        bowstyle: str,
        scores_expected: List[int],
    ) -> None:
        """
        Check that field classification returns expected value for a case.
        """
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
        """
        Check that field classification returns expected value for a case.
        """
        with pytest.raises(
            KeyError,
            match=(
                f"{age_group.lower().replace(' ','')}_{gender.lower()}_{bowstyle.lower()}"
            ),
        ):
            _ = class_funcs.agb_field_classification_scores(
                roundname=roundname,
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )


class TestCalculateAgbFieldClassification:
    """
    Class to test the field classification function.

    Methods
    -------
    test_calculate_agb_field_classification_scores()
        test if expected sanitised groupname returned
    test_calculate_agb_field_classification()
        test if expected full-face roundname returned
    """

    @pytest.mark.parametrize(
        "roundname,score,age_group,bowstyle,class_expected",
        [
            (
                "wa_field_24_red_marked",
                400,
                "adult",
                "compound",
                "Grand Master Bowman",
            ),
            (
                "wa_field_24_red_marked",
                337,
                "50+",
                "recurve",
                "Master Bowman",
            ),
            (
                "wa_field_24_blue_marked",
                306,
                "under21",
                "barebow",
                "Bowman",
            ),
            (
                "wa_field_24_blue_marked",
                177,
                "Under 18",
                "traditional",
                "1st Class",
            ),
            (
                "wa_field_24_blue_marked",
                143,
                "Under 12",
                "flatbow",
                "2nd Class",
            ),
            (
                "wa_field_24_blue_marked",
                96,
                "Under 12",
                "longbow",
                "3rd Class",
            ),
            (
                "wa_field_24_blue_marked",
                1,
                "Under 12",
                "longbow",
                "unclassified",
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
        """
        Check that field classification returns expected value for a few cases.
        """
        # pylint: disable=too-many-arguments
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
                "wa_field_24_blue_marked",
                400,
                "compound",
                "unclassified",
            ),
            (
                "wa_field_24_red_marked",
                337,
                "barebow",
                "unclassified",
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
        """
        Check that field classification returns unclassified for inappropriate rounds.
        """
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
        """
        Check that field classification fails for inappropriate scores.
        """
        with pytest.raises(
            ValueError,
            match=(
                f"Invalid score of {score} for a {roundname}. "
                f"Should be in range 0-{ALL_AGBFIELD_ROUNDS[roundname].max_score()}."
            ),
        ):
            _ = class_funcs.calculate_agb_field_classification(
                roundname=roundname,
                score=score,
                bowstyle="barebow",
                gender="male",
                age_group="adult",
            )
