---
name: stocks
description: Stock quotes, history, search, compare, crypto via Yahoo.
version: 0.1.0
author: Mibay (Mibayy), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Stocks, Finance, Market, Crypto, Investing]
    category: finance
    related_skills: [dcf-model, comps-analysis, lbo-model]
---

# 股票功能

通过 Yahoo Finance 获取只读市场数据。提供五种命令：`quote`、`search`、`history`、`compare` 和 `crypto`。仅依赖 Python 标准库——无需 API 密钥，也无需通过 pip 安装任何包。该功能使用的 Yahoo 接口为非官方接口，可能存在速率限制或变更情况。

## 适用场景

- 用户询问某只股票的当前价格（如 AAPL、TSLA、MSFT 等）
- 用户希望根据公司名称查询股票代码
- 用户需要获取某只股票的 OHLCV 数据或特定时间范围内的表现数据
- 用户希望对比多只股票的各项指标
- 用户询问某种加密货币的价格（如 BTC、ETH、SOL 等）

## 前提条件

仅需 Python 3.8 及以上版本的标准库。可选：设置 `ALPHA_VANTAGE_KEY`，以便在 Yahoo 返回受保护字段为空时补充 `market_cap`、`pe_ratio` 以及 52 周最高/最低价等数据。免费密钥获取地址：https://www.alphavantage.co/support/#api-key

## 使用方法

通过 `terminal` 工具调用该功能。安装完成后即可使用：

```
SCRIPT=~/.hermes/skills/finance/stocks/scripts/stocks_client.py
python3 $SCRIPT quote AAPL
```

所有输出结果均为标准输出中的 JSON 格式——如需对内容进行筛选处理，可将其传递给 `jq` 工具。 

## 快速参考指南

```
python3 $SCRIPT quote AAPL
python3 $SCRIPT quote AAPL MSFT GOOGL TSLA
python3 $SCRIPT search "Tesla"
python3 $SCRIPT history NVDA --range 6mo
python3 $SCRIPT compare AAPL MSFT GOOGL
python3 $SCRIPT crypto BTC ETH SOL
```

## 命令

### `quote SYMBOL [SYMBOL2 ...]`

显示当前价格、涨跌幅、涨跌幅百分比、成交量以及52周最高/最低价。

### `search QUERY`

根据公司名称查找股票代码。返回前5个结果，包括：股票代码、公司名称、交易平台类型。

### `history SYMBOL [--range RANGE]`

展示每日的开盘价、最高价、最低价、收盘价及成交量数据，同时提供统计信息（最小值、最大值、平均值、总回报百分比）。时间范围可选：`1mo`、`3mo`、`6mo`、`1y`、`5y`。默认值为`1mo`。

### `compare SYMBOL1 SYMBOL2 [...]`

以并列形式展示两只股票的价格、涨跌幅百分比以及52周表现情况。

### `crypto SYMBOL [SYMBOL2 ...]`

查询加密货币价格。输入`BTC`即可（脚本会自动添加`-USD`后缀）。

## 注意事项

- Yahoo Finance的API属于非官方接口。其端点地址可能会变更，也可能在未经通知的情况下实施速率限制——如果请求开始失败，很可能是由此原因造成的。
- 当Yahoo的会话未建立时，使用`quote`命令查询`market_cap`和`pe_ratio`可能会返回空值。此时可设置`ALPHA_VANTAGE_KEY`来补充这些数据。
- 在批量发送请求时，请添加适当的延迟，以避免触发速率限制。
- 该工具仅支持读取操作——无法下单，也不支持账户集成。

## 验证方式

```
python3 ~/.hermes/skills/finance/stocks/scripts/stocks_client.py quote AAPL
```

返回一个 JSON 对象，其中包含 `symbol: "AAPL"` 以及一个数值类型的 `price` 字段。
