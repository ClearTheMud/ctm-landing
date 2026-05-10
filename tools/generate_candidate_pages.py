#!/usr/bin/env python3
"""
generate_candidate_pages.py — Generates candidate dossier pages from clearthemud JSON data

Usage:
    python3 tools/generate_candidate_pages.py           # all states with races
    python3 tools/generate_candidate_pages.py WA        # single state
    python3 tools/generate_candidate_pages.py WA ME     # multiple states

Reads:
    tools/data/races.json — race/candidate roster
    ~/Local/Projects/github/clearthemud/output/dossiers/{state}/{year}/... — dossier JSON

Writes:
    races/{race-id}/index.html — race overview page
    races/{race-id}/{lastname}/index.html — candidate dossier page
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RACES_DIR = REPO_ROOT / "races"
DATA_DIR = Path(__file__).resolve().parent / "data"
DOSSIER_ROOT = Path.home() / "Local/Projects/github/clearthemud/output/dossiers"
SITE_URL = "https://clearthemud.org"

PARTY_CLASS = {
    "D": "party-dem", "R": "party-rep", "I": "party-neutral",
    "L": "party-neutral", "Libertarian": "party-neutral",
    "Cascade": "party-neutral", "Fifth Republic": "party-neutral",
    "NP": "party-neutral", "Non-Partisan": "party-neutral",
    "Socialist Workers": "party-neutral", "Union": "party-neutral",
    "Pro Gun Liberal": "party-neutral", "No Kings": "party-neutral",
    "Standup-America": "party-neutral",
    "dem": "party-dem", "rep": "party-rep", "ind": "party-neutral",
    "lib": "party-neutral", "nonpartisan": "party-neutral",
    "other": "party-neutral",
}

PARTY_FULL = {
    "D": "Democratic", "R": "Republican", "I": "Independent",
    "NP": "Non-Partisan", "L": "Libertarian",
    "dem": "Democratic", "rep": "Republican", "ind": "Independent",
    "lib": "Libertarian", "nonpartisan": "Non-Partisan",
    "other": "Other",
}


def load_races():
    with open(DATA_DIR / "races.json") as f:
        return json.load(f)["races"]


def load_states_data():
    with open(DATA_DIR / "states.json") as f:
        data = json.load(f)
    return {s["abbr"]: s for s in data["states"]}


def _county_office_to_filename(office):
    """Convert county office name to dossier filename component."""
    import re
    s = office.lower().strip()
    s = re.sub(r"pos\.\s*", "position_", s)
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s


def find_dossier_json(race, lastname):
    state = race["state_abbr"].lower()
    year = race["year"]
    office = race["office"]
    district = race.get("district", "")
    level = race.get("level", "")

    if level == "county":
        subdir = DOSSIER_ROOT / state / str(year) / "county"
        office_part = _county_office_to_filename(office)
        pattern = f"{state}_{office_part}_{lastname}_{year}.json"
    elif office == "State Senate":
        subdir = DOSSIER_ROOT / state / str(year) / "legislative" / f"ld-{int(district):02d}"
        pattern = f"{state}_state_senate_{district}_{lastname}_{year}.json"
    elif office.startswith("State House"):
        subdir = DOSSIER_ROOT / state / str(year) / "legislative" / f"ld-{int(district):02d}"
        pattern = f"{state}_state_house_{district}_{lastname}_{year}.json"
    elif "House" in office and district:
        subdir = DOSSIER_ROOT / state / str(year) / "congressional" / f"cd-{int(district):02d}"
        pattern = f"{state}_house_{district}_{lastname}_{year}.json"
    elif "Senate" in office:
        subdir = DOSSIER_ROOT / state / str(year) / "senate"
        pattern = f"{state}_senate_{lastname}_{year}.json"
    elif "Governor" in office:
        subdir = DOSSIER_ROOT / state / str(year) / "governor"
        pattern = f"{state}_governor_{lastname}_{year}.json"
    else:
        return None

    path = subdir / pattern
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def format_currency(amount):
    if isinstance(amount, (int, float)):
        return f"${amount:,.0f}"
    if isinstance(amount, str):
        import re
        m = re.search(r'\$[\d,]+(?:\.\d+)?', amount)
        if m:
            return m.group(0).split('.')[0]
        return amount
    return "Not reported"


def extract_amount_from_claim(claim_str):
    import re
    if not claim_str:
        return None
    m = re.search(r'\$([\d,]+(?:\.\d+)?)', claim_str)
    if m:
        return float(m.group(1).replace(',', ''))
    return None


def _district_label(race):
    """Return a human-readable district/jurisdiction label for a race."""
    level = race.get("level", "")
    if level == "county":
        return race.get("county", "") + " County"
    district_raw = race.get("district", "")
    if race["office"].startswith("State "):
        return f"LD-{district_raw}"
    return district_raw


def render_candidate_page(race, candidate, dossier, state_info):
    name = candidate["name"]
    party_short = candidate["party"]
    party_full = PARTY_FULL.get(party_short, party_short)
    party_class = PARTY_CLASS.get(party_short, "party-neutral")
    role = candidate.get("role", "challenger").title()
    district = _district_label(race)
    race_title = race["title"]
    race_url = race["url"]
    is_county = race.get("level") == "county"
    county_crumb = ""
    if is_county:
        county_slug = race.get("county_slug", "")
        county_name = race.get("county", "")
        county_crumb = f'  <a href="/states/{state_info["slug"]}/{county_slug}/">{county_name} County</a>\n  <span class="nav-sep">/</span>\n'

    meta = dossier["meta"] if dossier else {}
    cf = dossier.get("campaign_finance", {}) if dossier else {}
    scf = dossier.get("state_campaign_finance", {}) if dossier else {}
    bio = dossier.get("biographical", {}) if dossier else {}

    is_state_race = race["office"].startswith("State ")

    total_raised_claim = cf.get("total_raised", {}).get("claim", "")
    total_spent_claim = cf.get("total_spent", {}).get("claim", "")
    raised_amt = format_currency(extract_amount_from_claim(total_raised_claim)) if total_raised_claim else "Not reported"
    spent_amt = format_currency(extract_amount_from_claim(total_spent_claim)) if total_spent_claim else "Not reported"

    scf_raised_claim = scf.get("total_raised", {}).get("claim", "")
    scf_spent_claim = scf.get("total_spent", {}).get("claim", "")
    scf_ccf_claim = scf.get("cash_carried_forward", {}).get("claim", "")
    scf_entity_claim = scf.get("filing_entity", {}).get("claim", "")
    scf_raised = format_currency(extract_amount_from_claim(scf_raised_claim)) if scf_raised_claim else "Not reported"
    scf_spent = format_currency(extract_amount_from_claim(scf_spent_claim)) if scf_spent_claim else "Not reported"
    scf_ccf = format_currency(extract_amount_from_claim(scf_ccf_claim)) if scf_ccf_claim else None

    source_tier = meta.get("party", {}).get("highest_tier", "T2")

    # Top donors section (FEC data)
    CONDUITS = {"ACTBLUE", "WINRED", "ACTBLUE TECHNICAL SERVICES", "WINRED TECHNICAL SERVICES"}
    donors_html = ""
    top_donors = cf.get("top_donors", [])
    if top_donors:
        rows = []
        for d in top_donors[:10]:
            donor_name = d.get("donor", {}).get("name", "Unknown")
            amount = format_currency(d.get("amount", 0))
            if donor_name.upper() in CONDUITS:
                donor_name += ' <span class="conduit-tag">fundraising platform</span>'
            rows.append(f"          <tr><td>{donor_name}</td><td>{amount}</td></tr>")
        donors_html = f"""
      <h3>Top Donors</h3>
      <div class="finding">
        <table>
          <thead><tr><th>Donor</th><th>Amount</th></tr></thead>
          <tbody>
{"".join(rows)}
          </tbody>
        </table>
      </div>"""

    # Top expenditures section (FEC data)
    expenditures_html = ""
    expenditures = cf.get("expenditures", [])
    if expenditures:
        sorted_exp = sorted(expenditures, key=lambda x: x.get("amount", 0), reverse=True)
        rows = []
        for e in sorted_exp[:10]:
            vendor = e.get("recipient", {}).get("name", "")
            purpose = e.get("purpose", "")
            amount = format_currency(e.get("amount", 0))
            label = f"{vendor} — {purpose}" if vendor and purpose else vendor or purpose or "Unitemized"
            rows.append(f"          <tr><td>{label}</td><td>{amount}</td></tr>")
        expenditures_html = f"""
      <h3>Top Expenditures</h3>
      <div class="finding">
        <table>
          <thead><tr><th>Vendor / Purpose</th><th>Amount</th></tr></thead>
          <tbody>
{"".join(rows)}
          </tbody>
        </table>
      </div>"""

    has_fec_finance = total_raised_claim or top_donors
    has_state_finance = bool(scf_raised_claim)

    finance_section = ""
    if has_state_finance:
        ccf_row = f"\n          <dt>Cash Carried Forward</dt><dd>{scf_ccf}</dd>" if scf_ccf else ""
        finance_section = f"""
    <div class="section">
      <h2><span class="section-num">2</span> Campaign Finance</h2>
      <div class="finding">
        <dl>
          <dt>Total Raised</dt><dd>{scf_raised}</dd>
          <dt>Total Spent</dt><dd>{scf_spent}</dd>{ccf_row}
          <dt>Source</dt><dd>WA Public Disclosure Commission ({source_tier})</dd>
        </dl>
      </div>
    </div>"""
    elif has_fec_finance:
        finance_section = f"""
    <div class="section">
      <h2><span class="section-num">2</span> Campaign Finance</h2>
      <div class="finding">
        <dl>
          <dt>Total Raised</dt><dd>{raised_amt}</dd>
          <dt>Total Spent</dt><dd>{spent_amt}</dd>
          <dt>Source</dt><dd>FEC ({source_tier})</dd>
        </dl>
      </div>
{donors_html}
{expenditures_html}
    </div>"""
    elif is_state_race:
        finance_section = """
    <div class="section">
      <h2><span class="section-num">2</span> Campaign Finance</h2>
      <div class="no-research">
        <p>No state campaign finance filings found for this candidate. Data will be added when available.</p>
      </div>
    </div>"""
    else:
        finance_section = """
    <div class="section">
      <h2><span class="section-num">2</span> Campaign Finance</h2>
      <div class="no-research">
        <p>No FEC filings found for this candidate. Campaign finance data will be added when available.</p>
      </div>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
