# 桌面性能测试工具

这是一种系统化的方法，用于衡量桌面渲染/交互性能，将其与已确定的基准值进行对比，并在出现性能退化时触发告警。它取代了此前那些零散存在的 `measure-*` / `profile-*` 脚本——这些旧脚本各自独立实现 CDP 客户端、参数解析、数据统计及结果输出功能，且从未建立过统一的基准值。

## 快速开始

```bash
# Isolated instance (recommended) — no running app or LLM credits needed.
# Its own --user-data-dir + HERMES_HOME means it never collides with `hgui`.
npm run perf -- --spawn

# Or: launch an isolated instance once, attach repeatedly (faster iteration).
npm run perf:serve            # leaves an instance on :9222
npm run perf                  # attaches, runs the CI suite, gates on baseline

# One scenario, with a CPU profile:
npm run perf -- stream --cpuprofile --tokens 800

# Representative PRODUCTION numbers (minified React, not the ~3x-slower dev build):
npm run perf -- cold-start stream keystroke transcript --spawn --prod

# Re-capture the baseline on your reference device, then commit baseline.json:
npm run perf -- cold-start stream keystroke transcript --spawn --prod --update-baseline
```

## 开发环境与生产环境

默认情况下，该工具会检测**开发环境**下的渲染器（启动速度快，适合进行相对回归测试）。若需构建包含探针功能的生产环境渲染器（并设置 `VITE_PERF_PROBE=1`）以检测经过压缩处理的 React 代码——即实际部署时的性能数据，则需使用 `--prod`（配合 `--spawn` 参数）。通过 `--prod` 可获取已提交的基准性能数据。

## 为何隔离机制至关重要

过去，该工具旨在执行的性能测试一直无法实现：正在运行的 `hgui` 会占用 Electron 的单实例锁，导致第二个实例立即被强制关闭。而使用 `--spawn` / `perf:serve` 启动时，每个实例都会拥有独立的 `--user-data-dir`（独立的锁机制）、独立的 `HERMES_HOME`（独立的后端及会话管理），以及独立的 `--remote-debugging-port`。此外，合成测试场景会通过 `window.__PERF_DRIVE__` 直接触发 `$messages` 的生成，因此无需消耗大型语言模型的调用额度。

## 测试场景

| 场景 | 等级 | 指标 | 替代指标 |
|---|---|---|---|
| `stream` | ci | 流式长任务处理时间、帧处理时间 p95/p99 值、数据变更频率 | measure-synthetic-stream、profile-synth-stream、profile-long-stream |
| `stream --real` | backend | 同上，但数据来自真实的大语言模型流 | measure-real-stream、profile-real-stream |
| `keystroke` | ci | 输入法按键操作到内容显示的延迟时间 | measure-latency、profile-typing、leak-typing |
| `transcript` | ci | 大容量文本加载时间以及内容显示所需成本 | （新指标） |
| `render-churn` | ci | 各组件渲染耗时情况，以及在多标签页同时加载时的应用留存率 | （新指标） |
| `idle-cost` | report | 界面处于活跃状态但无操作时的情况：空闲操作频率，以及调整大小/输入文字时的帧率 | （新指标） |
| `right-pane` | report | 文件树结构，以及聊天/终端输出下方永久显示的 xterm 标签页，还包括界面分割拖动功能 | （新指标） |
| `cold-start` | cold | 应用启动 → CDP 初始化 → 驱动程序加载 → 首次内容显示（全新启动/运行场景） | （新指标） |
| `first-token` | backend | 按下回车键后，首个助手生成文本的显示时间（TTFT） | （新指标） |
| `submit` | backend | 按下回车键后输入内容被清除，直至用户消息显示并出现滚动跳转的整个过程 | measure-submit、measure-jump |
| `session-switch` | backend | 路由切换 → 首次内容显示 → 状态稳定 | profile-session-switch |
| `session-load` | backend | 首次内容显示后，会话相关文本向后的滚动距离 | （新指标） |
| `profile-switch` | backend | 点击侧边栏栏轨后，侧边栏内容的显示状态 | measure-profile-switch |
`ci` + `cold` 类型的测试场景无需后端支持或积分，且受 `baseline.json` 的限制（由于 `cold-start` 需要测量全新启动状态，因此必须使用 `--spawn` 参数，并在独立的调用过程中执行）。而 `backend` 类型的测试场景则需要运行中的后端支持（以及 `--spawn` 参数或真实的会话/积分），且仅用于生成报告。

CPU 性能分析是通过通用的 `--cpuprofile` 参数实现的，该参数适用于所有类型的测试场景（它会将整个运行过程封装在 `Profiler.start/stop` 函数中，并输出各函数的耗时排名表），从而取代了原有的所有独立 `profile-*` 脚本。

## 添加测试场景

首先创建名为 `scenarios/<name>.mjs` 的文件，其中需导出 `{ name, tier, description, run(cdp, opts) }` 对象，其中 `run` 函数会返回 `{ metrics, detail }` 对象（`metrics` 为数值指标，数值越低表示性能越好），随后将该文件注册到 `scenarios/index.mjs` 中。如果是 `ci` 类型的场景，则还需添加一个 `baseline.json` 条目（或执行 `--update-baseline` 命令）。

## 文件结构

- `lib/cdp.mjs` — 包含 CDP 客户端实现、目标检测功能、类型推断功能、CPU 性能分析封装以及 DOM 选择器。
- `lib/stats.mjs` — 用于处理百分位数计算、直方图生成以及 CPU 性能分析结果的排名功能。
- `lib/baseline.mjs` — 负责加载、比较及更新基准数据，同时实现回归检测功能。
- `lib/launch.mjs` — 用于附加已存在的实例，或启动一个完全隔离的新实例。
- `scenarios/` — 每个测量指标对应一个模块。
- `run.mjs` — 程序的入口点。`serve.mjs` — 独立的启动工具。

## 未迁移（作为开发工具保留）

`eval.mjs`、`reload.mjs`、`reload-renderer.mjs`、`probe-renderer.mjs`、`probe-thread.mjs`、`click-session.mjs`、`diag-*.mjs` 等均为交互式开发辅助工具，而非性能测试基准。未来这些工具可逐步采用 `lib/cdp.mjs` 的功能。
