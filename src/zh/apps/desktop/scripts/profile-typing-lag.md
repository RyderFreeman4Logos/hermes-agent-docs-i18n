# 分析渲染器的输入延迟问题

用于实际测量并解决桌面端聊天编辑器中输入/提交延迟问题的工作流程。

> **备注（2026年7月）：** 本文档中提到的独立 `measure-*` / `profile-*` 脚本已被整合到 `scripts/perf/` 目录下的标准化性能测试工具集中（可通过 `npm run perf`、`npm run perf:serve` 调用）。如今，无论在何种测试场景下，CPU 分析都需通过 `--cpuprofile` 参数来实现。本文档仅作为问题排查记录保留；关于当前的工具集以及场景与旧脚本的对应关系，请参阅 `scripts/perf/README.md`。

## 快速启动性能分析功能

Vite 8 + plugin-react 6 存在一个已知问题：React Fast Refresh 的初始化脚本不会被注入到 `index.html` 中，因此当通过 `http://127.0.0.1:5174` 启动 Electron 应用时，每个 TSX 模块都会出现 “$

```bash
# Terminal A — start dev server without HMR
cd apps/desktop
node scripts/dev-no-hmr.mjs

# Terminal B — start Electron with CDP exposed
cd apps/desktop
XCURSOR_SIZE=24 HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174 \
  ../../node_modules/.bin/electron --remote-debugging-port=9222 .
```

终端 C 可供您用来运行各种工具包。

## 工具包

全部为无依赖实现——基于 Node 24 自带的 `WebSocket` 和 `fetch` 技术。

### 打字延迟 — `measure-latency.mjs`

可测量每次按键从 `keypress` 发生到画面更新完成的延迟，支持显示 p50、p90、p99 及最大值等统计指标。
该工具通过 `Input.dispatchKeyEvent` 来模拟按键操作，从而确保实验结果的可重复性。

```bash
node apps/desktop/scripts/measure-latency.mjs --chars=120 --cps=20
```

任何超过16毫秒的数值都属于掉帧情况。在刚刚加载的测试会话（`scripts/click-session.mjs 'Phaser particle'`）中，我们观察到的数据如下：

| | 未应用补丁 | 已应用补丁 |
|---|---|---|
| p50绘制时间 | 1.9毫秒 | 2.0毫秒 |
| p90绘制时间 | 3.3毫秒 | 13.7毫秒 |
| p99绘制时间 | 16.7毫秒 | 15.2毫秒 |
| 最长绘制时间 | 20.5毫秒 | 30.4毫秒 |
| 超过16毫秒的掉帧次数 | 2/120 | 1/120 |

即便在快速测试会话中，两者的表现也大致相当——因为在理想的模拟输入条件下，现有的系统响应速度已经足够快，所以补丁无法进一步降低输入延迟。真正的优势体现在内存泄漏检测功能上（见下文）。如果用户反馈输入时有卡顿现象，可在其实际使用过程中捕获性能分析数据及堆内存差异，再与模拟测试的基准值进行对比，从而找出导致处理速度变慢的具体原因（如长线程、弹出窗口开启、粘贴操作等）。

### 内存泄漏检测工具 — `leak-typing.mjs`

该工具每轮输入N个字符后会清除相关数据、强制触发垃圾回收，并记录`Performance.getMetrics`中的数值变化。通过这些数据，可以识别出泄露的事件监听器、堆内存异常增长、文档节点数量增加以及强制布局操作的次数。

```bash
# After clicking into a real session (e.g. via click-session.mjs):
node apps/desktop/scripts/leak-typing.mjs --rounds=8 --chars=200 --cps=50
```

**实时会话数据（Phaser线程，8轮 × 200字符）：**

| | 未打补丁版本（HEAD~2） | 已打补丁版本（HEAD） |
|---|---|---|
| 每轮js监听器数量变化 | +0 | +0 |
| 每轮DOM节点数量变化 | +0 | +0 |
| 每轮堆内存增长量 | 约0（得益于V8的内存管理机制） | 约0 |
| **强制布局次数/字符数** | **7.02次** | **2.35次**（减少3倍） |

强制布局次数是衡量性能负担的关键指标——在未打补丁的版本中，每输入一个字符就会触发约7次布局操作（包括scrollHeight的读取、CSS变量值的写入以及FadeText的scrollWidth读取等操作共同叠加所致）。打补丁后这一数值降至约2.35次/字符，这已是Blink引擎对于每个字符长度为1px的可编辑内容所产生的自然性能开销，若不进行架构层面的调整，该数值无法进一步降低。

