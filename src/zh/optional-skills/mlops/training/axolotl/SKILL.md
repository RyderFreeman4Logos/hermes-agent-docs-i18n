---
name: axolotl
description: "Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO)."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [axolotl, torch, transformers, datasets, peft, accelerate, deepspeed]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Fine-Tuning, Axolotl, LLM, LoRA, QLoRA, DPO, KTO, ORPO, GRPO, YAML, HuggingFace, DeepSpeed, Multimodal]

---

# Axolotl 技能

## 功能概述

提供使用 Axolotl 对大语言模型进行微调的专家级指导——包括 YAML 配置文件、100 多种预训练模型、LoRA/QLoRA 技术，以及 DPO/KTO/ORPO/GRPO 等优化方法，同时还支持多模态处理。

所有内容均源自官方文档，可为您的 Axolotl 开发工作提供全面协助。

## 适用场景

在以下情况下可使用该技能：
- 使用 Axolotl 进行项目开发
- 咨询 Axolotl 的功能或 API 相关问题
- 实现基于 Axolotl 的解决方案
- 调试 Axolotl 代码
- 学习 Axolotl 的最佳实践

## 快速参考

### 常见用法模式

**模式 1：** 为确保训练作业的数据传输速度符合要求，可通过运行 NCCL 测试来识别潜在瓶颈，例如：

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

**模式 3：** context_parallel_size 的值必须能整除 GPU 的总数。例如：

```
context_parallel_size
```

**模式 4：** 例如：- 当拥有 8 块 GPU 且不启用序列并行处理时，每步会处理 8 个不同的批次；- 当拥有 8 块 GPU 且设置 context_parallel_size=4 时，每步仅处理 2 个不同的批次（每个批次分配到 4 块 GPU 上）；- 如果每块 GPU 的微批次大小为 2，则全局批次大小会从 16 减少到 4。

```
context_parallel_size=4
```

**模式 5：** 在配置中将 `save_compressed` 设置为 `true`，即可以压缩格式保存模型。这样做的好处包括：- 减少约 40% 的磁盘空间占用；- 保持与 vLLM 的兼容性，从而实现更快速的推理速度；- 保留与 llmcompressor 的兼容性，便于进一步优化（例如量化处理）。

```
save_compressed: true
```

**模式 6：** 注意，无需将您的集成代码放入 integrations 文件夹中。只要它被封装在 Python 环境中的某个包里，位于任何位置均可。相关示例可参考此仓库：https://github.com/axolotl-ai-cloud/diff-transformer

```
integrations
```

**模式 7：** 支持处理单个样本数据与批量数据。- 单个样本：sample[‘input_ids’] 的类型为 list[int] - 批量数据：sample[‘input_ids’] 的类型为 list[list[int]]

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

该技能在 `references/` 目录中提供了完整的文档资料：

- **api.md** - API文档
- **dataset-formats.md** - 数据集格式文档
- **other.md** - 其他文档

当需要详细信息时，可使用 `view` 命令来读取特定的参考文档。

## 使用该技能的方法

### 对于初学者
建议先阅读 `getting_started` 或教程类参考文档，以掌握基础概念。

### 针对特定功能
可查阅对应类别的参考文档（如API文档、指南等）以获取详细信息。

### 代码示例
上方的快速参考部分汇总了从官方文档中提取的常见模式。

## 资源目录

### references/
此处整理了从官方来源摘录的文档资料，包含以下内容：
- 详细说明
- 带有语言标注的代码示例
- 对应原始文档的链接
- 便于快速导航的目录结构

### scripts/
可在该目录中添加用于常见自动化任务的辅助脚本。

### assets/
此处可用于存放模板、基础代码框架或示例项目。

## 备注事项

- 该技能是根据官方文档自动生成的。
- 参考文档保留了源文档的结构与示例内容。
- 代码示例会进行语言检测，以实现更精准的语法高亮显示。
- 快速参考模式是从文档中的常见使用案例中提取而来的。

## 更新说明

如需用最新文档更新此技能：
1. 使用相同的配置重新运行抓取工具。
2. 该技能将基于最新信息重新生成。


