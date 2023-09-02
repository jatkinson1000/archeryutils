"""
Code for doing things with archery handicap equations.

Extended Summary
----------------
Code to add functionality to the basic handicap equations code
in handicap_equations.py including inverse function and display.

Routine Listings
----------------
handicap_from_score
print_handicap_table
abbreviate
format_row

"""
from typing import Union, Optional, List
import warnings
from itertools import chain
import numpy as np
import numpy.typing as npt

import archeryutils.handicaps.handicap_equations as hc_eq
from archeryutils import rounds

FILL = -9999


def handicap_from_score(
    score: Union[int, float],
    rnd: rounds.Round,
    hc_sys: str,
    hc_dat: hc_eq.HcParams,
    arw_d: Optional[float] = None,
    int_prec: bool = False,
) -> Union[int, float]:
    # One too many arguments. Makes sense at the moment => disable
    # Could try and simplify hc_sys and hc_dat in future refactor
    # pylint: disable=too-many-arguments
    """
    Calculate the handicap of a given score on a given round using root-finding.

    Parameters
    ----------
    score : float
        score achieved on the round
    rnd : rounds.Round
        a rounds.Round class object that was shot
    hc_sys : str
        identifier for the handicap system
    hc_dat : handicaps.handicap_equations.HcParams
        dataclass containing parameters for handicap equations
    arw_d : float
        arrow diameter in [metres] default = None
    int_prec : bool
        display results as integers? default = False, with decimal to 2dp accuracy from
        rootfinder

    Returns
    -------
    hc: int or float
        Handicap. Has type int if int_prec is True, and otherwise has type false.
    """
    # Check we have a valid score
    max_score = rnd.max_score()
    if score > max_score:
        raise ValueError(
            f"The score of {score} provided is greater than the maximum of {max_score} "
            f"for a {rnd.name}."
        )
    if score <= 0.0:
        raise ValueError(
            f"The score of {score} provided is less than or equal to zero so cannot "
            "have a handicap."
        )

    if score == max_score:
        # Deal with max score before root finding
        return get_max_score_handicap(rnd, hc_sys, hc_dat, arw_d, int_prec)

    handicap = rootfind_score_handicap(score, rnd, hc_sys, hc_dat, arw_d)

    # Force integer precision if required.
    if int_prec:
        if hc_sys in ("AA", "AA2"):
            handicap = np.floor(handicap)
        else:
            handicap = np.ceil(handicap)

        sc_int, _ = hc_eq.score_for_round(
            rnd, handicap, hc_sys, hc_dat, arw_d, round_score_up=True
        )

        # Check that you can't get the same score from a larger handicap when
        # working in integers
        min_h_flag = False
        if hc_sys in ("AA", "AA2"):
            hstep = -1.0
        else:
            hstep = 1.0
        while not min_h_flag:
            handicap += hstep
            sc_int, _ = hc_eq.score_for_round(
                rnd, handicap, hc_sys, hc_dat, arw_d, round_score_up=True
            )
            if sc_int < score:
                handicap -= hstep  # undo the iteration that caused flag to raise
                min_h_flag = True

    return handicap


