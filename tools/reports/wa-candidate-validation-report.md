# WA Candidate Validation Report
**Generated:** 2026-05-17 22:44
**Data Source:** WA Secretary of State CandidateList.csv (voter.votewa.gov)
**Engagement:** C6S Data Quality Assessment — Engagement 7

## Executive Summary

Cross-referenced **863** candidates in races.json against **1104** active SOS filings.
- **861** candidates matched (78.0% SOS coverage)
- **243** SOS candidates missing from races.json
- **2** races.json candidates not found in SOS data
- **1** party affiliation mismatches
- **0** orphan directories (no races.json entry)
- **0** candidates missing directories
- **Overall Quality Score: 95.5%**

## Data Quality Scorecard

| Dimension | Score | Description |
|-----------|-------|-------------|
| Completeness | **78.0%** | SOS candidates present in races.json |
| Accuracy | **99.8%** | races.json candidates confirmed by SOS |
| Consistency | **99.9%** | Party affiliation agreement |
| Validity | **100.0%** | Candidates with valid directory structure |
| Uniqueness | **100.0%** | No duplicate candidate entries |
| **Overall** | **95.5%** | Average across dimensions |

## Finding: Party Affiliation Mismatches
**Priority:** High
**Count:** 1

| Candidate | Race ID | SOS Party | Our Party | SOS Raw |
|-----------|---------|-----------|-----------|---------|
| Roman Buermann | wa-yakima-commissioner-district-1-2026 | other | unknown | TEA |

## Finding: Candidates in races.json NOT in SOS Filings
**Priority:** Critical — may indicate withdrawn, unfiled, or name-mismatched candidates
**Count:** 2

### District Court Judge (2)

| Candidate | Race ID | Party |
|-----------|---------|-------|
| David Mistachkin | wa-grays-harbor-district-court-1-2026 | nonpartisan |
| M. Brett Buckley | wa-thurston-district-court-judge-pos-3-2026 | nonpartisan |

## Finding: SOS Candidates Missing from races.json
**Priority:** High — filed candidates not yet in our database
**Count:** 243

### Commissioner (73)

