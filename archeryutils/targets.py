"""Module for representing a Target for archery applications."""

from collections.abc import Mapping
from functools import partial
from types import MappingProxyType
from typing import Literal, NamedTuple, Union, get_args

from archeryutils import length

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
FaceSpec = Mapping[float, int]

_rnd6 = partial(round, ndigits=6)


class Quantity(NamedTuple):
    """
    Dataclass for a quantity with units.

    Can be used in place of a plain tuple of (value, units)

    Attributes
    ----------
    value: float
        Scalar value of quantity
    units: str
        Units of quantity
    """

    value: float
    units: str


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

    _supported_systems = get_args(ScoringSystem)
    _supported_distance_units = length.yard | length.metre
    _supported_diameter_units = length.cm | length.inch | length.metre

    def __init__(
        self,
        scoring_system: ScoringSystem,
        diameter: Union[float, tuple[float, str]],
        distance: Union[float, tuple[float, str]],
        indoor: bool = False,
    ) -> None:
        if scoring_system not in self._supported_systems:
            msg = (
                f"""Invalid Target Face Type specified.\n"""
                f"""Please select from '{"', '".join(self._supported_systems)}'."""
            )
            raise ValueError(msg)

        diam, native_diam_unit = length.parse_optional_units(
            diameter, self._supported_diameter_units, "cm"
        )
        dist, native_dist_unit = length.parse_optional_units(
            distance, self._supported_distance_units, "metre"
        )
        self._scoring_system = scoring_system
        self._diameter = length.to_metres(diam, native_diam_unit)
        self._native_diameter = Quantity(diam, native_diam_unit)
        self._distance = length.to_metres(dist, native_dist_unit)
        self._native_distance = Quantity(dist, native_dist_unit)
        self.indoor = indoor

        if scoring_system != "Custom":
            self._face_spec = self.gen_face_spec(scoring_system, self._diameter)

    @classmethod
    def from_face_spec(
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
        face_spec : FaceSpec or 2-tuple of FaceSpec, str
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
        >>> # Kings of archery recurve scoring triple spot
        >>> specs = {0.08: 10, 0.12: 8, 0.16: 7, 0.2: 6}
        >>> target = Target.from_face_spec(specs, 40, 18)
        >>> assert target.scoring_system == "Custom"
        """
        spec_data, spec_units = length.parse_optional_units(
            face_spec, cls._supported_diameter_units, "metre"
        )
        spec = {
            _rnd6(length.to_metres(ring_diam, spec_units)): score
            for ring_diam, score in spec_data.items()
        }

        target = cls("Custom", diameter, distance, indoor)
        target._face_spec = spec  # noqa: SLF001 private member access
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
        if not isinstance(other, Target):
            return NotImplemented

        return self._parameters() == other._parameters()

    def _parameters(self):
        """Shortcut to get all target parameters as a tuple for comparison."""
        return (
            self._scoring_system,
            self._diameter,
            self._native_diameter,
            self._distance,
            self._native_distance,
            self.indoor,
            self.face_spec,
        )

    @property
    def scoring_system(self) -> ScoringSystem:
        """Get the target face/scoring system type."""
        return self._scoring_system

    @property
    def diameter(self) -> float:
        """Get target diameter in [metres]."""
        return self._diameter

    @property
    def distance(self) -> float:
        """Get target distance in [metres]."""
        return self._distance

    @property
    def native_distance(self) -> Quantity:
        """Get target distance in original native units."""
        return self._native_distance

    @property
    def native_diameter(self) -> Quantity:
        """Get target diameter in original native units."""
        return self._native_diameter

    @property
    def face_spec(self) -> FaceSpec:
        """
        Get the targets face specification.

        Raises
        ------
        ValueError
            If trying to access the face_spec for a `"Custom"` scoring target
            but that target was not instantiated correctly and no spec is found.
        """
        # Still have some error handling in here for the case where
        # users use the wrong initaliser:
        # eg target = Target("Custom", 10, 10)
        # As otherwise errors raised are somewhat cryptic
        try:
            return MappingProxyType(self._face_spec)
        except AttributeError as err:
            msg = (
                "Trying to generate face spec for custom target "
                "but no existing spec found: "
                "try instantiating with `Target.from_face_spec` instead"
            )
            raise ValueError(msg) from err

    def max_score(self) -> float:
        """
        Return the maximum numerical score possible on this target (i.e. not X).

        Returns
        -------
        float
            maximum score possible on this target face.

        Examples
        --------
        >>> mytarget = au.Target("10_zone", (122, "cm"), (70.0, "m"))
        >>> mytarget.max_score()
        10.0
        """
        return max(self.face_spec.values(), default=0)

    def min_score(self) -> float:
        """
        Return the minimum numerical score possible on this target (excluding miss/0).

        Returns
        -------
        float
            minimum score possible on this target face

        Examples
        --------
        >>> mytarget = au.Target("10_zone", (122, "cm"), (70.0, "m"))
        >>> mytarget.min_score()
        1.0
        """
        return min(self.face_spec.values(), default=0)

    @staticmethod
    def gen_face_spec(system: ScoringSystem, diameter: float) -> FaceSpec:
        """
        Derive specifications for common/supported targets.

        Parameters
        ----------
        system: ScoringSystem
            Name of scoring system
        diameter:
            Target diameter in [metres]

        Returns
        -------
        spec : dict
            Mapping of target ring sizes in [metres] to score

        Raises
        ------
        ValueError
            If no rule for producing a face_spec from the given system is found.

        Examples
        --------
        >>> Target.gen_face_spec("WA_field", 0.6)
        {0.06: 6, 0.12: 5, 0.24: 4, 0.36: 3, 0.48: 2, 0.6: 1}
        >>> Target.gen_face_spec("10_zone_5_ring_compound", 0.4)
        {0.02: 10, 0.08: 9, 0.12: 8, 0.16: 7, 0.2: 6}
        """
        removed_rings = {
            "10_zone_6_ring": 4,
            "10_zone_5_ring": 5,
            "10_zone_5_ring_compound": 5,
            "Worcester_2_ring": 3,
        }

        missing = removed_rings.get(system, 0)
        if system == "5_zone":
            spec = {_rnd6((n + 1) * diameter / 10): 10 - n for n in range(1, 11, 2)}

        elif system in ("10_zone", "10_zone_6_ring", "10_zone_5_ring"):
            spec = {_rnd6(n * diameter / 10): 11 - n for n in range(1, 11 - missing)}

        elif system in ("10_zone_compound", "10_zone_5_ring_compound"):
            spec = {_rnd6(diameter / 20): 10} | {
                _rnd6(n * diameter / 10): 11 - n for n in range(2, 11 - missing)
            }

        elif system == "WA_field":
            spec = {_rnd6(diameter / 10): 6} | {
                _rnd6(n * diameter / 5): 6 - n for n in range(1, 6)
            }

        elif system == "IFAA_field":
            spec = {_rnd6(n * diameter / 5): 5 - n // 2 for n in range(1, 6, 2)}

        elif system == "Beiter_hit_miss":
            spec = {diameter: 1}

        elif system in ("Worcester", "Worcester_2_ring", "IFAA_field_expert"):
            spec = {_rnd6(n * diameter / 5): 6 - n for n in range(1, 6 - missing)}

        # NB: Should be hard (but not impossible) to get here without catching earlier;
        # Most likely will only occur if a newly supported scoring system doesn't
        # have an implementation here for generating specs
        else:
            msg = f"Scoring system {system!r} is not supported"
            raise ValueError(msg)

        return spec
