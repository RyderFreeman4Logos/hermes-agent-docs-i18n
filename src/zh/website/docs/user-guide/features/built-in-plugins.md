---
sidebar_position: 12
sidebar_label: "Built-in Plugins"
title: "Built-in Plugins"
description: "Plugins shipped with Hermes Agent that run automatically via lifecycle hooks — disk-cleanup and friends"
---

# 内置插件

Hermes 在代码仓库中预置了一小部分插件。这些插件位于 `<repo>/plugins/<name>/` 目录下，会与用户安装在 `~/.hermes/plugins/` 中的插件一同自动加载。它们使用与第三方插件相同的接口机制——包括钩子、工具以及斜杠命令——只不过这些插件是直接内置在代码中的。

如需了解插件系统的整体架构，请参阅 [插件](/user-guide/features/plugins) 页面；若想自行编写插件，则可参考 [构建 Hermes 插件](/guides/build-a-hermes-plugin) 文档。

## 插件发现机制

`PluginManager` 会按顺序扫描四个来源：

1. **内置插件** — `<repo>/plugins/<name>/`（即本页所介绍的内容）
2. **用户插件** — `~/.hermes/plugins/<name>/`
3. **项目级插件** — `./.hermes/plugins/<name>/`（需设置 `HERMES_ENABLE_PROJECT_PLUGINS=1`）
4. **Pip 插件入口** — `hermes_agent.plugins`

当出现同名插件时，后续扫描到的插件会覆盖之前的版本——例如，名为 `disk-cleanup` 的用户插件将取代内置的同类插件。

`plugins/memory/` 和 `plugins/context_engine/` 目录会被刻意排除在内置插件扫描范围之外。因为内存提供器和上下文引擎属于通过配置文件中的 `hermes memory setup` / `context.engine` 选项进行配置的单选型提供器，因此它们拥有独立的发现路径。

## 内置插件为可选启用状态

内置插件在初始状态下是禁用的。虽然系统能够检测到它们的存在（它们会显示在 `hermes plugins list` 列表以及交互式的 `hermes plugins` 用户界面中），但除非您明确启用它们，否则这些插件不会被加载。

```bash
hermes plugins enable disk-cleanup
```

或者通过 `~/.hermes/config.yaml`：

```yaml
plugins:
  enabled:
    - disk-cleanup
```

这正是用户自行安装的插件所采用的机制。预装插件绝不会自动启用——无论是全新安装时，还是现有用户升级到新版Hermes时，都需要用户明确选择启用。

若要再次关闭某个预装插件：

```bash
hermes plugins disable disk-cleanup
# or: remove it from plugins.enabled in config.yaml
```

## 当前已发布的插件

该仓库将上述插件打包在 `plugins/` 目录下提供。所有插件均为可选功能——可通过 `hermes plugins enable <name>` 命令启用。