| Candidate | Party | Race (raw) | District |
|-----------|-------|------------|----------|
| Pamela "Pam" Hickey |  | PUBLIC UTILITY COMMISSIONER #01 | PUD 2 Commissioner District #1 |
| Aaron Young |  | PUBLIC UTILITY DIST COMMISSIONER DIST 1 | PUBLIC UTILITY DISTRICT COMMISSIONER 1 |
| Andrew Miller |  | Commissioner 1 | SKAGIT COUNTY PUD COMMISSIONER DIST 1 |
| Ben Kostick |  | Commissioner District 1 | PUD DIST COMM #1 |
| Bruce D. Wilkinson, Jr. |  | Commissioner, District No. 1 | PUD COMMISSIONER DISTRICT NO. 1 |
| Bruce King |  | Commissioner District 1 | PUD COMMISSIONER DISTRICT 1 |
| Bruce Pollock |  | Commissioner District 1 | Public Utility District Commissioner District 1 |
| Colleen Frei |  | PUBLIC UTILITY DIST COMMISSIONER DIST 1 | PUBLIC UTILITY DISTRICT COMMISSIONER 1 |
| Dan Christopher |  | Public Utility District #1 Commissioner Pos. 3 | PUBLIC UTILITY DISTRICT COMMISSIONER #3 |
| Dan G. Gunkel |  | Public Utility District #1 Commissioner Pos. 3 | PUBLIC UTILITY DISTRICT COMMISSIONER #3 |
| Darcy Nelly |  | PUBLIC UTILITY COMMISSIONER 1 | PUBLIC UTILITY DISTRICT #1 |
| Eddy Ury |  | Commissioner District 1 | PUD No. 1 Commissioner District 1 |
| Frank Imhof |  | Commissioner District 1 | PUD No. 1 Commissioner District 1 |
| Gene Healy |  | Commissioner #1 | PUD #1 |
| Janet St Clair |  | Commissioner District 1 | PUD COMMISSIONER DISTRICT 1 |
| Jeff Baine |  | Commissioner District 1 | PUD DIST COMM #1 |
| Jim Campbell |  | Commissioner, District No. 1 | PUD COMMISSIONER DISTRICT NO. 1 |
| Joe Louis |  | PUBLIC UTILITY COMMISSIONER 1 | PUBLIC UTILITY DISTRICT #1 |
| Logan B. Siebert |  | Public Utility District #1 Commissioner Pos. 3 | PUBLIC UTILITY DISTRICT COMMISSIONER #3 |
| Rick Catlin |  | Commissioner 1 | PUBLIC UTILITY DISTRICT 1, 1 |
| Scott Vejraska |  | Okanogan Commissioner Dist. #1 | OK PUBLIC UTILITY DISTRICT 01 |
| Sid Logan |  | Commissioner District 1 | PUD COMMISSIONER DISTRICT 1 |
| Spencer Roozen |  | Commissioner 1 | SKAGIT COUNTY PUD COMMISSIONER DIST 1 |
| Steve Grega |  | Commissioner District 1 | PUD DIST COMM #1 |
| Steven Gadd |  | Okanogan Commissioner Dist. #1 | OK PUBLIC UTILITY DISTRICT 01 |
| Troy Kirby |  | Commissioner, District No. 1 | PUD COMMISSIONER DISTRICT NO. 1 |
| Andrea Morgan |  | Commissioner #2 | PUD1-COMMISSIONER DISTRICT 2 |
| Ernie Hood |  | PUBLIC UTILITY COMMISSIONER #2 | Public Comm District - 02 |
| Gerry David Bradbury |  | PUBLIC UTILITY COMMISSIONER #2 | Public Comm District - 02 |
| Howie Kubik |  | Commissioner #2 | PUD1-COMMISSIONER DISTRICT 2 |
| John W “Jack” Smith |  | Commissioner District No. 2 | PUD 1 COMMISSIONER DIST 2 |
| Keith Kisler |  | Commissioner, District 2 | Public Utility District - Commissioner No. 2 |
| Micah Valentine |  | Commissioner Pos. 2 | PUD Commissioner Dist 2 |
| Michael Brittain |  | Commissioner, District 2 | Public Utility District - Commissioner No. 2 |
| Mick Sprouffske |  | Commissioner District 2 | Public Utility Dist 3-2 |
| Missi Baker |  | Commissioner District No. 2 | PUD 1 COMMISSIONER DIST 2 |
| Molly Doneen Simpson |  | Commissioner No. 2 | PUBLIC UTILITY DIST 2 |
| Nick Warner |  | Commissioner No. 2 | PUBLIC UTILITY DIST 2 |
| Pat Tucker |  | Commissioner Pos. 2 | PUD Commissioner Dist 2 |
| Randy Brackett |  | Commissioner District No. 2 | PUD 1 COMMISSIONER DIST 2 |
| Randy Neatherlin |  | Commissioner District 2 | Public Utility Dist 3-2 |
| Rick Paschall |  | Commissioner District No. 2 | PUD 1 COMMISSIONER DIST 2 |
| Ronald S. Gold |  | Commissioner District 2 | Public Utility Dist 1-2 |
| Roy C. "Dewey"  Holliday |  | Commissioner Pos. 2 | PUD Commissioner Dist 2 |
| Stacey Smith |  | Commissioner District 2 | PUD Commissioner District 2 |
| Tim Nies |  | Commissioner District 2 | PUD District 2 |
| Timothy Dalton |  | Commissioner District No. 2 | PUD 1 COMMISSIONER DIST 2 |
| Tracy Rutt |  | PUBLIC UTILITY COMMISSIONER #2 | Public Comm District - 02 |
| ANDREW POOLER |  | PUBLIC UTILITY COMMISSIONER #3 | PUD #3 |
| Addison Dillon |  | Commissioner #3 | PUD COMMISSIONER DIST. 3 |
| Christopher Pettit |  | Commissioner, District No. 3 | PUD COMMISSIONER DISTRICT NO. 3 |
| Doug Aubertin |  | PUBLIC UTILITY COMMISSIONER #3 | PUD #3 |
| Gordon Matthews |  | COMMISSIONER, DISTRICT NO. 3 | CLARK PUBLIC UTILITIES - COMM. DIST. #3 |
| Hans-Joachim Engelke |  | Commissioner, District 3 | PASCO PORT DISTRICT 3 |
| Jane A. Van Dyke |  | COMMISSIONER, DISTRICT NO. 3 | CLARK PUBLIC UTILITIES - COMM. DIST. #3 |
| Jeff Curry |  | Commissioner, District No. 3 | PUD COMMISSIONER DISTRICT NO. 3 |
| Kevin Roegner |  | COMMISSIONER, DISTRICT NO. 3 | CLARK PUBLIC UTILITIES - COMM. DIST. #3 |
| Larry Schaapman |  | Commissioner Dist #3 | GRANT COUNTY PUD COMM DIST #3 |
| Liz Green |  | Commissioner #3 | PUD COMMISSIONER DIST. 3 |
| Dean Berkeley |  | Commissioner District 4 | Port of Bellingham Commissioner District 4 |
| Jaden McConnell |  | Commissioner District 4 | Port of Bellingham Commissioner District 4 |
| Paul Burrill |  | Commissioner District 4 | Port of Bellingham Commissioner District 4 |
| Samantha Cruz-Mendoza |  | Commissioner District 4 | Port of Bellingham Commissioner District 4 |
| Tim Chartier |  | Commissioner District 4 | Port of Bellingham Commissioner District 4 |
| Tor Benson |  | Commissioner District 4 | Port of Bellingham Commissioner District 4 |
| Chris Elder |  | Commissioner District 5 | Port of Bellingham Commissioner District 5 |
| Jerry Burns |  | Commissioner District 5 | Port of Bellingham Commissioner District 5 |
| Randall Wood |  | Commissioner District 5 | Port of Bellingham Commissioner District 5 |
| Shawn Ensley |  | Commissioner District 5 | Port of Bellingham Commissioner District 5 |
| Spenser R. New |  | Commissioner District 5 | Port of Bellingham Commissioner District 5 |
| Todd Lagestee |  | Commissioner District 5 | Port of Bellingham Commissioner District 5 |
| Kelly Allen |  | PUBLIC UTILITY DIST COMMISSIONER DIST B | PUBLIC UTILITY DISTRICT COMMISSIONER B |
| Nelson Cox |  | Commissioner Dist #B AL | GRANT COUNTY PUD DIST #B |

