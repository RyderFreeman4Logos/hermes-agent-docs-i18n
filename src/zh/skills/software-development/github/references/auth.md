# GitHub 认证设置

该技能用于配置认证机制，使智能体能够操作 GitHub 仓库、Pull Request、问题以及 CI 工作流。它提供两种认证方式：

- **`git`（始终可用）** — 使用 HTTPS 个人访问令牌或 SSH 密钥进行认证
- **`gh` CLI（如已安装）** — 通过更简化的认证流程实现更全面的 GitHub API 访问权限

## 检测流程

当用户要求你操作 GitHub 相关功能时，首先执行此检查：

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"

# Check if already authenticated
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**决策树：**
1. 如果 `gh auth status` 显示已认证 → 恭喜，可直接使用 `gh` 执行所有操作
2. 如果已安装 `gh` 但未认证 → 请使用下方的 “gh auth” 方法进行认证
3. 如果未安装 `gh` → 请使用下方的 “仅 Git” 方法（无需使用 sudo）

---

## 方法 1：仅通过 Git 进行认证（无需 gh，无需 sudo）

只要安装了 `git` 的任何机器均可使用此方法，无需root权限。

### 方案 A：使用个人访问令牌的 HTTPS 认证（推荐）

这是最通用的方法——可在任何地方使用，且无需配置 SSH。

**步骤 1：创建个人访问令牌**

请用户访问：**https://github.com/settings/tokens**

- 点击 “Generate new token (classic)”
- 给其起一个名称，例如 “hermes-agent”
- 选择所需权限范围：
  - `repo`（完整的仓库访问权限——读取、写入、推送代码及提交 Pull Request）
  - `workflow`（触发和管理 GitHub Actions 工作流）
  - `read:org`（如需操作组织内的仓库）
- 设置令牌有效期（默认 90 天较为合适）
- 复制该令牌——此后再也不会显示

**步骤 2：配置 git 以存储该令牌**

```bash
# Set up the credential helper to cache credentials
# "store" saves to ~/.git-credentials in plaintext (simple, persistent)
git config --global credential.helper store

# Now do a test operation that triggers auth — git will prompt for credentials
# Username: <their-github-username>
# Password: <paste the personal access token, NOT their GitHub password>
git ls-remote https://github.com/<their-username>/<any-repo>.git
```

一旦输入过凭证，它们就会被保存下来，并在后续的所有操作中重复使用。

**备选方案：缓存辅助工具（凭证仅存在于内存中，到期后会自动清除）**

```bash
# Cache in memory for 8 hours (28800 seconds) instead of saving to disk
git config --global credential.helper 'cache --timeout=28800'
```

**备选方案：直接在远程 URL 中设置令牌（针对单个仓库）**

```bash
# Embed token in the remote URL (avoids credential prompts entirely)
git remote set-url origin https://<username>:<token>@github.com/<owner>/<repo>.git
```

**步骤 3：配置 Git 身份信息**

```bash
# Required for commits — set name and email
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

**第4步：验证**

```bash
# Test push access (this should work without any prompts now)
git ls-remote https://github.com/<their-username>/<any-repo>.git

# Verify identity
git config --global user.name
git config --global user.email
```

### 方案 B：SSH 密钥认证

适用于更倾向于使用 SSH 或已配置好密钥的用户。

**步骤 1：检查现有的 SSH 密钥**

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "No SSH keys found"
```

**步骤 2：如需，生成密钥**

```bash
# Generate an ed25519 key (modern, secure, fast)
ssh-keygen -t ed25519 -C "their-email@example.com" -f ~/.ssh/id_ed25519 -N ""

# Display the public key for them to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

请告知用户将公钥添加至以下地址：**https://github.com/settings/keys**
- 点击“新建 SSH 密钥”
- 粘贴公钥内容
- 为该密钥起一个名称，例如 “hermes-agent-<机器名称>”

**第 3 步：测试连接**

```bash
ssh -T git@github.com
# Expected: "Hi <username>! You've successfully authenticated..."
```

**第4步：配置git以使用SSH连接GitHub**

```bash
# Rewrite HTTPS GitHub URLs to SSH automatically
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**第5步：配置Git身份信息**

