"""Module for representing a Target for archery applications."""

from collections.abc import Mapping
from functools import partial
from types import MappingProxyType
from typing import Literal, NamedTuple, Optional, Union, get_args

from archeryutils.constants import length

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


class Q(NamedTuple):
    """Dataclass for a quantity with units."""

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

    _face_spec: Optional[FaceSpec] = None

    supported_systems = get_args(ScoringSystem)
    supported_distance_units = length.yard | length.metre
    supported_diameter_units = length.cm | length.inch | length.metre

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
        dist, native_dist_unit = length.parse_optional_units(
            distance, self.supported_distance_units, "metre"
        )
        diam, native_diameter_unit = length.parse_optional_units(
            diameter, self.supported_diameter_units, "cm"
        )
        self._scoring_system = scoring_system
        self._distance = length.to_metres(dist, native_dist_unit)
        self._native_dist_unit = native_dist_unit
        self._diameter = length.to_metres(diam, native_diameter_unit)
        self._native_diameter_unit = native_diameter_unit
        self.indoor = indoor

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
        >>> # WA 18m compound triple spot
        >>> specs = {0.02: 10, 0.08: 9, 0.12: 8, 0.16: 7, 0.2: 6}
        >>> target = Target.from_spec(specs, 40, 18)
        """
        spec_data, spec_units = length.parse_optional_units(
            face_spec, cls.supported_diameter_units, "metre"
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

        if self.scoring_system == other.scoring_system == "Custom":
            return (
                self._face_spec == other._face_spec
                and self._parameters() == other._parameters()
            )
        return self._parameters() == other._parameters()

    def _parameters(self):
        """Shortcut to get all target parameters as a tuple for comparison."""
        return (
            self._scoring_system,
            self._diameter,
            self._native_diameter_unit,
            self._distance,
            self._native_dist_unit,
            self.indoor,
        )

    @property
    def scoring_system(self):
        """Get target scoring system."""
        return self._scoring_system

    @property
    def is_custom(self):
        """Check if this Target uses a custom scoring system."""
        return self._scoring_system == "Custom"

    @property
    def diameter(self):
        """Get target diameter in [metres]."""
        return self._diameter

    @property
    def distance(self):
        """Get target distance in [metres]."""
        return self._distance

    @property
    def native_distance(self) -> Q:
        """Get target distance in original native units."""
        return Q(
            length.from_metres(self._distance, self._native_dist_unit),
            self._native_dist_unit,
        )

    @property
    def native_diameter(self) -> Q:
        """Get target diameter in original native units."""
        return Q(
            length.from_metres(self._diameter, self._native_diameter_unit),
            self._native_diameter_unit,
        )

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
        return max(self.face_spec.values())

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
        return min(self.face_spec.values())

    @property
    def face_spec(self) -> FaceSpec:
        """Get the targets face specification, generating on demand if needed."""
        if self._face_spec is None:
            if self.scoring_system == "Custom":
                msg = (
                    "Trying to generate face spec for custom target "
                    "but no existing spec found: "
                    "try instantiating with `Target.from_face_spec` instead"
                )
                raise ValueError(msg)
            self._face_spec = self.gen_face_spec(self.scoring_system, self._diameter)
        return MappingProxyType(self._face_spec)

    @staticmethod
    def gen_face_spec(system: ScoringSystem, diameter: float) -> FaceSpec:
        """
        Derive specifications for common/supported targets.

        Parameters
        ----------
        system: ScoringSystem
            Name of scoring system
        diameter:
            Target diameter in metres

        Returns
        -------
        spec : dict
            Mapping of target ring sizes in [metres] to score
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
        # Can only occur if target scoring system is modified after initialisation
        # Or newly supported scoring system doesn't have an implementation
        # here for generating specs
        else:
            msg = f"Scoring system {system!r} is not supported"
            raise ValueError(msg)

        return spec
