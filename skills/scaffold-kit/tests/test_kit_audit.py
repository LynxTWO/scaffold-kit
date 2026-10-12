"""Each check must catch its violation and pass a clean document set."""
import importlib.util
import contextlib
import io
import json
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

READY_ADD = CLEAN_ADD.replace("See SLICE-001.", "- **Current slice:** SLICE-001-demo.md")
READY_EDD = CLEAN_EDD + """
## 4. Requirements Ledger

### 4.1 Confirmed requirements
| ID | Requirement | Acceptance test |
|---|---|---|
| R-001 | Print the result | Result is visible |

### 4.2 Assumed requirements
"""
CLEAN_SLICE = """# Demo Slice

Version: 0.1 Draft. Date: 2026-10-12. Status: Proposed.

## 8. Acceptance criteria

| ID | Requirement | Criterion | Verified by | Gate |
|---|---|---|---|---|
| S-001 | R-001 | Given a valid input, the result is printed | Run demo with example input | manual: record stdout in the slice evidence |

## 9. Verification evidence required
"""


def ready_docs():
    return {"ARCHITECTURE.md": READY_ADD, "ENGINEERING.md": READY_EDD,
            "DECISION-LOG.md": CLEAN_LOG, "SLICE-001-demo.md": CLEAN_SLICE}


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

    def run_ready(self, files=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_docs(Path(tmp) / "docs", **(ready_docs() if files is None else files))
            return kit_audit.audit(root, ready=True)

    def test_empty_and_unselected_directories_fail(self):
        for files in ({}, {"README.md": "Notes"}):
            with self.subTest(files=files):
                self.assertIn("no selected documents", self.messages(self.run_audit(**files)))

    def test_ready_companions_required_but_partial_remains_available(self):
        files = {"ARCHITECTURE.md": READY_ADD}
        self.assertEqual([], self.run_audit(**files))
        messages = self.messages(self.run_ready(files))
        self.assertEqual(2, messages.count("required companion document is missing"))

    def test_clean_readiness_can_use_recorded_manual_check(self):
        self.assertEqual([], self.run_ready())

    def test_ready_rejects_interview_and_missing_active_file(self):
        files = ready_docs()
        files["ENGINEERING.md"] = READY_EDD.replace("Audited.", "In interview.") + "\nINTERVIEW STATE\n"
        del files["SLICE-001-demo.md"]
        messages = self.messages(self.run_ready(files))
        self.assertIn("still in interview", messages)
        self.assertIn("active slice file is missing", messages)

    def test_ready_rejects_missing_ambiguous_and_traversing_pointer(self):
        for pointer in ("", "SLICE-001-demo.md\n- **Current slice:** SLICE-002-other.md", "../SLICE-001-demo.md"):
            files = ready_docs()
            files["ARCHITECTURE.md"] = READY_ADD.replace("SLICE-001-demo.md", pointer)
            self.assertTrue(any("must name one Current slice" in m for m in self.messages(self.run_ready(files))))

    def test_ready_rejects_another_active_or_completed_current_slice(self):
        files = ready_docs()
        files["SLICE-002-other.md"] = CLEAN_SLICE.replace("Proposed.", "In progress.")
        self.assertIn("another slice is active", self.messages(self.run_ready(files)))
        files = ready_docs()
        files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Proposed.", "Done with evidence.")
        self.assertIn("completed slice cannot be the current build boundary", self.messages(self.run_ready(files)))

    def test_slice_status_vocabulary(self):
        for status in ("Proposed", "Approved for build", "In progress", "Done with evidence"):
            self.assertEqual([], self.run_audit(**{"SLICE-001-demo.md": CLEAN_SLICE.replace("Proposed", status)}))
        self.assertTrue(any("invalid slice status" in m for m in self.messages(self.run_audit(**{
            "SLICE-001-demo.md": CLEAN_SLICE.replace("Proposed", "Done")}))))

    def test_ready_requires_acceptance_and_confirmed_requirement_binding(self):
        for old, new, expected in (
            ("R-001 | Given", "R-999 | Given", "must reference confirmed R-IDs"),
            ("R-001 | Given", " | Given", "must reference confirmed R-IDs"),
            ("Run demo with example input", "[test]", "Verified by is empty or a placeholder"),
            ("manual: record stdout in the slice evidence", "", "Gate is empty or a placeholder"),
        ):
            files = ready_docs()
            files["SLICE-001-demo.md"] = CLEAN_SLICE.replace(old, new)
            self.assertTrue(any(expected in m for m in self.messages(self.run_ready(files))))
        files = ready_docs()
        files["SLICE-001-demo.md"] = CLEAN_SLICE.split("| S-001")[0]
        self.assertIn("section 8 needs acceptance rows with S-IDs", self.messages(self.run_ready(files)))

    def test_ready_rejects_duplicate_acceptance_ids_and_old_table_shape(self):
        files = ready_docs()
        row = next(line for line in CLEAN_SLICE.splitlines() if line.startswith("| S-001"))
        files["SLICE-001-demo.md"] = CLEAN_SLICE.replace(row, row + "\n" + row)
        self.assertIn("duplicate acceptance ID: S-001", self.messages(self.run_ready(files)))
        files["SLICE-001-demo.md"] = CLEAN_SLICE.replace(" R-001 |", "")
        self.assertTrue(any("needs ID, Requirement" in m for m in self.messages(self.run_ready(files))))

    def test_ready_missing_reference_document_is_reported(self):
        partial = {"ENGINEERING.md": CLEAN_EDD}
        self.assertEqual([], self.run_audit(**partial))
        self.assertIn("ADD document is missing", self.messages(self.run_ready(partial)))

    def test_subsection_must_exist_even_when_parent_exists(self):
        files = {"ARCHITECTURE.md": CLEAN_ADD, "ENGINEERING.md": CLEAN_EDD.replace("8.4", "8.99")}
        self.assertIn("ADD section 8.99 does not exist", self.messages(self.run_audit(**files)))

    def test_nested_sections_and_fenced_fake_headings(self):
        add = CLEAN_ADD + "\n#### 8.4.1 Constraint\n\n```\n### 8.99 Fake\n```\n"
        for target, clean in (("8.4.1", True), ("8.99", False)):
            messages = self.messages(self.run_audit(**{"ARCHITECTURE.md": add,
                "ENGINEERING.md": CLEAN_EDD.replace("8.4", target)}))
            self.assertEqual(clean, not messages)

    def test_status_disagreement_and_duplicate_ids_are_rejected(self):
        text = CLEAN_LOG.replace("Status: Confirmed", "Status: Open")
        self.assertIn("D-002 index and entry statuses disagree", self.messages(self.run_audit(**{"DECISION-LOG.md": text})))
        for suffix, expected in (
            ("\n## D-002: Duplicate\nStatus: Open\nSupersedes D-001.\n", "duplicate entry ID: D-002"),
            ("\n| D-002 | 2026-10-12 | Duplicate | Open | |\n", "duplicate index ID: D-002"),
        ):
            self.assertIn(expected, self.messages(self.run_audit(**{"DECISION-LOG.md": CLEAN_LOG + suffix})))

    def test_supersession_backlink_needs_whole_identifier(self):
        text = CLEAN_LOG.replace("Supersedes D-001.", "Supersedes D-0010.")
        self.assertIn("D-002 does not link back to D-001", self.messages(self.run_audit(**{"DECISION-LOG.md": text})))

    def test_read_errors_have_usage_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ARCHITECTURE.md").write_bytes(b"\xff")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(2, kit_audit.main(["--docs", str(root)]))

    def test_ready_cli_reports_mode_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_docs(Path(tmp) / "docs", **ready_docs())
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, kit_audit.main(["--docs", str(root), "--ready", "--json"]))
            self.assertEqual("ready", json.loads(output.getvalue())["mode"])
            (root / "DECISION-LOG.md").unlink()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, kit_audit.main(["--docs", str(root), "--ready"]))

    def test_each_decision_owns_exactly_one_nearby_status(self):
        for block, expected in (
            ("DECISION: Missing\nDECISION: Next\nSTATUS: Confirmed", "DECISION without STATUS"),
            ("DECISION: Duplicate\nSTATUS: Confirmed\nSTATUS: Open", "exactly one STATUS"),
            ("DECISION: Missing\n## Next section\nSTATUS: Confirmed", "DECISION without STATUS"),
        ):
            messages = self.messages(self.run_audit(**{"ARCHITECTURE.md": "Version: 0.1\n" + block}))
            self.assertTrue(any(expected in m for m in messages))

    def test_log_needs_one_status_and_superseded_replacement_links(self):
        for text, expected in (
            (CLEAN_LOG.replace("Status: Confirmed", "Status: Confirmed\nStatus: Open"), "exactly one Status line"),
            (CLEAN_LOG.replace("| Superseded | D-002 |", "| Superseded | |"), "has no replacement"),
            (CLEAN_LOG.replace("Superseded by D-002.", "Revised."), "entry does not link to D-002"),
            (CLEAN_LOG.replace("| Superseded | D-002 |", "| Superseded | D-001 |"), "cannot supersede itself"),
        ):
            self.assertTrue(any(expected in m for m in self.messages(self.run_audit(**{"DECISION-LOG.md": text}))))

    def test_fenced_examples_do_not_supply_planning_structure(self):
        for opener, closer in (("~~~", "~~~"), ("````", "````"), ("```", "")):
            files = ready_docs()
            inner = "```\n" if opener != "```" else ""
            files["ARCHITECTURE.md"] = READY_ADD.replace("- **Current slice:** SLICE-001-demo.md",
                opener + "\n" + inner + "- **Current slice:** SLICE-001-demo.md\n" + closer)
            self.assertTrue(any("must name one Current slice" in m for m in self.messages(self.run_ready(files))))
        files = ready_docs()
        files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("| ID |", "~~~\n| ID |").replace("## 9.", "~~~\n## 9.")
        self.assertIn("section 8 needs acceptance rows with S-IDs", self.messages(self.run_ready(files)))
        add = CLEAN_ADD + "\n~~~\n### 8.99 Example\n~~~\n"
        self.assertIn("ADD section 8.99 does not exist", self.messages(self.run_audit(**{
            "ARCHITECTURE.md": add, "ENGINEERING.md": CLEAN_EDD.replace("8.4", "8.99")})))

    def test_brackets_in_concrete_checks_and_linked_placeholders(self):
        for check in ("pytest tests/test_demo.py::test_result[valid]", "Run `demo.py [valid]`", "[check result](result.md)",
                      "Run ``demo.py `[valid]` ``", "[check [valid]](result.md)", '[check](result.md "result [valid]")'):
            files = ready_docs()
            files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Run demo with example input", check)
            self.assertEqual([], self.run_ready(files))
        files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Run demo with example input", "[test or reproducible check] [result](result.md)")
        self.assertIn("S-001 Verified by is empty or a placeholder", self.messages(self.run_ready(files)))

    def test_decision_status_scan_stops_at_its_fence_boundary(self):
        text = """Version: 0.1
```text
DECISION: Output
STATUS: Confirmed
CHOICE: Print result
```

Diagnostic example:
```text
STATUS: Open
```
"""
        self.assertEqual([], self.run_audit(**{"ARCHITECTURE.md": text}))

    def test_escaped_pipes_are_table_content(self):
        log = CLEAN_LOG.replace("Database, revised |", r"Database \| cache, revised |")
        self.assertEqual([], self.run_audit(**{"DECISION-LOG.md": log}))
        files = ready_docs()
        files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Run demo with example input", r"python demo.py \| rg Result")
        self.assertEqual([], self.run_ready(files))

    def test_log_rows_cannot_span_lines_or_have_extra_columns(self):
        for row in (
            "| D-001 | 2026-09-26 | Database\n| Superseded | D-002 |",
            "| D-001 | 2026-09-26 | Read | write | Superseded | D-002 |",
        ):
            text = CLEAN_LOG.replace("| D-001 | 2026-09-26 | Database | Superseded | D-002 |", row)
            self.assertTrue(any("index row needs five columns" in m for m in self.messages(self.run_audit(**{"DECISION-LOG.md": text}))))

    def test_reference_location_after_fence_uses_original_line(self):
        edd = CLEAN_EDD + "\n```\n" + "example text\n" * 10 + "```\nADD section 8.99\n"
        findings = self.run_audit(**{"ARCHITECTURE.md": CLEAN_ADD, "ENGINEERING.md": edd})
        error = next(f for f in findings if "8.99" in f["message"])
        self.assertEqual(edd.splitlines().index("ADD section 8.99") + 1, error["line"])

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

    def test_crlf_documents_audit_the_same_as_lf(self):
        """A Windows checkout with autocrlf must not change findings."""
        lf = {"ARCHITECTURE.md": CLEAN_ADD, "ENGINEERING.md": CLEAN_EDD, "DECISION-LOG.md": CLEAN_LOG}
        crlf = {name: text.replace("\n", "\r\n") for name, text in lf.items()}
        self.assertEqual(self.run_audit(**lf), self.run_audit(**crlf))
        broken = dict(crlf); broken["DECISION-LOG.md"] = crlf["DECISION-LOG.md"].replace("Supersedes D-001.", "Revised choice.")
        self.assertIn("D-002 does not link back to D-001", self.messages(self.run_audit(**broken)))

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_docs(Path(tmp) / "docs", **{"ARCHITECTURE.md": CLEAN_ADD})
            self.assertEqual(0, kit_audit.main(["--docs", str(root), "--json"]))
            (root / "ARCHITECTURE.md").write_text(CLEAN_ADD + "\nseamless\n", encoding="utf-8")
            self.assertEqual(1, kit_audit.main(["--docs", str(root)]))
            self.assertEqual(2, kit_audit.main(["--docs", str(Path(tmp) / "missing")]))


if __name__ == "__main__":
    unittest.main()
