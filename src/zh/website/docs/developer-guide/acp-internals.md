---
sidebar_position: 2
title: "ACP Internals"
description: "How the ACP adapter works: lifecycle, sessions, event bridge, approvals, and tool rendering"
---

# ACP 内部实现

ACP 适配器将 Hermes 的同步式 `AIAgent` 封装在异步的 JSON-RPC 标准输入输出服务器中。

主要实现文件包括：

- `acp_adapter/entry.py`
- `acp_adapter/server.py`
- `acp_adapter/session.py`
- `acp_adapter/events.py`
- `acp_adapter/permissions.py`
- `acp_adapter/tools.py`
- `acp_adapter/auth.py`

## 启动流程

```text
hermes acp / hermes-acp / python -m acp_adapter
  -> acp_adapter.entry.main()
  -> parse --version / --check / --setup before server startup
  -> load ~/.hermes/.env
  -> configure stderr logging
  -> construct HermesACPAgent
  -> acp.run_agent(agent, use_unstable_protocol=True)
```

标准输出流专用于 ACP JSON-RPC 传输，而便于人类阅读的日志则会被写入标准错误流。

## 主要组件

### `HermesACPAgent`

`acp_adapter/server.py` 负责实现 ACP Agent 协议。

其功能包括：

- 初始化/身份验证
- 创建/加载/恢复/分叉/列出/取消会话的相关方法
- 提示用户执行操作
- 切换会话模型
- 将同步版的 AIAgent 回调函数与 ACP 异步通知机制相连接

### `SessionManager`

`acp_adapter/session.py` 用于管理正在运行的 ACP 会话。

每个会话都会存储以下信息：

- `session_id`
- `agent`
- `cwd`
- `model`
- `history`
- `cancel_event`

该管理器具备线程安全性，支持以下操作：

- 创建会话
- 获取会话信息
- 删除会话
- 分叉会话
- 列出会话
- 清理资源
- 更新当前工作目录

### 事件桥接模块

`acp_adapter/events.py` 的作用是将 AIAgent 的回调函数转换为 ACP 的 `session_update` 事件。

经过桥接处理的回调函数包括：

- `tool_progress_callback`
- `thinking_callback`（在 ACP 桥接模块中该值为 `None`，推理逻辑会通过 `step_callback` 传递）
- `step_callback`

由于 `AIAgent` 在工作线程中运行，而 ACP I/O 操作则在主线程的事件循环中处理，因此该桥接模块采用了以下机制：

```python
asyncio.run_coroutine_threadsafe(...)
```

### 权限桥接模块

`acp_adapter/permissions.py` 负责将危险的终端授权提示转换为 ACP 权限请求。

映射规则如下：

- `allow_once` -> Hermes 的 `once` 模式
- `allow_always` -> Hermes 的 `always` 模式
- 拒绝选项 -> Hermes 的 `deny` 模式

默认情况下，若超过超时时间或桥接模块发生故障，请求将被拒绝。

### 工具渲染辅助模块

`acp_adapter/tools.py` 负责将 Hermes 工具映射为 ACP 工具类型，并生成面向编辑器的内容。

示例：

- `patch` / `write_file` -> 文件差异内容
- `terminal` -> shell 命令文本
- `read_file` / `search_files` -> 文本预览内容
- 对于大量结果 -> 为保障界面显示效果而进行截断的文本块

## 会话生命周期

```text
new_session(cwd)
  -> create SessionState
  -> create AIAgent(platform="acp", enabled_toolsets=["hermes-acp"])
  -> bind task_id/session_id to cwd override

prompt(..., session_id)
  -> extract text from ACP content blocks
  -> reset cancel event
  -> install callbacks + approval bridge
  -> run AIAgent in ThreadPoolExecutor
  -> update session history
  -> emit final agent message chunk
```

### 取消操作

`cancel(session_id)`：

- 触发会话取消事件
- 在条件允许时调用 `agent.interrupt()`
- 使提示响应返回 `stop_reason="cancelled"` 

### 分叉操作

`fork_session()` 会将消息历史记录深度复制到一个新的实时会话中，从而保留对话状态，同时为该分叉会话分配独立的会话 ID 和当前工作目录。

## 提供者/认证机制行为

ACP 并未实现自身的认证存储机制。

它而是复用了 Hermes 的运行时解析器：

- `acp_adapter/auth.py`
- `hermes_cli/runtime_provider.py`

因此，ACP 会使用当前配置的 Hermes 提供者及凭据。此外，它始终会声明一种终端设置认证方式（`hermes-setup`，参数为 `--setup`），以便首次运行的 ACP 客户端能够在启动常规 ACP 会话之前，先打开 Hermes 的交互式模型/提供者配置界面。

## 当前工作目录绑定

ACP 会话会携带编辑器的当前工作目录。

会话管理器通过任务级终端/文件覆盖机制，将该工作目录与 ACP 会话 ID 相关联，从而使各类文件和终端工具能够基于编辑器的工作空间进行操作。

## 同名工具的重复调用处理

事件桥接器会按工具名称为每个工具维护一个先进先出（FIFO）的工具 ID 列表，而非仅为每个名称分配一个 ID。这一点对于以下场景非常重要：

- 并行执行同名工具
- 在同一步骤中多次调用同名工具

若没有 FIFO 队列，完成事件可能会被错误地关联到某个工具调用上。

## 审批回调的恢复机制

在提示语执行期间，ACP 会临时在终端工具上安装一个审批回调函数，之后再恢复之前的回调函数。这样即可避免让特定于 ACP 会话的审批处理程序永久性地全局保留。

## 当前限制

- ACP 会话会被保存到共享的 `~/.hermes/state.db`（SessionDB）文件中，并能在进程重启后自动恢复；这些会话也会显示在 `session_search` 中
- 目前，非文本形式的提示内容不会被用于提取请求文本
- 不同 ACP 客户端的编辑器相关用户体验可能存在差异

## 相关文件

- `tests/acp/` — ACP 测试套件
- `toolsets.py` — `hermes-acp` 工具集定义
- `hermes_cli/main.py` — `hermes acp` CLI 子命令
- `pyproject.toml` — `[acp]` 可选依赖项以及 `hermes-acp` 脚本
