# 上下文压缩与缓存机制

Hermes Agent采用了双重压缩系统以及Anthropic提示词缓存技术，从而在长对话场景中高效管理上下文窗口的使用效率。

相关源文件：`agent/context_engine.py`（抽象基类）、`agent/context_compressor.py`（默认压缩引擎）、`agent/prompt_caching.py`、`gateway/run_turn.py`（会话管理功能）、`agent/compression_facade.py`（用于查找 `_compress_context` 函数）。

## 可插拔的上下文引擎

上下文管理功能基于`ContextEngine`抽象基类实现（位于`agent/context_engine.py`文件中）。系统内置的`ContextCompressor`为默认压缩引擎，但用户也可以通过插件替换为其他类型的引擎（例如无损上下文管理引擎）。

```yaml
context:
  engine: "compressor"    # default — built-in lossy summarization
  engine: "lcm"           # example — plugin providing lossless context
```

该引擎负责以下功能：  
- 决定何时执行压缩操作（`should_compress()`）  
- 执行实际的压缩操作（`compress()`）  
- 可选地提供代理可调用的工具（例如 `lcm_grep`）  
- 通过 API 响应跟踪令牌使用情况  

引擎的选择通过 `config.yaml` 中的 `context.engine` 参数进行配置。具体的筛选顺序如下：  
1. 检查 `plugins/context_engine/<名称>/` 目录  
2. 检查通用插件系统（`register_context_engine()`）  
3. 最终使用内置的 `ContextCompressor`  

插件引擎**绝不会自动激活**——用户必须明确将 `context.engine` 设置为对应插件的名称。默认值 `"compressor"` 始终使用内置引擎。  

可通过 `hermes plugins` → Provider Plugins → Context Engine 进行配置，或直接编辑 `config.yaml` 文件。  

如需构建上下文引擎插件，请参阅 [上下文引擎插件](/developer-guide/context-engine-plugin)。  

## 双重压缩系统  

Hermes 搭载了两个独立运行的压缩层：

```
                     ┌──────────────────────────┐
  Incoming message   │   Gateway Session Hygiene │  Fires at 85% of context
  ─────────────────► │   (pre-agent, rough est.) │  Safety net for large sessions
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │   Agent ContextCompressor │  Fires at 50% of context (default)
                     │   (in-loop, real tokens)  │  Normal context management
                     └──────────────────────────┘
```

### 1. 网关会话容量限制（85%阈值）

该功能位于 `gateway/run_turn.py` 文件中（可搜索 `Session hygiene`）。它是一道**安全保障机制**，在智能体处理消息之前启动，旨在防止因轮次间隔过长导致会话规模过大而引发的API故障（例如在Telegram/Discord中经过整夜的累积）。

- **阈值**：固定为模型上下文长度的85%
- **令牌来源**：优先使用上一次轮次中API报告的实际令牌数，其次是会话记录中保存的使用量基准值（实际计数加上自上次之后新增内容的增量；该数据可在网关重启后依然保留），最后才是基于字符数的粗略估算值（`estimate_messages_tokens_rough`）
- **触发条件**：仅当 `len(history) >= 4` 且压缩功能已启用时才会触发
- **作用**：用于检测那些已超出智能体自身压缩功能处理范围的会话

网关的容量限制阈值被设定得比智能体的压缩阈值更高，这是有意为之。若将阈值设为50%（与智能体相同），则会在长时间运行的网关会话中，导致每一轮都过早进行压缩。

### 2. 智能体上下文压缩器（50%阈值，可配置）

该功能位于 `agent/context_compressor.py` 文件中。它是**主要的压缩系统**，在智能体的工具处理循环中运行，并能获取API报告的精确令牌计数。

#### 令牌统计方式：提供者基准值与显式启发式备用机制

每个压缩节点（轮次开始预检、空闲状态、API调用前压力检测、工具使用后检测）都会首先查询**使用基准值**（位于 `agent/usage_anchor.py` 文件中）：即提供商上一次的提示词与完成标记数量，再加上自该响应之后新增消息数量的粗略估算值。该基准值通过内容指纹来标识对应的计费对话记录，因此即便每个轮次节点都会从数据库中重新读取历史记录，该基准值依然能够保留下来；同时它还会被保存在会话记录中，这样在满足条件的前提下，通过 `--resume` 参数启动的新进程或桌面端的逐轮服务功能即可恢复该基准值。而压缩操作、会话重置以及Codex原生压缩功能则会清除这些基准值。

