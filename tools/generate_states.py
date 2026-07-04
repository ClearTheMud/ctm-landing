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

SENATE_2026_STATES = {
    "AL", "AK", "AR", "CO", "DE", "GA", "ID", "IL", "IA", "KS",
    "KY", "LA", "ME", "MA", "MI", "MN", "MS", "MT", "NE", "NH",
    "NJ", "NM", "NC", "OK", "OR", "RI", "SC", "SD", "TN", "TX",
    "VA", "WV", "WY",
}


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
        <p><span class="status-active">{status_label}</span>, {summary}</p>
      </a>"""


def render_no_research(msg):
    return f"""    <div class="no-research">
      <p>{msg}</p>
    </div>"""


def load_legislative_svg(state_abbr):
    slug = state_abbr.lower()
    svg_path = REPO_ROOT / "geo" / "states" / f"{slug}-legislative.svg"
    if svg_path.exists():
        content = svg_path.read_text()
        if content.startswith("<?xml"):
            content = content[content.index("?>") + 2:].strip()
        return content
    return None


def render_legislature_section(state_name, leg_senate, leg_house, state_abbr=""):
    if not leg_senate and not leg_house:
        return render_no_research(f"No active research on {state_name} state legislative races.")

    from collections import defaultdict
    districts = defaultdict(list)
    for r in leg_senate + leg_house:
        districts[r["district"]].append(r)

    rows = []
    for d in sorted(districts.keys(), key=lambda x: int(x)):
        races = districts[d]
        links = []
        for r in sorted(races, key=lambda x: x["office"]):
            label = r["office"].replace("State ", "")
            count = len(r["candidates"])
            links.append(f'<a href="{r["url"]}">{label}</a> ({count})')
        rows.append(f'      <tr id="ld-{d}"><td>LD-{d}</td><td>{" &bull; ".join(links)}</td></tr>')

    total_races = len(leg_senate) + len(leg_house)
    total_cands = sum(len(r["candidates"]) for r in leg_senate + leg_house)

    leg_svg = load_legislative_svg(state_abbr) if state_abbr else None
    map_html = ""
    map_script = ""
    if leg_svg:
        leg_data_entries = []
        for d in sorted(districts.keys(), key=lambda x: int(x)):
            race_count = len(districts[d])
            cand_count = sum(len(r["candidates"]) for r in districts[d])
            leg_data_entries.append(f'"{d}":{{"races":{race_count},"candidates":{cand_count}}}')
        leg_data_js = "{" + ",".join(leg_data_entries) + "}"

        map_html = f"""
    <div class="legislative-map-container">
      {leg_svg}
      <div class="map-legend">
        <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--active"></span> Active races</span>
        <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--inactive"></span> No races tracked</span>
      </div>
      <p style="text-align:center;color:#8899aa;font-size:13px;margin:8px 0 0;">Click a district to jump to its races below</p>
    </div>
"""
        map_script = f"""
