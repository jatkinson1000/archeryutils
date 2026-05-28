# archeryutils

![GitHub](https://img.shields.io/github/license/jatkinson1000/archeryutils)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/jatkinson1000/archeryutils/testing.yaml)

A collection of archery utilities in Go.
Designed to make the development of archery codes and apps easier.

Contains:
- Generic representations of targets and rounds
- World Archery, Archery GB, IFAA, and Archery Australia rounds (embedded JSON)
- Calculations for Archery GB handicaps and Archery Australia archer skill level
- Calculation of Archery GB classifications (outdoor, indoor, field, legacy indoor/field)

## Installation

```sh
go get github.com/jatkinson1000/archeryutils
```

Requires Go 1.24+.

## Packages

| Package | Description |
|---|---|
| `targets` | `Target`, `ScoringSystem`, `FaceSpec`, distance/diameter quantities |
| `rounds` | `Pass`, `Round`, embedded round databases (AGB, WA, IFAA, AA) |
| `length` | Unit conversion helpers (metres, yards, cm, inches) |
| `handicaps` | AGB, AGBold, AA, AA2 handicap schemes; `HandicapTable` |
| `classifications` | AGB outdoor, indoor, field, old-indoor, old-field classifications |

## Quick start

```go
package main

import (
    "fmt"
    "github.com/jatkinson1000/archeryutils/classifications"
    "github.com/jatkinson1000/archeryutils/rounds"
)

func main() {
    r := rounds.AGBOutdoorMetric()["wa1440_90"]
    class, _ := classifications.CalculateOutdoorClassification(
        1200, r,
        classifications.Recurve, classifications.Male, classifications.Adult,
        true, true,
    )
    fmt.Println(class) // e.g. "B1"
}
```

```go
import "github.com/jatkinson1000/archeryutils/handicaps"

s := handicaps.MustScheme("AGB")
r := rounds.WAOutdoor()["wa1440_90"]
h, _ := handicaps.HandicapFromScore(s, 1200, r, 0, true)
fmt.Printf("Handicap: %.0f\n", h)
```

## Testing

```sh
go test ./...
go test -race ./...
```

## Module layout

```
go.mod
targets/           target face definitions, scoring systems
rounds/            pass and round types; embedded JSON round data
length/            unit conversion
handicaps/         handicap schemes (AGB, AGBold, AA, AA2), tables
classifications/   AGB classification calculations + embedded data
```

## Licence

Licensed under the MIT Licence — see [LICENCE](LICENCE).
