---
name: hermes-desktop-plugins
description: Write desktop app plugins that add UI panes and commands.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, plugins, ui, extension]
    category: productivity
    related_skills: []
---

# Hermes 桌面端插件技能

为 Hermes 桌面应用编写插件：状态栏组件、布局面板、命令面板指令、键绑定、路由以及主题。插件仅为一个普通的 JavaScript ESM 文件，可在应用运行时直接加载——无需构建步骤，也无需修改代码仓库。本技能不涵盖后端插件（位于 `~/.hermes/plugins/` 目录），这类插件使用 Python 编写，并有独立的文档说明。

## 适用场景

- 用户希望新增桌面 UI 元素（如面板、状态栏控件、仪表板或命令），但不想修改应用本身。
- 您希望将通过网关 RPC 计算得到的数据展示在应用内部。

## 先决条件

- Hermes 桌面应用（它会加载插件，而仅使用 CLI 或网关则无法加载）。
- 对 `$HERMES_HOME/desktop-plugins/` 目录的写入权限（通常为 `~/.hermes/desktop-plugins/`）。

## 运行方法

1. 从 `templates/plugin.js` 文件（位于本技能目录下）创建 `$HERMES_HOME/desktop-plugins/<name>/plugin.js` 文件——默认路径为 `~/.hermes/...`，若使用了命名配置文件，则路径为 `~/.hermes/profiles/<profile>/...`。请确保 `<name>` 与插件 ID 相同。
2. 桌面应用会持续监控该目录：文件保存后几秒内插件即可加载，后续再次保存时会实现热重载，无需手动重新加载。（若插件未出现，可按 ⌘K 键并选择 **Reload desktop plugins**。）
3. 若加载失败，应用会显示提示信息说明错误原因——请修复文件后再保存。

## 快速参考

唯一需要导入的模块是 `@hermes/plugin-sdk`（此外还有 `react` / `react/jsx-runtime`，这些会自动指向应用自带的 React 实现——请使用 `jsx()` 函数编写 UI，而非 JSX 语法；该文件不会被编译）。

- `host.state.*` —— 只读的响应式原子：`activeSessionId`、`cwd`、`gateway`、`model`、`profile`、`viewport`。在处理函数中可通过 `.get()` 方法读取，在组件中则可使用 `useValue(atom)` 方法读取。
- `host.request(method, params)` —— 用于调用网关的 JSON-RPC 接口（支持会话管理、配置设置、技能调用、定时任务等应用所需的所有操作）。
- `host.onEvent(type, fn)` —— 监听网关实时发送的事件（使用 `'*'` 可监听所有事件）。该方法会返回一个用于取消监听的函数。
- `host.notify({ kind, message })`、`host.navigate(path)`、`host.logs()`、`host.status()`、`haptic('tap')`。
- `ctx.register({ id, area, order?, render?, data? })` —— 用于添加 UI 元素。常用区域包括：`'statusBar.right'`/`'statusBar.left'`（状态栏芯片）、`'panes'`（布局区域——可设置 `title` 以及 `data: { placement, dock?, width?, height? }` 参数；面板会自动定位到对应的区域）、`PALETTE_AREA`（⌘K 命令区域）、`KEYBINDS_AREA`（可重新绑定的操作区域）。
- 面板定位：`placement: 'left'|'right'|'bottom'|'main'` 表示面板的逻辑位置——该类型的面板会与其他同位置的面板堆叠在一起。若希望面板固定在特定边缘，可添加 `dock: { pane, pos }` 参数——其操作方式与将元素拖放到面板上的放置芯片相同。`pane` 可以是任意面板 ID（如 `workspace` 表示主线程面板，还有 `sessions`、`terminal`、`files`、`review`、`logs` 等），`pos` 的取值为 `'top'|'bottom'|'left'|'right'|'center'`。例如，“位于对话内容下方”可表示为 `dock: { pane: 'workspace', pos: 'bottom' }`，同时建议指定 `height` 值（如 `'200px'`），以避免面板占据整个区域的一半空间。
- 完整页面：可通过注册 `area: ROUTES_AREA` 并设置 `data: { path: '/my-page' }` 以及对应的 `render` 函数来创建页面——该页面会像内置视图一样显示在主工作区面板中。若希望通过侧边栏导航访问该页面，可执行如下操作：`ctx.register({ id: 'nav', area: SIDEBAR_NAV_AREA, data: { path: '/my-page', label: 'My Page', codicon: 'project' } })`（该元素会显示在“Artifacts”下方，并在对应路由激活时高亮显示）——或者通过 `PALETTE_AREA` 区域的命令调用 `host.navigate('/my-page')` 来访问。
- `ctx.storage.get/set/remove` —— 用于实现插件自身的命名空间持久化存储。
- 用户可在“设置 → 插件”中管理插件（启用/禁用实时功能，以及显示/隐藏插件文件夹）。已被禁用的插件在重启后仍会保持禁用状态——无需强行启用，因为这是用户主动关闭的。
- UI 组件：应用自带了一套设计语言，可直接导入使用，包括 `Button`、`Input`、`Textarea`、`Select*`、`Switch`、`Checkbox`、`SegmentedControl`、`Tabs*`、`Dialog*`、`ConfirmDialog`、`DropdownMenu*`、`ContextMenu*`、`Popover*`、`Tip`/`Tooltip*`、`Badge`、`Kbd`/`KbdGroup`、`SearchField`、`ScrollArea`、`Separator`、`Skeleton`、`GlyphSpinner`、`EmptyState`、`ErrorState`、`CopyButton`、`StatusDot`、`LogView`、`Codicon`、`DecodeText`，此外还有 `cn` 和 `icons.*` 等组件。建议优先使用这些现成组件，而非自行编写，这样插件才能保持原生外观；样式应通过主题变量设置，切勿直接硬编码颜色。

