# Gravion Trainner — publication verification record

Verification date: **2026-11-05**
Verification host: Windows 11 (10.0.26300, x64)
Toolchain: Node.js **v24.14.0**, npm **11.9.0**, Python **3.15.0**
Project version: **0.1.0**
Repository: https://github.com/gravion-ux/gravion-trainner
Scope: the Gravion Trainner evaluator, model client, dataset loader and CLI.

> **Maturity statement.** This project is a **development foundation and MVP
> scaffold**. Nothing in this record is a production-readiness certification, a
> security sign-off or an anonymity guarantee.

## 1. Executive result

Every test suite in this repository was executed on the verification host and
passes.

| Suite | Discovered | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| `python -m unittest discover -s tests -v` | 20 | 20 | 0 | 0 |
| **Total** | **20** | **20** | **0** | **0** |

A Windows-only defect in the **test harness** was found and fixed here: the local mock HTTP server did not drain the POST request body, so Windows reset the socket and the client observed `ConnectionAbortedError` instead of the real response. The product code and the redirect-blocking security property are unchanged. 30 consecutive runs now pass; 12 runs previously produced 4 failures.

## 2. Static syntax, manifest and CLI gate

`scripts/syntax-checks.py` is an offline, layout-agnostic gate that reproduces
the static portion of `scripts/test-all.sh`. It is executed by the CI
`syntax-checks` job. It needs no network access, no credentials and no external
services.

| Check | Result | Detail |
|---|---|---|
| `javascript-syntax` | SKIP | no .js files in this repository |
| `python-compile` | PASS | compiled 3 director(ies) |
| `json-manifests` | PASS | 1 file(s) parsed |
| `jsonl-datasets` | PASS | 1 dataset(s) parsed line by line |
| `toml-manifests` | PASS | 1 file(s) parsed |
| `yaml-manifests` | PASS | 1 file(s) parsed |
| `shell-syntax` | PASS | 1 script(s) passed bash -n |
| `cli-smoke` | PASS | 1 entry point(s) ran successfully |

The CLI smoke check exercises the entry points declared in
`scripts/smoke-commands.json`; all of them exit `0`.

## 3. Secret and credential scan

`scripts/scan-secrets.py` fails the build on high-confidence credential
patterns and on files that must never be committed (`.env*`, `*.pem`, `*.key`,
`*.p12`, `*.pfx`, `id_rsa`, `id_ed25519`, `*.npmrc`, `*.netrc`,
`*credentials*`, `cloudflared*.json`, `profiles/*.conf`).

**Result on this repository: CLEAN.** 31 files inspected, 0 hard
matches, 0 forbidden filenames.

- soft  tests/test_evaluator.py:98  secret-shaped assignment (review only)

The scanner was validated with a negative test: 8 planted secrets (AWS access
key, GitHub token, PEM private key block, OpenAI-style key, `.env`, `.pem`,
`.npmrc`, WireGuard profile) were **all detected** with exit code `1`, and a
clean directory passed with exit code `0`.

The repository `.gitignore` excludes `.env`, `.env.*`, `cloudflared/*.json`,
`cloudflared/*.pem`, `profiles/*.conf`, `reports/*.json`, `node_modules/` and
the common cache directories.

## 4. CI configuration

| Job | Runs | Purpose |
|---|---:|---|
| `secret-scan` | 1 | Fails the build on committed credentials or secret-bearing files |
| `syntax-checks` | 1 | Static syntax, manifest parsing and CLI smoke gate |
| `python-tests` | 3 | Test suite on Python 3.11, 3.12 and 3.13 |

The workflow is named `CI` and stored at `.github/workflows/ci.yml`. It uses a
`concurrency` group that cancels superseded runs, reduces `permissions` to
`contents: read`, bounds every job with `timeout-minutes` and uses
`fail-fast: false` on matrices so one failing leg does not hide the others.

The Actions tab on the repository is the authoritative per-commit result.

## 5. Still not verifiable in this environment

These items are **not** counted as passes anywhere in this document.

| Item | Status | Why |
|---|---|---|
| External production model endpoint | Unverified locally | no external endpoint was called; integration was exercised against a local deterministic mock server |
| Real model quality measurement | Unverified locally | the evaluator is a heuristic keyword-coverage grader, not an intelligence score |
| Fine-tuning or adapter training | Unverified locally | not implemented in this release |
| Independent third-party security review | Unverified locally | **not performed** |

## 6. Relationship to the original Gravion Toolkit bundle

This repository was split out of the `gravion-toolkit-v0.4.3` bundle (archive
sha256 `5e711fd37fdf2953a4645d26187828f83e796f18243a330bc2721bb3290e5db1`,
77,597 bytes).

**Project files carried over byte-identical from the bundle: 6.**

Changed project files:

- `README.md`

Files present in this repository that were not inside the bundle's
`apps/gravion-trainner/` folder - the shared bundle-level files (`LICENSE`,
`.gitignore`, `CHANGELOG.md`) moved to the repository root, the shared
documentation, plus the per-repository CI workflow, scripts and verification
record:

- `.gitattributes`
- `.github/workflows/ci.yml`
- `.gitignore`
- `CHANGELOG.md`
- `LICENSE`
- `MANIFEST.md`
- `VERSION`
- `docs/API-CONTRACTS.md`
- `docs/ARCHITECTURE.md`
- `docs/AUDIT-REPORT.md`
- `docs/BRANDING.md`
- `docs/DEPENDENCIES.md`
- `docs/DEVELOPMENT.md`
- `docs/PRODUCTS.md`
- `docs/PUBLICATION-VERIFICATION.md`
- `docs/REFERENCES.md`
- `docs/ROADMAP.md`
- `docs/SECURITY.md`
- `docs/TEST-RESULTS.md`
- `docs/THREAT-MODEL.md`
- `docs/TRAINNER-ARCHITECTURE.md`
- `scripts/scan-secrets.py`
- `scripts/smoke-commands.json`
- `scripts/syntax-checks.py`
- `scripts/test-all.sh`

The shared toolkit documentation (`docs/PRODUCTS.md`, `docs/ARCHITECTURE.md`,
`docs/SECURITY.md`, `docs/THREAT-MODEL.md`, `docs/ROADMAP.md`,
`docs/TEST-RESULTS.md`, `docs/AUDIT-REPORT.md`, `docs/DEPENDENCIES.md`,
`docs/API-CONTRACTS.md`, `docs/BRANDING.md`, `docs/REFERENCES.md`,
`docs/BUNDLE-STATUS.md`), the MIT `LICENSE` and the toolkit `CHANGELOG.md` are
included so the project keeps its engineering history and its sibling-project
context. Path references inside those documents were rewritten so every link
resolves inside this repository; references to the other three projects now
point at their own repositories.

The project code moved from `apps/gravion-trainner/` to the repository root, so the
package is installed and tested directly from a checkout:

```bash
git clone https://github.com/gravion-ux/gravion-trainner.git
cd gravion-trainner
```

## 7. Release recommendation

**Suitable for developer preview, code review and continued implementation.**

**Not** suitable for production use, and not to be advertised as production
ready. Before any production deployment, the outstanding items in section 5
must be exercised and an independent security review must be completed.

The sibling projects in the Gravion Toolkit are published separately as
[`localshare`, `privacyflow`, `agent-browser`].
