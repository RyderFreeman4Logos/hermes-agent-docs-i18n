# 桌面应用插件 —— UI面板、命令与小部件

为Hermes桌面应用编写插件：状态栏项、布局面板、命令面板中的命令、快捷键绑定、路由规则以及主题设置。插件仅为一个普通的JavaScript ESM文件，可在应用运行时直接加载——无需任何构建步骤，也无需修改代码仓库。插件还可以与其自身的Python后端命名空间进行交互（通过`ctx.rest`/`ctx.socket`访问`/api/plugins/<id>`）；而通用的Python插件系统（位于`~/.hermes/plugins/`目录下）则有单独的文档说明。

系统中存在两种插件格式，它们遵循相同的接口规范并支持热重载功能：

- `$HERMES_HOME/desktop-plugins/<id>/plugin.js` —— 独立的桌面插件。默认情况下会被加载。
- `$HERMES_HOME/plugins/<id>/desktop/plugin.js` —— 统一代理插件包中的桌面端部分：该目录同时包含Python插件文件（`plugin.yaml`）及其后端文件`dashboard/plugin_api.py`，对应的桌面UI也会一同被加载，因此整个功能模块会作为一个整体进行安装或卸载。此部分为可选配置：它会在“设置 → 插件”中列出，但在用户手动开启之前不会生效（其机制与Python插件部分的`plugins.enabled`开关一致）。建议用户在安装完成后再手动开启该功能——在检查相关开关之前，无需先排查“插件未显示”的问题。

完整的参考文档（涵盖所有导出函数、区域数据负载、后端逻辑及安全相关内容）可见：`website/docs/developer-guide/desktop-plugin-sdk.md`。

## 适用场景

- 用户希望在不修改应用程序本身的情况下，添加新的桌面界面元素（如面板、状态栏控件、控制面板或命令功能）。  
- 您希望将通过网关 RPC 计算得到的数据展示在应用程序内部。  

## 先决条件

- Hermes 桌面应用（它会加载插件；仅使用 CLI 或网关则无法实现此功能）。  
- 对 `$HERMES_HOME/desktop-plugins/` 目录具有写入权限（通常为 `~/.hermes/desktop-plugins/`）。  

## 运行步骤

1. 从该技能目录下的 `templates/plugin.js` 文件创建 `$HERMES_HOME/desktop-plugins/<name>/plugin.js` 文件——默认路径为 `~/.hermes/...`，若使用了命名配置文件，则路径为 `~/.hermes/profiles/<profile>/...`。请确保 `<name>` 与插件的 `id` 相同。  
2. 桌面应用会持续监控该目录：文件放入后几秒内插件便会加载，之后每次保存都会直接热重载插件，无需手动重新加载。（若插件未显示，可尝试按 ⌘K 并选择 **Reload desktop plugins**。）  
3. 若加载失败，应用会显示提示信息说明具体错误原因——请修正文件内容后再次保存。  

## 快速参考

唯一需要导入的模块是 `@hermes/plugin-sdk`（此外还需导入 `react`/`react/jsx-runtime`，这两个模块实际上会引用应用自带的 React 库——应使用 `jsx()` 函数来编写界面代码，而非 JSX 语法；该文件无需经过编译）。

- `host.state.*` — 只读的响应式原子：`activeSessionId`、`busy`、`awaitingResponse`、`busyBySession`、`cwd`、`gateway`（表示套接字状态，而非轮次繁忙状态）、`model`、`profile`、`viewport`；此外还包括与分页视图相关的聚焦会话原子：`focusedSessionId`（运行时标识符，用于调用 `session.*` RPC 方法）、`focusedStoredSessionId`（持久化标识符，用于导航/列表匹配）、`focusedSessionProfile`（所聚焦聊天的所属用户配置文件——在需要针对特定机器人或用户配置进行读取时优先使用该值；而 `profile` 是套接字的主配置文件，不会随标签页焦点变化而改变），以及 `focusedUsage`（所聚焦会话的实时 `UsageStats` 数据，无需通过 RPC 获取）。当所聚焦的聊天在发送消息后仍在处理中（如思考或数据流传输）时，`busy` 的值为真；在收到第一个助手响应之前，`awaitingResponse` 的值为真。`busyBySession` 用于将运行时会话标识符与轮次中间状态关联起来，适用于需要监控所有会话的场景。对于需要在不同分页视图之间跟随用户变化的读取操作，建议使用这些聚焦原子。在处理程序中可通过 `.get()` 方法读取这些值，在组件中则可使用 `useValue(atom)` 方法。
- `host.request(method, params)` — 用于调用网关的 JSON-RPC 接口（涵盖会话、配置、技能、定时任务等应用所需的所有功能）。
- `host.onEvent(type, fn)` — 监听网关的实时事件（使用 `'*'` 可监听所有事件）。该方法会返回一个用于取消事件的函数。
- `host.notify({ kind, message })`、`host.navigate(path)`、`host.logs(...)`、`host.status()`、`haptic('tap')`。
- `ctx.register({ id, area, order?, render?, data? })` — 用于自定义 UI。  
  支持的区域包括：`'statusBar.right'`/`'statusBar.left'`（状态标签），  
  `'panes'`（布局区域——可设置 `title` 以及 `data: { placement, dock?, width?, height? }`；该面板会自动匹配到对应的区域），  
  `PALETTE_AREA`（⌘K 命令），`KEYBINDS_AREA`（可重新绑定的操作），  
  `THEMES_AREA`（其 `data` 参数为完整的 `DesktopTheme` 对象）。  

