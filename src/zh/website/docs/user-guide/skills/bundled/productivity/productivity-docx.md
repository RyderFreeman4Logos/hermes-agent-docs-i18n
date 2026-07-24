---
title: "Docx — Create, read, edit Word"
sidebar_label: "Docx"
description: "Create, read, edit Word"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Docx

创建、读取和编辑 Word .docx 文档及模板。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/productivity/docx` |
| 版本 | `1.0.0` |
| 开发者 | Anthropic（由 Nous Research 改编） |
| 许可证 | 专有许可证。详细条款请参见 LICENSE.txt 文件 |
| 支持平台 | linux、macos、windows |
| 标签 | `Word`、`DOCX`、`文档`、`Office`、`效率工具` |
| 相关技能 | [`pdf`](/docs/user-guide/skills/bundled/productivity/productivity-pdf)、[`xlsx`](/docs/user-guide/skills/bundled/productivity/productivity-xlsx)、[`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint)、[`ocr-and-documents`](/docs/user-guide/skills/bundled/productivity/productivity-ocr-and-documents) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# DOCX 技能

用于创建、读取和编辑 Word 文档——包括报告、备忘录、信件、信头、目录、修订标记（划线标注）以及评论。`.docx` 文件实际上是一个由 XML 文件组成的 ZIP 压缩包；该技能既支持高级的文档创建操作，也支持对 XML 文件进行精细编辑。

## 适用场景

当用户需要创建、读取、编辑或处理 Word 文档（.docx）或 Word 模板（.dotx）时，均可使用此技能。触发该技能的场景包括：提及“Word 文档”、“.docx”、“.dotx”，或要求以 Word 文件格式生成“报告”、“备忘录”、“信件”等文档；从 .docx 文件中提取或重新整理内容；在 Word 文件中进行查找替换；插入图片；添加修订标记或评论。请勿将此技能用于处理 PDF 文件（参见 `pdf` 技能）、电子表格（`xlsx`）或演示文稿（`powerpoint`）。

## 先决条件

```bash
npm ls docx --depth=0 2>/dev/null | grep -q docx || npm install docx   # creation (docx-js)
pip show pandoc >/dev/null 2>&1 || true; which pandoc || sudo apt install -y pandoc   # reading
which soffice || sudo apt install -y libreoffice     # rendering/verification
which pdftoppm || sudo apt install -y poppler-utils  # PDF → images
pip install defusedxml lxml   # validation scripts
```

macOS系统：执行`brew install pandoc libreoffice poppler`命令进行安装。

## 快速参考

| 任务 | 方法 |
|---|---|
| **创建**新文档 | 编写一个`docx`（npm）脚本——详见下方的注意事项 |
| **编辑**现有文档 | 先`unzip`解压文件 → 编辑`word/document.xml` → 再`zip`打包（docx-js无法直接打开现有文件） |
| **读取**内容 | 使用`pandoc -t markdown file.docx`命令（或使用可自动提取.docx文本的`read_file`函数） |

> 下方列出的脚本路径均相对于该技能对应的目录。

## 使用docx-js创建文档——注意事项

编写脚本并引入`require('docx')`。虽然模型熟悉该API，但仍需注意以下要点：

- **页面尺寸默认为A4。** 若需美式信纸尺寸，请设置`page: { size: { width: 12240, height: 15840 } }`（单位为DXA；1440等于1英寸）。
- **横向布局：** 需提供纵向尺寸并设置`orientation: PageOrientation.LANDSCAPE`——docx-js会自动调整宽高数值。
- **表格需设置双宽度：** 需同时为表格设置`columnWidths`，并为每个单元格设置`width`，且两者均需使用`WidthType.DXA`单位（使用PERCENTAGE比例会导致在Google Docs中显示异常）。所有列的宽度之和必须等于表格总宽度。
- **表格阴影：** 应使用`ShadingType.CLEAR`类型，切勿使用`SOLID`类型（否则会显示为黑色）。
- **列表项：** 不可直接插入`•`符号，应通过`numbering`配置并设置`LevelFormat.BULLET`来实现。
- **`ImageRun`元素必须指定`type:`属性**，可选值为`"png"`、`"jpg"`等。
- **`PageBreak`换行符必须位于`Paragraph`段落内部。**
- **严禁使用`\n`换行符**，应通过创建多个独立的`Paragraph`元素来实现换行。
- **目录生成：** 标题必须使用内置的`HeadingLevel.*`格式；自定义标题样式需设置`outlineLevel`属性，否则不会显示在目录中。
- **不可将表格用作横线分隔符**，应改用段落底部边框替代。
- **项目符号/同行右对齐：** 应在`TextRun`元素中使用`PositionalTab`属性（设置`alignment: PositionalTabAlignment.RIGHT`和`leader: PositionalTabLeader.DOT`），而非直接使用`.`符号或空格填充。

## 验证输出结果

