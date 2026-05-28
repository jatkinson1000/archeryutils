package rounds_test

import (
	"strings"
	"testing"

	"github.com/jatkinson1000/archeryutils/rounds"
	"github.com/jatkinson1000/archeryutils/targets"
)

var sharedTarget = func() *targets.Target {
	t, err := targets.NewTarget(targets.FiveZone, targets.CM(122), targets.Metres(50), false)
	if err != nil {
		panic(err)
	}
	return t
}()

func mustPass(t *testing.T, n int, tgt *targets.Target) *rounds.Pass {
	t.Helper()
	p, err := rounds.NewPass(n, tgt)
	if err != nil {
		t.Fatalf("NewPass error: %v", err)
	}
	return p
}

func mustAtTarget(t *testing.T, n int, sys targets.ScoringSystem, diam, dist targets.Quantity, indoor bool) *rounds.Pass {
	t.Helper()
	p, err := rounds.AtTarget(n, sys, diam, dist, indoor)
	if err != nil {
		t.Fatalf("AtTarget error: %v", err)
	}
	return p
}

func mustRound(t *testing.T, name string, passes []*rounds.Pass, opts ...rounds.Option) *rounds.Round {
	t.Helper()
	r, err := rounds.NewRound(name, passes, opts...)
	if err != nil {
		t.Fatalf("NewRound(%q) error: %v", name, err)
	}
	return r
}

// ---- TestPass ----

func TestPassInit(t *testing.T) {
	p := mustPass(t, 36, sharedTarget)
	if p.NArrows != 36 {
		t.Errorf("NArrows = %d, want 36", p.NArrows)
	}
	if !p.Target.Equal(sharedTarget) {
		t.Error("Target mismatch")
	}
}

func TestPassNilTarget(t *testing.T) {
	_, err := rounds.NewPass(36, nil)
	if err == nil {
		t.Fatal("expected error for nil target")
	}
}

func TestPassAtTarget(t *testing.T) {
	p := mustAtTarget(t, 36, targets.FiveZone, targets.CM(122), targets.Metres(50), false)
	if p.NArrows != 36 {
		t.Errorf("NArrows = %d, want 36", p.NArrows)
	}
	if !p.Target.Equal(sharedTarget) {
		t.Error("Target mismatch vs shared")
	}
}

func TestPassString(t *testing.T) {
	p := mustPass(t, 36, sharedTarget)
	got := p.String()
	if !strings.Contains(got, "Pass(36") {
		t.Errorf("String() = %q, want to contain Pass(36", got)
	}
}

