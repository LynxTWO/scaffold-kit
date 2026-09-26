---
name: scaffold-kit
description: Use when starting a software project, scaffolding planning documents for an existing codebase, choosing or writing the next slice brief, or recording a design decision with a status and a revisit trigger. Plan broadly, build narrowly, test reality, expand deliberately. A structured interview produces an Architecture Document, an Engineering Document, a Decision Log and one active Slice Brief that bounds what an AI agent may build. Works for apps, services, CLIs, libraries, data systems, games, automations and sites at any experience level. Pairs with anti-dark-code for mapping existing code and for verification.
license: FSL-1.1-MIT. LICENSE.md has complete terms
compatibility: Instructions only. The optional audit script needs Python 3.10 or newer and no packages.
---

# Scaffold Kit

Plan broadly. Build narrowly. Test reality. Expand deliberately.

You design the whole puzzle, then build one production-quality section with clean places for future pieces to connect, then repeat. This skill runs the planning interview and keeps the documents honest. It writes documents, not code: building starts only after the human approves the active Slice Brief.

## What it produces

Four documents in the repository, `docs/` by convention, under version control:

| Document | Template | Holds |
|---|---|---|
| `ARCHITECTURE.md` | [assets/templates/ARCHITECTURE.md](assets/templates/ARCHITECTURE.md) | the puzzle: modules, interfaces, data flow, technology, extension points, current build boundary |
| `ENGINEERING.md` | [assets/templates/ENGINEERING.md](assets/templates/ENGINEERING.md) | the rules: requirements ledger, data model, security, standards, verification, definition of done |
| `DECISION-LOG.md` | [assets/templates/DECISION-LOG.md](assets/templates/DECISION-LOG.md) | why: every significant choice, its options, and what reopens it |
| `SLICE-NNN-<name>.md` | [assets/templates/SLICE-BRIEF.md](assets/templates/SLICE-BRIEF.md) | the build boundary: one slice, acceptance criteria, evidence required |

Prior research and business planning go to a `PRODUCT-CONTEXT.md` companion, mined during the interview, never pasted into the documents.

## How to run it

Read [the Conductor](references/conductor.md) before Phase 0. It holds the operating rules, the decision status vocabulary, the Triage Card, the phases, the audit pass, the expansion loop, session management and writing hygiene. Load one template at a time, when its phase starts:

| Phase | Load |
|---|---|
| 0 Intake, 1 Triage | the Conductor only |
| 2 Architecture interview | `assets/templates/ARCHITECTURE.md` |
| 3 Engineering interview | `assets/templates/ENGINEERING.md` |
| 4 Decision completeness | `assets/templates/DECISION-LOG.md` |
| 5 Slice selection | `assets/templates/SLICE-BRIEF.md` |
| 6 Audit pass | the Conductor's checklist plus `python3 scripts/kit_audit.py --docs docs` |

When code already exists, or when anti-dark-code is installed in the repository, read [working with anti-dark-code](references/working-with-anti-dark-code.md) before Phase 1: it names the map artifacts that backfill the Architecture Document, the one mapping between the two vocabularies, and how acceptance criteria bind to verification gates. For Claude Code wiring (`CLAUDE.md` stub, permissions, hooks), read [the Claude addendum](references/claude-addendum.md).

## Gates that do not move

- **Interview, do not invent.** Every filled section traces to an answer, an accepted default, or a flagged assumption.
- **Planning writes documents only.** No package installs, schema changes or product code during the interview.
- **Irreversible choices need an explicit human confirmation:** payment provider, data residency, public API names and shapes, anything deleting user data.
- **Nothing is built until the active Slice Brief reads `Approved for build by: <name>, <date>`.** Say the gate out loud when the brief is presented; approval of the idea is not approval of the brief.
- **Verification effort is bounded by consequence.** A harness, campaign or observer is a build item with its own requirement ID, or it is out of scope.
- **Fast-run never skips checkpoints.** Irreversible decisions, risk-flag sections, slice selection and the audit readback get direct questions in every mode.

## Mechanical audit

`python3 scripts/kit_audit.py --docs docs` checks what politeness misses: banned punctuation and words, a status on every decision block and log entry, index and entries in agreement, superseded links in both directions, section cross-references that resolve, and a state block while a document is still in interview. Exit code 1 on any finding. Attach its output to the Phase 6 readback; it can run as a repository gate.

## Manual use without a host that loads skills

Hand an AI the Conductor and the four templates from this directory, then describe the project in a paragraph. The files are the single source of truth; this skill is a loader, not a fork.
