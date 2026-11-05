# Dependency audit

## Runtime requirements

| Project | Runtime | External runtime dependency | Verification state |
|---|---|---|---|
| Localshare | Node.js >=20 | `cloudflared` binary on PATH | CLI unit/process tests pass; live tunnel unavailable in the audit environment |
| Privacyflow | Python >=3.11 | None; Python standard library only | Editable package build/install and config validation pass |
| Agent Browser | Node.js >=20 | Playwright 1.64.1 plus downloaded Chromium | Direct dependency pinned; install/runtime smoke configured in CI; local registry access unavailable |
| Gravion Trainner | Python >=3.11 | None; Python standard library only | Editable package build/install and local HTTP mock endpoint integration pass |
| Demo web | Node.js >=20 | None | HTTP integration tests pass |
| VPS example | Docker Engine + Compose | Caddy 2 image and Node 22 Alpine image | CI configuration validation and container build configured; local Docker executable unavailable |

## Dependency installation

Agent Browser:

```bash
cd https://github.com/gravion-ux/agent-browser/tree/main
npm install
npx playwright install chromium
npm test
npm run smoke:runtime
```

Python applications:

```bash
cd https://github.com/gravion-ux/privacyflow/tree/main
python -m pip install -e .
```

```bash
cd 
python -m pip install -e .
```

The Python projects have no runtime third-party dependencies. Their build backend requires `setuptools>=68`.

## Reproducibility and audit note

The Agent Browser direct dependency is pinned to Playwright 1.64.1. A package lockfile and `npm audit` result are not included in this release because the build environment could not resolve `registry.npmjs.org`; dependency installation and advisory scanning must run in a network-enabled environment. CI runs `npm install --no-fund`, then `npm audit --audit-level=high`, installs Chromium, and performs a browser runtime smoke test. Commit the generated `package-lock.json` after a successful network-enabled install before treating the JavaScript dependency graph as fully locked.

Do not commit real WireGuard profiles, tunnel credentials, API keys, cookies or personal evaluation datasets.

## Publication addendum (2026-11-05)

The reproducibility note above records the 0.4.3 audit environment, in which `registry.npmjs.org` was unreachable. That gap has since been closed:

- `https://github.com/gravion-ux/agent-browser/tree/mainpackage-lock.json` is committed (lockfile version 3). The tree resolves to **2 packages** — `playwright@1.64.1` and `playwright-core@1.64.1` — with no transitive runtime dependencies.
- `npm audit --audit-level=high` reports **`found 0 vulnerabilities`** (exit code 0).
- `npm ci --no-fund` succeeds against the committed lockfile, so CI installs a reproducible dependency tree instead of re-resolving versions.
- `localshare` and `demo-web` declare no runtime dependencies and therefore have no lockfile; CI runs no install step for them.

The committed lockfile and the advisory-audit result are now part of the release, so the JavaScript dependency graph is fully locked. Full detail: [PUBLICATION-VERIFICATION.md](PUBLICATION-VERIFICATION.md).
