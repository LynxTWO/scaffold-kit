# The Scaffold Kit

Working title. Rename freely, it is one find and replace.

Version 0.3 (Field-Tested). July 30, 2026.

A document scaffolding system for AI-assisted software development. It works for any kind of build: app, service, CLI tool, library, database system, game, automation, or site. It works for any experience level, from a first project to a senior engineer converting judgment into specifications.

The model behind it:

**Plan broadly. Build narrowly. Test reality. Expand deliberately.**

You do not build the whole product first. You design the whole puzzle, then build one valuable, production-quality section of it, with clean places for future pieces to connect. Then you repeat, one slice at a time.

## Revision note: v0.3 (Field-Tested)

Version 0.3 applies the fifteen findings from a full stress-test run: a real T2 project with payments and personal-data risk flags, full interview mode, thirty-three sections, twenty-six logged decisions. New mechanics: a fast-run mode with mandatory checkpoints at irreversible decisions and risk-flag sections; a named spike pattern for closing Open decisions by evidence; a slice growth tally the Conductor must present at slice selection; an optional build-order table in the slice brief; and a product-context companion convention for pricing hypotheses, validation thresholds, and staged plans. Codified from the run: sections may share a turn within the question cap; readbacks on tap surfaces use Confirmed or adjust-in-reply; multi-select forms suit precedence questions; documents materialize at phase boundaries; mid-interview amendments supersede through the log; and the Decision Block gains an optional AI-recommendation-differed line, used seven times in the test. Adjustments: the audit rule now permits Open decisions inside the slice when their closing spike is scheduled before dependent work; risk-flag depth may be scheduled to a named trigger with full depth as the default; and the triage timeline field accepts staged notes. The run also validated the core loop: seven of twenty-six decisions overrode the AI recommendation, and every override produced a more specific design.

## Revision note: v0.2 (Audited)

Version 0.2 incorporates a full audit of the 0.1 draft. Fixes: a wrong cross-reference in the Engineering template (operations pointed at the failure-modes section for the release path), a status vocabulary mismatch between the Conductor and the Decision Log (Superseded was missing), and duplicate entries in the hygiene word lists. Structural changes: the First Slice Brief became the Slice Brief, one template for every slice with filled briefs numbered SLICE-001 onward, plus an expansion loop in the Conductor; the Decision Log is now written continuously with a completeness check phase; triage asks whether code already exists and routes existing codebases through a mapping pass first; and a shape adaptations table remaps sections for games, libraries, CLIs, data systems, automations, and sites. Additions: accessibility and language coverage, licensing and user-facing legal lines, local setup reproducibility, a worked example exchange in guided mode, an explicit override rule for template hard rules, and guidance for running in small context windows.

## What is in the kit

| File | What it is |
|---|---|
| `01-CONDUCTOR.md` | The protocol. Hand this to any AI along with your project description. It runs the interview and fills out everything else. |
| `02-TEMPLATE-ARCHITECTURE.md` | The Architecture Document (ADD). The whole puzzle: modules, interfaces, data flow, technology, extension points. |
| `03-TEMPLATE-ENGINEERING.md` | The Engineering Document (EDD). The rules for placing pieces: requirements, data model, security, standards, verification, definition of done. |
| `04-TEMPLATE-DECISION-LOG.md` | The Decision Log. Every significant choice, its reasoning, and its revisit trigger, kept inside the project instead of scattered across old chats. |
| `05-TEMPLATE-SLICE-BRIEF.md` | The Slice Brief. The narrow section being built right now, specified so an agent can build it without touching the rest. The first slice proves the central idea. The same template drives every slice after it. |
| `06-CLAUDE-ADDENDUM.md` | Optional. Claude Code specifics: CLAUDE.md wiring, permissions, skills, verification hooks. The rest of the kit is agent-agnostic. |

One convention rides alongside the files: prior research and business planning (pricing hypotheses, validation thresholds, staged rollout) lives in a `PRODUCT-CONTEXT.md` companion. The Conductor mines it during the interview instead of letting it rot in chat history.

## Quick start

1. Copy the kit files into your project folder, or an empty folder if the project does not exist yet.
2. Open your AI of choice. Give it `01-CONDUCTOR.md` and the four templates, then describe what you want to build in a paragraph. Rough is fine. The interview exists to sharpen it.
3. Answer the questions, or choose fast-run at triage and review filled defaults in batches instead. The AI fills out the Architecture Document, the Engineering Document, the Decision Log, and the first Slice Brief. Then it builds only that slice.

Time expectations: a T1 project interview usually fits in one sitting. T2 takes a few sessions. T3 takes longer, and should. The Conductor's state block makes pausing and resuming safe.

## The flow

```
Your description
      |
      v
CONDUCTOR: intake and triage  ->  Triage Card (type, tier, team, experience, risk, starting point)
      |
      v
Architecture interview        ->  ARCHITECTURE.md    (the puzzle)
      |
      v
Engineering interview         ->  ENGINEERING.md     (the rules)
      |
      v
Decision completeness check   ->  DECISION-LOG.md    (the reasoning)
      |
      v
Slice selection               ->  SLICE-001-[name].md (the build boundary)
      |
      v
Audit pass, then build the slice. Verify with evidence.
Then loop: next slice brief, expand deliberately.
```

## Why documents at all

AI agents did not make engineering discipline obsolete. They made undisciplined engineering expensive at machine speed. A "minimum" viable product quietly becomes the permanent foundation, and every new feature forces the agent to reopen the finished puzzle: trace dependencies, reinterpret old decisions, migrate the database, patch around shortcuts that were never supposed to survive.

These documents are how judgment becomes legible to an agent. The agent gets explicit context, documented boundaries, clear acceptance criteria, and a verification standard where evidence counts and "the agent said it worked" does not.

## When not to use the kit

A true throwaway spike does not need scaffolding: something you build in an afternoon to answer one question and then delete. Delete it on schedule and the kit was never needed. The dangerous middle is the spike everyone knows is temporary, right up until real users depend on it and nobody is allowed to replace it. If a spike survives its question, it enters the kit through triage like any other existing codebase.

## Scaling honesty

The kit scales to the project. Triage assigns a tier, and sections collapse or expand to match. A weekend prototype is never dragged through enterprise ceremony, and a system that touches money or personal data is never allowed to skip the sections that matter. Risk flags override tier.

## Versioning the documents

Documents produced by this kit start at v0.1 Draft. When a document survives a full audit pass, bump it and mark it Audited, for example v0.2 (Audited). The Conductor explains the audit pass. Filled documents are living files: they change through the Decision Log, not through silent edits.
