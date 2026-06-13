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

我已经将AAAI 2026的两个版本（匿名投稿版本和camera-ready版本）**完整合并**成一个统一的模板文件 `aaai2026-unified-template.tex`。

该模板包含了原始两个模板的**所有完整内容**（共886行，比原始文件更全面），包括：
- 所有格式化说明和要求
- 完整的示例代码和表格
- 图片处理指南
- 参考文献格式要求
- 所有章节和附录内容
- 版本特定的Acknowledgments部分

### 主要差异分析

通过比较原始的两个模板，我发现主要差异在于：

#### 1. 包的加载方式
- **匿名版本**: `\usepackage[submission]{aaai2026}`
- **Camera-ready版本**: `\usepackage{aaai2026}`

#### 2. 标题差异
- **匿名版本**: "AAAI Press Anonymous Submission Instructions for Authors Using LaTeX"
- **Camera-ready版本**: "AAAI Press Formatting Instructions for Authors Using LaTeX --- A Guide"

#### 3. Links环境的处理
- **匿名版本**: Links环境被注释掉，防止泄露作者身份
- **Camera-ready版本**: Links环境正常显示

#### 4. 内容部分差异
- **匿名版本**: 包含"Preparing an Anonymous Submission"部分的特殊说明
- **Camera-ready版本**: 包含完整的格式说明和版权信息

### 依赖文件检查结果

✅ **已验证并复制到主目录的文件**：

- `aaai2026.sty` - AAAI 2026 样式文件（两个版本完全相同）
- `aaai2026.bst` - 参考文献样式文件（两个版本完全相同）
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

统一模板采用了LaTeX的条件编译功能：

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

### 文件清单

当前主目录中包含以下文件：

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
`aaai2026-unified-supp.tex` 是专为AAAI 2026会议补充材料设计的统一模板，其版本切换机制与主论文模板完全一致。

#### 主要功能
- **版本切换**: 仅需修改一行代码即可在匿名投稿版本和最终定稿版本之间切换
- **补充内容支持**: 支持添加额外的实验结果、推导过程、数据集、图表、算法等内容
- **格式一致性**: 需遵循与主论文模板完全相同的格式要求
- **代码示例**: 提供算法实现、代码列表等补充材料的相关示例

#### 使用方法
操作方式与主论文模板相同，只需修改第11行即可：
```latex
% 匿名投稿版本
\def\aaaianonymous{true}

% Camera-ready版本  
% \def\aaaianonymous{true}
```

#### 补充材料内容建议
- 额外的实验结果与消融研究
- 详细的数学推导过程及证明
- 更多的图表与可视化展示
- 算法伪代码及实现细节
- 数据集描述与预处理步骤
- 超参数设置与实验配置信息
- 失败案例分析
- 计算复杂度分析

### 使用检查清单 (Usage Checklist)

#### 📋 投稿前检查清单 (Pre-Submission Checklist)

**版本设置**:
- [ ] 已设置 `\def\aaaianonymous{true}`（匿名投稿模式）
- [ ] 已注释掉所有可能暴露作者身份的信息
- [ ] 已对参考文献进行匿名化处理（移除作者姓名）

**内容完整性**:
- [ ] 标题、摘要及关键词已完整填写
- [ ] 所有章节的内容均完整无缺
- [ ] 图表编号连续且格式正确
- [ ] 参考文献的格式符合规范
- [ ] 补充材料（如有）已准备好

**格式检查**:
- [ ] 页面边距符合要求
- [ ] 字体及字号设置正确
- [ ] 行间距符合标准规范
- [ ] 图表的位置与大小适宜
- [ ] 数学公式的格式正确无误

**技术检查**:
- [ ] LaTeX编译过程无错误
- [ ] 参考文献已正确生成
- [ ] PDF输出文件正常
- [ ] 文件大小处于规定范围内

#### 📋 录用后检查清单 (Post-Acceptance Checklist)

**版本切换**:
- [ ] 已注释掉 `\def\aaaianonymous{true}`（准备正式发表版本）
- [ ] 已添加完整的作者信息
- [ ] 已补充所有作者的所属单位信息
- [ ] 已恢复所有之前被注释的内容

**内容更新**:
- [ ] 已根据审稿人的意见对内容进行修改
- [ ] 已更新所有的图表与实验相关内容
- [ ] 已进一步完善补充材料
- [ ] 已逐一检查所有链接与引用

**最终检查**:
- [ ] 对最终生成的PDF文件进行质量检查
- [ ] 已备份所有相关文件
- [ ] 确保符合会议的最终提交要求
- [ ] 如有需要，已单独提交补充材料

#### 📋 补充材料检查清单 (Supplementary Material Checklist)

