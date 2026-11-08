"""Decide, per skill, what is out of sync and which way to copy, then apply it.

Each skill is compared in neutral form against a stored baseline (the hash it had at the last
sync). A change on exactly one side is propagated to the other; a change on both sides, or a
difference with no baseline, is a conflict and is never written unless ``prefer`` picks a winner.

Required permissions: read access to both skill folders; write access to the destination skill
folders and the state file when applying (not in dry-run).
"""

from __future__ import annotations

import difflib
import logging
from dataclasses import dataclass, field
from enum import StrEnum

from skill_sync.locations import Scope
from skill_sync.rules import CLAUDE, CODEX
from skill_sync.skilltree import SKILL_FILE, NeutralTree, read_tree, roundtrip_problems, write_tree
from skill_sync.state import load_state, save_state

log = logging.getLogger(__name__)


class Status(StrEnum):
    """Where one skill stands."""

    IN_SYNC = "in-sync"
    DRIFTED = "drifted"
    CLAUDE_CHANGED = "claude-changed"
    CODEX_CHANGED = "codex-changed"
    MISSING_CODEX = "missing-codex"
    MISSING_CLAUDE = "missing-claude"
    CONFLICT = "conflict"
    AMBIGUOUS = "ambiguous"
    FOREIGN = "foreign"


@dataclass
class SkillPlan:
    """The verdict for one skill and, when there is work to do, the copies that fix it."""

    scope: str
    name: str
    status: Status
    detail: str = ""
    copies: tuple[tuple[str, str], ...] = ()  # (source target, destination target)
    new_hash: str | None = None  # baseline to record once both sides match
    trees: dict[str, NeutralTree] = field(default_factory=dict, repr=False)

    @property
    def needs_attention(self) -> bool:
        """True when `sync` cannot resolve this skill on its own."""
        return self.status in (Status.CONFLICT, Status.AMBIGUOUS) and not self.copies

    @property
    def pending(self) -> bool:
        """True when `sync` would change files for this skill."""
        return bool(self.copies)


@dataclass(frozen=True)
class SkillChange:
    """Files written or removed (or that would be, in dry-run) for one skill."""

    name: str
    actions: tuple[str, ...]


def other(target: str) -> str:
    """The other agent."""
    return CODEX if target == CLAUDE else CLAUDE


def _discover(scope: Scope, target: str) -> set[str]:
    """Names of skill folders (those holding SKILL.md) for one agent."""
    root = scope.directory(target)
    if not root.is_dir():
        return set()
    return {
        child.name
        for child in root.iterdir()
        if child.is_dir() and not child.name.startswith(".") and (child / SKILL_FILE).is_file()
    }


def _load(scope: Scope, target: str, name: str) -> NeutralTree | None:
    folder = scope.directory(target) / name
    return read_tree(folder, target) if (folder / SKILL_FILE).is_file() else None


def _blocked(scope: Scope, target: str, name: str) -> bool:
    """True when the destination folder exists with files but no SKILL.md (not ours to overwrite)."""
    folder = scope.directory(target) / name
    return folder.is_dir() and not (folder / SKILL_FILE).is_file() and any(folder.iterdir())


def _copy(plan: SkillPlan, scope: Scope, source: str, status: Status, detail: str) -> SkillPlan:
    """Fill ``plan`` with a copy from ``source`` to the other agent, after safety checks."""
    dest = other(source)
    tree = plan.trees[source]
    if _blocked(scope, dest, plan.name):
        plan.status, plan.detail = Status.CONFLICT, f"{dest} folder exists but has no {SKILL_FILE}"
        return plan
    problems = roundtrip_problems(tree, dest)
    if problems:
        plan.status = Status.AMBIGUOUS
        plan.detail = f"would not round-trip for {dest}: {', '.join(problems)}"
        return plan
    plan.status, plan.detail = status, detail
    plan.copies = ((source, dest),)
    plan.new_hash = tree.digest()
    return plan


def _is_foreign(scope: Scope, name: str, baseline: str | None) -> bool:
    """True for a skill only in the shared Codex folder that skill-sync has never managed."""
    only_codex = (scope.directory(CODEX) / name / SKILL_FILE).is_file() and not (
        scope.directory(CLAUDE) / name / SKILL_FILE
    ).is_file()
    return only_codex and baseline is None and not scope.adopt_codex_only