def get_max_score_handicap(
    rnd: rounds.Round,
    hc_sys: str,
    hc_dat: hc_eq.HcParams,
    arw_d: Optional[float],
    int_prec: bool = False,
) -> float:
    """
    Get handicap for maximum score on a round.

    Start high and drop down until no longer rounding to max score.
    i.e. >= max_score - 1.0 for AGB, and >= max_score - 0.5 for AA, AA2, and AGBold.

    Parameters
    ----------
    rnd : rounds.Round
        round being used
    hc_sys : str
        identifier for the handicap system
    hc_dat : handicaps.handicap_equations.HcParams
        dataclass containing parameters for handicap equations
    arw_d : float
        arrow diameter in [metres] default = None
    int_prec : bool
        display results as integers? default = False

    Returns
    -------
    handicap : float
        appropriate handicap for this maximum score
    """
    max_score = rnd.max_score()

    if hc_sys in ("AA", "AA2"):
        handicap = 175.0
        delta_hc = -0.01
    else:
        handicap = -75.0
        delta_hc = 0.01

    # Set rounding limit
    if hc_sys in ("AA", "AA2", "AGBold"):
        round_lim = 0.5
    else:
        round_lim = 1.0

    s_max, _ = hc_eq.score_for_round(
        rnd, handicap, hc_sys, hc_dat, arw_d, round_score_up=False
    )
    # Work down to where we would round or ceil to max score
    while s_max > max_score - round_lim:
        handicap = handicap + delta_hc
        s_max, _ = hc_eq.score_for_round(
            rnd, handicap, hc_sys, hc_dat, arw_d, round_score_up=False
        )
    handicap = handicap - delta_hc  # Undo final iteration that overshoots
    if int_prec:
        if hc_sys in ("AA", "AA2"):
            handicap = np.ceil(handicap)
        else:
            handicap = np.floor(handicap)
    else:
        warnings.warn(
            "Handicap requested for maximum score without integer precision.\n"
            "Value returned will be first handiucap that achieves this score.\n"
            "This could cause issues if you are not working in integers.",
            UserWarning,
        )
    return handicap


def rootfind_score_handicap(
    score: float,
    rnd: rounds.Round,
    hc_sys: str,
    hc_dat: hc_eq.HcParams,
    arw_d: Optional[float],
) -> float:
    """
    Get handicap for general score on a round through rootfinding algorithm.

    Parameters
    ----------
    score : float
        score to get handicap for
    rnd : rounds.Round
        round being used
    hc_sys : str
        identifier for the handicap system
    hc_dat : handicaps.handicap_equations.HcParams
        dataclass containing parameters for handicap equations
    arw_d : float
        arrow diameter in [metres] default = None

    Returns
    -------
    handicap : float
        appropriate accurate handicap for this score

    References
    ----------
    Brent's Method for Root Finding in Scipy
    - https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html
    - https://github.com/scipy/scipy/blob/dde39b7cc7dc231cec6bf5d882c8a8b5f40e73ad/
      scipy/optimize/Zeros/brentq.c

    """
    # The rootfinding algorithm here raises pylint errors for
    # too many statements (64/50), branches (17/12), and variables(23/15).
    # However, it is a single enclosed algorithm => disable
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements

    if hc_sys in ("AA", "AA2"):
        x_init = [-250.0, 175.0]
    else:
        x_init = [-75.0, 300.0]

    f_init = [
        f_root(x_init[0], score, rnd, hc_sys, hc_dat, arw_d),
        f_root(x_init[1], score, rnd, hc_sys, hc_dat, arw_d),
    ]
    xtol = 1.0e-16
    rtol = 0.00
    xblk = 0.0
    fblk = 0.0
    scur = 0.0
    spre = 0.0
    dpre = 0.0
    dblk = 0.0
    stry = 0.0

    if abs(f_init[1]) <= f_init[0]:
        xcur = x_init[1]
        xpre = x_init[0]
        fcur = f_init[1]
        fpre = f_init[0]
    else:
        xpre = x_init[1]
        xcur = x_init[0]
        fpre = f_init[1]
        fcur = f_init[0]

    for _ in range(25):
        if (fpre != 0.0) and (fcur != 0.0) and (np.sign(fpre) != np.sign(fcur)):
            xblk = xpre
            fblk = fpre
            spre = xcur - xpre
            scur = xcur - xpre
        if abs(fblk) < abs(fcur):
            # xpre = xcur
            # xcur = xblk
            # xblk = xpre
            xpre, xcur, xblk = xcur, xblk, xcur

            # fpre = fcur
            # fcur = fblk
            # fblk = fpre
            fpre, fcur, fblk = fcur, fblk, fcur

        delta = (xtol + rtol * abs(xcur)) / 2.0
        sbis = (xblk - xcur) / 2.0

        if (fcur == 0.0) or (abs(sbis) < delta):
            handicap = xcur
            break

        if (abs(spre) > delta) and (abs(fcur) < abs(fpre)):
            if xpre == xblk:
                stry = -fcur * (xcur - xpre) / (fcur - xpre)
            else:
                dpre = (fpre - fcur) / (xpre - xcur)
                dblk = (fblk - fcur) / (xblk - xcur)
                stry = -fcur * (fblk - fpre) / (fblk * dpre - fpre * dblk)

            if 2 * abs(stry) < min(abs(spre), 3 * abs(sbis) - delta):
                # accept step
                spre = scur
                scur = stry
            else:
                # bisect
                spre = sbis
                scur = sbis
        else:
            # bisect
            spre = sbis
            scur = sbis
        xpre = xcur
        fpre = fcur
        if abs(scur) > delta:
            xcur += scur
        else:
            if sbis > 0:
                xcur += delta
            else:
                xcur -= delta

        fcur = f_root(xcur, score, rnd, hc_sys, hc_dat, arw_d)
        handicap = xcur

    return handicap


