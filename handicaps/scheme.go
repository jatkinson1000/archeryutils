// Package handicaps provides archery handicap calculations for multiple schemes.
package handicaps

import (
	"fmt"
	"math"
	"sort"

	"github.com/jatkinson1000/archeryutils/rounds"
	"github.com/jatkinson1000/archeryutils/targets"
)

// Scheme is the interface implemented by all handicap systems.
type Scheme interface {
	// SigmaT returns the angular deviation in radians for the given handicap and distance.
	SigmaT(handicap, dist float64) float64
	// Descending reports whether a lower handicap is better.
	Descending() bool
	// ScaleBounds returns the reasonable lower and upper bound on the handicap scale.
	ScaleBounds() (lo, hi float64)
	// MaxScoreRoundingLim is the limit used when searching for the max-score handicap.
	MaxScoreRoundingLim() float64
	// ArrowDiameter returns the arrow diameter in metres appropriate for the target.
	ArrowDiameter(indoor bool) float64
	// RoundScore applies the scheme-specific rounding to a raw score.
	RoundScore(score float64) float64
	// Name returns the scheme's canonical name.
	Name() string
}

// SigmaR returns the radial standard deviation (metres) for a handicap and distance.
func SigmaR(s Scheme, handicap, dist float64) float64 {
	return dist * s.SigmaT(handicap, dist)
}

// arrowDiam resolves the arrow diameter: uses arwD when > 0, otherwise scheme default.
func arrowDiam(s Scheme, indoor bool, arwD float64) float64 {
	if arwD > 0 {
		return arwD
	}
	return s.ArrowDiameter(indoor)
}

// ArrowScore returns the expected average arrow score for a given target and handicap.
func ArrowScore(s Scheme, handicap float64, target *targets.Target, arwD float64) float64 {
	d := arrowDiam(s, target.Indoor(), arwD)
	arwRad := d / 2.0
	sigR := SigmaR(s, handicap, target.Distance())
	spec, _ := target.FaceSpec()
	return sBar(spec, arwRad, sigR)
}

// sBar computes the expected score per arrow given target face spec, arrow radius, and sigma_r.
func sBar(spec targets.FaceSpec, arwRad, sigR float64) float64 {
	// Sort ring diameters ascending
	keys := make([]float64, 0, len(spec))
	for k := range spec {
		keys = append(keys, k)
	}
	sort.Float64s(keys)

	// Scores in ascending ring-size order, then 0 appended
	ringScores := make([]float64, 0, len(keys)+1)
	for _, k := range keys {
		ringScores = append(ringScores, float64(spec[k]))
	}
	ringScores = append(ringScores, 0)

	maxScore := ringScores[0]
	var total float64
	for i, ringDiam := range keys {
		scoreDrop := ringScores[i] - ringScores[i+1]
		ratio := (arwRad + ringDiam/2.0) / sigR
		total += scoreDrop * math.Exp(-(ratio * ratio))
	}
	return maxScore - total
}

// ScoreForPassRaw returns the unrounded expected score for a single pass.
func ScoreForPassRaw(s Scheme, handicap float64, pass *rounds.Pass, arwD float64) float64 {
	return float64(pass.NArrows) * ArrowScore(s, handicap, pass.Target, arwD)
}

// ScoreForRound returns the expected score for a round at the given handicap.
// If rounded is true, the scheme's rounding function is applied.
func ScoreForRound(s Scheme, handicap float64, rnd *rounds.Round, arwD float64, rounded bool) float64 {
	var total float64
	for _, p := range rnd.Passes {
		total += ScoreForPassRaw(s, handicap, p, arwD)
	}
	if rounded {
		return s.RoundScore(total)
	}
	return total
}

// ScoreForPasses returns the expected score per pass (unrounded, then optionally rounded).
func ScoreForPasses(s Scheme, handicap float64, rnd *rounds.Round, arwD float64, rounded bool) []float64 {
	out := make([]float64, len(rnd.Passes))
	for i, p := range rnd.Passes {
		raw := ScoreForPassRaw(s, handicap, p, arwD)
		if rounded {
			out[i] = s.RoundScore(raw)
		} else {
			out[i] = raw
		}
	}
	return out
}

