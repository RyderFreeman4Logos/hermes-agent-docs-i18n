---
sidebar_position: 17
title: "Extending the Dashboard"
description: "Build themes and plugins for the Hermes web dashboard — palettes, typography, layouts, custom tabs, shell slots, page-scoped slots, and backend API routes"
---

# 扩展控制面板功能

Hermes 网页控制面板（`hermes dashboard`）设计为无需克隆代码库即可进行外观定制与功能扩展。它提供了三层扩展接口：

1. **主题**——用于重新设定控制面板的配色方案、字体、布局以及各组件的边框样式的 YAML 文件。只需将文件放入 `~/.hermes/dashboard-themes/` 目录中，它就会出现在主题切换器中。
2. **UI 插件**——包含 `manifest.json` 文件及 JavaScript 打包文件的目录，这类插件可用于新增标签页、替换内置页面、通过页面级插槽增强现有页面功能，或向指定插槽注入组件。
3. **后端插件**——位于该插件目录中的 Python 文件，它会暴露一个 FastAPI 路由器；相关路由会挂载在 `/api/plugins/<name>/` 下，并可由插件自身的 UI 调用。

这三种扩展方式均支持**运行时直接插入**：无需克隆仓库、无需执行 `npm run build`，也无需修改控制面板的源代码。本页面是关于这三种扩展方式的权威参考文档。

如果您仅想使用控制面板功能，请参阅 [网页控制面板](./web-dashboard)。若需定制终端 CLI 的外观（而非网页控制面板），请查看 [皮肤与主题](./skins)——CLI 的皮肤系统与控制面板主题无关。

:::note 本页面不涉及桌面应用
本页面介绍的是**网页控制面板**（`hermes dashboard`）的插件系统，包括 `window.__HERMES_PLUGIN_SDK__`、`manifest.json` 以及预编译好的 JS 打包文件。而**原生桌面应用**（`hermes desktop`）则拥有独立的 SDK——`@hermes/plugin-sdk`，它仅为一个 ESM 文件，无需任何构建步骤，相关文档请参见 [桌面插件 SDK](/developer-guide/desktop-plugin-sdk)。两者之间仅共享后端的 `plugin_api.py` 命名空间（`/api/plugins/<name>`）。
:::

