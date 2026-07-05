# 上下文压缩与缓存机制

Hermes Agent采用了双重压缩系统以及Anthropic提示词缓存技术，从而在长时间的对话中高效地管理上下文窗口的使用情况。

相关源文件：`agent/context_engine.py`（抽象基类）、`agent/context_compressor.py`（默认压缩引擎）、`agent/prompt_caching.py`、`gateway/run.py`（会话管理功能）、`run_agent.py`（包含 `_compress_context` 相关功能）

## 可插拔的上下文引擎

上下文管理功能基于 `ContextEngine` 抽象基类实现（位于 `agent/context_engine.py`）。系统内置的 `ContextCompressor` 是默认的压缩引擎，但用户可以通过插件替换为其他类型的引擎（例如无损上下文管理引擎）。

```yaml
context:
  engine: "compressor"    # default — built-in lossy summarization
  engine: "lcm"           # example — plugin providing lossless context
```

该引擎负责以下功能：  
- 决定何时触发压缩操作（`should_compress()`）  
- 执行压缩操作（`compress()`）  
- 可选地提供代理可调用的工具（例如 `lcm_grep`）  
- 通过 API 响应跟踪令牌使用情况  

引擎的选择通过 `config.yaml` 中的 `context.engine` 参数进行配置。选择顺序如下：  
1. 检查 `plugins/context_engine/<名称>/` 目录  
2. 检查通用插件系统（`register_context_engine()`）  
3. 最终回退到内置的 `ContextCompressor`  

插件引擎**绝不会自动激活**——用户必须明确将 `context.engine` 设置为对应插件的名称。默认值 `"compressor"` 始终使用内置引擎。  

可通过 `hermes plugins` → Provider Plugins → Context Engine 进行配置，或直接编辑 `config.yaml` 文件。  

如需构建上下文引擎插件，请参阅 [上下文引擎插件](/developer-guide/context-engine-plugin)。  

## 双重压缩系统  

Hermes 拥有两个独立运行的压缩层：

```
                     ┌──────────────────────────┐
  Incoming message   │   Gateway Session Hygiene │  Fires at 85% of context
  ─────────────────► │   (pre-agent, rough est.) │  Safety net for large sessions
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │   Agent ContextCompressor │  Fires at 50% of context (default)
                     │   (in-loop, real tokens)  │  Normal context management
                     └──────────────────────────┘
```

### 1. 网关会话容量限制（85%阈值）

该功能位于 `gateway/run.py` 文件中（可搜索 `Session hygiene: auto-compress`）。它是一道**安全防护机制**，在智能体处理消息之前运行，旨在防止因对话轮次之间会话数据积累过多（例如在 Telegram/Discord 中过夜累积）而导致的 API 错误。

- **阈值**：固定为模型上下文长度的 85%
- **Token 来源**：优先使用上一轮对话中 API 返回的实际 Token 数值；若无法获取，则采用基于字符数的粗略估算方法（`estimate_messages_tokens_rough`）
- **触发条件**：仅当 `len(history) >= 4` 且压缩功能已启用时才会触发
- **作用**：用于检测那些已超出智能体自身压缩机制处理范围的会话数据

设置较高的网关会话容量阈值是为了与智能体的压缩机制形成区分。若将阈值设为 50%（与智能体相同），则会在长时间运行的网关会话中每轮对话都过早触发压缩操作。

### 2. 智能体上下文压缩器（50%阈值，可配置）

该功能位于 `agent/context_compressor.py` 文件中。它是**主要的压缩系统**，在智能体的工具处理循环中运行，并能够获取 API 返回的精确 Token 数值。

## 配置方式

所有压缩相关设置均从 `config.yaml` 文件中的 `compression` 键下读取：

```yaml
compression:
  enabled: true              # Enable/disable compression (default: true)
  threshold: 0.50            # Fraction of context window (default: 0.50 = 50%)
  target_ratio: 0.20         # How much of threshold to keep as tail (default: 0.20)
  protect_last_n: 20         # Minimum protected tail messages (default: 20)
  codex_gpt55_autoraise: true  # gpt-5.5 on Codex OAuth: raise trigger to 85% (default: true)
  codex_gpt55_autoraise_notice: true  # Show the one-time autoraise notice (default: true)

# Summarization model/provider configured under auxiliary:
auxiliary:
  compression:
    model: null              # Override model for summaries (default: auto-detect)
    provider: auto           # Provider: "auto", "openrouter", "nous", "main", etc.
    base_url: null           # Custom OpenAI-compatible endpoint
```

