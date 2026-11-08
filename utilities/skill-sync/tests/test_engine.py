"""Tests for the per-skill sync decisions and their application."""

from __future__ import annotations

from conftest import MakeSkill
from skill_sync.engine import Status, apply_plans, build_plans, diff_lines
from skill_sync.locations import Scope
from skill_sync.rules import CLAUDE, CODEX
from skill_sync.state import load_state


def _sync(scope: Scope, *, dry_run: bool = False, prefer: str | None = None) -> None:
    apply_plans(scope, build_plans(scope, prefer=prefer), dry_run=dry_run)


def _status(scope: Scope, name: str) -> Status:
    return next(p for p in build_plans(scope) if p.name == name).status


def test_missing_codex_copy_is_created_and_baselined(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha")
    [plan] = build_plans(scope)
    assert plan.status is Status.MISSING_CODEX
    _sync(scope)
    text = (scope.codex_dir / "alpha" / "SKILL.md").read_text(encoding="utf-8")
    assert "AGENTS.md" in text
    assert "alpha" in load_state(scope.state_path)
    assert _status(scope, "alpha") is Status.IN_SYNC


def test_codex_only_skill_is_copied_to_claude_in_a_project(
    scope: Scope, make_skill: MakeSkill
) -> None:
    make_skill(scope.codex_dir, "beta", body="Read AGENTS.md\n")
    _sync(scope)
    assert "CLAUDE.md" in (scope.claude_dir / "beta" / "SKILL.md").read_text(encoding="utf-8")


def test_edit_on_codex_side_propagates_to_claude(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha")
    _sync(scope)
    skill = scope.codex_dir / "alpha" / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "New AGENTS.md rule.\n", encoding="utf-8")
    assert _status(scope, "alpha") is Status.CODEX_CHANGED
    _sync(scope)
    assert "New CLAUDE.md rule." in (scope.claude_dir / "alpha" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert _status(scope, "alpha") is Status.IN_SYNC


def test_edit_on_claude_side_propagates_to_codex(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha")
    _sync(scope)
    skill = scope.claude_dir / "alpha" / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8") + "More ~/.claude detail.\n", encoding="utf-8"
    )
    assert _status(scope, "alpha") is Status.CLAUDE_CHANGED
    _sync(scope)
    assert "More ~/.codex detail." in (scope.codex_dir / "alpha" / "SKILL.md").read_text(
        encoding="utf-8"
    )


def test_both_sides_changed_is_a_conflict_and_nothing_is_written(
    scope: Scope, make_skill: MakeSkill
) -> None:
    make_skill(scope.claude_dir, "alpha")
    _sync(scope)
    for folder, line in ((scope.claude_dir, "claude edit"), (scope.codex_dir, "codex edit")):
        skill = folder / "alpha" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + line + "\n", encoding="utf-8")
    [plan] = build_plans(scope)
    assert plan.status is Status.CONFLICT
    assert plan.needs_attention
    _sync(scope)
    assert "codex edit" not in (scope.claude_dir / "alpha" / "SKILL.md").read_text(encoding="utf-8")


def test_prefer_resolves_a_conflict(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha")
    _sync(scope)
    for folder, line in ((scope.claude_dir, "claude edit"), (scope.codex_dir, "codex edit")):
        skill = folder / "alpha" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + line + "\n", encoding="utf-8")
    _sync(scope, prefer=CLAUDE)
    assert "claude edit" in (scope.codex_dir / "alpha" / "SKILL.md").read_text(encoding="utf-8")
    assert "codex edit" not in (scope.codex_dir / "alpha" / "SKILL.md").read_text(encoding="utf-8")
    assert _status(scope, "alpha") is Status.IN_SYNC


def test_difference_without_baseline_is_a_conflict(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha", body="one\n")
    make_skill(scope.codex_dir, "alpha", body="two\n")
    assert _status(scope, "alpha") is Status.CONFLICT
    assert any("two" in line for line in diff_lines(scope, "alpha"))


def test_user_scope_leaves_foreign_codex_skills_alone(user: Scope, make_skill: MakeSkill) -> None:
    make_skill(user.codex_dir, "azure-deploy")
    [plan] = build_plans(user)
    assert plan.status is Status.FOREIGN
    apply_plans(user, [plan], dry_run=False)
    assert not (user.claude_dir / "azure-deploy").exists()


def test_foreign_skill_is_never_read_even_if_its_text_looks_ambiguous(
    user: Scope, make_skill: MakeSkill
) -> None:
    make_skill(user.codex_dir, "theirs", body="Symlink AGENTS.md to CLAUDE.md\n")
    [plan] = build_plans(user)
    assert plan.status is Status.FOREIGN
    assert plan.trees == {}


def test_user_scope_still_creates_codex_copies_of_claude_skills(
    user: Scope, make_skill: MakeSkill
) -> None:
    make_skill(user.claude_dir, "mine")
    _sync(user)
    assert (user.codex_dir / "mine" / "SKILL.md").is_file()


def test_alias_spelling_is_rewritten_without_touching_the_other_side(
    scope: Scope, make_skill: MakeSkill
) -> None:
    make_skill(scope.claude_dir, "alpha", body="Notes in ~/.claude/x\n")
    make_skill(scope.codex_dir, "alpha", body="Notes in ~/.Codex/x\n")
    assert _status(scope, "alpha") is Status.DRIFTED
    _sync(scope)
    assert "~/.codex/x" in (scope.codex_dir / "alpha" / "SKILL.md").read_text(encoding="utf-8")
    assert _status(scope, "alpha") is Status.IN_SYNC


def test_ambiguous_skill_is_reported_not_written(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha", body="Symlink AGENTS.md to CLAUDE.md\n")
    [plan] = build_plans(scope)
    assert plan.status is Status.AMBIGUOUS
    _sync(scope)
    assert not (scope.codex_dir / "alpha").exists()


def test_text_that_would_not_roundtrip_is_ambiguous(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha", body="Codex lives in ~/.codex\n")
    [plan] = build_plans(scope)
    assert plan.status is Status.AMBIGUOUS
    assert "round-trip" in plan.detail


def test_existing_non_skill_destination_is_not_overwritten(
    scope: Scope, make_skill: MakeSkill
) -> None:
    make_skill(scope.claude_dir, "alpha")
    (scope.codex_dir / "alpha").mkdir(parents=True)
    (scope.codex_dir / "alpha" / "keep.txt").write_text("mine", encoding="utf-8")
    [plan] = build_plans(scope)
    assert plan.status is Status.CONFLICT
    _sync(scope)
    assert (scope.codex_dir / "alpha" / "keep.txt").is_file()


def test_dry_run_changes_nothing(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha")
    _sync(scope, dry_run=True)
    assert not scope.codex_dir.exists()
    assert not scope.state_path.exists()


def test_deleted_file_propagates(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha", references__extra="x")
    _sync(scope)
    (scope.claude_dir / "alpha" / "references" / "extra").unlink()
    _sync(scope)
    assert not (scope.codex_dir / "alpha" / "references" / "extra").exists()


def test_only_filter_limits_plans(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, "alpha")
    make_skill(scope.claude_dir, "beta")
    plans = build_plans(scope, only=("beta",))
    assert [p.name for p in plans] == ["beta"]


def test_hidden_and_non_skill_folders_are_ignored(scope: Scope, make_skill: MakeSkill) -> None:
    make_skill(scope.claude_dir, ".hidden")
    (scope.claude_dir / "synced" / "bundle").mkdir(parents=True)
    (scope.claude_dir / "synced" / "bundle" / "x.txt").write_text("x", encoding="utf-8")
    assert build_plans(scope) == []
    assert CODEX != CLAUDE
