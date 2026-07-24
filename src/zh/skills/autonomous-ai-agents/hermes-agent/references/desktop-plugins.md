# 桌面应用插件 —— UI面板、命令与小部件

你可以为Hermes桌面应用编写插件：状态栏项目、布局面板、命令面板中的命令、快捷键绑定、路由以及主题。插件其实只是一个普通的JavaScript ESM文件，应用会在运行时直接加载它——无需任何构建步骤，也无需修改代码仓库。此外，插件还可以与其自身的Python后端命名空间进行交互（通过`ctx.rest`/`ctx.socket`访问`/api/plugins/<id>`）；而通用的Python插件系统（位于`~/.hermes/plugins/`目录下）则有单独的文档说明。

完整的参考资料（包括所有导出项、区域数据负载、后端功能及安全相关内容）可查阅：
`website/docs/developer-guide/desktop-plugin-sdk.md`。

## 适用场景

- 用户希望添加新的桌面UI元素（如面板、状态栏小部件、控制面板或命令），但又不想修改应用本身。
- 你希望将通过网关RPC计算得到的数据展示在应用内部。

## 先决条件

- 已安装Hermes桌面应用（该应用会加载插件，而仅CLI或网关本身则不具备此功能）。
- 对`$- `ctx.i18n.register({ en, ja, ... })` — 可上传您自己的区域设置包，这些包仅作用于您的插件（切勿修改核心的 `en.ts` 文件）。其值可以是原始字符串或插值函数；嵌套结构可通过点号路径访问。可在组件中使用 `usePluginI18n(id)` 以反应式方式读取这些内容，该函数会返回 `t('key', ...args)` 的形式（在切换区域设置时会重新渲染），也可在处理程序或存储模块中通过 `ctx.i18n.t` 来访问。解析顺序为先根据应用当前使用的区域设置查找，再查找您的 `en` 设置，最后才是原始键值。
- 数据处理：使用 `useQuery`/`useMutation`/`useQueryClient`/`queryClient`（这是应用中唯一的 React Query 客户端，具备缓存、去重、`refetchInterval` 功能以及类似核心组件的失效处理能力；切勿自行实现轮询逻辑），同时还可使用 `atom`/`computed` 来管理插件内部的本地状态。
- 后端接口：如果插件提供了 Python 版本的 `plugin_api.py` 文件（位于 `~/.hermes/plugins/<id>/dashboard/` 目录下，且配置中有 `"api": "plugin_api.py"` 字段），则可通过 `ctx.rest('/path', { method?, body?, timeoutMs? })` 调用该接口，也可通过 `ctx.socket('/events', onMessage)` 访问实时数据流——这两者按设计均仅作用于 `/api/plugins/<id>` 路径，不允许跨路径访问。在基于 OAuth 的远程环境中，`ctx.socket` 为无效操作，因此务必保留轮询作为备用方案。只有当插件被列入 `config.yaml` 文件中的 `plugins.enabled` 列表时（此设置与应用内的启用开关独立），才会导入 Python 后端。如需获取全局范围内的数据，请使用 `host.request` / `host.onEvent`。
- `Contribute`（作用范围为组件挂载层）：可在组件内部通过 `jsx(Contribute, { area, id, children })` 的方式使用该功能，这样当页面被卸载时，属于该页面的界面元素（例如 `TITLEBAR_AREAS.center` 中的标题栏控件）也会一同消失——而 `ctx.register` 用于实现永久性的界面添加。
- 默认导出项上设置 `defaultEnabled: false` 可将插件设为可选启用状态：此类插件会显示在“设置 → 插件”列表中，需用户手动开启才会生效。
- 用户可在“设置 → 插件”中管理插件（实时启用/禁用、查看插件文件夹）。已被禁用的插件在应用重启后仍会保持禁用状态——无需强行尝试重新启用，因为这是用户主动关闭的。
- UI 组件：应用自带的设计语言组件可直接导入，包括 `Button`、`Input`、`Textarea`、`Select*`、`Switch`、`Checkbox`、`SegmentedControl`、`Tabs*`、`Dialog*`、`ConfirmDialog`、`DropdownMenu*`、`ContextMenu*`、`Popover*`、`Tip`/`Tooltip*`、`Badge`、`Kbd`/`KbdGroup`、`SearchField`、`ScrollArea`、`Separator`、`Skeleton`、`GlyphSpinner`、`EmptyState`、`ErrorState`、`CopyButton`、`StatusDot`、`LogView`、`Codicon`、`DecodeText`，此外还有 `cn` 组件及各类 `icons.*` 图标组件。建议优先使用这些现成组件，而非自行编写元素，这样才能让插件看起来更符合整体风格；样式应通过主题变量来设置，切勿直接硬编码颜色值。

## 操作步骤

1. 选择一个简短的凯巴布式命名法 `id`，对应的文件夹名称也必须与此一致。
2. 从 `templates/plugin.js` 文件开始编写，保持其默认导出结构（即 `{ id, name, register(ctx) }`）。
3. 对于需要显示的面板，需注册 `area: 'panes'` 属性，并提供 `placement` 参数指示位置，同时通过 `render` 函数返回您的组件——应用会自动将面板放置到合适的区域，之后用户可自行拖动面板。
4. 使用 `host.request` 获取数据，或通过 `host.onEvent` 订阅事件；轮询频率最好控制在几秒一次以内。
5. 使用常规文件工具完成文件编写后，提示用户按 ⌘K 键执行“重新加载桌面插件”操作。

## 常见问题与注意事项- 绝对不要硬编码颜色或背景色（如`#000`、`black`、`rgb(...)`）。面板本身已位于应用编辑器的背景之上，因此请勿改动背景，而应使用主题变量来设置其他元素的颜色：`var(--ui-text-secondary)`、`var(--ui-text-quaternary)`、`var(--ui-stroke-secondary)`、`var(--ui-accent)`。对于画布绘图，可通过`getComputedStyle(canvas).getPropertyValue('--ui-accent')`一次性获取这些颜色值。
- 仅引用已导入的组件——若遗漏了某个组件的导入（例如`StatusDot`），在渲染时将会出现`ReferenceError`错误。请仔细检查`jsx()`调用中的所有标识符是否都出现在导入语句中。
- 画布面板必须使用`ResizeObserver`来监控其容器，并通过修改画布的宽高属性（而非仅依赖CSS）来调整大小——由于面板会因拖动边框或布局切换而不断变化尺寸，仅在组件初次加载时设置尺寸会导致空白区域或模糊的缩放效果。
- JSX语法无法被解析，文件将以未编译的状态加载。请使用`react/jsx-runtime`中的`jsx('div', { children: ... })`函数。
- 除了`@hermes/plugin-sdk`、`react`以及`react/jsx-runtime`之外，切勿导入其他任何内容；否则会导致解析失败。
- 处理函数必须以命令式方式读取状态（即使用`$
