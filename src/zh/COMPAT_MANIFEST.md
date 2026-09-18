# 插件兼容性声明文件（临时方案）

2026年9月进行的功能拆分（PR #102117）将Hermes Agent中的大型模块拆分为了更独立的文件。**内部导入路径并非稳定接口**，在该PR之后，下方列出的那些名称已不再存在于原来的位置。为给外部插件开发者留出更新时间，目前仍可通过在对应模块后添加`PLUGIN-COMPAT`块，从旧模块中导入这些名称。

**此临时方案将于2026-09-14被移除。**它是通过一个单独的提交添加的，未来也会通过回滚该提交来删除。请立即将您的插件更新为从“新位置”列指定的路径进行导入。本仓库内的任何代码均不得使用这些旧路径（否则`scripts/check_compat_pointers.py`脚本会在持续集成测试中失败）。

**受影响的插件将会出现以下情况：**

| 时间节点 | 命令行提示 / `hermes doctor` / `hermes update` | 桌面端 | 插件表现 |
|---|---|---|---|
| 2026-09-14之前 | 显示黄色警告，注明插件名称、日期以及`hermes plugins compat`相关信息 | 每次仅弹出一次模态窗口（针对所有受影响的插件集中显示） | 仍可加载；每次尝试通过旧路径访问时都会触发一次`HermesPluginCompatWarning`警告 |
| 2026-09-14之后 | 显示红色警告：插件**已禁用** | 每次仅弹出一次模态窗口 | **无法加载**；`hermes plugins list`命令会显示禁用原因 |
| 回滚操作完成后 | 同上 | 同上 | 仍无法加载（因为旧路径已不存在） |

对于无法等待开发者更新的用户，可采取以下应急方案：在`config.yaml`文件中设置`plugins.allow_deprecated_imports: true`，这样在日期之后受影响的插件仍可继续加载，直到回滚操作真正移除那些旧路径为止。

**针对插件开发者：** 运行命令 `hermes plugins compat <插件文件路径>`，该命令会输出每一行的 `文件路径:行号`、旧路径与新路径的信息；只要仍有未处理的条目，命令就会以状态码 1 退出。请从“新路径”一列中导入相应的文件。

**系统会发出警告信息。** 当某个进程首次通过这些机制解析某个名称时，Hermes 会生成一个 `HermesPluginCompatWarning`（属于 `FutureWarning` 类型），其中会注明旧路径、新路径以及被移除的目标——每个进程针对每个名称仅触发一次此类警告。修复导入问题后，该警告就会消失。若希望在迁移过程中屏蔽此警告，可使用以下命令：`python -W ignore::hermes_cli.plugin_compat.HermesPluginCompatWarning` 或 `warnings.filterwarnings("ignore", category=HermesPluginCompatWarning)`。

**适用范围。** 该机制仅适用于在模块顶层、分解操作之前定义或导入的公共名称（即不以下划线开头的名称）。私有名称（如 `_foo`、`_TG_NAME_LIMIT`、`_clamp_telegram_names` 等）从未暴露在模块接口中，因此不会被恢复；那些对这类私有名称进行了修补或导入的插件，必须将其替换为对应的公共名称或移至新的模块中。同样，通过临时修改实现的测试用例也不会被保留。

| 类型 | 数量 | 含义 |
|---|---|---|
| moved | 0 | 名称现定义于`新位置`；从旧模块重新导出 |
| moved-lazy | 1148 | 含义相同，通过`__getattr__`延迟解析以避免导入循环 |
| import | 592 | 旧模块曾用于暴露的第三方/标准库名称；已恢复原始导入 |
| restored-def | 290 | 因未被使用而被删除的公共名称；其分解前的原始定义被完整恢复 |
| restored-helper | 41 | 仅因上述某个restored-def需要而恢复的私有辅助函数 |
| restored-import | 17 | 仅因上述某个restored-def需要而重新添加的导入语句 |
| module-stub | 3 | 整个模块已被删除；由替代模块重新导出虚拟模块 |
| unrestorable | 34 | 无法恢复（例如循环变量泄漏）；为保持完整性而列出 |

## 按旧模块分类的名称


### `acp_adapter.auth`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `has_provider` | restored-def | `(已删除；恢复了BASE主体)` |

### `acp_adapter.edit_approval`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `FutureTimeout` | import | `concurrent.futures` |
| `clear_edit_approval_requester` | restored-def | `(已删除；恢复了BASE主体)` |
| `get_edit_approval_requester` | restored-def | `(已删除；恢复了BASE主体)` |

### `acp_adapter.events`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | import | `json` |

### `acp_adapter.server`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ACP_MAX_MODELS_PER_PROVIDER` | 已延迟移动 | `acp_adapter.model_catalog` |
| `AgentThoughtChunk` | 已导入 | `acp.schema` |
| `AudioContentBlock` | 已导入 | `acp.schema` |
| `AvailableCommand` | 已导入 | `acp.schema` |
| `AvailableCommandsUpdate` | 已导入 | `acp.schema` |
| `BlobResourceContents` | 已导入 | `acp.schema` |
| `EmbeddedResourceContentBlock` | 已导入 | `acp.schema` |
| `ImageContentBlock` | 已导入 | `acp.schema` |
| `Path` | 已导入 | `pathlib` |
| `ResourceContentBlock` | 已导入 | `acp.schema` |
| `TextResourceContents` | 已导入 | `acp.schema` |
| `UnstructuredCommandInput` | 已导入 | `acp.schema` |
| `base64` | 已导入 | `base64` |
| `json` | 已导入 | `json` |
| `unquote` | 已导入 | `urllib.parse` |
| `urlparse` | 已导入 | `urllib.parse` |

### `acp_adapter.session`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Lock` | 已导入 | `threading` |

### `agent`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `message_sanitization` | 不可恢复 | `BASE中无顶层定义` |

### `agent.agent_init`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ToolGuardrailDecision` | 已延迟移动 | `agent.tool_guardrails` |

### `agent.agent_runtime_helpers`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `agent_runtime_owns_post_tool_hook` | 已恢复定义 | `(已删除；BASE内容已恢复)` |
| `intent_ack_continuation_enabled` | 已恢复定义 | `(已删除；BASE内容已恢复)` |

### `agent.anthropic_adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CredentialPersistError` | 已延迟移动 | `agent.anthropic_credentials` |
| `Path` | 需导入 | `pathlib` |
| `Tuple` | 需导入 | `typing` |
| `base_url_host_matches` | 已延迟移动 | `utils` |
| `base_url_hostname` | 已延迟移动 | `utils` |
| `claude_code_credentials_path` | 已延迟移动 | `agent.anthropic_credentials` |
| `copy` | 需导入 | `copy` |
| `get_hermes_home` | 已延迟移动 | `hermes_constants` |
| `is_claude_code_token_valid` | 已延迟移动 | `agent.anthropic_credentials` |
| `is_rotation_consumed_uncommitted` | 已延迟移动 | `agent.anthropic_credentials` |
| `json` | 需导入 | `json` |
| `mark_rotation_consumed_uncommitted` | 已延迟移动 | `agent.anthropic_credentials` |
| `os` | 需导入 | `os` |
| `platform` | 需导入 | `platform` |
| `read_claude_code_credentials` | 已延迟移动 | `agent.anthropic_credentials` |
| `read_hermes_oauth_credentials` | 已延迟移动 | `agent.anthropic_credentials` |
| `refresh_anthropic_oauth_pure` | 已延迟移动 | `agent.anthropic_credentials` |
| `resolve_anthropic_token` | 已延迟移动 | `agent.anthropic_credentials` |
| `run_hermes_oauth_login_pure` | 已延迟移动 | `agent.anthropic_credentials` |
| `run_oauth_setup_token` | 已延迟移动 | `agent.anthropic_credentials` |
| `secrets` | 需导入 | `secrets` |
| `stat` | 需导入 | `stat` |
| `urlparse` | 需导入 | `urllib.parse` |

### `agent.aux_accounting`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `get_accounting_context` | 已恢复定义 | `(已删除；基础内容已恢复)` |
### `agent.auxiliary_client`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `NOUS_EXTRA_BODY` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |
| `Path` | 需导入的模块 | `pathlib` |
| `copy` | 需导入的模块 | `copy` |
| `get_async_text_auxiliary_client` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |

### `agent.backend_identity`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `_REASON_SCOPES` | 已恢复的辅助项 | `(已删除；作为 classify_failure_scope 的依赖项已恢复)` |
| `classify_failure_scope` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |

### `agent.background_review`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Path` | 需导入的模块 | `pathlib` |
| `is_background_review_enabled` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |

### `agent.bedrock_adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CONTEXT_OVERFLOW_PATTERNS` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |
| `OVERLOAD_PATTERNS` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |
| `THROTTLE_PATTERNS` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |
| `call_converse_stream` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |
| `classify_bedrock_error` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |
| `is_context_overflow_error` | 已恢复的辅助项 | `(已删除；作为 classify_bedrock_error 的依赖项已恢复)` |
| `is_context_overflow_error` | 已恢复的缺失项 | `(已删除；已恢复为基础版本内容)` |

### `agent.bounded_response`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | 导入项 | `typing` |
| `read_error_body_or_default` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.browser_provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入项 | `typing` |
| `Optional` | 导入项 | `typing` |

### `agent.browser_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 导入项 | `typing` |
| `List` | 导入项 | `typing` |
| `hermes_home_key` | 延迟移动项 | `hermes_constants` |
| `threading` | 导入项 | `threading` |

### `agent.codex_runtime`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `run_codex_create_stream_fallback` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.coding_context`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `_PROFILES` | 已恢复的辅助项 | `(已删除；作为 get_profile 的依赖项恢复)` |
| `coding_system_blocks` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `get_profile` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.context_compressor`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `tool_result_id_variants` | 延迟移动项 | `agent.message_sanitization` |

### `agent.conversation_compression`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CompressionExecutorSaturatedError` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.conversation_loop`

| name | kind | new location |
|---|---|---|
| `COMPRESSION_RETRY_CONTEXT_REDUCED_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `COMPRESSION_RETRY_MESSAGES_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `COMPRESSION_RETRY_TOKENS_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `COMPRESSION_RETRY_TOO_LARGE_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `FailoverReason` | moved-lazy | `agent.error_classifier` |
| `KawaiiSpinner` | moved-lazy | `agent.display` |
| `PARTIAL_STREAM_STUB_ID` | moved-lazy | `hermes_constants` |
| `PRE_API_COMPRESSION_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `adaptive_rate_limit_backoff` | moved-lazy | `agent.retry_utils` |
| `anchored_context_tokens` | moved-lazy | `agent.model_metadata` |
| `automatic_compaction_status_message` | moved-lazy | `agent.context_engine` |
| `capture_usage_anchor` | moved-lazy | `agent.model_metadata` |
| `classify_api_error` | moved-lazy | `agent.error_classifier` |
| `close_interrupted_tool_sequence` | moved-lazy | `agent.message_sanitization` |
| `coalesce_tool_call_id` | moved-lazy | `agent.message_sanitization` |
| `compose_user_api_content` | moved-lazy | `agent.turn_context` |
| `compression_blocked_transiently` | moved-lazy | `agent.conversation_compression` |
| `compression_skipped_due_to_lock` | moved-lazy | `agent.conversation_compression` |
| `context_compression_timed_out` | moved-lazy | `agent.conversation_compression` |
| `conversation_history_after_compression` | moved-lazy | `agent.conversation_compression` |
| `env_var_enabled` | moved-lazy | `utils` |
| `estimate_messages_tokens_rough` | moved-lazy | `agent.model_metadata` |
| `estimate_request_tokens_rough` | moved-lazy | `agent.model_metadata` |
| `estimate_usage_cost` | moved-lazy | `agent.usage_pricing` |
| `get_context_length_from_provider_error` | moved-lazy | `agent.model_metadata` |
| `has_incomplete_scratchpad` | moved-lazy | `agent.trajectory` |
| `is_output_cap_error` | moved-lazy | `agent.model_metadata` |
| `is_repetition_dominated` | moved-lazy | `agent.repetition_guard` |
| `is_zai_coding_overload_error` | moved-lazy | `agent.retry_utils` |
| `jittered_backoff` | moved-lazy | `agent.retry_utils` |
| `normalize_usage` | moved-lazy | `agent.usage_pricing` |
| `os` | import | `os` |
| `parse_available_output_tokens_from_error` | moved-lazy | `agent.model_metadata` |
| `random` | import | `random` |
| `reanchor_current_turn_user_idx` | moved-lazy | `agent.turn_context` |
| `save_context_length` | moved-lazy | `agent.model_metadata` |
| `serialized_messages_bytes` | moved-lazy | `agent.message_sanitization` |
| `splice_provider_projection` | moved-lazy | `agent.provider_projection` |
| `ssl` | import | `ssl` |
| `sys` | import | `sys` |
| `zai_coding_overload_retry_ceiling` | moved-lazy | `agent.retry_utils` |

### `agent.credential_sources`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `register` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.display`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `get_friendly_tool_labels` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.error_surface`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `LAYER_RUNTIME` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.estop`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | 需导入的模块 | `os` |

### `agent.file_safety`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `PROFILE_SCOPED_AREAS` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `classify_cross_profile_target` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `get_cross_profile_warning` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.image_gen_provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `base64` | 需导入的模块 | `base64` |
| `datetime` | 需导入的模块 | `datetime` |
| `uuid` | 需导入的模块 | `uuid` |

### `agent.image_gen_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 需导入的模块 | `typing` |
| `List` | 需导入的模块 | `typing` |
| `hermes_home_key` | 已延迟移动 | `hermes_constants` |
| `threading` | 需导入的模块 | `threading` |

### `agent.learning_graph_render`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Grid` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `Run` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.lsp.eventlog`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `_announce_once` | restored-helper | `(已删除；作为 log_no_server_configured 的依赖项被恢复)` |
| `_announced_no_server` | restored-helper | `(已删除；作为 log_no_server_configured 的依赖项被恢复)` |
| `log_no_server_configured` | restored-def | `(已删除；基础内容已恢复)` |

### `agent.lsp.protocol`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ERROR_REQUEST_CANCELLED` | restored-def | `(已删除；基础内容已恢复)` |

### `agent.monitoring.cron_health`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `GatewayHealthSnapshot` | moved-lazy | `agent.monitoring.gateway_health` |
| `hashlib` | import | `hashlib` |

### `agent.monitoring.emitter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `TelemetryEmitter` | restored-def | `(已删除；基础内容已恢复)` |

### `agent.monitoring.gateway_health`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `redact_gateway_message` | restored-def | `(已删除；基础内容已恢复)` |

### `agent.monitoring.gateway_health_export`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `re` | import | `re` |

### `agent.nous_rate_guard`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `atomic_replace` | moved-lazy | `utils` |
| `tempfile` | import | `tempfile` |

### `agent.outbound_webhooks`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Path` | import | `pathlib` |
| `datetime` | import | `datetime` |
| `timezone` | import | `datetime` |

### `agent.pet.generate.atlas`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `COLUMNS` | restored-def | `(已删除；基础内容已恢复)` |
| `FRAME_COUNTS` | restored-def | `(已删除；基础内容已恢复)` |
| `ROWS` | restored-def | `(已删除；基础内容已恢复)` |
| `atlas_to_webp_bytes` | restored-def | `(已删除；基础内容已恢复)` |
| `io` | restored-import | `io` |
| `io` | import | `io` |

### `agent.prompt_builder`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `List` | import | `typing` |
| `org_id_of_path` | moved-lazy | `agent.skill_utils` |

### `agent.prompt_cache_boundary`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `clear_stable_prefixes` | restored-def | `(已删除；基础内容已恢复)` |

### `agent.proxy_sources.iron_proxy`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `stat` | import | `stat` |

### `agent.reasoning_effort`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CODEX_RESPONSES_EFFORTS` | restored-def | `(已删除；基础内容已恢复)` |

### `agent.relay_llm`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `dataclass` | import | `dataclasses` |

### `agent.relay_runtime`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `auto` | 导入模块 | `enum` |
| `emit_mark` | 已恢复定义 | `(已删除；基础内容已恢复)` |
| `ensure_session` | 已恢复定义 | `(已删除；基础内容已恢复)` |
| `get_host` | 已恢复定义 | `(已删除；基础内容已恢复)` |
| `get_session_handle` | 已恢复定义 | `(已删除；基础内容已恢复)` |
| `run_in_session` | 已恢复定义 | `(已删除；基础内容已恢复)` |
| `run_in_session_async` | 已恢复定义 | `(已删除；基础内容已恢复)` |

### `agent.relay_tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `asyncio` | 导入模块 | `asyncio` |
| `inspect` | 导入模块 | `inspect` |

### `agent.review_idle_queue`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `List` | 导入模块 | `typing` |

### `agent.secret_sources._cache`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `FetchResult` | 拖延移动 | `agent.secret_sources.base` |
| `is_valid_env_name` | 拖延移动 | `agent.secret_sources.base` |

### `agent.secret_sources.bitwarden`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DiskCache` | 拖延移动 | `agent.secret_sources._cache` |
| `apply_bitwarden_secrets` | 已恢复定义 | `(已删除；基础内容已恢复)` |
| `stat` | 导入模块 | `stat` |

### `agent.secret_sources.command`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `apply_command_secrets` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `get_command_secret` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `get_source_environment` | 暂时移动项 | `agent.secret_sources.base` |
| `list_command_secrets` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `parse_secret_output` | 已恢复的辅助函数 | `(已删除；作为 get_command_secret 的依赖项被恢复)` |
| `parse_secret_output` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.secret_sources.onepassword`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DiskCache` | 暂时移动项 | `agent.secret_sources._cache` |
| `hashlib` | 需导入的模块 | `hashlib` |

### `agent.shell_hooks`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `shlex` | 需导入的模块 | `shlex` |

### `agent.skill_bundles`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `re` | 需导入的模块 | `re` |

### `agent.skill_utils`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `get_scan_ordered_skills_dirs` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.ssl_guard`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `verify_ca_bundle_with_fallback` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `agent.system_prompt`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `OPENAI_MODEL_EXECUTION_GUIDANCE` | 暂时移动项 | `agent.prompt_builder` |

### `agent.terminal_env_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 导入项 | `typing` |
| `hermes_home_key` | 暂缓移动 | `hermes_constants` |
| `threading` | 导入项 | `threading` |

### `agent.transcript_repair`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | 导入项 | `typing` |

### `agent.transcription_provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `List` | 导入项 | `typing` |
| `logger` | 暂缓移动 | `agent.i18n` |
| `logging` | 导入项 | `logging` |

### `agent.transcription_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 导入项 | `typing` |
| `List` | 导入项 | `typing` |
| `Optional` | 导入项 | `typing` |
| `hermes_home_key` | 暂缓移动 | `hermes_constants` |
| `threading` | 导入项 | `threading` |

### `agent.transports.chat_completions`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 导入项 | `typing` |

### `agent.transports.codex`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 导入项 | `typing` |
| `List` | 导入项 | `typing` |
| `Tuple` | 导入项 | `typing` |

### `agent.transports.codex_app_server`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `field` | 导入项 | `dataclasses` |
| `time` | 导入项 | `time` |

### `agent.tts_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 导入项 | `typing` |
| `List` | 导入项 | `typing` |
| `Optional` | 导入项 | `typing` |
| `hermes_home_key` | 暂缓移动 | `hermes_constants` |
| `threading` | 导入项 | `threading` |

### `agent.turn_context`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `IDLE_COMPACTION_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `PREFLIGHT_COMPRESSION_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `automatic_compaction_status_message` | moved-lazy | `agent.context_engine` |
| `compression_skipped_due_to_lock` | moved-lazy | `agent.conversation_compression` |
| `conversation_history_after_compression` | moved-lazy | `agent.conversation_compression` |

### `agent.turn_retry_state`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `fields` | import | `dataclasses` |

### `agent.usage_pricing`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEFAULT_PRICING` | restored-def | `(已删除；BASE结构体已恢复)` |

### `agent.video_gen_provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `base64` | import | `base64` |
| `datetime` | import | `datetime` |
| `uuid` | import | `uuid` |

### `agent.video_gen_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | import | `typing` |
| `List` | import | `typing` |
| `hermes_home_key` | moved-lazy | `hermes_constants` |
| `threading` | import | `threading` |

### `agent.web_search_provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | import | `typing` |

### `agent.web_search_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | import | `typing` |
| `List` | import | `typing` |
| `hermes_home_key` | moved-lazy | `hermes_constants` |
| `threading` | import | `threading` |

### `cli`

