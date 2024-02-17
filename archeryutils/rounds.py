"""Module to define a Pass and Round classes for archery applications."""

from typing import Optional, Union
from collections.abc import Iterable

from archeryutils.targets import Target, ScoringSystem
from archeryutils.constants import Length


class Pass:
    """
    A class used to represent a Pass.

    This class represents a pass of arrows shot at a target.
    It is the sub-unit of a Round.
    e.g. a single distance in a round or half of a single-distance round.

    Parameters
    ----------
    n_arrows : int
        number of arrows in this pass.
    scoring_system : str
        target face/scoring system type.
    diameter : float or tuple of float, str
        face diameter in [centimetres].
    distance : float or tuple of float, str
        linear distance from archer to target in [metres].
    indoor : bool, default=False
        is round indoors for arrow diameter purposes?

    Attributes
    ----------
    n_arrows : int
        number of arrows in this pass.
    target : Target
        A Target object defined using input parameters.

    Examples
    --------
    A Pass can be defined simply as:

    >>> my720pass = au.Pass(36, "10_zone", 122, 70.0)

    Like with the Target class, the units for diameter and distance can be specified
    using tuples:

    >>> myWA18pass = au.Pass(30, "10_zone", (40, "cm"), (18.0, "m"), indoor=True)

    See Also
    --------
    archeryutils.Target : The `Target` class.
    """

    # One too many arguments, but logically this structure makes sense => disable
    # pylint: disable=too-many-arguments

    def __init__(
        self,
        n_arrows: int,
        scoring_system: ScoringSystem,
        diameter: Union[float, tuple[float, str]],
        distance: Union[float, tuple[float, str]],
        indoor: bool = False,
    ) -> None:
        self.n_arrows = abs(n_arrows)
        self.target = Target(scoring_system, diameter, distance, indoor)

    @property
    def scoring_system(self) -> ScoringSystem:
        """Get target scoring_system."""
        return self.target.scoring_system

    @property
    def diameter(self) -> float:
        """Get target diameter [metres]."""
        return self.target.diameter

    @property
    def native_diameter_unit(self) -> str:
        """Get native_diameter_unit attribute of target."""
        return self.target.native_diameter_unit

    @property
    def distance(self) -> float:
        """Get target distance in [metres]."""
        return self.target.distance

    @property
    def native_dist_unit(self) -> str:
        """Get native_dist_unit attribute of target."""
        return self.target.native_dist_unit

    @property
    def indoor(self) -> bool:
        """Get indoor attribute of target."""
        return self.target.indoor

    def max_score(self) -> float:
        """
        Return the maximum numerical score possible on this pass (not counting x's).

        Returns
        -------
        float
            maximum score possible on this pass
        """
        return self.n_arrows * self.target.max_score()


class Round:
    """
    Class representing a Round.

    Describes an archer round made up of a number of Passes.
    e.g. for different distances.

    Parameters
    ----------
    name : str
        Formal name of the round
    passes : iterable of Pass
        an iterable of Pass classes making up the round
    location : str or None, default=None
        string identifing where the round is shot
    body : str or None, default=None
        string identifing the governing body the round belongs to
    family : str or None, default=None
        string identifing the family the round belongs to (e.g. wa1440, western, etc.)

    Attributes
    ----------
    name : str
        Formal name of the round
    passes : list of Pass
        a list of Pass classes making up the round
    location : str or None
        string identifing where the round is shot
    body : str or None
        string identifing the governing body the round belongs to
    family : str or None
        string identifing the family the round belongs to (e.g. wa1440, western, etc.)

    Examples
    --------
    Before defining a Round we need to first define the passes that make it up:

    >>> my720pass = au.Pass(36, "10_zone", 122, 70.0)

    These can now be passed to the Round constructor as any iterable,
    they will be stored as a list:

    >>> my720round = au.Round("WA 720", [my720pass, my720pass])
    >>> my720round = au.Round("WA 720", (my720pass, my720pass))
    >>> my720round.passes == [my720pass, my720pass]

    Additional, optional parameters can be used to provide 'metadata' about the round.

    """

    # One too many arguments, but logically this structure makes sense => disable
    # pylint: disable=too-many-arguments

    def __init__(
        self,
        name: str,
        passes: Iterable[Pass],
        location: Optional[str] = None,
        body: Optional[str] = None,
        family: Optional[str] = None,
    ) -> None:
        self.name = name
        self.passes = list(passes)
        self.location = location
        self.body = body
        self.family = family

    def max_score(self) -> float:
        """
        Return the maximum numerical score possible on this round (not counting x's).

        Returns
        -------
        max_score : float
            maximum score possible on this round
        """
        return sum(pass_i.max_score() for pass_i in self.passes)

    def max_distance(self, unit: bool = False) -> Union[float, tuple[float, str]]:
        """
        Return the maximum distance shot on this round along with the unit (optional).

        Parameters
        ----------
        unit : bool
            Return unit as well as numerical value?

        Returns
        -------
        max_dist : float
            maximum distance shot in this round
        (max_dist, unit) : tuple (float, str)
            tuple of max_dist and string of unit
        """
        max_dist = 0.0
        for pass_i in self.passes:
            if pass_i.distance > max_dist:
                max_dist = pass_i.distance
                d_unit = pass_i.native_dist_unit

        max_dist = Length.from_metres(max_dist, d_unit)
        if unit:
            return (max_dist, d_unit)
        return max_dist

    def get_info(self) -> None:
        """
        Print information about the Round.

        Prints a summary of each Pass in the round giving number of arrows,
        distance, and target size.

        """
        print(f"A {self.name} consists of {len(self.passes)} passes:")
        for pass_i in self.passes:
            native_dist = Length.from_metres(
                pass_i.target.distance, pass_i.native_dist_unit
            )
            native_diam = Length.from_metres(
                pass_i.target.diameter, pass_i.native_diameter_unit
            )

            print(
                f"\t- {pass_i.n_arrows} arrows "
                f"at a {native_diam:.1f} {pass_i.native_diameter_unit} target "
                f"at {native_dist:.1f} {pass_i.native_dist_unit}s."
            )
