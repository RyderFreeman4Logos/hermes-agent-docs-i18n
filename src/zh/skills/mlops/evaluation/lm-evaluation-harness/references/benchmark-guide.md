# 基准测试指南

全面介绍 lm-evaluation-harness 中的 60 多项评估任务，包括它们的衡量指标以及结果解读方法。

## 概述

lm-evaluation-harness 提供了 60 多项基准测试，涵盖以下领域：
- 语言理解（MMLU、GLUE）
- 数学推理（GSM8K、MATH）
- 代码生成（HumanEval、MBPP）
- 指令遵循（IFEval、AlpacaEval）
- 长上下文理解（LongBench）
- 多语言能力（AfroBench、NorEval）
- 推理能力（BBH、ARC）
- 真实性评估（TruthfulQA）

**查看所有任务列表**：
```bash
lm_eval --tasks list
```

## 主要基准测试

### MMLU（大规模多任务语言理解）

**衡量内容**：涵盖57个学科领域的广泛知识（包括STEM、人文科学、社会科学及法律）。

**任务变体**：
- `mmlu`：原始的57学科基准测试
- `mmlu_pro`：难度更高的版本，包含更多注重推理能力的题目
- `mmlu_prox`：多语言扩展版本

**格式**：多项选择题（4个选项）

**示例**：
```
Question: What is the capital of France?
A. Berlin
B. Paris
C. London
D. Madrid
Answer: B
```

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu \
  --num_fewshot 5
```

**解读结果**：
- 随机生成：25%（概率）
- GPT-3（175B）：43.9%
- GPT-4：86.4%
- 人类专家：约90%

**适用场景**：评估通用知识及领域专业能力。

### GSM8K（小学数学8K）

**测评内容**：针对小学水平文字题的数学推理能力。

**任务变体**：
- `gsm8k`：基础任务
- `gsm8k_cot`：包含思维链提示的版本
- `gsm_plus`：带有干扰项的对抗性版本

**输出格式**：自由生成文本，需提取数值答案

**示例**：
```
Question: A baker made 200 cookies. He sold 3/5 of them in the morning and 1/4 of the remaining in the afternoon. How many cookies does he have left?
Answer: 60
```

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks gsm8k \
  --num_fewshot 5
```

**模型识别结果**：
- 随机模型：约 0%
- GPT-3 (175B)：17.0%
- GPT-4：92.0%
- Llama 2 70B：56.8%

**适用场景**：用于测试多步骤推理与算术运算能力。

### HumanEval

**评估内容**：根据文档字符串生成 Python 代码（功能正确性）。

**任务类型**：
- `humaneval`：标准基准测试
- `humaneval_instruct`：适用于经指令微调的模型

**评估形式**：代码生成后通过运行进行测试

**示例**：
```python
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
```

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=codellama/CodeLlama-7b-hf \
  --tasks humaneval \
  --batch_size 1
```

**模型识别结果**：
- 随机模型：0%
- GPT-3（175B）：0%
- Codex：28.8%
- GPT-4：67.0%
- Code Llama 34B：53.7%

**适用场景**：评估代码生成能力。

### BBH（BIG-Bench Hard）

**测评内容**：包含23项极具挑战性的推理任务，以往的模型均无法在这些任务上超越人类水平。

**分类类别**：
- 逻辑推理
- 数学应用题
- 社会理解
- 算法推理

**答题形式**：选择题与自由作答题

**相关命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks bbh \
  --num_fewshot 3
```

**识别准确率**：
- 随机模型：约25%
- GPT-3（175B）：33.9%
- PaLM 540B：58.3%
- GPT-4：86.7%

**适用场景**：测试高级推理能力。

### IFEval（指令遵循评估）

**评估内容**：模型遵循具体且可验证的指令的能力。

**指令类型**：
- 格式限制（例如：“用3句话作答”）
- 长度限制（例如：“至少使用100个单词”）
- 内容要求（例如：“需包含‘banana’一词”）
- 结构要求（例如：“使用项目符号列出”）

**评估形式**：基于规则的自由生成内容验证

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-chat-hf \
  --tasks ifeval \
  --batch_size auto
```

**解读**：
- 评估指标：指令遵循程度（而非模型质量）
- GPT-4：指令遵循率为86%
- Claude 2：指令遵循率为84%

**适用场景**：用于评估对话型/指令遵循型模型。

### GLUE（通用语言理解评估）

**评估内容**：涵盖9项任务的自然语言理解能力。

**具体任务包括**：
- `cola`：语法正确性检测
- `sst2`：情感分析
- `mrpc`：释义识别
- `qqp`：问题对任务
- `stsb`：语义相似度计算
- `mnli`：自然语言推理
- `qnli`：问答式自然语言推理
- `rte`：文本蕴含关系识别
- `wnli`：Winograd图谱任务

**使用命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=bert-base-uncased \
  --tasks glue \
  --num_fewshot 0
```

**性能指标**：
- BERT Base：78.3（GLUE评分）
- RoBERTa Large：88.5
- 人类基准值：87.1

**适用场景**：仅包含编码器的模型，以及基线模型的微调。

### LongBench

**评估内容**：长上下文理解能力（4K–32K个标记）。

