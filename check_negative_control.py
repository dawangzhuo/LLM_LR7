import os
import json
import subprocess
from copy import deepcopy
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace
from unittest.mock import patch

from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
from agentdojo.task_suite.load_suites import get_suites

from check_react_live import scoring_messages
from gate import compare, dashboard
from react_loop import run_react
from tool_executor import execute_tool


ROOT = Path(__file__).resolve().parent


class ScriptedAgent(BasePipelineElement):
    name = "negative-control-scripted-react"

    def __init__(self):
        self.episode = None

    def query(self, query, runtime, env, messages=(), extra_args=None):
        def reply(history):
            outputs = [
                message["content"]
                for message in history
                if message["role"] == "tool"
            ]
            if outputs:
                return {
                    "role": "assistant",
                    "content": outputs[-1] or "No tool output available.",
                }

            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "scripted_search_1",
                    "type": "function",
                    "function": {
                        "name": "search_calendar_events",
                        "arguments": json.dumps({
                            "query": "Networking event",
                            "date": "2024-05-26",
                        }),
                    },
                }],
            }

        self.episode = run_react(query, runtime, env, reply)
        return (
            query,
            runtime,
            env,
            scoring_messages(self.episode["messages"]),
            extra_args or {},
        )


def lose_tool_result(runtime, env, name, arguments):
    outcome = execute_tool(runtime, env, name, arguments)
    return SimpleNamespace(text="", error=outcome.error)


def write_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main():
    output_dir = Path(
    os.environ.get(
        "LR7_NEGATIVE_CONTROL_DIR",
        str(ROOT / "eval/negative_control"),
    )
).resolve()
    if output_dir.exists():
        raise SystemExit(
            "eval/negative_control already exists. Keep its saved results."
        )

    benchmark = json.loads(
        (ROOT / "data/manifest.json").read_text(encoding="utf-8-sig")
    )
    manifest_path = ROOT / "versions/base/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()

    suite = get_suites(benchmark["benchmark_version"])[benchmark["suite"]]
    task_id = "user_task_0"
    summaries = {}
    output_dir.mkdir(parents=True)

    for version in ("scripted_base", "scripted_broken"):
        summary = {
            "batch_id": version,
            "version": version,
            "split": "debug",
            "task_ids": [task_id],
            "runs_per_task": 3,
            "benchmark_version": benchmark["benchmark_version"],
            "suite": benchmark["suite"],
            "evaluation_commit": commit,
            "manifest_path": "versions/base/manifest.json",
            "manifest_sha256": __import__("hashlib").sha256(
                manifest_path.read_bytes()
            ).hexdigest(),
            "version_manifest": deepcopy(manifest),
            "complete": False,
            "results": [],
            "control": {
                "model_used": False,
                "scripted_agent_file": "check_negative_control.py",
                "lose_tool_result": version == "scripted_broken",
            },
        }

        for run_number in (1, 2, 3):
            agent = ScriptedAgent()
            task = suite.get_user_task_by_id(task_id)
            started = perf_counter()

            executor = (
                lose_tool_result
                if version == "scripted_broken"
                else execute_tool
            )
            with patch("episode_tools.execute_tool", side_effect=executor):
                utility, _ = suite.run_task_with_pipeline(
                    agent, task, None, {}
                )

            record_path = output_dir / f"{version}_run{run_number}.json"
            row = {
                "task_id": task_id,
                "run": run_number,
                "utility": utility,
                "run_error": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "token_usage_complete": True,
                "elapsed_seconds": perf_counter() - started,
                "trace_id": None,
                "record_path": record_path.relative_to(ROOT).as_posix(),
            }
            write_json(record_path, {**row, "episode": agent.episode})
            summary["results"].append(row)
            print(f"{version} | run={run_number} | utility={utility}")

        summary["complete"] = True
        write_json(output_dir / f"{version}.json", summary)
        summaries[version] = summary

    base = summaries["scripted_base"]
    broken = summaries["scripted_broken"]
    result = compare(base, broken)

    report_path = ROOT / "reports/negative_control_gate_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        dashboard(result, base, broken), encoding="utf-8"
    )
    print("Gate status:", result["status"])
    print("Lost tasks:", result.get("lost"))
    print("Report saved to:", report_path)

    if not all(row["utility"] is True for row in base["results"]):
        raise SystemExit("Scripted baseline failed. Inspect saved records.")
    if not all(row["utility"] is False for row in broken["results"]):
        raise SystemExit("Broken version did not fail consistently.")
    if result["status"] != "FAIL" or result["lost"] != [task_id]:
        raise SystemExit("Negative control detection: FAIL")

    print("Negative control detection: PASS")


if __name__ == "__main__":
    main()