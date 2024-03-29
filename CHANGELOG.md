# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.9.0] - 2024-02-17

### Added

- Skins page

### Changed

- Skins are no longer displayed in Rooms page

## [2.8.0] - 2023-02-19

### Added

- Missiles page

### Changed

- Missiles are no longer displayed in Items page

### Fixed

- Fix DPS calculation for EMP, Fire in Crafts page
- Fix Speed calculation in Crafts page

## [2.7.0] - 2023-02-17

### Added

- Crafts page

### Changed

- Crafts are no longer displayed in Items page

## [2.6.0] - 2023-01-03

### Added

- Display galaxy map merchant trader on the home

### Changed

- Larger home page layout

## [2.5.0] - 2022-12-28

### Added

- Add button to display history of each daily sale origin (cargo, shop, etc)

### Changed

- Last sales by item show now 1,000 entries instead of 50

## [2.4.0] - 2022-09-14

### Added

- Social network banner
- Get promotions from API (new daily sales)
- Import daily sales (for futur historic display)
- Display tournament news
- Store Item page active tab in URL
- Add Savy token implementation
- Item page: display item space and requirement
- Add Docker environment for developing PixyShip
- Add Fire Resists and Walk/Run stats in crew popup
- Rooms page: filter by shop type (starbase, player, bux)
- Implementation of FleetGift sale
- Add search input for last sales in Item page
- Import market messages to retrieve item sales offstat
- WIP: display offstat in Item last sales table

### Changed

- Footer removed
- Merge room and skins
- Rename DSN to DATABASE_URI in backend configuration
- Reduce cache expiration from 1 hour to 5 minutes
- Randomize items when importing sales

### Fixed

- Builder was reloading at each change
- Daily bundle sales can be multiple
- Fix player search
- Fix equipments column sorting
- Rooms page: fix ids query parameter
- Fix XP books bonus display

## [2.3.0] - 2022-01-01

### Added

- Pins page
- Crews: display stats score
- Items: display "+??" (random stat) if rarity is at least hero
- Item page: new tab showing possible upgrades
- Home: display running event

### Changed

- Page's metadata

## [2.2.6] - 2021-11-24

### Added

- Items page: Type and Subtype columns sortable
- Items page: Display training % for instant training item

## [2.2.5] - 2021-11-14

### Added

- Ships page: extended filter
- Save sorting in URL

## [2.2.4] - 2021-11-12

### Changed

- Ships page: display full repair time

### Fixed

- Rooms page: wrong capacity label and value

## [2.2.3] - 2021-10-03

### Added

- Display item content (rewards)

### Changed

- Item description is now displayed in popup

## [2.2.2] - 2021-10-29

### Fixed

- Fix Speed unit for weapons rooms

## [2.2.1] - 2021-10-23

### Added

- Changelog page "/changelog"
- Changelog in about page

### Fixed

- Fix changelog link in footer

## [2.2.0] - 2021-10-23

### Added

- Dedicated item page with:
  - item infos
  - market history
  - last players sales
  - crafting tree
- Add "Type" filter on Changes page
- Add query parameter to all URL to filter assets (items, crews, etc.) by IDs (ids=X) or filters (ex: rarity=Common)
- Filtering data on pages will automatically update the URL, so going back in history will prevent losing your filters
- Add "player=" query parameter to the "Players" page URL
- [BETA] "Changes" page will now show new Pixel Starships sprites listed in API

### Changed

- Market chart is no longer displayed by expanding a row in Items page, it's now in item page by clicking item name or logo
- Serve sprites from PixyShip instead of Savy for better cache control
- Sort data by ID, most recent first (except Items, sorted by volume of sales)

### Fixed

- The armor calculation in the constructor always showed zero
- Display of power used/generated by rooms in Builder without color and too big font
- Old "/crew" and "/research" pages now redirect respectively to "/crews" and "/researches"
- Unknown pages redirect to homepage

## [2.1.10] - 2021-10-02

### Changed

- Increase number of displayed changes

## [2.1.9] - 2021-10-02

### Fixed

- Fix dailies infos (Savy moved data to another API endpoint)

## [2.1.8] - 2021-09-30

### Changed

- Reduce default cache expiration from 6 hours to 1 hour

## [2.1.7] - 2021-09-25

### Added

- Add sorting to the "Recipe" column to group items that can be crafted or not

## [2.1.6] - 2021-09-18

