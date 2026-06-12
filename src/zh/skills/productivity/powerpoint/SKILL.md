---
name: powerpoint
description: "Create, read, edit .pptx decks, slides, notes, templates."
license: Proprietary. LICENSE.txt has complete terms
platforms: [linux, macos, windows]
---

# PowerPoint技能

## 适用场景

只要涉及.pptx文件，无论作为输入、输出还是两者兼有，均可使用此技能。应用场景包括：创建幻灯片集、演示文稿或汇报材料；从任何.pptx文件中读取、解析或提取文本（即便这些提取出的内容会被用于其他地方，比如邮件或总结中）；编辑、修改或更新现有演示文稿；合并或拆分幻灯片文件；处理模板、布局、演讲者备注或评论。只要用户提到“幻灯片集”“幻灯片”“演示文稿”，或提及.pptx文件名，即可触发该技能，无需考虑其后续要对内容进行何种操作。若需要打开、创建或处理.pptx文件，均应使用此技能。

## 快速参考

| 任务 | 指引 |
|------|------|
| 读取/分析内容 | `python -m markitdown presentation.pptx` |
| 基于模板编辑或创建 | 阅读[editing.md](editing.md) |
| 从零开始创建 | 阅读[pptxgenjs.md](pptxgenjs.md) |

---

## 读取内容

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

## 编辑工作流程

**详情请参阅 [editing.md](editing.md)。**

1. 使用 `thumbnail.py` 分析模板
2. 解压 → 操作幻灯片 → 编辑内容 → 清理 → 打包

---

## 从零开始创建

**详情请参阅 [pptxgenjs.md](pptxgenjs.md)。**

在无法使用模板或参考演示文稿时使用此方法。

---

## 设计思路

**切勿制作乏味的幻灯片。** 纯白的背景配上简单的项目符号根本无法打动观众。为每张幻灯片参考以下建议中的创意。

### 开始之前

- **选择大胆且贴合主题的配色方案**：配色应专为当前主题设计。如果将这些颜色套用到完全不同的演示文稿中依然适用，说明你的选择还不够具体。
- **主次分明**：应有一种颜色占据主导地位（视觉占比60-70%），再搭配1-2种辅助色调以及1种醒目的强调色。切勿让所有颜色的权重相同。
- **明暗对比**：标题页和总结页可使用深色背景，内容页则用浅色背景（即“三明治”结构）。或者全程采用深色风格以营造高端感。
- **坚持统一的视觉元素**：选定一个独特的元素并贯穿所有幻灯片——如圆角图片框、彩色圆圈中的图标、厚实的单边边框等。

### 配色方案

选择与主题相匹配的颜色，不要默认使用普通的蓝色。以下配色方案可供参考：

| 主题 | 主色调 | 辅助色 | 强调色 |
|------|--------|--------|--------|
| **午夜商务风** | `1E2761`（深蓝） | `CADCFC`（冰蓝） | `FFFFFF`（白色） |
| **森林与苔藓风** | `2C5F2D`（森林绿） | `97BC62`（苔藓绿） | `F5F5F5`（奶油色） |
| **珊瑚活力风** | `F96167`（珊瑚红） | `F9E795`（金色） | `2F3C7E`（深蓝） |
| **温暖赤陶风** | `B85042`（赤陶色） | `E7E8D1`（沙色） | `A7BEAE`（鼠尾草绿） |
| **海洋渐变风** | `065A82`（深蓝） | `1C7293`（青绿色） | `21295C`（午夜蓝） |
| **炭灰极简风** | `36454F`（炭灰色） | `F2F2F2`（米白色） | `212121`（黑色） |
| **青绿信任风** | `028090`（青绿色） | `00A896`（海泡石蓝） | `02C39A`（薄荷绿） |
| **浆果与奶油风** | `6D2E46`（浆果红） | `A26769`（玫瑰粉） | `ECE2D0`（奶油色） |
| **鼠尾草宁静风** | `84B59F`（鼠尾草绿） | `69A297`（桉树绿） | `50808E`（板岩灰） |
| **樱桃醒目风** | `990011`（樱桃红） | `FCF6F5`（米白色） | `2F3C7E`（深蓝） |

### 每张幻灯片的设计要点

**每张幻灯片都需要视觉元素**——图片、图表、图标或形状。仅有文字的幻灯片极易被遗忘。

