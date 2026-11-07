#!/usr/bin/env python3
"""Fail the build if the repository contains credentials or secret-bearing files.

Checks tracked working-tree content for high-confidence credential patterns and for
files that must never be committed (.env, private keys, real WireGuard profiles,
tunnel credentials). Soft "looks like a secret" assignments are reported for
review but do not fail the build, because test fixtures legitimately contain
dummy values such as api_key="do-not-forward".

Usage:  python scripts/scan-secrets.py [root]
Exit code 0 = clean, 1 = hard match or forbidden filename found, 2 = scanner error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SELF = Path(__file__).name

HARD_PATTERNS = [
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("AWS secret access key", re.compile(r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b")),
    ("Stripe live key", re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
    ("Bearer token literal", re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.=]{24,}")),
    ("Cloudflare API token", re.compile(r"(?i)cloudflared[_-]?(?:api)?[_-]?token\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{30,}")),
]

SOFT_PATTERNS = [
    ("secret-shaped assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token|client[_-]?secret|password|passwd|private[_-]?key)\b"
        r"\s*[=:]\s*['\"][^'\"\s]{6,}['\"]")),
    ("env var holding a secret", re.compile(
        r"(?i)^\s*(?:export\s+)?[A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*\s*=")),
]

FORBIDDEN_NAMES = re.compile(
    r"(^|/)(\.env($|\.)|.*\.pem$|.*\.key$|.*\.p12$|.*\.pfx$|.*\.keystore$|"
    r"id_rsa$|id_ed25519$|.*credentials.*|.*\.npmrc$|.*\.netrc$|"
    r"cloudflared.*\.json$|profiles/.*\.conf$)",
    re.IGNORECASE)

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache",
             ".mypy_cache", ".venv", "venv", "reports", "dist", "build"}


def scan(root: Path):
    hard: list[tuple[str, int, str]] = []
    soft: list[tuple[str, int, str]] = []
    forbidden: list[str] = []
    scanned = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.name == SELF:
            continue
        rel = path.relative_to(root).as_posix()
        scanned += 1
        if FORBIDDEN_NAMES.search(rel):
            forbidden.append(rel)
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in HARD_PATTERNS:
            for match in pattern.finditer(text):
                hard.append((rel, text[:match.start()].count("\n") + 1, label))
        for label, pattern in SOFT_PATTERNS:
            for match in pattern.finditer(text):
                soft.append((rel, text[:match.start()].count("\n") + 1, label))
    return scanned, hard, soft, forbidden


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    try:
        scanned, hard, soft, forbidden = scan(root)
    except OSError as exc:
        print(f"scan-secrets: cannot scan {root}: {exc}", file=sys.stderr)
        return 2

    print(f"scan-secrets: inspected {scanned} files under {root}")
    for rel, line, label in hard:
        print(f"HARD  {rel}:{line}  {label}", file=sys.stderr)
    for rel in forbidden:
        print(f"FILE  {rel}  must not be committed", file=sys.stderr)
    for rel, line, label in soft:
        print(f"soft  {rel}:{line}  {label} (review only)")
    if hard or forbidden:
        print(f"scan-secrets: FAILED ({len(hard)} hard match(es), {len(forbidden)} forbidden file(s))",
              file=sys.stderr)
        return 1
    print("scan-secrets: CLEAN - no credentials or secret-bearing files detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
