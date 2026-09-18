---
sidebar_position: 12
sidebar_label: "Built-in Plugins"
title: "Built-in Plugins"
description: "Plugins shipped with Hermes Agent that run automatically via lifecycle hooks — disk-cleanup and friends"
---

# 内置插件

Hermes 在代码仓库中预置了一小部分插件。这些插件位于 `<repo>/plugins/<name>/` 目录下，会与用户安装在 `~/.hermes/plugins/` 中的插件一同自动加载。它们使用与第三方插件相同的接口机制——包括钩子、工具以及斜杠命令——只不过这些插件是直接内置在代码库中的。

如需了解插件系统的整体架构，请参阅 [插件](/user-guide/features/plugins) 页面；若想自行编写插件，则可参考 [构建 Hermes 插件](/developer-guide/plugins) 文档。

## 插件发现机制

`PluginManager` 会按顺序扫描四个来源：

1. **内置插件** — `<repo>/plugins/<name>/`（即本页面所介绍的内容）
2. **用户插件** — `~/.hermes/plugins/<name>/`
3. **项目插件** — `./.hermes/plugins/<name>/`（需设置 `HERMES_ENABLE_PROJECT_PLUGINS=1`）
4. **Pip 插件入口** — `hermes_agent.plugins`

当出现同名插件时，后续扫描到的插件会覆盖之前的版本——例如，名为 `disk-cleanup` 的用户插件将会替换内置的同类插件。

`plugins/memory/` 和 `plugins/context_engine/` 目录被刻意排除在内置插件扫描范围之外。因为内存提供器和上下文引擎属于通过配置文件中的 `hermes memory setup` / `context.engine` 选项进行单选配置的特殊提供器，因此它们拥有独立的发现路径。

## 内置插件为可选启用状态

内置插件在初始状态下是禁用的。虽然系统能够检测到它们的存在（它们会显示在 `hermes plugins list` 列表以及交互式的 `hermes plugins` 用户界面中），但除非你明确启用它们，否则这些插件不会被加载。

```bash
hermes plugins enable disk-cleanup
```

或者通过 `~/.hermes/config.yaml` 实现：

```yaml
plugins:
  enabled:
    - disk-cleanup
```

这与用户自行安装的插件所采用的机制相同。预装插件绝不会自动启用——无论是新安装时，还是现有用户升级到更高版本的Hermes时，都需手动选择启用。

如需再次关闭某个预装插件：

```bash
hermes plugins disable disk-cleanup
# or: remove it from plugins.enabled in config.yaml
```

## 当前已发布的版本

该仓库将上述插件打包在 `plugins/` 目录下提供。所有插件均为可选功能——可通过 `hermes plugins enable <name>` 命令进行启用。

