# Author        : Jack Atkinson
#
# Contributors  : Jack Atkinson
#
# Date Created  : 2022-08-16
# Last Modified : 2022-08-16 by Jack Atkinson
#
# Summary       : definition of classes to define rounds for archery applications
#

import numpy as np
import json
from pathlib import Path

import archerycls.targets as targets
from archerycls.constants import YARD_TO_METRE


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
    max_score()
        Returns the maximum score for Pass
    """
    def __init__(self, n_arrows, diameter, scoring_system, distance, dist_unit='metres'):
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

        """

        self.n_arrows = n_arrows
        self.target = targets.Target(diameter, scoring_system, distance, dist_unit)

    def max_score(self):
        """
        max_score
        returns the maximum numerical score possible on this pass (i.e. not counting x's)

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

        Parameters
        ----------

        Returns
        -------
        """
        print(f"A {self.name} round consists of {len(self.passes)} passes:")
        for pass_i in self.passes:
            print("\t- {} arrows at a {} cm target at {} {}.".format(
                pass_i.n_arrows, pass_i.target.diameter*100.0,
                (pass_i.target.distance/YARD_TO_METRE if pass_i.target.native_dist_unit == 'yard'
                 else pass_i.target.distance),
                pass_i.target.native_dist_unit))

        return None

    def max_score(self):
        """
        max_score
        returns the maximum numerical score possible on this round (i.e. not counting x's)

        Parameters
        ----------

        Returns
        ----------
        max_score : float
            maximum score possible on this pass
        """

        return np.sum([pass_i.max_score() for pass_i in self.passes])


def read_json_to_round_dict(json_file):
    """
    Subroutine to return round information read in from a json file as a dictionary of rounds

    Parameters
    ----------
    json_file : str
        filepath to json file

    Returns
    -------
    round_dict : dict of str : Round

    References
    ----------
    """
    with open(json_file) as json_file:
        data = json.load(json_file)

    round_dict = {}

    for round_i in data:
        passes = []
        for pass_i in round_i['passes']:
            passes.append(Pass(pass_i['n_arrows'], pass_i['diameter']/100, pass_i['scoring'],
                               pass_i['distance'], dist_unit=pass_i['dist_unit'],))

        round_dict[round_i['codename']] = Round(round_i['name'], passes)

    return round_dict


class DotDict(dict):
    """
    A subclass of dict to provide dot notation access to a dictionary

    Attributes
    ----------

    Methods
    -------

    References
    -------
    https://goodcode.io/articles/python-dict-object/
    """
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError(f'''No such attribute: {name}.
            Please select from '{"', '".join([key for key in self.keys()])}'.''')

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(f'''No such attribute: {name}.
            Please select from '{"', '".join([key for key in self.keys()])}'.''')


# Generate a set of default rounds that come with this module, accessible as a DotDict:
AGB = DotDict(read_json_to_round_dict(f'{Path(__file__).parent}/round_data_files/AGB.json'))
WA = DotDict(read_json_to_round_dict(f'{Path(__file__).parent}/round_data_files/WA.json'))
