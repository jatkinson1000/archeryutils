"""
Code for calculating old (pre-2023) Archery GB indoor classifications.

Routine Listings
----------------
calculate_AGB_old_indoor_classification
AGB_old_indoor_classification_scores
"""

# Due to structure of similar classification schemes they may trigger duplicate code.
# => disable for classification files and tests
# pylint: disable=duplicate-code

from typing import TypedDict

from archeryutils import load_rounds
import archeryutils.handicaps as hc
import archeryutils.classifications.classification_utils as cls_funcs


ALL_INDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_indoor.json",
        "WA_indoor.json",
    ]
)


class GroupData(TypedDict):
    """Structure for old AGB Indoor classification data."""

    classes: list[str]
    class_HC: list[int]


def _make_agb_old_indoor_classification_dict() -> dict[str, GroupData]:
    """
    Generate AGB outdoor classification data.

    Generate a dictionary of dictionaries providing handicaps for
    each classification band.

    Parameters
    ----------
    None

    Returns
    -------
    classification_dict : dict of str : dict of str: list
        dictionary indexed on group name (e.g 'adult_female_recurve')
        containing list of handicaps associated with each classification

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    agb_indoor_classes = ["A", "B", "C", "D", "E", "F", "G", "H"]

    # Generate dict of classifications
    # for both bowstyles, for both genders
    compound_male_adult: GroupData = {
        "classes": agb_indoor_classes,
        "class_HC": [5, 12, 24, 37, 49, 62, 73, 79],
    }
    compound_female_adult: GroupData = {
        "classes": agb_indoor_classes,
        "class_HC": [12, 18, 30, 43, 55, 67, 79, 83],
    }
    recurve_male_adult: GroupData = {
        "classes": agb_indoor_classes,
        "class_HC": [14, 21, 33, 46, 58, 70, 80, 85],
    }
    recurve_female_adult: GroupData = {
        "classes": agb_indoor_classes,
        "class_HC": [21, 27, 39, 51, 64, 75, 85, 90],
    }

    classification_dict = {
        cls_funcs.get_groupname("Compound", "Male", "Adult"): compound_male_adult,
        cls_funcs.get_groupname("Compound", "Female", "Adult"): compound_female_adult,
        cls_funcs.get_groupname("Recurve", "Male", "Adult"): recurve_male_adult,
        cls_funcs.get_groupname("Recurve", "Female", "Adult"): recurve_female_adult,
    }

    return classification_dict


agb_old_indoor_classifications = _make_agb_old_indoor_classification_dict()

del _make_agb_old_indoor_classification_dict


def calculate_agb_old_indoor_classification(
    roundname: str,
    score: float,
    bowstyle: str,
    gender: str,
    age_group: str,
) -> str:
    """
    Calculate AGB indoor classification from score.

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
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (pre-2023)

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> class_func.calculate_agb_old_indoor_classification(
    ...     "wa18",
    ...     547,
    ...     "compound",
    ...     "male",
    ...     "adult",
    ... )
    'C'

    """
    # Check score is valid
    if score < 0 or score > ALL_INDOOR_ROUNDS[roundname].max_score():
        raise ValueError(
            f"Invalid score of {score} for a {roundname}. "
            f"Should be in range 0-{ALL_INDOOR_ROUNDS[roundname].max_score()}."
        )

    # Get scores required on this round for each classification
    class_scores = agb_old_indoor_classification_scores(
        roundname,
        bowstyle,
        gender,
        age_group,
    )

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_old_indoor_classifications[groupname]
    class_data = dict(zip(group_data["classes"], class_scores))

    # What is the highest classification this score gets?
    to_del = []
    for classname, classscore in class_data.items():
        if classscore > score:
            to_del.append(classname)
    for del_class in to_del:
        del class_data[del_class]

    # NB No fiddle for Worcester required with this logic...
    # Beware of this later on, however, if we wish to rectify the 'anomaly'

    try:
        classification_from_score = list(class_data.keys())[0]
        return classification_from_score
    except IndexError:
        return "UC"


def agb_old_indoor_classification_scores(
    roundname: str,
    bowstyle: str,
    gender: str,
    age_group: str,
) -> list[int]:
    """
    Calculate AGB indoor classification scores for category.

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
        scores required for each classification in descending order

    References
    ----------
    ArcheryGB Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7

    Examples
    --------
    >>> from archeryutils import classifications as class_func
    >>> class_func.agb_old_indoor_classification_scores(
    ...     "portsmouth",
    ...     "barebow",
    ...     "male",
    ...     "under 12",
    ... )
    [592, 582, 554, 505, 432, 315, 195, 139]

    If a classification cannot be achieved a fill value of `-9999` is returned:

    >>> class_func.agb_old_indoor_classification_scores(
    ...     "worcester",
    ...     "compound",
    ...     "female",
    ...     "adult",
    ... )
    [299, 296, 279, 247, 200, 132, 65, 49]


    """
    # enforce compound scoring
    if bowstyle.lower() in ("compound"):
        roundname = cls_funcs.get_compound_codename(roundname)

    # deal with reduced categories:
    age_group = "Adult"
    if bowstyle.lower() not in ("compound"):
        bowstyle = "Recurve"

    groupname = cls_funcs.get_groupname(bowstyle, gender, age_group)
    group_data = agb_old_indoor_classifications[groupname]

    # Get scores required on this round for each classification
    class_scores = [
        hc.score_for_round(
            ALL_INDOOR_ROUNDS[roundname],
            group_data["class_HC"][i],
            "AGBold",
            rounded_score=True,
        )
        for i, class_i in enumerate(group_data["classes"])
    ]

    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    return int_class_scores
