---
sidebar_label: "Desktop Plugin SDK"
title: "Desktop Plugin SDK (@hermes/plugin-sdk)"
description: "Extend the native Hermes Desktop app — panes, pages, sidebar nav, status bar, palette commands, keybinds, themes, and a scoped backend namespace, with one import and no build step."
---

# 桌面插件 SDK

原生 [Hermes Desktop](/user-guide/desktop) 应用采用贡献驱动的开发模式：窗口中的所有组件——包括各个面板、路由、侧边栏导航、状态栏元素、调色板项、快捷键绑定以及主题设置——都会被注册到一个中央注册表中。核心应用对自身组件的注册方式与插件完全一致，因此插件才是整个系统的核心，而非后来临时添加的附属组件。

**桌面插件**实际上是一个单一的 ESM 文件，该文件会默认导出 `HermesPlugin` 接口。插件只需导入一个模块 `@hermes/plugin-sdk`，即可获取所有必要功能：应用的实时状态、JSON-RPC 接口、带作用域限制的 REST/Socket 后端命名空间、React Query 库，以及应用自带的 UI 组件库，这使得插件界面能够以原生风格呈现。无需克隆代码仓库，无需执行 `npm run build` 命令，也无需修改应用源码。只需将插件文件放入 `$HERMES_HOME/desktop-plugins/<id>/plugin.js` 目录中，应用即可在几秒钟内加载该插件，并在每次保存时实现热重载。

:::warning 这并非网页控制台插件 SDK。  
在 Hermes 中，“插件”这一概念包含多种不同的含义。本页面介绍的是**原生桌面应用**（`hermes desktop`）的 SDK，即 `@hermes/plugin-sdk` 模块以及 `$HERMES_HOME/desktop-plugins/` 目录。而**网页控制台**（`hermes dashboard`）则拥有独立的插件系统，该系统基于 `window.__HERMES_PLUGIN_SDK__` 并使用 `manifest.json` 进行配置，相关说明请参阅[扩展控制台功能](/user-guide/features/extending-the-dashboard)。Python CLI/网关插件的相关文档则位于[构建 Hermes 插件](/developer-guide/plugins)页面。这三种插件之间不会共享代码、API 或部署机制。仅有桌面版与控制台版 SDK 会共享后端的 `plugin_api.py` 命名空间（`/api/plugins/<id>`）。:::

## 心智模型  

该 SDK 采用了 VS Code 的模块模型。插件开发者只需导入一个模块，且绝不能触碰应用的内部实现（这些内容在打包后的插件中会被屏蔽，而在磁盘插件中则无法被解析）。插件的功能层级分为多个等级：

- **`host.state.*`** — 提供对应用实时状态（nanostore原子）的只读访问，包括活跃会话、单次会话的忙碌状态、当前工作目录、网关套接字状态、模型信息、用户配置以及视图窗口内容。此处所说的“gateway”指的是WebSocket连接，而非表示“忙碌中”的状态。
- **`host.*` 操作** — 为开发者精心挑选的安全操作指令，包括显示提示信息、导航、查看日志尾部分、重启网关以及订阅网关事件流。
- **`host.request`** — 对应网关的JSON-RPC接口，可用于获取会话信息、配置参数、技能相关数据以及定时任务执行结果——即应用自身所需调用的所有功能。
- **`ctx.rest` / `ctx.socket`** — 若您编写了 `plugin_api.py` 文件，这部分则用于定义插件自身的后端命名空间（路径为 `/api/plugins/<id>`）。
- **`ui.*`** — 对应设计语言部分，包含应用的实际组件、主题变量、图标以及格式化函数，确保您的界面能与应用实现像素级的一致。

## 两种交付方式

