"""Tests for agb indoor classification functions."""

import pytest

import archeryutils.classifications as class_funcs
from archeryutils import load_rounds

ALL_INDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_indoor.json",
        "WA_indoor.json",
    ],
)


class TestAgbIndoorClassificationScores:
    """
    Tests for the agb indoor classification scores function.

    This will implicitly check the dictionary creation.
    Provided sufficient options are covered across bowstyles, genders, and ages.
    """

    @pytest.mark.parametrize(
        "age_group,scores_expected",
        [
            (
                "adult",
                [378, 437, 483, 518, 546, 566, 582, 593],
            ),
            (
                "50+",
                [316, 387, 444, 488, 522, 549, 569, 583],
            ),
            (
                "under21",
                [316, 387, 444, 488, 522, 549, 569, 583],
            ),
            (
                "Under 18",
                [250, 326, 395, 450, 493, 526, 552, 571],
            ),
            (
                "Under 16",
                [187, 260, 336, 403, 457, 498, 530, 555],
            ),
            (
                "Under 15",
                [134, 196, 271, 346, 411, 463, 503, 534],
            ),
            (
                "Under 14",
                [92, 141, 206, 281, 355, 419, 469, 508],
            ),
            (
                "Under 12",
                [62, 98, 149, 215, 291, 364, 426, 475],
            ),
        ],
    )
    def test_agb_indoor_classification_scores_ages(
        self,
        age_group: str,
        scores_expected: list[int],
    ) -> None:
        """Check that  classification returns expected value for a case."""
        scores = class_funcs.agb_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle="recurve",
            gender="male",
            age_group=age_group,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "age_group,scores_expected",
        [
            (
                "adult",
                [331, 399, 454, 496, 528, 553, 572, 586],
            ),
            (
                "Under 16",
                [145, 211, 286, 360, 423, 472, 510, 539],
            ),
            (
                "Under 15",
                [134, 196, 271, 346, 411, 463, 503, 534],
            ),
            (
                "Under 12",
                [62, 98, 149, 215, 291, 364, 426, 475],
            ),
        ],
    )
    def test_agb_indoor_classification_scores_genders(
        self,
        age_group: str,
        scores_expected: list[int],
    ) -> None:
        """
        Check that indoor classification returns expected value for a case.

        Male equivalents already checked above.
        Also checks that compound rounds are being enforced.
        """
        scores = class_funcs.agb_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle="recurve",
            gender="female",
            age_group=age_group,
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "bowstyle,scores_expected",
        [
            (
                "compound",
                [472, 508, 532, 549, 560, 571, 583, 594],
            ),
            (
                "barebow",
                [331, 387, 433, 472, 503, 528, 549, 565],
            ),
            (
                "longbow",
                [127, 178, 240, 306, 369, 423, 466, 501],
            ),
            (
                "english longbow",
                [127, 178, 240, 306, 369, 423, 466, 501],
            ),
        ],
    )
    def test_agb_indoor_classification_scores_bowstyles(
        self,
        bowstyle: str,
        scores_expected: list[int],
    ) -> None:
        """Check that indoor classification returns expected value for a case."""
        scores = class_funcs.agb_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle=bowstyle,
            gender="male",
            age_group="adult",
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "bowstyle,scores_expected",
        [
            (
                "flatbow",
                [331, 387, 433, 472, 503, 528, 549, 565],
            ),
            (
                "traditional",
                [331, 387, 433, 472, 503, 528, 549, 565],
            ),
            (
                "asiatic",
                [331, 387, 433, 472, 503, 528, 549, 565],
            ),
        ],
    )
    def test_agb_indoor_classification_scores_nonbowstyles(
        self,
        bowstyle: str,
        scores_expected: list[int],
    ) -> None:
        """Check that barebow scores returned for valid but non-indoor styles."""
        scores = class_funcs.agb_indoor_classification_scores(
            roundname="portsmouth",
            bowstyle=bowstyle,
            gender="male",
            age_group="adult",
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "roundname,scores_expected",
        [
            (
                "portsmouth_triple",
                [472, 508, 532, 549, 560, 571, 583, 594],
            ),
            (
                "worcester_5_centre",
                [217, 246, 267, 283, 294, 300, -9999, -9999],
            ),
            (
                "vegas_300_triple",
                [201, 230, 252, 269, 281, 290, 297, 300],
            ),
        ],
    )
    def test_agb_indoor_classification_scores_triple_faces(
        self,
        roundname: str,
        scores_expected: list[int],
    ) -> None:
        """
        Check that indoor classification returns single face scores only.

        Includes check that Worcester returns null above max score.
        """
        scores = class_funcs.agb_indoor_classification_scores(
            roundname=roundname,
            bowstyle="compound",
            gender="male",
            age_group="adult",
        )

        assert scores == scores_expected[::-1]

    @pytest.mark.parametrize(
        "roundname,bowstyle,gender,age_group",
        # Check all systems, different distances, negative and large handicaps.
        [
            (
                "portsmouth",
                "invalidbowstyle",
                "male",
                "adult",
            ),
            (
                "portsmouth",
                "recurve",
                "invalidgender",
                "adult",
            ),
            (
                "portsmouth",
                "barebow",
                "male",
                "invalidage",
            ),
        ],
    )
    def test_agb_indoor_classification_scores_invalid(
        self,
        roundname: str,
        bowstyle: str,
        gender: str,
        age_group: str,
    ) -> None:
        """Check that indoor classification returns expected value for a case."""
        with pytest.raises(
            KeyError,
            match=(
                f"{age_group.lower().replace(' ','')}_"
                f"{gender.lower()}_{bowstyle.lower()}"
            ),
        ):
            _ = class_funcs.agb_indoor_classification_scores(
                roundname=roundname,
                bowstyle=bowstyle,
                gender=gender,
                age_group=age_group,
            )

    def test_agb_indoor_classification_scores_invalid_round(
        self,
    ) -> None:
        """Check that indoor classification raises error for invalid round."""
        with pytest.raises(
            KeyError,
            match=("invalid_roundname"),
        ):
            _ = class_funcs.agb_indoor_classification_scores(
                roundname="invalid_roundname",
                bowstyle="barebow",
                gender="female",
                age_group="adult",
            )


