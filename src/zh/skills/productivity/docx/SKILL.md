---
name: docx
description: "Create, read, edit Word .docx documents and templates."
version: 1.0.0
author: Anthropic (adapted by Nous Research)
license: Proprietary. LICENSE.txt has complete terms
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Word, DOCX, Documents, Office, Productivity]
    category: productivity
    related_skills: [pdf, xlsx, powerpoint, ocr-and-documents]
---

# DOCX技能

用于创建、读取和编辑Word文档——包括报告、备忘录、信件、信头、目录、修订痕迹（标红标注）以及评论。`.docx`文件实际上是一个由XML文件组成的ZIP压缩包；该技能既支持高级的创建操作，也支持精细的XML代码编辑。

## 适用场景

当用户需要创建、读取、编辑或处理Word文档（.docx）或Word模板（.dotx）时，均可使用此技能。触发场景包括：提及“Word文档”、“.docx”、“.dotx”，或要求将“报告”、“备忘录”、“信件”等内容以Word文件形式生成；从.docx文件中提取或重新整理内容；在Word文件中进行查找替换；插入图片；处理修订痕迹或评论。请勿用于PDF文件（请参考`pdf`技能）、电子表格（`xlsx`）或演示文稿（`powerpoint`）。

## 先决条件

```bash
npm ls docx --depth=0 2>/dev/null | grep -q docx || npm install docx   # creation (docx-js)
pip show pandoc >/dev/null 2>&1 || true; which pandoc || sudo apt install -y pandoc   # reading
which soffice || sudo apt install -y libreoffice     # rendering/verification
which pdftoppm || sudo apt install -y poppler-utils  # PDF → images
pip install defusedxml lxml   # validation scripts
```

macOS系统：执行命令 `brew install pandoc libreoffice poppler`。

## 快速参考

| 任务 | 方法 |
|---|---|
| **创建**新文档 | 编写一个`docx`（npm）脚本——详见下方的注意事项 |
| **编辑**现有文档 | 先`unzip`解压 → 编辑`word/document.xml`文件 → 再`zip`压缩（docx-js无法直接打开现有文件） |
| **读取**内容 | 使用命令 `pandoc -t markdown file.docx`（或使用能自动提取.docx文本的`read_file`函数） |

> 下方列出的脚本路径均相对于该技能对应的目录。

## 使用docx-js创建文档——注意事项

编写脚本并引入`require('docx')`。虽然模型了解该API的用法，但仍需注意以下几点：

- **页面大小默认为A4。** 若需美式信纸尺寸，请设置 `page: { size: { width: 12240, height: 15840 } }`（单位为DXA；1440 = 1英寸）。
- **横向布局：** 需提供纵向尺寸并设置`orientation: PageOrientation.LANDSCAPE`——docx-js会自动调整宽高值。
- **表格需设置双宽度：** 需同时为表格设置`columnWidths`，并为每个单元格设置`width`，且两者均需使用`WidthType.DXA`单位（使用PERCENTAGE单位会在Google Docs中出错）。所有列的宽度之和必须等于表格的总宽度。
- **表格阴影：** 应使用`ShadingType.CLEAR`，切勿使用`SOLID`（否则会显示为黑色）。
- **列表：** 不可直接插入`•`符号；应通过`numbering`配置并设置`LevelFormat.BULLET`来实现项目符号。
- **`ImageRun`元素必须指定`type:`属性**，可选值为`"png"`、`"jpg"`等。
- **`PageBreak`元素必须置于`Paragraph`元素内部。**
- **切勿使用`\n`换行符**——应通过创建独立的`Paragraph`元素来实现换行。
- **目录生成：** 标题必须使用内置的`HeadingLevel.*`格式；自定义标题样式需设置`outlineLevel`属性，否则不会显示在目录中。
- **不可将表格用作横线分隔符**——应改用段落底部边框来替代。
- **点状前导符/同行右对齐：** 应在`TextRun`元素内使用`PositionalTab`属性（设置`alignment: PositionalTabAlignment.RIGHT`和`leader: PositionalTabLeader.DOT`），而非直接使用`.`符号或空格填充。

## 验证输出结果

编写完`.docx`文件后，将其渲染并查看效果：

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

