---
sidebar_position: 3
title: "Nix & NixOS Setup"
description: "Install and deploy Hermes Agent with Nix — from quick `nix run` to fully declarative NixOS module with container mode"
---

# Nix 与 NixOS 配置

:::warning 第二级平台
Nix 和 NixOS 属于[第二级平台](./platform-support.md#tier-2)。此处文档中的 flake 与 NixOS 模块仅以尽力维护的方式提供。对 `main` 分支的任何修改都可能随时导致这些包出现故障。

如需获得官方支持的配置方式，请使用标准的[安装](./installation.md)路径——即 Docker 环境或 FHS 环境。
:::

Hermes Agent 提供了 Nix flake 与 NixOS 模块。

| 级别 | 目标用户 | 提供功能 |
|-------|---------|----------|
| **`nix run` / `nix profile install`** | 所有 Nix 用户（macOS、Linux） | 已预编译好的二进制文件，包含所有依赖项——随后即可使用常规的 CLI 工作流程 |
| **NixOS 模块（原生版）** | NixOS 服务器部署场景 | 声明式配置、加固过的 systemd 服务、受管理的机密信息 |
| **NixOS 模块（容器版）** | 需要能够自行修改的 Agent | 包含上述所有功能，此外还提供一个持久化的 Ubuntu 容器，Agent 可在此通过 `apt`/`pip`/`npm install` 安装依赖 |

:::info 与标准安装方式的区别
传统的 `curl | bash` 安装方式会自行管理 Python、Node 及其依赖项。而 Nix flake 则完全替代了这一机制——所有的 Python 依赖项都由 [uv2nix](https://github.com/pyproject-nix/uv2nix) 生成为 Nix 衍生包，运行时工具（Node.js、git、ripgrep、ffmpeg）则会被整合到二进制文件的 PATH 环境中。这种方式无需运行时的 pip，也不需要激活 venv 或执行 `npm install` 命令。

**对于非 NixOS 用户**，这一变化仅体现在安装步骤上。之后的操作（如 `hermes setup`、`hermes gateway install`、配置编辑等）与标准安装方式完全一致。

**对于使用 NixOS 模块的用户**，整个使用流程会有所不同：配置信息存储在 `configuration.nix` 文件中，机密信息会通过 sops-nix/agenix 进行管理，服务以 systemd 单元的形式存在，同时 CLI 配置命令也被禁用。你可以像管理其他 NixOS 服务一样来管理 Hermes Agent。
:::

## 先决条件

- **已启用 flakes 功能的 Nix**——推荐使用 [Determinate Nix](https://install.determinate.systems)（默认即可启用 flakes 功能）
- 所需服务的**API 密钥**（至少需要 OpenRouter 或 Anthropic 的密钥）

---

## 快速入门（适用于所有 Nix 用户）

无需克隆代码。Nix 会自动完成所有内容的获取、构建与运行：

```bash
# Run the desktop app
nix run github:NousResearch/hermes-agent#desktop

# Or install persistently
nix profile install github:NousResearch/hermes-agent#desktop

# run the tui
nix run github:NousResearch/hermes-agent -- setup
nix run github:NousResearch/hermes-agent -- --tui

# or install it in your profile
nix profile install github:NousResearch/hermes-agent
hermes setup
hermes --tui
```

执行 `nix profile install` 后，`hermes`、`hermes-agent` 以及 `hermes-acp` 将会被添加到您的 PATH 环境变量中。此后的操作流程与[标准安装方式](./installation.md)完全一致——`hermes setup` 会引导您完成提供程序的选择，`hermes gateway install` 会配置相应的启动服务（macOS 系统使用 launchd，其他系统使用 systemd 用户服务），而所有配置文件则存储在 `~/.hermes/` 目录下。

:::warning 消息传递平台（Discord、Telegram、Slack）
默认安装包中已包含 `hermes-agent` 所需的所有库。如果您希望使用更轻量的版本，可以查看其他 flake 输出选项。

`default` 安装包会使程序包大小增加约 700 MB。而如果您仅需要支持消息传递平台，选择 `#messaging` 选项则仅需额外增加约 33 MB 的体积。

:::

<details>
<summary><strong>从本地克隆的仓库运行</strong></summary>
</details>

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
nix develop
hermes setup
```

</details>

---

## NixOS 模块

该 Flake 会导出 `nixosModules.default` —— 一个功能完备的 NixOS 服务模块，能够以声明式方式管理用户创建、目录配置、配置文件生成、机密信息处理、文档管理以及服务生命周期。

:::note
该模块需要 NixOS 环境。对于非 NixOS 系统（如 macOS、其他 Linux 发行版），请使用 `nix profile install` 及上述标准 CLI 工作流程。
:::

### 添加 Flake 输入项

```nix
# /etc/nixos/flake.nix (or your system flake)
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    hermes-agent.url = "github:NousResearch/hermes-agent";
  };

  outputs = { nixpkgs, hermes-agent, ... }: {
    nixosConfigurations.your-host = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        hermes-agent.nixosModules.default
        ./configuration.nix
      ];
    };
  };
}
```

### 最小化配置

```nix
# configuration.nix
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    settings.model.default = "anthropic/claude-sonnet-4";
    environmentFiles = [ config.sops.secrets."hermes-env".path ];
    addToSystemPackages = true;
  };
}
```

就这样。`nixos-rebuild switch` 会创建 `hermes` 用户，生成 `config.yaml` 文件，配置保密信息，并启动网关——这是一个长期运行的服务，用于将代理与消息平台（如 Telegram、Discord 等）相连并监听传入的消息。

:::warning 需要保密信息
上述的 `environmentFiles` 行假设你已经配置了 [sops-nix](https://github.com/Mic92/sops-nix) 或 [agenix](https://github.com/ryantm/agenix)。该文件至少应包含一个 LLM 提供商密钥（例如 `OPENROUTER_API_KEY=sk-or-...`）。有关完整配置信息，请参阅[保密信息管理](#secrets-management)。如果你还没有保密信息管理工具，可以先使用普通文本文件作为起点——只需确保该文件不具备世界可读权限即可：

```bash
echo "OPENROUTER_API_KEY=sk-or-your-key" | sudo install -m 0600 -o hermes /dev/stdin /var/lib/hermes/env
```

```nix
services.hermes-agent.environmentFiles = [ "/var/lib/hermes/env" ];
```
:::

:::tip addToSystemPackages
将 `addToSystemPackages` 设置为 `true` 可实现两重作用：一是将 `hermes` CLI 添加到系统的 PATH 环境变量中，二是全局设置 `HERMES_HOME`，从而使交互式 CLI 能与网关服务共享状态（会话、技能、定时任务等）。如果不这样做，在终端中运行 `hermes` 时会创建一个独立的 `~/.hermes/` 目录。

:::

### 容器感知型 CLI

:::info
当 `container.enable` 设为 `true` 且 `addToSystemPackages` 也为 `true` 时，主机上的**所有** `hermes` 命令都会自动被路由到受管理的容器中。这意味着交互式 CLI 会话将在与网关服务相同的环境中运行，并能够使用容器内安装的所有软件包和工具。

- 路由过程是完全透明的：`hermes chat`、`hermes sessions list`、`hermes version` 等命令实际上都是在容器内部执行的
- 所有的 CLI 参数都会原样传递
- 如果容器未运行，CLI 会短暂重试（交互模式下为5秒并显示加载指示器，脚本模式下为10秒且无提示），之后会给出明确的错误信息——不会自动切换到其他模式
- 对于正在开发 hermes 代码库的开发者，可设置 `HERMES_DEV=1` 来绕过容器路由，直接运行本地版本

可通过设置 `container.hostUsers` 来创建一个指向服务状态目录的 `~/.hermes` 符号链接，从而使主机 CLI 与容器之间能够共享会话、配置和缓存信息：

```nix
services.hermes-agent = {
  container.enable = true;
  container.hostUsers = [ "your-username" ];
  addToSystemPackages = true;
};
```

位于 `hostUsers` 列表中的用户会自动被添加到 `hermes` 组中，从而获得文件权限访问权。

**Podman 用户：** NixOS 服务会以根用户身份运行容器。Docker 用户可通过 `docker` 组的套接字获得访问权限，但 Podman 的根用户模式容器则需要使用 sudo 权限。请为你的容器运行时配置无密码 sudo 权限：

```nix
security.sudo.extraRules = [{
  users = [ "your-username" ];
  commands = [{
    command = "/run/current-system/sw/bin/podman";
    options = [ "NOPASSWD" ];
  }];
}];
```

CLI 会自动检测是否需要使用 sudo，并在后台透明地调用它。若没有此功能，您就需要手动执行 `sudo hermes chat` 命令。
:::

### 验证功能正常

执行 `nixos-rebuild switch` 后，请检查该服务是否正在运行：

```bash
# Check service status
systemctl status hermes-agent

