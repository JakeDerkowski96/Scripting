"""Command-line entry point: argument parsing and output only; the logic lives in the package.

Exit codes: 0 ok, 1 error, 2 usage, 3 skills out of sync or needing attention (check/sync).

Required permissions: read access to the skill folders; write access to them and to the state
file for `sync` without --dry-run. No network access.

Usage:
    python -m skill_sync status
    python -m skill_sync sync --dry-run
    python -m skill_sync sync --prefer claude
    python -m skill_sync check --scope project
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from skill_sync.engine import SkillPlan, Status, apply_plans, build_plans, diff_lines
from skill_sync.exceptions import SkillSyncError
from skill_sync.locations import Scope, resolve_scopes
from skill_sync.rules import CLAUDE, CODEX, RULES

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_ATTENTION = 3

log = logging.getLogger("skill_sync")


def _parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--scope", choices=("project", "user", "all"), default="all")
    common.add_argument("--repo", type=Path, help="repository for the project scope (default: cwd)")
    common.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    common.add_argument("--only", action="append", default=[], metavar="NAME", help="one skill")
    common.add_argument("-v", "--verbose", action="store_true")

    parser = argparse.ArgumentParser(
        prog="skill-sync",
        description="Keep agent skills in sync between .claude/skills and .agents/skills.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", parents=[common], help="show what is in sync and what is not")
    sync = sub.add_parser("sync", parents=[common], help="copy changes to the other side")
    sync.add_argument("--dry-run", action="store_true", help="show changes without writing")
    sync.add_argument("--prefer", choices=(CLAUDE, CODEX), help="winner for conflicts")
    sub.add_parser("check", parents=[common], help="exit 3 if anything is out of sync")
    diff = sub.add_parser("diff", parents=[common], help="diff the neutral text of both copies")
    diff.add_argument("name", help="skill name")
    sub.add_parser("rules", help="show the transform rules")
    return parser


def _table(headers: tuple[str, ...], rows: Sequence[tuple[str, ...]]) -> str:
    widths = [max(len(str(row[i])) for row in [headers, *rows]) for i in range(len(headers))]
    lines = ["  ".join(h.ljust(w) for h, w in zip(headers, widths, strict=True)).rstrip()]
    lines.extend(
        "  ".join(str(c).ljust(w) for c, w in zip(row, widths, strict=True)).rstrip()
        for row in rows
    )
    return "\n".join(lines)


def _plans(scopes: list[Scope], only: list[str], prefer: str | None = None) -> list[SkillPlan]:
    plans: list[SkillPlan] = []
    for scope in scopes:
        plans.extend(build_plans(scope, only=tuple(only), prefer=prefer))
    missing = set(only) - {plan.name for plan in plans}
    for name in sorted(missing):
        print(f"warning: no skill named {name!r} in the selected scope(s)", file=sys.stderr)
    return plans


def _print_plans(plans: list[SkillPlan], *, show_foreign: bool) -> None:
    shown = [p for p in plans if show_foreign or p.status is not Status.FOREIGN]
    if not shown:
        print("No skills found.")
        return
    rows = [(p.scope, p.name, p.status.value, p.detail) for p in shown]
    print(_table(("SCOPE", "SKILL", "STATUS", "DETAIL"), rows))
    for plan in shown:
        uses_args = any(
            b"$ARGUMENTS" in item.content
            for tree in plan.trees.values()
            for item in tree.files.values()
        )
        if uses_args:
            print(
                f"note: {plan.scope}/{plan.name} uses $ARGUMENTS, which only Claude Code substitutes",
                file=sys.stderr,
            )


def _summary(plans: list[SkillPlan]) -> str:
    foreign = sum(1 for p in plans if p.status is Status.FOREIGN)
    managed = len(plans) - foreign
    in_sync = sum(1 for p in plans if p.status is Status.IN_SYNC)
    pending = sum(1 for p in plans if p.pending)
    attention = sum(1 for p in plans if p.needs_attention)
    text = f"{managed} skills: {in_sync} in sync, {pending} to sync, {attention} need attention"
    if foreign:
        text += f" ({foreign} from other tools hidden; -v shows them)"
    return text


def _cmd_status(args: argparse.Namespace) -> int:
    plans = _plans(resolve_scopes(args.scope, args.repo, args.home), args.only)
    _print_plans(plans, show_foreign=args.verbose)
    print(_summary(plans))
    return EXIT_OK


def _cmd_check(args: argparse.Namespace) -> int:
    plans = _plans(resolve_scopes(args.scope, args.repo, args.home), args.only)
    bad = [p for p in plans if p.pending or p.needs_attention]
    for plan in bad:
        print(f"OUT OF SYNC {plan.scope}/{plan.name}: {plan.status.value} - {plan.detail}")
    if bad:
        print(f"{len(bad)} skill(s) out of sync; run `skill-sync sync`")
        return EXIT_ATTENTION
    managed = sum(1 for p in plans if p.status is not Status.FOREIGN)
    print(f"OK: {managed} skills in sync")
    return EXIT_OK


def _cmd_sync(args: argparse.Namespace) -> int:
    scopes = resolve_scopes(args.scope, args.repo, args.home)
    plans: list[SkillPlan] = []
    changed = 0
    prefix = "[dry-run] " if args.dry_run else ""
    for scope in scopes:
        scope_plans = _plans([scope], args.only, args.prefer)
        for change in apply_plans(scope, scope_plans, dry_run=args.dry_run):
            changed += 1
            print(f"{prefix}{scope.name}/{change.name}")
            for action in change.actions:
                print(f"{prefix}  {action}")
        plans.extend(scope_plans)
    stuck = [p for p in plans if p.needs_attention]
    for plan in stuck:
        print(f"skipped {plan.scope}/{plan.name}: {plan.status.value} - {plan.detail}")
    print(
        f"{prefix}{changed} skill(s) {'would change' if args.dry_run else 'updated'}, "
        f"{len(stuck)} skipped"
    )
    return EXIT_ATTENTION if stuck else EXIT_OK


def _cmd_diff(args: argparse.Namespace) -> int:
    scopes = resolve_scopes(args.scope, args.repo, args.home)
    for scope in scopes:
        lines = diff_lines(scope, args.name)
        if lines:
            print(f"== {scope.name}/{args.name}")
            print("\n".join(lines))
    return EXIT_OK


def _cmd_rules(_args: argparse.Namespace) -> int:
    rows = [
        (
            rule.placeholder,
            rule.literals[CLAUDE],
            rule.literals[CODEX],
            ", ".join(rule.aliases.get(CODEX, ())) or "-",
        )
        for rule in RULES
    ]
    print(_table(("PLACEHOLDER", "CLAUDE", "CODEX", "CODEX ALIASES"), rows))
    return EXIT_OK


_COMMANDS = {
    "status": _cmd_status,
    "sync": _cmd_sync,
    "check": _cmd_check,
    "diff": _cmd_diff,
    "rules": _cmd_rules,
}


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return its exit code."""
    args = _parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if getattr(args, "verbose", False) else logging.WARNING,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )
    try:
        return _COMMANDS[args.command](args)
    except SkillSyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
