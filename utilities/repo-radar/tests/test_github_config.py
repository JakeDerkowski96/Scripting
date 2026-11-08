"""Tests for GitHub CLI handling (mocked at the subprocess boundary) and config."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from repo_radar import github
from repo_radar.config import ENV_ROOT, resolve_root
from repo_radar.exceptions import ConfigurationError, GitHubError


def _fake_run(responses: dict[str, Any]) -> Any:
    """Build a subprocess.run stand-in keyed on the gh subcommand ('repo', 'pr', ...)."""

    def run(cmd: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        value = responses[cmd[1]]
        if isinstance(value, Exception):
            raise value
        if isinstance(value, str):  # an error message from gh
            return subprocess.CompletedProcess(cmd, 1, "", value)
        return subprocess.CompletedProcess(cmd, 0, json.dumps(value), "")

    return run


def test_fetch_state_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        _fake_run(
            {
                "repo": {
                    "visibility": "PUBLIC",
                    "isArchived": False,
                    "defaultBranchRef": {"name": "main"},
                },
                "pr": [{"number": 1, "isDraft": True}, {"number": 2, "isDraft": False}],
                "issue": [{"number": 3}],
                "run": [{"status": "completed", "conclusion": "failure"}],
            }
        ),
    )
    state = github.fetch_state("o/r")
    assert (state.visibility, state.default_branch) == ("public", "main")
    assert (state.open_prs, state.draft_prs, state.open_issues) == (2, 1, 1)
    assert state.ci_status == "failure"
    assert state.error == ""


def test_fetch_state_repo_lookup_failure_is_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", _fake_run({"repo": "Could not resolve to a Repository"}))
    state = github.fetch_state("o/missing")
    assert "Could not resolve" in state.error
    assert state.open_prs is None


def test_fetch_state_partial_failure_keeps_other_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        _fake_run(
            {
                "repo": {"defaultBranchRef": {"name": "main"}},
                "pr": [],
                "issue": "the 'o/r' repository has disabled issues",
                "run": [{"status": "in_progress", "conclusion": None}],
            }
        ),
    )
    state = github.fetch_state("o/r")
    assert state.open_prs == 0
    assert state.open_issues is None
    assert "disabled issues" in state.error
    assert state.ci_status == "running"


def test_gh_missing_and_timeout_raise_github_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", _fake_run({"repo": FileNotFoundError()}))
    with pytest.raises(GitHubError, match="not found"):
        github._gh("repo", "view")
    timeout = subprocess.TimeoutExpired("gh", 30)
    monkeypatch.setattr(subprocess, "run", _fake_run({"repo": timeout}))
    with pytest.raises(GitHubError, match="timed out"):
        github._gh("repo", "view")


def test_gh_invalid_json_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def run(cmd: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, 0, "not json", "")

    monkeypatch.setattr(subprocess, "run", run)
    with pytest.raises(GitHubError, match="invalid JSON"):
        github._gh("repo", "view")


def test_resolve_root_explicit_and_missing(tmp_path: Path) -> None:
    assert resolve_root(tmp_path) == tmp_path.resolve()
    with pytest.raises(ConfigurationError, match="--root"):
        resolve_root(tmp_path / "nope")


def test_resolve_root_uses_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_ROOT, str(tmp_path))
    assert resolve_root() == tmp_path.resolve()
    monkeypatch.setenv(ENV_ROOT, str(tmp_path / "nope"))
    with pytest.raises(ConfigurationError):
        resolve_root()
