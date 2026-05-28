package handicaps

import "math"

// HandicapAGB implements the 2023 Archery GB handicap scheme.
type HandicapAGB struct {
	datum float64
	step  float64
	ang0  float64
	kd    float64
}

// NewHandicapAGB creates an AGB scheme with default parameters.
func NewHandicapAGB() *HandicapAGB {
	return &HandicapAGB{datum: 6.0, step: 3.5, ang0: 5e-4, kd: 0.00365}
}

func (h *HandicapAGB) Name() string               { return "AGB" }
func (h *HandicapAGB) Descending() bool            { return true }
func (h *HandicapAGB) ScaleBounds() (float64, float64) { return -75, 300 }
func (h *HandicapAGB) MaxScoreRoundingLim() float64 { return 1.0 }
func (h *HandicapAGB) ArrowDiameter(indoor bool) float64 {
	if indoor {
		return 9.3e-3
	}
	return 5.5e-3
}
func (h *HandicapAGB) RoundScore(score float64) float64 { return math.Ceil(score) }

func (h *HandicapAGB) SigmaT(handicap, dist float64) float64 {
	return h.ang0 * math.Pow(1.0+h.step/100.0, handicap+h.datum) * math.Exp(h.kd*dist)
}

// HandicapAGBold implements the pre-2023 Archery GB handicap scheme by D. Lane.
type HandicapAGBold struct {
	datum float64
	step  float64
	ang0  float64
	k1    float64
	k2    float64
	k3    float64
	p1    float64
}

// NewHandicapAGBold creates an AGBold scheme with default parameters.
func NewHandicapAGBold() *HandicapAGBold {
	return &HandicapAGBold{
		datum: 12.9, step: 3.6, ang0: 5e-4,
		k1: 1.429e-6, k2: 1.07, k3: 4.3, p1: 2.0,
	}
}

func (h *HandicapAGBold) Name() string               { return "AGBold" }
func (h *HandicapAGBold) Descending() bool            { return true }
func (h *HandicapAGBold) ScaleBounds() (float64, float64) { return -75, 300 }
func (h *HandicapAGBold) MaxScoreRoundingLim() float64 { return 0.5 }
func (h *HandicapAGBold) ArrowDiameter(_ bool) float64 { return 7.14e-3 }
func (h *HandicapAGBold) RoundScore(score float64) float64 {
	return math.Round(score)
}

func (h *HandicapAGBold) SigmaT(handicap, dist float64) float64 {
	kFactor := h.k1 * math.Pow(h.k2, handicap+h.k3)
	fFactor := 1.0 + kFactor*math.Pow(dist, h.p1)
	return h.ang0 * math.Pow(1.0+h.step/100.0, handicap+h.datum) * fFactor
}
