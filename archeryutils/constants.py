"""Constants used in the archeryutils package."""
from types import SimpleNamespace

TO_METRES = {
    "metre": 1.0,
    "yard": 0.9144,
    "cm": 0.01,
    "inch": 0.0254,
}

YARD_ALIASES = {
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

METRE_ALIASES = {
    "Metre",
    "metre",
    "Metres",
    "metres",
    "M",
    "m",
    "Ms",
    "ms",
}

CM_ALIASES = {
    "Centimeter",
    "centimeter",
    "Centimeters",
    "centimeters",
    "CM",
    "cm",
    "CMs",
    "cms",
}

INCH_ALIASES = {
    "Inch",
    "inch",
    "Inches",
    "inches",
}


DistanceUnits = SimpleNamespace(
    yard = YARD_ALIASES,
    metre = METRE_ALIASES,
    cm = CM_ALIASES,
    inch = INCH_ALIASES,
)

def normalise_unit_name(unit: str) -> str | None:
    """Convert any supported unit name alias into a cannonical string representation"""
    if unit in YARD_ALIASES:
        return 'yard'
    if unit in METRE_ALIASES:
        return 'metre'
    if unit in CM_ALIASES:
        return 'cm'
    if unit in INCH_ALIASES:
        return 'inch'
    return None
