"""Render projects as a fixed-width terminal table (stdlib only, optional ANSI colour)."""

from __future__ import annotations

import unicodedata
from datetime import datetime

from repo_radar.models import Project
from repo_radar.query import humanize_age, pr_summary, sync_summary

_RESET = "\x1b[0m"
_COLORS = {
    "red": "\x1b[31m",
    "yellow": "\x1b[33m",
    "green": "\x1b[32m",
    "cyan": "\x1b[36m",
    "dim": "\x1b[2m",
    "bold": "\x1b[1m",
}
_STAGE_COLOR = {
    "active": "green",
    "prototype": "cyan",
    "idea": "cyan",
    "maintenance": "dim",
    "paused": "yellow",
    "archived": "dim",
    "done": "dim",
}
_HEADERS = ("PROJECT", "STAGE", "BRANCH", "SYNC", "PRS", "LAST", "FLAGS")
_SUMMARY_WIDTH = 60


def _width(text: str) -> int:
    """Display width, counting wide (CJK/emoji) characters as 2 columns."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def _paint(text: str, color: str | None, *, enabled: bool) -> str:
    if not enabled or color is None:
        return text
    return f"{_COLORS[color]}{text}{_RESET}"


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render_table(
    projects: list[Project], *, now: datetime, color: bool = False, wide: bool = False
) -> str:
    """Return a table of `projects` as text.

    Args:
        projects: Rows to show, already filtered and sorted.
        now: Reference time for the "last commit" age column.
        color: Emit ANSI colour codes.
        wide: Add the summary and next-step lines under each row.
    """
    if not projects:
        return "No projects match."

    rows: list[list[tuple[str, str | None]]] = []
    for p in projects:
        sync = sync_summary(p)
        sync_color = "green" if sync == "✓" else "yellow"
        prs = pr_summary(p)
        rows.append(
            [
                (p.name, "bold"),
                (p.meta.stage or "unset", _STAGE_COLOR.get(p.meta.stage, "red")),
                (p.git.branch or "—", "dim"),
                (sync, sync_color),
                (prs, "yellow" if prs not in ("—", "0") else "dim"),
                (humanize_age(p.git.last_commit, now), "dim"),
                (" ".join(p.flags), "red" if p.flags else "green"),
            ]
        )
        if not p.flags:
            rows[-1][-1] = ("ok", "green")

    widths = [
        max(_width(_HEADERS[i]), *(_width(r[i][0]) for r in rows)) for i in range(len(_HEADERS))
    ]

    def line(cells: list[tuple[str, str | None]]) -> str:
        padded = [
            _paint(text, c, enabled=color) + " " * (widths[i] - _width(text))
            for i, (text, c) in enumerate(cells)
        ]
        return "  ".join(padded).rstrip()

    out = [line([(h, "dim") for h in _HEADERS])]
    for p, row in zip(projects, rows, strict=True):
        out.append(line(row))
        if wide:
            if p.meta.summary:
                out.append(
                    "    " + _paint(_truncate(p.meta.summary, _SUMMARY_WIDTH), "dim", enabled=color)
                )
            if p.meta.next_step:
                out.append("    next: " + _truncate(p.meta.next_step, _SUMMARY_WIDTH))

    flagged = sum(1 for p in projects if p.flags)
    out.append("")
    out.append(f"{len(projects)} projects · {flagged} need attention")
    return "\n".join(out)


def render_detail(project: Project, *, now: datetime) -> str:
    """Return a multi-line detail view of one project."""
    meta, git, gh = project.meta, project.git, project.github
    lines = [
        project.name,
        f"  path      {project.path}",
        f"  summary   {meta.summary or '(none)'}",
        f"  stage     {meta.stage or 'unset'}",
        f"  expects   {meta.visibility or '(no visibility expectation)'}",
        f"  next      {meta.next_step or '(none)'}",
        f"  blockers  {', '.join(meta.blockers) or '(none)'}",
        f"  tags      {', '.join(meta.tags) or '(none)'}",
    ]
    if meta.error:
        lines.append(f"  meta err  {meta.error}")
    if git.is_git:
        lines += [
            f"  branch    {git.branch or '—'}  (upstream: {git.upstream or 'none'})",
            f"  sync      ahead {git.ahead} · behind {git.behind} · changed files {git.dirty}",
            f"  last      {humanize_age(git.last_commit, now)} — {git.last_subject or '—'}",
            f"  remote    {git.remote_url or '(none)'}",
        ]
        if git.error:
            lines.append(f"  git err   {git.error}")
    else:
        lines.append("  git       not a git repository")
    if gh is not None:
        lines += [
            f"  github    {gh.slug} ({gh.visibility or '?'}{', archived' if gh.archived else ''})",
            f"  prs       {gh.open_prs if gh.open_prs is not None else '?'} open"
            f" ({gh.draft_prs} draft) · issues {gh.open_issues if gh.open_issues is not None else '?'}",
            f"  ci        {gh.ci_status or 'no runs'} on {gh.default_branch or '?'}",
        ]
        if gh.error:
            lines.append(f"  gh err    {gh.error}")
    lines.append(f"  flags     {' '.join(project.flags) or 'none'}")
    return "\n".join(lines)