| 方式 | 存放位置 | 使用者 | 构建步骤 |
|------|---------|-------|----------|
| **磁盘部署**（推荐） | `$HERMES_HOME/desktop-plugins/<id>/plugin.js` | 用户、智能体 | 无需额外构建步骤——采用纯ESM格式，以未编译状态直接加载 |
| **统一包部署** | `$HERMES_HOME/plugins/<id>/desktop/plugin.js` | 同时需要提供智能体端代码的插件 | 无需额外构建步骤——沿用相同的磁盘部署流程 |
| **打包嵌入部署** | `apps/desktop/src/plugins/<id>/plugin.tsx` | 内置在应用中，随应用一同分发 | 通过应用自身的Vite工具进行构建 |
这三种插件均遵循相同的 `HermesPlugin` 接口规范，会显示在 **Settings → Plugins** 页面中，并可开启或关闭实时功能。所谓“统一包”，实际上只是在你代理插件文件夹内的磁盘门扫描相关内容——详情请参阅 [一个包，两种 SDK](#one-package-both-sdks)。本页面的所有内容都是基于磁盘门机制编写的（即由你和代理程序共同写入的数据）；[打包插件](#bundled-plugins) 部分则说明了两者之间的差异。Radio 默认以仅包含 SDK 的打包插件形式提供。若需实现免费实时流播放、电台搜索以及带有音频响应波形的状态栏播放控制功能，可在 **Settings → Plugins** 中开启该插件。它在禁用状态下不会对系统产生任何影响，仅使用现有的插件切换机制。相关演示代码可直接在配套的 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins) 仓库中查看。

## 快速入门——创建你的第一个插件

创建文件 `$HERMES_HOME/desktop-plugins/hello/plugin.js`（默认路径为 `~/.hermes/...`，若使用了自定义配置文件，则路径为 `~/.hermes/profiles/<name>/...`）。该文件夹的名称必须与插件的 `id` 相同。

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

将其保存即可。该应用会实时监控 `desktop-plugins/` 目录，在几秒内加载该文件，并对后续的每一次保存进行即时热重载。如果相关功能仍未出现，请按下 ⌘K → **重新加载桌面插件**。若加载失败，系统会显示具体的错误提示——请修复问题后再尝试保存。

:::注意：无需 JSX，也无需构建流程
磁盘中的文件是以**未编译状态**被加载的，因此 JSX 语法将无法被解析。应使用来自 `react/jsx-runtime` 的 `jsx()` / `jsxs()` 函数（或 `React.createElement`）来编写用户界面代码。唯一允许导入的模块为 `@hermes/plugin-sdk`、`react` 以及 `react/jsx-runtime`——其他所有模块均会被刻意设置为无法解析。
:::

## 插件契约

插件默认会导出一个 `HermesPlugin` 对象：

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

`register`函数接收的是一个**限定作用域的**`PluginContext`对象。它从不直接操作注册表——该上下文会自动为每个贡献内容添加来源标签（`source: 'plugin:<id>'`），并为每个标识符标注命名空间（`<id>:<localId>`），因此两个插件绝不会发生冲突。

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
  /** The curated OS door: native notification, open-external, reveal-in-file-manager, clipboard. */
  os: PluginOs
  /** Plugin-scoped JSON persistence (keys live under `hermes.plugin.<id>.`). */
  storage: PluginStorage
}
```

**贡献值**是每个表面都共有的基础数值：

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

根据应用场景的不同，您需要提供 `render`、`data` 选项，或两者兼备。

## 贡献模块——使用指南

从 SDK 中导入对应模块的常量；每个模块都有其专属的 `data` 数据格式。

| 区域 | `area` 值 | 需要提供的内容 |
|-----|----------|--------------|
| 布局面板 | `PANES_AREA` (`'panes'`) | `title` + `render` + `data: { placement, dock?, width?, height? }` |
| 全页内容 | `ROUTES_AREA` | `data: { path }` + `render` |
| 侧边栏导航 | `SIDEBAR_NAV_AREA` | `data: { path, label, codicon }` |
| 状态栏 | `STATUSBAR_AREAS.left` / `.right` | `render`（或以 `StatusbarItem` 形式的 `data`） |
| 标题栏 | `TITLEBAR_AREAS.left` / `.center` / `.right` | 以 `TitlebarTool` 形式的 `data`，或基于 mount 的 `<Contribute>` 元素 |
| ⌘K 调色板 | `PALETTE_AREA` | `data: PaletteContribution` |
| 键绑定 | `KEYBINDS_AREA` | `data: KeybindContribution` |
| 主题 | `THEMES_AREA` | 以 `DesktopTheme` 形式的 `data` |
| 组合器 | `COMPOSER_AREAS.*` | 渲染槽位，或中间件/插件提供者 |

### 布局面板

布局面板是布局树中的独立单元。`placement` 参数用于定义该面板的逻辑位置——它会与具有相同位置的现有面板堆叠（类似标签页形式）；之后用户可自由拖动该面板至任意位置。

```javascript
ctx.register({
  id: 'pane',
  area: 'panes',
  title: 'my pane',
  data: { placement: 'right', width: '260px' },
  render: () => jsx(MyPane, {})
})
```

`placement` 的取值为 `'main' | 'left' | 'right' | 'top' | 'bottom'`。若希望将元素放置在特定的**边缘**而非堆叠在一起，可添加 `dock` 动作——该操作与将元素拖拽到面板上的放置区域完全相同。

```javascript
// Below the conversation, 200px tall.
data: {
  placement: 'bottom',
  dock: { pane: 'workspace', pos: 'bottom' },
  height: '200px'
}
```

`dock.pane` 可以是任意面板标识符（`workspace` 为主线程；此外还包括 `sessions`、`terminal`、`files`、`review`、`logs`）；`dock.pos` 的取值为 `'top' | 'bottom' | 'left' | 'right' | 'center'`。建议同时指定 `width`/`height`，以避免该面板占据整个区域的一半。

若关闭插件生成的唯一一个面板，该插件将会被禁用，但可通过 **Settings → Plugins** 重新启用它。当某个插件生成多个面板时，关闭其中一个仅会消失该面板，而该插件的其他面板、命令及中间件仍会保持活跃状态。使用 **Reset layout** 可以恢复已被关闭的插件面板。

### 页面与侧边栏导航

路由功能可在工作区面板中加载完整页面，其用法与任何内置视图相同。只需为其搭配侧边栏导航行（和/或调色板命令），即可方便地访问该页面。

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

状态栏元素会显示在底部栏的左侧或右侧区域。最简单的实现方式是使用 `render` 函数；而对于普通按钮，则可将 `data` 作为 `StatusbarItem` 的属性使用（格式为 `{ id, label?, icon?, detail?, variant?, menuItems?, … }`）。

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

快捷键可在设置中由用户自行重新绑定；`defaults`仅代表初始的绑定方式。

### 主题

主题贡献项目会将其完整的`DesktopTheme`作为`data`内容一同提交（包括名称、标签、颜色等信息）。这样的主题会在主题选择器中以内置主题的形式显示。

```javascript
import { THEMES_AREA } from '@hermes/plugin-sdk'

ctx.register({ id: 'noir', area: THEMES_AREA, data: myDesktopTheme })
```

注册主题仅会将其列出，而不会自动选中它。`useTheme()`函数可读取组件的当前显示样式（如`theme`、`themeName`、`availableThemes`、`resolvedMode`），并可通过相应函数（如`setTheme`、`setMode`、`previewTheme`）来更改这些样式。

```javascript
import { Button, useTheme } from '@hermes/plugin-sdk'

