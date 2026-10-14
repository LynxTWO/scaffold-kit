# [PROJECT NAME] Decision Log

Version: 0.1 Draft. Date: [date].
Companion documents: ARCHITECTURE.md, ENGINEERING.md, and the slice briefs (SLICE-001 onward).

The documents state what is true. This log preserves why, what else was considered, and what would reopen the question. It exists so context lives inside the project instead of across fifty dead chats that the next agent, or the next you, will never see.

## Rules

1. Every Decision Block in the ADD and EDD gets an entry here with a sequential ID.
2. Changing a decision never edits the old entry. Write a new entry that supersedes it and link both ways.
3. Stubs and shortcuts are decisions. Log them with their payback trigger.
4. An agent proposing work that conflicts with a logged decision must surface the conflict, not code around it.
5. Review pass: at every document audit, scan for entries whose Revisit trigger has fired.
6. Evidence stays out of entries. Receipts, hashes, run output and review packets live in a ledger or evidence file; an entry links them in one line. Keep an entry under forty lines. The index is the one-page view and must stay readable on its own.

## Index

| ID | Date | Decision | Status | Superseded by |
|---|---|---|---|---|
| D-001 | [date] | [short name] | [status] | [blank or ID] |

## Entry format

```
## D-[number]: [short name]
Date: [date]
Status: Confirmed | Proposed | Assumed | Open | Deferred | Superseded
Area: [ADD or EDD section reference]

Context:
[2 to 4 lines: the situation that forced a choice]

Decision:
[chosen option; for Open, unresolved with a link to the owner question/blocker]

Because:
[reason for the choice or for keeping it Open, plain]

Options considered:
- [plausible option]: [lets the user do/recover what] but [names actual work, loss or risk].
- [plausible option]: [lets the user do/recover what] but [names actual work, loss or risk].

Consequences:
[what this makes easier, what it makes harder, any cost accepted]

Revisit when:
[the trigger that reopens this: a usage number, a bill, a failure, a date]
```

## Example entry (delete once real entries exist)

## D-000: Example, permitted storage regions

Date: [date]
Status: Open
Area: EDD 8

Context:
The project will store household data. The owner has not confirmed permitted locations; verify provider offers before selection.

Decision:
Unresolved. The region question in EDD 4.3 blocks provisioning.

Because:
The owner must choose; comparing options does not authorize storing data.

Options considered:
- One owner-approved region keeps household data in one permitted place but limits providers that can store it there.
- Several owner-approved regions allow choosing among more providers but require checking where each stores household data.

Consequences:
Provisioning remains blocked. No region is selected by default.

Revisit when:
Owner constraints change or verified offers cannot support the permitted regions.

---

## Entries

[Entries begin here.]
