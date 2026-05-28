package classifications_test

import (
	"testing"

	"github.com/jatkinson1000/archeryutils/classifications"
	"github.com/jatkinson1000/archeryutils/rounds"
	"github.com/jatkinson1000/archeryutils/targets"
)

func outdoorRound(t *testing.T, name string) *rounds.Round {
	t.Helper()
	allRounds := make(map[string]*rounds.Round)
	for k, v := range rounds.AGBOutdoorImperial() {
		allRounds[k] = v
	}
	for k, v := range rounds.AGBOutdoorMetric() {
		allRounds[k] = v
	}
	for k, v := range rounds.WAOutdoor() {
		allRounds[k] = v
	}
	r, ok := allRounds[name]
	if !ok {
		t.Fatalf("round %q not found", name)
	}
	return r
}

func TestOutdoorClassificationScoresAges(t *testing.T) {
	tests := []struct {
		round string
		age   classifications.Age
		want  []int
	}{
		{"wa1440_90", classifications.Adult, []int{1320, 1266, 1197, 1110, 999, 866, 717, 566, 426}},
		{"wa720_70", classifications.Adult, []int{659, 631, 597, 552, 496, 425, 343, 259, 185}},
		{"wa1440_70", classifications.Over50, []int{1305, 1247, 1173, 1079, 960, 817, 659, 503, 364}},
		{"wa1440_90", classifications.Under21, []int{1270, 1203, 1117, 1008, 877, 728, 577, 435, 313}},
		{"wa1440_70", classifications.Under18, []int{1252, 1179, 1086, 969, 828, 671, 514, 373, 259}},
		{"wa1440_60", classifications.Under16, []int{1241, 1165, 1068, 946, 799, 635, 474, 335, 227}},
		{"metric_iii", classifications.Under15, []int{1261, 1191, 1101, 988, 849, 693, 534, 389, 270}},
		{"metric_iv", classifications.Under14, []int{1301, 1242, 1166, 1070, 952, 814, 666, 524, 396}},
		{"metric_v", classifications.Under12, []int{1317, 1263, 1193, 1104, 992, 858, 706, 550, 406}},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_"+tc.age.String(), func(t *testing.T) {
			r := outdoorRound(t, tc.round)
			got, err := classifications.OutdoorClassificationScores(r, classifications.Recurve, classifications.Male, tc.age, true, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOutdoorClassificationScoresGenders(t *testing.T) {
	tests := []struct {
		round string
		age   classifications.Age
		want  []int
	}{
		{"wa1440_70", classifications.Adult, []int{1316, 1261, 1191, 1101, 988, 849, 693, 536, 392}},
		{"metric_iii", classifications.Under16, []int{1274, 1207, 1122, 1014, 881, 727, 567, 418, 293}},
		{"metric_iii", classifications.Under15, []int{1261, 1191, 1101, 988, 849, 693, 534, 389, 270}},
		{"metric_v", classifications.Under12, []int{1317, 1263, 1193, 1104, 992, 858, 706, 550, 406}},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_female_"+tc.age.String(), func(t *testing.T) {
			r := outdoorRound(t, tc.round)
			got, err := classifications.OutdoorClassificationScores(r, classifications.Recurve, classifications.Female, tc.age, true, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOutdoorClassificationScoresBowstyles(t *testing.T) {
	tests := []struct {
		round    string
		bowstyle classifications.Bowstyle
		gender   classifications.Gender
		want     []int
	}{
		{"wa1440_90", classifications.Compound, classifications.Male, []int{1389, 1362, 1327, 1283, 1229, 1162, 1081, 982, 866}},
		{"wa1440_70", classifications.Compound, classifications.Female, []int{1392, 1364, 1330, 1286, 1233, 1167, 1086, 988, 870}},
		{"wa1440_90", classifications.Barebow, classifications.Male, []int{1124, 1042, 945, 835, 717, 598, 484, 380, 290}},
		{"wa1440_70", classifications.Barebow, classifications.Female, []int{1108, 1023, 921, 806, 682, 558, 441, 338, 252}},
		{"wa1440_90", classifications.Longbow, classifications.Male, []int{825, 696, 566, 445, 337, 248, 177, 124, 85}},
		{"wa1440_70", classifications.Longbow, classifications.Female, []int{761, 625, 493, 373, 274, 195, 136, 94, 64}},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_"+tc.bowstyle.String()+"_"+tc.gender.String(), func(t *testing.T) {
			r := outdoorRound(t, tc.round)
			got, err := classifications.OutdoorClassificationScores(r, tc.bowstyle, tc.gender, classifications.Adult, true, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOutdoorClassificationScoresSmallFace(t *testing.T) {
	r := outdoorRound(t, "wa1440_90_small")
	want := []int{1389, 1362, 1327, 1283, 1229, 1162, 1081, 982, 866}
	got, err := classifications.OutdoorClassificationScores(r, classifications.Compound, classifications.Male, classifications.Adult, true, true)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	assertIntSliceEqual(t, got, want)
}

func TestOutdoorClassificationScoresNonStrict(t *testing.T) {
	r := outdoorRound(t, "st_george")
	want := []int{562, 651, 729, 795, 848, 891, 924, 947, 961}
	// non-strict: all scores returned (no prestige or distance restriction)
	got, err := classifications.OutdoorClassificationScores(r, classifications.Compound, classifications.Male, classifications.Adult, false, false)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// non-strict/non-dist returns scores reversed vs strict
	want2 := []int{961, 947, 924, 891, 848, 795, 729, 651, 562}
	assertIntSliceEqual(t, got, want2)
	_ = want
}

func TestOutdoorClassificationScoresNonStrictRound(t *testing.T) {
	tests := []struct {
		round    string
		bowstyle classifications.Bowstyle
		gender   classifications.Gender
		age      classifications.Age
		want     []int
	}{
		{"st_george", classifications.Compound, classifications.Male, classifications.Adult,
			[]int{961, 947, 924, 891, 848, 795, 729, 651, 562}},
		{"wa720_70", classifications.Recurve, classifications.Male, classifications.Adult,
			[]int{-9999, -9999, -9999, -9999, 496, 425, 343, 259, 185}},
		{"wa720_50_c", classifications.Barebow, classifications.Male, classifications.Adult,
			[]int{-9999, -9999, -9999, -9999, -9999, -9999, 212, 159, 117}},
	}
	for _, tc := range tests {
		t.Run(tc.round, func(t *testing.T) {
			r := outdoorRound(t, tc.round)
			got, err := classifications.OutdoorClassificationScores(r, tc.bowstyle, tc.gender, tc.age, false, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOutdoorClassificationScoresNonStrictDistance(t *testing.T) {
	tests := []struct {
		round    string
		bowstyle classifications.Bowstyle
		gender   classifications.Gender
		age      classifications.Age
		want     []int
	}{
		{"st_george", classifications.Compound, classifications.Male, classifications.Adult,
			[]int{-9999, -9999, -9999, 891, 848, 795, 729, 651, 562}},
		{"wa720_70", classifications.Recurve, classifications.Male, classifications.Adult,
			[]int{659, 631, 597, 552, 496, 425, 343, 259, 185}},
		{"wa720_50_c", classifications.Barebow, classifications.Male, classifications.Adult,
			[]int{-9999, -9999, -9999, 406, 341, 274, 212, 159, 117}},
	}
	for _, tc := range tests {
		t.Run(tc.round, func(t *testing.T) {
			r := outdoorRound(t, tc.round)
			got, err := classifications.OutdoorClassificationScores(r, tc.bowstyle, tc.gender, tc.age, true, false)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOutdoorClassificationScoresInvalidBowstyle(t *testing.T) {
	r := outdoorRound(t, "wa1440_90")
	_, err := classifications.OutdoorClassificationScores(r, classifications.Traditional, classifications.Male, classifications.Adult, true, true)
	if err == nil {
		t.Fatal("expected error for invalid bowstyle")
	}
}

func TestOutdoorClassificationScoresInvalidRound(t *testing.T) {
	r, _ := rounds.NewRound("Custom", []*rounds.Pass{
		mustOutdoorPass(t, 36, targets.TenZone, targets.CM(122), targets.Metres(70)),
	})
	_, err := classifications.OutdoorClassificationScores(r, classifications.Recurve, classifications.Male, classifications.Adult, true, true)
	if err == nil {
		t.Fatal("expected error for unrecognised round")
	}
}

func TestCalculateOutdoorClassification(t *testing.T) {
	tests := []struct {
		round    string
		score    float64
		age      classifications.Age
		bowstyle classifications.Bowstyle
		want     string
	}{
		{"wa1440_90", 1390, classifications.Adult, classifications.Compound, "EMB"},
		{"wa1440_70", 1382, classifications.Over50, classifications.Compound, "GMB"},
		{"wa1440_90", 900, classifications.Under21, classifications.Barebow, "MB"},
		{"wa1440_70", 1269, classifications.Under18, classifications.Compound, "B1"},
		{"wa1440_70", 969, classifications.Under18, classifications.Recurve, "B1"},
		{"metric_v", 992, classifications.Under12, classifications.Recurve, "B2"},
		{"metric_v", 222, classifications.Under12, classifications.Longbow, "A1"},
		{"metric_v", 91, classifications.Under12, classifications.Longbow, "UC"},
		{"metric_v", 1, classifications.Under12, classifications.Longbow, "UC"},
		{"metric_v", 250, classifications.Under12, classifications.Longbow, "A1"},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_"+tc.bowstyle.String()+"_"+tc.want, func(t *testing.T) {
			r := outdoorRound(t, tc.round)
			got, err := classifications.CalculateOutdoorClassification(tc.score, r, tc.bowstyle, classifications.Male, tc.age, true, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Errorf("got %q, want %q", got, tc.want)
			}
		})
	}
}

func TestCalculateOutdoorClassificationInvalidScore(t *testing.T) {
	r := outdoorRound(t, "wa1440_90")
	_, err := classifications.CalculateOutdoorClassification(-1, r, classifications.Recurve, classifications.Male, classifications.Adult, true, true)
	if err == nil {
		t.Fatal("expected error for negative score")
	}
	_, err = classifications.CalculateOutdoorClassification(99999, r, classifications.Recurve, classifications.Male, classifications.Adult, true, true)
	if err == nil {
		t.Fatal("expected error for score over max")
	}
}

func TestCoaxOutdoorGroup(t *testing.T) {
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
			cat := classifications.CoaxOutdoorGroup(tc.bowstyle, classifications.Male, classifications.Adult)
			if cat.Bowstyle != tc.wantBowstyle {
				t.Errorf("CoaxOutdoorGroup(%s).Bowstyle = %s, want %s", tc.bowstyle, cat.Bowstyle, tc.wantBowstyle)
			}
		})
	}
}

func mustOutdoorPass(t *testing.T, n int, sys targets.ScoringSystem, diam, dist targets.Quantity) *rounds.Pass {
	t.Helper()
	p, err := rounds.AtTarget(n, sys, diam, dist, false)
	if err != nil {
		t.Fatalf("AtTarget: %v", err)
	}
	return p
}

func assertIntSliceEqual(t *testing.T, got, want []int) {
	t.Helper()
	if len(got) != len(want) {
		t.Errorf("len(got)=%d, len(want)=%d; got=%v, want=%v", len(got), len(want), got, want)
		return
	}
	for i := range got {
		if got[i] != want[i] {
			t.Errorf("index %d: got %d, want %d; full slice: got=%v, want=%v", i, got[i], want[i], got, want)
			return
		}
	}
}
