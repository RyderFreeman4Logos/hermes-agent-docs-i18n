---
sidebar_position: 9
---

# 添加平台适配器

本指南介绍如何将新的消息传递平台集成到 Hermes 网关中。平台适配器负责连接 Hermes 与外部消息服务（如 Telegram、Discord、企业微信等），从而使用户能够通过这些服务与智能体进行交互。

:::提示
添加平台有两种方式：
- **插件方式**（推荐用于社区或第三方开发）：只需将插件目录放入 `~/.hermes/plugins/` 即可，无需修改任何核心代码。详情请参见下文的[插件路径](#plugin-path-recommended)。
- **内置方式**：需要修改代码、配置文件及文档中的20多个相关文件。可使用下文的[内置集成检查清单](#step-by-step-checklist-built-in-path)进行参考。
:::

## 架构概览

```
User ↔ Messaging Platform ↔ Platform Adapter ↔ Gateway Runner ↔ AIAgent
```

每个适配器都继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter`，并实现以下功能：

- **`connect()`** — 建立连接（WebSocket、长轮询、HTTP 服务器等）*（抽象方法）*
- **`disconnect()`** — 正常关闭连接 *（抽象方法）*
- **`send()`** — 向聊天窗口发送文本消息 *（抽象方法）*
- **`send_typing()`** — 显示输入中状态指示器（可选择性重写）
- **`get_chat_info()`** — 返回聊天元数据（可选择性重写）

适配器负责接收传入的消息，然后通过 `self.handle_message(event)` 方法将其转发，而基类则会将请求路由至网关运行器。

## 插件路径（推荐方式）

插件系统允许您在不修改任何 Hermes 核心代码的情况下添加平台适配器。您的插件是一个包含两个文件的目录：

```
~/.hermes/plugins/my-platform/
  plugin.yaml      # Plugin metadata
  adapter.py       # Adapter class + register() entry point
```

### plugin.yaml

插件元数据。`requires_env` 和 `optional_env` 部分会自动填充到 `hermes config` 用户界面中（详情请参见下文的[环境变量展示](#surfacing-env-vars-in-hermes-config)）。

```yaml
name: my-platform
label: My Platform
kind: platform
version: 1.0.0
description: My custom messaging platform adapter
author: Your Name
requires_env:
  - MY_PLATFORM_TOKEN          # bare string works
  - name: MY_PLATFORM_CHANNEL  # or rich dict for better UX
    description: "Channel to join"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery"
    password: false
```

### adapter.py 文件

```python
import os
from gateway.platforms.base import (
    BasePlatformAdapter, SendResult, MessageEvent, MessageType,
)
from gateway.config import Platform, PlatformConfig


class MyPlatformAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform("my_platform"))
        extra = config.extra or {}
        self.token = os.getenv("MY_PLATFORM_TOKEN") or extra.get("token", "")

    async def connect(self) -> bool:
        # Connect to the platform API, start listeners
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # Send message via platform API
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}


def check_requirements() -> bool:
    return bool(os.getenv("MY_PLATFORM_TOKEN"))


def validate_config(config) -> bool:
    extra = getattr(config, "extra", {}) or {}
    return bool(os.getenv("MY_PLATFORM_TOKEN") or extra.get("token"))


def _env_enablement() -> dict | None:
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {"chat_id": home, "name": "Home"}
    return seed


