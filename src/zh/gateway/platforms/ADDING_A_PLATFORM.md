# 添加新的消息平台

将平台添加到 Hermes 网关有两种方式：

## 插件路径（推荐用于社区及第三方开发者）

在 `~/.hermes/plugins/` 目录下创建一个插件目录（对于预打包的插件，则位于 `plugins/platforms/` 下），并在其中放入 `plugin.yaml` 和 `adapter.py` 文件。该适配器需继承自 `BasePlatformAdapter`，并通过 `register(ctx)` 函数中的 `ctx.register_platform()` 方法进行注册。这种方式**无需对 Hermes 核心代码进行任何修改**。

插件系统会自动处理诸多任务：适配器的创建、配置解析、用户授权、定时任务发送、消息发送路由、系统提示信息展示、状态显示以及网关设置等。

此外，还有一些可选的钩子函数，可满足大多数适配器的需求：

- `env_enablement_fn: () -> Optional[dict]` — 在适配器构建之前，根据环境变量为 `PlatformConfig.extra`（以及可选的 `home_channel` 字典）赋值。若没有此函数，仅依赖环境变量的配置在 SDK 实例化之前不会显示在 `hermes gateway status` 或 `get_connected_platforms()` 的输出中。
- `apply_yaml_config_fn: (yaml_cfg, platform_cfg) -> Optional[dict]` — 将该平台的 `config.yaml` 中的键值转换为环境变量，或直接为 `PlatformConfig.extra` 赋值。这样插件就可以自行定义 YAML 结构，而无需为每个平台都在核心的 `gateway/config.py` 中添加大量样板代码。允许修改 `os.environ`（建议使用 `not os.getenv(...)` 这样的保护机制以确保环境变量优先于 YAML 设置）；返回的字典会被合并到 `PlatformConfig.extra` 中。该函数会在 `load_gateway_config()` 函数中、通用共享键处理流程之后以及 `_apply_env_overrides()` 之前被调用。
- `cron_deliver_env_var: str` — 指定 `*_HOME_CHANNEL` 类型环境变量的名称。当设置了该变量后，带有 `deliver=<name>` 参数的定时任务将会被路由到该变量，而无需修改 `cron/scheduler.py` 中硬编码的配置列表。
- `standalone_sender_fn: async (...) -> dict` — 用于为那些在网关之外独立运行的定时任务提供进程外发送功能。如果没有此函数，虽然带有 `deliver=<name>` 参数的任务能够正常触发，但实际发送操作会返回 “No live adapter for platform ‘<name>’” 的错误信息。如需实现完整的定时任务支持，需将该函数与 `cron_deliver_env_var` 一起使用。具体函数签名请参阅文档网站。
- `plugin.yaml` 中的 `requires_env` / `optional_env` 富文本字段 — 用于自动填充 `hermes_cli/config.py` 文件中的 `OPTIONAL_ENV_VARS`，从而使设置向导能够正确显示相关的描述、提示、密码输入选项以及 URL 地址。

**为特定平台定制用户界面。** 当某个平台存在基础适配器无法预判的严格时间限制时（例如 LINE 的 60 秒单次回复令牌、WhatsApp 的 24 小时会话窗口等），适配器可以通过重写 `_keep_typing` 方法，在达到特定阈值时添加一个正在输入的提示气泡，而无需增加额外的参数。务必始终调用 `await super()._keep_typing(...)` 以确保输入心跳信号持续发送，并在 `finally` 块中终止自定义的辅助任务。完整的实现模式可见 `plugins/platforms/line/` 目录（例如 45 秒时触发模板按钮回调、`RequestCache` 状态机、以及为 `/stop` 类型请求提供的 `interrupt_session_activity` 重写功能），详细的实现步骤说明请参阅开发者指南。

