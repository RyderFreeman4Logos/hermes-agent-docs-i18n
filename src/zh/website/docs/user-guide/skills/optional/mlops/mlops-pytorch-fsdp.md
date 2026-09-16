---
title: "Pytorch Fsdp — Fully sharded data-parallel training for large models"
sidebar_label: "Pytorch Fsdp"
description: "Fully sharded data-parallel training for large models"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Pytorch Fsdp

用于大型模型的全分片数据并行训练技术。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/pytorch-fsdp` 安装 |
| 路径 | `optional-skills/mlops\pytorch-fsdp` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `torch>=2.0`, `transformers` |
| 支持平台 | linux, macos |
| 标签 | `分布式训练`, `PyTorch`, `FSDP`, `数据并行`, `分片`, `混合精度`, `CPU卸载`, `FSDP2`, `大规模训练` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容获取操作指令。
:::

# Pytorch-Fsdp 技能

基于官方文档生成的、用于辅助 pytorch-fsdp 开发的功能。

## 何时使用此技能

在以下情况下可触发此技能：
- 处理与 pytorch-fsdp 相关的工作
- 查询 pytorch-fsdp 的功能或 API 信息
- 实现基于 pytorch-fsdp 的解决方案
- 调试 pytorch-fsdp 代码
- 学习 pytorch-fsdp 的最佳实践

## 快速参考

完整的常用模式目录（包含约157千字符的可运行FSDP代码片段）位于`references/common-patterns.md`中。当您需要了解包装机制、分片策略、检查点功能或混合精度相关的示例时，可通过`read_file`函数加载该文件。与其凭记忆重新编写FSDP相关代码，不如直接参考此文件。

## 参考文件

该技能在`references/`目录下提供了详尽的文档：

- **other.md** - 其他文档

当需要详细信息时，可使用`view`函数读取特定的参考文件。

## 使用该技能的指南

### 对于初学者
建议先阅读入门指南或教程类参考文件，以掌握基础概念。

### 针对特定功能
可根据需求查阅相应的分类参考文件（如API文档、使用指南等），以获取详细信息。

### 代码示例
上文中的快速参考部分汇总了从官方文档中提取的常用模式。

## 资源目录

### references/
此处整理了从官方来源摘录的文档。这些文件包含：
- 详细的说明内容
- 带有语言注释的代码示例
- 对应原始文档的链接
- 便于快速导航的目录结构

### scripts/
可在此处添加用于常见自动化任务的辅助脚本。

### assets/
可用于存放模板、基础代码框架或示例项目。

## 备注

- 该技能是根据官方文档自动生成的。  
- 参考文件保留了源文档中的结构与示例。  
- 代码示例会进行语言检测，从而实现更精准的语法高亮显示。  
- 快速参考模式是从文档中的常见使用案例中提取而来的。  

## 更新说明

如需使用最新文档更新此技能：  
1. 使用相同的配置重新运行抓取工具。  
2. 该技能将基于最新信息重新构建。
