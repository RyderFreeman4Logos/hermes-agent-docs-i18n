---
name: here.now
description: Publish sites to {slug}.here.now and store files in Drives.
version: 1.15.3
author: here.now
license: MIT
prerequisites:
  commands: [curl, file, jq]
platforms: [macos, linux]
metadata:
  hermes:
    tags: [here.now, herenow, publish, deploy, hosting, static-site, web, share, URL, drive, storage]
    homepage: https://here.now
    requires_toolsets: [terminal]
---

# here.now

here.now 允许智能体在云端存储中发布网站并保存私有文件。

该功能可用于完成以下两项任务：

- **网站发布**：将网站及文件发布至 `{slug}.here.now` 地址。
- **云存储管理**：在云端文件夹中存储智能体的私有文件。

## 当前文档

**在回答与 here.now 的功能、特性或工作流程相关的问题之前，请先阅读最新文档：**

→ **https://here.now/docs**

建议在以下情况下阅读文档：
- 对话中首次涉及 here.now 相关内容时
- 用户询问某项操作的执行方法时
- 用户询问哪些功能可用、受支持或被推荐使用时
- 在告知用户某项功能不受支持之前

以下主题需要参考最新文档（不可仅依赖本地技能文本）：
- 云存储及共享功能
- 自定义域名
- 支付及相关机制
- 分支功能
- 代理路由与服务变量
- 文件名与链接处理
- 使用限制与配额
- 单页应用路由
- 错误处理与解决方案
- 功能可用性

**若文档内容与实时 API 行为存在差异，请以实时 API 的实际表现为准。**

如果文档加载失败或超时，可继续依据本地技能逻辑以及实时 API/脚本的输出结果进行操作。对于正在进行的操作，建议优先遵循实时 API 的行为规范。

## 系统要求

- 必需的二进制工具：`curl`、`file`、`jq`
- 可选的环境变量：`$

```bash
PUBLISH="${HERMES_SKILL_DIR}/scripts/publish.sh"
bash "$PUBLISH" {file-or-dir} --client hermes
```

会输出该网站的在线地址（例如：`https://bright-canvas-a7k2.here.now/`）。

其内部处理流程分为三步：创建/更新 -> 上传文件 -> 完成配置。只有当“完成配置”步骤成功后，网站才会正式上线。

若未使用 API 密钥，则会创建一个**匿名网站**，且该网站的有效期为 24 小时。而使用已保存的 API 密钥，则可创建永久性的网站。

**文件结构：** 对于 HTML 网站，请将 `index.html` 文件放在发布目录的根目录下，而非子目录中。该目录的内容即构成网站的根目录。例如，应在存在 `my-site/index.html` 的 `my-site/` 目录下进行发布——切勿发布包含 `my-site/` 子目录的父级文件夹。

您也可以直接发布不包含 HTML 的原始文件。单个文件会自动生成丰富的预览功能（支持图片、PDF、视频、音频格式）。多个文件则会被自动生成目录列表，同时提供文件夹导航和图片画廊功能。

## 更新现有网站

```bash
PUBLISH="${HERMES_SKILL_DIR}/scripts/publish.sh"
bash "$PUBLISH" {file-or-dir} --slug {slug} --client hermes
```

在更新匿名站点时，该脚本会自动从 `.herenow/state.json` 中加载 `claimToken`。如需覆盖此值，可使用 `--claim-token {token}` 参数。

进行需要身份验证的更新时，则必须使用已保存的 API 密钥。

## 使用驱动器

当用户希望为智能体文件提供私有云存储空间时，可使用驱动器。这些文件包括文档、上下文信息、内存数据、计划方案、资源文件、媒体资料、研究内容、代码，以及任何无需以网站形式公开即可长期保存的内容。

每个已登录账户都拥有一个名为 “My Drive” 的默认驱动器。

```bash
DRIVE="${HERMES_SKILL_DIR}/scripts/drive.sh"
bash "$DRIVE" default
bash "$DRIVE" ls "My Drive"
bash "$DRIVE" put "My Drive" notes/today.md --from ./notes/today.md
bash "$DRIVE" cat "My Drive" notes/today.md
bash "$DRIVE" share "My Drive" --perms write --prefix notes/ --ttl 7d
```

在代理之间传递任务时，请使用作用域限定的 Drive 令牌。若收到包含 `herenow_drive` 的共享块，应将其 `token` 作为 `Authorization: Bearer <token>` 的值用于调用 `api_base`，同时需遵循所提供的 `pathPrefix` 规则，在进行写入操作时还需保留原有的 ETags。当 `pathPrefix` 设为 `null` 时，表示拥有对整个 Drive 的访问权限。若该技能支持使用 `drive.sh`，则优先采用该方式；否则请直接调用列出的 API 操作。

## API 密钥存储

