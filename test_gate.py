import unittest
from copy import deepcopy

from gate import compare


def make_summary(protected=5, other=2):
    task_ids = [f"task_{index}" for index in range(protected + other)]
    rows = []
    for index, task_id in enumerate(task_ids):
        for run in (1, 2, 3):
            rows.append({
                "task_id": task_id,
                "run": run,
                "utility": index < protected,
                "run_error": None,
                "input_tokens": 100,
                "output_tokens": 20,
                "token_usage_complete": True,
                "elapsed_seconds": 1.0,
            })
    return {
        "complete": True,
        "task_ids": task_ids,
        "runs_per_task": 3,
        "benchmark_version": "v1.2.2",
        "suite": "workspace",
        "split": "final",
        "version_manifest": {
            "benchmark": {
                "benchmark_version": "v1.2.2",
                "suite": "workspace",
            },
        },
        "results": rows,
    }


def set_outcomes(summary, task_id, outcomes):
    for row in summary["results"]:
        if row["task_id"] == task_id:
            row["utility"] = outcomes[row["run"] - 1]


class GateTests(unittest.TestCase):
    def test_identical_summaries_pass(self):
        base = make_summary()
        self.assertEqual(compare(base, deepcopy(base))["status"], "PASS")

    def test_one_loss_and_one_improvement_fail(self):
        base = make_summary()
        candidate = deepcopy(base)
        set_outcomes(candidate, "task_0", [True, False, False])
        set_outcomes(candidate, "task_5", [True, True, True])
        result = compare(base, candidate)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["lost"], ["task_0"])

    def test_one_candidate_failure_is_tolerated(self):
        base = make_summary()
        candidate = deepcopy(base)
        set_outcomes(candidate, "task_0", [True, False, True])
        self.assertEqual(compare(base, candidate)["status"], "PASS")

    def test_three_protected_tasks_require_review(self):
        base = make_summary(protected=3)
        self.assertEqual(compare(base, deepcopy(base))["status"], "REVIEW")

    def test_missing_run_is_error(self):
        base = make_summary()
        candidate = deepcopy(base)
        candidate["results"].pop()
        self.assertEqual(compare(base, candidate)["status"], "ERROR")

    def test_duplicate_run_is_error(self):
        base = make_summary()
        candidate = deepcopy(base)
        candidate["results"].append(deepcopy(candidate["results"][0]))
        self.assertEqual(compare(base, candidate)["status"], "ERROR")

    def test_different_benchmark_is_error(self):
        base = make_summary()
        candidate = deepcopy(base)
        candidate["benchmark_version"] = "different"
        self.assertEqual(compare(base, candidate)["status"], "ERROR")

    def test_remaining_tasks_drop_by_one_requires_review(self):
        base = make_summary()
        set_outcomes(base, "task_5", [True, True, False])
        set_outcomes(base, "task_6", [True, False, False])
        candidate = deepcopy(base)
        set_outcomes(candidate, "task_5", [False, False, False])
        set_outcomes(candidate, "task_6", [False, False, False])
        self.assertEqual(compare(base, candidate)["status"], "REVIEW")

    def test_exactly_25_percent_time_growth_passes(self):
        base = make_summary()
        candidate = deepcopy(base)
        for row in candidate["results"]:
            row["elapsed_seconds"] = 1.25
        self.assertEqual(compare(base, candidate)["status"], "PASS")

    def test_more_than_25_percent_time_growth_requires_review(self):
        base = make_summary()
        candidate = deepcopy(base)
        for row in candidate["results"]:
            row["elapsed_seconds"] = 1.26
        self.assertEqual(compare(base, candidate)["status"], "REVIEW")

    def test_more_than_25_percent_token_growth_requires_review(self):
        base = make_summary()
        candidate = deepcopy(base)
        for row in candidate["results"]:
            row["input_tokens"] = 131
        self.assertEqual(compare(base, candidate)["status"], "REVIEW")

    def test_model_free_test_failure_fails_gate(self):
        base = make_summary()
        result = compare(base, deepcopy(base), tests_failed=True)
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()