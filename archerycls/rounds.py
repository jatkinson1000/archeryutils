# Author        : Jack Atkinson
#
# Contributors  : Jack Atkinson
#
# Date Created  : 2022-08-16
# Last Modified : 2022-08-16 by Jack Atkinson
#
# Summary       : definition of classes to define rounds for archery applications
#

import archerycls.targets as targets


class Pass:
    """
    A class used to represent a Pass, a subunit of a Round
      e.g. a single distance or half

    Attributes
    ----------
    target : targets.Target
        a Target class representing the target used
    n_arrows : int
        the number of arrows shot at the target in this Pass

    Methods
    -------
    """
    def __init__(self, diameter, scoring_system, distance, n_arrows):
        """
        Parameters
        ----------
        diameter : float
            face diameter in [metres]
        scoring_system : str
            target face/scoring system type
        distance : float
            linear distance from archer to target
        n_arrows : int
            number of arrows in this pass

        """

        self.target = targets.Target(diameter, scoring_system, distance)
        self.n_arrows = n_arrows


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

    """
    def __init__(self, name, passes):
        """
        Parameters
        ----------
        name : str
            Formal name of the round
        passes : list of Pass
            a list of Pass classes making up the round

        """
        self.name = name
        self.passes = passes

    def get_info(self):
        """
        method get_info()
        Prints information about the round

        Attributes
        ----------

        Methods
        -------
        """
        print(f"A {self.name} round consists of {len(self.passes)} passes:")
        [print("\t- {} arrows at a {} cm target at {} metres.".format(
            pass_i.n_arrows, pass_i.target.diameter/100.0, pass_i.target.distance)) for pass_i in self.passes]

        # TODO: There is clearly a need here to deal with different units in an appropriate manner.
        #  e.g. we want to print imperial round distances in yards, not metres.
        #  Maybe use pint module in future? or encode a 'dia_base_unit' and 'dist_base_unit' attribute
        #  so as to keep all calculations in SI units?