<title>{name} &mdash; {race_title} | clearthemud.org</title>
<meta name="description" content="Verified candidate dossier for {name} ({party_full}) running in the {race_title}.">
<meta property="og:title" content="{name} &mdash; {race_title}">
<meta property="og:description" content="Verified candidate dossier for {name} ({party_full}) running in the {race_title}.">
<meta property="og:type" content="website">
<link rel="canonical" href="{SITE_URL}{candidate['url']}">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN &mdash; Approved for public sharing</div>

<nav class="dossier-nav">
  <a href="/">clearthemud.org</a>
  <span class="nav-sep">/</span>
  <a href="/states/">States</a>
  <span class="nav-sep">/</span>
  <a href="/states/{state_info['slug']}/">{state_info['name']}</a>
  <span class="nav-sep">/</span>
{county_crumb}  <a href="{race_url}">{race_title}</a>
  <span class="nav-sep">/</span>
  <span class="nav-current">{name}</span>
</nav>

<div class="header {party_class}">
  <div class="page">
    <h1>{name}</h1>
    <h2>{race_title}</h2>
    <div class="header-meta">
      <span><span class="tlp-badge">TLP:GREEN</span></span>
      <span><strong>Party:</strong> {party_full}</span>
      <span><strong>Status:</strong> {role}</span>
      <span><strong>District:</strong> {district}</span>
    </div>
  </div>
