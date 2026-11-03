# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Scan root not found` | No `--root`, `$REPO_RADAR_ROOT`, OneDrive `github-repos` folder or `~/github-repos` | Pass `--root PATH` or set `REPO_RADAR_ROOT` |
| `No cached scan` | `list`/`show`/`report` before any scan | Run `repo-radar scan` |
| `gh not found on PATH; skipping GitHub lookups` | GitHub CLI not installed | Install `gh`, or pass `--no-github` to silence it |
| PR/issue/CI columns show `—` | Repo has no GitHub remote, or the `gh` lookup failed | `repo-radar show NAME` prints the `gh err` line; check `gh auth status` |
| `↓` never appears | Remote-tracking refs are stale | Use `--fetch` |
| `git-error` flag | git could not read the repo (corrupt, or OneDrive sync lock) | `repo-radar show NAME` for the message; run `git status` in the repo |
| Glyphs show as `?` | Terminal font or encoding | Use a UTF-8 terminal (Windows Terminal); output is forced to UTF-8 |
| `bad-meta` flag | Invalid TOML or an unknown stage | `repo-radar show NAME` for the message |
