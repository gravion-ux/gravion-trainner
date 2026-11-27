import json
import tempfile
import unittest
from pathlib import Path
from gravion_trainner.evaluator import load_dataset


class DatasetEdgesTest(unittest.TestCase):
    def test_whitespace_variant_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "data.jsonl"
            rows = [
                {"id": "a", "prompt": "p", "expected_contains": ["x"]},
                {"id": " a ", "prompt": "p", "expected_contains": ["x"]},
            ]
            path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_dataset(path)