**内容组织**:
- [ ] 补充材料与主论文的内容相互对应
- [ ] 章节结构清晰且合理
- [ ] 图表编号与主论文中的编号不冲突
- [ ] 参考文献的格式保持一致

**技术细节**:
- [ ] 算法伪代码清晰完整
- [ ] 实验设置有详细说明
- [ ] 数据预处理步骤明确具体
- [ ] 超参数配置完整准确

**格式要求**:
- [ ] 使用统一的补充材料模板
- [ ] 页面设置与主论文保持一致
- [ ] 字体及格式符合规范要求
- [ ] 文件大小处于规定范围内

### 实际使用建议

1. **投稿阶段**: 
   - 取消注释 `\def\aaaianonymous{true}` 
   - 确保文档中不包含任何可能暴露作者身份的信息
   - 检查参考文献是否已完成匿名化处理

2. **录用后准备final版本**:
   - 注释掉或删除 `\def\aaaianonymous{true}` 这一行代码
   - 添加完整的作者信息及所属机构信息
   - 如有需要，取消注释links环境设置

3. **编译测试**:
   - 在两种不同的模式下分别进行编译，确保两种模式下都能正常生成文档
   - 检查生成的PDF文件是否符合要求
   - 验证参考文献的格式是否正确

4. **依赖文件确认**:
   - 确保所有依赖文件都保存在同一个目录下
   - 如果需要移动模板文件，务必同时移动相关的依赖文件

### 重要注意事项

⚠️ **关于Bibliography Style**:
- `aaai2026.sty`文件已自动设置了`\bibliographystyle{aaai2026}`指令
- **请勿**在文档中再次添加`\bibliographystyle{aaai2026}`命令
- 否则将会出现"`Illegal, another \bibstyle command`"的错误提示
- 只需要使用`\bibliography{aaai2026}`命令即可

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
**原因**: 重复设置了参考文献格式样式  
**解决方案**: 删除文档中的`\bibliographystyle{aaai2026}`命令，`aaai2026.sty`文件会自动处理相关设置。

#### 2. 参考文献格式不正确
**原因**: 可能缺少natbib包或BibTeX文件存在问题  
**解决方案**: 确保按照标准的LaTeX编译流程操作：pdflatex → bibtex → pdflatex → pdflatex

---

## 英文版本

### 概述 ✅

我已将AIAI 2026会议的两种版本（匿名投稿版和可直接提交版）**完全合并**为一个统一的模板文件`aaai2026-unified-template.tex`。

该模板包含了原两个模板中的**所有完整内容**（总计886行，比原始文件更为全面），包括：
- 所有的格式说明与要求
- 完整的示例代码和表格
- 图像处理相关指南
- 参考文献格式要求
- 所有章节及附录内容
- 不同版本特有的致谢部分

### 主要差异分析

通过对比两个原始模板，主要差异如下：

#### 1. 包加载方式
- **匿名投稿版**：使用`\usepackage[submission]{aaai2026}`命令
- **可直接提交版**：直接使用`\usepackage{aaai2026}`命令

#### 2. 标题差异
- **匿名投稿版**：标题为“AAAI Press Anonymous Submission Instructions for Authors Using LaTeX”
- **可直接提交版**：标题为“AAAI Press Formatting Instructions for Authors Using LaTeX --- A Guide”

#### 3. 链接环境处理方式
- **匿名投稿版**：为防止身份泄露，链接环境被注释掉
- **可直接提交版**：链接环境可正常显示

#### 4. 内容章节差异
- **匿名投稿版**：“准备匿名投稿”章节包含特殊说明
- **可直接提交版**：包含完整的格式说明及版权信息

### 依赖文件验证

✅ **已验证并复制到主目录的文件**包括：
- `aaai2026.sty` - AIAI 2026格式样式文件（两个版本内容相同）
- `aaai2026.bst` - 参考文献格式文件（两个版本内容相同）
- `aaai2026.bib` - 示例参考文献文件
- `figure1.pdf`和`figure2.pdf` - 示例图像文件

由于这些文件在两个版本中完全一致，因此统一模板可以正常使用。

### 如何使用统一模板

#### 切换到匿名投稿版本
在模板文件的第11行，**取消注释**该行即可：
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
- `aaai2026.sty` - AAAI 2026 LaTeX样式文件  
- `aaai2026.bst` - 参考文献样式文件  
- `aaai2026.bib` - 示例参考文献文件  
- `figure1.pdf` - 示例图片1  
- `figure2.pdf` - 示例图片2  
- `README.md` - 本文档  

### 补充材料模板

