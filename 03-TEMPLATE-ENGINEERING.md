# [PROJECT NAME] Engineering Document (EDD)

Version: 0.1 Draft. Date: [date]. Authors: [names]. Status: In interview.
Companion documents: ARCHITECTURE.md, DECISION-LOG.md, and the slice briefs (SLICE-001 onward).

This document is the rules for placing pieces: requirements, data, security, standards, verification, and the definition of done. The Architecture Document holds the puzzle itself. Facts live in one place: where a section depends on an architecture decision, it references the ADD section number instead of restating it.

**Template conventions.** Interview guide blocks are instructions to the AI and get deleted after filling. The Decision Block format is defined in ARCHITECTURE.md and used identically here.

---

## 1. One-Page Overview

- **Build philosophy in one line:** [for example: managed services, one language, evidence over claims]
- **The three goals that outrank the rest:** [from section 3]
- **The verification standard:** tests, logs, diffs, and observed behavior. An agent saying it worked is not a test result.
- **Current build boundary:** the active slice brief, per ADD section 15. Nothing outside it gets built without a Decision Log entry.

> **Interview guide. Delete after filling.**
> *Why:* the one-page overview is what an agent should re-read at the start of every session.
> *Ask:* nothing new. Write last, confirm with the human.

## 2. Engineering Principles

[5 to 8 short principles that settle arguments before they start.]

1. [for example: boring and mature beats novel until novelty pays rent]
2. [for example: every shortcut is labeled and logged, or it does not happen]
3. [for example: data has one owner, one shape, one source of truth]
4. [...]

> **Interview guide. Delete after filling.**
> *Ask:* what should win when speed and correctness fight? When cost and convenience fight? When a shortcut is tempting?
> *Default rule:* offer a starter set matching the Triage Card and let the human edit. Principles nobody chose get ignored later.

## 3. System Goals

[Quality attributes with numbers where numbers exist. Pick what matters; delete what does not.]

| Goal | Target | How measured |
|---|---|---|
| Fast | [for example: core screen interactive under N seconds] | [tool or log] |
| Reliable | [for example: core loop completes N percent of attempts] | [metric] |
| Secure | [baseline per section 7] | [audit checklist] |
| Low operating cost | [monthly ceiling at launch] | [billing review] |
| Maintainable | [a newcomer ships a small change in under a day] | [observed] |
| Accessible | [core flows work by keyboard and with assistive tech, platform conventions respected] | [manual pass or tooling] |
| Observable | [every failure of the core loop leaves a trace] | [log review] |

> **Interview guide. Delete after filling.**
> *Why:* goals without numbers are moods. Numbers make "done" and "good" checkable.
> *Ask:* which three of these would you protect if you could only protect three? Then set a number or an observable test for each kept goal.
> *Tier:* T1 keeps 3 to 4 goals. T3 keeps most and adds compliance-driven ones from risk flags.

## 4. Requirements Ledger

[What the system must do, separated by confidence. This is requirements discipline: known constraints are not the same as assumptions or hopes.]

### 4.1 Confirmed requirements
| ID | Requirement | Acceptance test |
|---|---|---|
| R-001 | [the system must ...] | [observable pass condition] |

### 4.2 Assumed requirements
| ID | Assumption | How it gets verified |
|---|---|---|
| A-001 | [we believe users need ...] | [test, interview, or usage data] |

### 4.3 Open questions
| ID | Question | Blocks what | Close by |
|---|---|---|---|
| Q-001 | [unresolved item] | [feature or section] | [trigger or date] |

**Ledger rules.** Every requirement has an acceptance test stated as an observable condition. Assumptions never silently become requirements: they get verified and promoted, or corrected. Open questions must close before anything they block gets built.

> **Interview guide. Delete after filling.**
> *Ask:* walk each feature area of the core loop. For each: is this known, believed, or unknown? What would prove it?
> *If a product context companion exists:* mine its validation thresholds and pricing hypotheses into Assumed requirements with verification plans.
> *Open questions:* when the evidence is a build experiment, schedule it as a spike per the Conductor: time box, success test, closed before dependent work.
> *Format for acceptance tests:* given a starting state, when the user acts, then the observable result. Plain sentences are fine.
> *Tier:* all tiers. This section never collapses. At T1 it may be short, never absent.

