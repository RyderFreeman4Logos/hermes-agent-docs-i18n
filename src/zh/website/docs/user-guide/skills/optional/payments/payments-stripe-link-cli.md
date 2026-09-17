---
title: "Stripe Link Cli — Agent payments via Stripe Link — cards, SPT, approvals"
sidebar_label: "Stripe Link Cli"
description: "Agent payments via Stripe Link — cards, SPT, approvals"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Stripe Link CLI

通过 Stripe Link 实现代理支付——支持信用卡、共享支付令牌（SPT）以及审批流程。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/payments/stripe-link-cli` 安装 |
| 路径 | `optional-skills/payments\stripe-link-cli` |
| 版本 | `0.1.0` |
| 开发者 | Teknium (teknium1)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos |
| 标签 | `Payments`、`Stripe`、`Link`、`Checkout`、`MPP` |
| 相关技能 | [`mpp-agent`](/docs/user-guide/skills/optional/payments/payments-mpp-agent)、[`stripe-projects`](/docs/user-guide/skills/optional/payments/payments-stripe-projects) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能激活后，代理将看到这些指令作为操作指南。
:::

# Stripe Link CLI 技能

该技能基于 [@stripe/link-cli](https://github.com/stripe/link-cli) 开发，使 Hermes 能够使用一次性虚拟卡片或共享支付令牌（SPT）代表用户完成购买。每次消费都需通过 Link 移动端/网页应用内的审批流程——Hermes 无法自行批准。

目前仅支持美国地区（需拥有 Link 账户）。上游 CLI 不支持 Windows 系统，因此该技能仅限在 `[linux, macos]` 平台上使用。

## 适用场景

触发语句：

- “购买X”、“为X付款”、“完成购买”、“结束结账流程”  
- “给我一张卡片”、“我需要一种支付方式”  
- “登录Link账户”、“连接我的Link钱包”  
- 商家API返回HTTP 402错误，且包含`www-authenticate: ... method="stripe"`字段  

如果用户需要进行需要付费的API调用（出现HTTP 402错误且无结账表单），则表示使用的“卡片”路径有误——应通过同一技能使用SPT功能，或转交给`mpp-agent`技能处理。  

## 先决条件  

- `PATH`环境中已安装Node.js 20及以上版本（可通过`node --version`查看）  
- 账户需位于美国境内（需拥有Link账户）  

在Hermes尝试进行支付之前，无需预先设置Link账户、支付方式或支出审批应用——CLI会在首次运行时引导用户完成这些设置：  
- 一个Link账户，地址为https://app.link.com，可在首次使用`link-cli`进行身份验证时创建或关联  
- 至少一种支付方式，需在首次访问https://app.link.com/wallet时添加  
- Link移动端/网页应用，用于在收到首次支出请求时进行审批  

无需配置任何环境变量——CLI会在其自身的配置目录中本地存储身份验证状态。  

## 安装  

只需全局安装一次即可：

```
npm install -g @stripe/link-cli
```

或者通过 `npx @stripe/link-cli` 命令进行临时调用。下面的技能示例使用了已安装的 `link-cli` 工具。

## 运行方式

所有命令均通过 `terminal` 工具执行。CLI 会自动检测非 TTY 环境下的调用，并默认输出简洁的 `toon` 格式内容——这已足以满足模型的需求。如果某个步骤需要结构化字段，请使用 `--format json` 参数。

查看可用命令：`link-cli --llms-full`。
在调用前查看某条命令的架构：`link-cli <command> --schema`。

## 操作流程

### 1. 检查/建立认证

```
link-cli auth status
```

如果尚未完成身份验证，请使用明确的客户端名称登录（该名称会显示在用户的 Link 应用中）：

```
link-cli auth login --client-name "Hermes" --interval 5 --timeout 300
```

`--interval`/`--timeout` 模式采用轮询方式，因此代理无需管理 `_next` 步骤。只需将验证网址及短语打印给用户，然后等待 CLI 返回结果即可。

**在 `auth status` 显示登录成功之前，请勿继续执行后续步骤。**

### 2. 在创建消费请求前对商户进行评估

首先确定凭证类型：

| 商户界面 | `--credential-type` |
|---|---|
| 标准网页结账表单 / Stripe Elements | `card`（默认值） |
| 在 `www-authenticate` 中返回包含 `method="stripe"` 的 HTTP 402 响应 | `shared_payment_token` |
| 返回不包含 `method="stripe"` 的 HTTP 402 响应 | 不支持 —— 应立即停止 |

对于返回 402 响应的情况，切勿手动解码验证挑战信息。直接传递原始请求头即可：

```
link-cli mpp decode --challenge '<full WWW-Authenticate header>'
```

该步骤用于验证挑战请求，并提取网络标识符以及解码后的请求体。

### 3. 列出支付方式与配送选项

```
link-cli payment-methods list
link-cli shipping-address list
```

除非用户另有指定，否则请使用列表中的第一个选项。`payment-methods list` 中的 `id` 值即为您在后续步骤中需要使用的 `--payment-method-id` 参数。

### 4. 创建支出请求

在执行此命令之前，请先与用户确认最终金额。所有金额均以分为单位。

```
link-cli spend-request create \
  --payment-method-id <pm_id> \
  --merchant-name "<name>" \
  --merchant-url "<url>" \
  --context "<one sentence: what is being purchased and why>" \
  --amount <cents> \
  --line-item "name:<item>,unit_amount:<cents>,quantity:1" \
  --total "type:total,display_text:Total,amount:<cents>" \
  --request-approval
