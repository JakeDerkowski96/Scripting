"""Exception hierarchy for repo-radar.

A single base class lets the CLI catch every expected failure without also
catching unrelated bugs.
"""


class RepoRadarError(Exception):
    """Base for all errors raised by this package."""


class ConfigurationError(RepoRadarError):
    """The scan root or another setting is missing or invalid."""


class GitError(RepoRadarError):
    """A git command failed or git is not available."""


class GitHubError(RepoRadarError):
    """A GitHub CLI call failed or `gh` is not available."""


class MetadataError(RepoRadarError):
    """A .project.toml file is unreadable or invalid."""


class CacheError(RepoRadarError):
    """The scan cache is missing or corrupt."""
