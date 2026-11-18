import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def git_output(*arguments):
    return subprocess.check_output(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    ).strip()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest_path = ROOT / "versions/base/manifest.json"
    backup_path = ROOT / "versions/base/manifest_initial.json"
    passport_path = ROOT / "configs/server_passport.json"
    tools_path = ROOT / "versions/base/tool_descriptions.json"

    for path in (manifest_path, passport_path, tools_path, ROOT / "eval.py"):
        if not path.is_file():
            raise SystemExit(f"Required file missing: {path}")

    if backup_path.exists():
        raise SystemExit(
            "manifest_initial.json already exists. Keep the existing backup."
        )

    passport = json.loads(
        passport_path.read_text(encoding="utf-8-sig")
    )

    # 通过 UTF-8 字节传输进程信息，保留路径中的中文字符。
    command = """
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
$connection = Get-NetTCPConnection -LocalPort 8080 -State Listen |
    Select-Object -First 1
if (-not $connection) {
    throw 'No model server listening on port 8080'
}
Get-CimInstance Win32_Process `
    -Filter ('ProcessId = ' + $connection.OwningProcess) |
    Select-Object ExecutablePath,CommandLine |
    ConvertTo-Json -Compress
"""
    process_bytes = subprocess.check_output(
        ["powershell.exe", "-NoProfile", "-Command", command]
    )
    current = json.loads(process_bytes.decode("utf-8-sig"))

    if current["CommandLine"] != passport["server_command_line"]:
        raise SystemExit(
            "Server command line differs from configs/server_passport.json"
        )

    executable = current.get("ExecutablePath")
    if not executable:
        raise SystemExit("Cannot read the running server executable path.")

    if file_hash(Path(executable)).lower() != passport["server_sha256"].lower():
        raise SystemExit("Server executable SHA-256 differs from the passport.")

    model_path = Path(passport["model_path"])
    print("Checking model SHA-256...", flush=True)
    if file_hash(model_path).lower() != passport["model_sha256"].lower():
        raise SystemExit("Model SHA-256 differs from the passport.")

    original = manifest_path.read_bytes()
    manifest = json.loads(original.decode("utf-8-sig"))

    tracked = git_output("ls-files", "-z").split("\0")
    source_paths = [
        name for name in tracked
        if name
        and not name.startswith(("versions/", "eval/"))
        and (ROOT / name).is_file()
    ]

    manifest["file_sha256"] = {
        name: file_hash(ROOT / name)
        for name in source_paths
    }
    manifest["git_commit"] = git_output("rev-parse", "HEAD")
    manifest["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["server_passport"] = passport
    manifest["server_passport_sha256"] = file_hash(passport_path)
    manifest["tool_descriptions_sha256"] = file_hash(tools_path)

    if "eval.py" not in manifest["file_sha256"]:
        raise SystemExit("eval.py must be tracked by Git before refreshing.")

    backup_path.write_bytes(original)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Server command line: MATCH")
    print("Server executable SHA-256: MATCH")
    print("Model SHA-256: MATCH")
    print("Source commit:", manifest["git_commit"])
    print("eval.py included: True")
    print("Backup saved to:", backup_path)
    print("Baseline manifest refresh: PASS")


if __name__ == "__main__":
    main()