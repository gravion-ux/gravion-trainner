# Gravion Trainner v0.1.0

Model quality evaluation starter for OpenAI-compatible chat-completions endpoints (including compatible local runtimes).

## Run a test

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
GRAVION_BASE_URL=http://localhost:11434/v1 \
GRAVION_MODEL=your-local-model \
python -m gravion_trainner.cli evaluate --dataset data/sample.jsonl --output reports/report.json
```

For a hosted provider, use its documented base URL and set the API credential in `GRAVION_API_KEY` or `OPENAI_API_KEY`. Do not put keys in source files or commit `.env`.

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
