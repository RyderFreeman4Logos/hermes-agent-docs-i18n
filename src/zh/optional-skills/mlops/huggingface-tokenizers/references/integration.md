# Transformers集成指南

关于如何将HuggingFace Tokenizers与Transformers库结合使用的完整指南。

## AutoTokenizer

加载分词器的最简便方式。

### 加载预训练分词器

```python
from transformers import AutoTokenizer

# Load from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Check if using fast tokenizer (Rust-based)
print(tokenizer.is_fast)  # True

# Access underlying tokenizers.Tokenizer
if tokenizer.is_fast:
    fast_tokenizer = tokenizer.backend_tokenizer
    print(type(fast_tokenizer))  # <class 'tokenizers.Tokenizer'>
```

### 快速分词器与慢速分词器

| 特性                  | 快速分词器（Rust） | 慢速分词器（Python） |
|--------------------------|------------------|---------------|
| 速度                    | 快5-10倍         | 基准水平       |
| 对齐跟踪功能           | ✅ 完全支持       | ❌ 有限支持     |
| 批量处理能力           | ✅ 优化处理       | ⚠️ 处理速度较慢 |
| 偏移量映射功能           | ✅ 支持         | ❌ 不支持       |
| 安装方式               | 需单独安装 `tokenizers` 库 | 内置支持     |

**只要条件允许，请始终使用快速分词器。**

### 查看可用分词器列表

```python
from transformers import TOKENIZER_MAPPING

# List all fast tokenizers
for config_class, (slow, fast) in TOKENIZER_MAPPING.items():
    if fast is not None:
        print(f"{config_class.__name__}: {fast.__name__}")
```

## PreTrainedTokenizerFast

用于为 Transformer 模型封装自定义分词器。

### 转换为自定义分词器

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from transformers import PreTrainedTokenizerFast

# Train custom tokenizer
tokenizer = Tokenizer(BPE())
trainer = BpeTrainer(
    vocab_size=30000,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]
)
tokenizer.train(files=["corpus.txt"], trainer=trainer)

# Save tokenizer
tokenizer.save("my-tokenizer.json")

# Wrap for transformers
transformers_tokenizer = PreTrainedTokenizerFast(
    tokenizer_file="my-tokenizer.json",
    unk_token="[UNK]",
    sep_token="[SEP]",
    pad_token="[PAD]",
    cls_token="[CLS]",
    mask_token="[MASK]"
)

# Save in transformers format
transformers_tokenizer.save_pretrained("my-tokenizer")
```

**结果**：包含 `tokenizer.json`、`tokenizer_config.json` 以及 `special_tokens_map.json` 的目录。

### 可像普通 Transformers 分词器一样使用

```python
# Load
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("my-tokenizer")

# Encode with all transformers features
outputs = tokenizer(
    "Hello world",
    padding="max_length",
    truncation=True,
    max_length=128,
    return_tensors="pt"
)

print(outputs.keys())
# dict_keys(['input_ids', 'token_type_ids', 'attention_mask'])
```

## 特殊标记

### 默认特殊标记

| 模型系列 | CLS/BOS | SEP/EOS       | PAD     | UNK     | MASK    |
|--------------|---------|---------------|---------|---------|---------|
| BERT         | [CLS]   | [SEP]         | [PAD]   | [UNK]   | [MASK]  |
| GPT-2        | -       | <\|endoftext\|> | <\|endoftext\|> | <\|endoftext\|> | -       |
| RoBERTa      | <s>     | </s>          | <pad>   | <unk>   | <mask>  |
| T5           | -       | </s>          | <pad>   | <unk>   | -       |

### 添加特殊标记

```python
# Add new special tokens
special_tokens_dict = {
    "additional_special_tokens": ["<|image|>", "<|video|>", "<|audio|>"]
}

num_added_tokens = tokenizer.add_special_tokens(special_tokens_dict)
print(f"Added {num_added_tokens} tokens")

# Resize model embeddings
model.resize_token_embeddings(len(tokenizer))

