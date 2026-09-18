---
sidebar_position: 13
title: "Delegation & Parallel Work"
description: "When and how to use subagent delegation — patterns for parallel research, code review, and multi-file work"
---

# 任务委派与并行处理

Hermes 能够创建独立的子代理，实现任务的并行处理。每个子代理拥有独立的对话界面、终端会话及工具集。最终只会返回汇总结果——中间阶段的工具调用不会出现在你的上下文窗口中。

如需查看完整的功能参考，请参阅 [子代理委派](/user-guide/features/delegation)。

---

## 何时进行任务委派

**适合委派的场景：**
- 需要大量推理的子任务（调试、代码审查、研究综合）
- 容易使上下文被中间数据淹没的任务
- 需要并行处理的独立工作流（同时开展研究 A 和 B）
- 需要在全新上下文中处理、以避免偏见的任务

**建议使用其他方式的场景：**
- 单次工具调用 → 直接使用该工具即可
- 具有步骤间逻辑关系的机械性多步骤任务 → 使用 `execute_code`
- 需要用户交互的任务 → 子代理无法使用 `clarify` 功能
- 简单的文件编辑 → 直接操作即可
- 需要持续运行且必须在会话关闭或进程重启后仍能继续的任务 → 使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。顶层委派虽为异步操作，但仍局限于当前进程内部。

---

## 并行研究模式

同时研究三个主题，并获取结构化的汇总结果：

```
Research these three topics in parallel:
1. Current state of WebAssembly outside the browser
2. RISC-V server chip adoption in 2025
3. Practical quantum computing applications

Focus on recent developments and key players.
```

在幕后，Hermes 使用了：

```python
delegate_task(tasks=[
    {
        "goal": "Research WebAssembly outside the browser in 2025",
        "context": "Focus on: runtimes (Wasmtime, Wasmer), cloud/edge use cases, WASI progress"
    },
    {
        "goal": "Research RISC-V server chip adoption",
        "context": "Focus on: server chips shipping, cloud providers adopting, software ecosystem"
    },
    {
        "goal": "Research practical quantum computing applications",
        "context": "Focus on: error correction breakthroughs, real-world use cases, key companies"
    }
])
```

这三个组件会同时运行。每个子代理都会独立地在网络上进行搜索，并返回相应的总结内容。随后，主代理会将这些信息整合成一份条理清晰的汇报。  

---

## 模式：代码审查

将安全审查任务委托给一个具有全新上下文认知的子代理，让它以毫无先入之见的态度来分析代码：

```
Review the authentication module at src/auth/ for security issues.
Check for SQL injection, JWT validation problems, password handling,
and session management. Fix anything you find and run the tests.
```

关键在于 `context` 字段——它必须包含子智能体所需的所有信息：

```python
delegate_task(
    goal="Review src/auth/ for security issues and fix any found",
    context="""Project at /home/user/webapp. Python 3.11, Flask, PyJWT, bcrypt.
    Auth files: src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py
    Test command: pytest tests/auth/ -v
    Focus on: SQL injection, JWT validation, password hashing, session management.
    Fix issues found and verify tests pass."""
)
```

:::warning 上下文问题
子智能体对您的对话**一无所知**，它们会从完全空白的状态开始工作。如果您要求其“修复我们之前讨论的错误”，子智能体根本无法知晓您指的是哪个错误。因此，请务必明确提供文件路径、错误信息、项目结构以及相关约束条件。
:::

---

## 模式：对比多种方案

同时评估解决同一问题的多种方法，进而选出最优方案：

```
I need to add full-text search to our Django app. Evaluate three approaches
in parallel:
1. PostgreSQL tsvector (built-in)
2. Elasticsearch via django-elasticsearch-dsl
3. Meilisearch via meilisearch-python

For each: setup complexity, query capabilities, resource requirements,
and maintenance overhead. Compare them and recommend one.
```

每个子智能体都会独立研究一个选项。由于它们彼此隔离，因此不会发生交叉干扰——每项评估都仅依据其自身优势来判定。父智能体则会收集这三份总结并加以对比。

---

## 模式：多文件重构

将大型重构任务分配给多个并行工作的子智能体，每个智能体负责处理代码库中的不同部分：

```python
delegate_task(tasks=[
    {
        "goal": "Refactor all API endpoint handlers to use the new response format",
        "context": """Project at /home/user/api-server.
        Files: src/handlers/users.py, src/handlers/auth.py, src/handlers/billing.py
        Old format: return {"data": result, "status": "ok"}
        New format: return APIResponse(data=result, status=200).to_dict()
        Import: from src.responses import APIResponse
        Run tests after: pytest tests/handlers/ -v"""
    },
    {
        "goal": "Update all client SDK methods to handle the new response format",
        "context": """Project at /home/user/api-server.
        Files: sdk/python/client.py, sdk/python/models.py
        Old parsing: result = response.json()["data"]
        New parsing: result = response.json()["data"] (same key, but add status code checking)
        Also update sdk/python/tests/test_client.py"""
    },
    {
        "goal": "Update API documentation to reflect the new response format",
        "context": """Project at /home/user/api-server.
        Docs at: docs/api/. Format: Markdown with code examples.
        Update all response examples from old format to new format.
        Add a 'Response Format' section to docs/api/overview.md explaining the schema."""
    }
])
```

:::提示
每个子智能体都会拥有独立的终端会话。只要它们编辑的文件不同，就可以在同一个项目目录下并行工作而互不干扰。如果有两个子智能体可能需要修改同一文件，则应在并行处理完成后由您亲自处理该文件。
:::