### District Court Judge (33)

| Candidate | Party | Race (raw) | District |
|-----------|-------|------------|----------|
| Abigail E. Bartlett |  | DISTRICT COURT JUDGE, DEPARTMENT NO. 6 | DISTRICT COURT JUDGES |
| Alex Schodowski |  | Judge - District Court 1 | COURT DISTRICT 1 |
| BRUCE HANIFY |  | Judge - District Court 2 | COURT DISTRICT 2 |
| Chad E. Sleight |  | DISTRICT COURT JUDGE, DEPARTMENT NO. 2 | DISTRICT COURT JUDGES |
| Claire A. Bradley |  | District Court Judge Department 1 | District Court |
| Claire Sussman |  | District Court No. 2 | DISTRICT COURT |
| Craig Juris |  | District Court Judge | UPPER COUNTY DISTRICT COURT |
| Dwayne Christopher |  | District Court No. 5 | DISTRICT COURT |
| Eric J. Lawless |  | District Court No. 7 | DISTRICT COURT |
| Gina M Buskirk |  | District Court Judge Department 2 | District Court |
| James Armstrong |  | District Court No. 8 | DISTRICT COURT |
| James B. Smith |  | DISTRICT COURT JUDGE, DEPARTMENT NO. 3 | DISTRICT COURT JUDGES |
| Jeff Baker |  | Klickitat County West District Court Judge | WEST DISTRICT COURT |
| Karl Williams |  | District Court No. 6 | DISTRICT COURT |
| Kevin A. McCann |  | District Court No. 1 | DISTRICT COURT |
| Kevin P Kelly |  | District Court Judge Department 4 | District Court |
| Kimberly (Kim) Boggs |  | Columbia County District Court Judge | COURT DISTRICT |
| Kristen L. Parcher |  | DISTRICT COURT JUDGE, DEPARTMENT NO. 1 | DISTRICT COURT JUDGES |
| Leslie A. Lopez |  | DISTRICT COURT JUDGE, DEPARTMENT NO. 4 | DISTRICT COURT JUDGES |
| Lizanne Padula |  | District Court No. 3 | DISTRICT COURT |
| Megan D. Peyton |  | DISTRICT COURT JUDGE, DEPARTMENT NO. 5 | DISTRICT COURT JUDGES |
| Mike Sommerfeld |  | District Court No. 7 | DISTRICT COURT |
| Nancy R. McAllister |  | DISTRICT COURT JUDGE | Court - South District |
| Neil Horibe |  | District Court No. 4 | DISTRICT COURT |
| Pam Nogueira |  | District Court No. 7 | DISTRICT COURT |
| Patrick David Murphy |  | Judge - District Court 1 | COURT DISTRICT 1 |
| Paul Sander |  | District Court Judge | LOWER COUNTY DISTRICT COURT |
| Rick L Hansen |  | Klickitat County East District Court Judge | EAST DISTRICT COURT |
| Scott Harmer |  | DISTRICT COURT JUDGE | Court - North District |
| Shane R. Seaman |  | District Court Judge Department 3 | District Court |
| Sven Nelson |  | District Court No. 8 | DISTRICT COURT |
| Wade S. Samuelson |  | District Court Judge, Dept 1 | DISTRICT COURT |
| RW Buzzard |  | District Court Judge, Dept 2 | DISTRICT COURT |

