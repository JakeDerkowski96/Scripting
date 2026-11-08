"""Shared fixtures: a throwaway project scope and a helper to create skill folders."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from skill_sync.locations import Scope, project_scope, user_scope

MakeSkill = Callable[..., Path]


@pytest.fixture
def scope(tmp_path: Path) -> Scope:
    """A project scope rooted in a temp directory."""
    return project_scope(tmp_path / "repo")


@pytest.fixture
def user(tmp_path: Path) -> Scope:
    """A user scope rooted in a temp 'home'."""
    return user_scope(tmp_path / "home")


@pytest.fixture
def make_skill() -> MakeSkill:
    """Create ``<root>/<name>/SKILL.md`` (plus extra files) and return the skill folder."""

    def _make(root: Path, name: str, body: str = "Use CLAUDE.md.\n", **extra: str | bytes) -> Path:
        folder = root / name
        folder.mkdir(parents=True, exist_ok=True)
        # Write bytes, not text: write_text would turn "\n" into "\r\n" on Windows and make the
        # fixtures differ by platform.
        (folder / "SKILL.md").write_bytes(f"---\nname: {name}\n---\n{body}".encode())
        for rel, content in extra.items():
            path = folder / rel.replace("__", "/")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content if isinstance(content, bytes) else content.encode())
        return folder

    return _make
