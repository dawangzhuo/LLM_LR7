import json
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parent

WITHOUT = ROOT / "eval/base_debug_20261118_163657_923730/summary.json"
WITH = ROOT / "eval/base_debug_20261118_165820_851029/summary.json"


def load_summary(path, expected_tracing):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not data.get("complete"):
        raise SystemExit(f"Incomplete batch: {path}")
    if data["tracing"] is not expected_tracing:
        raise SystemExit(f"Unexpected tracing setting: {path}")
    rows = data["results"]
    if len(rows) != 10 or len({row["task_id"] for row in rows}) != 10:
        raise SystemExit(f"Expected 10 unique task records: {path}")
    if any(row["run"] != 1 for row in rows):
        raise SystemExit(f"Expected one run per task: {path}")
    return data, {row["task_id"]: row for row in rows}


def main():
    baseline, without = load_summary(WITHOUT, False)
    traced, with_tracing = load_summary(WITH, True)

    for key in (
        "version", "split", "runs_per_task", "evaluation_commit",
        "manifest_sha256", "benchmark_version", "suite",
    ):
        if baseline[key] != traced[key]:
            raise SystemExit(f"Batch configuration mismatch: {key}")

    if set(without) != set(with_tracing):
        raise SystemExit("Task lists differ")

    comparisons = []
    for task_id in baseline["task_ids"]:
        first = without[task_id]
        second = with_tracing[task_id]

        for row in (first, second):
            if (
                type(row["utility"]) is not bool
                or row.get("run_error")
                or not row["token_usage_complete"]
            ):
                raise SystemExit(f"Invalid record: {task_id}")
            if any(
                type(row[key]) is not int or row[key] < 0
                for key in ("input_tokens", "output_tokens")
            ):
                raise SystemExit(f"Invalid token counts: {task_id}")

        comparison = {
            "task_id": task_id,
            "utility_match": first["utility"] == second["utility"],
            "tokens_match": (
                first["input_tokens"] == second["input_tokens"]
                and first["output_tokens"] == second["output_tokens"]
            ),
            "model_calls_match": first["model_calls"] == second["model_calls"],
            "tool_attempts_match": first["tool_attempts"] == second["tool_attempts"],
            "without_seconds": first["elapsed_seconds"],
            "with_seconds": second["elapsed_seconds"],
            "without_input_tokens": first["input_tokens"],
            "with_input_tokens": second["input_tokens"],
            "without_output_tokens": first["output_tokens"],
            "with_output_tokens": second["output_tokens"],
        }
        comparisons.append(comparison)
        print(
            f"{task_id}: "
            f"utility_match={comparison['utility_match']}, "
            f"tokens_match={comparison['tokens_match']}"
        )

    without_median = median(
        row["elapsed_seconds"] for row in without.values()
    )
    with_median = median(
        row["elapsed_seconds"] for row in with_tracing.values()
    )
    change = (with_median / without_median - 1) * 100

    checks = {
        key: all(row[key] for row in comparisons)
        for key in (
            "utility_match", "tokens_match",
            "model_calls_match", "tool_attempts_match",
        )
    }
    report = {
        "without_summary": WITHOUT.relative_to(ROOT).as_posix(),
        "with_summary": WITH.relative_to(ROOT).as_posix(),
        "without_median_seconds": without_median,
        "with_median_seconds": with_median,
        "median_change_percent": change,
        "checks": checks,
        "per_task": comparisons,
        "timing_scope": "Episode time excluding final batch trace flush",
    }

    output = ROOT / "reports/experiment1_tracing_comparison_hashseed0.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Without tracing median: {without_median:.6f} s")
    print(f"With tracing median: {with_median:.6f} s")
    print(f"Median change: {change:+.2f}%")
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'MISMATCH'}")
    print("Comparison saved to:", output)


if __name__ == "__main__":
    main()