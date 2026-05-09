#!/usr/bin/env python3
"""
update_races.py — Quick CLI to add races/candidates to the map data and regenerate pages.

Usage:
    python3 tools/update_races.py add-race
    python3 tools/update_races.py add-candidate <race-id>
    python3 tools/update_races.py list
    python3 tools/update_races.py regenerate

After any change, this script auto-runs generate_states.py to rebuild all pages.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = Path(__file__).resolve().parent / "data" / "races.json"
GENERATOR = Path(__file__).resolve().parent / "generate_states.py"


def load_races():
    with open(DATA_FILE) as f:
        return json.load(f)


def save_races(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Updated {DATA_FILE.relative_to(REPO_ROOT)}")


def regenerate():
    print("\nRegenerating pages...")
    subprocess.run([sys.executable, str(GENERATOR)], check=True)
    print("\nDone. Run 'git push' to deploy.")


def list_races(data):
    print(f"\n{'ID':<25} {'State':<6} {'Office':<15} {'Status':<12} Candidates")
    print("-" * 90)
    for race in data["races"]:
        candidates = ", ".join(c["name"] for c in race["candidates"])
        print(f"{race['id']:<25} {race['state_abbr']:<6} {race['office']:<15} {race['status']:<12} {candidates}")


def add_race(data):
    print("\n--- Add New Race ---")
    state_abbr = input("State abbreviation (e.g. TX): ").strip().upper()
    office = input("Office (e.g. US Senate, US House, Governor): ").strip()
    year = input("Year (e.g. 2026): ").strip()

    slug = f"{state_abbr.lower()}-{office.lower().replace(' ', '-')}-{year}"
    race_id = slug

    title = input(f"Title [{year} {state_abbr} {office}]: ").strip()
    if not title:
        title = f"{year} {state_abbr} {office}"

    primary_date = input("Primary date (e.g. March 3, 2026): ").strip()
    general_date = input("General date (e.g. November 3, 2026): ").strip()
    status = input("Status [draft]: ").strip() or "draft"

    race = {
        "id": race_id,
        "state_abbr": state_abbr,
        "office": office,
        "year": int(year),
        "title": title,
        "status": status,
        "url": f"/races/{race_id}/",
        "primary_date": primary_date,
        "general_date": general_date,
        "candidates": []
    }

    data["races"].append(race)
    save_races(data)
    print(f"\n  Added race: {race_id}")
    print(f"  Create folder: races/{race_id}/")
    print(f"  State '{state_abbr}' will now appear active on the map.")

    regenerate()


def add_candidate(data, race_id):
    race = next((r for r in data["races"] if r["id"] == race_id), None)
    if not race:
        print(f"Error: Race '{race_id}' not found.")
        list_races(data)
        sys.exit(1)

    print(f"\n--- Add Candidate to {race['title']} ---")
    name = input("Candidate name: ").strip()
    party = input("Party (dem/rep/ind): ").strip().lower()
    role = input("Role (e.g. Incumbent, Frontrunner, Challenger): ").strip()

    lastname = name.split()[-1].lower()
    candidate = {
        "name": name,
        "party": party,
        "role": role,
        "url": f"{race['url']}{lastname}/"
    }

    race["candidates"].append(candidate)
    save_races(data)
    print(f"\n  Added {name} ({party.upper()}) to {race_id}")
    print(f"  Create folder: races/{race_id}/{lastname}/")

    regenerate()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    data = load_races()

    if cmd == "list":
        list_races(data)
    elif cmd == "add-race":
        add_race(data)
    elif cmd == "add-candidate":
        if len(sys.argv) < 3:
            print("Usage: update_races.py add-candidate <race-id>")
            list_races(data)
            sys.exit(1)
        add_candidate(data, sys.argv[2])
    elif cmd == "regenerate":
        regenerate()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
