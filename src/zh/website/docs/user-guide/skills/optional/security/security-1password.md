---
title: "1Password — Set up and use 1Password CLI (op)"
sidebar_label: "1Password"
description: "Set up and use 1Password CLI (op)"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据该技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 1Password

用于设置和使用 1Password CLI（op）。适用于安装 CLI、启用桌面应用集成、登录，以及为命令读取/注入机密信息。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/security/1password` 进行安装 |
| 路径 | `optional-skills/security/1password` |
| 版本 | `1.0.0` |
| 创建者 | arceus77-7，由 Hermes Agent 改进 |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `security`、`secrets`、`1password`、`op`、`cli` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，Agent 就会依据此内容执行操作。
:::

# 1Password CLI

当用户希望通过 1Password 而非明文环境变量或文件来管理机密信息时，可使用此技能。

## 前提条件

- 1Password 账户
- 已安装 1Password CLI（op）
- 其中一种方式：桌面应用集成、服务账户令牌（`OP_SERVICE_ACCOUNT_TOKEN`）或 Connect 服务器
- 为在 Hermes 终端调用期间保持稳定的认证会话，需安装 `tmux`（仅适用于桌面应用流程）

## 使用场景

- 安装或配置 1Password CLI
- 使用 `op signin` 登录
- 读取类似 `op://Vault/Item/field` 的机密信息引用
- 使用 `op inject` 将机密信息注入配置文件/模板中
- 通过 `op run` 使用含机密信息的环境变量运行命令

## 认证方式

### 服务账户（Hermes 推荐）

在 `${HERMES_HOME:-~/.hermes}/.env` 文件中设置 `OP_SERVICE_ACCOUNT_TOKEN`（首次加载时技能会提示输入该值）。
无需桌面应用。支持 `op read`、`op inject`、`op run` 功能。

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
若要在桌面应用集成中可靠地使用 `op` 命令，请在专用的 tmux 会话中执行登录和密钥相关操作。

注意：当使用 `OP_SERVICE_ACCOUNT_TOKEN` 时则无需此操作——该令牌会自动在多次终端调用之间保持有效。

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

### 读取密钥

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

### 使用带密钥的环境变量运行命令

```bash
export DB_PASSWORD="op://app-prod/db/password"
op run -- sh -c '[ -n "$DB_PASSWORD" ] && echo "DB_PASSWORD is set" || echo "DB_PASSWORD missing"'
```

## 使用规范

- 除非用户明确要求，否则绝不要将原始密钥信息回显给用户。
- 建议使用 `op run` / `op inject` 命令，而非将密钥直接写入文件中。
- 若命令因“账户未登录”而失败，请在同一个 tmux 会话中再次执行 `op signin`。
- 若无法进行桌面应用集成（无界面环境/持续集成场景），则应采用服务账户令牌机制。

## 关于持续集成/无界面环境的说明

在非交互式使用场景下，应通过 `OP_SERVICE_ACCOUNT_TOKEN` 进行身份验证，避免使用需要交互操作的 `op signin` 命令。
服务账户功能要求 CLI 版本至少为 2.18.0。

## 参考资料

- `references/get-started.md`
- `references/cli-examples.md`
- https://developer.1password.com/docs/cli/
- https://developer.1password.com/docs/service-accounts/
