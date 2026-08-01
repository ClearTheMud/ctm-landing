"""Primary results on race hubs (ADO #2020).

Decisions taken 2026-07-31, before the 2026-08-04 primary:

  - show the FULL primary field, not just the two who advanced
  - eliminated candidates go under their own header, visually de-emphasised
  - publish partial counts between election night and certification, labelled
  - eliminated is NEVER inferred from absence

That last rule is the one with teeth. A candidate missing from the general
list may be eliminated, may have withdrawn after the primary, or may never
have been in the primary at all, because uncontested races skip it. One
observable, three facts. Asserting an unverified absence was the difference
between 3 pages and ~300 on #1915.

Certification matters too: Washington counts mail ballots for weeks and a
candidate trailing on election night can advance. Nothing says "eliminated"
without a certified result behind it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from primary_results import (  # noqa: E402
    BLOCK_END,
    BLOCK_START,
    build_primary_results_block,
    inject_primary_results,
)


def _cand(name, slug, outcome=None, **kw):
    c = {"name": name, "party": "D",
         "url": f"/races/wa-test-race-2026/{slug}/"}
    if outcome is not None:
        c["primary_result"] = {
            "outcome": outcome,
            "votes": kw.get("votes", 1000),
            "pct": kw.get("pct", 10.0),
            "place": kw.get("place", 3),
            "field_size": kw.get("field_size", 5),
            "certified": kw.get("certified", True),
            "as_of": kw.get("as_of", "2026-08-19"),
        }
    return c


def _race(candidates):
    return {"id": "wa-test-race-2026", "title": "Test Race",
            "url": "/races/wa-test-race-2026/", "candidates": candidates}


class TestNothingBeforeTheElection:
    def test_no_results_means_no_block_at_all(self):
        """Before the primary nobody has a result. The hub must look exactly
        as it does today, not gain an empty section."""
        race = _race([_cand("Ann Advancer", "advancer"),
                      _cand("Bob Byrne", "byrne")])
        assert build_primary_results_block(race) == ""


class TestEliminatedAreGroupedAndMarked:
    def _block(self):
        return build_primary_results_block(_race([
            _cand("Ann Advancer", "advancer", "advanced", place=1, pct=41.2, votes=8200),
            _cand("Bob Byrne", "byrne", "advanced", place=2, pct=28.8, votes=5730),
            _cand("Cal Cutt", "cutt", "eliminated", place=3, pct=18.1, votes=3600),
            _cand("Dee Drop", "drop", "eliminated", place=4, pct=11.9, votes=2370),
        ]))

    def test_eliminated_candidates_appear(self):
        block = self._block()
        assert "Cal Cutt" in block and "Dee Drop" in block

    def test_eliminated_sit_under_their_own_header(self):
        assert "Eliminated" in self._block()

    def test_eliminated_are_visually_de_emphasised(self):
        assert "dossier-link eliminated" in self._block()

    def test_status_is_not_conveyed_by_colour_alone(self):
        """House accessibility rule. A grey card must also say the word."""
        assert "ELIMINATED" in self._block()

    def test_the_numbers_are_shown_not_just_the_status(self):
        """'Eliminated, 4th of 5, 11.9%' distinguishes a fringe candidacy from
        a near miss. A bare flag discards that."""
        block = self._block()
        assert "11.9%" in block
        assert "2,370" in block or "2370" in block
        assert "4" in block and "5" in block

    def test_advancing_candidates_are_not_in_the_eliminated_group(self):
        block = self._block()
        elim_at = block.index("Eliminated")
        assert "Ann Advancer" not in block[elim_at:]
        assert "Bob Byrne" not in block[elim_at:]

    def test_advancing_candidates_and_their_share_are_shown(self):
        """Advancing is equally a result, and the share of the two people on
        the November ballot is the more useful half."""
        block = self._block()
        assert "Ann Advancer" in block and "41.2%" in block


class TestAbsenceIsNeverElimination:
    def test_a_candidate_with_no_result_is_not_marked_eliminated(self):
        """The uncontested case: races with no primary skip it entirely, so
        those candidates have no result and are not eliminated (#1915)."""
        block = build_primary_results_block(_race([
            _cand("Ann Advancer", "advancer", "advanced"),
            _cand("Uma Uncontested", "uncontested"),          # no primary_result
            _cand("Cal Cutt", "cutt", "eliminated"),
        ]))
        if "Uma Uncontested" in block:
            elim_at = block.index("Eliminated")
            assert "Uma Uncontested" not in block[elim_at:]

    def test_withdrawn_is_not_elimination(self):
        """Withdrawing is a choice made before ballots; elimination is an
        outcome after them. Different facts about a person."""
        race = _race([_cand("Ann Advancer", "advancer", "advanced")])
        race["candidates"].append(
            {"name": "Wanda Withdrew", "party": "R",
             "url": "/races/wa-test-race-2026/withdrew/", "withdrawn": True})
        block = build_primary_results_block(race)
        if "Wanda Withdrew" in block and "Eliminated" in block:
            assert "Wanda Withdrew" not in block[block.index("Eliminated"):]


class TestPartialCountsAreLabelled:
    def _block(self, certified):
        return build_primary_results_block(_race([
            _cand("Ann Advancer", "advancer", "advanced", certified=certified,
                  as_of="2026-08-05"),
            _cand("Cal Cutt", "cutt", "eliminated", certified=certified,
                  as_of="2026-08-05"),
        ]))

    def test_uncertified_results_say_so_and_carry_a_date(self):
        block = self._block(False)
        assert "artial" in block           # "Partial" / "partial"
        assert "2026-08-05" in block

    def test_uncertified_results_avoid_asserting_elimination_as_final(self):
        """A candidate trailing on election night can still advance."""
        assert "not certified" in self._block(False).lower()

    def test_certified_results_carry_no_partial_warning(self):
        assert "artial" not in self._block(True)


class TestInjectionIntoAnyHub:
    """Curated hubs are hand-authored and frozen; 64 of 612 races. The block
    is injected mechanically so all 612 behave identically and the
    hand-written narrative above it is left alone."""

    HUB = (
        '<html><body>\n<div class="page">\n'
        '  <div class="section">\n    <h2>Hand-authored analysis</h2>\n'
        '    <p>Careful prose nobody should regenerate.</p>\n  </div>\n\n'
        '  <div class="footer">\n    <em>footer</em>\n  </div>\n'
        '</div>\n</body></html>\n'
    )

    def _block(self):
        return build_primary_results_block(_race([
            _cand("Ann Advancer", "advancer", "advanced"),
            _cand("Cal Cutt", "cutt", "eliminated"),
        ]))

    def test_block_is_inserted_before_the_footer(self):
        out = inject_primary_results(self.HUB, self._block())
        assert out.index(BLOCK_START) < out.index('<div class="footer">')

    def test_hand_authored_content_survives(self):
        out = inject_primary_results(self.HUB, self._block())
        assert "Careful prose nobody should regenerate." in out
        assert "Hand-authored analysis" in out

    def test_injection_is_idempotent(self):
        once = inject_primary_results(self.HUB, self._block())
        twice = inject_primary_results(once, self._block())
        assert once == twice
        assert twice.count(BLOCK_START) == 1

    def test_reinjection_replaces_stale_results(self):
        stale = inject_primary_results(self.HUB, self._block())
        fresh = build_primary_results_block(_race([
            _cand("Ann Advancer", "advancer", "advanced", pct=99.9)]))
        out = inject_primary_results(stale, fresh)
        assert "99.9%" in out
        assert out.count(BLOCK_START) == 1

    def test_empty_block_removes_a_previous_one(self):
        """If results are retracted the section goes away cleanly rather than
        leaving an orphan header."""
        with_block = inject_primary_results(self.HUB, self._block())
        out = inject_primary_results(with_block, "")
        assert BLOCK_START not in out and BLOCK_END not in out
        assert "Careful prose nobody should regenerate." in out

    def test_a_hub_without_a_footer_is_left_untouched(self):
        """Better to skip a page than to guess where the block belongs."""
        odd = "<html><body><p>no footer here</p></body></html>"
        assert inject_primary_results(odd, self._block()) == odd


class TestPartyMatchesTheRestOfTheHub:
    """The existing cards say "(Democratic)". A block saying "(D)" beside them
    looks like a different page fragment, which is what it was."""

    def test_party_code_is_expanded(self):
        block = build_primary_results_block(_race([
            _cand("Ann Advancer", "advancer", "advanced")]))
        assert "(Democratic)" in block
        assert "(D)" not in block

    def test_unknown_party_is_passed_through_not_dropped(self):
        race = _race([_cand("Ann Advancer", "advancer", "advanced")])
        race["candidates"][0]["party"] = "Cascade"
        assert "(Cascade)" in build_primary_results_block(race)
