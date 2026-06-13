package classifications_test

import (
	"testing"

	"github.com/retbrown/archeryutils/classifications"
)

func TestOldFieldClassificationScoresAges(t *testing.T) {
	tests := []struct {
		age  classifications.Age
		want []int
	}{
		{classifications.Adult, []int{328, 307, 279, 252, 224, 197}},
		{classifications.Under18, []int{298, 279, 254, 229, 204, 179}},
	}
	for _, tc := range tests {
		t.Run(tc.age.String(), func(t *testing.T) {
			r := fieldRound(t, "wa_field_24_blue_marked")
			got, err := classifications.OldFieldClassificationScores(r, classifications.Barebow, classifications.Male, tc.age)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOldFieldClassificationScoresGenders(t *testing.T) {
	tests := []struct {
		round  string
		gender classifications.Gender
		age    classifications.Age
		want   []int
	}{
		{"wa_field_24_blue_marked", classifications.Male, classifications.Adult, []int{328, 307, 279, 252, 224, 197}},
		{"wa_field_24_blue_marked", classifications.Female, classifications.Adult, []int{303, 284, 258, 233, 207, 182}},
		{"wa_field_24_blue_marked", classifications.Male, classifications.Under18, []int{298, 279, 254, 229, 204, 179}},
		{"wa_field_24_blue_marked", classifications.Female, classifications.Under18, []int{251, 236, 214, 193, 172, 151}},
	}
	for _, tc := range tests {
		t.Run(tc.gender.String()+"_"+tc.age.String(), func(t *testing.T) {
			r := fieldRound(t, tc.round)
			got, err := classifications.OldFieldClassificationScores(r, classifications.Barebow, tc.gender, tc.age)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOldFieldClassificationScoresBowstyles(t *testing.T) {
	tests := []struct {
		round    string
		bowstyle classifications.Bowstyle
		want     []int
	}{
		{"wa_field_24_red_marked", classifications.Compound, []int{393, 377, 344, 312, 279, 247}},
		{"wa_field_24_red_marked", classifications.Recurve, []int{338, 317, 288, 260, 231, 203}},
		{"wa_field_24_blue_marked", classifications.Barebow, []int{328, 307, 279, 252, 224, 197}},
		{"wa_field_24_blue_marked", classifications.Traditional, []int{262, 245, 223, 202, 178, 157}},
		{"wa_field_24_blue_marked", classifications.Flatbow, []int{262, 245, 223, 202, 178, 157}},
		{"wa_field_24_blue_marked", classifications.Longbow, []int{201, 188, 171, 155, 137, 121}},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_"+tc.bowstyle.String(), func(t *testing.T) {
			r := fieldRound(t, tc.round)
			got, err := classifications.OldFieldClassificationScores(r, tc.bowstyle, classifications.Male, classifications.Adult)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			assertIntSliceEqual(t, got, tc.want)
		})
	}
}

func TestOldFieldClassificationScoresInvalidAge(t *testing.T) {
	r := fieldRound(t, "wa_field_24_blue_marked")
	// Under12 is not a valid old field age
	_, err := classifications.OldFieldClassificationScores(r, classifications.Barebow, classifications.Male, classifications.Under12)
	if err == nil {
		t.Fatal("expected error for invalid age (Under12)")
	}
}

func TestOldFieldClassificationScoresInvalidRound(t *testing.T) {
	// An outdoor round that isn't in field rounds
	r := outdoorRound(t, "wa1440_90")
	_, err := classifications.OldFieldClassificationScores(r, classifications.Recurve, classifications.Male, classifications.Adult)
	if err == nil {
		t.Fatal("expected error for non-field round")
	}
}

func TestCalculateOldFieldClassification(t *testing.T) {
	tests := []struct {
		round    string
		score    float64
		age      classifications.Age
		bowstyle classifications.Bowstyle
		want     string
	}{
		{"wa_field_24_red_marked", 400, classifications.Adult, classifications.Compound, "GMB"},
		{"wa_field_24_blue_marked", 177, classifications.Under18, classifications.Traditional, "1C"},
		// Wrong peg for sighted → UC
		{"wa_field_24_blue_marked", 400, classifications.Adult, classifications.Compound, "UC"},
		// Wrong peg for unsighted → UC
		{"wa_field_24_red_marked", 337, classifications.Adult, classifications.Barebow, "UC"},
		// Low score
		{"wa_field_24_blue_marked", 1, classifications.Adult, classifications.Longbow, "UC"},
	}
	for _, tc := range tests {
		t.Run(tc.round+"_"+tc.bowstyle.String()+"_"+tc.want, func(t *testing.T) {
			r := fieldRound(t, tc.round)
			got, err := classifications.CalculateOldFieldClassification(tc.score, r, tc.bowstyle, classifications.Male, tc.age)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Errorf("got %q, want %q", got, tc.want)
			}
		})
	}
}

func TestCalculateOldFieldClassificationInvalidScore(t *testing.T) {
	r := fieldRound(t, "wa_field_24_blue_marked")
	for _, score := range []float64{1000, 433, -1, -100} {
		_, err := classifications.CalculateOldFieldClassification(score, r, classifications.Barebow, classifications.Male, classifications.Adult)
		if err == nil {
			t.Errorf("expected error for score=%.0f", score)
		}
	}
}

func TestCoaxOldFieldGroup(t *testing.T) {
	tests := []struct {
		age     classifications.Age
		wantAge classifications.Age
	}{
		{classifications.Adult, classifications.Adult},
		{classifications.Over50, classifications.Adult},
		{classifications.Under21, classifications.Adult},
		{classifications.Under18, classifications.Under18},
		{classifications.Under16, classifications.Under18},
		{classifications.Under12, classifications.Under18},
	}
	for _, tc := range tests {
		t.Run(tc.age.String(), func(t *testing.T) {
			cat := classifications.CoaxOldFieldGroup(classifications.Recurve, classifications.Male, tc.age)
			if cat.AgeGroup != tc.wantAge {
				t.Errorf("CoaxOldFieldGroup(%s).AgeGroup = %s, want %s", tc.age, cat.AgeGroup, tc.wantAge)
			}
		})
	}
}