| 插件名称 | 类型 | 功能说明 |
|---|---|---|
| `disk-cleanup` | hooks + slash command | 自动追踪临时文件，并在会话结束时自动清理它们 |
| `security-guidance` | hooks | 对 `write_file`/`patch` 操作中的危险代码进行模式匹配，随后附加安全警告（或直接阻止操作）——包含25条规则（基于Anthropic的 `claude-plugins-official` 模式开发的Apache-2.0版本） |
| `observability/langfuse` | hooks | 将对话转向、大语言模型调用及工具使用情况追踪至 [Langfuse](https://langfuse.com) 平台 |
| `teams_pipeline` | 独立插件 | 用于Microsoft Teams会议的流程处理工具——基于图数据库架构，可生成以文字记录为主的会议总结 |
| `spotify` | 后端插件（含7个工具） | 支持Spotify的原生播放、队列管理、搜索、播放列表、专辑及资料库操作 |
| `google_meet` | 独立插件 | 可加入Google Meet视频会议，提供实时字幕转录功能，可选支持实时双向音频传输 |
| `image_gen/openai` | 图像处理后端 | 基于OpenAI GPT Image 2及2.5 Flare/Sunburst技术实现图像生成与编辑（需API密钥） |
| `image_gen/openai-codex` | 图像处理后端 | 通过Codex OAuth接口实现OpenAI图像生成功能 |
| `image_gen/xai` | 图像处理后端 | 基于xAI的 `grok-2-image`技术作为图像处理后端 |
| `hermes-achievements` | 仪表板标签页 | 根据用户的实际Hermes会话历史记录，生成类似Steam平台的收藏徽章 |
| `kanban/dashboard` | 仪表板标签页 | 为多智能体调度器提供的看板式用户界面——支持任务管理、评论功能、任务分发以及看板切换。详情请参阅 [Kanban多智能体功能](./kanban.md)。 |
内存提供器（`plugins/memory/*`）与上下文引擎（`plugins/context_engine/*`）会在[内存提供器文档](./memory-providers.md)中分别列出——它们分别通过`hermes memory`和`hermes plugins`进行管理。以下是这两个基于钩子的长期运行插件的详细信息。

### disk-cleanup

该功能会自动追踪并删除会话期间生成的临时文件——如测试脚本、临时输出、cron日志以及过期的Chrome配置文件——而无需让Agent主动调用相关工具。

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `post_tool_call` | 当`write_file`/`terminal`/`patch`在`HERMES_HOME`或 `/tmp/hermes-*`目录下创建名为`test_*`、`tmp_*`或`*.test.*`的文件时，会将其默默标记为`test`/`temp`/`cron-output`类型。 |
| `on_session_end` | 如果在当前会话中有任何测试文件被自动追踪到，就会执行安全的快速清理操作，并记录一条汇总信息；否则保持静默。 |

**删除规则：**

| 类型 | 时间阈值 | 是否需要确认 |
|---|---|---|
| `test` | 每次会话结束 | 不需要 |
| `temp` | 被追踪后超过7天 | 不需要 |
| `cron-output` | 被追踪后超过14天 | 不需要 |
| `HERMES_HOME`下的空目录 | 始终删除 | 不需要 |
| `research` | 超过30天，且保留最近10个文件 | 始终删除（仅深度扫描） |
| `chrome-profile` | 被追踪后超过14天 | 始终删除（仅深度扫描） |
| 大于500 MB的文件 | 永不自动删除 | 始终删除（仅深度扫描） |

**命令格式**——在CLI和网关会话中均可使用命令 `/disk-cleanup`：

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
| `tracked.json` | 记录被监控的路径信息，包含路径类别、大小及时间戳 |
| `tracked.json.bak` | 上述文件的原子写备份文件 |
| `cleanup.log` | 仅支持追加操作的审计日志，记录每一次“监控”、“跳过”、“拒绝”或“删除”操作 |

**安全性保障**——清理操作仅会针对 `HERMES_HOME` 或 `/tmp/hermes-*` 下的路径进行，不会影响 Windows 挂载的路径（如 `/mnt/c/...`）。那些常见的顶级状态目录（如 `logs/`、`memories/`、`sessions/`、`cron/`、`cache/`、`skills/` 以及 `disk-cleanup/` 本身），即便为空也不会被删除——这样即使首次会话结束，重新安装后这些数据也不会丢失。

**启用方式**：执行 `hermes plugins enable disk-cleanup`（或是在 `hermes plugins` 界面中勾选对应选项）。

**再次禁用方式**：执行 `hermes plugins disable disk-cleanup`。

### 安全指南

在文件写入时，系统能快速通过模式匹配识别出安全风险。当代理的 `write_file`、`patch` 或 `skill_manage` 函数调用的内容符合已知的危险代码模式时——例如 `pickle.load`、未使用 `SafeLoader` 的 `yaml.load`、`eval()`、`os.system`、`subprocess(..., shell=True)`、JavaScript 中的 `child_process.exec`、React 的 `dangerouslySetInnerHTML`、直接使用 `.innerHTML =`/`.outerHTML =`/`document.write`、Node.js 中的 `crypto.createCipher`、AES ECB 模式、禁用 TLS 验证、易受 XXE 攻击的 `xml.etree`/`minidom` 解析器、缺少 SRI 标签的 `<script src="//..." >`、未设置 `weights_only=True` 的 `torch.load`，以及 GitHub Actions 中的 `${{ github.event.* }}` 注入攻击——该插件会在工具的输出结果中添加一个 `⚠️ 安全指南` 区块。

文件仍会被写入。模型会在下一轮的工具响应中读取该警告，随后可以修复相关代码，或说明为何在该场景下该操作是安全的。由于模式匹配存在一定的误报率，因此默认采取警告而非直接阻止的处理方式。

**覆盖范围：** 共包含 25 条规则，涵盖不安全的反序列化操作、命令注入、XSS 漏洞、加密缺陷、XXE 攻击、供应链安全（SRI）以及 CI/CD 工作流注入风险。这些模式数据是基于 [Anthropic 的 `claude-plugins-official`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance/hooks) 所做的 Apache-2.0 协议下的完整复制——相关归属信息请参阅插件的 `LICENSE` 和 `NOTICE` 文件。

**模式类型：**

| 环境变量 | 效果 |
|---|---|
| （未设置） | **警告模式**（默认值）——文件仍会被写入，结果中会附加警告信息 |
| `SECURITY_GUIDANCE_BLOCK=1` | **阻止模式**——拒绝写入操作，并返回警告作为阻止原因 |
| `SECURITY_GUIDANCE_DISABLE=1` | 禁用开关——插件虽会加载，但不会执行任何功能 |

**启用方式：** `hermes plugins enable security-guidance`（或是在 `hermes plugins` 中勾选对应选项）。

**再次禁用方式：** `hermes plugins disable security-guidance`。

**目前尚未实现的功能：** 上游的 Anthropic 插件还包含另外两层审核机制——针对每次修改文件的智能体操作进行 LLM 差异审查，以及基于提交时间的智能体审查，用于追踪文件间的数据流向。这两项功能暂未移植到当前版本中。不过智能体已可通过 `delegate_task` 功能按需执行这些审查操作。

### 可观测性/Langfuse

该插件会将 Hermes 的智能体操作、LLM 调用以及工具调用记录到 [Langfuse](https://langfuse.com)——一个开源的 LLM 可观测性平台。每个智能体操作对应一个时间跨度，每次 API 调用对应一次生成操作，每次工具调用则对应一条工具使用记录。使用总量、各类 Token 的计数以及成本估算均源自 Hermes 的标准 `agent.usage_pricing` 数据，因此 Langfuse 仪表板显示的统计信息（输入/输出/cache_read_input_tokens/cache_creation_input_tokens/reasoning_tokens）与 `hermes logs` 中的内容完全一致。

该插件采用“故障自动容错”设计：无论是因为未安装 SDK、缺少凭证，还是出现临时的 Langfuse 错误，所有情况都会在钩子函数中以静默方式无操作处理，不会影响智能体的正常运行循环。

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

| Hook | 行为 |
|---|---|
| `pre_api_request` / `pre_llm_call` | 打开（或复用）一个按轮次划分的根级 span，命名为“Hermes turn”。针对此次 API 调用启动一个 `generation` 类型的子观察记录，并将近期消息序列化后作为输入。 |
| `post_api_request` / `post_llm_call` | 结束生成过程，附加 `usage_details`、`cost_details`、`finish_reason` 以及助手输出和工具调用信息。若没有工具调用但内容不为空，则结束当前轮次。 |
| `pre_tool_call` | 使用经过过滤处理的 `args` 启动一个 `tool` 类型的子观察记录。 |
| `post_tool_call` | 使用经过过滤处理后的 `result` 结束工具调用相关的观察记录。对于 `read_file` 类型的负载，会对其内容进行摘要处理（显示开头、结尾内容及省略行数），从而确保大文件读取后的总字符数仍低于 `HERMES_LANGFUSE_MAX_CHARS` 的限制。 |

通过 `langfuse.propagate_attributes`，会以 Hermes 会话 ID（或子智能体的任务 ID）作为键来对会话进行分组，因此同一个 `hermes chat` 会话中的所有内容都归属于同一个 Langfuse 会话。

**验证方法：**

```bash
hermes plugins list                 # observability/langfuse should show "enabled"
hermes chat -q "hello"              # check the Langfuse UI for a "Hermes turn" trace
```

**可选配置项**（位于 `.env` 文件中）：

| 变量名 | 默认值 | 用途 |
|---|---|---|
| `HERMES_LANGFUSE_ENV` | — | 日志追踪的环境标签（如 `production`、`staging` 等） |
| `HERMES_LANGFUSE_RELEASE` | — | 版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | `1.0` | 传递给 SDK 的采样率（范围：0.0–1.0） |
| `HERMES_LANGFUSE_MAX_CHARS` | `12000` | 消息内容、工具参数及工具输出结果的每字段截断长度 |
| `HERMES_LANGFUSE_DEBUG` | `false` | 向 `agent.log` 文件输出详细的插件日志 |

同时支持以 Hermes 前缀命名的环境变量以及标准 SDK 环境变量（如 `LANGFUSE_PUBLIC_KEY`、`LANGFUSE_SECRET_KEY`、`LANGFUSE_BASE_URL`）；若两者均被设置，则以 Hermes 前缀命名的变量优先生效。

**性能优化**：在首次调用钩子函数后，Langfuse 客户端会被缓存。如果凭证或 SDK 缺失，这一判断结果也会被缓存，后续调用可直接快速返回，无需再次检查环境变量或重新加载配置。

**禁用方式**：使用命令 `hermes plugins disable observability/langfuse` 即可。虽然该插件模块仍会被检测到，但在重新启用之前其代码不会被执行。

### NeMo Relay 原生集成（迁移说明）

NeMo Relay 已不再作为 Hermes 的内置插件提供。无需再运行 `hermes plugins enable observability/nemo_relay` 命令——如今 Hermes 核心已负责管理 Relay 会话、对话轮次、大语言模型及工具的整个生命周期。

若要启用 Relay 中间件或导出器，需先创建一个标准的 Relay `plugins.toml` 文件，然后在启动 Hermes 之前将 `HERMES_NEMO_RELAY_PLUGINS_TOML` 环境变量设置为该文件路径。此配置对由该 Hermes 进程托管的每个 Profile 均具有进程级效力。有关 ATOF、ATIF 以及 OpenTelemetry 相关选项的详细信息，请参阅 [NeMo Relay 可观测性配置](https://docs.nvidia.com/nemo/relay/configure-plugins/observability/about)。

旧的 `HERMES_NEMO_RELAY_ATOF_*` 和 `HERMES_NEMO_RELAY_ATIF_*` 设置已无法用于激活导出器。当未指定新的 `plugins.toml` 文件时，`hermes doctor` 命令会报告这些过时的设置。

#### 会话跨期分段（连续会话）

Relay 会在其作用域关闭时导出一个 span。尽管每次对话的 span 都会正常导出，但连续的网关会话仍可让其会话 span 保持开放状态数天之久。可选的分段功能仅会在每次对话结束之时切换会话作用域：

```yaml
gateway:
  telemetry:
    session_segments:
      on_compaction: false  # rotate after context compaction
      max_turns: 0          # 0 = unlimited; N = turns per segment
```

| 键值 | 默认值 | 行为说明 |
|---|---:|---|
| `on_compaction` | `false` | 在压缩操作完成后，于下一个轮次边界时进行切换。 |
| `max_turns` | `0` | 每完成 N 轮对话后进行切换；设置为 `0` 即表示取消此限制。 |

这两种默认设置均能确保整个会话期间保持单一的会话范围。经过切换的片段会保留原有的 `session_id`，同时新增 `hermes.session.segment` 以及 `hermes.session.segment_reason`（值为 `compaction` 或 `max_turns`）。 

### google_meet

该功能允许智能体**加入、转录并参与 Google Meet 通话**——可为会议做笔记、总结讨论内容、针对特定议题进行跟进，还可通过文本转语音功能（TTS）选择性地将回复内容说回通话中。

**主要功能包括：**

- 通过浏览器自动化技术，以无界面虚拟参与者身份加入 Meet 会议链接；
- 利用配置好的语音转文字服务，对会议音频进行实时转录；
- 提供 `meet_join` / `meet_status` / `meet_transcript` / `meet_leave` / `meet_say` 等工具集，智能体可通过这些工具加入通话、获取实时转录内容，并根据所听内容采取相应操作；
- 会议结束后，相关文件（如转录文本、会议状态信息）会保存在 `~/.hermes/workspace/meetings/<meeting_id>/` 目录下。

**设置方法：**

```bash
hermes plugins enable google_meet
hermes meet setup   # preflight: playwright, chromium, auth file
hermes meet auth    # opens a browser to sign into Google and saves session state —
                    # needs a Google account with Meet access. Host approval may be
                    # required if the meeting enforces "only invited participants can join".
```

**通过聊天框使用方式：**

> “加入 meet.google.com/abc-defg-hij 并做会议记录。通话结束后，请将包含行动项的总结发给我。”

该智能体将自动帮你进入会议，全程实时将转录内容同步至其上下文信息中，待会议结束（或你要求停止时），它会生成结构化的总结报告。

**适用场景：** 需要机器人为异步参与的成员进行转录和总结的定期站会；需要结构化记录的访谈类场景；任何原本就需要使用 Fireflies、Otter 或 Grain 工具的场景。若不希望让人工智能监听会议内容，请勿启用此功能。

**禁用方法：** `hermes plugins disable google_meet`。所有已保存的转录文件将存放在 `~/.hermes/workspace/meetings/` 目录中，直至你手动删除它们。

### hermes-achievements

该插件会在控制台添加一个**类似 Steam 的成就面板**——根据你真实的 Hermes 使用记录，生成 60 多个可收集的、分等级的徽章。这些徽章涵盖工具链使用技巧、调试模式、编码连续时长、技能/内存使用情况、模型/提供方类型，以及个人使用习惯（如周末或夜间编程）。该插件最初由 [@PCinkusz](https://github.com/PCinkusz) 作为外部插件开发，后被整合进 Hermes 内部，以确保其功能能与 Hermes 的更新保持同步。

**工作原理：**

- 在控制台后端全面扫描您的 `~/.hermes/state.db` 会话历史记录。  
- 每个会话的统计信息会通过 `(started_at, last_active)` 指纹进行缓存，因此后续扫描时仅会对新创建或发生变更的会话重新进行分析。  
- 首次扫描会在后台线程中执行——即便数据库中存在数千个会话，控制台也不会因等待扫描而阻塞。  
- 解锁状态会被保存至 `$HERMES_HOME/plugins/hermes-achievements/state.json` 文件中。

**等级晋升路径：** 铜级 → 银级 → 金级 → 钻石级 → 奥林匹克级。每张等级卡片都会展示一个“统计指标”板块，明确列出当前所追踪的具体指标。

**成就状态：**

| 状态 | 含义 |
|---|---|
| 已解锁 | 已达到至少一个等级 |
| 已发现 | 该成就已存在，进度可见，但尚未获得 |
| 秘密 | 在 Hermes 检测到会话历史中的相关信号之前，该成就保持隐藏状态 |

**API** — 接口路径位于 `/api/plugins/hermes-achievements/` 下：

| 接口地址 | 功能 |
|---|---|
| `GET /achievements` | 显示包含各徽章解锁状态的完整列表（在首次扫描进行时，会返回一个待处理的占位值） |
| `GET /scan-status` | 查看后台扫描器的状态：`idle` / `running` / `failed`，以及上次运行时长和运行次数 |
| `GET /recent-unlocks` | 显示最近解锁的20个徽章，最新解锁的排在最前 |
| `GET /sessions/{id}/badges` | 查看在特定会话中获得的徽章 |
| `POST /rescan` | 手动触发同步重新扫描（此操作会阻塞界面；适用于用户点击重新扫描按钮的场景） |
| `POST /reset-state` | 清除所有解锁记录及缓存快照 |
**状态文件**——存储于 `$HERMES_HOME/plugins/hermes-achievements/` 目录下：

| 文件 | 内容 |
|---|---|
| `state.json` | 解锁历史记录：记录您已获得的徽章及其获取时间。该文件在 Hermes 更新过程中保持稳定。 |
| `scan_snapshot.json` | 最近一次完成的扫描数据（在仪表板加载时会立即显示）。 |
| `scan_checkpoint.json` | 按指纹标识的会话级统计信息缓存，可加快快速重新扫描的速度。 |

**性能说明：**

- 对约 8,000 个会话进行首次扫描需要几分钟时间。该扫描会在首次请求仪表板时在后台线程中执行；此时界面会显示一个待处理占位符，并持续轮询 `/scan-status` 状态。
- **首次扫描过程中的逐步更新结果**——扫描工具会每隔约 250 个会话发布一次部分快照，因此每次刷新仪表板时都能看到随着扫描进度增加而逐步解锁的更多徽章，无需长时间盯着零值等待。
- 快速重新扫描会重用那些 `started_at` 和 `last_active` 指纹与缓存检查点匹配的会话的统计信息——即便处理的历史记录量很大，也能在几秒钟内完成扫描。
- 内存中快照的有效时间为 120 秒；过期的请求会立即返回旧快照，并触发后台刷新。因此不必因为快照过期而长时间等待。

**启用方式：**无需额外配置——`hermes-achievements` 是仅用于仪表板的插件（没有生命周期钩子，也不提供模型可见工具）。它在首次启动时会自动作为标签页注册到 `hermes dashboard` 中。`plugins.enabled` 配置项仅用于控制具有生命周期或工具功能的插件；而仪表板插件则是通过其 `dashboard/manifest.json` 文件被自动识别的。

**禁用方式：** 删除或重命名 `plugins/hermes-achievements/dashboard/manifest.json`，或者在 `~/.hermes/plugins/hermes-achievements/` 目录下使用同名的用户插件来覆盖它，该用户插件无需包含仪表板功能。位于 `$HERMES_HOME/plugins/hermes-achievements/` 下的插件状态文件仍会保留——重新安装即可维持您的解锁记录。

## 添加内置插件

内置插件的编写方式与其他 Hermes 插件完全相同——请参阅[构建 Hermes 插件](/developer-guide/plugins)文档。唯一的区别在于：

- 插件目录位于 `<repo>/plugins/<name>/`，而非 `~/.hermes/plugins/<name>/`
- 在“hermes plugins list”中，此类插件的来源会被标记为“bundled”
- 同名的用户插件会覆盖内置版本

以下情况适合将插件制作成内置插件：

- 该插件没有可选依赖项（或所有依赖项均已通过 `pip install .[all]` 安装）
- 其功能能惠及大多数用户，且采用禁用而非启用模式
- 其逻辑与代理的生命周期钩子相关联，否则代理需要手动调用这些钩子
- 能够补充核心功能，而不会增加模型可见的工具界面

相反，以下类型插件应保持为可用户安装的插件，而非内置插件：依赖 API 密钥的第三方集成、特定场景的工作流、庞大的依赖树，以及任何会默认显著改变代理行为的插件。
