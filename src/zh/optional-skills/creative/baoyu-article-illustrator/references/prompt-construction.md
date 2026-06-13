# 提示词构建

## 提示词文件格式

每个提示词文件均由 YAML 前置内容与实际内容组成：

```yaml
---
illustration_id: 01
type: infographic
style: blueprint
references:                    # ⚠️ ONLY if files EXIST in references/ directory
  - ref_id: 01
    filename: 01-ref-diagram.png
    usage: direct              # direct | style | palette
---

[Type-specific template content below...]
```

**⚠️ 重要提示——何时需要添加 `references` 字段**：

| 情况 | 操作建议 |
|-----------|----------|
| 参考文件已保存在 `references/` 目录中 | 需将其包含在 frontmatter 中 ✓ |
| 风格为口头描述且无对应文件 | 不要放入 frontmatter，而应直接添加到提示词正文中 |
| frontmatter 中虽写了文件路径，但该文件实际不存在 | 会引发错误——请删除 `references` 字段 |

**参考文件的使用方式**（仅当文件存在时适用）：

| 使用类型 | 描述 | 生成操作 |
|---------|------|----------|
| `direct` | 主要视觉参考 | 在提示词文本中描述该参考内容（构图、主体、风格、色调等）——`image_generate` 功能不支持直接传入参考图片 |
| `style` | 仅限风格特征 | 在提示词文本中描述风格特点 |
| `palette` | 色调板提取 | 将相关颜色直接写入提示词中 |

**若没有参考文件，但风格/色调为口头描述**，则直接将其添加到提示词正文中：
```
COLORS (from reference):
- Primary: #E8756D coral
- Secondary: #7ECFC0 mint
...

STYLE (from reference):
- Clean lines, minimal shadows
- Gradient backgrounds
...
```

## 默认构图要求

**默认适用于所有提示词**：

| 要求 | 说明 |
|------|------|
| **简洁的构图** | 布局简单，避免视觉杂乱 |
| **充足留白** | 元素之间保留足够的间距 |
| **无复杂背景** | 仅可使用纯色或柔和渐变，避免复杂的纹理 |
| **居中或符合内容需求** | 主要视觉元素需居中，或根据内容需求进行定位 |
| **风格统一的图形元素** | 使用与内容主题相匹配的图形元素 |
| **突出核心信息** | 通过留白引导注意力至关键信息 |

**需添加到所有提示词中**：
> 构图简洁，留白充足。背景可简单或无背景。主要元素需居中，或根据内容需求进行定位。

---

## 颜色规范规则

提示词中的颜色代码仅用于**渲染指导**——它们仅告知模型应使用何种颜色，而非指定要显示的文本内容。

**⚠️ 重要提示**：图像生成模型有时会将颜色名称和十六进制值以可见文本标签的形式呈现在图像中（例如将“马卡龙蓝 #A8D8EA”直接标注出来）。必须避免这种情况发生。

**对于包含“颜色”部分的提示词，需添加以下内容**：
> 颜色值（#hex）及颜色名称仅用于渲染指导——请勿在图像中以可见文本的形式显示颜色名称、十六进制代码或调色板标签。

---

## 人物形象的呈现方式

在描绘人物时：

| 指导原则 | 说明 |
|----------|------|
| **风格** | 采用简化的卡通轮廓或象征性表达 |
| **避免** | 真实感强的人物刻画及细节丰富的面部特征 |
| **多样性** | 若描绘多个人物，需体现不同的体型特征 |
| **情感表达** | 通过姿势和简单的手势来传达情感 |

**对于包含人物形象的提示词，需添加以下内容**：
> 人物形象：采用简化的风格化轮廓或象征性表现形式，而非写实风格。

---

## 插图中的文字

| 元素 | 指导原则 |
|------|----------|
| **大小** | 字体要足够大且醒目，便于立即识别 |
| **风格** | 为体现温馨感，建议使用手写体字体 |
| **内容** | 仅包含简短的关键词和核心概念 |
| **语言** | 与文章语言保持一致 |

