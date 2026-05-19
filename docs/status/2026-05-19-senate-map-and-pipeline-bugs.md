# Session Status: Senate Map + Pipeline Bug Fixes

**Date:** 2026-05-19
**Repos:** ctm-landing (GitHub), clearthemud (ADO civic-tech)

## What Was Done

### ADO #1713 — US Map: Denote States with 2026 Senate Races (ctm-landing)

Added a third visual state to the interactive US map showing all 33 Class II Senate race states in teal, alongside existing gold (published dossiers) and dark blue (not yet covered).

**Changes:**
- `css/dossier.css` — Added `state--senate` class (teal #5a9a7a), hover/focus states, glow animation, legend swatch
- `js/us-map.js` — Three-state logic: active (dossiers) > senate > inactive. Senate states are clickable and show "2026 U.S. Senate race" tooltip
- `tools/generate_states.py` — Added `SENATE_2026_STATES` constant (33 states), injects `senate` boolean into `CTM_STATE_DATA`, three-item legend
- `states/index.html` — Regenerated with senate flags
- 18 TDD tests in `test_senate_map.py`

**Note:** `senate_class_up` field in `states.json` is wrong for 15 states (shows Class I instead of Class II). The hardcoded `SENATE_2026_STATES` constant in `generate_states.py` is the authoritative source.

### ADO #1731 — wa_sos_csv adapter path resolution (clearthemud) — Already Fixed

Relative path resolution was fixed in a prior session (commit 167cd7e). Closed as already done.

### ADO #1732 — lda_adapter async context manager (clearthemud) — Already Fixed

LDAClient correctly does NOT use async context manager pattern. Adapter setup/teardown is implemented correctly. Closed as already done.

### ADO #1733 — Pipeline collect: profiles not persisted to disk (clearthemud)

The `collect` command returned profiles in memory but never wrote them to disk, so `generate` couldn't find them.

**Fix:** Added `persist_profiles_to_disk()` function that writes each profile to `output_dir/{candidate_id}/data.json`. Called automatically after collect completes. Round-trip test confirms generate can read persisted profiles.

**Changes:**
- `src/pipeline/cli.py` — Added `persist_profiles_to_disk()` and `_resolve_output_dir()`, wired into collect command
- 8 TDD tests including persist→load round-trip verification

### ADO #1683 — FEC conduit vs donor disambiguation (clearthemud)

ActBlue and WinRed appeared as "top donors" when they're payment processing conduits, not actual donors.

**Fix:** Added `_is_conduit()` function with case-insensitive name normalization against a `KNOWN_CONDUITS` set. Applied in both `adapt_top_donors()` (fec_adapter) and `top_donors()` (analysis module).

**Changes:**
- `src/fec_adapter.py` — Added `KNOWN_CONDUITS`, `_is_conduit()`, filter in `adapt_top_donors()`
- `src/pipeline/analysis.py` — Import and apply `_is_conduit()` filter in `top_donors()`
- 9 TDD tests covering filtering, case-insensitivity, real-donor preservation

## Test Results

| Repo | Tests | New | Regressions |
|------|-------|-----|-------------|
| ctm-landing | 637 passed | 18 (senate map) | 0 |
| clearthemud | 1761 passed | 17 (8 persist + 9 conduit) | 0 |

## ADO Work Items Closed

| # | Type | Title |
|---|------|-------|
| 1713 | User Story | US map: denote states with 2026 Senate races |
| 1731 | Bug | wa_sos_csv adapter: CSV file not found (already fixed) |
| 1732 | Bug | lda_adapter: LDAClient async context manager (already fixed) |
| 1733 | Bug | pipeline collect: profiles not persisted to disk |
| 1683 | Bug | FEC conduit vs donor disambiguation |
