# 提供者与模型别名

可通过 `hermes model`（选择器）或 `hermes setup` 进行设置。35 种以上的提供者配置以插件形式存在于 `plugins/model-providers/` 目录下；同名用户自定义插件将优先生效。完整文档请参阅：https://hermes-agent.nousresearch.com/docs/integrations/providers

### 提供者

| Provider | Auth | Key env var(s) |
|----------|------|----------------|
| openrouter | API key | `OPENROUTER_API_KEY` |
| anthropic | API key | `ANTHROPIC_API_KEY` (also `CLAUDE_CODE_OAUTH_TOKEN`) |
| nous | OAuth device code | `hermes auth add nous` (or `NOUS_API_KEY`) |
| openai-codex | OAuth | `hermes auth add openai-codex` |
| qwen-oauth | OAuth | `hermes auth add qwen-oauth` |
| minimax-oauth | OAuth | `hermes auth add minimax-oauth` |
| copilot | Token | `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` (Copilot device flow — `gh auth login` tokens do NOT work) |
| copilot-acp | External CLI | Copilot CLI on PATH or `COPILOT_CLI_PATH` |
| gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| xai | API key | `XAI_API_KEY` (SuperGrok OAuth also supported) |
| deepseek | API key | `DEEPSEEK_API_KEY` |
| zai (GLM) | API key | `GLM_API_KEY` / `ZAI_API_KEY` |
| minimax / minimax-cn | API key | `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY` |
| kimi-coding / -cn | API key | `KIMI_API_KEY` / `KIMI_CN_API_KEY` |
| alibaba (+coding-plan) | API key | `DASHSCOPE_API_KEY` / `ALIBABA_CODING_PLAN_API_KEY` |
| xiaomi | API key | `XIAOMI_API_KEY` |
| huggingface | Token | `HF_TOKEN` |
| fireworks / novita / nvidia / deepinfra / gmi / arcee / stepfun / upstage / kilocode / ai-gateway / opencode-zen / opencode-go / ollama-cloud | API key | `<NAME>_API_KEY` |
| bedrock / vertex / azure-foundry | Cloud SDK / key | AWS SDK creds / Vertex ADC / `AZURE_FOUNDRY_API_KEY` |
| custom | Config | `model.base_url` + `model.api_key` in config.yaml |

每个提供者池可配置多个凭证，并能自动轮换（使用命令 `hermes auth` 实现）。当主提供者出现故障时，可启用备用提供者链：通过命令 `hermes fallback add|remove|list` 操作。

### 用户自定义模型别名

在 CLI 及各类网关平台中，均可通过 `/model <name>` 来使用自定义模型别名。这些别名由 `hermes_cli/model_switch.py::resolve_alias()` 函数进行解析；系统会优先检查用户定义的别名，因此用户自定义的 `sonnet`/`grok` 等别名会覆盖内置的对应模型。

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
  theta:
    model: theta-1
    provider: custom
    base_url: "https://theta.example.com/v1"
    key_env: THETA_API_KEY        # or: api_key: "${THETA_API_KEY}"

# Short form ("provider/model"), also via CLI:
#   hermes config set model.aliases.fav openrouter/anthropic/claude-sonnet-4.6
model:
  aliases:
    fav: openrouter/anthropic/claude-sonnet-4.6
```

`/model fav` — 该指令为会话级操作；如需将其设为默认值，需添加 `--global` 参数。

拥有独立 `base_url` 的别名会使用自身的认证凭证进行身份验证（即 `api_key`，该参数也支持使用 `"${VAR}"` 形式的变量引用，或是 `key_env`）。若未设置上述任一参数，则认证密钥将从对应别名的 HOST 中获取，而不会继承自切换前的原服务提供方。

内置别名（根据当前激活的服务提供方从目录中确定）包括：`sonnet`、`opus`、`haiku`、`claude`、`gpt5`、`gpt`、`codex`、`o3`、`o4`、`gemini`、`deepseek`、`grok`、`llama`、`qwen`、`minimax`、`nemotron`、`kimi`、`glm`、`step`、`mimo`、`trinity`。
