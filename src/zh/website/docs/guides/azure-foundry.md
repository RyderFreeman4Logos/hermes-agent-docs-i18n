---
sidebar_position: 15
title: "Microsoft Foundry"
description: "Use Hermes Agent with Microsoft Foundry — OpenAI-style and Anthropic-style endpoints, auto-detection of transport and deployed models"
---

# Microsoft Foundry

Hermes Agent 的 `azure-foundry` 提供程序支持 Microsoft Foundry（旧称 Azure AI Foundry）以及 Azure OpenAI。同一个 Foundry 资源可以托管采用两种不同接口格式的模型：

- **OpenAI 风格** —— 通过类似 `https://<resource>.openai.azure.com/openai/v1` 的端点发送 `POST /v1/chat/completions` 请求。该格式适用于 GPT-4.x、GPT-5.x、Llama、Mistral 以及大多数开源模型。
- **Anthropic 风格** —— 通过类似 `https://<resource>.services.ai.azure.com/anthropic` 的端点发送 `POST /v1/messages` 请求。当 Microsoft Foundry 通过 Anthropic Messages API 格式提供 Claude 模型时，会使用此格式。

设置向导会自动探测您的端点，从而识别其所使用的传输协议、可用的部署选项以及每个模型的上下文长度。

## 先决条件

- 已拥有至少一个部署的 Microsoft Foundry 或 Azure OpenAI 资源
- 该部署的端点 URL
- **要么** 使用 API 密钥（可从 Azure Portal 的“密钥与端点”页面获取），**要么** 如果您打算使用 Microsoft Entra ID（微软推荐的无需密钥的方案），则需在 Foundry 资源上拥有 **Azure AI User** RBAC 角色。在微软进行名称变更的过程中，部分租户可能会看到该角色显示为 **Foundry User**。

## 快速入门

```bash
hermes model
# → Select "Azure Foundry"
# → Enter your endpoint URL
# → Choose Authentication:
#     1. API key
#     2. Microsoft Entra ID  (managed identity / workload identity / az login)
# → (Entra) Hermes probes DefaultAzureCredential; on success it never asks for a key
# → (API key) Enter your API key
# Hermes probes the endpoint and auto-detects transport + models
# → Pick a model from the list (or type a deployment name manually)
```

向导将执行以下操作：

1. **扫描 URL 路径** — 以 `/anthropic` 结尾的 URL 会被识别为 Microsoft Foundry Claude 的路由。
2. **探测 `GET <base>/models`** — 如果该端点返回类似 OpenAI 格式的模型列表，Hermes 会切换到 `chat_completions` 模式，并将返回的部署 ID 自动填充到选择器中。
3. **探测 Anthropic Messages 格式** — 作为备用方案，适用于不提供 `/models` 接口但支持 Anthropic Messages 格式的端点。
4. **回退至手动输入** — 对于拒绝所有探测的私有或受限制端点，仍可正常使用；此时需手动选择 API 模式并输入部署名称。

所选模型的上下文长度将通过 Hermes 的标准元数据链（`models.dev`、提供商元数据以及硬编码的默认值）来确定，并存储在 `config.yaml` 中，从而使模型能够正确设置自身的上下文窗口大小。

## Microsoft Entra ID（无密钥、基于 RBAC）——推荐方案

