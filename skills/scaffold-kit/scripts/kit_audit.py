#!/usr/bin/env python3
"""Mechanical audit for Scaffold Kit documents.

Checks what a polite reread misses: banned punctuation and words, a status on
every decision block and log entry, index and entries in agreement, superseded
links in both directions, section cross-references that resolve, and a state
block while a document is still in interview. Standard library only.

Partial/interview audit: python3 kit_audit.py --docs docs [--json]
Build-readiness structure: add --ready. This cannot establish human approval,
semantic completeness, or passing implementation checks.
Exit codes: 0 no findings, 1 findings, 2 usage or read error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STATUSES = ("Confirmed", "Proposed", "Assumed", "Open", "Deferred", "Superseded")
SLICE_STATUSES = ("Proposed", "Approved for build", "In progress", "Done with evidence")
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


def fenced_lines(text: str):
    """Yield each line with its ordinary Markdown fence identity, if any."""
    fence = None
    region = None
    for index, line in enumerate(text.splitlines(keepends=True)):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)", line)
        current = region
        if fence is not None:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= fence[1] and not marker.group(2).strip():
                fence = None
                region = None
        elif marker and not (marker.group(1)[0] == "`" and "`" in marker.group(2)):
            fence = (marker.group(1)[0], len(marker.group(1)))
            region = current = index
        yield line, current


def strip_fences(text: str) -> str:
    """Mask fenced examples without changing character/line offsets."""
    return "".join(re.sub(r"[^\r\n]", " ", line) if region is not None else line
                   for line, region in fenced_lines(text))


def table_cells(line: str) -> list[str]:
    """Split the kit's pipe tables, retaining escaped pipes inside cells."""
    body = line.strip()
    cells, start, escapes = [], 0, 0
    for index, char in enumerate(body):
        if char == "|" and escapes % 2 == 0:
            cells.append(body[start:index].strip())
            start = index + 1
        escapes = escapes + 1 if char == "\\" else 0
    cells.append(body[start:].strip())
    return cells[1:-1] if body.startswith("|") and body.endswith("|") else cells


def has_placeholder(cell: str) -> bool:
    # Brackets in code (including parametrized test nodes) and Markdown links
    # are concrete text. Template placeholders stand alone or follow whitespace.
    prose = re.sub(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)", "", cell)

    def closing(start: int, opening: str, ending: str):
        depth, escapes = 0, 0
        for index in range(start, len(prose)):
            char = prose[index]
            if escapes % 2 == 0:
                depth += (char == opening) - (char == ending)
                if depth == 0:
                    return index
            escapes = escapes + 1 if char == "\\" else 0
        return None

    # Remove actual inline links, including nested labels and bracketed titles.
    index = 0
    while index < len(prose):
        if prose[index] == "[":
            label_end = closing(index, "[", "]")
            if label_end is not None and prose[label_end + 1:label_end + 2] == "(":
                link_end = closing(label_end + 1, "(", ")")
                if link_end is not None:
                    prose = prose[:index] + prose[link_end + 1:]
                    continue
        index += 1
    return bool(re.search(r"(?<![\w\\])\[(?![^\]]*\]\()[^\]\n]+\]", prose))


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
    """Each decision owns one status, within six lines and before the next block."""
    findings = []
    lines = text.splitlines()
    regions = [region for _, region in fenced_lines(text)]
    for index, line in enumerate(lines):
        if not re.match(r"\s*DECISION:\s*\S", line):
            continue
        end = next((i for i in range(index + 1, len(lines))
                    if regions[i] != regions[index] or re.match(r"\s*DECISION:|^#{1,6}\s", lines[i])), len(lines))
        statuses = [(i, lines[i]) for i in range(index + 1, end) if re.match(r"\s*STATUS:", lines[i])]
        if len(statuses) > 1:
            findings.append({"check": "decision-block", "file": name, "line": index + 1, "message": "DECISION must have exactly one STATUS"})
        if not statuses or statuses[0][0] > index + 6:
            findings.append({"check": "decision-block", "file": name, "line": index + 1, "message": "DECISION without STATUS within six lines"})
            continue
        value = statuses[0][1].split(":", 1)[1].strip()
        if value not in STATUSES:
            findings.append({"check": "decision-block", "file": name, "line": index + 1, "message": f"STATUS not in vocabulary: {value!r}"})
    return findings


