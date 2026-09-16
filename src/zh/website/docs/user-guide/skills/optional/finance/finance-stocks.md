---
title: "Stocks — Stock quotes, history, search, compare, crypto via Yahoo"
sidebar_label: "Stocks"
description: "Stock quotes, history, search, compare, crypto via Yahoo"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 股票信息

通过 Yahoo Finance 提供股票行情、历史数据、搜索、对比功能，同时支持加密货币相关查询。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/finance/stocks` 命令安装 |
| 路径 | `optional-skills/finance\stocks` |
| 版本 | `0.1.0` |
| 开发者 | Mibay (Mibayy)，Hermes Agent 团队 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Stocks`、`Finance`、`Market`、`Crypto`、`Investing` |
| 相关技能 | [`dcf-model`](/docs/user-guide/skills/optional/finance/finance-dcf-model)、[`comps-analysis`](/docs/user-guide/skills/optional/finance/finance-comps-analysis)、[`lbo-model`](/docs/user-guide/skills/optional/finance/finance-lbo-model) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，智能体所看到的指令即为此内容。
:::

# 股票信息技能

通过 Yahoo Finance 提供只读型市场数据。支持五种操作命令：`quote`、`search`、`history`、`compare`、`crypto`。仅依赖 Python 标准库，无需 API 密钥，也不需要通过 pip 安装任何组件。该功能使用的 Yahoo 接口为非官方接口，可能会受到流量限制或接口变更。

## 适用场景

- 用户查询当前股票价格（如 AAPL、TSLA、MSFT 等）  
- 用户希望根据公司名称查找股票代码  
- 用户需要获取某只股票的 OHLCV 数据或特定时间范围内的表现情况  
- 用户希望并列对比多只股票的走势  
- 用户查询加密货币价格（如 BTC、ETH、SOL 等）  

## 先决条件  

仅需 Python 3.8 及以上版本的标准库。可选：设置 `ALPHA_VANTAGE_KEY`，以便在 Yahoo 提供的受限制字段返回空值时，补充获取 `market_cap`、`pe_ratio` 以及 52 周最高/最低价等数据。免费密钥地址：https://www.alphavantage.co/support/#api-key  

## 运行方式  

通过 `terminal` 工具调用该功能。安装完成后即可使用：

```
SCRIPT=~/.hermes/skills/finance/stocks/scripts/stocks_client.py
python $SCRIPT quote AAPL
```

所有输出内容均为标准输出中的 JSON 格式——如需提取特定数据，可将其传递给 `jq` 工具进行处理。

## 快速参考

```
python $SCRIPT quote AAPL
python $SCRIPT quote AAPL MSFT GOOGL TSLA
python $SCRIPT search "Tesla"
python $SCRIPT history NVDA --range 6mo
python $SCRIPT compare AAPL MSFT GOOGL
python $SCRIPT crypto BTC ETH SOL
```

## 命令

### `quote SYMBOL [SYMBOL2 ...]`

显示当前价格、涨跌幅、涨跌幅百分比、交易量以及52周最高/最低价。

### `search QUERY`

根据公司名称查找股票代码。返回前5项信息：代码、公司名称、交易所类型及代码类别。

### `history SYMBOL [--range RANGE]`

显示每日开盘价、最高价、最低价、收盘价及成交量数据，同时提供统计信息（最小值、最大值、平均值、总回报百分比）。时间范围可选：`1mo`、`3mo`、`6mo`、`1y`、`5y`。默认值为`1mo`。

### `compare SYMBOL1 SYMBOL2 [...]`

以并列形式展示两只股票的当前价格、涨跌幅百分比以及52周表现情况。

### `crypto SYMBOL [SYMBOL2 ...]`

查询加密货币价格。输入`BTC`即可（脚本会自动添加`-USD`后缀）。

## 注意事项

- Yahoo Finance的API属于非官方接口。其端点地址可能会变更，也可能在未提前通知的情况下实施流量限制——如果请求开始失败，很可能是由此原因造成的。
- 当Yahoo的会话未正常建立时，使用`quote`命令查询`market_cap`和`pe_ratio`的值可能会返回`null`。此时可设置`ALPHA_VANTAGE_KEY`参数来补充这些数据。
- 在批量发送请求时，建议在每次请求之间添加短暂延迟，以避免触发流量限制。
- 该工具仅支持读取操作——无法下单，也无法与账户系统进行集成。

## 验证方式

```
python ~/.hermes/skills/finance/stocks/scripts/stocks_client.py quote AAPL
```

返回一个 JSON 对象，其中包含 `symbol: "AAPL"` 以及一个数值型的 `price` 字段。
