# Working with anti-dark-code

Load when code already exists, or when the repository carries an installed anti-dark-code skill (`.agents/skills/anti-dark-code/` by convention). The two skills divide the work: the kit decides what gets built and records why; anti-dark-code establishes what is there and proves what was built. Neither restates the other's rules.

## Brownfield: map first, then scaffold

Scaffolding an unmapped codebase produces confident fiction. Before Phase 2, run anti-dark-code's Understand card on the relevant scope and backfill from its artifacts:

| anti-dark-code artifact | Fills |
|---|---|
| system map (modules, entry points, trust and data boundaries, owners) | concise pointers in ADD sections 4, 2 and 9; the observed map stays canonical |
| coverage ledger (examined, deferred, excluded, blocked surfaces) | a linked EDD section 16 summary of unexamined surfaces that matter to the plan; the ledger stays canonical |
| unknowns entries | EDD section 16 summaries with Scaffold-owned `U-` IDs, linked to ADC entries by title |
| verification plan and gate records (`calibration/`) | links from EDD sections 11 and 14; the gate records stay canonical |

Check the map's source identity and affected dependencies before reuse; matching repository identity is not freshness. Record observed facts with confidence and evidence. Confirmed describes an owner choice, not the mere existence of code. Proposed changes stay Proposed until chosen or delegated. Interview only the gaps.

EDD risk rows and ADC unknowns have different fields and status vocabularies. Choose one canonical record per unknown; the other document holds a short summary and link. Preserve stored status and fields, without migration or synchronized duplicate ledgers. Scaffold slices bound build increments; ADC slices group code for coverage passes. Their statuses stay separate.

Reuse the Triage Card's Explanation depth (or existing Interview depth) for both tools. If only anti-dark-code's calibration README records a depth, use it at triage, save it in the Triage Card and leave a pointer in calibration, so one choice remains. ADC owns evidence; the kit owns intended scope and rationale. Keep calibration and run artifacts in ADC's canonical paths. Link them from the existing documentation index rather than copying them into a new kit folder.

## One mapping between the vocabularies

The kit and anti-dark-code label different things. Keep them on their own axes:

| Axis | Vocabulary | Owner |
|---|---|---|
| Decision status | Confirmed, Proposed, Assumed, Open, Deferred, Superseded | kit (Conductor) |
| Claim confidence | `verified`, `inferred`, `unknown` | anti-dark-code core |
| Claim kind | `source_fact`, `configured_behavior`, `observed_behavior`, `guarantee` | anti-dark-code core |
| Ledger and item status | `unscanned` ... `blocked`; `open` ... `done` | anti-dark-code conventions |

A Confirmed decision is not a verified claim. "We chose Postgres" is a decision with a status; "the migration applies cleanly from scratch" is a claim with a confidence and evidence. When a document records evidence for a decision, the evidence uses anti-dark-code's words and cites its locator.

Risk flags map to consequence classes when a guarantee is assessed: payments to `money`; personal data, health data, minors and user-generated content to `user_data`; secrets with production reach to `production_secrets`; anything confined to a developer machine or a disposable resource to `local_only` or `none`.

## Acceptance criteria bind to gates

Each Slice Brief acceptance row names confirmed R-IDs and a reliable check: a catalog capability ID, exact calibrated gate, CI check, or `manual: <steps and result location>` when proportionate. Reference this binding from EDD section 11 rather than copying it. ADC's Verify card owns gate review and execution. These document links do not configure ADC routing automatically; machine obligations still require reviewed gate records. Selected or skipped is never passed.

## Proportionality

Verification effort is bounded by the consequence of the requirement it proves. A harness, campaign, observer or custody layer is a build item: it needs its own requirement identifier in EDD section 4 and a consequence, or it is out of scope for the slice. When anti-dark-code is installed, its need trace, consequence class and reframe trigger apply to that decision; the kit does not restate them. A campaign whose ledger stays at zero is a reframe, not a next milestone.

## Authority and protected areas

The kit's stop-and-ask list (EDD section 12) and anti-dark-code's protected-edit list are one list: auth, sessions, secrets, crypto, money, entitlements, deletion, retention, export, compliance, migrations, backfills, data repair, production-reach tooling and repository-protected paths. Name it once in `CLAUDE.md` (or the host's equivalent) as the areas unattended agents never touch, and let both skills point at it.

## Product principles

The five product principles (make truth easier, make repair normal, make dignity default, make ownership unavoidable, make manipulation unnecessary) appear in the kit as EDD section 4.4 and as acceptance rows in the Slice Brief. anti-dark-code's `product-principles.md` holds the full obligations, counterexamples and the verification methods that check them; the kit's review at Phase 3 and the slice's acceptance rows are where they enter the documents, and anti-dark-code's Investigate and Verify cards are where they are checked against the built software.

## Hygiene and the audit

The kit's writing hygiene applies to the documents it produces. anti-dark-code's writing hygiene applies to changed prose in code and comments. Where a project wants one list, adopt the kit's banned-word list in anti-dark-code's calibration and cite it from both. `scripts/kit_audit.py` runs as an anti-dark-code gate when the repository records it in `calibration/gates.json`; a configured gate is a proposal until the owner enables it.
