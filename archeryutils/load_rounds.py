"""Module to load round data from json files into DotDicts."""

import json
import warnings
from pathlib import Path
from typing import Any, TypeVar

from archeryutils.rounds import Pass, Round

V = TypeVar("V")

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


# --- Deprecated codename support ------------------------------------------
# Round JSON entries may declare a "deprecated_names" list of legacy codenames.
# Looking up a deprecated codename resolves to the canonical Round and emits a
# DeprecationWarning.  To remove the deprecation framework in future, delete
# _collect_deprecated_names, the deprecated_names= kwarg in read_json_to_round_dict,
# the four deprecation-aware methods on DotDict (__init__, __getitem__,
# __contains__, get), and simplify the __add__ method. Also remove related tests.


def _collect_deprecated_names(rounds_data: list[dict[str, Any]]) -> dict[str, str]:
    """
    Collect and validate deprecated codename aliases from parsed round data.

    Parameters
    ----------
    rounds_data : list[dict[str, Any]]
        Parsed round entries loaded from json.

    Returns
    -------
    dict[str, str]
        Mapping of deprecated alias to canonical codename.

    Raises
    ------
    ValueError
        If an alias clashes with a canonical codename or is duplicated.
    """
    codenames = {r["codename"] for r in rounds_data}
    deprecated_names: dict[str, str] = {}
    for round_i in rounds_data:
        for deprecation in round_i.get("deprecated_names") or []:
            if deprecation in codenames:
                msg = (
                    f"Deprecated codename '{deprecation}' clashes with an "
                    f"existing round codename."
                )
                raise ValueError(msg)
            if deprecation in deprecated_names:
                msg = (
                    f"Duplicate deprecated codename '{deprecation}' declared "
                    f"for rounds "
                    f"'{deprecated_names[deprecation]}' and '{round_i['codename']}'."
                )
                raise ValueError(msg)
            deprecated_names[deprecation] = round_i["codename"]
    return deprecated_names


