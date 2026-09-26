"""Each check must catch its violation and pass a clean document set."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("kit_audit", ROOT / "scripts" / "kit_audit.py")
kit_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit_audit)

CLEAN_ADD = """# Demo Architecture Document (ADD)

Version: 0.1 Draft. Date: 2026-09-26. Status: Audited.

## 1. One-Page Overview

Short and plain.

## 8. Technology Selection

### 8.4 Database

DECISION: Database
STATUS: Confirmed
CHOICE: relational

## 15. Current Build Boundary

See SLICE-001.
"""

CLEAN_EDD = """# Demo Engineering Document (EDD)

Version: 0.1 Draft. Date: 2026-09-26. Status: Audited.

## 11. Testing and Verification

Per ADD section 8.4 the database is relational.
"""

CLEAN_LOG = """# Demo Decision Log

Version: 0.1 Draft. Date: 2026-09-26.

## Index

| ID | Date | Decision | Status | Superseded by |
|---|---|---|---|---|
| D-001 | 2026-09-26 | Database | Superseded | D-002 |
| D-002 | 2026-09-26 | Database, revised | Confirmed | |

## Entries

## D-001: Database
Date: 2026-09-26
Status: Superseded
Area: ADD 8.4

Superseded by D-002.

## D-002: Database, revised
Date: 2026-09-26
Status: Confirmed
Area: ADD 8.4

Supersedes D-001.
"""


def write_docs(directory: Path, **files: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (directory / name.replace("_", "-")).write_text(text, encoding="utf-8")
    return directory


class KitAuditTests(unittest.TestCase):
    def run_audit(self, **files: str):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_docs(Path(tmp) / "docs", **files)
            return kit_audit.audit(root)

    def messages(self, findings):
        return [f["message"] for f in findings]

    def test_clean_document_set_has_no_findings(self):
        findings = self.run_audit(**{"ARCHITECTURE.md": CLEAN_ADD, "ENGINEERING.md": CLEAN_EDD, "DECISION-LOG.md": CLEAN_LOG})
        self.assertEqual([], findings)

    def test_dashes_and_banned_words_are_found(self):
        text = CLEAN_ADD + "\nA robust choice — truly.\n"
        messages = self.messages(self.run_audit(**{"ARCHITECTURE.md": text}))
        self.assertIn("em or en dash", messages)
        self.assertIn("banned word: robust", messages)

    def test_decision_without_status_is_found(self):
        text = CLEAN_ADD.replace("STATUS: Confirmed\n", "")
        messages = self.messages(self.run_audit(**{"ARCHITECTURE.md": text}))
        self.assertTrue(any("DECISION without STATUS" in m for m in messages))

    def test_status_outside_vocabulary_is_found(self):
        text = CLEAN_ADD.replace("STATUS: Confirmed", "STATUS: Decided")
        messages = self.messages(self.run_audit(**{"ARCHITECTURE.md": text}))
        self.assertTrue(any("not in vocabulary" in m for m in messages))

    def test_log_index_and_entries_must_agree(self):
        text = CLEAN_LOG.replace("| D-002 | 2026-09-26 | Database, revised | Confirmed | |\n", "")
        messages = self.messages(self.run_audit(**{"DECISION-LOG.md": text}))
        self.assertIn("D-002 has an entry but no index row", messages)

    def test_superseded_links_must_go_both_ways(self):
        text = CLEAN_LOG.replace("Supersedes D-001.", "Revised choice.")
        messages = self.messages(self.run_audit(**{"DECISION-LOG.md": text}))
        self.assertIn("D-002 does not link back to D-001", messages)

    def test_unresolved_cross_reference_is_found(self):
        edd = CLEAN_EDD.replace("ADD section 8.4", "ADD section 9.2")
        messages = self.messages(self.run_audit(**{"ARCHITECTURE.md": CLEAN_ADD, "ENGINEERING.md": edd}))
        self.assertIn("ADD section 9.2 does not exist", messages)

    def test_in_interview_needs_a_state_block(self):
        text = CLEAN_ADD.replace("Status: Audited.", "Status: In interview.")
        messages = self.messages(self.run_audit(**{"ARCHITECTURE.md": text}))
        self.assertIn("Status is In interview but no INTERVIEW STATE block", messages)
        with_block = text + "\nINTERVIEW STATE\nLast completed: Phase 2, section 8\n"
        self.assertNotIn("Status is In interview but no INTERVIEW STATE block", self.messages(self.run_audit(**{"ARCHITECTURE.md": with_block})))

    def test_only_kit_documents_are_audited_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_docs(Path(tmp) / "docs", **{"ARCHITECTURE.md": CLEAN_ADD, "white-paper.md": "A powerful vision — no version line."})
            self.assertEqual([], kit_audit.audit(root))
            self.assertTrue(any(f["file"] == "white-paper.md" for f in kit_audit.audit(root, everything=True)))

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_docs(Path(tmp) / "docs", **{"ARCHITECTURE.md": CLEAN_ADD})
            self.assertEqual(0, kit_audit.main(["--docs", str(root), "--json"]))
            (root / "ARCHITECTURE.md").write_text(CLEAN_ADD + "\nseamless\n", encoding="utf-8")
            self.assertEqual(1, kit_audit.main(["--docs", str(root)]))
            self.assertEqual(2, kit_audit.main(["--docs", str(Path(tmp) / "missing")]))


if __name__ == "__main__":
    unittest.main()
