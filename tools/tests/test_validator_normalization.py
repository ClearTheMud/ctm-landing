#!/usr/bin/env python3
"""TDD tests for validate_candidates.py normalization — Bug #1755.

The JSON race normalizer must correctly categorize:
1. "Clerk of Superior Court" as Clerk, not Other
2. "District Court" variants as District Court Judge
3. County prosecutor/prosecuting attorney as matching categories
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from validate_candidates import (
    map_json_race_to_category,
    normalize_race_type,
    normalize_party_csv,
    normalize_party_json,
    normalize_name,
    name_similarity,
)


class TestMapJsonRaceToCategory:
    """Tests for JSON race → category mapping."""

    def _make_race(self, office, race_id):
        return {"office": office, "id": race_id}

    def test_clerk_of_superior_court_maps_to_clerk(self):
        race = self._make_race("Clerk Of Superior Court", "wa-douglas-clerk-of-superior-court-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "Clerk"

    def test_plain_clerk_maps_to_clerk(self):
        race = self._make_race("Clerk", "wa-adams-clerk-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "Clerk"

    def test_county_clerk_maps_to_clerk(self):
        race = self._make_race("County Clerk", "wa-clark-county-clerk-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "Clerk"

    def test_district_court_not_confused_with_clerk(self):
        race = self._make_race("District Court Judge", "wa-adams-district-court-judge-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "District Court Judge"

    def test_district_court_hash_format(self):
        race = self._make_race("District Court #1", "wa-grays-harbor-district-court-1-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "District Court Judge"
        assert key == "1"

    def test_district_court_position_format(self):
        race = self._make_race("District Court Judge Position 1", "wa-adams-district-court-judge-position-1-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "District Court Judge"
        assert key == "1"

    def test_district_court_pos_dot_format(self):
        race = self._make_race("District Court Judge Pos. 3", "wa-thurston-district-court-judge-pos-3-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "District Court Judge"
        assert key == "3"

    def test_us_house(self):
        race = self._make_race("US House", "wa-house-5-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "US House"
        assert key == "5"

    def test_state_senate(self):
        race = self._make_race("State Senate", "wa-state-senate-13-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "State Senate"
        assert key == "13"

    def test_prosecuting_attorney(self):
        race = self._make_race("Prosecuting Attorney", "wa-adams-prosecuting-attorney-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "Prosecuting Attorney"

    def test_prosecutor_maps_to_prosecuting_attorney(self):
        """Prosecutor and Prosecuting Attorney normalize to same category for matching."""
        race = self._make_race("Prosecutor", "wa-adams-prosecutor-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "Prosecuting Attorney"

    def test_county_prosecuting_attorney(self):
        race = self._make_race("County Prosecuting Attorney", "wa-clark-county-prosecuting-attorney-2026")
        cat, key = map_json_race_to_category(race)
        assert cat == "Prosecuting Attorney"


class TestNormalizeRaceTypeCSV:
    """Tests for CSV race type normalization."""

    def test_clerk_of_superior_court_csv(self):
        cat, key = normalize_race_type("Countywide", "Clerk of Superior Court", "County")
        assert cat == "Clerk"

    def test_district_court_hash_csv(self):
        cat, key = normalize_race_type("Countywide", "District Court #1", "County")
        assert cat == "District Court Judge"
        assert key == "1"


class TestNormalizePartyJSON:
    """Tests for races.json party normalization."""

    def test_single_letter_D(self):
        assert normalize_party_json("D") == "dem"

    def test_single_letter_R(self):
        assert normalize_party_json("R") == "rep"

    def test_single_letter_I(self):
        assert normalize_party_json("I") == "ind"

    def test_word_dem(self):
        assert normalize_party_json("dem") == "dem"

    def test_word_rep(self):
        assert normalize_party_json("rep") == "rep"

    def test_NP(self):
        assert normalize_party_json("NP") == "nonpartisan"

    def test_nonpartisan(self):
        assert normalize_party_json("nonpartisan") == "nonpartisan"

    def test_cascade(self):
        assert normalize_party_json("Cascade") == "cascade"

    def test_empty_string(self):
        assert normalize_party_json("") == "nonpartisan"


class TestNormalizePartyCSV:
    """Tests for CSV party normalization."""

    def test_democratic(self):
        assert normalize_party_csv("DEMOCRATIC") == "dem"

    def test_democrat(self):
        assert normalize_party_csv("DEMOCRAT") == "dem"

    def test_republican(self):
        assert normalize_party_csv("REPUBLICAN") == "rep"

    def test_gop(self):
        assert normalize_party_csv("GOP") == "rep"

    def test_typo_repubilcan(self):
        assert normalize_party_csv("REPUBILCAN") == "rep"

    def test_typo_independant(self):
        assert normalize_party_csv("INDEPENDANT") == "ind"

    def test_empty_is_nonpartisan(self):
        assert normalize_party_csv("") == "nonpartisan"

    def test_states_no_party(self):
        assert normalize_party_csv("STATES NO PARTY PREFERENCE") == "nonpartisan"


class TestNameSimilarity:
    """Tests for fuzzy name matching."""

    def test_identical_names(self):
        assert name_similarity("John Smith", "John Smith") == 1.0

    def test_case_insensitive(self):
        assert name_similarity("john smith", "JOHN SMITH") == 1.0

    def test_suffix_stripped(self):
        assert name_similarity("Kenneth Spencer Jr", "Kenneth Spencer") >= 0.85

    def test_nickname_stripped(self):
        assert name_similarity('John "Jack" Smith', "John Smith") >= 0.85

    def test_different_names_low_score(self):
        assert name_similarity("John Smith", "Jane Doe") < 0.5