## 5. Data Model

[Field-level truth for the entities named in ADD section 7.]

Per entity:

```
ENTITY: [name]
Purpose: [one line]
Owned by: [module, per the ADD module map]
Fields: [name, type, required or optional, constraint]
Relations: [plain sentences]
Deletion rule: [what happens when this is deleted, cascades and orphans]
```

**Model rules.**
- Schema changes happen only through migrations, at every tier.
- Identifiers, timestamps, and time zones: [state the conventions once, for example UTC everywhere, timestamps on every table].
- [Any domain-specific integrity rule from the interview.]

> **Interview guide. Delete after filling.**
> *Why:* a working screen is not proof the data model makes sense. This section is where the model is forced to make sense before screens exist.
> *Ask:* per entity: what fields must exist at creation? What must never be null? What happens on delete? What connection, if broken, corrupts the product?
> *Tier:* all tiers. T1 may model only the slice's entities fully and sketch the rest.

## 6. Permissions and Access Model

- **Roles:** [list, one line each]
- **Access matrix:**

| Role | [Resource] | [Resource] |
|---|---|---|
| [role] | [read | write | none] | [...] |

- **Enforcement point:** [where rules are enforced, one place, per ADD]
- **Admin surface:** [what admins can see and do, and what is logged when they do]

> **Interview guide. Delete after filling.**
> *Ask:* who can see whose data? Who can change it? Where is that enforced so it cannot be bypassed by a new feature?
> *Tier:* T2+, forced to full depth by any risk flag. T1 single-user tools state "single user, local data" and mark it Confirmed.

## 7. Security Requirements

[Tiered baseline. Risk flags force the higher tier regardless of project tier.]

**Tier 1 baseline, every project:**
- [ ] Secrets live outside the code and outside version control.
- [ ] Passwords, if any, are handled by a managed provider, never stored by hand. Per ADD 8.5.
- [ ] All network traffic uses encrypted transport.
- [ ] Input is validated at every boundary where data enters the system.
- [ ] Keys and tokens carry the narrowest scope that works.
- [ ] Backups exist for anything the human would mourn.

**Tier 2 adds:**
- [ ] Rate limiting on public endpoints.
- [ ] Dependency vulnerability scanning on a schedule.
- [ ] An audit trail for sensitive actions.
- [ ] Defined session and token lifetimes.

**Tier 3 adds:**
- [ ] A written threat model: assets, attackers, entry points.
- [ ] Incident response steps: detect, contain, notify, learn.
- [ ] Periodic access reviews.
- [ ] [Compliance items driven by risk flags: name the regime and its requirements.]

> **Interview guide. Delete after filling.**
> *Ask:* what is the most damaging thing a hostile stranger could do with this system? What is the most damaging accident an authorized user could have? Convert answers into checklist items.
> *Protect:* anything touching payments, health data, or minors is irreversible-class. Explicit confirmation on every related choice.

## 8. Privacy and Data Handling

- **Personal data inventory:** [each field of personal data, why it is collected, where it lives]
- **Retention:** [how long each class of data lives, and what deletes it]
- **User deletion:** [what a user can delete themselves, and what full deletion means]
- **Sharing:** [every third party that receives user data, and what they receive]
- **User-facing legal:** [T2+ with real users: a privacy policy and terms exist and are linked from the product before launch; risk flags may add regime-specific documents]

> **Interview guide. Delete after filling.**
> *Default rule at every tier:* collect the minimum. Every personal field must answer "why do we need this at all?"
> *Tier:* T1 with no personal data states that in one line and moves on. Any personal-data risk flag forces full depth.

## 9. Coding Standards

