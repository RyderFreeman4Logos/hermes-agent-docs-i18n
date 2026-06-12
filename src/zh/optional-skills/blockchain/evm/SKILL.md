---
name: evm
description: "Read-only EVM client: wallets, tokens, gas across 8 chains."
version: 1.0.0
author: Mibayy (@Mibayy), youssefea (@youssefea), ethernet8023 (@ethernet8023), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [EVM, Ethereum, BNB, BSC, Base, Arbitrum, Polygon, Optimism, Avalanche, zkSync, Blockchain, Crypto, Web3, DeFi, NFT, ENS, Whale, Security]
    category: blockchain
    related_skills: [solana]
    requires_toolsets: [terminal]
---

# EVM区块链技能

可查询8条支持EVM的区块链数据，价格以美元计价。
提供14种命令：钱包资产组合查询、代币信息查询、交易查询、活动动态查询、燃气费追踪器、
网络统计信息查询、价格查询、多链扫描、大额转账检测、ENS域名解析、权限检查器、合约检测器以及交易解码器。

支持的区块链包括：Ethereum、BNB Chain（BSC）、Base、Arbitrum One、Polygon、Optimism、Avalanche（C-Chain）和zkSync Era。

无需API密钥，也不存在任何外部依赖——仅使用Python标准库（urllib、json、argparse、threading）即可。

> **该技能已取代独立的`base`技能。** 之前位于`optional-skills/blockchain/base/`目录下的Base链专用代币（AERO、DEGEN、TOSHI、BRETT、WELL、cbETH、cbBTC、wstETH、rETH）以及所有Base RPC功能，均已整合到此技能中。如需使用Base链相关功能，可在任意命令后添加`--chain base`参数。

---

## 适用场景
- 用户希望查询任意EVM区块链上的钱包余额或资产组合
- 用户想要一次性查看所有区块链上同一钱包的账户状况
- 用户需要通过哈希值检测某笔交易（或解析其操作内容）
- 用户需要了解ERC-20代币的元数据、价格、发行量或市值
- 用户希望查看某个地址的最新交易记录
- 用户需要了解当前燃气费，或比较不同区块链间的手续费差异
- 用户想要查找最近区块中的大额转账记录
- 用户希望解析ENS域名（如vitalik.eth）或反向查询地址信息
- 用户想要检查某个合约是否存在危险的代币授权设置
- 用户需要分析智能合约的详细信息（是代理合约？ERC-20？ERC-721？字节码大小是多少？）
- 用户希望在执行交易前比较不同区块链间的燃气费成本

---

## 先决条件
仅需Python 3.8及以上版本的标准库，无需通过pip安装任何额外包。
数据来源：CoinGecko免费API（有速率限制，约每分钟10-30次请求）。
ENS域名解析：ensideas.com公共API。
交易解码：4byte.directory公共API。
如需自定义RPC端点，可设置`export EVM_RPC_URL=https://your-rpc.com`。
辅助脚本路径：`~/.hermes/skills/blockchain/evm/scripts/evm_client.py`

---

## 快速参考

```
SCRIPT=~/.hermes/skills/blockchain/evm/scripts/evm_client.py

# Network & prices
python3 $SCRIPT stats                            # Ethereum stats
python3 $SCRIPT stats --chain arbitrum           # Arbitrum stats
python3 $SCRIPT compare                          # Gas + prices ALL 8 chains

# Wallet
python3 $SCRIPT wallet 0xd8dA...96045            # Portfolio (ETH + ERC-20)
python3 $SCRIPT wallet 0xd8dA...96045 --chain bsc
python3 $SCRIPT multichain 0xd8dA...96045        # Same wallet on ALL chains

# Tokens & prices
python3 $SCRIPT price ETH
python3 $SCRIPT price 0xdAC1...1ec7              # By contract address
python3 $SCRIPT token 0xdAC1...1ec7              # ERC-20 metadata + market cap

# Transactions
python3 $SCRIPT tx 0x5c50...f060                 # Transaction details
python3 $SCRIPT decode 0x5c50...f060             # Decode input data (4byte.directory)
python3 $SCRIPT activity 0xd8dA...96045          # Recent transactions

# Gas
python3 $SCRIPT gas                              # Gas prices + cost estimates
python3 $SCRIPT gas --chain optimism

# Security
python3 $SCRIPT allowance 0xd8dA...96045         # Dangerous ERC-20 approvals
python3 $SCRIPT contract 0xdAC1...1ec7           # Contract inspection (proxy? standards?)

# ENS
python3 $SCRIPT ens vitalik.eth                  # Name -> address + profile
python3 $SCRIPT ens 0xd8dA...96045               # Address -> ENS name

# Whale detection
python3 $SCRIPT whale                            # Large transfers (last 20 blocks, >$10k)
python3 $SCRIPT whale --blocks 50 --min-usd 100000 --chain arbitrum
```

