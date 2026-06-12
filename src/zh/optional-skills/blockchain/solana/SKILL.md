---
name: solana
description: Query Solana blockchain data with USD pricing — wallet balances, token portfolios with values, transaction details, NFTs, whale detection, and live network stats. Uses Solana RPC + CoinGecko. No API key required.
version: 0.2.0
author: Deniz Alagoz (gizdusum), enhanced by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Solana, Blockchain, Crypto, Web3, RPC, DeFi, NFT]
    related_skills: []
---

# Solana 区块链技能

通过 CoinGecko 获取经过美元价格标注的 Solana 在链数据。
提供 8 种命令：钱包资产组合查询、代币信息查询、交易记录查询、活动动态查询、NFT 查询、大额转账检测、网络状态查询以及价格查询。

无需 API 密钥，仅使用 Python 标准库（urllib、json、argparse）即可运行。

---

## 适用场景

- 用户需要查询 Solana 钱包余额、代币持有量或资产组合价值
- 用户希望根据签名查看特定交易记录
- 用户需要了解 SPL 代币的元数据、价格、供应量或主要持有者信息
- 用户需要获取某个地址的最新交易历史
- 用户想要了解某个钱包拥有的 NFT 情况
- 用户需要检测大规模的 SOL 转账行为（大额转账检测）
- 用户希望了解 Solana 网络的健康状况、TPS 值、时代编号或 SOL 价格
- 用户询问“BONK/JUP/SOL 的价格是多少？”

---

## 先决条件

该辅助脚本仅使用 Python 标准库（urllib、json、argparse），无需任何外部包。

价格数据来自 CoinGecko 的免费 API（无需密钥，但每分钟请求限制在约 10-30 次）。如需更快的查询速度，可使用 `--no-prices` 参数。

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

可查看SOL余额、以美元计价的SPL代币持有量、NFT数量以及资产组合总价值。代币会按价值进行排序，已归零的微小代币会被过滤掉，常见的代币还会标注其名称（如BONK、JUP、USDC等）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

标志选项：
- `--limit N` — 显示前 N 个代币的信息（默认值：20）
- `--all` — 显示所有代币信息，不进行无用数据过滤，且无数量限制
- `--no-prices` — 跳过对 CoinGecko 的价格查询（速度更快，仅通过 RPC 实现）

输出内容包括：SOL 净值及对应的美元价值、按价值排序的带价格的代币列表、无用数据数量、NFT 概要信息，以及以美元计价的整体投资组合价值。

### 2. 交易详情

可通过 base58 签名查看完整的交易记录，同时显示 SOL 和美元形式的资产余额变化情况。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  tx 5j7s8K...your_signature_here
```

输出内容包括：插槽信息、时间戳、手续费、状态、余额变动情况（SOL及美元计价）、以及程序调用记录。

### 3. 代币信息

可获取SPL代币的元数据、当前价格、市值、供应量、小数位信息、铸造/冻结权限，以及前五大持有者名单。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  token DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

输出内容包括：名称、符号、小数位数、供应量、价格、市值，以及占比最高的前5名持有者信息。

### 4. 最近动态

列出某个地址的近期交易记录（默认显示最近10条，最多显示25条）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  activity 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --limit 25
```

### 5. NFT 投资组合

展示钱包所拥有的 NFT 列表（判定规则：代币类型为 SPL，数量为 1，小数位为 0）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  nft 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

注意：该检测规则无法识别压缩型非同质化代币（cNFT）。

### 6. 大额资金追踪器

用于扫描最新区块中涉及高价值美元金额的SOL大额转账记录。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  whales --min-sol 500
```

注意：仅扫描最新的区块数据——属于时间点快照，不包含历史数据。

### 7. 网络统计信息

实时的 Solana 网络状态：当前时隙、时代周期、每秒交易量、总供应量、验证节点版本、SOL 价格以及市值。

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

- **CoinGecko 的请求频率限制**——免费套餐允许每分钟约 10–30 次请求。查询价格时每个代币需占用 1 次请求，因此拥有大量代币的钱包可能无法获取所有代币的价格。如需提高速度，可使用 `--no-prices` 参数。
- **公共 RPC 的请求频率限制**——Solana 主网上的公共 RPC 会对请求数量进行限制。如需在生产环境中使用，建议将 SOLANA_RPC_URL 设置为私有端点（如 Helius、QuickNode、Triton）。
- **NFT 检测为经验性判断**——检测标准为数量=1 且小数位=0。经过压缩的 NFT（cNFT）以及 Token-2022 格式的 NFT 不会被识别出来。
- **巨鲸检测仅扫描最新区块**——不涵盖历史区块，因此检测结果会因查询时间的不同而有所差异。
- **交易历史记录**——公共 RPC 仅保留约 2 天的记录，更早的交易可能无法查询到。
- **代币名称显示**——约有 25 种知名代币会直接显示其名称，其他代币则仅显示简写的铸造地址。如需获取完整信息，请使用 `token` 命令。
- **遇到 429 错误时会自动重试**——无论是 RPC 请求还是对 CoinGecko 的调用，在遭遇请求频率限制错误时都会以指数退避策略最多重试 2 次。

---

## 验证

```bash
# Should print current Solana slot, TPS, and SOL price
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```
