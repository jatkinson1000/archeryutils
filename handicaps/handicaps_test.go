package handicaps_test

import (
	"strings"
	"testing"

	"github.com/jatkinson1000/archeryutils/handicaps"
	"github.com/jatkinson1000/archeryutils/rounds"
	"github.com/jatkinson1000/archeryutils/targets"
)

// ---- Shared test rounds ----

func makeYork(t *testing.T) *rounds.Round {
	t.Helper()
	r, err := rounds.NewRound("York", []*rounds.Pass{
		mustAtTarget(t, 72, targets.FiveZone, targets.CM(122), targets.Yards(100), false),
		mustAtTarget(t, 48, targets.FiveZone, targets.CM(122), targets.Yards(80), false),
		mustAtTarget(t, 24, targets.FiveZone, targets.CM(122), targets.Yards(60), false),
	})
	if err != nil {
		t.Fatalf("York: %v", err)
	}
	return r
}

func makeWA720_70(t *testing.T) *rounds.Round {
	t.Helper()
	r, err := rounds.NewRound("WA 720 70m", []*rounds.Pass{
		mustAtTarget(t, 36, targets.TenZone, targets.CM(122), targets.Metres(70), false),
		mustAtTarget(t, 36, targets.TenZone, targets.CM(122), targets.Metres(70), false),
	})
	if err != nil {
		t.Fatalf("WA720_70: %v", err)
	}
	return r
}

func makeWA1440_90(t *testing.T) *rounds.Round {
	t.Helper()
	r, err := rounds.NewRound("WA1440 90m", []*rounds.Pass{
		mustAtTarget(t, 36, targets.TenZone, targets.CM(122), targets.Metres(90), false),
		mustAtTarget(t, 36, targets.TenZone, targets.CM(122), targets.Metres(70), false),
		mustAtTarget(t, 36, targets.TenZone, targets.CM(80), targets.Metres(50), false),
		mustAtTarget(t, 36, targets.TenZone, targets.CM(80), targets.Metres(30), false),
	})
	if err != nil {
		t.Fatalf("WA1440_90: %v", err)
	}
	return r
}

func makeMetric122_30(t *testing.T) *rounds.Round {
	t.Helper()
	r, err := rounds.NewRound("Metric 122-30", []*rounds.Pass{
		mustAtTarget(t, 36, targets.TenZone, targets.CM(122), targets.Metres(30), false),
		mustAtTarget(t, 36, targets.TenZone, targets.CM(122), targets.Metres(30), false),
	})
	if err != nil {
		t.Fatalf("Metric122_30: %v", err)
	}
	return r
}

func makeWestern(t *testing.T) *rounds.Round {
	t.Helper()
	r, err := rounds.NewRound("Western", []*rounds.Pass{
		mustAtTarget(t, 48, targets.FiveZone, targets.CM(122), targets.Yards(60), false),
		mustAtTarget(t, 48, targets.FiveZone, targets.CM(122), targets.Yards(50), false),
	})
	if err != nil {
		t.Fatalf("Western: %v", err)
	}
	return r
}

func makeVegas300(t *testing.T) *rounds.Round {
	t.Helper()
	r, err := rounds.NewRound("Vegas 300", []*rounds.Pass{
		mustAtTarget(t, 30, targets.TenZone, targets.CM(40), targets.Yards(20), true),
	})
	if err != nil {
		t.Fatalf("Vegas300: %v", err)
	}
	return r
}

func makeKings900(t *testing.T) *rounds.Round {
	t.Helper()
	spec := targets.FaceSpec{0.08: 10, 0.12: 8, 0.16: 7, 0.20: 6}
	tgt, _ := targets.FromFaceSpec(spec, targets.CM(40), targets.Metres(18), true)
	p, _ := rounds.NewPass(30, tgt)
	r, err := rounds.NewRound("Kings 900 (recurve)", []*rounds.Pass{p, p, p})
	if err != nil {
		t.Fatalf("Kings900: %v", err)
	}
	return r
}

func mustAtTarget(t *testing.T, n int, sys targets.ScoringSystem, diam, dist targets.Quantity, indoor bool) *rounds.Pass {
	t.Helper()
	p, err := rounds.AtTarget(n, sys, diam, dist, indoor)
	if err != nil {
		t.Fatalf("AtTarget: %v", err)
	}
	return p
}

// ---- TestNewScheme ----

func TestNewSchemeRepr(t *testing.T) {
	for _, name := range []string{"AGB", "AGBold", "AA", "AA2"} {
		s, err := handicaps.NewScheme(name)
		if err != nil {
			t.Fatalf("NewScheme(%q): %v", name, err)
		}
		if s.Name() != name {
			t.Errorf("Name() = %q, want %q", s.Name(), name)
		}
	}
}

func TestNewSchemeInvalid(t *testing.T) {
	_, err := handicaps.NewScheme("InvalidSystem")
	if err == nil {
		t.Fatal("expected error for invalid scheme name")
	}
	if !strings.Contains(err.Error(), "not a recognised handicap system") {
		t.Errorf("unexpected error: %v", err)
	}
}