| name | kind | new location |
|---|---|---|
| `AIAgent` | restored-def | `(deleted; BASE body restored)` |
| `CanonicalUsage` | restored-def | `(deleted; BASE body restored)` |
| `CompletionsMenu` | import | `prompt_toolkit.layout.menus` |
| `Condition` | import | `prompt_toolkit.filters` |
| `ConditionalContainer` | import | `prompt_toolkit.layout` |
| `ConditionalProcessor` | import | `prompt_toolkit.layout.processors` |
| `DEFAULT_BROWSER_CDP_URL` | moved-lazy | `hermes_cli.browser_connect` |
| `Dimension` | import | `prompt_toolkit.layout.dimension` |
| `FileHistory` | import | `prompt_toolkit.history` |
| `FormattedTextControl` | import | `prompt_toolkit.layout` |
| `HERMES_AGENT_LOGO` | moved-lazy | `hermes_cli.banner` |
| `HERMES_CADUCEUS` | moved-lazy | `hermes_cli.banner` |
| `HSplit` | import | `prompt_toolkit.layout` |
| `KeyBindings` | import | `prompt_toolkit.key_binding` |
| `Layout` | import | `prompt_toolkit.layout` |
| `PTStyle` | import | `prompt_toolkit.styles` |
| `Panel` | import | `rich.panel` |
| `PasswordProcessor` | import | `prompt_toolkit.layout.processors` |
| `Processor` | import | `prompt_toolkit.layout.processors` |
| `SlashCommandAutoSuggest` | moved-lazy | `hermes_cli.commands_completion` |
| `SlashCommandCompleter` | moved-lazy | `hermes_cli.commands_completion` |
| `TextArea` | import | `prompt_toolkit.widgets` |
| `Transformation` | import | `prompt_toolkit.layout.processors` |
| `Window` | import | `prompt_toolkit.layout` |
| `WindowAlign` | import | `prompt_toolkit.layout` |
| `base64` | import | `base64` |
| `build_welcome_banner` | moved-lazy | `hermes_cli.banner` |
| `concurrent` | import | `concurrent.futures` |
| `copy` | import | `copy` |
| `display_hermes_home` | moved-lazy | `hermes_constants` |
| `estimate_usage_cost` | moved-lazy | `agent.usage_pricing` |
| `get_all_toolsets` | moved-lazy | `toolsets` |
| `get_job` | moved-lazy | `cron.jobs` |
| `get_toolset_for_tool` | moved-lazy | `model_tools` |
| `get_toolset_info` | moved-lazy | `toolsets` |
| `init_skin_from_config` | moved-lazy | `hermes_cli.skin_engine` |
| `is_browser_debug_ready` | moved-lazy | `hermes_cli.browser_connect` |
| `is_table_divider` | moved-lazy | `agent.markdown_tables` |
| `looks_like_table_row` | moved-lazy | `agent.markdown_tables` |
| `manual_chrome_debug_command` | moved-lazy | `hermes_cli.browser_connect` |
| `print_config_warnings` | moved-lazy | `hermes_cli.config` |
| `prompt_for_secret` | moved-lazy | `hermes_cli.callbacks` |
| `rich_box` | import | `rich` |
| `set_friendly_tool_labels` | moved-lazy | `agent.display` |
| `set_tool_preview_max_len` | moved-lazy | `agent.display` |
| `setup_logging` | moved-lazy | `hermes_logging` |
| `tempfile` | import | `tempfile` |
| `try_launch_chrome_debug` | unrestorable | `no top-level definition on BASE` |

### `cron.jobs`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `clear_drift_alerted` | restored-def | `(已删除；基础内容已恢复)` |

### `cron.scheduler`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BOT_CHAT_PLATFORM` | moved-lazy | `cron.scheduler_delivery` |
| `SharedRouteAdapters` | moved-lazy | `cron.scheduler_preflight` |
| `asyncio` | import | `asyncio` |
| `cron_delivery_targets` | moved-lazy | `cron.scheduler_delivery` |
| `parse_bot_chat_deliver_token` | moved-lazy | `cron.scheduler_delivery` |
| `shutil` | import | `shutil` |
| `signal` | import | `signal` |

### `cron.scheduler_provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `provider_supports_fire_cancel` | restored-def | `(已删除；基础内容已恢复)` |

### `gateway.browser_control_artifacts`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ArtifactOverwrite` | restored-def | `(已删除；基础内容已恢复)` |

### `gateway.browser_control_broker`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BROWSER_CONTROL_ALL_CAPABILITIES` | restored-def | `(已删除；基础内容已恢复)` |

### `gateway.config`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | import | `json` |

### `gateway.delivery_ledger`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `debug_rows` | restored-def | `(已删除；基础内容已恢复)` |
| `json` | restored-import | `json` |
| `json` | import | `json` |

### `gateway.disk_status`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `logger` | moved-lazy | `gateway.run` |
| `logging` | import | `logging` |
### `gateway.hosted_room_discussion`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入项 | `json` |

### `gateway.hosted_room_driver`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Iterator` | 导入项 | `typing` |
| `Path` | 导入项 | `pathlib` |
| `contextmanager` | 导入项 | `contextlib` |
| `re` | 导入项 | `re` |

### `gateway.hosted_room_execution_policy`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入项 | `json` |
| `re` | 导入项 | `re` |

### `gateway.hosted_room_peer`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `RoomLinkProbe` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `RoomLinkProbe` | 已恢复的辅助项 | `(已删除；作为 select_room_link 的依赖项恢复)` |
| `_LINK_PRIORITY` | 已恢复的辅助项 | `(已删除；作为 select_room_link 的依赖项恢复)` |
| `select_room_link` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `time` | 导入项 | `time` |

### `gateway.hosted_room_replicas`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `MAX_EVENT_JSON_BYTES` | 延迟移动项 | `gateway.hosted_rooms` |
| `MAX_ROOM_ID_CHARS` | 延迟移动项 | `gateway.hosted_rooms` |
| `Path` | 导入项 | `pathlib` |
| `time` | 导入项 | `time` |

### `gateway.hosted_rooms`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Iterator` | 导入项 | `typing` |
| `NoReturn` | 导入项 | `typing` |
| `contextmanager` | 导入项 | `contextlib` |
| `time` | 导入项 | `time` |

### `gateway.kanban_watchers`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Callable` | 导入项 | `typing` |
| `Context` | 导入项 | `contextvars` |
| `logging` | 导入项 | `logging` |
| `re` | 导入项 | `re` |
| `sqlite3` | 导入项 | `sqlite3` |
| `t` | 拖迟移动 | `agent.i18n` |

### `gateway.memory_status`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `logger` | 拖迟移动 | `gateway.run` |
| `logging` | 导入项 | `logging` |

### `gateway.platforms.helpers`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 导入项 | `typing` |
| `TYPE_CHECKING` | 导入项 | `typing` |
| `TextBatchAggregator` | 恢复定义 | `(已删除；基础代码体已恢复)` |
| `asyncio` | 恢复导入 | `asyncio` |
| `asyncio` | 导入项 | `asyncio` |

### `gateway.platforms.qqbot`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ApprovalSender` | 无法恢复 | `BASE中不存在顶层定义` |

### `gateway.platforms.qqbot.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `base64` | 导入项 | `base64` |
| `mimetypes` | 导入项 | `mimetypes` |

### `gateway.platforms.qqbot.chunked_upload`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ApiRequestFn` | 恢复定义 | `(已删除；基础代码体已恢复)` |
| `Optional` | 导入项 | `typing` |
| `functools` | 导入项 | `functools` |

### `gateway.platforms.qqbot.keyboards`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ApprovalSender` | 已恢复的删除项 | `(已删除；基础内容已恢复)` |
| `Awaitable` | 已恢复的导入项 | `typing` |
| `Awaitable` | 导入项 | `typing` |
| `Callable` | 已恢复的导入项 | `typing` |
| `Callable` | 导入项 | `typing` |
| `PostMessageFn` | 已恢复的辅助项 | `(已删除；作为 ApprovalSender 的依赖项被恢复)` |
| `PostMessageFn` | 已恢复的删除项 | `(已删除；基础内容已恢复)` |
| `logger` | 已恢复的辅助项 | `(已删除；作为 ApprovalSender 的依赖项被恢复)` |
| `logger` | 延迟移动项 | `gateway.platforms.qqbot.adapter` |
| `logging` | 已恢复的导入项 | `logging` |
| `logging` | 导入项 | `logging` |

### `gateway.platforms.signal`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEFAULT_EXT_TO_MIME` | 延迟移动项 | `gateway.platforms.media_cache` |
| `TYPING_INTERVAL` | 已恢复的删除项 | `(已删除；基础内容已恢复)` |

### `gateway.platforms.weixin`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `MSG_TYPE_USER` | 已恢复的删除项 | `(已删除；基础内容已恢复)` |
| `struct` | 导入项 | `struct` |

### `gateway.platforms.yuanbao`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `AUTH_FAILED_CODES` | restored-def | `(已删除；基础内容已恢复)` |
| `AUTH_RETRYABLE_CODES` | restored-def | `(已删除；基础内容已恢复)` |
| `FileUrlHandler` | restored-def | `(已删除；基础内容已恢复)` |
| `GroupQueryService` | restored-def | `(已删除；基础内容已恢复)` |
| `REPLY_REF_TTL_S` | restored-def | `(已删除；基础内容已恢复)` |
| `get_active_adapter` | restored-def | `(已删除；基础内容已恢复)` |
| `send_yuanbao_direct` | restored-def | `(已删除；基础内容已恢复)` |

### `gateway.platforms.yuanbao_media`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `COS_USE_ACCELERATE` | restored-def | `(已删除；基础内容已恢复)` |

### `gateway.platforms.yuanbao_proto`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEBUG_MODE` | restored-def | `(已删除；基础内容已恢复)` |
| `_encode_forward_msg` | restored-helper | `(已删除；作为 encode_forward_msg_data 的依赖项被恢复)` |
| `_encode_forward_msg_content` | restored-helper | `(已删除；作为 encode_forward_msg_data 的依赖项被恢复)` |
| `_encode_forward_multimedia` | restored-helper | `(已删除；作为 encode_forward_msg_data 的依赖项被恢复)` |
| `encode_forward_msg_data` | restored-def | `(已删除；基础内容已恢复)` |
| `logger` | moved-lazy | `gateway.platforms.base` |
| `logging` | import | `logging` |

### `gateway.relay`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `relay_bot_username` | restored-def | `(已删除；基础内容已恢复)` |
### `gateway.relay.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `cast` | 导入项 | `typing` |

### `gateway.relay.auth`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DELIVERY_SIG_HEADER` | 已恢复的被移除项 | `(已删除；基础内容已恢复)` |
| `DELIVERY_TS_HEADER` | 已恢复的被移除项 | `(已删除；基础内容已恢复)` |
| `Optional` | 导入项 | `typing` |
| `Sequence` | 导入项 | `typing` |
| `_DEFAULT_MAX_SKEW_SECONDS` | 已恢复的辅助项 | `(已删除；作为 verify_delivery_signature 的依赖项被恢复)` |
| `_delivery_payload` | 已恢复的辅助项 | `(已删除；作为 verify_delivery_signature 的依赖项被恢复)` |
| `_hmac_hex` | 已恢复的辅助项 | `(已删除；作为 verify_delivery_signature 的依赖项被恢复)` |
| `verify_delivery_signature` | 已恢复的被移除项 | `(已删除；基础内容已恢复)` |
| `verify_signature` | 已恢复的辅助项 | `(已删除；作为 verify_delivery_signature 的依赖项被恢复)` |
| `verify_signature` | 已恢复的被移除项 | `(已删除；基础内容已恢复)` |
| `verify_token` | 已恢复的被移除项 | `(已删除；基础内容已恢复)` |

### `gateway.response_filters`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `SILENT_REPLY_TOKEN` | 已恢复的被移除项 | `(已删除；基础内容已恢复)` |

### `gateway.restart_loop_guard`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `is_restart_loop_tripped` | 已恢复的被移除项 | `(已删除；基础内容已恢复)` |

### `gateway.run`

| name | kind | new location |
|---|---|---|
| `Awaitable` | import | `typing` |
| `Context` | import | `contextvars` |
| `DEFAULT_GATEWAY_POST_INTERRUPT_GRACE_TIMEOUT` | moved-lazy | `gateway.restart` |
| `DEFAULT_HEARTBEAT_INTERVAL_S` | moved-lazy | `gateway.shutdown_watchdog` |
| `DEFAULT_LEASE_WAIT` | moved-lazy | `gateway.turn_lease` |
| `DEFAULT_LOOP_WATCHDOG_INTERVAL_S` | moved-lazy | `gateway.shutdown_watchdog` |
| `DEFAULT_LOOP_WATCHDOG_MAX_STRIKES` | moved-lazy | `gateway.shutdown_watchdog` |
| `DEFAULT_LOOP_WATCHDOG_TIMEOUT_S` | moved-lazy | `gateway.shutdown_watchdog` |
| `EphemeralReply` | moved-lazy | `gateway.platforms.base` |
| `GATEWAY_FATAL_CONFIG_EXIT_CODE` | moved-lazy | `gateway.restart` |
| `GATEWAY_SERVICE_RESTART_EXIT_CODE` | moved-lazy | `gateway.restart` |
| `SessionEntry` | moved-lazy | `gateway.session` |
| `TranscriptReadError` | moved-lazy | `gateway.session_transcript` |
| `TurnContext` | moved-lazy | `gateway.turn_context` |
| `TurnLeaseTimeoutError` | moved-lazy | `gateway.turn_lease` |
| `TurnRunner` | moved-lazy | `gateway.run_turn_runner` |
| `Union` | import | `typing` |
| `arm_shutdown_watchdog` | moved-lazy | `gateway.shutdown_watchdog` |
| `atomic_json_write` | moved-lazy | `utils` |
| `base_url_hostname` | moved-lazy | `utils` |
| `build_auto_tts_output_path` | moved-lazy | `gateway.platforms.base` |
| `build_channel_continuity_note` | moved-lazy | `gateway.session` |
| `build_session_context` | moved-lazy | `gateway.session` |
| `build_session_context_prompt` | moved-lazy | `gateway.session` |
| `consume_detached_task_result` | moved-lazy | `agent.async_utils` |
| `faulthandler` | import | `faulthandler` |
| `functools` | import | `functools` |
| `inspect` | import | `inspect` |
| `is_global_startup_conflict` | moved-lazy | `gateway.restart` |
| `is_shared_multi_user_session` | moved-lazy | `gateway.session` |
| `is_truthy_value` | moved-lazy | `utils` |
| `load_dotenv` | import | `dotenv` |
| `looks_like_telegram_private_chat_id` | moved-lazy | `gateway.delivery` |
| `loop_heartbeat_forever` | moved-lazy | `gateway.shutdown_watchdog` |
| `merge_pending_message_event` | moved-lazy | `gateway.platforms.base` |
| `neutralize_untrusted_inline_text` | moved-lazy | `gateway.session` |
| `parse_cron_drain_timeout` | moved-lazy | `gateway.restart` |
| `parse_restart_after_turn_timeout` | moved-lazy | `gateway.restart` |
| `parse_restart_drain_timeout` | moved-lazy | `gateway.restart` |
| `parse_signal_interrupt_grace_timeout` | moved-lazy | `gateway.restart` |
| `project_compaction_message_for_display` | moved-lazy | `agent.compaction_display` |
| `queue` | import | `queue` |
| `repair_explicit_computer_use_media_paths` | moved-lazy | `gateway.media_repair` |
| `resolve_cron_drain_budget` | moved-lazy | `gateway.restart` |
| `resolve_delivery_transport` | moved-lazy | `gateway.delivery` |
| `resolve_shutdown_watchdog_delay` | moved-lazy | `gateway.shutdown_watchdog` |
| `start_loop_liveness_watchdog` | moved-lazy | `gateway.shutdown_watchdog` |
| `t` | moved-lazy | `agent.i18n` |
| `timedelta` | import | `datetime` |
| `timezone` | import | `datetime` |
| `utf16_len` | moved-lazy | `gateway.platforms.base` |

### `gateway.session`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `SessionResetPolicy` | 已延迟移动 | `gateway.config` |
| `TranscriptReadError` | 已延迟移动 | `gateway.session_transcript` |
| `atomic_replace` | 已延迟移动 | `utils` |
| `auto_continue_freshness_window` | 已延迟移动 | `gateway.session_lifecycle` |
| `extract_api_content_sidecar` | 已延迟移动 | `agent.turn_context` |
| `normalize_whatsapp_identifier` | 已延迟移动 | `gateway.whatsapp_identity` |
| `replace` | 导入项 | `dataclasses` |
| `uuid` | 导入项 | `uuid` |

### `gateway.slash_access`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Tuple` | 导入项 | `typing` |

### `gateway.slash_commands`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入项 | `typing` |
| `HISTORY_UNREADABLE` | 已延迟移动 | `gateway.slash_commands_status` |
| `MessageType` | 已延迟移动 | `gateway.platforms.event` |
| `SessionSource` | 已延迟移动 | `gateway.session` |
| `base_url_host_matches` | 已延迟移动 | `utils` |
| `build_session_key` | 已延迟移动 | `gateway.session` |
| `clear_model_endpoint_credentials` | 已延迟移动 | `hermes_cli.config` |
| `extract_api_content_sidecar` | 已延迟移动 | `agent.turn_context` |
| `fetch_account_usage` | 已延迟移动 | `agent.account_usage` |
| `hashlib` | 导入项 | `hashlib` |
| `is_shared_multi_user_session` | 已延迟移动 | `gateway.session` |
| `render_account_usage_lines` | 已延迟移动 | `agent.account_usage` |

### `gateway.startup_watchdog`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `*` | module-stub | `gateway.shutdown_watchdog` |

### `gateway.status`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `clear_planned_stop_marker` | restored-def | `(已删除；基础内容已恢复)` |
| `is_gateway_running` | restored-def | `(已删除；基础内容已恢复)` |

### `gateway.sticker_cache`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | import | `os` |
| `tempfile` | import | `tempfile` |

### `gateway.stream_consumer`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `MEDIA_TAG_CLEANUP_RE` | moved-lazy | `gateway.platforms.base` |
| `escape_code_fences_for_display` | moved-lazy | `gateway.stream_consumer_fences` |

### `gateway.stream_dispatch`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ToolCallFinished` | moved-lazy | `gateway.stream_events` |

### `gateway.systemd_notify`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | import | `typing` |

### `hermes_cli.agent_import`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `backup_memory_file` | restored-def | `(已删除；基础内容已恢复)` |
| `default_source_dir` | restored-def | `(已删除；基础内容已恢复)` |

### `hermes_cli.auth`

| name | kind | new location |
|---|---|---|
| `BaseHTTPRequestHandler` | import | `http.server` |
| `CODEX_OAUTH_USER_AGENT` | moved-lazy | `hermes_cli.auth_constants` |
| `CODEX_QUOTA_PROBE_MIN_INTERVAL_SECONDS` | moved-lazy | `hermes_cli.auth_codex` |
| `DEFAULT_SPOTIFY_REDIRECT_URI` | moved-lazy | `hermes_cli.auth_constants` |
| `DEVICE_AUTH_POLL_INTERVAL_CAP_SECONDS` | moved-lazy | `hermes_cli.auth_constants` |
| `HTTPServer` | import | `http.server` |
| `MINIMAX_OAUTH_GRANT_TYPE` | moved-lazy | `hermes_cli.auth_constants` |
| `NOUS_INFERENCE_INVOKE_SCOPE` | moved-lazy | `hermes_cli.auth_constants` |
| `NOUS_SHARED_STORE_FILENAME` | moved-lazy | `hermes_cli.auth_nous` |
| `OAUTH_OVER_SSH_DOCS_URL` | moved-lazy | `hermes_cli.auth_constants` |
| `QWEN_OAUTH_CLIENT_ID` | moved-lazy | `hermes_cli.auth_constants` |
| `QWEN_OAUTH_TOKEN_URL` | moved-lazy | `hermes_cli.auth_constants` |
| `SINGLE_USE_OAUTH_SINGLETON_FILES` | moved-lazy | `hermes_cli.auth_oauth_grants` |
| `SPOTIFY_ACCESS_TOKEN_REFRESH_SKEW_SECONDS` | moved-lazy | `hermes_cli.auth_constants` |
| `SPOTIFY_DASHBOARD_URL` | moved-lazy | `hermes_cli.auth_constants` |
| `TYPE_CHECKING` | import | `typing` |
| `XAI_OAUTH_DEVICE_CODE_URL` | moved-lazy | `hermes_cli.auth_constants` |
| `XAI_OAUTH_DISCOVERY_URL` | moved-lazy | `hermes_cli.auth_constants` |
| `XAI_OAUTH_ISSUER` | moved-lazy | `hermes_cli.auth_constants` |
| `base64` | import | `base64` |
| `hashlib` | import | `hashlib` |
| `parse_qs` | import | `urllib.parse` |
| `refresh_nous_oauth_pure` | moved-lazy | `hermes_cli.auth_nous` |
| `ssl` | import | `ssl` |
| `subprocess` | import | `subprocess` |
| `sys` | import | `sys` |
| `urlencode` | import | `urllib.parse` |

