# Development setup

## Prerequisites
- Python 3.11 or newer
- No third-party runtime dependencies - the standard library is enough
- An OpenAI-compatible model endpoint to run a real evaluation (a local runtime such as Ollama is enough)

## Install and test

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## One-command runner

```bash
bash scripts/test-all.sh
```

This runs the test suite, the CLI smoke checks, the static syntax gate and the credential scan.

## Static checks only

```bash
python scripts/syntax-checks.py .
python scripts/scan-secrets.py .
```

## Code quality expectations
- Keep every network exposure explicit and documented.
- Add tests for argument validation, security policy and failure handling.
- Never commit API keys, provider endpoints, cookies or personal evaluation datasets.
- Keep safety-critical operations in narrow modules with dry-run and rollback paths.
- Update `MANIFEST.md`, `docs/` and `CHANGELOG.md` when implementation maturity changes.
