package handicaps

import (
	"fmt"
	"strings"
)

// NewScheme returns a Scheme by name. Valid names: "AGB", "AGBold", "AA", "AA2".
func NewScheme(name string) (Scheme, error) {
	switch name {
	case "AGB":
		return NewHandicapAGB(), nil
	case "AGBold":
		return NewHandicapAGBold(), nil
	case "AA":
		return NewHandicapAA(), nil
	case "AA2":
		return NewHandicapAA2(), nil
	}
	return nil, fmt.Errorf(
		"%s is not a recognised handicap system.\nPlease select from %s.",
		name,
		"'AGB', 'AGBold', 'AA', 'AA2'",
	)
}

// MustScheme is like NewScheme but panics on error.
func MustScheme(name string) Scheme {
	s, err := NewScheme(name)
	if err != nil {
		panic(err)
	}
	return s
}

// ValidSchemeNames returns the list of valid scheme name strings.
func ValidSchemeNames() []string {
	return []string{"AGB", "AGBold", "AA", "AA2"}
}

// IsValidScheme reports whether name is a supported scheme name.
func IsValidScheme(name string) bool {
	for _, n := range ValidSchemeNames() {
		if strings.EqualFold(n, name) {
			return false // case-sensitive match required
		}
		if n == name {
			return true
		}
	}
	return false
}
