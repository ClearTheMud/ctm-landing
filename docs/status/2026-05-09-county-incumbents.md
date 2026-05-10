# Session Status: County-Level Incumbent Tagging

**Date:** 2026-05-09
**Branch:** main
**Commits:** a1515d3, d127e68

## Work Completed

### County-Level Incumbent Tagging (US #1672 continuation)

Tagged 191 incumbents across 38 of 39 WA counties by cross-referencing current officeholders against filed 2026 candidates. Whatcom County is the only county with no incumbents (all 3 races are open seats where current holders didn't file).

**Data sources used:**
- Thurston County: Official elected officials PDF (updated 4/3/2025)
- King, Spokane, Pierce, Clark, Benton, Yakima, Kitsap, Snohomish: Ballotpedia county pages
- Remaining 30 counties: Ballotpedia + county official websites
- WA PDC open data (data.wa.gov dataset `ehbc-shxw`) identified as viable bulk source but not used for this batch

**Coverage by county:**

| County | Incumbents | County | Incumbents | County | Incumbents |
|--------|-----------|--------|-----------|--------|-----------|
| Adams | 6 | Grant | 4 | Pacific | 5 |
| Asotin | 3 | Grays Harbor | 7 | Pend Oreille | 6 |
| Benton | 3 | Island | 7 | San Juan | 6 |
| Chelan | 7 | Jefferson | 4 | Skagit | 5 |
| Clallam | 4 | King | 2 | Skamania | 7 |
| Clark | 4 | Kitsap | 3 | Snohomish | 1 |
| Columbia | 3 | Kittitas | 4 | Spokane | 4 |
| Cowlitz | 6 | Klickitat | 6 | Stevens | 5 |
| Douglas | 5 | Lewis | 6 | Thurston | 7 |
| Ferry | 6 | Lincoln | 8 | Wahkiakum | 7 |
| Franklin | 5 | Mason | 6 | Walla Walla | 6 |
| Garfield | 6 | Okanogan | 6 | Whatcom | 0 |
| | | | | Whitman | 7 |
| | | | | Yakima | 3 |

### Georgia Senate 2026 Race Pages

Added GA Senate race with 4 candidate dossiers (Ossoff incumbent, Collins, Carter, Dooley challengers).

### ADO Work Item Filed

- **US #1713** — "US map: denote states with 2026 Senate races" — New, unstarted. 35 states with Senate races (33 Class II + 2 specials: OH, FL) need visual indicator on the US map.

## Current Site Statistics

- **Total races:** 456 (133 federal/legislative + 322 county + 1 GA Senate)
- **Total candidates:** 497 county + federal/legislative
- **Total generated pages:** 1,325
- **Counties with races:** 39/39
- **Incumbents tagged:** 191 county + 102 legislative = 293 total

## Files Modified

- `tools/data/races.json` — 191 challenger→incumbent role changes
- `races/**/*.html` — ~390 regenerated pages with updated incumbent status
- `states/**/*.html` — 39 county pages + 50 state pages regenerated
- `sitemap.xml` — regenerated

## Known Issues

- Klickitat County race IDs have doubled prefix (`wa-klickitat-klickitat-county-*`) from CSV office name normalization — cosmetic only, pages render correctly
- Some county race BLUF text reads awkwardly: "incumbent in the Ferry County County Sheriff" (doubled "County") — minor, from office names in CandidateList.csv
- Whatcom County has zero incumbents tagged — verified correct (all open seats)

## Next Steps

- **US #1713**: Implement Senate race state indicator on US map
- Consider using WA PDC open data API (`ehbc-shxw`) for automated incumbent verification in future pipeline runs
- Fix doubled "County County" in BLUF text for affected races