def check_decision_log(name: str, text: str) -> list[dict]:
    findings = []
    body = strip_fences(text)
    entries = {}
    entry_statuses = {}
    for match in re.finditer(r"^## (D-\d+):", body, re.M):
        entry_id = match.group(1)
        start = match.end()
        next_heading = re.search(r"^## ", body[start:], re.M)
        section = body[start:start + next_heading.start()] if next_heading else body[start:]
        if entry_id in entries:
            findings.append({"check": "decision-log", "file": name, "message": f"duplicate entry ID: {entry_id}"})
            continue
        entries[entry_id] = section
        statuses = list(re.finditer(r"^Status:[ \t]*([^\n]*)$", section, re.M))
        status = statuses[0] if statuses else None
        if len(statuses) > 1:
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} must have exactly one Status line"})
        entry_statuses[entry_id] = status.group(1).strip() if status else None
        if not status:
            findings.append({"check": "decision-log", "file": name, "line": body[:match.start()].count("\n") + 1, "message": f"{entry_id} has no Status line"})
        elif status.group(1).strip() not in STATUSES:
            findings.append({"check": "decision-log", "file": name, "line": body[:match.start()].count("\n") + 1, "message": f"{entry_id} status not in vocabulary: {status.group(1).strip()!r}"})
    index_rows = {}
    for line in body.splitlines():
        if not re.match(r"^\|\s*D-\d+\s*\|", line):
            continue
        cells = table_cells(line)
        entry_id = cells[0]
        if len(cells) != 5:
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} index row needs five columns"})
            continue
        if entry_id in index_rows:
            findings.append({"check": "decision-log", "file": name, "message": f"duplicate index ID: {entry_id}"})
            continue
        index_rows[entry_id] = (cells[3], cells[4])
    example_ids = {"D-000", "D-[number]"}
    for entry_id in entries:
        if entry_id not in index_rows and entry_id not in example_ids:
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} has an entry but no index row"})
    for entry_id, (status, superseded_by) in index_rows.items():
        if entry_id not in entries and entry_id not in example_ids:
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} has an index row but no entry"})
        if status and status not in STATUSES and status != "[status]":
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} index status not in vocabulary: {status!r}"})
        if entry_id in entries and status != entry_statuses[entry_id]:
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} index and entry statuses disagree"})
        if status == "Superseded" and (not superseded_by or superseded_by == "[blank or ID]"):
            findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} is Superseded but has no replacement"})
        if superseded_by and superseded_by not in ("[blank or ID]", ""):
            if superseded_by == entry_id:
                findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} cannot supersede itself"})
            if entry_id in entries and not re.search(r"(?<![\w-])" + re.escape(superseded_by) + r"(?![\w-])", entries[entry_id]):
                findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} entry does not link to {superseded_by}"})
            if superseded_by not in entries:
                findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} superseded by {superseded_by}, which has no entry"})
            elif not re.search(r"(?<![\w-])" + re.escape(entry_id) + r"(?![\w-])", entries[superseded_by]):
                findings.append({"check": "decision-log", "file": name, "message": f"{superseded_by} does not link back to {entry_id}"})
            if entry_id in entries and status != "Superseded":
                findings.append({"check": "decision-log", "file": name, "message": f"{entry_id} is superseded but its index status is {status!r}"})
    return findings


def heading_numbers(text: str) -> set[str]:
    numbers = set()
    for match in re.finditer(r"^#{2,6}\s+(\d+(?:\.\d+)*)(?:\.?(?:\s|$))", strip_fences(text), re.M):
        numbers.add(match.group(1))
    return numbers


def check_cross_references(docs: dict[str, str], ready: bool = False) -> list[dict]:
    findings = []
    targets = {role: heading_numbers(docs[file]) for file, role in DOC_ROLES.items() if file in docs}
    for name, text in docs.items():
        for match in re.finditer(r"\b(ADD|EDD)\s+(?:section\s+)?(\d+(?:\.\d+)*)\b", strip_fences(text)):
            role, number = match.group(1), match.group(2)
            line = text[:match.start()].count("\n") + 1
            if role not in targets:
                if ready:
                    findings.append({"check": "cross-reference", "file": name, "line": line, "message": f"{role} document is missing"})
                continue
            if number not in targets[role]:
                findings.append({"check": "cross-reference", "file": name, "line": line, "message": f"{role} section {number} does not exist"})
    return findings


def slice_status(text: str) -> str | None:
    match = re.search(r"^(?:Version:[^\n]*?\s+)?Status:\s*([^\n]+)", text, re.M)
    return match.group(1).strip().removesuffix(".") if match else None


def section(text: str, number: str) -> str:
    """Numbered section including child headings, excluding fenced examples."""
    body = strip_fences(text)
    match = re.search(r"^(#{2,6})\s+" + re.escape(number) + r"\.?\s+[^\n]*", body, re.M)
    if not match:
        return ""
    tail = body[match.end():]
    next_heading = re.search(r"^#{1," + str(len(match.group(1))) + r"}\s+", tail, re.M)
    return tail[:next_heading.start()] if next_heading else tail


