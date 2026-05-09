#!/usr/bin/env python3
"""
generate_states.py — Generates 50-state skeleton site for clearthemud.org

Usage:
    python tools/generate_states.py

Reads:
    tools/data/states.json — static state reference data
    tools/data/races.json  — active research tracker

Writes:
    states/index.html            — 50-state grid page
    states/{slug}/index.html     — per-state hub page (x50)
    sitemap.xml                  — XML sitemap
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATES_DIR = REPO_ROOT / "states"
DATA_DIR = Path(__file__).resolve().parent / "data"
SITE_URL = "https://clearthemud.org"

SENATE_CLASS_YEARS = {1: 2030, 2: 2026, 3: 2028}


def load_data():
    with open(DATA_DIR / "states.json") as f:
        data = json.load(f)
    states = data["states"]
    cycle = data["cycle"]
    with open(DATA_DIR / "races.json") as f:
        races = json.load(f)["races"]
    races_by_state = {}
    for race in races:
        races_by_state.setdefault(race["state_abbr"], []).append(race)
    return states, races_by_state, cycle


def render_race_card(race):
    parts = []
    for c in race["candidates"][:2]:
        tag = c["party"].upper()[0]
        parts.append(f'{c["name"]} ({tag})')
    summary = " vs. ".join(parts)
    if len(race["candidates"]) > 2:
        summary += f' + {len(race["candidates"]) - 2} more'
    status_label = race["status"].upper()
    primary = race.get("primary_date", "")
    general = race.get("general_date", "")
    if primary and general:
        date_line = f'\n        <span class="party-tag neutral">Primary: {primary} &bull; General: {general}</span>'
    elif primary:
        date_line = f'\n        <span class="party-tag neutral">Primary: {primary}</span>'
    else:
        date_line = ""
    return f"""      <a href="{race['url']}" class="dossier-link">
        <h4>{race['title']}</h4>{date_line}
        <p><span class="status-active">{status_label}</span> &mdash; {summary}</p>
      </a>"""


def render_no_research(msg):
    return f"""    <div class="no-research">
      <p>{msg}</p>
    </div>"""


def load_state_svg(state_abbr):
    slug = state_abbr.lower()
    svg_path = REPO_ROOT / "geo" / "states" / f"{slug}-districts.svg"
    if svg_path.exists():
        content = svg_path.read_text()
        if content.startswith("<?xml"):
            content = content[content.index("?>") + 2:].strip()
        return content
    return None


def render_state_page(state, state_races, cycle):
    name = state["name"]
    abbr = state["abbr"]
    slug = state["slug"]
    capital = state["capital"]
    districts = state["house_districts"]
    gov_year = state["governor_next"]
    senate_year = SENATE_CLASS_YEARS.get(state["senate_class_up"], "N/A")
    senate_up = senate_year == cycle
    has_races = len(state_races) > 0

    senate_races = [r for r in state_races if "Senate" in r["office"]]
    house_races = [r for r in state_races if "House" in r["office"]]
    gov_races = [r for r in state_races if "Governor" in r["office"]]

    if senate_races:
        senate_html = '    <div class="dossier-links">\n' + "\n".join(render_race_card(r) for r in senate_races) + "\n    </div>"
    else:
        up_note = f" A Senate seat is on the ballot in {cycle}." if senate_up else f" Next Senate election: {senate_year}."
        senate_html = render_no_research(f"No active research on {name} US Senate races.{up_note}")

    if house_races:
        house_html = '    <div class="dossier-links">\n' + "\n".join(render_race_card(r) for r in house_races) + "\n    </div>"
    else:
        d = "district" if districts == 1 else "districts"
        at_large = " (at-large)" if districts == 1 else ""
        house_html = render_no_research(f"No active research on {name}&rsquo;s {districts} US House {d}{at_large}.")

    if gov_races:
        gov_html = '    <div class="dossier-links">\n' + "\n".join(render_race_card(r) for r in gov_races) + "\n    </div>"
    else:
        gov_up = gov_year == cycle
        gov_note = f" Governor is on the ballot in {cycle}." if gov_up else f" Next gubernatorial election: {gov_year}."
        gov_html = render_no_research(f"No active research on {name} gubernatorial race.{gov_note}")

    hero_html = ""
    if not has_races:
        hero_html = f"""
  <div class="no-research no-research--hero">
    <h3>No Active Research</h3>
    <p>Clear the Mud has not yet begun candidate research for {name} in the {cycle} cycle. When research begins, verified dossiers will appear here.</p>
  </div>
