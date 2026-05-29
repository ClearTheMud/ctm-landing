#!/usr/bin/env python3
"""Tests for curated deep-dive preservation in generate_candidate_pages.py.

The bulk generator regenerates every WA race in races.json from clearthemud
dossier JSON. Hand-authored OSINT deep-dives (Grays Harbor, Lewis, Thurston,
LD-02; ME/GA/MI senate; ID-sd1) must NOT be overwritten with T1 stubs. The
generator reads tools/data/curated_races.json and skips those race-ids.

Written before the skip logic was added (TDD).
"""

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "tools" / "data"
GEN_PATH = REPO_ROOT / "tools" / "generate_candidate_pages.py"


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen", GEN_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Config file: tools/data/curated_races.json
# ---------------------------------------------------------------------------
class TestCuratedConfig:
    @pytest.fixture
    def config(self):
        with open(DATA_DIR / "curated_races.json") as f:
            return json.load(f)

    def test_config_is_valid_json_with_list(self, config):
        assert isinstance(config["curated_race_ids"], list)
        assert len(config["curated_race_ids"]) > 0

    def test_includes_known_wa_deep_dives(self, config):
        ids = set(config["curated_race_ids"])
        for rid in ("wa-lewis-sheriff-2026", "wa-thurston-assessor-2026",
                    "wa-grays-harbor-coroner-2026", "wa-ld-02-position-1-2026"):
            assert rid in ids

    def test_includes_non_wa_deep_dives(self, config):
        ids = set(config["curated_race_ids"])
        for rid in ("me-senate-2026", "ga-senate-2026",
                    "mi-senate-2026", "id-sd1-2026"):
            assert rid in ids

    def test_does_not_protect_bulk_races(self, config):
        """New bulk races sharing a county prefix must NOT be protected."""
        ids = set(config["curated_race_ids"])
        assert "wa-thurston-district-court-pos-1-2026" not in ids
        assert "wa-adams-assessor-2026" not in ids

    def test_no_duplicate_ids(self, config):
        ids = config["curated_race_ids"]
        assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
class TestLoadCuratedRaceIds:
    def test_load_returns_set(self):
        gen = _load_gen()
        ids = gen.load_curated_race_ids()
        assert isinstance(ids, set)
        assert "wa-lewis-sheriff-2026" in ids

    def test_missing_config_returns_empty_set(self, monkeypatch, tmp_path):
        gen = _load_gen()
        monkeypatch.setattr(gen, "DATA_DIR", tmp_path)  # no curated_races.json here
        assert gen.load_curated_race_ids() == set()


# ---------------------------------------------------------------------------
# Integration: main() preserves curated pages, regenerates the rest
# ---------------------------------------------------------------------------
class TestMainPreservesCurated:
    @pytest.fixture
    def staged(self, tmp_path, monkeypatch):
        """Set up a tmp site with one curated race and one bulk race."""
        gen = _load_gen()

        data_dir = tmp_path / "data"
        races_dir = tmp_path / "races"
        dossier_root = tmp_path / "dossiers"
        data_dir.mkdir()
        races_dir.mkdir()

        # Minimal states.json
        (data_dir / "states.json").write_text(json.dumps(
            {"states": [{"abbr": "WA", "name": "Washington", "slug": "washington"}]}))

        # Curated race: protected; Bulk race: regenerated
        (data_dir / "races.json").write_text(json.dumps({"races": [
            {"id": "wa-lewis-sheriff-2026", "state_abbr": "WA", "office": "County Sheriff",
             "year": 2026, "title": "Lewis County Sheriff", "level": "county",
             "county": "Lewis", "url": "/races/wa-lewis-sheriff-2026/",
             "candidates": [{"name": "Jane Curated", "party": "R",
                             "url": "/races/wa-lewis-sheriff-2026/curated/"}]},
            {"id": "wa-adams-assessor-2026", "state_abbr": "WA", "office": "County Assessor",
             "year": 2026, "title": "Adams County Assessor", "level": "county",
             "county": "Adams", "url": "/races/wa-adams-assessor-2026/",
             "candidates": [{"name": "Joe Bulk", "party": "D",
                             "url": "/races/wa-adams-assessor-2026/bulk/"}]},
        ]}))

        (data_dir / "curated_races.json").write_text(json.dumps(
            {"curated_race_ids": ["wa-lewis-sheriff-2026"]}))

        # Pre-existing curated pages with a recognizable sentinel
        SENTINEL = "<!-- HAND-CURATED DEEP DIVE — DO NOT OVERWRITE -->"
        curated_race = races_dir / "wa-lewis-sheriff-2026"
        (curated_race / "curated").mkdir(parents=True)
        (curated_race / "index.html").write_text(SENTINEL)
        (curated_race / "curated" / "index.html").write_text(SENTINEL)

        monkeypatch.setattr(gen, "DATA_DIR", data_dir)
        monkeypatch.setattr(gen, "RACES_DIR", races_dir)
        monkeypatch.setattr(gen, "DOSSIER_ROOT", dossier_root)
        monkeypatch.setattr(gen.sys, "argv", ["generate_candidate_pages.py", "WA"])

        gen.main()
        return {"gen": gen, "races_dir": races_dir, "sentinel": SENTINEL}

    def test_curated_overview_not_overwritten(self, staged):
        page = staged["races_dir"] / "wa-lewis-sheriff-2026" / "index.html"
        assert page.read_text() == staged["sentinel"]

    def test_curated_candidate_not_overwritten(self, staged):
        page = staged["races_dir"] / "wa-lewis-sheriff-2026" / "curated" / "index.html"
        assert page.read_text() == staged["sentinel"]

    def test_bulk_race_is_generated(self, staged):
        page = staged["races_dir"] / "wa-adams-assessor-2026" / "bulk" / "index.html"
        assert page.exists()
        assert "Joe Bulk" in page.read_text()
        assert staged["sentinel"] not in page.read_text()
