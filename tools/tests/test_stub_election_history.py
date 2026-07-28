#!/usr/bin/env python3
"""Election History on T1 stub candidate pages (ADO #1969).

Election history reached only the 163 deep-dive races, which are rendered by
clearthemud's convert_to_ctm_landing.py. The other 437 published races are T1
stubs rendered here, and this generator had no election-history path at all.

The load-bearing test in this file is the caveat one. SOS rows are matched by
printed name with no identity key behind them, so a page that shows them
without saying so is asserting an identity it has not verified. The deep-dive
renderer already states that; these pages must state the same thing the same
way, or the site explains the same limitation two different ways.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_candidate_pages import render_candidate_page  # noqa: E402

RACE = {
    "id": "wa-adams-sheriff-2026",
    "state_abbr": "WA",
    "state": "Washington",
    "year": 2026,
    "office": "Sheriff",
    "level": "county",
    "district": "",
    "title": "Adams County Sheriff 2026",
    "url": "/races/wa-adams-sheriff-2026/",
    "county": "Adams",
    "county_slug": "adams",
    "candidates": [],
}

CANDIDATE = {
    "name": "Jane Q Public",
    "lastname": "public",
    "party": "REPUBLICAN",
    "url": "/races/wa-adams-sheriff-2026/public/",
}

STATE_INFO = {"name": "Washington", "abbr": "WA", "slug": "washington"}


def _dossier(history):
    return {
        "meta": {
            "full_name": "Jane Q Public",
            "collected_date": "2026-05-09",
            "party": {"claim": "Republican", "confidence": "official"},
            "race": {"office": "Sheriff"},
        },
        "biographical": {},
        "campaign_finance": {},
        "election_history": history,
    }


SOS_ROWS = [
    {"year": 2022, "race": "Adams County Sheriff (General)",
     "result": "Won (1 of 2)", "source": "wa-sos"},
    {"year": 2018, "race": "Adams County Sheriff (General)",
     "result": "Lost (2 of 2)", "source": "wa-sos"},
]


def _render(history):
    return render_candidate_page(RACE, CANDIDATE, _dossier(history), STATE_INFO)


class TestElectionHistorySection:
    def test_section_appears_when_history_present(self):
        assert "Election History" in _render(SOS_ROWS)

    def test_section_absent_when_no_history(self):
        assert "Election History" not in _render([])

    def test_section_absent_when_key_missing_entirely(self):
        """Older dossier JSON predates the key; that must not crash a build."""
        dossier = _dossier([])
        del dossier["election_history"]
        html = render_candidate_page(RACE, CANDIDATE, dossier, STATE_INFO)
        assert "Election History" not in html

    def test_no_dossier_at_all_still_renders(self):
        html = render_candidate_page(RACE, CANDIDATE, None, STATE_INFO)
        assert "Election History" not in html
        assert "Jane Q Public" in html

    def test_rows_are_rendered(self):
        html = _render(SOS_ROWS)
        assert "2022" in html and "Won (1 of 2)" in html
        assert "2018" in html and "Lost (2 of 2)" in html

    def test_source_column_labels_sos_rows(self):
        assert "WA SOS" in _render(SOS_ROWS)


class TestNameMatchCaveat:
    """The honesty contract. Wording is pinned to the deep-dive renderer."""

    def test_caveat_shown_when_sos_rows_present(self):
        html = _render(SOS_ROWS)
        assert "matched by name" in html
        assert "not by a verified identity" in html

    def test_caveat_wording_matches_deep_dive_renderer(self):
        """Byte-identical to convert_to_ctm_landing.py, so the site says it once."""
        expected = (
            "Rows marked WA SOS come from official Washington Secretary of State "
            "election results and are <strong>matched by name</strong>, not by a "
            "verified identity. A candidate who shares a name with another "
            "person may show results that are not theirs. "
            '<a href="mailto:contact@clearthemud.org">Tell us</a> if you spot one.'
        )
        assert expected in _render(SOS_ROWS)

    def test_no_caveat_when_all_rows_are_researched(self):
        researched = [
            {"year": 2022, "race": "Adams County Sheriff",
             "result": "Won", "source": "research"},
        ]
        html = _render(researched)
        assert "Election History" in html
        assert "matched by name" not in html


class TestSectionNumbering:
    def test_source_verification_follows_election_history(self):
        html = _render(SOS_ROWS)
        assert html.index("Election History") < html.index("Source Verification")

    def test_numbering_has_no_gap_without_history(self):
        html = _render([])
        assert '<span class="section-num">3</span> Source Verification' in html

    def test_numbering_has_no_duplicate_with_history(self):
        html = _render(SOS_ROWS)
        assert '<span class="section-num">3</span> Election History' in html
        assert '<span class="section-num">4</span> Source Verification' in html


class TestEscaping:
    def test_row_values_are_escaped(self):
        nasty = [
            {"year": 2022, "race": "<script>alert(1)</script>",
             "result": "Won", "source": "wa-sos"},
        ]
        html = _render(nasty)
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html
