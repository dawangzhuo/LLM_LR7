import unittest
from unittest.mock import Mock

from episode_tools import EpisodeTools


class EpisodeToolsTests(unittest.TestCase):
    def test_failures_count_and_sixteenth_call_is_blocked(self):
        runtime = Mock()
        runtime.run_function.return_value = (None, "ToolNotFoundError")
        tools = EpisodeTools()
        env = object()

        for _ in range(15):
            outcome = tools.call(runtime, env, "unknown_tool", "{}")
            self.assertEqual(outcome.error, "ToolNotFoundError")

        self.assertTrue(tools.exhausted)
        outcome = tools.call(runtime, env, "unknown_tool", "{}")
        self.assertEqual(outcome.error, "max_tools")
        self.assertEqual(tools.attempts, 15)
        self.assertEqual(runtime.run_function.call_count, 15)

    def test_wrong_planned_tool_never_reaches_runtime(self):
        runtime = Mock()
        tools = EpisodeTools()

        outcome = tools.call(
            runtime,
            object(),
            "list_files",
            "{}",
            planned_tool="search_files_by_filename",
        )

        self.assertIn("Expected planned tool", outcome.text)
        self.assertEqual(tools.attempts, 1)
        runtime.run_function.assert_not_called()