"""

    # District map
    district_svg = load_state_svg(abbr)
    if district_svg and house_races:
        district_data_entries = []
        for r in house_races:
            num_candidates = len(r.get("candidates", []))
            district_data_entries.append(f'"{r["id"]}":{{"candidates":{num_candidates}}}')
        district_data_js = "{" + ",".join(district_data_entries) + "}"
        district_map_html = f"""
    <div class="district-map-container">
      {district_svg}
      <div class="map-legend">
        <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--active"></span> Active research</span>
        <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--inactive"></span> Coming soon</span>
      </div>
    </div>
"""
        district_map_script = f"""
<script>window.CTM_DISTRICT_DATA = {district_data_js};</script>
<script src="/js/state-map.js"></script>
"""
    else:
        district_map_html = ""
        district_map_script = ""

    senate_meta = f"Senate seat up in {cycle}" if senate_up else f"Next Senate election: {senate_year}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
<title>{name} &mdash; Candidate Research | clearthemud.org</title>
<meta name="description" content="Verified candidate intelligence for {name} races: US Senate, US House, Governor, and state offices.">
<meta property="og:title" content="{name} &mdash; Candidate Research">
<meta property="og:description" content="Verified candidate intelligence for {name} races: US Senate, US House, Governor, and state offices.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/states/{slug}/">
<link rel="canonical" href="{SITE_URL}/states/{slug}/">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN &mdash; Approved for public sharing</div>

<nav class="dossier-nav">
  <a href="/">clearthemud.org</a>
  <span class="nav-sep">/</span>
  <a href="/states/">States</a>
  <span class="nav-sep">/</span>
  <span class="nav-current">{name}</span>
</nav>

<div class="header party-neutral">
  <div class="page">
    <h1>{name}</h1>
    <h2>Candidate Research &mdash; {cycle} Election Cycle</h2>
    <div class="header-meta">
      <span><span class="tlp-badge">TLP:GREEN</span></span>
      <span><strong>Capital:</strong> {capital}</span>
      <span><strong>US House:</strong> {districts} {"district" if districts == 1 else "districts"}</span>
      <span><strong>{senate_meta}</strong></span>
    </div>
  </div>
</div>

<div class="page">
{hero_html}
{district_map_html}
  <div class="section">
    <h2><span class="section-num">1</span> Federal Races</h2>
    <h3>US Senate</h3>
{senate_html}
    <h3>US House</h3>
{house_html}
  </div>

  <div class="section">
    <h2><span class="section-num">2</span> State Races</h2>
    <h3>Governor</h3>
{gov_html}
    <h3>State Legislature</h3>
{render_no_research(f"No active research on {name} state legislative races.")}
  </div>

  <div class="section">
    <h2><span class="section-num">3</span> Local Races</h2>
{render_no_research(f"Local race coverage is planned for future expansion.")}
  </div>

  <div class="footer">
    <strong>clearthemud.org</strong> &mdash; Verified public-record candidate intelligence
  </div>

</div>

<div class="classification-bar">TLP:GREEN &mdash; Approved for public sharing</div>
{district_map_script}
</body>
</html>
"""


def load_svg_map():
    svg_path = REPO_ROOT / "geo" / "us-states.svg"
    if svg_path.exists():
        content = svg_path.read_text()
        # Strip the XML declaration for inline embedding
        if content.startswith("<?xml"):
            content = content[content.index("?>") + 2:].strip()
        return content
    return None


