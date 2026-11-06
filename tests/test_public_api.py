import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
import gravion_trainner


class GravionTrainnerPublicApiTests(unittest.TestCase):
    def test_the_package_exposes_a_version(self):
        self.assertTrue(gravion_trainner.__version__)

    def test_the_package_exposes_the_public_api(self):
        for name in ("load_dataset", "evaluate", "score_output", "OpenAICompatibleClient", "EvalCase"):
            self.assertIn(name, gravion_trainner.__all__)
            self.assertTrue(hasattr(gravion_trainner, name))

    def test_the_exported_functions_are_the_evaluator_module_functions(self):
        from gravion_trainner.evaluator import (
            EvalCase,
            OpenAICompatibleClient,
            evaluate,
            load_dataset,
            score_output,
        )
        self.assertIs(gravion_trainner.load_dataset, load_dataset)
        self.assertIs(gravion_trainner.evaluate, evaluate)
        self.assertIs(gravion_trainner.score_output, score_output)
        self.assertIs(gravion_trainner.OpenAICompatibleClient, OpenAICompatibleClient)
        self.assertIs(gravion_trainner.EvalCase, EvalCase)


class GravionTrainnerCliTests(unittest.TestCase):
    def test_the_command_can_be_called_with_an_argument_list(self):
        from gravion_trainner.cli import main
        import inspect
        signature = inspect.signature(main)
        self.assertIn("argv", signature.parameters)
        self.assertIsNone(signature.parameters["argv"].default)
