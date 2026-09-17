---
sidebar_position: 14
title: "AWS Bedrock"
description: "Use Hermes Agent with Amazon Bedrock — native Converse API, Anthropic SDK routing, OpenAI models via Bedrock Mantle, IAM authentication, Guardrails, and cross-region inference"
---

# AWS Bedrock

Hermes Agent 将 Amazon Bedrock 作为原生提供商予以支持。这使您能够全面使用 Bedrock 生态系统中的各项功能：IAM 认证、Guardrails 安全机制、跨区域推理配置，以及所有基础模型。

Hermes 会为每个模型系列自动选择最合适的 API 路由：

| 模型系列 | API 路由 | 原因 |
|---|---|---|
| Anthropic Claude | Anthropic SDK (`AnthropicBedrock`) | 支持提示词缓存、思考预算设置以及自适应思考功能——这些功能在 Converse 接口中不可用 |
| OpenAI GPT-5.5 / GPT-5.6 (Sol, Terra, Luna) | Bedrock Mantle **OpenAI Responses** 接口 (`bedrock-mantle.<region>.api.aws/openai/v1`) | 这些模型仅支持 Mantle 接口——其模型卡片中明确标注 bedrock-runtime/Converse 不受支持 |
| 其他所有模型 (Nova, DeepSeek, Llama, GPT-OSS 等) | 原生 **Converse API** (`bedrock-runtime`) | 可享受完整的 Bedrock 功能集：Guardrails 安全机制、推理配置以及流式响应功能 |

以上三种路由均共享相同的 AWS 凭证体系与区域解析机制——无需额外配置。当设置了 `AWS_BEARER_TOKEN_BEDROCK` 时，对 Mantle 接口的请求将使用该令牌进行认证；否则则通过标准的 boto3 凭证体系采用 SigV4 签名方式进行认证。

## 先决条件

- **AWS 凭证** — 任何受 [boto3 凭证链](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) 支持的来源：
  - IAM 实例角色（EC2、ECS、Lambda — 无需额外配置）
  - `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY` 环境变量
  - 用于 SSO 或命名配置文件的 `AWS_PROFILE`
  - 用于本地开发的 `aws configure`
- **boto3** — 通过以下命令进行安装：`cd ~/.hermes/hermes-agent && uv pip install -e ".[bedrock]"`
- **IAM 权限** — 最低要求包括：
  - `bedrock:InvokeModel` 和 `bedrock:InvokeModelWithResponseStream`（用于模型推理）
  - `bedrock:ListFoundationModels` 和 `bedrock:ListInferenceProfiles`（用于查找模型）

:::提示 EC2 / ECS / Lambda
在 AWS 计算环境中，只需为实例附加一个具有 `AmazonBedrockFullAccess` 权限的 IAM 角色即可。无需 API 密钥，也无需 `.env` 配置文件 — Hermes 会自动检测该实例角色。
:::

## 快速入门

```bash
# Install with Bedrock support
cd ~/.hermes/hermes-agent && uv pip install -e ".[bedrock]"

# Select Bedrock as your provider
hermes model
# → Choose "More providers..." → "AWS Bedrock"
# → Select your region and model

# Start chatting
hermes chat
```

## 配置

运行 `hermes model` 后，您的 `~/.hermes/config.yaml` 文件中将包含以下内容：

```yaml
model:
  default: us.anthropic.claude-sonnet-4-6
  provider: bedrock
  base_url: https://bedrock-runtime.us-east-2.amazonaws.com

bedrock:
  region: us-east-2
```

### 区域设置

可通过以下任意方式设置 AWS 区域（按优先级从高到低排序）：

1. `config.yaml` 文件中的 `bedrock.region`  
2. `AWS_REGION` 环境变量  
3. `AWS_DEFAULT_REGION` 环境变量  
4. 默认值：`us-east-1`  

### 规则约束

如需对所有模型调用应用 [Amazon Bedrock 规则约束](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)：

```yaml
bedrock:
  region: us-east-2
  guardrail:
    guardrail_identifier: "abc123def456"  # From the Bedrock console
    guardrail_version: "1"                # Version number or "DRAFT"
    stream_processing_mode: "async"       # "sync" or "async"
    trace: "disabled"                     # "enabled", "disabled", or "enabled_full"
```

### 模型发现

Hermes 会通过 Bedrock 控制平面自动发现可用的模型。您也可以自定义模型发现流程：

```yaml
bedrock:
  discovery:
    enabled: true
    provider_filter: ["anthropic", "amazon"]  # Only show these providers
    refresh_interval: 3600                     # Cache for 1 hour
```

### 提示词缓存（cachePoint）

Hermes 会在 Bedrock **Converse API** 路径上自动实现提示词缓存功能，具体做法是在系统提示词、工具定义以及最新消息之后插入 `cachePoint` 标记。由于向不支持该功能的模型发送 `cachePoint` 标记会引发 `ValidationException` 异常，因此仅会在已知兼容的模型列表（如 Anthropic Claude 和 Amazon Nova 的模型编号）中添加这些标记；对于未知模型，则默认不添加缓存标记。Claude 模型通常使用 AnthropicBedrock SDK 路径，该路径拥有独立的提示词缓存机制——而 Converse 的 `cachePoint` 机制则用于处理 Nova 模型以及基于令牌的 Claude 回退方案。无需进行任何配置，缓存读写操作会体现在使用量统计中。

