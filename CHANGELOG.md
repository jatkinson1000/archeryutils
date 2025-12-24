# Changelog

All notable changes to the project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/jatkinson1000/archeryutils/compare/v2.0.0...HEAD)

[GitHub diff to v2.0.0](https://github.com/jatkinson1000/archeryutils/compare/v2.0.0...HEAD)

### Added

- `OPEN` category added to `AGB_genders` for use in 2026 classifications in
  [#169](https://github.com/jatkinson1000/archeryutils/pull/169)
- Addition of regression tests for classifications and handicaps using syrupy for
  snapshots in [#148](https://github.com/jatkinson1000/archeryutils/pull/148)
- Addition of strict_rounds and strict_distance arguments for classifications in
  [#149](https://github.com/jatkinson1000/archeryutils/pull/149)
- Addition of new WA rounds for Under 15 category and updating of prestige rounds for
  outdoor classifications accordingly in [#167](https://github.com/jatkinson1000/archeryutils/pull/167).

### Changed

- Tests now in a separate `tests/` directory instead of alongside source in
  [#148](https://github.com/jatkinson1000/archeryutils/pull/148)
- Workflows update to include Python 3.14 in [#148](https://github.com/jatkinson1000/archeryutils/pull/148)
- AGB age category enums dropped the `AGE_` prefix in [#159](https://github.com/jatkinson1000/archeryutils/pull/159).
  Replaced by `OVER_50`, `ADULT`, `UNDER_18` etc.
- `AGB_genders` enum updated to add `OPEN`. `MALE` remains for backwards compatibility
  and legacy classifications as an alias to `OPEN`. Implemented in
  [#169](https://github.com/jatkinson1000/archeryutils/pull/169)
- Long Metric Gents and Ladies renamed to Long Metric (90m) and (70m) in line with
  April 2026 changes to Archery GB Rules of Shooting in
  [#169](https://github.com/jatkinson1000/archeryutils/pull/169)

### Fixes

- Bugfix for old indoor classifications to enforce full single face on AGB rounds but
  allow separate scores for triple faces for WA rounds. Previously triple faces gave
  different classification scores on AGB rounds.
  In [#149](https://github.com/jatkinson1000/archeryutils/pull/149)
- All compound categories get metric 122 80 as a prestige round in addition to the
  WA 50m compound round as equivalent in [#167](https://github.com/jatkinson1000/archeryutils/pull/167).

### Deprecated

- Use of AGB age category enums with the `AGE_` prefix in [#159](https://github.com/jatkinson1000/archeryutils/pull/159).
  Raises a warning and will be removed in future.
  Instead use new `OVER_50`, `ADULT`, `UNDER_18` etc.

### Removed

- Removal of unused test dependency pytest-mock in [#148](https://github.com/jatkinson1000/archeryutils/pull/148)



## [2.0.0](https://github.com/jatkinson1000/archeryutils/compare/v1.1.1...v2.0.0) - 2025-10-04

[GitHub diff to v1.1.1](https://github.com/jatkinson1000/archeryutils/compare/v1.1.1...v2.0.0)

### Added

- Experimental WA 660 rounds in [#139](https://github.com/jatkinson1000/archeryutils/pull/139)
- Archery Australia rounds in [#135](https://github.com/jatkinson1000/archeryutils/pull/135)
- New AGB 900 rounds in [#116](https://github.com/jatkinson1000/archeryutils/pull/116)
- `n_arrows` attribute added to `Round` in [#111](https://github.com/jatkinson1000/archeryutils/pull/111)
- `__hash__` magic method added to `Target`, `Pass`, and `Round` in [#144](https://github.com/jatkinson1000/archeryutils/pull/144)
- This CHANGELOG.md added in [#143](https://github.com/jatkinson1000/archeryutils/pull/143)

### Changed

- Breaking API change to use enums for inputs to classification functions in
  [#113](https://github.com/jatkinson1000/archeryutils/pull/113)
- Better use of numpy typing in [#133](https://github.com/jatkinson1000/archeryutils/pull/133)
- Allow inputs to classification functions to be an archeryutils Round as well as a string
  in [#119](https://github.com/jatkinson1000/archeryutils/pull/119)
- Use flattened loops in classification dict generation by [@TomHall2020](https://github.com/TomHall2020)
  in [#110](https://github.com/jatkinson1000/archeryutils/pull/110)
- Field classification naming made consistent with other schemes
- Dependencies:
  - Use latest ruff (0.13.3)
  - Use latest mypy (1.16) to resolve enums
  - Pin sphinx at <8.2.0 due to typing incompatibilities
  - Pin blackdoc and black versions due to an incompatibility in latest releases

### Fixes

- Fixes issue whereby a divide-by-zero warning could arise in the handicap rootfinding
  algorithm in [#109](https://github.com/jatkinson1000/archeryutils/pull/109)
- Field classification naming made consistent with other schemes


## [1.1.1](https://github.com/jatkinson1000/archeryutils/releases/tag/v1.1.1) - 2024-11-17

[GitHub diff with 1.1.0](https://github.com/jatkinson1000/archeryutils/compare/v1.1.0...v1.1.1)

### Fixed

- Fixes bug whereby the new 2025 field classifications were not restricted to the
  Archer tier for shorter peg rounds. Includes tests to check for this.
  In [#101](https://github.com/jatkinson1000/archeryutils/pull/101)


## [1.1.0](https://github.com/jatkinson1000/archeryutils/releases/tag/v1.1.0) - 2024-11-16

[GitHub diff with 1.0.0](https://github.com/jatkinson1000/archeryutils/compare/v1.0.0...v1.1.0)

### Added

- Option to use “English Longbow” as a bowstyle alias

### Changed

- Updated field classifications to the 2025 Archery GB scheme:
    - Uses new age groups, rounds, classifications and scores
    - For full details see archerycalculator.co.uk/new-field
- Old field classifications archived but still available using old in the function calls.
  See related API documentation
- Test suite extended to cover Python 3.13
- Linting moved to use ruff v0.7.3
- Coverage workflows updated to latest versions


## [1.0.0](https://github.com/jatkinson1000/archeryutils/releases/tag/v1.0.0) - 2024-06-08

### Added

- Initial release of archeryutils.
- MIT License
- Notable features of the library include:
    - Generic representations of targets and rounds
    - World Archery, Archery GB, and IFAA rounds
    - Calculations for Archery GB handicaps and Archery Australia archer skill level
    - Calculation of Archery GB classifications
- Detailed examples notebook showcasing usage
- Testing suite using [pytest](https://docs.pytest.org/en/stable/)
- Code quality and static analysis checks
- Documentation:
  - README.md and associated files in repository
  - Online API and comprehensive docs built using Sphinx available at
    [archeryutils.readthedocs.io](https://archeryutils.readthedocs.io)
