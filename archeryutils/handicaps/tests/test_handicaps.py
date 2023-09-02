"""Tests for handicap equations and functions"""
from typing import Tuple, List, Union
import numpy as np
from numpy.typing import NDArray
import pytest

import archeryutils.handicaps.handicap_equations as hc_eq
import archeryutils.handicaps.handicap_functions as hc_func
from archeryutils.targets import Target
from archeryutils.rounds import Round, Pass


hc_params = hc_eq.HcParams()

# Define rounds used in these functions
york = Round(
    "York",
    [
        Pass(72, 1.22, "5_zone", 100, "yard", False),
        Pass(48, 1.22, "5_zone", 80, "yard", False),
        Pass(24, 1.22, "5_zone", 60, "yard", False),
    ],
)
hereford = Round(
    "Hereford",
    [
        Pass(72, 1.22, "5_zone", 80, "yard", False),
        Pass(48, 1.22, "5_zone", 60, "yard", False),
        Pass(24, 1.22, "5_zone", 50, "yard", False),
    ],
)
western = Round(
    "Western",
    [
        Pass(48, 1.22, "5_zone", 60, "yard", False),
        Pass(48, 1.22, "5_zone", 50, "yard", False),
    ],
)
vegas300 = Round(
    "Vegas 300",
    [
        Pass(30, 0.4, "10_zone", 20, "yard", True),
    ],
)
wa1440_90 = Round(
    "WA1440 90m",
    [
        Pass(36, 1.22, "10_zone", 90, "metre", False),
        Pass(36, 1.22, "10_zone", 70, "metre", False),
        Pass(36, 0.8, "10_zone", 50, "metre", False),
        Pass(36, 0.8, "10_zone", 30, "metre", False),
    ],
)
wa1440_70 = Round(
    "WA1440 70m",
    [
        Pass(36, 1.22, "10_zone", 70, "metre", False),
        Pass(36, 1.22, "10_zone", 60, "metre", False),
        Pass(36, 0.8, "10_zone", 50, "metre", False),
        Pass(36, 0.8, "10_zone", 30, "metre", False),
    ],
)
wa720_70 = Round(
    "WA 720 70m",
    [
        Pass(36, 1.22, "10_zone", 70, "metre", False),
        Pass(36, 1.22, "10_zone", 70, "metre", False),
    ],
)
metric122_30 = Round(
    "Metric 122-30",
    [
        Pass(36, 1.22, "10_zone", 30, "metre", False),
        Pass(36, 1.22, "10_zone", 30, "metre", False),
    ],
)


class TestSigmaT:
    """
    Class to test the sigma_t() function of handicap_equations.

    Uses output of the code when run at a particular point in time and then
    'frozen' to make sure future developments do not introduce unexpected changes.
    Deliberate changes to the schemes may affect these values and require changes.

    Methods
    -------
    def test_invalid_system()
        test if invalid handicap system raises error
    test_float()
        test if expected sigma_t returned from float
    test_array()
        test if expected sigma_t returned from array of floats
    """

    def test_invalid_system(self) -> None:
        """
        Check that sigma_t() returns error value for invalid system.
        """
        with pytest.raises(
            ValueError,
            match=(
                "Invalid Handicap System specified.\n"
                + "Please select from 'AGB', 'AGBold', 'AA', or 'AA2'."
            ),
        ):
            hc_eq.sigma_t(
                handicap=10.0,
                hc_sys="InvalidSystem",
                dist=10.0,
                hc_dat=hc_params,
            )

    @pytest.mark.parametrize(
        "handicap,system,distance,theta_expected",
        # Check all systems, different distances, negative and large handicaps.
        [
            (25.46, "AGB", 100.0, 0.002125743),
            (25.46, "AGBold", 100.0, 0.002149455),
            (25.46, "AA", 100.0, 0.011349271),
            (25.46, "AA2", 100.0, 0.011011017),
            (-12.0, "AGB", 100.0, 0.000585929),
            (-12.0, "AGBold", 100.0, 0.000520552),
            (-12.0, "AA", 100.0, 0.031204851),
            (-12.0, "AA2", 100.0, 0.030274820),
            (200.0, "AGB", 10.0, 0.620202925),
            (200.0, "AGBold", 10.0, 134.960599745),
            (200.0, "AA", 10.0, 7.111717503e-05),
            (200.0, "AA2", 10.0, 7.110517486e-05),
        ],
    )
    def test_float(
        self,
        handicap: float,
        system: str,
        distance: float,
        theta_expected: float,
    ) -> None:
        """
        Check that sigma_t(handicap=float) returns expected value for a case.
        """
        theta = hc_eq.sigma_t(
            handicap=handicap,
            hc_sys=system,
            dist=distance,
            hc_dat=hc_params,
        )

        assert theta == pytest.approx(theta_expected)

    def test_array(self) -> None:
        """
        Check that sigma_t(handicap=ndarray) returns expected value for a case.
        """
        handicap_array = np.array([25.46, -12.0, 200.0])
        theta_expected_array = np.array([0.002125743670, 0.0005859295368, 0.861389448])
        theta_array = hc_eq.sigma_t(
            handicap=handicap_array,
            hc_sys="AGB",
            dist=100.0,
            hc_dat=hc_params,
        )

        np.testing.assert_allclose(theta_array, theta_expected_array)