// ---- TestSigmaT ----

func TestSigmaT(t *testing.T) {
	tests := []struct {
		handicap float64
		system   string
		dist     float64
		want     float64
	}{
		{25.46, "AGB", 100.0, 0.002125743},
		{25.46, "AGBold", 100.0, 0.002149455},
		{25.46, "AA", 100.0, 0.011349271},
		{25.46, "AA2", 100.0, 0.011011017},
		{-12.0, "AGB", 100.0, 0.000585929},
		{-12.0, "AGBold", 100.0, 0.000520552},
		{-12.0, "AA", 100.0, 0.031204851},
		{-12.0, "AA2", 100.0, 0.030274820},
		{200.0, "AGB", 10.0, 0.620202925},
		{200.0, "AGBold", 10.0, 134.960599745},
		{200.0, "AA", 10.0, 7.111717503e-05},
		{200.0, "AA2", 10.0, 7.110517486e-05},
	}
	for _, tc := range tests {
		t.Run(tc.system, func(t *testing.T) {
			s, _ := handicaps.NewScheme(tc.system)
			got := s.SigmaT(tc.handicap, tc.dist)
			if !approxEqual(got, tc.want, 1e-6) {
				t.Errorf("SigmaT(%.2f, %.1f) = %.9f, want %.9f", tc.handicap, tc.dist, got, tc.want)
			}
		})
	}
}

// ---- TestScoreForRound ----

func TestScoreForRound(t *testing.T) {
	wa1440 := makeWA1440_90(t)

	tests := []struct {
		system   string
		handicap float64
		want     float64
	}{
		{"AGB", 10.0, 1356.0},
		{"AGBold", 10.0, 1352.0},
	}
	for _, tc := range tests {
		t.Run(tc.system, func(t *testing.T) {
			s, _ := handicaps.NewScheme(tc.system)
			got := handicaps.ScoreForRound(s, tc.handicap, wa1440, 0, true)
			if !approxEqual(got, tc.want, 1.0) {
				t.Errorf("ScoreForRound(10.0, wa1440, rounded=true) = %.1f, want %.1f", got, tc.want)
			}
		})
	}
}

func TestScoreForRoundAGB10(t *testing.T) {
	wa1440 := makeWA1440_90(t)
	s, _ := handicaps.NewScheme("AGB")
	got := handicaps.ScoreForRound(s, 10.0, wa1440, 0, true)
	if got != 1356.0 {
		t.Errorf("AGB score_for_round(10, wa1440_90, rounded) = %.0f, want 1356", got)
	}
}

func TestRoundedScores(t *testing.T) {
	rnd, _ := rounds.NewRound("MyRound", []*rounds.Pass{
		mustAtTarget(t, 10, targets.TenZone, targets.CM(122), targets.Metres(100), false),
		mustAtTarget(t, 10, targets.TenZone, targets.CM(80), targets.Metres(80), false),
		mustAtTarget(t, 10, targets.FiveZone, targets.CM(122), targets.Metres(60), false),
	})

	tests := []struct {
		system string
		want   float64
	}{
		{"AGB", 244.0},
		{"AGBold", 243.0},
	}
	for _, tc := range tests {
		t.Run(tc.system, func(t *testing.T) {
			s, _ := handicaps.NewScheme(tc.system)
			got := handicaps.ScoreForRound(s, 20.0, rnd, 0, true)
			if got != tc.want {
				t.Errorf("score_for_round(20, ...) = %.0f, want %.0f", got, tc.want)
			}
		})
	}
}

func TestScoreForRoundCustomScoring(t *testing.T) {
	kings := makeKings900(t)
	s, _ := handicaps.NewScheme("AGB")
	got := handicaps.ScoreForRound(s, 20.0, kings, 0, true)
	if got != 896.0 {
		t.Errorf("score_for_round(20, kings_900, rounded) = %.0f, want 896", got)
	}
}

// ---- TestHandicapFromScore ----

func TestHandicapFromScoreOverMax(t *testing.T) {
	rnd, _ := rounds.NewRound("R", []*rounds.Pass{
		mustAtTarget(t, 10, targets.TenZone, targets.CM(122), targets.Metres(50), false),
	})
	s, _ := handicaps.NewScheme("AGB")
	_, err := handicaps.HandicapFromScore(s, 9999, rnd, 0, true)
	if err == nil {
		t.Fatal("expected error for score over max")
	}
	if !strings.Contains(err.Error(), "greater than the maximum") {
		t.Errorf("unexpected error: %v", err)
	}
}

func TestHandicapFromScoreZero(t *testing.T) {
	rnd, _ := rounds.NewRound("R", []*rounds.Pass{
		mustAtTarget(t, 10, targets.TenZone, targets.CM(122), targets.Metres(50), false),
	})
	s, _ := handicaps.NewScheme("AGB")
	_, err := handicaps.HandicapFromScore(s, 0, rnd, 0, true)
	if err == nil {
		t.Fatal("expected error for zero score")
	}
}

