# Changelog

## 0.4.2 (unpublished preview candidate)

- Include the approved Living Blueprint brief in light and dark; refresh version labels and PDF provenance. Instructions, templates, safeguards and stable catalog pins are unchanged.
- Advance only the separate opt-in preview catalog after final package checks. No remote tag, release, asset upload or directory submission is authorized by this preparation.

## Unreleased improvements to 0.4

- Apply guided depth in generated compact briefs, explain identifiers and pending owner questions in existing sections, retain legacy check-header compatibility, and report unsupported dependencies without inventing reasons. Preserve status vocabulary, exact approval requirements and compact length limits.
- Clarify storage choices, recipe exclusions/recovery tradeoffs and closeout evidence; fix the skill validator's unsupported frontmatter without adding instructions. Source-bound trials, failures, repairs and scoped owner feedback remain in the dated evaluation records.
- Include Scaffold Kit artwork in the portable and Codex manifests and the Claude listing metadata. Record permanent local installs and host display limits in `evals/scaffold-v1/evidence-2026-10-14-packaging.json`. Public evidence copies redact local machine paths and private participant names; original hashes and scores are retained.
- Extend the existing depth choice to documents: guided/plain language, standard/balanced, expert/developer shorthand. Reuse one project choice and canonical document set, with unchanged evidence and approval gates.
- Route next slices and contained fixes through a compact existing brief. Bind handoffs to approved intent, source, next action and evidence; reconcile conflicts and scope changes explicitly.
- Add `kit_audit.py --ready` for companions, one current slice and R/S/check bindings. Reject empty input, duplicate decision IDs, status disagreement, missing exact subsections and invalid slice status. Keep partial audits for interviews.
- Remove module-count floors and required speculative expansions. Require proportionate recorded checks rather than automated tests for trivial prose changes.
- Clarify canonical unknowns, freshness, document indexes, historical records, scratch folders and cited evidence retention. Fix the old Claude Conductor path and use `Done with evidence` consistently.
- Review fixes: `--ready` accepts a linked or described Current slice filename. It rejects TBD, pending, N/A or bare `manual:` checks, duplicate requirement IDs, and an approved or in-progress brief without a named approver. Briefs marked `Done` under the earlier footer stay valid. The Triage Card has a home in the ARCHITECTURE.md header; a depth change rewrites other documents only on request. Next slices and contained fixes skip the slice growth tally. A brief resumes only from its SLICE STATE, and compact briefs link decision entries instead of repeating their options. Approval lines need a name and date on the same line, and a named brief version must match the brief; TODO, N/A and explicit non-approval are rejected. Fresh trials are in `evals/scaffold-v1/evidence-2026-10-12.json`. The Claude addendum no longer asks for plan mode, which cannot save the documents.
- Existing 0.4 documents: partial audits now also report inexact section numbers, duplicate IDs, disagreeing statuses and unknown slice statuses. Before the first `--ready`, name the active brief's filename in ADD section 15 and add a Requirement column of EDD 4.1 R-IDs to its section 8 table. Completed briefs need no edits.

- Follow-up planning fixes: an explicitly requested offline plan drafts questions, assumptions, Proposed choices and a candidate slice without granting approval. Small features as well as contained fixes use a compact brief, normally 250 to 400 words and at most 500 unless a named risk requires more. Keep each fact once; preserve requirement/check bindings, reviewed effects and approval. Fresh source-bound trials and remaining rubric limits are in `evals/scaffold-v1/evidence-2026-10-12-lean.json`.

- Recipe follow-up: put requested/planned exclusions and known connections in the existing brief's table; compare recovery choices in their own Decision Log entry. Keep no-stubs valid and approval pending. Source-bound comparisons are in `evals/scaffold-v1/evidence-2026-10-12-recipe.json`.

- Open-choice follow-up: use plain benefit/cost clauses in the existing log for significant unresolved choices, with owner questions and blockers linked. The entry template and its shorter Open example keep owner choices unresolved. Evaluation rubric revision 2 requires labeled stubs/payback only when needed; previous scores remain recorded. See `evals/scaffold-v1/evidence-2026-10-12-choices.json`.

These are unreleased source changes. Local consumer installation was checked; no public release or directory submission has been made.

## 0.4.0 (Draft)

- Package the kit as an agent skill under `skills/scaffold-kit/`: `SKILL.md` entry, the Conductor and Claude addendum under `references/`, the four templates under `assets/templates/` without numeric prefixes, a Claude Code plugin manifest and single-entry marketplace, and an Agent Plugins manifest.
- Engineering Document section 11: bound verification effort by the consequence of the requirement it proves; a harness, campaign or observer is a build item with its own requirement ID. State that decision statuses and claim confidence are two vocabularies. Section 16: anti-dark-code unknowns and coverage rows land here as `U-` rows.
- Slice Brief: a SLICE STATE block; a Gate column and an unlisted-inputs row in the acceptance table; an evidence-bound checkbox; a step-level-planner line in the guardrails; the approval footer says that idea approval is not brief approval.
- Decision Log: rule 6, evidence stays out of entries and the index stays a one-page view.
- Conductor: the brownfield procedure points at the anti-dark-code artifacts; a spoken build gate after slice selection; a mechanical-audit line in the Phase 6 checklist; three failure modes to refuse (sunk cost, unrequested harnesses, "too obvious" briefs).
- New reference `working-with-anti-dark-code.md`: map artifacts and where they land, the vocabulary mapping, acceptance-to-gate binding, proportionality, one protected-areas list, hygiene and the audit as a gate.
- New `scripts/kit_audit.py` with tests: banned punctuation and words, decision-block and log statuses, index and entry agreement, superseded links both ways, section cross-references, state block while in interview.
- Claude addendum: current documentation URL, an unattended-agents-never-touch list in the `CLAUDE.md` stub, packaging text replaced by the skill layout.
- License: FSL-1.1-MIT, in the repository root and inside the skill directory.

## 0.3 (Field-Tested), 2026-07-30

- Imported as the initial commit of this repository. See the README revision notes.