class TestCalculateAgbIndoorClassification:
    """Tests for the indoor classification function."""

    @pytest.mark.parametrize(
        "score,age_group,bowstyle,class_expected",
        [
            (
                594,  # 1 above GMB
                "adult",
                "compound",
                "I-GMB",
            ),
            (
                582,  # 1 below GMB
                "50+",
                "recurve",
                "I-MB",
            ),
            (
                520,  # midway to MB
                "under21",
                "barebow",
                "I-B1",
            ),
            (
                551,  # 1 below
                "Under 18",
                "recurve",
                "I-B1",
            ),
            (
                526,  # boundary value
                "Under 18",
                "recurve",
                "I-B1",
            ),
            (
                449,  # Boundary
                "Under 12",
                "compound",
                "I-B2",
            ),
            (
                40,  # Midway
                "Under 12",
                "longbow",
                "I-A1",
            ),
            (
                12,  # On boundary
                "Under 12",
                "longbow",
                "UC",
            ),
            (
                1,
                "Under 12",
                "english longbow",
                "UC",
            ),
        ],
    )
    def test_calculate_agb_indoor_classification(
        self,
        score: float,
        age_group: str,
        bowstyle: str,
        class_expected: str,
    ) -> None:
        """Check that indoor classification returns expected value for a few cases."""
        class_returned = class_funcs.calculate_agb_indoor_classification(
            score=score,
            roundname="portsmouth",
            bowstyle=bowstyle,
            gender="male",
            age_group=age_group,
        )

        assert class_returned == class_expected

    def test_calculate_agb_indoor_classification_invalid_round(
        self,
    ) -> None:
        """Check indoor classification returns unclassified for inappropriate rounds."""
        with pytest.raises(
            KeyError,
            match=("invalid_roundname"),
        ):
            _ = class_funcs.calculate_agb_indoor_classification(
                score=400,
                roundname="invalid_roundname",
                bowstyle="recurve",
                gender="male",
                age_group="adult",
            )

    @pytest.mark.parametrize("score", [1000, 601, -1, -100])
    def test_calculate_agb_indoor_classification_invalid_scores(
        self,
        score: float,
    ) -> None:
        """Check that indoor classification fails for inappropriate scores."""
        with pytest.raises(
            ValueError,
            match=(
                f"Invalid score of {score} for a portsmouth. "
                f"Should be in range 0-{ALL_INDOOR_ROUNDS['portsmouth'].max_score()}."
            ),
        ):
            _ = class_funcs.calculate_agb_indoor_classification(
                score=score,
                roundname="portsmouth",
                bowstyle="barebow",
                gender="male",
                age_group="adult",
            )