## 操作步骤

### 0. 设置检查
```bash
python3 --version   # 3.8+ required
python3 ~/.hermes/skills/blockchain/evm/scripts/evm_client.py stats
```

### 1. 钱包资产组合
显示原生代币余额以及已识别的 ERC-20 代币，按美元价值进行排序。
```bash
python3 $SCRIPT wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
python3 $SCRIPT wallet 0xd8dA... --chain bsc --no-prices   # faster
```

### 2. 多链扫描
通过线程技术同时对同一地址在8条区块链上展开扫描。
```bash
python3 $SCRIPT multichain 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```
输出内容：各链的本地余额 + 代币持有量 + 美元总计。

### 3. 对比（Gas费用 + 价格）
同时查询全部8条区块链，显示成本最低/最高的区块链。
```bash
python3 $SCRIPT compare
```

### 4. 交易详情与解码
```bash
python3 $SCRIPT tx 0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060
python3 $SCRIPT decode 0x5c504ed...   # Shows human-readable function signature
```
Decode功能会利用4byte.directory将0xa9059cbb转换为transfer(address,uint256)的形式。

### 5. ENS解析
```bash
python3 $SCRIPT ens vitalik.eth          # -> 0xd8dA... + avatar + social links
python3 $SCRIPT ens 0xd8dA...96045       # -> vitalik.eth
```

### 6. 准许度检查器（安全功能）
用于核查已授予已知去中心化交易所/桥接合约的 ERC-20 授权情况。
```bash
python3 $SCRIPT allowance 0xYourWallet
```
将该选项设置为“UNLIMITED approvals”时，会将其风险等级标记为“高风险”。

### 7. 合同审查工具
```bash
python3 $SCRIPT contract 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48   # USDC (proxy)
python3 $SCRIPT contract 0xdAC17F958D2ee523a2206206994597C13D831ec7   # USDT (ERC-20)
```
可检测类型：代理合约（EIP-1967/EIP-1167）、ERC-20、ERC-721、ERC-165。同时会显示代理合约的字节码大小及实现地址。

### 8. 大额资金账户检测
```bash
python3 $SCRIPT whale                                    # ETH, last 20 blocks, >$10k
python3 $SCRIPT whale --blocks 50 --min-usd 50000 --chain bsc
```

### 9. 燃气追踪器
```bash
python3 $SCRIPT gas
python3 $SCRIPT gas --chain polygon
```
显示以下操作的 gwei 价格及美元成本：转账、ERC-20 转账、授权、交换、NFT 发行、NFT 转让。

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

## 常见问题
- CoinGecko 免费套餐：每分钟约 10-30 次请求。如需加快钱包扫描速度，可使用 `--no-prices` 参数。
- 公共 RPC 服务可能会限制请求频率。在正式环境中，请将 EVM_RPC_URL 设置为私有端点。
- `wallet` 和 `allowance` 功能仅会检查已知的代币列表（每条链约 30 种代币）。如需查找所有代币，建议使用区块浏览器。
- `activity` 功能仅扫描最近的区块（最多 200 块）。如需查看完整交易历史，请使用 Etherscan API。
- `multichain` 功能会同时运行 8 个并行线程，这可能会触发公共 RPC 服务的速率限制。
- ENS 解析依赖于一个唯一的公共端点（ensideas.com / ens.vitalik.ca），且没有备用方案。如果该端点不可用，`ens` 功能将无法正常工作——可稍后重试或使用区块浏览器。
- 交易解码也依赖于一个唯一的公共端点（4byte.directory），且没有备用方案。数据库中不存在的地址选择器会显示为 `unknown`。
- **L2 燃费估算仅针对 L2 层的执行成本。** 在 Base、Arbitrum、Optimism 和 zkSync 等层叠网络中，实际交易成本还包括取决于调用数据大小及当前 L1 燃费价格的 L1 数据上传费用。`gas` 命令不会估算这部分 L1 成本。针对 Base 网络，可参考该网络的 L1 费用预言机（合约地址 `0x420000000000000000000000000000000000000F`）。
- 地址/交易哈希输入会经过验证，确保其以 0x 开头、长度正确且为十六进制格式，但不会强制要求遵循 EIP-55 校验和的大小写规范（RPC 端点可接受任意大小写的十六进制字符串）。

---

## 验证方式
```bash
# Should print current block, gas price, ETH price
python3 ~/.hermes/skills/blockchain/evm/scripts/evm_client.py stats

# Should resolve vitalik.eth to 0xd8dA...
python3 ~/.hermes/skills/blockchain/evm/scripts/evm_client.py ens vitalik.eth
```
