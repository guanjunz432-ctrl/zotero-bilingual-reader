# Changelog

## 0.2.0-beta.1 — 2026-10-16

- Replace per-page ACP sessions with ephemeral official CLI requests; pin Codex 0.163.0 and remove the ACP adapter.
- Default to gpt-6-luna / low for text and gpt-6.1-sol / low for complex graphics or scans.
- Report Python startup/dependency failures through job status, preserve page caches, reuse unchanged rendered PDFs.
- Stop document-wide on login/quota/model errors; retry ordinary page errors once.
- Preserve tiny/diagonal figure labels with bilingual notes to reduce graphic damage.
- Show real paper pages, a figure crop, a downloadable PDF and measured timings.
- Preserve isolated official login and portable setup.

## 0.1.0-beta.1 — 2026-10-09

First public Windows preview, derived from a local prototype.

- Zotero context menu, page selection, progress, stop-after-page and automatic attachment import.
- Source-position bilingual layout with native text and cloud-detected figure-label translation.
- Per-page caches, forward processing before retries, and explicitly marked partial output.
- Portable setup scripts, isolated official Codex login, restricted translation configuration and redacted environment diagnostics.
- Offline tests, reproducible XPI build, explicit release contents and privacy checks.

Known limitations and validation scope are documented separately. This preview does not claim comprehensive translation accuracy or cross-platform support.
