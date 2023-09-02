"""
Code for archery handicap scheme calculations using various schemes.

Extended Summary
----------------
Code to calculate information using a number of schemes:
  - Old Archery GB (D Lane)
  - New Archery GB (J Atkinson, 2023)
  - Old Archery Australia (J Park)
  - New Archery Australia (J Park)
Calculates arrow and round scores for a variety of target faces of given
distance and diameter:
  - 5-zone
  - 10-zone
  - 10-zone 6-ring
  - 10-zone compound
  - 10-zone 5-ring
  - 10-zone 5-ring compound
  - WA_field
  - IFAA_field
  - Beiter-hit-miss
  - Worcester
  - Worcester 2-ring)

Routine Listings
----------------
HcParams
sigma_t
sigma_r
arrow_score
score_for_round

References
----------
Old AGB - D Lane
New AGB - J Atkinson
AA & AA2 - J Park
"""
import json
from typing import Union, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt

from archeryutils import targets, rounds


@dataclass
class HcParams:
    """
    Class to hold information for various handicap schemes.

    Attributes
    ----------
    KEY PARAMETERS AND CONSTANTS FOR NEW AGB HANDICAP SCHEME
    AGB_datum : float
        offset required to set handicap 0 at desired score
    AGB_step : float
        percentage change in group size for each handicap step
    AGB_ang_0 : float
        baseline angle used for group size 0.5 [millirad]
    AGB_kd : float
        distance scaling factor [1/metres]

    KEY PARAMETERS AND CONSTANTS FOR OLD AGB HANDICAP SCHEME
    AGBo_datum : float
        offset required to set handicap 0 at desired score
    AGBo_step : float
        percentage change in group size for each handicap step
    AGBo_ang_0 : float
        baseline angle used for group size 0.5 [millirad]
    AGBo_k1 : float
        constant used in handicap equation
    AGBo_k2 : float
        constant used in handicap equation
    AGBo_k3 : float
        constant used in handicap equation
    AGBo_p1 : float
        exponent of distance scaling

    KEY PARAMETERS AND CONSTANTS FOR THE ARCHERY AUSTRALIA SCHEME
    AA_k0 : float
        offset required to set handicap 100 at desired score
    AA_ks : float
        change with each step of geometric progression
    AA_kd : float
        distance scaling factor [1/metres]

    KEY PARAMETERS AND CONSTANTS FOR THE UPDATED ARCHERY AUSTRALIA SCHEME
    AA2_k0 : float
        offset required to set handicap 100 at desired score
    AA2_ks : float
        change with each step of geometric progression
    AA2_f1 : float
        'linear' scaling factor
    AA2_f2 : float
        'quadratic' scaling factor
    AA2_d0 : float
        Normalisation distance [metres]

    DEFAULT ARROW DIAMETER
    arw_d_in : float
        Diameter of an indoor arrow [metres]
    arw_d_out : float
        Diameter of an outdoor arrow [metres]
    AGBo_arw_d : float
        arrow diameter used in the old AGB algorithm by D. Lane [metres]
    AA_arw_d_out : float
        Diameter of an outdoor arrow in the Archery Australia scheme [metres]

    """

    agb_hc_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "AGB_datum": 6.0,
                "AGB_step": 3.5,
                "AGB_ang_0": 5.0e-4,
                "AGB_kd": 0.00365,
            }
        )
    )

    agb_old_hc_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "AGBo_datum": 12.9,
                "AGBo_step": 3.6,
                "AGBo_ang_0": 5.0e-4,
                "AGBo_k1": 1.429e-6,
                "AGBo_k2": 1.07,
                "AGBo_k3": 4.3,
                "AGBo_p1": 2.0,
            }
        )
    )

    aa_hc_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "AA_k0": 2.37,
                "AA_ks": 0.027,
                "AA_kd": 0.004,
            }
        )
    )

    aa2_hc_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "AA2_k0": 2.57,
                "AA2_ks": 0.027,
                "AA2_f1": 0.815,
                "AA2_f2": 0.185,
                "AA2_d0": 50.0,
            }
        )
    )

    arw_d_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "arw_d_in": 9.3e-3,
                "arw_d_out": 5.5e-3,
                "AGBo_arw_d": 7.14e-3,
                "AA_arw_d_out": 5.0e-3,
            }
        )
    )

    @classmethod
    def load_json_params(cls, jsonpath: str) -> "HcParams":
        """
        Class method to load params from a json file.

        Parameters
        ----------
        jsonpath : str
            path to json file with handicap parameters

        Returns
        -------
        json_hc_params : HcParams
            dataclass of handicap parameters read from file

        """
        json_hc_params: "HcParams" = cls()
        with open(jsonpath, "r", encoding="utf-8") as read_file:
            paramsdict = json.load(read_file)
        json_hc_params.agb_hc_data["AGB_datum"] = paramsdict["AGB_datum"]
        json_hc_params.agb_hc_data["AGB_step"] = paramsdict["AGB_step"]
        json_hc_params.agb_hc_data["AGB_ang_0"] = paramsdict["AGB_ang_0"]
        json_hc_params.agb_hc_data["AGB_kd"] = paramsdict["AGB_kd"]
        json_hc_params.agb_old_hc_data["AGBo_datum"] = paramsdict["AGBo_datum"]
        json_hc_params.agb_old_hc_data["AGBo_step"] = paramsdict["AGBo_step"]
        json_hc_params.agb_old_hc_data["AGBo_ang_0"] = paramsdict["AGBo_ang_0"]
        json_hc_params.agb_old_hc_data["AGBo_k1"] = paramsdict["AGBo_k1"]
        json_hc_params.agb_old_hc_data["AGBo_k2"] = paramsdict["AGBo_k2"]
        json_hc_params.agb_old_hc_data["AGBo_k3"] = paramsdict["AGBo_k3"]
        json_hc_params.agb_old_hc_data["AGBo_p1"] = paramsdict["AGBo_p1"]
        json_hc_params.aa_hc_data["AA_k0"] = paramsdict["AA_k0"]
        json_hc_params.aa_hc_data["AA_ks"] = paramsdict["AA_ks"]
        json_hc_params.aa_hc_data["AA_kd"] = paramsdict["AA_kd"]
        json_hc_params.aa2_hc_data["AA2_k0"] = paramsdict["AA2_k0"]
        json_hc_params.aa2_hc_data["AA2_ks"] = paramsdict["AA2_ks"]
        json_hc_params.aa2_hc_data["AA2_f1"] = paramsdict["AA2_f1"]
        json_hc_params.aa2_hc_data["AA2_f2"] = paramsdict["AA2_f2"]
        json_hc_params.aa2_hc_data["AA2_d0"] = paramsdict["AA2_d0"]
        json_hc_params.arw_d_data["arw_d_in"] = paramsdict[
            "arrow_diameter_indoors"
        ]
        json_hc_params.arw_d_data["arw_d_out"] = paramsdict[
            "arrow_diameter_outdoors"
        ]
        json_hc_params.arw_d_data["AGBo_arw_d"] = paramsdict["AGBo_arw_d"]
        json_hc_params.arw_d_data["AA_arw_d_out"] = paramsdict["AA_arw_d_out"]

        return json_hc_params


