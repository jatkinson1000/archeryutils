"""Constants used in the archeryutils package."""

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

    _reversed = {alias: name for name in _CONVERSIONS_TO_M for alias in _ALIASES[name]}

    _conversions = {
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
