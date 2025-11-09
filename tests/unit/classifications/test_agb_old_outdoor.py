"""Tests for old agb outdoor classification functions."""

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

# wa1440_90 recurve mens
# GMB* 	1259
# MB* 	1190
# BM 	1065
# 1st 	885
# 2nd 	716
# 3rd 	481

# wa1440_70 recurve womens
# GMB* 	1242
# MB* 	1169
# BM 	1037
# 1st 	817
# 2nd 	602
# 3rd 	364

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
