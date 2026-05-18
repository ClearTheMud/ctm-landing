#!/usr/bin/env python3
"""TDD tests for candidate name parsing — Bug #1750.

The name-to-directory-slug function must:
1. Extract the actual surname, not suffixes (Jr, Sr, III, II, IV)
2. Preserve hyphenated surnames intact (Burton-Crow → burton-crow)
3. Handle quoted nicknames ("Jack") without breaking
4. Handle edge cases: single names, all-caps, mixed case
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from update_races import candidate_slug


class TestCandidateSlug:
    """Tests for the candidate_slug function (name → directory slug)."""

    # --- Suffix handling ---

    def test_strips_jr_suffix(self):
        assert candidate_slug("Kenneth Spencer Jr") == "spencer"

    def test_strips_jr_with_period(self):
        assert candidate_slug("Kenneth Spencer Jr.") == "spencer"

    def test_strips_sr_suffix(self):
        assert candidate_slug("James Wilson Sr") == "wilson"

    def test_strips_iii_suffix(self):
        assert candidate_slug("David T Lewis III") == "lewis"

    def test_strips_ii_suffix(self):
        assert candidate_slug("Robert Hall II") == "hall"

    def test_strips_iv_suffix(self):
        assert candidate_slug("Thomas Reed IV") == "reed"

    def test_strips_jr_uppercase(self):
        assert candidate_slug("Darryl Chepoda JR") == "chepoda"

    def test_jr_with_comma(self):
        assert candidate_slug("Bruce D. Wilkinson, Jr.") == "wilkinson"

    def test_jr_with_comma_in_middle(self):
        assert candidate_slug("Fa'amomoi Masaniai, Jr.") == "masaniai"

    # --- Hyphenated surnames ---

    def test_hyphenated_surname_preserved(self):
        assert candidate_slug("Kevin Burton-Crow") == "burton-crow"

    def test_hyphenated_with_middle_name(self):
        assert candidate_slug("Tillie Naputi-Pullar") == "naputi-pullar"

    def test_hyphenated_three_parts(self):
        assert candidate_slug("Nicolas Martinez-Dunning") == "martinez-dunning"

    def test_hyphenated_with_suffix(self):
        assert candidate_slug("Jack Griffin-Smith Jr") == "griffin-smith"

    def test_double_hyphenated(self):
        assert candidate_slug("Emily Lybbert-Hansen") == "lybbert-hansen"

    def test_hyphenated_with_middle_initial(self):
        assert candidate_slug("Janelle Carman-Wagner") == "carman-wagner"

    def test_hyphenated_with_prefix(self):
        assert candidate_slug("Carolyn Jewett-Platts") == "jewett-platts"

    def test_hyphenated_three_name_surname(self):
        assert candidate_slug("Jeremy Harrison-Smith") == "harrison-smith"

    # --- Quoted nicknames ---

    def test_quoted_nickname_ignored(self):
        assert candidate_slug('John W "Jack" Smith') == "smith"

    def test_parenthetical_nickname_ignored(self):
        assert candidate_slug("Richard (Rick) Viall") == "viall"

    def test_quoted_nickname_with_suffix(self):
        assert candidate_slug('Roy C. "Dewey" Holliday Jr.') == "holliday"

    # --- Standard cases ---

    def test_simple_two_part_name(self):
        assert candidate_slug("John Smith") == "smith"

    def test_three_part_name(self):
        assert candidate_slug("Marie Gluesenkamp Perez") == "perez"

    def test_middle_initial(self):
        assert candidate_slug("John P. Roco") == "roco"

    def test_all_caps_name(self):
        assert candidate_slug("ANDREW POOLER") == "pooler"

    def test_single_name(self):
        assert candidate_slug("Prince") == "prince"

    # --- Lowercase output ---

    def test_output_always_lowercase(self):
        assert candidate_slug("Suzan DelBene") == "delbene"

    def test_mixed_case_hyphenated(self):
        assert candidate_slug("Kevin Burton-Crow") == "burton-crow"
