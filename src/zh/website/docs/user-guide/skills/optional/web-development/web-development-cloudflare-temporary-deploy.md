---
title: "Cloudflare Temporary Deploy — Deploy a Worker live, no account, via wrangler --temporary"
sidebar_label: "Cloudflare Temporary Deploy"
description: "Deploy a Worker live, no account, via wrangler --temporary"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Cloudflare临时部署功能

无需创建账户，即可通过 `wrangler --temporary` 命令立即部署Worker。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/web-development/cloudflare-temporary-deploy` 安装 |
| 路径 | `optional-skills/web-development/cloudflare-temporary-deploy` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `cloudflare`、`workers`、`wrangler`、`deploy`、`temporary`、`agent`、`serverless`、`web-development` |

## 参考：完整SKILL.md内容

:::info
以下是Hermes在触发该技能时加载的完整技能定义。当技能处于激活状态时，Agent会看到这些指令作为操作指南。
:::

# Cloudflare临时部署技能

通过 `wrangler deploy --temporary` 命令，无需任何账户设置即可将Cloudflare Worker部署到 `workers.dev` 的在线地址。Cloudflare会自动创建一个临时账户完成部署，并生成一个有效期为60分钟的访问链接；未被领取的账户将会自动删除。这样一来，Agent便能在无需进行OAuth认证、注册操作或复制粘贴令牌的情况下，快速完成编写代码→部署→验证的完整流程。

该技能不支持生产环境部署（此类场景请使用 `wrangler login` 及永久账户），也不支持超出上述临时账户限制的Cloudflare非Worker类产品。

## 适用场景

当用户希望以下操作时，可加载此技能：

- **无需先创建Cloudflare账户即可将Agent编写的代码部署到在线地址** —— “直接部署并给我一个链接”
- 在**后台或自动运行会话中迭代开发**，因为浏览器端的OAuth步骤会中断流程
- 使用可临时获取的测试目标，快速**原型设计或测试Workers功能**
- 构建**自我验证的部署循环** —— 部署后通过 `curl` 获取在线地址，确认输出结果与代码一致后再重新部署

## 不适用场景

- **生产环境或CI/CD流程** → 应使用永久账户（`wrangler login` 或 `CLOUDFLARE_API_TOKEN`）。若存在任何认证凭证，`--temporary` 会报错。
- **Wrangler已处于登录状态** → 按设计要求，`--temporary` 会返回错误。仅当用户明确需要临时部署时，才需先运行 `wrangler logout`。
- **需要长期托管的场景** → 临时部署在60分钟后会被自动删除，除非有人领取该链接。

## 前提条件

- **Wrangler 4.102.0或更高版本**。该版本首次引入了 `--temporary` 参数，早期版本不支持此功能。可通过 `npx wrangler@latest --version` 进行验证。
- **Node 18+ / npm**（或 `npx`、`yarn`、`pnpm`）。无需全局安装，直接使用 `npx wrangler@latest` 即可。
- **不得存在Cloudflare认证凭证**。`--temporary` 仅在Wrangler未登录状态下有效：既不能进行OAuth登录，也不能设置 `CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_API_KEY` 环境变量，同时不能有 `~/.wrangler`/`~/.config/.wrangler` 中缓存的OAuth信息。请直接使用 `terminal` 工具的现有环境，无需设置这些变量。
- 能够访问 `cloudflare.com` 和 `workers.dev` 的网络出口。
- 使用 `--temporary` 即表示用户已同意Cloudflare的服务条款和隐私政策。

## 执行步骤

每一步操作均需使用 `terminal` 工具。请始终指定具体版本（如 `wrangler@latest` 或 `wrangler@4.102.0` 及更高版本），以避免误用旧版本的Wrangler而缺少该参数。

1. **创建一个最简化的Worker模板**（如果项目已存在则可跳过此步）。Worker需要一个 `wrangler.toml`（或 `wrangler.jsonc`）文件以及入口脚本。以下是一个最简的TypeScript示例 —— 可使用 `write_file` 工具创建这些文件：

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
工作量证明检查会自动添加一段短暂的延迟。验证成功后，Wrangler会输出一行信息，显示`Account: <name> (created)`（或`(reused)`），以及`Claim URL`和实时的`https://<worker>.<account>.workers.dev`地址。

3. **解析该输出中的URL地址**。建议使用专用工具来可靠地提取这些地址，而非凭肉眼查看。
   ```
   npx wrangler@latest deploy --temporary 2>&1 | python3 scripts/parse_deploy_output.py
   ```
