"""Tests for .project.toml parsing and drafting."""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_radar.exceptions import MetadataError
from repo_radar.meta import (
    META_FILENAME,
    draft_summary,
    load_meta,
    parse_meta,
    render_template,
    write_template,
)


def test_parse_meta_reads_all_fields() -> None:
    meta = parse_meta(
        'summary = "S"\nstage = "active"\nnext = "N"\nblockers = ["b"]\ntags = ["t"]\n'
    )
    assert (meta.summary, meta.stage, meta.next_step) == ("S", "active", "N")
    assert meta.blockers == ["b"]
    assert meta.tags == ["t"]
    assert meta.present


def test_parse_meta_reads_and_validates_visibility() -> None:
    assert parse_meta('visibility = "private"').visibility == "private"
    with pytest.raises(MetadataError, match="unknown visibility"):
        parse_meta('visibility = "secret"')


def test_parse_meta_rejects_unknown_stage() -> None:
    with pytest.raises(MetadataError, match="unknown stage"):
        parse_meta('stage = "wip"')


def test_parse_meta_rejects_wrong_types() -> None:
    with pytest.raises(MetadataError, match="blockers"):
        parse_meta("blockers = 3")
    with pytest.raises(MetadataError, match="summary"):
        parse_meta("summary = 3")


def test_parse_meta_rejects_invalid_toml() -> None:
    with pytest.raises(MetadataError, match="invalid TOML"):
        parse_meta("this is = = not toml")


def test_load_meta_missing_file_is_not_present(tmp_path: Path) -> None:
    assert load_meta(tmp_path).present is False


def test_load_meta_records_error_instead_of_raising(tmp_path: Path) -> None:
    (tmp_path / META_FILENAME).write_text('stage = "nope"', encoding="utf-8")
    meta = load_meta(tmp_path)
    assert meta.present
    assert "unknown stage" in meta.error


def test_template_round_trips_and_leaves_stage_unset() -> None:
    meta = parse_meta(render_template('A "quoted" summary'))
    assert meta.summary == 'A "quoted" summary'
    assert meta.stage == ""


def test_draft_summary_skips_headings_and_badges(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "# Title\n\n[![ci](x)](y)\n\nDoes the thing.\n", encoding="utf-8"
    )
    assert draft_summary(tmp_path) == "Does the thing."


def test_draft_summary_without_readme_is_empty(tmp_path: Path) -> None:
    assert draft_summary(tmp_path) == ""


def test_write_template_dry_run_writes_nothing(tmp_path: Path) -> None:
    assert write_template(tmp_path, "x", dry_run=True) is True
    assert not (tmp_path / META_FILENAME).exists()


def test_write_template_does_not_overwrite_without_force(tmp_path: Path) -> None:
    (tmp_path / META_FILENAME).write_text("summary = 'keep'", encoding="utf-8")
    assert write_template(tmp_path, "new") is False
    assert "keep" in (tmp_path / META_FILENAME).read_text(encoding="utf-8")
    assert write_template(tmp_path, "new", force=True) is True