**具有相同行为的兄弟适配器。** 当某个平台提供两种传输方式供用户选择时——例如非官方 API 与官方 API、轮询模式与 WebSocket 模式、库 A 与库 B——最佳的结构是创建两个共享同一行为混入类的适配器。WhatsApp 就采用了这种设计：`gateway/platforms/whatsapp.py`（Baileys 网关）和 `gateway/platforms/whatsapp_cloud.py`（Meta Cloud API）都继承自 `gateway/platforms/whatsapp_common.py` 中的 `WhatsAppBehaviorMixin` 类。该混入类负责处理权限控制、允许列表管理、提及信息解析、广播过滤以及符合 WhatsApp 风格的 Markdown 转换等功能——所有这些功能都与具体的平台协议无关。每个适配器则负责处理自身的传输方式。这两个适配器都会注册不同的 `Platform.*` 枚举值，这样网关就可以针对不同的电话号码同时运行这两种适配器。混入类必须在基类列表中位于最前面——即采用 `class WhatsAppAdapter(Mixin, BasePlatformAdapter)` 的写法——这样才能确保混入类中的 `format_message` 方法能够覆盖 `BasePlatformAdapter` 中的默认实现。

完整的可运行示例请参阅 `plugins/platforms/irc/`、`plugins/platforms/teams/` 和 `plugins/platforms/google_chat/` 目录，包含代码示例和钩子函数文档的完整插件指南则可在 `website/docs/developer-guide/adding-platform-adapters.md` 中找到。

---

## 内置路径（仅限核心贡献者）

将平台直接集成到 Hermes 核心中的检查清单。在开发内置适配器时，请以此清单作为参考——其中的每一项都代表着一个实际的集成点。若遗漏任何一项，都可能导致功能异常、缺失某些特性或出现行为不一致的问题。

---

## 1. 核心适配器（`gateway/platforms/<platform>.py`）

该适配器是 `gateway/platforms/base.py` 中 `BasePlatformAdapter` 类的子类。

### 必需的方法

| 方法 | 功能 |
|------|------|
| `__init__(self, config)` | 解析配置并初始化状态。需调用 `super().__init__(config, Platform.YOUR_PLATFORM)` |
| `connect() -> bool` | 连接到目标平台并启动监听器。成功连接后返回 True |
| `disconnect()` | 停止监听器、关闭连接并取消相关任务 |
| `send(chat_id, text, ...) -> SendResult` | 发送文本消息 |
| `send_typing(chat_id)` | 发送正在输入的提示 |
| `send_image(chat_id, image_url, caption) -> SendResult` | 发送图片 |
| `get_chat_info(chat_id) -> dict` | 返回指定聊天的 `{name, type, chat_id}` 信息 |

### 可选的方法（基础类中已提供默认实现）

| 方法 | 功能 |
|------|------|
| `send_document(chat_id, path, caption)` | 发送文件附件 |
| `send_voice(chat_id, path)` | 发送语音消息 |
| `send_video(chat_id, path, caption)` | 发送视频 |
| `send_animation(chat_id, path, caption)` | 发送 GIF 动图 |
| `send_image_file(chat_id, path, caption)` | 从本地文件发送图片 |

### 交互式用户界面（如果您的平台支持可点击按钮，建议使用）

如果您的平台支持包含交互式按钮或菜单的消息，实现这些功能可以让智能体提供更出色的用户体验。即使未进行自定义设置，这些功能也会自动降级为纯文本显示：

| 方法 | 功能 |
|------|------|
| `send_clarify(chat_id, question, choices, clarify_id, session_key, ...)` | 将 “clarify” 工具中的多选问题以可点击按钮的形式呈现。需配合相应的入口处理逻辑，将按钮点击事件路由到 `tools.clarify_gateway.resolve_gateway_clarify` 函数进行处理。 |
| `send_exec_approval(chat_id, command, session_key, description, ...)` | 将危险命令的确认操作以“批准”/“拒绝”按钮的形式呈现。入口处理逻辑会将请求路由到 `tools.approval.resolve_gateway_approval` 函数。 |
| `send_slash_confirm(chat_id, title, message, session_key, confirm_id, ...)` | 将斜杠命令的确认操作（例如 `/reload-mcp`）以“一次性”/“始终”/“取消”按钮的形式呈现。入口处理逻辑会将请求路由到 `tools.slash_confirm.resolve` 函数。 |
| `send_model_picker(...)` | 交互式的 “/model” 模型选择器。Telegram 和 Discord 都使用此功能。 |
| `send_choice_picker(...)` | 用于有限选项命令（如 `/reasoning`、 `/fast`）的扁平单层级选择器。Telegram 使用内嵌键盘，Discord 使用选择菜单，Matrix 则使用反应功能来实现。不支持该功能的平台会自动降级为文本状态卡片显示。 |