**布局选项：**
- 双栏布局（左侧为文字，右侧为插图）
- 图标+文字行布局（图标位于彩色圆圈中，上方为醒目标题，下方为描述文字）
- 2x2或2x3网格布局（一侧放置图片，另一侧排列内容块）
- 半透出图片（覆盖整个左侧或右侧），并在其上叠加文字内容

**数据展示方式：**
- 大型数据标注（数字大小为60-72磅，下方附有小标签）
- 对比列（前后对比、优缺点对比、并列选项对比）
- 时间轴或流程图（带编号的步骤及箭头）

**视觉优化技巧：**
- 在章节标题旁使用彩色小圆圈中的图标
- 用斜体标注关键数据或口号

### 字体选择

**挑选有趣且搭配协调的字体组合**——不要默认使用Arial。选择一个有特色的标题字体，并搭配简洁的正文字体。

| 标题字体 | 正文字体 |
|---------|---------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| 元素 | 字号大小 |
|---------|----------|
| 幻灯片标题 | 36-44磅，加粗 |
| 章节标题 | 20-24磅，加粗 |
| 正文内容 | 14-16磅 |
| 图注文字 | 10-12磅，浅色 |

### 空距设置

- 边距至少为0.5英寸
- 各内容块之间的间距为0.3-0.5英寸
- 保留适当空隙，无需填满每一寸空间

### 需避免的常见错误

- **不要重复相同的布局**——在不同幻灯片中变换列数、卡片样式和标注方式
- **不要将正文文字居中**——段落和列表应左对齐，仅标题可居中
- **不要忽视字号对比度**——标题字号需达到36磅以上，才能在14-16磅的正文背景下凸显出来
- **不要默认使用蓝色**——应选择能反映主题特色的颜色
- **不要随意混用空距大小**——选定0.3英寸或0.5英寸的间距并保持一致
- **不要只设计好一张幻灯片而其余的保持简单**——要么全面统一风格，要么全程保持简洁
- **不要制作仅有文字的幻灯片**——需添加图片、图标、图表等视觉元素，避免仅使用标题和项目符号
- **不要忘记文本框的内边距**——在将线条或形状与文本边缘对齐时，需为文本框设置`margin: 0`，或调整形状位置以考虑内边距的影响
- **不要使用对比度低的元素**——图标和文字都需要与背景形成强烈对比；避免在浅色背景上使用浅色文字，或在深色背景上使用深色文字
- **绝对不要在标题下方使用强调线**——这是AI生成幻灯片的典型特征；应改用空白区域或背景色替代

---

## 质量检查（必做）

**假设一定存在问题，你的任务就是找出它们。**

初次生成的版本几乎从来都不会完美。应将质量检查视为寻找缺陷的过程，而非简单的确认步骤。如果初次检查就未发现任何问题，说明你检查得还不够仔细。

### 内容质量检查

```bash
python -m markitdown output.pptx
```

检查是否存在内容缺失、拼写错误或顺序不当的问题。

**在使用模板时，还需确认是否还有残留的占位符文本：**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

如果 grep 返回了结果，在宣布任务成功之前必须先修复这些问题。

### 视觉质量检测

**⚠️ 请务必使用子智能体**——即便只有 2-3 张幻灯片也不例外。您长时间盯着代码查看，很容易看到自己期望看到的内容而非实际存在的状况。子智能体则能带来全新的视角。

首先将幻灯片转换为图像（详见[转换为图像](#converting-to-images)），然后再使用以下提示词：

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### 验证循环

1. 生成幻灯片 → 转换为图片 → 检查
2. **列出发现的问题**（若未发现问题，则需更仔细地重新检查）
3. 修复问题
4. **重新验证受影响的幻灯片**——通常一次修复会引发新的问题
5. 重复上述步骤，直到全部检查均未发现新问题为止

**在完成至少一个“修复-验证”循环之前，切勿宣布任务成功。**

---

## 转换为图片

将演示文稿转换为单个幻灯片图片，以便进行可视化检查：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

这将生成 `slide-01.jpg`、`slide-02.jpg` 等文件。

在修复问题后，如需重新渲染特定幻灯片：

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

## 依赖项

- `pip install "markitdown[pptx]"` —— 文本提取功能  
- `pip install Pillow` —— 缩略图网格生成  
- `npm install -g pptxgenjs` —— 从零开始创建演示文稿  
- LibreOffice（`soffice`）—— PDF格式转换（通过`scripts/office/soffice.py`自动配置，适用于沙箱环境）  
- Poppler（`pdftoppm`）—— PDF转换为图像文件
