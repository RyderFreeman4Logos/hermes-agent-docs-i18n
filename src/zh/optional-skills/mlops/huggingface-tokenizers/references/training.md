# 训练自定义分词器

从零开始训练分词器的完整指南。

## 训练流程

### 第一步：选择分词算法

**决策树**：
- **GPT风格模型** → BPE
- **BERT风格模型** → WordPiece
- **多语言/无词界分隔** → Unigram

### 第二步：准备训练数据

```python
# Option 1: From files
files = ["train.txt", "validation.txt"]

# Option 2: From Python list
texts = [
    "This is the first sentence.",
    "This is the second sentence.",
    # ... more texts
]

# Option 3: From dataset iterator
from datasets import load_dataset

dataset = load_dataset("wikitext", "wikitext-103-raw-v1", split="train")

def batch_iterator(batch_size=1000):
    for i in range(0, len(dataset), batch_size):
        yield dataset[i:i + batch_size]["text"]
```

### 第3步：初始化分词器

**BPE示例**：
```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel()
tokenizer.decoder = ByteLevelDecoder()

trainer = BpeTrainer(
    vocab_size=50000,
    min_frequency=2,
    special_tokens=["<|endoftext|>", "<|padding|>"],
    show_progress=True
)
```

**WordPiece 示例**：
```python
from tokenizers.models import WordPiece
from tokenizers.trainers import WordPieceTrainer
from tokenizers.normalizers import BertNormalizer
from tokenizers.pre_tokenizers import BertPreTokenizer

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
tokenizer.normalizer = BertNormalizer(lowercase=True)
tokenizer.pre_tokenizer = BertPreTokenizer()

trainer = WordPieceTrainer(
    vocab_size=30522,
    min_frequency=2,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    continuing_subword_prefix="##",
    show_progress=True
)
```

**Unigram 示例**：
```python
from tokenizers.models import Unigram
from tokenizers.trainers import UnigramTrainer

tokenizer = Tokenizer(Unigram())

trainer = UnigramTrainer(
    vocab_size=8000,
    special_tokens=["<unk>", "<s>", "</s>", "<pad>"],
    unk_token="<unk>",
    show_progress=True
)
```

### 第4步：训练模型

```python
# From files
tokenizer.train(files=files, trainer=trainer)

# From iterator (recommended for large datasets)
tokenizer.train_from_iterator(
    batch_iterator(),
    trainer=trainer,
    length=len(dataset)  # Optional, for progress bar
)
```

**训练时间**（基于16核CPU，词汇量3万）：
- 10 MB：15–30秒
- 100 MB：1–3分钟
- 1 GB：15–30分钟
- 10 GB：2–4小时

### 第5步：添加后处理功能

```python
from tokenizers.processors import TemplateProcessing

# BERT-style
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B [SEP]",
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]")),
    ],
)

# GPT-2 style
tokenizer.post_processor = TemplateProcessing(
    single="$A <|endoftext|>",
    special_tokens=[
        ("<|endoftext|>", tokenizer.token_to_id("<|endoftext|>")),
    ],
)
```

### 第6步：保存

```python
# Save to JSON
tokenizer.save("my-tokenizer.json")

# Save to directory (for transformers)
tokenizer.save("my-tokenizer-dir/tokenizer.json")

# Convert to transformers format
from transformers import PreTrainedTokenizerFast

transformers_tokenizer = PreTrainedTokenizerFast(
    tokenizer_object=tokenizer,
    unk_token="[UNK]",
    pad_token="[PAD]",
    cls_token="[CLS]",
    sep_token="[SEP]",
    mask_token="[MASK]"
)

transformers_tokenizer.save_pretrained("my-tokenizer-dir")
```

## 训练器配置

### BpeTrainer 参数

