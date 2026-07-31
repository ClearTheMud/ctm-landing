#!/usr/bin/env python3
"""A curated race page must show the same field as the registry (ADO #1992).

Curated race overviews are hand-maintained: the generator skips them so a
deep-dive page is never overwritten with a stub. That protection has a cost.
Nothing regenerates them, so nothing notices when the hand-edited roster stops
matching tools/data/races.json.

On 2026-07-30, four days before the primary, two curated pages were listing
candidates who had WITHDRAWN from their races:

  wa-house-5-2026   Mike Gahvarehchee (D)   also linked to a page that 404'd
  wa-house-2-2026   Raymond Pelletti (R)

Both appeared as active CHALLENGERs. Neither was in races.json. A voter
comparing the field saw someone who was not on the ballot.

Two things made this hard to see. The filing-week CandidateList.csv still
showed both as "Active / In Primary", because it is a snapshot from the day
they filed and withdrawal happens later. And the pages looked entirely normal:
a withdrawn candidate renders exactly like a live one.

races.json is the registry the rest of the site is generated from, so treating
it as the source of truth for the roster is what makes the drift visible. This
does not check that races.json itself is correct; that needs a human against
Ballotpedia or the county's certified list.
"""

import html
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA = REPO_ROOT / "tools" / "data"


def _registry():
    with open(DATA / "races.json") as f:
        return {r["id"]: r for r in json.load(f)["races"] if isinstance(r, dict) and "id" in r}


def _curated_ids():
    with open(DATA / "curated_races.json") as f:
        return set(json.load(f)["curated_race_ids"])


def _norm(name):
    """Compare people, not markup.

    The page is HTML-escaped and the registry is not, so a candidate with an
    apostrophe (Tamra 'Tam' Ingwaldson) differs only by &#x27; and would read
    as drift.
    """
    return " ".join(html.unescape(name or "").split()).casefold()


def _page_roster(path):
    h = path.read_text(errors="ignore")
    return {_norm(n) for n in re.findall(r"<h4>([^<(]+)\(", h)}


def _pairs():
    reg = _registry()
    for rid in sorted(_curated_ids()):
        idx = REPO_ROOT / "races" / rid / "index.html"
        if not idx.exists() or rid not in reg:
            continue
        page = _page_roster(idx)
        if not page:
            continue  # overview without candidate cards
        yield rid, page, {_norm(c.get("name")) for c in reg[rid].get("candidates", [])}


class TestCuratedRostersMatchRegistry:
    def test_no_candidate_on_a_page_is_missing_from_the_registry(self):
        """The withdrawn-candidate case. This is the one that misinforms voters."""
        bad = []
        for rid, page, reg in _pairs():
            extra = page - reg
            if extra:
                bad.append(f"{rid}: page shows {sorted(extra)}, registry does not")
        assert not bad, (
            "Curated pages list candidates the registry does not. A withdrawn "
            "candidate looks exactly like a live one, so check each against "
            "Ballotpedia or the certified list before deciding:\n  "
            + "\n  ".join(bad))

    def test_no_registered_candidate_is_missing_from_its_page(self):
        """The opposite drift: a real candidate the page never got."""
        bad = []
        for rid, page, reg in _pairs():
            missing = reg - page
            if missing:
                bad.append(f"{rid}: registry has {sorted(missing)}, page does not")
        assert not bad, "Curated pages omit registered candidates:\n  " + "\n  ".join(bad)

    def test_displayed_count_matches_the_cards(self):
        """A stale count is the tell that someone edited cards by hand."""
        bad = []
        for rid, page, _ in _pairs():
            h = (REPO_ROOT / "races" / rid / "index.html").read_text(errors="ignore")
            m = re.search(r"<strong>Candidates:</strong>\s*(\d+)", h)
            if not m:
                continue
            # Match the class as a prefix. A withdrawn card carries
            # class="dossier-link withdrawn", so an exact-string count silently
            # undercounts and reports drift that is not there.
            shown = int(m.group(1))
            actual = len(re.findall(r'class="dossier-link(?:\s[^"]*)?"', h))
            if shown != actual:
                bad.append(f"{rid}: header says {shown}, page has {actual} cards")
        assert not bad, "Candidate counts disagree with the cards:\n  " + "\n  ".join(bad)


class TestTheGuardCanActuallyFail:
    def test_curated_pages_are_actually_being_compared(self):
        pairs = list(_pairs())
        assert len(pairs) > 20, f"only {len(pairs)} curated pages compared; globs are wrong"

    def test_apostrophes_do_not_read_as_drift(self):
        assert _norm("Tamra &#x27;Tam&#x27; Ingwaldson") == _norm("Tamra 'Tam' Ingwaldson")

    def test_a_planted_extra_name_is_detected(self):
        page = {_norm("Real Candidate"), _norm("Withdrawn Person")}
        reg = {_norm("Real Candidate")}
        assert page - reg == {_norm("Withdrawn Person")}