**对于包含文字的提示词，需添加以下内容**：
> 文字应足够大且醒目，采用手写体风格。内容力求简洁，重点突出关键词。

---

## 优秀提示词应遵循的原则

一个好的提示词必须包含以下要素：

1. **先明确布局结构**：描述整体构图、分区以及内容流动方向
2. **具体的数据或标签**：使用实际数字及文章中的相关术语
3. **视觉元素间的关联**：说明各元素之间的联系
4. **语义化颜色运用**：根据含义选择颜色（如红色代表警告，绿色代表高效）
5. **风格特征描述**：包括线条处理方式、纹理以及整体氛围
6. **分辨率比例**：在提示词末尾注明图像比例及复杂程度

## 各类型内容的模板示例

### 信息图

```
[Title] - Data Visualization

Layout: [grid/radial/hierarchical]

ZONES:
- Zone 1: [data point with specific values]
- Zone 2: [comparison with metrics]
- Zone 3: [summary/conclusion]

LABELS: [specific numbers, percentages, terms from article]
COLORS: [semantic color mapping]
STYLE: [style characteristics]
ASPECT: 16:9
```

**信息图 + 向量插画**：
```
Flat vector illustration infographic. Clean black outlines on all elements.
COLORS: Cream background (#F5F0E6), Coral Red (#E07A5F), Mint Green (#81B29A), Mustard Yellow (#F2CC8F)
ELEMENTS: Geometric simplified icons, no gradients, playful decorative elements (dots, stars)
```

**信息图 + 向量插画 + 温暖色调**：
```
Flat vector illustration infographic. Clean black outlines on all elements.
PALETTE OVERRIDE (warm): Warm-only color palette, no cool colors.
COLORS: Soft Peach background (#FFECD2), Warm Orange (#ED8936),
        Terracotta (#C05621), Golden Yellow (#F6AD55), Deep Brown (#744210)
ELEMENTS: Geometric simplified icons, no gradients, rounded corners,
          modular card layout, consistent icon style
```

### 场景

```
[Title] - Atmospheric Scene

FOCAL POINT: [main subject]
ATMOSPHERE: [lighting, mood, environment]
MOOD: [emotion to convey]
COLOR TEMPERATURE: [warm/cool/neutral]
STYLE: [style characteristics]
ASPECT: 16:9
```

### 流程图

```
[Title] - Process Flow

Layout: [left-right/top-down/circular]

STEPS:
1. [Step name] - [brief description]
2. [Step name] - [brief description]
...

CONNECTIONS: [arrow types, decision points]
STYLE: [style characteristics]
ASPECT: 16:9
```

**流程图 + 向量插图**：
```
Flat vector flowchart with bold arrows and geometric step containers.
COLORS: Cream background (#F5F0E6), steps in Coral/Mint/Mustard, black outlines
ELEMENTS: Rounded rectangles, thick arrows, simple icons per step
```

**流程图 + 思路草图 + 马卡龙色板**：
```
Hand-drawn educational flowchart on warm cream paper. Slight wobble on all lines.
PALETTE: macaron — soft pastel color blocks
COLORS: Warm Cream background (#F5F0E8), zone fills in Macaron Blue (#A8D8EA),
        Lavender (#D5C6E0), Mint (#B5E5CF), Coral Red (#E8655A) for emphasis
ELEMENTS: Rounded cards with dashed/solid borders, wavy hand-drawn arrows with labels,
          simple stick-figure characters, doodle decorations (stars, underlines)
STYLE: Color fills don't completely fill outlines, hand-drawn lettering, generous white space
```

**流程图 + 手写笔记 + 单色墨水调色板**：
```
Professional hand-drawn visual-note flowchart on pure white. Black ink line work
with slight wobble, à la Mike Rohde sketchnoting.
PALETTE: mono-ink — black ink dominant, sparse semantic accents
COLORS: Pure White background (#FFFFFF), Near Black (#1A1A1A) for all lines,
        text, and figures; Coral Red (#E8655A) only for risk/emphasis,
        Muted Teal (#5FA8A8) only for positive/solution states
ELEMENTS: Left-to-right stage boxes with rounded-rect frames, wavy hand-drawn
          arrows between stages, simple stick-figure characters with role
          labels above (e.g., "ML Engineer", "Team Lead"), dashed-border box
          for future/empty stage, small doodle icons per stage
STYLE: Hand-lettered titles (bold, oversized), handwritten stage labels and
        annotations, generous white space, bottom tagline summarizing takeaway
```

