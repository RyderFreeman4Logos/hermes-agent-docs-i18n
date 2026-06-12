---
title: "Sketch — Throwaway HTML mockups: 2-3 design variants to compare"
sidebar_label: "Sketch"
description: "Throwaway HTML mockups: 2-3 design variants to compare"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Sketch

临时性 HTML 原型：提供 2-3 种设计版本供用户对比。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/creative/sketch` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent（基于 gsd-build/get-shit-done 改编） |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `sketch`、`mockup`、`design`、`ui`、`prototype`、`html`、`variants`、`exploration`、`wireframe`、`comparison` |
| 相关技能 | [`spike`](/docs/user-guide/skills/bundled/software-development/software-development-spike)、[`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design)、[`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs)、[`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能运行时，智能体看到的指令即为此内容。
:::

# Sketch

当用户希望在**最终确定设计方案之前**先预览设计方向，或想通过临时性 HTML 原型来探索某个 UI/UX 构思时，可使用此技能。其目的是生成 2-3 种交互式版本，以便用户直观对比不同设计方向，而非输出可直接使用的代码。

当用户说出“为这个界面画个草图”、“让我看看 X 可能长什么样”、“对比一下布局 A 和 B”、“给我出 2-3 种这个 UI 的设计方案”、“让我看看一些不同版本”、“在开发之前先做个原型”等类似语句时，可使用此技能。

## 何时不应使用此技能

- 用户需要可用于实际项目的组件——请使用 `claude-design` 或自行正确实现
- 用户需要经过精心制作的单次使用 HTML 文件（如登录页、演示文稿）——请使用 `claude-design`
- 用户需要图表——请使用 `excalidraw`、`architecture-diagram`
- 设计方案已确定——直接进行开发即可

## 如果用户已安装完整的 GSD 系统

如果 `gsd-sketch` 作为同级技能出现（通过 `npx get-shit-done-cc --hermes` 安装），则建议使用 **`gsd-sketch`** 以获得完整的工作流体验：包含 MANIFEST 文件的持久化 `.planning/sketches/` 目录、前沿模式分析、对历史草图的一致性检查，以及与 GSD 其他组件的集成。本技能为轻量级的独立版本，仅支持一次性草图绘制，不具备状态管理功能。

## 核心方法

```
intake  →  variants  →  head-to-head  →  pick winner (or iterate)
```

### 1. 信息收集（若用户已提供足够信息则可直接跳过）

在生成不同版本之前，需先获取三项信息——每次仅询问一项，无需一次性全部问完：

1. **整体氛围**。“它应该呈现出怎样的感觉？请用形容词、情绪或氛围词来描述。”例如，“宁静、具有编辑感，类似Linear的设计风格”，这样的描述比单纯的“极简”更有意义。
2. **参考案例**。“有哪些应用、网站或产品能体现你设想的氛围？”具体的参考案例远比抽象的描述更有价值。
3. **核心操作**。“用户在该页面上最需要完成的核心动作是什么？”所有生成的版本都应服务于这一核心目标；若无法做到，则只是装饰而已。

在提出下一个问题之前，先简要思考一下之前的回答。如果用户已经一次性提供了这三项信息，可直接进入生成版本阶段。

### 2. 不同版本生成（2-3个，绝不能只有1个，很少超过4个）

一次生成**2-3个不同版本**。每个版本都应是一个完整且独立的HTML文件。不要仅对版本进行描述，而要直接将其构建出来——这样做的目的是便于对比。

每个版本应采用**不同的设计理念**，而非仅仅调整像素数值。以下是三个实用的设计维度：

- **密度**：紧凑型 / 轻盈型 / 极致密集型（选择两个对比鲜明的风格）
- **重点突出方式**：内容优先 / 操作优先 / 工具优先
- **美学风格**：编辑风 / 实用风 / 有趣风
- **布局结构**：单列布局 / 侧边栏布局 / 分屏布局
- **呈现形式**：卡片式 / 纯内容展示 / 文档式

从其中一个维度入手进行设计调整。如果两个版本仅颜色略有不同，那完全是浪费精力——用户根本无法区分它们。

**版本命名**：应描述其设计理念，而非编号。
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

- 内联 `<style>` 标签——无需构建步骤，也无需外部 CSS 文件
- 可使用系统字体或通过 `<link>` 引入的某款 Google 字体
- 通过 CDN 引入 Tailwind（如 `<script src="https://cdn.tailwindcss.com"></script>`）也是可行的
- 内容需真实可信——应包含实际的句子和姓名，而非“Lorem ipsum”之类的占位文本
- **具备交互性**：链接可点击，悬停效果真实，且至少存在一种状态切换（如打开/关闭、筛选、切换）。相比粗糙的动画效果，静态图片反倒更糟糕。

请在浏览器中打开该文件。如果发现格式错误，务必在展示给用户之前修复它。

**建议使用 Hermes 的浏览器工具来直观验证各变体**。不要只编写 HTML 代码就期望它能正常显示；应逐一加载每个变体并仔细检查其效果。

```
browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="Does this layout look clean and readable? Any visible bugs (overlapping text, unstyled elements, broken images)?")
```

`browser_vision`功能会生成关于页面实际内容的AI描述，并提供截图路径——从而能够发现仅通过查看源代码无法察觉的布局问题（例如字体加载失败、弹性容器崩溃等）。需对这些问题进行修复并重新导航，直至所有版本均显示正常。

为实现快速启动，该工具采用**默认CSS重置设置及系统字体栈**。

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

### 4. 变体 README 文件

每个变体的 `README.md` 都会回答以下问题：

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

在所有变体构建完成后，应以对比形式呈现它们。切勿仅做罗列——而应给出**有见地的分析**：

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

让用户自行选出胜出方案，或将两个方案合并为混合版本，或是要求进行下一轮投票。

## 主题设置（当项目已设定视觉风格时）

如果用户已有既定的主题配置（颜色、字体、令牌），请将共享令牌放入 `sketches/themes/tokens.css` 文件中，并在每个变体中通过 `@import` 引入这些令牌。同时需注意保持令牌数量最少：

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

无需对临时草图进行过度标记化处理——通常三种颜色和一种字体就足够了。

## 交互性标准

当用户能够实现以下操作时，该草图即具备足够的交互性：

1. **点击主要操作按钮**后能触发可见的反馈（状态变化、模态框、提示信息或导航操作）；
2. **观察到有意义的界面状态转换**（如筛选列表、切换模式、打开/关闭面板）；
3. **将鼠标悬停在可识别的交互元素上**（如按钮、行、标签页）。

若超出这些标准，则属于对临时草图的过度设计；若未达到这些标准，则仅相当于截图而已。

## Frontier模式（选择下一个要设计的界面）

当已有草图存在且用户询问“接下来该设计什么？”时，可参考以下标准进行筛选：

- **一致性缺失**——来自不同草图的两个优秀方案做出了独立选择，但尚未整合在一起；
- **未设计的界面**——虽在草图中提及，但实际从未被设计过；
- **状态覆盖不足**——仅设计了正常流程的界面，而缺少空状态、加载状态、错误状态或包含1000个元素的场景；
- **响应式问题**——在某一屏幕尺寸下验证通过，但在移动端或超宽屏上表现如何？
- **交互模式缺失**——虽然存在静态布局，但缺乏过渡动画、拖拽或滚动等交互行为。

根据以上标准提出2到4个候选方案，由用户自行选择。

## 输出要求

- 在项目根目录下创建`sketches/`文件夹（如果用户遵循GSD规范，则使用`.planning/sketches/`）；
- 为每个候选方案创建一个子文件夹，结构为`NNN-stance-name/index.html`以及`README.md`文件；
- 告诉用户如何打开这些文件：在macOS上使用`open sketches/001-calm-editorial/index.html`，在Linux上使用`xdg-open`，在Windows上使用`start`；
- 注意保持候选方案的临时性——那些确实需要保留的草图应被整合进正式的项目代码中，而非作为独立资产进行管理。

**针对每个候选方案，典型的工具使用流程如下：**

```
terminal("mkdir -p sketches/001-calm-editorial")
write_file("sketches/001-calm-editorial/index.html", "<!doctype html>...")
write_file("sketches/001-calm-editorial/README.md", "## Variant: Calm editorial\n...")
browser_navigate(url="file://$(pwd)/sketches/001-calm-editorial/index.html")
browser_vision(question="How does this look? Any obvious layout issues?")
```

请对每个变体重复上述操作，随后生成对比表格。

## 出处说明

本方案改编自 GSD（Get Shit Done）项目中的 `/gsd-sketch` 工作流 — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。完整的 GSD 系统会提供持续的草图状态管理、主题/变体模式引用功能以及一致性审核工作流；可通过 `npx get-shit-done-cc --hermes --global` 命令进行安装。