def f_root(
    hc_est: float,
    score_est: Union[int, float],
    round_est: rounds.Round,
    sys: str,
    hc_data: hc_eq.HcParams,
    arw_dia: Optional[float],
) -> float:
    """
    Return error between predicted score and desired score.

    Parameters
    ----------
    hc_est : float
        current estimate of handicap
    score_est : float
        current estimate of score based on hc_est
    round_est : rounds.Round
        round being used
    sys : str
        identifier for the handicap system
    hc_data : handicaps.handicap_equations.HcParams
        dataclass containing parameters for handicap equations
    arw_dia : float
        arrow diameter in [metres] default = None

    Returns
    -------
    val-score_est : float
        difference between desired value and score estimate
    """
    # One too many arguments. Makes sense at the moment => disable
    # Could try and simplify hc_sys and hc_dat in future refactor
    # pylint: disable=too-many-arguments

    val, _ = hc_eq.score_for_round(
        round_est, hc_est, sys, hc_data, arw_dia, round_score_up=False
    )

    # Ensure we return float, not np.ndarray
    # These 8 lines replace `return val-scr` so as to satisfy mypy --strict.
    # Should never be triggered in reality as h is type float.
    if isinstance(val, np.float_):
        val = val.item()
    if isinstance(val, float):
        return val - score_est
    raise TypeError(
        f"f_root is attempting to return a {type(val)} type but expected float. "
        f"Was it passed an array of handicaps?"
    )


def print_handicap_table(
    hcs: Union[float, npt.NDArray[np.float_]],
    hc_sys: str,
    round_list: List[rounds.Round],
    hc_dat: hc_eq.HcParams,
    arrow_d: Optional[float] = None,
    round_scores_up: bool = True,
    clean_gaps: bool = True,
    printout: bool = True,
    filename: Optional[str] = None,
    csvfile: Optional[str] = None,
    int_prec: Optional[bool] = False,
) -> None:
    """
    Generate a handicap table to screen and/or file.

    Parameters
    ----------
    hcs : ndarray or float
        handicap value(s) to calculate score(s) for
    hc_sys : string
        identifier for the handicap system
    round_list : list of rounds.Round
        List of Round classes to calculate scores for
    hc_dat : handicaps.handicap_equations.HcParams
        dataclass containing parameters for handicap equations
    arrow_d : float
        arrow diameter in [metres] default = None
    round_scores_up : bool
        round scores up to nearest integer? default = True
    clean_gaps : bool
        Remove all instances of a score except the first? default = False
    printout : bool
        Print to screen? default = True
    filename : str
        filepath to save table to. default = None
    csvfile : str
        csv filepath to save to. default = None
    int_prec : bool
        display results as integers? default = False, with decimal to 2dp

    Returns
    -------
    None
    """
    # Cannot see any other way to handle the options required here => ignore
    # pylint: disable=too-many-arguments
    # Knock-on effect is too many local variables raised => ignore
    # pylint: disable=too-many-locals

    if not isinstance(hcs, np.ndarray):
        if isinstance(hcs, list):
            hcs = np.array(hcs)
        elif isinstance(hcs, (float, int)):
            hcs = np.array([hcs])
        else:
            raise TypeError("Expected float or ndarray for hcs.")

    table: npt.NDArray[Union[np.float_, np.int_]] = np.empty(
        [len(hcs), len(round_list) + 1]
    )
    table[:, 0] = hcs.copy()
    for i, round_i in enumerate(round_list):
        table[:, i + 1], _ = hc_eq.score_for_round(
            round_i,
            hcs,
            hc_sys,
            hc_dat,
            arrow_d,
            round_score_up=round_scores_up,
        )

    # If rounding scores up we don't want to display trailing zeros, so ensure int_prec
    if round_scores_up:
        int_prec = True

    if int_prec:
        table = table.astype(int)

    if clean_gaps:
        table = clean_repeated(table, int_prec, hc_sys)

    # Write to CSV
    if csvfile is not None:
        print("Writing handicap table to csv...", end="")
        np.savetxt(
            csvfile,
            table,
            delimiter=", ",
            header=f"handicap, {','.join([round_i.name for round_i in round_list])}'",
        )
        print("Done.")

    # Write to terminal/string
    # Return early if this isn't required
    if filename is None and not printout:
        return

    # To ensure both terminal and file output are the same, create a single string to
    # be used in either case

    round_names = [abbreviate(r.name) for r in round_list]
    output_header = "".join(name.rjust(14) for name in chain(["Handicap"], round_names))

    output_rows = [format_row(row, int_prec) for row in table]
    output_str = "\n".join(chain([output_header], output_rows))

    if printout:
        print(output_str)

    if filename is not None:
        print("Writing handicap table to file...", end="")
        with open(filename, "w", encoding="utf-8") as table_file:
            table_file.write(output_str)
        print("Done.")