对于内置引擎中的**轮次开始检测和API调用前阈值检测节点**，在不存在基准值的情况下（即首次请求、回放/编辑后重新发送请求），系统会对整个上下文范围的阈值进行粗略估算，并**等待一次请求**以获取提供商的确认信息（通过 `should_defer_preflight_to_real_usage` 参数实现）。这类估算可能涉及整个上下文窗口范围的内容，但估算出的数值本身并不能证明该请求一定会失败。在更换模型后，原有的使用数据会被清除，新的提供商也会对首次请求进行判定；对于真正超出限制规模的请求，在系统采取主动恢复措施之前，可能会先出现一次请求被拒绝的情况。

等待状态并不会导致功能禁用。即便某次响应未报告实际使用量，现有的启发式回退机制依然有效；即便实际使用量已超出阈值，且经提供商验证存在数据溢出情况，压缩功能仍可正常运行。压缩后的锁定机制会等待一次响应，即便该响应未提供使用量信息也会被处理。恢复过程仍受压缩尝试次数限制以及无进展保护机制的约束，而非陷入无限重试的循环。

这**并非仅基于精确计数的策略**，也不是对#104462中“绝不进行估算”的绝对化处理。以下策略保持不变：

- 锚点信息包含提供商的提示词与完成标记，以及一个**大致的附加消息变化量**（首个附加的助手内容已计入完成使用量中）。因此，即便新工具的输出结果较大，仍可通过估算出的变化量来判定是否超过阈值。边界指纹匹配不会对整个前缀、模型、工具或系统提示词进行完整指纹识别。
- 自愿启用的空闲状态压缩机制拥有独立的最低阈值与冷却时间，能够针对无锚点压力的情况采取行动；它并不共享阈值控制机制中的单次请求等待规则。
- 代理前置网关净化机制仍保留其基于粗略历史记录的回退方案以及严格的内容安全防护机制。重放工具的`gateway`模块仅负责重新加载对话记录字典，**不会**启用该独立的净化策略。
- 工具使用后无数据时的回退机制、微压缩功能、摘要/结尾内容长度调整、数据剪裁以及溢出进度检测等功能，依然依赖本地估算值。原生压缩机制则保持其针对不同提供商的专属控制逻辑及检查点锁定机制。
提供者数量相关接口的实现仍被推迟。要消除这些剩余的估算值，需要明确的策略决策：要么接受文档中规定的默认 fallback 方案，要么用提供者的实际使用数据来替代这些估算，并为那些从未返回使用记录的提供者定义相应的行为规则。仅仅禁用所有无依据的维护功能并不能达到相同效果。

`evals/token_accounting/replay_gates.py` 文件负责处理窗口内外的成本膨胀问题、超过阈值时的控制机制、锚点的重新加载/恢复功能，以及基于实际压缩但使用固定本地摘要文本的本地 HTTP 流量溢出或低使用量场景下的恢复处理。这些均为脚本化的控制流检查，而非来自供应商的分词器或计费数据。

那些不可见的提供者数据块（如 Codex 推理/压缩项中的 `encrypted_content`）不会对任何本地估算值产生任何影响；只有实际使用量才会为其定价。

图像的费用是根据**从提供者使用数据中得出的每张图像成本**来确定的（参见 `agent/image_token_cost.py`），而非遵循供应商的固定公式。对于那些自上一个锚点以来新增了 N 张图像的响应，实际 `prompt_tokens` 数量与仅文本形式的预估值之间的差值，将按 N 乘以该提供者的单价来计算。这一数值会存储在 `~/.hermes/cache/image_token_costs.json` 文件中的每个 `model@host` 条目下，并且会对每轮对话设置上限，以便触发估算器、尾预算控制机制以及网关校验功能都能使用相同的数值。在首次视觉处理轮次之前，则统一适用 1,500 的默认值。

#### 失败冷却机制与经提供者验证的流量溢出情况

若摘要生成尝试失败或陷入停滞状态，系统会启动会话级的**失败冷却机制**
（冷却时间逐步延长，从60秒变为300秒，再变为900秒，并存储在`state.db`中）。在冷却机制生效期间，常规的阈值触发型压缩操作会被延迟，从而避免因摘要后端故障而导致每轮都重复尝试。不过，仍有两种方式可以发起真正的生成尝试：