### Municipal (47)

| Candidate | Party | Race (raw) | District |
|-----------|-------|------------|----------|
| Dee Sonntag |  | Tacoma Municipal Court Pos. 1 | CITY OF TACOMA |
| Sergio C. Flores |  | Tacoma Municipal Court Pos. 2 | CITY OF TACOMA |
| Steven J. Krupa |  | Tacoma Municipal Court Pos. 3 | CITY OF TACOMA |
| Jerome O'Leary | REPUBLICAN | Council - District No. 1 | COUNTY COUNCIL DISTRICT NO. 1 |
| Kelsey Barrans | DEMOCRATIC | Council - District No. 1 | COUNTY COUNCIL DISTRICT NO. 1 |
| Kenneth King | DEMOCRATIC | Council - District No. 1 | COUNTY COUNCIL DISTRICT NO. 1 |
| Terrance Mayers | DEMOCRATIC | Council - District No. 1 | COUNTY COUNCIL DISTRICT NO. 1 |
| Bettina Gese | REPUBLICAN | Council - District No. 5 | COUNTY COUNCIL DISTRICT NO. 5 |
| Bryan Yambe | DEMOCRATIC | Council - District No. 5 | COUNTY COUNCIL DISTRICT NO. 5 |
| Ann E. Jolie | REPUBLICAN | Council - District No. 7 | COUNTY COUNCIL DISTRICT NO. 7 |
| Brenda Lykins | DEMOCRATIC | Council - District No. 7 | COUNTY COUNCIL DISTRICT NO. 7 |
| Chuck West | NONPARTISAN | Council - District No. 7 | COUNTY COUNCIL DISTRICT NO. 7 |
| Bryan Shull |  | COUNCILOR, DISTRICT NO. 1 | COUNTY COUNCILOR DISTRICT NO. 1 |
| Dusti Arab |  | COUNCILOR, DISTRICT NO. 1 | COUNTY COUNCILOR DISTRICT NO. 1 |
| Glen Yung |  | COUNCILOR, DISTRICT NO. 1 | COUNTY COUNCILOR DISTRICT NO. 1 |
| Lukas Bardue |  | COUNCILOR, DISTRICT NO. 1 | COUNTY COUNCILOR DISTRICT NO. 1 |
| John Zingale |  | COUNCILOR, DISTRICT NO. 2 | COUNTY COUNCILOR DISTRICT NO. 2 |
| Martin Pittioni |  | COUNCILOR, DISTRICT NO. 2 | COUNTY COUNCILOR DISTRICT NO. 2 |
| Michelle Belkot |  | COUNCILOR, DISTRICT NO. 2 | COUNTY COUNCILOR DISTRICT NO. 2 |
| Peter Silliman | States No Party Preference | COUNCILOR, DISTRICT NO. 5 | COUNTY COUNCILOR DISTRICT NO. 5 |
| Troy McCoy | States No Party Preference | COUNCILOR, DISTRICT NO. 5 | COUNTY COUNCILOR DISTRICT NO. 5 |
| David Tveraas |  | Council Pos. 4 | City Of Richland |
| Kyle Saltz |  | Council Pos. 4 | City Of Richland |
| Mary S. Lipton |  | Council Pos. 4 | City Of Richland |
| Ragan Faylor |  | Council Pos. 4 | City Of Richland |
| Todd Samuel |  | Council Pos. 4 | City Of Richland |
| Anita Crawford-Willis |  | Municipal Court Judge Position No. 4 | City of Seattle |
| Cat McDowall |  | Municipal Court Judge Position No. 1 | City of Seattle |
| Damon Shadid |  | Municipal Court Judge Position No. 7 | City of Seattle |
| Gabe Rothstein |  | Municipal Court Judge Position No. 5 | City of Seattle |
| Garmon Newsom |  | Municipal Court Judge Position No. 5 | City of Seattle |
| Katharine Edwards |  | Municipal Court Judge Position No. 2 | City of Seattle |
| Lindsay Calkins |  | Municipal Court Judge Position No. 5 | City of Seattle |
| Pooja Vaddadi |  | Municipal Court Judge Position No. 3 | City of Seattle |
| Shantrice Anderson |  | Municipal Court Judge Position No. 6 | City of Seattle |
| Miriam Mboya |  | Metropolitan King County Council District No. 2 | County Council District No. 2 |
| Rebecca Saldaña |  | Metropolitan King County Council District No. 2 | County Council District No. 2 |
| Toshiko Grace Hasegawa |  | Metropolitan King County Council District No. 2 | County Council District No. 2 |
| Jorge L. Barón |  | Metropolitan King County Council District No. 4 | County Council District No. 4 |
| Claudia Balducci |  | Metropolitan King County Council District No. 6 | County Council District No. 6 |
| Mia Jacobson |  | Metropolitan King County Council District No. 8 | County Council District No. 8 |
| Nick Duda |  | Metropolitan King County Council District No. 8 | County Council District No. 8 |
| Teresa Mosqueda |  | Metropolitan King County Council District No. 8 | County Council District No. 8 |
| Dimitri Georgakopoulos |  | Council District No. 5 | SEATTLE CITY COUNCIL DISTRICT 5 |
| Julie Kang |  | Council District No. 5 | SEATTLE CITY COUNCIL DISTRICT 5 |
| Nilu Jenks |  | Council District No. 5 | SEATTLE CITY COUNCIL DISTRICT 5 |
| Silas James |  | Council District No. 5 | SEATTLE CITY COUNCIL DISTRICT 5 |

