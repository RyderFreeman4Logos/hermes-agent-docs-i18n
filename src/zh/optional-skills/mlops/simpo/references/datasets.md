# 数据集

关于用于 SimPO 训练的偏好数据集的完整指南。

## 数据集格式

### 必填字段

偏好数据集必须包含：
```json
{
  "prompt": "User question or instruction",
  "chosen": "Better/preferred response",
  "rejected": "Worse/rejected response"
}
```

**备用字段名称**（自动检测）：
- `prompt` → `question`、`instruction`、`input`
- `chosen` → `response_chosen`、`winner`、`preferred`
- `rejected` → `response_rejected`、`loser`

### 示例条目

```json
{
  "prompt": "Explain quantum computing in simple terms.",
  "chosen": "Quantum computing uses quantum bits (qubits) that can exist in multiple states simultaneously through superposition. This allows quantum computers to process many possibilities at once, making them potentially much faster than classical computers for specific tasks like cryptography and optimization.",
  "rejected": "It's like regular computing but quantum."
}
```

## 热门数据集

### 1. UltraFeedback（推荐）

**HuggingFaceH4/ultrafeedback_binarized**：
- **规模**：60K组偏好对
- **质量**：高（由GPT-4完成标注）
- **应用领域**：通用指令遵循任务
- **格式**：结构清晰，可直接使用

**配置参数**：
```yaml
dataset_mixer:
  HuggingFaceH4/ultrafeedback_binarized: 1.0
dataset_splits:
  - train_prefs
  - test_prefs
```

### 2. Argilla UltraFeedback（已清洗版）

**argilla/ultrafeedback-binarized-preferences-cleaned**：
- **规模**：5万对数据（已过滤）
- **质量**：极高（已去重并清洗）
- **领域**：通用
- **格式**：已净化

**配置参数**：
```yaml
dataset_mixer:
  argilla/ultrafeedback-binarized-preferences-cleaned: 1.0
```

### 3. Distilabel Math

**argilla/distilabel-math-preference-dpo**：
- **数据量**：30K 对
- **质量**：高（GSM8K、MATH 标准）
- **应用领域**：数学推理
- **格式**：专为数学任务设计

**配置选项**：
```yaml
dataset_mixer:
  argilla/distilabel-math-preference-dpo: 1.0
```

### 4. HelpSteer

**nvidia/HelpSteer**：
- **样本量**：38K个样本
- **质量**：高（由人类评分确定）
- **应用领域**：实用性对齐
- **评分格式**：多属性评分

**配置参数**：
```yaml
dataset_mixer:
  nvidia/HelpSteer: 1.0
```

### 5. Anthropic HH-RLHF

**Anthropic/hh-rlhf**：
- **样本量**：161K条
- **质量**：高（符合人类偏好）
- **应用领域**：无害且实用
- **格式**：对话式

**配置参数**：
```yaml
dataset_mixer:
  Anthropic/hh-rlhf: 1.0
```

## 数据集混合

### 多个数据集

**等比例混合**：
```yaml
dataset_mixer:
  HuggingFaceH4/ultrafeedback_binarized: 0.5
  Anthropic/hh-rlhf: 0.5
```

**加权混合**：
```yaml
dataset_mixer:
  HuggingFaceH4/ultrafeedback_binarized: 0.7
  argilla/distilabel-math-preference-dpo: 0.2
  nvidia/HelpSteer: 0.1
```

**领域专用功能侧重**：
```yaml
# 80% general + 20% math
dataset_mixer:
  HuggingFaceH4/ultrafeedback_binarized: 0.8
  argilla/distilabel-math-preference-dpo: 0.2
```

## 数据质量

### 质量指标

**优质偏好数据**：
- ✅ 已选择与被拒绝的选项之间存在明显的质量差异
- ✅ 提示语多样化
- ✅ 噪声及标注错误极少
- ✅ 难度适中

**劣质偏好数据**：
- ❌ 偏好选项表述模糊
- ❌ 提示语重复
- ❌ 标注存在噪声
- ❌ 提示语难度过低或过高

