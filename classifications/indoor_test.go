package classifications_test

import (
	"testing"

	"github.com/retbrown/archeryutils/classifications"
	"github.com/retbrown/archeryutils/rounds"
	"github.com/retbrown/archeryutils/targets"
)

func indoorRound(t *testing.T, name string) *rounds.Round {
	t.Helper()
	allRounds := make(map[string]*rounds.Round)
	for k, v := range rounds.AGBIndoor() {
		allRounds[k] = v
	}
	for k, v := range rounds.WAIndoor() {
		allRounds[k] = v
	}
	r, ok := allRounds[name]
	if !ok {
		t.Fatalf("indoor round %q not found", name)
	}
	return r
}

func TestIndoorClassificationScoresAges(t *testing.T) {
	tests := []struct {
		age  classifications.Age
		want []int
	}{
		{classifications.Adult, []int{593, 582, 566, 546, 518, 483, 437, 378}},
		{classifications.Over50, []int{583, 569, 549, 522, 488, 444, 387, 316}},
		{classifications.Under21, []int{583, 569, 549, 522, 488, 444, 387, 316}},
		{classifications.Under18, []int{571, 552, 526, 493, 450, 395, 326, 250}},
		{classifications.Under16, []int{555, 530, 498, 457, 403, 336, 260, 187}},
		{classifications.Under15, []int{534, 503, 463, 411, 346, 271, 196, 134}},
		{classifications.Under14, []int{508, 469, 419, 355, 281, 206, 141, 92}},
		{classifications.Under12, []int{475, 426, 364, 291, 215, 149, 98, 62}},
	}
	for _, tc := range tests {
		t.Run("portsmouth_recurve_male_"+tc.age.String(), func(t *testing.T) {
			r := indoorRound(t, "portsmouth")
			got, err := classifications.IndoorClassificationScores(r, classifications.Recurve, classifications.Male, tc.age, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestIndoorClassificationScoresGenders(t *testing.T) {
	tests := []struct {
		age  classifications.Age
		want []int
	}{
		{classifications.Adult, []int{586, 572, 553, 528, 496, 454, 399, 331}},
		{classifications.Under16, []int{539, 510, 472, 423, 360, 286, 211, 145}},
		{classifications.Under15, []int{534, 503, 463, 411, 346, 271, 196, 134}},
		{classifications.Under12, []int{475, 426, 364, 291, 215, 149, 98, 62}},
	}
	for _, tc := range tests {
		t.Run("portsmouth_recurve_female_"+tc.age.String(), func(t *testing.T) {
			r := indoorRound(t, "portsmouth")
			got, err := classifications.IndoorClassificationScores(r, classifications.Recurve, classifications.Female, tc.age, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestIndoorClassificationScoresBowstyles(t *testing.T) {
	tests := []struct {
		bowstyle classifications.Bowstyle
		want     []int
	}{
		{classifications.Compound, []int{594, 583, 571, 560, 549, 532, 508, 472}},
		{classifications.Barebow, []int{565, 549, 528, 503, 472, 433, 387, 331}},
		{classifications.Longbow, []int{501, 466, 423, 369, 306, 240, 178, 127}},
	}
	for _, tc := range tests {
		t.Run("portsmouth_male_adult_"+tc.bowstyle.String(), func(t *testing.T) {
			r := indoorRound(t, "portsmouth")
			got, err := classifications.IndoorClassificationScores(r, tc.bowstyle, classifications.Male, classifications.Adult, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestIndoorClassificationScoresTripleFaces(t *testing.T) {
	tests := []struct {
		round string
		want  []int
	}{
		{"portsmouth_triple", []int{594, 583, 571, 560, 549, 532, 508, 472}},
		{"worcester_5_centre", []int{-9999, -9999, 300, 294, 283, 267, 246, 217}},
		{"vegas_300_triple", []int{300, 297, 290, 281, 269, 252, 230, 201}},
	}
	for _, tc := range tests {
		t.Run(tc.round, func(t *testing.T) {
			r := indoorRound(t, tc.round)
			got, err := classifications.IndoorClassificationScores(r, classifications.Compound, classifications.Male, classifications.Adult, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestIndoorClassificationScoresNonStrict(t *testing.T) {
	// Frostbite: 36 arrows at 30m 80cm outdoor target — not in indoor round set
	r, err := rounds.NewRound("Frostbite", []*rounds.Pass{
		mustOutdoorPass(t, 36, targets.TenZone, targets.CM(80), targets.Metres(30)),
	})
	if err != nil {
		t.Fatalf("NewRound: %v", err)
	}
	want := []int{360, 356, 349, 339, 326, 309, 286, 256}
	got, err := classifications.IndoorClassificationScores(r, classifications.Compound, classifications.Male, classifications.Adult, false)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	assertIntSliceEqual(t, got, want)
}

func TestIndoorClassificationScoresInvalidBowstyle(t *testing.T) {
	r := indoorRound(t, "portsmouth")
	_, err := classifications.IndoorClassificationScores(r, classifications.Traditional, classifications.Male, classifications.Adult, true)
	if err == nil {
		t.Fatal("expected error for invalid bowstyle")
	}
}

func TestIndoorClassificationScoresInvalidRound(t *testing.T) {
	r, _ := rounds.NewRound("Custom", []*rounds.Pass{
		mustIndoorPass(t, 36, targets.TenZone, targets.CM(122), targets.Metres(70)),
	})
	_, err := classifications.IndoorClassificationScores(r, classifications.Recurve, classifications.Male, classifications.Adult, true)
	if err == nil {
		t.Fatal("expected error for unrecognised round")
	}
}

func TestCalculateIndoorClassification(t *testing.T) {
	tests := []struct {
		score    float64
		age      classifications.Age
		bowstyle classifications.Bowstyle
		want     string
	}{
		{594, classifications.Adult, classifications.Compound, "I-GMB"},
		{582, classifications.Over50, classifications.Recurve, "I-MB"},
		{520, classifications.Under21, classifications.Barebow, "I-B1"},
		{551, classifications.Under18, classifications.Recurve, "I-B1"},
		{526, classifications.Under18, classifications.Recurve, "I-B1"},
		{449, classifications.Under12, classifications.Compound, "I-B2"},
		{40, classifications.Under12, classifications.Longbow, "I-A1"},
		{12, classifications.Under12, classifications.Longbow, "UC"},
		{1, classifications.Under12, classifications.Longbow, "UC"},
	}
	for _, tc := range tests {
		t.Run(tc.bowstyle.String()+"_"+tc.age.String()+"_"+tc.want, func(t *testing.T) {
			r := indoorRound(t, "portsmouth")
			got, err := classifications.CalculateIndoorClassification(tc.score, r, tc.bowstyle, classifications.Male, tc.age, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Errorf("got %q, want %q", got, tc.want)
			}
		})
	}
}

func TestCalculateIndoorClassificationInvalidScore(t *testing.T) {
	r := indoorRound(t, "portsmouth")
	_, err := classifications.CalculateIndoorClassification(-1, r, classifications.Recurve, classifications.Male, classifications.Adult, true)
	if err == nil {
		t.Fatal("expected error for negative score")
	}
}

func TestCoaxIndoorGroup(t *testing.T) {
	tests := []struct {
		bowstyle     classifications.Bowstyle
		wantBowstyle classifications.Bowstyle
	}{
		{classifications.Flatbow, classifications.Barebow},
		{classifications.Traditional, classifications.Barebow},
		{classifications.CompoundLimited, classifications.Compound},
		{classifications.CompoundBarebow, classifications.Compound},
		{classifications.Recurve, classifications.Recurve},
	}
	for _, tc := range tests {
		t.Run(tc.bowstyle.String(), func(t *testing.T) {
			cat := classifications.CoaxIndoorGroup(tc.bowstyle, classifications.Male, classifications.Adult)
			if cat.Bowstyle != tc.wantBowstyle {
				t.Errorf("CoaxIndoorGroup(%s).Bowstyle = %s, want %s", tc.bowstyle, cat.Bowstyle, tc.wantBowstyle)
			}
		})
	}
}

func mustIndoorPass(t *testing.T, n int, sys targets.ScoringSystem, diam, dist targets.Quantity) *rounds.Pass {
	t.Helper()
	p, err := rounds.AtTarget(n, sys, diam, dist, true)
	if err != nil {
		t.Fatalf("AtTarget: %v", err)
	}
	return p
}
