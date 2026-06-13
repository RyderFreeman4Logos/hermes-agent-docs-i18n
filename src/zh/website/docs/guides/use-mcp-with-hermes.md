---
sidebar_position: 6
title: "Use MCP with Hermes"
description: "A practical guide to connecting MCP servers to Hermes Agent, filtering their tools, and using them safely in real workflows"
---

# 在 Hermes 中使用 MCP

本指南将介绍如何在日常工作中实际将 MCP 与 Hermes Agent 结合使用。

虽然功能页面会解释什么是 MCP，但本指南的重点是教你如何快速且安全地发挥其价值。

## 何时应使用 MCP？

以下情况适合使用 MCP：
- 已存在基于 MCP 格式的工具，而你不想从头构建原生 Hermes 工具；
- 希望让 Hermes 通过简洁的 RPC 层操作本地或远程系统；
- 需要对每台服务器的接口访问进行精细控制；
- 希望在不修改 Hermes 核心代码的情况下，将其与内部 API、数据库或企业系统连接起来。

以下情况则不宜使用 MCP：
- Hermes 自带的工具已能很好地完成该任务；
- 服务器提供了大量危险的工具接口，而你又没有做好过滤准备；
- 仅需非常有限的集成功能，使用原生工具会更简单且更安全。

## 心理模型

可以将 MCP 视为一种适配层：

- Hermes 依然是智能体主体；
- MCP 服务器负责提供各种工具；
- Hermes 在启动或重新加载时会发现这些工具；
- 模型可以像使用普通工具一样调用它们；
- 你可以控制每台服务器的哪些工具对模型可见。

最后一点非常重要。正确的 MCP 使用方式并非“将所有东西都连接起来”，而是“仅连接必要的部分，并尽可能缩小其暴露的接口范围”。

## 第一步：安装 MCP 支持

如果你是通过标准安装脚本安装的 Hermes，那么已内置了 MCP 支持（安装程序会执行 `uv pip install -e ".[all]"` 命令）。

如果你是仅安装基础版本且需要单独添加 MCP 支持，则需自行操作：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

对于基于 npm 的服务器，需确保系统中已安装 Node.js 以及 `npx` 工具。

对于大多数 Python MCP 服务器而言，`uvx` 是一个不错的默认选择。

## 第 2 步：先添加一个服务器

从单个、安全的服务器开始构建。

示例：仅允许访问某个项目目录的文件系统。

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

接着启动 Hermes：

```bash
hermes chat
```

现在请提出一个具体的问题：

```text
Inspect this project and summarize the repo layout.
```

## 第 3 步：验证 MCP 是否已加载

您可以通过以下几种方式来验证 MCP 的加载情况：

- 在完成配置后，Hermes 的标题栏/状态栏应显示 MCP 已集成；
- 询问 Hermes 它具备哪些可用工具；
- 在配置发生更改后使用 `/reload-mcp` 命令重新加载；
- 若服务器连接失败，则查看相关日志。

一个实用的测试提示：

```text
Tell me which MCP-backed tools are available right now.
```

## 第 4 步：立即开始过滤

如果服务器提供了大量工具，请勿拖延处理。

### 示例：仅允许所需的工具通过白名单

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
```

对于敏感系统而言，这通常是最理想的默认配置。

## WSL2：在WSL中桥接Hermes与Windows版Chrome

当满足以下条件时，可采用此实用设置：

- Hermes在WSL2环境中运行
- 需要控制的浏览器是Windows上已登录的常规Chrome版本
- 从WSL直接使用`/browser connect`命令操作存在不便或不可靠性

在这种配置下，Hermes**不会**直接连接到Chrome。具体流程为：

- Hermes在WSL中运行
- Hermes启动一个本地的stdio MCP服务器
- 该MCP服务器通过Windows交互功能（如`cmd.exe`或`powershell.exe`）被启动
- 该MCP服务器随后连接到您正在使用的Windows Chrome会话

思维模型：

```text
Hermes (WSL) -> MCP stdio bridge -> Windows Chrome
```

### 为何选择此模式

- 您可以保留真实的 Windows 浏览器配置文件、Cookie 以及登录信息  
- Hermes 仍运行在它所支持的 Unix 环境中（WSL2）  
- 浏览器控制功能通过 MCP 工具实现，而无需依赖 Hermes 核心的浏览器传输机制  

### 推荐的服务器组件

建议使用 `chrome-devtools-mcp`。  

如果您的 Windows 版 Chrome 已经通过 `chrome://inspect/#remote-debugging` 开启了实时远程调试功能，可在 WSL 中按如下方式添加该组件：