### 质量过滤

**按长度差异进行过滤**：
```python
def filter_by_length(example):
    chosen_len = len(example['chosen'].split())
    rejected_len = len(example['rejected'].split())
    # Reject if chosen is much shorter (potential low-effort)
    return chosen_len >= rejected_len * 0.5

dataset = dataset.filter(filter_by_length)
```

**按多样性筛选**：
```python
seen_prompts = set()

def filter_duplicates(example):
    prompt = example['prompt']
    if prompt in seen_prompts:
        return False
    seen_prompts.add(prompt)
    return True

dataset = dataset.filter(filter_duplicates)
```

## 自定义数据集创建

### 格式 1：JSON Lines

**文件**（`preferences.jsonl`）：
```jsonl
{"prompt": "What is Python?", "chosen": "Python is a high-level programming language...", "rejected": "It's a snake."}
{"prompt": "Explain AI.", "chosen": "AI refers to systems that can...", "rejected": "It's computers that think."}
```

**加载**：
```yaml
dataset_mixer:
  json:
    data_files: preferences.jsonl
```

### 格式 2：HuggingFace 数据集

**通过字典创建**：
```python
from datasets import Dataset

data = {
    "prompt": ["What is Python?", "Explain AI."],
    "chosen": ["Python is...", "AI refers to..."],
    "rejected": ["It's a snake.", "It's computers..."]
}

dataset = Dataset.from_dict(data)
dataset.push_to_hub("username/my-preferences")
```

**在配置文件中的使用方式**：
```yaml
dataset_mixer:
  username/my-preferences: 1.0
```

### 格式 3：ChatML

**适用于对话数据**：
```json
{
  "prompt": [
    {"role": "user", "content": "What is quantum computing?"}
  ],
  "chosen": [
    {"role": "assistant", "content": "Quantum computing uses qubits..."}
  ],
  "rejected": [
    {"role": "assistant", "content": "It's like regular computing but quantum."}
  ]
}
```

**应用聊天模板**：
```yaml
dataset_text_field: null  # Will apply chat template
```

## 合成数据生成

### 使用 GPT-4

**提示词模板**：
```
Given the following question:
{prompt}

Generate two responses:
1. A high-quality, detailed response (chosen)
2. A low-quality, brief response (rejected)

Format as JSON with "chosen" and "rejected" fields.
```

**示例代码**：
```python
import openai

def generate_pair(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Given: {prompt}\n\nGenerate chosen/rejected pair in JSON."
        }]
    )
    return json.loads(response.choices[0].message.content)

# Generate dataset
prompts = load_prompts()
dataset = [generate_pair(p) for p in prompts]
```

### 使用本地模型

**配合 vLLM 使用**：
```python
from vllm import LLM

llm = LLM(model="meta-llama/Meta-Llama-3-70B-Instruct")

def generate_variations(prompt):
    # Generate multiple completions
    outputs = llm.generate(
        [prompt] * 4,
        sampling_params={
            "temperature": 0.8,
            "top_p": 0.9,
            "max_tokens": 512
        }
    )

    # Select best/worst
    chosen = max(outputs, key=lambda x: len(x.outputs[0].text))
    rejected = min(outputs, key=lambda x: len(x.outputs[0].text))

    return {
        "prompt": prompt,
        "chosen": chosen.outputs[0].text,
        "rejected": rejected.outputs[0].text
    }
```

## 数据预处理

### 截断处理

**限制序列长度**：
```yaml
max_prompt_length: 512
max_completion_length: 512
max_length: 1024  # Total
```

**实现方式**：
```python
def truncate_example(example):
    tokenizer.truncation_side = "left"  # For prompts
    prompt_tokens = tokenizer(
        example['prompt'],
        max_length=512,
        truncation=True
    )

    tokenizer.truncation_side = "right"  # For completions
    chosen_tokens = tokenizer(
        example['chosen'],
        max_length=512,
        truncation=True
    )

    return {
        "prompt": tokenizer.decode(prompt_tokens['input_ids']),
        "chosen": tokenizer.decode(chosen_tokens['input_ids'])
    }

dataset = dataset.map(truncate_example)
```

