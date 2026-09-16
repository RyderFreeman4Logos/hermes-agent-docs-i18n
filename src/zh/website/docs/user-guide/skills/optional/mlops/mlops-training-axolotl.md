---
title: "Axolotl — Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO)"
sidebar_label: "Axolotl"
description: "Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO)"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Axolotl

Axolotl：基于 YAML 的大语言模型微调工具（支持 LoRA、DPO、GRPO 等技术）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/axolotl` 安装 |
| 路径 | `optional-skills/mlops\training\axolotl` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `axolotl`、`torch`、`transformers`、`datasets`、`peft`、`accelerate`、`deepspeed` |
| 支持平台 | linux、macos |
| 标签 | `微调`、`Axolotl`、`大语言模型`、`LoRA`、`QLoRA`、`DPO`、`KTO`、`ORPO`、`GRPO`、`YAML`、`HuggingFace`、`DeepSpeed`、`多模态` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能启用后，智能体将依据此内容执行操作。
:::

# Axolotl 技能

## 功能概述

提供使用 Axolotl 微调大语言模型的专业指导 — 包含 YAML 配置文件、100 多种模型选项、LoRA/QLoRA 微调方法、DPO/KTO/ORPO/GRPO 等训练策略，同时还支持多模态处理。

基于官方文档整理的 Axolotl 开发相关帮助内容。

## 何时使用该技能

在以下情况下可触发此技能：
- 使用 Axolotl 工作
- 咨询 Axolotl 的功能或 API 信息
- 实现基于 Axolotl 的解决方案
- 调试 Axolotl 相关代码
- 学习 Axolotl 的最佳实践

## 快速参考

### 常见用法模式

**模式 1：** 为确保您的训练任务具有可接受的数据传输速度，运行 NCCL 测试有助于识别潜在瓶颈，例如：

```
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 3
```

**模式 2：** 在 Axolotl 的 YAML 配置文件中设置模型以使用 FSDP。例如：

```
fsdp_version: 2
fsdp_config:
  offload_params: true
  state_dict_type: FULL_STATE_DICT
  auto_wrap_policy: TRANSFORMER_BASED_WRAP
  transformer_layer_cls_to_wrap: LlamaDecoderLayer
  reshard_after_forward: true
```

**模式 3：** context_parallel_size 的数值必须能整除 GPU 的总数。例如：

```
context_parallel_size
```

**模式 4：** 例如：- 当使用 8 块 GPU 且不启用序列并行处理时，每步将处理 8 个不同的批次；- 当使用 8 块 GPU 且设置 context_parallel_size=4 时，每步仅处理 2 个不同的批次（每个批次分配到 4 块 GPU 上）；- 如果每块 GPU 的 micro_batch_size 为 2，则全局批量大小将从 16 减少至 4。

```
context_parallel_size=4
```

**模式 5：** 在配置中将 `save_compressed` 设置为 `true` 可使模型以压缩格式保存，从而实现以下优势：- 减少约 40% 的磁盘占用空间；- 保持与 vLLM 的兼容性，从而提升推理速度；- 保留与 llmcompressor 的兼容性，便于进一步优化（例如量化处理）。

```
save_compressed: true
```

**模式 6：** 注意，无需将您的集成代码放入 integrations 文件夹中。只要它能被打包到 Python 环境中的某个包中，放置在任何位置均可。有关示例，请参阅此仓库：https://github.com/axolotl-ai-cloud/diff-transformer

```
integrations
```

**模式 7：** 支持处理单个样本数据与批量数据。- 单个样本数据：sample['input_ids'] 的类型为 list[int]。- 批量数据：sample['input_ids'] 的类型为 list[list[int]]。

```
utils.trainer.drop_long_seq(sample, sequence_len=2048, min_sequence_len=2)
```

### 示例代码模式

**示例 1**（Python）：
```python
cli.cloud.modal_.ModalCloud(config, app=None)
```

**示例 2**（Python）：
```python
cli.cloud.modal_.run_cmd(cmd, run_folder, volumes=None)
```

**示例 3**（Python）：
```python
core.trainers.base.AxolotlTrainer(
    *_args,
    bench_data_collator=None,
    eval_data_collator=None,
    dataset_tags=None,
    **kwargs,
)
```

**示例 4**（Python）：
```python
core.trainers.base.AxolotlTrainer.log(logs, start_time=None)
```

**示例 5**（Python）：
```python
prompt_strategies.input_output.RawInputOutputPrompter()
```

## 参考文档

该技能在 `references/` 目录中提供了详尽的文档资料：

- **api.md** - API 文档
- **dataset-formats.md** - 数据集格式文档
- **other.md** - 其他文档

当需要详细信息时，可使用 `view` 命令来查看特定的参考文件。

## 使用该技能

### 面向初学者
建议先阅读 `getting_started` 或教程类参考文件，以了解基础概念。

### 针对特定功能
如需详细信息，请查阅对应类别的参考文件（如 API 文档、指南等）。

### 代码示例
上方的快速参考部分汇总了从官方文档中提取的常见模式。

## 资源目录

### references/
此处整理了从官方来源摘录的文档资料，包含以下内容：
- 详细说明
- 带有语言标注的代码示例
- 指向原始文档的链接
- 便于快速导航的目录结构

### scripts/
可在该目录中添加用于常见自动化任务的辅助脚本。

### assets/
可在此处存放模板、样板文件或示例项目。

## 备注

- 该技能是根据官方文档自动生成的。
- 参考文档保留了源文档的结构与示例内容。
- 代码示例包含语言检测功能，有助于实现更佳的语法高亮显示。
- 快速参考模式是从文档中的常见使用案例中提取而来的。

## 更新说明

如需用最新文档更新此技能：
1. 使用相同的配置重新运行抓取工具。
2. 该技能将基于最新信息重新生成。