### `hermes_cli.backup`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `copy_db_and_verify` | restored-def | `(已删除；基础内容已恢复)` |

### `hermes_cli.browser_connect`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `try_launch_chrome_debug` | restored-def | `(已删除；基础内容已恢复)` |

### `hermes_cli.callbacks`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `approval_callback` | restored-def | `(已删除；基础内容已恢复)` |
| `clarify_callback` | restored-def | `(已删除；基础内容已恢复)` |

### `hermes_cli.checkpoints`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `cmd_list` | moved-lazy | `hermes_cli.plugins_cmd` |
| `datetime` | import | `datetime` |

### `hermes_cli.commands`

| name | kind | new location |
|---|---|---|
| `Any` | import | `typing` |
| `AutoSuggest` | unrestorable | `no top-level definition on BASE` |
| `Callable` | import | `collections.abc` |
| `Completer` | unrestorable | `no top-level definition on BASE` |
| `Completion` | unrestorable | `no top-level definition on BASE` |
| `Dict` | import | `typing` |
| `Mapping` | import | `collections.abc` |
| `Optional` | import | `typing` |
| `Sequence` | import | `collections.abc` |
| `SlashCommandAutoSuggest` | moved-lazy | `hermes_cli.commands_completion` |
| `SlashCommandCompleter` | moved-lazy | `hermes_cli.commands_completion` |
| `Suggestion` | unrestorable | `no top-level definition on BASE` |
| `Tuple` | import | `typing` |
| `_CMD_NAME_LIMIT` | restored-helper | `(deleted; restored as a dependency of discord_skill_commands)` |
| `_clamp_command_names` | restored-helper | `(deleted; restored as a dependency of discord_skill_commands)` |
| `_collect_gateway_skill_entries` | restored-helper | `(deleted; restored as a dependency of discord_skill_commands)` |
| `_requires_argument` | restored-helper | `(deleted; restored as a dependency of discord_skill_commands)` |
| `discord_skill_commands` | restored-def | `(deleted; BASE body restored)` |
| `discord_skill_commands_by_category` | moved-lazy | `hermes_cli.commands_platforms` |
| `field` | import | `dataclasses` |
| `key` | unrestorable | `no top-level definition on BASE` |
| `m` | unrestorable | `no top-level definition on BASE` |
| `os` | import | `os` |
| `shutil` | import | `shutil` |
| `slack_app_manifest` | moved-lazy | `hermes_cli.commands_platforms` |
| `slack_native_slashes` | moved-lazy | `hermes_cli.commands_platforms` |
| `slack_subcommand_map` | moved-lazy | `hermes_cli.commands_platforms` |
| `subprocess` | import | `subprocess` |
| `telegram_bot_commands` | moved-lazy | `hermes_cli.commands_platforms` |
| `telegram_menu_commands` | moved-lazy | `hermes_cli.commands_platforms` |
| `telegram_menu_max_commands` | moved-lazy | `hermes_cli.commands_platforms` |
| `time` | import | `time` |

### `hermes_cli.config`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `_install_method_project_root` | restored-helper | `(已删除；现作为 stamp_install_method 的依赖项恢复)` |
| `normalize_route_base_url` | moved-lazy | `hermes_cli.route_identity` |
| `stamp_install_method` | restored-def | `(已删除；BASE body 已恢复)` |

### `hermes_cli.console_engine`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `shlex` | import | `shlex` |

### `hermes_cli.curses_ui`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Protocol` | import | `typing` |

### `hermes_cli.dashboard_auth.audit`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | import | `os` |

### `hermes_cli.dashboard_auth.middleware`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DashboardAuthProvider` | moved-lazy | `hermes_cli.dashboard_auth.base` |

### `hermes_cli.dingtalk_auth`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `logger` | moved-lazy | `hermes_cli.auth` |
| `logging` | import | `logging` |

### `hermes_cli.doctor`

| name | kind | new location |
|---|---|---|
| `FTS_STORAGE_VERSION` | moved-lazy | `hermes_state_common` |
| `OPENROUTER_MODELS_URL` | moved-lazy | `hermes_constants` |
| `Path` | import | `pathlib` |
| `STATE_DB_SIZE_WARN_BYTES` | moved-lazy | `hermes_cli.doctor_state` |
| `agent_browser_runnable` | moved-lazy | `hermes_constants` |
| `base_url_host_matches` | moved-lazy | `utils` |
| `check_certificates` | moved-lazy | `hermes_cli.doctor_platform` |
| `check_fail` | restored-def | `(deleted; BASE body restored)` |
| `check_macos_full_disk_access` | moved-lazy | `hermes_cli.doctor_platform` |
| `check_macos_tcc_anchor` | moved-lazy | `hermes_cli.doctor_platform` |
| `check_macos_tcc_grants` | moved-lazy | `hermes_cli.doctor_platform` |
| `check_ok` | restored-def | `(deleted; BASE body restored)` |
| `check_warn` | restored-def | `(deleted; BASE body restored)` |
| `collect_deprecated_config_keys` | moved-lazy | `hermes_cli.doctor_config` |
| `collect_deprecated_env_vars` | moved-lazy | `hermes_cli.doctor_config` |
| `collect_relay_plugin_cutover_findings` | moved-lazy | `hermes_cli.doctor_config` |
| `describe_vercel_auth` | moved-lazy | `hermes_cli.vercel_auth` |
| `detect_install_method` | moved-lazy | `hermes_cli.config` |
| `importlib` | import | `importlib.util` |
| `is_nix_install_method` | moved-lazy | `hermes_cli.config` |
| `managed_scope_check` | moved-lazy | `hermes_cli.doctor_config` |
| `recommended_update_command_for_method` | moved-lazy | `hermes_cli.config` |
| `report_deprecated_config_and_env` | moved-lazy | `hermes_cli.doctor_config` |
| `shutil` | import | `shutil` |
| `subprocess` | import | `subprocess` |

### `hermes_cli.doctor_live`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ELEVENLABS_VOICES_URL` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `FAL_MODELS_URL` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `FIRECRAWL_HEALTH_URL` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `GROQ_MODELS_URL` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `OPENAI_MODELS_URL` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `hermes_cli.focus_view`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `FOCUS_USAGE` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `effective_tool_progress_mode` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `hermes_cli.foreign_sessions`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `list_claude_sessions` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `list_codex_sessions` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `hermes_cli.gateway`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEFAULT_GATEWAY_RESTART_AFTER_TURN_TIMEOUT` | 懒加载移动项 | `gateway.restart` |
| `print_systemd_linger_guidance` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `hermes_cli.gitlock`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `is_ancestor_of_head` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `hermes_cli.heartbeat`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Dict` | 导入项 | `typing` |

### `hermes_cli.journey`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `cmd_journey` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
### `hermes_cli.kanban`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入 | `typing` |

### `hermes_cli.kanban_db`

| name | kind | new location |
|---|---|---|
| `DEFAULT_BUSY_TIMEOUT_MS` | moved-lazy | `hermes_cli.kanban_db_connect` |
| `DEFAULT_LOG_BACKUP_COUNT` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `DEFAULT_LOG_ROTATE_BYTES` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `DEFAULT_SPAWN_FAILURE_LIMIT` | restored-def | `(deleted; BASE body restored)` |
| `DERIVED_MAX_IN_PROGRESS_CEILING` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `DERIVED_MAX_IN_PROGRESS_FLOOR` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `KANBAN_TERMINAL_TIMEOUT_GRACE_SECONDS` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `KanbanDbCorruptError` | moved-lazy | `hermes_cli.kanban_db_connect` |
| `MEMORY_GUARD_MB_PER_WORKER` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `Mapping` | import | `typing` |
| `RepairResult` | moved-lazy | `hermes_cli.kanban_db_connect` |
| `add_notify_sub` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `advance_notify_cursor` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `check_respawn_guard` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `claim_unseen_events_for_sub` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `configured_max_in_progress` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `connect` | moved-lazy | `hermes_cli.kanban_db_connect` |
| `connect_closing` | moved-lazy | `hermes_cli.kanban_db_connect` |
| `count_notify_subs` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `count_running_tasks` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `count_running_tasks_other_boards` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `derive_default_max_in_progress` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `detect_crashed_workers` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `detect_stale_running` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `dispatch_once` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `enforce_max_runtime` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `field` | import | `dataclasses` |
| `has_spawnable_ready` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `has_spawnable_review` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `hashlib` | import | `hashlib` |
| `heartbeat_worker` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `list_notify_subs` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `parent_results` | restored-def | `(deleted; BASE body restored)` |
| `purge_stale_done_notify_subs` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `random` | import | `random` |
| `reap_worker_zombies` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `reconcile_orphaned_running` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `remove_notify_sub` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `repair_db` | moved-lazy | `hermes_cli.kanban_db_connect` |
| `resolve_max_in_progress` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `resolve_workspace` | moved-lazy | `hermes_cli.kanban_db_workspace` |
| `review_dispatch_enabled` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `rewind_notify_cursor` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `run_daemon` | moved-lazy | `hermes_cli.kanban_db_dispatch` |
| `set_branch_name` | moved-lazy | `hermes_cli.kanban_db_workspace` |
| `set_workspace_path` | moved-lazy | `hermes_cli.kanban_db_workspace` |
| `shutil` | import | `shutil` |
| `threading` | import | `threading` |
| `unseen_events_for_sub` | moved-lazy | `hermes_cli.kanban_db_notify` |
| `worker_log_rotation_config` | moved-lazy | `hermes_cli.kanban_db_dispatch` |

### `hermes_cli.kanban_decompose`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入模块 | `json` |
| `os` | 导入模块 | `os` |

### `hermes_cli.kanban_diagnostics`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DIAGNOSTIC_KINDS` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `hermes_cli.local_runtime.binaries`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `get_hermes_home` | 延迟移动 | `hermes_constants` |

### `hermes_cli.local_runtime.bootstrap`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `get_hermes_home` | 延迟移动 | `hermes_constants` |

### `hermes_cli.local_runtime.capabilities`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入模块 | `json` |
| `urllib` | 导入模块 | `urllib.request` |

### `hermes_cli.local_runtime.catalog`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `find_variant` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `re` | 导入模块 | `re` |
| `recommended_id` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `hermes_cli.local_runtime.hf_browse`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `field` | 导入模块 | `dataclasses` |

### `hermes_cli.main`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `hashlib` | 导入模块 | `hashlib` |
| `line_input` | 延迟移动 | `hermes_cli.cli_output` |
| `shlex` | 导入模块 | `shlex` |
| `stat` | 导入模块 | `stat` |
| `tempfile` | 导入模块 | `tempfile` |

### `hermes_cli.mcp_picker`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `color` | 延迟移动 | `hermes_cli.colors` |

### `hermes_cli.mcp_security`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `is_mcp_server_entry_suspicious` | restored-def | `(已删除；基础内容已恢复)` |

### `hermes_cli.middleware`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `API_EXECUTION_MIDDLEWARE` | restored-def | `(已删除；基础内容已恢复)` |
| `API_REQUEST_MIDDLEWARE` | restored-def | `(已删除；基础内容已恢复)` |
| `apply_api_request_middleware` | restored-def | `(已删除；基础内容已恢复)` |
| `run_api_execution_middleware` | restored-def | `(已删除；基础内容已恢复)` |

### `hermes_cli.moa_config`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `build_moa_turn_prompt` | restored-def | `(已删除；基础内容已恢复)` |
| `encode_moa_turn` | restored-helper | `(已删除；作为 build_moa_turn_prompt 的依赖项被恢复)` |
| `encode_moa_turn` | restored-def | `(已删除；基础内容已恢复)` |
| `list_moa_presets` | restored-def | `(已删除；基础内容已恢复)` |
| `set_active_moa_preset` | restored-def | `(已删除；基础内容已恢复)` |

### `hermes_cli.model_setup_flows`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BEDROCK_GEO_PREFIXES` | 已延迟移动 | `hermes_cli.model_setup_flows_bedrock` |
| `bedrock_model_routable_from_region` | 已延迟移动 | `hermes_cli.model_setup_flows_bedrock` |
| `bedrock_region_geo_prefix` | 已延迟移动 | `hermes_cli.model_setup_flows_bedrock` |
| `custom_provider_slug` | 已延迟移动 | `hermes_cli.providers` |
| `line_input` | 已延迟移动 | `hermes_cli.cli_output` |
| `subprocess` | 导入项 | `subprocess` |
| `urllib` | 导入项 | `urllib.parse` |

### `hermes_cli.model_switch`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `List` | 导入项 | `typing` |
| `base_url_host_matches` | 已延迟移动 | `utils` |
| `custom_provider_slug` | 已延迟移动 | `hermes_cli.providers` |
| `http` | 导入项 | `http.client` |
| `list_picker_providers` | 已延迟移动 | `hermes_cli.model_switch_providers` |
| `prewarm_picker_cache_async` | 已延迟移动 | `hermes_cli.model_switch_providers` |
| `time` | 导入项 | `time` |

### `hermes_cli.models`

| name | kind | new location |
|---|---|---|
| `LMStudioLoadResult` | moved-lazy | `hermes_cli.models_local` |
| `NamedTuple` | import | `typing` |
| `PROVIDER_GROUPS` | moved-lazy | `hermes_cli.models_catalog_static` |
| `ProviderEntry` | moved-lazy | `hermes_cli.models_catalog_static` |
| `_OPENCODE_KEYLESS_EXTRA_SLUGS` | restored-helper | `(deleted; restored as a dependency of is_opencode_zen_free_model)` |
| `atomic_json_write` | moved-lazy | `utils` |
| `base_url_host_matches` | moved-lazy | `utils` |
| `compute_sale_discount` | moved-lazy | `hermes_cli.models_pricing` |
| `ensure_lmstudio_model_loaded` | moved-lazy | `hermes_cli.models_local` |
| `fetch_ai_gateway_pricing` | moved-lazy | `hermes_cli.models_pricing` |
| `fetch_lmstudio_models` | moved-lazy | `hermes_cli.models_local` |
| `fetch_models_with_pricing` | moved-lazy | `hermes_cli.models_pricing` |
| `fetch_ollama_local_models` | moved-lazy | `hermes_cli.models_local` |
| `get_cached_nous_inference_base_url` | moved-lazy | `hermes_cli.models_pricing` |
| `get_close_matches` | import | `difflib` |
| `get_pricing_for_provider` | moved-lazy | `hermes_cli.models_pricing` |
| `group_providers` | moved-lazy | `hermes_cli.models_catalog_static` |
| `http` | import | `http.client` |
| `is_nous_free_tier` | restored-def | `(deleted; BASE body restored)` |
| `is_opencode_zen_free_model` | restored-def | `(deleted; BASE body restored)` |
| `lmstudio_model_reasoning_options` | moved-lazy | `hermes_cli.models_local` |
| `nous_catalog_url` | moved-lazy | `hermes_cli.models_reasoning_caps` |
| `nous_model_reasoning_capabilities` | moved-lazy | `hermes_cli.models_reasoning_caps` |
| `nous_policy_allowed_ids` | moved-lazy | `hermes_cli.models_pricing` |
| `ollama_model_supports_thinking` | moved-lazy | `hermes_cli.models_local` |
| `openrouter_model_reasoning_capabilities` | moved-lazy | `hermes_cli.models_reasoning_caps` |
| `parse_openrouter_reasoning_capabilities` | moved-lazy | `hermes_cli.models_reasoning_caps` |
| `peek_cached_pricing` | moved-lazy | `hermes_cli.models_pricing` |
| `pricing_cache_scope` | moved-lazy | `hermes_cli.models_pricing` |
| `probe_lmstudio_models` | moved-lazy | `hermes_cli.models_local` |
| `probe_ollama_local_models` | moved-lazy | `hermes_cli.models_local` |
| `provider_group_for_slug` | moved-lazy | `hermes_cli.models_catalog_static` |
| `refresh_reasoning_caps_async` | moved-lazy | `hermes_cli.models_reasoning_caps` |
| `restrict_to_nous_policy` | moved-lazy | `hermes_cli.models_pricing` |
| `should_use_ollama_native_catalog` | moved-lazy | `hermes_cli.models_local` |
| `url_origin` | moved-lazy | `hermes_cli.urllib_security` |
| `validate_requested_model` | moved-lazy | `hermes_cli.models_validate` |
| `warm_nous_reasoning_caps_async` | moved-lazy | `hermes_cli.models_reasoning_caps` |
| `warm_openrouter_reasoning_caps_async` | moved-lazy | `hermes_cli.models_reasoning_caps` |

### `hermes_cli.nous_billing`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BILLING_MANAGE_SCOPE` | 已恢复的被删除项 | `(已删除；BASE 结构已恢复)` |

### `hermes_cli.nous_subscription`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `managed_nous_tools_enabled` | 延迟移动项 | `tools.tool_backend_helpers` |

### `hermes_cli.observability.relay_runtime`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `*` | 模块占位符 | `agent.relay_runtime` |

### `hermes_cli.observability.relay_shared_metrics`

| name | kind | new location |
|---|---|---|
| `CLIENT_ACTIVE_MARK` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `MODEL_CALL_PROFILE_MODEL` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `SCHEMA_KEY` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `SCHEMA_VERSION` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `SKILL_LIFECYCLE_MARK` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `SKILL_LOAD_MARK` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `TOOL_APPROVAL_MARK` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `TOOL_CALL_SCOPE` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `model_call_fields` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `prepare_session_start` | restored-def | `(deleted; BASE body restored)` |
| `skill_lifecycle_fields` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `skill_load_fields` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `task_start_fields` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `task_terminal_fields` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `task_terminal_state` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `tool_approval_outcome` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `tool_category` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |
| `tool_terminal_fields` | moved-lazy | `hermes_cli.observability.shared_metrics_contract` |

### `hermes_cli.onepassword_secrets_cli`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Table` | 导入模块 | `rich.table` |
| `masked_secret_prompt` | 已延迟移动 | `hermes_cli.secret_prompt` |
| `sys` | 导入模块 | `sys` |

### `hermes_cli.platform_actions`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | 导入模块 | `typing` |

### `hermes_cli.plugins`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CAPABILITY_REGISTRY` | 暂缓移动 | `hermes_cli.plugin_capabilities` |
| `ENTRY_POINT_CAPABILITIES_GROUP` | 暂缓移动 | `hermes_cli.plugins_discovery` |
| `Iterable` | 导入项 | `typing` |
| `LEGACY_RELAY_PLUGIN_KEYS` | 暂缓移动 | `hermes_cli.relay_plugin_cutover` |
| `MAX_SYSTEM_PROMPT_SECTIONS` | 暂缓移动 | `hermes_cli.plugins_dispatch` |
| `OBSERVER_SCHEMA_VERSION` | 暂缓移动 | `hermes_cli.middleware` |
| `Type` | 导入项 | `typing` |
| `VALID_CAPABILITY_IDS` | 暂缓移动 | `hermes_cli.plugin_capabilities` |
| `cfg_get` | 暂缓移动 | `hermes_cli.config` |
| `contextmanager` | 导入项 | `contextlib` |
| `contextvars` | 导入项 | `contextvars` |
| `copy` | 导入项 | `copy` |
| `fast_safe_load` | 暂缓移动 | `utils` |
| `format_system_prompt_section` | 暂缓移动 | `hermes_cli.plugins_dispatch` |
| `get_plugin_subscriptions` | 已恢复（原为删除） | `(已删除；基础内容已恢复)` |
| `hashlib` | 导入项 | `hashlib` |
| `reset_hermes_home_override` | 暂缓移动 | `hermes_constants` |
| `set_hermes_home_override` | 暂缓移动 | `hermes_constants` |
| `time` | 导入项 | `time` |
| `unload_plugins` | 已恢复（原为删除） | `(已删除；基础内容已恢复)` |
| `wraps` | 导入项 | `functools` |
| `yaml` | 无法恢复 | `BASE文件中不存在顶层定义` |

