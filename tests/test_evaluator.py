import json
import os
import socket
import sys
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from gravion_trainner.evaluator import EvalCase, OpenAICompatibleClient, load_dataset, score_output, evaluate
from gravion_trainner.cli import main as trainner_main

class FakeClient:
    model = "fake-model"
    def complete(self, prompt): return "TLS provides encryption and authentication."

class TrainnerTests(unittest.TestCase):
    def test_scores_case_insensitive_contains(self):
        result = score_output("IP ADDRESS resolution", ["ip address", "DNS"])
        self.assertEqual(result["score"], 0.5)
    def test_loads_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "d.jsonl"
            path.write_text(json.dumps({"id":"a","prompt":"p","expected_contains":["ok"]}) + "\n")
            self.assertEqual(load_dataset(path)[0].case_id, "a")
    def test_rejects_empty_dataset(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"d.jsonl"; path.write_text("\n")
            with self.assertRaises(ValueError): load_dataset(path)
    def test_evaluate_fake_client(self):
        report=evaluate([EvalCase("tls", "explain", ["encryption", "authentication"])], FakeClient())
        self.assertEqual(report["average_score"], 1.0)
    def test_missing_dataset_has_actionable_error(self):
        with self.assertRaisesRegex(ValueError, "Cannot read dataset"):
            load_dataset("/path/that/does/not/exist.jsonl")
    def test_rejects_non_object_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"d.jsonl"; path.write_text('[1, 2]\n')
            with self.assertRaisesRegex(ValueError, "JSON object"):
                load_dataset(path)
    def test_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"d.jsonl"
            row=json.dumps({"id":"x","prompt":"p","expected_contains":["ok"]})
            path.write_text(row+"\n"+row+"\n")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_dataset(path)
    def test_missing_is_case_insensitive(self):
        result=score_output("IP ADDRESS", ["ip address", "Ip Address", "DNS"])
        self.assertEqual(result["missing"], ["DNS"])
    def test_rejects_invalid_base_url(self):
        with self.assertRaisesRegex(ValueError, r"HTTP\(S\)"):
            OpenAICompatibleClient(base_url="file:///etc/passwd", model="test")

class ModelEndpointIntegrationTests(unittest.TestCase):
    def setUp(self):
        class Handler(BaseHTTPRequestHandler):
            status = 200
            response_body = {"choices": [{"message": {"content": "local endpoint response"}}]}
            redirect_to = None
            def do_POST(self):
                # Drain the request body before responding. Closing the connection with
                # unread body bytes makes Windows reset the socket, which surfaces as a
                # ConnectionAbortedError in the client instead of the real response.
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                if self.redirect_to:
                    self.send_response(302); self.send_header("Location", self.redirect_to)
                    self.send_header("Content-Length", "0"); self.end_headers(); return
                self.send_response(self.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(json.dumps(self.response_body))))
                self.end_headers()
                self.wfile.write(json.dumps(self.response_body).encode())
            def log_message(self, *args): pass
        self.handler = Handler
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}/v1"
    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=2)
    def test_real_local_http_chat_completions_round_trip(self):
        client = OpenAICompatibleClient(base_url=self.base, model="test-model")
        self.assertEqual(client.complete("hello"), "local endpoint response")
    def test_openai_multimodal_text_parts_are_joined(self):
        self.handler.response_body = {"choices": [{"message": {"content": [{"type": "text", "text": "one"}, {"type": "image", "image": "x"}, {"type": "text", "text": "two"}]}}]}
        client = OpenAICompatibleClient(base_url=self.base, model="test-model")
        self.assertEqual(client.complete("hello"), "onetwo")
    def test_http_error_is_reported_without_body_leak(self):
        self.handler.status = 401
        client = OpenAICompatibleClient(base_url=self.base, model="test-model")
        with self.assertRaisesRegex(RuntimeError, "HTTP 401"):
            client.complete("hello")
    def test_redirects_are_not_followed(self):
        self.handler.redirect_to = "http://127.0.0.1:1/steal"
        client = OpenAICompatibleClient(base_url=self.base, model="test-model", api_key="do-not-forward")
        with self.assertRaisesRegex(RuntimeError, "HTTP 302"):
            client.complete("hello")

    def test_cli_evaluates_sample_dataset_and_writes_report(self):
        self.handler.response_body = {"choices": [{"message": {"content": "TLS provides encryption and authentication. DNS maps a domain name to an IP address. A 404 means not found."}}]}
        repo_root = Path(__file__).parents[1]
        dataset = repo_root / "data" / "sample.jsonl"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            environ = {
                "GRAVION_BASE_URL": self.base,
                "GRAVION_MODEL": "mock-model",
                "GRAVION_API_KEY": "",
            }
            argv = ["gravion-trainner", "evaluate", "--dataset", str(dataset), "--output", str(output)]
            with patch.dict(os.environ, environ, clear=False), patch("sys.argv", argv):
                self.assertEqual(trainner_main(), 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["case_count"], 3)
            self.assertEqual(report["average_score"], 1.0)
            self.assertEqual(report["model"], "mock-model")

