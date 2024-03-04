"""Module for representing a Target for archery applications."""

from typing import Literal, Union, get_args

from archeryutils.constants import Length

# TypeAlias (annotate explicitly in py3.10+)
ScoringSystem = Literal[
    "5_zone",
    "10_zone",
    "10_zone_compound",
    "10_zone_6_ring",
    "10_zone_5_ring",
    "10_zone_5_ring_compound",
    "WA_field",
    "IFAA_field",
    "IFAA_field_expert",
    "Beiter_hit_miss",
    "Worcester",
    "Worcester_2_ring",
]


class Target:
    """
    Class to represent a target.

    Parameters
    ----------
    scoring_system : {\
        ``"5_zone"`` ``"10_zone"`` ``"10_zone_compound"`` ``"10_zone_6_ring"``\
        ``"10_zone_5_ring"`` ``"10_zone_5_ring_compound"`` ``"WA_field"``\
        ``"IFAA_field"`` ``"IFAA_field_expert"`` ``"Beiter_hit_miss"`` ``"Worcester"``\
        ``"Worcester_2_ring"``}
        target face/scoring system type. Must be one of the supported values.
    diameter : float or tuple of float, str
        Target face diameter default [centimetres].
    distance : float or tuple of float, str
        linear distance from archer to target default [metres].
    indoor : bool, default=False
        is round indoors for arrow diameter purposes?

    Attributes
    ----------
    scoring_system : ScoringSystem
        target face/scoring system type.
    diameter : float
        Target face diameter [metres].
    native_diameter_unit : str
        Native unit the target size is measured in before conversion to [metres].
    distance : float
        linear distance from archer to target [metres].
    native_dist_unit : str
        Native unit the target distance is measured in before conversion to [metres].
    indoor : bool, default=False
        is round indoors?

    Raises
    ------
    ValueError
        If inappropriate scoring system or units are requested.

    Examples
    --------
    A target can be defined simply:

    >>> my720target = au.Target("10_zone", 122, 70.0)

    Alternatively the units for diameter and distance can be specified using tuples:

    >>> my720target = au.Target("10_zone", (122, "cm"), (70.0, "m"))
    >>> myWorcestertarget = au.Target("Worcester", (16, "inches"), (20.0, "yards"))

    Indoor rounds can be flagged as such using the `indoor` parameter:

    >>> myWA18target = au.Target("10_zone", (40, "cm"), (18.0, "m"), indoor=True)

    Attempting to construct a target with an invalid scoring system will fail
    in type checking and at runtime.

    >>> myUnknownTarget = au.Target("Unknown", 100, 50)
    ValueError: Invalid Target Face Type specified.
    Please select from '5_zone', '10_zone', '10_zone_compound', '10_zone_6_ring', ...

    """

    def __init__(
        self,
        scoring_system: ScoringSystem,
        diameter: Union[float, tuple[float, str]],
        distance: Union[float, tuple[float, str]],
        indoor: bool = False,
    ) -> None:
        systems = get_args(ScoringSystem)

        if scoring_system not in systems:
            msg = (
                f"""Invalid Target Face Type specified.\n"""
                f"""Please select from '{"', '".join(systems)}'."""
            )

            raise ValueError(msg)

        if isinstance(distance, tuple):
            (distance, native_dist_unit) = distance
        else:
            native_dist_unit = "metre"
        if native_dist_unit not in Length.yard | Length.metre:
            msg = (
                f"Distance unit '{native_dist_unit}' not recognised. "
                "Select from 'yard' or 'metre'."
            )
            raise ValueError(msg)
        distance = Length.to_metres(distance, native_dist_unit)

        if isinstance(diameter, tuple):
            (diameter, native_diameter_unit) = diameter
        else:
            native_diameter_unit = "cm"
        if native_diameter_unit not in Length.cm | Length.inch | Length.metre:
            msg = (
                f"Diameter unit '{native_diameter_unit}' not recognised. "
                "Select from 'cm', 'inch' or 'metre'"
            )
            raise ValueError(msg)
        diameter = Length.to_metres(diameter, native_diameter_unit)

        self.scoring_system = scoring_system
        self.diameter = diameter
        self.native_diameter_unit = Length.definitive_unit(native_diameter_unit)
        self.distance = distance
        self.native_dist_unit = Length.definitive_unit(native_dist_unit)
        self.indoor = indoor

    def __repr__(self) -> str:
        """Return a representation of a Target instance."""
        diam, diamunit = self.native_diameter
        dist, distunit = self.native_distance
        return (
            "Target("
            f"'{self.scoring_system}', "
            f"({diam:.6g}, '{diamunit}'), "
            f"({dist:.6g}, '{distunit}'), "
            f"indoor={self.indoor}"
            ")"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality of Targets based on parameters."""
        if isinstance(other, Target):
            return self._parameters() == other._parameters()
        return NotImplemented

    def _parameters(self):
        """Shortcut to get all target parameters as a tuple for comparison."""
        return (
            self.scoring_system,
            self.diameter,
            self.native_diameter_unit,
            self.distance,
            self.native_dist_unit,
            self.indoor,
        )

    @property
    def native_distance(self) -> tuple[float, str]:
        """Get target distance in original native units."""
        return (
            Length.from_metres(self.distance, self.native_dist_unit),
            self.native_dist_unit,
        )

    @property
    def native_diameter(self) -> tuple[float, str]:
        """Get target diameter in original native units."""
        return (
            Length.from_metres(self.diameter, self.native_diameter_unit),
            self.native_diameter_unit,
        )

    def max_score(self) -> float:
        """
        Return the maximum numerical score possible on this target (i.e. not X).

        Returns
        -------
        float
            maximum score possible on this target face.

        Raises
        ------
        ValueError
            If a scoring system is not accounted for in the function.

        Examples
        --------
        >>> mytarget = au.Target("10_zone", (122, "cm"), (70.0, "m"))
        >>> mytarget.max_score()
        10.0
        """
        if self.scoring_system in ("5_zone"):
            return 9.0
        if self.scoring_system in (
            "10_zone",
            "10_zone_compound",
            "10_zone_6_ring",
            "10_zone_6_ring_compound",
            "10_zone_5_ring",
            "10_zone_5_ring_compound",
        ):
            return 10.0
        if self.scoring_system in ("WA_field"):
            return 6.0
        if self.scoring_system in (
            "IFAA_field",
            "IFAA_field_expert",
            "Worcester",
            "Worcester_2_ring",
        ):
            return 5.0
        if self.scoring_system in ("Beiter_hit_miss"):
            return 1.0
        # NB: Should be hard (but not impossible) to get here without catching earlier.
        msg = f"Target face '{self.scoring_system}' has no specified maximum score."
        raise ValueError(msg)

    def min_score(self) -> float:
        """
        Return the minimum numerical score possible on this target (excluding miss/0).

        Returns
        -------
        float
            minimum score possible on this target face

        Raises
        ------
        ValueError
            If a scoring system is not accounted for in the function.

        Examples
        --------
        >>> mytarget = au.Target("10_zone", (122, "cm"), (70.0, "m"))
        >>> mytarget.min_score()
        1.0
        """
        if self.scoring_system in (
            "5_zone",
            "10_zone",
            "10_zone_compound",
            "WA_field",
            "IFAA_field_expert",
            "Worcester",
        ):
            return 1.0
        if self.scoring_system in (
            "10_zone_6_ring",
            "10_zone_6_ring_compound",
        ):
            return 5.0
        if self.scoring_system in (
            "10_zone_5_ring",
            "10_zone_5_ring_compound",
        ):
            return 6.0
        if self.scoring_system in ("Worcester_2_ring",):
            return 4.0
        if self.scoring_system in ("IFAA_field",):
            return 3.0
        if self.scoring_system in ("Beiter_hit_miss"):
            # For Beiter options are hit and miss, so return 0 here
            return 0.0
        # NB: Should be hard (but not impossible) to get here without catching earlier.
        msg = f"Target face '{self.scoring_system}' has no specified minimum score."
        raise ValueError(msg)