### `hermes_cli.plugins_cmd`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `importlib` | 导入项 | `importlib.metadata` |

### `hermes_cli.profile_describer`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入项 | `json` |

### `hermes_cli.profile_distribution`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `is_excluded_skill_path` | 晚期移动项 | `agent.skill_utils` |

### `hermes_cli.profiles`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `has_bundled_skills_opt_out` | 已恢复的删除项 | `(已删除；恢复为原始内容)` |

### `hermes_cli.runtime_provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `custom_provider_aliases` | 晚期移动项 | `hermes_cli.providers` |
| `custom_provider_slug` | 晚期移动项 | `hermes_cli.providers` |
| `os` | 导入项 | `os` |

### `hermes_cli.security_advisories`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `render_doctor_section` | 已恢复的删除项 | `(已删除；恢复为原始内容)` |

### `hermes_cli.setup`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入项 | `typing` |
| `Dict` | 导入项 | `typing` |
| `Optional` | 导入项 | `typing` |
| `get_nous_subscription_features` | 晚期移动项 | `hermes_cli.nous_subscription` |
| `get_optional_skills_dir` | 晚期移动项 | `hermes_constants` |
| `json` | 导入项 | `json` |
| `managed_nous_tools_enabled` | 晚期移动项 | `tools.tool_backend_helpers` |
| `shutil` | 导入项 | `shutil` |

### `hermes_cli.slack_cli`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | 导入项 | `os` |

### `hermes_cli.sqlite_safe_read`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `SQLITE_HEADER_MAGIC` | 已恢复的删除项 | `(已删除；恢复为原始内容)` |

### `hermes_cli.status`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `format_nous_portal_entitlement_message` | 已延迟移动 | `hermes_cli.nous_account` |
| `get_nous_portal_account_info` | 已延迟移动 | `hermes_cli.nous_account` |
| `get_nous_subscription_features` | 已延迟移动 | `hermes_cli.nous_subscription` |
| `managed_nous_tools_enabled` | 已延迟移动 | `tools.tool_backend_helpers` |
| `redact_key` | 已延迟移动 | `hermes_cli.config` |
| `subprocess` | 已导入 | `subprocess` |

### `hermes_cli.telegram_managed_bot`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEFAULT_MANAGER_BOT` | restored-def | `(已删除；基础内容已恢复)` |
| `_USERNAME_SLUG_ALPHABET` | restored-helper | `(已删除；作为 generate_bot_username 的依赖项已恢复)` |
| `auto_setup_telegram_bot` | restored-def | `(已删除；基础内容已恢复)` |
| `generate_bot_username` | restored-def | `(已删除；基础内容已恢复)` |
| `generate_deep_link` | restored-def | `(已删除；基础内容已恢复)` |
| `generate_pairing_nonce` | restored-def | `(已删除；基础内容已恢复)` |
| `generate_username_slug` | restored-helper | `(已删除；作为 generate_bot_username 的依赖项已恢复)` |
| `generate_username_slug` | restored-def | `(已删除；基础内容已恢复)` |
| `poll_for_token` | restored-def | `(已删除；基础内容已恢复)` |
| `poll_pairing_once` | restored-def | `(已删除；基础内容已恢复)` |
| `secrets` | restored-import | `secrets` |
| `secrets` | import | `secrets` |
| `urllib` | restored-import | `urllib.parse` |
| `urllib` | import | `urllib.parse` |

### `hermes_cli.tools_config`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `MANAGED_FEATURE_COVERAGE_CATEGORY` | 暂缓移动 | `hermes_cli.nous_subscription` |
| `NOUS_MANAGED_PROVIDER` | 暂缓移动 | `tools.tool_backend_helpers` |
| `base_url_hostname` | 暂缓移动 | `utils` |
| `fal_key_is_configured` | 暂缓移动 | `tools.tool_backend_helpers` |
| `format_nous_portal_entitlement_message` | 暂缓移动 | `hermes_cli.nous_account` |
| `is_truthy_value` | 暂缓移动 | `utils` |
| `save_env_value` | 暂缓移动 | `hermes_cli.config` |
| `shutil` | 导入项 | `shutil` |
| `subprocess` | 导入项 | `subprocess` |
| `sys` | 导入项 | `sys` |

### `hermes_cli.uninstall`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `find_shell_configs` | 已恢复的删除项 | `(已删除；原始内容已恢复)` |

### `hermes_cli.update_cmd`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | 导入项 | `typing` |
| `datetime` | 导入项 | `datetime` |
| `hashlib` | 导入项 | `hashlib` |
| `json` | 导入项 | `json` |

### `hermes_cli.update_inventory`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Path` | 导入项 | `pathlib` |
| `os` | 导入项 | `os` |

### `hermes_cli.web_deps`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `get_dashboard_health` | 已恢复的删除项 | `(已删除；原始内容已恢复)` |
| `get_session_token` | 已恢复的删除项 | `(已删除；原始内容已恢复)` |
| `has_valid_session_token` | 已恢复的删除项 | `(已删除；原始内容已恢复)` |
| `late_attr` | 已恢复的删除项 | `(已删除；原始内容已恢复)` |

### `hermes_cli.web_routers.cron`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `logging` | 导入项 | `logging` |

### `hermes_cli.web_routers.mcp`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `logging` | 导入项 | `logging` |

### `hermes_cli.web_routers.sessions`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入项 | `typing` |
| `Dict` | 导入项 | `typing` |
| `logging` | 导入项 | `logging` |

### `hermes_cli.web_routers.skills`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `LateState` | 延迟移动 | `hermes_cli.web_deps` |
| `logging` | 导入项 | `logging` |

### `hermes_cli.web_routers.tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `LateState` | 延迟移动 | `hermes_cli.web_deps` |
| `logging` | 导入项 | `logging` |

### `hermes_cli.web_server`

| name | kind | new location |
|---|---|---|
| `AudioTranscriptionRequest` | moved-lazy | `hermes_cli.web_models` |
| `AutomationBlueprintInstantiate` | moved-lazy | `hermes_cli.web_models` |
| `BackupRequest` | moved-lazy | `hermes_cli.web_models` |
| `BaseModel` | unrestorable | `no top-level definition on BASE` |
| `BulkDeleteSessions` | moved-lazy | `hermes_cli.web_models` |
| `CONFIG_SCHEMA` | moved-lazy | `hermes_cli.web_server_config` |
| `ChatImageUpload` | moved-lazy | `hermes_cli.web_models` |
| `ConfigUpdate` | moved-lazy | `hermes_cli.web_models` |
| `CredentialPoolAdd` | moved-lazy | `hermes_cli.web_models` |
| `CronJobCreate` | moved-lazy | `hermes_cli.web_models` |
| `CronJobUpdate` | moved-lazy | `hermes_cli.web_models` |
| `CuratorPause` | moved-lazy | `hermes_cli.web_models` |
| `CustomEndpointUpdate` | moved-lazy | `hermes_cli.web_models` |
| `DEFAULT_CONFIG` | moved-lazy | `hermes_cli.config` |
| `DebugShareRequest` | moved-lazy | `hermes_cli.web_models` |
| `EnvVarDelete` | moved-lazy | `hermes_cli.web_models` |
| `EnvVarReveal` | moved-lazy | `hermes_cli.web_models` |
| `EnvVarUpdate` | moved-lazy | `hermes_cli.web_models` |
| `File` | unrestorable | `no top-level definition on BASE` |
| `FileResponse` | unrestorable | `no top-level definition on BASE` |
| `FontSetBody` | moved-lazy | `hermes_cli.web_models` |
| `Form` | unrestorable | `no top-level definition on BASE` |
| `FsWriteText` | moved-lazy | `hermes_cli.web_models` |
| `GitBranchSwitchBody` | moved-lazy | `hermes_cli.web_models` |
| `GitCommitBody` | moved-lazy | `hermes_cli.web_models` |
| `GitFileBody` | moved-lazy | `hermes_cli.web_models` |
| `GitPathBody` | moved-lazy | `hermes_cli.web_models` |
| `GitWorktreeAddBody` | moved-lazy | `hermes_cli.web_models` |
| `GitWorktreeRemoveBody` | moved-lazy | `hermes_cli.web_models` |
| `HTMLResponse` | unrestorable | `no top-level definition on BASE` |
| `HookCreate` | moved-lazy | `hermes_cli.web_models` |
| `HookDelete` | moved-lazy | `hermes_cli.web_models` |
| `ImportRequest` | moved-lazy | `hermes_cli.web_models` |
| `LearningNodeEdit` | moved-lazy | `hermes_cli.web_models` |
| `LearningNodeRef` | moved-lazy | `hermes_cli.web_models` |
| `List` | import | `typing` |
| `Literal` | import | `typing` |
| `MCPCatalogInstall` | moved-lazy | `hermes_cli.web_models` |
| `MCPEnabledToggle` | moved-lazy | `hermes_cli.web_models` |
| `MCPServerCreate` | moved-lazy | `hermes_cli.web_models` |
| `MCPServersReplace` | moved-lazy | `hermes_cli.web_models` |
| `ManagedDirectoryCreate` | moved-lazy | `hermes_cli.web_models` |
| `ManagedFileDelete` | moved-lazy | `hermes_cli.web_models` |
| `ManagedFileUpload` | moved-lazy | `hermes_cli.web_models` |
| `ManagedFilesPolicy` | moved-lazy | `hermes_cli.web_server_files` |
| `MemoryProviderConfigUpdate` | moved-lazy | `hermes_cli.web_models` |
| `MemoryProviderSelect` | moved-lazy | `hermes_cli.web_models` |
| `MemoryProviderSetupRequest` | moved-lazy | `hermes_cli.web_models` |
| `MemoryReset` | moved-lazy | `hermes_cli.web_models` |
| `MessagingPlatformUpdate` | moved-lazy | `hermes_cli.web_models` |
| `MoaConfigPayload` | moved-lazy | `hermes_cli.web_models` |
| `MoaModelSlot` | moved-lazy | `hermes_cli.web_models` |
| `MoaPresetPayload` | moved-lazy | `hermes_cli.web_models` |
| `ModelAssignment` | moved-lazy | `hermes_cli.web_models` |
| `OAuthSubmitBody` | moved-lazy | `hermes_cli.web_models` |
| `OPTIONAL_ENV_VARS` | moved-lazy | `hermes_cli.config` |
| `PairingApprove` | moved-lazy | `hermes_cli.web_models` |
| `PairingRevoke` | moved-lazy | `hermes_cli.web_models` |
| `ProfileActiveUpdate` | moved-lazy | `hermes_cli.web_models` |
| `ProfileCreate` | moved-lazy | `hermes_cli.web_models` |
| `ProfileDescribeAuto` | moved-lazy | `hermes_cli.web_models` |
| `ProfileDescriptionUpdate` | moved-lazy | `hermes_cli.web_models` |
| `ProfileModelUpdate` | moved-lazy | `hermes_cli.web_models` |
| `ProfileRename` | moved-lazy | `hermes_cli.web_models` |
| `ProfileSoulUpdate` | moved-lazy | `hermes_cli.web_models` |
| `ProviderConfigSchema` | moved-lazy | `plugins.memory.config_schema` |
| `ProviderField` | moved-lazy | `plugins.memory.config_schema` |
| `PtyBridge` | moved-lazy | `hermes_cli.pty_bridge` |
| `PtySessionRegistry` | moved-lazy | `hermes_cli.pty_session` |
| `PtyUnavailableError` | moved-lazy | `hermes_cli.pty_bridge` |
| `Query` | unrestorable | `no top-level definition on BASE` |
| `RawConfigUpdate` | moved-lazy | `hermes_cli.web_models` |
| `RegistryFull` | moved-lazy | `hermes_cli.pty_session` |
| `Response` | unrestorable | `no top-level definition on BASE` |
| `STORAGE_HONCHO_HOST_BLOCK` | moved-lazy | `plugins.memory.config_schema` |
| `SecretStr` | unrestorable | `no top-level definition on BASE` |
| `SessionImport` | moved-lazy | `hermes_cli.web_models` |
| `SessionPrune` | moved-lazy | `hermes_cli.web_models` |
| `SessionRename` | moved-lazy | `hermes_cli.web_models` |
| `SkillContentUpdate` | moved-lazy | `hermes_cli.web_models` |
| `SkillCreate` | moved-lazy | `hermes_cli.web_models` |
| `SkillInstallRequest` | moved-lazy | `hermes_cli.web_models` |
| `SkillToggle` | moved-lazy | `hermes_cli.web_models` |
| `SkillUninstallRequest` | moved-lazy | `hermes_cli.web_models` |
| `SkillsUpdateRequest` | moved-lazy | `hermes_cli.web_models` |
| `StaticFiles` | unrestorable | `no top-level definition on BASE` |
| `TTSLeaseRequest` | moved-lazy | `hermes_cli.web_models` |
| `TTSSpeakRequest` | moved-lazy | `hermes_cli.web_models` |
| `TelegramOnboardingApply` | moved-lazy | `hermes_cli.web_models` |
| `TelegramOnboardingStart` | moved-lazy | `hermes_cli.web_models` |
| `TerminalBackendSelect` | moved-lazy | `hermes_cli.web_models` |
| `ThemeSetBody` | moved-lazy | `hermes_cli.web_models` |
| `ToolsetEnvUpdate` | moved-lazy | `hermes_cli.web_models` |
| `ToolsetModelSelect` | moved-lazy | `hermes_cli.web_models` |
| `ToolsetPostSetup` | moved-lazy | `hermes_cli.web_models` |
| `ToolsetProviderSelect` | moved-lazy | `hermes_cli.web_models` |
| `ToolsetToggle` | moved-lazy | `hermes_cli.web_models` |
| `UploadFile` | unrestorable | `no top-level definition on BASE` |
| `WebSocket` | unrestorable | `no top-level definition on BASE` |
| `WebSocketDisconnect` | unrestorable | `no top-level definition on BASE` |
| `WebhookCreate` | moved-lazy | `hermes_cli.web_models` |
| `WebhookEnabledToggle` | moved-lazy | `hermes_cli.web_models` |
| `WhatsAppOnboardingApply` | moved-lazy | `hermes_cli.web_models` |
| `WhatsAppOnboardingStart` | moved-lazy | `hermes_cli.web_models` |
| `activate_custom_endpoint` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `add_credential_pool_entry` | moved-lazy | `hermes_cli.web_routers.ops` |
| `add_mcp_server` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `apply_telegram_onboarding` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `apply_whatsapp_onboarding` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `approve_pairing` | moved-lazy | `hermes_cli.web_routers.ops` |
| `atexit` | import | `atexit` |
| `auth_mcp_server` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `base64` | import | `base64` |
| `binascii` | import | `binascii` |
| `build_cron_model_impact` | moved-lazy | `hermes_cli.config` |
| `bulk_delete_sessions_endpoint` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `cancel_oauth_session` | moved-lazy | `hermes_cli.web_routers.oauth` |
| `cancel_telegram_onboarding` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `cancel_whatsapp_onboarding` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `cfg_get` | moved-lazy | `hermes_cli.config` |
| `check_config_version` | moved-lazy | `hermes_cli.config` |
| `check_hermes_update` | moved-lazy | `hermes_cli.web_routers.actions` |
| `clear_model_endpoint_credentials` | moved-lazy | `hermes_cli.config` |
| `clear_pending_pairing` | moved-lazy | `hermes_cli.web_routers.ops` |
| `coerce_provider_id` | moved-lazy | `hermes_cli.config` |
| `concurrent` | import | `concurrent.futures` |
| `console_ws` | moved-lazy | `hermes_cli.web_routers.chat_ws` |
| `contextlib` | import | `contextlib` |
| `contextmanager` | import | `contextlib` |
| `count_empty_sessions_endpoint` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `create_cron_job` | moved-lazy | `hermes_cli.web_routers.cron` |
| `create_hook` | moved-lazy | `hermes_cli.web_routers.ops` |
| `create_managed_directory` | moved-lazy | `hermes_cli.web_routers.files` |
| `create_profile_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `create_skill` | moved-lazy | `hermes_cli.web_routers.skills` |
| `create_webhook` | moved-lazy | `hermes_cli.web_routers.ops` |
| `cron_fire_webhook` | moved-lazy | `hermes_cli.web_routers.cron` |
| `custom_endpoint_key_env` | moved-lazy | `hermes_cli.config` |
| `dataclass` | import | `dataclasses` |
| `datetime` | import | `datetime` |
| `delete_agent_plugin` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `delete_cron_job` | moved-lazy | `hermes_cli.web_routers.cron` |
| `delete_custom_endpoint` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `delete_empty_sessions_endpoint` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `delete_hook` | moved-lazy | `hermes_cli.web_routers.ops` |
| `delete_learning_node` | moved-lazy | `hermes_cli.web_routers.status` |
| `delete_managed_file` | moved-lazy | `hermes_cli.web_routers.files` |
| `delete_profile_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `delete_session_endpoint` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `delete_webhook` | moved-lazy | `hermes_cli.web_routers.ops` |
| `derive_gateway_busy` | moved-lazy | `gateway.status` |
| `derive_gateway_drainable` | moved-lazy | `gateway.status` |
| `describe_profile_auto_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `detect_install_method` | moved-lazy | `hermes_cli.config` |
| `disconnect_oauth_provider` | moved-lazy | `hermes_cli.web_routers.oauth` |
| `download_dashboard_backup` | moved-lazy | `hermes_cli.web_routers.ops` |
| `download_managed_file` | moved-lazy | `hermes_cli.web_routers.files` |
| `enable_webhooks` | moved-lazy | `hermes_cli.web_routers.ops` |
| `env_var_enabled` | moved-lazy | `utils` |
| `events_ws` | moved-lazy | `hermes_cli.web_routers.chat_ws` |
| `export_session_endpoint` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `field_validator` | unrestorable | `no top-level definition on BASE` |
| `find_provider_entry` | moved-lazy | `hermes_cli.config` |
| `format_docker_update_message` | moved-lazy | `hermes_cli.config` |
| `fs_default_cwd` | moved-lazy | `hermes_cli.web_routers.files` |
| `fs_download` | moved-lazy | `hermes_cli.web_routers.files` |
| `fs_git_root` | moved-lazy | `hermes_cli.web_routers.files` |
| `fs_list` | moved-lazy | `hermes_cli.web_routers.files` |
| `fs_read_data_url` | moved-lazy | `hermes_cli.web_routers.files` |
| `fs_read_text` | moved-lazy | `hermes_cli.web_routers.files` |
| `fs_write_text` | moved-lazy | `hermes_cli.web_routers.files` |
| `functools` | import | `functools` |
| `gateway_drain` | moved-lazy | `hermes_cli.web_routers.actions` |
| `gateway_ws` | moved-lazy | `hermes_cli.web_routers.chat_ws` |
| `get_action_status` | moved-lazy | `hermes_cli.web_routers.actions` |
| `get_active_profile_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `get_auxiliary_models` | moved-lazy | `hermes_cli.web_routers.models` |
| `get_client_voice_config` | moved-lazy | `hermes_cli.web_routers.audio` |
| `get_computer_use_status` | moved-lazy | `hermes_cli.web_routers.tools` |
| `get_config` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `get_config_path` | moved-lazy | `hermes_cli.config` |
| `get_config_raw` | moved-lazy | `hermes_cli.web_routers.analytics` |
| `get_cron_delivery_targets` | moved-lazy | `hermes_cli.web_routers.cron` |
| `get_cron_job` | moved-lazy | `hermes_cli.web_routers.cron` |
| `get_curator_status` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_dashboard_font` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `get_dashboard_plugins` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `get_dashboard_themes` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `get_defaults` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `get_egress_status` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `get_elevenlabs_voices` | moved-lazy | `hermes_cli.web_routers.audio` |
| `get_env_path` | moved-lazy | `hermes_cli.config` |
| `get_env_vars` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `get_health` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_hermes_home` | moved-lazy | `hermes_cli.config` |
| `get_learning_graph` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_learning_node` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_logs` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_media` | moved-lazy | `hermes_cli.web_routers.files` |
| `get_memory_provider_config` | moved-lazy | `hermes_cli.web_routers.memory_providers` |
| `get_memory_status` | moved-lazy | `hermes_cli.web_routers.ops` |
| `get_messaging_platforms` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `get_moa_models` | moved-lazy | `hermes_cli.web_routers.models` |
| `get_model_info` | moved-lazy | `hermes_cli.web_routers.models` |
| `get_model_options` | moved-lazy | `hermes_cli.web_routers.models` |
| `get_models_analytics` | moved-lazy | `hermes_cli.web_routers.analytics` |
| `get_plugins_hub` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `get_portal_status` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_process_hermes_home` | moved-lazy | `hermes_cli.config` |
| `get_profile_setup_command` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `get_profile_soul` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `get_profiles_sessions` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `get_profiles_sessions_sidebar` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `get_provider_config_schema` | moved-lazy | `plugins.memory.config_schema` |
| `get_recommended_default_model` | moved-lazy | `hermes_cli.web_routers.models` |
| `get_running_pid` | moved-lazy | `gateway.status` |
| `get_running_pid_cached` | moved-lazy | `gateway.status` |
| `get_runtime_status_running_pid` | moved-lazy | `gateway.status` |
| `get_schema` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `get_session_detail` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `get_session_latest_descendant` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `get_session_messages` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `get_session_stats` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `get_sessions` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `get_skill_content` | moved-lazy | `hermes_cli.web_routers.skills` |
| `get_skills` | moved-lazy | `hermes_cli.web_routers.skills` |
| `get_ssh_ownership` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_status` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_system_stats` | moved-lazy | `hermes_cli.web_routers.status` |
| `get_telegram_onboarding_status` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `get_terminal_backends` | moved-lazy | `hermes_cli.web_routers.tools` |
| `get_toolset_config` | moved-lazy | `hermes_cli.web_routers.tools` |
| `get_toolset_models` | moved-lazy | `hermes_cli.web_routers.tools` |
| `get_toolsets` | moved-lazy | `hermes_cli.web_routers.tools` |
| `get_update_receipt` | moved-lazy | `hermes_cli.web_routers.actions` |
| `get_usage_analytics` | moved-lazy | `hermes_cli.web_routers.analytics` |
| `get_whatsapp_onboarding_status` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `git_base_branches_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_branch_switch_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_branches_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_commit_context_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_commit_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_create_pr_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_file_diff_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_push_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_rev_parse_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_revert_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_review_diff_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_review_list_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_ship_info_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_stage_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_status_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_unstage_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_worktree_add_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_worktree_remove_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `git_worktrees_route` | moved-lazy | `hermes_cli.web_routers.git` |
| `grant_computer_use_permissions` | moved-lazy | `hermes_cli.web_routers.tools` |
| `hashlib` | import | `hashlib` |
| `import_sessions_endpoint` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `importlib` | import | `importlib.util` |
| `inspect` | import | `inspect` |
| `install_mcp_catalog_entry` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `install_skill_hub` | moved-lazy | `hermes_cli.web_routers.skills` |
| `instantiate_blueprint` | moved-lazy | `hermes_cli.web_routers.cron` |
| `ipaddress` | import | `ipaddress` |
| `is_nix_install_method` | moved-lazy | `hermes_cli.config` |
| `json` | import | `json` |
| `list_checkpoints` | moved-lazy | `hermes_cli.web_routers.ops` |
| `list_credential_pool` | moved-lazy | `hermes_cli.web_routers.ops` |
| `list_cron_blueprints` | moved-lazy | `hermes_cli.web_routers.cron` |
| `list_cron_job_runs` | moved-lazy | `hermes_cli.web_routers.cron` |
| `list_cron_jobs` | moved-lazy | `hermes_cli.web_routers.cron` |
| `list_custom_endpoints` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `list_hooks` | moved-lazy | `hermes_cli.web_routers.ops` |
| `list_managed_files` | moved-lazy | `hermes_cli.web_routers.files` |
| `list_mcp_catalog` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `list_mcp_servers` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `list_oauth_providers` | moved-lazy | `hermes_cli.web_routers.oauth` |
| `list_pairing` | moved-lazy | `hermes_cli.web_routers.ops` |
| `list_profiles_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `list_skills_hub_sources` | moved-lazy | `hermes_cli.web_routers.skills` |
| `list_webhooks` | moved-lazy | `hermes_cli.web_routers.ops` |
| `load_env` | moved-lazy | `hermes_cli.config` |
| `math` | import | `math` |
| `mcp_oauth_callback` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `mcp_oauth_flow_status` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `mimetypes` | import | `mimetypes` |
| `normalize_updated_at` | moved-lazy | `gateway.status` |
| `open_profile_terminal_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `parse_active_agents` | moved-lazy | `gateway.status` |
| `pause_cron_job` | moved-lazy | `hermes_cli.web_routers.cron` |
| `poll_oauth_session` | moved-lazy | `hermes_cli.web_routers.oauth` |
| `post_agent_plugin_disable` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `post_agent_plugin_enable` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `post_agent_plugin_install` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `post_agent_plugin_update` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `post_plugin_visibility` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `preview_skill_hub` | moved-lazy | `hermes_cli.web_routers.skills` |
| `prune_checkpoints` | moved-lazy | `hermes_cli.web_routers.ops` |
| `prune_sessions_endpoint` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `pty_ws` | moved-lazy | `hermes_cli.web_routers.chat_ws` |
| `pub_ws` | moved-lazy | `hermes_cli.web_routers.chat_ws` |
| `put_plugin_providers` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `queue` | import | `queue` |
| `read_managed_file` | moved-lazy | `hermes_cli.web_routers.files` |
| `read_raw_config` | moved-lazy | `hermes_cli.config` |
| `read_runtime_status` | moved-lazy | `gateway.status` |
| `recommended_update_command_for_method` | moved-lazy | `hermes_cli.config` |
| `redact_key` | moved-lazy | `hermes_cli.config` |
| `remove_credential_pool_entry` | moved-lazy | `hermes_cli.web_routers.ops` |
| `remove_env_value` | moved-lazy | `hermes_cli.config` |
| `remove_env_var` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `remove_mcp_server` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `rename_profile_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `rename_session_endpoint` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `replace_mcp_servers` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `rescan_dashboard_plugins` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `reset_memory` | moved-lazy | `hermes_cli.web_routers.ops` |
| `resolve_cron_model_drift_defaults` | moved-lazy | `hermes_cli.config` |
| `resolve_gateway_liveness` | moved-lazy | `gateway.status` |
| `restart_gateway` | moved-lazy | `hermes_cli.web_routers.actions` |
| `resume_cron_job` | moved-lazy | `hermes_cli.web_routers.cron` |
| `reveal_env_var` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `revoke_pairing` | moved-lazy | `hermes_cli.web_routers.ops` |
| `run_backup` | moved-lazy | `hermes_cli.web_routers.ops` |
| `run_config_migrate` | moved-lazy | `hermes_cli.web_routers.status` |
| `run_curator` | moved-lazy | `hermes_cli.web_routers.status` |
| `run_debug_share_endpoint` | moved-lazy | `hermes_cli.web_routers.status` |
| `run_doctor` | moved-lazy | `hermes_cli.doctor` |
| `run_dump` | moved-lazy | `hermes_cli.dump` |
| `run_import` | moved-lazy | `hermes_cli.web_routers.ops` |
| `run_import_upload` | moved-lazy | `hermes_cli.web_routers.ops` |
| `run_in_threadpool` | unrestorable | `no top-level definition on BASE` |
| `run_prompt_size` | moved-lazy | `hermes_cli.web_routers.status` |
| `run_security_audit` | moved-lazy | `hermes_cli.web_routers.ops` |
| `run_toolset_post_setup` | moved-lazy | `hermes_cli.web_routers.tools` |
| `save_config` | moved-lazy | `hermes_cli.config` |
| `save_env_value` | moved-lazy | `hermes_cli.config` |
| `save_toolset_env` | moved-lazy | `hermes_cli.web_routers.tools` |
| `scan_skill_hub` | moved-lazy | `hermes_cli.web_routers.skills` |
| `search_sessions` | moved-lazy | `hermes_cli.web_routers.sessions` |
| `search_skills_hub` | moved-lazy | `hermes_cli.web_routers.skills` |
| `select_terminal_backend` | moved-lazy | `hermes_cli.web_routers.tools` |
| `select_toolset_model` | moved-lazy | `hermes_cli.web_routers.tools` |
| `select_toolset_provider` | moved-lazy | `hermes_cli.web_routers.tools` |
| `serve_plugin_asset` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `set_active_profile_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `set_curator_paused` | moved-lazy | `hermes_cli.web_routers.status` |
| `set_dashboard_font` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `set_dashboard_theme` | moved-lazy | `hermes_cli.web_routers.dashboard_ui` |
| `set_env_var` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `set_mcp_server_enabled` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `set_memory_provider` | moved-lazy | `hermes_cli.web_routers.ops` |
| `set_moa_models` | moved-lazy | `hermes_cli.web_routers.models` |
| `set_model_assignment` | moved-lazy | `hermes_cli.web_routers.models` |
| `set_webhook_enabled` | moved-lazy | `hermes_cli.web_routers.ops` |
| `setup_memory_provider` | moved-lazy | `hermes_cli.web_routers.memory_providers` |
| `shlex` | import | `shlex` |
| `shutil` | import | `shutil` |
| `speak_stream_ws` | moved-lazy | `hermes_cli.web_routers.audio` |
| `speak_text` | moved-lazy | `hermes_cli.web_routers.audio` |
| `start_gateway` | moved-lazy | `hermes_cli.web_routers.ops` |
| `start_oauth_login` | moved-lazy | `hermes_cli.web_routers.oauth` |
| `start_telegram_onboarding` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `start_whatsapp_onboarding` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `stat` | import | `stat` |
| `stop_gateway` | moved-lazy | `hermes_cli.web_routers.ops` |
| `stream_managed_file` | moved-lazy | `hermes_cli.web_routers.files` |
| `submit_oauth_code` | moved-lazy | `hermes_cli.web_routers.oauth` |
| `tempfile` | import | `tempfile` |
| `test_mcp_server` | moved-lazy | `hermes_cli.web_routers.mcp` |
| `test_messaging_platform` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `timezone` | import | `datetime` |
| `toggle_skill` | moved-lazy | `hermes_cli.web_routers.skills` |
| `toggle_toolset` | moved-lazy | `hermes_cli.web_routers.tools` |
| `transcribe_audio_upload` | moved-lazy | `hermes_cli.web_routers.audio` |
| `trigger_cron_job` | moved-lazy | `hermes_cli.web_routers.cron` |
| `tts_lease` | moved-lazy | `hermes_cli.web_routers.audio` |
| `uninstall_skill_hub` | moved-lazy | `hermes_cli.web_routers.skills` |
| `update_config` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `update_config_raw` | moved-lazy | `hermes_cli.web_routers.analytics` |
| `update_cron_job` | moved-lazy | `hermes_cli.web_routers.cron` |
| `update_hermes` | moved-lazy | `hermes_cli.web_routers.actions` |
| `update_learning_node` | moved-lazy | `hermes_cli.web_routers.status` |
| `update_memory_provider_config` | moved-lazy | `hermes_cli.web_routers.memory_providers` |
| `update_messaging_platform` | moved-lazy | `hermes_cli.web_routers.messaging` |
| `update_profile_description_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `update_profile_model_endpoint` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `update_profile_soul` | moved-lazy | `hermes_cli.web_routers.profiles` |
| `update_skill_content` | moved-lazy | `hermes_cli.web_routers.skills` |
| `update_skills_hub` | moved-lazy | `hermes_cli.web_routers.skills` |
| `upload_chat_image` | moved-lazy | `hermes_cli.web_routers.files` |
| `upload_managed_file` | moved-lazy | `hermes_cli.web_routers.files` |
| `upload_managed_file_stream` | moved-lazy | `hermes_cli.web_routers.files` |
| `upsert_custom_endpoint` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `validate_custom_endpoint` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `validate_provider_credential` | moved-lazy | `hermes_cli.web_routers.config_env` |
| `windows_detach_flags` | moved-lazy | `hermes_cli._subprocess_compat` |
| `windows_hide_flags` | moved-lazy | `hermes_cli._subprocess_compat` |
| `write_platform_config_field` | moved-lazy | `hermes_cli.config` |
| `yaml` | import | `yaml` |
| `zipfile` | import | `zipfile` |

