"""Shared fixtures: throwaway git repos so tests never touch real ones."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest


def _run(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True)


@pytest.fixture
def make_repo(tmp_path: Path) -> Callable[..., Path]:
    """Return a factory that creates a git repo with N commits under tmp_path."""

    def factory(name: str = "demo", *, commits: int = 1, remote: str | None = None) -> Path:
        path = tmp_path / name
        path.mkdir()
        _run(path, "init", "-q", "-b", "main")
        _run(path, "config", "user.email", "test@example.com")
        _run(path, "config", "user.name", "Test")
        _run(path, "config", "commit.gpgsign", "false")
        for i in range(commits):
            (path / f"f{i}.txt").write_text(str(i), encoding="utf-8")
            _run(path, "add", "-A")
            _run(path, "commit", "-q", "-m", f"commit {i}")
        if remote:
            _run(path, "remote", "add", "origin", remote)
        return path

    return factory