func TestPassEquality(t *testing.T) {
	base := mustAtTarget(t, 30, targets.TenZone, targets.CM(40), targets.Yards(20), false)

	tests := []struct {
		name  string
		other *rounds.Pass
		want  bool
	}{
		{"duplicate", mustAtTarget(t, 30, targets.TenZone, targets.CM(40), targets.Yards(20), false), true},
		{"diff-arrows", mustAtTarget(t, 40, targets.TenZone, targets.CM(40), targets.Yards(20), false), false},
		{"diff-target", mustAtTarget(t, 30, targets.FiveZone, targets.CM(40), targets.Yards(20), false), false},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if got := base.Equal(tc.other); got != tc.want {
				t.Errorf("Equal() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestPassDefaultDistanceUnit(t *testing.T) {
	p := mustAtTarget(t, 36, targets.FiveZone, targets.CM(122), targets.Metres(50), false)
	if p.Target.NativeDistance().Units != "metre" {
		t.Errorf("NativeDistance unit = %q, want metre", p.Target.NativeDistance().Units)
	}
}

func TestPassDefaultDiamUnit(t *testing.T) {
	p := mustAtTarget(t, 36, targets.FiveZone, targets.CM(122), targets.Metres(50), false)
	if p.Target.NativeDiameter().Units != "cm" {
		t.Errorf("NativeDiameter unit = %q, want cm", p.Target.NativeDiameter().Units)
	}
}

func TestPassNegativeArrows(t *testing.T) {
	p := mustPass(t, -36, sharedTarget)
	if p.NArrows != 36 {
		t.Errorf("NArrows = %d, want 36 (abs value)", p.NArrows)
	}
}

func TestPassMaxScore(t *testing.T) {
	tests := []struct {
		system targets.ScoringSystem
		want   float64
	}{
		{targets.FiveZone, 900},
		{targets.TenZone, 1000},
		{targets.ElevenZone, 1100},
		{targets.WAField, 600},
		{targets.IFAAField, 500},
		{targets.AANationalField, 500},
		{targets.Worcester2Ring, 500},
		{targets.BeiterHitMiss, 100},
	}
	for _, tc := range tests {
		t.Run(string(tc.system), func(t *testing.T) {
			p := mustAtTarget(t, 100, tc.system, targets.CM(122), targets.Metres(50), false)
			if got := p.MaxScore(); got != tc.want {
				t.Errorf("MaxScore() = %v, want %v", got, tc.want)
			}
		})
	}
}

// ---- TestRound ----

func TestRoundInitWithVariousIterables(t *testing.T) {
	passA := mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(50), false)
	passB := mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(40), false)

	r1 := mustRound(t, "R1", []*rounds.Pass{passA, passB})
	r2 := mustRound(t, "R2", []*rounds.Pass{passA, passB})

	if len(r1.Passes) != len(r2.Passes) {
		t.Error("passes length mismatch")
	}
}

func TestRoundEmptyPasses(t *testing.T) {
	_, err := rounds.NewRound("Empty", []*rounds.Pass{})
	if err == nil {
		t.Fatal("expected error for empty passes")
	}
	if !strings.Contains(err.Error(), "passes must contain at least one") {
		t.Errorf("unexpected error: %v", err)
	}
}

func TestRoundNilPass(t *testing.T) {
	_, err := rounds.NewRound("Bad", []*rounds.Pass{nil})
	if err == nil {
		t.Fatal("expected error for nil pass")
	}
}

func TestRoundString(t *testing.T) {
	p := mustPass(t, 36, sharedTarget)
	r := mustRound(t, "Name", []*rounds.Pass{p})
	if got := r.String(); got != "<Round: 'Name'>" {
		t.Errorf("String() = %q, want \"<Round: 'Name'>\"", got)
	}
}

func TestRoundEquality(t *testing.T) {
	tgt := func() *targets.Target {
		t, _ := targets.NewTarget(targets.TenZone, targets.CM(40), targets.Yards(20), true)
		return t
	}()
	pass_, _ := rounds.NewPass(30, tgt)

	base := mustRound(t, "Test", []*rounds.Pass{pass_, pass_})

	tests := []struct {
		name  string
		round *rounds.Round
		want  bool
	}{
		{"duplicate", mustRound(t, "Test", []*rounds.Pass{pass_, pass_}), true},
		{"labelled", mustRound(t, "Test", []*rounds.Pass{pass_, pass_},
			rounds.WithLocation("indoor"), rounds.WithBody("AGB"), rounds.WithFamily("Bray")), true},
		{"different-name", mustRound(t, "Other", []*rounds.Pass{pass_, pass_}), false},
		{"one-less-pass", mustRound(t, "Test", []*rounds.Pass{pass_}), false},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if got := base.Equal(tc.round); got != tc.want {
				t.Errorf("Equal() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestRoundEqualityPassOrder(t *testing.T) {
	t1, _ := targets.NewTarget(targets.TenZone, targets.CM(122), targets.Metres(90), false)
	t2, _ := targets.NewTarget(targets.TenZone, targets.CM(122), targets.Metres(70), false)
	p1, _ := rounds.NewPass(30, t1)
	p2, _ := rounds.NewPass(30, t2)

	ra := mustRound(t, "Test", []*rounds.Pass{p1, p2})
	rb := mustRound(t, "Test", []*rounds.Pass{p2, p1})

	if ra.Equal(rb) {
		t.Error("rounds with reversed pass order should not be equal")
	}
}

func TestRoundNArrows(t *testing.T) {
	tests := []struct {
		passes []*rounds.Pass
		want   int
	}{
		{[]*rounds.Pass{
			mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(50), false),
			mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(40), false),
			mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(30), false),
		}, 300},
		{[]*rounds.Pass{
			mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(50), false),
		}, 100},
	}
	for _, tc := range tests {
		r := mustRound(t, "R", tc.passes)
		if r.NArrows != tc.want {
			t.Errorf("NArrows = %d, want %d", r.NArrows, tc.want)
		}
	}
}

