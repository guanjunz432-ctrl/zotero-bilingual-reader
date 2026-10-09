# Validation record

Date: 2026-10-09. Preview: 0.1.0-beta.1.

## Evidence completed locally

- Fresh Python virtual environment with pinned packages; separately downloaded official Node 24 LTS with verified SHA256; npm clean installation from lockfile.
- Environment doctor confirms backend executable paths, adapter, required fonts and PDF packages.
- Official Codex login completed in the application's dedicated profile. No login file was read, copied or included in project source.
- Real cloud smoke test on the self-authored one-page fixture: 8 native text regions and 3 raster figure labels returned; no missing translation IDs; no page-render errors. The English source was not modified.
- Cloud result visually inspected. A narrow OCR mask initially left the end of one English label visible; bounded raster-ink refinement and a regression test were added, then the corrected result was inspected again.
- 11 Python offline tests cover bounded page ranges, malformed/missing layout results, page recovery and ordering, partial native-job status, environment isolation and short-label mask refinement.
- JavaScript bridge scenarios cover complete, partial, stopped and failed jobs, parent attachment linkage, generated filename and avoiding false success.
- Prepared-translation sample separately verifies deterministic layout without a model call. It is explicitly labeled and must not be presented as a translation accuracy result.
- Release source ZIP was extracted to a separate directory and its setup script completed with a fresh virtual environment and npm clean installation; all environment checks passed. This is a fresh directory test on the same Windows machine, not a second physical computer.
- Public allowlist and package-member checks exclude authentication, user configuration, caches, logs and dependency directories. Repeated source ZIP and XPI builds have matching SHA256 hashes. An independent Gitleaks scan found no secrets in the candidate tree.

## Native UI verification boundary

The public bridge is derived from the prototype that successfully imported attachments in Zotero 9.0.6. The changed path/configuration and completion logic are covered by the JavaScript scenarios. A fresh native UI install-and-import check of this exact public XPI remains unverified: the desktop automation screenshot helper timed out during this release session. This preview does not claim that step passed. Feedback from a manual install on another user's machine is welcome.

Public samples: [source](assets/synthetic-example.pdf), [prepared layout](assets/synthetic-bilingual.pdf), [cloud result](assets/cloud-bilingual.pdf). The repository screenshot uses the prepared layout; cloud output is provided separately so these can be distinguished.

## Prototype evidence

Before the public packaging changes, the local prototype was exercised on Windows + Zotero 9.0.6 using a 21-page paper, including native text, figure labels, formulas and tables. This is practical experience with the workflow, not a public redistributable benchmark. That paper, translation cache and user's library are not included.

## Scope limits

These checks do not prove correctness for arbitrary scientific PDFs, absence of all OCR omissions, semantic translation accuracy, perfect preservation of figure pixels on the Chinese side, or compatibility with other operating systems. A rendered page is not a peer-reviewed translation. See limitations.md.

GitHub CI runs offline tests and builds without credentials. Cloud testing is manual and uses the tester's own account quota.
