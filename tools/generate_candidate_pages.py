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

import html as _html
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


def load_curated_race_ids():
    """Race-ids whose pages are hand-authored deep-dives and must NOT be
    overwritten by this bulk generator. See tools/data/curated_races.json."""
    path = DATA_DIR / "curated_races.json"
    if not path.exists():
        return set()
    with open(path) as f:
        return set(json.load(f).get("curated_race_ids", []))


def _county_office_to_filename(office):
    """Convert county office name to dossier filename component."""
    import re
    s = office.lower().strip()
    s = re.sub(r"pos\.\s*", "position_", s)
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s


# Markup that only a deep-dive dossier emits. clearthemud's converter writes
# these; this bulk generator never does, so their presence identifies a page
# that must not be overwritten with a T1 stub (ADO #1969).
_DEEP_DIVE_MARKERS = (
    'content="Deep-dive OSINT dossier',
    "<h1>Candidate Dossier:",
    '<meta property="og:type" content="article">',
)


def is_deep_dive_page(path):
    """True when `path` already holds a deep-dive dossier.

    curated_races.json was the only guard and it is maintained by hand, so it
    drifted: a 2026-07-27 run overwrote 509 deep-dive dossiers with stubs
    because nobody had registered those races. The page's own markup cannot
    drift, so it is checked directly.

    Unreadable paths are reported as deep-dives. If we cannot tell what a file
    is, refusing to overwrite loses a rebuild; overwriting loses research.
    """
    try:
        if not path.exists():
            return False          # nothing there yet: generate normally
        html = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return True               # exists but unreadable: refuse to clobber
    return any(marker in html for marker in _DEEP_DIVE_MARKERS)


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


# Byte-identical to the caveat in clearthemud's convert_to_ctm_landing.py. The
# SOS export has no identity key, so rows are matched on printed name alone;
# a page that shows them without saying so asserts an identity nobody verified.
# Keep the two copies in sync, or the site explains one limitation two ways.
SOS_NAME_MATCH_CAVEAT = (
    "Rows marked WA SOS come from official Washington Secretary of State "
    "election results and are <strong>matched by name</strong>, not by a "
    "verified identity. A candidate who shares a name with another "
    "person may show results that are not theirs. "
    '<a href="mailto:contact@clearthemud.org">Tell us</a> if you spot one.'
)