func TestHandicapFromScoreNegative(t *testing.T) {
	rnd, _ := rounds.NewRound("R", []*rounds.Pass{
		mustAtTarget(t, 10, targets.TenZone, targets.CM(122), targets.Metres(50), false),
	})
	s, _ := handicaps.NewScheme("AGB")
	_, err := handicaps.HandicapFromScore(s, -100, rnd, 0, true)
	if err == nil {
		t.Fatal("expected error for negative score")
	}
}

func TestHandicapFromScoreMaxScore(t *testing.T) {
	tests := []struct {
		system   string
		rnd      func(t *testing.T) *rounds.Round
		maxScore float64
		want     float64
	}{
		{"AGB", makeMetric122_30, 720, 11},
		{"AA", makeMetric122_30, 720, 107},
		{"AGB", makeWestern, 864, 9},
		{"AGBold", makeWestern, 864, 6},
		{"AGB", makeVegas300, 300, 3},
		{"AA", makeVegas300, 300, 119},
	}
	for _, tc := range tests {
		t.Run(tc.system+"_"+tc.rnd(t).Name, func(t *testing.T) {
			s, _ := handicaps.NewScheme(tc.system)
			h, err := handicaps.HandicapFromScore(s, tc.maxScore, tc.rnd(t), 0, true)
			if err != nil {
				t.Fatalf("HandicapFromScore error: %v", err)
			}
			if !approxEqual(h, tc.want, 0.5) {
				t.Errorf("HandicapFromScore(maxScore) = %.0f, want %.0f", h, tc.want)
			}
		})
	}
}

func TestHandicapFromScoreIntPrecision(t *testing.T) {
	wa720 := makeWA720_70(t)
	wa1440 := makeWA1440_90(t)

	tests := []struct {
		system string
		rnd    *rounds.Round
		score  float64
		want   float64
	}{
		{"AGB", wa720, 700, 1},
		{"AGBold", wa720, 700, 1},
		{"AA", wa720, 700, 119},
		{"AGB", wa720, 500, 44},
		{"AGBold", wa720, 500, 40},
		{"AA", wa720, 500, 64},
		{"AGB", wa720, 283, 63},
		{"AGBold", wa720, 286, 53},
		{"AA", wa720, 280, 39},
		{"AGB", wa720, 486, 46},
		{"AGBold", wa720, 488, 41},
		{"AA", wa720, 491, 62},
		{"AGB", wa720, 710, -5},
		{"AGBold", wa720, 710, -5},
		{"AA", wa720, 52, 0},
		{"AGB", wa1440, 850, 52},
		{"AGBold", wa1440, 850, 46},
		{"AA", wa1440, 850, 53},
	}
	for _, tc := range tests {
		t.Run(tc.system, func(t *testing.T) {
			s, _ := handicaps.NewScheme(tc.system)
			h, err := handicaps.HandicapFromScore(s, tc.score, tc.rnd, 0, true)
			if err != nil {
				t.Fatalf("HandicapFromScore error: %v", err)
			}
			if !approxEqual(h, tc.want, 0.5) {
				t.Errorf("HandicapFromScore(%v, %v, int) = %.0f, want %.0f",
					tc.score, tc.rnd.Name, h, tc.want)
			}
		})
	}
}

func TestHandicapFromScoreDecimal(t *testing.T) {
	wa720 := makeWA720_70(t)
	wa1440 := makeWA1440_90(t)

	tests := []struct {
		system string
		rnd    *rounds.Round
		score  float64
		want   float64
	}{
		{"AGB", wa720, 500, 43.474880980},
		{"AGBold", wa720, 500, 39.056931372},
		{"AA", wa720, 500, 64.197993398},
		{"AGB", wa1440, 850, 51.775514610},
		{"AGBold", wa1440, 850, 45.303733163},
		{"AA", wa1440, 850, 53.545592683},
	}
	for _, tc := range tests {
		t.Run(tc.system, func(t *testing.T) {
			s, _ := handicaps.NewScheme(tc.system)
			h, err := handicaps.HandicapFromScore(s, tc.score, tc.rnd, 0, false)
			if err != nil {
				t.Fatalf("HandicapFromScore error: %v", err)
			}
			if !approxEqual(h, tc.want, 1e-6) {
				t.Errorf("HandicapFromScore(%v, %v, decimal) = %.9f, want %.9f",
					tc.score, tc.rnd.Name, h, tc.want)
			}
		})
	}
}

func TestHandicapFromScoreCustomScoring(t *testing.T) {
	kings := makeKings900(t)
	s, _ := handicaps.NewScheme("AGB")
	h, err := handicaps.HandicapFromScore(s, 896, kings, 0, true)
	if err != nil {
		t.Fatalf("HandicapFromScore error: %v", err)
	}
	if !approxEqual(h, 20, 0.5) {
		t.Errorf("HandicapFromScore(kings 896) = %.0f, want 20", h)
	}
}

func approxEqual(a, b, tol float64) bool {
	d := a - b
	if d < 0 {
		d = -d
	}
	return d <= tol
}
