"""Tests for handicap equations and functions"""
import numpy as np
import pytest

import archeryutils.handicaps.handicap_equations as hc_eq
from archeryutils.targets import Target
from archeryutils.rounds import Round, Pass


hc_params = hc_eq.HcParams()


class TestSigmaT:
    """
    Class to test the sigma_t() function of handicap_equations.

    Methods
    -------
    def test_invalid_system()
        test if invalid handicap system raises error
    test_float()
        test if expected sigma_t returned from float
    test_array()
        test if expected sigma_t returned from array of floats
    """

    def test_invalid_system(self):
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
                hc_sys=None,
                dist=10.0,
                hc_dat=hc_params,
            )

    @pytest.mark.parametrize(
        "handicap,system,distance,theta_expected",
        # Check all systems, different distances, negative and large handicaps.
        [
            (25.46, "AGB", 100.0, 0.002125743670979009),
            (25.46, "AGBold", 100.0, 0.002149455433015334),
            (25.46, "AA", 100.0, 0.011349271879457612),
            (25.46, "AA2", 100.0, 0.011011017526614786),
            (-12.0, "AGB", 100.0, 0.0005859295368818659),
            (-12.0, "AGBold", 100.0, 0.000520552194308095),
            (-12.0, "AA", 100.0, 0.03120485183570297),
            (-12.0, "AA2", 100.0, 0.03027482063411134),
            (200.0, "AGB", 10.0, 0.6202029252075888),
            (200.0, "AGBold", 10.0, 134.96059974543883),
            (200.0, "AA", 10.0, 7.111717503148246e-05),
            (200.0, "AA2", 10.0, 7.110517486764852e-05),
        ],
    )
    def test_float(self, handicap, system, distance, theta_expected):
        """
        Check that sigma_t(handicap=float) returns expected value for a case.
        """
        theta = hc_eq.sigma_t(
            handicap=handicap,
            hc_sys=system,
            dist=distance,
            hc_dat=hc_params,
        )

        assert theta == theta_expected

    def test_array(self):
        """
        Check that sigma_t(handicap=ndarray) returns expected value for a case.
        """
        handicap_array = np.array([25.46, -12.0, 200.0])
        dist_array = np.array([100.0, 100.0, 10.0])
        theta_expected_array = np.array(
            [0.002125743670979009, 0.0005859295368818659, 0.6202029252075888]
        )
        theta_array = hc_eq.sigma_t(
            handicap=handicap_array,
            hc_sys="AGB",
            dist=dist_array,
            hc_dat=hc_params,
        )

        assert (theta_array == theta_expected_array).all()


class TestSigmaR:
    """
    Class to test the sigma_r() function of handicap_equations.

    Methods
    -------
    def test_invalid_system()
        test if invalid handicap system raises error
    test_float()
        test if expected sigma_r returned for from float
    test_array()
        test if expected sigma_r returned for from array of floats
    """

    def test_invalid_system(self):
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
                hc_sys=None,
                dist=10.0,
                hc_dat=hc_params,
            )

    @pytest.mark.parametrize(
        "handicap,system,distance,sigma_r_expected",
        # Check all systems, different distances, negative and large handicaps.
        [
            (25.46, "AGB", 100.0, 0.21257436709790092),
            (25.46, "AGBold", 100.0, 0.2149455433015334),
            (25.46, "AA", 100.0, 1.1349271879457612),
            (25.46, "AA2", 100.0, 1.1011017526614786),
            (-12.0, "AGB", 56.54, 0.02826893819014717),
            (-12.0, "AGBold", 56.54, 0.029263504818409218),
            (-12.0, "AA", 56.54, 1.482791802020098),
            (-12.0, "AA2", 56.54, 1.4794590746458498),
            (200.0, "AGB", 10.0, 6.202029252075888),
            (200.0, "AGBold", 10.0, 1349.6059974543882),
            (200.0, "AA", 10.0, 0.0007111717503148246),
            (200.0, "AA2", 10.0, 0.0007110517486764853),
        ],
    )
    def test_float(self, handicap, system, distance, sigma_r_expected):
        """
        Check that sigma_r(handicap=float) returns expected value for a case.
        """
        sigma_r = hc_eq.sigma_r(
            handicap=handicap,
            hc_sys=system,
            dist=distance,
            hc_dat=hc_params,
        )

        assert sigma_r == sigma_r_expected

    def test_array(self):
        """
        Check that sigma_r(handicap=ndarray) returns expected value for a case.
        """
        handicap_array = np.array([25.46, -12.0, 200.0])
        dist_array = np.array([100.0, 56.54, 10.0])
        sigma_r_expected_array = np.array(
            [0.21257436709790092, 0.02826893819014717, 6.202029252075888]
        )
        sigma_r_array = hc_eq.sigma_r(
            handicap=handicap_array,
            hc_sys="AGB",
            dist=dist_array,
            hc_dat=hc_params,
        )

        assert (sigma_r_array == sigma_r_expected_array).all()


