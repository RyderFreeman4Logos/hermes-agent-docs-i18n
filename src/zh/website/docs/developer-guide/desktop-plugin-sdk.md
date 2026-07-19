---
sidebar_label: "Desktop Plugin SDK"
title: "Desktop Plugin SDK (@hermes/plugin-sdk)"
description: "Extend the native Hermes Desktop app — panes, pages, sidebar nav, status bar, palette commands, keybinds, themes, and a scoped backend namespace, with one import and no build step."
---

# 桌面插件 SDK

原生 [Hermes Desktop](/user-guide/desktop) 应用采用贡献驱动模式：窗口中的所有组件——面板、路由、侧边栏导航、状态栏元素、调色板项、键绑定、主题等——都会被注册到一个中央注册表中。核心组件的各组件注册方式与插件完全一致，因此插件才是整个系统的核心，而非后期硬加的附加组件。

**桌面插件**是一个单一的 ESM 文件，该文件会默认导出 `HermesPlugin`。它只需导入一个模块——`@hermes/plugin-sdk`——即可获取所有必要功能：应用的实时状态、JSON-RPC 接口、带作用域的 REST/Socket 后端命名空间、React Query 以及应用自带的 UI 工具包，因此插件界面默认就能呈现出原生风格。无需克隆仓库、无需运行 `npm run build`，也无需修改应用源代码。只需将文件放入 `$HERMES_HOME/desktop-plugins/<id>/plugin.js` 目录中，应用即可在几秒内加载该插件，并在每次保存时实现热重载。

:::warning 这并非网页控制台插件 SDK  
在 Hermes 生态系统中，“插件”这一概念有多种不同含义。本页面介绍的是**原生桌面应用**（`hermes desktop`）的 SDK，即 `@hermes/plugin-sdk` 模块以及 `$HERMES_HOME/desktop-plugins/` 目录。而**网页控制台**（`hermes dashboard`）则拥有独立的插件系统，该系统基于 `window.__HERMES_PLUGIN_SDK__` 并使用 `manifest.json` 进行管理，相关文档请参见[扩展控制台功能](/user-guide/features/extending-the-dashboard)。Python CLI/网关插件的相关文档则在[构建 Hermes 插件](/developer-guide/plugins)中。这三种插件在代码、API 以及部署方式上均互不共享。仅桌面版和控制台版的 SDK 共享后端 `plugin_api.py` 命名空间（`/api/plugins/<id>`）。
:::

## 心智模型

该 SDK 遵循 VS Code 的模块模型。插件开发者只需导入一个模块，且绝不能触碰应用的内部实现（这些内容在打包的插件中会被代码检查工具屏蔽，而在磁盘插件中则无法被解析）。插件的功能分为不同层级：

- **`host.state.*`**——对应用实时状态的只读访问权限（基于 nanostore 原子）：当前会话、工作目录、网关状态、模型、配置文件、视图窗口等信息。
- **`host.*` 操作**——经过筛选的安全操作命令：显示提示信息、导航、查看日志尾部、重启网关、订阅网关事件流等。
- **`host.request`**——网关的 JSON-RPC 接口：用于获取会话信息、配置参数、技能相关数据、定时任务执行结果等，即应用自身会调用的所有功能。
- **`ctx.rest` / `ctx.socket`**——如果你提供了 `plugin_api.py` 文件，即可使用自己定义的后端命名空间（`/api/plugins/<id>`）。
- **`ui.*`**——设计语言相关内容：包括应用的实际组件、主题变量、图标以及格式化函数，确保你的插件界面能与应用实现像素级一致。

## 两种部署模式

| 模式 | 存放位置 | 使用者 | 构建步骤 |
|------|---------|-------|----------|
| **磁盘部署**（推荐） | `$HERMES_HOME/desktop-plugins/<id>/plugin.js` | 用户、智能体 | 无需额外构建——作为纯 ESM 文件直接加载，无需编译 |
| **内置部署** | `apps/desktop/src/plugins/<id>/plugin.tsx` | 应用内部组件，随应用一同分发 | 通过应用自身的 Vite 工具进行构建 |

