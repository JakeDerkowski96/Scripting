"""Filtering, sorting and display formatting shared by the table and HTML views."""

from __future__ import annotations

from datetime import datetime

from repo_radar.models import STAGES, Project

SORT_KEYS = ("name", "stage", "activity", "attention")


def filter_projects(
    projects: list[Project],
    *,
    stage: str | None = None,
    attention: bool = False,
    text: str | None = None,
) -> list[Project]:
    """Return the projects matching every given criterion.

    Args:
        projects: Projects to filter.
        stage: Keep only this stage; the value "unset" matches projects with none.
        attention: Keep only projects with at least one flag.
        text: Case-insensitive match against name, summary and tags.
    """
    result = projects
    if stage:
        wanted = "" if stage == "unset" else stage
        result = [p for p in result if p.meta.stage == wanted]
    if attention:
        result = [p for p in result if p.flags]
    if text:
        needle = text.lower()
        result = [
            p for p in result if needle in " ".join([p.name, p.meta.summary, *p.meta.tags]).lower()
        ]
    return result


def sort_projects(projects: list[Project], key: str) -> list[Project]:
    """Return `projects` ordered by `key` (one of SORT_KEYS)."""
    if key == "stage":
        order = {s: i for i, s in enumerate(STAGES)}
        return sorted(
            projects, key=lambda p: (order.get(p.meta.stage, len(STAGES)), p.name.lower())
        )
    if key == "activity":
        # ISO 8601 strings with the same offset sort chronologically; newest first.
        return sorted(projects, key=lambda p: p.git.last_commit, reverse=True)
    if key == "attention":
        return sorted(projects, key=lambda p: (-len(p.flags), p.name.lower()))
    return sorted(projects, key=lambda p: p.name.lower())


def humanize_age(iso: str, now: datetime) -> str:
    """Return a compact age like `3d`, `5mo` or `2y`; "—" when unknown."""
    if not iso:
        return "—"
    days = (now - datetime.fromisoformat(iso)).days
    if days < 1:
        return "today"
    if days < 31:
        return f"{days}d"
    if days < 365:
        return f"{days // 30}mo"
    return f"{days // 365}y"


def sync_summary(project: Project) -> str:
    """Describe local/remote sync in a few characters.

    `↑n` unpushed commits, `↓n` unpulled commits, `*n` changed files.
    """
    git = project.git
    if not git.is_git:
        return "—"
    if git.error:
        return "error"
    parts: list[str] = []
    if git.ahead:
        parts.append(f"↑{git.ahead}")
    if git.behind:
        parts.append(f"↓{git.behind}")
    if git.dirty:
        parts.append(f"*{git.dirty}")
    if not git.remote_url:
        parts.append("local-only")
    return " ".join(parts) if parts else "✓"


def pr_summary(project: Project) -> str:
    """Return the open PR count as text, `—` when not known."""
    gh = project.github
    if gh is None or gh.open_prs is None:
        return "—"
    return str(gh.open_prs)
