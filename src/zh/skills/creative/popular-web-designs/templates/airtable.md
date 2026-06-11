# 设计系统：Airtable

> **Hermes Agent — 实现说明**
>
> 原版网站使用了专有字体。如需生成独立的 HTML 输出，可使用以下 CDN 替代方案：
> - **正文字体**：`Inter` | **等宽字体**：`system monospace stack`
> - **字体堆栈（CSS）**：`font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;`
> - **等宽字体堆栈（CSS）**：`font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;`
> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
> ```
> 可使用 `write_file` 函数生成 HTML 文件，再通过 `generative-widgets` 技能（配合 cloudflared 隧道）进行发布。生成后可使用 `browser_vision` 工具验证视觉效果是否准确。

## 1. 视觉主题与氛围

Airtable 的网站风格简洁且适合企业使用，它以纯白色背景为基调，搭配深海军蓝文字（`#181d26`）以及作为主要交互强调色的 Airtable 蓝色（`#1b61c9`），从而展现出“精致简约”的设计感。Haas 字体系列（包含展示用与正文用版本）构成了具有瑞士式精准度的排版系统，所有文字均采用适度的字距设计。

**核心特征：**
- 纯白色背景，搭配深海军蓝文字（`#181d26`）
- 以 Airtable 蓝色（`#1b61c9`）作为主要操作按钮和链接颜色
- Haas + Haas Groot Disp 双字体系统
- 正文文字具有适度的字距（0.08px–0.28px）
- 按钮半径为 12px，卡片半径为 16px–32px
- 多层蓝色阴影效果：`rgba(45,127,249,0.28) 0px 1px 3px`
- 使用语义化主题变量：`--theme_*` CSS 变量命名

## 2. 颜色方案与用途

### 主要颜色
- **深海军蓝**（`#181d26`）：正文文字颜色
- **Airtable 蓝色**（`#1b61c9`）：操作按钮及链接颜色
- **白色**（`#ffffff`）：主要背景色
- **高亮色**（`rgba(249,252,255,0.97)`）：用于 `--theme_button-text-spotlight` 属性

### 语义化颜色
- **成功绿色**（`#006400`）：用于 `--theme_success-text`
- **浅色文字**（`rgba(4,14,32,0.69)`）：用于 `--theme_text-weak`
- **次要激活色**（`rgba(7,12,20,0.82)`）：用于 `--theme_button-text-secondary-active`

### 中性颜色
- **深灰色**（`#333333`）：辅助文字颜色
- **中蓝**（`#254fad`）：链接及强调色变体
- **边框色**（`#e0e2e6`）：卡片边框颜色
- **浅背景色**（`#f8fafc`）：柔和的背景色

### 阴影效果
- **蓝色阴影**：`rgba(0,0,0,0.32) 0px 0px 1px, rgba(0,0,0,0.08) 0px 0px 2px, rgba(45,127,249,0.28) 0px 1px 3px, rgba(0,0,0,0.06) 0px 0px 0px 0.5px inset`
- **柔和阴影**：`rgba(15,48,106,0.05) 0px 0px 20px`

## 3. 排版规则

### 字体系列
- **正文字体**：`Haas`，备用字体：`-apple-system, system-ui, Segoe UI, Roboto`
- **展示字体**：`Haas Groot Disp`，备用字体：`Haas`

### 层级结构

| 元素类型 | 字体 | 字号 | 字重 | 行高 | 字距 |
|----------|------|------|------|------|------|
| 标题级展示文字 | Haas | 48px | 400 | 1.15 | 正常 |
| 加粗展示文字 | Haas Groot Disp | 48px | 900 | 1.50 | 正常 |
| 段落标题 | Haas | 40px | 400 | 1.25 | 正常 |
| 子标题 | Haas | 32px | 400–500 | 1.15–1.25 | 正常 |
| 卡片标题 | Haas | 24px | 400 | 1.20–1.30 | 0.12px |
| 功能描述 | Haas | 20px | 400 | 1.25–1.50 | 0.1px |
| 正文文字 | Haas | 18px | 400 | 1.35 | 0.18px |
| 中等字号正文 | Haas | 16px | 500 | 1.30 | 0.08–0.16px |
| 按钮文字 | Haas | 16px | 500 | 1.25–1.30 | 0.08px |
| 图片说明文字 | Haas | 14px | 400–500 | 1.25–1.35 | 0.07–0.28px |

## 4. 组件样式

### 按钮
- **主蓝色按钮**：颜色为 `#1b61c9`，文字为白色，内边距为 16px × 24px，半径为 12px
- **白色按钮**：背景为白色，文字为 `#181d26`，半径为 12px，带 1px 宽的白色边框
- **Cookie 同意按钮**：背景为 `#1b61c9`，半径为 2px（边缘较锐利）

### 卡片：边框为 `1px solid #e0e2e6`，半径为 16px–24px
### 输入框：采用标准的 Haas 字体样式

## 5. 布局规范
- 内边距：1–48px（基础值为 8px）
- 圆角半径：小元素为 2px，按钮为 12px，卡片为 16px，段落为 24px，大型元素为 32px，圆形元素为 50%

## 6. 深度感设计
- 使用多层蓝色阴影效果
- 添加柔和的环境光阴影：`rgba(15,48,106,0.05) 0px 0px 20px`

## 7. 操作指南：该做什么与不该做什么
### 应该做的：
- 使用 Airtable 蓝色作为操作按钮颜色
- 选用 Haas 字体并保持适当的字距
- 按钮半径设为 12px

### 不应该做的：
- 忽略适当的字距设置
- 使用过重的阴影效果

## 8. 响应式设计
断点范围：425–1664px（共 23 个断点）

## 9. Agent 提示词指南
- 文本颜色：深海军蓝（`#181d26`）
- 操作按钮颜色：Airtable 蓝色（`#1b61c9`）
- 背景颜色：白色（`#ffffff`）
- 边框颜色：`#e0e2e6`
