"""Read local repository state by shelling out to git.

Required permissions: read access to the repository folder. With
`fetch=True` it also needs network access and read access to `origin`; that is
the only operation here that touches anything (it updates remote-tracking refs
and nothing else).
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from repo_radar.exceptions import GitError
from repo_radar.models import GitState

logger = logging.getLogger(__name__)

_TIMEOUT = 30
_FETCH_TIMEOUT = 60
# Never block a scan on a credential prompt.
_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def _git(path: Path, *args: str, timeout: int = _TIMEOUT) -> subprocess.CompletedProcess[str]:
    """Run `git -C path <args>` and return the completed process.

    Raises:
        GitError: git is missing or the command timed out. A non-zero exit is
            returned to the caller, because some failures (no commits yet, no
            remote) are expected states rather than errors.
    """
    cmd = ["git", "-C", str(path), *args]
    logger.debug("running: %s", " ".join(cmd))
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            env=_ENV,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitError(f"git {args[0]} timed out after {timeout}s in {path}") from exc


def parse_status(output: str) -> GitState:
    """Parse `git status --porcelain=v2 --branch` output.

    Args:
        output: Raw command output.

    Returns:
        A GitState with branch, upstream, ahead/behind and dirty count filled.
    """
    state = GitState(is_git=True)
    for line in output.splitlines():
        if line.startswith("# branch.head "):
            head = line.removeprefix("# branch.head ")
            state.branch = "(detached)" if head == "(detached)" else head
        elif line.startswith("# branch.upstream "):
            state.upstream = line.removeprefix("# branch.upstream ")
        elif line.startswith("# branch.ab "):
            plus, minus = line.removeprefix("# branch.ab ").split()
            state.ahead = int(plus.lstrip("+"))
            state.behind = int(minus.lstrip("-"))
        elif line and not line.startswith("#"):
            # Changed, renamed, unmerged and untracked entries all count.
            state.dirty += 1
    return state


def read_state(path: Path, *, fetch: bool = False) -> GitState:
    """Return the local git state of the repo at `path`.

    Args:
        path: Repository folder.
        fetch: Run `git fetch` first so ahead/behind reflects the real remote
            rather than the last fetch. Slower, and needs network access.

    Returns:
        A GitState. Failures are recorded in `error` instead of raised, so one
        broken repo does not abort a whole scan.
    """
    if not (path / ".git").exists():
        return GitState(is_git=False)

    try:
        if fetch:
            result = _git(path, "fetch", "--quiet", timeout=_FETCH_TIMEOUT)
            if result.returncode != 0:
                logger.warning("fetch failed in %s: %s", path.name, result.stderr.strip())

        status = _git(path, "status", "--porcelain=v2", "--branch")
        if status.returncode != 0:
            return GitState(is_git=True, error=status.stderr.strip() or "git status failed")
        state = parse_status(status.stdout)

        # Fails on a repo with no commits yet; that is a state, not an error.
        log = _git(path, "log", "-1", "--format=%cI%x1f%s")
        if log.returncode == 0 and log.stdout.strip():
            state.last_commit, _, state.last_subject = log.stdout.strip().partition("\x1f")

        remote = _git(path, "remote", "get-url", "origin")
        if remote.returncode == 0:
            state.remote_url = remote.stdout.strip()
    except GitError as exc:
        return GitState(is_git=True, error=str(exc))
    return state