class TestSigmaR:
    """
    Class to test the sigma_r() function of handicap_equations.

    Uses output of the code when run at a particular point in time and then
    'frozen' to make sure future developments do not introduce unexpected changes.
    Deliberate changes to the schemes may affect these values and require changes.

    Methods
    -------
    def test_invalid_system()
        test if invalid handicap system raises error
    test_float()
        test if expected sigma_r returned for from float
    test_array()
        test if expected sigma_r returned for from array of floats
    """

    def test_invalid_system(self) -> None:
        """
        Check that sigma_r() returns error value for invalid system.
        """
        with pytest.raises(
            ValueError,
            match=(
                "Invalid Handicap System specified.\n"
                + "Please select from 'AGB', 'AGBold', 'AA', or 'AA2'."
            ),
        ):
            hc_eq.sigma_r(
                handicap=10.0,
                hc_sys="InvalisHandicapSystem",
                dist=10.0,
                hc_dat=hc_params,
            )

    @pytest.mark.parametrize(
        "handicap,system,distance,sigma_r_expected",
        # Check all systems, different distances, negative and large handicaps.
        [
            (25.46, "AGB", 100.0, 0.212574367),
            (25.46, "AGBold", 100.0, 0.214945543),
            (25.46, "AA", 100.0, 1.134927187),
            (25.46, "AA2", 100.0, 1.101101752),
            (-12.0, "AGB", 56.54, 0.028268938),
            (-12.0, "AGBold", 56.54, 0.029263504),
            (-12.0, "AA", 56.54, 1.482791802),
            (-12.0, "AA2", 56.54, 1.479459074),
            (200.0, "AGB", 10.0, 6.202029252),
            (200.0, "AGBold", 10.0, 1349.605997454),
            (200.0, "AA", 10.0, 0.0007111717503),
            (200.0, "AA2", 10.0, 0.0007110517486),
        ],
    )
    def test_float(
        self,
        handicap: float,
        system: str,
        distance: float,
        sigma_r_expected: float,
    ) -> None:
        """
        Check that sigma_r(handicap=float) returns expected value for a case.
        """
        sigma_r = hc_eq.sigma_r(
            handicap=handicap,
            hc_sys=system,
            dist=distance,
            hc_dat=hc_params,
        )

        assert sigma_r == pytest.approx(sigma_r_expected)

    def test_array(self) -> None:
        """
        Check that sigma_r(handicap=ndarray) returns expected value for a case.
        """
        handicap_array = np.array([25.46, -12.0, 200.0])
        sigma_r_expected_array = np.array([0.2125743670, 0.05859295, 86.1389448])
        sigma_r_array = hc_eq.sigma_r(
            handicap=handicap_array,
            hc_sys="AGB",
            dist=100.0,
            hc_dat=hc_params,
        )

        np.testing.assert_allclose(sigma_r_array, sigma_r_expected_array)