<script>window.CTM_LEG_DATA = {leg_data_js};</script>
<script src="/js/legislative-map.js"></script>
"""

    return f"""{map_html}    <div class="finding">
      <p>{total_races} races tracked, {total_cands} candidates filed</p>
      <table>
        <thead><tr><th>District</th><th>Races</th></tr></thead>
        <tbody>
{"".join(rows)}
        </tbody>
      </table>
    </div>
{map_script}"""


def load_state_svg(state_abbr):
    slug = state_abbr.lower()
    svg_path = REPO_ROOT / "geo" / "states" / f"{slug}-districts.svg"
    if svg_path.exists():
        content = svg_path.read_text()
        if content.startswith("<?xml"):
            content = content[content.index("?>") + 2:].strip()
        return content
    return None


def load_county_svg(state_abbr):
    slug = state_abbr.lower()
    svg_path = REPO_ROOT / "geo" / "states" / f"{slug}-counties.svg"
    if svg_path.exists():
        content = svg_path.read_text()
        if content.startswith("<?xml"):
            content = content[content.index("?>") + 2:].strip()
        return content
    return None


def load_counties_data():
    path = DATA_DIR / "counties.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def load_places_data():
    path = DATA_DIR / "places.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def load_county_races_data():
    path = DATA_DIR / "county_races.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


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

    senate_races = [r for r in state_races if r["office"] == "US Senate"]
    house_races = [r for r in state_races if r["office"] == "US House"]
    gov_races = [r for r in state_races if "Governor" in r["office"]]
    leg_senate = [r for r in state_races if r["office"] == "State Senate"]
    leg_house = [r for r in state_races if r["office"].startswith("State House")]
    # Statewide judicial (Supreme Court, Court of Appeals). Gated on status so
    # draft stub pages do not render on the live hub until enriched and activated.
    judicial_races = [
        r for r in state_races
        if ("Supreme Court" in r["office"] or "Court of Appeals" in r["office"])
        and r.get("status") != "draft"
    ]

    if senate_races:
        senate_section = '    <h3>US Senate</h3>\n    <div class="dossier-links">\n' + "\n".join(render_race_card(r) for r in senate_races) + "\n    </div>"
    elif senate_up:
        senate_section = f'    <h3>US Senate</h3>\n' + render_no_research(f"A {name} Senate seat is on the ballot in {cycle}. Research will be added when available.")
    else:
        senate_section = ""

    if house_races:
        house_section = '    <h3>US House</h3>\n    <div class="dossier-links">\n' + "\n".join(render_race_card(r) for r in house_races) + "\n    </div>"
    else:
        d = "district" if districts == 1 else "districts"
        at_large = " (at-large)" if districts == 1 else ""
        house_section = '    <h3>US House</h3>\n' + render_no_research(f"No active research on {name}&rsquo;s {districts} US House {d}{at_large}.")

    gov_up = gov_year == cycle
    if gov_races:
        gov_section = '    <h3>Governor</h3>\n    <div class="dossier-links">\n' + "\n".join(render_race_card(r) for r in gov_races) + "\n    </div>"
    elif gov_up:
        gov_section = '    <h3>Governor</h3>\n' + render_no_research(f"The {name} governor&rsquo;s race is on the ballot in {cycle}. Research will be added when available.")
    else:
        gov_section = ""

    if judicial_races:
        judicial_section = '    <h3>Statewide Judicial</h3>\n    <div class="dossier-links">\n' + "\n".join(render_race_card(r) for r in judicial_races) + "\n    </div>"
    else:
        judicial_section = ""

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

    # County map
    counties_data = load_counties_data()
    county_svg = load_county_svg(abbr)
    state_counties = counties_data.get(abbr, [])
    if county_svg and state_counties:
        county_data_entries = []
        for c in state_counties:
            county_data_entries.append(f'"{c["slug"]}":{{"places":0}}')
        county_data_js = "{" + ",".join(county_data_entries) + "}"
        county_map_html = f"""
    <div class="county-map-container">
      {county_svg}
      <div class="map-legend">
        <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--active"></span> Active research</span>
        <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--inactive"></span> Coming soon</span>
      </div>
    </div>
"""
        county_map_script = f"""
<script>window.CTM_COUNTY_DATA = {county_data_js};</script>
<script>window.CTM_STATE_PATH = '/states/{slug}/';</script>
<script src="/js/county-map.js"></script>
"""
    else:
        county_map_html = ""
        county_map_script = ""

    senate_meta = f"Senate seat up in {cycle}" if senate_up else f"Next Senate election: {senate_year}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
<title>{name}, Candidate Research | clearthemud.org</title>
<meta name="description" content="Verified candidate intelligence for {name} races: US Senate, US House, Governor, and state offices.">
<meta property="og:title" content="{name}, Candidate Research">
<meta property="og:description" content="Verified candidate intelligence for {name} races: US Senate, US House, Governor, and state offices.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/states/{slug}/">
<link rel="canonical" href="{SITE_URL}/states/{slug}/">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>

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
    <h2>Candidate Research, {cycle} Election Cycle</h2>
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
{senate_section}
{house_section}
  </div>

  <div class="section">
    <h2><span class="section-num">2</span> State Races</h2>
{gov_section}
    <h3>State Legislature</h3>
{render_legislature_section(name, leg_senate, leg_house, abbr)}
{judicial_section}
  </div>

  <div class="section">
    <h2><span class="section-num">3</span> Local Races</h2>
{county_map_html if county_map_html else render_no_research(f"Local race coverage is planned for future expansion.")}
  </div>

  <div class="footer">
    <strong>clearthemud.org</strong>, Verified public-record candidate intelligence<br>
    <a href="mailto:contact@clearthemud.org">contact@clearthemud.org</a>
  </div>

</div>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>
{district_map_script}
{county_map_script}
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

    # State data for JS — includes dossier counts and senate flag per state
    all_abbrs = sorted(set(list(races_by_state.keys()) + list(SENATE_2026_STATES)))
    state_data_entries = []
    for abbr in all_abbrs:
        state_races = races_by_state.get(abbr, [])
        total_candidates = sum(len(r.get("candidates", [])) for r in state_races)
        race_count = len(state_races)
        senate = "true" if abbr in SENATE_2026_STATES else "false"
        state_data_entries.append(
            f'"{abbr}":{{"dossiers":{total_candidates},"races":{race_count},"senate":{senate}}}'
        )
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
      <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--senate"></span> 2026 U.S. Senate race</span>
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
<title>All States, Candidate Research by State | clearthemud.org</title>
<meta name="description" content="Browse verified candidate intelligence organized by state. Federal, state, and local race coverage across all 50 states.">
<meta property="og:title" content="All States, Candidate Research by State">
<meta property="og:description" content="Browse verified candidate intelligence organized by state. Federal, state, and local race coverage across all 50 states.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/states/">
<link rel="canonical" href="{SITE_URL}/states/">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>

<nav class="dossier-nav">
  <a href="/">clearthemud.org</a>
  <span class="nav-sep">/</span>
  <span class="nav-current">States</span>
</nav>

<div class="header party-neutral">
  <div class="page">
    <h1>Browse by State</h1>
    <h2>Candidate Research, {cycle} Election Cycle</h2>
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
    <strong>clearthemud.org</strong>, Verified public-record candidate intelligence<br>
    <a href="mailto:contact@clearthemud.org">contact@clearthemud.org</a>
  </div>

</div>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>
{map_script}
</body>
</html>
"""


