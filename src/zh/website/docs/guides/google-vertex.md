---
sidebar_position: 15
title: "Google Vertex AI"
description: "Use Hermes Agent with Gemini on Google Cloud Vertex AI — OAuth2 service account or ADC, GCP billing and quotas, no static API key"
---

# Google Vertex AI

Hermes Agent 支持通过 Vertex 的 OpenAI 兼容端点，使用**部署在 Google Cloud Vertex AI 上的 Gemini 模型**。与 [Google AI Studio 提供程序](/guides/google-gemini)（它使用针对 `generativelanguage.googleapis.com` 的静态 API 密钥）不同，Vertex 提供**企业级速率限制以及 GCP 计费/积分服务**。因此，当您希望将 Gemini 的使用费用计入您的 Google Cloud 账户而非 AI Studio 密钥对应的账户时，Vertex 是理想的选择。

:::info Vertex 使用 OAuth2 进行身份验证，而非 API 密钥
标准端点**没有静态 API 密钥**。每个请求都需要一个短时效的**OAuth2 访问令牌**（有效期约为 1 小时），该令牌可通过服务账户 JSON 文件或应用默认凭据（ADC）生成。Hermes 会为您自动生成并**定期刷新**这些令牌——您无需手动粘贴令牌。这就是为何将临时令牌粘贴到自定义提供程序的 `api_key` 字段中无法生效的原因：该令牌会在会话进行到一半时过期。
:::

## 先决条件

- 一个已**启用 Vertex AI API**且计费功能处于开启状态的**Google Cloud 项目**。
- **身份凭证**，可选以下之一：
  - 包含 `roles/aiplatform.user` 角色的**服务账户 JSON** 密钥文件，或
  - 通过 `gcloud auth application-default login` 获取的**应用默认凭据**（在 GCP 虚拟机上运行时则可通过元数据服务器获取）。
- **`google-auth`** 库——首次选择 Vertex 时会自动安装（延迟安装机制）。如果自动安装失败，可运行 `hermes setup` 命令进行修复。

## 快速入门

```bash
# Option A — service account JSON (recommended for servers / gateways)
echo "VERTEX_CREDENTIALS_PATH=/path/to/service-account.json" >> ~/.hermes/.env

# Option B — Application Default Credentials (good for local dev)
gcloud auth application-default login

# Select Vertex as your provider
hermes model
# → Choose "More providers..." → "Google Vertex AI"
# → Enter your GCP project ID (or leave blank to use the one in your credentials)
# → Choose a region (default: global)
# → Select a Gemini model

# Start chatting
hermes chat
```

## 配置

Vertex会根据敏感程度对各项设置进行分类：

- **凭证路径**是指向机密信息的引用，存储在 `~/.hermes/.env` 文件中。
- **项目 ID 和区域**属于非机密性的路由配置，存储在 `~/.hermes/config.yaml` 文件中。

`~/.hermes/.env`：

```bash
# One of these (checked in this order); omit both to use ADC:
VERTEX_CREDENTIALS_PATH=/path/to/service-account.json
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

`~/.hermes/config.yaml`：

```yaml
model:
  default: google/gemini-3-flash-preview
  provider: vertex

vertex:
  project_id: my-gcp-project   # blank → use the project embedded in the credentials
  region: global               # "global" is required for the Gemini 3.x previews