- 主题管理：仅注册主题不会使其立即出现在主题选择器中。若要在组件中应用某主题，可使用 `useTheme().setTheme(name)`；若在无组件的上下文中（如网关事件或套接字处理程序）使用主题，则可通过 `requestTheme(name)` 来实现。对于无法识别的主题名称，`requestTheme` 会返回 `false`，且不会更改界面外观，因此可将其用作可用性检测手段，而非强制用户恢复为默认主题。  

- 面板定位：`placement: 'left'|'right'|'bottom'|'main'` 表示面板的语义位置——该面板会与同位置的现有面板堆叠（类似标签页效果）。若需将面板固定在特定边缘位置，则可添加 `dock: { pane, pos }` 参数，操作方式与将元素拖放到面板的放置标签上相同。`pane` 可为任意面板标识符（如 `workspace` 表示主线程，还有 `sessions`、`terminal`、`files`、`review`、`logs` 等）；`pos` 的取值为 `'top'|'bottom'|'left'|'right'|'center'`。例如，“置于对话内容下方”可表示为 `dock: { pane: 'workspace', pos: 'bottom' }`，同时还需指定 `height` 值（如 `'200px'`），以避免面板占据整个区域的一半空间。
- 完整页面：注册 `area: ROUTES_AREA`，并传入 `data: { path: '/my-page' }` 以及 `render` 配置——该页面将如同任何内置视图一样显示在工作区（主）面板中。可通过侧边栏导航行访问该页面：`ctx.register({ id: 'nav', area: SIDEBAR_NAV_AREA, data: { path: '/my-page', label: '我的页面', codicon: 'project' } })`（会在“Artifacts”下方显示，并在对应路由处高亮）；或者使用 `PALETTE_AREA` 命令并调用 `host.navigate('/my-page')`。
- 转录指令：注册 `area: TRANSCRIPT_DIRECTIVE_AREA`，并传入 `data: { name: 'task', render: ({ attrs, streaming }) => jsx(...) }` 配置——这样助手便可以在聊天消息中通过单独一行输出 `::task{id="BB-12"}` 的形式来内联渲染你的组件。其中的 `attrs` 为不可信的 `key="value"` 字符串，需对其进行验证。未被使用或格式错误的指令将退化为纯文本；核心系统自带的 `::preview{file="…"}` 可作为参考。注册完此类指令后，需通过打包好的技能或用户指令告知模型其存在——模型无法自行识别指令名称。
- `ctx.storage.get/set/remove` —— 为你的插件提供命名空间的持久化存储功能。
- `ctx.os` — 专为插件设计的操作系统通知功能：
  `ctx.os.notify({ title, body?, silent?, icon?, activate?, onActivate?, actions? })`
  可用于发送原生的操作系统级通知。该功能仅在用户离开 Hermes 应用时触发（若需在应用内显示提示框，请使用 `host.notify`）；其启用状态由“设置”→“通知”→“插件通知”选项控制，且每个插件的通知频率都有限制——因此请仅将此功能用于真正重要的事件。`activate` 参数可接受插件深度链接（如 `hermes://index-network/intent/1`）、哈希路径（如 `/index-network/intent/1`），或是 `{ path, params }` 格式的数据，其解析逻辑与操作系统深度链接相同。操作按钮可自行设置 `activate` 函数或 `onAction` 回调函数（仅适用于渲染层；仅有操作标识符会通过 IPC 传递）。当相应功能不可用时，`ctx.os.openExternal(url)`、`ctx.os.revealPath(path)` 和 `ctx.os.writeClipboard(text)` 函数会返回 `false` 值（不会抛出异常）。
