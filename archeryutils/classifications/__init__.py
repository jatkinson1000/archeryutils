"""Module providing various classification functionalities."""

from .AGB_data import AGB_ages, AGB_bowstyles, AGB_genders
from .agb_field_classifications import (
    agb_field_classification_scores,
    calculate_agb_field_classification,
)
from .agb_indoor_classifications import (
    agb_indoor_classification_scores,
    calculate_agb_indoor_classification,
)
from .agb_old_field_classifications import (
    agb_old_field_classification_scores,
    calculate_agb_old_field_classification,
)
from .agb_old_indoor_classifications import (
    agb_old_indoor_classification_scores,
    calculate_agb_old_indoor_classification,
)
from .agb_outdoor_classifications import (
    agb_outdoor_classification_scores,
    calculate_agb_outdoor_classification,
)

__all__ = [
    "AGB_ages",
    "AGB_bowstyles",
    "AGB_genders",
    "agb_field_classification_scores",
    "agb_indoor_classification_scores",
    "agb_old_field_classification_scores",
    "agb_old_indoor_classification_scores",
    "agb_outdoor_classification_scores",
    "calculate_agb_field_classification",
    "calculate_agb_indoor_classification",
    "calculate_agb_old_field_classification",
    "calculate_agb_old_indoor_classification",
    "calculate_agb_outdoor_classification",
]
