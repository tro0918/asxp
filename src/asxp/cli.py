from __future__ import annotations

import argparse
import json
import sys

from .core import SkillError, load, validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="asxp")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "inspect", "manifest"):
        cmd = sub.add_parser(name)
        cmd.add_argument("path")
    args = parser.parse_args(argv)
    try:
        skill = load(args.path)
        errors = validate(skill)
    except (OSError, SkillError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    if args.command == "validate":
        print(f"valid: {skill.frontmatter['name']}@{skill.frontmatter['version']} ({skill.digest()})")
    elif args.command == "inspect":
        linked = "origin-url" in skill.frontmatter
        delegated = "delegation-url" in skill.frontmatter
        print(json.dumps({
            "name": skill.frontmatter["name"], "version": skill.frontmatter["version"],
            "tools": [tool["name"] for tool in skill.tools], "linked": linked,
            "delegation": delegated, "digest": skill.digest()
        }, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(skill.manifest(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
