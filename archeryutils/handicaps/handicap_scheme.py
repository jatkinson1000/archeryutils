"""Handicap scheme class for performing calculations using a generic handicap scheme.

Extended Summary
----------------
Calculates arrow and round scores for a variety of target faces of
given distance and diameter:

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

References
----------
- The construction of the graduated handicap tables for target
  archery
  Lane, D (2013)
  https://www.jackatkinson.net/files/Handicap_Tables_2013.pdf
- New AGB: Atkinson, J
- Modelling archers’ scores at different distances to quantify
  score loss due to equipment selection and technique errors
  Park, J (2014)
  https://doi.org/10.1177%2F1754337114539308

"""

import itertools as itr
import warnings
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Union, overload

import numpy as np
import numpy.typing as npt

from archeryutils import rounds, targets

FloatArray = TypeVar("FloatArray", float, npt.NDArray[np.float64])


class HandicapScheme(ABC):
    r"""
    Abstract Base Class to represent a generic handicap scheme.

    Attributes
    ----------
    name : str
        The name of the handicap scheme.
    arw_d_out : float
        diameter of an outdoor arrow [metres] for this scheme, default 5.5e-3
    arw_d_in: float
        diameter of an indoor arrow [metres] for this scheme, default 9.3e-3
    desc_scale: bool
        does the scheme use a descending scale (lower handicap is better), default True
    scale_bounds: list[int]
        Reasonable upper and lower bounds on the handicap scale for bounding searches
    max_score_rounding_lim: float
        Limit to round the max score to when searching
        depends on scheme rounding method e.g. round() vs. ceil() etc.

    See Also
    --------
    handicap_scheme_agb.HandicapAGB :
        The AGB HandicapScheme subclass and associated \\**kwargs
    handicap_scheme_agb.HandicapAGBold :
        The AGBold HandicapScheme subclass and associated \\**kwargs
    handicap_scheme_aa.HandicapAA :
        The AA HandicapScheme subclass and associated \\**kwargs
    handicap_scheme_aa.HandicapAA2 :
        The AA2 HandicapScheme subclass and associated \\**kwargs

    """

    def __init__(self) -> None:
        self.name: str = "unnamed"

        # Arrow diameters outdoor and indoor
        self.arw_d_out: float
        self.arw_d_in: float

        # Handicap Scale parameters
        self.desc_scale: bool
        self.scale_bounds: list[float]
        self.max_score_rounding_lim: float

    def __repr__(self) -> str:
        """Return a representation of a HandicapScheme instance."""
        return f"<HandicapScheme: '{self.name}'>"

    @overload
    @abstractmethod
    def sigma_t(self, handicap: float, dist: float) -> float: ...

    @overload
    @abstractmethod
    def sigma_t(
        self,
        handicap: npt.NDArray[np.float64],
        dist: float,
    ) -> npt.NDArray[np.float64]: ...

    @abstractmethod
    def sigma_t(self, handicap: FloatArray, dist: float) -> FloatArray:
        """Calculate angular deviation for given handicap and distance.

        Parameters
        ----------
        handicap : FloatArray
            handicap to calculate sigma_t at
        dist : float
            distance to target [metres]

        Returns
        -------
        sig_t : FloatArray
            angular deviation [rad]

        """

    def sigma_r(self, handicap: FloatArray, dist: float) -> FloatArray:
        """Calculate radial deviation for a given handicap and distance.

        Standard deviation as a proxy for 'group size' based on
        handicap parameters, scheme, and distance.
        Wraps around sigma_t() and multiplies by distance.

        Parameters
        ----------
        handicap : FloatArray
            handicap to calculate sigma_r at
        dist : float or ndarray
            distance to target [metres]

        Returns
        -------
        sig_r : FloatArray
            standard deviation of group size [metres]

        Examples
        --------
        Deviation (in metres) at a distance of 25m and a handicap of 10,
        using the AGB handicap system (via the HandicapSchemeAGB subclass)
        can be calculated with:

        >>> import archeryutils.handicaps as hc
        >>> agb_scheme = hc.handicap_scheme("AGB")
        >>> agb_scheme.sigma_r(10.0, 25.0)
        0.023745700245257646

        It can also be passed an array of handicaps:

        >>> agb_scheme.sigma_t(np.asarray([10.0, 50.0, 100.0]), "AGB", 25.0)
        array([0.0237457 , 0.09401539, 0.5250691 ])

        """
        sig_t = self.sigma_t(handicap, dist)
        sig_r = dist * sig_t
        return sig_r

    def arrow_score(
        self,
        handicap: FloatArray,
        target: targets.Target,
        arw_d: Optional[float] = None,
    ) -> FloatArray:
        """Calculate the average arrow score for a given target and handicap rating.

        Parameters
        ----------
        handicap : FloatArray
            handicap value to calculate score for
        target : targets.Target
            A Target class specifying the target to be used
        arw_d : float or None, default=None
            user-specified arrow diameter in [metres]

        Returns
        -------
        s_bar : FloatArray
            average score of the arrow for this set of parameters

        References
        ----------
        - The construction of the graduated handicap tables for target archery
          Lane, D (2013)

        Examples
        --------
        Expected arrow score on a WA720 70m target at a handicap of 10,
        using the AGB handicap system (via the HandicapSchemeAGB subclass)
        can be calculated with:

        >>> import archeryutils as au
        >>> import archeryutils.handicaps as hc
        >>> my720target = au.Target("10_zone", 122, 70.0)
        >>> agb_scheme = hc.handicap_scheme("AGB")
        >>> agb_scheme.arrow_score(10.0, my720target)
        9.401182682963338

        It can also be passed an array of handicaps:

        >>> agb_scheme.sigma_t(np.array([10.0, 50.0, 100.0]), my720target)
        array([9.40118268, 6.05227962, 0.46412515])

        """
        # Set arrow diameter. Use scheme default based on in/outdoors if none provided.
        if arw_d is None:
            if target.indoor:
                arw_d = self.arw_d_in
            else:
                arw_d = self.arw_d_out

        arw_rad = arw_d / 2.0
        spec = target.face_spec
        sig_r = self.sigma_r(handicap, target.distance)
        return self._s_bar(spec, arw_rad, sig_r)

    def _s_bar(
        self, target_specs: targets.FaceSpec, arw_rad: float, sig_r: FloatArray
    ) -> FloatArray:
        """Calculate expected score directly from target ring sizes.

        Parameters
        ----------
        target_specs : FaceSpec
            Mapping of target ring *diameters* in [metres], to points scored
        arw_rad : float
            arrow radius in [metres]
        sig_r : float
            standard deviation of group size [metres]

        Returns
        -------
        s_bar : float
            expected average score per arrow

        Notes
        -----
        Assumes that:
        - target rings are concentric
        - score decreases monotonically as ring sizes increase
        """
        target_specs = dict(sorted(target_specs.items()))
        ring_sizes = target_specs.keys()
        ring_scores = list(itr.chain(target_specs.values(), [0]))
        score_drops = (inner - outer for inner, outer in itr.pairwise(ring_scores))
        max_score = max(ring_scores)

        return max_score - sum(
            score_drop * np.exp(-(((arw_rad + (ring_diam / 2)) / sig_r) ** 2))
            for ring_diam, score_drop in zip(ring_sizes, score_drops, strict=True)
        )

    def score_for_passes(
        self,
        handicap: FloatArray,
        rnd: rounds.Round,
        arw_d: Optional[float] = None,
        rounded_score: bool = True,
    ) -> npt.NDArray[np.float64]:
        """Calculate the expected score for all passes in a round at a given handicap.

        Parameters
        ----------
        handicap : FloatArray
            handicap value to calculate score for
        rnd : rounds.Round
            A Round class specifying the round being shot
        arw_d : float or None, default=None
            user-specified arrow diameter in [metres]
        rounded_score : bool, default=True
            round score to integer value?
            Note: sum of rounded passes may not be the same as the rounded round score

        Returns
        -------
        pass_scores : NDArray
            average score for each pass in the round

        Examples
        --------
        Expected score for each pass on a WA1440 90m at a handicap of 10,
        using the AGB handicap system (via the HandicapSchemeAGB subclass)
        can be calculated with the following code which returns an array with
        one score for each pass that makes up the round:

        >>> import archeryutils as au
        >>> import archeryutils.handicaps as hc
        >>> wa_outdoor = au.load_rounds.WA_outdoor
        >>> agb_scheme = hc.handicap_scheme("AGB")
        >>> agb_scheme.score_for_passes(10.0, wa_outdoor.wa1440_90)
        array([322.84091528, 338.44257659, 338.66395001, 355.87959411])

        It can also be passed an array of handicaps:

        >>> agb_scheme.score_for_passes(
        ...     np.array([10.0, 50.0, 100.0]), wa_outdoor.wa1440_90
        ... )
        array([[322.84091528, 162.76200686,   8.90456718],
               [338.44257659, 217.88206641,  16.70850537],
               [338.66395001, 216.74407488,  16.41855209],
               [355.87959411, 288.77185611,  48.47897177]])

        """
        pass_scores = np.array(
            [
                pass_i.n_arrows * self.arrow_score(handicap, pass_i.target, arw_d=arw_d)
                for pass_i in rnd.passes
            ],
        )

        return self._rounded_score(pass_scores) if rounded_score else pass_scores

    def score_for_round(
        self,
        handicap: FloatArray,
        rnd: rounds.Round,
        arw_d: Optional[float] = None,
        rounded_score: bool = True,
    ) -> FloatArray:
        """Calculate the expected score for a round at a given handicap.

        Parameters
        ----------
        handicap : FloatArray
            handicap value to calculate score for
        rnd : rounds.Round
            A Round class specifying the round being shot
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
        Expected score for a WA1440 90m at a handicap of 10,
        using the AGB handicap system (via the HandicapSchemeAGB subclass)
        can be calculated using:

        >>> import archeryutils as au
        >>> import archeryutils.handicaps as hc
        >>> wa_outdoor = au.load_rounds.WA_outdoor
        >>> agb_scheme = hc.handicap_scheme("AGB")
        >>> agb_scheme.score_for_round(10.0, wa_outdoor.wa1440_90)
        1356.0

        To get a decimal value of the exact handicap corresponding to the requested
        score use ``rounded_score=False``:

        >>> agb_scheme.score_for_round(
        ...     wa_outdoor.wa1440_90,
        ...     10.0,
        ...     rounded_score=False,
        ... )
        1355.8270359849505

        It can also be passed an array of handicaps:

        >>> agb_scheme.score_for_round(
        ...     np.array([10.0, 50.0, 100.0]), wa_outdoor.wa1440_90
        ... )
        array([1356.,  887.,   91.])

        """
        round_score = np.sum(
            self.score_for_passes(handicap, rnd, arw_d=arw_d, rounded_score=False),
            axis=0,
        )
        return self._rounded_score(round_score) if rounded_score else round_score

    @staticmethod
    def _rounded_score(score: FloatArray) -> FloatArray:
        """
        Round a decimal score to an integer value.

        Most schemes use plain rounding as implemented here.
        Schemes that use floor or ceil will override in their subclass.

        Parameters
        ----------
        score : FloatArray
            raw scores to be rounded according to the handicap system convention

        Returns
        -------
        FloatArray
            scores after appropriate rounding
        """
        return np.around(score)

    def handicap_from_score(
        self,
        score: float,
        rnd: rounds.Round,
        arw_d: Optional[float] = None,
        int_prec: bool = False,
    ) -> Union[int, float]:
        """Calculate the handicap of a given score on a given round.

        Parameters
        ----------
        score : float
            score achieved on the round
        rnd : rounds.Round
            the rounds.Round object to calculate the handicap for
        arw_d : float or None, default=None
            user-specified arrow diameter in [metres]
        int_prec : bool, default=False
            display results as integers? default = False
            decimal results accurate to 2dp from rootfinder

        Returns
        -------
        handicap: int or float
            Handicap for score. Has type int if int_prec is True, else float.

        Raises
        ------
        ValueError
            If an invalid score for the given round is provided.

        Examples
        --------
        Handicap for a score of 999 on a WA 1440 (90m),
        using the AGB handicap system (via the HandicapSchemeAGB subclass),
        can be calculated using:

        >>> import archeryutils as au
        >>> import archeryutils.handicaps as hc
        >>> wa_outdoor = au.load_rounds.WA_outdoor
        >>> agb_scheme = hc.handicap_scheme("AGB")
        >>> agb_scheme.score_for_round(wa_outdoor.wa1440_90, 10.0)
        >>> agb_scheme.handicap_from_score(999, wa_outdoor.wa1440_90)
        43.999964586102706

        To get an integer value as would appear in the handicap tables use
        ``int_prec=True``:

        >>> agb_scheme.handicap_from_score(999, wa_outdoor.wa1440_90, int_prec=True)
        44.0

        """
        # Check we have a valid score
        max_score = rnd.max_score()
        if score > max_score:
            msg = (
                f"The score of {score} provided is greater than the maximum of "
                f"{max_score} for a {rnd.name}."
            )
            raise ValueError(msg)
        if score <= 0.0:
            msg = (
                f"The score of {score} provided is less than or equal to zero "
                "so cannot have a handicap."
            )
            raise ValueError(msg)

        if score == max_score:
            # Deal with max score before root finding
            return self._get_max_score_handicap(rnd, arw_d, int_prec)

        handicap = self._rootfind_score_handicap(score, rnd, arw_d=arw_d)

        # Force integer precision if required.
        if int_prec:
            if self.desc_scale:
                handicap = np.ceil(handicap)
            else:
                handicap = np.floor(handicap)

            sc_int = self.score_for_round(handicap, rnd, arw_d, rounded_score=True)

            # Check that you can't get the same score from a larger handicap when
            # working in integers
            min_h_flag = False
            if self.desc_scale:
                hstep = 1.0
            else:
                hstep = -1.0
            while not min_h_flag:
                handicap += hstep
                sc_int = self.score_for_round(handicap, rnd, arw_d, rounded_score=True)
                if sc_int < score:
                    handicap -= hstep  # undo the iteration that caused flag to raise
                    min_h_flag = True

        return handicap

    def _get_max_score_handicap(
        self,
        rnd: rounds.Round,
        arw_d: Optional[float] = None,
        int_prec: bool = False,
    ) -> Union[int, float]:
        """Get handicap for maximum score on a round.

        Start high and drop down until no longer rounding to max score.
        i.e. >= max_score - 1.0 for ceil(), and >= max_score - 0.5 for around().

        Parameters
        ----------
        rnd : rounds.Round
            round being used
        arw_d : float or None, default=None
            user-specified arrow diameter in [metres]
        int_prec : bool, default=False
            display results as integers?

        Returns
        -------
        handicap : int or float
            Handicap for maximum score. Has type int if int_prec is True, else float.

        Warns
        ------
        UserWarning
            If called with int_prec=False as precision limit of numerical scheme delta.

        """
        max_score = rnd.max_score()

        if self.desc_scale:
            handicap = min(self.scale_bounds)
            delta_hc = 1.0
        else:
            handicap = max(self.scale_bounds)
            delta_hc = -1.0

        target = max_score - self.max_score_rounding_lim

        def check_score(handicap):
            return self.score_for_round(handicap, rnd, arw_d, rounded_score=False)

        # Work down (coarse) to where we would round or ceil to max score
        while check_score(handicap) > target:
            handicap += delta_hc

        # Step back extra after overshoot and reduce step size
        handicap -= 1.01 * delta_hc
        delta_hc /= 100

        # Work down (fine) to where we would round or ceil to max score
        while check_score(handicap) > target:
            handicap += delta_hc

        handicap -= delta_hc  # Undo final iteration that overshoots

        if int_prec:
            if self.desc_scale:
                handicap = np.floor(handicap)
            else:
                handicap = np.ceil(handicap)
        else:
            warnings.warn(
                "Handicap requested for maximum score without integer precision.\n"
                "Value returned will be first handicap that achieves this score.\n"
                "This could cause issues if you are not working in integers.",
                UserWarning,
                stacklevel=3,
            )
        return handicap

    def _rootfind_score_handicap(  # noqa: PLR0912, PLR0914, PLR0915, RUF100 Too many: branches, locals, statements
        self,
        score: float,
        rnd: rounds.Round,
        arw_d: Optional[float] = None,
    ) -> float:
        """Get handicap for general score on a round through rootfinding algorithm.

        Parameters
        ----------
        score : float
            score to get handicap for
        rnd : rounds.Round
            round being used
        arw_d : float or None, default=None
            user-specified arrow diameter in [metres]

        Returns
        -------
        handicap : float
            appropriate accurate handicap for this score

        References
        ----------
        Brent's Method for Root Finding in Scipy:

        - https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html
        - https://github.com/scipy/scipy/blob/dde39b7/scipy/optimize/Zeros/brentq.c

        """
        x_init = self.scale_bounds

        f_init = [
            self._f_root(x_init[0], score, rnd, arw_d=arw_d),
            self._f_root(x_init[1], score, rnd, arw_d=arw_d),
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
                # xpre <- xcu, xcur <- xblk, xblk <- xpre
                xpre, xcur, xblk = xcur, xblk, xcur

                # fpre <- fcur, fcur <- fblk, fblk <- fpre
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
            elif sbis > 0:
                xcur += delta
            else:
                xcur -= delta

            fcur = self._f_root(xcur, score, rnd, arw_d)
            handicap = xcur

        return handicap

    def _f_root(
        self,
        hc_est: float,
        score_est: float,
        round_est: rounds.Round,
        arw_d: Optional[float] = None,
    ) -> float:
        """Return error between predicted score and desired score.

        Parameters
        ----------
        hc_est : float
            current estimate of handicap
        score_est : float
            target score
        round_est : rounds.Round
            round being used
        arw_d : float or None, default=None
            arrow diameter in [metres]

        Returns
        -------
        float
            difference between desired value and score estimate

        """
        val = self.score_for_round(hc_est, round_est, arw_d=arw_d, rounded_score=False)
        return val - score_est
