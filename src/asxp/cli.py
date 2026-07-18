from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import SkillError, load, validate
from .package import build_manifest, install, manifest_diff, pack, verify


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="asxp")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "inspect", "manifest"):
        cmd = sub.add_parser(name)
        cmd.add_argument("path")
    pack_cmd = sub.add_parser("pack", help="build a portable .asxp package")
    pack_cmd.add_argument("skill_dir")
    pack_cmd.add_argument("--output", "-o", required=True)
    pack_cmd.add_argument("--version", default="0.1.0")
    pack_cmd.add_argument("--publisher")
    verify_cmd = sub.add_parser("verify", help="validate package integrity")
    verify_cmd.add_argument("package")
    install_cmd = sub.add_parser("install", help="install a verified package")
    install_cmd.add_argument("package")
    install_cmd.add_argument("--target", required=True)
    install_cmd.add_argument("--force", action="store_true")
    diff_cmd = sub.add_parser("diff", help="show permission and binding changes")
    diff_cmd.add_argument("left")
    diff_cmd.add_argument("right")
    args = parser.parse_args(argv)
    try:
        if args.command == "pack":
            root = Path(args.skill_dir)
            manifest_path = root / "asxp.json"
            generated = None if manifest_path.exists() else build_manifest(root, args.version, args.publisher)
            output = pack(root, args.output, generated)
            print(f"packed: {output}")
            return 0
        if args.command == "verify":
            value = verify(args.package)
            print(f"verified: {value['package']['name']}@{value['package']['version']} ({value['revision']})")
            return 0
        if args.command == "install":
            output = install(args.package, args.target, args.force)
            print(f"installed: {output}")
            return 0
        if args.command == "diff":
            print(json.dumps(manifest_diff(verify(args.left), verify(args.right)), indent=2, ensure_ascii=False))
            return 0
    except (OSError, SkillError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
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
