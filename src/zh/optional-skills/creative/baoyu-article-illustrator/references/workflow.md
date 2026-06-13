# 详细工作流程说明

## 第一步：检测参考图片

如果用户提供了参考图片（本地路径或网址），目标是为这些图片生成可用于提示词中的**文本描述**——`image_generate`功能不支持接收参考图片，而Hermes的文本文件工具也无法读取或写入二进制文件。

**工具使用规则**：

| 任务 | 工具 | 备注 |
|------|------|------|
| 分析参考图片 | `vision_analyze` | 支持接受网址或本地路径。需询问图片的风格、色彩搭配、构图及主体内容。 |
| 编写文本描述 | `write_file` | 仅可用于生成侧边车`.md`文件——切勿尝试用该工具写入PNG/JPG格式的文件。 |
| （可选）保留二进制文件的本地副本 | `terminal` | 可使用命令`cp "$src" "{output-dir}/references/NN-ref-{slug}.{ext}"`进行复制——仅用于记录，实际技能功能并不读取该二进制文件。 |

| 输入类型 | 操作步骤 |
|----------|----------|
| 提供了图片文件路径 | 先调用`vision_analyze`分析，再生成侧边车`.md`文件；如需记录，可可选地使用`terminal cp`命令保存本地副本。 |
| 提供了图片网址 | 直接将网址传递给`vision_analyze`进行分析，随后生成侧边车`.md`文件。 |
| 对话中已提供图片（无路径也无网址） | 使用`clarify`工具询问用户的图片路径或网址，或要求用户用文字描述图片内容。 |
| 用户无法提供任何信息 | 通过口头交流从用户处获取风格和色彩信息，随后生成`references/extracted-style.md`文件。请勿在提示词的前置字段中添加`references:`标签。 |

**具体操作流程**（当有路径或网址可用时）：

1. 调用`vision_analyze(image_url=..., question="请描述图片的风格、色彩搭配（需提供十六进制近似值）、构图及主体内容，以便将其作为其他插画的风格/色彩参考。")`。
2. 使用`write_file`工具将描述内容写入 `{output-dir}/references/NN-ref-{slug}.md` 文件中。
3. （可选）使用`terminal`工具配合`cp`命令（或针对网址使用`curl -sSL -o ...`命令）来保留图片的本地二进制副本。该步骤并非技能功能所必需。
4. 在大纲中将该参考资料标记为`direct`/`style`/`palette`类型。在5.1步骤中，该描述内容将被添加到提示词的正文部分。

**侧边车文件格式**：
```yaml
---
ref_id: NN
source: "<original path or URL>"
local_copy: "NN-ref-{slug}.png"   # omit if no copy made
usage_hint: style                 # direct | style | palette
---
[vision_analyze description — colors, style, composition, subject]
```

## 第2步：分析

### 2.1 确定输出目录

| 输入内容 | 输出目录 | 来源文件保存路径 |
|---------|----------|----------------|
| 文章文件路径 | `{article-dir}/imgs/`（默认值） | —（通过 `read_file` 读取文章） |
| 粘贴的内容 | `illustrations/{topic-slug}/`（当前工作目录） | `source-{slug}.{ext}`（通过 `write_file` 保存） |

如果用户明确要求不同的结构（例如将图片放在文章文件夹中，或使用 `illustrations/` 子目录），则应遵从其要求。

### 2.2 分析内容

| 分析维度 | 描述 |
|---------|------|
| 内容类型 | 技术类 / 教程类 / 方法论类 / 叙事类 |
| 图片的用途 | 传递信息 / 可视化展示 / 激发想象 |
| 核心论点 | 需要通过可视化呈现的2-5个主要观点 |
| 适合添加图片的位置 | 图片能提升价值的段落位置 |
| 推荐的图片类型 | 根据内容特征与用途确定 |
| 推荐的图片密度 | 根据文章长度与复杂度决定 |

使用 `write_file` 将分析结果保存至 `{output-dir}/analysis.md` 文件中。

### 2.3 提取核心论点

- 主要论题
- 读者需要了解的关键概念
- 对比与差异点
- 提出的框架或模型

