from urllib.error import HTTPError
import json
from pathlib import Path
from time import perf_counter
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8080"

class ContextLimitError(RuntimeError):
    """模型服务明确拒绝了超出上下文容量的请求。"""
class ModelClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.model_id = self._request("/v1/models")["data"][0]["id"]

    def _request(self, path, payload=None):
        if payload is None:
            request = Request(self.base_url + path)
        else:
            request = Request(
                self.base_url + path,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
        with urlopen(request, timeout=180) as response:
            return json.load(response)

    def complete(self, messages, trace, *, tools=None, **options):
        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 1024,
            **options,
        }
        if tools:
            payload["tools"] = tools

        # 复制请求内容，避免后续追加消息时改变已经记录的历史。
        entry = {
            "message_count": len(messages),
            "request": json.loads(json.dumps(payload)),
        }
        trace.append(entry)

        started = perf_counter()
        try:
            response = self._request("/v1/chat/completions", payload)
            choice = response["choices"][0]
            entry["response"] = choice["message"]
            entry["finish_reason"] = choice.get("finish_reason")
            entry["usage"] = response.get("usage")
            return choice["message"]
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            entry["error"] = f"HTTP {exc.code}: {body}"

            try:
                detail = json.loads(body).get("error", {})
            except (json.JSONDecodeError, AttributeError):
                detail = {}

            error_type = detail.get("type") if isinstance(detail, dict) else None
            error_code = detail.get("code") if isinstance(detail, dict) else None

            if "exceed_context_size_error" in (error_type, error_code) or (
                "context_length_exceeded" in (error_type, error_code)
            ):
                raise ContextLimitError("The request exceeded the model context.") from exc

            raise
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            entry["elapsed_seconds"] = round(perf_counter() - started, 6)


def smoke_test():
    client = ModelClient()
    trace = []
    tool = {
        "type": "function",
        "function": {
            "name": "get_book_status",
            "description": "Look up the status of a book by its ID.",
            "parameters": {
                "type": "object",
                "properties": {"book_id": {"type": "string"}},
                "required": ["book_id"],
            },
        },
    }
    messages = [{
        "role": "user",
        "content": "Use the get_book_status tool to check book B123.",
    }]
    output = Path("results") / "model_client_smoke.json"
    output.parent.mkdir(exist_ok=True)

    try:
        message = client.complete(messages, trace, tools=[tool], tool_choice="auto")
    finally:
        output.write_text(
            json.dumps(trace, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    calls = message.get("tool_calls") or []
    if len(calls) != 1:
        raise SystemExit(f"Tool call: FAIL. See {output}")

    function = calls[0]["function"]
    if (
        function["name"] != "get_book_status"
        or json.loads(function["arguments"]) != {"book_id": "B123"}
    ):
        raise SystemExit(f"Tool name or arguments: FAIL. See {output}")

    usage = trace[0]["usage"] or {}
    if not all(isinstance(usage.get(key), int)
               for key in ("prompt_tokens", "completion_tokens")):
        raise SystemExit(f"Token usage: FAIL. See {output}")

    print("Python model client tool call: PASS (get_book_status, B123)")
    print(f"Input tokens: {usage['prompt_tokens']}")
    print(f"Output tokens: {usage['completion_tokens']}")
    print(f"Trace saved to: {output.resolve()}")


if __name__ == "__main__":
    smoke_test()