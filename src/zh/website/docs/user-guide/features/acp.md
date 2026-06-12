---
sidebar_position: 11
title: "ACP Editor Integration"
description: "Use Hermes Agent inside ACP-compatible editors such as VS Code, Zed, and JetBrains"
---

# ACP 编辑器集成

Hermes Agent 可作为 ACP 服务器运行，从而使兼容 ACP 的编辑器能够通过标准输入输出与 Hermes 进行交互，并实现以下功能的渲染：

- 聊天消息
- 工具操作状态
- 文件差异对比
- 终端命令
- 审批提示
- 流式思考过程/响应片段

当您希望 Hermes 表现为集成在编辑器中的原生编程智能体，而非独立的 CLI 或消息机器人时，ACP 是理想的选择。

## Hermes 在 ACP 模式下提供的功能

Hermes 会使用专为编辑器工作流设计的精选 `hermes-acp` 工具集运行，这些工具包括：

- 文件操作工具：`read_file`、`write_file`、`patch`、`search_files`
- 终端操作工具：`terminal`、`process`
- 网页/浏览器操作工具
- 内存管理、待办事项处理、会话搜索功能
- 各种智能体技能
- 代码执行与任务委托功能
- 视觉处理能力

有意排除那些不符合典型编辑器用户体验的功能，例如消息传递和定时任务管理。

## 安装方式

先按常规方式安装 Hermes，然后再添加 ACP 相关扩展组件：

```bash
pip install -e '.[acp]'
```

此操作会安装 `agent-client-protocol` 依赖项，并启用以下功能：

- `hermes acp`
- `hermes-acp`
- `python -m acp_adapter`

对于在 Zed 注册表中安装的情况，Zed 会通过官方的 ACP 注册表条目来启动 Hermes。该条目使用的是 `uvx` 发行版，其运行方式如下：

```bash
uvx --from 'hermes-agent[acp]==<version>' hermes-acp
```

在使用注册表安装路径之前，请确保 `PATH` 环境变量中已包含 `uv` 工具。

## 启动 ACP 服务器

执行以下任意操作即可以 ACP 模式启动 Hermes：

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

对于非交互式检查操作：

```bash
hermes acp --version
hermes acp --check
```

### 浏览器工具（可选）

浏览器工具（如 `browser_navigate`、`browser_click` 等）依赖于 `agent-browser` npm 包以及 Chromium，而这些并不包含在 Python wheel 中。请通过以下命令进行安装：

```bash
hermes acp --setup-browser           # interactive (prompts before ~400 MB download)
hermes acp --setup-browser --yes     # accept the download non-interactively
```

这是一个独立运行的命令。Zed Registry的终端认证流程（`hermes acp --setup`）在模型选择后会提供一个浏览器启动选项，因此大多数用户无需直接运行`--setup-browser`命令。

其功能如下：

- 若缺失，则将Node.js 22 LTS安装到`~/.hermes/node/`目录中；
- 在该目录下执行`npm install -g agent-browser @askjo/camofox-browser`命令进行安装（无需使用sudo权限，因为`npm`的`--prefix`参数会指向用户可写的、由Hermes管理的Node环境）；
- 安装Playwright Chromium版本，若系统已安装Chrome/Chromium，则直接使用它们。

该启动流程是幂等的——重复运行可快速执行，且会跳过已完成的操作。

## 编辑器配置

### VS Code

请安装[ACP Client](https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client)扩展。

连接步骤如下：

1. 从活动栏打开ACP Client面板；
2. 从内置的代理列表中选择**Hermes Agent**；
3. 进行连接并开始聊天。

如果希望手动定义Hermes Agent，可通过VS Code的设置项在`acp.agents`下进行添加：

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

Zed v0.221.x 及更高版本可通过官方 ACP Registry 安装外部代理。

1. 打开 Agent 面板。
2. 点击**添加代理**，或运行 `zed: acp registry` 命令。
3. 搜索**Hermes Agent**。
4. 安装该代理并启动一个新的 Hermes 外部代理线程。

前置条件：

- 首先需使用 `hermes model` 配置 Hermes 提供商的凭证，或将其设置在 `~/.hermes/.env` / `~/.hermes/config.yaml` 文件中。
- 需安装 `uv`，以便注册表启动器能够运行 `uvx --from 'hermes-agent[acp]==<version>' hermes-acp` 命令。

在注册表条目尚未可用时，如需进行本地开发，可在 Zed 设置中使用自定义代理服务器：

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

### JetBrains

请使用兼容 ACP 的插件，并将其配置为指向：

```text
/path/to/hermes-agent/acp_registry
```

## 注册表清单

Hermes 官方 ACP 注册表元数据的原始版本保存在以下地址：

```text
acp_registry/agent.json
acp_registry/icon.svg
```

