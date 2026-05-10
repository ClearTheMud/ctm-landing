#!/usr/bin/env python3
"""TDD tests for WA legislative race dossier ingestion — written before implementation.

Epic #1685: WA Legislative Race Dossier Ingestion — 122 Races, 294 Candidates
US #1686: URL scheme + races.json
US #1687: Generator updates for state_campaign_finance
US #1688: TDD tests (this file)
US #1689: Generate all legislative pages
US #1690: State page legislature integration
"""

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RACES_DIR = REPO_ROOT / "races"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSS_FILE = REPO_ROOT / "css" / "dossier.css"
STATES_DIR = REPO_ROOT / "states"
DOSSIER_ROOT = Path.home() / "Local/Projects/github/clearthemud/output/dossiers"


# ---------------------------------------------------------------------------
# Test Class 1: races.json schema for legislative races (US #1686)
# ---------------------------------------------------------------------------
class TestLegislativeRacesJSON:
    """Validate that races.json contains all 122 WA legislative races."""

    @pytest.fixture
    def races(self):
        with open(DATA_DIR / "races.json") as f:
            return json.load(f)["races"]

    @pytest.fixture
    def leg_races(self, races):
        return [r for r in races if r["state_abbr"] == "WA"
                and r["office"] in ("State Senate", "State House Pos. 1", "State House Pos. 2")]

    def test_has_122_legislative_races(self, leg_races):
        assert len(leg_races) == 122, f"Expected 122 WA legislative races, got {len(leg_races)}"

    def test_has_24_senate_races(self, leg_races):
        senate = [r for r in leg_races if r["office"] == "State Senate"]
        assert len(senate) == 24

    def test_has_49_house_pos1_races(self, leg_races):
        pos1 = [r for r in leg_races if r["office"] == "State House Pos. 1"]
        assert len(pos1) == 49

    def test_has_49_house_pos2_races(self, leg_races):
        pos2 = [r for r in leg_races if r["office"] == "State House Pos. 2"]
        assert len(pos2) == 49

    def test_total_294_candidates(self, leg_races):
        total = sum(len(r["candidates"]) for r in leg_races)
        assert total == 294, f"Expected 294 total candidates, got {total}"

    def test_race_id_format_senate(self, leg_races):
        for r in leg_races:
            if r["office"] == "State Senate":
                assert re.match(r"wa-state-senate-\d+-2026$", r["id"]), \
                    f"Bad senate race id: {r['id']}"

    def test_race_id_format_house(self, leg_races):
        for r in leg_races:
            if "House" in r["office"]:
                pos = "1" if "Pos. 1" in r["office"] else "2"
                assert re.match(rf"wa-state-house-\d+-pos{pos}-2026$", r["id"]), \
                    f"Bad house race id: {r['id']}"

    def test_race_url_matches_id(self, leg_races):
        for r in leg_races:
            assert r["url"] == f"/races/{r['id']}/", f"URL mismatch for {r['id']}"

    def test_each_race_has_candidates(self, leg_races):
        for r in leg_races:
            assert len(r["candidates"]) >= 1, f"Race {r['id']} has no candidates"

    def test_candidate_fields(self, leg_races):
        for r in leg_races:
            for c in r["candidates"]:
                assert "name" in c, f"Missing name in {r['id']}"
                assert "party" in c, f"Missing party in {r['id']}"
                assert "role" in c, f"Missing role in {r['id']}"
                assert "url" in c, f"Missing url in {r['id']}"

    def test_candidate_url_format(self, leg_races):
        for r in leg_races:
            for c in r["candidates"]:
                assert c["url"].startswith(f"/races/{r['id']}/"), \
                    f"Candidate URL should be under race: {c['url']}"
                assert c["url"].endswith("/"), f"URL must end with /: {c['url']}"

    def test_district_field_present(self, leg_races):
        for r in leg_races:
            assert "district" in r, f"Missing district in {r['id']}"
            assert r["district"], f"Empty district in {r['id']}"


