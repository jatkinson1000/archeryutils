"""Tests for Target class."""

from typing import Final

import pytest

from archeryutils.targets import ScoringSystem, Target


class TestTarget:
    """Tests for the Target class."""

    def test_repr(self) -> None:
        """Check Target string representation is as expected."""
        target = Target("10_zone", 80, 30)
        expected = "Target('10_zone', (80, 'cm'), (30, 'metre'), indoor=False)"
        assert repr(target) == expected

    def test_repr_native_units(self) -> None:
        """Check Target string representation returns values in native units."""
        target = Target("Worcester", (16, "inches"), (20, "yards"), indoor=True)
        expected = "Target('Worcester', (16, 'inch'), (20, 'yard'), indoor=True)"
        assert repr(target) == expected

    @pytest.mark.parametrize(
        "args, result",
        [
            pytest.param(
                ("10_zone", (40, "cm"), (20, "metre"), True),
                True,
                id="duplicate",
            ),
            pytest.param(
                ("10_zone", 40, 20, True),
                True,
                id="units-free",
            ),
            pytest.param(
                ("10_zone", (40, "cm"), (20, "metre"), False),
                False,
                id="different-loc",
            ),
            pytest.param(
                ("5_zone", (40, "cm"), (20, "metre"), True),
                False,
                id="different-scoring",
            ),
            pytest.param(
                ("10_zone", (40, "cm"), (19.9, "metre"), True),
                False,
                id="different-dist",
            ),
            pytest.param(
                ("10_zone", (40.1, "cm"), (20, "metre"), True),
                False,
                id="different-diam",
            ),
            pytest.param(
                ("10_zone", (40, "cm"), (20, "yard"), True),
                False,
                id="different-dist-unit",
            ),
            pytest.param(
                ("10_zone", (40, "inch"), (20, "metre"), True),
                False,
                id="different-diam-unit",
            ),
        ],
    )
    def test_equality(self, args, result) -> None:
        """Check Target equality comparison is supported."""
        target = Target("10_zone", (40, "cm"), (20, "metre"), indoor=True)
        comparison = target == Target(*args)
        assert comparison == result

    def test_equality_different_object(self) -> None:
        """Check Target equality comparison against a differnt type of object."""
        target = Target("10_zone", 40, (20, "yard"), indoor=True)

        assert target != ("10_zone", 40, (20, "yard"), True)

    def test_hash_consistency(self) -> None:
        """Check hash is same for same object."""
        target = Target("10_zone", 40, (20, "yard"), indoor=True)
        assert hash(target) == hash(target)

    def test_hash_uniqueness(self) -> None:
        """Check hash is different for different objects."""
        target1 = Target("10_zone", 40, (20, "yard"), indoor=True)
        target2 = Target("5_zone", 40, (20, "yard"), indoor=True)
        target3 = Target("10_zone", 122, (20, "yard"), indoor=True)
        target4 = Target("10_zone", 40, (80, "yard"), indoor=True)
        target5 = Target("10_zone", 40, (20, "metre"), indoor=True)
        target6 = Target("10_zone", 40, (20, "yard"), indoor=False)

        assert hash(target1) != hash(target2)
        assert hash(target1) != hash(target3)
        assert hash(target1) != hash(target4)
        assert hash(target1) != hash(target5)
        assert hash(target1) != hash(target6)

    def test_hashable_in_set(self) -> None:
        """Check hash can be used in a set."""
        target1 = Target("10_zone", 40, (20, "yard"), indoor=True)
        target2 = Target("10_zone", 30, (80, "yard"), indoor=False)
        targets_set = {target1, target2}
        assert target1 in targets_set
        assert target2 in targets_set

    def test_hashable_in_dict(self) -> None:
        """Check hash can be used in a dict as keys."""
        target1 = Target("10_zone", 40, (20, "yard"), indoor=True)
        target2 = Target("10_zone", 30, (80, "yard"), indoor=False)
        targets_dict = {target1: "First Target", target2: "Second Target"}
        assert targets_dict[target1] == "First Target"
        assert targets_dict[target2] == "Second Target"

    def test_invalid_system(self) -> None:
        """Check that Target() returns error value for invalid system."""
        with pytest.raises(
            ValueError,
            match=r"Invalid Target Face Type specified.\nPlease select from '(.+)'.",
        ):
            # Silence mypy as scoring_system must be a valid literal ScoringSystem
            Target("InvalidScoringSystem", 122, 50, False)  # type: ignore[arg-type]

    def test_invalid_distance_unit(self) -> None:
        """Check that Target() returns error value for invalid distance units."""
        with pytest.raises(
            ValueError, match=r"Unit '(.+)' not recognised. Select from"
        ):
            Target("5_zone", 122, (50, "InvalidDistanceUnit"), False)

    def test_default_distance_unit(self) -> None:
        """Check that Target() returns distance in metres when units not specified."""
        target = Target("5_zone", 122, 50)
        assert target.native_distance == (50, "metre")

    def test_yard_to_m_conversion(self) -> None:
        """Check Target() returns correct distance in metres when yards provided."""
        target = Target("5_zone", 122, (50, "yards"))
        assert target.native_distance == (50, "yard")
        assert target.distance == pytest.approx(50.0 * 0.9144)

    def test_invalid_diameter_unit(self) -> None:
        """Check Target() raises error when called with unsupported diameter units."""
        with pytest.raises(
            ValueError, match=r"Unit '(.+)' not recognised. Select from"
        ):
            Target("5_zone", (122, "bananas"), (50, "yards"))

    def test_default_diameter_unit(self) -> None:
        """Check that Target() is using centimetres by default for diameter."""
        target = Target("10_zone_5_ring_compound", 80, 50)
        assert target.diameter == pytest.approx(80 * 0.01)

    def test_diameter_metres_not_converted(self) -> None:
        """Check that Target() is storing diameter in metres."""
        target = Target("Beiter_hit_miss", (0.04, "m"), 18)
        assert target.diameter == 0.04

    def test_diameter_inches_supported(self) -> None:
        """Check that Target() converts diameters in inches correctly."""
        target = Target("Worcester", (16, "inches"), (20, "yards"), indoor=True)
        assert target.native_diameter == (16, "inch")
        assert target.diameter == pytest.approx(16 * 0.0254)

    def test_diameter_distance_units_coerced_to_definitive_names(self) -> None:
        """Check that Target coerces aliased distance units into standard names."""
        imperial_target = Target(
            "Worcester",
            (16, "Inches"),
            (20, "Yards"),
            indoor=True,
        )
        metric_target = Target(
            "10_zone",
            (80, "Centimetres"),
            (30, "Metres"),
        )

        assert imperial_target.native_distance.units == "yard"
        assert imperial_target.native_diameter.units == "inch"
        assert metric_target.native_distance.units == "metre"
        assert metric_target.native_diameter.units == "cm"

    def test_default_location(self) -> None:
        """Check that Target() returns indoor=False when indoor not specified."""
        target = Target("5_zone", 122, (50, "m"))
        assert target.indoor is False

    @pytest.mark.parametrize(
        "face_type,max_score_expected",
        [
            ("5_zone", 9),
            ("10_zone", 10),
            ("10_zone_compound", 10),
            ("10_zone_6_ring", 10),
            ("10_zone_5_ring", 10),
            ("10_zone_5_ring_compound", 10),
            ("11_zone", 11),
            ("11_zone_6_ring", 11),
            ("11_zone_5_ring", 11),
            ("WA_field", 6),
            ("IFAA_field", 5),
            ("IFAA_field_expert", 5),
            ("AA_national_field", 5),
            ("Worcester", 5),
            ("Worcester_2_ring", 5),
            ("Beiter_hit_miss", 1),
        ],
    )
    def test_max_score(
        self,
        face_type: ScoringSystem,
        max_score_expected: float,
    ) -> None:
        """Check that Target() returns correct max score."""
        target = Target(face_type, 122, (50, "metre"), False)
        assert target.max_score() == max_score_expected

    @pytest.mark.parametrize(
        "face_type,min_score_expected",
        [
            ("5_zone", 1),
            ("10_zone", 1),
            ("10_zone_compound", 1),
            ("10_zone_6_ring", 5),
            ("10_zone_5_ring", 6),
            ("10_zone_5_ring_compound", 6),
            ("11_zone", 1),
            ("11_zone_6_ring", 5),
            ("11_zone_5_ring", 6),
            ("WA_field", 1),
            ("IFAA_field", 3),
            ("IFAA_field_expert", 1),
            ("AA_national_field", 1),
            ("Worcester", 1),
            ("Worcester_2_ring", 4),
            ("Beiter_hit_miss", 1),
        ],
    )
    def test_min_score(
        self,
        face_type: ScoringSystem,
        min_score_expected: float,
    ) -> None:
        """Check that Target() returns correct min score."""
        target = Target(face_type, 122, 50, False)
        assert target.min_score() == min_score_expected

    @pytest.mark.parametrize(
        "scoring_system, diam, expected_spec",
        [
            (
                "5_zone",
                122,
                {
                    0.244: 9,
                    0.488: 7,
                    0.732: 5,
                    0.976: 3,
                    1.22: 1,
                },
            ),
            (
                "10_zone",
                80,
                {
                    0.08: 10,
                    0.16: 9,
                    0.24: 8,
                    0.32: 7,
                    0.4: 6,
                    0.48: 5,
                    0.56: 4,
                    0.64: 3,
                    0.72: 2,
                    0.8: 1,
                },
            ),
            (
                "11_zone",
                40,
                {
                    0.02: 11,
                    0.04: 10,
                    0.08: 9,
                    0.12: 8,
                    0.16: 7,
                    0.20: 6,
                    0.24: 5,
                    0.28: 4,
                    0.32: 3,
                    0.36: 2,
                    0.40: 1,
                },
            ),
            (
                "11_zone_6_ring",
                40,
                {
                    0.02: 11,
                    0.04: 10,
                    0.08: 9,
                    0.12: 8,
                    0.16: 7,
                    0.20: 6,
                    0.24: 5,
                },
            ),
            (
                "WA_field",
                80,
                {
                    0.08: 6,
                    0.16: 5,
                    0.32: 4,
                    0.48: 3,
                    0.64: 2,
                    0.8: 1,
                },
            ),
            (
                "IFAA_field",
                50,
                {
                    0.1: 5,
                    0.3: 4,
                    0.5: 3,
                },
            ),
            (
                "AA_national_field",
                20,
                {
                    0.04: 5,
                    0.08: 4,
                    0.12: 3,
                    0.16: 2,
                    0.2: 1,
                },
            ),
            (
                "Beiter_hit_miss",
                6,
                {
                    0.06: 1,
                },
            ),
            (
                "Worcester",
                (16, "inch"),
                {
                    0.08128: 5,
                    0.16256: 4,
                    0.24384: 3,
                    0.32512: 2,
                    0.4064: 1,
                },
            ),
            (
                "10_zone_6_ring",
                80,
                {
                    0.08: 10,
                    0.16: 9,
                    0.24: 8,
                    0.32: 7,
                    0.4: 6,
                    0.48: 5,
                },
            ),
            (
                "10_zone_5_ring_compound",
                40,
                {0.02: 10, 0.08: 9, 0.12: 8, 0.16: 7, 0.2: 6},
            ),
        ],
    )
    def test_face_spec(self, scoring_system, diam, expected_spec) -> None:
        """Check that target returns face specs from supported scoring systems."""
        target = Target(scoring_system, diam, 30)
        assert target.face_spec == expected_spec

    def test_face_spec_wrong_constructor(self) -> None:
        """
        Accessing face spec raises an error for custom target from standard init.

        Custom targets should be made using the `from_face_spec` classmethod
        """
        target = Target("Custom", 122, 50)
        with pytest.raises(
            ValueError,
            match=(
                "Trying to generate face spec for custom target "
                "but no existing spec found"
            ),
        ):
            assert target.face_spec

    def test_gen_face_spec_unsupported_system(self) -> None:
        """Check that generating face spec for an unsupported system raises error."""
        with pytest.raises(
            ValueError,
            match=r"Scoring system '(.+)' is not supported",
        ):
            # Silence mypy as using known invalid scoring system for test
            assert Target.gen_face_spec("Dartchery", 100)  # type: ignore[arg-type]