def load_place_svg(state_abbr, county_slug):
    slug = state_abbr.lower()
    svg_path = REPO_ROOT / "geo" / "states" / f"{slug}-{county_slug}-places.svg"
    if svg_path.exists():
        content = svg_path.read_text()
        if content.startswith("<?xml"):
            content = content[content.index("?>") + 2:].strip()
        return content
    return None


def render_county_race_table(county_races_list, county_slug, abbr_lower):
    """Render HTML for county office race tables."""
    if not county_races_list:
        return """  <div class="section">
    <h2><span class="section-num">1</span> County Offices</h2>
    <div class="no-research">
      <p>No county office filings recorded for this election cycle.</p>
    </div>
  </div>"""

    PARTY_LABELS = {
        "dem": "D", "rep": "R", "ind": "I", "lib": "L",
        "nonpartisan": "NP", "other": "O",
    }
    PARTY_CLASSES = {
        "dem": "party-dem", "rep": "party-rep", "ind": "party-neutral",
        "lib": "party-neutral", "nonpartisan": "party-neutral",
        "other": "party-neutral",
    }

    rows = []
    for race in county_races_list:
        office = race["office"]
        race_id = f"{abbr_lower}-{county_slug}-{_office_slug(office)}-2026"
        race_url = f"/races/{race_id}/"
        cand_parts = []
        for c in race["candidates"]:
            party_tag = PARTY_LABELS.get(c.get("party_code", "nonpartisan"), "NP")
            cand_parts.append(f'{c["name"]} ({party_tag})')
        cands_str = ", ".join(cand_parts)
        status = race["candidates"][0].get("election_status", "")
        rows.append(f'        <tr><td><a href="{race_url}">{office}</a></td>'
                    f'<td>{len(race["candidates"])}</td>'
                    f'<td>{cands_str}</td>'
                    f'<td>{status}</td></tr>')

    return f"""  <div class="section">
    <h2><span class="section-num">1</span> County Offices</h2>
    <div class="finding">
      <table>
        <thead><tr><th>Office</th><th>#</th><th>Candidates</th><th>Status</th></tr></thead>
        <tbody>
{"".join(rows)}
        </tbody>
      </table>
    </div>
  </div>"""


