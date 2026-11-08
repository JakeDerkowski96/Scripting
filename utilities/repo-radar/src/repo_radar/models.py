"""Plain data containers shared by every other module.

Holds no logic beyond (de)serialisation, so the scanner, renderers and cache
can all depend on it without depending on each other.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, TypeVar

STAGES: tuple[str, ...] = (
    "idea",
    "prototype",
    "active",
    "maintenance",
    "paused",
    "archived",
    "done",
)

VISIBILITIES: tuple[str, ...] = ("public", "private", "internal")

T = TypeVar("T")


def _build(cls: type[T], data: dict[str, Any]) -> T:
    """Construct a dataclass from a dict, ignoring unknown keys.

    Ignoring unknown keys keeps an older cache file loadable after a field is
    added or removed.
    """
    names = {f.name for f in fields(cls)}  # type: ignore[arg-type]
    return cls(**{k: v for k, v in data.items() if k in names})


@dataclass
class ProjectMeta:
    """Human-supplied intent read from a repo's .project.toml."""

    present: bool = False
    summary: str = ""
    stage: str = ""
    visibility: str = ""  # expected GitHub visibility; "" means no expectation
    next_step: str = ""
    blockers: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class GitState:
    """Local repository state, derived from git at scan time."""

    is_git: bool = False
    branch: str = ""
    upstream: str = ""
    ahead: int = 0
    behind: int = 0
    dirty: int = 0
    last_commit: str = ""  # ISO 8601 committer date
    last_subject: str = ""
    remote_url: str = ""
    error: str = ""


@dataclass
class GitHubState:
    """Remote state, derived from the GitHub CLI at scan time."""

    slug: str = ""
    visibility: str = ""
    archived: bool = False
    default_branch: str = ""
    open_prs: int | None = None
    draft_prs: int = 0
    open_issues: int | None = None
    ci_status: str = ""  # success | failure | running | "" (no runs)
    error: str = ""


@dataclass
class Project:
    """Everything known about one folder under the scan root."""

    name: str
    path: str
    meta: ProjectMeta = field(default_factory=ProjectMeta)
    git: GitState = field(default_factory=GitState)
    github: GitHubState | None = None
    flags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        """Rebuild a Project (and its nested states) from `asdict` output."""
        github = data.get("github")
        return cls(
            name=data["name"],
            path=data["path"],
            meta=_build(ProjectMeta, data.get("meta", {})),
            git=_build(GitState, data.get("git", {})),
            github=_build(GitHubState, github) if github else None,
            flags=list(data.get("flags", [])),
        )


@dataclass
class ScanResult:
    """A complete scan: when, where, and what was found."""

    scanned_at: str
    root: str
    projects: list[Project]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScanResult:
        """Rebuild a ScanResult from `to_dict` output."""
        return cls(
            scanned_at=data["scanned_at"],
            root=data["root"],
            projects=[Project.from_dict(p) for p in data["projects"]],
        )

    @property
    def root_path(self) -> Path:
        """The scan root as a Path."""
        return Path(self.root)
