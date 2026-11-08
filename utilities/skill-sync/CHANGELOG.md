# Changelog

All notable changes to skill-sync are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0]

### Added

- `status`, `sync`, `check`, `diff` and `rules` commands.
- Neutral-form comparison of `.claude/skills` and `.agents/skills` with explicit substitution rules
  for the instructions file name and the config directory.
- Per-skill baselines so a change on one side is propagated and a change on both is a conflict.
- Project scope (a repo's own folders) and user scope (`~/.claude/skills`, `~/.agents/skills`), with
  skills owned by other tools in the shared folder left alone.
- Round-trip and ambiguity guards so text that cannot be converted safely is skipped.
