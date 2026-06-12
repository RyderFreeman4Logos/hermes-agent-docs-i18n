# 机器学习/人工智能会议的LaTeX模板

该目录收录了各大机器学习与人工智能会议的官方LaTeX模板。

---

## 将LaTeX编译为PDF

### 方案1：搭配LaTeX Workshop的VS Code（推荐）

**准备工作：**
1. 安装[TeX Live](https://www.tug.org/texlive/)（建议安装完整版）
   - macOS系统：`brew install --cask mactex`
   - Ubuntu系统：`sudo apt install texlive-full`
   - Windows系统：从[tug.org/texlive](https://www.tug.org/texlive/)下载

2. 安装VS Code扩展：James Yu开发的**LaTeX Workshop**
   - 打开VS Code → 进入“扩展”选项（Cmd/Ctrl+Shift+X）→ 搜索“LaTeX Workshop”→ 点击安装

**使用方法：**
- 在VS Code中打开任意`.tex`文件
- 保存文件（Cmd/Ctrl+S）→ 系统会自动将其编译为PDF
- 点击绿色的播放按钮或使用`Cmd/Ctrl+Alt+B`来启动编译过程
- 查看PDF文档：点击“查看LaTeX PDF”图标或使用`Cmd/Ctrl+Alt+V`
- 并排查看文档：先按`Cmd/Ctrl+Alt+V`，再拖动标签页

**相关设置**（可添加到VS Code的`settings.json`文件中）：
```json
{
  "latex-workshop.latex.autoBuild.run": "onSave",
  "latex-workshop.view.pdf.viewer": "tab",
  "latex-workshop.latex.recipes": [
    {
      "name": "pdflatex → bibtex → pdflatex × 2",
      "tools": ["pdflatex", "bibtex", "pdflatex", "pdflatex"]
    }
  ]
}
```

### 方案二：命令行

```bash
# Basic compilation
pdflatex main.tex

# With bibliography (full workflow)
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Using latexmk (handles dependencies automatically)
latexmk -pdf main.tex

# Continuous compilation (watches for changes)
latexmk -pdf -pvc main.tex
```

### 方案 3：Overleaf（在线版）

1. 访问 [overleaf.com](https://www.overleaf.com)
2. 选择“新建项目”→“上传项目”→将模板文件夹以 ZIP 格式上传
3. 可在线编辑，并支持实时 PDF 预览
4. 无需在本地进行安装

### 方案 4：其他集成开发环境

| IDE | 扩展/插件 | 备注 |
|-----|----------|------|
| **Cursor** | LaTeX Workshop | 功能与 VS Code 相同 |
| **Sublime Text** | LaTeXTools | 广受欢迎且维护良好 |
| **Vim/Neovim** | VimTeX | 功能强大，依赖键盘操作 |
| **Emacs** | AUCTeX | 功能完善的 LaTeX 开发环境 |
| **TeXstudio** | 内置插件 | 专用的 LaTeX IDE |
| **Texmaker** | 内置功能 | 跨平台的 LaTeX 编辑器 |

### 编译故障排除

**“文件未找到”错误：**
```bash
# Ensure you're in the template directory
cd templates/icml2026
pdflatex example_paper.tex
```

**参考文献未显示：**
```bash
# Run bibtex after first pdflatex
pdflatex main.tex
bibtex main        # Uses main.aux to find citations
pdflatex main.tex  # Incorporates bibliography
pdflatex main.tex  # Resolves references
```

**缺失的包：**
```bash
# TeX Live package manager
tlmgr install <package-name>

# Or install full distribution to avoid this
```

## 可用模板

| 会议名称 | 目录路径 | 年份 | 来源 |
|----------|-----------|------|------|
| ICML | `icml2026/` | 2026 | [ICML官方页面](https://icml.cc/Conferences/2026/AuthorInstructions) |
| ICLR | `iclr2026/` | 2026 | [官方GitHub仓库](https://github.com/ICLR/Master-Template) |
| NeurIPS | `neurips2025/` | 2025 | 社区提供的模板 |
| ACL | `acl/` | 2025年及以后 | [ACL官方页面](https://github.com/acl-org/acl-style-files) |
| AAAI | `aaai2026/` | 2026 | [AAAI作者工具包](https://aaai.org/authorkit26/) |
| COLM | `colm2025/` | 2025 | [COLM官方页面](https://github.com/COLM-org/Template) |

## 使用方法

### ICML 2026

```latex
\documentclass{article}
\usepackage{icml2026}  % For submission
% \usepackage[accepted]{icml2026}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

关键文件：
- `icml2026.sty` – 样式文件
- `icml2026.bst` – 参考文献格式文件
- `example_paper.tex` – 示例文档

### ICLR 2026

```latex
\documentclass{article}
\usepackage[submission]{iclr2026_conference}  % For submission
% \usepackage[final]{iclr2026_conference}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

关键文件：
- `iclr2026_conference.sty` —— 样式文件
- `iclr2026_conference.bst` —— 参考文献格式文件
- `iclr2026_conference.tex` —— 示例文档

### ACL系列会议（ACL、EMNLP、NAACL）

```latex
\documentclass[11pt]{article}
\usepackage[review]{acl}  % For review
% \usepackage{acl}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

关键文件：
- `acl.sty` —— 样式文件
- `acl_natbib.bst` —— 参考文献样式文件
- `acl_latex.tex` —— 示例文档

### 2026年AAAI会议

```latex
\documentclass[letterpaper]{article}
\usepackage[submission]{aaai2026}  % For submission
% \usepackage{aaai2026}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

关键文件：
- `aaai2026.sty` - 样式文件
- `aaai2026.bst` - 参考文献格式文件

### COLM 2025

```latex
\documentclass{article}
\usepackage[submission]{colm2025_conference}  % For submission
% \usepackage[final]{colm2025_conference}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

关键文件：
- `colm2025_conference.sty` – 格式文件
- `colm2025_conference.bst` – 参考文献格式文件

## 页面限制概览

| 会议名称 | 提交版本 | 录制可用版本 | 备注 |
|----------|----------|--------------|------|
| ICML 2026 | 8页 | 9页 | 参考文献/附录数量不限 |
| ICLR 2026 | 9页 | 10页 | 参考文献/附录数量不限 |
| NeurIPS 2025 | 9页 | 9页 | 超出限制的部分需填写检查清单 |
| ACL 2025 | 8页（长文格式） | 规则因会议而异 | 参考文献/附录数量不限 |
| AAAI 2026 | 7页 | 8页 | 参考文献/附录数量不限 |
| COLM 2025 | 9页 | 10页 | 参考文献/附录数量不限 |

## 常见问题

### 编译错误

1. **缺少软件包**：需安装完整的TeX发行版（TeX Live Full或MikTeX）
2. **参考文献格式错误**：请使用提供的`.bst`文件，并通过`\bibliographystyle{}`指令进行设置
3. **字体相关警告**：需安装`cm-super`字体，或使用`\usepackage{lmodern}`指令

### 匿名处理

在提交稿件时，请确保：
- 不在`\author{}`指令中填写作者姓名
- 不包含致谢部分
- 不出现任何资助项目编号
| 使用匿名代码仓库存放稿件
| 以第三人称方式引用自己的研究成果 |

### 常用LaTeX软件包

```latex
% Recommended packages (check compatibility with venue style)
\usepackage{amsmath,amsthm,amssymb}  % Math
\usepackage{graphicx}                 % Figures
\usepackage{booktabs}                 % Tables
\usepackage{hyperref}                 % Links
\usepackage{algorithm,algorithmic}    % Algorithms
\usepackage{natbib}                   % Citations
```

## 模板更新

模板会每年进行更新。在提交之前，请务必查阅官方渠道的信息：

- ICML：https://icml.cc/
- ICLR：https://iclr.cc/
- NeurIPS：https://neurips.cc/
- ACL：https://github.com/acl-org/acl-style-files
- AAAI：https://aaai.org/
- COLM：https://colmweb.org/
