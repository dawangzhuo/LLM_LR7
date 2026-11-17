import mlflow
import argparse
import json
from datetime import datetime
from pathlib import Path
from time import perf_counter

from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
from agentdojo.functions_runtime import FunctionCall
from agentdojo.task_suite.load_suites import get_suites
from agentdojo.types import (
    ChatAssistantMessage,
    ChatToolResultMessage,
    ChatUserMessage,
    text_content_block_from_string as text,
)

from model_client import ModelClient
from react_loop import run_react


ROOT = Path(__file__).resolve().parent

def log_episode_to_mlflow(record, trace_path):
    # 使用 LR4 项目里的数据库，与之前手动验证使用的是同一个文件。
    database_path = (ROOT / "mlflow.db").as_posix()
    mlflow.set_tracking_uri(f"sqlite:///{database_path}")
    mlflow.set_experiment(f"LR4_{record['split'].capitalize()}")
    episode = record["episode"]
    with mlflow.start_run(run_name=trace_path.stem) as run:
        mlflow.log_params({
            "task_id": record["task_id"],
            "mode": record["mode"],
            "split": record["split"],
            "model_id": record["model_id"],
            "stop_reason": episode["stop_reason"],
            "trace_filename": trace_path.name,
        })
        mlflow.log_metrics({
            "utility": int(record["utility"]),
            "model_calls": episode["model_calls"],
            "tool_attempts": episode["tool_attempts"],
            "elapsed_seconds": record["elapsed_seconds"],
        })
        mlflow.log_artifact(str(trace_path), artifact_path="traces")
        return run.info.run_id

def scoring_messages(messages):
    """把回合历史转换成 AgentDojo 评分所用的消息。"""
    history = []
    calls_by_id = {}

    for message in messages:
        role = message["role"]

        if role == "user":
            history.append(
                ChatUserMessage(role="user", content=[text(message["content"])])
            )

        elif role == "assistant":
            calls = []
            for item in message.get("tool_calls") or []:
                function = item["function"]

                try:
                    args = json.loads(function["arguments"])
                except json.JSONDecodeError:
                    args = {}

                call = FunctionCall(
                    function=function["name"],
                    args=args if isinstance(args, dict) else {},
                    id=item["id"],
                )
                calls.append(call)
                calls_by_id[item["id"]] = call

            content = message.get("content")
            history.append(
                ChatAssistantMessage(
                    role="assistant",
                    content=[text(content)] if content else None,
                    tool_calls=calls or None,
                )
            )

        elif role == "tool":
            call_id = message["tool_call_id"]
            history.append(
                ChatToolResultMessage(
                    role="tool",
                    content=[text(message["content"])],
                    tool_call_id=call_id,
                    tool_call=calls_by_id[call_id],
                    error=message.get("error"),
                )
            )

    return history


class LiveReact(BasePipelineElement):
    def __init__(self, client, system_prompt):
        self.name = "local-react"
        self.client = client
        self.system_prompt = system_prompt
        self.model_trace = []
        self.episode = None

    def query(self, query, runtime, env, messages=(), extra_args=None):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters.model_json_schema(),
                },
            }
            for tool in runtime.functions.values()
        ]

        def reply(history):
            api_history = [
                {key: value for key, value in message.items() if key != "error"}
                for message in history
            ]
            return self.client.complete(
                [{"role": "system", "content": self.system_prompt}, *api_history],
                self.model_trace,
                tools=tools,
                tool_choice="auto",
            )

        self.episode = run_react(query, runtime, env, reply)
        history = scoring_messages(self.episode["messages"])
        return query, runtime, env, history, extra_args or {}


def main(agent_class=LiveReact, mode="react"):
    manifest_path = ROOT / "data" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("debug", "final"), default="debug")
    parser.add_argument("--task-id", help="AgentDojo task ID")
    args = parser.parse_args()

    split = args.split
    task_ids = manifest[f"{split}_task_ids"]
    if args.task_id is None and split == "final":
        parser.error("--split final requires --task-id")

    task_id = args.task_id if args.task_id is not None else task_ids[0]
    if task_id not in task_ids:
        parser.error(f"{task_id} is not in the {split} split")

    suite = get_suites(manifest["benchmark_version"])[manifest["suite"]]
    task = suite.get_user_task_by_id(task_id)

    prompt_path = ROOT / "prompts" / "react_system.txt"
    prompt = prompt_path.read_text(encoding="utf-8-sig")
    agent = agent_class(ModelClient(), prompt)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output = ROOT / "results" / f"{mode}_live_{task_id}_{stamp}.json"
    output.parent.mkdir(exist_ok=True)

    utility = None
    run_error = None
    started = perf_counter()

    try:
        utility, _ = suite.run_task_with_pipeline(agent, task, None, {})
    except Exception as exc:
        run_error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        record = {
            "task_id": task_id,
            "split": split,
            "mode": mode,
            "model_id": agent.client.model_id,
            "utility": utility,
            "run_error": run_error,
            "elapsed_seconds": round(perf_counter() - started, 6),
            "episode": agent.episode,
            "model_trace": agent.model_trace,
        }
        output.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Trace saved to: {output}")
    if isinstance(utility, bool) and agent.episode is not None:
        run_id = log_episode_to_mlflow(record, output)
        print(f"MLflow run ID: {run_id}")
    print(f"{split.capitalize()} task: {task_id}")
    print(f"AgentDojo utility: {utility}")
    print(f"Stop reason: {agent.episode['stop_reason']}")
    print(f"Model calls: {agent.episode['model_calls']}")
    print(f"Tool attempts: {agent.episode['tool_attempts']}")


if __name__ == "__main__":
    main()