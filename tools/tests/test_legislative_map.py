#!/usr/bin/env python3
"""TDD tests for WA legislative district map — US #1691."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GEO_STATES = REPO_ROOT / "geo" / "states"
JS_DIR = REPO_ROOT / "js"
CSS_FILE = REPO_ROOT / "css" / "dossier.css"
STATES_DIR = REPO_ROOT / "states"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class TestLegislativeDistrictSVG:
    """Validate the WA legislative district SVG map structure."""

    @pytest.fixture
    def svg_tree(self):
        svg_path = GEO_STATES / "wa-legislative.svg"
        assert svg_path.exists(), "geo/states/wa-legislative.svg must exist"
        return ET.parse(svg_path)

    def test_svg_has_49_districts(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        districts = svg_tree.findall(".//svg:path[@class='leg-district']", ns)
        assert len(districts) == 49

    def test_district_ids_format(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        districts = svg_tree.findall(".//svg:path[@class='leg-district']", ns)
        for d in districts:
            assert d.get("id"), "District path missing id"
            assert re.match(r"WA-LD-\d+$", d.get("id")), \
                f"District id should match WA-LD-N: {d.get('id')}"

    def test_districts_have_data_attributes(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for d in svg_tree.findall(".//svg:path[@class='leg-district']", ns):
            assert d.get("data-district"), f"{d.get('id')} missing data-district"
            assert d.get("data-name"), f"{d.get('id')} missing data-name"

    def test_districts_have_titles(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for d in svg_tree.findall(".//svg:path[@class='leg-district']", ns):
            title = d.find("svg:title", ns)
            assert title is not None, f"{d.get('id')} missing <title>"
            assert title.text, f"{d.get('id')} has empty <title>"

    def test_svg_has_viewbox(self, svg_tree):
        root = svg_tree.getroot()
        assert root.get("viewBox"), "SVG must have viewBox attribute"

    def test_svg_has_aria_label(self, svg_tree):
        root = svg_tree.getroot()
        assert root.get("aria-label"), "SVG must have aria-label"

    def test_districts_group_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        group = svg_tree.find(".//svg:g[@id='leg-districts']", ns)
        assert group is not None, "SVG must have <g id='leg-districts'>"

    def test_no_inline_styles(self, svg_tree):
        for el in svg_tree.iter():
            assert el.get("style") is None, "No inline styles — use CSS classes"

    def test_district_numbers_cover_1_to_49(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        districts = svg_tree.findall(".//svg:path[@class='leg-district']", ns)
        nums = sorted(int(d.get("data-district")) for d in districts)
        assert nums == list(range(1, 50)), "Must cover districts 1-49"


class TestLegislativeMapJS:
    """Validate the legislative-map.js interactivity script."""

    @pytest.fixture
    def js_content(self):
        path = JS_DIR / "legislative-map.js"
        assert path.exists(), "js/legislative-map.js must exist"
        return path.read_text()

    def test_is_iife(self, js_content):
        assert js_content.strip().startswith("(function"), "Must be an IIFE"

    def test_reads_ctm_data_global(self, js_content):
        assert "CTM_LEG_DATA" in js_content

    def test_has_click_handler(self, js_content):
        assert "click" in js_content

    def test_has_keyboard_handler(self, js_content):
        assert "keydown" in js_content or "keypress" in js_content

    def test_applies_active_class(self, js_content):
        assert "leg-district--active" in js_content

    def test_applies_inactive_class(self, js_content):
        assert "leg-district--inactive" in js_content

    def test_sets_tabindex(self, js_content):
        assert "tabindex" in js_content.lower() or "tabIndex" in js_content


class TestLegislativeMapCSS:
    """Validate CSS rules for legislative district map."""

    @pytest.fixture
    def css(self):
        return CSS_FILE.read_text()

    def test_has_container_class(self, css):
        assert "legislative-map-container" in css

    def test_has_active_class(self, css):
        assert "leg-district--active" in css

    def test_has_inactive_class(self, css):
        assert "leg-district--inactive" in css

    def test_has_hover_rule(self, css):
        assert "leg-district--active:hover" in css or \
            "leg-district--active:focus" in css


class TestStatePageLegislativeMap:
    """Validate the WA state page includes the legislative district map."""

    @pytest.fixture
    def wa_page(self):
        path = STATES_DIR / "washington" / "index.html"
        if not path.exists():
            pytest.skip("WA state page not generated")
        return path.read_text()

    def test_has_legislative_map_container(self, wa_page):
        assert "legislative-map-container" in wa_page

    def test_has_legislative_map_js(self, wa_page):
        assert "legislative-map.js" in wa_page

    def test_has_ctm_leg_data(self, wa_page):
        assert "CTM_LEG_DATA" in wa_page

    def test_has_map_legend(self, wa_page):
        leg_idx = wa_page.index("legislative-map-container")
        end_idx = wa_page.index("</div>", wa_page.index("map-legend", leg_idx)) + 10 \
            if "map-legend" in wa_page[leg_idx:] else leg_idx + 500000
        section = wa_page[leg_idx:end_idx]
        assert "map-legend" in section

    def test_inline_svg_present(self, wa_page):
        assert "leg-districts" in wa_page, "SVG group id should be in page"
