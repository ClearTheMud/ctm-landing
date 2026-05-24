# County Race Hub Buildout Process

Step-by-step process for building a new county's race hub on clearthemud.org after candidate dossiers are complete.

## Prerequisites

Before starting a county buildout, ensure:

1. **Candidate dossiers exist** in `~/Local/Projects/github/clearthemud/output/dossiers/{state}/{year}/county/{county-office}/`
   - Each candidate needs a `.json` dossier file
   - Only T0-T2 verified findings may be published
2. **County races are in `races.json`** with candidates populated
   - Run `python3 tools/ingest_sos_candidates.py` if races haven't been ingested yet
   - Run `python3 tools/detect_roles.py` to tag incumbents/challengers
3. **County map SVG exists** in `geo/states/`
   - Run `python3 tools/generate_county_maps.py {STATE} --places` if missing

## Quick Start

```bash
# Preview what will be built
python3 tools/build_county_hub.py WA grays-harbor --dry-run

# Build everything
python3 tools/build_county_hub.py WA grays-harbor

# Copy the landing page snippet from the output into index.html
# Then deploy
git add -A && git commit -m "feat: add {County} County race hub" && git push
```

## Full Pipeline (Manual Steps)

### Step 1: Validate Data

```bash
python3 tools/build_county_hub.py WA {county-slug} --dry-run
```

Check for:
- All races found in races.json
- Dossier JSONs located for each candidate
- County/places SVG maps exist
- No blocking errors

### Step 2: Generate Race & Candidate Pages

The pipeline runs `generate_candidate_pages.py` which creates:
- `races/wa-{county}-{office}-2026/index.html` — race overview with candidate field
- `races/wa-{county}-{office}-2026/{lastname}/index.html` — individual candidate dossier

Each page includes:
- Breadcrumb navigation (home → state → county → race → candidate)
- Party-specific header styling
- TLP:GREEN classification bars
- Sourced findings with tier badges

### Step 3: Regenerate State Hub

The pipeline runs `generate_states.py` which updates:
- `states/washington/index.html` — WA state hub with county map
- `states/washington/{county}/index.html` — county hub page with race table and places map
- `sitemap.xml` — search engine sitemap

### Step 4: Update Landing Page

The pipeline outputs an HTML snippet for the "Recently Added Profiles" section of `index.html`. Paste it inside the `<div class="recently-added">` container, before the closing `</div>`.

Format:
- **Contested races** (2+ candidates) → race cards with candidate pills
- **Unopposed races** (1 candidate) → compact list items
- County name as `<h3 class="subsection">` header

### Step 5: Deploy

```bash
git push origin main
```

GitHub Pages deploys automatically from the main branch.

## Pipeline Script Reference

```bash
# Build a single county
python3 tools/build_county_hub.py WA grays-harbor

# Dry run (preview only, no files written)
python3 tools/build_county_hub.py WA grays-harbor --dry-run

# Skip state hub regeneration (faster, if you're doing multiple counties)
python3 tools/build_county_hub.py WA grays-harbor --skip-state-regen

# List all counties and their build status
python3 tools/build_county_hub.py WA --list-counties
```

## Data Flow

```
WA SOS CandidateList.csv
  → ingest_sos_candidates.py → races.json (race + candidate entries)
  → detect_roles.py → races.json (incumbent/challenger tags)
  → build_county_races.py → county_races.json (parallel data)

clearthemud OSINT pipeline
  → YAML profiles + findings → JSON dossiers → HTML dossiers

build_county_hub.py (this pipeline)
  → generate_candidate_pages.py → races/{race-id}/*.html
  → generate_states.py → states/{state}/{county}/index.html
  → landing page snippet → manual paste into index.html
```

## Quality Checklist

Before committing a new county:

- [ ] All contested races have race overview pages
- [ ] All candidates have individual dossier pages
- [ ] Party header classes match actual party (`party-dem`, `party-rep`, `party-neutral`)
- [ ] Breadcrumb navigation links are correct
- [ ] Only T0-T2 findings are published (no T3/T4 or "RESEARCH NOTE" items)
- [ ] County hub page shows all races with correct links
- [ ] County appears on state map (clickable, with tooltip)
- [ ] Landing page "Recently Added" section includes the county
- [ ] Sitemap updated

## Troubleshooting

**"No races found in races.json"**
Run the ingestion pipeline first:
```bash
python3 tools/ingest_sos_candidates.py --dry-run
python3 tools/ingest_sos_candidates.py
```

**"Missing dossier JSONs for N candidates"**
The OSINT pipeline in the clearthemud repo hasn't generated dossiers for those candidates yet. Pages will still be generated but with minimal content (T1 stub data only).

**"No places SVG"**
Generate geographic data:
```bash
python3 tools/generate_county_maps.py WA --places
```

**Party class mismatch**
Check `races.json` party field matches the candidate's actual party. The page generator reads from races.json, so fix it there and re-run.
