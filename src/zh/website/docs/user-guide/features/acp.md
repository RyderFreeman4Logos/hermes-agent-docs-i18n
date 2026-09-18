---
sidebar_position: 11
title: "ACP Host Integration"
description: "Use Hermes Agent inside ACP-compatible editors and collaboration platforms"
---

# ACP主机集成

Hermes Agent可作为ACP服务器运行，使得兼容ACP的主机能够通过标准输入输出与Hermes进行通信。编辑器可以渲染以下内容：

- 聊天消息
- 工具操作状态
- 文件差异对比
- 终端命令
- 审批提示
- 流式思考过程/响应片段

其他主机也可使用相同协议将协作事件传递至Hermes。当您希望Hermes保留其现有的身份标识、提供程序配置、内存数据、技能及工具，而由其他应用程序负责处理对话传输时，ACP模式是理想的选择。

## Hermes在ACP模式下的功能接口

Hermes以专为编辑器工作流设计的精简版`hermes-acp`工具集运行，其中包括：

- 文件操作工具：`read_file`、`write_file`、`patch`、`search_files`
- 终端操作工具：`terminal`、`process`
- 网页/浏览器相关工具
- 内存管理、待办事项处理、会话搜索功能
- 各种技能模块
- 代码执行与任务委托功能
- 视觉处理功能

该版本刻意排除了那些不符合典型编辑器用户体验的功能，例如消息发送和定时任务管理功能。

## 安装方式

首先按常规方式安装Hermes，然后在安装过程中添加ACP相关扩展组件即可。

```bash
cd ~/.hermes/hermes-agent && uv pip install -e '.[acp]'
```

此操作会安装 `agent-client-protocol` 依赖项，并启用以下功能：

- `hermes acp`
- `hermes-acp`
- `python -m acp_adapter`

## 启动 ACP 服务器

执行以下任意命令即可以 ACP 模式启动 Hermes：

```bash
hermes acp
```

```bash
hermes-acp
```

```bash
python -m acp_adapter
```

Hermes 会将日志输出到标准错误流，从而确保标准输出流可用于 ACP JSON-RPC 数据传输。

对于非交互式检测场景：

```bash
hermes acp --version
hermes acp --check
```

### 浏览器工具（可选）

浏览器工具（如 `browser_navigate`、`browser_click` 等）依赖于 `agent-browser` npm 包以及 Chromium，而这些并不包含在 Python wheel 安装包中。请通过以下命令进行安装：

```bash
hermes acp --setup-browser           # interactive (prompts before ~400 MB download)
hermes acp --setup-browser --yes     # accept the download non-interactively
```

这是一个独立的命令。终端认证流程（`hermes acp --setup`）在模型选择后会进一步提供浏览器引导选项，因此大多数用户无需直接运行 `--setup-browser`。

其功能如下：

- 若缺失，则将 Node.js 26 安装到 `~/.hermes/node/` 目录中；
- 在该目录下执行 `npm install -g agent-browser @askjo/camofox-browser` 命令进行安装（无需使用 sudo权限，因为 `npm` 的 `--prefix` 参数会指向用户可写的、由 Hermes 管理的 Node 环境）；
- 安装 Playwright Chromium，或在使用系统自带的 Chrome/Chromium 版本时直接使用它们。

该引导操作是幂等的——重新运行时会快速执行，并跳过已完成的工作。

## 主机设置

### Buzz 频道（中继桥接）

