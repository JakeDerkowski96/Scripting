"""Command-line interface: argument parsing, logging setup and exit codes only.

Usage:
    repo-radar scan [--fetch] [--no-github]      scan, cache, print the table
    repo-radar list [--stage S] [--attention]    show the cached scan
    repo-radar show NAME                         detail for one project
    repo-radar report [-o FILE] [--open]         write the HTML dashboard
    repo-radar init NAME... | --all [--dry-run]  draft .project.toml files
    repo-radar check                             enforce the repos-folder rules
    repo-radar obsidian --vault DIR [--dry-run]  write notes into an Obsidian vault

Exit codes: 0 ok, 1 error, 2 bad usage, 3 `check` found rule violations.

Required permissions: read access to the repos folder; `gh auth login` for
PR/CI data; write access to ~/.repo-radar (cache, report), for `init`,
to the repos it drafts files into, and for `obsidian` to the vault. See README for the full table.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from repo_radar import __version__, cache, config, obsidian, scanner
from repo_radar.attention import FLAGS, RULE_FLAGS
from repo_radar.exceptions import RepoRadarError
from repo_radar.meta import META_FILENAME, draft_summary, write_template
from repo_radar.models import STAGES, Project, ScanResult
from repo_radar.query import SORT_KEYS, filter_projects, sort_projects
from repo_radar.render_html import render_html
from repo_radar.render_table import render_detail, render_table

logger = logging.getLogger("repo_radar")


def _add_view_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--stage", choices=[*STAGES, "unset"], help="only this stage")
    p.add_argument("--attention", action="store_true", help="only projects with flags")
    p.add_argument("--search", metavar="TEXT", help="match name, summary or tags")
    p.add_argument("--sort", choices=SORT_KEYS, default="name", help="sort order (default: name)")


def _add_source_args(p: argparse.ArgumentParser, *, refresh: bool) -> None:
    p.add_argument("--root", type=Path, help="folder containing all repos")
    p.add_argument("--cache", type=Path, help="scan cache file")
    if refresh:
        p.add_argument("--refresh", action="store_true", help="re-scan instead of using the cache")
    p.add_argument("--fetch", action="store_true", help="git fetch each repo when scanning")
    p.add_argument("--no-github", action="store_true", help="skip GitHub lookups when scanning")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="repo-radar",
        description="See what each repo is, where it stands, and what needs attention.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_p = sub.add_parser("scan", help="scan all repos, cache the result, print the table")
    _add_source_args(scan_p, refresh=False)
    _add_view_args(scan_p)
    scan_p.add_argument("--wide", action="store_true", help="show summary and next step")

    list_p = sub.add_parser("list", help="show the table from the cached scan")
    _add_source_args(list_p, refresh=True)
    _add_view_args(list_p)
    list_p.add_argument("--wide", action="store_true", help="show summary and next step")

    show_p = sub.add_parser("show", help="detail for one project")
    show_p.add_argument("name")
    _add_source_args(show_p, refresh=True)

    report_p = sub.add_parser("report", help="write the HTML dashboard")
    _add_source_args(report_p, refresh=True)
    _add_view_args(report_p)
    report_p.add_argument("-o", "--output", type=Path, help="output file")
    report_p.add_argument("--open", action="store_true", help="open the report in a browser")

    check_p = sub.add_parser(
        "check", help="verify the repos-folder rules (git-only, visibility); exit 3 on violations"
    )
    _add_source_args(check_p, refresh=False)

    obs_p = sub.add_parser("obsidian", help="write one note per repo plus a dashboard into a vault")
    _add_source_args(obs_p, refresh=True)
    _add_view_args(obs_p)
    obs_p.add_argument("--vault", type=Path, help="vault folder (or set REPO_RADAR_VAULT)")
    obs_p.add_argument("--dry-run", action="store_true", help="show what would be written")

    init_p = sub.add_parser("init", help=f"draft a {META_FILENAME} in repos that lack one")
    init_p.add_argument("names", nargs="*", help="project folder names")
    init_p.add_argument("--all", action="store_true", help="every git repo without one")
    init_p.add_argument("--root", type=Path, help="folder containing all repos")
    init_p.add_argument("--force", action="store_true", help="overwrite existing files")
    init_p.add_argument("--dry-run", action="store_true", help="show what would be written")
    return parser


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


def _use_color() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _get_result(args: argparse.Namespace) -> ScanResult:
    """Return a fresh scan (and cache it) or the cached one."""
    cache_path = args.cache or config.default_cache_path()
    always_scan = args.command in ("scan", "check")  # a rule check must never trust a stale cache
    if always_scan or getattr(args, "refresh", False) or not cache_path.is_file():
        root = config.resolve_root(args.root)
        result = scanner.scan(root, use_github=not args.no_github, fetch=args.fetch)
        cache.save(result, cache_path)
        return result
    return cache.load(cache_path)


def _select(result: ScanResult, args: argparse.Namespace) -> list[Project]:
    filtered = filter_projects(
        result.projects, stage=args.stage, attention=args.attention, text=args.search
    )
    return sort_projects(filtered, args.sort)


def _cmd_table(args: argparse.Namespace) -> int:
    result = _get_result(args)
    now = datetime.now().astimezone()
    print(render_table(_select(result, args), now=now, color=_use_color(), wide=args.wide))
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    result = _get_result(args)
    match = [p for p in result.projects if p.name.lower() == args.name.lower()]
    if not match:
        names = ", ".join(p.name for p in result.projects)
        print(f"error: no project named '{args.name}'. Known: {names}", file=sys.stderr)
        return 2
    print(render_detail(match[0], now=datetime.now().astimezone()))
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    result = _get_result(args)
    output = args.output or config.default_report_path()
    page = render_html(result, _select(result, args), now=datetime.now().astimezone())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    print(f"Wrote {output}")
    if args.open:
        webbrowser.open(output.resolve().as_uri())
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    result = _get_result(args)
    violations = [(p, f) for p in result.projects for f in p.flags if f in RULE_FLAGS]
    if not violations:
        print(f"OK: all {len(result.projects)} folders follow the repos-folder rules")
        return 0
    for project, flag in violations:
        print(f"VIOLATION {project.name}: {flag} - {FLAGS[flag]}")
    print(f"{len(violations)} violation(s) across {len(result.projects)} folders")
    return 3


def _cmd_obsidian(args: argparse.Namespace) -> int:
    vault = config.resolve_vault(args.vault)
    result = _get_result(args)
    actions = obsidian.export(
        vault, result, _select(result, args), datetime.now().astimezone(), dry_run=args.dry_run
    )
    for action in actions:
        if action.verb != "unchanged":
            verb = action.verb.removesuffix("d") if args.dry_run else action.verb
            prefix = "would " if args.dry_run else ""
            print(f"{prefix}{verb} {action.path.relative_to(vault)}")
    changed = sum(1 for a in actions if a.verb != "unchanged")
    print(
        f"{changed} of {len(actions)} note(s) {'would change' if args.dry_run else 'written'} in {vault}"
    )
    return 0


def _cmd_init(args: argparse.Namespace) -> int:
    if not args.names and not args.all:
        print("error: give project names or --all", file=sys.stderr)
        return 2
    root = config.resolve_root(args.root)
    candidates = scanner.discover(root)
    if not args.all:
        wanted = {n.lower() for n in args.names}
        unknown = wanted - {p.name.lower() for p in candidates}
        if unknown:
            print(f"error: not found under {root}: {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        candidates = [p for p in candidates if p.name.lower() in wanted]
    else:
        candidates = [p for p in candidates if (p / ".git").exists()]

    logging.getLogger("repo_radar").setLevel(logging.INFO)
    written = 0
    for path in candidates:
        if write_template(path, draft_summary(path), force=args.force, dry_run=args.dry_run):
            written += 1
            verb = "would write" if args.dry_run else "wrote"
            print(f"{verb} {path.name}/{META_FILENAME}")
        else:
            print(f"skip  {path.name} (already has {META_FILENAME}; use --force)")
    print(f"{written} file(s) {'would be ' if args.dry_run else ''}written")
    return 0


_HANDLERS = {
    "scan": _cmd_table,
    "list": _cmd_table,
    "show": _cmd_show,
    "report": _cmd_report,
    "init": _cmd_init,
    "check": _cmd_check,
    "obsidian": _cmd_obsidian,
}


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns the process exit code."""
    # Table glyphs (↑ ↓ ✓) must survive a cp1252 console or a redirect.
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    args = build_parser().parse_args(argv)
    _setup_logging(args.verbose)
    try:
        return _HANDLERS[args.command](args)
    except RepoRadarError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
