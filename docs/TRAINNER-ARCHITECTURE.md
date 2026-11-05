# Gravion Trainner — evaluation and improvement architecture

## Goal

Turn model improvement into a repeatable engineering loop. The system evaluates a candidate, finds failure patterns, proposes controlled changes and checks whether the result beats a baseline without unacceptable safety or capability regressions.

## Pipeline

```text
Versioned dataset
      |
      v
Model adapter (OpenAI-compatible endpoint)
      |
      v
Run prompts and collect responses
      |
      v
Scoring / rubric graders / safety checks
      |
      v
Failure clustering and diagnosis
      |
      v
Candidate change (prompt, retrieval, tool schema, supported fine-tune)
      |
      v
Fixed holdout + regression suite
      |
      +---- reject / rollback if regression
      |
      +---- promote candidate after review
```

## What the current starter does
- Reads JSONL examples from `data/sample.jsonl`.
- Calls a configured OpenAI-compatible chat completion endpoint.
- Scores responses with the included simple evaluator.
- Writes a JSON report for inspection.

## What it does not do
- It does not edit arbitrary model weights, retrain closed models or make a model conscious.
- It does not automatically send data to a third-party provider unless a remote endpoint is configured.
- It does not prove model quality from one score or one dataset.

## Future modules
1. Dataset versioning, deduplication and data-rights metadata.
2. Multiple graders: deterministic checks, rubric-based judge and human review.
3. Model/prompt registry with reproducible run metadata.
4. Error taxonomy and clustered diagnosis.
5. Prompt and retrieval optimization experiments.
6. Supported fine-tuning/adapter integration with explicit opt-in.
7. Fixed holdout, safety regression tests and rollback/promotion gates.

## Evaluation metrics
Use task-specific metrics: exact match/structured validity when applicable, rubric score, factual support/citation quality, tool-call success, latency, token cost and safety regression rate. Report sample size and uncertainty. A higher aggregate score must not hide a critical safety failure.
