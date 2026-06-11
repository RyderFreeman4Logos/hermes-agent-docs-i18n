---
title: "Ocr And Documents — Extract text from PDFs/scans (pymupdf, marker-pdf)"
sidebar_label: "Ocr And Documents"
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# OCR与文档处理

从PDF/扫描件中提取文本（使用pymupdf、marker-pdf库）。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/productivity/ocr-and-documents` |
| 版本 | `2.3.0` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `PDF`、`文档处理`、`研究`、`Arxiv`、`文本提取`、`OCR` |
| 相关技能 | [`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint) |

## 参考：完整SKILL.md内容

:::info
以下是Hermes在触发该技能时加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行操作。
:::

# PDF与文档提取

对于DOCX格式文件：建议使用`python-docx`库（可解析真实的文档结构，效果远优于OCR）。
对于PPTX格式文件：可参考`powerpoint`技能（该技能基于`python-pptx`库，支持完整的幻灯片及备注内容解析）。
本技能支持**PDF文件及扫描文档**的提取。

## 第一步：是否有远程URL？

如果文档存在URL地址，**请优先尝试使用`web_extract`方法**：

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

该功能通过 Firecrawl 实现 PDF 到 Markdown 的转换，且无需任何本地依赖。

仅在以下情况才使用本地提取方式：文件位于本地、web_extract 失败，或需要批量处理时。

## 第 2 步：选择本地提取器

| 功能特性 | pymupdf（约 25MB） | marker-pdf（约 3-5GB） |
|---------|-----------------|---------------------|
| **文本型 PDF** | ✅ | ✅ |
| **扫描版 PDF（OCR）** | ❌ | ✅（支持 90 多种语言） |
| **表格** | ✅（基础功能） | ✅（高精度识别） |
| **公式/LaTeX** | ❌ | ✅ |
| **代码块** | ❌ | ✅ |
| **表单** | ❌ | ✅ |
| **去除页眉/页脚** | ❌ | ✅ |
| **阅读顺序检测** | ❌ | ✅ |
| **图片提取** | ✅（嵌入式图片） | ✅（结合上下文提取） |
| **图片转文本（OCR）** | ❌ | ✅ |
| **EPUB 格式** | ✅ | ✅ |
| **Markdown 输出格式** | ✅（通过 pymupdf4llm 实现） | ✅（原生输出，质量更高） |
| **安装大小** | 约 25MB | 约 3-5GB（包含 PyTorch 及模型文件） |
| **处理速度** | 即时完成 | 每页约 1-14 秒（CPU），每页约 0.2 秒（GPU） |

**决策建议**：除非需要 OCR、公式识别、表单处理或复杂的布局分析功能，否则优先使用 pymupdf。

如果用户需要 marker 的高级功能，但系统可用磁盘空间不足 5GB：
> “该文档需要通过 OCR/高级提取功能（marker-pdf）处理，这需要约 5GB 的空间用于存储 PyTorch 及相关模型。您的系统目前仅有 [X]GB 的空闲空间。解决方案包括：释放更多空间、提供文件 URL 以便我使用 web_extract 方式处理，或者尝试使用仅适用于文本型 PDF、无法处理扫描文档或公式的 pymupdf。”

---

## pymupdf（轻量版）

```bash
pip install pymupdf pymupdf4llm
```

**通过辅助脚本**：
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**内联模式**：
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

## marker-pdf（高质量 OCR）

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**通过辅助脚本**：
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI**（与 marker-pdf 一同安装）：
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

## Arxiv论文库

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## 分割、合并与搜索

pymupdf可直接实现这些功能——可使用`execute_code`或内联Python代码来完成：

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

无需额外依赖——pymupdf 一个包即可实现文档的分割、合并、搜索及文本提取功能。

---

## 备注

- 对于网址，`web_extract` 始终是首选方案
- pymupdf 是安全可靠的默认选择——响应迅速、无需模型、可在任何环境中使用
- marker-pdf 适用于 OCR 处理、扫描文档、公式以及结构复杂的文档——仅在必要时安装
- 两个辅助脚本均支持 `--help` 参数以查看完整用法说明
- 首次使用时，marker-pdf 会向 `~/.cache/huggingface/` 下载约 2.5GB 的模型文件
- 处理 Word 文档时：请使用 `pip install python-docx`（相比 OCR 更高效，可直接解析文档结构）
- 处理 PowerPoint 文件时：请参考 `powerpoint` 技能（该技能基于 python-pptx 库）
