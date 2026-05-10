#!/usr/bin/env python3
"""Build county_races.json from WA SOS CandidateList.csv.

Reads CandidateList.csv, maps candidates to counties via city-to-county
lookup, and outputs tools/data/county_races.json.

Usage:
    python3 tools/build_county_races.py [path/to/CandidateList.csv]
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
DATA_DIR = TOOLS_DIR / "data"
DEFAULT_CSV = Path.home() / "Local" / "Projects" / "github" / "clearthemud" / "CandidateList.csv"

COUNTY_DISTRICT_TYPES = {"Countywide", "COUNTY", "Commissioner", "COMMISSIONER"}

SUPPLEMENTAL_CITY_COUNTY = {
    "CAMANO ISLAND": "Island",
    "CHIMACUM": "Jefferson",
    "ELTOPIA": "Franklin",
    "FREELAND": "Island",
    "FRIDAY HARBOR": "San Juan",
    "GIG HARBOR": "Pierce",
    "LOPEZ ISLAND": "San Juan",
    "NEWMAN LAKE": "Spokane",
    "NINE MILE FALLS": "Spokane",
    "ORONDO": "Douglas",
    "OYSTERVILLE": "Pacific",
    "PESHASTIN": "Chelan",
    "PORT HADLOCK": "Jefferson",
    "RICHALND": "Benton",
    "SALKUM": "Lewis",
    "SHAW ISLAND": "San Juan",
    "SILVER CREEK": "Lewis",
    "SKAMOKAWA": "Wahkiakum",
    "TOLEO": "Lewis",
    "UNDERWOOD": "Skamania",
    "USK": "Pend Oreille",
    "SPOKANE VALLEY": "Spokane",
    "UNIVERSITY PLACE": "Pierce",
    "WALLA WALLA": "Walla Walla",
    "COLLEGE PLACE": "Walla Walla",
    "OCEAN SHORES": "Grays Harbor",
    "OCEAN PARK": "Pacific",
    "BATTLE GROUND": "Clark",
    "BONNEY LAKE": "Pierce",
    "DEER PARK": "Spokane",
    "EAST WENATCHEE": "Douglas",
    "FEDERAL WAY": "King",
    "FOX ISLAND": "Pierce",
    "LAKE FOREST PARK": "King",
    "LAKE STEVENS": "Snohomish",
    "LIBERTY LAKE": "Spokane",
    "MAPLE VALLEY": "King",
    "MERCER ISLAND": "King",
    "MOUNT VERNON": "Skagit",
    "OAK HARBOR": "Island",
    "PORT ANGELES": "Clallam",
    "PORT ORCHARD": "Kitsap",
    "PORT TOWNSEND": "Jefferson",
    "SAN JUAN ISLAND": "San Juan",
    "VASHON": "King",
    "VASHON ISLAND": "King",
    "WHITE SALMON": "Klickitat",
    "BAINBRIDGE ISLAND": "Kitsap",
}


def build_city_county_map():
    """Build city-name to county-name mapping from places.json + supplements."""
    with open(DATA_DIR / "places.json") as f:
        places = json.load(f)
    with open(DATA_DIR / "counties.json") as f:
        counties = json.load(f)

    slug_to_name = {c["slug"]: c["name"] for c in counties["WA"]}
    city_county = dict(SUPPLEMENTAL_CITY_COUNTY)

    for county_slug, place_list in places["WA"].items():
        county_name = slug_to_name.get(county_slug)
        if not county_name:
            continue
        for p in place_list:
            city_county[p["name"].upper()] = county_name

    return city_county


def extract_city(address):
    """Extract city from WA mailing address."""
    m = re.search(r",\s*([A-Za-z][A-Za-z\s.()-]+),\s*WA", address)
    return m.group(1).strip().upper() if m else None


def normalize_office(race_name, district_type):
    """Normalize race name to a consistent office title."""
    race_name = race_name.strip()
    if district_type in ("Commissioner", "COMMISSIONER"):
        m = re.search(r"(?:District\s*(?:No\.?\s*)?)?(\d+)", race_name)
        if m:
            return f"Commissioner District {m.group(1)}"
        return race_name.title()
    return race_name.title()


def make_slug(name):
    """Convert candidate name to URL slug."""
    slug = name.lower().strip()
    slug = re.sub(r'["\']', '', slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def make_office_slug(office):
    """Convert office title to URL-safe slug."""
    slug = office.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def build_county_races(csv_path):
    """Parse CSV and build county race mapping."""
    city_county = build_city_county_map()

    with open(DATA_DIR / "counties.json") as f:
        counties_data = json.load(f)
    name_to_slug = {c["name"]: c["slug"] for c in counties_data["WA"]}

    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    county_data = defaultdict(lambda: defaultdict(list))
    unmatched = []

    for row in rows:
        dt = row["District Type"]
        if dt not in COUNTY_DISTRICT_TYPES:
            continue

        city = extract_city(row["Mailing Address"])
        if not city:
            unmatched.append(row)
            continue

        county_name = city_county.get(city)
        if not county_name:
            unmatched.append(row)
            continue

        office = normalize_office(row["Race"], dt)
        county_data[county_name][office].append({
            "name": row["Name"].strip(),
            "party": row["Party Preference"].strip() or "Nonpartisan",
            "filing_date": row["Filing Date"].strip(),
            "election_status": row["Election Status"].strip(),
            "status": "Active" if row["Status"].strip() == "Active" else row["Status"].strip(),
        })

    result = {}
    for county_info in counties_data["WA"]:
        county_name = county_info["name"]
        county_slug = county_info["slug"]
        races = []
        if county_name in county_data:
            for office, candidates in sorted(county_data[county_name].items()):
                races.append({
                    "office": office,
                    "candidates": candidates,
                })
        result[county_slug] = {
            "name": county_name,
            "full_name": county_info["full_name"],
            "fips": county_info["fips"],
            "races": races,
        }

    if unmatched:
        print(f"Warning: {len(unmatched)} candidates could not be mapped to a county:",
              file=sys.stderr)
        for r in unmatched:
            city = extract_city(r["Mailing Address"])
            print(f"  {r['Name']} ({city}) — {r['Race']}", file=sys.stderr)

    return {"WA": result}


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not csv_path.exists():
        print(f"Error: {csv_path} not found", file=sys.stderr)
        sys.exit(1)

    county_races = build_county_races(csv_path)
    out_path = DATA_DIR / "county_races.json"
    with open(out_path, "w") as f:
        json.dump(county_races, f, indent=2, ensure_ascii=False)

    wa = county_races["WA"]
    total_races = sum(len(c["races"]) for c in wa.values())
    total_candidates = sum(
        len(cand)
        for c in wa.values()
        for r in c["races"]
        for cand in [r["candidates"]]
    )
    counties_with_races = sum(1 for c in wa.values() if c["races"])

    print(f"Wrote {out_path}")
    print(f"  {counties_with_races}/39 counties with races")
    print(f"  {total_races} races, {total_candidates} candidates")


if __name__ == "__main__":
    main()
