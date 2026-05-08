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
tools/
  generate_states.py                    -- Generates states/ pages from data files
  data/states.json                      -- 50-state reference data (static)
  data/races.json                       -- Active research tracker (edit per new race)
```

## URL Scheme

- `/states/` — Browse by state (all 50)
- `/states/{state-name}/` — State hub (federal/state/local race sections)
- `/races/{state}-{office}-{year}/` — Race overview
- `/races/{state}-{office}-{year}/{lastname}/` — Candidate dossier
- Folder-based routing: each page is `index.html` inside its folder for clean URLs

## Adding a New Candidate

1. Create folder: `races/me-senate-2026/newname/`
2. Create `index.html` — copy an existing dossier, change content
3. Must include: `<link rel="stylesheet" href="/css/dossier.css">`, breadcrumb nav, party class on header
4. Add link in the race overview page (`races/me-senate-2026/index.html`)
5. `git push` to deploy

## Adding a New Race

1. Create folder: `races/{state}-{office}-{year}/`
2. Create `index.html` race overview (copy `me-senate-2026/index.html` as template)
3. Create candidate subfolders with `index.html` each
4. Add race to `tools/data/races.json` with state_abbr, office, candidates, URL
5. Run `python tools/generate_states.py` to update state hub page and states index
6. Optionally add a `.race-card` block to the landing page for featured races
7. `git push` to deploy

## Regenerating State Pages

```bash
python tools/generate_states.py
```

Reads `tools/data/states.json` + `tools/data/races.json`, writes all `states/` pages + `sitemap.xml`.
Re-run after editing `races.json`. Does NOT touch `index.html`, `races/*`, or `css/*`.

## CSS

Single shared stylesheet at `/css/dossier.css`. Covers:
- Dossier findings with severity badges (CRITICAL/SEVERE/HIGH/MODERATE/LOW)
- Party-specific header gradients (`.header.party-dem`, `.header.party-rep`, `.header.party-neutral`)
- Matchup cards, assessment boxes, BLUF sections (race pages)
- Callouts, note boxes (brief pages)
- Breadcrumb navigation, classification bars
- Print styles, responsive breakpoints

No build tools, no JS frameworks. Push HTML to deploy.

## Publication Rules

Only T0-T2 verified findings may be published. T3/T4 data, "RESEARCH NOTE" items, and "Journalist Leads" sections stay in local deliverables until vetted. Audit every finding's source tier before committing to this repo.

## Related

- Data pipeline: `~/Local/Projects/github/clearthemud/` (private, ADO civic-tech)
- Source dossiers: `~/Local/00-Claude/Clients/Clear_the_Mud_dot_org/Deliverables/dossiers/`
- GitHub org: https://github.com/ClearTheMud
