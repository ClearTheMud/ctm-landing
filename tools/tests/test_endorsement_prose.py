#!/usr/bin/env python3
"""Published race prose must not claim a collective endorsement (ADO #1971).

The sentence that triggered this shipped in a hand-curated race page, not in
generated output: "endorsed by ... all three Thurston County commissioners".
Thurston's board has five members and exactly three endorsed, so the clause was
wrong about the board and implied a unanimity that never happened.

A check on the source YAML would not have caught it, because curated pages are
edited directly. This scans the published HTML itself, which is the only layer
every page passes through regardless of how it was produced.

The rule is to name people. A reader cannot verify "all commissioners"; they
can verify "Carolina Mejia, Tye Menser, and Wayne Fournier". Naming also gives
voters the facts to judge an endorsement for themselves, which is the whole
point of publishing endorsements at all.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RACES_DIR = REPO_ROOT / "races"

_QUANTIFIER = r"all|every|both|each"
_NUMBER = r"one|two|three|four|five|six|seven|eight|nine|ten|\d+"
_GROUP = (r"commissioners?|councilmembers?|council members?|mayors?|"
          r"senators?|representatives?|judges?|justices?|legislators?")

COLLECTIVE_RE = re.compile(
    rf"\b({_QUANTIFIER})\s+(?:({_NUMBER})\s+)?"
    rf"((?:[A-Z][\w.'-]*\s+){{0,3}})?({_GROUP})\b",
    re.I,
)

# An appointment process that interviewed all five applicants is not an
# endorsement claim; a time interval is not a body of officeholders.
EXCLUDE_CONTEXT = re.compile(
    r"applicant|interview|nominee|"
    r"(all|every|both|each)\s+\w+\s+(years?|months?|cycles?|terms?)", re.I)

TAG_RE = re.compile(r"<[^>]+>")

# A candidate's voters' pamphlet statement is quoted verbatim under ADO #1915
# and is the candidate's words, not ours. Colleen Melody's statement says she
# is "endorsed by every sitting Supreme Court Justice"; our own data records
# six. That discrepancy is hers to own and ours to attribute, never to edit.
# Rewriting a submitted statement would be a transparency failure by a
# transparency tool, so quoted blocks are excluded from this house-style gate.
PAMPHLET_RE = re.compile(
    r'<blockquote class="pamphlet-statement">.*?</blockquote>',
    re.S | re.I,
)


def _visible_text(html):
    """Tags stripped and whitespace collapsed.

    Collapsing matters: published HTML wraps mid-sentence, so "Carolina\\n
    Mejia" is one name to a reader and two tokens to a naive search.
    """
    html = PAMPHLET_RE.sub(" ", html)
    return " ".join(TAG_RE.sub(" ", html).split())


def _endorsement_pages():
    """Pages whose visible text discusses endorsements."""
    for page in sorted(RACES_DIR.rglob("index.html")):
        html = page.read_text(encoding="utf-8", errors="replace")
        if "ndorse" in html:
            yield page, _visible_text(html)


class TestNoCollectiveEndorsementClaims:
    def test_corpus_is_not_empty(self):
        """Guard the guard: a broken glob would silently pass everything."""
        assert list(_endorsement_pages()), "no endorsement pages found"

    def test_no_published_page_claims_a_collective_endorsement(self):
        offenders = []
        for page, text in _endorsement_pages():
            for m in COLLECTIVE_RE.finditer(text):
                window = text[max(0, m.start() - 80):m.end() + 80]
                if EXCLUDE_CONTEXT.search(window):
                    continue
                if "ndorse" not in window:
                    continue          # the phrase is not about endorsements
                offenders.append(
                    f"{page.relative_to(RACES_DIR)}: {m.group(0)!r}")
        assert not offenders, "\n".join(offenders[:20])

    def test_the_thurston_page_names_the_three_commissioners(self):
        page = RACES_DIR / "wa-thurston-sheriff-2026" / "index.html"
        text = _visible_text(page.read_text(encoding="utf-8"))
        assert "all three Thurston County commissioners" not in text
        assert "three of the five Thurston County commissioners" in text
        for name in ("Carolina Mejia", "Tye Menser", "Wayne Fournier"):
            assert name in text, f"{name} should be named"


class TestDetectorBehaviour:
    @pytest.mark.parametrize("text", [
        "endorsed by all three Thurston County commissioners",
        "every county commissioner endorsed her",
        "both state senators endorsed him",
    ])
    def test_collective_phrases_match(self, text):
        assert COLLECTIVE_RE.search(text)

    @pytest.mark.parametrize("text", [
        "three of the five Thurston County commissioners (Carolina Mejia)",
        "Lt. Gov. Denny Heck and U.S. Rep. Marie Gluesenkamp Perez",
    ])
    def test_named_prose_does_not_match(self, text):
        assert not COLLECTIVE_RE.search(text)


class TestQuotedCandidateSpeechIsExempt:
    """House style governs our prose, never a candidate's quoted words."""

    def test_pamphlet_block_is_stripped_before_checking(self):
        html = (
            '<p>our prose</p>'
            '<blockquote class="pamphlet-statement">'
            '<p>endorsed by every sitting Supreme Court Justice</p>'
            '</blockquote>'
        )
        assert "every sitting" not in _visible_text(html)
        assert "our prose" in _visible_text(html)

    def test_melody_statement_is_left_verbatim(self):
        """A real page whose quoted statement makes a collective claim."""
        page = RACES_DIR / "wa-supreme-court-justice-pos-1-2026" / "melody" / "index.html"
        raw = page.read_text(encoding="utf-8")
        assert "every sitting Supreme Court Justice" in raw, (
            "the candidate's submitted statement must not be edited")
        assert not COLLECTIVE_RE.search(_visible_text(raw)), (
            "but it must not be counted against our house style")