class TestCustomScoringTarget:
    """Tests for Target class with custom scoring."""

    _11zone_spec: Final = {0.02: 11, 0.04: 10, 0.8: 9, 0.12: 8, 0.16: 7, 0.2: 6}

    def test_constructor(self) -> None:
        """Check initialisation of Target with a custom scoring system and spec."""
        target = Target.from_face_spec({0.1: 3, 0.5: 1}, 80, (50, "yard"))
        assert target.distance == pytest.approx(50.0 * 0.9144)
        assert target.diameter == 0.8
        assert target.scoring_system == "Custom"
        assert target.face_spec == {0.1: 3, 0.5: 1}

    def test_face_spec_units(self) -> None:
        """Check custom Target can be constructed with alternative units."""
        target = Target.from_face_spec(({10: 5, 20: 4, 30: 3}, "cm"), 50, 30)
        assert target.face_spec == {0.1: 5, 0.2: 4, 0.3: 3}

    def test_invalid_face_spec_units(self) -> None:
        """Check custom Target cannot be constructed with unsupported units."""
        with pytest.raises(ValueError):
            Target.from_face_spec(({10: 5, 20: 4, 30: 3}, "bananas"), 50, 30)

    @pytest.mark.parametrize(
        "spec, args, result",
        [
            pytest.param(
                {0.2: 2, 0.4: 1},
                (40, 20, True),
                True,
                id="duplicate",
            ),
            pytest.param(
                {0.4: 5},
                (40, 20, True),
                False,
                id="different_spec",
            ),
        ],
    )
    def test_equality(self, spec, args, result) -> None:
        """Check custom Target equality comparison is supported."""
        target = Target.from_face_spec({0.2: 2, 0.4: 1}, 40, 20, indoor=True)
        comparison = target == Target.from_face_spec(spec, *args)
        assert comparison == result

    def test_max_score(self) -> None:
        """Check that Target with custom scoring system returns correct max score."""
        target = Target.from_face_spec(self._11zone_spec, 40, 18)
        assert target.max_score() == 11

    def test_min_score(self) -> None:
        """Check that Target with custom scoring system returns correct min score."""
        target = Target.from_face_spec(self._11zone_spec, 40, 18)
        assert target.min_score() == 6
