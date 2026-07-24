# 提供商与模型别名

可通过 `hermes model`（选择器）或 `hermes setup` 进行设置。35 种以上的供应商配置以插件形式存在于 `plugins/model-providers/` 目录下；用户自定义的同名插件会优先生效。完整文档请参阅：https://hermes-agent.nousresearch.com/docs/integrations/providers

### 提供商列表

| 提供商 | 认证方式 | 关键环境变量 |
|--------|----------|--------------|
| openrouter | API 密钥 | `OPENROUTER_API_KEY` |
| anthropic | API 密钥 | `ANTHROPIC_API_KEY`（也可使用 `CLAUDE_CODE_OAUTH_TOKEN`） |
| nous | OAuth 设备码认证 | `hermes auth add nous`（或 `NOUS_API_KEY`） |
| openai-codex | OAuth 认证 | `hermes auth add openai-codex` |
| qwen-oauth | OAuth 认证 | `hermes auth add qwen-oauth` |
| minimax-oauth | OAuth 认证 | `hermes auth add minimax-oauth` |
| copilot | 令牌认证 | `COPILOT_GITHUB_TOKEN` / `GH_TOKEN`（Copilot 设备流式认证——使用 `gh auth login` 获取的令牌无效） |
| copilot-acp | 外部 CLI | PATH 路径下的 Copilot CLI，或指定 `COPILOT_CLI_PATH` |
| gemini | API 密钥 | `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` |
| xai | API 密钥 | `XAI_API_KEY`（也支持 SuperGrok OAuth 认证） |
| deepseek | API 密钥 | `DEEPSEEK_API_KEY` |
| zai (GLM) | API 密钥 | `GLM_API_KEY` / `ZAI_API_KEY` |
| minimax / minimax-cn | API 密钥 | `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY` |
| kimi-coding / -cn | API 密钥 | `KIMI_API_KEY` / `KIMI_CN_API_KEY` |
| alibaba (+coding-plan) | API 密钥 | `DASHSCOPE_API_KEY` / `ALIBABA_CODING_PLAN_API_KEY` |
| xiaomi | API 密钥 | `XIAOMI_API_KEY` |
| huggingface | 令牌认证 | `HF_TOKEN` |
| fireworks / novita / nvidia / deepinfra / gmi / arcee / stepfun / upstage / kilocode / opencode-zen / opencode-go / ollama-cloud | API 密钥 | `<NAME>_API_KEY` |
| bedrock / vertex / azure-foundry | 云 SDK / 密钥认证 | AWS SDK 凭据 / Vertex ADC / `AZURE_FOUNDRY_API_KEY` |
| 自定义供应商 | 配置文件 | 在 config.yaml 中设置 `model.base_url` 和 `model.api_key` |

每个供应商池可配置多个凭证，并会自动轮换（通过 `hermes auth` 实现）。当主凭证失效时，可使用 `hermes fallback add|remove|list` 设置备用凭证链。

### 用户自定义模型别名

可在 CLI 及所有网关平台上使用 `/model <name>` 形式调用。别名解析由 `hermes_cli/model_switch.py::resolve_alias()` 函数完成；用户自定义的别名会优先于内置别名被识别，因此用户定义的 `sonnet`/`grok` 别名可覆盖内置的对应别名。

```yaml
# Full form
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  local-qwen:
    model: qwen3.5:397b
    provider: custom
    base_url: "https://ollama.com/v1"

# Short form ("provider/model"), also via CLI:
#   hermes config set model.aliases.fav openrouter/anthropic/claude-sonnet-4.6
model:
  aliases:
    fav: openrouter/anthropic/claude-sonnet-4.6
```

`/model fav` — 该命令为会话级操作；如需将其设为默认值，可添加 `--global` 参数。

内置别名（根据当前使用的提供者自动匹配对应模型）包括：`sonnet`、`opus`、`haiku`、`claude`、`gpt5`、`gpt`、`codex`、`o3`、`o4`、`gemini`、`deepseek`、`grok`、`llama`、`qwen`、`minimax`、`nemotron`、`kimi`、`glm`、`step`、`mimo`、`trinity`。
