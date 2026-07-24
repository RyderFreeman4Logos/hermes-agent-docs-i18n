---
title: "Pdf — Create, merge, split, fill, and secure PDF files"
sidebar_label: "Pdf"
description: "Create, merge, split, fill, and secure PDF files"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# PDF 处理

创建、合并、拆分、填充及保护 PDF 文件。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/productivity/pdf` |
| 版本 | `1.0.0` |
| 开发者 | Anthropic（由 Nous Research 优化） |
| 许可证 | 专有许可证。详细条款请参阅 LICENSE.txt 文件 |
| 支持平台 | linux、macos、windows |
| 标签 | `PDF`、`文档`、`表单`、`办公软件`、`效率工具` |
| 相关技能 | [`ocr-and-documents`](/docs/user-guide/skills/bundled/productivity/productivity-ocr-and-documents)、[`nano-pdf`](/docs/user-guide/skills/bundled/productivity/productivity-nano-pdf)、[`docx`](/docs/user-guide/skills/bundled/productivity/productivity-docx)、[`xlsx`](/docs/user-guide/skills/bundled/productivity/productivity-xlsx) |

## 参考：完整 SKILL.md 内容

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当该技能处于激活状态时，智能体将依据此内容执行操作。
:::

# PDF 处理技能

可用来创建、组合、拆分、转换及保护 PDF 文件——支持合并文件、页面操作、表单填充、添加水印、加密/解密，以及提取文本和表格内容。若需从扫描文档中批量提取文本，建议使用 `ocr-and-documents` 技能；若需要对现有 PDF 文本进行自然语言编辑，则推荐使用 `nano-pdf`。

## 适用场景

每当用户需要对 PDF 文件执行以下操作时，均可使用此技能：读取或提取文本/表格、合并多个 PDF 文件、拆分 PDF 文件、旋转页面、添加水印、创建新 PDF 文件、填写 PDF 表单、加密/解密、提取图片，或对扫描版 PDF 进行 OCR 处理。如果用户提及了 .pdf 文件或要求生成此类文件，也应使用此技能。

## 先决条件

```bash
pip install pypdf pdfplumber reportlab
which pdftotext || sudo apt install -y poppler-utils   # pdftotext, pdftoppm, pdfimages
which qpdf || sudo apt install -y qpdf                 # CLI merge/split/decrypt
```

macOS系统：执行`brew install poppler qpdf`。如需OCR相关功能，还需安装：`pip install pytesseract pdf2image`，并执行`sudo apt install -y tesseract-ocr`。

> 下方列出的脚本路径均相对于该技能的目录所在位置。表单填写有专门的工作流程——请参阅[forms.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/pdf/forms.md)并按照说明操作。如需了解高级库的使用方法（如pypdfium2、pdf-lib）及故障排除技巧，请参考[reference.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/pdf/reference.md)。

## 快速参考

| 任务 | 最佳工具 | 命令/代码 |
|------|-----------|--------------|
| 合并PDF文件 | pypdf | 每页通过`writer.add_page(page)`添加 |
| 分割PDF文件 | pypdf | 每页生成一个文件 |
| 提取文本 | pdfplumber | 使用`page.extract_text()`方法 |
| 提取表格 | pdfplumber | 使用`page.extract_tables()`方法 |
| 创建PDF文件 | reportlab | 可选择Canvas或Platypus引擎 |
| 命令行合并/分割 | qpdf | 使用`qpdf --empty --pages ...`命令 |
| 对扫描版PDF进行OCR识别 | pytesseract | 需先将其转换为图像格式（或使用`ocr-and-documents`工具） |
| 填写PDF表单 | 请参阅[forms.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/pdf/forms.md) | 可使用`scripts/fill_fillable_fields.py`等脚本 |
| 编辑现有文本 | `nano-pdf`技能 | 使用命令`nano-pdf edit file.pdf <page> "<指令>"` |

## 常见操作

### 合并/分割/旋转PDF文件（使用pypdf）

```python
from pypdf import PdfReader, PdfWriter

# Merge
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    for page in PdfReader(pdf_file).pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as f:
    writer.write(f)

# Split: one file per page
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    w = PdfWriter(); w.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as f:
        w.write(f)

