"""Class to represent a Target for archery applications."""
from typing import Union, Tuple

from archeryutils.constants import Length


class Target:
    """
    Class to represent a target.

    Attributes
    ----------
    scoring_system : str
        target face/scoring system type
    diameter : float
        Target face diameter in [metres]
    native_diameter_unit : str
        Native unit the target size is measured in.
        Converts diameter and stores in [meteres]
    distance : float
        linear distance from archer to target
    native_dist_unit : str
        The native unit distance is measured in
    indoor : bool
        is round indoors for arrow diameter purposes? default = False

    Methods
    -------
    max_score()
        Returns the maximum score ring value
    min_score()
        Returns the minimum score ring value (excluding miss)
    """

    def __init__(
        self,
        scoring_system: str,
        diameter: Union[float, Tuple[float, str]],
        distance: Union[float, Tuple[float, str]],
        indoor: bool = False,
    ) -> None:
        systems = [
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

        if scoring_system not in systems:
            raise ValueError(
                f"""Invalid Target Face Type specified.\n"""
                f"""Please select from '{"', '".join(systems)}'."""
            )

        if isinstance(distance, tuple):
            (distance, native_dist_unit) = distance
        else:
            native_dist_unit = "metre"
        if native_dist_unit not in Length.yard | Length.metre:
            raise ValueError(
                f"Distance unit '{native_dist_unit}' not recognised. "
                "Select from 'yard' or 'metre'."
            )
        distance = Length.to_metres(distance, native_dist_unit)

        if isinstance(diameter, tuple):
            (diameter, native_diameter_unit) = diameter
        else:
            native_diameter_unit = "cm"
        if native_diameter_unit not in Length.cm | Length.inch | Length.metre:
            raise ValueError(
                f"Diameter unit '{native_diameter_unit}' not recognised. "
                "Select from 'cm', 'inch' or 'metre'"
            )
        diameter = Length.to_metres(diameter, native_diameter_unit)

        self.native_dist_unit = Length.definitive_unit(native_dist_unit)
        self.distance = distance
        self.native_diameter_unit = Length.definitive_unit(native_diameter_unit)
        self.diameter = diameter
        self.scoring_system = scoring_system
        self.indoor = indoor

    def max_score(self) -> float:
        """
        Return the maximum numerical score possible on this target (i.e. not X).

        Returns
        -------
        max_score : float
            maximum score possible on this target face
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
        raise ValueError(
            f"Target face '{self.scoring_system}' has no specified maximum score."
        )

    def min_score(self) -> float:
        """
        Return the minimum numerical score possible on this target (excluding miss/0).

        Returns
        -------
        min_score : float
            minimum score possible on this target face
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
        raise ValueError(
            f"Target face '{self.scoring_system}' has no specified minimum score."
        )
