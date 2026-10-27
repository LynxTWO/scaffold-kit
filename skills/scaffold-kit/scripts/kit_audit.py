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
import os
import re
import sys
from pathlib import Path

STATUSES = ("Confirmed", "Proposed", "Assumed", "Open", "Deferred", "Superseded")
# "Done" is what the earlier 0.4 footer told people to write; it stays valid.
COMPLETED_SLICE = ("Done with evidence", "Done")
SLICE_STATUSES = ("Proposed", "Approved for build", "In progress") + COMPLETED_SLICE
# Whole-cell values that hold a place rather than name a check.
PENDING_CELLS = {"", "tbd", "tba", "todo", "pending", "na", "none", "manual"}
# Approval values that say no approval exists yet.
NOT_APPROVED = re.compile(r"(not|no|un-?approved|pending|awaiting|waiting|tbd|tba|todo|none|withheld|declined|rejected)\b", re.I)
# Dates as people write them: 2026-10-12, 12/10/2026, 12 October 2026, Oct 12, 2026.
_MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
APPROVAL_DATE = re.compile(r"\b(?:\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}\s+" + _MONTH + r"\s+\d{4}|"
                           + _MONTH + r"\s+\d{1,2},?\s+\d{4})\b", re.I)
# A plain, backticked or self-linked filename, optionally followed by punctuation and a description.
CURRENT_SLICE = re.compile(
    r"^\s*[-*]\s+\*\*Current slice:\*\*\s+(\[)?`?(SLICE-[\w-]+\.md)`?(?(1)\]\((?:\./)?\2\))[.,;:]?(?=\s|$)", re.M)
BANNED_WORDS = (
    "robust", "seamless", "cutting-edge", "powerful", "world-class", "blazing",
    "game-changing", "captures", "implies", "reframes", "strips", "weaponize",
    "the exact", "delve",
)
FILLER_OPENERS = ("it is worth noting", "in today's fast-paced world", "as we all know")
DOC_ROLES = {"ARCHITECTURE.md": "ADD", "ENGINEERING.md": "EDD"}


KIT_DOCS = ("ARCHITECTURE.md", "ENGINEERING.md", "DECISION-LOG.md")
SCAN_EXCLUDED = {".git", "node_modules", "vendor"}
ONE_SET_RULE = ("one document set per project (SKILL.md: Keep one document set) "
                "[instruction line](https://github.com/LynxTWO/scaffold-kit/blob/8d6316b040136142890548a06a1d3e5d96be63b0/skills/scaffold-kit/SKILL.md#L30)")
BRIEF_LENGTH_RULE = ("compact form max 500 unless a named risk needs essential decision detail "
                     "(assets/templates/SLICE-BRIEF.md:20) "
                     "[instruction line](https://github.com/LynxTWO/scaffold-kit/blob/8d6316b040136142890548a06a1d3e5d96be63b0/skills/scaffold-kit/assets/templates/SLICE-BRIEF.md#L20)")
BRIEF_RETIREMENT_RULE = ("retire finished briefs (references/conductor.md: expansion loop step 3) "
                         "[instruction line](https://github.com/LynxTWO/scaffold-kit/blob/conductor/retire-finished-briefs/skills/scaffold-kit/references/conductor.md#L179)")


def is_kit_doc(name: str) -> bool:
    return name in KIT_DOCS or (name.startswith("SLICE-") and name.endswith(".md"))


def read_docs(root: Path, everything: bool = False) -> dict[str, str]:
    """The kit's own documents by default; --all widens to every Markdown file in the directory."""
    docs = {}
    for path in sorted(root.glob("*.md")):
        if everything or is_kit_doc(path.name):
            docs[path.name] = path.read_text(encoding="utf-8")
    return docs


def fenced_lines(text: str, blockquotes: bool = False):
    """Yield lines and fence identities; word counting can unwrap blockquotes."""
    fence = None
    region = None
    depth = 0
    for index, line in enumerate(text.splitlines(keepends=True)):
        containers = [line]
        if blockquotes:
            while re.match(r"^ {0,3}>[ \t]?", containers[-1]):
                containers.append(re.sub(r"^ {0,3}>[ \t]?", "", containers[-1], count=1))
            if fence is not None and len(containers) <= depth and line.strip():
                # Leaving the quote also ends a fence inside that container.
                fence = None
                region = None
            line = containers[depth] if fence is not None and len(containers) > depth else containers[-1]
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)", line)
        current = region
        if fence is not None:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= fence[1] and not marker.group(2).strip():
                fence = None
                region = None
        elif marker and not (marker.group(1)[0] == "`" and "`" in marker.group(2)):
            fence = (marker.group(1)[0], len(marker.group(1)))
            depth = len(containers) - 1
            region = current = index
        yield line, current


