"""Where skills live for each scope, and where the sync state is kept.

Two scopes exist. ``project`` is a repo's own ``.claude/skills`` and ``.agents/skills``. ``user``
is ``~/.claude/skills`` and ``~/.agents/skills``; the latter is shared with other skill managers,
so skills found only there are treated as foreign instead of being copied.

Required permissions: read access to the directories it inspects (for repo discovery).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skill_sync.exceptions import ScopeError
from skill_sync.rules import CLAUDE


@dataclass(frozen=True)
class Scope:
    """One place where both agents' skill folders live."""

    name: str
    claude_dir: Path
    codex_dir: Path
    state_path: Path
    # In a repo every skill is ours; in the user scope, skills only in the Codex folder may belong
    # to another manager (Azure, Copilot, ...) and must not be copied into Claude's folder.
    adopt_codex_only: bool

    def directory(self, target: str) -> Path:
        """Skills folder for ``target``."""
        return self.claude_dir if target == CLAUDE else self.codex_dir


def project_scope(repo: Path) -> Scope:
    """Scope for a single repository."""
    return Scope(
        name="project",
        claude_dir=repo / ".claude" / "skills",
        codex_dir=repo / ".agents" / "skills",
        state_path=repo / ".skill-sync.json",
        adopt_codex_only=True,
    )


def user_scope(home: Path) -> Scope:
    """Scope for the user-level skill folders."""
    return Scope(
        name="user",
        claude_dir=home / ".claude" / "skills",
        codex_dir=home / ".agents" / "skills",
        state_path=home / ".skill-sync" / "state.json",
        adopt_codex_only=False,
    )


def find_repo_root(start: Path) -> Path | None:
    """Nearest ancestor of ``start`` (inclusive) that contains a ``.git`` entry."""
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def resolve_scopes(choice: str, repo: Path | None, home: Path) -> list[Scope]:
    """Scopes selected by ``--scope``; ``all`` includes the project scope only inside a repo."""
    scopes: list[Scope] = []
    if choice in ("project", "all"):
        root = repo if repo is not None else find_repo_root(Path.cwd())
        if root is not None:
            scopes.append(project_scope(root))
        elif choice == "project":
            msg = "--scope project needs a git repository; run inside one or pass --repo"
            raise ScopeError(msg)
    if choice in ("user", "all"):
        scopes.append(user_scope(home))
    return scopes
