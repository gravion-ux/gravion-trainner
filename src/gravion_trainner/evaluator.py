from __future__ import annotations

import ipaddress
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

MAX_DATASET_BYTES = 5 * 1024 * 1024
MAX_DATASET_LINE_BYTES = 1024 * 1024
MAX_DATASET_CASES = 10_000
MAX_RESPONSE_BYTES = 10 * 1024 * 1024


@dataclass
class EvalCase:
    case_id: str
    prompt: str
    expected_contains: list[str]


def load_dataset(path: str | Path) -> list[EvalCase]:
    dataset_path = Path(path)
    try:
        if dataset_path.stat().st_size > MAX_DATASET_BYTES:
            raise ValueError(f"Dataset exceeds the {MAX_DATASET_BYTES}-byte limit")
        lines = dataset_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"Cannot read dataset: {exc}") from exc
    except UnicodeError as exc:
        raise ValueError("Dataset must be valid UTF-8 JSONL") from exc

    cases: list[EvalCase] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if len(line.encode("utf-8")) > MAX_DATASET_LINE_BYTES:
            raise ValueError(f"Line {line_number} exceeds the per-line size limit")
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL on line {line_number}") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"Line {line_number} must contain a JSON object")
        case_id, prompt = raw.get("id"), raw.get("prompt")
        if not isinstance(case_id, str) or not case_id.strip() or not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"Line {line_number} requires non-empty string fields id and prompt")
        if case_id in seen_ids:
            raise ValueError(f"Line {line_number}: duplicate case id {case_id!r}")
        seen_ids.add(case_id)
        expected = raw.get("expected_contains", [])
        if not isinstance(expected, list) or not expected or any(not isinstance(item, str) or not item.strip() for item in expected):
            raise ValueError(f"Line {line_number}: expected_contains must be a non-empty list of non-empty strings")
        folded = [item.casefold() for item in expected]
        if len(set(folded)) != len(folded):
            raise ValueError(f"Line {line_number}: expected_contains must not contain duplicate phrases")
        cases.append(EvalCase(case_id, prompt, expected))
        if len(cases) > MAX_DATASET_CASES:
            raise ValueError(f"Dataset exceeds the {MAX_DATASET_CASES}-case limit")
    if not cases:
        raise ValueError("Dataset has no evaluation cases")
    return cases


def score_output(output: str, expected_contains: list[str]) -> dict[str, Any]:
    if not isinstance(output, str):
        raise ValueError("Model output must be a string")
    if not isinstance(expected_contains, list) or not expected_contains or any(not isinstance(item, str) or not item.strip() for item in expected_contains):
        raise ValueError("Expected phrases must be a non-empty list of non-empty strings")
    normalized = output.casefold()
    matched = [item for item in expected_contains if item.casefold() in normalized]
    matched_folded = {item.casefold() for item in matched}
    total = len(expected_contains)
    score = 1.0 if total == 0 else len(matched) / total
    return {
        "score": round(score, 4),
        "matched": matched,
        "missing": [item for item in expected_contains if item.casefold() not in matched_folded],
    }


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not forward model API credentials to redirected destinations."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OpenAICompatibleClient:
    def __init__(self, base_url: str | None = None, model: str | None = None,
                 api_key: str | None = None, timeout: int = 60):
        self.base_url = (base_url or os.getenv("GRAVION_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = (model or os.getenv("GRAVION_MODEL", "")).strip()
        self.api_key = api_key if api_key is not None else os.getenv("GRAVION_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        self.timeout = timeout

        parsed = urlsplit(self.base_url)
        try:
            _ = parsed.port
        except ValueError as exc:
            raise ValueError("base_url contains an invalid port") from exc
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("base_url must be an absolute HTTP(S) URL without embedded credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("base_url must not contain a query string or fragment")
        if parsed.scheme == "http":
            hostname = parsed.hostname.lower().rstrip(".")
            loopback = hostname == "localhost" or hostname.endswith(".localhost")
            try:
                loopback = loopback or ipaddress.ip_address(hostname).is_loopback
            except ValueError:
                pass
            if not loopback:
                raise ValueError("HTTP model endpoints are allowed only on loopback; use HTTPS for remote endpoints")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 1 <= timeout <= 300:
            raise ValueError("timeout must be between 1 and 300 seconds")
        if not self.model:
            raise ValueError("Set GRAVION_MODEL to the model identifier supported by your endpoint")
        if not isinstance(self.api_key, str):
            raise ValueError("API key must be a string")

    def complete(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string")
        payload = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Gravion-Trainner/0.4.3"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=payload, headers=headers, method="POST"
        )
        opener = urllib.request.build_opener(_NoRedirect())
        try:
            with opener.open(request, timeout=self.timeout) as response:
                data = response.read(MAX_RESPONSE_BYTES + 1)
            if len(data) > MAX_RESPONSE_BYTES:
                raise RuntimeError("Model endpoint response exceeded the 10 MiB safety limit")
            body = json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Model endpoint returned HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RuntimeError(f"Model endpoint request failed: {exc.__class__.__name__}") from exc

        try:
            content = body["choices"][0]["message"]["content"]
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = [part["text"] for part in content if isinstance(part, dict)
                         and part.get("type") == "text" and isinstance(part.get("text"), str)]
                return "".join(parts)
            raise TypeError("message content is not text")
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Endpoint returned an unexpected chat-completions response") from exc


def evaluate(cases: list[EvalCase], client: OpenAICompatibleClient) -> dict[str, Any]:
    if not cases:
        raise ValueError("At least one evaluation case is required")
    results = []
    for case in cases:
        output = client.complete(case.prompt)
        scored = score_output(output, case.expected_contains)
        results.append({"id": case.case_id, **scored, "output": output})
    average = sum(item["score"] for item in results) / len(results)
    return {
        "model": client.model,
        "case_count": len(results),
        "average_score": round(average, 4),
        "results": results,
        "notice": "Heuristic keyword coverage is not a complete measure of correctness, reasoning, safety or human-like understanding.",
    }