发布脚本会从以下来源读取 API 密钥（优先使用第一个匹配到的来源）：

1. `--api-key {key}` 参数（仅适用于 CI/脚本环境——交互式使用时请避免使用）
2. `$HERENOW_API_KEY` 环境变量
3. `~/.herenow/credentials` 文件（推荐代理使用）

如需存储密钥，请将其写入该凭证文件中：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

**重要提示**：获取 API 密钥后，请立即将其保存——请自行运行上述命令，切勿让用户手动操作。在交互式会话中，请避免通过 CLI 参数（如 `--api-key`）传递该密钥；使用凭证文件才是更推荐的存储方式。

切勿将凭证或本地状态文件（如 `~/.herenow/credentials`、`.herenow/state.json`）提交到版本控制系统中。

## 获取 API 密钥

若要将匿名（24小时有效）站点升级为永久站点，请执行以下操作：

1. 询问用户的电子邮件地址。
2. 请求一个一次性登录验证码：

```bash
curl -sS https://here.now/api/auth/agent/request-code \
  -H "content-type: application/json" \
  -d '{"email": "user@example.com"}'
```

3. 告诉用户：“请查看您的收件箱，查看此处发送的登录验证码，然后将其粘贴到这里。”
4. 验证该验证码并获取 API 密钥：

```bash
curl -sS https://here.now/api/auth/agent/verify-code \
  -H "content-type: application/json" \
  -d '{"email":"user@example.com","code":"ABCD-2345"}'
```

5. 请自行保存返回的 `apiKey`（切勿要求用户执行此操作）：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

## 状态文件

每次创建或更新站点后，脚本都会将相关数据写入工作目录下的 `.herenow/state.json` 文件中：

```json
{
  "publishes": {
    "bright-canvas-a7k2": {
      "siteUrl": "https://bright-canvas-a7k2.here.now/",
      "claimToken": "abc123",
      "claimUrl": "https://here.now/claim?slug=bright-canvas-a7k2&token=abc123",
      "expiresAt": "2026-02-18T01:00:00.000Z"
    }
  }
}
```

在创建或更新站点之前，您可以查看此文件以获取之前的站点标识符。请将 `.herenow/state.json` 视为仅用于内部缓存的文件。切勿将该本地文件路径作为 URL 使用，也不应将其作为验证模式、有效期或声明地址的权威来源。

## 应如何告知用户

对于已发布的站点：

- 始终提供当前脚本运行生成的 `siteUrl`。
- 查看脚本标准错误输出中的 `publish_result.*` 行内容，以确定验证模式。
- 当 `publish_result.auth_mode=authenticated` 时，告知用户该站点为**永久性**存储，已保存在其账户中，无需提供声明地址。
- 当 `publish_result.auth_mode=anonymous` 时，告知用户该站点**24 小时后过期**。若 `publish_result.claim_url` 不为空且以 `https://` 开头，可提供该声明地址以便用户永久保存。同时需提醒用户，声明令牌仅会生成一次，且无法找回。
- 绝对不要建议用户通过查看 `.herenow/state.json` 来获取声明地址或验证状态。

对于 Drive 功能：

- 不要将 Drive 文件描述为公共 URL。
- 告知用户，除非使用带有限定范围的令牌进行共享，否则 Drive 内容为私密状态。
- 在与其他代理共享访问权限时，建议使用限定范围较窄且有效期较短的令牌。

## publish.sh 参数说明

| 参数                  | 描述                                      |
| ---------------------- | ------------------------------------------ |
| `--slug {slug}`        | 更新现有站点而非新建                        |
| `--claim-token {token}`| 为匿名更新覆盖声明令牌                    |
| `--title {text}`       | 查看器标题（非 HTML 站点使用）             |
| `--description {text}` | 查看器描述                              |
| `--ttl {seconds}`      | 设置有效期（仅适用于已验证用户）           |
| `--client {name}`      | 用于归属标识的代理名称（例如 `hermes`）    |
| `--base-url {url}`     | API 基础 URL（默认值：`https://here.now`）    |
| `--allow-nonherenow-base-url` | 允许向非默认的 `--base-url` 发送验证信息   |
| `--api-key {key}`      | 覆盖 API 密钥（优先使用凭证文件）           |
| `--spa`                | 启用单页应用路由（对未知路径返回 index.html） |
| `--forkable`           | 允许他人复制该站点                        |

## 除 publish.sh 之外的功能

对于 Drive 操作，可使用 `drive.sh` 或 Drive API。如需进行更广泛的账户及站点管理——包括删除、元数据管理、密码设置、支付处理、域名管理、用户名管理、链接管理、变量设置、代理路由配置、站点复制等功能——请参阅最新文档：

→ **https://here.now/docs**

完整文档地址：https://here.now/docs
