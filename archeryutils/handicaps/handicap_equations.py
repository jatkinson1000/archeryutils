# Author        : Jack Atkinson
#
# Contributors  : Jack Atkinson
#
# Date Created  : 2022-08-15
# Last Modified : 2022-08-22 by Jack Atkinson
#
# Summary       : Code for archery calculating handicaps using various systems
#

import numpy as np
import json
from dataclasses import dataclass


@dataclass
class HcParams:
    # KEY PARAMETERS AND CONSTANTS FOR NEW AGB HANDICAP SCHEME
    AGB_datum = 5.75  # offset required to set handicap 0 at desired score
    AGB_step = 3.5  # percentage change in group size for each handicap step
    AGB_ang_0 = 5.0e-4  # baseline angle used for group size 0.5 [millirad]
    AGB_kd = 0.00365  # distance scaling factor [1/metres]

    # KEY PARAMETERS AND CONSTANTS FOR OLD AGB HANDICAP SCHEME
    AGBo_datum = 12.9  # offset required to set handicap 0 at desired score
    AGBo_step = 3.5  # percentage change in group size for each handicap step
    AGBo_ang_0 = 5.0e-4  # baseline angle used for group size 0.5 [millirad]
    AGBo_k1 = 1.429e-6  # constant used in handicap equation
    AGBo_k2 = 1.07  # constant used in handicap equation
    AGBo_k3 = 4.3  # constant used in handicap equation
    AGBo_p1 = 2.0  # exponent of distance scaling
    AGB0_arw_d = 7.14e-3  # arrow diameter used in the old AGB algorithm by D. Lane

    # KEY PARAMETERS AND CONSTANTS FOR THE ARCHERY AUSTRALIA SCHEME
    AA_k0 = 2.37  # offset required to set handicap 100 at desired score
    AA_ks = 0.027  # change with each step of geometric progression
    AA_kd = 0.004  # distance scaling factor [1/metres]

    # KEY PARAMETERS AND CONSTANTS FOR THE UPDATED ARCHERY AUSTRALIA SCHEME
    AA2_k0 = 2.57  # offset required to set handicap 100 at desired score
    AA2_ks = 0.027  # change with each step of geometric progression
    AA2_f1 = 0.815  # 'linear' scaling factor
    AA2_f2 = 0.185  # 'quadratic' scaling factor
    AA2_d0 = 50.0  # Normalisation distance [metres]

    # DEFAULT ARROW DIAMETER
    arw_d_in = 9.3e-3  # Diameter of an indoor arrow [metres]
    arw_d_out = 5.5e-3  # Diameter of an outdoor arrow [metres]

    @classmethod
    def load_json_params(cls, jsonpath):
        json_HcParams = cls()
        with open(jsonpath, "r") as read_file:
            paramsdict = json.load(read_file)
        json_HcParams.AGB_datum = paramsdict["AGB_datum"]
        json_HcParams.AGB_step = paramsdict["AGB_step"]
        json_HcParams.AGB_ang_0 = paramsdict["AGB_ang_0"]
        json_HcParams.AGB_kd = paramsdict["AGB_kd"]
        json_HcParams.AGBo_datum = paramsdict["AGBo_datum"]
        json_HcParams.AGBo_step = paramsdict["AGBo_step"]
        json_HcParams.AGBo_ang_0 = paramsdict["AGBo_ang_0"]
        json_HcParams.AGBo_k1 = paramsdict["AGBo_k1"]
        json_HcParams.AGBo_k2 = paramsdict["AGBo_k2"]
        json_HcParams.AGBo_k3 = paramsdict["AGBo_k3"]
        json_HcParams.AGBo_p1 = paramsdict["AGBo_p1"]
        json_HcParams.AGB0_arw_d = paramsdict["AGB0_arw_d"]
        json_HcParams.AA_k0 = paramsdict["AA_k0"]
        json_HcParams.AA_ks = paramsdict["AA_ks"]
        json_HcParams.AA_kd = paramsdict["AA_kd"]
        json_HcParams.AA2_k0 = paramsdict["AA2_k0"]
        json_HcParams.AA2_ks = paramsdict["AA2_ks"]
        json_HcParams.AA2_f1 = paramsdict["AA2_f1"]
        json_HcParams.AA2_f2 = paramsdict["AA2_f2"]
        json_HcParams.AA2_d0 = paramsdict["AA2_d0"]
        json_HcParams.arw_d_in = paramsdict["arrow_diameter_indoors"]
        json_HcParams.arw_d_out = paramsdict["arrow_diameter_outdoors"]

        return json_HcParams


