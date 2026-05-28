package classifications

import (
	"fmt"
	"sync"

	"github.com/jatkinson1000/archeryutils/handicaps"
	"github.com/jatkinson1000/archeryutils/rounds"
)

// outdoorGroupData stores the classification config for one outdoor category.
type outdoorGroupData struct {
	classes       []string
	classesLong   []string
	classHC       []float64
	minDists      []float64
	maxDists      []float64
	prestigeRounds []string
}

var (
	outdoorOnce sync.Once
	outdoorDict map[string]outdoorGroupData
)

// outdoorRoundsOnce loads the outdoor round set once.
var (
	outdoorRoundsOnce sync.Once
	outdoorRoundsMap  map[string]*rounds.Round
)

func allOutdoorRounds() map[string]*rounds.Round {
	outdoorRoundsOnce.Do(func() {
		outdoorRoundsMap = make(map[string]*rounds.Round)
		for k, v := range rounds.AGBOutdoorImperial() {
			outdoorRoundsMap[k] = v
		}
		for k, v := range rounds.AGBOutdoorMetric() {
			outdoorRoundsMap[k] = v
		}
		for k, v := range rounds.WAOutdoor() {
			outdoorRoundsMap[k] = v
		}
	})
	return outdoorRoundsMap
}

func buildOutdoorDict() map[string]outdoorGroupData {
	outdoorOnce.Do(func() {
		agbAgeData := loadAgeData()
		agbBowstyleData := loadBowstyleData()
		classInfo := loadClassesOut()
		classes := classInfo.Classes
		classesLong := classInfo.ClassesLong
		n := len(classes)

		outdoorDict = make(map[string]outdoorGroupData)

		for _, bowstyle := range OutdoorBowstyles {
			for _, gender := range AllGenders {
				for _, age := range AllAges {
					groupname := GroupName(bowstyle, gender, age)
					ageName := age.String()
					ad := agbAgeData[ageName]
					bd := agbBowstyleData[bowstyle.String()]

					maxDists := maxDistsForGender(ad, gender)
					ageCat := ad.Step

					delta := GetAgeGenderStep(gender, ageCat, bd.AgeStepOut, bd.GenderStepOut)
					hcs := classHCs(bd.DatumOut, delta, bd.ClassStepOut, n)
					minDists := assignMinDistOutdoor(gender, age, maxDists)
					prestige := assignOutdoorPrestige(bowstyle, gender, age, maxDists)

					outdoorDict[groupname] = outdoorGroupData{
						classes:        classes,
						classesLong:    classesLong,
						classHC:        hcs,
						minDists:       minDists,
						maxDists:       maxDists,
						prestigeRounds: prestige,
					}
				}
			}
		}
	})
	return outdoorDict
}

// stdDists is the standard outdoor distance ladder in metres.
var stdDists = []float64{90, 70, 60, 50, 40, 30, 20, 15}

func assignMinDistOutdoor(gender Gender, age Age, maxDists []float64) []float64 {
	minMaxDist := minFloats(maxDists)
	maxDistIdx := distIndex(stdDists, minMaxDist)
	if maxDistIdx < 0 {
		maxDistIdx = 0
	}

	// U15 males and younger use one index pattern; everyone else uses another
	youngMale := age == Under15 || age == Under14 || age == Under12
	var idxs []int
	if gender == Male && !youngMale {
		idxs = []int{0, 0, 0, 0, 1, 2, 3, 4, 5}
	} else {
		idxs = []int{0, 0, 0, 0, 0, 1, 2, 3, 4}
	}

	return takeClip(stdDists, idxs, maxDistIdx)
}

func assignOutdoorPrestige(bowstyle Bowstyle, gender Gender, age Age, maxDists []float64) []string {
	prestigeImperial := []string{
		"york", "hereford", "bristol_i", "bristol_ii", "bristol_iii", "bristol_iv", "bristol_v",
	}
	prestigeMetric := []string{
		"wa1440_90", "wa1440_90_small", "wa1440_70", "wa1440_70_small",
		"wa1440_60", "wa1440_60_small",
		"metric_i", "metric_ii", "metric_iii", "metric_iv", "metric_v",
	}
	prestige720 := []string{
		"wa720_70", "wa720_60", "metric_122_50", "metric_122_40", "metric_122_30",
	}
	prestige720Compound := []string{
		"wa720_50_c", "metric_80_40", "metric_80_30",
	}
	prestige720Barebow := []string{
		"wa720_50_b", "metric_122_50", "metric_122_40", "metric_122_30",
	}

	var prestige []string
	var distCheck []string

	switch bowstyle {
	case Compound:
		prestige = append(prestige, prestige720Compound[0])
		distCheck = append(distCheck, prestige720Compound[1:]...)
	case Barebow:
		prestige = append(prestige, prestige720Barebow[0])
		distCheck = append(distCheck, prestige720Barebow[1:]...)
	default:
		prestige = append(prestige, prestige720[0])
		distCheck = append(distCheck, prestige720[1:]...)
		if gender == Male {
			if age == Over50 || age == Under18 {
				prestige = append(prestige, prestige720[1])
			} else if age == Under16 {
				prestige = append(prestige, prestige720[2])
			}
		}
	}

	distCheck = append(distCheck, prestigeImperial...)
	distCheck = append(distCheck, prestigeMetric...)

	minMaxDist := minFloats(maxDists)
	allRounds := allOutdoorRounds()
	for _, roundname := range distCheck {
		if r, ok := allRounds[roundname]; ok {
			if r.MaxDistance().Value >= minMaxDist {
				prestige = append(prestige, roundname)
			}
		}
	}

	return prestige
}

