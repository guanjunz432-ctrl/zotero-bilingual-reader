# Privacy / 隐私

## Data flow

Zotero selects a local PDF → the Python backend extracts coordinates and renders selected pages → Codex receives page text and images → validated translations are cached locally → the backend typesets a new PDF → Zotero imports it as a new attachment.

There is no project-operated server, analytics, remote crash reporting or document upload endpoint. OpenAI processes the selected document content under the user's applicable service terms. Installing dependencies contacts PyPI and npm. Using GitHub downloads contacts GitHub.

## Authentication

Every user signs in independently using the official Codex CLI. The application uses a dedicated local `codex-profile` directory and does not open, parse, copy or export login files. No maintainer credential is included in the repository or release. The isolated profile may contain official CLI credentials and session records; never attach it to an issue or send it to anyone.

Inherited API keys, model-provider overrides and logging variables are not passed to the translation process. Requests use read-only mode with shell, plugins, hooks, subagents and web search disabled, no requested MCP servers, and a client that rejects results reporting tool use. These controls reduce tool access; they are not a claim that PDF files or upstream software are risk-free. Do not relax these settings to work around an error.

## Local content

`%LOCALAPPDATA%\ZoteroBilingualReader` contains executable paths, job identifiers, source paths, page images, document text, translations and generated PDFs. These are private working data, not public diagnostics. Raw model responses and reasoning chunks are not saved by this project's backend. New requests use `codex exec --ephemeral --ignore-user-config`; no persistent per-page rollout is requested. The CLI still manages authentication and may maintain non-conversation diagnostics. Old sessions are not deleted. Validated page data includes model, elapsed time and token usage metadata, never reasoning text.

The source PDF is not modified. Generated attachments may subsequently sync according to your Zotero settings; that is managed by Zotero, not this plugin.

## Sharing a problem

Use the output of `scripts/doctor.py`, a brief description, and a self-authored or redistributable sample. Do not upload personal PDFs, account screenshots, cookies, tokens, login files, the data directory or unreviewed logs. Review screenshots for titles, usernames, email addresses and paths.

The main public example is an openly licensed paper excerpt with attribution, not a user library screenshot. See docs/sample-provenance.md. Historical synthetic fixtures are kept separately. No automated scan can prove the absence of every identifying detail; releases are built from an explicit source list and inspected before publication.
