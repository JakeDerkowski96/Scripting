# Usage

## Scopes

| Scope | Claude folder | Codex folder | Baselines |
|---|---|---|---|
| `project` | `<repo>/.claude/skills` | `<repo>/.agents/skills` | `<repo>/.skill-sync.json` (commit it) |
| `user` | `~/.claude/skills` | `~/.agents/skills` | `~/.skill-sync/state.json` (per machine) |

`--scope all` (the default) runs the user scope, plus the project scope when the current directory is inside a git repo. Use `--repo PATH` to point at a different repo.

In the user scope, `~/.agents/skills` is shared with other tools. A skill that exists only there and that skill-sync has never synced is shown as `foreign` (hidden unless `-v`) and is never copied or changed.

## Statuses

| Status | Meaning | What `sync` does |
|---|---|---|
| `in-sync` | Same content in neutral form | nothing |
| `drifted` | Same content, but one copy uses a legacy spelling such as `~/.Codex` | rewrites that copy canonically |
| `claude-changed` | Claude copy changed since the last sync | copies it to Codex |
| `codex-changed` | Codex copy changed since the last sync | copies it to Claude |
| `missing-codex` | No Codex copy yet | creates it |
| `missing-claude` | No Claude copy yet (project scope) | creates it |
| `conflict` | Both changed, they differ with no baseline, or the destination folder is not a skill | nothing, unless `--prefer` |
| `ambiguous` | The text cannot be converted safely (see [rules.md](rules.md)) | nothing |
| `foreign` | Owned by another tool | nothing |

## Workflows

**First run on a repo that already has both folders**

```powershell
python -m skill_sync status
python -m skill_sync diff <skill>        # for each conflict, see which side is newer
python -m skill_sync sync --prefer codex --only <skill>
python -m skill_sync sync                # everything else
```

**Day to day.** Edit a skill in either tool, then run `sync`. Add `python -m skill_sync check` to CI or a pre-commit hook to fail when the two folders drift.

**Dry run.** `sync --dry-run` prints every file it would write or remove, and writes nothing, including the baseline file.

## Deletions

Inside a managed skill, a file removed on the changed side is removed on the other side. Whole skill folders are never deleted.
