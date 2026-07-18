from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
TOOL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,127}$")
REQUIRED = ("name", "description", "asxp-version", "version", "ae-tools-json")
AGENT_SKILL_REQUIRED = ("name", "description")
SECRET_KEYS = ("api-key", "apikey", "access-token", "refresh-token", "client-secret", "password", "cookie", "credential")


class SkillError(ValueError):
    pass


@dataclass(frozen=True)
class Skill:
    frontmatter: dict[str, str]
    instructions: str
    tools: list[dict[str, Any]]

    def manifest(self) -> dict[str, Any]:
        fm = self.frontmatter
        result: dict[str, Any] = {
            "protocolVersion": fm["asxp-version"],
            "name": fm["name"],
            "description": fm["description"],
            "version": fm["version"],
            "instructions": self.instructions,
            "tools": self.tools,
        }
        direct = ("id", "revision", "publisher", "license", "privacy")
        for key in direct:
            if key in fm:
                result[key] = fm[key]
        if fm.get("permissions"):
            result["permissions"] = fm["permissions"].split()
        if fm.get("origin-url"):
            result["origin"] = {"url": fm["origin-url"]}
            if fm.get("delegation-url"):
                result["origin"]["delegationUrl"] = fm["delegation-url"]
        if fm.get("extensions-json"):
            result["extensions"] = json.loads(fm["extensions-json"])
        return result

    def digest(self) -> str:
        canonical = json.dumps(self.manifest(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        if value[0] == "'":
            return value[1:-1].replace("''", "'")
        return json.loads(value)
    return value


def parse(text: str) -> Skill:
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise SkillError("document must start with YAML frontmatter delimiter '---'")
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        raise SkillError("frontmatter closing delimiter is missing")
    fm: dict[str, str] = {}
    for number, raw in enumerate(lines[1:end], 2):
        line = raw.rstrip("\r\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise SkillError(f"frontmatter line {number} is not a scalar key/value")
        key, value = line.split(":", 1)
        key = key.strip()
        if not key or key in fm:
            raise SkillError(f"frontmatter line {number} has an empty or duplicate key")
        fm[key] = _unquote(value)
    missing = [key for key in REQUIRED if not fm.get(key)]
    if missing:
        raise SkillError("missing required field(s): " + ", ".join(missing))
    try:
        tools = json.loads(fm["ae-tools-json"])
    except json.JSONDecodeError as exc:
        raise SkillError(f"ae-tools-json is invalid JSON: {exc.msg}") from exc
    if not isinstance(tools, list):
        raise SkillError("ae-tools-json must contain an array")
    return Skill(fm, "".join(lines[end + 1 :]), tools)


def validate(skill: Skill) -> list[str]:
    errors: list[str] = []
    fm = skill.frontmatter
    if fm["asxp-version"] != "0.1":
        errors.append("unsupported asxp-version (expected 0.1)")
    if not NAME_RE.fullmatch(fm["name"]):
        errors.append("name must be lowercase kebab-case and at most 64 characters")
    if not SEMVER_RE.fullmatch(fm["version"]):
        errors.append("version must be SemVer")
    if len(fm["description"]) > 4096:
        errors.append("description exceeds 4096 characters")
    if len(skill.instructions.encode()) > 262144:
        errors.append("instructions exceed 256 KiB")
    if len(skill.tools) > 128:
        errors.append("tool count exceeds 128")
    for i, tool in enumerate(skill.tools):
        prefix = f"tools[{i}]"
        if not isinstance(tool, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for required in ("name", "description", "inputSchema"):
            if required not in tool:
                errors.append(f"{prefix}.{required} is required")
        if "name" in tool and (not isinstance(tool["name"], str) or not TOOL_RE.fullmatch(tool["name"])):
            errors.append(f"{prefix}.name is invalid")
        if "description" in tool and not isinstance(tool["description"], str):
            errors.append(f"{prefix}.description must be a string")
        if "inputSchema" in tool and not isinstance(tool["inputSchema"], dict):
            errors.append(f"{prefix}.inputSchema must be an object")
    for key, value in fm.items():
        lowered = key.lower()
        if any(marker in lowered for marker in SECRET_KEYS):
            errors.append(f"frontmatter field '{key}' appears to contain credential material")
        if key in ("origin-url", "delegation-url", "homepage"):
            parsed = urlparse(value)
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{key} must be an absolute HTTPS URL")
    if fm.get("privacy") not in (None, "local", "delegated", "external"):
        errors.append("privacy must be local, delegated, or external")
    if fm.get("delegation-url") and not fm.get("origin-url"):
        errors.append("delegation-url requires origin-url")
    return errors


def load(path: str | Path) -> Skill:
    return parse(Path(path).read_text(encoding="utf-8"))


def parse_agent_skill(text: str) -> Skill:
    """Parse the portable Agent Skills core without requiring ASXP fields."""
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise SkillError("document must start with YAML frontmatter delimiter '---'")
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        raise SkillError("frontmatter closing delimiter is missing")
    fm: dict[str, str] = {}
    for number, raw in enumerate(lines[1:end], 2):
        line = raw.rstrip("\r\n")
        if not line.strip() or line.lstrip().startswith("#") or line[0].isspace():
            continue
        if ":" not in line:
            raise SkillError(f"frontmatter line {number} is not a key/value")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if not key or key in fm:
            raise SkillError(f"frontmatter line {number} has an empty or duplicate key")
        fm[key] = _unquote(value)
    missing = [key for key in AGENT_SKILL_REQUIRED if not fm.get(key)]
    if missing:
        raise SkillError("missing Agent Skills field(s): " + ", ".join(missing))
    if not NAME_RE.fullmatch(fm["name"]) or "--" in fm["name"]:
        raise SkillError("Agent Skills name must be lowercase kebab-case")
    if len(fm["description"]) > 1024:
        raise SkillError("Agent Skills description exceeds 1024 characters")
    return Skill(fm, "".join(lines[end + 1 :]), [])


def load_agent_skill(path: str | Path) -> Skill:
    return parse_agent_skill(Path(path).read_text(encoding="utf-8"))