func TestRoundMaxScore(t *testing.T) {
	r := mustRound(t, "R", []*rounds.Pass{
		mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(50), false),
		mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(40), false),
		mustAtTarget(t, 100, targets.FiveZone, targets.CM(122), targets.Metres(30), false),
	})
	if got := r.MaxScore(); got != 2700 {
		t.Errorf("MaxScore() = %v, want 2700", got)
	}
}

func TestRoundMaxDistance(t *testing.T) {
	tests := []struct {
		unit string
		want float64
	}{
		{"metre", 100},
		{"yard", 100},
	}
	for _, tc := range tests {
		t.Run(tc.unit, func(t *testing.T) {
			var distUnit string
			if tc.unit == "metre" {
				distUnit = "metre"
			} else {
				distUnit = "yard"
			}
			r := mustRound(t, "R", []*rounds.Pass{
				mustAtTarget(t, 10, targets.FiveZone, targets.CM(122), targets.Quantity{Value: 100, Units: distUnit}, false),
				mustAtTarget(t, 10, targets.FiveZone, targets.CM(122), targets.Quantity{Value: 80, Units: distUnit}, false),
				mustAtTarget(t, 10, targets.FiveZone, targets.CM(122), targets.Quantity{Value: 60, Units: distUnit}, false),
			})
			if got := r.MaxDistance().Value; got != tc.want {
				t.Errorf("MaxDistance().Value = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestRoundMaxDistanceOutOfOrder(t *testing.T) {
	r := mustRound(t, "R", []*rounds.Pass{
		mustAtTarget(t, 10, targets.FiveZone, targets.CM(122), targets.Metres(80), false),
		mustAtTarget(t, 10, targets.FiveZone, targets.CM(122), targets.Metres(100), false),
		mustAtTarget(t, 10, targets.FiveZone, targets.CM(122), targets.Metres(60), false),
	})
	if got := r.MaxDistance().Value; got != 100 {
		t.Errorf("MaxDistance().Value = %v, want 100", got)
	}
}

func TestRoundMaxDistanceMixedUnits(t *testing.T) {
	pYards := mustAtTarget(t, 36, targets.FiveZone, targets.CM(122), targets.Yards(80), false)
	pMetric := mustAtTarget(t, 36, targets.FiveZone, targets.CM(122), targets.Metres(75), false)
	r := mustRound(t, "R", []*rounds.Pass{pYards, pMetric})

	if pMetric.Target.Distance() <= pYards.Target.Distance() {
		t.Fatal("test precondition: metric distance should be larger in metres")
	}
	if got := r.MaxDistance().Value; got != 75 {
		t.Errorf("MaxDistance().Value = %v, want 75 (metric)", got)
	}
}

func TestRoundGetInfo(t *testing.T) {
	r := mustRound(t, "MyRound", []*rounds.Pass{
		mustAtTarget(t, 10, targets.FiveZone, targets.CM(122), targets.Metres(100), false),
		mustAtTarget(t, 20, targets.FiveZone, targets.CM(122), targets.Yards(80), false),
		mustAtTarget(t, 30, targets.FiveZone, targets.CM(80), targets.Metres(60), false),
	})

	var sb strings.Builder
	r.GetInfo(&sb)
	got := sb.String()

	wantLines := []string{
		"A MyRound consists of 3 passes:",
		"10 arrows at a 122.0 cm target at 100.0 metres.",
		"20 arrows at a 122.0 cm target at 80.0 yards.",
		"30 arrows at a 80.0 cm target at 60.0 metres.",
	}
	for _, line := range wantLines {
		if !strings.Contains(got, line) {
			t.Errorf("GetInfo() output missing %q\nGot:\n%s", line, got)
		}
	}
}

// ---- Data loading ----

func TestLoadWAOutdoor(t *testing.T) {
	all := rounds.WAOutdoor()
	if len(all) == 0 {
		t.Fatal("WAOutdoor() returned empty map")
	}
	if _, ok := all["wa1440_90"]; !ok {
		t.Error("WAOutdoor() missing wa1440_90")
	}
}

func TestLoadAllRounds(t *testing.T) {
	all := rounds.AllRounds()
	if len(all) < 50 {
		t.Errorf("AllRounds() = %d rounds, want at least 50", len(all))
	}
}
