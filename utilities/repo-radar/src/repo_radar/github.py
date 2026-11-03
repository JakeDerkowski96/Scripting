"""Read remote repository state through the GitHub CLI (`gh`).

Required permissions: `gh auth login` as an account that can read the
repositories. Only read operations are used (`repo view`, `pr list`,
`issue list`, `run list`), so a token with the `repo` read scope is enough;
nothing is created or modified.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
from typing import Any

from repo_radar.exceptions import GitHubError
from repo_radar.models import GitHubState

logger = logging.getLogger(__name__)

_TIMEOUT = 30
_SLUG = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$")


def gh_available() -> bool:
    """Return True if the `gh` executable is on PATH."""
    return shutil.which("gh") is not None


def parse_slug(remote_url: str) -> str | None:
    """Extract `owner/repo` from a GitHub remote URL, or None if not GitHub."""
    match = _SLUG.search(remote_url.strip())
    return f"{match['owner']}/{match['repo']}" if match else None


def _gh(*args: str) -> Any:
    """Run `gh <args>` and return the parsed JSON output.

    Raises:
        GitHubError: gh is missing, timed out, exited non-zero, or returned
            something that is not JSON.
    """
    cmd = ["gh", *args]
    logger.debug("running: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_TIMEOUT,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitHubError("gh executable not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitHubError(f"gh {args[0]} {args[1]} timed out after {_TIMEOUT}s") from exc

    if result.returncode != 0:
        raise GitHubError(result.stderr.strip() or f"gh {args[0]} {args[1]} failed")
    try:
        return json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise GitHubError(f"gh {args[0]} {args[1]} returned invalid JSON") from exc


def fetch_state(slug: str) -> GitHubState:
    """Collect remote state for `owner/repo`.

    Args:
        slug: Repository in `owner/repo` form.

    Returns:
        A GitHubState. The repo lookup is required; the PR, issue and CI
        lookups are best-effort (issues may be disabled, a repo may have no
        workflow runs), and their failures are collected into `error` rather
        than raised.
    """
    state = GitHubState(slug=slug)
    try:
        repo = _gh("repo", "view", slug, "--json", "visibility,isArchived,defaultBranchRef")
    except GitHubError as exc:
        state.error = str(exc)
        return state

    state.visibility = str(repo.get("visibility", "")).lower()
    state.archived = bool(repo.get("isArchived", False))
    branch_ref = repo.get("defaultBranchRef") or {}
    state.default_branch = branch_ref.get("name", "")

    notes: list[str] = []
    try:
        prs = _gh(
            "pr",
            "list",
            "-R",
            slug,
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,isDraft",
        )
        state.open_prs = len(prs)
        state.draft_prs = sum(1 for pr in prs if pr.get("isDraft"))
    except GitHubError as exc:
        notes.append(f"prs: {exc}")

    try:
        issues = _gh(
            "issue", "list", "-R", slug, "--state", "open", "--limit", "100", "--json", "number"
        )
        state.open_issues = len(issues)
    except GitHubError as exc:
        notes.append(f"issues: {exc}")

    if state.default_branch:
        try:
            runs = _gh(
                "run",
                "list",
                "-R",
                slug,
                "--branch",
                state.default_branch,
                "--limit",
                "1",
                "--json",
                "status,conclusion",
            )
            if runs:
                run = runs[0]
                if run.get("status") != "completed":
                    state.ci_status = "running"
                else:
                    state.ci_status = str(run.get("conclusion") or "")
        except GitHubError as exc:
            notes.append(f"ci: {exc}")

    state.error = "; ".join(notes)
    return state
