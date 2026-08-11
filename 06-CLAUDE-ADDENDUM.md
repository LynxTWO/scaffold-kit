# Claude Addendum

Optional. The rest of the kit is agent-agnostic. This file wires it into Claude Code specifically. Feature details change; current documentation lives at https://docs.claude.com/en/docs/claude-code/overview

## Where the documents live

Put the filled documents in the repository, not in chat history:

```
project/
  CLAUDE.md
  docs/
    ARCHITECTURE.md
    ENGINEERING.md
    DECISION-LOG.md
    SLICE-001-[name].md
    SLICE-002-[name].md   (arrives with the expansion loop)
```

Claude Code reads `CLAUDE.md` automatically at the start of a session. That file should stay short and point at the documents instead of duplicating them.

## CLAUDE.md stub

```markdown
# CLAUDE.md

Read before any work, in this order:
1. docs/SLICE-001-[name].md  (the active slice brief, the build boundary)
2. docs/ARCHITECTURE.md      (the puzzle: modules, seams, guardrails)
3. docs/ENGINEERING.md       (the rules: standards, verification, done)
4. docs/DECISION-LOG.md      (why things are the way they are)

Standing rules:
- Build only inside the active slice brief's boundary. Anything else
  needs a Decision Log entry approved by me first.
- Do not build on decisions marked Open or Proposed. Ask.
- Stop and ask before: schema changes, new dependencies, deletions,
  anything touching secrets, any deploy.
- Verification means tests, logs, diffs, and observed behavior.
  Your summary of your own work is a claim, not evidence.
- If reality contradicts the documents, stop and surface it.
- Writing hygiene for any document you touch: no em dashes,
  short sentences, no marketing adjectives.
```

Adjust the stop list to match EDD section 12 for the project. When the expansion loop advances to a new slice, update line 1 to the new brief in the same commit that approves it. A stale pointer here quietly widens the build boundary.

## Running the interview in Claude

- The interview itself can run in claude.ai or in Claude Code. Give Claude `01-CONDUCTOR.md` plus the four templates and the project description, then answer its questions.
- In Claude Code, run planning phases in plan mode so nothing gets executed while the documents are being written. Switch out of plan mode only when the First Slice Brief is approved.
- Long interviews: rely on the Conductor's INTERVIEW STATE block. A fresh session resumes from the documents, not from chat memory.

## Permissions as tool discipline

EDD section 12 defines modes with narrow permissions. In Claude Code, that maps to its permission system: approve tool actions deliberately, keep the allowlist narrow, and widen it per mode rather than globally. Discovery sessions need read access. Implementation sessions add write access inside the slice paths. Nothing gets a standing approval for schema changes, deletions, or deploys.

## Packaging the Conductor as a skill or command

If you run this kit often, package it so it triggers by name:

- A custom skill whose SKILL.md wraps the Conductor protocol and points at the templates, so "scaffold this project" starts the interview the same way every time.
- Or a custom slash command that loads the Conductor and templates into context.

Either way, the templates stay the single source of truth. The skill or command is a loader, not a fork.

## Verification hooks

Claude Code hooks can enforce parts of the kit mechanically:

- A check that greps documents for banned punctuation and tell-words from the Conductor's hygiene list.
- A check that fails when a Decision Block is missing a STATUS line.
- A reminder that fires on schema or migration paths, pointing at the stop-and-ask rule.

Mechanical checks catch drift that polite intentions miss.

## Pairing with an existing codebase

This kit assumes a fresh start. When code already exists, map it first, then scaffold:

1. Run a codebase-mapping pass (for example an anti-dark-code style audit) to establish what is actually there: modules, trust boundaries, unknowns.
2. Backfill ARCHITECTURE.md from the map, marking reality-derived entries as Confirmed and aspirations as Proposed.
3. Run the Conductor for the gaps, then proceed slice by slice as usual.

Greenfield gets the interview first. Brownfield earns the interview by being mapped honestly first.
