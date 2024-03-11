"""Utility module for conversion of qunatities and unit aliases.

Contains common abbreviations, pluralisations and capitilizations for supported
units as sets to allow easy membership checks in combination.
Supported units are provided as module attributes for easy autocompletion,
"""

from collections.abc import Collection, Set
from typing import TypeVar, Union

__all__ = [
    "yard",
    "metre",
    "inch",
    "cm",
    "to_metres",
    "from_metres",
    "definitive_unit",
    "definitive_units",
    "parse_optional_units",
    "known_units",
]

T = TypeVar("T")

# Add aliases to any new supported units here
yard = {
    "Yard",
    "yard",
    "Yards",
    "yards",
    "Y",
    "y",
    "Yd",
    "yd",
    "Yds",
    "yds",
}

metre = {
    "Metre",
    "metre",
    "Metres",
    "metres",
    "M",
    "m",
    "Ms",
    "ms",
}

cm = {
    "Centimetre",
    "centimetre",
    "Centimetres",
    "centimetres",
    "CM",
    "cm",
    "CMs",
    "cms",
}

inch = {
    "Inch",
    "inch",
    "Inches",
    "inches",
}

# Update _ALIASES and _CONVERSIONSTO_M for any new supported units
# And they will be automatically incorporated
_ALIASES = {
    "yard": yard,
    "metre": metre,
    "cm": cm,
    "inch": inch,
}


_CONVERSIONSTO_M = {
    "metre": 1.0,
    "yard": 0.9144,
    "cm": 0.01,
    "inch": 0.0254,
}


_reversed = {alias: name for name in _CONVERSIONSTO_M for alias in _ALIASES[name]}

_conversions = {
    alias: factor
    for name, factor in _CONVERSIONSTO_M.items()
    for alias in _ALIASES[name]
}


def to_metres(value: float, unit: str) -> float:
    """
    Convert distance in any supported unit to metres.

    Parameters
    ----------
    value : float
        scalar value of distance to be converted to metres
    unit : str
        units of distance to be converted to metres

    Returns
    -------
    float
        scalar value of converted distance in metres

    Examples
    --------
    >>> convert.to_metres(10, "inches")
    0.254
    """
    return _conversions[unit] * value


def from_metres(metre_value: float, unit: str) -> float:
    """
    Convert distance in metres to specified unit.

    Parameters
    ----------
    metre_value : float
        scalar value of distance in metres to be converted
    unit : str
        units distance is to be converted TO

    Returns
    -------
    float
        scalar value of converted distance in the provided unit

    Examples
    --------
    >>> convert.from_metres(18.3, "yards")
    20.0131
    """
    return metre_value / _conversions[unit]


def definitive_unit(alias: str) -> str:
    """
    Convert any string alias representing a distance unit to a single version.

    Parameters
    ----------
    alias : str
        name of unit to be converted

    Returns
    -------
    str
        definitive name of unit

    Examples
    --------
    >>> convert.definitive_unit("Metres")
    "metre"
    """
    return _reversed[alias]


def definitive_units(aliases: Collection[str]) -> set[str]:
    """
    Reduce a set of string unit aliases to just their definitive names.

    Parameters
    ----------
    aliases : set of str
        names of units to be converted

    Returns
    -------
    set of str
        definitive names of unit

    Examples
    --------
    >>> convert.definitive_units(convert.metre | convert.yard)
    {'metre', 'yard'}
    """
    return {_reversed[alias] for alias in aliases}


def parse_optional_units(
    value: Union[T, tuple[T, str]],
    supported: Set[str],
    default: str,
) -> tuple[T, str]:
    """
    Parse single value or tuple of value and units.

    Always returns a tuple of value and units

    Parameters
    ----------
    value : Any or tuple of Any, str
        Either a single object, or a tuple with the desired units.
    supported: set of str
        Set of units (and aliases) that are expected/supported.
    default: str
        Default unit to be used when value does not specify units.

    Raises
    ------
    ValueError
        If default units or parsed values units
        are not contained in supported units.

    Returns
    -------
    tuple of Any, str
        original value, definitive name of unit

    Notes
    -----
    The supported parameter encodes both which units can be used,
    and also which aliases are acceptable for those units.
    If your downstream functionality for example only works with imperial units.
    Then pass supported = {'inch', 'inches', 'yard', 'yards'} etc.
    The units parsed from value will be checked against this set.
    The default parameter is what will be provided in the result if the input value
    is a scalar, so this must also be present in the set of supported units.

    Examples
    --------
    >>> m_and_yd = convert.metre | convert.yard
    >>> convert.parse_optional_units(10, m_and_yd, "metre")
    (10, 'metre')
    >>> convert.parse_optional_units((10, 'yards') m_and_yd, 'metre')
    (10, 'yard')
    >>> convert.parse_optional_units((10, 'banana') m_and_yd, 'metre')
    ValueError: Unit 'banana' not recognised. Select from {'yard', 'metre'}.
    """
    if default not in supported:
        msg = f"Default unit {default!r} must be in supported units"
        raise ValueError(msg)
    if isinstance(value, tuple) and len(value) == 2:  # noqa: PLR2004
        quantity, units = value
    else:
        quantity = value
        units = default

    if units not in supported:
        msg = (
            f"Unit {units!r} not recognised. "
            f"Select from {definitive_units(supported)}."
        )
        raise ValueError(msg)
    return quantity, definitive_unit(units)


known_units: set[str] = definitive_units(_conversions)
"""Display all units that can be converted by this module."""
