package classifications

import (
	"fmt"
	"math"
	"strings"
)

// GroupName generates a single string identifier for a category.
func GroupName(bowstyle Bowstyle, gender Gender, age Age) string {
	return fmt.Sprintf("%s_%s_%s", age.String(), gender.String(), bowstyle.String())
}

// GetAgeGenderStep calculates the combined age+gender handicap step relative to datum.
func GetAgeGenderStep(gender Gender, ageCat int, ageStep, genderStep float64) float64 {
	const under16Int = 3

	if gender == Female && ageCat == under16Int && ageStep < genderStep {
		return float64(ageCat)*ageStep + ageStep
	}
	if gender == Female && ageCat <= under16Int {
		return genderStep + float64(ageCat)*ageStep
	}
	return float64(ageCat) * ageStep
}

// StripSpots removes spot variant suffixes from a round codename.
func StripSpots(roundname string) string {
	roundname = strings.ReplaceAll(roundname, "_triple", "")
	roundname = strings.ReplaceAll(roundname, "_5_centre", "")
	roundname = strings.ReplaceAll(roundname, "_small", "")
	return roundname
}

// CompoundCodename converts indoor rounds with special compound scoring to their compound variants.
func CompoundCodename(codename string) string {
	conv := map[string]string{
		"bray_i":               "bray_i_compound",
		"bray_i_triple":        "bray_i_compound_triple",
		"bray_ii":              "bray_ii_compound",
		"bray_ii_triple":       "bray_ii_compound_triple",
		"stafford":             "stafford_compound",
		"portsmouth":           "portsmouth_compound",
		"portsmouth_triple":    "portsmouth_compound_triple",
		"vegas":                "vegas_compound",
		"wa18":                 "wa18_compound",
		"wa18_triple":          "wa18_compound_triple",
		"wa25":                 "wa25_compound",
		"wa25_triple":          "wa25_compound_triple",
	}
	if alt, ok := conv[codename]; ok {
		return alt
	}
	return codename
}

// classHCs computes handicap thresholds for each classification in a category.
// datum is the bowstyle datum, deltaHCAgeGender is the combined age+gender offset,
// classStep is the per-classification step, and n is the number of classes.
// The returned slice has len(n) values, one per class (highest class first).
// Classes at index 0,1,2 are EMB/GMB/MB; the rest are Bowman/Archer grades.
// The formula from Python is:
//
//	class_hc[i] = datum + deltaHCAgeGender + (i - 2) * classStep
func classHCs(datum, deltaHCAgeGender, classStep float64, n int) []float64 {
	hcs := make([]float64, n)
	for i := range n {
		hcs[i] = datum + deltaHCAgeGender + float64(i-2)*classStep
	}
	return hcs
}

// minF returns the minimum of two float64 values.
func minF(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}

// minInts returns the minimum of a slice of floats.
func minFloats(xs []float64) float64 {
	if len(xs) == 0 {
		return math.MaxFloat64
	}
	m := xs[0]
	for _, x := range xs[1:] {
		if x < m {
			m = x
		}
	}
	return m
}

// distIndex returns the index of d in dists, or -1.
func distIndex(dists []float64, d float64) int {
	for i, v := range dists {
		if v == d {
			return i
		}
	}
	return -1
}

// takeClip mimics numpy.take(arr, idxs + offset, mode="clip").
func takeClip(arr []float64, idxs []int, offset int) []float64 {
	out := make([]float64, len(idxs))
	for i, idx := range idxs {
		j := idx + offset
		if j < 0 {
			j = 0
		}
		if j >= len(arr) {
			j = len(arr) - 1
		}
		out[i] = arr[j]
	}
	return out
}

// fixRepeatedScores ensures no two adjacent class scores are the same or inverted,
// working from the easiest class upward. A class whose score equals or exceeds
// the class below it is bumped to classBelow+1; if that would exceed maxScore
// the class is marked unachievable (-9999). Classes already at -9999 propagate
// that mark upward.
func fixRepeatedScores(scores []int, maxScore float64) []int {
	for i := len(scores) - 1; i > 0; i-- {
		if scores[i] < 0 {
			scores[i-1] = -9999
		} else if scores[i-1] >= 0 && scores[i-1] <= scores[i] {
			if scores[i] == int(maxScore) {
				scores[i-1] = -9999
			} else {
				scores[i-1] = scores[i] + 1
			}
		}
	}
	return scores
}