- **Language and typing:** [per ADD 8.2, plus the strictness posture]
- **Naming:** [conventions for files, functions, variables, and database objects]
- **Functions:** [size posture, single-purpose rule, input validation expectations]
- **Errors:** [errors are handled or deliberately propagated, never swallowed; user-facing errors are written for humans]
- **Logging:** [levels, what always gets logged, what never gets logged: secrets, tokens, personal data]
- **Comments:** [comments say why, not what; stale comments are bugs]
- **Accessibility:** [platform accessibility conventions are the floor; interactive elements are labeled; core flows verified per the section 3 goal]
- **User-facing text:** [lives in one location per platform convention, per the language decision in ADD section 3]
- **Formatting:** [automated by a formatter; style debates are settled by tooling, not opinion]
- **AI-generated code:** held to every rule above and reviewed with the same care as human code. Authorship is not an excuse either direction.

> **Interview guide. Delete after filling.**
> *Default rule:* offer the conventional set for the chosen language, human edits. Do not invent exotic conventions.
> *Tier:* all tiers, short at T1.

## 10. Repository Organization

- **Top-level layout:** [folders and their single purpose]
- **Feature organization:** [by feature, by layer, or hybrid, and why]
- **Shared code location:** [where shared types, utilities, and interface definitions live: one place]
- **Dependency direction:** [restate the ADD rule by reference: see ADD section 4]
- **Documentation locations:** these documents live in [path], and agents read them before working.
- **Setup:** [written steps take a clean machine to a running local instance; the steps are re-tested whenever they change]

> **Interview guide. Delete after filling.**
> *Why:* context discipline. Decisions live in the project where the next agent will find them, not across fifty dead chats.
> *Default rule:* the conventional layout for the chosen stack. Novel layouts need a logged reason.

## 11. Testing and Verification

[Verification discipline: evidence, not confidence.]

**The standard.** A claim of "working" requires at least one of: a passing automated test, a log line showing the behavior, a diff plus observed output, or a reproducible manual script with its result recorded. An agent's summary of its own work is a claim, not evidence.

**Test types by tier.**
- **T1:** automated tests on the core loop and on anything that has already broken once. A written manual test script for the rest.
- **T2:** unit tests on logic, integration tests on module seams, a smoke test that runs the core loop end to end, all wired into CI.
- **T3:** T2 plus load tests against section 3 targets, security scanning, and a staging soak before release.

**Verification ledger.** Every Confirmed requirement in section 4 maps to a check:

| Requirement | Check | Evidence lives |
|---|---|---|
| R-001 | [test name or script step] | [CI run, log path, or recorded result] |

**Test data rule.** [How realistic test data is produced, and the rule that production data never lands in development unmasked.]

> **Interview guide. Delete after filling.**
> *Ask:* what already worries you most about being wrong? Test that first. What broke in projects like this before? Test that second.
> *Tier:* the ledger exists at every tier. Its size scales; its existence does not.

## 12. Tool and Agent Discipline

[Rules for AI agents working in this repository. More tools do not create better work. They create more ways to make a mistake before anyone notices.]

**Modes.** Work happens in one mode at a time, with the narrowest permissions that mode needs:

| Mode | Purpose | Allowed | Not allowed |
|---|---|---|---|
| Discovery | understand | read files, read docs, run read-only queries | writes of any kind |
| Planning | decide | write to documents | code, installs, schema changes |
| Implementation | build | write code inside the agreed boundary | deploys, deletions outside boundary |
| Verification | prove | run tests, read logs and diffs | "fixing while verifying" without a logged switch back |

**Standing rules.**
- Read before writing. Inspect before modifying.
- One purpose per tool call. A vague prompt must not research the market, choose the architecture, install packages, migrate the database, rewrite the UI, and deploy.
- Stop and ask before: schema changes, new dependencies, deletions, anything touching secrets, and any deploy.
- The current build boundary is the active slice brief, SLICE-NNN, per ADD section 15. Work outside it requires a Decision Log entry first.
- When evidence contradicts the plan, stop and surface it. Do not patch silently around a wrong assumption.

