# Hermes Agent — Web UI

基于浏览器的控制面板，用于管理Hermes Agent的配置、API密钥以及监控正在运行的会话。

## 技术栈

- **Vite** + **React 19** + **TypeScript**
- 带有自定义深色主题的**Tailwind CSS v4**
- 受**shadcn/ui**启发的组件（手动实现，无需依赖CLI）

## 开发相关说明

```bash
# Start the backend API server
cd ../
python -m hermes_cli.main web --no-open

# In another terminal, start the Vite dev server (with HMR + API proxy)
cd web/
npm install
npm run dev
```

打开终端中打印出的**Vite URL**（通常为 `http://localhost:5173`），那就是实时刷新界面。

运行在 9119 端口的 `hermes dashboard` 提供的是来自 `hermes_cli/web_dist/` 的**已构建**代码包，而非 Vite 开发服务器的版本——只有在执行 `npm run build` 并重启仪表板（或使用上述的 `web --no-open` 加上 Vite 方式），`web/src/` 中的更改才会在该界面中显示。

Vite 开发服务器会将 `/api` 请求代理到 `http://127.0.0.1:9119`（即 FastAPI 后端）。

## 构建

```bash
npm run build
```

这些内容会被输出到 `../hermes_cli/web_dist/` 目录中，随后由 FastAPI 服务器以静态单页应用的形式进行提供。通过 `pyproject.toml` 文件中的 package-data 选项，这些构建好的资源文件会被整合进 Python 包中。

## 目录结构

```
src/
├── components/ui/   # Reusable UI primitives (Card, Badge, Button, Input, etc.)
├── lib/
│   ├── api.ts       # API client — typed fetch wrappers for all backend endpoints
│   └── utils.ts     # cn() helper for Tailwind class merging
├── pages/
│   ├── StatusPage   # Agent status, active/recent sessions
│   ├── ConfigPage   # Dynamic config editor (reads schema from backend)
│   └── EnvPage      # API key management with save/clear
├── App.tsx          # Main layout and navigation
├── main.tsx         # React entry point
└── index.css        # Tailwind imports and theme variables
```

## 字体与对比度规则

在添加或修改 UI 样式之前，请先阅读本规则。这些规则可确保仪表板在所有内置主题下都能保持清晰易读，同时避免重新陷入设计系统刚刚摒弃的旧有模式。

### 文本最小尺寸要求

- **正文最小尺寸：`text-xs`（12px / 0.75rem）。** 禁止在文字内容、提示信息、标签、计数值或徽章上使用随意设定的 `text-[0.6rem]`、`text-[0.65rem]`、`text-[9px]`、`text-[10px]` 或 `text-[11px]` 等样式。请使用标准尺寸层级：`text-xs`、`text-sm`、`text-base`。
- 更小的尺寸仅适用于**装饰性叠加元素**（如图表条纹、空状态图标），绝不能用于用户需要阅读的文字。

### 文本最小透明度要求

- **文本透明度绝不可低于 0.7。** 禁止在 `<span>`、`<p>`、标签等元素上使用 `opacity-30`、`opacity-50`、`opacity-60` 等样式。
- **不得叠加透明度属性。** 如 `text-muted-foreground/60`、`text-midground/70`、`text-foreground/50` 这类写法会导致不可预测的 WCAG 合规性问题，因为父级属性本身已包含透明度值。
- 请使用 `@nous-research/ui` 的 `globals.css` 中提供的**语义化文本属性**：
  - `text-text-primary` —— 默认正文文字。
  - `text-text-secondary` —— 字幕、元信息、非激活状态导航文字。
  - `text-text-tertiary` —— 小型边框标签、计数值、脚注文字。
  - `text-text-disabled` —— 禁用状态文字。
  - `text-text-on-accent` —— 高亮背景上的文字。

### 品牌大写格式：使用 `text-display` 而非直接使用 `uppercase`

- 仪表板保留 Nous 品牌的大写视觉风格，但该功能是**按元素单独启用的，而非全局生效**。
- 仅可在**品牌相关元素**上使用 DS 工具类 `text-display` 来实现大写效果——例如页面标题、导航章节标题、徽章、品牌标识。DS 组件（如 `Button`、`Badge`、`Tabs`、`Segmented` 等）已自动应用 `text-display`。
- **请勿在 `hermes-agent/web/src` 中引入新的 `uppercase` 类**（即 Tailwind 的原生大写类）。对于新的品牌相关元素，建议优先使用 `text-display`。现有的 `uppercase` 使用位置（如 `components/ui/label.tsx`、`card.tsx`）将在后续迁移前保持不变。
- 由于应用壳层不再强制全局大写，因此无需再统一设置 `normal-case`。仅在 DS 组件已应用 `text-display` 但标签仍需保持小写格式时才使用 `normal-case`——例如动态用户内容（模型名称、主题名称），或非品牌相关元素的固定 UI 文本（如 EnvPage 的“未配置”切换按钮、侧边栏的“新建聊天”按钮）。

### 字体选择

字体设置也是**按界面区域单独启用的，而非在布局壳层全局生效**——应用壳层和页面标题会保留其原有的主题字体或扩展字体；只有明确指定时才会使用 Mondwest 字体。

| 层级 | 类名 | 适用场景 |
|------|------|----------|
| 品牌相关元素 | `font-mondwest text-display`（或 `themedChrome`） | 侧边栏导航、卡片章节标题（`CardTitle`）、Segmented 过滤按钮、过滤面板标题 |
| 主题正文区域 | `font-mondwest normal-case`（或 `themedBody`） | 卡片内容（`Card`、`CardDescription`）、会话/平台信息行、分析表格——**效果仅限于对应组件内部** |
| 页面相关元素 | `font-expanded` | 页面标题 h1（`PageHeaderProvider`）——保持小写格式，不使用 `text-display` |
| 品牌标识 | 仅设置字体大小和行高，使用 `Typography` 类 | 侧边栏/移动端的“Hermes Agent”文字——混合大小写，不使用 Mondwest 字体，也不使用 `text-display` |
| 技术相关内容 | `font-mono-ui` / `font-mono` / `font-courier` | 模型名称、环境变量键、调度时间表、YAML 文件、仓库地址等 |

- 请勿在 `<main>`、`App` 或其他布局容器上使用 `themedBody` 或 `themedFont`，因为这会覆盖组件内部的样式设置。
- **`Card` 组件**使用 `themedBody`；**`CardTitle` 组件**使用 `text-display`（实现大写效果）；**`CardDescription` 组件**同样使用 `themedBody`。
- **`NouiTypography`** 默认使用 `font-sans` 字体，除非显式传入其他字体属性。
- 在新的仪表板 UI 中，请勿直接使用 `font-sans` 或 `font-display`（主题中的无衬线字体变量），建议优先选择上述适合品牌风格的 Mondwest 字体层级。

### 颜色属性

- 建议优先使用**语义化颜色属性**（如 `text-text-*`、`bg-card`、`border-border`、`text-foreground`、`text-destructive`、`text-success`、`text-warning`），而非直接使用层级参考名称（如 `text-midground`、`text-foreground`）。
- `text-muted-foreground` 现已与 `--color-text-secondary` 绑定，因此现有代码仍可正常运行，但新代码建议优先使用语义化名称。
- 当确实需要非属性形式的颜色值时（例如在图表上为图标添加弱化效果，或通过内联样式设置终端文字前景色），请确保所有文字的透明度保持在 **≥ 0.7**。

