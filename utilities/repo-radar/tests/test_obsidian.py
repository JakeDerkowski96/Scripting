"""Obsidian export: generated parts refresh, human parts survive."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from repo_radar import cli, config, obsidian
from repo_radar.exceptions import ConfigurationError
from repo_radar.models import GitHubState, GitState, Project, ProjectMeta, ScanResult

NOW = datetime(2026, 11, 12, 9, 30, tzinfo=UTC)


def _project(name: str = "demo", **kw: object) -> Project:
    return Project(
        name=name,
        path=f"/r/{name}",
        meta=ProjectMeta(present=True, summary="A demo | tool", stage="active", next_step="ship"),
        git=GitState(is_git=True, branch="main", last_commit="2026-11-10T08:00:00+00:00"),
        github=GitHubState(slug=f"me/{name}", visibility="public", open_prs=2, ci_status="success"),
        flags=list(kw.get("flags", ["open-prs"])),  # type: ignore[call-overload]
    )


def test_new_note_has_frontmatter_block_and_human_sections() -> None:
    text = obsidian.merge_note(None, _project(), NOW)
    assert text.startswith('---\ntype: "repo"\nstage: "active"')
    assert obsidian.START in text and obsidian.END in text
    assert "## Notes" in text and "## Decisions" in text
    assert "**Next step:** ship" in text
    assert "- `open-prs`:" in text


def test_pipe_in_summary_does_not_break_table_cells() -> None:
    text = obsidian.render_block(_project(), NOW)
    assert "A demo | tool" in text  # summary sits outside the table
    row = next(ln for ln in text.splitlines() if ln.startswith("| Stage"))
    assert row.count("|") == 3


def test_merge_preserves_human_text_and_extra_frontmatter() -> None:
    first = obsidian.merge_note(None, _project(), NOW)
    edited = first.replace("---\n# demo", "mykey: keep me\n---\n# demo", 1).replace(
        "## Notes\n", "## Notes\nmy own words\n"
    )
    updated = _project(flags=[])
    updated.meta.stage = "maintenance"
    again = obsidian.merge_note(edited, updated, NOW)
    assert "my own words" in again
    assert "mykey: keep me" in again
    assert 'stage: "maintenance"' in again
    assert 'stage: "active"' not in again
    assert "Needs attention" not in again  # flag cleared, so the section is gone


def test_merge_without_markers_appends_block() -> None:
    again = obsidian.merge_note("# demo\n\nhand-written\n", _project(), NOW)
    assert again.startswith("---\n")
    assert "hand-written" in again
    assert again.count(obsidian.START) == 1


def test_merge_is_idempotent() -> None:
    first = obsidian.merge_note(None, _project(), NOW)
    assert obsidian.merge_note(first, _project(), NOW) == first


def test_export_writes_then_reports_unchanged(tmp_path: Path) -> None:
    result = ScanResult(
        scanned_at="x", root="/r", projects=[_project("a"), _project("b", flags=[])]
    )
    vault = tmp_path / "vault"
    first = obsidian.export(vault, result, result.projects, NOW)
    assert {a.verb for a in first} == {"created"}
    assert (vault / "Repos" / "a.md").is_file()
    assert (vault / obsidian.FOLLOW_UPS).is_file()
    dash = (vault / obsidian.DASHBOARD).read_text(encoding="utf-8")
    assert "[[Repos/a\\|a]]" in dash and "**2** repos, **1** needing attention" in dash
    second = obsidian.export(vault, result, result.projects, NOW)
    assert {a.verb for a in second} == {"unchanged"}


def test_follow_ups_is_never_overwritten(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / obsidian.FOLLOW_UPS).write_bytes(b"mine\n")
    result = ScanResult(scanned_at="x", root="/r", projects=[_project()])
    obsidian.export(vault, result, result.projects, NOW)
    assert (vault / obsidian.FOLLOW_UPS).read_bytes() == b"mine\n"


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    result = ScanResult(scanned_at="x", root="/r", projects=[_project()])
    actions = obsidian.export(tmp_path / "v", result, result.projects, NOW, dry_run=True)
    assert actions and not (tmp_path / "v").exists()


def test_files_use_lf_endings(tmp_path: Path) -> None:
    result = ScanResult(scanned_at="x", root="/r", projects=[_project()])
    obsidian.export(tmp_path, result, result.projects, NOW)
    assert b"\r\n" not in (tmp_path / "Repos" / "demo.md").read_bytes()


def test_resolve_vault_prefers_flag_then_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv(config.ENV_VAULT, raising=False)
    with pytest.raises(ConfigurationError):
        config.resolve_vault(None)
    monkeypatch.setenv(config.ENV_VAULT, str(tmp_path / "env"))
    assert config.resolve_vault(None) == tmp_path / "env"
    assert config.resolve_vault(tmp_path / "flag") == tmp_path / "flag"


def test_cli_obsidian_command(
    tmp_path: Path, make_repo, capsys: pytest.CaptureFixture[str]
) -> None:  # type: ignore[no-untyped-def]
    root = tmp_path / "repos"
    root.mkdir()
    repo = make_repo("demo")
    repo.rename(root / "demo")
    vault = tmp_path / "vault"
    code = cli.main(
        [
            "obsidian",
            "--root",
            str(root),
            "--cache",
            str(tmp_path / "c.json"),
            "--no-github",
            "--refresh",
            "--vault",
            str(vault),
        ]
    )
    assert code == 0
    assert (vault / "Repos" / "demo.md").is_file()
    assert "written in" in capsys.readouterr().out
