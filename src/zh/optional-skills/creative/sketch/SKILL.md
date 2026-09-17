---
name: sketch
description: "Throwaway HTML mockups: 2-3 design variants to compare."
version: 1.0.1
author: Hermes Agent (adapted from gsd-build/get-shit-done)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sketch, mockup, design, ui, prototype, html, variants, exploration, wireframe, comparison]
    related_skills: [spike, claude-design, popular-web-designs, excalidraw]
---

# 草图设计

当用户希望在**最终确定设计方案之前**先预览设计方向时，可使用此技能——通过临时性的 HTML 原型来探索 UI/UX 构想。其目的是生成 2-3 种交互式版本，以便用户直观对比不同视觉方案，而非产出可直接使用的代码。

当用户提出“为这个界面画个草图”、“让我看看 X 的可能样式”、“对比一下布局 A 和 B”、“给我 2-3 种这个 UI 的设计思路”、“让我看看一些不同版本”、“在开发前先做个原型”等需求时，即可加载此技能。

## 何时不应使用此技能

- 用户需要可投入实际使用的组件——请使用 `claude-design` 或自行正确构建；
- 用户需要精心制作的单次使用 HTML 文件（如登录页、演示文稿）——请使用 `claude-design`；
- 用户需要图表——请使用 `excalidraw`、`architecture-diagram`；
- 设计方案已确定——直接进行开发即可。

## 若用户已安装完整的 GSD 系统

如果 `gsd-sketch` 作为同级技能出现（通过 `npx get-shit-done-cc --hermes` 安装），则可使用 **`gsd-sketch`** 来实现更完整的工作流：包含带 MANIFEST 文件的持久化 `.planning/sketches/` 目录、前沿模式分析、对历史草图的一致性检查，以及与 GSD 其他组件的深度集成。而当前此技能为轻量级的独立版本——仅支持一次性草图绘制，不包含状态管理功能。

> **注意：** 上游的 GSD 项目（[gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)）已在 GitHub 上**归档/停止维护**。虽然该 npm 包（`get-shit-done-cc`）仍可安装，但请将其视为一个已归档的社区项目——此独立的 `sketch` 技能才是当前正在维护的版本，无需额外依赖。  

## 核心方法

```
intake  →  variants  →  head-to-head  →  pick winner (or iterate)
```

### 1. 信息收集（若用户已提供足够信息则可直接跳过）

在生成不同版本之前，需先获取三项信息——每次仅询问一项，无需一次性全部问完：

1. **整体氛围。**“希望它呈现出怎样的感觉？请用形容词、情绪或氛围词来描述。”例如，“平静、具有编辑风格，类似Linear”的描述比单纯的“极简”更具参考价值。
2. **参考案例。**“有哪些应用、网站或产品能体现你设想的氛围？”具体的参考案例远胜于抽象的描述。
3. **核心操作。**“用户在此页面上最需要完成的核心动作是什么？”所有生成版本都应围绕这一核心功能设计；否则就只是装饰性的存在。

在提出下一个问题之前，简要思考一下之前的回答。如果用户已经一次性提供了这三项信息，则直接进入生成版本阶段。

### 2. 不同版本生成（2-3个，绝不能只有1个，很少超过4个）

一次生成**2-3个不同版本**。每个版本都应是一个完整且独立的HTML文件。不要仅对版本进行描述，而要实际构建出来——其目的在于便于对比。

每个版本应采用**不同的设计理念**，而非仅仅调整像素数值。以下是三个实用的设计维度：

- **密度：**紧凑型/宽松型/超密集型（选择两个对比鲜明的风格）
- **重点突出方式：**内容优先/操作优先/工具优先
- **美学风格：**编辑风/实用风/趣味风
- **布局结构：**单列布局/侧边栏布局/分屏布局
- **呈现形式：**卡片式/纯内容展示/文档式

从其中一个维度入手进行设计调整。如果两个版本仅配色不同，那纯粹是浪费精力——用户根本无法区分它们。

**版本命名：**描述其设计理念，而非版本序号。

```
sketches/
├── 001-calm-editorial/
│   ├── index.html
│   └── README.md
├── 001-utilitarian-dense/
│   ├── index.html
│   └── README.md
└── 001-playful-split/
    ├── index.html
    └── README.md
```

### 3. 将其转化为真实的 HTML 文件

每个变体都应是一个**独立的 HTML 文件**：

- 内联 `<style>` 标签——无需构建步骤，也不需要外部 CSS 文件
- 可使用系统字体或通过 `<link>` 标签引入的某款 Google 字体
- 通过 CDN 引入 Tailwind（`<script src="https://cdn.tailwindcss.com"></script>`）也是可行的
- 内容需真实可信——应使用实际句子和真实姓名，而非“Lorem ipsum”这类虚拟文本
- **具备交互性**：链接可点击，悬停效果自然，且至少存在一种状态切换（如展开/收起、筛选、切换等）。相比粗糙的动画效果，静态图片反而是更糟糕的选择。

请在浏览器中打开这些文件。如果发现显示异常，请在展示给用户之前先进行修复。

**建议使用 Hermes 的浏览器工具来直观验证各变体**。不要仅仅编写 HTML 文件后就期望它能正常渲染；应逐一加载每个变体并仔细查看其显示效果。

```
browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="Does this layout look clean and readable? Any visible bugs (overlapping text, unstyled elements, broken images)?")
```

