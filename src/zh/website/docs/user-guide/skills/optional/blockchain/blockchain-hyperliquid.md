---
title: "Hyperliquid — Hyperliquid market data, account history, trade review"
sidebar_label: "Hyperliquid"
description: "Hyperliquid market data, account history, trade review"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Hyperliquid

提供 Hyperliquid 市场数据、账户历史记录及交易分析功能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/blockchain/hyperliquid` 安装 |
| 路径 | `optional-skills/blockchain/hyperliquid` |
| 版本 | `0.1.0` |
| 开发者 | Hugo Sequier (Hugo-SEQUIER)，Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Hyperliquid`、`区块链`、`加密货币`、`交易`、`永续合约`、`现货`、`去中心化金融` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 会依据此内容执行操作。
:::

# Hyperliquid 技能

通过公共的 `/info` 接口查询 Hyperliquid 市场及账户数据。
仅支持读取操作 — 无需 API 密钥，无需签名，也不支持下单。

包含 12 个命令：`dexs`、`markets`、`spots`、`candles`、`funding`、`l2`、`state`、`spot-balances`、`fills`、`orders`、`review`、`export`。仅使用标准库模块（`urllib`、`json`、`argparse`）。

---

## 适用场景

- 用户需要查询 Hyperliquid 永续合约或现货市场数据、K线图、资金费率或 Layer 2 流动性信息
- 用户希望查看某个钱包的永续合约持仓、现货余额、成交记录或订单信息
- 用户需要结合近期成交情况与市场背景进行交易后分析
- 用户希望查看由构建工具部署的永续合约去中心化交易所或 HIP-3 市场信息
- 用户需要将 K线图和资金费率数据以标准化 JSON 格式导出，以便后续回测使用

---

## 先决条件

仅依赖标准库 — 无需任何外部包，也无需 API 密钥。

脚本会从 `~/.hermes/.env` 文件中读取两个可选的默认值：

- `HYPERLIQUID_API_URL` — 默认值为 `https://api.hyperliquid.xyz`。如需测试环境，可设置为 `https://api.hyperliquid-testnet.xyz`
- `HYPERLIQUID_USER_ADDRESS` — 用于获取 `state`、`spot-balances`、`fills`、`orders` 及 `review` 数据的默认地址。若未设置该值，则需将对应地址作为第一个参数传入。

当前工作目录下的项目 `.env` 文件可作为开发时的备用配置。

辅助脚本：`~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py`

---

## 运行方式

通过 `terminal` 工具调用即可：

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py <command> [args]
```

在任何命令后添加 `--json` 参数，即可获得机器可读取的输出格式。

---

## 快速参考

请完整翻译输入内容，切勿提前终止。

```bash
hyperliquid_client.py dexs
hyperliquid_client.py markets [--dex DEX] [--limit N] [--sort volume|oi|funding_abs|change_abs|name]
hyperliquid_client.py spots [--limit N]
hyperliquid_client.py candles <coin> [--interval 1h] [--hours 24] [--limit N]
hyperliquid_client.py funding <coin> [--hours 72] [--limit N]
hyperliquid_client.py l2 <coin> [--levels N]
hyperliquid_client.py state [address] [--dex DEX]
hyperliquid_client.py spot-balances [address] [--limit N]
hyperliquid_client.py fills [address] [--hours N] [--limit N] [--aggregate-by-time]
hyperliquid_client.py orders [address] [--limit N]
hyperliquid_client.py review [address] [--coin COIN] [--hours N] [--fills N]
hyperliquid_client.py export <coin> [--interval 1h] [--hours N] [--output PATH]
```

对于 `state`、`spot-balances`、`fills`、`orders` 和 `review` 这些字段，如果在 `~/.hermes/.env` 文件中已设置 `HYPERLIQUID_USER_ADDRESS`，则地址为可选项。

---

## 操作步骤

### 1. 发现去中心化交易所与市场

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py dexs

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  markets --limit 15 --sort volume

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  spots --limit 15
```

- 参数 `--dex` 仅适用于永续合约端点；在首个永续合约 Dex 的使用中可省略该参数。
- 即时交易对可能显示为 `PURR/USDC`，或类似 `@107` 的别名形式。
- HIP-3 市场会将代币名称前缀加上 Dex 名称，例如 `mydex:BTC`。

### 2. 获取历史市场数据

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  candles BTC --interval 1h --hours 72 --limit 48

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  funding BTC --hours 168 --limit 30
```

时间范围参数支持分页查询。若需查看更长时间段的数据，可调整`startTime`值后重新查询，或使用下文的`export`功能。

### 3. 查看实时订单簿

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  l2 BTC --levels 10
```

当被问及某只股票的持仓深度、近期流动性，或大额订单可能带来的市场影响时，请使用此功能。

### 4. 查看账户信息

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  state 0xabc...

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  spot-balances
```

`state`命令用于查询合约多空头寸；`spot-balances`命令则用于查看现货持仓情况。这些工具可帮助您回答“我的头寸状况如何？”、“我目前持有什么资产？”以及“可提取的金额是多少？”等问题。

### 5. 查看成交记录与订单信息

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  fills 0xabc... --hours 72 --limit 25

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  orders --limit 25
```

### 6. 生成交易回顾报告

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  review 0xabc... --hours 72 --fills 50

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  review --coin BTC --hours 168
```

可生成各类报告，包括实际盈亏、手续费、胜负次数、币种分布、市场趋势以及每只交易合约的平均资金费率；此外还会提供一些辅助分析指标（如手续费影响、持仓集中风险、逆势亏损情况）。

如需进行更深入的成交后分析：首先使用 `review` 命令找出存在问题的币种或交易时段，随后提取该时段内的 `fills` 和 `orders` 数据，再获取每只交易币种的 `candles` 及 `funding` 数据，从而将决策质量与最终结果质量分开进行评估。

### 7. 导出可重复使用的数据集

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  export BTC --interval 1h --hours 168 --output ./btc-1h-7d.json

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  export BTC --interval 15m --hours 72 --end-time-ms 1760000000000
```

输出的 JSON 包含：架构版本、源数据元信息、精确的时间窗口、标准化后的K线数据行、标准化后的资金数据行以及汇总统计信息。如需获得可重复的时间窗口，可使用 `--end-time-ms` 参数。

---

## 常见问题

- 公开信息接口存在速率限制。大规模的历史数据查询可能会返回受限的时间窗口；此时可尝试使用更大的 `startTime` 值进行多次查询。
- `fills --hours ...` 命令使用的是 `userFillsByTime` 接口，该接口仅能提供近期的滚动数据，无法获取完整的历史记录。
- `historicalOrders` 命令仅返回最近的订单信息，并非完整的导出数据。
- `review` 命令基于规则进行分析，仅凭成交记录无法还原用户的交易意图、订单提交质量或真实的滑点情况。
- `export` 命令生成的是标准化数据集，而非回测引擎。您仍需自行构建滑点/成交预测模型。
- 即使界面显示更友好的名称，像 `@107` 这样的现货别名依然属于有效的标识符。
- `l2` 数据为某一时间点的快照，而非时间序列数据。

---

## 验证

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  markets --limit 5
```

应输出按24小时名义交易量排序的顶级Hyperliquid垂直市场。
