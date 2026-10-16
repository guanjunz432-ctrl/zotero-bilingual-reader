# Validation record

## 0.2.0-beta.1 — 2026-10-16

The public backend was tested using its own official login profile and pinned Codex CLI 0.163.0. The previous 0.148.0 rejected the new model name; that rejected probe is not included in the successful-run timings below. No authentication file was read or copied.

### Actual paper run

Green et al. (2017), DOI 10.5194/nhess-17-1-2017, original pages 1, 4 and 7, empty translation cache:

| Page | Model / reasoning | Cloud request | Native regions | Extra raster/outlined regions |
| --- | --- | --- | --- | --- |
| 1 | gpt-6-luna / low | 19.72 s | 11 | 2 |
| 4 | gpt-6-luna / low | 20.11 s | 22 | 0 |
| 7 | gpt-6.1-sol / low | 32.65 s | 37 | 3 |

Page preparation plus translation: 73.33 s. Local rendering: 19.83 s. Total backend wall time: **93.16 s**. Setup, login and Zotero import are excluded. No page retries or render errors occurred in this successful run. A full-cache rerun took 0.085 s locally; no new cloud translation was needed. This is one machine and one small sample, not a general speed or cost benchmark.

The three returned thread IDs were absent from the dedicated and Desktop state databases and rollout files. Requests reported zero tool use. Validated page metadata supplies elapsed time and token usage; token counts are not converted to subscription quota percentages. See [sanitized measurements](assets/benchmark.json).

The two-page public sample and Figure 2 crop were rendered and visually checked. Text, axes, legend and caption are actual model output, not prepared translations. The source PDF remains unchanged. Only source pages 1 and 4 are redistributed with CC BY attribution; the internal map page is excluded. [Provenance](sample-provenance.md).

### Regression and runtime checks

21 Python offline tests pass, including ephemeral arguments, isolated environment, bounded timeout, startup failure status, model routing, global-error abort, cached-page preservation, tiny/diagonal label preservation and rendered-PDF cache invalidation. JavaScript bridge scenarios cover complete, partial, stopped and error jobs. Required executables, PDF dependencies and Windows fonts pass the environment doctor. The public allowlist/privacy check passes.

The source ZIP was extracted to a new directory on the same Windows machine. Its setup completed with a fresh virtual environment, clean locked npm install and separate test data directory; all 21 Python tests and bridge scenarios passed there. No login was copied into that test directory. Repeated XPI/source builds matched SHA256, and Gitleaks found no secrets in the extracted public package. This is not a test on another physical computer.

### Native UI and broader scope

The repaired personal prototype was installed and visually verified in Zotero 9.0.6, completing and attaching a 16-page result. Its successful cloud requests totalled 515.70 seconds (6 Luna pages, 10 Sol pages); that sum excludes exploratory requests and local rendering, so it is **not** a full end-to-end measurement. This is separate evidence from the public three-page run above.

The exact public 0.2.0 XPI has automated bridge/package checks but has not been freshly installed through the native UI in this release session. Native desktop control was deferred while another user task was active. The existing working personal installation was retained. This preview does not claim cross-machine installation or comprehensive OCR/translation accuracy.

## Historical 0.1.0 validation

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
