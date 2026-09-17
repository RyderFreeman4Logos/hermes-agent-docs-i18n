---
title: "Evm — Read-only EVM client: wallets, tokens, gas across 8 chains"
sidebar_label: "Evm"
description: "Read-only EVM client: wallets, tokens, gas across 8 chains"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Evm

只读型 EVM 客户端：支持查询 8 条区块链上的钱包信息、代币数据及燃气费用。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/blockchain/evm` 安装 |
| 路径 | `optional-skills/blockchain\evm` |
| 版本 | `1.0.0` |
| 开发者 | Mibayy (@Mibayy)、youssefea (@youssefea)、ethernet8023 (@ethernet8023)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `EVM`、`Ethereum`、`BNB`、`BSC`、`Base`、`Arbitrum`、`Polygon`、`Optimism`、`Avalanche`、`zkSync`、`Blockchain`、`Crypto`、`Web3`、`DeFi`、`NFT`、`ENS`、`Whale`、`Security` |
| 相关技能 | [`solana`](/docs/user-guide/skills/optional/blockchain/blockchain-solana) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 就会依据此内容执行操作。
:::

# EVM 区块链技能

可查询 8 条支持 EVM 的区块链数据，并提供以美元计价的费用信息。
包含 14 种命令：钱包资产查询、代币信息查询、交易记录查询、活动动态查询、燃气费用追踪、网络状态查询、价格查询、多链扫描、大额钱包检测、ENS 地址解析、授权状态检查、合约分析以及交易解码。

支持 8 条区块链：Ethereum、BNB Chain（BSC）、Base、Arbitrum One、Polygon、Optimism、Avalanche（C-Chain）、zkSync Era。

无需 API 密钥，也不存在任何外部依赖——仅依赖 Python 标准库（urllib、json、argparse、threading）即可。

> **该技能已取代独立的 `base` 技能。** 以往位于 `optional-skills/blockchain/base/` 下的与 Base 相关的令牌（AERO、DEGEN、TOSHI、BRETT、WELL、cbETH、cbBTC、wstETH、rETH）以及所有 Base RPC 功能，均已整合到此技能中。如需使用 Base 网络，可在任何命令后添加 `--chain base` 参数。

---

## 适用场景
- 用户查询任意 EVM 网络上的钱包余额或资产组合
- 用户希望一次性查看所有网络中同一钱包的状态
- 用户需要通过交易哈希来查询交易详情（或解析其操作内容）
- 用户需要获取 ERC-20 代币的元数据、价格、供应量或市值信息
- 用户希望查看某个地址的最新交易记录
- 用户需要了解当前的气费情况，或比较不同网络间的手续费差异
- 用户希望查找最近区块中发生的巨额转账行为
- 用户需要解析 ENS 域名（如 vitalik.eth）或反向查询地址信息
- 用户希望检查合约是否存在危险的代币授权设置
- 用户需要分析智能合约的详细信息（是代理合约？ERC-20？ERC-721？字节码大小是多少？）
- 用户希望在执行交易前比较不同网络间的气费成本

---

## 先决条件
仅需 Python 3.8 及以上版本的标准库，无需通过 pip 安装任何额外包。
费用说明：使用 CoinGecko 免费 API（有速率限制，约每分钟 10-30 次请求）。
ENS 支持：依靠 ensideas.com 的公共 API。
交易解析：依赖 4byte.directory 的公共 API。
如需自定义 RPC 接口地址，可设置 `export EVM_RPC_URL=https://your-rpc.com`。

辅助脚本路径：`~/.hermes/skills/blockchain/evm/scripts/evm_client.py`

```
SCRIPT=~/.hermes/skills/blockchain/evm/scripts/evm_client.py

# Network & prices
python $SCRIPT stats                            # Ethereum stats
python $SCRIPT stats --chain arbitrum           # Arbitrum stats
python $SCRIPT compare                          # Gas + prices ALL 8 chains

# Wallet
python $SCRIPT wallet 0xd8dA...96045            # Portfolio (ETH + ERC-20)
python $SCRIPT wallet 0xd8dA...96045 --chain bsc
python $SCRIPT multichain 0xd8dA...96045        # Same wallet on ALL chains

# Tokens & prices
python $SCRIPT price ETH
python $SCRIPT price 0xdAC1...1ec7              # By contract address
python $SCRIPT token 0xdAC1...1ec7              # ERC-20 metadata + market cap

# Transactions
python $SCRIPT tx 0x5c50...f060                 # Transaction details
python $SCRIPT decode 0x5c50...f060             # Decode input data (4byte.directory)
python $SCRIPT activity 0xd8dA...96045          # Recent transactions

# Gas
python $SCRIPT gas                              # Gas prices + cost estimates
python $SCRIPT gas --chain optimism

# Security
python $SCRIPT allowance 0xd8dA...96045         # Dangerous ERC-20 approvals
python $SCRIPT contract 0xdAC1...1ec7           # Contract inspection (proxy? standards?)

# ENS
python $SCRIPT ens vitalik.eth                  # Name -> address + profile
python $SCRIPT ens 0xd8dA...96045               # Address -> ENS name

# Whale detection
python $SCRIPT whale                            # Large transfers (last 20 blocks, >$10k)
python $SCRIPT whale --blocks 50 --min-usd 100000 --chain arbitrum
```

