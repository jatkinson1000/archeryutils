"""
Code for calculating Archery GB indoor classifications.

Routine Listings
----------------
_make_agb_old_indoor_classification_dict
calculate_agb_indoor_classification
agb_indoor_classification_scores
"""
# Due to structure of similar classification schemes they may trigger duplicate code.
# => disable for classification files and tests
# pylint: disable=duplicate-code

from typing import List, Dict, Any
import numpy as np

from archeryutils import load_rounds
from archeryutils.handicaps import handicap_equations as hc_eq
import archeryutils.classifications.classification_utils as cls_funcs


ALL_INDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_indoor.json",
        "WA_indoor.json",
    ]
)


def _make_agb_indoor_classification_dict() -> Dict[str, Dict[str, Any]]:
    """
    Generate new (2023) AGB indoor classification data.

    Generate a dictionary of dictionaries providing handicaps for each
    classification band and a list of prestige rounds for each category from data files.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    None

    Returns
    -------
    classification_dict : dict of str : dict of str: list, list, list
        dictionary indexed on group name (e.g 'adult_female_barebow')
        containing list of handicaps associated with each classification,
        a list of prestige rounds eligible for that group, and a list of
        the maximum distances available to that group

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # For score purposes in classifications we use the full face, not the triple.
    # Option of having triple is handled in get classification function
    # Compound version of rounds is handled below.

    # Read in age group info as list of dicts
    agb_ages = cls_funcs.read_ages_json()
    # Read in bowstyleclass info as list of dicts
    agb_bowstyles = cls_funcs.read_bowstyles_json()
    # Read in gender info as list of dicts
    agb_genders = cls_funcs.read_genders_json()
    # Read in classification names as dict
    agb_classes_info_in = cls_funcs.read_classes_json("agb_indoor")
    agb_classes_in = agb_classes_info_in["classes"]
    agb_classes_in_long = agb_classes_info_in["classes_long"]

    # Generate dict of classifications
    # loop over bowstyles
    # loop over ages
    # loop over genders
    classification_dict = {}
    for bowstyle in agb_bowstyles:
        for gender in agb_genders:
            for age in agb_ages:
                groupname = cls_funcs.get_groupname(
                    bowstyle["bowstyle"], gender, age["age_group"]
                )

                classification_dict[groupname] = {
                    "classes": agb_classes_in,
                    "classes_long": agb_classes_in_long,
                }

                # set step from datum based on age and gender steps required
                delta_hc_age_gender = cls_funcs.get_age_gender_step(
                    gender,
                    age["step"],
                    bowstyle["ageStep_in"],
                    bowstyle["genderStep_in"],
                )

                classification_dict[groupname]["class_HC"] = np.empty(
                    len(agb_classes_in)
                )
                for i in range(len(agb_classes_in)):
                    # Assign handicap for this classification
                    classification_dict[groupname]["class_HC"][i] = (
                        bowstyle["datum_in"]
                        + delta_hc_age_gender
                        + (i - 1) * bowstyle["classStep_in"]
                    )

    return classification_dict


agb_indoor_classifications = _make_agb_indoor_classification_dict()

del _make_agb_indoor_classification_dict


def calculate_agb_indoor_classification(
    roundname: str,
    score: float,
    bowstyle: str,
    gender: str,
    age_group: str,
) -> str:
    """
    Calculate new (2023) AGB indoor classification from score.

    Subroutine to calculate a classification from a score given suitable inputs.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json
    score : int
        numerical score on the round to calculate classification for
    bowstyle : str
        archer's bowstyle under AGB outdoor target rules
    gender : str
        archer's gender under AGB outdoor target rules
    age_group : str
        archer's age group under AGB outdoor target rules

    Returns
    -------
    classification_from_score : str
        the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # Check score is valid
    if score < 0 or score > ALL_INDOOR_ROUNDS[roundname].max_score():
        raise ValueError(
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_INDOOR_ROUNDS[roundname].max_score()}."
        )

    # Get scores required on this round for each classification
    # Enforcing full size face and compound scoring (for compounds)
    all_class_scores = agb_indoor_classification_scores(
        roundname,
        bowstyle,
        gender,
        age_group,
    )

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_indoor_classifications[groupname]
    class_data: Dict[str, Any] = dict(zip(group_data["classes"], all_class_scores))

    # What is the highest classification this score gets?
    # < 0 handles max scores, > score handles higher classifications
    to_del = []
    for classname, classscore in class_data.items():
        if classscore < 0 or classscore > score:
            to_del.append(classname)
    for del_class in to_del:
        del class_data[del_class]

    try:
        classification_from_score = list(class_data.keys())[0]
        return classification_from_score
    except IndexError:
        return "UC"


def agb_indoor_classification_scores(
    roundname: str,
    bowstyle: str,
    gender: str,
    age_group: str,
) -> List[int]:
    """
    Calculate new (2023) AGB indoor classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate ArcheryGB age groups and classifications.

    Parameters
    ----------
    roundname : str
        name of round shot as given by 'codename' in json
    bowstyle : str
        archer's bowstyle under AGB outdoor target rules
    gender : str
        archer's gender under AGB outdoor target rules
    age_group : str
        archer's age group under AGB outdoor target rules

    Returns
    -------
    classification_scores : ndarray
        scores required for each classification band

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7
    """
    # deal with reduced categories:
    if bowstyle.lower() in ("flatbow", "traditional", "asiatic"):
        bowstyle = "Barebow"

    # enforce compound scoring
    if bowstyle.lower() in ("compound"):
        roundname = cls_funcs.get_compound_codename(roundname)

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_indoor_classifications[groupname]

    hc_scheme = "AGB"
    hc_params = hc_eq.HcParams()

    # Get scores required on this round for each classification
    # Enforce full size face
    class_scores = [
        hc_eq.score_for_round(
            ALL_INDOOR_ROUNDS[cls_funcs.strip_spots(roundname)],
            group_data["class_HC"][i],
            hc_scheme,
            hc_params,
            round_score_up=True,
        )
        for i, class_i in enumerate(group_data["classes"])
    ]

    # Make sure that hc.eq.score_for_round did not return array to satisfy mypy
    if any(isinstance(x, np.ndarray) for x in class_scores):
        raise TypeError(
            "score_for_round is attempting to return an array when float expected."
        )
    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    # Handle possibility of gaps in the tables or max scores by checking 1 HC point
    # above current (floored to handle 0.5) and amending accordingly
    for i, (score, handicap) in enumerate(
        zip(int_class_scores, group_data["class_HC"])
    ):
        next_score = hc_eq.score_for_round(
            ALL_INDOOR_ROUNDS[cls_funcs.strip_spots(roundname)],
            np.floor(handicap) + 1,
            hc_scheme,
            hc_params,
            round_score_up=True,
        )
        if next_score == score:
            # If already at max score this classification is impossible
            if score == ALL_INDOOR_ROUNDS[roundname].max_score():
                int_class_scores[i] = -9999
            # If gap in table increase to next score
            # (we assume here that no two classifications are only 1 point apart...)
            else:
                int_class_scores[i] += 1

    return int_class_scores
