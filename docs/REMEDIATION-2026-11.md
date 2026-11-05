# Gravion Trainner remediation — 2026-11-05

This file records a defect audit and the fixes applied on top of the published
v0.1.0 tree. The original `README.md`, `CHANGELOG.md`, `docs/AUDIT-REPORT.md`,
`docs/TEST-RESULTS.md` and `docs/SECURITY.md` are left unchanged so the earlier
audit record stays intact; this file is the new evidence.

Audit method: `src/gravion_trainner/evaluator.py` and
`src/gravion_trainner/cli.py` were read in full, then each suspected defect was
reproduced with an executable probe that used raw sockets to drive the HTTP
client. Every fix below is covered by a regression test that fails on the
pre-fix code.

## Fixes

### 1. A malformed endpoint response escaped as a raw traceback (medium)

* Where: `src/gravion_trainner/evaluator.py`, `complete`;
  `src/gravion_trainner/cli.py`, `main`.
* Cause: the transport handler caught `URLError`, `TimeoutError`, `OSError` and
  the JSON and Unicode decode errors, but not `http.client.HTTPException`. A
  server that answers with a malformed status line, an over-long header line or
  a truncated message therefore raised `http.client.BadStatusLine` straight out
  of `complete()`. The CLI only catches `OSError`, `ValueError` and
  `RuntimeError`, so the operator saw a Python traceback and exit status 1
  instead of the documented one-line error and exit status 2.
* Fix: `http.client.HTTPException` is now caught in `complete()` and reported as
  `RuntimeError: Model endpoint request failed: <ExceptionName>`, and the CLI
  error handler also accepts `http.client.HTTPException` as a backstop. Every
  transport failure now takes the same clean path.
* Test: `tests/test_evaluator.py` —
  `test_malformed_status_line_raises_runtime_error`,
  `test_cli_reports_a_malformed_endpoint_without_a_traceback`.

### 2. A dataset starting with a UTF-8 BOM was rejected (low)

* Where: `src/gravion_trainner/evaluator.py`, `load_dataset`.
* Cause: the dataset was read with plain `utf-8`, which keeps a leading byte
  order mark, so the first JSON object no longer parsed and the loader reported
  "Invalid JSONL on line 1" for a file that is otherwise valid JSONL. Windows
  editors commonly add the mark.
* Fix: the dataset is read with `utf-8-sig`, which strips the mark when it is
  present and behaves identically when it is not.
* Test: `tests/test_evaluator.py` — `test_loads_dataset_with_utf8_bom`.

## Test status after the fixes

| Suite | Before | After |
|---|---|---|
| `tests/test_evaluator.py` | 20 | 23 |

Full local gate on 2026-11-05 (Windows 11, Python 3.15.0): 23/23 tests passed,
`scripts/syntax-checks.py` 7/7 checks passed (JavaScript check skipped — no
JavaScript in this repository), `scripts/scan-secrets.py` clean.

## Known limitations that were deliberately not changed

* The low-level `score_output` helper still accepts expected phrases that
  differ only by case, so one output can satisfy two case variants and both are
  counted in the score. The dataset loader rejects case-insensitive duplicates,
  so every path that reads a dataset is unaffected; the helper was left as it
  is because the existing suite relies on case-variant phrases to check
  case-insensitive matching.
* Keyword coverage remains a heuristic smoke test. It does not measure
  correctness, reasoning, factuality or safety, and a high score is not
  evidence that a model is fit to promote.
* A cleartext HTTP endpoint is accepted for any host name ending in
  `.localhost`. That name is reserved for loopback by RFC 6761, but the host is
  not resolved and checked before the request is made.
* No external production model endpoint was called during this audit; the
  integration tests use a local deterministic mock server.
