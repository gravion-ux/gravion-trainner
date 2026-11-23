"""Scoring and report-generation coverage.

The cases in test_evaluator.py cover the happy paths of score_output and
evaluate plus the loader's structural validation. This module pins down the
scoring arithmetic (fractions, rounding, casing), the exact shape of the
report dictionary that evaluate returns, and the per-case detail the CLI
writes into its JSON report file.
"""
import json
import os
import sys
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from gravion_trainner.evaluator import EvalCase, evaluate, load_dataset, score_output
from gravion_trainner.cli import main as trainner_main


class ScriptedClient:
    """Fake model client that answers from a prompt -> output mapping."""

    model = "scripted-model"

    def __init__(self, answers):
        self.answers = answers
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return self.answers[prompt]


class ScoreOutputEdgeCaseTests(unittest.TestCase):
    def test_full_match_scores_one_with_nothing_missing(self):
        result = score_output("Encryption and authentication.", ["encryption", "authentication"])
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["matched"], ["encryption", "authentication"])
        self.assertEqual(result["missing"], [])

    def test_no_match_scores_zero_with_everything_missing(self):
        result = score_output("Completely unrelated answer.", ["encryption", "authentication"])
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["matched"], [])
        self.assertEqual(result["missing"], ["encryption", "authentication"])

    def test_fractional_score_is_rounded_to_four_places(self):
        result = score_output("only alpha is here", ["alpha", "beta", "gamma"])
        self.assertEqual(result["score"], 0.3333)

    def test_matched_and_missing_keep_the_dataset_phrase_casing_and_order(self):
        result = score_output("dns resolves an ip address", ["DNS", "Ip Address", "TLS"])
        self.assertEqual(result["matched"], ["DNS", "Ip Address"])
        self.assertEqual(result["missing"], ["TLS"])

    def test_matching_is_a_substring_check_not_a_word_check(self):
        # The scorer is a documented heuristic: a phrase counts as covered
        # when it appears anywhere in the output, even inside a longer word.
        result = score_output("concatenate the values", ["cat"])
        self.assertEqual(result["score"], 1.0)

    def test_rejects_non_string_output(self):
        with self.assertRaisesRegex(ValueError, "must be a string"):
            score_output(None, ["ok"])

    def test_rejects_blank_phrase(self):
        with self.assertRaisesRegex(ValueError, "non-empty strings"):
            score_output("any text", ["ok", "  "])

    def test_rejects_non_string_phrase(self):
        with self.assertRaisesRegex(ValueError, "non-empty strings"):
            score_output("any text", ["ok", 42])


class EvaluateReportTests(unittest.TestCase):
    def test_average_is_the_mean_of_the_case_scores(self):
        cases = [
            EvalCase("full", "p1", ["alpha", "beta"]),
            EvalCase("half", "p2", ["alpha", "beta"]),
            EvalCase("none", "p3", ["alpha", "beta"]),
        ]
        client = ScriptedClient({"p1": "alpha beta", "p2": "alpha only", "p3": "neither"})
        report = evaluate(cases, client)
        self.assertEqual(report["case_count"], 3)
        self.assertEqual(report["average_score"], 0.5)
        self.assertEqual([item["score"] for item in report["results"]], [1.0, 0.5, 0.0])

    def test_average_score_is_rounded_to_four_places(self):
        cases = [EvalCase("a", "p1", ["x"]), EvalCase("b", "p2", ["x"]), EvalCase("c", "p3", ["x"])]
        client = ScriptedClient({"p1": "x", "p2": "y", "p3": "z"})
        report = evaluate(cases, client)
        self.assertEqual(report["average_score"], 0.3333)

    def test_report_shape_and_notice(self):
        client = ScriptedClient({"p": "alpha"})
        report = evaluate([EvalCase("only", "p", ["alpha"])], client)
        self.assertEqual(
            set(report), {"model", "case_count", "average_score", "results", "notice"}
        )
        self.assertEqual(report["model"], "scripted-model")
        self.assertEqual(
            report["notice"],
            "Heuristic keyword coverage is not a complete measure of correctness, "
            "reasoning, safety or human-like understanding.",
        )

    def test_each_result_carries_matched_missing_and_the_raw_output(self):
        client = ScriptedClient({"p": "alpha and nothing else"})
        report = evaluate([EvalCase("case-1", "p", ["alpha", "beta"])], client)
        (result,) = report["results"]
        self.assertEqual(set(result), {"id", "score", "matched", "missing", "output"})
        self.assertEqual(result["id"], "case-1")
        self.assertEqual(result["matched"], ["alpha"])
        self.assertEqual(result["missing"], ["beta"])
        self.assertEqual(result["output"], "alpha and nothing else")

    def test_the_client_receives_each_prompt_in_dataset_order(self):
        cases = [EvalCase("a", "first", ["x"]), EvalCase("b", "second", ["x"])]
        client = ScriptedClient({"first": "x", "second": "x"})
        evaluate(cases, client)
        self.assertEqual(client.prompts, ["first", "second"])


class DatasetScoringInputTests(unittest.TestCase):
    def _write(self, tmp, text):
        path = Path(tmp) / "d.jsonl"
        path.write_text(text, encoding="utf-8")
        return path

    def test_loaded_case_keeps_id_prompt_and_expected_phrases(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                tmp, json.dumps({"id": "c1", "prompt": "Explain X", "expected_contains": ["Alpha"]}) + "\n"
            )
            (case,) = load_dataset(path)
            self.assertEqual(case.case_id, "c1")
            self.assertEqual(case.prompt, "Explain X")
            self.assertEqual(case.expected_contains, ["Alpha"])

    def test_comment_and_blank_lines_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = json.dumps({"id": "a", "prompt": "p", "expected_contains": ["ok"]})
            path = self._write(tmp, "# a comment line\n\n" + row + "\n")
            self.assertEqual([case.case_id for case in load_dataset(path)], ["a"])

    def test_rejects_case_insensitive_duplicate_expected_phrases(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = json.dumps({"id": "a", "prompt": "p", "expected_contains": ["DNS", "dns"]})
            path = self._write(tmp, row + "\n")
            with self.assertRaisesRegex(ValueError, "duplicate phrases"):
                load_dataset(path)

    def test_rejects_a_case_without_expected_contains(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = json.dumps({"id": "a", "prompt": "p"})
            path = self._write(tmp, row + "\n")
            with self.assertRaisesRegex(ValueError, "non-empty list"):
                load_dataset(path)


class CliReportFileTests(unittest.TestCase):
    """The JSON file the CLI writes is the report users actually consume."""

    def setUp(self):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                body = {"choices": [{"message": {"content": "alpha only"}}]}
                payload = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}/v1"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_written_report_contains_per_case_scoring_detail(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "d.jsonl"
            dataset.write_text(
                json.dumps({"id": "c1", "prompt": "p", "expected_contains": ["alpha", "beta"]}) + "\n"
            )
            output = Path(tmp) / "nested" / "report.json"
            environ = {"GRAVION_BASE_URL": self.base, "GRAVION_MODEL": "cli-model", "GRAVION_API_KEY": ""}
            argv = ["evaluate", "--dataset", str(dataset), "--output", str(output)]
            with patch.dict(os.environ, environ, clear=False):
                self.assertEqual(trainner_main(argv), 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["average_score"], 0.5)
            (result,) = report["results"]
            self.assertEqual(result["matched"], ["alpha"])
            self.assertEqual(result["missing"], ["beta"])
            self.assertEqual(result["output"], "alpha only")
            self.assertIn("notice", report)


if __name__ == "__main__":
    unittest.main()