function ThemePicker() {
  const { availableThemes, setTheme, themeName } = useTheme()

  return availableThemes.map(t => (
    <Button key={t.name} disabled={t.name === themeName} onClick={() => setTheme(t.name)}>
      {t.label}
    </Button>
  ))
}
```

若切换是由渲染之外的因素触发的——例如连接网关、套接字事件或任何 `host.onEvent` 回调函数——则不存在可用于挂载钩子的组件。此时应使用 `requestTheme(name)` 函数。对于无法解析的名称，系统会直接拒绝请求而不会强制使用默认皮肤，因此该函数的返回值同时起到了可用性检查的作用；此外，错误的名称也绝不可能在后台悄无声息地改变某人的外观设置。

```javascript
import { host, requestTheme } from '@hermes/plugin-sdk'

host.onEvent('gateway.ready', () => {
  if (!requestTheme('noir')) {
    host.notifyError('Connected, but the noir theme is not installed.')
  }
})
```

根据配置文件设置，两扇门的状态会持续保留，因此通过插件驱动的开关操作效果与手动开启完全一致。若希望仅调整*当前生效*的主题而非完全替换它，可使用`setAccentOverride(hex)`函数进行设置，并在`ctx.onDispose`中清除该设置——附带的`accent`插件即为相关实现示例。

### Composer扩展

`COMPOSER_AREAS`（`top`、`bottom`、`leading`、`actions`、`attachments`、`middleware`）允许插件在消息编辑器周围添加控件、提供附件来源，或在消息发送前对其进行转换（例如使用`ComposerMiddleware`并配置`handler(draft) => draft | null`）。

### 转录指令——模型所引用的内联组件

`TRANSCRIPT_DIRECTIVE_AREA`可将转录内容本身视为可编辑区域。通过注册带名称的指令，智能体便能在助手消息中以`::name{key="value"}`格式的内联段落来渲染您的组件：

```javascript
import { TRANSCRIPT_DIRECTIVE_AREA } from '@hermes/plugin-sdk'

ctx.register({
  id: 'task-card',
  area: TRANSCRIPT_DIRECTIVE_AREA,
  data: {
    name: 'task', // the model writes ::task{id="BB-12"}
    render: ({ attrs, streaming }) => jsx(TaskCard, { taskId: attrs.id, streaming })
  }
})
```

主机为保障界面安全而遵循的规则如下：

- 指令必须为**完整的段落**——若在正文中间出现 `::name` 格式，该部分仍属于正文，因此插件组件绝无法篡改正在显示的文本。
- 属性属于**不可信的模型输出**（仅为 `key="value"` 的键值对及字符串形式）。请自行验证相关字段，切勿基于不确定的信息进行渲染。
- 若某个指令未被任何插件注册使用，它将始终以原始段落的形式呈现——即便相关插件处于关闭状态，也不会出现任何异常。
- 所有渲染内容都会被包裹在错误处理边界中：一旦发生异常，系统会显示内联错误提示，而不会让页面完全无响应。
- 当名称发生冲突时，**最先注册的插件**将占据该名称；建议为命名空间使用包含自定义标识符的独特名称（如 `myplugin-board`，而非单纯的 `board`）。
Core框架内置了一个作为参考用例的指令：`::preview{file="…"}`。该指令会**在消息内部实时渲染**工作区HTML文件——即一个具有不可见源地址的沙箱化`srcdoc` iframe，其中的脚本可以正常运行，组件也具备完全的交互性；同时不会访问应用程序、其存储数据或桥梁组件。该iframe的尺寸会自动适配内容大小（高度实时调整，宽度则取自内容本身的跨度，在消息流中保持左对齐）。此外，还有一个主题预处理阶段，负责为文档提供应用程序已解析的样式参数（如`--foreground`、`--muted-foreground`、`--accent`、`--border`、`--card`）、应用程序字体以及透明背景——这样一来，呈组件形状的HTML内容会看起来像原生元素，而完整页面则能保持原有的设计风格。对于非HTML目标或远程网关，则会回退到传统的预览卡片形式。你可以在某个技能中向智能体说明对应的指令（智能体便是通过这种方式学会如何使用该指令的）。

被预览的组件还可以**进行反馈**。在那个iframe内部，使用`window.hermes.send('get-price eth')`（或声明式的`<button data-hermes-send="get-price eth">`——无需脚本）即可将相应请求以用户轮次的身份发送给智能体，且操作发生在屏幕之外：不会出现任何提示气泡占据文本区域，组件的更新内容即为可见的响应。这一轮次仍然是有效的——它能够唤醒智能体，遵循消息编辑器的路由/队列规则，并会被保留下来（可手动标记为`hidden`），这样继续处理功能及会话数据库就能保存完整的记录。此外，提示文本会被截断，长度上限为500个字符，且每个iframe每秒最多只能发送一条请求。

### Mount作用域下的扩展功能（`Contribute`）

`ctx.register` 用于进行**永久性**的贡献。如果某个组件已经在屏幕上显示，且 Chrome 应随该组件的消失而关闭（例如页面卸载时页面自身的标题栏控件也会随之消失），则应在其内部渲染 `<Contribute>`。

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

在插件中的任何位置均可访问 `host` 上的所有资源。状态原子为只读属性——可在处理函数中通过 `.get()` 方法读取，也可在组件中通过 `useValue(atom)` 方法进行订阅。

```ts
host.state.activeSessionId  // ReadableAtom<string | null>
host.state.awaitingResponse // ReadableAtom<boolean>  true until the first assistant payload
host.state.busy             // ReadableAtom<boolean>  focused chat is working after a send
host.state.busyBySession    // ReadableAtom<Record<string, boolean>>  runtime id → mid-turn
host.state.focusedSessionId // ReadableAtom<string | null>  (runtime id of the FOCUSED session — tile-aware; prefer for session.* RPC)
host.state.focusedSessionProfile // ReadableAtom<string>  (owner profile of the focused chat — prefer over `profile` for per-bot/profile readouts)
host.state.focusedStoredSessionId // ReadableAtom<string | null>  (durable id — navigation / session-list matching)
host.state.focusedUsage     // ReadableAtom<UsageStats | null>  (live streamed usage of the focused session, no RPC needed)
host.state.cwd              // ReadableAtom<string>
host.state.gateway          // ReadableAtom<string>  socket state ('idle' | 'connecting' | 'open' | …)
host.state.model            // ReadableAtom<string>
host.state.profile          // ReadableAtom<string>
host.state.viewport         // ReadableAtom<{ width, height, narrow }>
```

`host.state.gateway` 指的是 WebSocket 连接状态，而非当前是否正处于对话轮次中。在套接字处于 `open` 状态时，一个会话可能正处于对话轮次中；而同一时间另一个会话则可能处于空闲状态。应禁止从**当前活跃会话**的轮次忙碌状态标志（即 `host.state.busyBySession[sessionId]` 或该会话的 `view.$busy`）触发 composer 或插件相关操作——绝不能从 `gateway` 状态或全局进程的忙碌标志来触发此类操作。

```ts
host.notify({ kind, message, title?, detail?, action? })  // toast; returns id
host.notifyError(error, fallbackMessage)                   // toast an error
ctx.os.notify({ title, body?, silent?, icon?, activate?, onActivate?, actions? })
                                           // native OS notification (attributed to your plugin)
