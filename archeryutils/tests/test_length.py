"""Tests for length conversion module."""

import pytest

from archeryutils import length

CM = "cm"
INCH = "inch"
METRE = "metre"
YARD = "yard"


class TestLengths:
    """Tests for length module."""

    def test_units_available(self):
        """Check and document currently supported units."""
        assert length.known_units == {CM, INCH, METRE, YARD}

    def test_units_available_on_attributes(self):
        """Test common length unit names."""
        assert CM in length.cm
        assert INCH in length.inch
        assert METRE in length.metre
        assert YARD in length.yard

    def test_pluralised_unit_alises_available(self):
        """Test plurailised versions of common length unit names."""
        assert CM + "s" in length.cm
        assert INCH + "es" in length.inch
        assert METRE + "s" in length.metre
        assert YARD + "s" in length.yard

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
        assert length.to_metres(value, unit) == pytest.approx(result)

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
        assert length.from_metres(value, unit) == pytest.approx(result)

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
        assert length.definitive_unit(unit) == result

    def test_unit_alias_reduction(self):
        """Test full set of unit alises can be reduced to just definitive names."""
        assert length.definitive_units(length.inch | length.cm) == {"inch", "cm"}

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
        supported = length.metre | length.yard
        default = "metre"
        assert length.parse_optional_units(value, supported, default) == expected

    def test_optional_unit_parsing_units_not_supported(self):
        """Test parsing of quantities with and without units."""
        with pytest.raises(ValueError, match="Unit (.+) not recognised. Select from"):
            length.parse_optional_units(
                (10, "bannana"), length.metre | length.yard, "metre"
            )

    def test_optional_unit_parsing_default_not_supported(self):
        """Test parsing of quantities with and without units."""
        with pytest.raises(
            ValueError, match="Default unit (.+) must be in supported units"
        ):
            length.parse_optional_units(10, length.metre | length.yard, "inch")
