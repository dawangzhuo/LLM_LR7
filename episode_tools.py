from dataclasses import dataclass

from tool_executor import ToolOutcome, execute_tool


@dataclass
class EpisodeTools:
    max_tools: int = 15
    attempts: int = 0

    @property
    def exhausted(self) -> bool:
        return self.attempts >= self.max_tools

    def call(
        self, runtime, env, name, arguments_json, *, planned_tool=None
    ) -> ToolOutcome:
        if self.exhausted:
            return ToolOutcome(text="Tool call limit reached.", error="max_tools")

        # 每次尝试都计数，包括参数错误和工具名不符。
        self.attempts += 1

        if planned_tool is not None and name != planned_tool:
            error = f"Expected planned tool '{planned_tool}', received '{name}'."
            return ToolOutcome(text=error, error=error)

        return execute_tool(runtime, env, name, arguments_json)