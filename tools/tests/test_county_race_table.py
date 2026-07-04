#!/usr/bin/env python3
"""Tests for county-hub race-table URL resolution.

A county_races entry may carry an explicit race_id when the registry slug does not
match the office-name slug (council districts, or a malformed PUD id). Without it,
the URL is derived by slugifying the office name.

ADO Epic #1610 (Clark County council/PUD hub wiring).
"""
import importlib.util
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("generate_states", TOOLS_DIR / "generate_states.py")
generate_states = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generate_states)

render = generate_states.render_county_race_table


def _race(office, race_id=None):
    r = {"office": office, "candidates": [{"name": "Jane Doe", "election_status": "In Primary"}]}
    if race_id:
        r["race_id"] = race_id
    return r


class TestCountyRaceTableUrls:
    def test_office_slug_derivation_without_race_id(self):
        html = render([_race("County Assessor")], "clark", "wa")
        assert 'href="/races/wa-clark-county-assessor-2026/"' in html

    def test_explicit_race_id_overrides_office_slug(self):
        # Malformed/registry-specific id that office slugging would never produce.
        html = render(
            [_race("PUD Commissioner District 3", "wa-clark-pud-pud-commissioner-dist-3-2026")],
            "clark", "wa",
        )
        assert 'href="/races/wa-clark-pud-pud-commissioner-dist-3-2026/"' in html
        # The clean display name is still shown as link text.
        assert ">PUD Commissioner District 3</a>" in html
        # It must NOT emit the naive office-slug URL.
        assert "pud-commissioner-district-3-2026/" not in html.replace(
            "pud-pud-commissioner-dist-3-2026/", ""
        )

    def test_council_district_explicit_id(self):
        html = render(
            [_race("County Council District 1", "wa-clark-county-council-dist-1-2026")],
            "clark", "wa",
        )
        assert 'href="/races/wa-clark-county-council-dist-1-2026/"' in html
        assert ">County Council District 1</a>" in html
