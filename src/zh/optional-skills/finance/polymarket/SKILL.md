---
name: polymarket
description: "Query Polymarket: markets, prices, orderbooks, history."
version: 1.0.0
author: Hermes Agent + Teknium
license: MIT
tags: [polymarket, prediction-markets, market-data, trading]
platforms: [linux, macos, windows]
---

# Polymarket — 预测市场数据

可通过 Polymarket 提供的公共 REST API 查询预测市场数据。
所有接口均为只读性质，无需任何身份验证。

如需包含 curl 示例的完整接口参考，请参阅 `references/api-endpoints.md`。

## 适用场景

- 用户询问有关预测市场、投注赔率或事件概率的问题
- 用户想要了解“X 发生的概率是多少？”
- 用户专门咨询 Polymarket 相关内容
- 用户需要获取市场价格、订单簿数据或价格历史记录
- 用户希望监控或追踪预测市场的动态变化

## 核心概念

- **事件**包含一个或多个**市场**（1:多关系）
- **市场**具有二元结果，对应的 Yes/No 赔率范围在 0.00 到 1.00 之间
- 赔率即概率：赔率为 0.65 表示市场认为该事件发生的概率为 65%
- `outcomePrices` 字段：以 JSON 格式存储的数组，例如 `["0.80", "0.20"]`
- `clobTokenIds` 字段：用于查询价格和订单簿的两个代币 ID 的 JSON 数组 [Yes, No]
- `conditionId` 字段：用于查询价格历史记录的十六进制字符串
- 所有交易量均以 USDC（美元）计价

## 三大公共 API

1. **Gamma API**，地址为 `gamma-api.polymarket.com` —— 用于发现、搜索和浏览功能
2. **CLOB API**，地址为 `clob.polymarket.com` —— 提供实时价格、订单簿及历史数据
3. **Data API**，地址为 `data-api.polymarket.com` —— 提供交易记录和未平仓合约信息

## 典型使用流程

当用户询问预测市场的赔率时：

1. 使用 Gamma API 的 public-search 接口，结合查询条件进行**搜索**。  
2. **解析**返回结果——提取相关事件及其嵌套的市场数据。  
3. **展示**市场问题、以百分比形式呈现的当前价格以及交易量。  
4. 如有需要可进行**深入分析**——此时可使用 clobTokenIds 获取订单簿信息，使用 conditionId 获取历史数据。  

## 结果展示方式

为便于阅读，需将价格以百分比形式呈现：  
- 若 `outcomePrices` 的值为 `["0.652", "0.348"]`，则应显示为“是：65.2%，否：34.8%”。  
- 必须同时展示市场问题及对应的概率值。  
- 如有交易量数据，也需一并显示。  

示例：`“X 会发生吗？”——65.2% 的概率为是（交易量为 120 万美元）。`  

## 解析双重编码的字段

Gamma API 会在 JSON 响应中以字符串形式返回 `outcomePrices`、`outcomes` 和 `clobTokenIds` 等数据，即这些数据本身是经过双重编码的。在使用 Python 处理时，需通过 `json.loads(market['outcomePrices'])` 的方式将其解析为真正的数组格式。  

## 请求频率限制

限制较为宽松，正常使用情况下几乎不会达到上限：  
- Gamma：每 10 秒允许 4,000 次请求（普通用途）。  
- CLOB：每 10 秒允许 9,000 次请求（普通用途）。  
- Data：每 10 秒允许 1,000 次请求（普通用途）。  

## 局限性

- 该功能仅为只读模式，不支持执行交易操作。  
- 进行交易需要基于钱包的加密认证（即 EIP-712 签名）。  
- 部分新上市的市场可能暂无价格历史数据。  
- 虽然只读数据可在全球范围内访问，但实际交易仍受地域限制。
