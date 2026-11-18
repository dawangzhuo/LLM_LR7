import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main():
    manifest_path = ROOT / "versions/base/manifest.json"
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8-sig")
    )
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    ).decode("utf-8").split("\0")

    manifest["file_sha256"] = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in tracked
        if name
        and not name.startswith(("versions/", "eval/", "reports/"))
        and (ROOT / name).is_file()
    }
    manifest["git_commit"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    manifest["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["environment"] = {"PYTHONHASHSEED": "0"}

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Baseline source hashes updated: PASS")


if __name__ == "__main__":
    main()