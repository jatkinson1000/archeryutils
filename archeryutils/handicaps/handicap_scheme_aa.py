"""Code for handicap calculations using Archery Australia handicap schemes.

Extended Summary
----------------
Code to calculate information using a number of schemes:

- Original Archery Australia (J Park)
- Updated Archery Australia (J Park)

Routine Listings
----------------
- HandicapAA Class
- HandicapAA2 Class

References
----------
- Modelling archers’ scores at different distances to quantify
  score loss due to equipment selection and technique errors
  Park, J (2014)
  https://doi.org/10.1177%2F1754337114539308

"""

import numpy as np
import numpy.typing as npt

from .handicap_scheme import FloatArray, HandicapScheme


class HandicapAA(HandicapScheme):
    """
    Class to represent the original Archery Australia scheme by J. Park.

    Parameters
    ----------
    ang_0 : float
        datum angle used in scheme, default = 1.0e-3,
    k0 : float
        handicap offset to set scratch point, default= 2.37,
    ks : float
        change with each handicap step as a geometric progression, default= 0.027,
    kd : float
        distance scaling factor, default= 0.004,

    Attributes
    ----------
    name : str="AA"
        The name of the handicap scheme.
    arw_d_out : float
        diameter of an outdoor arrow: 5.0e-3 [metres]
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
        ang_0: float = 1.0e-3,
        k0: float = 2.37,
        ks: float = 0.027,
        kd: float = 0.004,
    ):
        super().__init__()

        self.name = "AA"

        self.arw_d_out = 5.0e-3
        self.arw_d_in: float = 9.3e-3

        # AA Uses an ascending scale with round. All numbers typically in [-250, 175]
        self.desc_scale = False
        self.scale_bounds = [-250, 175]
        self.max_score_rounding_lim = 0.5

        self.params = {
            "ang_0": ang_0,  # Baseline angle used for group size 1.0 [millirad].
            "k0": k0,  # Offset required to set handicap 100 at desired score.
            "ks": ks,  # Change with each step of geometric progression.
            "kd": kd,  # Distance scaling factor [1/metres].
        }

    def sigma_t(self, handicap: npt.ArrayLike, dist: float) -> FloatArray:
        """Calculate angular deviation for given handicap and distance.

        Parameters
        ----------
        handicap : ArrayLike
            handicap(s) to calculate sigma_t at
        dist : float
            distance to target [metres]

        Returns
        -------
        sig_t : FloatArray
            angular deviation [rad]

        Notes
        -----
        This is the key part of this scheme.
        The values are taken from Park (2014) [2]_.

        References
        ----------
        .. [2] Park, J. L. (2014). "Modelling archers’ scores at different distances
           to quantify score loss due to equipment selection and technique errors."
           Proceedings of the Institution of Mechanical Engineers,
           Part P: Journal of Sports Engineering and Technology, 228(4), 250-258.
           DOI: 10.1177/175433711453930

        Examples
        --------
        Angular deviation at a distance of 25m, using the AGBold handicap system at a
        handicap of 10 can be calculated with:

        >>> import archeryutils.handicaps as hc
        >>> aa_scheme = hc.handicap_scheme("AA")
        >>> aa_scheme.sigma_t(10.0, 25.0)
        0.012763296491500004

        It can also be passed an array of handicaps:

        >>> import numpy as np
        >>> aa_scheme.sigma_t(np.array([10.0, 50.0, 100.0]), 25.0)
        array([0.0127633 , 0.00433436, 0.00112364])

        """
        handicap = np.asarray(handicap)  # Ensure numpy array for calculations

        # Factor of sqrt(2) to deal with factor of 2 in differing definitions of sigma
        # between AGB and AA
        # Required so code elsewhere is unchanged
        # Factor of 1.0e-3 due to AA algorithm specifying sigma t in milliradians, so
        # convert to rad
        return (
            np.sqrt(2.0)
            * self.params["ang_0"]
            * np.exp(
                self.params["k0"]
                - self.params["ks"] * handicap
                + self.params["kd"] * dist,
            )
        )


class HandicapAA2(HandicapScheme):
    """
    Class to represent the updated (2014) Archery Australia scheme by J. Park.

    Parameters
    ----------
    ang_0 : float
        datum angle used in scheme, default = 1.0e-3,
    k0 : float
        handicap offset to set scratch point, default= 2.57,
    ks : float
        change with each handicap step as a geometric progression, default= 0.027,
    f1 : float
        'linear' scaling factor, default= 0.815,
    f2 : float
        'quadratic' scaling factor, default= 0.185,
    d0 : float
        normalisation distance, default = 50.0,

    Attributes
    ----------
    name : str="AA2"
        The name of the handicap scheme.
    arw_d_out : float
        diameter of an outdoor arrow: 5.0e-3 [metres]
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

    def __init__(  # noqa: PLR0913 - Too many arguments
        self,
        ang_0: float = 1.0e-3,
        k0: float = 2.57,
        ks: float = 0.027,
        f1: float = 0.815,
        f2: float = 0.185,
        d0: float = 50.0,
    ):
        super().__init__()

        self.name = "AA2"

        self.arw_d_out = 5.0e-3
        self.arw_d_in = 9.3e-3

        # AA Uses an ascending scale with round. All numbers typically in [-250, 175]
        self.desc_scale = False
        self.scale_bounds = [-250, 175]
        self.max_score_rounding_lim = 0.5

        self.params = {
            "ang_0": ang_0,
            "k0": k0,  # Offset required to set handicap 100 at desired score.
            "ks": ks,  # Change with each step of geometric progression.
            "f1": f1,  # 'Linear' scaling factor.
            "f2": f2,  # 'Quadratic' scaling factor.
            "d0": d0,  # Normalisation distance [metres].
        }

    def sigma_t(self, handicap: npt.ArrayLike, dist: float) -> FloatArray:
        """Calculate angular deviation for given handicap and distance.

        Parameters
        ----------
        handicap : ArrayLike
            handicap(s) to calculate sigma_t at
        dist : float
            distance to target [metres]

        Returns
        -------
        sig_t : FloatArray
            angular deviation [rad]

        Notes
        -----
        This is the key part of this scheme.
        The values are taken from Park (2014) [3]_.

        References
        ----------
        .. [3] Park, J. L. (2014). "Modelling archers’ scores at different distances
           to quantify score loss due to equipment selection and technique errors."
           Proceedings of the Institution of Mechanical Engineers,
           Part P: Journal of Sports Engineering and Technology, 228(4), 250-258.
           DOI: 10.1177/175433711453930

        Examples
        --------
        Angular deviation at a distance of 25m, using the AGBold handicap system at a
        handicap of 10 can be calculated with:

        >>> import archeryutils.handicaps as hc
        >>> aa2_scheme = hc.handicap_scheme("AA2")
        >>> aa2_scheme.sigma_t(10.0, 25.0)
        0.012800853871823342

        It can also be passed an array of handicaps:

        >>> import numpy as np
        >>> aa2_scheme.sigma_t(np.array([10.0, 50.0, 100.0]), 25.0)
        array([0.01280085, 0.00434711, 0.00112695])

        """
        handicap = np.asarray(handicap)  # Ensure numpy array for calculations

        # Factor of sqrt(2) to deal with factor of 2 in differing definitions of sigma
        # between AGB and AA
        # Required so code elsewhere is unchanged
        # Factor of 1.0e-3 due to AA algorithm specifying sigma t in milliradians, so
        # convert to rad
        return (
            np.sqrt(2.0)
            * self.params["ang_0"]
            * np.exp(self.params["k0"] - self.params["ks"] * handicap)
            * (self.params["f1"] + self.params["f2"] * dist / self.params["d0"])
        )
