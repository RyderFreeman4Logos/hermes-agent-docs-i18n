---
sidebar_position: 16
title: "Google Gemini"
description: "Use Hermes Agent with Google Gemini — native AI Studio API, API-key setup, OAuth option, tool calling, streaming, and quota guidance"
---

# Google Gemini

Hermes Agent 支持将 Google Gemini 作为原生提供商使用，通过 **Google AI Studio / Gemini API** 进行连接——而非兼容 OpenAI 的接口。这样一来，Hermes 能够将其内部的 OpenAI 风格消息处理与工具调用机制转换为 Gemini 原生的 `generateContent` API，同时保留工具调用、流式处理、多模态输入以及 Gemini 特有的响应元数据功能。

此外，Hermes 还支持另一种独立的 **Google Gemini (OAuth)** 提供商，该版本使用与 Google Gemini CLI 相同的 Cloud Code Assist 后端。如需风险最低的官方 API 访问方式，请使用 API 密钥提供商（`gemini`）。

## 前提条件

- **Google AI Studio API 密钥**——可在 [aistudio.google.com/apikey](https://aistudio.google.com/apikey) 处创建；
- **已启用计费的 Google Cloud 项目**——强烈建议用于部署 Agent，因为 Gemini 的免费套餐容量有限，无法支持长时间运行的 Agent 会话，而 Hermes 在每次用户交互中可能会多次调用模型；
- **已安装 Hermes**——对于原生 Gemini 提供商，无需额外安装任何 Python 包。

:::提示 API 密钥设置方式
请设置 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`。Hermes 会同时检查这两个名称以识别 `gemini` 提供商。
:::

## 快速入门

```bash
# Add your Gemini API key
echo "GOOGLE_API_KEY=..." >> ~/.hermes/.env

# Select Gemini as your provider
hermes model
# → Choose "More providers..." → "Google AI Studio"
# → Hermes checks your key tier and shows Gemini models
# → Select a model

# Start chatting
hermes chat
```

如果您更倾向于直接编辑配置，可使用原生的 Gemini API 基础地址：

```yaml
model:
  default: gemini-3-flash-preview
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

## 配置

运行 `hermes model` 后，您的 `~/.hermes/config.yaml` 文件中将包含以下内容：

```yaml
model:
  default: gemini-3-flash-preview
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

在 `~/.hermes/.env` 文件中：

```bash
GOOGLE_API_KEY=...
```

### 原生 Gemini API

推荐的接口地址为：

```text
https://generativelanguage.googleapis.com/v1beta
```

Hermes会检测到该端点，并为其创建专用的Gemini适配器。在内部，Hermes仍以类似OpenAI的消息格式维持代理循环，随后将每个请求转换为Gemini的原生架构：

- `messages[]` → Gemini的`contents[]`
- 系统提示语 → Gemini的`systemInstruction`
- 工具结构定义 → Gemini的`functionDeclarations`
- 工具执行结果 → Gemini的`functionResponse`部分
- 流式响应 → 用于Hermes循环的类似OpenAI格式的流式数据块

:::注意 Gemini 3的思维签名
在支持Gemini 3工具时，Hermes会保留函数调用部分附带的`thoughtSignature`值，并在后续工具执行阶段重新使用这些值。这有助于确保多步骤代理工作流的验证流程正常运行。

Gemini 3也可能为其他响应部分添加思维签名。由于Hermes的专用适配器目前主要针对代理工具循环进行优化，因此还无法以完整的字段级精度重新呈现所有非函数调用部分的签名。
:::

### 建议使用原生端点
Google还提供了一个兼容OpenAI的端点：

```text
https://generativelanguage.googleapis.com/v1beta/openai/
```

对于 Hermes Agent 会话，建议优先使用上述原生 Gemini 端点。Hermes 内置了原生 Gemini 适配器，能够将多轮对话中的工具使用、工具调用结果、流式数据、多模态输入以及 Gemini 的响应元数据直接映射到 Gemini 的 `generateContent` API 中。而当您确实需要 OpenAI API 兼容性时，兼容 OpenAI 的端点依然十分有用。

如果您之前将 `GEMINI_BASE_URL` 设置为 `/openai` 地址，请将其删除或进行更改：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

### OAuth 提供商

Hermes 还支持 `google-gemini-cli` 这一提供商：

```bash
hermes model
# → Choose "Google Gemini (OAuth)"
```

该功能采用浏览器 PKCE 登录方式，并依托 Cloud Code Assist 后端。对于希望使用类似 Gemini CLI 的 OAuth 功能的用户而言，这一方案颇具实用价值，但 Hermes 会给出明确警告：因为谷歌可能会将第三方软件中使用 Gemini CLI OAuth 客户端的行为视为违反政策。如需在正式环境或低风险场景下使用，建议优先选择上述 API 密钥提供方式。

## 可用模型

`hermes model` 选择器会展示存储在 Hermes 提供商注册表中的 Gemini 模型。常见选项包括：

| 模型 | ID | 备注 |
|-------|----|-------|
| Gemini 3.1 Pro 预览版 | `gemini-3.1-pro-preview` | 可用时功能最强大的预览模型 |
| Gemini 3 Pro 预览版 | `gemini-3-pro-preview` | 具备出色的推理与编程能力 |
| Gemini 3 Flash 预览版 | `gemini-3-flash-preview` | 在速度与功能之间达到最佳平衡的推荐选项 |
| Gemini 3.1 Flash Lite 预览版 | `gemini-3.1-flash-lite-preview` | 可用时速度最快且成本最低的选项 |

模型的可用性会随时间变化。如果某个模型不再可用或未被您的密钥启用，请再次运行 `hermes model`，从当前列表中选择其他模型。

:::info 模型 ID
当使用 `provider: gemini` 时，请使用 Gemini 的原生模型 ID，如 `gemini-3-flash-preview`，而非 OpenRouter 风格的 ID，如 `google/gemini-3-flash-preview`。
:::

### 最新别名

谷歌会为 Pro 和 Flash 系列的 Gemini 模型发布动态更新的别名。当您希望让谷歌自动升级模型而无需修改 Hermes 配置时，`gemini-pro-latest` 和 `gemini-flash-latest` 将非常有用。

| 别名 | 当前追踪的模型 | 备注 |
|-------|------------------|-------|
| `gemini-pro-latest` | 最新的 Gemini Pro 模型 | 适合希望使用谷歌当前默认的 Pro 版模型的用户 |
| `gemini-flash-latest` | 最新的 Gemini Flash 模型 | 适合希望使用谷歌当前默认的 Flash 版模型的用户 |

```yaml
model:
  default: gemini-pro-latest
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

如果需要确保结果的严格可复现性，建议使用明确的模型编号，例如 `gemini-3.1-pro-preview` 或 `gemini-3-flash-preview`。

### 通过 Gemini API 使用 Gemma 模型

Google 还通过 Gemini API 提供 Gemma 模型。Hermes 会将这些模型识别为 Google 的模型，但会隐藏那些吞吐量极低的 Gemma 模型选项，避免新用户在不经意间为长时间运行的智能体会话选择评估版本模型。

常用的评估模型编号如下：

| 模型 | ID | 备注 |
|-------|----|-------|
| Gemma 4 31B IT | `gemma-4-31b-it` | 规模更大的 Gemma 模型，适用于兼容性及质量评估 |
| Gemma 4 26B A4B IT | `gemma-4-26b-a4b-it` | 在可用情况下的较小参数量版本 |

这类模型最好作为 Gemini API 密钥中的评估选项使用。Google 的 Gemma API 仅提供免费套餐，且其使用限额远低于正式版的 Gemini 模型，因此若需长期运行 Hermes 智能体，通常应转而使用付费的 Gemini 模型、自托管部署方案，或选择具备足够配额的其他服务提供商。

若要使用那些在模型选择器中不可见的 Gemma 模型，可直接指定其编号进行调用：

```yaml
model:
  default: gemma-4-31b-it
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

## 会话进行中切换模型

在对话过程中，可使用 `/model` 命令：

```text
/model gemini-3-flash-preview
/model gemini-flash-latest
/model gemini-3-pro-preview
/model gemini-pro-latest
/model gemma-4-31b-it
/model gemini-3.1-flash-lite-preview
```

如果您尚未配置 Gemini 模型，请先退出当前会话并运行 `hermes model` 命令。`/model` 用于在已配置的提供方和模型之间切换，不会用于获取新的 API 密钥。

## 诊断功能

```bash
hermes doctor
```

医生会检查以下内容：

- 是否存在 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`
- `google-gemini-cli` 是否已配置 Gemini OAuth 凭证
- 已配置的提供方凭证是否能够被成功解析

如需查看 OAuth 配额使用情况，请在 Hermes 会话中运行以下命令：

```text
/gquota
```

`/gquota` 命令适用于 `google-gemini-cli` OAuth 提供商，而不适用于 AI Studio API-key 提供商。

## 网关（消息平台）

Gemini 可与所有 Hermes 网关平台（Telegram、Discord、Slack、WhatsApp、LINE、飞书等）兼容。只需将 Gemini 配置为对应的提供商，即可像平常一样启动网关：

```bash
hermes gateway setup
hermes gateway start
```

网关会读取 `config.yaml` 文件，并使用相同的 Gemini 提供商配置。

## 故障排除

### “Gemini 原生客户端需要 API 密钥”

Hermes 未能找到有效的 API 密钥。请在 `~/.hermes/.env` 文件中添加以下内容之一：

```bash
GOOGLE_API_KEY=...
# or
GEMINI_API_KEY=...
```

接着再次运行 `hermes model` 命令。

### “此 Google API 密钥处于免费套餐层级”

Hermes 在初始化时会检测 Gemini API 密钥。由于工具调用、重试操作、数据压缩以及各类辅助任务都可能需要多次模型调用，因此仅经过几次智能体交互，免费套餐的调用配额就可能被耗尽。

请为关联该密钥的 Google Cloud 项目开启计费功能，必要时重新生成密钥，之后再运行相应命令：

```bash
hermes model
```

### “404：未找到模型”

您当前使用的账户、地区或密钥无法访问所选模型。请再次运行 `hermes model` 命令，从现有列表中选择其他 Gemini 模型。

### 在 `hermes model` 中未显示 Gemma 模型

Hermes 默认会隐藏那些吞吐量较低的 Gemma 模型，不显示在模型选择列表中。如果您确实想测试这类模型，可直接在 `~/.hermes/config.yaml` 文件中指定该模型的 ID。

### 使用 Gemma 时出现 “429：配额已用尽” 错误

通过 Gemini API 提供的 Gemma 模型虽适合用于测试，但其免费套餐的调用限额较低。建议将其用于兼容性测试，如需维持长时间的智能体会话，则应切换到付费的 Gemini 模型或其他服务提供商的模型。

### 已配置与 OpenAI 兼容的接口端点

请检查 `~/.hermes/.env` 文件中的相关设置：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

将其更改为原生端点，或移除该覆盖设置：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

### OAuth登录警告

`google-gemini-cli`提供程序采用Gemini CLI/Cloud Code Assist的OAuth认证流程。由于该流程与官方AI Studio API密钥机制不同，Hermes会在启动前发出警告。如需使用官方API密钥进行集成，请同时设置`provider: gemini`和`GOOGLE_API_KEY`。

### 工具调用因架构错误失败

请升级Hermes版本并重新运行`hermes model`命令。内置的Gemini适配器会按照Gemini更严格的函数声明格式对工具架构进行优化处理；旧版本或自定义端点可能无法实现此功能。

## 相关内容

- [AI提供程序](/integrations/providers)
- [配置设置](/user-guide/configuration)
- [备用提供程序](/user-guide/features/fallback-providers)
- [AWS Bedrock](/guides/aws-bedrock) —— 基于AWS凭证实现的原生云服务集成