### `hermes_cli.webhook`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `atomic_replace` | 已移动（延迟处理） | `utils` |
| `os` | 导入项 | `os` |
| `tempfile` | 导入项 | `tempfile` |

### `hermes_cli.win_pty_bridge`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | 导入项 | `os` |

### `hermes_logging`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `rotating_file_handlers` | 已恢复（原功能） | `(已删除；基础功能已恢复)` |

### `hermes_state`

| name | kind | new location |
|---|---|---|
| `AUTO_VACUUM_MIN_FREELIST_RATIO` | moved-lazy | `hermes_state_common` |
| `ActivityProvenance` | moved-lazy | `agent.session_activity` |
| `CompressionSessionBusyError` | moved-lazy | `hermes_state_errors` |
| `CompressionSessionClosedError` | moved-lazy | `hermes_state_errors` |
| `DEFERRED_INDEX_SQL` | moved-lazy | `hermes_state_common` |
| `FTS_CJK_STALE_KEY` | moved-lazy | `hermes_state_common` |
| `FTS_CJK_TABLE_SQL` | moved-lazy | `hermes_state_fts` |
| `FTS_CJK_TRIGGER_SQL` | moved-lazy | `hermes_state_fts` |
| `FTS_REBUILD_DEFERRAL_KEY` | moved-lazy | `hermes_state_common` |
| `FTS_SQL` | moved-lazy | `hermes_state_common` |
| `FTS_STALE_KEY` | moved-lazy | `hermes_state_common` |
| `FTS_STORAGE_VERSION` | moved-lazy | `hermes_state_common` |
| `FTS_TRIGRAM_SQL` | moved-lazy | `hermes_state_common` |
| `LEGACY_FTS_SQL` | moved-lazy | `hermes_state_common` |
| `LEGACY_FTS_TRIGRAM_SQL` | moved-lazy | `hermes_state_common` |
| `MAX_FTS5_QUERY_CHARS` | moved-lazy | `hermes_state_common` |
| `MAX_SAFE_EXPORT_MESSAGES` | restored-def | `(deleted; BASE body restored)` |
| `MAX_SAFE_RESUME_MESSAGES` | restored-def | `(deleted; BASE body restored)` |
| `PERSISTENCE_ERROR_CAUSES` | moved-lazy | `hermes_state_errors` |
| `SCHEMA_SQL` | moved-lazy | `hermes_state_common` |
| `SCHEMA_VERSION` | moved-lazy | `hermes_state_common` |
| `SESSION_STATUS_COMPLETE` | moved-lazy | `hermes_state_sessions` |
| `SESSION_STATUS_EMPTY` | moved-lazy | `hermes_state_sessions` |
| `SESSION_STATUS_ERROR` | moved-lazy | `hermes_state_sessions` |
| `SESSION_STATUS_INTERRUPTED` | moved-lazy | `hermes_state_sessions` |
| `SKILL_EXCERPT_JOINT` | moved-lazy | `agent.skill_commands` |
| `SKILL_SCAFFOLD_SQL_LIKE` | moved-lazy | `agent.skill_commands` |
| `SessionTurnLeaseLostError` | moved-lazy | `hermes_state_errors` |
| `Set` | import | `typing` |
| `WalUnsupportedError` | moved-lazy | `hermes_state_wal` |
| `apply_durability_barriers` | moved-lazy | `hermes_state_repair` |
| `classify_session_status` | moved-lazy | `hermes_state_sessions` |
| `close_shared_session_dbs` | unrestorable | `no top-level definition on BASE` |
| `collect_state_db_stats` | moved-lazy | `hermes_state_dbfile` |
| `contextlib` | import | `contextlib` |
| `count_db_holders` | moved-lazy | `hermes_state_dbfile` |
| `describe_skill_invocation` | moved-lazy | `agent.skill_commands` |
| `errno` | import | `errno` |
| `fts5_cjk_so_path` | moved-lazy | `hermes_state_fts` |
| `get_shared_session_db` | unrestorable | `no top-level definition on BASE` |
| `is_advisory_lock_contention` | moved-lazy | `hermes_state_common` |
| `is_automatic_end_reason` | moved-lazy | `hermes_state_common` |
| `is_disk_full_error` | moved-lazy | `hermes_state_errors` |
| `is_sqlite_wal_reset_vulnerable` | moved-lazy | `hermes_state_wal` |
| `is_transient_sqlite_error` | moved-lazy | `hermes_state_errors` |
| `iter_deleted_sqlite_sidecar_holders` | moved-lazy | `hermes_state_dbfile` |
| `release_or_close` | moved-lazy | `hermes_state_registry` |
| `release_shared_session_db` | unrestorable | `no top-level definition on BASE` |
| `report_startup_progress` | moved-lazy | `hermes_startup_watchdog` |
| `resolve_journal_mode` | moved-lazy | `hermes_state_wal` |
| `resolve_synchronous_level` | moved-lazy | `hermes_state_wal` |
| `sanitize_context` | moved-lazy | `agent.memory_manager` |
| `sqlite_source_id` | moved-lazy | `hermes_state_wal` |
| `struct` | import | `struct` |
| `weakref` | import | `weakref` |
| `workspace_key` | moved-lazy | `hermes_state_sessions` |

### `hermes_state_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `close_shared_session_dbs` | restored-def | `(已删除；基础内容已恢复)` |
| `get_shared_session_db` | restored-def | `(已删除；基础内容已恢复)` |
| `release_shared_session_db` | restored-def | `(已删除；基础内容已恢复)` |

### `hermes_state_search`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | import | `json` |
| `os` | import | `os` |

### `plugins.browser.browser_use.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BrowserProvider` | moved-lazy | `agent.browser_provider` |
| `os` | import | `os` |

### `plugins.browser.browserbase.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BrowserProvider` | moved-lazy | `agent.browser_provider` |
| `requests` | import | `requests` |
| `uuid` | import | `uuid` |

### `plugins.browser.firecrawl.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BrowserProvider` | moved-lazy | `agent.browser_provider` |
| `requests` | import | `requests` |
| `uuid` | import | `uuid` |

### `plugins.context_engine`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `importlib` | import | `importlib.util` |
| `sys` | import | `sys` |

### `plugins.cron_providers`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `importlib` | import | `importlib.util` |
| `sys` | import | `sys` |

### `plugins.cron_providers.chronos`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | import | `typing` |

### `plugins.cron_providers.chronos._nas_client`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | 导入模块 | `typing` |

### `plugins.dashboard_auth.basic`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入模块 | `typing` |
| `LoginStart` | 暂缓移动 | `hermes_cli.dashboard_auth` |

### `plugins.dashboard_auth.drain`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `LoginStart` | 暂缓移动 | `hermes_cli.dashboard_auth` |

### `plugins.dashboard_auth.nous`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DashboardAuthProvider` | 暂缓移动 | `hermes_cli.dashboard_auth` |
| `InvalidCodeError` | 暂缓移动 | `hermes_cli.dashboard_auth` |
| `RefreshExpiredError` | 暂缓移动 | `hermes_cli.dashboard_auth` |
| `base64` | 导入模块 | `base64` |
| `classify_jwks_lookup_error` | 暂缓移动 | `hermes_cli.dashboard_auth` |
| `hashlib` | 导入模块 | `hashlib` |
| `httpx` | 导入模块 | `httpx` |
| `os` | 导入模块 | `os` |
| `secrets` | 导入模块 | `secrets` |
| `urllib` | 导入模块 | `urllib.parse` |

### `plugins.dashboard_auth.self_hosted`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DashboardAuthProvider` | 暂缓移动 | `hermes_cli.dashboard_auth` |
| `InvalidCodeError` | 暂缓移动 | `hermes_cli.dashboard_auth` |
| `RefreshExpiredError` | 暂缓移动 | `hermes_cli.dashboard_auth` |
| `classify_jwks_lookup_error` | 暂缓移动 | `hermes_cli.dashboard_auth` |
| `hashlib` | 导入模块 | `hashlib` |
| `os` | 导入模块 | `os` |
| `secrets` | 导入模块 | `secrets` |

### `plugins.google_meet.audio_bridge`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `chrome_fake_audio_flags` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |

### `plugins.google_meet.meet_bot`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `SAY_PCM_FILENAME` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |
| `SAY_QUEUE_FILENAME` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |
| `json` | 导入项 | `json` |

### `plugins.google_meet.node.cli`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入项 | `typing` |

### `plugins.google_meet.node.registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入项 | `json` |

### `plugins.image_gen.deepinfra`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ImageGenProvider` | 暂缓移动 | `agent.image_gen_provider` |
| `error_response` | 暂缓移动 | `agent.image_gen_provider` |
| `save_b64_image` | 暂缓移动 | `agent.image_gen_provider` |
| `save_url_image` | 暂缓移动 | `agent.image_gen_provider` |

