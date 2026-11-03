"""Tests for attention flag logic."""

from __future__ import annotations

from datetime import datetime, timedelta

from repo_radar.attention import compute_flags
from repo_radar.models import GitHubState, GitState, ProjectMeta

NOW = datetime(2026, 11, 3).astimezone()


def _git(**kw: object) -> GitState:
    base = {
        "is_git": True,
        "branch": "main",
        "upstream": "origin/main",
        "remote_url": "https://github.com/o/r.git",
        "last_commit": NOW.isoformat(),
    }
    return GitState(**{**base, **kw})  # type: ignore[arg-type]


def _meta(stage: str = "active") -> ProjectMeta:
    return ProjectMeta(present=True, stage=stage)


def test_clean_repo_has_no_flags() -> None:
    assert compute_flags(_meta(), _git(), None, now=NOW) == []


def test_not_git_short_circuits() -> None:
    flags = compute_flags(ProjectMeta(), GitState(is_git=False), None, now=NOW)
    assert flags == ["not-git", "no-meta"]


def test_git_error_short_circuits() -> None:
    flags = compute_flags(_meta(), GitState(is_git=True, error="boom"), None, now=NOW)
    assert flags == ["git-error"]


def test_dirty_unpushed_behind() -> None:
    flags = compute_flags(_meta(), _git(dirty=2, ahead=1, behind=3), None, now=NOW)
    assert flags == ["dirty", "unpushed", "behind"]


def test_no_remote_and_no_upstream() -> None:
    assert "no-remote" in compute_flags(_meta(), _git(remote_url="", upstream=""), None, now=NOW)
    assert "no-upstream" in compute_flags(_meta(), _git(upstream=""), None, now=NOW)


def test_detached_head_is_not_flagged_no_upstream() -> None:
    flags = compute_flags(_meta(), _git(upstream="", branch="(detached)"), None, now=NOW)
    assert "no-upstream" not in flags


def test_github_flags() -> None:
    gh = GitHubState(slug="o/r", open_prs=2, ci_status="failure")
    flags = compute_flags(_meta(), _git(), gh, now=NOW)
    assert flags == ["open-prs", "ci-failing"]


def test_stale_applies_to_active_but_not_paused() -> None:
    old = (NOW - timedelta(days=90)).isoformat()
    assert "stale" in compute_flags(_meta("active"), _git(last_commit=old), None, now=NOW)
    assert "stale" not in compute_flags(_meta("paused"), _git(last_commit=old), None, now=NOW)


def _expecting(visibility: str) -> ProjectMeta:
    return ProjectMeta(present=True, stage="active", visibility=visibility)


def test_visibility_match_is_clean() -> None:
    gh = GitHubState(slug="o/r", visibility="private")
    assert compute_flags(_expecting("private"), _git(), gh, now=NOW) == []


def test_visibility_mismatch_is_flagged() -> None:
    gh = GitHubState(slug="o/r", visibility="public")
    flags = compute_flags(_expecting("private"), _git(), gh, now=NOW)
    assert flags == ["visibility-mismatch"]


def test_unverifiable_visibility_is_flagged_not_passed() -> None:
    # gh skipped entirely, and gh lookup failed (visibility left empty)
    assert compute_flags(_expecting("private"), _git(), None, now=NOW) == ["visibility-unknown"]
    failed = GitHubState(slug="o/r", error="boom")
    assert compute_flags(_expecting("private"), _git(), failed, now=NOW) == ["visibility-unknown"]


def test_visibility_expectation_ignored_for_local_only_repo() -> None:
    flags = compute_flags(_expecting("public"), _git(remote_url="", upstream=""), None, now=NOW)
    assert flags == ["no-remote"]


def test_no_expectation_means_no_visibility_flag() -> None:
    gh = GitHubState(slug="o/r", visibility="public")
    assert compute_flags(_meta(), _git(), gh, now=NOW) == []


def test_meta_flags() -> None:
    assert compute_flags(ProjectMeta(), _git(), None, now=NOW) == ["no-meta"]
    assert compute_flags(ProjectMeta(present=True), _git(), None, now=NOW) == ["no-meta"]
    bad = ProjectMeta(present=True, error="x")
    assert compute_flags(bad, _git(), None, now=NOW) == ["bad-meta"]