class TestArrowScore:
    """
    Class to test the arrow_score() function of handicap_equations.

    Tests all of the different types of target faces.

    Methods
    -------
    test_invalid_scoring_system()
        test if invalid target raises error
    test_different_handicap_systems()
        test if expected score returned for different systems
    test_different_target_faces()
        test if expected score returned for different faces
    """

    def test_invalid_scoring_system(self):
        """
        Check that arrow_score() returns error value for invalid system.
        """
        with pytest.raises(
            ValueError,
            match="No rule for calculating scoring for face type (.+).",
        ):
            target = Target(122.0, "5_zone", 100.0)
            target.scoring_system = None

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
            ("AGB", False, None, 9.134460979236048),
            ("AGB", True, None, 9.20798112770351),
            ("AGB", False, 7.2e-3, 9.167309048169756),
            ("AGBold", False, None, 8.983801507994793),
            ("AGBold", True, None, 8.983801507994793),
            ("AGBold", False, 5.5e-3, 8.95254355127178),
            ("AA", False, None, 1.8256148953722988),
            ("AA", True, None, 1.9015069522219408),
            ("AA", False, 7.2e-3, 1.8642888081318025),
            ("AA2", False, None, 1.818143484577794),
            ("AA2", True, None, 1.8937675318872254),
            ("AA2", False, 7.2e-3, 1.8566804060966389),
        ],
    )
    def test_different_handicap_systems(
        self, hc_system, indoor, arrow_diameter, arrow_score_expected
    ):
        """
        Check correct arrow scores returned for different handicap systems
        """
        arrow_score = hc_eq.arrow_score(
            target=Target(0.40, "10_zone_5_ring_compound", 20.0, "metre", indoor),
            handicap=20.0,
            hc_sys=hc_system,
            hc_dat=hc_params,
            arw_d=arrow_diameter,
        )

        assert arrow_score == arrow_score_expected

    @pytest.mark.parametrize(
        "target_face,arrow_score_expected",
        [
            ("5_zone", 7.044047485373609),
            ("10_zone", 7.5472101235522695),
            ("10_zone_compound", 7.481017199706876),
            ("10_zone_6_ring", 7.397557278755085),
            ("10_zone_5_ring", 7.059965360625537),
            ("10_zone_5_ring_compound", 6.9937724367801435),
            ("WA_field", 4.807397627133902),
            ("IFAA_field", 4.265744100115446),
            ("IFAA_field_expert", 4.0219427627782665),
            ("Beiter_hit_miss", 0.999838040182924),
            ("Worcester", 4.0219427627782665),
            ("Worcester_2_ring", 3.34641459746045),
        ],
    )
    def test_different_target_faces(self, target_face, arrow_score_expected):
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

        assert arrow_score == arrow_score_expected


class TestScoreForRound:
    """
    Class to test the score_for_round() function of handicap_equations.

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
                    243.38187034389472,
                    [79.84565537600997, 76.64715034267604, 86.88906462520869],
                ),
            ),
            (
                "AGBold",
                (
                    242.76923846935358,
                    [80.59511929560365, 76.16106748461186, 86.01305168913808],
                ),
            ),
            (
                "AA",
                (
                    36.36897790870545,
                    [7.8139031556465, 6.287938401968809, 22.267136351090144],
                ),
            ),
            (
                "AA2",
                (
                    37.12605100927616,
                    [8.266044100895407, 6.465486423674918, 22.394520484705836],
                ),
            ),
        ],
    )
    def test_float_round_score(self, hc_system, round_score_expected):
        """
        Check appropriate expected round scores are returned not rounding.
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
                test_round, 20.0, hc_system, hc_eq.HcParams(), None, False
            )
            == round_score_expected
        )

    @pytest.mark.parametrize(
        "hc_system,round_score_expected",
        [
            (
                "AGB",
                (244.0, [79.84565537600997, 76.64715034267604, 86.88906462520869]),
            ),
            (
                "AGBold",
                (243.0, [80.59511929560365, 76.16106748461186, 86.01305168913808]),
            ),
        ],
    )
    def test_rounded_round_score(self, hc_system, round_score_expected):
        """
        Check appropriate expected round scores are returned for rounding.

        NB AGBold differs to other schemes in that it rounds rather than rounding up.
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
            )
            == round_score_expected
        )
