// Package targets provides types for representing archery targets.
package targets

import (
	"fmt"
	"math"
	"sort"
	"strings"

	"github.com/retbrown/archeryutils/length"
)

// ScoringSystem names a target face/scoring system.
type ScoringSystem string

// All scoring systems supported natively.
const (
	FiveZone              ScoringSystem = "5_zone"
	TenZone               ScoringSystem = "10_zone"
	TenZoneCompound       ScoringSystem = "10_zone_compound"
	TenZoneSixRing        ScoringSystem = "10_zone_6_ring"
	TenZoneFiveRing       ScoringSystem = "10_zone_5_ring"
	TenZoneFiveRingCmpd   ScoringSystem = "10_zone_5_ring_compound"
	ElevenZone            ScoringSystem = "11_zone"
	ElevenZoneSixRing     ScoringSystem = "11_zone_6_ring"
	ElevenZoneFiveRing    ScoringSystem = "11_zone_5_ring"
	WAField               ScoringSystem = "WA_field"
	IFAAField             ScoringSystem = "IFAA_field"
	IFAAFieldExpert       ScoringSystem = "IFAA_field_expert"
	AANationalField       ScoringSystem = "AA_national_field"
	BeiterHitMiss         ScoringSystem = "Beiter_hit_miss"
	Worcester             ScoringSystem = "Worcester"
	Worcester2Ring        ScoringSystem = "Worcester_2_ring"
	Custom                ScoringSystem = "Custom"
)

// supportedSystems lists every scoring system archeryutils knows by default.
var supportedSystems = []ScoringSystem{
	FiveZone, TenZone, TenZoneCompound, TenZoneSixRing, TenZoneFiveRing,
	TenZoneFiveRingCmpd, ElevenZone, ElevenZoneSixRing, ElevenZoneFiveRing,
	WAField, IFAAField, IFAAFieldExpert, AANationalField, BeiterHitMiss,
	Worcester, Worcester2Ring, Custom,
}

var supportedSystemSet map[ScoringSystem]struct{}

func init() {
	supportedSystemSet = make(map[ScoringSystem]struct{}, len(supportedSystems))
	for _, s := range supportedSystems {
		supportedSystemSet[s] = struct{}{}
	}
}

// FaceSpec maps each ring diameter (in metres) to its score value.
type FaceSpec map[float64]int

// Quantity is a scalar value with its unit.
type Quantity struct {
	Value float64
	Units string
}

// CM returns a Quantity in centimetres.
func CM(v float64) Quantity { return Quantity{v, "cm"} }

// Metres returns a Quantity in metres.
func Metres(v float64) Quantity { return Quantity{v, "metre"} }

// Yards returns a Quantity in yards.
func Yards(v float64) Quantity { return Quantity{v, "yard"} }

// Inches returns a Quantity in inches.
func Inches(v float64) Quantity { return Quantity{v, "inch"} }

// supported unit sets for diameter and distance
var (
	supportedDiamUnits = length.Union(length.CM, length.Inch, length.Metre)
	supportedDistUnits = length.Union(length.Yard, length.Metre)
)

// Target represents an archery target face at a given distance.
type Target struct {
	diameter       float64  // metres
	distance       float64  // metres
	nativeDiameter Quantity // original value+unit
	nativeDistance Quantity // original value+unit
	scoringSystem  ScoringSystem
	indoor         bool
	faceSpec       FaceSpec
}

// NewTarget creates a Target. diameter defaults to centimetres; distance defaults to metres.
func NewTarget(system ScoringSystem, diameter, distance Quantity, indoor bool) (*Target, error) {
	if _, ok := supportedSystemSet[system]; !ok {
		names := make([]string, len(supportedSystems))
		for i, s := range supportedSystems {
			names[i] = "'" + string(s) + "'"
		}
		return nil, fmt.Errorf(
			"Invalid Target Face Type specified.\nPlease select from %s.",
			strings.Join(names, ", "),
		)
	}

	diamVal, diamUnit, err := length.ParseOptionalUnitsFloat(
		diameter.Value, supportedDiamUnits, diameter.Units,
	)
	if err != nil {
		return nil, err
	}
	distVal, distUnit, err := length.ParseOptionalUnitsFloat(
		distance.Value, supportedDistUnits, distance.Units,
	)
	if err != nil {
		return nil, err
	}

	diamM, err := length.ToMetres(diamVal, diamUnit)
	if err != nil {
		return nil, err
	}
	distM, err := length.ToMetres(distVal, distUnit)
	if err != nil {
		return nil, err
	}

	t := &Target{
		scoringSystem:  system,
		diameter:       diamM,
		nativeDiameter: Quantity{diamVal, diamUnit},
		distance:       distM,
		nativeDistance: Quantity{distVal, distUnit},
		indoor:         indoor,
	}

	if system != Custom {
		spec, err := GenFaceSpec(system, diamM)
		if err != nil {
			return nil, err
		}
		t.faceSpec = spec
	}

	return t, nil
}

