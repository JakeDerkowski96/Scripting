# skill-sync

Keeps agent skills available in both Claude Code (`.claude/skills`) and Codex (`.agents/skills`), so you can edit a skill in either tool and the other copy follows.

## Purpose

Claude Code and Codex read skills from different folders, and a few words inside a skill differ between them (`CLAUDE.md` vs `AGENTS.md`, `~/.claude` vs `~/.codex`). Keeping two copies by hand drifts. skill-sync compares both copies in a tool-neutral form, works out which side changed since the last sync, and copies that change across, converting the tool-specific words. If both sides changed, it stops and tells you instead of overwriting either.

## Prerequisites

- Python 3.11 or newer (standard library only; no runtime dependencies)
- Skill folders laid out as `<name>/SKILL.md`

## Install

```powershell
python -m pip install --user -e .\utilities\skill-sync
```

Then run it as `python -m skill_sync ...` (or `skill-sync ...` if your Python Scripts folder is on PATH).

## Required permissions

| Resource | Access | Why |
|---|---|---|
| `~/.claude/skills`, `~/.agents/skills` | read, write | user-level skill folders (user scope) |
| `<repo>/.claude/skills`, `<repo>/.agents/skills` | read, write | project skill folders (project scope) |
| `<repo>/.skill-sync.json`, `~/.skill-sync/state.json` | read, write | last-synced baselines |

No network access, no GitHub access, no elevation. `status`, `check`, `diff` and `rules` only read; `sync --dry-run` reads and reports without writing.

## Usage

```powershell
python -m skill_sync status                   # what is in sync and what is not
python -m skill_sync sync --dry-run           # show what would change
python -m skill_sync sync                     # copy one-sided changes across
python -m skill_sync sync --prefer claude     # resolve conflicts in Claude's favour
python -m skill_sync check                    # exit 3 if anything is out of sync (CI, hooks)
python -m skill_sync diff portfolio           # explain a conflict
python -m skill_sync rules                    # the word substitutions it applies
```

Common flags: `--scope project|user|all` (default `all`), `--repo PATH`, `--only NAME` (repeatable), `-v`.

Exit codes: 0 ok, 1 error, 2 usage, 3 out of sync or needs attention.

## Safety

- It never deletes or overwrites a skill it does not manage. In the user scope, skills that exist only in `~/.agents/skills` belong to other tools (Azure, Copilot) and are left alone.
- A conflict, or text it cannot convert safely (`ambiguous`), is reported and skipped, never guessed.
- Skills that use `$ARGUMENTS` get a note: only Claude Code substitutes it.

## Documentation

See [docs/README.md](docs/README.md): [usage](docs/usage.md), [how the conversion works](docs/rules.md), [troubleshooting](docs/troubleshooting.md).
