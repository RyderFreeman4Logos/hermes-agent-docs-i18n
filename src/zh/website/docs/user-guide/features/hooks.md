---
sidebar_position: 6
title: "Event Hooks"
description: "Run custom code at key lifecycle points — log activity, send alerts, post to webhooks"
---

# 事件钩子

Hermes 提供了三种钩子系统，可在关键生命周期节点执行自定义代码：

| 系统 | 注册方式 | 执行位置 | 典型用途 |
|------|-----------|---------|----------|
| **[网关钩子](#gateway-event-hooks)** | 通过 `~/.hermes/hooks/` 目录下的 `HOOK.yaml` 和 `handler.py` 文件 | 仅限网关层 | 日志记录、警报发送、Webhook 接收 |
| **[插件钩子](#plugin-hooks)** | 在 [插件](/user-guide/features/plugins) 中使用 `ctx.register_hook()` 方法 | CLI 及网关层 | 工具拦截、指标收集、规则校验 |
| **[Shell 钩子](#shell-hooks)** | 通过 `~/.hermes/config.yaml` 中的 `hooks:` 块指定 Shell 脚本 | CLI 及网关层 | 用于实现拦截、自动格式化、上下文注入等功能的插件式脚本 |

这三种系统均为非阻塞式设计——任何钩子中的错误都会被捕获并记录，而不会导致代理程序崩溃。

## 网关事件钩子

网关钩子会在处理 Telegram、Discord、Slack、WhatsApp、Teams 等消息时自动触发，且不会影响主代理流程的运行。

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

`events` 列表用于指定哪些事件会触发相应的处理函数。您可以订阅任意组合的事件，包括使用通配符如 `command:*`。 

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
- 接收参数包括 `event_type`（字符串类型）和 `context`（字典类型）
- 可以使用 `async def` 或普通 `def` 形式定义——两种方式均有效
- 程序中的错误会被捕获并记录，不会导致代理程序崩溃

### 可用的事件类型

| 事件类型 | 触发时机 | Context 包含的键 |
|---------|----------|------------------|
| `gateway:startup` | 网关进程启动时 | `platforms`（活跃平台名称列表） |
| `session:start` | 创建新的消息会话时 | `platform`、`user_id`、`session_id`、`session_key` |
| `session:end` | 会话结束（尚未重置前） | `platform`、`user_id`、`session_key` |
| `session:reset` | 用户执行 `/new` 或 `/reset` 命令时 | `platform`、`user_id`、`session_key` |
| `agent:start` | 代理开始处理消息时 | `platform`、`user_id`、`session_id`、`message` |
| `agent:step` | 工具调用循环的每次迭代时 | `platform`、`user_id`、`session_id`、`iteration`、`tool_names` |
| `agent:end` | 代理处理完成时 | `platform`、`user_id`、`session_id`、`message`、`response` |
| `command:*` | 任何斜杠命令被执行时 | `platform`、`user_id`、`command`、`args` |

#### 通配符匹配

注册了 `command:*` 的处理函数，将会对所有以 `command:` 开头的事件（如 `command:model`、`command:reset` 等）生效。只需一个订阅即可监控所有斜杠命令。

### 示例

#### 长任务时的 Telegram 警报功能

当代理程序的处理步骤超过 10 步时，向自己发送一条消息：

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

在新会话创建时向外部服务发送 POST 请求：

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

社区中流行的一种做法是将 Markdown 格式的检查清单放入 `~/.hermes/BOOT.md` 文件中，让代理在每次网关启动时自动执行该清单。这种做法非常实用，比如“每次启动时检查夜间运行的 cron 任务是否出错，如有异常则通过 Discord 发送通知”，或是“汇总过去 24 小时的 deploy.log 内容并发布到 Slack 的 #ops 频道中”。

本教程将指导您如何将其作为用户自定义钩子自行实现。Hermes 并未预置 BOOT.md 钩子——您可以根据自身需求定制具体的功能行为。

#### 我们要实现的功能

1. 在 `~/.hermes/BOOT.md` 中创建一个包含自然语言启动指令的文件。
2. 创建一个在 `gateway:startup` 事件触发时执行的网关钩子，该钩子会使用网关已解析的模型/凭据启动一个一次性代理，进而执行 BOOT.md 文件中的指令。
3. 设定 `[SILENT]` 规则，以便在无需报告任何信息时让代理选择不发送消息。

#### 第一步：编写您的检查清单

创建 `~/.hermes/BOOT.md` 文件。撰写内容时，可将其视为在向人工助手下达指令：

```markdown
# Startup Checklist

1. Run `hermes cron list` and check if any scheduled jobs failed overnight.
2. If any failed, summarize them for Discord #ops (the hook delivers your final response to its configured target).
3. Check if `/opt/app/deploy.log` has any ERROR lines from the last 24 hours. If yes, summarize them and include in the same report.
4. If nothing went wrong, reply with only `[SILENT]` so no message is sent.
```

智能体会将此内容视为其提示词的一部分，因此只要能用通俗语言描述的内容都可以——无论是工具调用、Shell命令、发送消息，还是文件总结。 

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
- `_resolve_runtime_agent_kwargs()` 会以与普通网关相同的机制来解析提供方凭证——包括 API 密钥、基础 URL、OAuth 令牌以及凭证池。

若缺少这些功能，单纯的 `AIAgent()` 对象将回退到内置默认设置，从而导致对任何非默认端点的请求均返回 401 错误。

#### 第 3 步：进行测试

重启网关：

```bash
hermes gateway restart
```

查看日志：

```bash
hermes logs --follow --level INFO | grep boot-md
```

当代理返回如 `[SILENT]` 这样的静默令牌时，您应会看到“正在运行 BOOT.md（N 个字符）”的提示，随后要么出现“boot-md 已完成：……”（说明代理的执行情况），要么显示“boot-md 已完成（无需报告）”。

若要禁用该检查清单，可删除 `~/.hermes/BOOT.md` 文件——即使该文件不存在，钩子仍会被加载，但会直接跳过相关操作。

#### 扩展使用方式

- **基于时间的检查清单**：在 BOOT.md 中的指令中取消对 `datetime.now().weekday()` 的依赖（例如“如果是周一，则同时检查每周部署日志”）。由于这些指令为自由文本形式，只要代理能够理解，任何逻辑均可实现。
- **多个检查清单**：将钩子指向不同的文件（如 `STARTUP.md`、`MORNING.md` 等），并为每个文件创建独立的钩子目录。
- **非代理版本**：如果您不需要完整的代理循环，可直接跳过 `AIAgent`，让处理程序通过 `httpx` 直接发送固定格式的通知。这种方式成本更低、速度更快，且无需依赖任何提供方。

#### 为何未作为内置功能

Hermes 的早期版本将此功能作为内置钩子，会在每个网关启动时自动以默认配置创建代理。这不仅让使用了自定义端点的用户感到意外，也让那些不知其正在运行的用户无法察觉该功能。将其作为需手动实现的文档化模式——由您在自身的钩子目录中创建——可以让您清晰了解其功能，并通过编写相应文件来选择是否启用。

### 工作原理

1. 网关启动时，`HookRegistry.discover_and_load()` 会扫描 `~/.hermes/hooks/` 目录。
2. 每个包含 `HOOK.yaml` 和 `handler.py` 文件的子目录都会被动态加载。
3. 处理程序会根据其声明的事件进行注册。
4. 在每个生命周期节点，`hooks.emit()` 会触发所有匹配的处理程序。
5. 任何处理程序中的错误都会被捕获并记录——即使某个钩子出错，也不会导致整个代理崩溃。

:::info
网关钩子仅在 **网关端**（Telegram、Discord、Slack、WhatsApp、Teams）触发。CLI 环境不会加载网关钩子。如需在所有场景下都生效的钩子，请使用[插件钩子](#plugin-hooks)。
:::

## 插件钩子

[插件](/user-guide/features/plugins)可以注册在**CLI 和网关环境**中均会触发的钩子。这些钩子可通过插件 `register()` 函数中的 `ctx.register_hook()` 方法以编程方式注册。

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
```

**所有钩子的通用规则：**

- 回调函数接收**关键字参数**。为确保向后兼容性，始终应接受 `**kwargs` 参数——未来版本可能会添加新参数，而不会影响您的插件正常运行。
- 如果某个回调发生**崩溃**，系统会将其记录并跳过该回调。其他钩子及智能体仍可正常工作。表现异常的插件绝不会导致智能体崩溃。
- 有两个钩子的返回值会影响行为：[`pre_tool_call`](#pre_tool_call) 可以**阻止**工具调用，而 [`pre_llm_call`](#pre_llm_call) 可以在向大语言模型发起请求时**注入上下文**。其余所有钩子均为仅触发即忽略的观察者。
- 观察者回调函数会自动接收 `telemetry_schema_version` 参数。若该参数存在，`turn_id`、`api_request_id`、`task_id`、`session_id` 和 `api_call_count` 则作为独立的关联字段。请将 `api_request_id` 视为不可解析的标识符，无需解析其字符串格式。

### 快速参考表

| 钩子名称 | 触发时机 | 返回值 |
|----------|----------|--------|
| [`pre_tool_call`](#pre_tool_call) | 任何工具执行之前 | `{"action": "block", "message": str}`，用于拒绝该工具调用 |
| [`post_tool_call`](#post_tool_call) | 任何工具返回之后 | 被忽略 |
| [`pre_llm_call`](#pre_llm_call) | 每轮对话中，在工具调用循环之前仅触发一次 | `{"context": str}`，用于在用户消息前添加上下文 |
| [`post_llm_call`](#post_llm_call) | 每轮对话中，在工具调用循环之后仅触发一次 | 被忽略 |
| [`on_session_start`](#on_session_start) | 创建新会话时（仅第一轮对话） | 被忽略 |
| [`on_session_end`](#on_session_end) | 会话结束时 | 被忽略 |
| [`on_session_finalize`](#on_session_finalize) | CLI或网关终止当前会话时（用于刷新、保存数据或统计信息） | 被忽略 |
| [`on_session_reset`](#on_session_reset) | 网关更换新的会话密钥时（例如通过 `/new` 或 `/reset` 指令） | 被忽略 |
| [`subagent_start`](#subagent_start) | 已创建待运行的 `delegate_task` 子智能体时 | 被忽略 |
| [`subagent_stop`](#subagent_stop) | `delegate_task` 子智能体已退出时 | 被忽略 |
| [`pre_gateway_dispatch`](#pre_gateway_dispatch) | 网关收到用户消息后，在进行身份验证和任务分发之前 | `{"action": "skip" \| "rewrite" \| "allow", ...}`，用于控制流程走向 |
| [`pre_approval_request`](#pre_approval_request) | 需要用户批准的危险指令在发送提示或通知之前 | 被忽略 |
| [`post_approval_response`](#post_approval_response) | 用户对批准提示作出响应（或超时）时 | 被忽略 |
| [`transform_tool_result`](#transform_tool_result) | 任何工具返回之后，在将结果传递给模型之前 | `str`，用于替换结果；`None`，表示保持原样 |
| [`transform_terminal_output`](#transform_terminal_output) | 在 `terminal` 工具内部，于内容截断、ANSI编码移除或敏感信息遮蔽之前 | `str`，用于替换原始输出；`None`，表示保持原样 |
| [`transform_llm_output`](#transform_llm_output) | 工具调用循环结束后，在最终响应返回给用户之前 | `str`，用于替换响应文本；`None` 或空字符串，表示保持原样 |

---

### `pre_tool_call`

在**每次工具执行之前立即触发**——无论是内置工具还是插件提供的工具。

**回调函数签名：**

```python
def my_callback(tool_name: str, args: dict, task_id: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 即将执行的工具名称（例如 `"terminal"`、`"web_search"`、`"read_file"`） |
| `args` | `dict` | 模型传递给该工具的参数 |
| `task_id` | `str` | 会话/任务标识符；若未设置则为空字符串 |

**触发时机：** 在 `model_tools.py` 文件的 `handle_function_call()` 函数内部，于工具处理程序执行之前触发。每次调用工具都会触发一次——如果模型同时调用3个工具，则会触发3次。

**返回值——拒绝调用：**

```python
return {"action": "block", "message": "Reason the tool call was blocked"}
```

该智能体会通过将 `message` 作为错误信息返回给模型，从而触发工具的短路处理。首先匹配到的块指令将会生效（优先考虑最先注册的 Python 插件，其次是 shell 钩子）。任何其他返回值都会被忽略，因此现有的仅用于监控的回调函数仍可照常运行。

**应用场景：** 日志记录、审计追踪、工具调用计数、阻止危险操作、速率限制以及按用户实施策略控制。

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
| `tool_name` | `str` | 刚刚执行过的工具名称 |
| `args` | `dict` | 模型传递给该工具的参数 |
| `result` | `str` | 工具的返回值（始终为 JSON 字符串） |
| `task_id` | `str` | 会话/任务标识符。若未设置则为空字符串 |
| `duration_ms` | `int` | 工具被调用的耗时，以毫秒为单位（通过在 `registry.dispatch()` 附近使用 `time.monotonic()` 进行测量） |

**触发时机：** 在 `model_tools.py` 文件的 `handle_function_call()` 函数中，工具处理程序返回之后触发。每次调用工具都会触发一次。如果工具抛出了未处理的异常，则不会触发该事件（错误会被捕获并作为错误 JSON 字符串返回，此时 `post_tool_call` 会使用该错误字符串作为 `result` 参数被触发）。

**返回值：** 被忽略。

**应用场景：** 记录工具执行结果、收集指标数据、追踪工具的成功/失败率、生成延迟监控面板、针对不同工具设置使用限额提醒，以及在特定工具执行完成时发送通知。

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

该钩子在每轮对话开始、工具调用循环启动之前**触发一次**。它是**唯一一个其返回值会被使用的钩子**——可通过它将上下文注入到当前轮次的用户消息中。

**回调函数签名：**

```python
def my_callback(session_id: str, user_message: str, conversation_history: list,
                is_first_turn: bool, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 该轮对话中用户发送的原始消息（在应用任何技能处理之前） |
| `conversation_history` | `list` | 完整消息列表的副本（采用 OpenAI 格式：`[{"role": "user", "content": "..."}]`） |
| `is_first_turn` | `bool` | 若为新会话的第一轮则值为 `True`，后续轮次则为 `False` |
| `model` | `str` | 模型标识符（例如 `"anthropic/claude-sonnet-4.6"`） |
| `platform` | `str` | 会话运行的平台：`"cli"`、`"telegram"`、`"discord"` 等 |

**触发时机：** 在 `run_agent.py` 文件的 `run_conversation()` 函数中，上下文压缩之后、主 `while` 循环之前触发。每次调用 `run_conversation()`（即每轮用户对话）都会触发一次，而非工具循环中的每次 API 调用都会触发。

**返回值：** 如果回调函数返回一个包含 `"context"` 键的字典，或是一个非空的普通字符串，则该文本会被追加到当前轮次的用户消息中。若无需进行任何内容注入，则返回 `None`。

```python
# Inject context
return {"context": "Recalled memories:\n- User likes Python\n- Working on hermes-agent"}

# Plain string (equivalent)
return "Recalled memories:\n- User likes Python"

# No injection
return None
```

**上下文注入的位置：**始终为**用户消息**，而非系统提示词。这样做有助于保留提示词缓存——由于系统提示词在多轮对话中保持不变，因此已缓存的标记可以被重复使用。系统提示词负责管理模型的行为引导、工具调用规则、角色设定以及各项技能。插件则与用户输入一同提供上下文。

所有注入的上下文均为**临时性**的——仅在调用 API 时添加。对话历史中的原始用户消息不会被修改，也不会有任何内容被保存到会话数据库中。

当**多个插件**返回上下文时，它们的输出会按照插件发现顺序（按目录名称的字母顺序）用双换行符连接起来。

**应用场景：**记忆召回、RAG上下文注入、行为规范设置以及每轮对话分析。

**示例——记忆召回：**

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

**示例——防护规则：**

```python
POLICY = "Never execute commands that delete files without explicit user confirmation."

def guardrails(**kwargs):
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", guardrails)
```

### `post_llm_call`

该函数在**每轮对话结束后**触发一次，即工具调用循环完成且智能体已生成最终响应之后。仅会在**成功完成**的轮次中触发——若某轮对话被中断，则不会触发。

**回调函数签名：**

```python
def my_callback(session_id: str, user_message: str, assistant_response: str,
                conversation_history: list, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 用户在本轮对话中输入的原始消息 |
| `assistant_response` | `str` | 智能体在本轮对话中给出的最终文本回复 |
| `conversation_history` | `list` | 本轮对话结束后完整的消息记录副本 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的平台 |

**触发条件：** 在 `run_agent.py` 文件的 `run_conversation()` 函数中，工具循环处理完并返回最终回复后触发。该逻辑由 `if final_response and not interrupted` 控制——因此当用户在对话进行过程中中断，或智能体达到迭代次数上限仍未生成回复时，不会触发。

**返回值：** 无需返回值。

**应用场景：** 将对话数据同步至外部内存系统、计算回复质量指标、记录对话摘要、触发后续操作。

**示例——同步到外部内存：**

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

### `on_session_start`

在创建一个全新的会话时触发**一次**。在会话继续进行时（即用户在现有会话中发送第二条消息时）**不会**触发。

**回调函数签名：**

```python
def my_callback(session_id: str, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的唯一标识符 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的平台 |

**触发时机：** 在 `run_agent.py` 文件的 `run_conversation()` 函数中，于新会话的第一个轮次——即系统提示语生成之后、工具调用循环开始之前。判断条件为 `if not conversation_history`（没有历史消息则说明是新会话）。

**返回值：** 该参数的值将被忽略。

**应用场景：** 初始化会话级状态、预热缓存、将会话注册到外部服务、记录会话启动信息。

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
| `completed` | `bool` | 若智能体已生成最终响应则为 `True`，否则为 `False` |
| `interrupted` | `bool` | 若当前轮次被中断（用户发送新消息、输入 `/stop` 或退出程序）则为 `True` |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的平台 |

**触发时机：** 在两个位置触发：
1. **`run_agent.py`** —— 每次调用 `run_conversation()` 之后、所有清理工作完成时。即使当前轮次出现错误，也会触发。
2. **`cli.py`** —— 在 CLI 的 atexit 处理程序中，但**仅限于**在程序退出时智能体正处于处理中（即 `_agent_running=True`）的情况。该机制可捕获处理过程中的 Ctrl+C 和 `/exit` 操作。此时 `completed=False` 且 `interrupted=True`。

**返回值：** 该参数的值会被忽略。

**应用场景：** 清空缓冲区、关闭连接、保存会话状态、记录会话时长，以及清理在 `on_session_start` 中初始化的资源。

**示例 —— 清空缓冲区与资源清理：**

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

当 CLI 或网关**终止**一个正在使用的会话时触发——例如用户执行 `/new` 命令、网关回收了空闲会话，或是 CLI 在仍有活跃代理的情况下退出。这是在该会话被完全移除之前，最后一次清理与其相关的状态的机会。

**回调函数签名：**

```python
def my_callback(session_id: str | None, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` 或 `None` | 对外使用的会话 ID。若当前没有活跃会话，则该值为 `None`。 |
| `platform` | `str` | 值为 `"cli"`，或消息平台名称（如 `"telegram"`、`"discord"` 等）。 |

**触发时机：** 在 `cli.py` 中（在调用 `/new` 或 CLI 退出时），以及在 `gateway/run.py` 中（当会话被重置或垃圾回收时）。在网关端始终与 `on_session_reset` 配合使用。

**返回值：** 无需处理。

**应用场景：** 在会话 ID 被丢弃之前保存最终的会话指标，关闭与会话相关的资源，发送最终的遥测事件，清空队列中的待写入数据。---

### `on_session_reset`

当网关为当前对话**更换新的会话密钥**时触发——即用户调用了 `/new`、`/reset`、`/clear`，或者适配器在空闲一段时间后选择了新的会话。这使插件能够在无需等待下一次 `on_session_start` 的情况下，及时响应对话状态已被清除的情况。

**回调函数签名：**

```python
def my_callback(session_id: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的 ID（已更新为最新值）。 |
| `platform` | `str` | 消息平台名称。 |

**触发时机：** 在 `gateway/run.py` 中，新会话密钥分配完成后、处理下一条入站消息之前触发。在网关端，执行顺序为：首次接收到入站消息时，依次执行 `on_session_finalize(old_id)` → 密钥替换 → `on_session_reset(new_id)` → `on_session_start(new_id)`。 

**返回值：** 该参数会被忽略。

**应用场景：** 重置以 `session_id` 为键的会话级缓存，生成“会话已更换”的分析数据，为新的状态存储桶初始化数据。

---

如需包含工具架构、处理函数及高级钩子模式的完整操作指南，请参阅 **[构建插件指南](/guides/build-a-hermes-plugin)**。

---

### `subagent_start`

在 `delegate_task` 构建完子代理 `AIAgent` 之后、该子代理开始运行之前，**每个子代理仅触发一次**。无论您是委托单个任务还是三组任务，此钩子都会为每个子代理触发一次。

该钩子专用于代理/子代理的生命周期管理，并非适用于网关、CLI、cron、批处理、MoA 或其他由运行器发起的代理执行的通用“在任何代理调用之前”触发点。

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
| `parent_turn_id` | `str` | 发起委托的上级代理轮次的 ID（如有）。 |
| `parent_subagent_id` | `str \| None` | 当该子代理由其他子代理创建时的上级子代理 ID；顶级上级代理则为 `None`。 |
| `child_session_id` | `str \| None` | 为子代理分配的会话 ID。 |
| `child_subagent_id` | `str` | 用于委托监控与控制的稳定子代理 ID。 |
| `child_role` | `str` | 应用委托策略后的实际子代理角色，例如 `"leaf"` 或 `"orchestrator"`。 |
| `child_goal` | `str` | 子代理将执行的委托目标/提示语。 |

**触发时机：** 在 `tools/delegate_tool.py` 文件的 `_build_child_agent()` 函数中，即在构建完子 `AIAgent` 并为其添加子代理身份元数据之后、调用 `_run_single_child()` 运行子代理之前。

**返回值：** 该参数将被忽略。这仅是一个观察者钩子；返回值不会阻止子代理的运行，也不会对其造成任何修改。

**应用场景：** 记录子代理的创建过程、映射上下级会话关系、追踪嵌套的委托结构、生成运行前的审计记录、预先为每个子代理分配监控资源。

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
`subagent_start` 功能有助于实现任务委派的可视化监控，但它并非用于阻塞操作的策略钩子。若希望在子代理生成之前阻止任务委派，应使用 [`pre_tool_call`](#pre_tool_call) 来拦截 `delegate_task` 工具调用。  
:::

---

### `subagent_stop`

在 `delegate_task` 执行完成之后，**每个子代理仅触发一次**。无论您是委派单个任务还是三批任务，该钩子都会针对每个子代理触发一次，且所有触发会在父线程中依次处理。  

**回调函数签名：**

```python
def my_callback(parent_session_id: str, child_role: str | None,
                child_summary: str | None, child_status: str,
                duration_ms: int, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `parent_session_id` | `str` | 上级代理的会话 ID |
| `child_role` | `str \| None` | 分配给子代理的协调器角色标签（若该功能未启用，则为 `None`） |
| `child_summary` | `str \| None` | 子代理返回给上级代理的最终响应 |
| `child_status` | `str` | 可取值为 `"completed"`、`"failed"`、`"interrupted"` 或 `"error"` |
| `duration_ms` | `int` | 子代理运行所消耗的实时时长，单位为毫秒 |

**触发时机：** 在 `tools/delegate_tool.py` 文件中，当 `ThreadPoolExecutor.as_completed()` 处理完所有子任务后触发。该触发操作会被传递到上级线程，从而无需开发者自行处理并发回调的执行问题。

**返回值：** 该参数将被忽略。

**应用场景：** 记录协调器操作日志、统计子代理运行时长以用于计费、生成任务委派后的审计记录。

**示例——记录协调器操作日志：**

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
在高度委托的场景下（例如：协调器角色 × 5个叶子节点 × 嵌套层级），`subagent_stop`会在每个轮次中触发多次。请确保回调函数执行速度尽可能快；将耗时较长的操作放到后台队列中处理。
:::

---

### `pre_gateway_dispatch`

该函数在网关中**每当收到一个`MessageEvent`时触发一次**，位于内部事件检测之后，但认证/配对以及代理调度之前。对于那些无法完全适配于任何单一平台适配器的网关级消息流策略（如仅监听窗口、人工干预、按聊天会话路由等），此处正是实施这些策略的拦截点。

**回调函数签名：**

```python
def my_callback(event, gateway, session_store, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `event` | `MessageEvent` | 标准化的传入消息（包含`.text`、`.source`、`.message_id`、`.internal`等字段）。 |
| `gateway` | `GatewayRunner` | 当前正在运行的网关运行器，插件可通过`gateway.adapters[platform].send(...)`发送旁路回复（如通知消息发送者等）。 |
| `session_store` | `SessionStore` | 用于通过`session_store.append_to_transcript(...)`实现静默记录对话内容。 |

**触发时机：** 在`gateway/run.py`文件中的`GatewayRunner._handle_message()`方法内，于计算出`is_internal`值之后立即触发。**内部事件将完全跳过此钩子**（这类事件由系统生成，如后台处理完成等，不应受面向用户的策略限制）。

**返回值：** `None`或字典。第一个被识别的操作字典将生效，其余插件的处理结果将被忽略。插件回调中的异常会被捕获并记录；出现错误时，网关会始终继续执行正常的消息分发流程。

| 返回值 | 效果 |
|--------|------|
| `{"action": "skip", "reason": "..."}` | 直接丢弃该消息——不生成智能体回复，也不触发配对流程或认证步骤。假设插件已处理该消息（例如将其静默记录到对话文本中）。 |
| `{"action": "rewrite", "text": "new text"}` | 替换`event.text`的值，然后使用修改后的消息继续正常的消息分发流程。此方式可用于将缓冲的背景消息合并为单个提示词。 |
| `{"action": "allow"}` / `None` | 执行正常的分发流程——运行完整的认证/配对/智能体循环流程。 |

**应用场景：** 仅监听模式的群组聊天（仅在被标记时回复；将背景消息缓存到上下文中）；人工接管模式（在负责人手动处理聊天时，将客户消息静默记录下来）；按用户配置文件实施速率限制；基于策略的路由控制。

**示例——静默丢弃未经授权的私信，且不触发配对码生成：**

```python
def deny_unauthorized_dms(event, **kwargs):
    src = event.source
    if src.chat_type == "dm" and not _is_approved_user(src.user_id):
        return {"action": "skip", "reason": "unauthorized-dm"}
    return None

def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", deny_unauthorized_dms)
```

**示例——在被提及时将环境消息缓冲区重写为单个提示词：**

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

### `pre_approval_request`

该指令会在审批请求展示给用户**之前立即触发**——适用于所有交互场景：命令行界面、Ink TUI、各类网关平台（Telegram、Discord、Slack、WhatsApp、Matrix等），以及ACP客户端（VS Code、Zed、JetBrains）。

这是集成自定义通知功能的理想位置——例如，可以添加一个macOS菜单栏应用来弹出允许/拒绝的通知，或创建审计日志以记录每一条包含详细上下文的审批请求。

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
| `command` | `str` | 需要审批的 Shell 命令 |
| `description` | `str` | 该命令被标记的原因（当多个模式同时匹配时，这些原因会合并显示） |
| `pattern_key` | `str` | 触发审批的主要模式键（例如 `"rm_rf"`、`"sudo"`） |
| `pattern_keys` | `list[str]` | 所有匹配的模式键 |
| `session_key` | `str` | 会话标识符，有助于针对单次聊天精准发送通知 |
| `surface` | `str` | `"cli"` 表示交互式 CLI/TUI 提示；`"gateway"` 表示异步平台审批 |

**返回值：** 无需考虑。此处的钩子仅具有观察功能，无法否决审批或预先回复。若需在工具进入审批系统之前进行拦截，请使用 [`pre_tool_call`](#pre_tool_call)。

**应用场景：** 桌面通知、推送提醒、审计日志记录、Slack Webhook、升级路由处理、指标统计。

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

在用户对审批提示作出响应后（或该提示超时后）触发。

**回调签名：**

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

与 `pre_approval_request` 使用相同的关键字参数，此外还需包含：

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `choice` | `str` | 必须为 `"once"`、`"session"`、`"always"`、`"deny"` 或 `"timeout"` 之一 |

**返回值：** 无需返回值。

**应用场景：** 关闭对应的桌面通知，将最终决策记录到审计日志中，更新相关指标，以及继续执行速率限制机制。

```python
def log_decision(command, choice, session_key, **kwargs):
    logger.info("approval %s: %s for session %s", choice, command[:60], session_key)

def register(ctx):
    ctx.register_hook("post_approval_response", log_decision)
```

### `transform_tool_result`

在工具返回之后、结果被添加到对话内容之前触发。该功能允许插件在模型看到结果之前，重写任意工具的输出字符串——而不仅限于终端输出。

**回调函数签名：**

```python
def my_callback(
    tool_name: str,
    arguments: dict,
    result: str,
    task_id: str | None,
    **kwargs,
) -> str | None:
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 生成结果的工具名称（如 `read_file`、`web_extract`、`delegate_task` 等）。 |
| `arguments` | `dict` | 模型传递给该工具的参数。 |
| `result` | `str` | 工具返回的原始结果字符串，已进行截断处理并去除了 ANSI 格式符。 |
| `task_id` | `str \| None` | 在 RL/benchmark 环境中运行时使用的任务/会话 ID。 |

**返回值：** 若需替换结果，则返回 `str` 类型（模型将看到此返回的字符串）；若保持原样，则返回 `None`。

**应用场景：** 从 `web_extract` 的输出中删除与特定机构相关的敏感信息，为较长的 JSON 工具响应添加摘要标题，向 `read_file` 的结果中注入检索增强提示，以及将 `delegate_task` 子智能体的报告重写为符合项目特定结构的格式。

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

该功能适用于所有工具。如需仅针对终端输出的重写处理，请参阅下方的 `transform_terminal_output` —— 其功能范围更为有限，且会在处理流程的更早阶段执行（即在数据截断和敏感信息遮蔽之前）。

---

### `transform_terminal_output`

该函数在 `terminal` 工具的前端输出处理流程中运行，**在**默认的 50 KB 截断、ANSI 格式清除以及敏感信息遮蔽操作之前执行。它允许插件在后续处理对原始 stdout/stderr 进行操作之前，对其内容进行重新编写。

**回调函数签名：**

```python
def my_callback(
    command: str,
    output: str,
    exit_code: int,
    cwd: str,
    task_id: str | None,
    **kwargs,
) -> str | None:
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `command` | `str` | 生成该输出的Shell命令。 |
| `output` | `str` | 原始的stdout/stderr合并内容（可能体积极大——会在钩子处理前被截断）。 |
| `exit_code` | `int` | 进程退出码。 |
| `cwd` | `str` | 命令运行的工作目录。 |

**返回值：** 返回 `str` 以替换现有输出，或返回 `None` 以保持原样。

**应用场景：** 为那些会产生大量输出的命令（如 `du -ah`、`find`、`tree`）注入摘要；用项目专属标记对输出进行标注，以便后续钩子知晓如何处理；去除多次运行间产生的时间波动噪声，从而避免破坏提示词缓存功能。

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

与 `transform_tool_result`（适用于其他所有工具）搭配使用效果最佳。

---

### `transform_llm_output`

在工具调用循环结束且模型生成最终响应后、该响应被传递给用户（通过 CLI、网关或程序化调用方式）之前，**每轮对话仅触发一次**。该功能允许插件利用传统编程方法重写助手的最终文本，无需为基于 SOUL 模型的文本处理或技能驱动的转换消耗额外的推理令牌。

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
| `session_id` | `str` | 当前对话的会话 ID（一次性任务可能为空）。 |
| `model` | `str` | 生成该回复的模型名称（例如 `anthropic/claude-sonnet-4.6`）。 |
| `platform` | `str` | 输出平台（`cli`、`telegram`、`discord` 等；未设置时为空）。 |

**返回值：** 若需替换回复文本，则返回非空字符串；若保持原样，则返回 `None` 或空字符串。当多个插件同时注册时，**第一个非空字符串将被采用**，这一规则与 `transform_tool_result` 相同。

**应用场景：** 对回复内容进行风格/词汇转换（如海盗语、海绵宝宝式语气），从最终文本中删除用户专属标识符，添加项目专用签名页脚，以及在无需消耗 SOUL 指令令牌的情况下强制执行企业风格指南。

```python
import os, re

def spongebob(response_text, **kwargs):
    if os.environ.get("SPONGEBOB_MODE") != "on":
        return None  # pass through unchanged
    return re.sub(r"!", "!! Tartar sauce!", response_text)

def register(ctx):
    ctx.register_hook("transform_llm_output", spongebob)
```

该钩子仅在接收到非空且连续的响应时才会触发——若因用户点击停止按钮而中断或出现空轮次，则不会启动。异常情况会被记录为警告，不会导致智能体执行流程中断。

---

## Shell 钩子

在 `cli-config.yaml` 中声明 shell 脚本钩子，每当对应的插件钩子事件触发时，Hermes 就会在 CLI 和网关会话中以子进程的形式运行这些脚本。无需编写 Python 插件。

当您希望使用一个即插即用的单文件脚本（Bash、Python 或任何带有 shebang 的语言）来实现以下功能时，可使用 Shell 钩子：

- **阻止工具调用**——拒绝危险的 `terminal` 命令，实施按目录划分的策略，对具有破坏性的 `write_file` / `patch` 操作要求事先批准。
- **在工具调用后执行**——自动格式化智能体刚刚生成的 Python 或 TypeScript 文件，记录 API 调用信息，触发 CI 工作流。
- **向下一轮 LLM 对话注入上下文**——在用户消息的开头添加 `git status` 的输出结果、当前星期几或获取到的文档内容（详见 [`pre_llm_call`](#pre_llm_call)）。
- **监控生命周期事件**——在子智能体完成任务（`subagent_stop`）或会话开始（`on_session_start`）时记录日志。

Shell 钩子可通过在 CLI 启动时（`hermes_cli/main.py`）和网关启动时（`gateway/run.py`）调用 `agent.shell_hooks.register_from_config(cfg)` 来注册。它们可以与 Python 插件钩子自然协同工作——两者均通过相同的调度器处理。

### 一览对比表

| 维度 | Shell 钩子 | [插件钩子](#plugin-hooks) | [网关钩子](#gateway-event-hooks) |
|------|-------------|-------------------------------|-----------------------------------|
| 声明位置 | `~/.hermes/config.yaml` 中的 `hooks:` 块 | `plugin.yaml` 插件中的 `register()` 函数 | `HOOK.yaml` 文件及 `handler.py` 目录 |
| 存放路径 | （按惯例）`~/.hermes/agent-hooks/` | `~/.hermes/plugins/<名称>/` | `~/.hermes/hooks/<名称>/` |
| 支持语言 | 任意语言（Bash、Python、Go 可执行文件等） | 仅限 Python | 仅限 Python |
| 运行环境 | CLI + 网关 | CLI + 网关 | 仅限网关 |
| 触发事件 | `VALID_HOOKS`（包括 `subagent_stop`） | `VALID_HOOKS` | 网关生命周期事件（`gateway:startup`、`agent:*`、`command:*`） |
| 是否可阻止工具调用 | 是（`pre_tool_call`） | 是（`pre_tool_call`） | 否 |
| 是否可注入 LLM 上下文 | 是（`pre_llm_call`） | 是（`pre_llm_call`） | 否 |
| 同意机制 | 每对 `(事件, 命令)` 需在首次使用时进行提示 | 默认启用（基于对 Python 插件的信任） | 默认启用（基于对目录的信任） |
| 进程隔离程度 | 是（通过子进程实现） | 否（同进程执行） | 否（同进程执行） |

### 配置结构说明

```yaml
hooks:
  <event_name>:                  # Must be in VALID_HOOKS
    - matcher: "<regex>"         # Optional; used for pre/post_tool_call only
      command: "<shell command>" # Required; runs via shlex.split, shell=False
      timeout: <seconds>         # Optional; default 60, capped at 300

hooks_auto_accept: false         # See "Consent model" below
```

事件名称必须属于[插件钩子事件](#plugin-hooks)之一；若输入有误，系统会显示“您是指X吗？”的警告并跳过该事件。单个条目中未知的键会被忽略；若缺少`command`字段，则会发出警告并跳过该事件。若`timeout > 300`，系统也会发出警告并对该值进行限制。

### JSON 数据传输协议

每当有事件触发时，Hermes会根据匹配的钩子（在匹配器允许的情况下）为每个钩子启动一个子进程，将JSON格式的数据通过**stdin**传递给该进程，然后再以JSON格式从**stdout**读取返回数据。

**stdin — 脚本接收到的数据载荷：**

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

// Inject context for pre_llm_call:
{"context": "Today is Friday, 2026-04-17"}

// Silent no-op — any empty / non-matching output is fine:
```

格式错误的 JSON 数据、非零退出码以及超时情况仅会记录警告信息，而不会中断代理循环。

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

该智能体对文件的内联视图**不会**自动重新读取——格式化操作仅会影响磁盘上的文件。后续的 `read_file` 调用将会读取到已格式化后的版本。

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

#### 3. 在每一轮对话中都插入 `git status` 命令（相当于 Claude-Code 的 `UserPromptSubmit` 功能）

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

Claude Code 的 `UserPromptSubmit` 事件并未被刻意设计为独立的 Hermes 事件——`pre_llm_call` 会在同一环节触发，且已具备上下文注入功能。因此请在此处使用它。

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

每当 Hermes 首次遇到独特的 `(事件, 命令)` 对时，都会向用户请求批准，随后会将该决策保存至 `~/.hermes/shell-hooks-allowlist.json` 文件中。后续的运行（无论是通过 CLI 还是网关）都将跳过此提示。

有三种方式可以绕过交互式提示——任意一种均可：

1. 在 CLI 中使用 `--accept-hooks` 参数（例如：`hermes --accept-hooks chat`）
2. 设置 `HERMES_ACCEPT_HOOKS=1` 环境变量
3. 在 `cli-config.yaml` 中将 `hooks_auto_accept` 设置为 `true`

在非 TTY 环境下运行（如网关、cron 任务或 CI 环境）时，必须使用上述三种方式之一；否则任何新添加的钩子都会被默默忽略且会记录警告信息。

**对脚本的修改会被默认视为有效。** 允许列表是依据确切的命令字符串来识别的，而非脚本的哈希值，因此对磁盘上的脚本进行修改不会导致之前的同意失效。`hermes hooks doctor` 命令能够检测文件修改时间的变化，帮助你发现脚本已被修改，并决定是否需要重新批准。

#### 手动添加允许项

对于无法通过交互方式回应首次使用提示的非 TTY 环境或服务账户部署场景，手动添加允许项非常实用。允许列表文件位于 `~/.hermes/shell-hooks-allowlist.json`，其预期格式为一个 `approvals` 数组。每条批准记录都会包含对应的钩子 `事件` 以及确切的 `命令` 字符串：

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

命令字符串必须与已配置的钩子命令完全一致。包含 `sha256` 字段的路径键对象并不符合预期格式，因此不会被批准用于该钩子。建议使用 `hermes hooks list` 命令来验证手动输入的内容。

### `hermes hooks` CLI 命令

| 命令 | 功能说明 |
|---------|----------|
| `hermes hooks list` | 列出所有已配置的钩子，包括匹配规则、超时设置以及授权状态 |
| `hermes hooks test <event> [--for-tool X] [--payload-file F]` | 使用模拟请求触发所有匹配的钩子，并输出解析后的响应结果 |
| `hermes hooks revoke <command>` | 删除所有与 `<command>` 匹配的允许列表项（更改将在下次重启后生效） |
| `hermes hooks doctor` | 对每个已配置的钩子进行检查：包括执行权限、允许列表状态、修改时间偏差、JSON 输出有效性以及大致的执行时间 |

### 安全性

Shell 钩子是以**完整的用户凭证**来运行的，其信任级别与 cron 任务或 shell 别名相同。因此，请将 `config.yaml` 文件中的 `hooks:` 部分视为高权限配置：

- 仅引用您自己编写或经过彻底审查的脚本。
- 将脚本保存在 `~/.hermes/agent-hooks/` 目录下，以便于进行路径审计。
- 在拉取共享配置后，重新运行 `hermes hooks doctor`，以便在新的钩子注册之前及时发现它们。
- 如果您的 `config.yaml` 文件是在团队内部进行版本控制的，请像审查 CI 配置一样仔细检查所有修改了 `hooks:` 部分的提交请求。

### 执行顺序与优先级

Python 插件钩子和 Shell 钩子都会通过同一个 `invoke_hook()` 调度器来处理。Python 插件会首先被注册（通过 `discover_and_load()` 函数），而 Shell 钩子则在之后注册（通过 `register_from_config()` 函数）。因此在出现冲突时，Python 的 `pre_tool_call` 块中的决策将具有优先权。只要有任何回调函数返回包含非空消息的 `{"action": "block", "message": str}` 对象，聚合器就会立即停止后续处理并返回结果。
