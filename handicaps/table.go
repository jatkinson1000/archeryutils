package handicaps

import (
	"encoding/csv"
	"fmt"
	"io"
	"math"
	"os"
	"strings"

	"github.com/retbrown/archeryutils/rounds"
)

const fillInt = -9999

// HandicapTable generates and stores a handicap table.
type HandicapTable struct {
	Scheme        Scheme
	Handicaps     []float64
	RoundList     []*rounds.Round
	RoundedScores bool
	IntPrec       bool
	CleanGaps     bool
	// table[row][col]: col 0 = handicap, col 1+ = round scores
	// NaN (float) or fillInt (int) marks a cleaned repeated score
	tableF [][]float64 // float view
	tableI [][]int     // int view (when IntPrec)
}

// NewHandicapTable builds a HandicapTable.
// handicaps is a slice of handicap values; arwD ≤ 0 means use scheme default.
func NewHandicapTable(
	s Scheme,
	handicaps []float64,
	roundList []*rounds.Round,
	roundedScores, intPrec, cleanGaps bool,
	arwD float64,
) (*HandicapTable, error) {
	if len(roundList) == 0 {
		return nil, fmt.Errorf("no rounds provided for handicap table")
	}
	if len(handicaps) == 0 {
		return nil, fmt.Errorf("no handicaps provided for handicap table")
	}

	// Force intPrec when rounding scores (to avoid trailing .0 display)
	if roundedScores && !intPrec {
		intPrec = true
	}

	// Extend handicap slice by one step at each end when cleaning gaps
	hcs := make([]float64, len(handicaps))
	copy(hcs, handicaps)
	if cleanGaps && len(hcs) > 1 {
		delta0 := hcs[1] - hcs[0]
		deltaE := hcs[len(hcs)-1] - hcs[len(hcs)-2]
		extended := make([]float64, 0, len(hcs)+2)
		extended = append(extended, hcs[0]-delta0)
		extended = append(extended, hcs...)
		extended = append(extended, hcs[len(hcs)-1]+deltaE)
		hcs = extended
	}

	// Build raw float table [row][col]
	nrows := len(hcs)
	ncols := len(roundList) + 1
	tableF := make([][]float64, nrows)
	for r := range tableF {
		tableF[r] = make([]float64, ncols)
		tableF[r][0] = hcs[r]
	}
	for ci, rnd := range roundList {
		for ri, h := range hcs {
			tableF[ri][ci+1] = ScoreForRound(s, h, rnd, arwD, roundedScores)
		}
	}

	// Convert to int if required
	var tableI [][]int
	if intPrec {
		tableI = make([][]int, nrows)
		for r := range tableI {
			tableI[r] = make([]int, ncols)
			for c := range tableI[r] {
				if c == 0 {
					tableI[r][0] = int(math.Round(tableF[r][0]))
				} else {
					tableI[r][c] = int(tableF[r][c])
				}
			}
		}
	}

	ht := &HandicapTable{
		Scheme:        s,
		Handicaps:     hcs,
		RoundList:     roundList,
		RoundedScores: roundedScores,
		IntPrec:       intPrec,
		CleanGaps:     cleanGaps,
		tableF:        tableF,
		tableI:        tableI,
	}

	if cleanGaps {
		ht.cleanRepeated()
		// Trim sentinel rows
		if len(hcs) > 2 {
			ht.Handicaps = ht.Handicaps[1 : len(ht.Handicaps)-1]
			ht.tableF = ht.tableF[1 : len(ht.tableF)-1]
			if intPrec {
				ht.tableI = ht.tableI[1 : len(ht.tableI)-1]
			}
		}
	}

	return ht, nil
}

// cleanRepeated replaces repeated scores with sentinel values.
func (ht *HandicapTable) cleanRepeated() {
	n := len(ht.tableF)
	ncols := len(ht.RoundList) + 1

	flip := !ht.Scheme.Descending()
	if flip {
		reverseRows(ht.tableF)
		if ht.IntPrec {
			reverseRows2I(ht.tableI)
		}
	}

	for r := 0; r < n-1; r++ {
		for c := 1; c < ncols; c++ {
			if ht.tableF[r][c] == ht.tableF[r+1][c] {
				if ht.IntPrec {
					ht.tableI[r][c] = fillInt
				}
				ht.tableF[r][c] = math.NaN()
			}
		}
	}

	if flip {
		reverseRows(ht.tableF)
		if ht.IntPrec {
			reverseRows2I(ht.tableI)
		}
	}
}