```

:::提示 环境变量优先于config.yaml设置  
`VERTEX_PROJECT_ID`和`VERTEX_REGION`会覆盖`config.yaml`中的`vertex.project_id`/`vertex.region`值。建议将此类临时覆盖设置放在这些环境变量中，而将持久性配置保留在`config.yaml`中。  
:::

### 认证机制说明

1. Hermes会按以下顺序查找凭证：`VERTEX_CREDENTIALS_PATH` → `GOOGLE_APPLICATION_CREDENTIALS` → ADC。  
2. 它会生成一个具有`cloud-platform`范围的OAuth2访问令牌，并将其缓存起来；当令牌剩余有效期不足5分钟时，系统会自动刷新该令牌。  
3. 该令牌会被传递给指向Vertex端点的标准OpenAI客户端使用：
   ```text
   https://aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{region}/endpoints/openapi
   ```
区域节点则使用 `{region}-aiplatform.googleapis.com` 作为主机地址。

4. 如果会话运行时间超过令牌的有效期限，且请求返回 `401` 错误，Hermes 会自动重新生成令牌并尝试再次发送请求。在长时间运行的网关上，如果 ADC 的刷新令牌也已过期，且已配置服务账户 JSON 文件，Hermes 将回退至该 JSON 文件中的令牌。

## 可用的模型

Vertex 要求模型 ID 前缀为 `google/`。Hermes 模型选择器提供以下模型：

| 模型 | ID |
|-------|----|
| Gemini 3.8 Flash | `google/gemini-3.8-flash` |
| Gemini 3.7 Flash | `google/gemini-3.7-flash` |
| Gemini 3.1 Pro 预览版 | `google/gemini-3.1-pro-preview` |
| Gemini 3 Pro 预览版 | `google/gemini-3-pro-preview` |
| Gemini 3 Flash 预览版 | `google/gemini-3-flash-preview` |
| Gemini 3.1 Flash Lite 预览版 | `google/gemini-3.1-flash-lite-preview` |
| Gemini 2.5 Pro | `google/gemini-2.5-pro` |
| Gemini 2.5 Flash | `google/gemini-2.5-flash` |

:::注意：Gemini 3.x 系列的 `global` 地区
Gemini 3.x 的预览版模型通过 `global` 接口提供，区域接口（如 `us-central1` 等）可能无法找到这些模型。除非有特殊原因需要指定特定地区，否则请保持 `region: global` 设置。
:::

## 在会话进行中切换模型

```text
/model google/gemini-3-pro-preview
/model google/gemini-3-flash-preview
```

`/model` 命令用于在已配置的提供者和模型之间切换，不会收集新的凭证。请先使用 `hermes model` 命令对 Vertex 进行配置。

## 原理说明
Vertex 通过兼容 OpenAI 的接口暴露 Gemini 的推理预算设置。Hermes 会自动将该推理强度设置映射到 `extra_body.google.thinking_config` 中，因此 `reasoning_effort` 的使用方式与其他 Gemini 接口一致。

## 诊断功能

```bash
hermes doctor
```

该医生会反馈是否已成功解析 Vertex 认证信息（服务账户路径或 ADC），以及提供程序是否已正确配置。

## 故障排除

### “无法解析 Vertex AI 认证信息”

Hermes 未找到服务账户的 JSON 文件，也未检测到可用的 ADC。请在 `~/.hermes/.env` 文件中设置 `VERTEX_CREDENTIALS_PATH`，或运行 `gcloud auth application-default login` 命令。如果您的项目未被包含在这些认证信息中，请在 `config.yaml` 文件中设置 `vertex.project_id`。

### 未安装 `google-auth` 库

首次选择 Vertex 提供程序时，Hermes 会自动懒加载该库。若此操作失败，请运行 `hermes setup` 命令来修复其托管安装状态。

### Gemini 3.x 模型出现 404 错误

这可能是由于您使用了区域端点导致的。请在 `config.yaml` 文件的 `vertex:` 部分设置 `region: global`（或取消设置 `VERTEX_REGION`）。

### 403 / 权限被拒绝错误

服务账户（或您的 ADC 身份）需要在项目中拥有 `roles/aiplatform.user` 角色，同时该项目还需启用 Vertex AI API。

## 相关内容

- [Google Gemini (AI Studio)](/guides/google-gemini) — 无需 GCP 环境的静态 API 密钥 Gemini
- [AWS Bedrock](/guides/aws-bedrock) — 另一种原生云服务提供程序集成方案
- [AI 提供程序](/integrations/providers)
- [配置指南](/user-guide/configuration)