def sigma_t(h, hc_sys, dist, hc_dat):
    """
    function sigma_t
    Calculates the angular deviation for a given handicap scheme, handicap value,
    and distance.

    Parameters
    ----------
    h : ndarray or float
        handicap to calculate sigma_t at
    hc_sys : str
        identifier for handicap system
    dist : float or ndarray
        distance to target [metres]
    hc_dat : HcParams
        dataclass containing parameters for handicap equations

    Returns
    -------
    sigma_t : float or ndarray
        angular deviation [rad]

    References
    ----------
    - The construction of the graduated handicap tables for target archery
      Lane, D (2013)
      https://www.jackatkinson.net/files/Handicap_Tables_2013.pdf
    - Modelling archers’ scores at different distances to quantify score loss due to
      equipment selection and technique errors
      Park, J (2014)
      https://doi.org/10.1177%2F1754337114539308
    """

    if hc_sys == "AGB":
        # New AGB (Archery GB) System
        # Written by Jack Atkinson
        sig_t = (
            hc_dat.AGB_ang_0
            * ((1.0 + hc_dat.AGB_step / 100.0) ** (h + hc_dat.AGB_datum))
            * np.exp(hc_dat.AGB_kd * dist)
        )

    elif hc_sys == "AGBold":
        # Old AGB (Archery GB) System
        # Written by David Lane (2013)
        K = hc_dat.AGBo_k1 * hc_dat.AGBo_k2 ** (h + hc_dat.AGBo_k3)
        F = 1 + K * dist**hc_dat.AGBo_p1
        sig_t = (
            hc_dat.AGBo_ang_0
            * ((1.0 + hc_dat.AGBo_step / 100.0) ** (h + hc_dat.AGBo_datum))
            * F
        )

    elif hc_sys == "AA":
        # Original Archery Australia (AA) System
        # Factor of sqrt(2) to deal with factor of 2 in differing definitions of sigma
        # between AGB and AA
        # Required so code elsewhere is unchanged
        # Factor of 1.0e-3 due to AA algorithm specifying sigma t in milliradians, so
        # convert to rad
        sig_t = (
            1.0e-3
            * np.sqrt(2)
            * np.exp(hc_dat.AA_k0 - hc_dat.AA_ks * h + hc_dat.AA_kd * dist)
        )

    elif hc_sys == "AA2":
        # Updated Archery Australia (AA) System
        # Factor of sqrt(2) to deal with factor of 2 in differing definitions of sigma
        # between AGB and AA
        # Required so code elsewhere is unchanged
        # Factor of 1.0e-3 due to AA algorithm specifying sigma t in milliradians, so
        # convert to rad
        sig_t = (
            np.sqrt(2)
            * 1.0e-3
            * np.exp(hc_dat.AA2_k0 - hc_dat.AA2_ks * h)
            * (hc_dat.AA2_f1 + hc_dat.AA2_f2 * dist / hc_dat.AA2_d0)
        )

    # elif hc_sys == 'AA2AGB':
    #     # AA2AGB System
    #     # Same starting point HC0 as AGB, but using AA distance scaling
    #     F = np.exp(ap.k_d * dist)
    #     sig_t = ((1.0 + ap.step / 100.0) ** (h + ap.datum)) * ap.ang_0 * F

    else:
        raise ValueError(
            "Invalid Handicap System specified.\n"
            "Please select from 'AGB', 'AGBold', 'AA', or 'AA2'."
        )

    return sig_t


def sigma_r(h, hc_sys, dist, hc_dat):
    """
    function sigma_r
    Calculates the angular deviation for a given handicap scheme, handicap value
    Wraps around sigma_t() and multiplies by distance

    Parameters
    ----------
    h : ndarray or float
        handicap to calculate sigma_t at
    hc_sys : str
        identifier for handicap system
    dist : float or ndarray
        distance to target [m]
    hc_dat : HcParams
        dataclass containing parameters for handicap equations

    Returns
    -------
    sig_r : float or ndarray
        standard deviation of group size [metres]

    References
    ----------
    """
    sig_t = sigma_t(h, hc_sys, dist, hc_dat)
    sig_r = dist * sig_t

    return sig_r


