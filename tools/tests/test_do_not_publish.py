#!/usr/bin/env python3
"""Pages on the do-not-publish list must not be tracked (ADO #1971, #1974).

This repo is public only so GitHub Pages can serve clearthemud.org. Anything
tracked here is published, and untracked pages under races/ exist precisely
because someone decided not to publish them.

`git add races/` cannot tell the difference. On 2026-07-28 it swept in two
phantom candidates from a stub roster scrape and one orphan page, and that
commit was pushed live before the mistake was caught. Staging the same
directory again later that day repeated it; that time a review of newly-added
paths caught it before the commit.

Noticing is not a control. This test is.
"""

import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA = REPO_ROOT / "tools" / "data" / "do-not-publish.json"


def _entries():
    with open(DATA) as f:
        return json.load(f)["paths"]


def _tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "races/"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    return set(out.stdout.splitlines())


class TestTheListItself:
    def test_list_loads(self):
        assert _entries()

    def test_every_entry_explains_why(self):
        """An unexplained entry becomes cargo cult and gets deleted later."""
        for e in _entries():
            assert e.get("reason") and len(e["reason"]) > 20, e.get("path")

    def test_paths_are_race_scoped(self):
        for e in _entries():
            assert e["path"].startswith("races/"), e["path"]


class TestNothingForbiddenIsTracked:
    def test_no_forbidden_page_is_tracked(self):
        tracked = _tracked_files()
        published = []
        for e in _entries():
            prefix = e["path"].rstrip("/") + "/"
            hits = [f for f in tracked if f.startswith(prefix)]
            if hits:
                published.append(f"{e['path']}: {e['reason']}")
        assert not published, (
            "These pages are on the do-not-publish list but are tracked, "
            "which means they are live:\n  " + "\n  ".join(published))

    def test_the_guard_can_actually_fail(self):
        """A guard that cannot fail is not a guard.

        Confirms the tracked-file lookup returns real data, so an empty result
        never silently passes this suite.
        """
        assert _tracked_files(), "git ls-files races/ returned nothing"
