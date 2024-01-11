"""Tests for Pass and Round classes"""
from typing import Union, Tuple
import pytest

from archeryutils.rounds import Pass, Round


class TestPass:
    """
    Class to test the Pass class.

    Methods
    -------
    test_default_distance_unit()
        test behaviour of default distance unit
    test_default_location()
        test behaviour of default location
    test_negative_arrows()
        test behaviour of negative arrow number
    test_properties()
        test setting of Pass properties
    test_max_score()
        test max score functionality of Pass
    """

    def test_default_distance_unit(self) -> None:
        """
        Check that Pass() returns distance in metres when units not specified.
        """
        test_pass = Pass(36, 122, "5_zone", 50)
        assert test_pass.native_dist_unit == "metre"

    def test_default_diameter_unit(self) -> None:
        """
        Check that Pass() has same default diameter units as Target.
        """
        test_pass = Pass(36, 122, "5_zone", 50)
        assert test_pass.native_diam_unit == test_pass.target.native_diameter_unit == "cm"

    def test_diameter_units_passed_to_target(self) -> None:
        """
        Check that Pass() passes on diameter units to Target object.
        """
        test_pass = Pass(60, 16, "Worcester", 20, dist_unit="yards", diam_unit="inches")
        assert test_pass.target.native_diameter_unit == "inch"

    def test_default_location(self) -> None:
        """
        Check that Pass() returns indoor=False when indoor not specified.
        """
        test_pass = Pass(36, 122, "5_zone", 50, "metre")
        assert test_pass.indoor is False

    def test_negative_arrows(self) -> None:
        """
        Check that Pass() uses abs(narrows).
        """
        test_pass = Pass(-36, 122, "5_zone", 50, "metre")
        assert test_pass.n_arrows == 36

    def test_properties(self) -> None:
        """
        Check that Pass properties are set correctly
        """
        test_pass = Pass(36, 122, "5_zone", 50, "metre", False, "cm")
        assert test_pass.distance == 50.0
        assert test_pass.native_dist_unit == "metre"
        assert test_pass.diameter == 1.22
        assert test_pass.scoring_system == "5_zone"
        assert test_pass.indoor is False
        assert test_pass.native_diam_unit == "cm"

    @pytest.mark.parametrize(
        "face_type,max_score_expected",
        [
            ("5_zone", 900),
            ("10_zone", 1000),
            ("WA_field", 600),
            ("IFAA_field", 500),
            ("Worcester_2_ring", 500),
            ("Beiter_hit_miss", 100),
        ],
    )
    def test_max_score(
        self,
        face_type: str,
        max_score_expected: float,
    ) -> None:
        """
        Check that Pass.max_score() method is functioning correctly
        """
        test_pass = Pass(100, 122, face_type, 50, "metre", False)
        assert test_pass.max_score() == max_score_expected


class TestRound:
    """
    Class to test the Round class.

    Methods
    -------
    def test_max_score()
        test max score functionality of Round
    def test_max_distance()
        test max distance functionality of Round
    test_max_distance_out_of_order()
        test max distance functionality of Round with unsorted Passes
    def test_get_info()
        test get_info functionality of Round
    """

    def test_max_score(self) -> None:
        """
        Check that max score is calculated correctly for a Round
        """

        test_round = Round(
            "MyRound",
            [
                Pass(100, 122, "5_zone", 50, "metre", False),
                Pass(100, 122, "5_zone", 40, "metre", False),
                Pass(100, 122, "5_zone", 30, "metre", False),
            ],
        )
        assert test_round.max_score() == 2700

    @pytest.mark.parametrize(
        "unit,get_unit,max_dist_expected",
        [
            ("metres", True, (100, "metre")),
            ("yards", True, (100, "yard")),
            ("metres", False, 100),
            ("yards", False, 100),
        ],
    )
    def test_max_distance(
        self,
        unit: str,
        get_unit: bool,
        max_dist_expected: Union[float, Tuple[float, str]],
    ) -> None:
        """
        Check that max distance is calculated correctly for a Round.

        Returns a tuple or float depending on input argument.
        Always returns the distance in appropriate units regardless of whether unit
        requested or not - i.e. should not convert yards to metres.
        """

        test_round = Round(
            "MyRound",
            [
                Pass(10, 122, "5_zone", 100, unit, False),
                Pass(10, 122, "5_zone", 80, unit, False),
                Pass(10, 122, "5_zone", 60, unit, False),
            ],
        )
        assert test_round.max_distance(unit=get_unit) == max_dist_expected

    def test_max_distance_out_of_order(self) -> None:
        """
        Check max distance correct for Round where Passes not in descending dist order.
        """

        test_round = Round(
            "MyRound",
            [
                Pass(10, 122, "5_zone", 80, "metre", False),
                Pass(10, 122, "5_zone", 100, "metre", False),
                Pass(10, 122, "5_zone", 60, "metre", False),
            ],
        )
        assert test_round.max_distance() == 100

    def test_max_distance_mixed_units(self) -> None:
        """
        Check that max distance accounts for different units in round
        """
        pyards = Pass(36, 122, "5_zone", 80, 'yard')
        pmetric = Pass(36, 122, "5_zone", 75, 'metres')
        test_round = Round('test', [pyards, pmetric])

        assert pmetric.distance > pyards.distance
        assert test_round.max_distance() == 75

    def test_get_info(self, capsys: pytest.CaptureFixture[str]) -> None:
        """
        Check printing info works as expected.
        """
        test_round = Round(
            "MyRound",
            [
                Pass(10, 122, "5_zone", 100, "metre", False),
                Pass(20, 122, "5_zone", 80, "yards", False),
                Pass(30, 80, "5_zone", 60, "metre", False),
            ],
        )
        test_round.get_info()
        captured = capsys.readouterr()
        assert captured.out == (
            "A MyRound consists of 3 passes:\n"
            + "\t- 10 arrows at a 122.0 cm target at 100.0 metres.\n"
            + "\t- 20 arrows at a 122.0 cm target at 80.0 yards.\n"
            + "\t- 30 arrows at a 80.0 cm target at 60.0 metres.\n"
        )