# Use new tokens
text = "This is an image: <|image|>"
tokens = tokenizer.encode(text)
```

### 添加普通令牌

```python
# Add domain-specific tokens
new_tokens = ["COVID-19", "mRNA", "vaccine"]
num_added = tokenizer.add_tokens(new_tokens)

# These are NOT special tokens (can be split if needed)
tokenizer.add_tokens(new_tokens, special_tokens=False)

# These ARE special tokens (never split)
tokenizer.add_tokens(new_tokens, special_tokens=True)
```

## 编码与解码

### 基本编码

```python
# Single sentence
text = "Hello, how are you?"
encoded = tokenizer(text)

print(encoded)
# {'input_ids': [101, 7592, 1010, 2129, 2024, 2017, 1029, 102],
#  'token_type_ids': [0, 0, 0, 0, 0, 0, 0, 0],
#  'attention_mask': [1, 1, 1, 1, 1, 1, 1, 1]}
```

### 批量编码

```python
# Multiple sentences
texts = ["Hello world", "How are you?", "I am fine"]
encoded = tokenizer(texts, padding=True, truncation=True, max_length=10)

print(encoded['input_ids'])
# [[101, 7592, 2088, 102, 0, 0, 0, 0, 0, 0],
#  [101, 2129, 2024, 2017, 1029, 102, 0, 0, 0, 0],
#  [101, 1045, 2572, 2986, 102, 0, 0, 0, 0, 0]]
```

### 返回张量

```python
# Return PyTorch tensors
outputs = tokenizer("Hello world", return_tensors="pt")
print(outputs['input_ids'].shape)  # torch.Size([1, 5])

# Return TensorFlow tensors
outputs = tokenizer("Hello world", return_tensors="tf")

# Return NumPy arrays
outputs = tokenizer("Hello world", return_tensors="np")

# Return lists (default)
outputs = tokenizer("Hello world", return_tensors=None)
```

### 解码

```python
# Decode token IDs
ids = [101, 7592, 2088, 102]
text = tokenizer.decode(ids)
print(text)  # "[CLS] hello world [SEP]"

# Skip special tokens
text = tokenizer.decode(ids, skip_special_tokens=True)
print(text)  # "hello world"

# Batch decode
batch_ids = [[101, 7592, 102], [101, 2088, 102]]
texts = tokenizer.batch_decode(batch_ids, skip_special_tokens=True)
print(texts)  # ["hello", "world"]
```

## 填充与截断

### 填充策略

```python
# Pad to max length in batch
tokenizer(texts, padding="longest")

# Pad to model max length
tokenizer(texts, padding="max_length", max_length=128)

# No padding
tokenizer(texts, padding=False)

# Pad to multiple of value (for efficient computation)
tokenizer(texts, padding="max_length", max_length=128, pad_to_multiple_of=8)
# Result: length will be 128 (already multiple of 8)
```

### 截断策略

```python
# Truncate to max length
tokenizer(text, truncation=True, max_length=10)

# Only truncate first sequence (for pairs)
tokenizer(text1, text2, truncation="only_first", max_length=20)

# Only truncate second sequence
tokenizer(text1, text2, truncation="only_second", max_length=20)

# Truncate longest first (default for pairs)
tokenizer(text1, text2, truncation="longest_first", max_length=20)

# No truncation (error if too long)
tokenizer(text, truncation=False)
```

### 处理长文档的步进策略

```python
# For documents longer than max_length
text = "Very long document " * 1000

# Encode with overlap
encodings = tokenizer(
    text,
    max_length=512,
    stride=128,          # Overlap between chunks
    truncation=True,
    return_overflowing_tokens=True,
    return_offsets_mapping=True
)

# Get all chunks
num_chunks = len(encodings['input_ids'])
print(f"Split into {num_chunks} chunks")

# Each chunk overlaps by stride tokens
for i, chunk in enumerate(encodings['input_ids']):
    print(f"Chunk {i}: {len(chunk)} tokens")
```

**应用场景**：长文档质量检测、滑动窗口推理

## 对齐与偏移量

### 偏移量映射

```python
# Get character offsets for each token
encoded = tokenizer("Hello, world!", return_offsets_mapping=True)

