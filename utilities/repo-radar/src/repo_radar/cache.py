"""Persist the last scan as JSON so `list`, `show` and `report` are instant.

Required permissions: read/write access to the cache file's directory.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from repo_radar.exceptions import CacheError
from repo_radar.models import ScanResult

logger = logging.getLogger(__name__)


def save(result: ScanResult, path: Path) -> None:
    """Write `result` to `path`, creating parent folders as needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    except OSError as exc:
        raise CacheError(f"Could not write cache {path}: {exc}") from exc
    logger.debug("cache written to %s", path)


def load(path: Path) -> ScanResult:
    """Read a previously saved scan.

    Raises:
        CacheError: The file is missing, unreadable, or not a valid scan.
    """
    if not path.is_file():
        raise CacheError(f"No cached scan at {path}. Run `repo-radar scan` first.")
    try:
        return ScanResult.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise CacheError(f"Cache {path} is unreadable ({exc}). Re-run `repo-radar scan`.") from exc
