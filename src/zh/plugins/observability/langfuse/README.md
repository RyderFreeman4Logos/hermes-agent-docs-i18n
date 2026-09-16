# Langfuse 可观测性插件

该插件随 Hermes 一同提供，但属于**可选启用**类型——仅当您明确开启它时才会被加载。

## 启用方式

请选择其中一种：

```bash
# Interactive: walks you through credentials + SDK install + enable
hermes tools  # → Langfuse Observability

# Manual
pip install langfuse
hermes plugins enable observability/langfuse
```

## 必需的凭证

请在 `~/.hermes/.env` 文件中设置这些凭证（也可通过 `hermes tools` 进行设置）：

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

若缺少 SDK 或凭证，钩子函数将静默地不执行任何操作——从而导致插件无法正常启动。

## 验证

```bash
hermes plugins list                 # observability/langfuse should show "enabled"
hermes chat -q "hello"              # then check Langfuse for a "Hermes turn" trace
```

若提供方使用独立的 `system` 参数（如 Anthropic Messages API），生成内容中将会包含 Hermes 系统提示词。您可以打开相应的 **LLM 调用** 子跨度，查看 `role: system` 的内容（该内容会因 `HERMES_LANGFUSE_MAX_CHARS` 设置而被截断）。

## 可选配置调整

```bash
HERMES_LANGFUSE_ENV=production       # environment tag
HERMES_LANGFUSE_RELEASE=v1.0.0       # release tag
HERMES_LANGFUSE_SAMPLE_RATE=0.5      # sample 50% of traces
HERMES_LANGFUSE_MAX_CHARS=12000      # max chars per field (default: 12000)
HERMES_LANGFUSE_CAPTURE=sanitized    # content capture mode (see below)
HERMES_LANGFUSE_DEBUG=true           # verbose plugin logging
```

## 捕获模式

`HERMES_LANGFUSE_CAPTURE`用于控制要导出的*内容*量（提示词、响应、工具参数/结果等）。而结构化元数据——如ID、角色、工具名称、令牌使用情况、成本及耗时——在所有模式下都会被完整捕获。

| 模式 | 行为说明 |
|------|----------|
| `metadata` | 不导出任何内容。每个内容字段会被替换为一个形状/长度占位符（`{"omitted": true, "type": "text", "chars": N}`）。 |
| `sanitized` | **（默认值）** 先对敏感信息进行模式化遮蔽处理（如API密钥、令牌、JWT、私钥以及以`password=`开头的字段），然后再进行内容截断。遮蔽操作在截断之前执行。 |
| `full` | 导出原始内容，仅进行截断处理。需手动启用此模式——此时追踪记录将包含对话中的所有内容，包括注入的内存数据及文件内容。 |

当前激活的模式会作为`metadata.capture_mode`字段记录在每个追踪日志中。

注意：`sanitized`模式属于基于模式的纵深防御措施，并不能完全保证数据防泄露效果。对于个人会话或共享的Langfuse项目，建议使用`metadata`模式。

## 错误与关闭处理机制

- 模型请求失败时（通过`api_request_error`钩子），系统会以`level=ERROR`、状态码、重试计数器以及经过捕获模式处理后的错误信息来结束该次生成过程。那些无法自动重试的错误也会导致当前对话轮次终止。
- 会话结束或手动终止时，系统会关闭该会话下所有尚未处理的追踪记录，并清空队列中的事件，从而避免出现中断或仅包含工具操作的对话轮次悬而未决的情况。

## 禁用功能

```bash
hermes plugins disable observability/langfuse
```
