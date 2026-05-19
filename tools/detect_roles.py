#!/usr/bin/env python3
"""detect_roles.py — Detect incumbent/challenger roles from SOS election status data.

Cross-references WA Secretary of State CandidateList.csv election status against
races.json to detect incumbents (solo filers with ATG/Elected status) and set
challengers when an incumbent exists in a multi-candidate race.

Rules:
  - Solo filer + "Advanced to General" or "Elected" → incumbent
  - Solo filer + "In Primary" → keep Filed (not confident)
  - Multi-candidate race with incumbent → Filed candidates become challenger
  - Manually-set roles (incumbent/challenger/frontrunner/etc.) never overwritten
  - Role case normalized: 'Incumbent' → 'incumbent', 'Frontrunner' → 'frontrunner'
  - election_status field propagated to all matched WA candidates

Usage:
    python3 tools/detect_roles.py                # Apply changes to races.json
    python3 tools/detect_roles.py --dry-run      # Preview only

C6S Data Engineering — Engagement 7
"""

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "CandidateList.csv"
RACES_JSON = REPO_ROOT / "tools" / "data" / "races.json"

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

from validate_candidates import normalize_name, name_similarity


# --- Role constants ---

# Roles that indicate a known/manual assignment — never overwrite these
KNOWN_ROLES = {"incumbent", "challenger", "frontrunner"}

# Roles that should be case-normalized (Title Case → lowercase)
NORMALIZABLE_ROLES = {"incumbent", "challenger", "frontrunner"}

# Election statuses that indicate incumbent for solo filers
INCUMBENT_STATUSES = {"Advanced to General", "Elected"}

# Name similarity threshold for matching
MATCH_THRESHOLD = 0.82


def match_election_status(json_candidates, csv_candidates):
    """Match races.json candidates to CSV candidates and return election statuses.

    Args:
        json_candidates: List of candidate dicts from races.json
        csv_candidates: List of row dicts from CandidateList.csv

    Returns:
        dict mapping candidate name (from JSON) → election_status string
    """
    if not json_candidates or not csv_candidates:
        return {}

    result = {}

    # Build lookup of normalized CSV names → (original row, election status)
    csv_lookup = []
    for row in csv_candidates:
        name = row.get("Name", "").strip()
        if name:
            csv_lookup.append((normalize_name(name), name, row.get("Election Status", "")))

    for cand in json_candidates:
        cand_name = cand.get("name", "").strip()
        if not cand_name:
            continue

        norm_json = normalize_name(cand_name)

        # Try exact normalized match first
        matched = False
        for norm_csv, orig_csv, status in csv_lookup:
            if norm_json == norm_csv:
                result[cand_name] = status
                matched = True
                break

        if matched:
            continue

        # Fuzzy match fallback
        best_score = 0.0
        best_status = None
        for norm_csv, orig_csv, status in csv_lookup:
            score = name_similarity(cand_name, orig_csv)
            if score > best_score:
                best_score = score
                best_status = status

        if best_score >= MATCH_THRESHOLD:
            result[cand_name] = best_status

    return result


def detect_incumbent(race, election_statuses):
    """Detect incumbent/challenger roles for candidates in a race.

    Args:
        race: Race dict from races.json
        election_statuses: dict mapping candidate name → election_status

    Returns:
        List of (candidate_name, detected_role) tuples in candidate order.

    Rules:
        1. If candidate already has role != 'Filed' → preserve (normalize case)
        2. If race has 1 candidate AND status is ATG/Elected → 'incumbent'
        3. If race has multiple candidates and one is incumbent → Filed → 'challenger'
        4. Otherwise → keep 'Filed'
    """
    candidates = race.get("candidates", [])
    if not candidates:
        return []

    state = race.get("state_abbr", "")

    # Non-WA races: pass through without detection
    if state != "WA":
        return [(c["name"], c.get("role", "Filed")) for c in candidates]

    results = []

    for cand in candidates:
        name = cand.get("name", "")
        role = cand.get("role", "Filed")

        # Normalize case for known roles
        if role.lower() in NORMALIZABLE_ROLES:
            role = role.lower()

        # If role is already set (not Filed), preserve it
        if role != "Filed":
            results.append((name, role))
            continue

        # Role is "Filed" — try to detect
        status = election_statuses.get(name, "")

        if len(candidates) == 1 and status in INCUMBENT_STATUSES:
            # Solo filer with ATG/Elected → incumbent
            results.append((name, "incumbent"))
        else:
            # Keep as Filed for now (will be updated in second pass)
            results.append((name, "Filed"))

    # Second pass: if any candidate in this race is incumbent,
    # convert remaining Filed candidates to challenger
    has_incumbent = any(role == "incumbent" for _, role in results)

    if has_incumbent:
        results = [
            (name, "challenger" if role == "Filed" else role)
            for name, role in results
        ]

    return results


