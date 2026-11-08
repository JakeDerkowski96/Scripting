"""Read a skill folder into its neutral form and write a neutral form back out for one agent.

Text files go through the transform rules; everything else is copied byte for byte. Line endings
are ignored when comparing and preserved when writing, so CRLF checkouts do not look like edits.

Required permissions: read access to the source skill folder; write access to the destination
skill folder (only when ``dry_run`` is false).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

from skill_sync.rules import Normalized, normalize, render

log = logging.getLogger(__name__)

SKILL_FILE = "SKILL.md"

TEXT_SUFFIXES = frozenset(
    {
        ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".ps1", ".sh", ".js", ".cjs",
        ".mjs", ".ts", ".html", ".css", ".csv", ".kql", ".xml",
    }
)  # fmt: skip
# Files that exist for one agent only. Mirroring them would delete or clobber the other side's copy.
TARGET_ONLY_FILES = frozenset({"agents/openai.yaml"})
IGNORED_DIRS = frozenset({"__pycache__", ".git", "node_modules"})


@dataclass(frozen=True)
class NeutralFile:
    """One file in neutral form: neutral text (UTF-8, LF) or raw bytes."""

    content: bytes
    is_text: bool
    newline: str = "\n"
    drifted: bool = False  # literal text differs from its own canonical rendering (alias spelling)


@dataclass
class NeutralTree:
    """A whole skill folder in neutral form."""

    files: dict[str, NeutralFile] = field(default_factory=dict)
    ambiguous: dict[str, tuple[str, ...]] = field(default_factory=dict)

    @property
    def drifted(self) -> bool:
        """True when any file uses a non-canonical spelling that a rewrite would fix."""
        return any(item.drifted for item in self.files.values())

    def digest(self) -> str:
        """Content hash over paths, kinds and neutral content (line endings excluded)."""
        hasher = hashlib.sha256()
        for rel in sorted(self.files):
            item = self.files[rel]
            hasher.update(rel.encode())
            hasher.update(b"\0t" if item.is_text else b"\0b")
            hasher.update(len(item.content).to_bytes(8, "big"))
            hasher.update(item.content)
        return hasher.hexdigest()


def _relative_files(root: Path) -> list[str]:
    """Posix-style relative paths of every syncable file under ``root``."""
    found: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel_path.parts):
            continue
        rel = rel_path.as_posix()
        if rel not in TARGET_ONLY_FILES:
            found.append(rel)
    return found


def _decode(path: Path, data: bytes) -> str | None:
    """Return the text of a file, or None when it should be treated as binary."""
    if path.suffix.lower() not in TEXT_SUFFIXES or b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def read_tree(root: Path, target: str) -> NeutralTree:
    """Read ``root`` (a skill folder written for ``target``) into neutral form."""
    tree = NeutralTree()
    for rel in _relative_files(root):
        path = root / rel
        data = path.read_bytes()
        text = _decode(path, data)
        if text is None:
            tree.files[rel] = NeutralFile(data, is_text=False)
            continue
        newline = "\r\n" if "\r\n" in text else "\n"
        lf_text = text.replace("\r\n", "\n")
        result: Normalized = normalize(lf_text, target)
        if result.ambiguous:
            tree.ambiguous[rel] = result.ambiguous
        drifted = not result.ambiguous and render(result.text, target) != lf_text
        tree.files[rel] = NeutralFile(result.text.encode(), True, newline, drifted)
    return tree


def write_tree(dest: Path, tree: NeutralTree, target: str, *, dry_run: bool) -> list[str]:
    """Render ``tree`` for ``target`` into ``dest``, returning the actions taken (or planned).

    Files that exist in ``dest`` but not in ``tree`` are removed so deletions propagate. Only
    called for one-sided changes, so the destination holds nothing newer than the source.
    """
    actions: list[str] = []
    existing = set(_relative_files(dest)) if dest.is_dir() else set()
    for rel, item in tree.files.items():
        if item.is_text:
            text = render(item.content.decode(), target)
            data = text.replace("\n", item.newline).encode()
        else:
            data = item.content
        path = dest / rel
        if path.is_file() and path.read_bytes() == data:
            continue
        actions.append(f"write {rel}")
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    for rel in sorted(existing - set(tree.files)):
        actions.append(f"remove {rel}")
        if not dry_run:
            (dest / rel).unlink()
    if not dry_run:
        _prune_empty_dirs(dest)
    return actions


def roundtrip_problems(tree: NeutralTree, target: str) -> list[str]:
    """Files whose rendering for ``target`` would not normalise back to the same neutral text.

    That happens when a neutral text holds a literal that is one of ``target``'s own tokens (for
    example a Claude skill that mentions ``~/.codex``): writing it out would make the next sync see
    a "change" on the destination side and push it back, corrupting the source.
    """
    problems: list[str] = []
    for rel, item in tree.files.items():
        if not item.is_text:
            continue
        neutral = item.content.decode()
        back = normalize(render(neutral, target), target)
        if back.ambiguous or back.text != neutral:
            problems.append(rel)
    return problems


def _prune_empty_dirs(root: Path) -> None:
    """Remove directories left empty by deleted files, deepest first."""
    if not root.is_dir():
        return
    for path in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
        if not any(path.iterdir()):
            log.debug("removing empty directory %s", path)
            path.rmdir()