class TestArrowScore:
    """
    Class to test the arrow_score() function of handicap_equations.

    Tests all of the different types of target faces.
    Uses output of the code when run at a particular point in time and then
    'frozen' to make sure future developments do not introduce unexpected changes.
    Deliberate changes to the schemes may affect these values and require changes.


    Methods
    -------
    test_invalid_scoring_system()
        test if invalid target raises error
    test_different_handicap_systems()
        test if expected score returned for different systems
    test_different_target_faces()
        test if expected score returned for different faces
    """

    def test_invalid_scoring_system(self) -> None:
        """
        Check that arrow_score() returns error value for invalid system.
        """
        with pytest.raises(
            ValueError,
            match="No rule for calculating scoring for face type (.+).",
        ):
            target = Target(122.0, "5_zone", 100.0)
            target.scoring_system = "InvalidScoringSystem"

            hc_eq.arrow_score(
                target=target,
                handicap=12.0,
                hc_sys="AGB",
                hc_dat=hc_params,
                arw_d=None,
            )

    @pytest.mark.parametrize(
        "hc_system,indoor,arrow_diameter,arrow_score_expected",
        [
            ("AGB", False, None, 9.134460979),
            ("AGB", True, None, 9.207981127),
            ("AGB", False, 7.2e-3, 9.167309048),
            ("AGBold", False, None, 8.983801507),
            ("AGBold", True, None, 8.983801507),
            ("AGBold", False, 5.5e-3, 8.952543551),
            ("AA", False, None, 1.825614895),
            ("AA", True, None, 1.901506952),
            ("AA", False, 7.2e-3, 1.864288808),
            ("AA2", False, None, 1.818143484),
            ("AA2", True, None, 1.893767531),
            ("AA2", False, 7.2e-3, 1.856680406),
        ],
    )
    def test_different_handicap_systems(
        self,
        hc_system: str,
        indoor: bool,
        arrow_diameter: float,
        arrow_score_expected: float,
    ) -> None:
        """
        Check arrow scores returned for different handicap systems and arrow diameters.

        """
        arrow_score = hc_eq.arrow_score(
            target=Target(0.40, "10_zone_5_ring_compound", 20.0, "metre", indoor),
            handicap=20.0,
            hc_sys=hc_system,
            hc_dat=hc_params,
            arw_d=arrow_diameter,
        )

        assert arrow_score == pytest.approx(arrow_score_expected)

    @pytest.mark.parametrize(
        "target_face,arrow_score_expected",
        [
            ("5_zone", 7.044047485),
            ("10_zone", 7.547210123),
            ("10_zone_compound", 7.481017199),
            ("10_zone_6_ring", 7.397557278),
            ("10_zone_5_ring", 7.059965360),
            ("10_zone_5_ring_compound", 6.993772436),
            ("WA_field", 4.807397627),
            ("IFAA_field", 4.265744101),
            ("IFAA_field_expert", 4.021942762),
            ("Beiter_hit_miss", 0.9998380401),
            ("Worcester", 4.021942762),
            ("Worcester_2_ring", 3.346414597),
        ],
    )
    def test_different_target_faces(
        self, target_face: str, arrow_score_expected: float
    ) -> None:
        """
        Check correct arrow scores returned for different target faces
        """
        arrow_score = hc_eq.arrow_score(
            target=Target(0.80, target_face, 50.0, "metre", False),
            handicap=38.0,
            hc_sys="AGB",
            hc_dat=hc_params,
            arw_d=None,
        )

        assert arrow_score == pytest.approx(arrow_score_expected)


