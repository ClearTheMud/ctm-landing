# WA Congressional District Map Build — Session Status

**Date:** 2026-05-09
**Branch:** main
**Status:** IN PROGRESS

## What We're Building

Interactive SVG map of Washington's 10 federal congressional districts for the WA state hub page on clearthemud.org, plus races.json entries and candidate page scaffolding for 71 candidates across 10 races.

## Completed

1. Census TIGER shapefile downloaded (118th Congress boundaries, `/tmp/cd118/`)
2. Raw shapefile parser — reads .shp/.dbf without geopandas
3. `geo/states/wa-districts.svg` generated (42KB) with all 10 districts
   - IDs: WA-01 through WA-10
   - Data attrs: data-district, data-name, data-slug (zero-padded: `wa-house-01-2026`)
   - ARIA: aria-label on root, `<title>` on each district path
4. `tools/tests/test_state_maps.py` written (TDD — tests before implementation)
5. `tools/tests/__init__.py` created

## Test Results (12 pass, 9 fail)

### Passing (SVG structure)
- SVG has 10 districts, correct IDs (WA-01..WA-10), data attributes, titles, viewBox, aria-label, districts group, no inline styles, correct slug pattern

### Failing (not yet implemented)
- CSS: `.district`, `.district--active`, `.district--inactive`, `district-glow` rules
- races.json: 10 WA House entries with candidates
- JS: `js/state-map.js` (district interactivity)
- Generator: `load_state_svg` function, `CTM_DISTRICT_DATA`, `state-map.js` reference

## Next Steps

1. Add district CSS rules to `css/dossier.css`
2. Add 10 WA House races to `tools/data/races.json` (zero-padded IDs)
3. Write `js/state-map.js` mirroring `us-map.js` patterns
4. Add `load_state_svg()` and district data injection to `generate_states.py`
5. Regenerate state pages
6. Create candidate page skeletons from dossier JSON data

## Key Decisions

- Zero-padded district IDs: `wa-house-01-2026` (matches SVG, diverges from handoff doc's `wa-house-1-2026`)
- Federal districts only (county maps = future)
- No external deps — pure Python shapefile parser
- Handoff doc: `~/Local/Projects/github/clearthemud/docs/ctm-landing-wa-congressional-handoff.md`
- Dossier data: `~/Local/Projects/github/clearthemud/output/dossiers/wa/2026/congressional/cd-XX/`