def register(ctx):
    """Plugin entry point — called by the Hermes plugin system."""
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        required_env=["MY_PLATFORM_TOKEN"],
        install_hint="pip install my-platform-sdk",
        # Env-driven auto-configuration — seeds PlatformConfig.extra from
        # env vars before adapter construction. See "Env-Driven Auto-
        # Configuration" section below.
        env_enablement_fn=_env_enablement,
        # Cron home-channel delivery support. Lets deliver=my_platform cron
        # jobs route without editing cron/scheduler.py. See "Cron Delivery"
        # section below.
        cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
        # Per-platform user authorization env vars
        allowed_users_env="MY_PLATFORM_ALLOWED_USERS",
        allow_all_env="MY_PLATFORM_ALLOW_ALL_USERS",
        # Message length limit for smart chunking (0 = no limit)
        max_message_length=4000,
        # LLM guidance injected into system prompt
        platform_hint=(
            "You are chatting via My Platform. "
            "It supports markdown formatting."
        ),
        # Display
        emoji="💬",
    )

    # Optional: register platform-specific tools
    ctx.register_tool(
        name="my_platform_search",
        toolset="my_platform",
        schema={...},
        handler=my_search_handler,
    )
```

### 配置

用户可通过 `config.yaml` 文件对平台进行配置：

```yaml
gateway:
  platforms:
    my_platform:
      enabled: true
      extra:
        token: "..."
        channel: "#general"
```

或者通过环境变量实现（适配器会在 `__init__` 方法中读取这些变量）。

### 插件系统自动处理的流程

当您调用 `ctx.register_platform()` 时，以下集成环节将由系统自动处理——无需修改核心代码：

| 集成环节 | 工作原理 |
|---|---|
| 网关适配器创建 | 先检查注册表，若未找到则使用内置的 if/elif 判断链 |
| 配置解析 | `Platform._missing_()` 函数可接受任意平台名称 |
| 已连接平台验证 | 调用注册表的 `validate_config()` 方法进行验证 |
| 用户授权检查 | 检查 `allowed_users_env` 和 `allow_all_env` 环境变量 |
| 仅基于环境的自动启用 | `env_enablement_fn` 函数会设置 `PlatformConfig.extra` 及 `home_channel` 的值 |
| YAML 配置转换 | `apply_yaml_config_fn` 函数负责将 `config.yaml` 中的键值转换为环境变量或额外配置项 |
| Cron 定时任务触发 | `cron_deliver_env_var` 函数使 `deliver=<name>` 的写法能够正常工作 |
| `hermes config` 用户界面显示 | `plugin.yaml` 文件中的 `requires_env` 和 `optional_env` 设置会自动填充到界面中 |
| `send_message` 工具 | 消息将通过实时网关适配器进行传输 |
| Webhook 跨平台发送 | 系统会先检查注册表，确认目标平台是否存在 |
| `/update` 命令访问权限 | 通过 `allow_update_command` 标志控制访问权限 |
| 频道目录展示 | 插件支持的平台会显示在频道列表中 |
| 系统提示信息 | `platform_hint` 值会被注入到大语言模型的上下文中 |
| 消息分片处理 | 根据 `max_message_length` 参数智能分割长消息 |
| 个人身份信息脱敏 | 通过 `pii_safe` 标志实现敏感信息保护 |
| `hermes status` 状态显示 | 插件支持的平台会以 `(plugin)` 标签显示 |
| `hermes gateway setup` 设置界面 | 插件支持的平台会出现在设置菜单中 |
| `hermes tools` / `hermes skills` 功能 | 各平台的配置文件中会列出对应的插件平台 |
| 令牌锁定（多配置文件场景） | 在 `connect()` 方法中使用 `acquire_scoped_lock()` 实现令牌锁定 |
| 丢失配置的警告提示 | 当插件缺失时，系统会输出详细的日志信息 |

## 基于环境的自动配置

大多数用户是通过在 `~/.hermes/.env` 文件中设置环境变量来配置平台，而非直接编辑 `config.yaml` 文件。`env_enablement_fn` 这一钩子函数允许插件在适配器构建之前就获取这些环境变量，这样一来，`hermes gateway status`、`get_connected_platforms()` 以及 Cron 定时任务都能获取到正确的平台状态，而无需先实例化平台 SDK。

```python
def _env_enablement() -> dict | None:
    """Seed PlatformConfig.extra from env vars.

    Called by the platform registry during load_gateway_config().
    Return None when the platform isn't minimally configured — the
    caller then skips auto-enabling. Return a dict to seed extras.

    The special 'home_channel' key is extracted and becomes a proper
    HomeChannel dataclass on the PlatformConfig; every other key is
    merged into PlatformConfig.extra.
    """
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {
            "chat_id": home,
            "name": os.getenv("MY_PLATFORM_HOME_CHANNEL_NAME", "Home"),
        }
    return seed


