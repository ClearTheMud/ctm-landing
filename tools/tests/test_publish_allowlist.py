#!/usr/bin/env python3
"""Only static site content may be tracked in this repo (ADO #1980, #1981).

This repo is public solely so GitHub Pages can serve clearthemud.org. Tracking
a file here publishes it. The canonical copy of everything else lives in the
private clearthemud ADO repo.

The existing do-not-publish guard covers `races/` only, so it had nothing to
say when internal process files landed at the top level: eight session status
docs under `docs/status/` and the internal candidate-validation report under
`tools/reports/`. Neither is site content. Both were published.

A per-page denylist cannot catch that class of mistake, because it only knows
about pages someone already thought to name. This test inverts the question:
every tracked path must match something on the allowlist, so a new kind of
file has to be declared before it can be published.
"""

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG = REPO_ROOT / "tools" / "data" / "publish-allowlist.json"


def _config():
    with open(CONFIG) as f:
        return json.load(f)


def _tracked_files():
    """Every tracked path, raw.

    `-z` is load-bearing. Without it git C-quotes any path containing a
    non-ASCII byte, so `races/.../saldaña/index.html` comes back as the
    literal string `"races/.../salda\\303\\261a/index.html"`, quotes and all.
    That path then matches no allowlist prefix and reads as a violation, and
    worse, the same quoting in the pre-commit hook meant a non-ASCII page
    could never match a denylist prefix either. Two real candidates are
    affected today: Saldaña and Barón.
    """
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT, capture_output=True, check=True)
    return [p for p in out.stdout.decode("utf-8").split("\0") if p]


def is_publishable(path, config):
    """True if `path` may be tracked. Deny wins over allow."""
    for entry in config["deny"]:
        prefix = entry["path"]
        if path == prefix or path.startswith(prefix.rstrip("/") + "/"):
            return False
    for entry in config["allow"]:
        prefix = entry["path"]
        if prefix.endswith("/"):
            if path.startswith(prefix):
                return True
        elif path == prefix:
            return True
    return False


class TestTheConfigItself:
    def test_config_loads(self):
        config = _config()
        assert config["allow"]
        assert config["deny"]

    def test_every_entry_explains_why(self):
        """An unexplained entry becomes cargo cult and gets deleted later."""
        for key in ("allow", "deny"):
            for entry in _config()[key]:
                assert entry.get("reason") and len(entry["reason"]) > 20, (
                    f"{key} entry {entry.get('path')!r} needs a reason")

    def test_no_entry_uses_a_leading_slash(self):
        """Paths are repo-relative, matching `git ls-files` output."""
        for key in ("allow", "deny"):
            for entry in _config()[key]:
                assert not entry["path"].startswith("/"), entry["path"]


class TestMatching:
    def test_directory_prefix_allows_nested_files(self):
        config = {"allow": [{"path": "races/"}], "deny": []}
        assert is_publishable("races/wa-thurston-sheriff-2026/sanders/index.html", config)

    def test_directory_prefix_does_not_allow_a_sibling(self):
        config = {"allow": [{"path": "races/"}], "deny": []}
        assert not is_publishable("racesignore/x.html", config)

    def test_exact_file_entry_matches_only_itself(self):
        config = {"allow": [{"path": "index.html"}], "deny": []}
        assert is_publishable("index.html", config)
        assert not is_publishable("index.html.bak", config)

    def test_deny_beats_allow(self):
        config = {
            "allow": [{"path": "tools/"}],
            "deny": [{"path": "tools/reports/"}],
        }
        assert is_publishable("tools/build_county_hub.py", config)
        assert not is_publishable("tools/reports/wa-candidate-validation-report.md", config)

    def test_non_ascii_path_matches_its_prefix(self):
        """Real candidates have non-ASCII names; matching must not depend on git quoting."""
        config = {"allow": [{"path": "races/"}], "deny": []}
        assert is_publishable(
            "races/wa-king-county-council-dist-2-2026/saldaña/index.html", config)

    def test_tracked_paths_are_not_git_quoted(self):
        """Regression: C-quoted paths defeat every prefix match in this repo."""
        for path in _tracked_files():
            assert not path.startswith('"'), (
                f"{path} came back C-quoted; git output is not being read raw")

    def test_unlisted_path_is_refused_by_default(self):
        config = {"allow": [{"path": "races/"}], "deny": []}
        assert not is_publishable("docs/status/2026-05-09-county-incumbents.md", config)


class TestNothingUnpublishableIsTracked:
    def test_every_tracked_file_is_publishable(self):
        config = _config()
        violations = [f for f in _tracked_files() if not is_publishable(f, config)]
        assert not violations, (
            "These tracked files are not static site content, which means "
            "they are published to clearthemud.org:\n  "
            + "\n  ".join(sorted(violations))
            + "\n\nEither move them to the private clearthemud ADO repo, or "
              "add them to tools/data/publish-allowlist.json with a reason.")

    def test_the_guard_can_actually_fail(self):
        """A guard that cannot fail is not a guard."""
        assert _tracked_files(), "git ls-files returned nothing"
        config = _config()
        assert not is_publishable("docs/status/some-session-note.md", config), (
            "the allowlist would permit an internal status doc")
