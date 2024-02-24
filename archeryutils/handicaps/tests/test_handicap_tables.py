"""Tests for handicap table code."""

import numpy as np
import pytest
from numpy.typing import NDArray

import archeryutils.handicaps.handicap_tables as hc
from archeryutils.rounds import Pass, Round

# Define rounds used in these functions
# Due to defining some rounds to use in testing duplicate code may trigger.
# => disable for handicap tests
# pylint: disable=duplicate-code
york = Round(
    "York",
    [
        Pass.at_target(72, "5_zone", 122, (100, "yard"), False),
        Pass.at_target(48, "5_zone", 122, (80, "yard"), False),
        Pass.at_target(24, "5_zone", 122, (60, "yard"), False),
    ],
)
hereford = Round(
    "Hereford",
    [
        Pass.at_target(72, "5_zone", 122, (80, "yard"), False),
        Pass.at_target(48, "5_zone", 122, (60, "yard"), False),
        Pass.at_target(24, "5_zone", 122, (50, "yard"), False),
    ],
)
metric122_30 = Round(
    "Metric 122-30",
    [
        Pass.at_target(36, "10_zone", 122, 30, False),
        Pass.at_target(36, "10_zone", 122, 30, False),
    ],
)
roundlist = [york, hereford, metric122_30]


class TestHandicapTable:
    """Class to test the handicap table functionalities of handicap_functions.

    Methods
    -------
    test_format_row
    test_table_as_str
    test_print_agb
    test_print_aa
    test_check_print_table_inputs_invalid_rounds
    test_check_print_table_inputs_invalid_handicaps

    """

    def test_repr(self) -> None:
        """Check HandicapTable representation."""
        test_table = hc.HandicapTable(
            "AGB", np.array([1.0, 2.0, 3.0]), [york, hereford]
        )
        expected = "<HandicapTable: 'AGB'>"
        assert repr(test_table) == expected

    @pytest.mark.parametrize(
        "hcs,int_prec,rounded,expected",
        [
            (
                # Check int_prec true
                np.array([1, 2, 3]),
                True,
                True,
                "      Handicap          York      Hereford\n"
                + "             1          1281              \n"
                + "             2          1279          1294\n"
                + "             3          1276          1293",
            ),
            (
                # Check int_prec false and rounded true (forces int_prec true)
                np.array([1, 2, 3]),
                False,
                True,
                "      Handicap          York      Hereford\n"
                + "             1          1281              \n"
                + "             2          1279          1294\n"
                + "             3          1276          1293",
            ),
            (
                # Check int_prec false and rounded false
                np.array([1, 2, 3]),
                False,
                False,
                "      Handicap          York      Hereford\n"
                + "             1 1280.95163666 1293.85033513\n"
                + "             2 1278.16257099 1293.14707366\n"
                + "             3 1275.05905507 1292.28105576",
            ),
            (
                # Check handicap float integers are converted to ints
                np.array([1.0, 2.0, 3.0]),
                True,
                True,
                "      Handicap          York      Hereford\n"
                + "             1          1281              \n"
                + "             2          1279          1294\n"
                + "             3          1276          1293",
            ),
            (
                # Check handicap dp are allocated OK
                np.array([1.20, 2.0, 3.0]),
                True,
                True,
                "      Handicap          York      Hereford\n"
                + "           1.2          1281              \n"
                + "           2.0          1279          1294\n"
                + "           3.0          1276          1293",
            ),
        ],
    )
    def test_table_as_str(
        self,
        hcs: NDArray[np.float_],
        int_prec: bool,
        rounded: bool,
        expected: str,
    ) -> None:
        """Check that format_row returns expected results for float and int."""
        test_table = hc.HandicapTable(
            "AGB", hcs, [york, hereford], int_prec=int_prec, rounded_scores=rounded
        )

        assert str(test_table) == expected

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
        """Check that abbreviate returns expected results."""
        # Accessing a protected member function, but for testing, not production code
        # pylint: disable=protected-access
        assert hc.HandicapTable._abbreviate(input_str) == expected

    def test_print_agb(
        self,
        capsys,
    ) -> None:
        """Check that inputs processed appropriately."""
        expected_out = (
            "      Handicap          York      Hereford\n"
            + "             1          1281              \n"
            + "             2          1279          1294\n"
            + "             3          1276          1293\n"
        )
        test_table = hc.HandicapTable(
            "AGB", np.array([1.0, 2.0, 3.0]), [york, hereford]
        )
        test_table.print()
        captured = capsys.readouterr()
        assert captured.out == expected_out

    def test_print_aa(
        self,
        capsys,
    ) -> None:
        """Check that inputs processed appropriately."""
        expected_out = (
            "      Handicap          York      Hereford\n"
            + "             1            79           136\n"
            + "             2            83           142\n"
            + "             3            87           149\n"
        )
        test_table = hc.HandicapTable("AA", np.array([1.0, 2.0, 3.0]), [york, hereford])
        test_table.print()
        captured = capsys.readouterr()
        assert captured.out == expected_out

    def test_inputs_as_list(
        self,
        capsys,
    ) -> None:
        """Check that input handicaps as a list are processed appropriately."""
        expected_out = (
            "      Handicap          York      Hereford\n"
            + "             1          1281              \n"
            + "             2          1279          1294\n"
            + "             3          1276          1293\n"
        )
        test_table = hc.HandicapTable(
            "AGB", [1.0, 2.0, 3.0], [york, hereford]  # type: ignore
        )
        test_table.print()
        captured = capsys.readouterr()
        assert captured.out == expected_out

    def test_check_print_table_inputs_invalid_rounds(
        self,
    ) -> None:
        """Check that empty rounds list triggers error."""
        with pytest.raises(
            ValueError,
            match=("No rounds provided for handicap table."),
        ):
            hc.HandicapTable("AGB", 1.0, [])

    def test_check_print_table_inputs_invalid_handicaps(
        self,
    ) -> None:
        """Check that inappropriate handicaps triggers error."""
        with pytest.raises(
            TypeError,
            match=("Expected float or ndarray for hcs."),
        ):
            hc.HandicapTable("AGB", "a", [york, hereford])  # type: ignore


