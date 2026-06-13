package classifications

import (
	"fmt"
	"strings"
	"sync"

	"github.com/retbrown/archeryutils/handicaps"
	"github.com/retbrown/archeryutils/rounds"
)

type oldIndoorGroupData struct {
	classes []string
	classHC []float64
}

var (
	oldIndoorOnce sync.Once
	oldIndoorDict map[string]oldIndoorGroupData
)

// OldIndoorBowstyles lists bowstyles eligible for old indoor classification.
var OldIndoorBowstyles = []Bowstyle{Compound, Recurve}

func buildOldIndoorDict() map[string]oldIndoorGroupData {
	oldIndoorOnce.Do(func() {
		classes := []string{"A", "B", "C", "D", "E", "F", "G", "H"}

		type key struct {
			b Bowstyle
			g Gender
		}
		hcTable := map[key][]float64{
			{Compound, Male}:   {5, 12, 24, 37, 49, 62, 73, 79},
			{Compound, Female}: {12, 18, 30, 43, 55, 67, 79, 83},
			{Recurve, Male}:    {14, 21, 33, 46, 58, 70, 80, 85},
			{Recurve, Female}:  {21, 27, 39, 51, 64, 75, 85, 90},
		}

		oldIndoorDict = make(map[string]oldIndoorGroupData)
		for k, hcs := range hcTable {
			hcsCopy := make([]float64, len(hcs))
			copy(hcsCopy, hcs)
			groupname := GroupName(k.b, k.g, Adult)
			oldIndoorDict[groupname] = oldIndoorGroupData{
				classes: classes,
				classHC: hcsCopy,
			}
		}
	})
	return oldIndoorDict
}

func CoaxOldIndoorGroup(bowstyle Bowstyle, gender Gender, _ Age) Category {
	coaxedBowstyle := Recurve
	switch bowstyle {
	case Compound, CompoundLimited, CompoundBarebow:
		coaxedBowstyle = Compound
	}
	return Category{Bowstyle: coaxedBowstyle, Gender: gender, AgeGroup: Adult}
}

func isOldIndoorBowstyle(b Bowstyle) bool {
	for _, ob := range OldIndoorBowstyles {
		if b == ob {
			return true
		}
	}
	return false
}

func getOldIndoorGroupData(bowstyle Bowstyle, gender Gender, age Age) (oldIndoorGroupData, error) {
	if !isOldIndoorBowstyle(bowstyle) {
		return oldIndoorGroupData{}, fmt.Errorf(
			"%s is not a recognised bowstyle for old indoor classifications", bowstyle)
	}
	if !isValidGender(gender) {
		return oldIndoorGroupData{}, fmt.Errorf(
			"%s is not a recognised gender for old indoor classifications", gender)
	}
	if age != Adult {
		return oldIndoorGroupData{}, fmt.Errorf(
			"%s is not a recognised age group for old indoor classifications (only Adult)", age)
	}
	dict := buildOldIndoorDict()
	groupname := GroupName(bowstyle, gender, age)
	if gd, ok := dict[groupname]; ok {
		return gd, nil
	}
	return oldIndoorGroupData{}, fmt.Errorf("no old indoor data for group %q", groupname)
}

// CalculateOldIndoorClassification returns the classification string for a score.
func CalculateOldIndoorClassification(
	score float64,
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
	strictRounds bool,
) (string, error) {
	if score < 0 || score > archeryRound.MaxScore() {
		return "", fmt.Errorf(
			"Invalid score of %.0f for a %s. Should be in range 0-%.0f.",
			score, archeryRound.Name, archeryRound.MaxScore(),
		)
	}

	scores, err := OldIndoorClassificationScores(archeryRound, bowstyle, gender, age, strictRounds)
	if err != nil {
		return "", err
	}

	gd, err := getOldIndoorGroupData(bowstyle, gender, age)
	if err != nil {
		return "", err
	}

	for i, classname := range gd.classes {
		if float64(scores[i]) > score {
			continue
		}
		return classname, nil
	}
	return "UC", nil
}

// OldIndoorClassificationScores returns score thresholds for each class (descending).
func OldIndoorClassificationScores(
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
	strictRounds bool,
) ([]int, error) {
	gd, err := getOldIndoorGroupData(bowstyle, gender, age)
	if err != nil {
		return nil, err
	}

	allRounds := allIndoorRounds()
	roundname := archeryRound.Codename

	if strictRounds {
		if _, ok := allRounds[roundname]; !ok {
			return nil, fmt.Errorf(
				"This round is not recognised for old indoor classification. "+
					"Please select an appropriate option. (codename=%q)", roundname)
		}
		if bowstyle == Compound {
			roundname = CompoundCodename(roundname)
			if r, ok := allRounds[roundname]; ok {
				archeryRound = r
			}
		}
		// Strip spots only for the specific AGB rounds that require full-face enforcement
		for _, name := range []string{"portsmouth", "worcester", "bray_i", "bray_ii"} {
			if strings.Contains(roundname, name) {
				stripped := StripSpots(roundname)
				if r, ok := allRounds[stripped]; ok {
					archeryRound = r
				}
				break
			}
		}
	}

	hcScheme := handicaps.MustScheme("AGBold")
	n := len(gd.classes)
	classScores := make([]int, n)
	for i := range n {
		s := handicaps.ScoreForRound(hcScheme, gd.classHC[i], archeryRound, 0, true)
		classScores[i] = int(s)
	}

	return classScores, nil
}
