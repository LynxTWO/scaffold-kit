# Opt-in previews

This is the single preview catalog for both kits. Its two host manifests pin the
same candidate commits. The existing `lynxtwo` and `anti-dark-code` catalogs stay
on reviewed stable commits; development on `main` does not promote a release.
Current candidates: Scaffold Kit **0.4.2** and Anti-Dark-Code **2026.10.15-unified.20**, including the reviewed light and dark briefs. Plugin publishing remains on hold.

From a reviewed checkout containing this folder, register **this folder**, not
the repository root. First disable or remove the current copy of each kit you
want to test, including any standalone skill, so only one copy is active.

Claude Code:

```sh
claude plugin marketplace add /absolute/path/to/scaffold-kit/preview
claude plugin install scaffold-kit@lynxtwo-preview
claude plugin install anti-dark-code@lynxtwo-preview
```

Codex:

```sh
codex plugin marketplace add /absolute/path/to/scaffold-kit/preview
codex plugin add scaffold-kit@lynxtwo-preview
codex plugin add anti-dark-code@lynxtwo-preview
```

Install either kit or both, then use a fresh chat. To update an existing preview, first replace this local catalog with the reviewed newer copy. Claude: `claude plugin marketplace update lynxtwo-preview`, then `claude plugin update <kit>@lynxtwo-preview`. Codex reads the local catalog directly: repeat `codex plugin add <kit>@lynxtwo-preview`. Repeat for each installed kit. To roll back, uninstall/remove
the preview copy and re-enable or reinstall the copy from your original stable
catalog. Removing a marketplace in Claude also removes its installed plugins;
keep project documents and calibration outside host caches.
If an earlier unpinned checkout installed a preview under a stable catalog name,
remove that copy and reinstall from the corrected stable catalog.

Maintainers advance preview pins only after validation. Each changed public
preview payload needs a new plugin version so hosts detect the update. Stable
promotion is a separate reviewed change to the stable pins. A version suffix or
GitHub prerelease checkbox does not select a host channel.