# Watch logs (Ctrl+C to stop)
journalctl -u hermes-agent -f

# If addToSystemPackages is true, test the CLI
hermes version
hermes config       # shows the generated config
```

### 选择部署模式

该模块支持两种模式，由 `container.enable` 参数控制：

| | **原生模式**（默认） | **容器模式** |
|---|---|---|
| 运行方式 | 在主机上运行经过强化的 systemd 服务 | 使用持久化的 Ubuntu 容器，并将 `/nix/store` 直接挂载进来 |
| 安全性 | 启用 `NoNewPrivileges`、`ProtectSystem=strict` 和 `PrivateTmp` 设置 | 通过容器隔离机制保障安全，以无特权用户身份运行 |
| Agent 是否能自行安装软件包 | 不支持——仅可使用 Nix 指定的 PATH 路径下的工具 | 支持——`apt`、`pip`、`npm` 等工具的安装状态可在重启后保持不变 |
| 配置接口 | 与原生模式相同 | 与原生模式相同 |
| 适用场景 | 标准部署场景，需要最高级别的安全性及可重复性 | Agent 需要在运行时安装软件包、拥有可变环境或使用实验性工具时 |

如需启用容器模式，只需添加一行配置即可：

```nix
{
  services.hermes-agent = {
    enable = true;
    container.enable = true;
    # ... rest of config is identical
  };
}
```

:::info
容器模式会通过 `mkDefault` 自动启用 `virtualisation.docker.enable`。如果您使用的是 Podman，则需设置 `container.backend = "podman"` 且将 `virtualisation.docker.enable` 设为 `false`。
:::

---

## 配置

### 声明式设置

`settings` 选项可接受任意属性集，这些属性集会被转换为 `config.yaml` 格式。该功能支持通过 `lib.recursiveUpdate` 在多个模块定义之间进行深度合并，因此您可以将配置分散到多个文件中：

```nix
# base.nix
services.hermes-agent.settings = {
  model.default = "anthropic/claude-sonnet-4";
  toolsets = [ "all" ];
  terminal = { backend = "local"; timeout = 180; };
};

