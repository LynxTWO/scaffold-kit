"""Check the portable and Codex listing, including directory constraints."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]

class PluginListingTests(unittest.TestCase):
    def test_stable_catalogs_pin_the_reviewed_stable_source(self):
        for host in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
            catalog = json.loads((ROOT / host).read_text())
            self.assertEqual(catalog["name"], "lynxtwo")
            source = catalog["plugins"][0]["source"]
            self.assertEqual(source["sha"], "6095fad4215e6192bfb331e7b51e671a977ca1d6")
            self.assertNotIn("ref", source)
            self.assertEqual(source["source"], "url")
            self.assertEqual(source["url"], "https://github.com/LynxTWO/scaffold-kit.git")

    def test_host_versions_and_listing_are_consistent(self):
        portable = json.loads((ROOT / "plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        self.assertEqual({portable["version"], codex["version"], claude["version"]}, {portable["version"]})
        interface = portable["extensions"]["com.openai"]["interface"]
        self.assertEqual(interface, codex["interface"])
        for field, limit in (("displayName", 30), ("shortDescription", 30), ("longDescription", 4000), ("developerName", 80)):
            self.assertTrue(interface[field])
            self.assertLessEqual(len(interface[field]), limit)
        self.assertEqual(interface["category"], "Productivity")
        for field in ("logo", "composerIcon"):
            self.assertTrue((ROOT / interface[field]).is_file())
        rgb = [int(interface["brandColor"][i:i+2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in rgb]
        luminance = sum(c * weight for c, weight in zip(linear, (.2126, .7152, .0722)))
        self.assertGreaterEqual(1.05 / (luminance + .05), 2)

if __name__ == "__main__":
    unittest.main()