def register(ctx):
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        env_enablement_fn=_env_enablement,
        # ... other fields
    )
```


## YAML与环境变量配置转换桥接

部分用户更倾向于直接在`config.yaml`中定义相关键值（如`my_platform.require_mention`、`my_platform.allowed_channels`等），而非使用环境变量。通过`apply_yaml_config_fn`钩子，您的插件可以自行处理这种配置转换工作，无需强制让核心的`gateway/config.py`了解您所使用的平台的YAML格式规范。

```python
import os

def _apply_yaml_config(yaml_cfg: dict, platform_cfg: dict) -> dict | None:
    """Translate config.yaml `my_platform:` keys into env vars / extras.

    yaml_cfg     — the full top-level parsed config.yaml dict
    platform_cfg — the platform's own sub-dict (yaml_cfg.get("my_platform", {}))

    May mutate os.environ directly (use `not os.getenv(...)` guards to
    preserve env > YAML precedence) and/or return a dict to merge into
    PlatformConfig.extra. Return None or {} for no extras.
    """
    if "require_mention" in platform_cfg and not os.getenv("MY_PLATFORM_REQUIRE_MENTION"):
        os.environ["MY_PLATFORM_REQUIRE_MENTION"] = str(platform_cfg["require_mention"]).lower()
    allowed = platform_cfg.get("allowed_channels")
    if allowed is not None and not os.getenv("MY_PLATFORM_ALLOWED_CHANNELS"):
        if isinstance(allowed, list):
            allowed = ",".join(str(v) for v in allowed)
        os.environ["MY_PLATFORM_ALLOWED_CHANNELS"] = str(allowed)
    return None  # nothing extra to merge into PlatformConfig.extra

def register(ctx):
    ctx.register_platform(
        name="my_platform",
        ...,
        apply_yaml_config_fn=_apply_yaml_config,
    )
