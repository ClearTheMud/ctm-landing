# ctm-landing — clearthemud.org Website

Static site for clearthemud.org, hosted on GitHub Pages with Cloudflare DNS. Publishes verified candidate dossiers organized by race.

## Hosting

- **GitHub Pages**: Deployed from `main` branch root (`/`)
- **Custom Domain**: clearthemud.org (CNAME file in repo root)
- **DNS**: Cloudflare — CNAME records for `@` and `www` → `ClearTheMud.github.io`
- **SSL**: Enforced via GitHub Pages (Let's Encrypt) — DNS-only mode on Cloudflare

## Structure

```
index.html                              -- Landing page
CNAME                                   -- GitHub Pages custom domain
sitemap.xml                             -- Generated XML sitemap
css/
  dossier.css                           -- Shared styles for all pages
states/
  index.html                            -- 50-state browse grid (generated)
  maine/index.html                      -- State hub with active races (generated)
  texas/index.html                      -- State hub placeholder (generated)
  ...                                   -- All 50 states
races/
  me-senate-2026/
    index.html                          -- Race overview (dynamics, matchup, field changes)
    collins/index.html                  -- Collins dossier (R, incumbent)
    platner/index.html                  -- Platner dossier (D, frontrunner)
    costello/index.html                 -- Costello brief (D, longshot)
geo/
  us-states.svg                         -- Clickable US map SVG (50 states + DC)
js/
  us-map.js                             -- Map interactivity (click, hover, keyboard, touch)
tools/
  generate_states.py                    -- Generates states/ pages from data files
  generate_candidate_pages.py           -- Generates race/candidate HTML from dossier JSON
  build_county_hub.py                   -- End-to-end county buildout pipeline
  update_races.py                       -- CLI to add races/candidates and regenerate
  COUNTY_BUILDOUT.md                    -- County buildout process documentation
  data/states.json                      -- 50-state reference data (static)
  data/races.json                       -- Active research tracker (edit per new race)
```

## URL Scheme

- `/states/` — Browse by state (all 50)
- `/states/{state-name}/` — State hub (federal/state/local race sections)
- `/races/{state}-{office}-{year}/` — Race overview
- `/races/{state}-{office}-{year}/{lastname}/` — Candidate dossier
- Folder-based routing: each page is `index.html` inside its folder for clean URLs

## Data Update Workflow (Default Method)

**This is the standard process for adding or modifying race data. Always use this workflow.**

### Quick Commands

```bash
# List all races
python3 tools/update_races.py list

# Add a new race (interactive prompts)
python3 tools/update_races.py add-race

# Add a candidate to an existing race
python3 tools/update_races.py add-candidate me-senate-2026

# Regenerate all pages after manual edits to races.json
python3 tools/update_races.py regenerate
```

### Full Process: Adding a New Race

1. Run `python3 tools/update_races.py add-race` — fills in races.json, regenerates map + state pages
2. Create folder: `races/{race-id}/`
3. Create `index.html` race overview (copy `me-senate-2026/index.html` as template)
4. Create candidate subfolders with `index.html` each
5. Optionally add a `.race-card` block to the landing page for featured races
6. `git push` to deploy — the state lights up on the map automatically

### Full Process: Adding a New Candidate

1. Run `python3 tools/update_races.py add-candidate <race-id>` — updates races.json, regenerates pages
2. Create folder: `races/{race-id}/{lastname}/`
3. Create `index.html` dossier (copy existing dossier as template)
4. Must include: `<link rel="stylesheet" href="/css/dossier.css">`, breadcrumb nav, party class on header
5. Add link in the race overview page
6. `git push` to deploy

### County Buildout (After Dossiers Are Complete)

```bash
# Preview
python3 tools/build_county_hub.py WA {county-slug} --dry-run

# Build pages, regenerate state hub, get landing page snippet
python3 tools/build_county_hub.py WA {county-slug}

# List all counties and their build status
python3 tools/build_county_hub.py WA --list-counties
```

See `tools/COUNTY_BUILDOUT.md` for the full process documentation.

### Curated Deep-Dive Protection

`generate_candidate_pages.py` regenerates every race in `races.json` from
clearthemud dossier JSON. Hand-authored OSINT deep-dives would otherwise be
overwritten with thin T1 stubs. The generator reads `tools/data/curated_races.json`
and **skips** every race-id listed there (it logs each preserved race on run).

**When you publish a new deep-dive** (via clearthemud's `convert_to_ctm_landing.py`),
add its race-id to `tools/data/curated_races.json` or the next bulk regen will
clobber it. Tests: `tools/tests/test_curated_skip.py`.

### Manual Edit Alternative

Edit `tools/data/races.json` directly, then run:
```bash
python3 tools/generate_states.py
```

Reads `tools/data/states.json` + `tools/data/races.json`, writes all `states/` pages + `sitemap.xml`.
Re-run after editing `races.json`. Does NOT touch `index.html`, `races/*`, or `css/*`.

## Interactive Map

The `/states/` page displays an interactive SVG US map above the state grid.
- States with races in `races.json` appear gold (clickable, navigate to state page)
- States without data appear dark/inactive with "Research coming soon" tooltip
- Map is generated inline by `generate_states.py` from `geo/us-states.svg`
- `window.CTM_ACTIVE_STATES` is set automatically from races.json state_abbr values
- Same inactive/active pattern applies to future state-level district/county maps (Tier 2)

## CSS

Single shared stylesheet at `/css/dossier.css`. Covers:
- Dossier findings with severity badges (CRITICAL/SEVERE/HIGH/MODERATE/LOW)
- Party-specific header gradients (`.header.party-dem`, `.header.party-rep`, `.header.party-neutral`)
- Matchup cards, assessment boxes, BLUF sections (race pages)
- Callouts, note boxes (brief pages)
- Breadcrumb navigation, classification bars
- Print styles, responsive breakpoints

No build tools, no JS frameworks. Push HTML to deploy.

## Public Repo Boundary — Do Not Leak Internal Info (MANDATORY)

This repo is **public solely so GitHub Pages can host clearthemud.org.** Public visibility is a
hosting requirement, not an invitation to track internal work here. Hard rules:

- **This repo receives ONLY validated public site files** — T0–T2 published HTML/CSS/site assets
  and the generators/registry needed to build them. Never commit T3/T4 data, internal research,
  raw collection reports, journalist leads, or other internal artifacts here.
- **ALL issues, bugs, and work items go to the private ADO tracker** (the `clearthemud` data
  pipeline repo) — *including bugs about this repo's own code/tests.* **Never open GitHub issues
  on this repo.** This overrides the generic workspace rule "public repo → GitHub issue."
- The private data pipeline and system of record live in `~/Local/Projects/github/clearthemud/`.
  When unsure whether something is public-ready, it stays there, not here.

## Publication Rules

Only T0-T2 verified findings may be published. T3/T4 data, "RESEARCH NOTE" items, and "Journalist Leads" sections stay in local deliverables until vetted. Audit every finding's source tier before committing to this repo.

### Findings Quality Gates

Before publishing any finding, apply these filters:

1. **T1 trumps T2/T3.** If a T1 source (SOS filing, official record) directly contradicts or renders a T2/T3 finding moot, drop the finding entirely. Example: SOS filing confirms residency → don't publish a "possible non-residency" finding based on an old media bio.
2. **Verify domain ownership before claiming misuse.** A `.com` domain is not a government resource. Only `.gov`, `.us`, or domains confirmed as official county/state property count as government resources. Personal websites styled after an office name are not government resource misuse.
3. **No speculative findings.** If a finding requires "may be," "could be," "raises questions," or "needs clarification" in its core claim, it is not verified — it is speculation. Either verify the claim to T1/T2 or drop it.
4. **Temporal relevance.** Old media coverage does not establish current facts. Board bios, news articles, and social media posts reflect the time they were written. If stronger current evidence exists (SOS filings, current employment records), use the current evidence.

## Related

- Data pipeline: `~/Local/Projects/github/clearthemud/` (private, ADO civic-tech)
- Source dossiers: `~/Local/00-Claude/Clients/Clear_the_Mud_dot_org/Deliverables/dossiers/`
- GitHub org: https://github.com/ClearTheMud

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **ctm-landing** (4764 symbols, 6164 relationships, 57 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/ctm-landing/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/ctm-landing/context` | Codebase overview, check index freshness |
| `gitnexus://repo/ctm-landing/clusters` | All functional areas |
| `gitnexus://repo/ctm-landing/processes` | All execution flows |
| `gitnexus://repo/ctm-landing/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

- Re-index: `npx gitnexus analyze`
- Check freshness: `npx gitnexus status`
- Generate docs: `npx gitnexus wiki`

<!-- gitnexus:end -->
