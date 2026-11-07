#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

(cd "$ROOT" && PYTHONPATH=src python -m unittest discover -s tests -v \
  && PYTHONPATH=src python -m gravion_trainner.cli --help >/dev/null)

python -m compileall -q "$ROOT/src"
python scripts/syntax-checks.py "$ROOT"
python scripts/scan-secrets.py "$ROOT"
