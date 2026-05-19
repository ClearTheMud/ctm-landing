# WA Candidate Validation Report
**Generated:** 2026-05-19 07:25
**Data Source:** WA Secretary of State CandidateList.csv (voter.votewa.gov)
**Engagement:** C6S Data Quality Assessment — Engagement 7

## Executive Summary

Cross-referenced **1105** candidates in races.json against **1104** active SOS filings.
- **1104** candidates matched (100.0% SOS coverage)
- **0** SOS candidates missing from races.json
- **1** races.json candidates not found in SOS data
- **0** party affiliation mismatches
- **0** orphan directories (no races.json entry)
- **243** candidates missing directories
- **Overall Quality Score: 95.6%**

## Data Quality Scorecard

| Dimension | Score | Description |
|-----------|-------|-------------|
| Completeness | **100.0%** | SOS candidates present in races.json |
| Accuracy | **99.9%** | races.json candidates confirmed by SOS |
| Consistency | **100.0%** | Party affiliation agreement |
| Validity | **78.0%** | Candidates with valid directory structure |
| Uniqueness | **100.0%** | No duplicate candidate entries |
| **Overall** | **95.6%** | Average across dimensions |

## Finding: Candidates in races.json NOT in SOS Filings
**Priority:** Critical — may indicate withdrawn, unfiled, or name-mismatched candidates
**Count:** 1

### District Court Judge (1)

| Candidate | Race ID | Party |
|-----------|---------|-------|
| M. Brett Buckley | wa-thurston-district-court-judge-pos-3-2026 | nonpartisan |

## Finding: Directory Structure Discrepancies
**Priority:** Medium

### Missing Directories (243)
Candidates in races.json with no directory on disk.

