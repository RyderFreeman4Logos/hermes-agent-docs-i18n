---
sidebar_position: 12
title: "Batch Processing"
description: "Generate agent trajectories at scale — parallel processing, checkpointing, and toolset distributions"
---

# 批量处理

批量处理功能允许您并行地对数百甚至数千条提示词运行Hermes智能体，从而生成结构化的轨迹数据。该功能主要用于**训练数据生成**——输出包含工具使用统计信息的ShareGPT格式轨迹数据，这些数据可用于模型微调或性能评估。

## 概述

批量处理器（`batch_runner.py`）会处理以JSONL格式存储的提示词数据集，为每条提示词启动一个具备工具调用功能的完整智能体会话。每条提示词都会拥有独立的运行环境。最终生成的则是结构化的轨迹数据，其中包含完整的对话历史、工具调用统计信息以及推理覆盖度指标。

## 快速入门

```bash
# Basic batch run
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --model=anthropic/claude-sonnet-4.6 \
    --num_workers=4

# Resume an interrupted run
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --resume

# List available toolset distributions
python batch_runner.py --list_distributions
```

:::提示：实现大规模场景下的成本可预测性  
批量运行会同时启动多个代理会话，每个会话都会进行模型调用和工具调用。通过[Nous Portal](/user-guide/features/tool-gateway)订阅服务，可将模型访问权限与网页搜索、图像生成、文本转语音以及云浏览器功能整合到同一账单中——这非常适合那些希望稳定控制单次任务的成本，而无需在五个不同供应商的账户间频繁处理速率限制问题的用户。只需使用`hermes setup --portal`进行配置，再将`--model`参数设置为对应的Nous模型即可。  
:::

## 数据集格式  
输入数据集为JSONL文件格式（每行一个JSON对象）。每个数据条目都必须包含`prompt`字段：

```jsonl
{"prompt": "Write a Python function that finds the longest palindromic substring"}
{"prompt": "Create a REST API endpoint for user authentication using Flask"}
{"prompt": "Debug this error: TypeError: cannot unpack non-iterable NoneType object"}
```

条目可可选地包含以下内容：
- `image` 或 `docker_image`：用于该提示词沙箱环境的容器镜像（支持 Docker、Modal 和 Singularity 后端）
- `cwd`：任务终端会话的工作目录覆盖值

## 配置选项

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `--dataset_file` | （必填） | JSONL 数据集的路径 |
| `--batch_size` | （必填） | 每批处理的提示词数量 |
| `--run_name` | （必填） | 本次运行的名称（用于输出目录和检查点保存） |
| `--distribution` | `"default"` | 用于随机抽取的工具集分布 |
| `--model` | `claude-sonnet-4.6` | 要使用的模型 |
| `--base_url` | `https://openrouter.ai/api/v1` | API 基础地址 |
| `--api_key` | （环境变量） | 模型的 API 密钥 |
| `--max_turns` | `10` | 每个提示词最多允许的工具调用次数 |
| `--num_workers` | `4` | 并行工作进程数 |
| `--resume` | `false` | 是否从检查点继续运行 |
| `--verbose` | `false` | 是否启用详细日志记录 |
| `--max_samples` | 全部 | 仅处理数据集中的前 N 个样本 |
| `--max_tokens` | 模型默认值 | 每条模型响应的最大字符数 |

### 提供商路由（OpenRouter）

| 参数 | 描述 |
|------|------|
| `--providers_allowed` | 用逗号分隔的允许使用的提供商（例如：`"anthropic,openai"`） |
| `--providers_ignored` | 用逗号分隔的应忽略的提供商（例如：`"together,deepinfra"`） |
| `--providers_order` | 用逗号分隔的优先提供商顺序 |
| `--provider_sort` | 按 `"价格"`、`"吞吐量"` 或 `"延迟"` 排序 |

### 推理控制

| 参数 | 描述 |
|------|------|
| `--reasoning_effort` | 推理强度级别：`none`、`minimal`、`low`、`medium`、`high`、`xhigh` |
| `--reasoning_disabled` | 完全禁用推理/思考相关的token生成 |

### 高级选项

| 参数 | 描述 |
|------|------|
| `--ephemeral_system_prompt` | 执行过程中使用的系统提示词，但不会被保存到运行轨迹中 |
| `--log_prefix_chars` | 日志预览中显示的字符数（默认：100） |
| `--prefill_messages_file` | 包含少量样本预填充信息的 JSON 文件路径，用于引导模型生成答案 |

## 工具集分布

每个提示词都会从指定的**分布**中随机抽取一组工具集。这样能确保训练数据涵盖多种不同的工具组合。可使用 `--list_distributions` 查看所有可用的分布。

在当前的实现方式中，各分布会为**每一个单独的工具集**分配一个概率值。采样器会独立地为每个工具集进行随机选择，同时保证至少启用一个工具集。这与手动编写的预构建组合表有所不同。

