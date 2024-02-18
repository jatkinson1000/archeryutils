"""Module to load round data from json files into DotDicts."""

import json
from pathlib import Path
import warnings
from typing import Union, Any

from archeryutils.rounds import Pass, Round

LOCATIONS = {
    "indoor": {
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
    },
    "outdoor": {
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
    },
    "field": {
        "f",
        "F",
        "field",
        "Field",
        "woods",
        "Woods",
    },
}


def read_json_to_round_dict(json_filelist: Union[str, list[str]]) -> dict[str, Round]:
    """
    Read round information from a json file into a dictionary of rounds.

    Parameters
    ----------
    json_filelist : list of str
        filenames of json round files in ./round_data_files/

    Returns
    -------
    round_dict : dict of str : rounds.Round
    """
    if not isinstance(json_filelist, list):
        json_filelist = [json_filelist]

    round_data_files = Path(__file__).parent.joinpath("round_data_files")

    round_dict = {}

    for json_file in json_filelist:
        json_filepath = round_data_files.joinpath(json_file)
        with open(json_filepath, encoding="utf-8") as json_round_file:
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

            elif round_i["location"] in LOCATIONS["indoor"]:
                round_i["indoor"] = True
                round_i["location"] = "indoor"

            elif round_i["location"] in LOCATIONS["outdoor"]:
                round_i["indoor"] = False
                round_i["location"] = "outdoor"

            elif round_i["location"] in LOCATIONS["field"]:
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

            # Assign round family
            if "family" not in round_i:
                warnings.warn(
                    f"No family provided for round {round_i['name']}. "
                    "Defaulting to ''."
                )
                round_i["family"] = ""

            # Assign passes
            passes = [
                Pass.at_target(
                    pass_i["n_arrows"],
                    pass_i["scoring"],
                    (pass_i["diameter"], pass_i.get("diameter_unit", "cm")),
                    (pass_i["distance"], pass_i["dist_unit"]),
                    indoor=round_i["indoor"],
                )
                for pass_i in round_i["passes"]
            ]

            round_dict[round_i["codename"]] = Round(
                round_i["name"],
                passes,
                location=round_i["location"],
                body=round_i["body"],
                family=round_i["family"],
            )

    return round_dict


class DotDict(dict[str, Any]):
    """
    A subclass of dict to provide dot notation access to a dictionary.

    References
    ----------
    https://goodcode.io/articles/python-dict-object/
    """

    def __getattr__(self, name: str) -> Any:
        """
        getter.

        Parameters
        ----------
        name : str
            name of attribute to look for in self
        """
        if name in self:
            return self[name]
        raise AttributeError(self._attribute_err_msg(name))

    def __setattr__(self, name: str, value: Any) -> None:
        """
        setter.

        Parameters
        ----------
        name : str
            name of attribute to look for in self
        value : any
            value to set for attribute matching name
        """
        self[name] = value

    def __delattr__(self, name: str) -> None:
        """
        delete.

        Parameters
        ----------
        name : str
            name of attribute to delete from self
        """
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
WA_field = _make_rounds_dict("WA_field.json")
IFAA_field = _make_rounds_dict("IFAA_field.json")
WA_VI = _make_rounds_dict("WA_VI.json")
AGB_VI = _make_rounds_dict("AGB_VI.json")
custom = _make_rounds_dict("Custom.json")


del _make_rounds_dict