我在首次测试未打补丁版本时发现的“每轮监听器数量增加35个”的现象，实际上只是短暂的启动阶段现象（如弹出窗口的初始化等）；在稳定状态下，无论是打补丁前还是打补丁后，监听器数量均无变化。

### CPU性能分析 + 堆内存快照 — `profile-typing.mjs`

该脚本可在输入内容时记录CPU性能分析数据，同时生成输入前后的堆内存快照，便于在Chrome DevTools的“内存”标签页中进行对比分析。

```bash
node apps/desktop/scripts/profile-typing.mjs \
  --chars=400 --cps=30 --out=/tmp/hermes-typing
# → /tmp/hermes-typing.cpuprofile  (open in Chrome DevTools Performance)
# → /tmp/hermes-typing.before.heapsnapshot
# → /tmp/hermes-typing.after.heapsnapshot
```

正在加载 CPU 分析文件：可通过 Chrome DevTools → Performance 标签页拖入对应文件，或直接在 VS Code 中打开 `.cpuprofile` 文件。

如需查看堆内存差异，请依次操作：Chrome DevTools → Memory → Load snapshot，先加载“之前”的状态，然后切换到 Comparison view，再加载“之后”的状态。按 `# Delta` 字段对结果进行排序。同时需注意检查是否存在脱离的 DOM 元素、已卸载的 FiberNodes，以及监听器数量的增长情况。

## 辅助工具

- `probe-renderer.mjs` —— 输出页面状态信息（URL、composer 是否已加载、正文内容）
- `click-session.mjs <title>` —— 根据标题的部分匹配内容点击侧边栏中的对应会话
- `reload-renderer.mjs` —— 通过 CDP 强制触发 Page.reload（不支持热重载）
- `dump-state.mjs` —— 输出更详细的状态信息（线程消息数量、粘性会话等）
- `probe-console.mjs` —— 输出最近的控制台错误与异常信息

## 分析结果

有关 `apps/desktop/src/app/chat/composer/index.tsx` 的修改，可查看对应的提交信息。共有三项更改：

1. **移除了每次按键时读取 `scrollHeight` 的操作。** 之前的扩展 useEffect 会在每次内容草稿发生变化时都读取 `editorRef.current.scrollHeight`（这会导致同步布局），现已改为使用 `draft.length > 60` 这一判断规则；若该规则未能捕捉到某些变化，则由 ResizeObserver 来处理。

2. **对 CSS 自定义属性的写入操作进行了分组处理。** 之前的 `syncComposerMetrics` 会在每次检测到尺寸变化时都执行 `setProperty('--composer-measured-height', height + 'px')` 操作，从而导致整个页面的计算样式失效。现在只有在高度变化超过 8 px 的阈值时才会进行写入，因此在该固定高度的输入行中输入内容时完全不会导致样式失效。

3. **移除了无效的 `$composerDraft` → `aui.composer().setText` 循环调用。** 经过 grep 验证，除 composer 组件外并无其他代码订阅 `$composerDraft` 变量。之前用于将草稿内容推送到存储层以及从存储层同步回 composer 组件的两个 useEffect 实际上只是每次按键时的纯冗余操作。此外，`reconcileComposerTerminalSelections` 函数也曾在每次按键时被调用，现在可将其延迟到内容提交时再执行——该函数属于过时数据清理操作，并非用于保证正确性（因为在提交时会直接读取当前文本，而忽略过期的标签信息）。

4. **当草稿内容中不存在 `@`/`/` 字符时，`refreshTrigger` 会立即终止操作。** 之前即使草稿中不存在触发字符，`textBeforeCaret()` 函数仍会在每次按键时执行 `range.toString()` 操作（时间复杂度为 O(n)）。

其中最显著的优化效果来自第 3 点中提到的监听器泄漏问题——若没有这一改进，每次输入都会导致约 35 个事件监听器持续泄漏，直到达到稳定状态。

## 提交 / TTFT 延迟问题（待解决）

有用户反馈在按下回车键之后、助手开始输出内容之前会出现明显的延迟现象。`scripts/measure-submit.mjs` 脚本用于测量从“按下回车”到“composer 清空”、“用户消息渲染完成”以及“首次绘制”的整个时间间隔。该脚本会触发真实的提示提交操作，因此请在临时测试会话中使用，CI 环境中暂未启用此功能。

## 流式输出“5fps”问题调查（2026 年 5 月 21 日）

有用户抱怨称：“流式输出的输出帧率似乎只有 5 帧左右？哈哈”——在处理较长内容的对话时，助手的流式输出会出现卡顿现象。

### 新增的工具