def _classify(scope: Scope, name: str, baseline: str | None, prefer: str | None) -> SkillPlan:
    if _is_foreign(scope, name, baseline):
        # Decided before reading any file: other managers own these, so they are never inspected.
        return SkillPlan(
            scope.name,
            name,
            Status.FOREIGN,
            "only in the shared Codex folder; not managed by skill-sync, left alone",
        )
    trees = {
        target: tree
        for target in (CLAUDE, CODEX)
        if (tree := _load(scope, target, name)) is not None
    }
    plan = SkillPlan(scope.name, name, Status.IN_SYNC, trees=trees)

    ambiguous = [f"{t}:{rel}" for t, tree in trees.items() for rel in tree.ambiguous]
    if ambiguous:
        plan.status = Status.AMBIGUOUS
        plan.detail = "mixes both agents' names for the same thing: " + ", ".join(ambiguous)
        return plan

    claude, codex = trees.get(CLAUDE), trees.get(CODEX)
    if claude is not None and codex is None:
        return _copy(plan, scope, CLAUDE, Status.MISSING_CODEX, "no .agents copy; will create it")
    if codex is not None and claude is None:
        return _copy(plan, scope, CODEX, Status.MISSING_CLAUDE, "no .claude copy; will create it")
    if claude is None or codex is None:  # pragma: no cover - names come from discovery
        return plan

    digest_claude, digest_codex = claude.digest(), codex.digest()
    if digest_claude == digest_codex:
        plan.new_hash = digest_claude
        fixes = tuple((t, t) for t, tree in trees.items() if tree.drifted)
        if fixes:
            plan.status = Status.DRIFTED
            plan.detail = "same content, non-canonical spelling (e.g. ~/.Codex); will rewrite"
            plan.copies = fixes
        return plan

    if baseline is None:
        if prefer:
            return _copy(plan, scope, prefer, Status.CONFLICT, f"no baseline; --prefer {prefer}")
        plan.status = Status.CONFLICT
        plan.detail = "copies differ and have never been synced; pick a side with --prefer"
        return plan
    if digest_claude == baseline:
        return _copy(plan, scope, CODEX, Status.CODEX_CHANGED, "codex copy changed; -> claude")
    if digest_codex == baseline:
        return _copy(plan, scope, CLAUDE, Status.CLAUDE_CHANGED, "claude copy changed; -> codex")
    if prefer:
        return _copy(plan, scope, prefer, Status.CONFLICT, f"both changed; --prefer {prefer}")
    plan.status = Status.CONFLICT
    plan.detail = "both copies changed since the last sync; pick a side with --prefer"
    return plan


def build_plans(
    scope: Scope, *, only: tuple[str, ...] = (), prefer: str | None = None
) -> list[SkillPlan]:
    """Classify every skill in ``scope`` (optionally limited to the names in ``only``)."""
    baselines = load_state(scope.state_path)
    names = _discover(scope, CLAUDE) | _discover(scope, CODEX)
    if only:
        names &= set(only)
    return [_classify(scope, name, baselines.get(name), prefer) for name in sorted(names)]


def apply_plans(scope: Scope, plans: list[SkillPlan], *, dry_run: bool) -> list[SkillChange]:
    """Perform the copies in ``plans`` and record baselines; nothing is written in dry-run."""
    state = load_state(scope.state_path)
    changes: list[SkillChange] = []
    dirty = False
    for plan in plans:
        actions: list[str] = []
        for source, dest in plan.copies:
            folder = scope.directory(dest) / plan.name
            log.debug("%s: %s -> %s", plan.name, source, dest)
            actions.extend(write_tree(folder, plan.trees[source], dest, dry_run=dry_run))
        if plan.new_hash is not None and state.get(plan.name) != plan.new_hash:
            state[plan.name] = plan.new_hash
            dirty = True
        if actions:
            changes.append(SkillChange(plan.name, tuple(actions)))
    if dirty and not dry_run:
        save_state(scope.state_path, state)
    return changes


def diff_lines(scope: Scope, name: str) -> list[str]:
    """Unified diff of the two copies' neutral text, for explaining a conflict."""
    claude, codex = _load(scope, CLAUDE, name), _load(scope, CODEX, name)
    if claude is None or codex is None:
        return []
    out: list[str] = []
    for rel in sorted(set(claude.files) | set(codex.files)):
        left, right = claude.files.get(rel), codex.files.get(rel)
        if left is not None and right is not None and left.content == right.content:
            continue
        a = left.content.decode(errors="replace").splitlines() if left and left.is_text else []
        b = right.content.decode(errors="replace").splitlines() if right and right.is_text else []
        out.extend(difflib.unified_diff(a, b, f"claude/{rel}", f"codex/{rel}", lineterm=""))
        if (left and not left.is_text) or (right and not right.is_text):
            out.append(f"(binary file differs: {rel})")
    return out
