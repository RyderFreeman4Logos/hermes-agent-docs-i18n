---
title: "Cloudflare Temporary Deploy — Deploy a Worker live, no account, via wrangler --temporary"
sidebar_label: "Cloudflare Temporary Deploy"
description: "Deploy a Worker live, no account, via wrangler --temporary"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Cloudflare临时部署功能

无需创建账户，即可通过 wrangler --temporary 命令实时部署 Worker。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/web-development/cloudflare-temporary-deploy` 安装 |
| 路径 | `optional-skills/web-development\cloudflare-temporary-deploy` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `cloudflare`、`workers`、`wrangler`、`deploy`、`temporary`、`agent`、`serverless`、`web-development` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 就会看到这些指令作为操作指南。
:::

# Cloudflare临时部署技能

无需任何账户设置，即可通过 `wrangler deploy --temporary` 命令将 Cloudflare Worker 部署到 `workers.dev` 的实时地址上。Cloudflare 会创建一个临时账户完成部署，并生成一个有效期为60分钟的访问链接；未被使用的临时账户会自动删除。这样一来，Agent 即可在无需进行 OAuth 认证、注册操作或复制粘贴令牌的情况下，快速完成写入 → 部署 → 验证的全流程。

该技能不支持生产环境部署（此类场景请使用 `wrangler login` 及永久账户），也不涵盖超出上述临时账户限制的 Cloudflare 非 Worker 类产品。

## 适用场景

当用户希望：

- **无需先创建 Cloudflare 账户即可将代理编写的代码部署到实时网址**——只需执行“部署并生成链接”操作即可。  
- **在后台/自动化会话中进行迭代开发**，因为浏览器 OAuth 步骤会导致流程中断。  
- **利用可临时使用的目标地址快速原型设计或测试 Workers**。  
- **构建自我验证的部署循环**——部署代码后，通过 `curl` 获取实时网址的响应，确认输出与代码一致后再重新部署。  

## 不建议使用的场景

- **生产环境或 CI/CD 流水线** → 应使用永久账户（如 `wrangler login` 或 `CLOUDFLARE_API_TOKEN`）。若存在任何凭证，`--temporary` 参数会立即引发错误。  
- **Wrangler 已完成身份验证** → 按设计要求，`--temporary` 参数会返回错误。仅当用户明确希望使用临时部署时，才需先运行 `wrangler logout`。  
- **需要长期托管的场景** → 临时部署的文件在 60 分钟后会被自动删除，除非有人主动认领。  

## 先决条件

- **Wrangler 4.102.0 或更高版本**。该版本首次引入了 `--temporary` 参数，早期版本不支持此功能。可通过 `npx wrangler@latest --version` 查看当前版本号。
- **Node 18+ / npm**（或 `npx`、`yarn`、`pnpm`）。无需全局安装，直接使用 `npx wrangler@latest` 即可。
- **不得包含 Cloudflare 凭证**。`--temporary` 参数仅在 Wrangler 未进行身份验证时有效：不允许 OAuth 登录，不得设置 `CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_API_KEY` 环境变量，也不得存在 `~/.wrangler`/`~/.config/.wrangler` 中的 OAuth 缓存数据。请直接使用 `terminal` 工具的现有环境，无需设置上述变量。
- 需要能够访问 `cloudflare.com` 和 `workers.dev` 的网络出口。
- 使用 `--temporary` 参数即表示您已同意 Cloudflare 的服务条款和隐私政策。

## 运行步骤

每一步均需使用 `terminal` 工具。请始终指定具体版本（如 `wrangler@latest`、`wrangler@4.102.0` 或更高版本），以避免误用旧版全局安装的 Wrangler，从而导致该参数无法使用。

1. **创建一个最简 Worker 模板**（如果项目已存在则可跳过此步骤）。Worker 需要一个 `wrangler.toml`（或 `wrangler.jsonc`）文件以及一个入口脚本。以下是一个最简的 TypeScript 示例，可通过 `write_file` 函数生成这些文件：

   `wrangler.jsonc`：
   ```jsonc
   {
     "name": "hello-agent",
     "main": "src/index.ts",
     "compatibility_date": "2025-01-01"
   }
   ```

`src/index.ts`：
   ```typescript
   export default {
     async fetch(): Promise<Response> {
       return new Response("hello cloudflare");
     },
   };
   ```

2. 从项目目录中使用 `--temporary` 参数进行部署：
   ```
   npx wrangler@latest deploy --temporary
   ```
工作量证明检查会自动添加一段短暂的延迟。验证成功后，Wrangler会输出一行信息，显示“账户：<名称>（已创建）”（或“（已复用）”），同时还会给出“领取地址”以及实时可用的 `https://<worker>.<account>.workers.dev` 地址。

