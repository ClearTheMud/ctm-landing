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
import re
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
        assert is_publishable("tools/primary_results.py", config)
        assert not is_publishable("tools/reports/wa-candidate-validation-report.md", config)

    def test_migrated_generators_are_refused_by_the_real_list(self):
        """Site generation code moved to the build repo and must not return.

        The generators lived here until 2026-08-01 (ADO #1975). A copy landing
        back in this repo is invisible to the build repo's tests, and the two
        drift silently: a fix lands in one and the other overwrites it on the
        next run. The allowlist is where that gets refused.
        """
        config = _config()
        for path in (
            "tools/generate_states.py",
            "tools/generate_candidate_pages.py",
            "tools/generate_county_maps.py",
            "tools/build_county_hub.py",
            "tools/build_county_races.py",
            "tools/detect_roles.py",
            "tools/ingest_sos_candidates.py",
            "tools/update_races.py",
            "tools/validate_candidates.py",
        ):
            assert not is_publishable(path, config), (
                f"{path} is publishable again. Site generators belong in the "
                f"build repo's site_tools/, not here.")

    def test_migrated_tests_are_refused_by_the_real_list(self):
        """The 14 tests that moved with the generators must not return either.

        `tools/tests/` is allowed as a whole directory prefix, so denying the
        nine generators protected the code and left every one of their tests
        free to reappear. A returning test is the same drift problem in a
        quieter form: two copies of an assertion, one of which the build
        repo's suite never runs, so a fix in one is silently contradicted by
        the other.
        """
        config = _config()
        for name in (
            "test_county_race_table.py",
            "test_curated_skip.py",
            "test_deep_dive_preservation.py",
            "test_detect_roles.py",
            "test_ingest_candidates.py",
            "test_judicial_hub.py",
            "test_legislative_pages.py",
            "test_name_parser.py",
            "test_senate_map.py",
            "test_state_maps.py",
            "test_stub_election_history.py",
            "test_supreme_court_nav.py",
            "test_validator_normalization.py",
            "test_withdrawn_candidate_page.py",
        ):
            path = "tools/tests/" + name
            assert not is_publishable(path, config), (
                f"{path} is publishable again. It moved to the build repo's "
                f"tests/site_tools/ with the generator it covers.")

    def test_every_deny_entry_refuses_the_path_it_names(self):
        """A deny entry that matches nothing is decoration, not a control.

        The matcher is exact-path or directory-prefix. A partial name prefix
        such as `tools/generate_` matches no real path and is silently
        ignored, so an entry can look like protection while providing none.
        """
        config = _config()
        for entry in config["deny"]:
            path = entry["path"]
            probe = path.rstrip("/") + "/probe.txt" if path.endswith("/") else path
            assert not is_publishable(probe, config), (
                f"deny entry {path!r} does not refuse {probe!r}. The matcher "
                f"is exact-path or directory prefix; a partial name prefix "
                f"never matches and is silently ignored.")

    def test_the_two_retained_tools_are_still_allowed(self):
        """The election-night path must not be broken by the migration.

        primary_results.py and inject_primary_results.py stay here until the
        2026-08-04 primary is certified. Denying them would block the commit
        that publishes results on election night.
        """
        config = _config()
        assert is_publishable("tools/primary_results.py", config)
        assert is_publishable("tools/inject_primary_results.py", config)
        assert is_publishable("tools/data/races.json", config)
        assert is_publishable("tools/tests/test_primary_results.py", config)

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


class TestTheHookInspectsMoreThanAdditions:
    """Regression guard for the diff-filter widening (2026-08-01).

    The hook read `--diff-filter=A`, so it saw only additions. Three bypasses
    followed, each confirmed by running real commits in a scratch clone:

      * a file already tracked at a denied path could be modified forever
      * a page on the do-not-publish list could be edited once it was tracked
      * `git mv tools/primary_results.py tools/generate_states.py` committed
        clean, because git reports a rename as R and never as A

    The filter is now ACMRT. D stays out on purpose: deleting a file here
    unpublishes it, which is not the mistake this hook exists to catch.
    """

    HOOK = REPO_ROOT / ".githooks" / "pre-commit"

    def _filter(self):
        match = re.search(r"--diff-filter=([A-Z]+)", self.HOOK.read_text())
        assert match, "the hook no longer passes --diff-filter at all"
        return set(match.group(1))

    def test_modifications_and_renames_are_inspected(self):
        letters = self._filter()
        for needed in "ACMRT":
            assert needed in letters, (
                f"--diff-filter is missing {needed!r}. With only additions "
                f"inspected, a rename or a modification walks past both the "
                f"deny list and the do-not-publish list.")

    def test_deletions_are_still_not_gated(self):
        assert "D" not in self._filter(), (
            "gating deletions blocks the commits that remove a denied path, "
            "and removing a file from this repo unpublishes it rather than "
            "publishing anything.")


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
