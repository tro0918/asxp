import tempfile
import unittest
from pathlib import Path

from src.asxp.core import SkillError, load, parse, validate


ROOT = Path(__file__).parents[1]


class CoreTests(unittest.TestCase):
    def test_examples_are_valid(self):
        for path in (ROOT / "examples").glob("*.skill.md"):
            self.assertEqual(validate(load(path)), [], path.name)

    def test_manifest_and_digest_are_stable(self):
        skill = load(ROOT / "examples/customer-support.skill.md")
        self.assertEqual(skill.manifest()["name"], "customer-support")
        self.assertTrue(skill.digest().startswith("sha256:"))
        self.assertEqual(skill.digest(), skill.digest())

    def test_rejects_missing_frontmatter(self):
        with self.assertRaises(SkillError):
            parse("# no frontmatter")

    def test_rejects_secret_field(self):
        text = """---
name: unsafe
description: Unsafe fixture.
asxp-version: 0.1
version: 1.0.0
api-key: secret
ae-tools-json: '[]'
---
Do work.
"""
        self.assertTrue(any("credential" in e for e in validate(parse(text))))

    def test_rejects_insecure_origin(self):
        text = """---
name: linked
description: Linked fixture.
asxp-version: 0.1
version: 1.0.0
origin-url: http://localhost/agent
ae-tools-json: '[]'
---
Do work.
"""
        self.assertTrue(any("HTTPS" in e for e in validate(parse(text))))


if __name__ == "__main__":
    unittest.main()
