#!/usr/bin/env python3
"""TDD tests for county race mapping and page generation — US #1672."""

import csv
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
DATA_DIR = TOOLS_DIR / "data"
STATES_DIR = REPO_ROOT / "states"
RACES_JSON = DATA_DIR / "races.json"
COUNTY_RACES_JSON = DATA_DIR / "county_races.json"
CSS_FILE = REPO_ROOT / "css" / "dossier.css"
DOSSIER_ROOT = Path.home() / "Local" / "Projects" / "github" / "clearthemud" / "output" / "dossiers"

# The dossier JSON that TestCountyDossierResolution reads is built in the
# private build repo and is not part of this repository. On a workstation that
# has the build repo checked out they run and must pass. In a fresh clone, and
# in CI, there is nothing to assert against, so they skip with a named reason
# rather than fail on a missing path.
#
# This is the only place under tools/tests that reaches outside this
# repository. Every other test here reads the site tree, so the checks on
# published content run everywhere, including CI.
requires_dossiers = pytest.mark.skipif(
    not DOSSIER_ROOT.is_dir(),
    reason=(
        f"build-repo dossier output not present at {DOSSIER_ROOT}; "
        "these run where the build repo is checked out"
    ),
)


# ---------------------------------------------------------------------------
# Phase 1: County-Candidate Mapping
# ---------------------------------------------------------------------------

class TestCountyRacesJSON:
    """Validate county_races.json structure and content."""

    @pytest.fixture
    def county_races(self):
        assert COUNTY_RACES_JSON.exists(), "tools/data/county_races.json must exist"
        with open(COUNTY_RACES_JSON) as f:
            return json.load(f)

    def test_has_wa_key(self, county_races):
        assert "WA" in county_races

    def test_has_39_counties(self, county_races):
        wa = county_races["WA"]
        assert len(wa) == 39, f"Expected 39 WA counties, got {len(wa)}"

    def test_thurston_exists(self, county_races):
        assert "thurston" in county_races["WA"]

    def test_thurston_has_races(self, county_races):
        thurston = county_races["WA"]["thurston"]
        assert "races" in thurston
        assert len(thurston["races"]) > 0

    def test_thurston_has_assessor(self, county_races):
        thurston = county_races["WA"]["thurston"]
        offices = [r["office"] for r in thurston["races"]]
        assert "Assessor" in offices

    def test_thurston_has_sheriff(self, county_races):
        thurston = county_races["WA"]["thurston"]
        offices = [r["office"] for r in thurston["races"]]
        assert "Sheriff" in offices

    def test_race_has_required_fields(self, county_races):
        thurston = county_races["WA"]["thurston"]
        for race in thurston["races"]:
            assert "office" in race, f"Race missing office"
            assert "candidates" in race, f"Race {race.get('office')} missing candidates"
            assert len(race["candidates"]) > 0, f"Race {race['office']} has no candidates"

    def test_candidate_has_required_fields(self, county_races):
        thurston = county_races["WA"]["thurston"]
        for race in thurston["races"]:
            for c in race["candidates"]:
                assert "name" in c, f"Candidate missing name in {race['office']}"
                assert "party" in c, f"{c['name']} missing party"
                assert "filing_date" in c, f"{c['name']} missing filing_date"

    def test_thurston_assessor_has_olson(self, county_races):
        thurston = county_races["WA"]["thurston"]
        assessor_race = [r for r in thurston["races"] if r["office"] == "Assessor"][0]
        names = [c["name"] for c in assessor_race["candidates"]]
        assert "JJ Olson" in names

    def test_thurston_sheriff_has_two_candidates(self, county_races):
        thurston = county_races["WA"]["thurston"]
        sheriff_race = [r for r in thurston["races"] if r["office"] == "Sheriff"][0]
        assert len(sheriff_race["candidates"]) == 2

    def test_county_name_field(self, county_races):
        thurston = county_races["WA"]["thurston"]
        assert thurston["name"] == "Thurston"
        assert thurston["full_name"] == "Thurston County"

    def test_no_duplicate_candidates(self, county_races):
        """No candidate should appear twice in the same race."""
        for county_slug, county in county_races["WA"].items():
            for race in county.get("races", []):
                names = [c["name"] for c in race["candidates"]]
                assert len(names) == len(set(names)), \
                    f"Duplicate candidate in {county_slug} {race['office']}"


