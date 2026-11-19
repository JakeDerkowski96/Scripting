"""Locations: scan root, cache file and report file.

Resolution order for the scan root: --root, then $REPO_RADAR_ROOT, then
`github-repos` under each OneDrive folder, then `~/OneDrive/github-repos`, then
`~/github-repos`. Nothing here performs
work; it only decides where things live.
"""

from __future__ import annotations

import os
from pathlib import Path

from repo_radar.exceptions import ConfigurationError

ENV_ROOT = "REPO_RADAR_ROOT"
ENV_CACHE = "REPO_RADAR_CACHE"
ENV_VAULT = "REPO_RADAR_VAULT"
_STATE_DIR_NAME = ".repo-radar"


def _candidate_roots() -> list[Path]:
    candidates: list[Path] = []
    # %OneDrive% can point at a business account while the repos sit in the
    # personal one, so every OneDrive variable is tried, then the plain folders.
    for var in ("OneDriveConsumer", "OneDrive", "OneDriveCommercial"):
        value = os.environ.get(var)  # noqa: SIM112 - Windows defines these with this casing
        if value:
            candidates.append(Path(value) / "github-repos")
    candidates.append(Path.home() / "OneDrive" / "github-repos")
    candidates.append(Path.home() / "github-repos")
    return candidates


def resolve_root(explicit: Path | None = None) -> Path:
    """Return the directory containing all repos.

    Args:
        explicit: Value of --root, if given.

    Raises:
        ConfigurationError: No usable directory was found.
    """
    if explicit is not None:
        sources = [explicit]
    else:
        env = os.environ.get(ENV_ROOT)
        sources = [Path(env)] if env else _candidate_roots()

    for path in sources:
        if path.is_dir():
            return path.resolve()

    tried = ", ".join(str(p) for p in sources)
    raise ConfigurationError(
        f"Scan root not found (tried: {tried}). Pass --root or set {ENV_ROOT}."
    )


def state_dir() -> Path:
    """Directory for the cache and generated report (not created here)."""
    return Path.home() / _STATE_DIR_NAME


def default_cache_path() -> Path:
    """Where the last scan is stored."""
    env = os.environ.get(ENV_CACHE)
    return Path(env) if env else state_dir() / "scan.json"


def default_report_path() -> Path:
    """Where the HTML report is written."""
    return state_dir() / "report.html"


def resolve_vault(explicit: Path | None = None) -> Path:
    """Return the Obsidian vault folder to export into.

    Args:
        explicit: Value of --vault, if given; otherwise $REPO_RADAR_VAULT is used.

    Raises:
        ConfigurationError: Neither was provided.
    """
    env = os.environ.get(ENV_VAULT)
    chosen = explicit or (Path(env) if env else None)
    if chosen is None:
        raise ConfigurationError(f"No vault given. Pass --vault or set {ENV_VAULT}.")
    return chosen
