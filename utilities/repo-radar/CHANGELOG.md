# Changelog

All notable changes to this project are documented here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `scan`, `list`, `show`, `report` and `init` commands.
- Terminal table and self-contained HTML dashboard.
- Attention flags: dirty, unpushed, behind, no-remote, no-upstream, open-prs,
  ci-failing, stale, not-git, no-meta, bad-meta, git-error.
- `.project.toml` per-repo metadata (summary, stage, next, blockers, tags).
- Expected `visibility` in `.project.toml`, with `visibility-mismatch` and
  `visibility-unknown` flags, so a private repo going public is caught.
