<p align="center"><img src="assets/banner.svg" alt="gravion-trainner banner" width="100%"/></p>

# Gravion Trainner v0.1.0

[![CI](https://github.com/gravion-ux/gravion-trainner/actions/workflows/ci.yml/badge.svg)](https://github.com/gravion-ux/gravion-trainner/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Model quality evaluation starter for OpenAI-compatible chat-completions endpoints (including compatible local runtimes).**

## Run a test

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
GRAVION_BASE_URL=http://localhost:11434/v1 \
GRAVION_MODEL=your-local-model \
python -m gravion_trainner.cli evaluate --dataset data/sample.jsonl --output reports/report.json
```

For a hosted provider, use its documented base URL and set the API credential in `GRAVION_API_KEY` or `OPENAI_API_KEY`. Do not put keys in source files or commit `.env`.

### Endpoint configuration

The client is configured through flags or environment variables:

| Setting | Flag | Environment variable | Default |
|---|---|---|---|
| Base URL | `--base-url` | `GRAVION_BASE_URL` | `https://api.openai.com/v1` |
| Model | `--model` | `GRAVION_MODEL` | none — a model identifier is required |
| API key | — | `GRAVION_API_KEY`, falling back to `OPENAI_API_KEY` | empty (no `Authorization` header is sent) |

Requests are sent to `<base URL>/chat/completions` with `temperature: 0`. Two safety rules are enforced before any request is made: plain HTTP endpoints are accepted only on loopback addresses (remote endpoints must use HTTPS), and redirects are never followed, so an API key is never forwarded to a redirected destination.

## Dataset format

A dataset is a UTF-8 JSON Lines file (a leading byte-order mark is tolerated): one JSON object per line, with blank lines and lines starting with `#` skipped. Each object describes one evaluation case:

```json
{"id":"explain-tls","prompt":"In two short sentences, explain what TLS does for a website connection.","expected_contains":["encryption","authentication"]}
```

| Field | Requirement |
|---|---|
| `id` | Non-empty string, unique within the dataset |
| `prompt` | Non-empty string, sent to the model as the user message |
| `expected_contains` | Non-empty list of non-empty strings; duplicates are rejected, ignoring case |

Loading fails with an error naming the offending line when a line is not valid JSON, is not a JSON object, repeats an `id`, or breaks the field rules above. Size limits are also enforced: the file may be at most 5 MiB, each line at most 1 MiB, and a dataset may hold at most 10,000 cases; a file with no cases at all is an error. The bundled `data/sample.jsonl` ships three cases (TLS, DNS and HTTP 404) and is what the example report below was produced from.

## How scoring works

Scoring is a deliberately simple heuristic, implemented by `score_output` in `src/gravion_trainner/evaluator.py`:

1. The model's response and every expected phrase are case-folded.
2. A phrase counts as **matched** when it appears anywhere in the response as a substring — this is a coverage check, not a word or semantic match.
3. The case score is `matched / total` expected phrases, rounded to four decimal places. The report lists `matched` and `missing` phrases in the dataset's original casing and order.

`evaluate` runs every case in dataset order and averages the case scores into `average_score` (also rounded to four decimal places). The CLI prints the result as a percentage (`average heuristic coverage: 83.3%`) and exits with status 0 on success or 2 on any dataset, configuration or endpoint error, with the reason written to stderr instead of a traceback.

## Example report

The report is a single JSON document with the model name, the case count, the average score, one entry per case (including the model's raw output) and a fixed notice about what the score does and does not mean. The example below is genuine output: it was produced by running the CLI on the bundled `data/sample.jsonl` against a local stub endpoint that returns fixed canned answers — which is why the model is named `stub-model`. The DNS case scores 0.5 because the stub's answer says "domain name" but never "IP address":

```json
{
  "model": "stub-model",
  "case_count": 3,
  "average_score": 0.8333,
  "results": [
    {
      "id": "explain-tls",
      "score": 1.0,
      "matched": [
        "encryption",
        "authentication"
      ],
      "missing": [],
      "output": "TLS provides encryption and authentication for a website connection."
    },
    {
      "id": "explain-dns",
      "score": 0.5,
      "matched": [
        "domain name"
      ],
      "missing": [
        "IP address"
      ],
      "output": "DNS translates a domain name into a numeric address that computers use."
    },
    {
      "id": "explain-http",
      "score": 1.0,
      "matched": [
        "not found"
      ],
      "missing": [],
      "output": "An HTTP 404 status code means the requested resource was not found."
    }
  ],
  "notice": "Heuristic keyword coverage is not a complete measure of correctness, reasoning, safety or human-like understanding."
}
```

## What it measures

This starter checks whether each model response includes expected phrases and reports heuristic keyword coverage. This is useful as a smoke test, not a general intelligence/reasoning score. Add rubric-based graders, factuality checks, human review, safety suites and fixed holdout datasets before using the result to promote a model.

## What it does not do

It does not retrain all AI models, edit closed model weights, guarantee improved reasoning, create human emotions or silently retain user conversations. Future optimization could tune prompts, retrieval, tool selection, routing or supported adapters/fine-tuning after explicit authorization and evaluation.

---

## Part of the Gravion Toolkit

This repository holds one project from the four-project Gravion Toolkit. The projects are independent and can be used separately.

| Project | Purpose | Repository |
|---|---|---|
| localshare | Share a local development server through Cloudflare Quick or Named Tunnels | https://github.com/gravion-ux/localshare/tree/main |
| privacyflow | Validate authorized VPN profiles and plan safe rotation workflows | https://github.com/gravion-ux/privacyflow/tree/main |
| agent-browser | Run permission-aware browser tasks on allow-listed domains | https://github.com/gravion-ux/agent-browser/tree/main |
| **This repository** | Evaluate AI models against a JSONL dataset and report quality | https://github.com/gravion-ux/gravion-trainner/tree/main |

The four projects are **development foundations and MVP scaffolds**, not production services. They do not provide anonymity guarantees, CAPTCHA or anti-bot bypass, universal model retraining, or a managed multi-tenant sharing relay. See [the shared security notes](docs/SECURITY.md), [the threat model](docs/THREAT-MODEL.md) and [the roadmap](docs/ROADMAP.md) for the boundaries and the planned work.