| 插件名称 | 类型 | 功能说明 |
|---|---|---|
| `disk-cleanup` | hooks + slash命令 | 自动追踪会话期间生成的临时文件，并在会话结束时自动清理，包括测试脚本、临时输出、cron日志以及过期的Chrome配置文件等——无需让智能体主动调用相应工具。 |
| `security-guidance` | hooks | 对 `write_file`/`patch` 操作中的危险代码进行模式匹配，随后添加安全警告（或直接阻止操作）——共包含25条规则（基于Anthropic的`claude-plugins-official`规则集的Apache-2.0版本）。 |
| `observability/langfuse` | hooks | 将对话轮次、LLM调用及工具使用情况追踪并上传至[Langfuse](https://langfuse.com)。 |
| `observability/nemo_relay` | hooks | 将各类可观测性事件（对话轮次、LLM调用、工具使用记录等）转发至NVIDIA NeMo平台。 |
| `teams_pipeline` | 独立插件 | 用于Microsoft Teams会议的流程处理功能——基于图结构存储数据，优先生成会议文字记录。 |
| `spotify` | 后端插件（含7个工具） | 支持Spotify的播放、队列管理、搜索、播放列表操作以及专辑和音乐库管理等功能。 |
| `google_meet` | 独立插件 | 可用于加入Google Meet会议，提供实时字幕转录功能，还可选择开启实时双向音频传输。 |
| `image_gen/openai` | 图像生成后端 | 基于OpenAI的`gpt-image-2`技术实现的图像生成后端（可作为FAL的替代方案）。 |
| `image_gen/openai-codex` | 图像生成后端 | 通过Codex OAuth机制实现OpenAI图像生成功能。 |
| `image_gen/xai` | 图像生成后端 | 基于xAI的`grok-2-image`技术实现的图像生成后端。 |
| `hermes-achievements` | 仪表板标签页 | 根据用户的实际Hermes会话历史记录，生成类似Steam风格的收藏徽章。 |
| `kanban/dashboard` | 仪表板标签页 | 为多智能体调度系统提供的看板式用户界面——支持任务管理、评论功能、任务分发以及看板切换等功能。详情请参阅[Kanban多智能体功能](./kanban.md)。 |

内存提供插件（`plugins/memory/*`）和上下文引擎插件（`plugins/context_engine/*`）会在[内存提供插件文档](./memory-providers.md)中单独列出——它们分别通过 `hermes memory` 和 `hermes plugins` 命令进行管理。下面将详细介绍这两个基于hooks的长期运行插件的具体功能。

### disk-cleanup插件

该插件会自动追踪并删除会话期间生成的临时文件，包括测试脚本、临时输出、cron日志以及过期的Chrome配置文件等——无需智能体主动记住要调用相应工具来执行清理操作。

**工作原理：**

| Hooks钩子 | 行为表现 |
|---|---|
| `post_tool_call` | 当`write_file`/`terminal`/`patch`命令在`HERMES_HOME`或 `/tmp/hermes-*`目录下生成名为`test_*`、`tmp_*`或`*.test.*`的文件时，会将其悄悄标记为`test`、`temp`或`cron-output`类型。 |
| `on_session_end` | 如果在某个对话轮次期间有临时文件被自动标记，该插件会执行简单的快速清理操作，并记录一条简要的总结信息；否则则保持静默。 |

**删除规则：**

| 文件类别 | 删除阈值 | 是否需要确认 |
|---|---|---|
| `test`类文件 | 每次会话结束时 | 不需要 |
| `temp`类文件 | 自标记以来超过7天 | 不需要 |
| `cron-output`类文件 | 自标记以来超过14天 | 不需要 |
| `HERMES_HOME`目录下的空文件夹 | 始终删除 | 不需要 |
| `research`类文件 | 自标记以来超过30天，且保留最近10个文件 | 始终删除（仅深度扫描） |
| `chrome-profile`类文件 | 自标记以来超过14天 | 始终删除（仅深度扫描） |
| 大于500 MB的文件 | 永不自动删除 | 始终删除（仅深度扫描） |

**Slash命令** —— 在CLI会话和网关会话中均可使用 `/disk-cleanup` 命令来调用该功能。

```
/disk-cleanup status                     # breakdown + top-10 largest
/disk-cleanup dry-run                    # preview without deleting
/disk-cleanup quick                      # run safe cleanup now
/disk-cleanup deep                       # quick + list items needing confirmation
/disk-cleanup track <path> <category>    # manual tracking
/disk-cleanup forget <path>              # stop tracking (does not delete)
```

**状态存储**——所有相关数据均保存在 `$HERMES_HOME/disk-cleanup/` 目录下：

| 文件 | 内容 |
|---|---|
| `tracked.json` | 记录被监控路径的类别、大小及时间戳 |
| `tracked.json.bak` | 上述文件的原子写入备份 |
| `cleanup.log` | 记录每次监控、跳过、拒绝或删除操作的只读审计日志 |

**安全性保障**——清理操作仅针对 `HERMES_HOME` 或 `/tmp/hermes-*` 下的路径，不会影响 Windows 挂载路径（如 `/mnt/c/...`）。那些知名的上层状态目录（如 `logs/`、`memories/`、`sessions/`、`cron/`、`cache/`、`skills/` 以及 `disk-cleanup/` 本身），即便为空也不会被删除——这样即使首次会话结束，重新安装后的系统也不会被清空。

**启用方式**：执行 `hermes plugins enable disk-cleanup`（或在 `hermes plugins` 界面中勾选对应选项）。

**再次禁用方式**：执行 `hermes plugins disable disk-cleanup`。

### 安全指导功能

该插件可在文件写入时快速进行模式匹配，从而发出安全警告。当智能体的 `write_file`、`patch` 或 `skill_manage` 函数所处理的内容匹配到已知危险的代码模式时——例如 `pickle.load`、未使用 `SafeLoader` 的 `yaml.load`、`eval(`、`os.system`、`subprocess(..., shell=True)`、JavaScript 中的 `child_process.exec`、React 的 `dangerouslySetInnerHTML`、直接的 `.innerHTML =`/`.outerHTML =`/`document.write`、Node.js 中的 `crypto.createCipher`、AES ECB 模式、禁用 TLS 验证、易受 XXE 攻击的 `xml.etree`/`minidom` 解析器、缺少 SRI 标签的 `<script src="//..." >`、未设置 `weights_only=True` 的 `torch.load`，以及 GitHub Actions 中的 `${{ github.event.* }}` 注入攻击——插件会在该工具的输出中添加一个 `⚠️ 安全指导` 标块。

文件仍会被正常写入。模型会在下一轮的输出中读取到该警告，随后可以选择修正相关代码，或说明为何在当前场景下该操作是安全的。由于模式匹配存在一定的误报率，因此默认采取警告而非直接阻止的方式。

**覆盖范围**：共包含 25 条规则，涵盖不安全的反序列化操作、命令注入、XSS 漏洞、加密漏洞、XXE 攻击、供应链注入（通过 SRI 标签检测）以及 CI/CD 工作流注入风险。这些模式数据是基于 [Anthropic 的 `claude-plugins-official`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance/hooks) 项目按 Apache-2.0 协议修改而来的；具体来源信息请参阅插件中的 `LICENSE` 和 `NOTICE` 文件。

**工作模式**：

| 环境变量 | 效果 |
|---|---|
| 未设置 | **警告模式**（默认）——文件仍会被写入，仅在结果中添加警告 |
| `SECURITY_GUIDANCE_BLOCK=1` | **阻止模式**——拒绝写入操作，并以警告作为拒绝原因返回 |
| `SECURITY_GUIDANCE_DISABLE=1` | 禁用开关——插件虽被加载，但不会执行任何操作 |

**启用方式**：执行 `hermes plugins enable security-guidance`（或在 `hermes plugins` 界面中勾选对应选项）。

**再次禁用方式**：执行 `hermes plugins disable security-guidance`。

**目前未实现的功能**：上游的 Anthropic 插件还包含另外两层安全机制——即对每次修改文件的智能体操作进行大语言模型差异审查，以及在提交代码时追踪文件间的数据流并进行审查。这些功能暂未移植到当前版本中。不过智能体仍可通过 `delegate_task` 功能按需执行这些审查操作。

### 可观测性/Langfuse 集成

该插件会将 Hermes 的各轮处理、大语言模型调用以及工具调用信息上报至 [Langfuse](https://langfuse.com)——这是一个开源的大语言模型可观测性平台。每轮处理生成一个时间跨度记录，每次 API 调用对应一次生成操作，每次工具调用则产生一条工具使用记录。使用量统计、各类 Token 数量以及成本估算均基于 Hermes 的标准 `agent.usage_pricing` 数据，因此 Langfuse 控制台显示的统计项（输入/输出/`cache_read_input_tokens`/`cache_creation_input_tokens`/`reasoning_tokens`）与 `hermes logs` 中的记录一致。

该插件采用“故障即忽略”设计：即使未安装 SDK、缺少认证信息，或出现临时的 Langfuse 错误，钩子函数也会静默无动作地处理，不会影响智能体的正常运行循环。

**设置方式（推荐交互式设置）：**

```bash
hermes tools          # → Langfuse Observability → Cloud or Self-Hosted
```

向导会自动收集您的密钥，通过 `pip install` 安装 `langfuse` SDK，并帮您将 `observability/langfuse` 添加到 `plugins.enabled` 中。重启 Hermes 后，下一个对话轮次就会生成追踪数据。

**手动设置：**

```bash
pip install langfuse
hermes plugins enable observability/langfuse
```

接着将凭证保存到 `~/.hermes/.env` 文件中：

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

**工作原理：**

| Hook | 行为描述 |
|---|---|
| `pre_api_request` / `pre_llm_call` | 打开（或复用）一个按轮次划分的根级跨度“Hermes turn”。针对此次 API 调用启动一个 `generation` 子观察，将近期已序列化的消息作为输入。 |
| `post_api_request` / `post_llm_call` | 结束生成过程，并附加 `usage_details`、`cost_details`、`finish_reason`、助手输出以及工具调用信息。若没有工具调用且内容非空，则结束当前轮次。 |
| `pre_tool_call` | 使用经过过滤处理的 `args` 启动一个 `tool` 子观察。 |
| `post_tool_call` | 使用经过过滤处理的 `result` 结束工具观察。对于 `read_file` 类型的负载，会对其进行摘要处理（包含开头内容、结尾内容及省略行数），以确保大型文件的读取内容长度仍符合 `HERMES_LANGFUSE_MAX_CHARS` 的限制。 |

通过 `langfuse.propagate_attributes`，会将会话分组键从 Hermes 会话 ID（或子智能体的任务 ID）中分离出来，从而使单个 `hermes chat` 会话中的所有内容都归属于同一个 Langfuse 会话之下。

**验证方式：**

```bash
hermes plugins list                 # observability/langfuse should show "enabled"
hermes chat -q "hello"              # check the Langfuse UI for a "Hermes turn" trace
```

**可选配置**（位于 `.env` 文件中）：

| 变量 | 默认值 | 用途 |
|---|---|---|
| `HERMES_LANGFUSE_ENV` | — | 追踪记录的环境标签（如 `production`、`staging` 等） |
| `HERMES_LANGFUSE_RELEASE` | — | 发布版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | `1.0` | 传递给 SDK 的采样率（范围：0.0–1.0） |
| `HERMES_LANGFUSE_MAX_CHARS` | `12000` | 消息内容、工具参数及工具结果的每字段截断长度 |
| `HERMES_LANGFUSE_DEBUG` | `false` | 向 `agent.log` 文件输出详细的插件日志 |

同时支持以 Hermes 前缀命名的环境变量以及标准 SDK 环境变量（如 `LANGFUSE_PUBLIC_KEY`、`LANGFUSE_SECRET_KEY`、`LANGFUSE_BASE_URL`）；若两者均被设置，则以 Hermes 前缀的变量优先生效。

**性能优化：** 在首次触发钩子调用后，Langfuse 客户端会被缓存。如果凭证或 SDK 缺失，这一判断结果也会被缓存，后续调用可快速返回而无需重新检查环境变量或加载配置。

**禁用方式：** 使用命令 `hermes plugins disable observability/langfuse` 进行禁用。此时插件模块仍会被检测到，但在重新启用之前不会执行任何模块代码。

### google_meet

该插件允许智能体**加入、转录并参与 Google Meet 通话**——可为会议做笔记、总结讨论内容、针对特定要点进行跟进，还可通过文本转语音功能（TTS）选择性地将回复语音回放至通话中。

**主要功能包括：**

- 通过浏览器自动化技术，以无界面虚拟参会者身份加入 Meet 会议链接
- 利用配置好的语音转文字服务实时转录会议音频
- 提供 `meet_summarize`、`meet_speak`、`meet_followup` 等工具集，让智能体能够根据所听内容采取相应操作
- 会议结束后，相关输出文件（如转录文本、按发言人分类的笔记、待办事项）会保存在 `~/.hermes/cache/google_meet/<meeting_id>/` 目录下

**设置方式：**

```bash
hermes plugins enable google_meet
# Prompts you to sign in via the plugin's OAuth flow on first use —
# needs a Google account with Meet access. Host approval may be required
# if the meeting enforces "only invited participants can join".
```

**通过聊天使用方式：**

> “加入 meet.google.com/abc-defg-hij 并做会议记录。通话结束后，请将包含行动项的总结发给我。”

该智能体将自动启动会议连接，在通话进行过程中持续将实时转录内容同步到其上下文中，待会议结束（或您要求停止时）自动生成结构化的总结报告。

**适用场景：** 需要机器人为异步参与者进行转录和总结的定期站会；需要结构化记录的访谈类场景；任何原本就需要使用 Fireflies/Otter/Grain 工具的场景。若不希望让 AI 监听会议内容，请勿启用此功能。

**禁用方法：** `hermes plugins disable google_meet`。所有缓存的转录文本和录音文件会保存在 `~/.hermes/cache/google_meet/` 目录中，直到您手动删除它们为止。

### hermes-achievements

该插件为控制面板添加了**类似 Steam 的成就栏**——根据您的实际 Hermes 会话历史记录，生成 60 多个可收集的阶梯式徽章。这些徽章涵盖工具链使用技巧、调试模式、编码连续时长、技能/内存使用情况、模型/提供方种类，以及生活习惯（如周末或夜间编程等）。该插件最初由 [@PCinkusz](https://github.com/PCinkusz) 作为外部插件开发，后来被整合进 Hermes 内部，以便与 Hermes 的功能更新保持同步。

**工作原理：**

- 在控制面板后台扫描您所有的 `~/.hermes/state.db` 会话历史记录
- 每个会话的统计数据会通过 `(started_at, last_active)` 编码进行缓存，因此后续扫描时仅会对新会话或已变更的会话重新分析
- 首次扫描在后台线程中执行——即便数据库中存储了数千个会话，控制面板也不会因等待扫描而卡住
- 解锁状态会被保存到 `$HERMES_HOME/plugins/hermes-achievements/state.json` 文件中

**等级晋升路径：** 铜级 → 银级 → 金级 → 钻石级 → 奥运级。每张徽章卡片都会显示“统计指标”部分，明确列出所追踪的具体数据。

**成就状态：**

| 状态 | 含义 |
|---|---|
| 已解锁 | 已达到至少一个等级 |
| 已发现 | 该成就存在，进度可见，但尚未获得 |
| 秘密 | 在 Hermes 检测到会话历史中的相关信号之前保持隐藏状态 |

**API 接口**——接口路径为 `/api/plugins/hermes-achievements/`：

| 接口地址 | 功能 |
|---|---|
| `GET /achievements` | 显示完整的徽章目录及每个徽章的解锁状态（在首次完整扫描进行时，会返回占位符信息） |
| `GET /scan-status` | 查询后台扫描器的状态：`idle`/`running`/`failed`，以及上次扫描时长和运行次数 |
| `GET /recent-unlocks` | 显示最近解锁的 20 个徽章，最新解锁的排在最前 |
| `GET /sessions/{id}/badges` | 查看在某个特定会话中获得的徽章 |
| `POST /rescan` | 手动触发同步重新扫描（会阻塞当前操作；适用于用户点击重新扫描按钮时） |
| `POST /reset-state` | 清除解锁历史记录及缓存快照 |

**状态文件**——存储在 `$HERMES_HOME/plugins/hermes-achievements/` 目录下：

| 文件名 | 内容 |
|---|---|
| `state.json` | 解锁历史记录：记录您已获得的徽章及其获得时间。此数据在 Hermes 更新后依然保持稳定 |
| `scan_snapshot.json` | 上次完成扫描的完整数据（控制面板加载时会立即使用该数据） |
| `scan_checkpoint.json` | 按会话编码缓存的每会话统计数据（便于快速进行快速重新扫描） |

**性能说明：**

- 对约 8,000 个会话进行首次完整扫描需要几分钟时间。该扫描在控制面板首次请求时就在后台线程中执行；界面会显示占位符，并持续查询 `/scan-status` 状态
- **首次扫描期间也会逐步显示结果**——扫描器每隔约 250 个会话就会发布一次部分快照，因此每次刷新控制面板时，都能看到更多徽章被解锁，无需长时间盯着零值等待
- 快速重新扫描会复用那些 `started_at` + `last_active` 编码与之前检查点匹配的会话的统计数据——即便会话历史记录非常庞大，也能在几秒钟内完成扫描
- 内存中的快照有效期为 120 秒；过期的请求会立即返回旧快照，并触发后台刷新。因此不必因为快照过期而长时间等待

**启用方式：** 无需额外操作——`hermes-achievements` 是仅用于控制面板的插件（没有生命周期钩子，也不提供模型相关工具）。首次启动时，它会自动作为标签页添加到 `hermes dashboard` 中。`plugins.enabled` 配置项仅用于控制生命周期/工具类插件；控制面板插件则是通过其 `dashboard/manifest.json` 文件被自动识别的

**选择不使用的方式：** 删除或重命名 `plugins/hermes-achievements/dashboard/manifest.json`，或者在 `~/.hermes/plugins/hermes-achievements/` 目录下创建一个同名的用户插件，且该插件不包含控制面板功能。此时 `$HERMES_HOME/plugins/hermes-achievements/` 下的插件状态文件仍会保留——重新安装插件后，您的解锁历史记录不会丢失

## 添加打包插件

打包插件的编写方式与其他 Hermes 插件完全相同——请参考[构建 Hermes 插件](/guides/build-a-hermes-plugin)文档。唯一的不同在于：

- 插件目录位于 `<repo>/plugins/<name>/`，而非 `~/.hermes/plugins/<name>/`
- 在 `hermes plugins list` 中，其插件类型会被标记为 `bundled`
- 同名的用户插件会覆盖打包版本

以下情况适合将插件打包：

- 该插件没有可选依赖项（或所有依赖项都已通过 `pip install .[all]` 一次性安装）
- 其功能对大多数用户都有益，且采用“不启用则放弃”而非“选择启用”的模式
- 其逻辑与某些生命周期钩子相关，否则智能体就需要手动记得调用这些钩子
- 该插件能够补充核心功能，而不会增加模型可见的工具种类

反例——这类插件应保持为用户可安装的独立插件，而非打包版本：需要 API 密钥的第三方集成、特定领域的专用工作流、依赖关系复杂的插件，以及任何会默认显著改变智能体行为的插件。
