# 添加新的消息平台

将新平台添加到 Hermes 网关有两种方式：

## 插件路径（社区版/第三方推荐）

在 `~/.hermes/plugins/` 目录下创建一个插件目录（对于内置插件，则位于 `plugins/platforms/` 下），并在其中放置 `plugin.yaml` 和 `adapter.py` 文件。该适配器需继承自 `BasePlatformAdapter`，并通过 `register(ctx)` 函数中的 `ctx.register_platform()` 方法进行注册。这种方式**无需对 Hermes 的核心代码进行任何修改**。

插件系统会自动处理诸多功能，包括：适配器的创建、配置解析、用户授权、定时任务发送、消息发送路由、系统提示信息生成、状态显示以及网关配置等。

此外，还提供了若干可选的钩子函数，可满足大多数适配器所需的特殊需求：

- `env_enablement_fn: () -> Optional[dict]` — 在适配器被创建之前，根据环境变量为 `PlatformConfig.extra`（以及可选的 `home_channel` 字典）赋值。若没有此函数，仅依赖环境变量的配置在 SDK 实例化之前，不会显示在 `hermes gateway status` 或 `get_connected_platforms()` 的输出结果中。
- `apply_yaml_config_fn: (yaml_cfg, platform_cfg) -> Optional[dict]` —
  将该平台的 `config.yaml` 中的键值转换为环境变量，或直接注入到 `PlatformConfig.extra` 中。这样一来，插件便可自行定义 YAML 结构，而无需为每个平台在核心的 `gateway/config.py` 文件中添加大量冗余代码。允许修改 `os.environ`（建议使用 `not os.getenv(...)` 这样的保护机制，以确保环境变量的优先级高于 YAML 配置）；返回的字典会被合并到 `PlatformConfig.extra` 中。该函数在 `load_gateway_config()` 函数中调用，位于通用共享密钥处理流程之后、`_apply_env_overrides()` 之前。

- `cron_deliver_env_var: str` — 表示 `*_HOME_CHANNEL` 类型环境变量的名称。当设置此值后，值为 `deliver=<name>` 的定时任务将直接使用该变量，而无需修改 `cron/scheduler.py` 文件中预定义的变量列表。

- `standalone_sender_fn: async (...) -> dict`：用于为那些独立于网关运行的定时任务提供进程外发送功能。如果不使用此函数，虽然值为 `deliver=<name>` 的任务能够正常触发，但实际发送操作会返回 “No live adapter for platform ‘<name>’” 的错误信息。如需实现完整的定时任务支持，需将该函数与 `cron_deliver_env_var` 一起使用。具体函数签名请参阅官方文档。

- `plugin.yaml` 文件中的 `requires_env` / `optional_env` 富文本字段 —
  用于自动填充 `hermes_cli/config.py` 文件中的 `OPTIONAL_ENV_VARS`，从而使配置向导能够正确显示相应的描述、提示信息、密码输入选项以及相关 URL。
**为特定平台设计自定义用户体验。** 当某个平台存在基础适配器无法预判的严格时间限制时（例如 LINE 的 60 秒单次回复令牌、WhatsApp 的 24 小时会话窗口等），适配器可以通过重写 `_keep_typing` 方法，在达到特定阈值时叠加一个临时消息气泡，而无需增加额外的参数。务必始终调用 `await super()._keep_typing(...)` 以确保打字状态心跳持续运行，并在 `finally` 块中终止自定义任务。完整的实现方案可参考 `plugins/platforms/line/` 目录中的相关内容（包括 45 秒时的模板按钮回传处理、`RequestCache` 状态机，以及针对 `/stop` 请求的 `interrupt_session_activity` 重写方法），详细的实现步骤则可在开发者指南页面中找到。

**具有相同行为逻辑的兄弟适配器。** 当某个平台提供两种可选的传输方式时——例如非官方 API 与官方 API、轮询机制与 WebSocket、库 A 与库 B——最合理的架构便是设计两个共享同一行为混入类的适配器。WhatsApp 就采用了这种设计：`gateway/platforms/whatsapp.py`（Baileys 网关）和 `gateway/platforms/whatsapp_cloud.py`（Meta Cloud API）都继承自 `gateway/platforms/whatsapp_common.py` 中的 `WhatsAppBehaviorMixin` 类。该混入类负责处理权限控制、允许列表管理、提及信息解析、广播过滤以及符合 WhatsApp 格式的 Markdown 转换——所有这些功能都与具体平台协议无关。每个适配器则负责处理自身的传输逻辑。二者都会注册不同的 `Platform.*` 枚举值，从而使网关能够针对不同的电话号码同时运行这两个适配器。混入类必须在基类列表中位于最前面——即采用 `class WhatsAppAdapter(Mixin, BasePlatformAdapter)` 的写法——这样混入类中的 `format_message` 方法就能覆盖 `BasePlatformAdapter` 中的默认实现。

