---
title: "Openhands — Delegate coding to OpenHands CLI (model-agnostic, LiteLLM)"
sidebar_label: "Openhands"
description: "Delegate coding to OpenHands CLI (model-agnostic, LiteLLM)"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Openhands

将编程任务委托给 OpenHands CLI（支持多种模型，基于 LiteLLM 架构）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/autonomous-ai-agents/openhands` 命令安装 |
| 路径 | `optional-skills/autonomous-ai-agents\openhands` |
| 版本 | `0.1.0` |
| 开发者 | Tim Koepsel (xzessmedia)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos |
| 标签 | `Coding-Agent`、`OpenHands`、`Model-Agnostic`、`LiteLLM` |
| 相关技能 | [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code)、[`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex)、[`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode)、[`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能启用后，智能体将看到这些内容作为指令。
:::

# OpenHands CLI

通过 `terminal` 工具将编程任务委托给 [OpenHands CLI](https://github.com/All-Hands-AI/OpenHands)。OpenHands 不限制模型类型：任何支持 LiteLLM 的服务提供商（如 OpenAI、Anthropic、OpenRouter、DeepSeek、Ollama、vLLM 等）均可使用。

该技能是用于批量/单次任务委托的无界面模式封装工具，Hermes本身并不使用交互式文本用户界面。

## 适用场景

- 用户希望将编程任务专门委托给OpenHands处理。
- 用户需要能够在非Anthropic/非OpenAI提供商平台（如DeepSeek、Qwen、Ollama、vLLM、Nous等）上运行的编程智能体——其姊妹技能`claude-code`和`codex`仅适用于特定供应商的平台。
- 需要在工作空间内进行多步骤文件编辑并配合Shell命令操作。

若使用Claude原生平台，建议选择`claude-code`；若使用OpenAI原生平台，则推荐`codex`；而对于Hermes原生的子智能体，应使用`delegate_task`。

## 先决条件

1. 需先安装上游依赖项（要求Python 3.12及以上版本以及`uv`工具）：

   ```
   terminal(command="uv tool install openhands --python 3.12")
   ```

验证方式：执行 `openhands --version` 命令（本文撰写时当前版本为 `OpenHands CLI 1.16.0` / `SDK v1.21.0`）。 

2. 选择模型，并为 `--override-with-envs` 参数设置环境变量：

   ```
   export LLM_MODEL=openrouter/openai/gpt-4o-mini       # or any LiteLLM slug
   export LLM_API_KEY=$OPENROUTER_API_KEY
   export LLM_BASE_URL=https://openrouter.ai/api/v1     # omit for native OpenAI
   ```

`LLM_MODEL` 参数需使用 LiteLLM 的完整标识符。当服务提供商为 OpenRouter 时，该标识符需添加双重前缀，格式为 `openrouter/<供应商>/<模型名>`（例如 `openrouter/anthropic/claude-sonnet-4.5`）。对于原生 Anthropic 模型，标识符格式为 `anthropic/claude-sonnet-4-5`；而对于原生 OpenAI 模型，则为 `openai/gpt-4o-mini`。

3. 如需隐藏启动横幅，避免 JSON 输出前出现 ASCII 艺术图案，可进行相应设置：

   ```
   export OPENHANDS_SUPPRESS_BANNER=1
   ```

## 运行方式

请始终通过 `terminal` 工具来调用该代理。如需实现自动化操作，务必添加 `--headless --json --override-with-envs --exit-without-confirmation` 参数。

### 单次任务

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openrouter/openai/gpt-4o-mini LLM_API_KEY=$OPENROUTER_API_KEY LLM_BASE_URL=https://openrouter.ai/api/v1 openhands --headless --json --override-with-envs --exit-without-confirmation -t 'Add error handling to all API calls in src/'",
  workdir="/path/to/project",
  timeout=600
)
```

### 长时间任务的相关背景说明

```
terminal(command="<same as above>", workdir="/path/to/project", background=true, notify_on_complete=true)
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
```

### 恢复之前的对话

每次运行结束后，OpenHands 会输出 `Conversation ID: <32位十六进制字符串>`，以及一行提示信息 `Hint: openhands --resume <带连字符的UUID>`。请使用带连字符的UUID格式来恢复对话：

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=... openhands --headless --json --override-with-envs --exit-without-confirmation --resume <dashed-uuid> -t 'Now fix the bug you found'",
  workdir="/path/to/project"
)
```

## 实际可用参数列表

已通过 `openhands --help`（CLI 1.16.0 版本）进行验证。表格中未列出的参数均不属于有效参数——请通过环境变量或配置文件来传入。

| 参数 | 效果 |
|------|------|
| `--headless` | 禁用用户界面，必须配合 `-t` 或 `-f` 使用。此模式下会自动批准所有操作（无需使用 `--llm-approve`）。 |
| `--json` | 以 JSONL 格式输出事件流（需配合 `--headless` 使用）。 |
| `-t TEXT` | 任务提示语。 |
| `-f PATH` | 从文件中读取任务内容。 |
| `--resume [ID]` | 恢复对话。若未指定 ID，则列出最近的对话记录。 |
| `--last` | 恢复最近的一次对话（需配合 `--resume` 使用）。 |
| `--override-with-envs` | 使用 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` 环境变量来覆盖默认值。若未启用此选项，OpenHands 将读取 `~/.openhands/settings.json` 中的配置并忽略环境变量设置。 |
| `--exit-without-confirmation` | 不显示“您确定要退出吗？”的确认对话框。 |
| `--always-approve` / `--yolo` | 自动批准所有操作（`--headless` 模式下的默认行为）。 |
| `--llm-approve` | 基于大语言模型的安全审核机制（仅支持交互模式，在无界面模式下无效）。 |
| `--version` / `-v` | 显示版本信息后退出。 |

**不存在 `--model`、`--max-iterations`、`--workspace`、`--sandbox`、`--sandbox-type` 这些参数。** 模型参数对应 `LLM_MODEL`；工作空间即为传递给 `terminal` 工具的 `workdir` 路径；沙箱/运行环境则由 `RUNTIME` 和 `SANDBOX_VOLUMES` 环境变量控制。

## JSON 事件格式规范

通过使用 `--json --headless` 参数，OpenHands 会以 JSONL 格式输出数据——即每行一个 JSON 对象，此外还包含少量非 JSON 格式的状态行（如 `Initializing agent...`、`Agent is working`、`Agent finished`、最终总结框、`Goodbye!`、`Conversation ID:`、`Hint:`）。可通过筛选以 `{` 开头的行来获取所需数据。

顶层的 `kind` 字段用于区分不同类型的事件：

- `MessageEvent`——表示用户或智能体的文本轮次。其 `source` 字段的值为 `user` 或 `agent`。
- `ActionEvent`——表示智能体选择了某个工具。可查看 `tool_name`（如 `file_editor`、`terminal`、`finish`）以及 `action.kind`（如 `FileEditorAction`、`TerminalAction`、`FinishAction`）。
- `ObservationEvent`——表示工具的执行结果。`observation.is_error` 字段用于标识操作是否成功，其 `source` 字段的值为 `environment`。
- `ActionEvent` 中的 `FinishAction` 会通过 `action.message` 字段携带智能体的最终消息。

该命令行工具会首先输出 LiteLLM 和 Authlib 产生的所有标准错误信息——详情请参阅“注意事项”部分。实际解析时应仅处理标准输出内容，并逐行筛选，忽略那些不以 `{` 开头的行。

## 注意事项

- **每次调用都会出现 LiteLLM 警告信息。**由于未安装 `botocore`，命令行工具会将 `bedrock-runtime` 和 `sagemaker-runtime` 相关的警告信息输出到标准错误流中，同时还会出现 Authlib 的过时警告。这些都属于冗余信息，并非真正的错误。可在将错误信息展示给用户之前，将其重定向至 `/dev/null` 或直接过滤掉。
- **广告横幅干扰。**如果不设置 `OPENHANDS_SUPPRESS_BANNER=1`，每次运行都会以一个多行的 `+--+` ASCII 格式横幅开始，用于宣传该 SDK。建议始终设置该环境变量以避开此干扰。
- **在自动化场景中，`--override-with-envs` 是必需参数。** 若未使用该参数，OpenHands 会忽略 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL` 这些设置，转而使用 `~/.openhands/settings.json` 中的配置。在首次安装时该文件并不存在，因此 CLI 会一直挂起，等待首次运行时的设置流程。
- **模型标识符属于 LiteLLM，而非提供方。** 使用 `openrouter/openai/gpt-4o-mini` 可以正常工作；而尽管指向 OpenRouter，使用 `openai/gpt-4o-mini` 却无法生效。`anthropic/claude-sonnet-4-5`（使用连字符）是直接来自 Anthropic 的模型；而 `openrouter/anthropic/claude-sonnet-4.5`（使用点号）则是通过 OpenRouter 获取的。如果选择错误，将会出现难以理解的 LiteLLM 400 错误。
- **`pip install openhands-ai` 是错误的包名。** 那是旧版的 V0 SDK。新的 CLI 命令应为 `uv tool install openhands --python 3.12`。目前并没有得到维护的 conda 版本。
- **会话 ID 的格式较为复杂。** CLI 会先输出 `Conversation ID: f46573d9cfdb45e492ca189bde40019b`（不含连字符），随后再显示 `Hint: openhands --resume f46573d9-cfdb-45e4-92ca-189bde40019b`（含连字符）。请务必使用带连字符的格式。
- **无界面模式会忽略 `--llm-approve` 参数。** 若尝试传入该参数，将会引发 argparse 错误。无界面模式会强制设置为始终批准的状态。
- **上游版本不支持 Windows 系统。** OpenHands 的文档要求在 Windows 上使用 WSL 环境，因此该技能被限制在 `[linux, macos]` 平台上使用。
- **`~/.openhands/conversations/<id>/` 目录会持续积累数据。** 每次运行都会在该目录下保存对应的轨迹信息。如果需要批量处理任务，请及时清理该目录中的旧数据。
- **安装体积较大（约 200 个包）。** 建议使用 `uv tool install`（在隔离的虚拟环境中安装），以避免与当前项目中的依赖项发生冲突。

## 验证

```
terminal(
  command="OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openrouter/openai/gpt-4o-mini LLM_API_KEY=$OPENROUTER_API_KEY LLM_BASE_URL=https://openrouter.ai/api/v1 openhands --headless --json --override-with-envs --exit-without-confirmation -t 'Print the string OPENHANDS_OK to stdout via the terminal tool.'",
  workdir="/tmp",
  timeout=120
)
```

如果 JSONL 数据流的末尾是一个 `FinishAction`，且其 `action.message` 中包含 `OPENHANDS_OK` 字样，则说明安装过程已成功完成。

## 相关资源

- [OpenHands GitHub 仓库](https://github.com/All-Hands-AI/OpenHands)
- [OpenHands CLI 命令参考手册](https://docs.openhands.dev/openhands/usage/cli/command-reference)
- 相关技能：`claude-code`（仅支持 Anthropic）、`codex`（仅支持 OpenAI）、`opencode`（通过 OpenCode 支持多提供商）、`hermes-agent`（通过 `delegate_task` 实现的 Hermes 子智能体）。
