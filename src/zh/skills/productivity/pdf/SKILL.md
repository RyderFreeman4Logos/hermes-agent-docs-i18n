---
name: pdf
description: "Create, merge, split, fill, and secure PDF files."
version: 1.0.0
author: Anthropic (adapted by Nous Research)
license: Proprietary. LICENSE.txt has complete terms
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Forms, Office, Productivity]
    category: productivity
    related_skills: [ocr-and-documents, nano-pdf, docx, xlsx]
---

# PDF技能

用于创建、合并、拆分、转换及保护PDF文件——支持文档合并、页面操作、表单填写、水印添加、加密以及文本/表格提取功能。若需从扫描文档中批量提取文本，建议使用`ocr-and-documents`技能；若需要对现有PDF文本中的自然语言内容进行编辑，则推荐使用`nano-pdf`技能。

## 适用场景

每当用户需要对PDF文件执行任何操作时均可使用此技能，例如读取或提取文本/表格、合并多个PDF文件、拆分PDF文件、旋转页面、添加水印、创建新PDF文件、填写PDF表单、加密/解密、提取图片，或是对扫描版PDF进行OCR识别。若用户提及.pdf文件或要求生成此类文件，也应使用此技能。

## 先决条件

```bash
pip install pypdf pdfplumber reportlab
which pdftotext || sudo apt install -y poppler-utils   # pdftotext, pdftoppm, pdfimages
which qpdf || sudo apt install -y qpdf                 # CLI merge/split/decrypt
```

macOS系统：执行`brew install poppler qpdf`。如需OCR相关功能，还需安装：`pip install pytesseract pdf2image`，并通过`sudo apt install -y tesseract-ocr`完成配置。

> 下方列出的脚本路径均相对于该技能的所在目录。表单填写有独立的工作流程——请参阅[forms.md](forms.md)中的说明。如需了解高级库的使用方法（如pypdfium2、pdf-lib）及故障排除技巧，请参考[reference.md](reference.md)。

## 快速参考

| 任务 | 最佳工具 | 命令/代码 |
|------|-----------|--------------|
| 合并PDF文件 | pypdf | 每页分别调用`writer.add_page(page)` |
| 分割PDF文件 | pypdf | 每页生成一个独立文件 |
| 提取文本 | pdfplumber | 调用`page.extract_text()`方法 |
| 提取表格 | pdfplumber | 调用`page.extract_tables()`方法 |
| 创建PDF文件 | reportlab | 可选择Canvas或Platypus引擎 |
| 命令行合并/分割 | qpdf | 使用命令`qpdf --empty --pages ...` |
| 对扫描版PDF进行OCR识别 | pytesseract | 需先将其转换为图像格式（或使用`ocr-and-documents`工具） |
| 填写PDF表单 | 请参阅[forms.md](forms.md) | 可使用`scripts/fill_fillable_fields.py`等脚本 |
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

**下标/上标：** 绝对不要使用 Unicode 下标/上标字符（如 ₀₁₂、⁰¹２），因为内置字体不支持这些符号，会导致显示为实心黑色方框。应在 `Paragraph` 对象中使用 `<sub>`/`<super>` 标签来实现该效果，例如：`Paragraph("H<sub>2</sub>O", styles['Normal'])`。对于通过画布绘制的文本，则需要手动调整字体大小和位置。

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

### OCR扫描版PDF文件

```python
import pytesseract
from pdf2image import convert_from_path

pages = convert_from_path("scanned.pdf")
text = "\n\n".join(pytesseract.image_to_string(img) for img in pages)
```

对于扫描文档的批量/结构化提取，`ocr-and-documents` 技能（基于 pymupdf 和 marker-pdf）是更为理想的选择。

## 表单填写

请先阅读 [forms.md](forms.md) —— 该文档明确了可填写的（AcroForm）PDF 文件与普通扫描表单的区别，并介绍了相关的辅助脚本：

- `scripts/check_fillable_fields.py` —— 检测 PDF 中是否存在 AcroForm 字段；
- `scripts/extract_form_field_info.py` / `scripts/extract_form_structure.py` —— 列出所有字段信息；
- `scripts/fill_fillable_fields.py` —— 填写 AcroForm 字段；
- `scripts/fill_pdf_form_with_annotations.py` —— 在普通表单上叠加文本；
- `scripts/check_bounding_boxes.py`, `scripts/create_validation_image.py` —— 通过视觉方式验证内容位置是否正确。

## 常见问题

- 对于仅包含图像的页面，`page.extract_text()` 会返回 `None` —— 应使用 `or ""` 进行处理，并回退至 OCR 方法；
- pypdf 会保留文档的加密标志：若要读取加密 PDF，需先使用 `PdfReader(path, password=...)` 解密，之后才能访问页面内容；
- reportlab 的坐标系以左下角为原点，单位为 1/72 英寸 —— 而非左上角；
- 通过叠加文本方式填写普通表单时，务必先生成验证图像并检查内容位置，然后再提交结果。

## 验证方法

1. 使用 `PdfReader` 打开输出文件，确认页面数量与预期一致；
2. 使用 `pdftotext` 或 pdfplumber 重新提取输出文件中的文本，确保所添加的内容确实存在；
3. 对于包含水印、已填写的表单或生成的报告等可视化内容，可使用 `pdftoppm -jpeg -r 100 output.pdf page` 导出图像，再通过 `vision_analyze` 工具进行查看。

## 相关技能

`ocr-and-documents`（扫描文档文本提取）、`nano-pdf`（对 PDF 进行原生文本编辑）、`docx`（Word 文档处理）、`xlsx`（电子表格处理）、`powerpoint`（演示文稿处理）。
