# Troubleshooting

## `conflict`: copies differ and have never been synced

There is no baseline, so skill-sync cannot tell which copy is newer. Look at the difference, then choose:

```powershell
python -m skill_sync diff <skill>
python -m skill_sync sync --only <skill> --prefer claude   # or codex
```

`--prefer` makes that side win for the named skill only, and records the baseline so later runs can tell the sides apart.

## `conflict`: both copies changed since the last sync

Same fix: `diff`, then `--prefer`. The losing side's changes are overwritten, so copy anything you want to keep first.

## `conflict`: folder exists but has no SKILL.md

The destination folder already holds files that are not a skill. skill-sync will not write into it. Move or rename that folder, or add a `SKILL.md`.

## `ambiguous`

See [rules.md](rules.md#why-a-skill-is-ambiguous). Reword the skill so it does not mention both tools' files or config folders.

## A skill I did not expect is missing from the list

- In the user scope, skills that exist only in `~/.agents/skills` are `foreign` and hidden. Run `status -v` to list them.
- A folder without `SKILL.md`, or whose name starts with `.`, is not a skill.

## `error: --scope project needs a git repository`

Run from inside a repo, or pass `--repo PATH`.

## `error: cannot read sync state`

The baseline file is not valid JSON. Delete it; the next run treats every differing skill as a conflict and asks for `--prefer`.

## A change was written to the wrong side

Run `git diff` in the repo (project scope) to see and revert it. User-scope skills in `~/.claude/skills` usually live in a git repo too. Use `sync --dry-run` first when unsure.
