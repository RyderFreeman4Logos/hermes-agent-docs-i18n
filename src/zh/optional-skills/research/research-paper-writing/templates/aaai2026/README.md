# AAAI 2026 统一LaTeX模板使用说明 / AAAI 2026 Unified LaTeX Template Guide

> **📝 重要说明 / Important Notice**: 本仓库借助Cursor在AAAI 2026官方模板基础上改进得到。如果遇到不满足或有冲突的情况，请积极提issues。
> 
> **📝 Important Notice**: This repository is improved based on the official AAAI 2026 template with the assistance of Cursor. If you encounter any issues or conflicts, please actively submit issues.

[中文](#中文版本) | [English](#english-version)

---

## 🌐 在线查看 / Online Access

**📖 在线阅读和测试模板**: [https://cn.overleaf.com/read/wyhcnvcrtpyt#cd4a07](https://cn.overleaf.com/read/wyhcnvcrtpyt#cd4a07)

**📖 Online View and Test Template**: [https://cn.overleaf.com/read/wyhcnvcrtpyt#cd4a07](https://cn.overleaf.com/read/wyhcnvcrtpyt#cd4a07)

💡 **提示 / Tips**: 
- 中文：您可以通过上述链接在Overleaf中直接查看、编辑和编译模板，无需本地安装LaTeX环境
- English: You can view, edit, and compile the template directly in Overleaf using the link above, without needing a local LaTeX installation

---

## 中文版本

### 概述 ✅

我已将AAAI 2026的两种版本（匿名投稿版本和可直接投稿版本）**完整整合**为一个统一的模板文件 `aaai2026-unified-template.tex`。

该模板包含了原始两个模板的**所有完整内容**（共886行，比原始文件更全面），包括：
- 所有格式化说明和要求
- 完整的示例代码和表格
- 图片处理指南
- 参考文献格式要求
- 所有章节和附录内容
- 版本特定的Acknowledgments部分

### 主要差异分析

通过比较原始的两个模板，我发现主要差异在于：

#### 1. 宏包的加载方式
- **匿名版本**：`\usepackage[submission]{aaai2026}`
- **可直接投稿版本**：`\usepackage{aaai2026}`

#### 2. 标题差异
- **匿名版本**：「AAAI Press Anonymous Submission Instructions for Authors Using LaTeX」
- **可直接投稿版本**：「AAAI Press Formatting Instructions for Authors Using LaTeX --- A Guide」

#### 3. Links环境的处理方式
- **匿名版本**：Links环境会被注释掉，以避免泄露作者身份信息
- **可直接投稿版本**：Links环境会正常显示

#### 4. 正文部分的差异
- **匿名版本**：包含“Preparing an Anonymous Submission”章节中的特殊说明
- **可直接投稿版本**：包含完整的格式规范说明及版权信息

### 依赖文件检查结果

✅ **已验证并复制到主目录的文件**：

- `aaai2026.sty` - AAAI 2026 格式文件（两个版本内容完全相同）  
- `aaai2026.bst` - 参考文献格式文件（两个版本内容完全相同）  
- `aaai2026.bib` - 示例参考文献文件  
- `figure1.pdf` 和 `figure2.pdf` - 示例图片文件

所有这些文件在两个版本中都是相同的，因此统一模板可以正常工作。

### 如何使用统一模板

#### 切换到匿名投稿版本
在模板文件第11行，**取消注释**这一行：
```latex
\def\aaaianonymous{true}
```

#### 切换到Camera-ready版本
在模板文件的第11行，**注释掉**或**删除**这一行：
```latex
% \def\aaaianonymous{true}
```

### 一键切换的核心机制

统一模板使用了LaTeX的条件编译功能：

```latex
% 条件包加载
\ifdefined\aaaianonymous
    \usepackage[submission]{aaai2026}  % 匿名版本
\else
    \usepackage{aaai2026}              % Camera-ready版本
\fi

% 条件标题设置
\ifdefined\aaaianonymous
    \title{AAAI Press Anonymous Submission\\Instructions for Authors Using \LaTeX{}}
\else
    \title{AAAI Press Formatting Instructions \\for Authors Using \LaTeX{} --- A Guide}
\fi

% 条件内容显示
\ifdefined\aaaianonymous
    % 匿名版本特有内容
\else
    % Camera-ready版本特有内容
\fi
```

### 文件列表

主目录现在包含以下文件：

- `aaai2026-unified-template.tex` - 统一主论文模板文件  
- `aaai2026-unified-supp.tex` - 统一补充材料模板文件  
- `aaai2026.sty` - AAAI 2026 LaTeX 样式文件  
- `aaai2026.bst` - 参考文献样式文件  
- `aaai2026.bib` - 示例参考文献文件  
- `figure1.pdf` - 示例图片1  
- `figure2.pdf` - 示例图片2  
- `README.md` - 本说明文档  

### 补充材料模板 (Supplementary Material Template)

#### 概述
`aaai2026-unified-supp.tex` 是专为AAAI 2026的补充材料设计的统一模板，其版本切换机制与主论文模板保持一致。

#### 主要功能
- **版本切换**: 通过修改一行代码在匿名投稿和camera-ready版本间切换
- **补充内容支持**: 支持额外的实验、推导、数据、图表、算法等
- **格式一致性**: 与主论文模板保持完全一致的格式要求
- **代码示例**: 包含算法、代码列表等补充材料的示例

#### 使用方法
与主论文模板相同，只需修改第11行：
```latex
% 匿名投稿版本
\def\aaaianonymous{true}

% Camera-ready版本  
% \def\aaaianonymous{true}
```

#### 补充材料内容建议
- 额外的实验结果和消融研究
- 详细的数学推导和证明
- 更多的图表和可视化
- 算法伪代码和实现细节
- 数据集描述和预处理步骤
- 超参数设置和实验配置
- 失败案例分析
- 计算复杂度分析

### 使用检查清单 (Usage Checklist)

#### 📋 投稿前检查清单 (Pre-Submission Checklist)

**版本设置**:
- [ ] 已设置 `\def\aaaianonymous{true}`（启用匿名投稿模式）
- [ ] 已注释掉所有可能暴露身份的信息
- [ ] 已对参考文献进行匿名处理（已移除作者姓名）

**内容完整性**:
- [ ] 标题、摘要、关键词已填写
- [ ] 所有章节内容完整
- [ ] 图表编号连续且正确
- [ ] 参考文献格式正确
- [ ] 补充材料（如有）已准备

**格式检查**:
- [ ] 页面边距符合要求
- [ ] 字体和字号正确
- [ ] 行间距符合标准
- [ ] 图表位置和大小合适
- [ ] 数学公式格式正确

**技术检查**：
- [ ] LaTeX编译无错误
- [ ] 参考文献已正确生成
- [ ] PDF输出正常
- [ ] 文件大小处于规定范围内

#### 📋 录用后检查清单 (Post-Acceptance Checklist)

**版本切换**：
- [ ] 已注释掉 `\def\aaaianonymous{true}`（适用于直接投稿版本）
- [ ] 已添加完整的作者信息
- [ ] 已补充所有作者所在单位的信息
- [ ] 已恢复所有被注释掉的代码内容

**内容更新**:
- [ ] 已根据审稿意见修改内容
- [ ] 已更新所有图表和实验
- [ ] 已完善补充材料
- [ ] 已检查所有链接和引用

**最终检查**:
- [ ] 最终PDF质量检查
- [ ] 所有文件已备份
- [ ] 符合会议最终提交要求
- [ ] 补充材料已单独提交（如需要）

#### 📋 补充材料检查清单 (Supplementary Material Checklist)

**内容组织**:
- [ ] 补充材料与主论文内容对应
- [ ] 章节结构清晰合理
- [ ] 图表编号与主论文不冲突
- [ ] 参考文献格式一致

**技术细节**:
- [ ] 算法伪代码清晰完整
- [ ] 实验设置详细说明
- [ ] 数据预处理步骤明确
- [ ] 超参数配置完整

**格式要求**:
- [ ] 使用统一的supp模板
- [ ] 页面设置与主论文一致
- [ ] 字体和格式符合要求
- [ ] 文件大小在限制范围内

### 实际使用建议

1. **投稿阶段**：  
   - 取消对`\def\aaaianonymous{true}`的注释  
   - 确保稿件中不包含任何可能暴露作者身份的信息  
   - 检查参考文献是否已进行匿名处理  

2. **文章被录用后准备最终版本**：  
   - 对`\def\aaaianonymous{true}`这一行进行注释处理或直接删除  
   - 添加完整的作者信息及所属机构信息  
   - 如有需要，取消对links环境的注释

3. **编译测试**:
   - 分别在两种模式下编译，确保都能正常工作
   - 检查输出的PDF是否符合要求
   - 验证参考文献格式是否正确

4. **依赖文件确认**:
   - 确保所有依赖文件都在同一目录下
   - 如果移动模板文件，记得同时移动依赖文件

### 重要注意事项

⚠️ **关于参考文献样式**：
- `aaai2026.sty`文件已自动设置了`\bibliographystyle{aaai2026}`指令
- **请勿**在文档中再次添加`\bibliographystyle{aaai2026}`命令
- 否则将会出现“`Illegal, another \bibstyle command`”的错误提示
- 仅需使用`\bibliography{aaai2026}`指令即可

### 编译命令示例

```bash
# 编译LaTeX文档
pdflatex aaai2026-unified-template.tex
bibtex aaai2026-unified-template
pdflatex aaai2026-unified-template.tex
pdflatex aaai2026-unified-template.tex
```

### 常见问题解决

#### 1. “Illegal, another \bibstyle command”错误
**原因**: 重复设置了参考文献格式  
**解决方案**: 删除文档中的`\bibliographystyle{aaai2026}`命令，`aaai2026.sty`文件会自动处理相关设置。

#### 2. 参考文献格式不正确
**原因**: 可能缺少natbib包或BibTeX文件存在问题  
**解决方案**: 确保按照标准的LaTeX编译流程操作：pdflatex → bibtex → pdflatex → pdflatex

---

## 英文版本

### 概述 ✅

我已将两个AAAI 2026版本的模板（匿名投稿版和可直接投稿版）**完全合并**为一个统一的模板文件`aaai2026-unified-template.tex`。

该模板包含了原两个模板中的**所有内容**（总计886行，内容比原始文件更为完整），包括：
- 所有的格式要求与规范
- 完整的示例代码与表格
- 图像处理相关指南
- 参考文献的格式要求
- 所有章节及附录内容
- 针对不同版本的致谢部分

### 主要差异分析

通过对比两个原始模板，其主要差异如下：

#### 1. 包加载方式
- **匿名投稿版**: `\usepackage[submission]{aaai2026}`
- **可直接投稿版**: `\usepackage{aaai2026}`

#### 2. 标题差异
- **匿名投稿版**: “AAAI Press Anonymous Submission Instructions for Authors Using LaTeX”
- **可直接投稿版**: “AAAI Press Formatting Instructions for Authors Using LaTeX --- A Guide”

#### 3. 链接环境处理方式
- **匿名版本**：为防止泄露身份，相关环境链接已被注释掉  
- **可直接提交版本**：环境链接会正常显示  

#### 4. 内容部分的差异  
- **匿名版本**：“准备匿名提交”部分包含特殊说明  
- **可直接提交版本**：包含完整的格式规范及版权信息  

### 依赖文件验证

✅ **已验证并复制到主目录的文件**：  

- `aaai2026.sty` - AAAI 2026格式文件（两个版本内容完全一致）  
- `aaai2026.bst` - 参考文献格式文件（两个版本内容完全一致）  
- `aaai2026.bib` - 示例参考文献文件  
- `figure1.pdf` 和 `figure2.pdf` - 示例图片文件  

所有这些文件在两个版本中均保持一致，因此统一模板可以正常使用。  

### 如何使用统一模板

#### 切换到匿名提交版本  
在模板文件的第11行，**取消注释**该行：
```latex
\def\aaaianonymous{true}
```

#### 切换到可直接用于拍摄的版本
在模板文件的第11行，**注释掉**或**删除**该行内容：
```latex
% \def\aaaianonymous{true}
```

### 一键切换的核心机制

该统一模板采用了LaTeX条件编译技术：

```latex
% Conditional package loading
\ifdefined\aaaianonymous
    \usepackage[submission]{aaai2026}  % Anonymous version
\else
    \usepackage{aaai2026}              % Camera-ready version
\fi

% Conditional title setting
\ifdefined\aaaianonymous
    \title{AAAI Press Anonymous Submission\\Instructions for Authors Using \LaTeX{}}
\else
    \title{AAAI Press Formatting Instructions \\for Authors Using \LaTeX{} --- A Guide}
\fi

% Conditional content display
\ifdefined\aaaianonymous
    % Anonymous version specific content
\else
    % Camera-ready version specific content
\fi
```

### 文件列表

当前主目录中包含以下文件：

- `aaai2026-unified-template.tex` - 统一的主论文模板文件  
- `aaai2026-unified-supp.tex` - 统一的补充材料模板文件  
- `aaai2026.sty` - AAAI 2026 LaTeX格式文件  
- `aaai2026.bst` - 参考文献格式文件  
- `aaai2026.bib` - 示例参考文献文件  
- `figure1.pdf` - 示例图片1  
- `figure2.pdf` - 示例图片2  
- `README.md` - 本文档  

### 补充材料模板

#### 概述
`aaai2026-unified-supp.tex` 是专为AIAI 2026会议补充材料设计的统一模板，采用与主论文模板相同的版本切换机制。

#### 主要特性
- **版本切换**：通过修改一行代码即可在匿名提交版本和最终定稿版本之间切换  
- **补充内容支持**：可容纳额外的实验结果、推导过程、数据、图表、算法等内容  
- **格式一致性**：与主论文模板保持完全一致的格式  
- **代码示例**：提供算法、代码片段及其他补充材料的示例  

#### 使用方法
与主论文模板相同，只需修改第11行即可：
```latex
% Anonymous submission version
\def\aaaianonymous{true}

% Camera-ready version
% \def\aaaianonymous{true}
```

#### 补充材料内容建议
- 额外的实验结果与消融研究
- 详细的数学推导与证明
- 更多的图表与可视化内容
- 算法伪代码及实现细节
- 数据集描述与预处理步骤
- 超参数设置与实验配置
- 失败案例分析
- 计算复杂度分析

### 使用检查清单

#### 📋 提交前检查清单

**版本设置**：
- [ ] 设置 `\def\aaaianonymous{true}`（匿名提交）
- [ ] 将所有可能暴露身份的信息注释掉
- [ ] 对参考文献进行匿名处理（删除作者姓名）

**内容完整性**：
- [ ] 已填写标题、摘要及关键词
- [ ] 所有章节均已完整填写
- [ ] 图表编号连续且正确
- [ ] 参考文献格式正确
- [ ] 已准备好补充材料（如有）

**格式检查**：
- [ ] 页面边距符合要求
- [ ] 字体及字体大小正确
- [ ] 行间距符合标准
- [ ] 图表的位置与大小恰当
- [ ] 数学公式格式正确

**技术检查**：
- [ ] LaTeX编译无错误
- [ ] 参考文献生成正确
- [ ] PDF输出正常
- [ ] 文件大小在限制范围内

#### 📋 录用后检查清单

**版本切换**：
- [ ] 取消注释 `\def\aaaianonymous{true}`（准备发表版本）
- [ ] 添加完整的作者信息
- [ ] 添加所有作者的所属机构信息
- [ ] 恢复所有被注释的内容

**内容更新**：
- [ ] 根据审稿人意见修改内容  
- [ ] 更新所有图表与实验部分  
- [ ] 完成补充材料编写  
- [ ] 检查所有链接与引用格式  

**最终检查**：  
- [ ] 进行PDF最终质量检测  
- [ ] 备份所有文件  
- [ ] 确保符合会议最终提交要求  
- [ ] 如有需要，单独提交补充材料  

#### 📋 补充材料核对清单  

**内容组织**：  
- [ ] 补充材料与主论文内容对应一致  
- [ ] 章节结构清晰合理  
- [ ] 图表编号与主论文无冲突  
- [ ] 参考文献格式统一  

**技术细节**：  
- [ ] 算法伪代码清晰完整  
- [ ] 详细说明实验设置  
- [ ] 数据预处理步骤表述清晰  
- [ ] 超参数配置齐全  

**格式要求**：  
- [ ] 使用统一的补充材料模板  
- [ ] 页面设置与主论文保持一致  
- [ ] 字体及排版符合规范  
- [ ] 文件大小在允许范围内  

### 实际使用建议

1. **提交阶段**：  
   - 取消注释 `\def\aaaianonymous{true}`  
   - 确保不包含任何可能暴露身份的信息  
   - 检查参考文献是否已进行匿名处理  

2. **通过审核后准备最终版本**：  
   - 将 `\def\aaaianonymous{true}` 这一行注释掉或删除  
   - 添加完整的作者信息及所属机构  
   - 如有需要，取消注释用于链接的环境设置  

3. **编译测试**：  
   - 以两种模式分别进行编译，以确保功能正常  
   - 检查生成的 PDF 是否符合要求  
   - 验证参考文献的格式是否正确  

4. **依赖文件确认**：  
   - 确保所有依赖文件都位于同一目录下  
   - 移动模板文件时别忘了一同移动这些依赖文件  

### 重要注意事项  

⚠️ **关于参考文献样式**：  
- `aaai2026.sty` 文件会自动设置 `\bibliographystyle{aaai2026}`  
- **切勿**在文档中再次添加 `\bibliographystyle{aaai2026}` 命令  
- 否则会出现“`Illegal, another \bibstyle command`”的错误  
- 请直接使用 `\bibliography{aaai2026}` 命令即可  

### 编译命令示例

```bash
# Compile LaTeX document
pdflatex aaai2026-unified-template.tex
bibtex aaai2026-unified-template
pdflatex aaai2026-unified-template.tex
pdflatex aaai2026-unified-template.tex
```

### 常见问题与解决方案

#### 1. “非法操作：另一个 \bibstyle 命令”错误
**原因**： bibliography 样式设置重复  
**解决方案**：从文档中删除 `\bibliographystyle{aaai2026}` 命令，该命令可由 `aaai2026.sty` 文件自动处理

#### 2. 参考文献格式错误
**原因**：缺少 natbib 包或 BibTeX 文件存在问题  
**解决方案**：按照标准的 LaTeX 编译流程操作：pdflatex → bibtex → pdflatex → pdflatex

---

## 版本信息 / Version Information

- **模板版本 / Template Version**：AAAI 2026 统一版（主论文 + 补充材料）  
- **创建日期 / Created**：2024年12月  
- **支持格式 / Supported Formats**：匿名投稿版与可直接用于演示的版本  
- **模板类型 / Template Types**：主论文模板与补充材料模板  
- **兼容性 / Compatibility**：LaTeX 2020+ / TeXLive 2024+

---

🎉 **现在您只需修改一行代码就可以在两个版本之间切换，同时所有必要的依赖文件都已经准备就绪！**  
🎉 **现在您仅需修改一行代码即可在这两个版本间切换，所有必需的依赖文件也已准备妥当！**