### `plugins.image_gen.fal`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ImageGenProvider` | 暂缓移动 | `agent.image_gen_provider` |
| `os` | 导入项 | `os` |

### `plugins.image_gen.krea`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ImageGenProvider` | 暂缓移动 | `agent.image_gen_provider` |
| `error_response` | 暂缓移动 | `agent.image_gen_provider` |
| `normalize_reference_images` | 暂缓移动 | `agent.image_gen_provider` |
| `os` | 导入项 | `os` |

### `plugins.image_gen.openai`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ImageGenProvider` | 已延迟移动 | `agent.image_gen_provider` |
| `error_response` | 已延迟移动 | `agent.image_gen_provider` |
| `normalize_reference_images` | 已延迟移动 | `agent.image_gen_provider` |
| `save_b64_image` | 已延迟移动 | `agent.image_gen_provider` |
| `save_url_image` | 已延迟移动 | `agent.image_gen_provider` |

### `plugins.image_gen.xai`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ImageGenProvider` | 已延迟移动 | `agent.image_gen_provider` |
| `error_response` | 已延迟移动 | `agent.image_gen_provider` |
| `normalize_reference_images` | 已延迟移动 | `agent.image_gen_provider` |
| `save_b64_image` | 已延迟移动 | `agent.image_gen_provider` |
| `save_url_image` | 已延迟移动 | `agent.image_gen_provider` |

### `plugins.memory.hindsight`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `dataclass` | 导入项 | `dataclasses` |
| `importlib` | 导入项 | `importlib` |

### `plugins.memory.honcho`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CONCLUDE_SCHEMA` | 已恢复定义 | `(已删除；恢复基础结构)` |
| `CONTEXT_SCHEMA` | 已恢复定义 | `(已删除；恢复基础结构)` |
| `PROFILE_SCHEMA` | 已恢复定义 | `(已删除；恢复基础结构)` |
| `REASONING_SCHEMA` | 已恢复定义 | `(已删除；恢复基础结构)` |
| `SEARCH_SCHEMA` | 已恢复定义 | `(已删除；恢复基础结构)` |
| `TRIVIAL_PROMPT_RE` | 已延迟移动 | `agent.memory_provider` |

### `plugins.memory.honcho.client`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `SingletonSlot` | moved-lazy | `plugins.plugin_utils` |

### `plugins.memory.honcho.oauth`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Callable` | import | `typing` |

### `plugins.memory.honcho.session`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Callable` | import | `typing` |
| `Path` | import | `pathlib` |
| `hashlib` | import | `hashlib` |
| `re` | import | `re` |

### `plugins.memory.mem0`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ADD_SCHEMA` | restored-def | `(已删除；已恢复基础内容)` |
| `DELETE_SCHEMA` | restored-def | `(已删除；已恢复基础内容)` |
| `SEARCH_SCHEMA` | restored-def | `(已删除；已恢复基础内容)` |
| `UPDATE_SCHEMA` | restored-def | `(已删除；已恢复基础内容)` |

### `plugins.memory.mem0._setup`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `has_oss_flags` | restored-def | `(已删除；已恢复基础内容)` |

### `plugins.memory.retaindb`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CONTEXT_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `Dict` | 导入 | `typing` |
| `FILE_DELETE_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `FILE_INGEST_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `FILE_LIST_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `FILE_READ_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `FILE_UPLOAD_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `FORGET_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `List` | 导入 | `typing` |
| `PROFILE_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `REMEMBER_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `SEARCH_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |

### `plugins.memory.supermemory`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `FORGET_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `PROFILE_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `SEARCH_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |
| `STORE_SCHEMA` | 已恢复-定义 | `(已删除；基础内容已恢复)` |

### `plugins.platforms.a2a.protocol`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ERR_PUSH_NOT_SUPPORTED` | restored-def | `(已删除；基础内容已恢复)` |
| `STATE_AUTH_REQUIRED` | restored-def | `(已删除；基础内容已恢复)` |
| `copy` | import | `copy` |
| `data_part` | restored-def | `(已删除；基础内容已恢复)` |
| `file_part` | restored-def | `(已删除；基础内容已恢复)` |
| `message_with_parts` | restored-def | `(已删除；基础内容已恢复)` |
| `stream_message` | restored-def | `(已删除；基础内容已恢复)` |

### `plugins.platforms.a2a.security`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Path` | import | `pathlib` |
| `authenticate` | restored-def | `(已删除；基础内容已恢复)` |
| `get_bearer_token` | restored-def | `(已删除；基础内容已恢复)` |
| `get_peer_tokens` | restored-def | `(已删除；基础内容已恢复)` |
| `get_push_secret` | restored-def | `(已删除；基础内容已恢复)` |
| `get_trusted_peers` | restored-def | `(已删除；基础内容已恢复)` |
| `is_trusted_peer` | restored-def | `(已删除；基础内容已恢复)` |
| `resolve_bind_host` | restored-def | `(已删除；基础内容已恢复)` |
| `sign_push_payload` | restored-def | `(已删除；基础内容已恢复)` |

### `plugins.platforms.a2a.tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `TypedDict` | import | `typing` |

### `plugins.platforms.dingtalk.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DINGTALK_TYPE_MAPPING` | 已延迟移动 | `plugins.platforms.dingtalk.inbound` |
| `EXT_MAP` | 已恢复（原为删除状态） | `(已删除；基础内容已恢复)` |
| `MessageType` | 已延迟移动 | `gateway.platforms.event` |

### `plugins.platforms.discord.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `env_int` | 已延迟移动 | `utils` |

### `plugins.platforms.feishu.feishu_comment`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `add_comment_reaction` | 已恢复（原为删除状态） | `(已删除；基础内容已恢复)` |
| `delete_comment_reaction` | 已恢复（原为删除状态） | `(已删除；基础内容已恢复)` |

### `plugins.platforms.google_chat.oauth`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `atomic_replace` | 已延迟移动 | `utils` |
| `secrets` | 导入项 | `secrets` |
| `subprocess` | 导入项 | `subprocess` |

### `plugins.platforms.irc.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | 导入项 | `os` |

### `plugins.platforms.line.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `field` | 导入项 | `dataclasses` |

### `plugins.platforms.matrix.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `MAX_MESSAGE_LENGTH` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `PaginationDirection` | 无法恢复的项 | `BASE中不存在顶层定义` |
| `SyncToken` | 无法恢复的项 | `BASE中不存在顶层定义` |
| `_MATRIX_CAPABILITIES` | 已恢复的辅助项 | `(已删除；作为get_matrix_capabilities的依赖项被恢复)` |
| `get_matrix_capabilities` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `plugins.platforms.ntfy.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | 导入项 | `os` |

### `plugins.platforms.photon.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ProcessingOutcome` | 暂时移动的项 | `gateway.platforms.event` |
| `resolve_sidecar_dir` | 暂时移动的项 | `plugins.platforms.photon.sidecar_paths` |

### `plugins.platforms.photon.auth`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `credential_summary` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `get_session` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `plugins.platforms.photon.cli`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Path` | 导入项 | `pathlib` |
| `resolve_sidecar_dir` | 暂时移动的项 | `plugins.platforms.photon.sidecar_paths` |

### `plugins.platforms.raft.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `asyncio` | 导入项 | `asyncio` |

### `plugins.platforms.teams.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `TeamsSummaryWriter` | 已延迟移动 | `plugins.platforms.teams.summary_writer` |
| `html` | 导入模块 | `html` |
| `quote` | 导入模块 | `urllib.parse` |

### `plugins.platforms.telegram.adapter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `atomic_replace` | 已延迟移动 | `utils` |
| `cache_document_from_bytes` | 已延迟移动 | `gateway.platforms.base` |
| `threading` | 导入模块 | `threading` |

### `plugins.platforms.telegram.telegram_ids`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `telegram_chat_id_key` | 已恢复 | `(已删除；基础内容已恢复)` |

### `plugins.platforms.wecom.adapter`

| name | kind | new location |
|---|---|---|
| `ABSOLUTE_MAX_BYTES` | moved-lazy | `plugins.platforms.wecom.media` |
| `APP_CMD_UPLOAD_MEDIA_CHUNK` | moved-lazy | `plugins.platforms.wecom.media` |
| `APP_CMD_UPLOAD_MEDIA_FINISH` | moved-lazy | `plugins.platforms.wecom.media` |
| `APP_CMD_UPLOAD_MEDIA_INIT` | moved-lazy | `plugins.platforms.wecom.media` |
| `FILE_MAX_BYTES` | moved-lazy | `plugins.platforms.wecom.media` |
| `IMAGE_MAX_BYTES` | moved-lazy | `plugins.platforms.wecom.media` |
| `MAX_INTERMEDIATE_FRAMES` | moved-lazy | `plugins.platforms.wecom.streaming` |
| `MAX_UPLOAD_CHUNKS` | moved-lazy | `plugins.platforms.wecom.media` |
| `Path` | import | `pathlib` |
| `ReplyFrame` | moved-lazy | `plugins.platforms.wecom.streaming` |
| `STREAM_EXPIRED_ERRCODE` | moved-lazy | `plugins.platforms.wecom.streaming` |
| `STREAM_REQUEST_EXPIRED_ERRCODE` | moved-lazy | `plugins.platforms.wecom.streaming` |
| `STREAM_VERSION_CONFLICT_ERRCODE` | moved-lazy | `plugins.platforms.wecom.streaming` |
| `UPLOAD_CHUNK_SIZE` | moved-lazy | `plugins.platforms.wecom.media` |
| `VIDEO_MAX_BYTES` | moved-lazy | `plugins.platforms.wecom.media` |
| `VOICE_MAX_BYTES` | moved-lazy | `plugins.platforms.wecom.media` |
| `VOICE_SUPPORTED_MIMES` | moved-lazy | `plugins.platforms.wecom.media` |
| `WeComStreamExpiredError` | moved-lazy | `plugins.platforms.wecom.streaming` |
| `base64` | import | `base64` |
| `cache_document_from_bytes_async` | moved-lazy | `gateway.platforms.base` |
| `cache_image_from_bytes_async` | moved-lazy | `gateway.platforms.base` |
| `dataclass` | import | `dataclasses` |
| `deque` | import | `collections` |
| `hashlib` | import | `hashlib` |
| `mimetypes` | import | `mimetypes` |
| `os` | import | `os` |
| `unquote` | import | `urllib.parse` |
| `urlparse` | import | `urllib.parse` |

### `plugins.spotify`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `SPOTIFY_ALBUMS_SCHEMA` | 已延迟移动 | `plugins.spotify.tools` |
| `SPOTIFY_DEVICES_SCHEMA` | 已延迟移动 | `plugins.spotify.tools` |
| `SPOTIFY_LIBRARY_SCHEMA` | 已延迟移动 | `plugins.spotify.tools` |
| `SPOTIFY_PLAYBACK_SCHEMA` | 已延迟移动 | `plugins.spotify.tools` |
| `SPOTIFY_PLAYLISTS_SCHEMA` | 已延迟移动 | `plugins.spotify.tools` |
| `SPOTIFY_QUEUE_SCHEMA` | 已延迟移动 | `plugins.spotify.tools` |
| `SPOTIFY_SEARCH_SCHEMA` | 已延迟移动 | `plugins.spotify.tools` |

### `plugins.spotify.client`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `compact_json` | 已恢复 | `(已删除；基础内容已恢复)` |
| `json` | 已导入恢复 | `json` |
| `json` | 导入项 | `json` |

### `plugins.spotify.tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `SpotifyAPIError` | 已延迟移动 | `plugins.spotify.client` |
| `SpotifyAuthRequiredError` | 已延迟移动 | `plugins.spotify.client` |

### `plugins.teams_pipeline.cli`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `GraphSubscription` | 已延迟移动 | `plugins.teams_pipeline.models` |
| `Path` | 导入项 | `pathlib` |
| `datetime` | 导入项 | `datetime` |
| `timedelta` | 导入项 | `datetime` |
| `timezone` | 导入项 | `datetime` |

### `plugins.teams_pipeline.meetings`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `fetch_call_record_artifact` | 已恢复 | `(已删除；基础内容已恢复)` |

### `plugins.teams_pipeline.pipeline`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | 导入项 | `os` |
### `plugins.teams_pipeline.subscriptions`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `build_store` | restored-def | `(已删除；恢复为原始内容)` |
| `resolve_store_path` | restored-helper | `(已删除；作为 build_store 的依赖项被恢复)` |
| `resolve_store_path` | restored-def | `(已删除；恢复为原始内容)` |
| `resolve_teams_pipeline_store_path` | restored-import | `plugins.teams_pipeline.store` |
| `resolve_teams_pipeline_store_path` | moved-lazy | `plugins.teams_pipeline.store` |

### `plugins.video_gen.fal`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | import | `os` |

### `plugins.video_gen.xai`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `_run_xai_video_coroutine` | restored-helper | `(已删除；作为 run_xai_video_generation 的依赖项被恢复)` |
| `run_xai_video_generation` | restored-def | `(已删除；恢复为原始内容)` |

### `plugins.web.brave_free.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `WebSearchProvider` | moved-lazy | `agent.web_search_provider` |
| `os` | import | `os` |

### `plugins.web.ddgs.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `WebSearchProvider` | moved-lazy | `agent.web_search_provider` |

### `plugins.web.exa.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `WebSearchProvider` | moved-lazy | `agent.web_search_provider` |
| `os` | import | `os` |

### `plugins.web.firecrawl.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `NoReturn` | import | `typing` |
| `TYPE_CHECKING` | import | `typing` |
| `WebSearchProvider` | 暂缓移动 | `agent.web_search_provider` |
| `os` | import | `os` |

### `plugins.web.keenable.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `WebSearchProvider` | 暂缓移动 | `agent.web_search_provider` |

### `plugins.web.parallel.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `WebSearchProvider` | 暂缓移动 | `agent.web_search_provider` |

### `plugins.web.searxng.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `WebSearchProvider` | 暂缓移动 | `agent.web_search_provider` |
| `os` | import | `os` |

### `plugins.web.tavily.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `WebSearchProvider` | 暂缓移动 | `agent.web_search_provider` |

### `plugins.web.xai.provider`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `WebSearchProvider` | 暂缓移动 | `agent.web_search_provider` |

### `providers`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `OMIT_TEMPERATURE` | 暂缓移动 | `providers.base` |

### `run_agent`

| name | kind | new location |
|---|---|---|
| `COMPRESSED_SUMMARY_METADATA_KEY` | moved-lazy | `agent.context_compressor` |
| `ContextCompressor` | moved-lazy | `agent.context_compressor` |
| `DEFAULT_AGENT_IDENTITY` | moved-lazy | `agent.prompt_builder` |
| `FailoverReason` | moved-lazy | `agent.error_classifier` |
| `OpenAI` | moved-lazy | `agent.process_bootstrap` |
| `SimpleNamespace` | import | `types` |
| `asyncio` | import | `asyncio` |
| `atomic_json_write` | moved-lazy | `utils` |
| `base64` | import | `base64` |
| `build_context_files_prompt` | moved-lazy | `agent.prompt_builder` |
| `build_environment_hints` | moved-lazy | `agent.prompt_builder` |
| `build_skills_system_prompt` | moved-lazy | `agent.prompt_builder` |
| `check_toolset_requirements` | moved-lazy | `model_tools` |
| `convert_scratchpad_to_think` | moved-lazy | `agent.trajectory` |
| `copy` | import | `copy` |
| `estimate_request_tokens_rough` | moved-lazy | `agent.model_metadata` |
| `file_mutation_result_landed` | moved-lazy | `agent.tool_result_classification` |
| `flatten_message_text` | moved-lazy | `agent.message_content` |
| `get_tool_definitions` | moved-lazy | `model_tools` |
| `handle_function_call` | moved-lazy | `model_tools` |
| `hashlib` | import | `hashlib` |
| `is_truthy_value` | moved-lazy | `utils` |
| `jittered_backoff` | moved-lazy | `agent.retry_utils` |
| `load_soul_md` | moved-lazy | `agent.prompt_builder` |
| `normalize_usage` | moved-lazy | `agent.usage_pricing` |
| `redact_sensitive_text` | moved-lazy | `agent.redact` |
| `request_hard_interrupt` | moved-lazy | `agent.interrupt_compat` |
| `sanitize_context` | moved-lazy | `agent.memory_manager` |
| `tempfile` | import | `tempfile` |
| `user_originated_turn_view` | moved-lazy | `agent.context_compressor` |

### `tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `mcp_tool` | 不可恢复型 | `BASE 中无顶层定义` |

### `tools.apply_layout_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入型 | `json` |

### `tools.approval`

| name | kind | new location |
|---|---|---|
| `DANGEROUS_PATTERNS` | moved-lazy | `tools.approval_detection` |
| `DANGEROUS_PATTERNS_COMPILED` | moved-lazy | `tools.approval_detection` |
| `HARDLINE_PATTERNS` | moved-lazy | `tools.approval_detection` |
| `HARDLINE_PATTERNS_COMPILED` | moved-lazy | `tools.approval_detection` |
| `HUMAN_WAIT_MARGIN_S` | moved-lazy | `tools.approval_human_wait` |
| `cfg_get` | moved-lazy | `hermes_cli.config` |
| `contextlib` | import | `contextlib` |
| `contextvars` | import | `contextvars` |
| `fnmatch` | import | `fnmatch` |
| `functools` | import | `functools` |
| `get_plugin_manager` | moved-lazy | `tools.approval_prompt` |
| `human_wait_ceiling` | moved-lazy | `tools.approval_human_wait` |
| `human_wait_seconds` | moved-lazy | `tools.approval_human_wait` |
| `human_wait_window` | moved-lazy | `tools.approval_human_wait` |
| `is_interrupted` | moved-lazy | `tools.interrupt` |
| `re` | import | `re` |
| `request_elicitation_consent` | moved-lazy | `tools.approval_prompt` |
| `reset_current_observability_context` | moved-lazy | `tools.approval_context` |
| `reset_current_session_key` | moved-lazy | `tools.approval_context` |
| `reset_hermes_interactive_context` | moved-lazy | `tools.approval_context` |
| `set_current_observability_context` | moved-lazy | `tools.approval_context` |
| `set_current_session_key` | moved-lazy | `tools.approval_context` |
| `set_hermes_interactive_context` | moved-lazy | `tools.approval_context` |
| `shlex` | import | `shlex` |
| `sys` | import | `sys` |
| `tempfile` | import | `tempfile` |
| `time` | import | `time` |
| `unicodedata` | import | `unicodedata` |
| `uuid` | import | `uuid` |

### `tools.async_delegation`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `active_for_session` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `tools.browser_camofox_state`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CAMOFOX_STATE_DIR_NAME` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `CAMOFOX_STATE_SUBDIR` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `tools.browser_dialog_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `logger` | 暂缓移动 | `tools.approval` |
| `logging` | 导入项 | `logging` |

### `tools.browser_supervisor`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CONSOLE_HISTORY_MAX` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `ConsoleEvent` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `DIALOG_BRIDGE_HOST` | 暂缓移动 | `tools.browser_supervisor_dialogs` |
| `DIALOG_BRIDGE_URL_PATTERN` | 暂缓移动 | `tools.browser_supervisor_dialogs` |
| `DIALOG_POLICY_AUTO_ACCEPT` | 暂缓移动 | `tools.browser_supervisor_dialogs` |
| `DIALOG_POLICY_AUTO_DISMISS` | 暂缓移动 | `tools.browser_supervisor_dialogs` |
| `DIALOG_POLICY_MUST_RESPOND` | 暂缓移动 | `tools.browser_supervisor_dialogs` |
| `FRAME_TREE_MAX_ENTRIES` | 暂缓移动 | `tools.browser_supervisor_frames` |
| `FRAME_TREE_MAX_OOPIF_DEPTH` | 暂缓移动 | `tools.browser_supervisor_frames` |

### `tools.browser_tool`

