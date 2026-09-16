---
title: "Polymarket — Query Polymarket: markets, prices, orderbooks, history"
sidebar_label: "Polymarket"
description: "Query Polymarket: markets, prices, orderbooks, history"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Polymarket

查询 Polymarket 的相关数据：市场信息、价格、订单簿及历史记录。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/finance/polymarket` 安装 |
| 路径 | `optional-skills/finance\polymarket` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent + Teknium |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。技能处于激活状态时，代理程序会依据此内容执行操作。
:::

# Polymarket — 预测市场数据

通过 Polymarket 提供的公共 REST API 查询预测市场数据。
所有接口均为只读性质，无需任何身份验证。

如需包含 curl 示例的完整接口参考，请参阅 `references/api-endpoints.md`。

## 适用场景

- 用户询问有关预测市场、投注赔率或事件概率的问题
- 用户想要了解“某件事发生的概率是多少？”
- 用户专门咨询 Polymarket 相关信息
- 用户需要获取市场价格、订单簿数据或价格历史记录
- 用户希望监控或追踪预测市场的动态变化

## 核心概念

- **事件**包含一个或多个**市场**（1对多关系）；
- **市场**具有二元结果，其价格以Yes/No形式呈现，数值范围在0.00到1.00之间；
- 这些价格实际上代表概率：价格0.65意味着该市场认为相应事件发生的概率为65%；
- `outcomePrices`字段：为JSON编码的数组，格式如下`["0.80", "0.20"]`；
- `clobTokenIds`字段：用于查询价格和订单簿的JSON编码数组，包含两个代币ID[Yes, No]；
- `conditionId`字段：用于查询价格历史记录的十六进制字符串；
- 交易量以USDC（美元）计价。

## 三个公共API

1. **Gamma API**，地址为`gamma-api.polymarket.com`——用于事件发现、搜索和浏览；
2. **CLOB API**，地址为`clob.polymarket.com`——提供实时价格、订单簿及历史数据；
3. **Data API**，地址为`data-api.polymarket.com`——用于查询交易记录和未平仓合约数量。

## 典型工作流程

当用户询问关于预测市场赔率的信息时：

1. 使用Gamma API的公共搜索端点根据用户的查询进行搜索；
2. 解析返回结果，提取出相关事件及其嵌套的市场信息；
3. 显示市场问题、以百分比形式呈现的当前价格以及交易量；
4. 若用户进一步询问，可深入分析——此时可使用`clobTokenIds`查询订单簿信息，使用`conditionId`查询历史记录。

## 结果展示方式

为便于理解，需将价格以百分比形式呈现：
- 若`outcomePrices`的值为`["0.652", "0.348"]`，则应显示为“Yes：65.2%，No：34.8%”；
- 必须同时展示市场问题及对应的概率值；
- 若有交易量数据，也需一并显示。

示例：`“X事件会发生吗？”——65.2%的概率为Yes，对应交易量为120万美元`

## 解析双重编码的字段

Gamma API会在JSON响应中以双重编码的形式，以JSON字符串的形式返回`outcomePrices`、`outcomes`和`clobTokenIds`。在使用Python处理时，可通过`json.loads(market['outcomePrices'])`来解析这些数据，从而获取实际的数组格式。

## 请求频率限制

限制较为宽松，正常使用情况下几乎不会达到上限：
- Gamma：每10秒4,000次请求（常规使用）
- CLOB：每10秒9,000次请求（常规使用）
- Data：每10秒1,000次请求（常规使用）

## 局限性

- 该功能为只读模式，不支持执行交易操作
- 进行交易需要通过基于钱包的加密认证（EIP-712签名）
- 部分新上线的市场可能没有价格历史记录
- 虽然交易存在地域限制，但只读数据可在全球范围内访问