def strip_fences(text: str) -> str:
    """Mask fenced examples without changing character/line offsets."""
    return "".join(re.sub(r"[^\r\n]", " ", line) if region is not None else line
                   for line, region in fenced_lines(text))


def slice_state_regions(lines: list) -> set:
    return {region for index, (line, region) in enumerate(lines)
            if line.strip() == "SLICE STATE" and region == index - 1
            and re.fullmatch(r"(?:`{3,}|~{3,})(?:text|plaintext)?", lines[region][0].strip())}


def scan_document_sets(root: Path) -> list[dict]:
    """Inventory sets without following symlinks or reading repository code."""
    parts = root.absolute().parts
    if (root.is_symlink() or any(part in SCAN_EXCLUDED for part in parts)
            or any(pair == ("assets", "templates") for pair in zip(parts, parts[1:]))):
        return []
    sets = []

    def read_error(error):
        raise error

    for directory, children, filenames in os.walk(root, followlinks=False, onerror=read_error):
        path = Path(directory)
        if any(pair == ("assets", "templates") for pair in zip(path.parts, path.parts[1:])):
            children[:] = []
            continue
        children[:] = sorted(child for child in children
                             if child not in SCAN_EXCLUDED and not (path / child).is_symlink())
        companions = {name for name in KIT_DOCS if name in filenames
                      and not (path / name).is_symlink() and (path / name).is_file()}
        if len(companions) < 2:
            continue
        archived = False
        if "ARCHITECTURE.md" in companions:
            text = strip_fences((path / "ARCHITECTURE.md").read_text(encoding="utf-8"))
            status = re.search(r"^(?:Version:[^\r\n]*?[ \t]+)?Status:[ \t]*([^\r\n]*)", text, re.M)
            archived = bool(status and re.search(r"\b(?:Superseded|Archived)\b", status.group(1)))
        sets.append({"path": path.relative_to(root).as_posix(), "archived": archived})
    return sorted(sets, key=lambda item: item["path"])


def check_document_sets(root: Path, sets: list[dict]) -> list[dict]:
    if sum(not item["archived"] for item in sets) <= 1:
        return []
    paths = ", ".join(f"{item['path']} ({'archived' if item['archived'] else 'current'})" for item in sets)
    return [{"check": "document-set", "file": str(root), "message": f"{ONE_SET_RULE}; sets: {paths}"}]


def check_brief_length(name: str, text: str) -> list[dict]:
    lines = list(fenced_lines(text, blockquotes=True))
    words = sum(len(line.split()) for line, region in lines if region is None)
    states = slice_state_regions(lines)
    for index, (line, region) in enumerate(lines):
        if region not in states or index == region:
            continue
        # SLICE STATE is metadata, so its content counts but its delimiters do not.
        opening = re.match(r"\s*(`{3,}|~{3,})", lines[region][0]).group(1)
        closing = re.fullmatch(r" {0,3}(`{3,}|~{3,})[ \t]*", line.rstrip("\r\n"))
        if closing and closing.group(1)[0] == opening[0] and len(closing.group(1)) >= len(opening):
            continue
        words += len(line.split())
    expanded = any(region is None and re.match(r"^Expanded for:[^\S\r\n]*\S", line)
                   for line, (_, region) in zip(text.splitlines(keepends=True), lines))
    if words <= 500 or expanded:
        return []
    return [{"check": "brief-length", "file": name, "message": f"{words} words; {BRIEF_LENGTH_RULE}"}]


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


def is_pending(cell: str) -> bool:
    """A cell such as TBD, N/A, pending or a bare `manual:` names no check."""
    return re.sub(r"[\W_]+", "", cell).lower() in PENDING_CELLS


def approved_versions(text: str) -> list:
    """Brief versions named on approval lines that carry a name, then a date (None when unnamed).

    This reads structure only; it cannot show the approval is genuine."""
    found = []
    for match in re.finditer(r"^[ \t>*_-]*Approved for build by:[ \t]*([^\r\n]*)", strip_fences(text), re.M):
        value = match.group(1).strip(" \t*_`")
        date = APPROVAL_DATE.search(value)
        if not date or "<" in value or has_placeholder(value) or NOT_APPROVED.match(value):
            continue
        name = value[:date.start()].strip(" ,;:.-")
        if re.search(r"[^\W\d_]", name) and not is_pending(name):
            version = re.search(r"\bbrief version\s+v?(\d+(?:\.\d+)*)", value, re.I)
            found.append(version.group(1) if version else None)
    return found