### 参数详情

| 参数 | 默认值 | 取值范围 | 说明 |
|-----------|---------|----------|------|
| `threshold` | `0.50` | 0.0-1.0 | 当提示词token数 ≥ `threshold × context_length`时触发压缩操作 |
| `target_ratio` | `0.20` | 0.10-0.80 | 用于控制尾部保护所需的token预算：`threshold_tokens × target_ratio` |
| `protect_last_n` | `20` | ≥1 | 总是会保留的最少近期消息数量 |
| `protect_first_n` | `3` | （固定值） | 系统提示词及首次对话内容将始终被保留 |
| `codex_gpt55_autoraise` | `true` | 布尔值 | 对通过ChatGPT Codex OAuth接口使用的gpt-5.5模型，将触发阈值提升至85%（详见下文）。若设置为`false`，则保持全局默认阈值 |
| `codex_gpt55_autoraise_notice` | `true` | 布尔值 | 显示针对Codex gpt-5.5模型的临时阈值提升提示。若设置为`false`，则仍维持85%的触发阈值，但不会显示相关提示信息 |

### Codex gpt-5.5模型的阈值提升机制

ChatGPT Codex OAuth后端将gpt-5.5模型的上下文窗口大小上限设定为**272K**
（而在OpenAI的直接API及OpenRouter平台上，同一接口的上下文窗口为105万token；
在GitHub Copilot平台则为40万token）。在默认50%的触发阈值下，压缩操作会在上下文窗口达到约136K时触发——这仅相当于模型实际可用空间的一半。当当前使用的是Codex OAuth接口（`provider: openai-codex`）且模型为gpt-5.5时，Hermes会将触发阈值提升至**85%**（约231K），并显示一条一次性提示信息，同时提供取消该设置的命令。此机制仅适用于该特定接口；在其他提供商上使用的gpt-5.5模型则仍遵循全局默认阈值。如需恢复为全局默认阈值：

```bash
hermes config set compression.codex_gpt55_autoraise false
```

若要保持85%的自动提升比例，同时仅隐藏一次性通知：

```bash
hermes config set compression.codex_gpt55_autoraise_notice false
```

### 计算值（基于默认参数下的200万上下文模型）

```
context_length       = 200,000
threshold_tokens     = 200,000 × 0.50 = 100,000
tail_token_budget    = 100,000 × 0.20 = 20,000
max_summary_tokens   = min(200,000 × 0.05, 12,000) = 10,000
```

:::note 阈值是根据主模型的上下文窗口确定的。
`threshold_tokens` 的值始终为 `threshold × context_length`，其中 `context_length` 指的是**主智能体模型**的上下文窗口大小，而非辅助/摘要模型的窗口大小。对于上下文窗口为 262,144 个令牌的模型，在默认阈值 `0.50` 的情况下，该阈值为 `262,144 × 0.50 = 131,072`。这一数值与常见的“128K 上下文”相近，纯属百分比设定所致，并不意味着触发压缩的是辅助模型的窗口大小。辅助模型的上下文窗口属于另一个独立考量范畴——关于它如何影响摘要的生成能力而非压缩触发的时机，请参阅下方的“摘要模型上下文长度”警告说明。:::


## 压缩算法

`ContextCompressor.compress()` 方法采用四阶段算法：

### 第一阶段：剔除旧工具输出结果（操作简单，无需调用大语言模型）

位于受保护区域之外的旧工具输出结果（长度超过 200 个字符）将被替换为：
```
[Old tool output cleared to save context space]
```

这是一项低成本的预处理功能，能够有效节省大量令牌，避免因冗长的工具输出（如文件内容、终端输出及搜索结果）而造成的浪费。

### 第二阶段：确定处理范围

