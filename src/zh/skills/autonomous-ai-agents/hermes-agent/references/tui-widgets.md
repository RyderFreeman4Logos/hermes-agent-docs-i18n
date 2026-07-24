# TUI 小部件——Ink TUI Dock 的实时面板功能

为 Hermes TUI（`hermes --tui`）创建小部件应用：可在状态栏上方嵌入可快速查看的背景面板，或生成能接管键盘控制的模态覆盖层。这些小部件均为纯 ESM 文件，TUI 在启动时会自动加载——无需任何构建步骤，也无需修改代码仓库。本功能不涵盖桌面应用程序或网页控制台中的小部件。

## 适用场景

- 用户希望在 TUI 中显示实时面板（如行情行情板、时钟、倒计时器、状态卡片、基于 API 的数据展示等）。
- 用户需要为某个斜杠命令绑定自定义的模态工具（如选择器、计算器、查看器等）。

## 先决条件

- 必须正在使用 TUI（通过 `hermes --tui` 启动）。小部件无法在传统 CLI 环境或消息平台中显示。
- 需要网络支持的小组件必须具备其 API 所要求的相应凭据；请求失败时应以错误形式呈现，而不得导致程序崩溃。

## 使用方法

1. 使用 `write_file` 命令创建 `~/.hermes/tui-widgets/<名称>.mjs` 文件（可参考 `templates/clock.mjs` 中的完整示例小部件）。
2. 若 TUI 正在运行，它会在约一秒内热加载该文件（系统会持续监控小部件目录）；执行 `/widgets-reload` 命令可强制重新扫描。
3. 小部件的 ID 会自动成为其对应的斜杠命令路径（格式为 `</ID>`），其 `help` 文档会显示在 `/` 的自动补全弹窗中。无需其他注册步骤。
4. 自动打开功能（无需输入命令）：在 `register(sdk)` 函数结尾添加 `sdk.openWidget(app, app.init(''))` —— 文件加载完成后小部件便会自动嵌入 Dock。仅应在用户明确要求时使用此方法；请注意，每次执行 `/widgets-reload` 后小部件都会重新嵌入 Dock。

## 快速参考

小部件文件默认会导出 `register(sdk)` 函数：

```js
export default function register(sdk) {
  const { Box, Text, defineWidgetApp, h } = sdk

  defineWidgetApp({
    id: 'clock',                    // slash command name
    help: 'live clock in the dock', // `/` completion metadata
    mode: 'ambient',                // 'ambient' docks; 'modal' takes input
    init: arg => ({ label: arg.trim() || 'UTC' }),   // null = print usage
    reduce: (state, { ch, key }) => (key.escape || ch === 'q' ? null : state),
    render: ({ state, t }) => h(sdk.Dialog, { width: 24 }, h(Text, { color: t.color.label }, state.label))
  })
}
```

`sdk` 包含的组件有：`defineWidgetApp`、`openWidget`、`updateWidget`、`isCtrl`、`React`、`h`（用于创建元素，.mjs 文件中不支持 JSX），以及组件 `Box`、`Text`、`Dialog`、`Overlay`、`WidgetGrid`、`GridAreas`，还有加载器 `Shimmer`、`ShimmerRows`、`useShimmerPhase`——可使用 `ShimmerRows` 来显示加载状态，而非仅显示简单的“加载中…”文字。

展开/折叠功能：通过 `sdk.Accordion` 实现，该组件与会话面板中的工具/技能板块所使用的机制相同。使用 `h(Accordion, { t, title: 'details', count: 3, defaultOpen: false }, body)` 可在点击时切换状态（适用于不接收键盘输入的普通 Widget）；而对于模态应用，则可通过传递 `open` 和 `onToggle` 参数，根据还原器状态来控制其展开与关闭。

固定尺寸要求（在数据更新过程中，卡片绝不能改变尺寸）：
- 为 `Dialog` 明确指定 `width`；图表会精确返回用户设定的宽度（在数据加载初期，较短的序列数据会在左侧留出空白）。
- 对动态数值进行填充处理：使用 `String(v).padStart(6)`——例如将 `51 ms` 转换为 `112 ms` 时，需确保行长度不变。
- 每个加载阶段内的行数应保持一致，仅可更换内容，不可更改结构。

