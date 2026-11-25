"""Command line: `python -m app catalog check|set` and `python -m app schema`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.catalog import CatalogError, CatalogIndex, FlagDefinition, load_catalog

SCHEMAS = {
    "flag-definition.schema.json": FlagDefinition,
    "catalog-index.schema.json": CatalogIndex,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="labeler")
    sub = parser.add_subparsers(dest="command", required=True)

    catalog = sub.add_parser("catalog", help="flag catalog operations").add_subparsers(dest="action", required=True)
    check = catalog.add_parser("check", help="validate flag definitions and the index")
    check.add_argument("path", type=Path)
    show_set = catalog.add_parser("set", help="list the flags of a set with includes expanded")
    show_set.add_argument("path", type=Path)
    show_set.add_argument("name")

    schema = sub.add_parser("schema", help="write JSON Schema files for the catalog format")
    schema.add_argument("--out", type=Path, default=Path("schemas"))

    args = parser.parse_args(argv)

    if args.command == "schema":
        args.out.mkdir(parents=True, exist_ok=True)
        for name, model in SCHEMAS.items():
            content = json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n"
            (args.out / name).write_text(content, encoding="utf-8")
            print(args.out / name)
        return 0

    try:
        cat = load_catalog(args.path)
    except CatalogError as e:
        print(f"Catalog {args.path} has {len(e.problems)} problem(s):", file=sys.stderr)
        for p in e.problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    if args.action == "check":
        without_instructions = sum(1 for f in cat.flags.values() if f.instructions is None)
        print(f"Catalog {cat.version}: {len(cat.flags)} flags, {len(cat.index.sets)} sets")
        for name, s in cat.index.sets.items():
            print(f"  {name:<28} {len(cat.flag_set(name)):>3}  {s.description}")
        if without_instructions:
            print(f"Without model instructions: {without_instructions} of {len(cat.flags)}")
        if unassigned := cat.unassigned():
            print(f"Not in any set: {', '.join(unassigned)}")
        return 0

    try:
        flags = cat.flag_set(args.name)
    except KeyError as e:
        print(e.args[0], file=sys.stderr)
        return 1
    for f in flags:
        print(f.code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