（将 `scripts/parse_deploy_output.py` 的路径解析为该技能的绝对路径。该脚本会输出 JSON 格式的数据：`{"live_url", "claim_url", "account", "account_state", "expires_minutes", "deployed"}`。）

4. **验证部署是否真正生效**——切勿仅依赖部署日志来判断。请使用 `curl` 访问实际运行地址，确认返回的内容与代码输出的结果一致：
   ```
   curl -sS <live_url>
   ```

5. **迭代优化。**修改代码后，使用相同的命令`npx wrangler@latest deploy --temporary`再次部署。在60分钟的时间窗口内，Wrangler会重用已缓存的临时账户（显示为“Account: <name> (reused)”），从而保持URL的稳定性。此时可再次使用`curl`命令来确认更改是否生效。

6. **将领取URL告知用户。**需告知用户：必须在60分钟内打开该URL，才能保留部署成果及相关资源；若未及时领取，所有内容将会自动删除。请将领取URL视为机密信息——它等同于账户的所有权凭证。

## 快速参考

| 步骤 | 命令 |
|---|---|
| 检查版本（需4.102.0及以上） | `npx wrangler@latest --version` |
| 无账户部署 | `npx wrangler@latest deploy --temporary` |
| 部署并解析URL | `npx wrangler@latest deploy --temporary 2>&1 \| python3 scripts/parse_deploy_output.py` |
| 验证实时状态 | `curl -sS <live_url>` |
| 清除缓存的临时账户 | `npx wrangler@latest logout` |

### 临时账户的产品限制

| 产品类型 | 临时账户的限制 |
|---|---|
| Workers | 可部署到`workers.dev` |
| 静态资源 | 最多1,000个文件，每个文件大小不超过5 MiB |
| KV存储 | 允许使用 |
| D1实例 | 支持1个数据库，每个数据库容量为100 MB，总计100 MB |
| 持久对象 | 允许使用 |
| Hyperdrive | 支持2种配置，最多10个连接 |
| 队列 | 最多10个 |
| SSL/TLS证书 | 允许使用 |

## 常见问题与注意事项

- **`--temporary`选项并未出现在`wrangler deploy --help`的列表中，也不是全局标志。**该选项是刻意隐藏的，会动态显示：当未经认证尝试执行`wrangler deploy`失败时，Wrangler会提示“请使用`--temporary`选项重新运行”。切勿仅因`--help`未列出该选项就认为其不存在——应检查软件版本。
- **过时的全局安装版本。**若全局安装的`wrangler`版本低于4.102.0，可能会隐式缺失该选项。务必使用`npx wrangler@latest`（或指定版本号≥4.102.0的版本）来确保控制软件版本。
- **已进行身份认证→会引发错误。**如果之前曾执行过`wrangler login`操作，或设置了`CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_API_KEY`环境变量，使用`--temporary`选项将会出错。此时要么为当前终端会话取消这些变量的设置，要么执行`wrangler logout`。绝不可在未告知用户的情况下移除其真实凭证。
- **速率限制。**过快创建临时账户会导致操作失败。应在60分钟时间窗口内重用已缓存的账户（只需再次部署），而非强制创建新账户；若遇到速率限制，可等待片刻或使用永久账户。
- **60分钟硬性时限，不可延长。**如果部署内容需要超过1小时才被访问，用户必须及时领取该资源。相关提示需明确告知用户。
- **重新部署后，`curl`可能会短暂返回旧内容。**`workers.dev`具有短暂的边缘缓存机制；即使`curl`显示的内容有几秒钟是过时的，但“(reused)”字样以及新的“Current Version ID”都能证明部署已成功。在判定重新部署失败之前，可再次执行`curl`命令，或添加用于清除缓存的查询字符串。
- **切勿将领取URL简单视为“普通链接”而记录在共享文档中。**它实际上等同于账户凭证。

## 验证方法

- 执行`npx wrangler@latest --version`，结果应显示版本号≥4.102.0。
- 执行`npx wrangler@latest deploy --temporary`，命令应输出`workers.dev`平台的实时URL以及用于领取资源的`claim-preview?claimToken=` URL。
- 执行`curl -sS <live_url>`，返回的内容应与Worker代码生成的输出完全一致。
- 再次部署后，系统应显示“Account: <name> (reused)”信息，且实时URL保持不变。
- 解析脚本的自我测试应通过：执行`python3 scripts/parse_deploy_output.py --selftest`。
