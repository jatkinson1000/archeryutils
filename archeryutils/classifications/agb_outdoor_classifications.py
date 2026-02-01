"""
Code for calculating Archery GB outdoor classifications.

Routine Listings
----------------
calculate_agb_outdoor_classification
agb_outdoor_classification_scores
"""

import itertools
from typing import Any, Literal, Tuple, TypedDict, cast

import numpy as np
import numpy.typing as npt

import archeryutils.classifications.classification_utils as cls_funcs
import archeryutils.handicaps as hc
from archeryutils import load_rounds
from archeryutils.classifications.AGB_data import AGB_ages, AGB_bowstyles, AGB_genders
from archeryutils.rounds import Round

ALL_OUTDOOR_ROUNDS = load_rounds.read_json_to_round_dict(
    [
        "AGB_outdoor_imperial.json",
        "AGB_outdoor_metric.json",
        "WA_outdoor.json",
    ],
)

outdoor_bowstyles = (
    AGB_bowstyles.COMPOUND
    | AGB_bowstyles.RECURVE
    | AGB_bowstyles.BAREBOW
    | AGB_bowstyles.LONGBOW
)


class GroupData(TypedDict):
    """Structure for AGB Outdoor classification data."""

    classes: list[str]
    max_distances: list[float]
    classes_long: list[str]
    class_HC: npt.NDArray[np.float64]
    min_dists: npt.NDArray[np.float64]
    prestige_rounds: list[str]


