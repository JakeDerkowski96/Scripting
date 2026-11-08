"""Tests for the command-line layer: exit codes and output."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import MakeSkill
from skill_sync.cli import main
from skill_sync.locations import Scope


def _args(scope: Scope, *rest: str) -> list[str]:
    repo = scope.claude_dir.parents[1]
    return [
        rest[0],
        "--scope",
        "project",
        "--repo",
        str(repo),
        "--home",
        str(repo / "nohome"),
        *rest[1:],
    ]


def test_status_lists_skills_and_exits_zero(
    scope: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(scope.claude_dir, "alpha")
    assert main(_args(scope, "status")) == 0
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "missing-codex" in out
    assert "1 skills: 0 in sync, 1 to sync" in out


def test_foreign_skills_are_hidden_unless_verbose(
    user: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(user.codex_dir, "theirs")
    home = user.claude_dir.parents[1]
    base = ["status", "--scope", "user", "--home", str(home)]
    assert main(base) == 0
    out = capsys.readouterr().out
    assert "theirs" not in out
    assert "1 from other tools hidden" in out
    assert main([*base, "-v"]) == 0
    assert "theirs" in capsys.readouterr().out


def test_check_exits_3_until_synced(
    scope: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(scope.claude_dir, "alpha")
    assert main(_args(scope, "check")) == 3
    assert "OUT OF SYNC project/alpha" in capsys.readouterr().out
    assert main(_args(scope, "sync")) == 0
    assert main(_args(scope, "check")) == 0
    assert "OK: 1 skills in sync" in capsys.readouterr().out


def test_sync_dry_run_reports_without_writing(
    scope: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(scope.claude_dir, "alpha")
    assert main([*_args(scope, "sync"), "--dry-run"]) == 0
    assert "[dry-run] project/alpha" in capsys.readouterr().out
    assert not scope.codex_dir.exists()


def test_sync_exits_3_when_a_skill_is_skipped(
    scope: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(scope.claude_dir, "alpha", body="one\n")
    make_skill(scope.codex_dir, "alpha", body="two\n")
    assert main(_args(scope, "sync")) == 3
    assert "skipped project/alpha: conflict" in capsys.readouterr().out
    assert main([*_args(scope, "sync"), "--prefer", "claude"]) == 0


def test_diff_prints_the_difference(
    scope: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(scope.claude_dir, "alpha", body="one\n")
    make_skill(scope.codex_dir, "alpha", body="two\n")
    assert main([*_args(scope, "diff"), "alpha"]) == 0
    assert "+two" in capsys.readouterr().out


def test_unknown_only_name_warns(
    scope: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(scope.claude_dir, "alpha")
    main([*_args(scope, "status"), "--only", "nope"])
    assert "no skill named 'nope'" in capsys.readouterr().err


def test_arguments_placeholder_is_noted(
    scope: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(scope.claude_dir, "alpha", body="Args: $ARGUMENTS\n")
    main(_args(scope, "status"))
    assert "uses $ARGUMENTS" in capsys.readouterr().err


def test_rules_prints_the_table(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["rules"]) == 0
    out = capsys.readouterr().out
    assert "CLAUDE.md" in out
    assert "AGENTS.md" in out
    assert "~/.Codex" in out


def test_project_scope_outside_a_repo_is_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["status", "--scope", "project", "--home", str(tmp_path)]) == 1
    assert "needs a git repository" in capsys.readouterr().err


def test_corrupt_state_is_a_clean_error(
    scope: Scope, make_skill: MakeSkill, capsys: pytest.CaptureFixture[str]
) -> None:
    make_skill(scope.claude_dir, "alpha")
    scope.state_path.write_text("{bad", encoding="utf-8")
    assert main(_args(scope, "status")) == 1
    assert "cannot read sync state" in capsys.readouterr().err