def approval_recorded(text: str) -> bool:
    return bool(approved_versions(text))


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
    pointers = [match.group(2) for match in CURRENT_SLICE.finditer(boundary)]
    for name, text in docs.items():
        if name not in pointers and name.startswith("SLICE-") and name.endswith(".md") and slice_status(text) in COMPLETED_SLICE:
            fail(name, f"completed slice is not the current build boundary; {BRIEF_RETIREMENT_RULE}")
    if len(pointers) != 1:
        fail("ARCHITECTURE.md", "section 15 must name one Current slice filename (SLICE-*.md)")
        return findings
    active = pointers[0]
    if active not in docs:
        fail(active, "active slice file is missing")
        return findings
    status = slice_status(docs[active])
    if status in COMPLETED_SLICE:
        fail(active, "completed slice cannot be the current build boundary")
    elif status in ("Approved for build", "In progress"):
        named = approved_versions(docs[active])
        version = re.search(r"^Version:\s*v?(\d+(?:\.\d+)*)", strip_fences(docs[active]), re.M)
        if not named:
            fail(active, f"status {status!r} needs 'Approved for build by:' followed by a name and date on that line")
        elif version and any(named) and version.group(1) not in named:
            fail(active, f"approval names brief version {[v for v in named if v][-1]} but the brief is version {version.group(1)}")
    for name, text in docs.items():
        if name != active and name.startswith("SLICE-") and slice_status(text) in ("Approved for build", "In progress"):
            fail(name, "another slice is active")

    requirement_rows = re.findall(r"^\|\s*(R-\d+)\s*\|", section(docs.get("ENGINEERING.md", ""), "4.1"), re.M)
    for duplicate in sorted({ref for ref in requirement_rows if requirement_rows.count(ref) > 1}):
        fail("ENGINEERING.md", f"duplicate requirement ID: {duplicate}")
    requirements = set(requirement_rows)
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
            fail(active, f"{criterion_id} needs ID, Requirement, Criterion, How it will be checked, Gate columns")
            continue
        refs = re.findall(r"\bR-\d+\b", cells[1])
        if not refs or any(ref not in requirements for ref in refs):
            fail(active, f"{criterion_id} must reference confirmed R-IDs in EDD section 4.1")
        for label, cell in zip(("Criterion", "How it will be checked", "Gate"), cells[2:]):
            if is_pending(cell) or has_placeholder(cell):
                fail(active, f"{criterion_id} {label} is empty or a placeholder")
    return findings


def check_state_and_version(name: str, text: str) -> list[dict]:
    findings = []
    if not re.search(r"^Version:\s*\S", text, re.M) and not re.search(r"^Version \d", text, re.M):
        findings.append({"check": "version", "file": name, "message": "no Version line"})
    if re.search(r"Status:\s*In interview", text) and "INTERVIEW STATE" not in text:
        findings.append({"check": "state-block", "file": name, "message": "Status is In interview but no INTERVIEW STATE block"})
    return findings


def check_omissions(name: str, text: str) -> list[dict]:
    """Explicit omission sentences only; no semantic completeness claim."""
    if slice_status(text) in COMPLETED_SLICE:
        return []
    body = re.sub(r"^ {0,3}#{1,6}\s.*$", "", strip_fences(text), flags=re.M)
    pattern = (r"\b(?:tables?|sections?\s+\d+(?:\s*(?:,|-|and|through|to)\s*\d+)*)\s+(?:is|are)\s+omitted\b|"
               r"\bno\s+(?:(?:future(?:-work)?|connection|exclusion|milestone|unused|additional|template)[ /]+)*tables?\s+is\s+needed\b")
    lines = []
    for sentence in re.finditer(r"[^.!?]+", body):
        hit = re.search(pattern, sentence.group(), re.I)
        if hit:
            lines.append(body[:sentence.start() + hit.start()].count("\n") + 1)
    return ([{"check": "omissions", "file": name, "line": lines[1],
              "message": "multiple explicit omission sentences; combine section/table omissions in one sentence"}]
            if len(lines) > 1 else [])