```python
from tokenizers.trainers import BpeTrainer

trainer = BpeTrainer(
    vocab_size=30000,              # Target vocabulary size
    min_frequency=2,               # Minimum frequency for merges
    special_tokens=["[UNK]"],      # Special tokens (added first)
    limit_alphabet=1000,           # Limit initial alphabet size
    initial_alphabet=[],           # Pre-defined initial characters
    show_progress=True,            # Show progress bar
    continuing_subword_prefix="",  # Prefix for continuing subwords
    end_of_word_suffix=""          # Suffix for end of words
)
```

**参数调优**：
- **vocab_size**：英语语料建议从30k开始，多语言语料则建议设置为50k。
- **min_frequency**：大型语料库的取值范围为2-5，小型语料库则为1。
- **limit_alphabet**：针对非英语语种（如CJK语言），需适当降低该参数值。

### WordPieceTrainer参数

```python
from tokenizers.trainers import WordPieceTrainer

trainer = WordPieceTrainer(
    vocab_size=30522,              # BERT uses 30,522
    min_frequency=2,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    limit_alphabet=1000,
    continuing_subword_prefix="##", # BERT-style prefix
    show_progress=True
)
```

### UnigramTrainer 参数

```python
from tokenizers.trainers import UnigramTrainer

trainer = UnigramTrainer(
    vocab_size=8000,               # Typically smaller than BPE/WordPiece
    special_tokens=["<unk>", "<s>", "</s>"],
    unk_token="<unk>",
    max_piece_length=16,           # Maximum token length
    n_sub_iterations=2,            # EM algorithm iterations
    shrinking_factor=0.75,         # Vocabulary reduction rate
    show_progress=True
)
```

## 基于大规模数据集的训练

### 高内存效率的训练方式

```python
from datasets import load_dataset
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer

# Load dataset
dataset = load_dataset("wikipedia", "20220301.en", split="train", streaming=True)

# Create iterator (yields batches)
def batch_iterator(batch_size=1000):
    batch = []
    for sample in dataset:
        batch.append(sample["text"])
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

# Initialize tokenizer
tokenizer = Tokenizer(BPE())
trainer = BpeTrainer(vocab_size=50000, special_tokens=["<|endoftext|>"])

# Train (memory efficient - streams data)
tokenizer.train_from_iterator(
    batch_iterator(),
    trainer=trainer
)
```

**内存占用**：约200 MB（而加载完整数据集时需超过10 GB）

### 多文件训练

```python
import glob

# Find all training files
files = glob.glob("data/train/*.txt")
print(f"Training on {len(files)} files")

# Train on all files
tokenizer.train(files=files, trainer=trainer)
```

### 并行训练（多进程）

```python
from multiprocessing import Pool, cpu_count
import os

def train_shard(shard_files):
    """Train tokenizer on a shard of files."""
    tokenizer = Tokenizer(BPE())
    trainer = BpeTrainer(vocab_size=50000)
    tokenizer.train(files=shard_files, trainer=trainer)
    return tokenizer.get_vocab()

# Split files into shards
num_shards = cpu_count()
file_shards = [files[i::num_shards] for i in range(num_shards)]

# Train shards in parallel
with Pool(num_shards) as pool:
    vocab_shards = pool.map(train_shard, file_shards)

# Merge vocabularies (custom logic needed)
# This is a simplified example - real implementation would merge intelligently
final_vocab = {}
for vocab in vocab_shards:
    final_vocab.update(vocab)
```

## 领域专用分词器

### 代码分词器

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.normalizers import Sequence, NFC

# Code-optimized configuration
tokenizer = Tokenizer(BPE())

# Minimal normalization (preserve case, whitespace)
tokenizer.normalizer = NFC()  # Only normalize Unicode

# Byte-level pre-tokenization (handles all characters)
tokenizer.pre_tokenizer = ByteLevel()

# Train on code corpus
trainer = BpeTrainer(
    vocab_size=50000,
    special_tokens=["<|endoftext|>", "<|pad|>"],
    min_frequency=2
)