for token, (start, end) in zip(
    encoded.tokens(),
    encoded['offset_mapping'][0]
):
    print(f"{token:10s} → [{start:2d}, {end:2d})")

# Output:
# [CLS]      → [ 0,  0)
# Hello      → [ 0,  5)
# ,          → [ 5,  6)
# world      → [ 7, 12)
# !          → [12, 13)
# [SEP]      → [ 0,  0)
```

### 单词 ID

```python
# Get word index for each token
encoded = tokenizer("Hello world", return_offsets_mapping=True)
word_ids = encoded.word_ids()

print(word_ids)
# [None, 0, 1, None]
# None = special token, 0 = first word, 1 = second word
```

**应用场景**：令牌分类（命名实体识别、词性标注）

### 字符到令牌的映射

```python
text = "Machine learning is awesome"
encoded = tokenizer(text, return_offsets_mapping=True)

# Find token for character position
char_pos = 8  # "l" in "learning"
token_idx = encoded.char_to_token(char_pos)

print(f"Character {char_pos} is in token {token_idx}: {encoded.tokens()[token_idx]}")
# Character 8 is in token 2: learning
```

**应用场景**：问答系统（将答案的字符范围映射为标记）

### 序列对

请翻译完整的输入内容，切勿提前终止。

```python
# Encode sentence pair
encoded = tokenizer("Question here", "Answer here", return_offsets_mapping=True)

# Get sequence IDs (which sequence each token belongs to)
sequence_ids = encoded.sequence_ids()
print(sequence_ids)
# [None, 0, 0, 0, None, 1, 1, 1, None]
# None = special token, 0 = question, 1 = answer
```

## 模型集成

### 与 Transformer 模型配合使用

```python
from transformers import AutoModel, AutoTokenizer
import torch

# Load model and tokenizer
model = AutoModel.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokenize
text = "Hello world"
inputs = tokenizer(text, return_tensors="pt")

# Forward pass
with torch.no_grad():
    outputs = model(**inputs)

# Get embeddings
last_hidden_state = outputs.last_hidden_state
print(last_hidden_state.shape)  # [1, seq_len, hidden_size]
```

### 带自定义分词器的定制模型

```python
from transformers import BertConfig, BertModel

# Train custom tokenizer
from tokenizers import Tokenizer, models, trainers
tokenizer = Tokenizer(models.BPE())
trainer = trainers.BpeTrainer(vocab_size=30000)
tokenizer.train(files=["data.txt"], trainer=trainer)

# Wrap for transformers
from transformers import PreTrainedTokenizerFast
fast_tokenizer = PreTrainedTokenizerFast(
    tokenizer_object=tokenizer,
    unk_token="[UNK]",
    pad_token="[PAD]"
)

# Create model with custom vocab size
config = BertConfig(vocab_size=30000)
model = BertModel(config)

# Use together
inputs = fast_tokenizer("Hello world", return_tensors="pt")
outputs = model(**inputs)
```

### 同时保存与加载

```python
# Save both
model.save_pretrained("my-model")
tokenizer.save_pretrained("my-model")

# Directory structure:
# my-model/
#   ├── config.json
#   ├── pytorch_model.bin
#   ├── tokenizer.json
#   ├── tokenizer_config.json
#   └── special_tokens_map.json

# Load both
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("my-model")
tokenizer = AutoTokenizer.from_pretrained("my-model")
```

## 高级功能

### 多模态分词功能

```python
from transformers import AutoTokenizer

# LLaVA-style (image + text)
tokenizer = AutoTokenizer.from_pretrained("llava-hf/llava-1.5-7b-hf")

# Add image placeholder token
tokenizer.add_special_tokens({"additional_special_tokens": ["<image>"]})

# Use in prompt
text = "Describe this image: <image>"
inputs = tokenizer(text, return_tensors="pt")
```

### 模板格式设置

```python
# Chat template
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What's the weather?"}
]

# Apply chat template (if tokenizer has one)
if hasattr(tokenizer, "apply_chat_template"):
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer(text, return_tensors="pt")
```

### 自定义模板

```python
from transformers import PreTrainedTokenizerFast