// HandicapFromScore derives the handicap for a given score on a given round.
// arwD ≤ 0 means "use scheme default".
// intPrec=true returns an integer-resolution handicap.
func HandicapFromScore(s Scheme, score float64, rnd *rounds.Round, arwD float64, intPrec bool) (float64, error) {
	maxScore := rnd.MaxScore()
	if score > maxScore {
		return 0, fmt.Errorf(
			"The score of %v provided is greater than the maximum of %v for a %s.",
			score, maxScore, rnd.Name,
		)
	}
	if score <= 0 {
		return 0, fmt.Errorf(
			"The score of %v provided is less than or equal to zero so cannot have a handicap.",
			score,
		)
	}

	if score == maxScore {
		return getMaxScoreHandicap(s, rnd, arwD, intPrec)
	}

	handicap := rootfindScoreHandicap(s, score, rnd, arwD)

	if intPrec {
		if s.Descending() {
			handicap = math.Ceil(handicap)
		} else {
			handicap = math.Floor(handicap)
		}

		var hstep float64 = 1.0
		if !s.Descending() {
			hstep = -1.0
		}
		for {
			handicap += hstep
			sc := ScoreForRound(s, handicap, rnd, arwD, true)
			if sc < score {
				handicap -= hstep
				break
			}
		}
	}

	return handicap, nil
}

// getMaxScoreHandicap finds the handicap that produces the maximum score.
func getMaxScoreHandicap(s Scheme, rnd *rounds.Round, arwD float64, intPrec bool) (float64, error) {
	maxScore := rnd.MaxScore()
	lo, hi := s.ScaleBounds()

	var handicap, deltaHC float64
	if s.Descending() {
		handicap = lo
		deltaHC = 1.0
	} else {
		handicap = hi
		deltaHC = -1.0
	}

	target := maxScore - s.MaxScoreRoundingLim()

	// Coarse pass: step until score drops below target
	for ScoreForRound(s, handicap, rnd, arwD, false) > target {
		handicap += deltaHC
	}

	// Step back and refine
	handicap -= 1.01 * deltaHC
	deltaHC /= 100

	for ScoreForRound(s, handicap, rnd, arwD, false) > target {
		handicap += deltaHC
	}
	handicap -= deltaHC // undo overshoot

	if intPrec {
		if s.Descending() {
			return math.Floor(handicap), nil
		}
		return math.Ceil(handicap), nil
	}
	// Non-integer precision warning: just return the value
	// (Python emits a UserWarning here; Go callers can check the returned float)
	return handicap, nil
}

// rootfindScoreHandicap implements Brent's rootfinding method, translated from the
// Python source (itself ported from SciPy's brentq.c) with identical convergence
// behaviour (xtol=1e-16, rtol=0, 25 iterations).
func rootfindScoreHandicap(s Scheme, score float64, rnd *rounds.Round, arwD float64) float64 {
	lo, hi := s.ScaleBounds()

	fRoot := func(hc float64) float64 {
		return ScoreForRound(s, hc, rnd, arwD, false) - score
	}

	f0 := fRoot(lo)
	f1 := fRoot(hi)

	const xtol = 1e-16
	const rtol = 0.0

	var xpre, xcur, fpre, fcur float64
	if math.Abs(f1) <= math.Abs(f0) {
		xcur, xpre = hi, lo
		fcur, fpre = f1, f0
	} else {
		xpre, xcur = hi, lo
		fpre, fcur = f1, f0
	}

	var xblk, fblk, scur, spre float64
	handicap := xcur

	for range 25 {
		if fpre != 0 && fcur != 0 && sign(fpre) != sign(fcur) {
			xblk, fblk = xpre, fpre
			spre = xcur - xpre
			scur = xcur - xpre
		}
		if math.Abs(fblk) < math.Abs(fcur) {
			xpre, xcur, xblk = xcur, xblk, xcur
			fpre, fcur, fblk = fcur, fblk, fcur
		}

		delta := (xtol + rtol*math.Abs(xcur)) / 2.0
		sbis := (xblk - xcur) / 2.0

		if fcur == 0 || math.Abs(sbis) < delta {
			handicap = xcur
			break
		}

		if math.Abs(spre) > delta && math.Abs(fcur) < math.Abs(fpre) {
			var stry float64
			if xpre == xblk {
				denom := fcur - xpre
				if denom == 0 {
					denom = xtol
				}
				stry = -fcur * (xcur - xpre) / denom
			} else {
				dpre := (fpre - fcur) / (xpre - xcur)
				dblk := (fblk - fcur) / (xblk - xcur)
				stry = -fcur * (fblk - fpre) / (fblk*dpre - fpre*dblk)
			}
			if 2*math.Abs(stry) < min(math.Abs(spre), 3*math.Abs(sbis)-delta) {
				spre = scur
				scur = stry
			} else {
				spre = sbis
				scur = sbis
			}
		} else {
			spre = sbis
			scur = sbis
		}

		xpre = xcur
		fpre = fcur
		if math.Abs(scur) > delta {
			xcur += scur
		} else if sbis > 0 {
			xcur += delta
		} else {
			xcur -= delta
		}

		fcur = fRoot(xcur)
		handicap = xcur
	}

	return handicap
}

func sign(x float64) float64 {
	if x < 0 {
		return -1
	}
	if x > 0 {
		return 1
	}
	return 0
}
