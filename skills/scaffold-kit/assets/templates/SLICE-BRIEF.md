# [PROJECT NAME] Slice Brief: SLICE-[NNN] [slice name]

Version: 0.1 Draft. Date: [date]. Status: [Proposed | Approved for build | In progress | Done with evidence].

```
SLICE STATE
Milestone:        [M-n in progress, or none]
Blocked by:       [decision IDs, spikes, external gates, or none]
Evidence so far:  [links to ledgers, runs, packets]
Last audit:       [date]
```

The state block is the slice's resume point, the same way the Conductor's INTERVIEW STATE block is the interview's. Update it at every checkpoint; do not invent status tokens elsewhere.
Companion documents: ARCHITECTURE.md, ENGINEERING.md, DECISION-LOG.md.

One narrow, production-quality section, small enough to test and structured so the next pieces connect without smashing the existing architecture apart. This document is the agent's build boundary: if it is not in here, it does not get built. The first slice (SLICE-001) proves the central idea. Every later slice uses this same template through the Conductor's expansion loop, and exactly one slice is active at a time, named in ADD section 15.

---

## 1. What the slice proves

- **Central claim (SLICE-001) or capability added (later slices):** [the one thing that, if true, makes this project worth continuing; or the specific capability this slice adds and why it is next]
- **The slice in one line:** [a user can register, do X once, and get Y]
- **Honest stakes:** for SLICE-001: if real users go through this slice and it fails to deliver value, the project deserves a rethink. If that sentence feels too strong, the slice is too small to prove anything. For later slices: if this capability did not exist, what would users be unable to do?

> **Interview guide. Delete after filling.**
> *Ask, first slice:* strip everything away. What is the single workflow that makes someone say "I would use this again"? That workflow is the slice. Everything else waits.
> *Ask, later slices:* which extension point from ADD section 10 is this, and why now instead of the alternatives?

## 2. The walkthrough

[The complete path, step by step, exactly as a real user experiences it.]

1. [user arrives, how]
2. [user does the one thing]
3. [system produces the one result]
4. [user takes one meaningful action on the result]

Every step above must work end to end against the real architecture: real interfaces, real data module, real persistence. No bypasses inside the boundary.

## 3. In scope, with build order

| Item | Notes |
|---|---|
| [capability] | [production quality, per EDD standards] |

For multi-week slices, add the build-order table: sequenced milestones so the riskiest proof lands first and every spike closes before the milestone that depends on it.

| Milestone | Contents |
|---|---|
| M1 | [engine-critical work and any spikes] |
| M2 | [...] |

## 4. Out of scope, on purpose

| Excluded | Where it will connect later | Log entry |
|---|---|---|
| [feature] | [extension point, per ADD section 10] | D-[n] |

**Rule.** Out-of-scope items are named, not implied. Silence is how "minimum" quietly becomes the permanent foundation.

## 5. Stubs and their debts

| Stub | Real version arrives when | Behavior for now | Log entry |
|---|---|---|---|
| [for example: one hardcoded provider] | [trigger] | [what the stub does] | D-[n] |

Stubs live outside the slice boundary and are labeled in code. Inside the boundary, nothing is a stub.

## 6. Modules touched

Per the ADD module map: [list modules the slice builds, and the interfaces it exercises]. The slice must pass through the real seams. A slice that bypasses the architecture proves nothing about the architecture.

## 7. Data subset

[The entities and fields from EDD section 5 that must exist for the slice, in full production shape: migrations, constraints, deletion rules included.]

## 8. Acceptance criteria

[Each one observable. These are the finish line, agreed before building starts.]

| ID | Criterion | Verified by | Gate |
|---|---|---|---|
| S-001 | [given, when, then] | [test or scripted check] | [CI check name, anti-dark-code capability ID or exact gate] |
| S-002 | [error path: given a failure at step N, the user sees ...] | [test] | [gate] |
| S-003 | [unlisted input: an input the brief never mentions that the slice must still survive, with the expected behavior] | [test] | [gate] |

The Gate column is what binds a pull request's checks to these IDs. A row with an empty Gate is a criterion nobody can prove mechanically; say so or fill it.

For a slice with users, the relevant obligations from EDD section 4.4 appear here as rows: truthful status, a recoverable mistake, a dignified refusal, an ownership or correction path, an honest default. A principle that does not apply to this slice is named as such in one line.

## 9. Verification evidence required

Per EDD section 11. Before this slice is called done, the following exist and are linked:

- [ ] Automated tests covering each acceptance criterion, passing in CI or a recorded run.
- [ ] The core walkthrough executed against a clean environment, result recorded.
- [ ] Error paths exercised, at minimum: [the top two failures from ADD section 13].
- [ ] EDD section 17 per-change checklist satisfied for every change in the slice.
- [ ] Verification effort stayed inside EDD section 11's bound: any harness, campaign or observer built for this slice has its own requirement ID, and none of them is the slice.

An agent's statement that the slice works is a claim. This list is the evidence.

## 10. Agent guardrails for this build

- **Boundary:** only the modules in section 6, only the data in section 7.
- **Stop and ask before:** schema changes beyond section 7, new dependencies, deletions, deploys. Per EDD section 12.
- **Mode separation:** discovery, then implementation, then verification. No single prompt spans all three.
- **Step-level planning:** the brief is the boundary, not the plan. Implementation planning for a milestone may use a step-level planner (for example a writing-plans skill); the plan cites the S-IDs it satisfies and stays inside sections 6 and 7.
- **Conflicts:** if reality contradicts these documents, stop and surface it. Update through the Decision Log, then continue.

## 11. Slice definition of done

- [ ] All acceptance criteria pass with linked evidence.
- [ ] All EDD guardrails hold. No unlabeled shortcuts inside the boundary.
- [ ] Documents updated: statuses, unknowns, log entries for anything learned.
- [ ] Human walkthrough completed and approved by [name].

## 12. What this unlocks

[The next one or two candidate slices, one line each, connecting at the extension points named in ADD section 10. Not a commitment. A direction. The expansion loop in the Conductor picks the next one from here.]

---

*Approved for build by: [name], [date]. Until then, this brief is a proposal, and no implementation starts: approval of the idea is not approval of the brief. When section 11 closes with evidence, mark the status Done and update ADD section 15 before opening the next brief.*
