import json
from dataclasses import dataclass

from agentdojo.agent_pipeline.tool_execution import tool_result_to_str


@dataclass(frozen=True)
class ToolOutcome:
    text: str
    error: str | None = None


def execute_tool(runtime, env, name: str, arguments_json: str) -> ToolOutcome:
    # 模型返回的 arguments 是 JSON 字符串，先转换为字典。
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError as exc:
        error = f"Invalid JSON arguments: {exc.msg}"
        return ToolOutcome(text=error, error=error)

    if not isinstance(arguments, dict):
        error = "Tool arguments must be a JSON object."
        return ToolOutcome(text=error, error=error)

    # AgentDojo 检查工具名称和参数，并返回结果或错误。
    result, error = runtime.run_function(env, name, arguments)
    if error is not None:
        return ToolOutcome(text=error, error=error)

    return ToolOutcome(text=tool_result_to_str(result))