```
┌─────────────────────────────────────────────────────────────┐
│  Message list                                               │
│                                                             │
│  [0..2]  ← protect_first_n (system + first exchange)        │
│  [3..N]  ← middle turns → SUMMARIZED                        │
│  [N..end] ← tail (by token budget OR protect_last_n)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

消息尾部的保护机制是基于**令牌预算**的：从消息末尾开始向后遍历，不断累积令牌，直到预算耗尽。如果按此方式无法保护足够多的消息，系统则会回退到固定的`protect_last_n`条消息保护策略。

边界处理会进行对齐，以避免拆分`tool_call`与`tool_result`组。`_align_boundary_backward()`方法会依次检查连续的`tool_result`，从而找到对应的父级助手消息，确保各组结构完整。

### 第三阶段：生成结构化摘要

:::warning 摘要模型的上下文长度限制
摘要模型的上下文窗口**必须至少**与主智能体模型的上下文窗口大小相当。中间部分的全部内容会通过一次`call_llm(task="compression")`调用发送给摘要模型。如果摘要模型的上下文容量不足，API会返回上下文长度过大的错误——`_generate_summary()`函数会捕获该错误，记录警告信息，并返回`None`值。此时压缩器将直接丢弃中间部分的对话内容而不会生成摘要，从而导致对话上下文丢失。这是导致压缩质量下降的最常见原因。
:::

中间部分的对话内容会通过辅助大语言模型，并借助结构化模板进行摘要生成：

```
## Goal
[What the user is trying to accomplish]

## Constraints & Preferences
[User preferences, coding style, constraints, important decisions]

## Progress
### Done
[Completed work — specific file paths, commands run, results]
### In Progress
[Work currently underway]
### Blocked
[Any blockers or issues encountered]

## Key Decisions
[Important technical decisions and why]

## Relevant Files
[Files read, modified, or created — with brief note on each]

## Next Steps
[What needs to happen next]

## Critical Context
[Specific values, error messages, configuration details]
```

摘要部分的字数会根据需要压缩的内容量动态调整：
- 计算公式：`内容令牌数 × 0.20`（即常量 `_SUMMARY_RATIO`）
- 最小值：2,000 个令牌
- 最大值：`min(上下文长度 × 0.05, 12,000)` 个令牌

### 第四阶段：整合压缩后的消息

压缩后的消息列表包含以下内容：
1. 主要消息（首次压缩时，系统提示中会附加相关说明）
2. 摘要消息（为避免连续出现相同角色，会选择不同的角色）
3. 尾部消息（保持原样不变）

由 `_sanitize_tool_pairs()` 函数负责清理那些孤立的 `tool_call/tool_result` 对：
- 若工具结果引用了已被移除的调用，则该结果会被删除
- 若工具调用的结果已被移除，则会注入虚拟结果

### 迭代式重新压缩

在后续的压缩过程中，之前的摘要内容会被传递给大语言模型，并附带**更新**该摘要的指令，而非从头开始生成新的摘要。这种方式能够保留多次压缩过程中的信息——旧信息会从“处理中”状态转为“已完成”状态，新的进展会被添加进来，而过时的信息则会被移除。

压缩器实例中的 `_previous_summary` 字段用于存储上一次生成的摘要文本，以实现这一功能。

## 压缩前/后示例

### 压缩前（45条消息，约95,000个令牌）

```
[0] system:    "You are a helpful assistant..." (system prompt)
[1] user:      "Help me set up a FastAPI project"
[2] assistant: <tool_call> terminal: mkdir project </tool_call>
[3] tool:      "directory created"
[4] assistant: <tool_call> write_file: main.py </tool_call>
[5] tool:      "file written (2.3KB)"
    ... 30 more turns of file editing, testing, debugging ...
[38] assistant: <tool_call> terminal: pytest </tool_call>
[39] tool:      "8 passed, 2 failed\n..."  (5KB output)
[40] user:      "Fix the failing tests"
[41] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[42] tool:      "import pytest\n..."  (3KB)
[43] assistant: "I see the issue with the test fixtures..."
[44] user:      "Great, also add error handling"
```

### 压缩后（25条消息，约45K个标记）

```
[0] system:    "You are a helpful assistant...
               [Note: Some earlier conversation turns have been compacted...]"
[1] user:      "Help me set up a FastAPI project"
[2] assistant: "[CONTEXT COMPACTION] Earlier turns were compacted...

               ## Goal
               Set up a FastAPI project with tests and error handling

               ## Progress
               ### Done
               - Created project structure: main.py, tests/, requirements.txt
               - Implemented 5 API endpoints in main.py
               - Wrote 10 test cases in tests/test_api.py
               - 8/10 tests passing

               ### In Progress
               - Fixing 2 failing tests (test_create_user, test_delete_user)

               ## Relevant Files
               - main.py — FastAPI app with 5 endpoints
               - tests/test_api.py — 10 test cases
               - requirements.txt — fastapi, pytest, httpx

               ## Next Steps
               - Fix failing test fixtures
               - Add error handling"
