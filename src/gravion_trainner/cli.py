from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from .evaluator import OpenAICompatibleClient, evaluate, load_dataset

def main() -> int:
    parser = argparse.ArgumentParser(prog="gravion-trainner", description="Evaluate a model against a versioned JSONL dataset")
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("evaluate"); cmd.add_argument("--dataset", required=True); cmd.add_argument("--output", required=True)
    cmd.add_argument("--base-url"); cmd.add_argument("--model")
    args = parser.parse_args()
    try:
        cases = load_dataset(args.dataset)
        client = OpenAICompatibleClient(base_url=args.base_url, model=args.model)
        report = evaluate(cases, client)
        output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Evaluated {report['case_count']} case(s); average heuristic coverage: {report['average_score']:.1%}")
        print(f"Report: {output}")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"gravion-trainner: {exc}", file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
