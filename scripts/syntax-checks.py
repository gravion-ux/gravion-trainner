#!/usr/bin/env python3
"""Repository-wide static syntax, manifest and CLI smoke checks.

Layout-agnostic: it discovers sources from the repository tree instead of
assuming a fixed directory layout, so the same script works for every
repository in the Gravion Toolkit.

Checks performed:

1.  ``javascript-syntax``  - ``node --check`` over every ``.js`` file.
2.  ``python-compile``     - bytecode compilation of every Python source tree.
3.  ``json-manifests``     - every ``.json`` file parses.
4.  ``jsonl-datasets``     - every ``.jsonl`` line parses as a JSON object.
5.  ``toml-manifests``     - every ``.toml`` file parses.
6.  ``yaml-manifests``     - every ``.yml``/``.yaml`` file parses (needs PyYAML;
                             reported as skipped, never failed, when absent).
7.  ``shell-syntax``       - ``bash -n`` over every ``.sh`` file.
8.  ``cli-smoke``          - the commands declared in ``scripts/smoke-commands.json``.

Every check is offline and deterministic: no network access, no API keys and no
external services are required.

Usage::

    python scripts/syntax-checks.py [repo_root]

Exit codes: ``0`` all checks passed, ``1`` at least one check failed,
``2`` the script itself could not run.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache",
             ".mypy_cache", ".venv", "venv", "dist", "build", "reports", "htmlcov",
             "playwright-report", "test-results", ".tox", ".idea"}


def find_tool(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def iter_files(root: Path, suffixes: tuple[str, ...]):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.suffix.lower() in suffixes:
            yield path, rel.as_posix()


class Results:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def ok(self, name: str, detail: str) -> None:
        self.rows.append(("PASS", name, detail))

    def skip(self, name: str, detail: str) -> None:
        self.rows.append(("SKIP", name, detail))

    def fail(self, name: str, detail: str) -> None:
        self.rows.append(("FAIL", name, detail))

    @property
    def failed(self) -> int:
        return sum(1 for status, _, _ in self.rows if status == "FAIL")


def check_javascript(root: Path, results: Results) -> None:
    node = find_tool("node", "node.exe")
    files = list(iter_files(root, (".js",)))
    if not files:
        results.skip("javascript-syntax", "no .js files in this repository")
        return
    if not node:
        results.skip("javascript-syntax", "node is not installed")
        return
    failures = []
    for path, _rel in files:
        proc = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
        if proc.returncode != 0:
            failures.append(f"{path.relative_to(root).as_posix()}: {proc.stderr.strip()}")
    if failures:
        results.fail("javascript-syntax", "; ".join(failures[:5]))
    else:
        results.ok("javascript-syntax", f"{len(files)} file(s) parsed by node --check")


def check_python_compile(root: Path, results: Results) -> None:
    dirs = sorted({path.parent for path, _rel in iter_files(root, (".py",))})
    if not dirs:
        results.skip("python-compile", "no .py files in this repository")
        return
    failures = []
    for directory in dirs:
        proc = subprocess.run([sys.executable, "-m", "compileall", "-q", str(directory)],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            failures.append(f"{directory.relative_to(root).as_posix()}: "
                            f"{(proc.stdout + proc.stderr).strip()[:300]}")
    if failures:
        results.fail("python-compile", "; ".join(failures[:5]))
    else:
        results.ok("python-compile", f"compiled {len(dirs)} director(ies)")


def check_json(root: Path, results: Results) -> None:
    files = list(iter_files(root, (".json",)))
    failures = []
    for path, rel in files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            failures.append(f"{rel}: {exc}")
    if failures:
        results.fail("json-manifests", "; ".join(failures[:5]))
    else:
        results.ok("json-manifests", f"{len(files)} file(s) parsed")


def check_jsonl(root: Path, results: Results) -> None:
    files = list(iter_files(root, (".jsonl",)))
    failures = []
    for path, rel in files:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                failures.append(f"{rel}:{number}: {exc}")
    if failures:
        results.fail("jsonl-datasets", "; ".join(failures[:5]))
    else:
        results.ok("jsonl-datasets", f"{len(files)} dataset(s) parsed line by line")


def check_toml(root: Path, results: Results) -> None:
    files = list(iter_files(root, (".toml",)))
    failures = []
    for path, rel in files:
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeDecodeError, OSError) as exc:
            failures.append(f"{rel}: {exc}")
    if failures:
        results.fail("toml-manifests", "; ".join(failures[:5]))
    else:
        results.ok("toml-manifests", f"{len(files)} file(s) parsed")


def check_yaml(root: Path, results: Results) -> None:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        results.skip("yaml-manifests", "PyYAML is not installed (install it to enable this check)")
        return
    files = list(iter_files(root, (".yml", ".yaml")))
    failures = []
    for path, rel in files:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - yaml raises many types
            failures.append(f"{rel}: {exc}")
    if failures:
        results.fail("yaml-manifests", "; ".join(failures[:5]))
    else:
        results.ok("yaml-manifests", f"{len(files)} file(s) parsed")


def check_shell(root: Path, results: Results) -> None:
    bash = find_tool("bash")
    if not bash:
        results.skip("shell-syntax", "bash is not installed")
        return
    files = list(iter_files(root, (".sh",)))
    failures = []
    for _path, rel in files:
        # Use a repo-relative POSIX path: Git Bash on Windows cannot open a
        # native Windows absolute path such as C:\... .
        proc = subprocess.run([bash, "-n", rel], cwd=str(root), capture_output=True, text=True)
        if proc.returncode != 0:
            failures.append(f"{rel}: {proc.stderr.strip()}")
    if failures:
        results.fail("shell-syntax", "; ".join(failures[:5]))
    else:
        results.ok("shell-syntax", f"{len(files)} script(s) passed bash -n")


def _resolve_command(cmd: list[str]) -> list[str]:
    first = cmd[0]
    if first in ("python", "python3"):
        return [sys.executable] + list(cmd[1:])
    if os.name == "nt" and os.path.sep not in first:
        for candidate in (first, first + ".cmd", first + ".exe"):
            found = shutil.which(candidate)
            if found:
                return [found] + list(cmd[1:])
    return cmd


def check_cli_smoke(root: Path, results: Results) -> None:
    spec_path = root / "scripts" / "smoke-commands.json"
    if not spec_path.is_file():
        results.skip("cli-smoke", "scripts/smoke-commands.json not present")
        return
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        results.fail("cli-smoke", f"scripts/smoke-commands.json is not valid JSON: {exc}")
        return

    failures = []
    for entry in spec:
        label = entry.get("label", " ".join(entry.get("cmd", [])))
        cwd = root / entry.get("cwd", ".")
        cmd = _resolve_command(list(entry["cmd"]))
        env = dict(os.environ)
        for key, value in (entry.get("env") or {}).items():
            env[key] = value.replace("$ROOT", str(root))
        if not cwd.is_dir():
            failures.append(f"{label}: working directory missing ({cwd})")
            continue
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            output = (proc.stdout + proc.stderr).strip().replace("\n", " ")[:300]
            failures.append(f"{label}: exit {proc.returncode}: {output}")
    if failures:
        results.fail("cli-smoke", "; ".join(failures))
    else:
        results.ok("cli-smoke", f"{len(spec)} entry point(s) ran successfully")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.is_dir():
        print(f"syntax-checks: {root} is not a directory", file=sys.stderr)
        return 2

    results = Results()
    check_javascript(root, results)
    check_python_compile(root, results)
    check_json(root, results)
    check_jsonl(root, results)
    check_toml(root, results)
    check_yaml(root, results)
    check_shell(root, results)
    check_cli_smoke(root, results)

    width = max(len(name) for _s, name, _d in results.rows)
    for status, name, detail in results.rows:
        print(f"{status:4}  {name.ljust(width)}  {detail}")

    if results.failed:
        print(f"\nsyntax-checks: FAILED ({results.failed} check(s) failed)", file=sys.stderr)
        return 1
    passed = sum(1 for status, _, _ in results.rows if status == "PASS")
    skipped = sum(1 for status, _, _ in results.rows if status == "SKIP")
    print(f"\nsyntax-checks: OK ({passed} passed, {skipped} skipped)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
