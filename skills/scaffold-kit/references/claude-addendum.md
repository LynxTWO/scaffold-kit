# Claude Addendum

Optional. The rest of the kit is agent-agnostic. This file wires it into Claude Code specifically. Feature details change; current documentation lives at https://code.claude.com/docs/en/overview

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

Start with docs/README.md and docs/SLICE-001-[name].md (active brief).
Read the Architecture and Engineering overviews, then only the relevant
sections and decision entries linked by the brief. Check source freshness
on resume. Reuse the Triage Card's Explanation depth.

Standing rules:
- Build only inside the approved active brief. New scope needs a revised
  approved brief; significant decision changes go through the log.
- Do not build on decisions marked Open or Proposed. Ask.
- Require explicit approval for schema changes, new dependencies,
  deletions, secrets and deploys. Carry forward approval within reviewed
  targets and effects; changed scope reopens the gate.
- Unattended agents never touch: auth, sessions, secrets, migrations,
  RLS or access policies, CI workflows, billing, retention or deletion
  of user data. A founder or owner drives those in an interactive session.
- Verification means tests, logs, diffs, and observed behavior.
  Your summary of your own work is a claim, not evidence.
- If reality contradicts the documents, stop and surface it.
- Writing hygiene for any document you touch: no em dashes,
  short sentences, no marketing adjectives.
```

Adjust the stop list to EDD section 12. When advancing a slice, update the index, ADD section 15 and this active pointer together. If the repository already has an index, use it instead of creating another.

## Running the interview in Claude

- The interview can run in claude.ai or Claude Code. Give Claude [the Conductor](conductor.md), then load templates as their phases start and describe the project.
- In Claude Code, plan mode blocks file writes, so it suits read-only discovery but cannot save the planning documents. During the interview allow edits to the documents only, and leave product code untouched until the active brief is approved.
- Long interviews: rely on the Conductor's INTERVIEW STATE block. A fresh session resumes from the documents, not from chat memory.

## Permissions as tool discipline

EDD section 12 defines modes with narrow permissions. In Claude Code, that maps to its permission system: approve tool actions deliberately, keep the allowlist narrow, and widen it per mode rather than globally. Discovery sessions need read access. Implementation sessions add write access inside the slice paths. Nothing gets a standing approval for schema changes, deletions, or deploys.

## The kit as a skill

This repository is the skill: `skills/scaffold-kit/SKILL.md` is the loader, `references/conductor.md` is the protocol, and `assets/templates/` holds the templates. Install it where your host reads skills (`.agents/skills/scaffold-kit/` for Codex, Cursor, Copilot and Gemini; `.claude/skills/scaffold-kit/` for Claude Code), or add the repository as a plugin marketplace. The templates stay the single source of truth; the skill is a loader, not a fork.

## Verification hooks

Claude Code hooks can enforce parts of the kit mechanically:

- A check that greps documents for banned punctuation and tell-words from the Conductor's hygiene list.
- A check that fails when a Decision Block is missing a STATUS line.
- A reminder that fires on schema or migration paths, pointing at the stop-and-ask rule.

Mechanical checks catch drift that polite intentions miss.

## Pairing with an existing codebase

When code already exists, map the relevant scope first, then scaffold gaps:

1. Run a codebase-mapping pass (anti-dark-code's Understand card when it is installed; see [working with anti-dark-code](working-with-anti-dark-code.md)) to establish what is actually there: modules, trust boundaries, unknowns.
2. Link observed facts from ARCHITECTURE.md to current map evidence and confidence. Proposed changes need owner choice or delegation before becoming Confirmed.
3. Run the Conductor for the gaps, then proceed slice by slice as usual.

Greenfield gets the interview first. Brownfield earns the interview by being mapped honestly first.