| Candidate | Race ID | Expected URL |
|-----------|---------|--------------|
| David S. Mann | wa-appeals-div-1-dist-1-pos-5-2026 | /races/wa-appeals-div-1-dist-1-pos-5-2026/mann/ |
| Bill A. Bowman | wa-appeals-div-1-dist-1-pos-6-2026 | /races/wa-appeals-div-1-dist-1-pos-6-2026/bowman/ |
| Linda Coburn | wa-appeals-div-1-dist-2-pos-2-2026 | /races/wa-appeals-div-1-dist-2-pos-2-2026/coburn/ |
| Meng Li Che | wa-appeals-div-2-dist-1-pos-2-2026 | /races/wa-appeals-div-2-dist-1-pos-2-2026/che/ |
| Erik D. Price | wa-appeals-div-2-dist-2-pos-1-2026 | /races/wa-appeals-div-2-dist-2-pos-1-2026/price/ |
| Tracy Arlene Staab | wa-appeals-div-3-dist-1-pos-2-2026 | /races/wa-appeals-div-3-dist-1-pos-2-2026/staab/ |
| Tyson R. Hill | wa-appeals-div-3-dist-2-pos-1-2026 | /races/wa-appeals-div-3-dist-2-pos-1-2026/hill/ |
| Megan K. Murphy | wa-appeals-div-3-dist-3-pos-1-2026 | /races/wa-appeals-div-3-dist-3-pos-1-2026/murphy/ |
| Darcy Nelly | wa-asotin-pud-1-pud-commissioner-dist-1-2026 | /races/wa-asotin-pud-1-pud-commissioner-dist-1-2026/nelly/ |
| Joe Louis | wa-asotin-pud-1-pud-commissioner-dist-1-2026 | /races/wa-asotin-pud-1-pud-commissioner-dist-1-2026/louis/ |
| Tim Chartier | wa-bellingham-port-commissioner-dist-4-2026 | /races/wa-bellingham-port-commissioner-dist-4-2026/chartier/ |
| Samantha Cruz-Mendoza | wa-bellingham-port-commissioner-dist-4-2026 | /races/wa-bellingham-port-commissioner-dist-4-2026/cruz-mendoza/ |
| Paul Burrill | wa-bellingham-port-commissioner-dist-4-2026 | /races/wa-bellingham-port-commissioner-dist-4-2026/burrill/ |
| Dean Berkeley | wa-bellingham-port-commissioner-dist-4-2026 | /races/wa-bellingham-port-commissioner-dist-4-2026/berkeley/ |
| Tor Benson | wa-bellingham-port-commissioner-dist-4-2026 | /races/wa-bellingham-port-commissioner-dist-4-2026/benson/ |
| Jaden McConnell | wa-bellingham-port-commissioner-dist-4-2026 | /races/wa-bellingham-port-commissioner-dist-4-2026/mcconnell/ |
| Todd Lagestee | wa-bellingham-port-commissioner-dist-5-2026 | /races/wa-bellingham-port-commissioner-dist-5-2026/lagestee/ |
| Chris Elder | wa-bellingham-port-commissioner-dist-5-2026 | /races/wa-bellingham-port-commissioner-dist-5-2026/elder/ |
| Shawn Ensley | wa-bellingham-port-commissioner-dist-5-2026 | /races/wa-bellingham-port-commissioner-dist-5-2026/ensley/ |
| Randall Wood | wa-bellingham-port-commissioner-dist-5-2026 | /races/wa-bellingham-port-commissioner-dist-5-2026/wood/ |
| Spenser R. New | wa-bellingham-port-commissioner-dist-5-2026 | /races/wa-bellingham-port-commissioner-dist-5-2026/new/ |
| Jerry Burns | wa-bellingham-port-commissioner-dist-5-2026 | /races/wa-bellingham-port-commissioner-dist-5-2026/burns/ |
| Robert W. Grim | wa-benton-district-court-pos-1-2026 | /races/wa-benton-district-court-pos-1-2026/grim/ |
| Byron Moore | wa-benton-district-court-pos-1-2026 | /races/wa-benton-district-court-pos-1-2026/moore/ |
| John Andrew Bangerter | wa-benton-district-court-pos-2-2026 | /races/wa-benton-district-court-pos-2-2026/bangerter/ |
| Charles Short | wa-benton-district-court-pos-2-2026 | /races/wa-benton-district-court-pos-2-2026/short/ |
| Micah Valentine | wa-benton-pud-pud-commissioner-dist-2-2026 | /races/wa-benton-pud-pud-commissioner-dist-2-2026/valentine/ |
| Pat Tucker | wa-benton-pud-pud-commissioner-dist-2-2026 | /races/wa-benton-pud-pud-commissioner-dist-2-2026/tucker/ |
| Roy C. "Dewey"  Holliday | wa-benton-pud-pud-commissioner-dist-2-2026 | /races/wa-benton-pud-pud-commissioner-dist-2-2026/holliday/ |
| Jennifer Rancourt | wa-cascade-district-court-pos-1-2026 | /races/wa-cascade-district-court-pos-1-2026/rancourt/ |
| Rachelle Francis | wa-cascade-district-court-pos-2-2026 | /races/wa-cascade-district-court-pos-2-2026/francis/ |
| Colleen Frei | wa-chelan-pud-pud-commissioner-dist-1-2026 | /races/wa-chelan-pud-pud-commissioner-dist-1-2026/frei/ |
| Aaron Young | wa-chelan-pud-pud-commissioner-dist-1-2026 | /races/wa-chelan-pud-pud-commissioner-dist-1-2026/young/ |
| Kelly Allen | wa-chelan-pud-pud-commissioner-dist-b-2026 | /races/wa-chelan-pud-pud-commissioner-dist-b-2026/allen/ |
| Timothy Dalton | wa-clallam-pud-1-pud-commissioner-dist-2-2026 | /races/wa-clallam-pud-1-pud-commissioner-dist-2-2026/dalton/ |
| Missi Baker | wa-clallam-pud-1-pud-commissioner-dist-2-2026 | /races/wa-clallam-pud-1-pud-commissioner-dist-2-2026/baker/ |
| Rick Paschall | wa-clallam-pud-1-pud-commissioner-dist-2-2026 | /races/wa-clallam-pud-1-pud-commissioner-dist-2-2026/paschall/ |
| Randy Brackett | wa-clallam-pud-1-pud-commissioner-dist-2-2026 | /races/wa-clallam-pud-1-pud-commissioner-dist-2-2026/brackett/ |
| John W “Jack” Smith | wa-clallam-pud-1-pud-commissioner-dist-2-2026 | /races/wa-clallam-pud-1-pud-commissioner-dist-2-2026/smith/ |
| Dusti Arab | wa-clark-county-council-dist-1-2026 | /races/wa-clark-county-council-dist-1-2026/arab/ |
| Lukas Bardue | wa-clark-county-council-dist-1-2026 | /races/wa-clark-county-council-dist-1-2026/bardue/ |
| Glen Yung | wa-clark-county-council-dist-1-2026 | /races/wa-clark-county-council-dist-1-2026/yung/ |
| Bryan Shull | wa-clark-county-council-dist-1-2026 | /races/wa-clark-county-council-dist-1-2026/shull/ |
| Martin Pittioni | wa-clark-county-council-dist-2-2026 | /races/wa-clark-county-council-dist-2-2026/pittioni/ |
| Michelle Belkot | wa-clark-county-council-dist-2-2026 | /races/wa-clark-county-council-dist-2-2026/belkot/ |
| John Zingale | wa-clark-county-council-dist-2-2026 | /races/wa-clark-county-council-dist-2-2026/zingale/ |
| Peter Silliman | wa-clark-county-council-dist-5-2026 | /races/wa-clark-county-council-dist-5-2026/silliman/ |
| Troy McCoy | wa-clark-county-council-dist-5-2026 | /races/wa-clark-county-council-dist-5-2026/mccoy/ |
| Gordon Matthews | wa-clark-pud-pud-commissioner-dist-3-2026 | /races/wa-clark-pud-pud-commissioner-dist-3-2026/matthews/ |
| Kevin Roegner | wa-clark-pud-pud-commissioner-dist-3-2026 | /races/wa-clark-pud-pud-commissioner-dist-3-2026/roegner/ |
| Jane A. Van Dyke | wa-clark-pud-pud-commissioner-dist-3-2026 | /races/wa-clark-pud-pud-commissioner-dist-3-2026/dyke/ |
| Kimberly (Kim) Boggs | wa-columbia-district-court-pos-1-2026 | /races/wa-columbia-district-court-pos-1-2026/boggs/ |
| Bruce Pollock | wa-cowlitz-pud-pud-commissioner-dist-1-2026 | /races/wa-cowlitz-pud-pud-commissioner-dist-1-2026/pollock/ |
| Jill Karmy | wa-cowlitz-superior-court-pos-4-2026 | /races/wa-cowlitz-superior-court-pos-4-2026/karmy/ |
| Jacob Lervold | wa-cowlitz-superior-court-pos-4-2026 | /races/wa-cowlitz-superior-court-pos-4-2026/lervold/ |
| Molly Doneen Simpson | wa-douglas-pud-2-pud-commissioner-dist-2-2026 | /races/wa-douglas-pud-2-pud-commissioner-dist-2-2026/simpson/ |
| Nick Warner | wa-douglas-pud-2-pud-commissioner-dist-2-2026 | /races/wa-douglas-pud-2-pud-commissioner-dist-2-2026/warner/ |
| Anthony E. Howard | wa-everett-district-court-pos-1-2026 | /races/wa-everett-district-court-pos-1-2026/howard/ |
| Jennifer Millett | wa-everett-district-court-pos-2-2026 | /races/wa-everett-district-court-pos-2-2026/millett/ |
| Rick Leo | wa-evergreen-district-court-pos-1-2026 | /races/wa-evergreen-district-court-pos-1-2026/leo/ |
| Patricia Lyon | wa-evergreen-district-court-pos-2-2026 | /races/wa-evergreen-district-court-pos-2-2026/lyon/ |
| Thomas Franklin Webster | wa-ferry-pend-oreille-stevens-superior-court-pos-2-2026 | /races/wa-ferry-pend-oreille-stevens-superior-court-pos-2-2026/webster/ |
| ANDREW POOLER | wa-ferry-pud-pud-commissioner-dist-3-2026 | /races/wa-ferry-pud-pud-commissioner-dist-3-2026/pooler/ |
| Doug Aubertin | wa-ferry-pud-pud-commissioner-dist-3-2026 | /races/wa-ferry-pud-pud-commissioner-dist-3-2026/aubertin/ |
| Tim Nies | wa-franklin-pud-pud-commissioner-dist-2-2026 | /races/wa-franklin-pud-pud-commissioner-dist-2-2026/nies/ |
| Larry Schaapman | wa-grant-pud-pud-commissioner-dist-3-2026 | /races/wa-grant-pud-pud-commissioner-dist-3-2026/schaapman/ |
| Nelson Cox | wa-grant-pud-pud-commissioner-dist-b-2026 | /races/wa-grant-pud-pud-commissioner-dist-b-2026/cox/ |
| Jennifer Richardson | wa-grant-superior-court-pos-3-2026 | /races/wa-grant-superior-court-pos-3-2026/richardson/ |
| Trevor Bevier | wa-grant-superior-court-pos-3-2026 | /races/wa-grant-superior-court-pos-3-2026/bevier/ |
| Kenneth "Ken" Chadwick | wa-grant-superior-court-pos-3-2026 | /races/wa-grant-superior-court-pos-3-2026/chadwick/ |
| Jon Martin | wa-grays-harbor-pud-pud-commissioner-dist-3-2026 | /races/wa-grays-harbor-pud-pud-commissioner-dist-3-2026/martin/ |
| Keith Kisler | wa-jefferson-pud-pud-commissioner-dist-2-2026 | /races/wa-jefferson-pud-pud-commissioner-dist-2-2026/kisler/ |
| Michael Brittain | wa-jefferson-pud-pud-commissioner-dist-2-2026 | /races/wa-jefferson-pud-pud-commissioner-dist-2-2026/brittain/ |
| Toshiko Grace Hasegawa | wa-king-county-council-dist-2-2026 | /races/wa-king-county-council-dist-2-2026/hasegawa/ |
| Miriam Mboya | wa-king-county-council-dist-2-2026 | /races/wa-king-county-council-dist-2-2026/mboya/ |
| Rebecca Saldaña | wa-king-county-council-dist-2-2026 | /races/wa-king-county-council-dist-2-2026/saldaña/ |
| Jorge L. Barón | wa-king-county-council-dist-4-2026 | /races/wa-king-county-council-dist-4-2026/barón/ |
| Claudia Balducci | wa-king-county-council-dist-6-2026 | /races/wa-king-county-council-dist-6-2026/balducci/ |
| Teresa Mosqueda | wa-king-county-council-dist-8-2026 | /races/wa-king-county-council-dist-8-2026/mosqueda/ |
| Mia Jacobson | wa-king-county-council-dist-8-2026 | /races/wa-king-county-council-dist-8-2026/jacobson/ |
| Nick Duda | wa-king-county-council-dist-8-2026 | /races/wa-king-county-council-dist-8-2026/duda/ |
| Kristen L. Parcher | wa-king-district-court-pos-1-2026 | /races/wa-king-district-court-pos-1-2026/parcher/ |
| Chad E. Sleight | wa-king-district-court-pos-2-2026 | /races/wa-king-district-court-pos-2-2026/sleight/ |
| James B. Smith | wa-king-district-court-pos-3-2026 | /races/wa-king-district-court-pos-3-2026/smith/ |
| Leslie A. Lopez | wa-king-district-court-pos-4-2026 | /races/wa-king-district-court-pos-4-2026/lopez/ |
| Megan D. Peyton | wa-king-district-court-pos-5-2026 | /races/wa-king-district-court-pos-5-2026/peyton/ |
| Abigail E. Bartlett | wa-king-district-court-pos-6-2026 | /races/wa-king-district-court-pos-6-2026/bartlett/ |
| Jan Trasen | wa-king-electoral-northeast-pos-1-2026 | /races/wa-king-electoral-northeast-pos-1-2026/trasen/ |
| Josh Schaer | wa-king-electoral-northeast-pos-1-2026 | /races/wa-king-electoral-northeast-pos-1-2026/schaer/ |
| Bianca Tse | wa-king-electoral-northeast-pos-1-2026 | /races/wa-king-electoral-northeast-pos-1-2026/tse/ |
| Michelle Gehlsen | wa-king-electoral-northeast-pos-2-2026 | /races/wa-king-electoral-northeast-pos-2-2026/gehlsen/ |
| Lisa O'Toole | wa-king-electoral-northeast-pos-3-2026 | /races/wa-king-electoral-northeast-pos-3-2026/o'toole/ |
| Kevin Peck | wa-king-electoral-northeast-pos-4-2026 | /races/wa-king-electoral-northeast-pos-4-2026/peck/ |
| Jill Klinge | wa-king-electoral-northeast-pos-5-2026 | /races/wa-king-electoral-northeast-pos-5-2026/klinge/ |
| Denice Gagner | wa-king-electoral-northeast-pos-6-2026 | /races/wa-king-electoral-northeast-pos-6-2026/gagner/ |
| Peter Peaquin | wa-king-electoral-northeast-pos-7-2026 | /races/wa-king-electoral-northeast-pos-7-2026/peaquin/ |
| Raul Martinez | wa-king-electoral-shoreline-pos-1-2026 | /races/wa-king-electoral-shoreline-pos-1-2026/martinez/ |
| Karama H. Hawkins | wa-king-electoral-shoreline-pos-2-2026 | /races/wa-king-electoral-shoreline-pos-2-2026/hawkins/ |
| Leah Taguba | wa-king-electoral-southeast-pos-1-2026 | /races/wa-king-electoral-southeast-pos-1-2026/taguba/ |
| Matthew York | wa-king-electoral-southeast-pos-2-2026 | /races/wa-king-electoral-southeast-pos-2-2026/york/ |
| Tricia Grove Johnson | wa-king-electoral-southeast-pos-3-2026 | /races/wa-king-electoral-southeast-pos-3-2026/johnson/ |
| Corinna Harn | wa-king-electoral-southeast-pos-4-2026 | /races/wa-king-electoral-southeast-pos-4-2026/harn/ |
| Heather M. Barker | wa-king-electoral-southeast-pos-5-2026 | /races/wa-king-electoral-southeast-pos-5-2026/barker/ |
| Joshua C. Harris | wa-king-electoral-southeast-pos-5-2026 | /races/wa-king-electoral-southeast-pos-5-2026/harris/ |
| Rhonda Laumann | wa-king-electoral-southeast-pos-6-2026 | /races/wa-king-electoral-southeast-pos-6-2026/laumann/ |
| Brian Todd | wa-king-electoral-southwest-pos-1-2026 | /races/wa-king-electoral-southwest-pos-1-2026/todd/ |
| Andrea Samonica Jarmon | wa-king-electoral-southwest-pos-2-2026 | /races/wa-king-electoral-southwest-pos-2-2026/jarmon/ |
| Laurel Gibson | wa-king-electoral-southwest-pos-3-2026 | /races/wa-king-electoral-southwest-pos-3-2026/gibson/ |
| Mitch Greene | wa-king-electoral-southwest-pos-3-2026 | /races/wa-king-electoral-southwest-pos-3-2026/greene/ |
| Quita St. John | wa-king-electoral-southwest-pos-3-2026 | /races/wa-king-electoral-southwest-pos-3-2026/john/ |
| Harry Steinmetz | wa-king-electoral-southwest-pos-4-2026 | /races/wa-king-electoral-southwest-pos-4-2026/steinmetz/ |
| Fa'amomoi Masaniai, Jr. | wa-king-electoral-southwest-pos-4-2026 | /races/wa-king-electoral-southwest-pos-4-2026/masaniai/ |
| Renee Walls | wa-king-electoral-southwest-pos-5-2026 | /races/wa-king-electoral-southwest-pos-5-2026/walls/ |
| Noel Merfeld | wa-king-electoral-southwest-pos-5-2026 | /races/wa-king-electoral-southwest-pos-5-2026/merfeld/ |
| Nyjat Rose-Akins | wa-king-electoral-west-pos-1-2026 | /races/wa-king-electoral-west-pos-1-2026/rose-akins/ |
| Bardi Martin | wa-king-electoral-west-pos-1-2026 | /races/wa-king-electoral-west-pos-1-2026/martin/ |
| Kuljinder K. Dhillon | wa-king-electoral-west-pos-2-2026 | /races/wa-king-electoral-west-pos-2-2026/dhillon/ |
| Rebecca Robertson | wa-king-electoral-west-pos-3-2026 | /races/wa-king-electoral-west-pos-3-2026/robertson/ |
| Yvonne Chin | wa-king-electoral-west-pos-4-2026 | /races/wa-king-electoral-west-pos-4-2026/chin/ |
| Kristin Shotwell | wa-king-electoral-west-pos-5-2026 | /races/wa-king-electoral-west-pos-5-2026/shotwell/ |
| Kent Y. Liu | wa-king-superior-court-pos-20-2026 | /races/wa-king-superior-court-pos-20-2026/liu/ |
| Daniel York | wa-king-superior-court-pos-32-2026 | /races/wa-king-superior-court-pos-32-2026/york/ |
| Tenaya Scheinman | wa-king-superior-court-pos-45-2026 | /races/wa-king-superior-court-pos-45-2026/scheinman/ |
| Stacey Smith | wa-kitsap-pud-pud-commissioner-dist-2-2026 | /races/wa-kitsap-pud-pud-commissioner-dist-2-2026/smith/ |
| Rick Catlin | wa-kittitas-pud-1-pud-commissioner-dist-1-2026 | /races/wa-kittitas-pud-1-pud-commissioner-dist-1-2026/catlin/ |
| Rick L Hansen | wa-klickitat-east-district-court-pos-1-2026 | /races/wa-klickitat-east-district-court-pos-1-2026/hansen/ |
| Logan B. Siebert | wa-klickitat-pud-1-pud-commissioner-dist-3-2026 | /races/wa-klickitat-pud-1-pud-commissioner-dist-3-2026/siebert/ |
| Dan G. Gunkel | wa-klickitat-pud-1-pud-commissioner-dist-3-2026 | /races/wa-klickitat-pud-1-pud-commissioner-dist-3-2026/gunkel/ |
| Dan Christopher | wa-klickitat-pud-1-pud-commissioner-dist-3-2026 | /races/wa-klickitat-pud-1-pud-commissioner-dist-3-2026/christopher/ |
| Jeff Baker | wa-klickitat-west-district-court-pos-1-2026 | /races/wa-klickitat-west-district-court-pos-1-2026/baker/ |
| Steve Grega | wa-lewis-pud-pud-commissioner-dist-1-2026 | /races/wa-lewis-pud-pud-commissioner-dist-1-2026/grega/ |
| Jeff Baine | wa-lewis-pud-pud-commissioner-dist-1-2026 | /races/wa-lewis-pud-pud-commissioner-dist-1-2026/baine/ |
| Ben Kostick | wa-lewis-pud-pud-commissioner-dist-1-2026 | /races/wa-lewis-pud-pud-commissioner-dist-1-2026/kostick/ |
| Paul Sander | wa-lower-county-district-court-pos-1-2026 | /races/wa-lower-county-district-court-pos-1-2026/sander/ |
| Ronald S. Gold | wa-mason-pud-1-pud-commissioner-dist-2-2026 | /races/wa-mason-pud-1-pud-commissioner-dist-2-2026/gold/ |
| Mick Sprouffske | wa-mason-pud-3-pud-commissioner-dist-2-2026 | /races/wa-mason-pud-3-pud-commissioner-dist-2-2026/sprouffske/ |
| Randy Neatherlin | wa-mason-pud-3-pud-commissioner-dist-2-2026 | /races/wa-mason-pud-3-pud-commissioner-dist-2-2026/neatherlin/ |
| Scott Vejraska | wa-okanogan-pud-pud-commissioner-dist-1-2026 | /races/wa-okanogan-pud-pud-commissioner-dist-1-2026/vejraska/ |
| Steven Gadd | wa-okanogan-pud-pud-commissioner-dist-1-2026 | /races/wa-okanogan-pud-pud-commissioner-dist-1-2026/gadd/ |
| Rachel Hong | wa-okanogan-superior-court-pos-2-2026 | /races/wa-okanogan-superior-court-pos-2-2026/hong/ |
| Pamela "Pam" Hickey | wa-pacific-pud-2-pud-commissioner-dist-1-2026 | /races/wa-pacific-pud-2-pud-commissioner-dist-1-2026/hickey/ |
| Hans-Joachim Engelke | wa-pasco-port-commissioner-dist-3-2026 | /races/wa-pasco-port-commissioner-dist-3-2026/engelke/ |
| Gerry David Bradbury | wa-pend-oreille-pud-1-pud-commissioner-dist-2-2026 | /races/wa-pend-oreille-pud-1-pud-commissioner-dist-2-2026/bradbury/ |
| Ernie Hood | wa-pend-oreille-pud-1-pud-commissioner-dist-2-2026 | /races/wa-pend-oreille-pud-1-pud-commissioner-dist-2-2026/hood/ |
| Tracy Rutt | wa-pend-oreille-pud-1-pud-commissioner-dist-2-2026 | /races/wa-pend-oreille-pud-1-pud-commissioner-dist-2-2026/rutt/ |
| Jerome O'Leary | wa-pierce-county-council-dist-1-2026 | /races/wa-pierce-county-council-dist-1-2026/o'leary/ |
| Terrance Mayers | wa-pierce-county-council-dist-1-2026 | /races/wa-pierce-county-council-dist-1-2026/mayers/ |
| Kenneth King | wa-pierce-county-council-dist-1-2026 | /races/wa-pierce-county-council-dist-1-2026/king/ |
| Kelsey Barrans | wa-pierce-county-council-dist-1-2026 | /races/wa-pierce-county-council-dist-1-2026/barrans/ |
| Bryan Yambe | wa-pierce-county-council-dist-5-2026 | /races/wa-pierce-county-council-dist-5-2026/yambe/ |
| Bettina Gese | wa-pierce-county-council-dist-5-2026 | /races/wa-pierce-county-council-dist-5-2026/gese/ |
| Chuck West | wa-pierce-county-council-dist-7-2026 | /races/wa-pierce-county-council-dist-7-2026/west/ |
| Brenda Lykins | wa-pierce-county-council-dist-7-2026 | /races/wa-pierce-county-council-dist-7-2026/lykins/ |
| Ann E. Jolie | wa-pierce-county-council-dist-7-2026 | /races/wa-pierce-county-council-dist-7-2026/jolie/ |
| Kevin A. McCann | wa-pierce-district-court-pos-1-2026 | /races/wa-pierce-district-court-pos-1-2026/mccann/ |
| Claire Sussman | wa-pierce-district-court-pos-2-2026 | /races/wa-pierce-district-court-pos-2-2026/sussman/ |
| Lizanne Padula | wa-pierce-district-court-pos-3-2026 | /races/wa-pierce-district-court-pos-3-2026/padula/ |
| Neil Horibe | wa-pierce-district-court-pos-4-2026 | /races/wa-pierce-district-court-pos-4-2026/horibe/ |
| Dwayne Christopher | wa-pierce-district-court-pos-5-2026 | /races/wa-pierce-district-court-pos-5-2026/christopher/ |
| Karl Williams | wa-pierce-district-court-pos-6-2026 | /races/wa-pierce-district-court-pos-6-2026/williams/ |
| Eric J. Lawless | wa-pierce-district-court-pos-7-2026 | /races/wa-pierce-district-court-pos-7-2026/lawless/ |
| Mike Sommerfeld | wa-pierce-district-court-pos-7-2026 | /races/wa-pierce-district-court-pos-7-2026/sommerfeld/ |
| Pam Nogueira | wa-pierce-district-court-pos-7-2026 | /races/wa-pierce-district-court-pos-7-2026/nogueira/ |
| Sven Nelson | wa-pierce-district-court-pos-8-2026 | /races/wa-pierce-district-court-pos-8-2026/nelson/ |
| James Armstrong | wa-pierce-district-court-pos-8-2026 | /races/wa-pierce-district-court-pos-8-2026/armstrong/ |
| Doris Walkins | wa-pierce-superior-court-pos-17-2026 | /races/wa-pierce-superior-court-pos-17-2026/walkins/ |
| Todd Samuel | wa-richland-city-council-pos-4-2026 | /races/wa-richland-city-council-pos-4-2026/samuel/ |
| David Tveraas | wa-richland-city-council-pos-4-2026 | /races/wa-richland-city-council-pos-4-2026/tveraas/ |
| Kyle Saltz | wa-richland-city-council-pos-4-2026 | /races/wa-richland-city-council-pos-4-2026/saltz/ |
| Ragan Faylor | wa-richland-city-council-pos-4-2026 | /races/wa-richland-city-council-pos-4-2026/faylor/ |
| Mary S. Lipton | wa-richland-city-council-pos-4-2026 | /races/wa-richland-city-council-pos-4-2026/lipton/ |
| Julie Kang | wa-seattle-city-council-pos-5-2026 | /races/wa-seattle-city-council-pos-5-2026/kang/ |
| Silas James | wa-seattle-city-council-pos-5-2026 | /races/wa-seattle-city-council-pos-5-2026/james/ |
| Nilu Jenks | wa-seattle-city-council-pos-5-2026 | /races/wa-seattle-city-council-pos-5-2026/jenks/ |
| Dimitri Georgakopoulos | wa-seattle-city-council-pos-5-2026 | /races/wa-seattle-city-council-pos-5-2026/georgakopoulos/ |
| Cat McDowall | wa-seattle-municipal-court-pos-1-2026 | /races/wa-seattle-municipal-court-pos-1-2026/mcdowall/ |
| Katharine Edwards | wa-seattle-municipal-court-pos-2-2026 | /races/wa-seattle-municipal-court-pos-2-2026/edwards/ |
| Pooja Vaddadi | wa-seattle-municipal-court-pos-3-2026 | /races/wa-seattle-municipal-court-pos-3-2026/vaddadi/ |
| Anita Crawford-Willis | wa-seattle-municipal-court-pos-4-2026 | /races/wa-seattle-municipal-court-pos-4-2026/crawford-willis/ |
| Garmon Newsom | wa-seattle-municipal-court-pos-5-2026 | /races/wa-seattle-municipal-court-pos-5-2026/newsom/ |
| Lindsay Calkins | wa-seattle-municipal-court-pos-5-2026 | /races/wa-seattle-municipal-court-pos-5-2026/calkins/ |
| Gabe Rothstein | wa-seattle-municipal-court-pos-5-2026 | /races/wa-seattle-municipal-court-pos-5-2026/rothstein/ |
| Shantrice Anderson | wa-seattle-municipal-court-pos-6-2026 | /races/wa-seattle-municipal-court-pos-6-2026/anderson/ |
| Damon Shadid | wa-seattle-municipal-court-pos-7-2026 | /races/wa-seattle-municipal-court-pos-7-2026/shadid/ |
| Andrew Miller | wa-skagit-pud-pud-commissioner-dist-1-2026 | /races/wa-skagit-pud-pud-commissioner-dist-1-2026/miller/ |
| Spencer Roozen | wa-skagit-pud-pud-commissioner-dist-1-2026 | /races/wa-skagit-pud-pud-commissioner-dist-1-2026/roozen/ |
| Mary Crandall | wa-skagit-superior-court-pos-4-2026 | /races/wa-skagit-superior-court-pos-4-2026/crandall/ |
| Liz Green | wa-skamania-pud-pud-commissioner-dist-3-2026 | /races/wa-skamania-pud-pud-commissioner-dist-3-2026/green/ |
| Addison Dillon | wa-skamania-pud-pud-commissioner-dist-3-2026 | /races/wa-skamania-pud-pud-commissioner-dist-3-2026/dillon/ |
| Wade S. Samuelson | wa-snohomish-district-court-pos-1-2026 | /races/wa-snohomish-district-court-pos-1-2026/samuelson/ |
| RW Buzzard | wa-snohomish-district-court-pos-2-2026 | /races/wa-snohomish-district-court-pos-2-2026/buzzard/ |
| Scott Harmer | wa-snohomish-north-district-court-pos-1-2026 | /races/wa-snohomish-north-district-court-pos-1-2026/harmer/ |
| Sid Logan | wa-snohomish-pud-1-pud-commissioner-dist-1-2026 | /races/wa-snohomish-pud-1-pud-commissioner-dist-1-2026/logan/ |
| Janet St Clair | wa-snohomish-pud-1-pud-commissioner-dist-1-2026 | /races/wa-snohomish-pud-1-pud-commissioner-dist-1-2026/clair/ |
| Bruce King | wa-snohomish-pud-1-pud-commissioner-dist-1-2026 | /races/wa-snohomish-pud-1-pud-commissioner-dist-1-2026/king/ |
| Elizabeth Fraser | wa-snohomish-south-district-court-pos-1-2026 | /races/wa-snohomish-south-district-court-pos-1-2026/fraser/ |
| Jeffrey D. Goodwin | wa-snohomish-south-district-court-pos-2-2026 | /races/wa-snohomish-south-district-court-pos-2-2026/goodwin/ |
| Matthew Baldock | wa-snohomish-south-district-court-pos-3-2026 | /races/wa-snohomish-south-district-court-pos-3-2026/baldock/ |
| Mindy Walker | wa-spokane-district-court-pos-1-2026 | /races/wa-spokane-district-court-pos-1-2026/walker/ |
| Kevin G. Blondin | wa-spokane-district-court-pos-1-2026 | /races/wa-spokane-district-court-pos-1-2026/blondin/ |
| M. Jamie Imboden | wa-spokane-district-court-pos-2-2026 | /races/wa-spokane-district-court-pos-2-2026/imboden/ |
| Christopher Eastwood | wa-spokane-district-court-pos-3-2026 | /races/wa-spokane-district-court-pos-3-2026/eastwood/ |
| Nicole G. Knowles | wa-spokane-district-court-pos-3-2026 | /races/wa-spokane-district-court-pos-3-2026/knowles/ |
| Candie M. Dibble | wa-spokane-superior-court-pos-3-2026 | /races/wa-spokane-superior-court-pos-3-2026/dibble/ |
| Howie Kubik | wa-stevens-pud-1-pud-commissioner-dist-2-2026 | /races/wa-stevens-pud-1-pud-commissioner-dist-2-2026/kubik/ |
| Andrea Morgan | wa-stevens-pud-1-pud-commissioner-dist-2-2026 | /races/wa-stevens-pud-1-pud-commissioner-dist-2-2026/morgan/ |
| Anne Melani Bremner | wa-supreme-court-justice-pos-1-2026 | /races/wa-supreme-court-justice-pos-1-2026/bremner/ |
| Colleen Melody | wa-supreme-court-justice-pos-1-2026 | /races/wa-supreme-court-justice-pos-1-2026/melody/ |
| Laura Christensen Colberg | wa-supreme-court-justice-pos-1-2026 | /races/wa-supreme-court-justice-pos-1-2026/colberg/ |
| Scott Edwards | wa-supreme-court-justice-pos-1-2026 | /races/wa-supreme-court-justice-pos-1-2026/edwards/ |
| Jaime Michelle Hawk | wa-supreme-court-justice-pos-3-2026 | /races/wa-supreme-court-justice-pos-3-2026/hawk/ |
| David Stevens | wa-supreme-court-justice-pos-3-2026 | /races/wa-supreme-court-justice-pos-3-2026/stevens/ |
| Mike Diaz | wa-supreme-court-justice-pos-3-2026 | /races/wa-supreme-court-justice-pos-3-2026/diaz/ |
| Ian Birk | wa-supreme-court-justice-pos-4-2026 | /races/wa-supreme-court-justice-pos-4-2026/birk/ |
| Sean O'Donnell | wa-supreme-court-justice-pos-4-2026 | /races/wa-supreme-court-justice-pos-4-2026/o'donnell/ |
| Greg Miller | wa-supreme-court-justice-pos-5-2026 | /races/wa-supreme-court-justice-pos-5-2026/miller/ |
| Theo Angelis | wa-supreme-court-justice-pos-5-2026 | /races/wa-supreme-court-justice-pos-5-2026/angelis/ |
| Dave Larson | wa-supreme-court-justice-pos-5-2026 | /races/wa-supreme-court-justice-pos-5-2026/larson/ |
| Sharonda Amamilo | wa-supreme-court-justice-pos-5-2026 | /races/wa-supreme-court-justice-pos-5-2026/amamilo/ |
| David R Shelvey | wa-supreme-court-justice-pos-7-2026 | /races/wa-supreme-court-justice-pos-7-2026/shelvey/ |
| Debra L. Stephens | wa-supreme-court-justice-pos-7-2026 | /races/wa-supreme-court-justice-pos-7-2026/stephens/ |
| Karim A. Merchant | wa-supreme-court-justice-pos-7-2026 | /races/wa-supreme-court-justice-pos-7-2026/merchant/ |
| Todd A. Bloom | wa-supreme-court-justice-pos-7-2026 | /races/wa-supreme-court-justice-pos-7-2026/bloom/ |
| Dee Sonntag | wa-tacoma-municipal-court-pos-1-2026 | /races/wa-tacoma-municipal-court-pos-1-2026/sonntag/ |
| Sergio C. Flores | wa-tacoma-municipal-court-pos-2-2026 | /races/wa-tacoma-municipal-court-pos-2-2026/flores/ |
| Steven J. Krupa | wa-tacoma-municipal-court-pos-3-2026 | /races/wa-tacoma-municipal-court-pos-3-2026/krupa/ |
| Claire A. Bradley | wa-thurston-district-court-pos-1-2026 | /races/wa-thurston-district-court-pos-1-2026/bradley/ |
| Gina M Buskirk | wa-thurston-district-court-pos-2-2026 | /races/wa-thurston-district-court-pos-2-2026/buskirk/ |
| Shane R. Seaman | wa-thurston-district-court-pos-3-2026 | /races/wa-thurston-district-court-pos-3-2026/seaman/ |
| Kevin P Kelly | wa-thurston-district-court-pos-4-2026 | /races/wa-thurston-district-court-pos-4-2026/kelly/ |
| Troy Kirby | wa-thurston-pud-pud-commissioner-dist-1-2026 | /races/wa-thurston-pud-pud-commissioner-dist-1-2026/kirby/ |
| Bruce D. Wilkinson, Jr. | wa-thurston-pud-pud-commissioner-dist-1-2026 | /races/wa-thurston-pud-pud-commissioner-dist-1-2026/wilkinson/ |
| Jim Campbell | wa-thurston-pud-pud-commissioner-dist-1-2026 | /races/wa-thurston-pud-pud-commissioner-dist-1-2026/campbell/ |
| Jeff Curry | wa-thurston-pud-pud-commissioner-dist-3-2026 | /races/wa-thurston-pud-pud-commissioner-dist-3-2026/curry/ |
| Christopher Pettit | wa-thurston-pud-pud-commissioner-dist-3-2026 | /races/wa-thurston-pud-pud-commissioner-dist-3-2026/pettit/ |
| Nancy R. McAllister | wa-thurston-south-district-court-pos-1-2026 | /races/wa-thurston-south-district-court-pos-1-2026/mcallister/ |
| Craig Juris | wa-upper-county-district-court-pos-1-2026 | /races/wa-upper-county-district-court-pos-1-2026/juris/ |
| Gene Healy | wa-wahkiakum-pud-pud-commissioner-dist-1-2026 | /races/wa-wahkiakum-pud-pud-commissioner-dist-1-2026/healy/ |
| Alex Schodowski | wa-whatcom-1-district-court-pos-1-2026 | /races/wa-whatcom-1-district-court-pos-1-2026/schodowski/ |
| Patrick David Murphy | wa-whatcom-1-district-court-pos-1-2026 | /races/wa-whatcom-1-district-court-pos-1-2026/murphy/ |
| BRUCE HANIFY | wa-whatcom-2-district-court-pos-2-2026 | /races/wa-whatcom-2-district-court-pos-2-2026/hanify/ |
| Eddy Ury | wa-whatcom-pud-1-pud-commissioner-dist-1-2026 | /races/wa-whatcom-pud-1-pud-commissioner-dist-1-2026/ury/ |
| Frank Imhof | wa-whatcom-pud-1-pud-commissioner-dist-1-2026 | /races/wa-whatcom-pud-1-pud-commissioner-dist-1-2026/imhof/ |

