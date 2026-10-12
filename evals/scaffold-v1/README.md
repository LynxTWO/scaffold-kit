# Scaffold evaluation set v1

One case prompt in `cases.json`, a yes/no rubric on the outputs that distinguish the kit from a generic planning pack, and dated evidence files holding every trial that ran.

Trials are behavioral: a fresh agent receives the prompt (with the skill path for treated trials), cannot run tools beyond reading files, cannot ask a live person, and writes the planning output it would hand over. A reviewer scores it against the rubric and quotes the sentence that earned each yes. Record the model, the date, the skill state (git ref and the SHA-256 of `SKILL.md`, the Conductor and the templates), the working directory's own instruction files if any were in context, and who scored.

Keep the baseline trials: they are the failing test that justified the skill text. The rule author scoring their own trials is not independent review, and each evidence file says so. Report counts and quotes; three trials per state are too few for a rate.

Rerun the set when `SKILL.md`, `references/conductor.md` or a template changes. A wording change that is not retested inherits no result.

`workflow_cases` adds bounded regression scenarios for compact changes, audience parity, stale maps, scope growth, resume and closeout. Each uses an isolated repository with the named starting artifacts; read-only checks and planning writes are allowed only there. Give the trial the raw prompt and files, not its rubric. Score the requested action and any unsupported/unauthorized action separately. Record source hashes, artifacts, actual commands and gaps. A single independent pass is a smoke trial, not repeated qualification or evidence of human comprehension. Older evidence remains bound to its recorded source.
