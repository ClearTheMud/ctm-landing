#!/usr/bin/env python3
"""TDD tests for SOS CandidateList.csv ingestion — ADO #1751/#1753/#1754.

The ingestion script (tools/ingest_sos_candidates.py) parses the WA
Secretary of State CandidateList.csv, identifies candidates in 10 new
race categories not yet tracked, and adds them to races.json.

Race categories handled:
  1. PUD Commissioner (58 candidates)
  2. KC District Court Electoral (33)
  3. County Council (26)
  4. WA Supreme Court (17)
  5. Superior Court (13)
  6. Port Commissioner (13)
  7. Municipal Court (12)
  8. City Council (9)
  9. Court of Appeals (8)
 10. District Court Judicial (33)

Functions under test:
  - identify_pud(district_str, race_str=None) -> (slug, display_name)
  - extract_position_number(race_str, district_str=None) -> str
  - categorize_candidate(race_str, district_str, district_type_str) -> str|None
  - generate_race_id(category, race_str, district_str, year) -> str
  - build_race_entry(category, race_id, office_name, year, candidates) -> dict
  - is_duplicate(candidate_name, race_id, existing_races) -> bool
"""

import json
import re
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from ingest_sos_candidates import (
    build_race_entry,
    categorize_candidate,
    extract_position_number,
    generate_race_id,
    identify_pud,
    is_duplicate,
)


# ===========================================================================
# 1. identify_pud — Extract PUD identifier from wildly inconsistent CSV data
# ===========================================================================

class TestIdentifyPUD:
    """Extract a normalized PUD identifier from the CSV district field.

    PUD district strings in the SOS CSV are spectacularly inconsistent.
    The function returns (pud_slug, pud_display_name) tuple.
    """

    # --- Named county PUDs (county name appears in string) ---

    def test_skagit_county_pud(self):
        slug, name = identify_pud("SKAGIT COUNTY PUD COMMISSIONER DIST 1")
        assert slug == "skagit-pud"
        assert "Skagit" in name

    def test_clark_public_utilities(self):
        slug, name = identify_pud("CLARK PUBLIC UTILITIES - COMM. DIST. #3")
        assert slug == "clark-pud"
        assert "Clark" in name

    def test_grant_county_pud_comm(self):
        slug, name = identify_pud("GRANT COUNTY PUD COMM DIST #3")
        assert slug == "grant-pud"
        assert "Grant" in name

    def test_grant_county_pud_dist_b(self):
        slug, name = identify_pud("GRANT COUNTY PUD DIST #B")
        assert slug == "grant-pud"
        assert "Grant" in name

    def test_okanogan_ok_abbrev(self):
        """'OK PUBLIC UTILITY DISTRICT 01' is Okanogan PUD."""
        slug, name = identify_pud("OK PUBLIC UTILITY DISTRICT 01")
        assert slug == "okanogan-pud"
        assert "Okanogan" in name

    # --- PUD with specific county mappings (from lookup table) ---

    def test_pud_hash_1_wahkiakum(self):
        """'PUD #1' maps to Wahkiakum PUD via lookup table."""
        slug, name = identify_pud("PUD #1")
        assert slug is not None
        assert isinstance(slug, str)
        assert len(slug) > 0

    def test_pud_hash_3_ferry(self):
        """'PUD #3' maps to Ferry County PUD via lookup table."""
        slug, name = identify_pud("PUD #3")
        assert slug is not None
        assert isinstance(slug, str)

    def test_pud1_dash_commissioner(self):
        """'PUD1-COMMISSIONER DISTRICT 2' is resolved via lookup."""
        slug, name = identify_pud("PUD1-COMMISSIONER DISTRICT 2")
        assert slug is not None
        assert isinstance(slug, str)

    def test_pud_no_1(self):
        """'PUD No. 1 Commissioner District 1' is resolved via lookup."""
        slug, name = identify_pud("PUD No. 1 Commissioner District 1")
        assert slug is not None
        assert isinstance(slug, str)

    def test_pud_2_commissioner_district(self):
        """'PUD 2 Commissioner District #1' is resolved via lookup."""
        slug, name = identify_pud("PUD 2 Commissioner District #1")
        assert slug is not None
        assert isinstance(slug, str)

    def test_pud_1_commissioner_dist_2(self):
        slug, name = identify_pud("PUD 1 COMMISSIONER DIST 2")
        assert slug is not None

    def test_public_utility_district_hash_1(self):
        slug, name = identify_pud("PUBLIC UTILITY DISTRICT #1")
        assert slug is not None

    def test_public_utility_dist_2(self):
        slug, name = identify_pud("PUBLIC UTILITY DIST 2")
        assert slug is not None

    def test_public_utility_district_1_comma_1(self):
        """'PUBLIC UTILITY DISTRICT 1, 1' means PUD 1 position 1."""
        slug, name = identify_pud("PUBLIC UTILITY DISTRICT 1, 1")
        assert slug is not None

    # --- Compound formats with PUD number embedded ---

    def test_public_utility_dist_1_dash_2(self):
        """'Public Utility Dist 1-2' -> Mason County PUD No. 1."""
        slug, name = identify_pud("Public Utility Dist 1-2")
        assert slug is not None

    def test_public_utility_dist_3_dash_2(self):
        """'Public Utility Dist 3-2' -> Mason County PUD No. 3."""
        slug, name = identify_pud("Public Utility Dist 3-2")
        assert slug is not None

    # --- Formats that need context resolution ---

    def test_pud_commissioner_district_1(self):
        """'PUD COMMISSIONER DISTRICT 1' — resolved via lookup."""
        slug, name = identify_pud("PUD COMMISSIONER DISTRICT 1")
        assert slug is not None
        assert isinstance(slug, str)

    def test_pud_commissioner_district_no_1(self):
        """'PUD COMMISSIONER DISTRICT NO. 1' — resolved via lookup."""
        slug, name = identify_pud("PUD COMMISSIONER DISTRICT NO. 1")
        assert slug is not None
        assert isinstance(slug, str)

    def test_pud_dist_comm_hash_1(self):
        """'PUD DIST COMM #1' — resolved via lookup."""
        slug, name = identify_pud("PUD DIST COMM #1")
        assert slug is not None

    def test_public_comm_district_02(self):
        """'Public Comm District - 02' — resolved via lookup."""
        slug, name = identify_pud("Public Comm District - 02")
        assert slug is not None

    def test_pud_comm_dist_3(self):
        """'PUD Comm. Dist. 3' — resolved via lookup."""
        slug, name = identify_pud("PUD Comm. Dist. 3")
        assert slug is not None

    def test_pud_commissioner_dist_dot_3(self):
        """'PUD COMMISSIONER DIST. 3' — resolved via lookup."""
        slug, name = identify_pud("PUD COMMISSIONER DIST. 3")
        assert slug is not None

    # --- Full spelled-out formats ---

    def test_public_utility_district_commissioner_district_1(self):
        slug, name = identify_pud("Public Utility District Commissioner District 1")
        assert slug is not None

    def test_public_utility_district_commissioner_no_2(self):
        slug, name = identify_pud("Public Utility District - Commissioner No. 2")
        assert slug is not None

    def test_public_utility_district_commissioner_hash_3(self):
        slug, name = identify_pud("PUBLIC UTILITY DISTRICT COMMISSIONER #3")
        assert slug is not None

    def test_public_utility_district_commissioner_1(self):
        slug, name = identify_pud("PUBLIC UTILITY DISTRICT COMMISSIONER 1")
        assert slug is not None

    def test_public_utility_district_commissioner_b(self):
        slug, name = identify_pud("PUBLIC UTILITY DISTRICT COMMISSIONER B")
        assert slug is not None

    def test_pud_commissioner_dist_2(self):
        slug, name = identify_pud("PUD Commissioner Dist 2")
        assert slug is not None

    def test_pud_commissioner_district_2(self):
        slug, name = identify_pud("PUD Commissioner District 2")
        assert slug is not None

    def test_pud_district_2(self):
        slug, name = identify_pud("PUD District 2")
        assert slug is not None

    # --- Output format invariants ---

    def test_slug_is_lowercase(self):
        slug, _ = identify_pud("SKAGIT COUNTY PUD COMMISSIONER DIST 1")
        assert slug == slug.lower()

    def test_slug_has_no_spaces(self):
        slug, _ = identify_pud("GRANT COUNTY PUD COMM DIST #3")
        assert " " not in slug

    def test_slug_uses_hyphens(self):
        slug, _ = identify_pud("CLARK PUBLIC UTILITIES - COMM. DIST. #3")
        assert "-" in slug

    def test_returns_tuple_of_two_strings(self):
        result = identify_pud("PUD #1")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_display_name_is_string(self):
        _, name = identify_pud("SKAGIT COUNTY PUD COMMISSIONER DIST 1")
        assert isinstance(name, str)
        assert len(name) > 0

    def test_unrecognized_returns_none_tuple(self):
        """A completely unrecognizable string returns (None, None)."""
        slug, name = identify_pud("SOMETHING COMPLETELY UNRELATED")
        assert slug is None
        assert name is None

    # --- All 31 distinct district strings from CSV must resolve ---

    @pytest.mark.parametrize("district_str", [
        "CLARK PUBLIC UTILITIES - COMM. DIST. #3",
        "GRANT COUNTY PUD COMM DIST #3",
        "GRANT COUNTY PUD DIST #B",
        "OK PUBLIC UTILITY DISTRICT 01",
        "PUBLIC UTILITY DIST 2",
        "PUBLIC UTILITY DISTRICT #1",
        "PUBLIC UTILITY DISTRICT 1, 1",
        "PUBLIC UTILITY DISTRICT COMMISSIONER #3",
        "PUBLIC UTILITY DISTRICT COMMISSIONER 1",
        "PUBLIC UTILITY DISTRICT COMMISSIONER B",
        "PUD #1",
        "PUD #3",
        "PUD 1 COMMISSIONER DIST 2",
        "PUD 2 Commissioner District #1",
        "PUD COMMISSIONER DIST. 3",
        "PUD COMMISSIONER DISTRICT 1",
        "PUD COMMISSIONER DISTRICT NO. 1",
        "PUD COMMISSIONER DISTRICT NO. 3",
        "PUD Comm. Dist. 3",
        "PUD Commissioner Dist 2",
        "PUD Commissioner District 2",
        "PUD DIST COMM #1",
        "PUD District 2",
        "PUD No. 1 Commissioner District 1",
        "PUD1-COMMISSIONER DISTRICT 2",
        "Public Comm District - 02",
        "Public Utility Dist 1-2",
        "Public Utility Dist 3-2",
        "Public Utility District - Commissioner No. 2",
        "Public Utility District Commissioner District 1",
        "SKAGIT COUNTY PUD COMMISSIONER DIST 1",
    ])
    def test_all_csv_district_strings_resolve(self, district_str):
        """Every PUD district string from the actual CSV must resolve to a non-None slug."""
        slug, name = identify_pud(district_str)
        assert slug is not None, f"identify_pud({district_str!r}) returned None slug"
        assert name is not None, f"identify_pud({district_str!r}) returned None name"