tokenizer.train(files=["code_corpus.txt"], trainer=trainer)
```

### 医学/科学领域分词器

```python
# Preserve case and special characters
from tokenizers.normalizers import NFKC
from tokenizers.pre_tokenizers import Whitespace, Punctuation, Sequence

tokenizer = Tokenizer(BPE())

# Minimal normalization
tokenizer.normalizer = NFKC()

# Preserve medical terms
tokenizer.pre_tokenizer = Sequence([
    Whitespace(),
    Punctuation(behavior="isolated")  # Keep punctuation separate
])

trainer = BpeTrainer(
    vocab_size=50000,
    special_tokens=["[UNK]", "[CLS]", "[SEP]"],
    min_frequency=3  # Higher threshold for rare medical terms
)

tokenizer.train(files=["pubmed_corpus.txt"], trainer=trainer)
```

### 多语言分词器

```python
# Handle multiple scripts
from tokenizers.normalizers import NFKC, Lowercase, Sequence

tokenizer = Tokenizer(BPE())

# Normalize but don't lowercase (preserves script differences)
tokenizer.normalizer = NFKC()

# Byte-level handles all Unicode
from tokenizers.pre_tokenizers import ByteLevel
tokenizer.pre_tokenizer = ByteLevel()

trainer = BpeTrainer(
    vocab_size=100000,  # Larger vocab for multiple languages
    special_tokens=["<unk>", "<s>", "</s>"],
    limit_alphabet=None  # No limit (handles all scripts)
)

# Train on multilingual corpus
tokenizer.train(files=["multilingual_corpus.txt"], trainer=trainer)
```

## 词汇表大小选择

### 按任务类型制定的指导原则

| 任务类型                  | 推荐词汇表大小       | 原因说明 |
|-------------------------|--------------------|----------|
| 英语（单语）            | 30,000 – 50,000     | 覆盖范围均衡 |
| 多语言                  | 50,000 – 250,000    | 语言种类越多，所需标记数越多 |
| 代码处理                | 30,000 – 50,000     | 与英语需求类似 |
| 领域专用内容            | 10,000 – 30,000     | 词汇量较小，更具针对性 |
| 字符级任务              | 1,000 – 5,000       | 仅包含字符及子词 |

### 词汇表大小的影响

**小型词汇表（10k）**：
- 优点：训练速度更快，模型体积更小，内存占用更低
- 缺点：每句所需的标记数更多，对未知词的处理能力较差

**中型词汇表（30k–50k）**：
- 优点：平衡性佳，为通用推荐选择
- 缺点：无（默认推荐配置）

**大型词汇表（100k+）**：
- 优点：每句标记数更少，对未知词的处理能力更强
- 缺点：训练速度较慢，嵌入表体积更大

### 实证测试结果

```python
# Train multiple tokenizers with different vocab sizes
vocab_sizes = [10000, 30000, 50000, 100000]

for vocab_size in vocab_sizes:
    tokenizer = Tokenizer(BPE())
    trainer = BpeTrainer(vocab_size=vocab_size)
    tokenizer.train(files=["sample.txt"], trainer=trainer)

    # Evaluate on test set
    test_text = "Test sentence for evaluation..."
    tokens = tokenizer.encode(test_text).ids

    print(f"Vocab: {vocab_size:6d} | Tokens: {len(tokens):3d} | Avg: {len(test_text)/len(tokens):.2f} chars/token")

# Example output:
# Vocab:  10000 | Tokens:  12 | Avg: 2.33 chars/token
# Vocab:  30000 | Tokens:   8 | Avg: 3.50 chars/token
# Vocab:  50000 | Tokens:   7 | Avg: 4.00 chars/token
# Vocab: 100000 | Tokens:   6 | Avg: 4.67 chars/token
```

## 测试分词器质量

### 覆盖率测试

```python
# Test on held-out data
test_corpus = load_dataset("wikitext", "wikitext-103-raw-v1", split="test")

