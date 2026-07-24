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

当您希望 Hermes 表现得更像原生集成在编辑器中的编程智能体，而非独立的 CLI 工具或消息机器人时，ACP 是理想的选择。

## Hermes 在 ACP 模式下提供的功能

Hermes 会以专为编辑器工作流设计的 `hermes-acp` 工具集运行，该工具集包括：

- 文件操作工具：`read_file`、`write_file`、`patch`、`search_files`
- 终端操作工具：`terminal`、`process`
- 网页/浏览器操作工具
- 内存管理、待办事项处理、会话搜索功能
- 智能体技能
- 代码执行与任务委派功能
- 视觉处理能力

有意排除那些不符合典型编辑器用户体验的功能，例如消息传递和定时任务管理。

## 安装方式

首先按常规方式安装 Hermes，然后在安装过程中添加 ACP 相关扩展组件即可。

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

这是一个独立的命令。终端认证流程（`hermes acp --setup`）在模型选择后会提供浏览器引导选项，因此大多数用户无需直接运行 `--setup-browser` 命令。

其功能如下：

- 若缺失，则将 Node.js 22 LTS 安装到 `~/.hermes/node/` 目录中；
- 在该目录下执行 `npm install -g agent-browser @askjo/camofox-browser` 命令进行安装（无需使用 sudo 权限，因为 `npm` 的 `--prefix` 参数会指向用户可写的、由 Hermes 管理的 Node 环境）；
- 安装 Playwright Chromium 版本，若系统中已安装 Chrome/Chromium，则直接使用。

该引导过程是幂等的——重新运行时会快速执行，且会跳过已完成的操作。

## 编辑器配置

### VS Code

请安装 [ACP Client](https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client) 扩展。

连接步骤如下：

1. 从活动栏打开 ACP Client 面板；
2. 从内置的智能体列表中选择 **Hermes Agent**；
3. 进行连接并开始聊天。

如果您希望手动定义 Hermes，可以通过 VS Code 的设置，在 `acp.agents` 下添加相应配置：

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

- 首先使用 `hermes model` 配置 Hermes 提供商凭据，或将其设置在 `~/.hermes/.env` / `~/.hermes/config.yaml` 中。

### JetBrains 环境

请使用兼容 ACP 的插件，并将其指向 `hermes acp` 或 `hermes-acp`。

## 配置与凭据

ACP 模式使用的 Hermes 配置与 CLI 相同：

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/skills/`
- `~/.hermes/state.db`

提供商的解析会使用 Hermes 的常规运行时解析器，因此 ACP 会继承当前配置的提供商及凭据。对于首次运行的 ACP 客户端，Hermes 还会提供一种终端认证方式（`--setup`），用于打开 Hermes 的交互式模型/提供商设置界面。

## 会话行为

在服务器运行期间，ACP 会话由 ACP 适配器的内存会话管理器进行跟踪。

每个会话会存储以下信息：

- 会话 ID
- 工作目录
- 所选模型
- 当前的对话历史
- 取消事件

底层的 `AIAgent` 仍然使用 Hermes 的常规持久化/日志路径，但 ACP 的 `list/load/resume/fork` 操作仅作用于当前正在运行的 ACP 服务器进程。

## 工作目录行为

ACP 会话会将编辑器的当前工作目录与 Hermes 任务 ID 绑定，因此文件操作和终端命令都会相对于编辑器的工作区执行，而非服务器进程的当前工作目录。

## 审批机制

危险的终端命令可以被转回编辑器，以审批提示的形式呈现。ACP 的审批选项比 CLI 更为简单：

- 仅允许一次
- 始终允许
- 拒绝

如果出现超时或错误，审批桥接器会拒绝该请求。

### 会话范围的自动审批

ACP 在“仅允许一次”和“始终允许”之间提供了第三种选项：**仅限当前会话允许**。在编辑器的权限提示中选择此选项后，审批记录将仅保存在当前的 ACP 会话中——此后该会话中的同类命令无需再次提示即可执行，但一旦开始新的 ACP 会话（或重启编辑器），审批状态将重置并重新发起提示。

| 选项 | 编辑器显示标签 | 范围 | 是否在重启后保留 |
|---|---|---|---|
| `allow_once` | 仅允许一次 | 当前这一次工具调用 | 否 |
| `allow_session` | 仅限当前会话允许 | 当前 ACP 会话中的所有同类调用 | 否——会话结束后清除 |
| `allow_always` | 始终允许 | 所有后续会话 | 是——写入 Hermes 的永久允许列表 |
| `deny` | 拒绝 | 当前这一次工具调用 | 否 |

对于那些在任务执行期间信任代理，但又不想创建长期有效允许列表的编辑器工作流而言，`allow_session` 是最合适的默认选项。其安全性权衡十分明确：范围越广，编辑器就越少打扰你；反之，若代理行为异常（或发生提示注入），在你察觉之前可能造成的危害就越大。对于不熟悉的命令，建议先使用 `allow_once`；在多次看到代理正确执行相同操作后，可升级为 `allow_session`；而那些真正可重复执行且永远值得信任的命令（如 `git status`），则可使用 `allow_always`。

ACP 桥接器会将这些选项映射到 Hermes 的内部审批机制——`allow_always` 会像 CLI 一样创建永久允许列表条目，而 `allow_session` 仅影响当前 ACP 会话的进程内审批缓存。

## 故障排除

### 编辑器中未显示 ACP 代理

请检查以下几点：

- 对于手动/本地开发环境，请确认自定义的 `agent_servers` 命令指向的是 `hermes acp`。
- 确保已安装 Hermes，且其路径已在系统 PATH 中。
- 确已安装 ACP 相关组件（执行命令：`cd ~/.hermes/hermes-agent && uv pip install -e '.[acp]'`）。

### ACP 启动后立即出错

请尝试以下检查步骤：

```bash
hermes acp --version
hermes acp --check
hermes doctor
hermes status
```

### 凭证缺失

ACP 模式会使用 Hermes 现有的提供程序配置。请通过以下方式配置凭证：

```bash
hermes model
```

或者通过编辑 `~/.hermes/.env` 文件来实现。终端认证流程（`hermes acp --setup`）同样可以触发交互式的提供者/模型配置。

## 参见

- [ACP 内部机制](../../developer-guide/acp-internals.md)
- [提供者运行时解析](../../developer-guide/provider-runtime.md)
- [工具运行时](../../developer-guide/tools-runtime.md)