ctx.os.openExternal(url)                   // OS default handler (browser, mail, spotify:) → Promise<boolean>
ctx.os.revealPath(path)                    // reveal in Finder / Explorer → Promise<boolean>
ctx.os.writeClipboard(text)                // system clipboard → Promise<boolean>
host.navigate('/route')                    // hash-route navigation
host.openSession(id, { profile?, intent? }) // open a stored session core-style;
                                           //   profile: soft-swap to that profile's backend first
                                           //   intent: 'in-place' (default) | 'stack' | 'tab' | 'window'
host.newChat(profile?)                     // fresh chat draft, optionally in another profile
host.openWorkspace(id, { render, title?, minWidth?, onClose? })
                                           // dock a plugin-rendered tab into the MAIN
                                           //   workspace zone and reveal it; returns a disposer
host.paneVisibility(paneId)                // ReadableAtom<boolean> — is a contributed pane
                                           //   actually on screen (its zone's active tab)?
host.onEvent(type, fn)                     // gateway event stream ('*' = all); returns disposer
host.logs(...)                             // tail an app log file
host.status()                              // one-shot system status snapshot
host.restartGateway()                      // restart the backend gateway
host.profileRoutes()                       // [{ profile, targetProfile, connectionId, mode }]
host.requestProfile<T>(route, method, params?)   // registry-routed RPC; no foreground swap
host.requestProfile<T>(profile, method, params?) // legacy v1/local overload
host.request<T>(method, params?)           // active-gateway JSON-RPC — the real power
```

`host.request` 与应用程序本身所使用的 JSON-RPC 接口完全相同（包括会话、配置、技能、定时任务、看板等功能）。`host.requestProfile` 可以接收来自 `host.profileRoutes()` 的描述符，然后通过对应的注册表源和配置文件来路由该 RPC 请求，而不会改变当前正在使用的聊天界面或网关。仅支持基于配置文件的调用方式仅保留用于纯本地/旧版架构；具备注册表识别功能的插件应传递该描述符，以避免两个使用相同配置文件名的来源发生冲突。

`host.openWorkspace(id, { render, title?, minWidth?, onClose? })` 会将由插件生成的视图以标签页的形式嵌入到**主工作区区域**——即会话卡片和预览内容所显示的中央区域——并使其可见。若再次使用相同的 `id` 调用该函数，将会在原有位置刷新内容并重新加载该标签页，而不会创建重复的标签页。关闭标签页（通过标签页上的关闭按钮或按 ⌘W 键）会解除其关联关系，并触发对应的 `onClose` 回调函数；返回的处置器会以编程方式将其关闭。建议通过 `typeof host.openWorkspace === 'function'` 来检测该功能，若在旧版桌面版本中无法使用，则可回退到常规的插件面板——Bot Mode 的群组聊天室即为该功能的参考实现方式（在有主窗口支持时占据整个主窗口，否则以面板形式显示）。

`host.paneVisibility(paneId)` 方法会返回一个只读的响应式原子值，当某个贡献式面板实际显示在屏幕上时该值为 `true`：即该面板存在于布局树中、未被关闭或隐藏，其区域未被最小化，并且占据着该区域的当前活动标签页位置（单独位于自己区域内的面板也符合条件）。此参数的 ID 为基于贡献范围的面板标识，格式为 `<pluginId>:<paneId>`。由于原子值会按 ID 进行缓存，因此在渲染阶段调用该方法是安全的。请仅在您的面板可见时使用它来注册配套 UI —— Bot Mode 中的 Cronjobs 面板就是典型的使用案例：当 Bots 面板处于侧边栏标签页状态时会注册该 UI，而当用户切换回 Sessions 面板时则会取消注册。对于旧版桌面系统，建议先通过 `typeof host.paneVisibility === 'function'` 进行功能检测，若不支持则采用始终注册的默认行为。

`host.profileRoutes()` 用于枚举当前连接注册表中所有的已注册数据源。按需连接的 SSH 数据源无需建立隧道即可提供无需凭证的 `default` 基准路由，因此插件可作为首个调用方与其建立连接；而 SSH 的 `remoteProfile` 仍作为该路由的后端 `targetProfile`。`connectionId` 是注册表中的路由标识符，需与用于存储键值及持久化数据的 `profile` 配合使用。端点、令牌、SSH 主机/密钥以及其他原始连接字段绝不会跨越插件间的进程间通信边界。`profile` 是用于处理请求的源端本地路由，而 `targetProfile` 则是该路由所对应的服务后端 Hermes 配置文件。当某路由明确指向另一个后端配置文件时（例如通过 SSH `remoteProfile` 覆盖或传统的按配置文件划分的 URL 别名），二者便会存在差异。这种区分方式能够在不泄露连接机密的前提下，保留后端的唯一标识。

基于配置文件的插件也拥有高级方法：
`profiles.list`（每个配置文件及其最新的对话记录会被视为`last_session`；若需跳过针对单个配置文件的数据库查询，可传入`include_sessions: false`；若希望精确查找每个配置文件中标记为首选的会话并验证其是否存在，可传入`preferred_session_ids: { profileName: sessionId }`——此时每条记录都会包含一个`preferred_session`字段，该字段可用于将隐藏行及压缩后的对话链路还原至当前活跃的对话节点，若该会话已彻底消失，则值为`null`；较旧的网关会忽略此参数并省略该字段）；
以及`profiles.create`（包含`name`、`description`、`clone_from`、`clone_all`、`no_skills`、`soul`等参数，还可可选指定`model`和`provider`进行固定）——它们对应于控制台`/api/profiles` REST接口的WebSocket版本。
`host.state.busy`表示当前正在处理的对话处于活跃状态（即助手正在思考或发送内容）。
`host.state.awaitingResponse`在消息发送后直至收到首个助手响应前始终为真。这两个状态都会跟随用户当前正在查看的对话——当焦点在某个特定会话卡片上时，状态即为该会话的状态；否则则为主工作区中的对话状态（这与状态栏中显示的忙碌指示灯所依据的信号相同）。可在组件中订阅这些状态变化：

```javascript
const busy = useValue(host.state.busy)
```

如需获取更细致的令牌级信息，可通过 `host.onEvent`（包括 `message.start`、`message.delta`、`message.complete`）来监听事件。

`host.onEvent` 会实时传输网关事件（如消息变更、会话生命周期及工具运行状态）。各监听器之间是相互隔离的——监听器中的异常不会影响应用程序的调度流程。每个 `host` 接口都具有异步安全性：即使内部辅助函数抛出同步异常（例如在纯浏览器环境中没有桌面桥接），也只会被 `.catch()` 捕获，而不会导致错误边界崩溃。

`ctx.os` 是一个经过精心设计的操作系统接口——插件可通过该接口以专属命名空间访问应用程序窗口之外的各种功能。`ctx.os.notify` 用于发送**原生操作系统级通知**，其机制与应用程序自身的确认/关闭提示相同。该功能仅在用户离开 Hermes 应用时（处于后台状态或未聚焦时）触发；若需在用户使用应用时显示应用内提示，应使用 `host.notify`。用户可在“设置”→“通知”→“插件通知”中针对不同设备关闭该通知，且同一插件的重复通知也会被限制频率，因此应将其视为真正重要事件的信号，而非普通日志。

丰富的展示与激活功能（基于原始的 `ctx.os` 接口扩展而来）：

```ts
ctx.os.notify({
  title: 'New match found',
  body: 'Someone matched your signal',
  icon: '/abs/path/to/icon.png', // Electron Notification icon
  // Body click → focus Hermes + navigate. Same vocabulary as OS deep links:
  activate: 'hermes://index-network/intent/1',
  // or: activate: '/index-network/intent/1'
  // or: activate: { path: '/index-network/intent/1' }
  onActivate: () => focusLocalState('1'), // optional renderer callback
  actions: [
    { id: 'open', label: 'Open', activate: 'hermes://index-network/intent/1' },
    { id: 'dismiss', label: 'Dismiss', onAction: () => dismiss('1') },
  ],
})
```

`activate` 功能支持深度链接：`hermes://index-network/intent/1` 以及哈希路径 `/index-network/intent/1` 都会指向相同的应用内路由（而且同样的 `hermes://…` URL 也能作为操作系统的深度链接使用）。操作按钮仅会在已签名版本的 macOS 系统上显示；在其他系统上，点击内容区域同样可以触发相应功能。页面导航必须由用户主动点击才能实现——绝不会因后台事件而自动发生。

