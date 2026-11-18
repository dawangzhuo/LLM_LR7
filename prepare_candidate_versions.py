import hashlib
import json
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main():
    versions = ("truncate2000", "truncate2000_notice")
    for version in versions:
        if (ROOT / "versions" / version).exists():
            raise SystemExit(f"Version directory already exists: {version}")

    base_path = ROOT / "versions/base/manifest.json"
    base = json.loads(base_path.read_text(encoding="utf-8-sig"))
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    ).decode("utf-8").split("\0")

    hashes = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in tracked
        if name
        and not name.startswith(("versions/", "eval/", "reports/"))
        and (ROOT / name).is_file()
    }
    for required in ("eval.py", "candidate_tools.py"):
        if required not in hashes:
            raise SystemExit(f"Commit this file first: {required}")

    tools = (ROOT / "versions/base/tool_descriptions.json").read_bytes()

    for version in versions:
        manifest = deepcopy(base)
        manifest["version"] = version
        manifest["git_commit"] = commit
        manifest["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["file_sha256"] = hashes
        manifest["parent_manifest_sha256"] = hashlib.sha256(
            base_path.read_bytes()
        ).hexdigest()
        manifest["change"] = {
            "kind": "tool_result_truncation",
            "prefix_characters": 2000,
            "append_notice": version == "truncate2000_notice",
            "implementation": "candidate_tools.py",
            "original_results_preserved": True,
        }
        manifest["environment"] = {"PYTHONHASHSEED": "0"}

        folder = ROOT / "versions" / version
        folder.mkdir()
        (folder / "tool_descriptions.json").write_bytes(tools)
        (folder / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Version manifest saved: {version}")

    print("Candidate version manifests: PASS")


if __name__ == "__main__":
    main()