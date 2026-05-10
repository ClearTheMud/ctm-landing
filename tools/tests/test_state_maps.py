#!/usr/bin/env python3
"""Tests for state-level district map system — TDD: written before implementation."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GEO_STATES = REPO_ROOT / "geo" / "states"
JS_DIR = REPO_ROOT / "js"
CSS_FILE = REPO_ROOT / "css" / "dossier.css"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class TestWADistrictSVG:
    """Validate the WA congressional district SVG structure."""

    @pytest.fixture
    def svg_tree(self):
        svg_path = GEO_STATES / "wa-districts.svg"
        assert svg_path.exists(), "geo/states/wa-districts.svg must exist"
        return ET.parse(svg_path)

    def test_svg_has_10_districts(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        districts = svg_tree.findall(".//svg:path[@class='district']", ns)
        assert len(districts) == 10

    def test_district_ids_follow_convention(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        districts = svg_tree.findall(".//svg:path[@class='district']", ns)
        ids = sorted(d.get("id") for d in districts)
        expected = [f"WA-{i:02d}" for i in range(1, 11)]
        assert ids == expected

    def test_districts_have_required_data_attributes(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for d in svg_tree.findall(".//svg:path[@class='district']", ns):
            assert d.get("data-district"), f"{d.get('id')} missing data-district"
            assert d.get("data-name"), f"{d.get('id')} missing data-name"
            assert d.get("data-slug"), f"{d.get('id')} missing data-slug"

    def test_districts_have_title_children(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for d in svg_tree.findall(".//svg:path[@class='district']", ns):
            title = d.find("svg:title", ns)
            assert title is not None, f"{d.get('id')} missing <title>"
            assert title.text, f"{d.get('id')} has empty <title>"

    def test_svg_has_viewbox(self, svg_tree):
        root = svg_tree.getroot()
        assert root.get("viewBox"), "SVG must have viewBox attribute"

    def test_svg_has_aria_label(self, svg_tree):
        root = svg_tree.getroot()
        assert root.get("aria-label"), "SVG must have aria-label for accessibility"

    def test_districts_group_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        group = svg_tree.find(".//svg:g[@id='districts']", ns)
        assert group is not None, "SVG must have <g id='districts'>"

    def test_no_inline_styles_in_svg(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for el in svg_tree.iter():
            assert el.get("style") is None, f"Element {el.tag} has inline style — use CSS classes"

    def test_data_slug_matches_race_id_pattern(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for d in svg_tree.findall(".//svg:path[@class='district']", ns):
            slug = d.get("data-slug")
            assert re.match(r"^wa-house-\d{1,2}-2026$", slug), f"Bad slug: {slug}"


class TestStateMapJS:
    """Validate state-map.js exists and follows patterns from us-map.js."""

    @pytest.fixture
    def js_content(self):
        js_path = JS_DIR / "state-map.js"
        assert js_path.exists(), "js/state-map.js must exist"
        return js_path.read_text()

    def test_reads_district_data_global(self, js_content):
        assert "CTM_DISTRICT_DATA" in js_content

    def test_queries_district_class(self, js_content):
        assert ".district" in js_content

    def test_applies_active_inactive_classes(self, js_content):
        assert "district--active" in js_content
        assert "district--inactive" in js_content

    def test_creates_tooltip(self, js_content):
        assert "tooltip" in js_content.lower()

    def test_keyboard_navigation(self, js_content):
        assert "keydown" in js_content
        assert "Enter" in js_content

    def test_aria_attributes(self, js_content):
        assert "aria-label" in js_content
        assert "tabindex" in js_content

    def test_uses_strict_mode(self, js_content):
        assert "'use strict'" in js_content

    def test_iife_pattern(self, js_content):
        assert js_content.strip().startswith("(function")


class TestDossierCSSDistrictRules:
    """Validate CSS has district map rules scoped under .district-map-container."""

    @pytest.fixture
    def css_content(self):
        return CSS_FILE.read_text()

    def test_district_base_scoped_under_container(self, css_content):
        assert ".district-map-container .district" in css_content

    def test_district_active_scoped_under_container(self, css_content):
        assert ".district-map-container .district--active" in css_content

    def test_district_inactive_scoped_under_container(self, css_content):
        assert ".district-map-container .district--inactive" in css_content

    def test_district_glow_animation(self, css_content):
        assert "district-glow" in css_content

    def test_district_stroke_not_near_black(self, css_content):
        assert "#253545" not in css_content, "Stroke #253545 is too dark on navy background"

    def test_district_stroke_is_visible(self, css_content):
        assert "#5a7a94" in css_content, "District strokes should use #5a7a94 for visibility"


class TestRacesJSON:
    """Validate races.json has WA House races."""

    @pytest.fixture
    def races(self):
        with open(DATA_DIR / "races.json") as f:
            return json.load(f)["races"]

    def test_wa_house_races_exist(self, races):
        wa_house = [r for r in races if r["state_abbr"] == "WA" and r["office"] == "US House"]
        assert len(wa_house) == 10, f"Expected 10 WA US House races, got {len(wa_house)}"

    def test_wa_races_have_district_field(self, races):
        wa_house = [r for r in races if r["state_abbr"] == "WA" and "House" in r["office"]]
        for race in wa_house:
            assert "district" in race, f"Race {race['id']} missing 'district' field"

    def test_wa_races_have_candidates(self, races):
        wa_house = [r for r in races if r["state_abbr"] == "WA" and "House" in r["office"]]
        for race in wa_house:
            assert len(race["candidates"]) > 0, f"Race {race['id']} has no candidates"

    def test_wa_race_ids_follow_convention(self, races):
        wa_house = [r for r in races if r["state_abbr"] == "WA" and r["office"] == "US House"]
        ids = sorted([r["id"] for r in wa_house], key=lambda x: int(x.split("-")[2]))
        expected = [f"wa-house-{i}-2026" for i in range(1, 11)]
        assert ids == expected

    def test_candidates_have_required_fields(self, races):
        wa_house = [r for r in races if r["state_abbr"] == "WA" and "House" in r["office"]]
        for race in wa_house:
            for c in race["candidates"]:
                assert "name" in c, f"Candidate in {race['id']} missing name"
                assert "party" in c, f"Candidate in {race['id']} missing party"


class TestCandidatePages:
    """Validate generated candidate dossier pages."""

    @pytest.fixture
    def jayapal_page(self):
        path = REPO_ROOT / "races" / "wa-house-7-2026" / "jayapal" / "index.html"
        assert path.exists(), "Jayapal dossier page must exist"
        return path.read_text()

    def test_no_unknown_in_expenditures(self, jayapal_page):
        assert "Unknown" not in jayapal_page, "Expenditure rows should not contain 'Unknown'"

    def test_expenditures_show_vendor_names(self, jayapal_page):
        assert "SYMMETRY MEDIA" in jayapal_page or "MEDIA BUY" in jayapal_page, \
            "Expenditure table should show actual vendor names or purposes"

    def test_no_na_raised_text(self):
        overview = (REPO_ROOT / "races" / "wa-house-7-2026" / "index.html").read_text()
        assert "Raised: N/A" not in overview, "Should say 'Not reported' instead of 'N/A'"

    def test_breadcrumb_links_to_washington(self, jayapal_page):
        assert "/states/washington/" in jayapal_page

    def test_has_campaign_finance_section(self, jayapal_page):
        assert "Campaign Finance" in jayapal_page

    def test_has_source_verification(self, jayapal_page):
        assert "Source Verification" in jayapal_page


class TestGeneratorDistrictSupport:
    """Validate generate_states.py supports district maps."""

    @pytest.fixture
    def generator_content(self):
        gen_path = REPO_ROOT / "tools" / "generate_states.py"
        return gen_path.read_text()

    def test_has_load_state_svg_function(self, generator_content):
        assert "def load_state_svg" in generator_content

    def test_has_district_data_injection(self, generator_content):
        assert "CTM_DISTRICT_DATA" in generator_content

    def test_references_state_map_js(self, generator_content):
        assert "state-map.js" in generator_content
