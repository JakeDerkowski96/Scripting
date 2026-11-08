"""Package-specific exceptions for skill-sync.

Required permissions: none (pure definitions).
"""

from __future__ import annotations


class SkillSyncError(Exception):
    """Base class for every error skill-sync raises on purpose."""


class ScopeError(SkillSyncError):
    """A scope (project or user) could not be resolved, e.g. no git repo for --scope project."""


class StateError(SkillSyncError):
    """The sync state file exists but cannot be read."""
