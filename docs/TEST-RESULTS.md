# Test results

Release: 0.1.0
Run date: 2026-11-06
Command: `bash scripts/test-all.sh`

Verified local regression counts: Localshare 40, Agent Browser 43, demo-web 5, Privacyflow 38, Gravion Trainner 27 — **153 tests, 152 passed, 1 skipped**. The single skip is the Localshare fake-cloudflared process integration test: it is skipped on Windows because the POSIX shebang fixture script cannot run there, and it runs in the Linux CI job. The Python profile tests cover multiple peers, DNS search domains, WireGuard ListenPort/FwMark, invalid and unknown options, executable hook rejection, and size limits. The Localshare suite includes the fake-cloudflared process integration test and the HTTP origin pre-flight checks. The Agent Browser suite now covers the command-line parser, the domain allow-list and the private-network checks. The Trainner suite includes a local HTTP mock-server plus CLI integration test covering successful evaluation and report creation, text-part arrays, HTTP errors and redirect rejection.

The previous recorded run (2026-11-04) reported 82/82 passed. That figure is superseded by the counts above. The environment statements below describe the local audit container of that earlier run; they were not re-verified in this pass.

The full local regression suite also includes CLI help/config validation, JavaScript syntax checks, and Python bytecode compilation. Both Python packages were built as wheels and installed in editable mode with the installed setuptools backend. Both Node packages passed `npm pack --dry-run`. Their console entry points and help paths were checked.

Browser runtime smoke tests are maintained separately as `npm run smoke:runtime`. The container has a system Chromium 144 binary, but the Playwright Node module could not be installed because npm registry DNS was unavailable; a direct headless Chromium smoke also timed out in this container without its D-Bus services. CI installs Playwright and its managed Chromium browser, then runs the browser smoke test.

The local audit environment could not resolve `registry.npmjs.org`, and had no `cloudflared`, Docker, Caddy, `wg` or `wg-quick` executables. Therefore the following could not be executed locally: Playwright-driven Chromium launch (the system Chromium 144 direct smoke timed out without container D-Bus services; the Playwright Node module could not be installed), npm audit/lockfile generation, live Cloudflare tunnels, active WireGuard switching/leak tests, and Docker/Caddy deployment. CI installs Playwright/Chromium and runs the browser runtime smoke; deployment configuration checks are also wired into CI. End-to-end tunnel/VPN/VPS validation still requires external credentials and infrastructure.

`pip check` reports a pre-existing environment conflict: `moviepy 2.2.1` requires `pillow<12`, while the shared Python environment has Pillow 12.3.0. Neither Gravion Python package declares Pillow or MoviePy dependencies, so this is unrelated to the toolkit.
