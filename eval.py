import os
import argparse
import hashlib
import json
import subprocess
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

import mlflow
from mlflow.entities import SpanType

from check_react_live import LiveReact, get_suites
from check_tracing_live import TracedClient, traced_execute_tool
from model_client import ModelClient


ROOT = Path(__file__).resolve().parent


class BaselineClient(ModelClient):
    def complete(self, messages, trace, *, tools=None, **options):
        return super().complete(
            messages,
            trace,
            tools=tools,
            **{**options, "temperature": 0, "seed": 42},
        )


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=["base"], required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--split", choices=["debug", "final"], default="final")
    parser.add_argument("--task-id")
    parser.add_argument("--no-tracing", action="store_true")
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be positive")

    benchmark = json.loads(
        (ROOT / "data/manifest.json").read_text(encoding="utf-8-sig")
    )
    task_ids = benchmark[f"{args.split}_task_ids"]
    if args.task_id:
        if args.task_id not in task_ids:
            parser.error("Task ID does not belong to the selected split")
        task_ids = [args.task_id]

    if args.split == "final" and (args.runs != 3 or args.task_id):
        parser.error("Final evaluation requires all 30 tasks and --runs 3")

    manifest_path = ROOT / "versions" / args.version / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    version_manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    passport = json.loads(
        (ROOT / "configs/server_passport.json").read_text(encoding="utf-8-sig")
    )
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()

    prompt = (ROOT / "prompts/react_system.txt").read_text(
        encoding="utf-8-sig"
    )
    suite = get_suites(benchmark["benchmark_version"])[benchmark["suite"]]

    tracing = not args.no_tracing
    mlflow.set_tracking_uri(
        f"sqlite:///{(ROOT / 'mlflow.db').as_posix()}"
    )
    experiment = mlflow.set_experiment(f"LR7_{args.split.capitalize()}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    batch_id = f"{args.version}_{args.split}_{stamp}"
    output_dir = ROOT / "eval" / batch_id
    output_dir.mkdir(parents=True, exist_ok=False)
    records_dir = ROOT / "results" / batch_id
    records_dir.mkdir(parents=True, exist_ok=False)

    summary = {
        "batch_id": batch_id,
        "version": args.version,
        "split": args.split,
        "task_ids": task_ids,
        "runs_per_task": args.runs,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "evaluation_commit": commit,
        "manifest_path": manifest_path.relative_to(ROOT).as_posix(),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "version_manifest": version_manifest,
        "server_passport": passport,
        "benchmark_version": benchmark["benchmark_version"],
        "suite": benchmark["suite"],
        "complete": False,
        "results": [],
    }
    summary_path = output_dir / "summary.json"
    write_json(summary_path, summary)

    client_class = TracedClient if tracing else BaselineClient
    client = client_class()

    if client.model_id != passport["model_path"]:
        raise SystemExit("Current model ID differs from the server passport")

    for run_number in range(1, args.runs + 1):
        for task_id in task_ids:
            agent = LiveReact(client, prompt)
            task = suite.get_user_task_by_id(task_id)
            trace_id = None
            utility = None
            run_error = None
            started = perf_counter()

            context = (
                mlflow.start_span(
                    name=f"episode {task_id}",
                    span_type=SpanType.AGENT,
                )
                if tracing else nullcontext()
            )

            try:
                with context as span:
                    if tracing:
                        trace_id = span.trace_id
                        span.set_inputs({
                            "task_id": task_id,
                            "query": task.PROMPT,
                        })
                        mlflow.update_current_trace(tags={
                            "task": task_id,
                            "version": args.version,
                            "run": str(run_number),
                            "batch": batch_id,
                            "split": args.split,
                        })

                    tool_context = (
                        patch(
                            "episode_tools.execute_tool",
                            side_effect=traced_execute_tool,
                        )
                        if tracing else nullcontext()
                    )
                    with tool_context:
                        utility, _ = suite.run_task_with_pipeline(
                            agent, task, None, {}
                        )

                    if tracing:
                        span.set_outputs({"utility": utility})
                        mlflow.update_current_trace(
                            tags={"utility": str(utility)}
                        )
            except Exception as exc:
                run_error = f"{type(exc).__name__}: {exc}"

            elapsed = perf_counter() - started
            usage = [entry.get("usage") or {} for entry in agent.model_trace]
            usage_complete = bool(usage) and all(
                type(item.get("prompt_tokens")) is int
                and type(item.get("completion_tokens")) is int
                for item in usage
            )
            episode = agent.episode or {}

            row = {
                "task_id": task_id,
                "run": run_number,
                "utility": utility,
                "run_error": run_error,
                "stop_reason": episode.get("stop_reason"),
                "model_calls": len(agent.model_trace),
                "tool_attempts": episode.get("tool_attempts"),
                "elapsed_seconds": elapsed,
                "input_tokens": (
                    sum(item["prompt_tokens"] for item in usage)
                    if usage_complete else None
                ),
                "output_tokens": (
                    sum(item["completion_tokens"] for item in usage)
                    if usage_complete else None
                ),
                "token_usage_complete": usage_complete,
                "trace_id": trace_id,
                "experiment_id": experiment.experiment_id,
            }
            record_path = records_dir / f"{task_id}_run{run_number}.json"
            write_json(record_path, {
                **row,
                "episode": agent.episode,
                "model_trace": agent.model_trace,
            })
            row["record_path"] = record_path.relative_to(ROOT).as_posix()
            summary["results"].append(row)
            write_json(summary_path, summary)

            print(
                f"Run {run_number}/{args.runs} | {task_id} | "
                f"utility={utility} | calls={row['model_calls']} | "
                f"tools={row['tool_attempts']} | seconds={elapsed:.3f}",
                flush=True,
            )
            if run_error:
                raise SystemExit(
                    f"Evaluation interrupted: {run_error}\n"
                    f"Partial results saved to: {summary_path}"
                )

    if tracing:
        mlflow.search_traces(max_results=1, flush=True)

    summary["complete"] = all(
        type(row["utility"]) is bool and row["token_usage_complete"]
        for row in summary["results"]
    )
    write_json(summary_path, summary)
    print("Summary saved to:", summary_path)
    if not summary["complete"]:
        raise SystemExit("Evaluation records incomplete. Inspect summary.json")
    print("LR7 evaluation batch: PASS")


if __name__ == "__main__":
    main()