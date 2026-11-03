# repo-radar

A small CLI that scans a folder of git repositories and shows, for each one, what it is, what stage it is at, whether local and remote agree, and what needs attention, as a terminal table or a self-contained HTML dashboard.

## Purpose

With many repos it is easy to lose track of what each one is for, which have uncommitted or unpushed work, and which are quietly stale. Git and GitHub already know most of the answers, so repo-radar *derives* them at scan time instead of asking you to maintain a list. The few things only a human knows (purpose, stage, next step) live in a small `.project.toml` inside each repo.

## What's here

```text
src/repo_radar/   scanner, git/GitHub readers, renderers, CLI
tests/            pytest suite (uses throwaway git repos)
docs/             usage, metadata format, troubleshooting
```

## Prerequisites

- Python 3.11+
- `git` on PATH
- Optional: [GitHub CLI](https://cli.github.com/) (`gh`) authenticated via `gh auth login`, for open PRs, issues, and CI status. Without it, repo-radar still works and skips those columns.

## Required permissions

| Role | Scope | Reason |
|---|---|---|
| Read | the repos folder | Read git state and `.project.toml` |
| Write | `~/.repo-radar/` | Cache the last scan and write the HTML report |
| Write | each repo (only for `init`) | Create a draft `.project.toml` |
| GitHub: read access to your repos | `gh` login | Read PRs, issues, and workflow runs. Nothing is created or modified |
| Network + `origin` read | only with `--fetch` | `git fetch` updates remote-tracking refs, nothing else |

## Usage

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"   # run from utilities/repo-radar; add --user instead of a venv for a global install

repo-radar scan                   # scan, cache, print the table
repo-radar list --attention       # cached scan, only repos with flags
repo-radar report --open          # write and open the HTML dashboard
repo-radar init --all --dry-run   # preview draft .project.toml files
repo-radar check                  # enforce the repos-folder rules (exit 3 on violations)
```

This tool lives in the `Scripting` repo under `utilities/repo-radar/`, so install it from there. Run `python -m repo_radar ...` if the `repo-radar` script is not on your PATH.

The scan root is found from `--root`, then `$REPO_RADAR_ROOT`, then `github-repos` under each OneDrive folder, then `~/OneDrive/github-repos`, then `~/github-repos`.

## Documentation

See the [docs index](docs/README.md): [usage](docs/usage.md), [`.project.toml` format](docs/metadata.md), [troubleshooting](docs/troubleshooting.md).

## Contributing

Follow the Scripting repo's conventions: branch as `<type>/<kebab-description>`, Conventional Commits, PR, squash merge. From this folder run `ruff check .`, `ruff format --check .`, `mypy src` and `pytest` before pushing; CI runs the same checks on changes under `utilities/repo-radar/`.

## License

GPL-3.0, inherited from the Scripting repo. See the [repo LICENSE](../../LICENSE).
