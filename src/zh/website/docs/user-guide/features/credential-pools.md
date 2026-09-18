---
title: Credential Pools
description: Pool multiple API keys or OAuth tokens per provider for automatic rotation and rate limit recovery.
sidebar_label: Credential Pools
sidebar_position: 9
---

# 凭证池

凭证池允许您为同一提供商注册多个 API 密钥或 OAuth 令牌。当某个密钥达到速率限制或费用限额时，Hermes 会自动切换到下一个正常工作的密钥——这样无需更换提供商即可保持会话的连续性。

这与[备用提供商](./fallback-providers.md)有所不同，后者会完全切换到*另一个*提供商。凭证池实现的是同一提供商内的密钥轮换，而备用提供商则属于跨提供商的故障转移机制。系统会首先尝试使用凭证池中的密钥；只有当所有密钥都用尽后，才会启用备用提供商。

:::warning 密钥轮换会重置提示词缓存
提供商端的提示词缓存（如 Anthropic、OpenAI、OpenRouter）是针对发起请求的账户/API 密钥单独管理的。如果在会话进行过程中切换到不同的密钥，新密钥将没有该对话的历史提示词缓存——后续请求需要以全价重新读取全部历史记录。除非之前使用的密钥的缓存有效期尚未结束，否则再次切换回来时也需重新完整读取。虽然密钥轮换能保证会话持续运行，但在长时间对话中，每次轮换都会导致上下文需要按全价重新处理。
:::

:::tip
凭证池主要适用于提供 API 密钥的提供商（如 OpenRouter、Anthropic）。单个[Nous Portal](/integrations/nous-portal)的 OAuth 访问权限已覆盖 300 多种模型，因此大多数用户在通过 Portal 使用服务时无需使用凭证池。
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
      → Immediately rotate to next pool key (1h cooldown)
  → 401 auth expired?
      → Try refreshing the token (OAuth)
      → Refresh failed → rotate to next pool key
  → Success → continue normally
```

## 快速入门

如果您已在 `.env` 文件中设置了 API 密钥，Hermes 会自动将其识别为一个包含单个密钥的池。若要充分利用密钥池功能，请添加更多密钥：

```bash
# Add a second OpenRouter key
hermes auth add openrouter --api-key sk-or-v1-your-second-key

# Add a second Anthropic key
hermes auth add anthropic --type api-key --api-key sk-ant-api03-your-second-key

# Add an Anthropic OAuth credential (requires Claude Max plan + extra usage credits)
hermes auth add anthropic --type oauth
# Opens browser for OAuth login
```

检查您的资源池：

```bash
hermes auth list
```

输出：
```
openrouter (2 credentials):
  #1  OPENROUTER_API_KEY   api_key id=ab12cd34 priority=0 env:OPENROUTER_API_KEY ←
  #2  backup-key           api_key id=ef56gh78 priority=1 manual

anthropic (3 credentials):
  #1  hermes_pkce          oauth   id=ab12cd34 priority=0 hermes_pkce ←
  #2  claude_code          oauth   id=cd34ef56 priority=1 claude_code
  #3  ANTHROPIC_API_KEY    api_key id=ef56gh78 priority=2 env:ANTHROPIC_API_KEY
