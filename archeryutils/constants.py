"""Constants used in the archeryutils package."""

from typing import Any, ClassVar, TypeVar, Union

T = TypeVar("T")

_CONVERSIONS_TO_M = {
    "metre": 1.0,
    "yard": 0.9144,
    "cm": 0.01,
    "inch": 0.0254,
}

_YARD_ALIASES = {
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

_METRE_ALIASES = {
    "Metre",
    "metre",
    "Metres",
    "metres",
    "M",
    "m",
    "Ms",
    "ms",
}

_CM_ALIASES = {
    "Centimetre",
    "centimetre",
    "Centimetres",
    "centimetres",
    "CM",
    "cm",
    "CMs",
    "cms",
}

_INCH_ALIASES = {
    "Inch",
    "inch",
    "Inches",
    "inches",
}

_ALIASES = {
    "yard": _YARD_ALIASES,
    "metre": _METRE_ALIASES,
    "cm": _CM_ALIASES,
    "inch": _INCH_ALIASES,
}


class Length:
    """
    Utility class for Length unit conversions.

    Contains common abbreviations, pluralisations and capitilizations for supported
    units as sets to allow easy membership checks in combination.
    Methods for conversions to and from metres are provided as classmethods.

    """

    yard = _YARD_ALIASES
    metre = _METRE_ALIASES
    cm = _CM_ALIASES
    inch = _INCH_ALIASES

    _reversed: ClassVar = {
        alias: name for name in _CONVERSIONS_TO_M for alias in _ALIASES[name]
    }

    _conversions: ClassVar = {
        alias: factor
        for name, factor in _CONVERSIONS_TO_M.items()
        for alias in _ALIASES[name]
    }

    @classmethod
    def to_metres(cls, value: float, unit: str) -> float:
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
        >>> Length.to_metres(10, "inches")
        0.254
        """
        return cls._conversions[unit] * value

    @classmethod
    def from_metres(cls, metre_value: float, unit: str) -> float:
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
        >>> Length.from_metres(18.3, "yards")
        20.0131
        """
        return metre_value / cls._conversions[unit]

    @classmethod
    def definitive_unit(cls, alias: str) -> str:
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
        >>> Length.definitive_unit("Metres")
        "metre"
        """
        return cls._reversed[alias]

    @classmethod
    def definitive_units(cls, aliases: set[str]) -> set[str]:
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
        >>> Length.definitive_unit(Length.metre | Length.yard)
        {'metre', 'yard'}
        """
        return {cls._reversed[alias] for alias in aliases}

    @classmethod
    def parse_optional_units(
        cls,
        value: Union[T, tuple[T, str]],
        supported: set[str],
        default: str,
    ) -> tuple[T, str]:
        """
        Parse single value or tuple of value and units.

        Always returns a tuple of value and units

        Parameters
        ----------
        value : Any or tuple of Any, str
            Either a single object, or a tuple with the desired units
        supported: set of str
            Valid unit aliases to be accepted
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

        Examples
        --------
        >>> m_and_yd = Length.metre | Length.yard
        >>> Length.parse_optional_units(10, m_and_yd, "metre")
        (10, 'metre')
        >>> Length.parse_optional_units((10, 'yards') m_and_yd, 'metre')
        (10, 'yard')
        >>> Length.parse_optional_units((10, 'banana') m_and_yd, 'metre')
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
                f"Select from {cls.definitive_units(supported)}."
            )
            raise ValueError(msg)
        return quantity, cls.definitive_unit(units)
