"""Set of useful enums for input to Archery GB classification routines."""

# To support python versions < 3.12 we can use the aenum library as a separate
# dependency before it was integrated into python3.11
# It is needed for iterable Flag in 3.11 and use of `in` for Flag in 3.12
import sys

if sys.version_info >= (3, 12):
    from enum import Enum, Flag, auto
else:
    from aenum import Enum, Flag, auto


class AGB_genders(Enum):
    """An enum for holding information about AGB genders."""

    MALE = auto()
    FEMALE = auto()


class AGB_ages(Flag):
    """An enum for holding information about AGB ages."""

    AGE_50_PLUS = auto()
    AGE_ADULT = auto()
    AGE_UNDER_21 = auto()
    AGE_UNDER_18 = auto()
    AGE_UNDER_16 = auto()
    AGE_UNDER_15 = auto()
    AGE_UNDER_14 = auto()
    AGE_UNDER_12 = auto()


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