```bash
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

## 方法 2：gh CLI 认证

如果已安装 `gh`，它能够一步完成 API 访问及 git 凭据的处理。

### 交互式浏览器登录（桌面端）

> **注意事项（Windows 系统下的代理驱动会话）：** 当通过 pty 后台进程执行 `gh auth login` 时，应使用 `process(submit)` 来响应提示，而绝不能仅使用带单独 `\n` 的 `process(write)`。在 Windows 的 PTY（ConPTY/pywinpty）环境中，按回车键实际上相当于发送 carriage return 符号；单独的 `\n` 并不会被当作行终止符，因此 gh 发出的“按回车键打开浏览器”提示（属于阻塞式行读取操作）将永远无法得到响应，从而导致登录过程卡住。另外还需注意，在后台会话中可能无法在用户的桌面端打开浏览器——如果遇到此类情况，请改用下方的设备端登录流程。

```bash
gh auth login
# Select: GitHub.com
# Select: HTTPS
# Authenticate via browser
```

### 手动 OAuth 设备登录流程（无需 TTY —— 经验证有效）

在交互式登录不可行时使用的备用方案（由智能体驱动会话，无需启动浏览器，支持无头模式）。该流程使用 GitHub 的公共 OAuth 客户端 ID，用户只需在 github.com/login/device 页面输入验证码即可。授权范围方面：根据文档规定，`gh auth login --with-token` 命令的最小必要范围为 `repo,read:org,gist`；仅当需要推送工作流文件时，才需额外添加 `,workflow`。

```bash
# 1. Request a device code (gh's official client_id)
RESP=$(curl -s -X POST -H "Accept: application/json" \
  -d "client_id=178c6fc778ccc68e1d6a&scope=repo,read:org,gist" \
  https://github.com/login/device/code)
DEVICE_CODE=$(echo "$RESP" | sed 's/.*"device_code":"\([^"]*\)".*/\1/')
USER_CODE=$(echo "$RESP" | sed 's/.*"user_code":"\([^"]*\)".*/\1/')
INTERVAL=$(echo "$RESP" | sed 's/.*"interval":\([0-9]*\).*/\1/'); INTERVAL=${INTERVAL:-5}
echo "Tell the user: go to https://github.com/login/device and enter code: $USER_CODE"

# 2. Poll for the token (respect interval; +5s on slow_down; ~15 min expiry).
#    Run this loop as a background process and show the user the code first.
while true; do
  sleep "$INTERVAL"
  POLL=$(curl -s -X POST -H "Accept: application/json" \
    -d "client_id=178c6fc778ccc68e1d6a&device_code=${DEVICE_CODE}&grant_type=urn:ietf:params:oauth:grant-type:device_code" \
    https://github.com/login/oauth/access_token)
  case "$POLL" in
    *access_token*)
      # Never echo the token; pipe it straight into gh.
      # timeout guards the headless-keyring hang (see pitfall below) —
      # on exit 124, fall back to writing ~/.config/gh/hosts.yml directly.
      echo "$POLL" | sed 's/.*"access_token":"\([^"]*\)".*/\1/' | timeout 20 gh auth login --with-token \
        || { echo "WITH_TOKEN_HUNG_OR_FAILED — use the hosts.yml fallback below"; exit 1; }
      gh auth setup-git
      gh auth status
      echo "LOGIN_COMPLETE"; break ;;
    *authorization_pending*) ;;                      # keep polling
    *slow_down*) INTERVAL=$((INTERVAL + 5)) ;;       # back off per GitHub docs
    *expired_token*) echo "CODE_EXPIRED — restart the flow"; exit 1 ;;
    *access_denied*) echo "USER_DENIED"; exit 1 ;;
    *) echo "UNEXPECTED: $POLL"; exit 1 ;;
  esac
