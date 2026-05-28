// Package classifications provides AGB archery classification calculations.
package classifications

// Gender identifies an archer's gender under AGB rules.
type Gender uint8

const (
	Male   Gender = 1 << iota // MALE   — Open category
	Female                    // FEMALE
	Open                      // OPEN
)

var genderNames = map[Gender]string{
	Male:   "MALE",
	Female: "FEMALE",
	Open:   "OPEN",
}

func (g Gender) String() string {
	if n, ok := genderNames[g]; ok {
		return n
	}
	return "UNKNOWN_GENDER"
}

// AllGenders lists every defined Gender value.
var AllGenders = []Gender{Male, Female, Open}

// Age identifies an AGB age group as a bitflag.
type Age uint32

const (
	Over50   Age = 1 << iota // OVER_50
	Adult                    // ADULT
	Under21                  // UNDER_21
	Under18                  // UNDER_18
	Under16                  // UNDER_16
	Under15                  // UNDER_15
	Under14                  // UNDER_14
	Under12                  // UNDER_12
)

// AllAges lists every defined Age value in order (oldest to youngest).
var AllAges = []Age{Over50, Adult, Under21, Under18, Under16, Under15, Under14, Under12}

var ageNames = map[Age]string{
	Over50:  "OVER_50",
	Adult:   "ADULT",
	Under21: "UNDER_21",
	Under18: "UNDER_18",
	Under16: "UNDER_16",
	Under15: "UNDER_15",
	Under14: "UNDER_14",
	Under12: "UNDER_12",
}

func (a Age) String() string {
	if n, ok := ageNames[a]; ok {
		return n
	}
	return "UNKNOWN_AGE"
}

// AgeStep returns the numeric step value for this age group (0=Adult, 6=U12).
var AgeStepMap = map[Age]int{
	Over50:  1,
	Adult:   0,
	Under21: 1,
	Under18: 2,
	Under16: 3,
	Under15: 4,
	Under14: 5,
	Under12: 6,
}

// Bowstyle identifies an AGB bowstyle as a bitflag.
type Bowstyle uint32

const (
	Compound        Bowstyle = 1 << iota // COMPOUND
	Recurve                              // RECURVE
	Barebow                              // BAREBOW
	Longbow                              // LONGBOW
	Traditional                          // TRADITIONAL
	Flatbow                              // FLATBOW
	CompoundLimited                      // COMPOUNDLIMITED
	CompoundBarebow                      // COMPOUNDBAREBOW
)

// EnglishLongbow is an alias for Longbow under AGB rules.
const EnglishLongbow = Longbow

// AllBowstyles lists every primary (non-alias) bowstyle.
var AllBowstyles = []Bowstyle{
	Compound, Recurve, Barebow, Longbow, Traditional, Flatbow, CompoundLimited, CompoundBarebow,
}

// OutdoorBowstyles lists bowstyles eligible for outdoor target classification.
var OutdoorBowstyles = []Bowstyle{Compound, Recurve, Barebow, Longbow}

// IndoorBowstyles lists bowstyles eligible for indoor classification.
var IndoorBowstyles = []Bowstyle{Compound, Recurve, Barebow, Longbow}

// FieldBowstyles lists bowstyles eligible for field classification (all bowstyles).
var FieldBowstyles = []Bowstyle{Compound, Recurve, Barebow, Longbow, Traditional, Flatbow, CompoundLimited, CompoundBarebow}

var bowstyleNames = map[Bowstyle]string{
	Compound:        "COMPOUND",
	Recurve:         "RECURVE",
	Barebow:         "BAREBOW",
	Longbow:         "LONGBOW",
	Traditional:     "TRADITIONAL",
	Flatbow:         "FLATBOW",
	CompoundLimited: "COMPOUNDLIMITED",
	CompoundBarebow: "COMPOUNDBAREBOW",
}

func (b Bowstyle) String() string {
	if n, ok := bowstyleNames[b]; ok {
		return n
	}
	return "UNKNOWN_BOWSTYLE"
}

// Category holds the resolved archer category.
type Category struct {
	Bowstyle  Bowstyle
	Gender    Gender
	AgeGroup  Age
}