class TestScoreForRound:
    """
    Class to test the score_for_round() function of handicap_equations.

    Uses output of the code when run at a particular point in time and then
    'frozen' to make sure future developments do not introduce unexpected changes.
    Deliberate changes to the schemes may affect these values and require changes.

    Methods
    -------
    test_float_round_score()
        test if round_score returns expected results
    test_rounded_round_score
        test if round_score returns expected results when rounding
    """

    @pytest.mark.parametrize(
        "hc_system,round_score_expected",
        [
            (
                "AGB",
                (
                    243.381870343,
                    [79.845655370, 76.647150342, 86.889064625],
                ),
            ),
            (
                "AGBold",
                (
                    242.769238469,
                    [80.595119295, 76.161067484, 86.013051689],
                ),
            ),
            (
                "AA",
                (
                    36.368977908,
                    [7.813903155, 6.287938401, 22.267136351],
                ),
            ),
            (
                "AA2",
                (
                    37.126051009,
                    [8.266044100, 6.465486423, 22.394520484],
                ),
            ),
        ],
    )
    def test_float_round_score(
        self, hc_system: str, round_score_expected: Tuple[float, List[float]]
    ) -> None:
        """
        Check appropriate expected round scores are returned not rounding.

        Note: Checks round score only, not the separate distance scores.
        """
        test_round = Round(
            "MyRound",
            [
                Pass(10, 1.22, "10_zone", 100, "metre", False),
                Pass(10, 0.80, "10_zone", 80, "metre", False),
                Pass(10, 1.22, "5_zone", 60, "metre", False),
            ],
        )

        assert hc_eq.score_for_round(
            test_round, 20.0, hc_system, hc_eq.HcParams(), None, False
        )[0] == pytest.approx(round_score_expected[0])

    @pytest.mark.parametrize(
        "hc_system,round_score_expected",
        [
            (
                "AGB",
                (244.0, [79.845655376, 76.647150342, 86.889064625]),
            ),
            (
                "AGBold",
                (243.0, [80.595119295, 76.161067484, 86.013051689]),
            ),
        ],
    )
    def test_rounded_round_score(
        self, hc_system: str, round_score_expected: Tuple[float, List[float]]
    ) -> None:
        """
        Check appropriate expected round scores are returned for rounding.

        Notes: Checks round score only, not the separate distance scores.
               AGBold differs to AGB in that it rounds rather than rounding up.
        """
        test_round = Round(
            "MyRound",
            [
                Pass(10, 1.22, "10_zone", 100, "metre", False),
                Pass(10, 0.80, "10_zone", 80, "metre", False),
                Pass(10, 1.22, "5_zone", 60, "metre", False),
            ],
        )

        assert (
            hc_eq.score_for_round(
                test_round, 20.0, hc_system, hc_eq.HcParams(), None, True
            )[0]
            == round_score_expected[0]
        )


