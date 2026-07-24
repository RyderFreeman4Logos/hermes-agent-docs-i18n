---
title: "Solana — Query Solana wallets, tokens, txs, and NFTs in USD"
sidebar_label: "Solana"
description: "Query Solana wallets, tokens, txs, and NFTs in USD"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Solana

查询 Solana 钱包、代币、交易记录及 NFT 的相关信息，并以美元价格呈现。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/blockchain/solana` 安装 |
| 路径 | `optional-skills/blockchain/solana` |
| 版本 | `0.2.0` |
| 开发者 | Deniz Alagoz (gizdusum)，由 Hermes Agent 增强功能 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Solana`、`区块链`、`加密货币`、`Web3`、`RPC`、`去中心化金融`、`NFT` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。技能运行时，Agent 就会依据这些指令来执行操作。
:::

# Solana 区块链技能

通过 CoinGecko 获取数据，查询 Solana 网络上的信息，并以美元价格进行标注。
提供 8 种命令：钱包资产组合查询、代币信息查询、交易记录查询、网络活动查询、NFT 查询、大额转账检测、网络统计查询以及价格查询。

无需 API 密钥，仅使用 Python 标准库（urllib、json、argparse）即可运行。

---

## 适用场景

- 用户询问 Solana 钱包余额、代币持有量或资产组合价值
- 用户希望根据签名查看特定交易记录
- 用户需要了解 SPL 代币的元数据、价格、供应量或主要持有者信息
- 用户想要查询某个地址的最新交易历史
- 用户想了解某个钱包所拥有的 NFT
- 用户希望检测大额 SOL 转账行为（即识别大额转账者）
- 用户想要了解 Solana 网络的健康状况、每秒交易处理量、当前时代编号或 SOL 价格
- 用户询问“BONK/JUP/SOL 的价格是多少？”

---

## 前提条件

该辅助脚本仅使用 Python 标准库（urllib、json、argparse），无需任何外部包。

价格数据来自 CoinGecko 的免费 API（无需密钥，但每分钟请求次数有限，约为 10-30 次）。如需更快速的查询速度，可使用 `--no-prices` 参数。

---

## 快速参考

RPC 接口地址（默认）：https://api.mainnet-beta.solana.com
如需自定义地址，请执行：export SOLANA_RPC_URL=https://your-private-rpc.com

辅助脚本路径：~/.hermes/skills/blockchain/solana/scripts/solana_client.py

```
python3 solana_client.py wallet   <address> [--limit N] [--all] [--no-prices]
python3 solana_client.py tx       <signature>
python3 solana_client.py token    <mint_address>
python3 solana_client.py activity <address> [--limit N]
python3 solana_client.py nft      <address>
python3 solana_client.py whales   [--min-sol N]
python3 solana_client.py stats
python3 solana_client.py price    <mint_or_symbol>
```

## 操作步骤

### 0. 设置检查

```bash
python3 --version

# Optional: set a private RPC for better rate limits
export SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"

# Confirm connectivity
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```

### 1. 钱包资产组合

可查看SOL余额、以美元计价的SPL代币持有量、NFT数量以及资产组合总价值。代币会按价值进行排序，已忽略无价值代币，且常见的代币会标注其名称（如BONK、JUP、USDC等）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

标志选项：
- `--limit N` — 显示前 N 个代币的信息（默认值：20）
- `--all` — 显示所有代币信息，不进行无用数据过滤且无数量限制
- `--no-prices` — 跳过对 CoinGecko 的价格查询（速度更快，仅通过 RPC 获取数据）

输出内容包括：SOL 存款余额及其对应的美元价值、按价值排序的带价格的代币列表、无用数据数量、NFT 概要信息，以及以美元计价的整体投资组合价值。

### 2. 交易详情

可通过 Base58 签名查看完整的交易信息。该功能会显示 SOL 和美元两种货币形式的余额变动情况。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  tx 5j7s8K...your_signature_here
```

输出内容包括：槽位信息、时间戳、费用、状态、余额变动情况（SOL及USD计价）、以及程序调用记录。

### 3. 代币信息

可获取SPL代币的元数据、当前价格、市值、供应量、小数位数、铸造/冻结权限，以及前5大持有者信息。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  token DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

输出内容包括：名称、符号、小数位、供应量、价格、市值，以及占比最高的前5名持有者。

### 4. 最近活动记录

列出某个地址的近期交易记录（默认显示最近10笔，最多显示25笔）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  activity 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --limit 25
```

### 5. NFT 投资组合

列出钱包所拥有的 NFT（判定规则：SPL 类代币且数量为 1、小数位为 0）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  nft 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

注意：该检测规则无法识别压缩型非同质化代币（cNFT）。

### 6. 大额资金追踪器

扫描最新区块中涉及高价值美元金额的SOL转账记录。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  whales --min-sol 500
```

注意：仅扫描最新的区块数据——属于时间点快照，不包含历史数据。

### 7. 网络统计信息

实时的 Solana 网络运行状况：当前时隙、时代周期、每秒交易量、货币供应量、验证节点版本、SOL 价格以及市值。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```

### 8. 价格查询

可通过代币的铸造地址或已知符号，快速查询任意代币的价格。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price BONK
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price JUP
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price SOL
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

已知符号：SOL、USDC、USDT、BONK、JUP、WETH、JTO、mSOL、stSOL、PYTH、HNT、RNDR、WEN、W、TNSR、DRIFT、bSOL、JLP、WIF、MEW、BOME、PENGU。

---

## 常见问题

- **CoinGecko 请求频率限制**——免费套餐允许每分钟约10-30次请求。查询价格时每个代币需1次请求。若钱包中包含大量代币，可能无法获取所有代币的价格。为提升速度，可使用`--no-prices`选项。
- **公共RPC 请求频率限制**——Solana主网公共RPC会对请求次数进行限制。如需在生产环境中使用，应将SOLANA_RPC_URL设置为私有端点（如Helius、QuickNode、Triton）。
- **NFT检测为启发式方法**——检测标准为数量=1且小数位=0。压缩型NFT（cNFT）以及2022年推出的Token型NFT将不会被识别。
- **巨鲸检测仅扫描最新区块**——不涵盖历史区块。检测结果会因查询时间不同而有所差异。
- **交易历史记录**——公共RPC仅保留约2天的交易记录，更早的交易可能无法查询到。
- **代币名称显示**——约25种知名代币会直接显示其名称，其他代币则显示简写的铸造地址。如需完整信息，请使用`token`命令。
- **遇到429错误时会自动重试**——无论是RPC请求还是对CoinGecko的调用，在遭遇请求频率限制错误时都会以指数退避策略最多重试2次。

---

## 验证

```bash
# Should print current Solana slot, TPS, and SOL price
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```
