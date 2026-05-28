package classifications

import (
	"fmt"
	"math"
	"sync"

	"github.com/jatkinson1000/archeryutils/handicaps"
	"github.com/jatkinson1000/archeryutils/rounds"
)

type indoorGroupData struct {
	classes     []string
	classesLong []string
	classHC     []float64
}

var (
	indoorOnce sync.Once
	indoorDict map[string]indoorGroupData
)

var (
	indoorRoundsOnce sync.Once
	indoorRoundsMap  map[string]*rounds.Round
)

func allIndoorRounds() map[string]*rounds.Round {
	indoorRoundsOnce.Do(func() {
		indoorRoundsMap = make(map[string]*rounds.Round)
		for k, v := range rounds.AGBIndoor() {
			indoorRoundsMap[k] = v
		}
		for k, v := range rounds.WAIndoor() {
			indoorRoundsMap[k] = v
		}
	})
	return indoorRoundsMap
}

func buildIndoorDict() map[string]indoorGroupData {
	indoorOnce.Do(func() {
		agbAgeData := loadAgeData()
		agbBowstyleData := loadBowstyleData()
		classInfo := loadClassesIn()
		classes := classInfo.Classes
		classesLong := classInfo.ClassesLong
		n := len(classes)

		indoorDict = make(map[string]indoorGroupData)

		for _, bowstyle := range IndoorBowstyles {
			for _, gender := range AllGenders {
				for _, age := range AllAges {
					groupname := GroupName(bowstyle, gender, age)
					ageName := age.String()
					ad := agbAgeData[ageName]
					bd := agbBowstyleData[bowstyle.String()]

					ageCat := ad.Step
					delta := GetAgeGenderStep(gender, ageCat, bd.AgeStepIn, bd.GenderStepIn)
					hcs := make([]float64, n)
					for i := range n {
						hcs[i] = bd.DatumIn + delta + float64(i-1)*bd.ClassStepIn
					}

					indoorDict[groupname] = indoorGroupData{
						classes:     classes,
						classesLong: classesLong,
						classHC:     hcs,
					}
				}
			}
		}
	})
	return indoorDict
}

func CoaxIndoorGroup(bowstyle Bowstyle, gender Gender, age Age) Category {
	coaxedBowstyle := bowstyle
	switch bowstyle {
	case Flatbow, Traditional:
		coaxedBowstyle = Barebow
	case CompoundLimited, CompoundBarebow:
		coaxedBowstyle = Compound
	}
	return Category{Bowstyle: coaxedBowstyle, Gender: gender, AgeGroup: age}
}

func getIndoorGroupData(bowstyle Bowstyle, gender Gender, age Age) (indoorGroupData, error) {
	if !isIndoorBowstyle(bowstyle) {
		return indoorGroupData{}, fmt.Errorf(
			"%s is not a recognised bowstyle for indoor classifications", bowstyle)
	}
	if !isValidGender(gender) {
		return indoorGroupData{}, fmt.Errorf(
			"%s is not a recognised gender for indoor classifications", gender)
	}
	if !isValidAge(age) {
		return indoorGroupData{}, fmt.Errorf(
			"%s is not a recognised age group for indoor classifications", age)
	}
	dict := buildIndoorDict()
	groupname := GroupName(bowstyle, gender, age)
	if gd, ok := dict[groupname]; ok {
		return gd, nil
	}
	return indoorGroupData{}, fmt.Errorf("no indoor data for group %q", groupname)
}

func isIndoorBowstyle(b Bowstyle) bool {
	for _, ob := range IndoorBowstyles {
		if b == ob {
			return true
		}
	}
	return false
}

// CalculateIndoorClassification returns the classification string for a score.
func CalculateIndoorClassification(
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

	scores, err := IndoorClassificationScores(archeryRound, bowstyle, gender, age, strictRounds)
	if err != nil {
		return "", err
	}

	gd, err := getIndoorGroupData(bowstyle, gender, age)
	if err != nil {
		return "", err
	}

	for i, classname := range gd.classes {
		classscore := float64(scores[i])
		if classscore < 0 || classscore > score {
			continue
		}
		return classname, nil
	}
	return "UC", nil
}

// IndoorClassificationScores returns score thresholds for each class (descending).
// -9999 indicates the class is not achievable on this round.
func IndoorClassificationScores(
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
	strictRounds bool,
) ([]int, error) {
	gd, err := getIndoorGroupData(bowstyle, gender, age)
	if err != nil {
		return nil, err
	}

	allRounds := allIndoorRounds()
	roundname := archeryRound.Codename

	if strictRounds {
		if _, ok := allRounds[roundname]; !ok {
			return nil, fmt.Errorf(
				"This round is not recognised for indoor classification. "+
					"Please select an appropriate option. (codename=%q)", roundname)
		}
		if bowstyle == Compound {
			roundname = CompoundCodename(roundname)
		}
		archeryRound = allRounds[StripSpots(roundname)]
	}

	hcScheme := handicaps.MustScheme("AGB")
	n := len(gd.classes)
	classScores := make([]int, n)
	for i := range n {
		s := handicaps.ScoreForRound(hcScheme, gd.classHC[i], archeryRound, 0, true)
		classScores[i] = int(s)
	}

	// Gap/max-score handling: check score at floor(hc)+1
	for i, hc := range gd.classHC {
		nextScore := int(handicaps.ScoreForRound(hcScheme, math.Floor(hc)+1, archeryRound, 0, true))
		if nextScore == classScores[i] {
			if classScores[i] == int(archeryRound.MaxScore()) {
				classScores[i] = -9999
			} else {
				classScores[i]++
			}
		}
	}

	return classScores, nil
}