[3] user:      "Fix the failing tests"
[4] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[5] tool:      "import pytest\n..."
[6] assistant: "I see the issue with the test fixtures..."
[7] user:      "Great, also add error handling"
```


## 提示词缓存（Anthropic）

代码来源：`agent/prompt_caching.py`

该功能通过缓存对话开头部分，可在多轮对话中将输入token成本降低约75%。它利用了Anthropic的`cache_control`断点机制。

### 策略：system_and_3

Anthropic允许每个请求最多设置4个`cache_control`断点。Hermes则采用“system_and_3”策略：

```
Breakpoint 1: System prompt           (stable across all turns)
Breakpoint 2: 3rd-to-last non-system message  ─┐
Breakpoint 3: 2nd-to-last non-system message   ├─ Rolling window
Breakpoint 4: Last non-system message          ─┘
```

### 工作原理

`apply_anthropic_cache_control()`函数会对消息内容进行深度复制，并注入`cache_control`标记：

```python
# Cache marker format
marker = {"type": "ephemeral"}
# Or for 1-hour TTL:
marker = {"type": "ephemeral", "ttl": "1h"}
```

标记的添加方式会因内容类型而异：

| 内容类型 | 标记的放置位置 |
|-----------|----------------|
| 字符串内容 | 会被转换为 `[{"type": "text", "text": ..., "cache_control": ...}]` |
| 列表内容 | 会添加到最后一个元素的字典中 |
| 无/空内容 | 以 `msg["cache_control"]` 的形式添加 |
| 工具消息 | 以 `msg["cache_control"]` 的形式添加（仅限原生 Anthropic） |

### 考虑缓存的设计模式

1. **稳定的系统提示词**：系统提示词是第一个断点，并会在所有对话轮次中被缓存。避免在对话进行过程中修改它（压缩功能仅在首次压缩时才会附加说明）。

2. **消息顺序很重要**：缓存命中需要前缀匹配。如果在中间添加或删除消息，将会使之后的所有内容缓存失效。

3. **压缩与缓存的交互**：经过压缩后，被压缩区域的缓存会失效，但系统提示词缓存仍然有效。通过滚动3条消息的窗口，可在1-2轮对话内重新建立缓存。

4. **TTL设置**：默认值为 `5m`（5分钟）。对于用户会在各轮对话之间休息的长时间会话，可设置为 `1h`。

5. **模型标识也是缓存键的一部分**：提供商端的缓存是针对处理请求的模型（以及账户/API密钥）来划分范围的。如果在对话过程中更换模型——无论是通过显式的 `/model` 切换、主模型回退，还是将凭证池切换到其他账户——那么后续请求都将无法命中缓存，需要以全额输入费用重新读取整个对话历史。这是提供商端缓存机制的固有特性，Hermes 无法避免；因此，关于 `/model`、备用提供商及凭证池的用户文档都会包含相关成本警告。请勿添加会在会话中途悄悄更换模型或凭证的功能。

### 启用提示词缓存

在以下情况下，提示词缓存会自动启用：
- 模型为 Anthropic Claude 系列模型（通过模型名称识别）
- 提供商支持 `cache_control` 功能（原生 Anthropic API 或 OpenRouter）

```yaml
# config.yaml — TTL is configurable (must be "5m" or "1h")
prompt_caching:
  cache_ttl: "5m"
```

在启动时，CLI会显示缓存状态：
```
💾 Prompt caching: ENABLED (Claude via OpenRouter, 5m TTL)
```


## 上下文压力警告

中间级别的上下文压力警告已被移除（请参见 `run_agent.py` 文件中的迭代预算相关部分，其中说明：“不再显示中间级压力警告——因为这些警告会导致模型在处理复杂任务时过早放弃”）。当提示词令牌数量达到预设的 `compression.threshold` 值（默认为50%）且未提前发出警告时，系统会立即触发压缩机制；而作为第二道安全保障机制，当模型上下文窗口使用率达到85%时，也会启动会话清理功能。