def render_election_history(history, section_num):
    """Election History section for a T1 stub page, or "" when there is none.

    Mirrors the deep-dive renderer: a Source column per row so a reader can
    tell researched history from a name match, and the caveat only when at
    least one row actually came from the SOS export (ADO #1969).
    """
    if not history:
        return ""

    rows = []
    for entry in history:
        src = entry.get("source")
        label = {"wa-sos": "WA SOS", "research": "Research"}.get(src, "Research")
        rows.append(
            f'        <tr><td>{_html.escape(str(entry.get("year", "")))}</td>'
            f'<td>{_html.escape(str(entry.get("race", "")))}</td>'
            f'<td>{_html.escape(str(entry.get("result", "")))}</td>'
            f'<td>{_html.escape(label)}</td></tr>'
        )

    caveat = ""
    if any(e.get("source") == "wa-sos" for e in history):
        caveat = (
            '\n      <p style="font-size:13px; color:var(--gray-dark);">'
            f'{SOS_NAME_MATCH_CAVEAT}</p>'
        )

    body = "\n".join(rows)
    return f"""
    <div class="section">
      <h2><span class="section-num">{section_num}</span> Election History</h2>
      <table>
        <thead><tr><th>Year</th><th>Race</th><th>Result</th><th>Source</th></tr></thead>
        <tbody>
{body}
        </tbody>
      </table>{caveat}
    </div>"""


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
    # A withdrawn candidate is not on the ballot, so nothing on their own page
    # may present them as running. They are never removed: a reader who
    # remembers the name deserves to learn what happened (ADO #2014, #1992).
    withdrawn = bool(candidate.get("withdrawn"))
    status_display = "Withdrawn" if withdrawn else role
    district = _district_label(race)
    # Omit the field entirely when there is no district. A race that belongs
    # to no district rendered as a bare "District:" label (ADO #1996).
    district_meta = (f'      <span><strong>District:</strong> {district}</span>\n'
                     if str(district).strip() else "")
    race_title = race["title"]
    race_url = race["url"]
    is_county = race.get("level") == "county"
    county_crumb = ""
    if is_county:
        county_slug = race.get("county_slug", "")
        county_name = race.get("county", "")
        county_crumb = f'  <a href="/states/{state_info["slug"]}/{county_slug}/">{county_name} County</a>\n  <span class="nav-sep">/</span>\n'

    if withdrawn:
        page_desc = (f"Candidate record for {name} ({party_full}), who filed in the "
                     f"{race_title} and withdrew from the race.")
        bluf = (f"{name} filed as a {party_full} candidate in the {race_title} and "
                f"withdrew from the race. They are not on the ballot.")
        withdrawn_banner = (
            '  <div class="withdrawn-notice" role="note">\n'
            f'    <p><strong>WITHDRAWN.</strong> {name} withdrew from the race and is not on '
            f'the ballot for the {race_title}. The record below is kept for reference and '
            'describes the period before the withdrawal.</p>\n'
            '  </div>\n')
        finance_scope = ('\n      <p class="finance-scope">Figures below were reported before '
                         'withdrawing from the race and are not current fundraising totals.</p>')
    else:
        page_desc = f"Verified candidate dossier for {name} ({party_full}) running in the {race_title}."
        bluf = f"{name} is a {party_full} {role.lower()} in the {race_title}."
        withdrawn_banner = ""
        finance_scope = ""

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

    # Only when there are actually figures to scope. A "no filings found"
    # section has nothing to qualify (ADO #2014).
    if finance_scope and (has_state_finance or has_fec_finance):
        finance_section = finance_section.replace(
            "Campaign Finance</h2>", "Campaign Finance</h2>" + finance_scope)

    # Election History sits between finance and sourcing, and only when the
    # candidate has any. Source Verification shifts to 4 in that case so the
    # numbering never gaps or repeats (ADO #1969).
    election_history = dossier.get("election_history", []) if dossier else []
    election_history_section = render_election_history(election_history, 3)
    source_verification_num = 4 if election_history_section else 3

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
<title>{name}, {race_title} | clearthemud.org</title>
<meta name="description" content="{page_desc}">
<meta property="og:title" content="{name}, {race_title}">
<meta property="og:description" content="{page_desc}">
<meta property="og:type" content="website">
<link rel="canonical" href="{SITE_URL}{candidate['url']}">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>

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
      <span><strong>Status:</strong> {status_display}</span>
{district_meta}    </div>
  </div>
</div>

<div class="page">

{withdrawn_banner}    <div class="section">
      <h2><span class="section-num">1</span> Candidate Overview</h2>
      <div class="bluf">
        <h3>BLUF, Bottom Line Up Front</h3>
        <p>{bluf}</p>
      </div>
    </div>
{finance_section}
{election_history_section}
    <div class="section">
      <h2><span class="section-num">{source_verification_num}</span> Source Verification</h2>
      <div class="finding">
        <dl>
          <dt>Data Source</dt><dd>clearthemud.org data pipeline</dd>
          <dt>Collection Date</dt><dd>{meta.get("collected_date", "2026-05-09")}</dd>
          <dt>Party Verification</dt><dd>{source_tier}, {meta.get("party", {}).get("confidence", "unverified")}</dd>
        </dl>
      </div>
    </div>

  <div class="footer">
    <strong>clearthemud.org</strong>, Verified public-record candidate intelligence<br>
    <a href="mailto:contact@clearthemud.org">contact@clearthemud.org</a>
  </div>

</div>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>

