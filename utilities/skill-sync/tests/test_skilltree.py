"""Tests for reading and writing skill folders."""

from __future__ import annotations

from pathlib import Path

from conftest import MakeSkill
from skill_sync.rules import CLAUDE, CODEX
from skill_sync.skilltree import read_tree, roundtrip_problems, write_tree


def test_text_is_neutralised_and_binary_is_raw(tmp_path: Path, make_skill: MakeSkill) -> None:
    folder = make_skill(tmp_path, "s", logo=b"\x89PNG\0data")
    tree = read_tree(folder, CLAUDE)
    assert b"{{instructions_file}}" in tree.files["SKILL.md"].content
    assert tree.files["logo"].is_text is False
    assert tree.files["logo"].content == b"\x89PNG\0data"


def test_digest_ignores_line_endings(tmp_path: Path, make_skill: MakeSkill) -> None:
    lf = make_skill(tmp_path / "a", "s")
    crlf = make_skill(tmp_path / "b", "s")
    (crlf / "SKILL.md").write_bytes((crlf / "SKILL.md").read_bytes().replace(b"\n", b"\r\n"))
    assert read_tree(lf, CLAUDE).digest() == read_tree(crlf, CLAUDE).digest()


def test_alias_spelling_is_flagged_as_drift(tmp_path: Path, make_skill: MakeSkill) -> None:
    folder = make_skill(tmp_path, "s", body="Notes in ~/.Codex/x\n")
    tree = read_tree(folder, CODEX)
    assert tree.drifted is True
    assert tree.ambiguous == {}


def test_target_only_files_are_ignored(tmp_path: Path, make_skill: MakeSkill) -> None:
    folder = make_skill(tmp_path, "s", agents__openai_yaml="x")
    (folder / "agents" / "openai.yaml").write_text("interface: {}", encoding="utf-8")
    assert "agents/openai.yaml" not in read_tree(folder, CODEX).files


def test_write_renders_for_target_and_preserves_newlines(
    tmp_path: Path, make_skill: MakeSkill
) -> None:
    src = make_skill(tmp_path / "claude", "s")
    (src / "SKILL.md").write_bytes((src / "SKILL.md").read_bytes().replace(b"\n", b"\r\n"))
    tree = read_tree(src, CLAUDE)
    dest = tmp_path / "codex" / "s"
    actions = write_tree(dest, tree, CODEX, dry_run=False)
    data = (dest / "SKILL.md").read_bytes()
    assert b"AGENTS.md" in data
    assert b"CLAUDE.md" not in data
    assert b"\r\n" in data
    assert actions == ["write SKILL.md"]


def test_write_removes_files_missing_from_source(tmp_path: Path, make_skill: MakeSkill) -> None:
    src = make_skill(tmp_path / "claude", "s")
    dest = make_skill(tmp_path / "codex", "s", stale__notes="old")
    actions = write_tree(dest, read_tree(src, CLAUDE), CODEX, dry_run=False)
    assert "remove stale/notes" in actions
    assert not (dest / "stale").exists()


def test_dry_run_writes_nothing(tmp_path: Path, make_skill: MakeSkill) -> None:
    src = make_skill(tmp_path / "claude", "s")
    dest = tmp_path / "codex" / "s"
    actions = write_tree(dest, read_tree(src, CLAUDE), CODEX, dry_run=True)
    assert actions == ["write SKILL.md"]
    assert not dest.exists()


def test_roundtrip_problem_when_text_holds_destination_token(
    tmp_path: Path, make_skill: MakeSkill
) -> None:
    folder = make_skill(tmp_path, "s", body="Codex lives in ~/.codex.\n")
    tree = read_tree(folder, CLAUDE)
    assert roundtrip_problems(tree, CODEX) == ["SKILL.md"]
    assert roundtrip_problems(tree, CLAUDE) == []
