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

## 必需的凭据

请在 `~/.hermes/.env` 文件中设置这些凭据（也可通过 `hermes tools` 进行设置）：

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

若缺少 SDK 或凭证，钩子函数将静默地执行无操作——从而导致插件无法正常启动。

## 验证

```bash
hermes plugins list                 # observability/langfuse should show "enabled"
hermes chat -q "hello"              # then check Langfuse for a "Hermes turn" trace
```

## 可选配置调整

```bash
HERMES_LANGFUSE_ENV=production       # environment tag
HERMES_LANGFUSE_RELEASE=v1.0.0       # release tag
HERMES_LANGFUSE_SAMPLE_RATE=0.5      # sample 50% of traces
HERMES_LANGFUSE_MAX_CHARS=12000      # max chars per field (default: 12000)
HERMES_LANGFUSE_DEBUG=true           # verbose plugin logging
```

## 禁用

```bash
hermes plugins disable observability/langfuse
```
