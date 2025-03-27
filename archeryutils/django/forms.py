from django import forms
from django.db.models import BLANK_CHOICE_DASH

from archeryutils.rounds import Round


class RoundField(forms.ChoiceField):

    def __init__(self, rounds, **kwargs):
        self.rounds = rounds
        choices = BLANK_CHOICE_DASH + [(round.codename, round.name) for (codename, round) in rounds.items()]
        kwargs.setdefault("choices", choices)
        super().__init__(**kwargs)

    def clean(self, value):
        if value in self.rounds:
            return self.rounds[value]
        elif value is None:
            return None
        raise forms.ValidationError("Round type unknown", code="invalid")

    def prepare_value(self, value):
        if isinstance(value, Round):
            return value.codename
        return value
