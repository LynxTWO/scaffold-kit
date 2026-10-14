# [PROJECT NAME] Slice Brief: SLICE-[NNN] [slice name]

Version: 0.1 Draft. Date: [date]. Status: [Proposed | Approved for build | In progress | Done with evidence].

```
SLICE STATE
Approved intent:  [brief version, approving name/date, or pending]
Source checked:   [source identity; paths/triggers]
Milestone:        [M-n in progress, or none]
Next action:      [one concrete step]
Blocked by:       [D-IDs, spikes, gates, or none]
Evidence so far:  [recorded checks/runs]
Last audit:       [date]
```

Companions: Architecture Document (ADD), ARCHITECTURE.md; Engineering Document (EDD), ENGINEERING.md; DECISION-LOG.md. Update SLICE STATE; no INTERVIEW STATE. ADD 15 names one active brief.

Apply Triage Card depth to the written brief. Guided: spell out every used abbreviation, including in the project name (CLI means command-line tool), and explain each used ID prefix once, including A for assumptions and U for unknowns. Describe included actions as behavior the reader can observe. Explain necessary builder terms once in their existing section. Preserve facts, gates, dates, audit state and source identity.

**Compact form.** Keep header/state, outcome, scope/exclusions, paths/effects, section 8, D-links and approval. Aim for 250 to 400 words; max 500 including state/tables unless a named risk needs essential decision detail. Delete unused guides/headings. Record omitted section/table numbers and one combined reason in existing linked planning/audit evidence, otherwise a labeled footer before approval. D-links ask plain owner questions; options, recommendations and conditional answers stay in the log. Concrete scope, baseline facts and inspected R/S-ID results may remain; link rules/evidence. Run the partial audit, resolve findings and count the whole brief. Preserve uncertainty, checks and approval.

## 1. What the slice proves

[Outcome and why now: central claim, new capability or restored behavior.]


## 2. The walkthrough

[Input/trigger through result and failure path, with actual interfaces/data.]

## 3. In scope, with build order

| Change | What the user sees; S-IDs |
|---|---|
| [capability or fix] | [plain action and preserved behavior; S-IDs] |

Add milestones for multi-week work; close spikes before dependent work, testing the riskiest assumption first.

## 4. Out of scope, on purpose

| Excluded capability | Known later connection or decision |
|---|---|
| [requested or planned later capability] | [existing module, interface, entity or D-ID] |

Keep this table when such exclusions exist. State permanent non-goals separately; do not invent future work or stubs to fill rows.

## 5. Stubs and their debts

[None, or each labeled stub outside the boundary, its current behavior, replacement trigger and D-ID. No stubs inside the behavior being proved.]

## 6. Modules and paths touched

[Known affected files/interfaces/constraints; link ADD 4 or observed map. Unsettled storage locations belong only in D-entries, even conditionally. No mandatory folders/services.]

## 7. Data subset and reviewed effects

[EDD 5 entities/fields, or none. Name schema/dependency/deletion/secret/deploy approvals; carry approval for reviewed targets/effects.]

## 8. Acceptance criteria

| ID | Requirement | Criterion | How it will be checked | Gate |
|---|---|---|---|---|
| S-001 | R-001 | [observable success] | [test or reproducible check] | [CI/calibrated gate, or manual: steps/result location] |
| S-002 | R-001 | [relevant failure path] | [check] | [gate/manual check] |
| S-003 | R-001 | [unlisted input and expected behavior] | [check] | [gate/manual check] |

Use EDD 4.1 R-IDs; each selected requirement has an S-row and each implementation item serves one. Empty checks are pending. Record results here or link canonical evidence.

For user-facing work, apply EDD 4.4 obligations; explain any not applicable.

## 9. Verification evidence required

Link EDD 11/17 checks to executed S-ID results, counts, skips and limits. Trivial prose may use inspection; summaries are not execution. New verification infrastructure needs an R-ID.

## 10. Agent guardrails for this build

Follow EDD 12 modes and approved paths/effects. Approve new scope; reconcile contradictions with evidence, IDs and options in DECISION-LOG.md before resuming.

## 11. Slice definition of done

- [ ] Checks pass; diff/behavior match intent, including approved retirement.
- [ ] Docs, unknowns and pointers are current; consequential lessons recorded.
- [ ] Human acceptance: [name]; retain cited evidence before scratch cleanup.

## 12. What this unlocks

[Next candidate, or none; invent no work.]

*Approved for build by: [name], [date], brief version [version]. Approval of the idea is not approval of this brief.*

Evidence updates preserve intent. At completion, mark Done with evidence; update ADD 15 and host pointers before another brief.
