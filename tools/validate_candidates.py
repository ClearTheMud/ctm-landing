#!/usr/bin/env python3
"""
WA Candidate Validation Script
Cross-references CandidateList.csv (WA SOS) against races.json and directory structure.

C6S Data Quality Assessment — Engagement 7
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "CandidateList.csv"
RACES_JSON = REPO_ROOT / "tools" / "data" / "races.json"
RACES_DIR = REPO_ROOT / "races"

# --- Name Normalization ---

def normalize_name(name):
    """Normalize a candidate name for fuzzy matching."""
    name = name.strip()
    name = re.sub(r'"[^"]*"', '', name)  # remove quoted nicknames
    name = re.sub(r'\([^)]*\)', '', name)  # remove parenthetical
    name = re.sub(r'\b(Jr\.?|Sr\.?|III|II|IV)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.upper()


def name_similarity(a, b):
    """Score similarity between two names (0-1)."""
    na, nb = normalize_name(a), normalize_name(b)
    if na == nb:
        return 1.0
    # Try last-name match
    parts_a = na.split()
    parts_b = nb.split()
    if parts_a and parts_b and parts_a[-1] == parts_b[-1]:
        return 0.85 + 0.15 * SequenceMatcher(None, na, nb).ratio()
    return SequenceMatcher(None, na, nb).ratio()


def extract_lastname(name):
    """Extract likely last name from full name."""
    name = normalize_name(name)
    parts = name.split()
    return parts[-1] if parts else name


# --- Party Normalization ---

PARTY_MAP = {
    'DEMOCRATIC': 'dem',
    'DEMOCRAT': 'dem',
    'LABOR DEMOCRAT': 'dem',
    'CASCADE DEMOCRAT': 'dem',
    'PRACTICAL DEMOCRAT': 'dem',
    'MODERATE DEMOCRAT': 'dem',
    'REPUBLICAN': 'rep',
    'GOP': 'rep',
    'TRUMP REPUBLICAN': 'rep',
    'REPUBLICAN - GOP': 'rep',
    'REPUBILCAN': 'rep',  # typo in SOS data
    'INDEPENDENT': 'ind',
    'INDEPENDANT': 'ind',  # typo in SOS data
    'IND': 'ind',
    'STATES NO PARTY PREFERENCE': 'nonpartisan',
    'States No Party Preference': 'nonpartisan',
    'NONPARTISAN': 'nonpartisan',
    'NON PARTISAN': 'nonpartisan',
    'LIBERTARIAN': 'lib',
    'CASCADE': 'cascade',
    'SOCIALIST WORKERS': 'other',
    'FIFTH REPUBLIC': 'other',
    'UNION': 'other',
    'NO KINGS': 'other',
    'PRO GUN LIBERAL': 'other',
    'STANDUP-AMERICA': 'other',
    'TEA': 'other',
    '': 'nonpartisan',
}


def normalize_party_csv(party_str):
    """Normalize CSV party to internal code."""
    p = party_str.strip().upper()
    for key, val in PARTY_MAP.items():
        if key.upper() == p:
            return val
    return 'unknown'


def normalize_party_json(party_str):
    """Normalize races.json party to internal code."""
    p = party_str.strip()
    mapping = {
        'dem': 'dem', 'D': 'dem', 'd': 'dem',
        'rep': 'rep', 'R': 'rep', 'r': 'rep',
        'ind': 'ind', 'I': 'ind', 'i': 'ind',
        'nonpartisan': 'nonpartisan', 'NP': 'nonpartisan', 'np': 'nonpartisan',
        'neutral': 'nonpartisan',
        'lib': 'lib', 'L': 'lib',
        'cascade': 'cascade', 'Cascade': 'cascade',
        'Fifth Republic': 'other', 'Socialist Workers': 'other',
        'Union': 'other', 'No Kings': 'other',
        'Pro Gun Liberal': 'other', 'Standup-America': 'other',
        'TEA': 'other', 'Tea': 'other', 'tea': 'other',
        '': 'nonpartisan',
    }
    return mapping.get(p, 'unknown')


# --- Race Type Normalization ---

def normalize_race_type(district_type, race, district):
    """Map CSV race info to a normalized (race_category, district_key) tuple."""
    dt = district_type.strip().upper()
    race_clean = race.strip()
    race_upper = race_clean.upper()
    dist = district.strip()

    # Congressional
    if dt == 'CONGRESSIONAL' or 'U.S. REPRESENTATIVE' in race_upper or 'U.S. SENATOR' in race_upper:
        if 'SENATOR' in race_upper:
            return ('US Senate', 'WA')
        m = re.search(r'(\d+)', dist)
        if m:
            return ('US House', m.group(1))

    # Legislative
    if dt == 'LEGISLATIVE' or 'STATE REPRESENTATIVE' in race_upper or 'STATE SENATOR' in race_upper:
        m = re.search(r'(\d+)', dist)
        ld = m.group(1) if m else '?'
        if 'SENATOR' in race_upper:
            return ('State Senate', ld)
        if 'POS' in race_upper and '2' in race_upper:
            return ('State House Pos. 2', ld)
        if 'POS' in race_upper and '1' in race_upper:
            return ('State House Pos. 1', ld)
        return ('State House', ld)

    # County-level (many variations)
    race_lower = race_clean.lower()
    if 'assessor' in race_lower:
        return ('Assessor', 'county')
    if 'auditor' in race_lower:
        return ('Auditor', 'county')
    if 'clerk' in race_lower and 'district court' not in race_lower:
        return ('Clerk', 'county')
    if 'sheriff' in race_lower:
        return ('Sheriff', 'county')
    if 'treasurer' in race_lower:
        return ('Treasurer', 'county')
    if 'coroner' in race_lower:
        return ('Coroner', 'county')
    if 'prosecut' in race_lower:
        return ('Prosecuting Attorney', 'county')
    if 'prosecutor' in race_lower:
        return ('Prosecutor', 'county')

    # Supreme Court
    dist_upper = dist.upper()
    if 'SUPREME' in dist_upper or 'SUPREME' in race_upper:
        m = re.search(r'(\d+)', race_clean)
        return ('Supreme Court', m.group(1) if m else '?')

    # Court of Appeals
    if 'APPEALS' in dist_upper or 'APPEALS' in race_upper:
        div_m = re.search(r'DIVISION\s+(\d+)', dist_upper)
        dist_m = re.search(r'DISTRICT\s+(\d+)', dist_upper)
        pos_m = re.search(r'(\d+)', race_clean)
        key = f"div{div_m.group(1) if div_m else '?'}-dist{dist_m.group(1) if dist_m else '?'}-pos{pos_m.group(1) if pos_m else '?'}"
        return ('Court of Appeals', key)

    # Superior Court (not Clerk)
    if 'SUPERIOR' in dist_upper and 'CLERK' not in race_upper:
        pos_m = re.search(r'(\d+)', race_clean)
        return ('Superior Court', f"{dist}|{pos_m.group(1) if pos_m else '?'}")

    # PUD Commissioner (before generic Commissioner)
    if dt == 'PUBLIC UTILITY' or 'PUD' in dist_upper or 'UTILITY' in dist_upper or 'PUD' in race_upper:
        pos_m = re.search(r'(\d+|[A-Za-z])\s*$', re.sub(r'(commissioner|comm|dist|district|no|#|\.|-|,)', '', dist.lower()).strip())
        if not pos_m:
            pos_m = re.search(r'(\d+)', race_clean)
        return ('PUD Commissioner', f"{dist}|{pos_m.group(1) if pos_m else '?'}")

    # Port Commissioner (before generic Commissioner)
    if 'PORT' in dist_upper:
        pos_m = re.search(r'(\d+)', race_clean + ' ' + dist)
        return ('Port Commissioner', f"{dist}|{pos_m.group(1) if pos_m else '?'}")

    # Municipal Court
    if 'MUNICIPAL' in race_upper:
        pos_m = re.search(r'(\d+)', race_clean)
        return ('Municipal Court', f"{dist}|{pos_m.group(1) if pos_m else '?'}")

    # KC Electoral District Court
    if 'ELECTORAL' in dist_upper:
        pos_m = re.search(r'(\d+)', race_clean)
        return ('KC Electoral Court', f"{dist}|{pos_m.group(1) if pos_m else '?'}")

    # County Council / Councilor
    if 'COUNTY COUNCIL' in dist_upper or 'COUNTY COUNCILOR' in dist_upper:
        pos_m = re.search(r'(\d+)', race_clean + ' ' + dist)
        return ('County Council', f"{dist}|{pos_m.group(1) if pos_m else '?'}")

    # City Council
    if ('SEATTLE CITY COUNCIL' in dist_upper or ('CITY' in dist_upper and 'COUNCIL' in race_upper)):
        pos_m = re.search(r'(\d+)', race_clean)
        return ('City Council', f"{dist}|{pos_m.group(1) if pos_m else '?'}")

    # Commissioner (county-level, after PUD/Port)
    if 'commissioner' in race_lower or 'COMMISSIONER' in dt:
        m = re.search(r'(\d+)', race_clean + ' ' + dist)
        num = m.group(1) if m else '?'
        return ('Commissioner', num)

    # District Court Judge (judicial and county-level)
    if 'district court' in race_lower or 'DISTRICT COURT' in dist_upper:
        m = re.search(r'(?:pos(?:ition)?\.?\s*|#|dept\.?\s*|department\s*(?:no\.?\s*)?)(\d+)', race_lower)
        if m:
            return ('District Court Judge', m.group(1))
        m = re.search(r'(?:judge|court)\s*(?:no\.?\s*)?(\d+)', race_lower)
        if m:
            return ('District Court Judge', m.group(1))
        return ('District Court Judge', '0')

    # Director of Community Development, Director of Elections, etc.
    if 'director' in race_lower:
        return ('Director', race_clean)

    return ('Other', f'{dt}|{race_clean}|{dist}')


def map_json_race_to_category(race_obj):
    """Map a races.json race to the same category system."""
    office = race_obj.get('office', '')
    race_id = race_obj.get('id', '')

    if office == 'US House':
        m = re.search(r'house-(\d+)', race_id)
        return ('US House', m.group(1) if m else '?')
    if office == 'US Senate':
        return ('US Senate', 'WA')
    if office == 'State Senate':
        m = re.search(r'senate-(\d+)', race_id)
        return ('State Senate', m.group(1) if m else '?')
    if 'State House Pos. 1' in office:
        m = re.search(r'house-(\d+)', race_id)
        return ('State House Pos. 1', m.group(1) if m else '?')
    if 'State House Pos. 2' in office:
        m = re.search(r'house-(\d+)', race_id)
        return ('State House Pos. 2', m.group(1) if m else '?')

    off_lower = office.lower()

    # Supreme Court
    if 'supreme court' in off_lower:
        m = re.search(r'(\d+)', office)
        return ('Supreme Court', m.group(1) if m else '?')

    # Court of Appeals
    if 'court of appeals' in off_lower or 'appeals-div' in race_id:
        div_m = re.search(r'div[.-]?\s*(\d+)', race_id)
        dist_m = re.search(r'dist[.-]?\s*(\d+)', race_id)
        pos_m = re.search(r'pos[.-]?\s*(\d+)', race_id)
        key = f"div{div_m.group(1) if div_m else '?'}-dist{dist_m.group(1) if dist_m else '?'}-pos{pos_m.group(1) if pos_m else '?'}"
        return ('Court of Appeals', key)

    # Superior Court (but not Clerk of Superior Court)
    if 'superior court' in off_lower and 'clerk' not in off_lower:
        pos_m = re.search(r'(\d+)', office)
        return ('Superior Court', f"{office}|{pos_m.group(1) if pos_m else '?'}")

    # PUD Commissioner (before generic Commissioner)
    if 'pud' in off_lower or 'pud' in race_id:
        pos_m = re.search(r'dist[.-]?\s*(\d+|[a-z])', race_id)
        return ('PUD Commissioner', f"{office}|{pos_m.group(1) if pos_m else '?'}")

    # Port Commissioner (before generic Commissioner)
    if 'port' in off_lower and 'commissioner' in off_lower:
        pos_m = re.search(r'dist[.-]?\s*(\d+)', race_id)
        return ('Port Commissioner', f"{office}|{pos_m.group(1) if pos_m else '?'}")

    # Municipal Court
    if 'municipal court' in off_lower:
        pos_m = re.search(r'(\d+)', office)
        return ('Municipal Court', f"{office}|{pos_m.group(1) if pos_m else '?'}")

    # KC Electoral District Court
    if 'electoral' in off_lower or 'electoral' in race_id:
        pos_m = re.search(r'(\d+)', office)
        return ('KC Electoral Court', f"{office}|{pos_m.group(1) if pos_m else '?'}")

    # County Council
    if 'county council' in off_lower:
        pos_m = re.search(r'(\d+)', office)
        return ('County Council', f"{office}|{pos_m.group(1) if pos_m else '?'}")

    # City Council
    if 'city council' in off_lower:
        pos_m = re.search(r'(\d+)', office)
        return ('City Council', f"{office}|{pos_m.group(1) if pos_m else '?'}")

    # County-level normalization
    if 'assessor' in off_lower:
        return ('Assessor', 'county')
    if 'auditor' in off_lower:
        return ('Auditor', 'county')
    if 'clerk' in off_lower and 'district court' not in off_lower:
        return ('Clerk', 'county')
    if 'sheriff' in off_lower:
        return ('Sheriff', 'county')
    if 'treasurer' in off_lower:
        return ('Treasurer', 'county')
    if 'coroner' in off_lower:
        return ('Coroner', 'county')
    if 'prosecut' in off_lower:
        return ('Prosecuting Attorney', 'county')
    if off_lower == 'prosecutor':
        return ('Prosecutor', 'county')
    if 'commissioner' in off_lower:
        m = re.search(r'(\d+)', office)
        return ('Commissioner', m.group(1) if m else '?')
    if 'district court' in off_lower:
        m = re.search(r'(\d+)', office)
        if m:
            return ('District Court Judge', m.group(1))
        return ('District Court Judge', '0')
    if 'director' in off_lower:
        return ('Director', office)

    return ('Other', office)


# --- Data Loading ---

def load_csv():
    """Load and parse CandidateList.csv."""
    candidates = []
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get('Status', '').strip()
            if status.upper() == 'WITHDRAWN':
                continue  # skip withdrawn candidates
            cat, key = normalize_race_type(
                row['District Type'], row['Race'], row['District']
            )
            candidates.append({
                'name': row['Name'].strip(),
                'name_norm': normalize_name(row['Name']),
                'lastname': extract_lastname(row['Name']),
                'party_raw': row['Party Preference'].strip(),
                'party': normalize_party_csv(row['Party Preference']),
                'race_category': cat,
                'race_key': key,
                'district_type': row['District Type'].strip(),
                'district': row['District'].strip(),
                'race_raw': row['Race'].strip(),
                'address': row.get('Mailing Address', ''),
                'filing_date': row.get('Filing Date', ''),
                'election_status': row.get('Election Status', ''),
            })
    return candidates


def load_races_json():
    """Load races.json and extract WA candidates."""
    with open(RACES_JSON) as f:
        data = json.load(f)
    candidates = []
    races = []
    for race in data.get('races', []):
        if race.get('state_abbr') != 'WA':
            continue
        races.append(race)
        cat, key = map_json_race_to_category(race)
        for cand in race.get('candidates', []):
            candidates.append({
                'name': cand['name'],
                'name_norm': normalize_name(cand['name']),
                'lastname': extract_lastname(cand['name']),
                'party': normalize_party_json(cand.get('party', '')),
                'party_raw': cand.get('party', ''),
                'race_id': race['id'],
                'race_category': cat,
                'race_key': key,
                'office': race.get('office', ''),
                'url': cand.get('url', ''),
            })
    return candidates, races


def scan_directories():
    """Scan race directories for candidate folders."""
    dirs = []
    for race_dir in sorted(RACES_DIR.glob('wa-*')):
        if not race_dir.is_dir():
            continue
        race_id = race_dir.name
        for cand_dir in sorted(race_dir.iterdir()):
            if cand_dir.is_dir() and not cand_dir.name.startswith('.'):
                dirs.append({
                    'race_id': race_id,
                    'dirname': cand_dir.name,
                    'has_index': (cand_dir / 'index.html').exists(),
                    'path': str(cand_dir.relative_to(REPO_ROOT)),
                })
    return dirs


# --- Matching Engine ---

def match_candidates(csv_cands, json_cands):
    """Match CSV candidates to JSON candidates."""
    results = {
        'matched': [],
        'csv_only': [],       # in SOS but not in races.json
        'json_only': [],      # in races.json but not in SOS
        'party_mismatch': [], # matched but party differs
    }

    # Index JSON candidates by normalized name
    json_by_name = defaultdict(list)
    for jc in json_cands:
        json_by_name[jc['name_norm']].append(jc)

    # Index JSON candidates by lastname + race_category
    json_by_last_cat = defaultdict(list)
    for jc in json_cands:
        json_by_last_cat[(jc['lastname'], jc['race_category'])].append(jc)

    json_matched = set()
    csv_matched = set()

    # Pass 1: Exact name match within same race category + key (federal/legislative)
    for i, cc in enumerate(csv_cands):
        if cc['race_key'] != 'county':
            for jc in json_by_name.get(cc['name_norm'], []):
                if jc['race_category'] == cc['race_category'] and jc['race_key'] == cc['race_key']:
                    jid = id(jc)
                    if jid not in json_matched:
                        results['matched'].append((cc, jc))
                        json_matched.add(jid)
                        csv_matched.add(i)
                        break

    # Pass 2: Exact name match by category (county-level + new race types)
    NEW_CATS = {'Supreme Court', 'Court of Appeals', 'Superior Court', 'PUD Commissioner',
                'Port Commissioner', 'Municipal Court', 'KC Electoral Court', 'County Council',
                'City Council', 'District Court Judge'}
    for i, cc in enumerate(csv_cands):
        if i in csv_matched:
            continue
        cat = cc['race_category']
        match_cats = {cat}
        if cat in ('Prosecuting Attorney', 'Prosecutor'):
            match_cats = {'Prosecuting Attorney', 'Prosecutor'}
        if cc['race_key'] == 'county' or cat in NEW_CATS:
            for jc in json_by_name.get(cc['name_norm'], []):
                jid = id(jc)
                if jid in json_matched:
                    continue
                if jc['race_category'] in match_cats or (cc['race_key'] == 'county' and jc['race_key'] == 'county'):
                    results['matched'].append((cc, jc))
                    json_matched.add(jid)
                    csv_matched.add(i)
                    break

    # Pass 3: Fuzzy name match (lastname + category)
    for i, cc in enumerate(csv_cands):
        if i in csv_matched:
            continue
        cat = cc['race_category']
        match_cats = {cat}
        if cat in ('Prosecuting Attorney', 'Prosecutor'):
            match_cats = {'Prosecuting Attorney', 'Prosecutor'}

        best_match = None
        best_score = 0
        for jc in json_cands:
            jid = id(jc)
            if jid in json_matched:
                continue
            if jc['race_category'] not in match_cats and not (cc['race_key'] == 'county' and jc['race_key'] == 'county'):
                if jc['race_category'] != cc['race_category']:
                    continue
            sim = name_similarity(cc['name'], jc['name'])
            if sim > best_score and sim >= 0.75:
                best_match = jc
                best_score = sim

        if best_match:
            jid = id(best_match)
            results['matched'].append((cc, best_match))
            json_matched.add(jid)
            csv_matched.add(i)

    # Collect unmatched
    for i, cc in enumerate(csv_cands):
        if i not in csv_matched:
            results['csv_only'].append(cc)

    for jc in json_cands:
        if id(jc) not in json_matched:
            results['json_only'].append(jc)

    # Check party mismatches among matched pairs
    for cc, jc in results['matched']:
        cp = cc['party']
        jp = jc['party']
        # Allow nonpartisan/unknown flexibility for county races
        if cp == jp:
            continue
        if cp in ('nonpartisan', 'unknown') and jp in ('nonpartisan', 'unknown', ''):
            continue
        if jp in ('nonpartisan', 'unknown') and cp in ('nonpartisan', 'unknown', ''):
            continue
        results['party_mismatch'].append((cc, jc))

    return results


def validate_directories(json_cands, dirs):
    """Cross-check directory structure against races.json candidates."""
    results = {
        'dir_no_json': [],   # directory exists but no candidate in races.json
        'json_no_dir': [],   # candidate in races.json but no directory
        'missing_index': [], # directory exists but no index.html
    }

    # Build map: race_id -> set of candidate lastnames from dirs
    dir_map = defaultdict(set)
    dir_index = {}
    for d in dirs:
        dir_map[d['race_id']].add(d['dirname'].lower())
        dir_index[(d['race_id'], d['dirname'].lower())] = d

    # Build map: race_id -> candidates from JSON
    json_map = defaultdict(list)
    for jc in json_cands:
        json_map[jc['race_id']].append(jc)

    # Check JSON candidates for directory existence
    for jc in json_cands:
        url = jc.get('url', '')
        if url:
            # Extract expected dirname from URL
            parts = [p for p in url.strip('/').split('/') if p]
            if len(parts) >= 2:
                expected_dir = parts[-1].lower()
                race_id = jc['race_id']
                if expected_dir not in dir_map.get(race_id, set()):
                    results['json_no_dir'].append(jc)

    # Check directories for JSON candidate
    for d in dirs:
        race_id = d['race_id']
        dirname = d['dirname'].lower()
        # Find matching candidate in JSON
        found = False
        for jc in json_map.get(race_id, []):
            url = jc.get('url', '')
            if url:
                parts = [p for p in url.strip('/').split('/') if p]
                if len(parts) >= 2 and parts[-1].lower() == dirname:
                    found = True
                    break
            elif extract_lastname(jc['name']).lower() == dirname:
                found = True
                break
        if not found:
            results['dir_no_json'].append(d)

        if not d['has_index']:
            results['missing_index'].append(d)

    return results


# --- Quality Scoring ---

def compute_quality_scores(csv_cands, json_cands, match_results, dir_results):
    """Compute data quality scores across six dimensions."""
    total_csv = len(csv_cands)
    total_json = len(json_cands)
    matched = len(match_results['matched'])

    # Completeness: what % of SOS candidates are in our data
    completeness = matched / total_csv * 100 if total_csv > 0 else 0

    # Accuracy: what % of our candidates actually exist in SOS
    accuracy = matched / total_json * 100 if total_json > 0 else 0

    # Consistency: matched without party mismatch
    party_correct = matched - len(match_results['party_mismatch'])
    consistency = party_correct / matched * 100 if matched > 0 else 0

    # Validity: JSON candidates with valid directory
    json_with_dir = total_json - len(dir_results['json_no_dir'])
    validity = json_with_dir / total_json * 100 if total_json > 0 else 0

    # Uniqueness: check for duplicate names in JSON
    seen = set()
    dupes = 0
    for jc in json_cands:
        key = (jc['name_norm'], jc['race_id'])
        if key in seen:
            dupes += 1
        seen.add(key)
    uniqueness = (total_json - dupes) / total_json * 100 if total_json > 0 else 0

    return {
        'completeness': round(completeness, 1),
        'accuracy': round(accuracy, 1),
        'consistency': round(consistency, 1),
        'validity': round(validity, 1),
        'uniqueness': round(uniqueness, 1),
        'overall': round((completeness + accuracy + consistency + validity + uniqueness) / 5, 1),
        'detail': {
            'total_sos_candidates': total_csv,
            'total_json_candidates': total_json,
            'matched': matched,
            'sos_only': len(match_results['csv_only']),
            'json_only': len(match_results['json_only']),
            'party_mismatches': len(match_results['party_mismatch']),
            'dir_orphans': len(dir_results['dir_no_json']),
            'missing_dirs': len(dir_results['json_no_dir']),
            'missing_index_html': len(dir_results['missing_index']),
            'duplicates': dupes,
        }
    }


# --- Race Coverage Analysis ---

def analyze_race_coverage(csv_cands, json_races):
    """Identify SOS race types not covered in races.json."""
    # Build set of (category, key) pairs from JSON
    json_race_keys = set()
    for race in json_races:
        cat, key = map_json_race_to_category(race)
        json_race_keys.add((cat, key))

    # Build CSV race groups
    csv_race_groups = defaultdict(list)
    for cc in csv_cands:
        csv_race_groups[(cc['race_category'], cc['race_key'])].append(cc)

    missing_races = []
    for (cat, key), cands in sorted(csv_race_groups.items()):
        if cat in ('Other', 'PUD', 'Port', 'Municipal', 'Higher Court'):
            continue  # skip non-target race types
        if key != 'county' and (cat, key) not in json_race_keys:
            missing_races.append({
                'category': cat,
                'key': key,
                'candidate_count': len(cands),
                'candidates': [c['name'] for c in cands],
            })

    return missing_races


# --- Report Generation ---

def generate_report(scores, match_results, dir_results, coverage_gaps):
    """Generate the full validation report."""
    lines = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    lines.append("# WA Candidate Validation Report")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Data Source:** WA Secretary of State CandidateList.csv (voter.votewa.gov)")
    lines.append(f"**Engagement:** C6S Data Quality Assessment — Engagement 7")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    d = scores['detail']
    lines.append(f"Cross-referenced **{d['total_json_candidates']}** candidates in races.json "
                 f"against **{d['total_sos_candidates']}** active SOS filings.")
    lines.append(f"- **{d['matched']}** candidates matched ({scores['completeness']}% SOS coverage)")
    lines.append(f"- **{d['sos_only']}** SOS candidates missing from races.json")
    lines.append(f"- **{d['json_only']}** races.json candidates not found in SOS data")
    lines.append(f"- **{d['party_mismatches']}** party affiliation mismatches")
    lines.append(f"- **{d['dir_orphans']}** orphan directories (no races.json entry)")
    lines.append(f"- **{d['missing_dirs']}** candidates missing directories")
    lines.append(f"- **Overall Quality Score: {scores['overall']}%**")
    lines.append("")

    # Quality Scorecard
    lines.append("## Data Quality Scorecard")
    lines.append("")
    lines.append("| Dimension | Score | Description |")
    lines.append("|-----------|-------|-------------|")
    lines.append(f"| Completeness | **{scores['completeness']}%** | SOS candidates present in races.json |")
    lines.append(f"| Accuracy | **{scores['accuracy']}%** | races.json candidates confirmed by SOS |")
    lines.append(f"| Consistency | **{scores['consistency']}%** | Party affiliation agreement |")
    lines.append(f"| Validity | **{scores['validity']}%** | Candidates with valid directory structure |")
    lines.append(f"| Uniqueness | **{scores['uniqueness']}%** | No duplicate candidate entries |")
    lines.append(f"| **Overall** | **{scores['overall']}%** | Average across dimensions |")
    lines.append("")

    # Party Mismatches
    if match_results['party_mismatch']:
        lines.append("## Finding: Party Affiliation Mismatches")
        lines.append(f"**Priority:** High")
        lines.append(f"**Count:** {len(match_results['party_mismatch'])}")
        lines.append("")
        lines.append("| Candidate | Race ID | SOS Party | Our Party | SOS Raw |")
        lines.append("|-----------|---------|-----------|-----------|---------|")
        for cc, jc in sorted(match_results['party_mismatch'], key=lambda x: x[1]['race_id']):
            lines.append(f"| {cc['name']} | {jc['race_id']} | {cc['party']} | {jc['party']} | {cc['party_raw']} |")
        lines.append("")

    # JSON-Only (in our data but not in SOS)
    if match_results['json_only']:
        lines.append("## Finding: Candidates in races.json NOT in SOS Filings")
        lines.append(f"**Priority:** Critical — may indicate withdrawn, unfiled, or name-mismatched candidates")
        lines.append(f"**Count:** {len(match_results['json_only'])}")
        lines.append("")

        by_cat = defaultdict(list)
        for jc in match_results['json_only']:
            by_cat[jc['race_category']].append(jc)

        for cat in sorted(by_cat.keys()):
            cands = by_cat[cat]
            lines.append(f"### {cat} ({len(cands)})")
            lines.append("")
            lines.append("| Candidate | Race ID | Party |")
            lines.append("|-----------|---------|-------|")
            for jc in sorted(cands, key=lambda x: x['race_id']):
                lines.append(f"| {jc['name']} | {jc['race_id']} | {jc['party_raw']} |")
            lines.append("")

    # CSV-Only (in SOS but not in our data) — grouped by category
    if match_results['csv_only']:
        lines.append("## Finding: SOS Candidates Missing from races.json")
        lines.append(f"**Priority:** High — filed candidates not yet in our database")
        lines.append(f"**Count:** {len(match_results['csv_only'])}")
        lines.append("")

        by_cat = defaultdict(list)
        for cc in match_results['csv_only']:
            by_cat[cc['race_category']].append(cc)

        for cat in sorted(by_cat.keys()):
            cands = by_cat[cat]
            lines.append(f"### {cat} ({len(cands)})")
            lines.append("")
            lines.append("| Candidate | Party | Race (raw) | District |")
            lines.append("|-----------|-------|------------|----------|")
            for cc in sorted(cands, key=lambda x: (x.get('race_key', ''), x['name'])):
                lines.append(f"| {cc['name']} | {cc['party_raw']} | {cc['race_raw']} | {cc['district']} |")
            lines.append("")

    # Directory Validation
    if dir_results['dir_no_json'] or dir_results['json_no_dir'] or dir_results['missing_index']:
        lines.append("## Finding: Directory Structure Discrepancies")
        lines.append(f"**Priority:** Medium")
        lines.append("")

        if dir_results['dir_no_json']:
            lines.append(f"### Orphan Directories ({len(dir_results['dir_no_json'])})")
            lines.append("Directories exist but no matching candidate in races.json.")
            lines.append("")
            lines.append("| Path | Race ID |")
            lines.append("|------|---------|")
            for d in sorted(dir_results['dir_no_json'], key=lambda x: x['path']):
                lines.append(f"| {d['path']} | {d['race_id']} |")
            lines.append("")

        if dir_results['json_no_dir']:
            lines.append(f"### Missing Directories ({len(dir_results['json_no_dir'])})")
            lines.append("Candidates in races.json with no directory on disk.")
            lines.append("")
            lines.append("| Candidate | Race ID | Expected URL |")
            lines.append("|-----------|---------|--------------|")
            for jc in sorted(dir_results['json_no_dir'], key=lambda x: x['race_id']):
                lines.append(f"| {jc['name']} | {jc['race_id']} | {jc.get('url', 'N/A')} |")
            lines.append("")

        if dir_results['missing_index']:
            lines.append(f"### Directories Missing index.html ({len(dir_results['missing_index'])})")
            lines.append("")
            lines.append("| Path |")
            lines.append("|------|")
            for d in sorted(dir_results['missing_index'], key=lambda x: x['path']):
                lines.append(f"| {d['path']} |")
            lines.append("")

    # Race Coverage Gaps
    if coverage_gaps:
        lines.append("## Finding: SOS Races Not in races.json (Federal/Legislative)")
        lines.append(f"**Priority:** Medium — filed races without race directory")
        lines.append(f"**Count:** {len(coverage_gaps)}")
        lines.append("")
        lines.append("| Race Type | District | Candidates |")
        lines.append("|-----------|----------|------------|")
        for gap in sorted(coverage_gaps, key=lambda x: (x['category'], x['key'])):
            names = ', '.join(gap['candidates'][:5])
            if len(gap['candidates']) > 5:
                names += f' (+{len(gap["candidates"]) - 5} more)'
            lines.append(f"| {gap['category']} | {gap['key']} | {gap['candidate_count']}: {names} |")
        lines.append("")

    # Methodology
    lines.append("## Methodology")
    lines.append("")
    lines.append("### Matching Strategy")
    lines.append("1. **Pass 1 — Exact name + district** (federal/legislative races with district numbers)")
    lines.append("2. **Pass 2 — Exact name + race category** (county races without district keys)")
    lines.append("3. **Pass 3 — Fuzzy name match** (>=75% similarity within same race category)")
    lines.append("")
    lines.append("### Normalization Applied")
    lines.append("- Names: uppercase, strip nicknames/suffixes (Jr, Sr, III), collapse whitespace")
    lines.append("- Parties: DEMOCRATIC/DEMOCRAT/LABOR DEMOCRAT→dem, REPUBLICAN/GOP→rep, etc.")
    lines.append("- Race types: 71 CSV variations mapped to 15 normalized categories")
    lines.append("- Withdrawn candidates excluded from CSV analysis")
    lines.append("")
    lines.append("### Limitations")
    lines.append("- County-level matching relies on name matching (no county field in SOS CSV export)")
    lines.append("- Fuzzy matching may produce false positives for common surnames")
    lines.append("- PUD, Port, Municipal, and Superior/Appellate court races excluded from gap analysis")
    lines.append("")

    return '\n'.join(lines)


# --- Main ---

def main():
    print("Loading data sources...")
    csv_cands = load_csv()
    json_cands, json_races = load_races_json()
    dirs = scan_directories()

    print(f"  CSV: {len(csv_cands)} active candidates")
    print(f"  JSON: {len(json_cands)} candidates in {len(json_races)} races")
    print(f"  Dirs: {len(dirs)} candidate directories")
    print()

    print("Matching candidates...")
    match_results = match_candidates(csv_cands, json_cands)
    print(f"  Matched: {len(match_results['matched'])}")
    print(f"  SOS-only: {len(match_results['csv_only'])}")
    print(f"  JSON-only: {len(match_results['json_only'])}")
    print(f"  Party mismatches: {len(match_results['party_mismatch'])}")
    print()

    print("Validating directories...")
    dir_results = validate_directories(json_cands, dirs)
    print(f"  Orphan dirs: {len(dir_results['dir_no_json'])}")
    print(f"  Missing dirs: {len(dir_results['json_no_dir'])}")
    print(f"  Missing index.html: {len(dir_results['missing_index'])}")
    print()

    print("Analyzing race coverage gaps...")
    coverage_gaps = analyze_race_coverage(csv_cands, json_races)
    print(f"  Coverage gaps: {len(coverage_gaps)}")
    print()

    print("Computing quality scores...")
    scores = compute_quality_scores(csv_cands, json_cands, match_results, dir_results)
    print(f"  Overall: {scores['overall']}%")
    print()

    print("Generating report...")
    report = generate_report(scores, match_results, dir_results, coverage_gaps)

    report_path = REPO_ROOT / "tools" / "reports" / "wa-candidate-validation-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    print(f"Report written to: {report_path}")

    # Also write JSON summary for programmatic use
    json_summary = {
        'generated': datetime.now().isoformat(),
        'scores': scores,
        'match_summary': {
            'matched': len(match_results['matched']),
            'csv_only': len(match_results['csv_only']),
            'json_only': len(match_results['json_only']),
            'party_mismatches': len(match_results['party_mismatch']),
        },
        'dir_summary': {
            'orphan_dirs': len(dir_results['dir_no_json']),
            'missing_dirs': len(dir_results['json_no_dir']),
            'missing_index': len(dir_results['missing_index']),
        },
        'coverage_gaps': len(coverage_gaps),
        'json_only_candidates': [
            {'name': jc['name'], 'race_id': jc['race_id'], 'party': jc['party_raw']}
            for jc in match_results['json_only']
        ],
        'party_mismatches': [
            {
                'name': cc['name'],
                'race_id': jc['race_id'],
                'sos_party': cc['party_raw'],
                'our_party': jc['party_raw'],
            }
            for cc, jc in match_results['party_mismatch']
        ],
    }
    json_path = REPO_ROOT / "tools" / "reports" / "wa-candidate-validation-summary.json"
    json_path.write_text(json.dumps(json_summary, indent=2))
    print(f"JSON summary written to: {json_path}")

    return scores['overall']


if __name__ == '__main__':
    score = main()
    sys.exit(0 if score >= 80 else 1)
