# delegate_task：诊断“我的任务批次被限制了”

当用户反馈`delegate_task`运行的子代理数量少于其预期值时（例如：“我设置了max_concurrent_children为15，但实际上只运行了9个”），Hermes中实际上存在**三种**限制任务批次的代码路径。如果这些路径均未触发，那么限制措施便来自**模型本身**——而非Hermes——此时用户所说的“运行时被限制在N个”其实是模型对自己决策的合理化解释。

## Hermes中的三种实际限制机制

所有限制均通过`tools.delegate_tool._get_max_concurrent_children()`函数实现，该函数会读取`config.yaml`文件中的`delegation.max_concurrent_children`配置项（若未配置则使用环境变量`DELEGATION_MAX_CONCURRENT_CHILDREN`，默认值为3），且最低限制为1。**不存在硬性上限。**

1. **单次调用直接拒绝**——位于`tools/delegate_tool.py`文件中（约第1953行）。如果`len(tasks) > max_children`，该函数会返回一个包含如下信息的`tool_error`错误：`"任务数量过多：用户提供了{N}个任务，但最大并发子代理数为{M}。......"`模型会将此视为工具调用失败，通常会尝试使用更少的任务重新执行。

2. **单轮对话截断机制**——位于`run_agent.py::AIAgent._cap_delegate_task_calls`函数中（约第5708行）。如果在一次助手对话中，模型发出了*多个独立的*`delegate_task`工具调用，那么这些调用的数量将被限制在`max_children`以内。系统会以警告级别记录如下信息：`为确保最大并发子代理数不超过{M}，已截断{N}个多余的delegate_task调用。`

3. **成本警告**——同样通过 `_get_max_concurrent_children()` 函数实现。当计算出的数值大于10时，系统会仅输出一条警告日志：`delegation.max_concurrent_children={N}：每个子代理都会独立消耗API令牌，较高的数值会导致成本呈线性增长。`这**仅仅是一条日志记录**——并不会真正限制任何功能。很容易被误认为是“Hermes拒绝了我的设置值。”

## 诊断步骤

当用户表示“delegate功能被限制在N个”时：

```bash
# 1. What does the loaded config actually say?
hermes config get delegation.max_concurrent_children

# 2. Did Hermes' truncator or rejector actually fire?
grep -E "Truncated.*delegate_task|Too many tasks" ~/.hermes/logs/agent.log | tail
# If neither line appears, neither cap path executed.

# 3. Confirm the resolver returns what config says (in venv with hermes on path)
python -c "from tools.delegate_tool import _get_max_concurrent_children; \
           print(_get_max_concurrent_children())"
```

如果配置值与 `_get_max_concurrent_children()` 的返回结果一致，且两条日志均不出现，**那么限制因素在于模型本身，而非 Hermes**。

## 为何模型会自我限制任务批次大小

推理型模型（如 Claude Opus/Sonnet、GPT-5、Grok-4）在内部判断协调成本高于并行处理效率时，通常会将原本包含 13 或 15 个任务的批次缩减为更接近整数的数量（如 5、8、9、10）。启动时输出的成本警告日志会进一步强化这一行为——模型通过读取自身的推理过程，发现“每个子任务都会独立消耗 API 令牌”，因此认为较小的批次更为合理。

随后，模型会将这一决策解释为“运行时限制为 9”或“尽管配置值为 15，但最大并行数实际为 9”。但实际上**这并非事实**，只是模型事后的合理化解释。向用户说明这一点并无问题，因为这是推理型模型中一种常见且广为人知的缺陷表现（即倾向于将问题归咎于系统，而非承认是模型自身设定了限制）。

## 如何强制启用 N 个并行子任务

在提示词中明确告知模型：

> “请通过**一次**`delegate_task` 调用发送全部 13 个任务，`tasks` 数组中应包含恰好 13 个项目。切勿拆分为多次调用。运行时支持此操作，且 `delegation.max_concurrent_children` 的值已设置为 15。”

如果模型仍会自动缩减任务数量，可使用 `execute_code` 功能以确定性方式构建 `tasks` 列表，并使用该精确列表调用工具——此时模型仅充当传递者角色，不太可能对任务数量产生质疑。或者更换为其他模型：实际上，规模较小或推理强度较低的模型较少出现这种过度限制的行为。

## 常见陷阱与注意事项

- **`max_concurrent_children` 是针对每个父任务的独立限制，而非全局限制。**这一点在 `ui-tui/src/components/appChrome.tsx` 中有明确说明。不同的父任务可以各自同时启动最多 `max_children` 个工作进程。
- **`subagent_auto_approve: false` 并不会限制并行度**。它仅控制子任务是否继承“快速批准”功能，切勿将其误认为是限流机制。
- 当任务数量超过 10 时，**每次调用都会触发成本警告日志**。但请注意，仅凭该日志的存在并不能证明存在实际的限制——只有出现 `Truncated...` 和 `Too many tasks` 这类日志时，才表明确实存在限制。
- **切勿建议通过将 `max_concurrent_children` 恢复原值来解决此问题**。该数值是用户刻意设置的，正确的解决方式应是向模型提出明确要求，而非修改配置文件。
