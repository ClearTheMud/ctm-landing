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
css/
  dossier.css                           -- Shared styles for all dossier/race pages
races/
  me-senate-2026/
    index.html                          -- Race overview (dynamics, matchup, field changes)
    collins/index.html                  -- Collins dossier (R, incumbent)
    platner/index.html                  -- Platner dossier (D, frontrunner)
    costello/index.html                 -- Costello brief (D, longshot)
```

## URL Scheme

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
4. Add a `.race-card` block to the landing page `index.html`
5. `git push` to deploy

## CSS

Single shared stylesheet at `/css/dossier.css`. Covers:
- Dossier findings with severity badges (CRITICAL/SEVERE/HIGH/MODERATE/LOW)
- Party-specific header gradients (`.header.party-dem`, `.header.party-rep`, `.header.party-neutral`)
- Matchup cards, assessment boxes, BLUF sections (race pages)
- Callouts, note boxes (brief pages)
- Breadcrumb navigation, classification bars
- Print styles, responsive breakpoints

No build tools, no JS frameworks. Push HTML to deploy.

## Related

- Data pipeline: `~/Local/Projects/github/clearthemud/` (private, ADO civic-tech)
- Source dossiers: `~/Local/00-Claude/Clients/Clear_the_Mud_dot_org/Deliverables/dossiers/`
- GitHub org: https://github.com/ClearTheMud