**涵盖的21项任务包括**：
- 单文档问答
- 多文档问答
- 摘要生成
- 少样本学习
- 代码补全
- 合成任务

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks longbench \
  --batch_size 1
```

**解读**：
- 测试模型对上下文信息的利用能力
- 许多模型在处理超过4K令牌长度的文本时表现不佳
- GPT-4 Turbo：54.3%

**适用场景**：评估支持长上下文处理的模型。

## 其他基准测试

### TruthfulQA

**衡量指标**：模型倾向于说真话，而非生成看似合理但实际上虚假的内容。

**题目格式**：包含4-5个选项的多项选择题

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks truthfulqa_mc2 \
  --batch_size auto
```

**解读结果**：
- 模型规模越大，表现往往越差（编造的谎言越难以被识破）
- GPT-3：58.8%
- GPT-4：59.0%
- 人类：约94%

### ARC（AI2推理挑战）

**测试内容**：小学阶段的科学问题。

**题目难度版本**：
- `arc_easy`：较简单的问题
- `arc_challenge`：需要逻辑推理的较难问题

**使用命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks arc_challenge \
  --num_fewshot 25
```

**解读结果**：
- ARC-Easy：大多数模型的准确率 >80%
- ARC-Challenge随机测试：25%
- GPT-4：96.3%

### HellaSwag

**评估内容**：针对日常场景的常识推理能力。

**格式**：选择最合理的后续内容

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks hellaswag \
  --num_fewshot 10
```

**识别结果**：
- 随机模型：25%
- GPT-3：78.9%
- Llama 2 70B：85.3%

### WinoGrande

**衡量指标**：通过代词解析能力来评估常识推理水平。

**示例**：
```
The trophy doesn't fit in the brown suitcase because _ is too large.
A. the trophy
B. the suitcase
```

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks winogrande \
  --num_fewshot 5
```

### PIQA

**衡量内容**：物理常识推理能力。

**示例**：“要清洁键盘，可以使用压缩空气或……”

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks piqa
```

## 多语言基准测试

### AfroBench

**测试内容**：64种非洲语言的性能表现。

**包含15项任务**：自然语言理解、文本生成、知识问答、推理问答、数学推理

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks afrobench
```

### NorEval

**衡量指标**：挪威语理解能力（涵盖9类任务）。

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=NbAiLab/nb-gpt-j-6B \
  --tasks noreval
```

## 领域特定基准测试

### 数学

**衡量内容**：高中竞赛数学题目。

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks math \
  --num_fewshot 4
```

**理解能力测试**：
- 非常具有挑战性
- GPT-4：42.5%
- Minerva 540B：33.6%

### MBPP（基础Python问题集）

**考核内容**：根据自然语言描述进行Python编程。

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=codellama/CodeLlama-7b-hf \
  --tasks mbpp \
  --batch_size 1
```

### DROP

**衡量能力**：需要运用逻辑推理的阅读理解能力。

**命令**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks drop
```

## 基准测试选择指南

### 通用模型适用场景

运行以下测试套件：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag,arc_challenge,truthfulqa_mc2 \
  --num_fewshot 5
```

### 针对代码模型

```bash
lm_eval --model hf \
  --model_args pretrained=codellama/CodeLlama-7b-hf \
  --tasks humaneval,mbpp \
  --batch_size 1
```

### 用于聊天/指令模型

```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-chat-hf \
  --tasks ifeval,mmlu,gsm8k_cot \
  --batch_size auto
```

### 适用于长上下文模型

```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-3.1-8B \
  --tasks longbench \
  --batch_size 1
```

## 结果解读

### 指标说明

**准确率**：正确答案所占的百分比（最常用指标）

**完全匹配（Exact Match, EM）**：要求字符串实现完全一致（要求极为严格）

**F1分数**：在精确度与召回率之间取得平衡

**BLEU/ROUGE**：用于衡量文本生成的相似度

**Pass@k**：生成k个样本后通过测试的样本所占百分比

### 常见分数范围

| 模型规模 | MMLU | GSM8K | HumanEval | HellaSwag |
|----------|------|-------|-----------|-----------|
| 7B | 40-50% | 10-20% | 5-15% | 70-80% |
| 13B | 45-55% | 20-35% | 15-25% | 75-82% |
| 70B | 60-70% | 50-65% | 35-50% | 82-87% |
| GPT-4 | 86% | 92% | 67% | 95% |

### 需警惕的异常情况

- **所有任务的表现都仅处于随机水平**：说明模型训练不当
- **生成类任务的准确率为0%**：很可能是格式或解析问题所致
- **不同运行结果差异极大**：请检查种子值或采样设置
- **在所有指标上均优于GPT-4**：极有可能是数据被污染

## 最佳实践建议

1. **务必说明少样本训练的设置**：如0样本、5样本等
2. **运行多次实验并使用不同种子**：最终报告平均值及标准差
3. **检查数据是否被污染**：在训练数据中查找基准测试案例
4. **与已公开的基准模型进行对比**：以此验证你的实验环境
5. **完整列出所有超参数**：包括模型类型、批量大小、最大token数、温度值等

## 参考资料

- 任务列表：`lm_eval --tasks list`
- 各任务说明文档：`lm_eval/tasks/README.md`
- 相关论文：请查阅各基准测试对应的学术论文