参考实现示例可见 `gateway/platforms/telegram.py`、`discord.py` 和 `whatsapp_cloud.py` 文件。各适配器之间都遵循相同的按钮回调标识规则（`cl:<id>:<idx>`、`appr:<id>:<choice>`、`sc:<choice>:<id>`），请确保使用一致的标识格式，这样网关端的处理函数无需修改即可正常工作。

### 必需的函数

```python
def check_<platform>_requirements() -> bool:
    """Check if this platform's dependencies are available."""
```

### 需遵循的关键模式

- 使用 `self.build_source(...)` 来构建 `SessionSource` 对象  
- 调用 `self.handle_message(event)` 将传入的消息转发至网关  
- 使用基础模块中的 `MessageEvent`、`MessageType` 和 `SendResult`  
- 对附件使用 `cache_image_from_bytes`、`cache_audio_from_bytes`、`cache_document_from_bytes` 进行缓存  
- 过滤自发消息（避免回复循环）  
- 若平台支持同步/回显消息，则对其进行过滤  
- 在所有日志输出中遮蔽敏感标识符（如电话号码、令牌）  
- 对流式连接实现带有指数退避和抖动机制的重连功能  
- 若平台对消息大小有限制，请设置 `MAX_MESSAGE_LENGTH`  

---

## 2. 平台枚举 (`gateway/config.py`)

将对应平台添加到 `Platform` 枚举中：

```python
class Platform(Enum):
    ...
    YOUR_PLATFORM = "your_platform"
```

在 `_apply_env_overrides()` 函数中添加环境变量加载功能：

```python
# Your Platform
your_token = os.getenv("YOUR_PLATFORM_TOKEN")
if your_token:
    if Platform.YOUR_PLATFORM not in config.platforms:
        config.platforms[Platform.YOUR_PLATFORM] = PlatformConfig()
    config.platforms[Platform.YOUR_PLATFORM].enabled = True
    config.platforms[Platform.YOUR_PLATFORM].token = your_token
```

如果您的平台不使用令牌或 API 密钥，请更新 `get_connected_platforms()` 函数（例如，WhatsApp 使用 `enabled` 标志，而 Signal 则使用 `extra` 字典）。

```python
elif platform == Platform.YOUR_PLATFORM:
    from gateway.platforms.your_platform import YourAdapter, check_your_requirements
    if not check_your_requirements():
        logger.warning("Your Platform: dependencies not met")
        return None
    return YourAdapter(config)
```

## 4. 权限映射（`gateway/run.py`）

需在 `_is_user_authorized()` 函数中的两个字典中均添加相关内容：

```python
platform_env_map = {
    ...
    Platform.YOUR_PLATFORM: "YOUR_PLATFORM_ALLOWED_USERS",
}
platform_allow_all_map = {
    ...
    Platform.YOUR_PLATFORM: "YOUR_PLATFORM_ALLOW_ALL_USERS",
}
```

## 5. 会话来源（`gateway/session.py`）

如果您的平台需要额外的身份标识字段（例如 Signal 的 UUID 以及电话号码），请使用 `Optional` 类型为这些字段设置默认值，将其添加到 `SessionSource` 数据类中，并同时更新 `base.py` 文件中的 `to_dict()`、`from_dict()` 和 `build_source()` 函数。 

---

## 6. 系统提示信息（`agent/prompt_builder.py`）

添加一个 `PLATFORM_HINTS` 键值对，以便智能体知晓当前所处的平台类型：

```python
PLATFORM_HINTS = {
    ...
    "your_platform": (
        "You are on Your Platform. "
        "Describe formatting capabilities, media support, etc."
    ),
}
```

若缺少此配置，智能体将无法识别自己当前所处的平台，进而可能使用不合适的格式（例如在无法渲染 Markdown 的平台上使用 Markdown 格式）。

```python
"hermes-your-platform": {
    "description": "Your Platform bot toolset",
    "tools": _HERMES_CORE_TOOLS,
    "includes": []
},
```

并将其添加到 `hermes-gateway` 组合体中：

```python
"hermes-gateway": {
    "includes": [..., "hermes-your-platform"]
}
```

## 8. 定时任务交付（`cron/scheduler.py`）

在 `_deliver_result()` 函数中的 `platform_map` 中进行添加：

```python
platform_map = {
    ...
    "your_platform": Platform.YOUR_PLATFORM,
}
```

若缺少此项，`cronjob(action="create", deliver="your_platform", ...)` 将会静默失败。