```

对于 MPP 商家，请添加 `--credential-type shared_payment_token` 参数。

`--request-approval` 会向用户的 Link 应用发送请求，并持续轮询直至用户同意或拒绝。若遭到拒绝或出现超时情况，CLI 的退出码将为非零值。

### 5. 安全地获取凭证

**切勿将卡片详细信息输出到标准输出。**请使用 `--output-file` 参数，这样卡号就永远不会出现在代理的记录或日志中：

```
link-cli spend-request retrieve <lsrq_id> \
  --include card \
  --output-file /tmp/link-card.json \
  --format json
```

该文件的权限设置为`0600`；标准输出仅显示已脱敏的字段（品牌名、卡号后四位、有效期），以及`card_output_file`的路径。

### 6. 使用凭证

- 对于网页支付场景：可将文件路径直接交给用户，或将其传递给能够直接从磁盘填充表单的浏览器驱动工具。绝不可通过`read_file`或`cat`命令将卡片文件内容读取到智能体的推理上下文中。
- 对于MPP商户：

  ```
  link-cli mpp pay <merchant-url> \
    --spend-request-id <lsrq_id> \
    --method POST \
    --data '<json body>'
  ```

### 7. 清理操作

交易完成后应立即删除卡片文件：

```
rm -f /tmp/link-card.json
```

## 可选：以 MCP 服务器模式运行

`@stripe/link-cli --mcp` 会通过标准输入输出提供与 MCP 工具相同的命令功能。若要将其注册到 Hermes 的原生 MCP 系统中：

```
hermes mcp add stripe-link --command "npx" --args "@stripe/link-cli --mcp"
```

此时执行 `hermes mcp list` 应会显示 `stripe-link`。其审批规则依然适用——MCP 并不会跳过 Link 应用的审批步骤。

## 常见问题

- **仅限美国地区。** 在美国以外，`auth login` 操作将会失败。请告知用户无需反复尝试。
- **卡号 PAN 绝对不能进入代理上下文。** 每次操作都必须使用 `--output-file` 参数。如果之前未使用该参数就已获取了卡号信息，仅执行 `link-cli auth logout` 是不够的——虽然该卡号为一次性使用，但遵循安全规范进行数据轮换依然十分重要。
- **`--request-approval` 会一直处于阻塞状态，直到用户采取操作。** 如果用户正在休息，CLI 会达到超时时间。请提前向用户说明这一点。
- **多步骤的 `_next` 命令。** 某些命令会返回 `_next.command`，必须执行该命令才能继续后续操作。如有疑问，建议优先使用内联轮询参数（`--interval`/`--timeout`）。
- 在非 TTY 模式下，输出格式默认为 `toon`。这种格式适用于普通文本，但如果后续步骤需要解析特定字段，请使用 `--format json` 参数。
- **不要默认选择 `card` 类型。** 设置商户评估步骤（第 2 节）的目的在于避免因选择错误的凭证类型而导致购买失败或泄露不必要的数据。

## 验证方法

```
link-cli --version && link-cli auth status
```

退出码为0表示已成功安装并完成登录。
