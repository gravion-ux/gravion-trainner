# Gravion Trainner - repository manifest

Version: 0.1.0
Repository: https://github.com/gravion-ux/gravion-trainner
Published: 2026-11-05

## Contents

- `src/gravion_trainner/`: OpenAI-compatible client, JSONL dataset loader, heuristic evaluator and CLI
- `tests/`: evaluator, local mock HTTP server and CLI end-to-end regression tests
- `data/sample.jsonl`: example evaluation dataset
- `pyproject.toml`: Python package manifest (standard library only)
- `docs/`: shared toolkit documentation plus the Trainner architecture document
- `scripts/`: secret scanner, static syntax gate, smoke commands and a one-command test runner
- `.github/workflows/ci.yml`: Python 3.11/3.12/3.13 tests, static checks and a secret scan

## Security

No API keys, model endpoints, provider credentials or personal evaluation
datasets are included. API credentials are read from the environment only.

See `docs/PUBLICATION-VERIFICATION.md` for the verified checks and the explicit
environment limitations.
