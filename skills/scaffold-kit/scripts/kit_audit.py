#!/usr/bin/env python3
"""Mechanical audit for Scaffold Kit documents.

Checks what a polite reread misses: banned punctuation and words, a status on
every decision block and log entry, index and entries in agreement, superseded
links in both directions, section cross-references that resolve, and a state
block while a document is still in interview. Standard library only.

Usage: python3 kit_audit.py --docs docs [--json]
Exit codes: 0 no findings, 1 findings, 2 usage or read error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STATUSES = ("Confirmed", "Proposed", "Assumed", "Open", "Deferred", "Superseded")
BANNED_WORDS = (
    "robust", "seamless", "cutting-edge", "powerful", "world-class", "blazing",
    "game-changing", "captures", "implies", "reframes", "strips", "weaponize",
    "the exact", "delve",
)
FILLER_OPENERS = ("it is worth noting", "in today's fast-paced world", "as we all know")
DOC_ROLES = {"ARCHITECTURE.md": "ADD", "ENGINEERING.md": "EDD"}


KIT_DOCS = ("ARCHITECTURE.md", "ENGINEERING.md", "DECISION-LOG.md")


def is_kit_doc(name: str) -> bool:
    return name in KIT_DOCS or (name.startswith("SLICE-") and name.endswith(".md"))


def read_docs(root: Path, everything: bool = False) -> dict[str, str]:
    """The kit's own documents by default; --all widens to every Markdown file in the directory."""
    docs = {}
    for path in sorted(root.glob("*.md")):
        if everything or is_kit_doc(path.name):
            docs[path.name] = path.read_text(encoding="utf-8")
    return docs


def strip_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def check_hygiene(name: str, text: str) -> list[dict]:
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        if "—" in line or "–" in line:
            findings.append({"check": "hygiene", "file": name, "line": number, "message": "em or en dash"})
        lowered = line.lower()
        for word in BANNED_WORDS:
            if re.search(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", lowered):
                findings.append({"check": "hygiene", "file": name, "line": number, "message": f"banned word: {word}"})
        for opener in FILLER_OPENERS:
            if opener in lowered:
                findings.append({"check": "hygiene", "file": name, "line": number, "message": f"filler opener: {opener}"})
    return findings


def check_decision_blocks(name: str, text: str) -> list[dict]:
    """Every DECISION: line is followed within six lines by a STATUS: line from the vocabulary."""
    findings = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not re.match(r"\s*DECISION:\s*\S", line):
            continue
        window = lines[index + 1:index + 7]
        status = next((w for w in window if re.match(r"\s*STATUS:", w)), None)
        if status is None:
            findings.append({"check": "decision-block", "file": name, "line": index + 1, "message": "DECISION without STATUS within six lines"})
            continue
        value = status.split(":", 1)[1].strip()
        if value not in STATUSES:
            findings.append({"check": "decision-block", "file": name, "line": index + 1, "message": f"STATUS not in vocabulary: {value!r}"})
    return findings


def check_decision_log(name: str, text: str) -> list[dict]:
    findings = []
    body = strip_fences(text)
    entries = {}
    for match in re.finditer(r"^## (D-\d+):", body, re.M):
        entry_id = match.group(1)
        start = match.end()
        next_heading = re.search(r"^## ", body[start:], re.M)
        section = body[start:start + next_heading.start()] if next_heading else body[start:]
        entries[entry_id] = section
        status = re.search(r"^Status:\s*(.+)$", section, re.M)
        if not status:
            findings.append({"check": "decision-log", "file": name, "line": body[:match.start()].count("\n") + 1, "message": f"{entry_id} has no Status line"})
        elif status.group(1).strip() not in STATUSES:
            findings.append({"check": "decision-log", "file": name, "line": body[:match.start()].count("\n") + 1, "message": f"{entry_id} status not in vocabulary: {status.group(1).strip()!r}"})
    index_rows = {}
    for match in re.finditer(r"^\|\s*(D-\d+)\s*\|[^|]*\|[^|]*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$", body, re.M):
        index_rows[match.group(1)] = (match.group(2).strip(), match.group(3).strip())
    example_ids = {"D-000", "D-[number]"}
    for entry_id in entries:
        if entry_id not in index_rows and entry_id not in example_ids:
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} has an entry but no index row"})
    for entry_id, (status, superseded_by) in index_rows.items():
        if entry_id not in entries and entry_id not in example_ids:
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} has an index row but no entry"})
        if status and status not in STATUSES and status != "[status]":
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} index status not in vocabulary: {status!r}"})
        if superseded_by and superseded_by not in ("[blank or ID]", ""):
            if superseded_by not in entries:
                findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} superseded by {superseded_by}, which has no entry"})
            elif entry_id not in entries[superseded_by]:
                findings.append({"check": "decision-log", "file": name, "message": f"{superseded_by} does not link back to {entry_id}"})
            if entry_id in entries and status != "Superseded":
                findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} is superseded but its index status is {status!r}"})
    return findings