```

该钩子在 `load_gateway_config()` 函数中被调用，位于处理常见密钥（如 `unauthorized_dm_behavior`、`notice_delivery`、`reply_prefix`、`require_mention` 等）的通用共享密钥处理逻辑之后，以及 `_apply_env_overrides()` 之前。因此，您的插件只需处理**特定于平台**的密钥即可。

该钩子抛出的异常会被捕获并记录在调试级别——出现故障的插件不会导致网关配置加载过程中断。

## 定时任务消息发送

若希望将 `deliver=my_platform` 格式的定时任务消息发送到已配置的主频道，需将 `cron_deliver_env_var` 设置为存储默认聊天/房间/频道 ID 的环境变量名称：

```python
ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
)
```

在为 `deliver=my_platform` 类型的任务确定目标地址时，调度器会读取该环境变量；同时，在基于 `_KNOWN_DELIVERY_PLATFORMS` 规则进行的校验中，该平台也会被视为有效的 Cron 目标。如果您的 `env_enablement_fn` 函数已设置了 `home_channel` 字典（见上文），其设置将优先生效——而对于在环境变量设置之前运行的 Cron 任务，则会以 `cron_deliver_env_var` 作为备用值。

### 进程外的 Cron 任务发送

`cron_deliver_env_var` 能使您的平台成为被系统识别的 `deliver=` 目标。若需确保在 Cron 任务在独立于网关的进程中运行时（即通过 `hermes cron run` 启动，且与 `hermes gateway` 分开），仍能成功完成发送操作，就需要注册一个 `standalone_sender_fn` 函数：

```python
async def _standalone_send(
    pconfig,
    chat_id,
    message,
    *,
    thread_id=None,
    media_files=None,
    force_document=False,
):
    """Open an ephemeral connection / acquire a fresh token, send, and close."""
    # ... open connection, send message, return result ...
    return {"success": True, "message_id": "..."}
    # or {"error": "..."}

ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
    standalone_sender_fn=_standalone_send,
)
```

为何需要此钩子：内置平台（如 Telegram、Discord、Slack 等）在 `tools/send_message_tool.py` 中提供了直接的 REST 工具，因此 cron 可以在无需将网关置于同一进程中的情况下发送消息。而插件平台过去依赖于 `_gateway_runner_ref()` 函数，该函数在网关进程之外会返回 `None`，因此如果没有 `standalone_sender_fn`，cron 端的发送操作就会因“平台 ‘<name>’ 没有可用适配器”而失败。

该函数会接收与实时适配器相同的 `pconfig` 和 `chat_id`，此外还支持可选的 `thread_id`、`media_files` 以及 `force_document` 关键字参数。若返回 `{"success": True, "message_id": ...}` 即表示发送成功；若返回 `{"error": "..."}`，则该错误信息会显示在 cron 的 `delivery_errors` 中。函数内部抛出的异常会被调度器捕获，并以“插件独立发送失败：<原因>”的形式进行报告。相关参考实现位于 `plugins/platforms/{irc,teams,google_chat}/adapter.py` 文件中。

## 在 `hermes config` 中显示环境变量

`hermes_cli/config.py` 会在导入时扫描 `plugins/platforms/*/plugin.yaml` 文件，自动从 `requires_env` 以及可选的 `optional_env` 块中提取 `OPTIONAL_ENV_VARS`。建议使用 rich-dict 格式来填写详细的描述、提示信息、密码标记及 URL —— CLI 配置界面会自动识别这些内容。

```yaml
# plugins/platforms/my_platform/plugin.yaml
name: my_platform-platform
label: My Platform
kind: platform
version: 1.0.0
description: >
  My Platform gateway adapter for Hermes Agent.
author: Your Name
requires_env:
  - name: MY_PLATFORM_TOKEN
    description: "Bot API token from the My Platform console"
    prompt: "My Platform bot token"
    url: "https://my-platform.example.com/bots"
    password: true
  - name: MY_PLATFORM_CHANNEL
    description: "Channel to join (e.g. #hermes)"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery (defaults to MY_PLATFORM_CHANNEL)"
    prompt: "Home channel (or empty)"
    password: false
  - name: MY_PLATFORM_ALLOWED_USERS
    description: "Comma-separated user IDs allowed to talk to the bot"
    prompt: "Allowed users (comma-separated)"
    password: false
```

**支持的字典键值：** `name`（必填）、`description`、`prompt`、`url`、`password`（布尔类型；若未指定，则自动从带有 `*_TOKEN` / `*_SECRET` / `*_KEY` / `*_PASSWORD` / `*_JSON` 后缀的参数中检测）、`category`（默认值为 `"messaging"`）。

直接以字符串形式提供的参数（如 `- MY_PLATFORM_TOKEN`）同样有效——系统会自动根据插件的 `label` 为其生成通用描述。如果 `OPTIONAL_ENV_VARS` 中已存在该变量的硬编码值，则优先使用该值（以保证向后兼容性）；否则将以 `plugin.yaml` 中的配置作为备用方案。

## 各平台针对慢速大语言模型的特殊交互设计

部分平台存在特定限制，这要求以不同方式呈现慢速大语言模型的响应：

- **LINE** 会生成一个一次性使用的*回复令牌*，该令牌在收到消息后约60秒失效。使用该令牌回复是免费的，而转而使用计费制的Push API则需付费。如果大语言模型在截止时间前仍未完成响应，用户只能选择“消耗已支付的Push额度”或“在令牌过期前用该令牌尝试更巧妙的回复方式”。
- **WhatsApp** 会在24小时后判定会话处于非活跃状态，此后仅允许发送模板消息。
- **SMS** 不支持输入状态指示或进度更新功能——较长的响应内容会被视为机器人处于离线状态。

这些都是基础类 `BasePlatformAdapter` 无法预料的实际限制。因此，插件设计刻意保留了空间，让适配器能够在不增加参数列表的情况下，在基础输入状态循环之上叠加针对特定平台的交互逻辑。

### 实现方式：通过继承 `_keep_typing` 方法添加运行中的交互功能

`BasePlatformAdapter._keep_typing` 方法用于生成输入状态指示——在大语言模型生成响应的期间，它作为后台任务持续运行，一旦响应送达则会被终止。若想在达到特定时间点时添加平台特有的交互功能（例如在45秒时显示“仍在思考”提示），可在自己的适配器中重写 `_keep_typing` 方法，在调用 `super()._keep_typing()` 的同时安排自己的任务，并在 `finally` 块中取消该任务：

```python
class LineAdapter(BasePlatformAdapter):
    async def _keep_typing(self, chat_id: str, *args, **kwargs) -> None:
        if self.slow_response_threshold <= 0:
            await super()._keep_typing(chat_id, *args, **kwargs)
            return

        async def _fire_at_threshold() -> None:
            try:
                await asyncio.sleep(self.slow_response_threshold)
            except asyncio.CancelledError:
                raise
            # Platform-specific work here — for LINE, send a Template
            # Buttons "Get answer" bubble using the cached reply token
            # so the user can fetch the cached response later via a
            # fresh (free) reply token from the postback callback.
            await self._send_slow_response_button(chat_id)

        side_task = asyncio.create_task(_fire_at_threshold())
        try:
            await super()._keep_typing(chat_id, *args, **kwargs)
        finally:
            if not side_task.done():
                side_task.cancel()
                try:
                    await side_task
                except (asyncio.CancelledError, Exception):
                    pass
```

要点：

- **务必始终调用 `await super()._keep_typing()`**。打字心跳信号本身具有独立作用——不应将其替代，而应在其基础上进行扩展。
- **在 `finally` 块中终止辅助任务**。当大语言模型处理完成（或通过 `/stop` 取消运行）时，网关会取消打字任务。您的辅助任务也必须能够检测到这一取消操作，否则它可能会持续运行，并在响应已经发送之后仍被触发。
- **结合使用 `interrupt_session_activity`**，以解决用户在发起 `/stop` 指令时可能出现的异常用户界面状态问题。对于 LINE 平台，这意味着需要将回传缓存记录的状态从 `PENDING` 更改为 `ERROR`，这样永久显示的“获取答案”按钮就会展示“运行已中断”的提示，而不会陷入循环。

### 实现模式：通过子类化 `send` 方法，让响应先进入缓存而非立即发送

如果您的低响应速度用户界面会将响应缓存起来以供后续获取（如 LINE 的回传流程），那么您对 `send` 方法的重写就需要能够识别三种不同的状态：

1. **当前对话处于回传待处理状态** → 将响应缓存在对应的 `request_id` 下，不要发送任何可见内容。
2. **系统正在处理中**（显示为 `⚡ Interrupting`、`⏳ Queued`、`⏩ Steered` 等状态）→ 跳过缓存直接发送可见内容，以便用户能看到网关对输入的响应。
3. **正常响应情况** → 按常规方式通过回复令牌或推送功能发送响应。

```python
async def send(self, chat_id: str, content: str, **kw) -> SendResult:
    if _is_system_bypass(content):
        return await self._send_text_chunks(chat_id, content, force_push=False)
    pending_rid = self._pending_buttons.get(chat_id)
    if pending_rid:
        self._cache.set_ready(pending_rid, content)
        return SendResult(success=True, message_id=pending_rid)
    return await self._send_text_chunks(chat_id, content, force_push=False)
```

`_SYSTEM_BYPASS_PREFIXES` 是网关自用的忙碌状态指示前缀（如 `⚡`、`⏳`、`⏩`、`💾`）。无论缓存的用户界面状态如何，都应始终以可见形式显示这些前缀。

### 适用场景

在以下情况下，可使用打字循环覆盖机制：

- 平台的后端 API 存在严格的时限约束（如一次性回复令牌、过期会话等），且
- 该平台允许使用“可见的传输中提示框”作为用户界面元素。

而在以下情况下，则建议采用更简单的 `slow_response_threshold = 0` 的始终推送方案：

- 该平台并未明确区分免费与付费服务，或
- 用户群体更倾向于“加载中…加载中…完成”的静默等待后再显示回复，而非交互式的中间提示框。

LINE 平台同时支持这两种方式：免费回传请求的默认超时时间为 45 秒，而设置 `LINE_SLOW_RESPONSE_THRESHOLD=0` 则会切换为“始终推送”模式作为备用。

### 参考实现

完整的 LINE 回传实现可见于 `plugins/platforms/line/adapter.py` —— 其中包含一个 `RequestCache` 状态机（状态包括 `PENDING → READY → DELIVERED`，以及 `/stop` 操作对应的 `ERROR` 状态）、一个在达到阈值时触发模板按钮提示框的 `_keep_typing` 覆盖机制、一个通过缓存处理消息发送的 `send` 覆盖机制，以及一个用于清理异常的 `PENDING` 状态记录的 `interrupt_session_activity` 覆盖机制。

### 插件实现参考路径

如需完整的可运行示例，可查看代码库中的 `plugins/platforms/irc/` 目录 —— 这是一个完全异步的 IRC 适配器，且不依赖任何外部组件。`plugins/platforms/teams/` 目录涵盖 Bot Framework / Adaptive Cards 功能，`plugins/platforms/google_chat/` 目录涉及基于 OAuth 的 REST API，而 `plugins/platforms/line/` 目录则处理基于 webhook 的消息传递 API，并针对不同平台提供特定的慢速大语言模型用户界面体验。

---

## 分步检查清单（直接集成路径）

:::note
本检查清单适用于将某个平台直接集成到 Hermes 核心代码库中——通常由核心开发人员为官方支持的平台执行此操作。社区开发或第三方平台则应使用上述[插件集成路径](#plugin-path-recommended)。
:::

### 1. 平台枚举

在 `gateway/config.py` 文件中的 `Platform` 枚举中添加您的平台：

```python
class Platform(str, Enum):
    # ... existing platforms ...
    NEWPLAT = "newplat"
```

### 2. 适配器文件

创建 `plugins/platforms/newplat/adapter.py` 文件：

```python
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter, MessageEvent, MessageType, SendResult,
)

def check_newplat_requirements() -> bool:
    """Return True if dependencies are available."""
    return SOME_SDK_AVAILABLE

class NewPlatAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.NEWPLAT)
        # Read config from config.extra dict
        extra = config.extra or {}
        self._api_key = extra.get("api_key") or os.getenv("NEWPLAT_API_KEY", "")

    async def connect(self) -> bool:
        # Set up connection, start polling/webhook
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._running = False
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # Send message via platform API
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}
```

对于接收到的消息，需构建一个 `MessageEvent` 对象，然后调用 `self.handle_message(event)` 方法：

```python
source = self.build_source(
    chat_id=chat_id,
    chat_name=name,
    chat_type="dm",  # or "group"
    user_id=user_id,
    user_name=user_name,
)
event = MessageEvent(
    text=content,
    message_type=MessageType.TEXT,
    source=source,
    message_id=msg_id,
)
await self.handle_message(event)
```

### 3. 网关配置（`gateway/config.py`）

涉及三个修改点：

1. **`get_connected_platforms()`** — 需添加对平台所需凭证的校验逻辑
2. **`load_gateway_config()`** — 需添加令牌环境变量映射项：`Platform.NEWPLAT: "NEWPLAT_TOKEN"`
3. **`_apply_env_overrides()`** — 需将所有 `NEWPLAT_*` 格式的环境变量映射至配置中

### 4. 网关运行器（`gateway/run.py`）

涉及五个修改点：

1. **`_create_adapter()`** — 需添加 `elif platform == Platform.NEWPLAT:` 分支
2. **`_is_user_authorized()` 的 allowed_users 映射表** — 添加 `Platform.NEWPLAT: "NEWPLAT_ALLOWED_USERS"`
3. **`_is_user_authorized()` 的 allow_all 映射表** — 添加 `Platform.NEWPLAT: "NEWPLAT_ALLOW_ALL_USERS"`
4. **提前进行的环境变量检查 `_any_allowlist` 元组** — 需添加 `"NEWPLAT_ALLOWED_USERS"` 至该元组中
5. **提前进行的环境变量检查 `_allow_all` 元组** — 需添加 `"NEWPLAT_ALLOW_ALL_USERS"` 至该元组中
6. **`_UPDATE_ALLOWED_PLATFORMS` 冻结集** — 需添加 `Platform.NEWPLAT` 至该集合中

### 5. 跨平台消息发送功能

1. **`gateway/platforms/webhook.py`** — 需将 `"newplat"` 添加至消息发送类型对应的元组中
2. **`cron/scheduler.py`** — 需将 `"newplat"` 添加至 `_KNOWN_DELIVERY_PLATFORMS` 冻结集，以及 `_deliver_result()` 函数的平台映射表中

### 6. CLI集成

1. **`hermes_cli/config.py`** — 需将所有 `NEWPLAT_*` 格式的环境变量添加至 `_EXTRA_ENV_KEYS` 列表中
2. **`hermes_cli/gateway.py`** — 需在 `_PLATFORMS` 列表中为该平台添加对应条目，需包含键值、标签、表情符号、令牌变量、设置说明以及相关环境变量
3. **`hermes_cli/platforms.py`** — 需添加包含标签和默认工具集的 `PlatformInfo` 条目（这些信息会被 `skills_config` 和 `tools_config` 的图形用户界面所使用）
4. **`hermes_cli/setup.py`** — 需添加 `_setup_newplat()` 函数（该函数可调用 `gateway.py` 中的逻辑），同时需将 `"newplat"` 添加至消息平台列表对应的元组中
5. **`hermes_cli/status.py`** — 需添加平台识别相关条目：`"NewPlat": ("NEWPLAT_TOKEN", "NEWPLAT_HOME_CHANNEL")`
6. **`hermes_cli/dump.py`** — 需在平台识别字典中添加 `"newplat": "NEWPLAT_TOKEN"` 的对应项

### 7. 工具类

1. **`tools/send_message_tool.py`** — 需在平台映射表中添加 `"newplat": Platform.NEWPLAT` 的对应关系
2. **`tools/cronjob_tools.py`** — 需在消息发送目标描述字符串中添加 `"newplat"` 相关内容

### 8. 工具集

1. **`toolsets.py`** — 需定义包含 `_HERMES_CORE_TOOLS` 的 `"hermes-newplat"` 工具集
2. **`toolsets.py`** — 需将 `"hermes-newplat"` 添加至 `"hermes-gateway"` 所依赖的包含列表中

### 9. 可选功能：平台特定提示

**`agent/prompt_builder.py`** — 如果您的平台存在特定的渲染限制（如不支持 Markdown、消息长度限制等），可在 `_PLATFORM_HINTS` 字典中为该平台添加对应提示。这些提示会被嵌入到系统提示语中，为相关平台提供定制化指导：

```python
_PLATFORM_HINTS = {
    # ...
    "newplat": (
        "You are chatting via NewPlat. It supports markdown formatting "
        "but has a 4000-character message limit."
    ),
}
```

并非所有平台都需要提示信息——只有当代理的行为需要有所区别时才需添加。

### 10. 测试

创建 `tests/gateway/test_newplat.py`，涵盖以下内容：

- 根据配置构建适配器
- 消息事件的生成
- 发送方法（对外部 API 进行模拟）
- 平台特定功能（加密、路由等）

### 11. 文档编写

| 文件路径 | 需要添加的内容 |
|----------|--------------|
| `website/docs/user-guide/messaging/newplat.md` | 完整的平台配置页面 |
| `website/docs/user-guide/messaging/index.md` | 平台对比表、架构图、工具集列表、安全相关内容以及后续操作链接 |
| `website/docs/reference/environment-variables.md` | 所有 NEWPLAT_* 环境变量 |
| `website/docs/reference/toolsets-reference.md` | hermes-newplat 工具集介绍 |
| `website/docs/integrations/index.md` | 对应平台的链接 |
| `website/sidebars.ts` | 文档页面的侧边栏条目 |
| `website/docs/developer-guide/architecture.md` | 适配器数量及列表 |
| `website/docs/developer-guide/gateway-internals.md` | 适配器文件列表 |

## 对等性审核

在将新平台的 Pull Request 标记为已完成之前，需先针对某个已有的平台进行对等性审核：

```bash
# Find every .py file mentioning the reference platform
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# Find every .py file mentioning the new platform
search_files "newplat" output_mode="files_only" file_glob="*.py"

# Any file in the first set but not the second is a potential gap
```

对 `.md` 和 `.ts` 文件执行相同操作。逐一检查这些缺失项——是平台枚举问题（需要更新）还是平台特定引用问题（可直接跳过）？

## 常见模式

### 长轮询适配器

如果您的适配器采用长轮询机制（如 Telegram 或微信），则应使用轮询循环任务：

```python
async def connect(self):
    self._poll_task = asyncio.create_task(self._poll_loop())
    self._mark_connected()

async def _poll_loop(self):
    while self._running:
        messages = await self._fetch_updates()
        for msg in messages:
            await self.handle_message(self._build_event(msg))
```

### 回调/Webhook 适配器

如果平台通过您的端点（如企业微信回调）推送消息，请运行一个 HTTP 服务器：

```python
async def connect(self):
    self._app = web.Application()
    self._app.router.add_post("/callback", self._handle_callback)
    # ... start aiohttp server
    self._mark_connected()

async def _handle_callback(self, request):
    event = self._build_event(await request.text())
    await self._message_queue.put(event)
    return web.Response(text="success")  # Acknowledge immediately
```

对于对响应时间有严格要求的平台（例如 WeCom 设定的 5 秒限制），应立即确认接收请求，并随后通过 API 主动返回智能体的回复。智能体会话的持续时间为 3 至 30 分钟，因此在回调响应时间内进行即时回复是不可行的。

### 令牌锁定机制

如果适配器使用唯一的凭据维持着持久连接，应添加基于作用域的锁定机制，以防止多个配置文件使用相同的凭据：

```python
from gateway.status import acquire_scoped_lock, release_scoped_lock

async def connect(self):
    if not acquire_scoped_lock("newplat", self._token):
        logger.error("Token already in use by another profile")
        return False
    # ... connect

async def disconnect(self):
    release_scoped_lock("newplat", self._token)
```

## 参考实现

| 适配器 | 模式 | 复杂度 | 适用场景参考 |
|---------|------|--------|--------------|
| `bluebubbles.py` | REST + webhook | 中等 | 简单的 REST API 集成 |
| `weixin.py` | 长轮询 + CDN | 高 | 媒体处理、加密功能 |
| `wecom_callback.py` | 回调/ webhook | 中等 | HTTP 服务器、AES 加密、多应用支持 |
| `plugins/platforms/irc/adapter.py` | 长轮询 + IRC 协议 | 高 | 具有范围令牌锁定功能的完整插件适配器 |