def arrow_score(target, h, hc_sys, hc_dat, arw_d=None):
    """
    Subroutine to calculate the average arrow score for a given
    target and handicap rating.

    Parameters
    ----------
    target : targets.Target
        A Target class specifying the target to be used
    h : ndarray or float
        handicap value to calculate score for
    hc_sys : string
        identifier for the handicap system
    hc_dat : HcParams
        dataclass containing parameters for handicap equations
    arw_d : float
        arrow diameter in [metres]

    Returns
    -------
    s_bar : float
        average score of the arrow for this set of parameters

    References
    ----------
    """
    # Set arrow diameter. Use provided, if AGBold scheme set value, otherwise select
    # default from params based on in/out
    if arw_d is None:
        if hc_sys == "AGBold":
            arw_rad = hc_dat.AGB0_arw_d / 2.0
        else:
            if target.indoor:
                arw_rad = hc_dat.arw_d_in / 2.0
            else:
                arw_rad = hc_dat.arw_d_out / 2.0
    else:
        arw_rad = arw_d / 2.0

    tar_dia = target.diameter
    sig_r = sigma_r(h, hc_sys, target.distance, hc_dat)

    if target.scoring_system == "5_zone":
        s_bar = (
            9
            - 2
            * sum(
                np.exp(-((((n * tar_dia / 10) + arw_rad) / sig_r) ** 2))
                for n in range(1, 5)
            )
            - np.exp(-((((5 * tar_dia / 10) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "10_zone":
        s_bar = 10 - sum(
            np.exp(-((((n * tar_dia / 20) + arw_rad) / sig_r) ** 2))
            for n in range(1, 11)
        )

    elif target.scoring_system == "10_zone_6_ring":
        s_bar = (
            10
            - sum(
                np.exp(-((((n * tar_dia / 20) + arw_rad) / sig_r) ** 2))
                for n in range(1, 6)
            )
            - 5.0 * np.exp(-((((6 * tar_dia / 20) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "10_zone_compound":
        s_bar = (
            10
            - np.exp(-((((tar_dia / 40) + arw_rad) / sig_r) ** 2))
            - sum(
                np.exp(-((((n * tar_dia / 20) + arw_rad) / sig_r) ** 2))
                for n in range(2, 11)
            )
        )

    elif target.scoring_system == "10_zone_5_ring":
        s_bar = (
            10
            - sum(
                np.exp(-((((n * tar_dia / 20) + arw_rad) / sig_r) ** 2))
                for n in range(1, 5)
            )
            - 6.0 * np.exp(-((((5 * tar_dia / 20) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "10_zone_5_ring_compound":
        s_bar = (
            10
            - np.exp(-((((tar_dia / 40) + arw_rad) / sig_r) ** 2))
            - sum(
                np.exp(-((((n * tar_dia / 20) + arw_rad) / sig_r) ** 2))
                for n in range(2, 5)
            )
            - 6.0 * np.exp(-((((5 * tar_dia / 20) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "WA_field":
        s_bar = (
            6
            - np.exp(-((((tar_dia / 20) + arw_rad) / sig_r) ** 2))
            - sum(
                np.exp(-((((n * tar_dia / 10) + arw_rad) / sig_r) ** 2))
                for n in range(2, 7)
            )
        )

    elif target.scoring_system == "IFAA_field":
        s_bar = (
            5
            - np.exp(-((((tar_dia / 10) + arw_rad) / sig_r) ** 2))
            - np.exp(-((((3 * tar_dia / 10) + arw_rad) / sig_r) ** 2))
            - 3.0 * np.exp(-((((5 * tar_dia / 10) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "Beiter_hit_miss":
        s_bar = 1 - np.exp(-((((tar_dia / 2) + arw_rad) / sig_r) ** 2))

    elif target.scoring_system == "Worcester":
        s_bar = 5 - sum(
            np.exp(-((((n * tar_dia / 10) + arw_rad) / sig_r) ** 2))
            for n in range(1, 6)
        )

    elif target.scoring_system == "Worcester_2_ring":
        s_bar = (
            5
            - np.exp(-((((tar_dia / 10) + arw_rad) / sig_r) ** 2))
            - 4.0 * np.exp(-((((2 * tar_dia / 10) + arw_rad) / sig_r) ** 2))
        )

    # elif target.scoring_system == 12:
    # Worcester with an extra point for the 'x' ring
    #     s_bar = 6 - np.exp(-(((tar_dia / 20.32) + arw_rad) / sig_r) ** 2) -\
    #             np.exp(-(((tar_dia / 10) + arw_rad) / sig_r) ** 2)\
    #             - 4.0 * np.exp(-(((2 * tar_dia / 10) + arw_rad) / sig_r) ** 2)

    else:
        raise ValueError(
            f"No rule for calculating scoring for face type {target.scoring_system}."
        )

    return s_bar


def score_for_round(rnd, h, hc_sys, hc_dat, arw_d=None, round_score_up=True):
    """
    Subroutine to calculate the average arrow score for a given
    target and handicap rating.

    Parameters
    ----------
    rnd : rounds.Round
        A Round class specifying the round being shot
    h : ndarray or float
        handicap value to calculate score for
    hc_sys : string
        identifier for the handicap system
    hc_dat : HcParams
        dataclass containing parameters for handicap equations
    arw_d : float
        arrow diameter in [metres] default = None -> (use defaults)
    round_score_up : bool
        round score up to nearest integer value


    Returns
    -------
    round_score : float
        average score of the round for this set of parameters
    pass_score : list of float
        average score for each pass in the round

    References
    ----------
    """

    pass_score = []
    for Pass_i in rnd.passes:
        pass_score.append(
            Pass_i.n_arrows * arrow_score(Pass_i.target, h, hc_sys, hc_dat, arw_d=arw_d)
        )

    round_score = np.sum(pass_score, axis=0)

    if round_score_up:
        round_score = np.ceil(round_score)

    return round_score, pass_score
