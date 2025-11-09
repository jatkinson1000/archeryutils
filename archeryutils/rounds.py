"""Module to define a Pass and Round classes for archery applications."""

from collections.abc import Iterable

from archeryutils.targets import Quantity, ScoringSystem, Target


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
    target : Target
        A Target object.

    Attributes
    ----------
    n_arrows : int
        number of arrows in this pass.
    target : Target
        A Target object.

    Examples
    --------
    A Pass can be defined simply as:

    >>> my720pass = au.Pass(36, au.Target("10_zone", 122, 70.0))

    See Also
    --------
    archeryutils.Target : The `Target` class.
    """

    def __init__(self, n_arrows: int, target: Target) -> None:
        self.n_arrows = abs(n_arrows)
        self.target = target
        if not isinstance(self.target, Target):
            msg = "The target passed to a Pass should be of type Target."
            raise TypeError(msg)

    @classmethod
    def at_target(
        cls,
        n_arrows: int,
        scoring_system: ScoringSystem,
        diameter: float | tuple[float, str],
        distance: float | tuple[float, str],
        indoor: bool = False,
    ) -> "Pass":
        """
        Initalise a Pass directly with the parameters of its target.

        The parameters are passed directly to the default Target constuctor and
        therefore share the same behaviours and defaults.

        Parameters
        ----------
        n_arrows : int
            number of arrows in this pass
        scoring_system : ScoringSystem
            Literal string value of target face/scoring system type.
        diameter : float | tuple[float, str]
            Target diameter size (and units, default [cm])
        distance : float | tuple[float, str]
            Target distance (and units, default [metres])
        indoor : bool
            is round indoors for arrow diameter purposes? default = False

        Returns
        -------
        Pass
            The constructed Pass instance

        Examples
        --------
        >>> pass_ = au.Pass.at_target(36, "10_zone", 122, 70.0)

        Like with the Target class, the units for diameter and distance can be
        explicitly specified using tuples:

        >>> myWA18pass = au.Pass.at_target(
        ...     30, "10_zone", (40, "cm"), (18.0, "m"), indoor=True
        ... )
        """
        target = Target(scoring_system, diameter, distance, indoor)
        return cls(n_arrows, target)

    def __repr__(self) -> str:
        """Return a representation of a Pass instance."""
        return f"Pass({self.n_arrows}, {self.target})"

    def __eq__(self, other: object) -> bool:
        """Check equality of Passes based on parameters."""
        if not isinstance(other, Pass):
            return NotImplemented
        return self.n_arrows == other.n_arrows and self.target == other.target

    def __hash__(self) -> int:
        """Generate hash for the Pass object."""
        return hash((self.n_arrows, self.target))

    @property
    def scoring_system(self) -> ScoringSystem:
        """Get target scoring_system."""
        return self.target.scoring_system

    @property
    def diameter(self) -> float:
        """Get target diameter in [metres]."""
        return self.target.diameter

    @property
    def distance(self) -> float:
        """Get target distance in [metres]."""
        return self.target.distance

    @property
    def native_diameter(self) -> Quantity:
        """Get diameter of target in native units."""
        return self.target.native_diameter

    @property
    def native_distance(self) -> Quantity:
        """Get distance of target in native units."""
        return self.target.native_distance

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
    codename : str or None
        A machine readable identifier for the round
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
    location : str | None
        string identifing where the round is shot
    body : str | None
        string identifing the governing body the round belongs to
    family : str | None
        string identifing the family the round belongs to (e.g. wa1440, western, etc.)
    n_arrows : int
        total number of arrows in this round

    Examples
    --------
    Before defining a Round we need to first define the passes that make it up:

    >>> my720pass = au.Pass.at_target(36, "10_zone", 122, 70.0)

    These can now be passed to the Round constructor as any iterable,
    they will be stored as a list:

    >>> my720round = au.Round("WA 720", [my720pass, my720pass])
    >>> my720round2 = au.Round("WA 720", (my720pass, my720pass))
    >>> assert my720round.passes == my720round2.passes == [my720pass, my720pass]

    Additional, optional parameters can be used to provide 'metadata' about the round.

    """

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        passes: Iterable[Pass],
        codename: str | None = None,
        location: str | None = None,
        body: str | None = None,
        family: str | None = None,
    ) -> None:
        self.name = name
        self.codename = codename
        self.passes = list(passes)
        if not self.passes:
            msg = "passes must contain at least one Pass object but none supplied."
            raise ValueError(msg)
        if any(not isinstance(x, Pass) for x in self.passes):
            msg = "passes in a Round object should be an iterable of Pass objects."
            raise TypeError(msg)
        self.location = location
        self.body = body
        self.family = family
        self.n_arrows: int = sum(pass_i.n_arrows for pass_i in self.passes)

    def __repr__(self) -> str:
        """Return a representation of a Round instance."""
        return f"<Round: '{self.name}'>"

    def __eq__(self, other: object) -> bool:
        """Check equality of Rounds based on name and passes.

        Does not consider optional labels of location/body/family as these
        do not affect behaviour.
        """
        if not isinstance(other, Round):
            return NotImplemented
        return self.name == other.name and self.passes == other.passes

    def __hash__(self) -> int:
        """Generate hash for the Round object."""
        return hash((self.name, tuple(self.passes)))

    def max_score(self) -> float:
        """
        Return the maximum numerical score possible on this round (not counting x's).

        Returns
        -------
        max_score : float
            maximum score possible on this round
        """
        return sum(pass_i.max_score() for pass_i in self.passes)

    def max_distance(self) -> Quantity:
        """
        Return the maximum distance shot on this round along with the unit (optional).

        Returns
        -------
        max_dist : Quantity
            maximum distance and units shot in this round

        Notes
        -----
        This does not convert the units of the result.
        Rather the maximum distance shot in the round is returned in
        whatever units it was defined in.
        """
        longest_pass = max(self.passes, key=lambda p: p.distance)
        return longest_pass.native_distance

    # def n_arrows(self) -> int:
    #     """
    #     Return the total number of arrows shot on this round.
    #
    #     Returns
    #     -------
    #     n_arrows : int
    #         number of arrows in the round
    #     """
    #     return sum(pass_i.n_arrows for pass_i in self.passes)

    def get_info(self) -> None:
        """
        Print information about the Round.

        Prints a summary of each Pass in the round giving number of arrows,
        distance, and target size.

        """
        print(f"A {self.name} consists of {len(self.passes)} passes:")
        for pass_i in self.passes:
            diam, diam_units = pass_i.native_diameter
            dist, dist_units = pass_i.native_distance
            print(
                f"\t- {pass_i.n_arrows} arrows "
                f"at a {diam:.1f} {diam_units} target "
                f"at {dist:.1f} {dist_units}s.",
            )
