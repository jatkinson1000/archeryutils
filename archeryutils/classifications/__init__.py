"""Module providing various classification functionalities."""

from .AGB_data import AGB_ages, AGB_bowstyles, AGB_genders
from .agb_field_classifications import (
    agb_field_classification_scores,
    calculate_agb_field_classification,
    coax_field_group,
)
from .agb_indoor_classifications import (
    agb_indoor_classification_scores,
    calculate_agb_indoor_classification,
    coax_indoor_group,
)
from .agb_old_field_classifications import (
    agb_old_field_classification_scores,
    calculate_agb_old_field_classification,
    coax_old_field_group,
)
from .agb_old_indoor_classifications import (
    agb_old_indoor_classification_scores,
    calculate_agb_old_indoor_classification,
    coax_old_indoor_group,
)
from .agb_old_outdoor_classifications import (
    agb_old_outdoor_classification_scores,
    calculate_agb_old_outdoor_classification,
)
from .agb_outdoor_classifications import (
    agb_outdoor_classification_scores,
    calculate_agb_outdoor_classification,
    coax_outdoor_group,
)

__all__ = [
    "AGB_ages",
    "AGB_bowstyles",
    "AGB_genders",
    "agb_field_classification_scores",
    "agb_indoor_classification_scores",
    "agb_old_field_classification_scores",
    "agb_old_indoor_classification_scores",
    "agb_old_outdoor_classification_scores", #new
    "agb_outdoor_classification_scores",
    "calculate_agb_field_classification",
    "calculate_agb_indoor_classification",
    "calculate_agb_old_field_classification",
    "calculate_agb_old_indoor_classification",
    "calculate_agb_old_outdoor_classification", #new
    "calculate_agb_outdoor_classification",
    "coax_field_group",
    "coax_indoor_group",
    "coax_old_field_group",
    "coax_old_indoor_group",
    # coax_old_outdoor
    "coax_outdoor_group",
]