这两种模式都遵循相同的 `HermesPlugin` 接口规范，都会显示在**设置 → 插件**页面中，且均可启用/禁用实时功能。本页面的所有内容都是以磁盘部署模式为基准编写的（即你和智能体所编写的插件）；[内置插件](#bundled-plugins)部分则说明了两者之间的差异。目前核心应用目录中并不包含任何桌面插件，相关的演示示例可在配套的[`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins)仓库中找到。

## 快速入门——创建你的第一个插件

创建 `$HERMES_HOME/desktop-plugins/hello/plugin.js` 文件（默认路径为 `~/.hermes/...`，若使用了自定义配置文件，则路径为 `~/.hermes/profiles/<name>/...`）。该文件夹的名称必须与插件的 `id` 相同。

```javascript
// ~/.hermes/desktop-plugins/hello/plugin.js
import { host, haptic, useValue } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'

function HelloPane() {
  const gateway = useValue(host.state.gateway)

  return jsxs('div', {
    className: 'flex h-full flex-col gap-2 p-3 text-sm',
    children: [
      jsx('div', { className: 'font-medium', children: 'Hello, Hermes' }),
      jsx('div', {
        className: 'text-(--ui-text-tertiary)',
        children: `gateway: ${gateway}`
      })
    ]
  })
}

export default {
  id: 'hello', // must match the folder name
  name: 'Hello',
  register(ctx) {
    ctx.register({
      id: 'pane',
      area: 'panes',
      title: 'hello',
      data: { placement: 'right', width: '260px' },
      render: () => jsx(HelloPane, {})
    })
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 130,
      render: () =>
        jsx('button', {
          type: 'button',
          className: 'px-1.5 text-[0.6875rem] text-(--ui-text-tertiary)',
          onClick: () => {
            haptic('tap')
            host.notify({ kind: 'info', message: 'Hello from my plugin!' })
          },
          children: 'hello'
        })
    })
  }
}
```

将其保存即可。该应用会实时监控 `desktop-plugins/` 目录，在几秒钟内加载该文件，并对后续的每一次保存进行即时热重载。如果相关内容未显示，请按下 ⌘K → **重新加载桌面插件**。若加载失败，系统会通过提示信息告知具体错误——请修复问题后再尝试保存。

:::注意：无需 JSX，也无需构建流程
磁盘文件是以**未编译状态**被加载的，因此 JSX 语法将无法被解析。应使用来自 `react/jsx-runtime` 的 `jsx()` / `jsxs()` 函数（或 `React.createElement`）来编写用户界面代码。唯一允许导入的模块为 `@hermes/plugin-sdk`、`react` 以及 `react/jsx-runtime`——其他所有模块均会被刻意设置为无法解析。
:::

## 插件规范

插件会默认导出一个 `HermesPlugin` 对象：

```ts
interface HermesPlugin {
  /** Stable slug — becomes the `plugin:<id>` source and the id namespace. */
  id: string
  /** Human name for Settings / about UI. Defaults to `id`. */
  name?: string
  /** Registers on load when the user hasn't chosen (default true). Set false
   *  for opt-in plugins: they inventory in Settings ▸ Plugins, off until the
   *  user flips the switch. */
  defaultEnabled?: boolean
  /** Called once at load; wire contributions through `ctx`. */
  register: (ctx: PluginContext) => void
}
```

`register`函数接收的是一个**具有作用域限制的**`PluginContext`对象。它从不直接操作注册表——该上下文会自动为每个贡献内容添加来源标签（`source: 'plugin:<id>'`），并为每个贡献ID标注命名空间（`<id>:<localId>`），因此两个插件绝不会发生冲突。

```ts
interface PluginContext {
  /** Resolved source tag, e.g. `'plugin:hello'`. */
  readonly source: string
  /** Register one contribution (id namespaced, source stamped). Returns a disposer. */
  register: (c: PluginContribution) => () => void
  /** Register several at once; the returned disposer removes all of them. */
  registerMany: (cs: PluginContribution[]) => () => void
  /** REST to this plugin's own backend namespace (`/api/plugins/<id>`). */
  rest: <T>(path: string, opts?: PluginRestOptions) => Promise<T>
  /** Live WebSocket to this plugin's own namespace. Returns a disposer. */
  socket: (path: string, onMessage: (data: unknown) => void) => () => void
  /** Plugin-scoped JSON persistence (keys live under `hermes.plugin.<id>.`). */
  storage: PluginStorage
}
```

**贡献值**是所有表面共有的基础数值：

```ts
interface Contribution {
  id: string          // you write the local id; the host namespaces it
  area: string        // WHERE it goes (a contribution-area constant)
  title?: string
  order?: number      // sort within the area (lower = earlier)
  when?: () => boolean // dynamic visibility; re-evaluated by the area
  enabled?: boolean
  render?: () => ReactNode  // the component to mount
  data?: unknown      // area-specific payload (see the cookbook)
}
```

根据具体应用场景，您需要提供 `render`、`data` 选项，或同时提供两者。

## 贡献模块——使用指南

从 SDK 中导入对应模块的常量；每个模块都有其专属的 `data` 数据结构。

| 显示区域 | `area` 值 | 需要提供的内容 |
|---------|--------|-------------|
| 布局面板 | `PANES_AREA` (`'panes'`) | `title` + `render` + `data: { placement, dock?, width?, height? }` |
| 全页内容 | `ROUTES_AREA` | `data: { path }` + `render` |
| 侧边栏导航 | `SIDEBAR_NAV_AREA` | `data: { path, label, codicon }` |
| 状态栏 | `STATUSBAR_AREAS.left` / `.right` | `render`（或以 `StatusbarItem` 形式的 `data`） |
| 标题栏 | `TITLEBAR_AREAS.left` / `.center` / `.right` | 以 `TitlebarTool` 形式的 `data`，或基于 mount 的 `<Contribute>` 元素 |
| ⌘K 调色板 | `PALETTE_AREA` | `data: PaletteContribution` |
| 键绑定 | `KEYBINDS_AREA` | `data: KeybindContribution` |
| 主题 | `THEMES_AREA` | 以 `DesktopTheme` 形式的 `data` |
| 组合器 | `COMPOSER_AREAS.*` | 渲染槽位，或中间件/插件提供者 |

### 面板

面板是布局树中的独立组件。`placement` 参数用于定义面板的层级关系——该面板会与该层级类型的现有面板堆叠（类似标签页形式）；之后用户可将其拖动到任意位置。

```javascript
ctx.register({
  id: 'pane',
  area: 'panes',
  title: 'my pane',
  data: { placement: 'right', width: '260px' },
  render: () => jsx(MyPane, {})
})
```

`placement` 的取值为 `'main' | 'left' | 'right' | 'top' | 'bottom'`。若希望将元素放置于特定的**边缘**而非堆叠在一起，可添加 `dock` 动作——该操作与将元素拖拽到面板上的放置区域相同。

```javascript
// Below the conversation, 200px tall.
data: {
  placement: 'bottom',
  dock: { pane: 'workspace', pos: 'bottom' },
  height: '200px'
}
```

`dock.pane` 可以是任意面板标识（`workspace` 为主线程；此外还包括 `sessions`、`terminal`、`files`、`review`、`logs`）；`dock.pos` 的取值为 `'top' | 'bottom' | 'left' | 'right' | 'center'`。建议同时指定 `width`/`height`，以避免该面板占据整个区域的一半。

### 页面与侧边栏导航

路由功能可在工作区面板中加载完整页面，其使用方式与各类内置视图相同。需配合侧边栏导航行（和/或调色板命令）才能方便地访问这些页面。

```javascript
import { ROUTES_AREA, SIDEBAR_NAV_AREA } from '@hermes/plugin-sdk'

ctx.registerMany([
  {
    id: 'page',
    area: ROUTES_AREA,
    data: { path: '/my-page' },
    render: () => jsx(MyPage, {})
  },
  {
    id: 'nav',
    area: SIDEBAR_NAV_AREA,
    data: { path: '/my-page', label: 'My Page', codicon: 'project' }
  }
])
```

`codicon` 是一种 [VS Code codicon](https://microsoft.github.io/vscode-codicons/dist/codicon.html) 标识。可通过 `host.navigate('/my-page')` 从任意位置导航至指定路径。

### 状态栏与标题栏

状态栏元素会显示在底部栏的左侧或右侧区域。最简单的实现方式是使用 `render` 函数；而对于普通按钮，则需以 `data` 的形式定义 `StatusbarItem`（结构为 `{ id, label?, icon?, detail?, variant?, menuItems?: … }`）。

```javascript
import { STATUSBAR_AREAS, TITLEBAR_AREAS } from '@hermes/plugin-sdk'

ctx.register({
  id: 'count',
  area: STATUSBAR_AREAS.right,
  order: 120,
  render: () => jsx(MyStatus, {})
})
```

标题栏工具以 `TitlebarTool` 数据格式存储在 `TITLEBAR_AREAS.left | .center | .right` 中，其数据结构为 `{ id, label, icon, active?, onSelect? }`。

### 调色板命令与快捷键绑定

```javascript
import { PALETTE_AREA, KEYBINDS_AREA } from '@hermes/plugin-sdk'

ctx.registerMany([
  {
    id: 'open',
    area: PALETTE_AREA,
    data: {
      id: 'my-page.open',
      label: 'Open My Page',
      keywords: ['my', 'page'],
      run: () => host.navigate('/my-page')
    }
  },
  {
    id: 'refresh',
    area: KEYBINDS_AREA,
    data: {
      id: 'my-page.refresh',
      label: 'Refresh My Page',
      category: 'My Plugin',
      defaults: ['mod+shift+r'],
      run: () => void doRefresh()
    }
  }
])
```

按键绑定可在设置中由用户自行重新配置；`defaults` 仅代表初始的绑定方式。

### 主题

主题贡献项目会将其完整的 `DesktopTheme` 结构作为 `data`（包括名称、标签、颜色等信息）一同提交。这样的主题会在主题选择器中以内置主题的形式显示。

```javascript
import { THEMES_AREA } from '@hermes/plugin-sdk'

ctx.register({ id: 'noir', area: THEMES_AREA, data: myDesktopTheme })
```

### Composer扩展

`COMPOSER_AREAS`（`top`、`bottom`、`leading`、`actions`、`attachments`、`middleware`）允许插件在消息编辑器周围添加控件、提供附件来源，或在消息发送前对其进行转换（例如使用`ComposerMiddleware`并传入`handler(draft) => draft | null`函数）。

### Mount-scoped chrome（“Contribute”模式）

`ctx.register`用于实现**永久性**的组件扩展。而对于那些需随已显示在屏幕上的组件一同存在或消失的组件（例如页面卸载时其自身的标题栏控件也会随之消失），则应在该组件内部渲染`<Contribute>`标签。

```javascript
import { Contribute, TITLEBAR_AREAS } from '@hermes/plugin-sdk'

jsx(Contribute, {
  area: TITLEBAR_AREAS.center,
  id: 'my-page:switcher', // namespace with your slug
  children: jsx(MySwitcher, {})
})
```

该代理会在挂载时自动注册，而在卸载时则会自动注销。

## 主机 API

在插件中的任何位置均可访问 `host` 上的所有资源。状态原子为只读属性——可在处理程序中通过 `.get()` 方法读取，也可在组件中通过 `useValue(atom)` 方法进行订阅。

```ts
host.state.activeSessionId  // ReadableAtom<string | null>
host.state.cwd              // ReadableAtom<string>
host.state.gateway          // ReadableAtom<string>  ('idle' | 'connecting' | 'open' | …)
host.state.model            // ReadableAtom<string>
host.state.profile          // ReadableAtom<string>
host.state.viewport         // ReadableAtom<{ width, height, narrow }>

host.notify({ kind, message, title?, detail?, action? })  // toast; returns id
host.notifyError(error, fallbackMessage)                   // toast an error
host.navigate('/route')                    // hash-route navigation
host.onEvent(type, fn)                     // gateway event stream ('*' = all); returns disposer
host.logs(...)                             // tail an app log file
host.status()                              // one-shot system status snapshot
host.restartGateway()                      // restart the backend gateway
host.request<T>(method, params?)           // gateway JSON-RPC — the real power
```

`host.request` 与应用程序本身所使用的 JSON-RPC 协议完全一致（包括会话管理、配置设置、技能调用、定时任务、看板功能等）。`host.onEvent` 则用于实时传输网关事件（如消息变更、会话生命周期状态、工具使用情况等）。各个监听器之间是相互隔离的——在某个监听器中抛出的异常不会影响应用程序的正常调度。每一个 `host` 接口都具有异步安全性：即使内部辅助函数抛出同步异常（例如在纯浏览器环境中没有桌面桥接支持），也只会被 `.catch()` 捕获并处理，而不会导致错误边界崩溃。

## 数据层 — React Query + nanostores

所有插件都会共享应用程序的单一 `QueryClient` 实例，因此插件的查询操作也会像核心界面一样进行缓存、去重、轮询以及失效处理——无需自行实现数据获取逻辑。

```javascript
import { useQuery, useMutation, useQueryClient, atom, computed, useValue } from '@hermes/plugin-sdk'

function MyPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['my-plugin', 'items'],
    queryFn: () => host.request('my.list', {})
  })
  // …
}
```

对于触发器与其面板（或轮询循环）之间需要共享的状态，应使用与 `host.state` 所采用的相同机制，即 `atom` 或 `computed`。可在渲染该值的叶子组件中通过 `useValue` 函数进行订阅。若需从 React **外部**（例如通过传入的 `ctx.socket` 数据）使查询失效，则需导入共享的 `queryClient` 对象：

```javascript
import { queryClient } from '@hermes/plugin-sdk'

ctx.socket('/events', () => {
  queryClient.invalidateQueries({ queryKey: ['my-plugin', 'items'] })
})
```

## UI组件库与主题系统

直接导入应用程序的原始组件，让界面默认呈现原生风格：

> `Button`、`Input`、`Textarea`、`Select*`、`Switch`、`Checkbox`、
> `SegmentedControl`、`Tabs*`、`Dialog*`、`ConfirmDialog`、`DropdownMenu*`、
> `ContextMenu*`、`Popover*`、`Tip`/`Tooltip*`、`Badge`、`Kbd`/`KbdGroup`、
> `SearchField`、`ScrollArea`、`Separator`、`Skeleton`、`GlyphSpinner`、`Loader`、
> `EmptyState`、`ErrorState`、`CopyButton`、`StatusDot`、`LogView`、`Codicon`、
> `DecodeText`。

此外还包括辅助组件：`cn`（类合并功能）、`icons.*`（应用程序自带的Lucide图标集）、`haptic`、
`profileColor` / `profileColorSoft`（用于标识唯一性的颜色值）、时间格式化函数`relativeTime` / `fmtDateTime` / `fmtDayTime` / `coarseElapsed`、
`useI18n`（支持本地化文本——确保插件始终可翻译），以及`evaluateRuntimeReadiness`函数。

**应使用主题变量来设置样式，切勿硬编码颜色值。** 各界面元素本身已位于应用程序编辑器的背景之上，无需修改背景色，只需为其他所有元素使用变量，例如：`var(--ui-text-secondary)`、`var(--ui-text-tertiary)`、
`var(--ui-text-quaternary)`、`var(--ui-stroke-secondary)`、`var(--ui-accent)`。对于Canvas绘图场景，可通过
`getComputedStyle(canvas).getPropertyValue('--ui-accent')`一次性获取这些颜色值。正是这一机制使得插件能够随主题变化自动调整外观。

## 插件的后端支持

如果您的插件需要执行服务器端操作，只需提供一个Python文件`plugin_api.py`，并通过`ctx.rest` / `ctx.socket`来调用它——这两个接口**从设计上就属于您插件专用**的命名空间。

### Python实现方式

桌面端插件可复用仪表板插件的后端架构。只需将后端代码放入普通Hermes插件的`dashboard/`子文件夹中，并在`manifest.json`文件中进行相应声明即可：

```
~/.hermes/plugins/<id>/
└── dashboard/
    ├── manifest.json      # { "name": "<id>", "api": "plugin_api.py" }
    └── plugin_api.py      # exports `router = APIRouter()`
```

```python
# plugin_api.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/board")
async def board():
    return {"items": ["one", "two", "three"]}

@router.post("/action")
async def action(body: dict):
    return {"ok": True, "received": body}
```

路由会挂载在 `/api/plugins/<id>/` 下（例如 `GET /api/plugins/<id>/board` 等）。后端代码在网关进程内部运行，因此可以直接从 hermes-agent 代码库中导入相关模块（如 `hermes_state`、`hermes_cli.config` 等）。有关完整的后端参考信息，请参阅[扩展控制面板 → 后端 API 路由](/user-guide/features/extending-the-dashboard#backend-api-routes)，其挂载方式与此相同。

:::注意 Python 后端是单独启用的
在桌面端的**设置 → 插件**面板中启用插件仅是前端渲染器的操作，并不会导入 Python 代码。只有当用户自定义插件的 `plugin_api.py` 被列入 `config.yaml` 中的 `plugins.enabled` 允许列表（且不在 `plugins.disabled` 列表中）时，才会被导入。项目自带的插件（位于 `./.hermes/` 目录下）则永远不会自动导入 Python 代码。这是出于安全考虑而设置的限制，并非疏忽（GHSA-mcfc-hp25-cjv7）。
:::

### 从插件中调用它

```javascript
register(ctx) {
  // REST — namespace-relative path.
  const load = () => ctx.rest('/board')                 // GET /api/plugins/<id>/board
  const act  = () => ctx.rest('/action', { method: 'POST', body: { go: true } })

  // Live twin — a WebSocket to your own namespace.
  const stop = ctx.socket('/events', frame => {
    queryClient.invalidateQueries({ queryKey: [ctx.source, 'board'] })
  })
}
```

`ctx.rest` 具备配置文件感知功能，会阻止路径遍历（如 `..`），因此你绝无法通过它来调用其他插件的 API 或核心路由。`PluginRestOptions` 的结构为 `{ method?, body?: { filename, contentType?, bytes }, timeoutMs? }`。

`ctx.socket` 会在被释放前以退避机制自动重连。在基于 OAuth 的远程服务中，该功能实际上相当于无操作（因为一次性使用的 WS 令牌由核心系统管理）——应将其视为轮询方式的加速工具，而非替代品。无论如何，每个客户端都需要保留轮询作为备用方案，因为任何 Socket 都可能中断连接。

对于全局数据（非你自己的命名空间），请改用 `host.request`（JSON-RPC）和 `host.onEvent`（网关事件流）。

## 设置、启用状态与存储

无论是否已启用，所有插件都会显示在 **Settings → Plugins** 中，用户可在那里实时切换插件状态（无需重启应用）、查看其所在文件夹或重新扫描插件。用户的设置会被保留：

- 尚未做选择 → 采用插件自身的 `defaultEnabled` 值（默认为 `true`）。若要发布需用户主动启用的插件，可将 `defaultEnabled` 设置为 `false`，这样该插件在用户开启前将处于隐藏状态。
- 已明确选择 → 该设置会被持久化，并在应用重启后依然有效。已禁用的插件将保持禁用状态——无需强行启用，因为这是用户主动关闭的。

你可以使用 `ctx.storage` 来保存自己的状态，其命名空间为你的插件标识（`hermes.plugin.<id>.*`），这样其他插件就无法读取或篡改你的数据。

```javascript
ctx.storage.set('lastTab', 'board')
const tab = ctx.storage.get('lastTab', 'summary')
ctx.storage.remove('lastTab')
```

## 内置插件

插件可被打包到 `apps/desktop/src/plugins/<id>/plugin.tsx` 中（默认需导出 `HermesPlugin`）。系统在启动时会通过 `discoverBundledPlugins()` 自动发现这些插件——无需手动导入，也无需修改注册表——并且它们会像磁盘插件一样共享完整的资源清单以及实时的启用/禁用状态。两者的主要区别如下：

1. 它们会经过应用的 Vite 构建流程，因此你可以使用**真正的 JSX**语法，并通过 `@hermes/plugin-sdk` 别名来导入 SDK。
2. 它们仍受限于仅能使用 `@hermes/plugin-sdk` 和 `react`，无法访问应用内部的 `@/…` 相关代码。

目前核心代码树中不包含任何桌面插件；这样可以保持打包后的应用结构整洁，相关示例则位于 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins) 仓库中。

## 安全模型

加载的插件会在渲染环境中以 ESM 方式运行，并拥有**完整的应用权限**——包括 React 单例、整个 SDK（如 `host.request` 网关 RPC、`ctx.rest`、存储功能以及导航功能）。加载器所提供的隔离机制仅限于**错误隔离**：插件无法导致应用崩溃（其功能被限制在错误范围内，监听器也被隔离），但可以执行应用允许的任何操作。

对于**本地源**而言，这种设计是可接受的——磁盘文件本来就可以在用户的机器上运行代码——正因如此，磁盘插件机制仅会加载由用户（或其智能体）编写的本地文件。可选的 `integrity`（如 `sha256-…`）校验仅能证明字节内容与哈希值一致，**并不具备沙箱功能**。未来的远程源插件机制在启用前需要真正的隔离措施（如 iframe/worker、CSP 限制以及能力管控），请勿将此流程视为安全的信任边界。

## 常见问题

- **磁盘插件中 JSX 无法解析**。这类文件是以未编译的形式加载的，因此需使用 `jsx()` / `jsxs()`（或 `React.createElement`）函数，而不能直接使用 JSX 语法。（内置插件经过构建处理，因此可以使用 JSX。）
- **仅三种指定符可以被识别**：`@hermes/plugin-sdk`、`react`、`react/jsx-runtime`。任何其他导入语句都会导致加载时立即出现错误。
- **切勿硬编码颜色值**（如 `#000`、`black`、`rgb(...)`）。请勿直接设置背景色，所有颜色都应使用主题变量（如 `var(--ui-*)`）来定义。
- **仅引用已导入的组件**。如果遗漏了某个组件的导入（例如 `StatusDot`），在渲染时就会引发 `ReferenceError` 错误。请仔细检查 `jsx()` 调用中的所有标识符是否都出现在导入语句中。
- **在处理函数中应以命令式方式读取状态**（如使用 `$atom.get()`），切勿从渲染闭包中读取——否则快速发生的事件将会获取到过时的值。应在实际渲染该值的节点中使用 `useValue` 进行订阅。
- **Canvas 面板必须通过 `ResizeObserver` 监听其容器尺寸变化，并动态调整 Canvas 的宽高属性（而非仅依赖 CSS）——因为面板尺寸会不断变化。**
- **使用 `host.request` 时，查询频率不宜超过几秒一次**。建议优先使用 `host.onEvent` / `ctx.socket`，并让 React Query 负责去重处理。
- **在 OAuth 远程环境中，`ctx.socket` 为无效功能**。务必准备相应的轮询作为备用方案。

## 参考资料

### SDK 导出内容概览

| 类别 | 导出项 |
|------|--------|
| 主机对象 | `host`（包含 `.state.*`、`.notify`、`.notifyError`、`.navigate`、`.onEvent`、`.logs`、`.status`、`.restartGateway`、`.request` 等属性） |
| 插件接口 | `HermesPlugin`、`PluginContext`、`PluginContribution`、`PluginStorage`、`PluginRestOptions`、`Contribution` |
| 区域常量 | `PANES_AREA`、`ROUTES_AREA`、`SIDEBAR_NAV_AREA`、`STATUSBAR_AREAS`、`TITLEBAR_AREAS`、`PALETTE_AREA`、`KEYBINDS_AREA`、`THEMES_AREA`、`COMPOSER_AREAS` |
| 区域数据结构 | `RouteContribution`、`SidebarNavContribution`、`StatusbarItem`、`TitlebarTool`、`PaletteContribution`、`KeybindContribution`、`ComposerMiddleware`、`ComposerAttachmentProvider` |
| React / 状态管理 | `useValue`、`atom`、`computed`、`useQuery`、`useMutation`、`useQueryClient`、`queryClient`、`Contribute` |
| UI 组件库 | `Button`、`Input`、`Textarea`、`Select*`、`Switch`、`Checkbox`、`SegmentedControl`、`Tabs*`、`Dialog*`、`ConfirmDialog`、`DropdownMenu*`、`ContextMenu*`、`Popover*`、`Tip`/`Tooltip*`、`Badge`、`Kbd`/`KbdGroup`、`SearchField`、`ScrollArea`、`Separator`、`Skeleton`、`GlyphSpinner`、`Loader`、`EmptyState`、`ErrorState`、`CopyButton`、`StatusDot`、`LogView`、`Codicon`、`DecodeText` |
| 辅助工具 | `cn`、`icons`、`haptic`、`useI18n`、`profileColor`、`profileColorSoft`、`relativeTime`、`fmtDateTime`、`fmtDayTime`、`coarseElapsed`、`evaluateRuntimeReadiness` |

最新的完整导出列表可查看 `apps/desktop/src/sdk/index.ts` 文件。

### 智能体：`hermes-desktop-plugins` 技能

当智能体编写桌面插件时，应加载内置的 **`hermes-desktop-plugins`** 技能——该技能以智能体可理解的形式呈现了与本页面相同的接口规范，同时还提供了可直接复制的 `templates/plugin.js` 模板。本页面是为人类用户和开发者提供的参考资料，而该技能则是实际开发时的操作检查清单。

## 故障排除

**我的插件没有显示出来。**请确认文件位于 `$HERMES_HOME/desktop-plugins/<id>/plugin.js`，且文件夹名称与导出时指定的 `id` 一致。随后按下 ⌘K 并选择 **“重新加载桌面插件”**。检查应用中是否有提示错误原因的弹窗，并通过 `hermes logs gui -f` 命令持续查看日志。

**加载时出现“不支持的导入语句”错误。**磁盘插件仅允许导入 `@hermes/plugin-sdk`、`react` 和 `react/jsx-runtime` 这三个模块。请删除其他所有导入语句。

**`jsx` 元素无法渲染或抛出 `ReferenceError` 错误。**这说明在 `jsx()` 调用中使用的某个标识符未被导入。请将其添加到导入语句中。

**`ctx.rest` 返回 404 错误。**说明后端服务尚未启动：请确认 `~/.hermes/plugins/<id>/dashboard/manifest.json` 文件中包含 `"api": "plugin_api.py"` 这一配置，同时确保该插件已在 `config.yaml` 的 `plugins.enabled` 列表中启用，最后重启网关服务（后端路由会在启动时加载）。可通过查看 `~/.hermes/logs/errors.log` 文件中的 “Failed to load plugin <id> API routes” 错误信息来定位问题。

**`ctx.socket` 从未触发过。**在 OAuth 远程环境中，该功能按设计本就是无效的——请使用轮询作为备用方案。在其他情况下，请确认后端在其命名空间下确实提供了对应的 `@router.websocket(...)` 路由。

**切换主题后颜色显示异常。**这可能是由于你硬编码了颜色值所致。请将其替换为 `var(--ui-*)` 形式的主题变量。
