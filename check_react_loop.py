from agentdojo.functions_runtime import FunctionsRuntime
from agentdojo.task_suite.load_suites import get_suites

from react_loop import run_react


suite = get_suites("v1.2.2")["workspace"]


def tool_reply(call_id, name, arguments="{}"):
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": call_id,
            "type": "function",
            "function": {"name": name, "arguments": arguments},
        }],
    }


def recover_after_error(messages):
    last_message = messages[-1]
    if last_message["role"] == "user":
        return tool_reply("call_1", "lr4_nonexistent_tool")
    if last_message["tool_call_id"] == "call_1":
        assert "ToolNotFoundError" in last_message["content"]
        return tool_reply(
            "call_2", "search_files_by_filename", '{"filename": "example.txt"}'
        )
    assert last_message["tool_call_id"] == "call_2"
    return {"role": "assistant", "content": "The file search has finished."}


def repeat_tool(messages):
    call_number = sum(message["role"] == "tool" for message in messages) + 1
    return tool_reply(f"call_{call_number}", "lr4_nonexistent_tool")


def run_check(reply):
    runtime = FunctionsRuntime(suite.tools)
    env = suite.load_and_inject_default_environment({})
    return run_react("Run the scripted check.", runtime, env, reply)


recovery = run_check(recover_after_error)
assert recovery["stop_reason"] == "answered"
assert recovery["model_calls"] == 3
assert recovery["tool_attempts"] == 2
print("Continue after runtime error: PASS (2 tool attempts)")

limited = run_check(repeat_tool)
assert limited["stop_reason"] == "max_tools"
assert limited["tool_attempts"] == 15
assert limited["model_calls"] == 15
assert limited["messages"][-1]["role"] == "assistant"
assert limited["messages"][-1]["content"]
print("Stop at tool limit: PASS (max_tools, 15 attempts)")
print("Final assistant text: PASS")