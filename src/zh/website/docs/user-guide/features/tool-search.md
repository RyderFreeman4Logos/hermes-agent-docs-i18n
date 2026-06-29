---
title: Tool Search
sidebar_position: 95
---

# 工具搜索功能

当一个会话中连接了众多MCP服务器或非核心插件工具时，它们的JSON架构可能会在每一轮对话中占用大量上下文窗口空间——即便其中只有少数工具与用户实际提出的问题相关。

**工具搜索功能**正是Hermes为解决这一问题而推出的可选渐进式披露机制。启用该功能后，模型可见工具数组中的MCP工具和插件工具会被三个桥接工具替代，模型会按需加载每个特定工具的架构。

:::info 内置Hermes工具从不延迟加载
构成Hermes核心功能集的工具（如`terminal`、`read_file`、`write_file`、`patch`、`search_files`、`todo`、`memory`、`browser_*`、`web_search`、`web_extract`、`clarify`、`execute_code`、`delegate_task`、`session_search`以及`_HERMES_CORE_TOOLS`中的其他工具）会*始终*直接加载。只有MCP工具和非核心插件工具才具备延迟加载的资格。
:::

## 工作原理

当某轮对话启用工具搜索功能时，模型会看到被延迟加载的工具被三个新工具所取代：

```
tool_search(query, limit?)     — search the deferred-tool catalog
tool_describe(name)            — load the full schema for one tool
tool_call(name, arguments)     — invoke a deferred tool
```

典型的交互流程如下：

```
Model: tool_search("create a github issue")
  → { matches: [{ name: "mcp_github_create_issue", ... }, ...] }
Model: tool_describe("mcp_github_create_issue")
  → { parameters: { type: "object", properties: { ... } } }
Model: tool_call("mcp_github_create_issue", { title: "...", body: "..." })
  → { ok: true, issue_number: 42 }
```

当模型调用 `tool_call` 时，Hermes 会**解除桥接层的封装**，并将请求直接转发给底层的工具，其效果就如同模型直接调用了该工具一样。无论是调用前的钩子、安全限制、审批提示，还是调用后的钩子，都会针对真实的工具名称执行，而非 `tool_call`。CLI 和网关中的操作日志也会去除桥接层的封装，因此你能看到的是底层工具本身，而非桥接层。

## 何时启用该功能？

默认情况下，工具搜索以“自动”模式运行：只有当那些可延迟调用的工具所需占用的上下文窗口空间达到活跃模型总容量的 10% 时，该功能才会被激活。在未达到此阈值时，工具数组的构建仅起到简单转发作用，不会产生任何额外开销。

由于这一判断会在每次构建工具数组时重新评估，因此会出现以下情况：
- 若会话中仅包含少量 MCP 工具且上下文模型容量较大，则工具搜索永远不会被激活。
- 若会话中连接了众多 MCP 服务器（通常为 15 种及以上工具），则该功能会开始启动。
- 若在会话进行过程中移除某些 MCP 服务器，那么在下一次构建工具数组时，系统会自动恢复直接调用模式。

## 配置

```yaml
tools:
  tool_search:
    enabled: auto       # auto (default), on, or off
    threshold_pct: 10   # percentage of context — only used in auto mode
    search_default_limit: 5
    max_search_limit: 20
```

| 键值 | 默认值 | 含义 |
| --- | --- | --- |
| `enabled` | `auto` | `auto` 模式在上下文长度超过阈值时启用；若存在至少一个可延迟处理的工具，则始终处于 `on` 状态；`off` 表示完全禁用该功能。 |
| `threshold_pct` | `10` | `auto` 模式启动的上下文长度百分比阈值，范围为 0–100。 |
| `search_default_limit` | `5` | 当模型调用 `tool_search` 时未指定 `limit` 参数时返回的搜索结果数量。 |
| `max_search_limit` | `20` | 模型通过 `limit` 参数可请求的最大搜索结果数量上限，范围为 1–50。 |

您也可以切换为传统的布尔值格式：

```yaml
tools:
  tool_search: true   # equivalent to {enabled: auto}
```

## 何时不应使用该功能

Tool Search通过牺牲每轮固定的令牌成本（三种桥接工具模式约300个令牌）以及至少一次额外的往返调用过程（搜索→描述→调用），来换取延迟加载工具模式的成本节省。当工具数量较多且每轮使用的工具较少时，这种做法显然更具优势；而当工具总数较少时，则会带来额外开销。

默认的`auto`模式会自动处理这些问题。如果您无条件将`enabled`设置为`on`，那么在工具较少的场景下，每轮仍会产生一定的成本。

## 无法避免的权衡

这些问题源于提示词缓存的一致性要求——它们是任何渐进式披露设计所固有的，并非该实现特有：

- **针对冷启动工具的额外往返调用**。模型首次需要使用延迟加载的工具时，需要额外进行一两次调用来查找并加载其结构描述。虽然静态加载方式确实能节省令牌，但部分成本仍需在运行时补偿。
- **延迟加载工具模式无法享受缓存优势**。已加载的`tool_describe`结果会被记录到对话历史中（因此会在后续轮次中被缓存），但它无法受益于系统提示词缓存的前缀优化。
- **模型质量的影响**。Tool Search假设模型能够为其所需工具编写合理的搜索查询。小型模型的表现较差；Anthicropic公布的测试数据表明（使用Tool Search后Opus 4模型的准确率从49%提升至74%），尽管有改善，但仍有约26个百分点的准确率损失源于检索失败。
- **工具集修改会导致缓存失效**。在会话进行中添加或删除工具，会改变桥接工具的描述信息（其中包含延迟加载工具的数量）以及工具目录，从而导致提示词缓存失效。这与任何工具集修改都会带来的后果相同。

## 实现细节

- **检索机制**：基于对工具名称、描述及参数名称进行分词后的BM25算法进行检索。当BM25未找到匹配结果时，会回退到对工具名称的直接子串匹配，以避免IDF值为零的极端情况（例如在所有工具名称都包含“github”的目录中搜索“github”）。
- **工具目录在多轮对话间保持无状态**：系统会在每次会话开始时根据当前的工具定义列表重新构建工具目录——不会使用基于会话密钥的`Map`结构。这样可以避免因存储的目录与实时工具注册表不同步而引发的故障。
- **工具目录仅限于当前会话的工具集范围**：`tool_search`、`tool_describe`和`tool_call`函数仅能访问和调用当前会话中被授权使用的工具。那些被限制只能使用部分工具集的子代理、看板任务处理程序或网关会话，无法通过桥接机制发现或调用该范围之外的工具——延迟加载的目录仅包含当前会话中已启用/禁用的工具集中的对应部分，而非整个流程的注册表。
- **不支持JS沙箱**：Hermes采用更简单的“结构化工具”模式（将搜索、描述和调用操作视为普通函数）。其他一些实现提供的JS沙箱“代码模式”存在较大的安全风险，因此我们未采用该机制。

## 参考资料

- `tools/tool_search.py` —— 实现代码
- `tests/tools/test_tool_search.py` —— 回归测试套件
- 原始实现PR中的`openclaw-tool-search-report` PDF文件，其中包含了影响该设计的研究成果