- **`src/app/chat/perf-probe.tsx`** —— 仅用于开发阶段的副作用导入文件（在 `main.tsx` 中通过 `import.meta.env.MODE !== 'production'` 条件进行保护）。该文件向 `window` 对象添加了两个辅助函数：
  - `__PERF_PROBE__` —— React 的 `<Profiler>` 记录器。由于当前 Vite 正在提供生产环境版本的 React 构建产物（详见下文的“Vite 开发构建问题”），该功能暂时处于闲置状态；待该问题解决后将重新启用。
  - `__PERF_DRIVE__` —— 人工生成的流式数据驱动器。它会以固定频率将数据项推送到实时的 `$messages` 原子变量中，这样助手界面运行时、增量存储系统、Streamdown Markdown 渲染器以及 React 提交处理流程就能接收到与真实大型语言模型流式输出相同的工作负载——只不过无需调用真实的大语言模型，也不会产生任何费用。
- **`scripts/measure-synthetic-stream.mjs`** —— 负责驱动 `__PERF_DRIVE__`，同时记录 rAF 帧间隔、`PerformanceObserver({entryTypes:['longtask']})` 捕获的长时间任务记录，以及实时消息更新频率，并可选地测量流式输入时的按键延迟。
- **`scripts/profile-synthetic-stream.mjs`** —— 在人工生成的流式输出过程中采集 CPU 使用情况，生成 `.cpuprofile` 文件（可在 Chrome DevTools 的 Performance 面板中打开），并输出前 30 个最高耗时函数的列表。
- **`scripts/measure-real-stream.mjs`** —— 与人工生成流式测试使用的工具类似，但会发送真实的 LLM 提示。当您拥有足够的调用额度且希望验证人工生成的测试结果是否准确时，可使用此脚本。
- **`scripts/profile-real-stream.mjs`** —— 在真实 LLM 流式输出过程中采集 CPU 使用情况。

辅助工具还包括：`scripts/eval.mjs`（用于一次性执行 CDP 评估操作），以及 `scripts/reload.mjs`（通过 CDP 强制重新加载渲染器）。

### 分析结果

测试在 Cloud Shadows 会话（7 轮对话，滚动高度约 11k px）以及大小为 34 MB 的会话 `session_20260514_215353_fe0ac8.json`（包含 110 个 FadeText 实例及大量历史工具调用记录）上进行。

| 指标 | Cloud Shadows 会话 | 34 MB 会话 |
|---|---|---|
| 平均帧率（60 个标记/秒，5 秒测试时长） | 60.0 | 58.6 |
| 帧率的 p50 / p95 / p99 值（毫秒） | 16.7 / 18.0 / 21.1 | 16.6 / 25.6 / 31.4 |
| 最高帧率（毫秒） | 31.1 | 97-127（数值随测试内容变化） |
| 每 5 秒窗口内的长时间任务数量 | 0 | 1-2，耗时 75-127 毫秒 |
| 流式输入时的 p95 延迟（毫秒） | 17 | — |

在 Cloud Shadows 环境下，一次使用 gpt-4o-mini 模型的真实流式输出测试（测试窗口时长为 39 秒）共产生了 12 个长时间任务，总耗时为 1.26 秒——这一频率与人工生成的测试结果一致（大约每 3.25 秒出现一次卡顿，最长卡顿时间不超过 123 毫秒）。因此，**人工生成的流式测试结果能够真实反映真实场景下的表现**，无需支付额外标记费用即可用于持续优化代码。

### 流式输出过程中的 CPU 使用情况分析（人工生成内容，Markdown 格式）

在 5 秒测试窗口内，按耗时从高到低排序的前几大功能模块如下（基于 400 个标记、处理速度为 125 个标记/秒的假设，且内容为 Markdown 格式）：

| 毫秒（自身耗时） | 函数名 | 所属文件 |
|---|---|---|
| 260 | `bn$长任务数量及最大长任务时长保持不变——`useDeferredValue`并不会降低CPU使用率，仅会调整其执行优先级。平均帧率提升以及p99帧丢失率的改善，恰恰证明了现有的CPU已不再成为限制60帧/秒刷新率的瓶颈：由于React能够推迟文本解析，因此帧率依然稳定。有一次测试甚至记录到了**MUTATIONS=0**——React跳过了所有中间文本状态，仅保存最终状态，这正是`useDeferredValue`功能的典型表现。

### 尚未解决的问题：Streamdown的Markdown重新解析开销（最棘手的难题）

在每5秒的时间窗口内，micromark/mdast/hast处理流程所消耗的总CPU时间仍约为700毫秒。虽然使用了`useDeferredValue`后该操作不再阻塞输入，但若查看CPU性能分析报告，仍会看到那些高负载函数（如`Tn$