```

`←` 符号用于标记当前选中的凭据。当标签存在歧义时，`hermes auth remove <provider> <target>` 命令会使用 `id=` 作为输入标识；而在 `fill_first` 策略下，`priority=` 则决定了凭证池尝试凭据的顺序。

## 交互式管理

直接运行不带子命令的 `hermes auth` 即可进入交互式向导界面：

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
| `hermes auth add <provider>` | 添加凭证（系统会提示凭证类型和密钥） |
| `hermes auth add <provider> --type api-key --api-key <key>` | 非交互式方式添加 API 密钥 |
| `hermes auth add <provider> --type oauth` | 通过浏览器登录添加 OAuth 凭证 |
| `hermes auth add <provider> --priority 0` | 添加凭证并将其置于 `fill_first` 顺序中的首位 |
| `hermes auth priority <provider> <target> <n>` | 将某凭证的优先级设置为 `n`（0 表示优先尝试）；其余凭证的顺序将相应重新编号 |
| `hermes auth remove <provider> <index>` | 根据基于 1 的索引删除凭证 |
| `hermes auth reset <provider>` | 清除所有冷却时间/使用限制状态 |
| `hermes auth reset <provider> <target>` | 根据索引、ID 或标签清除指定凭证的冷却时间 |
| `hermes auth refresh <provider> [target]` | 刷新某个 OAuth 凭证的令牌，并使其重新进入轮换使用状态（用于确认授权有效；后续请求将再次检查配额） |
对于 Nous，`auth refresh` 功能仅支持登录时使用的 `device_code` 单例值。在刷新之前，独立的 Nous 池账户会被拒绝处理，但其令牌和冷却时间仍会保留。如需更新该单例值，需使用 `hermes auth add nous --type oauth` 命令重新进行身份验证，此操作不会刷新独立账户。其他提供商则保留其原有的特定来源刷新支持功能。

## 旋转策略

优先级位置从零开始计数，并会被限制在池的边界范围内；显示的目标则为从一开始的索引、条目 ID 或唯一明确的标签。使用 `auth add --priority` 命令时，通过重新身份验证更新的现有条目也会被赋予优先级。Anthropic 会将手动输入的凭证置于系统预设凭证之前，因此当规则发生变化时，命令会显示相应的有效位置。其他策略可能会覆盖优先级设置，且重新排序不会改变正在运行的会话所持有的凭证。

无论采用何种策略，每次成功选择池都会使 `request_count` 值加一，仅执行刷新操作或查看操作的请求则不计入统计。这些计数器用于记录选择次数，而非计费总额或所有推理请求的数量——因为一个缓存的凭证可以服务于多次请求。这些计数值会保留在内存中，直到下一次对池进行写入操作（如旋转、用尽、刷新或管理变更）为止；每次选择操作都不会产生额外的磁盘写入。

可通过 `hermes auth` → “设置旋转策略”或直接在 `config.yaml` 文件中进行配置：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```

| 策略 | 行为 |
|------|------|
| `fill_first`（默认值） | 先使用第一个正常的密钥，直到其被用尽后再切换到下一个；顺序依据每个凭证的 `priority` 值决定（可通过 `hermes auth priority` 进行调整） |
| `round_robin` | 以均匀的方式循环使用各密钥，每次选择后都会进行切换 |
| `least_used` | 始终选择请求次数最少的密钥 |
| `random` | 在所有正常的密钥中随机选择 |

## 错误恢复

该密钥池会对不同类型的错误采取不同的处理方式：

| 错误类型 | 行为 | 冷却时间 |
|----------|------|----------|
| **429 速率限制** | 仅重试当前密钥一次（属于临时性错误）。若连续两次出现 429 错误，则切换到下一个密钥 | 1 小时 |
| **402 费用/配额不足** | 立即切换到下一个密钥 | 1 小时 |
| **401 认证过期** | 首先尝试刷新 OAuth 令牌；仅在刷新失败时才切换密钥 | 5 分钟 |
| **所有密钥均已用尽** | 若已配置 `fallback_model`，则自动切换到该备用模式 | — |

由服务提供商提供的 `reset_at` 时间戳可覆盖这些默认的冷却时间设置。

`has_retried_429` 标志会在每次成功的 API 调用后重置，因此单次临时性的 429 错误不会触发密钥切换。

## 自定义端点池

兼容 OpenAI 的自定义端点（如 Together.ai、RunPod、本地服务器）会拥有独立的端点池，其标识依据 `config.yaml` 文件中 `providers:` 字典中的端点名称确定（旧版配置则使用 `custom_providers` 列表，该列表已自动迁移）。

通过 `hermes model` 设置自定义端点时，系统会自动生成类似 “Together.ai” 或 “Local (localhost:8080)” 这样的名称，该名称即作为端点池的标识。

```bash
# After setting up a custom endpoint via hermes model:
hermes auth list
# Shows:
#   Together.ai (1 credential):
#     #1  config key    api_key config:Together.ai ←

# Add a second key for the same endpoint:
hermes auth add Together.ai --api-key sk-together-second-key
```

自定义端点池会以 `custom:` 为前缀，存储在 `auth.json` 文件的 `credential_pool` 子目录中。

```json
{
  "credential_pool": {
    "openrouter": [...],
    "custom:together.ai": [...]
  }
}
```

## 自动发现

Hermes 会在启动时自动从多个来源获取凭证，并将其加入凭证池中：

