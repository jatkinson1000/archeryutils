package targets_test

import (
	"strings"
	"testing"

	"github.com/retbrown/archeryutils/targets"
)

func mustTarget(t *testing.T, sys targets.ScoringSystem, diam, dist targets.Quantity, indoor bool) *targets.Target {
	t.Helper()
	tgt, err := targets.NewTarget(sys, diam, dist, indoor)
	if err != nil {
		t.Fatalf("NewTarget(%q,...) error: %v", sys, err)
	}
	return tgt
}

// ---- TestTarget ----

func TestTargetString(t *testing.T) {
	tgt := mustTarget(t, targets.TenZone, targets.CM(80), targets.Metres(30), false)
	want := "Target('10_zone', (80, 'cm'), (30, 'metre'), indoor=false)"
	if got := tgt.String(); got != want {
		t.Errorf("String() = %q, want %q", got, want)
	}
}

func TestTargetStringNativeUnits(t *testing.T) {
	tgt := mustTarget(t, targets.Worcester, targets.Inches(16), targets.Yards(20), true)
	want := "Target('Worcester', (16, 'inch'), (20, 'yard'), indoor=true)"
	if got := tgt.String(); got != want {
		t.Errorf("String() = %q, want %q", got, want)
	}
}

func TestTargetEquality(t *testing.T) {
	base := mustTarget(t, targets.TenZone, targets.CM(40), targets.Metres(20), true)

	tests := []struct {
		name   string
		args   func() *targets.Target
		want   bool
	}{
		{"duplicate", func() *targets.Target {
			return mustTarget(t, targets.TenZone, targets.CM(40), targets.Metres(20), true)
		}, true},
		{"units-free-cm-metre", func() *targets.Target {
			// no explicit unit → CM(40)/Metres(20) equivalent
			return mustTarget(t, targets.TenZone, targets.CM(40), targets.Metres(20), true)
		}, true},
		{"different-loc", func() *targets.Target {
			return mustTarget(t, targets.TenZone, targets.CM(40), targets.Metres(20), false)
		}, false},
		{"different-scoring", func() *targets.Target {
			return mustTarget(t, targets.FiveZone, targets.CM(40), targets.Metres(20), true)
		}, false},
		{"different-dist", func() *targets.Target {
			return mustTarget(t, targets.TenZone, targets.CM(40), targets.Metres(19.9), true)
		}, false},
		{"different-diam", func() *targets.Target {
			return mustTarget(t, targets.TenZone, targets.CM(40.1), targets.Metres(20), true)
		}, false},
		{"different-dist-unit", func() *targets.Target {
			return mustTarget(t, targets.TenZone, targets.CM(40), targets.Yards(20), true)
		}, false},
		{"different-diam-unit", func() *targets.Target {
			return mustTarget(t, targets.TenZone, targets.Inches(40), targets.Metres(20), true)
		}, false},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if got := base.Equal(tc.args()); got != tc.want {
				t.Errorf("Equal() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestTargetInvalidSystem(t *testing.T) {
	_, err := targets.NewTarget("InvalidScoringSystem", targets.CM(122), targets.Metres(50), false)
	if err == nil {
		t.Fatal("expected error for invalid system")
	}
	if !strings.Contains(err.Error(), "Invalid Target Face Type specified") {
		t.Errorf("error %q does not mention 'Invalid Target Face Type specified'", err.Error())
	}
}

func TestTargetInvalidDistanceUnit(t *testing.T) {
	_, err := targets.NewTarget(targets.FiveZone, targets.CM(122), targets.Quantity{50, "InvalidUnit"}, false)
	if err == nil {
		t.Fatal("expected error for invalid distance unit")
	}
}

func TestTargetDefaultDistanceUnit(t *testing.T) {
	tgt := mustTarget(t, targets.FiveZone, targets.CM(122), targets.Metres(50), false)
	if tgt.NativeDistance().Units != "metre" {
		t.Errorf("NativeDistance().Units = %q, want metre", tgt.NativeDistance().Units)
	}
}

func TestTargetYardToMetreConversion(t *testing.T) {
	tgt := mustTarget(t, targets.FiveZone, targets.CM(122), targets.Yards(50), false)
	if tgt.NativeDistance().Units != "yard" {
		t.Errorf("NativeDistance().Units = %q, want yard", tgt.NativeDistance().Units)
	}
	if !approxEqual(tgt.Distance(), 50.0*0.9144, 1e-9) {
		t.Errorf("Distance() = %v, want %v", tgt.Distance(), 50.0*0.9144)
	}
}

func TestTargetDefaultDiamUnit(t *testing.T) {
	tgt := mustTarget(t, targets.TenZoneFiveRingCmpd, targets.CM(80), targets.Metres(50), false)
	if !approxEqual(tgt.Diameter(), 80*0.01, 1e-9) {
		t.Errorf("Diameter() = %v, want %v", tgt.Diameter(), 80*0.01)
	}
}

func TestTargetDiamMetresNotConverted(t *testing.T) {
	tgt := mustTarget(t, targets.BeiterHitMiss, targets.Metres(0.04), targets.Metres(18), false)
	if tgt.Diameter() != 0.04 {
		t.Errorf("Diameter() = %v, want 0.04", tgt.Diameter())
	}
}

func TestTargetInchDiameter(t *testing.T) {
	tgt := mustTarget(t, targets.Worcester, targets.Inches(16), targets.Yards(20), true)
	if tgt.NativeDiameter().Units != "inch" {
		t.Errorf("NativeDiameter().Units = %q, want inch", tgt.NativeDiameter().Units)
	}
	if !approxEqual(tgt.Diameter(), 16*0.0254, 1e-9) {
		t.Errorf("Diameter() = %v, want %v", tgt.Diameter(), 16*0.0254)
	}
}

func TestTargetUnitsCoercedToDefinitive(t *testing.T) {
	imperial := mustTarget(t, targets.Worcester,
		targets.Quantity{16, "Inches"}, targets.Quantity{20, "Yards"}, true)
	metric := mustTarget(t, targets.TenZone,
		targets.Quantity{80, "Centimetres"}, targets.Quantity{30, "Metres"}, false)

	if imperial.NativeDistance().Units != "yard" {
		t.Errorf("imperial NativeDistance().Units = %q, want yard", imperial.NativeDistance().Units)
	}
	if imperial.NativeDiameter().Units != "inch" {
		t.Errorf("imperial NativeDiameter().Units = %q, want inch", imperial.NativeDiameter().Units)
	}
	if metric.NativeDistance().Units != "metre" {
		t.Errorf("metric NativeDistance().Units = %q, want metre", metric.NativeDistance().Units)
	}
	if metric.NativeDiameter().Units != "cm" {
		t.Errorf("metric NativeDiameter().Units = %q, want cm", metric.NativeDiameter().Units)
	}
}

func TestTargetDefaultLocation(t *testing.T) {
	tgt := mustTarget(t, targets.FiveZone, targets.CM(122), targets.Metres(50), false)
	if tgt.Indoor() {
		t.Error("Indoor() = true, want false")
	}
}

func TestTargetMaxScore(t *testing.T) {
	tests := []struct {
		system targets.ScoringSystem
		want   float64
	}{
		{targets.FiveZone, 9},
		{targets.TenZone, 10},
		{targets.TenZoneCompound, 10},
		{targets.TenZoneSixRing, 10},
		{targets.TenZoneFiveRing, 10},
		{targets.TenZoneFiveRingCmpd, 10},
		{targets.ElevenZone, 11},
		{targets.ElevenZoneSixRing, 11},
		{targets.ElevenZoneFiveRing, 11},
		{targets.WAField, 6},
		{targets.IFAAField, 5},
		{targets.IFAAFieldExpert, 5},
		{targets.AANationalField, 5},
		{targets.Worcester, 5},
		{targets.Worcester2Ring, 5},
		{targets.BeiterHitMiss, 1},
	}
	for _, tc := range tests {
		t.Run(string(tc.system), func(t *testing.T) {
			tgt := mustTarget(t, tc.system, targets.CM(122), targets.Metres(50), false)
			if got := tgt.MaxScore(); got != tc.want {
				t.Errorf("MaxScore() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestTargetMinScore(t *testing.T) {
	tests := []struct {
		system targets.ScoringSystem
		want   float64
	}{
		{targets.FiveZone, 1},
		{targets.TenZone, 1},
		{targets.TenZoneCompound, 1},
		{targets.TenZoneSixRing, 5},
		{targets.TenZoneFiveRing, 6},
		{targets.TenZoneFiveRingCmpd, 6},
		{targets.ElevenZone, 1},
		{targets.ElevenZoneSixRing, 5},
		{targets.ElevenZoneFiveRing, 6},
		{targets.WAField, 1},
		{targets.IFAAField, 3},
		{targets.IFAAFieldExpert, 1},
		{targets.AANationalField, 1},
		{targets.Worcester, 1},
		{targets.Worcester2Ring, 4},
		{targets.BeiterHitMiss, 1},
	}
	for _, tc := range tests {
		t.Run(string(tc.system), func(t *testing.T) {
			tgt := mustTarget(t, tc.system, targets.CM(122), targets.Metres(50), false)
			if got := tgt.MinScore(); got != tc.want {
				t.Errorf("MinScore() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestTargetFaceSpec(t *testing.T) {
	tests := []struct {
		system targets.ScoringSystem
		diam   targets.Quantity
		want   targets.FaceSpec
	}{
		{targets.FiveZone, targets.CM(122), targets.FaceSpec{
			0.244: 9, 0.488: 7, 0.732: 5, 0.976: 3, 1.22: 1,
		}},
		{targets.TenZone, targets.CM(80), targets.FaceSpec{
			0.08: 10, 0.16: 9, 0.24: 8, 0.32: 7, 0.40: 6,
			0.48: 5, 0.56: 4, 0.64: 3, 0.72: 2, 0.80: 1,
		}},
		{targets.ElevenZone, targets.CM(40), targets.FaceSpec{
			0.02: 11, 0.04: 10, 0.08: 9, 0.12: 8, 0.16: 7,
			0.20: 6, 0.24: 5, 0.28: 4, 0.32: 3, 0.36: 2, 0.40: 1,
		}},
		{targets.ElevenZoneSixRing, targets.CM(40), targets.FaceSpec{
			0.02: 11, 0.04: 10, 0.08: 9, 0.12: 8, 0.16: 7, 0.20: 6, 0.24: 5,
		}},
		{targets.WAField, targets.CM(80), targets.FaceSpec{
			0.08: 6, 0.16: 5, 0.32: 4, 0.48: 3, 0.64: 2, 0.80: 1,
		}},
		{targets.IFAAField, targets.CM(50), targets.FaceSpec{
			0.10: 5, 0.30: 4, 0.50: 3,
		}},
		{targets.AANationalField, targets.CM(20), targets.FaceSpec{
			0.04: 5, 0.08: 4, 0.12: 3, 0.16: 2, 0.20: 1,
		}},
		{targets.BeiterHitMiss, targets.CM(6), targets.FaceSpec{0.06: 1}},
		{targets.Worcester, targets.Inches(16), targets.FaceSpec{
			0.08128: 5, 0.16256: 4, 0.24384: 3, 0.32512: 2, 0.40640: 1,
		}},
		{targets.TenZoneSixRing, targets.CM(80), targets.FaceSpec{
			0.08: 10, 0.16: 9, 0.24: 8, 0.32: 7, 0.40: 6, 0.48: 5,
		}},
		{targets.TenZoneFiveRingCmpd, targets.CM(40), targets.FaceSpec{
			0.02: 10, 0.08: 9, 0.12: 8, 0.16: 7, 0.20: 6,
		}},
	}

	for _, tc := range tests {
		t.Run(string(tc.system), func(t *testing.T) {
			tgt := mustTarget(t, tc.system, tc.diam, targets.Metres(30), false)
			got, err := tgt.FaceSpec()
			if err != nil {
				t.Fatalf("FaceSpec() error: %v", err)
			}
			if !faceSpecEqual(got, tc.want, 1e-5) {
				t.Errorf("FaceSpec() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestTargetFaceSpecWrongConstructor(t *testing.T) {
	tgt := mustTarget(t, targets.Custom, targets.CM(122), targets.Metres(50), false)
	_, err := tgt.FaceSpec()
	if err == nil {
		t.Fatal("expected error accessing face spec on Custom target with no spec")
	}
	if !strings.Contains(err.Error(), "Trying to generate face spec for custom target") {
		t.Errorf("unexpected error: %v", err)
	}
}

func TestGenFaceSpecUnsupported(t *testing.T) {
	_, err := targets.GenFaceSpec("Dartchery", 1.0)
	if err == nil {
		t.Fatal("expected error for unsupported scoring system")
	}
}

// ---- TestCustomScoringTarget ----

func TestCustomTargetConstructor(t *testing.T) {
	spec := targets.FaceSpec{0.1: 3, 0.5: 1}
	tgt, err := targets.FromFaceSpec(spec, targets.CM(80), targets.Yards(50), false)
	if err != nil {
		t.Fatalf("FromFaceSpec error: %v", err)
	}
	if !approxEqual(tgt.Distance(), 50.0*0.9144, 1e-9) {
		t.Errorf("Distance() = %v, want %v", tgt.Distance(), 50.0*0.9144)
	}
	if tgt.Diameter() != 0.8 {
		t.Errorf("Diameter() = %v, want 0.8", tgt.Diameter())
	}
	if tgt.ScoringSystem() != targets.Custom {
		t.Errorf("ScoringSystem() = %q, want Custom", tgt.ScoringSystem())
	}
	got, _ := tgt.FaceSpec()
	want := targets.FaceSpec{0.1: 3, 0.5: 1}
	if !faceSpecEqual(got, want, 1e-9) {
		t.Errorf("FaceSpec() = %v, want %v", got, want)
	}
}

func TestCustomTargetFaceSpecUnits(t *testing.T) {
	spec := targets.FaceSpec{10: 5, 20: 4, 30: 3}
	tgt, err := targets.FromFaceSpec([2]any{spec, "cm"}, targets.CM(50), targets.Metres(30), false)
	if err != nil {
		t.Fatalf("FromFaceSpec error: %v", err)
	}
	got, _ := tgt.FaceSpec()
	want := targets.FaceSpec{0.1: 5, 0.2: 4, 0.3: 3}
	if !faceSpecEqual(got, want, 1e-9) {
		t.Errorf("FaceSpec() = %v, want %v", got, want)
	}
}

func TestCustomTargetInvalidFaceSpecUnits(t *testing.T) {
	spec := targets.FaceSpec{10: 5, 20: 4}
	_, err := targets.FromFaceSpec([2]any{spec, "bananas"}, targets.CM(50), targets.Metres(30), false)
	if err == nil {
		t.Fatal("expected error for unsupported face spec units")
	}
}

func TestCustomTargetEquality(t *testing.T) {
	base, _ := targets.FromFaceSpec(targets.FaceSpec{0.2: 2, 0.4: 1}, targets.CM(40), targets.Metres(20), true)
	dup, _ := targets.FromFaceSpec(targets.FaceSpec{0.2: 2, 0.4: 1}, targets.CM(40), targets.Metres(20), true)
	diff, _ := targets.FromFaceSpec(targets.FaceSpec{0.4: 5}, targets.CM(40), targets.Metres(20), true)

	if !base.Equal(dup) {
		t.Error("duplicate custom targets should be equal")
	}
	if base.Equal(diff) {
		t.Error("different custom targets should not be equal")
	}
}

func TestCustomTargetMaxScore(t *testing.T) {
	spec := targets.FaceSpec{0.02: 11, 0.04: 10, 0.8: 9, 0.12: 8, 0.16: 7, 0.2: 6}
	tgt, _ := targets.FromFaceSpec(spec, targets.CM(40), targets.Metres(18), false)
	if got := tgt.MaxScore(); got != 11 {
		t.Errorf("MaxScore() = %v, want 11", got)
	}
}

func TestCustomTargetMinScore(t *testing.T) {
	spec := targets.FaceSpec{0.02: 11, 0.04: 10, 0.8: 9, 0.12: 8, 0.16: 7, 0.2: 6}
	tgt, _ := targets.FromFaceSpec(spec, targets.CM(40), targets.Metres(18), false)
	if got := tgt.MinScore(); got != 6 {
		t.Errorf("MinScore() = %v, want 6", got)
	}
}

// ---- helpers ----

func approxEqual(a, b, tol float64) bool {
	d := a - b
	if d < 0 {
		d = -d
	}
	return d <= tol
}

func faceSpecEqual(a, b targets.FaceSpec, tol float64) bool {
	if len(a) != len(b) {
		return false
	}
	for k, va := range a {
		// Find closest key in b
		found := false
		for kb, vb := range b {
			if approxEqual(k, kb, tol) {
				if va != vb {
					return false
				}
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}
	return true
}