- 手动执行`/compress`命令并设置`force=True`——可取消冷却限制并重新尝试。
- **由提供方确认的超出长度限制情况**——当提供方本身因上下文长度超限而拒绝请求时，恢复流程会忽略冷却限制，进行一次有限次数的尝试（最多`max_compression_attempts`次），且不会清除冷却记录。若在此情况下仍延迟处理，会导致会话陷入死循环：每轮都会被提供方拒绝，后续的失败又会进一步延长冷却时间（参见问题#100661）。如果该次尝试也失败了，冷却机制将按常规方式被记录。

## 配置

所有压缩相关设置均来自`config.yaml`文件中的`compression`键：

```yaml
compression:
  enabled: true              # Enable/disable compression (default: true)
  threshold: 0.50            # Fraction of context window (default: 0.50 = 50%)
  # model_thresholds:        # Per-model threshold overrides (substring match,
  #   "glm-5.2": 0.40        # longest key wins). See "Per-model threshold
  #   "claude-sonnet": 0.35  # overrides" below.
  target_ratio: 0.20         # How much of threshold to keep as tail (default: 0.20)
  tail_mode: lean            # Tail retention policy: lean | legacy (default: lean)
  protect_last_n: 20         # Minimum protected tail messages (default: 20)
  min_tail_user_messages: 1  # Real user messages guaranteed in the tail (default: 1)
  codex_gpt55_autoraise: true  # gpt-5.5 on Codex OAuth: raise trigger to 85% (default: true)
  codex_gpt55_autoraise_notice: true  # Show the one-time autoraise notice (default: true)
  codex_app_server_auto: native  # native|hermes|off for Codex app-server thread compaction
  codex_responses_native: false  # gpt-5.6 on direct OpenAI/Codex: server-side compaction (opt-in)
  codex_responses_compact_threshold: null  # Automatic server compaction trigger
  in_place: true             # Compact on the same session id, no rotation (default: true)

# Summarization model/provider configured under auxiliary:
auxiliary:
  compression:
    model: null              # Override model for summaries (default: auto-detect)
    provider: auto           # Provider: "auto", "openrouter", "nous", "main", etc.
    base_url: null           # Custom OpenAI-compatible endpoint
```

### 参数详情

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `threshold` | `0.50` | 0.0-1.0 | Compression triggers when prompt tokens ≥ `threshold × context_length` |
| `model_thresholds` | `{}` | map | Per-model overrides of `threshold`. Keys are substring-matched against the model name (longest match wins). The small-context floor still applies on top (see below) |
| `target_ratio` | `0.20` | 0.10-0.80 | Controls tail protection token budget: `threshold_tokens × target_ratio` (legacy mode only — `lean` uses its own clamp) |
| `tail_mode` | `lean` | `lean`, `legacy` | Tail retention policy. `legacy` keeps a `target_ratio`-sized verbatim tail (~100K+ tokens on big-window models). `lean` keeps a clamped tail of `2.5% × context window` (10K floor, 25K cap) and instead carries continuity in the summary: a detailed identifier-preserving session log (produced by the same single summary request — lean compaction makes exactly one auxiliary LLM call per attempt), a mechanically extracted anchor index (PR numbers, SHAs, paths, error strings — regex, never paraphrased), every real user message quoted verbatim (newest-first budget), and a `session_search` recovery pointer so the agent can re-access anything summarized away. Oversized regions are evenly sampled into the summarizer input (with explicit elision markers) rather than triggering extra calls. Result on 500K-token real sessions: ~49K retained vs ~162K, with higher recall when paired with recovery (see `evals/compaction/results/`). Old tool results inside the lean tail are demoted to one-line stubs carrying a recovery pointer |
| `protect_last_n` | `20` | ≥1 | Minimum number of recent messages always preserved |
| `min_tail_user_messages` | `1` | ≥1 | Minimum number of REAL (actionable) user messages guaranteed to survive in the uncompressed tail. `1` = the existing single last-user anchor (behavior-preserving default). Raise to e.g. `3` to keep the last 3 real user turns verbatim even when bulky tool outputs fill the tail token budget. Blank platform echoes, compaction handoffs, and synthetic continuation rows never count toward N. The guarantee wins over the tail token budget — the tail may exceed the budget when the anchor pulls the cut back |
| `protect_first_n` | `3` | (hardcoded) | System prompt + first exchange always preserved |
| `idle_compact_after_seconds` | `0` | ≥0 seconds | Opt-in: compact up front when a session resumes after this many seconds idle (0 = disabled). Skips when context ≤ threshold × target_ratio; honors cooldown/anti-thrash/lock guards |
| `codex_gpt55_autoraise` | `true` | bool | Raise the trigger to 85% for gpt-5.4/5.5/5.6 and gpt-6 Astra on the ChatGPT Codex OAuth route (see below). Set `false` to keep the global `threshold` |
| `codex_gpt55_autoraise_notice` | `true` | bool | Show the one-time Codex gpt-5.5 autoraise notice. Set `false` to keep the 85% autoraise but suppress the banner |
| `codex_app_server_auto` | `native` | `native`, `hermes`, `off` | Thread-compaction mode for Codex app-server sessions (see below) |
| `codex_responses_native` | `false` | bool | Opt in to OpenAI's server-side compaction on the Responses API. Engages only for gpt-5.6-family models on the direct OpenAI API or a ChatGPT Codex subscription (see below) |
| `codex_responses_compact_threshold` | `null` | `null` or positive integer | `null` follows the resolved local compression trigger with an 8,192 token safety margin. A positive integer remains absolute and only clamps downward when required. Invalid values use automatic behavior. Automatic mode falls back to `200000` when no usable local trigger exists |
| `in_place` | `true` | bool | Compact on the same session id instead of rotating to a new one (see below) |

