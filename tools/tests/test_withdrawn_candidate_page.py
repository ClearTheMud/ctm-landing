"""A withdrawn candidate's own page must not present them as running (ADO #2014).

#1992 fixed the roster cards. It stopped there. Withdrawn candidates are kept ON
the roster deliberately, so a reader who remembers the name still learns what
happened, which means they pass every roster gate and their own page rendered as
though nothing had happened.

Audited 2026-07-31, four days before the primary: all 11 withdrawn candidates had
a live page, none carried any withdrawal notice, 9 said "running", and 7 rendered
a Campaign Finance section. A reader clicked a card correctly marked WITHDRAWN and
landed on a page presenting the person as an active candidate.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generate_candidate_pages import render_candidate_page  # noqa: E402

STATE = {"name": "Washington", "slug": "washington"}
RACE = {
    "id": "wa-kitsap-commissioner-district-3-2026",
    "title": "Kitsap County Commissioner District 3",
    "url": "/races/wa-kitsap-commissioner-district-3-2026/",
    "office": "County Commissioner",
    "level": "county",
    "county": "Kitsap",
    "county_slug": "kitsap",
    "state_abbr": "WA",
    "candidates": [],
}


def _candidate(withdrawn):
    c = {
        "name": "Kitty Candelaria",
        "party": "R",
        "role": "challenger",
        "url": "/races/wa-kitsap-commissioner-district-3-2026/candelaria/",
    }
    if withdrawn:
        c["withdrawn"] = True
    return c


def _render(withdrawn, dossier=None):
    return render_candidate_page(RACE, _candidate(withdrawn), dossier, STATE)


class TestWithdrawnCandidatePage:
    def test_does_not_say_running(self):
        assert "running in the" not in _render(True)

    def test_status_field_is_not_challenger(self):
        """The live page read "Status: Challenger" for someone off the ballot."""
        html = _render(True)
        assert "Status:</strong> Challenger" not in html

    def test_states_the_withdrawal(self):
        assert "withdrew from the race" in _render(True).lower()

    def test_keeps_the_candidate_name(self):
        """Never removed: #1992's principle is that the reader who remembers the
        name must learn what happened rather than find nothing."""
        assert "Kitty Candelaria" in _render(True)

    def test_bluf_does_not_assert_an_active_candidacy(self):
        html = _render(True)
        assert "is a Republican challenger in the" not in html

    def test_finance_is_scoped_to_before_the_withdrawal(self):
        """A PDC refresh must not write a live-looking total onto the page of
        someone who is not on the ballot."""
        dossier = {
            "meta": {},
            "state_campaign_finance": {
                "total_raised": {"claim": "$12,400"},
                "total_spent": {"claim": "$9,100"},
            },
        }
        html = _render(True, dossier)
        assert "before withdrawing" in html.lower()


class TestActivePageUnchanged:
    def test_active_candidate_still_reads_as_running(self):
        html = _render(False)
        assert "running in the" in html
        assert "Status:</strong> Challenger" in html

    def test_active_candidate_has_no_withdrawal_notice(self):
        assert "withdrew from the race" not in _render(False).lower()
