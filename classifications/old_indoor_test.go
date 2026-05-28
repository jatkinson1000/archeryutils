package classifications_test

import (
	"testing"

	"github.com/jatkinson1000/archeryutils/classifications"
	"github.com/jatkinson1000/archeryutils/rounds"
	"github.com/jatkinson1000/archeryutils/targets"
)

func TestOldIndoorClassificationScoresAges(t *testing.T) {
	r := indoorRound(t, "portsmouth")
	want := []int{592, 582, 554, 505, 432, 315, 195, 139}
	// All ages map to Adult for old indoor
	got, err := classifications.OldIndoorClassificationScores(r, classifications.Recurve, classifications.Male, classifications.Adult, true)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	assertIntSliceEqual(t, got, want)
}

func TestOldIndoorClassificationScoresGender(t *testing.T) {
	r := indoorRound(t, "portsmouth")
	want := []int{582, 569, 534, 479, 380, 255, 139, 93}
	got, err := classifications.OldIndoorClassificationScores(r, classifications.Recurve, classifications.Female, classifications.Adult, true)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	assertIntSliceEqual(t, got, want)
}

func TestOldIndoorClassificationScoresBowstyles(t *testing.T) {
	tests := []struct {
		bowstyle classifications.Bowstyle
		gender   classifications.Gender
		want     []int
	}{
		{classifications.Compound, classifications.Male, []int{581, 570, 554, 529, 484, 396, 279, 206}},
		{classifications.Compound, classifications.Female, []int{570, 562, 544, 509, 449, 347, 206, 160}},
	}
	for _, tc := range tests {
		t.Run(tc.bowstyle.String()+"_"+tc.gender.String(), func(t *testing.T) {
			r := indoorRound(t, "portsmouth")
			got, err := classifications.OldIndoorClassificationScores(r, tc.bowstyle, tc.gender, classifications.Adult, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOldIndoorClassificationScoresTripleFaces(t *testing.T) {
	// Triple and spot variants: reversed expected (ascending → descending)
	tests := []struct {
		round string
		want  []int // descending order (A first)
	}{
		{"portsmouth_triple", []int{581, 570, 554, 529, 484, 396, 279, 206}},
		{"worcester_5_centre", []int{300, 299, 289, 264, 226, 162, 96, 65}},
		{"wa18_triple", []int{568, 558, 537, 486, 370, 203, 100, 63}},
		{"wa18", []int{568, 558, 537, 493, 420, 295, 173, 117}},
	}
	for _, tc := range tests {
		t.Run(tc.round, func(t *testing.T) {
			r := indoorRound(t, tc.round)
			got, err := classifications.OldIndoorClassificationScores(r, classifications.Compound, classifications.Male, classifications.Adult, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOldIndoorClassificationScoresInvalidBowstyle(t *testing.T) {
	r := indoorRound(t, "portsmouth")
	_, err := classifications.OldIndoorClassificationScores(r, classifications.Barebow, classifications.Male, classifications.Adult, true)
	if err == nil {
		t.Fatal("expected error for invalid (Barebow) bowstyle")
	}
}

func TestOldIndoorClassificationScoresInvalidAge(t *testing.T) {
	r := indoorRound(t, "portsmouth")
	_, err := classifications.OldIndoorClassificationScores(r, classifications.Recurve, classifications.Male, classifications.Under12, true)
	if err == nil {
		t.Fatal("expected error for invalid age (Under12)")
	}
}

func TestOldIndoorClassificationScoresInvalidRound(t *testing.T) {
	r := outdoorRound(t, "wa1440_90")
	_, err := classifications.OldIndoorClassificationScores(r, classifications.Recurve, classifications.Male, classifications.Adult, true)
	if err == nil {
		t.Fatal("expected error for outdoor round in old indoor")
	}
}

func TestOldIndoorClassificationScoresNonStrict(t *testing.T) {
	// Frostbite: 36 arrows at 30m 80cm outdoor — not an indoor round
	frostbite := mustOutdoorPass(t, 36, "10_zone", targets.CM(80), targets.Metres(30))
	r, err := rounds.NewRound("Frostbite", []*rounds.Pass{frostbite})
	if err != nil {
		t.Fatalf("NewRound: %v", err)
	}
	want := []int{357, 351, 336, 310, 269, 195, 110, 68}
	got, err := classifications.OldIndoorClassificationScores(r, classifications.Compound, classifications.Male, classifications.Adult, false)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	assertIntSliceEqual(t, got, want)
}

func TestCalculateOldIndoorClassification(t *testing.T) {
	tests := []struct {
		score  float64
		gender classifications.Gender
		want   string
	}{
		{400, classifications.Male, "F"},
		{337, classifications.Female, "F"},
		{592, classifications.Male, "A"},
		{582, classifications.Female, "A"},
		{581, classifications.Male, "C"},
		{120, classifications.Male, "UC"},
		{1, classifications.Male, "UC"},
	}
	for _, tc := range tests {
		t.Run(tc.gender.String()+"_"+tc.want, func(t *testing.T) {
			r := indoorRound(t, "portsmouth")
			got, err := classifications.CalculateOldIndoorClassification(tc.score, r, classifications.Recurve, tc.gender, classifications.Adult, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Errorf("score=%.0f: got %q, want %q", tc.score, got, tc.want)
			}
		})
	}
}

func TestCalculateOldIndoorClassificationInvalidScore(t *testing.T) {
	r := indoorRound(t, "portsmouth")
	for _, score := range []float64{1000, 601, -1, -100} {
		_, err := classifications.CalculateOldIndoorClassification(score, r, classifications.Recurve, classifications.Male, classifications.Adult, true)
		if err == nil {
			t.Errorf("expected error for score=%.0f", score)
		}
	}
}

func TestCoaxOldIndoorGroup(t *testing.T) {
	tests := []struct {
		bowstyle     classifications.Bowstyle
		wantBowstyle classifications.Bowstyle
		wantAge      classifications.Age
	}{
		{classifications.Compound, classifications.Compound, classifications.Adult},
		{classifications.CompoundLimited, classifications.Compound, classifications.Adult},
		{classifications.CompoundBarebow, classifications.Compound, classifications.Adult},
		{classifications.Recurve, classifications.Recurve, classifications.Adult},
		{classifications.Barebow, classifications.Recurve, classifications.Adult},
		{classifications.Longbow, classifications.Recurve, classifications.Adult},
	}
	for _, tc := range tests {
		t.Run(tc.bowstyle.String(), func(t *testing.T) {
			cat := classifications.CoaxOldIndoorGroup(tc.bowstyle, classifications.Male, classifications.Under18)
			if cat.Bowstyle != tc.wantBowstyle {
				t.Errorf("bowstyle: got %s, want %s", cat.Bowstyle, tc.wantBowstyle)
			}
			if cat.AgeGroup != tc.wantAge {
				t.Errorf("age: got %s, want %s", cat.AgeGroup, tc.wantAge)
			}
		})
	}
}