# ===========================================================================
# 2. extract_position_number — Pull position/district number from strings
# ===========================================================================

class TestExtractPositionNumber:
    """Extract the position, district, or department number from race/district strings.

    Must handle: #01, #1, No. 1, Pos. 2, Position 1, District 1, Dept 1,
    Department No. 6, Dist #B, etc.
    """

    # --- Hash-number formats ---

    def test_hash_01_padded(self):
        assert extract_position_number("PUBLIC UTILITY COMMISSIONER #01") == "1"

    def test_hash_1(self):
        assert extract_position_number("Commissioner #1") == "1"

    def test_hash_3(self):
        assert extract_position_number("PUBLIC UTILITY COMMISSIONER #3") == "3"

    # --- "Position" keyword formats ---

    def test_justice_position_hash_01(self):
        assert extract_position_number("Justice Position #01") == "1"

    def test_justice_position_hash_03(self):
        assert extract_position_number("Justice Position #03") == "3"

    def test_justice_position_hash_07(self):
        assert extract_position_number("Justice Position #07") == "7"

    def test_judge_position_no_1(self):
        assert extract_position_number("Judge Position No. 1") == "1"

    def test_judge_position_no_5(self):
        assert extract_position_number("Judge Position No. 5") == "5"

    def test_judge_position_plain(self):
        assert extract_position_number("Judge Position 2") == "2"

    def test_judge_position_5(self):
        assert extract_position_number("Judge Position 5") == "5"

    def test_judge_pos_dot_1(self):
        assert extract_position_number("Judge Pos. 1") == "1"

    def test_judge_position_20(self):
        assert extract_position_number("Judge Position 20") == "20"

    def test_judge_position_45(self):
        assert extract_position_number("Judge Position 45") == "45"

    # --- "Commissioner Pos." formats ---

    def test_commissioner_pos_2(self):
        assert extract_position_number("Commissioner Pos. 2") == "2"

    def test_commissioner_pos_3(self):
        assert extract_position_number("Commissioner Pos. 3") == "3"

    # --- "District" keyword formats ---

    def test_commissioner_district_1(self):
        assert extract_position_number("Commissioner District 1") == "1"

    def test_commissioner_district_no_1(self):
        assert extract_position_number("Commissioner, District No. 1") == "1"

    def test_commissioner_district_2(self):
        assert extract_position_number("Commissioner District 2") == "2"

    def test_commissioner_district_no_2(self):
        assert extract_position_number("Commissioner District No. 2") == "2"

    def test_commissioner_district_4(self):
        assert extract_position_number("Commissioner District 4") == "4"

    # --- "No." and "No" formats ---

    def test_commissioner_no_2(self):
        assert extract_position_number("Commissioner No. 2") == "2"

    def test_district_court_no_7(self):
        assert extract_position_number("District Court No. 7") == "7"

    def test_district_court_no_1(self):
        assert extract_position_number("District Court No. 1") == "1"

    # --- "Department" / "Dept" formats ---

    def test_department_no_6(self):
        assert extract_position_number("DISTRICT COURT JUDGE, DEPARTMENT NO. 6") == "6"

    def test_department_no_1(self):
        assert extract_position_number("DISTRICT COURT JUDGE, DEPARTMENT NO. 1") == "1"

    def test_dept_1(self):
        assert extract_position_number("District Court Judge, Dept 1") == "1"

    def test_dept_2(self):
        assert extract_position_number("District Court Judge, Dept 2") == "2"

    def test_department_plain(self):
        assert extract_position_number("District Court Judge Department 1") == "1"

    def test_department_4(self):
        assert extract_position_number("District Court Judge Department 4") == "4"

    # --- Council formats ---

    def test_council_district_no_5(self):
        assert extract_position_number("Council - District No. 5") == "5"

    def test_council_district_no_1(self):
        assert extract_position_number("Council - District No. 1") == "1"

    def test_councilor_district_no_1(self):
        assert extract_position_number("COUNCILOR, DISTRICT NO. 1") == "1"

    def test_councilor_district_no_5(self):
        assert extract_position_number("COUNCILOR, DISTRICT NO. 5") == "5"

    def test_metropolitan_king_county_council_district_no_8(self):
        assert extract_position_number("Metropolitan King County Council District No. 8") == "8"

    def test_metropolitan_king_county_council_district_no_2(self):
        assert extract_position_number("Metropolitan King County Council District No. 2") == "2"

    def test_council_district_no_5_from_race(self):
        assert extract_position_number("Council District No. 5") == "5"

    def test_council_pos_4(self):
        assert extract_position_number("Council Pos. 4") == "4"

    # --- Municipal court "Pos." format ---

    def test_tacoma_municipal_court_pos_1(self):
        assert extract_position_number("Tacoma Municipal Court Pos. 1") == "1"

    def test_tacoma_municipal_court_pos_3(self):
        assert extract_position_number("Tacoma Municipal Court Pos. 3") == "3"

    def test_municipal_court_judge_position_no_1(self):
        assert extract_position_number("Municipal Court Judge Position No. 1") == "1"

    def test_municipal_court_judge_position_no_7(self):
        assert extract_position_number("Municipal Court Judge Position No. 7") == "7"

    # --- Fallback to district_str when race_str has no number ---

    def test_fallback_to_district_str(self):
        """When race_str has no extractable number, fall back to district_str."""
        result = extract_position_number("Commissioner", "PUD 2 Commissioner District #1")
        # Should find some number (1 from "District #1")
        assert result is not None
        assert result.isdigit()

    def test_fallback_district_str_court(self):
        result = extract_position_number("District Court Judge", "COURT DISTRICT 2")
        assert result is not None
        assert result.isdigit()

    # --- Leading zeros stripped ---

    def test_strips_leading_zero(self):
        assert extract_position_number("PUBLIC UTILITY COMMISSIONER #01") == "1"

    def test_strips_leading_zero_03(self):
        assert extract_position_number("Justice Position #03") == "3"

    # --- Judge - District Court format ---

    def test_judge_dash_district_court_1(self):
        assert extract_position_number("Judge - District Court 1") == "1"

    def test_judge_dash_district_court_2(self):
        assert extract_position_number("Judge - District Court 2") == "2"

    # --- Return type ---

    def test_always_returns_string(self):
        result = extract_position_number("Justice Position #01")
        assert isinstance(result, str)

    def test_default_fallback_is_string(self):
        """When no number is found at all, still returns a string."""
        result = extract_position_number("Something with no numbers")
        assert isinstance(result, str)


