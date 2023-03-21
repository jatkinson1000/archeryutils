"""
Code for doing things with archery handicap equations.

Extended Summary
----------------
Code to add functionality to the basic handicap equations code
in handicap_equations.py including inverse function and display.

Routine Listings
----------------
print_handicap_table
handicap_from_score

"""
from typing import Union, Optional, List
import warnings
from itertools import chain
import numpy as np
import numpy.typing as npt

import archeryutils.handicaps.handicap_equations as hc_eq
from archeryutils import rounds

FILL = -1000


def print_handicap_table(
    hcs: Union[float, npt.NDArray[np.float_]],
    hc_sys: str,
    round_list: List[rounds.Round],
    hc_dat: hc_eq.HcParams,
    arrow_d: Optional[float] = None,
    round_scores_up: bool = True,
    clean_gaps: bool = False,
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
    # Abbreviations to replace headings with in Handicap Tables to keep concise
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

    if not isinstance(hcs, np.ndarray):
        if isinstance(hcs, list):
            hcs = np.array(hcs)
        elif isinstance(hcs, (float, int)):
            hcs = np.array([hcs])
        else:
            raise TypeError("Expected float or ndarray for hcs.")

    table = np.empty([len(hcs), len(round_list) + 1])
    table[:, 0] = hcs.copy()
    for i, round_i in enumerate(round_list):
        table[:, i + 1], _ = hc_eq.score_for_round(
            round_i, hcs, hc_sys, hc_dat, arrow_d, round_score_up=round_scores_up
        )

    if int_prec:
        table = table.astype(int)

    if clean_gaps:
        # TODO: This assumes scores are running highest to lowest.
        #  AA and AA2 will only work if hcs passed in reverse order (large to small)
        for irow, row in enumerate(table[:-1, :]):
            for jscore in range(len(row)):
                if table[irow, jscore] == table[irow + 1, jscore]:
                    if int_prec:
                        table[irow, jscore] = FILL
                    else:
                        table[irow, jscore] = np.nan

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

    def abbreviate(name: str) -> str:
        return " ".join(abbreviations.get(i, i) for i in name.split())

    round_names = [abbreviate(r.name) for r in round_list]
    output_header = "".join(name.rjust(14) for name in chain(["Handicap"], round_names))

    def format_row(row: npt.NDArray[Union[np.float_, np.int_]]) -> str:
        if int_prec:
            return "".join("".rjust(14) if x == FILL else f"{x:14d}" for x in row)
        return "".join("".rjust(14) if np.isnan(x) else f"{x:14.8f}" for x in row)

    output_rows = [format_row(row) for row in table]
    output_str = "\n".join(chain([output_header], output_rows))

    if printout:
        print(output_str)

    if filename is not None:
        print("Writing handicap table to file...", end="")
        with open(filename, "w") as f:
            f.write(output_str)
        print("Done.")


def handicap_from_score(
    score: Union[int, float],
    rnd: rounds.Round,
    hc_sys: str,
    hc_dat: hc_eq.HcParams,
    arw_d: Optional[float] = None,
    int_prec: bool = False,
) -> Union[int, float]:
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

    References
    ----------
    Brent's Method for Root Finding in Scipy
    - https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html
    - https://github.com/scipy/scipy/blob/dde39b7cc7dc231cec6bf5d882c8a8b5f40e73ad/
      scipy/optimize/Zeros/brentq.c
    """
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
        # start high and drop down until no longer rounding to max score
        # (i.e. >= max_score - 1.0 for AGB, and >= max_score - 0.5 for AA, AA2, and AGBold)
        if hc_sys in ("AA", "AA2"):
            hc = 175.0
            dhc = -0.01
        else:
            hc = -75.0
            dhc = 0.01

        # Set rounding limit
        if hc_sys in ("AA", "AA2", "AGBold"):
            round_lim = 0.5
        else:
            round_lim = 1.0

        s_max, _ = hc_eq.score_for_round(
            rnd, hc, hc_sys, hc_dat, arw_d, round_score_up=False
        )
        # Work down to where we would round or ceil to max score
        while s_max > max_score - round_lim:
            hc = hc + dhc
            s_max, _ = hc_eq.score_for_round(
                rnd, hc, hc_sys, hc_dat, arw_d, round_score_up=False
            )
        hc = hc - dhc  # Undo final iteration that overshoots
        if int_prec:
            if hc_sys in ("AA", "AA2"):
                hc = np.ceil(hc)
            else:
                hc = np.floor(hc)
        else:
            warnings.warn(
                "Handicap requested for maximum score without integer precision.\n"
                "Value returned will be first handiucap that achieves this score.\n"
                "This could cause issues if you are not working in integers.",
                UserWarning,
            )
        return hc

    # ROOT FINDING for general case (not max score)
    def f_root(
        h: float,
        scr: Union[int, float],
        rd: rounds.Round,
        sys: str,
        hc_data: hc_eq.HcParams,
        arw_dia: Optional[float],
    ) -> float:
        val, _ = hc_eq.score_for_round(
            rd, h, sys, hc_data, arw_dia, round_score_up=False
        )
        # Ensure we return float, not np.ndarray
        # These 9 lines replace `return val-scr` so as to satisfy mypy --strict.
        # Should never be triggered in reality as h is type float.
        if isinstance(val, np.float_):
            val = val.item()
        if isinstance(val, float):
            return val - scr
        raise TypeError(
            f"f_root is attempting to return a {type(val)} type but expected float. "
            f"Was it passed an array of handicaps?"
        )

    if hc_sys in ("AA", "AA2"):
        x = [-250.0, 175.0]
    else:
        x = [-75.0, 300.0]

    f = [
        f_root(x[0], score, rnd, hc_sys, hc_dat, arw_d),
        f_root(x[1], score, rnd, hc_sys, hc_dat, arw_d),
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

    if abs(f[1]) <= f[0]:
        xcur = x[1]
        xpre = x[0]
        fcur = f[1]
        fpre = f[0]
    else:
        xpre = x[1]
        xcur = x[0]
        fpre = f[1]
        fcur = f[0]

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
            hc = xcur
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
        hc = xcur

    # Force integer precision if required.
    if int_prec:
        if hc_sys in ("AA", "AA2"):
            hc = np.floor(hc)
        else:
            hc = np.ceil(hc)

        sc, _ = hc_eq.score_for_round(
            rnd, hc, hc_sys, hc_dat, arw_d, round_score_up=True
        )

        # Check that you can't get the same score from a larger handicap when
        # working in integers
        min_h_flag = False
        if hc_sys in ("AA", "AA2"):
            hstep = -1.0
        else:
            hstep = 1.0
        while not min_h_flag:
            hc += hstep
            sc, _ = hc_eq.score_for_round(
                rnd, hc, hc_sys, hc_dat, arw_d, round_score_up=True
            )
            if sc < score:
                hc -= hstep  # undo the iteration that caused the flag to raise
                min_h_flag = True

    return hc
