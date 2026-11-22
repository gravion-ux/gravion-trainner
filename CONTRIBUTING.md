# Contributing to Gravion Trainner

Thanks for helping! Gravion Trainner is a model-quality evaluation
starter for OpenAI-compatible chat-completions endpoints, including
compatible local runtimes: point it at an endpoint, run a dataset,
get a report you can compare between models and runs.

The most valuable contributions are new evaluation metrics, dataset
formats, and tests.

## Ground rules

- **Zero runtime dependencies — hard rule.** Python standard library
  only; the evaluator talks to endpoints over plain HTTP.
- **Your keys, your endpoints.** Never commit an API key or a report
  generated against a private endpoint. CI runs a secret scan
  (`python scripts/scan-secrets.py .`) and it must stay green.

## Development setup

Requires Python 3.11 or newer:

```bash
git clone https://github.com/gravion-ux/gravion-trainner.git
cd gravion-trainner
python -m pip install --no-deps -e .
```

The package uses a `src/` layout (`src/gravion_trainner/`).

## Running the tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

That is exactly what CI runs, on Python 3.11, 3.12 and 3.13. CI
also runs the secret scan and static syntax/manifest checks
(`python scripts/syntax-checks.py .`).

Try the evaluator against a local runtime:

```bash
GRAVION_BASE_URL=http://localhost:11434/v1 \
GRAVION_MODEL=your-local-model \
python -m gravion_trainner.cli evaluate --dataset data/sample.jsonl --output reports/report.json
```

## Code style

- Tests are `unittest` test cases in `tests/` — match the existing
  style rather than introducing a second framework.
- Comments explain *why* a metric is computed the way it is.

## Pull request workflow

1. Fork and branch from `main`: `feat/<short-name>`,
   `fix/<short-name>`, `docs/<short-name>`.
2. Run the full test suite locally.
3. Open the PR against `main` with: what changed, why, how you
   tested it.
4. CI must be green — secret scan, syntax checks and the Python
   test matrix.
5. One logical change per PR.
