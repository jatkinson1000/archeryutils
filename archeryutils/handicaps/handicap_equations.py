"""
Code for archery handicap calculations using various handicap schemes.

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
- Worcester 2-ring

Routine Listings
----------------
- HcParams Class
- sigma_t
- sigma_r
- arrow_score
- score_for_passes
- score_for_round

References
----------
- Old AGB: The construction of the graduated handicap tables for target archery
  Lane, D (2013)
  https://www.jackatkinson.net/files/Handicap_Tables_2013.pdf
- New AGB: Atkinson, J
- AA: Modelling archers’ scores at different distances to quantify score loss due to
  equipment selection and technique errors
  Park, J (2014)
  https://doi.org/10.1177%2F1754337114539308

"""
import json
from typing import Optional, TypeVar

from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt

from archeryutils import targets, rounds

FloatArray = TypeVar('FloatArray', float, np.float_, npt.NDArray[np.float_])

@dataclass
class HcParams:
    """Class to hold information for various handicap schemes."""

    # Key values for the new Archery GB handicap scheme [Atkinson].
    agb_hc_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "AGB_datum": 6.0,  # Offset required to set handicap 0 at desired score.
                "AGB_step": 3.5,  # Percentage change in group size for each handicap step.
                "AGB_ang_0": 5.0e-4,  # Baseline angle used for group size 0.5 [millirad].
                "AGB_kd": 0.00365,  # Distance scaling factor [1/metres].
            }
        )
    )

    # Key values for the old Archery GB handicap scheme [Lane].
    agb_old_hc_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "AGBo_datum": 12.9,  # Offset required to set handicap 0 at desired score.
                "AGBo_step": 3.6,  # Percentage change in group size for each handicap step.
                "AGBo_ang_0": 5.0e-4,  # Baseline angle used for group size 0.5 [millirad].
                "AGBo_k1": 1.429e-6,  # Constant 1 used in handicap equation.
                "AGBo_k2": 1.07,  # Constant 2 used in handicap equation.
                "AGBo_k3": 4.3,  # Constant 3 used in handicap equation.
                "AGBo_p1": 2.0,  # Exponent of distance scaling.
            }
        )
    )

    # Key values for the original Archery Australia scheme [Park].
    aa_hc_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "AA_k0": 2.37,  # Offset required to set handicap 100 at desired score.
                "AA_ks": 0.027,  # Change with each step of geometric progression.
                "AA_kd": 0.004,  # Distance scaling factor [1/metres].
            }
        )
    )

    # Key values for the new Archery Australia scheme [Park].
    aa2_hc_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "AA2_k0": 2.57,  # Offset required to set handicap 100 at desired score.
                "AA2_ks": 0.027,  # Change with each step of geometric progression.
                "AA2_f1": 0.815,  # 'Linear' scaling factor.
                "AA2_f2": 0.185,  # 'Quadratic' scaling factor.
                "AA2_d0": 50.0,  # Normalisation distance [metres].
            }
        )
    )

    # Key values for arrow diameter in the different schemes.
    arw_d_data: dict[str, float] = field(
        default_factory=lambda: (
            {
                "arw_d_in": 9.3e-3,  # Diameter of an indoor arrow [metres].
                "arw_d_out": 5.5e-3,  # Diameter of an outdoor arrow for AGB [metres].
                "AGBo_arw_d": 7.14e-3,  # Diameter of an arrow in the old AGB algorithm [metres].
                "AA_arw_d_out": 5.0e-3,  # Diameter of an outdoor arrow for AA [metres].
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
        json_hc_params.arw_d_data["arw_d_in"] = paramsdict["arrow_diameter_indoors"]
        json_hc_params.arw_d_data["arw_d_out"] = paramsdict["arrow_diameter_outdoors"]
        json_hc_params.arw_d_data["AGBo_arw_d"] = paramsdict["AGBo_arw_d"]
        json_hc_params.arw_d_data["AA_arw_d_out"] = paramsdict["AA_arw_d_out"]

        return json_hc_params


def sigma_t(
    handicap: FloatArray,
    hc_sys: str,
    dist: float,
    hc_dat: HcParams,
) -> FloatArray:
    """
    Calculate angular deviation for given scheme, handicap, and distance.

    Parameters
    ----------
    handicap : float or ndarray
        handicap to calculate sigma_t at
    hc_sys : str
        identifier for handicap system
    dist : float
        distance to target [metres]
    hc_dat : HcParams
        dataclass containing parameters for handicap equations

    Returns
    -------
    sig_t : float or ndarray
        angular deviation [rad]

    Raises
    ------
    ValueError
        If no valid handicap scheme is specified

    Examples
    --------
    Angular deviation at a distance of 25m, using the AGB handicap system at a
    handicap of 10 can be calculated with:

    >>> import archeryutils.handicap_equations as hc_eq
    >>> hc_params = hc_eq.HcParams()
    >>> hc_eq.sigma_t(10.0, "AGB", 25.0, hc_params)
    0.0009498280098103058

    It can also be passed an array of handicaps:

    >>> hc_eq.sigma_t(np.asarray([10.0, 50.0, 100.0]), "AGB", 25.0, hc_params)
    array([0.00094983, 0.00376062, 0.02100276])

    """
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
    handicap: FloatArray,
    hc_sys: str,
    dist: float,
    hc_dat: HcParams,
) -> FloatArray:
    """
    Calculate deviation for a given scheme and handicap value.

    Standard deviation as a proxy for 'group size' based on
    handicap parameters, scheme, and distance.
    Wraps around sigma_t() and multiplies by distance.

    Parameters
    ----------
    handicap : float or ndarray
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

    Examples
    --------
    Deviation (in metres) at a distance of 25m, using the AGB handicap system at a
    handicap of 10 can be calculated with:

    >>> import archeryutils.handicap_equations as hc_eq
    >>> hc_params = hc_eq.HcParams()
    >>> hc_eq.sigma_r(10.0, "AGB", 25.0, hc_params)
    0.023745700245257646

    It can also be passed an array of handicaps:

    >>> hc_eq.sigma_t(np.asarray([10.0, 50.0, 100.0]), "AGB", 25.0, hc_params)
    array([0.0237457 , 0.09401539, 0.5250691 ])

    """
    sig_t = sigma_t(handicap, hc_sys, dist, hc_dat)
    sig_r = dist * sig_t

    return sig_r


def arrow_score(
    target: targets.Target,
    handicap: FloatArray,
    hc_sys: str,
    hc_dat: HcParams,
    arw_d: Optional[float] = None,
) -> FloatArray:
    # Six too many branches. Makes sense due to different target faces => disable
    # pylint: disable=too-many-branches
    """
    Calculate the average arrow score for a given target and handicap rating.

    Parameters
    ----------
    target : targets.Target
        A Target class specifying the target to be used
    handicap : float or ndarray
        handicap value to calculate score for
    hc_sys : string
        identifier for the handicap system
    hc_dat : HcParams
        dataclass containing parameters for handicap equations
    arw_d : float or None, default=None
        arrow diameter in [metres]

    Returns
    -------
    s_bar : float or ndarray
        average score of the arrow for this set of parameters

    Raises
    ------
    ValueError
        If the target uses a scoring system for which no handicap calculations exist.

    References
    ----------
    - The construction of the graduated handicap tables for target archery
      Lane, D (2013)

    Examples
    --------
    Expected arrow score on a WA720 70m target, using the AGB handicap system at a
    handicap of 10 can be calculated with:

    >>> import archeryutils as au
    >>> my720target = au.Target("10_zone", 122, 70.0)
    >>> hc_params = au.handicap_equations.HcParams()
    >>> au.handicap_equations.arrow_score(my720target, 10.0, "AGB", hc_params)
    9.401182682963338

    It can also be passed an array of handicaps:

    >>> au.handicap_equations.sigma_t(my720target,
    ...                               np.asarray([10.0, 50.0, 100.0]),
    ...                               "AGB",
    ...                               hc_params)
    array([9.40118268, 6.05227962, 0.46412515])

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


def score_for_passes(
    rnd: rounds.Round,
    handicap: FloatArray,
    hc_sys: str,
    hc_dat: HcParams,
    arw_d: Optional[float] = None,
) -> npt.NDArray[np.float_]:
    """
    Calculate the expected score for all passes in a round at a given handicap rating.

    Parameters
    ----------
    rnd : rounds.Round
        A Round class specifying the round being shot
    handicap : float or ndarray
        handicap value to calculate score for
    hc_sys : string
        identifier for the handicap system
    hc_dat : HcParams
        dataclass containing parameters for handicap equations
    arw_d : float or None, default=None
        arrow diameter in [metres] default = None -> (use defaults)

    Returns
    -------
    pass_scores : ndarray
        average score for each pass in the round (unrounded decimal)

    Examples
    --------
    Expected score for each pass on a WA1440 90m, using the AGB handicap system at a
    handicap of 10 can be calculated with the code below which returns an array with
    one score for each pass that makes up the round:

    >>> import archeryutils as au
    >>> wa_outdoor = au.load_rounds.WA_outdoor
    >>> hc_params = au.handicap_equations.HcParams()
    >>> au.handicap_equations.score_for_passes(wa_outdoor.wa1440_90, 10.0, "AGB", hc_params)
    array([322.84091528, 338.44257659, 338.66395001, 355.87959411])

    It can also be passed an array of handicaps:

    >>> au.handicap_equations.score_for_passes(wa_outdoor.wa1440_90,
    ...                                        np.asarray([10.0, 50.0, 100.0]),
    ...                                        "AGB",
    ...                                        hc_params)
    array([[322.84091528, 162.76200686,   8.90456718],
           [338.44257659, 217.88206641,  16.70850537],
           [338.66395001, 216.74407488,  16.41855209],
           [355.87959411, 288.77185611,  48.47897177]])

    """
    pass_scores = np.array(
        [
            pass_i.n_arrows
            * arrow_score(pass_i.target, handicap, hc_sys, hc_dat, arw_d=arw_d)
            for pass_i in rnd.passes
        ]
    )

    return pass_scores


def score_for_round(
    rnd: rounds.Round,
    handicap: FloatArray,
    hc_sys: str,
    hc_dat: HcParams,
    arw_d: Optional[float] = None,
    round_score_up: bool = True,
) -> FloatArray:
    """
    Calculate the expected score for a round at a given handicap rating.

    Parameters
    ----------
    rnd : rounds.Round
        A Round class specifying the round being shot
    handicap : float or ndarray
        handicap value to calculate score for
    hc_sys : string
        identifier for the handicap system
    hc_dat : HcParams
        dataclass containing parameters for handicap equations
    arw_d : float or None, default=None
        arrow diameter in [metres] default = None -> (use defaults)
    round_score_up : bool, default=True
        round score up to nearest integer value?

    Returns
    -------
    round_score : float or ndarray
        average score of the round for this set of parameters

    Examples
    --------
    Expected score for a WA1440 90m, using the AGB handicap system at a
    handicap of 10 can be calculated with:

    >>> import archeryutils as au
    >>> wa_outdoor = au.load_rounds.WA_outdoor
    >>> hc_params = au.handicap_equations.HcParams()
    >>> au.handicap_equations.score_for_round(wa_outdoor.wa1440_90, 10.0, "AGB", hc_params)
    1356.0
    >>> au.handicap_equations.score_for_round(wa_outdoor.wa1440_90,
    ...                                       10.0,
    ...                                       "AGB",
    ...                                       hc_params,
    ...                                       round_score_up=False)
    1355.8270359849505

    It can also be passed an array of handicaps:

    >>> au.handicap_equations.score_for_passes(wa_outdoor.wa1440_90,
    ...                                        np.asarray([10.0, 50.0, 100.0]),
    ...                                        "AGB",
    ...                                        hc_params)
    array([1356.,  887.,   91.])

    """
    # Two too many arguments. Makes sense at the moment => disable
    # Could try and simplify hc_sys and hc_dat in future refactor
    # pylint: disable=too-many-arguments

    round_score = np.sum(score_for_passes(rnd, handicap, hc_sys, hc_dat, arw_d), axis=0)

    if round_score_up:
        # Old AGB system uses plain rounding rather than ceil of other schemes
        if hc_sys in ("AGBold", "AA", "AA2"):
            round_score = np.around(round_score)
        else:
            round_score = np.ceil(round_score)

    return round_score
