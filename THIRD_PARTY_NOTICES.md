# Third-party notices and provenance

Project source: Copyright 2026 Zotero Bilingual Reader contributors. GNU AGPL-3.0-only; see LICENSE. The source ZIP and XPI do not bundle Python, Node.js, Codex executables or dependency directories. Setup downloads dependencies separately.

| Component | Role | License / source |
| --- | --- | --- |
| PyMuPDF 1.28.2 / MuPDF | PDF extraction, rendering, editing | AGPL-3.0 or commercial dual license; this project uses the AGPL route. [Official terms](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright) |
| ReportLab 4.4.9 | TrueType character coverage; no local model | BSD-style; [source](https://github.com/MrBitBucket/reportlab-mirror) |
| Pillow 12.3.0 | Bounded raster-ink analysis and asset inspection | MIT-CMU; [source](https://github.com/python-pillow/Pillow) |
| charset-normalizer 3.5.2 | ReportLab dependency | MIT; [source](https://github.com/jawah/charset_normalizer) |
| @agentclientprotocol/codex-acp 1.6.2 | ACP / Codex App Server adapter | Apache-2.0; Copyright 2025 JetBrains s.r.o. [Source](https://github.com/agentclientprotocol/codex-acp) |
| @openai/codex 0.148.0 | Official CLI and authentication | Apache-2.0; [source](https://github.com/openai/codex) |

The complete Node dependency resolution is recorded in `package-lock.json`; installed packages retain their upstream licenses. `requirements.txt` pins the Python runtime dependencies. Do not remove upstream notices when redistributing a dependency or packaged runtime in a future release.

## Font handling

The Windows preview reads SimSun, Arial and Segoe UI Symbol from the user's own Windows font installation. Font files are not copied into the repository, source ZIP or XPI. Example PDFs contain embedded font subsets as normal document output. Installing or redistributing font files separately requires checking their own terms.

## Original code and reference projects

The application bridge, Python workflow and scripts were developed for this project with AI assistance. Maintainers remain responsible for reviewing contributions and claims. The release organization was informed by the following projects; their code, logos and translation engines are not bundled:

- [Zotero PDF Translate](https://github.com/windingwind/zotero-pdf-translate): quick start, usage and contribution organization.
- [Zotero PDF2zh](https://github.com/guaguastandup/zotero-pdf2zh): plugin/backend documentation and release presentation.
- [Zotero Plugin Template](https://github.com/windingwind/zotero-plugin-template): XPI build and tagged-release conventions.

The synthetic example and its figure were authored specifically for this project and are included under the project license. They contain no research paper, user screenshot or library data. `synthetic-bilingual.pdf` uses prepared translations for repeatable rendering; `cloud-bilingual.pdf` is the separately generated cloud smoke-test result. Neither is an accuracy benchmark.

GNU AGPL text was obtained from the SPDX license-list-data copy of AGPL-3.0-only. No original or dependency author should be understood to endorse this project.
