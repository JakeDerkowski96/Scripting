"""The sync baseline: the neutral hash each skill had when it was last in sync.

Without a baseline a difference between the two copies cannot be attributed to either side, so it
is reported as a conflict. Project state is committed with the repo; user state is per machine.

Required permissions: read/write access to the state file's directory.
"""

from __future__ import annotations

import json
from pathlib import Path

from skill_sync.exceptions import StateError

STATE_VERSION = 1


def load_state(path: Path) -> dict[str, str]:
    """Return ``{skill name: neutral hash}``; an absent file means no baselines yet."""
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        skills = raw["skills"]
        return {str(name): str(digest) for name, digest in skills.items()}
    except (OSError, ValueError, KeyError, AttributeError) as exc:
        msg = f"cannot read sync state {path}: {exc}"
        raise StateError(msg) from exc


def save_state(path: Path, skills: dict[str, str]) -> None:
    """Write the baselines, sorted so the file diffs cleanly in git."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": STATE_VERSION, "skills": dict(sorted(skills.items()))}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
