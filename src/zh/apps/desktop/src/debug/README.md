# 仅开发人员可用的状态诊断功能

针对任何交互操作，该功能通过两个计数器来回答以下问题：**哪些内容被重新渲染、为何重新渲染，以及是由哪个存储模块触发了这一操作？**

```
window.__RENDER_COUNTS__   what re-rendered, attributed to props / state / parent
window.__ATOM_CHURN__      which store published it, and whether it mattered
```

在调用 `start()` 之前，两者均处于闲置状态，因此每次提交和每次通知都会产生一个空操作分支的开销。此外，这两个功能都不会被默认启用：在非开发服务器构建场景下（或未设置 `VITE_PERF_PROBE=1` 时），`vite.config.ts` 会将 `@/debug/dev-only` 引用为一个空操作模块。

## 使用方法

当代理正在传输数据时，可通过开发者工具控制台进行操作：

```js
__RENDER_COUNTS__.start(); __ATOM_CHURN__.start()
// ...let it run for a few seconds...
__RENDER_COUNTS__.stop();  __ATOM_CHURN__.stop()
console.table(__RENDER_COUNTS__.report())
console.table(__ATOM_CHURN__.report())
```

其中每个条目中的`wasted`列即为修复清单：

- **render `wasted`** — 由于父组件触发而重新渲染，但既没有更改props，也没有改变hook状态。使用`memo()`或更严格的订阅机制即可消除这种情况。
- **atom `wasted`** — 发布的值与之前的值深度相等。`@nanostores/react`仅支持基于*引用*的相等性判断，因此会导致所有订阅者都进行不必要的重新渲染。这正是`apps/desktop/AGENTS.md`中规定的“无操作时保持引用身份不变”原则。

或者作为一种衡量标准：在没有任何后端支持且不消耗任何资源的情况下，人工生成5个同时运行的流式标签页。

```bash
node scripts/perf/run.mjs render-churn --spawn --tiles 5 --tokens 240
```

## 为何选择 bippy，而非其他显而易见的选择

**React 19.2 已从 react-dom 中移除了 `injectProfilingHooks`。** 经验证：
执行命令 `grep -c injectProfilingHooks node_modules/react-dom/cjs/react-dom-client.development.js`，结果为 `0`。此时仅剩下 `onCommitFiberRoot` 和 `onPostCommitFiberRoot` 两个选项。在该版本中，整个 `mark*` 系列的性能监控钩子（如 `component-render-start`、`state-update`、`render-scheduled`）均已失效——任何基于这些钩子开发的工具都将无法使用。

**`<Profiler>` 无法判断“侧边栏是否重新渲染了？”** React 会为已提交代码树中的每一个 Profiler 调用 `onRender` 方法，即便那些子树已经因为错误而停止处理。通过统计这些回调次数，反而会“证明”发生了实际上并未发生的重新渲染。`actualDuration` 也无法作为判断依据：出现错误的子树仍会返回一个非零的小数值，因此不存在安全的阈值标准。唯有 `didFiberRender` 才是可靠的信号。（注：文件 `app/chat/perf-probe.tsx` 中导出了一个名为 `PerfProbe` 的 Profiler 封装类，但实际上从未被使用——这就是原因所在。）

**react-scan** 在其未正式文档化的 `react-scan/lite` 子目录中提供了类似的理念，但该 “lite” 版本实际上只是一个非常轻量的封装，其导入的依赖仅限于 `bippy` 和 `bippy/source`。该包还引入了约 217 个间接依赖（如 babel、preact），并且会将 `react-grab`/`react-doctor` 维持在最新版本，因此安装结果不具备可重复性。此外，其主入口文件目前还会因 JSON 导入属性错误导致 Vite 错误（相关上游问题编号为 #448 和 #467，均处于未解决状态）。我们直接选择使用 bippy：它采用 MIT 许可协议，且没有任何依赖项。

## 导入顺序的限制

`main.tsx` 会在 **`react-dom` 之前**，以**静态方式**导入 `@/debug/dev-only`。这一操作是用于功能实现的核心代码，而非仅用于样式处理。

`react-dom` 会在**模块初始化阶段**捕获调试工具钩子，而非在 `createRoot` 时。如果在之后再安装该库，虽然钩子对象仍会存在，但 `bippy._renderers` 会为空，从而导致所有提交记录都无法被检测到。我们已对两种顺序进行了验证：

| 安装顺序 | `_renderers` 值 | 提交记录数 |
|---|---|---|
| 先安装 bippy | 1 | 1 |
| 先执行 `react-dom` | 0 | 0 |

如果在 `import.meta.env.DEV` 判断条件之后再使用动态 `import()`，则该导入操作会在 `main.tsx` 的静态依赖图（包括 `react-dom`）解析完成之后才会被执行——为时已晚。因此，应采用静态导入方式，而生产环境下的排除处理则通过构建时的别名来实现，而非依赖代码剪枝机制。

如果您要添加测试来检查这些计数器，请注意：`ui` vitest 项目中的 `setupFiles` 会在任何测试代码执行之前就引入 `@testing-library/react`（进而引入 `react-dom`），因此钩子根本无法在该环境中被安装。建议使用不包含 `setupFiles` 的配置。

## 基准配置（5个标签页 × 240个令牌，开发模式渲染器，darwin-arm64架构）

```
sidebar_renders          6
sidebar_wasted           0
wasted_renders      10,432
total_renders       78,385
commits              1,566
wasted_notifies          0
```

“侧边栏假设”已被**证伪**：在整个运行过程中仅有6次渲染，且全部源于真实处于忙碌状态或需要输入时的钩子状态触发，没有任何不必要的渲染。`stableArray` 对 `$workingSessionIds` / `$attentionSessionIds` 的保护机制（位于 `store/session-states.ts:236-259`）发挥了应有的作用。

真正的性能开销出在别的地方——可查看该场景“详情”中的 `topRenders` 数据。` $sessionStates` 共被触发1,200次，对应**10个监听器**（总触发次数达12,000次），且没有一次触发是多余的，由此可见数据发布环节是正常的；真正的浪费发生在那些在父组件状态变更时便重新渲染、但其自身状态并未改变的组件中。