Word会将文本拆分到多个 `<w:r>` 单元中（即修订编号、拼写检查标记），因此你在文档中看到的某个短语，在XML文件中往往并非以连续字符串的形式存在。`merge_runs.py` 可以合并 `word/document.xml` 中格式相同的相邻单元，且不会改变内容或渲染效果；它还支持直接处理 `.docx` 文件（用法：`python scripts/merge_runs.py doc.docx -o merged.docx`）。

**已跟踪的更改**：在进行标记编辑时，可使用 `--author "<你在标记处填写的姓名>"` 参数进行验证（该参数需要配合 `--original` 使用）——它会标出所有未被 `<w:ins>`/`<w:del>` 标记的修改内容，这类修改很容易在无意间发生，且在常规视图下是不可见的。你可以利用 `w:id`、`w:author`、`w:date` 属性将相关单元包裹在 `<w:ins>`/`<w:del>` 标签中。在 `<w:del>` 标签内，文本元素应为 `<w:delText>`，而非 `<w:t>`。被删除的段落标记（格式为 `<w:pPr><w:rPr><w:del w:id=".." w:author=".." w:date=".."/></w:rPr></w:pPr>`）表示“将该段落与下一段合并”——因此要彻底删除一个段落，还需在每个单元周围添加 `<w:del>` 标签。`<w:del/>` 标签必须出现在 `rPr` 元素的其他子元素之前，其顺序受架构规范约束。

若要生成一份已接受所有已跟踪更改的完整副本，可使用命令：`python scripts/accept_changes.py in.docx out.docx`。

对于被删除的段落标记，处理方式应是将其与下一段合并，这样一来，所有单元都被删除的段落就会消失。Word能够做到这一点，但 `accept_changes.py` 和 `pandoc --track-changes=accept` 并不总是如此。两者的错误表现一致：它们虽然去除了被删除的文本，却留下了空段落，而在自动编号列表中，这些空段落会显示为多余的空白项：

- `pandoc --track-changes=accept` 从不合并段落。
- `accept_changes.py`（基于LibreOffice）能够正确合并段落，但当被删除的段落后面紧跟一个空段落时除外。

无论在哪种视图下出现的空白项，都只是该视图的表现形式，并非文档本身的缺陷。建议直接查看XML文件中的段落删除情况。

## 注释

注释的生成需要六个相互关联的文件。可使用专用工具处理：若还需编辑 `document.xml`，则采用目录模式（这样可以避免反复解压/压缩的操作）；否则则使用直接处理 `.docx` 文件的模式：

```bash
# Against an already-unpacked directory (preferred when also placing markers)
python scripts/comment.py unpacked/ "Fees & expenses cap is too low"
python scripts/comment.py unpacked/ "Agreed" --parent 0

# Against a .docx directly
python scripts/comment.py contract.docx "This cap is too low" -o annotated.docx
```

该脚本会生成 `comments.xml`、`commentsExtended.xml`、`commentsIds.xml`、`commentsExtensible.xml`，以及用于定义文本关联关系和内容类型覆盖规则的文件。评论编号会自动分配。随后，脚本还会输出 `<w:commentRangeStart>`/`<w:commentRangeEnd>`/`<w:commentReference>` 这些标签片段，将其添加到 `word/document.xml` 中，从而让评论能够定位到具体的文本——在插入这些标记之前，评论虽然存在，但不可见。

## 常见问题

- 不要通过 `xml.etree.ElementTree` 对 OOXML 文件进行反复读写操作，因为这会导致命名空间前缀被重写，进而使文件损坏。如需通过脚本实现转换，请使用 `defusedxml.minidom`。
- 应在解压后的目录内部执行压缩操作（即 `cd unpacked && zip -Xr ../out.docx .`），并且先删除目标文件，否则被删除的文件内容仍会残留在压缩包中。

## 验证方法

1. 运行命令 `python scripts/office/validate.py out.docx --original in.docx`，对文件的架构、关联关系及内容类型进行检查；每次检测失败时都会提示相应的修复方法。
2. 将文件转换为 PDF 后再提取图片（详见“验证输出结果”部分），并使用 `vision_analyze` 工具检查每一页的内容，查看是否存在表格损坏、图片缺失、排版异常或残留的占位文本等问题。

## 相关技能

`pdf`（PDF 处理）、`xlsx`（电子表格）、`powerpoint`（演示文稿）、`ocr-and-documents`（扫描文档内容提取）。
