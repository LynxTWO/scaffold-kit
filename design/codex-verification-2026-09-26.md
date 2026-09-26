# Codex verification brief

For a Codex session (CLI, IDE extension or ChatGPT desktop) run by the owner. Everything below is read-only or session-scoped except the two steps marked persistent, which change the user's Codex configuration and are reversed at the end. Record results in `evals/scaffold-v1/evidence-codex-<date>.json`: exact commands, Codex version, what appeared, and what did not. Do not edit the skill to make a check pass; report the failure.

## Already verified without a Codex host

- Marketplace file shape (`.agents/plugins/marketplace.json`) mirrors the documented format and a published cross-host plugin; legacy manifest `.codex-plugin/plugin.json` present because the root portable manifest carries no `extensions.com.openai` block.
- Skill directory name equals frontmatter `name`; description under 1024 characters; only spec frontmatter fields.
- Headless checks from the authoring machine with the extension-bundled `codex` binary (0.155.0-alpha.16.3) are in `evals/scaffold-v1/evidence-codex-2026-09-26.json`: project-skill discovery passed (skill listed, description quoted verbatim); the session-override plugin route returned NONE. One host, one version; not coverage of the IDE or ChatGPT surfaces.

## Checks for the Codex session

1. **Version.** `codex --version`. Record it.
2. **Project-skill discovery, no plugin.** In an empty directory: create `.agents/skills/scaffold-kit/` as a copy of `skills/scaffold-kit/`, start Codex there, and ask it to list available skills without opening files. Expected: `scaffold-kit` is listed with the description's first sentence. Then ask: "Use $scaffold-kit. Read only its SKILL.md and answer: which template does Phase 3 load?" Expected: `assets/templates/ENGINEERING.md`, proving relative paths resolve inside the skill.
3. **Explicit invocation.** In the same directory, send `$scaffold-kit` followed by the case prompt from `evals/scaffold-v1/cases.json` (`prompt_treated`, with `<SKILL_PATH>` replaced by the skill's path). Expected: a Phase 0 restatement, a Triage Card, questions with assumptions marked, decisions with statuses, and the build gate said out loud, within the word cap. Score it against the rubric and add the trial to the evidence file.
4. **Marketplace and plugin, session-scoped.** From an empty directory: `codex exec -c 'marketplaces.lynxtwo.source_type="local"' -c 'marketplaces.lynxtwo.source="<absolute path to this repository>"' -c 'plugins."scaffold-kit@lynxtwo".enabled=true' "List available skills and installed plugins without opening files."` On codex-cli 0.155.0-alpha.16.3 this returned NONE for both the plugin and the marketplace (recorded in `evals/scaffold-v1/evidence-codex-2026-09-26.json`), which is consistent with plugins resolving from the cache that `codex plugin marketplace add` populates. Repeat it once on the session's version and record the answer either way; check 5 is the route that decides.
5. **Marketplace and plugin, persistent (reverse at the end).** `codex plugin marketplace add LynxTWO/scaffold-kit` (needs read access to the private repository; record the auth path used), then enable `scaffold-kit@lynxtwo` in `config.toml` per the documentation, restart, and repeat check 3 through the plugin rather than the project copy. Then remove the marketplace (`codex plugin marketplace remove lynxtwo`) and the config entry, and confirm `codex plugin marketplace list` no longer shows it.
6. **ChatGPT desktop, if used.** Restart the app, open the Plugins Directory, add the marketplace, install the plugin, invoke `@scaffold-kit`. Record what the directory shows for name, description and category.
7. **Catalog pressure.** With the owner's usual set of skills installed, ask Codex to print the `scaffold-kit` description as it sees it. Expected: intact. If shortened or omitted, record the number of installed skills and the model's context size; the description is 619 characters and Codex fits all descriptions into 2% of context.
8. **Reference validator, if installable.** `pip install` the agentskills reference tool in a scratch environment and run `skills-ref validate ./skills/scaffold-kit`. Record the output verbatim. This is demonstration-grade tooling; a failure here is a finding, not a blocker.

## What passes

Checks 2, 3 and 4 are the acceptance for this brief. Check 5 proves the marketplace route; 6, 7 and 8 are observations. Any check that changed the skill, the manifests or the user's configuration to pass is a failed check.
