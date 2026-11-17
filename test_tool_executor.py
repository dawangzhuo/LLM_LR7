import unittest
from unittest.mock import Mock, patch

from tool_executor import execute_tool


class ToolExecutorTests(unittest.TestCase):
    def setUp(self):
        self.runtime = Mock()
        self.env = object()

    def test_valid_arguments_reach_runtime(self):
        self.runtime.run_function.return_value = ("available", None)

        with patch("tool_executor.tool_result_to_str", return_value="available"):
            outcome = execute_tool(
                self.runtime, self.env, "get_book_status", '{"book_id": "B123"}'
            )

        self.runtime.run_function.assert_called_once_with(
            self.env, "get_book_status", {"book_id": "B123"}
        )
        self.assertEqual(outcome.text, "available")
        self.assertIsNone(outcome.error)

    def test_invalid_arguments_do_not_reach_runtime(self):
        for arguments in ("{", '["B123"]'):
            with self.subTest(arguments=arguments):
                outcome = execute_tool(
                    self.runtime, self.env, "get_book_status", arguments
                )
                self.assertIsNotNone(outcome.error)

        self.runtime.run_function.assert_not_called()

    def test_runtime_errors_are_returned_as_text(self):
        cases = [
            ("unknown_tool", "{}", "Unknown tool"),
            ("get_book_status", "{}", "book_id: Field required"),
        ]

        for name, arguments, expected_error in cases:
            with self.subTest(tool=name):
                self.runtime.run_function.return_value = (None, expected_error)
                outcome = execute_tool(self.runtime, self.env, name, arguments)
                self.assertEqual(outcome.text, expected_error)
                self.assertEqual(outcome.error, expected_error)


if __name__ == "__main__":
    unittest.main()