| name | kind | new location |
|---|---|---|
| `BrowserUseProvider` | moved-lazy | `plugins.browser.browser_use.provider.BrowserUseBrowserProvider` |
| `BrowserbaseProvider` | moved-lazy | `plugins.browser.browserbase.provider.BrowserbaseBrowserProvider` |
| `CloudBrowserProvider` | moved-lazy | `agent.browser_provider.BrowserProvider` |
| `FirecrawlProvider` | moved-lazy | `plugins.browser.firecrawl.provider.FirecrawlBrowserProvider` |
| `List` | import | `typing` |
| `SNAPSHOT_SUMMARIZE_THRESHOLD` | restored-def | `(deleted; BASE body restored)` |
| `Tuple` | import | `typing` |
| `agent_browser_runnable` | moved-lazy | `hermes_constants` |
| `check_browser_requirements` | moved-lazy | `tools.browser_tool_install` |
| `check_browser_vision_requirements` | moved-lazy | `tools.browser_tool_install` |
| `cleanup_all_browsers` | moved-lazy | `tools.browser_tool_lifecycle` |
| `cleanup_browser` | moved-lazy | `tools.browser_tool_lifecycle` |
| `contextlib` | import | `contextlib` |
| `datetime` | import | `datetime` |
| `functools` | import | `functools` |
| `get_hermes_home_override` | moved-lazy | `hermes_constants` |
| `hermes_home_key` | moved-lazy | `hermes_constants` |
| `is_truthy_value` | moved-lazy | `utils` |
| `lightpanda_engine_status` | moved-lazy | `tools.browser_tool_lightpanda_fallback` |
| `node_tool_runnable` | moved-lazy | `hermes_constants` |
| `normalize_browser_cloud_provider` | moved-lazy | `tools.tool_backend_helpers` |
| `re` | import | `re` |
| `reset_hermes_home_override` | moved-lazy | `hermes_constants` |
| `set_hermes_home_override` | moved-lazy | `hermes_constants` |
| `shutil` | import | `shutil` |
| `signal` | import | `signal` |
| `timezone` | import | `datetime` |
| `warm_agent_browser_npx_cache` | moved-lazy | `tools.browser_tool_install` |
| `windows_hide_flags` | moved-lazy | `hermes_cli._subprocess_compat` |

### `tools.clarify_gateway`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `get_notify` | restored-def | `(已删除；基础内容已恢复)` |
| `register_notify` | restored-def | `(已删除；基础内容已恢复)` |
| `unregister_notify` | restored-def | `(已删除；基础内容已恢复)` |

### `tools.close_preview_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CLOSE_PREVIEW_SCHEMA` | restored-def | `(已删除；基础内容已恢复)` |
| `json` | import | `json` |
| `registry` | moved-lazy | `tools.registry` |
| `tool_error` | moved-lazy | `tools.registry` |

### `tools.code_execution_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEFAULT_KERNEL_MODE` | restored-def | `(已删除；基础内容已恢复)` |
| `KERNEL_MODES` | restored-def | `(已删除；基础内容已恢复)` |
| `platform` | import | `platform` |
| `socket` | import | `socket` |
| `sys` | import | `sys` |
| `thread_scoped_silence` | moved-lazy | `agent.thread_scoped_output` |

### `tools.code_kernel_remote`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `base64` | import | `base64` |

### `tools.computer_use`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `annotations` | 导入模块 | `__future__` |
| `check_computer_use_requirements` | 拖延移动 | `tools.computer_use.tool` |
| `get_computer_use_schema` | 拖延移动 | `tools.computer_use.tool` |
| `handle_computer_use` | 拖延移动 | `tools.computer_use.tool` |
| `release_computer_use_session` | 拖延移动 | `tools.computer_use.tool` |
| `set_approval_callback` | 拖延移动 | `tools.computer_use.tool` |

### `tools.computer_use.cua_backend`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `CaptureResult` | 拖延移动 | `tools.computer_use.backend` |
| `PureWindowsPath` | 导入模块 | `pathlib` |
| `Tuple` | 导入模块 | `typing` |
| `UIElement` | 拖延移动 | `tools.computer_use.backend` |
| `asyncio` | 导入模块 | `asyncio` |
| `base64` | 导入模块 | `base64` |
| `concurrent` | 导入模块 | `concurrent.futures` |
| `cua_driver_install_hint` | 拖延移动 | `tools.computer_use.cua_backend_driver` |
| `cua_driver_update_check` | 拖延移动 | `tools.computer_use.cua_backend_driver` |
| `deque` | 导入模块 | `collections` |
| `functools` | 导入模块 | `functools` |
| `json` | 导入模块 | `json` |
| `re` | 导入模块 | `re` |
| `shutil` | 导入模块 | `shutil` |
| `tempfile` | 导入模块 | `tempfile` |
| `time` | 导入模块 | `time` |

### `tools.computer_use.permissions`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `List` | 导入模块 | `typing` |

### `tools.computer_use.tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `struct` | 导入模块 | `struct` |

### `tools.cronjob_tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `effective_job_state` | 已延迟移动 | `cron.jobs` |
| `re` | 已导入 | `re` |

### `tools.delegate_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEFAULT_CHILD_TIMEOUT` | 已延迟移动 | `tools.delegate_tool_config` |
| `DEFAULT_MAX_SUMMARY_CHARS` | 已延迟移动 | `tools.delegate_tool_results` |
| `DEFAULT_TOOLSETS` | 已延迟移动 | `tools.delegate_tool_toolsets` |
| `FuturesTimeoutError` | 已导入 | `concurrent.futures` |
| `MAX_DEPTH` | 已延迟移动 | `tools.delegate_tool_config` |
| `TOOLSETS` | 已延迟移动 | `toolsets` |
| `base_url_hostname` | 已延迟移动 | `utils` |
| `contextvars` | 已导入 | `contextvars` |
| `enum` | 已导入 | `enum` |
| `file_state` | 已延迟移动 | `tools` |
| `json` | 已导入 | `json` |
| `os` | 已导入 | `os` |
| `re` | 已导入 | `re` |
| `request_hard_interrupt` | 已延迟移动 | `agent.interrupt_compat` |
| `threading` | 已导入 | `threading` |
| `urlsplit` | 已导入 | `urllib.parse` |
| `urlunsplit` | 已导入 | `urllib.parse` |

### `tools.delegation_live_log`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `new_live_delegation_id` | 已恢复（原为删除） | `(已删除；基础内容已恢复)` |

### `tools.delegation_output_schema`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `MAX_SCHEMA_RETRIES` | 已恢复（原为删除） | `(已删除；基础内容已恢复)` |

### `tools.discord_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `TYPE_CHECKING` | 已导入 | `typing` |
| `Tuple` | 已导入 | `typing` |
| `get_dynamic_schema` | 已恢复（原为删除） | `(已删除；基础内容已恢复)` |
### `tools.drive_preview_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入模块 | `json` |

### `tools.env_probe`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `os` | 导入模块 | `os` |

### `tools.environments`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `modal_utils` | 不可恢复的模块 | `BASE 中不存在顶层定义` |

### `tools.environments.base`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `IO` | 导入模块 | `typing` |
| `Protocol` | 导入模块 | `typing` |
| `codecs` | 导入模块 | `codecs` |
| `deque` | 导入模块 | `collections` |
| `re` | 导入模块 | `re` |
| `sanitize_task_id_for_path` | 暂缓移动 | `tools.environments.path_utils` |
| `select` | 导入模块 | `select` |
| `subprocess` | 导入模块 | `subprocess` |
| `windows_hide_flags` | 暂缓移动 | `hermes_cli._subprocess_compat` |

### `tools.environments.managed_modal`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BaseModalExecutionEnvironment` | 不可恢复的模块 | `BASE 中不存在顶层定义` |
| `ModalExecStart` | 不可恢复的模块 | `BASE 中不存在顶层定义` |
| `PreparedModalExec` | 不可恢复的模块 | `BASE 中不存在顶层定义` |
| `dataclass` | 导入模块 | `dataclasses` |

### `tools.environments.modal_utils`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `*` | 模块占位符 | `(已删除)` |

### `tools.environments.vercel_sandbox`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `dataclass` | 导入模块 | `dataclasses` |

### `tools.feishu_doc_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入模块 | `json` |
| `logger` | 暂缓移动 | `tools.approval` |
| `logging` | 导入模块 | `logging` |
| `threading` | 导入模块 | `threading` |

### `tools.feishu_drive_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入模块 | `json` |
| `threading` | 导入模块 | `threading` |

### `tools.file_operations`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入项 | `typing` |
| `ClassVar` | 导入项 | `typing` |
| `DEFAULT_READ_LIMIT` | 暂缓移动 | `tools.file_operations_common` |
| `DEFAULT_READ_OFFSET` | 暂缓移动 | `tools.file_operations_common` |
| `DEFAULT_SEARCH_LIMIT` | 暂缓移动 | `tools.file_operations_common` |
| `DEFAULT_SEARCH_OFFSET` | 暂缓移动 | `tools.file_operations_common` |
| `LINTERS` | 暂缓移动 | `tools.file_operations_lint` |
| `LintResult` | 暂缓移动 | `tools.file_operations_common` |
| `List` | 导入项 | `typing` |
| `MAX_FILE_SIZE` | 暂缓移动 | `tools.transcription_common` |
| `MAX_LINES` | 已恢复的删除项 | （已删除；基础内容已恢复） |
| `MAX_LINE_LENGTH` | 已恢复的删除项 | （已删除；基础内容已恢复） |
| `SEARCH_PRUNE_DIR_NAMES` | 暂缓移动 | `agent.search_policy` |
| `SearchMatch` | 暂缓移动 | `tools.file_operations_common` |
| `WRITE_DENIED_PATHS` | 已恢复的删除项 | （已删除；基础内容已恢复） |
| `WRITE_DENIED_PREFIXES` | 已恢复的删除项 | （已删除；基础内容已恢复） |
| `build_write_denied_paths` | 已恢复的导入项 | `agent.file_safety` |
| `build_write_denied_paths` | 暂缓移动 | `agent.file_safety` |
| `build_write_denied_prefixes` | 已恢复的导入项 | `agent.file_safety` |
| `build_write_denied_prefixes` | 暂缓移动 | `agent.file_safety` |
| `dataclass` | 导入项 | `dataclasses` |
| `field` | 导入项 | `dataclasses` |
| `posixpath` | 导入项 | `posixpath` |
| `threading` | 导入项 | `threading` |
| `tool_interrupt` | 暂缓移动 | `tools.interrupt` |
### `tools.file_tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `PurePosixPath` | 导入项 | `pathlib` |
| `has_opaque_document_extension` | 暂缓移动 | `tools.binary_extensions` |
| `is_pdf_path` | 暂缓移动 | `tools.binary_extensions` |
| `notify_other_tool_call` | 暂缓移动 | `tools.file_tools_read_tracking` |
| `posixpath` | 导入项 | `posixpath` |
| `reset_file_dedup` | 暂缓移动 | `tools.file_tools_read_tracking` |
| `sys` | 导入项 | `sys` |

### `tools.focus_pane_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `FOCUS_PANE_SCHEMA` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |
| `json` | 导入项 | `json` |

### `tools.fuzzy_match`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `List` | 导入项 | `typing` |
| `Tuple` | 导入项 | `typing` |

### `tools.image_generation_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `is_krea_model` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |

### `tools.lazy_deps`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `feature_specs` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |

### `tools.managed_tool_gateway`

| name | kind | new location |
|---|---|---|
| `_MANAGED_GATEWAY_VENDOR` | restored-helper | `(deleted; restored as a dependency of build_managed_media_uploader)` |
| `_MEDIA_UPLOAD_PRESIGN_TIMEOUT_SECONDS` | restored-helper | `(deleted; restored as a dependency of build_managed_media_uploader)` |
| `_MEDIA_UPLOAD_PUT_READ_TIMEOUT_SECONDS` | restored-helper | `(deleted; restored as a dependency of build_managed_media_uploader)` |
| `_MEDIA_UPLOAD_PUT_WRITE_TIMEOUT_SECONDS` | restored-helper | `(deleted; restored as a dependency of build_managed_media_uploader)` |
| `_describe_media_upload_refusal` | restored-helper | `(deleted; restored as a dependency of build_managed_media_uploader)` |
| `build_managed_media_uploader` | restored-def | `(deleted; BASE body restored)` |
| `is_managed_nous_gateway_url` | restored-helper | `(deleted; restored as a dependency of build_managed_media_uploader)` |
| `is_managed_nous_gateway_url` | restored-def | `(deleted; BASE body restored)` |
| `managed_gateway_auth_headers` | restored-helper | `(deleted; restored as a dependency of build_managed_media_uploader)` |
| `managed_gateway_auth_headers` | restored-def | `(deleted; BASE body restored)` |
| `managed_vendor_base_path` | restored-def | `(deleted; BASE body restored)` |
| `managed_vendor_endpoints` | restored-def | `(deleted; BASE body restored)` |
| `managed_vendor_upload_path` | restored-helper | `(deleted; restored as a dependency of managed_vendor_endpoints)` |
| `managed_vendor_upload_path` | restored-def | `(deleted; BASE body restored)` |
| `urlsplit` | restored-import | `urllib.parse` |
| `urlsplit` | import | `urllib.parse` |

### `tools.mcp_oauth`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `OAuthClientInformationFull` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `OAuthClientMetadata` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `OAuthClientProvider` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `OAuthMetadata` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `OAuthToken` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `contextmanager` | 导入项 | `contextlib` |

### `tools.mcp_schema_cache`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `clear_cache_entry` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `has_cached_entry` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `tools.mcp_tool`

| name | kind | new location |
|---|---|---|
| `Coroutine` | import | `typing` |
| `InvalidMcpUrlError` | moved-lazy | `tools.mcp_tool_errors` |
| `MCP_TOOL_NAME_PREFIX` | moved-lazy | `tools.mcp_tool_schema` |
| `NonMcpEndpointError` | moved-lazy | `tools.mcp_tool_errors` |
| `SimpleNamespace` | import | `types` |
| `Tuple` | import | `typing` |
| `asynccontextmanager` | import | `contextlib` |
| `concurrent` | import | `concurrent.futures` |
| `datetime` | import | `datetime` |
| `discover_mcp_tools` | moved-lazy | `tools.mcp_tool_discovery` |
| `errno` | import | `errno` |
| `fnmatch` | import | `fnmatch` |
| `get_mcp_status` | moved-lazy | `tools.mcp_tool_discovery` |
| `get_registered_mcp_server_names` | moved-lazy | `tools.mcp_tool_discovery` |
| `has_registered_mcp_tools` | moved-lazy | `tools.mcp_tool_discovery` |
| `is_mcp_tool_parallel_safe` | moved-lazy | `tools.mcp_tool_discovery` |
| `json` | import | `json` |
| `matches_name_filter` | moved-lazy | `tools.mcp_tool_schema` |
| `math` | import | `math` |
| `mcp_prefixed_tool_name` | moved-lazy | `tools.mcp_tool_schema` |
| `persist_agent_tool_names` | moved-lazy | `tools.mcp_tool_agent` |
| `probe_mcp_server_tools` | moved-lazy | `tools.mcp_tool_discovery` |
| `random` | import | `random` |
| `re` | import | `re` |
| `reconnect_mcp_server` | moved-lazy | `tools.mcp_tool_loop` |
| `refresh_agent_mcp_tools` | moved-lazy | `tools.mcp_tool_agent` |
| `register_mcp_servers` | moved-lazy | `tools.mcp_tool_discovery` |
| `reprobe_tool_availability` | moved-lazy | `tools.mcp_tool_agent` |
| `restore_agent_tool_prefix` | moved-lazy | `tools.mcp_tool_agent` |
| `sanitize_mcp_name_component` | moved-lazy | `tools.mcp_tool_schema` |
| `shutdown_mcp_servers` | moved-lazy | `tools.mcp_tool_lifecycle` |
| `shutil` | import | `shutil` |
| `strip_unicode_tags` | moved-lazy | `tools.ansi_strip` |
| `tool_error` | moved-lazy | `tools.registry` |
| `urlparse` | import | `urllib.parse` |

### `tools.memory_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `atomic_write_text` | 暂时移动 | `utils` |
| `contextmanager` | 导入项 | `contextlib` |
| `time` | 导入项 | `time` |

### `tools.microsoft_graph_client`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `AsyncIterator` | 导入项 | `typing` |
| `GraphCredentials` | 暂时移动 | `tools.microsoft_graph_auth` |

### `tools.open_preview_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `OPEN_PREVIEW_SCHEMA` | 已恢复的已定义项 | `(已删除；基础内容已恢复)` |
| `json` | 导入项 | `json` |
| `registry` | 暂时移动 | `tools.registry` |

### `tools.openrouter_client`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `get_async_client` | 已恢复的已定义项 | `(已删除；基础内容已恢复)` |

### `tools.path_security`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `logger` | 暂时移动 | `tools.approval` |
| `logging` | 导入项 | `logging` |

### `tools.preview_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入项 | `json` |
| `preview_open` | 已恢复的已定义项 | `(已删除；基础内容已恢复)` |

### `tools.process_registry`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `MAX_ACTIVE_PROCESS_AGE` | 已恢复的已定义项 | `(已删除；基础内容已恢复)` |

### `tools.react_to_message_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `env_var_enabled` | 暂时移动 | `utils` |

### `tools.read_extract`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `MAX_XLSX_BYTES` | 已恢复的已定义项 | `(已删除；基础内容已恢复)` |

### `tools.read_preview_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `READ_PREVIEW_SCHEMA` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `json` | 导入项 | `json` |
| `registry` | 暂时迁移项 | `tools.registry` |
| `tool_error` | 暂时迁移项 | `tools.registry` |

### `tools.read_terminal_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入项 | `json` |

### `tools.read_window_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `json` | 导入项 | `json` |
| `tool_error` | 暂时迁移项 | `tools.registry` |

### `tools.send_message_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `SEND_MESSAGE_SCHEMA` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `re` | 导入项 | `re` |
| `redact_sensitive_text` | 暂时迁移项 | `agent.redact` |
| `time` | 导入项 | `time` |

### `tools.skill_ledger`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `ACTOR_AGENT` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `ACTOR_CURATOR` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `ACTOR_USER` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `tools.skill_linter`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `format_findings` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |
| `has_errors` | 已恢复的被删除项 | `(已删除；基础内容已恢复)` |

### `tools.skill_manager_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `mark_background_review_skill_read` | 暂时迁移项 | `tools.skill_manager_guards` |

### `tools.skill_usage`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `_suppressed_file` | restored-helper | `(已删除；作为 add_suppressed_name 的依赖项被恢复)` |
| `_write_suppressed_names` | restored-helper | `(已删除；作为 add_suppressed_name 的依赖项被恢复)` |
| `add_suppressed_name` | restored-def | `(已删除；基础内容已被恢复)` |
| `agent_created_report` | restored-def | `(已删除；基础内容已被恢复)` |
| `os` | restored-import | `os` |
| `os` | import | `os` |
| `remove_suppressed_name` | restored-def | `(已删除；基础内容已被恢复)` |
| `tempfile` | restored-import | `tempfile` |
| `tempfile` | import | `tempfile` |

### `tools.skillevaluator_scan`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | import | `typing` |
| `SCANNER_NAME` | restored-def | `(已删除；基础内容已被恢复)` |
| `scanner_available` | restored-def | `(已删除；基础内容已被恢复)` |

### `tools.skills_guard`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `full_content_hash` | restored-def | `(已删除；基础内容已被恢复)` |

### `tools.skills_hub`

| name | kind | new location |
|---|---|---|
| `ABC` | import | `abc` |
| `BrowseShSource` | moved-lazy | `tools.skills_hub_sources` |
| `ClawHubSource` | moved-lazy | `tools.skills_hub_clawhub` |
| `GITHUB_TAP_PROVIDERS` | moved-lazy | `tools.skills_hub_github` |
| `GitHubAuth` | moved-lazy | `tools.skills_hub_github` |
| `GitHubSource` | moved-lazy | `tools.skills_hub_github` |
| `HERMES_INDEX_TTL` | moved-lazy | `tools.skills_hub_search` |
| `HERMES_INDEX_URL` | moved-lazy | `tools.skills_hub_search` |
| `HermesIndexSource` | moved-lazy | `tools.skills_hub_official` |
| `LobeHubSource` | moved-lazy | `tools.skills_hub_sources` |
| `OptionalSkillSource` | moved-lazy | `tools.skills_hub_official` |
| `PurePosixPath` | import | `pathlib` |
| `ScanResult` | moved-lazy | `tools.skills_guard` |
| `SkillBundle` | moved-lazy | `tools.skills_hub_models` |
| `SkillMeta` | moved-lazy | `tools.skills_hub_models` |
| `SkillSource` | moved-lazy | `tools.skills_hub_models` |
| `SkillsShSource` | moved-lazy | `tools.skills_hub_skillssh` |
| `TRUSTED_REPOS` | moved-lazy | `tools.skills_guard` |
| `Tuple` | import | `typing` |
| `Union` | import | `typing` |
| `UrlSource` | moved-lazy | `tools.skills_hub_sources` |
| `WellKnownSkillSource` | moved-lazy | `tools.skills_hub_sources` |
| `abstractmethod` | import | `abc` |
| `bundle_content_hash` | moved-lazy | `tools.skills_hub_install` |
| `check_for_skill_updates` | moved-lazy | `tools.skills_hub_install` |
| `content_hash` | moved-lazy | `tools.skills_guard` |
| `create_source_router` | moved-lazy | `tools.skills_hub_search` |
| `dataclass` | import | `dataclasses` |
| `field` | import | `dataclasses` |
| `github_provider_for` | moved-lazy | `tools.skills_hub_github` |
| `hashlib` | import | `hashlib` |
| `install_from_quarantine` | moved-lazy | `tools.skills_hub_install` |
| `is_excluded_skill_path` | moved-lazy | `agent.skill_utils` |
| `os` | import | `os` |
| `parallel_search_sources` | moved-lazy | `tools.skills_hub_search` |
| `quarantine_bundle` | moved-lazy | `tools.skills_hub_install` |
| `quote` | import | `urllib.parse` |
| `re` | import | `re` |
| `shutil` | import | `shutil` |
| `source_url_for_bundle` | moved-lazy | `tools.skills_hub_models` |
| `subprocess` | import | `subprocess` |
| `unified_search` | moved-lazy | `tools.skills_hub_search` |
| `uninstall_skill` | moved-lazy | `tools.skills_hub_install` |
| `unquote` | import | `urllib.parse` |
| `urlparse` | import | `urllib.parse` |
| `urlsplit` | import | `urllib.parse` |
| `urlunparse` | import | `urllib.parse` |
| `windows_hide_flags` | moved-lazy | `hermes_cli._subprocess_compat` |
| `yaml` | import | `yaml` |

