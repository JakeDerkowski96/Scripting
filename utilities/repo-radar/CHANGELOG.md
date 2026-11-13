# Changelog

All notable changes to this project are documented here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `obsidian` command: writes a per-repo note and a dashboard into an Obsidian vault, refreshing generated parts and preserving hand-written ones.
- `scan`, `list`, `show`, `report`, `init` and `check` commands; `python -m repo_radar` entry point.
- `check` enforces the repos-folder rules (git-only folders, expected visibility) and exits 3 on violations.
- Terminal table and self-contained HTML dashboard.
- Attention flags: dirty, unpushed, behind, no-remote, no-upstream, open-prs,
  ci-failing, stale, not-git, no-meta, bad-meta, git-error.
- `.project.toml` per-repo metadata (summary, stage, next, blockers, tags).
- Expected `visibility` in `.project.toml`, with `visibility-mismatch` and
  `visibility-unknown` flags, so a private repo going public is caught.
