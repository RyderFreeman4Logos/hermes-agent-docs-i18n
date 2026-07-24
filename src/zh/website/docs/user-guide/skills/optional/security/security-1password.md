---
title: "1Password — Set up op CLI, sign in, and read or inject secrets"
sidebar_label: "1Password"
description: "Set up op CLI, sign in, and read or inject secrets"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 1Password

配置 op CLI、登录账号，以及读取或注入机密信息。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/security/1password` 进行安装 |
| 路径 | `optional-skills/security/1password` |
| 版本 | `1.0.0` |
| 开发者 | arceus77-7，由 Hermes Agent 改进 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `security`、`secrets`、`1password`、`op`、`cli` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能运行时，Agent 会将此内容视为操作指令。
:::

# 1Password CLI

当用户希望通过 1Password 而非明文环境变量或文件来管理机密信息时，可使用此技能。

## 前提条件

- 1Password 账号
- 已安装 1Password CLI（即 `op` 工具）
- 需满足以下条件之一：桌面应用集成、服务账户令牌（`OP_SERVICE_ACCOUNT_TOKEN`）或 Connect 服务器
- 为在 Hermes 终端调用期间保持会话稳定，需安装 `tmux`（仅适用于桌面应用流程）

## 使用场景

- 安装或配置 1Password CLI
- 使用 `op signin` 登录账号
- 读取类似 `op://Vault/Item/field` 格式的机密信息引用
- 使用 `op inject` 将机密信息注入配置文件或模板中
- 通过 `op run` 使用含机密信息的环境变量运行命令

## 认证方式

### 服务账户（Hermes 推荐方式）

在 `${HERMES_HOME:-~/.hermes}/.env` 文件中设置 `OP_SERVICE_ACCOUNT_TOKEN`（首次加载时技能会提示设置该值）。
无需使用桌面应用。支持 `op read`、`op inject`、`op run` 操作。

```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token-here"
op whoami  # verify — should show Type: SERVICE_ACCOUNT
```

### 桌面应用集成（交互式）

1. 在 1Password 桌面应用中开启该功能：设置 → 开发者 → 与 1Password CLI 集成
2. 确保应用处于解锁状态
3. 运行 `op signin` 命令，并确认生物识别验证请求

### 连接服务器（自托管）

```bash
export OP_CONNECT_HOST="http://localhost:8080"
export OP_CONNECT_TOKEN="your-connect-token"
```

## 设置

1. 安装 CLI：

```bash
# macOS
brew install 1password-cli

# Linux (official package/install docs)
# See references/get-started.md for distro-specific links.

# Windows (winget)
winget install AgileBits.1Password.CLI
```

2. 验证：

```bash
op --version
```

3. 从上方选择一种认证方式并对其进行配置。

## Hermes 执行模式（桌面应用流程）

Hermes 的终端命令默认为非交互式，因此在多次调用之间可能会丢失认证上下文。
若要在桌面应用集成中可靠地使用 `op` 命令，建议在专用的 tmux 会话中执行登录及密钥相关操作。

注意：当使用 `OP_SERVICE_ACCOUNT_TOKEN` 时无需此操作——该令牌会自动在多次终端调用之间保持有效。

```bash
SOCKET_DIR="${TMPDIR:-/tmp}/hermes-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/hermes-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell

# Sign in (approve in desktop app when prompted)
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "eval \"\$(op signin --account my.1password.com)\"" Enter

# Verify auth
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op whoami" Enter

# Example read
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op read 'op://Private/Npmjs/one-time password?attribute=otp'" Enter

# Capture output when needed
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200

# Cleanup
tmux -S "$SOCKET" kill-session -t "$SESSION"
```

## 常见操作

### 读取机密信息

```bash
op read "op://app-prod/db/password"
```

### 获取一次性密码

```bash
op read "op://app-prod/npm/one-time password?attribute=otp"
```

### 注入模板中

```bash
echo "db_password: {{ op://app-prod/db/password }}" | op inject
```

### 使用密钥环境变量运行命令

```bash
export DB_PASSWORD="op://app-prod/db/password"
op run -- sh -c '[ -n "$DB_PASSWORD" ] && echo "DB_PASSWORD is set" || echo "DB_PASSWORD missing"'
```

## 规则限制

- 除非用户明确要求，否则绝不可将原始敏感信息打印回给用户。
- 建议使用 `op run` / `op inject` 命令，而非将敏感信息直接写入文件中。
- 若命令因“账户未登录”而失败，请在同一 tmux 会话中再次运行 `op signin`。
- 若无法进行桌面应用集成（无界面环境/持续集成场景），则应使用服务账户令牌机制。

## 关于持续集成/无界面环境的说明

在非交互式使用场景下，应通过 `OP_SERVICE_ACCOUNT_TOKEN` 进行身份验证，避免使用需要交互操作的 `op signin` 命令。
服务账户需配合 CLI v2.18.0 及更高版本使用。

## 参考资料

- `references/get-started.md`
- `references/cli-examples.md`
- https://developer.1password.com/docs/cli/
- https://developer.1password.com/docs/service-accounts/
