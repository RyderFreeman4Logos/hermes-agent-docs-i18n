---
title: Codex App-Server Runtime (optional)
sidebar_label: Codex App-Server Runtime
---

# Codex 应用服务器运行时

Hermes 可选地将 `openai/*` 和 `openai-codex/*` 类型的任务交给 [Codex CLI 应用服务器](https://github.com/openai/codex) 处理，而无需使用自身的工具处理循环。启用该功能后，终端命令、文件编辑、沙箱环境以及 MCP 工具调用都将在 Codex 的运行时中执行——Hermes 则充当其外围壳层（负责会话数据库、斜杠命令、网关以及内存和技能管理）。

此功能**仅支持手动启用**。除非您主动开启该选项，否则 Hermes 的默认行为不会改变。Hermes 永不会自动将任务路由到该运行时。

:::提示
未使用 OpenAI Codex？只需执行 `hermes setup --portal` 即可一步配置基于 Claude/Gemini 等引擎的非 Codex 后端。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 为何选择此运行时

- 可利用与 Codex CLI 相同的认证流程，通过您的 **ChatGPT 订阅账号**（无需 API 密钥）来运行 OpenAI 智能体任务。
- 使用 **Codex 自带的工具集和沙箱环境**——包括用于终端操作/读写/搜索的 `shell`、用于结构化编辑的 `apply_patch`、用于规划任务的 `update_plan`，所有功能均在 seatbelt/landlock 沙箱环境中运行。
- **原生 Codex 插件**——如 Linear、GitHub、Gmail、日历、Canva 等——通过 `codex plugin` 安装后，会自动迁移并在您的 Hermes 会话中启用。
- **Hermes 更丰富的工具也能使用**——web_search、web_extract、浏览器自动化、视觉处理、图像生成、技能管理以及文本转语音功能均可通过 MCP 回调实现。对于 Codex 未内置的工具，它会向 Hermes 发起请求。
- **内存和技能管理功能依然可用**——Codex 产生的事件会被转换为 Hermes 的消息格式，从而使自我优化循环能够看到结构正常的对话记录。

## 模型实际可用的工具

这是大多数用户最关心的部分。当启用此运行时后，处理当前任务的模型将拥有三种独立的工具来源：

### 1. Codex 内置工具集（始终可用）

这些工具随 `codex app-server` 一同提供——无需 Hermes 参与，也不涉及 MCP 或插件。一旦运行时启动，这五种工具即可立即使用：

- **`shell`**——在沙箱环境中执行任意 shell 命令。模型可通过它读取文件（如 `cat`、`head`、`tail`）、写入文件（如 `echo > foo`、heredocs）、搜索文件（如 `find`、`rg`、`grep`）、导航目录（如 `ls`、`cd`）、运行构建命令、管理进程，以及执行任何类似 bash 的操作。
- **`apply_patch`**——以 Codex 自定的补丁格式应用结构化的多文件差异。模型可利用它进行复杂的代码编辑（如添加函数、跨文件重构）；对于一次性写入操作，仍可使用 shell heredocs。
- **`update_plan`**——Codex 内部的待办事项/计划追踪工具。功能与 Hermes 的 `todo` 工具类似，但完全由 Codex 运行时管理。
- **`view_image`**——将本地图像文件加载到对话中，以便模型查看。
- **`web_search`**——若配置了相应功能，Codex 自带内置网络搜索功能。Hermes 也通过下述回调提供基于 Firecrawl 的 `web_search` 功能；模型可自行选择使用哪种方式。

因此，**任何可通过终端完成的操作——读/写/搜/找/运行——Codex 都能原生支持**。沙箱配置文件（启用运行时时默认为 `:workspace`）决定了哪些操作可以被写入。

### 2. 原生 Codex 插件（从您安装的 `codex plugin` 自动迁移）

启用运行时后，Hermes 会查询 Codex 的 `plugin/list` RPC，并为您安装的每个插件创建一个 `[plugins."<name>@openai-curated"]` 格式的条目。这些插件本身由 Codex 管理，并通过 Codex 自带的界面完成一次授权。

以下是一些示例（OpenClaw 讨论组中认为“值得制作成视频”的插件）：

- **Linear**——查找/更新问题
- **GitHub**——搜索代码、查看 Pull Request、发表评论
- **Gmail**——读取/发送邮件
- **Google Calendar**——创建/查找日程事件
- **Outlook 日历/邮件**——通过 Microsoft 连接器实现类似功能
- **Canva**——设计生成
- ...以及您通过 `codex plugin marketplace add openai-curated` + `codex plugin install ...` 安装的其他插件

**不会被迁移的插件包括**：
- 尚未安装的插件——请先在 Codex 中完成安装。
- ChatGPT 应用市场中的插件（`app/list`）——由于您的账号已通过认证，这些插件在 Codex 中早已处于启用状态。

### 3. Hermes 工具回调（MCP 服务器，注册在 `~/.codex/config.toml` 中）

Hermes 会将自己注册为 MCP 服务器，以便 Codex 能够调用它来获取自身未内置的工具。通过该回调可使用的工具包括：

- **`web_search`** / **`web_extract`**——基于 Firecrawl 实现，相比传统爬虫方式能更高效地提取结构化内容。
- **`browser_navigate` / `browser_click` / `browser_type` / `browser_press` / `browser_snapshot` / `browser_scroll` / `browser_back` / `browser_get_images` / `browser_console` / `browser_vision`**——通过 Camofox 或 Browserbase 实现完整的浏览器自动化功能。
- **`vision_analyze`**——调用独立的视觉模型来分析图像（与 Codex 的 `view_image` 功能不同，后者仅将图像加载到对话中）。
- **`image_generate`**——通过 Hermes 的 image_gen 插件链实现图像生成。
- **`skill_view` / `skills_list`**——从 Hermes 的技能库中读取信息。
- **`text_to_speech`**——通过 Hermes 配置的提供方实现文本转语音功能。

当模型需要使用这些工具时，Codex 会通过 stdio MCP 启动 `hermes_tools_mcp_server` 子进程，调用会通过 `model_tools.handle_function_call()` 函数处理（与 Hermes 默认运行时的代码路径相同），最终结果会以常规 MCP 响应的形式返回给 Codex。

## 此运行时不支持的功能

以下四种 Hermes 工具需要依赖正在运行的 AIAgent 上下文（即任务处理循环中的状态），而无状态的 MCP 回调无法驱动它们。如果需要使用这些功能，请切换回默认运行时（`/codex-runtime auto`）：

- **`delegate_task`**——创建子智能体
- **`memory`**——Hermes 的持久化内存存储
- **`session_search`**——跨会话搜索
- **`todo`**——Hermes 的待办事项存储（Codex 的 `update_plan` 功能可视为运行时内的等效功能）

## 工作流相关功能（`/goal`、看板、定时任务）

### `/goal`（Ralph 循环）

**在此运行时上可用**。目标信息会以会话 ID 为键存储在 `state_meta` 中，后续的继续提示会作为普通用户消息通过 `run_conversation()` 函数传递，随后 Codex 会原生地处理下一个任务轮次。目标审核功能则通过辅助客户端运行（配置路径为 `config.yaml` 中的 `auxiliary.goal_judge`），与当前使用的运行时无关。如果 Codex 在审核过程中陷入停滞，审核器的“已阻塞，需要用户输入”判定可作为一种简洁的退出机制。

**需要注意的一点是**：每个继续提示都相当于一个新的 Codex 任务轮次，这意味着 Codex 需要重新从头评估命令授权策略。如果您正在处理一个需要大量写入操作的长期目标，出现的授权提示数量可能会比单次会话内的任务更多。建议将 `default_permissions = ":workspace"` 设置为该值（启用运行时时 Hermes 会自动设置此值），这样简单的workspace写入操作就不需要额外授权提示。

### 看板功能（多智能体工作流调度）

**在此运行时上可用，但存在一个细微的依赖关系**。看板调度器会将每个工作节点作为独立的 `hermes chat -q` 子进程启动，而这些子进程会读取用户的配置文件——这意味着如果全局设置了 `model.openai_runtime: codex_app_server`，那么这些工作节点也会在 Codex 运行时中启动。

在 Codex 运行时工作节点中可用的功能包括：
- Codex 的完整工具集（shell、apply_patch、update_plan、view_image、web_search）——工作节点可直接执行实际任务。
- 已迁移的 Codex 插件——如 Linear、GitHub 等。
- 用于浏览器操作、视觉处理、图像生成、技能管理以及文本转语音功能的 Hermes 工具回调。

此外，由于 MCP 回调也提供了这些功能，以下功能同样可用：
- **`kanban_complete` / `kanban_block` / `kanban_comment` / `kanban_heartbeat`**——用于工作节点间传递状态的工具。这些工具会读取环境变量 `HERMES_KANBAN_TASK`（由调度器设置），正确控制访问权限，并向由 `HERMES_KANBAN_DB` 指定的 SQLite 数据库写入数据。如果回调中缺少这些功能，运行在此运行时的工作节点虽然能完成任务，但无法反馈结果，最终会因调度器的超时机制而挂起。
- **`kanban_show` / `kanban_list`**——用于工作节点查询自身上下文的只读看板信息。
- **`kanban_create` / `kanban_unblock` / `kanban_link`**——仅 orchestrator 智能体可使用，用于向运行在 Codex 运行时的 orchestrator 智能体发送新任务。

看板工具的访问权限由调度器设置的 `HERMES_KANBAN_TASK` 环境变量控制——该变量会传递给 Codex 子进程（Codex 会继承环境变量），然后再传递给启动的 `hermes-tools` MCP 服务器子进程。这样，这些工具就能获取正确的任务 ID 并正确控制访问权限。对于 Codex 应用服务器工作节点，当存在 `HERMES_KANBAN_TASK` 时，Hermes 还会传递特定的应用服务器沙箱配置：保持 `workspace-write` 沙箱设置，将**看板数据库目录以及调度器指定的所有看板路径**添加为额外的可写根目录（分别为 `HERMES_KANBAN_WORKSPACES_ROOT`、`HERMES_KANBAN_WORKSPACE`，旧版本为 `HERMES_KANBAN_ROOT`——已去重，且数据库目录优先），同时默认保持网络禁用状态。这样既避免了使用脆弱的 `:danger-no-sandbox` 变通方案，又允许 `kanban_complete` / `kanban_block` 功能更新看板数据库，同时让工作节点能够在数据库目录之外的 workspace 挂载点（例如独立硬盘上的 `/media/.../kanban-workspaces/...` 路径——[问题 #27941](https://github.com/NousResearch/hermes-agent/issues/27941)）写入报告或生成结果文件。

### 定时任务

**尚未进行专门测试**。定时任务是通过 `cronjob` → `AIAgent.run_conversation` 的路径运行的，代码路径与 CLI 相同。如果定时任务的配置中设置了 `openai_runtime: codex_app_server`，则该任务将在 Codex 运行时中执行。工具可用性规则同样适用——Codex 内置工具、插件以及 MCP 回调功能均可使用，而智能体循环相关工具（如 `delegate_task`、memory、session_search、todo）则不可用。如果您的定时任务依赖这些功能，请将定时任务的运行环境设置为使用默认运行时的配置。

## 权衡与取舍|  | Hermes默认运行时 | Codex应用服务器（可选） |
|---|---|---|
| `delegate_task`子智能体 | 支持 | 不支持——需要智能体循环上下文 |
| `memory`、`session_search`、`todo` | 支持 | 不支持——需要智能体循环上下文 |
| `web_search`、`web_extract` | 支持 | 支持（通过MCP回调实现） |
| 浏览器自动化（Camofox/Browserbase） | 支持 | 支持（通过MCP回调实现） |
| `vision_analyze`、`image_generate` | 支持 | 支持（通过MCP回调实现） |
| `skill_view`、`skills_list` | 支持 | 支持（通过MCP回调实现） |
| `text_to_speech` | 支持 | 支持（通过MCP回调实现） |
| Codex `shell`（终端/读写/搜索/查找/运行） | 不支持 | 支持（Codex内置功能） |
| Codex `apply_patch`（结构化多文件编辑） | 不支持 | 支持（Codex内置功能） |
| Codex `update_plan`（运行时待办事项） | 不支持 | 支持（Codex内置功能） |
| Codex `view_image`（将图片加载到对话中） | 不支持 | 支持（Codex内置功能） |
| Codex沙箱环境（seatbelt/landlock功能及用户配置文件） | 不支持 | 支持（Codex内置功能） |
| ChatGPT订阅授权验证 | 不支持 | 支持（通过`openai-codex`提供程序实现） |
| 原生Codex插件（Linear、GitHub等） | 不支持 | 支持（自动迁移） |
| 用户自定义MCP服务器 | 支持 | 支持（自动迁移至Codex） |
| 背景下的内存与技能回顾功能 | 支持 | 支持（通过项目投射实现） |
| 多轮对话功能 | 支持 | 支持 |
| `/goal`（Ralph循环机制） | 支持 | 支持 |
| 看板任务调度功能 | 支持 | 支持（通过回调实现） |
| 看板协调工具功能 | 支持 | 支持（通过回调实现） |
| 所有网关平台 | 支持 | 支持 |
| 非OpenAI提供程序 | 支持 | 不适用——仅限OpenAI/Codex平台 |

### 实时显示功能

尽管智能体循环在Codex子进程中运行，但该运行时仍能将Codex的事件流接入与默认运行时相同的显示路径：

- 在对话进行过程中，实时助手状态变化、推理过程（包括摘要更新）以及stable-ID工具的启动/完成事件会同步显示在TUI界面、桌面端以及消息网关中。仅记录完成状态的历史展示功能则保持独立，因此恢复会话时仍会显示该轮对话期间出现的相同工具卡片。
- 即使关闭令牌流传输功能，网关评论仍会持续显示；即便在等待审批请求之前已处理完相关通知，实时工具事件也会被继续转发。评论功能的显示与否由`display.show_commentary`参数控制。

## 先决条件

1. **已安装Codex CLI：**
   ```bash
   npm i -g @openai/codex
   codex --version   # 0.130.0 or newer
   ```
2. **Codex OAuth 登录。** Codex 子进程会读取 `~/.codex/auth.json` 文件。该文件可通过两种方式进行配置：
   ```bash
   codex login                  # writes tokens to ~/.codex/auth.json
   ```
Hermes 自带的 `hermes auth add openai-codex` 命令会将配置信息写入 `~/.hermes/auth.json`，这属于独立的会话。如果您尚未执行该操作，请**单独运行 `codex login`**。

3. **（可选）安装您需要的 Codex 插件。** 当启用运行时环境后，Hermes 会自动迁移您之前通过 Codex CLI 安装的精选插件。
   ```bash
   codex plugin marketplace add openai-curated
   # then via codex's TUI, install Linear / GitHub / Gmail / etc.
   ```
Hermes 会自动发现这些插件，并在 `~/.codex/config.toml` 文件中写入 `[plugins."<name>@openai-curated"]` 格式的条目。

## 启用方式

在 Hermes 会话中：

```
/codex-runtime codex_app_server
```

该命令的功能包括：
- 检查是否已安装 `codex` CLI（若未安装则会提示用户进行安装）。
- 将 `model.openai_runtime: codex_app_server` 保存到您的 `config.yaml` 文件中。
- 将用户的 MCP 服务器从 `~/.hermes/config.yaml` 迁移至 `~/.codex/config.toml`。
- 通过调用 Codex 的 `plugin/list` RPC，**识别并迁移已安装的原生 Codex 插件**（如 Linear、GitHub、Gmail、日历、Canva 等）。
- **将 Hermes 自带的工具注册为 MCP 服务器**，以便 Codex 子进程能够调用这些其本身不提供的工具。
- 设置 `default_permissions = ":workspace"`，从而使沙箱环境允许在工作区内进行写入操作，无需每次操作都再次确认。
- 显示已完成的迁移内容。相关更改将在**下一个会话**中生效——当前缓存的智能体仍会保留之前的运行时配置，因此提示词缓存依然有效。

同义命令：`/codex-runtime on`、`/codex-runtime off`、`/codex-runtime auto`。

如需查看当前状态而不做任何更改：
```
/codex-runtime
```

您也可以在 `~/.hermes/config.yaml` 中手动进行设置：
```yaml
model:
  openai_runtime: codex_app_server   # default is "auto" (= Hermes runtime)
```

## 自我提升循环（记忆与技能提示）

Hermes 的后台自我提升机制会在达到特定阈值时触发：

- 每收到 10 条用户提示 → 一个独立的审查代理会查看对话内容，判断是否有内容需要保存到记忆中。
- 在单次轮次内每使用工具 10 次 → 规则相同，但适用于技能层面（由 `skill_manage` 负责处理）。

**这两种机制都会在 Codex 运行时中持续运行。** Codex 的处理流程会将每一个完成的 `commandExecution`、`fileChange`、`mcpToolCall` 或 `dynamicToolCall` 操作转换为格式统一的 `assistant tool_call` 与工具响应消息，因此当审查代理运行时，看到的数据结构与默认 Hermes 运行时中的完全一致。

两者保持功能等价的机制如下：

| | 默认运行时 | Codex 运行时 |
|---|---|---|
| `_turns_since_memory` 的递增逻辑 | 在 `run_conversation` 函数的预循环阶段，每次收到用户提示时递增 | 代码路径相同，在提前返回之前递增 |
| `_iters_since_skill` 的递增逻辑 | 在聊天补全循环中，每次使用工具时递增 | 在 Codex 轮次结束之后，根据 `turn.tool_iterations` 递增 |
| 记忆触发条件（`_turns_since_memory >= _memory_nudge_interval`） | 在预循环阶段计算，于响应生成后触发 | 在预循环阶段计算，随后传递给 Codex 辅助函数 |
| 技能触发条件（`_iters_since_skill >= _skill_nudge_interval`） | 在循环结束后计算 | 在 Codex 轮次处理完成后计算 |
| `_spawn_background_review(messages_snapshot=..., review_memory=..., review_skills=...)` 的调用时机 | 任一触发条件满足时都会调用 | 任一触发条件满足时，调用方式完全相同 |

需要注意的一点是：负责审查的子进程本身需要调用 Hermes 的代理循环工具（如 `memory`、`skill_manage`），而这些工具依赖 Hermes 自身的调度机制。因此，当主代理运行在 `codex_app_server` 上时，审查子进程会被**降级为使用 `codex_responses` 模式**——虽然 OAuth 凭证和 `openai-codex` 提供商保持不变，但它会直接与 OpenAI 的 Responses API 进行通信，从而由 Hermes 来掌控整个循环流程，确保代理循环工具能够正常工作。这一过程对用户来说是完全透明的。

最终效果是：启用 Codex 运行时后，你的记忆与技能提示功能仍会像以往一样正常触发。

## 审批机制的工作原理

Codex 在执行命令或应用补丁之前会先请求审批。这些审批请求会被转换为 Hermes 标准的“危险命令”提示框：

```
╭───────────────────────────────────────╮
│ Dangerous Command                     │
│                                       │
│ /bin/bash -lc 'echo hello > foo.txt'  │
│                                       │
│ ❯ 1. Allow once                       │
│   2. Allow for this session           │
│   3. Deny                             │
│                                       │
│ Codex requests exec in /your/cwd      │
╰───────────────────────────────────────╯
```

- **允许一次** → 仅批准本次命令。
- **允许当前会话** → Codex 不会再次提示类似命令。
- **拒绝** → 命令被驳回；Codex 将继续以只读模式运行。

对于 `apply_patch`（文件编辑）的审批操作，当 Codex 通过相应的 `fileChange` 项提供相关数据时，Hermes 会显示更改摘要（例如“1 个新增，1 个更新：/tmp/new.py, /tmp/old.py”）。

## 权限配置文件

Codex 提供三种内置权限配置文件：
- `:read-only` — 禁止写入；所有 shell 命令均需审批
- `:workspace` — 允许在当前工作区内进行写入操作且无需提示（启用运行时后的默认设置）
- `:danger-no-sandbox` — 完全不使用沙箱环境（除非您完全了解其风险，否则请勿使用）

您可以在 Hermes 管理块之外的 `~/.codex/config.toml` 文件中覆盖这些默认设置：

```toml
default_permissions = ":read-only"
```

（只要您的自定义设置位于 `# managed by hermes-agent` 标记之外，Hermes在重新迁移时仍会保留这些设置。）

## 辅助任务与ChatGPT订阅费用

当使用 `openai-codex` 提供商且该运行时处于开启状态时，**辅助任务（标题生成、上下文压缩、视觉内容自动检测以及后台自我优化审查功能）默认也会通过您的ChatGPT订阅账户来调用**，因为在没有为特定任务设置自定义选项时，Hermes的辅助客户端会使用主提供商/模型。

这种情况并非仅限于 `codex_app_server`，现有的 `codex_responses` 路径也是如此——只是在这里更为明显，因为您是明确选择了按订阅计费的方式。

若希望将特定的辅助任务路由到成本更低或不同的模型，请在 `~/.hermes/config.yaml` 中设置明确的自定义选项：

```yaml
auxiliary:
  title_generation:
    provider: openrouter
    model: google/gemini-3-flash-preview
  compression:
    provider: openrouter
    model: google/gemini-3-flash-preview
  vision:
    provider: openrouter
    model: google/gemini-3-flash-preview
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

自我提升评估分支通过 `_current_main_runtime()` 继承主运行时环境，Hermes 会自动将其从 `codex_app_server` 下降级为 `codex_responses`（这样该分支就能调用 `memory` 和 `skill_manage` —— 这些都是 Hermes 自带的智能体循环工具）。除非您已将辅助任务路由到其他地方，否则该分支仍会使用您的订阅授权进行身份验证。

## 安全地编辑 `~/.codex/config.toml` 文件

Hermes 会将所有需要管理的内容封装在两条标记注释之间：

```toml
# managed by hermes-agent — `hermes codex-runtime migrate` regenerates this section
default_permissions = ":workspace"
[mcp_servers.filesystem]
...
[plugins."github@openai-curated"]
...
# end hermes-agent managed section
```

该管理块**之外的所有内容**均归您所有。通过 `/codex-runtime codex_app_server` 命令或在任何时候重新启动运行时，都会替换掉该管理块，但会原封不动地保留其上下方的用户内容。这意味着您可以：

- 添加 Hermes 未知的自有 MCP 服务器
- 若希望每次操作都收到确认提示，可将 `default_permissions` 设置为 `:read-only`
- 配置仅适用于 Codex 的选项（模型、提供程序、otel 等）
- 在 `[permissions.<name>]` 表中添加用户自定义的权限配置文件

而在管理块**内部**添加的任何内容都将在下一次迁移时被清除。如果您需要通过修改管理块来实现某些功能，可以提交问题报告，我们会为您添加相应的配置选项。

## 多配置文件/多租户设置

默认情况下，无论当前使用的是哪个 Hermes 配置文件，Hermes 都会将 Codex 子进程指向 `~/.codex/` 目录。这意味着 `hermes -p work` 和 `hermes -p personal` 会共享相同的 Codex 认证信息、插件及配置。对大多数用户而言，这种行为是合理的——它与直接运行 `codex` CLI 的效果一致。

如果您希望为每个配置文件实现独立的 Codex 环境（独立的认证、独立的已安装插件、独立的配置），则需要为每个配置文件明确设置 `CODEX_HOME`。最简单的方法是指向 `HERMES_HOME` 目录下的某个子目录：

```bash
# Inside the work profile, you might wrap hermes:
CODEX_HOME=~/.hermes/profiles/work/codex hermes chat
```

你需要在该环境变量 `CODEX_HOME` 设置好之后，重新运行一次 `codex login`，这样 OAuth 令牌就会被存储到与用户配置相关的位置。之后，执行 `hermes -p work` 命令时就会在隔离的 Codex 状态下运行。

我们并未自动进行这种配置调整，因为如果移动现有用户的 `~/.codex/` 目录，其 Codex CLI 认证将会悄无声息地失效——所有已经执行过 `codex login` 的用户都将需要重新认证。主动征得用户同意比让用户措手不及更为安全。

## HOME 环境变量传递机制

Hermes 在启动 codex 应用服务器子进程时不会重写 `HOME` 变量（我们使用 `os.environ.copy()` 方法，仅覆盖 `CODEX_HOME` 和 `RUST_LOG` 这两个变量）。这意味着：

- 通过 `shell` 工具运行的命令能够看到真实的用户 `HOME` 路径，从而正确找到 `~/.gitconfig`、`~/.gh/`、`~/.aws/`、`~/.npmrc` 等配置文件。
- 由于 `CODEX_HOME`（默认指向 `~/.codex/`）的存在，Codex 的内部状态依然保持隔离。

这一设计与 OpenClaw 经过早期测试后确定的方案一致：隔离 Codex 的状态，不对用户的个人目录进行干预。（参见 openclaw/openclaw#81562）

## MCP 服务器迁移

Hermes 的 `mcp_servers` 配置会自动转换为 Codex 所期望的 TOML 格式。每次启用运行时都会执行此迁移操作，且该过程是可重复执行的——重新运行只会替换已管理的配置部分，而不会丢失用户手动编辑过的 Codex 配置。

以下是转换规则：

| Hermes (`config.yaml`) | Codex (`config.toml`) |
|---|---|
| `command` + `args` + `env` | stdio 传输协议 |
| `url` + `headers` | streamable_http 传输协议 |
| `timeout` | `tool_timeout_sec` |
| `connect_timeout` | `startup_timeout_sec` |
| `enabled: false` | `enabled = false` |

以下内容不会被迁移：
- Hermes 特有的配置项，如 `sampling`（Codex 的 MCP 客户端没有对应的功能——这些项会被移除，并会给出针对该服务器的警告）。

## 原生 Codex 插件迁移

通过 `codex plugin` 命令安装的插件（如 Linear、GitHub、Gmail、Calendar、Canva 等），会通过 Codex 的 `plugin/list` RPC 接口被识别。对于那些 `installed: true` 的插件，Hermes 会在你的 Hermes 会话中添加一个 `[plugins."<name>@openai-curated"]` 块来启用它们。

这意味着：当你的朋友说“我在我的 Codex CLI 中已经配置了 Calendar 和 GitHub”，然后他们启用了 Hermes 的 codex 运行时，Hermes 会自动激活这些插件，无需重新配置。

以下内容不会被迁移：
- 尚未安装的插件——请先在 Codex 中进行安装。
- Codex 显示 `availability != AVAILABLE` 状态的插件（如安装失败、OAuth 令牌过期、已从市场下架等）。为避免生成后续激活时会出错的配置，这类插件会被跳过。
- ChatGPT 应用市场中的插件（即通过账户认证后可在 `app/list` 中查看的插件——这些插件因账户认证的原因已自动在 Codex 中启用）。
- 插件的 OAuth 配置——你需要在 Codex 内部为每个插件单独授权一次；Hermes 不会处理相关凭证。

## Hermes 工具回调机制（新的 MCP 服务器）

Codex 自带的工具集虽然支持 shell 操作、文件操作和代码补全等功能，但缺乏网页搜索、浏览器自动化、视觉处理、图像生成等能力。为让这些功能也能在 codex 会话中使用，Hermes 会在 `~/.codex/config.toml` 中将自己注册为 MCP 服务器：

```toml
[mcp_servers.hermes-tools]
command = "/path/to/python"
args = ["-m", "agent.transports.hermes_tools_mcp_server"]
env = { HERMES_HOME = "/your/.hermes", PYTHONPATH = "...", HERMES_QUIET = "1" }
startup_timeout_sec = 30.0
tool_timeout_sec = 600.0
```

当模型调用 `web_search`（或其他已公开的 Hermes 工具）时，Codex 会通过标准输入输出启动 `hermes_tools_mcp_server` 子进程，请求会经由 `model_tools.handle_function_call()` 进行处理，最终结果会像其他 MCP 响应一样返回给 Codex。

**可通过回调使用的工具：** `web_search`、`web_extract`、`browser_navigate`、`browser_click`、`browser_type`、`browser_press`、`browser_snapshot`、`browser_scroll`、`browser_back`、`browser_get_images`、`browser_console`、`browser_vision`、`vision_analyze`、`image_generate`、`skill_view`、`skills_list`、`text_to_speech`。

**不可用的工具：** `delegate_task`、`memory`、`session_search`、`todo`。这些工具需要运行中的 AIAgent 上下文才能被触发（处于循环中间状态），而无状态的 MCP 回调无法驱动它们。如需使用这些工具，请启用默认的 Hermes 运行时（`/codex-runtime auto`）。

## 禁用功能

可随时重新开启：

```
/codex-runtime auto
```

该功能将在下次会话中生效。由 Codex 管理的配置块会保存在 `~/.codex/config.toml` 中，因此您日后可以重新启用而不会丢失配置——当然，如果您愿意，也可以手动将其删除。

## 局限性

此运行时处于**可选测试版**状态。目前已在 Hermes Agent 2026.5 + Codex CLI 0.130.0 上验证可用，支持以下功能：

- 多轮对话
- 通过 Hermes UI 对 `commandExecution` 和 `fileChange`（apply_patch）操作进行审批
- MCP 工具调用（已针对 `@modelcontextprotocol/server-filesystem` 及新的 `hermes-tools` 回调函数进行验证）
- 原生 Codex 插件迁移（已针对 Linear、GitHub 和 Calendar 目录进行验证）
- 拒绝/取消操作路径
- 开启/关闭切换功能
- 内存使用量和技能调用次数计数器（通过集成测试实时验证）
- 通过 Codex 实现 Hermes 的网页搜索功能（已实际验证：“OpenAI Codex CLI – Getting Started” 查询可完整执行）

已知局限性包括：

- **Hermes 认证与 Codex 认证属于独立的会话。** 为获得最佳用户体验，您需要同时执行 `codex login` 和 `hermes auth add openai-codex` 操作（该运行时在调用大型语言模型时会使用 Codex 的会话）。这是 Hermes 中 `_import_codex_cli_tokens` 函数的刻意设计——Hermes 不会与 Codex CLI 共享 OAuth 状态，以避免在令牌刷新时导致数据冲突）。
- **在此运行时中无法使用 `delegate_task`、`memory`、`session_search` 和 `todo` 功能。** 这些功能需要正在运行的 AIAgent 上下文，而无状态的 MCP 回调函数无法提供此类上下文。如需使用这些功能，请使用 `/codex-runtime auto` 命令。
- **当 Codex 未跟踪变更集时，审批提示中不会显示内联补丁预览。** Codex 的 `fileChange` 审批参数并不总是包含变更集信息。Hermes 会在可能的情况下缓存来自相应 `item/started` 通知的数据，但如果在相关数据尚未完全传输时就收到审批请求，提示内容将退化为 Codex 提供的任意 `reason` 信息。
- **无法保证在亚秒级时间内完成取消操作。** 在处理过程中中断（例如在 Codex 正在响应时按下 Ctrl+C）会通过 `turn/interrupt` 机制传递，但如果 Codex 已经发送了最终消息，您仍会收到该响应。

如果您发现漏洞，请附上 `hermes logs --since 5m` 的输出结果，[提交问题](https://github.com/NousResearch/hermes-agent/issues)。在标题中注明 `codex-runtime`，以便于问题分类处理。

## 架构

```
                ┌─── Hermes shell (CLI / TUI / gateway) ───┐
                │  sessions DB · slash commands · memory   │
                │  & skill review · cron · session pickers │
                └──┬──────────────────────────────────────┬┘
                   │ user_message               final     │
                   ▼                            text +    │
        ┌──────────────────────────────────┐   projected  │
        │  AIAgent.run_conversation()       │   messages   │
        │   if api_mode == codex_app_server │              │
        │     → CodexAppServerSession       │              │
        │   else: chat_completions / codex_responses (default)
        └────┬─────────────────────────────┘              │
             │ JSON-RPC over stdio                        │
             ▼                                            │
        ┌──────────────────────────────────┐              │
        │  codex app-server (subprocess)    │──────────────┘
        │   thread/start, turn/start        │
        │   item/* notifications            │
        │   shell + apply_patch + update_plan│
        │   view_image + sandbox            │
        │   ┌─────────────────────────┐     │
        │   │  MCP client             │     │
        │   │  ├─ user MCP servers    │     │
        │   │  ├─ native plugins      │     │
        │   │  │   (linear, github,   │     │
        │   │  │    gmail, calendar,  │     │
        │   │  │    canva, ...)       │     │
        │   │  └─ hermes-tools ───────┼─────────────────┐
        │   │       (callback to     │     │           │
        │   │        Hermes' richer  │     │           │
        │   │        tools)          │     │           │
        │   └─────────────────────────┘     │           │
        └──────────────────────────────────┘           │
                                                        │
                                                        ▼
        ┌──────────────────────────────────────────────────────────┐
        │  hermes_tools_mcp_server.py (subprocess on demand)        │
        │   web_search, web_extract, browser_*, vision_analyze,    │
        │   image_generate, skill_view, skills_list, text_to_speech│
        └──────────────────────────────────────────────────────────┘
```

如需了解实现细节，请参阅[PR #24182](https://github.com/NousResearch/hermes-agent/pull/24182)以及[Codex应用服务器协议说明文档](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)。
