package classifications_test

import (
	"testing"

	"github.com/retbrown/archeryutils/classifications"
	"github.com/retbrown/archeryutils/rounds"
	"github.com/retbrown/archeryutils/targets"
)

func fieldRound(t *testing.T, name string) *rounds.Round {
	t.Helper()
	r, ok := rounds.WAField()[name]
	if !ok {
		t.Fatalf("field round %q not found", name)
	}
	return r
}

func TestFieldClassificationScoresAges(t *testing.T) {
	tests := []struct {
		age  classifications.Age
		want []int
	}{
		{classifications.Adult, []int{336, 311, 283, 249, 212, 173, 135, 101, 74}},
		{classifications.Over50, []int{321, 294, 263, 227, 188, 149, 114, 84, 60}},
		{classifications.Under18, []int{305, 275, 241, 203, 164, 127, 94, 68, 48}},
		{classifications.Under12, []int{224, 185, 146, 111, 82, 58, 41, 28, 19}},
	}
	for _, tc := range tests {
		t.Run("blue_marked_barebow_male_"+tc.age.String(), func(t *testing.T) {
			r := fieldRound(t, "wa_field_24_blue_marked")
			got, err := classifications.FieldClassificationScores(r, classifications.Barebow, classifications.Male, tc.age, true, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestFieldClassificationScoresGenders(t *testing.T) {
	tests := []struct {
		gender classifications.Gender
		age    classifications.Age
		want   []int
	}{
		{classifications.Male, classifications.Adult, []int{336, 311, 283, 249, 212, 173, 135, 101, 74}},
		{classifications.Female, classifications.Adult, []int{315, 287, 255, 218, 179, 140, 106, 78, 55}},
		{classifications.Male, classifications.Under18, []int{305, 275, 241, 203, 164, 127, 94, 68, 48}},
		{classifications.Female, classifications.Under18, []int{280, 247, 209, 170, 132, 99, 72, 51, 35}},
	}
	for _, tc := range tests {
		t.Run("blue_marked_barebow_"+tc.gender.String()+"_"+tc.age.String(), func(t *testing.T) {
			r := fieldRound(t, "wa_field_24_blue_marked")
			got, err := classifications.FieldClassificationScores(r, classifications.Barebow, tc.gender, tc.age, true, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestFieldClassificationScoresBowstyles(t *testing.T) {
	tests := []struct {
		round    string
		bowstyle classifications.Bowstyle
		want     []int
	}{
		{"wa_field_24_red_marked", classifications.Compound, []int{408, 391, 369, 345, 318, 286, 248, 204, 157}},
		{"wa_field_12_red_unmarked", classifications.Compound, []int{-9999, -9999, -9999, 173, 159, 143, 124, 102, 79}},
		{"wa_field_24_red_marked", classifications.CompoundLimited, []int{369, 347, 322, 293, 259, 219, 176, 133, 96}},
		{"wa_field_24_blue_marked", classifications.CompoundBarebow, []int{343, 321, 296, 268, 235, 200, 164, 129, 99}},
		{"wa_field_24_red_marked", classifications.Recurve, []int{369, 343, 314, 279, 237, 189, 139, 96, 62}},
		{"wa_field_24_blue_marked", classifications.Barebow, []int{336, 311, 283, 249, 212, 173, 135, 101, 74}},
		{"wa_field_24_blue_marked", classifications.Traditional, []int{309, 283, 252, 218, 182, 146, 114, 86, 63}},
		{"wa_field_24_blue_marked", classifications.Flatbow, []int{273, 244, 212, 179, 146, 116, 90, 68, 51}},
		{"wa_field_24_blue_marked", classifications.Longbow, []int{241, 209, 176, 143, 114, 88, 67, 49, 36}},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_"+tc.bowstyle.String(), func(t *testing.T) {
			r := fieldRound(t, tc.round)
			got, err := classifications.FieldClassificationScores(r, tc.bowstyle, classifications.Male, classifications.Adult, true, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestFieldClassificationScoresUnmarked(t *testing.T) {
	// Unmarked should give same scores as marked (normalization)
	r := fieldRound(t, "wa_field_24_blue_unmarked")
	want := []int{336, 311, 283, 249, 212, 173, 135, 101, 74}
	got, err := classifications.FieldClassificationScores(r, classifications.Barebow, classifications.Male, classifications.Adult, true, true)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	assertIntSliceEqual(t, got, want)
}

func TestFieldClassificationScoresNonStrictRound(t *testing.T) {
	tests := []struct {
		roundname string
		bowstyle  classifications.Bowstyle
		gender    classifications.Gender
		age       classifications.Age
		want      []int
	}{
		{"wa_field_24_red_marked", classifications.Barebow, classifications.Male, classifications.Adult,
			[]int{-9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999}},
		{"wa_field_24_yellow_marked", classifications.Barebow, classifications.Male, classifications.Adult,
			[]int{-9999, -9999, -9999, -9999, -9999, -9999, 178, 140, 106}},
	}
	for _, tc := range tests {
		t.Run(tc.roundname, func(t *testing.T) {
			r := fieldRound(t, tc.roundname)
			got, err := classifications.FieldClassificationScores(r, tc.bowstyle, tc.gender, tc.age, false, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestFieldClassificationScoresNonStrictDistance(t *testing.T) {
	tests := []struct {
		round    string
		bowstyle classifications.Bowstyle
		gender   classifications.Gender
		age      classifications.Age
		want     []int
	}{
		{"wa_field_24_red_marked", classifications.Barebow, classifications.Male, classifications.Adult,
			[]int{306, 277, 243, 204, 164, 125, 91, 64, 44}},
		{"wa_field_12_red_marked", classifications.Barebow, classifications.Male, classifications.Adult,
			[]int{-9999, -9999, -9999, 102, 82, 63, 46, 32, 22}},
		{"wa_field_24_yellow_marked", classifications.Barebow, classifications.Male, classifications.Adult,
			[]int{360, 338, 313, 285, 253, 217, 178, 140, 106}},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_"+tc.bowstyle.String(), func(t *testing.T) {
			r := fieldRound(t, tc.round)
			got, err := classifications.FieldClassificationScores(r, tc.bowstyle, tc.gender, tc.age, true, false)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestFieldClassificationScoresInvalidAge(t *testing.T) {
	r := fieldRound(t, "wa_field_24_blue_marked")
	// Under21 is not a valid field age
	_, err := classifications.FieldClassificationScores(r, classifications.Barebow, classifications.Male, classifications.Under21, true, true)
	if err == nil {
		t.Fatal("expected error for Under21 field age")
	}
}

func TestFieldClassificationScoresInvalidRound(t *testing.T) {
	customRound, _ := rounds.NewRound("Custom", []*rounds.Pass{
		mustOutdoorPass(t, 36, "10_zone", targets.CM(122), targets.Metres(70)),
	})
	_, err := classifications.FieldClassificationScores(customRound, classifications.Recurve, classifications.Male, classifications.Adult, true, true)
	if err == nil {
		t.Fatal("expected error for unrecognised round")
	}
}

func TestCalculateFieldClassification(t *testing.T) {
	tests := []struct {
		round    string
		score    float64
		age      classifications.Age
		bowstyle classifications.Bowstyle
		want     string
	}{
		{"wa_field_24_red_marked", 400, classifications.Adult, classifications.Compound, "GMB"},
		{"wa_field_12_red_marked", 200, classifications.Adult, classifications.Compound, "B1"},
		{"wa_field_24_blue_marked", 400, classifications.Adult, classifications.Compound, "A1"},
		{"wa_field_24_blue_marked", 177, classifications.Under18, classifications.Traditional, "B1"},
		{"wa_field_24_blue_marked", 100, classifications.Adult, classifications.Barebow, "A3"},
		{"wa_field_24_blue_marked", 50, classifications.Adult, classifications.Barebow, "UC"},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_"+tc.bowstyle.String()+"_"+tc.want, func(t *testing.T) {
			r := fieldRound(t, tc.round)
			got, err := classifications.CalculateFieldClassification(tc.score, r, tc.bowstyle, classifications.Male, tc.age, true, true)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Errorf("got %q, want %q", got, tc.want)
			}
		})
	}
}

func TestCoaxFieldGroup(t *testing.T) {
	tests := []struct {
		age     classifications.Age
		wantAge classifications.Age
	}{
		{classifications.Adult, classifications.Adult},
		{classifications.Under21, classifications.Adult},
		{classifications.Under18, classifications.Under18},
		{classifications.Under12, classifications.Under12},
	}
	for _, tc := range tests {
		t.Run(tc.age.String(), func(t *testing.T) {
			cat := classifications.CoaxFieldGroup(classifications.Recurve, classifications.Male, tc.age)
			if cat.AgeGroup != tc.wantAge {
				t.Errorf("CoaxFieldGroup(%s).AgeGroup = %s, want %s", tc.age, cat.AgeGroup, tc.wantAge)
			}
		})
	}
}