```bash
hermes mcp add chrome-devtools-win --command cmd.exe --args /c npx -y chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

保存服务器配置后：

```bash
hermes mcp test chrome-devtools-win
```

接着启动一个全新的 Hermes 会话，或执行以下命令：

```text
/reload-mcp
```

### 典型提示词

加载完成后，Hermes即可直接使用以MCP为前缀的浏览器工具。例如：

```text
调用 MCP 工具 mcp_chrome_devtools_win_list_pages，列出当前浏览器标签页。
```

### 为何 `/browser connect` 不是合适的选择

当 Hermes 在 WSL 环境中运行，而 Chrome 在 Windows 系统上运行时，即便 Chrome 已打开且可调试，`/browser connect` 命令仍可能失败。

常见原因包括：

- WSL 无法访问 Chrome 向 Windows 工具暴露的本地主机端点；
- 新版本的 Chrome 实时调试机制与传统的 `ws://localhost:9222` 协议不同；
- 使用如 `chrome-devtools-mcp` 这类 Windows 端辅助工具时，能更便捷地连接浏览器。

在这些情况下，建议在相同环境配置中继续使用 `/browser connect`，而将 WSL 与 Windows 之间的浏览器桥接任务交给 MCP 来处理。

### 已知的常见问题

- 当通过 MCP 使用 Windows 标准输入输出可执行文件时，若从 Windows 挂载路径（如 `/mnt/c/Users/<you>` 或 `/mnt/c/workspace/...`）启动 Hermes，可能会出现问题。
- 若从 `/root` 或 `/home/...` 路径启动 Hermes，Windows 可能在 MCP 服务器启动前发出关于“UNC 格式当前目录”的警告。
- 如果 `chrome-devtools-mcp --autoConnect` 在枚举页面时超时，可尝试减少 Chrome 中的后台标签页或冻结标签页数量，然后再试。

### 示例：黑名单限制危险操作

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### 示例：同时禁用工具封装程序

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

## 过滤实际上会影响什么？

在 Hermes 中，通过 MCP 提供的功能可分为两类：

1. 服务器原生的 MCP 工具
- 通过以下参数进行过滤：
  - `tools.include`
  - `tools.exclude`

2. Hermes 添加的实用工具封装
- 通过以下参数进行过滤：
  - `tools.resources`
  - `tools.prompts`

### 您可能用到的实用工具封装

资源相关：
- `list_resources`
- `read_resource`

提示词相关：
- `list_prompts`
- `get_prompt`

只有同时满足以下条件时，这些封装才会出现：
- 您的配置允许使用它们；
- MCP 服务器会话确实支持相应功能。

因此，如果服务器不具备某些功能，Hermes 不会强行假装它拥有这些资源或提示词。

## 常见用法模式

### 模式 1：本地项目助手

当您希望 Hermes 在受限的工作空间内处理本地文件系统或 Git 服务器上的内容时，可使用 MCP 实现该功能。

```yaml
mcp_servers:
  fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]

  git:
    command: "uvx"
    args: ["mcp-server-git", "--repository", "/home/user/project"]
```

优质提示词：

```text
Review the project structure and identify where configuration lives.
```

```text
Check the local git state and summarize what changed recently.
```

