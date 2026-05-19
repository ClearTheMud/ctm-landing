#!/usr/bin/env python3
"""Tests for ADO #1713 — US map Senate race indicators. TDD: written before implementation."""

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CSS_FILE = REPO_ROOT / "css" / "dossier.css"
JS_FILE = REPO_ROOT / "js" / "us-map.js"
GEN_FILE = REPO_ROOT / "tools" / "generate_states.py"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SENATE_2026_STATES = {
    "AL", "AK", "AR", "CO", "DE", "GA", "ID", "IL", "IA", "KS",
    "KY", "LA", "ME", "MA", "MI", "MN", "MS", "MT", "NE", "NH",
    "NJ", "NM", "NC", "OK", "OR", "RI", "SC", "SD", "TN", "TX",
    "VA", "WV", "WY",
}


class TestSenateCSS:
    """CSS must have a third visual state for Senate race markers."""

    @pytest.fixture
    def css(self):
        return CSS_FILE.read_text()

    def test_has_senate_fill_class(self, css):
        assert ".map-container .state--senate" in css

    def test_senate_has_distinct_fill(self, css):
        match = re.search(r'\.state--senate\s*\{[^}]*fill:\s*(#[0-9a-fA-F]{6})', css)
        assert match, "state--senate must define a fill color"
        color = match.group(1).lower()
        assert color != "#d4a83a", "Senate fill must differ from active (gold)"
        assert color != "#3d5570", "Senate fill must differ from inactive (dark blue)"

    def test_senate_has_hover_state(self, css):
        assert ".state--senate:hover" in css

    def test_senate_has_cursor_pointer(self, css):
        match = re.search(r'\.state--senate\s*\{[^}]*cursor:\s*pointer', css)
        assert match, "Senate states should be clickable"

    def test_legend_swatch_senate(self, css):
        assert "map-legend-swatch--senate" in css

    def test_senate_glow_animation(self, css):
        assert "senate-glow" in css


class TestSenateJS:
    """us-map.js must handle the senate flag in CTM_STATE_DATA."""

    @pytest.fixture
    def js(self):
        return JS_FILE.read_text()

    def test_checks_senate_flag(self, js):
        assert "senate" in js, "JS must reference senate property from state data"

    def test_applies_senate_class(self, js):
        assert "state--senate" in js

    def test_senate_tooltip_text(self, js):
        assert "Senate" in js, "Tooltip should mention Senate race"


class TestGeneratorSenateData:
    """generate_states.py must inject senate flag into CTM_STATE_DATA."""

    @pytest.fixture
    def gen(self):
        return GEN_FILE.read_text()

    def test_has_senate_states_constant(self, gen):
        assert "SENATE_2026" in gen

    def test_senate_flag_in_state_data(self, gen):
        assert '"senate"' in gen or "'senate'" in gen

    def test_senate_legend_item(self, gen):
        assert "map-legend-swatch--senate" in gen

    def test_legend_has_three_items(self, gen):
        count = gen.count("map-legend-item")
        assert count >= 3, f"Legend should have at least 3 items, found {count}"


class TestGeneratedOutput:
    """The generated states/index.html must contain senate markers."""

    @pytest.fixture
    def states_page(self):
        path = REPO_ROOT / "states" / "index.html"
        assert path.exists(), "states/index.html must exist"
        return path.read_text()

    def test_ctm_state_data_has_senate_flags(self, states_page):
        match = re.search(r'CTM_STATE_DATA\s*=\s*(\{.*?\});', states_page)
        assert match, "CTM_STATE_DATA must exist in states page"
        data = json.loads(match.group(1))
        senate_in_data = {k for k, v in data.items() if v.get("senate")}
        assert len(senate_in_data) == 33, f"Expected 33 senate states, got {len(senate_in_data)}"

    def test_senate_legend_present(self, states_page):
        assert "map-legend-swatch--senate" in states_page
        assert "Senate" in states_page

    def test_all_33_senate_states_flagged(self, states_page):
        match = re.search(r'CTM_STATE_DATA\s*=\s*(\{.*?\});', states_page)
        data = json.loads(match.group(1))
        senate_in_data = {k for k, v in data.items() if v.get("senate")}
        missing = SENATE_2026_STATES - senate_in_data
        assert not missing, f"Missing senate flags for: {missing}"


class TestSenateStateCount:
    """Verify the 33 Class II Senate seats are correct."""

    def test_exactly_33_senate_states(self):
        assert len(SENATE_2026_STATES) == 33

    def test_no_class_3_states_included(self):
        class_3_2026 = {"AZ", "CA", "CT", "FL", "HI", "IN", "MD", "MO",
                        "NV", "NY", "ND", "OH", "PA", "UT", "VT", "WA", "WI"}
        overlap = SENATE_2026_STATES & class_3_2026
        assert not overlap, f"Class III states wrongly in senate list: {overlap}"
