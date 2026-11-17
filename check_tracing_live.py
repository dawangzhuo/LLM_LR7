import json
from datetime import datetime
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

import mlflow
from mlflow.entities import SpanType

from check_react_live import LiveReact, get_suites
from model_client import ModelClient
from tool_executor import execute_tool


ROOT = Path(__file__).resolve().parent


class TracedClient(ModelClient):
    def complete(self, messages, trace, *, tools=None, **options):
        with mlflow.start_span(
            name="chat",
            span_type=SpanType.CHAT_MODEL,
        ) as span:
            span.set_inputs({
                "messages": messages,
                "tools": tools,
                "temperature": 0,
                "seed": 42,
            })
            span.set_attribute("gen_ai.request.model", self.model_id)
            previous_count = len(trace)

            try:
                response = super().complete(
                    messages,
                    trace,
                    tools=tools,
                    **{**options, "temperature": 0, "seed": 42},
                )
                span.set_outputs(response)
                return response
            finally:
                if len(trace) > previous_count:
                    entry = trace[-1]
                    usage = entry.get("usage") or {}
                    span.set_attribute("usage", usage)

                    if isinstance(usage.get("prompt_tokens"), int):
                        span.set_attribute(
                            "gen_ai.usage.input_tokens",
                            usage["prompt_tokens"],
                        )
                    if isinstance(usage.get("completion_tokens"), int):
                        span.set_attribute(
                            "gen_ai.usage.output_tokens",
                            usage["completion_tokens"],
                        )

                    span.set_attribute(
                        "elapsed_seconds",
                        entry.get("elapsed_seconds"),
                    )
                    if entry.get("error"):
                        span.set_attribute("error", entry["error"])


def traced_execute_tool(runtime, env, name, arguments):
    with mlflow.start_span(
        name=name,
        span_type=SpanType.TOOL,
    ) as span:
        span.set_inputs({
            "tool_name": name,
            "arguments": arguments,
        })

        outcome = execute_tool(runtime, env, name, arguments)

        span.set_outputs({
            "text": outcome.text,
            "chars": len(outcome.text),
            "error": outcome.error,
        })
        span.set_attribute("tool_name", name)
        span.set_attribute("result_chars", len(outcome.text))
        span.set_attribute("tool_error", bool(outcome.error))
        return outcome


def main():
    manifest = json.loads(
        (ROOT / "data" / "manifest.json").read_text(
            encoding="utf-8-sig"
        )
    )
    task_id = manifest["debug_task_ids"][0]
    suite = get_suites(manifest["benchmark_version"])[manifest["suite"]]
    task = suite.get_user_task_by_id(task_id)

    prompt = (ROOT / "prompts" / "react_system.txt").read_text(
        encoding="utf-8-sig"
    )
    agent = LiveReact(TracedClient(), prompt)

    database = (ROOT / "mlflow.db").as_posix()
    mlflow.set_tracking_uri(f"sqlite:///{database}")
    experiment = mlflow.set_experiment("LR7_Debug")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output = ROOT / "results" / f"tracing_debug_{task_id}_{stamp}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    utility = None
    run_error = None
    trace_id = None
    started = perf_counter()

    try:
        with mlflow.start_span(
            name=f"episode {task_id}",
            span_type=SpanType.AGENT,
        ) as span:
            trace_id = span.trace_id
            span.set_inputs({
                "task_id": task_id,
                "query": task.PROMPT,
            })

            mlflow.update_current_trace(tags={
                "task": task_id,
                "version": "base_debug",
                "run": "1",
                "split": "debug",
            })

            try:
                with patch(
                    "episode_tools.execute_tool",
                    side_effect=traced_execute_tool,
                ):
                    utility, _ = suite.run_task_with_pipeline(
                        agent, task, None, {}
                    )
                span.set_outputs({
                    "utility": utility,
                    "stop_reason": agent.episode["stop_reason"],
                })
                mlflow.update_current_trace(
                    tags={"utility": str(utility)}
                )
            except Exception as exc:
                mlflow.update_current_trace(
                    tags={"evaluation_error": f"{type(exc).__name__}: {exc}"}
                )
                raise

    except Exception as exc:
        run_error = f"{type(exc).__name__}: {exc}"

    finally:
        record = {
            "task_id": task_id,
            "version": "base_debug",
            "run": 1,
            "temperature": 0,
            "seed": 42,
            "model_id": agent.client.model_id,
            "utility": utility,
            "run_error": run_error,
            "elapsed_seconds": round(perf_counter() - started, 6),
            "trace_id": trace_id,
            "experiment_id": experiment.experiment_id,
            "episode": agent.episode,
            "model_trace": agent.model_trace,
        }
        output.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Record saved to: {output}")

    # 等待异步追踪写入后，再读取这条追踪。
    mlflow.search_traces(
        experiment_ids=[experiment.experiment_id],
        max_results=1,
        flush=True,
    )

    if run_error:
        raise SystemExit(f"Tracing episode error: {run_error}")

    saved_trace = mlflow.get_trace(trace_id)
    if saved_trace is None:
        raise SystemExit(f"Trace was not found: {trace_id}")

    spans = saved_trace.data.spans
    model_spans = [
        span for span in spans
        if span.span_type == SpanType.CHAT_MODEL
    ]
    tool_spans = [
        span for span in spans
        if span.span_type == SpanType.TOOL
    ]

    print(f"Task: {task_id}")
    print(f"AgentDojo utility: {utility}")
    print(f"Stop reason: {agent.episode['stop_reason']}")
    print(f"Model calls in JSON: {len(agent.model_trace)}")
    print(f"Model spans in MLflow: {len(model_spans)}")
    print(f"Tool attempts in JSON: {agent.episode['tool_attempts']}")
    print(f"Tool spans in MLflow: {len(tool_spans)}")
    print(f"Trace ID: {trace_id}")

    if len(model_spans) != len(agent.model_trace):
        raise SystemExit("Model span count: FAIL")
    if len(tool_spans) != agent.episode["tool_attempts"]:
        raise SystemExit("Tool span count: FAIL")

    print("LR7 live tracing counts: PASS")


if __name__ == "__main__":
    main()