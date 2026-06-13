---
title: "Bioinformatics — Gateway to 400+ bioinformatics skills from bioSkills and ClawBio"
sidebar_label: "Bioinformatics"
description: "Gateway to 400+ bioinformatics skills from bioSkills and ClawBio"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 生物信息学

汇集了来自 bioSkills 和 ClawBio 的 400 多项生物信息学技能的入口。涵盖基因组学、转录组学、单细胞分析、变异检测、药物基因组学、宏基因组学、结构生物学等多个领域，并可按需获取特定领域的参考资料。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/bioinformatics` 安装 |
| 路径 | `optional-skills/research/bioinformatics` |
| 版本 | `1.0.0` |
| 支持平台 | linux、macos |
| 标签 | `bioinformatics`、`genomics`、`sequencing`、`biology`、`research`、`science` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，智能体将以此作为操作指南。
:::

# 生物信息学技能入口

当被询问有关生物信息学、基因组学、测序技术、变异检测、基因表达、单细胞分析、蛋白质结构、药物基因组学、宏基因组学、系统发育学或任何计算生物学任务的问题时，可使用此技能。

该技能是两个开源生物信息学技能库的入口。它不会直接整合数百项特定领域的技能，而是对它们进行索引，以便按需调用所需功能。

## 资源来源

◆ **bioSkills** — 385 项参考技能（代码模板、参数指南、决策树）
  仓库地址：https://github.com/GPTomics/bioSkills
  格式：每个主题对应一个包含代码示例的 SKILL.md 文件，支持 Python/R/CLI 语言。

◆ **ClawBio** — 33 个可运行的流程技能（可执行脚本、可复现性包）
  仓库地址：https://github.com/ClawBio/ClawBio
  格式：附带演示示例的 Python 脚本。每次分析都会生成 report.md、commands.sh 和 environment.yml 文件。

## 如何获取并使用技能

1. 从下方的索引中确定所属领域及技能名称。
2. 克隆相应的仓库（建议使用浅克隆以节省时间）：
   ```bash
   # bioSkills (reference material)
   git clone --depth 1 https://github.com/GPTomics/bioSkills.git /tmp/bioSkills

   # ClawBio (runnable pipelines)
   git clone --depth 1 https://github.com/ClawBio/ClawBio.git /tmp/ClawBio
   ```
3. 查阅对应的特定技能信息：
   ```bash
   # bioSkills — each skill is at: <category>/<skill-name>/SKILL.md
   cat /tmp/bioSkills/variant-calling/gatk-variant-calling/SKILL.md

   # ClawBio — each skill is at: skills/<skill-name>/
   cat /tmp/ClawBio/skills/pharmgx-reporter/README.md
   ```
4. 请以获取的技能文档作为参考资料。这些并非Hermes格式的技能——应将其视为各领域的专家指南。它们包含了正确的参数、合适的工具标志以及经过验证的流程。

## 按领域划分的技能索引

### 序列处理基础
bioSkills:
  sequence-io/ — 序列读取、序列写入、格式转换、批量处理、压缩文件处理、FastQ质量检测、序列过滤、双端FastQ处理、序列统计
  sequence-manipulation/ — 序列对象操作、反向互补、转录翻译、基序搜索、密码子使用频率分析、序列属性分析、序列切片
ClawBio:
  seq-wrangler — 序列质量检测、比对及BAM文件处理（封装了FastQC、BWA、SAMtools工具）

### 测序读段质量检测与比对
bioSkills:
  read-qc/ — 质量报告生成、fastp工作流程、接头去除、质量过滤、UMI处理、污染检测、RNA-seq质量检测
  read-alignment/ — BWA比对、STAR比对、Hisat2比对、Bowtie2比对
  alignment-files/ — SAM/BAM基础操作、比对排序、比对过滤、BAM统计分析、重复数据处理、重叠图生成

### 变异调用与注释
bioSkills:
  variant-calling/ — GATK变异调用、DeepVariant、BCFTools变异调用、联合变异调用、结构变异调用、最佳实践过滤、变异注释、变异标准化、VCF基础操作、VCF文件处理、VCF统计分析、共识序列生成、临床意义解读
ClawBio:
  vcf-annotator — 结合VEP、ClinVar及gnomAD的注释功能，并具备祖先背景信息分析能力
  variant-annotation — 变异注释流程

### 差异表达分析（批量RNA-seq）
bioSkills:
  differential-expression/ — DESeq2基础操作、EdgeR基础操作、批次效应校正、差异分析结果生成、结果可视化、时间序列差异分析
  rna-quantification/ — 无需比对的定量分析（Salmon/kallisto）、featureCounts计数、tximport工作流程、计数矩阵质量检测
  expression-matrix/ — 计数数据导入、基因ID映射、元数据关联、稀疏数据处理
ClawBio:
  rnaseq-de — 完整的差异表达分析流程，包含质量检测、标准化及可视化功能
  diff-visualizer — 为差异表达结果提供丰富的可视化展示与报告功能

### 单细胞RNA-seq
bioSkills:
  single-cell/ — 数据预处理、聚类分析、批次整合、细胞注释、细胞间通讯分析、双细胞检测、标记物注释、轨迹推断、多模态数据整合、Perturb-Seq分析、SCATAC分析、谱系追踪、代谢物通讯分析、数据输入输出
ClawBio:
  scrna-orchestrator — 完整的Scanpy分析流程（包含质量检测、聚类、标记物识别及注释功能）
  scrna-embedding — 基于scVI的潜在特征嵌入与批次整合技术

### 空间转录组学
bioSkills:
  spatial-transcriptomics/ — 空间数据输入输出、空间数据预处理、空间域定义、空间去卷积、空间通讯分析、空间邻居关系分析、空间统计分析、空间可视化、空间多组学整合、空间蛋白质组学、图像分析
### 表观基因组学
bioSkills:
  chip-seq/ — 峰值调用、差异结合分析、基序分析、峰值注释、芯片测序质量检测、芯片测序结果可视化、超级增强子识别
  atac-seq/ — ATAC峰值调用、ATAC质量检测、可及性差异分析、足迹图生成、基序偏差分析、核小体定位分析
  methylation-analysis/ — Bismark比对、甲基化调用、DNA甲基化区域检测、MethylKit分析
  hi-c-analysis/ — Hi-C数据输入输出、TAD结构检测、环结构识别、区室分析、接触对分析、矩阵运算、Hi-C结果可视化、Hi-C差异分析
ClawBio:
  methylation-clock — 表观遗传年龄估算工具

### 药物基因组学与临床应用
bioSkills:
  clinical-databases/ — ClinVar数据库查询、gnomAD频率数据查询、DBSNP数据库查询、药物基因组学分析、多基因风险评分、HLA分型、变异优先级排序、体细胞特征分析、肿瘤突变负荷分析、MyVariant数据库查询
ClawBio:
  pharmgx-reporter — 基于23andMe/AncestryDNA数据的PGx报告生成（涵盖12个基因、31个SNP及51种药物）
  drug-photo — 通过图像识别技术将药物照片转换为个性化PGx剂量卡
  clinpgx — 提供基因-药物数据及CPIC指南的ClinPGx API接口
  gwas-lookup — 跨9个基因组数据库的联合变异查询功能
  gwas-prs — 基于消费者遗传数据的多基因风险评分计算
  nutrigx_advisor — 基于消费者遗传数据的个性化营养建议生成

### 种群遗传学与全基因组关联分析
bioSkills:
  population-genetics/ — 关联分析（PLINK GWAS）、PLINK基础操作、群体结构分析、连锁不平衡分析、ScikitAllele分析、选择统计分析
  causal-genomics/ — 孟德尔随机化分析、精细定位分析、共定位分析、中介效应分析、多效性检测
  phasing-imputation/ — 单倍型分型、基因型推断、推断结果质量检测、参考面板构建
ClawBio:
  claw-ancestry-pca — 基于SGDP参考面板的祖先信息PCA分析

### 元基因组学与微生物组学
bioSkills:
  metagenomics/ — Kraken分类分析、Metaphlan功能谱分析、丰度估算、功能特征分析、耐药基因检测、菌株追踪、元基因组可视化
  microbiome/ — 扩增子处理、多样性分析、差异丰度分析、分类学鉴定、功能预测、Qiime2工作流程
ClawBio:
  claw-metagenomics — 基于Shotgun技术的元基因组分析（涵盖分类学、耐药基因组及功能通路分析）

### 基因组组装与注释
bioSkills:
  genome-assembly/ — HIFI组装、长读长序列组装、短读长序列组装、元基因组组装、组装优化、组装质量检测、支架构建、污染检测
  genome-annotation/ — 真核生物基因预测、原核生物注释、功能注释、非编码RNA注释、重复序列注释、注释信息传递
  long-read-sequencing/ — 基序调用、长读长序列比对、长读长序列质量检测、Clair3变异识别、结构变异分析、Medaka组装优化、纳米孔测序甲基化分析、Isoseq分析
### 结构生物学与化学信息学
bioSkills:
  structural-biology/ — AlphaFold预测、现代结构预测、结构数据输入输出、结构导航、结构修饰、几何结构分析
  chemoinformatics/ — 分子数据输入输出、分子描述符生成、相似性搜索、子结构搜索、虚拟筛选、ADMET性质预测、反应路径枚举
ClawBio:
  struct-predictor — 支持局部AlphaFold/Boltz/Chai结构预测并具备结果对比功能

### 蛋白组学
bioSkills:
  proteomics/ — 数据导入、肽段识别、蛋白质推断、定量分析、差异丰度分析、二硫键分析、蛋白质修饰分析、蛋白组学质量检测、光谱库构建
ClawBio:
  proteomics-de — 蛋白组学差异表达分析

### 通路分析与基因网络
bioSkills:
  pathway-analysis/ — GO富集分析、GSEA分析、KEGG通路分析、Reactome通路分析、Wikipathways通路分析、富集结果可视化
  gene-regulatory-networks/ — SCENIC调控子分析、共表达网络分析、差异网络分析、多组学基因调控网络、扰动模拟分析

### 免疫信息学
bioSkills:
  immunoinformatics/ — MHC结合预测、表位预测、新抗原预测、免疫原性评分、TCR表位结合分析
  tcr-bcr-analysis/ — MixCR分析、SCIRPY分析、IMMCANTATION分析、免疫受体库可视化、VDJ工具分析

### CRISPR与基因组工程
bioSkills:
  crispr-screens/ — MAGECK分析、JACKS分析、靶点识别、筛选流程质量检测、文库设计、CRISPR编辑、碱基编辑分析、批次效应校正
  genome-engineering/ — gRNA设计、脱靶效应预测、HDR模板设计、碱基编辑设计、Prime编辑设计

### 工作流管理
bioSkills:
  workflow-management/ — Snakemake工作流程、Nextflow管道、CWL工作流程、WDL工作流程
ClawBio:
  repro-enforcer — 将任何分析结果导出为可重复性数据包（包含Conda环境、Singularity镜像及校验和）
  galaxy-bridge — 允许通过usegalaxy.org访问8,000多种Galaxy工具

### 特定领域分析
bioSkills:
  alternative-splicing/ — 断码剪接定量分析、差异剪接分析、异构体转换分析、Sashimi图绘制、单细胞剪接分析、剪接质量检测
  ecological-genomics/ — EDNA宏条形码分析、景观基因组学、保护遗传学、生物多样性指标分析、群落生态学、物种界定分析
  epidemiological-genomics/ — 病原体分型、变异监测、系统发育动态分析、传播路径推断、耐药性监测
  liquid-biopsy/ — cDNA预处理、ctDNA突变检测、片段分析、肿瘤细胞占比估算、基于甲基化的检测方法、纵向监测分析
  epitranscriptomics/ — m6A峰值调用、m6A差异分析、m6ANet分析、MERIP预处理、修饰类型可视化
  metabolomics/ — XCMS预处理、代谢物注释、标准化质量检测、统计分析、通路图构建、脂质组学分析、靶向分析、MSDIAL预处理
  flow-cytometry/ — FCS数据处理、门控分析、补偿转换、聚类表型分析、差异分析、流式细胞术质量检测、双细胞检测、微球标准化分析
  systems-biology/ — 流量平衡分析、代谢网络重建、基因必需性分析、特定环境模型构建、模型优化管理
  rna-structure/ — 次级结构预测、非编码RNA搜索、结构探针分析

### 数据可视化与报告生成
bioSkills:
  data-visualization/ — ggplot2基础操作、热图与聚类可视化、火山图自定义、Circos图绘制、基因组浏览器轨迹展示、交互式可视化、多面板图表设计、网络结构可视化、UpSet图绘制、颜色调色板设计、特殊组学数据可视化、基因组轨迹展示
  reporting/ — RMarkdown报告生成、Quarto报告生成、Jupyter报告生成、自动化质量检测报告、图表导出功能
ClawBio:
  profile-report — 分析结果概况报告生成
  data-extractor — 通过图像识别技术从科学图表中提取数值数据
  lit-synthesizer — PubMed/bioRxiv数据库检索、内容总结及引用关系图谱生成
  pubmed-summariser — 基于PubMed的基因/疾病信息检索，并提供结构化摘要报告

### 数据库访问
bioSkills:
  database-access/ — Entrez数据库搜索、数据获取、链接查询、BLAST序列搜索、本地BLAST搜索、SRA数据访问、地理数据查询、Uniprot数据库访问、批量数据下载、相互作用数据库查询、序列相似性分析
ClawBio:
  ukb-navigator — 对12,000多个UK Biobank字段进行语义搜索
  clinical-trial-finder — 临床试验检索工具

### 实验设计
bioSkills:
  experimental-design/ — 功效分析、样本量计算、批次设计、多重检验分析

### 组学领域的机器学习应用
bioSkills:
  machine-learning/ — 组学分类器开发、生物标志物发现、生存分析、模型验证、预测结果解释、图谱映射分析
ClawBio:
  claw-semantic-sim — 基于PubMedBERT的疾病相关文献语义相似度指数
  omics-target-evidence-mapper — 聚合来自不同组学数据源的靶点级证据

## 环境配置要求

这些技能分析需要具备生物信息学工作站环境。常见依赖项包括：

```bash
# Python
pip install biopython pysam cyvcf2 pybedtools pyBigWig scikit-allel anndata scanpy mygene

