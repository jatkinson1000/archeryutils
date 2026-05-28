// Package rounds provides the Pass and Round types for archery applications.
package rounds

import (
	"fmt"
	"io"

	"github.com/jatkinson1000/archeryutils/targets"
)

// Pass represents a single pass of arrows shot at a target.
type Pass struct {
	NArrows int
	Target  *targets.Target
}

// NewPass creates a Pass, taking the absolute value of nArrows.
func NewPass(nArrows int, target *targets.Target) (*Pass, error) {
	if target == nil {
		return nil, fmt.Errorf("the target passed to a Pass must not be nil")
	}
	if nArrows < 0 {
		nArrows = -nArrows
	}
	return &Pass{NArrows: nArrows, Target: target}, nil
}

// AtTarget creates a Pass by constructing the Target inline.
func AtTarget(
	nArrows int,
	system targets.ScoringSystem,
	diameter, distance targets.Quantity,
	indoor bool,
) (*Pass, error) {
	t, err := targets.NewTarget(system, diameter, distance, indoor)
	if err != nil {
		return nil, err
	}
	return NewPass(nArrows, t)
}

// MaxScore returns the maximum score achievable in this pass.
func (p *Pass) MaxScore() float64 {
	return float64(p.NArrows) * p.Target.MaxScore()
}

// Equal reports whether two Passes are equivalent.
func (p *Pass) Equal(other *Pass) bool {
	if p == other {
		return true
	}
	if other == nil {
		return false
	}
	return p.NArrows == other.NArrows && p.Target.Equal(other.Target)
}

// String returns a human-readable representation.
func (p *Pass) String() string {
	return fmt.Sprintf("Pass(%d, %s)", p.NArrows, p.Target)
}

// Round represents a full archery round made up of multiple passes.
type Round struct {
	Name     string
	Codename string
	Passes   []*Pass
	Location *string
	Body     *string
	Family   *string
	NArrows  int
}

// NewRound creates a Round from a non-empty slice of Passes.
func NewRound(name string, passes []*Pass, opts ...Option) (*Round, error) {
	if len(passes) == 0 {
		return nil, fmt.Errorf("passes must contain at least one Pass object but none supplied.")
	}
	for _, p := range passes {
		if p == nil {
			return nil, fmt.Errorf("passes in a Round object should be an iterable of Pass objects.")
		}
	}

	r := &Round{
		Name:   name,
		Passes: make([]*Pass, len(passes)),
	}
	copy(r.Passes, passes)
	for _, p := range r.Passes {
		r.NArrows += p.NArrows
	}
	for _, o := range opts {
		o(r)
	}
	return r, nil
}

// Option configures optional Round fields.
type Option func(*Round)

func WithCodename(c string) Option  { return func(r *Round) { r.Codename = c } }
func WithLocation(l string) Option  { return func(r *Round) { s := l; r.Location = &s } }
func WithBody(b string) Option      { return func(r *Round) { s := b; r.Body = &s } }
func WithFamily(f string) Option    { return func(r *Round) { s := f; r.Family = &s } }

// MaxScore returns the maximum score achievable in this round.
func (r *Round) MaxScore() float64 {
	var total float64
	for _, p := range r.Passes {
		total += p.MaxScore()
	}
	return total
}

// MaxDistance returns the largest distance shot in the round in its native units.
func (r *Round) MaxDistance() targets.Quantity {
	var maxM float64
	var result targets.Quantity
	for _, p := range r.Passes {
		if p.Target.Distance() > maxM {
			maxM = p.Target.Distance()
			result = p.Target.NativeDistance()
		}
	}
	return result
}

// GetInfo prints a summary of the round's passes to w.
func (r *Round) GetInfo(w io.Writer) {
	fmt.Fprintf(w, "A %s consists of %d passes:\n", r.Name, len(r.Passes))
	for _, p := range r.Passes {
		diam := p.Target.NativeDiameter()
		dist := p.Target.NativeDistance()
		fmt.Fprintf(w, "\t- %d arrows at a %.1f %s target at %.1f %ss.\n",
			p.NArrows, diam.Value, diam.Units, dist.Value, dist.Units)
	}
}

// Equal reports whether two Rounds are equivalent (based on name and passes only).
func (r *Round) Equal(other *Round) bool {
	if r == other {
		return true
	}
	if other == nil || r.Name != other.Name || len(r.Passes) != len(other.Passes) {
		return false
	}
	for i, p := range r.Passes {
		if !p.Equal(other.Passes[i]) {
			return false
		}
	}
	return true
}

// String returns a human-readable representation.
func (r *Round) String() string {
	return fmt.Sprintf("<Round: '%s'>", r.Name)
}
