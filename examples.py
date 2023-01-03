# Author        : Jack Atkinson
#
# Contributors  : Jack Atkinson
#
# Date Created  : 2022-08-16
#
# Summary       : Example script using the archeryutils functionalities
#

import numpy as np
from pathlib import Path
from archeryutils import (
    rounds,
    handicap_equations as hc_eq,
    handicap_functions as hc_func,
)

if __name__ == "__main__":
    # Generate a set of handicap tables for the York/Hereford/Bristol rounds
    hc_json_path = Path(__file__).parent / "archeryutils/handicaps/hc_sys_params.json"
    hc_params = hc_eq.HcParams().load_json_params(hc_json_path)

    # Rounds
    # Get round info from preloaded data:
    rounds.AGB_outdoor_imperial.york.get_info()
    print(
        f"Max score for a {rounds.AGB_outdoor_imperial.york.name} is {rounds.AGB_outdoor_imperial.york.max_score()}."
    )
    print(
        f"Max distance shot in a {rounds.AGB_outdoor_imperial.york.name} is {rounds.AGB_outdoor_imperial.york.max_distance()} {rounds.AGB_outdoor_imperial.york.max_distance(True)[1]}s."
    )
    print(
        f"The first pass on a {rounds.AGB_outdoor_imperial.york.name} is "
        f"{rounds.AGB_outdoor_imperial.york.passes[0].n_arrows} arrows shot at "
        f"{rounds.AGB_outdoor_imperial.york.passes[0].distance} and has a max score of "
        f"{rounds.AGB_outdoor_imperial.york.passes[0].max_score()}."
    )

    # Handicaps
    # Print the continuous score that is comes from this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 38.25, "AGB", hc_params, round_score_up=False
    )
    print(
        f"A handicap of 38.25 on a {rounds.AGB_outdoor_imperial.york.name} is a continuous score of {score_from_hc}."
    )

    # Print the continuous score that is comes from this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 38, "AGB", hc_params, round_score_up=False
    )
    print(
        f"A handicap of 38 on a {rounds.AGB_outdoor_imperial.york.name} is a continuous score of {score_from_hc}."
    )

    # Print the minimum discrete score that is required to get this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 38, "AGB", hc_params, round_score_up=True
    )
    print(
        f"A handicap of 38 on a {rounds.AGB_outdoor_imperial.york.name} requires a minimum score of {score_from_hc}."
    )

    # Print score for a certain handicap - continuous
    hc_from_score = hc_func.handicap_from_score(
        950, rounds.AGB_outdoor_imperial.york, "AGB", hc_params, int_prec=False
    )
    print(
        f"A score of 950 on a {rounds.AGB_outdoor_imperial.york.name} is a continuous handicap of {hc_from_score}."
    )

    # Print score for a certain handicap - discrete
    hc_from_score = hc_func.handicap_from_score(
        950, rounds.AGB_outdoor_imperial.york, "AGB", hc_params, int_prec=True
    )
    print(
        f"A score of 950 on a {rounds.AGB_outdoor_imperial.york.name} is a discrete handicap of {hc_from_score}."
    )

    # Generate handicap tables for all round groups - AGB Handicaps 0-150
    # Save to nice data files
    hc_func.print_handicap_table(
        np.arange(0.0, 151.0, 1.0),
        "AGB",
        list(rounds.AGB_outdoor_imperial.values()),
        hc_params,
        round_scores_up=True,
        clean_gaps=True,
        filename="AGB_outdoor_imperial_table.dat",
        int_prec=True,
    )

    hc_func.print_handicap_table(
        np.arange(0.0, 151.0, 1.0),
        "AGB",
        list(rounds.AGB_outdoor_metric.values()),
        hc_params,
        printout=False,
        round_scores_up=True,
        clean_gaps=True,
        filename="AGB_outdoor_metric_table.dat",
        int_prec=True,
    )

    hc_func.print_handicap_table(
        np.arange(0.0, 151.0, 1.0),
        "AGB",
        list(rounds.AGB_indoor.values()),
        hc_params,
        printout=False,
        round_scores_up=True,
        clean_gaps=True,
        filename="AGB_indoor_table.dat",
        int_prec=True,
    )

    hc_func.print_handicap_table(
        np.arange(0.0, 151.0, 1.0),
        "AGB",
        list(rounds.WA_outdoor.values()),
        hc_params,
        printout=False,
        round_scores_up=True,
        clean_gaps=True,
        filename="WA_outdoor_table.dat",
        int_prec=True,
    )

    hc_func.print_handicap_table(
        np.arange(0.0, 151.0, 1.0),
        "AGB",
        list(rounds.WA_indoor.values()),
        hc_params,
        printout=False,
        round_scores_up=True,
        clean_gaps=True,
        filename="WA_indoor_table.dat",
        int_prec=True,
    )

    hc_func.print_handicap_table(
        np.arange(0.0, 151.0, 1.0),
        "AGB",
        list(rounds.custom.values()),
        hc_params,
        printout=False,
        round_scores_up=True,
        clean_gaps=True,
        filename="custom_table.dat",
        int_prec=True,
    )






    # Print the continuous score that is comes from this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 51., "AGB", hc_params, round_score_up=False
    )
    print(
        f"A handicap of 51. on a {rounds.AGB_outdoor_imperial.york.name} is a continuous score of {score_from_hc}."
    )

        # Print the continuous score that is comes from this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 50.0, "AGB", hc_params, round_score_up=False
    )
    print(
        f"A handicap of 50.0 on a {rounds.AGB_outdoor_imperial.york.name} is a continuous score of {score_from_hc}."
    )

        # Print the continuous score that is comes from this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 49., "AGB", hc_params, round_score_up=False
    )
    print(
        f"A handicap of 49. on a {rounds.AGB_outdoor_imperial.york.name} is a continuous score of {score_from_hc}."
    )

    # Print the minimum discrete score that is required to get this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 51, "AGB", hc_params, round_score_up=True
    )
    print(
        f"A handicap of 51 on a {rounds.AGB_outdoor_imperial.york.name} requires a minimum score of {score_from_hc}."
    )

        # Print the minimum discrete score that is required to get this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 50, "AGB", hc_params, round_score_up=True
    )
    print(
        f"A handicap of 50 on a {rounds.AGB_outdoor_imperial.york.name} requires a minimum score of {score_from_hc}."
    )

        # Print the minimum discrete score that is required to get this handicap
    score_from_hc = hc_eq.score_for_round(
        rounds.AGB_outdoor_imperial.york, 49, "AGB", hc_params, round_score_up=True
    )
    print(
        f"A handicap of 49 on a {rounds.AGB_outdoor_imperial.york.name} requires a minimum score of {score_from_hc}."
    )

    # Print score for a certain handicap - continuous
    hc_from_score = hc_func.handicap_from_score(
        706, rounds.AGB_outdoor_imperial.york, "AGB", hc_params, int_prec=False
    )
    print(
        f"A score of 706 on a {rounds.AGB_outdoor_imperial.york.name} is a continuous handicap of {hc_from_score}."
    )
    hc_from_score = hc_func.handicap_from_score(
        705, rounds.AGB_outdoor_imperial.york, "AGB", hc_params, int_prec=False
    )
    print(
        f"A score of 705 on a {rounds.AGB_outdoor_imperial.york.name} is a continuous handicap of {hc_from_score}."
    )
    hc_from_score = hc_func.handicap_from_score(
        704, rounds.AGB_outdoor_imperial.york, "AGB", hc_params, int_prec=False
    )
    print(
        f"A score of 704 on a {rounds.AGB_outdoor_imperial.york.name} is a continuous handicap of {hc_from_score}."
    )

    # Print score for a certain handicap - discrete
    hc_from_score = hc_func.handicap_from_score(
        704, rounds.AGB_outdoor_imperial.york, "AGB", hc_params, int_prec=True
    )
    print(
        f"A score of 704 on a {rounds.AGB_outdoor_imperial.york.name} is a discrete handicap of {hc_from_score}."
    )
    hc_from_score = hc_func.handicap_from_score(
        705, rounds.AGB_outdoor_imperial.york, "AGB", hc_params, int_prec=True
    )
    print(
        f"A score of 705 on a {rounds.AGB_outdoor_imperial.york.name} is a discrete handicap of {hc_from_score}."
    )
    hc_from_score = hc_func.handicap_from_score(
        706, rounds.AGB_outdoor_imperial.york, "AGB", hc_params, int_prec=True
    )
    print(
        f"A score of 706 on a {rounds.AGB_outdoor_imperial.york.name} is a discrete handicap of {hc_from_score}."
    )
