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
    Utility class for Length unit conversions

    Contains common abbreviations, pluralisations and capitilizations for supported
    units as sets to allow easy membership checks in combination.
    Methods for conversions to and from metres are provided as classmethods.

    Attributes
    ----------
    yard : set[str]
    metre : set[str]
    cm: set[str]
    inch: set[str]

    Methods
    -------
    to_metres()
        Convert distance in any supported unit to metres
    from_metres()
        Convert distance in metres to any supported unit
    definitive_name()
        Convert any string alias representing a distance unit to a single version.
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
        """Convert value in metres to given unit"""
        return cls._conversions[unit] * value

    @classmethod
    def from_metres(cls, metre_value: float, unit: str) -> float:
        """Convert value in given unit to metres"""
        return metre_value / cls._conversions[unit]

    @classmethod
    def definitive_name(cls, alias: str) -> str:
        """Convert alias for unit into a single definied name set in constants"""
        return cls._reversed[alias]