### Other (89)

| Candidate | Party | Race (raw) | District |
|-----------|-------|------------|----------|
| Bianca Tse |  | Judge Position No. 1 | NORTHEAST ELECTORAL DISTRICT |
| Jan Trasen |  | Judge Position No. 1 | NORTHEAST ELECTORAL DISTRICT |
| Josh Schaer |  | Judge Position No. 1 | NORTHEAST ELECTORAL DISTRICT |
| Raul Martinez |  | Judge Position No. 1 | SHORELINE ELECTORAL DISTRICT |
| Leah Taguba |  | Judge Position No. 1 | SOUTHEAST ELECTORAL DISTRICT |
| Brian Todd |  | Judge Position No. 1 | SOUTHWEST ELECTORAL DISTRICT |
| Bardi Martin |  | Judge Position No. 1 | WEST ELECTORAL DISTRICT |
| Nyjat Rose-Akins |  | Judge Position No. 1 | WEST ELECTORAL DISTRICT |
| Michelle Gehlsen |  | Judge Position No. 2 | NORTHEAST ELECTORAL DISTRICT |
| Karama H. Hawkins |  | Judge Position No. 2 | SHORELINE ELECTORAL DISTRICT |
| Matthew York |  | Judge Position No. 2 | SOUTHEAST ELECTORAL DISTRICT |
| Andrea Samonica Jarmon |  | Judge Position No. 2 | SOUTHWEST ELECTORAL DISTRICT |
| Kuljinder K. Dhillon |  | Judge Position No. 2 | WEST ELECTORAL DISTRICT |
| Lisa O'Toole |  | Judge Position No. 3 | NORTHEAST ELECTORAL DISTRICT |
| Tricia Grove Johnson |  | Judge Position No. 3 | SOUTHEAST ELECTORAL DISTRICT |
| Laurel Gibson |  | Judge Position No. 3 | SOUTHWEST ELECTORAL DISTRICT |
| Mitch Greene |  | Judge Position No. 3 | SOUTHWEST ELECTORAL DISTRICT |
| Quita St. John |  | Judge Position No. 3 | SOUTHWEST ELECTORAL DISTRICT |
| Rebecca Robertson |  | Judge Position No. 3 | WEST ELECTORAL DISTRICT |
| Kevin Peck |  | Judge Position No. 4 | NORTHEAST ELECTORAL DISTRICT |
| Corinna Harn |  | Judge Position No. 4 | SOUTHEAST ELECTORAL DISTRICT |
| Fa'amomoi Masaniai, Jr. |  | Judge Position No. 4 | SOUTHWEST ELECTORAL DISTRICT |
| Harry Steinmetz |  | Judge Position No. 4 | SOUTHWEST ELECTORAL DISTRICT |
| Yvonne Chin |  | Judge Position No. 4 | WEST ELECTORAL DISTRICT |
| Jill Klinge |  | Judge Position No. 5 | NORTHEAST ELECTORAL DISTRICT |
| Heather M. Barker |  | Judge Position No. 5 | SOUTHEAST ELECTORAL DISTRICT |
| Joshua C. Harris |  | Judge Position No. 5 | SOUTHEAST ELECTORAL DISTRICT |
| Noel Merfeld |  | Judge Position No. 5 | SOUTHWEST ELECTORAL DISTRICT |
| Renee Walls |  | Judge Position No. 5 | SOUTHWEST ELECTORAL DISTRICT |
| Kristin Shotwell |  | Judge Position No. 5 | WEST ELECTORAL DISTRICT |
| Denice Gagner |  | Judge Position No. 6 | NORTHEAST ELECTORAL DISTRICT |
| Rhonda Laumann |  | Judge Position No. 6 | SOUTHEAST ELECTORAL DISTRICT |
| Peter Peaquin |  | Judge Position No. 7 | NORTHEAST ELECTORAL DISTRICT |
| Byron Moore |  | Judge Pos. 1 | DISTRICT COURT JUDGE |
| Robert W. Grim |  | Judge Pos. 1 | DISTRICT COURT JUDGE |
| Charles Short |  | Judge Pos. 2 | DISTRICT COURT JUDGE |
| John Andrew Bangerter |  | Judge Pos. 2 | DISTRICT COURT JUDGE |
| Jennifer Richardson |  | Judge Position #03 | Grant Superior Court |
| Kenneth "Ken" Chadwick |  | Judge Position #03 | Grant Superior Court |
| Trevor Bevier |  | Judge Position #03 | Grant Superior Court |
| Doris Walkins |  | Judge Position 17 | Pierce Superior Court |
| Jennifer Rancourt |  | Judge Position 1 | CASCADE DISTRICT COURT |
| Erik D. Price |  | Judge Position 1 | Court of Appeals, Division 2, District 2 |
| Tyson R. Hill |  | Judge Position 1 | Court of Appeals, Division 3, District 2 |
| Megan K. Murphy |  | Judge Position 1 | Court of Appeals, Division 3, District 3 |
| Kevin G. Blondin |  | Judge Position 1 | District Court |
| Anthony E. Howard |  | Judge Position 1 | EVERETT DISTRICT COURT |
| Rick Leo |  | Judge Position 1 | EVERGREEN DISTRICT COURT |
| Elizabeth Fraser |  | Judge Position 1 | SOUTH DISTRICT COURT |
| Kent Y. Liu |  | Judge Position 20 | KING COUNTY SUPERIOR COURT |
| Rachelle Francis |  | Judge Position 2 | CASCADE DISTRICT COURT |
| Linda Coburn |  | Judge Position 2 | COURT OF APPEALS, DIVISION 1, DISTRICT 2 |
| Meng Li Che |  | Judge Position 2 | Court of Appeals, Division 2, District 1 |
| Tracy Arlene Staab |  | Judge Position 2 | Court of Appeals, Division 3, District 1 |
| M. Jamie Imboden |  | Judge Position 2 | District Court |
| Jennifer Millett |  | Judge Position 2 | EVERETT DISTRICT COURT |
| Patricia Lyon |  | Judge Position 2 | EVERGREEN DISTRICT COURT |
| Thomas Franklin Webster |  | Judge Position 2 | Ferry, Pend Oreille, Stevens Superior Court |
| Rachel Hong |  | Judge Position 2 | Okanogan Superior Court |
| Jeffrey D. Goodwin |  | Judge Position 2 | SOUTH DISTRICT COURT |
| Daniel York |  | Judge Position 32 | KING COUNTY SUPERIOR COURT |
| Christopher Eastwood |  | Judge Position 3 | District Court |
| Nicole G. Knowles |  | Judge Position 3 | District Court |
| Matthew Baldock |  | Judge Position 3 | SOUTH DISTRICT COURT |
| Candie M. Dibble |  | Judge Position 3 | Spokane Superior Court |
| Tenaya Scheinman |  | Judge Position 45 | KING COUNTY SUPERIOR COURT |
| Jacob Lervold |  | Judge Position 4 | Cowlitz Superior Court |
| Jill Karmy |  | Judge Position 4 | Cowlitz Superior Court |
| Mary Crandall |  | Judge Position 4 | Skagit Superior Court |
| David S. Mann |  | Judge Position 5 | COURT OF APPEALS, DIVISION 1, DISTRICT 1 |
| Bill A. Bowman |  | Judge Position 6 | COURT OF APPEALS, DIVISION 1, DISTRICT 1 |
| Mindy Walker |  | Judge Position No. 1 | District Court |
| Anne Melani Bremner |  | Justice Position #01 | SUPREME COURT |
| Colleen Melody |  | Justice Position #01 | SUPREME COURT |
| Laura Christensen Colberg |  | Justice Position #01 | SUPREME COURT |
| Scott Edwards |  | Justice Position #01 | SUPREME COURT |
| David Stevens |  | Justice Position #03 | SUPREME COURT |
| Jaime Michelle Hawk |  | Justice Position #03 | SUPREME COURT |
| Mike Diaz |  | Justice Position #03 | SUPREME COURT |
| Ian Birk |  | Justice Position #04 | SUPREME COURT |
| Sean O'Donnell |  | Justice Position #04 | SUPREME COURT |
| Dave Larson |  | Justice Position #05 | SUPREME COURT |
| Greg Miller |  | Justice Position #05 | SUPREME COURT |
| Sharonda Amamilo |  | Justice Position #05 | SUPREME COURT |
| Theo Angelis |  | Justice Position #05 | SUPREME COURT |
| David R Shelvey |  | Justice Position #07 | SUPREME COURT |
| Debra L. Stephens |  | Justice Position #07 | SUPREME COURT |
| Karim A. Merchant |  | Justice Position #07 | SUPREME COURT |
| Todd A. Bloom |  | Justice Position #07 | SUPREME COURT |