对于其他功能（如 `openExternal`、`revealPath`、`writeClipboard`），当对应功能不可用时（例如旧版桌面外壳或普通浏览器），它们会返回 `false` 而不会抛出错误——应基于该返回值进行分支处理，而非尝试检测桥接器状态。

## 数据层 — React Query + nanostores

所有插件共享应用中的同一个 `QueryClient`，因此插件的查询操作在缓存、去重、轮询以及失效处理方面都与核心界面完全一致——无需自行实现获取数据的循环逻辑。

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

对于触发器与其面板（或轮询循环）之间需要共享的状态，应使用与 `host.state` 所采用的相同的数据类型 `atom`/`computed`。可在渲染该值的叶子组件中通过 `useValue` 函数进行订阅。若需从 React **外部**（例如通过传入的 `ctx.socket` 数据）失效某个查询，需导入共享的 `queryClient` 对象：

```javascript
import { queryClient } from '@hermes/plugin-sdk'

ctx.socket('/events', () => {
  queryClient.invalidateQueries({ queryKey: ['my-plugin', 'items'] })
})
```

## UI组件库与主题系统

直接导入应用的原生组件，让界面默认呈现原生风格：

> `Button`、`Input`、`Textarea`、`Select*`、`Switch`、`Checkbox`、
> `SegmentedControl`、`Tabs*`、`Dialog*`、`ConfirmDialog`、`DropdownMenu*`、
> `ContextMenu*`、`Popover*`、`Tip`/`Tooltip*`、`Badge`、`Kbd`/`KbdGroup`、
> `SearchField`、`ScrollArea`、`Separator`、`Skeleton`、`GlyphSpinner`、`Loader`、
> `EmptyState`、`ErrorState`、`CopyButton`、`StatusDot`、`LogView`、`Codicon`、
> `DecodeText`。