### Fixed

- Fix sorting of crew walk & run speed by splitting the column in two

## [2.1.5] - 2021-08-29

### Fixed

- Ignore changes of 2021-08-29 (old changes retrieved due to API url issue)

## [2.1.4] - 2021-08-29

### Added

- Add PSS Api URL in config.py (cannot trust ProductionServer from API for now)

### Fixed

- Wrong PSS Api URL because ProductionServer don't return the one to use

## [2.1.3] - 2021-08-27

### Fixed

- Slowdown players importation due to new Savy API limitations

## [2.1.2] - 2021-08-24

### Fixed

- Slowdown market history importation due to new Savy API limitations

## [2.1.1] - 2021-08-23

### Fixed

- Fix missing market history of items in Changes and Ships pages

## [2.1.0] - 2021-08-23

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

## [2.0.3] - 2021-07-07

### Fixed

- Fix DPS value in Rooms page

## [2.0.2] - 2021-06-20

### Security

- Security fix

## [2.0.1] - 2021-06-05

### Security

- Security fix

## [2.0.0] - 2020-06-04

### Changed

- New more modern UI

## [1.1.0] - 2021-05-28

### Changed

- Refactoring

### Fixed

- Bugs fixes

## [1.0.0] - 2019-10-04

### Changed

- Last Jeff commit

[unreleased]: https://github.com/solevis/pixyship/compare/main...develop
[rolling]: https://github.com/solevis/pixyship/compare/2.9.0...main
[2.9.0]: https://github.com/solevis/pixyship/compare/2.8.0...2.9.0
[2.8.0]: https://github.com/solevis/pixyship/compare/2.7.0...2.8.0
[2.7.0]: https://github.com/solevis/pixyship/compare/2.6.0...2.7.0
[2.6.0]: https://github.com/solevis/pixyship/compare/2.5.0...2.6.0
[2.5.0]: https://github.com/solevis/pixyship/compare/2.4.0...2.5.0
[2.4.0]: https://github.com/solevis/pixyship/compare/2.3.0...2.4.0
[2.3.0]: https://github.com/solevis/pixyship/compare/2.2.6...2.3.0
[2.2.6]: https://github.com/solevis/pixyship/compare/2.2.5...2.2.6
[2.2.5]: https://github.com/solevis/pixyship/compare/2.2.4...2.2.5
[2.2.4]: https://github.com/solevis/pixyship/compare/2.2.3...2.2.4
[2.2.3]: https://github.com/solevis/pixyship/compare/2.2.2...2.2.3
[2.2.2]: https://github.com/solevis/pixyship/compare/2.2.1...2.2.2
[2.2.1]: https://github.com/solevis/pixyship/compare/2.2.0...2.2.1
[2.2.0]: https://github.com/solevis/pixyship/compare/2.1.10...2.2.0
[2.1.10]: https://github.com/solevis/pixyship/compare/2.1.9...2.1.10
[2.1.9]: https://github.com/solevis/pixyship/compare/2.1.8...2.1.9
[2.1.8]: https://github.com/solevis/pixyship/compare/2.1.7...2.1.8
[2.1.7]: https://github.com/solevis/pixyship/compare/2.1.6...2.1.7
[2.1.6]: https://github.com/solevis/pixyship/compare/2.1.5...2.1.6
[2.1.5]: https://github.com/solevis/pixyship/compare/2.1.4...2.1.5
[2.1.4]: https://github.com/solevis/pixyship/compare/2.1.3...2.1.4
[2.1.3]: https://github.com/solevis/pixyship/compare/2.1.2...2.1.3
[2.1.2]: https://github.com/solevis/pixyship/compare/2.1.1...2.1.2
[2.1.1]: https://github.com/solevis/pixyship/compare/2.1.0...2.1.1
[2.1.0]: https://github.com/solevis/pixyship/compare/2.0.3...2.1.0
[2.0.3]: https://github.com/solevis/pixyship/compare/2.0.2...2.0.3
[2.0.2]: https://github.com/solevis/pixyship/compare/2.0.1...2.0.2
[2.0.1]: https://github.com/solevis/pixyship/compare/2.0...2.0.1
[2.0.0]: https://github.com/solevis/pixyship/compare/1.1...2.0
[1.1.0]: https://github.com/solevis/pixyship/compare/1.0...1.1
[1.0.0]: https://github.com/solevis/pixyship/releases/tag/1.0