def render_states_index(states, races_by_state, cycle):
    active_count = sum(1 for s in states if s["abbr"] in races_by_state)
    total_races = sum(len(v) for v in races_by_state.values())

    # State data for JS — includes dossier counts per state
    state_data_entries = []
    for abbr in sorted(races_by_state.keys()):
        state_races = races_by_state[abbr]
        total_candidates = sum(len(r.get("candidates", [])) for r in state_races)
        total_races = len(state_races)
        state_data_entries.append(f'"{abbr}":{{"dossiers":{total_candidates},"races":{total_races}}}')
    state_data_js = "{" + ",".join(state_data_entries) + "}"

    # SVG map
    svg_content = load_svg_map()
    if svg_content:
        map_html = f"""
  <p class="map-intro">Select a highlighted state to read verified candidate dossiers.</p>
  <div class="map-container">
    {svg_content}
    <div class="map-legend">
      <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--active"></span> Published dossiers</span>
      <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--inactive"></span> Not yet covered</span>
    </div>
    <p class="map-fallback-link">Or <a href="#state-grid">browse the full list below</a></p>
  </div>
"""
        map_script = f"""
<script>window.CTM_STATE_DATA = {state_data_js};</script>
<script src="/js/us-map.js"></script>
"""
    else:
        map_html = ""
        map_script = ""

    cards = []
    for state in sorted(states, key=lambda s: s["name"]):
        slug = state["slug"]
        abbr = state["abbr"]
        name = state["name"]
        sr = races_by_state.get(abbr, [])
        if sr:
            count = len(sr)
            badge = f'\n      <span class="state-badge">{count} {"race" if count == 1 else "races"}</span>'
            active_class = " state-card--active"
        else:
            badge = ""
            active_class = ""
        cards.append(f"""    <a href="/states/{slug}/" class="state-card{active_class}">
      <span class="state-abbr">{abbr}</span>
      <span class="state-name">{name}</span>{badge}
    </a>""")

    cards_html = "\n".join(cards)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
<title>All States &mdash; Candidate Research by State | clearthemud.org</title>
<meta name="description" content="Browse verified candidate intelligence organized by state. Federal, state, and local race coverage across all 50 states.">
<meta property="og:title" content="All States &mdash; Candidate Research by State">
<meta property="og:description" content="Browse verified candidate intelligence organized by state. Federal, state, and local race coverage across all 50 states.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/states/">
<link rel="canonical" href="{SITE_URL}/states/">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN &mdash; Approved for public sharing</div>

<nav class="dossier-nav">
  <a href="/">clearthemud.org</a>
  <span class="nav-sep">/</span>
  <span class="nav-current">States</span>
</nav>

<div class="header party-neutral">
  <div class="page">
    <h1>Browse by State</h1>
    <h2>Candidate Research &mdash; {cycle} Election Cycle</h2>
    <div class="header-meta">
      <span><span class="tlp-badge">TLP:GREEN</span></span>
      <span><strong>Active Research:</strong> {active_count} {"state" if active_count == 1 else "states"}</span>
      <span><strong>Total Races:</strong> {total_races}</span>
    </div>
  </div>
</div>

<div class="page">
{map_html}
  <div id="state-grid" class="state-grid">
{cards_html}
  </div>

  <div class="footer">
    <strong>clearthemud.org</strong> &mdash; Verified public-record candidate intelligence
  </div>

</div>

<div class="classification-bar">TLP:GREEN &mdash; Approved for public sharing</div>
{map_script}
</body>
</html>
"""


def render_sitemap(states, races_by_state):
    urls = [
        SITE_URL + "/",
        SITE_URL + "/states/",
    ]
    for state in sorted(states, key=lambda s: s["slug"]):
        urls.append(f'{SITE_URL}/states/{state["slug"]}/')
    for race_list in races_by_state.values():
        for race in race_list:
            urls.append(SITE_URL + race["url"])
            for c in race.get("candidates", []):
                if "url" in c:
                    urls.append(SITE_URL + c["url"])
    entries = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""


def main():
    states, races_by_state, cycle = load_data()

    STATES_DIR.mkdir(exist_ok=True)

    index_html = render_states_index(states, races_by_state, cycle)
    (STATES_DIR / "index.html").write_text(index_html)
    print("  wrote states/index.html")

    for state in states:
        slug = state["slug"]
        state_dir = STATES_DIR / slug
        state_dir.mkdir(exist_ok=True)
        sr = races_by_state.get(state["abbr"], [])
        page_html = render_state_page(state, sr, cycle)
        (state_dir / "index.html").write_text(page_html)
        print(f"  wrote states/{slug}/index.html")

    sitemap = render_sitemap(states, races_by_state)
    (REPO_ROOT / "sitemap.xml").write_text(sitemap)
    print("  wrote sitemap.xml")

    print(f"\nDone: {len(states)} state pages + index + sitemap")


if __name__ == "__main__":
    main()