此外还包括辅助组件：`cn`（类合并功能）、`icons.*`（应用自带的Lucide图标集）、`haptic`、
`profileColor` / `profileColorSoft`（用于定义唯一标识色），以及时间格式化函数 `relativeTime` / `fmtDateTime` / `fmtDayTime` / `coarseElapsed`、
`useI18n`（实现本地化文本——确保插件始终可翻译），还有 `evaluateRuntimeReadiness` 函数。

**应使用主题变量来定义样式，避免硬编码颜色。** 各组件元素本身已位于应用编辑器的背景之上，因此无需修改背景色，只需为其他所有元素使用变量即可：如 `var(--ui-text-secondary)`、`var(--ui-text-tertiary)`、`var(--ui-text-quaternary)`、`var(--ui-stroke-secondary)`、`var(--ui-accent)`。对于Canvas绘图场景，可通过 `getComputedStyle(canvas).getPropertyValue('--ui-accent')` 一次性获取这些颜色值。正是这一机制使得插件能够随主题变化自动调整外观。

## 插件的后端支持

如果您的插件需要执行服务器端操作，只需提供一个 Python 文件 `plugin_api.py`，然后通过 `ctx.rest` / `ctx.socket` 来调用它——这两个接口**从设计上就属于插件专用**的命名空间。

### 一个软件包，同时包含两种 SDK {#one-package-both-sdks}

对于那些既需要桌面端用户界面，又需要代理端代码（如 Python 插件、其后端路由及智能体功能）的功能，无需以两个相互依赖的独立安装包形式提供。桌面应用还会扫描常规的代理插件目录 `$HERMES_HOME/plugins/<id>/`，查找其中的 `desktop/plugin.js` 文件，并通过与独立磁盘门控组件完全相同的流程来加载该文件（包括热重载功能）：

```
~/.hermes/plugins/<id>/           # ONE installable folder
├── plugin.yaml                   # the agent half: tools, hooks, commands
├── skills/…
├── dashboard/
│   ├── manifest.json             # { "name": "<id>", "api": "plugin_api.py" }
│   └── plugin_api.py             # backend routes → /api/plugins/<id>/
└── desktop/
    └── plugin.js                 # the desktop half: panes, commands, ctx.rest
```

`desktop/plugin.js` 部分属于普通的磁盘插件——遵循相同的接口规范、导入依赖，也通过相同的 `ctx.rest('/…')` 方法来调用位于其旁的 `plugin_api.py` 文件。要安装、共享或移除该功能，只需操作同一个文件夹即可。

出于设计考虑，此处仍保留了两个启用开关，且默认均为**关闭**状态：桌面端以可选方式提供——它会在 **设置 → 插件** 中列出，但在用户手动开启之前始终处于禁用状态——这一机制与 Python 端 `config.yaml` 文件中的 `plugins.enabled` 设置一致（即上述的安全隔离机制）。除非用户另有指定，否则将插件包放入 `~/.hermes/plugins` 目录后，在任何层面都不会产生任何效果。当后端部分处于关闭状态时，桌面端会以优雅的方式降级运行——此时 `ctx.rest` 会返回错误信息，而不会导致程序崩溃。

:::note
扫描操作仅在桌面应用运行的本地机器上进行。对于远程后端，无法像访问本地文件系统那样访问远程机器上的 `~/.hermes/plugins` 目录——只有本地安装的插件才能为桌面端提供功能（这与独立版 Hermes 的规则相同）。
:::

### 通过安装链接分发 {#install-link}

只需上传您的插件代码仓库（包含代理端部分、桌面端部分或两者皆有），并通过 `hermes://` 协议提供访问链接——可直接在网站或 README 文件中添加相应链接：

```html
<a href="hermes://plugin/install?repo=owner/repo&enable=1">Install in Hermes</a>
```

