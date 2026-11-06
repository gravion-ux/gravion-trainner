# Remediation notes — 2026-11, second pass

This file records the second audit pass over the Gravion Trainner repository in
November 2026. It is additive: the earlier `docs/REMEDIATION-2026-11.md` keeps the
record of the first pass and is not modified by this one.

## Method

Every source file, test file and document was read again. Each suspected defect was
confirmed with a regression test before the fix was applied.

## Defects fixed

| Severity | Defect | Fix |
| --- | --- | --- |
| Medium | The package exposed no public API: `load_dataset`, `evaluate`, `score_output` and `OpenAICompatibleClient` were only reachable through the private `gravion_trainner.evaluator` module | The package now re-exports the public API with a sorted `__all__` and a `__version__` |
| Low | `cli.main()` read `sys.argv` directly, so the command could not be called with an argument list | `cli.main(argv)` accepts an argument list and falls back to `sys.argv` when it is omitted |
| Low | `docs/TEST-RESULTS.md` claimed 82/82 tests from the 2026-11-04 run while the suites had grown since | The document now records the verified counts of the current run: 153 tests, 152 passed, 1 skipped, and it marks the old figure as superseded |

## Fixes re-verified, no change needed

The first pass already fixed the following, and this pass confirmed the fixes are
present in the published code: the dataset size, line and case limits, the
duplicate case and duplicate phrase checks, the redirect rejection that keeps
model credentials from following a redirect, the loopback-only rule for plain HTTP
endpoints, and the response size limit.

## Documentation and spelling corrections

- `LICENSE` shipped a truncated MIT text without the warranty and liability
  clauses. The complete canonical MIT text is now in place.
- Spelling was inconsistent (`authorised` against `authorization` and `normalized`).
  The prose now uses one convention: American English.

## Verification

| Check | Before | After |
| --- | --- | --- |
| Gravion Trainner tests | 23 passed | 27 passed |
| Documented test total | 82/82 (stale) | 153 tests, 152 passed, 1 skipped |

## Residual limitations

- The score is a keyword-coverage heuristic. A high score says that expected
  phrases appear in the output; it does not measure correctness, reasoning or
  safety.
- The evaluator needs a model endpoint and a credential. Nothing was called
  against a live provider during this pass; the CLI test uses a local HTTP mock.
- The report stores the full model output next to the score, so it can contain
  whatever the model returned. Treat the report file as sensitive.