class DotDict(dict[str, V]):
    """
    A subclass of dict to provide dot notation access to a dictionary.

    Also supports backwards-compatible resolution for deprecated round
    codenames. Looking up a deprecated codename returns the canonical
    :class:`~archeryutils.rounds.Round` and emits a :class:`DeprecationWarning`.

    Two DotDicts can be combined with ``+``, merging entries and deprecated
    names into a new DotDict.

    References
    ----------
    https://goodcode.io/articles/python-dict-object/
    """

    def __init__(
        self,
        *args: Any,
        deprecated_names: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        object.__setattr__(
            self,
            "_deprecated_names",
            dict(deprecated_names) if deprecated_names else {},
        )

    def __getitem__(self, key: Any) -> V:
        """
        Get item, resolving deprecated codenames with a warning.

        Added to DotDict to provide a front layer to any item fetches and handle
        warnings for deprecated codenames.

        Parameters
        ----------
        key : Any
            Codename (or deprecated codename) to look up.

        Raises
        ------
        KeyError
            If the key is neither a canonical codename nor a known deprecation.
        """
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        deprecated_names = self.__dict__.get("_deprecated_names", {})
        if isinstance(key, str) and key in deprecated_names:
            canonical = deprecated_names[key]
            warnings.warn(
                f"Round codename '{key}' is deprecated; use '{canonical}' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return dict.__getitem__(self, canonical)
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        """
        Check membership, including deprecated codenames (without warning).

        Added to DotDict to allow checking of deprecation entries as well as dict
        contents.

        """
        return dict.__contains__(self, key) or (
            isinstance(key, str) and key in self.__dict__.get("_deprecated_names", {})
        )

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get item, resolving deprecated codenames with a warning.

        Definition needed to call modified __contains__ and __getitem__.
        """
        if key in self:  # Use modified __contains__
            return self[key]  # Use modified __getitem__
        return default

    def __add__(self, other: "DotDict[V]") -> "DotDict[V]":
        """
        Combine two DotDicts into a new DotDict.

        Merges the codename to item pairs and deprecated name mappings of
        both operands. Codenames and deprecated names must each be unique
        across the two DotDicts.

        Parameters
        ----------
        other : DotDict
            The DotDict to combine with this one.

        Returns
        -------
        DotDict
            A new ``DotDict`` containing all entries and deprecated names
            from both operands.

        Raises
        ------
        ValueError
            If the DotDicts share a codename or deprecated name, or if a
            deprecated name clashes with a codename in the combined DotDict.
        """
        if not isinstance(other, DotDict):
            return NotImplemented

        duplicates = self.keys() & other.keys()
        if duplicates:
            msg = f"Duplicate codename(s) {sorted(duplicates)} found in both DotDicts."
            raise ValueError(msg)

        self_deprecated = self.__dict__.get("_deprecated_names", {})
        other_deprecated = other.__dict__.get("_deprecated_names", {})
        duplicates = set(self_deprecated) & set(other_deprecated)
        if duplicates:
            msg = (
                f"Duplicate deprecated name(s) {sorted(duplicates)} found in "
                f"both DotDicts."
            )
            raise ValueError(msg)

        combined = {**self, **other}
        deprecated_names = {**self_deprecated, **other_deprecated}
        clashes = deprecated_names.keys() & combined.keys()
        if clashes:
            msg = (
                f"Deprecated codename(s) {sorted(clashes)} clash with an "
                f"existing round codename."
            )
            raise ValueError(msg)

        return DotDict(combined, deprecated_names=deprecated_names)

    def __getattr__(self, name: str) -> Any:
        """
        Getter.

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
        Setter.

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
        Delete.

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


def read_json_to_round_dict(json_filelist: str | list[str]) -> DotDict[Round]:
    """
    Read round information from a json file into a dictionary of rounds.

    Parameters
    ----------
    json_filelist : str | list[str]
        filenames of json round files in ./round_data_files/

    Returns
    -------
    DotDict[Round]
        A ``DotDict`` of codename to :class:`~archeryutils.rounds.Round` with
        dot-notation access and backwards-compatible deprecation resolution.
    """
    if not isinstance(json_filelist, list):
        json_filelist = [json_filelist]

    round_data_files = Path(__file__).parent.joinpath("round_data_files")

    round_dict: dict[str, Round] = {}
    all_data: list[dict[str, Any]] = []

    for json_file in json_filelist:
        json_filepath = round_data_files.joinpath(json_file)
        with open(json_filepath, encoding="utf-8") as json_round_file:
            data = json.load(json_round_file)
        all_data.extend(data)

        for round_i in data:
            codename = round_i["codename"]

            # Assign location
            if "location" not in round_i:
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
                round_i["indoor"] = False
                round_i["location"] = None

            # Assign governing body
            if "body" not in round_i:
                round_i["body"] = None

            # Assign round family
            if "family" not in round_i:
                round_i["family"] = None

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

            round_dict[codename] = Round(
                round_i["name"],
                passes,
                codename=codename,
                location=round_i["location"],
                body=round_i["body"],
                family=round_i["family"],
            )

    deprecated_names = _collect_deprecated_names(all_data)

    return DotDict(round_dict, deprecated_names=deprecated_names)


# Generate a set of default rounds that come with this module, accessible as a DotDict:
def _make_rounds_dict(json_name: str | list[str]) -> DotDict[Round]:
    return read_json_to_round_dict(json_name)


AGB_outdoor_imperial = _make_rounds_dict("AGB_outdoor_imperial.json")
AGB_outdoor_metric = _make_rounds_dict(["AGB_outdoor_metric.json", "WA_outdoor.json"])
AGB_indoor = _make_rounds_dict("AGB_indoor.json")
AGB_field = _make_rounds_dict("AGB_field.json")
AGB_VI = _make_rounds_dict("AGB_VI.json")
WA_outdoor = _make_rounds_dict("WA_outdoor.json")
WA_indoor = _make_rounds_dict("WA_indoor.json")
WA_field = _make_rounds_dict("WA_field.json")
WA_VI = _make_rounds_dict("WA_VI.json")
WA_experimental = _make_rounds_dict("WA_experimental.json")
IFAA_field = _make_rounds_dict("IFAA_field.json")
AA_outdoor_metric = _make_rounds_dict("AA_outdoor_metric.json")
AA_indoor = _make_rounds_dict("AA_indoor.json")
AA_field = _make_rounds_dict("AA_field.json")
misc = _make_rounds_dict("Miscellaneous.json")


del _make_rounds_dict