#     @pytest.mark.parametrize(
#         "input_table,int_prec,sys,expected",
#         [
#             (
#                 np.array([[0, 11, 12, 13], [1, 10, 12, 12]]),
#                 True,
#                 "AGB",
#                 np.array([[0, 11, -9999, 13], [1, 10, 12, 12]]),
#             ),
#             (
#                 np.array([[0, 13], [5, 12], [10, 12], [15, 11]]),
#                 True,
#                 "AGB",
#                 np.array([[0, 13], [5, -9999], [10, 12], [15, 11]]),
#             ),
#             (
#                 np.array([[4, 13], [3, 12], [2, 12], [1, 11]]),
#                 True,
#                 "AA",
#                 np.array([[4, 13], [3, 12], [2, -9999], [1, 11]]),
#             ),
#             (
#                 np.array([[0.0, 11.0, 12.0, 13.0], [1.0, 10.0, 12.0, 12.0]]),
#                 False,
#                 "AGB",
#                 np.array([[0.0, 11.0, np.nan, 13.0], [1.0, 10.0, 12.0, 12.0]]),
#             ),
#             (
#                 np.array([[0.0, 11.5, 12.5, 13.5], [1.0, 11.5, 12.0, 13.5]]),
#                 False,
#                 "AGB",
#                 np.array([[0.0, np.nan, 12.5, np.nan], [1.0, 11.5, 12.0, 13.5]]),
#             ),
#         ],
#     )
#     def test_clean_repeated(
#         self,
#         input_table: NDArray[Union[np.int_, np.float_]],
#         int_prec: bool,
#         sys: str,
#         expected: NDArray[Union[np.int_, np.float_]],
#     ) -> None:
#         """
#         Check that abbreviate returns expected results.
#         """
#         print(hc_func.clean_repeated(input_table, int_prec, sys))
#         np.testing.assert_allclose(
#             hc_func.clean_repeated(input_table, int_prec, sys), expected
#         )