如需完整的可用示例，请参阅 `plugins/platforms/irc/`、`plugins/platforms/teams/` 和 `plugins/platforms/google_chat/` 相关文件；而包含代码示例及钩子函数文档的完整插件指南，则可在 `website/docs/developer-guide/adding-platform-adapters.md` 中找到。

---

## 内置路径（仅限核心贡献者）

将平台直接集成到 Hermes 核心中的检查清单。在构建内置适配器时，请以此清单作为参考——其中的每一项都是真正的集成点。若遗漏任何一项，都可能导致功能异常、缺失某些特性或行为不一致。

---

## 1. 核心适配器（`gateway/platforms/<platform>.py`）

该适配器是来自 `gateway/platforms/base.py` 的 `BasePlatformAdapter` 的子类。

### 必需方法

| 方法 | 用途 |
|------|------|
| `__init__(self, config)` | 解析配置并初始化状态。需调用 `super().__init__(config, Platform.YOUR_PLATFORM)` |
| `connect() -> bool` | 连接到平台并启动监听器。成功时返回 True |
| `disconnect()` | 停止监听器、关闭连接并取消任务 |
| `send(chat_id, text, ...) -> SendResult` | 发送文本消息 |
| `send_typing(chat_id)` | 发送正在输入指示 |
| `send_image(chat_id, image_url, caption) -> SendResult` | 发送图片 |
| `get_chat_info(chat_id) -> dict` | 返回聊天的 `{name, type, chat_id}` 信息 |

### 可选方法（基础版本中已提供默认占位实现）

| 方法 | 用途 |
|------|------|
| `send_document(chat_id, path, caption)` | 发送文件附件 |
| `send_voice(chat_id, path)` | 发送语音消息 |
| `send_video(chat_id, path, caption)` | 发送视频 |
| `send_animation(chat_id, path, caption)` | 发送 GIF/动画 |
| `send_image_file(chat_id, path, caption)` | 从本地文件发送图片 |

### 交互式用户界面（若您的平台支持可点击按钮，建议使用）

如果您的平台支持交互式按钮/菜单消息，建议实现这些功能，从而提升智能体的使用体验。在未被覆盖的情况下，它们都会自动降级为普通文本显示：

| 方法 | 用途 |
|------|------|
| `send_clarify(chat_id, question, choices, clarify_id, session_key, ...)` | 将 `clarify` 工具中的多项选择题呈现为可点击的按钮。需配合入站调度机制，将按钮点击事件路由至 `tools.clarify_gateway.resolve_gateway_clarify`。 |
| `send_exec_approval(chat_id, command, session_key, description, ...)` | 将高风险命令的确认流程呈现为“批准”/“拒绝”按钮。入站调度机制会将请求路由至 `tools.approval.resolve_gateway_approval`。 |
| `send_slash_confirm(chat_id, title, message, session_key, confirm_id, ...)` | 将斜杠命令的确认操作（如 `/reload-mcp`）呈现为“一次”、“始终”或“取消”按钮。入站调度机制会将请求路由至 `tools.slash_confirm.resolve`。 |
| `send_model_picker(...)` | 交互式 `/model` 模型选择器。被 Telegram、Discord 和 Slack（Socket 模式）所采用。 |
| `send_choice_picker(...)` | 用于有限选项命令（如 `/reasoning`、`/fast`）的扁平单级选择器。Telegram 通过内联键盘、Discord 通过选择菜单、Matrix 通过反应功能来实现该功能；不支持该功能的平台则会自动降级为文本状态卡片显示。 |
如需参考实现，可查看 `gateway/platforms/telegram.py`、`discord.py` 以及 `whatsapp_cloud.py` 文件。按钮回调 ID 的命名规则（`cl:<id>:<idx>`、`appr:<id>:<choice>`、`sc:<choice>:<id>`）在所有适配器中均保持一致——请遵循该规则，以便网关端的解析器无需修改即可正常工作。

### 必需函数

```python
def check_<platform>_requirements() -> bool:
    """Check if this platform's dependencies are available."""
```

### 需遵循的关键模式

- 使用 `self.build_source(...)` 来构建 `SessionSource` 对象  
- 调用 `self.handle_message(event)` 将接收到的消息转发至网关  
- 使用 `gateway.platforms.event` 中的 `MessageEvent`、`MessageType` 以及基础模块中的 `SendResult`  
- 对附件使用 `cache_image_from_bytes`、`cache_audio_from_bytes`、`cache_document_from_bytes` 进行缓存  
- 过滤自发送消息（避免回复循环）  
- 若平台支持同步/回显消息，则对其进行过滤  
- 在所有日志输出中屏蔽敏感标识符（电话号码、令牌等）  
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