## 操作步骤

1. 选择一个简短的凯巴式命名法 ID，文件夹名称也需与之一致。
2. 以 `templates/plugin.js` 为模板，保持其默认的导出结构（即 `{ id, name, register(ctx) }`）。
3. 若要创建面板，需注册 `area: 'panes'`，同时提供 `placement` 参数说明定位方式，并通过 `render` 函数返回对应的组件——应用会自动将面板放置到合适的区域，之后用户可自行拖动面板。
4. 使用 `host.request` 方法获取数据，或通过 `host.onEvent` 方法订阅事件；请勿频繁轮询，间隔至少几秒。
5. 使用常规文件编辑工具完成文件编写后，让用户按 ⌘K 键并选择 **Reload desktop plugins** 以重新加载插件。

## 常见问题与注意事项

- 绝对不要硬编码颜色或背景色（如 `#000`、`black`、`rgb(...)`）。面板本身已位于应用的编辑器背景之上，无需修改背景色，其他所有元素都应使用主题变量来设置颜色，例如 `var(--ui-text-secondary)`、`var(--ui-text-quaternary)`、`var(--ui-stroke-secondary)`、`var(--ui-accent)`。若需在画布上绘图，可先通过 `getComputedStyle(canvas).getPropertyValue('--ui-accent')` 获取当前主题中的强调色值。
- 仅能使用已导入的组件——若遗漏了某个组件的导入（例如 `StatusDot`），则在渲染时会触发 `ReferenceError` 错误。请仔细检查 `jsx()` 函数中出现的所有标识符是否都已出现在导入语句中。
- 使用画布的面板必须通过 `ResizeObserver` 监听其容器尺寸变化，并动态调整画布的宽高属性（而非仅依赖 CSS），因为面板会因用户拖动边框或切换布局而不断改变大小；仅在初始化时设置一次尺寸会导致空白区域或模糊的缩放效果。
- JSX 语法不会被解析，该文件将以未编译状态加载。请使用 `react/jsx-runtime` 中提供的 `jsx('div', { children: ... })` 函数来编写代码。
- 除 `@hermes/plugin-sdk`、`react` 和 `react/jsx-runtime` 外，切勿导入其他任何模块；否则会导致解析失败。
- 处理函数必须以命令式方式读取状态（即使用 `$atom.get()` 方法），绝不能通过渲染闭包来获取状态——否则在处理高频事件时可能会得到过时的数据值。
- 请尽量保持组件结构简洁；仅在真正需要使用该值的组件中通过 `useValue` 进行订阅。

## 验证方法

- 执行 **Reload desktop plugins** 后，插件的 UI 元素应正常显示。
- 不会出现任何错误提示（如“插件 <name> 加载失败”）；若出现错误提示，会明确说明失败原因——请修复问题后再重新加载插件。
- 对于面板而言，新的布局区域应能正常显示，且可像其他核心面板一样被拖动。
