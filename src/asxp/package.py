from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

from .core import NAME_RE, SEMVER_RE, SkillError, load_agent_skill

MAX_PACKAGE_BYTES = 10 * 1024 * 1024
MAX_FILES = 256
SECRET_NAMES = (".env", "credentials", "secret", "token", "id_rsa", "id_ed25519", ".pem", ".p12")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_manifest(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SkillError("asxp.json must contain an object")
    return value


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("specVersion") != "0.2":
        errors.append("specVersion must be 0.2")
    package = manifest.get("package")
    if not isinstance(package, dict):
        errors.append("package must be an object")
        package = {}
    name, version = package.get("name"), package.get("version")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        errors.append("package.name is invalid")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        errors.append("package.version must be SemVer")
    skill = manifest.get("skill")
    if not isinstance(skill, dict) or skill.get("entrypoint") != "SKILL.md":
        errors.append("skill.entrypoint must be SKILL.md")
    permissions = manifest.get("permissions")
    if not isinstance(permissions, list) or any(not isinstance(x, str) for x in permissions):
        errors.append("permissions must be an array of strings")
    elif len(set(permissions)) != len(permissions):
        errors.append("permissions must not contain duplicates")
    bindings = manifest.get("bindings")
    if not isinstance(bindings, list):
        errors.append("bindings must be an array")
        bindings = []
    supported = {"embedded", "mcp", "asxp-http", "a2a"}
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict) or binding.get("type") not in supported:
            errors.append(f"bindings[{index}].type is unsupported")
            continue
        if binding["type"] == "mcp" and not binding.get("server"):
            errors.append(f"bindings[{index}].server is required")
        if binding["type"] == "asxp-http" and not _https(binding.get("url")):
            errors.append(f"bindings[{index}].url must be HTTPS")
        if binding["type"] == "a2a" and (not _https(binding.get("agentCard")) or not binding.get("skillId")):
            errors.append(f"bindings[{index}] requires HTTPS agentCard and skillId")
    origin = manifest.get("origin")
    if origin is not None and (not isinstance(origin, dict) or not _https(origin.get("syncUrl"))):
        errors.append("origin.syncUrl must be HTTPS")
    return errors


def _https(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _portable_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix().lower()
        if any(marker in relative for marker in SECRET_NAMES):
            raise SkillError(f"refusing to package possible credential file: {relative}")
        files.append(path)
    if len(files) > MAX_FILES:
        raise SkillError(f"package exceeds {MAX_FILES} files")
    if sum(path.stat().st_size for path in files) > MAX_PACKAGE_BYTES:
        raise SkillError("package exceeds 10 MiB")
    return files


def build_manifest(skill_dir: str | Path, version: str, publisher: str | None = None) -> dict[str, Any]:
    root = Path(skill_dir)
    skill = load_agent_skill(root / "SKILL.md")
    manifest: dict[str, Any] = {
        "specVersion": "0.2",
        "package": {"name": skill.frontmatter["name"], "version": version},
        "skill": {"entrypoint": "SKILL.md"},
        "permissions": [],
        "privacy": "local",
        "bindings": [],
    }
    if publisher:
        manifest["package"]["publisher"] = publisher
        manifest["skill"]["id"] = f"asxp://{publisher}/{skill.frontmatter['name']}"
    if skill.frontmatter.get("license"):
        manifest["package"]["license"] = skill.frontmatter["license"]
    return manifest


def pack(skill_dir: str | Path, output: str | Path, manifest: dict[str, Any] | None = None) -> Path:
    root, destination = Path(skill_dir), Path(output)
    if not (root / "SKILL.md").is_file():
        raise SkillError("skill directory must contain SKILL.md")
    if manifest is None:
        sidecar = root / "asxp.json"
        if not sidecar.is_file():
            raise SkillError("skill directory must contain asxp.json or receive a generated manifest")
        manifest = load_manifest(sidecar)
    errors = validate_manifest(manifest)
    if errors:
        raise SkillError("invalid manifest: " + "; ".join(errors))
    files = [path for path in _portable_files(root) if path.name != "asxp.json"]
    integrity = {path.relative_to(root).as_posix(): sha256_bytes(path.read_bytes()) for path in files}
    manifest = json.loads(json.dumps(manifest))
    manifest["integrity"] = {"algorithm": "sha256", "files": integrity}
    manifest_without_revision = json.loads(json.dumps(manifest))
    manifest_without_revision.pop("revision", None)
    manifest["revision"] = "sha256:" + sha256_bytes(canonical_json(manifest_without_revision))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("asxp.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
    return destination


def verify(package_path: str | Path) -> dict[str, Any]:
    path = Path(package_path)
    if path.stat().st_size > MAX_PACKAGE_BYTES:
        raise SkillError("package exceeds 10 MiB")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) > MAX_FILES or "asxp.json" not in names or "SKILL.md" not in names:
            raise SkillError("package must contain asxp.json and SKILL.md within file limits")
        for name in names:
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts:
                raise SkillError(f"unsafe archive path: {name}")
        manifest = json.loads(archive.read("asxp.json"))
        errors = validate_manifest(manifest)
        if errors:
            raise SkillError("invalid manifest: " + "; ".join(errors))
        integrity = manifest.get("integrity", {}).get("files", {})
        if not isinstance(integrity, dict):
            raise SkillError("integrity.files is required")
        for name, expected in integrity.items():
            if name not in names or sha256_bytes(archive.read(name)) != expected:
                raise SkillError(f"integrity mismatch: {name}")
        revision_manifest = json.loads(json.dumps(manifest))
        revision = revision_manifest.pop("revision", None)
        expected_revision = "sha256:" + sha256_bytes(canonical_json(revision_manifest))
        if revision != expected_revision:
            raise SkillError("package revision mismatch")
        with tempfile.TemporaryDirectory() as temp:
            skill_path = Path(temp) / "SKILL.md"
            skill_path.write_bytes(archive.read("SKILL.md"))
            skill = load_agent_skill(skill_path)
            if skill.frontmatter["name"] != manifest["package"]["name"]:
                raise SkillError("SKILL.md name does not match package.name")
        return manifest


def install(package_path: str | Path, target: str | Path, force: bool = False) -> Path:
    manifest = verify(package_path)
    destination = Path(target) / manifest["package"]["name"]
    if destination.exists() and not force:
        raise SkillError(f"destination already exists: {destination}")
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    with zipfile.ZipFile(package_path) as archive:
        for name in archive.namelist():
            output = destination / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(archive.read(name))
    return destination


def manifest_diff(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    old_permissions, new_permissions = set(left.get("permissions", [])), set(right.get("permissions", []))
    old_bindings = {json.dumps(x, sort_keys=True) for x in left.get("bindings", [])}
    new_bindings = {json.dumps(x, sort_keys=True) for x in right.get("bindings", [])}
    return {
        "from": left.get("package", {}).get("version"),
        "to": right.get("package", {}).get("version"),
        "permissionsAdded": sorted(new_permissions - old_permissions),
        "permissionsRemoved": sorted(old_permissions - new_permissions),
        "bindingsAdded": [json.loads(x) for x in sorted(new_bindings - old_bindings)],
        "bindingsRemoved": [json.loads(x) for x in sorted(old_bindings - new_bindings)],
        "requiresApproval": bool((new_permissions - old_permissions) or (new_bindings - old_bindings)),
    }
