# [PROJECT NAME] Architecture Document (ADD)

Version: 0.1 Draft. Date: [date]. Authors: [names]. Status: In interview.
Companion documents: ENGINEERING.md, DECISION-LOG.md, and the slice briefs (SLICE-001 onward).

This document is the puzzle: what the system is, what its major pieces are, how they connect, and where future pieces will attach. The Engineering Document holds the rules for placing pieces. Where the two conflict, this document's guardrails control.

**How this template works.** Blocks that begin with "Interview guide" are instructions to the AI running the Conductor protocol. They are not part of the final document. The AI asks, fills the skeleton, records Decision Blocks, then deletes the guide. Placeholders in [brackets] get replaced or removed.

**Decision Block format.** Used everywhere a significant choice is made, and copied into the Decision Log:

```
DECISION: [short name]
STATUS: Confirmed | Proposed | Assumed | Open | Deferred
CHOICE: [what was chosen]
BECAUSE: [2 to 4 plain lines]
OPTIONS CONSIDERED: [each with a one-line tradeoff]
AI RECOMMENDATION DIFFERED: [optional; include when the human overrode the
        recommendation, naming the declined option]
REVISIT WHEN: [the trigger that reopens this]
```

---

## 1. One-Page Overview

[The whole puzzle on one page. If it does not fit on one page, it is not yet understood.]

- **What it is:** [two sentences]
- **Who it is for:** [primary user, secondary users]
- **The core loop:** [user enters, does what, gets what value]
- **Major pieces:** [module names only, 5 to 9 of them]
- **Current slice:** [one line naming it, detail lives in the current slice brief]
- **What this is not:** [two or three explicit exclusions]

> **Interview guide. Delete after filling.**
> *Why:* anyone, human or agent, should understand the system in one page before touching anything.
> *Ask:* nothing new. Write this section last, from everything below, then read it back to the human for confirmation.

## 2. System Context

[Who and what touches this system from outside.]

