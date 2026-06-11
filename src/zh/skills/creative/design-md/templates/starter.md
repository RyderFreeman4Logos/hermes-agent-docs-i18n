---
version: alpha
name: MyBrand
description: One-sentence description of the visual identity.
colors:
  primary: "#0F172A"
  secondary: "#64748B"
  tertiary: "#2563EB"
  neutral: "#F8FAFC"
  on-primary: "#FFFFFF"
  on-tertiary: "#FFFFFF"
typography:
  h1:
    fontFamily: Inter
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  h2:
    fontFamily: Inter
    fontSize: 2rem
    fontWeight: 600
    lineHeight: 1.2
  body-md:
    fontFamily: Inter
    fontSize: 1rem
    lineHeight: 1.5
  label-caps:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: 600
    letterSpacing: "0.08em"
rounded:
  sm: 4px
  md: 8px
  lg: 16px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
  card:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: 24px
---

## 概述

用一两段文字描述品牌的语调与风格。它能够唤起怎样的情绪？用户在初次接触时应产生何种情感反应？

## 颜色

- **主色（{colors.primary}）：** 用于核心文本、标题以及需要重点突出的区域。
- **辅色（{colors.secondary}）：** 用于辅助文本、边框及元数据。
- **第三色（{colors.tertiary}）：** 用于交互元素——如按钮、链接及其选中状态。应谨慎使用，以保持其强调效果。
- **中性色（{colors.neutral}）：** 用于页面背景及填充区域。

## 字体

所有内容均统一使用 Inter 字体。层次感由字重和字号决定，而非字体系列。显示尺寸的字母间距宜紧凑，正文则采用默认间距。

## 布局

间距基准为 4px。组件内部间距使用 `md`（16px），组件间间距使用 `lg`（24px），章节分隔则使用 `xl`（48px）。

## 圆角设计

圆角尺寸宜适中——交互元素采用 `sm`，卡片则采用 `md`。`full` 尺寸仅用于头像和圆形徽章。

## 组件

- 每个页面上仅允许存在一个高优先级的操作按钮，即 `button-primary`。
- `card` 是用于展示分组内容的默认容器，默认不带阴影效果。

## 正确做法与禁忌

- **正确做法：** 在组件定义中使用占位符引用（如 `{colors.primary}`），而非直接写明十六进制颜色值。
- **禁忌：** 不要在预设色板之外自行添加颜色——应先扩展色板。
- **禁忌：** 不要嵌套组件变体。`button-primary-hover` 是同级组件，而非子组件。
