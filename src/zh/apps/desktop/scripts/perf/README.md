# 桌面性能测试工具

这是一种系统化的方法，用于测量桌面渲染/交互性能，将其与已确定的基准值进行对比，并在出现性能退化时触发告警。它取代了此前那些零散存在的 `measure-*` / `profile-*` 脚本——这些旧脚本都需重新实现 CDP 客户端、参数解析、统计功能以及输出格式，而且根本不存在基准值概念。

## 快速入门

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

默认情况下，该工具会检测**开发环境**下的渲染器（启动速度快，适合进行相对回归测试）。若需构建包含探针功能的生产环境渲染器（设置 `VITE_PERF_PROBE=1`），并测量经过压缩的 React 代码——即实际部署后的性能数据，则需使用 `--prod`（配合 `--spawn` 参数）选项。通过 `--prod` 可以捕获已提交的基准性能数据。

## 为何需要隔离机制

该工具旨在执行的性能测试在以往往往无法实现：正在运行的 `hgui` 会占用 Electron 的单实例锁，导致第二个实例立即被强制关闭。而 `--spawn` / `perf:serve` 选项则会各自使用独立的 `--user-data-dir`（独立的锁机制）、独立的 `HERMES_HOME`（独立的后端及会话管理），以及独立的 `--remote-debugging-port`。此外，合成测试场景会通过 `window.__PERF_DRIVE__` 直接触发 `$messages` 的生成，因此不会消耗任何大语言模型额度。

## 测试场景

| 场景 | 等级 | 测量指标 | 替代的原有脚本 |
|---|---|---|---|
| `stream` | ci | 长时间任务的流式处理情况、帧率 p95/p99 值、数据更新频率 | measure-synthetic-stream、profile-synth-stream、profile-long-stream |
| `stream --real` | backend | 与上述相同，但基于真实的大语言模型流输出 | measure-real-stream、profile-real-stream |
| `keystroke` | ci | 输入字符到内容显示的延迟时间 | measure-latency、profile-typing、leak-typing |
| `transcript` | ci | 大容量文本加载后的显示成本 | （新添加） |
| `cold-start` | cold | 应用启动 → CDP 初始化 → 驱动程序加载 → 首次内容显示（全新启动/运行） | （新添加） |
| `first-token` | backend | 输入字符后首次生成助手响应的时间（TTFT） | （新添加） |
| `submit` | backend | 输入内容并确认发送后，用户消息的显示及页面滚动跳转情况 | measure-submit、measure-jump |
| `session-switch` | backend | 路由切换后到首次内容显示及状态稳定所需时间 | profile-session-switch |
| `profile-switch` | backend | 点击导航栏后侧边栏状态恢复所需时间 | measure-profile-switch |

`ci` 类型和 `cold` 类型的测试场景无需后端支持或消耗模型额度，其运行结果会与 `baseline.json` 中的基准数据进行比对（`cold-start` 场景由于需要检测全新启动情况，必须使用 `--spawn` 选项，并且需在独立的测试进程中运行）。而 `backend` 类型的测试场景则需要实时运行的后端支持（以及 `--spawn` 选项或真实的会话/模型额度），仅用于生成报告。

在任何测试场景中，都可以通过通用的 `--cpuprofile` 参数进行 CPU 性能分析（该参数会使用 `Profiler.start/stop` 包装整个测试过程，并输出各函数的耗时排名表），从而替代所有独立的 `profile-*` 脚本。

## 添加新测试场景

首先创建名为 `scenarios/<name>.mjs` 的文件，其中需导出 `{ name, tier, description, run(cdp, opts) }` 对象，其中的 `run` 函数应返回 `{ metrics, detail }` 对象（`metrics` 为数值型指标，数值越低越好），随后将该文件注册到 `scenarios/index.mjs` 中。如果是 `ci` 类型的场景，还需添加对应的 `baseline.json` 条目（或执行 `--update-baseline` 命令）。

## 文件结构

- `lib/cdp.mjs` —— 包含 CDP 客户端功能、目标检测、输入处理、CPU 性能分析以及 DOM 选择器相关功能。
- `lib/stats.mjs` —— 负责处理百分位数计算、直方图展示以及 CPU 性能分析结果的排序。
- `lib/baseline.mjs` —— 用于加载、比较及更新基准数据，同时作为回归测试的判定依据。
- `lib/launch.mjs` —— 负责附加到现有实例，或启动完全隔离的新实例。
- `scenarios/` —— 每个独立的性能测量功能对应一个模块。
- `run.mjs` —— 程序的入口文件。`serve.mjs` —— 独立的隔离式启动工具。

## 未迁移的项目（仍作为开发工具保留）

`eval.mjs`、`reload.mjs`、`reload-renderer.mjs`、`probe-renderer.mjs`、`probe-thread.mjs`、`click-session.mjs`、`diag-*.mjs` 等均为交互式的开发辅助工具，而非性能测试脚本。未来这些工具可能会集成 `lib/cdp.mjs` 的功能。
