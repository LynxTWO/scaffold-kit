"""The shared preview catalog must never become a stable catalog alias."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ChannelTests(unittest.TestCase):
    def test_both_hosts_select_the_same_explicit_preview_commits(self):
        catalogs = [json.loads((ROOT / "preview" / path).read_text()) for path in
                    (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json")]
        stable = {"scaffold-kit": "d6783f8f51db0b6c74f001f425666225d7e79220",
                  "anti-dark-code": "f3bb47904a9eb4d75e19cc84dcdbb62039feac46"}
        selections = []
        for catalog in catalogs:
            self.assertEqual(catalog["name"], "lynxtwo-preview")
            self.assertEqual({p["name"] for p in catalog["plugins"]}, set(stable))
            selected = {}
            for plugin in catalog["plugins"]:
                if "policy" in plugin:
                    self.assertEqual(plugin["policy"]["installation"], "AVAILABLE")
                source = plugin["source"]
                sha = source["sha"]
                self.assertRegex(sha, r"^[0-9a-f]{40}$")
                self.assertNotEqual(sha, stable[plugin["name"]])
                self.assertNotIn("ref", source)
                self.assertEqual(source["source"], "url")
                self.assertTrue(source["url"].startswith("https://github.com/"))
                selected[plugin["name"]] = (source["url"], sha)
            selections.append(selected)
        self.assertEqual(*selections)