class TestHandicapFromScore:
    """
    Class to test the handicap_from_score() function of handicap_functions.

    Test both float and integer values, and maximum score.
    Where possible try and perform comparisons using values taken from literature,
    not generated by this codebase.
    - For Archery GB old use the published handicap tables.
    - For Archery GB new use the published handicap tables or values from this code.
    - For Archery Australia use Archery Scorepad- [ ] Classifications
    - For Archery Australia 2 there are no published tables and issues exist with

    Methods
    -------
    test_score_over_max()
    test_score_of_zero()
    test_score_below_zero()
    test_maximum_score()
    test_int_precision()
    test_decimal()

    References
    ----------
    Archery GB Old
        Published handicap tables by David Lane
        http://www.oldbasingarchers.co.uk/wp-content/uploads/2019/01/2011-Handicap-Booklet-Complete.pdf
    Archery GB New
        Published tables for outdoor rounds
        https://archerygb.org/files/outdoor-handicap-tables-200123092252.pdf
    Archery Australia
        Archery Scorepad
        https://www.archeryscorepad.com/ratings.php
    Archery Australia 2
        Currently no easily available data
    """

    @pytest.mark.parametrize(
        "testround,hc_system,int_prec,handicap_expected",
        [
            (metric122_30, "AGB", True, 11),
            (metric122_30, "AA", True, 107),
            # (metric122_30, "AA2", True, 107),
            # ------------------------------
            (western, "AGB", False, 9.89),
            (western, "AGBold", True, 6),
            # ------------------------------
            (vegas300, "AGB", True, 3),
            (vegas300, "AA", False, 118.38),
            # (vegas300, "AA2", True, 119),
        ],
    )
    def test_get_max_score_handicap(
        self,
        testround: Round,
        hc_system: str,
        int_prec: bool,
        handicap_expected: float,
    ) -> None:
        """
        Check that get_max_score_handicap() returns expected handicap.
        """
        handicap = hc_func.get_max_score_handicap(
            testround,
            hc_system,
            hc_params,
            None,
            int_prec,
        )

        assert pytest.approx(handicap) == handicap_expected

    def test_score_over_max(self) -> None:
        """
        Check that handicap_from_score() returns error value for too large score.
        """
        with pytest.raises(
            ValueError,
            match=(
                "The score of (.+) provided is greater than"
                + " the maximum of (.+) for a (.+)."
            ),
        ):
            test_round = Round(
                "TestRound",
                [
                    Pass(10, 1.22, "10_zone", 50, "metre", False),
                    Pass(10, 0.80, "10_zone", 50, "metre", False),
                ],
            )

            hc_func.handicap_from_score(9999, test_round, "AGB", hc_params)

    def test_score_of_zero(self) -> None:
        """
        Check that handicap_from_score() returns error for zero score.
        """
        with pytest.raises(
            ValueError,
            match=(
                "The score of 0 provided is less than or equal to"
                + " zero so cannot have a handicap."
            ),
        ):
            test_round = Round(
                "TestRound",
                [
                    Pass(10, 1.22, "10_zone", 50, "metre", False),
                    Pass(10, 0.80, "10_zone", 50, "metre", False),
                ],
            )

            hc_func.handicap_from_score(0, test_round, "AGB", hc_params)

    def test_score_below_zero(self) -> None:
        """
        Check that handicap_from_score() returns error for negative score.
        """
        with pytest.raises(
            ValueError,
            match=(
                "The score of (.+) provided is less than or equal to"
                + " zero so cannot have a handicap."
            ),
        ):
            test_round = Round(
                "TestRound",
                [
                    Pass(10, 1.22, "10_zone", 50, "metre", False),
                    Pass(10, 0.80, "10_zone", 50, "metre", False),
                ],
            )

            hc_func.handicap_from_score(-9999, test_round, "AGB", hc_params)

    @pytest.mark.parametrize(
        "hc_system,testround,max_score,handicap_expected",
        [
            ("AGB", metric122_30, 720, 11),
            ("AA", metric122_30, 720, 107),
            # ("AA2", metric122_30, 720, 107),
            # ------------------------------
            ("AGB", western, 864, 9),
            ("AGBold", western, 864, 6),
            # ------------------------------
            ("AGB", vegas300, 300, 3),
            ("AA", vegas300, 300, 119),
            # ("AA2", vegas300, 300, 119),
        ],
    )
    def test_maximum_score(
        self,
        hc_system: str,
        testround: Round,
        max_score: float,
        handicap_expected: float,
    ) -> None:
        """
        Check correct handicap returned for max score.
        """

        handicap = hc_func.handicap_from_score(
            max_score,
            testround,
            hc_system,
            hc_params,
            None,
            True,
        )

        assert handicap == handicap_expected

    @pytest.mark.parametrize(
        "hc_system,testround,testscore,handicap_expected",
        [
            # ------------------------------
            # Generic scores:
            ("AGB", wa720_70, 700, 1),
            ("AGBold", wa720_70, 700, 1),
            ("AA", wa720_70, 700, 119),
            # ("AA2", wa720_70, 700, 107),
            ("AGB", wa720_70, 500, 44),
            ("AGBold", wa720_70, 500, 40),
            ("AA", wa720_70, 500, 64),
            # ("AA2", wa720_70, 500, 107),
            # ------------------------------
            # Score on the lower bound of a band:
            ("AGB", wa720_70, 283, 63),
            ("AGBold", wa720_70, 286, 53),
            ("AA", wa720_70, 280, 39),
            # ("AA2", wa720_70, 500, 107),
            # ------------------------------
            # Score on upper bound of a band:
            ("AGB", wa720_70, 486, 46),
            ("AGBold", wa720_70, 488, 41),
            ("AA", wa720_70, 491, 62),
            # ("AA2", wa720_70, 500, 107),
            # ------------------------------
            # Scores that give negative AGB handicaps:
            ("AGB", wa720_70, 710, -5),
            ("AGBold", wa720_70, 710, -5),
            # ("AA", wa720_70, 491, 62)
            # ("AA2", wa720_70, 500, 107),
            # ------------------------------
            # Scores that give 0 AA handicaps:
            ("AA", wa720_70, 52, 0),
            # ("AA2", wa720_70, 500, 107),
            # ------------------------------
            # Multiple Distance Round:
            ("AGB", wa1440_90, 850, 52),
            ("AGBold", wa1440_90, 850, 46),
            ("AA", wa1440_90, 850, 53),
            # ("AA2", wa1440_90, 850, 53),
        ],
    )
    def test_int_precision(
        self,
        hc_system: str,
        testround: Round,
        testscore: float,
        handicap_expected: float,
    ) -> None:
        """
        Check correct handicap returned for various scores.
        """
        handicap = hc_func.handicap_from_score(
            testscore,
            testround,
            hc_system,
            hc_params,
            None,
            True,
        )

        assert handicap == handicap_expected

    @pytest.mark.parametrize(
        "hc_system,testround,testscore,handicap_expected",
        [
            # Generic scores:
            ("AGB", wa720_70, 500, 43.474880980),
            ("AGBold", wa720_70, 500, 39.056931372),
            ("AA", wa720_70, 500, 64.197993398),
            # ("AA2", wa720_70, 500, 107),
            # ------------------------------
            # Multiple Distance Round:
            ("AGB", wa1440_90, 850, 51.775514610),
            ("AGBold", wa1440_90, 850, 45.303733163),
            ("AA", wa1440_90, 850, 53.545592683),
            # ("AA2", wa1440_90, 850, 53),
        ],
    )
    def test_decimal(
        self,
        hc_system: str,
        testround: Round,
        testscore: float,
        handicap_expected: float,
    ) -> None:
        """
        Check correct handicap returned for various scores.

        Uses output of the code when run at a particular point in time then
        'frozen' to monitor future developments introducing unexpected changes.
        Deliberate changes to the schemes may affect these values and require changes.

        """
        handicap = hc_func.handicap_from_score(
            testscore,
            testround,
            hc_system,
            hc_params,
            None,
            False,
        )

        assert handicap == pytest.approx(handicap_expected)