在开始安装任何组件之前，用户会看到一个确认对话框（其中显示仓库 ID、源链接以及该仓库所包含的内容概览），需自行选择要安装的组件——深度链接绝不会被自动安装。使用 `force=1` 可以替换已有的安装版本；开发构建则需使用 `hermes-dev://` 协议。完整链接参考：[一键安装链接](/user-guide/features/plugins#one-click-install-links-desktop)。

### Python 端实现

桌面端插件会复用仪表板插件后端的挂载机制。只需将相关后端代码放入普通 Hermes 插件的 `dashboard/` 子文件夹中，并在 `manifest.json` 文件中进行声明即可：

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

路由挂载在 `/api/plugins/<id>/` 下（例如 `GET /api/plugins/<id>/board` 等）。后端代码在网关进程内部运行，因此可以直接从 hermes-agent 代码库中导入相关模块（如 `hermes_state`、`hermes_cli.config` 等）。如需完整的后端参考信息，请参阅[扩展控制面板 → 后端 API 路由](/user-guide/features/extending-the-dashboard#backend-api-routes)，其挂载方式与此相同。

:::注意 Python 后端是独立启用的
在桌面端的 **设置 → 插件** 面板中启用插件仅属于渲染端层面的操作，并不会导入 Python 代码。只有当用户插件对应的 `plugin_api.py` 被列入 `config.yaml` 中的 `plugins.enabled` 允许列表（且不在 `plugins.disabled` 列表中）时，才会被导入。项目自带的插件（位于 `./.hermes/` 目录下）则永远不会自动导入 Python 代码。这是出于安全考虑而设置的限制，并非疏忽（GHSA-mcfc-hp25-cjv7）。
:::

### 从插件中调用该功能

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

`ctx.rest` 具备配置文件感知功能，会阻止路径遍历（如 `..`），因此您绝不可能通过它来调用其他插件的 API 或核心路由。`PluginRestOptions` 的结构为 `{ method?, body?, upload?: { filename, contentType?, bytes }, timeoutMs? }`。

`ctx.socket` 会在被释放前持续进行带退避机制的自动重连。在基于 OAuth 的远程服务中，该接口实际上会返回无操作结果（单次使用的 WS 令牌由核心系统管理）——因此请将此套接字视为轮询方式的加速工具，而绝非替代品。无论如何，每个客户端都需要保留轮询作为备用方案，因为任何套接字都可能出现连接中断的情况。

对于整个网关范围内的数据（而非您自己的命名空间），建议使用 `host.request`（JSON-RPC）和 `host.onEvent`（网关事件流）。

## 设置、启用状态与存储

无论是否处于启用状态，所有插件都会显示在 **Settings → Plugins** 中，用户可在此实时切换插件状态（无需重启应用）、查看其所在文件夹或重新扫描插件。用户的设置选择会被保留：

- 尚未做选择 → 采用插件自身的 `defaultEnabled` 值（默认为 `true`）。若希望发布需用户主动启用的插件，可将 `defaultEnabled` 设置为 `false`，这样该插件在用户开启前将处于隐藏状态。
- 已明确做出选择 → 该设置会被持久化，并在应用重启后依然有效。已禁用的插件仍将保持禁用状态——无需强行启用，因为这是用户主动选择的。

您可以使用 `ctx.storage` 来保存自己的状态，该存储空间会按插件进行命名（格式为 `hermes.plugin.<id>.*`），这样各插件便无法互相读取或覆盖数据。

```javascript
ctx.storage.set('lastTab', 'board')
const tab = ctx.storage.get('lastTab', 'summary')
ctx.storage.remove('lastTab')
```

## 内置插件

插件可被打包至 `apps/desktop/src/plugins/<id>/plugin.tsx` 目录中（默认需导出 `HermesPlugin` 类型）。系统在启动时会通过 `discoverBundledPlugins()` 函数自动检测到这些插件——无需手动导入，也无需修改注册表——并且其功能清单以及实时启用/禁用机制与磁盘插件完全一致。二者之间的主要区别在于：

1. 这类插件会经过应用的 Vite 构建流程，因此你可以使用**真正的 JSX 语法**，并通过 `@hermes/plugin-sdk` 别名来导入 SDK。
2. 它们仍受限于 `@hermes/plugin-sdk` 和 `react` 的规范——不允许使用应用内部的 `@/…` 目录下的代码。

目前，核心代码树中不包含任何桌面端插件；这样一来，发布的应用结构会更加简洁，相关示例则位于 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins) 仓库中。

## 安全模型

已加载的插件会在渲染环境中以 ESM 方式运行，并拥有**完整的应用权限**——包括 React 单例、整个 SDK（如 `host.request` 网关 RPC、`ctx.rest`、存储功能以及导航功能）。加载器所提供的隔离机制仅限于**错误隔离**：插件虽无法导致应用崩溃（其功能受错误边界限制，监听器也被隔离），但可以执行应用所能做的任何操作。

对于**本地**来源而言，这种做法是可行的——磁盘文件本就能够在您的机器上运行代码，正因如此，该磁盘插件仅会加载由您（或您的智能体）编写的本地文件。可选的`integrity`（`sha256-…`）校验功能仅能证明数据字节与哈希值一致，**并不具备沙箱隔离功能**。未来的远程来源插件在投入使用前，必须建立真正的边界防护机制（如iframe/worker技术、CSP策略以及能力访问控制），切勿将当前这一处理流程视为可信边界。

## 常见问题

- **磁盘插件中无法解析 JSX。** 文件会以未编译的形式被加载——请使用 `jsx()` / `jsxs()`（或 `React.createElement`），而非 JSX 语法。（已打包的插件经过构建处理，因此可以使用 JSX。）
- **仅三种指定项可被识别：** `@hermes/plugin-sdk`、`react`、`react/jsx-runtime`。任何其他导入项都会导致立即出现加载错误。
- **切勿硬编码颜色值**（如 `#000`、`black`、`rgb(...)`）。请勿直接设置背景色，所有颜色都应通过主题变量（如 `var(--ui-*)`）来指定。
- **仅引用已导入的组件。** 若遗漏了某个组件的导入（例如 `StatusDot`），则会在渲染时引发 `ReferenceError`——请仔细检查 `jsx()` 调用中的所有标识符是否都出现在导入语句中。
- **在处理函数中以命令式方式读取状态**（使用 `$atom.get()`），切勿从渲染闭包中读取——否则快速发生的事件将获取到过时的值。仅在实际渲染该值的节点中使用订阅机制（`useValue`）。
- **Canvas 面板需通过 `ResizeObserver` 监听其容器尺寸变化，并调整 Canvas 的宽高属性（而非仅依赖 CSS）——因为面板尺寸会不断变化。**
- **使用 `host.request` 时，查询频率请勿超过几秒/次**；建议优先使用 `host.onEvent` / `ctx.socket`，并让 React Query 负责去重处理。
- **在 OAuth 远程端，`ctx.socket` 不具备实际功能**。务必准备好轮询作为备用方案。

## 参考资料

### SDK 导出项概览

| Category | Exports |
|----------|---------|
| Host | `host` (`.state.*`, `.notify`, `.notifyError`, `.navigate`, `.onEvent`, `.logs`, `.status`, `.restartGateway`, `.request`) |
| Plugin contract | `HermesPlugin`, `PluginContext`, `PluginContribution`, `PluginStorage`, `PluginOs`, `PluginRestOptions`, `PluginNativeNotificationInput`, `PluginNotificationAction`, `HermesOpenTarget`, `Contribution` |
| Area constants | `PANES_AREA`, `ROUTES_AREA`, `SIDEBAR_NAV_AREA`, `STATUSBAR_AREAS`, `TITLEBAR_AREAS`, `PALETTE_AREA`, `KEYBINDS_AREA`, `THEMES_AREA`, `COMPOSER_AREAS` |
| Area payloads | `RouteContribution`, `SidebarNavContribution`, `StatusbarItem`, `TitlebarTool`, `PaletteContribution`, `KeybindContribution`, `ComposerMiddleware`, `ComposerAttachmentProvider` |
| React / state | `useValue`, `atom`, `computed`, `useQuery`, `useMutation`, `useQueryClient`, `queryClient`, `Contribute` |
| Theming | `useTheme`, `requestTheme`, `setAccentOverride`, `$accentOverride`, `retintTheme`, `themeHue`, `DesktopTheme`, `DesktopThemeColors`, plus OKLCH math (`hexToOklch`, `oklchToHex`, `oklchToSrgb255`, `mixOklab`, `maxChroma`, `hueDelta`, `contrastRatio`, `readableOn`, `normalizeHex`) |
| UI kit | `Button`, `Input`, `Textarea`, `Select*`, `Switch`, `Checkbox`, `SegmentedControl`, `Tabs*`, `Dialog*`, `ConfirmDialog`, `DropdownMenu*`, `ContextMenu*`, `Popover*`, `Tip`/`Tooltip*`, `Badge`, `Kbd`/`KbdGroup`, `SearchField`, `ScrollArea`, `Separator`, `Skeleton`, `GlyphSpinner`, `Loader`, `EmptyState`, `ErrorState`, `CopyButton`, `StatusDot`, `LogView`, `Codicon`, `DecodeText` |
| Helpers | `cn`, `icons`, `haptic`, `useI18n`, `profileColor`, `profileColorSoft`, `relativeTime`, `fmtDateTime`, `fmtDayTime`, `coarseElapsed`, `evaluateRuntimeReadiness` |

当前最新且官方认可的插件列表位于 `apps/desktop/src/sdk/index.ts` 文件中。

### Agent：`hermes-desktop-plugins` 技能

当 Agent 编写桌面端插件时，应加载内置的 **`hermes-desktop-plugins`** 技能——该技能以面向 Agent 的格式呈现了与本页面相同的接口规范，并附有可直接复制的 `templates/plugin.js` 文件。本页面是为人类用户及开发者提供的参考资料，而该技能则是实际开发时的操作检查清单。

## 故障排除

**我的插件没有显示。** 请确认文件位于 `$HERMES_HOME/desktop-plugins/<id>/plugin.js`，且文件夹名称与导出的 `id` 完全一致。随后执行 ⌘K → **Reload desktop plugins**。检查应用中是否有提示失败原因的错误提示信息，并通过 `hermes logs gui -f` 实时查看日志。

**加载时出现“unsupported import”错误。** 磁盘插件仅允许导入 `@hermes/plugin-sdk`、`react` 以及 `react/jsx-runtime` 这三个模块。请删除其他所有导入语句。

**`jsx` 元素无内容显示或抛出 `ReferenceError` 错误。** 这是因为在 `jsx()` 调用中使用的标识符未被导入。请将其添加到导入行中。

**`ctx.rest` 返回 404 错误。** 说明后端服务尚未启动：请确认 `~/.hermes/plugins/<id>/dashboard/manifest.json` 文件中包含 `"api": "plugin_api.py"`，同时确保该插件已在 `config.yaml` 的 `plugins.enabled` 列表中启用，最后重启网关服务（后端路由会在启动时加载）。通过 `~/.hermes/logs/errors.log` 查看是否存在 “Failed to load plugin <id> API routes” 的错误记录。

**`ctx.socket` 从未触发。** 在基于 OAuth 的远程环境中，按设计该功能为无操作——请使用轮询机制作为替代方案。否则，请确认后端在其命名空间下确实提供了对应的 `@router.websocket(...)` 路由。

**切换主题后颜色显示异常。** 您使用了硬编码的颜色值，应将其替换为 `var(--ui-*)` 形式的主题变量。
