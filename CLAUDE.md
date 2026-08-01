# ctm-landing — clearthemud.org Website

Static site for clearthemud.org, hosted on GitHub Pages with Cloudflare DNS. Publishes verified candidate dossiers organized by race.

## What belongs in this repository

This repo is **published output only**. It is public because GitHub Pages must
serve clearthemud.org from a public repository. That is a hosting requirement,
not an invitation to work here.

**Site generation code lives in the clearthemud build repo, not here.**

| Belongs here | Does not belong here |
|---|---|
| Rendered HTML under `races/`, `states/` | Generators, builders, converters |
| `css/`, `js/`, `geo/` site assets | Research data, YAML, working notes |
| `CNAME`, `sitemap.xml`, `index.html` | Anything that produces the files above |

**Do not add a script to this repository.** If a page needs to change, the
change belongs in the build repo that generates it, and the output is
published from there. A generator added here is invisible to the build repo's
tests and its review process, and the two copies drift apart silently: a fix
lands in one, the other overwrites it on the next run, and the correction
disappears from the live site with nothing failing.

`tools/` predated this rule. The nine site generators it held moved to the
build repo on 2026-08-01 (ADO #1975) and now live there under `site_tools/`,
with their tests. What is left is **frozen and finishes moving after the
2026-08-04 primary is certified**:

- `primary_results.py` and `inject_primary_results.py`, which run on election
  night and own a contested write path. Moving them days before the primary
  was the larger risk, so they stayed.
- `tools/data/`, the registry and the two publication gate lists. The
  pre-commit gate reads the lists from this repo, and the results injector
  writes `races.json` here, so the data cannot lead the code out.
- `tools/tests/`, covering the two files above plus the gate lists and
  published site content.

Do not extend any of it, do not add tests to it, and do not treat its presence
as precedent. If a task seems to require adding to `tools/`, it belongs in the
build repo instead, and the publish allowlist will refuse it here.

Issues and work items go to Azure DevOps, project `civic-tech`. Do not open
GitHub issues on this repository, including issues about this repository's own
code.

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
tools/                                  -- FROZEN. Generators moved to the build repo (ADO #1975).
  primary_results.py                    -- Election-night results block. Moves after certification.
  inject_primary_results.py             -- Injects that block into race hubs. Moves after certification.
  data/races.json                       -- Race and candidate registry, and the ballot-status truth
                                           the build repo's converter reads. Written here on election
                                           night by inject_primary_results.py.
  data/publish-allowlist.json           -- What may be tracked here at all. Read by .githooks/pre-commit.
  data/do-not-publish.json              -- Pages withheld on purpose. Read by the same hook.
  data/states.json, counties.json,      -- Reference and registry data the generators read from the
    places.json, county_races.json,        build repo. Still served from here as one registry.
    curated_races.json
  tests/                                -- Covers the two files above, the gate lists, and published
                                           site content. Generator tests went to the build repo.
```

## URL Scheme

- `/states/` — Browse by state (all 50)
- `/states/{state-name}/` — State hub (federal/state/local race sections)
- `/races/{state}-{office}-{year}/` — Race overview
- `/races/{state}-{office}-{year}/{lastname}/` — Candidate dossier
- Folder-based routing: each page is `index.html` inside its folder for clean URLs

## Changing site data

**Race and candidate content is generated in the build repo and published from
there.** There is no supported workflow for authoring content in this
repository.

To add a race, add a candidate, refresh finance figures, or publish a
dossier, do the work in the build repo and let its publish step write the
output here. Then review the resulting diff before pushing, and stage only the
paths you intended to change.

### Before you push

- Stage explicit paths. Never `git add .` or `git add -A` in this repo.
- Read the diff. An unexpected file in it means something regenerated content
  it did not own, and pushing it will overwrite work.
- Untracked directories under `races/` are not automatically safe to publish.
  A candidate can end up with two pages at two URLs that way.

### What is left in tools/

The generators moved to the build repo on 2026-08-01 and are gone from here.
`tools/data/publish-allowlist.json` now names each of them on the deny list,
so a copy cannot come back without someone deliberately editing the gate.

Two files remain, `primary_results.py` and `inject_primary_results.py`. They
run on election night, which is why they did not move three days before the
primary. They move after certification, and the deny entries above are the
pattern to follow when they do.

The bulk page generator that used to live here still behaves the same way,
now from the build repo: it regenerates races from dossier JSON and will
replace a detailed page with a thin one unless the race is listed in
`tools/data/curated_races.json`. That list is still maintained by hand.

## Interactive Map

The `/states/` page displays an interactive SVG US map above the state grid.
- States with races in `races.json` appear gold (clickable, navigate to state page)
- States without data appear dark/inactive with "Research coming soon" tooltip
- Map is generated inline by the build repo's `site_tools/generate_states.py` from `geo/us-states.svg`
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

- **This repo receives ONLY validated public site files**: published HTML, CSS and site assets,
  plus the small data registry the site needs at serve time. It does **not** receive the code that
  produces them. Generators, builders and converters belong in the build repo. See "What belongs
  in this repository" at the top of this file. Never commit T4 data, internal research, raw
  collection reports, journalist leads, or other internal artifacts here.
- **ALL issues, bugs, and work items go to the private ADO tracker** (the `clearthemud` data
  pipeline repo) — *including bugs about this repo's own code/tests.* **Never open GitHub issues
  on this repo.** This overrides the generic workspace rule "public repo → GitHub issue."
- The private data pipeline and system of record live in `~/Local/Projects/github/clearthemud/`.
  When unsure whether something is public-ready, it stays there, not here.

### Install the promotion gate first (every clone)

```bash
git config core.hooksPath .githooks
```

This is **not** optional and is **not** inherited by a clone. `core.hooksPath` is
local config, so a fresh clone has the gate switched off until someone runs that
line. Run it before your first commit.

The gate enforces two lists:

| List | Question it answers |
|---|---|
| `tools/data/publish-allowlist.json` | Is this path site content at all? A path must match `allow` (and miss `deny`) to be tracked. |
| `tools/data/do-not-publish.json` | Is this specific page withheld on purpose? |

The allowlist is the broader of the two. A denylist only knows about pages someone
already thought to name, so it cannot catch a whole category of file that nobody
anticipated. If you need to track something new, add it to the allowlist with a
reason in the same commit.

`tools/tests/test_publish_allowlist.py` and `tools/tests/test_do_not_publish.py`
cover both lists, but **nothing runs them automatically**. This repository has
no continuous integration, no pre-push hook and no branch protection. The
pre-commit hook is the only gate, it is per-clone, and it only sees files it is
installed to see.

Do not rely on a check catching a mistake here. Read the diff before pushing.

## Publication Rules

T0 through T3 may be published. T4 is withheld, along with "RESEARCH NOTE"
items and "Journalist Leads" sections, which stay in the build repo.

The tier gate lives in the build repo's converter, which is the single place
that decides. Do not re-implement a tier check here, and do not hand-edit a
page to add a claim the gate withheld.

**A tier is not the only test.** A claim about someone who is not the
candidate, a spouse, a child, a named private associate, publishes only when
that person's own disclosure is the source, for example a candidate naming
their spouse in their own campaign biography. Something we observed and wrote
up about a private individual is not published at any tier.

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
