package rounds

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"strings"
	"sync"

	"github.com/jatkinson1000/archeryutils/targets"
)

// roundJSON mirrors the JSON structure of a single round entry.
type roundJSON struct {
	Name     string     `json:"name"`
	Codename string     `json:"codename"`
	Location string     `json:"location"`
	Body     string     `json:"body"`
	Family   string     `json:"family"`
	Passes   []passJSON `json:"passes"`
}

type passJSON struct {
	NArrows      int     `json:"n_arrows"`
	Diameter     float64 `json:"diameter"`
	DiameterUnit string  `json:"diameter_unit"`
	Scoring      string  `json:"scoring"`
	Distance     float64 `json:"distance"`
	DistUnit     string  `json:"dist_unit"`
}

var indoorAliases = map[string]bool{
	"i": true, "I": true, "indoors": true, "indoor": true, "in": true,
	"inside": true, "Indoors": true, "Indoor": true, "In": true, "Inside": true,
}
var outdoorAliases = map[string]bool{
	"o": true, "O": true, "outdoors": true, "outdoor": true, "out": true,
	"outside": true, "Outdoors": true, "Outdoor": true, "Out": true, "Outside": true,
}
var fieldAliases = map[string]bool{
	"f": true, "F": true, "field": true, "Field": true, "woods": true, "Woods": true,
}

// ParseRoundsJSON parses a JSON byte slice (array of round objects) into a map keyed by codename.
func ParseRoundsJSON(data []byte) (map[string]*Round, error) {
	var raw []roundJSON
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("rounds JSON parse: %w", err)
	}

	out := make(map[string]*Round, len(raw))
	for _, rj := range raw {
		// Resolve location
		var locationPtr *string
		indoor := false
		loc := ""
		if indoorAliases[rj.Location] {
			indoor = true
			loc = "indoor"
		} else if outdoorAliases[rj.Location] {
			loc = "outdoor"
		} else if fieldAliases[rj.Location] {
			loc = "field"
		}
		if loc != "" {
			locationPtr = &loc
		}

		passes := make([]*Pass, 0, len(rj.Passes))
		for _, pj := range rj.Passes {
			diamUnit := pj.DiameterUnit
			if diamUnit == "" {
				diamUnit = "cm"
			}
			p, err := AtTarget(
				pj.NArrows,
				targets.ScoringSystem(pj.Scoring),
				targets.Quantity{Value: pj.Diameter, Units: diamUnit},
				targets.Quantity{Value: pj.Distance, Units: pj.DistUnit},
				indoor,
			)
			if err != nil {
				return nil, fmt.Errorf("round %q pass: %w", rj.Codename, err)
			}
			passes = append(passes, p)
		}

		opts := []Option{WithCodename(rj.Codename)}
		if locationPtr != nil {
			opts = append(opts, WithLocation(*locationPtr))
		}
		if rj.Body != "" {
			opts = append(opts, WithBody(rj.Body))
		}
		if rj.Family != "" {
			opts = append(opts, WithFamily(rj.Family))
		}

		r, err := NewRound(rj.Name, passes, opts...)
		if err != nil {
			return nil, fmt.Errorf("round %q: %w", rj.Codename, err)
		}
		out[rj.Codename] = r
	}
	return out, nil
}

// LoadFromFS loads all rounds from a list of JSON file names in the given FS.
func LoadFromFS(fsys fs.FS, filenames ...string) (map[string]*Round, error) {
	out := make(map[string]*Round)
	for _, name := range filenames {
		data, err := fs.ReadFile(fsys, name)
		if err != nil {
			return nil, fmt.Errorf("reading %q: %w", name, err)
		}
		rounds, err := ParseRoundsJSON(data)
		if err != nil {
			return nil, fmt.Errorf("parsing %q: %w", name, err)
		}
		for k, v := range rounds {
			out[k] = v
		}
	}
	return out, nil
}

// normaliseFilename ensures the filename ends in .json.
func normaliseFilename(name string) string {
	if !strings.HasSuffix(name, ".json") {
		return name + ".json"
	}
	return name
}

// Embedded data files —- these are loaded once.
//go:embed data
var dataFS embed.FS

type roundsCache struct {
	mu   sync.Mutex
	data map[string]map[string]*Round
}

var cache = &roundsCache{data: make(map[string]map[string]*Round)}

func loadOnce(name string) map[string]*Round {
	cache.mu.Lock()
	defer cache.mu.Unlock()
	if m, ok := cache.data[name]; ok {
		return m
	}
	data, err := dataFS.ReadFile("data/" + name)
	if err != nil {
		panic(fmt.Sprintf("embedded round file %q: %v", name, err))
	}
	m, err := ParseRoundsJSON(data)
	if err != nil {
		panic(fmt.Sprintf("parsing embedded round file %q: %v", name, err))
	}
	cache.data[name] = m
	return m
}

// Pre-defined accessors for each bundled round collection.
func AGBOutdoorImperial() map[string]*Round { return loadOnce("AGB_outdoor_imperial.json") }
func AGBOutdoorMetric() map[string]*Round   { return loadOnce("AGB_outdoor_metric.json") }
func AGBIndoor() map[string]*Round          { return loadOnce("AGB_indoor.json") }
func WAOutdoor() map[string]*Round          { return loadOnce("WA_outdoor.json") }
func WAIndoor() map[string]*Round           { return loadOnce("WA_indoor.json") }
func WAField() map[string]*Round            { return loadOnce("WA_field.json") }
func WAExperimental() map[string]*Round     { return loadOnce("WA_experimental.json") }
func IFAAField() map[string]*Round          { return loadOnce("IFAA_field.json") }
func WAVI() map[string]*Round               { return loadOnce("WA_VI.json") }
func AGBVI() map[string]*Round              { return loadOnce("AGB_VI.json") }
func AAOutdoorMetric() map[string]*Round    { return loadOnce("AA_outdoor_metric.json") }
func AAIndoor() map[string]*Round           { return loadOnce("AA_indoor.json") }
func AAField() map[string]*Round            { return loadOnce("AA_field.json") }
func Miscellaneous() map[string]*Round      { return loadOnce("Miscellaneous.json") }

// AllRounds returns a merged map of all bundled rounds.
func AllRounds() map[string]*Round {
	sources := []func() map[string]*Round{
		AGBOutdoorImperial, AGBOutdoorMetric, AGBIndoor,
		WAOutdoor, WAIndoor, WAField, WAExperimental,
		IFAAField, WAVI, AGBVI,
		AAOutdoorMetric, AAIndoor, AAField,
		Miscellaneous,
	}
	out := make(map[string]*Round)
	for _, src := range sources {
		for k, v := range src() {
			out[k] = v
		}
	}
	return out
}
