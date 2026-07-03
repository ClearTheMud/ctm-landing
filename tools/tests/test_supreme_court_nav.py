#!/usr/bin/env python3
"""TDD tests for statewide judicial (Supreme Court) navigation on state hub pages.

ADO civic-tech (Epic #1610): Supreme Court races were built and present in
races.json but silently dropped from the state hub because render_state_page had
no bucket for judicial offices. This adds a "Statewide Judicial" section, gated so
that draft (stub) races do NOT render until they are enriched and flipped active.
"""

import importlib.util
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent

# Load generate_states.py as a module
_spec = importlib.util.spec_from_file_location(
    "generate_states", TOOLS_DIR / "generate_states.py"
)
generate_states = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generate_states)


WA_STATE = {
    "name": "Washington",
    "abbr": "WA",
    "slug": "washington",
    "capital": "Olympia",
    "house_districts": 10,
    "governor_next": 2028,
    "senate_class_up": 1,
}


def _sc_race(status):
    return {
        "id": "wa-supreme-court-justice-pos-1-2026",
        "state_abbr": "WA",
        "office": "WA Supreme Court Justice Pos. 1",
        "level": "statewide",
        "year": 2026,
        "title": "2026 WA Supreme Court Justice Pos. 1",
        "status": status,
        "url": "/races/wa-supreme-court-justice-pos-1-2026/",
        "primary_date": "August 4, 2026",
        "general_date": "November 3, 2026",
        "candidates": [
            {"name": "Jane Doe", "party": "Nonpartisan"},
            {"name": "John Roe", "party": "Nonpartisan"},
        ],
    }


class TestStatewideJudicialSection:
    def test_active_judicial_race_renders_with_heading_and_link(self):
        html = generate_states.render_state_page(WA_STATE, [_sc_race("active")], 2026)
        assert "Statewide Judicial" in html
        assert "/races/wa-supreme-court-justice-pos-1-2026/" in html

    def test_draft_judicial_race_is_gated_out(self):
        """Stub pages marked draft must not leak onto the live hub."""
        html = generate_states.render_state_page(WA_STATE, [_sc_race("draft")], 2026)
        assert "/races/wa-supreme-court-justice-pos-1-2026/" not in html

    def test_no_empty_judicial_heading_when_all_draft(self):
        html = generate_states.render_state_page(WA_STATE, [_sc_race("draft")], 2026)
        assert "Statewide Judicial" not in html
