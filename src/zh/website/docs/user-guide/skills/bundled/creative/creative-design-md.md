---
title: "Design Md — Author/validate/export Google's DESIGN"
sidebar_label: "Design Md"
description: "Author/validate/export Google's DESIGN"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# DESIGN.md 技能

用于生成/验证/导出 Google 的 DESIGN.md 标识规范文件。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/creative/design-md` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `design`、`design-system`、`tokens`、`ui`、`accessibility`、`wcag`、`tailwind`、`dtcg`、`google` |
| 相关技能 | [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs)、[`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design)、[`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw)、[`html-artifact`](/docs/user-guide/skills/bundled/creative/creative-html-artifact) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，智能体看到的指令即为此内容。
:::

# DESIGN.md 技能详解

DESIGN.md 是 Google 推出的开放规范（采用 Apache-2.0 许可，文件地址为 `google-labs-code/design.md`），旨在为编程智能体描述视觉设计规范。一个 DESIGN.md 文件包含以下两部分：

- **YAML 前置内容**——机器可读取的设计标识符（标准化数值）
- **Markdown 正文**——人类可阅读的设计思路，按标准章节组织

设计标识符提供精确的数值值，而正文则向智能体说明这些数值的设定依据及应用方法。可通过 CLI 工具（`npx @google/design.md`）对文件结构进行代码检查、验证 WCAG 对比度标准、对比不同版本以检测功能退化，并将结果导出为 Tailwind 或 W3C DTCG JSON 格式。

## 何时使用此技能

- 用户需要 DESIGN.md 文件、设计标识符或设计系统规范
- 用户希望在不同项目或工具中保持统一的界面/品牌风格
- 用户粘贴现有的 DESIGN.md 文件，要求对其进行代码检查、对比、导出或扩展
- 用户希望将样式指南转换为智能体可识别的格式
- 用户需要对色彩方案进行对比度检测或 WCAG 无障碍性验证

若仅需获取视觉灵感或布局示例，建议使用 `popular-web-designs` 技能。对于从零开始设计一次性 HTML 文件（如原型、演示文稿、着陆页、组件库）时的设计流程与风格把控，可使用 `claude-design` 技能。而本技能专门用于处理正式的设计规范文件本身。

## 文件结构

```md
---
version: alpha
name: Heritage
description: Architectural minimalism meets journalistic gravitas.
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  body-md:
    fontFamily: Public Sans
    fontSize: 1rem
rounded:
  sm: 4px
  md: 8px
  lg: 16px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.primary}"
---

## Overview

Architectural Minimalism meets Journalistic Gravitas...

## Colors

