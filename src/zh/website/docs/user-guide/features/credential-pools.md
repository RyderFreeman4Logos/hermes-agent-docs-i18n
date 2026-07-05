---
title: Credential Pools
description: Pool multiple API keys or OAuth tokens per provider for automatic rotation and rate limit recovery.
sidebar_label: Credential Pools
sidebar_position: 9
---

# 凭证池

凭证池允许您为同一提供商注册多个 API 密钥或 OAuth 令牌。当某个密钥达到速率限制或计费配额时，Hermes 会自动切换到下一个正常的密钥——从而在无需更换提供商的情况下保持会话的持续运行。

这与[备用提供商](./fallback-providers.md)有所不同，后者会完全切换到*另一个*提供商。凭证池实现的是同一提供商内的密钥轮换，而备用提供商则属于跨提供商的故障转移机制。系统会首先尝试使用凭证池中的密钥；只有当所有密钥都用尽后，才会启用备用提供商。

:::warning 密钥轮换会重置提示词缓存
提供商端的提示词缓存（如 Anthropic、OpenAI、OpenRouter）是针对发起请求的账户/API 密钥进行限定的。如果在会话进行过程中凭证池切换到另一个密钥，新密钥将没有该对话的历史提示词缓存——后续请求需要以全价重新读取全部历史记录。即便之后再切换回原来的密钥，除非该密钥的缓存有效期尚未结束，否则同样需要再次完整读取历史记录。虽然密钥轮换能确保会话持续运行，但在长时间对话中，每次轮换都会导致上下文需要按全价被重新处理一次。
:::

:::tip
凭证池主要适用于提供 API 密钥的提供商（如 OpenRouter、Anthropic）。单个[Nous Portal](/integrations/nous-portal) 的 OAuth 访问权限即可支持 300 多种模型，因此大多数用户在通过 Portal 使用服务时并不需要使用凭证池。
:::

## 工作原理

```
Your request
  → Pick key from pool (round_robin / least_used / fill_first / random)
  → Send to provider
  → 429 rate limit?
      → Plan/usage limit reached (e.g. ChatGPT/Codex "usage limit reached")?
          → Rotate to next pool key immediately (no retry — the cap won't clear on retry)
      → Generic / transient 429?
          → Retry same key once (transient blip)
          → Second 429 → rotate to next pool key
      → All keys exhausted → fallback_model (different provider)
  → 402 billing error?
      → Immediately rotate to next pool key (24h cooldown)
  → 401 auth expired?
      → Try refreshing the token (OAuth)
      → Refresh failed → rotate to next pool key
  → Success → continue normally
```

## 快速入门

如果您已在 `.env` 文件中配置了 API 密钥，Hermes 会自动将其识别为一个包含 1 个密钥的池。如需利用密钥池功能，请添加更多密钥：

```bash
# Add a second OpenRouter key
hermes auth add openrouter --api-key sk-or-v1-your-second-key

# Add a second Anthropic key
hermes auth add anthropic --type api-key --api-key sk-ant-api03-your-second-key

# Add an Anthropic OAuth credential (requires Claude Max plan + extra usage credits)
hermes auth add anthropic --type oauth
# Opens browser for OAuth login
```

检查您的池：

```bash
hermes auth list
```

输出：
```
openrouter (2 credentials):
  #1  OPENROUTER_API_KEY   api_key env:OPENROUTER_API_KEY ←
  #2  backup-key           api_key manual

anthropic (3 credentials):
  #1  hermes_pkce          oauth   hermes_pkce ←
  #2  claude_code          oauth   claude_code
  #3  ANTHROPIC_API_KEY    api_key env:ANTHROPIC_API_KEY
```

`←` 符号用于标识当前已选中的凭据。

## 交互式管理

运行不带子命令的 `hermes auth` 即可启动交互式向导：

```bash
hermes auth
```

此处会显示您的完整资源池状态，并提供一个菜单：

```
What would you like to do?
  1. Add a credential
  2. Remove a credential
  3. Reset cooldowns for a provider
  4. Set rotation strategy for a provider
  5. Exit
```

对于同时支持 API 密钥和 OAuth 的服务提供商（如 Anthropic、Nous、Codex），添加流程会询问应使用哪种认证方式。

```
anthropic supports both API keys and OAuth login.
  1. API key (paste a key from the provider dashboard)
  2. OAuth login (authenticate via browser)
Type [1/2]:
```

## CLI 命令

| 命令 | 描述 |
|---------|-------------|
| `hermes auth` | 交互式池管理向导 |
| `hermes auth list` | 显示所有池及凭证信息 |
| `hermes auth list <provider>` | 显示指定提供商的池信息 |
| `hermes auth add <provider>` | 添加凭证（会提示输入凭证类型和密钥） |
| `hermes auth add <provider> --type api-key --api-key <key>` | 以非交互方式添加 API 密钥 |
| `hermes auth add <provider> --type oauth` | 通过浏览器登录添加 OAuth 凭证 |
| `hermes auth remove <provider> <index>` | 根据基于 1 的索引删除凭证 |
| `hermes auth reset <provider>` | 清除所有冷却时间/使用限制状态 |

## 密钥轮换策略