### 在原位置压缩（单个稳定会话 ID）

当设置 `compression.in_place: true`（默认值）时，压缩操作会**在同一个会话 ID 下重写实时消息列表**：系统提示会被重新生成，汇总后的中间内容会被替换进去，而压缩前的消息记录则会以软归档形式保存在同一个 ID 下（在会话存储中标记为 `active=0, compacted=1`）——这些记录仍可通过 `session_search` 检索并恢复，绝不会被删除。该模式下不存在 `parent_session_id` 链，也不会进行 `name #N` 这样的重新编号操作；一个对话在其整个生命周期内都保持同一个持久性 ID。这样一来，那些由会话轮转引发的故障问题（如 `/goal` 状态丢失、孤立会话、跨边界搜索缺失等）也就得以消除。

客户端只需关注该压缩模式，而无需关注会话 ID 的变化：

- `session:compress` 事件会携带 `in_place: true/false` 及 `old_session_id` 参数（在原位置压缩模式下该值为空字符串，因为不存在旧会话 ID）。
- 网关会根据代理节点中与轮转无关的 `_last_compaction_in_place` 标志来重新确定转录处理的基准，而非依据会话 ID 的变化差异。

若要将模式切换回旧的轮转方式，即每次压缩都会生成一个通过 `parent_session_id` 与前一个会话关联的新会话 ID，请将 `inplace: false` 设为 true。

### 辅助功能实现与尾部数据保留

较小的辅助压缩模型可在不改变所选尾部策略的情况下，降低实时压缩的触发阈值。在“精简”模式下，选择预算仍基于**主模型的上下文窗口**来计算：比例为2.5%，范围限制在1万至2.5万个标记之间。例如，当主模型规模为100万，辅助模型为512K时，即便可行性阈值从85万下降到512K，其选择预算仍保持在2.5万个标记。而“传统”模式则会重新计算`threshold_tokens × target_ratio`的值（即512K规模下为102,400个标记 × 0.20）。这些数值属于尾部选择预算，并非对整个压缩后上下文的严格限制——受保护的消息、边界对齐内容、摘要以及锚点信息都可能增加标记数量。

### 每个模型的阈值覆盖设置

`compression.model_thresholds`功能允许根据当前使用的模型，在不同节点触发压缩操作——这对于需要在上下文窗口差异极大的模型之间切换的场景尤为有用（例如，上下文窗口为100万的模型可稍后进行压缩，而上下文窗口为128K的模型则应更早压缩）。

```yaml
compression:
  threshold: 0.50
  model_thresholds:
    "glm-5.2": 0.40
    "glm-5.2-1M": 0.25
    "claude-sonnet": 0.35
```

分辨率规则：

- 键值会与模型名称进行**子串匹配**，**匹配度最高的键值将起决定作用**
 （对于模型 `glm-5.2-1M`，`glm-5.2-1M` 的匹配度高于 `glm-5.2`）。
- 若没有键值匹配（或映射表为空），则适用全局阈值。
- 每次切换 `/model` 时都会重新进行分辨率判定；若切换到的模型没有匹配的键值，则会回退到全局阈值。
- 即使有自定义设置，**最小上下文限制依然有效**（仅限上限调整）：
  上下文窗口小于 512K 的模型的阈值最低为 `0.75`，因此低于此最低值的自定义阈值将被提升至 `0.75`，而高于该值的自定义阈值（如 `0.80`）则优先生效。