# personality.nix
services.hermes-agent.settings = {
  display = { compact = false; personality = "kawaii"; };
  memory = { memory_enabled = true; user_profile_enabled = true; };
};
```

在评估阶段，这两者会进行深度合并。由 Nix 定义的配置键始终优先于磁盘上现有 `config.yaml` 中的配置键，但**Nix 未修改的用户自定义配置键会被保留**。这意味着，如果智能体或手动编辑添加了诸如 `skills.disabled` 或 `streaming.enabled` 这样的配置键，它们在执行 `nixos-rebuild switch` 操作后依然存在。

:::note 模型命名
`settings.model.default` 使用的是您的提供商所期望的模型标识符。对于默认使用的 [OpenRouter](https://openrouter.ai)，这些标识符通常为 `"anthropic/claude-sonnet-4"` 或 `"google/gemini-3-flash"`。如果您直接使用某些提供商（如 Anthropic、OpenAI），则需将 `settings.model.base_url` 设置为指向其 API 的地址，并使用该提供商提供的原生模型标识符（例如 `"claude-sonnet-4-20250514"`）。若未设置 `base_url`，Hermes 会默认使用 OpenRouter。
:::

:::tip 查找可用的配置键
运行 `nix build .#configKeys && cat result` 即可查看从 Python 的 `DEFAULT_CONFIG` 中提取出的所有配置键。您也可以将现有的 `config.yaml` 内容粘贴到 `settings` 属性集中——两者结构是一一对应的。
:::

<details>
<summary><strong>完整示例：所有常见的自定义设置</strong></summary>

```nix
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    container.enable = true;

    # ── Model ──────────────────────────────────────────────────────────
    settings = {
      model = {
        base_url = "https://openrouter.ai/api/v1";
        default = "anthropic/claude-opus-4.6";
      };
      toolsets = [ "all" ];
      max_turns = 100;
      terminal = { backend = "local"; cwd = "."; timeout = 180; };
      compression = {
        enabled = true;
        threshold = 0.85;
        summary_model = "google/gemini-3-flash-preview";
      };
      memory = { memory_enabled = true; user_profile_enabled = true; };
      display = { compact = false; personality = "kawaii"; };
      agent = { max_turns = 60; verbose = false; };
    };

    # ── Secrets ────────────────────────────────────────────────────────
    environmentFiles = [ config.sops.secrets."hermes-env".path ];

    # ── Documents ──────────────────────────────────────────────────────
    documents = {
      "USER.md" = ./documents/USER.md;
    };

    # ── MCP Servers ────────────────────────────────────────────────────
    mcpServers.filesystem = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-filesystem" "/data/workspace" ];
    };

    # ── Container options ──────────────────────────────────────────────
    container = {
      image = "ubuntu:24.04";
      backend = "docker";
      hostUsers = [ "your-username" ];
      extraVolumes = [ "/home/user/projects:/projects:rw" ];
      extraOptions = [ "--gpus" "all" ];
    };

    # ── Service tuning ─────────────────────────────────────────────────
    addToSystemPackages = true;
    extraArgs = [ "--verbose" ];
    restart = "always";
    restartSec = 5;
  };
}
```

</details>

### 应急方案：自行配置

如果您希望完全在 Nix 之外管理 `config.yaml`，可以使用 `configFile`：

```nix
services.hermes-agent.configFile = /etc/hermes/config.yaml;
```

此方式完全绕过了`settings`设置——既不进行合并操作，也不生成新内容。每次启动时，该文件都会原封不动地被复制到`$

```nix
{
  sops = {
    defaultSopsFile = ./secrets/hermes.yaml;
    age.keyFile = "/home/user/.config/sops/age/keys.txt";
    secrets."hermes-env" = { format = "yaml"; };
  };

  services.hermes-agent.environmentFiles = [
    config.sops.secrets."hermes-env".path
  ];
}
```

密钥文件中包含键值对：

```yaml
# secrets/hermes.yaml (encrypted with sops)
hermes-env: |
    OPENROUTER_API_KEY=sk-or-...
    TELEGRAM_BOT_TOKEN=123456:ABC...
    ANTHROPIC_API_KEY=sk-ant-...
```

### agenix

```nix
{
  age.secrets.hermes-env.file = ./secrets/hermes-env.age;

  services.hermes-agent.environmentFiles = [
    config.age.secrets.hermes-env.path
  ];
}
```

### OAuth / 认证信息初始化

对于需要使用 OAuth 的平台（例如 Discord），可在首次部署时通过 `authFile` 参数来设置认证凭证。

```nix
{
  services.hermes-agent = {
    authFile = config.sops.secrets."hermes/auth.json".path;
    # authFileForceOverwrite = true;  # overwrite on every activation
  };
}
```

仅当`auth.json`文件不存在时，才会复制该文件（除非设置了`authFileForceOverwrite = true`）。运行时的OAuth令牌刷新信息会被保存到状态目录中，并在重新构建后依然保留。

---

## 文档

`documents`选项用于将文件安装到代理的工作目录中（即`workingDirectory`，代理将其视为工作空间）。Hermes会按照惯例查找特定的文件名：

- **`USER.md`** — 用于说明代理正在与之交互的用户的相关信息。
- 您放置在此处的其他所有文件都会作为工作空间文件被代理识别。

代理的身份文件则是单独存储的：Hermes会从`$

```nix
{
  services.hermes-agent.documents = {
    "USER.md" = ./documents/USER.md;  # path reference, copied from Nix store
  };
}
```

值可以是内联字符串或路径引用。这些文件会在每次执行 `nixos-rebuild switch` 时被重新安装。

---

## MCP 服务器

