"""Primary results block for race hubs (ADO #2020).

Decisions taken 2026-07-31, before the 2026-08-04 primary:

  - show the FULL primary field, not just the candidates who advanced
  - eliminated candidates go under their own header, visually de-emphasised,
    never deleted: a reader who remembers a name must learn what happened
  - publish partial counts between election night and certification, labelled
  - eliminated is NEVER inferred from absence

The block is injected between sentinel comments rather than rendered by the
hub generators. 64 of 612 race hubs are curated and hand-authored, and
hand-editing 64 pages is how roster drift happened in #1992. Injection keeps
all 612 behaving identically while leaving hand-written narrative alone.
"""
from __future__ import annotations

import html as _html

# Reuse the hub's own party map so the block reads "(Democratic)" like the
# cards beside it, rather than "(D)" (ADO #2020).
try:
    from generate_candidate_pages import PARTY_FULL
except ImportError:                                   # pragma: no cover
    PARTY_FULL = {}

BLOCK_START = "<!-- primary-results:start -->"
BLOCK_END = "<!-- primary-results:end -->"

#: Injected immediately before this anchor, which both mechanical and curated
#: hubs carry. A hub without it is skipped rather than guessed at.
_ANCHOR = '<div class="footer">'


def _result(candidate: dict) -> dict | None:
    r = candidate.get("primary_result")
    return r if isinstance(r, dict) and r.get("outcome") else None


def _placing(r: dict) -> str:
    """"3rd of 5, 18.1%, 3,600 votes", omitting whatever is missing."""
    bits = []
    place, field = r.get("place"), r.get("field_size")
    if place and field:
        bits.append(f"{_ordinal(place)} of {field}")
    elif place:
        bits.append(_ordinal(place))
    if r.get("pct") is not None:
        bits.append(f"{r['pct']}%")
    if r.get("votes") is not None:
        bits.append(f"{r['votes']:,} votes")
    return ", ".join(bits)


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def _card(candidate: dict, r: dict, eliminated: bool) -> str:
    name = _html.escape(str(candidate.get("name", "")))
    raw_party = str(candidate.get("party", ""))
    party = _html.escape(PARTY_FULL.get(raw_party, raw_party))
    url = _html.escape(str(candidate.get("url", "")))
    cls = "dossier-link eliminated" if eliminated else "dossier-link"
    badge = "status-eliminated" if eliminated else "status-advanced"
    # Text label as well as the grey treatment: status is never carried by
    # colour alone (house accessibility rule).
    label = "ELIMINATED" if eliminated else "ADVANCED"
    detail = _placing(r)
    return (f'      <a href="{url}" class="{cls}">\n'
            f'        <h4>{name} ({party})</h4>\n'
            f'        <p><span class="{badge}">{label}</span>, {detail}</p>\n'
            f'      </a>')


def build_primary_results_block(race: dict) -> str:
    """Return the block for a race, or "" when nothing has a result yet.

    Before the primary no candidate has one, and the hub must look exactly as
    it does today rather than gain an empty section.
    """
    candidates = race.get("candidates", [])
    scored = [(c, _result(c)) for c in candidates]
    scored = [(c, r) for c, r in scored if r]
    if not scored:
        return ""

    scored.sort(key=lambda cr: (cr[1].get("place") or 999))
    advanced = [(c, r) for c, r in scored if r["outcome"] != "eliminated"]
    eliminated = [(c, r) for c, r in scored if r["outcome"] == "eliminated"]

    # Washington counts mail ballots for weeks, and a candidate trailing on
    # election night can advance. Until every result is certified the whole
    # block is provisional and says so.
    uncertified = [r for _, r in scored if not r.get("certified")]
    notice = ""
    if uncertified:
        as_of = next((r.get("as_of") for r in uncertified if r.get("as_of")), "")
        dated = f" as of {_html.escape(str(as_of))}" if as_of else ""
        notice = (
            '    <p class="partial-count" role="note"><strong>Partial count'
            f'{dated}.</strong> These results are not certified. Washington '
            "counts mail ballots for days after election night and standings "
            "can change.</p>\n"
        )

    parts = [BLOCK_START]
    parts.append('  <div class="section primary-results">')
    parts.append("    <h2>Primary Results</h2>")
    if notice:
        parts.append(notice.rstrip("\n"))

    if advanced:
        parts.append('    <div class="dossier-links">')
        parts.extend(_card(c, r, False) for c, r in advanced)
        parts.append("    </div>")

    if eliminated:
        parts.append('    <h3 class="eliminated-header">Eliminated in the primary</h3>')
        parts.append(
            '    <p class="eliminated-note">These candidates are not on the '
            "general election ballot. Their pages remain available.</p>"
        )
        parts.append('    <div class="dossier-links">')
        parts.extend(_card(c, r, True) for c, r in eliminated)
        parts.append("    </div>")

    parts.append("  </div>")
    parts.append(BLOCK_END)
    return "\n".join(parts) + "\n"


def inject_primary_results(hub_html: str, block: str) -> str:
    """Insert, replace, or remove the block in a hub page. Idempotent.

    An empty block removes any previous one, so retracted results leave no
    orphan header. A hub with no anchor is returned untouched: skipping a
    page is better than guessing where the block belongs.
    """
    start = hub_html.find(BLOCK_START)
    end = hub_html.find(BLOCK_END)
    if start != -1 and end != -1:
        tail = hub_html[end + len(BLOCK_END):].lstrip("\n")
        head = hub_html[:start]
        return head + block + tail if block else head + tail

    if not block:
        return hub_html

    anchor = hub_html.find(_ANCHOR)
    if anchor == -1:
        return hub_html
    line_start = hub_html.rfind("\n", 0, anchor) + 1
    return hub_html[:line_start] + block + hub_html[line_start:]