插件上下文引擎可通过 `from agent.context_compressor import resolve_model_threshold` 重用相同的分辨率逻辑；而那些重写了 `update_model()` 函数的引擎则拥有自己的压缩策略，可能不会考虑该映射表。

### Codex gpt-5.x / Astra 阈值自动上调功能

ChatGPT Codex OAuth后端将gpt-5.4/5.5/5.6以及gpt-6 Astra模型的上下文窗口大小严格限制在**272K**。而在OpenAI的直接API及OpenRouter平台上，同一模型类型的上下文窗口可达105万字符，GitHub Copilot则为40万字符。在默认50%的触发阈值下，上下文压缩会在约136K时启动——这仅相当于模型实际可用空间的一半。当当前使用的路由为Codex OAuth（`provider: openai-codex`）且模型属于上述系列时（Astra指任何包含“astra”字样的模型；已开启更高上下文窗口的特定版本因无需额外限制而除外），Hermes会将触发阈值提升至**85%**（约231K），并显示一条提示信息及对应的取消选项。该提示每个用户配置仅展示一次——` $HERMES_HOME`目录下的`.codex_gpt55_autoraise_notice`文件会记录提示已显示的痕迹，因此后续的代理/会话启动（如每次收到新消息）不会再重复显示；若阈值 later再次变更，则会重新发出通知。这一调整仅影响通过该特定路由加载的模型；在其他提供商平台上使用的相同模型仍会保持原有的全局阈值。若需恢复为全局默认值：

```bash
hermes config set compression.codex_gpt55_autoraise false
```

为保持85%的自动提升比例，同时仅隐藏一次性通知：

```bash
hermes config set compression.codex_gpt55_autoraise_notice false
```

### Codex 大上下文模式 `-900k` 变体（需手动启用）

ChatGPT Codex 后端虽宣称 gpt-5.4 及 gpt-5.6（Sol/Terra/Luna 系列）的上下文窗口为 272K，但实际上允许 ChatGPT 订阅账户输入约 911K 个标记（数据截至 2026 年 8 月已通过实时验证）。Hermes 仍将**272K 作为基础模型的默认值**——更大的上下文窗口意味着每次请求可处理的标记更多，也会更快消耗订阅额度，因此大上下文模式必须手动启用。

若要使用大上下文窗口，需在 `/model` 参数中明确选择 `-900k` 变体（例如 `gpt-5.6-sol-900k`、`gpt-5.6-terra-900k`、`gpt-5.6-luna-900k`、`gpt-5.4-900k`）。这些只是 Hermes 端的别名：在将模型标识发送至后端之前，其后的后缀会被移除，且计费与使用统计也会将其视为基础模型。那些严格限制上下文为 272K 的模型（如 gpt-5.5、gpt-5.4-mini）则没有 `-900k` 变体。

压缩阈值会随上下文窗口大小而变化：基础模型（272K）采用上文所述的**85% 自动提升机制**，而 `-900k` 变体则保持用户设定的全局 `compression.threshold` 值（默认为 50%，即约 450K）。设置自动提升机制是为了避免在小上下文窗口下造成资源浪费，而 900K 的大窗口则无需此功能。

### Codex 应用服务器线程压缩功能

Codex应用服务器运行模式（`api_mode: codex_app_server`，即Codex CLI/Agent的运行时）与其他运行模式有所不同：该模式下由Codex Agent负责管理线程上下文，因此Hermes的辅助摘要生成器无法对其进行压缩——若重新编写本地转录内容，会导致实际线程规模无限增长，直至强制重置上下文。针对这种运行时，压缩操作通过应用服务器自身的机制来完成：

- 手动压缩（`/compress`）：向应用服务器发起压缩请求（`thread/compact/start`），并等待压缩操作完成。
- 自动压缩由`compression.codex_app_server_auto`参数控制：默认值为`native`，由应用服务器自行决定压缩时机，同时Hermes会记录相关的压缩事件（如压缩计数、会话事件）。可将该参数设置为`hermes`，让Hermes设定的压缩阈值触发应用服务器的压缩操作；或设置为`off`，完全禁用Hermes发起的自动压缩功能（此时Codex仍可进行原生压缩）。

