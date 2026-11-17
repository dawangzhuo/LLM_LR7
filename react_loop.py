from model_client import ContextLimitError
from episode_tools import EpisodeTools


def run_react(query, runtime, env, reply, *, max_calls=15, max_tools=15):
    """reply 接收消息历史，返回一条 OpenAI 格式的助手消息。"""
    messages = [{"role": "user", "content": query}]
    tools = EpisodeTools(max_tools=max_tools)

    def finish(reason, text, model_calls):
        messages.append({"role": "assistant", "content": text})
        return {
            "stop_reason": reason,
            "model_calls": model_calls,
            "tool_attempts": tools.attempts,
            "messages": messages,
        }

    for model_calls in range(1, max_calls + 1):
        try:
            message = reply(messages)
        except ContextLimitError:
            return finish(
                "context_limit",
                "Stopped because the request exceeded the model context.",
                model_calls,
            )

        calls = message.get("tool_calls") or []
        if not calls:
            text = (message.get("content") or "").strip()
            if not text:
                return finish("empty_answer", "The model returned an empty answer.", model_calls)
            return finish("answered", text, model_calls)

        # 只把本回合剩余预算内的工具调用写入消息历史。
        remaining = tools.max_tools - tools.attempts
        accepted_calls = calls[:remaining]
        messages.append({
            "role": "assistant",
            "content": message.get("content"),
            "tool_calls": accepted_calls,
        })

        for call in accepted_calls:
            function = call["function"]
            outcome = tools.call(
                runtime, env, function["name"], function["arguments"]
            )
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": outcome.text,
                "error": outcome.error,
            })
#把工作结果写入messge
        if tools.exhausted:
            return finish("max_tools", "Stopped after reaching the tool call limit.", model_calls)

    return finish("max_calls", "Stopped after reaching the model call limit.", max_calls)