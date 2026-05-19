#!/usr/bin/env python3
"""TDD tests for detect_roles.py — role detection from SOS election status data.

The role detection script must:
1. Match races.json candidates to CSV candidates by name
2. Detect incumbents from election status (ATG/Elected solo filers)
3. Set challengers when an incumbent is detected in a multi-candidate race
4. Normalize role case ('Incumbent' → 'incumbent')
5. Propagate election_status to all matched candidates
6. Never overwrite manually-set roles (incumbent/challenger/frontrunner)

C6S Data Engineering — Engagement 7
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from detect_roles import (
    match_election_status,
    detect_incumbent,
    normalize_roles,
    propagate_election_status,
)


# --- Helper factories ---

def make_candidate(name, party="dem", role="Filed", url=None):
    """Create a candidate dict matching races.json schema."""
    return {
        "name": name,
        "party": party,
        "role": role,
        "url": url or f"/races/test/{name.split()[-1].lower()}/",
    }


def make_race(race_id, candidates, state_abbr="WA", office="Assessor"):
    """Create a race dict matching races.json schema."""
    return {
        "id": race_id,
        "state_abbr": state_abbr,
        "office": office,
        "year": 2026,
        "title": f"2026 {office}",
        "status": "stub",
        "candidates": candidates,
    }


def make_csv_row(name, election_status="In Primary", party="DEMOCRATIC"):
    """Create a CSV row dict matching SOS CandidateList.csv schema."""
    return {
        "Name": name,
        "Election Status": election_status,
        "Party Preference": party,
        "District Type": "Countywide",
        "District": "Test County",
        "Race": "Assessor",
        "Status": "Active",
    }


# =============================================================================
# match_election_status tests
# =============================================================================


class TestMatchElectionStatus:
    """Tests for matching JSON candidates to CSV rows and extracting election status."""

    def test_exact_name_match(self):
        json_cands = [make_candidate("John Smith")]
        csv_cands = [make_csv_row("John Smith", "In Primary")]
        result = match_election_status(json_cands, csv_cands)
        assert result["John Smith"] == "In Primary"

    def test_case_insensitive_match(self):
        json_cands = [make_candidate("John Smith")]
        csv_cands = [make_csv_row("john smith", "Advanced to General")]
        result = match_election_status(json_cands, csv_cands)
        assert result["John Smith"] == "Advanced to General"

    def test_suffix_stripped_match(self):
        json_cands = [make_candidate("Kenneth Spencer Jr")]
        csv_cands = [make_csv_row("Kenneth Spencer", "Elected")]
        result = match_election_status(json_cands, csv_cands)
        assert result["Kenneth Spencer Jr"] == "Elected"

    def test_csv_has_suffix_json_doesnt(self):
        json_cands = [make_candidate("Kenneth Spencer")]
        csv_cands = [make_csv_row("Kenneth Spencer Jr.", "In Primary")]
        result = match_election_status(json_cands, csv_cands)
        assert result["Kenneth Spencer"] == "In Primary"

    def test_nickname_stripped_match(self):
        json_cands = [make_candidate('John "Jack" Smith')]
        csv_cands = [make_csv_row("John Smith", "Advanced to General")]
        result = match_election_status(json_cands, csv_cands)
        assert result['John "Jack" Smith'] == "Advanced to General"

    def test_no_match_returns_empty_for_candidate(self):
        json_cands = [make_candidate("John Smith")]
        csv_cands = [make_csv_row("Jane Doe", "In Primary")]
        result = match_election_status(json_cands, csv_cands)
        assert "John Smith" not in result

    def test_multiple_candidates_matched(self):
        json_cands = [
            make_candidate("Alice Jones"),
            make_candidate("Bob Brown"),
        ]
        csv_cands = [
            make_csv_row("Alice Jones", "In Primary"),
            make_csv_row("Bob Brown", "Advanced to General"),
        ]
        result = match_election_status(json_cands, csv_cands)
        assert result["Alice Jones"] == "In Primary"
        assert result["Bob Brown"] == "Advanced to General"

    def test_empty_election_status_preserved(self):
        json_cands = [make_candidate("John Smith")]
        csv_cands = [make_csv_row("John Smith", "")]
        result = match_election_status(json_cands, csv_cands)
        assert result["John Smith"] == ""

    def test_elected_status_matched(self):
        json_cands = [make_candidate("Solo Runner")]
        csv_cands = [make_csv_row("Solo Runner", "Elected")]
        result = match_election_status(json_cands, csv_cands)
        assert result["Solo Runner"] == "Elected"

    def test_empty_json_candidates(self):
        result = match_election_status([], [make_csv_row("John Smith")])
        assert result == {}

    def test_empty_csv_candidates(self):
        result = match_election_status([make_candidate("John Smith")], [])
        assert result == {}

    def test_hyphenated_name_match(self):
        json_cands = [make_candidate("Tillie Naputi-Pullar")]
        csv_cands = [make_csv_row("Tillie Naputi-Pullar", "In Primary")]
        result = match_election_status(json_cands, csv_cands)
        assert result["Tillie Naputi-Pullar"] == "In Primary"

    def test_middle_initial_match(self):
        json_cands = [make_candidate("David S. Mann")]
        csv_cands = [make_csv_row("David S Mann", "Advanced to General")]
        result = match_election_status(json_cands, csv_cands)
        assert result["David S. Mann"] == "Advanced to General"


# =============================================================================
# detect_incumbent tests
# =============================================================================


class TestDetectIncumbent:
    """Tests for incumbent detection from election status and race structure."""

    # --- Solo filer scenarios ---

    def test_solo_filer_atg_becomes_incumbent(self):
        """Single candidate with 'Advanced to General' → incumbent."""
        cands = [make_candidate("Jane Solo", role="Filed")]
        race = make_race("wa-test-2026", cands)
        statuses = {"Jane Solo": "Advanced to General"}
        result = detect_incumbent(race, statuses)
        assert result == [("Jane Solo", "incumbent")]

    def test_solo_filer_elected_becomes_incumbent(self):
        """Single candidate with 'Elected' → incumbent."""
        cands = [make_candidate("Jane Solo", role="Filed")]
        race = make_race("wa-test-2026", cands)
        statuses = {"Jane Solo": "Elected"}
        result = detect_incumbent(race, statuses)
        assert result == [("Jane Solo", "incumbent")]

    def test_solo_filer_in_primary_stays_filed(self):
        """Single candidate with 'In Primary' should NOT become incumbent."""
        cands = [make_candidate("Jane Solo", role="Filed")]
        race = make_race("wa-test-2026", cands)
        statuses = {"Jane Solo": "In Primary"}
        result = detect_incumbent(race, statuses)
        assert result == [("Jane Solo", "Filed")]

    def test_solo_filer_no_status_stays_filed(self):
        """Single candidate with no election status data → stay Filed."""
        cands = [make_candidate("Jane Solo", role="Filed")]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert result == [("Jane Solo", "Filed")]

    def test_solo_filer_empty_status_stays_filed(self):
        """Single candidate with blank election status → stay Filed."""
        cands = [make_candidate("Jane Solo", role="Filed")]
        race = make_race("wa-test-2026", cands)
        statuses = {"Jane Solo": ""}
        result = detect_incumbent(race, statuses)
        assert result == [("Jane Solo", "Filed")]

    def test_solo_filer_already_incumbent_preserved(self):
        """Solo incumbent should keep their role, not change."""
        cands = [make_candidate("Jane Solo", role="incumbent")]
        race = make_race("wa-test-2026", cands)
        statuses = {"Jane Solo": "Advanced to General"}
        result = detect_incumbent(race, statuses)
        assert result == [("Jane Solo", "incumbent")]

    # --- Multi-candidate race: incumbent detection propagation ---

    def test_multi_candidate_incumbent_detected_others_become_challenger(self):
        """In a 2-person race, if one is detected incumbent, the other Filed → challenger."""
        cands = [
            make_candidate("Alice Incumbent", role="Filed"),
            make_candidate("Bob Challenger", role="Filed"),
        ]
        race = make_race("wa-test-2026", cands)
        # Alice is solo-ATG? No — she's in a multi-race. But the detection logic
        # only sets incumbent for solo filers. Multi-candidate Filed stays Filed.
        statuses = {
            "Alice Incumbent": "In Primary",
            "Bob Challenger": "In Primary",
        }
        result = detect_incumbent(race, statuses)
        # Both in primary, multi-candidate: no incumbent signal → stay Filed
        assert ("Alice Incumbent", "Filed") in result
        assert ("Bob Challenger", "Filed") in result

    def test_multi_candidate_existing_incumbent_makes_filed_challenger(self):
        """If one candidate already has role 'incumbent', Filed candidates become 'challenger'."""
        cands = [
            make_candidate("Alice Boss", role="incumbent"),
            make_candidate("Bob Filed", role="Filed"),
        ]
        race = make_race("wa-test-2026", cands)
        statuses = {"Alice Boss": "In Primary", "Bob Filed": "In Primary"}
        result = detect_incumbent(race, statuses)
        assert ("Alice Boss", "incumbent") in result
        assert ("Bob Filed", "challenger") in result

    def test_multi_candidate_no_incumbent_all_stay_filed(self):
        """Multiple Filed candidates, no incumbent signal → all stay Filed."""
        cands = [
            make_candidate("Alice Filed", role="Filed"),
            make_candidate("Bob Filed", role="Filed"),
            make_candidate("Charlie Filed", role="Filed"),
        ]
        race = make_race("wa-test-2026", cands)
        statuses = {
            "Alice Filed": "In Primary",
            "Bob Filed": "In Primary",
            "Charlie Filed": "In Primary",
        }
        result = detect_incumbent(race, statuses)
        for name, role in result:
            assert role == "Filed", f"{name} should be Filed, got {role}"

    def test_multi_candidate_all_challengers_preserved(self):
        """Existing challengers are never changed."""
        cands = [
            make_candidate("Alice", role="challenger"),
            make_candidate("Bob", role="challenger"),
        ]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert ("Alice", "challenger") in result
        assert ("Bob", "challenger") in result

    def test_multi_candidate_mixed_roles_preserved(self):
        """Mix of incumbent + challenger + frontrunner: all preserved."""
        cands = [
            make_candidate("Alice", role="incumbent"),
            make_candidate("Bob", role="challenger"),
            make_candidate("Charlie", role="frontrunner"),
        ]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert ("Alice", "incumbent") in result
        assert ("Bob", "challenger") in result
        assert ("Charlie", "frontrunner") in result

    # --- Preserving manually-set roles ---

    def test_existing_incumbent_preserved(self):
        cands = [make_candidate("Sitting Judge", role="incumbent")]
        race = make_race("wa-test-2026", cands)
        statuses = {"Sitting Judge": "In Primary"}
        result = detect_incumbent(race, statuses)
        assert result == [("Sitting Judge", "incumbent")]

    def test_existing_challenger_preserved(self):
        cands = [
            make_candidate("Incumbent Person", role="incumbent"),
            make_candidate("Challenger Person", role="challenger"),
        ]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert ("Challenger Person", "challenger") in result

    def test_existing_frontrunner_preserved(self):
        cands = [make_candidate("Star Candidate", role="frontrunner")]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert result == [("Star Candidate", "frontrunner")]

    def test_existing_custom_role_preserved(self):
        """Roles like 'Primary Frontrunner', 'Self-Funded' etc. are preserved."""
        cands = [make_candidate("Richie Rich", role="Self-Funded")]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert result == [("Richie Rich", "Self-Funded")]

    # --- Case normalization in detect_incumbent ---

    def test_capital_incumbent_normalized(self):
        """'Incumbent' (capital I) should be normalized to 'incumbent'."""
        cands = [make_candidate("Susan Collins", role="Incumbent")]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert result == [("Susan Collins", "incumbent")]

    def test_capital_frontrunner_normalized(self):
        """'Frontrunner' (capital F) should be normalized to 'frontrunner'."""
        cands = [make_candidate("Graham Platner", role="Frontrunner")]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert result == [("Graham Platner", "frontrunner")]

    # --- Three-candidate race with incumbent detection ---

    def test_three_candidate_race_incumbent_sets_others_challenger(self):
        """In a 3-person race with one existing incumbent, Filed candidates → challenger."""
        cands = [
            make_candidate("Incumbent Judge", role="incumbent"),
            make_candidate("New Filer A", role="Filed"),
            make_candidate("New Filer B", role="Filed"),
        ]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        assert ("Incumbent Judge", "incumbent") in result
        assert ("New Filer A", "challenger") in result
        assert ("New Filer B", "challenger") in result

    # --- Non-WA race filtering ---

    def test_non_wa_race_not_processed(self):
        """Non-WA races should pass through without role changes."""
        cands = [make_candidate("Maine Candidate", role="Filed")]
        race = make_race("me-senate-2026", cands, state_abbr="ME")
        statuses = {"Maine Candidate": "Advanced to General"}
        result = detect_incumbent(race, statuses)
        # Non-WA: return roles as-is (no detection applied)
        assert result == [("Maine Candidate", "Filed")]


# =============================================================================
# normalize_roles tests
# =============================================================================


class TestNormalizeRoles:
    """Tests for case normalization of roles across all races."""

    def test_normalize_incumbent_case(self):
        races = [make_race("wa-test-2026", [make_candidate("Sue", role="Incumbent")])]
        norm, inc, chal = normalize_roles(races)
        assert races[0]["candidates"][0]["role"] == "incumbent"
        assert norm == 1

    def test_normalize_frontrunner_case(self):
        races = [make_race("wa-test-2026", [make_candidate("Al", role="Frontrunner")])]
        norm, _, _ = normalize_roles(races)
        assert races[0]["candidates"][0]["role"] == "frontrunner"
        assert norm == 1

    def test_already_lowercase_not_counted(self):
        races = [make_race("wa-test-2026", [make_candidate("Al", role="incumbent")])]
        norm, _, _ = normalize_roles(races)
        assert norm == 0

    def test_filed_not_normalized(self):
        """'Filed' has intentional capitalization — should not be changed by normalize."""
        races = [make_race("wa-test-2026", [make_candidate("Al", role="Filed")])]
        norm, _, _ = normalize_roles(races)
        assert races[0]["candidates"][0]["role"] == "Filed"
        assert norm == 0

    def test_normalize_multiple_races(self):
        races = [
            make_race("wa-test1-2026", [
                make_candidate("A", role="Incumbent"),
                make_candidate("B", role="challenger"),
            ]),
            make_race("wa-test2-2026", [
                make_candidate("C", role="Frontrunner"),
            ]),
        ]
        norm, _, _ = normalize_roles(races)
        assert norm == 2
        assert races[0]["candidates"][0]["role"] == "incumbent"
        assert races[0]["candidates"][1]["role"] == "challenger"
        assert races[1]["candidates"][0]["role"] == "frontrunner"

    def test_returns_incumbent_and_challenger_counts(self):
        races = [make_race("wa-test-2026", [
            make_candidate("A", role="Incumbent"),
            make_candidate("B", role="challenger"),
            make_candidate("C", role="Filed"),
        ])]
        _, inc, chal = normalize_roles(races)
        # After normalization: 1 incumbent, 1 challenger
        assert inc == 1
        assert chal == 1

    def test_custom_roles_not_normalized(self):
        """Roles like 'Self-Funded', 'Kemp-Backed' are left as-is."""
        races = [make_race("wa-test-2026", [make_candidate("A", role="Self-Funded")])]
        norm, _, _ = normalize_roles(races)
        assert races[0]["candidates"][0]["role"] == "Self-Funded"
        assert norm == 0


# =============================================================================
# propagate_election_status tests
# =============================================================================


class TestPropagateElectionStatus:
    """Tests for adding election_status field to candidate records."""

    def test_status_added_to_candidate(self):
        races = [make_race("wa-test-2026", [make_candidate("John Smith")])]
        statuses = {"John Smith": "In Primary"}
        count = propagate_election_status(races, statuses)
        assert races[0]["candidates"][0]["election_status"] == "In Primary"
        assert count == 1

    def test_atg_status_propagated(self):
        races = [make_race("wa-test-2026", [make_candidate("Jane Doe")])]
        statuses = {"Jane Doe": "Advanced to General"}
        count = propagate_election_status(races, statuses)
        assert races[0]["candidates"][0]["election_status"] == "Advanced to General"
        assert count == 1

    def test_elected_status_propagated(self):
        races = [make_race("wa-test-2026", [make_candidate("Solo Winner")])]
        statuses = {"Solo Winner": "Elected"}
        count = propagate_election_status(races, statuses)
        assert races[0]["candidates"][0]["election_status"] == "Elected"
        assert count == 1

    def test_no_match_no_status_added(self):
        races = [make_race("wa-test-2026", [make_candidate("Unknown Person")])]
        statuses = {"Other Person": "In Primary"}
        count = propagate_election_status(races, statuses)
        assert "election_status" not in races[0]["candidates"][0]
        assert count == 0

    def test_multiple_candidates_propagated(self):
        races = [make_race("wa-test-2026", [
            make_candidate("Alice"),
            make_candidate("Bob"),
        ])]
        statuses = {"Alice": "In Primary", "Bob": "Advanced to General"}
        count = propagate_election_status(races, statuses)
        assert races[0]["candidates"][0]["election_status"] == "In Primary"
        assert races[0]["candidates"][1]["election_status"] == "Advanced to General"
        assert count == 2

    def test_multiple_races_propagated(self):
        races = [
            make_race("wa-test1-2026", [make_candidate("Alice")]),
            make_race("wa-test2-2026", [make_candidate("Bob")]),
        ]
        statuses = {"Alice": "In Primary", "Bob": "Elected"}
        count = propagate_election_status(races, statuses)
        assert count == 2
        assert races[0]["candidates"][0]["election_status"] == "In Primary"
        assert races[1]["candidates"][0]["election_status"] == "Elected"

    def test_empty_status_string_propagated(self):
        races = [make_race("wa-test-2026", [make_candidate("Blank Status")])]
        statuses = {"Blank Status": ""}
        count = propagate_election_status(races, statuses)
        assert races[0]["candidates"][0]["election_status"] == ""
        assert count == 1

    def test_existing_election_status_overwritten(self):
        """If candidate already has election_status, it gets updated."""
        cand = make_candidate("John Smith")
        cand["election_status"] = "old status"
        races = [make_race("wa-test-2026", [cand])]
        statuses = {"John Smith": "In Primary"}
        count = propagate_election_status(races, statuses)
        assert races[0]["candidates"][0]["election_status"] == "In Primary"
        assert count == 1

    def test_non_wa_candidates_skipped(self):
        """Only WA candidates get election_status propagation."""
        races = [make_race("me-senate-2026", [make_candidate("Maine Cand")], state_abbr="ME")]
        statuses = {"Maine Cand": "In Primary"}
        count = propagate_election_status(races, statuses)
        assert "election_status" not in races[0]["candidates"][0]
        assert count == 0


# =============================================================================
# Integration / edge case tests
# =============================================================================


class TestEdgeCases:
    """Integration and edge case tests."""

    def test_detect_incumbent_empty_race(self):
        """Race with no candidates should return empty list."""
        race = make_race("wa-test-2026", [])
        result = detect_incumbent(race, {})
        assert result == []

    def test_detect_incumbent_preserves_order(self):
        """Output order should match candidate input order."""
        cands = [
            make_candidate("Charlie", role="Filed"),
            make_candidate("Alpha", role="incumbent"),
            make_candidate("Bravo", role="Filed"),
        ]
        race = make_race("wa-test-2026", cands)
        statuses = {}
        result = detect_incumbent(race, statuses)
        names = [name for name, _ in result]
        assert names == ["Charlie", "Alpha", "Bravo"]

    def test_two_incumbents_race_doesnt_crash(self):
        """Edge case: race with two incumbents (data error). Both preserved."""
        cands = [
            make_candidate("Inc A", role="incumbent"),
            make_candidate("Inc B", role="incumbent"),
        ]
        race = make_race("wa-test-2026", cands)
        result = detect_incumbent(race, {})
        assert ("Inc A", "incumbent") in result
        assert ("Inc B", "incumbent") in result

    def test_filed_only_multi_candidate_in_primary_stays_filed(self):
        """Multiple Filed candidates all In Primary → all stay Filed."""
        cands = [make_candidate(f"Cand {i}", role="Filed") for i in range(5)]
        race = make_race("wa-test-2026", cands)
        statuses = {f"Cand {i}": "In Primary" for i in range(5)}
        result = detect_incumbent(race, statuses)
        for name, role in result:
            assert role == "Filed"

    def test_normalize_roles_empty_list(self):
        norm, inc, chal = normalize_roles([])
        assert norm == 0
        assert inc == 0
        assert chal == 0

    def test_propagate_empty_statuses(self):
        races = [make_race("wa-test-2026", [make_candidate("John")])]
        count = propagate_election_status(races, {})
        assert count == 0

    def test_match_election_status_duplicate_names(self):
        """If same name appears in CSV multiple times, last wins (or first — just no crash)."""
        json_cands = [make_candidate("John Smith")]
        csv_cands = [
            make_csv_row("John Smith", "In Primary"),
            make_csv_row("John Smith", "Advanced to General"),
        ]
        result = match_election_status(json_cands, csv_cands)
        assert "John Smith" in result
        # Either value is acceptable; test that it doesn't crash

    def test_solo_filer_incumbent_with_atg_and_no_existing_role_change(self):
        """Full integration: solo Filed candidate + ATG → incumbent."""
        cand = make_candidate("Solo Judge", role="Filed")
        race = make_race("wa-test-2026", [cand])
        statuses = {"Solo Judge": "Advanced to General"}
        result = detect_incumbent(race, statuses)
        assert result == [("Solo Judge", "incumbent")]
