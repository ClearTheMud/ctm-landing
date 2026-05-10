#!/usr/bin/env python3
"""TDD tests for county and place map system — written before implementation."""

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
STATES_DIR = REPO_ROOT / "states"


# ---------------------------------------------------------------------------
# Test Class 1: WA County SVG structure (ADO #1674)
# ---------------------------------------------------------------------------
class TestWACountySVG:
    """Validate the WA county SVG map structure."""

    @pytest.fixture
    def svg_tree(self):
        svg_path = GEO_STATES / "wa-counties.svg"
        assert svg_path.exists(), "geo/states/wa-counties.svg must exist"
        return ET.parse(svg_path)

    def test_svg_has_39_counties(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        counties = svg_tree.findall(".//svg:path[@class='county']", ns)
        assert len(counties) == 39

    def test_county_ids_use_fips(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        counties = svg_tree.findall(".//svg:path[@class='county']", ns)
        for c in counties:
            assert c.get("id"), "County path missing id"
            assert c.get("id").startswith("WA-"), f"County id should start with WA-: {c.get('id')}"

    def test_counties_have_required_data_attributes(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for c in svg_tree.findall(".//svg:path[@class='county']", ns):
            assert c.get("data-county"), f"{c.get('id')} missing data-county"
            assert c.get("data-name"), f"{c.get('id')} missing data-name"
            assert c.get("data-slug"), f"{c.get('id')} missing data-slug"
            assert c.get("data-fips"), f"{c.get('id')} missing data-fips"

    def test_thurston_county_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        thurston = svg_tree.find(".//svg:path[@data-slug='thurston']", ns)
        assert thurston is not None, "Thurston County must be in the SVG"
        assert thurston.get("data-fips") == "067"

    def test_counties_have_title_children(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for c in svg_tree.findall(".//svg:path[@class='county']", ns):
            title = c.find("svg:title", ns)
            assert title is not None, f"{c.get('id')} missing <title>"
            assert title.text, f"{c.get('id')} has empty <title>"

    def test_svg_has_viewbox(self, svg_tree):
        root = svg_tree.getroot()
        assert root.get("viewBox"), "SVG must have viewBox attribute"

    def test_svg_has_aria_label(self, svg_tree):
        root = svg_tree.getroot()
        assert root.get("aria-label"), "SVG must have aria-label"

    def test_counties_group_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        group = svg_tree.find(".//svg:g[@id='counties']", ns)
        assert group is not None, "SVG must have <g id='counties'>"

    def test_no_inline_styles(self, svg_tree):
        for el in svg_tree.iter():
            assert el.get("style") is None, f"Element has inline style — use CSS classes"

    def test_known_counties_present(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        expected = ["king", "pierce", "snohomish", "thurston", "clark", "spokane", "yakima"]
        for slug in expected:
            match = svg_tree.find(f".//svg:path[@data-slug='{slug}']", ns)
            assert match is not None, f"County '{slug}' not found in SVG"


# ---------------------------------------------------------------------------
# Test Class 2: Thurston County place SVG structure (ADO #1675)
# ---------------------------------------------------------------------------
class TestThurstonPlaceSVG:
    """Validate the Thurston County place (city/town) SVG."""

    @pytest.fixture
    def svg_tree(self):
        svg_path = GEO_STATES / "wa-thurston-places.svg"
        assert svg_path.exists(), "geo/states/wa-thurston-places.svg must exist"
        return ET.parse(svg_path)

    def test_svg_has_places(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        places = svg_tree.findall(".//svg:path[@class='place']", ns)
        assert len(places) >= 5, f"Expected at least 5 places, got {len(places)}"

    def test_olympia_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        olympia = svg_tree.find(".//svg:path[@data-slug='olympia']", ns)
        assert olympia is not None, "Olympia must be in the SVG"

    def test_lacey_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        lacey = svg_tree.find(".//svg:path[@data-slug='lacey']", ns)
        assert lacey is not None, "Lacey must be in the SVG"

    def test_tumwater_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        tumwater = svg_tree.find(".//svg:path[@data-slug='tumwater']", ns)
        assert tumwater is not None, "Tumwater must be in the SVG"

    def test_places_have_required_data_attributes(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for p in svg_tree.findall(".//svg:path[@class='place']", ns):
            assert p.get("data-name"), f"{p.get('id')} missing data-name"
            assert p.get("data-slug"), f"{p.get('id')} missing data-slug"

    def test_places_have_title_children(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for p in svg_tree.findall(".//svg:path[@class='place']", ns):
            title = p.find("svg:title", ns)
            assert title is not None, f"{p.get('id')} missing <title>"

    def test_svg_has_viewbox_and_aria(self, svg_tree):
        root = svg_tree.getroot()
        assert root.get("viewBox"), "SVG must have viewBox"
        assert root.get("aria-label"), "SVG must have aria-label"

    def test_places_group_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        group = svg_tree.find(".//svg:g[@id='places']", ns)
        assert group is not None, "SVG must have <g id='places'>"

    def test_county_boundary_outline_exists(self, svg_tree):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        boundary = svg_tree.find(".//svg:path[@class='county-boundary']", ns)
        assert boundary is not None, "SVG must include county boundary outline"


# ---------------------------------------------------------------------------
# Test Class 3: counties.json and places.json (ADO #1676)
# ---------------------------------------------------------------------------
class TestCountiesJSON:
    """Validate counties.json data structure."""

    @pytest.fixture
    def counties(self):
        path = DATA_DIR / "counties.json"
        assert path.exists(), "tools/data/counties.json must exist"
        with open(path) as f:
            return json.load(f)

    def test_wa_has_39_counties(self, counties):
        wa = counties.get("WA", [])
        assert len(wa) == 39, f"Expected 39 WA counties, got {len(wa)}"

    def test_county_required_fields(self, counties):
        for c in counties.get("WA", []):
            assert "name" in c, f"County missing 'name'"
            assert "fips" in c, f"County missing 'fips'"
            assert "slug" in c, f"County missing 'slug'"

    def test_thurston_county_data(self, counties):
        wa = counties.get("WA", [])
        thurston = [c for c in wa if c["slug"] == "thurston"]
        assert len(thurston) == 1, "Thurston County must exist"
        assert thurston[0]["fips"] == "067"
        assert thurston[0]["name"] == "Thurston"

    def test_county_slugs_are_lowercase_hyphenated(self, counties):
        for c in counties.get("WA", []):
            assert c["slug"] == c["slug"].lower(), f"Slug not lowercase: {c['slug']}"
            assert " " not in c["slug"], f"Slug has spaces: {c['slug']}"


class TestPlacesJSON:
    """Validate places.json data structure."""

    @pytest.fixture
    def places(self):
        path = DATA_DIR / "places.json"
        assert path.exists(), "tools/data/places.json must exist"
        with open(path) as f:
            return json.load(f)

    def test_thurston_has_places(self, places):
        thurston = places.get("WA", {}).get("thurston", [])
        assert len(thurston) >= 5, f"Expected at least 5 Thurston places, got {len(thurston)}"

    def test_olympia_in_thurston(self, places):
        thurston = places.get("WA", {}).get("thurston", [])
        olympia = [p for p in thurston if p["slug"] == "olympia"]
        assert len(olympia) == 1, "Olympia must be in Thurston places"

    def test_place_required_fields(self, places):
        for p in places.get("WA", {}).get("thurston", []):
            assert "name" in p, f"Place missing 'name'"
            assert "slug" in p, f"Place missing 'slug'"
            assert "type" in p, f"Place missing 'type' (city/town/cdp)"


# ---------------------------------------------------------------------------
# Test Class 4: County hub page and state page integration (ADO #1677, #1678)
# ---------------------------------------------------------------------------
class TestCountyHubPage:
    """Validate county hub page structure."""

    @pytest.fixture
    def thurston_page(self):
        path = STATES_DIR / "washington" / "thurston" / "index.html"
        assert path.exists(), "states/washington/thurston/index.html must exist"
        return path.read_text()

    def test_breadcrumb_has_washington(self, thurston_page):
        assert "/states/washington/" in thurston_page

    def test_breadcrumb_has_thurston(self, thurston_page):
        assert "Thurston" in thurston_page

    def test_has_place_map_container(self, thurston_page):
        assert "place-map-container" in thurston_page

    def test_references_place_map_js(self, thurston_page):
        assert "place-map.js" in thurston_page

    def test_has_classification_bar(self, thurston_page):
        assert "TLP:GREEN" in thurston_page


class TestStatePageCountyMap:
    """Validate county map is integrated into state hub page."""

    @pytest.fixture
    def wa_page(self):
        path = STATES_DIR / "washington" / "index.html"
        return path.read_text()

    def test_has_county_map_container(self, wa_page):
        assert "county-map-container" in wa_page

    def test_has_county_data_global(self, wa_page):
        assert "CTM_COUNTY_DATA" in wa_page

    def test_references_county_map_js(self, wa_page):
        assert "county-map.js" in wa_page

    def test_still_has_district_map(self, wa_page):
        assert "district-map-container" in wa_page


# ---------------------------------------------------------------------------
# Test Class 5: CSS and JS for county/place maps (ADO #1679)
# ---------------------------------------------------------------------------
class TestCountyMapCSS:
    """Validate CSS has county and place map rules."""

    @pytest.fixture
    def css_content(self):
        return CSS_FILE.read_text()

    def test_county_container_exists(self, css_content):
        assert ".county-map-container" in css_content

    def test_county_active_scoped(self, css_content):
        assert ".county-map-container .county--active" in css_content

    def test_county_inactive_scoped(self, css_content):
        assert ".county-map-container .county--inactive" in css_content

    def test_place_container_exists(self, css_content):
        assert ".place-map-container" in css_content

    def test_place_active_scoped(self, css_content):
        assert ".place-map-container .place--active" in css_content

    def test_place_inactive_scoped(self, css_content):
        assert ".place-map-container .place--inactive" in css_content

    def test_county_glow_animation(self, css_content):
        assert "county-glow" in css_content

    def test_place_glow_animation(self, css_content):
        assert "place-glow" in css_content


class TestCountyMapJS:
    """Validate county-map.js exists and follows patterns."""

    @pytest.fixture
    def js_content(self):
        js_path = JS_DIR / "county-map.js"
        assert js_path.exists(), "js/county-map.js must exist"
        return js_path.read_text()

    def test_reads_county_data_global(self, js_content):
        assert "CTM_COUNTY_DATA" in js_content

    def test_queries_county_class(self, js_content):
        assert ".county" in js_content

    def test_applies_active_inactive_classes(self, js_content):
        assert "county--active" in js_content
        assert "county--inactive" in js_content

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


class TestPlaceMapJS:
    """Validate place-map.js exists and follows patterns."""

    @pytest.fixture
    def js_content(self):
        js_path = JS_DIR / "place-map.js"
        assert js_path.exists(), "js/place-map.js must exist"
        return js_path.read_text()

    def test_reads_place_data_global(self, js_content):
        assert "CTM_PLACE_DATA" in js_content

    def test_queries_place_class(self, js_content):
        assert ".place" in js_content

    def test_applies_active_inactive_classes(self, js_content):
        assert "place--active" in js_content
        assert "place--inactive" in js_content

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
