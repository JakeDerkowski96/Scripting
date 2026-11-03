"""Tests for scanning, caching, querying and rendering."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pytest

from repo_radar import cache, scanner
from repo_radar.cli import main
from repo_radar.exceptions import CacheError, ConfigurationError
from repo_radar.meta import META_FILENAME
from repo_radar.models import ScanResult
from repo_radar.query import filter_projects, sort_projects
from repo_radar.render_html import render_html
from repo_radar.render_table import render_detail, render_table


def _scan(root: Path) -> ScanResult:
    return scanner.scan(root, use_github=False)


def test_discover_skips_dot_folders_and_files(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "A").mkdir()
    (tmp_path / "file.txt").write_text("x", encoding="utf-8")
    assert [p.name for p in scanner.discover(tmp_path)] == ["A", "b"]


def test_discover_missing_root_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        scanner.discover(tmp_path / "nope")


def test_scan_includes_non_git_folder_with_flag(
    tmp_path: Path, make_repo: Callable[..., Path]
) -> None:
    make_repo("repo")
    (tmp_path / "plain").mkdir()
    result = _scan(tmp_path)
    by_name = {p.name: p for p in result.projects}
    assert "not-git" in by_name["plain"].flags
    assert by_name["repo"].git.is_git


def test_cache_round_trip(tmp_path: Path, make_repo: Callable[..., Path]) -> None:
    make_repo("repo")
    result = _scan(tmp_path)
    path = tmp_path / "out" / "scan.json"
    cache.save(result, path)
    assert cache.load(path) == result


def test_cache_load_errors(tmp_path: Path) -> None:
    with pytest.raises(CacheError, match="scan"):
        cache.load(tmp_path / "missing.json")
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(CacheError, match="unreadable"):
        cache.load(bad)


def test_filter_and_sort(tmp_path: Path, make_repo: Callable[..., Path]) -> None:
    make_repo("zeta")
    alpha = make_repo("alpha")
    (alpha / META_FILENAME).write_text('stage = "active"\ntags = ["x"]', encoding="utf-8")
    projects = _scan(tmp_path).projects
    assert [p.name for p in sort_projects(projects, "name")] == ["alpha", "zeta"]
    assert [p.name for p in filter_projects(projects, stage="active")] == ["alpha"]
    assert [p.name for p in filter_projects(projects, stage="unset")] == ["zeta"]
    assert [p.name for p in filter_projects(projects, text="X")] == ["alpha"]
    assert sort_projects(projects, "stage")[0].name == "alpha"


def test_table_and_detail_render(tmp_path: Path, make_repo: Callable[..., Path]) -> None:
    make_repo("repo")
    projects = _scan(tmp_path).projects
    now = datetime.now().astimezone()
    table = render_table(projects, now=now)
    assert "repo" in table and "1 projects" in table
    assert render_table([], now=now) == "No projects match."
    assert "path" in render_detail(projects[0], now=now)


def test_html_escapes_repo_content(tmp_path: Path, make_repo: Callable[..., Path]) -> None:
    repo = make_repo("repo")
    (repo / META_FILENAME).write_text(
        'summary = "<script>alert(1)</script>"\nstage = "active"', encoding="utf-8"
    )
    result = _scan(tmp_path)
    page = render_html(result, result.projects, now=datetime.now().astimezone())
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_cli_scan_list_and_report(
    tmp_path: Path,
    make_repo: Callable[..., Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    make_repo("repo")
    cache_file = tmp_path / "cache" / "scan.json"
    base = ["--root", str(tmp_path), "--cache", str(cache_file)]
    assert main(["scan", "--no-github", *base]) == 0
    assert "repo" in capsys.readouterr().out
    assert main(["list", *base]) == 0
    out_file = tmp_path / "report.html"
    assert main(["report", "-o", str(out_file), *base]) == 0
    assert "<!doctype html>" in out_file.read_text(encoding="utf-8")


def test_cli_show_unknown_project_exits_2(
    tmp_path: Path, make_repo: Callable[..., Path], capsys: pytest.CaptureFixture[str]
) -> None:
    make_repo("repo")
    base = ["--root", str(tmp_path), "--cache", str(tmp_path / "c.json"), "--no-github"]
    assert main(["show", "ghost", *base]) == 2
    assert "no project named" in capsys.readouterr().err


def test_cli_missing_root_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["scan", "--root", str(tmp_path / "nope"), "--cache", str(tmp_path / "c.json")])
    assert code == 1
    assert "Scan root not found" in capsys.readouterr().err


def test_cli_init_dry_run_then_real(tmp_path: Path, make_repo: Callable[..., Path]) -> None:
    repo = make_repo("repo")
    assert main(["init", "--all", "--dry-run", "--root", str(tmp_path)]) == 0
    assert not (repo / META_FILENAME).exists()
    assert main(["init", "repo", "--root", str(tmp_path)]) == 0
    assert (repo / META_FILENAME).exists()


def test_cli_check_passes_when_every_folder_is_a_repo(
    tmp_path: Path, make_repo: Callable[..., Path], capsys: pytest.CaptureFixture[str]
) -> None:
    make_repo("repo")
    args = ["check", "--no-github", "--root", str(tmp_path), "--cache", str(tmp_path / "c.json")]
    assert main(args) == 0
    assert "OK" in capsys.readouterr().out


def test_cli_check_fails_on_non_git_folder(
    tmp_path: Path, make_repo: Callable[..., Path], capsys: pytest.CaptureFixture[str]
) -> None:
    make_repo("repo")
    (tmp_path / "loose").mkdir()
    args = ["check", "--no-github", "--root", str(tmp_path), "--cache", str(tmp_path / "c.json")]
    assert main(args) == 3
    assert "VIOLATION loose: not-git" in capsys.readouterr().out


def test_cli_init_requires_target(tmp_path: Path) -> None:
    assert main(["init", "--root", str(tmp_path)]) == 2
    assert main(["init", "ghost", "--root", str(tmp_path)]) == 2