def brief_reader_prose(text: str, keep_literals: bool = True, keep_state: bool = False) -> str:
    """Mask common Markdown destinations/literals while retaining source lines."""
    lines = list(fenced_lines(text))
    states = slice_state_regions(lines) if keep_state else set()
    body = "".join(line if region is None or (region in states and index != region)
                   else re.sub(r"[^\r\n]", " ", line)
                   for index, (line, region) in enumerate(lines)).replace("\r\n", "\n")
    mask = lambda value: re.sub(r"[^\n]", " ", value)
    def link(match):
        start, end = match.start(1) - match.start(), match.end(1) - match.start()
        return mask(match[0][:start]) + match[1] + mask(match[0][end:])
    body = re.sub(r"\[([^\]]+)\]\((?:[^()]|\([^()]*\))*\)", link, body)
    body = re.sub(r"^[ \t]{0,3}\[[^\]]+\]:[^\n]*(?:\n[ \t]*(?:\"[^\n]*\"|'[^\n]*'|\([^\n]*\))[ \t]*)?",
                  lambda match: mask(match[0]), body, flags=re.M)
    def literal(match):
        is_path = re.fullmatch(r"\S+\.[A-Za-z0-9]{1,10}", match[2].strip())
        return mask(match[0]) if not keep_literals or is_path else match[0]
    return re.sub(r"(`+)([^\n]*?)\1", literal, body)


def check_brief_recommendations(name: str, text: str) -> list[dict]:
    """Observed copied recommendation cue; alternatives still need source review."""
    if slice_status(text) in COMPLETED_SLICE:
        return []
    body = brief_reader_prose(text, keep_literals=False)
    match = re.search(r"\b(?:is|are)\s+recommended\b", body, re.I)
    return ([{"check": "decision-copy", "file": name, "line": body[:match.start()].count("\n") + 1,
              "message": "brief recommendation belongs in its canonical decision entry; keep the linked owner question here"}]
            if match else [])


