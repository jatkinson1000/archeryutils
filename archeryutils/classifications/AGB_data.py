"""Set of useful enums for input to Archery GB classification routines."""

from enum import Enum, Flag, auto


class AGB_genders(Enum):
    """An enum for holding information about AGB genders."""

    MALE = auto()
    FEMALE = auto()


class AGB_ages(Flag):
    """An enum for holding information about AGB ages."""

    P50 = auto()
    ADULT = auto()
    U21 = auto()
    U18 = auto()
    U16 = auto()
    U15 = auto()
    U14 = auto()
    U12 = auto()


class AGB_bowstyles(Flag):
    """
    An enum for holding information about AGB bowstyles.

    Note that under AGB rules Longbow and English Longbow are identical, but English
    Longbow is used in field to avoid confusion with World Archery rules in which
    "Longbow" is equivalent to the Archery GB Flatbow.
    """

    COMPOUND = auto()
    RECURVE = auto()
    BAREBOW = auto()
    LONGBOW = auto()
    ENGLISHLONGBOW = LONGBOW
    TRADITIONAL = auto()
    FLATBOW = auto()
    COMPOUNDLIMITED = auto()
    COMPOUNDBAREBOW = auto()
