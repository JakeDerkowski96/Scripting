"""Decide which "needs attention" flags apply to a project.

Pure logic over already-collected state: no I/O, so it is trivial to test.
"""

from __future__ import annotations

from datetime import datetime

from repo_radar.models import GitHubState, GitState, ProjectMeta

STALE_DAYS = 60
# Stages where silence is expected, so "stale" would just be noise.
QUIET_STAGES = frozenset({"maintenance", "paused", "archived", "done"})

# Flags that break a rule of the repos folder (as opposed to merely suggesting
# work), so `repo-radar check` can fail on them.
RULE_FLAGS: tuple[str, ...] = ("not-git", "visibility-mismatch", "visibility-unknown")

FLAGS: dict[str, str] = {
    "not-git": "Not a git repository; only git repos may live in the repos folder",
    "git-error": "git could not read this repository",
    "no-meta": "No .project.toml, or it has no stage set",
    "bad-meta": ".project.toml is invalid",
    "dirty": "Uncommitted or untracked changes",
    "unpushed": "Local commits not yet on the remote",
    "behind": "Remote has commits not pulled locally",
    "no-remote": "No origin remote configured",
    "no-upstream": "Current branch does not track a remote branch",
    "visibility-mismatch": "GitHub visibility differs from the visibility in .project.toml",
    "visibility-unknown": "Expected visibility is set but could not be verified (gh missing or failed)",
    "open-prs": "Open pull requests",
    "ci-failing": "Latest CI run on the default branch failed",
    "stale": f"No commits in over {STALE_DAYS} days",
}


def compute_flags(
    meta: ProjectMeta,
    git: GitState,
    github: GitHubState | None,
    *,
    now: datetime,
) -> list[str]:
    """Return the attention flags that apply, in display order.

    Args:
        meta: Human-supplied metadata.
        git: Local git state.
        github: Remote state, or None when the repo has no GitHub remote or
            GitHub lookups were skipped.
        now: Reference time for the staleness check (injected for testing).
    """
    flags: list[str] = []

    if meta.error:
        flags.append("bad-meta")
    elif not meta.present or not meta.stage:
        flags.append("no-meta")

    if not git.is_git:
        flags.insert(0, "not-git")
        return flags
    if git.error:
        flags.insert(0, "git-error")
        return flags

    if git.dirty:
        flags.append("dirty")
    if git.ahead:
        flags.append("unpushed")
    if git.behind:
        flags.append("behind")

    if not git.remote_url:
        flags.append("no-remote")
    elif not git.upstream and git.branch != "(detached)":
        flags.append("no-upstream")

    if meta.visibility and git.remote_url:
        actual = github.visibility if github is not None else ""
        if not actual:
            # An unverifiable guard must not look like a passing one.
            flags.append("visibility-unknown")
        elif actual != meta.visibility:
            flags.append("visibility-mismatch")

    if github is not None:
        if github.open_prs:
            flags.append("open-prs")
        if github.ci_status == "failure":
            flags.append("ci-failing")

    if git.last_commit and meta.stage not in QUIET_STAGES:
        age = now - datetime.fromisoformat(git.last_commit)
        if age.days > STALE_DAYS:
            flags.append("stale")

    return flags
