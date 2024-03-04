"""Tests for constants, including Length class."""

import pytest

from archeryutils.constants import Length

CM = "cm"
INCH = "inch"
METRE = "metre"
YARD = "yard"


class TestLengths:
    """Tests for Length class."""

    def test_units_available(self):
        """Test common length unit names."""
        assert CM in Length.cm
        assert INCH in Length.inch
        assert METRE in Length.metre
        assert YARD in Length.yard

    def test_pluralised_unit_alises_available(self):
        """Test plurailised versions of common length unit names."""
        assert CM + "s" in Length.cm
        assert INCH + "es" in Length.inch
        assert METRE + "s" in Length.metre
        assert YARD + "s" in Length.yard

    @pytest.mark.parametrize(
        "value,unit,result",
        [
            (10, "metre", 10),
            (10, "cm", 0.1),
            (10, "inch", 0.254),
            (10, "yard", 9.144),
        ],
    )
    def test_conversion_to_metres(self, value, unit, result):
        """Test conversion from other units to metres."""
        assert Length.to_metres(value, unit) == result

    @pytest.mark.parametrize(
        "value,unit,result",
        [
            (10, "metre", 10),
            (10, "cm", 1000),
            (10, "inch", 393.7008),
            (10, "yard", 10.93613),
        ],
    )
    def test_conversion_from_metres(self, value, unit, result):
        """Test conversion from metres to other units."""
        assert Length.from_metres(value, unit) == pytest.approx(result)

    @pytest.mark.parametrize(
        "unit,result",
        [
            ("m", "metre"),
            ("centimetre", "cm"),
            ("Inch", "inch"),
            ("yd", "yard"),
        ],
    )
    def test_unit_name_coercion(self, unit, result):
        """Test unit name standardisation available on Length class."""
        assert Length.definitive_unit(unit) == result