`browser_vision` 功能会生成关于页面实际内容的 AI 描述以及截图路径，从而能够发现仅通过查看源代码无法发现的布局问题（例如字体加载失败、Flex 容器结构异常等）。需对这些问题进行修复并重新浏览，直至所有版本的外观都符合要求。

为实现快速启动，该工具采用了**默认的 CSS 重置设置与系统字体栈**。

```html
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #1a1a1a;
    background: #fafafa;
    line-height: 1.5;
  }
</style>
```

### 4. 不同版本的 README 文件

每个版本的 `README.md` 都会回答以下问题：

```markdown
## Variant: {stance name}

### Design stance
One sentence on the principle driving this variant.

### Key choices
- Layout: ...
- Typography: ...
- Color: ...
- Interaction: ...

### Trade-offs
- Strong at: ...
- Weak at: ...

### Best for
- The kind of user or use case this variant actually serves
```

### 5. 直接对比

在所有版本构建完成后，应以对比形式呈现它们。切勿仅做简单罗列——而需给出**有见地的评价**：

```markdown
## Three takes on the home screen

| Dimension | Calm editorial | Utilitarian dense | Playful split |
|-----------|----------------|-------------------|---------------|
| Density   | Low            | High              | Medium        |
| Primary action visibility | Low | High | Medium |
| Scan-ability | High | Medium | Low |
| Feel | Calm, trusted | Sharp, tool-like | Inviting, energetic |

**My take:** Utilitarian dense for power users, calm editorial for content-forward audiences. Playful split is weakest — tries to do both and commits to neither.
```

让用户自行选出胜出者，或将两个选项合并为混合版本，或是要求进行下一轮投票。

## 主题设置（当项目已设定视觉风格时）

如果用户已有既定的主题配置（颜色、字体、标记符号），请将共享的标记符号放入 `sketches/themes/tokens.css` 文件中，并在每个变体中通过 `@import` 语句引入这些标记符号。同时应注意保持标记符号的数量尽可能少：

```css
/* sketches/themes/tokens.css */
:root {
  --color-bg: #fafafa;
  --color-fg: #1a1a1a;
  --color-accent: #0066ff;
  --color-muted: #666;
  --radius: 8px;
  --font-display: "Inter", sans-serif;
  --font-body: -apple-system, BlinkMacSystemFont, sans-serif;
}
```

对于那些仅用于临时演示的简单界面，无需过度添加标记元素——通常三种颜色搭配一种字体就足够了。

## 交互性要求

当用户能够实现以下操作时，该界面即具备足够的交互性：

1. **点击主要操作按钮**后能触发可见的反馈（状态变化、弹出窗口、提示信息或导航操作）；
2. **观察到有实际意义的状态转换**（如筛选列表、切换模式、打开/关闭面板）；
3. **将鼠标悬停在可识别的交互元素上**（如按钮、行、标签页）。

若超出这些要求，则属于对简单界面的过度设计；而未达到这些标准则仅相当于截图而已。

## Frontier模式（选择下一个要设计的界面）

当已有若干界面设计，且用户询问“接下来该设计什么？”时，可参考以下标准来筛选候选方案：

- **一致性缺失**——来自不同设计的两个优秀方案分别做出了独立选择，但尚未整合在一起；
- **未设计的界面**——在现有设计中被提及，但实际从未被开发过；
- **状态覆盖不足**——已设计了正常流程下的界面，但缺少空状态、加载状态、错误状态以及包含1000个元素的场景；
- **响应式问题**——在某一屏幕尺寸下测试通过，但在移动端或超宽屏上表现如何？
- **交互模式缺失**——存在静态布局，但缺乏过渡动画、拖拽操作及滚动行为。

根据以上标准提出2到4个具体的候选方案，由用户自行选择。

## 输出结果

- 在仓库根目录下创建 `sketches/` 文件夹（如果用户遵循 GSD 规范，则创建 `.planning/sketches/` 文件夹）。
- 为每个变体创建一个子文件夹，结构为 `NNN-stance-name/index.html` 加上 `README.md` 文件。
- 告诉用户如何打开这些文件：在 macOS 上使用 `open sketches/001-calm-editorial/index.html`，在 Linux 上使用 `xdg-open`，在 Windows 上使用 `start`。
- 应将各变体视为临时文件——只有那些确实需要保留的草图才应升级为正式的项目代码，而非作为独立资源进行管理。

**处理单个变体的典型工具流程：**

```
terminal("mkdir -p sketches/001-calm-editorial")
write_file("sketches/001-calm-editorial/index.html", "<!doctype html>...")
write_file("sketches/001-calm-editorial/README.md", "## Variant: Calm editorial\n...")
browser_navigate(url="file://$(pwd)/sketches/001-calm-editorial/index.html")
browser_vision(question="How does this look? Any obvious layout issues?")
```

请针对每个变体重复执行上述操作，随后生成对比表格。

## 出处说明

本方案改编自 GSD（Get Shit Done）项目中的 `/gsd-sketch` 工作流 — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。该项目的原始代码库现已在 GitHub 上**归档且不再维护**；虽然仍可通过 `npx get-shit-done-cc --hermes --global` 安装对应的 npm 包，它仍能保留草图状态、主题/变体模式引用以及一致性审核工作流，但建议将其视为一个已归档的社区项目。
