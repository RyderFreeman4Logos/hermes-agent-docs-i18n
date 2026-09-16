---
title: "Mpp Agent — Pay HTTP 402 APIs via Machine Payments Protocol (MPP)"
sidebar_label: "Mpp Agent"
description: "Pay HTTP 402 APIs via Machine Payments Protocol (MPP)"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Mpp Agent

通过机器支付协议（MPP）向返回 HTTP 402 错误的 API 发送支付请求。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/payments/mpp-agent` 安装 |
| 路径 | `optional-skills/payments\mpp-agent` |
| 版本 | `0.1.0` |
| 开发者 | Teknium (teknium1)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos |
| 标签 | `Payments`、`MPP`、`HTTP-402`、`Tempo`、`Stripe` |
| 相关技能 | [`stripe-link-cli`](/docs/user-guide/skills/optional/payments/payments-stripe-link-cli)、[`stripe-projects`](/docs/user-guide/skills/optional/payments/payments-stripe-projects) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，代理程序会将这些内容视为操作指令。
:::

# MPP Agent 技能

该技能会对机器支付协议（MPP，https://mpp.dev）的客户端进行封装，从而使 Hermes 能够针对那些返回 `HTTP 402 Payment Required` 错误的服务器，为每次 API 请求支付费用。

目前提供三种通过 npm 分发的客户端选项。请选择最轻量级且能满足用户需求的方案。由于 Windows 平台上的支付工具仍在完善中，该技能暂仅支持 `[linux, macos]` 平台。

## 适用场景

- 当商家 API 返回带有 `www-authenticate` 请求头的 `HTTP 402` 状态码时，用户希望实际完成支付，而不仅仅是记录响应信息。
- 用户要求“按请求付费”、“设置代理钱包”、“使用 Tempo/Privy/AgentCash”，或希望查找按 MPP 定价的服务。
- 当通过 Stripe Link 进行消费后产生了共享支付令牌（SPT），代理需要将其附加到 402 挑战中——在这种情况下，建议使用 `link-cli mpp pay`（详见 `stripe-link-cli` 技能）。

## 客户端选择

| 工具 | 适用场景 | 设置方式 |
|---|---|---|
| `link-cli` | 用户已配置 Stripe Link，或 402 挑战中指定了 `method="stripe"` | 见 `stripe-link-cli` 技能 |
| Tempo Wallet | 支持消费控制及服务搜索的 MPP 服务 | `tempo wallet login` |
| Privy Agent CLI | 多链钱包、基于浏览器的充值功能 | `privy-agent-wallets login` |
| AgentCash | 通过一个 USDC.e 账户访问 300 多种预定价 API | `npx agentcash onboard` |
| `mppx` | 开发与调试用途，依赖项最少 | 先执行 `npm install -g mppx`，再执行 `mppx account create` |

默认情况：如果用户已配置 Stripe Link，或 402 挑战中指定了 `method="stripe"`，则使用 `link-cli mpp pay`（即 `stripe-link-cli` 技能）。否则，对于一次性支付调用及调试场景可使用 `mppx`；而当用户需要持续的消费控制功能时，则推荐使用 Tempo Wallet。

## 先决条件

- `PATH` 环境中已安装 Node.js 20+ 版本  
- 已开通资金的钱包（Tempo / Privy / AgentCash）或 `mppx` 账户  
- 对于 Tempo / Privy / AgentCash，需按照其对应的入门指南操作：  
  - `https://tempo.xyz/SKILL.md`  
  - `https://agents.privy.io/skill.md`  
  - `https://agentcash.dev/skill.md`  

如果用户选择某款钱包，可使用 `web_extract` 工具获取相应的 SKILL.md 文件。  

## 操作步骤（mppx，最快路径）

通过 `terminal` 工具执行所有命令。  

### 1. 安装并创建账户

```
npm install -g mppx
mppx account create
```

请将生成的账户凭证存储在 CLI 指定的位置（CLI 会将其保存在自己的配置文件中——切勿将其粘贴到代理的记录中）。

### 2. 检查商家的 402 挑战请求

如果用户提供了某个 URL，请先对其进行检测，以确认该 URL 确实使用的是 MPP 协议：

```
curl -i <url>
```

真正的 MPP 402 看起来是这样的：

```
HTTP/1.1 402 Payment Required
www-authenticate: tempo amount=0.1 currency=...
```

### 3. 提交请求以进行支付

```
mppx <url>
```

对于非 GET 方法或请求体：

```
mppx <url> --method POST --data '<json>'
```

`mppx` 会自动处理 402 挑战与凭证验证流程，成功时还会输出商家的实际响应内容。

### 4. 验证收据

`mppx` 会自动添加收据头部信息。如需查看该信息，请：

```
mppx <url> -v
```

## 操作步骤（Tempo 钱包）

官方参考文档为 https://tempo.xyz/SKILL.md 中的 Tempo Wallet 技能说明；请使用 `web_extract` 工具获取该文档内容并据此操作。标题：

```
tempo wallet login
tempo wallet pay <url>
```

支出控制与服务发现功能均集成在 https://wallet.tempo.xyz 的钱包界面中。

## 常见问题

- **若请求未设置 `method="stripe"` 且返回 `HTTP 402`，则 Stripe Link 无法完成支付。** 如果验证流程仅支持 Tempo 或其他支付方式，请使用 `mppx`（或与用户钱包匹配的其他工具）——否则 Stripe Link 会拒绝该请求。反之，若验证流程指定了 `method="stripe"`，建议通过 `stripe-link-cli` 技能使用 Stripe Link，这样费用即可从用户已授权的信用卡中扣除。
- **一个请求头中包含多种支付方式。** `www-authenticate` 头可能列出多种支付方式（例如 `tempo, stripe`）。Link CLI 的 `mpp decode` 功能会优先选择 Stripe 方式，而 `mppx` 则会选择 Tempo 方式。并没有通用的“最佳”客户端——需根据用户已充值的钱包类型来选择。
- **零金额验证请求。** 某些 MPP 接口会收取 `$0.00` 的费用，仅要求提供验证凭证。此类请求无需使用已充值的钱包即可处理，不应将其视为“故障”而予以拒绝。
- **钱包密钥绝不会进入智能体上下文。** 四种客户端都会将密钥存储在各自的配置目录中（Privy 则会为每次会话生成临时密钥对），切勿使用 `cat`/`read_file` 等命令读取这些密钥。
- **服务器端 MPP 是另一种独立的技能。** 如果用户希望在自己的 API 中实现 402 验证功能，此技能并不适用——请引导他们前往 https://mpp.dev/quickstart/server，以及 `mppx/nextjs` / `mppx/hono` / `mppx/express` / `mppx/elysia` 等中间件文档。未来可能会推出专门的 `mpp-server` 技能。

## 验证方式

```
mppx --version && mppx account list
```

退出码为0表示该组件已成功安装，且存在对应的账户。