class TestHandicapTable:
    """
    Class to test the handicap table functionalities of handicap_functions.

    Methods
    -------

    References
    ----------
    """

    @pytest.mark.parametrize(
        "input_arr,int_prec,expected",
        [
            (
                np.array([1, 20.0, 23.0]),
                False,
                "    1.00000000   20.00000000   23.00000000",
            ),
            (
                np.array([1, 20.0, 23.0]),
                True,
                "             1            20            23",
            ),
        ],
    )
    def test_format_row(
        self,
        input_arr: NDArray[Union[np.int_, np.float_]],
        int_prec: bool,
        expected: str,
    ) -> None:
        """
        Check that format_row returns expected results for float and int.
        """
        assert hc_func.format_row(input_arr, int_prec) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("Compound", "C"),
            ("Recurve Triple Portsmouth", "R Tr Ports"),
            ("Recurve Triple Portsmouth", "R Tr Ports"),
            ("Short Gents Worcester", "St G Worc"),
        ],
    )
    def test_abbreviate(
        self,
        input_str: str,
        expected: str,
    ) -> None:
        """
        Check that abbreviate returns expected results.
        """
        assert hc_func.abbreviate(input_str) == expected

    @pytest.mark.parametrize(
        "input_table,int_prec,sys,expected",
        [
            (
                np.array([[0, 11, 12, 13], [1, 10, 12, 12]]),
                True,
                "AGB",
                np.array([[0, 11, -9999, 13], [1, 10, 12, 12]]),
            ),
            (
                np.array([[0, 13], [5, 12], [10, 12], [15, 11]]),
                True,
                "AGB",
                np.array([[0, 13], [5, -9999], [10, 12], [15, 11]]),
            ),
            (
                np.array([[4, 13], [3, 12], [2, 12], [1, 11]]),
                True,
                "AA",
                np.array([[4, 13], [3, 12], [2, -9999], [1, 11]]),
            ),
            (
                np.array([[0.0, 11.0, 12.0, 13.0], [1.0, 10.0, 12.0, 12.0]]),
                False,
                "AGB",
                np.array([[0.0, 11.0, np.nan, 13.0], [1.0, 10.0, 12.0, 12.0]]),
            ),
            (
                np.array([[0.0, 11.5, 12.5, 13.5], [1.0, 11.5, 12.0, 13.5]]),
                False,
                "AGB",
                np.array([[0.0, np.nan, 12.5, np.nan], [1.0, 11.5, 12.0, 13.5]]),
            ),
        ],
    )
    def test_clean_repeated(
        self,
        input_table: NDArray[Union[np.int_, np.float_]],
        int_prec: bool,
        sys: str,
        expected: NDArray[Union[np.int_, np.float_]],
    ) -> None:
        """
        Check that abbreviate returns expected results.
        """
        print(hc_func.clean_repeated(input_table, int_prec, sys))
        np.testing.assert_allclose(
            hc_func.clean_repeated(input_table, int_prec, sys), expected
        )
