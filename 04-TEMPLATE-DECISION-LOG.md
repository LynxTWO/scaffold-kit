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
[what was chosen, one or two lines]

Because:
[the reasoning, plain]

Options considered:
- [option]: [one-line tradeoff]
- [option]: [one-line tradeoff]

Consequences:
[what this makes easier, what it makes harder, any cost accepted]

Revisit when:
[the trigger that reopens this: a usage number, a bill, a failure, a date]
```

## Example entry (delete once real entries exist)

## D-000: Example, single relational database

Date: [date]
Status: Confirmed
Area: ADD 8.4

Context:
The data domain is relationship-dense: users own projects, projects hold items, and every result must stay connected to the inputs that produced it.

Decision:
One relational database, accessed only through the data module.

Because:
Relationship density and integrity needs favor relational. One database keeps operations simple at this tier.

Options considered:
- Relational: strong integrity, familiar tooling, fits the domain.
- Document store: flexible shapes, weaker relational integrity for this domain.
- Plain files: near-zero setup, collapses under concurrent writes.

Consequences:
Easier: joins, constraints, migrations. Harder: flexible or nested shapes need deliberate modeling.

Revisit when:
A workload appears that is document-shaped end to end, or scale forces a split.

---

## Entries

[Entries begin here.]
