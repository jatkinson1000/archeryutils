// Package length provides unit conversion utilities for archery distances.
package length

import (
	"fmt"
	"strings"
)

// UnitSet is a set of unit name aliases.
type UnitSet map[string]struct{}

// Union returns a new UnitSet containing all members of all provided sets.
func Union(sets ...UnitSet) UnitSet {
	out := make(UnitSet)
	for _, s := range sets {
		for k := range s {
			out[k] = struct{}{}
		}
	}
	return out
}

func makeSet(aliases ...string) UnitSet {
	s := make(UnitSet, len(aliases))
	for _, a := range aliases {
		s[a] = struct{}{}
	}
	return s
}

// Yard contains all recognised aliases for the yard unit.
var Yard = makeSet("Yard", "yard", "Yards", "yards", "Y", "y", "Yd", "yd", "Yds", "yds")

// Metre contains all recognised aliases for the metre unit.
var Metre = makeSet("Metre", "metre", "Metres", "metres", "M", "m", "Ms", "ms")

// CM contains all recognised aliases for the centimetre unit.
var CM = makeSet("Centimetre", "centimetre", "Centimetres", "centimetres", "CM", "cm", "CMs", "cms")

// Inch contains all recognised aliases for the inch unit.
var Inch = makeSet("Inch", "inch", "Inches", "inches")

// KnownUnits lists all definitive unit names supported by this package.
var KnownUnits = makeSet("yard", "metre", "cm", "inch")

var aliases = map[string]UnitSet{
	"yard":  Yard,
	"metre": Metre,
	"cm":    CM,
	"inch":  Inch,
}

var conversionsToM = map[string]float64{
	"metre": 1.0,
	"yard":  0.9144,
	"cm":    0.01,
	"inch":  0.0254,
}

// aliasToDefinitive maps every alias string to its canonical unit name.
var aliasToDefinitive map[string]string

// aliasToFactor maps every alias string to its conversion factor to metres.
var aliasToFactor map[string]float64

func init() {
	aliasToDefinitive = make(map[string]string)
	aliasToFactor = make(map[string]float64)
	for name, factor := range conversionsToM {
		for alias := range aliases[name] {
			aliasToDefinitive[alias] = name
			aliasToFactor[alias] = factor
		}
	}
}

// ToMetres converts a value in the given unit to metres.
func ToMetres(value float64, unit string) (float64, error) {
	f, ok := aliasToFactor[unit]
	if !ok {
		return 0, fmt.Errorf("unit %q not recognised", unit)
	}
	return f * value, nil
}

// FromMetres converts a value in metres to the given unit.
func FromMetres(value float64, unit string) (float64, error) {
	f, ok := aliasToFactor[unit]
	if !ok {
		return 0, fmt.Errorf("unit %q not recognised", unit)
	}
	return value / f, nil
}

// DefinitiveUnit returns the canonical name for a unit alias.
func DefinitiveUnit(alias string) (string, error) {
	name, ok := aliasToDefinitive[alias]
	if !ok {
		return "", fmt.Errorf("unit %q not recognised", alias)
	}
	return name, nil
}

// DefinitiveUnits reduces a set of unit aliases to their canonical names.
func DefinitiveUnits(aliases UnitSet) (UnitSet, error) {
	out := make(UnitSet)
	for alias := range aliases {
		name, ok := aliasToDefinitive[alias]
		if !ok {
			return nil, fmt.Errorf("unit %q not recognised", alias)
		}
		out[name] = struct{}{}
	}
	return out, nil
}

// definitiveUnitNames returns the set of definitive unit names reachable from
// the provided supported set, formatted for error messages.
func definitiveUnitNames(supported UnitSet) string {
	seen := map[string]struct{}{}
	for alias := range supported {
		if name, ok := aliasToDefinitive[alias]; ok {
			seen[name] = struct{}{}
		}
	}
	names := make([]string, 0, len(seen))
	for n := range seen {
		names = append(names, "'"+n+"'")
	}
	return "{" + strings.Join(names, ", ") + "}"
}

// ParseOptionalUnitsFloat parses a value that is either a plain float64 or a
// [2]any{float64, string} pair, returning the value and its canonical unit name.
// supported restricts which unit aliases are accepted; defaultUnit is used when
// no unit is present in value.
func ParseOptionalUnitsFloat(value any, supported UnitSet, defaultUnit string) (float64, string, error) {
	if _, ok := supported[defaultUnit]; !ok {
		return 0, "", fmt.Errorf("Default unit %q must be in supported units", defaultUnit)
	}

	var v float64
	var unitAlias string

	switch val := value.(type) {
	case float64:
		v = val
		unitAlias = defaultUnit
	case int:
		v = float64(val)
		unitAlias = defaultUnit
	case [2]any:
		fv, ok := toFloat64(val[0])
		if !ok {
			return 0, "", fmt.Errorf("first element of pair must be numeric, got %T", val[0])
		}
		us, ok := val[1].(string)
		if !ok {
			return 0, "", fmt.Errorf("second element of pair must be a string unit, got %T", val[1])
		}
		v = fv
		unitAlias = us
	default:
		fv, ok := toFloat64(val)
		if !ok {
			return 0, "", fmt.Errorf("value must be float64, int, or [2]any{float64,string}, got %T", value)
		}
		v = fv
		unitAlias = defaultUnit
	}

	if _, ok := supported[unitAlias]; !ok {
		return 0, "", fmt.Errorf("Unit %q not recognised. Select from %s.", unitAlias, definitiveUnitNames(supported))
	}
	defUnit, _ := DefinitiveUnit(unitAlias)
	return v, defUnit, nil
}

func toFloat64(v any) (float64, bool) {
	switch n := v.(type) {
	case float64:
		return n, true
	case float32:
		return float64(n), true
	case int:
		return float64(n), true
	case int64:
		return float64(n), true
	}
	return 0, false
}
