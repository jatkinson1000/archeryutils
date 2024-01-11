"""Constants used in the archeryutils package."""

_CONVERSIONS = {
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
    "Centimeter",
    "centimeter",
    "Centimeters",
    "centimeters",
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

_ALIASES = dict(
    yard = _YARD_ALIASES,
    metre = _METRE_ALIASES,
    cm = _CM_ALIASES,
    inch = _INCH_ALIASES,
)

class Length:
    yard = _YARD_ALIASES
    metre = _METRE_ALIASES
    cm = _CM_ALIASES
    inch = _INCH_ALIASES

    _reversed = {
        alias: name
        for name in _CONVERSIONS
        for alias in _ALIASES[name]
    }

    _conversions = {
        alias: factor
        for name, factor in _CONVERSIONS.items()
        for alias in _ALIASES[name]
    }

    @classmethod
    def to_metres(cls, value: float, unit: str) -> float:
        return cls._conversions[unit] * value

    @classmethod
    def from_metres(cls, metre_value: float, unit: str) -> float:
        return metre_value / cls._conversions[unit]

    @classmethod
    def definitive_name(cls, alias: str) -> str:
        return cls._reversed[alias]
