#!/usr/bin/env python3
"""TDD tests for the dedicated Statewide Judicial hub page.

ADO civic-tech #1944 (Epic #1916): a dedicated /states/{slug}/judicial/ hub that
collects the WA Supreme Court and Court of Appeals tiers on one page, and turns the
state-page "Statewide Judicial" header into a link to that hub. Draft (stub) Court
of Appeals races stay gated out until enriched.
"""

import importlib.util
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent

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


def _sc_race():
    return {
        "id": "wa-supreme-court-justice-pos-1-2026",
        "state_abbr": "WA",
        "office": "WA Supreme Court Justice Pos. 1",
        "status": "active",
        "title": "2026 WA Supreme Court Justice Pos. 1",
        "url": "/races/wa-supreme-court-justice-pos-1-2026/",
        "primary_date": "August 4, 2026",
        "general_date": "November 3, 2026",
        "candidates": [
            {"name": "Jane Doe", "party": "Nonpartisan"},
            {"name": "John Roe", "party": "Nonpartisan"},
        ],
    }


def _appeals_race(status="draft"):
    return {
        "id": "wa-appeals-div-1-dist-1-pos-5-2026",
        "state_abbr": "WA",
        "office": "Court of Appeals Div. 1 Dist. 1 Pos. 5",
        "status": status,
        "title": "2026 Court of Appeals Div. 1 Dist. 1 Pos. 5",
        "url": "/races/wa-appeals-div-1-dist-1-pos-5-2026/",
        "candidates": [{"name": "Jane Appeals", "party": "Nonpartisan"}],
    }


class TestRenderJudicialPage:
    def test_renders_both_court_tiers(self):
        html = generate_states.render_judicial_page(
            WA_STATE, [_sc_race(), _appeals_race()], 2026
        )
        assert "Supreme Court" in html
        assert "Court of Appeals" in html

    def test_active_supreme_court_race_links(self):
        html = generate_states.render_judicial_page(WA_STATE, [_sc_race()], 2026)
        assert "/races/wa-supreme-court-justice-pos-1-2026/" in html

    def test_breadcrumb_and_canonical(self):
        html = generate_states.render_judicial_page(WA_STATE, [_sc_race()], 2026)
        assert 'href="https://clearthemud.org/states/washington/judicial/"' in html
        assert "https://clearthemud.org/states/washington/judicial/" in html
        # Breadcrumb ends on the current (non-link) Judicial crumb
        assert '<span class="nav-current">Judicial</span>' in html
        assert '<a href="/states/washington/">Washington</a>' in html

    def test_draft_appeals_race_is_gated_out(self):
        html = generate_states.render_judicial_page(
            WA_STATE, [_sc_race(), _appeals_race("draft")], 2026
        )
        assert "/races/wa-appeals-div-1-dist-1-pos-5-2026/" not in html

    def test_active_appeals_race_links_when_enriched(self):
        html = generate_states.render_judicial_page(
            WA_STATE, [_sc_race(), _appeals_race("active")], 2026
        )
        assert "/races/wa-appeals-div-1-dist-1-pos-5-2026/" in html

    def test_appeals_coming_soon_note_when_all_draft(self):
        html = generate_states.render_judicial_page(
            WA_STATE, [_sc_race(), _appeals_race("draft")], 2026
        )
        # Section header still present, with a coming-soon note instead of links
        assert "Court of Appeals" in html
        assert "no-research" in html


class TestStatePageHeaderLinksToHub:
    def test_statewide_judicial_header_is_a_link(self):
        html = generate_states.render_state_page(WA_STATE, [_sc_race()], 2026)
        assert '<a href="/states/washington/judicial/">Statewide Judicial</a>' in html
