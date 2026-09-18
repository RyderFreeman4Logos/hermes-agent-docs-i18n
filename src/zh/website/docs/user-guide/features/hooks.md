---
sidebar_position: 6
title: "Event Hooks"
description: "Run custom code at key lifecycle points — log activity, send alerts, post to webhooks"
---

# 事件钩子

Hermes 提供了四种钩子系统，可在关键生命周期节点执行自定义代码：

| 系统 | 注册方式 | 执行环境 | 使用场景 |
|------|---------|---------|----------|
| **[网关钩子](#gateway-event-hooks)** | 通过 `~/.hermes/hooks/` 目录下的 `HOOK.yaml` 和 `handler.py` 文件注册 | 仅限网关 | 日志记录、警报发送、Webhook 接收 |
| **[插件钩子](#plugin-hooks)** | 在 [插件](/user-guide/features/plugins) 中使用 `ctx.register_hook()` 方法注册 | CLI + 网关 | 工具拦截、指标收集、规则校验 |
| **[Shell 钩子](#shell-hooks)** | 通过 `config.yaml` 配置文件中的 `hooks:` 块指定 Shell 脚本 | CLI + 网关 + 桌面端/TUI/控制台聊天界面 | 用于实现拦截、自动格式化、上下文注入等功能的即插即用脚本 |
| **[出站 Webhook](#outbound-webhooks)** | 通过 `~/.hermes/config.yaml` 文件中的 `hooks.outbound:` 列表配置 | CLI + 网关 | 将经过签名的生命周期事件推送到外部 HTTP 接口——如 CI 系统、监控面板或其他 Agent |

钩子回调出错时会被隔离并记录，而不会导致 Agent 崩溃。并非所有钩子都是被动的：指令/控制型钩子可以改变执行流程，转换型钩子可以替换内容，而 Shell 的 `pre_tool_call` 钩子则可以阻止操作或直接使其失败。

## 网关事件钩子

网关钩子会在网关处理消息时（如 Telegram、Discord、Slack、WhatsApp、Teams）自动触发，且不会影响主 Agent 的处理流程。

### 创建钩子

每个钩子都是 `~/.hermes/hooks/` 目录下的一个文件夹，其中包含两个文件：

```text
~/.hermes/hooks/
└── my-hook/
    ├── HOOK.yaml      # Declares which events to listen for
    └── handler.py     # Python handler function
```

#### HOOK.yaml 配置文件

```yaml
name: my-hook
description: Log all agent activity to a file
events:
  - agent:start
  - agent:end
  - agent:step
```

`events` 列表用于指定哪些事件会触发对应的处理程序。您可以选择订阅任意组合的事件，包括使用通配符如 `command:*`。 

#### handler.py

```python
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".hermes" / "hooks" / "my-hook" / "activity.log"

async def handle(event_type: str, context: dict):
    """Called for each subscribed event. Must be named 'handle'."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **context,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**处理规则：**
- 名称必须为 `handle`
- 接收 `event_type`（字符串类型）和 `context`（字典类型）作为参数
- 可以使用 `async def` 或常规的 `def` 函数定义——两种方式均有效
- 程序会捕获错误并记录日志，而不会导致代理程序崩溃

### 可用的事件类型

| Event | When it fires | Context keys |
|-------|---------------|--------------|
| `gateway:startup` | Gateway process starts | `platforms` (list of active platform names) |
| `session:start` | New messaging session created | `platform`, `user_id`, `session_id`, `session_key` |
| `session:end` | Session ended (before reset) | `platform`, `user_id`, `session_key` |
| `session:reset` | User ran `/new` or `/reset` | `platform`, `user_id`, `session_key` |
| `session:compress` | Context compression completed for a session | `platform`, `session_id`, `old_session_id` (empty when compacted in place), `in_place` (bool — `true` = transcript compacted on the same id, `false` = rotated from `old_session_id`), `compression_count` |
| `agent:start` | Agent begins processing a message | `platform`, `user_id`, `chat_id`, `thread_id` (forum-topic / thread root id; empty when not in a thread), `chat_type` (`"dm"` \| `"group"` \| `"forum"`; empty if unknown), `session_id`, `message` (truncated to 500 chars) |
| `agent:step` | Each iteration of the tool-calling loop | `platform`, `user_id`, `session_id`, `iteration`, `tool_names` |
| `agent:end` | Agent finishes processing | same keys as `agent:start`, plus `response` (truncated to 500 chars) |
| `reaction:added` | An emoji reaction was added to a message the bot can see (Slack adapter currently). Requires the `reactions:read` scope + the `reaction_added` bot event subscription; the bot must be a member of the channel. | `platform`, `reaction`, `user_id`, `item_user_id`, `item_type`, `channel_id`, `message_ts`, `team_id`, `event_ts`, `raw_event` |
| `reaction:removed` | An emoji reaction was removed from a message the bot can see. Requires the `reaction_removed` bot event subscription. | same shape as `reaction:added` |
| `command:*` | Any slash command executed | `platform`, `user_id`, `command`, `args` |

#### 通配符匹配

注册了 `command:*` 的处理程序会响应所有以 `command:` 开头的事件（如 `command:model`、`command:reset` 等）。只需一次订阅即可监控所有斜杠命令。

:::提示 线程回复
当 `chat_type == "forum"` 且 `thread_id` 不为空时，若处理程序要在同一个 Telegram 论坛主题中发布后续消息，应包含 `message_thread_id=int(thread_id)` 参数。
:::

### 示例

#### 长任务时的 Telegram 警报

当智能体执行步骤超过 10 步时，向自己发送一条消息：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: Alert when agent is taking many steps
events:
  - agent:step
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
import os
import httpx

THRESHOLD = 10
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_HOME_CHANNEL")

async def handle(event_type: str, context: dict):
    iteration = context.get("iteration", 0)
    if iteration == THRESHOLD and BOT_TOKEN and CHAT_ID:
        tools = ", ".join(context.get("tool_names", []))
        text = f"⚠️ Agent has been running for {iteration} steps. Last tools: {tools}"
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": text},
            )
```

#### 命令使用记录器

用于追踪使用了哪些斜杠命令：

```yaml
# ~/.hermes/hooks/command-logger/HOOK.yaml
name: command-logger
description: Log slash command usage
events:
  - command:*
```

```python
# ~/.hermes/hooks/command-logger/handler.py
import json
from datetime import datetime
from pathlib import Path

LOG = Path.home() / ".hermes" / "logs" / "command_usage.jsonl"

def handle(event_type: str, context: dict):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "command": context.get("command"),
        "args": context.get("args"),
        "platform": context.get("platform"),
        "user": context.get("user_id"),
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

#### 会话启动 Webhook

在新建会话时向外部服务发送 POST 请求：

```yaml
# ~/.hermes/hooks/session-webhook/HOOK.yaml
name: session-webhook
description: Notify external service on new sessions
events:
  - session:start
  - session:reset
```

```python
# ~/.hermes/hooks/session-webhook/handler.py
import httpx

WEBHOOK_URL = "https://your-service.example.com/hermes-events"

async def handle(event_type: str, context: dict):
    async with httpx.AsyncClient() as client:
        await client.post(WEBHOOK_URL, json={
            "event": event_type,
            **context,
        }, timeout=5)
```

### 教程：BOOT.md —— 在每个网关启动时运行启动检查清单

社区中流行的一种做法是将 Markdown 格式的检查清单保存在 `~/.hermes/BOOT.md` 文件中，让代理在每次网关启动时自动执行该清单。这种做法非常实用，比如“每次启动时检查夜间运行的 cron 任务是否出错，如有异常则通过 Discord 发送通知”，或者“汇总最近 24 小时的 deploy.log 内容并发布到 Slack 的 #ops 频道中”。

本教程将展示如何作为用户自定义钩子自行实现这一功能。Hermes 并未预置 BOOT.md 钩子——你需要根据自身需求来配置相应的行为。

#### 我们要实现的功能

1. 在 `~/.hermes/BOOT.md` 中创建一个包含自然语言启动指令的文件。
2. 创建一个在 `gateway:startup` 事件触发时执行的网关钩子，该钩子会使用网关已解析的模型/凭据启动一个一次性代理，进而执行 BOOT.md 中的指令。
3. 定义 `[SILENT]` 规则，以便在无需报告任何信息时让代理选择不发送消息。

#### 第一步：编写你的检查清单

创建 `~/.hermes/BOOT.md` 文件。其写作方式应如同你在向人工助手下达指令一般：

```markdown
# Startup Checklist

1. Run `hermes cron list` and check if any scheduled jobs failed overnight.
2. If any failed, summarize them for Discord #ops (the hook delivers your final response to its configured target).
3. Check if `/opt/app/deploy.log` has any ERROR lines from the last 24 hours. If yes, summarize them and include in the same report.
4. If nothing went wrong, reply with only `[SILENT]` so no message is sent.
```

智能体会将此内容视为其提示词的一部分，因此只要能用通俗语言描述的内容都可以——无论是工具调用、Shell命令、发送消息，还是文件摘要。 

#### 第2步：创建钩子

```text
~/.hermes/hooks/boot-md/
├── HOOK.yaml
└── handler.py
```

**`~/.hermes/hooks/boot-md/HOOK.yaml`**

```yaml
name: boot-md
description: Run ~/.hermes/BOOT.md on gateway startup
events:
  - gateway:startup
```

**`~/.hermes/hooks/boot-md/handler.py`**

```python
"""Run ~/.hermes/BOOT.md on every gateway startup."""

import logging
import threading
from pathlib import Path

logger = logging.getLogger("hooks.boot-md")

BOOT_FILE = Path.home() / ".hermes" / "BOOT.md"


def _build_prompt(content: str) -> str:
    return (
        "You are running a startup boot checklist. Follow the instructions "
        "below exactly.\n\n"
        "---\n"
        f"{content}\n"
        "---\n\n"
        "Execute each instruction. Put any user-facing summary in your "
        "final response — the hook delivers it to the configured channel "
        "(e.g. Discord or Slack); you do not send messages yourself.\n"
        "If nothing needs attention and there is nothing to report, reply "
        "with ONLY: [SILENT]"
    )


def _run_boot_agent(content: str) -> None:
    """Spawn a one-shot agent and execute the checklist.

    Uses the gateway's resolved model and runtime credentials so this works
    against custom endpoints, aggregators, and OAuth-based providers alike.
    """
    try:
        from gateway.run import _resolve_gateway_model, _resolve_runtime_agent_kwargs
        from run_agent import AIAgent

        agent = AIAgent(
            model=_resolve_gateway_model(),
            **_resolve_runtime_agent_kwargs(),
            platform="gateway",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            max_iterations=20,
        )
        result = agent.run_conversation(_build_prompt(content))
        response = (result.get("final_response", "") or "").strip()
        if response.upper() not in {"[SILENT]", "SILENT", "NO_REPLY", "NO REPLY"}:
            logger.info("boot-md completed: %s", response[:200])
        else:
            logger.info("boot-md completed (nothing to report)")
    except Exception as e:
        logger.error("boot-md agent failed: %s", e)


async def handle(event_type: str, context: dict) -> None:
    if not BOOT_FILE.exists():
        return
    content = BOOT_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return

    logger.info("Running BOOT.md (%d chars)", len(content))

    # Background thread so gateway startup isn't blocked on a full agent turn.
    thread = threading.Thread(
        target=_run_boot_agent,
        args=(content,),
        name="boot-md",
        daemon=True,
    )
    thread.start()
```

两条关键代码行如下：

- `_resolve_gateway_model()` 用于读取网关当前配置的模型。
- `_resolve_runtime_agent_kwargs()` 会以与普通网关相同的机制来解析提供者凭证——包括 API 密钥、基础 URL、OAuth 令牌以及凭证池。

若缺少这些功能，单纯的 `AIAgent()` 对象将回退到内置默认设置，从而导致对任何非默认端点的请求都出现 401 错误。

#### 第 3 步：进行测试

重启网关：

```bash
hermes gateway restart
```

查看日志：

```bash
hermes logs --follow --level INFO | grep boot-md
```

当代理返回如 `[SILENT]` 这样的静默令牌时，您应该会看到“正在运行 BOOT.md（N 个字符）”的提示，随后要么出现“boot-md 已完成：……”（说明代理的执行情况），要么显示“boot-md 已完成（无需报告）”。

若要禁用该检查清单，可删除 `~/.hermes/BOOT.md` 文件——即使该文件不存在，钩子仍会被加载，但会直接跳过相关操作。

#### 扩展该模式

- **支持时间安排的检查清单**：在 BOOT.md 的指令中取消对 `datetime.now().weekday()` 的依赖（例如“如果是周一，则同时检查每周部署日志”）。由于这些指令为自由文本形式，只要代理能够理解的内容均可使用。
- **多个检查清单**：将钩子指向不同的文件（如 `STARTUP.md`、`MORNING.md` 等），并为每个文件创建独立的钩子目录。
- **非代理版本**：如果您不需要完整的代理循环，可直接跳过 `AIAgent`，让处理程序通过 `httpx` 直接发送固定格式的通知。这种方式成本更低、速度更快，且无需依赖任何提供方。

#### 为何未将其内置

Hermes 的早期版本曾将此功能作为内置钩子，在每个网关启动时自动以默认配置创建代理。这令使用自定义端点的用户感到意外，同时也让那些不知其正在运行的用户无法察觉该功能。将其作为需自行在钩子目录中实现的文档化模式，能让您清楚地了解其功能，并通过编写相应文件来选择是否启用。

### 工作原理

1. 在网关启动时，`HookRegistry.discover_and_load()` 会扫描 `~/.hermes/hooks/` 目录。  
2. 每个包含 `HOOK.yaml` 和 `handler.py` 文件的子目录都会被动态加载。  
3. 处理器会根据其声明的事件进行注册。  
4. 在每个生命周期节点，`hooks.emit()` 都会触发所有匹配的处理器。  
5. 任何处理器中的错误都会被捕获并记录——出现故障的钩子不会导致整个代理程序崩溃。

:::info
网关钩子仅在 **网关端**（Telegram、Discord、Slack、WhatsApp、Teams）触发。CLI 不会加载网关钩子。如需在所有场景下都能使用的钩子，请使用[插件钩子](#plugin-hooks)。
:::

## 插件钩子

[插件](/user-guide/features/plugins)可以注册在**CLI 和网关端**会话中都能触发的钩子。这些钩子可通过插件 `register()` 函数中的 `ctx.register_hook()` 以编程方式注册。

有关插件打包与注册的详细信息，请参阅
[插件指南](/docs/user-guide/features/plugins)。

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", my_tool_observer)
    ctx.register_hook("post_tool_call", my_tool_logger)
    ctx.register_hook("pre_llm_call", my_memory_callback)
    ctx.register_hook("post_llm_call", my_sync_callback)
    ctx.register_hook("on_session_start", my_init_callback)
    ctx.register_hook("on_session_end", my_cleanup_callback)
    # Kanban board lifecycle (dependency-wait blocking may fire inside its transaction):
    ctx.register_hook("kanban_task_claimed", my_claim_callback)     # dispatcher process
    ctx.register_hook("kanban_task_completed", my_done_callback)    # worker process
    ctx.register_hook("kanban_task_blocked", my_blocked_callback)   # worker process
```

**所有钩子的通用规则：**

- 回调函数接收**关键字参数**。为确保向后兼容，始终应接受 `**kwargs`。
- 回调函数抛出的异常会被记录并跳过，后续的回调仍会继续执行。
- 对于具有**超时限制**的钩子（如 `post_tool_call` / `pre_llm_call` 这类热路径观察器，以及 `pre_tool_call` 政策钩子）上的 Python 插件回调，如果其**阻塞时间**超过 `plugins.hook_callback_timeout` 的阈值（默认为 30 秒，设为 `0` 表示禁用，最大值为 600 秒），则该回调将被放弃且不会加入工作线程，从而使智能体循环能够继续运行。超时或仍在运行的 `pre_tool_call` 回调会导致操作**直接失败**（从而阻塞工具调用）；其他具有时间限制的钩子则会导致操作**被跳过**。那些有明确调用线程约定（如 `subagent_stop`）的钩子永远不会被放入超时处理工作线程中。Shell 钩子则各自拥有独立的单次调用超时设置。
- 下面的分类说明仅供参考：**观察器**类型会忽略返回值，**转换器**类型会接受第一个有效的字符串替换结果，而**指令/控制**类型钩子则会按照文档规定的格式处理返回值。插件中间件属于独立的注册表和接口，不属于另一种钩子类别。
- 如 `turn_id`、`api_request_id`、`task_id`、`session_id` 和 `api_call_count` 这类关联字段是特定于各钩子的，可能并不存在。应将这些标识符视为不可见数据。
- 运行时事件名称的有效性由 `hermes_cli.plugins.VALID_HOOKS` 决定。`hermes hooks list` 只列出已配置的 Shell/外部调用钩子，并非所有可用的事件；而 `hermes hooks test <event>` 命令仅在输入无效事件时才会显示有效事件列表。

### 对缓存安全的系统提示部分

那些需要持久且持续不断的指导功能的插件，可以注册一个“受限系统提示”模块，而无需在每一轮对话中都通过 `pre_llm_call` 注入相同的文本。

```python
def board_rules(session_info):
    return f"Apply the worker rules for profile {session_info['profile_name']}."

def register(ctx):
    ctx.register_system_prompt_section(
        "kanban-advanced.worker-rules",
        board_rules,                       # a string is also accepted
        position="after_memory",
        max_chars=4000,
    )
```

该契约的设计具有高度的约束性：

- ID为全局唯一的稳定标识符，长度在1至128个字符之间，仅能由字母、数字、`.`、`_`和`-`组成。重复的ID将被拒绝。
- `after_memory`是唯一的排序依据。各部分内容将按ID顺序排列，先于记忆/个人资料上下文呈现，后于会话元数据；插件无法重新排序或替换核心提示内容。
- 可调用函数会接收一个只读映射，其中包含`session_id`、`model`、`provider`、`platform`、`profile_name`和`cwd`等信息。该函数**每个新会话仅运行一次**。其生成的内容在压缩后会固定下来，进程重启或恢复后将从已保存的完整系统提示中读取；对于现有会话，不会重新读取插件状态。
- `max_chars`的限制为4,000个字符。所有插件部分内容加起来，包括其审核标题在内，总长度不得超过8,000个字符，且最多包含32个部分。空内容、非字符串类型、超出大小限制、超出预算或存在错误的部分会被跳过并给出警告，提示构建过程仍会继续。
- 每个被接受的插件部分都将在提示中明确标注名称，并在会话开始时记录下其所属插件、位置及字符数。

如需实现真正动态的每轮上下文处理，可使用`pre_llm_call`。该契约刻意未设置插件环境提示钩子：更改当前工作目录、分支或其他环境数据时，不得擅自修改会话中缓存的提示内容。此类钩子需要明确的调用方，且必须具备与固定/恢复安全机制一致的语义，才能被添加进来。

### 已发布的插件钩子目录

下方的有效载荷字段均为各调用方所提供的特定事件相关字段。为确保向后兼容性，`PluginManager`还会在每个插件钩子回调中添加`telemetry_schema_version="hermes.observer.v1"`这一标识。不过，这一旧版标记并不意味着所有钩子有效载荷都遵循相同的语义架构；新版本的契约会归属于其对应的特定事件或功能类别。

| Hook | Category | Exact timing and return behavior | Explicit payload fields | Privacy / sensitivity |
|---|---|---|---|---|
| [`pre_tool_call`](#pre_tool_call) | Directive/control | Once before execution; first valid `block` or `approve` directive wins, and `modify` returns are shallow-merged into the tool arguments. | `tool_name`, `args`, `task_id`, `session_id`, `tool_call_id`, `turn_id`, `api_request_id`, `middleware_trace` | Raw arguments may contain user content, paths, commands, or secrets. |
| `post_tool_call` | Observer | After blocked, error, or successful result; return ignored. | `tool_name`, `args`, `result`, `task_id`, `session_id`, `tool_call_id`, `turn_id`, `api_request_id`, `duration_ms`, `status`, `error_type`, `error_message`, `middleware_trace` | Result/error text may contain arbitrary tool or user content and secrets. |
| `transform_tool_result` | Transform | After `post_tool_call`, before conversation append; first string replaces the result. | `tool_name`, `args`, `result`, `task_id`, `session_id`, `tool_call_id`, `turn_id`, `api_request_id`, `duration_ms`, `status`, `error_type`, `error_message` | Exposes the full model-bound result and arguments. |
| `transform_terminal_output` | Transform | After bounded foreground process capture, before final output limiting; first string replaces output. | `command`, `output`, `returncode`, `task_id`, `env_type` | Command/output may contain credentials. |
| `pre_transcription` | Transform | Fired by the STT dispatcher after provider resolution and before any backend (built-in, command-type, or plugin-registered) is invoked; dict results are applied in registration order, last-writer-wins per field (`prompt`, `language`, `model`; `file_path` is read-only). | `file_path`, `provider`, `model`, `language`, `prompt`, `source` | The final prompt is uploaded to the configured STT provider with the audio — keep secrets out of hook returns. |
| `pre_llm_call` | Directive/control | Once per turn before the loop; all valid string/`{"context": ...}` returns are joined and injected into the user message. | `session_id`, `task_id`, `turn_id`, `user_message`, `conversation_history`, `is_first_turn`, `model`, `platform`, `parent_session_id`, `sender_id` | Full user message and conversation history. |
| `post_llm_call` | Observer | Successful, non-interrupted turn finalization; return ignored. | `session_id`, `task_id`, `turn_id`, `user_message`, `assistant_response`, `conversation_history`, `model`, `platform` | Full prompt, response, and history. |
| `transform_llm_output` | Transform | Before `post_llm_call` and final delivery; first non-empty string replaces the response. | `response_text`, `session_id`, `model`, `platform` | Full final assistant text. |
| `pre_verify` | Directive/control | At the bounded edited-code verify gate; first valid continue/block-stop directive keeps the turn going. | `session_id`, `platform`, `model`, `coding`, `attempt`, `final_response`, `changed_paths` | Draft response and changed paths. |
| `pre_api_request` | Observer | Per provider attempt, immediately before the request; return ignored. | `task_id`, `turn_id`, `api_request_id`, `session_id`, `user_message`, `conversation_history`, `platform`, `model`, `provider`, `base_url`, `api_mode`, `api_call_count`, `retry_count`, `request_messages`, `message_count`, `tool_count`, `approx_input_tokens`, `request_char_count`, `max_tokens`, `started_at`, `middleware_trace`, `request` | High sensitivity: legacy `user_message`, `conversation_history`, and `request_messages` are intentionally raw; prefer sanitized `request`. |
| `post_api_request` | Observer | After normalized provider success; return ignored. | `task_id`, `turn_id`, `api_request_id`, `session_id`, `platform`, `model`, `provider`, `base_url`, `api_mode`, `api_call_count`, `api_duration`, `started_at`, `ended_at`, `finish_reason`, `message_count`, `response_model`, `response`, `usage`, `assistant_message`, `assistant_content_chars`, `assistant_tool_call_count` | Sanitized `response` is available, but raw normalized `assistant_message` may contain model/user content; `usage` is accounting data. |
| `api_request_error` | Observer | On each failed provider attempt; return ignored. | `task_id`, `turn_id`, `api_request_id`, `session_id`, `platform`, `model`, `provider`, `base_url`, `api_mode`, `api_call_count`, `api_duration`, `started_at`, `ended_at`, `status_code`, `retry_count`, `max_retries`, `retryable`, `reason`, `error`, `request` | Error text may contain provider/user data; `request` is intended to be sanitized. |
| `on_stream_start` | Observer | Dispatched when a streaming LLM response begins; delivered off the token path via a host-owned bounded queue with one worker per callback; return ignored. | `turn_id`, `iteration`, `session_id`, `model`, `provider`, `surface` | Identifiers and routing metadata only. |
| `on_stream_delta` | Observer | Dispatched per normalized streaming text delta via the bounded observer queue; a stalled callback drops only its own oldest events; return ignored. | `delta`, `kind` (`text` or `reasoning`), `turn_id`, `iteration`, `session_id`, `model`, `provider`, `surface` | Delta text is raw model output; reasoning deltas require the `plugins.stream_reasoning_deltas` opt-in. |
| `on_stream_end` | Observer | Dispatched when a streaming response finishes or errors, after the stream closes; return ignored. | `final_text`, `finished`, `error`, `turn_id`, `iteration`, `session_id`, `model`, `provider`, `surface` | Full assembled response text; error text may include provider data. |
| `on_interim_message` | Observer | Dispatched when a mid-loop assistant message is surfaced before the final answer (streaming or non-streaming); return ignored. | `text`, `already_streamed`, `turn_id`, `iteration`, `session_id`, `model`, `provider`, `surface` | Full interim assistant text. |
| `transform_api_error_classification` | Transform | On each failed provider attempt, at the top of the built-in classifier; all callbacks run, then the first dict with a valid `reason` wins (run-all-then-pick-first), and skipped valid results log a runtime warning. Python plugins only. | `provider`, `model`, `status_code`, `error_type`, `error_code`, `error_message`, `error_body`, `error`, `approx_tokens`, `context_length`, `num_messages` | `error_message` and `error_body` may contain raw provider/user data. |
| `on_session_start` | Observer | First turn of a new session; return ignored. | `session_id`, `model`, `platform` | Identifiers and routing metadata only. |
| `on_session_end` | Observer | Canonically at each turn finalization; CLI/TUI exits have additional reduced legacy shapes. Return ignored. | Canonical: `session_id`, `task_id`, `turn_id`, `completed`, `failed`, `interrupted`, `turn_exit_reason`, `model`, `platform`; exit paths may add `reason`/`api_request_id` and omit fields. | IDs, model/platform, and outcome; canonical payload has no message body. |
| `on_session_finalize` | Observer | CLI/TUI/gateway teardown through `finalize_session`; gateway shutdown may finalize without a reset. Return ignored. | Surface-dependent `session_id`, `platform`, optionally `reason`, `old_session_id`, `new_session_id` | Session and routing identifiers. |
| `on_session_reset` | Observer | CLI/TUI session boundary and gateway after the replacement session exists; return ignored. | CLI: `session_id`, `platform`, `reason`; TUI: `session_id`, `platform`; gateway: those plus `reason`, `old_session_id`, `new_session_id` | Session and routing identifiers. |
| `on_skill_lifecycle` | Observer | After an authoritative skill-usage state change; return ignored. | `action`, `skill_name`, `provenance`, `task_id`, `session_id`, `use_count`, `reused`, `reuse_after_patch` | Exposes the local skill name and provenance. |
| `subagent_start` | Observer | Child constructed and about to run; return ignored. | `parent_session_id`, `parent_turn_id`, `parent_subagent_id`, `child_session_id`, `child_subagent_id`, `child_role`, `child_goal` | Child goal may contain user/project content. |
| `subagent_stop` | Observer | Child exit; return ignored. | `parent_session_id`, `parent_turn_id`, `child_session_id`, `child_role`, `child_summary`, `child_status`, `tool_call_history`, `duration_ms` | Summary and redacted tool-history metadata may reveal project structure. |
| `pre_gateway_dispatch` | Directive/control | Incoming non-internal message before auth/pairing/dispatch; first valid `skip`, `rewrite`, or `allow` controls flow. | `event`, `gateway`, `session_store` | Extremely privileged in-process objects expose inbound user/routing data and host handles. |
| `gateway_platform_event` | Observer | After the gateway's profile-scoped authorization succeeds, when a supported platform-native event is normalized at the gateway boundary (Telegram: reactions, message edits; Discord: message edits/deletes, thread created/renamed); return ignored. | `platform`, `event_type`, `payload` (event-type-specific dict — see the per-event contracts below) | Normalized plain-dict envelope only; raw SDK objects, adapter handles, and bot clients are never exposed. |
| `pre_command` | Observer | Recognized slash command about to be dispatched, before the handler runs, on CLI and gateway cold-path dispatch; return ignored in v1 (directive-shaped dicts are logged at debug). Gateway running-agent intercept commands (`/stop`, `/approve` during an active run) are deliberately excluded — control-plane escape hatches must stay outside plugin reach. | `surface` (`"cli"` \| `"gateway"`), `command` (canonical name), `alias_used`, `args_raw`, `session_key`, `platform` | `args_raw` may contain user content or secrets typed after the command. |
| `pre_approval_request` | Observer | Before prompted or smart approval; return ignored. | `command`, `description`, `pattern_key`, `pattern_keys`, `session_key`, `surface`, `turn_id`, `tool_call_id` | Command may contain secrets; smart observer preparation force-redacts, but surfaces do not all have identical redaction. |
| `post_approval_response` | Observer | After a decision, timeout, or gateway notification failure; return ignored. | `command`, `description`, `pattern_key`, `pattern_keys`, `session_key`, `surface`, `turn_id`, `tool_call_id`, `choice`; smart path may add `decided_by` | Same command sensitivity plus decision metadata. |
| `kanban_task_claimed` | Observer | After claim commit, in dispatcher process before worker spawn; return ignored. | `task_id`, `profile_name`, `board`, `assignee`, `run_id` | Board/task/profile/assignee identifiers. |
| `kanban_task_completed` | Observer | After completion and cleanup, usually in worker process; return ignored. | `task_id`, `profile_name`, `board`, `assignee`, `run_id`, `summary` | Summary may contain project/user content. |
| `kanban_task_blocked` | Observer | After a blocked transition; the dependency-wait path fires before its transaction exits. Return ignored. | `task_id`, `profile_name`, `board`, `assignee`, `run_id`, `reason` | Reason may contain project/user content. |
| `on_kanban_worker_spawned` | Observer | After `spawn_fn` returns and the worker PID is persisted; runs inside the dispatch lock, keep callbacks fast. Return ignored. | `task_id`, `profile_name`, `board`, `assignee`, `run_id`, `worker_pid`, `workspace_path` | `workspace_path` is a filesystem path and may reveal project layout or usernames. |
| `on_kanban_worker_exited` | Observer | Tick-derived: after `detect_crashed_workers` reclaims a dead-PID task and the reclaim commits. Return ignored. | `task_id`, `profile_name`, `board`, `assignee`, `run_id`, `worker_pid`, `exit_kind`, `exit_code`, `outcome`, `retry_status` | Identifiers and exit metadata only. |
| `on_kanban_worker_stale_claim` | Observer | After a TTL-expired claim is reclaimed; live-PID extensions don't fire. Return ignored. | `task_id`, `profile_name`, `board`, `assignee`, `run_id`, `worker_pid`, `heartbeat_stale`, `retry_status` | Identifiers and claim metadata only. |
| `on_kanban_task_updated` | Observer | After a committed task-field write outside the claim/complete/block lifecycle (assign, overrides, dashboard editors). Return ignored. | `task_id`, `profile_name`, `board`, `assignee`, `run_id`, `changed_fields` | `changed_fields` carries field names only, never values; the named title/body values in the board DB may contain user/project content. |
| `on_kanban_dispatch_tick` | Observer | Once per dispatcher tick, strictly after the dispatch lock is released; idle and contended ticks fire too. Return ignored. | `board`, `profile_name`, `dry_run`, `outcome`, `result` | `result` is the tick's `DispatchResult` and carries task ids, assignees, and workspace paths. |

### 流式输出钩子

这些仅用于监听的钩子允许插件获取流式的大型语言模型输出，以便用于性能监控、实时仪表板或文本转语音流程，且不会改变原始响应内容。这些输出通过主机管理的有限队列进行传递，每个已注册的回调函数对应一个后台工作进程，因此插件回调绝不会在消息处理路径中直接执行。如果某个回调出现阻塞，仅该回调对应的队列会满并丢弃其中最旧的待处理事件；其他监听器仍可独立地持续接收事件。

其注册方式与其他插件钩子完全相同：

```python
def on_delta(delta, kind, model, provider, **kwargs):
    if kind == "text":
        print(delta, end="", flush=True)

def register(ctx):
    ctx.register_hook("on_stream_delta", on_delta)
```

四个钩子共有的字段：

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `turn_id` | `str` | 可用的匿名轮次标识符 |
| `iteration` | `int` | 当前的 API 调用/工具循环次数 |
| `session_id` | `str` | 当前的 Hermes 会话 ID |
| `model` | `str` | 当前使用的模型标识符 |
| `provider` | `str` | 当前使用的提供者名称 |
| `surface` | `str` | 调用接口类型，例如 `cli`、`discord`、`telegram` |

其他字段：

| 钩子 | 额外字段 |
|------|----------|
| `on_stream_start` | 无 |
| `on_stream_delta` | `delta: str`，`kind: "text" | "reasoning"` |
| `on_stream_end` | `final_text: str`，`finished: bool`，`error: str | None` |
| `on_interim_message` | `text: str`，`already_streamed: bool` |

`on_interim_message` 在非流式响应之后也可能会被触发，因此仅注册该钩子并不会强制要求提供者通过流式传输进行响应。

默认情况下，推理过程中的增量数据不会暴露给插件。如需使用，需明确启用相应功能：

```yaml
plugins:
  stream_reasoning_deltas: true
```

返回值将被忽略。为保证数据流的处理速度，回调函数应自行将任务加入队列并尽快返回。异常会被记录下来，而不会中断数据流的传输。

---

### `pre_tool_call`

在每次工具执行**之前立即触发**——无论是内置工具还是插件工具均适用。

**回调函数签名：**

```python
def my_callback(tool_name: str, args: dict, task_id: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 即将执行的工具名称（例如 `"terminal"`、`"web_search"`、`"read_file"`） |
| `args` | `dict` | 模型传递给该工具的参数 |
| `task_id` | `str` | 会话/任务标识符；若未设置则为空字符串 |

**触发时机：** 在 `model_tools.py` 文件的 `handle_function_call()` 函数中，于工具处理程序执行之前触发。每次调用工具都会触发一次——如果模型同时调用3个工具，则会触发3次。

**返回值 —— 需要审批或直接返回结果：**

```python
return {"action": "block", "message": "Reason the tool call was blocked"}
# or
return {"action": "approve", "message": "Why approval is required", "rule_key": "optional:scope"}
```

第一个有效的指令将会被优先执行（先加载最先注册的 Python 插件，然后再加载 shell 钩子）。`block` 指令要求必须提供非空的 `message` 参数，并会直接以该文本作为错误信息返回给模型，从而终止工具的执行。`approve` 指令则会将请求转发至现有的人工审批流程；`message` 和 `rule_key` 为可选参数，若发生拒绝、超时或审批流程出错，则会直接终止处理。其他返回值将被忽略，因此现有的仅用于观察的回调函数仍可照常运行，不受影响。

**返回值——重写工具的参数：**

```python
return {"action": "modify", "args": {"new_string": "fixed content"}}
```

在工具执行之前，返回的 `args` 字典会与原始工具参数进行浅层合并。多个 `modify` 钩子会被依次应用——每个钩子的键值都会被合并到以原始参数为基础构建的累积字典中，因此，无论钩子 A 修改的是 `path` 还是钩子 B 修改的是 `content`，其修改内容都会被保留。如果有两个钩子试图修改同一个键，则后应用的钩子会覆盖之前的修改结果。

Shell 钩子同样支持与 Claude Code 兼容的格式：

```json
{"decision": "modify", "tool_input": {"new_string": "fixed content"}}
```

这两种格式在内部都会被标准化为 `{"action": "modify", "args": {...}}` 的结构。

如果某个 `pre_tool_call` 回调函数的执行时间超过了 `plugins.hook_callback_timeout` 的限制（或者仍在之前因超时而触发的处理流程中运行），Hermes 会**直接终止处理**：该工具调用会被超时消息阻断，而不会在没有做出策略决策的情况下继续执行。

**应用场景**：日志记录、审计追踪、工具调用计数、阻止危险操作、速率限制、按用户实施策略、参数净化、路径重写以及注入默认参数。

**示例——工具调用审计日志：**

```python
import json, logging
from datetime import datetime

logger = logging.getLogger(__name__)

def audit_tool_call(tool_name, args, task_id, **kwargs):
    logger.info("TOOL_CALL session=%s tool=%s args=%s",
                task_id, tool_name, json.dumps(args)[:200])

def register(ctx):
    ctx.register_hook("pre_tool_call", audit_tool_call)
```

**示例——对危险工具发出警告：**

```python
DANGEROUS = {"terminal", "write_file", "patch"}

def warn_dangerous(tool_name, **kwargs):
    if tool_name in DANGEROUS:
        print(f"⚠ Executing potentially dangerous tool: {tool_name}")

def register(ctx):
    ctx.register_hook("pre_tool_call", warn_dangerous)
```

### `post_tool_call`

在每次工具执行返回后**立即触发**。

**回调函数签名：**

```python
def my_callback(tool_name: str, args: dict, result: str, task_id: str,
                duration_ms: int, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 刚刚执行的工具名称 |
| `args` | `dict` | 模型传递给该工具的参数 |
| `result` | `str` | 工具的返回值（始终为 JSON 字符串） |
| `task_id` | `str` | 会话/任务标识符。若未设置则为空字符串 |
| `duration_ms` | `int` | 工具被调用的耗时，以毫秒为单位（通过在 `registry.dispatch()` 周围使用 `time.monotonic()` 进行测量） |

**触发时机：** 在 `model_tools.py` 文件的 `handle_function_call()` 函数中，工具的处理程序返回之后触发。每次调用工具都会触发一次。如果工具抛出了未处理的异常，则不会触发该事件（错误会被捕获并作为错误 JSON 字符串返回，此时 `post_tool_call` 会使用该错误字符串作为 `result` 参数被触发）。

**返回值：** 该参数将被忽略。

**应用场景：** 记录工具执行结果、收集指标数据、追踪工具的成功/失败率、生成延迟监控面板、设置针对不同工具的调用限额警报，以及在特定工具执行完成时发送通知。

**示例——追踪工具使用指标：**

```python
from collections import Counter, defaultdict
import json

_tool_counts = Counter()
_error_counts = Counter()
_latency_ms = defaultdict(list)

def track_metrics(tool_name, result, duration_ms=0, **kwargs):
    _tool_counts[tool_name] += 1
    _latency_ms[tool_name].append(duration_ms)
    try:
        parsed = json.loads(result)
        if "error" in parsed:
            _error_counts[tool_name] += 1
    except (json.JSONDecodeError, TypeError):
        pass

def register(ctx):
    ctx.register_hook("post_tool_call", track_metrics)
```

### `pre_llm_call`

该函数在每个回合开始、工具调用循环启动之前**仅触发一次**。所有有效的回调返回值会按照插件顺序进行汇总，随后被注入到当前回合的用户消息中。

**回调函数签名：**

```python
def my_callback(session_id: str, user_message: str, conversation_history: list,
                is_first_turn: bool, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 该轮对话中用户输入的原始消息（在应用任何技能处理之前） |
| `conversation_history` | `list` | 完整的消息列表副本（采用 OpenAI 格式：`[{"role": "user", "content": "..."}]`） |
| `is_first_turn` | `bool` | 若为新会话的第一个轮次则值为 `True`，后续轮次则为 `False` |
| `model` | `str` | 模型标识符（例如 `"anthropic/claude-sonnet-4.6"`） |
| `platform` | `str` | 会话运行的平台：`"cli"`、`"telegram"`、`"discord"` 等 |

**触发时机：** 在 `agent/turn_context.py` 文件中（即 `agent/conversation_loop.py` 中 `run_conversation()` 函数的轮次准备阶段），在上下文压缩之后、主 `while` 循环之前触发。每次调用 `run_conversation()` 都会触发一次（即每轮用户输入时触发一次），而非在工具循环中的每次 API 调用时都触发。

**返回值：** 如果回调函数返回一个包含 `"context"` 键的字典，或是一个非空的普通字符串，则该文本会被追加到当前轮次的用户消息中。若无需进行任何内容注入，则返回 `None`。

```python
# Inject context
return {"context": "Recalled memories:\n- User likes Python\n- Working on hermes-agent"}

# Plain string (equivalent)
return "Recalled memories:\n- User likes Python"

# No injection
return None
```

**上下文注入的位置：** 始终为**用户消息**，而非系统提示词。这样做有助于保留提示词缓存——由于系统提示词在多轮对话中保持不变，因此已缓存的标记可以被重复使用。系统提示词负责管理模型的行为引导、工具调用规则、人格设定以及各项技能。插件则会在用户输入的基础上补充上下文信息。

原始的用户消息`content`内容本身不会发生改变。为确保对话回放的准确性和提示词缓存的稳定性，Hermes可能会将包含插件注入的上下文的完整API格式消息，存储在对应记录的`api_content`侧边字段中。

当**多个插件**同时返回上下文时，它们的输出会按照插件发现顺序（即目录名称的字母顺序），通过双换行符连接在一起。

**应用场景：** 记忆回忆、RAG上下文注入、行为规范约束、每轮对话分析。

**示例——记忆回忆：**

```python
import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall(session_id, user_message, is_first_turn, **kwargs):
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None
        text = "Recalled context:\n" + "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None

def register(ctx):
    ctx.register_hook("pre_llm_call", recall)
```

**示例——保护机制：**

```python
POLICY = "Never execute commands that delete files without explicit user confirmation."

def guardrails(**kwargs):
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", guardrails)
```

### `post_llm_call`

该函数在**每轮对话结束后**触发一次，即工具调用循环完成且智能体已生成最终响应之后。仅会在**成功的对话轮次**中触发——若某轮对话被中断，则不会触发。

**回调函数签名：**

```python
def my_callback(session_id: str, user_message: str, assistant_response: str,
                conversation_history: list, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 用户在本轮对话中输入的原始消息 |
| `assistant_response` | `str` | 智能体在本轮对话中生成的最终文本回复 |
| `conversation_history` | `list` | 本轮对话结束后完整的消息记录副本 |
| `model` | `str` | 所使用的模型标识符 |
| `platform` | `str` | 会话运行的平台 |

**触发条件：** 在 `agent/turn_finalizer.py` 文件中的 `finalize_turn()` 函数内（该函数由 `agent/conversation_loop.py` 中的 `run_conversation()` 调用），在工具调用循环处理完最终回复后触发。该函数通过 `if final_response and not interrupted` 条件进行保护——因此当用户在对话中途中断，或智能体达到迭代次数限制且未生成回复时，不会触发此函数。

**返回值：** 无返回值。

**应用场景：** 将对话数据同步到外部内存系统、计算回复质量指标、记录对话摘要、触发后续操作。

**示例——同步至外部内存：**

```python
import httpx

MEMORY_API = "https://your-memory-api.example.com"

def sync_memory(session_id, user_message, assistant_response, **kwargs):
    try:
        httpx.post(f"{MEMORY_API}/store", json={
            "session_id": session_id,
            "user": user_message,
            "assistant": assistant_response,
        }, timeout=5)
    except Exception:
        pass  # best-effort

def register(ctx):
    ctx.register_hook("post_llm_call", sync_memory)
```

**示例——跟踪响应长度：**

```python
import logging
logger = logging.getLogger(__name__)

def log_response_length(session_id, assistant_response, model, **kwargs):
    logger.info("RESPONSE session=%s model=%s chars=%d",
                session_id, model, len(assistant_response or ""))

def register(ctx):
    ctx.register_hook("post_llm_call", log_response_length)
```

### `pre_verify`

该钩子在**智能体每次编辑代码后、编译完成之前**触发一次（位于内置的“停止时验证”机制之后）。它属于用户/插件策略控制机制：回调函数可以决定让智能体继续执行操作——比如进行进一步检查、暂缓处理或整理差异内容——而非让其直接停止。

Hermes 已内置的验证提示并非默认的 `pre_verify` 钩子。仅在编辑的代码缺乏最新的验证证据时，它才会作为基于证据的“停止时验证”提示的补充，因此不会产生第二个默认的继续执行路径。如需保持内置的简洁提示，可设置 `agent.verify_guidance: false`。

**回调函数签名：**

```python
def my_callback(session_id: str, platform: str, model: str, coding: bool,
                attempt: int, final_response: str, changed_paths: list, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `platform` | `str` | 会话运行的平台（如 `"cli"`、`"telegram"` 等） |
| `model` | `str` | 模型标识符 |
| `coding` | `bool` | 当前轮次是否处于编码模式（即在代码工作区中）——可基于此参数限定钩子的触发范围 |
| `attempt` | `int` | 该轮次已被触发的次数（首次为 0）——可通过此参数实现自我节流 |
| `final_response` | `str` | 智能体即将给出的答案 |
| `changed_paths` | `list` | 智能体在当前轮次中修改过的文件列表（已排序，此处始终非空） |

可通过检查 `coding` 参数将钩子限定在编码上下文中，并利用 `attempt` 参数实现单次触发效果（shell 钩子会同时读取 `.extra` 文件中的这两个参数），这与基于 `tool_name` 限定的 `pre_tool_call` 钩子的工作方式相同——因此你可以注册多个 `pre_verify` 钩子，每个钩子都只在其应触发的语境下执行。

**触发时机：** 在 `agent/conversation_loop.py` 文件中，即智能体准备接受最终答案、完成停止前验证之后的时刻——但仅限于当前轮次智能体确实修改了代码且已注册了至少一个 `pre_verify` 钩子的情形。

**返回值——用于让智能体继续运行：**

```python
return {"action": "continue", "message": "Run the formatter on your changes, then finish."}
```

`message` 会被作为一条虚拟用户轮次附加在后面，随后循环会再次启动。Claude-Code 的停止指令格式（`{"decision": "block", "reason": "..."}`，其中“阻止停止”意味着*继续执行*）也同样有效。若指令不包含任何消息或其他返回值，则该轮次即告结束。

**限制机制：** 单次轮次中连续的“继续”指令数量受 `agent.max_verify_nudges`（默认值为 3）的限制，因此那些始终要求继续执行的钩子函数永远无法使循环陷入死循环。在代理被持续提示时，尝试生成的答案会被保存在历史记录中，但不会显示给用户。

**确保操作的可重置性：** 由于钩子函数会在每次提示后重新触发，因此应基于 `attempt` 参数设置判断条件（`if attempt: return None`）；否则，系统将不断发送提示直至达到数量上限。

**应用场景：** 在创意迭代过程中暂缓执行测试或代码检查；要求某些路径必须通过检查；在生成变更日志条目之前阻止任务标记为“已完成”；运行针对特定项目的验证清单。

**示例——针对创意界面开发暂缓检查，限定范围且仅执行一次：**

```python
UI = (".tsx", ".jsx", ".css", ".scss")

def defer_ui_checks(coding, attempt, changed_paths, **kwargs):
    if attempt or not coding:
        return None  # one-shot, coding only
    if not all(p.endswith(UI) for p in changed_paths):
        return None  # only pure-UI edits
    return {
        "action": "continue",
        "message": "This is UI work — don't run tests/lints yet; ask the user to "
                   "eyeball it first, and clean the diff before any commit.",
    }

def register(ctx):
    ctx.register_hook("pre_verify", defer_ui_checks)
```

若需持续性的指导以优化内置的“缺失证据提示”功能，可使用 `agent.verify_guidance`。而对于那些无需通过验证机制来强制执行的更广泛的编码规范，建议在 `config.yaml` 中使用 `agent.coding_instructions` —— 该选项会随编码任务一同处理，且不会额外占用推理轮次。

---

### `transform_api_error_classification`

该函数会在每次 API 调用失败时触发一次，执行位置位于 `agent/error_classifier.classify_api_error()` 的最开头、内置处理流程之前。提供商插件可通过它来应对自身插件所特有的错误问题，而无需进行核心代码修改。这是一个会改变行为的功能（属于“转换”系列）：其返回的错误分类结果将决定后续是进行重试、数据压缩、凭证轮换还是启用备用路由。

回调函数会以关键字参数的形式接收解析后的错误上下文信息，包括 `provider`（在此为自身作用域）、`model`、`status_code`、`error_type`、`error_code`、`error_message`、`error_body`、`error`、`approx_tokens`、`context_length` 以及 `num_messages`。如需拒绝处理，可返回 `None`；若要处理该错误，则需返回一个字典。

```python
return {"reason": "model_not_found",   # required: a FailoverReason name
        "retryable": False, "should_fallback": True}  # optional recovery-hint overrides
```

调度机制采用“全部执行后再优先选择”的方式：所有回调函数都会被执行，失败情况会被隔离处理，且按注册顺序出现的第一个有效结果将胜出（虽有效但排名靠后的结果会记录运行时警告）。无效的字典数据及未知原因会导致对应处理被跳过，因此即使某个插件出现故障，也不会影响整体分类结果。

**隐私说明：** `error_message` 和 `error_body` 中可能包含未经过脱敏处理的提供方数据。**仅支持 Python 插件**——shell 格式的插件在配置解析阶段会被拒绝，并同时发出警告。

---

### `on_session_start`

在创建全新会话时**触发一次**。当用户在现有会话中发送第二条消息（即会话继续使用时）**不会触发**。

**回调函数签名：**

```python
def my_callback(session_id: str, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的唯一标识符 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的平台 |

**触发时机：** 在 `agent/conversation_loop.py` 文件的 `run_conversation()` 函数中，于新会话的第一个轮次——即系统提示语生成之后、工具调用循环开始之前。判断条件为 `if not conversation_history`（没有历史消息意味着是新会话）。

**返回值：** 该参数的值将被忽略。

**应用场景：** 初始化会话级状态、预热缓存、将会话注册到外部服务、记录会话启动时间。

**示例——初始化会话缓存：**

```python
_session_caches = {}

def init_session(session_id, model, platform, **kwargs):
    _session_caches[session_id] = {
        "model": model,
        "platform": platform,
        "tool_calls": 0,
        "started": __import__("datetime").datetime.now().isoformat(),
    }

def register(ctx):
    ctx.register_hook("on_session_start", init_session)
```

### `on_session_end`

无论对话执行结果如何，该回调都会在每次 `run_conversation()` 调用的**最后阶段**被触发。此外，如果用户在对话进行到中间时退出，CLI 的退出处理程序也会触发此回调。

**回调函数签名：**

```python
def my_callback(session_id: str, completed: bool, interrupted: bool,
                model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 会话的唯一标识符 |
| `completed` | `bool` | 若智能体已生成最终回复则为 `True`，否则为 `False` |
| `interrupted` | `bool` | 若当前轮次被中断（用户发送新消息、输入 `/stop` 或退出程序）则为 `True` |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的平台 |

**触发时机：** 在两个位置触发：
1. **`agent/turn_finalizer.py`** — 每次调用 `run_conversation()` 方法后（位于 `agent/conversation_loop.py` 中），在所有清理工作完成后。即使当前轮次出现错误，也会触发。
2. **`cli.py`** — 在 CLI 的 atexit 处理程序中，但**仅**在程序退出时智能体正处于处理中状态（即 `_agent_running=True`）时触发。该机制可捕获处理过程中的 Ctrl+C 操作或 `/exit` 命令。此时 `completed=False` 且 `interrupted=True`。

**返回值：** 该参数的值将被忽略。

**应用场景：** 清空缓冲区、关闭连接、保存会话状态、记录会话持续时间，以及清理在 `on_session_start` 中初始化的资源。

**示例 — 清空缓冲区与资源清理：**

```python
_session_caches = {}

def cleanup_session(session_id, completed, interrupted, **kwargs):
    cache = _session_caches.pop(session_id, None)
    if cache:
        # Flush accumulated data to disk or external service
        status = "completed" if completed else ("interrupted" if interrupted else "failed")
        print(f"Session {session_id} ended: {status}, {cache['tool_calls']} tool calls")

def register(ctx):
    ctx.register_hook("on_session_end", cleanup_session)
```

**示例——会话时长跟踪：**

```python
import time, logging
logger = logging.getLogger(__name__)

_start_times = {}

def on_start(session_id, **kwargs):
    _start_times[session_id] = time.time()

def on_end(session_id, completed, interrupted, **kwargs):
    start = _start_times.pop(session_id, None)
    if start:
        duration = time.time() - start
        logger.info("SESSION_DURATION session=%s seconds=%.1f completed=%s interrupted=%s",
                     session_id, duration, completed, interrupted)

def register(ctx):
    ctx.register_hook("on_session_start", on_start)
    ctx.register_hook("on_session_end", on_end)
```

### `on_session_finalize`

当 CLI 或网关**终止**当前会话时触发该回调——例如用户执行 `/new` 命令，或 CLI 在仍有活跃代理运行的情况下退出。仅基于资源闲置度的缓存清除操作不会结束该持久对话。可利用此回调来清除与当前会话 ID 相关联的状态信息。在网关重置后，替换会话会在该回调执行之前就已创建完成。

**回调签名：**

```python
def my_callback(session_id: str | None, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` 或 `None` | 对外的会话 ID。若不存在活跃会话，则该值为 `None`。 |
| `platform` | `str` | `"cli"` 或消息平台名称（如 `"telegram"`、`"discord"` 等）。 |

**触发场景：** 在 CLI/TUI 会话关闭时，以及网关重置或停止运行时。若没有对应的 `on_session_reset` 回调函数，网关仍可正常关闭。

**返回值：** 该参数会被忽略。

**应用场景：** 在会话 ID 被丢弃之前保存最终的会话指标、释放与当前会话相关的资源、发送最终的遥测事件、处理队列中的待写数据。**

---

### `on_session_reset`

在 CLI 或 TUI 会话结束时，或当网关为某个活跃聊天更换新的会话密钥时触发。这使得插件能够在无需等待下一次 `on_session_start` 的情况下，对已清除的对话状态作出响应。

**回调函数签名：**

```python
def my_callback(session_id: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的 ID（已更新为最新值）。 |
| `platform` | `str` | 值可为 `"cli"`、`"tui"`，或消息平台的名称。 |
| `reason` | `str`，可选 | 在 CLI 及网关重置路径中需要提供该参数。 |
| `old_session_id` | `str`，可选 | 仅网关使用的旧会话 ID。 |
| `new_session_id` | `str`，可选 | 仅网关使用的新会话 ID。 |

**触发时机：** CLI 会提供 `session_id`、`platform` 和 `reason`；TUI 会提供 `session_id` 和 `platform`；网关在分配好替换密钥后会添加 `reason`、`old_session_id` 和 `new_session_id`。在网关重置时，执行顺序为：先创建并保存替换会话 → 调用 `on_session_finalize(old_id)` → 在首次接收请求时调用 `on_session_reset(new_id)` → 最后调用 `on_session_start(new_id)`。

**返回值：** 无。

**应用场景：** 重置以 `session_id` 为键的会话级缓存，生成“会话已更换”的分析数据，为新的状态存储桶做好准备。

---

如需包含工具结构、处理函数及高级钩子模式的完整操作指南，请参阅 **[构建插件指南](/developer-guide/plugins)**。

---

### `subagent_start`

在 `delegate_task` 构建完子代理 `AIAgent` 之后、该子代理开始运行之前，**每个子代理仅触发一次**此钩子。无论您是委托单个任务还是三组任务，每个子代理都会对应触发一次该钩子。

该钩子专门用于处理委托/子代理的生命周期相关操作。它并非适用于网关、CLI、cron、批处理、MoA或其他由运行器发起的代理执行的通用“在任何代理调用之前”触发机制。

**回调函数签名：**

```python
def my_callback(parent_session_id: str | None,
                parent_turn_id: str,
                parent_subagent_id: str | None,
                child_session_id: str | None,
                child_subagent_id: str,
                child_role: str,
                child_goal: str,
                **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `parent_session_id` | `str \| None` | 上级代理的会话 ID。 |
| `parent_turn_id` | `str` | 若存在，表示发起委托的上级代理轮次的 ID。 |
| `parent_subagent_id` | `str \| None` | 当该子代理由其他子代理创建时对应的上级子代理 ID；顶级上级代理则为 `None`。 |
| `child_session_id` | `str \| None` | 为子代理分配的会话 ID。 |
| `child_subagent_id` | `str` | 用于委托监控与控制的稳定子代理 ID。 |
| `child_role` | `str` | 应用委托策略后的实际子代理角色，例如 `"leaf"` 或 `"orchestrator"`。 |
| `child_goal` | `str` | 子代理将执行的委托目标/提示语。 |

**触发时机：** 在 `tools/delegate_tool.py` 文件的 `_build_child_agent()` 函数中，即在构建完子 `AIAgent` 并为其添加子代理身份元数据之后、调用 `_run_single_child()` 运行子代理之前。

**返回值：** 该参数会被忽略。这仅是一个观察者钩子；返回值不会阻止子代理的运行，也不会对其造成任何修改。

**应用场景：** 记录子代理的创建过程、映射上下级会话之间的关系、追踪嵌套的委托结构、生成运行前的审计记录、为每个子代理预先分配监控资源。

**示例——记录子代理创建：**

```python
import logging

logger = logging.getLogger(__name__)

def log_subagent_start(
    parent_session_id,
    parent_turn_id,
    child_session_id,
    child_subagent_id,
    child_role,
    child_goal,
    **kwargs,
):
    logger.info(
        "SUBAGENT_START parent=%s turn=%s child_session=%s child=%s role=%s goal=%r",
        parent_session_id,
        parent_turn_id,
        child_session_id,
        child_subagent_id,
        child_role,
        child_goal[:200],
    )

def register(ctx):
    ctx.register_hook("subagent_start", log_subagent_start)
```

:::info  
`subagent_start` 功能有助于实现任务委派的可视化监控，但它并非阻塞式策略钩子。若希望在子代理创建之前阻止任务委派，应使用 [`pre_tool_call`](#pre_tool_call) 来拦截 `delegate_task` 工具调用。  
:::

---

### `subagent_stop`

在 `delegate_task` 执行完成之后，**每个子代理仅触发一次**。无论您是委派单个任务还是三批任务，每个子代理都会对应触发一次该钩子。在所有子任务的异步处理完成之后，父线程会按顺序执行回调函数，且每个 Python 回调函数都在其对应的调用线程上运行（而非在超时工作线程上）。  

**回调函数签名：**

```python
def my_callback(parent_session_id: str, child_role: str | None,
                child_summary: str | None, child_status: str,
                tool_call_history: list[dict], duration_ms: int, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `parent_session_id` | `str` | 上级代理的会话 ID |
| `child_role` | `str \| None` | 分配给子代理的协调者角色标签（若该功能未启用，则为 `None`） |
| `child_summary` | `str \| None` | 子代理返回给上级代理的最终响应 |
| `child_status` | `str` | 取值为 `"completed"`、`"failed"`、`"interrupted"` 或 `"error"` |
| `tool_call_history` | `list[dict]` | 按顺序排列的仅包含元数据的工具调用信息：`tool_name`、受限的 `tool_input`、`input_bytes`、`output_bytes` 以及 `status`；原始输入和输出数据不会被包含在内 |
| `duration_ms` | `int` | 子代理运行所耗用的实际时间，单位为毫秒 |

**触发时机：** 在 `tools/delegate_tool.py` 文件中，当 `ThreadPoolExecutor.as_completed()` 处理完所有子任务的执行结果后。此时会向上级线程调用 `invoke_hook("subagent_stop", ...)`，这样开发者便不会看到子代理池中的递归调用现象，同时回调函数也会保留在发起调用的线程上。

**返回值：** 该参数将被忽略。

**应用场景：** 记录协调流程的运行情况、统计子代理的运行时长以用于计费、生成任务委派后的审计记录。

**示例——记录协调者操作日志：**

```python
import logging
logger = logging.getLogger(__name__)

def log_subagent(parent_session_id, child_role, child_status, duration_ms, **kwargs):
    logger.info(
        "SUBAGENT parent=%s role=%s status=%s duration_ms=%d",
        parent_session_id, child_role, child_status, duration_ms,
    )

def register(ctx):
    ctx.register_hook("subagent_stop", log_subagent)
```

:::info
在高度委托的场景下（例如：调度器角色×5个分支×多层嵌套），`subagent_stop`会在每个回合中多次触发。请确保您的回调函数执行速度尽可能快；将耗时较长的操作放到后台队列中处理。
:::

---

### `pre_gateway_dispatch`

该函数在网关中**每个接收到的 `MessageEvent` 发生时触发一次**，位于内部事件检测之后，但认证/配对以及代理调度之前。对于那些无法完全适配于任何单一平台适配器的网关级消息流策略（如仅监听窗口、人工干预、按聊天会话路由等），此处正是实施这些策略的拦截点。

**回调函数签名：**

```python
def my_callback(event, gateway, session_store, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `event` | `MessageEvent` | 标准化的传入消息（包含 `.text`、`.source`、`.message_id`、`.internal` 等字段）。 |
| `gateway` | `GatewayRunner` | 当前正在运行的网关运行器，插件可通过 `gateway.adapters[platform].send(...)` 发送旁路回复（如通知消息发送方等）。 |
| `session_store` | `SessionStore` | 用于通过 `session_store.append_to_transcript(...)` 实现静默转录功能。 |

**触发时机：** 在 `gateway/run.py` 文件的 `GatewayRunner._handle_message()` 方法中，在计算出 `is_internal` 的紧接着之后触发。**内部事件会完全跳过此钩子**（这类事件由系统生成，例如后台进程处理完成等，不应受面向用户的策略限制）。 

**返回值：** `None` 或字典。第一个被识别的操作字典将生效，其余插件的处理结果将被忽略。插件回调中的异常会被捕获并记录；出现错误时，网关会始终继续执行正常的消息分发流程。

| 返回值 | 效果 |
|--------|------|
| `{"action": "skip", "reason": "..."}` | 直接丢弃该消息——不触发智能体回复，也不进行配对或认证流程。假定插件已对该消息进行了处理（例如将其静默添加到转录记录中）。 |
| `{"action": "rewrite", "text": "new text"}` | 替换 `event.text` 的内容，然后使用修改后的消息继续正常的消息分发流程。此方式可用于将缓冲的背景消息合并为单个提示词。 |
| `{"action": "allow"}` / `None` | 执行正常的分发流程——运行完整的认证/配对/智能体循环流程。 |
**应用场景：** 单向监听群聊（仅在被标记时才回复；将背景消息暂存以纳入上下文）；人工接管模式（在负责人手动处理聊天时，静默接收客户消息）；基于用户档案的速率限制；策略驱动的路由分配。

**示例——静默过滤未经授权的私信，且无需触发配对码：**

```python
def deny_unauthorized_dms(event, **kwargs):
    src = event.source
    if src.chat_type == "dm" and not _is_approved_user(src.user_id):
        return {"action": "skip", "reason": "unauthorized-dm"}
    return None

def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", deny_unauthorized_dms)
```

**示例——在提及时将环境消息缓冲区重写为单个提示语：**

```python
_buffers = {}

def buffer_or_rewrite(event, **kwargs):
    key = (event.source.platform, event.source.chat_id)
    buf = _buffers.setdefault(key, [])
    if _bot_mentioned(event.text):
        combined = "\n".join(buf + [event.text])
        buf.clear()
        return {"action": "rewrite", "text": combined}
    buf.append(event.text)
    return {"action": "skip", "reason": "ambient-buffered"}

def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", buffer_or_rewrite)
```

### `gateway_platform_event`

该事件仅在网关完成常规的、基于用户配置文件的授权检查之后，针对受支持的平台原生事件触发。回调函数接收的是纯字典格式的数据；原始的 SDK 对象、适配器句柄、机器人客户端以及回调上下文均不属于此稳定接口的组成部分。

Telegram 消息反应是最早被支持的事件类型，随后依次增加了消息编辑、删除以及主题对话生命周期相关事件：

```python
def on_platform_event(platform, event_type, payload, **kwargs):
    if platform == "telegram" and event_type == "reaction":
        print(payload["chat_id"], payload["message_id"], payload["emojis"])
    elif event_type == "message_edited":
        print(platform, payload["chat_id"], payload["message_id"], payload["text"])

def register(ctx):
    ctx.register_hook("gateway_platform_event", on_platform_event)
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `platform` | `str` | 稳定平台标识（`"telegram"`、`"discord"`）。 |
| `event_type` | `str` | 事件对应的本地合约标识（详见下表）。 |
| `payload` | `dict` | 各事件类型特有的字段，具体说明见下文的各事件类型介绍。 |

每个 payload 均为叠加式结构且与特定事件相关；并不存在统一的网关 payload 版本。所有标识均为字符串形式；缺失或不可用的字段将标记为 `None`，绝不会进行猜测。格式错误的事件以及来源无法被授权的事件将被直接丢弃（拒绝处理）。当 Telegram 应用发生临时重建时，观察者及核心处理程序会一同重新注册。

**各事件类型的 payload 规范（v1版本，叠加式结构）：**

| `event_type` | 平台 | 数据字段 |
|--------------|-----------|----------|
| `reaction` | Telegram | `emojis: list[str]`、`custom_emoji_ids: list[str]`、`chat_id: str`、`message_id: str`、`thread_id: str \| None`（Telegram的互动更新不包含主题ID，因此始终为`None`）。 |
| `message_edited` | Telegram、Discord | `chat_id: str`、`message_id: str`、`thread_id: str \| None`、`text: str \| None`（已编辑的文本或标题，长度有限；仅编辑媒体内容或未缓存时则为`None`）、`edited_at: str \| None`（遵循ISO 8601格式）。 |
| `message_deleted` | Discord | `chat_id: str`、`message_id: str`、`thread_id: str \| None`、`author_id: str \| None`。Discord的删除事件不会标明删除者；授权来源为被删除消息的发送者，且未缓存的删除操作不会触发该事件。 |
| `thread_created` | Discord | `thread_id: str`、`parent_chat_id: str \| None`、`name: str \| None`、`owner_id: str \| None`。 |
| `thread_renamed` | Discord | `thread_id: str`、`parent_chat_id: str \| None`、`old_name: str \| None`、`new_name: str`。仅当主题名称确实发生更改时才会触发该事件；其他线程相关更新（如归档、慢速模式、标签添加等）则会被忽略。Discord的线程更新事件不包含操作者信息，因此线程所有者即为授权来源。 |

在Discord上，机器人对消息进行的连续编辑操作（流式编辑）不会触发`message_edited`事件——由机器人生成的此类事件会在处理环节被直接忽略。

该钩子仅具备观察功能：它**不**提供对原始事件的访问权限或适配器访问权限。**刻意未提供对原始 SDK 数据负载的直接访问功能**——因为适配器 SDK 的结构可能会在未经通知的情况下发生变化，从而导致 API 接口无法进一步演化；只有在确实有需求时，才会通过一个带有“无稳定性保障”标识的独立能力项（`gateway.raw_events`）并配合专门的设计方案来实现该功能（相关讨论见 #64228）。若需在平台上执行操作（如添加回复、重命名主题），请使用 [插件指南](plugins.md#platform-actions) 中记载的、受能力项限制的 `ctx.platform_actions` 接口——该接口默认会被 `gateway.platform_actions` 能力项屏蔽。`PluginContext.dispatch_tool()` 仅能调用工具注册表中已注册的工具；而 `send_message` 被刻意排除在注册表之外（其传输机制专门用于 CLI、cron、看板以及 MCP 等明确的传递路径）。未来的外部发送协议必须首先确保在所有适配器上都能稳定地传递内容/处理结果；因此当前版本并未预注册一个无实际功能的 `gateway_message_delivered` 钩子。

---

### `pre_approval_request`

该钩子在请求批准决策之前触发。它适用于需要用户交互的场景——包括交互式 CLI、Ink TUI、网关平台以及 ACP 客户端——同时也涵盖那些在无需人工干预的情况下、通过 `approvals.mode=smart` 设置而做出的决策（即 `surface="smart"` 模式）。在智能模式下，该钩子会在调用辅助大语言模型之前执行。

此处正是集成自定义通知器的理想位置——例如，可以接入能在 macOS 菜单栏中弹出允许/拒绝通知的应用，或是记录每项审批请求及其相关上下文的审计日志。

**回调函数签名：**

```python
def my_callback(
    command: str,
    description: str,
    pattern_key: str,
    pattern_keys: list[str],
    session_key: str,
    surface: str,
    **kwargs,
):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `command` | `str` | 正在被评估的终端命令或 `execute_code` 脚本。在将数据发送给观察者之前，智能模式和网关模式的负载内容会被脱敏处理。即使关闭了 `security.redact_secrets`，也必须对智能观察者模式的内容进行脱敏；如果脱敏失败，则会跳过智能钩子机制。 |
| `description` | `str` | 该命令被标记的原因（当多个模式同时匹配时，这些原因会被合并显示） |
| `pattern_key` | `str` | 触发批准操作的主要模式键（例如 `"rm_rf"`、`"sudo"`） |
| `pattern_keys` | `list[str]` | 所有匹配的模式键 |
| `session_key` | `str` | 会话标识符，有助于针对特定聊天记录发送通知 |
| `surface` | `str` | `"cli"` 表示交互式 CLI/TUI 提示；`"gateway"` 表示异步平台审批；`"smart"` 表示由辅助大语言模型自动做出的批准/拒绝决策 |

**返回值：** 无需返回值。此处的钩子仅用于观察者，无法否决审批结果或预先回答相关问题。若要在工具进入审批系统之前进行拦截，请使用 [`pre_tool_call`](#pre_tool_call)。

**应用场景：** 桌面通知、推送警报、审计日志记录、Slack Webhook、升级路由处理以及指标统计。

**示例——在 macOS 上发送桌面通知：**

```python
import subprocess

def notify_approval(command, description, session_key, **kwargs):
    title = "Hermes needs approval"
    body = f"{description}: {command[:80]}"
    subprocess.Popen([
        "osascript", "-e",
        f'display notification "{body}" with title "{title}"',
    ])

def register(ctx):
    ctx.register_hook("pre_approval_request", notify_approval)
```

### `post_approval_response`

在人工审批或智能审批决策作出后、提示超时后，或是网关无法发送审批通知时触发。若通知发送失败，则会在任何审批决策生成之前输出 `choice="notify_failed"`。

**回调函数签名：**

```python
def my_callback(
    command: str,
    description: str,
    pattern_key: str,
    pattern_keys: list[str],
    session_key: str,
    surface: str,
    choice: str,
    **kwargs,
):
```

与 `pre_approval_request` 所使用的参数完全相同，此外还需补充以下参数：

| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `choice` | `str` | 引导式决策模式使用 `"once"`、`"session"`、`"always"`、`"deny"`、`"timeout"` 或 `"notify_failed"`；智能决策模式则使用 `"smart_approve"` 或 `"smart_deny"` |
| `decided_by` | `str` | 智能决策模式时为 `"aux_llm"`；引导式决策模式下该参数不存在 |

**返回值：** 无需关注。

**应用场景：** 关闭对应的桌面通知、在审计日志中记录最终决策结果、更新相关指标数据，以及触发速率限制机制的后续处理。

```python
def log_decision(command, choice, session_key, **kwargs):
    logger.info("approval %s: %s for session %s", choice, command[:60], session_key)

def register(ctx):
    ctx.register_hook("post_approval_response", log_decision)
```

### `pre_transcription`

在提供商已被确定之后、任何后端被调用之前，于 STT 调度器（`tools.transcription_tools.transcribe_audio`）内部触发，无论该后端是内置的、类型为 `command` 的提供商，还是通过插件注册的提供商。这使得插件能够直接控制转录请求的流程，而不仅仅是在转录完成后进行观察。

**回调函数签名：**

```python
def my_callback(
    file_path: str,
    provider: str,
    model: str | None,
    language: str | None,
    prompt: str | None,
    source: str | None,
    **kwargs,
) -> dict | None:
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `file_path` | `str` | 需要转录的音频文件的绝对路径。该参数为只读属性。 |
| `provider` | `str` | 已确定的文本转语音服务提供商（如 `local`、`groq`、`openai`、`mistral`、`xai`、`elevenlabs`、`deepinfra`、`local_command`，或是某个命令型提供商的名称、插件型提供商的名称）。 |
| `model` | `str \| None` | 目前已确定的模型，若采用后端默认设置则值为 `None`。 |
| `language` | `str \| None` | 来自服务提供商配置文件中的语言代码，若未指定则为 `None`。 |
| `prompt` | `str \| None` | 静态的 [`stt.prompt`](/user-guide/configuration#transcription-prompt-vocabulary-hints) 值，若未指定则为 `None`。 |
| `source` | `str \| None` | 调用方标识标签（如 `gateway`、`voice_mode` 等）。仅用于监控目的，不会影响请求的路由处理。 |

**返回值：** 一个 `dict` 对象，其中 `"prompt"`、`"language"`、`"model"` 这些键对应的值为字符串类型；若无需修改请求，则这些键的值为 `None`。非字符串类型的值、未知的键以及 `file_path` 参数将被忽略（尝试使用 `file_path` 参数时会记录警告信息）。各项设置将按照注册顺序应用，同一字段采用“后设置者优先”的原则，其效果会叠加在 `stt.prompt` 的默认配置之上。若将 `prompt` 参数设置为 `""`，则可清除该请求对应的已配置提示语。

**适用场景：** 在上传音频之前注入针对特定用户或对话的词汇表；根据调用方的区域设置强制指定语言；针对长度过长的录音降低所使用的模型级别；将背景噪音较大的音频路由至不同的模型进行处理。

```python
VOCAB = "Hermes, Teknium, Nous Research, kanban"

def add_vocab(provider, prompt, source, **kwargs):
    if source != "gateway":
        return None
    return {"prompt": f"{prompt}. {VOCAB}" if prompt else VOCAB}

def register(ctx):
    ctx.register_hook("pre_transcription", add_vocab)
```

并非所有后端都支持接收提示词。`local` 类型会将提示词映射为 faster-whisper 的 `initial_prompt`；而 `openai`、`groq`、`mistral` 和 `deepinfra` 则以 `prompt` 的形式发送该提示词；`xai`、`elevenlabs`、`local_command` 以及类型为 `command` 的提供者会在 DEBUG 级别记录日志，并在无需提示词的情况下进行转录。如需查看完整的对应关系及隐私边界说明，请参阅 [提供者支持表](/user-guide/configuration#transcription-prompt-vocabulary-hints)。若发生 Hook 集成错误，系统将采用“故障即继续”策略：请求会原样发送，不会被修改。

---

### `transform_tool_result`

该回调在工具返回**之后**、结果被添加到对话记录**之前**触发。它允许插件在模型查看之前，重写任意工具生成的输出字符串——而不仅限于终端输出。

**回调函数签名：**

```python
def my_callback(tool_name: str, args: dict, result: str, task_id: str, **kwargs) -> str | None:
```

完整的有效载荷还包括 `session_id`、`tool_call_id`、`turn_id`、`api_request_id`、`duration_ms`、`status`、`error_type` 以及 `error_message`。`result` 是工具调度机制返回的最终结果；该字段与 `args` 可以包含任意形式的用户或工具相关内容，以及敏感信息。

**返回值：** 第一个 `str` 参数将替换原有结果（包括空字符串）；若为 `None`，则保持原样不变。

**应用场景：** 从 `web_extract` 的输出中移除与特定组织相关的隐私信息，将长度过长的 JSON 工具响应封装在汇总标题中，在 `read_file` 的结果中注入基于检索的提示信息，以及将 `delegate_task` 子智能体的报告按照特定项目结构进行重新格式化。

```python
import re
SECRET = re.compile(r"sk-[A-Za-z0-9]{32,}")

def redact_secrets(tool_name, result, **kwargs):
    if SECRET.search(result):
        return SECRET.sub("[REDACTED]", result)
    return None

def register(ctx):
    ctx.register_hook("transform_tool_result", redact_secrets)
```

该功能适用于所有工具。如需仅针对终端输出的转换，请参阅下方的 `transform_terminal_output` —— 其功能范围更为有限，会在 `transform_tool_result` 之前执行，且其替换内容仍需符合终端工具的最终输出限制。

---

### `transform_terminal_output`

该函数在环境已对前端进程的输出进行限制之后、最终输出限制生效之前，在 `terminal` 工具内部被调用。它允许插件替换捕获到的 stdout/stderr 内容；不过这些替换后的内容同样需遵守最终的输出限制。

**回调函数签名：**

```python
def my_callback(
    command: str,
    output: str,
    returncode: int,
    task_id: str,
    env_type: str,
    **kwargs,
) -> str | None:
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `command` | `str` | 生成该输出对应的Shell命令。 |
| `output` | `str` | 在限制进程捕获后，标准输出与标准错误的合并内容。 |
| `returncode` | `int` | 进程的返回码。 |
| `task_id` | `str` | 实际的任务标识符，若无则为空字符串。 |
| `env_type` | `str` | 执行环境类型。 |

**返回值：** 第一个`str`参数将替换原有的输出内容；若为`None`则保持原样不变。命令和输出内容中可能包含凭证或其他敏感数据。

```python
def summarize_find(command, output, **kwargs):
    if command.startswith("find ") and len(output) > 50_000:
        lines = output.count("\n")
        head = "\n".join(output.splitlines()[:40])
        return f"{head}\n\n[summary: {lines} paths total, showing first 40]"
    return None

def register(ctx):
    ctx.register_hook("transform_terminal_output", summarize_find)
```

该功能与 `transform_tool_result` 配合使用，后者会在每个工具（包括 `terminal`）执行完毕后依次运行。

---

### `transform_llm_output`

在工具调用循环结束且模型生成最终响应后、该响应被传递给用户（通过 CLI、网关或程序化调用方式）之前，**每轮对话仅触发一次**。它允许插件利用传统编程方法重写助手的最终文本，而无需为基于 SOUL 的文本处理或技能驱动的转换消耗额外的推理令牌。

**回调函数签名：**

```python
def my_callback(
    response_text: str,
    session_id: str,
    model: str,
    platform: str,
    **kwargs,
) -> str | None:
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `response_text` | `str` | 该轮对话中助手的最终回复文本。 |
| `session_id` | `str` | 当前对话的会话ID（一次性任务可能为空）。 |
| `model` | `str` | 生成该回复的模型名称（例如 `anthropic/claude-sonnet-4.6`）。 |
| `platform` | `str` | 输出平台（如 `cli`、`telegram`、`discord` 等；未设置时为空）。 |

**返回值：** 若需替换回复文本，则返回非空字符串；若保持原样，则返回 `None` 或空字符串。当多个插件同时注册时，**第一个非空字符串优先生效**。与工具类及终端转换不同，空字符串不可作为替换内容。

**应用场景：** 对回复进行风格/词汇转换（如海盗语、海绵宝宝风格），从最终文本中删除用户专属标识符，添加项目专用签名页脚，无需在 SOUL 指令上消耗过多令牌即可强制执行企业风格指南。

当启用 CLI 流式输出时，仅会先打印追加型转换内容，而替换型转换内容则会在流式输出结束后完整打印，并标注为“流式输出后转换”，从而确保替换内容不会被遗漏。

```python
import os, re

def spongebob(response_text, **kwargs):
    if os.environ.get("SPONGEBOB_MODE") != "on":
        return None  # pass through unchanged
    return re.sub(r"!", "!! Tartar sauce!", response_text)

def register(ctx):
    ctx.register_hook("transform_llm_output", spongebob)
```

该钩子仅在接收到非空且完整的响应时才会触发——在用户点击停止按钮中断流程或轮次为空的情况下不会启动。此类异常会被记录为警告，不会导致智能体执行中断。

### API请求观察者钩子

#### `pre_api_request`

在向服务提供商发送请求之前立即触发。该钩子仅适用于观察者。为保持兼容性，传统的`user_message`、`conversation_history`和`request_messages`字段均为原始数据且未经过清洗；新开发者建议使用已处理过的`request`数据结构。

#### `post_api_request`

在服务提供商的响应成功处理并标准化后触发。该钩子仅适用于观察者。建议优先使用已处理过的`response`数据；`assistant_message`为原始的标准化消息，而`usage`字段则包含使用统计信息。

#### `api_request_error`

当服务提供商的请求失败时触发，此时会提供状态码、重试时间信息、`error`对象以及已处理过的`request`数据。该钩子仅适用于观察者。错误信息中可能仍包含服务提供商或用户的相关数据。

### `on_skill_lifecycle`

在智能体的技能使用状态发生权威性变更后触发。该钩子仅适用于观察者，可获取本地存储的`skill_name`、数据来源、关联ID、使用次数以及是否可复用等信息。

### 看板任务生命周期观察者

#### `kanban_task_claimed`

在调度器进程完成任务接管操作后、工作进程启动之前触发。

#### `kanban_task_completed`

在任务处理完毕并进行清理工作之后触发，通常发生在工作进程内。其`summary`字段可能包含项目或用户相关的信息。

#### `kanban_task_blocked`

在常规的阻塞式状态转换之后触发。在该写操作事务完成之前，依赖等待路径会先调用该钩子。其 `reason` 字段可包含项目或用户相关的内容。

这三种看板钩子均仅具备观察功能，会携带 `task_id`、`profile_name`、`board`、`assignee` 和 `run_id` 等字段；已完成任务的钩子还会额外包含 `summary` 字段，而阻塞状态的钩子则会包含 `reason` 字段。

### 看板工作流程、任务变更及调度观察器

另有五种观察器（RFC #58548）属于看板系列扩展。它们同样仅作为观察者存在，在相关事务提交后会触发，并且会在检测到 `has_hook` 为假时直接跳过处理——若没有订阅者，其调度行为将保持不变。任务范围的钩子会携带与上述钩子相同的常用字段。

- **`on_kanban_worker_spawned`** — 在 `spawn_fn` 执行完毕且工作进程的 PID 被记录之后触发。该回调会添加 `worker_pid`（可能为 `None`）以及 `workspace_path` 参数。它在调度锁内部执行，因此需确保回调操作尽可能高效。
- **`on_kanban_worker_exited`** — 基于时间戳触发，即在 `detect_crashed_workers` 功能回收已死亡进程的任务时触发。该回调会添加 `worker_pid`、`exit_kind`、`exit_code`、`outcome` 以及 `retry_status` 等参数。
- **`on_kanban_worker_stale_claim`** — 当 TTL 到期的任务请求被回收时触发；此时处于活跃状态的进程不会触发相应回调。该回调会添加 `worker_pid`、`heartbeat_stale` 以及 `retry_status` 等参数。
- **`on_kanban_task_updated`** — 在任务状态不在“请求中/已完成/已阻塞”生命周期内时，对任务字段进行写入操作后触发（例如调用 `assign_task`、对模型或推理结果进行修改，或通过仪表板编辑器进行操作）。该回调会返回 `changed_fields` 参数，其中仅包含字段名称，不包含字段值。
- **`on_kanban_dispatch_tick`** — 每次调度器执行一次计时任务后触发，严格在调度锁释放之后执行，包括系统空闲状态或调度锁被占用时的计时任务。回调携带的参数包括 `board`、`profile_name`、`dry_run`、`outcome` 以及 `result`。

---

## Shell 钩子

您可以在配置文件 `config.yaml` 中定义 Shell 脚本钩子，每当对应的插件钩子事件被触发时，Hermes 就会以子进程的形式运行这些脚本——无论是在 CLI、网关、桌面端、TUI 还是仪表板聊天界面中。无需编写 Python 插件即可实现该功能。

在构建智能体时，桌面端、命令行界面及控制面板会注册聊天钩子，这些钩子会使用该会话的配置文件设置与授权列表。切换配置文件后不会复用其他配置文件的钩子。现有的钩子授权要求及安全模式规则依然有效；未经批准的钩子会被跳过，而不会被默许使用。

当您需要一个即插即用的单文件脚本（支持 Bash、Python 或任何带有 shebang 语法的脚本）来实现以下功能时，可使用 Shell 钩子：

- **阻止或修改工具调用**——拒绝危险的 `terminal` 命令，实施按目录划分的策略，对具有破坏性的 `write_file`/`patch` 操作要求授权，或在工具运行前重写参数（对路径进行清理、注入默认值）。
- **在工具调用后执行操作**——自动格式化智能体刚刚生成的 Python 或 TypeScript 文件，记录 API 调用日志，触发持续集成工作流。
- **向下一个大语言模型响应中注入上下文**——在用户消息的开头添加 `git status` 的输出结果、当前星期几的信息或已获取的文档内容（详见 [`pre_llm_call`](#pre_llm_call)）。
- **监控生命周期事件**——在子智能体完成任务（`subagent_stop`）或会话启动时（`on_session_start`）记录日志行。

可通过在命令行工具启动时（`hermes_cli/main.py`）以及网关启动时（`gateway/run.py`）调用 `agent.shell_hooks.register_from_config(cfg)` 来注册 Shell 钩子。它们能与 Python 插件钩子自然结合使用——两者均通过同一个调度器处理。

### 一览对比

| 维度 | Shell 钩子 | [插件钩子](#plugin-hooks) | [网关钩子](#gateway-event-hooks) |
|-----------|-------------|-------------------------------|---------------------------------------|
| 定义位置 | `~/.hermes/config.yaml` 文件中的 `hooks:` 块 | `plugin.yaml` 插件中的 `register()` 函数 | `HOOK.yaml` 文件及 `handler.py` 目录 |
| 存放路径 | （按惯例）`~/.hermes/agent-hooks/` | `~/.hermes/plugins/<名称>/` | `~/.hermes/hooks/<名称>/` |
| 支持语言 | 任意语言（Bash、Python、Go 可执行文件等） | 仅限 Python | 仅限 Python |
| 运行环境 | CLI + 网关 | CLI + 网关 | 仅网关 |
| 触发事件 | `VALID_HOOKS`（包括 `subagent_stop`） | `VALID_HOOKS` | 网关生命周期事件（`gateway:startup`、`agent:*`、`command:*`） |
| 是否可阻止工具调用 | 是（通过 `pre_tool_call`） | 是（通过 `pre_tool_call`） | 否 |
| 是否可注入大语言模型上下文 | 是（通过 `pre_llm_call`） | 是（通过 `pre_llm_call`） | 否 |
| 同意机制 | 每次使用前根据 `(事件, 命令)` 对显示提示 | 隐式同意（基于对 Python 插件的信任） | 隐式同意（基于对目录结构的信任） |
| 进程间隔离 | 是（通过子进程实现） | 否（同一进程内） | 否（同一进程内） |

### 配置架构

```yaml
hooks:
  <event_name>:                  # Must be in VALID_HOOKS
    - matcher: "<regex>"         # Optional; used for pre/post_tool_call only
      command: "<shell command>" # Required; runs via shlex.split, shell=False
      timeout: <seconds>         # Optional; default 60, capped at 300
      fail_closed: <bool>        # Optional; default false. pre_tool_call only.
                                 # `failClosed` also accepted (Cursor/Claude Code compat)

hooks_auto_accept: false         # See "Consent model" below
```

事件名称必须属于[插件钩子事件](#plugin-hooks)之一；若输入有误，系统会显示“您是指X吗？”的警告并跳过该事件。单个条目中未知的键会被忽略；若缺少`command`字段，则会发出警告并跳过该事件。当`timeout > 300`时，系统会发出警告并对该值进行限制。对于非`pre_tool_call`类型的事件，若设置`fail_closed: true`，系统会发出警告但仍会忽略该设置（仅具备阻塞功能的事件才能因关闭而失败）。

### JSON网络协议

每当事件触发时，Hermes会根据匹配的钩子（在匹配器允许的情况下）为每个钩子启动一个子进程，将JSON格式的有效载荷通过**stdin**输入，然后再以JSON格式从**stdout**读取返回值。

**stdin — 脚本接收到的有效载荷：**

```json
{
  "hook_event_name": "pre_tool_call",
  "tool_name":       "terminal",
  "tool_input":      {"command": "rm -rf /"},
  "session_id":      "sess_abc123",
  "cwd":             "/home/user/project",
  "extra":           {"task_id": "...", "tool_call_id": "..."}
}
```

对于非工具类事件（如 `pre_llm_call`、`subagent_stop` 以及会话生命周期相关事件），`tool_name` 和 `tool_input` 的值为 `null`。`extra` 字典则用于存储所有与特定事件相关的关键字参数（如 `user_message`、`conversation_history`、`child_role`、`duration_ms` 等）。对于无法序列化的值，系统会将其转换为字符串形式，而非直接省略。

**stdout — 可选响应：**

```jsonc
// Block a pre_tool_call (both shapes accepted; normalised internally):
{"decision": "block", "reason":  "Forbidden: rm -rf"}   // Claude-Code style
{"action":   "block", "message": "Forbidden: rm -rf"}   // Hermes-canonical

// Modify a pre_tool_call — rewrite tool args before dispatch:
{"action": "modify", "args": {"new_string": "fixed content"}}         // Hermes-canonical
{"decision": "modify", "tool_input": {"new_string": "fixed content"}} // Claude-Code style

// Inject context for pre_llm_call:
{"context": "Today is Friday, 2026-04-17"}

// Keep the agent going at the verify gate (pre_verify); both shapes accepted:
{"action": "continue", "message": "Run the formatter, then finish."}
{"decision": "block",  "reason":  "Run the formatter, then finish."}

// Silent no-op — any empty / non-matching output is fine:
```

格式错误的 JSON、非零退出码以及超时情况只会记录警告，而不会中断代理循环。

### 退出码 2 = 拦截（兼容 Claude Code / Cursor）

若 `pre_tool_call` 钩子以**2**号代码退出，即便其标准输出中不包含拦截用的 JSON，也会阻止工具调用。拦截信息会按照以下优先级确定：

1. 存在时的标准输出中的拦截 JSON（包含 `reason`/`message` 字段）；
2. 标准错误流的前 400 个字符；
3. 默认的通用消息 `"Blocked by shell hook."`。

因此，最简单的拦截钩子实现方式如下：

```bash
#!/usr/bin/env bash
echo "policy violation: rm -rf is not permitted" >&2
exit 2
```

对于那些其阻塞指令未被遵守的事件（即除 `pre_tool_call` 之外的所有事件），退出码 2 会被视为其他非零退出码：系统会记录一条警告，同时仍会对标准输出进行解析。

### 失败时继续执行与失败时终止执行

默认情况下，shell 钩子采用**失败时继续执行**的策略：若工具启动失败、超时或标准输出无法解析，系统仅会记录警告，然后继续执行后续操作。这种设置对于用于监控目的的钩子来说是合适的——但对于安全防护机制而言则不恰当。一旦密钥扫描器发生故障，绝不能让它悄无声息地允许执行本应对其进行检查的工具调用。

若希望改变这一行为，可在 `pre_tool_call` 条目中设置 `fail_closed: true`（或 Cursor/Claude Code 版本的拼写 `failClosed: true`）。

```yaml
hooks:
  pre_tool_call:
    - matcher: "terminal|write_file|patch"
      command: "~/.hermes/agent-hooks/secret-scan.sh"
      timeout: 10
      fail_closed: true
```

当设置 `fail_closed: true` 后，上述每种情况都会通过 `hook <command> failed closed: <reason>` **阻止**工具调用：

| 失败类型 | 默认行为（fail-open） | `fail_closed: true` 行为 |
|---------|--------------------|--------------------|
| 命令不存在/无法执行 | 发出警告并继续执行 | **阻止** |
| 超时 | 发出警告并继续执行 | **阻止** |
| 输出非 JSON 格式（如堆栈跟踪） | 发出警告并继续执行 | **阻止** |
| 正常退出，且输出有效的空操作 JSON（`{}`） | 继续执行 | 继续执行 |

`fail_closed` 仅适用于可被阻止的事件类型（目前为 `pre_tool_call`）；若在其他事件上设置该参数，将在配置解析时记录警告并被忽略。`hermes hooks test` 能够反映这些规则——`parsed` 行会准确显示调度器将接收到的阻止信息格式。

### 实际应用示例

#### 1. 每次写入后自动格式化 Python 文件

```yaml
# ~/.hermes/config.yaml
hooks:
  post_tool_call:
    - matcher: "write_file|patch"
      command: "~/.hermes/agent-hooks/auto-format.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/auto-format.sh
payload="$(cat -)"
path=$(echo "$payload" | jq -r '.tool_input.path // empty')
[[ "$path" == *.py ]] && command -v black >/dev/null && black "$path" 2>/dev/null
printf '{}\n'
```

该智能体对文件的上下文感知视图**不会**自动重新读取——格式化操作仅影响磁盘上的文件。后续的 `read_file` 调用将会读取到已格式化后的版本。

#### 2. 阻止具有破坏性的 `terminal` 命令执行

```yaml
hooks:
  pre_tool_call:
    - matcher: "terminal"
      command: "~/.hermes/agent-hooks/block-rm-rf.sh"
      timeout: 5
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/block-rm-rf.sh
payload="$(cat -)"
cmd=$(echo "$payload" | jq -r '.tool_input.command // empty')
if echo "$cmd" | grep -qE 'rm[[:space:]]+-rf?[[:space:]]+/'; then
  printf '{"decision": "block", "reason": "blocked: rm -rf / is not permitted"}\n'
else
  printf '{}\n'
fi
```

#### 3. 在每一轮对话中插入 `git status` 命令（相当于 Claude-Code 的 `UserPromptSubmit` 功能）

```yaml
hooks:
  pre_llm_call:
    - command: "~/.hermes/agent-hooks/inject-cwd-context.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/inject-cwd-context.sh
cat - >/dev/null   # discard stdin payload
if status=$(git status --porcelain 2>/dev/null) && [[ -n "$status" ]]; then
  jq --null-input --arg s "$status" \
     '{context: ("Uncommitted changes in cwd:\n" + $s)}'
else
  printf '{}\n'
fi
```

Claude Code 的 `UserPromptSubmit` 事件并非特意设计为独立的 Hermes 事件——`pre_llm_call` 会在同一环节触发，且已具备上下文注入功能。因此请在此处使用它。

#### 4. 记录每个子智能体的处理结果

```yaml
hooks:
  subagent_stop:
    - command: "~/.hermes/agent-hooks/log-orchestration.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/log-orchestration.sh
log=~/.hermes/logs/orchestration.log
jq -c '{ts: now, parent: .session_id, extra: .extra}' < /dev/stdin >> "$log"
printf '{}\n'
```

### 同意机制

每当 Hermes 首次遇到独特的 `(事件, 命令)` 对时，都会向用户请求批准；之后会将该决策保存到 `~/.hermes/shell-hooks-allowlist.json` 文件中。后续的运行（无论是通过 CLI 还是网关）都将跳过此提示。

有三种方式可以绕过交互式提示——任意一种均可：

1. 在 CLI 中使用 `--accept-hooks` 参数（例如：`hermes --accept-hooks chat`）
2. 设置 `HERMES_ACCEPT_HOOKS=1` 环境变量
3. 在 `~/.hermes/config.yaml` 中将 `hooks_auto_accept` 设置为 `true`

在非 TTY 环境下运行（如网关、cron 任务或 CI 环境）时，必须使用上述三种方式之一；否则任何新添加的钩子都会被默默忽略且会记录警告信息。

**对脚本的修改会被默认视为有效。** 允许列表是依据确切的命令字符串来识别的，而非脚本的哈希值，因此直接修改磁盘上的脚本并不会使之前的同意失效。`hermes hooks doctor` 命令能够检测文件修改时间的变化，帮助你发现脚本已被修改，并决定是否需要重新批准。

#### 手动添加允许项

对于无法通过交互方式回应首次使用提示的非 TTY 环境或服务账户部署场景，手动添加允许项非常实用。允许列表文件位于 `~/.hermes/shell-hooks-allowlist.json`，其格式为一个 `approvals` 数组。每条批准记录都会包含对应的钩子“事件”以及确切的“命令”字符串：

```json
{
  "approvals": [
    {
      "event": "post_llm_call",
      "command": "/home/hermes/.hermes/hooks/my-hook.py"
    }
  ]
}
```

命令字符串必须与已配置的钩子命令完全一致。包含 `sha256` 字段的路径键对象并不符合预期格式，因此不会被批准用于该钩子。建议使用 `hermes hooks list` 命令来核对手动输入的内容。

### `hermes hooks` CLI 命令

| 命令 | 功能说明 |
|---------|----------|
| `hermes hooks list` | 列出所有已配置的钩子，包括匹配规则、超时设置以及授权状态 |
| `hermes hooks test <event> [--for-tool X] [--payload-file F]` | 使用模拟负载触发所有匹配的钩子，并输出解析后的响应结果 |
| `hermes hooks revoke <command>` | 移除所有与 `<command>` 匹配的允许列表项（更改将在下次重启后生效） |
| `hermes hooks doctor` | 对每个已配置的钩子进行检查：包括执行权限、允许列表状态、修改时间偏差、JSON 输出有效性以及大致的执行时间 |

### 安全性

Shell 钩子是使用**您的完整用户凭证**来运行的，其信任级别与 cron 任务或 shell 别名相同。请将 `config.yaml` 文件中的 `hooks:` 部分视为高权限配置：

- 仅引用您自己编写或经过彻底审查的脚本。
- 将脚本保存在 `~/.hermes/agent-hooks/` 目录下，以便于进行路径审计。
- 在拉取共享配置后，重新运行 `hermes hooks doctor` 命令，以便在新的钩子注册之前发现它们。
- 如果您的 `config.yaml` 文件由团队共同版本控制，请像审查 CI 配置一样仔细检查所有修改 `hooks:` 部分的 Pull Request。

### 顺序与优先级

Python插件钩子与Shell钩子均通过同一个`invoke_hook()`调度器来处理。Python插件会首先被注册（通过`discover_and_load()`函数），而Shell钩子则稍后注册（通过`register_from_config()`函数），因此在出现冲突时，Python的`pre_tool_call`块中的决策将具有优先权。第一个返回有效结果的块就会胜出——一旦有任何回调函数返回包含非空消息的`{"action": "block", "message": str}`格式的数据，聚合器就会立即终止执行。

## 出站Webhook

出站Webhook是[入站Webhook平台](/user-guide/messaging/webhooks)的推送式对应功能：入站Webhook用于在外部环境发生变化时唤醒Hermes，而出站Webhook则用于在Hermes执行某些操作时通知外部系统。只需配置一组HTTP端点以及它们关注的生命周期事件，每当有匹配的事件发生时，Hermes就会向这些端点发送经过签名的JSON数据包——无需接收端进行轮询操作。

常见应用场景包括：

- 在代理任务结束时通知CI系统或监控面板（`on_session_end`事件）
- 跟踪整个代理集群中各个子代理的任务完成情况（`subagent_stop`事件）
- 将工具的运行状态反馈给外部监控系统（通过带有`matcher`参数的`post_tool_call`函数）
- 唤醒*另一个*Hermes实例：只需将URL指向该实例的入站Webhook即可

### 配置方法

在`~/.hermes/config.yaml`文件中添加一个`hooks.outbound:`列表即可：

```yaml
hooks:
  outbound:
    - name: ci-notify                       # optional label for logs
      url: https://ci.example.com/hermes-events
      events: [on_session_end, subagent_stop]
      secret_env: HERMES_OUTBOUND_WEBHOOK_SECRET   # env var holding the HMAC secret
      timeout: 10                           # per-attempt seconds (1–60)

    - name: tool-monitor
      url: https://metrics.example.com/hooks/hermes
      events: [post_tool_call]
      matcher: "terminal|delegate_task"     # regex, tool-scoped events only
```

插件钩子集合中的任何事件都是有效的（如 `pre_tool_call`、`post_tool_call`、`pre_llm_call`、`post_llm_call`、`on_session_start`、`on_session_end`、`subagent_start`、`subagent_stop` 等）。格式错误的条目会触发警告并被跳过——有问题的 webhook 不会导致代理程序崩溃。配置更改将在下一次 CLI 会话或网关重启时生效。

关于密钥：建议使用 `secret_env`（即环境变量名称，通常设置在 `~/.hermes/.env` 文件中），而非直接写明 `secret:`，这样就能避免配置文件中出现敏感信息。未指定密钥的条目将以未签名形式发送（`hermes hooks list` 命令会将其标记为 `UNSIGNED`）。

### 数据格式

每次触发事件时，系统都会发送一个 JSON 数据体，其顶层结构与 shell 钩子的标准输入相同，同时还包含传输元数据。`profile` 字段用于标识发出该事件的 Hermes 配置文件（在未使用配置文件的情况下则为 `"default"`），这样通过多路复用网关接收数据的程序就能区分不同的配置文件。

```json
{
  "hook_event_name": "on_session_end",
  "profile": "default",
  "tool_name": null,
  "tool_input": null,
  "session_id": "sess_abc123",
  "cwd": "/home/user/project",
  "extra": {"completed": true, "interrupted": false, "model": "...", "platform": "cli"},
  "delivery_id": "3f2c9a...",
  "timestamp": "2026-07-22T14:00:00Z"
}
```

请求头：

| 请求头 | 值 |
|--------|-------|
| `Content-Type` | `application/json` |
| `X-Hermes-Event` | 钩子事件名称 |
| `X-Hermes-Delivery` | 每次交付的唯一标识——其值与请求体中的 `delivery_id` 相同 |
| `X-Hermes-Signature-256` | `sha256=<hex>` —— 采用 GitHub 风格的对原始请求体的 HMAC-SHA256 加密值；仅当已配置密钥时才会出现 |

请按照验证 GitHub webhook 的相同方式来校验该签名：

```python
import hashlib, hmac

def verify(body: bytes, header: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header)
```

由于 `delivery_id` 和 `timestamp` 位于已签名内容**内部**，经过验证的接收方也能自动获得重放保护功能：

- 根据 `delivery_id`（或对应的 `X-Hermes-Delivery` 请求头）进行**去重处理**——系统会记住近期出现过的 ID，从而跳过重复消息。Hermes 仅会对失败的交付尝试重试一次，因此同一个 ID 理论上可能会出现两次。
- 通过将 `timestamp` 与本地时间进行比对，并设置一定的容差窗口（通常默认为 5 分钟），来**拒绝过期的事件**。没有密钥的话，攻击者即便重放截获的请求，也无法伪造新的时间戳。

### 交付语义

- **无需操心，后台处理**。事件会立即被序列化并放入队列，由单个后台线程负责发送 HTTP POST 请求。即便目标端点响应缓慢或无法响应，也不会导致工具调用或智能体轮次停滞。  
- **仅用于通知**。与 shell 钩子不同，外发 webhook 无法阻止工具调用，也无法注入额外上下文——其响应内容会被直接忽略。它们仅能监控，无法干预流程。  
- **有限重试机制**。遇到连接错误或 5xx 状态码时，系统会进行一次带退避策略的重试；而 4xx 状态码则不会重试（因为接收方已表明请求本身有误）。失败情况会被记录后丢弃——传输为尽力而为模式，并不保证一定成功。  
- **绝不跟随重定向**。3xx 状态码会被视为配置错误并予以记录——若尝试跟随重定向后的地址发送请求，带签名的有效载荷将会被 silently 丢弃。请将 `url` 参数设置为最终目标地址。  
- **队列容量受限**。当队列出现积压（如目标端点故障或事件激增）时，新事件会被记录并警告，而不会占用无限的内存资源。  
- **无需用户确认**。外发目标不会在您的设备上执行任何代码——它们会在您配置的 URL 地址处接收数据。即使设置了 `HERMES_SAFE_MODE=1`，也仍会跳过注册流程，这一点与插件及 shell 钩子相同。需注意，有效载荷中包含工具输入参数和事件元数据，因此请确保仅将目标地址指向可信任的端点，并优先使用 `https://` 协议。  

`hermes hooks list` 命令可显示已配置的外发目标以及 shell 钩子信息，同时还会标注每个目标是否已进行签名处理。
