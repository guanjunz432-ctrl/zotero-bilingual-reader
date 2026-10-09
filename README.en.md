# Zotero Bilingual Reader

**Source-position English–Chinese PDF reading in Zotero, including figure labels.**

[简体中文](README.md) · [Installation](docs/installation.md) · [Privacy](PRIVACY.md) · [Limitations](docs/limitations.md)

Early Windows preview for Zotero 9. Licensed under AGPL-3.0-only.

![Synthetic bilingual layout example](docs/assets/demo.png)

Select a paper in Zotero, request a page range or the full PDF, and receive a new attachment with the English page on the left and a Chinese layout on the right. The pipeline attempts to translate figure labels, caches successful pages, retries failures after processing later pages, and labels incomplete output explicitly.

## Install

Requires Windows 10/11, Zotero 9, Python 3.11+, Node.js 22+ with npm, and the Windows SimSun, Arial and Segoe UI Symbol fonts. The installer checks fonts; installing the Simplified Chinese supplemental font feature may be necessary.

Download and extract the backend source ZIP from Releases into a permanent directory. In PowerShell, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\login.ps1
```

Sign in with your own account through the official Codex login page. Install the XPI built in `dist` via Zotero → Tools → Plugins → gear → Install Plugin From File. Both the backend and XPI are required.

Right-click a paper or PDF → **Codex 中英对照** → first menu item. Try `1-2` first; leave the page field empty for all pages. The generated attachment opens after completion. Repeat the same selection to retry unfinished pages. The preview's Zotero menu and detailed operation guide are in Chinese.

## Privacy and costs

Selected page text, coordinates and images are sent to OpenAI. Parsing, rendering and typesetting run locally without local model weights. There is no project-operated relay, telemetry, shared account or included credential. Each user signs in independently; usage is subject to their account limits and service policies. Open source does not mean free or unlimited cloud inference.

The official CLI manages its own credentials in an isolated local profile. The application never reads or copies its authentication storage. Translation caches contain document content; do not share them publicly. See [PRIVACY.md](PRIVACY.md).

## Scope and evidence

The original local prototype was exercised on Windows + Zotero 9.0.6 with a 21-page paper. The public package has changed installation and authentication; [validation notes](docs/validation.md) distinguish public-package checks from prototype experience. No broad accuracy benchmark or macOS/Linux compatibility claim is made.

Dense labels may shrink; OCR, formulas, tables and masks over figure text can be inaccurate. Always compare against the left-hand source. A completed request is not a scholarly review.

## Development

```powershell
.venv\Scripts\python.exe scripts\test.py
node tests\test_native_bridge.cjs
.venv\Scripts\python.exe scripts\privacy_check.py
.venv\Scripts\python.exe scripts\build.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Repository organization was informed by Zotero PDF Translate, Zotero PDF2zh and Zotero Plugin Template; their translation engines or templates are not bundled. This independent community project is not affiliated with Zotero or OpenAI.