在这种运行模式下，Hermes的本地转录内容不会被重新编写——`state.db`会记录压缩边界，而可见的转录内容则保持不变。其他所有运行模式（包括Codex OAuth聊天会话）均会使用Hermes的摘要压缩器。

### 原生响应压缩功能（直接使用OpenAI的gpt-5.6模型/Codex订阅版）

OpenAI的Responses API支持服务器端上下文压缩功能：当请求中包含`context_management: [{type: "compaction", compact_threshold: N}]`且生成的输出内容超过N个token时，服务器会将旧上下文剪裁并封装为经过加密处理的“压缩”输出项。Hermes会将该压缩项存储在助手消息的回放侧边数据中，并在后续轮次中将其重新发送出来，以此替代被剪裁的历史上下文——从而实现无需客户端额外处理即可进行长时序信息检索的功能，同时还能满足ZDR规范的要求（设置`store: false`且不包含`previous_response_id`）。

如需启用此功能，需设置`compression.codex_responses_native: true`。由于该功能的限制较为严格，因此会针对每个请求重新进行验证：
- **模型限制**：仅支持gpt-5.6系列模型。其他模型在检测到该字段时会无法在服务器端正常工作——gpt-5.1/5.2模型会返回HTTP 500错误或中断响应流，且目前没有结构化的降级处理方案，这一点已在2026年8月的实际测试中得到验证。
- **接口路径限制**：仅支持`api.openai.com`（使用OpenAI API密钥）或ChatGPT Codex后端（通过Codex订阅进行OAuth认证）。xAI、GitHub/Copilot、OpenRouter、各类中转服务以及本地服务器均无法访问该字段。
压缩功能的其他方面保持不变：本地压缩器仍作为备用方案存在（默认阈值会被设定在本地触发值下方约8K个令牌处，以便服务器优先进行压缩）；如果结构化提供方拒绝该字段，那么该会话将不再使用原生压缩功能，而是重新发送不包含该字段的请求。若将会话切换到不符合要求的模型或路由，该字段 simply就不会被发送——当端点发生变化时，现有的跨发布方保护机制会自动丢弃已捕获的检查点，从而避免其被重新播放。

默认情况下，`compression.codex_responses_compact_threshold: null` 会根据确定的本地触发值来设定默认阈值。例如，若本地触发值为765,000，则对应的阈值将为756,808。如需设定固定阈值，可输入正整数，比如200,000。无效的数值则会触发自动模式。若不存在可用的本地触发值，自动模式将使用200,000作为阈值。而提供方的最低阈值则为1,024个令牌，因此低于此阈值的异常较小的本地触发值将无法确保严格遵循原生的优先处理顺序。

### 计算值（基于默认设置下的200K上下文模型）

```
context_length       = 200,000
threshold_tokens     = 200,000 × 0.50 = 100,000
tail_token_budget    = 100,000 × 0.20 = 20,000
max_summary_tokens   = min(200,000 × 0.05, 12,000) = 10,000
```

:::note 阈值是根据 MAIN 模型的上下文窗口确定的。
`threshold_tokens` 的值始终为 `threshold × context_length`，其中 `context_length` 指的是**主智能体模型**的上下文窗口，而非辅助/摘要模型的窗口。对于上下文长度为 262,144 个令牌的模型，在默认阈值 `0.50` 的情况下，该阈值为 `262,144 × 0.50 = 131,072`。这一数值与常见的“128K 上下文长度”相近，纯属百分比计算的结果，并不意味着触发压缩的是辅助模型的窗口。辅助模型的上下文窗口是另一个需要单独考虑的因素——请参阅下方的“摘要模型上下文长度”警告，了解它会影响摘要的生成，而不会影响压缩触发的时机。
:::


## 压缩算法

`ContextCompressor.compress()` 方法采用四阶段算法：

### 第一阶段：剔除旧工具输出结果（操作简单，无需调用大语言模型）

位于受保护区域之外的过旧工具输出结果（长度超过 200 个字符）将被替换为：
```
[Old tool output cleared to save context space]
```

这是一种低成本的预处理方式，能够有效节省大量令牌，避免处理繁琐的工具输出内容（如文件内容、终端输出及搜索结果）。 

### 第二阶段：确定处理范围

