"""Classes to define a Pass and Round for archery applications."""
from typing import List, Union, Tuple

from archeryutils.targets import Target
from archeryutils.constants import Length


class Pass:
    """
    A class used to represent a Pass.

    This class represents a pass of arrows, i.e. a subunit of a Round.
    e.g. a single distance or half

    Attributes
    ----------
    n_arrows : int
        number of arrows in this pass
    diameter : float
        face diameter in [centimetres]
    scoring_system : str
        target face/scoring system type
    distance : float
        linear distance from archer to target in [metres]
    dist_unit : str
        The unit distance is measured in. default = 'metres'
    indoor : bool
        is round indoors for arrow diameter purposes? default = False

    Methods
    -------
    max_score()
        Returns the maximum score for Pass
    """

    # Two too many arguments, but logically this structure makes sense => disable
    # pylint: disable=too-many-arguments

    def __init__(
        self,
        n_arrows: int,
        diameter: float,
        scoring_system: str,
        distance: float,
        dist_unit: str = "metres",
        indoor: bool = False,
        diam_unit: str = "cm",
    ) -> None:
        self.n_arrows = abs(n_arrows)
        self.target = Target(
            diameter, scoring_system, distance, dist_unit, indoor, diam_unit
        )

    @property
    def distance(self) -> float:
        """Get distance."""
        return self.target.distance

    @property
    def native_dist_unit(self) -> str:
        """Get native_dist_unit."""
        return self.target.native_dist_unit

    @property
    def diameter(self) -> float:
        """Get diameter."""
        return self.target.diameter

    @property
    def native_diam_unit(self) -> str:
        """Get native_diameter unit."""
        return self.target.native_diameter_unit

    @property
    def scoring_system(self) -> str:
        """Get scoring_system."""
        return self.target.scoring_system

    @property
    def indoor(self) -> bool:
        """Get indoor."""
        return self.target.indoor

    def max_score(self) -> float:
        """
        Return the maximum numerical score possible on this pass (not counting x's).

        Returns
        -------
        max_score : float
            maximum score possible on this pass
        """
        return self.n_arrows * self.target.max_score()


class Round:
    """
    Class representing a Round.

    Describes an archer round made up of a number of Passes.
    e.g. for different distances.

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

    Methods
    -------
    get_info()
        Prints information about the round including name and breakdown of passes
    max_score()
        Returns the maximum score for Round

    """

    # Two too many arguments, but logically this structure makes sense => disable
    # pylint: disable=too-many-arguments

    def __init__(
        self,
        name: str,
        passes: List[Pass],
        location: Union[str, None] = None,
        body: Union[str, None] = None,
        family: Union[str, None] = None,
    ) -> None:
        self.name = name
        self.passes = passes
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

    def max_distance(self, unit: bool = False) -> Union[float, Tuple[float, str]]:
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
        """Print information about the Round."""
        print(f"A {self.name} consists of {len(self.passes)} passes:")
        for pass_i in self.passes:
            native_dist = Length.from_metres(
                pass_i.target.distance, pass_i.native_dist_unit
            )
            native_diam = Length.from_metres(
                pass_i.target.diameter, pass_i.native_diam_unit
            )

            print(
                f"\t- {pass_i.n_arrows} arrows "
                f"at a {native_diam:.1f} {pass_i.native_diam_unit} target "
                f"at {native_dist:.1f} {pass_i.native_dist_unit}s."
            )