total_tokens = 0
unk_tokens = 0
unk_id = tokenizer.token_to_id("[UNK]")

for text in test_corpus["text"]:
    if text.strip():
        encoding = tokenizer.encode(text)
        total_tokens += len(encoding.ids)
        unk_tokens += encoding.ids.count(unk_id)

unk_rate = unk_tokens / total_tokens
print(f"Unknown token rate: {unk_rate:.2%}")

# Good quality: <1% unknown tokens
# Acceptable: 1-5%
# Poor: >5%
```

### 压缩测试

```python
# Measure tokenization efficiency
import numpy as np

token_lengths = []

for text in test_corpus["text"][:1000]:
    if text.strip():
        encoding = tokenizer.encode(text)
        chars_per_token = len(text) / len(encoding.ids)
        token_lengths.append(chars_per_token)

avg_chars_per_token = np.mean(token_lengths)
print(f"Average characters per token: {avg_chars_per_token:.2f}")

# Good: 4-6 chars/token (English)
# Acceptable: 3-4 chars/token
# Poor: <3 chars/token (under-compression)
```

### 语义测试

```python
# Manually inspect tokenization of common words/phrases
test_phrases = [
    "tokenization",
    "machine learning",
    "artificial intelligence",
    "preprocessing",
    "hello world"
]

for phrase in test_phrases:
    tokens = tokenizer.encode(phrase).tokens
    print(f"{phrase:25s} → {tokens}")

# Good tokenization:
# tokenization              → ['token', 'ization']
# machine learning          → ['machine', 'learning']
# artificial intelligence   → ['artificial', 'intelligence']
```

## 故障排除

### 问题：训练速度过慢

**解决方案**：
1. 减小词汇表规模
2. 提高 `min_frequency` 的值
3. 使用 `limit_alphabet` 减少初始字母表范围
4. 先对数据子集进行训练

```python
# Fast training configuration
trainer = BpeTrainer(
    vocab_size=20000,      # Smaller vocab
    min_frequency=5,       # Higher threshold
    limit_alphabet=500,    # Limit alphabet
    show_progress=True
)
```

### 问题：未知标记比例过高

**解决方案**：
1. 增大词汇表规模
2. 降低 `min_frequency` 的数值
3. 检查标准化处理方式（可能过于严格）

```python
# Better coverage configuration
trainer = BpeTrainer(
    vocab_size=50000,      # Larger vocab
    min_frequency=1,       # Lower threshold
)
```

### 问题：分词质量不佳

**解决方案**：
1. 确认所使用的规范化处理方式符合您的应用场景需求
2. 检查预分词后的分割结果是否正确
3. 确保训练数据具有代表性
4. 尝试不同的算法（BPE、WordPiece 或 Unigram）

```python
# Debug tokenization pipeline
text = "Sample text to debug"

# Check normalization
normalized = tokenizer.normalizer.normalize_str(text)
print(f"Normalized: {normalized}")

# Check pre-tokenization
pre_tokens = tokenizer.pre_tokenizer.pre_tokenize_str(text)
print(f"Pre-tokens: {pre_tokens}")

# Check final tokenization
tokens = tokenizer.encode(text).tokens
print(f"Tokens: {tokens}")
```

## 最佳实践

1. **使用具有代表性的训练数据**——确保其与目标领域相匹配  
2. **从标准配置开始**——采用BERT WordPiece或GPT-2 BPE格式  
3. **在保留数据上开展测试**——统计未知标记的出现率  
4. **逐步调整词汇表规模**——分别测试3万、5万、10万个词条的版本  
5. **将分词器与模型一同保存**——保障实验结果的可复现性  
6. **为分词器版本进行编号**——记录变更历史以方便复现  
7. **对特殊标记做好文档记录**——这对模型训练至关重要