# Rotate
page = reader.pages[0]
page.rotate(90)  # clockwise
```

### 提取文本与表格（pdfplumber）

```python
import pdfplumber, pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    tables = [pd.DataFrame(t[1:], columns=t[0])
              for page in pdf.pages
              for t in page.extract_tables() if t]
```

### 创建 PDF 文件（ReportLab）

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = [Paragraph("Report Title", styles["Title"]), Spacer(1, 12),
         Paragraph("Body text...", styles["Normal"]), PageBreak(),
         Paragraph("Page 2", styles["Heading1"])]
doc.build(story)
```

**下标/上标：** 绝对不要使用 Unicode 下标/上标字符（如 ₀₁₂、⁰¹２），因为内置字体不支持这些符号，会导致显示为纯黑色方框。应在 `Paragraph` 对象中使用 `<sub>`/`<super>` 标签来实现该效果，例如：`Paragraph("H<sub>2</sub>O", styles['Normal'])`。对于通过画布绘制的文本，则需要手动调整字体大小和位置。

### 命令行工具

```bash
pdftotext -layout input.pdf output.txt                     # text, layout preserved
pdftotext -f 1 -l 5 input.pdf output.txt                   # pages 1-5
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf     # merge
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf               # split range
qpdf input.pdf output.pdf --rotate=+90:1                   # rotate page 1
qpdf --password=pw --decrypt encrypted.pdf decrypted.pdf   # remove password
pdfimages -j input.pdf img                                 # extract images
```

### 水印功能

```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader, writer = PdfReader("document.pdf"), PdfWriter()
for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)
with open("watermarked.pdf", "wb") as f:
    writer.write(f)
```

### 密码保护

```python
writer.encrypt("userpassword", "ownerpassword")
```

### OCR扫描的PDF文件

```python
import pytesseract
from pdf2image import convert_from_path

pages = convert_from_path("scanned.pdf")
text = "\n\n".join(pytesseract.image_to_string(img) for img in pages)
```

对于扫描文档的批量/结构化提取，使用 `ocr-and-documents` 技能（基于 pymupdf 和 marker-pdf）是更为理想的选择。

## 表单填写

请先阅读 [forms.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/pdf/forms.md) —— 该文档明确了可填写的（AcroForm 格式）PDF与普通扫描表单的区别，并介绍了相关的辅助脚本：

- `scripts/check_fillable_fields.py` —— 检测 PDF 是否包含 AcroForm 字段；
- `scripts/extract_form_field_info.py` / `scripts/extract_form_structure.py` —— 列出所有字段信息；
- `scripts/fill_fillable_fields.py` —— 填写 AcroForm 字段；
- `scripts/fill_pdf_form_with_annotations.py` —— 在普通表单上叠加文本进行填写；
- `scripts/check_bounding_boxes.py`、`scripts/create_validation_image.py` —— 通过视觉方式验证字段的放置位置是否正确。

## 常见问题

- 对于仅包含图片的页面，`page.extract_text()` 会返回 `None` —— 应使用 `or ""` 进行处理，并回退至 OCR 方法；
- pypdf 会保留 PDF 的加密标志：若要读取加密PDF，需先使用 `PdfReader(path, password=...)` 解密，才能访问页面内容；
- reportlab 的坐标系原点位于左下角，单位为1/72英寸——而非左上角；
- 通过叠加文本的方式填写普通表单时，务必先生成验证图像并检查字段位置，确认无误后再提交。

## 验证方法

1. 使用 `PdfReader` 打开处理后的文件，确认页面数量与预期一致；
2. 再次从输出文件中提取文本（可使用 `pdftotext` 或 pdfplumber），确保手动添加的内容完整存在；
3. 对于包含水印、已填写的表单或生成的报告等视觉内容，可使用 `pdftoppm -jpeg -r 100 output.pdf page` 导出对应页面的图像，再通过 `vision_analyze` 工具进行查看。

## 相关技能

`ocr-and-documents`（扫描文档文本提取）、`nano-pdf`（对PDF内容进行原生文本编辑）、`docx`（Word文档处理）、`xlsx`（电子表格处理）、`powerpoint`（演示文稿处理）。
