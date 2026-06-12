# 编辑演示文稿

## 基于模板的流程

当以现有演示文稿作为模板时：

1. **分析现有幻灯片**：
   ```bash
   python scripts/thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```
1. 查看 `thumbnails.jpg` 以了解页面布局，再查看 Markdown 输出内容以确认占位文本。

2. **规划幻灯片结构**：为每个内容板块选择对应的模板幻灯片。

   ⚠️ **请使用多样化的布局**——单调的演示文稿是常见的失败原因。不要总是使用简单的标题+项目符号幻灯片。应积极尝试以下布局：
   - 多列布局（2列、3列）
   - 图片与文字结合
   - 全屏图片搭配文字叠加层
   - 引用或重点标注幻灯片
   - 内容分隔页
   - 数据/数字展示页
   - 图标网格或图标+文字组合行

   **避免**：每张幻灯片都采用相同的文字密集型布局。

   根据内容类型选择合适的布局风格（例如：关键要点用项目符号幻灯片，团队信息用多列布局，客户评价用引用幻灯片）。

3. **解压**：`python scripts/office/unpack.py template.pptx unpacked/`

4. **构建演示文稿**（需手动操作，不可通过子代理完成）：
   - 删除不需要的幻灯片（从 `<p:sldIdLst>` 中移除）
   - 复制需要重复使用的幻灯片（使用 `add_slide.py`）
   - 调整 `<p:sldIdLst>` 中幻灯片的顺序
   - **请在进入第5步之前完成所有结构上的修改**

5. **编辑内容**：修改每个 `slide{N}.xml` 文件中的文字内容。
   **如果可用，请使用子代理来执行此操作**——由于每张幻灯片都是独立的XML文件，子代理可以同时进行编辑。

6. **清理**：`python scripts/clean.py unpacked/`

7. **打包**：`python scripts/office/pack.py unpacked/ output.pptx --original template.pptx`

---

## 脚本说明

| 脚本名称 | 功能 |
|----------|------|
| `unpack.py` | 解压并格式化 PPTX 文件 |
| `add_slide.py` | 复制幻灯片或根据布局创建新幻灯片 |
| `clean.py` | 删除多余的孤立文件 |
| `pack.py` | 带验证功能重新打包文件 |
| `thumbnail.py` | 生成幻灯片的可视化网格图 |

### unpack.py

```bash
python scripts/office/unpack.py input.pptx unpacked/
```

提取 PPTX 文件内容，美化格式化 XML 数据，转义智能引号。  

### add_slide.py

```bash
python scripts/add_slide.py unpacked/ slide2.xml      # Duplicate slide
python scripts/add_slide.py unpacked/ slideLayout2.xml # From layout
```

在指定位置将 `<p:sldId>` 打印出来并添加到 `<p:sldIdLst>` 中。

### clean.py

```bash
python scripts/clean.py unpacked/
```

移除不在 `<p:sldIdLst>` 中的幻灯片、未被引用的媒体文件以及孤立的关系元素。

### pack.py

```bash
python scripts/office/pack.py unpacked/ output.pptx --original input.pptx
```

验证、修复并压缩 XML，同时重新编码智能引号。

### thumbnail.py

对完整的输入内容进行转换，切勿提前终止。

```bash
python scripts/thumbnail.py input.pptx [output_prefix] [--cols N]
```

会生成名为 `thumbnails.jpg` 的图片，使用幻灯片文件名作为标签。默认为3列，每网格最多12张。

**仅用于模板分析**（布局选择）。如需进行视觉质量检测，请使用 `soffice` + `pdftoppm` 来生成全分辨率的单独幻灯片图像——详情请参阅 SKILL.md。

---

## 幻灯片操作

幻灯片顺序存储在 `ppt/presentation.xml` 文件的 `<p:sldIdLst>` 中。

**重新排序**：调整 `<p:sldId>` 元素的顺序。

**删除**：移除对应的 `<p:sldId>`，然后运行 `clean.py` 脚本。

