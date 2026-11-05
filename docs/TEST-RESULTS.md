# Test results

Release: 0.4.3
Run date: 2026-11-04
Command: `bash scripts/test-all.sh`

Verified local regression counts: Localshare 17, Agent Browser 19, demo-web 2, Privacyflow 24, Gravion Trainner 20 — **82/82 passed**. The Python profile tests now cover multiple peers, DNS search domains, WireGuard ListenPort/FwMark, invalid/unknown options, executable hook rejection, and size limits. The Localshare suite includes a fake-cloudflared process integration test. The Trainner suite includes a local HTTP mock-server plus CLI integration test covering successful evaluation/report creation, text-part arrays, HTTP errors and redirect rejection.

The full local regression suite also includes CLI help/config validation, JavaScript syntax checks, and Python bytecode compilation. Both Python packages were built as wheels and installed in editable mode with the installed setuptools backend. Both Node packages passed `npm pack --dry-run`. Their console entry points and help paths were checked.

Browser runtime smoke tests are maintained separately as `npm run smoke:runtime`. The container has a system Chromium 144 binary, but the Playwright Node module could not be installed because npm registry DNS was unavailable; a direct headless Chromium smoke also timed out in this container without its D-Bus services. CI installs Playwright and its managed Chromium browser, then runs the browser smoke test.

The local audit environment could not resolve `registry.npmjs.org`, and had no `cloudflared`, Docker, Caddy, `wg` or `wg-quick` executables. Therefore the following could not be executed locally: Playwright-driven Chromium launch (the system Chromium 144 direct smoke timed out without container D-Bus services; the Playwright Node module could not be installed), npm audit/lockfile generation, live Cloudflare tunnels, active WireGuard switching/leak tests, and Docker/Caddy deployment. CI installs Playwright/Chromium and runs the browser runtime smoke; deployment configuration checks are also wired into CI. End-to-end tunnel/VPN/VPS validation still requires external credentials and infrastructure.

`pip check` reports a pre-existing environment conflict: `moviepy 2.2.1` requires `pillow<12`, while the shared Python environment has Pillow 12.3.0. Neither Gravion Python package declares Pillow or MoviePy dependencies, so this is unrelated to the toolkit.
