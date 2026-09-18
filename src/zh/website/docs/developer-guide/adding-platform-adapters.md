---
sidebar_position: 9
---

# 添加平台适配器

本指南介绍了如何将新的消息传递平台集成到 Hermes 网关中。平台适配器用于连接 Hermes 与外部消息服务（如 Telegram、Discord、企业微信等），从而使用户能够通过这些服务与智能体进行交互。

:::提示
添加新平台有两种方式：
- **插件方式**（推荐用于社区或第三方开发）：只需将插件目录放入 `~/.hermes/plugins/` 目录中，无需修改任何核心代码。详情请参见下文的[插件路径推荐](#plugin-path-recommended)。
- **内置方式**：需要修改代码、配置文件及文档中的20多个相关文件。可使用下文的[内置方式检查清单](#step-by-step-checklist-built-in-path)进行参考。
:::

## 架构概览

```
User ↔ Messaging Platform ↔ Platform Adapter ↔ Gateway Runner ↔ AIAgent
```

每个适配器均继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter`，并实现以下功能：

- **`connect()`** — 建立连接（WebSocket、长轮询、HTTP 服务器等）*（抽象方法）*
- **`disconnect()`** — 正常关闭连接 *（抽象方法）*
- **`send()`** — 向聊天窗口发送文本消息 *（抽象方法）*
- **`send_typing()`** — 显示输入中状态指示器（可选择性重写）
- **`get_chat_info()`** — 返回聊天元数据（可选择性重写）

适配器负责接收传入的消息，并通过 `self.handle_message(event)` 将其转发，而基类则会将其路由至网关运行器。

## 插件路径（推荐方式）

插件系统允许您在无需修改任何 Hermes 核心代码的情况下添加平台适配器。您的插件是一个包含两个文件的目录：

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

#### 出站客户端工具：`provides_tools`

类型为 `kind: platform` 的插件采用**延迟加载**机制：只有当网关、定时任务或 `send_message` 路径首次向平台注册表查询对应平台时，适配器模块（及其 SDK 导入项）才会被加载。如果您的插件还提供了可从任意会话中调用的出站*客户端工具*（例如预置的 `a2a` 插件中的 `a2a_call`/`a2a_discover` 等功能），请将其放入专用的 `tools.py` 文件中，并在其中定义 `register_tools(ctx)` 函数，同时在工作清单中对这些工具进行声明。

```yaml
provides_tools:
  - my_platform_call
  - my_platform_list
```

当声明了 `provides_tools` 后，Hermes 在插件发现阶段仅会导入 `tools.py`，并将客户端工具注册到所有进程中——包括 CLI 和 TUI 进程——而适配器则会被延迟加载。应保持该包的 `__init__.py` 文件中的导入内容尽可能简洁，通过在 `register()` 函数内部再引入适配器，从而避免不必要的提前导入带来的性能开销。若未设置该字段，则一切保持不变：整个插件仍会被延迟加载。

用户可以像启用其他工具集一样，按平台来启用特定工具集，例如使用命令 `hermes tools enable my_platform --platform cli`；或者通过在 `config.yaml` 文件的 `platform_toolsets` 下列出相应的工具集键值。插件所对应的平台名称同样可作为有效的 `--platform` 参数，这样一来，接入该平台的会话便能拥有专属的对外工具。

### adapter.py

```python
import os
from gateway.platforms.base import BasePlatformAdapter, SendResult
from gateway.platforms.event import MessageEvent, MessageType
from gateway.config import Platform, PlatformConfig


class MyPlatformAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform("my_platform"))
        extra = config.extra or {}
        self.token = os.getenv("MY_PLATFORM_TOKEN") or extra.get("token", "")

    async def connect(self, *, is_reconnect: bool = False) -> bool:
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
        # PASSIVE probe — "are deps/config present right now?".  Called from
        # status displays and config loading, so it must NEVER pip-install.
        check_fn=check_requirements,
        # ACTIVE installer (optional) — only for platforms with a
        # lazy-installable SDK.  create_adapter() calls it when check_fn
        # returns False, right before the gateway connects the platform.
        # Typically wraps tools.lazy_deps.ensure_and_bind(...).  Omit it
        # and a False check_fn is a hard block.
        # ensure_deps_fn=ensure_requirements,
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

### 插件系统自动处理的内容

当您调用 `ctx.register_platform()` 时，以下集成环节将由系统自动处理——无需修改任何核心代码：

| 集成点 | 工作原理 |
|---|---|
| 网关适配器创建 | 先查询注册表，再使用内置的 `_BUILTIN_ADAPTERS` 表 |
| 配置解析 | `Platform._missing_()` 函数可接受任意平台名称 |
| 已连接平台验证 | 调用注册表的 `validate_config()` 方法进行验证 |
| 用户授权检查 | 根据 `allowed_users_env` / `allow_all_env` 的设置进行授权判断 |
| 仅基于环境变量的自动启用 | 通过 `env_enablement_fn` 函数设置 `PlatformConfig.extra` 及 `home_channel` 参数 |
| YAML 配置转换 | `apply_yaml_config_fn` 函数负责将 `config.yaml` 中的键值转换为环境变量或额外参数 |
| Cron 定时任务传递 | `cron_deliver_env_var` 函数可实现通过 `deliver=<名称>` 的方式传递值 |
| `hermes config` 用户界面字段填充 | 自动填充 `plugin.yaml` 文件中的 `requires_env` / `optional_env` 设置 |
| 发送引擎（`tools/send_message_tool.py`） | 通过实时运行的网关适配器进行消息路由 |
| Webhook 跨平台消息传递 | 先查询注册表以确定支持的消息平台 |
| `/update` 命令访问权限控制 | 通过 `allow_update_command` 标志来控制该命令的访问权限 |
| 频道目录管理 | 在枚举过程中会包含插件所对应的平台信息 |
| 系统提示信息生成 | 将 `platform_hint` 参数注入到大语言模型的上下文中 |
| 消息分块处理 | 根据 `max_message_length` 参数智能分割长消息 |
| 个人身份信息脱敏 | 通过 `pii_safe` 标志实现敏感信息隐藏 |
| `hermes status` 显示功能 | 以 `(plugin)` 标签标注插件所对应的平台 |
| `hermes gateway setup` 设置界面 | 在设置菜单中显示插件平台选项 |
| `hermes tools` / `hermes skills` 功能 | 在各平台的配置文件中体现插件平台信息 |
| 令牌锁定（多配置文件场景） | 在 `connect()` 函数中使用 `acquire_scoped_lock()` 实现令牌锁定 |
| 丢失的配置警告 | 当缺少相应插件时，会生成详细的日志提示
## 独立型发送路径扩展功能

独立型平台可通过在由 `ctx.register_platform()` 创建的同一 `PlatformEntry` 上定义发送行为，直接使用 `hermes send --to ...` 命令或 cron 表达式 `deliver=platform:...` 来参与由主机驱动的外发消息传递流程。有意将 `send_message` 设计为不可被智能体调用的模型工具；因此插件也不得注册类似的模型接口，以免让智能体能够自行发起外发消息。

```python
async def _send_request(args, chat_id, platform_name, pconfig):
    # `args` contains the host-driven send request fields.
    message_id = await client.send(
        address=chat_id,
        body=args["message"],
        subject=args.get("subject"),
    )
    return {"success": True, "platform": platform_name,
            "chat_id": chat_id, "message_id": message_id}


def _parse_address(raw):
    normalized = raw.strip().lower()
    if normalized.startswith("@") and "@" in normalized[1:]:
        return normalized, None  # (chat_id, optional thread_id)
    return None                 # continue to channel-directory resolution


def _validate_address(address):
    # True accepts; False rejects; a string rejects with that diagnostic.
    return True if address.endswith("@example.com") else "unsupported domain"


def register(ctx):
    ctx.register_platform(
        name="fmsg",
        label="Fixture Message",
        adapter_factory=lambda cfg: FmsgAdapter(cfg),
        check_fn=check_requirements,
        parse_target_ref_fn=_parse_address,
        validate_target_ref_fn=_validate_address,
        # May be a regular function or async def. Hermes awaits any awaitable
        # result, including callable objects and functools.partial wrappers.
        send_message_handler=_send_request,
        # Prefer this lower-level hook when cron must send from a process
        # without the live gateway.
        standalone_sender_fn=_standalone_send,
    )
```

目标解析结果会在三个输出通道之间共享。解析器输出会先经过标准化处理，同时也会优先采用通道目录标识符。插件解析器必须明确支持原生目标语法；任何无法解析的字符串都不会被隐式传递下去。对于未知平台或验证失败的情况，系统会返回诊断信息，而不会尝试默默进行发送操作。当通过插件强制重新加载配置或切换配置文件时，该插件所管理的条目将会被注销，从而防止解析器和处理程序残留到下一个配置文件中。

## 基于环境变量的自动配置

大多数用户都是通过将环境变量添加到 `~/.hermes/.env` 文件中来配置平台，而非直接编辑 `config.yaml`。`env_enablement_fn` 钩子允许插件在适配器构建之前就获取这些环境变量，这样一来，`hermes gateway status`、`get_connected_platforms()` 以及定时任务发送功能便能无需实例化平台 SDK 即可获取正确的状态信息。

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

部分用户更倾向于直接在`config.yaml`中定义相关键值（如`my_platform.require_mention`、`my_platform.allowed_channels`等），而非使用环境变量。通过`apply_yaml_config_fn`钩子，您的插件可以自行处理这种配置转换逻辑，无需强制让核心的`gateway/config.py`了解您所使用平台的YAML格式规范。

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

该钩子在 `load_gateway_config()` 函数中被调用，位于处理常见密钥（如 `unauthorized_dm_behavior`、`notice_delivery`、`reply_prefix`、`require_mention` 等）的通用共享密钥处理流程之后，以及 `_apply_env_overrides()` 之前。因此，您的插件只需处理**特定于平台**的密钥即可。

该钩子抛出的异常会被捕获并记录在调试级别——出现问题的插件不会导致网关配置加载过程中断。

## 定时任务消息发送

若希望将 `deliver=my_platform` 格式的定时任务消息发送到已配置的主频道，需将 `cron_deliver_env_var` 设置为存储默认聊天/房间/频道 ID 的环境变量名称：

```python
ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
)
```

在为 `deliver=my_platform` 类型的任务确定目标地址时，调度器会读取该环境变量；同时，在基于 `_KNOWN_DELIVERY_PLATFORMS` 规则进行的校验中，也会将该平台视为有效的 Cron 目标。如果您的 `env_enablement_fn` 函数已设置了 `home_channel` 字典（见上文），其设置将优先生效——而对于在环境变量初始化之前运行的 Cron 任务，则会以 `cron_deliver_env_var` 作为默认值。

### 进程外的 Cron 任务发送

通过 `cron_deliver_env_var`，您的平台即可被识别为 `deliver=` 类型的目标。若要在 Cron 任务在独立于网关的进程中运行时（即通过 `hermes cron run` 启动且与 `hermes gateway` 分开运行）仍能成功发送数据，需注册一个 `standalone_sender_fn` 函数：

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

为何需要此钩子：内置平台（如 Telegram、Discord、Slack 等）在 `tools/send_message_tool.py` 中提供了直接的 REST 助手，因此 cron 可以在无需将网关保留在同一进程中的情况下完成消息发送。而插件平台过去依赖于 `_gateway_runner_ref()` 函数，该函数在网关进程之外会返回 `None`，因此如果没有 `standalone_sender_fn`，cron 端的消息发送将会因“平台 ‘<name>’ 没有可用适配器”而失败。

该函数会接收与实际适配器相同的 `pconfig` 和 `chat_id`，此外还支持可选的 `thread_id`、`media_files` 以及 `force_document` 关键字参数。若返回 `{"success": True, "message_id": ...}` 即表示消息发送成功；若返回 `{"error": "..."}`，则该错误信息会显示在 cron 的 `delivery_errors` 中。函数内部抛出的异常会被调度器捕获，并以“插件独立发送失败：<原因>”的形式报告。相关参考实现位于 `plugins/platforms/{irc,teams,google_chat}/adapter.py` 文件中。

## 在 `hermes config` 中显示环境变量

`hermes_cli/config.py` 会在导入时扫描 `plugins/platforms/*/plugin.yaml` 文件，自动从 `requires_env` 以及（可选的）`optional_env` 块中提取 `OPTIONAL_ENV_VARS`。建议使用富字典格式来填写详细的描述、提示信息、密码标记及 URL —— CLI 配置界面会自动识别这些内容。

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

仅以字符串形式提供的参数（如 `- MY_PLATFORM_TOKEN`）同样有效——系统会自动根据插件的 `label` 为其生成通用描述。如果 `OPTIONAL_ENV_VARS` 中已存在该变量的硬编码值，则优先使用该值（以保持向后兼容性）；否则将以 `plugin.yaml` 中的配置作为备用。

## 各平台针对慢速大语言模型的特殊体验设计

部分平台存在特定限制，这要求以不同方式呈现慢速大语言模型的响应内容：

- **LINE** 会生成一个一次性使用的*回复令牌*，该令牌在接收消息后约60秒失效。使用该令牌回复是免费的，而转而使用按量计费的Push API则需付费。如果大语言模型在截止时间前仍未完成响应，用户只能选择“消耗已支付的Push额度”或“在令牌过期前想出更巧妙的回复方式”。
- **WhatsApp** 会在24小时后将会话标记为非活跃状态，此后仅允许发送模板消息。
- **SMS** 不支持输入状态指示或逐步更新功能——较长的响应内容会显得机器人处于离线状态。

这些都是基础 `BasePlatformAdapter` 无法预见的实际限制。因此，插件设计特意保留了空间，让适配器能够在不增加参数列表的情况下，在基础输入状态循环之上叠加针对特定平台的用户体验功能。

### 实现方式：通过继承 `_keep_typing` 类来添加运行中的用户体验功能

`BasePlatformAdapter._keep_typing` 是用于指示输入状态的心跳机制——在大型语言模型生成内容时，它会作为后台任务持续运行；而一旦响应生成完成，该任务便会立即被终止。若需在达到特定时间阈值时添加平台专属功能（例如在45秒时显示“仍在思考”提示），可在自定义适配器中重写 `_keep_typing` 方法，在调用 `super()._keep_typing()` 的同时安排自己的任务，并在 `finally` 块中取消该任务。

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

- **务必始终调用 `await super()._keep_typing()`**。打字心跳信号本身具有独立价值——切勿替代它，而应在其基础上进行扩展使用。
- **在 `finally` 块中终止辅助任务**。当大语言模型处理完成（或通过 `/stop` 取消运行）时，网关会同时取消打字任务。您的辅助任务也必须能检测到这一取消操作，否则它可能会持续运行，并在响应已发送后才被触发。
- **结合使用 `interrupt_session_activity`**，以便在用户发出 `/stop` 命令时解决任何残留的界面状态问题。对于 LINE 平台，这意味着需将回传缓存条目的状态从 `PENDING` 更改为 `ERROR`，这样永久显示的“获取答案”按钮就会显示“运行已被中断”的提示，而不会陷入循环。

### 模式：通过子类化 `send` 方法经由缓存路由，而非立即发送

如果您的低响应速度界面会将响应缓存起来以供后续获取（如 LINE 的回传流程），那么您对 `send` 方法的重写就需要能够识别三种不同模式：

1. **当前对话处于待处理回传状态** → 将响应缓存到对应 request_id 下，不要发送任何可见内容。
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

`_SYSTEM_BYPASS_PREFIXES`指的是网关自身用于表示处理中状态的符号（如`⚡`、`⏳`、`⏩`、`💾`）。无论用户界面缓存中的状态如何，都应始终让这些符号清晰可见地显示出来。

### 何时适用此方案

在以下情况下，可采用“打字循环覆盖”方式：

- 平台的外发API存在严格的时限约束（如一次性回复令牌、会话过期等），且
- 在该平台上，显示“处理中提示框”属于可接受的用户体验。

而在以下情况下，则可直接使用更简单的`slow_response_threshold = 0`的“始终推送”方案：

- 该平台并未明确区分免费与付费服务，或
- 用户群体更倾向于“加载中……加载中……完成”的静默状态后再显示回复，而非交互式的处理中提示框。

LINE平台同时支持这两种方式：免费用户的回传请求默认等待时间为45秒，而设置`LINE_SLOW_RESPONSE_THRESHOLD=0`则可强制启用“始终推送”模式作为备用方案。

### 参考实现

完整的LINE回传功能实现可见于`plugins/platforms/line/adapter.py`文件——其中包含一个`RequestCache`状态机（状态包括`PENDING → READY → DELIVERED`，以及用于处理 `/stop` 操作的`ERROR`状态）；一个在达到阈值时触发模板按钮提示框的`_keep_typing`覆盖功能；一个通过缓存来路由请求的`send`覆盖功能；以及一个用于清理异常的`PENDING`状态记录的`interrupt_session_activity`覆盖功能。

### 插件路径下的参考实现

如需查看完整的可运行示例，请查阅仓库中的 `plugins/platforms/irc/` 目录——这是一个无需任何外部依赖的完整异步 IRC 适配器。`plugins/platforms/teams/` 目录涉及 Bot Framework / Adaptive Cards，`plugins/platforms/google_chat/` 目录涉及基于 OAuth 的 REST API，而 `plugins/platforms/line/` 目录则涉及通过 webhook 驱动的消息传递 API，这类 API 具有针对特定平台的低效大语言模型使用体验。

---

## 分步检查清单（内置路径）

:::note
此检查清单用于将某个平台直接添加到 Hermes 核心代码库中——通常由核心贡献者为官方支持的平台执行此操作。社区或第三方平台应使用上述的[插件路径](#plugin-path-recommended)。
:::

### 1. 平台枚举

在 `gateway/config.py` 文件中的 `Platform` 枚举中添加您的平台：

```python
class Platform(Enum):
    # ... existing platforms ...
    NEWPLAT = "newplat"
```

### 2. 适配器文件

创建 `plugins/platforms/newplat/adapter.py` 文件：

```python
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import BasePlatformAdapter, SendResult
from gateway.platforms.event import MessageEvent, MessageType

def check_newplat_requirements() -> bool:
    """Return True if dependencies are available."""
    return SOME_SDK_AVAILABLE

class NewPlatAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.NEWPLAT)
        # Read config from config.extra dict
        extra = config.extra or {}
        self._api_key = extra.get("api_key") or os.getenv("NEWPLAT_API_KEY", "")

    async def connect(self, *, is_reconnect: bool = False) -> bool:
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

对于传入的消息，需构建一个 `MessageEvent` 对象，然后调用 `self.handle_message(event)` 方法：

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

涉及三个关键点：

1. **`get_connected_platforms()`** — 需添加对平台所需凭证的校验逻辑。
2. **`load_gateway_config()`** — 需添加令牌环境变量映射项：`Platform.NEWPLAT: "NEWPLAT_TOKEN"`。
3. **`_apply_env_overrides()`** — 将所有以 `NEWPLAT_*` 开头的环境变量映射至配置中。

### 4. 网关运行器（`gateway/run.py` 及其相关文件 `gateway/run_*.py`）

涉及六个关键点：

1. **`_BUILTIN_ADAPTERS` 表**（位于 `gateway/run.py`）—— 需添加一条 `Platform.NEWPLAT: (模块名, 类名, 校验函数, 错误信息)` 的记录；`_instantiate_adapter()` 函数会先查询插件注册表，再参考该表——目前不存在可用于扩展的 `elif` 语句链。`_create_adapter()` 包装函数会将所有成功加载的适配器与其对应的网关运行器关联起来。
2. **`_is_user_authorized()` 函数的 allowed_users 映射** — 设置为 `Platform.NEWPLAT: "NEWPLAT_ALLOWED_USERS"`。
3. **`_is_user_authorized()` 函数的 allow_all 映射** — 设置为 `Platform.NEWPLAT: "NEWPLAT_ALLOW_ALL_USERS"`。
4. **启动时的访问策略校验**（位于 `gateway/run_startup.py`）—— 需将 `"NEWPLAT"` 添加到 `_ALLOWLIST_ENV_PLATFORMS` 中，该列表会自动推导出 `NEWPLAT_ALLOWED_USERS` 和 `NEWPLAT_ALLOW_ALL_USERS` 的值。
5. **启动时的 _BUILTIN_ALLOW_ALL_VARS 设置**（位于 `gateway/run_startup.py`）—— 其值同样来自 `_ALLOWLIST_ENV_PLATFORMS` 列表，无需额外添加内容。
6. **`_UPDATE_ALLOWED_PLATFORMS` 冻结集** — 需将 `Platform.NEWPLAT` 添加到该集合中。

### 5. 跨平台交付机制

1. **`gateway/platforms/webhook.py`** — 在传递类型元组中添加 `"newplat"`。  
2. **`cron/scheduler_delivery.py`** — 将其添加到 `_KNOWN_DELIVERY_PLATFORMS` 冻集以及 `_deliver_result()` 的平台映射中。

### 6. CLI集成

1. **`hermes_cli/config.py`** — 将所有 `NEWPLAT_*` 变量添加到 `_EXTRA_ENV_KEYS` 中。  
2. **`hermes_cli/gateway.py`** — 在 `_PLATFORMS` 列表中添加包含键值、标签、表情符号、令牌变量、设置说明及相关变量的条目。  
3. **`hermes_cli/platforms.py`** — 添加包含标签及默认工具集的 `PlatformInfo` 条目（供 `skills_config` 和 `tools_config` 的图形界面使用）。  
4. **`hermes_cli/setup.py`** — 添加 `_setup_newplat()` 函数（可委托给 `gateway.py` 处理），并在消息平台列表中添加相应的元组。  
5. **`hermes_cli/status.py`** — 添加平台检测条目：`"NewPlat": ("NEWPLAT_TOKEN", "NEWPLAT_HOME_CHANNEL")`。  
6. **`hermes_cli/dump.py`** — 在平台检测字典中添加 `"newplat": "NEWPLAT_TOKEN"`。

### 7. 工具

1. **`tools/send_message_tool.py`** — 在平台映射中添加 `"newplat": Platform.NEWPLAT`。  
2. **`tools/cronjob_tools.py`** — 在传递目标描述字符串中加入 `newplat`。

### 8. 工具集

1. **`toolsets.py`** — 在 `_HERMES_CORE_TOOLS` 中添加 `"hermes-newplat"` 工具集定义。  
2. **`toolsets.py`** — 将 `"hermes-newplat"` 添加到 `"hermes-gateway"` 的包含列表中。

### 9. 可选：平台提示信息

**`agent/prompt_builder.py`** — 如果您的平台存在特定的渲染限制（如不支持 Markdown、消息长度受限等），请在 `PLATFORM_HINTS` 字典中添加相应条目。这样即可将针对该平台的特定指引注入系统提示语中：

```python
PLATFORM_HINTS = {
    # ...
    "newplat": (
        "You are chatting via NewPlat. It supports markdown formatting "
        "but has a 4000-character message limit."
    ),
}
```

并非所有平台都需要提示信息——只有当智能体的行为需要有所区别时，才需添加提示。

### 10. 测试

创建 `tests/gateway/test_newplat.py`，用于测试以下内容：

- 根据配置构建适配器
- 消息事件的生成
- 发送方法（对外部 API 进行模拟）
- 平台特定功能（加密、路由等）

### 11. 文档编写

| 文件路径 | 需要添加的内容 |
|----------|--------------|
| `website/docs/user-guide/messaging/newplat.md` | 完整的平台配置页面 |
| `website/docs/user-guide/messaging/index.md` | 平台对比表、架构图、工具集列表、安全相关内容以及后续操作链接 |
| `website/docs/reference/environment-variables.md` | 所有 NEWPLAT_* 环境变量说明 |
| `website/docs/reference/toolsets-reference.md` | hermes-newplat 工具集的相关文档 |
| `website/docs/integrations/index.md` | 对应平台的链接 |
| `website/sidebars.ts` | 文档页面的侧边栏条目 |
| `website/docs/developer-guide/architecture.md` | 适配器的数量及列表展示 |
| `website/docs/developer-guide/gateway-internals.md` | 适配器文件的列表 |

## 同等性审计

在将新平台的 Pull Request 标记为已完成之前，需先针对某个已成熟的平台进行同等性审计：

```bash
# Find every .py file mentioning the reference platform
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# Find every .py file mentioning the new platform
search_files "newplat" output_mode="files_only" file_glob="*.py"

# Any file in the first set but not the second is a potential gap
```

对于 `.md` 和 `.ts` 文件也需重复此操作。逐一检查其中的缺失项——是平台枚举问题（需要更新）还是特定于平台的引用问题（可直接跳过）？

## 常见模式

### 长轮询适配器

如果您的适配器采用长轮询机制（如 Telegram 或 Weixin），则应使用轮询循环任务：

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

如果平台通过您的端点（如企业微信回调）发送消息，请运行一个 HTTP 服务器：

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

对于对响应时间有严格要求的平台（例如微信工作台的5秒限制），系统应立即确认收到请求，随后通过API主动返回智能体的回复。智能体会话的持续时间通常为3至30分钟，因此在回调响应时间内进行即时回复是不可行的。

### 令牌锁定机制

如果适配器使用唯一的凭据维持持久连接，可设置范围限定锁，以防止多个配置文件使用相同的凭据：

```python
from gateway.status import acquire_scoped_lock, release_scoped_lock

async def connect(self, *, is_reconnect: bool = False):
    acquired, _existing = acquire_scoped_lock("newplat", self._token)
    if not acquired:
        logger.error("Token already in use by another profile")
        return False
    # ... connect

async def disconnect(self):
    release_scoped_lock("newplat", self._token)
```

## 参考实现方案

| 适配器 | 架构模式 | 复杂度 | 适用场景参考 |
|---------|----------|--------|--------------|
| `bluebubbles.py` | REST + webhook | 中等 | 简单的 REST API 集成 |
| `weixin.py` | 长轮询 + CDN | 高 | 媒体处理、加密功能 |
| `plugins/platforms/wecom/callback_adapter.py` | 回调/Webhook | 中等 | HTTP 服务器、AES 加密、多应用支持 |
| `plugins/platforms/irc/adapter.py` | 长轮询 + IRC 协议 | 高 | 具有范围令牌锁定功能的完整插件适配器 |
