# Zotero Bilingual Reader

Generate English–Chinese, side-by-side PDFs in Zotero while retaining the source page layout. Body text, captions, axes and legends can be translated; the result is imported as a new attachment.

**Windows 10/11 · Zotero 9 · Your own Codex account · AGPL-3.0-only**

[Download 0.2.0 preview](https://github.com/guanjunz432-ctrl/zotero-bilingual-reader/releases/tag/v0.2.0-beta.1) · [中文 / installation](README.md) · [Validation](docs/validation.md)

## Actual paper output

Source page 4 of Green et al. (2017), rendered directly from the generated PDF. No mockup or manually substituted translations.

![Actual paper page: English left, Chinese right](docs/assets/paper-page-04.png)

The same output's Figure 2 shows translated axes, legend and caption, retaining numeric ticks and bars:

![Actual bilingual figure crop](docs/assets/paper-figure-02.png)

[Download two-page PDF (source pages 1 and 4)](docs/assets/paper-bilingual-sample.pdf) · [Original paper](https://doi.org/10.5194/nhess-17-1-2017) · [Attribution and reproduction](docs/sample-provenance.md)

Source © Green et al., 2017, CC BY 3.0. Modified by AI Chinese translation and side-by-side layout; no author endorsement.

## Models and measured time

| Page type | Default model | Reasoning | Cloud request |
| --- | --- | --- | --- |
| Text / simple charts | `gpt-6-luna` | `low` | 19.72 and 20.11 seconds/page |
| Complex graphics / scans | `gpt-6.1-sol` | `low` | 32.65 seconds/page |
| Local typesetting | PyMuPDF and deterministic software | No model | 19.83 seconds for these 3 pages |

A fresh public-backend run on source pages 1, 4 and 7 took **93.16 seconds end to end**, excluding setup, login and Zotero import. A separate 16-page prototype run recorded 8m36s summed successful cloud requests; that is not total processing time. These are single-machine samples, not a speed guarantee or subscription quota percentage. Figure 2 used Luna; routing is a page-level heuristic. Model access depends on the account.

## Changes in 0.2.0

Ephemeral requests replace persistent per-page ACP chats. Low-reasoning model routing, reusable rendered PDFs, clear dependency errors, and document-wide aborts on login/quota/model errors reduce unnecessary work. Ordinary page failures are retried once after the forward pass. Tiny or diagonal figure labels can be preserved with a bilingual note below the page.

## Install

Install Python 3.11+, Node.js 22+ with npm, and Zotero 9 on Windows. Download the source ZIP and XPI. Extract the source to a stable directory, run `setup.ps1`, then `login.ps1` using your own account. Install the XPI via Zotero's add-on manager. Right-click an English PDF or parent item → Codex 中英对照. Leave pages empty for all pages, or start with `1-2`.

Updates require the new source/setup and XPI. Authentication and compatible caches remain in the dedicated application data directory. [Detailed instructions](docs/installation.md).

## Privacy and limitations

Selected page text and images go to OpenAI; parsing and layout run locally. No relay server, telemetry, shared account or local model weights. Credentials are managed only by the official CLI in an isolated profile. New translations use ephemeral requests; old history is not deleted. [Privacy](PRIVACY.md).

Dense maps, tiny text, formulas and rotated labels need human review. Structural validation does not prove semantic accuracy or complete OCR. [Limitations](docs/limitations.md). This is a community project, not an official Zotero or OpenAI plugin.

Source code: AGPL-3.0-only. Paper samples: CC BY 3.0 with attribution. [Third-party notices](THIRD_PARTY_NOTICES.md).
