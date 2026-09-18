---
title: "Sketch — Throwaway HTML mockups: 2-3 design variants to compare"
sidebar_label: "Sketch"
description: "Throwaway HTML mockups: 2-3 design variants to compare"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Sketch

临时 HTML 原型：提供 2-3 种设计版本供用户对比。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/creative/sketch` |
| 版本 | `1.0.1` |
| 开发者 | Hermes Agent（基于 gsd-build/get-shit-done 改编） |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `sketch`、`mockup`、`design`、`ui`、`prototype`、`html`、`variants`、`exploration`、`wireframe`、`comparison` |
| 相关技能 | [`spike`](/docs/user-guide/skills/bundled/software-development/software-development-spike)、[`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design)、[`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs)、[`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，智能体看到的指令即为此内容。
:::

# Sketch

当用户希望在**最终确定设计方案之前**先预览设计方向时，可使用此技能——通过生成临时 HTML 原型来探索各种 UI/UX 构想。其目的是创建 2-3 种交互式版本，以便用户直观对比不同设计方向，而非生成可直接使用的代码。

当用户提出诸如“画出这个界面”“展示X可能的长什么样”“对比布局A和B”“为这个UI提供2-3种设计方案”“让我看看一些变体”“在开发之前先制作个原型”之类的请求时，即可加载此功能。

## 何时不应使用此功能

- 用户需要可用于实际项目的组件——请使用`claude-design`或自行正确构建；
- 用户需要一个精心制作的单次使用HTML文件（如登录页、演示文稿）——请使用`claude-design`；
- 用户需要图表——请使用`excalidraw`或`architecture-diagram`；
- 设计方案已经确定——直接进行开发即可。

## 若用户已安装完整的GSD系统

如果通过`npx get-shit-done-cc --hermes`安装后，`gsd-sketch`作为同级技能出现，那么您可以使用**`gsd-sketch`**来实现更完整的工作流：具备持久化的`.planning/sketches/`目录及MANIFEST文件、前沿模式分析功能、对历史草图的一致性检查，以及与GSD其他组件的深度集成。而此独立的`sketch`技能则是轻量级的单次使用版本，不包含状态管理机制。

> **注意：** 上游的GSD项目（[gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)）已在GitHub上**归档/停止维护**。虽然npm包`get-shit-done-cc`仍可安装，但应将其视为一个已归档的社区项目；而此独立的`sketch`技能才是仍在维护的版本，无需额外依赖。

## 核心方法

```
intake  →  variants  →  head-to-head  →  pick winner (or iterate)
```

### 1. 信息收集（若用户已提供足够信息可跳过此步）

在生成不同版本之前，需先获取三项信息——每次仅询问一项，无需一次性全部收集：

1. **整体氛围**。“希望它呈现出怎样的感觉？请用形容词、情绪或氛围描述。”例如，“宁静、具有编辑风格，类似Linear”这样的描述比单纯的“极简”更能传达意图。
2. **参考案例**。“有哪些应用、网站或产品能体现你设想的氛围？”具体的参考对象远胜于抽象的描述。
3. **核心操作**。“用户在此页面上最需要完成的核心动作是什么？”所有生成版本都应服务于这一核心目标；若无法做到，则只是装饰性内容。

在提出下一个问题之前，简要回顾之前的每个回答。如果用户已经一次性提供了全部三项信息，可直接进入生成版本阶段。

### 2. 生成版本（2-3个，绝不能少于1个，一般不超过4个）

一次生成**2-3个版本**。每个版本都应是一个完整、独立的HTML文件。不要仅对版本进行描述，而要直接将其构建出来——其意义在于便于对比。

每个版本应采用**不同的设计理念**，而非仅调整像素值。以下是三个实用的设计维度：

- **密度**：紧凑型 / 轻盈型 / 高密度型（选择两个对比鲜明的风格）
- **重点突出方式**：内容优先 / 操作优先 / 工具优先
- **美学风格**：编辑风 / 实用风 / 休闲风
- **布局结构**：单列式 / 侧边栏式 / 分屏式
- **呈现形式**：卡片式 / 纯内容式 / 文档式

从其中一个维度入手进行差异化设计。仅通过强调色差异来区分的两个版本属于无效努力——用户根本无法区分它们。

**版本命名**：描述其设计理念，而非编号。

<!-- ascii-guard-ignore -->
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

每个版本都应是一个**独立的 HTML 文件**：

- 内联 `<style>` 标签——无需构建步骤，也不需要外部 CSS 文件
- 可使用系统字体或通过 `<link>` 引入的某款 Google 字体
- 通过 CDN 引入 Tailwind（如 `<script src="https://cdn.tailwindcss.com"></script>`）也是可行的
- 内容需真实可信——使用真实的句子和姓名，而非“Lorem ipsum”之类的占位文本
- **具备交互性**：链接可点击，悬停效果真实，且至少包含一种状态切换（如展开/收起、筛选、切换）。相比粗糙的动画效果，静态图像反倒更糟糕。

请在浏览器中打开该文件。如果发现显示异常，请在展示给用户之前先进行修复。

**建议使用 Hermes 的浏览器工具来直观检查各版本的效果**。不要仅仅编写 HTML 文件后就期望它能正常显示；应逐一加载每个版本并仔细查看其呈现效果。

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
