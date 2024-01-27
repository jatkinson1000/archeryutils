"""Tests for handicap table printing"""

# Due to defining some rounds to use in testing duplicate code may trigger.
# => disable for handicap tests
# pylint: disable=duplicate-code

from typing import Union
import numpy as np
from numpy.typing import NDArray
import pytest

import archeryutils.handicaps.handicap_equations as hc_eq
import archeryutils.handicaps.handicap_functions as hc_func
from archeryutils.rounds import Pass, Round

hc_params = hc_eq.HcParams()

# Define rounds used in these functions
york = Round(
    "York",
    [
        Pass(72, "5_zone", 122, (100, "yard"), False),
        Pass(48, "5_zone", 122, (80, "yard"), False),
        Pass(24, "5_zone", 122, (60, "yard"), False),
    ],
)
hereford = Round(
    "Hereford",
    [
        Pass(72, "5_zone", 122, (80, "yard"), False),
        Pass(48, "5_zone", 122, (60, "yard"), False),
        Pass(24, "5_zone", 122, (50, "yard"), False),
    ],
)
metric122_30 = Round(
    "Metric 122-30",
    [
        Pass(36, "10_zone", 122, 30, False),
        Pass(36, "10_zone", 122, 30, False),
    ],
)


class TestHandicapTable:
    """
    Class to test the handicap table functionalities of handicap_functions.

    Methods
    -------

    References
    ----------
    """

    @pytest.mark.parametrize(
        "input_arr,hc_dp,int_prec,expected",
        [
            (
                np.array([1, 20.0, 23.0]),
                0,
                True,
                "             1            20            23",
            ),
            (
                np.array([1, 20.0, 23.0]),
                2,
                True,
                "          1.00            20            23",
            ),
            (
                np.array([1, 20.0, 23.0]),
                3,
                False,
                "         1.000   20.00000000   23.00000000",
            ),
        ],
    )
    def test_format_row(
        self,
        input_arr: NDArray[Union[np.int_, np.float_]],
        hc_dp: int,
        int_prec: bool,
        expected: str,
    ) -> None:
        """
        Check that format_row returns expected results for float and int.
        """
        assert hc_func.format_row(input_arr, hc_dp, int_prec) == expected

    @pytest.mark.parametrize(
        "hcs,table,int_prec,expected",
        [
            (
                # Check int_prec true
                np.array([1, 2, 3]),
                np.array([[1, 20.0, 23.0], [2, 20.0, 23.0], [3, 20.0, 23.0]]),
                True,
                "      Handicap          York      Hereford\n"
                + "             1            20            23\n"
                + "             2            20            23\n"
                + "             3            20            23",
            ),
            (
                # Check int_prec false
                np.array([1, 2, 3]),
                np.array([[1, 20.0, 23.0], [2, 20.0, 23.0], [3, 20.0, 23.0]]),
                False,
                "      Handicap          York      Hereford\n"
                + "             1   20.00000000   23.00000000\n"
                + "             2   20.00000000   23.00000000\n"
                + "             3   20.00000000   23.00000000",
            ),
            (
                # Check handicap float integers are converted to ints
                np.array([1.0, 2.0, 3.0]),
                np.array([[1.0, 20.0, 23.0], [2.0, 20.0, 23.0], [3.0, 20.0, 23.0]]),
                True,
                "      Handicap          York      Hereford\n"
                + "             1            20            23\n"
                + "             2            20            23\n"
                + "             3            20            23",
            ),
            (
                # Check handicap dp are allocated OK
                np.array([1.20, 2.0, 3.0]),
                np.array([[1.20, 20.0, 23.0], [2.0, 20.0, 23.0], [3.0, 20.0, 23.0]]),
                True,
                "      Handicap          York      Hereford\n"
                + "           1.2            20            23\n"
                + "           2.0            20            23\n"
                + "           3.0            20            23",
            ),
        ],
    )
    def test_table_as_str(
        self,
        hcs: NDArray[Union[np.int_, np.float_]],
        table: NDArray[Union[np.int_, np.float_]],
        int_prec: bool,
        expected: str,
    ) -> None:
        """
        Check that format_row returns expected results for float and int.
        """
        print(hc_func.table_as_str([york, hereford], hcs, table, int_prec))
        print(expected)
        assert hc_func.table_as_str([york, hereford], hcs, table, int_prec) == expected

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
        "hcs,clean_gaps,expected",
        [
            (
                # 'Correct' inputs
                np.array([1.0, 2.0, 3.0]),
                False,
                np.array([1.0, 2.0, 3.0]),
            ),
            (
                # List inputs
                [1.0, 2.0, 3.0],
                False,
                np.array([1.0, 2.0, 3.0]),
            ),
            (
                # Clean gaps True
                np.array([1.0, 2.0, 3.0]),
                True,
                np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
            ),
            (
                # Clean gaps True
                np.array([1.75, 2.0, 2.5]),
                True,
                np.array([1.5, 1.75, 2.0, 2.5, 3.0]),
            ),
            (
                # Single float
                1.0,
                False,
                np.array([1.0]),
            ),
            (
                # Single float clean gaps True
                1.5,
                True,
                np.array([0.5, 1.5, 2.5]),
            ),
        ],
    )
    def test_check_print_table_inputs(
        self,
        hcs: Union[float, NDArray[np.float_]],
        clean_gaps: bool,
        expected: Union[float, NDArray[np.float_]],
    ) -> None:
        """
        Check that inputs processed appropriately.
        """
        np.testing.assert_allclose(
            hc_func.check_print_table_inputs(hcs, [york, metric122_30], clean_gaps),
            expected,
        )

    def test_check_print_table_inputs_invalid_rounds(
        self,
    ) -> None:
        """
        Check that empty rounds list triggers error.
        """
        with pytest.raises(
            ValueError,
            match=("No rounds provided for handicap table."),
        ):
            hc_func.check_print_table_inputs(1.0, [], True)

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
