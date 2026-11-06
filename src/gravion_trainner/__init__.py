"""Gravion Trainner evaluation toolkit.

Public API
----------
``load_dataset``              parse and validate a JSONL evaluation dataset
``evaluate``                  run the cases against a model client
``score_output``              score one model output
``OpenAICompatibleClient``    the OpenAI-compatible HTTP client
"""
from .evaluator import (
    EvalCase,
    OpenAICompatibleClient,
    evaluate,
    load_dataset,
    score_output,
)

__all__ = [
    "EvalCase",
    "OpenAICompatibleClient",
    "__version__",
    "evaluate",
    "load_dataset",
    "score_output",
]

__version__ = "0.1.0"
