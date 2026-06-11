---
sidebar_position: 14
title: "AWS Bedrock"
description: "Use Hermes Agent with Amazon Bedrock — native Converse API, IAM authentication, Guardrails, and cross-region inference"
---

# AWS Bedrock

Hermes Agent 支持通过 **Converse API** 将 Amazon Bedrock 作为原生提供商使用——而非兼容 OpenAI 的接口。这样一来，您便能完整利用 Bedrock 生态系统：IAM 认证、Guardrails 功能、跨区域推理配置，以及所有基础模型。

## 前提条件

- **AWS 凭据** — 任何 [boto3 凭据链](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) 所支持的来源：
  - IAM 实例角色（EC2、ECS、Lambda——无需额外配置）
  - `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY` 环境变量
  - 用于 SSO 或命名角色的 `AWS_PROFILE`
  - 用于本地开发的 `aws configure`
- **boto3** — 通过 `pip install hermes-agent[bedrock]` 安装
- **IAM 权限** — 最低需具备以下权限：
  - `bedrock:InvokeModel` 和 `bedrock:InvokeModelWithResponseStream`（用于模型推理）
  - `bedrock:ListFoundationModels` 和 `bedrock:ListInferenceProfiles`（用于查找模型）

:::提示 EC2 / ECS / Lambda
在 AWS 计算环境中，只需为实例附加一个具有 `AmazonBedrockFullAccess` 权限的 IAM 角色即可。无需 API 密钥，也无需 `.env` 配置——Hermes 会自动检测该实例角色。
:::

## 快速入门

```bash
# Install with Bedrock support
pip install hermes-agent[bedrock]

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

可通过以下任意方式设置 AWS 区域（按优先级从高到低）：

1. `config.yaml` 文件中的 `bedrock.region` 参数
2. `AWS_REGION` 环境变量
3. `AWS_DEFAULT_REGION` 环境变量
4. 默认值：`us-east-1`

### 规范约束

如需对所有模型调用应用 [Amazon Bedrock 规范约束](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)：

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

Hermes 会通过 Bedrock 控制平面自动发现可用的模型。您也可以自定义模型发现机制：

```yaml
bedrock:
  discovery:
    enabled: true
    provider_filter: ["anthropic", "amazon"]  # Only show these providers
    refresh_interval: 3600                     # Cache for 1 hour
```

## 可用模型

Bedrock 模型通过**推理配置文件 ID**来实现按需调用。`hermes model` 选择器会自动显示这些模型，其中推荐使用的模型会显示在顶部：

| 模型 | ID | 备注 |
|-------|-----|------|
| Claude Sonnet 4.6 | `us.anthropic.claude-sonnet-4-6` | 推荐使用——速度与性能的最佳平衡 |
| Claude Opus 4.6 | `us.anthropic.claude-opus-4-6-v1` | 性能最强 |
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | 速度最快的 Claude 模型 |
| Amazon Nova Pro | `us.amazon.nova-pro-v1:0` | Amazon 的旗舰模型 |
| Amazon Nova Micro | `us.amazon.nova-micro-v1:0` | 速度最快且价格最低 |
| DeepSeek V3.2 | `deepseek.v3.2` | 性能出色的开源模型 |
| Llama 4 Scout 17B | `us.meta.llama4-scout-17b-instruct-v1:0` | Meta 的最新模型 |

:::info 跨区域推理
以 `us.` 开头的模型使用跨区域推理配置文件，这类配置能在 AWS 各区域之间提供更强的处理能力并实现自动故障转移。而以 `global.` 开头的模型则可在全球所有可用区域间进行调用。
:::

## 会话中进行模型切换

在对话过程中，可使用 `/model` 命令来切换模型：

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
- 是否能够访问 Bedrock API（通过 ListFoundationModels 接口测试）
- 您所在区域可用的模型数量

## 网关（消息平台）

Bedrock 支持所有 Hermes 网关平台（Telegram、Discord、Slack、飞书等）。只需将 Bedrock 配置为服务提供方，即可像平常一样启动网关：

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

如果均未找到相关凭证，请运行 `aws configure`，或为您的计算实例附加 IAM 角色。

### “不支持使用按需吞吐量调用模型 ID ...”

请使用**推理配置文件 ID**（以 `us.` 或 `global.` 为前缀），而非单纯的基础模型 ID。例如：
- ❌ `anthropic.claude-sonnet-4-6`
- ✅ `us.anthropic.claude-sonnet-4-6`

### “ThrottlingException” 错误

您已达到 Bedrock 对单个模型的速率限制。Hermes 会自动进行带退避机制的重试。如需提高限制，可在 [AWS 服务配额控制台](https://console.aws.amazon.com/servicequotas/) 中申请增加配额。

## 一键 AWS 部署

通过 CloudFormation 在 EC2 上实现全自动部署：

**[sample-hermes-agent-on-aws-with-bedrock](https://github.com/JiaDe-Wu/sample-hermes-agent-on-aws-with-bedrock)** —— 该示例会自动创建 VPC、IAM 角色和 EC2 实例，并完成 Bedrock 的配置。只需点击一下即可在任何区域完成部署。
