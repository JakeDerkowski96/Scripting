"""Transform rules between the tool-neutral skill form and each agent's dialect.

A skill is compared and stored in a neutral form where tool-specific text is replaced by a
placeholder (for example ``CLAUDE.md`` and ``AGENTS.md`` both become ``{{instructions_file}}``).
Rendering turns the placeholders back into one agent's literals.

Required permissions: none (pure text functions, no file or network access).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

CLAUDE = "claude"
CODEX = "codex"
TARGETS: tuple[str, ...] = (CLAUDE, CODEX)


@dataclass(frozen=True)
class Rule:
    """One substitution: a placeholder plus the literal each target uses for it."""

    placeholder: str
    literals: dict[str, str]
    # Legacy spellings accepted when normalising; they are always rendered as the canonical literal.
    aliases: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def own(self, target: str) -> tuple[str, ...]:
        """Literals that belong to ``target`` (canonical first, then aliases)."""
        return (self.literals[target], *self.aliases.get(target, ()))

    def foreign(self, target: str) -> tuple[str, ...]:
        """Literals that belong to every other target."""
        found: list[str] = []
        for other in TARGETS:
            if other != target:
                found.extend(self.own(other))
        return tuple(found)


# Codex's home is ~/.codex. The capitalised spelling only works on case-insensitive file systems
# (Windows), so it is accepted as an alias and rewritten to the portable form.
RULES: tuple[Rule, ...] = (
    Rule("{{instructions_file}}", {CLAUDE: "CLAUDE.md", CODEX: "AGENTS.md"}),
    Rule(
        "{{config_dir}}",
        {CLAUDE: "~/.claude", CODEX: "~/.codex"},
        aliases={CODEX: ("~/.Codex",)},
    ),
)


@dataclass(frozen=True)
class Normalized:
    """Result of normalising one text: the neutral text plus any rules that could not be applied."""

    text: str
    ambiguous: tuple[str, ...]


def _pattern(literals: tuple[str, ...]) -> re.Pattern[str]:
    """Match any literal as a whole token, so ``~/.claude.json`` or ``MYCLAUDE.md`` are untouched."""
    alternation = "|".join(re.escape(item) for item in sorted(literals, key=len, reverse=True))
    return re.compile(rf"(?<![A-Za-z0-9_])(?:{alternation})(?![A-Za-z0-9_-])(?!\.[A-Za-z0-9])")


def normalize(text: str, target: str) -> Normalized:
    """Replace ``target``'s literals with placeholders.

    A rule is skipped and reported as ambiguous when the text holds both this target's literal and
    another target's literal for it: rendering for the other target would then turn a deliberate
    mention (for example "symlink AGENTS.md to CLAUDE.md") into a duplicate.
    """
    out = text
    ambiguous: list[str] = []
    for rule in RULES:
        own = _pattern(rule.own(target))
        if own.search(out) and _pattern(rule.foreign(target)).search(out):
            ambiguous.append(rule.placeholder)
            continue
        out = own.sub(rule.placeholder, out)
    return Normalized(out, tuple(ambiguous))


def render(neutral: str, target: str) -> str:
    """Replace placeholders with ``target``'s canonical literals."""
    out = neutral
    for rule in RULES:
        out = out.replace(rule.placeholder, rule.literals[target])
    return out