**重要提示**：如果文章使用了比喻（例如“用电锯切西瓜”），切勿按字面意思绘制图片，而应可视化其背后的**核心概念**。

### 2.4 确定需配图的位置

**需要配图的情况**：
- 核心论点（必须）
- 抽象概念
- 数据对比
- 流程或工作流程

**无需配图的情况**：
- 比喻的字面含义
- 装饰性场景
- 通用型插图

### 2.5 规划参考图片的使用方式（若已在第1步完成分析）

针对每张参考图片（使用第1步中的 `vision_analyze` 分析结果）：

| 分析维度 | 描述 |
|---------|------|
| 视觉特征 | 风格、颜色、构图 |
| 内容/主题 | 参考图片所描绘的内容 |
| 适用位置 | 哪些部分与参考图片匹配 |
| 风格匹配度 | 哪种插图类型或风格与之契合 |
| 使用建议 | `direct` / `style` / `palette` |

| 使用方式 | 适用场景 | 在第5.1步中的应用方式 |
|---------|----------|------------------------|
| `direct` | 参考图片与期望输出高度匹配 | 将描述内容（包括构图、主题、风格和色彩方案）直接加入提示词中 |
| `style` | 仅提取视觉风格特征 | 将提取的风格特点添加到提示词中 |
| `palette` | 仅提取色彩方案 | 将提取的十六进制颜色值添加到提示词中 |

注意：无论采用哪种使用方式，`image_generate` 都不接受直接输入参考图片，所有相关内容均需通过 `vision_analyze` 的分析结果来传递。

---

## 第3步：确认设置

使用 `clarify` 工具进行确认。由于该工具一次仅能处理一个问题，因此请先询问最关键的问题。对于用户已在请求中回答过的问题则可直接跳过。

### 问题1：预设方案还是自定义类型（优先级最高）

根据第2步的内容分析结果，首先推荐一个预设方案（同时确定类型与风格）。可参考 [style-presets.md](style-presets.md) 中的“内容类型 → 预设方案推荐”表格。

- [推荐的预设方案] — [简述：类型、风格及推荐理由]
- [备选预设方案] — [简述]
- 或手动选择类型：信息图 / 场景图 / 流程图 / 对比图 / 框架图 / 时间轴图 / 混合型

**如果用户选择了预设方案 → 跳过问题3**（类型与风格均已确定）。
**如果用户选择了自定义类型 → 需要回答问题3。**

### 问题2：图片密度

- **极简型（1-2张）** — 仅包含核心概念
- **均衡型（3-5张）** — 覆盖主要章节
- **每章一张** — 每个章节/部分至少配1张图（推荐）
- **丰富型（6张以上）** — 全面覆盖内容

### 问题3：风格选择（若已在问题1中选择了预设方案则跳过）

首先展示核心风格选项：

- [最佳匹配的核心风格]（推荐）
- [其他兼容的核心风格1]
- [其他兼容的核心风格2]
- 其他风格（可查看完整的风格库）

**核心风格**（简化版选择）：

| 核心风格 | 对应类型 | 最适合的场景 |
|----------|---------|--------------|
| `minimal-flat` | notion | 通用内容、知识分享、SaaS相关主题 |
| `sci-fi` | blueprint | AI、前沿技术、系统设计相关内容 |
| `hand-drawn` | sketch/warm | 轻松、反思性、休闲风格的内容 |
| `editorial` | editorial | 流程说明、数据展示、新闻报道类内容 |
| `scene` | warm/watercolor | 叙事类、情感表达、生活方式相关内容 |
| `poster` | screen-print | 观点阐述、社论、文化主题、电影相关内容 |

风格选择依据为类型与风格的兼容性矩阵（详见 [styles.md](styles.md)）。**在第5步**中，可阅读 `styles/<style>.md` 文件了解该风格的视觉元素及渲染规则。

### 问题4：色彩方案（可选）

如果预设方案未指定色彩方案，可提供以下选项：

- **默认方案**（使用该风格内置的色彩）（推荐）
- `macaron` — 暖米色背景搭配柔和的粉彩色块
- `warm` — 暖色调，不含冷色
- `neon` — 深色背景上搭配鲜艳的霓虹色

**以下情况可跳过此步骤**：预设方案已指定色彩方案，或用户已在请求中明确指定了色彩方案。