done
```

注意：在 Windows 系统通过 winget 安装时，GitHub CLI 的安装路径为 `/c/Program Files/GitHub CLI`，需在同一终端中将其添加到 PATH 环境变量中，命令如下：`export PATH="$PATH:/c/Program Files/GitHub CLI"`。

> **常见陷阱（无界面的 Linux 环境）：使用 `gh auth login --with-token` 命令时可能会永久挂起。**
> 在没有密钥环或处于无界面环境中的系统上（如 VPS、容器，且未启动 dbus 会话），GitHub CLI 的凭据存储机制可能会无限期地等待 secret-service 密钥环的响应——即便使用了 `--insecure-storage` 参数且没有输出信息也是如此。如果该命令在约 20 秒内仍未返回（可通过 `timeout 20 …` 封装该命令来检测这种情况），则应绕过 GitHub CLI 的登录流程，直接写入凭据信息：

> ```bash
> # $TOKEN = 上述设备流中获取的访问令牌（切勿将其输出到终端）
> mkdir -p ~/.config/gh
> LOGIN=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/user \
>   | sed 's/.*"login": *"\([^"]*\)".*/\1/')
> printf 'github.com:\n    users:\n        %s:\n            oauth_token: %s\n    git_protocol: https\n    oauth_token: %s\n    user: %s\n' \
>   "$LOGIN" "$TOKEN" "$TOKEN" "$LOGIN" > ~/.config/gh/hosts.yml
> chmod 600 ~/.config/gh/hosts.yml
> gh auth status          # 直接读取 hosts.yml 文件——无需依赖密钥环即可完成验证
> gh auth setup-git       # 配置 Git 凭据辅助工具（不会导致程序挂起）
> ```
>
> `gh auth status` 和 `setup-git` 命令会直接读取该文件存储的凭据，而不会涉及密钥环，因此能够立即生效。此方法已在一次使用 `--with-token` 命令导致程序两次挂起的无界面 x86_64 VPS 环境中得到验证（GitHub CLI 版本为 2.97.0，2026 年 8 月）。

### 基于令牌的登录（无界面环境/SSH 服务器）

```bash
echo "<THEIR_TOKEN>" | gh auth login --with-token

# Set up git credentials through gh
gh auth setup-git
```

如果使用 `--with-token` 选项时在此处卡住，可参考上文提到的应急方案，使用 hosts.yml 文件作为替代。 

### 验证

```bash
gh auth status
```

## 无需使用 `gh` 即可调用 GitHub API

即使没有 `gh` 工具，您仍然可以通过结合 `curl` 命令与个人访问令牌来访问完整的 GitHub API。其他 GitHub 功能也正是通过这种方式实现备用方案。

### 为 API 调用设置令牌

```bash
# Option 1: Export as env var (preferred — keeps it out of commands)
export GITHUB_TOKEN="<token>"

# Then use in curl calls:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### 从 Git 凭证中提取令牌

如果已通过 `credential.helper store` 配置了 Git 凭证，即可从中提取令牌：

```bash
# Read from git credential store
uv run python "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/git-credential-token.py"
```

### 助手：检测认证方式

在任意 GitHub 工作流的开头使用此模式：

```bash
# Try gh first, fall back to git + curl
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
elif _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  echo "AUTH_METHOD=curl"
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(uv run python "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/git-credential-token.py")
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
  echo "Need to set up authentication first"
fi
```

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `git push` 时要求输入密码 | GitHub 已禁用密码认证。请使用个人访问令牌作为密码，或切换为 SSH 方式 |
| `remote: Permission to X denied` | 令牌可能缺少 `repo` 权限范围——请使用包含正确权限范围的令牌重新生成 |
| `fatal: Authentication failed` | 缓存的凭据可能已过期——请执行 `git credential reject` 后重新进行认证 |
| `ssh: connect to host github.com port 22: Connection refused` | 尝试通过 HTTPS 端口使用 SSH：在 `~/.ssh/config` 中添加 `Host github.com`、`Port 443` 以及 `Hostname ssh.github.com` |
| 凭据无法持久保存 | 检查 `git config --global credential.helper` 的值——该值必须为 `store` 或 `cache` |
| 拥有多个 GitHub 账户 | 在 `~/.ssh/config` 中为每个主机别名配置不同的 SSH 密钥，或为每个仓库设置独立的凭据 URL |
| 出现 `gh: command not found` 且未使用 sudo 权限 | 请使用上述仅依赖 Git 的解决方案——无需进行任何安装 |