> **Interview guide. Delete after filling.**
> *Ask:* which actions should always require your explicit approval? Add them to the stop list.
> *Tier:* all tiers. This section is the point of the kit.

## 13. Observability (T2+)

- **Logging vs analytics:** logs answer "what happened in the system," analytics answer "what are users doing." They are separate streams.
- **Always logged:** [errors with context, the core loop's completion and failure, external calls and their outcomes]
- **Never logged:** secrets, tokens, raw personal data.
- **Dashboards or checks:** [the few numbers reviewed on a schedule, per section 3]
- **Alerts:** [what pages a human, and what merely gets recorded]

> **Interview guide. Delete after filling.**
> *Default at T1:* structured error logging plus one "core loop succeeded" log line. Stated, Confirmed, done.

## 14. Operations and Deployment

- **Environments and release path:** per ADD section 12, by reference.
- **CI gates:** [what must pass before merge: tests, lint, format, hygiene checks]
- **Migrations:** [how schema changes are applied and reversed]
- **Configuration:** [where environment configuration lives, and the rule that code never contains environment secrets]
- **Release checklist:** see section 17.

> **Interview guide. Delete after filling.**
> *Tier:* T1 states its minimal path in three lines. T2+ fills every field.

## 15. Cost Discipline

- **Monthly ceiling at launch:** [number from the budget posture]
- **Managed first:** build only what creates differentiated value; rent the rest. Exceptions get a Decision Block.
- **Cost triggers:** [the usage or billing thresholds that force a review, for example AI spend above N per month]
- **Engineering time is a cost:** [the rule for build vs buy arguments]

> **Interview guide. Delete after filling.**
> *Ask:* what monthly bill would make you wince? Work backward from that number.
> *Tier:* all tiers. Near-zero budgets make this section more important, not less.

## 16. Risk Register and Unknowns

| ID | Risk or unknown | Impact if wrong | Verification or mitigation | Status |
|---|---|---|---|---|
| U-001 | [assumption or risk] | [what breaks] | [how we find out or soften it] | [Open | Watching | Closed] |

**Rule.** Every Assumed decision and every Open question from any document appears here. This table is reviewed at every document audit.

> **Interview guide. Delete after filling.**
> *Why:* recorded unknowns are a plan. Hidden unknowns are a countdown.

## 17. Definition of Done

**Per change:**
- [ ] Builds clean, lints clean, formatted.
- [ ] Tests exist for the change and pass. Evidence linked per section 11.
- [ ] Errors on the new path are handled and logged.
- [ ] No secrets, no debug leftovers, no dead code introduced.
- [ ] Documents and Decision Log updated if any decision changed.
- [ ] Reviewed. At T1 solo, that means a deliberate self-review pass against this checklist, not a skim.

**Per release:**
- [ ] Migrations applied and reversible.
- [ ] Rollback path confirmed per ADD section 12.
- [ ] Monitoring or checks in place per section 13.
- [ ] Version tagged, one-line changelog entry written.
- [ ] Human approval recorded. Final approval for release rests with [name or role].

> **Interview guide. Delete after filling.**
> *Ask:* who holds final approval? What would you add to these lists from past scar tissue?

## 18. Change Control

- **Document versions:** documents start at v0.1 Draft. A full audit pass bumps the version and marks it Audited.
- **The audit pass:** reread against the Conductor's Phase 6 checklist: statuses complete, references resolve, unknowns current, hygiene clean.
- **Status lifecycle:** Proposed becomes Confirmed or is replaced. Assumed is verified or corrected. Open closes before dependent work. Deferred reopens on its trigger.
- **No silent edits:** decision changes travel through DECISION-LOG.md. The documents state what is true now; the log preserves how it got that way.

> **Interview guide. Delete after filling.**
> *Why:* a document nobody trusts is worse than no document. Change control is what keeps these files worth reading in month six.

---

*End of Engineering Document template. Sections filled: [n of 18]. Unknowns carried: [n]. See DECISION-LOG.md for reasoning.*