### 重复项去重

**移除完全相同的重复项**：
```python
dataset = dataset.unique('prompt')
```

**移除近似重复项**（MinHash算法）：
```python
from datasketch import MinHash, MinHashLSH

def deduplicate_lsh(dataset, threshold=0.8):
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    seen = []

    for i, example in enumerate(dataset):
        m = MinHash(num_perm=128)
        for word in example['prompt'].split():
            m.update(word.encode('utf8'))

        if not lsh.query(m):
            lsh.insert(i, m)
            seen.append(example)

    return Dataset.from_list(seen)

dataset = deduplicate_lsh(dataset)
```

## 数据增强

### 重述提示词

```python
def paraphrase_prompt(example):
    # Use paraphrasing model
    paraphrased = paraphrase_model(example['prompt'])

    return [
        example,  # Original
        {
            "prompt": paraphrased,
            "chosen": example['chosen'],
            "rejected": example['rejected']
        }
    ]

dataset = dataset.map(paraphrase_prompt, batched=False, remove_columns=[])
```

### 难度平衡

**混合简单/中等/困难级别**：
```python
def categorize_difficulty(example):
    prompt_len = len(example['prompt'].split())
    if prompt_len < 20:
        return "easy"
    elif prompt_len < 50:
        return "medium"
    else:
        return "hard"

dataset = dataset.map(lambda x: {"difficulty": categorize_difficulty(x)})

# Sample balanced dataset
easy = dataset.filter(lambda x: x['difficulty'] == 'easy').shuffle().select(range(1000))
medium = dataset.filter(lambda x: x['difficulty'] == 'medium').shuffle().select(range(1000))
hard = dataset.filter(lambda x: x['difficulty'] == 'hard').shuffle().select(range(1000))

balanced = concatenate_datasets([easy, medium, hard]).shuffle()
```

## 数据集统计信息

### 统计值计算

```python
def compute_stats(dataset):
    prompt_lens = [len(x['prompt'].split()) for x in dataset]
    chosen_lens = [len(x['chosen'].split()) for x in dataset]
    rejected_lens = [len(x['rejected'].split()) for x in dataset]

    print(f"Dataset size: {len(dataset)}")
    print(f"Avg prompt length: {np.mean(prompt_lens):.1f} words")
    print(f"Avg chosen length: {np.mean(chosen_lens):.1f} words")
    print(f"Avg rejected length: {np.mean(rejected_lens):.1f} words")
    print(f"Chosen > Rejected: {sum(c > r for c, r in zip(chosen_lens, rejected_lens)) / len(dataset):.1%}")

compute_stats(dataset)
```

**预期输出**：
```
Dataset size: 50000
Avg prompt length: 45.2 words
Avg chosen length: 180.5 words
Avg rejected length: 120.3 words
Chosen > Rejected: 85.2%
```

## 最佳实践

### 1. 重视数据质量而非数量

- **推荐**：1万组高质量数据对
- **避免**：10万组含噪声的数据对

### 2. 明确的优选标准

- 所选数据应具有显著优势
- 避免微不足道的差异
- 去除模糊不清的数据对

### 3. 领域匹配

- 使数据集领域与目标应用场景相匹配
- 混合使用不同数据集以实现更广泛的覆盖范围
- 纳入经过安全过滤的数据

### 4. 训练前进行验证

```python
# Sample 10 random examples
samples = dataset.shuffle().select(range(10))

for ex in samples:
    print(f"Prompt: {ex['prompt']}")
    print(f"Chosen: {ex['chosen'][:100]}...")
    print(f"Rejected: {ex['rejected'][:100]}...")
    print(f"Preference clear: {'✓' if len(ex['chosen']) > len(ex['rejected']) else '?'}")
    print()
```

## 参考资料

- HuggingFace 数据集：https://huggingface.co/datasets  
- 对齐手册：https://github.com/huggingface/alignment-handbook  
- UltraFeedback：https://huggingface.co/datasets/HuggingFaceH4/ultrafeedback_binarized
