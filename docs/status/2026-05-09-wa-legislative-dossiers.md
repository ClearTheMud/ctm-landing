# WA Legislative Dossier Ingestion — 2026-05-09

## Summary

Ingested 294 WA state legislative dossiers (122 races) from clearthemud data pipeline into ctm-landing. All pages generated, tested, and integrated into the state page.

## Deliverables

### Data (US #1686)
- Added 122 legislative races to `tools/data/races.json` (133 total races now)
- 24 State Senate races, 49 House Pos. 1, 49 House Pos. 2
- 294 candidates with party, role, URL fields
- URL scheme: `/races/wa-state-senate-{n}-2026/`, `/races/wa-state-house-{n}-pos{p}-2026/`

### Generator Updates (US #1687)
- `find_dossier_json()` resolves legislative paths: `legislative/ld-{nn}/`
- `render_candidate_page()` renders `state_campaign_finance` (WA PDC data)
- Shows total raised, total spent, cash carried forward, PDC source
- State races show "WA Public Disclosure Commission" not "FEC"
- Added party mappings: Libertarian, Pro Gun Liberal, No Kings, Standup-America
- Race overview shows correct office label (not hardcoded "US House")
- District displays as "LD-{n}" for legislative races

### Generated Pages (US #1689)
- 122 race overview pages at `races/wa-state-*/index.html`
- 294 candidate dossier pages at `races/wa-state-*/{lastname}/index.html`
- 416 total new pages
- sitemap.xml updated with all URLs

### State Page Integration (US #1690)
- WA state page shows "State Legislature" section with 49 districts
- Each district links to Senate (if applicable), House Pos. 1, House Pos. 2
- Shows candidate counts per race
- Replaced "No active research" placeholder

### Tests (US #1688)
- 61 tests in `tools/tests/test_legislative_pages.py` — all passing
- 10 test classes covering: races.json schema, dossier path resolution, state campaign finance rendering, candidate pages, race overviews, URL scheme, state page integration, party mappings, file structure, sitemap
- Updated 2 existing tests in `test_state_maps.py` to distinguish US House from State House
- 156 total tests passing across all test files

## ADO Work Items
- Epic #1685: WA Legislative Race Dossier Ingestion (Closed)
- US #1686-1690: All closed

## Test Evidence
```
python3 -m pytest tools/tests/ -v --tb=short
# 156 passed
```