## Finding: SOS Races Not in races.json (Federal/Legislative)
**Priority:** Medium — filed races without race directory
**Count:** 98

| Race Type | District | Candidates |
|-----------|----------|------------|
| City Council | City Of Richland|4 | 5: Todd Samuel, David Tveraas, Kyle Saltz, Ragan Faylor, Mary S. Lipton |
| City Council | SEATTLE CITY COUNCIL DISTRICT 5|5 | 4: Julie Kang, Silas James, Nilu Jenks, Dimitri Georgakopoulos |
| County Council | COUNTY COUNCIL DISTRICT NO. 1|1 | 4: Jerome O'Leary, Terrance Mayers, Kenneth King, Kelsey Barrans |
| County Council | COUNTY COUNCIL DISTRICT NO. 5|5 | 2: Bryan Yambe, Bettina Gese |
| County Council | COUNTY COUNCIL DISTRICT NO. 7|7 | 3: Chuck West, Brenda Lykins, Ann E. Jolie |
| County Council | COUNTY COUNCILOR DISTRICT NO. 1|1 | 4: Dusti Arab, Lukas Bardue, Glen Yung, Bryan Shull |
| County Council | COUNTY COUNCILOR DISTRICT NO. 2|2 | 3: Martin Pittioni, Michelle Belkot, John Zingale |
| County Council | COUNTY COUNCILOR DISTRICT NO. 5|5 | 2: Peter Silliman, Troy McCoy |
| County Council | County Council District No. 2|2 | 3: Toshiko Grace Hasegawa, Miriam Mboya, Rebecca Saldaña |
| County Council | County Council District No. 4|4 | 1: Jorge L. Barón |
| County Council | County Council District No. 6|6 | 1: Claudia Balducci |
| County Council | County Council District No. 8|8 | 3: Teresa Mosqueda, Mia Jacobson, Nick Duda |
| Director | Director of Community Development | 1: Bruce Emery |
| Director | Director of Elections | 1: Julie Wise |
| KC Electoral Court | NORTHEAST ELECTORAL DISTRICT|1 | 3: Jan Trasen, Josh Schaer, Bianca Tse |
| KC Electoral Court | NORTHEAST ELECTORAL DISTRICT|2 | 1: Michelle Gehlsen |
| KC Electoral Court | NORTHEAST ELECTORAL DISTRICT|3 | 1: Lisa O'Toole |
| KC Electoral Court | NORTHEAST ELECTORAL DISTRICT|4 | 1: Kevin Peck |
| KC Electoral Court | NORTHEAST ELECTORAL DISTRICT|5 | 1: Jill Klinge |
| KC Electoral Court | NORTHEAST ELECTORAL DISTRICT|6 | 1: Denice Gagner |
| KC Electoral Court | NORTHEAST ELECTORAL DISTRICT|7 | 1: Peter Peaquin |
| KC Electoral Court | SHORELINE ELECTORAL DISTRICT|1 | 1: Raul Martinez |
| KC Electoral Court | SHORELINE ELECTORAL DISTRICT|2 | 1: Karama H. Hawkins |
| KC Electoral Court | SOUTHEAST ELECTORAL DISTRICT|1 | 1: Leah Taguba |
| KC Electoral Court | SOUTHEAST ELECTORAL DISTRICT|2 | 1: Matthew York |
| KC Electoral Court | SOUTHEAST ELECTORAL DISTRICT|3 | 1: Tricia Grove Johnson |
| KC Electoral Court | SOUTHEAST ELECTORAL DISTRICT|4 | 1: Corinna Harn |
| KC Electoral Court | SOUTHEAST ELECTORAL DISTRICT|5 | 2: Heather M. Barker, Joshua C. Harris |
| KC Electoral Court | SOUTHEAST ELECTORAL DISTRICT|6 | 1: Rhonda Laumann |
| KC Electoral Court | SOUTHWEST ELECTORAL DISTRICT|1 | 1: Brian Todd |
| KC Electoral Court | SOUTHWEST ELECTORAL DISTRICT|2 | 1: Andrea Samonica Jarmon |
| KC Electoral Court | SOUTHWEST ELECTORAL DISTRICT|3 | 3: Laurel Gibson, Mitch Greene, Quita St. John |
| KC Electoral Court | SOUTHWEST ELECTORAL DISTRICT|4 | 2: Harry Steinmetz, Fa'amomoi Masaniai, Jr. |
| KC Electoral Court | SOUTHWEST ELECTORAL DISTRICT|5 | 2: Renee Walls, Noel Merfeld |
| KC Electoral Court | WEST ELECTORAL DISTRICT|1 | 2: Nyjat Rose-Akins, Bardi Martin |
| KC Electoral Court | WEST ELECTORAL DISTRICT|2 | 1: Kuljinder K. Dhillon |
| KC Electoral Court | WEST ELECTORAL DISTRICT|3 | 1: Rebecca Robertson |
| KC Electoral Court | WEST ELECTORAL DISTRICT|4 | 1: Yvonne Chin |
| KC Electoral Court | WEST ELECTORAL DISTRICT|5 | 1: Kristin Shotwell |
| Municipal Court | CITY OF TACOMA|1 | 1: Dee Sonntag |
| Municipal Court | CITY OF TACOMA|2 | 1: Sergio C. Flores |
| Municipal Court | CITY OF TACOMA|3 | 1: Steven J. Krupa |
| Municipal Court | City of Seattle|1 | 1: Cat McDowall |
| Municipal Court | City of Seattle|2 | 1: Katharine Edwards |
| Municipal Court | City of Seattle|3 | 1: Pooja Vaddadi |
| Municipal Court | City of Seattle|4 | 1: Anita Crawford-Willis |
| Municipal Court | City of Seattle|5 | 3: Garmon Newsom, Lindsay Calkins, Gabe Rothstein |
| Municipal Court | City of Seattle|6 | 1: Shantrice Anderson |
| Municipal Court | City of Seattle|7 | 1: Damon Shadid |
| PUD Commissioner | CLARK PUBLIC UTILITIES - COMM. DIST. #3|3 | 3: Gordon Matthews, Kevin Roegner, Jane A. Van Dyke |
| PUD Commissioner | GRANT COUNTY PUD COMM DIST #3|3 | 1: Larry Schaapman |
| PUD Commissioner | GRANT COUNTY PUD DIST #B|b | 1: Nelson Cox |
| PUD Commissioner | OK PUBLIC UTILITY DISTRICT 01|01 | 2: Scott Vejraska, Steven Gadd |
| PUD Commissioner | PUBLIC UTILITY DIST 2|2 | 2: Molly Doneen Simpson, Nick Warner |
| PUD Commissioner | PUBLIC UTILITY DISTRICT #1|1 | 2: Darcy Nelly, Joe Louis |
| PUD Commissioner | PUBLIC UTILITY DISTRICT 1, 1|1 | 1: Rick Catlin |
| PUD Commissioner | PUBLIC UTILITY DISTRICT COMMISSIONER #3|3 | 3: Logan B. Siebert, Dan G. Gunkel, Dan Christopher |
| PUD Commissioner | PUBLIC UTILITY DISTRICT COMMISSIONER 1|1 | 2: Colleen Frei, Aaron Young |
| PUD Commissioner | PUBLIC UTILITY DISTRICT COMMISSIONER B|b | 1: Kelly Allen |
| PUD Commissioner | PUD #1|1 | 1: Gene Healy |
| PUD Commissioner | PUD #3|3 | 2: ANDREW POOLER, Doug Aubertin |
| PUD Commissioner | PUD 1 COMMISSIONER DIST 2|2 | 5: Timothy Dalton, Missi Baker, Rick Paschall, Randy Brackett, John W “Jack” Smith |
| PUD Commissioner | PUD 2 Commissioner District #1|1 | 1: Pamela "Pam" Hickey |
| PUD Commissioner | PUD COMMISSIONER DIST. 3|3 | 2: Liz Green, Addison Dillon |
| PUD Commissioner | PUD COMMISSIONER DISTRICT 1|1 | 3: Sid Logan, Janet St Clair, Bruce King |
| PUD Commissioner | PUD COMMISSIONER DISTRICT NO. 1|1 | 3: Troy Kirby, Bruce D. Wilkinson, Jr., Jim Campbell |
| PUD Commissioner | PUD COMMISSIONER DISTRICT NO. 3|3 | 2: Jeff Curry, Christopher Pettit |
| PUD Commissioner | PUD Comm. Dist. 3|3 | 1: Jon Martin |
| PUD Commissioner | PUD Commissioner Dist 2|2 | 3: Micah Valentine, Pat Tucker, Roy C. "Dewey"  Holliday |
| PUD Commissioner | PUD Commissioner District 2|2 | 1: Stacey Smith |
| PUD Commissioner | PUD DIST COMM #1|1 | 3: Steve Grega, Jeff Baine, Ben Kostick |
| PUD Commissioner | PUD District 2|2 | 1: Tim Nies |
| PUD Commissioner | PUD No. 1 Commissioner District 1|1 | 2: Eddy Ury, Frank Imhof |
| PUD Commissioner | PUD1-COMMISSIONER DISTRICT 2|2 | 2: Howie Kubik, Andrea Morgan |
| PUD Commissioner | Public Comm District - 02|02 | 3: Gerry David Bradbury, Ernie Hood, Tracy Rutt |
| PUD Commissioner | Public Utility Dist 1-2|12 | 1: Ronald S. Gold |
| PUD Commissioner | Public Utility Dist 3-2|32 | 2: Mick Sprouffske, Randy Neatherlin |
| PUD Commissioner | Public Utility District - Commissioner No. 2|2 | 2: Keith Kisler, Michael Brittain |
| PUD Commissioner | Public Utility District Commissioner District 1|1 | 1: Bruce Pollock |
| PUD Commissioner | SKAGIT COUNTY PUD COMMISSIONER DIST 1|1 | 2: Andrew Miller, Spencer Roozen |
| Port Commissioner | PASCO PORT DISTRICT 3|3 | 1: Hans-Joachim Engelke |
| Port Commissioner | Port of Bellingham Commissioner District 4|4 | 6: Tim Chartier, Samantha Cruz-Mendoza, Paul Burrill, Dean Berkeley, Tor Benson (+1 more) |
| Port Commissioner | Port of Bellingham Commissioner District 5|5 | 6: Todd Lagestee, Chris Elder, Shawn Ensley, Randall Wood, Spenser R. New (+1 more) |
| Superior Court | Cowlitz Superior Court|4 | 2: Jill Karmy, Jacob Lervold |
| Superior Court | Ferry, Pend Oreille, Stevens Superior Court|2 | 1: Thomas Franklin Webster |
| Superior Court | Grant Superior Court|03 | 3: Jennifer Richardson, Trevor Bevier, Kenneth "Ken" Chadwick |
| Superior Court | KING COUNTY SUPERIOR COURT|20 | 1: Kent Y. Liu |
| Superior Court | KING COUNTY SUPERIOR COURT|32 | 1: Daniel York |
| Superior Court | KING COUNTY SUPERIOR COURT|45 | 1: Tenaya Scheinman |
| Superior Court | Okanogan Superior Court|2 | 1: Rachel Hong |
| Superior Court | Pierce Superior Court|17 | 1: Doris Walkins |
| Superior Court | Skagit Superior Court|4 | 1: Mary Crandall |
| Superior Court | Spokane Superior Court|3 | 1: Candie M. Dibble |
| Supreme Court | 01 | 4: Anne Melani Bremner, Colleen Melody, Laura Christensen Colberg, Scott Edwards |
| Supreme Court | 03 | 3: Jaime Michelle Hawk, David Stevens, Mike Diaz |
| Supreme Court | 04 | 2: Ian Birk, Sean O'Donnell |
| Supreme Court | 05 | 4: Greg Miller, Theo Angelis, Dave Larson, Sharonda Amamilo |
| Supreme Court | 07 | 4: David R Shelvey, Debra L. Stephens, Karim A. Merchant, Todd A. Bloom |

## Methodology

### Matching Strategy
1. **Pass 1 — Exact name + district** (federal/legislative races with district numbers)
2. **Pass 2 — Exact name + race category** (county races without district keys)
3. **Pass 3 — Fuzzy name match** (>=75% similarity within same race category)

### Normalization Applied
- Names: uppercase, strip nicknames/suffixes (Jr, Sr, III), collapse whitespace
- Parties: DEMOCRATIC/DEMOCRAT/LABOR DEMOCRAT→dem, REPUBLICAN/GOP→rep, etc.
- Race types: 71 CSV variations mapped to 15 normalized categories
- Withdrawn candidates excluded from CSV analysis

### Limitations
- County-level matching relies on name matching (no county field in SOS CSV export)
- Fuzzy matching may produce false positives for common surnames
- PUD, Port, Municipal, and Superior/Appellate court races excluded from gap analysis
