package handicaps

import "math"

// HandicapAA implements the original Archery Australia handicap scheme by J. Park.
type HandicapAA struct {
	ang0 float64
	k0   float64
	ks   float64
	kd   float64
}

// NewHandicapAA creates an AA scheme with default parameters.
func NewHandicapAA() *HandicapAA {
	return &HandicapAA{ang0: 1e-3, k0: 2.37, ks: 0.027, kd: 0.004}
}

func (h *HandicapAA) Name() string               { return "AA" }
func (h *HandicapAA) Descending() bool            { return false }
func (h *HandicapAA) ScaleBounds() (float64, float64) { return -250, 175 }
func (h *HandicapAA) MaxScoreRoundingLim() float64 { return 0.5 }
func (h *HandicapAA) ArrowDiameter(indoor bool) float64 {
	if indoor {
		return 9.3e-3
	}
	return 5.0e-3
}
func (h *HandicapAA) RoundScore(score float64) float64 { return math.Round(score) }

func (h *HandicapAA) SigmaT(handicap, dist float64) float64 {
	return math.Sqrt2 * h.ang0 * math.Exp(h.k0-h.ks*handicap+h.kd*dist)
}

// HandicapAA2 implements the updated (2014) Archery Australia handicap scheme.
type HandicapAA2 struct {
	ang0 float64
	k0   float64
	ks   float64
	f1   float64
	f2   float64
	d0   float64
}

// NewHandicapAA2 creates an AA2 scheme with default parameters.
func NewHandicapAA2() *HandicapAA2 {
	return &HandicapAA2{ang0: 1e-3, k0: 2.57, ks: 0.027, f1: 0.815, f2: 0.185, d0: 50.0}
}

func (h *HandicapAA2) Name() string               { return "AA2" }
func (h *HandicapAA2) Descending() bool            { return false }
func (h *HandicapAA2) ScaleBounds() (float64, float64) { return -250, 175 }
func (h *HandicapAA2) MaxScoreRoundingLim() float64 { return 0.5 }
func (h *HandicapAA2) ArrowDiameter(indoor bool) float64 {
	if indoor {
		return 9.3e-3
	}
	return 5.0e-3
}
func (h *HandicapAA2) RoundScore(score float64) float64 { return math.Round(score) }

func (h *HandicapAA2) SigmaT(handicap, dist float64) float64 {
	return math.Sqrt2 * h.ang0 * math.Exp(h.k0-h.ks*handicap) * (h.f1 + h.f2*dist/h.d0)
}