- **Primary (#1A1C1E):** Deep ink for headlines and core text.
- **Tertiary (#B8422E):** "Boston Clay" — the sole driver for interaction.

## Typography

Public Sans for everything except small all-caps labels...

## Components

`button-primary` is the only high-emphasis action on a page...
```

## Token 类型

| 类型 | 格式 | 示例 |
|------|------|---------|
| 颜色 | `#` + 十六进制值（sRGB） | `"#1A1C1E"` |
| 尺寸 | 数字 + 单位（`px`、`em`、`rem`） | `48px`、`-0.02em` |
| Token 引用 | `{path.to.token}` | `{colors.primary}` |
| 字体样式 | 包含 `fontFamily`、`fontSize`、`fontWeight`、`lineHeight`、`letterSpacing`、`fontFeature`、`fontVariation` 的对象 | 见上文 |

组件属性白名单：`backgroundColor`、`textColor`、`typography`、`rounded`、`padding`、`size`、`height`、`width`。不同状态（悬停、激活、按下）为**独立的组件条目**，拥有对应的键名（如 `button-primary-hover`），而非嵌套结构。

## 标准章节顺序

这些章节为可选内容，但若存在则必须按此顺序排列。重复的标题会导致文件被拒绝。

1. 概述（别名：品牌与风格）
2. 颜色
3. 字体样式
4. 布局（别名：布局与间距）
5. 立体感与深度（别名：立体效果）
6. 形状
7. 组件
8. 正确做法与禁忌

未知章节会被保留，而不会引发错误。只要值类型有效，未知的 Token 名称也会被接受。未知的组件属性则只会产生警告。

## 创建新的 DESIGN.md 的工作流程

1. **询问用户**（或推断）其品牌风格、主色调以及字体方向。如果用户提供了网站链接、图片或整体氛围描述，需将其转换为上述的 Token 格式。
2. 使用 `write_file` 在项目根目录中编写 `DESIGN.md` 文件。务必包含 `name:` 和 `colors:` 选项；其他章节虽为可选，但建议添加。
3. 在 `components:` 部分使用 Token 引用（如 `{colors.primary}`），而非重复输入十六进制值。这样可确保配色方案来自单一来源。
4. 对文件进行代码检查（见下文）。在提交之前，需修复所有无效的引用或 WCAG 标准违规问题。
5. **如果用户已有项目**，还需在文件旁生成 Tailwind 或 DTCG 导出文件（如 `tailwind.theme.json`、`tokens.json`）。

## 代码检查/差异对比/导出工作流程

该工具的 CLI 命名为 `@google/design.md`（基于 Node 环境）。可直接使用 `npx` 调用，无需全局安装。

```bash
# Validate structure + token references + WCAG contrast
npx -y @google/design.md lint DESIGN.md

# Compare two versions, fail on regression (exit 1 = regression)
npx -y @google/design.md diff DESIGN.md DESIGN-v2.md

# Export to Tailwind theme JSON
npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json

# Export to W3C DTCG (Design Tokens Format Module) JSON
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json

# Print the spec itself — useful when injecting into an agent prompt
npx -y @google/design.md spec --rules-only --format json
```

所有命令均支持使用 `-` 指定标准输入。`lint` 命令在检测到错误时会返回退出码 1。若需以结构化方式呈现检测结果，可使用 `--format json` 标志并对输出内容进行解析。

### 代码检查规则说明（7条规则可检测的问题）

- `broken-ref`（错误）——`{colors.missing}` 指向了不存在的标记
- `duplicate-section`（错误）——相同的 `## Heading` 标题出现了两次
- `invalid-color`、`invalid-dimension`、`invalid-typography`（错误）
- `wcag-contrast`（警告/信息）——组件中的 `textColor` 与 `backgroundColor` 之比未达到 WCAG AA 级标准（4.5:1）及 AAA 级标准（7:1）
- `unknown-component-property`（警告）——使用了上述白名单之外的属性

如果用户关注无障碍性，应在总结中明确指出相关问题——WCAG 检测结果是使用该 CLI 最重要的依据。

## 常见误区

- **切勿嵌套组件变体。** `button-primary.hover` 的写法是错误的；正确的做法是将 `button-primary-hover` 作为同级键使用。
- **十六进制颜色值必须用引号括起。** 否则 YAML 解析器会因 `#` 符号而出错，或对类似 `#1A1C1E` 这样的颜色值进行异常截断。
- **负数值尺寸同样需要加引号。** `letterSpacing: -0.02em` 会被视为 YAML 的流式语法——应写成 `letterSpacing: "-0.02em"`。
- **章节顺序是强制规定的。** 如果用户提供的文本内容顺序混乱，需在保存前将其重新排序为标准列表顺序。
- **当前规范版本为 `version: alpha`**（截至 2026 年 4 月）。该规范仍处于测试阶段，可能会出现破坏性变更，请注意留意。
- **标记引用通过点号路径来解析。** `{colors.primary}` 的写法有效；而 `{primary}` 则无效。

## 规范权威来源

- 代码仓库：https://github.com/google-labs-code/design.md（Apache-2.0 许可协议）
- CLI 包：npm 上的 `@google/design.md`
- 生成的 DESIGN.md 文件的许可证：遵循用户项目所采用的许可协议；规范本身采用 Apache-2.0 许可协议。