### PUD (1)

| Candidate | Party | Race (raw) | District |
|-----------|-------|------------|----------|
| Jon Martin |  | PUD Comm (3) | PUD Comm. Dist. 3 |

## Finding: SOS Races Not in races.json (Federal/Legislative)
**Priority:** Medium — filed races without race directory
**Count:** 4

| Race Type | District | Candidates |
|-----------|----------|------------|
| Commissioner | 01 | 1: Pamela "Pam" Hickey |
| Commissioner | ? | 2: Kelly Allen, Nelson Cox |
| Director | Director of Community Development | 1: Bruce Emery |
| Director | Director of Elections | 1: Julie Wise |

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
- PUD, Port, Municipal, and Superior/Appellate court races not yet tracked in gap analysis

## Missing Candidates — Categorized Breakdown

Of the 243 SOS-filed candidates not yet in races.json, all are from race types not yet tracked.
None are from race types we currently cover that were missed.

| Category | Count | Status |
|----------|-------|--------|
| PUD Commissioner | 61 | Not yet tracked |
| District Court Judge (county-level) | 51 | Not yet tracked |
| King County District Court (electoral) | 33 | Not yet tracked |
| County Council | 26 | Not yet tracked |
| WA Supreme Court | 17 | Not yet tracked |
| Superior Court | 13 | Not yet tracked |
| Port Commissioner | 13 | Not yet tracked |
| Municipal Court Judge | 12 | Not yet tracked |
| City Council | 9 | Not yet tracked |
| Court of Appeals | 8 | Not yet tracked |
| **Total** | **243** | |

