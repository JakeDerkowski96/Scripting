"""Tests for the sync baseline file."""

from __future__ import annotations

from pathlib import Path

import pytest

from skill_sync.exceptions import StateError
from skill_sync.state import load_state, save_state


def test_missing_file_means_no_baselines(tmp_path: Path) -> None:
    assert load_state(tmp_path / "nope.json") == {}


def test_roundtrip_is_sorted(tmp_path: Path) -> None:
    path = tmp_path / "dir" / "state.json"
    save_state(path, {"b": "2", "a": "1"})
    assert load_state(path) == {"a": "1", "b": "2"}
    assert path.read_text(encoding="utf-8").index('"a"') < path.read_text(encoding="utf-8").index(
        '"b"'
    )


def test_corrupt_file_raises_state_error(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(StateError):
        load_state(path)
