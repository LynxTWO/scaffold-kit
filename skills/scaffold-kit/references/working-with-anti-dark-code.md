# Working with anti-dark-code

Load when code already exists, or when the repository carries an installed anti-dark-code skill (`.agents/skills/anti-dark-code/` by convention). The two skills divide the work: the kit decides what gets built and records why; anti-dark-code establishes what is there and proves what was built. Neither restates the other's rules.

## Brownfield: map first, then scaffold

Scaffolding an unmapped codebase produces confident fiction. Before Phase 2, run anti-dark-code's Understand card on the repository and backfill from its artifacts:

| anti-dark-code artifact | Fills |
|---|---|
| system map (modules, entry points, trust and data boundaries, owners) | ADD section 4 module map, section 2 boundary statement, section 9 integration map |
| coverage ledger (examined, deferred, excluded, blocked surfaces) | EDD section 16 rows for every surface not examined |
| unknowns entries | EDD section 16 risk register, one row per unknown, keeping the kit's `U-` identifiers |
| verification plan and gate records (`calibration/`) | EDD section 11 verification ledger, section 14 CI gates |

Reality-derived entries enter the documents as Confirmed. Aspirations enter as Proposed. The interview then covers only the gaps. The kit's unknowns row and anti-dark-code's unknowns entry carry the same fields (area, concern, why it matters, evidence, confidence, owner, next check, risk, status); use either shape, do not keep two copies of one unknown.

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

Each Slice Brief acceptance row names the check that proves it: an anti-dark-code capability ID from its catalog, an exact gate from `calibration/gates.json`, or a named CI check. That column is what lets `route` and shadow evidence bind a pull request's checks to `S-` identifiers instead of to prose. The kit's verification ledger (EDD section 11) lists the same bindings; anti-dark-code's Verify card owns how a gate is reviewed and executed.

## Proportionality

Verification effort is bounded by the consequence of the requirement it proves. A harness, campaign, observer or custody layer is a build item: it needs its own requirement identifier in EDD section 4 and a consequence, or it is out of scope for the slice. When anti-dark-code is installed, its need trace, consequence class and reframe trigger apply to that decision; the kit does not restate them. A campaign whose ledger stays at zero is a reframe, not a next milestone.

## Authority and protected areas

The kit's stop-and-ask list (EDD section 12) and anti-dark-code's protected-edit list are one list: auth, sessions, secrets, crypto, money, entitlements, deletion, retention, export, compliance, migrations, backfills, data repair, production-reach tooling and repository-protected paths. Name it once in `CLAUDE.md` (or the host's equivalent) as the areas unattended agents never touch, and let both skills point at it.

## Product principles

The five product principles (make truth easier, make repair normal, make dignity default, make ownership unavoidable, make manipulation unnecessary) appear in the kit as EDD section 4.4 and as acceptance rows in the Slice Brief. anti-dark-code's `product-principles.md` holds the full obligations, counterexamples and the verification methods that check them; the kit's review at Phase 3 and the slice's acceptance rows are where they enter the documents, and anti-dark-code's Investigate and Verify cards are where they are checked against the built software.

## Hygiene and the audit

The kit's writing hygiene applies to the documents it produces. anti-dark-code's writing hygiene applies to changed prose in code and comments. Where a project wants one list, adopt the kit's banned-word list in anti-dark-code's calibration and cite it from both. `scripts/kit_audit.py` runs as an anti-dark-code gate when the repository records it in `calibration/gates.json`; a configured gate is a proposal until the owner enables it.
