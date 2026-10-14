"""Protect the reviewed PDF bytes, source bindings and public brief links."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BriefArtifactTests(unittest.TestCase):
    def test_both_reviewed_palettes_match_their_provenance(self):
        for theme in ("light", "dark"):
            with self.subTest(theme=theme):
                name = "scaffold-kit-brief" + ("-dark" if theme == "dark" else "") + ".pdf"
                pdf = ROOT / "brief" / name
                record = json.loads(pdf.with_suffix(".pdf.provenance.json").read_text())
                self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
                self.assertEqual(digest(pdf), record["pdf_sha256"])
                self.assertEqual(record["color_scheme"], theme)
                self.assertEqual(digest(ROOT / "brief/scaffold-kit-brief.html"), record["source_sha256"])
                self.assertEqual(digest(ROOT / "design/render-brief-pdf.py"), record["renderer_sha256"])
                for name, expected in record["source_facts_checked_against"].items():
                    self.assertEqual(digest(ROOT / name), expected, name)

    def test_readme_links_both_pdfs_and_the_responsive_html(self):
        readme = (ROOT / "README.md").read_text()
        for name in ("scaffold-kit-brief.pdf", "scaffold-kit-brief-dark.pdf", "scaffold-kit-brief.html"):
            self.assertIn("brief/" + name, readme)
            self.assertTrue((ROOT / "brief" / name).is_file())


if __name__ == "__main__":
    unittest.main()
