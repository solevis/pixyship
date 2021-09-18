# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.6] - 2020-09-18

### Fixes

- Fix sorting of crew walk & run speed by splitting the column in two

## [2.1.5] - 2020-08-29

### Fixes

- Ignore changes of 2021-08-29 (old changes retrieved due to API url issue)

## [2.1.4] - 2020-08-29

### Added

- Add PSS Api URL in config.py (cannot trust ProductionServer from API for now) 

### Fixed

- Wrong PSS Api URL because ProductionServer don't return the one to use

## [2.1.3] - 2020-08-27

### Fixed

- Slowdown players importation due to new Savy API limitations 

## [2.1.2] - 2020-08-24

### Fixed

- Slowdown market history importation due to new Savy API limitations 

## [2.1.1] - 2020-08-23

### Fixed

- Fix missing market history of items in Changes and Ships pages

## [2.1.0] - 2020-08-23

### Added

- Add crew description
- Add the blueprints (or other item) to the cost of ships
- Colorize item name on Home page based on rarity
- Colorize item and crew name on Changes page based on rarity
- Like crews, hover on items display a tooltip with basic infos, recipe and market data
- Allow items to be ordered by id

### Fixed

- Wrong value of starbux/mineral unlock cost for some ships

### Security

- Stricter header security rules for the API

### Removed

- Remove Material icons CDN, use self hosted files (no more dependent of Google servers)

## [2.0.3] - 2020-07-07

### Fixed

- Fix DPS value in Rooms page

## [2.0.2] - 2020-06-20

### Security

- Security fix

## [2.0.1] - 2020-06-05

### Security

- Security fix

## [2.0.0] - 2020-06-04

### Changed

- New more modern UI

## [1.1.0] - 2020-05-28

### Changed

- Refactoring

### Fixed

- Bugs fixes

## [1.0.0] - 2019-10-04

### Changed

- Last Jeff commit

[unreleased]: https://github.com/solevis/pixyship/compare/main...develop
[2.1.6]: https://github.com/solevis/pixyship/compare/v2.1.5...v2.1.6
[2.1.5]: https://github.com/solevis/pixyship/compare/v2.1.4...v2.1.5
[2.1.4]: https://github.com/solevis/pixyship/compare/v2.1.3...v2.1.4
[2.1.3]: https://github.com/solevis/pixyship/compare/v2.1.2...v2.1.3
[2.1.2]: https://github.com/solevis/pixyship/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/solevis/pixyship/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/solevis/pixyship/compare/v2.0.3...v2.1.0
[2.0.3]: https://github.com/solevis/pixyship/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/solevis/pixyship/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/solevis/pixyship/compare/v2.0....v2.0.1
[2.0.0]: https://github.com/solevis/pixyship/compare/v1.1...v2.0
[1.1.0]: https://github.com/solevis/pixyship/compare/v1.0...v1.1
[1.0.0]: https://github.com/solevis/pixyship/releases/tag/v1.0
