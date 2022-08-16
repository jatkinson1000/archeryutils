# Author        : Jack Atkinson
#
# Contributors  : Jack Atkinson
#
# Date Created  : 2022-08-16
# Last Modified : 2022-08-16 by Jack Atkinson
#
# Summary       : Code for doing things with archery handicap code
#

import numpy as np

from archerycls import rounds
import handicaps.handicap_equations as hc_eq


def print_handicap_table(hcs, hc_sys, round_list, hc_dat, arrow_rad,
                         round_scores_up=True, clean_gaps=False,
                         printout=True, filename=None, csvfile=None,
                         int_prec=False):
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
    hc_dat : HcParams
        dataclass containing parameters for handicap equations
    arrow_rad : float
        arrow radius in [metres]
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
    table = np.empty([len(hcs), len(round_list)+1])
    table[:, 0] = hcs[:]
    for i, round_i in enumerate(round_list):
        table[:, i+1], _ = hc_eq.score_for_round(round_i, hcs, hc_sys, hc_dat, arrow_rad,
                                                 round_score_up=round_scores_up)

    if int_prec:
        table = table.astype(int)

    if clean_gaps:
        # TODO: This assumes scores are running highest to lowest.
        #  AA and AA2 will only work if hcs passed in reverse order (large to small)
        for irow, row in enumerate(table[:-1, :]):
            for jscore, score in enumerate(row):
                if table[irow, jscore] == table[irow+1, jscore]:
                    if int_prec:
                        table[irow, jscore] = -1
                    else:
                        table[irow, jscore] = np.nan

    if printout:
        print('Handicap'.rjust(14), end='')
        [print(f'{round_i.name.rjust(14)}', end='') for round_i in round_list]
        print('\n', end='')
        for row in table:
            if int_prec:
                [print(f"{''.rjust(14)}" if (sc == -1) else f"{sc:14d}", end='') for sc in row]
            else:
                [print(f"{''.rjust(14)}" if (np.isnan(sc)) else f"{sc:14.2f}", end='') for sc in row]
            print('\n', end='')

    if filename is not None:
        print('Writing handicap table to file...', end='')
        with open(filename, 'w') as f:
            f.write('Handicap'.rjust(14))
            [f.write(f'{round_i.name.rjust(14)}') for round_i in round_list]
            f.write('\n')
            for row in table:
                if int_prec:
                    [f.write(f"{''.rjust(14)}" if (sc == -1) else f"{sc:14d}") for sc in row]
                else:
                    [f.write(f"{''.rjust(14)}" if np.isnan(sc) else f"{sc:14.2f}") for sc in row]
                f.write('\n')
        print('Done.')

    if csvfile is not None:
        print('Writing handicap table to csv...', end='')
        np.savetxt(csvfile, table,
                   delimiter=', ', header=f"handicap, {','.join([round_i.name for round_i in round_list])}'")
        print('Done.')

    return None