def check_guided_labels(docs: dict[str, str]) -> list[dict]:
    """Known label and action-term glosses in active guided prose, not comprehension."""
    architecture = docs.get("ARCHITECTURE.md", "")
    depth = re.search(r"^(?:Explanation|Interview) depth:\s*([^\n]+)", architecture, re.M)
    active = list(CURRENT_SLICE.finditer(section(architecture, "15")))
    if not depth or not depth.group(1).strip().startswith("guided") or len(active) != 1:
        return []
    name = active[0].group(2)
    text = docs.get(name, "")
    if slice_status(text) in COMPLETED_SLICE:
        return []
    body = brief_reader_prose(text, keep_state=True)
    source = text.replace("\r\n", "\n")
    cuts = [0] + [match.end() for match in re.finditer(r"\n[ \t]*\n", source)] + [len(body)]
    paragraphs = [re.sub(r"\s+", " ", body[start:end]) for start, end in zip(cuts, cuts[1:])]
    findings = []
    labels = {
        "ADD": ("Architecture Document", r"architecture(?:\s+document)?"),
        "EDD": ("Engineering Document", r"engineering(?:\s+document)?"),
        "CLI": ("command-line tool", r"command[- ]line(?:\s+(?:tool|interface))?|tool[^.\n]{0,30}typing commands"),
        "T1": ("prototype or personal tool", r"prototype|personal tool|experiment"),
        "Q": ("question identifier", r"question(?: identifier| ID)?"),
        "SHA-256": ("file fingerprint", r"(?:file|source|content) (?:fingerprint|digest)|fingerprint (?:of|for) (?:the )?file"),
        "HEAD": ("current source revision", r"(?:current|checked|source) (?:source )?revision|revision (?:checked|of (?:the )?source)"),
        "exit code": ("success or failure number; 0 means success", r"(?:success(?:ful)?|failure|failed)[^.]{0,30}(?:number|code|status)|(?:number|code|status|0)[^.]{0,30}(?:success(?:ful)?|failure|failed)|(?:reports?|means|indicates) (?:success|failure)"),
        "stdout": ("printed text", r"printed (?:text|output)|normal output|(?:text|output) printed"),
        "stderr": ("error text", r"error (?:text|output|messages)|(?:text|output) printed for errors"),
        "dispatch": ("handling command arguments", r"(?:read(?:ing|s)?|interpret(?:ing|s)?|handl(?:e|es|ing)|process(?:ing|es)?) (?:the )?(?:command(?:[- ]line)? )?arguments"),
        "rendering": ("printing result text", r"(?:print(?:s|ing)?|display(?:s|ing)?|format(?:s|ting)?|prepar(?:e|es|ing)) (?:the )?(?:result )?(?:text|output)"),
        "version branch": ("path that handles the version request", r"(?:path|part)[^.]{0,30}(?:version|request)"),
        "stubs": ("temporary substitutes", r"temporary (?:substitutes|replacements|placeholders)|stand[- ]ins"),
        "constant": ("fixed value stored in code", r"(?:fixed|stored) (?:version )?value|value (?:stored|defined) in (?:the )?(?:code|script)"),
        "output contract": ("rules for printed text and command results", r"(?:rules|agreement|requirements|format)[^.]{0,30}(?:print(?:ed|ing|s)?|text|exit|results?)"),
        "output streams": ("normal and error output", r"(?:normal|printed)(?:\s+and\s+|\s*/\s*)error (?:text|output)|(?:normal|printed) output[^.]{0,20}error (?:text|output)"),
        "source-read failure": ("unable to read the version value", r"(?:cannot|unable to|fails? to|could not) read (?:the )?(?:version|source|value)"),
    }
    for label, (expansion, words) in labels.items():
        alias = r"\b" + re.escape(label).replace(r"\ ", r"\s+") + r"\b"
        if label == "exit code":
            alias = r"\bexits?(?:\s+with)?\s+(?:code|result|status|0)\b"
        if not label.isupper():
            alias = "(?i:" + alias + ")"
        used = re.search(alias, body)
        gloss = r"\b(?i:" + words + r")\b"
        pattern = gloss + r"[^.]{0,60}" + alias + "|" + alias + r"[^.]{0,60}" + gloss
        if used and not any(re.search(pattern, paragraph) for paragraph in paragraphs):
            findings.append({"check": "guided-label", "file": name, "line": body[:used.start()].count("\n") + 1,
                             "message": f"guided brief uses {label} without a nearby plain label; write {expansion} ({label}) once"})
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
        if name.startswith("SLICE-") and name.endswith(".md"):
            findings.extend(check_brief_length(name, text))
            findings.extend(check_omissions(name, text))
            findings.extend(check_brief_recommendations(name, text))
            if slice_status(text) not in SLICE_STATUSES:
                findings.append({"check": "slice-status", "file": name, "message": f"invalid slice status: {slice_status(text)!r}"})
    findings.extend(check_cross_references(docs, ready))
    findings.extend(check_guided_labels(docs))
    if ready:
        findings.extend(check_readiness(docs))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Mechanical audit for Scaffold Kit documents.")
    parser.add_argument("--docs", help="directory holding ARCHITECTURE.md, ENGINEERING.md, DECISION-LOG.md and SLICE-*.md (default: docs; omitted for a standalone --repo scan)")
    parser.add_argument("--repo", help="scan a repository for extra document sets, skipping templates, .git, node_modules and vendor")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--all", action="store_true", help="audit every Markdown file in the directory, not only the kit's documents")
    parser.add_argument("--ready", action="store_true", help="require companions, one active slice and acceptance/check bindings; does not grant approval")
    args = parser.parse_args(argv)
    root = Path(args.docs if args.docs is not None else "docs")
    audit_docs = args.docs is not None or args.ready or args.all or args.repo is None
    repo = Path(args.repo) if args.repo is not None else None
    if audit_docs and not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    if repo is not None and not repo.is_dir():
        print(f"not a directory: {repo}", file=sys.stderr)
        return 2
    try:
        audited = sorted(read_docs(root, args.all)) if audit_docs else []
        findings = audit(root, args.all, args.ready) if audit_docs else []
        sets = scan_document_sets(repo) if repo is not None else []
        if repo is not None:
            findings.extend(check_document_sets(repo, sets))
    except (OSError, UnicodeError) as error:
        print(f"cannot read documents: {error}", file=sys.stderr)
        return 2
    if args.json:
        result = {"docs": audited, "mode": "ready" if args.ready else "partial", "findings": findings}
        if repo is not None:
            result["document_sets"] = sets
        print(json.dumps(result, indent=2))
    else:
        if repo is not None:
            for item in sets:
                print(f"document set: {item['path']} ({'archived' if item['archived'] else 'current'})")
        for finding in findings:
            where = f"{finding['file']}:{finding['line']}" if "line" in finding else finding["file"]
            print(f"{finding['check']}: {where}: {finding['message']}")
        print(f"{len(findings)} finding(s) across {len(audited)} document(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