```
┌─────────────────────────────────────────────────────────────┐
│  Message list                                               │
│                                                             │
│  [0..2]  ← protect_first_n (system + first exchange)        │
│  [3..N]  ← middle turns → SUMMARIZED                        │
│  [N..end] ← tail (by token budget OR protect_last_n)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

消息尾部的保护机制采用**令牌预算制**：从消息末尾开始向后遍历，不断累积令牌，直至预算耗尽。如果按此方式无法保护足够多的消息，系统则会回退到固定的`protect_last_n`条消息保护策略。

边界处理会进行对齐，以避免拆分`tool_call`与`tool_result`组。`_align_boundary_backward()`方法会依次检查连续的`tool_result`，从而找到对应的父级助手消息，确保各组结构完整。

### 第三阶段：生成结构化摘要

:::warning 摘要模型的上下文长度限制
摘要模型的上下文窗口**必须至少与主智能体模型相同大小**。中间部分的全部内容会通过一次`call_llm(task="compression")`调用发送给摘要模型。如果摘要模型的上下文容量不足，API会返回上下文长度过大的错误——`_generate_summary()`函数会捕获该错误，记录警告信息，并返回`None`值。此时压缩器将直接丢弃中间部分的对话内容而不会生成摘要，从而导致对话上下文丢失。这是导致压缩质量下降的最常见原因。
:::

中间部分的对话内容会通过辅助大型语言模型，并结合结构化模板来进行摘要生成：

```
## Goal
[What the user is trying to accomplish]

## Constraints & Preferences
[User preferences, coding style, constraints, important decisions]

## Progress
### Done
[Completed work — specific file paths, commands run, results]
### In Progress
[Work currently underway]
### Blocked
[Any blockers or issues encountered]

## Key Decisions
[Important technical decisions and why]

## Relevant Files
[Files read, modified, or created — with brief note on each]

## Next Steps
[What needs to happen next]

## Critical Context
[Specific values, error messages, configuration details]
```

摘要部分的字数会随着需要压缩的内容量而变化：
- 计算公式：`内容标记数 × 0.20`（即常量 `_SUMMARY_RATIO`）
- 最小值：2,000 个标记
- 最大值：`min(上下文长度 × 0.05, 12,000)` 个标记

### 第四阶段：组装压缩后的消息

压缩后的消息列表包含以下内容：
1. 开头消息（首次压缩时会在系统提示语后附加说明）
2. 摘要消息（会选择不同的角色，以避免出现连续相同角色的情况）
3. 结尾消息（保持不变）

那些没有对应工具调用/工具结果的孤立项会由 `_sanitize_tool_pairs()` 函数进行处理：
- 引用已被移除的调用的工具结果 → 被直接删除
- 其结果已被移除的工具调用 → 会注入虚拟结果

### 迭代式重新压缩

在后续的压缩过程中，之前的摘要内容会被传递给大语言模型，并附带**更新**该摘要的指令，而非从头开始生成新摘要。这样一来，多次压缩过程中的信息就能得以保留——旧信息会从“处理中”状态变为“已完成”状态，新的进展信息会被添加，而过时的信息则会被移除。

压缩器实例中的 `_previous_summary` 字段便用于存储上一次生成的摘要文本，以实现这一功能。

## 压缩前/后示例

### 压缩前（45条消息，约95,000个标记）

```
[0] system:    "You are a helpful assistant..." (system prompt)
[1] user:      "Help me set up a FastAPI project"
[2] assistant: <tool_call> terminal: mkdir project </tool_call>
[3] tool:      "directory created"
[4] assistant: <tool_call> write_file: main.py </tool_call>
[5] tool:      "file written (2.3KB)"
    ... 30 more turns of file editing, testing, debugging ...
[38] assistant: <tool_call> terminal: pytest </tool_call>
[39] tool:      "8 passed, 2 failed\n..."  (5KB output)
[40] user:      "Fix the failing tests"
[41] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[42] tool:      "import pytest\n..."  (3KB)
[43] assistant: "I see the issue with the test fixtures..."
[44] user:      "Great, also add error handling"
```

### 压缩后（25条消息，约45K个标记）

```
[0] system:    "You are a helpful assistant...
               [Note: Some earlier conversation turns have been compacted...]"
[1] user:      "Help me set up a FastAPI project"
[2] assistant: "[CONTEXT COMPACTION] Earlier turns were compacted...

               ## Goal
               Set up a FastAPI project with tests and error handling

               ## Progress
               ### Done
               - Created project structure: main.py, tests/, requirements.txt
               - Implemented 5 API endpoints in main.py
               - Wrote 10 test cases in tests/test_api.py
               - 8/10 tests passing

               ### In Progress
               - Fixing 2 failing tests (test_create_user, test_delete_user)

               ## Relevant Files
               - main.py — FastAPI app with 5 endpoints
               - tests/test_api.py — 10 test cases
               - requirements.txt — fastapi, pytest, httpx

               ## Next Steps
               - Fix failing test fixtures
               - Add error handling"
