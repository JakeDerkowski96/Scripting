"""Walk the scan root and assemble a ScanResult.

Required permissions: read access to the scan root and the repos under it;
network and `gh` authentication only when GitHub lookups or fetch are enabled.
Nothing is written here.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from repo_radar import github
from repo_radar.attention import compute_flags
from repo_radar.exceptions import ConfigurationError
from repo_radar.gitinfo import read_state
from repo_radar.meta import load_meta
from repo_radar.models import GitHubState, Project, ScanResult

logger = logging.getLogger(__name__)

_MAX_WORKERS = 8


def discover(root: Path) -> list[Path]:
    """Return the project folders directly under `root`.

    Dot-folders (like `.claude`) are tooling, not projects, and are skipped.
    """
    if not root.is_dir():
        raise ConfigurationError(f"Scan root is not a directory: {root}")
    return sorted(
        (p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: p.name.lower(),
    )


def scan_one(path: Path, *, use_github: bool, fetch: bool, now: datetime) -> Project:
    """Collect all state for a single project folder."""
    logger.debug("scanning %s", path.name)
    meta = load_meta(path)
    git = read_state(path, fetch=fetch)

    remote: GitHubState | None = None
    if use_github and git.remote_url:
        slug = github.parse_slug(git.remote_url)
        if slug:
            remote = github.fetch_state(slug)
            if remote.error:
                logger.warning("%s: GitHub lookup problem: %s", path.name, remote.error)

    return Project(
        name=path.name,
        path=str(path),
        meta=meta,
        git=git,
        github=remote,
        flags=compute_flags(meta, git, remote, now=now),
    )


def scan(
    root: Path,
    *,
    use_github: bool = True,
    fetch: bool = False,
    only: Iterable[str] | None = None,
) -> ScanResult:
    """Scan every project under `root`.

    Args:
        root: Directory containing all repos.
        use_github: Query GitHub for PRs, issues and CI. Silently downgraded
            (with a warning) when `gh` is not installed.
        fetch: `git fetch` each repo first for accurate ahead/behind.
        only: Restrict the scan to these folder names.
    """
    if use_github and not github.gh_available():
        logger.warning("gh not found on PATH; skipping GitHub lookups")
        use_github = False

    paths = discover(root)
    if only is not None:
        wanted = {n.lower() for n in only}
        paths = [p for p in paths if p.name.lower() in wanted]

    now = datetime.now().astimezone()
    # Work is dominated by waiting on subprocesses, so threads are enough.
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
        projects = list(
            pool.map(
                lambda p: scan_one(p, use_github=use_github, fetch=fetch, now=now),
                paths,
            )
        )
    return ScanResult(
        scanned_at=now.isoformat(timespec="seconds"), root=str(root), projects=projects
    )
