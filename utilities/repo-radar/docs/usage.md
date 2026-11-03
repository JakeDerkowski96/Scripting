# Usage

## Commands

| Command | What it does |
|---|---|
| `repo-radar scan` | Scan every folder under the root, cache the result, print the table |
| `repo-radar list` | Print the table from the cached scan (instant); `--refresh` re-scans |
| `repo-radar show NAME` | Full detail for one project |
| `repo-radar report` | Write the HTML dashboard to `~/.repo-radar/report.html` (`-o` to change, `--open` to launch) |
| `repo-radar check` | Enforce the repos-folder rules (below). Always re-scans. Exit code 3 when there are violations, so it can gate a hook or CI |
| `repo-radar init NAME... \| --all` | Draft a `.project.toml` where none exists (`--dry-run`, `--force`) |

Shared flags: `--root`, `--cache`, `--fetch`, `--no-github`, `-v`.
View flags (`scan`, `list`, `report`): `--stage`, `--attention`, `--search`, `--sort name|stage|activity|attention`; `--wide` (table) adds summary and next step.

## Examples

```bash
repo-radar scan --fetch                  # accurate ahead/behind; slower
repo-radar list --attention --sort attention
repo-radar list --stage unset            # repos still needing a stage
repo-radar show scrawl
repo-radar report --stage active --open
repo-radar init --all --dry-run          # then re-run without --dry-run
```

## Reading the table

`SYNC` shows `↑n` unpushed commits, `↓n` commits to pull, `*n` changed files, `local-only` when there is no remote, and `✓` when everything agrees.

`↓` is only as fresh as the last `git fetch`. Use `--fetch` for the truth.

## Attention flags

| Flag | Meaning |
|---|---|
| `not-git` | Folder is not a git repository |
| `git-error` | git could not read the repository |
| `no-meta` | No `.project.toml`, or it has no `stage` |
| `bad-meta` | `.project.toml` is invalid (see `show`) |
| `dirty` | Uncommitted or untracked changes |
| `unpushed` | Local commits not on the remote |
| `behind` | Remote has commits not pulled |
| `no-remote` | No `origin` |
| `no-upstream` | Branch does not track a remote branch |
| `visibility-mismatch` | GitHub visibility differs from `visibility` in `.project.toml` (e.g. a private repo went public) |
| `visibility-unknown` | `visibility` is set but could not be verified; run with `gh` authenticated and without `--no-github` |
| `open-prs` | Open pull requests |
| `ci-failing` | Latest run on the default branch failed |
| `stale` | No commits in 60+ days (skipped for maintenance, paused, archived, done) |

## What `init` changes

`init` creates a new untracked `.project.toml` inside each target repo, which makes that repo show as `dirty` until you commit the file. The `stage` line is left commented out on purpose; pick one and uncomment it.

## Not covered

repo-radar never commits, pushes, or modifies repo content. It only reads, except for `init` and its own cache and report.

## Repos-folder rules

`repo-radar check` fails (exit 3) when:

1. **A folder under the root is not a git repository** (`not-git`). Only git projects live in the repos folder. Dot-folders such as `.claude` are exempt. Fix by running `git init` in it, or moving it out of the folder.
2. **A repo's GitHub visibility differs from `visibility` in its `.project.toml`** (`visibility-mismatch`), for example a private repo that became public.
3. **An expected visibility could not be verified** (`visibility-unknown`), so a failing `gh` never reads as a pass.

Exit codes: 0 ok, 1 error, 2 bad usage, 3 rule violations.