## Remediation Actions Completed

| # | Action | Status |
|---|--------|--------|
| R1 | Deleted 11 orphan directories (suffix/hyphen parsing artifacts) | Done |
| R2 | Updated 11 party mismatches in races.json to match SOS filings | Done |
| R3 | Added M. Brett Buckley to Thurston District Court Pos. 3 | Done |
| R4 | Fixed `candidate_slug()` in update_races.py for suffixes/hyphens (Bug #1750) | Done |
| R5 | Fixed Clerk of Superior Court normalization in validator (Bug #1755) | Done |
| R6 | Updated 38 dossier disclaimers to acknowledge T3 sources (Story #1756) | Done |
| R7 | Categorized 243 missing candidates by race type (Story #1751) | Done |

## ADO Work Items Filed (civic-tech)

| # | Type | Title |
|---|------|-------|
| 1750 | Bug | Fix candidate name parser for hyphenated names and suffixes |
| 1751 | User Story | Add 245 missing SOS-filed candidates to races.json |
| 1752 | User Story | Review 4 candidates in races.json not confirmed by SOS filings |
| 1753 | User Story | Review district court judge matching gaps (~33 candidates) |
| 1754 | User Story | Evaluate adding WA Supreme Court and Appeals Court races |
| 1755 | Bug | Fix validate_candidates.py Clerk of Superior Court normalization |
| 1756 | User Story | Update dossier disclaimer for T3 sources |