def heading_numbers(text: str) -> set[str]:
    numbers = set()
    for match in re.finditer(r"^#{2,3}\s+(\d+(?:\.\d+)?)[.\s]", text, re.M):
        numbers.add(match.group(1))
    return numbers


def check_cross_references(docs: dict[str, str]) -> list[dict]:
    findings = []
    targets = {role: heading_numbers(docs[file]) for file, role in DOC_ROLES.items() if file in docs}
    for name, text in docs.items():
        for match in re.finditer(r"\b(ADD|EDD)\s+(?:section\s+)?(\d+(?:\.\d+)?)\b", strip_fences(text)):
            role, number = match.group(1), match.group(2)
            if role not in targets:
                continue
            base = number.split(".")[0]
            if number not in targets[role] and base not in targets[role]:
                line = text[:match.start()].count("\n") + 1
                findings.append({"check": "cross-reference", "file": name, "line": line, "message": f"{role} section {number} does not exist"})
    return findings


def check_state_and_version(name: str, text: str) -> list[dict]:
    findings = []
    if not re.search(r"^Version:\s*\S", text, re.M) and not re.search(r"^Version \d", text, re.M):
        findings.append({"check": "version", "file": name, "message": "no Version line"})
    if re.search(r"Status:\s*In interview", text) and "INTERVIEW STATE" not in text:
        findings.append({"check": "state-block", "file": name, "message": "Status is In interview but no INTERVIEW STATE block"})
    return findings


def audit(root: Path, everything: bool = False) -> list[dict]:
    docs = read_docs(root, everything)
    findings: list[dict] = []
    for name, text in docs.items():
        findings.extend(check_hygiene(name, text))
        findings.extend(check_state_and_version(name, text))
        if name in DOC_ROLES or name.startswith("SLICE-"):
            findings.extend(check_decision_blocks(name, text))
        if name == "DECISION-LOG.md":
            findings.extend(check_decision_log(name, text))
    findings.extend(check_cross_references(docs))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Mechanical audit for Scaffold Kit documents.")
    parser.add_argument("--docs", default="docs", help="directory holding ARCHITECTURE.md, ENGINEERING.md, DECISION-LOG.md and SLICE-*.md")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--all", action="store_true", help="audit every Markdown file in the directory, not only the kit's documents")
    args = parser.parse_args(argv)
    root = Path(args.docs)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    audited = sorted(read_docs(root, args.all))
    findings = audit(root, args.all)
    if args.json:
        print(json.dumps({"docs": audited, "findings": findings}, indent=2))
    else:
        for finding in findings:
            where = f"{finding['file']}:{finding['line']}" if "line" in finding else finding["file"]
            print(f"{finding['check']}: {where}: {finding['message']}")
        print(f"{len(findings)} finding(s) across {len(audited)} document(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