def check_readiness(docs: dict[str, str]) -> list[dict]:
    """Check declared structure only; the Conductor owns the semantic review."""
    findings = []
    def fail(name: str, message: str):
        findings.append({"check": "readiness", "file": name, "message": message})

    for name in KIT_DOCS:
        if name not in docs:
            fail(name, "required companion document is missing")
    for name, text in docs.items():
        if is_kit_doc(name) and re.search(r"Status:\s*In interview\b", text):
            fail(name, "still in interview")
    boundary = section(docs.get("ARCHITECTURE.md", ""), "15")
    pointers = re.findall(r"^\s*-\s+\*\*Current slice:\*\*\s+`?(SLICE-[\w-]+\.md)`?(?=\s|$)", boundary, re.M)
    if len(pointers) != 1:
        fail("ARCHITECTURE.md", "section 15 must name one Current slice filename (SLICE-*.md)")
        return findings
    active = pointers[0]
    if active not in docs:
        fail(active, "active slice file is missing")
        return findings
    if slice_status(docs[active]) == "Done with evidence":
        fail(active, "completed slice cannot be the current build boundary")
    for name, text in docs.items():
        if name != active and name.startswith("SLICE-") and slice_status(text) in ("Approved for build", "In progress"):
            fail(name, "another slice is active")

    requirements = set(re.findall(r"^\|\s*(R-\d+)\s*\|", section(docs.get("ENGINEERING.md", ""), "4.1"), re.M))
    acceptance = section(docs[active], "8")
    rows = [line for line in acceptance.splitlines() if re.match(r"^\|\s*S-\d+\s*\|", line)]
    if not rows:
        fail(active, "section 8 needs acceptance rows with S-IDs")
    seen = set()
    for row in rows:
        cells = table_cells(row)
        criterion_id = cells[0]
        if criterion_id in seen:
            fail(active, f"duplicate acceptance ID: {criterion_id}")
        seen.add(criterion_id)
        if len(cells) != 5:
            fail(active, f"{criterion_id} needs ID, Requirement, Criterion, Verified by, Gate columns")
            continue
        refs = re.findall(r"\bR-\d+\b", cells[1])
        if not refs or any(ref not in requirements for ref in refs):
            fail(active, f"{criterion_id} must reference confirmed R-IDs in EDD section 4.1")
        for label, cell in zip(("Criterion", "Verified by", "Gate"), cells[2:]):
            if not cell or has_placeholder(cell):
                fail(active, f"{criterion_id} {label} is empty or a placeholder")
    return findings


def check_state_and_version(name: str, text: str) -> list[dict]:
    findings = []
    if not re.search(r"^Version:\s*\S", text, re.M) and not re.search(r"^Version \d", text, re.M):
        findings.append({"check": "version", "file": name, "message": "no Version line"})
    if re.search(r"Status:\s*In interview", text) and "INTERVIEW STATE" not in text:
        findings.append({"check": "state-block", "file": name, "message": "Status is In interview but no INTERVIEW STATE block"})
    return findings


def audit(root: Path, everything: bool = False, ready: bool = False) -> list[dict]:
    docs = read_docs(root, everything)
    findings: list[dict] = []
    if not docs:
        findings.append({"check": "document-set", "file": str(root), "message": "no selected documents"})
    for name, text in docs.items():
        findings.extend(check_hygiene(name, text))
        findings.extend(check_state_and_version(name, text))
        if name in DOC_ROLES or name.startswith("SLICE-"):
            findings.extend(check_decision_blocks(name, text))
        if name == "DECISION-LOG.md":
            findings.extend(check_decision_log(name, text))
        if name.startswith("SLICE-") and name.endswith(".md") and slice_status(text) not in SLICE_STATUSES:
            findings.append({"check": "slice-status", "file": name, "message": f"invalid slice status: {slice_status(text)!r}"})
    findings.extend(check_cross_references(docs, ready))
    if ready:
        findings.extend(check_readiness(docs))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Mechanical audit for Scaffold Kit documents.")
    parser.add_argument("--docs", default="docs", help="directory holding ARCHITECTURE.md, ENGINEERING.md, DECISION-LOG.md and SLICE-*.md")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--all", action="store_true", help="audit every Markdown file in the directory, not only the kit's documents")
    parser.add_argument("--ready", action="store_true", help="require companions, one active slice and acceptance/check bindings; does not grant approval")
    args = parser.parse_args(argv)
    root = Path(args.docs)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    try:
        audited = sorted(read_docs(root, args.all))
        findings = audit(root, args.all, args.ready)
    except (OSError, UnicodeError) as error:
        print(f"cannot read documents: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"docs": audited, "mode": "ready" if args.ready else "partial", "findings": findings}, indent=2))
    else:
        for finding in findings:
            where = f"{finding['file']}:{finding['line']}" if "line" in finding else finding["file"]
            print(f"{finding['check']}: {where}: {finding['message']}")
        print(f"{len(findings)} finding(s) across {len(audited)} document(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
