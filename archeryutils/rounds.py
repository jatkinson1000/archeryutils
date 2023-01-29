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
import json
from pathlib import Path
import warnings

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
            print(
                "\t- {} arrows at a {} cm target at {} {}s.".format(
                    pass_i.n_arrows,
                    pass_i.diameter * 100.0,
                    (
                        pass_i.target.distance / YARD_TO_METRE
                        if pass_i.native_dist_unit == "yard"
                        else pass_i.distance
                    ),
                    pass_i.native_dist_unit,
                )
            )

        return None

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
        else:
            return max_dist


def read_json_to_round_dict(json_filelist):
    """
    Subroutine to return round information read in from a json file as a dictionary of
    rounds

    Parameters
    ----------
    json_filelist : list of str
        filenames of json round files in ./round_data_files/

    Returns
    -------
    round_dict : dict of str : Round

    References
    ----------
    """
    if type(json_filelist) is not list:
        json_filelist = [json_filelist]

    round_data_files = Path(__file__).parent.joinpath("round_data_files")

    round_dict = {}

    for json_file in json_filelist:
        json_filepath = round_data_files.joinpath(json_file)
        with open(json_filepath) as json_round_file:
            data = json.load(json_round_file)

        for round_i in data:

            # Assign location
            if "location" not in round_i:
                warnings.warn(
                    f"No location provided for round {round_i['name']}. "
                    "Defaulting to None."
                )
                round_i["location"] = None
                round_i["indoor"] = False
            elif round_i["location"] in [
                "i",
                "I",
                "indoors",
                "indoor",
                "in",
                "inside",
                "Indoors",
                "Indoor",
                "In",
                "Inside",
            ]:
                round_i["indoor"] = True
                round_i["location"] = "indoor"
            elif round_i["location"] in [
                "o",
                "O",
                "outdoors",
                "outdoor",
                "out",
                "outside",
                "Outdoors",
                "Outdoor",
                "Out",
                "Outside",
            ]:
                round_i["indoor"] = False
                round_i["location"] = "outdoor"
            elif round_i["location"] in [
                "f",
                "F",
                "field",
                "Field",
                "woods",
                "Woods",
            ]:
                round_i["indoor"] = False
                round_i["location"] = "field"
            else:
                warnings.warn(
                    f"Location not recognised for round {round_i['name']}. "
                    "Defaulting to None"
                )
                round_i["indoor"] = False
                round_i["location"] = None

            # Assign governing body
            if "body" not in round_i:
                warnings.warn(
                    f"No body provided for round {round_i['name']}. "
                    "Defaulting to 'custom'."
                )
                round_i["body"] = "custom"
                # TODO: Could do sanitisation here e.g. AGB vs agb etc or trust user...
            
            # Assign round family
            if "family" not in round_i:
                warnings.warn(
                    f"No family provided for round {round_i['name']}. "
                    "Defaulting to ''."
                )
                round_i["family"] = ""

            # Assign passes
            passes = []
            for pass_i in round_i["passes"]:
                passes.append(
                    Pass(
                        pass_i["n_arrows"],
                        pass_i["diameter"] / 100,
                        pass_i["scoring"],
                        pass_i["distance"],
                        dist_unit=pass_i["dist_unit"],
                        indoor=round_i["indoor"],
                    )
                )

            round_dict[round_i["codename"]] = Round(
                round_i["name"],
                passes,
                location=round_i["location"],
                body=round_i["body"],
                family=round_i["family"],
            )

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
            raise AttributeError(self._attribute_err_msg(name))

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(self._attribute_err_msg(name))

    def _attribute_err_msg(self, name: str) -> str:
        quoted = [f"'{key}'" for key in self]
        return f"No such attribute: '{name}'. Please select from {', '.join(quoted)}."


# Generate a set of default rounds that come with this module, accessible as a DotDict:


def _make_rounds_dict(json_name: str) -> DotDict:
    return DotDict(read_json_to_round_dict(json_name))


AGB_outdoor_imperial = _make_rounds_dict("AGB_outdoor_imperial.json")
AGB_outdoor_metric = _make_rounds_dict("AGB_outdoor_metric.json")
AGB_indoor = _make_rounds_dict("AGB_indoor.json")
WA_outdoor = _make_rounds_dict("WA_outdoor.json")
WA_indoor = _make_rounds_dict("WA_indoor.json")
custom = _make_rounds_dict("Custom.json")

del _make_rounds_dict