- `ctx.i18n.register({ en, ja, ... })` — 允许您为自己的插件创建专属的本地化资源包（切勿修改核心的 `en.ts` 文件）。这些资源可以是纯字符串，也可以是包含插值功能的函数；嵌套的本地化资源可通过点号路径来访问。在组件中，可使用 `usePluginI18n(id)` 函数以响应式方式读取这些本地化内容，该函数会返回 `t('key', ...args)` 的形式（当语言环境发生变化时会导致组件重新渲染）；在处理程序或状态管理器中，则可通过 `ctx.i18n.t` 来获取对应内容。资源的解析顺序为：首先优先使用应用当前设定的语言环境，其次是您自定义的 `en` 资源，最后才是原始的键值。
- **数据层**：使用 `useQuery`/`useMutation`/`useQueryClient`/`queryClient`（应用中唯一的 React Query 客户端，具备缓存、去重、`refetchInterval` 设置及数据失效等功能；切勿自行实现轮询逻辑），同时通过 `atom`/`computed` 来管理插件内部的本地状态。  
- **后端层**：若插件提供了 Python 版本的 `plugin_api.py`（位于 `~/.hermes/plugins/<id>/dashboard/` 目录下，且配置有 `"api": "plugin_api.py"`），可通过 `ctx.rest('/path', { method?, body?, timeoutMs? })` 调用该接口，或通过 `ctx.socket('/events', onMessage)` 获取实时数据——这两者均默认限定在 `/api/plugins/<id>` 路径下，不允许跨路径访问。在基于 OAuth 的远程环境中，`ctx.socket` 为无效操作，因此必须始终保留轮询作为备用方案。Python 后端仅在 `config.yaml` 中的 `plugins.enabled` 设置为该插件时才会被导入（此设置与应用内的启用开关独立）。如需在网关范围内共享数据，则应使用 `host.request`/`host.onEvent`。  
- **组件集成**：使用 `mount-scoped` 方式时，可通过在组件内调用 `jsx(Contribute, { area, id, children })` 实现动态内容嵌入；这样当页面卸载时，属于该页面的插件功能（例如 `TITLEBAR_AREAS.center` 中的标题栏控件）也会自动退出。而 `ctx.register` 用于实现永久性的插件集成。  
- **默认启用状态**：默认导出值设置为 `defaultEnabled: false`，意味着该插件为可选启用类型——它会在“设置 → 插件”页面中列出，直到用户手动开启为止。  
- **插件管理**：用户可通过“设置 → 插件”来管理插件（包括启用/禁用实时功能及查看插件目录）。已被禁用的插件在重启后仍会保持禁用状态，无需强行尝试激活，因为这是用户主动关闭的。
- UI：应用程序的设计语言，可直接导入——包括 `Button`、`Input`、`Textarea`、`Select*`、`Switch`、`Checkbox`、`SegmentedControl`、`Tabs*`、`Dialog*`、`ConfirmDialog`、`DropdownMenu*`、`ContextMenu*`、`Popover*`、`Tip`/`Tooltip*`、`Badge`、`Kbd`/`KbdGroup`、`SearchField`、`ScrollArea`、`Separator`、`Skeleton`、`GlyphSpinner`、`EmptyState`、`ErrorState`、`CopyButton`、`StatusDot`、`LogView`、`Codicon`、`DecodeText`，以及 `cn` 和 `icons.*`。建议优先使用这些预定义元素，而非自行编写组件，这样才能让插件呈现原生外观；样式应通过主题变量设置，切勿硬编码颜色。

## 操作步骤

1. 选择一个简短的驼峰式 `id`，文件夹名称必须与之一致。
2. 从 `templates/plugin.js` 开始编写，保持默认的导出结构（`{ id, name, register(ctx) }`）。
3. 对于某个面板，需注册 `area: 'panes'`，并指定 `placement` 参数以及返回对应组件的 `render` 函数——应用程序会自动将其放置到合适的区域，之后用户可自由拖动该面板。
4. 使用 `host.request` 获取数据，或通过 `host.onEvent` 订阅事件；查询频率最好控制在几秒一次以内。
5. 用文件工具保存文件后，提示用户按 ⌘K 运行 **Reload desktop plugins**。

## 常见问题

- 绝对不要硬编码颜色或背景色（如`#000`、`black`、`rgb(...)`）。面板本身已位于应用的编辑器背景之上，无需再手动设置背景，其余所有内容都应使用主题变量来定义，例如`var(--ui-text-secondary)`、`var(--ui-text-quaternary)`、`var(--ui-stroke-secondary)`、`var(--ui-accent)`。对于画布绘图，可通过`getComputedStyle(canvas).getPropertyValue('--ui-accent')`一次性获取这些值。
- 仅引用已导入的组件——若遗漏了某个组件的导入（例如`StatusDot`），在渲染时就会引发`ReferenceError`错误。请仔细检查`jsx()`调用中的所有标识符是否都出现在导入语句中。
- 画布面板必须使用`ResizeObserver`来监控其容器，并通过修改画布的宽高属性（而非仅依赖CSS）来调整大小。由于面板会因拖动边框或布局变化而不断调整尺寸，仅在组件初次加载时设置尺寸会导致空白区域或模糊的缩放效果。
- JSX语法将无法被解析，文件会以未编译的状态加载。应使用`react/jsx-runtime`中的`jsx('div', { children: ... })`函数。
- 除了`@hermes/plugin-sdk`、`react`以及`react/jsx-runtime`之外，切勿导入其他任何内容；否则会导致解析失败。
- 处理函数必须以命令式方式读取状态（即通过` $atom.get()`），绝不能从渲染闭包中获取状态——否则在处理高频事件时就会得到过时的数据。
- 将组件设计得尽可能简洁；仅在实际渲染该值的叶子组件中使用`useValue`进行订阅。

- 执行“重新加载桌面插件”操作后，该插件的用户界面便会显示出来。  
- 不会出现错误提示弹窗（如“插件 <名称> 加载失败”）；如果出现了此类提示，其中会说明具体的失败原因——请修复问题后再重新加载插件。  
- 对于各个面板而言：新的区域会像其他核心面板一样可见且可拖动。