// FromFaceSpec creates a Target with a custom scoring spec.
// spec may be a FaceSpec (units default to metres) or [2]any{FaceSpec, string}.
func FromFaceSpec(spec any, diameter, distance Quantity, indoor bool) (*Target, error) {
	var rawSpec FaceSpec
	var specUnits string

	switch v := spec.(type) {
	case FaceSpec:
		rawSpec = v
		specUnits = "metre"
	case [2]any:
		fs, ok := v[0].(FaceSpec)
		if !ok {
			return nil, fmt.Errorf("first element must be FaceSpec, got %T", v[0])
		}
		u, ok := v[1].(string)
		if !ok {
			return nil, fmt.Errorf("second element must be string unit, got %T", v[1])
		}
		rawSpec = fs
		specUnits = u
	default:
		return nil, fmt.Errorf("spec must be FaceSpec or [2]any{FaceSpec,string}, got %T", spec)
	}

	// Validate spec units
	defSpecUnit, err := validateAndResolveUnit(specUnits, supportedDiamUnits)
	if err != nil {
		return nil, err
	}

	// Convert spec ring diameters to metres
	converted := make(FaceSpec, len(rawSpec))
	for ringDiam, score := range rawSpec {
		m, err := length.ToMetres(ringDiam, defSpecUnit)
		if err != nil {
			return nil, err
		}
		converted[rnd6(m)] = score
	}

	t, err := NewTarget(Custom, diameter, distance, indoor)
	if err != nil {
		return nil, err
	}
	t.faceSpec = converted
	return t, nil
}

func validateAndResolveUnit(unit string, supported length.UnitSet) (string, error) {
	if _, ok := supported[unit]; !ok {
		return "", fmt.Errorf("Unit %q not recognised.", unit)
	}
	def, _ := length.DefinitiveUnit(unit)
	return def, nil
}

// ScoringSystem returns the scoring system of this target.
func (t *Target) ScoringSystem() ScoringSystem { return t.scoringSystem }

// Diameter returns the target diameter in metres.
func (t *Target) Diameter() float64 { return t.diameter }

// Distance returns the target distance in metres.
func (t *Target) Distance() float64 { return t.distance }

// NativeDiameter returns diameter in its original unit.
func (t *Target) NativeDiameter() Quantity { return t.nativeDiameter }

// NativeDistance returns distance in its original unit.
func (t *Target) NativeDistance() Quantity { return t.nativeDistance }

// Indoor reports whether the target is marked as indoor.
func (t *Target) Indoor() bool { return t.indoor }

// FaceSpec returns a copy of the target's face spec.
// Returns an error if the target was created as Custom without a valid spec.
func (t *Target) FaceSpec() (FaceSpec, error) {
	if t.faceSpec == nil {
		return nil, fmt.Errorf(
			"Trying to generate face spec for custom target " +
				"but no existing spec found: " +
				"try instantiating with FromFaceSpec instead",
		)
	}
	out := make(FaceSpec, len(t.faceSpec))
	for k, v := range t.faceSpec {
		out[k] = v
	}
	return out, nil
}

// MaxScore returns the maximum score achievable on this target face.
func (t *Target) MaxScore() float64 {
	var max float64
	for _, v := range t.faceSpec {
		if float64(v) > max {
			max = float64(v)
		}
	}
	return max
}