def clean_repeated(
    table: npt.NDArray[Union[np.float_, np.int_]],
    int_prec: Optional[bool] = False,
    hc_sys: Optional[str] = "AGB",
) -> npt.NDArray[Union[np.float_, np.int_]]:
    """
    Keep only the first instance of a score in the handicap tables.

    Parameters
    ----------
    table : np.ndarray
        handicap table of scores
    int_prec : bool
        return integers, not floats?
    hc_sys : str
        handicap system used - assume AGB (high -> low) unless specified

    Returns
    -------
    table : np.ndarray
        handicap table of scores with repetitions filtered
    """
    # NB: This assumes scores are running highest to lowest.
    # :. Flip AA and AA2 tables before operating.

    if hc_sys in ("AA", "AA2"):
        table = np.flip(table, axis=0)

    for irow, row in enumerate(table[:-1, :]):
        for jscore in range(len(row)):
            if table[irow, jscore] == table[irow + 1, jscore]:
                if int_prec:
                    table[irow, jscore] = FILL
                else:
                    table[irow, jscore] = np.nan

    if hc_sys in ("AA", "AA2"):
        table = np.flip(table, axis=0)

    return table


def abbreviate(name: str) -> str:
    """
    Replace headings within Handicap Tables with abbreviations to keep concise.

    NB: This function only works with names containing space-separated words.

    Parameters
    ----------
    name : str
        full, long round name as appears currently

    Returns
    -------
    shortname : str
        abbreviated round name to replace with
    """
    abbreviations = {
        "Compound": "C",
        "Recurve": "R",
        "Triple": "Tr",
        "Centre": "C",
        "Portsmouth": "Ports",
        "Worcester": "Worc",
        "Short": "St",
        "Long": "Lg",
        "Small": "Sm",
        "Gents": "G",
        "Ladies": "L",
    }

    return " ".join(abbreviations.get(i, i) for i in name.split())


def format_row(
    row: npt.NDArray[Union[np.float_, np.int_]],
    int_prec: Optional[bool] = False,
) -> str:
    """
    Fornat appearance of handicap table row to look nice.

    Parameters
    ----------
    row : NDArray
        numpy array of table row
    int_prec : bool
        return integers, not floats?

    Returns
    -------
    formatted_row : str
        pretty string based on input array data
    """
    if int_prec:
        return "".join("".rjust(14) if x == FILL else f"{int(x):14d}" for x in row)
    return "".join("".rjust(14) if np.isnan(x) else f"{x:14.8f}" for x in row)