### 模式2：GitHub 分类处理助手

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false
```

优秀的提示词：

```text
List open issues about MCP, cluster them by theme, and draft a high-quality issue for the most common bug.
```

```text
Search the repo for uses of _discover_and_register_server and explain how MCP tools are registered.
```

### 模式 3：内部 API 助手

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      include: [list_customers, get_customer, list_invoices]
      resources: false
      prompts: false
```

优质提示词：

```text
Look up customer ACME Corp and summarize recent invoice activity.
```

在这种场景下，严格的白名单机制远比排除列表更为有效。

### 模式 4：文档/知识服务器

某些 MCP 服务器提供的提示词或资源更类似于共享的知识资产，而非直接的执行动作。

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: true
      resources: true
```

优质提示词：

```text
List available MCP resources from the docs server, then read the onboarding guide and summarize it.
```

```text
List prompts exposed by the docs server and tell me which ones would help with incident response.
```

## 教程：包含过滤功能的端到端配置指南

以下是逐步操作流程。

### 第一阶段：使用严格的白名单添加 GitHub MCP

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
      prompts: false
      resources: false
```

启动 Hermes 后，输入如下命令：

```text
Search the codebase for references to MCP and summarize the main integration points.
```

### 第二阶段：仅在需要时进行扩展

如果您日后也需要问题更新功能：

```yaml
tools:
  include: [list_issues, create_issue, update_issue, search_code]
```

随后重新加载：

```text
/reload-mcp
```

### 第三阶段：添加采用不同策略的第二台服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]
```

如今，Hermes已能够将它们整合在一起：

```text
Inspect the local project files, then create a GitHub issue summarizing the bug you find.
```

这正是MCP展现强大优势的地方：无需修改Hermes核心即可实现跨系统工作流。

## 安全使用建议

### 对高风险系统优先采用白名单机制

对于任何涉及金融、面向客户或可能造成破坏的场景：
- 使用 `tools.include` 参数
- 从最小的功能集开始配置

### 禁用未使用的工具功能

如果您不希望模型浏览服务器提供的资源或提示词，可将其关闭：

```yaml
tools:
  resources: false
  prompts: false
```

### 将服务器的权限范围限制在最小范围内

示例：
- 文件系统服务器仅以单个项目目录为根目录，而非整个用户主目录；
- Git服务器仅指向一个代码仓库；
- 内部API服务器默认仅开放以读取操作为主的工具接口。

### 修改配置后请重新加载

```text
/reload-mcp
```

在以下内容更改后请执行此操作：
- 包含/排除列表
- 启用标志
- 资源/提示开关
- 认证标头/环境变量

## 按症状排查问题

### “服务器已连接，但缺少我期望的工具”

可能原因：
- 被 `tools.include` 过滤掉了
- 被 `tools.exclude` 排除了
- 通过 `resources: false` 或 `prompts: false` 禁用了工具封装功能
- 服务器实际上不支持资源/提示功能

### “服务器已配置，但无内容加载”

请检查：
- 配置中未留下 `enabled: false` 的设置
- 命令/运行时工具存在（如 `npx`、`uvx` 等）
- HTTP 接口可访问
- 认证环境变量或标头正确无误

### “为什么我看到的工具数量比 MCP 服务器声明的少？”

因为 Hermes 现在会遵循您为每个服务器设定的策略以及基于能力的注册机制。这是正常现象，通常也是期望的结果。

### “如何移除 MCP 服务器而不删除配置文件？”

请使用：

```yaml
enabled: false
```

这样虽然会保留相关配置，但能阻止连接与注册操作。

## 推荐的首选 MCP 配置

对大多数用户而言，以下服务器是不错的选择：
- 文件系统
- Git
- GitHub
- fetch / 文档相关 MCP 服务器
- 单一专注的内部 API

不太适合作为首选服务器的情况：
- 拥有大量破坏性操作且缺乏过滤机制的庞大企业系统
- 那些你对其运作机制了解不够深入、难以加以限制的服务

## 相关文档

- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [常见问题解答](/reference/faq)
- [Slash 命令](/reference/slash-commands)