**添加**：使用 `add_slide.py` 脚本。切勿手动复制幻灯片文件——该脚本会处理手动复制会遗漏的备注引用、Content_Types.xml 文件以及关联ID。

---

## 编辑内容

**子代理**：如果可用，可在完成第4步后在此处使用它们。由于每个幻灯片都是独立的XML文件，子代理可以并行编辑。在向子代理发出的指令中，需包含以下信息：
- 需要编辑的幻灯片文件路径
- **“所有更改均使用编辑工具进行”**
- 下方列出的格式规则及常见陷阱

针对每张幻灯片，请执行以下操作：
1. 读取该幻灯片的XML文件
2. 找出所有占位符内容——包括文本、图片、图表、图标以及标题文字
3. 将每个占位符替换为最终内容

**请使用编辑工具，而非sed或Python脚本**。编辑工具能明确指定要替换的内容及其位置，从而提升操作的可靠性。

### 格式规则

- **将所有标题、子标题及行内标签加粗**：在 `<a:rPr>` 标签中设置 `b="1"`。这包括：
  - 幻灯片标题
  - 幻灯片内的章节标题
  - 行首的行内标签，例如“状态：”、“描述：”等
- **切勿使用Unicode项目符号（•）**：应使用 `<a:buChar>` 或 `<a:buAutoNum>` 来实现正确的列表格式
- **保持项目符号一致性**：让项目符号随布局自动设定。只需指定 `<a:buChar>` 或 `<a:buNone>` 即可。

---

## 常见陷阱

### 模板适配问题

当源内容的项目数量少于模板要求时：
- **应彻底移除多余的元素**（如图片、形状、文本框），而不仅仅是清除文字
- 清除文字内容后，需检查是否存在孤立的视觉元素
- 进行视觉质量检测，以发现数量不匹配的问题

当用长度不同的内容替换原有文本时：
- **较短的替换内容**：通常不会有问题
- **较长的替换内容**：可能会超出显示范围或出现意外换行
- 文本更改后，请通过视觉质量检测进行测试
- 考虑截断或拆分内容，以符合模板的设计要求

**模板中的占位槽 ≠ 源内容中的项目**：如果模板要求4名团队成员，但源内容只有3位用户，则需删除第4位成员的所有相关元素（包括图片和文本框），而不仅仅是文字。

### 多项目内容处理

如果源内容包含多个项目（如编号列表、多个章节），应为每个项目创建独立的 `<a:p>` 元素——**绝不能将它们合并成一段字符串**。

**❌ 错误做法**——将所有项目放在同一段落中：
```xml
<a:p>
  <a:r><a:rPr .../><a:t>Step 1: Do the first thing. Step 2: Do the second thing.</a:t></a:r>
</a:p>
```

**✅ 正确** — 使用加粗标题分隔各个段落：
```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" .../><a:t>Do the first thing.</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 2</a:t></a:r>
</a:p>
<!-- continue pattern -->
```

为保留行间距，请从原始段落中复制 `<a:pPr>` 标签。对于标题，则需使用 `b="1"` 属性。

### 智能引号

这类引号会由 unpack/pack 功能自动处理。不过“编辑”工具会将智能引号转换为 ASCII 引号。

**在添加带引号的新文本时，请使用 XML 实体：**

```xml
<a:t>the &#x201C;Agreement&#x201D;</a:t>
```

| 字符 | 名称 | Unicode编码 | XML实体 |
|-----------|------|---------|------------|
| `“` | 左双引号 | U+201C | `&#x201C;` |
| `”` | 右双引号 | U+201D | `&#x201D;` |
| `‘` | 左单引号 | U+2018 | `&#x2018;` |
| `’` | 右单引号 | U+2019 | `&#x2019;` |

### 其他说明

- **空白字符**：若 `<a:t>` 元素前后存在空白，需使用 `xml:space="preserve"` 属性。
- **XML解析**：请使用 `defusedxml.minidom` 而非 `xml.etree.ElementTree`（后者会导致命名空间损坏）。