### 对比分析

```
[Title] - Comparison View

LEFT SIDE - [Option A]:
- [Point 1]
- [Point 2]

RIGHT SIDE - [Option B]:
- [Point 1]
- [Point 2]

DIVIDER: [visual separator]
STYLE: [style characteristics]
ASPECT: 16:9
```

**对比分析 + 向量插图**：
```
Flat vector comparison with split layout. Clear visual separation.
COLORS: Left side Coral (#E07A5F), Right side Mint (#81B29A), cream background
ELEMENTS: Bold icons, black outlines, centered divider line
```

**对比风格 + 向量插画 + 温暖色调**：
```
Flat vector comparison with split layout. Clear visual separation.
PALETTE OVERRIDE (warm): Warm-only color palette, no cool colors.
COLORS: Left side Warm Orange (#ED8936), Right side Terracotta (#C05621),
        Soft Peach background (#FFECD2), Deep Brown (#744210) accents
ELEMENTS: Bold icons, black outlines, centered divider line
```

**对比功能 + 手写备注 + 单色墨水调色板**（前后对比、传统模式与新模式）：
```
Professional hand-drawn sketchnote comparison on pure white. Black ink line work
with slight wobble, à la Mike Rohde sketchnoting.
PALETTE: mono-ink — black ink dominant, sparse semantic accents
COLORS: Pure White background (#FFFFFF), Near Black (#1A1A1A) for all outlines,
        text, figures, arrows; Coral Red (#E8655A) reserved for risks/gaps
        (left/Before side); Muted Teal (#5FA8A8) reserved for positives
        (right/After side). Color accents under 10% of canvas.
LAYOUT: Left | Right split with vertical hand-drawn divider. Hand-lettered
        "Before" label (top-left) and "After" label (top-right).
LEFT SIDE: Stick figure(s) with role label above, speech bubble showing the
           pain point, bulleted pain-point list in handwritten text.
RIGHT SIDE: Stick figure(s) showing the new state, bulleted improvement list,
            small positive-action icons.
BRIDGE: Curved hand-drawn "mindset shift" arrow bridging left → right with
        small inline label describing the shift.
BOTTOM: Single-line hand-lettered tagline summarizing the takeaway.
STYLE: Hand-lettered headings (bold, oversized), handwritten body annotations,
        generous white space, no computer fonts, no gradients, no shadows.
```

### 框架

```
[Title] - Conceptual Framework

STRUCTURE: [hierarchical/network/matrix]

NODES:
- [Concept 1] - [role]
- [Concept 2] - [role]

RELATIONSHIPS: [how nodes connect]
STYLE: [style characteristics]
ASPECT: 16:9
```

**框架 + 向量插画**：
```
Flat vector framework diagram with geometric nodes and bold connectors.
COLORS: Cream background (#F5F0E6), nodes in Coral/Mint/Mustard/Blue, black outlines
ELEMENTS: Rounded rectangles or circles for nodes, thick connecting lines
```

**框架设计 + 向量插画 + 温暖色调**：
```
Flat vector framework diagram with geometric nodes and bold connectors.
PALETTE OVERRIDE (warm): Warm-only color palette, no cool colors.
COLORS: Soft Peach background (#FFECD2), nodes in Warm Orange (#ED8936),
        Terracotta (#C05621), Golden Yellow (#F6AD55), black outlines
ELEMENTS: Rounded rectangles or circles for nodes, thick connecting lines
```