:::note 各组件的组合方式
主题与插件虽各自独立，但能够协同工作。单个主题可以仅以 YAML 文件的形式存在；单个插件也可以仅以标签页的形式存在。将二者结合使用，便可打造出带有自定义 HUD 的完整视觉风格——示例中的 `strike-freedom-cockpit` 演示项目（位于 `hermes-example-plugins` 附录仓库中，安装步骤请参见 [主题与插件组合演示](#combined-theme--plugin-demo)）正是如此实现的。
:::

---

## 目录

- [主题](#themes)
  - [快速入门——创建你的第一个主题](#quick-start--your-first-theme)
  - [配色方案、字体与布局](#palette-typography-layout)
  - [布局变体](#layout-variants)
  - [主题资源（将图片作为 CSS 变量）](#theme-assets-images-as-css-vars)
  - [组件边框样式覆盖](#component-chrome-overrides)
  - [颜色覆盖](#color-overrides)
  - [原始 `customCSS` 文件](#raw-customcss)
  - [内置主题](#built-in-themes)
  - [完整主题 YAML 参考](#full-theme-yaml-reference)
- [插件](#plugins)
  - [快速入门——创建你的第一个插件](#quick-start--your-first-plugin)
  - [目录结构](#directory-layout)
  - [manifest 文件参考](#manifest-reference)
  - [插件 SDK](#the-plugin-sdk)
  - [插槽](#shell-slots)
  - [替换内置页面（`tab.override`）](#replacing-built-in-pages-taboverride)
  - [增强内置页面（页面级插槽）](#augmenting-built-in-pages-page-scoped-slots)
  - [仅包含插槽的插件（`tab.hidden`）](#slot-only-plugins-tabhidden)
  - [后端 API 路由](#backend-api-routes)
  - [每个插件的自定义 CSS](#custom-css-per-plugin)
  - [插件发现与重新加载](#plugin-discovery--reload)
- [主题与插件组合演示](#combined-theme--plugin-demo)
- [API 参考](#api-reference)
- [故障排除](#troubleshooting)

---

## 主题

主题为存储在 `~/.hermes/dashboard-themes/` 目录中的 YAML 文件。文件名并无特殊要求（系统会使用主题中的 `name:` 字段来识别），但通常采用 `<name>.yaml` 的格式。所有字段均为可选——若缺少某些键值，系统会自动回退到内置的 `default` 主题，因此一个主题甚至只需定义一种颜色即可。

### 快速入门——创建你的第一个主题

```bash
mkdir -p ~/.hermes/dashboard-themes
```

```yaml
# ~/.hermes/dashboard-themes/neon.yaml
name: neon
label: Neon
description: Pure magenta on black

palette:
  background: "#000000"
  midground: "#ff00ff"
```

刷新仪表板。点击顶部的调色板图标，选择 **Neon** 风格。此时背景会变为黑色，文字及强调元素则转为洋红色，而所有派生颜色（如卡片色、边框色、柔和色、环状色等）都会通过 CSS 中的 `color-mix()` 函数，基于这两种颜色重新计算得出。

整个入门流程就这些：仅需一个文件和两种颜色，其余均为可选的精细化设置。

### 调色板、字体与布局

这三部分构成了主题的核心。它们彼此独立——只需修改其中一项，其余部分保持不变即可。

#### 调色板（3层结构）

调色板由三组颜色值构成，此外还包括一个暖光晕色以及一个噪点纹理强度系数。仪表板的设计系统会通过 CSS 的 `color-mix()` 函数，基于这组颜色值生成所有与 shadcn 兼容的颜色标识（如卡片色、弹出框色、柔和色、边框色、主色调、对比色、环状色等）。只要修改这三组颜色，就会影响整个用户界面的外观。

| 键值 | 描述 |
|-----|-----|
| `palette.background` | 最深的背景色——通常接近黑色。用于设定页面背景及卡片填充色。 |
| `palette.midground` | 主要文字与强调色。大多数界面元素都会使用此颜色（如前景文字、按钮轮廓、焦点环）。 |
| `palette.foreground` | 最上层的高亮色。默认主题将其设置为透明度为 0 的白色（不可见）；若希望添加更醒目的高亮效果，可提高其透明度值。 |
| `palette.warmGlow` | 用于 `<Backdrop />` 元素生成晕影效果的 `rgba(...)` 格式颜色字符串。 |
| `palette.noiseOpacity` | 噪点纹理的强度系数，范围为 0–1.2。数值越低，纹理效果越柔和；数值越高，纹理越明显。 |

每层颜色值既可以采用 `{hex: "#RRGGBB", alpha: 0.0–1.0}` 的格式，也可以直接使用纯十六进制字符串（此时透明度默认为 1.0）。

```yaml
palette:
  background:
    hex: "#05091a"
    alpha: 1.0
  midground: "#d8f0ff"          # bare hex, alpha = 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0                    # invisible top layer
  warmGlow: "rgba(255, 199, 55, 0.24)"
  noiseOpacity: 0.7
```

#### 字体设置

| 键值 | 类型 | 描述 |
|-----|------|-------------|
| `fontSans` | 字符串 | 正文内容的 CSS 字体系列（应用于 `html` 和 `body` 元素）。 |
| `fontMono` | 字符串 | 代码块、`<code>` 标签以及 `.font-mono` 工具类的 CSS 字体系列。 |
| `fontDisplay` | 字符串 | 可选的标题/显示文本字体系列。若未设置，则默认使用 `fontSans`。 |
| `fontUrl` | 字符串 | 可选的外部样式表地址。在切换主题时，该地址会以 `<link rel="stylesheet">` 的形式注入到 `<head>` 标签中。同一地址不会被重复注入。支持 Google Fonts、Bunny Fonts 以及自托管的 `@font-face` 样式表——任何可通过链接引入的字体格式均可使用。 |
| `baseSize` | 字符串 | 基础字体大小，用于控制 rem 单位的缩放比例。例如 `"14px"`、`"16px"`。 |
| `lineHeight` | 字符串 | 默认行高值。例如 `"1.5"`、`"1.65"`。 |
| `letterSpacing` | 字符串 | 默认字距值。例如 `"0"`、`"0.01em"`、`"-0.01em"`。 |

```yaml
typography:
  fontSans: '"Orbitron", "Eurostile", "Impact", sans-serif'
  fontMono: '"Share Tech Mono", ui-monospace, monospace'
  fontDisplay: '"Orbitron", "Eurostile", sans-serif'
  fontUrl: "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Share+Tech+Mono&display=swap"
  baseSize: "14px"
  lineHeight: "1.5"
  letterSpacing: "0.04em"
```

##### 通过用户界面更改字体（无需 YAML）

控制台顶部的主题选择器在主题列表下方设有**字体**选项。选择任意字体即可覆盖当前激活主题的正文字体——该设置与具体主题无关，且会在切换主题时保持不变（存储在 `config.yaml` 的 `dashboard.font` 字段中）。若要取消覆盖并恢复为当前主题自带的 `fontSans` 字体，可选择**主题默认值**。

该选择器提供了精心筛选的字体列表，包括系统预设的字体组合以及一系列来自 Google Fonts 的无衬线/衬线/等宽字体系列。它故意不支持直接输入自由文本形式的字体网址——因为字体样式表是通过 `<link>` 标签注入的，所以列表能确保注入源地址的稳定性。若需使用完全自定义的字体，则需如上所示在主题的 YAML 文件中同时设置 `fontSans` 和 `fontUrl` 参数。而主题中的 `fontMono`（用于代码块和终端显示）设置则始终不会受到用户界面更改的影响。

#### 布局

| 键值 | 可选值 | 说明 |
|-----|--------|-------------|
| `radius` | 任意 CSS 长度值（如 `"0"`、`"0.25rem"`、`"0.5rem"`、`"1rem"` 等） | 角落圆角参数。对应 `--radius`，并可进一步细分为 `--radius-sm/md/lg/xl` —— 所有带有圆角的元素会同步变化。 |
| `density` | `compact` \| `comfortable` \| `spacious` | 间距倍数，以 `--spacing-mul` CSS 变量形式应用。其中 `compact = 0.85×`，`comfortable = 1.0×`（默认值），`spacious = 1.2×`。该参数会调整 Tailwind 的基础间距，因此填充、间隙及元素间的间距类都会按比例变化。 |

```yaml
layout:
  radius: "0"
  density: compact
```

### 布局样式

`layoutVariant` 用于选择终端的整体布局。若未指定该参数，则默认为 `"standard"`。

| 样式 | 行为描述 |
|------|----------|
| `standard` | 单列布局，最大宽度为 1600px（默认值）。 |
| `cockpit` | 左侧边栏（宽度为 260px）+ 主内容区。侧边栏内容由插件通过 `sidebar` 插槽填充——详情请参阅[终端插槽](#shell-slots)。若没有对应插件，该侧边栏将显示占位符。 |
| `tiled` | 取消最大宽度限制，使页面能够占据整个视口宽度。 |

```yaml
layoutVariant: cockpit
```

当前版本通过 `document.documentElement.dataset.layoutVariant` 来标识，因此 `customCSS` 中的原始 CSS 可以使用 `:root[data-layout-variant="cockpit"] ...` 的写法来定位它。

### 主题资源（以 CSS 变量形式存在的图片）

主题会附带相应的船体图案网址。每个命名的插槽都会对应一个 CSS 变量（`--theme-asset-<name>`），内置终端及各类插件均可读取这些变量。`bg` 插槽会自动用于背景设置，而其他插槽则供插件使用。

```yaml
assets:
  bg: "https://example.com/hero-bg.jpg"           # auto-wired into <Backdrop />
  hero: "/my-images/strike-freedom.png"           # for plugin sidebars
  crest: "/my-images/crest.svg"                   # for header-left plugins
  logo: "/my-images/logo.png"
  sidebar: "/my-images/rail.png"
  header: "/my-images/header-art.png"
  custom:
    scanLines: "/my-images/scanlines.png"         # → --theme-asset-custom-scanLines
```

支持的值包括：

- 纯网址 — 会自动被封装在 `url(...)` 中。
- 已经封装好的 `url(...)`, `linear-gradient(...)`, `radial-gradient(...)` 表达式 — 可直接使用原格式。
- `"none"` — 明确表示不使用该功能。

此外，每个资源还会以 `--theme-asset-<name>-raw`（即未封装的网址）的形式输出，以便插件在需要时将其传递给 `<img src>` 而非 `background-image` 属性。

插件可通过普通的 CSS 或 JS 代码来读取这些资源：

```javascript
// In a plugin slot
const hero = getComputedStyle(document.documentElement)
  .getPropertyValue("--theme-asset-hero").trim();
```

### 组件级样式覆盖

`componentStyles` 功能允许无需编写 CSS 选择器即可重新定义各个 Shell 组件的样式。每个配置项都会被转换为 CSS 变量（格式为 `--component-<bucket>-<kebab-property>`），供 Shell 的共享组件读取。因此，以 `card:` 开头的覆盖规则将应用于所有的 `<Card>` 元素，以 `header:` 开头的规则则适用于应用栏，以此类推。

```yaml
componentStyles:
  card:
    clipPath: "polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px)"
    background: "linear-gradient(180deg, rgba(10, 22, 52, 0.85), rgba(5, 9, 26, 0.92))"
    boxShadow: "inset 0 0 0 1px rgba(64, 200, 255, 0.28)"
  header:
    background: "linear-gradient(180deg, rgba(16, 32, 72, 0.95), rgba(5, 9, 26, 0.9))"
  tab:
    clipPath: "polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)"
  sidebar: {}
  backdrop: {}
  footer: {}
  progress: {}
  badge: {}
  page: {}
```

支持的容器类型包括：`card`、`header`、`footer`、`sidebar`、`tab`、`progress`、`badge`、`backdrop`以及`page`。

属性名称采用驼峰命名法（如`clipPath`），但在输出时会转换为连字符分隔的形式（如`clip-path`）。其值则为普通的CSS字符串——任何CSS支持的格式均可使用（如`clip-path`、`border-image`、`background`、`box-shadow`、`animation`等）。

### 颜色覆盖设置

大多数主题无需使用此功能，因为三层调色板已可生成所有所需的颜色值。只有当您需要某种通过常规方式无法得到的特殊强调色时，才需使用`colorOverrides`——例如为柔和的淡色主题设计更浅的红色，或为特定品牌定制专属的成功绿色。

```yaml
colorOverrides:
  primary: "#ffce3a"
  primaryForeground: "#05091a"
  accent: "#3fd3ff"
  ring: "#3fd3ff"
  destructive: "#ff3a5e"
  border: "rgba(64, 200, 255, 0.28)"
```

支持的键值包括：`card`、`cardForeground`、`popover`、`popoverForeground`、`primary`、`primaryForeground`、`secondary`、`secondaryForeground`、`muted`、`mutedForeground`、`accent`、`accentForeground`、`destructive`、`destructiveForeground`、`success`、`warning`、`border`、`input`、`ring`。

每个键值都会与 `--color-<kebab>` 这一 CSS 变量实现一一对应（例如 `primaryForeground` 对应 `--color-primary-foreground`）。此处设置的任何键值仅对当前激活的主题生效，覆盖原有的颜色方案设置；切换到其他主题后，这些自定义设置将会被清除。

### 原始 CSS 代码

对于 `componentStyles` 无法处理的选择器级样式——如伪元素、动画效果、媒体查询以及基于主题的覆盖规则——可直接将原始 CSS 代码放入 `customCSS` 字段中：

```yaml
customCSS: |
  /* Scanline overlay — only visible when cockpit variant is active. */
  :root[data-layout-variant="cockpit"] body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 100;
    background: repeating-linear-gradient(to bottom,
      transparent 0px, transparent 2px,
      rgba(64, 200, 255, 0.035) 3px, rgba(64, 200, 255, 0.035) 4px);
    mix-blend-mode: screen;
  }
```

该 CSS 会在主题应用时以一个带作用域的 `<style data-hermes-theme-css>` 标签形式注入，而在切换主题时则会被清除。**每个主题的容量上限为 32 KiB。**

### 内置主题

所有内置主题均自带独特的配色方案、字体样式及布局设计——因此切换主题时带来的变化远不止颜色上的差异。

| 主题 | 配色方案 | 字体样式 | 布局 |
|-------|---------|----------|------|
| **Hermes Teal**（`default`） | 深青色 + 奶油色 | 系统默认字体，15px | 半径为 0.5rem，布局舒适 |
| **Hermes Teal (Large)**（`default-large`） | 与默认主题相同 | 系统默认字体，18px，行高 1.65 | 半径为 0.5rem，布局更为宽敞 |
| **Midnight**（`midnight`） | 深蓝紫色 | Inter + JetBrains Mono，14px | 半径为 0.75rem，布局舒适 |
| **Ember**（`ember`） | 温暖的深红色 + 青铜色 | Spectral（衬线体）+ IBM Plex Mono，15px | 半径为 0.25rem，布局舒适 |
| **Mono**（`mono`） | 灰度色调 | IBM Plex Sans + IBM Plex Mono，13px | 半径为 0，布局紧凑 |
| **Cyberpunk**（`cyberpunk`） | 黑色背景上的霓虹绿 | 全部使用 Share Tech Mono，14px | 半径为 0，布局紧凑 |
| **Rosé**（`rose`） | 粉色 + 象牙白 | Fraunces（衬线体）+ DM Mono，16px | 半径为 1rem，布局宽敞 |

除 Hermes Teal 外，其他所有使用 Google Fonts 的主题都会按需加载样式表——首次切换到这些主题时，系统会将一个 `<link>` 标签注入到 `<head>` 中。

### 完整的主题 YAML 参考

所有设置均集中在一个文件中——可直接复制并删除不必要的部分：

```yaml
# ~/.hermes/dashboard-themes/ocean.yaml
name: ocean
label: Ocean Deep
description: Deep sea blues with coral accents

# 3-layer palette (accepts {hex, alpha} or bare hex)
palette:
  background:
    hex: "#0a1628"
    alpha: 1.0
  midground:
    hex: "#a8d0ff"
    alpha: 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0.0
  warmGlow: "rgba(255, 107, 107, 0.35)"
  noiseOpacity: 0.7

typography:
  fontSans: "Poppins, system-ui, sans-serif"
  fontMono: "Fira Code, ui-monospace, monospace"
  fontDisplay: "Poppins, system-ui, sans-serif"   # optional
  fontUrl: "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Fira+Code:wght@400;500&display=swap"
  baseSize: "15px"
  lineHeight: "1.6"
  letterSpacing: "-0.003em"

layout:
  radius: "0.75rem"
  density: comfortable

layoutVariant: standard        # standard | cockpit | tiled

assets:
  bg: "https://example.com/ocean-bg.jpg"
  hero: "/my-images/kraken.png"
  crest: "/my-images/anchor.svg"
  logo: "/my-images/logo.png"
  custom:
    pattern: "/my-images/waves.svg"

componentStyles:
  card:
    boxShadow: "inset 0 0 0 1px rgba(168, 208, 255, 0.18)"
  header:
    background: "linear-gradient(180deg, rgba(10, 22, 40, 0.95), rgba(5, 9, 26, 0.9))"

colorOverrides:
  destructive: "#ff6b6b"
  ring: "#ff6b6b"

customCSS: |
  /* Any additional selector-level tweaks */
```

创建文件后，请刷新控制面板。可通过顶部栏实时切换主题——点击调色板图标即可。所选主题会保存在 `config.yaml` 文件的 `dashboard.theme` 字段中，下次加载时将自动恢复。

---

## 插件

控制面板插件是一个包含 `manifest.json`、预构建的 JS 包，以及可选的 CSS 文件和包含 FastAPI 路由的 Python 文件的目录。这些插件存储在 `~/.hermes/plugins/<名称>/` 目录下，与其他 Hermes 插件并存——控制面板扩展功能则位于该插件目录内的 `dashboard/` 子文件夹中，因此只需安装一个插件，即可同时为 CLI/网关和控制面板添加扩展功能。

插件不会自带 React 或 UI 组件，而是使用通过 `window.__HERMES_PLUGIN_SDK__` 提供的 **插件 SDK**。这样一来，插件包的体积非常小（通常只有几 KB），同时也能避免版本冲突。

### 快速入门——创建你的第一个插件

首先创建目录结构：

```bash
mkdir -p ~/.hermes/plugins/my-plugin/dashboard/dist
```

编写清单文件：

```json
// ~/.hermes/plugins/my-plugin/dashboard/manifest.json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:skills"
  },
  "entry": "dist/index.js"
}
```

编写 JS 捆包文件（采用普通的 IIFE 形式——无需任何构建步骤）：

```javascript
// ~/.hermes/plugins/my-plugin/dashboard/dist/index.js
(function () {
  "use strict";

  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { Card, CardHeader, CardTitle, CardContent } = SDK.components;

  function MyPage() {
    return React.createElement(Card, null,
      React.createElement(CardHeader, null,
        React.createElement(CardTitle, null, "My Plugin"),
      ),
      React.createElement(CardContent, null,
        React.createElement("p", { className: "text-sm text-muted-foreground" },
          "Hello from my custom dashboard tab.",
        ),
      ),
    );
  }

  window.__HERMES_PLUGINS__.register("my-plugin", MyPage);
})();
```

刷新控制面板——您的标签页会出现在导航栏中，位于 **Skills** 之后。

:::提示：可跳过 React.createElement
如果您更喜欢使用 JSX，可以使用任何打包工具（如 esbuild、Vite、rollup），并将 React 作为外部依赖并以 IIFE 形式输出。唯一的硬性要求是最终生成的文件必须是一个可通过 `<script>` 加载的单一 JS 文件。React 本身不会被打包，它直接来自 `SDK.React`。
:::

### 目录结构

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml              # optional — existing CLI/gateway plugin manifest
├── __init__.py              # optional — existing CLI/gateway hooks
└── dashboard/               # dashboard extension
    ├── manifest.json        # required — tab config, icon, entry point
    ├── dist/
    │   ├── index.js         # required — pre-built JS bundle (IIFE)
    │   └── style.css        # optional — custom CSS
    └── plugin_api.py        # optional — backend API routes (FastAPI)
```

一个插件目录可包含三种相互独立的扩展组件：

- `plugin.yaml` + `__init__.py` — CLI/网关插件（[详见插件页面](./plugins)）。
- `dashboard/manifest.json` + `dashboard/dist/index.js` — 控制台界面插件。
- `dashboard/plugin_api.py` — 控制台后端路由。

这些组件并非全部必需，只需添加您实际需要的部分即可。

### 配置文件参考

```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "description": "What this plugin does",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:skills",
    "override": "/",
    "hidden": false
  },
  "slots": ["sidebar", "header-left"],
  "entry": "dist/index.js",
  "css": "dist/style.css",
  "api": "plugin_api.py"
}
```

| 字段 | 是否必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 唯一的插件标识符。需为小写，可包含连字符。用于URL地址及插件注册。 |
| `label` | 是 | 在导航标签页中显示的名称。 |
| `description` | 否 | 简短描述（显示在控制台管理界面中）。 |
| `icon` | 否 | Lucide图标名称。默认值为`Puzzle`；若为未知名称，则自动回退至`Puzzle`。 |
| `version` | 否 | Semver版本格式的字符串。默认值为`0.0.0`。 |
| `tab.path` | 是 | 标签页的URL路径（例如`/my-plugin`）。 |
| `tab.position` | 否 | 标签页的插入位置。可选值包括“end”（默认）、“after:<path>”或“before:<path>”——冒号后的内容为目标标签页的**路径片段**，且不含前置斜杠。示例：“after:skills”、“before:config”。 |
| `tab.override` | 否 | 设置为内置路由路径（如`"/"`、`"/sessions"`、`"/config"`等），即可**替换**该页面而非新增标签页。详见[替换内置页面](#replacing-built-in-pages-taboverride)。 |
| `tab.hidden` | 否 | 若设置为true，则仅注册组件及对应的插槽，而不会在导航栏中添加标签页。适用于仅包含插槽的插件。详见[仅含插槽的插件](#slot-only-plugins-tabhidden)。 |
| `slots` | 否 | 该插件所填充的命名壳层插槽。此字段**仅用于文档说明**——实际注册是通过JS包中的`registerSlot()`函数完成的。在此列出插槽有助于提升发现功能的便捷性。 |
| `entry` | 是 | 相对于`dashboard/`目录的JS包路径。默认值为`dist/index.js`。 |
| `css` | 否 | 用于以 `<link>` 标签注入的CSS文件路径。 |
| `api` | 否 | 包含FastAPI路由的Python文件路径。该接口将挂载在 `/api/plugins/<name>/` 路径下。 |

#### 可用的图标

插件需使用Lucide图标名称。控制台会通过名称对应这些图标——若为未知名称，则会自动回退至`Puzzle`图标。

目前已映射的图标包括：`Activity`、`BarChart3`、`Clock`、`Code`、`Database`、`Eye`、`FileText`、`Globe`、`Heart`、`KeyRound`、`MessageSquare`、`Package`、`Puzzle`、`Settings`、`Shield`、`Sparkles`、`Star`、`Terminal`、`Wrench`、`Zap`。

需要其他图标？可直接在 `web/src/App.tsx` 文件的 `ICON_MAP` 对象中提交PR进行添加——属于简单的增改操作。

### 插件SDK

插件所需的所有功能均位于 `window.__HERMES_PLUGIN_SDK__` 对象中。插件绝不可直接导入React库。

```javascript
const SDK = window.__HERMES_PLUGIN_SDK__;

// React + hooks
SDK.React                    // the React instance
SDK.hooks.useState
SDK.hooks.useEffect
SDK.hooks.useCallback
SDK.hooks.useMemo
SDK.hooks.useRef
SDK.hooks.useContext
SDK.hooks.createContext

// UI components (shadcn/ui primitives)
SDK.components.Card
SDK.components.CardHeader
SDK.components.CardTitle
SDK.components.CardContent
SDK.components.Badge
SDK.components.Button
SDK.components.Input
SDK.components.Label
SDK.components.Select
SDK.components.SelectOption
SDK.components.Separator
SDK.components.Tabs
SDK.components.TabsList
SDK.components.TabsTrigger
SDK.components.PluginSlot    // render a named slot (useful for nested plugin UIs)

// Hermes API client + raw fetcher
SDK.api                      // typed client — getStatus, getSessions, getConfig, ...
SDK.fetchJSON                // raw fetch for custom endpoints (plugin-registered routes)

// Utilities
SDK.utils.cn                 // Tailwind class merger (clsx + twMerge)
SDK.utils.timeAgo            // "5m ago" from unix timestamp
SDK.utils.isoTimeAgo         // "5m ago" from ISO string

// Hooks
SDK.useI18n                  // i18n hook for multi-language plugins
```

#### 调用插件后端服务

```javascript
SDK.fetchJSON("/api/plugins/my-plugin/data")
  .then((data) => console.log(data))
  .catch((err) => console.error("API call failed:", err));
```

`fetchJSON` 会注入会话认证令牌，将错误以异常形式抛出，并自动解析 JSON 数据。

#### 调用内置的 Hermes 接口

```javascript
// Agent status
SDK.api.getStatus().then((s) => console.log("Version:", s.version));

// Recent sessions
SDK.api.getSessions(10).then((resp) => console.log(resp.sessions.length));
```

完整列表请参见[Web Dashboard → REST API](./web-dashboard#rest-api)。

### Shell插槽

插槽功能允许插件将组件注入应用Shell的指定位置——如驾驶舱侧边栏、页头、页脚或覆盖层——而无需占用整个标签页。多个插件可以填充同一个插槽，它们会按照注册顺序依次显示。

可在插件包内部进行注册：

```javascript
window.__HERMES_PLUGINS__.registerSlot("my-plugin", "sidebar", MySidebar);
window.__HERMES_PLUGINS__.registerSlot("my-plugin", "header-left", MyCrest);
```

#### 插槽目录

**全局插槽**（可在应用界面中的任意位置显示）：

| 插槽名称 | 显示位置 |
|----------|----------|
| `backdrop` | 位于 `<Backdrop />` 图层堆叠的内部，噪声图层之上。 |
| `header-left` | 顶部栏中Hermes品牌标识之前。 |
| `header-right` | 顶部栏中主题/语言切换器之前。 |
| `header-banner` | 导航栏下方的全宽横幅区域。 |
| `sidebar` | 控制台侧边栏区域——**仅当 `layoutVariant === "cockpit"` 时显示**。 |
| `pre-main` | 路由输出区域上方（位于 `<main>` 内部）。 |
| `post-main` | 路由输出区域下方（位于 `<main>` 内部）。 |
| `footer-left` | 底部栏内容区域（替代默认内容）。 |
| `footer-right` | 底部栏内容区域（替代默认内容）。 |
| `overlay` | 固定定位的图层，位于所有其他元素之上。适用于那些仅靠 `customCSS` 无法实现的界面效果，如扫描线、暗角等。 |

**页面级插槽**（仅在指定的内置页面中显示——可用于向现有页面添加小部件、卡片或工具栏，而无需覆盖整个路由页面）：

| 插槽名称 | 显示位置 |
|----------|----------|
| `sessions:top` / `sessions:bottom` | `/sessions` 页面的顶部/底部。 |
| `analytics:top` / `analytics:bottom` | `/analytics` 页面的顶部/底部。 |
| `logs:top` / `logs:bottom` | `/logs` 页面的顶部（过滤工具栏之上）/底部（日志查看器之下）。 |
| `cron:top` / `cron:bottom` | `/cron` 页面的顶部/底部。 |
| `skills:top` / `skills:bottom` | `/skills` 页面的顶部/底部。 |
| `config:top` / `config:bottom` | `/config` 页面的顶部/底部。 |
| `env:top` / `env:bottom` | `/env`（键值列表）页面的顶部/底部。 |
| `docs:top` / `docs:bottom` | `/docs` 页面的顶部（iframe之上）/底部。 |
| `chat:top` / `chat:bottom` | `/chat` 页面的顶部/底部（仅当启用了嵌入式聊天功能时显示）。 |

示例——在“会话”页面顶部添加一个横幅卡片：

```javascript
function PinnedSessionsBanner() {
  return React.createElement(Card, null,
    React.createElement(CardContent, { className: "py-2 text-xs" },
      "Pinned note injected by my-plugin"),
  );
}

window.__HERMES_PLUGINS__.registerSlot("my-plugin", "sessions:top", PinnedSessionsBanner);
```

如果您的插件仅用于增强现有页面，无需独立的侧边栏标签页，那么可以将页面级插槽与 `tab.hidden: true` 结合使用。

Shell 仅会为上述插槽渲染 `<PluginSlot name="..." />`。对于嵌套式插件界面，注册表还支持使用其他名称——插件可通过 `SDK.components.PluginSlot` 自定义其插槽。

#### 重新注册与 HMR

如果相同的 `(plugin, slot)` 对被重复注册，后一次调用会替换前一次的注册结果——这一行为与 React HMR 对插件重新挂载的预期一致。

### 替换内置页面（`tab.override`）

将 `tab.override` 设置为某个内置路由路径，即可让插件的组件替代该页面，而非新增一个标签页。当主题希望自定义首页路径（如 `/`），同时又要保持仪表板其他部分的原有结构时，此功能非常有用。

```json
{
  "name": "my-home",
  "label": "Home",
  "tab": {
    "path": "/my-home",
    "override": "/",
    "position": "end"
  },
  "entry": "dist/index.js"
}
```

当设置 `override` 时：

- 路由器中的 `/` 页面组件会被移除。
- 取而代之的是由您的插件在 `/` 地址处进行渲染。
- 对于 `tab.path`，不会添加导航标签页（这正是设置 `override` 的意义所在）。

同一路径只能被一个插件覆盖。如果有两个插件试图覆盖同一路径，第一个插件会生效，第二个插件将被忽略，并同时显示开发模式警告。

如果您仅需在现有页面上添加卡片或工具栏，而不想完全接管该页面，建议使用[页面作用域插槽](#augmenting-built-in-pages-page-scoped-slots)。

### 扩展内置页面（页面作用域插槽）

通过 `tab.override` 进行完全替换的方式效率较低——因为您的插件将掌控整个页面，包括后续的所有更新。大多数情况下，您只是想在现有页面上添加横幅、卡片或工具栏，而这正是**页面作用域插槽**的用途。

所有内置页面都会在其内容区域的顶部和底部提供 `<page>:top` 和 `<page>:bottom` 插槽。您只需调用 `registerSlot()` 即可填充其中一个插槽——内置页面仍能正常运行，同时您的组件也会与其一同显示。

可用插槽包括：`sessions:*`、`analytics:*`、`logs:*`、`cron:*`、`skills:*`、`config:*`、`env:*`、`docs:*`、`chat:*`（每个插槽都包含 `:top` 和 `:bottom` 变体）。完整的插槽列表请参见[Shell 插槽 → 插槽目录](#slot-catalogue)。

以下是一个简单示例：将横幅固定在“会话”页面的顶部：

```json
// ~/.hermes/plugins/session-notes/dashboard/manifest.json
{
  "name": "session-notes",
  "label": "Session Notes",
  "tab": { "path": "/session-notes", "hidden": true },
  "slots": ["sessions:top"],
  "entry": "dist/index.js"
}
```

```javascript
// ~/.hermes/plugins/session-notes/dashboard/dist/index.js
(function () {
  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { Card, CardContent } = SDK.components;

  function Banner() {
    return React.createElement(Card, null,
      React.createElement(CardContent, { className: "py-2 text-xs" },
        "Remember to label important sessions before archiving."),
    );
  }

  // Placeholder for the hidden tab.
  window.__HERMES_PLUGINS__.register("session-notes", function () { return null; });

  // The real work.
  window.__HERMES_PLUGINS__.registerSlot("session-notes", "sessions:top", Banner);
})();
```

要点说明：

- `tab.hidden: true` 可让插件不会显示在侧边栏中——因为这类插件没有独立的页面。
- `slots` 字段仅用于文档说明，实际的绑定操作是通过 JS 包中的 `registerSlot()` 方法来完成的。
- 多个插件可以占用同一个页面范围的插槽，它们会按照注册顺序依次叠加显示。
- 若没有插件注册，则不会对系统造成任何影响：内置页面将保持原有的显示方式。

参考插件 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins/tree/main/example-dashboard) 中的 `example-dashboard` 提供了一个实时演示，该演示会将横幅插入到 `sessions:top` 位置——安装该插件即可完整了解这一工作流程。

### 仅包含插槽的插件（`tab.hidden`）

当设置 `tab.hidden: true` 时，插件会注册其组件（用于直接通过 URL 访问）以及相关的插槽，但不会在导航栏中添加对应的标签页。这类插件主要用于向页面中的特定位置插入内容，比如页眉徽标、侧边栏操作面板或覆盖层等。

```json
{
  "name": "header-crest",
  "label": "Header Crest",
  "tab": {
    "path": "/header-crest",
    "position": "end",
    "hidden": true
  },
  "slots": ["header-left"],
  "entry": "dist/index.js"
}
```

该捆绑包仍会使用一个占位组件调用 `register()` 方法（这是为防止有人直接访问该 URL 而采取的良好实践），随后再通过 `registerSlot()` 方法来执行实际功能。

### 后端 API 路由

插件可以通过在清单中设置 `api` 参数来注册 FastAPI 路由。首先创建相应文件，并导出一个 `router` 对象：

```python
# ~/.hermes/plugins/my-plugin/dashboard/plugin_api.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/data")
async def get_data():
    return {"items": ["one", "two", "three"]}

@router.post("/action")
async def do_action(body: dict):
    return {"ok": True, "received": body}
```

路由会被挂载在 `/api/plugins/<name>/` 下，因此上述请求路径可表示为：

- `GET  /api/plugins/my-plugin/data`
- `POST /api/plugins/my-plugin/action`

由于控制台服务器默认绑定在本地主机上，插件 API 路由无需经过会话令牌认证。**如果运行了不可信的插件，请勿使用 `--host 0.0.0.0` 将控制台暴露在公共网络接口上**——否则这些插件的路由也会被访问到。

#### 访问 Hermes 内部功能

后端路由在控制台进程内部运行，因此可以直接从 hermes-agent 代码库中导入相关功能：

```python
from fastapi import APIRouter
from hermes_state import SessionDB
from hermes_cli.config import load_config

router = APIRouter()

@router.get("/session-count")
async def session_count():
    db = SessionDB()
    try:
        count = len(db.list_sessions(limit=9999))
        return {"count": count}
    finally:
        db.close()

@router.get("/config-snapshot")
async def config_snapshot():
    cfg = load_config()
    return {"model": cfg.get("model", {})}
```

### 每个插件的自定义 CSS

如果您的插件需要超出 Tailwind 类别和内联 `style=` 属性之外的样式，可以添加一个 CSS 文件，并在清单文件中引用它：

```json
{
  "css": "dist/style.css"
}
```

该文件会在插件加载时以 `<link>` 标签的形式被注入。建议使用特定的类名以避免与控制面板的样式发生冲突，同时引用控制面板的 CSS 变量以确保设计风格的一致性。

```css
/* dist/style.css */
.my-plugin-chart {
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-card-foreground);
  padding: 1rem;
}
.my-plugin-chart:hover {
  border-color: var(--color-ring);
}
```

控制面板会将每个 shadcn token 以 `--color-*` 的形式暴露出来，同时还会提供主题相关的额外参数（如 `--theme-asset-*`、`--component-<bucket>-*`、`--radius`、`--spacing-mul`）。通过使用这些参数，您的插件就能自动适配当前生效的主题风格。

### 插件发现与重新加载

控制面板会扫描三个目录以查找 `dashboard/manifest.json` 文件：

| 优先级 | 目录路径 | 来源标签 |
|----------|-----------|--------------|
| 1（冲突时优先使用） | `~/.hermes/plugins/<name>/dashboard/` | `user` |
| 2 | `<repo>/plugins/memory/<name>/dashboard/` | `bundled` |
| 2 | `<repo>/plugins/<name>/dashboard/` | `bundled` |
| 3 | `./.hermes/plugins/<name>/dashboard/` | `project` — 仅当设置了 `HERMES_ENABLE_PROJECT_PLUGINS` 时生效 |

插件发现结果会针对每个控制面板进程进行缓存。添加新插件后，可以：

```bash
# Force a rescan without restart
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

…或重启 `hermes dashboard`。

#### 插件加载生命周期

1. 控制面板加载。`main.tsx` 会将 SDK 暴露在 `window.__HERMES_PLUGIN_SDK__` 中，将插件注册表暴露在 `window.__HERMES_PLUGINS__` 中。
2. `App.tsx` 调用 `usePlugins()` → 发起 `GET /api/dashboard/plugins` 请求。
3. 对于每个插件清单：首先注入 CSS `<link>` 标签（如果已声明），随后通过 `<script>` 标签加载 JS 包。
4. 插件的 IIFE 代码开始运行，并调用 `window.__HERMES_PLUGINS__.register(name, Component)` —— 对于每个插槽，还可选择性地调用 `.registerSlot(name, slot, Component)`。
5. 控制面板会根据插件清单解析已注册的组件，将对应标签页添加到导航栏中（除非被标记为 `hidden`），并将其作为路由进行渲染。

插件在脚本加载后的 **2秒** 内必须调用 `register()` 方法。超过此时间后，控制面板将停止等待并完成初始渲染。如果后续有插件注册，它仍然会显示出来——因为导航栏是响应式的。

如果插件的脚本加载失败（如 404 错误、语法错误或 IIFE 执行期间出现异常），控制面板会在浏览器控制台记录警告信息，然后继续正常运行，无需该插件。

---

## 组合主题与插件的演示

[`strike-freedom-cockpit`](https://github.com/NousResearch/hermes-example-plugins/tree/main/strike-freedom-cockpit) 插件（位于配套仓库 `hermes-example-plugins` 中）是一个完整的主题重制演示示例。它通过将主题 YAML 文件与仅支持插槽的插件结合使用，无需修改控制面板代码即可实现类似驾驶舱风格的 HUD。

**该演示展示了以下内容：**

- 一个完整的主题，包含调色板、字体设置、`fontUrl`、`layoutVariant: cockpit`、`assets`、`componentStyles`（带圆角的卡片、渐变背景）、`colorOverrides` 以及 `customCSS`（扫描线叠加效果）等功能。
- 一个仅支持插槽的插件（通过 `tab.hidden: true` 设置），可注册到三个插槽中：
  - `sidebar` —— 一个 MS-STATUS 面板，其实时数据条由 `SDK.api.getStatus()` 提供。
  - `header-left` —— 一个显示当前主题中 `--theme-asset-crest` 内容的阵营徽章。
  - `footer-right` —— 一个自定义标语，用于替换默认的组织名称行。
- 该插件通过 CSS 变量读取主题提供的图像资源，因此更换主题时无需修改插件代码即可改变背景图像或徽章内容。

**安装方式：**

```bash
git clone https://github.com/NousResearch/hermes-example-plugins.git

# Theme
cp hermes-example-plugins/strike-freedom-cockpit/theme/strike-freedom.yaml \
   ~/.hermes/dashboard-themes/

# Plugin
cp -r hermes-example-plugins/strike-freedom-cockpit ~/.hermes/plugins/
```

打开控制面板，从主题切换器中选择 **Strike Freedom**。此时控制台侧边栏会出现，页头会显示品牌标识，而页脚则会被标语取代。若再切换回 **Hermes Teal**，该插件虽仍已安装，但不会显示出来（因为 `sidebar` 插槽仅在 `cockpit` 布局模式下才会渲染）。

可以查看插件的源代码（位于配套仓库中的 `strike-freedom-cockpit/dashboard/dist/index.js`），了解它是如何读取 CSS 变量的、如何针对不支持插槽的旧版控制面板进行兼容处理，以及如何从一个代码包中注册三个插槽的。

---

## API 参考

### 主题相关端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/dashboard/themes` | GET | 列出所有可用主题及其当前激活名称。内置主题会返回 `{name, label, description}`；用户自定义主题还会包含一个 `definition` 字段，其中存储完整的标准化主题对象。 |
| `/api/dashboard/theme` | PUT | 设置当前激活的主题。请求体格式为 `{"name": "midnight"}`。该设置会被保存到 `config.yaml` 文件的 `dashboard.theme` 字段中。 |

### 插件相关端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/dashboard/plugins` | GET | 列出已发现的插件（包含清单文件，但不包括内部字段）。 |
| `/api/dashboard/plugins/rescan` | GET | 在不重启的情况下强制重新扫描插件目录。 |
| `/dashboard-plugins/<name>/<path>` | GET | 从插件的 `dashboard/` 目录中提供静态资源。系统会阻止路径遍历攻击。 |
| `/api/plugins/<name>/*` | * | 由插件注册的后端路由。 |

### `window` 对象上的 SDK

| 全局变量 | 类型 | 提供方 |
|----------|------|--------|
| `window.__HERMES_PLUGIN_SDK__` | 对象 | `registry.ts` —— 包含 React、钩子函数、UI 组件、API 客户端及实用工具。 |
| `window.__HERMES_PLUGINS__.register(name, Component)` | 函数 | 用于注册插件的主组件。 |
| `window.__HERMES_PLUGINS__.registerSlot(name, slot, Component)` | 函数 | 用于将组件注册到指定名称的插槽中。 |

---

## 故障排除

**我的主题没有出现在主题选择器中。**
请确认相关文件位于 `~/.hermes/dashboard-themes/` 目录下，且文件扩展名为 `.yaml` 或 `.yml`。之后刷新页面，并执行命令 `curl http://127.0.0.1:9119/api/dashboard/themes`，您的主题应会出现在响应结果中。如果 YAML 文件存在解析错误，相关日志会记录在 `~/.hermes/logs/` 目录下的 `errors.log` 文件中。

**我的插件标签页没有显示。**
1. 确认清单文件位于 `~/.hermes/plugins/<name>/dashboard/manifest.json` 中（注意其中必须包含 `dashboard/` 子目录）。
2. 执行命令 `curl http://127.0.0.1:9119/api/dashboard/plugins/rescan` 以强制重新发现插件。
3. 打开浏览器开发者工具 → 网络标签页，确认 `manifest.json`、`index.js` 以及所有加载的 CSS 文件均未出现 404 错误。
4. 打开浏览器开发者工具 → 控制台标签页，查看在 IIFE 执行过程中是否有错误，或者是否存在 `window.__HERMES_PLUGINS__ is undefined` 的提示（这通常表明 SDK 未能初始化，很可能是之前 React 渲染出现了问题）。
5. 确认您的代码包确实使用了与 `manifest.json:name` **完全相同** 的名称来调用 `window.__HERMES_PLUGINS__.register(...)` 函数。

**通过插槽注册的组件无法渲染。**
只有当当前激活的主题的 `layoutVariant` 为 `cockpit` 时，`sidebar` 插槽才会被渲染；其他插槽则始终会显示。如果您尝试向某个没有匹配到的插槽注册组件，可以在 `registerSlot` 函数中添加 `console.log` 语句，以确认插件代码包是否成功执行。

**插件对应的后端路由返回 404 错误。**
1. 确认清单文件中包含 `"api": "plugin_api.py"` 这一字段，且该值指向 `dashboard/` 目录下存在的实际文件。
2. 重启 `hermes dashboard` 服务——插件 API 路由仅在启动时加载一次，**不会在重新扫描时自动加载**。
3. 确认 `plugin_api.py` 文件导出了模块级的 `router = APIRouter()` 对象。其他形式的导出内容则不会被识别。
4. 查看 `~/.hermes/logs/errors.log` 文件中的相关日志，寻找类似 “Failed to load plugin <name> API routes” 的提示——导入错误的信息会记录在此处。

**更换主题后，我自定义的颜色设置丢失了。**
`colorOverrides` 设置是针对当前激活的主题生效的，每当切换主题时这些设置就会被清除——这是该功能的设计初衷。如果您希望自定义颜色设置能够持久保留，应将其放入主题的 YAML 文件中，而非实时主题切换器中。

**主题中的 customCSS 内容被截断。**
每个主题的 `customCSS` 内容长度上限为 32 KiB。对于较大的样式表，建议将其拆分到多个主题中，或者使用通过 `css` 字段注入完整样式表的插件（此类插件没有长度限制）。

**我想将插件发布到 PyPI 上。**
控制面板插件是通过目录结构来安装的，而非通过 pip 的入口点来安装。目前最简便的发布方式是让用户将相关代码库克隆到 `~/.hermes/plugins/` 目录下。目前暂未实现针对控制面板插件的基于 pip 的安装机制。
