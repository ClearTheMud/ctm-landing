#!/usr/bin/env python3
"""
ingest_sos_candidates.py — Ingest SOS-filed candidates not yet in races.json.

Reads WA Secretary of State CandidateList.csv, identifies candidates in 10 new
race categories not yet tracked, and adds them to races.json with proper race
entries and candidate records.

Race categories handled:
  1. WA Supreme Court (5 positions, 17 candidates)
  2. Court of Appeals (8 positions across 3 divisions)
  3. Superior Court (various counties)
  4. PUD Commissioner (30+ districts, wildly inconsistent naming)
  5. Port Commissioner (Bellingham, Pasco)
  6. Municipal Court (Seattle, Tacoma)
  7. KC District Court Electoral (5 electoral districts)
  8. County Council (King, Clark, Pierce)
  9. City Council (Seattle, Richland)
  10. District Court Judicial (named courts across multiple counties)

Usage:
    python3 tools/ingest_sos_candidates.py                # Ingest and write
    python3 tools/ingest_sos_candidates.py --dry-run      # Preview only
    python3 tools/ingest_sos_candidates.py --verbose       # Show details

C6S Data Engineering — Engagement 7
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Add tools/ to path for sibling imports
TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

from update_races import candidate_slug
from validate_candidates import normalize_name, name_similarity, normalize_party_csv

CSV_PATH = REPO_ROOT / "CandidateList.csv"
RACES_JSON = TOOLS_DIR / "data" / "races.json"

# WA election dates for 2026
PRIMARY_DATE = "August 4, 2026"
GENERAL_DATE = "November 3, 2026"


# ---------------------------------------------------------------------------
# PUD District Identification
# ---------------------------------------------------------------------------

# Known PUD district strings mapped to (pud_slug, pud_display_name)
# Built from manual analysis of SOS CandidateList.csv district field variations
PUD_DISTRICT_MAP = {
    # Explicit county/name in district
    "CLARK PUBLIC UTILITIES - COMM. DIST. #3": ("clark-pud", "Clark PUD"),
    "GRANT COUNTY PUD COMM DIST #3": ("grant-pud", "Grant County PUD"),
    "GRANT COUNTY PUD DIST #B": ("grant-pud", "Grant County PUD"),
    "SKAGIT COUNTY PUD COMMISSIONER DIST 1": ("skagit-pud", "Skagit County PUD"),
    "OK PUBLIC UTILITY DISTRICT 01": ("okanogan-pud", "Okanogan PUD"),
    # PUD with number identifiers
    "PUD #1": ("wahkiakum-pud", "Wahkiakum PUD"),
    "PUD #3": ("ferry-pud", "Ferry County PUD No. 3"),
    "PUD1-COMMISSIONER DISTRICT 2": ("stevens-pud-1", "Stevens County PUD No. 1"),
    "PUD 2 Commissioner District #1": ("pacific-pud-2", "Pacific County PUD No. 2"),
    "PUD 1 COMMISSIONER DIST 2": ("clallam-pud-1", "Clallam County PUD No. 1"),
    "PUD District 2": ("franklin-pud", "Franklin PUD"),
    "PUD No. 1 Commissioner District 1": ("whatcom-pud-1", "Whatcom County PUD No. 1"),
    "PUD COMMISSIONER DIST. 3": ("skamania-pud", "Skamania PUD"),
    "PUD Comm. Dist. 3": ("grays-harbor-pud", "Grays Harbor PUD"),
    "PUD Commissioner Dist 2": ("benton-pud", "Benton PUD"),
    "PUD Commissioner District 2": ("kitsap-pud", "Kitsap PUD"),
    "PUD DIST COMM #1": ("lewis-pud", "Lewis County PUD"),
    "PUD COMMISSIONER DISTRICT 1": ("snohomish-pud-1", "Snohomish County PUD No. 1"),
    "PUD COMMISSIONER DISTRICT NO. 1": ("thurston-pud", "Thurston PUD"),
    "PUD COMMISSIONER DISTRICT NO. 3": ("thurston-pud", "Thurston PUD"),
    # PUBLIC UTILITY DISTRICT variants
    "PUBLIC UTILITY DIST 2": ("douglas-pud-2", "Douglas County PUD No. 2"),
    "PUBLIC UTILITY DISTRICT #1": ("asotin-pud-1", "Asotin County PUD No. 1"),
    "PUBLIC UTILITY DISTRICT 1, 1": ("kittitas-pud-1", "Kittitas County PUD No. 1"),
    "PUBLIC UTILITY DISTRICT COMMISSIONER #3": ("klickitat-pud-1", "Klickitat PUD No. 1"),
    "PUBLIC UTILITY DISTRICT COMMISSIONER 1": ("chelan-pud", "Chelan County PUD"),
    "PUBLIC UTILITY DISTRICT COMMISSIONER B": ("chelan-pud", "Chelan County PUD"),
    "Public Comm District - 02": ("pend-oreille-pud-1", "Pend Oreille PUD No. 1"),
    "Public Utility Dist 1-2": ("mason-pud-1", "Mason County PUD No. 1"),
    "Public Utility Dist 3-2": ("mason-pud-3", "Mason County PUD No. 3"),
    "Public Utility District - Commissioner No. 2": ("jefferson-pud", "Jefferson County PUD"),
    "Public Utility District Commissioner District 1": ("cowlitz-pud", "Cowlitz PUD"),
    "PUBLIC UTILITY DISTRICT COMMISSIONER 1": ("chelan-pud", "Chelan County PUD"),
}


def identify_pud(district_str, race_str=None):
    """Identify PUD slug and display name from district string.

    Returns (pud_slug, pud_display_name) or (None, None) if unrecognized.
    """
    dist = district_str.strip()

    # Exact match first
    if dist in PUD_DISTRICT_MAP:
        return PUD_DISTRICT_MAP[dist]

    # Case-insensitive match
    dist_upper = dist.upper()
    for key, val in PUD_DISTRICT_MAP.items():
        if key.upper() == dist_upper:
            return val

    # Fallback: try to extract from known patterns
    # "SKAGIT COUNTY PUD..." -> skagit
    m = re.match(r'(\w+)\s+COUNTY\s+PUD', dist_upper)
    if m:
        county = m.group(1).capitalize()
        slug = f"{county.lower()}-pud"
        return (slug, f"{county} County PUD")

    # "CLARK PUBLIC UTILITIES..." -> clark
    m = re.match(r'(\w+)\s+PUBLIC\s+UTILIT', dist_upper)
    if m:
        county = m.group(1).capitalize()
        slug = f"{county.lower()}-pud"
        return (slug, f"{county} PUD")

    return (None, None)


def extract_pud_commissioner_district(district_str, race_str):
    """Extract the commissioner district number from PUD district/race fields.

    Returns district identifier string (number or letter like 'b').
    """
    race_upper = race_str.upper()

    # Best source: the race field usually has the actual commissioner position
    # "Commissioner #1", "Commissioner Pos. 2", "Commissioner District 2",
    # "PUBLIC UTILITY COMMISSIONER #01", "Commissioner, District No. 3"
    m = re.search(r'COMMISSIONER\s*[,.]?\s*(?:POS(?:ITION)?\.?\s*|DIST(?:RICT)?\.?\s*(?:NO\.?\s*)?|#)\s*(\w+)', race_upper)
    if m:
        val = m.group(1).lower().lstrip('0') or '0'
        return val

    # "Commissioner 1" (simple trailing number)
    m = re.search(r'COMMISSIONER\s+(\d+)', race_upper)
    if m:
        return m.group(1).lstrip('0') or '0'

    # "PUD Comm (3)" style
    m = re.search(r'COMM\s*\((\d+)\)', race_upper)
    if m:
        return m.group(1)

    # "Commissioner Dist #3" / "Commissioner Dist #B AL"
    m = re.search(r'DIST\s*#?\s*(\w+)', race_upper)
    if m:
        val = m.group(1).lower()
        if val not in ('al', 'of', 'the'):
            return val.lstrip('0') or '0'

    # Fallback: trailing number in race string
    m = re.search(r'(\d+)\s*$', race_str)
    if m:
        return m.group(1).lstrip('0') or '0'

    # Last resort: trailing number in district string
    m = re.search(r'(\d+)\s*$', district_str)
    if m:
        return m.group(1).lstrip('0') or '0'

    return "1"


# ---------------------------------------------------------------------------
# Position Number Extraction
# ---------------------------------------------------------------------------

def extract_position_number(race_str, district_str=None):
    """Extract position/judge number from race string.

    Handles: "Justice Position #01", "Judge Position 5", "Judge Position No. 2",
    "Judge Position #03", "Judge Pos. 1", "Council Pos. 4", "District Court No. 7",
    "Tacoma Municipal Court Pos. 1", "DISTRICT COURT JUDGE, DEPARTMENT NO. 1"
    """
    race = race_str.strip()

    # "Position #01" / "Position 5" / "Position No. 2" / "Pos. 1"
    m = re.search(r'(?:Position|Pos\.?)\s*(?:#|No\.?\s*)?\s*(\d+)', race, re.IGNORECASE)
    if m:
        return str(int(m.group(1)))  # strip leading zeros

    # "District Court No. 7" / "Court No. 3"
    m = re.search(r'(?:Court|District)\s+No\.?\s*(\d+)', race, re.IGNORECASE)
    if m:
        return str(int(m.group(1)))

    # "DEPARTMENT NO. 1" / "Dept 1" / "Dept. 2"
    m = re.search(r'(?:DEPARTMENT|Dept)\.?\s*(?:NO\.?\s*)?(\d+)', race, re.IGNORECASE)
    if m:
        return str(int(m.group(1)))

    # "District No. 5" (council)
    m = re.search(r'District\s*No\.?\s*(\d+)', race, re.IGNORECASE)
    if m:
        return str(int(m.group(1)))

    # Fallback: first number in race string
    m = re.search(r'(\d+)', race)
    if m:
        return str(int(m.group(1)))

    # Try district string
    if district_str:
        m = re.search(r'(\d+)', district_str)
        if m:
            return str(int(m.group(1)))

    return "1"


# ---------------------------------------------------------------------------
# Candidate Categorization
# ---------------------------------------------------------------------------

# Categories this script handles (the 10 new types)
CATEGORIES = {
    "supreme_court",
    "court_of_appeals",
    "superior_court",
    "pud_commissioner",
    "port_commissioner",
    "municipal_court",
    "kc_electoral_district_court",
    "county_council",
    "city_council",
    "district_court_judicial",
}


def categorize_candidate(race_str, district_str, district_type_str):
    """Categorize a CSV row into one of the 10 new race types.

    Returns category string or None if not one of the 10 target types.
    """
    dt = district_type_str.strip().upper()
    dist = district_str.strip().upper()
    race = race_str.strip().upper()

    # 1. Supreme Court
    if "SUPREME COURT" in dist:
        return "supreme_court"

    # 2. Court of Appeals
    if "COURT OF APPEALS" in dist:
        return "court_of_appeals"

    # 3. Superior Court (but not Clerk of Superior Court)
    if "SUPERIOR COURT" in dist and "CLERK" not in dist:
        return "superior_court"

    # 7. KC District Court Electoral (must check before generic district court)
    if "ELECTORAL DISTRICT" in dist:
        return "kc_electoral_district_court"

    # 6. Municipal Court
    if "MUNICIPAL COURT" in race:
        return "municipal_court"

    # 4. PUD Commissioner
    if dt == "PUBLIC UTILITY":
        return "pud_commissioner"

    # 5. Port Commissioner
    if dt == "PORT":
        return "port_commissioner"

    # 8. County Council
    if "COUNTY COUNCIL" in dist or "COUNTY COUNCILOR" in dist:
        return "county_council"

    # 9. City Council
    if dt == "CITY COUNCIL":
        return "city_council"
    if dt == "CITY/TOWN" and "COUNCIL" in race:
        # Distinguish from municipal court (already caught above)
        return "city_council"

    # 10. District Court Judicial (catch remaining judicial district courts)
    if dt == "JUDICIAL" and "DISTRICT COURT" in dist:
        return "district_court_judicial"
    if dt == "JUDICIAL" and "COURT DISTRICT" in dist:
        return "district_court_judicial"
    if dt == "JUDICIAL" and dist.startswith("COURT ") and "DISTRICT" in dist:
        return "district_court_judicial"
    # Named district courts: CASCADE, EVERETT, EVERGREEN, SOUTH, etc.
    if dt == "JUDICIAL" and any(k in dist for k in [
        "CASCADE", "EVERETT", "EVERGREEN", "SOUTH DISTRICT",
        "NORTH DISTRICT", "UPPER COUNTY", "LOWER COUNTY",
        "EAST DISTRICT", "WEST DISTRICT"
    ]):
        return "district_court_judicial"

    return None


# ---------------------------------------------------------------------------
# Race ID and Office Generation
# ---------------------------------------------------------------------------

def _slugify(s):
    """Convert a string to a URL-safe slug."""
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def generate_race_id(category, race_str, district_str, year=2026):
    """Generate a unique race ID from category and race/district fields."""
    race = race_str.strip()
    dist = district_str.strip()

    if category == "supreme_court":
        pos = extract_position_number(race)
        return f"wa-supreme-court-justice-pos-{pos}-{year}"

    if category == "court_of_appeals":
        # Parse "Court of Appeals, Division 2, District 1"
        m = re.search(r'Division\s*(\d+)', dist, re.IGNORECASE)
        div = m.group(1) if m else "1"
        m = re.search(r'District\s*(\d+)', dist, re.IGNORECASE)
        dd = m.group(1) if m else "1"
        pos = extract_position_number(race)
        return f"wa-appeals-div-{div}-dist-{dd}-pos-{pos}-{year}"

    if category == "superior_court":
        # Extract county from district: "Cowlitz Superior Court", "KING COUNTY SUPERIOR COURT"
        d = dist.strip()
        d_clean = re.sub(r'\s*COUNTY\s*', ' ', d, flags=re.IGNORECASE).strip()
        d_clean = re.sub(r'\s*Superior\s*Court\s*$', '', d_clean, flags=re.IGNORECASE).strip()
        # Handle multi-county: "Ferry, Pend Oreille, Stevens"
        county_slug = _slugify(d_clean)
        pos = extract_position_number(race)
        return f"wa-{county_slug}-superior-court-pos-{pos}-{year}"

    if category == "pud_commissioner":
        pud_slug, _ = identify_pud(dist, race)
        if not pud_slug:
            pud_slug = _slugify(dist)[:30]
        comm_dist = extract_pud_commissioner_district(dist, race)
        return f"wa-{pud_slug}-pud-commissioner-dist-{comm_dist}-{year}"

    if category == "port_commissioner":
        # "Port of Bellingham Commissioner District 4" or "PASCO PORT DISTRICT 3"
        m = re.search(r'Port\s+of\s+(\w+)', dist, re.IGNORECASE)
        if m:
            port_name = m.group(1).lower()
        else:
            m = re.search(r'(\w+)\s+PORT', dist, re.IGNORECASE)
            port_name = m.group(1).lower() if m else "unknown"
        pos = extract_position_number(race, dist)
        return f"wa-{port_name}-port-commissioner-dist-{pos}-{year}"

    if category == "municipal_court":
        # "City of Seattle" or "CITY OF TACOMA"
        m = re.search(r'CITY\s+OF\s+(\w+)', dist, re.IGNORECASE)
        city = m.group(1).lower() if m else "unknown"
        pos = extract_position_number(race)
        return f"wa-{city}-municipal-court-pos-{pos}-{year}"

    if category == "kc_electoral_district_court":
        # "NORTHEAST ELECTORAL DISTRICT" -> northeast
        m = re.match(r'(\w+)\s+ELECTORAL', dist, re.IGNORECASE)
        ed = m.group(1).lower() if m else "unknown"
        pos = extract_position_number(race)
        return f"wa-king-electoral-{ed}-pos-{pos}-{year}"

    if category == "county_council":
        # Determine county from district/race patterns
        race_upper = race.upper()
        dist_upper = dist.upper()
        if "METROPOLITAN" in race_upper or "METROPOLITAN" in dist_upper:
            county = "king"
        elif "COUNCILOR" in dist_upper:
            county = "clark"
        else:
            county = "pierce"
        pos = extract_position_number(race, dist)
        return f"wa-{county}-county-council-dist-{pos}-{year}"

    if category == "city_council":
        # "City Of Richland" or "SEATTLE CITY COUNCIL DISTRICT 5"
        if "SEATTLE" in dist.upper():
            city = "seattle"
        else:
            m = re.search(r'CITY\s+OF\s+(\w+)', dist, re.IGNORECASE)
            city = m.group(1).lower() if m else "unknown"
        pos = extract_position_number(race, dist)
        return f"wa-{city}-city-council-pos-{pos}-{year}"

    if category == "district_court_judicial":
        d = dist.strip().upper()
        race_up = race.upper()
        # Named courts (most specific first)
        if "CASCADE" in d:
            court = "cascade"
        elif "EVERETT" in d:
            court = "everett"
        elif "EVERGREEN" in d:
            court = "evergreen"
        elif "SOUTH DISTRICT COURT" in d:
            court = "snohomish-south"
        elif "Court - South" in dist:
            court = "thurston-south"
        elif "NORTH DISTRICT" in d:
            court = "snohomish-north"
        elif "Court - North" in dist:
            court = "thurston-north"
        elif "UPPER COUNTY" in d:
            court = "upper-county"
        elif "LOWER COUNTY" in d:
            court = "lower-county"
        elif "EAST DISTRICT" in d:
            court = "klickitat-east"
        elif "WEST DISTRICT" in d:
            court = "klickitat-west"
        elif "COURT DISTRICT 1" in d:
            court = "whatcom-1"
        elif "COURT DISTRICT 2" in d:
            court = "whatcom-2"
        elif d == "COURT DISTRICT":
            court = "columbia"
        elif d == "DISTRICT COURT JUDGES":
            # King County uses "DISTRICT COURT JUDGES" as district
            court = "king"
        elif d == "DISTRICT COURT JUDGE":
            # Benton County uses "DISTRICT COURT JUDGE" as district
            court = "benton"
        elif d == "DISTRICT COURT":
            # Disambiguate by race field patterns:
            # Snohomish: "District Court Judge, Dept 1/2"
            # Pierce: "District Court No. 1/2/..."
            # Spokane: "Judge Position No. 1" / "Judge Position 1"
            # Thurston: "District Court Judge Department 1/2/3/4"
            if "DEPT" in race_up and "DEPARTMENT" not in race_up:
                court = "snohomish"
            elif "DEPARTMENT" in race_up:
                court = "thurston"
            elif "NO." in race_up and "POSITION" not in race_up:
                court = "pierce"
            elif "POSITION" in race_up:
                court = "spokane"
            else:
                court = "district"
        else:
            court = _slugify(re.sub(r'DISTRICT COURT', '', d).strip()) or "district"

        pos = extract_position_number(race, dist)
        return f"wa-{court}-district-court-pos-{pos}-{year}"

    return None


def generate_office_name(category, race_str, district_str):
    """Generate a human-readable office display name."""
    race = race_str.strip()
    dist = district_str.strip()

    if category == "supreme_court":
        pos = extract_position_number(race)
        return f"WA Supreme Court Justice Pos. {pos}"

    if category == "court_of_appeals":
        m = re.search(r'Division\s*(\d+)', dist, re.IGNORECASE)
        div = m.group(1) if m else "1"
        m = re.search(r'District\s*(\d+)', dist, re.IGNORECASE)
        dd = m.group(1) if m else "1"
        pos = extract_position_number(race)
        return f"Court of Appeals Div. {div} Dist. {dd} Pos. {pos}"

    if category == "superior_court":
        d_clean = re.sub(r'\s*COUNTY\s*', ' ', dist, flags=re.IGNORECASE).strip()
        d_clean = re.sub(r'\s*Superior\s*Court\s*$', '', d_clean, flags=re.IGNORECASE).strip()
        pos = extract_position_number(race)
        return f"{d_clean.title()} Superior Court Pos. {pos}"

    if category == "pud_commissioner":
        _, pud_name = identify_pud(dist, race)
        if not pud_name:
            pud_name = dist.title()
        comm_dist = extract_pud_commissioner_district(dist, race)
        return f"{pud_name} Commissioner Dist. {comm_dist}"

    if category == "port_commissioner":
        m = re.search(r'Port\s+of\s+(\w+)', dist, re.IGNORECASE)
        if m:
            port_name = f"Port of {m.group(1).title()}"
        else:
            m = re.search(r'(\w+)\s+PORT', dist, re.IGNORECASE)
            port_name = f"{m.group(1).title()} Port" if m else "Port"
        pos = extract_position_number(race, dist)
        return f"{port_name} Commissioner Dist. {pos}"

    if category == "municipal_court":
        m = re.search(r'CITY\s+OF\s+(\w+)', dist, re.IGNORECASE)
        city = m.group(1).title() if m else "Unknown"
        pos = extract_position_number(race)
        return f"{city} Municipal Court Pos. {pos}"

    if category == "kc_electoral_district_court":
        m = re.match(r'(\w+)\s+ELECTORAL', dist, re.IGNORECASE)
        ed = m.group(1).title() if m else "Unknown"
        pos = extract_position_number(race)
        return f"King County {ed} Electoral Dist. Court Pos. {pos}"

    if category == "county_council":
        race_upper = race.upper()
        dist_upper = dist.upper()
        if "METROPOLITAN" in race_upper or "METROPOLITAN" in dist_upper:
            county = "King County"
        elif "COUNCILOR" in dist_upper:
            county = "Clark County"
        else:
            county = "Pierce County"
        pos = extract_position_number(race, dist)
        return f"{county} Council Dist. {pos}"

    if category == "city_council":
        if "SEATTLE" in dist.upper():
            city = "Seattle"
        else:
            m = re.search(r'CITY\s+OF\s+(\w+)', dist, re.IGNORECASE)
            city = m.group(1).title() if m else "Unknown"
        pos = extract_position_number(race, dist)
        return f"{city} City Council Pos. {pos}"

    if category == "district_court_judicial":
        race_id = generate_race_id(category, race, dist)
        # Extract court name from race_id
        m = re.match(r'wa-(.+)-district-court-pos-(\d+)-\d+', race_id)
        if m:
            court_slug = m.group(1)
            pos = m.group(2)
            # Pretty-print known court names
            court_names = {
                "cascade": "Cascade",
                "everett": "Everett",
                "evergreen": "Evergreen",
                "snohomish-south": "Snohomish South",
                "snohomish-north": "Snohomish North",
                "snohomish": "Snohomish",
                "thurston-south": "Thurston South",
                "thurston-north": "Thurston North",
                "thurston": "Thurston",
                "spokane": "Spokane",
                "pierce": "Pierce",
                "king": "King County",
                "benton": "Benton",
                "whatcom-1": "Whatcom Dist. 1",
                "whatcom-2": "Whatcom Dist. 2",
                "columbia": "Columbia County",
                "upper-county": "Upper County",
                "lower-county": "Lower County",
                "klickitat-east": "Klickitat East",
                "klickitat-west": "Klickitat West",
            }
            court_name = court_names.get(court_slug, court_slug.replace('-', ' ').title())
            return f"{court_name} District Court Pos. {pos}"
        return "District Court Judge"

    return race


def generate_race_title(category, office_name, year=2026):
    """Generate a title for the race entry."""
    return f"{year} WA {office_name}"


# ---------------------------------------------------------------------------
# Race Entry Builder
# ---------------------------------------------------------------------------

def build_race_entry(category, race_id, office_name, year, candidates):
    """Build a complete race entry dict for races.json."""
    race_url = f"/races/{race_id}/"

    # Determine level
    if category in ("supreme_court", "court_of_appeals"):
        level = "statewide"
    elif category in ("superior_court", "district_court_judicial",
                       "kc_electoral_district_court", "county_council"):
        level = "county"
    elif category in ("pud_commissioner", "port_commissioner"):
        level = "special_district"
    elif category in ("municipal_court", "city_council"):
        level = "municipal"
    else:
        level = "other"

    entry = {
        "id": race_id,
        "state_abbr": "WA",
        "office": office_name,
        "level": level,
        "year": year,
        "title": generate_race_title(category, office_name, year),
        "status": "draft",
        "url": race_url,
        "primary_date": PRIMARY_DATE,
        "general_date": GENERAL_DATE,
        "candidates": [],
    }

    for cand in candidates:
        slug = candidate_slug(cand["name"])
        party = normalize_party_csv(cand.get("party_raw", ""))
        entry["candidates"].append({
            "name": cand["name"],
            "party": party,
            "role": "Filed",
            "slug": slug,
            "status": cand.get("election_status", "In Primary"),
            "url": f"{race_url}{slug}/",
        })

    return entry


# ---------------------------------------------------------------------------
# Duplicate Detection
# ---------------------------------------------------------------------------

def is_duplicate(candidate_name, race_id, existing_races):
    """Check if a candidate is already in a specific race in races.json."""
    for race in existing_races:
        if race["id"] != race_id:
            continue
        for cand in race.get("candidates", []):
            sim = name_similarity(candidate_name, cand["name"])
            if sim >= 0.85:
                return True
    return False


# ---------------------------------------------------------------------------
# Main Ingestion Logic
# ---------------------------------------------------------------------------

def load_csv():
    """Load active candidates from SOS CSV."""
    candidates = []
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get('Status', '').strip().upper()
            if status == 'WITHDRAWN':
                continue
            candidates.append(row)
    return candidates


def load_races_json():
    """Load races.json data."""
    with open(RACES_JSON) as f:
        return json.load(f)


def save_races_json(data):
    """Write updated races.json."""
    with open(RACES_JSON, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def ingest(dry_run=False, verbose=False):
    """Main ingestion routine.

    Returns dict with summary statistics.
    """
    csv_rows = load_csv()
    data = load_races_json()
    existing_races = data.get("races", [])
    existing_ids = {r["id"] for r in existing_races}

    # Step 1: Categorize all CSV candidates into our 10 target types
    categorized = defaultdict(list)
    skipped_count = 0
    unrecognized = []

    for row in csv_rows:
        cat = categorize_candidate(
            row["Race"], row["District"], row["District Type"]
        )
        if cat is None:
            continue  # Not one of our 10 target categories
        categorized[cat].append(row)

    if verbose:
        print("\n--- Categorization Summary ---")
        for cat in sorted(categorized.keys()):
            print(f"  {cat}: {len(categorized[cat])} candidates")

    # Step 2: Group candidates by race ID within each category
    race_groups = defaultdict(list)  # race_id -> list of candidate rows
    race_meta = {}  # race_id -> (category, office_name, first_row)

    for cat, rows in categorized.items():
        for row in rows:
            race_id = generate_race_id(cat, row["Race"], row["District"])
            if race_id is None:
                skipped_count += 1
                continue

            office = generate_office_name(cat, row["Race"], row["District"])

            # Check if candidate already exists in this race
            if race_id in existing_ids:
                if is_duplicate(row["Name"], race_id, existing_races):
                    skipped_count += 1
                    continue

            race_groups[race_id].append({
                "name": row["Name"].strip(),
                "party_raw": row.get("Party Preference", "").strip(),
                "election_status": row.get("Election Status", "In Primary").strip(),
            })

            if race_id not in race_meta:
                race_meta[race_id] = (cat, office, row)

    # Step 3: Build race entries
    new_races = []
    updated_races = []
    new_candidates_total = 0

    for race_id, candidates in sorted(race_groups.items()):
        cat, office, _ = race_meta[race_id]

        if race_id in existing_ids:
            # Add candidates to existing race
            existing_race = next(r for r in existing_races if r["id"] == race_id)
            new_cands = []
            for cand in candidates:
                if not is_duplicate(cand["name"], race_id, existing_races):
                    slug = candidate_slug(cand["name"])
                    party = normalize_party_csv(cand.get("party_raw", ""))
                    new_cands.append({
                        "name": cand["name"],
                        "party": party,
                        "role": "Filed",
                        "slug": slug,
                        "status": cand.get("election_status", "In Primary"),
                        "url": f"{existing_race['url']}{slug}/",
                    })
            if new_cands:
                updated_races.append((race_id, new_cands))
                new_candidates_total += len(new_cands)
        else:
            # Create new race
            entry = build_race_entry(cat, race_id, office, 2026, candidates)
            new_races.append(entry)
            new_candidates_total += len(candidates)

    # Step 4: Apply changes
    if not dry_run:
        # Add new races
        for race_entry in new_races:
            data["races"].append(race_entry)

        # Update existing races with new candidates
        for race_id, new_cands in updated_races:
            for race in data["races"]:
                if race["id"] == race_id:
                    race["candidates"].extend(new_cands)
                    break

        save_races_json(data)

    # Step 5: Summary
    summary = {
        "csv_total": len(csv_rows),
        "categorized": sum(len(v) for v in categorized.items()),
        "new_races": len(new_races),
        "updated_races": len(updated_races),
        "new_candidates": new_candidates_total,
        "skipped_duplicates": skipped_count,
        "by_category": {},
    }

    # Per-category breakdown
    for cat in sorted(CATEGORIES):
        cat_race_ids = [
            rid for rid, (c, _, _) in race_meta.items() if c == cat
        ]
        cat_cands = sum(
            len(race_groups[rid]) for rid in cat_race_ids if rid in race_groups
        )
        cat_new = sum(1 for r in new_races if r["id"] in set(cat_race_ids))
        summary["by_category"][cat] = {
            "races": len(cat_race_ids),
            "candidates": cat_cands,
            "new_races": cat_new,
        }

    return summary, new_races, updated_races


def print_summary(summary, new_races, updated_races, dry_run=False):
    """Print human-readable summary."""
    mode = "DRY RUN" if dry_run else "INGESTED"
    print(f"\n{'='*60}")
    print(f"  SOS Candidate Ingestion — {mode}")
    print(f"{'='*60}")
    print(f"  CSV candidates scanned:  {summary['csv_total']}")
    print(f"  New races created:       {summary['new_races']}")
    print(f"  Existing races updated:  {summary['updated_races']}")
    print(f"  New candidates added:    {summary['new_candidates']}")
    print(f"  Skipped (duplicates):    {summary['skipped_duplicates']}")
    print()

    print("  By Category:")
    print(f"  {'Category':<35} {'Races':>6} {'Cands':>6} {'New':>5}")
    print(f"  {'-'*35} {'-'*6} {'-'*6} {'-'*5}")
    for cat, info in sorted(summary["by_category"].items()):
        if info["candidates"] > 0:
            print(f"  {cat:<35} {info['races']:>6} {info['candidates']:>6} {info['new_races']:>5}")
    print()

    if new_races:
        print("  New Races:")
        for race in sorted(new_races, key=lambda r: r["id"]):
            cands = ", ".join(c["name"] for c in race["candidates"])
            print(f"    {race['id']}")
            print(f"      Office: {race['office']}")
            print(f"      Candidates ({len(race['candidates'])}): {cands}")
        print()

    if updated_races:
        print("  Updated Races (new candidates added):")
        for race_id, cands in sorted(updated_races):
            names = ", ".join(c["name"] for c in cands)
            print(f"    {race_id}: +{len(cands)} ({names})")
        print()

    if not dry_run:
        print(f"  races.json updated at: {RACES_JSON}")
    else:
        print("  No changes written (dry run).")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ingest SOS-filed candidates into races.json"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without writing to races.json"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed categorization output"
    )
    args = parser.parse_args()

    if not CSV_PATH.exists():
        print(f"Error: CSV not found at {CSV_PATH}")
        sys.exit(1)
    if not RACES_JSON.exists():
        print(f"Error: races.json not found at {RACES_JSON}")
        sys.exit(1)

    summary, new_races, updated_races = ingest(
        dry_run=args.dry_run, verbose=args.verbose
    )
    print_summary(summary, new_races, updated_races, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