Microsoft 建议在生产环境中的 Foundry 工作负载中使用[基于 Microsoft Entra ID 的无密钥认证](https://learn.microsoft.com/azure/ai-foundry/foundry-models/how-to/configure-entra-id)。Hermes 支持在**两种 API 接口风格**下使用 Entra ID：

- **OpenAI 风格**（`api_mode: chat_completions` / `codex_responses`）——适用于 GPT-4/5、Llama、Mistral、DeepSeek 等模型。
- **Anthropic 风格**（`api_mode: anthropic_messages`）——适用于 Microsoft Foundry 上的 Claude 模型。

Foundry 的 RBAC 是按资源划分的（“Azure AI User”角色可同时授权这两种接口；部分租户可能会显示为“Foundry User”角色），而 Microsoft 也为这两种场景规定了相同的推理作用域（`https://ai.azure.com/.default`）。在实现层面：

- OpenAI 风格使用 OpenAI Python SDK 的原生可调用的 `api_key=` 接口——SDK 会自动为每个请求生成新的 JWT。
- Anthropic 风格则使用由 `agent.azure_identity_adapter.build_bearer_http_client` 安装的请求事件钩子与 `httpx.Client` 结合，因为 Anthropic SDK 本身不支持 `auth_token` 可调用接口。该钩子会为每个外发请求重新生成 `Authorization: Bearer <新鲜JWT>` 格式的授权头。两种方案都采用相同的 Microsoft RBAC 机制和 Foundry 作用域，唯一的区别在于 SDK 的接口实现方式。

### 为何选择 Entra ID？

- 无需管理长期有效的 API 密钥，也无需对其进行轮换或撤销。
- 基于 RBAC 的访问控制——只需在 Foundry 资源上授予或移除 “Azure AI User” 角色，无需修改配置文件。
- 访问日志和审计日志会按具体使用者进行分类，而非所有调用者共享同一个静态密钥。
- 通过托管身份机制，可为 Azure 虚拟机、AKS 容器、App Service、Functions、Container Apps 以及 Foundry Agent Service 提供统一的认证方式。
- 支持为 CI/CD 管道使用工作负载身份和服务主体流程。

### 一次性设置步骤（Azure 端）

1. 在 Azure Portal 中打开您的 Foundry 资源 → **访问控制 (IAM)** → **添加 → 添加角色分配**。
2. 选择 “Azure AI User” 角色（如果您的租户使用了重命名后的角色，则选择 “Foundry User”）。
3. 将该角色分配给以下对象：
   - 使用 `az login` 进行本地开发的**个人用户账户**。
   - 部署在 Azure 上的计算资源对应的**托管身份或工作负载身份**（推荐用于生产环境）。
   - 当 Hermes 在托管代理中运行时，对应**托管代理中的 Agent Identity**。
   - 当无法使用工作负载身份时，用于 CI/CD 管道的**服务主体**。
4. 等待约 5 分钟，让角色权限同步完成。

Azure CLI 对应操作：

```bash
az role assignment create \
  --assignee <principal-or-agent-identity-client-id> \
  --role "Azure AI User" \
  --scope <foundry-resource-id>
```

### 一次性设置（Hermes端）

```bash
hermes model
# → Select "Azure Foundry"
# → Enter your endpoint URL
# → Authentication: 2 (Microsoft Entra ID)
# → (optional) user-assigned managed identity client ID
# → (optional) Azure tenant ID
# → Hermes probes DefaultAzureCredential() and reports which inner
#    credential succeeded (e.g. AzureCliCredential, ManagedIdentityCredential)
```

向导会运行一次时限为10秒的预检探测。如果检测失败，它会提供“仍继续保存，稍后验证”的选项——这在配置发生在尚未拥有凭据但将在运行时获取凭据的机器上时非常有用（例如为基于托管身份的部署准备配置文件）。

`azure-identity`模块会在首次使用时通过Hermes的延迟安装机制自动安装。如需提前安装：

```bash
pip install azure-identity
```

### 写入 `config.yaml` 的配置文件

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  auth_mode: entra_id
  default: gpt-4o
  context_length: 128000
  entra:
    scope: https://ai.azure.com/.default        # only when overriding the default
```

Hermes在`config.yaml`中仅管理一个与Entra相关的配置项：

- **`scope`** — OAuth资源作用域。其默认值为Microsoft官方文档中规定的推理作用域（`https://ai.azure.com/.default`）。仅当您的资源是基于非标准访问对象配置时才需要手动修改此值。

其余所有配置项（租户信息、服务主体密钥、联合令牌文件、主权云授权机构以及代理服务器偏好设置）均由`azure-identity`直接从标准的`AZURE_*`环境变量中读取——具体顺序请参见下文的[凭据解析顺序](#credential-resolution-order)。请按照Microsoft SDK参考文档中的说明，在`~/.hermes/.env`或您的部署环境中设置这些变量。

在Entra模式下，没有任何密钥会存储在`~/.hermes/.env`文件中——`azure-identity`会在进程内部缓存令牌（若系统支持，也会缓存在操作系统的钥匙串或`~/.IdentityService`目录中）。

### 凭据解析顺序

每次请求令牌时，`azure-identity`的`DefaultAzureCredential`都会按以下顺序依次查找，一旦有凭据能成功获取令牌便会停止搜索：

1. **环境变量中的凭据** — `AZURE_TENANT_ID` + `AZURE_CLIENT_ID` + `AZURE_CLIENT_SECRET`（或`AZURE_CLIENT_CERTIFICATE_PATH` / `AZURE_FEDERATED_TOKEN_FILE`）。
2. **工作负载身份** — `AZURE_FEDERATED_TOKEN_FILE`（用于AKS的联合令牌/OIDC）。
3. **托管身份** — 虚拟机的IMDS端点（`169.254.169.254`）；App Service / Functions / Container Apps则使用`IDENTITY_ENDPOINT`。由Foundry Agent Service托管的代理会使用该托管代理的自身身份。
4. **Visual Studio Code** — Azure账户扩展。
5. **Azure CLI** — `az login`会话。
6. **Azure Developer CLI** — `azd auth login`命令。
7. **Azure PowerShell** — `Connect-AzAccount`命令。
8. **代理服务器**（仅限Windows/WSL系统）——Web Account Manager。

对于无人值守运行的Hermes实例，系统默认会忽略浏览器交互式凭据；此时应使用Azure CLI、Azure Developer CLI、托管身份、工作负载身份或服务主体凭据。

### 部署模式

**本地开发：**
```bash
az login
hermes model   # pick Azure Foundry → Entra ID
hermes         # uses your az login token
```

**Azure VM / Functions / App Service / Container Apps（系统分配的托管身份）：**
1. 在计算资源上启用系统分配的托管身份。
2. 为该身份在 Foundry 资源中授予 `Azure AI User`（或 `Foundry User`）权限。
3. 在 config.yaml 中设置 `model.auth_mode: entra_id`——无需配置环境变量。

**Azure VM / Functions / App Service / Container Apps（用户分配的托管身份）：**
- 将 `AZURE_CLIENT_ID` 设置为用户分配的托管身份的客户端 ID，以便 `DefaultAzureCredential` 能正确选择对应的身份。

**由 Foundry Agent Service 托管的代理：**
- 创建托管代理，并为该代理的身份在 Foundry 资源中授予 `Azure AI User`（或 `Foundry User`）权限。Hermes 会在托管代理内部使用 `ManagedIdentityCredential`；角色分配应针对代理身份本身，而不仅限于父项目或您的用户。

**AKS 工作负载身份（替代 AAD Pod Identity）：**
- 用工作负载身份的客户端 ID 对 Pod 的服务账户进行标注。
- 通过 `AZURE_FEDERATED_TOKEN_FILE` 可自动检测到 Pod 的联合令牌文件。
- 设置 `model.auth_mode: entra_id` 后无需进一步修改配置即可正常使用。

**CI 环境中的服务主体：**
- 在运行器环境中设置 `AZURE_TENANT_ID`、`AZURE_CLIENT_ID` 和 `AZURE_CLIENT_SECRET`。

#### 主权云（政府机构、中国地区）

需导出 `AZURE_AUTHORITY_HOST` 的值（例如，Azure 政府版为 `https://login.microsoftonline.us`，Azure 中国版为 `https://login.partner.microsoftonline.cn`）。`azure-identity` 会直接读取该值。

### 健康检查

当设置 `model.auth_mode: entra_id` 时，`hermes doctor` 会针对 `DefaultAzureCredential` 执行为期 10 秒的探测，从而判断哪种身份验证方式有效（如环境变量是否存在、托管身份端点是否可达等），并输出检测结果。

`hermes auth` 会显示结构化的状态信息块：

```
azure-foundry (Microsoft Entra ID):
  Endpoint: https://my-resource.openai.azure.com/openai/v1
  Scope: https://ai.azure.com/.default
  Status: configured; live token probe is skipped here
```

### 局限性

- **Anthropic 风格的接口端点使用 httpx 事件钩子。** Anthropic 的 Python SDK 在版本 ≤ 0.86.0 时并不原生支持可调用的 `auth_token` 接口。Hermes 会在自定义的 `httpx.Client` 上安装请求事件钩子，该钩子会为每次外发请求生成全新的 JWT，并重写 `Authorization: Bearer <jwt>` 头部信息。这一机制在功能上等同于 OpenAI SDK 原生的 `Callable[[], str]` 接口，但多了一层间接处理。如果 Anthropic SDK 在后续版本中加入原生的一等可调用认证支持，Hermes 将会无缝切换到该机制。
- **批量任务与 `multiprocessing.Pool`。** Entra 令牌提供器是一个无法跨进程边界序列化的闭包函数。`batch_runner.py` 会自动从工作进程配置中移除该可调用对象，让每个工作进程根据 `config.yaml` 文件重新构建自己的令牌提供器——无需用户手动操作，但每个工作进程在启动时都需要进行一次凭证链解析。
- **`auth.json` 中不支持 bearer JWT 持久化存储。** Hermes 并不会复制 `azure-identity` 的内部令牌缓存机制；因此在首次推理时，系统需要重新遍历整个凭证链。

## 配置文件（存储于 `config.yaml`）

运行向导后，您将看到类似如下的配置内容：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions         # or "anthropic_messages"
  default: gpt-5.4-mini              # your deployment / model name
  context_length: 400000             # auto-detected
```

在 `~/.hermes/.env` 文件中：

```
AZURE_FOUNDRY_API_KEY=<your-azure-key>
```

## 类 OpenAI 的端点（GPT、Llama 等）

Azure OpenAI 的 v1 正式版端点在几乎无需任何修改的情况下即可兼容标准的 `openai` Python 客户端：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  default: gpt-5.4
```

重要行为说明：

- **GPT-5.x、codex以及o系列模型会自动路由至Responses API。** Microsoft Foundry部署的GPT-5/codex/o1/o3/o4模型均为仅支持Responses API的版本——通过`/chat/completions`接口调用这些模型时会返回`400 "The requested operation is unsupported."`错误。Hermes能够通过模型名称识别这些系列，并在`config.yaml`中仍设置为`api_mode: chat_completions`的情况下，自动将`api_mode`更改为`codex_responses`。而GPT-4、GPT-4o、Llama、Mistral等其他模型则继续使用`/chat/completions`接口。
- **会自动应用`max_completion_tokens`参数。** Azure OpenAI（与直接使用OpenAI的情况类似）要求对GPT-4o、o系列及GPT-5.x模型设置`max_completion_tokens`参数。Hermes会根据所使用的接口端点自动传递正确的参数值。
- **需要指定`api-version`的预v1版本接口。** 如果您使用的是类似`https://<resource>.openai.azure.com/openai?api-version=2025-04-01-preview`这样的旧版基础URL，Hermes会提取查询字符串，并在每次请求中通过`default_query`参数将其传递过去（否则OpenAI SDK在拼接路径时会忽略该参数）。

## Anthropic风格接口（通过Microsoft Foundry部署的Claude）

对于Claude模型，应使用Anthropic风格的路由方式：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.services.ai.azure.com/anthropic
  api_mode: anthropic_messages
  default: claude-sonnet-4-6
```

重要行为说明：

- **基础URL中会去掉`/v1`**。Anthropic SDK会在每个请求URL后附加`/v1/messages`，而Hermes在将URL传递给SDK之前会移除末尾的`/v1`，以避免出现双`/v1`路径。
- **`api-version`通过`default_query`传递，而非附加在URL中**。Azure Anthropic要求使用`api-version`查询字符串。若将其直接嵌入基础URL，会导致路径格式错误，例如`/anthropic?api-version=.../v1/messages`，进而引发404错误。因此Hermes会通过Anthropic SDK的`default_query`字段传递`api-version=2025-04-15`。
- **使用Bearer认证而非`x-api-key`**。Azure兼容Anthropic的接口要求使用`Authorization: Bearer <key>`格式的授权头，而非Anthropic默认的`x-api-key`头。Hermes检测到基础URL中包含`azure.com`后，会通过SDK的`auth_token`字段传递API密钥，从而确保正确的授权头能被上传服务识别。
- **保留100万上下文窗口的测试版标记**。Azure仍然要求在`anthropic-beta: context-1m-2025-08-07`标记后方可使用100万token的 Claude 上下文功能（适用于Opus 4.6/4.7及Sonnet 4.6版本）。Hermes在处理Azure接口时仍保留该测试版标记（在原生Anthropic OAuth请求中该标记会被移除，因为某些订阅计划不支持它，但Azure却要求其存在）。
- **禁用OAuth令牌刷新功能**。Azure部署使用的是静态API密钥。为防止Claude Code的OAuth令牌在会话进行过程中覆盖您的Azure密钥，针对Azure端点，明确跳过了适用于Anthropic控制台的`~/.claude/.credentials.json`中的OAuth令牌刷新机制。

## 备选方案：使用`provider: anthropic` + Azure基础URL

如果您已经配置了`provider: anthropic`，且只想将其指向用于Claude的Microsoft Foundry平台，那么完全可以跳过`azure-foundry`提供程序。

```yaml
model:
  provider: anthropic
  base_url: https://my-resource.services.ai.azure.com/anthropic
  key_env: AZURE_ANTHROPIC_KEY
  default: claude-sonnet-4-6
```

在 `~/.hermes/.env` 中设置 `AZURE_ANTHROPIC_KEY` 后，Hermes 会检测到基础 URL 中的 `azure.com`，从而跳过 Claude Code 的 OAuth 令牌流程，直接使用带有 `x-api-key` 认证方式的 Azure 密钥。

`key_env` 是标准的下划线命名格式；`api_key_env`（以及驼峰命名的 `keyEnv` / `apiKeyEnv`）也被视为其别名。如果同时设置了 `key_env` 与 `AZURE_ANTHROPIC_KEY`/`ANTHROPIC_API_KEY`，则以 `key_env` 命名的环境变量优先生效。

## 模型发现

Azure 并未提供仅基于 API 密钥的接口来列出已部署的模型。要枚举这些部署，需要使用 Azure AD 主体通过 Azure Resource Manager 进行身份验证（即执行 `az cognitiveservices account deployment list` 命令），而非使用推理 API 密钥。

Hermes 可以做到以下几点：

- Azure OpenAI v1 接口（`<resource>.openai.azure.com/openai/v1`）会提供 `GET /models` 接口，返回该资源下**可用**的模型列表。Hermes 会利用此列表自动填充模型选择器。
- Microsoft Foundry 的 `/anthropic` 路由：可通过 URL 路径检测，或手动输入模型名称。
- 私有/被防火墙屏蔽的接口：需手动输入模型名称，同时会显示“无法探测到”的提示信息。

您始终可以直接输入模型部署名称——Hermes 不会对照返回的列表进行验证。

## 环境变量

| 变量名 | 用途 |
|--------|------|
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI 的主 API 密钥（api_key 模式） |
| `AZURE_FOUNDRY_BASE_URL` | 接口端点 URL（可通过 `hermes model` 命令设置；若未设置则使用环境变量作为备用） |
| `AZURE_ANTHROPIC_KEY` | 供 `provider: anthropic` 模式及 Azure 基础 URL 使用（可作为 `ANTHROPIC_API_KEY` 的替代选项） |
| `AZURE_TENANT_ID` | 用于服务主体流程的 Entra ID 租户标识 |
| `AZURE_CLIENT_ID` | Entra ID 客户端 ID（服务主体、工作负载身份或用户分配的管理身份） |
| `AZURE_CLIENT_SECRET` | 服务主体密钥 |
| `AZURE_CLIENT_CERTIFICATE_PATH` | 服务主体证书（可作为密钥的替代选项） |
| `AZURE_FEDERATED_TOKEN_FILE` | AKS 环境下工作负载身份的联合令牌路径 |
| `AZURE_AUTHORITY_HOST` | 用于覆盖主权云认证权威节点的主机地址 |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | App Service、Functions 和 Container Apps 的管理身份接口端点；虚拟机通常使用 IMDS 接口 |

Azure SDK 会直接读取 `AZURE_*` 开头的环境变量。Hermes 除了在 `hermes doctor` 的输出中显示存在哪些配置源外，不会对这些变量进行任何检查。

## 故障排除

**在 gpt-5.x 模型部署上出现 401 Unauthorized 错误。**
Azure 实际在 `/chat/completions` 路径下提供 gpt-5.x 模型的服务，而非 `/responses`。当 URL 包含 `openai.azure.com` 时，Hermes 会自动处理此情况；但若出现 401 错误且错误信息为“Invalid API key”，请检查 `config.yaml` 文件中的 `api_mode` 是否设置为 `chat_completions`。

**在访问 `/v1/messages?api-version=.../v1/messages` 时出现 404 错误。**
这是早期 Azure Anthropic 配置中存在的 URL 格式错误导致的。请升级 Hermes——目前 `api-version` 参数是通过 `default_query` 传递的，而非直接嵌入在基础 URL 中，因此 SDK 在拼接 URL 时不会再破坏该参数。

**向导提示“自动检测未完成”。**
说明该接口端点拒绝了 `/models` 探测请求以及 Anthropic Messages 探测请求。对于处于防火墙后面或仅有特定 IP 允许列表的私有接口，这种情况属于正常现象。此时可切换到手动选择 API 模式并输入模型部署名称——所有功能依然可用，只是 Hermes 无法自动填充模型选择器。

**选错了传输方式。**
请再次运行 `hermes model` 命令，向导会重新进行探测。如果探测后仍选择错误的模式，您可以直接编辑 `config.yaml` 文件进行修改。

```yaml
model:
  provider: azure-foundry
  api_mode: anthropic_messages   # or chat_completions
```

**使用 `auth_mode: entra_id` 后出现 Entra ID 错误：“凭证链已耗尽”或 401 未授权。**
- 运行 `az login` 以刷新开发者会话（缓存中的令牌可能已过期）。
- 确认 `Azure AI User`（或 `Foundry User`）角色分配已生效：执行 `az role assignment list --assignee <user-or-identity-id>`，该命令应在您的 Foundry 资源中列出该角色。角色传播可能需要最多 5 分钟。
- 对于用户分配的托管身份，请仔细检查 `AZURE_CLIENT_ID` 是否与计算资源上附加的身份一致。
- 运行 `hermes doctor`——Azure Entra 探测工具会报告令牌获取是否成功，并提供相应的解决方案提示。

**Entra ID：向导预检步骤卡住或超时。**
10 秒的预检仅作为初步检查。可选择“仍保存并稍后验证”，在部署到目标环境后再运行 `hermes doctor`。常见原因包括令牌服务无法访问或本地登录状态过期——在 CI 环境中建议使用工作负载身份；使用服务主体时请设置 `AZURE_TENANT_ID`、`AZURE_CLIENT_ID` 和 `AZURE_CLIENT_SECRET`；本地开发时则运行 `az login`。

**使用 Entra ID 时，Anthropic 风格的端点出现 401 错误。**
请确认 Foundry 资源上已分配相同的 `Azure AI User`（或 `Foundry User`）角色（该角色同时适用于 `/openai/v1` 和 `/anthropic` 路径）。如果在向导过程中 OpenAI 风格的探测正常，但运行时 `claude-*` 请求失败，最常见原因是之前向导运行时留下的过期 `model.entra.scope` 设置——请从 `config.yaml` 中删除 `entra.scope` 这一行，这样运行时就会回退到默认的 `https://ai.azure.com/.default` 范围。

## 相关内容

- [环境变量](/reference/environment-variables)
- [配置](/user-guide/configuration)
- [AWS Bedrock](/guides/aws-bedrock)——另一项主要的云服务提供商集成方案
- [Microsoft：为 Foundry 配置 Entra ID](https://learn.microsoft.com/azure/ai-foundry/foundry-models/how-to/configure-entra-id)——无密钥路径的相关上游文档
