#!/usr/bin/env python3
"""CLI for searching and installing skills."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from skill_registry import RegistryError, SourceSpec, install_candidate, load_sources, save_user_sources, search


def print_candidates(candidates: list, warnings: list[str], as_json: bool) -> int:
    if as_json:
        print(
            json.dumps(
                {
                    "warnings": warnings,
                    "candidates": [candidate.to_dict() for candidate in candidates],
                },
                indent=2,
            )
        )
        return 0

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if not candidates:
        print("No matching skills found.")
        return 1

    for idx, candidate in enumerate(candidates, start=1):
        state = "installed" if candidate.installed else "remote"
        print(f"{idx}. {candidate.name} [{state}] score={candidate.score}")
        print(f"   source: {candidate.source_name}")
        print(f"   desc:   {candidate.description}")
        print(f"   where:  {candidate.location}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    candidates, warnings = search(args.need, limit=args.limit)
    return print_candidates(candidates, warnings, args.json)


def cmd_ensure(args: argparse.Namespace) -> int:
    candidates, warnings = search(args.need, limit=max(args.limit, 3))
    if warnings:
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
    if not candidates:
        print("No matching skills found.", file=sys.stderr)
        return 1

    best = candidates[0]
    runner_up_gap = best.score - candidates[1].score if len(candidates) > 1 else best.score
    if not args.force and len(candidates) > 1 and runner_up_gap < 4:
        print("Multiple close matches found. Re-run with --force to install the top match.", file=sys.stderr)
        return print_candidates(candidates[:3], [], False)

    if best.installed:
        print(f"Already available: {best.name}")
        print(best.location)
        return 0

    try:
        destination = install_candidate(best, Path(args.dest) if args.dest else None)
    except RegistryError as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1

    print(f"Installed {best.name} -> {destination}")
    print("Restart or reload the target agent to pick up new skills.")
    return 0


def cmd_list_sources(_: argparse.Namespace) -> int:
    for source in load_sources():
        print(f"{source.name}: {source.repo} {source.ref} {source.path}")
    return 0


def cmd_add_source(args: argparse.Namespace) -> int:
    sources = load_sources()
    custom = [source for source in sources if not source.name.startswith("openai-")]
    custom.append(
        SourceSpec(
            name=args.name,
            repo=args.repo,
            path=args.path.strip("/"),
            ref=args.ref,
            tags=tuple(args.tags or []),
        )
    )
    path = save_user_sources(custom)
    print(f"Saved source config to {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search and install AI agent skills.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search for matching skills")
    search_parser.add_argument("--need", required=True, help="Capability or task to match")
    search_parser.add_argument("--limit", type=int, default=8)
    search_parser.add_argument("--json", action="store_true")
    search_parser.set_defaults(func=cmd_search)

    ensure_parser = subparsers.add_parser("ensure", help="Install the best matching skill")
    ensure_parser.add_argument("--need", required=True, help="Capability or task to match")
    ensure_parser.add_argument("--limit", type=int, default=8)
    ensure_parser.add_argument("--dest", help="Alternate skills destination root for non-default agent runtimes")
    ensure_parser.add_argument("--force", action="store_true", help="Install the top match even if the scores are close")
    ensure_parser.set_defaults(func=cmd_ensure)

    list_parser = subparsers.add_parser("list-sources", help="Show configured registries")
    list_parser.set_defaults(func=cmd_list_sources)

    add_parser = subparsers.add_parser("add-source", help="Add a custom GitHub skill registry")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--repo", required=True, help="owner/repo")
    add_parser.add_argument("--path", required=True, help="path inside repo")
    add_parser.add_argument("--ref", default="main")
    add_parser.add_argument("--tags", nargs="*")
    add_parser.set_defaults(func=cmd_add_source)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