def sigma_t(
    handicap: Union[float, npt.NDArray[np.float_]],
    hc_sys: str,
    dist: float,
    hc_dat: HcParams,
) -> Union[float, np.float_, npt.NDArray[np.float_]]:
    """
    Calculate angular deviation for given scheme, handicap, and distance.

    Parameters
    ----------
    handicap : ndarray or float
        handicap to calculate sigma_t at
    hc_sys : str
        identifier for handicap system
    dist : float
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
    # Declare sig_t type for mypy
    sig_t: Union[float, npt.NDArray[np.float_]]

    if hc_sys == "AGB":
        # New AGB (Archery GB) System
        # Written by Jack Atkinson
        hc_data = hc_dat.agb_hc_data
        sig_t = (
            hc_data["AGB_ang_0"]
            * ((1.0 + hc_data["AGB_step"] / 100.0) ** (handicap + hc_data["AGB_datum"]))
            * np.exp(hc_data["AGB_kd"] * dist)
        )

    elif hc_sys == "AGBold":
        # Old AGB (Archery GB) System
        # Written by David Lane (2013)
        hc_data = hc_dat.agb_old_hc_data
        k_factor = hc_data["AGBo_k1"] * hc_data["AGBo_k2"] ** (
            handicap + hc_data["AGBo_k3"]
        )
        f_factor = 1.0 + k_factor * dist ** hc_data["AGBo_p1"]
        sig_t = (
            hc_data["AGBo_ang_0"]
            * (
                (1.0 + hc_data["AGBo_step"] / 100.0)
                ** (handicap + hc_data["AGBo_datum"])
            )
            * f_factor
        )

    elif hc_sys == "AA":
        # Original Archery Australia (AA) System
        # Factor of sqrt(2) to deal with factor of 2 in differing definitions of sigma
        # between AGB and AA
        # Required so code elsewhere is unchanged
        # Factor of 1.0e-3 due to AA algorithm specifying sigma t in milliradians, so
        # convert to rad
        hc_data = hc_dat.aa_hc_data
        sig_t = (
            1.0e-3
            * np.sqrt(2.0)
            * np.exp(
                hc_data["AA_k0"] - hc_data["AA_ks"] * handicap + hc_data["AA_kd"] * dist
            )
        )

    elif hc_sys == "AA2":
        # Updated Archery Australia (AA) System
        # Factor of sqrt(2) to deal with factor of 2 in differing definitions of sigma
        # between AGB and AA
        # Required so code elsewhere is unchanged
        # Factor of 1.0e-3 due to AA algorithm specifying sigma t in milliradians, so
        # convert to rad
        hc_data = hc_dat.aa2_hc_data
        sig_t = (
            np.sqrt(2.0)
            * 1.0e-3
            * np.exp(hc_data["AA2_k0"] - hc_data["AA2_ks"] * handicap)
            * (hc_data["AA2_f1"] + hc_data["AA2_f2"] * dist / hc_data["AA2_d0"])
        )

    else:
        raise ValueError(
            "Invalid Handicap System specified.\n"
            "Please select from 'AGB', 'AGBold', 'AA', or 'AA2'."
        )

    return sig_t


def sigma_r(
    handicap: Union[float, npt.NDArray[np.float_]],
    hc_sys: str,
    dist: float,
    hc_dat: HcParams,
) -> Union[float, np.float_, npt.NDArray[np.float_]]:
    """
    Calculate deviation for a given scheme and handicap value.

    Standard deviation as a proxy for 'group size' based on
    handicap parameters, scheme, and distance.
    Wraps around sigma_t() and multiplies by distance.

    Parameters
    ----------
    handicap : ndarray or float
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
    """
    sig_t = sigma_t(handicap, hc_sys, dist, hc_dat)
    sig_r = dist * sig_t

    return sig_r


def arrow_score(
    target: targets.Target,
    handicap: Union[float, npt.NDArray[np.float_]],
    hc_sys: str,
    hc_dat: HcParams,
    arw_d: Optional[float] = None,
) -> Union[float, np.float_, npt.NDArray[np.float_]]:
    # Six too many branches. Makes sense due to different target faces => disable
    # pylint: disable=too-many-branches
    """
    Calculate the average arrow score for a given target and handicap rating.

    Parameters
    ----------
    target : targets.Target
        A Target class specifying the target to be used
    handicap : ndarray or float
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
    - The construction of the graduated handicap tables for target archery
      Lane, D (2013)
    """
    # Set arrow diameter. Use provided, if AGBold or AA/AA2 scheme set value,
    # otherwise select default from params based on in-/out-doors
    if arw_d is None:
        if hc_sys == "AGBold":
            arw_rad = hc_dat.arw_d_data["AGBo_arw_d"] / 2.0
        else:
            if target.indoor:
                arw_rad = hc_dat.arw_d_data["arw_d_in"] / 2.0
            else:
                if hc_sys in ("AA", "AA2"):
                    arw_rad = hc_dat.arw_d_data["AA_arw_d_out"] / 2.0
                else:
                    arw_rad = hc_dat.arw_d_data["arw_d_out"] / 2.0
    else:
        arw_rad = arw_d / 2.0

    tar_dia = target.diameter
    sig_r = sigma_r(handicap, hc_sys, target.distance, hc_dat)

    if target.scoring_system == "5_zone":
        s_bar = (
            9.0
            - 2.0
            * sum(
                np.exp(-((((n * tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
                for n in range(1, 5)
            )
            - np.exp(-((((5.0 * tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "10_zone":
        s_bar = 10.0 - sum(
            np.exp(-((((n * tar_dia / 20.0) + arw_rad) / sig_r) ** 2))
            for n in range(1, 11)
        )

    elif target.scoring_system == "10_zone_6_ring":
        s_bar = (
            10.0
            - sum(
                np.exp(-((((n * tar_dia / 20.0) + arw_rad) / sig_r) ** 2))
                for n in range(1, 6)
            )
            - 5.0 * np.exp(-((((6.0 * tar_dia / 20.0) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "10_zone_compound":
        s_bar = (
            10.0
            - np.exp(-((((tar_dia / 40.0) + arw_rad) / sig_r) ** 2))
            - sum(
                np.exp(-((((n * tar_dia / 20.0) + arw_rad) / sig_r) ** 2))
                for n in range(2, 11)
            )
        )

    elif target.scoring_system == "10_zone_5_ring":
        s_bar = (
            10.0
            - sum(
                np.exp(-((((n * tar_dia / 20.0) + arw_rad) / sig_r) ** 2))
                for n in range(1, 5)
            )
            - 6.0 * np.exp(-((((5.0 * tar_dia / 20.0) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "10_zone_5_ring_compound":
        s_bar = (
            10.0
            - np.exp(-((((tar_dia / 40) + arw_rad) / sig_r) ** 2))
            - sum(
                np.exp(-((((n * tar_dia / 20) + arw_rad) / sig_r) ** 2))
                for n in range(2, 5)
            )
            - 6.0 * np.exp(-((((5 * tar_dia / 20) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "WA_field":
        s_bar = (
            6.0
            - np.exp(-((((tar_dia / 20.0) + arw_rad) / sig_r) ** 2))
            - sum(
                np.exp(-((((n * tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
                for n in range(2, 7)
            )
        )

    elif target.scoring_system == "IFAA_field":
        s_bar = (
            5.0
            - np.exp(-((((tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
            - np.exp(-((((3.0 * tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
            - 3.0 * np.exp(-((((5.0 * tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
        )

    elif target.scoring_system == "Beiter_hit_miss":
        s_bar = 1.0 - np.exp(-((((tar_dia / 2.0) + arw_rad) / sig_r) ** 2))

    elif target.scoring_system in ("Worcester", "IFAA_field_expert"):
        s_bar = 5.0 - sum(
            np.exp(-((((n * tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
            for n in range(1, 6)
        )

    elif target.scoring_system == "Worcester_2_ring":
        s_bar = (
            5.0
            - np.exp(-((((tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
            - 4.0 * np.exp(-((((2 * tar_dia / 10.0) + arw_rad) / sig_r) ** 2))
        )

    else:
        raise ValueError(
            f"No rule for calculating scoring for face type {target.scoring_system}."
        )

    return s_bar


def score_for_round(
    rnd: rounds.Round,
    handicap: Union[float, npt.NDArray[np.float_]],
    hc_sys: str,
    hc_dat: HcParams,
    arw_d: Optional[float] = None,
    round_score_up: bool = True,
) -> Tuple[Union[float, np.float_, npt.NDArray[np.float_]], npt.NDArray[np.float_]]:
    """
    Calculate the average arrow score for a given target and handicap rating.

    Parameters
    ----------
    rnd : rounds.Round
        A Round class specifying the round being shot
    handicap : ndarray or float
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

    """
    # Two too many arguments. Makes sense at the moment => disable
    # Could try and simplify hc_sys and hc_dat in future refactor
    # pylint: disable=too-many-arguments
    pass_score = np.array(
        [
            pass_i.n_arrows
            * arrow_score(pass_i.target, handicap, hc_sys, hc_dat, arw_d=arw_d)
            for pass_i in rnd.passes
        ]
    )

    round_score = np.sum(pass_score, axis=0)

    if round_score_up:
        # Old AGB system uses plain rounding rather than ceil of other schemes
        if hc_sys in ("AGBold", "AA", "AA2"):
            round_score = np.around(round_score)
        else:
            round_score = np.ceil(round_score)

    return round_score, pass_score
