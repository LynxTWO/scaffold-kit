# [PROJECT NAME] Slice Brief: SLICE-[NNN] [slice name]

Version: 0.1 Draft. Date: [date]. Status: [Proposed | Approved for build | In progress | Done with evidence].

```
SLICE STATE
Approved intent:  [brief version, approving name/date, or pending]
Source checked:   [commit or tree identity; relevant paths/triggers]
Milestone:        [M-n in progress, or none]
Next action:      [one concrete step]
Blocked by:       [decision IDs, spikes, external gates, or none]
Evidence so far:  [links to recorded checks, runs, packets]
Last audit:       [date]
```

Companions: ARCHITECTURE.md, ENGINEERING.md, DECISION-LOG.md. Update state at checkpoints. ADD section 15 names exactly one active brief by filename.

This brief bounds what may be built. Keep a short overview: what changes now, how we prove it, what waits, decisions needed, and next action. Use the Triage Card's Explanation depth; facts and gates do not change with audience.

**Compact form.** For a contained fix, retain only the short outcome, scope/exclusions, paths, state, section 8 acceptance table and approval. Omit unused headings and boilerplate with one combined reason; do not fill all twelve sections. Aim for a minute's reading, expanding only for a concrete risk. Update affected companions/pointers only, without a new document set or routine log entries. Delete guides and placeholders after filling.

## 1. What the slice proves

- **Outcome:** [central idea for the first product slice; capability or restored behavior for later work]
- **Why now:** [what someone gains, or what failure this fixes]

> **Interview guide. Delete after filling.** Ask what smallest observable result makes this work worth doing. A first product slice tests its central claim. A small fix need only restore its named behavior.

## 2. The walkthrough

[Steps from input or trigger to real result, including the relevant failure path. Use the actual interfaces and data inside the boundary.]

## 3. In scope, with build order

| Item | Notes |
|---|---|
| [capability or fix] | [links to the S-IDs it serves] |

For multi-week work, add milestones. Close every spike before dependent work and test the riskiest assumption first.

## 4. Out of scope, on purpose

[Name exclusions. Link a known extension point or decision only where useful; do not invent future features to fill a table.]

## 5. Stubs and their debts

[None, or each labeled stub outside the boundary, its current behavior, replacement trigger and D-ID. No stubs inside the behavior being proved.]

## 6. Modules and paths touched

[List relevant modules, files, interfaces and constraints, linked to ADD section 4 or the canonical observed map. Logical boundaries do not mandate new folders or services.]

## 7. Data subset and reviewed effects

[Relevant entities/fields from EDD section 5, or not applicable. Name schema, dependency, deletion, secret or deploy actions needing explicit approval. Record existing approval covering their targets and effects; do not request it twice.]

## 8. Acceptance criteria

| ID | Requirement | Criterion | Verified by | Gate |
|---|---|---|---|---|
| S-001 | R-001 | [observable success] | [test or reproducible check] | [CI check, exact calibrated gate, or manual: steps and result location] |
| S-002 | R-001 | [relevant failure path] | [check] | [gate or recorded manual check] |
| S-003 | R-001 | [relevant unlisted input and expected behavior] | [check] | [gate or recorded manual check] |

R-IDs come from EDD section 4.1. Keep only relevant rows. Each selected requirement has an S-row; each implementation item serves one. Empty checks are pending, not proof. Record outcomes beside these bindings or link canonical evidence; do not create a parallel ledger.

For user-facing work, review EDD section 4.4's relevant obligations here: truthful status, recoverable mistakes, neutral refusal, ownership/correction and honest defaults. Record a reason for any not-applicable obligation.

## 9. Verification evidence required

Per EDD section 11:

- [ ] Each S-ID has a reliable executed check and linked result. Automate meaningful behavior and regressions; recorded inspection may suffice for trivial prose or formatting.
- [ ] The walkthrough and relevant error paths ran, results recorded.
- [ ] Relevant EDD section 17 checks passed; skips and limits are stated.
- [ ] Verification serves named requirements and stays within their consequence. Any new harness, campaign or observer needs its own requirement ID.

A selected test or agent summary is not executed evidence.

## 10. Agent guardrails for this build

- Build only the approved outcome, paths and effects. Use the S-IDs to plan steps; the brief remains the contract.
- Carry forward explicit approval inside its reviewed boundary. New scope or effects need approval before dependent work.
- Separate discovery, implementation and verification. Switch back to implementation openly before fixing a verification failure.
- If code or documents contradict intent, pause dependent work. Record evidence, affected IDs, options and the smallest correction in DECISION-LOG.md; reconcile and approve changed intent before continuing.

## 11. Slice definition of done

- [ ] Acceptance checks pass with linked evidence, actual counts and skips.
- [ ] Diff and observed behavior match approved intent; removed behavior was deliberately preserved or approved for retirement.
- [ ] Affected docs, unknowns and pointers are current; useful consequential lessons recorded.
- [ ] Human acceptance recorded by [name]; cited evidence retained durably before scratch cleanup.

## 12. What this unlocks

[Known next candidate, or none yet. This is a direction, not an obligation to invent more work.]

*Approved for build by: [name], [date], brief version [version]. Approval of the idea is not approval of this brief. Progress and evidence can change without changing approved intent. When section 11 closes, mark Status: Done with evidence and update ADD section 15 and host pointers before activating the next brief.*