可通过 `hermes auth` → “设置轮换策略”或直接在 `config.yaml` 中进行配置：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```

| 策略 | 行为 |
|------|------|
| `fill_first`（默认值） | 先使用第一个正常可用的密钥，直至其被用完后再切换到下一个 |
| `round_robin` | 均匀轮询各密钥，每次选择后进行切换 |
| `least_used` | 始终选择请求次数最少的密钥 |
| `random` | 在所有正常可用的密钥中随机选择 |

## 错误恢复机制

该密钥池会对不同类型的错误采取不同的处理方式：

| 错误类型 | 处理方式 | 冷却时间 |
|----------|----------|----------|
| **429 速率限制** | 仅重试当前密钥一次（属于临时性错误）。若连续两次出现 429 错误，则切换到下一个密钥 | 1 小时 |
| **402 费用/配额限制** | 立即切换到下一个密钥 | 24 小时 |
| **401 认证过期** | 首先尝试刷新 OAuth 令牌；仅当刷新失败时才切换密钥 | — |
| **所有密钥均已用尽** | 若已配置 `fallback_model`，则自动切换到该备用模型 | — |

`has_retried_429` 标志会在每次成功的 API 调用后重置，因此单次临时性的 429 错误不会触发密钥切换。

## 自定义端点池

兼容 OpenAI 的自定义端点（如 Together.ai、RunPod、本地服务器）会拥有独立的密钥池，其标识依据为 `config.yaml` 中 `custom_providers` 配置项所指定的端点名称。

通过 `hermes model` 设置自定义端点时，系统会自动生成类似 “Together.ai” 或 “Local (localhost:8080)” 这样的名称，该名称即作为该端点池的密钥。

```bash
# After setting up a custom endpoint via hermes model:
hermes auth list
# Shows:
#   Together.ai (1 credential):
#     #1  config key    api_key config:Together.ai ←

# Add a second key for the same endpoint:
hermes auth add Together.ai --api-key sk-together-second-key
```

自定义端点池会以 `custom:` 为前缀，存储在 `auth.json` 文件的 `credential_pool` 下。

```json
{
  "credential_pool": {
    "openrouter": [...],
    "custom:together.ai": [...]
  }
}
```

## 自动发现

Hermes 会在启动时自动从多个来源获取凭证，并将其初始化到凭证池中：

| 来源 | 示例 | 是否自动添加？ |
|------|------|--------------|
| 环境变量 | `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` | 是 |
| OAuth 令牌（auth.json） | Codex 设备代码、Nous 设备代码 | 是 |
| Claude Code 凭证 | `~/.claude/.credentials.json` | 是（Anthropic 平台） |
| Hermes PKCE OAuth | `~/.hermes/auth.json` | 是（Anthropic 平台） |
| 自定义端点配置 | config.yaml 中的 `model.api_key` | 是（自定义端点） |
| 手动添加项 | 通过 `hermes auth add` 添加 | 保存在 auth.json 中 |

自动添加的凭证项会在每次加载凭证池时更新——如果移除了某个环境变量，其对应的凭证项也会被自动删除。而通过 `hermes auth add` 手动添加的凭证项则不会被自动删除。

从外部获取的运行时密钥（如环境变量、Bitwarden/Vault/keyring/systemd 中的引用值以及自定义配置值）在 `auth.json` 文件中仅以引用形式存在。Hermes 可以在当前运行过程中使用解析后的实际值，但仅会保存来源引用、标签、状态、请求计数器以及不可逆的指纹等元数据。手动添加的凭证项以及 Hermes 管理的 OAuth/设备代码状态则会保留用于刷新凭证的持久性令牌。

## 委派与子代理共享

当代理通过 `delegate_task` 创建子代理时，父代理的凭证池会自动与子代理共享：

- **同一提供商**——子代理可获取父代理的全部凭证池，从而实现速率限制时的密钥轮换
- **不同提供商**——子代理会加载该提供商自身的凭证池（如果已配置）
- **未配置凭证池**——子代理将回退到继承的单一 API 密钥

这意味着子代理无需额外配置即可享有与父代理相同的抗速率限制能力。此外，每项任务独立的凭证租赁机制可确保在同时进行密钥轮换时，各子代理之间不会发生冲突。

## 线程安全

凭证池对所有状态修改操作（如 `select()`, `mark_exhausted_and_rotate()`, `try_refresh_current()`, `mark_used()`）都使用线程锁进行保护。这保证了在网关同时处理多个聊天会话时，仍能实现安全的并发访问。

## 架构

完整的流程图请参见仓库中的 [`docs/credential-pool-flow.excalidraw`](https://excalidraw.com/#json=2Ycqhqpi6f12E_3ITyiwh,c7u9jSt5BwrmiVzHGbm87g) 文件。

凭证池在提供商解析层进行集成，具体包括：

1. **`agent/credential_pool.py`**——凭证池管理器：负责存储、选择、轮换凭证及设置冷却时间
2. **`hermes_cli/auth_commands.py`**——CLI 命令及交互式向导
3. **`hermes_cli/runtime_provider.py`**——支持凭证池感知的凭证解析功能
4. **`run_agent.py`**——错误处理机制：针对 429/402/401 错误自动触发凭证池轮换并启用备用方案

## 存储

凭证池的状态存储在 `~/.hermes/auth.json` 文件的 `credential_pool` 键下：

```json
{
  "version": 1,
  "credential_pool": {
    "openrouter": [
      {
        "id": "abc123",
        "label": "OPENROUTER_API_KEY",
        "auth_type": "api_key",
        "priority": 0,
        "source": "env:OPENROUTER_API_KEY",
        "secret_source": "bitwarden",
        "secret_fingerprint": "sha256:12ab34cd56ef7890",
        "last_status": "ok",
        "request_count": 142
      }
    ],
    "anthropic": [
      {
        "id": "manual1",
        "label": "personal-api-key",
        "auth_type": "api_key",
        "priority": 0,
        "source": "manual",
        "access_token": "sk-ant-api03-..."
      }
    ]
  }
}
```

上述 OpenRouter 条目是从外部来源引入的，因此其原始密钥并未存储在 `auth.json` 中。而手动添加的 Anthropic 条目则是有意存储在 Hermes 的凭证存储库中的，这样其令牌才能保持持久性。

策略信息存储在 `config.yaml` 文件中（而非 `auth.json`）：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```