// CoaxOutdoorGroup maps non-outdoor bowstyles to their outdoor equivalent.
func CoaxOutdoorGroup(bowstyle Bowstyle, gender Gender, age Age) Category {
	coaxedBowstyle := bowstyle
	switch bowstyle {
	case Flatbow, Traditional:
		coaxedBowstyle = Barebow
	case CompoundLimited, CompoundBarebow:
		coaxedBowstyle = Compound
	}
	return Category{Bowstyle: coaxedBowstyle, Gender: gender, AgeGroup: age}
}

func isOutdoorBowstyle(b Bowstyle) bool {
	for _, ob := range OutdoorBowstyles {
		if b == ob {
			return true
		}
	}
	return false
}

func isValidGender(g Gender) bool {
	return g == Male || g == Female
}

func isValidAge(a Age) bool {
	for _, age := range AllAges {
		if a == age {
			return true
		}
	}
	return false
}

func getOutdoorGroupData(bowstyle Bowstyle, gender Gender, age Age) (outdoorGroupData, error) {
	if !isOutdoorBowstyle(bowstyle) {
		return outdoorGroupData{}, fmt.Errorf(
			"%s is not a recognised bowstyle for outdoor classifications", bowstyle)
	}
	if !isValidGender(gender) {
		return outdoorGroupData{}, fmt.Errorf(
			"%s is not a recognised gender for outdoor classifications", gender)
	}
	if !isValidAge(age) {
		return outdoorGroupData{}, fmt.Errorf(
			"%s is not a recognised age group for outdoor classifications", age)
	}
	dict := buildOutdoorDict()
	groupname := GroupName(bowstyle, gender, age)
	if gd, ok := dict[groupname]; ok {
		return gd, nil
	}
	return outdoorGroupData{}, fmt.Errorf("no outdoor data for group %q", groupname)
}

// CalculateOutdoorClassification returns the classification string for a score.
func CalculateOutdoorClassification(
	score float64,
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
	strictRounds, strictDistance bool,
) (string, error) {
	if score < 0 || score > archeryRound.MaxScore() {
		return "", fmt.Errorf(
			"Invalid score of %.0f for a %s. Should be in range 0-%.0f.",
			score, archeryRound.Name, archeryRound.MaxScore(),
		)
	}

	scores, err := OutdoorClassificationScores(archeryRound, bowstyle, gender, age, strictRounds, strictDistance)
	if err != nil {
		return "", err
	}

	gd, err := getOutdoorGroupData(bowstyle, gender, age)
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

// OutdoorClassificationScores returns score thresholds for each class (descending order).
// -9999 indicates the class is not achievable on this round.
func OutdoorClassificationScores(
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
	strictRounds, strictDistance bool,
) ([]int, error) {
	gd, err := getOutdoorGroupData(bowstyle, gender, age)
	if err != nil {
		return nil, err
	}

	allRounds := allOutdoorRounds()

	// Resolve round and codename
	roundname := archeryRound.Codename
	if strictRounds {
		if _, ok := allRounds[roundname]; !ok {
			return nil, fmt.Errorf(
				"This round is not recognised for outdoor classification. "+
					"Please select an appropriate option. (codename=%q)", roundname)
		}
		// Strip spots variant to get base round
		baseCodename := StripSpots(roundname)
		if base, ok := allRounds[baseCodename]; ok {
			archeryRound = base
		}
	}

	hcScheme := handicaps.MustScheme("AGB")

	n := len(gd.classes)
	classScores := make([]int, n)
	for i := range n {
		s := handicaps.ScoreForRound(hcScheme, gd.classHC[i], archeryRound, 0, true)
		classScores[i] = int(s)
	}

	// Prestige round check: non-prestige rounds cannot earn MB or above (classes 0,1,2)
	if strictRounds {
		isPrestige := false
		for _, pr := range gd.prestigeRounds {
			if pr == roundname {
				isPrestige = true
				break
			}
		}
		if !isPrestige {
			classScores[0] = -9999
			classScores[1] = -9999
			classScores[2] = -9999
		}
	}

	// Distance-based eligibility
	if strictDistance {
		isPrestige := false
		if strictRounds {
			for _, pr := range gd.prestigeRounds {
				if pr == roundname {
					isPrestige = true
					break
				}
			}
		}
		if !(strictRounds && isPrestige) {
			roundMaxDist := archeryRound.MaxDistance().Value
			for i := range classScores {
				if gd.minDists[i] > roundMaxDist {
					classScores[i] = -9999
				}
			}
		}
	}

	return classScores, nil
}