class TrainnerValidationTests(unittest.TestCase):
    def test_rejects_empty_expected_phrase_list(self):
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            score_output("any text", [])
    def test_rejects_empty_evaluation_list(self):
        with self.assertRaisesRegex(ValueError, "At least one"):
            evaluate([], FakeClient())
    def test_rejects_remote_plain_http_endpoint(self):
        with self.assertRaisesRegex(ValueError, "HTTPS for remote"):
            OpenAICompatibleClient(base_url="http://api.example.com/v1", model="test")
    def test_allows_loopback_plain_http_endpoint(self):
        client = OpenAICompatibleClient(base_url="http://localhost:11434/v1", model="local-model")
        self.assertEqual(client.model, "local-model")
    def test_rejects_query_string_and_fragment(self):
        with self.assertRaisesRegex(ValueError, "query string or fragment"):
            OpenAICompatibleClient(base_url="https://api.example.com/v1?token=x", model="test")
    def test_rejects_empty_expected_phrase_in_dataset(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.jsonl"
            path.write_text(json.dumps({"id": "x", "prompt": "p", "expected_contains": [""]}) + "\n")
            with self.assertRaisesRegex(ValueError, "non-empty strings"):
                load_dataset(path)


class MalformedEndpointTests(unittest.TestCase):
    """A malformed HTTP response must surface as a clean RuntimeError, not a raw traceback."""

    @staticmethod
    def _serve_once(payload):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def run():
            try:
                conn, _ = server.accept()
            except OSError:
                return
            try:
                conn.settimeout(2)
                try:
                    conn.recv(65536)
                except OSError:
                    pass
                conn.sendall(payload)
            except OSError:
                pass
            finally:
                conn.close()

        thread = Thread(target=run, daemon=True)
        thread.start()
        return server, port, thread

    def test_malformed_status_line_raises_runtime_error(self):
        server, port, thread = self._serve_once(b"NOT-HTTP GARBAGE\r\n\r\n")
        try:
            client = OpenAICompatibleClient(base_url=f"http://127.0.0.1:{port}/v1", model="test-model", timeout=5)
            with self.assertRaisesRegex(RuntimeError, "Model endpoint request failed"):
                client.complete("hello")
        finally:
            server.close()
            thread.join(timeout=2)

    def test_cli_reports_a_malformed_endpoint_without_a_traceback(self):
        server, port, thread = self._serve_once(b"NOT-HTTP GARBAGE\r\n\r\n")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                dataset = Path(tmp) / "d.jsonl"
                dataset.write_text(json.dumps({"id": "x", "prompt": "p", "expected_contains": ["ok"]}) + "\n")
                output = Path(tmp) / "report.json"
                environ = {
                    "GRAVION_BASE_URL": f"http://127.0.0.1:{port}/v1",
                    "GRAVION_MODEL": "mock-model",
                    "GRAVION_API_KEY": "",
                }
                argv = ["gravion-trainner", "evaluate", "--dataset", str(dataset), "--output", str(output)]
                with patch.dict(os.environ, environ, clear=False), patch("sys.argv", argv):
                    self.assertEqual(trainner_main(), 2)
        finally:
            server.close()
            thread.join(timeout=2)

    def test_loads_dataset_with_utf8_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "d.jsonl"
            row = json.dumps({"id": "a", "prompt": "p", "expected_contains": ["ok"]}) + "\n"
            path.write_bytes(b"\xef\xbb\xbf" + row.encode("utf-8"))
            self.assertEqual(load_dataset(path)[0].case_id, "a")


if __name__ == "__main__": unittest.main()

