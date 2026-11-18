# Regression gate

Status: **FAIL**

- Protected tasks lost
- Fewer than five protected tasks

| Metric | Base | Candidate |
|---|---:|---:|
| successes | 3 | 0 |
| episodes | 3 | 3 |
| median_tokens | 0 | 0 |
| median_seconds | 0.0460925999796018 | 0.04547190002631396 |

## Base

- Batch `scripted_base`
- Version `scripted_base`
- Evaluation commit `b26ee40f3fe4a4e14c81b50c04bd7541d2726975`
- Manifest `versions/base/manifest.json`
- Manifest SHA-256 `8748937fcff760a03d6935c0b013d2058ebf455c5f34b39c6faaef2c52d4a399`

## Candidate

- Batch `scripted_broken`
- Version `scripted_broken`
- Evaluation commit `b26ee40f3fe4a4e14c81b50c04bd7541d2726975`
- Manifest `versions/base/manifest.json`
- Manifest SHA-256 `8748937fcff760a03d6935c0b013d2058ebf455c5f34b39c6faaef2c52d4a399`

Protected tasks: 1

Lost tasks: 1

Token median change: +0.00%

Time median change: -1.35%

## Changed tasks


### user_task_0

- Base, run 1, utility=True, trace `None`, record `eval/negative_control/scripted_base_run1.json`
- Base, run 2, utility=True, trace `None`, record `eval/negative_control/scripted_base_run2.json`
- Base, run 3, utility=True, trace `None`, record `eval/negative_control/scripted_base_run3.json`
- Candidate, run 1, utility=False, trace `None`, record `eval/negative_control/scripted_broken_run1.json`
- Candidate, run 2, utility=False, trace `None`, record `eval/negative_control/scripted_broken_run2.json`
- Candidate, run 3, utility=False, trace `None`, record `eval/negative_control/scripted_broken_run3.json`
