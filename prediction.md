# LR7 Pre-Experiment Predictions

Recorded before the formal LR7 experiments.

## 1. Baseline and evaluation settings

The baseline uses the LR4 ReAct agent with the LR5 zero-fault
configuration: temperature 0, seed 42, at most 15 model calls,
and at most 15 tool attempts.

The benchmark is AgentDojo 0.1.35, benchmark version v1.2.2,
workspace suite. The existing split contains 10 debug tasks
and 30 final tasks.

Each final task will be evaluated three times per version.
All completed runs will be retained.

> 中文批注：沿用原来的任务划分和零故障配置，每个版本的每道最终题运行三次。

## 2. Tracing overhead

I predict that tracing will increase median episode time
by less than 10% on the 10 debug tasks.

With identical requests and server settings, I expect task
outcomes and token counts to match between tracing enabled
and disabled runs. Any differences will be investigated.

> 中文批注：预计追踪的耗时增幅小于 10%，结果与 token 数应一致。
> 这是运行前预测，实际差异需要检查。

## 3. A/A comparison

I predict PASS when comparing two independent evaluation
batches of the unchanged baseline.

A task is protected only if the baseline succeeds in all
three runs. A protected task is lost if the compared version
succeeds in fewer than two of three runs.

> 中文批注：同一版本独立运行两批，预计门禁通过。
> 基线三次全对的题才受保护，候选版至少两次成功才保住该题。

## 4. Candidate change

The candidate will truncate each tool-result text delivered
to the model to its first 2,000 Python string characters.
Tool execution and environment state changes remain part
of the normal AgentDojo evaluation.

I predict that tasks requiring information near the end of
long email, file, or search results are most vulnerable.
The affected task IDs will be identified from traces.

I predict lower median input-token usage. Episode time may
decrease, but extra tool calls may offset the saving.

I predict FAIL because at least one protected task may lose
necessary information.

> 中文批注：候选版只把工具返回文本的前 2,000 个字符传给模型。
> 长邮件、文件或搜索结果末尾的信息可能丢失。
> 预计输入 token 减少，但补充查询可能抵消耗时收益。
> 预计至少一道受保护任务受影响，门禁为 FAIL。

## 5. Repair attempt

The repaired candidate will retain truncation and append
an explicit notice that the result was truncated, asking
the agent to refine its query when necessary.

I predict fewer lost protected tasks than for the candidate.
The repair may require more tool calls and input tokens.
Complete recovery is uncertain.

If the first change causes no regressions, a second change
will be selected from the assignment and its prediction
recorded before running it.

> 中文批注：修复版保留截断，并明确提示模型结果不完整、必要时细化查询。
> 预计丢失任务减少，但调用次数和 token 可能回升。

## 6. Gate rules fixed before evaluation

- FAIL if any protected task is lost or model-free tests fail.
- REVIEW if no protected task is lost, but expected solved-task
  count on the remaining tasks drops by at least one task,
  median token cost or episode time increases by more than 25%,
  or fewer than five tasks are protected.
- ERROR if results are missing or invalid, task lists differ,
  or benchmark versions differ.
- PASS otherwise.

Token cost will be measured as input plus output tokens
per episode for the local model.

Improvements on other tasks do not compensate for a lost
protected task.

> 中文批注：正式运行前固定门禁规则，本地模型用输入加输出 token 衡量开销。
> 其余任务的平均成功数按各题三次成功比例求和。