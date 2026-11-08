"""Tests for the neutral-form transform rules."""

from __future__ import annotations

from skill_sync.rules import CLAUDE, CODEX, normalize, render


def test_claude_literals_become_placeholders() -> None:
    result = normalize("Read CLAUDE.md and ~/.claude/skills.", CLAUDE)
    assert result.text == "Read {{instructions_file}} and {{config_dir}}/skills."
    assert result.ambiguous == ()


def test_codex_literals_become_placeholders() -> None:
    result = normalize("Read AGENTS.md and ~/.codex/skills.", CODEX)
    assert result.text == "Read {{instructions_file}} and {{config_dir}}/skills."


def test_render_targets_each_dialect() -> None:
    neutral = "See {{instructions_file}} in {{config_dir}}."
    assert render(neutral, CLAUDE) == "See CLAUDE.md in ~/.claude."
    assert render(neutral, CODEX) == "See AGENTS.md in ~/.codex."


def test_legacy_alias_is_accepted_and_rewritten_canonically() -> None:
    neutral = normalize("Config in ~/.Codex/notes", CODEX).text
    assert neutral == "Config in {{config_dir}}/notes"
    assert render(neutral, CODEX) == "Config in ~/.codex/notes"


def test_whole_token_matching_leaves_lookalikes_alone() -> None:
    text = "~/.claude.json and MYCLAUDE.md and ~/.claude-code"
    assert normalize(text, CLAUDE).text == text


def test_mixing_own_and_foreign_literal_is_ambiguous() -> None:
    result = normalize("Symlink AGENTS.md to CLAUDE.md.", CLAUDE)
    assert result.ambiguous == ("{{instructions_file}}",)
    assert result.text == "Symlink AGENTS.md to CLAUDE.md."


def test_foreign_literal_alone_is_not_ambiguous() -> None:
    result = normalize("Codex reads AGENTS.md.", CLAUDE)
    assert result.ambiguous == ()
    assert result.text == "Codex reads AGENTS.md."