[3] user:      "Fix the failing tests"
[4] assistant: <tool_call> read_file: tests/test_api.py </tool_call>
[5] tool:      "import pytest\n..."
[6] assistant: "I see the issue with the test fixtures..."
[7] user:      "Great, also add error handling"
```


## 提示词缓存（Anthropic）

代码来源：`agent/prompt_caching.py`

该功能通过缓存对话开头部分，可在多轮对话中将输入token成本降低约75%。它利用了Anthropic的`cache_control`断点机制。

### 策略：system_and_3

Anthropic允许每个请求最多设置4个`cache_control`断点。Hermes则采用“system_and_3”策略：

```
Breakpoint 1: System prompt           (stable across all turns)
Breakpoint 2: 3rd-to-last non-system message  ─┐
Breakpoint 3: 2nd-to-last non-system message   ├─ Rolling window
Breakpoint 4: Last non-system message          ─┘
```

### 工作原理

`apply_anthropic_cache_control()`函数会对消息内容进行深度复制，并注入`cache_control`标记：

```python
# Cache marker format
marker = {"type": "ephemeral"}
# Or for 1-hour TTL:
marker = {"type": "ephemeral", "ttl": "1h"}
```

根据内容类型的不同，标记的添加方式也有所差异：

| 内容类型 | 标记的放置位置 |
|-----------|--------------|
| 字符串内容 | 会被转换为 `[{"type": "text", "text": ..., "cache_control": ...}]` 的格式 |
| 列表内容 | 会添加到列表中最后一个元素的字典里 |
| 无/空内容 | 以 `msg["cache_control"]` 的形式添加 |
| 工具消息 | 以 `msg["cache_control"]` 的形式添加（仅适用于原生 Anthropic 平台） |

### 具有缓存意识的设计模式

1. **稳定系统提示词**：系统提示词为第一个断点，并会在所有对话轮次中保持缓存。请避免在对话进行过程中修改它（压缩功能仅在首次压缩时添加备注）。

2. **消息顺序至关重要**：缓存命中依赖于前缀匹配。如果在中间添加或删除消息，将会使之后的所有内容缓存失效。

3. **压缩缓存交互机制**：经过压缩后，被压缩区域的缓存会失效，但系统提示词缓存依然有效。通过3条消息的滚动窗口，通常在1-2轮对话后即可重新建立缓存。

4. **TTL设置选项**：默认值为`5m`（5分钟）。对于那些用户会在各轮对话之间暂停较长时间的长时间会话，可设置为`1h`。

5. **模型标识是缓存键的一部分**：提供商端的缓存仅针对处理请求的模型（以及账户/API密钥）生效。如果在对话过程中更换模型——无论是通过显式的`/model`指令、主模型回退机制，还是将凭证池切换到其他账户——那么后续请求将无法命中任何缓存，必须以全额输入成本重新读取整个对话历史。这是提供商端缓存机制的固有特性，Hermes无法避免；正因如此，关于`/model`指令、备用提供商及凭证池的用户文档都会包含相关费用警告。请勿开发会在会话过程中悄悄更换模型或凭证的功能。

### 启用提示词缓存

在以下情况下，提示词缓存会自动启用：
- 该模型为 Anthropic Claude 模型（可通过模型名称识别）。
- 该提供方支持 `cache_control` 功能（适用于原生 Anthropic API 或 OpenRouter）。

```yaml
# config.yaml — TTL is configurable (must be "5m" or "1h")
prompt_caching:
  cache_ttl: "5m"
```

在启动时，CLI会显示缓存状态：
```
💾 Prompt caching: ENABLED (Claude via OpenRouter, 5m TTL)
```


## 上下文压力警告

中间级别的上下文压力警告已被移除（详见 `agent/turn_iteration_prep.py` 文件中的迭代预算相关部分，其中说明：“不再提供中间级压力警告——因为这些警告会导致模型在处理复杂任务时过早放弃”）。当提示词token数量达到预设的 `compression.threshold` 值（默认为50%）且未触发任何前置警告时，系统会立即启动压缩机制；而作为第二道安全保障机制，当模型上下文窗口使用率达到85%时，系统则会触发会话清理功能。