def normalize_roles(races):
    """Normalize role case across all races.

    Converts 'Incumbent' → 'incumbent', 'Frontrunner' → 'frontrunner', etc.
    Does NOT touch 'Filed' (intentional capitalization) or custom roles
    like 'Self-Funded', 'Kemp-Backed'.

    Args:
        races: List of race dicts (modified in place)

    Returns:
        Tuple of (normalized_count, total_incumbents, total_challengers)
    """
    normalized_count = 0
    total_incumbents = 0
    total_challengers = 0

    for race in races:
        for cand in race.get("candidates", []):
            role = cand.get("role", "Filed")

            # Check if this role should be normalized
            if role.lower() in NORMALIZABLE_ROLES and role != role.lower():
                cand["role"] = role.lower()
                normalized_count += 1

            # Count after normalization
            final_role = cand.get("role", "Filed")
            if final_role == "incumbent":
                total_incumbents += 1
            elif final_role == "challenger":
                total_challengers += 1

    return (normalized_count, total_incumbents, total_challengers)


def propagate_election_status(races, election_statuses):
    """Add election_status field to all matched WA candidates.

    Args:
        races: List of race dicts (modified in place)
        election_statuses: dict mapping candidate name → election_status

    Returns:
        Count of candidates updated.
    """
    count = 0

    for race in races:
        # Only propagate to WA candidates
        if race.get("state_abbr", "") != "WA":
            continue

        for cand in race.get("candidates", []):
            name = cand.get("name", "")
            if name in election_statuses:
                cand["election_status"] = election_statuses[name]
                count += 1

    return count


# --- File I/O ---

def load_csv():
    """Load active candidates from SOS CSV."""
    candidates = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get("Status", "").strip().upper()
            if status == "WITHDRAWN":
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


# --- Main workflow ---

def run(dry_run=False):
    """Execute role detection pipeline.

    Returns:
        dict with summary statistics.
    """
    print("=" * 60)
    print("Role Detection — SOS Election Status Analysis")
    print("=" * 60)

    # Load data
    csv_candidates = load_csv()
    data = load_races_json()
    races = data.get("races", [])

    print(f"\nLoaded {len(csv_candidates)} CSV candidates")
    print(f"Loaded {len(races)} races from races.json")

    # Filter to WA races only
    wa_races = [r for r in races if r.get("state_abbr") == "WA"]
    wa_candidates = []
    for r in wa_races:
        wa_candidates.extend(r.get("candidates", []))
    print(f"WA races: {len(wa_races)}, WA candidates: {len(wa_candidates)}")

    # Step 1: Match election statuses
    print("\n--- Step 1: Matching election statuses ---")
    election_statuses = match_election_status(wa_candidates, csv_candidates)
    print(f"Matched {len(election_statuses)} candidates to CSV records")

    # Count statuses
    from collections import Counter
    status_counts = Counter(election_statuses.values())
    for status, count in status_counts.most_common():
        label = status if status else "(blank)"
        print(f"  {label}: {count}")

    # Step 2: Detect roles
    print("\n--- Step 2: Detecting roles ---")
    incumbents_detected = 0
    challengers_set = 0
    roles_preserved = 0
    changes = []

    for race in wa_races:
        results = detect_incumbent(race, election_statuses)
        for i, (name, new_role) in enumerate(results):
            old_role = race["candidates"][i].get("role", "Filed")
            if old_role != new_role:
                changes.append((race["id"], name, old_role, new_role))
                if new_role == "incumbent":
                    incumbents_detected += 1
                elif new_role == "challenger":
                    challengers_set += 1
                # Apply change
                race["candidates"][i]["role"] = new_role
            else:
                if old_role.lower() in KNOWN_ROLES:
                    roles_preserved += 1

    print(f"Incumbents detected: {incumbents_detected}")
    print(f"Challengers set: {challengers_set}")
    print(f"Roles preserved: {roles_preserved}")

    # Step 3: Normalize role case
    print("\n--- Step 3: Normalizing role case ---")
    norm_count, total_inc, total_chal = normalize_roles(races)
    print(f"Case-normalized: {norm_count}")
    print(f"Total incumbents: {total_inc}")
    print(f"Total challengers: {total_chal}")

    # Step 4: Propagate election status
    print("\n--- Step 4: Propagating election status ---")
    status_count = propagate_election_status(races, election_statuses)
    print(f"Election status set on {status_count} candidates")

    # Summary of changes
    if changes:
        print(f"\n--- Role Changes ({len(changes)}) ---")
        for race_id, name, old, new in changes[:30]:
            print(f"  {race_id}: {name} [{old} → {new}]")
        if len(changes) > 30:
            print(f"  ... and {len(changes) - 30} more")

    # Final role distribution
    print("\n--- Final Role Distribution ---")
    role_dist = Counter()
    for race in races:
        for cand in race.get("candidates", []):
            role_dist[cand.get("role", "Filed")] += 1
    for role, count in role_dist.most_common():
        print(f"  {role}: {count}")

    # Save or report
    if dry_run:
        print(f"\n[DRY RUN] No changes written. Would modify {len(changes)} roles + {status_count} statuses.")
    else:
        save_races_json(data)
        print(f"\nWrote updated races.json with {len(changes)} role changes + {status_count} election statuses.")

    return {
        "matched": len(election_statuses),
        "incumbents_detected": incumbents_detected,
        "challengers_set": challengers_set,
        "case_normalized": norm_count,
        "statuses_propagated": status_count,
        "total_changes": len(changes),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect incumbent/challenger roles from SOS election status data."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to races.json",
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
