"""Tests for git state parsing and reading (against throwaway repos)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from repo_radar.github import parse_slug
from repo_radar.gitinfo import parse_status, read_state


def test_parse_status_reads_branch_ahead_behind_and_dirty() -> None:
    out = (
        "# branch.oid abc\n# branch.head main\n# branch.upstream origin/main\n"
        "# branch.ab +2 -1\n1 .M N... 100644 100644 100644 a b file.txt\n? new.txt\n"
    )
    state = parse_status(out)
    assert (state.branch, state.upstream) == ("main", "origin/main")
    assert (state.ahead, state.behind, state.dirty) == (2, 1, 2)


def test_read_state_non_git_folder(tmp_path: Path) -> None:
    assert read_state(tmp_path).is_git is False


def test_read_state_clean_repo(make_repo: Callable[..., Path]) -> None:
    state = read_state(make_repo(commits=2))
    assert state.is_git
    assert state.branch == "main"
    assert state.dirty == 0
    assert state.last_subject == "commit 1"
    assert state.remote_url == ""


def test_read_state_counts_untracked_files(make_repo: Callable[..., Path]) -> None:
    repo = make_repo()
    (repo / "new.txt").write_text("x", encoding="utf-8")
    assert read_state(repo).dirty == 1


def test_read_state_repo_without_commits(make_repo: Callable[..., Path]) -> None:
    state = read_state(make_repo(commits=0))
    assert state.is_git
    assert state.last_commit == ""
    assert state.error == ""


def test_read_state_reports_remote(make_repo: Callable[..., Path]) -> None:
    state = read_state(make_repo(remote="https://github.com/o/r.git"))
    assert state.remote_url == "https://github.com/o/r.git"


def test_read_state_corrupt_repo_records_error(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()  # looks like a repo but is not a valid one
    state = read_state(tmp_path)
    assert state.is_git
    assert state.error


def test_parse_slug_variants() -> None:
    assert parse_slug("https://github.com/o/r.git") == "o/r"
    assert parse_slug("git@github.com:o/r.git") == "o/r"
    assert parse_slug("https://github.com/o/r") == "o/r"
    assert parse_slug("https://gitlab.com/o/r.git") is None
    assert parse_slug("") is None