#### 概述
`aaai2026-unified-supp.tex`是专为A AAAI 2026补充材料设计的统一模板，采用与主论文模板相同的版本切换机制。

#### 主要特性
- **版本切换**：只需修改一行代码即可在这两种版本之间切换  
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
- [ ] 填写标题、摘要及关键词
- [ ] 所有章节均已完整
- [ ] 图表编号连续且正确
- [ ] 参考文献格式正确
- [ ] 已准备好补充材料（如有）

**格式检查**：
- [ ] 页面边距符合要求
- [ ] 字体及字体大小正确
- [ ] 行间距符合标准
- [ ] 图表的位置与尺寸适当
- [ ] 数学公式格式正确

**技术检查**：
- [ ] LaTeX编译无错误
- [ ] 参考文献生成正确
- [ ] PDF输出正常
- [ ] 文件大小在限制范围内

#### 📋 录用后检查清单

**版本切换**：
- [ ] 将 `\def\aaaianonymous{true}` 注释掉（准备发表版本）
- [ ] 添加完整的作者信息
- [ ] 添加所有作者的所属机构信息
- [ ] 恢复所有被注释的内容

**内容更新**：
- [ ] 根据审稿人意见修改内容
- [ ] 更新所有图表与实验内容
- [ ] 完成补充材料的编写
- [ ] 检查所有链接与引用

**最终检查**：
- [ ] 检查最终PDF的质量
- [ ] 备份所有文件
- [ ] 确保符合会议的最终提交要求
- [ ] 如有需要，单独提交补充材料

#### 📋 补充材料检查清单

**内容组织**：
- [ ] 补充材料与主论文内容对应
- [ ] 章节结构清晰合理
- [ ] 图表编号与主论文无冲突
- [ ] 参考文献格式一致

**技术细节**：
- [ ] 算法伪代码清晰完整
- [ ] 实验设置说明详尽
- [ ] 数据预处理步骤明确
- [ ] 超参数配置完整

**格式要求**：
- [ ] 使用统一的补充材料模板
- [ ] 页面设置与主论文一致
- [ ] 字体及格式符合要求
- [ ] 文件大小在限制范围内

### 实际使用建议

1. **提交阶段**：
   - 取消注释 `\def\aaaianonymous{true}` 
   - 确保不包含任何可能暴露身份的信息
   - 检查参考文献是否已进行匿名处理

2. **录用后准备最终版本**：
   - 将 `\def\aaaianonymous{true}` 这一行注释掉或删除
   - 添加完整的作者信息及所属机构
   - 如有需要，取消注释链接相关设置

3. **编译测试**：
   - 以两种模式分别进行编译，确保功能正常
   - 检查生成的PDF是否符合要求
   - 验证参考文献格式是否正确

4. **依赖文件确认**：
   - 确保所有依赖文件都在同一目录下
   - 移动模板文件时别忘了一同移动依赖文件

### 重要注意事项

⚠️ **关于参考文献样式**：
- `aaai2026.sty` 文件会自动设置 `\bibliographystyle{aaai2026}`
- **请勿**在文档中再次添加 `\bibliographystyle{aaai2026}` 命令
- 否则会出现“`Illegal, another \bibstyle command`”错误
- 仅需使用 `\bibliography{aaai2026}` 命令即可

### 编译命令示例

```bash
# Compile LaTeX document
pdflatex aaai2026-unified-template.tex
bibtex aaai2026-unified-template
pdflatex aaai2026-unified-template.tex
pdflatex aaai2026-unified-template.tex
```

### 常见问题与解决方案

#### 1. “非法指令：另一个 \bibstyle 命令”错误
**原因**：参考文献样式设置重复  
**解决方案**：从文档中删除 `\bibliographystyle{aaai2026}` 这一行命令，`aaai2026.sty` 文件会自动处理该设置。

#### 2. 参考文献格式错误
**原因**：未安装 natbib 包或 BibTeX 文件存在问题  
**解决方案**：按照标准的 LaTeX 编译流程操作：pdflatex → bibtex → pdflatex → pdflatex

---

## 版本信息 / Version Information

- **模板版本 / Template Version**：AAAI 2026 统一版（主论文 + 补充材料）  
- **创建日期 / Created**：2024年12月  
- **支持格式 / Supported Formats**：匿名投稿版与可直接用于展示的版本  
- **模板类型 / Template Types**：主论文模板与补充材料模板  
- **兼容性 / Compatibility**：LaTeX 2020+ / TeXLive 2024+

---

🎉 **现在您只需修改一行代码就可以在两个版本之间切换，同时所有必要的依赖文件都已经准备就绪！**  
🎉 **现在您只需修改一行代码即可在这两个版本间切换，所有必需的依赖文件也已准备就绪！**