---

## 9. 发送消息工具（`tools/send_message_tool.py`）

在 `send_message_tool()` 函数中的 `platform_map` 中添加相应内容：

```python
platform_map = {
    ...
    "your_platform": Platform.YOUR_PLATFORM,
}
```

在 `_send_to_platform()` 函数中添加路由功能：

```python
elif platform == Platform.YOUR_PLATFORM:
    return await _send_your_platform(pconfig, chat_id, message)
```

实现 `_send_your_platform()` 函数——这是一个独立的异步函数，无需完整的适配器即可发送单条消息（适用于定时任务以及网关进程之外的 `send_message` 工具）。

请更新工具架构中的 `target` 描述，加入您所使用平台的示例。

---

## 10. 定时任务工具架构 (`tools/cronjob_tools.py`)

请修改 `deliver` 参数的描述及文档字符串，将您的平台列为一种消息传递选项。

---

## 11. 频道目录 (`gateway/channel_directory.py`)

如果您的平台无法枚举聊天记录（大多数平台都无法做到），请将其添加到基于会话的发现列表中：

```python
for plat_name in ("telegram", "whatsapp", "signal", "your_platform"):
```

## 12. 状态显示（`hermes_cli/status.py`）

在“消息平台”部分中的 `platforms` 字典中添加：

```python
platforms = {
    ...
    "Your Platform": ("YOUR_PLATFORM_TOKEN", "YOUR_PLATFORM_HOME_CHANNEL"),
}
```

## 13. 网关设置向导（`hermes_cli/gateway.py`）

将其添加到 `_PLATFORMS` 列表中：

```python
{
    "key": "your_platform",
    "label": "Your Platform",
    "emoji": "📱",
    "token_var": "YOUR_PLATFORM_TOKEN",
    "setup_instructions": [...],
    "vars": [...],
}
```

如果您的平台需要自定义设置逻辑（如连接性测试、二维码生成、策略选择等），请添加一个 `_setup_your_platform()` 函数，并在平台选择开关中将其作为默认选项。

如果您的平台所使用的“已配置”检测方式与标准的 `bool(get_env_value(token_var))` 不同，请相应修改 `_platform_status()` 函数。

---

## 14. 电话号码/身份信息遮蔽 (`agent/redact.py`)

如果您的平台使用敏感标识符（如电话号码等），请在 `agent/redact.py` 文件中添加正则表达式模式及对应的遮蔽函数。这样可确保所有日志输出中的这些标识符都会被屏蔽，而不仅限于您所使用的适配器日志。

---

## 15. 文档编写

| 文件 | 需要更新的内容 |
|------|---------------|
| `README.md` | 功能列表表与文档说明表中的平台信息 |
| `AGENTS.md` | 网关描述及环境变量配置部分 |
| `website/docs/user-guide/messaging/<platform>.md` | **新增** — 完整的设置指南（模板可参考现有平台的文档） |
| `website/docs/user-guide/messaging/index.md` | 架构图、工具集列表、安全示例以及后续操作链接 |
| `website/docs/reference/environment-variables.md` | 该平台相关的所有环境变量 |

---

## 16. 测试 (`tests/gateway/test_<platform>.py`)

建议覆盖的测试项包括：

- 平台枚举是否存在且值正确
- 通过 `_apply_env_overrides` 功能从环境变量加载配置
- 适配器的初始化过程（配置解析、白名单处理、默认值设置）
- 辅助函数的功能（遮蔽处理、数据解析、文件类型识别）
- 会话数据的往返转换（`to_dict` → `from_dict`）
- 权限验证集成（检查平台是否在白名单中）
- 消息发送功能的路由逻辑（检查平台是否在平台映射表中）

可选但很有价值的测试项包括：
- 针对消息处理流程的异步测试（通过模拟平台 API 进行测试）
- SSE/WebSocket 重连逻辑测试
- 附件处理功能测试
- 群组消息过滤功能测试

---

## 快速验证

完成所有设置后，请通过以下方式进行验证：

```bash
# All tests pass
python -m pytest tests/ -q

# Grep for your platform name to find any missed integration points
grep -r "telegram\|discord\|whatsapp\|slack" gateway/ tools/ agent/ cron/ hermes_cli/ toolsets.py \
  --include="*.py" -l | sort -u
# Check each file in the output — if it mentions other platforms but not yours, you missed it
```
