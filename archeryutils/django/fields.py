from django.db import models

from archeryutils.rounds import Round


class RoundField(models.CharField):
    description = "Choose from a set of archery rounds"

    def __init__(self, rounds, **kwargs):
        self.rounds = rounds
        self._round_dict = (
            rounds  # TOOD: allow more complex round structures to be passed
        )

        # TODO Hack for deconstruction for now
        if isinstance(rounds, list):
            self._round_dict = {r: r for r in rounds}

        kwargs.setdefault("max_length", 64)
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # TODO - round deconstruction
        kwargs["rounds"] = list(self._round_dict.keys())
        return name, path, args, kwargs

    @property
    def non_db_attrs(self):
        return super().non_db_attrs + ("rounds",)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self._round_dict[value]

    def to_python(self, value):
        if isinstance(value, Round):
            return value.codename

        if value is None:
            return value

        if value in self.rounds:
            return self._round_dict[value]

        raise ValueError("Round unknown")

    def get_prep_value(self, value):
        if isinstance(value, Round):
            return value.codename
        return value

    def formfield(self, **kwargs):
        from . import forms

        return forms.RoundField(rounds=self.rounds, required=not self.blank)
