# Contributing

Thank you for helping improve bilingual reading. Start with a focused issue or pull request describing the observed behavior and expected result.

1. Install dependencies using `setup.ps1` on Windows.
2. Run `scripts/test.py`, the JavaScript bridge tests, `scripts/privacy_check.py`, and `scripts/build.py` as shown in the README.
3. For layout changes, include a self-authored or redistributable fixture and compare rendered English/Chinese pages. Do not commit user documents or caches.
4. Explain changes to data flow, dependencies, permissions and supported versions. Keep authentication delegated to the official CLI.
5. Contributions are accepted under the project's AGPL-3.0-only license. Do not submit code or assets you cannot license accordingly.

Avoid drive-by dependency upgrades and claims of translation accuracy without evidence. CI tests are offline and require no account secrets. Cloud smoke tests are manual and consume the tester's own quota.

Please keep discussions respectful and reproducible. Redact personal information before submitting screenshots. For sensitive bugs, see SECURITY.md.