上游注册表拉取请求会将这些文件复制到 `agentclientprotocol/registry` 目录下的顶级 `hermes-agent/` 文件夹中。该注册表条目所使用的 `uvx` 发行版直接指向 `hermes-agent` 的 PyPI 版本。

```text
uvx --from 'hermes-agent[acp]==<version>' hermes-acp
```

注册表 CI 会验证指定的版本是否存在于 PyPI 上，因此清单中的 `version` 字段与 uvx 的 `package` 指定值必须始终与 `pyproject.toml` 中的内容保持一致。`scripts/release.py` 会自动确保二者同步。

## 配置与凭据

ACP 模式使用与 CLI 相同的 Hermes 配置文件：

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/skills/`
- `~/.hermes/state.db`

提供者解析会使用 Hermes 的常规运行时解析器，因此 ACP 会继承当前配置的提供者及凭据。对于首次运行的注册表客户端，Hermes 还会提供一种终端认证方式（`--setup`），用于启动交互式的模型/提供者设置流程。

## 会话行为

在服务器运行期间，ACP 会话由 ACP 适配器的内存会话管理器进行跟踪。

每个会话会存储以下信息：

- 会话 ID
- 工作目录
- 所选模型
- 当前的对话历史记录
- 取消事件

底层的 `AIAgent` 仍然使用 Hermes 的常规持久化/日志路径，但 ACP 的 `list/load/resume/fork` 操作仅作用于当前正在运行的 ACP 服务器进程。

## 工作目录行为

ACP 会话会将编辑器的当前工作目录与 Hermes 任务 ID 绑定，这样文件操作和终端命令都会相对于编辑器的工作区执行，而非服务器进程的当前工作目录。

## 审批机制

危险的终端命令会被转回编辑器，并以审批提示的形式呈现。ACP 的审批选项比 CLI 更为简单：

- 仅允许一次
- 始终允许
- 拒绝

若超过时间限制或出现错误，审批桥接组件将会拒绝该请求。

### 会话范围的自动审批

ACP 在“仅允许一次”和“始终允许”之间提供了第三种选项：**仅限当前会话允许**。在编辑器的权限提示中选择此选项后，审批记录将仅保存在当前的 ACP 会话中——此后在该会话中出现的相同类型命令将无需再次审批，但一旦开启新的 ACP 会话（或重新启动编辑器），审批状态将会重置并需要重新确认。

| 选项 | 编辑器显示标签 | 适用范围 | 是否在重启后保留 |
|---|---|---|---|
| `allow_once` | 仅允许一次 | 当前这一次工具调用 | 否 |
| `allow_session` | 仅限当前会话允许 | 当前 ACP 会话中的所有相同类型调用 | 否——会话结束时清除 |
| `allow_always` | 始终允许 | 所有后续会话 | 是——写入 Hermes 的永久允许列表 |
| `deny` | 拒绝 | 当前这一次工具调用 | 否 |

对于那些在任务执行期间信任智能体但又不希望为其创建长期允许列表的编辑器工作流而言，`allow_session` 是最合适的默认选项。其安全性权衡十分明确：范围越广，编辑器打扰用户的频率就越低，但若智能体行为异常（或发生提示注入），在用户察觉之前可能造成的危害也就越大。对于不熟悉的命令，可先使用 `allow_once`；在多次看到智能体正确执行相同操作后，可升级为 `allow_session`；而那些确实永远可靠、可重复执行的命令（如 `git status`），则可使用 `allow_always`。

ACP 桥接组件会将这些选项映射到 Hermes 的内部审批机制——`allow_always` 会像 CLI 一样创建永久的允许列表条目，而 `allow_session` 仅影响当前 ACP 会话的进程内审批缓存。

## 故障排除

### 编辑器中未显示 ACP 智能体

请检查以下内容：

- 在 Zed 中，使用 `zed: acp registry` 打开 ACP 注册表，然后搜索 **Hermes Agent**。
- 若为手动或本地开发，请确认自定义的 `agent_servers` 命令指向 `hermes acp`。
- 确认 Hermes 已安装且其路径已在系统 PATH 中。
- 确认已安装 ACP 相关组件（`pip install -e '.[acp]'`）。
- 若从官方 Zed 注册表入口启动程序，则需确认 `uv` 已安装。

### ACP 启动后立即出错

请尝试以下排查步骤：

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

或者通过编辑 `~/.hermes/.env` 文件来实现。注册表客户端也可以触发 Hermes 的终端认证流程，该流程会执行相同的交互式提供者/模型配置步骤。

### Zed 注册表启动器无法找到 uv

请根据官方的 uv 安装文档安装 `uv`，然后再从 Zed 中尝试启动 Hermes Agent 线程。

## 参见

- [ACP 内部机制](../../developer-guide/acp-internals.md)
- [提供者运行时解析](../../developer-guide/provider-runtime.md)
- [工具运行时](../../developer-guide/tools-runtime.md)