`_create_adapter()`函数会封装该创建机制，并将每个成功生成的适配器与其对应的`GatewayRunner`关联起来。请勿在生命周期回调函数中直接创建平台适配器；在应用启动及重新连接时，必须继续使用该封装函数，这样才能确保在调用`connect()`之前完成配置路由的设置。 

---

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

如果您的平台需要额外的身份识别字段（例如 Signal 的 UUID 以及电话号码），请使用 `Optional` 类型为这些字段设置默认值，并将其添加到 `SessionSource` 数据类中，同时更新 `base.py` 文件中的 `to_dict()`、`from_dict()` 和 `build_source()` 函数。 

---

## 6. 系统提示信息（`agent/prompt_builder.py`）

添加一个 `PLATFORM_HINTS` 键值对，以便智能体知晓其当前所处的平台类型：

```python
PLATFORM_HINTS = {
    ...
    "your_platform": (
        "You are on Your Platform. "
        "Describe formatting capabilities, media support, etc."
    ),
}
```

若缺少此配置，智能体将无法识别自己当前所在的平台，进而可能使用不合适的格式（例如在无法渲染 Markdown 的平台上使用 Markdown 格式）。

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

若缺少此配置，`cronjob(action="create", deliver="your_platform", ...)` 将会静默失败。

---

## 9. 发送消息工具（`tools/send_message_tool.py`）

在 `send_message_tool()` 函数中的 `platform_map` 中添加对应配置：

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

实现 `_send_your_platform()` 函数——这是一个独立的异步函数，无需使用完整的适配器即可发送单条消息（适用于定时任务以及网关进程之外的 `send_message` 工具）。

请更新工具架构中的 `target` 描述，加入您所使用的平台示例。

---

## 10. 定时任务工具架构 (`tools/cronjob_tools.py`)

请修改 `deliver` 参数的描述及文档字符串，将您的平台列为一种消息投递选项。

---

## 11. 频道目录 (`gateway/channel_directory.py`)

如果您的平台无法枚举聊天记录（大多数平台都无法做到），请将其添加到基于会话的发现列表中：

```python
for plat_name in ("telegram", "whatsapp", "signal", "your_platform"):
```

## 12. 状态显示（`hermes_cli/status.py`）

在“消息平台”部分中的 `platforms` 字典中添加相应内容：

```python
platforms = {
    ...
    "Your Platform": ("YOUR_PLATFORM_TOKEN", "YOUR_PLATFORM_HOME_CHANNEL"),
}
```

## 13. 网关设置向导 (`hermes_cli/gateway.py`)

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

如果您的平台对“已配置”状态的判断方式与标准的 `bool(get_env_value(token_var))` 不同，请相应更新 `_platform_status()` 函数。

---

## 14. 电话号码/身份信息遮蔽（`agent/redact.py`）

如果您的平台使用敏感标识符（如电话号码等），请在 `agent/redact.py` 文件中添加正则表达式模式及对应的遮蔽函数。这样即可确保所有日志输出中的这些标识符都会被隐藏，而不仅仅是适配器本身的日志。

---

## 15. 文档编写

| 文件 | 需要更新的内容 |
|------|---------------|
| `README.md` | 功能列表与文档说明表中的平台项 |
| `AGENTS.md` | 网关描述以及环境变量配置部分 |
| `website/docs/user-guide/messaging/<platform>.md` | **新增**——完整的设置指南（模板可参考现有平台的文档） |
| `website/docs/user-guide/messaging/index.md` | 架构图、工具列表表、安全示例以及后续步骤链接 |
| `website/docs/reference/environment-variables.md` | 该平台相关的所有环境变量 |

---

## 16. 测试用例（`tests/gateway/test_<platform>.py`）

建议的测试覆盖率：

- 存在包含正确值的平台枚举  
- 通过 `_apply_env_overrides` 从环境变量加载配置  
- 适配器初始化（配置解析、白名单处理、默认值设置）  
- 辅助函数（内容脱敏、解析、文件类型检测）  
- 会话源的往返转换（to_dict → from_dict）  
- 权限集成（白名单中的平台映射关系）  
- 消息发送工具路由（platform_map 中的平台对应关系）  

可选但非常有价值的功能：  
- 针对消息处理流程的异步测试（模拟平台 API）  
- SSE/WebSocket 重连逻辑  
- 附件处理功能  
- 群组消息过滤功能  

---

## 快速验证  

实现所有功能后，请通过以下方式进行检查：

```bash
# All tests pass
python -m pytest tests/ -q

# Grep for your platform name to find any missed integration points
grep -r "telegram\|discord\|whatsapp\|slack" gateway/ tools/ agent/ cron/ hermes_cli/ toolsets.py \
  --include="*.py" -l | sort -u
# Check each file in the output — if it mentions other platforms but not yours, you missed it
```
