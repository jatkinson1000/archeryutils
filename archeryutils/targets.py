"""Module for representing a Target for archery applications."""

from functools import partial
from types import MappingProxyType
from typing import Final, Literal, NamedTuple, Union, get_args

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
    "Custom",
]

# TypeAlias (annotate explicitly in py3.10+)
FaceSpec = dict[float, int]

_rnd6 = partial(round, ndigits=6)


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

    _face_spec: FaceSpec

    # Lookup data for min and max scores for supported scoring systems.
    # Used to deduplicate logic from max_score, min_score and get_face_spec methods
    _scoring_system_data: Final = MappingProxyType(
        {
            "5_zone": {"high": 9, "low": 1},
            "10_zone": {"high": 10, "low": 1},
            "10_zone_compound": {"high": 10, "low": 1},
            "10_zone_6_ring": {"high": 10, "low": 5},
            "10_zone_5_ring": {"high": 10, "low": 6},
            "10_zone_5_ring_compound": {"high": 10, "low": 6},
            "WA_field": {"high": 6, "low": 1},
            "IFAA_field": {"high": 5, "low": 3},
            "IFAA_field_expert": {"high": 5, "low": 1},
            "Beiter_hit_miss": {"high": 1, "low": 1},
            "Worcester": {"high": 5, "low": 1},
            "Worcester_2_ring": {"high": 5, "low": 4},
        }
    )

    supported_systems = get_args(ScoringSystem)
    supported_distance_units = Length.yard | Length.metre
    supported_diameter_units = Length.cm | Length.inch | Length.metre

    def __init__(
        self,
        scoring_system: ScoringSystem,
        diameter: Union[float, tuple[float, str]],
        distance: Union[float, tuple[float, str]],
        indoor: bool = False,
    ) -> None:
        if scoring_system not in self.supported_systems:
            msg = (
                f"""Invalid Target Face Type specified.\n"""
                f"""Please select from '{"', '".join(self.supported_systems)}'."""
            )
            raise ValueError(msg)

        if isinstance(distance, tuple):
            (distance, native_dist_unit) = distance
        else:
            native_dist_unit = "metre"

        if native_dist_unit not in self.supported_distance_units:
            msg = (
                f"Distance unit '{native_dist_unit}' not recognised. "
                f"Select from {Length.definitive_units(self.supported_distance_units)}."
            )
            raise ValueError(msg)
        distance = Length.to_metres(distance, native_dist_unit)

        if isinstance(diameter, tuple):
            (diameter, native_diameter_unit) = diameter
        else:
            native_diameter_unit = "cm"
        if native_diameter_unit not in self.supported_diameter_units:
            msg = (
                f"Diameter unit '{native_diameter_unit}' not recognised. "
                f"Select from {Length.definitive_units(self.supported_diameter_units)}"
            )
            raise ValueError(msg)
        diameter = Length.to_metres(diameter, native_diameter_unit)

        self.scoring_system = scoring_system
        self.diameter = diameter
        self.native_diameter_unit = Length.definitive_unit(native_diameter_unit)
        self.distance = distance
        self.native_dist_unit = Length.definitive_unit(native_dist_unit)
        self.indoor = indoor

    @classmethod
    def from_spec(
        cls,
        face_spec: Union[FaceSpec, tuple[FaceSpec, str]],
        diameter: Union[float, tuple[float, str]],
        distance: Union[float, tuple[float, str]],
        indoor: bool = False,
    ) -> "Target":
        """
        Constuctor to build a target with custom scoring system.

        Optionally can convert units at the time of construction.
        Diameter must still be provided as a seperate arguement as it is impossible
        to know what the nominal diameter would be from the face specification
        without a known scoring system. However it is superceeded by face_spec
        and has no effect when calculating handicaps.

        Parameters
        ----------
        face_spec : dict of floats to ints or 2-tuple of dict, str
            Target face specification, a mapping of target ring sizes to score.
            Default units are assumed as [metres] but can be provided as the second
            element of a tuple.
        diameter : float or tuple of float, str
            Target face diameter (and units, default [cm])
        distance : float or tuple of float, str
            linear distance from archer to target (and units, default [metres])
        indoor : bool
            Is target indoors for arrow diameter purposes? default = False

        Returns
        -------
        Target
            Instance of Target class with scoring system set as "Custom" and
            face specification stored.

        Examples
        --------
        >>> # WA 18m compound triple spot
        >>> specs = {0.02: 10, 0.08: 9, 0.12: 8, 0.16: 7, 0.2: 6}
        >>> target = Target.from_spec(specs, 40, 18)
        """
        if isinstance(face_spec, tuple):
            spec_data, spec_units = face_spec

            if spec_units not in cls.supported_diameter_units:
                msg = (
                    f"Face specification unit '{spec_units}' not recognised. "
                    "Select from 'cm', 'inch' or 'metre'"
                )
                raise ValueError(msg)
            face_spec = {
                _rnd6(Length.to_metres(ring_diam, spec_units)): score
                for ring_diam, score in spec_data.items()
            }

        target = cls("Custom", diameter, distance, indoor)
        target._face_spec = face_spec  # noqa: SLF001 private member access
        return target

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
            if self.scoring_system == other.scoring_system == "Custom":
                return (
                    self._face_spec == other._face_spec
                    and self._parameters() == other._parameters()
                )
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
    def is_custom(self):
        """Check if this Target uses a custom scoring system."""
        return self.scoring_system == "Custom"

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
        if self.is_custom:
            return max(self._face_spec.values())
        data = self._scoring_system_data.get(self.scoring_system)
        if data:
            return data["high"]
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
        if self.is_custom:
            return min(self._face_spec.values())
        data = self._scoring_system_data.get(self.scoring_system)
        if data:
            return data["low"]
        # NB: Should be hard (but not impossible) to get here without catching earlier.
        msg = f"Target face '{self.scoring_system}' has no specified minimum score."
        raise ValueError(msg)

    def get_face_spec(self) -> FaceSpec:
        # Could replace with mapping face to lambda that returns spec
        """Derive specifications for common/supported targets.

        Returns
        -------
        spec : dict
            Mapping of target ring sizes in [metres] to score
        """
        system = self.scoring_system
        tar_dia = self.diameter

        if system == "Custom":
            return self._face_spec

        data = self._scoring_system_data.get(system)
        if not data:
            # no data for scoring system, raise
            msg = f"No rule for calculating scoring for face type {system}."
            raise ValueError(msg)

        # calculate missing rings for certain targets from minimum score
        missing = data["low"] - 1

        if system == "5_zone":
            spec = {_rnd6((n + 1) * tar_dia / 10): 10 - n for n in range(1, 11, 2)}

        elif system in ("10_zone", "10_zone_6_ring", "10_zone_5_ring"):
            spec = {_rnd6(n * tar_dia / 10): 11 - n for n in range(1, 11 - missing)}

        elif system in ("10_zone_compound", "10_zone_5_ring_compound"):
            spec = {_rnd6(tar_dia / 20): 10} | {
                _rnd6(n * tar_dia / 10): 11 - n for n in range(2, 11 - missing)
            }

        elif system == "WA_field":
            spec = {_rnd6(tar_dia / 10): 6} | {
                _rnd6(n * tar_dia / 5): 6 - n for n in range(1, 6)
            }

        elif system == "IFAA_field":
            spec = {_rnd6(n * tar_dia / 5): 5 - n // 2 for n in range(1, 6, 2)}

        elif system == "Beiter_hit_miss":
            spec = {tar_dia: 1}

        elif system in ("Worcester", "Worcester_2_ring", "IFAA_field_expert"):
            spec = {_rnd6(n * tar_dia / 5): 6 - n for n in range(1, 6 - missing)}

        return spec
