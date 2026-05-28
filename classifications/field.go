package classifications

import (
	"fmt"
	"strings"
	"sync"

	"github.com/jatkinson1000/archeryutils/handicaps"
	"github.com/jatkinson1000/archeryutils/rounds"
)

type fieldGroupData struct {
	classes     []string
	classesLong []string
	classHC     []float64
	maxDistance float64
	minDists    []float64
}

var (
	fieldOnce sync.Once
	fieldDict map[string]fieldGroupData
)

var (
	fieldRoundsOnce sync.Once
	fieldRoundsMap  map[string]*rounds.Round
)

// FieldAges lists age groups valid for field classification (no Under21).
var FieldAges = []Age{Over50, Adult, Under18, Under16, Under15, Under14, Under12}

// SightedBowstyles are those with sights (use red peg distances).
var SightedBowstyles = []Bowstyle{Compound, Recurve, CompoundLimited}

func allFieldRounds() map[string]*rounds.Round {
	fieldRoundsOnce.Do(func() {
		fieldRoundsMap = make(map[string]*rounds.Round)
		for k, v := range rounds.WAField() {
			fieldRoundsMap[k] = v
		}
	})
	return fieldRoundsMap
}

func isSighted(b Bowstyle) bool {
	for _, s := range SightedBowstyles {
		if b == s {
			return true
		}
	}
	return false
}

func isFieldBowstyle(b Bowstyle) bool {
	for _, fb := range FieldBowstyles {
		if b == fb {
			return true
		}
	}
	return false
}

func isFieldAge(a Age) bool {
	for _, fa := range FieldAges {
		if a == fa {
			return true
		}
	}
	return false
}

func assignDistsField(bowstyle Bowstyle, ad AgeData) ([]float64, float64) {
	var minD, maxD float64
	if isSighted(bowstyle) {
		minD = ad.Sighted[0]
		maxD = ad.Sighted[1]
	} else {
		minD = ad.Unsighted[0]
		maxD = ad.Unsighted[1]
	}

	const nClasses = 9
	minDists := make([]float64, nClasses)
	for i := 0; i < 6; i++ {
		minDists[i] = minD
	}
	for i := 0; i < 3; i++ {
		v := minD - 10*float64(i+1)
		if v < 30 {
			v = 30
		}
		minDists[6+i] = v
	}
	return minDists, maxD
}

func buildFieldDict() map[string]fieldGroupData {
	fieldOnce.Do(func() {
		agbAgeData := loadAgeData()
		agbBowstyleData := loadBowstyleData()
		classInfo := loadClassesOut() // field reuses outdoor class names
		classes := classInfo.Classes
		classesLong := classInfo.ClassesLong
		n := len(classes)

		fieldDict = make(map[string]fieldGroupData)

		for _, bowstyle := range AllBowstyles {
			for _, gender := range AllGenders {
				for _, age := range FieldAges {
					groupname := GroupName(bowstyle, gender, age)
					ageName := age.String()
					ad := agbAgeData[ageName]
					bd := agbBowstyleData[bowstyle.String()]

					minDists, maxDistance := assignDistsField(bowstyle, ad)

					ageCat := ad.Step
					delta := GetAgeGenderStep(gender, ageCat, bd.AgeStepField, bd.GenderStepField)
					hcs := make([]float64, n)
					for i := range n {
						hcs[i] = bd.DatumField + delta + float64(i-2)*bd.ClassStepField
					}

					fieldDict[groupname] = fieldGroupData{
						classes:     classes,
						classesLong: classesLong,
						classHC:     hcs,
						maxDistance: maxDistance,
						minDists:    minDists,
					}
				}
			}
		}
	})
	return fieldDict
}

func CoaxFieldGroup(bowstyle Bowstyle, gender Gender, age Age) Category {
	coaxedAge := age
	if age == Under21 {
		coaxedAge = Adult
	}
	return Category{Bowstyle: bowstyle, Gender: gender, AgeGroup: coaxedAge}
}

func getFieldGroupData(bowstyle Bowstyle, gender Gender, age Age) (fieldGroupData, error) {
	if !isFieldBowstyle(bowstyle) {
		return fieldGroupData{}, fmt.Errorf(
			"%s is not a recognised bowstyle for field classifications", bowstyle)
	}
	if !isValidGender(gender) {
		return fieldGroupData{}, fmt.Errorf(
			"%s is not a recognised gender for field classifications", gender)
	}
	if !isFieldAge(age) {
		return fieldGroupData{}, fmt.Errorf(
			"%s is not a recognised age group for field classifications", age)
	}
	dict := buildFieldDict()
	groupname := GroupName(bowstyle, gender, age)
	if gd, ok := dict[groupname]; ok {
		return gd, nil
	}
	return fieldGroupData{}, fmt.Errorf("no field data for group %q", groupname)
}

// normaliseFieldRound replaces unmarked/mixed with marked equivalent.
func normaliseFieldRound(roundname string) string {
	roundname = strings.ReplaceAll(roundname, "unmarked", "marked")
	roundname = strings.ReplaceAll(roundname, "mixed", "marked")
	return roundname
}

// CalculateFieldClassification returns the classification string for a score.
func CalculateFieldClassification(
	score float64,
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
	strictRounds, strictDistance bool,
) (string, error) {
	if strictRounds {
		allRounds := allFieldRounds()
		normName := normaliseFieldRound(archeryRound.Codename)
		if r, ok := allRounds[normName]; ok {
			archeryRound = r
		} else {
			return "", fmt.Errorf(
				"This round is not recognised for field classification. (codename=%q)", archeryRound.Codename)
		}
	}

	if score < 0 || score > archeryRound.MaxScore() {
		return "", fmt.Errorf(
			"Invalid score of %.0f for a %s. Should be in range 0-%.0f.",
			score, archeryRound.Name, archeryRound.MaxScore(),
		)
	}

	scores, err := FieldClassificationScores(archeryRound, bowstyle, gender, age, strictRounds, strictDistance)
	if err != nil {
		return "", err
	}

	gd, err := getFieldGroupData(bowstyle, gender, age)
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

// FieldClassificationScores returns score thresholds for each class (descending).
// -9999 indicates the class is not achievable on this round.
func FieldClassificationScores(
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
	strictRounds, strictDistance bool,
) ([]int, error) {
	gd, err := getFieldGroupData(bowstyle, gender, age)
	if err != nil {
		return nil, err
	}

	allRounds := allFieldRounds()
	roundname := archeryRound.Codename

	if strictRounds {
		normName := normaliseFieldRound(roundname)
		if r, ok := allRounds[normName]; ok {
			archeryRound = r
			roundname = normName
		} else {
			return nil, fmt.Errorf(
				"This round is not recognised for field classification. (codename=%q)", roundname)
		}
	}

	hcScheme := handicaps.MustScheme("AGB")
	n := len(gd.classes)
	classScores := make([]int, n)
	for i := range n {
		s := handicaps.ScoreForRound(hcScheme, gd.classHC[i], archeryRound, 0, true)
		classScores[i] = int(s)
	}

	// MB+ requires 24-target round
	if strictRounds && !strings.Contains(archeryRound.Codename, "wa_field_24_") {
		classScores[0] = -9999
		classScores[1] = -9999
		classScores[2] = -9999
	}

	// Distance restrictions
	if strictDistance {
		roundMaxDist := archeryRound.MaxDistance().Value
		for i := range classScores {
			if gd.minDists[i] > roundMaxDist {
				classScores[i] = -9999
			}
			if gd.maxDistance < roundMaxDist {
				classScores[i] = -9999
			}
		}
	}

	return classScores, nil
}
