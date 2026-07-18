import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.asxp.core import SkillError, load_agent_skill
from src.asxp.package import build_manifest, install, manifest_diff, pack, validate_manifest, verify

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/v0.2/refund-policy"


class PackageTests(unittest.TestCase):
    def test_example_manifest_is_valid(self):
        manifest = json.loads((EXAMPLE / "asxp.json").read_text())
        self.assertEqual(validate_manifest(manifest), [])

    def test_pack_verify_install(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "refund-policy.asxp"
            pack(EXAMPLE, package)
            manifest = verify(package)
            self.assertEqual(manifest["package"]["name"], "refund-policy")
            installed = install(package, Path(temp) / "skills")
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue((installed / "asxp.json").is_file())

    def test_generated_manifest(self):
        manifest = build_manifest(EXAMPLE, "2.0.0", "example.org")
        self.assertEqual(manifest["skill"]["id"], "asxp://example.org/refund-policy")

    def test_detects_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "good.asxp"
            tampered = Path(temp) / "tampered.asxp"
            pack(EXAMPLE, package)
            with zipfile.ZipFile(package) as source, zipfile.ZipFile(tampered, "w") as target:
                for name in source.namelist():
                    data = source.read(name)
                    if name == "SKILL.md":
                        data += b"\nmalicious change"
                    target.writestr(name, data)
            with self.assertRaises(SkillError):
                verify(tampered)

    def test_rejects_zip_slip(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "unsafe.asxp"
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr("asxp.json", "{}")
                archive.writestr("SKILL.md", "---\nname: safe\ndescription: safe\n---\n")
                archive.writestr("../escape", "bad")
            with self.assertRaises(SkillError):
                verify(package)

    def test_permission_diff_requires_approval(self):
        left = {"package": {"version": "1.0.0"}, "permissions": ["orders.read"], "bindings": []}
        right = {"package": {"version": "1.1.0"}, "permissions": ["orders.read", "orders.write"], "bindings": []}
        result = manifest_diff(left, right)
        self.assertEqual(result["permissionsAdded"], ["orders.write"])
        self.assertTrue(result["requiresApproval"])

    def test_standard_agent_skill_has_no_asxp_frontmatter(self):
        skill = load_agent_skill(EXAMPLE / "SKILL.md")
        self.assertEqual(skill.frontmatter["name"], "refund-policy")
        self.assertNotIn("asxp-version", skill.frontmatter)

    def test_rejects_insecure_http_binding(self):
        manifest = json.loads((EXAMPLE / "asxp.json").read_text())
        manifest["bindings"] = [{"type": "asxp-http", "url": "http://localhost/delegate"}]
        self.assertTrue(any("HTTPS" in x for x in validate_manifest(manifest)))

    def test_rejects_unsupported_binding(self):
        manifest = json.loads((EXAMPLE / "asxp.json").read_text())
        manifest["bindings"] = [{"type": "magic"}]
        self.assertTrue(any("unsupported" in x for x in validate_manifest(manifest)))

    def test_rejects_duplicate_permissions(self):
        manifest = json.loads((EXAMPLE / "asxp.json").read_text())
        manifest["permissions"] = ["orders.read", "orders.read"]
        self.assertTrue(any("duplicates" in x for x in validate_manifest(manifest)))

    def test_rejects_secret_like_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "unsafe"
            root.mkdir()
            (root / "SKILL.md").write_text((EXAMPLE / "SKILL.md").read_text())
            (root / "asxp.json").write_text((EXAMPLE / "asxp.json").read_text())
            (root / ".env").write_text("API_KEY=secret")
            with self.assertRaises(SkillError):
                pack(root, Path(temp) / "unsafe.asxp")

    def test_install_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "skill.asxp"
            pack(EXAMPLE, package)
            target = Path(temp) / "target"
            install(package, target)
            with self.assertRaises(SkillError):
                install(package, target)

    def test_rejects_package_name_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "mismatch"
            root.mkdir()
            (root / "SKILL.md").write_text((EXAMPLE / "SKILL.md").read_text())
            manifest = json.loads((EXAMPLE / "asxp.json").read_text())
            manifest["package"]["name"] = "other-skill"
            (root / "asxp.json").write_text(json.dumps(manifest))
            package = Path(temp) / "mismatch.asxp"
            pack(root, package)
            with self.assertRaises(SkillError):
                verify(package)

    def test_rejects_revision_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "good.asxp"
            changed = Path(temp) / "changed.asxp"
            pack(EXAMPLE, package)
            with zipfile.ZipFile(package) as source, zipfile.ZipFile(changed, "w") as target:
                for name in source.namelist():
                    data = source.read(name)
                    if name == "asxp.json":
                        value = json.loads(data)
                        value["revision"] = "sha256:" + "0" * 64
                        data = json.dumps(value).encode()
                    target.writestr(name, data)
            with self.assertRaises(SkillError):
                verify(changed)

    def test_extensions_survive_packaging(self):
        manifest = json.loads((EXAMPLE / "asxp.json").read_text())
        manifest["extensions"] = {"org.example/audit": {"level": "strict"}}
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "extension.asxp"
            pack(EXAMPLE, package, manifest)
            self.assertEqual(verify(package)["extensions"], manifest["extensions"])


if __name__ == "__main__":
    unittest.main()
