# Session Status: WA SOS Candidate Ingestion

**Date:** 2026-05-18
**Commit:** (main, pushed)
**Engagement:** C6S Data Quality (Engagement 7) + AppDev Tech Debt (Engagement 6)

## What Was Done

### ADO #1751 — Ingest 243 Missing SOS-Filed Candidates

Built `tools/ingest_sos_candidates.py` with 30-entry PUD mapping table, 10-category classifier, and race ID generator. Ingested all 243 previously untracked candidates into `tools/data/races.json` across 147 new races in 10 categories:

| Category | Races | Candidates |
|----------|-------|------------|
| PUD Commissioner | 31 | 61 |
| District Court Judicial | 43 | 51 |
| KC Electoral District Court | 25 | 33 |
| County Council | 10 | 26 |
| WA Supreme Court | 5 | 17 |
| Superior Court | 10 | 13 |
| Port Commissioner | 3 | 13 |
| Municipal Court | 10 | 12 |
| City Council | 2 | 9 |
| Court of Appeals | 8 | 8 |

### ADO #1752 — Review Candidates Not Confirmed by SOS

- **David Mistachkin**: Found in SOS — Withdrawn from District Court #1, Active for District Court #2. Removed from DC#1 race, orphan directory deleted.
- **M. Brett Buckley**: Not found in SOS CandidateList.csv. Flagged with note in races.json for manual verification.
- **Roman Buermann**: Confirmed TEA party in SOS. Updated from "unknown" to "tea" in races.json.

### ADO #1753 — District Court Judge Naming Gaps (33 Candidates)

All 33 judicial-type district court candidates ingested with proper jurisdiction identification:
- Pierce District Court (13 positions)
- King County District Court (6 department positions)
- Spokane District Court (3 positions)
- Thurston District Court (4 positions)
- Snohomish District Court (5 positions across main, north, south)
- Named courts: Cascade (2), Everett (2), Evergreen (2), Klickitat East/West (2), Upper/Lower County (2)
- Columbia County (1), Whatcom Districts 1/2 (3)

### ADO #1754 — WA Supreme Court + Court of Appeals

Added all statewide court races:
- **Supreme Court**: 5 justice positions (Pos. 1, 3, 4, 5, 7) with 17 candidates
- **Court of Appeals**: 8 positions across 3 divisions with 8 candidates (all uncontested)

### Validator Updated

Updated `validate_candidates.py` with:
- 10 new race categories in both `normalize_race_type()` (CSV) and `map_json_race_to_category()` (JSON)
- Extended matching engine Pass 2 to handle new categories by name + category
- Fixed `normalize_party_json()` to map lowercase "tea" to "other"
- Fixed Superior Court check to exclude Clerk of Superior Court

## Quality Scores — Before vs After

| Dimension | Before | After |
|-----------|--------|-------|
| Completeness | 78.0% | **100.0%** |
| Accuracy | 99.8% | 99.9% |
| Consistency | 99.9% | **100.0%** |
| Validity | 100.0% | 78.0% |
| Uniqueness | 100.0% | 100.0% |
| **Overall** | **95.5%** | **95.6%** |

Validity dropped because 243 new candidates don't have directories yet (draft entries — directories created when dossiers are researched).

## New Files

- `tools/ingest_sos_candidates.py` — SOS candidate ingestion script (891 lines)
- `tools/tests/test_ingest_candidates.py` — TDD tests for ingestion (1683 lines, 278 tests)

## Test Suite

563 tests passing (0 failures). 278 new ingestion tests + 285 existing.

## ADO Work Items Closed

| # | Type | Title |
|---|------|-------|
| 1749 | User Story | Homepage: Replace 'Current Research' with 'Recently Added Profiles' |
| 1750 | Bug | Fix candidate name parser for hyphenated names/suffixes |
| 1751 | User Story | Add 245 missing SOS-filed candidates to races.json |
| 1752 | User Story | Review candidates not confirmed by SOS filings |
| 1753 | User Story | Review district court judge matching gaps (~33) |
| 1754 | User Story | Evaluate adding WA Supreme Court and Appeals Court races |
| 1755 | Bug | Fix validate_candidates.py Clerk of Superior Court normalization |
| 1756 | User Story | Update dossier disclaimer for T3 sources |

## Final State

- **601 WA races** (up from 454)
- **1,105 WA candidates** (up from 863)
- **1,104/1,104 SOS candidates matched** (100% completeness)
- **1 JSON-only** (Buckley — not in SOS, flagged for investigation)
- **0 party mismatches, 0 orphan directories**

## Remaining

- 243 new candidates need directories/dossiers when research is prioritized
- Buckley filing status needs manual SOS verification
- 98 coverage gaps (new race types without race overview pages — draft entries)
