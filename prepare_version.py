import hashlib
import importlib.metadata as metadata
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
from agentdojo.task_suite.load_suites import get_suites


ROOT = Path(__file__).resolve().parent
BASE_URL = "http://127.0.0.1:8080"


def git_output(*arguments):
    return subprocess.check_output(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    ).strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request_json(endpoint):
    with urlopen(BASE_URL + endpoint, timeout=30) as response:
        return json.load(response)


class ToolDescriptionsCaptured(Exception):
    pass


class CaptureToolDescriptions(BasePipelineElement):
    name = "capture-tool-descriptions"

    def __init__(self):
        self.descriptions = None

    def query(self, query, runtime, env, messages=(), extra_args=None):
        self.descriptions = [
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
        raise ToolDescriptionsCaptured()


def main():
    status = git_output("status", "--porcelain", "--untracked-files=all")
    if status:
        raise SystemExit(
            "Commit the current code before preparing a version:\n" + status
        )

    benchmark = json.loads(
        (ROOT / "data" / "manifest.json").read_text(encoding="utf-8-sig")
    )
    suite = get_suites(benchmark["benchmark_version"])[benchmark["suite"]]
    task = suite.get_user_task_by_id(benchmark["debug_task_ids"][0])
    capture = CaptureToolDescriptions()

    try:
        suite.run_task_with_pipeline(capture, task, None, {})
    except ToolDescriptionsCaptured:
        pass

    if not capture.descriptions:
        raise SystemExit("Tool-description capture failed.")

    version_dir = ROOT / "versions" / "base"
    if version_dir.exists():
        raise SystemExit(
            "versions/base already exists. Keep the existing version record."
        )

    tool_bytes = (
        json.dumps(
            capture.descriptions,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        ) + "\n"
    ).encode("utf-8")

    tracked_files = git_output("ls-files", "-z").split("\0")
    file_hashes = {
        name: sha256(ROOT / name)
        for name in tracked_files
        if name and (ROOT / name).is_file()
    }

    server = {
        "base_url": BASE_URL,
        "health": request_json("/health"),
        "models": request_json("/v1/models"),
    }
    try:
        server["props"] = request_json("/props")
    except Exception as exc:
        server["props_unavailable"] = f"{type(exc).__name__}: {exc}"

    manifest = {
        "version": "base",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_output("rev-parse", "HEAD"),
        "working_tree_clean": True,
        "file_sha256": file_hashes,
        "tool_descriptions_sha256": hashlib.sha256(tool_bytes).hexdigest(),
        "tool_descriptions_file": "tool_descriptions.json",
        "tool_count": len(capture.descriptions),
        "benchmark": benchmark,
        "packages": {
            name: metadata.version(name)
            for name in ("agentdojo", "mlflow", "openai")
        },
        "generation": {
            "temperature": 0,
            "seed": 42,
            "max_tokens": 1024,
            "tool_choice": "auto",
            "max_calls": 15,
            "max_tools": 15,
            "fault_p": 0,
        },
        "server": server,
    }

    version_dir.mkdir(parents=True)
    (version_dir / "tool_descriptions.json").write_bytes(tool_bytes)
    manifest_path = version_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Version: base")
    print("Source commit:", manifest["git_commit"])
    print("Tracked file hashes:", len(file_hashes))
    print("Tool descriptions:", len(capture.descriptions))
    print("Debug tasks:", len(benchmark["debug_task_ids"]))
    print("Final tasks:", len(benchmark["final_task_ids"]))
    print("Manifest saved to:", manifest_path)
    print("LR7 baseline version manifest: PASS")


if __name__ == "__main__":
    main()