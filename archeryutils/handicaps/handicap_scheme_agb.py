"""Code for handicap calculations using Archery GB handicap schemes.

Extended Summary
----------------
Code to calculate information using a number of schemes:

- New Archery GB (J Atkinson, 2023)
- Old Archery GB (D Lane)

Routine Listings
----------------
- HandicapAGB Class
- HandicapAGBold Class

References
----------
- New AGB: Atkinson, J
- Old AGB: The construction of the graduated handicap tables for target
  archery
  Lane, D (2013)
  https://www.jackatkinson.net/files/Handicap_Tables_2013.pdf

"""

import numpy as np

from .handicap_scheme import FloatArray, HandicapScheme


class HandicapAGB(HandicapScheme):
    """
    Class to represent the Archery GB handicap scheme.

    This class represents the 2023 handicap scheme by Jack Atkinson.

    Parameters
    ----------
    datum : float
        offset to set scratch point, default = 6.0,
    step : float
        percentage change in deviation per handicap step, default = 3.5,
    ang_0 : float
        datum angle used in scheme, default = 5.0e-4,
    kd : float
        factor controlling excess dispersion scaling with distance, default = 0.00365,

    Attributes
    ----------
    name : str="AGB"
        The name of the handicap scheme.
    arw_d_out : float
        diameter of an outdoor arrow: 5.5e-3 [metres]
    arw_d_in: float
        diameter of an indoor arrow 9.3e-3 [metres]

    Warnings
    --------
    Using non-default values for the kwargs may produce results that
    do not match the official values for this scheme.
    Only change if you are experimenting and know what you are doing!

    See Also
    --------
    HandicapScheme : The base class for a handicap scheme from which this is subclassed
                     containing details of additional methods.

    """

    def __init__(
        self,
        datum: float = 6.0,
        step: float = 3.5,
        ang_0: float = 5.0e-4,
        kd: float = 0.00365,
    ):
        super().__init__()

        self.name = "AGB"

        self.arw_d_out: float = 5.5e-3
        self.arw_d_in: float = 9.3e-3

        # AGB Uses a descending scale with ceil. All numbers typically in [-75, 300]
        self.desc_scale: bool = True
        self.scale_bounds: list[float] = [-75, 300]
        self.max_score_rounding_lim: float = 1.0

        self.params = {
            "datum": datum,
            "step": step,
            "ang_0": ang_0,
            "kd": kd,
        }

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

        Examples
        --------
        Angular deviation at a distance of 25m, using the AGB handicap system at a
        handicap of 10 can be calculated with:

        >>> import archeryutils.handicaps as hc
        >>> agb_scheme = hc.handicap_scheme("AGB")
        >>> agb_scheme.sigma_t(10.0, 25.0)
        0.0009498280098103058

        It can also be passed an array of handicaps:

        >>> import numpy as np
        >>> agb_scheme.sigma_t(np.array([10.0, 50.0, 100.0]), 25.0)
        array([0.00094983, 0.00376062, 0.02100276])

        """
        return (
            self.params["ang_0"]
            * ((1.0 + self.params["step"] / 100.0) ** (handicap + self.params["datum"]))
            * np.exp(self.params["kd"] * dist)
        )

    # Override rounding method for AGB to always round up to next highest score.
    @staticmethod
    def _rounded_score(score):
        return np.ceil(score)


class HandicapAGBold(HandicapScheme):
    """
    Class to represent the old (pre-2023) Archery GB handicap scheme by D. Lane.

    Parameters
    ----------
    datum : float
        offset to set scratch point, default = 12.9,
    step : float
        percentage change in deviation per handicap step, default = 3.6,
    ang_0 : float
        datum angle used in scheme, default = 5.0e-4,
    k1 : float
        constant k1 in the handicap equation, default = 1.429e-6,
    k2 : float
        constant k2 in the handicap equation, default = 1.07,
    k3 : float
        constant k3 in the handicap equation, default = 4.3,
    p1 : float
        exponent of distance scaling, default = 2.0,

    Attributes
    ----------
    name : str="AGBold"
        The name of the handicap scheme.
    arw_d_out : float
        diameter of an outdoor arrow: 7.14e-3 [metres]
    arw_d_in: float
        diameter of an indoor arrow 7.14e-3 [metres]

    Warnings
    --------
    Using non-default values for the kwargs may produce results that
    do not match the official values for this scheme.
    Only change if you are experimenting and know what you are doing!

    See Also
    --------
    HandicapScheme : The base class for a handicap scheme from which this is subclassed
                     containing details of additional methods.

    """

    def __init__(
        self,
        datum: float = 12.9,
        step: float = 3.6,
        ang_0: float = 5.0e-4,
        k1: float = 1.429e-6,
        k2: float = 1.07,
        k3: float = 4.3,
        p1: float = 2.0,
    ):
        # three too many arguments, but all are hc-scheme params => disable
        # pylint: disable=too-many-arguments

        super().__init__()

        self.name = "AGBold"

        self.arw_d_out = 7.14e-3
        self.arw_d_in = 7.14e-3

        # AGBold Uses a descending scale with round. All numbers typically in [-75, 300]
        self.desc_scale = True
        self.scale_bounds = [-75, 300]
        self.max_score_rounding_lim = 0.5

        self.params = {
            "datum": datum,  # Offset required to set handicap 0 at desired score.
            "step": step,  # Percentage change in group size for each handicap step.
            "ang_0": ang_0,  # Baseline angle used for group size 0.5 [millirad].
            "k1": k1,  # Constant 1 used in handicap equation.
            "k2": k2,  # Constant 2 used in handicap equation.
            "k3": k3,  # Constant 3 used in handicap equation.
            "p1": p1,  # Exponent of distance scaling.
        }

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

        Notes
        -----
        This is the key part of this scheme.
        The values are taken from Lane (2013) [1]_.

        References
        ----------
        .. [1] Lane, D. (2013). "The Construction of the Graduated Handicap Tables
           for Target Archery."

        Examples
        --------
        Angular deviation at a distance of 25m, using the AGBold handicap system at a
        handicap of 10 can be calculated with:

        >>> import archeryutils.handicaps as hc
        >>> agbold_scheme = hc.handicap_scheme("AGBold")
        >>> agbold_scheme.sigma_t(10.0, 25.0)
        0.001126491382794861

        It can also be passed an array of handicaps:

        >>> import numpy as np
        >>> agbold_scheme.sigma_t(np.array([10.0, 50.0, 100.0]), 25.0)
        array([0.00112649, 0.00478762, 0.05520862])

        """
        k_factor = self.params["k1"] * self.params["k2"] ** (
            handicap + self.params["k3"]
        )
        f_factor = 1.0 + k_factor * dist ** self.params["p1"]
        return (
            self.params["ang_0"]
            * ((1.0 + self.params["step"] / 100.0) ** (handicap + self.params["datum"]))
            * f_factor
        )
