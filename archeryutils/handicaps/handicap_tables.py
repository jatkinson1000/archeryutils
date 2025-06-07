"""
Code providing the HandicapTable class for generating and manipulating handicap tables.

Makes use of the basic handicap equations in .handicap_equations.

"""

import decimal
import warnings
from itertools import chain

import numpy as np
import numpy.typing as npt

import archeryutils.handicaps.handicap_functions as hc
from archeryutils import rounds

from .handicap_scheme import HandicapScheme

_FILL = -9999


class HandicapTable:
    r"""
    Class to generate and store a handicap table.

    Parameters
    ----------
    handicap_sys : str | HandicapScheme
        identifier for the handicap system to use
    hcs : ArrayLike
        handicap values to calculate scores for
    round_list : list[rounds.Round]
        list of Round classes to show in the handicap table
    rounded_scores : bool, default=True
        round scores to integer value?
    int_prec : bool, default=True
        display numbers in table as integers rather than decimals to improve appearance
    clean_gaps : bool, default=True
        clean out gaps of repeated scores (using only first occurrence)
        gaps will be filled with -9999 (int_prec=True) or np.nan (int_prec=False)
    arrow_d : float | None, default=None
        user-specified arrow diameter in [metres]


    Attributes
    ----------
    hc_sys : HandicapScheme
        HandicapScheme class to be used in constructing this table
    round_list : list[rounds.Round]
        list of Round classes to show in the handicap table
    rounded_scores : bool
        round scores to integer value?
    int_prec : bool
        display numbers in table as integers rather than decimals to improve appearance
    clean_gaps : bool
        clean out gaps of repeated scores (using only first occurrence)
    hcs : NDArray[np.float64]
        handicap values to calculate scores for
    table: NDArray[np.float64 | np.int\\_]
        the generated handicap table containing appropriate score values

    """

    def __init__(  # noqa: PLR0913 - Too many arguments
        self,
        handicap_sys: str | HandicapScheme,
        hcs: npt.ArrayLike,
        round_list: list[rounds.Round],
        rounded_scores: bool = True,
        int_prec: bool = True,
        clean_gaps: bool = True,
        arrow_d: float | None = None,
    ):
        self.hc_sys = hc.handicap_scheme(handicap_sys)
        self.round_list = round_list
        self.rounded_scores = rounded_scores
        self.int_prec = int_prec
        self.clean_gaps = clean_gaps

        # Sanitise inputs
        self.hcs: npt.NDArray[np.float64] = self._check_print_table_inputs(hcs)

        # Set up empty handicap table and populate
        self.table: npt.NDArray[np.float64 | np.int_] = np.empty(
            [len(self.hcs), len(self.round_list) + 1],
        )
        self.table[:, 0] = self.hcs[:]
        # Assign values to table
        for i, round_i in enumerate(round_list):
            self.table[:, i + 1] = self.hc_sys.score_for_round(
                self.hcs,
                round_i,
                arrow_d,
                rounded_score=self.rounded_scores,
            )

        # If rounding scores up don't want to display trailing zeros, so ensure int_prec
        if self.rounded_scores and not self.int_prec:
            warnings.warn(
                "Handicap Table incompatible options.\n"
                "Requesting scores to be rounded up but without integer precision.\n"
                "Setting integer precision (`int_prec`) as true.",
                UserWarning,
                stacklevel=2,
            )
            self.int_prec = True

        if self.int_prec:
            self.table[:, 1:] = self.table[:, 1:].astype(int)

        if self.clean_gaps:
            self._clean_repeated()
            self.hcs = self.hcs[1:-1]
            self.table = self.table[1:-1, :]

    def __repr__(self) -> str:
        """Return a representation of a HandicapTable instance."""
        return f"<HandicapTable: '{self.hc_sys.name}'>"

    def __str__(
        self,
    ) -> str:
        """
        Format the handicap table as a string.

        Returns
        -------
        output_str : str
            a string representation of the Handicap table for printing/saving

        """
        # To ensure both terminal and file output are the same, create a single string
        round_names = [self._abbreviate(r.name) for r in self.round_list]
        output_header = "".join(
            name.rjust(14) for name in chain(["Handicap"], round_names)
        )
        # Auto-set the number of decimal places to display handicaps to
        if np.max(self.hcs % 1.0) <= 0.0:
            hc_dp = 0
        else:
            hc_dp = np.max(
                np.abs([decimal.Decimal(str(d)).as_tuple().exponent for d in self.hcs]),
            )
        # Format each row appropriately
        output_rows = [
            self._format_row(np.asarray(row), hc_dp, self.int_prec)
            for row in self.table
        ]
        output_str = "\n".join(chain([output_header], output_rows))

        return output_str

    def print(self) -> None:
        """
        Print handicap table to screen/stdout.

        Examples
        --------
        >>> import archeryutils as au
        >>> wa_outdoor = au.load_rounds.WA_outdoor
        >>> from archeryutils import handicaps as hc
        >>> agb_table = hc.HandicapTable(
        ...     "AGB",
        ...     [1.0, 2.0, 3.0, 4.0, 5.0],
        ...     [wa_outdoor.wa1440_90, wa_outdoor.wa1440_70, wa_outdoor.wa1440_60],
        ... )
        >>> agb_table.print()
              Handicap WA 1440 (90m) WA 1440 (70m) WA 1440 (60m)
                     1          1396          1412          1427
                     2          1393          1409          1425
                     3          1389          1406          1423
                     4          1385          1403          1420
                     5          1380          1399          1418

        """
        print(self)

    def to_csv(
        self,
        csvfile: str,
    ) -> None:
        """
        Save handicap table as a csv file.

        Parameters
        ----------
        csvfile : str
            csv filepath to save to.

        Examples
        --------
        >>> import archeryutils as au
        >>> wa_outdoor = au.load_rounds.WA_outdoor
        >>> from archeryutils import handicaps as hc
        >>> agb_table = hc.HandicapTable(
        ...     "AGB",
        ...     [1.0, 2.0, 3.0, 4.0, 5.0],
        ...     [wa_outdoor.wa1440_90, wa_outdoor.wa1440_70, wa_outdoor.wa1440_60],
        ... )
        >>> agb_table.to_csv("mycsvfile.csv")
        Writing handicap table to csv...Done.

        """
        print("Writing handicap table to csv...", end="")
        roundlist_csv = (
            f"handicap, {','.join([round_i.name for round_i in self.round_list])}'"
        )
        np.savetxt(
            csvfile,
            self.table,
            delimiter=", ",
            header=roundlist_csv,
        )
        print("Done.")

    def to_file(self, filename: str) -> None:
        """
        Save handicap table to text file.

        Parameters
        ----------
        filename : str
            filepath to save table to.

        Examples
        --------
        >>> import archeryutils as au
        >>> wa_outdoor = au.load_rounds.WA_outdoor
        >>> from archeryutils import handicaps as hc
        >>> agb_table = hc.HandicapTable(
        ...     "AGB",
        ...     [1.0, 2.0, 3.0, 4.0, 5.0],
        ...     [wa_outdoor.wa1440_90, wa_outdoor.wa1440_70, wa_outdoor.wa1440_60],
        ... )
        >>> agb_table.to_file("mytextfile.txt")
        Writing handicap table to file...Done.

        """
        print("Writing handicap table to file...", end="")
        # Generate string to output to file or display
        with open(filename, "w", encoding="utf-8") as table_file:
            table_file.write(str(self))
        print("Done.")

    def _check_print_table_inputs(
        self,
        hcs_in: npt.ArrayLike,
    ) -> npt.NDArray[np.float64]:
        """
        Sanitise and format inputs to handicap printing code.

        Parameters
        ----------
        hcs_in : ArrayLike
            handicap value(s) to calculate score(s) for

        Returns
        -------
        hcs : NDArray[np.float64]
            handicaps prepared for use in table printing routines

        Raises
        ------
        TypeError
            If handicaps not provided as float or ndarray
        ValueError
            If no rounds are provided for the handicap table

        """
        try:
            hcs = np.asarray(hcs_in, dtype=np.float64)
        except ValueError as exc:
            msg = "Cannot convert supplied handicaps to float for HandicapTable."
            raise TypeError(msg) from exc

        if len(self.round_list) == 0:
            msg = "No rounds provided for handicap table."
            raise ValueError(msg)

        # if cleaning gaps add row to top/bottom of table to catch out of range repeats
        if self.clean_gaps:
            delta_s = hcs[1] - hcs[0] if len(hcs) > 1 else 1.0
            delta_e = hcs[-1] - hcs[-2] if len(hcs) > 1 else 1.0
            hcs = np.insert(hcs, 0, np.array([hcs[0] - delta_s]))
            hcs = np.append(hcs, [hcs[-1] + delta_e])

        return hcs

    def _clean_repeated(
        self,
    ) -> None:
        """Keep only the first instance of a score in the handicap tables."""
        # NB: This assumes scores are running highest to lowest.
        # :. Flip schemes with a descending scale (AA and AA2) tables before operating.
        if not self.hc_sys.desc_scale:
            self.table = np.flip(self.table, axis=0)

        for irow, row in enumerate(self.table[:-1, :]):
            for jscore in range(len(np.asarray(row))):
                if self.table[irow, jscore] == self.table[irow + 1, jscore]:
                    if self.int_prec:
                        self.table[irow, jscore] = _FILL
                    else:
                        self.table[irow, jscore] = np.nan

        # Undo the initial reversal if required
        if not self.hc_sys.desc_scale:
            self.table = np.flip(self.table, axis=0)

    @staticmethod
    def _abbreviate(name: str) -> str:
        """
        Generate headings using abbreviations to keep table output concise.

        Parameters
        ----------
        name : str
            full, long round name as appears currently

        Returns
        -------
        str
            abbreviated round name to replace with

        Warnings
        --------
        This function only works with names containing space-separated words.

        """
        abbreviations = {
            "Compound": "C",
            "Recurve": "R",
            "Triple": "Tr",
            "Centre": "C",
            "Portsmouth": "Ports",
            "Worcester": "Worc",
            "Short": "St",
            "Long": "Lg",
            "Small": "Sm",
            "Gents": "G",
            "Ladies": "L",
        }

        return " ".join(abbreviations.get(i, i) for i in name.split())

    @staticmethod
    def _format_row(
        row: npt.NDArray[np.float64 | np.int_],
        hc_dp: int = 0,
        int_prec: bool = False,
    ) -> str:
        """
        Fornat appearance of handicap table row to look nice.

        Parameters
        ----------
        row : NDArray[np.float64 | np.int_]
            numpy array of data for one table row
        hc_dp : int, default=0
            handicap decimal places
        int_prec : bool, default=False
            return integers, not floats?

        Returns
        -------
        str
            pretty string based on input array data
        """
        if hc_dp == 0:
            handicap_str = f"{int(row[0]):14d}"
        else:
            handicap_str = f"{row[0]:14.{hc_dp}f}"

        if int_prec:
            return handicap_str + "".join(
                "".rjust(14) if x == _FILL else f"{int(x):14d}" for x in row[1:]
            )
        return handicap_str + "".join(
            "".rjust(14) if np.isnan(x) else f"{x:14.8f}" for x in row[1:]
        )