func reverseRows(t [][]float64) {
	for i, j := 0, len(t)-1; i < j; i, j = i+1, j-1 {
		t[i], t[j] = t[j], t[i]
	}
}

func reverseRows2I(t [][]int) {
	for i, j := 0, len(t)-1; i < j; i, j = i+1, j-1 {
		t[i], t[j] = t[j], t[i]
	}
}

// Format writes the formatted handicap table to w.
func (ht *HandicapTable) Format(w io.Writer) {
	// Header
	fmt.Fprint(w, rjust("Handicap", 14))
	for _, rnd := range ht.RoundList {
		fmt.Fprint(w, rjust(abbreviate(rnd.Name), 14))
	}
	fmt.Fprintln(w)

	// Determine handicap decimal places
	hcDP := 0
	for _, h := range ht.Handicaps {
		frac := h - math.Floor(h)
		if frac > 0 {
			// Count decimals
			s := fmt.Sprintf("%v", h)
			if idx := strings.Index(s, "."); idx >= 0 {
				dp := len(s) - idx - 1
				if dp > hcDP {
					hcDP = dp
				}
			}
		}
	}

	for ri, h := range ht.Handicaps {
		// Handicap cell
		if hcDP == 0 {
			fmt.Fprintf(w, "%14d", int(h))
		} else {
			fmt.Fprintf(w, "%14.*f", hcDP, h)
		}

		// Score cells
		for ci := range ht.RoundList {
			if ht.IntPrec {
				v := ht.tableI[ri][ci+1]
				if v == fillInt {
					fmt.Fprint(w, rjust("", 14))
				} else {
					fmt.Fprintf(w, "%14d", v)
				}
			} else {
				v := ht.tableF[ri][ci+1]
				if math.IsNaN(v) {
					fmt.Fprint(w, rjust("", 14))
				} else {
					fmt.Fprintf(w, "%14.8f", v)
				}
			}
		}
		fmt.Fprintln(w)
	}
}

// Print writes the formatted table to stdout.
func (ht *HandicapTable) Print() {
	ht.Format(os.Stdout)
}

// WriteCSV writes the table in CSV format.
func (ht *HandicapTable) WriteCSV(w io.Writer) error {
	cw := csv.NewWriter(w)
	// Header
	header := []string{"handicap"}
	for _, rnd := range ht.RoundList {
		header = append(header, rnd.Name)
	}
	if err := cw.Write(header); err != nil {
		return err
	}

	for ri, h := range ht.Handicaps {
		row := make([]string, len(ht.RoundList)+1)
		row[0] = fmt.Sprintf("%v", h)
		for ci := range ht.RoundList {
			if ht.IntPrec {
				v := ht.tableI[ri][ci+1]
				if v == fillInt {
					row[ci+1] = ""
				} else {
					row[ci+1] = fmt.Sprintf("%d", v)
				}
			} else {
				v := ht.tableF[ri][ci+1]
				if math.IsNaN(v) {
					row[ci+1] = ""
				} else {
					row[ci+1] = fmt.Sprintf("%.8f", v)
				}
			}
		}
		if err := cw.Write(row); err != nil {
			return err
		}
	}
	cw.Flush()
	return cw.Error()
}

func rjust(s string, width int) string {
	if len(s) >= width {
		return s
	}
	return strings.Repeat(" ", width-len(s)) + s
}

func abbreviate(name string) string {
	abbrevs := map[string]string{
		"Compound":   "C",
		"Recurve":    "R",
		"Triple":     "Tr",
		"Centre":     "C",
		"Portsmouth": "Ports",
		"Worcester":  "Worc",
		"Short":      "St",
		"Long":       "Lg",
		"Small":      "Sm",
		"Gents":      "G",
		"Ladies":     "L",
	}
	words := strings.Fields(name)
	out := make([]string, len(words))
	for i, w := range words {
		if a, ok := abbrevs[w]; ok {
			out[i] = a
		} else {
			out[i] = w
		}
	}
	return strings.Join(out, " ")
}