| 来源 | 示例 | 是否自动添加？ |
|------|------|--------------|
| 环境变量 | `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` | 是 |
| OAuth 令牌（auth.json） | Codex 设备代码、Nous 设备代码 | 是 |
| Claude Code 凭证 | `~/.claude/.credentials.json` | 是（Anthropic 平台） |
| Hermes PKCE OAuth | `~/.hermes/auth.json` | 是（Anthropic 平台） |
| 自定义端点配置 | config.yaml 中的 `model.api_key` | 是（自定义端点） |
| 手动添加项 | 通过 `hermes auth add` 添加 | 会保存在 auth.json 中 |

自动添加的凭证项会在每次加载凭证池时更新——如果移除了某个环境变量，其对应的凭证项也会被自动删除。而通过 `hermes auth add` 手动添加的凭证项则不会被自动删除。

那些被借用的运行时密钥（如环境变量、Bitwarden/Vault/keyring/systemd 中的引用值以及自定义配置值）在 `auth.json` 文件中仅作为引用存在。Hermes 可以在当前运行过程中使用已解析出的实际值，但只会保存来源引用、标签、状态、请求计数器以及一个不可逆的指纹等元数据。手动添加的凭证项以及由 Hermes 管理的 OAuth/设备代码状态，则会保留用于刷新凭证的持久性令牌。

## 委派与子代理共享

当代理通过 `delegate_task` 功能创建子代理时，父代理的凭证池会自动与子代理共享：

- **同一提供方**——子代理可获取父代理的完整凭证池，从而实现速率限制下的密钥轮换。  
- **不同提供方**——子代理会加载该提供方自身的凭证池（如已配置）。  
- **未配置凭证池**——子代理将回退至继承的单个 API 密钥。  

这意味着子代理无需额外配置即可享有与父代理相同的速率限制抵御能力。通过按任务租用凭证机制，可确保在同时进行密钥轮换时各子代理之间不会发生冲突。  

## 线程安全  

凭证池对所有状态修改操作（如 `select()`、`mark_exhausted_and_rotate()`、`try_refresh_current()`、`mark_used()`）均使用线程锁进行保护。这保证了网关在同时处理多个聊天会话时仍能实现安全的并发访问。  

在跨进程场景下（如多个子代理、网关与 CLI 共存、定时任务等），OAuth 凭证刷新操作会通过 `auth.json` 文件锁实现串行化处理。当多个并发进程中的某个共享 OAuth 授权失效时，仅有一个进程会执行刷新操作；其余进程会检测到磁盘上的令牌与已失效的令牌不一致，便直接使用该有效令牌，而不会再次轮换一次性使用的刷新令牌。若某个进程在锁竞争中落败，它仍会保持自身状态并尝试重试——锁竞争情况不会被记为凭证失效。  

## 架构  

完整的 数据流图请参见仓库中的 [`docs/credential-pool-flow.excalidraw`](https://excalidraw.com/#json=2Ycqhqpi6f12E_3ITyiwh,c7u9jSt5BwrmiVzHGbm87g) 文件。

凭证池在提供者解析层实现集成：

1. **`agent/credential_pool.py`** — 凭证池管理器：负责凭证的存储、选择、轮换以及冷却机制；**`agent/credential_pool_admin.py`** 则负责锁定目标解析、重置、添加、移除以及优先级调整等功能。
2. **`hermes_cli/auth_commands.py`** — 提供命令行界面及交互式向导功能。
3. **`hermes_cli/runtime_provider.py`** — 支持基于凭证池的凭证解析机制。
4. **`agent/turn_api_error.py`** — 错误处理机制：当遇到 429/402/401 等错误时，会自动触发凭证池轮换，并采用备用方案。

## 存储方式

凭证池的状态存储在 `~/.hermes/auth.json` 文件中的 `credential_pool` 键下。

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

上述 OpenRouter 条目是从外部来源获取的，因此其原始密钥并未存储在 `auth.json` 中。而手动添加的 Anthropic 条目则是特意存入 Hermes 的凭证存储库中的，这样其令牌就能保持持久有效。

策略信息存储在 `config.yaml` 文件中（而非 `auth.json`）：

```yaml
credential_pool_strategies:
  openrouter: round_robin
  anthropic: least_used
```
