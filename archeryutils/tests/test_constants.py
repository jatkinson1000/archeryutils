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

    def test_unit_alias_reduction(self):
        """Test full set of unit alises can be reduced to just definitive names."""
        assert Length.definitive_units(Length.inch | Length.cm) == {"inch", "cm"}

    @pytest.mark.parametrize(
        "value,expected",
        [
            pytest.param(
                10,
                (10, "metre"),
                id="int-scalar",
            ),
            pytest.param(
                10.1,
                (10.1, "metre"),
                id="float-scalar",
            ),
            pytest.param(
                (10, "Metres"),
                (10, "metre"),
                id="default-units",
            ),
            pytest.param(
                (10, "yds"),
                (10, "yard"),
                id="other-units",
            ),
        ],
    )
    def test_optional_unit_parsing(self, value, expected):
        """Test parsing of quantities with and without units."""
        supported = Length.metre | Length.yard
        default = "metre"
        assert Length.parse_optional_units(value, supported, default) == expected

    def test_optional_unit_parsing_units_not_supported(self):
        """Test parsing of quantities with and without units."""
        with pytest.raises(ValueError, match="Unit (.+) not recognised. Select from"):
            assert Length.parse_optional_units(
                (10, "bannana"), Length.metre | Length.yard, "metre"
            )

    def test_optional_unit_parsing_default_not_supported(self):
        """Test parsing of quantities with and without units."""
        with pytest.raises(
            ValueError, match="Default unit (.+) must be in supported units"
        ):
            assert Length.parse_optional_units(10, Length.metre | Length.yard, "inch")
