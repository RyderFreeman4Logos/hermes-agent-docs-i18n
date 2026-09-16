---
sidebar_position: 3
title: "Document Extraction"
description: "How read_file converts PDFs, Office documents, and notebooks to text — and what to do when a PDF is scanned images"
---

# 文档提取功能

`read_file` 工具能够自动将常见的文档格式转换为可读文本，从而使智能体能够以与读取源代码相同的方式查看 PDF 或电子表格文件。

## 支持的格式

| 格式 | 文件扩展名 | 转换器 | 是否始终可用 |
|------|-----------|---------|--------------|
| Jupyter 笔记本 | `.ipynb` | 内置（标准库） | 始终可用 |
| Word 文档 | `.docx` | 内置（标准库） | 始终可用 |
| Excel 工作簿 | `.xlsx` | 内置（标准库） | 始终可用 |
| PDF | `.pdf` | 可选 `anydoc` 转换器 | 首次使用时自动安装* |
| 旧版 Office 格式 | `.doc`, `.ppt`, `.xls`, `.pptx` 及其变体 | 可选 `anydoc` 转换器 | 首次使用时自动安装* |
| OpenDocument 格式 | `.odt`, `.ods`, `.odp` | 可选 `anydoc` 转换器 | 首次使用时自动安装* |
| 富文本/电子书 | `.rtf`, `.epub` | 可选 `anydoc` 转换器 | 首次使用时自动安装* |

\* 所述可选转换器为 `firecrawl-anydoc` 包，仅在允许懒加载的安装环境中自动安装（参见 `config.yaml` 中的 `security.allow_lazy_installs` 设置）。即便没有该包，三种标准库支持的格式仍可正常使用；其他格式则会回退至二进制文件处理机制。

转换后的输出为 Markdown 格式，可通过 `read_file` 工具原有的 `offset`/`limit` 参数进行分页查看。为控制单次处理时间，超过 50 MB 的文档将无法被处理。

提取功能支持远程终端后端（Docker、Modal、SSH）：文件的字节数据会通过后端边界传输并在主机端进行转换，因此沙箱环境中的文档与本地文档的读取效果一致。

## 扫描版PDF：覆盖率警告

PDF转换仅读取**文本层**。那些由扫描图像构成的页面——常见于法律文件、再销售包装、已签署的合同以及传真件——由于不存在文本层，因此会直接被转换为无内容格式。其典型特征是章节标题却没有任何文本内容。

当有相当比例的页面无法提取文本时（占文档总页数的20%以上，或绝对页数达到10页及以上），`read_file`函数会在提取结果前添加警告信息。每个无法读取的空白区域都会标注上其之前最后提取到的文本内容——通常是章节分隔符——这样智能体就能仅针对实际需要处理的区域进行操作，而无需对整个文档进行OCR识别：

```
[EXTRACTION COVERAGE WARNING: 198 of 311 pages in this PDF yielded no
text. ... Unreadable gaps, each labeled with the last text extracted
before it:
  pages 42-77 (36 pages) — after "Antigua Maintenance Corp Bylaws" (p41)
  pages 92-213 (122 pages) — after "... Covenants, Codes and Regulations" (p91)
  page 224 (1 page) — after "... Insurance Declaration Pages" (p223)
Decide which gaps you actually need — do NOT OCR or render everything. ...]
```

该警告会明确列出受影响的页面范围及恢复方法：

1. **少量页面——渲染模块与视觉识别模块。** 将这些页面转换为图像，然后使用视觉识别工具进行读取：
   ```bash
   pdftoppm -jpeg -r 150 -f 92 -l 94 document.pdf /tmp/page
   ```
随后可使用 `vision_analyze` 工具对每张图片进行检测。无需额外依赖（检测功能本身需要 poppler）。
2. **多页文档 —— OCR识别。** `ocr-and-documents` 技能可通过 marker-pdf 实现批量 OCR 识别（支持90多种语言，可处理公式和表格；安装包大小约为3-5 GB）。
检测过程会利用 poppler 的 `pdftotext` 功能来统计每页的文字数量。即便未安装 poppler，文档提取功能依然可用——只是会静默跳过覆盖率检查。
:::提示
该智能体可自动处理相关警告信息——它会主动提议对缺失的页面进行渲染或 OCR 识别。如果您自行查看提取结果，可将“内容为空的页眉”视为已扫描的部分，而非缺失页。 
:::