编写完`.docx`文件后，需将其渲染并查看最终效果：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.docx
pdftoppm -jpeg -r 100 output.pdf page
ls page-*.jpg   # then inspect each with vision_analyze
```

`pdftoppm` 会将页码补零至与页面宽度相同的长度（即 `page-01.jpg`…`page-12.jpg`）。

## 编辑现有文档

需先将旧版的 `.doc` 文件转换为其他格式：`python scripts/office/soffice.py --headless --convert-to docx file.doc`。

```bash
unzip -q doc.docx -d unpacked/
find unpacked -type l -delete   # strip symlink entries — docx from external parties is untrusted
python scripts/merge_runs.py unpacked/   # coalesce fragmented runs so text is findable
# edit unpacked/word/document.xml in place — do NOT reformat or pretty-print
(cd unpacked && rm -f ../out.docx && zip -Xr ../out.docx .)
python scripts/office/validate.py out.docx --original doc.docx   # XSD checks; --auto-repair fixes common issues
# redlining? add --author "<the name you redlined under>" to check every edit is tracked
```

Word会将文本拆分到多个 `<w:r>` 单元中（即修订编号、拼写检查标记等），因此你在文档中看到的某个短语，在XML文件中往往并非以连续的字符串形式存在。`merge_runs.py` 能够合并 `word/document.xml` 中格式相同的相邻单元，同时不会改变内容或渲染效果；它还支持直接处理 `.docx` 文件（用法：`python scripts/merge_runs.py doc.docx -o merged.docx`）。

**已跟踪的更改**：在标记修改处时，可使用 `--author "<你在标记处填写的姓名>"` 参数进行验证（该参数需要配合 `--original` 使用）——它会列出所有未被 `<w:ins>`/`<w:del>` 标记包裹的修改内容，这类修改很容易在无意间产生，且在常规显示模式下是不可见的。你可以利用 `w:id`、`w:author`、`w:date` 属性将相关单元包裹在 `<w:ins>`/`<w:del>` 标签中。在 `<w:del>` 标签内，文本元素应为 `<w:delText>`，而非 `<w:t>`。被删除的段落标记（格式为 `<w:pPr><w:rPr><w:del w:id=".." w:author=".." w:date=".."/></w:rPr></w:pPr>`）表示“将此段落与下一段合并”——因此，若要彻底删除一个段落，则需在每个单元周围加上 `<w:del>` 标签。`<w:del/>` 标签必须位于该段落标记的其他子元素之前，其顺序受架构规范约束。

如需生成一份已接受所有跟踪更改的干净副本，可使用命令：`python scripts/accept_changes.py in.docx out.docx`。

对于被删除的段落标记，处理方式应是将其与下一段合并，这样一来，所有单元都被删除的段落就会消失。Word能够做到这一点，但 `accept_changes.py` 和 `pandoc --track-changes=accept` 并不总是如此。两者的错误表现一致：它们虽然去除了被删除的文本，却留下了空段落，而在自动编号时，这些空段落会显示为多余的空白项目符号：

- `pandoc --track-changes=accept` 从不合并段落。
- `accept_changes.py`（基于LibreOffice）可以正确合并段落，但当被删除的段落后紧跟一个空段落时除外。

无论在哪种显示模式下，出现的空白项目符号都是该显示方式的特性，并非文档本身的缺陷。建议直接查看XML文件中的段落删除情况。

## 注释

注释需要六个相互关联的文件。可使用专用工具处理：若还需编辑 `document.xml`，则采用目录模式（可避免反复解压/压缩的操作）；否则则使用直接处理 `.docx` 文件的模式：

```bash
# Against an already-unpacked directory (preferred when also placing markers)
python scripts/comment.py unpacked/ "Fees & expenses cap is too low"
python scripts/comment.py unpacked/ "Agreed" --parent 0

# Against a .docx directly
python scripts/comment.py contract.docx "This cap is too low" -o annotated.docx
```

该脚本会生成 `comments.xml`、`commentsExtended.xml`、`commentsIds.xml`、`commentsExtensible.xml`，以及用于定义文本关联关系和内容类型覆盖规则的文件。评论编号会自动分配。随后，脚本还会输出 `<w:commentRangeStart>`/`<w:commentRangeEnd>`/`<w:commentReference>` 这些片段，将其添加到 `word/document.xml` 中，从而让评论能够定位到具体的文本——在插入这些标记之前，虽然评论已存在，但不可见。

## 常见问题

- 不要通过 `xml.etree.ElementTree` 对 OOXML 文件进行反复读写操作，因为这会导致命名空间前缀被重写，进而使文件损坏。如需通过脚本实现转换，请使用 `defusedxml.minidom`。
- 应在解压后的目录内部执行压缩操作（即 `cd unpacked && zip -Xr ../out.docx .`），并且先删除目标文件，否则被删除的文件内容仍会残留在压缩包中。

## 验证方法

1. 运行命令 `python scripts/office/validate.py out.docx --original in.docx`，对文件的架构、关联关系及内容类型进行检测；每次检测失败时都会提示相应的修复方法。
2. 将文件转换为 PDF 后再提取为图片（详见“验证输出结果”部分），并使用 `vision_analyze` 工具检查每一页的内容，查看是否存在表格损坏、图片缺失、排版异常或残留的占位文本等问题。

## 相关技能

`pdf`（PDF 处理）、`xlsx`（电子表格）、`powerpoint`（演示文稿）、`ocr-and-documents`（扫描文档内容提取）。
