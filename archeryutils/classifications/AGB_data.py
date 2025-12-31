"""Set of useful enums for input to Archery GB classification routines."""

# To support python versions < 3.12 we can use the aenum library as a separate
# dependency before it was integrated into python3.11
# It is needed for iterable Flag in 3.11 and use of `in` for Flag in 3.12
import sys
import warnings
from typing import Any

if sys.version_info >= (3, 12):
    from enum import Enum, EnumMeta, Flag, auto
else:  # pragma: no cover
    from aenum import Enum, EnumMeta, Flag, auto


class AGB_genders(Enum):
    """
    An enum for holding information about AGB genders.

    The Open category is equivalent to Male for scores following 2025 rule changes.
    Scores remain the same, only branding has changed.
    """

    OPEN = auto()
    MALE = OPEN
    FEMALE = auto()


class AgeDeprecationMeta(EnumMeta):
    """Metaclass overriding getattribute to raise warning for deprecated age classes."""

    def __getattribute__(cls, name: str) -> Any:
        """Overridden getattribute to raise warning for deprecated age classes."""
        _deprecated_names = {
            "AGE_50_PLUS": "OVER_50",
            "AGE_ADULT": "ADULT",
            "AGE_UNDER_21": "UNDER_21",
            "AGE_UNDER_18": "UNDER_18",
            "AGE_UNDER_16": "UNDER_16",
            "AGE_UNDER_15": "UNDER_15",
            "AGE_UNDER_14": "UNDER_14",
            "AGE_UNDER_12": "UNDER_12",
        }

        if name in _deprecated_names:
            warnings.warn(
                f"'AGB_ages.{name}' is deprecated and will be removed in future, "
                f"use 'AGB_ages.{_deprecated_names[name]}' instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        return super().__getattribute__(name)


class AGB_ages(Flag, metaclass=AgeDeprecationMeta):
    """
    A Flag enum for holding information about AGB ages.

    Note: The 50+ category is represented with the key ``OVER_50``.
    """

    OVER_50 = auto()
    ADULT = auto()
    UNDER_21 = auto()
    UNDER_18 = auto()
    UNDER_16 = auto()
    UNDER_15 = auto()
    UNDER_14 = auto()
    UNDER_12 = auto()
    # Values preserved for legacy, but deprecated (see metaclass)
    AGE_50_PLUS = OVER_50
    AGE_ADULT = ADULT
    AGE_UNDER_21 = UNDER_21
    AGE_UNDER_18 = UNDER_18
    AGE_UNDER_16 = UNDER_16
    AGE_UNDER_15 = UNDER_15
    AGE_UNDER_14 = UNDER_14
    AGE_UNDER_12 = UNDER_12


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
