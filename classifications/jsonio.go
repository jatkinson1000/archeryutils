package classifications

import (
	"embed"
	"encoding/json"
	"sync"
)

//go:embed data
var dataFS embed.FS

// AgeData holds configuration for one age group.
type AgeData struct {
	AgeGroup  string    `json:"age_group"`
	Open      []float64 `json:"open"`   // previously "male"
	Female    []float64 `json:"female"`
	Sighted   []float64 `json:"sighted"`
	Unsighted []float64 `json:"unsighted"`
	Step      int       `json:"step"`
}

// BowstyleData holds configuration for one bowstyle.
type BowstyleData struct {
	Bowstyle       string  `json:"bowstyle"`
	DatumOut       float64 `json:"datum_out"`
	ClassStepOut   float64 `json:"classStep_out"`
	GenderStepOut  float64 `json:"genderStep_out"`
	AgeStepOut     float64 `json:"ageStep_out"`
	DatumIn        float64 `json:"datum_in"`
	ClassStepIn    float64 `json:"classStep_in"`
	GenderStepIn   float64 `json:"genderStep_in"`
	AgeStepIn      float64 `json:"ageStep_in"`
	DatumField     float64 `json:"datum_field"`
	ClassStepField float64 `json:"classStep_field"`
	GenderStepField float64 `json:"genderStep_field"`
	AgeStepField   float64 `json:"ageStep_field"`
}

// ClassificationData holds the class name lists for a system.
type ClassificationData struct {
	Location   string   `json:"location"`
	Classes    []string `json:"classes"`
	ClassesLong []string `json:"classes_long"`
}

var (
	ageDataOnce sync.Once
	ageDataMap  map[string]AgeData

	bowstyleDataOnce sync.Once
	bowstyleDataMap  map[string]BowstyleData

	classOutOnce sync.Once
	classOutData ClassificationData

	classInOnce sync.Once
	classInData ClassificationData
)

func loadAgeData() map[string]AgeData {
	ageDataOnce.Do(func() {
		raw, err := dataFS.ReadFile("data/AGB_ages.json")
		if err != nil {
			panic("loading AGB_ages.json: " + err.Error())
		}
		if err := json.Unmarshal(raw, &ageDataMap); err != nil {
			panic("parsing AGB_ages.json: " + err.Error())
		}
	})
	return ageDataMap
}

func loadBowstyleData() map[string]BowstyleData {
	bowstyleDataOnce.Do(func() {
		raw, err := dataFS.ReadFile("data/AGB_bowstyles.json")
		if err != nil {
			panic("loading AGB_bowstyles.json: " + err.Error())
		}
		if err := json.Unmarshal(raw, &bowstyleDataMap); err != nil {
			panic("parsing AGB_bowstyles.json: " + err.Error())
		}
	})
	return bowstyleDataMap
}

func loadClassesOut() ClassificationData {
	classOutOnce.Do(func() {
		raw, err := dataFS.ReadFile("data/AGB_classes_out.json")
		if err != nil {
			panic("loading AGB_classes_out.json: " + err.Error())
		}
		if err := json.Unmarshal(raw, &classOutData); err != nil {
			panic("parsing AGB_classes_out.json: " + err.Error())
		}
	})
	return classOutData
}

func loadClassesIn() ClassificationData {
	classInOnce.Do(func() {
		raw, err := dataFS.ReadFile("data/AGB_classes_in.json")
		if err != nil {
			panic("loading AGB_classes_in.json: " + err.Error())
		}
		if err := json.Unmarshal(raw, &classInData); err != nil {
			panic("parsing AGB_classes_in.json: " + err.Error())
		}
	})
	return classInData
}

// ageDataForAge returns the AgeData for an Age value.
func ageDataForAge(age Age) AgeData {
	name := age.String() // e.g. "OVER_50"
	data := loadAgeData()
	if d, ok := data[name]; ok {
		return d
	}
	panic("no age data for " + name)
}

// bowstyleDataFor returns the BowstyleData for a Bowstyle value.
func bowstyleDataFor(b Bowstyle) BowstyleData {
	name := b.String() // e.g. "RECURVE"
	data := loadBowstyleData()
	if d, ok := data[name]; ok {
		return d
	}
	panic("no bowstyle data for " + name)
}

// maxDistsForGender returns the max distance list for the given gender from AgeData.
// Male and Open both use the "open" distances; Female uses "female".
func maxDistsForGender(ad AgeData, g Gender) []float64 {
	if g == Female {
		return ad.Female
	}
	return ad.Open
}
