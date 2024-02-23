"""
Code providing various functionalities using the archery handicap equations.

Makes use of the basic handicap equations in handicaps.handicap_equations to do
more elaborate things such as reverse calculation of handicap from score,
generation of handicap tables, etc.

Extended Summary
----------------
Code to add functionality to the basic handicap equations code
in handicap_equations.py including inverse function and display.

Routine Listings
----------------
- handicap_scheme()
- arrow_score()
- score_for_passes()
- score_for_round()
- handicap_from_score()


"""

from typing import Optional, Union

import numpy as np
import numpy.typing as npt

from archeryutils import rounds, targets

from .handicap_scheme import FloatArray, HandicapScheme
from .handicap_scheme_aa import HandicapAA, HandicapAA2
from .handicap_scheme_agb import HandicapAGB, HandicapAGBold

_CLASSES = {
    "AGB": HandicapAGB,
    "AGBold": HandicapAGBold,
    "AA": HandicapAA,
    "AA2": HandicapAA2,
}


def handicap_scheme(
    handicap_sys: Union[str, HandicapScheme], **kwargs: float
) -> HandicapScheme:
    """
    Create a HandicapScheme subclass for a requested handicap scheme.

    Parameters
    ----------
    handicap_sys : Union[str, HandicapScheme]
        String identifying the handicap scheme class to be generated, or an existing
        HandicapScheme
    \\**kwargs : float
        Various kwargs defining custom values of parameters as appropriate for hc_sys

    Returns
    -------
    HandicapScheme
        a subclass of HandicapScheme as appropriate for the inputs

    Raises
    ------
    ValueError
        If a handicap scheme is requested for which there is no defined class.

    See Also
    --------
    handicap_scheme.HandicapScheme : The HandicapScheme class
    handicap_scheme_agb.HandicapAGB :
        The AGB HandicapScheme subclass and associated \\**kwargs
    handicap_scheme_agb.HandicapAGBold :
        The AGBold HandicapScheme subclass and associated \\**kwargs
    handicap_scheme_aa.HandicapAA :
        The AA HandicapScheme subclass and associated \\**kwargs
    handicap_scheme_aa.HandicapAA2 :
        The AA2 HandicapScheme subclass and associated \\**kwargs

    Examples
    --------
    To generate a HandicapScheme class using the Archery GB (AGB) handicap scheme:

    >>> from archeryutils import handicaps as hc
    >>> agb_scheme = hc.handicap_scheme("AGB")
    >>> agb_scheme
    <archeryutils.handicaps.handicap_equations.HandicapAGB object at 0x31415ee00>

    """
    if isinstance(handicap_sys, HandicapScheme):
        return handicap_sys
    try:
        return _CLASSES[handicap_sys](**kwargs)
    except KeyError as exc:
        raise ValueError(
            f"{handicap_sys} is not a recognised handicap system.\n"
            f"""Please select from '{"', '".join(_CLASSES.keys())}'."""
        ) from exc


def arrow_score(
    target: targets.Target,
    handicap: FloatArray,
    handicap_sys: Union[str, HandicapScheme],
    arw_d: Optional[float] = None,
) -> FloatArray:
    """
    Calculate the average arrow score for a given target and handicap rating.

    Parameters
    ----------
    target : targets.Target
        A Target class specifying the target to be used
    handicap : FloatArray
        handicap value to calculate score for
    handicap_sys : Union[str, HandicapScheme]
        identifier for the handicap system to use
    arw_d : float or None, default=None
        user-specified arrow diameter in [metres]

    Returns
    -------
    FloatArray
        average expected arrow score for this handicap and target

    Warnings
    --------
    Using a custom value for arrow diameter may give values that differ
    from the official handicap scheme values.

    Examples
    --------
    Expected arrow score on a WA720 70m target, using the AGB handicap system at a
    handicap of 10 can be calculated with:

    >>> import archeryutils as au
    >>> from archeryutils import handicaps as hc
    >>> my720target = au.Target("10_zone", 122, 70.0)
    >>> hc.arrow_score(my720target, 10.0, "AGB")
    9.401182682963338

    It can also be passed an array of handicaps:

    >>> hc.arrow_score(my720target, np.array([10.0, 50.0, 100.0]), "AGB")
    array([9.40118268, 6.05227962, 0.46412515])

    """
    hc_sys = handicap_scheme(handicap_sys)

    return hc_sys.arrow_score(target, handicap, arw_d=arw_d)


