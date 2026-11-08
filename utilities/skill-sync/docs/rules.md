# How the conversion works

Both copies of a skill are read into a **neutral form**: tool-specific words are replaced by placeholders. Two copies are in sync when their neutral forms are equal. Writing a copy renders the placeholders back into that tool's words.

## Rules

Run `python -m skill_sync rules` to print the live table.

| Placeholder | Claude | Codex | Accepted legacy spelling |
|---|---|---|---|
| `{{instructions_file}}` | `CLAUDE.md` | `AGENTS.md` | none |
| `{{config_dir}}` | `~/.claude` | `~/.codex` | `~/.Codex` (rewritten to `~/.codex`) |

`~/.Codex` only works on case-insensitive file systems such as Windows; it breaks on Linux and WSL, so it is always rewritten.

Matching is by whole token: `~/.claude.json`, `MYCLAUDE.md` and `~/.claude-code` are left alone. Windows-style paths such as `C:\Users\you\.claude` are not converted.

## What is not converted

- **Frontmatter and everything else**: only the substitutions above are applied; text is otherwise copied unchanged. Binary files are copied byte for byte.
- **`$ARGUMENTS`**: only Claude Code substitutes it. skill-sync prints a note for skills that use it and does not change it.
- **`agents/openai.yaml`**: a Codex-only metadata file. It is ignored on both sides, so it is never copied, overwritten or deleted.
- Line endings are ignored when comparing and preserved when writing.

## Why a skill is `ambiguous`

A skill is skipped when converting it could change its meaning:

1. **Mixed vocabulary.** It contains both this tool's word and the other tool's word for the same thing, for example "symlink `AGENTS.md` to `CLAUDE.md`". Converting for the other side would turn that into "symlink `AGENTS.md` to `AGENTS.md`".
2. **Would not round-trip.** A Claude skill mentions `~/.codex`. Writing the Codex copy is fine, but the next sync would read that copy's `~/.codex` as its own word and push a spurious change back.

To resolve either, reword the skill so it does not name both tools' files, or maintain the two copies by hand.

## Baselines

After a successful sync the neutral hash of each skill is recorded. On the next run:

- one side differs from the baseline: that side changed, so it is copied across;
- both differ: `conflict`;
- no baseline and the copies differ: `conflict` (it cannot tell which side is newer, so it does not guess; file timestamps are deliberately not used).