// MinScore returns the minimum score achievable on this target face (excluding miss).
func (t *Target) MinScore() float64 {
	if len(t.faceSpec) == 0 {
		return 0
	}
	min := math.MaxFloat64
	for _, v := range t.faceSpec {
		if float64(v) < min {
			min = float64(v)
		}
	}
	return min
}

// String returns a human-readable representation of the Target.
func (t *Target) String() string {
	d, du := t.nativeDiameter.Value, t.nativeDiameter.Units
	di, diu := t.nativeDistance.Value, t.nativeDistance.Units
	return fmt.Sprintf("Target('%s', (%.6g, '%s'), (%.6g, '%s'), indoor=%v)",
		t.scoringSystem, d, du, di, diu, t.indoor)
}

// Equal reports whether two Targets are equivalent.
func (t *Target) Equal(other *Target) bool {
	if t == other {
		return true
	}
	if other == nil {
		return false
	}
	if t.scoringSystem != other.scoringSystem ||
		t.diameter != other.diameter ||
		t.distance != other.distance ||
		t.nativeDiameter != other.nativeDiameter ||
		t.nativeDistance != other.nativeDistance ||
		t.indoor != other.indoor {
		return false
	}
	// Compare face specs
	if len(t.faceSpec) != len(other.faceSpec) {
		return false
	}
	for k, v := range t.faceSpec {
		if ov, ok := other.faceSpec[k]; !ok || ov != v {
			return false
		}
	}
	return true
}

// GenFaceSpec derives the face specification for supported scoring systems.
// diameter must be in metres.
func GenFaceSpec(system ScoringSystem, diameter float64) (FaceSpec, error) {
	removedRings := map[ScoringSystem]int{
		TenZoneSixRing:      4,
		TenZoneFiveRing:     5,
		TenZoneFiveRingCmpd: 5,
		ElevenZoneSixRing:   4,
		ElevenZoneFiveRing:  5,
		Worcester2Ring:      3,
	}

	missing := removedRings[system]
	spec := make(FaceSpec)

	switch system {
	case FiveZone:
		for n := 1; n <= 10; n += 2 {
			spec[rnd6(float64(n+1)*diameter/10)] = 10 - n
		}

	case TenZone, TenZoneSixRing, TenZoneFiveRing:
		for n := 1; n <= 10-missing; n++ {
			spec[rnd6(float64(n)*diameter/10)] = 11 - n
		}

	case TenZoneCompound, TenZoneFiveRingCmpd:
		spec[rnd6(diameter/20)] = 10
		for n := 2; n <= 10-missing; n++ {
			spec[rnd6(float64(n)*diameter/10)] = 11 - n
		}

	case ElevenZone, ElevenZoneSixRing, ElevenZoneFiveRing:
		spec[rnd6(diameter/20)] = 11
		for n := 1; n <= 10-missing; n++ {
			spec[rnd6(float64(n)*diameter/10)] = 11 - n
		}

	case WAField:
		spec[rnd6(diameter/10)] = 6
		for n := 1; n <= 5; n++ {
			spec[rnd6(float64(n)*diameter/5)] = 6 - n
		}

	case IFAAField:
		for _, n := range []int{1, 3, 5} {
			spec[rnd6(float64(n)*diameter/5)] = 5 - n/2
		}

	case AANationalField:
		for n := 1; n <= 5; n++ {
			spec[rnd6(float64(n)*diameter/5)] = 6 - n
		}

	case BeiterHitMiss:
		spec[diameter] = 1

	case Worcester, Worcester2Ring, IFAAFieldExpert:
		for n := 1; n <= 5-missing; n++ {
			spec[rnd6(float64(n)*diameter/5)] = 6 - n
		}

	default:
		return nil, fmt.Errorf("Scoring system %q is not supported", system)
	}

	return spec, nil
}

// rnd6 rounds a float64 to 6 decimal places, matching Python's round(x, ndigits=6).
func rnd6(x float64) float64 {
	return math.Round(x*1e6) / 1e6
}

// SortedKeys returns the keys of a FaceSpec in ascending order (for deterministic iteration).
func SortedKeys(fs FaceSpec) []float64 {
	keys := make([]float64, 0, len(fs))
	for k := range fs {
		keys = append(keys, k)
	}
	sort.Float64s(keys)
	return keys
}