**框架 + 笔记功能 + 单色墨水调色板**（指挥中心，类操作系统概念）：
```
Professional hand-drawn sketchnote framework on pure white. Black ink line work
with slight wobble, à la Mike Rohde sketchnoting.
PALETTE: mono-ink — black ink dominant, sparse semantic accents
COLORS: Pure White background (#FFFFFF), Near Black (#1A1A1A) for all lines,
        text, figures; Dusty Lavender (#9B8AB5) for neutral category tags only;
        Coral Red (#E8655A) for emphasis sparingly. Color accents under 10%.
STRUCTURE: Central rounded-rectangle frame as "the system" with hand-lettered
           title inside. Inner layer of labeled sub-components (node labels
           above each). Outer layer of feeder arrows from stick-figure
           operators/users with role labels.
ELEMENTS: Stick figures at the edges with role tags ("Team Lead", "Operator"),
          wavy hand-drawn connector arrows with small inline labels, small
          doodle icons per component, dashed-border placeholder(s) for
          future/empty capabilities.
BOTTOM: Single-line hand-lettered tagline.
STYLE: Hand-lettered headings, handwritten annotations, generous white space,
        no computer fonts, no gradients.
```

### 时间线

```
[Title] - Chronological View

DIRECTION: [horizontal/vertical]

EVENTS:
- [Date/Period 1]: [milestone]
- [Date/Period 2]: [milestone]

MARKERS: [visual indicators]
STYLE: [style characteristics]
ASPECT: 16:9
```

### 屏印风格覆盖设置

当设置为 `style: screen-print` 时，需用以下内容替换原有的标准样式指令：

```
Screen print / silkscreen poster art. Flat color blocks, NO gradients.
COLORS: 2-5 colors maximum. [Choose from style palette or duotone pair]
TEXTURE: Halftone dot patterns, slight color layer misregistration, paper grain
COMPOSITION: Bold silhouettes, geometric framing, negative space as storytelling element
FIGURES: Silhouettes only, no detailed faces, stencil-cut edges
TYPOGRAPHY: Bold condensed sans-serif integrated into composition (not overlaid)
```

**场景 + 印花图案**：
```
Conceptual poster scene. Single symbolic focal point, NOT literal illustration.
COLORS: Duotone pair (e.g., Burnt Orange #E8751A + Deep Teal #0A6E6E) on Off-Black #121212
COMPOSITION: Centered silhouette or geometric frame, 60%+ negative space
TEXTURE: Halftone dots, paper grain, slight print misregistration
```

**对比模式 + 屏幕打印**：
```
Split poster composition. Each side dominated by one color from duotone pair.
LEFT: [Color A] side with silhouette/icon for [Option A]
RIGHT: [Color B] side with silhouette/icon for [Option B]
DIVIDER: Geometric shape or negative space boundary
TEXTURE: Halftone transitions between sides
```

## 调色板覆盖功能

当指定了调色板（通过 `--palette` 参数或预设值）时，它将覆盖该风格的默认颜色设置：

1. 读取风格文件 → 获取渲染规则（视觉元素、风格规则、线条处理方式）
2. 读取调色板文件（`palettes/<palette>.md`）→ 获取颜色与背景颜色
3. 调色板中的颜色会**替换**提示词中风格的默认颜色方案
4. 调色板中的背景颜色会**替换**风格的背景色（同时保留风格的纹理描述）
5. 组合生成提示词：风格渲染指令 + 调色板颜色

若指定了调色板，**提示词的前置信息**中也会包含该调色板的相关内容：
```yaml
---
illustration_id: 01
type: infographic
style: vector-illustration
palette: macaron
---
```

**示例**：`vector-illustration` + `macaron` 色板：
```
Flat vector illustration infographic. Clean black outlines on all elements.
PALETTE: macaron — soft pastel color blocks
COLORS: Warm Cream background (#F5F0E8), Macaron Blue (#A8D8EA), Mint (#B5E5CF),
        Lavender (#D5C6E0), Peach (#FFD5C2), Coral Red (#E8655A) for emphasis
ELEMENTS: Geometric simplified icons, no gradients, playful decorative elements
```

当未指定调色板时，将如以往一样使用该样式内置的色彩调色板。

```
Include a subtle watermark "[content]" positioned at [position].
```
