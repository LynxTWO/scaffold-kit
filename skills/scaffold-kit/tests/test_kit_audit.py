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

    def test_acceptance_table_header_compatibility(self):
        for header in ("Verified by", "How to check", "How it will be checked"):
            with self.subTest(header=header):
                text = CLEAN_SLICE.replace("Verified by", header)
                files = ready_docs()
                files["SLICE-001-demo.md"] = text
                self.assertEqual([], self.run_ready(files))
                for placeholder in ("[test]", "TODO", ""):
                    files["SLICE-001-demo.md"] = text.replace("Run demo with example input", placeholder)
                    self.assertEqual(["S-001 How it will be checked is empty or a placeholder"],
                                     self.messages(self.run_ready(files)), placeholder)
                files["SLICE-001-demo.md"] = text.replace(" | manual:", " | extra | manual:")
                self.assertEqual(["S-001 needs ID, Requirement, Criterion, How it will be checked, Gate columns"],
                                 self.messages(self.run_ready(files)))

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

    def test_ready_accepts_linked_or_described_pointer(self):
        for pointer in ("[SLICE-001-demo.md](SLICE-001-demo.md)", "[`SLICE-001-demo.md`](./SLICE-001-demo.md)",
                        "SLICE-001-demo.md: print the result", "`SLICE-001-demo.md`."):
            files = ready_docs()
            files["ARCHITECTURE.md"] = READY_ADD.replace("SLICE-001-demo.md", pointer)
            self.assertEqual([], self.run_ready(files), pointer)
        for pointer in ("[SLICE-001-demo.md](SLICE-002-other.md)", "SLICE-001-demo.md.bak", "[SLICE-NNN-name.md] [description]"):
            files = ready_docs()
            files["ARCHITECTURE.md"] = READY_ADD.replace("SLICE-001-demo.md", pointer)
            self.assertTrue(any("must name one Current slice" in m for m in self.messages(self.run_ready(files))), pointer)

    def test_ready_rejects_another_active_or_completed_current_slice(self):
        files = ready_docs()
        files["SLICE-002-other.md"] = CLEAN_SLICE.replace("Proposed.", "In progress.")
        self.assertIn("another slice is active", self.messages(self.run_ready(files)))
        for done in ("Done with evidence.", "Done."):
            files = ready_docs()
            files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Proposed.", done)
            self.assertIn("completed slice cannot be the current build boundary", self.messages(self.run_ready(files)))

    def test_ready_approved_status_needs_a_named_approver(self):
        for status in ("Approved for build.", "In progress."):
            for footer in ("", "\n*Approved for build by: [name], [date], brief version [version].*\n",
                           "\nApproved for build by: pending.\n", "\n```\nApproved for build by: Sam, 2026-10-12\n```\n"):
                files = ready_docs()
                files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Proposed.", status) + footer
                self.assertTrue(any("needs 'Approved for build by:'" in m for m in self.messages(self.run_ready(files))), footer)
            files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Proposed.", status) + "\n*Approved for build by: Sam Owner, 2026-10-12, brief version 0.1.*\n"
            self.assertEqual([], self.run_ready(files))

    def test_approval_value_is_read_from_its_own_line(self):
        rejected = (
            "Approved for build by: TODO", "Approved for build by: N/A", "Approved for build by: not approved",
            "Approved for build by: Not yet approved, 2026-10-12", "Approved for build by: pending, 2026-10-12",
            "Approved for build by:\n\n## Next action\nReview scope.", "Approved for build by: Sam Owner",
            "Approved for build by: 2026-10-12", "Approved for build by: N/A, 2026-10-12",
            "Approved for build by: <name>, <date>", "Approved for build by: Sam Owner, [date]",
            "Nothing is built until this reads `Approved for build by: Sam Owner, 2026-10-12`.",
        )
        accepted = (
            "*Approved for build by: Sam Owner, 2026-10-12, brief version 0.1.*",
            "**Approved for build by:** Sam Owner, 12 October 2026",
            "Approved for build by: Sam Owner on Oct 12, 2026",
            "Approved for build by: Noah Na, 10/12/2026\r",
            "*Approved for build by: Dan, 2026-10-01. Until then, this brief is a proposal, and no implementation starts.*",
        )
        for line in rejected + accepted:
            self.assertEqual(line in accepted, kit_audit.approval_recorded("Version: 0.1\n\n" + line + "\n"), line)
        files = ready_docs()
        files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Proposed.", "In progress.") + "\nApproved for build by: TODO\n"
        self.assertTrue(any("followed by a name and date" in m for m in self.messages(self.run_ready(files))))
        files = ready_docs()
        files["SLICE-000-old.md"] = CLEAN_SLICE.replace("Proposed.", "Done.")
        self.assertEqual([], self.run_ready(files))

    def test_approval_must_name_the_current_brief_version(self):
        approved = CLEAN_SLICE.replace("Proposed.", "Approved for build.")
        footer = "\n*Approved for build by: Sam Owner, 2026-10-12, brief version 0.1.*\n"
        files = ready_docs()
        files["SLICE-001-demo.md"] = approved.replace("Version: 0.1", "Version: 0.2") + footer
        self.assertIn("approval names brief version 0.1 but the brief is version 0.2", self.messages(self.run_ready(files)))
        for text in (approved + footer, approved + "\nApproved for build by: Sam Owner, 2026-10-12\n"):
            files["SLICE-001-demo.md"] = text
            self.assertEqual([], self.run_ready(files))

    def test_slice_status_vocabulary(self):
        # "Done" is the earlier 0.4 footer's wording, so historical briefs stay valid.
        for status in ("Proposed", "Approved for build", "In progress", "Done with evidence", "Done"):
            self.assertEqual([], self.run_audit(**{"SLICE-001-demo.md": CLEAN_SLICE.replace("Proposed", status)}))
        self.assertTrue(any("invalid slice status" in m for m in self.messages(self.run_audit(**{
            "SLICE-001-demo.md": CLEAN_SLICE.replace("Proposed", "Finished")}))))

    def test_guided_check_inspects_generated_prose_not_setting(self):
        # Excerpts from the failing generated version brief, with guided already set.
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n\n## 4. Modules\n"
        docs["SLICE-001-demo.md"] = docs["SLICE-001-demo.md"].replace("record stdout", "record printed text")
        docs["SLICE-001-demo.md"] += "\n# Demo CLI\nUse the one-script seam in ADD 4. EDD 11 bounds verification.\n"
        for ready in (False, True):
            with tempfile.TemporaryDirectory() as tmp:
                root = write_docs(Path(tmp), **docs)
                errors = [f for f in kit_audit.audit(root, ready=ready) if f["check"] == "guided-label"]
                self.assertEqual(3, len(errors))
        docs["SLICE-001-demo.md"] += "\nArchitecture Document ([ADD](ARCHITECTURE.md)); [EDD](ENGINEERING.md), the Engineering Document; command-line tool (CLI).\n"
        self.assertEqual([], self.run_ready(docs))

    def test_guided_labels_preserve_alias_expert_and_history(self):
        docs = ready_docs()
        docs["SLICE-001-demo.md"] = docs["SLICE-001-demo.md"].replace("record stdout", "record printed text")
        docs["SLICE-001-demo.md"] += "\nDemo CLI; ADD 4; EDD 11.\n"
        for setting, status, count in (("Interview depth: guided", "Proposed", 3),
                                       ("Explanation depth: expert", "Proposed", 0),
                                       ("Explanation depth: guided", "Done with evidence", 0)):
            docs["ARCHITECTURE.md"] = READY_ADD + "\n" + setting + "\n"
            docs["SLICE-001-demo.md"] = docs["SLICE-001-demo.md"].replace("Proposed", status)
            self.assertEqual(count, len(kit_audit.check_guided_labels(docs)))

    def test_guided_label_markdown_boundaries(self):
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n"
        for prose, expected in (("Architecture Document\n(ADD); command-line tool\n(CLI).", 0),
                                ("Read [Plan][plan].\n\n[plan]: notes/ADD.md", 0),
                                ("Reengineering EDD is in scope.", 1)):
            docs["SLICE-001-demo.md"] = CLEAN_SLICE.replace("record stdout", "record printed text") + "\n" + prose
            self.assertEqual(expected, len(kit_audit.check_guided_labels(docs)), prose)

    def test_guided_check_rejects_observed_action_jargon(self):
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n"
        # Actual included-work excerpts from round18 and round19 generated briefs.
        docs["SLICE-001-demo.md"] = CLEAN_SLICE.replace("record stdout", "record printed text") + (
            "\nPlan argument dispatch and version lookup; preserve result rendering.\n"
            "\nThen add the version branch and its confirmed version source.\n"
            "\nCompare stdout, stderr and exit code to baseline.\n")
        self.assertEqual(6, len(kit_audit.check_guided_labels(docs)))
        docs["SLICE-001-demo.md"] += (
            "\nDispatch handles arguments; rendering prints result text.\n"
            "\nThe version branch is the path that handles the version request.\n"
            "\nPrinted text is stdout; error text is stderr.\n"
            "\nExit code is the success or failure number.\n")
        self.assertEqual([], kit_audit.check_guided_labels(docs))
        for prose in ("Dispatch means handling command arguments.",
                      "Dispatch means handling the command-line arguments.",
                      "Rendering means printing the result text.",
                      "Dispatch means handling arguments.",
                      "Rendering means preparing output.",
                      "Rendering means formatting output.",
                      "Printed text is STDOUT; error text is STDERR.",
                      "stdout is the text printed by the command.",
                      "stderr is the text printed for errors."):
            docs["SLICE-001-demo.md"] = CLEAN_SLICE.replace("record stdout", "record printed text") + "\n" + prose
            self.assertEqual([], kit_audit.check_guided_labels(docs), prose)
        docs["SLICE-001-demo.md"] = CLEAN_SLICE.replace("record stdout", "record printed text") + (
            "\nAdd the version request; preserve ordinary result output.\n"
            "\nCompare printed text, error text and exit code.\n")
        self.assertEqual(1, len(kit_audit.check_guided_labels(docs)))
        docs["SLICE-001-demo.md"] += "\nExit code is the success or failure number.\n"
        self.assertEqual([], kit_audit.check_guided_labels(docs))

    def test_guided_check_rejects_observed_remaining_terms(self):
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n"
        base = CLEAN_SLICE.replace("record stdout", "record printed text")
        # Concrete terms in the three failed round20 generated briefs.
        docs["SLICE-001-demo.md"] = base + "\nNo stubs. A constant is proposed. What output contract? Compare both output streams; check a source-read failure.\n"
        self.assertEqual(5, len(kit_audit.check_guided_labels(docs)))
        for prose in (
            "Stubs are temporary substitutes.",
            "A constant is a fixed value stored in code.",
            "The output contract sets rules for printed text and command results.",
            "Output streams are normal and error output.",
            "A source-read failure means unable to read the version value.",
        ):
            docs["SLICE-001-demo.md"] = base + "\n" + prose
            self.assertEqual([], kit_audit.check_guided_labels(docs), prose)

    def test_copied_recommendation_remains_in_decision_log(self):
        text = CLEAN_SLICE + "\nA constant is recommended; alternative paths remain in D-002.\n"
        self.assertEqual(1, len(kit_audit.check_brief_recommendations("SLICE-001-demo.md", text)))
        text = CLEAN_SLICE + "\nVersion source needs the owner's answer in D-002.\n"
        self.assertEqual([], kit_audit.check_brief_recommendations("SLICE-001-demo.md", text))
        for prose in ("This is not recommended.", "The file is `recommended.py`.",
                      "Read [D-002](DECISION-LOG.md#is-recommended).",
                      "Read [choice][d].\n\n[d]: DECISION-LOG.md#is-recommended"):
            self.assertEqual([], kit_audit.check_brief_recommendations("SLICE-001-demo.md", CLEAN_SLICE + "\n" + prose), prose)
        text = text.replace("Proposed", "Done with evidence") + "\nA constant is recommended.\n"
        self.assertEqual([], kit_audit.check_brief_recommendations("SLICE-001-demo.md", text))
        for depth in ("guided", "expert"):
            docs = ready_docs()
            docs["ARCHITECTURE.md"] += "\nExplanation depth: " + depth + "\n"
            docs["SLICE-001-demo.md"] = CLEAN_SLICE.replace("record stdout", "record printed text") + "\nA constant (fixed value stored in code) is recommended.\n"
            findings = self.run_ready(docs)
            self.assertEqual(["decision-copy"], [f["check"] for f in findings], depth)

    def test_new_brief_checks_preserve_markdown_and_lines(self):
        base = CLEAN_SLICE.replace("record stdout", "record printed text")
        for gap in (" ", "  ", "\n", "\t"):
            errors = kit_audit.check_brief_recommendations("SLICE-001-demo.md", base + "\nA value is" + gap + "recommended.")
            self.assertEqual(1, len(errors), gap)
        for prose in ('[choice](DECISION-LOG.md#version(source) "is recommended")',
                      '[choice][d]\n\n[d]: DECISION-LOG.md\n  "is recommended"',
                      '`is recommended.txt`'):
            self.assertEqual([], kit_audit.check_brief_recommendations("SLICE-001-demo.md", base + "\n" + prose), prose)
        text = base + "\n[choice](\nDECISION-LOG.md\n)\nA value is recommended.\n"
        self.assertEqual(text[:text.index("A value is recommended")].count("\n") + 1,
                         kit_audit.check_brief_recommendations("SLICE-001-demo.md", text)[0]["line"])
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n"
        for prose in ('[choice](notes/x(v)/constant.md)', '`constant.py`',
                      '[ADD](\nARCHITECTURE.md\n) is the Architecture Document.',
                      'Output contract means an agreement on printed results.'):
            docs["SLICE-001-demo.md"] = base + "\n" + prose
            self.assertEqual([], kit_audit.check_guided_labels(docs), prose)

    def test_guided_scale_label_in_generated_footer(self):
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n"
        base = CLEAN_SLICE.replace("record stdout", "record printed text")
        # Actual failed round21 footer; the configured scale alone is insufficient.
        docs["SLICE-001-demo.md"] = base + "\nOmissions are recorded because this is a contained T1 change.\n"
        self.assertEqual(1, len(kit_audit.check_guided_labels(docs)))
        docs["SLICE-001-demo.md"] += "\nT1 means a prototype or personal tool.\n"
        self.assertEqual([], kit_audit.check_guided_labels(docs))
        docs["SLICE-001-demo.md"] = base + "\nOmissions are recorded because this is a small change.\n"
        self.assertEqual([], kit_audit.check_guided_labels(docs))

    def test_guided_generated_question_and_source_identity(self):
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n"
        base = CLEAN_SLICE.replace("record stdout", "record printed text")
        # Actual round22 miss: owner-question reference and reader-facing state.
        docs["SLICE-001-demo.md"] = base + "\nCompare Q-002 record and D-003.\n\n```text\nSLICE STATE\nSource checked: demo.py SHA-256 in linked evidence\n```\n"
        errors = kit_audit.check_guided_labels(docs)
        self.assertEqual(2, len(errors))
        self.assertEqual(2, len({error["line"] for error in errors}))
        docs["SLICE-001-demo.md"] += "\nQ identifies a question. SHA-256 is a file fingerprint.\n"
        self.assertEqual([], kit_audit.check_guided_labels(docs))
        docs["SLICE-001-demo.md"] = base + "\n```python\nQ = 'SHA-256'\n```\n"
        self.assertEqual([], kit_audit.check_guided_labels(docs))
        docs["ARCHITECTURE.md"] = docs["ARCHITECTURE.md"].replace("depth: guided", "depth: expert")
        docs["SLICE-001-demo.md"] += "\nCompare Q-002.\n"
        self.assertEqual([], kit_audit.check_guided_labels(docs))

    def test_guided_state_uses_existing_fence_regions(self):
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n"
        base = CLEAN_SLICE.replace("record stdout", "record printed text")
        cases = [
            ("````python\n```text\nSLICE STATE\nSource checked: SHA-256; Q-002\n```\n````\n", 0),
            ("~~~python\n```text\nSLICE STATE\nSource checked: SHA-256; Q-002\n```\n~~~\n", 0),
            ("   ```text\nSLICE STATE\nSource checked: SHA-256; Q-002\n   ```\n", 2),
            ("~~~text\nSLICE STATE\nSource checked: SHA-256; Q-002\n~~~\n", 2),
            ("````text\nSLICE STATE\n```\nSource checked: SHA-256; Q-002\n````\n", 2),
        ]
        for prose, count in cases:
            for newline in ("\n", "\r\n"):
                docs["SLICE-001-demo.md"] = (base + "\n" + prose).replace("\n", newline)
                self.assertEqual(count, len(kit_audit.check_guided_labels(docs)), prose)

    def test_guided_generated_revision_and_exit_numbers(self):
        docs = ready_docs()
        docs["ARCHITECTURE.md"] += "\nExplanation depth: guided\n"
        base = CLEAN_SLICE.replace("record stdout", "record printed text")
        # Actual round24 state/acceptance wording, not just configured depth.
        for term in ("exit code", "exit result", "exit status", "exit 0"):
            docs["SLICE-001-demo.md"] = base + "\n```text\nSLICE STATE\nSource checked: local HEAD f51e0f4\n```\n\nCompare printed text and " + term + ".\n"
            self.assertEqual(2, len(kit_audit.check_guided_labels(docs)))
            docs["SLICE-001-demo.md"] += "\nHEAD is the current source revision. The " + term + " is a success or failure number; 0 means success.\n"
            self.assertEqual([], kit_audit.check_guided_labels(docs))
        # Approved Sample B explains its numeric result in an ordinary clause.
        docs["SLICE-001-demo.md"] = base + "\nRefuses to overwrite and exits with code 2 (reports failure).\n\nRecord output and exit code.\n"
        self.assertEqual([], kit_audit.check_guided_labels(docs))

    def test_explicit_structural_omissions(self):
        # Predicate excerpts from all four round12 failed active briefs.
        combined = "Sections 2, 5, 7 and 9 through 12 and unused tables are omitted because this is one prose edit."
        for extra in ("the exclusion/connection table is omitted.", "No future-work table is needed.",
                      "no future connection table is needed.", "no exclusion/connection table is needed."):
            text = CLEAN_SLICE + "\n" + extra + "\n" + combined
            errors = self.run_audit(**{"SLICE-001-demo.md": text})
            self.assertEqual(["omissions"], [f["check"] for f in errors], extra)
            self.assertEqual(len(text.splitlines()), errors[0]["line"])
        ignored = "No stubs are needed. No test harness is needed. No table changes are needed. Review sections 2 and 5; optional flags are omitted."
        for body in (combined, combined.replace("unused", "milestone"), ignored, extra[:-1] + "; " + combined,
                     "## " + extra + "\n~~~\n" + extra + "\n~~~\n" + combined):
            self.assertEqual([], self.run_audit(**{"SLICE-001-demo.md": CLEAN_SLICE + "\n" + body}))
        for status in kit_audit.COMPLETED_SLICE:
            self.assertEqual([], self.run_audit(**{"SLICE-000-old.md": CLEAN_SLICE.replace("Proposed", status) + extra + combined}))

    def test_ready_requires_acceptance_and_confirmed_requirement_binding(self):
        for old, new, expected in (
            ("R-001 | Given", "R-999 | Given", "must reference confirmed R-IDs"),
            ("R-001 | Given", " | Given", "must reference confirmed R-IDs"),
            ("Run demo with example input", "[test]", "How it will be checked is empty or a placeholder"),
            ("manual: record stdout in the slice evidence", "", "Gate is empty or a placeholder"),
        ):
            files = ready_docs()
            files["SLICE-001-demo.md"] = CLEAN_SLICE.replace(old, new)
            self.assertTrue(any(expected in m for m in self.messages(self.run_ready(files))))
        files = ready_docs()
        files["SLICE-001-demo.md"] = CLEAN_SLICE.split("| S-001")[0]
        self.assertIn("section 8 needs acceptance rows with S-IDs", self.messages(self.run_ready(files)))

    def test_ready_rejects_placeholder_words_and_duplicate_requirements(self):
        for old, label in (("Run demo with example input", "How it will be checked"),
                           ("manual: record stdout in the slice evidence", "Gate"),
                           ("Given a valid input, the result is printed", "Criterion")):
            for word in ("TBD", "pending", "N/A", "manual:", "-", "**TODO**"):
                files = ready_docs()
                files["SLICE-001-demo.md"] = CLEAN_SLICE.replace(old, word)
                self.assertIn(f"S-001 {label} is empty or a placeholder", self.messages(self.run_ready(files)), word)
        files = ready_docs()
        files["SLICE-001-demo.md"] = CLEAN_SLICE.replace("Given a valid input", "None of the valid inputs fail; given one")
        self.assertEqual([], self.run_ready(files))
        row = "| R-001 | Print the result | Result is visible |"
        files["ENGINEERING.md"] = READY_EDD.replace(row, row + "\n" + row)
        self.assertIn("duplicate requirement ID: R-001", self.messages(self.run_ready(files)))

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
        self.assertIn("S-001 How it will be checked is empty or a placeholder", self.messages(self.run_ready(files)))

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