[Buzz](https://github.com/block/buzz) 是一个基于 Nostr 的协作平台，专为人类和智能体设计。其 `buzz-acp` 工具可通过标准输入/输出将 Buzz 频道与任何 ACP 智能体连接起来：

```text
Buzz relay <-- WebSocket --> buzz-acp <-- ACP over stdio --> Hermes Agent
```

这是一种传输集成方式，而非再次安装 Hermes。`buzz-acp` 启动的子进程会使用与该主机上 `hermes` 完全相同的配置、凭据、内存资源、技能及状态。

（这与 [Buzz Desktop 的托管运行时](#buzz-desktop) 不同，后者会在本地以预置的 harness 形式启动 Hermes。而中继桥则是用于以代理身份加入 Buzz *频道*，通常部署在服务器上。）

前置条件：

- 完成 ACP 的安装并执行上述的 `hermes acp --check` 检查。
- 从 [Buzz 仓库](https://github.com/block/buzz) 编译 `buzz-acp` 及 `buzz` CLI（执行 `cargo build --release -p buzz-acp`）。
- 为 Hermes 创建专用的 Nostr 密钥对（使用 `buzz-admin generate-key`），并将其注册为中继成员（使用 `buzz-admin add-member`）。每个代理都需要独立的身份——切勿重复使用个人密钥对。
- 将该身份添加到目标 Buzz 频道中。

通过以下命令启动中继桥：

```bash
export BUZZ_RELAY_URL="wss://community.example.com"
export BUZZ_PRIVATE_KEY="..."
export BUZZ_API_TOKEN="..."
export BUZZ_ACP_AGENT_COMMAND="hermes"
export BUZZ_ACP_AGENT_ARGS="acp"

buzz-acp
```

仅当中继节点要求使用令牌进行身份验证时，才需要 `BUZZ_API_TOKEN`。请勿将私钥或 API 令牌提交到版本控制系统中或粘贴在公共代码中。

对于需要长期运行的服务器部署，应以拥有相应 Hermes 主目录的操作系统用户身份，在服务管理器下运行 `buzz-acp`。关于设置、密钥生成、频道发现以及针对各个代理的配置选项，详细说明请参见 [buzz-acp README](https://github.com/block/buzz/tree/main/crates/buzz-acp)。

该桥接组件会自动发现所有 Hermes 账户所属的 Buzz 频道，并在账户被添加到其他频道时自动完成订阅。因此，Buzz 频道成员关系即构成了访问控制边界；Hermes 无需在其自身配置中维护独立的频道列表。

若想在所有者对应的 Buzz 桌面端查看 Hermes ACP 的运行状态，可添加如下内容：

```bash
export BUZZ_ACP_RELAY_OBSERVER="true"
```

该功能会发布加密后的类型为`24200`的观察者帧，这些帧是发送给代理所有者（Buzz的NIP-AO）的。桌面端会在代理的**活动日志**中实时显示其生命周期、工具使用情况、响应内容以及使用流量。中继节点会将这些帧视为临时数据，因此必须在轮次开始前让桌面端保持在线状态；而桌面端的本地观察者存档则构成了持久化的所有者侧历史记录。

由于没有编辑器可供显示审批对话框，无头桥接节点会自行处理ACP权限请求——详情请参阅[仅限所有者使用Buzz代理](#keep-buzz-agents-owner-only)。应将此类桥接节点视为具有特殊权限的自动化工具：需使用专用的操作系统账户，限制能够触发代理操作的Buzz用户范围（`buzz-acp`可通过`BUZZ_ACP_AGENT_OWNER`参数实现仅限所有者的响应机制），并且仅允许那些需要Hermes运行的频道中的用户拥有相应权限。

### VS Code

请安装[ACP客户端](https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client)扩展程序。

连接步骤如下：

1. 从活动栏打开ACP客户端面板。
2. 从内置的代理列表中选择**Hermes Agent**。
3. 进行连接并开始聊天。

如果您希望手动定义Hermes代理，可通过VS Code的设置项在`acp.agents`下进行添加：

```json
{
  "acp.agents": {
    "Hermes Agent": {
      "command": "hermes",
      "args": ["acp"]
    }
  }
}
```

### Zed

在 Zed 的设置中将 Hermes 配置为自定义代理服务器：

1. 打开代理面板。
2. 使用以下配置添加一个自定义代理服务器：

```json
{
  "agent_servers": {
    "hermes-agent": {
      "type": "custom",
      "command": "hermes",
      "args": ["acp"]
    }
  }
}
```

3. 启动一个新的 Hermes 外部代理线程。

前提条件：

- 首先使用 `hermes model` 配置 Hermes 提供商的凭证，或将其设置在 `~/.hermes/.env` / `~/.hermes/config.yaml` 中。

### JetBrains

请使用兼容 ACP 的插件，并将其指向 `hermes acp` 或 `hermes-acp`。

### Buzz Desktop

[Buzz](https://github.com/block/buzz) 已将 Hermes Agent 作为预置运行时环境提供。
只要以常规方式安装了 Hermes，Buzz 就会自动检测到它——
打开 **设置 → 运行时环境**，即可在该列表中看到 Hermes。

如果检测失败（针对旧版本安装），请确保 ACP 启动器能在登录Shell的 PATH路径中被找到：

```bash
command -v hermes-acp || command -v hermes
```

最近安装的版本会将 `hermes` 和 `hermes-acp` 两个启动器同时写入 `~/.local/bin` 目录；对于较早版本的安装，执行 `hermes update` 命令即可添加 `hermes-acp` 启动器。作为手动替代方案，可将 Buzz 的代理命令设置为 `hermes`，并传入参数 `["acp"]`。

#### 模型选择器

Buzz Desktop（v0.5.1+）会在代理的运行时设置中展示 Hermes 的完整模型菜单。该列表通过 ACP 从 Hermes 本身获取，其中会显示你在 Hermes 中已认证的所有提供商的模型（这些模型与 `hermes model` 命令及 `/model` 接口背后展示的内容相同）。如果某个模型未出现在菜单中，说明其对应的提供商在 Hermes 端尚未配置相应的访问凭证。

模型的标识符格式为 `provider:model`（例如 `openrouter:z-ai/glm-5.1`），或是针对在 `config.yaml` 中定义的自定义 OpenAI 兼容端点所使用的 `custom:<name>:<model>` 格式。选择某个模型仅对该特定代理的会话生效，不会改变整个 Hermes 系统的默认设置——如需更改全局默认值，请使用 `hermes model` 命令。

#### 保持 Buzz 代理仅限所有者访问

Buzz 创建的每个代理均将“谁可以与该代理交互”的权限设置为“仅所有者”。当运行环境为 Hermes 时，也应保持此设置不变。

在这种配置下，两种机制会协同工作。`hermes-acp` 工具集包含了 `terminal` 和 `execute_code` 功能，而 Buzz 的 ACP 桥接层会直接以 `allow_once` 的方式响应 Hermes 的权限请求，而不会将请求上报给其他层级。因此，运行在 Buzz 中的 Hermes 代理无需任何提示即可直接在主机上执行 shell 命令。我曾让其中一个代理对某个临时目录执行 `rm -rf` 命令，它立刻就删除了该目录，全程没有任何提示。

选择“任何人”选项会将相同的Shell访问权限授予所有能够访问该频道的作者。选择此选项时，Buzz不会发出任何警告。

目前，两种显而易见的缓解措施均无效：

- 设置 `approvals.mode: manual` 可使Hermes发起权限请求，但Buzz会自动批准该请求，命令依然能够执行。
- `platform_toolsets.acp` 无法限制ACP工具集的范围，因此无法用于禁用“终端”功能。

无论处于何种模式，所有者发出的 `!shutdown` 命令均可终止代理进程，而其他用户发出的该命令则会被Buzz忽略。

## 配置与凭证

ACP模式使用与CLI相同的Hermes配置文件：

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/skills/`
- `~/.hermes/state.db`

提供者解析会使用Hermes的常规运行时解析器，因此ACP会继承当前配置的提供者及凭证。对于首次运行的ACP客户端，Hermes还会提供一种终端认证方式（`--setup`），以便用户进行交互式的模型/提供者设置。

## 主机集成

这些变量由**ACP主机进程**（如编辑器或其他代理管理工具）在其启动的Hermes子进程中设置。它们不属于用户配置项——请勿在 `.env` 或 `config.yaml` 文件中手动设置。

| 变量 | 值 | 效果 |
|------|-----|------|
| `HERMES_ACP_SKIP_CONFIGURED_MCP` | `1` | 在ACP JSON-RPC循环开始之前，跳过启动 `config.yaml` 中**全局配置的**MCP服务器。 |
在进入 ACP JSON-RPC 循环之前，Hermes 通常会先启动 `config.yaml` 中配置的所有 MCP 服务器。而对于那些自行管理 MCP 服务器的主机——即通过 `session/new` 显式指定会话所需的服务器——则无需执行这种全局启动流程；否则，某个性能较差或交互型较强的 MCP 服务器就可能会延迟 `initialize` 操作。将该标记值设置为 `1` 即可让此类主机跳过此步骤。

仅会跳过基于全局 `config.yaml` 的服务器发现过程。**通过 `session/new` 由 ACP 会话提供的 MCP 服务器仍会被注册**，因此主机不会失去其所需的功能。任何其他值（未设置、空值、`0`、`false`）都会保持默认行为，因此，即便存在看似为真的字符串，也不会悄无声息地禁用 MCP 功能。

## 会话行为

在服务器运行期间，ACP 会话由 ACP 适配器的内存会话管理器负责跟踪。

每个会话会存储以下信息：

- 会话 ID
- 工作目录
- 所选模型
- 当前对话历史记录
- 取消事件

对话内容会被保存到 Hermes 的会话数据库中，因此在 ACP 服务器重启后，仍可查看、加载、继续或复制这些对话。若在未输入提示语的情况下打开新会话，该会话仅会保留在内存中：模型发现流程不会生成空的对话历史记录行。非空状态的会话副本会立即被持久化保存，即便其当前对话历史为空，现有的会话元数据仍可被更新。

旧版本中遗留的空白行不会被自动删除。一个处于开启状态的 ACP 会话并不能说明其对应的客户端已经断开连接。在关闭相关的编辑器会话后，可使用 `hermes sessions show <id>` 查看不需要的行，然后仅通过 `hermes sessions delete <id>` 删除那些经确认为不必要的会话。

## 工作目录行为

ACP 会话会将编辑器的当前工作目录与 Hermes 任务 ID 相关联，因此文件操作和终端命令都是相对于编辑器的工作区来执行的，而非服务器进程的当前工作目录。

## 审批机制

某些危险的终端命令可能会以审批提示的形式返回给编辑器。ACP 的审批选项比 CLI 的流程更为简单：

- 仅允许一次
- 始终允许
- 拒绝

是否向用户显示该审批提示由主机决定。主机可以选择通过编程方式自动处理该请求，而无需向用户展示，这种情况下这些选项虽然会在网络上传输，但不会到达人类用户手中。Buzz Desktop 就采用这种方式，因此无论您的 `approvals` 设置为何，都应将其视为无人值守执行模式。

一旦超时或出现错误，审批桥接机制就会拒绝该请求。

### 会话级编辑自动审批

ACP 在“仅允许一次”和“始终允许”之间提供了第三种选项：**仅允许在当前会话中执行**。如果在编辑器的权限提示中选择此选项，审批记录将仅保存在当前的 ACP 会话中——此后在该会话中出现的相同命令将无需再次审批即可直接执行，但一旦开启新的 ACP 会话（或重新启动编辑器），审批状态就会重置，首次执行时仍需再次确认。

| 选项 | 编辑器标签 | 作用范围 | 是否在重启后保留 |
|---|---|---|---|
| `allow_once` | 允许一次 | 本次工具调用 | 否 |
| `allow_session` | 允许会话内使用 | 当前 ACP 会话中的所有匹配调用 | 否 —— 会话结束时清除 |
| `allow_always` | 永久允许 | 所有后续会话 | 是（会被写入 Hermes 的永久允许列表） |
| `deny` | 拒绝 | 本次工具调用 | 否 |

对于那些在任务执行期间信任智能体但又不希望创建长期有效允许列表的编辑器工作流而言，`allow_session` 是最合适的默认设置。其安全性权衡十分明确：作用范围越广，编辑器就越少干扰你；反之，若智能体行为异常（或出现提示注入），在你察觉之前可能造成的危害就越大。对于不熟悉的命令，建议先使用 `allow_once`；在多次看到智能体正确执行相同操作后，可升级为 `allow_session`；而那些你完全信任且永远不会出错的命令（例如 `git status`），则应保留 `allow_always` 选项。

ACP 桥接层会将这些选项映射到 Hermes 的内部审批机制——`allow_always` 会像 CLI 一样创建永久允许列表条目，而 `allow_session` 仅影响当前 ACP 会话的进程内审批缓存。

## 故障排除

### ACP 智能体未出现在编辑器中

请检查：

- 对于手动或本地开发环境，需确认主机命令指向 `hermes acp`。
- Hermes 已安装且其路径已添加到系统的 PATH 环境变量中。
- ACP 相关扩展也已安装（执行命令：`cd ~/.hermes/hermes-agent && uv pip install -e '.[acp]'`）。

### ACP 启动后立即出现错误

请尝试以下检查步骤：

```bash
hermes acp --version
hermes acp --check
hermes doctor
hermes status
```

### 缺少凭证

ACP 模式会使用 Hermes 现有的提供程序配置。请通过以下方式配置凭证：

```bash
hermes model
```

或者通过编辑 `~/.hermes/.env` 文件来实现。终端认证流程（`hermes acp --setup`）同样可以触发交互式的提供者/模型配置。

## 参见

- [Buzz ACP harness](https://github.com/block/buzz/tree/main/crates/buzz-acp)
- [ACP 内部机制](../../developer-guide/acp-internals.md)
- [提供者运行时解析](../../developer-guide/provider-runtime.md)
- [工具运行时](../../developer-guide/tools-runtime.md)
