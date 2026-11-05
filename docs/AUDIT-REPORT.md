# Gravion Toolkit 0.4.3 — engineering audit

Audit date: 2026-11-04  
Scope: Localshare, Privacyflow, Agent Browser, Gravion Trainner, demo-web, Python/Node packaging, CI and deployment examples.

## Executive result

The local regression suite passes **82/82 tests**. Both Node packages pass `npm pack --dry-run`. Both Python packages build wheels and install in editable mode. JSON/TOML/YAML manifests parse, JavaScript syntax checks pass, Python bytecode compilation passes, the shared CLI/config smoke checks pass, and shell syntax validation passes.

This is a verified development release, not a production certification. Some external integrations could not be exercised in the offline audit container. Their status is listed below rather than treated as passed.

## Findings addressed

### Localshare

- Validate decimal TCP ports rather than accepting alternate numeric spellings.
- Format IPv6 loopback URLs with brackets.
- Verify the named-tunnel configuration path is readable and a regular file.
- Make `cloudflared` discovery work through process spawning rather than shell-specific `which`/`where` commands.
- Support explicitly configured wildcard email-domain allow-lists while rejecting malformed patterns.
- Add a child-process integration test with a fake `cloudflared` executable. It checks the actual arguments passed to the spawned process and verifies the temporary link is surfaced.

### Privacyflow

- Reject malformed TOML types, duplicate paths/keys/sections, invalid WireGuard key lengths, malformed addresses/endpoints/AllowedIPs and invalid port/keepalive values.
- Parse multiple `[Peer]` sections.
- Validate standard interface fields including MTU, Table, SaveConfig, ListenPort and FwMark.
- Accept DNS IPs and valid DNS search domains; reject malformed numeric-looking IP strings and empty entries.
- Reject unknown directives, executable `PreUp`/`PostUp`/`PreDown`/`PostDown` hooks and oversized config/profile files.
- Clarify that `require_kill_switch=true` is only a policy declaration in this release. No firewall kill switch, route change or active VPN rotation is implemented.

### Agent Browser

- Normalize allowed hostnames, reject URL/port/path entries and embedded credentials, and keep explicit host allow-list matching.
- Block loopback, private, link-local, reserved and non-public IPv4/IPv6 destinations by default; make private-network access an explicit operator opt-in.
- Block service workers so they cannot bypass Playwright's request routing.
- Keep visible browser operation and human handoff for authentication/challenge checkpoints.
- Pin the direct Playwright dependency to 1.64.1 and configure CI to install Chromium, run the browser runtime smoke and run `npm audit --audit-level=high`.
- Residual risk: DNS checks and browser-side request routing do not fully eliminate DNS rebinding/time-of-check-to-time-of-use races. Run only against domains you are authorised to access.

### Gravion Trainner

- Bound JSONL dataset size, row size, case count and HTTP response size.
- Reject empty datasets, malformed rows, duplicate IDs, empty/duplicate expected phrases and invalid model endpoint configuration.
- Restrict cleartext HTTP model endpoints to loopback, reject URL credentials/query/fragment, and disable redirects to prevent API-key forwarding.
- Add local HTTP mock-server and CLI end-to-end tests for successful runs, text-part responses, error responses and redirects.
- Residual limitation: this is a heuristic keyword-coverage evaluator. It does not autonomously fine-tune or retrain arbitrary model weights.

### demo-web and deployment examples

- Escape operator-configured HTML values, validate port input, add baseline security headers, and provide graceful shutdown.
- Run the demo container as the unprivileged Node user and include a health check.
- Add CI checks for Compose configuration, Caddyfile validation and demo-container build.

## Local verification matrix

| Area | Result |
|---|---|
| Localshare tests | 17/17 passed |
| Agent Browser policy/challenge/network tests | 19/19 passed |
| demo-web HTTP tests | 2/2 passed |
| Privacyflow parser/config tests | 24/24 passed |
| Gravion Trainner evaluator/mock API/CLI tests | 20/20 passed |
| **Total automated regression tests** | **82/82 passed** |
| JavaScript syntax checks | Passed |
| Python compile checks | Passed |
| JSON/TOML manifests | Parsed successfully |
| GitHub Actions YAML | Parsed successfully |
| Shell script syntax | Passed |
| Node package dry-run packaging | Both packages passed |
| Python wheel builds | Both packages passed |
| Python editable installs | Both packages passed |

## Not verified in this environment

The audit container could not resolve `registry.npmjs.org`; it also lacked `cloudflared`, Docker, Caddy, `wg` and `wg-quick`. Consequently:

- The Playwright Node module could not be installed because npm registry DNS was unavailable. A system Chromium 144 binary is present, but its direct headless smoke timed out in this container without D-Bus services; therefore no Playwright-driven browser session was locally verified. CI is configured to install them and run `npm run smoke:runtime`.
- `npm audit` and committed `package-lock.json` generation could not be completed locally. CI creates the npm lock as part of install and now runs `npm audit --audit-level=high`. A successful CI run and committing the generated lockfile are required before declaring the npm dependency graph fully locked.
- A live Cloudflare tunnel could not be opened.
- Actual WireGuard connect/disconnect, endpoint rotation, firewall kill-switch and DNS/IPv6 leak tests could not be run. Privacyflow does not yet change routes.
- Docker image build and Caddy/Compose runtime could not be run locally. CI contains corresponding configuration/build checks.
- No external production model endpoint was called; Gravion Trainner integration was tested against a local deterministic mock server.

`pip check` also reports an unrelated pre-existing conflict in the shared Python environment: MoviePy 2.2.1 requires Pillow below 12 while the environment has Pillow 12.3.0. Neither Gravion Python package depends on MoviePy or Pillow.

## Release recommendation

Suitable for developer preview, code review and continued implementation. Do not advertise the four apps as production-ready until the unavailable runtime checks pass, the npm lockfile and audit are committed, the residual network-policy risks are reviewed, and an independent security review is completed.

## Publication addendum (2026-11-05)

This addendum records facts established by an independent publication verification pass on Windows 11 (Node v24.14.0, npm 11.9.0, Python 3.15.0), after the 0.4.3 audit above was recorded. The 0.4.3 audit text above is unchanged and remains accurate as a record of that environment.

- The 82-test total was independently reproduced: **81 passed, 1 skipped, 0 failed**. The skipped test is an author-written `process.platform === "win32"` guard on the Localshare fake-`cloudflared` integration test, which does execute on CI's Ubuntu runners — which is why this Linux audit container recorded 82/82.
- A Windows-only defect in the Gravion Trainner **test harness** was found and fixed: the local mock HTTP server did not drain the POST request body, so Windows reset the socket and the client observed `ConnectionAbortedError` instead of the response. The product code and the redirect-blocking security property are unchanged. 30 consecutive runs now pass; 12 runs previously produced 4 failures.
- `npm audit` and lockfile generation could be completed here. `https://github.com/gravion-ux/agent-browser/tree/mainpackage-lock.json` is now committed and the audit reports **0 vulnerabilities**, so the JavaScript dependency graph is locked. This was an open item above.
- A credential scanner (`scripts/scan-secrets.py`) and a static syntax/manifest gate (`scripts/syntax-checks.py`) were added and wired into CI.
- Every item in "Not verified in this environment" above remains unverified **except** the npm lockfile/audit item. Playwright/Chromium runtime smoke, live Cloudflare tunnels, Docker/Caddy runtime checks and WireGuard connect/rotation/leak tests were still not exercised on this host.
- An independent third-party security review has **not** been performed.

Full detail: [PUBLICATION-VERIFICATION.md](PUBLICATION-VERIFICATION.md).