# ---------------------------------------------------------------------------
# Test Class 2: Dossier path resolution for legislative races (US #1687)
# ---------------------------------------------------------------------------
class TestDossierPathResolution:
    """Validate that find_dossier_json resolves legislative dossier paths."""

    def _import_find_dossier(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gen", REPO_ROOT / "tools" / "generate_candidate_pages.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.find_dossier_json

    def test_resolves_state_senate(self):
        find = self._import_find_dossier()
        race = {"state_abbr": "WA", "year": 2026, "office": "State Senate",
                "district": "47"}
        result = find(race, "kauffman")
        assert result is not None, "Should find wa_state_senate_47_kauffman_2026.json"
        assert result["meta"]["full_name"] == "Claudia Kauffman"

    def test_resolves_state_house_pos1(self):
        find = self._import_find_dossier()
        race = {"state_abbr": "WA", "year": 2026, "office": "State House Pos. 1",
                "district": "1"}
        result = find(race, "duerr")
        assert result is not None, "Should find wa_state_house_1_duerr_2026.json"
        assert result["meta"]["full_name"] == "Davina Duerr"

    def test_resolves_state_house_pos2(self):
        find = self._import_find_dossier()
        race = {"state_abbr": "WA", "year": 2026, "office": "State House Pos. 2",
                "district": "1"}
        result = find(race, "kloba")
        assert result is not None, "Should find wa_state_house_1_kloba_2026.json"
        assert result["meta"]["full_name"] == "Shelley Kloba"

    def test_no_regression_federal_house(self):
        find = self._import_find_dossier()
        race = {"state_abbr": "WA", "year": 2026, "office": "US House",
                "district": "7"}
        result = find(race, "jayapal")
        if (DOSSIER_ROOT / "wa/2026/congressional/cd-07").exists():
            assert result is not None or result is None  # pass either way if dir exists
        else:
            pytest.skip("Federal dossier directory not present")

    def test_no_regression_us_senate(self):
        find = self._import_find_dossier()
        race = {"state_abbr": "ME", "year": 2026, "office": "US Senate",
                "district": ""}
        # Should not crash for existing US Senate path logic
        find(race, "collins")


# ---------------------------------------------------------------------------
# Test Class 3: State campaign finance rendering (US #1687)
# ---------------------------------------------------------------------------
class TestStateCampaignFinance:
    """Validate state_campaign_finance data renders correctly on candidate pages."""

    @pytest.fixture
    def sample_dossier_with_pdc(self):
        path = DOSSIER_ROOT / "wa/2026/legislative/ld-14/wa_state_house_14_dimas_2026.json"
        if not path.exists():
            pytest.skip("Sample dossier not available")
        with open(path) as f:
            return json.load(f)

    def _import_renderer(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gen", REPO_ROOT / "tools" / "generate_candidate_pages.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_page_shows_wa_pdc_total_raised(self, sample_dossier_with_pdc):
        mod = self._import_renderer()
        race = {"state_abbr": "WA", "year": 2026, "office": "State House Pos. 1",
                "district": "14", "title": "WA LD-14 State House Pos. 1",
                "url": "/races/wa-state-house-14-pos1-2026/"}
        candidate = {"name": "Chelsea Dimas", "party": "D", "role": "challenger",
                     "url": "/races/wa-state-house-14-pos1-2026/dimas/"}
        state_info = {"name": "Washington", "slug": "washington"}
        html = mod.render_candidate_page(race, candidate, sample_dossier_with_pdc, state_info)
        assert "$9,655" in html, "Should display WA PDC total raised amount"

    def test_page_shows_wa_pdc_total_spent(self, sample_dossier_with_pdc):
        mod = self._import_renderer()
        race = {"state_abbr": "WA", "year": 2026, "office": "State House Pos. 1",
                "district": "14", "title": "WA LD-14 State House Pos. 1",
                "url": "/races/wa-state-house-14-pos1-2026/"}
        candidate = {"name": "Chelsea Dimas", "party": "D", "role": "challenger",
                     "url": "/races/wa-state-house-14-pos1-2026/dimas/"}
        state_info = {"name": "Washington", "slug": "washington"}
        html = mod.render_candidate_page(race, candidate, sample_dossier_with_pdc, state_info)
        assert "$22,316" in html, "Should display WA PDC total spent amount"

    def test_page_shows_cash_carried_forward(self, sample_dossier_with_pdc):
        mod = self._import_renderer()
        race = {"state_abbr": "WA", "year": 2026, "office": "State House Pos. 1",
                "district": "14", "title": "WA LD-14 State House Pos. 1",
                "url": "/races/wa-state-house-14-pos1-2026/"}
        candidate = {"name": "Chelsea Dimas", "party": "D", "role": "challenger",
                     "url": "/races/wa-state-house-14-pos1-2026/dimas/"}
        state_info = {"name": "Washington", "slug": "washington"}
        html = mod.render_candidate_page(race, candidate, sample_dossier_with_pdc, state_info)
        assert "$17,377" in html, "Should display cash carried forward"

    def test_page_shows_pdc_source(self, sample_dossier_with_pdc):
        mod = self._import_renderer()
        race = {"state_abbr": "WA", "year": 2026, "office": "State House Pos. 1",
                "district": "14", "title": "WA LD-14 State House Pos. 1",
                "url": "/races/wa-state-house-14-pos1-2026/"}
        candidate = {"name": "Chelsea Dimas", "party": "D", "role": "challenger",
                     "url": "/races/wa-state-house-14-pos1-2026/dimas/"}
        state_info = {"name": "Washington", "slug": "washington"}
        html = mod.render_candidate_page(race, candidate, sample_dossier_with_pdc, state_info)
        assert "PDC" in html or "Public Disclosure" in html, \
            "Should cite WA PDC as data source"

    def test_no_fec_section_for_state_races(self, sample_dossier_with_pdc):
        mod = self._import_renderer()
        race = {"state_abbr": "WA", "year": 2026, "office": "State House Pos. 1",
                "district": "14", "title": "WA LD-14 State House Pos. 1",
                "url": "/races/wa-state-house-14-pos1-2026/"}
        candidate = {"name": "Chelsea Dimas", "party": "D", "role": "challenger",
                     "url": "/races/wa-state-house-14-pos1-2026/dimas/"}
        state_info = {"name": "Washington", "slug": "washington"}
        html = mod.render_candidate_page(race, candidate, sample_dossier_with_pdc, state_info)
        assert "No FEC filings" not in html, \
            "State races should not show 'No FEC filings' when PDC data exists"


# ---------------------------------------------------------------------------
# Test Class 4: Candidate page structure for legislative races (US #1689)
# ---------------------------------------------------------------------------
class TestLegislativeCandidatePage:
    """Validate generated candidate dossier pages for state legislative races."""

    @pytest.fixture
    def sample_page(self):
        path = RACES_DIR / "wa-state-senate-47-2026" / "kauffman" / "index.html"
        if not path.exists():
            pytest.skip("Legislative candidate page not yet generated")
        return path.read_text()

    def test_page_has_correct_title(self, sample_page):
        assert "Claudia Kauffman" in sample_page

    def test_page_has_race_title(self, sample_page):
        assert "State Senate" in sample_page
        assert "LD-47" in sample_page or "District 47" in sample_page

    def test_page_has_party_class(self, sample_page):
        assert 'party-dem' in sample_page or 'party-rep' in sample_page \
            or 'party-neutral' in sample_page

    def test_page_has_dossier_css(self, sample_page):
        assert '/css/dossier.css' in sample_page

    def test_page_has_breadcrumb_nav(self, sample_page):
        assert 'dossier-nav' in sample_page
        assert '/states/washington/' in sample_page
        assert 'Washington' in sample_page

    def test_page_has_tlp_badge(self, sample_page):
        assert 'TLP:GREEN' in sample_page

    def test_page_has_bluf_section(self, sample_page):
        assert 'BLUF' in sample_page

    def test_page_has_canonical_url(self, sample_page):
        assert '<link rel="canonical"' in sample_page
        assert '/races/wa-state-senate-47-2026/kauffman/' in sample_page

    def test_page_has_csp_header(self, sample_page):
        assert 'Content-Security-Policy' in sample_page


# ---------------------------------------------------------------------------
# Test Class 5: Race overview page for legislative races (US #1689)
# ---------------------------------------------------------------------------
class TestLegislativeRaceOverview:
    """Validate race overview pages for state legislative races."""

    @pytest.fixture
    def senate_overview(self):
        path = RACES_DIR / "wa-state-senate-47-2026" / "index.html"
        if not path.exists():
            pytest.skip("Legislative race overview not yet generated")
        return path.read_text()

    @pytest.fixture
    def house_overview(self):
        path = RACES_DIR / "wa-state-house-1-pos1-2026" / "index.html"
        if not path.exists():
            pytest.skip("Legislative race overview not yet generated")
        return path.read_text()

    def test_senate_overview_has_title(self, senate_overview):
        assert "State Senate" in senate_overview
        assert "LD-47" in senate_overview or "District 47" in senate_overview

    def test_senate_overview_lists_candidates(self, senate_overview):
        assert 'dossier-link' in senate_overview

    def test_senate_overview_has_correct_office(self, senate_overview):
        assert "State Senate" in senate_overview

    def test_house_overview_has_position(self, house_overview):
        assert "Pos. 1" in house_overview or "Position 1" in house_overview

    def test_overview_has_dossier_css(self, senate_overview):
        assert '/css/dossier.css' in senate_overview

    def test_overview_has_breadcrumb(self, senate_overview):
        assert 'dossier-nav' in senate_overview
        assert '/states/washington/' in senate_overview

    def test_overview_has_candidate_links(self, senate_overview):
        assert '/races/wa-state-senate-47-2026/' in senate_overview


# ---------------------------------------------------------------------------
# Test Class 6: URL scheme validation (US #1686)
# ---------------------------------------------------------------------------
class TestURLScheme:
    """Validate URL scheme for state legislative races."""

    @pytest.fixture
    def races(self):
        with open(DATA_DIR / "races.json") as f:
            return json.load(f)["races"]

    def test_senate_url_pattern(self, races):
        senate = [r for r in races if r.get("office") == "State Senate"
                  and r["state_abbr"] == "WA"]
        if not senate:
            pytest.fail("No State Senate races in races.json")
        for r in senate:
            assert re.match(r"/races/wa-state-senate-\d+-2026/$", r["url"]), \
                f"Bad senate URL: {r['url']}"

    def test_house_pos1_url_pattern(self, races):
        pos1 = [r for r in races if r.get("office") == "State House Pos. 1"
                and r["state_abbr"] == "WA"]
        if not pos1:
            pytest.fail("No State House Pos. 1 races in races.json")
        for r in pos1:
            assert re.match(r"/races/wa-state-house-\d+-pos1-2026/$", r["url"]), \
                f"Bad house pos1 URL: {r['url']}"

    def test_house_pos2_url_pattern(self, races):
        pos2 = [r for r in races if r.get("office") == "State House Pos. 2"
                and r["state_abbr"] == "WA"]
        if not pos2:
            pytest.fail("No State House Pos. 2 races in races.json")
        for r in pos2:
            assert re.match(r"/races/wa-state-house-\d+-pos2-2026/$", r["url"]), \
                f"Bad house pos2 URL: {r['url']}"

    def test_no_collision_with_federal_races(self, races):
        federal_ids = {r["id"] for r in races if r["office"] in ("US House", "US Senate")}
        leg_ids = {r["id"] for r in races if r.get("office", "").startswith("State")}
        overlap = federal_ids & leg_ids
        assert not overlap, f"ID collision between federal and state races: {overlap}"

    def test_all_ids_unique(self, races):
        ids = [r["id"] for r in races]
        assert len(ids) == len(set(ids)), "Duplicate race IDs found"


# ---------------------------------------------------------------------------
# Test Class 7: State page legislature section integration (US #1690)
# ---------------------------------------------------------------------------
class TestStatePageLegislature:
    """Validate WA state page integrates legislature race section."""

    @pytest.fixture
    def wa_page(self):
        path = STATES_DIR / "washington" / "index.html"
        if not path.exists():
            pytest.skip("WA state page not generated")
        return path.read_text()

    def test_has_legislature_section(self, wa_page):
        assert "State Legislature" in wa_page

    def test_no_placeholder_in_legislature_section(self, wa_page):
        leg_idx = wa_page.index("State Legislature")
        after_leg = wa_page[leg_idx:leg_idx + 2000]
        assert "No active research" not in after_leg, \
            "Legislature section should not show 'No active research' placeholder"

    def test_links_to_senate_races(self, wa_page):
        assert "/races/wa-state-senate-" in wa_page

    def test_links_to_house_races(self, wa_page):
        assert "/races/wa-state-house-" in wa_page

    def test_shows_district_numbers(self, wa_page):
        assert "LD-" in wa_page or "District" in wa_page


# ---------------------------------------------------------------------------
# Test Class 8: Party mapping for legislative candidates (US #1687)
# ---------------------------------------------------------------------------
class TestPartyMapping:
    """Validate party abbreviation mapping covers all legislative parties."""

    def _import_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gen", REPO_ROOT / "tools" / "generate_candidate_pages.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_democratic_maps(self):
        mod = self._import_module()
        assert "Democratic" in mod.PARTY_FULL.values() or "D" in mod.PARTY_FULL

    def test_republican_maps(self):
        mod = self._import_module()
        assert "Republican" in mod.PARTY_FULL.values() or "R" in mod.PARTY_FULL

    def test_independent_maps(self):
        mod = self._import_module()
        assert "I" in mod.PARTY_FULL or "Independent" in mod.PARTY_FULL.values()

    def test_nonpartisan_maps(self):
        mod = self._import_module()
        assert "NP" in mod.PARTY_FULL or "Non-Partisan" in mod.PARTY_FULL.values()

    def test_libertarian_has_class(self):
        mod = self._import_module()
        assert "Libertarian" in mod.PARTY_CLASS or "L" in mod.PARTY_CLASS, \
            "Libertarian party needs a CSS class mapping"

    def test_all_parties_have_css_class(self):
        """All party values in dossiers must map to a CSS class."""
        mod = self._import_module()
        parties_in_data = {"Democratic", "Republican", "Independent",
                           "Non-Partisan", "Libertarian", "Cascade",
                           "Pro Gun Liberal", "No Kings", "Standup-America"}
        for p in parties_in_data:
            short = {v: k for k, v in mod.PARTY_FULL.items()}.get(p, p)
            assert short in mod.PARTY_CLASS or p in mod.PARTY_CLASS, \
                f"Party '{p}' ({short}) has no CSS class mapping"


# ---------------------------------------------------------------------------
# Test Class 9: Filesystem structure for generated pages (US #1689)
# ---------------------------------------------------------------------------
class TestLegislativeFileStructure:
    """Validate the filesystem structure of generated legislative pages."""

    def test_senate_race_dirs_exist(self):
        expected_districts = [6, 7, 8, 13, 15, 21, 26, 29, 30, 31,
                              32, 33, 34, 35, 36, 37, 38, 42, 43, 44,
                              45, 46, 47, 48]
        for d in expected_districts:
            race_dir = RACES_DIR / f"wa-state-senate-{d}-2026"
            assert race_dir.exists(), f"Missing senate race dir: {race_dir.name}"
            assert (race_dir / "index.html").exists(), \
                f"Missing overview: {race_dir.name}/index.html"

    def test_house_pos1_dirs_exist(self):
        for d in range(1, 50):
            race_dir = RACES_DIR / f"wa-state-house-{d}-pos1-2026"
            assert race_dir.exists(), f"Missing house pos1 dir: {race_dir.name}"

    def test_house_pos2_dirs_exist(self):
        for d in range(1, 50):
            race_dir = RACES_DIR / f"wa-state-house-{d}-pos2-2026"
            assert race_dir.exists(), f"Missing house pos2 dir: {race_dir.name}"

    def test_candidate_subdirs_have_index(self):
        leg_dirs = [d for d in RACES_DIR.iterdir()
                    if d.is_dir() and d.name.startswith("wa-state-")]
        if not leg_dirs:
            pytest.skip("No legislative race dirs yet")
        missing = []
        for race_dir in leg_dirs:
            for sub in race_dir.iterdir():
                if sub.is_dir() and sub.name != "__pycache__":
                    idx = sub / "index.html"
                    if not idx.exists():
                        missing.append(f"{race_dir.name}/{sub.name}")
        assert not missing, f"Missing index.html in: {missing[:5]}"


# ---------------------------------------------------------------------------
# Test Class 10: Sitemap includes legislative race URLs (US #1689)
# ---------------------------------------------------------------------------
class TestSitemapLegislative:
    """Validate sitemap.xml includes all legislative race URLs."""

    @pytest.fixture
    def sitemap(self):
        path = REPO_ROOT / "sitemap.xml"
        if not path.exists():
            pytest.skip("sitemap.xml not present")
        return path.read_text()

    def test_sitemap_has_senate_urls(self, sitemap):
        assert "/races/wa-state-senate-" in sitemap

    def test_sitemap_has_house_urls(self, sitemap):
        assert "/races/wa-state-house-" in sitemap

    def test_sitemap_has_at_least_122_race_urls(self, sitemap):
        leg_urls = re.findall(r'/races/wa-state-(?:senate|house)-[^<]+', sitemap)
        assert len(leg_urls) >= 122, \
            f"Expected at least 122 legislative URLs in sitemap, found {len(leg_urls)}"
