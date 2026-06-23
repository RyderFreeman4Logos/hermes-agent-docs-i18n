---
name: cloudflare-temporary-deploy
description: Deploy a Worker live, no account, via wrangler --temporary.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cloudflare, workers, wrangler, deploy, temporary, agent, serverless, web-development]
    category: web-development
---

# Cloudflare临时部署技能

通过使用`wrangler deploy --temporary`命令，无需进行任何账户设置即可将Cloudflare Worker部署到正在运行的`workers.dev`地址。Cloudflare会自动创建一个临时账户完成部署，并输出一个有效期为60分钟的访问链接；未被使用的临时账户将会自动删除。这样一来，智能体便能实现高效的“编写代码→部署→验证”流程，全程无需处理OAuth认证、注册操作或复制粘贴令牌。

该技能不支持正式环境部署（此类场景请使用`wrangler login`及永久账户），也不适用于超出上述临时账户限制的Cloudflare非Worker类产品。

## 适用场景

当用户希望实现以下需求时，可使用此技能：
- **无需先创建Cloudflare账户即可将智能体编写的代码部署到实时网址**——只需“完成部署并给我一个链接”
- 在**后台或自动运行会话中迭代开发**，因为浏览器端的OAuth步骤会阻碍流程推进
- 利用可临时获取的测试地址，快速构建原型或测试Cloudflare Worker功能
- 构建**自我验证的部署循环**——部署后通过`curl`调用实时网址，确认输出结果与代码一致后再重新部署

## 不适用场景

- **正式环境或CI/CD流程** → 应使用永久账户（通过`wrangler login`或`CLOUDFLARE_API_TOKEN`）。若存在任何认证凭证，`--temporary`选项将会报错。
- **Wrangler已处于登录状态** → 按设计要求，`--temporary`会返回错误。只有当用户明确需要临时部署时，才需先运行`wrangler logout`。
- **需要长期运行的托管服务** → 临时部署在60分钟后会被自动删除，除非有人访问该链接。

## 前提条件

- **Wrangler 4.102.0或更高版本**。此版本首次引入了`--temporary`选项，旧版本不支持该功能。可通过`npx wrangler@latest --version`命令进行版本验证。
- **Node 18+ / npm**（或`npx`、`yarn`、`pnpm`）。无需全局安装，直接使用`npx wrangler@latest`即可。
- **不得存在任何Cloudflare认证凭证**。`--temporary`仅在Wrangler未登录状态下有效：既不能进行OAuth登录，也不能设置`CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_API_KEY`环境变量，同时不能有存储在`~/.wrangler`或`~/.config/.wrangler`中的OAuth缓存。请直接使用“终端”工具的现有环境，无需手动设置这些变量。
- 网络能够访问`cloudflare.com`和`workers.dev`。
- 使用`--temporary`选项即表示用户同意遵守Cloudflare的服务条款和隐私政策。

## 操作步骤

每一步操作均需使用“终端”工具。请始终指定具体版本（如`wrangler@latest`或`wrangler@4.102.0`及以上版本），以避免意外使用缺少该选项的旧版全局Wrangler。
1. **创建一个最简化的Worker模板**（如果项目已存在则可跳过此步）。Worker需要一个`wrangler.toml`（或`wrangler.jsonc`）文件以及入口脚本。以下是一个最简的TypeScript示例，可通过`write_file`命令生成这些文件：

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
工作量证明检查会自动添加一段短暂的延迟。验证成功后，Wrangler会输出一行信息，显示`Account: <name> (created)`（或`(reused)`），同时还会给出`Claim URL`以及实时的`https://<worker>.<account>.workers.dev`地址。

3. **解析该输出中的URL地址**。建议使用专用工具来准确提取这些地址，而非凭肉眼查看。
   ```
   npx wrangler@latest deploy --temporary 2>&1 | python3 scripts/parse_deploy_output.py
   ```
（将 `scripts/parse_deploy_output.py` 解析为该技能的绝对路径。该脚本会输出 JSON 格式的数据：`{"live_url", "claim_url", "account", "account_state", "expires_minutes", "deployed"}`。）

4. **验证部署是否真正生效**——切勿仅凭部署日志就下结论。请使用 `curl` 访问实时地址，确认返回的内容与代码输出的结果一致：
   ```
   curl -sS <live_url>
   ```

5. **迭代优化。**编辑代码后，使用相同的命令`npx wrangler@latest deploy --temporary`重新部署。在60分钟的时间窗口内，Wrangler会重用缓存的临时账户（显示为“Account: <name> (reused)”），从而保证URL的稳定性。再次使用`curl`命令确认更改已生效。

6. **将领取URL提供给用户。**告知用户需在60分钟内打开该URL以保留部署结果及相关资源；若未及时领取，所有内容将会自动删除。请将领取URL视为机密信息——它代表着对该账户的所有权。

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
| D1数据库 | 允许1个数据库，每个数据库容量为100 MB，总计100 MB |
| 持久对象 | 允许使用 |
| Hyperdrive | 允许2个配置，最多10个连接 |
| 队列 | 最多10个 |
| SSL/TLS证书 | 允许使用 |

## 常见问题与注意事项

- **`--temporary`选项并未出现在`wrangler deploy --help`的列表中，也不是全局标志。**该选项是刻意隐藏的，会动态显示：当未经身份验证的`wrangler deploy`命令执行失败时，Wrangler会提示“请使用`--temporary`选项重新运行”。切勿仅因`--help`未列出该选项就认为其不存在——应检查软件版本。
- **使用了过旧的全球安装版Wrangler。**已过时的全局安装版Wrangler（版本低于4.102.0）可能默认不支持该选项。务必使用`npx wrangler@latest`命令（或指定版本号大于等于4.102.0的版本），从而确保能控制软件版本。
- **存在身份验证信息时会导致错误。**如果之前执行过`wrangler login`命令，或设置了`CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_API_KEY`环境变量，使用`--temporary`选项将会出错。此时要么为当前Shell会话取消设置这些变量，要么执行`wrangler logout`命令。绝不能在未告知用户的情况下移除其真实凭证。
- **速率限制问题。**过快创建临时账户会导致操作失败。建议在60分钟时间窗口内重用已缓存的账户（只需重新部署），而非强制创建新账户；若遇到速率限制，可等待片刻或使用永久账户。
- **临时账户有严格的60分钟有效期，且不可延长。**如果需要让部署结果长期保留，用户必须及时领取该账户。相关提示应明确告知用户。
- **重新部署后，`curl`命令可能会短暂返回旧内容。**`workers.dev`平台具有短暂的边缘缓存机制；即使`curl`显示的内容有几秒钟是过时的，但出现“(reused)”字样以及新的“Current Version ID”仍可证明部署已成功。在判定重新部署失败之前，建议再次执行`curl`命令，或添加查询字符串来清除缓存。
- **切勿将领取URL简单视为普通链接而记录在共享的日志中。**它实际上等同于账户凭证。

## 验证方法

- 执行`npx wrangler@latest --version`命令，结果应显示版本号大于等于4.102.0。
- 执行`npx wrangler@latest deploy --temporary`命令，应输出`workers.dev`平台的实时URL以及用于领取账户的URL`claim-preview?claimToken=`。
- 执行`curl -sS <live_url>`命令，返回的内容应与Workers代码生成的输出完全一致。
- 进行第二次部署后，应显示“Account: <name> (reused)”字样，且实时URL保持不变。
- 解析脚本的自我测试应通过：执行`python3 scripts/parse_deploy_output.py --selftest`命令。