def score_for_passes(
    rnd: rounds.Round,
    handicap: FloatArray,
    handicap_sys: Union[str, HandicapScheme],
    arw_d: Optional[float] = None,
    rounded_score: bool = True,
) -> npt.NDArray[np.float_]:
    """
    Calculate the expected score for all passes in a round at a given handicap.

    Parameters
    ----------
    rnd : rounds.Round
        A Round class specifying the round being shot
    handicap : FloatArray
        handicap value to calculate score for
    handicap_sys : Union[str, HandicapScheme]
        identifier for the handicap system to use
    arw_d : float or None, default=None
        user-specified arrow diameter in [metres]
    rounded_score : bool, default=True
        round score to integer value?
        Note the sum of rounded passes may not be the same as the rounded round score

    Returns
    -------
    NDArray
        average score for each pass in the round

    Examples
    --------
    Expected score for each pass on a WA1440 90m, using the AGB handicap system at a
    handicap of 10 can be calculated with the code below which returns an array with
    one score for each pass that makes up the round:

    >>> import archeryutils as au
    >>> from archeryutils import handicaps as hc
    >>> wa_outdoor = au.load_rounds.WA_outdoor
    >>> hc.score_for_passes(wa_outdoor.wa1440_90, 10.0, "AGB")
    array([322.84091528, 338.44257659, 338.66395001, 355.87959411])

    It can also be passed an array of handicaps:

    >>> hc.score_for_passes(
    ...     wa_outdoor.wa1440_90,
    ...     np.array([10.0, 50.0, 100.0]),
    ...     "AGB",
    ... )
    array([[322.84091528, 162.76200686,   8.90456718],
           [338.44257659, 217.88206641,  16.70850537],
           [338.66395001, 216.74407488,  16.41855209],
           [355.87959411, 288.77185611,  48.47897177]])

    """
    hc_sys = handicap_scheme(handicap_sys)

    return hc_sys.score_for_passes(
        rnd, handicap, arw_d=arw_d, rounded_score=rounded_score
    )


def score_for_round(
    rnd: rounds.Round,
    handicap: FloatArray,
    handicap_sys: Union[str, HandicapScheme],
    arw_d: Optional[float] = None,
    rounded_score: bool = True,
):
    """
    Calculate the expected score for a round at a given handicap.

    Parameters
    ----------
    rnd : rounds.Round
        A Round class specifying the round being shot
    handicap : FloatArray
        handicap value to calculate score for
    handicap_sys : Union[str, HandicapScheme]
        identifier for the handicap system to use
    arw_d : float or None, default=None
        user-specified arrow diameter in [metres]
    rounded_score : bool, default=True
        round score to integer value?

    Returns
    -------
    round_score : FloatArray
        average score of the round for this set of parameters

    Examples
    --------
    Expected score for a WA1440 90m, using the AGB handicap system at a
    handicap of 10 can be calculated with:

    >>> import archeryutils as au
    >>> from archeryutils import handicaps as hc
    >>> wa_outdoor = au.load_rounds.WA_outdoor
    >>> hc.score_for_round(wa_outdoor.wa1440_90, 10.0, "AGB")
    1356.0
    >>> au.handicap_equations.score_for_round(wa_outdoor.wa1440_90,
    ...                                       10.0,
    ...                                       rounded_score=False)
    1355.8270359849505

    It can also be passed an array of handicaps:

    >>> hc.score_for_round(
    ...     wa_outdoor.wa1440_90,
    ...     np.array([10.0, 50.0, 100.0]),
    ... )
    array([1356.,  887.,   91.])

    """
    hc_sys = handicap_scheme(handicap_sys)

    return hc_sys.score_for_round(
        rnd, handicap, arw_d=arw_d, rounded_score=rounded_score
    )


def handicap_from_score(
    score: float,
    rnd: rounds.Round,
    handicap_sys: Union[str, HandicapScheme],
    arw_d: Optional[float] = None,
    int_prec: bool = False,
) -> Union[int, float]:
    """
    Calculate the handicap of a given score on a given round.

    Parameters
    ----------
    score : float
        score achieved on the round
    rnd : rounds.Round
        the rounds.Round object to calculate the handicap for
    handicap_sys : str or HandicapScheme
        identifier for the handicap system to use
    arw_d : float or None, default=None
        user-specified arrow diameter in [metres]
    int_prec : bool, default=False
        display results as integers? default = False
        if True decimal results accurate to 2dp

    Returns
    -------
    int or float
        Handicap for score. Has type int if int_prec is True, else float.

    Examples
    --------
    Handicap for a score of 999 on a WA 1440 (90m) using the AGB scheme can be
    calculated as:

    >>> import archeryutils as au
    >>> wa_outdoor = au.load_rounds.WA_outdoor
    >>> hc.handicap_from_score(999, wa_outdoor.wa1440_90, "AGB")
    43.999964586102706

    To get an integer value as would appear in the handicap tables use
    ``int_prec=True``:

    >>> au.handicap_functions.handicap_from_score(
    ...     999,
    ...     wa_outdoor.wa1440_90,
    ...     "AGB", hc_params,
    ...     int_prec=True
    ... )
    44.0

    """
    hc_sys = handicap_scheme(handicap_sys)

    return hc_sys.handicap_from_score(score, rnd, arw_d=arw_d, int_prec=int_prec)
