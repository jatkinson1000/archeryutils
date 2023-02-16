# Author        : Jack Atkinson
#
# Contributors  : Jack Atkinson
#
# Date Created  : 2022-08-16
# Last Modified : 2022-08-22 by Jack Atkinson
#
# Summary       : definition of classes to define rounds for archery applications
#

import numpy as np

from archeryutils.targets import Target
from archeryutils.constants import YARD_TO_METRE


class Pass:
    """
    A class used to represent a Pass, a subunit of a Round
      e.g. a single distance or half

    Attributes
    ----------
    target : Target
        a Target class representing the target used
    n_arrows : int
        the number of arrows shot at the target in this Pass

    Methods
    -------
    max_score()
        Returns the maximum score for Pass
    """

    def __init__(
        self,
        n_arrows,
        diameter,
        scoring_system,
        distance,
        dist_unit="metres",
        indoor=False,
    ):
        """
        Parameters
        ----------
        n_arrows : int
            number of arrows in this pass
        diameter : float
            face diameter in [metres]
        scoring_system : str
            target face/scoring system type
        distance : float
            linear distance from archer to target
        dist_unit : str
            The unit distance is measured in. default = 'metres'
        indoor : bool
            is round indoors for arrow diameter purposes? default = False
        """

        self.n_arrows = n_arrows
        self.target = Target(diameter, scoring_system, distance, dist_unit, indoor)

    @property
    def distance(self):
        return self.target.distance

    @property
    def native_dist_unit(self):
        return self.target.native_dist_unit

    @property
    def diameter(self):
        return self.target.diameter

    @property
    def scoring_system(self):
        return self.target.scoring_system

    @property
    def indoor(self):
        return self.target.indoor

    def max_score(self):
        """
        max_score
        returns the maximum numerical score possible on this pass (not counting x's)

        Parameters
        ----------

        Returns
        ----------
        max_score : float
            maximum score possible on this pass
        """

        return self.n_arrows * self.target.max_score()


class Round:
    """
    A class used to represent a Round
    Made up of a number of Passes

    Attributes
    ----------
    name : str
        Formal name of the round
    passes : list of Pass
        a list of Pass classes making up the round

    Methods
    -------
    get_info()
        Prints information about the round including name and breakdown of passes
    max_score()
        Returns the maximum score for Round

    """

    def __init__(self, name, passes, location=None, body=None, family=None):
        """
        Parameters
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

        """
        self.name = name
        self.passes = passes
        self.location = location
        self.body = body
        self.family = family

    def get_info(self):
        """
        method get_info()
        Prints information about the round

        Parameters
        ----------

        Returns
        -------
        """
        print(f"A {self.name} consists of {len(self.passes)} passes:")
        for pass_i in self.passes:
            if pass_i.native_dist_unit == "yard":
                native_dist = pass_i.target.distance / YARD_TO_METRE
            else:
                native_dist = pass_i.distance
            print(
                f"\t- {pass_i.n_arrows} arrows "
                f"at a {pass_i.diameter * 100.0} cm target "
                f"at {native_dist} {pass_i.native_dist_unit}s."
            )

    def max_score(self):
        """
        max_score
        returns the maximum numerical score possible on this round (not counting x's)

        Parameters
        ----------

        Returns
        ----------
        max_score : float
            maximum score possible on this round
        """

        return np.sum([pass_i.max_score() for pass_i in self.passes])

    def max_distance(self, unit=False):
        """
        max_distance
        returns the maximum distance shot on this round along with the unit (optional)

        Parameters
        ----------
        unit : bool
            Return unit as well as numerical value?

        Returns
        ----------
        max_dist : float
            maximum distance shot in this round
        (max_dist, unit) : tuple (float, str)
            tuple of max_dist and string of unit
        """
        max_dist = 0
        for pass_i in self.passes:
            dist = (
                pass_i.distance / YARD_TO_METRE
                if pass_i.native_dist_unit == "yard"
                else pass_i.distance
            )
            if dist > max_dist:
                max_dist = dist
                d_unit = pass_i.native_dist_unit

        if unit:
            return (max_dist, d_unit)
        return max_dist