# R/Bioconductor
Rscript -e 'BiocManager::install(c("DESeq2","edgeR","Seurat","clusterProfiler","methylKit"))'

# CLI tools (Ubuntu/Debian)
sudo apt install samtools bcftools ncbi-blast+ minimap2 bedtools

# CLI tools (macOS)
brew install samtools bcftools blast minimap2 bedtools

# Or via Conda (recommended for reproducibility)
conda install -c bioconda samtools bcftools blast minimap2 bedtools fastp kraken2
```

## 常见问题

- 获取到的技能并非采用 Hermes SKILL.md 格式，而是采用各自的格式结构（bioSkills：代码模式手册；ClawBio：README 文件与 Python 脚本）。应将其视为专家参考资料。
- bioSkills 仅为参考指南——其中会列出正确的参数和代码模式，但并非可直接运行的流程。
- ClawBio 类型的技能是可运行的——许多此类技能都带有 `--demo` 参数，可直接执行。
- 这两个代码仓库均假定用户已安装生物信息学工具。在运行相关流程之前，请先检查系统是否满足前置条件。
- 对于 ClawBio，需首先在克隆的代码仓库中执行 `pip install -r requirements.txt` 命令。
- 基因组数据文件通常体积庞大。在下载参考基因组、SRA 数据集或构建索引时，请注意磁盘空间不足的问题。