`mcpServers` 选项用于以声明式方式配置 [MCP（模型上下文协议）](https://modelcontextprotocol.io) 服务器。每个服务器均采用 **stdio**（本地命令）或 **HTTP**（远程 URL）传输方式。

### Stdio 传输方式（本地服务器）

```nix
{
  services.hermes-agent.mcpServers = {
    filesystem = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-filesystem" "/data/workspace" ];
    };
    github = {
      command = "npx";
      args = [ "-y" "@modelcontextprotocol/server-github" ];
      env.GITHUB_PERSONAL_ACCESS_TOKEN = "\${GITHUB_TOKEN}"; # resolved from .env
    };
  };
}
```

:::提示
在运行时，`env` 中指定的环境变量值会从 `$HERMES_HOME/.env` 文件中读取。建议使用 `environmentFiles` 功能来注入敏感信息——切勿将令牌直接写入 Nix 配置文件中。
:::

### HTTP 传输方式（远程服务器）

```nix
{
  services.hermes-agent.mcpServers.remote-api = {
    url = "https://mcp.example.com/v1/mcp";
    headers.Authorization = "Bearer \${MCP_REMOTE_API_KEY}";
    timeout = 180;
  };
}
```

### 基于 OAuth 的 HTTP 传输方式

对于使用 OAuth 2.1 的服务器，需将 `auth` 参数设置为 `"oauth"`。Hermes 支持完整的 PKCE 流程——包括元数据发现、动态客户端注册、令牌交换以及自动刷新功能。

```nix
{
  services.hermes-agent.mcpServers.my-oauth-server = {
    url = "https://mcp.example.com/mcp";
    auth = "oauth";
  };
}
```

令牌会被存储在 `$HERMES_HOME/mcp-tokens/<server-name>.json` 中，因此即使在重启或重新构建后也能保持不变。

<details>
<summary><strong>无头服务器上的初始 OAuth 授权</strong></summary>

首次进行 OAuth 授权时需要通过基于浏览器的同意流程来完成。在无头部署环境中，Hermes 会将授权 URL 输出到标准输出/日志中，而不会打开浏览器。

**方案 A：交互式引导** — 通过 `docker exec`（针对容器）或 `sudo -u hermes`（针对原生环境）运行该流程一次即可：

```bash
# Container mode
docker exec -it hermes-agent \
  hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth

# Native mode
sudo -u hermes HERMES_HOME=/var/lib/hermes/.hermes \
  hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth
```

该容器使用了 `--network=host` 参数，因此主机上的浏览器能够访问位于 `127.0.0.1` 的 OAuth 回调监听器。

**方案 B：预置令牌**——在工作站上完成相关流程，随后复制令牌：

```bash
hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth
scp ~/.hermes/mcp-tokens/my-oauth-server{,.client}.json \
    server:/var/lib/hermes/.hermes/mcp-tokens/
# Ensure: chown hermes:hermes, chmod 0600
```

</details>

### 取样（服务器发起的LLM请求）

某些MCP服务器能够向智能体请求LLM生成的内容：

```nix
{
  services.hermes-agent.mcpServers.analysis = {
    command = "npx";
    args = [ "-y" "analysis-server" ];
    sampling = {
      enabled = true;
      model = "google/gemini-3-flash";
      max_tokens_cap = 4096;
      timeout = 30;
      max_rpm = 10;
    };
  };
}
```

## 托管模式

当通过 NixOS 模块运行 Hermes 时，以下 CLI 命令会被**禁止使用**，并会显示带有说明的错误信息，指引您查看 `configuration.nix` 文件：

| 被禁止的命令 | 原因 |
|---|---|
| `hermes setup` | 配置为声明式形式——请在 Nix 配置文件中编辑 `settings` |
| `hermes config edit` | 配置是由 `settings` 生成的 |
| `hermes config set <key> <value>` | 配置是由 `settings` 生成的 |
| `hermes gateway install` | systemd 服务由 NixOS 管理 |
| `hermes gateway uninstall` | systemd 服务由 NixOS 管理 |

这样可避免 Nix 中声明的配置与磁盘上的实际配置出现不一致。系统通过两种信号来检测这种差异：

1. **`HERMES_MANAGED=true`** 环境变量——由 systemd 服务设置，可供网关进程读取
2. **`HERMES_HOME` 目录下的 `.managed` 标记文件**——由激活脚本设置，可供交互式 shell 读取（例如，`docker exec -it hermes-agent hermes config set ...` 这类命令也会被禁止）

如需更改配置，请编辑您的 Nix 配置文件，然后运行 `sudo nixos-rebuild switch`。

---

## 容器架构

:::info
仅当您设置了 `container.enable = true` 时，本节内容才适用。在原生模式部署中可跳过此部分。
:::

启用容器模式后，Hermes 会在一个持久化的 Ubuntu 容器中运行，而 Nix 编译生成的二进制文件则从主机以只读方式挂载到该容器中：

```
Host                                    Container
────                                    ─────────
/nix/store/...-hermes-agent-0.1.0  ──►  /nix/store/... (ro)
~/.hermes -> /var/lib/hermes/.hermes       (symlink bridge, per hostUsers)
/var/lib/hermes/                    ──►  /data/          (rw)
  ├── current-package -> /nix/store/...    (symlink, updated each rebuild)
  ├── .gc-root -> /nix/store/...           (prevents nix-collect-garbage)
  ├── .container-identity                  (sha256 hash, triggers recreation)
  ├── .hermes/                             (HERMES_HOME)
  │   ├── .env                             (merged from environment + environmentFiles)
  │   ├── config.yaml                      (Nix-generated, deep-merged by activation)
  │   ├── .managed                         (marker file)
  │   ├── .container-mode                  (routing metadata: backend, exec_user, etc.)
  │   ├── state.db, sessions/, memories/   (runtime state)
  │   └── mcp-tokens/                      (OAuth tokens for MCP servers)
  ├── home/                                ──►  /home/hermes    (rw)
  └── workspace/                           (agent working directory)
      ├── SOUL.md                          (from documents option)
      └── (agent-created files)

Container writable layer (apt/pip/npm):   /usr, /usr/local, /tmp
```

在 Ubuntu 容器中，通过绑定挂载 `/nix/store`，Nix 构建的二进制文件可以正常运行——因为它自带解释器及所有依赖项，因此无需依赖容器的系统库。容器的入口点通过一个名为 `current-package` 的符号链接来确定，即 `/data/current-package/bin/hermes gateway run --replace`。执行 `nixos-rebuild switch` 时，仅会更新该符号链接，容器则会继续运行。

### 各要素的持久性对比

| 操作 | 是否重新创建容器 | `/data`（状态数据） | `/home/hermes` | 可写层（`apt`/`pip`/`npm`） |
|---|---|---|---|---|
| `systemctl restart hermes-agent` | 否 | 持久保留 | 持久保留 | 持久保留 |
| `nixos-rebuild switch`（代码变更） | 否（仅更新符号链接） | 持久保留 | 持久保留 | 持久保留 |
| 主机重启 | 否 | 持久保留 | 持久保留 | 持久保留 |
| `nix-collect-garbage` | 否（GC 根节点不变） | 持久保留 | 持久保留 | 持久保留 |
| 镜像变更（`container.image`） | **是** | 持久保留 | 持久保留 | **丢失** |
| 卷/选项变更 | **是** | 持久保留 | 持久保留 | **丢失** |
| `environment`/`environmentFiles` 变更 | 否 | 持久保留 | 持久保留 | 持久保留 |

只有当容器的**身份哈希**发生变化时，才会重新创建容器。该哈希涵盖：架构版本、镜像、`extraVolumes`、`extraOptions` 以及入口点脚本。环境变量、设置、文档或 hermes 包本身的更改不会触发容器重建。

:::warning 可写层丢失风险
当身份哈希发生变化时（如镜像升级、新增卷或容器选项），容器会被销毁，并从最新的 `container.image` 中重新构建。此时，可写层中通过 `apt install`、`pip install` 或 `npm install` 安装的任何包都会丢失。不过，/data 和 /home/hermes 中的数据仍会保留（因为这些目录是绑定挂载的）。

如果该代理依赖某些特定包，建议将它们打包到自定义镜像中（如 `container.image = "my-registry/hermes-base:latest"`），或在其 SOUL.md 文件中编写相应的安装脚本。
:::

### GC 根节点保护机制
`preStart` 脚本会在 `${stateDir}/.gc-root` 处创建一个指向当前 hermes 包的 GC 根节点。这样可以防止 `nix-collect-garbage` 功能误删正在运行的二进制文件。如果 GC 根节点出现异常，只需重启服务即可重新生成。

---

## 插件
NixOS 模块支持声明式插件安装——无需使用命令式的 `hermes plugins install` 方法。

### 目录型插件（`extraPlugins`）
对于那些仅由包含 `plugin.yaml` 和 `__init__.py` 文件的源代码树构成的插件（例如 [hermes-lcm](https://github.com/stephenschoettler/hermes-lcm)），即可使用此方式安装。

```nix
services.hermes-agent.extraPlugins = [
  (pkgs.fetchFromGitHub {
    owner = "stephenschoettler";
    repo = "hermes-lcm";
    rev = "v0.7.0";
    hash = "sha256-...";
  })
];
```

在激活时，插件会通过符号链接的方式被添加到 `$HERMES_HOME/plugins/` 目录中。Hermes 会通过常规的目录扫描来发现这些插件。若要从列表中移除某个插件，并执行 `nixos-rebuild switch` 命令，即可同时删除对应的符号链接。

### 入口点插件（`extraPythonPackages`）

对于那些通过 `[project.entry-points."hermes_agent.plugins"]` 注册的、以 pip 包形式存在的插件（例如 [rtk-hermes](https://github.com/ogallotti/rtk-hermes)）：

```nix
services.hermes-agent.extraPythonPackages = [
  (pkgs.python312Packages.buildPythonPackage {
    pname = "rtk-hermes";
    version = "1.0.0";
    src = pkgs.fetchFromGitHub {
      owner = "ogallotti";
      repo = "rtk-hermes";
      rev = "v1.0.0";
      hash = "sha256-...";
    };
    format = "pyproject";
    build-system = [ pkgs.python312Packages.setuptools ];
  })
];
```

在Hermes封装工具中，该包的`site-packages`目录会被添加到PYTHONPATH环境变量中。`importlib.metadata`会在会话启动时自动定位到程序的入口点。

### 可选依赖组（`extraDependencyGroups`）

对于在hermes-agent的`pyproject.toml`文件中声明的可选扩展模块，可使用`extraDependencyGroups`参数在构建阶段将其纳入密封虚拟环境之中。对于那些未被包含在默认的 `[all]` 组中的额外模块而言，这是必不可少的——因为在Nix系统中无法将它们运行时安装到只读存储目录中。

```nix
# Enable Discord, Telegram, Slack
services.hermes-agent.extraDependencyGroups = [ "messaging" ];
```

```nix
# Enable a memory provider
services.hermes-agent = {
  extraDependencyGroups = [ "hindsight" ];
  settings.memory.provider = "hindsight";
};
```

该问题可通过与核心依赖项一同使用 uv 来解决——无需进行 PYTHONPATH 的修改，也不存在冲突风险。可选的组别如下：

| 组别 | 支持的功能 |
|-------|------------|
| `messaging` | Discord、Telegram、Slack |
| `matrix` | Matrix/Element（带加密功能的 mautrix；仅限 Linux） |
| `dingtalk` | DingTalk |
| `feishu` | Feishu/Lark |
| `voice` | 本地语音转文本功能（faster-whisper） |
| `edge-tts` | Edge TTS 提供服务 |
| `tts-premium` | ElevenLabs TTS 服务 |
| `anthropic` | 原生 Anthropic SDK（通过 OpenRouter 无需使用） |
| `bedrock` | AWS Bedrock（boto3 接口） |
| `azure-identity` | Azure Entra ID 认证 |
| `honcho` | Honcho 内存提供服务 |
| `hindsight` | Hindsight 内存提供服务 |
| `modal` | Modal 终端后端 |
| `daytona` | Daytona 终端后端 |
| `exa` | Exa 网络搜索 |
| `firecrawl` | Firecrawl 网络搜索 |
| `fal` | FAL 图像生成功能 |

或者，您也可以直接使用预构建的 `#messaging` 或 `#full` flake 包，而无需进行逐项配置（详见[快速入门](#quick-start-any-nix-user)）。

**如何选择合适的配置：**

| 需求 | 适用选项 |
|------|----------|
| 为 pyproject.toml 中的可选依赖项启用功能 | `extraDependencyGroups` |
| 添加 pyproject.toml 中未列出的外部 Python 插件 | `extraPythonPackages` |
| 添加系统级二进制文件（如 pandoc、jq 等） | `extraPackages` |
| 添加基于目录结构的插件源码 | `extraPlugins` |

### 同时使用两种配置

若插件依赖第三方 Python 库，则需要同时使用上述两个选项：

```nix
services.hermes-agent = {
  extraPlugins = [ my-plugin-src ];          # plugin source
  extraPythonPackages = [ pkgs.python312Packages.redis ];  # its Python dep
  extraPackages = [ pkgs.redis ];            # system binary it needs
};
```

### 使用覆盖功能

外部 flakes 可以直接覆盖该包：

```nix
{
  inputs.hermes-agent.url = "github:NousResearch/hermes-agent";
  outputs = { hermes-agent, nixpkgs, ... }: {
    nixpkgs.overlays = [ hermes-agent.overlays.default ];
    # Then:
    #   pkgs.hermes-agent.override { extraPythonPackages = [...]; }
    #   pkgs.hermes-agent.override { extraDependencyGroups = [ "hindsight" ]; }
  };
}
```

### 插件配置

插件仍需在 `config.yaml` 中进行启用。可通过声明式设置来添加这些插件：

```nix
services.hermes-agent.settings.plugins.enabled = [
  "hermes-lcm"
  "rtk-rewrite"
];
```

:::note
构建时的冲突检测机制可防止插件包覆盖 Hermes 的核心依赖项。如果某个插件提供了已存在于封闭虚拟环境中的包，`nixos-rebuild` 将会抛出明确的错误并终止执行。
:::

---

## 开发

### 开发 Shell

该 Flake 提供了一个配备 Python 3.12、uv、Node.js 以及所有运行时工具的开发 Shell：

```bash
cd hermes-agent
nix develop

# Shell provides:
#   - Python 3.12 + uv (deps installed into .venv on first entry)
#   - Node.js 22, ripgrep, git, openssh, ffmpeg on PATH
#   - Stamp-file optimization: re-entry is near-instant if deps haven't changed

hermes setup
hermes chat
```

### direnv（推荐）

随附的`.envrc`文件可自动启动开发 Shell：

```bash
cd hermes-agent
direnv allow    # one-time
# Subsequent entries are near-instant (stamp file skips dep install)
```

### Flake 检查

Flake 包含在 CI 环境及本地运行的构建时验证功能：

```bash
# Run all checks
nix flake check

# Individual checks
nix build .#checks.x86_64-linux.package-contents   # binaries exist + version
nix build .#checks.x86_64-linux.entry-points-sync  # pyproject.toml ↔ Nix package sync
nix build .#checks.x86_64-linux.cli-commands        # gateway/config subcommands
nix build .#checks.x86_64-linux.managed-guard       # HERMES_MANAGED blocks mutation
nix build .#checks.x86_64-linux.bundled-skills      # skills present in package
nix build .#checks.x86_64-linux.config-roundtrip    # merge script preserves user keys
```

<details>
<summary><strong>各检查项的验证内容</strong></summary>

| 检查项 | 验证内容 |
|---|---|
| `package-contents` | 确保 `hermes` 和 `hermes-agent` 二进制文件存在，且能够运行 `hermes version` 命令 |
| `entry-points-sync` | `pyproject.toml` 中的每个 `[project.scripts]` 条目在 Nix 包中都对应有封装好的二进制文件 |
| `cli-commands` | 运行 `hermes --help` 时能显示 `gateway` 和 `config` 子命令 |
| `managed-guard` | 当执行 `HERMES_MANAGED=true hermes config set ...` 时，应输出 NixOS 相关错误信息 |
| `bundled-skills` | 确保存在技能目录，其中包含 SKILL.md 文件，并且在封装脚本中设置了 `HERMES_BUNDLED_SKILLS` |
| `config-roundtrip` | 测试 7 种合并场景：全新安装、Nix 覆盖、保留用户配置键、混合合并、MCP 添加式合并、嵌套深度合并、幂等性测试 |

</details>

---

## 选项参考

### 核心选项

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `enable` | `bool` | `false` | 是否启用 hermes-agent 服务 |
| `package` | `package` | `hermes-agent` | 要使用的 hermes-agent 包 |
| `user` | `str` | `"hermes"` | 系统用户 |
| `group` | `str` | `"hermes"` | 系统组 |
| `createUser` | `bool` | `true` | 是否自动创建用户/组 |
| `stateDir` | `str` | `"/var/lib/hermes"` | 状态目录（位于 `HERMES_HOME` 的父目录） |
| `workingDirectory` | `str` | `"${stateDir}/workspace"` | Agent 的工作目录 |
| `addToSystemPackages` | `bool` | `false` | 是否将 `hermes` CLI 添加到系统 PATH，并在全局范围内设置 `HERMES_HOME` |

### 配置选项

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `settings` | `attrs`（深度合并） | `{}` | 以声明式方式定义的配置，最终会被渲染为 `config.yaml` 文件。支持任意层级嵌套；多个定义会通过 `lib.recursiveUpdate` 函数进行合并 |
| `configFile` | `null` 或 `path` | `null` | 已存在的 `config.yaml` 文件路径。如果指定了该选项，则会完全覆盖 `settings` 中的配置 |

### 密钥与环境变量

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `environmentFiles` | `listOf str` | `[]` | 包含密钥的环境文件路径。在服务启动时会合并到 `$HERMES_HOME/.env` 文件中 |
| `environment` | `attrsOf str` | `{}` | 非敏感的环境变量。**会显示在 Nix 存储库中**——请勿在此处存放敏感信息 |
| `authFile` | `null` 或 `path` | `null` | OAuth 凭证种子文件。仅在首次部署时会被复制 |
| `authFileForceOverwrite` | `bool` | `false` | 服务启动时是否始终用 `authFile` 中的内容覆盖 `auth.json` 文件 |

### 文档相关选项

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `documents` | `attrsOf (either str path)` | `{}` | 工作区文件。键为文件名，值为内联字符串或文件路径。在服务启动时会被安装到 `workingDirectory` 目录中 |

### MCP 服务器选项

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `mcpServers` | `attrsOf submodule` | `{}` | MCP 服务器的定义，会被合并到 `settings.mcp_servers` 中 |
| `mcpServers.<name>.command` | `null` 或 `str` | `null` | 服务器命令（采用标准输入输出传输方式） |
| `mcpServers.<name>.args` | `listOf str` | `[]` | 命令参数 |
| `mcpServers.<name>.env` | `attrsOf str` | `{}` | 服务器进程所需的环境变量 |
| `mcpServers.<name>.url` | `null` 或 `str` | `null` | 服务器端点 URL（采用 HTTP/StreamableHTTP 传输方式） |
| `mcpServers.<name>.headers` | `attrsOf str` | `{}` | HTTP 请求头，例如 `Authorization` |
| `mcpServers.<name>.auth` | `null` 或 `"oauth"` | `null` | 认证方式。设置为 `"oauth"` 时可启用 OAuth 2.1 PKCE 认证 |
| `mcpServers.<name>.enabled` | `bool` | `true` | 是否启用该服务器 |
| `mcpServers.<name>.timeout` | `null` 或 `int` | `null` | 工具调用的超时时间（单位：秒，默认值为 120） |
| `mcpServers.<name>.connect_timeout` | `null` 或 `int` | `null` | 连接建立的超时时间（单位：秒，默认值为 60） |
| `mcpServers.<name>.tools` | `null` 或 `submodule` | `null` | 工具过滤规则（包含/排除列表） |
| `mcpServers.<name>.sampling` | `null` 或 `submodule` | `null` | 针对服务器发起的 LLM 请求的采样配置 |

### 服务行为相关选项

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `extraArgs` | `listOf str` | `[]` | 传递给 `hermes gateway` 的额外参数 |
| `extraPackages` | `listOf package` | `[]` | 提供给 Agent 的额外软件包。这些包会被添加到 hermes 用户的个性化配置中，因此终端命令、技能以及定时任务都能使用到它们 |
| `extraPlugins` | `listOf package` | `[]` | 需要链接到 `$HERMES_HOME/plugins/` 目录中的插件包。每个插件包都必须包含 `plugin.yaml` 文件 |
| `extraPythonPackages` | `listOf package` | `[]` | 会被添加到 PYTHONPATH 中的 Python 包，用于发现入口点插件。这些包会通过 `python312Packages` 参数进行构建 |
| `extraDependencyGroups` | `listOf str` | `[]` | 需要包含在密封虚拟环境中的 pyproject.toml 可选依赖项（例如 `["hindsight"]`）。这些依赖项会通过 uv 工具解析，避免出现冲突 |
| `restart` | `str` | `"always"` | systemd 的 `Restart=` 策略值 |
| `restartSec` | `int` | `5` | systemd 的 `RestartSec=` 参数值 |

### 容器模式选项

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `container.enable` | `bool` | `false` | 是否启用 OCI 容器模式 |
| `container.backend` | `enum ["docker" "podman"]` | `"docker"` | 容器运行时引擎 |
| `container.image` | `str` | `"ubuntu:24.04"` | 基础镜像（会在运行时拉取） |
| `container.extraVolumes` | `listOf str` | `[]` | 额外的卷挂载配置（格式为 `host:container:mode`） |
| `container.extraOptions` | `listOf str` | `[]` | 传递给 `docker create` 命令的额外参数 |
| `container.hostUsers` | `listOf str` | `[]` | 具有交互权限的用户，这类用户会获得一个指向服务状态目录的 `~/.hermes` 符号链接，并会被自动添加到 `hermes` 组中 |

---

## 目录结构

### 原生模式

```
/var/lib/hermes/                     # stateDir (owned by hermes:hermes, 0750)
├── .hermes/                         # HERMES_HOME
│   ├── config.yaml                  # Nix-generated (deep-merged each rebuild)
│   ├── .managed                     # Marker: CLI config mutation blocked
│   ├── .env                         # Merged from environment + environmentFiles
│   ├── auth.json                    # OAuth credentials (seeded, then self-managed)
│   ├── gateway.pid
│   ├── state.db
│   ├── mcp-tokens/                  # OAuth tokens for MCP servers
│   ├── sessions/
│   ├── memories/
│   ├── skills/
│   ├── cron/
│   └── logs/
├── home/                            # Agent HOME
└── workspace/                       # Agent working directory
    ├── SOUL.md                      # From documents option
    └── (agent-created files)
```

### 容器模式

布局保持不变，直接挂载到容器中：

| 容器路径 | 主机路径 | 模式 | 备注 |
|---|---|---|---|
| `/nix/store` | `/nix/store` | `ro` | Hermes 可执行文件及所有 Nix 依赖项 |
| `/data` | `/var/lib/hermes` | `rw` | 所有状态数据、配置文件及工作区内容 |
| `/home/hermes` | `${stateDir}/home` | `rw` | 持久化的代理用户目录——用于存放 `pip install --user` 安装的包及工具缓存 |
| `/usr`, `/usr/local`, `/tmp` | （可写层） | `rw` | 通过 `apt`/`pip`/`npm` 安装的软件——数据会在重启后保留，但在重新创建容器时会被清除 |

---

## 更新操作

```bash
# Update the flake input (run from the directory containing flake.nix)
cd /etc/nixos && nix flake update hermes-agent

# Rebuild
sudo nixos-rebuild switch
```

在容器模式下，`current-package`符号链接会随之更新，代理在重启时便会加载新的二进制文件。无需重新创建容器，也不会导致已安装的软件包丢失。

---

## 故障排除

:::tip Podman用户
以下所有`docker`命令在`podman`中同样适用。如果您设置了`container.backend = "podman"`，请进行相应替换。
:::

### 服务日志

```bash
# Both modes use the same systemd unit
journalctl -u hermes-agent -f

# Container mode: also available directly
docker logs -f hermes-agent
```

### 容器检测

```bash
systemctl status hermes-agent
docker ps -a --filter name=hermes-agent
docker inspect hermes-agent --format='{{.State.Status}}'
docker exec -it hermes-agent bash
docker exec hermes-agent readlink /data/current-package
docker exec hermes-agent cat /data/.container-identity
```

### 强制重新创建容器

如果您需要重置可写层（使用全新的 Ubuntu 环境）：

```bash
sudo systemctl stop hermes-agent
docker rm -f hermes-agent
sudo rm /var/lib/hermes/.container-identity
sudo systemctl start hermes-agent
```

### 验证密钥是否已正确加载

如果代理已启动但无法与大语言模型提供商完成身份验证，请检查`.env`文件是否已正确合并：

```bash
# Native mode
sudo -u hermes cat /var/lib/hermes/.hermes/.env

# Container mode
docker exec hermes-agent cat /data/.hermes/.env
```

### GC 根对象验证

```bash
nix-store --query --roots $(docker exec hermes-agent readlink /data/current-package)
```

### 常见问题

| 症状 | 原因 | 解决方案 |
|---|---|---|
| `无法保存配置：由 NixOS 管理` | CLI 安全机制处于激活状态 | 编辑 `configuration.nix` 文件并执行 `nixos-rebuild switch` 命令 |
| `没有可用于 Discord`（或 Telegram/Slack）的适配器 | 密封式 Nix 虚拟环境中缺少消息传递相关依赖 | 安装 `#messaging` 变体：`nix profile install ...#messaging`。对于 NixOS 模块，则设置 `extraDependencyGroups = [ "messaging" ]`。可通过查看 `journalctl -u hermes-agent` 中的 `FeatureUnavailable` 或 `requirements not met` 等信息来确定具体错误原因 |
| 容器意外被重新创建 | `extraVolumes`、`extraOptions` 或 `image` 参数发生更改 | 这是正常现象——可写层会被重置。建议重新安装相关软件包或使用自定义镜像 |
| `hermes version` 显示旧版本号 | 容器未重启 | 执行 `systemctl restart hermes-agent` 命令重启服务 |
| 对 `/var/lib/hermes` 目录存在权限不足问题 | 该状态目录的权限设置为 `0750 hermes:hermes` | 可使用 `docker exec` 命令或通过 `sudo -u hermes` 来获取相应权限 |
| `nix-collect-garbage` 命令删除了 hermes 相关组件 | 缺少垃圾回收根目录 | 重启服务即可（服务的 preStart 阶段会重新生成垃圾回收根目录） |
| (Podman 环境下) `找不到名为或 ID 为 "hermes-agent" 的容器` | 普通用户无法查看 Podman 的 rootful 容器 | 为 Podman 添加无密码 sudo 权限（详见[容器模式](#container-mode)部分） |
| `找不到名为 hermes 的用户` | 容器仍在启动过程中（入口点程序尚未创建该用户） | 等待几秒后重试——CLI 会自动进行重试操作 |
| 通过 `extraPackages` 添加的工具在终端中不可用 | 需要执行 `nixos-rebuild switch` 命令来更新用户级配置文件 | 执行重建并重启操作：`nixos-rebuild switch && systemctl restart hermes-agent` |