# ---------------------------------------------------------------------------
# Phase 2: races.json County-Level Entries
# ---------------------------------------------------------------------------

class TestRacesJSONCountyEntries:
    """Validate county-level race entries in races.json."""

    @pytest.fixture
    def races(self):
        with open(RACES_JSON) as f:
            return json.load(f)["races"]

    def test_has_county_races(self, races):
        county = [r for r in races if r.get("level") == "county"]
        assert len(county) > 0, "races.json should have county-level races"

    def test_thurston_assessor_race(self, races):
        race = [r for r in races if r["id"] == "wa-thurston-assessor-2026"]
        assert len(race) == 1
        assert race[0]["office"] == "Assessor"
        assert race[0]["county"] == "Thurston"
        assert race[0]["level"] == "county"

    def test_thurston_sheriff_race(self, races):
        race = [r for r in races if r["id"] == "wa-thurston-sheriff-2026"]
        assert len(race) == 1

    def test_county_race_id_format(self, races):
        county = [r for r in races if r.get("level") == "county"]
        for r in county:
            assert re.match(r"wa-[a-z-]+-[a-z0-9-]+-2026$", r["id"]), \
                f"County race id should match wa-{{county}}-{{office}}-2026: {r['id']}"

    def test_county_race_has_candidates(self, races):
        county = [r for r in races if r.get("level") == "county"]
        for r in county:
            assert len(r["candidates"]) > 0, f"Race {r['id']} has no candidates"

    def test_county_candidate_has_fields(self, races):
        county = [r for r in races if r.get("level") == "county"
                  and r.get("county") == "Thurston"]
        for r in county:
            for c in r["candidates"]:
                assert "name" in c
                assert "party" in c
                assert "slug" in c
                assert "status" in c

    def test_thurston_race_urls(self, races):
        county = [r for r in races if r.get("level") == "county"
                  and r.get("county") == "Thurston"]
        for r in county:
            assert r["url"].startswith("/races/wa-thurston-")


# ---------------------------------------------------------------------------
# Phase 3: County Page Generation
# ---------------------------------------------------------------------------

class TestCountyPageGeneration:
    """Validate generated county hub pages show race content."""

    @pytest.fixture
    def thurston_page(self):
        path = STATES_DIR / "washington" / "thurston" / "index.html"
        if not path.exists():
            pytest.skip("Thurston county page not generated yet")
        return path.read_text()

    def test_no_coming_soon_placeholder(self, thurston_page):
        assert "research for Thurston County is in progress" not in thurston_page

    def test_has_county_offices_section(self, thurston_page):
        assert "County Offices" in thurston_page

    def test_has_assessor_race(self, thurston_page):
        assert "Assessor" in thurston_page

    def test_has_sheriff_race(self, thurston_page):
        assert "Sheriff" in thurston_page

    def test_has_candidate_names(self, thurston_page):
        assert "JJ Olson" in thurston_page
        assert "Lynda Nashed Zeman" in thurston_page

    def test_has_race_links(self, thurston_page):
        assert "/races/wa-thurston-assessor-2026/" in thurston_page

    def test_has_party_info(self, thurston_page):
        assert "(D)" in thurston_page or "(R)" in thurston_page


# ---------------------------------------------------------------------------
# Phase 4: Race Overview and Candidate Dossier Pages
# ---------------------------------------------------------------------------

