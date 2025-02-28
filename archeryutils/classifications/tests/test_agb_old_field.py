"""Tests for old (pre-2025) agb field classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders
from archeryutils.rounds import Pass, Round

ALL_AGBFIELD_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "WA_field.json",
    ],
)


class TestAgbOldFieldClassificationScores:
    """Tests for the field classification scores function."""

    @pytest.mark.parametrize(
        "archery_round,age_group,scores_expected",
        [
            (
                "wa_field_24_blue_marked",
                AGB_ages.AGE_ADULT,
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_ages.AGE_UNDER_18,
                [298, 279, 254, 229, 204, 179],
            ),
        ],
    )
    def test_agb_old_field_classification_scores_ages(
        self,
        archery_round: str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_old_field_classification_scores(
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
                "wa_field_24_blue_marked",
                AGB_ages.AGE_50_PLUS,
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_ages.AGE_UNDER_21,
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_ages.AGE_UNDER_18,
                [298, 279, 254, 229, 204, 179],
            ),
            # Check adult passes through coaxing unchanged
            (
                "wa_field_24_blue_marked",
                AGB_ages.AGE_ADULT,
                [328, 307, 279, 252, 224, 197],
            ),
        ],
    )
    def test_agb_old_field_classification_scores_coaxed_ages(
        self,
        archery_round: str,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a coaxed age."""
        coaxed_vals = class_funcs.coax_old_field_group(
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )
        scores = class_funcs.agb_old_field_classification_scores(
            archery_round=archery_round,
            **coaxed_vals,
        )

        assert scores == scores_expected

    @pytest.mark.parametrize(
        "archery_round,gender,age_group,scores_expected",
        [
            (
                "wa_field_24_blue_marked",
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_genders.FEMALE,
                AGB_ages.AGE_ADULT,
                [303, 284, 258, 233, 207, 182],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_genders.MALE,
                AGB_ages.AGE_UNDER_18,
                [298, 279, 254, 229, 204, 179],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_genders.FEMALE,
                AGB_ages.AGE_UNDER_18,
                [251, 236, 214, 193, 172, 151],
            ),
        ],
    )
    def test_agb_old_field_classification_scores_genders(
        self,
        archery_round: str,
        gender: AGB_genders,
        age_group: AGB_ages,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_old_field_classification_scores(
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
                "wa_field_24_red_marked",
                AGB_bowstyles.COMPOUND,
                [393, 377, 344, 312, 279, 247],
            ),
            (
                "wa_field_24_red_marked",
                AGB_bowstyles.RECURVE,
                [338, 317, 288, 260, 231, 203],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.BAREBOW,
                [328, 307, 279, 252, 224, 197],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.TRADITIONAL,
                [262, 245, 223, 202, 178, 157],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.FLATBOW,
                [262, 245, 223, 202, 178, 157],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.LONGBOW,
                [201, 188, 171, 155, 137, 121],
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.ENGLISHLONGBOW,
                [201, 188, 171, 155, 137, 121],
            ),
        ],
    )
    def test_agb_old_field_classification_scores_bowstyles(
        self,
        archery_round: str,
        bowstyle: AGB_bowstyles,
        scores_expected: list[int],
    ) -> None:
        """Check that field classification returns expected value for a case."""
        scores = class_funcs.agb_old_field_classification_scores(
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
                "wa_field_24_red_marked",
                "invalidbowstyle",
                AGB_genders.MALE,
                AGB_ages.AGE_ADULT,
                (
                    "invalidbowstyle is not a recognised bowstyle for old field "
                    "classifications. Please select from "
                    "`AGB_bowstyles.COMPOUND|RECURVE|BAREBOW|ENGLISHLONGBOW|TRADITIONAL"
                    "|FLATBOW|COMPOUNDLIMITED|COMPOUNDBAREBOW`."
                ),
            ),
            (
                "wa_field_24_red_marked",
                AGB_bowstyles.RECURVE,
                "invalidgender",
                AGB_ages.AGE_ADULT,
                (
                    "invalidgender is not a recognised gender group for old field "
                    "classifications. Please select from `archeryutils.AGB_genders`."
                ),
            ),
            (
                "wa_field_24_blue_marked",
                AGB_bowstyles.BAREBOW,
                AGB_genders.MALE,
                "invalidage",
                (
                    "invalidage is not a recognised age group for old field "
                    "classifications. "
                    "Please select from `AGB_ages.AGE_ADULT|AGE_UNDER_18`."
                ),
            ),
        ],
    )
    def test_agb_old_field_classification_scores_invalid(
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
            _ = class_funcs.agb_old_field_classification_scores(
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
                "This round is not recognised for the purposes of "
                "field classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            my_round = Round(
                "Some Roundname",
                [Pass.at_target(36, "10_zone", 122, 70.0)],
            )
            _ = class_funcs.agb_field_classification_scores(
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
                "This round is not recognised for the purposes of "
                "field classification.\n"
                "Please select an appropriate option using `archeryutils.load_rounds`."
            ),
        ):
            _ = class_funcs.agb_field_classification_scores(
                archery_round="invalid_roundname",
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.FEMALE,
                age_group=AGB_ages.AGE_ADULT,
            )

    def test_agb_field_classification_scores_string_round(
        self,
    ) -> None:
        """Check that field classification can process a string roundname."""
        scores = class_funcs.agb_field_classification_scores(
            archery_round="wa_field_24_blue_marked",
            bowstyle=AGB_bowstyles.BAREBOW,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert scores == [336, 311, 283, 249, 212, 173, 135, 101, 74]


class TestCalculateOldAgbFieldClassification:
    """Tests for the field classification function."""

    @pytest.mark.parametrize(
        "archery_round,score,age_group,bowstyle,class_expected",
        [
            (
                "wa_field_24_red_marked",
                400,
                AGB_ages.AGE_ADULT,
                AGB_bowstyles.COMPOUND,
                "GMB",
            ),
            (
                "wa_field_24_blue_marked",
                177,
                AGB_ages.AGE_UNDER_18,
                AGB_bowstyles.TRADITIONAL,
                "1C",
            ),
        ],
    )
    def test_calculate_agb_old_field_classification(
        self,
        archery_round: str,
        score: float,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that field classification returns expected value for a few cases."""
        # pylint: disable=too-many-arguments
        class_returned = class_funcs.calculate_agb_old_field_classification(
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
                "wa_field_24_red_marked",
                337,
                AGB_ages.AGE_50_PLUS,
                AGB_bowstyles.RECURVE,
                "MB",
            ),
            (
                "wa_field_24_blue_marked",
                306,
                AGB_ages.AGE_UNDER_21,
                AGB_bowstyles.BAREBOW,
                "B",
            ),
            (
                "wa_field_24_blue_marked",
                143,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.FLATBOW,
                "2C",
            ),
            (
                "wa_field_24_blue_marked",
                96,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "3C",
            ),
            (
                "wa_field_24_blue_marked",
                1,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.LONGBOW,
                "UC",
            ),
            (
                "wa_field_24_blue_marked",
                1,
                AGB_ages.AGE_UNDER_12,
                AGB_bowstyles.ENGLISHLONGBOW,
                "UC",
            ),
        ],
    )
    def test_calculate_agb_old_field_classification_coaxed_ages(
        self,
        archery_round: str,
        score: float,
        age_group: AGB_ages,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check that field classification returns expected value for a coaxed case."""
        coaxed_vals = class_funcs.coax_old_field_group(
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=age_group,
        )
        class_returned = class_funcs.calculate_agb_old_field_classification(
            archery_round=archery_round,
            score=score,
            **coaxed_vals,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "archery_round,score,bowstyle,class_expected",
        [
            (
                "wa_field_24_blue_marked",
                400,
                AGB_bowstyles.COMPOUND,
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
    def test_calculate_agb_old_field_classification_invalid_rounds(
        self,
        archery_round: str,
        score: float,
        bowstyle: AGB_bowstyles,
        class_expected: str,
    ) -> None:
        """Check field classification returns unclassified for inappropriate rounds."""
        class_returned = class_funcs.calculate_agb_old_field_classification(
            archery_round=archery_round,
            score=score,
            bowstyle=bowstyle,
            gender=AGB_genders.MALE,
            age_group=AGB_ages.AGE_ADULT,
        )

        assert class_returned == class_expected

    @pytest.mark.parametrize(
        "archery_round,score",
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
    def test_calculate_agb_old_field_classification_invalid_scores(
        self,
        archery_round: str,
        score: float,
    ) -> None:
        """Check that field classification fails for inappropriate scores."""
        with pytest.raises(
            ValueError,
            match=(
                f"Invalid score of {score} for a "
                f"{ALL_AGBFIELD_ROUNDS[archery_round].name}. "
                f"Should be in range "
                f"0-{ALL_AGBFIELD_ROUNDS[archery_round].max_score()}."
            ),
        ):
            _ = class_funcs.calculate_agb_old_field_classification(
                score=score,
                archery_round=archery_round,
                bowstyle=AGB_bowstyles.BAREBOW,
                gender=AGB_genders.MALE,
                age_group=AGB_ages.AGE_ADULT,
            )
