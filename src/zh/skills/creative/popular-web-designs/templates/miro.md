# 设计系统：Miro

> **Hermes Agent — 实现说明**
>
> 原版网站使用了专有字体。若需生成独立的 HTML 输出，可使用以下 CDN 替代方案：
> - **正文字体**：`Inter` | **等宽字体**：`system monospace stack`
> - **字体栈（CSS）**：`font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;`
> - **等宽字体栈（CSS）**：`font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;`
> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
> ```
> 可使用 `write_file` 函数创建 HTML 文件，再通过 `generative-widgets` 技能（配合 cloudflared 隧道）进行服务。生成后可使用 `browser_vision` 工具验证视觉效果是否准确。

## 1. 视觉主题与氛围

Miro 的网站是一个简洁且以协作工具为核心的平台，它通过充足的留白、柔和的彩色点缀以及具有现代感的几何字体，展现出“视觉化思维”的理念。该设计以纯白色背景为主，文字颜色接近黑色（`#1c1c1e`），并采用了珊瑚色、玫瑰色、青绿色、橙色、黄色和苔藓绿等独特的柔和色调——每种颜色都代表着不同的协作场景。

在字体选择上，主显示字体为 Roobert PRO Medium，并使用了 OpenType 字符变体（`"blwf", "cv03", "cv04", "cv09", "cv11"`），同时设置了负字距（56px 时为 -1.68px）。正文文本则使用 Noto Sans，它也拥有自己的一组风格参数（`"liga" 0, "ss01", "ss04", "ss05"`）。整个界面基于 Framer 框架构建，因此具备流畅的动画效果和现代化的组件设计。

**核心特征：**
- 纯白色背景，文字颜色接近黑色（`#1c1c1e`）
- 主显示字体为 Roobert PRO Medium，搭配多种 OpenType 字符变体
- 柔和的彩色点缀色：珊瑚色、玫瑰色、青绿色、橙色、黄色、苔藓绿（含浅色与深色组合）
- 主要交互颜色为蓝色 450（`#5b76fe`）
- 表示成功状态的绿色为 `#00b473`
- 边角圆角半径较大，范围在 8px 至 50px 之间
- 基于 Framer 构建，具有流畅的动态效果
- 边框采用环形阴影效果：`rgb(224,226,232) 0px 0px 0px 1px`

## 2. 色彩方案与用途

### 主要颜色
- **接近黑色**（`#1c1c1e`）：正文文字颜色
- **白色**（`#ffffff`）：`--tw-color-white`，主要背景色
- **蓝色 450**（`#5b76fe`）：`--tw-color-blue-450`，主要交互元素颜色
- **按下状态颜色**（`#2a41b6`）：`--tw-color-actionable-pressed`

### 柔和彩色点缀色（浅色/深色组合）
- **珊瑚色**：浅色 `#ffc6c6` / 深色 `#600000`
- **玫瑰色**：浅色 `#ffd8f4` / 深色（未明确指定）
- **青绿色**：浅色 `#c3faf5` / 深色 `#187574`
- **橙色**：浅色 `#ffe6cd`
- **黄色**：深色 `#746019`
- **苔藓绿**：深色 `#187574`
- **粉色**（`#fde0f0`）：柔和的粉色背景
- **红色**（`#fbd4d4`）：浅红色背景
- **深红色**（`#e3c5c5**）：暗淡的红色

### 语义颜色
- **成功状态**（`#00b473`）：`--tw-color-success-accent`

### 中性颜色
- **石板灰**（`#555a6a`）：次要文字颜色
- **输入占位符色**（`#a5a8b5`）：`--tw-color-input-placeholder`
- **边框色**（`#c7cad5`）：按钮边框颜色
- **环形阴影色**（`rgb(224,226,232)`）：用作阴影的边界颜色

## 3. 字体规则

### 字体家族
- **显示字体**：`Roobert PRO Medium`，备选为占位符字体 — `"blwf", "cv03", "cv04", "cv09", "cv11"`
- **显示字体变体**：`Roobert PRO SemiBold`、`Roobert PRO SemiBold Italic`、`Roobert PRO`
- **正文字体**：`Noto Sans` — `"liga" 0, "ss01", "ss04", "ss05"`

### 字体层级

| 角色 | 字体 | 字号 | 字重 | 行高 | 字距 |
|------|------|------|------|-------|------|
| 主标题 | Roobert PRO Medium | 56px | 400 | 1.15 | -1.68px |
| 区块标题 | Roobert PRO Medium | 48px | 400 | 1.15 | -1.44px |
| 卡片标题 | Roobert PRO Medium | 24px | 400 | 1.15 | -0.72px |
| 子标题 | Noto Sans | 22px | 400 | 1.35 | -0.44px |
| 功能描述 | Roobert PRO Medium | 18px | 600 | 1.35 | 正常 |
| 正文内容 | Noto Sans | 18px | 400 | 1.45 | 正常 |
| 标准正文 | Noto Sans | 16px | 400–600 | 1.50 | -0.16px |
| 按钮文字 | Roobert PRO Medium | 17.5px | 700 | 1.29 | 0.175px |
| 图注文字 | Roobert PRO Medium | 14px | 400 | 1.71 | 正常 |
| 小号文字 | Roobert PRO Medium | 12px | 400 | 1.15 | -0.36px |
| 微型大写文字 | Roobert PRO | 10.5px | 400 | 0.90 | 大写 |

## 4. 组件样式

### 按钮
- **虚线按钮**：透明背景，`1px solid #c7cad5` 的边框，圆角 8px，内边距 7px × 12px
- **白色圆形按钮**：圆角为 50%，白色背景并带有阴影
- **蓝色主按钮**：颜色与主要交互色一致

### 卡片：圆角为 12px–24px，背景为柔和色调
### 输入框：白色背景，`1px solid #e9eaef` 的边框，圆角 8px，内边距 16px

## 5. 布局原则
- **间距**：基础间距比例为 1–24px
- **圆角半径**：按钮为 8px，卡片为 10px–12px，面板为 20px–24px，大型容器为 40px–50px
- **环形阴影**：`rgb(224,226,232) 0px 0px 0px 1px`

## 6. 深度与立体感
设计上尽量保持简洁——仅通过环形阴影与柔和背景色的对比来营造层次感。

## 7. 正确做法与禁忌
### 正确做法
- 在功能板块中使用柔和色调的浅色与深色组合
- 使用带有 OpenType 字符变体的 Roobert PRO 字体
- 为交互元素选用蓝色 450（`#5b76fe`）颜色

### 禁忌事项
- 避免使用过重的阴影效果
- 每个板块中使用的柔和彩色点缀色不宜超过 2 种

## 8. 响应式设计
断点设置：425px、576px、768px、896px、1024px、1200px、1280px、1366px、1700px、1920px

## 9. Agent 提示词指南
### 快速颜色参考
- 文字颜色：接近黑色（`#1c1c1e`）
- 背景颜色：白色（`#ffffff`）
- 交互元素颜色：蓝色 450（`#5b76fe`）
- 成功状态颜色：`#00b473`
- 边框颜色：`#c7cad5`
### 组件提示词示例
- “创建主标题区域：白色背景。使用 Roobert PRO Medium 字体，字号 56px，行高 1.15，字距 -1.68px。添加蓝色行动按钮（`#5b76fe`）。再添加一个虚线风格的次要按钮（边框为 `1px solid #c7cad5`，圆角 8px）。”
