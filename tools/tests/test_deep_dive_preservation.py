#!/usr/bin/env python3
"""The bulk stub generator must never overwrite a deep-dive page (ADO #1969).

`curated_races.json` was the only guard, and it is a hand-maintained list. On
2026-07-27 a full generator run overwrote 509 deep-dive dossiers with T1 stubs,
because those races had been converted by clearthemud's converter and nobody
had added them to the list. Net content loss on every one; the Skamania
assessor page went from a researched dossier to a stub with 85 lines removed.

A registry that must be updated by hand will drift again. The reliable signal
is the page itself: a deep-dive dossier says so in its own markup. This checks
the file on disk before writing over it, so the guard holds for pages nobody
remembered to register.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_candidate_pages import is_deep_dive_page  # noqa: E402

DEEP_DIVE = """<!DOCTYPE html>
<html lang="en"><head>
<title>Gabriel P Spencer, Skamania County Assessor | clearthemud.org</title>
<meta name="description" content="Deep-dive OSINT dossier for Gabriel Spencer (Democrat) running for Skamania County Assessor 2026.">
<meta property="og:type" content="article">
</head><body><h1>Candidate Dossier: Gabriel Spencer</h1></body></html>
"""

STUB = """<!DOCTYPE html>
<html lang="en"><head>
<title>Jane Doe, Adams County Sheriff | clearthemud.org</title>
<meta name="description" content="Verified candidate dossier for Jane Doe (Republican) running in the Adams County Sheriff.">
<meta property="og:type" content="website">
</head><body><h1>Jane Doe</h1></body></html>
"""


class TestDeepDiveDetection:
    def test_deep_dive_page_is_detected(self, tmp_path):
        p = tmp_path / "index.html"
        p.write_text(DEEP_DIVE)
        assert is_deep_dive_page(p) is True

    def test_stub_page_is_not_detected(self, tmp_path):
        p = tmp_path / "index.html"
        p.write_text(STUB)
        assert is_deep_dive_page(p) is False

    def test_missing_file_is_not_a_deep_dive(self, tmp_path):
        """A page that does not exist yet must be generated normally."""
        assert is_deep_dive_page(tmp_path / "absent.html") is False

    def test_unreadable_file_is_treated_as_deep_dive(self, tmp_path):
        """Fail safe: if we cannot tell, do not overwrite."""
        d = tmp_path / "adir"
        d.mkdir()
        assert is_deep_dive_page(d) is True


class TestMarkersThatIdentifyADeepDive:
    @pytest.mark.parametrize("marker", [
        '<meta name="description" content="Deep-dive OSINT dossier for X">',
        '<h1>Candidate Dossier: Someone</h1>',
        '<meta property="og:type" content="article">',
    ])
    def test_any_single_marker_is_enough(self, tmp_path, marker):
        """Deep-dive pages vary by vintage; one marker suffices to protect."""
        p = tmp_path / "index.html"
        p.write_text(f"<html><head>{marker}</head><body></body></html>")
        assert is_deep_dive_page(p) is True

    def test_the_word_dossier_alone_does_not_trigger(self, tmp_path):
        """Stubs say 'candidate dossier' in prose; that must not block them."""
        p = tmp_path / "index.html"
        p.write_text(
            '<html><head><meta name="description" '
            'content="Verified candidate dossier for Jane Doe">'
            '</head><body></body></html>')
        assert is_deep_dive_page(p) is False
