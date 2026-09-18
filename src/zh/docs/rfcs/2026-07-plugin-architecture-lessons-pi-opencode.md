# 研究分析：从Pi和OpenCode中汲取的插件架构经验

**相关问题：** #64180 · **关联议题：** #64164（事件总线）、#64161（流式钩子）、#64162（可插拔审批机制）、#64165（清单格式v2）、#64229（生命周期/账本系统）、#64230（插件诊断工具）

**研究方法：** 本研究直接从源代码层面对这两个系统进行了分析（通过固定某个提交版本的浅层克隆），而非仅参考官方文档。所分析的系统包括Pi（原项目名`badlogic/pi-mono`，现名为`earendil-works/pi`），其对应版本为`eb79351`，版本号为v0.80.7，发布时间为2026年7月14日；另一系统为OpenCode（原项目名`sst/opencode`，现名为`anomalyco/opencode`），对应版本为`c69abee`，版本号为v1.18.2，发布时间为2026年7月16日）。文中所有引用均标注了对应提交版本中的文件及行号。对于那些无法找到的内容（如地址定义、策略规则、超时设置等），则通过搜索予以确认，并将其作为研究结果予以记录。在整个分析过程中，#64182中规定的Hermes基本原则——仅允许功能叠加、严格保护提示缓存、以观察者模式为核心、采用失败即关闭的安全机制——被视作具有优先约束力的标准；本报告依据“借鉴而非复制”的评估准则，对这些系统中的设计模式进行了符合性评估。

**核心结论：** 在Hermes目前关注的四大设计维度上，这两个系统呈现出近乎完全对立的特征，这一特性使得它们成为理想的对照实验对象。

| 维度 | Pi | OpenCode | Hermes 的相关提案 |
|---|---|---|---|
| 每个数据变更的流式钩子 | 支持——以内联方式等待处理，无超时限制 | 完全不存在（仅支持文本结束触发） | 每个数据变更一个观察者 + 非阻塞契约（#64161） |
| 否决机制的语义 | 每个事件的结果都有类型定义（`{block}`、`{cancel}`、`"handled"`） | 通过抛出异常实现否决（无法区分错误与策略拒绝） | 尚待确定，见 #64162 |
| 钩子函数失败处理 | 直接终止（仅支持 `tool_call`） | 完全没有运行时隔离机制 | 基本原则 4：与安全相关的操作必须直接终止 |
| 插件事件总线 | 支持——包含 33 条通道，且**无命名空间** | 不存在（插件只能观察核心总线，无法发送消息） | 将引入带命名空间的 `ctx.emit`/`ctx.subscribe`（#64164） |

这两种系统均没有钩子超时机制，也因此都出现过因长时间挂起或状态漂移导致的故障。这是 Hermes 学到的最重要的跨领域经验教训。

---

## 1. Pi（badlogic/pi-mono → earendil-works/pi）