- **Actors:** [user roles, admin roles, other humans]
- **External systems:** [services, data providers, platforms this system talks to]
- **Boundary statement:** [one paragraph: what is inside this system's responsibility and what is explicitly outside it]

> **Interview guide. Delete after filling.**
> *Why:* half of all scope creep is boundary confusion. Naming the outside is as valuable as naming the inside.
> *Ask:* who uses this? Who administers it? What existing systems must it talk to? What nearby problems are we deliberately not solving?
> *Tier:* all tiers. Short at T1.

## 3. Product Shape and Platforms

- **Shape:** [app | service or API | CLI | library | data system | game | automation | site | mixed]
- **Platform targets:** [for example iOS and Android, web, desktop, server only]
- **Offline behavior:** [required | degraded | not applicable]
- **Distribution:** [app stores, package registry, web deploy, internal only]
- **Languages at launch:** [one language | list. Even "one for now" is a decision: user-facing text kept in one place makes translation later a move, not a rewrite]
- **Code license:** [proprietary | open source, which license]

DECISION: Product shape and platforms
[Decision Block]

> **Interview guide. Delete after filling.**
> *Why:* shape drives every technology decision below. Get it wrong here and section 8 is fiction.
> *Ask:* where do your users already live? Does this need to work without a network? How does it reach people? Any language, store policy, or licensing constraint from day one?
> *Options:* pull from the Triage Card project type, confirm rather than re-ask.
> *Default rule:* fewest platforms that reach the primary user. Multi-platform is a cost, not a virtue.

## 4. Module Map

[The major systems. Each module is a puzzle region with one owner and one job.]

| Module | Responsibility | Owns what data | Talks to |
|---|---|---|---|
| [name] | [one line] | [entities] | [modules, externals] |

**Module rules.**
- Every module has exactly one primary responsibility.
- Every piece of data has exactly one owning module. Others read through interfaces.
- Dependency direction: [state it, for example UI depends on services, services depend on data, never the reverse].

> **Interview guide. Delete after filling.**
> *Why:* this table is the map an agent consults before touching anything. Vague module boundaries are how agents smash the puzzle apart.
> *Ask:* walk the core loop and name each system it passes through. Then name the supporting systems: auth, notifications, admin, analytics.
> *Options:* typical counts are 5 to 9 modules at T1 and T2. More than 12 at any tier is a smell. Fewer than 4 for a real product usually means hidden coupling.
> *Tier:* all tiers. This section never collapses.

## 5. Interfaces and Contracts

[How modules talk. The seams of the puzzle.]

- **Interface style:** [function calls in one codebase | internal API | public API | events | mixed]
- **Public interfaces:** [list each module's public surface in one line each]
- **Contract rule:** [where interface shapes are defined and validated, one source of truth]
- **Versioning posture:** [how breaking changes to interfaces are handled]

DECISION: Interface style
[Decision Block]

> **Interview guide. Delete after filling.**
> *Why:* extension points only work if seams are explicit. An agent adding a feature should extend an interface, not reach around it.
> *Ask:* is this one deployable thing or several? Does anything outside your own code call in? Do interface shapes need to survive version skew between client and server?
> *Default rule:* T1 and most T2: one codebase, typed function boundaries, one shared types location. Public APIs only when an external consumer exists or is a named future feature.
> *Tier:* versioning posture is T2+.

## 6. Core Data Flow

[The main journey from input to value, step by step.]

1. [step]
2. [step]
3. [step]

- **Trigger points:** [what starts work: user action, schedule, event, webhook]
- **Slow paths:** [anything async or long-running, and how the user experiences the wait]
- **Failure path:** [what the user sees when a step fails, one line per fragile step]

> **Interview guide. Delete after filling.**
> *Why:* the flow reveals missing modules and hidden dependencies before code exists.
> *Ask:* narrate one real use from open to done. Where does data enter, transform, persist, and return? What runs on a schedule instead of a click?
> *Tier:* all tiers. T3 adds a flow per major workflow, not just the core loop.

## 7. Data Domain Overview

[The major entities and how they relate. High level only. Field-level detail lives in ENGINEERING.md section 5.]

- **Entities:** [name each, one line of purpose]
- **Key relationships:** [plain sentences, for example a user has many projects, a project belongs to one workspace]
- **Volume expectations:** [rough counts at launch and at success]

> **Interview guide. Delete after filling.**
> *Why:* relationship density is the main input to the database decision in section 8.
> *Ask:* what are the nouns of this system? Which connections must never break? How much of each thing exists at launch, and at success?
> *Tier:* all tiers.

## 8. Technology Selection

[One Decision Block per layer. Categories are stable; specific products change. The AI running the interview supplies current candidates inside each category and flags anything it is unsure is current.]

### 8.1 Client
Categories: web app | native mobile | cross-platform mobile | desktop | terminal | game engine.
Criteria: audience devices, team skills, rendering ceiling, offline needs, store distribution.
DECISION: Client technology
[Decision Block]

### 8.2 Language
Criteria: team fluency first, ecosystem for the shape second, type safety posture third.
DECISION: Primary language
[Decision Block]

### 8.3 Backend
Categories: none, client only | managed app platform | serverless functions | traditional server | existing internal platform.
Criteria: server-held secrets, background jobs, cost floor, appetite for operations work.
DECISION: Backend approach
[Decision Block]

### 8.4 Database
Categories: relational | document | key-value or cache | embedded local | plain files.
Criteria: relationship density from section 7, transactional needs, query patterns, sync requirements.
Rule of thumb: highly related data with records that must stay connected favors relational.
DECISION: Database
[Decision Block]

### 8.5 Authentication
Categories: managed identity provider | platform sign-in | none, local only.
Hard rule at every tier: do not hand-roll password storage.
DECISION: Authentication
[Decision Block]

### 8.6 AI layer (if any)
Rules that apply whenever AI is a component: put the provider behind an abstraction so it can be swapped; separate decision logic from explanation text; use structured inputs and outputs; validate outputs before they touch users or data; define fallback behavior when the provider fails; set cost controls.
DECISION: AI provider and boundary
[Decision Block]

### 8.7 Notifications and messaging (if any)
Categories: push | email | in-app | none at first.
DECISION: Notification channels
[Decision Block]

### 8.8 Hosting and builds
Categories: managed hosting | container platform | store distribution pipeline | package registry.
DECISION: Hosting and build pipeline
[Decision Block]

> **Interview guide. Delete after filling.**
> *Why:* these are the expensive-to-change choices. Every one gets options, a recommendation tied to the Triage Card, and a status.
> *Ask:* per layer: what does the shape require, what does the team already know, what does the budget posture allow?
> *Default rule:* T1 and solo T2: managed services first, one language if possible, boring and mature over novel. The human can overrule any default; record the reason either way.
> *Protect:* payment providers and data residency are irreversible-class. Explicit confirmation only.
> *Tier:* skip subsections that do not apply to the shape, and say which were skipped and why.

## 9. Integration Map

[Every external service in one table, with the adapter rule.]

| External service | Purpose | Direction | Failure behavior |
|---|---|---|---|
| [name] | [one line] | [read | write | both] | [what happens here when it is down] |

**Adapter rule.** Each external provider gets one adapter module. Nothing else in the codebase imports the provider directly. Swapping a provider means rewriting one adapter, not hunting through the repository.

> **Interview guide. Delete after filling.**
> *Why:* external services are the least reliable and most replaced parts of any system.
> *Ask:* for each integration: what breaks in your product when it is down? Read-only or read-write? Any rate limits or terms that shape usage?
> *Tier:* all tiers with any integration.

## 10. Extension Points

[Where future pieces connect. Named seams, planned but unbuilt.]

| Future feature | Connects at | What exists now | What is deliberately absent |
|---|---|---|---|
| [likely feature] | [module or interface] | [the seam or stub] | [what we are not building yet] |

**Rule.** An extension point is a named seam, not a built feature. Building for the future means leaving a clean edge, not adding speculative code.

> **Interview guide. Delete after filling.**
> *Why:* this section is the entire reason planning broadly works. You are not predicting every future button. You are deciding where future pieces are likely to connect.
> *Ask:* if this succeeds, what do you add in the next three expansions? For each: which module does it touch, and what seam should exist so adding it does not smash the puzzle apart?
> *Tier:* all tiers. Even a prototype should know its next three moves.

## 11. Scale and Performance Posture (T2+)

- **Load expectations:** [users and requests at launch, at success]
- **Performance targets:** [the two or three numbers that matter, for example first screen under N seconds]
- **Scaling approach:** [what scales first and how, in one paragraph]

DECISION: Performance targets
[Decision Block]

> **Interview guide. Delete after filling.**
> *Default at T1:* "single instance of everything, revisit at real usage," stated as a Deferred decision with a trigger.

## 12. Deployment Topology (T2+)

- **Environments:** [local | staging | production, or the T1 subset]
- **Release path:** [how a change travels from commit to users]
- **Rollback:** [how a bad release is undone, in one paragraph]

> **Interview guide. Delete after filling.**
> *Default at T1:* local plus production, releases by tagged commit, rollback by redeploying the previous tag. State it, mark Confirmed or Deferred, move on.

## 13. Failure and Degraded Modes (T2+, forced by risk flags)

| Failure | User sees | System does | Recovery |
|---|---|---|---|
| [external provider down] | [message] | [cached | queued | disabled feature] | [automatic or manual] |

> **Interview guide. Delete after filling.**
> *Ask:* for each external dependency and each fragile step from section 6: what should a user see, and what should the system quietly do?
> *Tier:* T1 may cover only the top two failures.

## 14. Architecture Guardrails

[The shall-nots. Short, absolute, checkable.]

1. [for example: no module reads another module's tables directly]
2. [for example: no provider imported outside its adapter]
3. [for example: no schema change outside a migration]
4. [add project-specific guardrails from the interview]

> **Interview guide. Delete after filling.**
> *Why:* guardrails are the rules an agent checks before acting. They must be checkable by reading a diff.
> *Ask:* what mistakes would be expensive here? Convert each answer into a one-line prohibition.

## 15. Current Build Boundary

- **Current slice:** [SLICE-NNN and its one-line description, matching the active slice brief]
- **Modules the slice touches:** [list]
- **Modules the slice stubs:** [list, each stub labeled in the Decision Log]
- **Everything else:** designed above, deliberately unbuilt.

This section is updated at every turn of the expansion loop. It always names exactly one active slice.

> **Interview guide. Delete after filling.**
> *Why:* this section makes "build narrowly" visible inside the architecture itself, so no reader mistakes the whole puzzle for the current job.

---

*End of Architecture Document template. Sections filled: [n of 15]. Unknowns carried: [n]. See DECISION-LOG.md for reasoning.*