## 操作步骤

### 0. 设置检查
```bash
python --version   # 3.8+ required
python ~/.hermes/skills/blockchain/evm/scripts/evm_client.py stats
```

### 1. 钱包资产组合
显示原生代币余额以及已识别的 ERC-20 代币，按美元价值进行排序。
```bash
python $SCRIPT wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
python $SCRIPT wallet 0xd8dA... --chain bsc --no-prices   # faster
```

### 2. 多链扫描
通过线程技术，同时对同一地址在8条区块链上展开扫描。
```bash
python $SCRIPT multichain 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```
输出内容：每条链的本地余额 + 代币持有量 + 美元总价值。

### 3. 对比（Gas费用 + 价格）
同时查询全部8条区块链，显示成本最低/最高的区块链。
```bash
python $SCRIPT compare
```

### 4. 交易详情与解码
```bash
python $SCRIPT tx 0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060
python $SCRIPT decode 0x5c504ed...   # Shows human-readable function signature
```
Decode功能会使用4byte.directory将0xa9059cbb转换为transfer(address,uint256)格式。

### 5. ENS解析

需对完整的输入内容进行转换，不得提前终止处理。
```bash
python $SCRIPT ens vitalik.eth          # -> 0xd8dA... + avatar + social links
python $SCRIPT ens 0xd8dA...96045       # -> vitalik.eth
```

### 6. 准许度检查器（安全功能）
用于检测已授予已知去中心化交易所/桥接合约的 ERC-20 授权情况。
```bash
python $SCRIPT allowance 0xYourWallet
```
将该选项标记为“UNLIMITED approvals”，并将其风险等级设定为“HIGH”。 

### 7. 合同审查工具
```bash
python $SCRIPT contract 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48   # USDC (proxy)
python $SCRIPT contract 0xdAC17F958D2ee523a2206206994597C13D831ec7   # USDT (ERC-20)
```
可检测类型：代理合约（EIP-1967/EIP-1167）、ERC-20、ERC-721、ERC-165。同时会显示代理合约的字节码大小及实现地址。

### 8. 大额资产持有者检测
```bash
python $SCRIPT whale                                    # ETH, last 20 blocks, >$10k
python $SCRIPT whale --blocks 50 --min-usd 50000 --chain bsc
```

### 9. 燃气追踪器
```bash
python $SCRIPT gas
python $SCRIPT gas --chain polygon
```
显示以下操作所需的 gwei 价格及美元成本：转账、ERC-20 转账、授权、交换、NFT 发行、NFT 转让。

---

## 支持的链
| 键值       | 名称           | 原生代币 | 链 ID |
|-----------|----------------|--------|----------|
| ethereum  | Ethereum       | ETH    | 1        |
| bsc       | BNB Chain      | BNB    | 56       |
| base      | Base           | ETH    | 8453     |
| arbitrum  | Arbitrum One   | ETH    | 42161    |
| polygon   | Polygon        | POL    | 137      |
| optimism  | Optimism       | ETH    | 10       |
| avalanche | Avalanche C    | AVAX   | 43114    |
| zksync    | zkSync Era     | ETH    | 324      |

---

## 常见问题与注意事项
- CoinGecko免费套餐：每分钟约10–30次请求。如需加快钱包扫描速度，可使用`--no-prices`参数。
- 公共RPC节点可能存在流量限制。在正式环境中，建议将EVM_RPC_URL设置为私有端点。
- `wallet`和`allowance`功能仅会检查已知的代币列表（每条链约30种代币）。如需查找所有代币，可使用区块浏览器。
- `activity`功能仅扫描最近的区块（最多200个）。如需查看完整交易历史，请使用Etherscan API。
- `multichain`功能会同时运行8个并行线程，这可能会导致公共RPC节点出现流量限制。
- ENS解析依赖于一个固定的公共端点（ensideas.com / ens.vitalik.ca），且没有备用方案。若该端点不可用，`ens`功能将无法正常工作，建议稍后重试或使用区块浏览器。
- 交易解码同样依赖于一个固定的公共端点（4byte.directory），且没有备用方案。数据库中不存在的标识符会显示为“unknown”。
- **L2层的气费估算仅针对L2层的执行成本。**在Base、Arbitrum、Optimism和zkSync等rollup网络中，实际交易费用还包括取决于调用数据大小及当前L1层气费的L1层数据上传费。`gas`命令无法估算这部分L1层费用。对于Base网络，可参考该网络的L1层费用预言机（合约地址：`0x420000000000000000000000000000000000000F`）。
- 地址/交易哈希输入会经过验证，确保其以0x开头、长度正确且为十六进制格式，但不会强制要求遵循EIP-55校验和的大小写规范（RPC节点可接受任意大小写的十六进制字符串）。
```bash
# Should print current block, gas price, ETH price
python ~/.hermes/skills/blockchain/evm/scripts/evm_client.py stats

# Should resolve vitalik.eth to 0xd8dA...
python ~/.hermes/skills/blockchain/evm/scripts/evm_client.py ens vitalik.eth
```
