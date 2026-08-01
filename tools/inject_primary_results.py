#!/usr/bin/env python3
"""Apply the primary-results block to every race hub (ADO #2020).

Runs as a separate pass AFTER any hub generation, so it does not matter which
generator wrote the page. That is deliberate: 64 of 612 race hubs are curated
and hand-authored, and hand-editing 64 pages is how roster drift happened in
#1992. One owner, one pass, all 612 treated identically.

Idempotent. Safe to run before the primary, when it writes nothing at all
because no candidate has a result yet.

Usage:
    python3 tools/inject_primary_results.py            # apply
    python3 tools/inject_primary_results.py --dry-run  # report, change nothing
    python3 tools/inject_primary_results.py --json     # machine-readable
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from primary_results import build_primary_results_block, inject_primary_results  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
RACES_JSON = REPO_ROOT / "tools" / "data" / "races.json"
RACES_DIR = REPO_ROOT / "races"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Inject primary results into race hub pages.",
        epilog="Examples:\n"
               "  python3 tools/inject_primary_results.py\n"
               "  python3 tools/inject_primary_results.py --dry-run\n"
               "  python3 tools/inject_primary_results.py --json\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--dry-run", action="store_true", help="Report only; write nothing")
    ap.add_argument("--json", action="store_true", help="Machine-readable output")
    args = ap.parse_args()

    races = json.loads(RACES_JSON.read_text()).get("races", [])
    changed, skipped_no_anchor, with_results = [], [], 0

    for race in races:
        block = build_primary_results_block(race)
        if block:
            with_results += 1
        hub = RACES_DIR / race["id"] / "index.html"
        if not hub.is_file():
            continue
        before = hub.read_text()
        after = inject_primary_results(before, block)
        if after == before:
            # A page that should have gained a block but did not means the
            # anchor is missing. Report it rather than failing silently.
            if block and "primary-results:start" not in before:
                skipped_no_anchor.append(race["id"])
            continue
        changed.append(race["id"])
        if not args.dry_run:
            hub.write_text(after)

    if args.json:
        print(json.dumps({
            "races": len(races), "with_results": with_results,
            "changed": len(changed), "skipped_no_anchor": skipped_no_anchor,
            "dry_run": args.dry_run,
        }))
    else:
        verb = "would change" if args.dry_run else "changed"
        print(f"[OK] {len(races)} races, {with_results} with primary results, "
              f"{verb} {len(changed)} hub(s)")
        if skipped_no_anchor:
            print(f"[WARN] {len(skipped_no_anchor)} hub(s) have results but no "
                  f"injection anchor and were skipped:")
            for rid in skipped_no_anchor[:10]:
                print(f"         {rid}")

    # A hub that needs a block and cannot take one is a real problem: that
    # race would silently show a stale field after the primary.
    return 1 if skipped_no_anchor else 0


if __name__ == "__main__":
    raise SystemExit(main())
