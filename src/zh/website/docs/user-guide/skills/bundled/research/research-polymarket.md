---
title: "Polymarket — Query Polymarket: markets, prices, orderbooks, history"
sidebar_label: "Polymarket"
description: "Query Polymarket: markets, prices, orderbooks, history"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Polymarket

查询 Polymarket 的市场信息、价格、订单簿及历史数据。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/research/polymarket` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent + Teknium |
| 支持平台 | linux、macos、windows |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。当技能处于激活状态时，代理程序会将此内容视为操作指令。
:::

# Polymarket — 预测市场数据

通过 Polymarket 的公共 REST API 查询预测市场数据。
所有接口均为只读类型，无需任何身份验证。

如需包含 curl 示例的完整接口参考，请查看 `references/api-endpoints.md` 文件。

## 适用场景

- 用户询问关于预测市场、投注赔率或事件发生概率的问题
- 用户想要了解“X 发生的概率是多少？”
- 用户专门询问关于 Polymarket 的信息
- 用户需要获取市场价格、订单簿数据或价格历史记录
- 用户希望监控或追踪预测市场的动态变化

## 核心概念

- **事件**包含一个或多个**市场**（1:多关系）
- **市场**具有二元结果，对应的“是”/“否”价格范围在 0.00 到 1.00 之间
- 价格即概率：价格 0.65 表示市场认为该事件发生的概率为 65%
- `outcomePrices` 字段：以 JSON 编码的数组形式，例如 `["0.80", "0.20"]`
- `clobTokenIds` 字段：用于查询价格和订单簿的 JSON 编码数组，包含两个代币 ID [是, 否]
- `conditionId` 字段：用于查询价格历史记录的十六进制字符串
- 成交量以 USDC（美元）计价

## 三个公共 API

1. **Gamma API**，地址为 `gamma-api.polymarket.com` —— 用于发现、搜索和浏览功能
2. **CLOB API**，地址为 `clob.polymarket.com` —— 提供实时价格、订单簿及历史数据
3. **Data API**，地址为 `data-api.polymarket.com` —— 提供交易记录和未平仓合约数据

## 典型工作流程

当用户询问预测市场赔率时：

1. 使用 Gamma API 的 public-search 接口根据用户的查询内容进行搜索
2. 解析响应结果——提取事件及其嵌套的市场信息
3. 显示市场问题、以百分比形式呈现的当前价格以及成交量
4. 若用户进一步要求深入分析，则使用 `clobTokenIds` 查询订单簿，使用 `conditionId` 查询历史数据

## 结果展示方式

为便于阅读，需将价格以百分比形式呈现：
- `outcomePrices` 为 `["0.652", "0.348"]` 时，显示为“是：65.2%，否：34.8%”
- 必须同时显示市场问题及对应的概率值
- 若有成交量数据，也需一并展示

示例：`“X 会发生吗？”——65.2% 的概率为是（成交量达 120 万美元）`

## 解析双重编码的字段

Gamma API 会在 JSON 响应中以双重编码的形式，将 `outcomePrices`、`outcomes` 和 `clobTokenIds` 作为 JSON 字符串返回。使用 Python 处理时，需通过 `json.loads(market['outcomePrices'])` 来解析出实际的数组数据。

## 请求频率限制

限制较为宽松，正常使用情况下不太可能达到上限：
- Gamma API：每 10 秒允许 4,000 次请求（常规使用）
- CLOB API：每 10 秒允许 9,000 次请求（常规使用）
- Data API：每 10 秒允许 1,000 次请求（常规使用）

## 局限性

- 该技能为只读功能，不支持执行交易
- 进行交易需要基于钱包的加密身份验证（EIP-712 签名）
- 部分新创建的市场可能没有价格历史记录
- 虽然只读数据可全球访问，但交易功能存在地域限制