### 上下文窗口检测

对于那些未列入 Hermes 静态列表中的模型，Hermes 可以通过发送固定大小的请求（约 130 万和 220 万个标记）来检测其实际的上限，并解析 Bedrock 返回的长度验证错误信息中的 `maximum` 值。检测得到的数值会存入与静态列表相同的元数据缓存中；那些因数据过时而低估了模型上下文窗口大小的缓存条目（例如在模型 100 万标记上限正式推出之前生成的条目）将会被自动剔除，取而代之的是更准确的已知数值。

## 支持的模型

Bedrock 模型通过**推理配置文件编号**来实现按需调用。`hermes model` 选择器会自动显示这些模型，其中推荐使用的模型会显示在列表顶部：

| 模型 | ID | 备注 |
|-------|-----|------|
| Claude Sonnet 4.6 | `us.anthropic.claude-sonnet-4-6` | 推荐选择——速度与性能的最佳平衡 |
| Claude Opus 4.6 | `us.anthropic.claude-opus-4-6-v1` | 性能最强 |
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | 速度最快的Claude模型 |
| OpenAI GPT-5.6 Sol | `openai.gpt-5.6-sol` | OpenAI的尖端模型（通过Bedrock Mantle提供） |
| OpenAI GPT-5.6 Terra | `openai.gpt-5.6-terra` | 性能均衡的模型（通过Bedrock Mantle提供） |
| OpenAI GPT-5.6 Luna | `openai.gpt-5.6-luna` | 速度快且价格实惠（通过Bedrock Mantle提供） |
| OpenAI GPT-5.5 | `openai.gpt-5.5` | 旧版OpenAI旗舰模型（通过Bedrock Mantle提供） |
| Amazon Nova Pro | `us.amazon.nova-pro-v1:0` | Amazon的旗舰模型 |
| Amazon Nova Micro | `us.amazon.nova-micro-v1:0` | 速度最快且价格最低的模型 |
| DeepSeek V3.2 | `deepseek.v3.2` | 实力强劲的开源模型 |
| Llama 4 Scout 17B | `us.meta.llama4-scout-17b-instruct-v1:0` | Meta的最新模型 |

:::info 跨区域推理
以 `us.` 开头的模型采用跨区域推理配置，能够提供更强的处理能力，并在AWS不同区域之间实现自动故障转移。以 `global.` 开头的模型则可在全球所有可用区域间切换。OpenAI的 `openai.*` 类型模型由Bedrock Mantle在配置好的区域内提供服务，不使用此类推理配置前缀。
:::

## 会话进行中切换模型

在对话过程中可使用 `/model` 命令来切换模型：

```
/model us.amazon.nova-pro-v1:0
/model deepseek.v3.2
/model us.anthropic.claude-opus-4-6-v1
```

## 诊断功能

```bash
hermes doctor
```

医生会检查以下内容：
- 是否具备 AWS 凭证（环境变量、IAM 角色或 SSO）
- 是否已安装 `boto3` 库
- 是否能够访问 Bedrock API（通过 ListFoundationModels 命令进行测试）
- 您所在区域可用的模型数量

## 网关（消息平台）

Bedrock 支持所有 Hermes 网关平台（Telegram、Discord、Slack、飞书等）。只需将 Bedrock 配置为对应的提供者，即可像平常一样启动网关：

```bash
hermes gateway setup
hermes gateway start
```

网关会读取 `config.yaml` 文件，并使用相同的 Bedrock 提供商配置。

## 故障排除

### “未找到 API 密钥” / “未找到 AWS 凭证”

Hermes 会按以下顺序检查凭证：
1. `AWS_BEARER_TOKEN_BEDROCK`
2. `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
3. `AWS_PROFILE`
4. EC2 实例元数据（IMDS）
5. ECS 容器凭证
6. Lambda 执行角色

如果未找到任何凭证，请运行 `aws configure`，或为您的计算实例附加 IAM 角色。

### “不支持使用按需吞吐量调用模型 ID ...”

请使用**推理配置文件 ID**（以 `us.` 或 `global.` 为前缀），而非单纯的基础模型 ID。例如：
- ❌ `anthropic.claude-sonnet-4-6`
- ✅ `us.anthropic.claude-sonnet-4-6`

### “ThrottlingException” 错误

您已达到 Bedrock 对单个模型的速率限制。Hermes 会自动进行带退避机制的重试。如需提高限制，请在 [AWS Service Quotas 控制台](https://console.aws.amazon.com/servicequotas/) 中申请配额增加。

## 一键 AWS 部署

通过 CloudFormation 在 EC2 上实现完全自动化的部署：

**[sample-hermes-agent-on-aws-with-bedrock](https://github.com/JiaDe-Wu/sample-hermes-agent-on-aws-with-bedrock)** —— 该示例会自动创建 VPC、IAM 角色和 EC2 实例，并完成 Bedrock 的配置。只需点击一下即可在任意区域完成部署。
