# Maintainer release process

1. Update versions in `package.json`, the lockfile, `backend/settings.py`, and `addon/manifest.json`. Zotero uses its compatible prerelease version syntax.
2. Run offline tests and a cloud smoke test with a self-authored PDF and your own account. Record exact scope in `validation.md`; never include account information or private source paths.
3. Keep `release-files.json` explicit and reviewed. Add new public files deliberately.
4. Run the privacy checker and inspect Git staging/history with an independent secret scanner. Inspect screenshot pixels and PDF metadata, not only text source. Use a nonpersonal commit email.
5. Run `scripts/package_release.py` twice and compare SHA256SUMS. Open ZIP/XPI members and confirm only approved files are present.
6. Extract the release ZIP to a fresh path, install dependencies and run the environment check. Check that no original developer directory is needed.
7. Push the source, wait for CI, and create a prerelease with the XPI, source ZIP and checksums. State limitations and verification scope. Enable private vulnerability reporting on GitHub.
8. Verify repository visibility, README links, release downloads and checksums from GitHub after publication.

No automatic release workflow receives an account secret. CI uses read-only repository permissions; release publication is a deliberate maintainer action. The first preview uses manual plugin updates.

## Organization references

- Zotero PDF Translate: installation instructions, usage guide, release links and contribution section.
- Zotero PDF2zh: separation of plugin/backend setup, bilingual documentation and feature/limitation explanations.
- Zotero Plugin Template: source/build separation and versioned XPI releases.

These are structural references, not copied implementation or implied endorsement. Source links are in the README.