图表功能（纯字符串生成方式——可使用主题颜色对结果进行着色）：
- `sdk.sparkline(series, width?)` → 生成单行趋势图，显示为 `▂▃▅▇█▆` 形式。
- `sdk.sparkRows(series, width, rows)` → 生成多行柱状图（从上到下排列），外观类似任务控制面板；单元格高度越大，显示的细节越丰富。
- `sdk.gauge(ratio, width)` → 为 0 到 1 之间的数值生成填充条，显示为 `█████░░░` 形式。
- `sdk.hbars(values, width)` → 生成水平条形图，每个数值对应一条条形，条形宽度按最大值比例缩放，标签显示为八分之一个方块大小。

建议将滚动数据序列保存在组件状态中（每次数据更新时追加一条记录，最多保留约 120 条样本），并在仪表板面板中使用 `sparkRows`、在简短显示区域中使用 `sparkline` 来呈现数据。

核心功能约定：
- `mode: 'ambient'` 模式——不接收任何用户输入，需通过命令手动切换该模式；`render` 函数会返回一个卡片（通常为 `Dialog`），绝不会返回 `Overlay`。组件的放置位置由 `zone` 参数决定——每个区域都会预留实际显示空间，确保内容不会覆盖在文本记录之上：
  - 托盘式布局（位于页面顶部的 Chrome 行）：`dock-top`（位于顶部状态栏下方）、`dock-bottom`（默认位置，位于底部状态栏上方）。
  - 边栏式布局（位于文本记录两侧的列，文字会自动环绕边栏排列）：`top-left`、`top-right`、`bottom-left`、`bottom-right`——这些名称分别表示边栏的位置及其上下锚点。需在应用中设置与卡片宽度相同的 `width` 值（建议与默认的 Dialog 宽度 44 像素一致），这样边栏就会预留相应数量的列空间。系统会根据用户输入的描述自动匹配对应的区域，例如“右上角”对应 `top-right`，“状态栏上方/旁边”则对应托盘式布局。边栏式布局更适合宽度较窄的卡片（约 30-46 列）；而全宽或宽度较大的内容则应放在托盘式布局中。
- `mode: 'modal'` 模式为默认值——该模式会捕获所有键盘输入；`reduce` 函数负责返回下一个状态，若要忽略某个按键，可传入相同的引用，若要关闭模态窗口，则传入 `null`；`render` 函数会将内容包裹在 `Overlay` 中以实现定位。
- 异步数据处理：在 `init` 阶段发起数据获取请求，通过 `sdk.updateWidget(app, fn)` 函数将结果更新到界面中——如果窗口已关闭，此操作将不会执行任何操作，因此即使数据返回较晚，也无法重新显示该窗口。
- 动画效果：可通过 `React.useState` 和 `React.useEffect` 在组件内部创建计时器来实现动画（可参考相关模板），建议将间隔时间设置为至少 250 毫秒。
- 颜色使用：必须始终使用主题颜色（如 `t.color.primary/label/muted/ok/error/…`），严禁直接使用硬编码的十六进制颜色值——这样才能确保 Widget 在不同主题风格以及浅色/深色模式下都能正常显示。

## 操作步骤

1. 确定 `id`、`mode` 及状态结构，确保状态数据可序列化。
2. 根据模板编写代码，并通过 `init` 和 `updateWidget` 函数实现数据传递。
3. 使用 `/<id>` 语句启动 Widget（每次修改文件后都会实现热加载）；若要关闭普通 Widget，可再次运行 `/<id>` 语句。
4. 循环修改文件——每次保存后都会立即热加载（采用“最后写入者胜”的原则，新的定义会覆盖旧的定义）。需要重新显示 Widget 时，只需再次运行 `/<id>` 语句即可。

## 常见问题与注意事项

- `.mjs` 文件中不得使用 JSX 语法，也不得有直接的导入语句——所有功能都需通过 `sdk` 参数实现，元素由 `h(...)` 函数构建。
- 开发的模态窗口必须提供关闭方式（如按 `Esc` 键或输入 `q` 后返回 `null`）。
- 普通 Widget 的行数应保持较少（建议不超过 6 行），因为托盘式布局位于文本记录和状态栏之间，空间较为有限。
- 如果 `register()` 函数抛出异常，系统会记录错误并跳过该 Widget 的注册；如果某个 Widget 一直无法显示，可检查 `~/.hermes/logs/tui_gateway_crash.log` 文件中的日志信息。

## 验证方法运行 `/widgets-reload` 命令——命令输出中的对应行必须将相关文件列在 `loaded:` 下。随后输入 `/<id>`，即会在状态栏正上方的右侧显示该环境小部件，同时编辑器仍可继续接收输入；再次输入 `/<id>` 即可将其移除。
