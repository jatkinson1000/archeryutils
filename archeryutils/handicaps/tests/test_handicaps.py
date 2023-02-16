import pytest
import numpy as np

import archeryutils.handicaps.handicap_equations as hc_eq


hc_params = hc_eq.HcParams()


class TestSigma_t:
    def test_AGB_float(self):
        # Check that sigma_t returns the value we expect it to for a single float value
        theta = hc_eq.sigma_t(
            handicap=25.46,
            hc_sys="AGB",
            dist=100.0,
            hc_dat=hc_params,
        )

        theta_expected = (
            hc_params.AGB_ang_0
            * ((1.0 + hc_params.AGB_step / 100.0) ** (25.46 + hc_params.AGB_datum))
            * np.exp(hc_params.AGB_kd * 100.0)
        )
        assert theta == theta_expected

    def test_AGB_array(self):
        # Check that sigma_t returns the value we expect it to for multiple floats
        handicap_array = np.array([25.46, 0.0, 243.9])
        theta = hc_eq.sigma_t(
            handicap=handicap_array,
            hc_sys="AGB",
            dist=100.0,
            hc_dat=hc_params,
        )

        theta_expected = (
            hc_params.AGB_ang_0
            * (
                (1.0 + hc_params.AGB_step / 100.0)
                ** (handicap_array + hc_params.AGB_datum)
            )
            * np.exp(hc_params.AGB_kd * 100.0)
        )
        assert (theta == theta_expected).all()


class TestSigma_r:
    def test_float(self):
        # Check that sigma_r returns the value we expect it to for a single float value
        sig_r = hc_eq.sigma_r(
            handicap=25.46,
            hc_sys="AGB",
            dist=100.0,
            hc_dat=hc_params,
        )

        sig_r_expected = 100.0 * hc_eq.sigma_t(
            handicap=25.46,
            hc_sys="AGB",
            dist=100.0,
            hc_dat=hc_params,
        )
        assert sig_r == sig_r_expected

    def test_array(self):
        # Check that sigma_r returns the value we expect it to for multiple floats
        handicap_array = np.array([25.46, 0.0, 243.9])
        sig_r = hc_eq.sigma_r(
            handicap=handicap_array,
            hc_sys="AGB",
            dist=100.0,
            hc_dat=hc_params,
        )

        sig_r_expected = 100.0 * hc_eq.sigma_t(
            handicap=handicap_array,
            hc_sys="AGB",
            dist=100.0,
            hc_dat=hc_params,
        )
        assert (sig_r == sig_r_expected).all()
