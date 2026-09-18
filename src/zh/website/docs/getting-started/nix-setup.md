---
sidebar_position: 3
title: "Nix & NixOS Setup"
description: "Install and deploy Hermes Agent with Nix — from quick `nix run` to fully declarative NixOS module with container mode"
---

# Nix 与 NixOS 配置指南

:::warning 二级平台
Nix 和 NixOS 属于[二级平台](./platform-support.md#tier-2)。此处提供的 flake 文件及 NixOS 模块仅以尽力维护的方式提供。对 `main` 分支的任何修改都可能随时导致这些包出现故障。

如需获得官方支持的配置方式，请选择标准的[安装](./installation.md)途径——即使用 Docker 或 FHS 环境。
:::

Hermes Agent 提供了 Nix flake 文件、NixOS 模块以及 Home Manager 模块。

| 级别 | 适用对象 | 提供功能 |
|-------|---------|----------|
| **`nix run` / `nix profile install`** | 所有 Nix 用户（macOS、Linux） | 已预编译好所有依赖的二进制文件，可直接使用标准的 CLI 工作流程 |
| **Home Manager 模块** | 适用于任意发行版或 macOS 的单人代理 | 基于声明式的配置方式，无需 root 权限即可管理用户服务 |
| **NixOS 模块（原生版）** | NixOS 服务器部署场景 | 声明式配置、强化的 systemd 服务以及托管的密钥管理功能 |
| **NixOS 模块（容器版）** | 需要能够自行修改代码的代理 | 包含上述所有功能，同时还提供一个持久的 Ubuntu 容器，代理可在其中使用 `apt`/`pip`/`npm install` 进行软件安装 |
:::info 与标准安装方式的区别  
`curl | bash` 安装工具会自行管理 Python、Node 及其依赖项。而 Nix flake 则完全改变了这一机制——所有的 Python 依赖项都由 [uv2nix](https://github.com/pyproject-nix/uv2nix) 构建为 Nix 衍生包，而运行时工具（如 Node.js、git、ripgrep、ffmpeg）则会被集成到二进制文件的 PATH 环境中。因此无需使用运行时的 pip，也无需激活 venv 或执行 `npm install` 命令。

**对于非 NixOS 用户**，这一变化仅体现在安装步骤上。之后的操作（如 `hermes setup`、`hermes gateway install` 以及配置编辑）与标准安装方式完全一致。

**对于使用 NixOS 模块的用户**，整个使用流程会有所不同：配置信息存储在 `configuration.nix` 文件中，敏感信息通过 sops-nix/agenix 进行管理，服务以 systemd 单元的形式存在，同时 CLI 配置命令也会被禁用。您只需像管理其他 NixOS 服务一样来管理 hermes 即可。
:::

## 先决条件

- **已启用 flakes 的 Nix 环境**——推荐使用 [Determinate Nix](https://install.determinate.systems)（它默认即可启用 flakes）
- 所需服务的**API 密钥**（至少需要 OpenRouter 或 Anthropic 的密钥）

---

## 快速开始（适用于所有 Nix 用户）

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

执行 `nix profile install` 后，`hermes`、`hermes-agent` 以及 `hermes-acp` 就会被添加到用户的 PATH 环境变量中。此后的操作流程与[标准安装方式](./installation.md)完全相同——`hermes setup` 会引导用户完成提供程序的选择，`hermes gateway install` 会配置相应的启动服务（macOS 系统使用 launchd，其他系统使用 systemd 用户服务），而所有配置文件则存储在 `~/.hermes/` 目录下。

:::warning 消息平台（Discord、Telegram、Slack）
默认安装包中已包含 `hermes-agent` 所需的所有库。如果希望使用更轻量的版本，可以查看其他 flake 输出选项。

`default` 安装包会使程序体积增加约 700 MB。而如果仅需支持消息平台功能，选择 `#messaging` 选项即可，其体积仅增加约 33 MB。

:::

<details>
<summary><strong>从本地克隆的代码库运行</strong></summary>
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

该 Flake 会导出 `nixosModules.default` —— 一个完整的 NixOS 服务模块，能够以声明式方式管理用户创建、目录设置、配置生成、机密信息处理、文档管理以及服务生命周期。

:::note
该模块需要 NixOS 支持。Hermes 是专为个人设计的代理工具。如果您需要的是个人专用代理而非系统级服务，请使用 [Home Manager 模块](#home-manager-module)。该模块既可在 NixOS 上运行，也可在 Home Manager 支持的其它系统中运行。
:::

### 添加 Flake 输入

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

就是这样。`nixos-rebuild switch` 会创建 `hermes` 用户，生成 `config.yaml` 文件，配置密钥管理，并启动网关——这是一种长期运行的服务，用于将代理与消息平台（如 Telegram、Discord 等）相连并接收传入的消息。

:::warning 需要配置密钥
上述的 `environmentFiles` 行假设您已配置了 [sops-nix](https://github.com/Mic92/sops-nix) 或 [agenix](https://github.com/ryantm/agenix)。该文件至少应包含一个大型语言模型提供商的密钥（例如 `OPENROUTER_API_KEY=sk-or-...`）。有关完整配置步骤，请参阅[密钥管理](#secrets-management)部分。如果您尚未使用密钥管理工具，也可以先使用普通文本文件作为起点——只需确保该文件不具备世界可读权限即可：

```bash
echo "OPENROUTER_API_KEY=sk-or-your-key" | sudo install -m 0600 -o hermes /dev/stdin /var/lib/hermes/env
```

```nix
services.hermes-agent.environmentFiles = [ "/var/lib/hermes/env" ];
```
:::

:::tip addToSystemPackages
将 `addToSystemPackages` 设置为 `true` 可实现两重作用：其一是将 `hermes` CLI 添加到系统的 PATH 环境变量中；其二是在系统范围内设置 `HERMES_HOME`，从而使交互式 CLI 能与网关服务共享状态（会话、技能、定时任务等信息）。若不设置此参数，在终端中运行 `hermes` 时会创建一个独立的 `~/.hermes/` 目录。

:::

### 容器感知型 CLI

:::info
当 `container.enable` 设为 `true` 且 `addToSystemPackages` 也为 `true` 时，主机上的**所有** `hermes` 命令都会自动被路由到受管理的容器中。这意味着交互式 CLI 会话将在与网关服务相同的环境中运行，并能够使用容器内安装的所有软件包和工具。

- 路由过程是完全透明的：无论是 `hermes chat`、`hermes sessions list`、`hermes --version` 等命令，实际上都是在后台执行于容器中
- 所有的 CLI 参数都会原样传递给容器
- 如果容器未运行，CLI 会短暂重试（交互模式为5秒并显示加载提示，脚本模式为10秒后无提示），之后会给出明确的错误信息——不会自动降级处理
- 对于正在参与 hermes 代码库开发的开发者，可设置 `HERMES_DEV=1` 来绕过容器路由机制，直接运行本地版本

可通过设置 `container.hostUsers` 来创建一个指向服务状态目录的 `~/.hermes` 符号链接，从而使主机 CLI 与容器之间能够共享会话、配置及运行状态信息：

```nix
services.hermes-agent = {
  container.enable = true;
  container.hostUsers = [ "your-username" ];
  addToSystemPackages = true;
};
```

`hostUsers` 中列出的用户会自动被添加到 `hermes` 组中，从而获得文件权限访问资格。

**Podman 用户：** NixOS 服务会以 root 权限运行容器。Docker 用户可通过 `docker` 组套接字获取访问权限，而 Podman 的 root 权限容器则需要使用 sudo。请为你的容器运行时配置无密码 sudo 权限：

```nix
security.sudo.extraRules = [{
  users = [ "your-username" ];
  commands = [{
    command = "/run/current-system/sw/bin/podman";
    options = [ "NOPASSWD" ];
  }];
}];
```

CLI 会自动检测是否需要使用 sudo，并在后台透明地调用它。若没有此功能，您则需手动执行 `sudo hermes chat` 命令。
:::

### 验证功能正常

执行 `nixos-rebuild switch` 后，请检查该服务是否正在运行：

```bash
# Check service status
systemctl status hermes-agent

# Watch logs (Ctrl+C to stop)
journalctl -u hermes-agent -f

# If addToSystemPackages is true, test the CLI
hermes --version
hermes config       # shows the generated config
```

### 选择部署模式

该模块支持两种模式，由 `container.enable` 参数控制：

| | **原生模式**（默认） | **容器模式** |
|---|---|---|
| 运行方式 | 在主机上运行经过强化的 systemd 服务 | 使用持久化的 Ubuntu 容器，并将 `/nix/store` 直接挂载进来 |
| 安全性 | 启用 `NoNewPrivileges`、`ProtectSystem=strict` 和 `PrivateTmp` 设置 | 通过容器隔离机制运行，以无特权用户身份执行操作 |
| Agent 是否能自行安装软件包 | 否——仅可使用 Nix 预置的 PATH 路径下的工具 | 是——`apt`、`pip`、`npm` 等工具的安装状态可在重启后保持不变 |
| 配置接口 | 与原生模式相同 | 与原生模式相同 |
| 适用场景 | 标准部署场景，需要最高安全性及可重复性 | Agent 需要在运行时安装软件包、使用可变环境或实验性工具时 |

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

`settings` 选项可接受任意属性集，这些属性集会被转换为 `config.yaml` 格式。该选项支持通过 `lib.recursiveUpdate` 在多个模块定义之间进行深度合并，因此您可以将配置分散到多个文件中：

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

在评估阶段，这两者会进行深度合并。由 Nix 定义的配置键始终优先于磁盘上现有 `config.yaml` 中的键，但**Nix 未修改的用户自定义键会被保留**。这意味着，如果智能体或手动编辑添加了诸如 `skills.disabled` 或 `streaming.enabled` 这样的键，它们在执行 `nixos-rebuild switch` 后依然存在。

:::note 模型命名
`settings.model.default` 使用的是您的服务提供商所期望的模型标识符。对于默认使用的 [OpenRouter](https://openrouter.ai)，这些标识符通常为 `"anthropic/claude-sonnet-4"` 或 `"google/gemini-3-flash"`。如果您直接使用某些服务提供商（如 Anthropic、OpenAI），则需将 `settings.model.base_url` 设置为指向其 API 的地址，并使用该提供商提供的原生模型标识符（例如 `"claude-sonnet-4-20250514"`）。若未设置 `base_url`，Hermes 会默认使用 OpenRouter。
:::

:::tip 查找可用的配置键
运行 `nix build .#configKeys && cat result` 即可查看从 Python 的 `DEFAULT_CONFIG` 中提取出的所有配置键。您也可以将现有的 `config.yaml` 内容粘贴到 `settings` attrset 中——两者结构是一一对应的。
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
    # USER.md is memory, so it goes to HERMES_HOME. Workspace files use
    # `documents`, and that option needs an explicit `workingDirectory`.
    hermesHomeFiles = {
      "memories/USER.md" = ./documents/USER.md;
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

### 应急方案：自行管理配置文件

如果您希望完全在 Nix 之外来管理 `config.yaml`，可以使用 `configFile`：

```nix
services.hermes-agent.configFile = /etc/hermes/config.yaml;
```

此方式完全绕过了`settings`设置——既不进行合并，也不生成新内容。每次启动时，该文件都会原封不动地被复制到` $HERMES_HOME/config.yaml `中。

### 自定义功能速查表

为Nix用户常用的自定义操作提供的快速参考指南：

| 我想... | 选项 | 示例 |
|---|---|---|
| 更换大语言模型 | `settings.model.default` | `"anthropic/claude-sonnet-4"` |
| 使用不同的服务提供商端点 | `settings.model.base_url` | `"https://openrouter.ai/api/v1"` |
| 添加 API 密钥 | `environmentFiles` | `[ config.sops.secrets."hermes-env".path ]` |
| 为智能体设定身份标识 | `hermesHomeFiles."SOUL.md"` | `"You are a terse ops assistant."` |
| 向工作空间添加项目上下文 | `documents."AGENTS.md"` | `./documents/AGENTS.md` |
| 运行桌面应用或控制台的后端服务 | `backend.mode` | `"serve"` 或 `"dashboard"` |
| 添加 MCP 工具服务器 | `mcpServers.<name>` | 请参阅 [MCP 工具服务器](#mcp-servers) |
| 启用 Discord/Telegram/Slack 功能 | `extraDependencyGroups` | `[ "messaging" ]` |
| 将主机目录挂载到容器中 | `container.extraVolumes` | `[ "/data:/data:rw" ]` |
| 向容器授予 GPU 使用权限 | `container.extraOptions` | `[ "--gpus" "all" ]` |
| 使用 Podman 代替 Docker | `container.backend` | `"podman"` |
| 在主机 CLI 与容器之间共享状态 | `container.hostUsers` | `[ "sidbin" ]` |
| 为智能体提供额外工具 | `extraPackages` | `[ pkgs.pandoc pkgs.imagemagick ]` |
| 使用自定义基础镜像 | `container.image` | `"ubuntu:24.04"` |
| 覆盖 hermes 相关包的设置 | `package` | `inputs.hermes-agent.packages.${system}.default.override { ... }` |
| 更改状态存储目录 | `stateDir` | `"/opt/hermes"` |
| 设置智能体的工作目录 | `workingDirectory` | `"/home/user/projects"` |

## 密钥管理

:::danger 绝不要将 API 密钥放入 `settings` 或 `environment` 中  
Nix 表达式中的值最终会存储在 `/nix/store` 目录中，该目录对所有用户都是可读的。因此，在使用密钥管理工具时，请务必通过 `environmentFiles` 来传递敏感信息。
:::

在系统启动时（执行 `nixos-rebuild switch` 操作），`environment`（非敏感变量）和 `environmentFiles`（敏感文件）会被合并到 `$HERMES_HOME/.env` 文件中。Hermes 每次启动时都会读取该文件，因此只需执行 `systemctl restart hermes-agent` 即可使更改生效，无需重新创建容器。

### sops-nix

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

该密钥文件中包含键值对：

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

### OAuth/身份认证初始化

对于需要使用 OAuth 的平台（例如 Discord），可在首次部署时通过 `authFile` 参数来上传相应的认证凭证。

```nix
{
  services.hermes-agent = {
    authFile = config.sops.secrets."hermes/auth.json".path;
    # authFileForceOverwrite = true;  # overwrite on every activation
  };
}
```

仅当`auth.json`文件不存在时才会复制该文件（除非设置了`authFileForceOverwrite = true`）。运行时的OAuth令牌刷新信息会被保存到状态目录中，并在重新构建时得以保留。

---

## 文档

Hermes会从两个目录中读取文件，因此提供了两种选择。请根据文件应存放的目录选择相应的选项。

`documents`选项会将文件安装到代理的**工作目录**中，该目录的路径为`workingDirectory`。代理会从该工作空间中读取项目上下文信息：

```nix
{
  services.hermes-agent = {
    # documents needs this option. Read the note below.
    workingDirectory = "/var/lib/hermes/workspace";
    documents = {
      "AGENTS.md" = ./documents/AGENTS.md;   # path reference, copied from Nix store
      "notes/oncall.md" = "Page #infra before restarting anything.";
    };
  };
}
```

:::警告：文档处理功能需要明确指定工作目录  
在您设置 `workingDirectory` 之前，该模块会拒绝处理 `documents` 目录中的文件。此选项的默认值因模块而异：在 Home Manager 中为用户的家目录，而在 NixOS 中则为 `${stateDir}/workspace`。因此，若未设置默认值，文件将被保存在您未指定的目录中。只有选择与默认路径相同的目录才能满足要求。  

:::  
`hermesHomeFiles` 会安装到 **`HERMES_HOME`** 目录中。Hermes 会从该目录读取代理的身份文件及内存文件，`SOUL.md` 和 `memories/` 文件也只能从该目录被访问。若在 `documents` 目录下创建 `SOUL.md` 文件，则会生成一个工作空间文件，但 Hermes 不会将该文件作为代理的身份文件来加载。

```nix
{
  services.hermes-agent.hermesHomeFiles = {
    "SOUL.md" = "You are a helpful AI assistant.";
    "memories/USER.md" = ./documents/USER.md;
  };
}
```

每个值均为字符串或路径。这两种选项中的键都可以包含子目录，该模块会自动将这些子目录视为父目录。每次激活时都会重新安装这些文件。

`hermesHomeFiles` 无需指定 `workingDirectory`，因为该模块已拥有 `HERMES_HOME` 目录。大多数用户会选择使用 `hermesHomeFiles`。

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
在运行时，`env` 中指定的环境变量值会从 `$HERMES_HOME/.env` 文件中读取。建议使用 `environmentFiles` 来注入敏感信息——切勿将令牌直接写入 Nix 配置文件中。
:::

### HTTP 传输（远程服务器）

```nix
{
  services.hermes-agent.mcpServers.remote-api = {
    url = "https://mcp.example.com/v1/mcp";
    headers.Authorization = "Bearer \${MCP_REMOTE_API_KEY}";
    timeout = 180;
  };
}
```

### 基于 OAuth 的 HTTP 传输机制

对于使用 OAuth 2.1 协议的服务器，需将 `auth` 参数设置为 `"oauth"`。Hermes 完整实现了 PKCE 流程——包括元数据发现、动态客户端注册、令牌交换以及自动刷新功能。

```nix
{
  services.hermes-agent.mcpServers.my-oauth-server = {
    url = "https://mcp.example.com/mcp";
    auth = "oauth";
  };
}
```

令牌存储在 `$HERMES_HOME/mcp-tokens/<server-name>.json` 文件中，因此即使在重启或重新构建后也能保持不变。

<details>
<summary><strong>无头服务器上的初始 OAuth 授权</strong></summary>

首次进行 OAuth 授权时需要通过基于浏览器的同意流程来完成。在无头部署环境中，Hermes 会将授权地址输出到标准输出/日志中，而不会打开浏览器。

**方案 A：交互式引导启动** — 通过 `docker exec`（针对容器）或 `sudo -u hermes`（针对原生系统）执行该流程一次即可：

```bash
# Container mode
docker exec -it hermes-agent \
  hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth

# Native mode
sudo -u hermes HERMES_HOME=/var/lib/hermes/.hermes \
  hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth
```

该容器使用了 `--network=host` 参数，因此主机浏览器能够访问位于 `127.0.0.1` 上的 OAuth 回调监听器。

**方案 B：预置令牌**——在工作站上完成相关流程，随后复制令牌：

```bash
hermes mcp add my-oauth-server --url https://mcp.example.com/mcp --auth oauth
scp ~/.hermes/mcp-tokens/my-oauth-server{,.client}.json \
    server:/var/lib/hermes/.hermes/mcp-tokens/
# Ensure: chown hermes:hermes, chmod 0600
```

</details>

### 取样（服务器发起的LLM请求）

某些MCP服务器能够向智能体请求LLM生成结果：

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

当通过 NixOS 模块运行 hermes 时，以下 CLI 命令会被**阻断**，并显示带有说明的错误信息，指引用户查看 `configuration.nix` 文件：

| 被阻断的命令 | 原因 |
|---|---|
| `hermes setup` | 配置采用声明式方式——请在 Nix 配置文件中编辑 `settings` |
| `hermes config edit` | 配置是由 `settings` 生成的 |
| `hermes config set <key> <value>` | 配置是由 `settings` 生成的 |
| `hermes gateway install` | systemd 服务由 NixOS 管理 |
| `hermes gateway uninstall` | systemd 服务由 NixOS 管理 |

这样做可以避免 Nix 所声明的配置与磁盘上的实际配置出现不一致。系统通过两种信号来检测这种差异：

1. **`HERMES_MANAGED` 环境变量**：该变量由服务设置，网关进程会读取它。
2. **`HERMES_HOME` 目录下的 `.managed` 标记文件**：激活脚本会写入该文件，交互式 shell 会读取它。因此，类似 `docker exec -it hermes-agent hermes config set ...` 这样的命令也会被 CLI 阻断。

这两种信号都会指示负责管理安装的系统名称，从而让错误信息明确指出正确的重新构建命令。对于 NixOS 模块，对应的命令是 `sudo nixos-rebuild switch`；而对于 Home Manager 模块，则是 `home-manager switch`。

---

## Home Manager 模块

该 Flake 还会导出 `homeManagerModules.default`。Hermes 是专为个人设计的智能体，其凭证、内存、会话以及定时任务均归属于该用户。因此，在个人电脑上使用用户服务才是最佳架构。它可在 Home Manager 支持的各类发行版上运行，而不仅限于 NixOS。

其所使用的选项集与 NixOS 模块相同，即为 `services.hermes-agent`，包含相同的 `settings`、`environmentFiles`、`documents`、`mcpServers`、`extraPlugins` 以及 `backend` 选项。上述所有示例在此处均可直接使用，无需任何修改，仅有必要部分存在差异：

| | NixOS 模块 | Home Manager 模块 |
|---|---|---|
| 运行方式 | 通过 `user`、`group` 和 `createUser` 指定的系统用户 | 用户本人 |
| 状态目录 | `stateDir` 和 `/.hermes` | 直接设置为 `hermesHome`，默认值为 `~/.hermes` |
| 服务类型 | `systemd.services` | Linux 系统为 `systemd.user.services`，MacOS 系统为 `launchd.agents` |
| PATH 中的 CLI 命令 | `addToSystemPackages`，会为整个系统导出 `HERMES_HOME` | `programs.hermes-agent.enable`，仅为你当前会话导出该路径 |
| 桌面应用程序 | 不支持，因为系统服务无法拥有用户会话 | `programs.hermes-agent.desktop.enable` |
| 容器模式 | 支持 | 不支持，因为需要 root 权限及 Docker socket |

### 添加 Flake 输入

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager.url = "github:nix-community/home-manager";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
    hermes-agent.url = "github:NousResearch/hermes-agent";
  };
}
```

接着将该模块导入到您的 Home Manager 配置中。该配置既可以独立存在，也可以放在 NixOS 或 nix-darwin 配置的 `home-manager.users.<name>` 下：

```nix
{
  imports = [ hermes-agent.homeManagerModules.default ];

  services.hermes-agent = {
    enable = true;
    gateway.enable = true;
    settings.model.default = "anthropic/claude-sonnet-4";
    environmentFiles = [ config.sops.secrets."hermes-env".path ];
  };
}
```

`home-manager switch`命令会操作`~/.hermes`目录，生成`config.yaml`文件，创建`.env`配置文件，并以用户服务的形式启动网关。

:::warning 建议启用“延迟关闭”功能，否则注销时会立即停止服务
注意：请为你的账户开启“延迟关闭”功能。若未开启该功能，当您的最后一次会话结束时，systemd会立即终止用户管理器，进而导致网关也随之停止运行。由于“延迟关闭”属于账户级设置，因此Home Manager无法直接对其进行配置：

```nix
# NixOS
users.users.your-username.linger = true;
```

```bash
# anywhere else
sudo loginctl enable-linger your-username
```

macOS系统没有对应的选项。带有`RunAtLoad`属性的`launchd`代理会在用户登录时启动，并持续运行。
:::

### 运行桌面端/控制台后端

`gateway.enable`用于启动Telegram、Discord、Slack及其他平台的消息传递网关。Hermes桌面端和网页控制台则连接到另一个独立的进程，即`hermes serve`或`hermes dashboard`。`backend.mode`则会让该进程与网关一同运行：

```nix
{
  services.hermes-agent = {
    enable = true;
    gateway.enable = true;      # messaging platforms
    backend.mode = "dashboard"; # + the browser dashboard on 127.0.0.1:9119
    backend.port = 9119;
  };
}
```

`serve` 模式运行时不提供用户界面。它仅提供 Hermes Desktop 所连接的 `/api/ws` 和 `/api/pty` 套接字，且不会构建任何 Web 应用程序。而 `dashboard` 模式则不仅具备上述功能，还会提供浏览器版的管理面板。这两种模式在运行时都会使用同一个与网关关联的 `HERMES_HOME` 目录，因此会话、智能体、内存资源以及定时任务对所有模式都是共享的。`backend.mode` 在 NixOS 模式下也能以相同方式工作，但在容器模式下则不可用。

:::warning 绑定到非回环地址
默认绑定地址为 `127.0.0.1`。若绑定其他地址，则会启动仪表板的身份验证网关。此外，对于那些 `Host` 头部信息与服务器实际绑定地址不一致的请求，服务器也会予以拒绝。这是为了防止 DNS 重绑攻击。请确保将服务器绑定到客户端所使用的名称或地址。
:::

### 验证功能正常运行

```bash
# Linux
systemctl --user status hermes-agent
journalctl --user -u hermes-agent -f

# macOS
launchctl list | grep hermes
tail -f ~/Library/Logs/hermes-agent.log

hermes --version
hermes config     # shows the configuration that Nix wrote
```

## 容器架构

:::info
仅当您使用 `container.enable = true` 时，本节内容才适用。对于原生模式部署，可直接跳过。
:::

在启用容器模式后，Hermes 会在一个持久化的 Ubuntu 容器中运行，其通过 Nix 编译生成的二进制文件以只读方式从主机挂载进来：

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
      ├── AGENTS.md                        (from the documents option)
      └── (agent-created files)

Container writable layer (apt/pip/npm):   /usr, /usr/local, /tmp
```

由于 `/nix/store` 被绑定挂载，基于 Nix 构建的二进制文件能够在 Ubuntu 容器中正常运行——该二进制文件自带解释器及所有依赖项，因此无需依赖容器的系统库。容器的启动脚本通过一个名为 `current-package` 的符号链接来执行，具体路径为 `/data/current-package/bin/hermes gateway run --replace`。在执行 `nixos-rebuild switch` 操作时，仅会更新该符号链接，容器则会继续运行。

### 不同场景下的数据保留情况

| 操作 | 是否重新创建容器 | `/data`（状态数据） | `/home/hermes` | 可写层（`apt`/`pip`/`npm`） |
|---|---|---|---|---|
| `systemctl restart hermes-agent` | 否 | 保留 | 保留 | 保留 |
| `nixos-rebuild switch`（代码变更） | 否（仅更新符号链接） | 保留 | 保留 | 保留 |
| 主机重启 | 否 | 保留 | 保留 | 保留 |
| `nix-collect-garbage` | 否（仅进行垃圾回收） | 保留 | 保留 | 保留 |
| 镜像变更（`container.image`） | **是** | 保留 | 保留 | **丢失** |
| 卷/选项变更 | **是** | 保留 | 保留 | **丢失** |
| `environment`/`environmentFiles` 变更 | 否 | 保留 | 保留 | 保留 |

只有当容器的**身份哈希值**发生变化时，才会重新创建容器。该哈希值包含以下信息：架构版本、镜像版本、`extraVolumes`、`extraOptions` 以及启动脚本。而环境变量、配置设置、文档或 hermes 包本身的变更则不会触发容器的重新创建。

:::warning 可写层数据丢失  
当镜像哈希值发生变化时（如图像升级、新增卷或容器配置变更），系统会销毁当前容器，并从最新的 `container.image` 镜像重新创建容器。此时，可写层中通过 `apt install`、`pip install` 或 `npm install` 安装的软件包将会丢失。而存储在 `/data` 和 `/home/hermes` 目录中的数据则会被保留（因为这些目录是绑定挂载的）。

如果代理程序依赖某些特定软件包，建议将其打包到自定义镜像中（例如设置 `container.image = "my-registry/hermes-base:latest"`），或是在代理程序的 SOUL.md 文件中编写相应的安装脚本。  
:::

### GC 根保护机制  

`preStart` 脚本会在 `${stateDir}/.gc-root` 目录下创建一个 GC 根节点，该节点指向当前正在运行的 hermes 程序包。这一机制可防止 `nix-collect-garbage` 工具误删正在运行的二进制文件。若 GC 根节点出现异常，只需重启服务即可重新生成该节点。

---

## 插件  

NixOS 模块支持声明式插件安装——无需使用命令式的 `hermes plugins install` 命令。  

### 目录型插件（`extraPlugins`）  

对于那些仅由包含 `plugin.yaml` 和 `__init__.py` 文件的源代码树构成的插件（例如 [hermes-lcm](https://github.com/stephenschoettler/hermes-lcm)），即可使用此类插件机制。

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

在激活时，插件会以符号链接的形式被添加到 `$HERMES_HOME/plugins/` 目录中。Hermes 会通过常规的目录扫描机制来发现这些插件。若要从列表中移除某个插件并执行 `nixos-rebuild switch` 命令，即可同时删除对应的符号链接。

### 入口点插件（`extraPythonPackages`）

对于那些通过 `[project.entry-points."hermes_agent.plugins"]` 注册的、采用 pip 打包的插件（例如 [rtk-hermes](https://github.com/ogallotti/rtk-hermes)）：

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

在Hermes封装程序中，该包的`site-packages`目录会被添加到PYTHONPATH环境变量中。`importlib.metadata`会在会话启动时自动定位到对应的入口点。

### 可选依赖组（`extraDependencyGroups`）

对于在hermes-agent的`pyproject.toml`中声明的可选扩展模块，可使用`extraDependencyGroups`参数在构建阶段将其纳入密封虚拟环境之中。对于那些未包含在默认的 `[all]` 组中的额外模块，这一设置是必需的——因为在Nix系统中，无法将它们运行时安装到只读存储目录中。

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

该问题可通过与核心依赖项一同使用 `uv` 来解决——无需进行 `PYTHONPATH` 的修改，也不存在冲突风险。可选的组别如下：

| 组别 | 支持的功能 |
|-------|------------|
| `messaging` | Discord、Telegram、Slack |
| `matrix` | Matrix/Element（带加密功能的 mautrix；仅限 Linux） |
| `dingtalk` | 微信工作台 |
| `feishu` | 飞书/Lark |
| `voice` | 本地语音转文本功能（faster-whisper） |
| `edge-tts` | Edge TTS 提供商 |
| `tts-premium` | ElevenLabs 语音合成服务 |
| `anthropic` | 原生 Anthropic SDK（通过 OpenRouter 使用时无需此选项） |
| `bedrock` | AWS Bedrock（boto3 接口） |
| `azure-identity` | Azure Entra ID 身份验证 |
| `honcho` | Honcho 内存提供方 |
| `hindsight` | Hindsight 内存提供方 |
| `modal` | Modal 终端后端 |
| `daytona` | Daytona 终端后端 |
| `exa` | Exa 网页搜索功能 |
| `firecrawl` | Firecrawl 网页搜索功能 |
| `fal` | FAL 图像生成功能 |

或者，您也可以直接使用预构建的 `#messaging` 或 `#full` flake 包，而无需进行逐项配置（详见[快速入门](#quick-start-any-nix-user)）。

**如何选择合适的选项：**

| 需求 | 适用选项 |
|------|----------|
| 为 `pyproject.toml` 中的可选依赖项启用功能 | `extraDependencyGroups` |
| 添加 `pyproject.toml` 中未列出的外部 Python 插件 | `extraPythonPackages` |
| 添加系统级二进制文件（如 pandoc、jq 等） | `extraPackages` |
| 添加基于目录的插件源代码树 | `extraPlugins` |

### 同时使用两种选项

若插件依赖第三方 Python 库，则需同时使用上述两个选项：

```nix
services.hermes-agent = {
  extraPlugins = [ my-plugin-src ];          # plugin source
  extraPythonPackages = [ pkgs.python312Packages.redis ];  # its Python dep
  extraPackages = [ pkgs.redis ];            # system binary it needs
};
```

### 使用覆盖机制

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

仍需在 `config.yaml` 中启用插件。可通过声明式设置来添加它们：

```nix
services.hermes-agent.settings.plugins.enabled = [
  "hermes-lcm"
  "rtk-rewrite"
];
```

:::note
构建时的冲突检测机制可防止插件包覆盖 Hermes 的核心依赖项。如果某个插件提供了已存在于密封虚拟环境中的包，`nixos-rebuild` 将会抛出明确的错误并终止执行。
:::

---

## 开发

### 开发 Shell

该 Flake 提供了一个包含 Python 3.12、uv、Node.js 以及所有运行时工具的开发 Shell：

```bash
cd hermes-agent
nix develop

# Shell provides:
#   - Python 3.12 + uv (deps installed into .venv on first entry)
#   - Node.js 26, ripgrep, git, openssh, ffmpeg on PATH
#   - Stamp-file optimization: re-entry is near-instant if deps haven't changed

hermes setup
hermes chat
```

### direnv（推荐方案）

随附的`.envrc`文件可自动启动开发 Shell：

```bash
cd hermes-agent
direnv allow    # one-time
# Subsequent entries are near-instant (stamp file skips dep install)
```

### Flake 检查

Flake 支持在 CI 环境及本地进行构建时验证：

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
| `package-contents` | 确保 `hermes` 和 `hermes-agent` 可执行文件存在，且能正常运行 `hermes --version` 命令 |
| `entry-points-sync` | 确保 `pyproject.toml` 中的每个 `[project.scripts]` 条目在 Nix 包中都有对应的封装可执行文件 |
| `cli-commands` | 确保运行 `hermes --help` 能显示 `gateway` 和 `config` 子命令 |
| `managed-guard` | 确保执行 `HERMES_MANAGED=true hermes config set ...` 时会输出 NixOS 相关错误信息 |
| `bundled-skills` | 确保技能目录存在，其中包含 SKILL.md 文件，并且在封装脚本中已设置 `HERMES_BUNDLED_SKILLS` 参数 |
| `config-roundtrip` | 测试 7 种合并场景：全新安装、Nix 覆盖、用户密钥保留、混合合并、MCP 添加式合并、嵌套深度合并以及幂等性测试 |

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
| `stateDir` | `str` | `"/var/lib/hermes"` | 状态目录（位于 `HERMES_HOME` 目录的父目录） |
| `workingDirectory` | `str` | `"${stateDir}/workspace"` | Agent 的工作目录 |
| `addToSystemPackages` | `bool` | `false` | 是否将 `hermes` CLI 添加到系统 PATH，并在全局范围内设置 `HERMES_HOME` |

### 配置选项 |

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `settings` | `attrs`（深度合并） | `{}` | 以 `config.yaml` 格式呈现的声明式配置。支持任意层级嵌套；多个定义会通过 `lib.recursiveUpdate` 进行合并 |
| `configFile` | `null` 或 `path` | `null` | 已存在的 `config.yaml` 文件路径。若设置该选项，则会完全覆盖 `settings` 的内容 |

### 密钥与环境变量

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `environmentFiles` | `listOf str` | `[]` | 包含密钥的环境文件路径。在启动时会合并到 `$HERMES_HOME/.env` 文件中 |
| `environment` | `attrsOf str` | `{}` | 非敏感的环境变量。**会显示在 Nix 存储库中**——请勿在此处存放敏感信息 |
| `authFile` | `null` 或 `path` | `null` | OAuth 凭证种子文件。仅在首次部署时会被复制 |
| `authFileForceOverwrite` | `bool` | `false` | 启动时始终用 `authFile` 中的内容覆盖 `auth.json` 文件 |

### 文档

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `documents` | `attrsOf (either str path)` | `{}` | 工作区文件。每个键都是相对于 `workingDirectory` 的路径。若要使用此选项，必须先设置该选项 |
| `hermesHomeFiles` | `attrsOf (either str path)` | `{}` | 将放入 `HERMES_HOME` 目录的文件。`SOUL.md` 和 `memories/` 文件必须位于此处，否则 Hermes 不会加载它们 |

### MCP 服务器

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `mcpServers` | `子模块的属性` | `{}` | MCP服务器定义，会被合并到`settings.mcp_servers`中 |
| `mcpServers.<名称>.command` | `null` 或 `字符串` | `null` | 服务器命令（采用stdio传输方式） |
| `mcpServers.<名称>.args` | `字符串列表` | `[]` | 命令参数 |
| `mcpServers.<名称>.env` | `字符串的属性` | `{}` | 服务器进程所需的环境变量 |
| `mcpServers.<名称>.url` | `null` 或 `字符串` | `null` | 服务器端点URL（采用HTTP/StreamableHTTP传输方式） |
| `mcpServers.<名称>.headers` | `字符串的属性` | `{}` | HTTP请求头，例如`Authorization` |
| `mcpServers.<名称>.auth` | `null` 或 `"oauth"` | `null` | 认证方式。设置为`"oauth"`时可启用OAuth 2.1 PKCE认证 |
| `mcpServers.<名称>.enabled` | `布尔值` | `true` | 开启或关闭该服务器 |
| `mcpServers.<名称>.timeout` | `null` 或 `整数` | `null` | 工具调用的超时时间（单位：秒，默认值为120） |
| `mcpServers.<名称>.connect_timeout` | `null` 或 `整数` | `null` | 连接超时时间（单位：秒，默认值为60） |
| `mcpServers.<名称>.tools` | `null` 或 `子模块` | `null` | 工具过滤规则（包含/排除列表） |
| `mcpServers.<名称>.sampling` | `null` 或 `子模块` | `null` | 服务器发起的LLM请求的采样配置 |

### 服务行为

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `extraArgs` | `字符串列表` | `[]` | 用于 `hermes gateway` 的额外参数 |
| `extraPackages` | `包列表` | `[]` | 提供给智能体的额外包。这些包会被添加到 hermes 用户的个性化配置中，从而使终端命令、智能体技能以及定时任务都能使用它们 |
| `extraPlugins` | `包列表` | `[]` | 需要链接到 `$HERMES_HOME/plugins/` 目录下的插件包。每个包都必须包含 `plugin.yaml` 文件 |
| `extraPythonPackages` | `包列表` | `[]` | 将其添加到 PYTHONPATH 中，以便用于发现入口点插件。此类包需通过 `python312Packages` 进行构建 |
| `extraDependencyGroups` | `字符串列表` | `[]` | 需要包含在密封虚拟环境中的 pyproject.toml 可选依赖项（例如 `["hindsight"]`）。这些依赖项会由 uv 工具解析，因此不会发生冲突 |
| `restart` | `字符串` | `"always"` | systemd 的 `Restart=` 策略。macOS 系统不使用该选项 |
| `restartSec` | `整数` | `5` | systemd 的 `RestartSec=` 值。macOS 系统不使用该选项 |

### 后端服务（`hermes serve` / `hermes dashboard`）

此选项用于运行 Hermes Desktop 和网页控制面板与网关相连的进程。若启用了 `container.enable`，则无法使用此选项。

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `backend.mode` | `enum ["none" "serve" "dashboard"]` | `"none"` | `serve` 模式无需用户界面，仅提供 `/api/ws` 和 `/api/pty` 接口；`dashboard` 模式还会启动浏览器控制面板。 |
| `backend.host` | `str` | `"127.0.0.1"` | 绑定地址。除回环地址外的其他地址都会启动认证网关。 |
| `backend.port` | `port` | `9119` | 绑定端口 |
| `backend.extraArgs` | `listOf str` | `[]` | 传递给后端命令的额外参数 |

### 仅适用于 Home Manager

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `hermesHome` | `str` | `"${config.home.homeDirectory}/.hermes"` | 直接使用 `HERMES_HOME` 环境变量。NixOS 模块则根据 `stateDir` 自动生成该路径。 |
| `gateway.enable` | `bool` | `false` | 是否启动消息网关。在 NixOS 模式中，网关本身即为服务，因此该模块不存在此选项。 |

### `programs.hermes-agent`（仅适用于 Home Manager）

Home Manager 将“为我安装该应用程序”与“运行该守护进程”分开处理。`services.hermes-agent` 负责管理状态、配置及守护进程；而 `programs.hermes-agent` 则负责安装实际使用的组件，并从相关服务中读取 `hermesHome` 路径及后端地址。

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `enable` | `bool` | `false` | 将 `hermes` CLI 添加到 `home.packages` 中，并为对应的 Shell 环境导出 `HERMES_HOME` 变量 |
| `package` | `package` | `services.hermes-agent.package` | 需要安装的软件包。默认情况下会同时应用该服务中定义的 `extraPythonPackages` 和 `extraDependencyGroups`，因此二者会在同一个构建过程中被处理 |
| `desktop.enable` | `bool` | `false` | 安装 Hermes 桌面应用程序，并在 Linux 系统中生成对应的启动项 |
| `desktop.package` | `package` | `package.hermesDesktop` | 桌面应用对应的软件包。默认值与 `package` 选项一致，即该应用程序与服务将在同一个 Hermes 运行时环境中运行 |

```nix
programs.hermes-agent = {
  enable = true;
  desktop.enable = true;
};

services.hermes-agent = {
  enable = true;
  backend.mode = "serve";
  backend.sessionTokenFile = config.sops.secrets."hermes/desktop-token".path;
};
```

启动器会自带 `HERMES_HOME` 变量。桌面菜单不会读取任何 shell 配置文件，因此 `programs.hermes-agent.enable` 通过 `home.sessionVariables` 输出的值仅能传递给交互式 shell。若启动器中未设置该值，应用程序将会打开 `~/.hermes` 文件，而服务端则使用 `hermesHome`，此时用户将看不到任何会话信息或密钥。

通过 `backend.sessionTokenFile` 设置后，应用程序将直接连接到服务的后端，而非自行启动后端。双方都会在启动时读取该文件，因此令牌不会被存储到 Nix 存储路径中。若未设置此选项，则各方都会独立运行自己的后端。

由于此次架构拆分，`services.hermes-agent.installPackage` 已被移除。仍尝试设置该参数的配置将会出现错误，并指出相应的替代方案。

### 容器模式（仅限 NixOS）

| 选项 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `container.enable` | `bool` | `false` | 启用 OCI 容器模式 |
| `container.backend` | `enum ["docker" "podman"]` | `"docker"` | 容器运行时 |
| `container.image` | `str` | `"ubuntu:24.04"` | 基础镜像（运行时拉取） |
| `container.extraVolumes` | `listOf str` | `[]` | 额外卷挂载项（格式：`host:container:mode`） |
| `container.extraOptions` | `listOf str` | `[]` | 传递给 `docker create` 的额外参数 |
| `container.hostUsers` | `listOf str` | `[]` | 交互式用户列表，这些用户会获得指向服务状态目录的 `~/.hermes` 符号链接，并自动加入 `hermes` 组 |

---

## 目录结构

### 原生模式

```
/var/lib/hermes/                     # stateDir (owned by hermes:hermes, 0750)
├── .hermes/                         # HERMES_HOME
│   ├── SOUL.md                      # from hermesHomeFiles: the agent identity
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
    ├── AGENTS.md                    # from the documents option
    └── (agent-created files)
```

### 主页管理器

```
~/.hermes/                           # hermesHome (HERMES_HOME), 0700
├── SOUL.md                          # from hermesHomeFiles
├── config.yaml                      # written by Nix, merged at each activation
├── .managed                         # marker: names the system that manages this
├── .env                             # written again from environment + environmentFiles
├── auth.json                        # OAuth credentials: seeded, then Hermes owns it
├── memories/  sessions/  skills/  cron/  logs/  plugins/
└── (runtime state)

~/                                   # workingDirectory, your home by default
└── AGENTS.md                        # from the documents option
```

### 容器模式

布局保持不变，直接挂载到容器中：

| 容器路径 | 主机路径 | 模式 | 备注 |
|---|---|---|---|
| `/nix/store` | `/nix/store` | `ro` | Hermes 可执行文件及所有 Nix 依赖项 |
| `/data` | `/var/lib/hermes` | `rw` | 所有状态数据、配置文件及工作区内容 |
| `/home/hermes` | `${stateDir}/home` | `rw` | 持久化的代理用户目录——用于存放 `pip install --user` 安装的软件及工具缓存 |
| `/usr`, `/usr/local`, `/tmp` | （可写层） | `rw` | 通过 `apt`/`pip`/`npm` 安装的软件——数据会在重启后保留，但在重新创建容器时会被清除 |

---

## 更新操作

```bash
# Update the flake input (run from the directory containing flake.nix)
cd /etc/nixos && nix flake update hermes-agent

# Rebuild
sudo nixos-rebuild switch          # for the NixOS module
home-manager switch                # for the Home Manager module
```

在容器模式下，`current-package` 符号链接会得到更新，代理在重启时会自动加载新的二进制文件。无需重新创建容器，已安装的包也不会丢失。

---

## 故障排除

:::tip Podman 用户
以下所有 `docker` 命令在 `podman` 环境下同样适用。如果您设置了 `container.backend = "podman"`，则需进行相应替换。
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

如果您需要重置可写层（使用全新的 Ubuntu 系统）：

```bash
sudo systemctl stop hermes-agent
docker rm -f hermes-agent
sudo rm /var/lib/hermes/.container-identity
sudo systemctl start hermes-agent
```

### 验证密钥是否已正确加载

如果代理已启动但无法与大型语言模型服务提供商完成身份验证，请检查 `.env` 文件是否已正确合并：

```bash
# Native mode
sudo -u hermes cat /var/lib/hermes/.hermes/.env

# Container mode
docker exec hermes-agent cat /data/.hermes/.env
```

### GC根对象验证

```bash
nix-store --query --roots $(docker exec hermes-agent readlink /data/current-package)
```

### 常见问题

| Symptom | Cause | Fix |
|---|---|---|
| `Cannot save configuration: managed by NixOS` | CLI guards active | Edit `configuration.nix` and `nixos-rebuild switch` |
| `No adapter available for discord` (or telegram/slack) | Messaging deps missing from the sealed Nix venv | Install `#messaging` variant: `nix profile install ...#messaging`. For NixOS module: `extraDependencyGroups = [ "messaging" ]`. Check `journalctl -u hermes-agent` for `FeatureUnavailable` or `requirements not met` for the underlying error. |
| Container recreated unexpectedly | `extraVolumes`, `extraOptions`, or `image` changed | Expected — writable layer resets. Reinstall packages or use a custom image |
| `hermes --version` shows old version | Container not restarted | `systemctl restart hermes-agent` |
| Permission denied on `/var/lib/hermes` | State dir is `0750 hermes:hermes` | Use `docker exec` or `sudo -u hermes` |
| `nix-collect-garbage` removed hermes | GC root missing | Restart the service (preStart recreates the GC root) |
| `no container with name or ID "hermes-agent"` (Podman) | Podman rootful container not visible to regular user | Add passwordless sudo for podman (see [Container Mode](#container-mode) section) |
| `unable to find user hermes` | Container still starting (entrypoint hasn't created user yet) | Wait a few seconds and retry — the CLI retries automatically |
| Tool added via `extraPackages` not found in terminal | Requires `nixos-rebuild switch` to update the per-user profile | Rebuild and restart: `nixos-rebuild switch && systemctl restart hermes-agent` |