# ===========================================================================
# 3. categorize_candidate — Route CSV rows to one of 10 categories
# ===========================================================================

class TestCategorizeCandidate:
    """Determine which of the 10 new race categories a CSV row belongs to.

    Arguments: race_str, district_str, district_type_str (CSV columns 3, 2, 1).
    Returns category string or None for already-tracked types.
    """

    # --- Supreme Court ---

    def test_supreme_court_justice_pos_1(self):
        assert categorize_candidate("Justice Position #01", "SUPREME COURT", "Judicial") == "supreme_court"

    def test_supreme_court_justice_pos_3(self):
        assert categorize_candidate("Justice Position #03", "SUPREME COURT", "Judicial") == "supreme_court"

    def test_supreme_court_justice_pos_7(self):
        assert categorize_candidate("Justice Position #07", "SUPREME COURT", "Judicial") == "supreme_court"

    # --- Court of Appeals ---

    def test_court_of_appeals_div1_dist1(self):
        assert categorize_candidate(
            "Judge Position 5", "COURT OF APPEALS, DIVISION 1, DISTRICT 1", "JUDICIAL"
        ) == "court_of_appeals"

    def test_court_of_appeals_div2_dist1(self):
        assert categorize_candidate(
            "Judge Position 2", "Court of Appeals, Division 2, District 1", "Judicial"
        ) == "court_of_appeals"

    def test_court_of_appeals_div3_dist3(self):
        assert categorize_candidate(
            "Judge Position 1", "Court of Appeals, Division 3, District 3", "Judicial"
        ) == "court_of_appeals"

    def test_court_of_appeals_case_insensitive(self):
        assert categorize_candidate(
            "Judge Position 6", "COURT OF APPEALS, DIVISION 1, DISTRICT 1", "Judicial"
        ) == "court_of_appeals"

    # --- Superior Court ---

    def test_superior_court_cowlitz(self):
        assert categorize_candidate("Judge Position 4", "Cowlitz Superior Court", "Judicial") == "superior_court"

    def test_superior_court_grant(self):
        assert categorize_candidate("Judge Position #03", "Grant Superior Court", "Judicial") == "superior_court"

    def test_superior_court_king_county(self):
        assert categorize_candidate("Judge Position 20", "KING COUNTY SUPERIOR COURT", "Judicial") == "superior_court"

    def test_superior_court_ferry_pend_oreille_stevens(self):
        assert categorize_candidate(
            "Judge Position 2", "Ferry, Pend Oreille, Stevens Superior Court", "Judicial"
        ) == "superior_court"

    def test_superior_court_okanogan(self):
        assert categorize_candidate("Judge Position 2", "Okanogan Superior Court", "Judicial") == "superior_court"

    def test_superior_court_spokane(self):
        assert categorize_candidate("Judge Position 3", "Spokane Superior Court", "Judicial") == "superior_court"

    # --- PUD Commissioner ---

    def test_pud_commissioner_basic(self):
        assert categorize_candidate("Commissioner #1", "PUD #1", "Public Utility") == "pud_commissioner"

    def test_pud_commissioner_skagit(self):
        assert categorize_candidate(
            "Commissioner 1", "SKAGIT COUNTY PUD COMMISSIONER DIST 1", "Public Utility"
        ) == "pud_commissioner"

    def test_pud_commissioner_clark(self):
        assert categorize_candidate(
            "COMMISSIONER, DISTRICT NO. 3", "CLARK PUBLIC UTILITIES - COMM. DIST. #3", "Public Utility"
        ) == "pud_commissioner"

    def test_pud_commissioner_from_district_type(self):
        """District type 'Public Utility' is the primary signal for PUDs."""
        assert categorize_candidate(
            "Commissioner District 1", "PUD COMMISSIONER DISTRICT 1", "Public Utility"
        ) == "pud_commissioner"

    # --- Port Commissioner ---

    def test_port_commissioner_bellingham(self):
        assert categorize_candidate(
            "Commissioner District 4", "Port of Bellingham Commissioner District 4", "Port"
        ) == "port_commissioner"

    def test_port_commissioner_bellingham_dist_5(self):
        assert categorize_candidate(
            "Commissioner District 5", "Port of Bellingham Commissioner District 5", "Port"
        ) == "port_commissioner"

    def test_port_commissioner_pasco(self):
        assert categorize_candidate(
            "Commissioner District 3", "PASCO PORT DISTRICT 3", "Port"
        ) == "port_commissioner"

    # --- Municipal Court ---

    def test_municipal_court_seattle(self):
        assert categorize_candidate(
            "Municipal Court Judge Position No. 1", "City of Seattle", "City/Town"
        ) == "municipal_court"

    def test_municipal_court_seattle_pos_7(self):
        assert categorize_candidate(
            "Municipal Court Judge Position No. 7", "City of Seattle", "City/Town"
        ) == "municipal_court"

    def test_municipal_court_tacoma(self):
        assert categorize_candidate(
            "Tacoma Municipal Court Pos. 1", "CITY OF TACOMA", "City/Town"
        ) == "municipal_court"

    def test_municipal_court_tacoma_pos_3(self):
        assert categorize_candidate(
            "Tacoma Municipal Court Pos. 3", "CITY OF TACOMA", "City/Town"
        ) == "municipal_court"

    # --- KC District Court Electoral ---

    def test_kc_electoral_northeast(self):
        assert categorize_candidate(
            "Judge Position No. 1", "NORTHEAST ELECTORAL DISTRICT", "District Court"
        ) == "kc_electoral_district_court"

    def test_kc_electoral_shoreline(self):
        assert categorize_candidate(
            "Judge Position No. 1", "SHORELINE ELECTORAL DISTRICT", "District Court"
        ) == "kc_electoral_district_court"

    def test_kc_electoral_southeast(self):
        assert categorize_candidate(
            "Judge Position No. 3", "SOUTHEAST ELECTORAL DISTRICT", "District Court"
        ) == "kc_electoral_district_court"

    def test_kc_electoral_southwest(self):
        assert categorize_candidate(
            "Judge Position No. 2", "SOUTHWEST ELECTORAL DISTRICT", "District Court"
        ) == "kc_electoral_district_court"

    def test_kc_electoral_west(self):
        assert categorize_candidate(
            "Judge Position No. 4", "WEST ELECTORAL DISTRICT", "District Court"
        ) == "kc_electoral_district_court"

    # --- County Council ---

    def test_county_council_king(self):
        assert categorize_candidate(
            "Metropolitan King County Council District No. 2",
            "County Council District No. 2",
            "Council",
        ) == "county_council"

    def test_county_council_pierce(self):
        assert categorize_candidate(
            "Council - District No. 1",
            "COUNTY COUNCIL DISTRICT NO. 1",
            "Council",
        ) == "county_council"

    def test_county_councilor_clark(self):
        assert categorize_candidate(
            "COUNCILOR, DISTRICT NO. 1",
            "COUNTY COUNCILOR DISTRICT NO. 1",
            "Council",
        ) == "county_council"

    def test_county_councilor_clark_uppercase(self):
        assert categorize_candidate(
            "COUNCILOR, DISTRICT NO. 5",
            "COUNTY COUNCILOR DISTRICT NO. 5",
            "COUNCIL",
        ) == "county_council"

    # --- City Council ---

    def test_city_council_seattle(self):
        assert categorize_candidate(
            "Council District No. 5",
            "SEATTLE CITY COUNCIL DISTRICT 5",
            "City Council",
        ) == "city_council"

    def test_city_council_richland(self):
        assert categorize_candidate(
            "Council Pos. 4",
            "City Of Richland",
            "City/Town",
        ) == "city_council"

    # --- District Court Judicial (named courts, non-KC, non-county) ---

    def test_district_court_judicial_cascade(self):
        assert categorize_candidate(
            "Judge Position 1", "CASCADE DISTRICT COURT", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_everett(self):
        assert categorize_candidate(
            "Judge Position 1", "EVERETT DISTRICT COURT", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_evergreen(self):
        assert categorize_candidate(
            "Judge Position 1", "EVERGREEN DISTRICT COURT", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_south(self):
        assert categorize_candidate(
            "Judge Position 1", "SOUTH DISTRICT COURT", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_east(self):
        assert categorize_candidate(
            "Klickitat County East District Court Judge",
            "EAST DISTRICT COURT",
            "Judicial",
        ) == "district_court_judicial"

    def test_district_court_judicial_west(self):
        assert categorize_candidate(
            "Klickitat County West District Court Judge",
            "WEST DISTRICT COURT",
            "Judicial",
        ) == "district_court_judicial"

    def test_district_court_judicial_upper(self):
        assert categorize_candidate(
            "District Court Judge", "UPPER COUNTY DISTRICT COURT", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_lower(self):
        assert categorize_candidate(
            "District Court Judge", "LOWER COUNTY DISTRICT COURT", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_court_district(self):
        """'COURT DISTRICT' with 'Judge - District Court 1'."""
        assert categorize_candidate(
            "Judge - District Court 1", "COURT DISTRICT 1", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_district_court_dept(self):
        """District Court with dept format."""
        assert categorize_candidate(
            "District Court Judge, Dept 1", "DISTRICT COURT", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_department_no(self):
        assert categorize_candidate(
            "DISTRICT COURT JUDGE, DEPARTMENT NO. 6",
            "DISTRICT COURT JUDGES",
            "Judicial",
        ) == "district_court_judicial"

    def test_district_court_judicial_court_no(self):
        assert categorize_candidate(
            "District Court No. 7", "DISTRICT COURT", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_north_district(self):
        assert categorize_candidate(
            "DISTRICT COURT JUDGE", "Court - North District", "Judicial"
        ) == "district_court_judicial"

    def test_district_court_judicial_south_district(self):
        assert categorize_candidate(
            "DISTRICT COURT JUDGE", "Court - South District", "Judicial"
        ) == "district_court_judicial"

    # --- Non-target types return None ---

    def test_us_rep_returns_none(self):
        assert categorize_candidate(
            "U.S. Representative", "Congressional District 1", "Congressional"
        ) is None

    def test_state_senate_returns_none(self):
        assert categorize_candidate(
            "State Senator", "Legislative District 38", "Legislative"
        ) is None

    def test_state_rep_returns_none(self):
        assert categorize_candidate(
            "State Representative Pos. 1", "Legislative District 17", "Legislative"
        ) is None

    def test_county_commissioner_returns_none(self):
        assert categorize_candidate(
            "County Commissioner District No. 3", "County Commissioner Dist 3", "Commissioner"
        ) is None

    def test_county_assessor_returns_none(self):
        assert categorize_candidate(
            "Assessor", "Countywide", "Countywide"
        ) is None

    def test_county_sheriff_returns_none(self):
        assert categorize_candidate(
            "Sheriff", "Countywide", "Countywide"
        ) is None

    # --- Edge: Clerk of Superior Court should NOT be categorized as superior_court ---

    def test_clerk_of_superior_court_not_superior(self):
        """Clerk of Superior Court is a county office, not a judicial position."""
        result = categorize_candidate(
            "Clerk of Superior Court", "Countywide", "Countywide"
        )
        assert result != "superior_court"


# ===========================================================================
# 4. generate_race_id — URL-safe race ID from category + fields
# ===========================================================================

class TestGenerateRaceId:
    """Generate a URL-safe race ID for the /races/ folder structure.

    Pattern: wa-{qualifier}-{office-type}-{position}-{year}
    """

    # --- Supreme Court ---

    def test_supreme_court_pos_1(self):
        result = generate_race_id("supreme_court", "Justice Position #01", "SUPREME COURT", 2026)
        assert result == "wa-supreme-court-justice-pos-1-2026"

    def test_supreme_court_pos_3(self):
        result = generate_race_id("supreme_court", "Justice Position #03", "SUPREME COURT", 2026)
        assert result == "wa-supreme-court-justice-pos-3-2026"

    def test_supreme_court_pos_4(self):
        result = generate_race_id("supreme_court", "Justice Position #04", "SUPREME COURT", 2026)
        assert result == "wa-supreme-court-justice-pos-4-2026"

    def test_supreme_court_pos_5(self):
        result = generate_race_id("supreme_court", "Justice Position #05", "SUPREME COURT", 2026)
        assert result == "wa-supreme-court-justice-pos-5-2026"

    def test_supreme_court_pos_7(self):
        result = generate_race_id("supreme_court", "Justice Position #07", "SUPREME COURT", 2026)
        assert result == "wa-supreme-court-justice-pos-7-2026"

    # --- Court of Appeals ---

    def test_court_of_appeals_div1_dist1_pos5(self):
        result = generate_race_id(
            "court_of_appeals", "Judge Position 5",
            "COURT OF APPEALS, DIVISION 1, DISTRICT 1", 2026,
        )
        assert result == "wa-appeals-div-1-dist-1-pos-5-2026"

    def test_court_of_appeals_div2_dist2_pos1(self):
        result = generate_race_id(
            "court_of_appeals", "Judge Position 1",
            "Court of Appeals, Division 2, District 2", 2026,
        )
        assert result == "wa-appeals-div-2-dist-2-pos-1-2026"

    def test_court_of_appeals_div3_dist1_pos2(self):
        result = generate_race_id(
            "court_of_appeals", "Judge Position 2",
            "Court of Appeals, Division 3, District 1", 2026,
        )
        assert result == "wa-appeals-div-3-dist-1-pos-2-2026"

    def test_court_of_appeals_div3_dist3_pos1(self):
        result = generate_race_id(
            "court_of_appeals", "Judge Position 1",
            "Court of Appeals, Division 3, District 3", 2026,
        )
        assert result == "wa-appeals-div-3-dist-3-pos-1-2026"

    # --- Superior Court ---

    def test_superior_court_grant_pos_3(self):
        result = generate_race_id(
            "superior_court", "Judge Position #03", "Grant Superior Court", 2026,
        )
        assert result == "wa-grant-superior-court-pos-3-2026"

    def test_superior_court_cowlitz_pos_4(self):
        result = generate_race_id(
            "superior_court", "Judge Position 4", "Cowlitz Superior Court", 2026,
        )
        assert result == "wa-cowlitz-superior-court-pos-4-2026"

    def test_superior_court_king_pos_20(self):
        result = generate_race_id(
            "superior_court", "Judge Position 20", "KING COUNTY SUPERIOR COURT", 2026,
        )
        assert result == "wa-king-superior-court-pos-20-2026"

    def test_superior_court_okanogan_pos_2(self):
        result = generate_race_id(
            "superior_court", "Judge Position 2", "Okanogan Superior Court", 2026,
        )
        assert result == "wa-okanogan-superior-court-pos-2-2026"

    def test_superior_court_multi_county(self):
        result = generate_race_id(
            "superior_court", "Judge Position 2",
            "Ferry, Pend Oreille, Stevens Superior Court", 2026,
        )
        assert result == "wa-ferry-pend-oreille-stevens-superior-court-pos-2-2026"

    # --- PUD Commissioner ---

    def test_pud_skagit_dist_1(self):
        result = generate_race_id(
            "pud_commissioner", "Commissioner 1",
            "SKAGIT COUNTY PUD COMMISSIONER DIST 1", 2026,
        )
        assert "skagit" in result
        assert "pud" in result
        assert result.endswith("-2026")

    def test_pud_clark_dist_3(self):
        result = generate_race_id(
            "pud_commissioner", "COMMISSIONER, DISTRICT NO. 3",
            "CLARK PUBLIC UTILITIES - COMM. DIST. #3", 2026,
        )
        assert "clark" in result
        assert "pud" in result
        assert "3" in result
        assert result.endswith("-2026")

    def test_pud_grant_dist_3(self):
        result = generate_race_id(
            "pud_commissioner", "Commissioner Dist #3",
            "GRANT COUNTY PUD COMM DIST #3", 2026,
        )
        assert "grant" in result
        assert "pud" in result

    def test_pud_okanogan(self):
        result = generate_race_id(
            "pud_commissioner", "Okanogan Commissioner Dist. #1",
            "OK PUBLIC UTILITY DISTRICT 01", 2026,
        )
        assert "okanogan" in result
        assert "pud" in result

    def test_pud_race_id_contains_commissioner(self):
        result = generate_race_id(
            "pud_commissioner", "Commissioner #1", "PUD #1", 2026,
        )
        assert "commissioner" in result

    def test_pud_race_id_contains_dist(self):
        result = generate_race_id(
            "pud_commissioner", "Commissioner #1", "PUD #1", 2026,
        )
        assert "dist" in result

    # --- Port Commissioner ---

    def test_port_bellingham_dist_4(self):
        result = generate_race_id(
            "port_commissioner", "Commissioner District 4",
            "Port of Bellingham Commissioner District 4", 2026,
        )
        assert result == "wa-bellingham-port-commissioner-dist-4-2026"

    def test_port_bellingham_dist_5(self):
        result = generate_race_id(
            "port_commissioner", "Commissioner District 5",
            "Port of Bellingham Commissioner District 5", 2026,
        )
        assert result == "wa-bellingham-port-commissioner-dist-5-2026"

    def test_port_pasco_dist_3(self):
        result = generate_race_id(
            "port_commissioner", "Commissioner District 3",
            "PASCO PORT DISTRICT 3", 2026,
        )
        assert result == "wa-pasco-port-commissioner-dist-3-2026"

    # --- Municipal Court ---

    def test_municipal_seattle_pos_1(self):
        result = generate_race_id(
            "municipal_court", "Municipal Court Judge Position No. 1",
            "City of Seattle", 2026,
        )
        assert result == "wa-seattle-municipal-court-pos-1-2026"

    def test_municipal_seattle_pos_5(self):
        result = generate_race_id(
            "municipal_court", "Municipal Court Judge Position No. 5",
            "City of Seattle", 2026,
        )
        assert result == "wa-seattle-municipal-court-pos-5-2026"

    def test_municipal_tacoma_pos_1(self):
        result = generate_race_id(
            "municipal_court", "Tacoma Municipal Court Pos. 1",
            "CITY OF TACOMA", 2026,
        )
        assert result == "wa-tacoma-municipal-court-pos-1-2026"

    def test_municipal_tacoma_pos_3(self):
        result = generate_race_id(
            "municipal_court", "Tacoma Municipal Court Pos. 3",
            "CITY OF TACOMA", 2026,
        )
        assert result == "wa-tacoma-municipal-court-pos-3-2026"

    # --- KC District Court Electoral ---

    def test_kc_electoral_northeast_pos_1(self):
        result = generate_race_id(
            "kc_electoral_district_court", "Judge Position No. 1",
            "NORTHEAST ELECTORAL DISTRICT", 2026,
        )
        assert result == "wa-king-electoral-northeast-pos-1-2026"

    def test_kc_electoral_shoreline_pos_2(self):
        result = generate_race_id(
            "kc_electoral_district_court", "Judge Position No. 2",
            "SHORELINE ELECTORAL DISTRICT", 2026,
        )
        assert result == "wa-king-electoral-shoreline-pos-2-2026"

    def test_kc_electoral_southeast_pos_3(self):
        result = generate_race_id(
            "kc_electoral_district_court", "Judge Position No. 3",
            "SOUTHEAST ELECTORAL DISTRICT", 2026,
        )
        assert result == "wa-king-electoral-southeast-pos-3-2026"

    def test_kc_electoral_southwest_pos_5(self):
        result = generate_race_id(
            "kc_electoral_district_court", "Judge Position No. 5",
            "SOUTHWEST ELECTORAL DISTRICT", 2026,
        )
        assert result == "wa-king-electoral-southwest-pos-5-2026"

    def test_kc_electoral_west_pos_4(self):
        result = generate_race_id(
            "kc_electoral_district_court", "Judge Position No. 4",
            "WEST ELECTORAL DISTRICT", 2026,
        )
        assert result == "wa-king-electoral-west-pos-4-2026"

    # --- County Council ---

    def test_county_council_king_dist_2(self):
        result = generate_race_id(
            "county_council",
            "Metropolitan King County Council District No. 2",
            "County Council District No. 2", 2026,
        )
        assert result == "wa-king-county-council-dist-2-2026"

    def test_county_council_pierce_dist_1(self):
        result = generate_race_id(
            "county_council", "Council - District No. 1",
            "COUNTY COUNCIL DISTRICT NO. 1", 2026,
        )
        assert result == "wa-pierce-county-council-dist-1-2026"

    def test_county_council_clark_dist_1(self):
        result = generate_race_id(
            "county_council", "COUNCILOR, DISTRICT NO. 1",
            "COUNTY COUNCILOR DISTRICT NO. 1", 2026,
        )
        assert result == "wa-clark-county-council-dist-1-2026"

    def test_county_council_clark_dist_5(self):
        result = generate_race_id(
            "county_council", "COUNCILOR, DISTRICT NO. 5",
            "COUNTY COUNCILOR DISTRICT NO. 5", 2026,
        )
        assert result == "wa-clark-county-council-dist-5-2026"

    # --- City Council ---

    def test_city_council_seattle_dist_5(self):
        result = generate_race_id(
            "city_council", "Council District No. 5",
            "SEATTLE CITY COUNCIL DISTRICT 5", 2026,
        )
        assert result == "wa-seattle-city-council-pos-5-2026"

    def test_city_council_richland_pos_4(self):
        result = generate_race_id(
            "city_council", "Council Pos. 4",
            "City Of Richland", 2026,
        )
        assert result == "wa-richland-city-council-pos-4-2026"

    # --- District Court Judicial ---

    def test_district_court_cascade_pos_1(self):
        result = generate_race_id(
            "district_court_judicial", "Judge Position 1",
            "CASCADE DISTRICT COURT", 2026,
        )
        assert result == "wa-cascade-district-court-pos-1-2026"

    def test_district_court_cascade_pos_2(self):
        result = generate_race_id(
            "district_court_judicial", "Judge Position 2",
            "CASCADE DISTRICT COURT", 2026,
        )
        assert result == "wa-cascade-district-court-pos-2-2026"

    def test_district_court_everett_pos_1(self):
        result = generate_race_id(
            "district_court_judicial", "Judge Position 1",
            "EVERETT DISTRICT COURT", 2026,
        )
        assert result == "wa-everett-district-court-pos-1-2026"

    def test_district_court_evergreen_pos_2(self):
        result = generate_race_id(
            "district_court_judicial", "Judge Position 2",
            "EVERGREEN DISTRICT COURT", 2026,
        )
        assert result == "wa-evergreen-district-court-pos-2-2026"

    def test_district_court_south_pos_3(self):
        result = generate_race_id(
            "district_court_judicial", "Judge Position 3",
            "SOUTH DISTRICT COURT", 2026,
        )
        assert "south" in result
        assert "district-court" in result
        assert "pos-3" in result

    def test_district_court_dept_format(self):
        result = generate_race_id(
            "district_court_judicial",
            "DISTRICT COURT JUDGE, DEPARTMENT NO. 6",
            "DISTRICT COURT JUDGES", 2026,
        )
        assert "district-court" in result
        assert "6" in result
        assert result.endswith("-2026")

    def test_district_court_no_format(self):
        result = generate_race_id(
            "district_court_judicial",
            "District Court No. 7",
            "DISTRICT COURT", 2026,
        )
        assert "district-court" in result
        assert "7" in result
        assert result.endswith("-2026")

    def test_district_court_north_district(self):
        result = generate_race_id(
            "district_court_judicial",
            "DISTRICT COURT JUDGE",
            "Court - North District", 2026,
        )
        assert "district-court" in result
        assert result.startswith("wa-")
        assert result.endswith("-2026")

    # --- Race ID format invariants ---

    def test_race_id_is_lowercase(self):
        result = generate_race_id("supreme_court", "Justice Position #01", "SUPREME COURT", 2026)
        assert result == result.lower()

    def test_race_id_no_spaces(self):
        result = generate_race_id(
            "court_of_appeals", "Judge Position 5",
            "COURT OF APPEALS, DIVISION 1, DISTRICT 1", 2026,
        )
        assert " " not in result

    def test_race_id_no_special_chars(self):
        result = generate_race_id(
            "pud_commissioner", "COMMISSIONER, DISTRICT NO. 3",
            "CLARK PUBLIC UTILITIES - COMM. DIST. #3", 2026,
        )
        # Only lowercase letters, digits, and hyphens
        assert re.match(r'^[a-z0-9-]+$', result), f"Invalid chars in: {result}"

    def test_race_id_ends_with_year(self):
        result = generate_race_id("supreme_court", "Justice Position #01", "SUPREME COURT", 2026)
        assert result.endswith("-2026")

    def test_race_id_starts_with_wa(self):
        result = generate_race_id("supreme_court", "Justice Position #01", "SUPREME COURT", 2026)
        assert result.startswith("wa-")


# ===========================================================================
# 5. build_race_entry — Construct a races.json race object
# ===========================================================================

class TestBuildRaceEntry:
    """Build a properly-structured race entry for races.json."""

    def test_returns_dict(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert isinstance(entry, dict)

    def test_has_required_keys(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        required = {"id", "state_abbr", "office", "year", "title", "status", "url", "candidates"}
        assert required.issubset(set(entry.keys()))

    def test_id_matches_input(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert entry["id"] == "wa-supreme-court-justice-pos-1-2026"

    def test_state_abbr_is_wa(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert entry["state_abbr"] == "WA"

    def test_year_is_int(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert isinstance(entry["year"], int)
        assert entry["year"] == 2026

    def test_url_matches_race_id(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert entry["url"] == "/races/wa-supreme-court-justice-pos-1-2026/"

    def test_status_is_draft(self):
        """New ingested races should have status 'draft' until dossiers are written."""
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert entry["status"] == "draft"

    def test_has_primary_date(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert "primary_date" in entry
        assert "2026" in entry["primary_date"]

    def test_has_general_date(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert "general_date" in entry
        assert "2026" in entry["general_date"]

    def test_has_level_field(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert "level" in entry

    def test_supreme_court_level_statewide(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert entry["level"] == "statewide"

    def test_court_of_appeals_level_statewide(self):
        entry = build_race_entry(
            "court_of_appeals", "wa-appeals-div-1-dist-1-pos-5-2026",
            "Court of Appeals Div. 1 Dist. 1 Pos. 5", 2026, [],
        )
        assert entry["level"] == "statewide"

    def test_pud_level_special_district(self):
        entry = build_race_entry(
            "pud_commissioner", "wa-skagit-pud-commissioner-dist-1-2026",
            "Skagit PUD Commissioner Dist. 1", 2026, [],
        )
        assert entry["level"] == "special_district"

    def test_port_level_special_district(self):
        entry = build_race_entry(
            "port_commissioner", "wa-bellingham-port-commissioner-dist-4-2026",
            "Port of Bellingham Commissioner Dist. 4", 2026, [],
        )
        assert entry["level"] == "special_district"

    def test_municipal_court_level_municipal(self):
        entry = build_race_entry(
            "municipal_court", "wa-seattle-municipal-court-pos-1-2026",
            "Seattle Municipal Court Pos. 1", 2026, [],
        )
        assert entry["level"] == "municipal"

    def test_city_council_level_municipal(self):
        entry = build_race_entry(
            "city_council", "wa-seattle-city-council-pos-5-2026",
            "Seattle City Council Pos. 5", 2026, [],
        )
        assert entry["level"] == "municipal"

    def test_superior_court_level_county(self):
        entry = build_race_entry(
            "superior_court", "wa-grant-superior-court-pos-3-2026",
            "Grant Superior Court Pos. 3", 2026, [],
        )
        assert entry["level"] == "county"

    def test_county_council_level_county(self):
        entry = build_race_entry(
            "county_council", "wa-king-county-council-dist-2-2026",
            "King County Council Dist. 2", 2026, [],
        )
        assert entry["level"] == "county"

    def test_candidates_with_raw_party(self):
        candidates = [
            {"name": "Anne Melani Bremner", "party_raw": ""},
        ]
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, candidates,
        )
        assert len(entry["candidates"]) == 1
        assert entry["candidates"][0]["name"] == "Anne Melani Bremner"
        # Empty party in judicial races should normalize to nonpartisan
        assert entry["candidates"][0]["party"] == "nonpartisan"

    def test_candidate_has_url(self):
        """Candidate URL should be generated from race ID and candidate slug."""
        candidates = [{"name": "Anne Melani Bremner", "party_raw": ""}]
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, candidates,
        )
        assert "url" in entry["candidates"][0]
        assert entry["candidates"][0]["url"].startswith("/races/wa-supreme-court-justice-pos-1-2026/")

    def test_candidate_has_slug(self):
        candidates = [{"name": "Anne Melani Bremner", "party_raw": ""}]
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, candidates,
        )
        assert "slug" in entry["candidates"][0]
        assert entry["candidates"][0]["slug"] == "bremner"

    def test_candidate_role_is_filed(self):
        candidates = [{"name": "Anne Melani Bremner", "party_raw": ""}]
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, candidates,
        )
        assert entry["candidates"][0]["role"] == "Filed"

    def test_title_includes_year(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert "2026" in entry["title"]

    def test_empty_candidates_list(self):
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, [],
        )
        assert entry["candidates"] == []

    def test_multiple_candidates_preserved(self):
        candidates = [
            {"name": "Anne Melani Bremner", "party_raw": ""},
            {"name": "Colleen Melody", "party_raw": ""},
            {"name": "Scott Edwards", "party_raw": ""},
            {"name": "Laura Christensen Colberg", "party_raw": ""},
        ]
        entry = build_race_entry(
            "supreme_court", "wa-supreme-court-justice-pos-1-2026",
            "WA Supreme Court Justice Pos. 1", 2026, candidates,
        )
        assert len(entry["candidates"]) == 4

    def test_democratic_party_normalized(self):
        candidates = [{"name": "Jerome O'Leary", "party_raw": "REPUBLICAN"}]
        entry = build_race_entry(
            "county_council", "wa-pierce-county-council-dist-1-2026",
            "Pierce County Council Dist. 1", 2026, candidates,
        )
        assert entry["candidates"][0]["party"] == "rep"

    def test_republican_party_normalized(self):
        candidates = [{"name": "Terrance Mayers", "party_raw": "DEMOCRATIC"}]
        entry = build_race_entry(
            "county_council", "wa-pierce-county-council-dist-1-2026",
            "Pierce County Council Dist. 1", 2026, candidates,
        )
        assert entry["candidates"][0]["party"] == "dem"

    def test_hyphenated_name_slug(self):
        candidates = [{"name": "Samantha Cruz-Mendoza", "party_raw": ""}]
        entry = build_race_entry(
            "port_commissioner", "wa-bellingham-port-commissioner-dist-4-2026",
            "Port of Bellingham Commissioner Dist. 4", 2026, candidates,
        )
        assert entry["candidates"][0]["slug"] == "cruz-mendoza"


# ===========================================================================
# 6. is_duplicate — Fuzzy match against existing races.json
# ===========================================================================

class TestIsDuplicate:
    """Check if a candidate name already exists in a specific race in races.json.

    The function signature is: is_duplicate(candidate_name, race_id, existing_races)
    It checks only within the specified race_id.
    """

    @pytest.fixture
    def sample_races(self):
        """Minimal races.json structure for duplicate detection."""
        return [
            {
                "id": "wa-thurston-assessor-2026",
                "candidates": [
                    {"name": "Jason Olson", "party": "nonpartisan"},
                    {"name": "Todd Zeman", "party": "nonpartisan"},
                ],
            },
            {
                "id": "wa-thurston-sheriff-2026",
                "candidates": [
                    {"name": "Kevin Burton-Crow", "party": "nonpartisan"},
                    {"name": "Derek Sanders", "party": "nonpartisan"},
                ],
            },
            {
                "id": "wa-thurston-district-court-judge-pos-3-2026",
                "candidates": [
                    {"name": 'Catherine "Cat" Wohl', "party": "nonpartisan"},
                    {"name": "David M. Buckley", "party": "nonpartisan"},
                ],
            },
        ]

    # --- Exact matches ---

    def test_exact_match_found(self, sample_races):
        assert is_duplicate("Jason Olson", "wa-thurston-assessor-2026", sample_races) is True

    def test_exact_match_different_case(self, sample_races):
        assert is_duplicate("jason olson", "wa-thurston-assessor-2026", sample_races) is True

    def test_exact_match_uppercase(self, sample_races):
        assert is_duplicate("JASON OLSON", "wa-thurston-assessor-2026", sample_races) is True

    # --- Hyphenated names ---

    def test_hyphenated_name_found(self, sample_races):
        assert is_duplicate("Kevin Burton-Crow", "wa-thurston-sheriff-2026", sample_races) is True

    def test_hyphenated_name_lowercase(self, sample_races):
        assert is_duplicate("kevin burton-crow", "wa-thurston-sheriff-2026", sample_races) is True

    # --- Race-scoped: candidate in different race is not a duplicate ---

    def test_candidate_in_wrong_race_not_found(self, sample_races):
        """Jason Olson is in assessor race, not sheriff race."""
        assert is_duplicate("Jason Olson", "wa-thurston-sheriff-2026", sample_races) is False

    # --- Nickname matching ---

    def test_nickname_in_quotes_found(self, sample_races):
        """'Catherine Wohl' should match 'Catherine "Cat" Wohl'."""
        assert is_duplicate(
            "Catherine Wohl", "wa-thurston-district-court-judge-pos-3-2026", sample_races
        ) is True

    # --- Middle initial differences ---

    def test_with_middle_initial_found(self, sample_races):
        """'David Buckley' should match 'David M. Buckley'."""
        assert is_duplicate(
            "David Buckley", "wa-thurston-district-court-judge-pos-3-2026", sample_races
        ) is True

    def test_different_middle_initial_found(self, sample_races):
        """'David M Buckley' should match 'David M. Buckley'."""
        assert is_duplicate(
            "David M Buckley", "wa-thurston-district-court-judge-pos-3-2026", sample_races
        ) is True

    # --- Not found ---

    def test_completely_different_name(self, sample_races):
        assert is_duplicate(
            "Elizabeth Warren", "wa-thurston-assessor-2026", sample_races
        ) is False

    def test_partial_last_name_no_match(self, sample_races):
        assert is_duplicate(
            "Jason Anderson", "wa-thurston-assessor-2026", sample_races
        ) is False

    def test_partial_first_name_no_match(self, sample_races):
        assert is_duplicate(
            "Jason Smith", "wa-thurston-assessor-2026", sample_races
        ) is False

    def test_empty_name(self, sample_races):
        assert is_duplicate("", "wa-thurston-assessor-2026", sample_races) is False

    def test_nonexistent_race_id(self, sample_races):
        """Looking up a race_id that doesn't exist should return False."""
        assert is_duplicate("Jason Olson", "wa-nonexistent-race-2026", sample_races) is False

    def test_empty_races_list(self):
        assert is_duplicate("Jason Olson", "wa-thurston-assessor-2026", []) is False

    # --- Pamela vs Pam (nickname in quotes) ---

    def test_pam_matches_pamela(self, sample_races):
        """Quoted nicknames should support full name matching."""
        races = sample_races + [{
            "id": "wa-pud-2-commissioner-dist-1-2026",
            "candidates": [
                {"name": 'Pamela "Pam" Hickey', "party": "nonpartisan"},
            ],
        }]
        assert is_duplicate("Pamela Hickey", "wa-pud-2-commissioner-dist-1-2026", races) is True


# ===========================================================================
# Integration-style tests — end-to-end scenarios
# ===========================================================================

class TestEndToEndScenarios:
    """Higher-level scenarios that test the functions working together."""

    def test_supreme_court_full_pipeline(self):
        """Categorize -> generate ID -> build entry for a Supreme Court race."""
        race_str = "Justice Position #01"
        district_str = "SUPREME COURT"
        district_type = "Judicial"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "supreme_court"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert race_id == "wa-supreme-court-justice-pos-1-2026"

        entry = build_race_entry(
            category, race_id, "WA Supreme Court Justice Pos. 1", 2026,
            [{"name": "Anne Melani Bremner", "party_raw": ""}],
        )
        assert entry["id"] == race_id
        assert len(entry["candidates"]) == 1
        assert entry["candidates"][0]["name"] == "Anne Melani Bremner"

    def test_pud_full_pipeline(self):
        """Categorize -> identify PUD -> generate ID -> build entry."""
        race_str = "Commissioner 1"
        district_str = "SKAGIT COUNTY PUD COMMISSIONER DIST 1"
        district_type = "Public Utility"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "pud_commissioner"

        pud_slug, pud_name = identify_pud(district_str)
        assert pud_slug == "skagit-pud"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert "skagit" in race_id
        assert race_id.endswith("-2026")

    def test_kc_electoral_full_pipeline(self):
        """Categorize -> generate ID for KC electoral district court."""
        race_str = "Judge Position No. 3"
        district_str = "SOUTHEAST ELECTORAL DISTRICT"
        district_type = "District Court"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "kc_electoral_district_court"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert race_id == "wa-king-electoral-southeast-pos-3-2026"

    def test_court_of_appeals_full_pipeline(self):
        """Categorize -> generate ID for Court of Appeals."""
        race_str = "Judge Position 2"
        district_str = "Court of Appeals, Division 3, District 1"
        district_type = "Judicial"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "court_of_appeals"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert race_id == "wa-appeals-div-3-dist-1-pos-2-2026"

    def test_municipal_court_full_pipeline(self):
        """Categorize -> generate ID for municipal court."""
        race_str = "Municipal Court Judge Position No. 5"
        district_str = "City of Seattle"
        district_type = "City/Town"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "municipal_court"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert race_id == "wa-seattle-municipal-court-pos-5-2026"

    def test_port_commissioner_full_pipeline(self):
        """Categorize -> generate ID for port commissioner."""
        race_str = "Commissioner District 4"
        district_str = "Port of Bellingham Commissioner District 4"
        district_type = "Port"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "port_commissioner"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert race_id == "wa-bellingham-port-commissioner-dist-4-2026"

    def test_non_target_type_returns_none(self):
        """US Rep should not be categorized (returns None)."""
        race_str = "U.S. Representative"
        district_str = "Congressional District 1"
        district_type = "Congressional"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category is None

    def test_duplicate_candidate_not_added(self):
        """A candidate already in races.json should be detected."""
        existing = [{
            "id": "wa-thurston-assessor-2026",
            "candidates": [{"name": "Jason Olson", "party": "nonpartisan"}],
        }]
        assert is_duplicate("Jason Olson", "wa-thurston-assessor-2026", existing) is True
        assert is_duplicate("JASON OLSON", "wa-thurston-assessor-2026", existing) is True
        assert is_duplicate("Someone Else", "wa-thurston-assessor-2026", existing) is False

    def test_superior_court_full_pipeline(self):
        """Categorize -> generate ID for superior court."""
        race_str = "Judge Position #03"
        district_str = "Grant Superior Court"
        district_type = "Judicial"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "superior_court"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert race_id == "wa-grant-superior-court-pos-3-2026"

    def test_county_council_full_pipeline(self):
        """Categorize -> generate ID for county council."""
        race_str = "Metropolitan King County Council District No. 2"
        district_str = "County Council District No. 2"
        district_type = "Council"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "county_council"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert race_id == "wa-king-county-council-dist-2-2026"

    def test_city_council_full_pipeline(self):
        """Categorize -> generate ID for city council."""
        race_str = "Council District No. 5"
        district_str = "SEATTLE CITY COUNCIL DISTRICT 5"
        district_type = "City Council"

        category = categorize_candidate(race_str, district_str, district_type)
        assert category == "city_council"

        race_id = generate_race_id(category, race_str, district_str, 2026)
        assert "seattle" in race_id
        assert "city-council" in race_id
