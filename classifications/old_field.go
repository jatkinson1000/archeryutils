package classifications

import (
	"fmt"
	"strings"

	"github.com/jatkinson1000/archeryutils/rounds"
)

type oldFieldGroupData struct {
	classes     []string
	classScores []int
}

// OldFieldClasses are the old (pre-2025) field classification names.
var OldFieldClasses = []string{"GMB", "MB", "B", "1C", "2C", "3C"}

// OldFieldAges lists age groups valid for old field classification.
var OldFieldAges = []Age{Adult, Under18}

// AllFieldBowstyles lists bowstyles eligible for old field classification (all bowstyles).
var AllFieldBowstyles = []Bowstyle{
	Compound, Recurve, Barebow, Longbow, Traditional, Flatbow, CompoundLimited, CompoundBarebow,
}

var oldFieldScoreTable = map[[3]interface{}][]int{
	{Compound, Male, Adult}:          {393, 377, 344, 312, 279, 247},
	{Compound, Female, Adult}:        {376, 361, 330, 299, 268, 237},
	{Recurve, Male, Adult}:           {338, 317, 288, 260, 231, 203},
	{Recurve, Female, Adult}:         {322, 302, 275, 247, 220, 193},
	{Barebow, Male, Adult}:           {328, 307, 279, 252, 224, 197},
	{Barebow, Female, Adult}:         {303, 284, 258, 233, 207, 182},
	{Longbow, Male, Adult}:           {201, 188, 171, 155, 137, 121},
	{Longbow, Female, Adult}:         {152, 142, 129, 117, 103, 91},
	{Traditional, Male, Adult}:       {262, 245, 223, 202, 178, 157},
	{Traditional, Female, Adult}:     {197, 184, 167, 152, 134, 118},
	{Flatbow, Male, Adult}:           {262, 245, 223, 202, 178, 157},
	{Flatbow, Female, Adult}:         {197, 184, 167, 152, 134, 118},
	{CompoundLimited, Male, Adult}:   {338, 317, 288, 260, 231, 203},
	{CompoundLimited, Female, Adult}: {322, 302, 275, 247, 220, 193},
	{CompoundBarebow, Male, Adult}:   {328, 307, 279, 252, 224, 197},
	{CompoundBarebow, Female, Adult}: {303, 284, 258, 233, 207, 182},

	{Compound, Male, Under18}:          {385, 369, 337, 306, 273, 242},
	{Compound, Female, Under18}:        {357, 343, 314, 284, 255, 225},
	{Recurve, Male, Under18}:           {311, 292, 265, 239, 213, 187},
	{Recurve, Female, Under18}:         {280, 263, 239, 215, 191, 168},
	{Barebow, Male, Under18}:           {298, 279, 254, 229, 204, 179},
	{Barebow, Female, Under18}:         {251, 236, 214, 193, 172, 151},
	{Longbow, Male, Under18}:           {161, 150, 137, 124, 109, 96},
	{Longbow, Female, Under18}:         {122, 114, 103, 94, 83, 73},
	{Traditional, Male, Under18}:       {210, 196, 178, 161, 143, 126},
	{Traditional, Female, Under18}:     {158, 147, 134, 121, 107, 95},
	{Flatbow, Male, Under18}:           {210, 196, 178, 161, 143, 126},
	{Flatbow, Female, Under18}:         {158, 147, 134, 121, 107, 95},
	{CompoundLimited, Male, Under18}:   {311, 292, 265, 239, 213, 187},
	{CompoundLimited, Female, Under18}: {280, 263, 239, 215, 191, 168},
	{CompoundBarebow, Male, Under18}:   {298, 279, 254, 229, 204, 179},
	{CompoundBarebow, Female, Under18}: {251, 236, 214, 193, 172, 151},
}

func CoaxOldFieldGroup(bowstyle Bowstyle, gender Gender, age Age) Category {
	coaxedAge := age
	switch age {
	case Under21, Over50:
		coaxedAge = Adult
	case Adult:
		coaxedAge = Adult
	default:
		// Under18 and younger all map to Under18
		coaxedAge = Under18
	}
	return Category{Bowstyle: bowstyle, Gender: gender, AgeGroup: coaxedAge}
}

func isOldFieldBowstyle(b Bowstyle) bool {
	for _, ob := range AllFieldBowstyles {
		if b == ob {
			return true
		}
	}
	return false
}

func isOldFieldAge(a Age) bool {
	for _, oa := range OldFieldAges {
		if a == oa {
			return true
		}
	}
	return false
}

func getOldFieldGroupData(bowstyle Bowstyle, gender Gender, age Age) (oldFieldGroupData, error) {
	if !isOldFieldBowstyle(bowstyle) {
		return oldFieldGroupData{}, fmt.Errorf(
			"%s is not a recognised bowstyle for old field classifications", bowstyle)
	}
	if !isValidGender(gender) {
		return oldFieldGroupData{}, fmt.Errorf(
			"%s is not a recognised gender for old field classifications", gender)
	}
	if !isOldFieldAge(age) {
		return oldFieldGroupData{}, fmt.Errorf(
			"%s is not a recognised age group for old field classifications", age)
	}
	key := [3]interface{}{bowstyle, gender, age}
	if scores, ok := oldFieldScoreTable[key]; ok {
		return oldFieldGroupData{classes: OldFieldClasses, classScores: scores}, nil
	}
	return oldFieldGroupData{}, fmt.Errorf("no old field data for bowstyle=%s gender=%s age=%s", bowstyle, gender, age)
}

func allFieldRoundsForOld() map[string]*rounds.Round {
	return allFieldRounds()
}

// CalculateOldFieldClassification returns the classification string for a score.
func CalculateOldFieldClassification(
	score float64,
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
) (string, error) {
	allRounds := allFieldRoundsForOld()
	roundname := archeryRound.Codename
	if _, ok := allRounds[roundname]; !ok {
		return "", fmt.Errorf(
			"This round is not recognised for old field classification. (codename=%q)", roundname)
	}

	if score < 0 || score > archeryRound.MaxScore() {
		return "", fmt.Errorf(
			"Invalid score of %.0f for a %s. Should be in range 0-%.0f.",
			score, archeryRound.Name, archeryRound.MaxScore(),
		)
	}

	gd, err := getOldFieldGroupData(bowstyle, gender, age)
	if err != nil {
		return "", err
	}

	// Check round eligibility: sighted needs red 24, unsighted needs blue 24
	if isSighted(bowstyle) {
		if !strings.Contains(roundname, "wa_field_24_red_") {
			return "UC", nil
		}
	} else {
		if !strings.Contains(roundname, "wa_field_24_blue_") {
			return "UC", nil
		}
	}

	for i, classname := range gd.classes {
		if float64(gd.classScores[i]) > score {
			continue
		}
		return classname, nil
	}
	return "UC", nil
}

// OldFieldClassificationScores returns score thresholds for each class (descending).
func OldFieldClassificationScores(
	archeryRound *rounds.Round,
	bowstyle Bowstyle,
	gender Gender,
	age Age,
) ([]int, error) {
	allRounds := allFieldRoundsForOld()
	if _, ok := allRounds[archeryRound.Codename]; !ok {
		return nil, fmt.Errorf(
			"This round is not recognised for old field classification. (codename=%q)", archeryRound.Codename)
	}

	gd, err := getOldFieldGroupData(bowstyle, gender, age)
	if err != nil {
		return nil, err
	}
	return gd.classScores, nil
}