class TestCountyRaceOverviewPages:
    """Validate race overview pages for county races."""

    @pytest.fixture
    def assessor_overview(self):
        path = REPO_ROOT / "races" / "wa-thurston-assessor-2026" / "index.html"
        if not path.exists():
            pytest.skip("Thurston Assessor race page not generated yet")
        return path.read_text()

    def test_has_breadcrumb(self, assessor_overview):
        assert "Thurston County" in assessor_overview
        assert "Washington" in assessor_overview

    def test_has_race_title(self, assessor_overview):
        assert "Assessor" in assessor_overview

    def test_has_candidate_cards(self, assessor_overview):
        assert "JJ Olson" in assessor_overview
        assert "Lynda Nashed Zeman" in assessor_overview

    def test_has_candidate_links(self, assessor_overview):
        assert "olson" in assessor_overview.lower()
        assert "zeman" in assessor_overview.lower()


class TestCountyCandidateDossierPages:
    """Validate candidate dossier pages for county races."""

    @pytest.fixture
    def zeman_page(self):
        path = REPO_ROOT / "races" / "wa-thurston-assessor-2026" / "zeman" / "index.html"
        if not path.exists():
            pytest.skip("Zeman dossier page not generated yet")
        return path.read_text()

    def test_has_candidate_name(self, zeman_page):
        assert "Lynda Nashed Zeman" in zeman_page

    def test_has_party(self, zeman_page):
        assert "Democratic" in zeman_page or "party-dem" in zeman_page

    def test_has_breadcrumb(self, zeman_page):
        assert "Thurston" in zeman_page

    def test_has_dossier_css(self, zeman_page):
        assert "dossier.css" in zeman_page

    def test_has_state_finance(self, zeman_page):
        """Zeman has PDC finance data — should render."""
        assert "PDC" in zeman_page or "Campaign Finance" in zeman_page \
            or "Total Raised" in zeman_page or "$" in zeman_page


# ---------------------------------------------------------------------------
# Phase 5: Dossier Path Resolution for County Races
# ---------------------------------------------------------------------------

@requires_dossiers
class TestCountyDossierResolution:
    """Validate that county dossiers can be found for Thurston candidates."""

    def test_assessor_dossier_exists(self):
        path = DOSSIER_ROOT / "wa" / "2026" / "county" / "wa_assessor_zeman_2026.json"
        assert path.exists(), f"Dossier not found at {path}"

    def test_sheriff_dossier_exists(self):
        path = DOSSIER_ROOT / "wa" / "2026" / "county" / "wa_sheriff_sanders_2026.json"
        assert path.exists(), f"Dossier not found at {path}"

    def test_dossier_has_meta(self):
        path = DOSSIER_ROOT / "wa" / "2026" / "county" / "wa_assessor_zeman_2026.json"
        with open(path) as f:
            d = json.load(f)
        assert "meta" in d
        assert d["meta"]["race"]["office"] == "Assessor"

    def test_dossier_has_state_finance(self):
        path = DOSSIER_ROOT / "wa" / "2026" / "county" / "wa_assessor_zeman_2026.json"
        with open(path) as f:
            d = json.load(f)
        assert "state_campaign_finance" in d
        scf = d["state_campaign_finance"]
        assert "total_raised" in scf


# ---------------------------------------------------------------------------
# Structural integrity
# ---------------------------------------------------------------------------

class TestCountyRaceURLScheme:
    """Validate URL scheme for county races."""

    @pytest.fixture
    def races(self):
        with open(RACES_JSON) as f:
            return json.load(f)["races"]

    def test_county_race_url_pattern(self, races):
        county = [r for r in races if r.get("level") == "county"
                  and r.get("county") == "Thurston"]
        for r in county:
            assert r["url"] == f"/races/{r['id']}/"

    def test_candidate_slug_lowercase(self, races):
        county = [r for r in races if r.get("level") == "county"]
        for r in county:
            for c in r["candidates"]:
                assert c["slug"] == c["slug"].lower(), \
                    f"Slug should be lowercase: {c['slug']}"
                assert " " not in c["slug"], \
                    f"Slug should have no spaces: {c['slug']}"
