"""Tests for Target class"""
import pytest

from archeryutils.targets import Target


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

    def test_invalid_system(self) -> None:
        """
        Check that Target() returns error value for invalid system.
        """
        with pytest.raises(
            ValueError,
            match="Invalid Target Face Type specified.\nPlease select from '(.+)'.",
        ):
            Target(1.22, "InvalidScoringSystem", 50, "m", False)

    def test_invalid_distance_unit(self) -> None:
        """
        Check that Target() returns error value for invalid distance units.
        """
        with pytest.raises(
            ValueError,
            match="Distance unit '(.+)' not recognised. Select from 'yard' or 'metre'.",
        ):
            Target(1.22, "5_zone", 50, "InvalidDistanceUnit", False)

    def test_default_distance_unit(self) -> None:
        """
        Check that Target() returns distance in metres when units not specified.
        """
        target = Target(1.22, "5_zone", 50)
        assert target.native_dist_unit == "metre"

    def test_default_location(self) -> None:
        """
        Check that Target() returns indoor=False when indoor not specified.
        """
        target = Target(1.22, "5_zone", 50, "m")
        assert target.indoor is False

    def test_yard_to_m_conversion(self) -> None:
        """
        Check that Target() returns correct distance in metres when yards provided.
        """
        target = Target(1.22, "5_zone", 50, "yards")
        assert target.distance == 50.0 * 0.9144

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
    def test_max_score(self, face_type: str, max_score_expected: float) -> None:
        """
        Check that Target() returns correct max score.
        """
        target = Target(1.22, face_type, 50, "metre", False)
        assert target.max_score() == max_score_expected

    def test_max_score_invalid_face_type(self) -> None:
        """
        Check that Target() raises error for invalid face.
        """
        with pytest.raises(
            ValueError,
            match="Target face '(.+)' has no specified maximum score.",
        ):
            target = Target(1.22, "5_zone", 50, "metre", False)
            # Requires manual resetting of scoring system to get this error.
            target.scoring_system = "InvalidScoringSystem"
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
    def test_min_score(self, face_type: str, min_score_expected: float) -> None:
        """
        Check that Target() returns correct min score.
        """
        target = Target(1.22, face_type, 50, "metre", False)
        assert target.min_score() == min_score_expected

    def test_min_score_invalid_face_type(self) -> None:
        """
        Check that Target() raises error for invalid face.
        """
        with pytest.raises(
            ValueError,
            match="Target face '(.+)' has no specified minimum score.",
        ):
            target = Target(1.22, "5_zone", 50, "metre", False)
            # Requires manual resetting of scoring system to get this error.
            target.scoring_system = "InvalidScoringSystem"
            target.min_score()