tokenizer = PreTrainedTokenizerFast(tokenizer_file="tokenizer.json")

# Define chat template
tokenizer.chat_template = """
{%- for message in messages %}
    {%- if message['role'] == 'system' %}
        System: {{ message['content'] }}\\n
    {%- elif message['role'] == 'user' %}
        User: {{ message['content'] }}\\n
    {%- elif message['role'] == 'assistant' %}
        Assistant: {{ message['content'] }}\\n
    {%- endif %}
{%- endfor %}
Assistant:
"""

# Use template
text = tokenizer.apply_chat_template(messages, tokenize=False)
```

## 性能优化

### 批量处理

```python
# Process large datasets efficiently
from datasets import load_dataset

dataset = load_dataset("imdb", split="train[:1000]")

# Tokenize in batches
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=512
    )

# Map over dataset (batched)
tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    batch_size=1000,
    num_proc=4  # Parallel processing
)
```

### 缓存机制

```python
# Enable caching for repeated tokenization
tokenizer = AutoTokenizer.from_pretrained(
    "bert-base-uncased",
    use_fast=True,
    cache_dir="./cache"  # Cache tokenizer files
)

# Tokenize with caching
from functools import lru_cache

@lru_cache(maxsize=10000)
def cached_tokenize(text):
    return tuple(tokenizer.encode(text))

# Reuses cached results for repeated inputs
```

### 内存效率

```python
# For very large datasets, use streaming
from datasets import load_dataset

dataset = load_dataset("pile", split="train", streaming=True)

def process_batch(batch):
    # Tokenize
    tokens = tokenizer(batch["text"], truncation=True, max_length=512)

    # Process tokens...

    return tokens

# Process in chunks (memory efficient)
for batch in dataset.batch(batch_size=1000):
    processed = process_batch(batch)
```

## 故障排除

### 问题：分词器运行速度过慢

**症状**：
```python
tokenizer.is_fast  # False
```

**解决方案**：安装分词器库
```bash
pip install tokenizers
```

### 问题：特殊标记无法正常使用

**症状**：特殊标记被拆分成了多个子词

**解决方案**：应将其作为特殊标记添加，而非普通标记
```python
# Wrong
tokenizer.add_tokens(["<|image|>"])

# Correct
tokenizer.add_special_tokens({"additional_special_tokens": ["<|image|>"]})
```

### 问题：无法使用偏移映射功能

**症状**：
```python
tokenizer("text", return_offsets_mapping=True)
# Error: return_offsets_mapping not supported
```

**解决方案**：使用高效的分词器。
```python
from transformers import AutoTokenizer

# Load fast version
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased", use_fast=True)
```

### 问题：填充不一致

**症状**：部分序列被添加了填充符，而其他序列则没有

**解决方案**：指定填充策略
```python
# Explicit padding
tokenizer(
    texts,
    padding="max_length",  # or "longest"
    max_length=128
)
```

## 最佳实践

1. **始终使用高效的分词器**：
   - 加速效率提升5-10倍
   - 支持完整的对齐跟踪功能
   - 提升批量处理性能

2. **将分词器与模型一同保存**：
   - 确保实验结果可复现
   - 避免版本不匹配问题

3. **对数据集采用批量处理方式**：
   - 使用`.map(batched=True)`进行分词
   - 设置`num_proc`参数以实现并行处理

4. **为重复输入启用缓存功能**：
   - 在推理过程中使用`lru_cache`
   - 通过`cache_dir`参数缓存分词器文件

5. **正确处理特殊标记**：
   - 使用`add_special_tokens()`处理不可分割的标记
   - 添加标记后调整嵌入向量的尺寸

6. **为后续任务验证对齐效果**：
   - 检查`offset_mapping`是否正确
   - 对样本数据测试`char_to_token()`功能

7. **对分词器配置进行版本控制**：
   - 保存`tokenizer_config.json`文件
   - 对自定义模板做好文档记录
   - 跟踪词汇表的变化情况