其扩展功能为进程内的 TypeScript 模块（通过 jiti 加载），这些模块会接收到 `ExtensionAPI` 接口；不存在独立进程、无进程间通信机制，也不需要清单权限。Pi 明确拒绝采用 MCP 作为扩展机制（参见 Zechner 的文章《如果根本不需要 MCP 呢？》[https://mariozechner.at/posts/2025-11-02-what-if-you-dont-need-mcp/]）。值得注意的是，Pi 最初秉持“极简、无钩子”的理念（2025 年 11 月），但在大约 7 个月后便转向了拥有 33 种事件的扩展系统——因为用户的可扩展性需求占了上风，而“不使用 MCP”的原则则得以保留。

### 1.1 钩子/事件分类体系

共有33种事件类型（位于 `src/core/extensions/types.ts:507-902`）。其设计理念是：**每一种会触发状态变更的事件都会拥有独立的类型化发射器以及专属的结果格式**，而非使用通用的中间件处理流程——

- `tool_call` → `{ block: true, reason }`；参数会在原处直接修改，并明确规定“修改完成后无需再次验证”（参见 `docs/extensions.md:742-765`）；
- `session_before_*` → `{ cancel: true }`，最先注册的取消处理函数优先生效，后续注册的将被跳过；
- `input` → 表示“已处理”的值为 `"handled"`（直接终止处理流程），而表示“需进一步处理”的值为 `"transform"`（进入处理链）（参见 `runner.ts:1148-1188`）；
- `tool_result`：各处理函数会逐步累积部分更新结果（参见 `runner.ts:835-883`）；
- `before_agent_start`：用于实现系统提示语的链式处理，且会通过实时调用的 `ctx.getSystemPrompt()` 反映之前所有处理函数的执行结果（参见 `runner.ts:1034-1098`）；
- 观察者事件**完全不存在返回通道**——事件是通过何种发射器传递来决定其属于观察者还是状态修改器，而非依赖某种约定。

事件分发采用完全顺序式的异步处理方式（参见 `runner.ts:759-791`）：每个处理函数会依次被等待执行；唯一的排序规则为扩展模块的加载顺序（项目级 → 全局级 → CLI级，参见 `loader.ts:660-708`），其次是注册顺序。系统中不存在优先级或处理阶段的概念——在过去的8个月里，社区也并未提出过相关需求。对于名称冲突的处理，则是依据各个注册表制定的明确确定性规则，而非依赖关系解析机制：工具名称以先注册者为准；命令名称若重复则会在其后添加后缀（如 `name:2`）；快捷指令名称若重复则以后注册者为准，但系统会发出警告，并设置一个包含18个键的专用拒绝列表（参见 `runner.ts:421-604`）。

有两项值得借鉴的调度保障机制：扩展模块能够在用户界面渲染之前以及会话持久化之前获取事件信息（`agent-session.ts:596-601`）；同时，并行执行的同级工具调用会先按顺序进行预检，之后再同步运行（`docs/extensions.md:750`）。

### 1.2 插件间的交互机制

系统采用了一个共33行的共享事件总线（`src/core/event-bus.ts`）：支持在**任意字符串通道**上使用 `pi.events.emit/on` 方法——无需命名空间、无需声明、也不具备冲突检测功能；每个处理函数都配有 try/catch 机制以及用于取消订阅的闭包函数。为了简化设计，该系统刻意省略了更复杂的机制，如能力注册表和依赖管理等功能；至于未来是否需要通过扩展模块来实现更完善的协调功能，相关讨论已作为社区 RFC 提出，交由用户端自行处理（pi#2715）。

### 1.3 兼容性策略

该系统不采用 API 版本控制、握手机制或弃用标注。取而代之的是三种实用的处理方式：(a) 在加载器层面提供别名补丁，确保在 `@mariozechner` → `@earendil-works` 包名变更以及 pi-ai API 分拆过程中，旧的导入语句仍能正常工作，同时会提前公告这些补丁的移除时间（`loader.ts:47-71`；`CHANGELOG.md:243`）；(b) 在变更日志中明确标注**破坏性变更**，并为重大功能整合（如 hooks、customTools 向扩展模块的迁移，对应版本 v0.35-0.37）提供自动迁移功能，例如在程序启动时自动重命名目录、自动将会话格式从 v2 升级为 v3）；(c) 为旧版本的参数结构提供针对特定工具的 `prepareArguments()` 补丁。

有记录以来的真正严重故障：pi#2860——由于一次内部会话管理重构，导致`pi.sendUserMessage()`在`ctx.newSession()`之后悄悄丢弃消息。该问题的修复方式颇具特色：采用了**“过期上下文污染”**策略——在会话替换后，所有尝试获取上下文的函数都会抛出一段冗长的错误信息，引导开发者使用安全的`withSession`模式（相关代码见`runner.ts:514-527`；包含不安全模式的示例及说明见于`docs/extensions.md:1223-1265`）。其兼容性保障并非通过永不修改代码来实现，而是通过让错误行为更加明显来避免问题。

### 1.4 故障隔离

控制错误，而非控制时间：每个处理函数调用都会被独立地包裹在`try/catch`结构中，并在聊天界面中以红色堆栈跟踪形式展示；加载失败时仅会影响出问题的扩展程序，同时还提供了`pi -ne`命令作为无需使用扩展的应急方案。**唯一有意保留的例外情况**是：`tool_call`函数内部没有异常处理机制——如果守护钩子发生崩溃，将会阻止工具执行（显示“扩展程序故障，正在阻止执行”），此时该错误会被转换为LLM能够识别的工具执行结果；整体循环仍会继续运行，只是相关的守护逻辑会终止（相关代码见`runner.ts:885-906`；`agent-session.ts:454-467`；`agent-loop.ts:657-665`）。

**系统中不存在任何超时机制。**所有处理函数——包括按每个令牌处理的`message_update`函数——都在代理程序的事件处理流程中直接被异步等待（相关代码见`agent-session.ts:598, 728-734`）。如果某个扩展程序卡死，将会导致整个代理程序停滞；更新日志中记录了针对此类卡死问题的修复方案（如pi#5687中的后台处理机制，以及pi#5115中的关闭时资源清理功能）。目前可用的缓解措施均为协作式方案，例如通过`ctx.signal`的AbortSignal或Esc-abort命令来强制终止程序。

由于决策上的考量，该系统并未采用沙箱机制：“部分进程级沙箱很容易被误认为是安全边界”（参见 `docs/security.md:33-35`）；唯一的限制是在加载时需要项目信任授权。

### 1.5 设计历史记录

**Pi 并没有 ADR 文档**——引发此次讨论的 Discord 记录在 Pi 系统中并未得到证实。相关设计依据分散在四处：用户文档中的“注意事项”部分（实际上相当于内嵌的 ADR），一个包含 5,000 行内容的、与问题相关的变更日志（其中记录了已被废弃的设计方案，如 hooks 与 customTools 的分离、slash-commands 到 prompt-templates 的重命名，以及因 undici 派发器而废弃的 fetch-override 代理），Zechner 的博客，以及各类问题记录本身。

### 1.6 提示词/上下文构建

在所调研的所有系统中，只有 Pi 将**提示词缓存的稳定性视为扩展 API 合同的一部分**：扩展程序接收的是结构化的提示词输入（`systemPromptOptions`——与 Pi 自身使用的分解格式一致），而非最终的字符串；每次请求的上下文转换均通过 `structuredClone` 实现，从而确保会话历史不会被破坏；此外，从版本 0.80.6（pi#6474）开始，该系统采用了对缓存友好的动态工具加载机制，通过原生的提供者延迟加载功能（类似 Anthropic 的 `defer_loading`）以增量方式激活工具，从而明确避免使前缀缓存失效——同时相关文档还说明了因提示词元数据变化可能导致的二级缓存失效问题（参见 `docs/extensions.md:2254-2290`）。

---

## 2. OpenCode（sst/opencode → anomalyco/opencode）

服务器端（Bun/Effect）与客户端（TUI/桌面端/网页端）相结合；插件为 npm 包或直接在进程内加载的本地 TypeScript 文件，**一个包中可包含两种类型的插件**——即 `server` 和 `tui` 入口点，且必须二选一（参见 `shared.ts:103-114, 293-295`）。v2 版本的插件 API 与 v1 版并行存在（通过 `/v2/effect`、`/v2/promise` 等子路径访问），其设计细节记载在长达 516 行的 `PLAN.md` 文档中。

### 2.1 钩子/事件分类体系

异步工厂会返回一个包含各类钩子的对象（位于 `packages/plugin/src/index.ts:74, 222-335`）：约 16 个可修改数据的 `(input, output)` 钩子（可直接修改 `output` 的值，随后由主机读取该值），以及用于声明式注册的工具、认证机制和提供程序，此外还包含一个统一的 `event` 监听器。整个调度引擎仅由约 13 行代码构成（位于 `plugin/index.ts:280-293`）：按顺序执行、支持异步等待，后续注册的钩子会看到之前已完成的修改操作——具体的执行顺序有明确规范（“全局配置 → 项目配置 → 全局插件目录 → 项目插件目录”；v2 版则规定为“插件注册顺序，随后是转换函数注册顺序”）。

拒绝某项操作的方式是通过抛出异常来实现。文档中规定的拒绝工具调用的标准写法是 `throw new Error("Do not read .env files")`（参见 `plugins.mdx:247-257》）——对于下游的所有使用方而言，策略性拒绝与插件本身的缺陷是无法区分的。

**一个已定义但实际无法使用的钩子。** `permission.ask` 是唯一具备真正决策语义的钩子（`output.status: "ask" | "deny" | "allow"`），虽然存在于公开的类型定义中，但在整个架构树中**没有任何调度点**：权限子系统的重写导致它被孤立，类型定义仍能正常编译，而插件则只能默默地执行无操作（对应问题 oc#7006，自2026年1月开放）。这是整个测试项目中发现的最为严重的单点故障模式。

### 2.2 插件间的交互方式

不存在依赖关系、注册表或插件发布的事件。插件间的交互方式包括：(a) 通过共享的可变 `output` 进行盲目组合（各字段遵循“最后写入者胜”原则）；(b) 监听核心事件总线。2026版的核心事件总线本身功能较为复杂——采用事件驱动架构，具备持久性存储能力（使用SQLite，为每个聚合数据维护独立序列，支持幂等重放），还包含版本化的消息类型，以及**背压保护机制**：`allBounded` 会封装一个限流队列，当订阅者数量过多时，会通过 `SubscriberOverflowError` 向这些订阅者发送错误信号（位于 `packages/core/src/event.ts:152-164`）。插件则处于三层桥接结构的末尾部分（Effect流 → 全局事件发射器 → `event`钩子），其触发方式为**即发即忘**——异步观察者的拒绝处理会被视为未处理的Promise拒绝，主机错误路由系统无法察觉到这一情况（位于 `plugin/index.ts:251-258`）。

### 2.3 兼容性策略

采用同步版本控制机制（`opencode` = `@opencode-ai/plugin` = `@opencode-ai/sdk` 的版本均为 1.18.2），并设置了一道验证关卡：npm 插件可声明 `engines.opencode` 的语义化版本范围，该范围会在加载时进行检查（位于 `shared.ts:194-205`）——但此功能为插件可选，本地文件插件则完全无需遵守这一规定。系统会同时加载三代的模块格式；对于已被替代的包，会通过硬编码的 `DEPRECATED_PLUGIN_PACKAGES` 列表将其静默忽略。

社区的历史经验颇具参考价值：v1.14.42 版本——那是一次**修补版发布**——直接移除了整个 `api.command.*` TUI 命名空间，且并未设置任何弃用周期（参见 oc#26557）。在引发众多反馈后，开发者又在代码中重新添加了该废弃的兼容层（“为确保 v1 版插件能够正常初始化，暂时保留了旧的 `api.command` API，将在 v2 版中移除”，见 `tui.ts:87-120`）。目前整个项目中并不存在任何书面的弃用政策，这种“在争议出现后才补充兼容层”的做法实际上已成为默认流程。

### 2.4 故障隔离

边缘表现强劲，核心功能却存在缺陷。加载过程分为多个阶段（`install | entry | compatibility | missing | load`），每个阶段及插件均被独立隔离，同时还会向用户显示相关提示信息（`loader.ts:82-93`; `plugin/index.ts:215-249`）。运行时钩子**既没有异常捕获机制，也没有超时设置**：工具钩子中抛出异常会导致该工具调用失败（这是被明文允许的终止方式）；聊天/转换钩子中抛出异常则会中止当前轮次处理（虽会导致会话错误，但服务器仍可正常运行）；而程序**挂起则会使整个轮次永久停滞**——v2版本的计划文档在*延迟决策*部分明确列出了“转换超时”问题（`PLAN.md:507-510`）。启动时的递归调用也曾导致严重问题：某个插件在自身初始化过程中调用了SDK客户端，从而引发了启动死锁（oc#7741）。官方故障排查页面给出的首要建议便是“先尝试禁用所有插件”。

有两个值得借鉴的成熟设计方案：流式处理的主路径采用了**结构化保护机制**——根本不存在针对单个数据变更的钩子；文本处理钩子仅在`text-end`时刻触发一次（`processor.ts:512-524`）；此外，TUI运行时还具备作用域追踪的注册功能（通过`Proxy`封装的键映射API会自动记录每个插件的所有注册信息，从而实现高效的实时禁用功能），同时还设置了**严格的5秒资源释放时限**，所有清理操作都会在计时器的驱动下同步进行（`runtime.ts:122-226, 388-468`）。

### 2.5 设计历史记录

Hermes 并不采用 ADR 系统；不过 v2 版本的 `PLAN.md` 是个例外，其质量甚至优于大多数 ADR 档案——它指出了 v1 的缺陷（如返回的 hooks 集合、由 finalizer 触发的特殊情况），以契约形式明确了操作顺序，将可重放的 *transforms* 与实时的 *hooks* 分开处理，而且——最为关键的是——它还设有一个详尽的 **Deferred Decisions** 部分（包含类型化的错误模型及 transform 超时设置），而非试图用虚假的完成状态来掩盖问题。

### 2.6 提示词/上下文构建

插件可以干预每一层功能，但深层功能则被 `experimental.` 前缀所限制（如 `experimental.chat.system.transform`、`experimental.chat.messages.transform`、压缩提示词替换功能）——这体现了有意为之的双重稳定性保障策略：在操作边界进行拦截是稳定的，而直接重写上下文本身则不具备稳定性。目前尚未发现与 Pi 类似的缓存稳定性机制。

---

## 3. Hermes 的采用/调整/规避策略

评估标准依据 #64182 中的准则制定。“已验证”意味着相关提案已在 Hermes 问题跟踪系统中，且有实际使用案例作为独立证据予以确认。

| # | Lesson | Verdict | Maps to | Evidence |
|---|---|---|---|---|
| 1 | **Typed per-hook result vocabularies, not veto-by-throw.** Pi's `{block, reason}` / `{cancel}` / `"handled"` enums vs OpenCode's throw-idiom (bug ≡ policy denial) and its dead `permission.ask`. Approval/gate hooks need enumerated results dispatched from the policy engine itself. | **Adopt** | #64162 | Pi runner.ts:759-1188; oc plugins.mdx:247-257, oc#7006 |
| 2 | **Guard hooks fail closed; observers fail open.** Pi contains every handler error except `tool_call`, whose crash blocks the tool with an LLM-visible error result. Independently confirms ground rule 4 — and refines it: the failure mode of a *crashed* security hook must also be closed, not just its config default. | **Adopt** (validated) | #64162, #64204 | Pi agent-session.ts:454-467, agent-loop.ts:657-665 |
| 3 | **Hook wire-up drift is the killer bug class: CI-check that every declared hook has a live dispatch site.** OpenCode's `permission.ask` sat typed-but-dead for 6+ months after a subsystem rewrite. Hermes already stores unknown hook names for forward compat (`register_hook`, plugins.py ~L1158) — the same drift is possible. A `VALID_HOOKS` ↔ `invoke_hook(` cross-check is a one-file test. | **Adopt now** (cheap, standalone) | #64230 (Doctor), CI | oc index.ts:261 + absent trigger site, oc#7006 |
| 4 | **Deadline budgets on plugin callbacks — be the first framework to have them.** Neither system times out runtime hooks; both shipped hang-class failures (pi#5687/#5115; oc#7741, "Transform timeouts" deferred twice). OpenCode's own TUI dispose path (hard 5s, per-cleanup timer race) proves the mechanism is practical. Observer hooks: enforce a budget and log-and-drop. Mutating/guard hooks: budget + fail per lesson 2. | **Adopt** (differentiator) | #64161, #64164, #64229 | Pi grep: zero timeout logic; oc PLAN.md:507-510, runtime.ts:122-226 |
| 5 | **Per-delta streaming hooks are viable only if non-blocking is structural, not documentary.** The controlled experiment: Pi offers per-delta and awaits inline → slow observer throttles the visible stream, hangs freeze it; OpenCode offers nothing per-delta → hot path safe, TTS use case unserved. #64161's "never-block contract + buffered-queue helper" is the right middle — but make the bounded queue the *only* consumption path (drop/coalesce policy included, cf. OpenCode's `SubscriberOverflowError` dropping queue), not an optional convenience next to a raw sync callback. | **Adapt** | #64161 | Pi agent-session.ts:728-734; oc processor.ts:512-524, event.ts:152-164 |
| 6 | **The namespaced bus proposal is ahead of both systems — proceed, with their two omissions fixed.** Pi's bus works but has arbitrary un-namespaced string channels and no discoverability; OpenCode has no plugin-emit at all. #64164's `<plugin_key>:` enforcement, reserved `hermes:` prefix, advisory declarations, recursion cap, and deterministic subscription order have no counterexample in the field. Carry over per-callback isolation (both systems do this right) and add lesson-4 budgets. Fire-and-forget with return-values-ignored matches both systems' stable practice. | **Adopt own design** (validated) | #64164 | Pi event-bus.ts (whole file); oc plugin/index.ts:251-258 |
| 7 | **Load order as the only priority system; explicit per-registry collision policies.** Zero configuration, deterministic, and no field demand for priorities in either ecosystem. Document Hermes's ordering as a spec the way OpenCode's PLAN does; pick a collision rule per registry (Pi: first-wins tools / suffixed commands / reserved denylist) instead of building dependency resolution. | **Adopt** | #64164, #64229 | Pi loader.ts:660-708, runner.ts:421-604; oc PLAN.md:144-146 |
| 8 | **Host-enforced compat gate + written deprecation window; migration tooling over semver ceremony.** OpenCode's `engines` gate is the right shape but plugin-opt-in only, and its patch-release API removal (oc#26557) shows lockstep versioning without policy is social, not mechanical. Pi shows the complement: loud breaking changes + automatic migrations + alias shims *before* removal. Manifest v2 should carry a host-checked `api_version` range; the repo should carry a one-paragraph deprecation policy. | **Adapt** | #64165, #64179 | oc shared.ts:194-205, tui.ts:87-120, oc#26557; Pi CHANGELOG:243, 3530-3620 |
| 9 | **Scoped registrations with auto-tracked disposal; poison stale contexts with teaching errors.** OpenCode's Proxy-tracked per-plugin scopes (clean live disable) and Pi's post-replacement context poisoning (silent race pi#2860 → loud self-documenting error) are the two halves of a robust lifecycle story — exactly what the #64229 ownership ledger needs. | **Adopt** | #64229 | oc runtime.ts:143-160; Pi runner.ts:514-527, docs:1223-1265 |
| 10 | **Prompt-cache stability as API contract is real and Pi proves it's implementable.** Structured prompt inputs instead of final strings, `structuredClone` for ephemeral transforms, additive-only tool activation with provider deferred loading, documented second-order invalidation warnings. Strongest possible validation of ground rule 2, with a concrete reference implementation for cache-safe injection. | **Adopt** (validated) | #64167 | Pi docs:2254-2290, CHANGELOG 0.80.6/pi#6474 |
| 11 | **Half-sandboxes: both systems refuse, for the same stated reason.** Pi documents that a partial in-process sandbox "would be easy to misunderstand as a security boundary"; OpenCode runs plugins fully privileged with path-containment only. Viable while plugin authors ≈ users; Hermes's Skills-Hub-style trust/scan pipeline is the nearer-term marketplace answer than in-process isolation. | **Adapt with eyes open** | security posture | Pi docs/security.md:5-37; oc shared.ts:89-97 |
| 12 | **Events to plugins before UI and before persistence; boot-stage the plugin-facing client.** Pi's explicit ordering guarantee removes a whole class of races; OpenCode's plugins-as-API-clients design is elegant but deadlocked startup when a plugin called the API mid-init (oc#7741) — if ctx ever grows client-like powers, stage them ("unavailable until ready"). | **Adapt** | #64178, #64229 | Pi agent-session.ts:596-601; oc plugin/index.ts:142-147, oc#7741 |
| 13 | **Neither system has ADRs — and both paid for it.** Pi's rationale is scattered across changelog/blog/footguns; OpenCode broke APIs in patch releases partly because no decision record said not to. Hermes's per-sub-issue design sketches (#64182 style) are already ahead of both; add an explicit **Deferred Decisions** section per design (OpenCode's PLAN.md's best feature) so open questions stay visible instead of silently unresolved. | **Keep + adapt** | process | verified ADR absence in both repos |

## 4. 已验证的缺失情况（属于问题发现，而非峰值检测中的间隔）

- **两个代码库中均无ADR记录**（已对整个代码库进行了`adr`/`decision`相关文档的搜索）。Discord中提到的“描述故障模式的ADR”在两个项目中也均未找到对应依据；最接近的类似内容为Pi项目的文档中的footgun部分，以及OpenCode项目的单个v2版本PLAN.md文件。
- **两个系统中均不存在运行时钩子超时问题**（已在Pi项目的`src/core/extensions/`目录中通过grep验证；OpenCode项目则通过其自身的计划机制避免了此类问题）。
- **两个代码库中均无关于功能废弃或插件API稳定性的书面政策。**
- 注意事项：Pi项目#2860议题中提到的问题解决因果关系是通过故障与修复之间的对应关系推断出来的，并非维护者明确声明；OpenCode项目在重写之前的历史版本未进行差异对比（仅进行了浅层克隆）；所引用议题中的维护者回复在获取的内容中无法查看。

---

*峰值检测的时间范围依据#64180确定。主要参考资料如下：`earendil-works/pi` @ `eb79351` — `packages/coding-agent/src/core/extensions/{runner,loader,types}.ts`, `src/core/{agent-session,event-bus}.ts`, `packages/agent/src/agent-loop.ts`, `docs/{extensions,security}.md`, `CHANGELOG.md`；`anomalyco/opencode` @ `c69abee` — `packages/plugin/src/{index,tui}.ts`, `packages/plugin/src/v2/effect/PLAN.md`, `packages/opencode/src/plugin/{index,shared,loader}.ts`, `packages/opencode/src/plugin/tui/runtime.ts`, `packages/core/src/event.ts`, `packages/web/src/content/docs/plugins.mdx`；相关议题包括pi#2860/#2715/#5080/#5687，oc#7006/#26557/#7741/#4850/#12222；以及mariozechner.at发布的文章（2025-11-02，2025-11-30）。*