## 输出格式

所有输出都会保存到 `data/<run_name>/` 目录下：

```text
data/my_run/
├── trajectories.jsonl    # Combined final output (all batches merged)
├── batch_0.jsonl         # Individual batch results
├── batch_1.jsonl
├── ...
├── checkpoint.json       # Resume checkpoint
└── statistics.json       # Aggregate tool usage stats
```

### 轨迹格式

`trajectories.jsonl` 文件中的每一行都是一个 JSON 对象：

```json
{
  "prompt_index": 42,
  "conversations": [
    {"from": "human", "value": "Write a function..."},
    {"from": "gpt", "value": "I'll create that function...",
     "tool_calls": [...]},
    {"from": "tool", "value": "..."},
    {"from": "gpt", "value": "Here's the completed function..."}
  ],
  "metadata": {
    "batch_num": 2,
    "timestamp": "2026-01-15T10:30:00",
    "model": "anthropic/claude-sonnet-4.6"
  },
  "completed": true,
  "partial": false,
  "api_calls": 3,
  "toolsets_used": ["terminal", "file"],
  "tool_stats": {
    "terminal": {"count": 2, "success": 2, "failure": 0},
    "read_file": {"count": 1, "success": 1, "failure": 0}
  },
  "tool_error_counts": {
    "terminal": 0,
    "read_file": 0
  }
}
```

`conversations` 字段采用类似 ShareGPT 的格式，包含 `from` 和 `value` 两个字段。工具统计信息经过标准化处理，涵盖了所有可能的工具，且不设置默认值，从而确保不同条目之间的结构一致，便于与 HuggingFace 数据集兼容。

## 检查点机制

批量运行器具备强大的检查点功能，以提高容错能力：

- **检查点文件**：在每个批次处理完成后生成，用于记录已完成提示的索引位置  
- **基于内容的恢复**：当使用 `--resume` 参数时，运行器会扫描现有的批次文件，并通过实际文本内容（而非仅索引）来匹配已完成的提示，即便数据集顺序发生变化也能实现恢复  
- **失败提示**：仅将成功处理完成的提示标记为已完成——失败的提示会在恢复时重新尝试处理  
- **批次合并**：处理完成后，所有批次文件（包括之前运行生成的文件）都会被合并为一个统一的 `trajectories.jsonl` 文件

### 恢复功能的运作原理

1. 扫描所有的 `batch_*.jsonl` 文件，通过内容匹配找出已完成的提示  
2. 过滤数据集，排除那些已经处理完成的提示  
3. 将剩余的提示重新分组为新的批次  
4. 仅对剩余的提示进行后续处理  
5. 将所有批次文件（旧文件与新文件）合并为最终输出结果

## 质量过滤

批量运行器会自动执行质量过滤操作：

- **无推理过滤**：那些助手回复中完全不含推理内容（即没有 `<REASONING_SCRATCHPAD>` 标记或相关的思考标记）的样本会被直接丢弃  
- **损坏条目过滤**：在最终合并阶段，那些包含错误工具名称（不在有效工具列表中的名称）的条目也会被过滤掉  
- **推理统计**：会记录整个运行过程中包含推理内容与不包含推理内容的回复所占的比例

## 统计信息

处理完成后，运行器会输出详尽的统计数据：

- **工具使用情况**：各工具的调用次数以及成功/失败率  
- **推理覆盖率**：包含推理内容的助手回复所占的百分比  
- **被丢弃的样本数量**：因缺乏推理内容而被过滤掉的样本数  
- **处理时长**：整个处理过程所耗用的总时间  

这些统计信息还会被保存到 `statistics.json` 文件中，以便通过编程方式进一步分析。

## 应用场景

### 训练数据生成

为模型微调任务生成多样化的工具使用轨迹：

```bash
python batch_runner.py \
    --dataset_file=data/coding_prompts.jsonl \
    --batch_size=20 \
    --run_name=coding_v1 \
    --model=anthropic/claude-sonnet-4.6 \
    --num_workers=8 \
    --distribution=default \
    --max_turns=15
```

### 模型评估

通过标准化提示语，评估模型使用各类工具的效能：

```bash
python batch_runner.py \
    --dataset_file=data/eval_suite.jsonl \
    --batch_size=10 \
    --run_name=eval_gpt4 \
    --model=openai/gpt-4o \
    --num_workers=4 \
    --max_turns=10
```

### 每个提示独立的容器镜像

对于需要特定运行环境的基准测试，每个提示都可以指定对应的独立容器镜像：

```jsonl
{"prompt": "Install numpy and compute eigenvalues of a 3x3 matrix", "image": "python:3.11-slim"}
{"prompt": "Compile this Rust program and run it", "image": "rust:1.75"}
{"prompt": "Set up a Node.js Express server", "image": "node:20-alpine", "cwd": "/app"}
```

在执行每条指令之前，批处理运行器会先验证相应的 Docker 镜像是否可访问。
