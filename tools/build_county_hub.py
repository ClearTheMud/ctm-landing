#!/usr/bin/env python3
"""
build_county_hub.py — End-to-end county race hub buildout pipeline

Run this after candidate dossiers are built in the clearthemud repo.
It validates data, generates race/candidate pages, regenerates the
state hub, and reports what's ready for the landing page.

Usage:
    python3 tools/build_county_hub.py WA grays-harbor      # build one county
    python3 tools/build_county_hub.py WA grays-harbor --dry-run  # preview only
    python3 tools/build_county_hub.py WA grays-harbor --skip-state-regen
    python3 tools/build_county_hub.py WA --list-counties    # show all counties

Prereqs:
    1. Candidate dossier JSONs exist in clearthemud/output/dossiers/
    2. County is in races.json with candidates populated
    3. County map SVG exists in geo/states/ (run generate_county_maps.py first)

Pipeline steps:
    1. Validate: races.json has county races, dossier JSONs exist
    2. Generate: race overview + candidate dossier pages
    3. Regenerate: state hub pages (states/{state}/ and states/{state}/{county}/)
    4. Report: landing page snippet for contested/unopposed races
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = Path(__file__).resolve().parent
DATA_DIR = TOOLS_DIR / "data"
RACES_DIR = REPO_ROOT / "races"
STATES_DIR = REPO_ROOT / "states"
GEO_DIR = REPO_ROOT / "geo" / "states"
DOSSIER_ROOT = Path.home() / "Local/Projects/github/clearthemud/output/dossiers"

PARTY_LABEL = {
    "dem": "D", "rep": "R", "ind": "I", "lib": "L",
    "nonpartisan": "", "other": "",
}

PARTY_CSS = {
    "dem": "dem", "rep": "rep", "ind": "neutral", "lib": "neutral",
    "nonpartisan": "neutral", "other": "neutral",
}


def load_races():
    with open(DATA_DIR / "races.json") as f:
        return json.load(f)


def load_counties():
    path = DATA_DIR / "counties.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def get_county_races(races_data, state_abbr, county_slug):
    return [
        r for r in races_data["races"]
        if r.get("county_slug") == county_slug
        and r["state_abbr"] == state_abbr
        and r.get("level") == "county"
    ]


def find_dossier(race, lastname):
    state = race["state_abbr"].lower()
    year = race["year"]
    county_slug = race.get("county_slug", "")
    office = race["office"].lower().strip()

    import re
    office_part = re.sub(r"pos\.\s*", "position_", office)
    office_part = re.sub(r"[^a-z0-9\s]", "", office_part)
    office_part = re.sub(r"\s+", "_", office_part).strip("_")

    search_paths = [
        DOSSIER_ROOT / state / str(year) / "county" / f"{county_slug}-{office_part}" / f"{state}_{office_part}_{county_slug}_{lastname}_{year}.json",
        DOSSIER_ROOT / state / str(year) / "county" / f"{county_slug}-{office_part}" / f"{state}_{office_part}_{lastname}_{year}.json",
        DOSSIER_ROOT / state / str(year) / "county" / f"{state}_{office_part}_{lastname}_{year}.json",
    ]

    for p in search_paths:
        if p.exists():
            return p
    return None


def validate_county(state_abbr, county_slug, county_races):
    issues = []
    warnings = []

    if not county_races:
        issues.append(f"No races found in races.json for {state_abbr}/{county_slug}")
        return issues, warnings

    state_lower = state_abbr.lower()
    county_svg = GEO_DIR / f"{state_lower}-{county_slug}-places.svg"
    if not county_svg.exists():
        warnings.append(f"No places SVG at {county_svg} — run: python3 tools/generate_county_maps.py {state_abbr} --places")

    state_svg = GEO_DIR / f"{state_lower}-counties.svg"
    if not state_svg.exists():
        warnings.append(f"No county map SVG at {state_svg} — run: python3 tools/generate_county_maps.py {state_abbr}")

    total_candidates = 0
    dossiers_found = 0
    dossiers_missing = []

    for race in county_races:
        if race.get("status") == "draft":
            warnings.append(f"Race {race['id']} is draft — will skip page generation")
            continue

        candidates = race.get("candidates", [])
        if not candidates:
            warnings.append(f"Race {race['id']} has no candidates")

        for c in candidates:
            total_candidates += 1
            slug = c.get("slug", c.get("url", "").rstrip("/").split("/")[-1])
            dossier = find_dossier(race, slug)
            if dossier:
                dossiers_found += 1
            else:
                dossiers_missing.append(f"{race['office']}/{slug}")

    if dossiers_missing:
        warnings.append(f"Missing dossier JSONs for {len(dossiers_missing)} candidates: {', '.join(dossiers_missing)}")

    return issues, warnings


def generate_pages(state_abbr, county_slug, county_races, dry_run=False):
    non_draft = [r for r in county_races if r.get("status") != "draft"]
    if not non_draft:
        print("  No non-draft races to generate pages for")
        return 0

    race_ids = [r["id"] for r in non_draft]
    print(f"  Generating pages for {len(non_draft)} races ({len(race_ids)} race IDs)")

    if dry_run:
        for rid in race_ids:
            print(f"    [dry-run] would generate: races/{rid}/")
        return len(race_ids)

    cmd = [sys.executable, str(TOOLS_DIR / "generate_candidate_pages.py"), state_abbr]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: generate_candidate_pages.py failed:\n{result.stderr}")
        return 0
    print(result.stdout)
    return len(non_draft)


def regenerate_state_hub(state_abbr, dry_run=False):
    if dry_run:
        print(f"  [dry-run] would regenerate state hub for {state_abbr}")
        return True

    cmd = [sys.executable, str(TOOLS_DIR / "generate_states.py")]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: generate_states.py failed:\n{result.stderr}")
        return False
    lines = result.stdout.strip().split("\n")
    for line in lines[-5:]:
        print(f"  {line}")
    return True


def generate_landing_snippet(county_name, county_slug, county_races):
    non_draft = [r for r in county_races if r.get("status") != "draft"]
    contested = [r for r in non_draft if len(r.get("candidates", [])) > 1]
    unopposed = [r for r in non_draft if len(r.get("candidates", [])) == 1]

    lines = []
    lines.append(f'    <h3 class="subsection">{county_name} County</h3>')
    lines.append('    <div class="race-grid">')

    for race in sorted(contested, key=lambda r: len(r.get("candidates", [])), reverse=True):
        cands = race.get("candidates", [])
        office = race["office"]
        race_url = race["url"]

        if any(c.get("role") == "incumbent" for c in cands) and len(cands) == 2:
            subtitle = "Incumbent vs. Challenger"
        else:
            subtitle = f"{len(cands)} candidates &bull; Contested"

        lines.append('      <div class="race-card">')
        lines.append(f'        <a href="{race_url}" style="text-decoration:none; color:inherit;">')
        lines.append('          <div class="race-card-header">')
        lines.append(f'            <h3>{office}</h3>')
        lines.append(f'            <p>{subtitle}</p>')
        lines.append('          </div>')
        lines.append('        </a>')
        lines.append('        <div class="race-card-body">')
        lines.append('          <div class="candidates">')

        for c in cands:
            party_short = c.get("party", "other")
            css_class = PARTY_CSS.get(party_short, "neutral")
            label = PARTY_LABEL.get(party_short, "")
            display_name = c["name"]
            if label:
                display_name += f" ({label})"
            slug = c.get("slug", c.get("url", "").rstrip("/").split("/")[-1])
            lines.append(f'            <a href="{race_url}{slug}/" class="candidate-pill {css_class}">{display_name}</a>')

        lines.append('          </div>')
        lines.append('          <div class="race-status">')
        lines.append('            <span class="badge">Deep Dive</span>')
        lines.append(f'            <a href="{race_url}">view race analysis</a>')
        lines.append('          </div>')
        lines.append('        </div>')
        lines.append('      </div>')
        lines.append('')

    lines.append('    </div>')

    if unopposed:
        lines.append('')
        lines.append('    <div class="race-list">')
        for race in unopposed:
            c = race["candidates"][0]
            party_short = c.get("party", "other")
            css_class = PARTY_CSS.get(party_short, "neutral")
            label = PARTY_LABEL.get(party_short, "")
            display_name = c["name"]
            if label:
                display_name += f" ({label})"
            slug = c.get("slug", c.get("url", "").rstrip("/").split("/")[-1])
            lines.append('      <div class="race-item">')
            lines.append(f'        <a href="{race["url"]}" class="race-name">{race["office"]}</a>')
            lines.append(f'        <a href="{race["url"]}{slug}/" class="candidate-pill {css_class}">{display_name}</a>')
            lines.append('      </div>')
        lines.append('    </div>')

    return "\n".join(lines)


def list_counties(state_abbr):
    counties = load_counties()
    state_counties = counties.get(state_abbr, [])
    if not state_counties:
        print(f"No counties in counties.json for {state_abbr}")
        return

    races_data = load_races()
    print(f"\n{state_abbr} Counties ({len(state_counties)}):")
    print(f"{'County':<25} {'FIPS':<6} {'Races':<8} {'Candidates':<12} {'Status'}")
    print("-" * 65)

    for c in sorted(state_counties, key=lambda x: x["name"]):
        county_races = get_county_races(races_data, state_abbr, c["slug"])
        total_cands = sum(len(r.get("candidates", [])) for r in county_races)
        has_pages = (RACES_DIR / f"wa-{c['slug']}-sheriff-2026").exists() if county_races else False
        status = "built" if has_pages and county_races else ("data only" if county_races else "no data")
        print(f"{c['name']:<25} {c['fips']:<6} {len(county_races):<8} {total_cands:<12} {status}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="County race hub buildout pipeline")
    parser.add_argument("state", help="State abbreviation (e.g., WA)")
    parser.add_argument("county", nargs="?", help="County slug (e.g., grays-harbor)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--skip-state-regen", action="store_true", help="Skip state hub regeneration")
    parser.add_argument("--list-counties", action="store_true", help="List all counties for a state")
    args = parser.parse_args()

    state_abbr = args.state.upper()

    if args.list_counties:
        list_counties(state_abbr)
        return

    if not args.county:
        print("Error: county slug is required (or use --list-counties)")
        sys.exit(1)

    county_slug = args.county.lower()
    races_data = load_races()
    county_races = get_county_races(races_data, state_abbr, county_slug)

    counties = load_counties()
    state_counties = counties.get(state_abbr, [])
    county_meta = next((c for c in state_counties if c["slug"] == county_slug), None)
    county_name = county_meta["name"] if county_meta else county_slug.replace("-", " ").title()

    print(f"\n{'='*60}")
    print(f"County Hub Buildout: {county_name} County, {state_abbr}")
    print(f"{'='*60}")

    # Step 1: Validate
    print(f"\n[1/4] Validating data...")
    issues, warnings = validate_county(state_abbr, county_slug, county_races)

    print(f"  Races: {len(county_races)}")
    total_cands = sum(len(r.get("candidates", [])) for r in county_races)
    print(f"  Candidates: {total_cands}")

    for w in warnings:
        print(f"  WARNING: {w}")
    for i in issues:
        print(f"  ERROR: {i}")

    if issues:
        print("\nBuild aborted due to errors.")
        sys.exit(1)

    # Step 2: Generate race/candidate pages
    print(f"\n[2/4] Generating race & candidate pages...")
    pages = generate_pages(state_abbr, county_slug, county_races, args.dry_run)
    print(f"  Generated pages for {pages} races")

    # Step 3: Regenerate state hub
    if not args.skip_state_regen:
        print(f"\n[3/4] Regenerating state hub pages...")
        regenerate_state_hub(state_abbr, args.dry_run)
    else:
        print(f"\n[3/4] Skipped state hub regeneration (--skip-state-regen)")

    # Step 4: Report landing page snippet
    print(f"\n[4/4] Landing page snippet for {county_name} County:")
    print(f"{'─'*60}")
    snippet = generate_landing_snippet(county_name, county_slug, county_races)
    print(snippet)
    print(f"{'─'*60}")
    print(f"\nPaste the snippet above into index.html inside the")
    print(f"<div class=\"recently-added\"> section.")

    # Summary
    contested = [r for r in county_races if len(r.get("candidates", [])) > 1 and r.get("status") != "draft"]
    unopposed = [r for r in county_races if len(r.get("candidates", [])) == 1 and r.get("status") != "draft"]
    draft = [r for r in county_races if r.get("status") == "draft"]

    print(f"\n{'='*60}")
    print(f"Summary: {county_name} County, {state_abbr}")
    print(f"  Contested races: {len(contested)}")
    print(f"  Unopposed races: {len(unopposed)}")
    print(f"  Draft (skipped):  {len(draft)}")
    print(f"  Total candidates: {total_cands}")
    print(f"\nNext steps:")
    print(f"  1. Review generated pages in races/wa-{county_slug}-*/")
    print(f"  2. Add landing page snippet to index.html")
    print(f"  3. git add && git commit && git push to deploy")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
