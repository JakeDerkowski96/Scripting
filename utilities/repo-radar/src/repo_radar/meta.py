"""Read and draft `.project.toml`, the per-repo file holding human intent.

Git can say *where* a repo stands but not *what it is for* or *what comes
next*; those live in this small file inside each repo so they are versioned
with it. TOML is used because the standard library can read it.

Required permissions: read access to the repo folder; write access only when
drafting a new file via `write_template`.
"""

from __future__ import annotations

import json
import logging
import tomllib
from pathlib import Path
from typing import Any

from repo_radar.exceptions import MetadataError
from repo_radar.models import STAGES, VISIBILITIES, ProjectMeta

logger = logging.getLogger(__name__)

META_FILENAME = ".project.toml"
_SUMMARY_MAX = 140


def _str_list(value: Any, key: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise MetadataError(f"'{key}' must be a list of strings")
    return list(value)


def parse_meta(text: str) -> ProjectMeta:
    """Parse the contents of a .project.toml.

    Raises:
        MetadataError: The TOML is invalid, a field has the wrong type, or the
            stage is not one of STAGES.
    """
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise MetadataError(f"invalid TOML: {exc}") from exc

    meta = ProjectMeta(present=True)
    for key in ("summary", "stage", "visibility", "next"):
        value = data.get(key, "")
        if not isinstance(value, str):
            raise MetadataError(f"'{key}' must be a string")
        if key == "next":
            meta.next_step = value
        else:
            setattr(meta, key, value)

    if meta.stage and meta.stage not in STAGES:
        raise MetadataError(f"unknown stage '{meta.stage}' (expected one of: {', '.join(STAGES)})")

    if meta.visibility and meta.visibility not in VISIBILITIES:
        raise MetadataError(
            f"unknown visibility '{meta.visibility}' (expected one of: {', '.join(VISIBILITIES)})"
        )

    meta.blockers = _str_list(data.get("blockers", []), "blockers")
    meta.tags = _str_list(data.get("tags", []), "tags")
    return meta


def load_meta(repo: Path) -> ProjectMeta:
    """Load `<repo>/.project.toml`.

    Returns:
        ProjectMeta with `present=False` if the file does not exist, or with
        `error` set if it exists but is invalid. Problems are surfaced as a
        flag rather than aborting the scan.
    """
    path = repo / META_FILENAME
    if not path.is_file():
        return ProjectMeta()
    try:
        return parse_meta(path.read_text(encoding="utf-8"))
    except (MetadataError, OSError, UnicodeDecodeError) as exc:
        logger.warning("%s: %s", path, exc)
        return ProjectMeta(present=True, error=str(exc))


def draft_summary(repo: Path) -> str:
    """Guess a one-line summary from the repo's README.

    Takes the first prose line that is not a heading, badge, image, HTML or
    list marker. Returns "" when there is no README or nothing usable; the
    result is only a starting point for the user to edit.
    """
    for name in ("README.md", "readme.md", "README.rst", "README.txt", "README"):
        readme = repo / name
        if not readme.is_file():
            continue
        try:
            lines = readme.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return ""
        for raw in lines:
            line = raw.strip()
            if not line or line.startswith(("#", "![", "[![", "<", "-", "*", "=", "`", ">", "|")):
                continue
            return line if len(line) <= _SUMMARY_MAX else line[: _SUMMARY_MAX - 1].rstrip() + "…"
        return ""
    return ""


def render_template(summary: str) -> str:
    """Return the text of a starter .project.toml.

    `stage` is left commented out on purpose: guessing it would put wrong
    data in the dashboard, so the repo keeps its `no-meta` flag until a human
    picks a stage.
    """
    return (
        "# repo-radar project metadata. Edit, then run `repo-radar scan`.\n"
        f"summary = {json.dumps(summary, ensure_ascii=False)}\n"
        f'# stage = "active"   # one of: {" | ".join(STAGES)}\n'
        f'# visibility = "private"   # expected on GitHub; flagged if it differs. {" | ".join(VISIBILITIES)}\n'
        'next = ""\n'
        "blockers = []\n"
        "tags = []\n"
    )


def write_template(repo: Path, summary: str, *, force: bool = False, dry_run: bool = False) -> bool:
    """Create `<repo>/.project.toml` from the starter template.

    Args:
        repo: Repository folder.
        summary: Drafted summary text.
        force: Overwrite an existing file.
        dry_run: Report what would happen without writing.

    Returns:
        True if a file was (or, in dry-run, would be) written; False if one
        already exists and `force` is not set.
    """
    path = repo / META_FILENAME
    if path.exists() and not force:
        return False
    if dry_run:
        logger.info("[dry-run] would write %s", path)
        return True
    path.write_text(render_template(summary), encoding="utf-8")
    logger.info("wrote %s", path)
    return True
