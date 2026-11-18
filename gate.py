import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from statistics import median


def validate(data):
    if data.get("complete") is not True:
        raise ValueError("Evaluation batch is incomplete")

    task_ids = data["task_ids"]
    if not task_ids or len(task_ids) != len(set(task_ids)):
        raise ValueError("Task list is empty or contains duplicates")
    if data["runs_per_task"] != 3:
        raise ValueError("Expected three runs per task")

    grouped = {task: {} for task in task_ids}
    for row in data["results"]:
        task = row["task_id"]
        run = row["run"]
        if task not in grouped:
            raise ValueError("Unexpected task")
        if type(run) is not int or run not in (1, 2, 3):
            raise ValueError("Invalid run index")
        if run in grouped[task]:
            raise ValueError("Duplicate task/run record")
        if type(row["utility"]) is not bool or row.get("run_error"):
            raise ValueError("Invalid task outcome or evaluation error")
        if row.get("token_usage_complete") is not True:
            raise ValueError("Incomplete token usage")

        for key in ("input_tokens", "output_tokens"):
            if type(row[key]) is not int or row[key] < 0:
                raise ValueError(f"Invalid {key}")
        seconds = row["elapsed_seconds"]
        if (
            type(seconds) not in (int, float)
            or not math.isfinite(seconds)
            or seconds <= 0
        ):
            raise ValueError("Invalid elapsed time")
        grouped[task][run] = row

    if any(set(runs) != {1, 2, 3} for runs in grouped.values()):
        raise ValueError("Missing task/run record")
    return grouped


def metrics(data):
    rows = data["results"]
    return {
        "successes": sum(row["utility"] for row in rows),
        "episodes": len(rows),
        "median_tokens": median(
            row["input_tokens"] + row["output_tokens"] for row in rows
        ),
        "median_seconds": median(row["elapsed_seconds"] for row in rows),
    }


def compare(base, candidate, tests_failed=False):
    try:
        first = validate(base)
        second = validate(candidate)

        for key in ("benchmark_version", "suite", "split"):
            if not base.get(key) or base[key] != candidate.get(key):
                raise ValueError(f"Evaluation setting differs: {key}")

        first_benchmark = base["version_manifest"]["benchmark"]
        second_benchmark = candidate["version_manifest"]["benchmark"]
        if first_benchmark != second_benchmark:
            raise ValueError("Benchmark manifests differ")
        if set(first) != set(second):
            raise ValueError("Task lists differ")

        base_counts = {
            task: sum(row["utility"] for row in runs.values())
            for task, runs in first.items()
        }
        candidate_counts = {
            task: sum(row["utility"] for row in runs.values())
            for task, runs in second.items()
        }

        protected = sorted(task for task in first if base_counts[task] == 3)
        lost = [
            task for task in protected if candidate_counts[task] < 2
        ]
        newly_solved = sorted(
            task for task in first
            if base_counts[task] < 2 and candidate_counts[task] >= 2
        )

        remaining = set(first) - set(protected)
        remaining_drop = sum(
            Fraction(base_counts[task] - candidate_counts[task], 3)
            for task in remaining
        )
        base_metrics = metrics(base)
        candidate_metrics = metrics(candidate)
        token_growth = (
            candidate_metrics["median_tokens"] / base_metrics["median_tokens"] - 1
            if base_metrics["median_tokens"] else
            (math.inf if candidate_metrics["median_tokens"] else 0)
        )
        time_growth = (
            candidate_metrics["median_seconds"] / base_metrics["median_seconds"] - 1
        )

        failures = []
        reviews = []
        if lost:
            failures.append("Protected tasks lost")
        if tests_failed:
            failures.append("Model-free tests failed")
        if len(protected) < 5:
            reviews.append("Fewer than five protected tasks")
        if remaining_drop >= 1:
            reviews.append("Expected solved count on remaining tasks dropped by at least one")
        if token_growth > 0.25:
            reviews.append("Median token cost increased by more than 25%")
        if time_growth > 0.25:
            reviews.append("Median episode time increased by more than 25%")

        return {
            "status": "FAIL" if failures else ("REVIEW" if reviews else "PASS"),
            "reasons": failures + reviews or ["All comparison conditions passed"],
            "protected": protected,
            "lost": lost,
            "newly_solved": newly_solved,
            "base_metrics": base_metrics,
            "candidate_metrics": candidate_metrics,
            "remaining_expected_solved_drop": float(remaining_drop),
            "token_growth_percent": token_growth * 100,
            "time_growth_percent": time_growth * 100,
        }
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        return {"status": "ERROR", "reasons": [str(exc)]}


