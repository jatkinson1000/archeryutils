// Command example demonstrates the archeryutils library.
//
// It walks through the main features of the library:
//
//  1. Looking up pre-defined rounds from the embedded databases.
//  2. Computing AGB handicaps from scores and vice-versa.
//  3. Printing a handicap table for a pair of rounds.
//  4. Calculating AGB outdoor, indoor, and field classifications.
//  5. Using the CoaxOutdoorGroup helper for non-standard bowstyles.
//  6. Comparing AGB and Archery Australia handicap schemes.
package main

import (
	"fmt"
	"os"

	"github.com/jatkinson1000/archeryutils/classifications"
	"github.com/jatkinson1000/archeryutils/handicaps"
	"github.com/jatkinson1000/archeryutils/rounds"
)

func main() {
	// ------------------------------------------------------------------ //
	// 1. Rounds
	// ------------------------------------------------------------------ //
	fmt.Println("=== Rounds ===")

	wa1440 := rounds.WAOutdoor()["wa1440_90"]
	york := rounds.AGBOutdoorImperial()["york"]
	portsmouth := rounds.AGBIndoor()["portsmouth"]
	waField := rounds.WAField()["wa_field_24_red_marked"]

	fmt.Printf("Round: %s\n", wa1440.Name)
	fmt.Printf("  Max score:    %.0f\n", wa1440.MaxScore())
	fmt.Printf("  Max distance: %.0f %s\n",
		wa1440.MaxDistance().Value, wa1440.MaxDistance().Units)
	fmt.Println()
	wa1440.GetInfo(os.Stdout)
	fmt.Println()

	// ------------------------------------------------------------------ //
	// 2. Handicaps — score → handicap
	// ------------------------------------------------------------------ //
	fmt.Println("=== Handicap from score (AGB scheme) ===")

	agb := handicaps.MustScheme("AGB")

	scoreExamples := []struct {
		round *rounds.Round
		score float64
	}{
		{wa1440, 1200},
		{york, 900},
		{portsmouth, 580},
	}

	for _, ex := range scoreExamples {
		hc, err := handicaps.HandicapFromScore(agb, ex.score, ex.round, 0, true)
		if err != nil {
			fmt.Fprintf(os.Stderr, "  handicap error (%s): %v\n", ex.round.Name, err)
			continue
		}
		fmt.Printf("  %-20s  score %4.0f  →  handicap %5.1f\n",
			ex.round.Name, ex.score, hc)
	}
	fmt.Println()

	// ------------------------------------------------------------------ //
	// 3. Handicaps — handicap → score
	// ------------------------------------------------------------------ //
	fmt.Println("=== Score for handicap (AGB scheme, WA1440 90m) ===")

	for _, hc := range []float64{0, 10, 20, 30, 50} {
		score := handicaps.ScoreForRound(agb, hc, wa1440, 0, true)
		fmt.Printf("  handicap %2.0f  →  score %4.0f\n", hc, score)
	}
	fmt.Println()

	// ------------------------------------------------------------------ //
	// 4. Handicap table
	// ------------------------------------------------------------------ //
	fmt.Println("=== Handicap table (WA1440 90m + York, handicaps 0–20) ===")

	hcRange := make([]float64, 21)
	for i := range hcRange {
		hcRange[i] = float64(i)
	}
	table, err := handicaps.NewHandicapTable(
		agb,
		hcRange,
		[]*rounds.Round{wa1440, york},
		true,  // rounded scores
		true,  // integer precision
		false, // don't clean repeated rows
		0,     // default arrow diameter
	)
	if err != nil {
		fmt.Fprintf(os.Stderr, "table error: %v\n", err)
		os.Exit(1)
	}
	table.Print()
	fmt.Println()

	// ------------------------------------------------------------------ //
	// 5. Outdoor classification
	// ------------------------------------------------------------------ //
	fmt.Println("=== Outdoor classification ===")

	type outdoorCase struct {
		round    *rounds.Round
		score    float64
		bowstyle classifications.Bowstyle
		gender   classifications.Gender
		age      classifications.Age
	}

	outdoorCases := []outdoorCase{
		{wa1440, 1200, classifications.Recurve, classifications.Male, classifications.Adult},
		{wa1440, 900, classifications.Recurve, classifications.Female, classifications.Under18},
		{york, 900, classifications.Recurve, classifications.Male, classifications.Adult},
		{rounds.WAOutdoor()["wa720_70"], 650, classifications.Recurve, classifications.Male, classifications.Adult},
		{rounds.WAOutdoor()["wa1440_70"], 1100, classifications.Compound, classifications.Female, classifications.Adult},
	}

	for _, c := range outdoorCases {
		class, err := classifications.CalculateOutdoorClassification(
			c.score, c.round, c.bowstyle, c.gender, c.age,
			true, true,
		)
		if err != nil {
			fmt.Fprintf(os.Stderr, "  outdoor classification error: %v\n", err)
			continue
		}
		fmt.Printf("  %-22s  %8s  %6s  %-8s  score %5.0f  →  %s\n",
			c.round.Name,
			c.bowstyle, c.gender, c.age,
			c.score, class,
		)
	}
	fmt.Println()

	// Show the full score thresholds for one group
	fmt.Println("  Score thresholds — WA1440 (90m), Recurve, Male, Adult:")
	thresholds, err := classifications.OutdoorClassificationScores(
		wa1440,
		classifications.Recurve, classifications.Male, classifications.Adult,
		true, true,
	)
	if err != nil {
		fmt.Fprintf(os.Stderr, "  thresholds error: %v\n", err)
	} else {
		labels := []string{"EMB", "GMB", "MB", "B1", "B2", "B3", "A1", "A2", "A3"}
		for i, score := range thresholds {
			label := ""
			if i < len(labels) {
				label = labels[i]
			}
			if score < 0 {
				fmt.Printf("    %-4s  not achievable on this round\n", label)
			} else {
				fmt.Printf("    %-4s  %d\n", label, score)
			}
		}
	}
	fmt.Println()

	// ------------------------------------------------------------------ //
	// 6. Indoor classification
	// ------------------------------------------------------------------ //
	fmt.Println("=== Indoor classification ===")

	type indoorCase struct {
		round    *rounds.Round
		score    float64
		bowstyle classifications.Bowstyle
		gender   classifications.Gender
		age      classifications.Age
	}

	indoorCases := []indoorCase{
		{portsmouth, 580, classifications.Recurve, classifications.Male, classifications.Adult},
		{portsmouth, 580, classifications.Compound, classifications.Female, classifications.Under18},
		{rounds.WAIndoor()["wa18"], 290, classifications.Barebow, classifications.Male, classifications.Adult},
	}

	for _, c := range indoorCases {
		class, err := classifications.CalculateIndoorClassification(
			c.score, c.round, c.bowstyle, c.gender, c.age,
			true,
		)
		if err != nil {
			fmt.Fprintf(os.Stderr, "  indoor classification error: %v\n", err)
			continue
		}
		fmt.Printf("  %-12s  %8s  %6s  %-8s  score %3.0f  →  %s\n",
			c.round.Name,
			c.bowstyle, c.gender, c.age,
			c.score, class,
		)
	}
	fmt.Println()

	// ------------------------------------------------------------------ //
	// 7. Field classification
	// ------------------------------------------------------------------ //
	fmt.Println("=== Field classification ===")

	type fieldCase struct {
		round    *rounds.Round
		score    float64
		bowstyle classifications.Bowstyle
		gender   classifications.Gender
		age      classifications.Age
	}

	fieldCases := []fieldCase{
		{waField, 350, classifications.Recurve, classifications.Male, classifications.Adult},
		{waField, 250, classifications.Barebow, classifications.Female, classifications.Adult},
		{rounds.WAField()["wa_field_24_red_marked"], 400, classifications.Compound, classifications.Male, classifications.Adult},
	}

	for _, c := range fieldCases {
		class, err := classifications.CalculateFieldClassification(
			c.score, c.round, c.bowstyle, c.gender, c.age,
			true, true,
		)
		if err != nil {
			fmt.Fprintf(os.Stderr, "  field classification error: %v\n", err)
			continue
		}
		fmt.Printf("  %-28s  %8s  %6s  %-8s  score %3.0f  →  %s\n",
			c.round.Name,
			c.bowstyle, c.gender, c.age,
			c.score, class,
		)
	}
	fmt.Println()

	// ------------------------------------------------------------------ //
	// 8. Coaxing non-standard bowstyles
	// ------------------------------------------------------------------ //
	fmt.Println("=== CoaxOutdoorGroup (non-standard bowstyles → outdoor equivalent) ===")

	for _, bs := range []classifications.Bowstyle{
		classifications.Flatbow,
		classifications.Traditional,
		classifications.CompoundLimited,
		classifications.CompoundBarebow,
	} {
		cat := classifications.CoaxOutdoorGroup(bs, classifications.Male, classifications.Adult)
		fmt.Printf("  %-16s  →  %s\n", bs, cat.Bowstyle)
	}
	fmt.Println()

	// ------------------------------------------------------------------ //
	// 9. Archery Australia handicap scheme comparison
	// ------------------------------------------------------------------ //
	fmt.Println("=== AGB vs AA handicap comparison (WA1440 90m) ===")

	aa := handicaps.MustScheme("AA")
	for _, score := range []float64{800, 1000, 1100, 1200, 1250} {
		hcAGB, _ := handicaps.HandicapFromScore(agb, score, wa1440, 0, true)
		hcAA, _ := handicaps.HandicapFromScore(aa, score, wa1440, 0, true)
		fmt.Printf("  score %4.0f  →  AGB handicap %5.1f   AA handicap %5.1f\n", score, hcAGB, hcAA)
	}
}
