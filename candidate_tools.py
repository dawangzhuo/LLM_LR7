from contextlib import nullcontext

from tool_executor import ToolOutcome, execute_tool


NOTICE = (
    "\n[Tool result truncated to 2000 characters. "
    "Refine your query or request a smaller portion if needed.]"
)


def transform_result(text, version):
    if version == "base" or len(text) <= 2000:
        return text
    if version == "truncate2000":
        return text[:2000]
    if version == "truncate2000_notice":
        return text[:2000] + NOTICE
    raise ValueError(f"Unknown version: {version}")


def make_executor(version, tracing, records):
    def run_tool(runtime, env, name, arguments):
        if tracing:
            import mlflow
            from mlflow.entities import SpanType

            context = mlflow.start_span(
                name=name,
                span_type=SpanType.TOOL,
            )
        else:
            context = nullcontext()

        with context as span:
            if span is not None:
                span.set_inputs({
                    "tool_name": name,
                    "arguments": arguments,
                })

            original = execute_tool(runtime, env, name, arguments)
            delivered = transform_result(original.text, version)
            record = {
                "tool_name": name,
                "arguments": arguments,
                "original_text": original.text,
                "delivered_text": delivered,
                "original_chars": len(original.text),
                "delivered_chars": len(delivered),
                "truncated": delivered != original.text,
                "error": original.error,
            }
            records.append(record)

            if span is not None:
                span.set_outputs(record)
                span.set_attribute("tool_name", name)
                span.set_attribute("result_chars", len(delivered))
                span.set_attribute("tool_error", bool(original.error))
                span.set_attribute("truncated", record["truncated"])

            return ToolOutcome(text=delivered, error=original.error)

    return run_tool