def dashboard(result, base, candidate):
    lines = [
        "# Regression gate",
        "",
        f"Status: **{result['status']}**",
        "",
        *[f"- {reason}" for reason in result["reasons"]],
        "",
    ]
    if "base_metrics" not in result:
        return "\n".join(lines) + "\n"

    lines += [
        "| Metric | Base | Candidate |",
        "|---|---:|---:|",
    ]
    for key in ("successes", "episodes", "median_tokens", "median_seconds"):
        lines.append(
            f"| {key} | {result['base_metrics'][key]} "
            f"| {result['candidate_metrics'][key]} |"
        )

    for label, data in (("Base", base), ("Candidate", candidate)):
        lines += [
            "",
            f"## {label}",
            "",
            f"- Batch `{data['batch_id']}`",
            f"- Version `{data['version']}`",
            f"- Evaluation commit `{data['evaluation_commit']}`",
            f"- Manifest `{data['manifest_path']}`",
            f"- Manifest SHA-256 `{data['manifest_sha256']}`",
        ]

    lines += [
        "",
        f"Protected tasks: {len(result['protected'])}",
        "",
        f"Lost tasks: {len(result['lost'])}",
        "",
        f"Token median change: {result['token_growth_percent']:+.2f}%",
        "",
        f"Time median change: {result['time_growth_percent']:+.2f}%",
        "",
        "## Changed tasks",
        "",
    ]
    changed = result["lost"] + result["newly_solved"]
    if not changed:
        lines.append("No lost protected tasks or newly majority-solved tasks.")
    for task in changed:
        lines += ["", f"### {task}", ""]
        for label, data in (("Base", base), ("Candidate", candidate)):
            for row in data["results"]:
                if row["task_id"] == task:
                    lines.append(
                        f"- {label}, run {row['run']}, "
                        f"utility={row['utility']}, trace `{row.get('trace_id')}`, "
                        f"record `{row.get('record_path')}`"
                    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base")
    parser.add_argument("candidate")
    parser.add_argument("--report", required=True)
    parser.add_argument("--tests-failed", action="store_true")
    args = parser.parse_args()

    base = {}
    candidate = {}
    try:
        base = json.loads(Path(args.base).read_text(encoding="utf-8-sig"))
        candidate = json.loads(
            Path(args.candidate).read_text(encoding="utf-8-sig")
        )
        result = compare(base, candidate, args.tests_failed)
    except (OSError, ValueError) as exc:
        result = {"status": "ERROR", "reasons": [str(exc)]}

    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dashboard(result, base, candidate), encoding="utf-8")

    print("Gate status:", result["status"])
    for reason in result["reasons"]:
        print("Reason:", reason)
    if "protected" in result:
        print("Protected tasks:", len(result["protected"]))
        print("Lost tasks:", len(result["lost"]))
        print(f"Token change: {result['token_growth_percent']:+.2f}%")
        print(f"Time change: {result['time_growth_percent']:+.2f}%")
    print("Report saved to:", output.resolve())
    raise SystemExit(1 if result["status"] in ("FAIL", "ERROR") else 0)


if __name__ == "__main__":
    main()