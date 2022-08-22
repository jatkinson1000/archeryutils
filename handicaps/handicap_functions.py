# Author        : Jack Atkinson
#
# Contributors  : Jack Atkinson
#
# Date Created  : 2022-08-16
# Last Modified : 2022-08-22 by Jack Atkinson
#
# Summary       : Code for doing things with archery handicap code
#

import numpy as np
import scipy.optimize
import warnings

from archerycls import rounds
import handicaps.handicap_equations as hc_eq

FILL = -1000


def print_handicap_table(
    hcs,
    hc_sys,
    round_list,
    hc_dat,
    arrow_d=None,
    round_scores_up=True,
    clean_gaps=False,
    printout=True,
    filename=None,
    csvfile=None,
    int_prec=False,
):
    """
    Subroutine to generate a handicap table

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

    References
    ----------
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

    table = np.empty([len(hcs), len(round_list) + 1])
    table[:, 0] = hcs[:]
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
            for jscore, score in enumerate(row):
                if table[irow, jscore] == table[irow + 1, jscore]:
                    if int_prec:
                        table[irow, jscore] = FILL
                    else:
                        table[irow, jscore] = np.nan

    if printout:
        print("Handicap".rjust(14), end="")
        [
            print(f"{' '.join([abbreviations.get(i, i) for i in round_i.name.split()]).rjust(14)}", end="",)
            for round_i in round_list
        ]
        print("\n", end="")
        for row in table:
            if int_prec:
                [
                    print(f"{''.rjust(14)}" if (sc == FILL) else f"{sc:14d}", end="")
                    for sc in row
                ]
            else:
                [
                    print(f"{''.rjust(14)}" if (np.isnan(sc)) else f"{sc:14.8f}", end="")
                    for sc in row
                ]
            print("\n", end="")

    if filename is not None:
        print("Writing handicap table to file...", end="")
        with open(filename, "w") as f:
            f.write("Handicap".rjust(14))
            [
                f.write(
                    f"{' '.join([abbreviations.get(i, i) for i in round_i.name.split()]).rjust(14)}"
                )
                for round_i in round_list
            ]
            f.write("\n")
            for row in table:
                if int_prec:
                    [
                        f.write(f"{''.rjust(14)}" if (sc == FILL) else f"{sc:14d}")
                        for sc in row
                    ]
                else:
                    [
                        f.write(f"{''.rjust(14)}" if np.isnan(sc) else f"{sc:14.2f}")
                        for sc in row
                    ]
                f.write("\n")
        print("Done.")

    if csvfile is not None:
        print("Writing handicap table to csv...", end="")
        np.savetxt(
            csvfile,
            table,
            delimiter=", ",
            header=f"handicap, {','.join([round_i.name for round_i in round_list])}'",
        )
        print("Done.")

    return None


def handicap_from_score(score, rnd, hc_sys, hc_dat, arw_d=None, int_prec=False):
    """
    Subroutine to return the handicap of a given score on a given round

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
        display results as integers? default = False, with decimal to 2dp accuracy from rootfinder

    Returns
    -------
    hc

    References
    ----------
    Brent's Method for Root Finding in Scipy
    - https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html
    """
    max_score = rnd.max_score()
    if score > max_score:
        raise ValueError(
            f"The score of {score} provided is greater that the maximum of {max_score} for a {rnd.name}."
        )
    elif score <= 0.0:
        raise ValueError(
            f"The score of {score} provided is less than or equal to zero so cannot have a handicap."
        )

    elif score == max_score:
        # Deal with max score before root finding
        # start high and drop down until no longer ceiling to max score (i.e. >= max_score - 1.0)
        if hc_sys in ["AA", "AA2"]:
            hc = 175
            dhc = -0.01
        else:
            hc = -75
            dhc = 0.01
        s_max, _ = hc_eq.score_for_round(
            rnd, hc, hc_sys, hc_dat, arw_d, round_score_up=False
        )
        # Work down to where we would round up (ceil) to max score - ceiling approach
        while s_max > max_score - 1.0:
            hc += dhc
            s_max, _ = hc_eq.score_for_round(
                rnd, hc, hc_sys, hc_dat, arw_d, round_score_up=False
            )
        hc -= dhc  # Undo final iteration that overshoots
        if int_prec:
            if hc_sys in ["AA", "AA2"]:
                hc = np.ceil(hc)
            else:
                hc = np.floor(hc)
        else:
            warnings.warn(
                "Handicap requested for maximum score without integer precision.\n"
                "Value returned will be handicap required for score > max_score-1.\n"
                "This could cause issues if you are not working in integers.",
                UserWarning,
            )
        return hc

    else:
        # ROOT FINDING
        def f_root(h, scr, rd, sys, hc_data, arw_dia):
            val, _ = hc_eq.score_for_round(
                rd, h, sys, hc_data, arw_dia, round_score_up=False
            )
            return val - scr

        if hc_sys in ["AA", "AA2"]:
            br = [-250, 175]
        else:
            br = [-75, 300]
        sol = scipy.optimize.root_scalar(
            f_root,
            args=(score, rnd, hc_sys, hc_dat, arw_d),
            method="brenth",
            bracket=br,
            xtol=0.001,
            maxiter=50,
        )
        hc = sol.root

        # Force integer precision if required. If Aus systems force down, other systems force up.
        # Not trivial as we require asymmetric rounding, hence the if <0 clause
        if int_prec:
            if np.sign(hc) < 0:
                if hc_sys in ["AA", "AA2"]:
                    hc = np.ceil(hc)
                else:
                    hc = np.floor(hc)
            else:
                if hc_sys in ["AA", "AA2"]:
                    hc = np.floor(hc)
                else:
                    hc = np.ceil(hc)

            # Check that you can't get the same score from a larger handicap when working in integers
            min_h_flag = False
            if hc_sys in ["AA", "AA2"]:
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

        else:
            return hc
