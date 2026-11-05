# Changelog

## Unreleased
- Gravion Trainner: fixed a Windows-only defect in the **test harness** where the local mock HTTP server did not drain the POST request body, so Windows reset the socket and the client observed `ConnectionAbortedError` instead of the real response. The product code and the redirect-blocking behaviour are unchanged; the suite now passes 30 consecutive runs where 12 previously produced 4 failures.
- Added `https://github.com/gravion-ux/agent-browser/tree/mainpackage-lock.json`. The JavaScript dependency graph is now fully locked, `npm audit --audit-level=high` reports 0 vulnerabilities, and CI installs from the lockfile with `npm ci` for reproducible builds.
- Added `scripts/scan-secrets.py`, a self-contained credential and secret-file scanner that fails the build on committed API keys, tokens, private keys, `.env` files, tunnel credentials or WireGuard profiles. Wired into CI as the `secret-scan` job.
- Added `scripts/syntax-checks.py`, an offline static gate covering JavaScript syntax, Python compilation, JSON/JSONL/TOML/YAML parsing, shell syntax and CLI smoke entry points. Wired into CI as the `syntax-checks` job.
- CI: renamed the workflow to `CI`, added concurrency cancellation for superseded runs, per-job timeouts, least-privilege `permissions: contents: read` and `fail-fast: false` matrix strategies.
- Added `docs/PUBLICATION-VERIFICATION.md`, an independent dated verification record covering every suite result, the Windows defect and its root cause, the lockfile and advisory audit, the credential scan and the items that remain unverifiable. The original 0.4.3 audit and test records are preserved unchanged.
- Added `.gitattributes` forcing LF for text files, so `scripts/test-all.sh` keeps working on Linux and macOS runners and on Windows checkouts with `core.autocrlf=true`.

## 0.4.3 — deeper validation and release audit
- Privacyflow: validate WireGuard interface ListenPort/FwMark/MTU/Table/SaveConfig, allow valid DNS search domains, reject malformed numeric DNS, unknown directives, executable wg-quick hooks and oversized profile/config files.
- Privacyflow: CLI now clearly states that the configured kill-switch requirement is not a live firewall control in this dry-run release.
- Added regression coverage for all additional parser and safety cases; full suite now passes 82/82, including injected DNS-answer regression tests.
- Verified both Node packages with `npm pack --dry-run` and built wheels + editable installs for both Python packages.
- Added explicit limitations for unavailable Playwright/Chromium, npm audit, live Cloudflare, WireGuard route/leak tests and Docker/Caddy checks.

## 0.4.2 — deep audit and hardening
- Localshare: fixed IPv6 origin formatting, decimal port validation, cross-platform cloudflared detection and named-config regular-file checks; added wildcard email-domain access and fake-cloudflared process integration test.
- Agent Browser: canonicalized hostname allow-lists, blocked non-public network destinations by default, added explicit private-network opt-in, blocked service workers from bypassing Playwright request routing, and fixed cross-platform CLI entrypoint detection.
- Privacyflow: strengthened WireGuard key, endpoint, address, AllowedIPs, DNS and TOML type validation; rejected duplicate profile paths and added valid multi-peer config parsing.
- Gravion Trainner: rejected empty/duplicate expected phrases and empty runs, restricted cleartext HTTP to loopback endpoints, disabled redirects to protect API credentials, bounded response/dataset sizes, and added local HTTP + CLI end-to-end tests.
- Demo web: added HTML escaping, security headers, basic configuration validation, graceful shutdown and container healthcheck.
- CI: added demo tests, Playwright/Chromium runtime smoke testing, Compose/Caddy validation and a demo-container build job.


## 0.4.1 — 2026-11-04
- Fixed Privacyflow accepting TOML booleans as integer rotation intervals.
- Hardened Gravion Trainner dataset loading against missing files, non-object JSONL rows, empty identifiers/prompts and duplicate case IDs.
- Fixed case-insensitive missing-keyword reporting when expected terms differ only by capitalization.
- Validated model endpoint URLs and timeout bounds before network requests.
- Added support for text-part arrays in compatible chat-completions responses.
- Expanded regression coverage from 29 to 35 tests and removed generated Python bytecode from the release archive.

## 0.4.0 — 2026-11-04
- Confirmed the four product names: Localshare, Privacyflow, Agent Browser and Gravion Trainner.
- Consolidated the repository, product portfolio and documentation around these four independent projects.
- Added Agent Browser challenge detection and terminal-mediated human handoff.
- Added a dedicated Gravion Trainner architecture and measured evaluation pipeline document.
- Updated the test runner and CI matrix to cover exactly the four projects.
- Added a 29-test results record and current protected Quick Tunnel reference.

## 0.3.0 — 2026-11-04
- Expanded the product documentation, architecture guidance and development workflow.

## 0.2.0 — 2026-11-04
- Expanded Localshare from Quick Tunnel-only to Quick + configured Named Tunnel modes.
- Added local, named tunnel and direct VPS deployment documentation and a Caddy Compose demo.
- Added initial runnable Privacyflow, Agent Browser and Gravion Trainner utility starters with unit tests.

## 0.1.0 — initial foundation
- Initial product specifications and Localshare temporary tunnel CLI.