---

## 模式：收集数据后再进行分析

先使用 `execute_code` 功能进行机械式的数据收集，再将需要大量逻辑推理的分析任务交由其他智能体处理：

```python
# Step 1: Mechanical gathering (execute_code is better here — no reasoning needed)
execute_code("""
from hermes_tools import web_search, web_extract

results = []
for query in ["AI funding Q1 2026", "AI startup acquisitions 2026", "AI IPOs 2026"]:
    r = web_search(query, limit=5)
    for item in r["data"]["web"]:
        results.append({"title": item["title"], "url": item["url"], "desc": item["description"]})

# Extract full content from top 5 most relevant
urls = [r["url"] for r in results[:5]]
content = web_extract(urls)

# Save for the analysis step
import json
with open("/tmp/ai-funding-data.json", "w") as f:
    json.dump({"search_results": results, "extracted": content["results"]}, f)
print(f"Collected {len(results)} results, extracted {len(content['results'])} pages")
""")

# Step 2: Reasoning-heavy analysis (delegation is better here)
delegate_task(
    goal="Analyze AI funding data and write a market report",
    context="""Raw data at /tmp/ai-funding-data.json contains search results and
    extracted web pages about AI funding, acquisitions, and IPOs in Q1 2026.
    Write a structured market report: key deals, trends, notable players,
    and outlook. Focus on deals over $100M."""
)
```

这通常是最高效的模式：`execute_code` 能以较低成本处理 10 次及以上的连续工具调用，随后子代理便能在清晰的上下文环境中执行那项耗时的推理任务。

---

## 继承的工具访问权限

子代理会继承父代理已启用的工具集。由于 `delegate_task` 不接受面向模型的 `toolsets` 参数，因此被委托的任务无法获得父代理所不具备的功能。当需要网络、终端、文件或其他访问权限的任务被委托时，需在对话开始前先配置好父代理的工具。Hermes 仍会屏蔽诸如 `clarify`、`memory` 和 `send_message` 等被子代理屏蔽的工具；子代理则保留 `execute_code` 以用于程序化的工具调用。

---

## 约束条件

- **默认 10 个并行任务**：批次处理默认同时运行 10 个子代理（可通过 config.yaml 中的 `delegation.max_concurrent_children` 参数进行配置，无上限限制，仅下限为 1）。
- **嵌套委托为可选功能**：默认情况下，最底层的子代理无法调用 `delegate_task`、`clarify`、`memory` 或 `execute_code`。编排型子代理（`role="orchestrator"`）虽保留了 `delegate_task` 以用于进一步委托，但仅当 `delegation.max_spawn_depth` 的值高于默认的 1 时才允许（下限为 1，无上限）；其余三种功能仍会被屏蔽。如需全局禁用该功能，可设置 `delegation.orchestrator_enabled: false`。

### 调整并行度与嵌套深度

| 配置项 | 默认值 | 取值范围 | 效果 |
|--------|---------|-------|------|
| `max_concurrent_children` | 10 | >=1 | 每次调用 `delegate_task` 时允许的并行任务数量 |
| `max_spawn_depth` | 1 | >=1 | 允许嵌套代理的层级深度 |

示例：运行30个并行工作进程并使用嵌套子代理：

```yaml
delegation:
  max_concurrent_children: 30
  max_spawn_depth: 2
```

- **独立终端**——每个子代理都会拥有独立的终端会话，具备各自的工作目录和状态。  
- **无对话历史**——子代理仅能看到父代理在调用 `delegate_task` 时传递的 `goal` 和 `context`。  
- **默认迭代次数为250次**——对于由简单任务构成的任务组，可在 `config.yaml` 中将 `delegation.max_iterations` 设置得更低，以节省成本。  
- **非持久化**——顶层委托任务在后台运行，并在稍后返回结果，但它仍与对应的会话及Hermes进程绑定。若会话关闭、执行 `/stop`、`/new` 指令或进程重启，正在进行中的任务可能会被取消或卡住。对于那些必须跨越这些边界仍能正常运行的任务，建议使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。  

---

## 小贴士

**目标描述要具体明确**。“修复错误”这样的表述过于模糊。而“修复 api/handlers.py 第47行的 TypeError，该错误源于 process_request() 函数从 parse_body() 接收到的值为 None”则能为子代理提供足够的操作依据。

**务必包含文件路径**。子代理并不知道你的项目结构，因此请始终提供相关文件的绝对路径、项目根目录以及测试命令的完整路径。

**利用委托实现上下文隔离**。有时你需要全新的视角来解决问题。通过委托任务，你可以更清晰地阐述问题，而子代理在处理问题时也不会受到你在前期对话中形成的各种预设影响。

**检查结果**。子代理的总结仅属于概要性质，不可完全依赖。如果子代理称“已修复错误且测试通过”，建议自行运行测试或查看代码差异，以确认实际情况。

**故障会被及时呈现。** 当某个子代理发生故障（如提供程序错误、超时或崩溃）时，无论是否关闭了工具进度显示，都会在 CLI 授权树中以及网关平台的聊天消息中以简洁的一行提示展示相关信息：`⚠️ 子代理失败 — "你的目标": <原因>`。同时，父代理也会在工具结果中收到完整的错误信息。

---

*如需了解完整的授权参考资料——包括所有参数、ACP 集成及高级配置选项——请参阅 [子代理授权](/user-guide/features/delegation)。*