def _office_slug(office):
    import re
    slug = office.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def render_county_page(state, county, cycle, county_races=None):
    name = state["name"]
    abbr = state["abbr"]
    slug = state["slug"]
    county_name = county["name"]
    county_slug = county["slug"]
    county_fips = county["fips"]

    place_svg = load_place_svg(abbr, county_slug)
    places_data = load_places_data()
    county_places = places_data.get(abbr, {}).get(county_slug, [])

    cr = county_races or {}
    county_race_list = cr.get(abbr, {}).get(county_slug, {}).get("races", [])

    PARTY_MAP = {
        "DEMOCRATIC": "dem", "DEMOCRAT": "dem", "MODERATE DEMOCRAT": "dem",
        "REPUBLICAN": "rep", "REPUBILCAN": "rep",
        "INDEPENDENT": "ind", "LIBERTARIAN": "lib",
        "STATES NO PARTY PREFERENCE": "nonpartisan", "NONPARTISAN": "nonpartisan",
    }
    for race in county_race_list:
        for c in race.get("candidates", []):
            c["party_code"] = PARTY_MAP.get(c.get("party", "").upper(), "nonpartisan")

    race_section = render_county_race_table(county_race_list, county_slug, abbr.lower())

    if place_svg and county_places:
        place_data_js = "{}"
        place_map_html = f"""
    <div class="place-map-container">
      {place_svg}
      <div class="map-legend">
        <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--active"></span> Active research</span>
        <span class="map-legend-item"><span class="map-legend-swatch map-legend-swatch--inactive"></span> Coming soon</span>
      </div>
    </div>
"""
        place_map_script = f"""
<script>window.CTM_PLACE_DATA = {place_data_js};</script>
<script src="/js/place-map.js"></script>
"""
    else:
        place_map_html = ""
        place_map_script = ""

    places_section = ""
    if county_places:
        places_section = """  <div class="section">
    <h2><span class="section-num">2</span> Cities &amp; Towns</h2>
    <div class="no-research">
      <p>City and town race coverage is coming soon.</p>
    </div>
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
<title>{county_name} County, {name}, Local Races | clearthemud.org</title>
<meta name="description" content="Local race coverage for {county_name} County, {name}. Browse cities and towns with verified candidate intelligence.">
<meta property="og:title" content="{county_name} County, {name}, Local Races">
<meta property="og:description" content="Local race coverage for {county_name} County, {name}.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/states/{slug}/{county_slug}/">
<link rel="canonical" href="{SITE_URL}/states/{slug}/{county_slug}/">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>

<nav class="dossier-nav">
  <a href="/">clearthemud.org</a>
  <span class="nav-sep">/</span>
  <a href="/states/">States</a>
  <span class="nav-sep">/</span>
  <a href="/states/{slug}/">{name}</a>
  <span class="nav-sep">/</span>
  <span class="nav-current">{county_name} County</span>
</nav>

<div class="header party-neutral">
  <div class="page">
    <h1>{county_name} County</h1>
    <h2>Local Races, {cycle} Election Cycle</h2>
    <div class="header-meta">
      <span><span class="tlp-badge">TLP:GREEN</span></span>
      <span><strong>State:</strong> {name}</span>
      <span><strong>FIPS:</strong> {county_fips}</span>
      <span><strong>Places:</strong> {len(county_places)}</span>
    </div>
  </div>
</div>

<div class="page">

{place_map_html}
{race_section}

{places_section}

  <div class="footer">
    <strong>clearthemud.org</strong>, Verified public-record candidate intelligence<br>
    <a href="mailto:contact@clearthemud.org">contact@clearthemud.org</a>
  </div>

</div>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>
{place_map_script}
</body>
</html>
"""


def render_sitemap(states, races_by_state, counties_data):
    urls = [
        SITE_URL + "/",
        SITE_URL + "/states/",
    ]
    for state in sorted(states, key=lambda s: s["slug"]):
        urls.append(f'{SITE_URL}/states/{state["slug"]}/')
        for county in counties_data.get(state["abbr"], []):
            urls.append(f'{SITE_URL}/states/{state["slug"]}/{county["slug"]}/')
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
    counties_data = load_counties_data()
    county_races = load_county_races_data()

    STATES_DIR.mkdir(exist_ok=True)

    index_html = render_states_index(states, races_by_state, cycle)
    (STATES_DIR / "index.html").write_text(index_html)
    print("  wrote states/index.html")

    county_pages = 0
    for state in states:
        slug = state["slug"]
        abbr = state["abbr"]
        state_dir = STATES_DIR / slug
        state_dir.mkdir(exist_ok=True)
        sr = races_by_state.get(abbr, [])
        page_html = render_state_page(state, sr, cycle)
        (state_dir / "index.html").write_text(page_html)
        print(f"  wrote states/{slug}/index.html")

        for county in counties_data.get(abbr, []):
            county_dir = state_dir / county["slug"]
            county_dir.mkdir(exist_ok=True)
            county_html = render_county_page(state, county, cycle, county_races)
            (county_dir / "index.html").write_text(county_html)
            county_pages += 1
        if counties_data.get(abbr):
            print(f"    + {len(counties_data[abbr])} county pages")

    sitemap = render_sitemap(states, races_by_state, counties_data)
    (REPO_ROOT / "sitemap.xml").write_text(sitemap)
    print("  wrote sitemap.xml")

    print(f"\nDone: {len(states)} state pages + {county_pages} county pages + index + sitemap")


if __name__ == "__main__":
    main()
