"""Tests for Target class"""

import pytest

from archeryutils.targets import Target, ScoringSystem


class TestTarget:
    """
    Class to test the Target class.

    Methods
    -------
    def test_invalid_system()
        test if invalid target face type system raises an error
    test_invalid_distance_unit()
        test if invalid distance unit raises an error
    """

    def test_repr(self) -> None:
        """
        Check Target string representation is as expected.
        """
        target = Target("10_zone", 80, 30)
        expected = "Target('10_zone', (80, 'cm'), (30, 'metre'), indoor=False)"
        assert repr(target) == expected

    def test_repr_native_units(self) -> None:
        """
        Check Target string representation returns values in native units.
        """
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
        """
        Check Target equality comparison is supported.
        """
        target = Target("10_zone", (40, "cm"), (20, "metre"), indoor=True)
        comparison = target == Target(*args)
        assert comparison == result

    def test_equality_different_object(self) -> None:
        """
        Check Target equality comparison against a differnt type of object.
        """
        target = Target("10_zone", 40, (20, "yard"), indoor=True)

        assert target != ("10_zone", 40, (20, "yard"), True)

    def test_invalid_system(self) -> None:
        """
        Check that Target() returns error value for invalid system.
        """
        with pytest.raises(
            ValueError,
            match="Invalid Target Face Type specified.\nPlease select from '(.+)'.",
        ):
            # Silence mypy as scoring_system must be a valid literal ScoringSystem
            Target("InvalidScoringSystem", 122, 50, False)  # type: ignore[arg-type]

    def test_invalid_distance_unit(self) -> None:
        """
        Check that Target() returns error value for invalid distance units.
        """
        with pytest.raises(
            ValueError,
            match="Distance unit '(.+)' not recognised. Select from 'yard' or 'metre'.",
        ):
            Target("5_zone", 122, (50, "InvalidDistanceUnit"), False)

    def test_default_distance_unit(self) -> None:
        """
        Check that Target() returns distance in metres when units not specified.
        """
        target = Target("5_zone", 122, 50)
        assert target.native_dist_unit == "metre"

    def test_yard_to_m_conversion(self) -> None:
        """
        Check that Target() returns correct distance in metres when yards provided.
        """
        target = Target("5_zone", 122, (50, "yards"))
        assert target.distance == 50.0 * 0.9144

    def test_unsupported_diameter_unit(self) -> None:
        """
        Check that Target() raises an error when called with unsupported diameter units.
        """
        with pytest.raises(
            ValueError,
            match="Diameter unit '(.+)' not recognised. Select from 'cm', 'inch' or 'metre'",
        ):
            Target("5_zone", (122, "feet"), (50, "yards"))

    def test_default_diameter_unit(self) -> None:
        """
        Check that Target() is using centimetres by default for diameter.
        """
        target = Target("10_zone_5_ring_compound", 80, 50)
        assert target.diameter == 80 * 0.01

    def test_diameter_metres_not_converted(self) -> None:
        """
        Check that Target() is storing diameter in metres.
        """
        target = Target("Beiter_hit_miss", (0.04, "m"), 18)
        assert target.diameter == 0.04

    def test_diameter_inches_supported(self) -> None:
        """
        Check that Target() converts diameters in inches correctly.
        """
        target = Target("Worcester", (16, "inches"), (20, "yards"), indoor=True)
        assert target.diameter == 16 * 0.0254

    def test_diameter_distance_units_coerced_to_definitive_names(self) -> None:
        """
        Check that Target coerces aliased distance units into standard names
        """

        imperial_target = Target(
            "Worcester", (16, "Inches"), (20, "Yards"), indoor=True
        )
        metric_target = Target(
            "10_zone",
            (80, "Centimetres"),
            (30, "Metres"),
        )

        assert imperial_target.native_dist_unit == "yard"
        assert imperial_target.native_diameter_unit == "inch"
        assert metric_target.native_dist_unit == "metre"
        assert metric_target.native_diameter_unit == "cm"

    def test_default_location(self) -> None:
        """
        Check that Target() returns indoor=False when indoor not specified.
        """
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
            ("WA_field", 6),
            ("IFAA_field", 5),
            ("IFAA_field_expert", 5),
            ("Worcester", 5),
            ("Worcester_2_ring", 5),
            ("Beiter_hit_miss", 1),
        ],
    )
    def test_max_score(
        self, face_type: ScoringSystem, max_score_expected: float
    ) -> None:
        """
        Check that Target() returns correct max score.
        """
        target = Target(face_type, 122, (50, "metre"), False)
        assert target.max_score() == max_score_expected

    def test_max_score_invalid_face_type(self) -> None:
        """
        Check that Target() raises error for invalid face.
        """
        with pytest.raises(
            ValueError,
            match="Target face '(.+)' has no specified maximum score.",
        ):
            target = Target("5_zone", 122, 50, False)
            # Requires manual resetting of scoring system to get this error.
            # Silence mypy as scoring_system must be a valid literal ScoringSystem
            target.scoring_system = "InvalidScoringSystem"  # type: ignore[assignment]
            target.max_score()

    @pytest.mark.parametrize(
        "face_type,min_score_expected",
        [
            ("5_zone", 1),
            ("10_zone", 1),
            ("10_zone_compound", 1),
            ("10_zone_6_ring", 5),
            ("10_zone_5_ring", 6),
            ("10_zone_5_ring_compound", 6),
            ("WA_field", 1),
            ("IFAA_field", 3),
            ("IFAA_field_expert", 1),
            ("Worcester", 1),
            ("Worcester_2_ring", 4),
            ("Beiter_hit_miss", 0),
        ],
    )
    def test_min_score(
        self, face_type: ScoringSystem, min_score_expected: float
    ) -> None:
        """
        Check that Target() returns correct min score.
        """
        target = Target(face_type, 122, 50, False)
        assert target.min_score() == min_score_expected

    def test_min_score_invalid_face_type(self) -> None:
        """
        Check that Target() raises error for invalid face.
        """
        with pytest.raises(
            ValueError,
            match="Target face '(.+)' has no specified minimum score.",
        ):
            target = Target("5_zone", 122, 50, False)
            # Requires manual resetting of scoring system to get this error.
            # Silence mypy as scoring_system must be a valid literal ScoringSystem
            target.scoring_system = "InvalidScoringSystem"  # type: ignore[assignment]
            target.min_score()
