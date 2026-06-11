# 工具搜索实时测试套件

该工具会针对真实模型（通过 OpenRouter 连接的 Claude Haiku 4.5）执行五种测试场景，以验证桥接工具能否实现端到端的正常运行。所有测试对话记录都会保存在 `scripts/out/` 目录中。

## 运行方式

```bash
cd <repo root>
python3 scripts/tool_search_livetest.py        # runs all 5 scenarios x 2 modes
python3 scripts/analyze_livetest.py            # side-by-side report
```

需在 `~/.hermes/.env` 文件中设置或存在 `OPENROUTER_API_KEY`。

## 验证内容

| 场景 | 测试项 |
|------|--------|
| A 明确单一工具 | 对明确工具名称（如 github_create_issue）进行 BM25 检索 |
| B 模糊改写需求 | 当模型需要改写请求时进行检索（例如将“安排会议”转换为 evt_create） |
| C 多工具链操作 | 连续执行多步任务，涉及两个延迟调用的工具（GitHub + Slack） |
| D 核心工具与延迟工具结合 | 混合使用直接调用的核心工具（read_file）以及通过桥接机制调用的延迟工具（Slack） |
| E 无需使用工具 | 纯知识类提示词；验证不会发生不必要的 tool_search 调用 |

对于每个场景，都会先在 `tool_search.enabled = on` 的条件下运行，然后再在 `off` 的条件下运行，以此形成 A/B 对比基准。该测试框架会记录以下信息：

- bridge_calls（模型发出的 tool_search / tool_describe / tool_call 调用序列）
- underlying_tool_calls（实际通过注册表调度器执行的调用）
- 最终响应、迭代次数、耗时以及任何错误信息

## 输出结构

```
scripts/out/
  <scenario>__enabled.json    # tool_search ON
  <scenario>__disabled.json   # tool_search OFF
  _summary.json               # one-line summary across all runs
```

已存档2026-05版本的基准运行结果以供参考。重新运行可能会生成略有差异的转录内容（该模型具有非确定性），但预期的底层工具调用断言应依然能够得到满足。
