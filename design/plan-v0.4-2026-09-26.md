# v0.4: package as a skill and apply the second field run

Date: 2026-09-26. Status: In progress on branch `v0.4`.

## Decisions

- **Own skill, not a subskill of anti-dark-code.** Different trigger (planning a project or slice versus auditing one), planning-only mode, its own templates, its own cadence. The two pair through one reference (`working-with-anti-dark-code.md`) rather than by sharing files.
- **Name `scaffold-kit`**, permanent once installed. Searches for "plan broadly" find it through the description's first sentence, the manifest keywords (`plan-broadly`, `build-narrowly`) and the repository topics; an alias skill would spend catalog budget for nothing.
- **License FSL-1.1-MIT**, same licensor and text as anti-dark-code. Repository stays private until v0.4 is verified.
- **Layout `skills/scaffold-kit/` from the first commit**, so Claude Code plugins, the Agent Plugins standard (Codex, Cursor, Copilot CLI) and `gh skill publish` all discover it without a later migration. Numeric filename prefixes dropped; the README maps old to new.
- **Codex marketplace file deferred.** `.agents/plugins/marketplace.json`'s entry schema was not verified against the Codex documentation during this pass; `.claude-plugin/marketplace.json` is also read by Codex per its plugin docs, so nothing is lost.

## Source of the changes

The second field run is the six-week slice-by-slice build under v0.3 that produced a 960-line decision log and, in its sixth week, a four-day verification campaign serving no requirement. The v0.4 text changes are listed in `CHANGELOG.md`; each maps to one of those two lessons or to skill packaging.

## Evidence

`evals/scaffold-v1/` holds one case prompt (a family recipe app, near-zero budget, weekends only) and a yes/no rubric on the kit's distinctive outputs. Baseline trials ran without the skill; treated trials run with it. Counts and quotes, no rates. The baseline trials ran in a working directory whose project instructions were in context, which the evidence file records.

## Checks before merge

- `python3 -m unittest discover -s skills/scaffold-kit/tests` green.
- `python3 skills/scaffold-kit/scripts/kit_audit.py` runs on a real document set and on the fixtures.
- `claude plugin validate --strict .` passes.
- SKILL.md frontmatter within the shared limits (name equals directory; description under 1024 characters; `license` and `compatibility` present).
- No em or en dashes in any kit file (the kit's own hygiene rule).
- Treated trials show the rubric items the baseline lacked.

## Follow-ups

- Verify the Codex marketplace entry schema, then add `.agents/plugins/marketplace.json`.
- Run `skills-ref validate` (agentskills reference validator) and `gh skill publish --dry-run` once the tools are installed here.
- Update the vendored copy in the consuming repository through its own pull request.
- Flip the repository public and tag `v0.4.0` after the owner's review.