def _get_outdoor_groupname(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> str:
    """
    Wrap function to generate string id for a particular category with outdoor guards.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB outdoor target rules
    gender : AGB_genders
        archer's gender under AGB outdoor target rules
    age_group : AGB_ages
        archer's age group under AGB outdoor target rules

    Returns
    -------
    groupname : str
        single str id for this category
    """
    if bowstyle not in AGB_bowstyles or bowstyle not in outdoor_bowstyles:
        msg = (
            f"{bowstyle} is not a recognised bowstyle for outdoor classifications. "
            f"Please select from `{outdoor_bowstyles}`."
        )
        raise ValueError(msg)
    if gender not in AGB_genders:
        msg = (
            f"{gender} is not a recognised gender group for outdoor classifications. "
            "Please select from `archeryutils.AGB_genders`."
        )
        raise ValueError(msg)
    if age_group not in AGB_ages:
        msg = (
            f"{age_group} is not a recognised age group for outdoor classifications. "
            "Please select from `archeryutils.AGB_ages`."
        )
        raise ValueError(msg)
    return cls_funcs.get_groupname(bowstyle, gender, age_group)


def coax_outdoor_group(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
) -> cls_funcs.AGBCategory:
    """
    Coax category not conforming to outdoor classification rules to one that does.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        archer's bowstyle
    gender : AGB_genders
        archer's gender under AGB
    age_group : AGB_ages
        archer's age group

    Returns
    -------
    dict[str, AGB_bowstyles | AGB_genders | AGB_ages]
        dict of archer's bowstyle, gender, and age_group under AGB coaxed to outdoor
        target rules
    """
    if bowstyle in (AGB_bowstyles.FLATBOW | AGB_bowstyles.TRADITIONAL):
        coax_bowstyle = AGB_bowstyles.BAREBOW
    elif bowstyle in (AGB_bowstyles.COMPOUNDLIMITED | AGB_bowstyles.COMPOUNDBAREBOW):
        coax_bowstyle = AGB_bowstyles.COMPOUND
    else:
        coax_bowstyle = bowstyle

    coax_gender = gender

    coax_age_group = age_group

    return {
        "bowstyle": coax_bowstyle,
        "gender": coax_gender,
        "age_group": coax_age_group,
    }


def _make_agb_outdoor_classification_dict() -> dict[str, GroupData]:
    """
    Generate AGB outdoor classification data.

    Generate a dictionary of dictionaries providing handicaps for each
    classification band and a list prestige rounds for each category from data files.
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
    # Read in age group info as list of dicts
    agb_age_data = cls_funcs.read_ages_json()
    # Read in bowstyleclass info as list of dicts
    agb_bowstyle_data = cls_funcs.read_bowstyles_json()
    # Read in classification names as dict
    agb_classes_info_out = cls_funcs.read_classes_json("agb_outdoor")
    agb_classes_out = agb_classes_info_out["classes"]
    agb_classes_out_long = agb_classes_info_out["classes_long"]

    # Generate dict of classifications
    # loop over all bowstyles, genders, ages
    classification_dict = {}
    for bowstyle, gender, age in itertools.product(
        outdoor_bowstyles, AGB_genders, AGB_ages
    ):
        # Generate groupname
        # The following satisfies mypy that names are all valid strings
        # Cannot currently be reached, so ignore for coverage
        if gender.name is None:  # pragma: no cover
            errmsg = f"Gender {gender} does not have a name."
            raise ValueError(errmsg)
        if age.name is None:  # pragma: no cover
            errmsg = f"Age {age} does not have a name."
            raise ValueError(errmsg)
        if bowstyle.name is None:  # pragma: no cover
            errmsg = f"Bowstyle {bowstyle} does not have a name."
            raise ValueError(errmsg)
        groupname = _get_outdoor_groupname(bowstyle, gender, age)

        # Get max dists for category from json file data
        # Use metres as corresponding yards >= metric
        gender_key = cast(Literal["male", "female"], gender.name.lower())
        max_dists = agb_age_data[age.name][gender_key]

        # set step from datum based on age and gender steps required
        delta_hc_age_gender = cls_funcs.get_age_gender_step(
            gender,
            agb_age_data[age.name]["step"],
            agb_bowstyle_data[bowstyle.name]["ageStep_out"],
            agb_bowstyle_data[bowstyle.name]["genderStep_out"],
        )

        # set handicap threshold values for all classifications in the category
        class_hc = (
            agb_bowstyle_data[bowstyle.name]["datum_out"]
            + delta_hc_age_gender
            + (np.arange(len(agb_classes_out)) - 2)
            * agb_bowstyle_data[bowstyle.name]["classStep_out"]
        ).astype(np.float64)

        # get minimum distances to be shot for all classifications in the category
        min_dists = _assign_min_dist(
            gender=gender,
            age_group=age,
            max_dists=max_dists,
        )

        # Assign prestige rounds for the category
        prestige_rounds = _assign_outdoor_prestige(
            bowstyle=bowstyle,
            age=age,
            gender=gender,
            max_dists=max_dists,
        )

        groupdata: GroupData = {
            "classes": agb_classes_out,
            "max_distances": max_dists,
            "classes_long": agb_classes_out_long,
            "class_HC": class_hc,
            "min_dists": min_dists,
            "prestige_rounds": prestige_rounds,
        }

        classification_dict[groupname] = groupdata

    return classification_dict


def _assign_min_dist(
    gender: AGB_genders,
    age_group: AGB_ages,
    max_dists: list[float],
) -> npt.NDArray[np.float64]:
    """
    Assign appropriate minimum distance required for a category and classification.

    Appropriate for 2023 ArcheryGB age groups and classifications.
    Anything B1 and beyond requires max distance for men U16 and older
    Anything B2 and beyond requires max distance for women, and men U15 and younger
    Then step down a distance with each classification

    Parameters
    ----------
    gender : str
        string defining gender
    age_group : str,
        string defining age group
    max_dists: List[float]
        list of integers defining the maximum distances for category

    Returns
    -------
    min_dists : array of int
        minimum distance [m] required by category for each classification (EMB -> A3)

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    """
    # List of maximum distances for use in assigning maximum distance [metres]
    # Use metres because corresponding yards distances are >= metric ones
    dists = [90, 70, 60, 50, 40, 30, 20, 15]

    max_dist_index = dists.index(np.min(max_dists))

    # Age group trickery:
    # U15 males and younger step down for B2 and below to align with female scores/hcs
    if (
        gender is AGB_genders.MALE
        and age_group not in AGB_ages.UNDER_15 | AGB_ages.UNDER_14 | AGB_ages.UNDER_12
    ):
        idxs = np.array([0, 0, 0, 0, 1, 2, 3, 4, 5])

    # All other categories require max dist for B1 and B2 then step down
    else:
        idxs = np.array([0, 0, 0, 0, 0, 1, 2, 3, 4])

    # Extract relevant distances for each classification from the dists array
    return np.take(dists, idxs + max_dist_index, mode="clip")


def _assign_outdoor_prestige(
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age: AGB_ages,
    max_dists: list[float],
) -> list[str]:
    """
    Assign appropriate outdoor prestige rounds for a category.

    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    bowstyle : AGB_bowstyles
        enum defining bowstyle
    gender : AGB_genders
        enum defining gender
    age : AGB_ages,
        enum defining age group
    max_dists: List[int]
        list of integers defining the maximum distances for category in [m] and [yds]

    Returns
    -------
    prestige_rounds : list of str
        list of perstige rounds for category defined by inputs

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)
    """
    # Lists of prestige rounds defined by 'codename' of 'Round' class
    # WARNING: do not change these without also addressing the prestige round code.
    prestige_imperial = [
        "york",
        "hereford",
        "bristol_i",
        "bristol_ii",
        "bristol_iii",
        "bristol_iv",
        "bristol_v",
    ]
    prestige_metric = [
        "wa1440_90",
        "wa1440_90_small",
        "wa1440_70",
        "wa1440_70_small",
        "wa1440_60",
        "wa1440_60_small",
        "metric_i",
        "metric_ii",
        "metric_iii",
        "metric_iv",
        "metric_v",
    ]
    prestige_720 = [
        "wa720_70",
        "wa720_60",
        "metric_122_50",
        "wa720_40",
        "metric_122_40",
        "metric_122_30",
    ]
    prestige_720_compound = [
        "wa720_50_c",
        "metric_80_50",
        "wa720_40_c",
        "metric_80_40",
        "metric_80_30",
    ]
    prestige_720_barebow = [
        "wa720_50_b",
        "metric_122_50",
        "wa720_40",
        "metric_122_40",
        "wa720_30_b",
        "metric_122_30",
    ]

    # Assign prestige rounds for the category
    #  - check bowstyle, distance, and age
    prestige_rounds = []
    distance_check: list[str] = []

    # 720 rounds - bowstyle dependent
    if bowstyle is AGB_bowstyles.COMPOUND:
        # Everyone gets the 'adult' 720
        prestige_rounds.extend(prestige_720_compound[0:2])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720_compound[2:]

        # Additional fix for U15 who get the 40m round
        # By extension this also applies to U14 and U12 (though also covered by dist)
        if age in AGB_ages.UNDER_15 | AGB_ages.UNDER_14 | AGB_ages.UNDER_12:
            prestige_rounds.extend(prestige_720_compound[2:4])  # 40m C

    elif bowstyle is AGB_bowstyles.BAREBOW:
        # Everyone gets the 'adult' 720
        prestige_rounds.append(prestige_720_barebow[0])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720_barebow[1:]

        # Additional fix for U15 who get the 30m round
        # By extension they also get the 40m and this also applies to U14 and U12
        if age in AGB_ages.UNDER_15 | AGB_ages.UNDER_14 | AGB_ages.UNDER_12:
            prestige_rounds.extend(prestige_720_barebow[2:])  # 40m and 30m B

    else:
        # Everyone gets the 'adult' 720
        prestige_rounds.append(prestige_720[0])
        # Check rest for junior eligible shorter rounds
        distance_check = distance_check + prestige_720[1:]

        # Additional fix for U15 who get the 40m round
        # By extension this also applies to U14 and U12 (though also covered by dist)
        if age in AGB_ages.UNDER_15 | AGB_ages.UNDER_14 | AGB_ages.UNDER_12:
            prestige_rounds.extend(prestige_720[3:5])  # 40m

        # Additional fix for Male 50+, U18, and U16 recurve/longbow
        if gender is AGB_genders.MALE:
            if age in AGB_ages.OVER_50 | AGB_ages.UNDER_18:
                prestige_rounds.append(prestige_720[1])  # 60m
            elif age is AGB_ages.UNDER_16:
                prestige_rounds.append(prestige_720[2])  # 50m

    # Imperial and 1440 rounds - Check based on distance
    distance_check = distance_check + prestige_imperial
    distance_check = distance_check + prestige_metric

    # Check all other rounds based on distance
    for roundname in distance_check:
        if ALL_OUTDOOR_ROUNDS[roundname].max_distance().value >= np.min(max_dists):
            prestige_rounds.append(roundname)

    return prestige_rounds


agb_outdoor_classifications = _make_agb_outdoor_classification_dict()

del _make_agb_outdoor_classification_dict


def _check_round_eligibility(archery_round: Round | str) -> Tuple[Round, str]:
    """
    Check round is eligible for outdoor classifications.

    Parameters
    ----------
    archery_round : Round | str
        an archeryutils Round object as suitable for this scheme
        alternatively the round codename as a str can be used

    Returns
    -------
    archery_round : Round
        an archeryutils Round from the value passed in
    roundname : str
        codename of the round as it appears in the rounds dict

    Raises
    ------
    ValueError
        If requested round is not in the rounds dict for this scheme

    """
    if isinstance(archery_round, str) and archery_round in ALL_OUTDOOR_ROUNDS:
        roundname = archery_round
        archery_round = ALL_OUTDOOR_ROUNDS[roundname]
    elif (
        isinstance(archery_round, Round)
        and archery_round in ALL_OUTDOOR_ROUNDS.values()
    ):
        # Get string key for this round:
        roundname = list(ALL_OUTDOOR_ROUNDS.keys())[
            list(ALL_OUTDOOR_ROUNDS.values()).index(archery_round)
        ]
    else:
        error = (
            "This round is not recognised for the purposes of outdoor classification.\n"
            "Please select an appropriate option using `archeryutils.load_rounds`."
        )
        raise ValueError(error)

    return archery_round, roundname


def calculate_agb_outdoor_classification(  # noqa: PLR0913 Too many arguments
    score: float,
    archery_round: Round | str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
    strict_rounds: bool = True,
    strict_distance: bool = True,
) -> str:
    """
    Calculate AGB outdoor classification from score.

    Calculate a classification from a score given suitable inputs.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    score : int
        numerical score on the round to calculate classification for
    archery_round : Round | str
        an archeryutils Round object as suitable for this scheme
        alternatively the round codename as a str can be used (provided strict_rounds)
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB outdoor target rules
    gender : AGB_genders
        archer's gender under AGB outdoor target rules
    age_group : AGB_ages
        archer's age group under AGB outdoor target rules
    strict_rounds : bool, default=True
        Whether to enforce valid AGB outdoor rounds and apply prestige rounds rules.
        If False then `archery_round` must be of type `Round` for explicit clarity.
        Prestige rounds will no longer default to allow MB classifications and any
        max-distance rounds will return MB-tier classifications.
    strict_distance : bool, default=True
        Whether to enforce age-dependent distance restrictions

    Returns
    -------
    classification_from_score : str
        abbreviation of the classification appropriate for this score

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    Raises
    ------
    ValueError
        If requested round is not valid for this scheme (when strict_rounds enabled)
        If an invalid score for the requested round is provided
    TypeError
        If archery_round is passed as a string when strict_rounds disabled

    Examples
    --------
    >>> from archeryutils import classifications as cf
    >>> from archeryutils import load_rounds
    >>> agb_outdoor = load_rounds.AGB_outdoor_imperial
    >>> cf.calculate_agb_outdoor_classification(
    ...     858,
    ...     agb_outdoor.hereford,
    ...     cf.AGB_bowstyles.RECURVE,
    ...     cf.AGB_genders.FEMALE,
    ...     cf.AGB_ages.UNDER_18,
    ... )
    'B1'

    """
    if strict_rounds:
        archery_round, _ = _check_round_eligibility(archery_round)
    elif isinstance(archery_round, str):
        msg = (
            "strict_rounds is False so archery_round must be explicitly specified as "
            "a Round type instead of a string."
        )
        raise TypeError(msg)

    # Check score is valid
    if score < 0 or score > archery_round.max_score():
        msg = (
            f"Invalid score of {score} for a {archery_round.name}. "
            f"Should be in range 0-{archery_round.max_score()}."
        )
        raise ValueError(msg)

    # Get scores required on this round for each classification
    # Enforcing full size face and compound scoring (for compounds)
    all_class_scores = agb_outdoor_classification_scores(
        archery_round,
        bowstyle,
        gender,
        age_group,
        strict_rounds=strict_rounds,
        strict_distance=strict_distance,
    )

    groupname = _get_outdoor_groupname(bowstyle, gender, age_group)
    group_data = agb_outdoor_classifications[groupname]
    class_data = dict(zip(group_data["classes"], all_class_scores, strict=True))

    # Of the classes available, what is the highest classification this score gets?
    # < 0 handles invalid classes & max scores, > score handles higher classifications
    for classname, classscore in class_data.items():
        if classscore < 0 or classscore > score:
            continue
        else:
            return classname
    return "UC"


def agb_outdoor_classification_scores(  # noqa:PLR0912
    archery_round: Round | str,
    bowstyle: AGB_bowstyles,
    gender: AGB_genders,
    age_group: AGB_ages,
    strict_rounds: bool = True,
    strict_distance: bool = True,
) -> list[int]:
    """
    Calculate AGB outdoor classification scores for category.

    Subroutine to calculate classification scores for a specific category and round.
    Appropriate for 2023 ArcheryGB age groups and classifications.

    Parameters
    ----------
    archery_round : Round | str
        an archeryutils Round object as suitable for this scheme
        alternatively the round codename as a str can be used
    bowstyle : AGB_bowstyles
        archer's bowstyle under AGB outdoor target rules
    gender : AGB_genders
        archer's gender under AGB outdoor target rules
    age_group : AGB_ages
        archer's age group under AGB outdoor target rules
    strict_rounds : bool, default=True
        Whether to enforce valid AGB rounds only and prestige rounds rules
        If False prestige rounds will no longer default to give all classifications and
        max-distance rounds will return scores for MB classifications.
    strict_distance : bool, default=True
        Whether to enforce age-dependent distance restrictions

    Returns
    -------
    classification_scores : ndarray
        scores required for each classification in descending order

    References
    ----------
    ArcheryGB 2023 Rules of Shooting
    ArcheryGB Shooting Administrative Procedures - SAP7 (2023)

    Raises
    ------
    ValueError
        If requested round is not valid for this scheme (when strict_rounds enabled)
    TypeError
        If archery_round is passed as a string when strict_rounds disabled

    Examples
    --------
    >>> from archeryutils import classifications as cf
    >>> from archeryutils import load_rounds
    >>> agb_outdoor = load_rounds.AGB_outdoor_imperial
    >>> cf.agb_outdoor_classification_scores(
    ...     agb_outdoor.hereford,
    ...     cf.AGB_bowstyles.RECURVE,
    ...     cf.AGB_genders.FEMALE,
    ...     cf.AGB_ages.ADULT,
    ... )
    [1232, 1178, 1107, 1015, 900, 763, 614, 466, 336]

    If a classification cannot be achieved a fill value of `-9999` is returned:

    >>> cf.agb_outdoor_classification_scores(
    ...     agb_outdoor.bristol_ii,
    ...     cf.AGB_bowstyles.RECURVE,
    ...     cf.AGB_genders.FEMALE,
    ...     cf.AGB_ages.ADULT,
    ... )
    [-9999, -9999, -9999, -9999, -9999, 931, 797, 646, 493]

    """
    if strict_rounds:
        archery_round, roundname = _check_round_eligibility(archery_round)
        archery_round = ALL_OUTDOOR_ROUNDS[cls_funcs.strip_spots(roundname)]
    elif isinstance(archery_round, str):
        msg = (
            "strict_rounds is False so archery_round must be explicitly specified as "
            "a Round type instead of a string."
        )
        raise TypeError(msg)
    else:
        # If a custom round has been passed use codename for prestige checks
        # This assumes users do not set the codename to an alreay existing codename
        roundname = archery_round.codename

    groupname = _get_outdoor_groupname(bowstyle, gender, age_group)
    group_data = agb_outdoor_classifications[groupname]

    hc_scheme = "AGB"

    # Get scores required on this round for each classification
    class_scores = [
        hc.score_for_round(
            group_data["class_HC"][i],
            archery_round,
            hc_scheme,
            rounded_score=True,
        )
        for i in range(len(group_data["classes"]))
    ]

    # Reduce list based on other criteria besides handicap
    # Is it a prestige round? If not remove MB scores
    if (
        strict_rounds
        and roundname not in agb_outdoor_classifications[groupname]["prestige_rounds"]
    ):
        class_scores[0:3] = [-9999] * 3

    # What classes are eligible based on category and distance
    # Restrict scores based on distance, unless we are enforcing strict round rules and
    # this is a prestige round in which case all classifications are available.
    if strict_distance and not (
        strict_rounds
        and roundname in agb_outdoor_classifications[groupname]["prestige_rounds"]
    ):
        round_max_dist = archery_round.max_distance().value
        for i in range(len(class_scores)):
            if group_data["min_dists"][i] > round_max_dist:
                class_scores[i] = -9999

    # Score threshold should be int (score_for_round called with round=True)
    # Enforce this for better code and to satisfy mypy
    int_class_scores = [int(x) for x in class_scores]

    # Handle possibility of gaps in the tables or max scores by checking 1 HC point
    # above current (floored to handle 0.5) and amending accordingly
    # i.e. one must exceed (be lower than) the handicap threshold, not be awarded if
    # the same score is achievable at a higher handicap.
    for i, (score, handicap) in enumerate(
        zip(int_class_scores, group_data["class_HC"], strict=True),
    ):
        next_score = hc.score_for_round(
            np.floor(handicap) + 1,
            archery_round,
            hc_scheme,
            rounded_score=True,
        )
        if next_score == score:
            # If already at max score this classification is impossible
            if score == archery_round.max_score():
                int_class_scores[i] = -9999
            # If gap in table increase to next score
            # (we assume here that no two classifications are only 1 point apart...)
            else:
                int_class_scores[i] += 1

    # Handle repeated scores by forcing at least 1 point separation between classes.
    for i, score in enumerate(int_class_scores[:-1]):
        if int_class_scores[i + 1] == score and score >= 0:
            if score == archery_round.max_score():  # pragma: no cover
                # Currently no coverage as not triggered and hard to test for.
                int_class_scores[i + 1] = -9999
            else:
                int_class_scores[i + 1] += 1

    return int_class_scores