3. 从上述输出中**解析出这些网址**。建议使用专用工具来准确提取，而非凭肉眼查看。
   ```
   npx wrangler@latest deploy --temporary 2>&1 | python scripts/parse_deploy_output.py
   ```
（将 `scripts/parse_deploy_output.py` 解析为该技能的绝对路径。该脚本会输出 JSON 格式的数据：`{"live_url", "claim_url", "account", "account_state", "expires_minutes", "deployed"}`。）

4. **验证部署内容是否真正已上线**——切勿仅凭部署日志来判断。请使用 `curl` 访问实时 URL，并确认其返回的内容与代码输出的结果一致：
   ```
   curl -sS <live_url>
   ```

5. **迭代优化。**编辑代码后，使用相同的命令 `npx wrangler@latest deploy --temporary` 进行重新部署。在60分钟的时间窗口内，Wrangler会重用已缓存的临时账户（显示为“Account: <name> (reused)”），从而保持URL的稳定性。此时可再次使用 `curl` 命令来确认更改是否生效。

6. **将获取链接告知用户。**需告知用户：必须在60分钟内打开该链接，才能保留部署内容及所有相关资源；若未及时操作，所有内容将会自动删除。请将此获取链接视为机密信息——它决定了账户的所有权。

## 快速参考

| 步骤 | 命令 |
|---|---|
| 检查版本（需4.102.0及以上） | `npx wrangler@latest --version` |
| 无账户部署 | `npx wrangler@latest deploy --temporary` |
| 部署并解析URL | `npx wrangler@latest deploy --temporary 2>&1 \| python scripts/parse_deploy_output.py` |
| 验证链接是否可用 | `curl -sS <live_url>` |
| 清除缓存的临时账户 | `npx wrangler@latest logout` |

### 临时账户的产品限制

| 产品类型 | 临时账户的限制 |
|---|---|
| Workers | 可部署到 `workers.dev` 地址 |
| 静态资源 | 最多1,000个文件，每个文件大小不超过5 MiB |
| KV存储 | 支持使用 |
| D1实例 | 允许创建1个数据库，每个数据库容量为100 MB，总计上限为100 MB |
| 持久对象 | 支持使用 |
| Hyperdrive | 允许配置2种设置，最多支持10个连接 |
| 队列 | 最多可创建10个队列 |
| SSL/TLS证书 | 支持使用 |

## 常见问题与注意事项

- **`--temporary` 并未出现在 `wrangler deploy --help` 的列表中，也不属于全局标志。**该标志是刻意隐藏的，会动态显示：当未经身份验证的 `wrangler deploy` 操作失败时，Wrangler 会提示“使用 `--temporary` 重新运行”。切勿仅因 `--help` 中未列出该标志就认为其不存在——应检查软件版本。
- **过旧的全局 Wrangler 版本。** 已过时的全局安装版 Wrangler（版本 `< 4.102.0`）会默认不支持该标志。务必使用 `npx wrangler@latest`（或指定版本号 `>=4.102.0`）的命令来确保使用特定版本。
- **已登录状态 → 严重错误。** 如果曾经执行过 `wrangler login` 操作，或者设置了 `CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_API_KEY`，则使用 `--temporary` 会引发错误。此时要么为当前终端取消设置相关变量，要么执行 `wrangler logout`。绝不能在未告知用户的情况下删除其真实凭证。
- **速率限制。** 过快创建临时账户会导致操作失败。建议在 60 分钟时间内重复使用已缓存的账户（只需重新部署），而非强制创建新账户；若遇到速率限制，可等待片刻或使用永久账户。
- **60 分钟的硬性截止时间，不可延长。** 如果需要让部署结果持续超过一小时，用户必须主动接管该部署任务。相关提示应清晰明确地展示出来。
- **重新部署后，`curl` 可能会短暂显示旧内容。** `workers.dev` 拥有短暂的边缘缓存机制；即便 `curl` 显示过时的内容几秒钟，出现“(reused)”字样以及新的“当前版本号”即可证明部署已成功。在判定重新部署失败之前，建议再次执行 `curl` 命令，或添加用于清除缓存的查询字符串。
- **切勿将索赔链接仅作为“普通链接”记录在共享的日志中**。实际上它具有与凭证相同的敏感度。

## 验证步骤

- 运行 `npx wrangler@latest --version`，输出结果应大于或等于 `4.102.0`。
- 执行 `npx wrangler@latest deploy --temporary`，系统会输出 `workers.dev` 的实时访问地址以及带有 `claim-preview?claimToken=` 参数的索赔链接。
- 使用 `curl -sS <live_url>` 命令，可获取 Worker 代码生成的完整内容。
- 进行第二次部署时，系统会显示 `Account: <name> (reused)` 的提示，且实时访问地址保持不变。
- 解析脚本的自检功能可通过测试：运行 `python scripts/parse_deploy_output.py --selftest`。
