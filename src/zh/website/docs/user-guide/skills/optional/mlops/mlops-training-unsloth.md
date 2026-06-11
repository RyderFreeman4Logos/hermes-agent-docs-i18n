---
title: "Unsloth — Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM"
sidebar_label: "Unsloth"
description: "Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Unsloth

Unsloth：可使 LoRA/QLoRA 微调速度提升 2-5 倍，同时降低 VRAM 使用量。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/mlops/unsloth` 安装 |
| 路径 | `optional-skills/mlops/training/unsloth` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `unsloth`, `torch`, `transformers`, `trl`, `datasets`, `peft` |
| 支持平台 | linux, macos |
| 标签 | `微调`, `Unsloth`, `快速训练`, `LoRA`, `QLoRA`, `节省内存`, `优化`, `Llama`, `Mistral`, `Gemma`, `Qwen` |

## 参考：完整的 SKILL.md

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能启用时，智能体看到的指令即为此内容。
:::

# Unsloth 技能

基于官方文档整理的 Unsloth 开发全方位辅助功能。

## 何时使用此技能

在以下情况下可触发此技能：
- 使用 Unsloth 进行开发
- 查询 Unsloth 的功能或 API 信息
- 实现 Unsloth 相关解决方案
| 调试 Unsloth 代码 | 学习 Unsloth 最佳实践 |
|---|---|

## 快速参考

### 常见模式

*随着您不断使用此技能，更多快速参考模式将会被添加。*

## 参考文件

此技能在 `references/` 目录下提供了详尽的文档：

- **llms-txt.md** - Llms-Txt 文档

当需要详细信息时，可使用 `view` 命令查看特定的参考文件。

## 如何使用此技能

### 面向初学者
请从入门指南或教程类参考文件开始，了解基础概念。

### 查询特定功能
针对具体功能，可查阅相应的分类参考文件（如 API 文档、操作指南等）以获取详细信息。

### 查看代码示例
上述快速参考部分汇总了从官方文档中提取的常见模式。

## 资源

### references/
汇总自官方来源的结构化文档。这些文件包含：
- 详细的解释说明
- 带有语言标注的代码示例
- 指向原始文档的链接
- 便于快速导航的目录结构

### scripts/
在此处可添加用于常见自动化任务的辅助脚本。

### assets/
可在此处存放模板、基础代码框架或示例项目。

## 备注

- 本技能是根据官方文档自动生成的
- 参考文件保留了源文档的结构与示例内容
- 代码示例已进行语言检测，以便实现更精准的语法高亮显示
- 快速参考模式取自文档中的常见使用案例

## 更新说明

如需用最新文档更新此技能：
1. 使用相同的配置重新运行抓取脚本
2. 技能将基于最新信息重新生成

<!-- 触发重新上传 1763621536 -->