详情可查看 [styles.md](styles.md#palette-gallery) 中的色彩方案库，以及 `palettes/<palette>.md` 文件中的完整规格说明。

### 问题5：图片中的文字语言（仅在存在歧义时询问）

如果文章的语言与用户的对话语言不同，请询问应使用哪种语言：
- 文章原文语言（与文章内容保持一致）（推荐）
- 用户的对话语言

**以下情况可跳过此步骤**：两种语言相同，或用户已在请求中明确指定。

### 显示参考图片的使用情况（若已在第1步保存了参考图片）

在向用户展示大纲预览时，同时显示各部分对应的参考图片分配情况。

```
Reference Images:
| Ref | Filename | Recommended Usage |
|-----|----------|-------------------|
| 01 | 01-ref-diagram.png | direct → Illustration 1, 3 |
| 02 | 02-ref-chart.png | palette → Illustration 2 |
```

## 第 4 步：生成大纲

使用 `write_file` 函数将结果保存为 `{output-dir}/outline.md` 文件：

```yaml
---
type: infographic
density: balanced
style: blueprint
image_count: 4
references:                    # Only if references provided
  - ref_id: 01
    filename: 01-ref-diagram.png
    description: "Technical diagram showing system architecture"
  - ref_id: 02
    filename: 02-ref-chart.png
    description: "Color chart with brand palette"
---

## Illustration 1

**Position**: [section] / [paragraph]
**Purpose**: [why this helps]
**Visual Content**: [what to show]
**Type Application**: [how type applies]
**References**: [01]                    # Optional: list ref_ids used
**Reference Usage**: direct             # direct | style | palette
**Filename**: 01-infographic-concept-name.png

## Illustration 2
...
```

**备份规则**：如果存在 `outline.md` 文件，在进行写入之前需将其重命名为 `outline-backup-YYYYMMDD-HHMMSS.md`。

**要求**：
- 每个位置的选择都需有内容上的依据
- 类型应用需保持一致
- 描述中需体现相应风格
- 需统计匹配的密度
- 参考文献的分配需基于第 2.5 步的分析结果

---

## 第 5 步：生成提示词

**强制要求**：在生成任何图像之前，每幅插图都必须先拥有对应的提示词文件。

针对大纲中的每一幅插图：

1. **创建提示词文件**：通过 `write_file` 函数在 `{output-dir}/prompts/NN-{type}-{slug}.md` 路径下生成该文件
2. **添加 YAML 前置信息**：
   ```yaml
   ---
   illustration_id: 01
   type: infographic
   style: custom-flat-vector
   ---
   ```
3. **加载样式规范**：通过 `read_file` 功能读取 `styles/<style>.md` 文件，获取视觉元素、样式规则及渲染指令。  
4. **加载调色板规范**（如指定了调色板）：读取 `palettes/<palette>.md` 文件以获取颜色和背景信息。调色板中的颜色将**替换**该样式默认的配色方案；若未指定调色板，则使用该样式内置的颜色。  
5. **遵循 [prompt-construction.md](prompt-construction.md) 中针对不同类型的模板**，结合样式定义的渲染效果及调色板中的颜色（或样式默认颜色）来生成内容。  
6. **提示词质量要求**（均为必填项）：  
   - `Layout`：描述整体布局结构（网格式/放射式/层级式/左右布局/上下布局）。  
   - `ZONES`：需明确描述每个视觉区域的内容，避免模糊表述。  
   - `LABELS`：必须使用**文章中的实际数字、术语、数据或引文**，严禁使用通用占位符。  
   - `COLORS`：需指定调色板中的十六进制颜色代码（或样式默认颜色），并说明其语义含义。  
   - `STYLE`：根据样式规则描述线条处理方式、纹理效果、整体氛围及字符渲染风格。  
   - `ASPECT`：指定宽高比，例如 `16:9`。  
7. **应用默认设置**：包括布局要求、字符渲染规则及文本格式规范。  
8. **备份规则**：若存在提示词文件，需将其重命名为 `prompts/NN-{type}-{slug}-backup-YYYYMMDD-HHMMSS.md`。

**重要提示——前置数据中的引用处理**：  
- 仅当 `{output-dir}/references/` 目录下存在对应的侧边栏 `.md` 描述文件时，才添加 `references` 字段。  
- 若样式或调色板是通过口头描述确定的（无对应描述文件），则仅可将相关信息添加到提示词的正文部分。  
- 在编写前置数据之前，务必确认侧边栏文件是否存在（可通过对 `.md` 文件执行 `read_file` 操作进行验证）。

### 5.1 处理引用信息（若在第一步中已进行分析）

通过 `read_file` 功能读取侧边栏文件 `references/NN-ref-{slug}.md` 中的 `vision_analyze` 描述内容，并将其嵌入到提示词的正文部分。`image_generate` 函数不会接收二进制数据。

| 使用方式 | 操作内容 |
|---------|----------|
| `direct` | 将完整的引用描述内容（包括布局、主题、风格、调色板等信息）直接粘贴到提示词正文中。 |
| `style` | 仅列出风格特征，例如：“风格：简洁的线条、渐变背景……” |
| `palette` | 仅列出十六进制颜色代码，例如：“颜色：#E8756D 珊瑚色、#7ECFC0 薄荷绿……” |

---

## 第6步：生成图像

`image_generate` 函数会返回一个包含 URL 的 JSON 数据块（格式为 `{"success": true, "image": "<url>"}`）。该函数不会保存本地文件，也不接受输出路径参数，同时不允许智能体选择后端或模型。应将该 URL 视为临时生成的图像文件，需手动下载。

针对每个提示词文件，请执行以下操作：  
1. 通过 `read_file` 功能读取提示词文件，提取出完整的提示词内容。  
2. 将提示词中的 `ASPECT` 值映射到 `image_generate` 函数支持的枚举值：`16:9` 对应 `landscape`（横屏），`9:16` 对应 `portrait`（竖屏），`1:1` 对应 `square`（正方形）；对于其他自定义宽高比，则选择最接近的预设比例。  
3. 调用 `image_generate(prompt=<assembled>, aspect_ratio=<enum>)` 函数，从返回的 JSON 数据中提取图像的 URL。  
4. **备份规则**：若 `{output-dir}/NN-{type}-{slug}.png` 文件已存在，则在写入新文件之前，通过 `terminal` 命令将其重命名为 `"{output-dir}/NN-{type}-{slug}-backup-YYYYMMDD-HHMMSS.png"`。  
5. 使用 `terminal` 命令下载该图像文件。
   ```bash
   curl -sSL -o "{output-dir}/NN-{type}-{slug}.png" "{image_url}"
   ```
如果无法使用 `curl`，则改用命令 `wget -qO "{output-dir}/NN-{type}-{slug}.png" "{image_url}"`。

6. 确认文件存在且大小非零（终端中执行：`test -s "{path}" && echo ok`）。

7. 若图像生成失败，重新调用 `image_generate` 一次；若下载失败，则增加超时时间后再次尝试使用 `curl`。之后记录错误并继续执行后续操作。

8. 每次生成完成后，输出“已生成 X/N 张图像”。

---

## 第 7 步：完成处理

### 7.1 更新文章

在对应段落后插入图片，路径需相对于文章文件所在位置：

| 输入内容 | 插入路径 |
|---------|----------|
| 文章文件路径（默认为 `imgs-subdir`） | `![描述文字](imgs/NN-{type}-{slug}.png)` |
| 文章文件路径（图片与正文并列显示） | `![描述文字](NN-{type}-{slug}.png)` |
| 文章文件路径（位于 `illustrations/` 子目录中） | `![描述文字](illustrations/NN-{type}-{slug}.png)` |
| 粘贴的内容 | `![描述文字](illustrations/{topic-slug}/NN-{type}-{slug}.png)`（相对于当前工作目录） |

替代文本：用文章所在语言书写的简短描述。

### 7.2 输出总结

```
Article Illustration Complete!

Article: [path]
Type: [type] | Density: [level] | Style: [style]
Location: [directory]
Images: X/N generated

Positions:
- 01-xxx.png → After "[Section]"
- 02-yyy.png → After "[Section]"

[If failures]
Failed:
- NN-zzz.png: [reason]
```