</body>
</html>
"""


def render_race_overview(race, dossiers, state_info):
    title = race["title"]
    district = _district_label(race)
    # Omit the field entirely when there is no district. A race that belongs
    # to no district rendered as a bare "District:" label (ADO #1996).
    district_meta = (f'      <span><strong>District:</strong> {district}</span>\n'
                     if str(district).strip() else "")
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

        # A withdrawn candidate is not on the ballot, so the field must not
        # show them as running. They stay listed rather than being removed: a
        # reader who remembers the name deserves to learn what happened rather
        # than find nothing (ADO #1992).
        if c.get("withdrawn"):
            status_class, status_text = "status-withdrawn", "WITHDRAWN"
            link_class, detail = "dossier-link withdrawn", "Withdrew from the race"
        else:
            status_class = "status-incumbent" if role.lower() == "incumbent" else "status-active"
            status_text, link_class, detail = role.upper(), "dossier-link", f"Raised: {raised}"

        candidate_cards.append(f"""      <a href="{c['url']}" class="{link_class}">
        <h4>{c['name']} ({party_label})</h4>
        <p><span class="{status_class}">{status_text}</span>, {detail}</p>
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
<title>{title}, Race Overview | clearthemud.org</title>
<meta name="description" content="Candidate field and race dynamics for the {title}. {len(candidates)} candidates filed.">
<meta property="og:title" content="{title}, Race Overview">
<meta property="og:description" content="Candidate field and race dynamics for the {title}. {len(candidates)} candidates filed.">
<meta property="og:type" content="website">
<link rel="canonical" href="{SITE_URL}{race['url']}">
<link rel="stylesheet" href="/css/dossier.css">
</head>
<body>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>

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
{district_meta}      <span><strong>Candidates:</strong> {len(candidates)}</span>
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
    <strong>clearthemud.org</strong>, Verified public-record candidate intelligence<br>
    <a href="mailto:contact@clearthemud.org">contact@clearthemud.org</a>
  </div>

</div>

<div class="classification-bar">TLP:GREEN, Approved for public sharing</div>

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

    # Preserve hand-authored deep-dives: never overwrite curated pages with
    # bulk T1 stubs. See tools/data/curated_races.json.
    curated_ids = load_curated_race_ids()
    skipped = [r["id"] for r in target_races if r["id"] in curated_ids]
    target_races = [r for r in target_races if r["id"] not in curated_ids]
    if skipped:
        print(f"Preserving {len(skipped)} curated deep-dive race(s) (not regenerated):")
        for rid in sorted(skipped):
            print(f"  - {rid}")

    total_pages = 0
    states_processed = set()
    preserved_deep_dives = []

    for race in target_races:
        abbr = race["state_abbr"]
        state_info = states_data.get(abbr, {"name": abbr, "slug": abbr.lower()})
        race_dir = RACES_DIR / race["id"]
        race_dir.mkdir(parents=True, exist_ok=True)

        dossiers = {}
        preserved_here = 0
        for c in race["candidates"]:
            lastname = c["url"].rstrip("/").split("/")[-1]
            candidate_dir = race_dir / lastname
            candidate_dir.mkdir(exist_ok=True)

            dossier = find_dossier_json(race, lastname)
            dossiers[lastname] = dossier

            target = candidate_dir / "index.html"
            # A deep-dive dossier is researched output; a stub is derived from
            # the roster. Never trade the first for the second (ADO #1969).
            if is_deep_dive_page(target):
                preserved_deep_dives.append(f"{race['id']}/{lastname}")
                preserved_here += 1
                continue

            page_html = render_candidate_page(race, c, dossier, state_info)
            target.write_text(page_html)
            total_pages += 1

        # The overview lists the field, so it is regenerated even when some of
        # its candidates are preserved; it carries no researched content.
        overview_html = render_race_overview(race, dossiers, state_info)
        (race_dir / "index.html").write_text(overview_html)
        total_pages += 1
        states_processed.add(abbr)
        note = f", {preserved_here} deep-dive preserved" if preserved_here else ""
        print(f"  wrote {race['id']}/: "
              f"{len(race['candidates']) - preserved_here} candidates + overview{note}")

    print(f"\nDone: {total_pages} pages across {len(target_races)} races in {len(states_processed)} state(s)")
    if preserved_deep_dives:
        print(f"Preserved {len(preserved_deep_dives)} existing deep-dive page(s), "
              f"not overwritten with stubs.")


if __name__ == "__main__":
    main()
