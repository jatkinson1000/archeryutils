package length_test

import (
	"testing"

	"github.com/retbrown/archeryutils/length"
)

func TestKnownUnits(t *testing.T) {
	want := map[string]struct{}{
		"cm": {}, "inch": {}, "metre": {}, "yard": {},
	}
	if len(length.KnownUnits) != len(want) {
		t.Fatalf("KnownUnits = %v, want %v", length.KnownUnits, want)
	}
	for k := range want {
		if _, ok := length.KnownUnits[k]; !ok {
			t.Errorf("KnownUnits missing %q", k)
		}
	}
}

func TestUnitSetsContainDefinitiveName(t *testing.T) {
	tests := []struct {
		name string
		set  length.UnitSet
	}{
		{"cm", length.CM},
		{"inch", length.Inch},
		{"metre", length.Metre},
		{"yard", length.Yard},
	}
	for _, tc := range tests {
		if _, ok := tc.set[tc.name]; !ok {
			t.Errorf("set %q does not contain definitive name %q", tc.name, tc.name)
		}
	}
}

func TestUnitSetsContainPlurals(t *testing.T) {
	tests := []struct {
		plural string
		set    length.UnitSet
	}{
		{"cms", length.CM},
		{"inches", length.Inch},
		{"metres", length.Metre},
		{"yards", length.Yard},
	}
	for _, tc := range tests {
		if _, ok := tc.set[tc.plural]; !ok {
			t.Errorf("set does not contain plural %q", tc.plural)
		}
	}
}

func TestToMetres(t *testing.T) {
	tests := []struct {
		value float64
		unit  string
		want  float64
	}{
		{10, "metre", 10},
		{10, "cm", 0.1},
		{10, "inch", 0.254},
		{10, "yard", 9.144},
	}
	for _, tc := range tests {
		got, err := length.ToMetres(tc.value, tc.unit)
		if err != nil {
			t.Errorf("ToMetres(%v,%q) error: %v", tc.value, tc.unit, err)
			continue
		}
		if !approxEqual(got, tc.want, 1e-9) {
			t.Errorf("ToMetres(%v,%q) = %v, want %v", tc.value, tc.unit, got, tc.want)
		}
	}
}

func TestFromMetres(t *testing.T) {
	tests := []struct {
		value float64
		unit  string
		want  float64
	}{
		{10, "metre", 10},
		{10, "cm", 1000},
		{10, "inch", 393.7008},
		{10, "yard", 10.93613},
	}
	for _, tc := range tests {
		got, err := length.FromMetres(tc.value, tc.unit)
		if err != nil {
			t.Errorf("FromMetres(%v,%q) error: %v", tc.value, tc.unit, err)
			continue
		}
		if !approxEqual(got, tc.want, 1e-4) {
			t.Errorf("FromMetres(%v,%q) = %v, want %v", tc.value, tc.unit, got, tc.want)
		}
	}
}

func TestDefinitiveUnit(t *testing.T) {
	tests := []struct {
		alias string
		want  string
	}{
		{"m", "metre"},
		{"centimetre", "cm"},
		{"Inch", "inch"},
		{"yd", "yard"},
	}
	for _, tc := range tests {
		got, err := length.DefinitiveUnit(tc.alias)
		if err != nil {
			t.Errorf("DefinitiveUnit(%q) error: %v", tc.alias, err)
			continue
		}
		if got != tc.want {
			t.Errorf("DefinitiveUnit(%q) = %q, want %q", tc.alias, got, tc.want)
		}
	}
}

func TestDefinitiveUnits(t *testing.T) {
	set := length.Union(length.Inch, length.CM)
	got, err := length.DefinitiveUnits(set)
	if err != nil {
		t.Fatalf("DefinitiveUnits error: %v", err)
	}
	want := length.UnitSet{"inch": {}, "cm": {}}
	if len(got) != len(want) {
		t.Fatalf("DefinitiveUnits = %v, want %v", got, want)
	}
	for k := range want {
		if _, ok := got[k]; !ok {
			t.Errorf("DefinitiveUnits result missing %q", k)
		}
	}
}

func TestParseOptionalUnitsFloat(t *testing.T) {
	supported := length.Union(length.Metre, length.Yard)
	tests := []struct {
		name        string
		value       any
		wantVal     float64
		wantUnit    string
	}{
		{"int-scalar", 10, 10, "metre"},
		{"float-scalar", 10.1, 10.1, "metre"},
		{"default-units", [2]any{10, "Metres"}, 10, "metre"},
		{"other-units", [2]any{10, "yds"}, 10, "yard"},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			v, u, err := length.ParseOptionalUnitsFloat(tc.value, supported, "metre")
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if !approxEqual(v, tc.wantVal, 1e-12) {
				t.Errorf("value = %v, want %v", v, tc.wantVal)
			}
			if u != tc.wantUnit {
				t.Errorf("unit = %q, want %q", u, tc.wantUnit)
			}
		})
	}
}

func TestParseOptionalUnitsUnsupported(t *testing.T) {
	supported := length.Union(length.Metre, length.Yard)
	_, _, err := length.ParseOptionalUnitsFloat([2]any{10.0, "bannana"}, supported, "metre")
	if err == nil {
		t.Fatal("expected error for unsupported unit, got nil")
	}
}

func TestParseOptionalUnitsDefaultNotSupported(t *testing.T) {
	supported := length.Union(length.Metre, length.Yard)
	_, _, err := length.ParseOptionalUnitsFloat(10.0, supported, "inch")
	if err == nil {
		t.Fatal("expected error for unsupported default unit, got nil")
	}
}

func approxEqual(a, b, tol float64) bool {
	d := a - b
	if d < 0 {
		d = -d
	}
	return d <= tol
}