</div>

<div class="page">

    <div class="section">
      <h2><span class="section-num">1</span> Candidate Overview</h2>
      <div class="bluf">
        <h3>BLUF &mdash; Bottom Line Up Front</h3>
        <p>{name} is a {party_full} {role.lower()} in the {race_title}.</p>
      </div>
    </div>
{finance_section}
    <div class="section">
      <h2><span class="section-num">3</span> Source Verification</h2>
      <div class="finding">
        <dl>
          <dt>Data Source</dt><dd>clearthemud.org data pipeline</dd>
          <dt>Collection Date</dt><dd>{meta.get("collected_date", "2026-05-09")}</dd>
          <dt>Party Verification</dt><dd>{source_tier} &mdash; {meta.get("party", {}).get("confidence", "unverified")}</dd>
        </dl>
      </div>
    </div>

  <div class="footer">
    <strong>clearthemud.org</strong> &mdash; Verified public-record candidate intelligence
  </div>

</div>

<div class="classification-bar">TLP:GREEN &mdash; Approved for public sharing</div>

</body>
</html>
"""


def render_race_overview(race, dossiers, state_info):
    title = race["title"]
    district = _district_label(race)
    candidates = race["candidates"]
    is_county = race.get("level") == "county"

    candidate_cards = []
    for c in candidates:
        party_short = c["party"]
        party_full = PARTY_FULL.get(party_short, party_short)
        party_class = PARTY_CLASS.get(party_short, "party-neutral")
        party_label = PARTY_FULL.get(party_short, party_short)
        role = c.get("role", "challenger").title()
        lastname = c["url"].rstrip("/").split("/")[-1]

        dossier = dossiers.get(lastname)
        cf = dossier.get("campaign_finance", {}) if dossier else {}
        scf = dossier.get("state_campaign_finance", {}) if dossier else {}
        raised_claim = scf.get("total_raised", {}).get("claim", "") or cf.get("total_raised", {}).get("claim", "")
        raised = format_currency(extract_amount_from_claim(raised_claim)) if raised_claim else "Not reported"

        status_class = "status-incumbent" if role.lower() == "incumbent" else "status-active"
        candidate_cards.append(f"""      <a href="{c['url']}" class="dossier-link">
        <h4>{c['name']} ({party_label})</h4>
        <p><span class="{status_class}">{role.upper()}</span> &mdash; Raised: {raised}</p>
      </a>""")

    cards_html = "\n".join(candidate_cards)

    county_crumb = ""
    if is_county:
        county_slug = race.get("county_slug", "")
        county_name = race.get("county", "")
        county_crumb = f"""  <a href="/states/{state_info['slug']}/{county_slug}/">{county_name} County</a>
  <span class="nav-sep">/</span>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
