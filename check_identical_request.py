import json
from datetime import datetime
from pathlib import Path

import mlflow

from check_tracing_live import TracedClient
from eval import BaselineClient


ROOT = Path(__file__).resolve().parent


def main():
    source = (
        ROOT
        / "results"
        / "base_debug_20261118_163657_923730"
        / "user_task_32_run1.json"
    )
    record = json.loads(source.read_text(encoding="utf-8-sig"))
    request = record["model_trace"][3]["request"]

    mlflow.set_tracking_uri(
        f"sqlite:///{(ROOT / 'mlflow.db').as_posix()}"
    )
    mlflow.set_experiment("LR7_IdenticalRequest")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output = ROOT / "results" / f"identical_request_{stamp}.json"
    results = []

    try:
        # 交替顺序，检查三对完全相同的请求。
        for pair in range(1, 4):
            order = [False, True] if pair % 2 else [True, False]
            for tracing in order:
                client = TracedClient() if tracing else BaselineClient()
                if client.model_id != request["model"]:
                    raise RuntimeError("Current model differs from saved request")

                model_trace = []
                options = {
                    key: value
                    for key, value in request.items()
                    if key not in ("model", "messages", "tools")
                }
                response = client.complete(
                    request["messages"],
                    model_trace,
                    tools=request.get("tools"),
                    **options,
                )
                entry = model_trace[-1]
                if entry["request"] != request:
                    raise RuntimeError("Request differs from saved request")

                results.append({
                    "pair": pair,
                    "tracing": tracing,
                    "model_trace": entry,
                })
                print(
                    f"Pair {pair} | tracing={tracing} | "
                    f"usage={entry.get('usage')}",
                    flush=True,
                )

        for pair in range(1, 4):
            rows = [row for row in results if row["pair"] == pair]
            first, second = [row["model_trace"] for row in rows]
            print(
                f"Pair {pair}: "
                f"usage_match={first.get('usage') == second.get('usage')}, "
                f"response_match={first.get('response') == second.get('response')}"
            )
    finally:
        output.write_text(
            json.dumps({
                "source": source.relative_to(ROOT).as_posix(),
                "saved_request": request,
                "results": results,
            }, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("Records saved to:", output)

    mlflow.search_traces(max_results=1, flush=True)


if __name__ == "__main__":
    main()