### `tools.skills_sync`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `PurePosixPath` | 导入项 | `pathlib` |
| `atomic_replace` | 暂时移动 | `utils` |
| `datetime` | 导入项 | `datetime` |
| `diff_bundled_skill` | 暂时移动 | `tools.skills_sync_bundled_ops` |
| `is_bundled_skills_opt_out` | 恢复为原状 | `(已删除；基础内容已恢复)` |
| `json` | 导入项 | `json` |
| `list_user_modified_bundled_skills` | 暂时移动 | `tools.skills_sync_bundled_ops` |
| `remove_pristine_bundled_skills` | 暂时移动 | `tools.skills_sync_bundled_ops` |
| `reset_bundled_skill` | 暂时移动 | `tools.skills_sync_bundled_ops` |
| `restore_official_optional_skill` | 暂时移动 | `tools.skills_sync_optional` |
| `set_bundled_skills_opt_out` | 暂时移动 | `tools.skills_sync_bundled_ops` |
| `timezone` | 导入项 | `datetime` |

### `tools.skills_sync_client`

| name | kind | new location |
|---|---|---|
| `ARTIFACT_TYPE_SKILL` | moved-lazy | `tools.skills_sync_client_wire` |
| `KIND_COMMIT` | restored-def | `(deleted; BASE body restored)` |
| `KIND_TREE` | restored-def | `(deleted; BASE body restored)` |
| `MODE_DIR` | restored-def | `(deleted; BASE body restored)` |
| `MODE_EXEC` | restored-def | `(deleted; BASE body restored)` |
| `MODE_FILE` | restored-def | `(deleted; BASE body restored)` |
| `SYNC_MANIFEST_ENTRY_NAME` | moved-lazy | `tools.skills_sync_client_wire` |
| `SYNC_MANIFEST_TYPE` | restored-def | `(deleted; BASE body restored)` |
| `SYNC_MANIFEST_VERSION` | moved-lazy | `tools.skills_sync_client_wire` |
| `WIRE_VERSION` | moved-lazy | `tools.skills_sync_client_wire` |
| `canonical_json_bytes` | moved-lazy | `tools.skills_sync_client_wire` |
| `datetime` | import | `datetime` |
| `dev_gate_open` | restored-def | `(deleted; BASE body restored)` |
| `hashlib` | import | `hashlib` |
| `maybe_pull_org_skills` | moved-lazy | `tools.skills_sync_client_org` |
| `org_head_ref` | moved-lazy | `tools.skills_sync_client_org` |
| `org_skill_is_locally_modified` | moved-lazy | `tools.skills_sync_client_org` |
| `org_sync_available` | restored-def | `(deleted; BASE body restored)` |
| `parse_sync_manifest` | moved-lazy | `tools.skills_sync_client_wire` |
| `propose_skill` | moved-lazy | `tools.skills_sync_client_org` |
| `pull_org_skills` | moved-lazy | `tools.skills_sync_client_org` |
| `time` | import | `time` |
| `timezone` | import | `datetime` |
| `user_conflict_ref` | restored-def | `(deleted; BASE body restored)` |
| `wire_address` | moved-lazy | `tools.skills_sync_client_wire` |

### `tools.skills_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Enum` | 导入模块 | `enum` |
| `Set` | 导入模块 | `typing` |
| `display_hermes_home` | 暂时迁移 | `hermes_constants` |
| `env_var_enabled` | 暂时迁移 | `utils` |
| `re` | 导入模块 | `re` |
| `threading` | 导入模块 | `threading` |

### `tools.slash_confirm`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `asyncio` | 导入模块 | `asyncio` |
| `resolve_sync_compat` | 恢复已删除功能 | `(已删除；基础代码已恢复)` |

### `tools.terminal_scope`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `install_refusal_scope` | 恢复已删除功能 | `(已删除；基础代码已恢复)` |
| `terminal_scope` | 恢复已删除功能 | `(已删除；基础代码已恢复)` |

### `tools.terminal_tool`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Path` | 导入模块 | `pathlib` |
| `cleanup_vm` | 暂时移动 | `tools.terminal_tool_lifecycle` |
| `env_var_enabled` | 暂时移动 | `utils` |
| `get_active_env` | 暂时移动 | `tools.terminal_tool_lifecycle` |
| `has_direct_modal_credentials` | 暂时移动 | `tools.tool_backend_helpers` |
| `importlib` | 导入模块 | `importlib.util` |
| `is_interrupted` | 暂时移动 | `tools.interrupt` |
| `is_managed_tool_gateway_ready` | 暂时移动 | `tools.managed_tool_gateway` |
| `is_persistent_env` | 暂时移动 | `tools.terminal_tool_lifecycle` |
| `nous_tool_gateway_unavailable_message` | 暂时移动 | `tools.tool_backend_helpers` |
| `platform` | 导入模块 | `platform` |
| `re` | 导入模块 | `re` |
| `resolve_modal_backend_state` | 暂时移动 | `tools.tool_backend_helpers` |
| `shlex` | 导入模块 | `shlex` |
| `shutil` | 导入模块 | `shutil` |
| `stat` | 导入模块 | `stat` |
| `strip_inert_heredoc_bodies` | 暂时移动 | `tools.shell_heredoc` |
| `subprocess` | 导入模块 | `subprocess` |
| `sys` | 导入模块 | `sys` |

### `tools.tool_result_storage`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `HEREDOC_MARKER` | 恢复原有状态 | `(已删除；基础内容已恢复)` |
| `uuid` | 导入模块 | `uuid` |

### `tools.tool_search`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Literal` | 导入模块 | `typing` |
| `build_catalog_listing` | 已恢复的删除项 | `(已删除；基础内容已恢复)` |
| `copy` | 导入模块 | `copy` |
| `field` | 导入模块 | `dataclasses` |
| `re` | 导入模块 | `re` |
| `snowballstemmer` | 导入模块 | `snowballstemmer` |
| `threading` | 导入模块 | `threading` |

### `tools.transcription_tools`

| name | kind | new location |
|---|---|---|
| `COMMAND_STT_OUTPUT_FORMATS` | moved-lazy | `tools.transcription_command` |
| `COMMON_LOCAL_BIN_DIRS` | moved-lazy | `tools.transcription_common` |
| `DEFAULT_COMMAND_STT_LANGUAGE` | moved-lazy | `tools.transcription_command` |
| `DEFAULT_COMMAND_STT_OUTPUT_FORMAT` | moved-lazy | `tools.transcription_command` |
| `DEFAULT_COMMAND_STT_TIMEOUT_SECONDS` | moved-lazy | `tools.transcription_command` |
| `DEFAULT_LOCAL_STT_LANGUAGE` | moved-lazy | `tools.transcription_common` |
| `ELEVENLABS_STT_BASE_URL` | moved-lazy | `tools.transcription_common` |
| `GROQ_BASE_URL` | moved-lazy | `tools.transcription_common` |
| `GROQ_MODELS` | moved-lazy | `tools.transcription_common` |
| `LOCAL_NATIVE_AUDIO_FORMATS` | moved-lazy | `tools.transcription_common` |
| `MAX_FILE_SIZE` | moved-lazy | `tools.transcription_common` |
| `OPENAI_BASE_URL` | moved-lazy | `tools.transcription_common` |
| `OPENAI_MODELS` | moved-lazy | `tools.transcription_common` |
| `SUPPORTED_FORMATS` | moved-lazy | `tools.transcription_common` |
| `XAI_STT_BASE_URL` | moved-lazy | `tools.transcription_common` |
| `managed_nous_tools_enabled` | moved-lazy | `tools.tool_backend_helpers` |
| `nous_tool_gateway_unavailable_message` | moved-lazy | `tools.tool_backend_helpers` |
| `platform` | import | `platform` |
| `queue` | import | `queue` |
| `re` | import | `re` |
| `resolve_managed_tool_gateway` | moved-lazy | `tools.managed_tool_gateway` |
| `resolve_openai_audio_api_key` | moved-lazy | `tools.tool_backend_helpers` |
| `shlex` | import | `shlex` |
| `subprocess` | import | `subprocess` |
| `tempfile` | import | `tempfile` |
| `urljoin` | import | `urllib.parse` |
| `windows_hide_flags` | moved-lazy | `hermes_cli._subprocess_compat` |

### `tools.tts_tool` 工具

| name | kind | new location |
|---|---|---|
| `AudioDeliveryProfile` | moved-lazy | `tools.tts_tool_delivery` |
| `COMMAND_TTS_OUTPUT_FORMATS` | moved-lazy | `tools.tts_command_provider` |
| `DEFAULT_COMMAND_TTS_MAX_TEXT_LENGTH` | moved-lazy | `tools.tts_command_provider` |
| `DEFAULT_COMMAND_TTS_OUTPUT_FORMAT` | moved-lazy | `tools.tts_command_provider` |
| `DEFAULT_COMMAND_TTS_TIMEOUT_SECONDS` | moved-lazy | `tools.tts_command_provider` |
| `DEFAULT_DEEPINFRA_TTS_VOICE` | moved-lazy | `tools.tts_tool_openai` |
| `DEFAULT_EDGE_VOICE` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_ELEVENLABS_MODEL_ID` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_ELEVENLABS_STREAMING_MODEL_ID` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_ELEVENLABS_VOICE_ID` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_GEMINI_AUDIO_TAGS` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_GEMINI_TTS_BASE_URL` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_GEMINI_TTS_MODEL` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_GEMINI_TTS_VOICE` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_KITTENTTS_MODEL` | moved-lazy | `tools.tts_tool_local` |
| `DEFAULT_KITTENTTS_VOICE` | moved-lazy | `tools.tts_tool_local` |
| `DEFAULT_MINIMAX_BASE_URL` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_MINIMAX_CN_BASE_URL` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_MINIMAX_MODEL` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_MINIMAX_VOICE_ID` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_MISTRAL_TTS_MODEL` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_MISTRAL_TTS_VOICE_ID` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_OPENAI_BASE_URL` | moved-lazy | `tools.tts_tool_openai` |
| `DEFAULT_OPENAI_MODEL` | moved-lazy | `tools.tts_tool_openai` |
| `DEFAULT_OPENAI_VOICE` | moved-lazy | `tools.tts_tool_openai` |
| `DEFAULT_PIPER_VOICE` | moved-lazy | `tools.tts_tool_local` |
| `DEFAULT_XAI_AUTO_SPEECH_TAGS` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_BASE_URL` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_BIT_RATE` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_LANGUAGE` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_OPTIMIZE_STREAMING_LATENCY_DEFAULT` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_SAMPLE_RATE` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_SPEED_DEFAULT` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_SPEED_MAX` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_SPEED_MIN` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_TEXT_NORMALIZATION_DEFAULT` | moved-lazy | `tools.tts_tool_providers` |
| `DEFAULT_XAI_VOICE_ID` | moved-lazy | `tools.tts_tool_providers` |
| `ELEVENLABS_MODEL_MAX_TEXT_LENGTH` | moved-lazy | `tools.tts_tool_delivery` |
| `FALLBACK_MAX_TEXT_LENGTH` | moved-lazy | `tools.tts_tool_delivery` |
| `FALLBACK_MAX_TEXT_LENGTH` | restored-helper | `(deleted; restored as a dependency of MAX_TEXT_LENGTH)` |
| `Future` | import | `concurrent.futures` |
| `GEMINI_AUDIO_TAG_REWRITE_TASK` | moved-lazy | `tools.tts_tool_providers` |
| `GEMINI_TTS_CHANNELS` | restored-def | `(deleted; BASE body restored)` |
| `GEMINI_TTS_SAMPLE_RATE` | restored-def | `(deleted; BASE body restored)` |
| `GEMINI_TTS_SAMPLE_WIDTH` | restored-def | `(deleted; BASE body restored)` |
| `Iterator` | import | `typing` |
| `MANAGED_OPENAI_TTS_MODELS` | moved-lazy | `tools.tts_tool_openai` |
| `MAX_TEXT_LENGTH` | restored-def | `(deleted; BASE body restored)` |
| `PROVIDER_MAX_TEXT_LENGTH` | moved-lazy | `tools.tts_tool_delivery` |
| `TTS_RESPONSE_BODY_CHUNK_BYTES` | moved-lazy | `tools.tts_tool_providers` |
| `TTS_RESPONSE_BODY_LIMIT_BYTES` | moved-lazy | `tools.tts_tool_providers` |
| `ThreadPoolExecutor` | import | `concurrent.futures` |
| `Tuple` | import | `typing` |
| `acquire_tts_lease` | moved-lazy | `tools.tts_tool_lifecycle` |
| `base64` | import | `base64` |
| `dataclass` | import | `dataclasses` |
| `field` | import | `dataclasses` |
| `hermes_xai_user_agent` | moved-lazy | `tools.xai_http` |
| `managed_nous_tools_enabled` | moved-lazy | `tools.tool_backend_helpers` |
| `nous_tool_gateway_unavailable_message` | moved-lazy | `tools.tool_backend_helpers` |
| `platform` | import | `platform` |
| `queue` | import | `queue` |
| `re` | import | `re` |
| `read_selection` | moved-lazy | `tools.tool_backend_helpers` |
| `release_tts_lease` | moved-lazy | `tools.tts_tool_lifecycle` |
| `release_tts_provider` | moved-lazy | `tools.tts_tool_lifecycle` |
| `resolve_managed_tool_gateway` | moved-lazy | `tools.managed_tool_gateway` |
| `resolve_openai_audio_api_key` | moved-lazy | `tools.tool_backend_helpers` |
| `selection_error` | moved-lazy | `tools.tool_backend_helpers` |
| `shlex` | import | `shlex` |
| `shutil` | import | `shutil` |
| `stream_tts_to_speaker` | moved-lazy | `tools.tts_tool_speaker` |
| `subprocess` | import | `subprocess` |
| `threading` | import | `threading` |
| `time` | import | `time` |
| `tts_lease_holders` | moved-lazy | `tools.tts_tool_lifecycle` |
| `urljoin` | import | `urllib.parse` |
| `urlparse` | import | `urllib.parse` |
| `uuid` | import | `uuid` |
| `warm_tts_provider` | moved-lazy | `tools.tts_tool_lifecycle` |
| `windows_hide_flags` | moved-lazy | `hermes_cli._subprocess_compat` |

### `tools.url_safety`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `has_sensitive_query_params` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |
| `ssrf_safe_async_http_transport` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |
| `ssrf_safe_http_transport` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |

### `tools.vision_tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `contextlib` | 导入模块 | `contextlib` |
| `sys` | 导入模块 | `sys` |
| `threading` | 导入模块 | `threading` |

### `tools.voice_mode`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEFAULT_TTS_ECHO_SIMILARITY_THRESHOLD` | 拖延移动项 | `tools.voice_mode_transcript` |
| `DEFAULT_VOICE_STOP_PHRASES` | 拖延移动项 | `tools.voice_mode_transcript` |
| `MIN_FRAGMENT_LENGTH_FOR_ECHO` | 拖延移动项 | `tools.voice_mode_transcript` |
| `WHISPER_HALLUCINATIONS` | 已恢复的已删除项 | `(已删除；基础内容已恢复)` |
| `difflib` | 导入模块 | `difflib` |
| `is_tts_echo` | 拖延移动项 | `tools.voice_mode_transcript` |
| `re` | 导入模块 | `re` |
| `voice_stop_hint` | 拖延移动项 | `tools.voice_mode_transcript` |

### `tools.web_result_cache`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Any` | 导入模块 | `typing` |
| `List` | 导入模块 | `typing` |

### `tools.web_tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `DEFAULT_EXTRACT_CHAR_LIMIT` | 已延迟移动 | `tools.web_tools_truncate` |
| `Dict` | 导入项 | `typing` |
| `Firecrawl` | 已延迟移动 | `plugins.web.firecrawl.provider` |
| `MAX_STORED_TEXT_CHARS` | 已延迟移动 | `tools.web_tools_truncate` |
| `TYPE_CHECKING` | 导入项 | `typing` |
| `asyncio` | 导入项 | `asyncio` |
| `build_vendor_gateway_url` | 已延迟移动 | `tools.managed_tool_gateway` |
| `httpx` | 导入项 | `httpx` |
| `managed_nous_tools_enabled` | 已延迟移动 | `tools.tool_backend_helpers` |
| `normalize_url_for_request` | 已延迟移动 | `tools.url_safety` |
| `nous_tool_gateway_unavailable_message` | 已延迟移动 | `tools.tool_backend_helpers` |
| `prefers_gateway` | 已延迟移动 | `tools.tool_backend_helpers` |
| `re` | 导入项 | `re` |
| `resolve_managed_tool_gateway` | 已延迟移动 | `tools.managed_tool_gateway` |
| `sensitive_query_param_name` | 已延迟移动 | `tools.url_safety` |
| `sys` | 导入项 | `sys` |

### `tools.website_policy`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `invalidate_cache` | 已恢复定义 | `(已删除；基础内容已恢复)` |

### `tools.write_approval`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `is_background` | 已恢复定义 | `(已删除；基础内容已恢复)` |

### `tools.yuanbao_tools`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `List` | 导入项 | `typing` |
| `Optional` | 导入项 | `typing` |

### `toolsets`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `resolve_multiple_toolsets` | 已恢复定义 | `(已删除；基础内容已恢复)` |
### `tui_gateway.compute_host`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `HostSession` | 已恢复的缺失项 | `(已删除；恢复了基础内容)` |
| `SpikeAgent` | 已恢复的辅助项 | `(已删除；作为 HostSession 的依赖项被恢复)` |
| `SpikeAgent` | 已恢复的缺失项 | `(已删除；恢复了基础内容)` |
| `dataclass` | 已恢复的导入项 | `dataclasses` |
| `dataclass` | 导入项 | `dataclasses` |
| `field` | 已恢复的导入项 | `dataclasses` |
| `field` | 导入项 | `dataclasses` |
| `request_hard_interrupt` | 延迟移动项 | `agent.interrupt_compat` |

### `tui_gateway.hosted_room_driver`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `contextlib` | 导入项 | `contextlib` |
| `null_turn_lock` | 已恢复的缺失项 | `(已删除；恢复了基础内容)` |

### `tui_gateway.hosted_room_service`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `hashlib` | 导入项 | `hashlib` |

### `tui_gateway.mcp_rpc_helpers`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `Optional` | 导入项 | `typing` |
| `Tuple` | 导入项 | `typing` |
| `resolve_profile` | 已恢复的缺失项 | `(已删除；恢复了基础内容)` |

### `tui_gateway.methods_browser_control`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `BROWSER_CONTROL_PROTOCOL_VERSION` | 延迟移动项 | `gateway.browser_control_broker` |
| `browser_control_protocol_supported` | 延迟移动项 | `gateway.browser_control_broker` |
| `filter_browser_control_capabilities` | 延迟移动项 | `gateway.browser_control_broker` |

### `tui_gateway.methods_prompt`

| 名称 | 类型 | 新位置 |
|---|---|---|
| `types` | 导入模块 | `types` |
