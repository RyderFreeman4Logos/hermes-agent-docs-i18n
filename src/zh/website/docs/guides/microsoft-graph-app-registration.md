---
title: "Register a Microsoft Graph Application"
description: "Azure portal walkthrough for creating the app registration that powers the Teams meeting pipeline"
---

# 注册 Microsoft Graph 应用程序

Teams 会议处理流程会通过**仅限应用**（守护进程）身份验证方式，从 Microsoft Graph 中读取会议记录、录像及相关数据——无需用户登录，也无需为每次会议进行交互式授权。为此，需在 Azure AD 中注册应用程序，并授予管理员同意的应用程序权限。

本指南将详细介绍以下步骤：

1. 创建应用程序注册
2. 创建客户端密钥
3. 授予处理流程所需的 Graph API 权限
4. 由管理员对这些权限予以同意
5. （可选）通过应用程序访问策略将应用范围限制在特定用户

完成这些操作需要**租户管理员权限**（或由管理员代为授权）。请记住您收集的各个值，稍后需将其填写到 `~/.hermes/.env` 文件中。

## 先决条件

- 拥有 Teams Premium 或可生成会议记录与录像的 Teams 许可证的 Microsoft 365 租户
- 具有 [entra.microsoft.com](https://entra.microsoft.com) 上 Azure 门户的管理员访问权限
- 一个可用于接收 Graph 变更通知的公开 HTTPS 端点（稍后在 webhook 监听器步骤中设置）

## 步骤 1：创建应用程序注册

1. 以租户管理员身份登录 [entra.microsoft.com](https://entra.microsoft.com)。
2. 导航至 **Identity → Applications → App registrations**。
3. 点击 **New registration**。
4. 填写以下信息：
   - **Name**：`Hermes Teams Meeting Pipeline`（或任何您容易识别的名称）。
   - **Supported account types**：选择*仅此组织目录中的账户（单租户）*。
   - **Redirect URI**：保持空白——仅限应用身份验证无需该字段。
5. 点击 **Register**。

随后会进入应用程序概览页面。请复制以下两个值：

- **Application (client) ID** → `MSGRAPH_CLIENT_ID`
- **Directory (tenant) ID** → `MSGRAPH_TENANT_ID`

## 步骤 2：创建客户端密钥

1. 在左侧导航栏中，打开 **Certificates & secrets**。
2. 点击 **New client secret**。
3. **Description**：填写 `hermes-graph-secret`。**Expires**：选择一个与您的密钥轮换策略相匹配的期限（通常为 6 至 24 个月）。
4. 点击 **Add**。
5. 立即复制 **Value** 列中的内容——该值仅显示一次，其值为 `MSGRAPH_CLIENT_SECRET`。

> **Secret ID** 列并非密钥本身，您需要的是 **Value** 列。

## 步骤 3：授予 Graph API 权限

处理流程仅使用最基本的必需应用程序权限。只需添加实际需要的权限；每添加一个权限，应用就能读取更多整个租户范围内的数据。

1. 在左侧导航栏中，打开 **API permissions**。
2. 点击 **Add a permission** → **Microsoft Graph** → **Application permissions**。
3. 从下表中添加与处理流程功能相匹配的权限。
4. 添加完成后，点击 **Grant admin consent for `<your tenant>`**。每个权限的 **Status** 列应会变为绿色对勾标识。

### 用于生成基于记录的摘要所需权限

| 权限 | 该权限允许应用执行的功能 |
|------|--------------------------|
| `OnlineMeetings.Read.All` | 读取 Teams 在线会议的元数据（主题、参与者、加入链接）。 |
| `OnlineMeetingTranscript.Read.All` | 读取 Teams 生成的会议记录。 |

### 用于在无记录时使用录像作为备用方案所需权限

| 权限 | 该权限允许应用执行的功能 |
|------|--------------------------|
| `OnlineMeetingRecording.Read.All` | 下载 Teams 会议录像，以便离线进行语音转文字处理。 |
| `CallRecords.Read.All` | 当仅知道加入链接时，从通话记录中识别出相关会议。 |

### 用于向外发送摘要（仅 Graph 模式）所需权限

如果 `platforms.teams.extra.delivery_mode` 设置为 `graph`，处理流程将通过 Graph API 将摘要发布到 Teams 频道或聊天中。如果您使用的是 `incoming_webhook` 发送模式，则无需这些权限。

| 权限 | 该权限允许应用执行的功能 |
|------|--------------------------|
| `ChannelMessage.Send` | 代表应用向 Teams 频道发送消息。 |
| `Chat.ReadWrite.All` | 向一对一聊天和群组聊天发送消息（仅当您将 `chat_id` 设置为发送目标时有效）。 |

### 不推荐使用的权限

- 不带 `.All` 后缀的 `OnlineMeetings.ReadWrite.All` / `Chat.ReadWrite` —— 它们的权限范围超出了处理流程的实际需求。
- 委托权限——处理流程使用的是仅限应用（客户端凭据）的身份验证流程；没有用户登录的话，委托权限将无法正常工作。

## 步骤 4：（推荐）通过应用程序访问策略限制应用范围

默认情况下，像 `OnlineMeetings.Read.All` 这样的应用程序权限会允许应用访问租户中的**所有**会议。对于合作伙伴演示和开发测试环境来说这没问题；但在生产环境中，您几乎肯定希望限制应用可以读取哪些用户的会议。

Microsoft 正是为此提供了 Teams 的**应用程序访问策略**。该策略仅通过 PowerShell 界面管理，没有对应的门户界面。

在已安装并连接了 MicrosoftTeams 模块的管理员 PowerShell 环境中（执行 `Connect-MicrosoftTeams` 命令），即可进行操作：

```powershell
# Create a policy scoped to the Hermes app
New-CsApplicationAccessPolicy `
  -Identity "Hermes-Meeting-Pipeline-Policy" `
  -AppIds "<MSGRAPH_CLIENT_ID>" `
  -Description "Restrict Hermes meeting pipeline to allow-listed users"

# Grant the policy to specific users whose meetings the pipeline may read
Grant-CsApplicationAccessPolicy `
  -PolicyName "Hermes-Meeting-Pipeline-Policy" `
  -Identity "alice@example.com"

Grant-CsApplicationAccessPolicy `
  -PolicyName "Hermes-Meeting-Pipeline-Policy" `
  -Identity "bob@example.com"
```

权限授予后，消息传播可能需要长达30分钟的时间。可通过以下方式进行验证：

```powershell
Test-CsApplicationAccessPolicy -Identity "alice@example.com" -AppId "<MSGRAPH_CLIENT_ID>"
```

若未设置策略，**任何**用户的会议内容都将可被读取——这正是该权限在技术层面所赋予的权限。在生产环境租户中，请务必不要跳过此步骤。

## 第 5 步：将凭证写入您的环境配置文件

将您收集到的三个值放入 `~/.hermes/.env` 文件中：

```bash
MSGRAPH_TENANT_ID=<directory-tenant-id>
MSGRAPH_CLIENT_ID=<application-client-id>
MSGRAPH_CLIENT_SECRET=<client-secret-value>
```

设置文件权限，确保只有您自己能够读取该机密信息：

```bash
chmod 600 ~/.hermes/.env
```

## 第6步：验证令牌流流程

Hermes提供了图式认证的烟雾测试功能。您可以在已安装的Hermes环境中执行该测试：

```python
python -c "
import asyncio
from tools.microsoft_graph_auth import MicrosoftGraphTokenProvider
provider = MicrosoftGraphTokenProvider.from_env()
token = asyncio.run(provider.get_access_token())
print('Token acquired, length:', len(token))
print(provider.inspect_token_health())
"
```

当运行成功时，会输出一段较长的令牌字符串以及一个健康状态字典，其中显示 `cached: True`，且 `expires_in_seconds` 的值接近 3600。若运行失败，则会抛出带有 Azure 错误代码的 `MicrosoftGraphTokenError`，最常见的错误包括：

| Azure 错误 | 含义 | 解决方案 |
|-------------|------|----------|
| `AADSTS7000215: Invalid client secret` | 客户端密钥值不匹配或已过期。 | 在第 2 步中生成新的密钥，并更新 `.env` 文件。 |
| `AADSTS700016: Application not found` | `MSGRAPH_CLIENT_ID` 错误或租户不正确。 | 仔细核对第 1 步中的值，确保它们来自同一个应用。 |
| `AADSTS90002: Tenant not found` | `MSGRAPH_TENANT_ID` 中存在拼写错误。 | 从应用概览中再次复制目录（租户）ID。 |
| 调用时出现 `insufficient_claims`（并非令牌生成时） | 虽然获得了令牌，但 Graph 服务返回 401/403 错误。 | 可能是跳过了第 3 步的管理员同意流程，或是虽添加了权限但未重新进行同意操作。请重新检查 API 权限，然后再次点击 **Grant admin consent**。 |

## 客户端密钥轮换

Azure 客户端密钥具有固定的有效期。在当前密钥过期之前，请执行以下操作：

1. 在第 2 步中创建第二个客户端密钥，同时不要删除原来的密钥。
2. 将新的密钥值更新到 `~/.hermes/.env` 文件中的 `MSGRAPH_CLIENT_SECRET` 字段。
3. 重启网关以便使用新密钥：执行 `hermes gateway restart`。
4. 通过上述测试用例进行验证。
5. 在 Azure 门户中删除旧的客户端密钥。

## 后续步骤

一旦凭据验证成功，可继续开展以下工作：

- **设置 Webhook 监听器** —— 部署用于接收 Graph 变更通知的 `msgraph_webhook` 网关平台。
- **配置流水线** —— 设置 Teams 会议流水线的运行时环境及操作员 CLI 工具。
- **结果输出** —— 将汇总信息发送回 Teams 频道或聊天窗口。

相关页面会与添加对应运行时组件的 PR 一同提供。此凭据设置是一个独立的先决条件，可提前安全地完成。