<title>{title} &mdash; Race Overview | clearthemud.org</title>
<meta name="description" content="Candidate field and race dynamics for the {title}. {len(candidates)} candidates filed.">
<meta property="og:title" content="{title} &mdash; Race Overview">
<meta property="og:description" content="Candidate field and race dynamics for the {title}. {len(candidates)} candidates filed.">
<meta property="og:type" content="website">
<link rel="canonical" href="{SITE_URL}{race['url']}">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN &mdash; Approved for public sharing</div>

<nav class="dossier-nav">
  <a href="/">clearthemud.org</a>
  <span class="nav-sep">/</span>
  <a href="/states/">States</a>
  <span class="nav-sep">/</span>
  <a href="/states/{state_info['slug']}/">{state_info['name']}</a>
  <span class="nav-sep">/</span>
{county_crumb}  <span class="nav-current">{title}</span>
</nav>

<div class="header party-neutral">
  <div class="page">
    <h1>{title}</h1>
    <h2>2026 Primary Election</h2>
    <div class="header-meta">
      <span><span class="tlp-badge">TLP:GREEN</span></span>
      <span><strong>District:</strong> {district}</span>
      <span><strong>Candidates:</strong> {len(candidates)}</span>
      <span><strong>Office:</strong> {race['office']}</span>
    </div>
  </div>
</div>

<div class="page">

  <div class="section">
    <h2><span class="section-num">1</span> Candidate Field</h2>
    <div class="dossier-links">
{cards_html}
    </div>
  </div>

  <div class="footer">
    <strong>clearthemud.org</strong> &mdash; Verified public-record candidate intelligence
  </div>

</div>

<div class="classification-bar">TLP:GREEN &mdash; Approved for public sharing</div>

</body>
</html>
"""


def main():
    races = load_races()
    states_data = load_states_data()

    filter_states = [s.upper() for s in sys.argv[1:]] if len(sys.argv) > 1 else None

    if filter_states:
        target_races = [r for r in races if r["state_abbr"] in filter_states]
    else:
        target_races = races

    if not target_races:
        print("No races found for the specified states.")
        return

    total_pages = 0
    states_processed = set()

    for race in target_races:
        abbr = race["state_abbr"]
        state_info = states_data.get(abbr, {"name": abbr, "slug": abbr.lower()})
        race_dir = RACES_DIR / race["id"]
        race_dir.mkdir(parents=True, exist_ok=True)

        dossiers = {}
        for c in race["candidates"]:
            lastname = c["url"].rstrip("/").split("/")[-1]
            candidate_dir = race_dir / lastname
            candidate_dir.mkdir(exist_ok=True)

            dossier = find_dossier_json(race, lastname)
            dossiers[lastname] = dossier

            page_html = render_candidate_page(race, c, dossier, state_info)
            (candidate_dir / "index.html").write_text(page_html)
            total_pages += 1

        overview_html = render_race_overview(race, dossiers, state_info)
        (race_dir / "index.html").write_text(overview_html)
        total_pages += 1
        states_processed.add(abbr)
        print(f"  wrote {race['id']}/: {len(race['candidates'])} candidates + overview")

    print(f"\nDone: {total_pages} pages across {len(target_races)} races in {len(states_processed)} state(s)")


if __name__ == "__main__":
    main()
