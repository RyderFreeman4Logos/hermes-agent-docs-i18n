# 分词流程组件

关于规范化器、预分词器、模型、后处理器及解码器的完整指南。

## 流程概览

**完整的分词流程**：
```
Raw Text
  ↓
Normalization (cleaning, lowercasing)
  ↓
Pre-tokenization (split into words)
  ↓
Model (apply BPE/WordPiece/Unigram)
  ↓
Post-processing (add special tokens)
  ↓
Token IDs
```

**解码会反向执行该过程**：
```
Token IDs
  ↓
Decoder (handle special encodings)
  ↓
Raw Text
```

## 规范化工具

用于清理并标准化输入文本。

### 常用规范化工具

**小写转换**：
```python
from tokenizers.normalizers import Lowercase

tokenizer.normalizer = Lowercase()

# Input: "Hello WORLD"
# Output: "hello world"
```

**Unicode规范化**：
```python
from tokenizers.normalizers import NFD, NFC, NFKD, NFKC

# NFD: Canonical decomposition
tokenizer.normalizer = NFD()
# "é" → "e" + "́" (separate characters)

# NFC: Canonical composition (default)
tokenizer.normalizer = NFC()
# "e" + "́" → "é" (composed)

# NFKD: Compatibility decomposition
tokenizer.normalizer = NFKD()
# "ﬁ" → "f" + "i"

# NFKC: Compatibility composition
tokenizer.normalizer = NFKC()
# Most aggressive normalization
```

**移除重音符号**：
```python
from tokenizers.normalizers import StripAccents

tokenizer.normalizer = StripAccents()

# Input: "café"
# Output: "cafe"
```

**空白字符处理**：
```python
from tokenizers.normalizers import Strip, StripAccents

# Remove leading/trailing whitespace
tokenizer.normalizer = Strip()

# Input: "  hello  "
# Output: "hello"
```

**替换模式**：
```python
from tokenizers.normalizers import Replace

# Replace newlines with spaces
tokenizer.normalizer = Replace("\\n", " ")

# Input: "hello\\nworld"
# Output: "hello world"
```

### 组合规范化工具

```python
from tokenizers.normalizers import Sequence, NFD, Lowercase, StripAccents

# BERT-style normalization
tokenizer.normalizer = Sequence([
    NFD(),           # Unicode decomposition
    Lowercase(),     # Convert to lowercase
    StripAccents()   # Remove accents
])

# Input: "Café au Lait"
# After NFD: "Café au Lait" (e + ́)
# After Lowercase: "café au lait"
# After StripAccents: "cafe au lait"
```

### 使用场景示例

**不区分大小写的模型（BERT）**：
```python
from tokenizers.normalizers import BertNormalizer

# All-in-one BERT normalization
tokenizer.normalizer = BertNormalizer(
    clean_text=True,        # Remove control characters
    handle_chinese_chars=True,  # Add spaces around Chinese
    strip_accents=True,     # Remove accents
    lowercase=True          # Lowercase
)
```

**区分大小写的模型（GPT-2）**：
```python
# Minimal normalization
tokenizer.normalizer = NFC()  # Only normalize Unicode
```

**多语言模型（mBERT）**：
```python
# Preserve scripts, normalize form
tokenizer.normalizer = NFKC()
```

## 预分词器

在正式进行分词之前，先将文本拆分为类似单词的单元。

### 基于空白字符的分割

```python
from tokenizers.pre_tokenizers import Whitespace

tokenizer.pre_tokenizer = Whitespace()

# Input: "Hello world! How are you?"
# Output: [("Hello", (0, 5)), ("world!", (6, 12)), ("How", (13, 16)), ("are", (17, 20)), ("you?", (21, 25))]
```

### 标点符号隔离

```python
from tokenizers.pre_tokenizers import Punctuation

tokenizer.pre_tokenizer = Punctuation()

# Input: "Hello, world!"
# Output: [("Hello", ...), (",", ...), ("world", ...), ("!", ...)]
```

### 字节级（GPT-2）

```python
from tokenizers.pre_tokenizers import ByteLevel

tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)

# Input: "Hello world"
# Output: Byte-level tokens with Ġ prefix for spaces
# [("ĠHello", ...), ("Ġworld", ...)]
```

**核心功能**：可处理所有 Unicode 字符（256 字节组合）。

### Metaspace（SentencePiece）

对整个输入内容进行完整翻译，不得提前终止。

```python
from tokenizers.pre_tokenizers import Metaspace

tokenizer.pre_tokenizer = Metaspace(replacement="▁", add_prefix_space=True)

# Input: "Hello world"
# Output: [("▁Hello", ...), ("▁world", ...)]
```

**被以下模型使用**：T5、ALBERT（通过 SentencePiece 实现）

### 数字分割

```python
from tokenizers.pre_tokenizers import Digits

# Split digits individually
tokenizer.pre_tokenizer = Digits(individual_digits=True)

# Input: "Room 123"
# Output: [("Room", ...), ("1", ...), ("2", ...), ("3", ...)]

# Keep digits together
tokenizer.pre_tokenizer = Digits(individual_digits=False)

# Input: "Room 123"
# Output: [("Room", ...), ("123", ...)]
```

### BERT预分词器

```python
from tokenizers.pre_tokenizers import BertPreTokenizer

tokenizer.pre_tokenizer = BertPreTokenizer()

# Splits on whitespace and punctuation, preserves CJK
# Input: "Hello, 世界!"
# Output: [("Hello", ...), (",", ...), ("世", ...), ("界", ...), ("!", ...)]
```

### 组合预分词器

```python
from tokenizers.pre_tokenizers import Sequence, Whitespace, Punctuation

tokenizer.pre_tokenizer = Sequence([
    Whitespace(),     # Split on whitespace first
    Punctuation()     # Then isolate punctuation
])

# Input: "Hello, world!"
# After Whitespace: [("Hello,", ...), ("world!", ...)]
# After Punctuation: [("Hello", ...), (",", ...), ("world", ...), ("!", ...)]
```

### 预分词器对比

| 预分词器         | 使用场景                        | 示例                                      |
|-------------------|---------------------------------|--------------------------------------------|
| 空白字符处理       | 简单的英文文本                  | "Hello world" → ["Hello", "world"]         |
| 标点符号处理       | 分离特殊符号                    | "world!" → ["world", "!"]                  |
| 字节级处理         | 多语言及表情符号处理            | "🌍" → 字节级标记                            |
| 元空间处理         | SentencePiece风格                | "Hello" → ["▁Hello"]                       |
| BertPreTokenizer   | BERT风格（支持中日韩字符）        | "世界" → ["世", "界"]                        |
| 数字处理           | 处理数字序列                    | "123" → ["1", "2", "3"] 或 ["123"]        |

## 模型

核心分词算法。

### BPE模型

```python
from tokenizers.models import BPE

model = BPE(
    vocab=None,           # Or provide pre-built vocab
    merges=None,          # Or provide merge rules
    unk_token="[UNK]",    # Unknown token
    continuing_subword_prefix="",
    end_of_word_suffix="",
    fuse_unk=False        # Keep unknown tokens separate
)

tokenizer = Tokenizer(model)
```

**参数**：
- `vocab`：标记到编号的映射字典
- `merges`：合并规则列表，格式为 `["a b", "ab c"]`
- `unk_token`：用于表示未知单词的标记
- `continuing_subword_prefix`：子词的前缀（GPT-2模型为此字段设置为空）
- `end_of_word_suffix`：最后一个子词的后缀（GPT-2模型为此字段设置为空）

### WordPiece模型

```python
from tokenizers.models import WordPiece

model = WordPiece(
    vocab=None,
    unk_token="[UNK]",
    max_input_chars_per_word=100,  # Max word length
    continuing_subword_prefix="##"  # BERT-style prefix
)

tokenizer = Tokenizer(model)
```

**主要区别**：使用 `##` 前缀来表示后续的子词。

### 单语模型

```python
from tokenizers.models import Unigram

model = Unigram(
    vocab=None,  # List of (token, score) tuples
    unk_id=0,    # ID for unknown token
    byte_fallback=False  # Fall back to bytes if no match
)

tokenizer = Tokenizer(model)
```

**概率优先**：选择出现概率最高的分词方式。

### 单词级模型

```python
from tokenizers.models import WordLevel

# Simple word-to-ID mapping (no subwords)
model = WordLevel(
    vocab=None,
    unk_token="[UNK]"
)

tokenizer = Tokenizer(model)
```

**警告**：需要庞大的词汇量（每个单词对应一个标记）。

## 后处理工具

用于添加特殊标记并格式化输出结果。

### 模板处理

**BERT风格**（`[CLS] 句子内容 [SEP]`）：
```python
from tokenizers.processors import TemplateProcessing

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B [SEP]",
    special_tokens=[
        ("[CLS]", 101),
        ("[SEP]", 102),
    ],
)

# Single sentence
output = tokenizer.encode("Hello world")
# [101, ..., 102]  ([CLS] hello world [SEP])

# Sentence pair
output = tokenizer.encode("Hello", "world")
# [101, ..., 102, ..., 102]  ([CLS] hello [SEP] world [SEP])
```

**GPT-2风格**（`句子`）：
```python
tokenizer.post_processor = TemplateProcessing(
    single="$A <|endoftext|>",
    special_tokens=[
        ("<|endoftext|>", 50256),
    ],
)
```

**RoBERTa风格**（`<s> 句子 </s>`）：
```python
tokenizer.post_processor = TemplateProcessing(
    single="<s> $A </s>",
    pair="<s> $A </s> </s> $B </s>",
    special_tokens=[
        ("<s>", 0),
        ("</s>", 2),
    ],
)
```

**T5风格**（无需特殊标记）：
```python
# T5 doesn't add special tokens via post-processor
tokenizer.post_processor = None
```

### Roberta处理模块

```python
from tokenizers.processors import RobertaProcessing

tokenizer.post_processor = RobertaProcessing(
    sep=("</s>", 2),
    cls=("<s>", 0),
    add_prefix_space=True,  # Add space before first token
    trim_offsets=True       # Trim leading space from offsets
)
```

### 字节级处理

```python
from tokenizers.processors import ByteLevel as ByteLevelProcessing

tokenizer.post_processor = ByteLevelProcessing(
    trim_offsets=True  # Remove Ġ from offsets
)
```

## 解码器

将令牌 ID 转换回文本。

### 字节级解码器

```python
from tokenizers.decoders import ByteLevel

tokenizer.decoder = ByteLevel()

# Handles byte-level tokens
# ["ĠHello", "Ġworld"] → "Hello world"
```

### WordPiece 解码器

```python
from tokenizers.decoders import WordPiece

tokenizer.decoder = WordPiece(prefix="##")

# Removes ## prefix and concatenates
# ["token", "##ization"] → "tokenization"
```

### 元空间解码器

```python
from tokenizers.decoders import Metaspace

tokenizer.decoder = Metaspace(replacement="▁", add_prefix_space=True)

# Converts ▁ back to spaces
# ["▁Hello", "▁world"] → "Hello world"
```

### BPEDecoder 解码器

```python
from tokenizers.decoders import BPEDecoder

tokenizer.decoder = BPEDecoder(suffix="</w>")

# Removes suffix and concatenates
# ["token", "ization</w>"] → "tokenization"
```

### 序列解码器

```python
from tokenizers.decoders import Sequence, ByteLevel, Strip

tokenizer.decoder = Sequence([
    ByteLevel(),      # Decode byte-level first
    Strip(' ', 1, 1)  # Strip leading/trailing spaces
])
```

## 完整的流程示例

### BERT 分词器

```python
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.normalizers import BertNormalizer
from tokenizers.pre_tokenizers import BertPreTokenizer
from tokenizers.processors import TemplateProcessing
from tokenizers.decoders import WordPiece as WordPieceDecoder

# Model
tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))

# Normalization
tokenizer.normalizer = BertNormalizer(lowercase=True)

# Pre-tokenization
tokenizer.pre_tokenizer = BertPreTokenizer()

# Post-processing
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B [SEP]",
    special_tokens=[("[CLS]", 101), ("[SEP]", 102)],
)

# Decoder
tokenizer.decoder = WordPieceDecoder(prefix="##")

# Enable padding
tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")

# Enable truncation
tokenizer.enable_truncation(max_length=512)
```

### GPT-2 分词器

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.normalizers import NFC
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.processors import TemplateProcessing

# Model
tokenizer = Tokenizer(BPE())

# Normalization (minimal)
tokenizer.normalizer = NFC()

# Byte-level pre-tokenization
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=False)

# Post-processing
tokenizer.post_processor = TemplateProcessing(
    single="$A <|endoftext|>",
    special_tokens=[("<|endoftext|>", 50256)],
)

# Byte-level decoder
tokenizer.decoder = ByteLevelDecoder()
```

### T5 分词器（SentencePiece 风格）

```python
from tokenizers import Tokenizer
from tokenizers.models import Unigram
from tokenizers.normalizers import NFKC
from tokenizers.pre_tokenizers import Metaspace
from tokenizers.decoders import Metaspace as MetaspaceDecoder

# Model
tokenizer = Tokenizer(Unigram())

# Normalization
tokenizer.normalizer = NFKC()

# Metaspace pre-tokenization
tokenizer.pre_tokenizer = Metaspace(replacement="▁", add_prefix_space=True)

# No post-processing (T5 doesn't add CLS/SEP)
tokenizer.post_processor = None

# Metaspace decoder
tokenizer.decoder = MetaspaceDecoder(replacement="▁", add_prefix_space=True)
```

## 对齐跟踪

用于追踪原始文本中的标记位置。

### 基本对齐功能

```python
text = "Hello, world!"
output = tokenizer.encode(text)

for token, (start, end) in zip(output.tokens, output.offsets):
    print(f"{token:10s} → [{start:2d}, {end:2d}): {text[start:end]!r}")

# Output:
# [CLS]      → [ 0,  0): ''
# hello      → [ 0,  5): 'Hello'
# ,          → [ 5,  6): ','
# world      → [ 7, 12): 'world'
# !          → [12, 13): '!'
# [SEP]      → [ 0,  0): ''
```

### 单词级对齐

```python
# Get word_ids (which word each token belongs to)
encoding = tokenizer.encode("Hello world")
word_ids = encoding.word_ids

print(word_ids)
# [None, 0, 0, 1, None]
# None = special token, 0 = first word, 1 = second word
```

**应用场景**：令牌分类（命名实体识别）
```python
# Align predictions to words
predictions = ["O", "B-PER", "I-PER", "O", "O"]
word_predictions = {}

for token_idx, word_idx in enumerate(encoding.word_ids):
    if word_idx is not None and word_idx not in word_predictions:
        word_predictions[word_idx] = predictions[token_idx]

print(word_predictions)
# {0: "B-PER", 1: "O"}  # First word is PERSON, second is OTHER
```

### 时间跨度对齐

```python
# Find token span for character span
text = "Machine learning is awesome"
char_start, char_end = 8, 16  # "learning"

encoding = tokenizer.encode(text)

# Find token span
token_start = encoding.char_to_token(char_start)
token_end = encoding.char_to_token(char_end - 1) + 1

print(f"Tokens {token_start}:{token_end} = {encoding.tokens[token_start:token_end]}")
# Tokens 2:3 = ['learning']
```

**应用场景**：问答系统（提取答案片段）

## 自定义组件

### 自定义规范化器

```python
from tokenizers import NormalizedString, Normalizer

class CustomNormalizer:
    def normalize(self, normalized: NormalizedString):
        # Custom normalization logic
        normalized.lowercase()
        normalized.replace("  ", " ")  # Replace double spaces

# Use custom normalizer
tokenizer.normalizer = CustomNormalizer()
```

### 自定义预分词器

```python
from tokenizers import PreTokenizedString

class CustomPreTokenizer:
    def pre_tokenize(self, pretok: PreTokenizedString):
        # Custom pre-tokenization logic
        pretok.split(lambda i, char: char.isspace())

tokenizer.pre_tokenizer = CustomPreTokenizer()
```

## 故障排除

### 问题：偏移量不一致

**症状**：偏移量与原始文本不匹配
```python
text = "  hello"  # Leading spaces
offsets = [(0, 5)]  # Expects "  hel"
```

**解决方案**：检查标准化处理是否去除了空格。
```python
# Preserve offsets
tokenizer.normalizer = Sequence([
    Strip(),  # This changes offsets!
])

# Use trim_offsets in post-processor instead
tokenizer.post_processor = ByteLevelProcessing(trim_offsets=True)
```

### 问题：特殊标记未被添加

**症状**：输出结果中不存在 [CLS] 或 [SEP] 标记

**解决方案**：检查后处理模块是否已正确配置
```python
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    special_tokens=[("[CLS]", 101), ("[SEP]", 102)],
)
```

### 问题：解码错误

**症状**：解码后的文本中出现##或△字符

**解决方案**：设置正确的解码器
```python
# For WordPiece
tokenizer.decoder = WordPieceDecoder(prefix="##")

# For SentencePiece
tokenizer.decoder = MetaspaceDecoder(replacement="▁")
```

## 最佳实践

1. **使处理流程与模型架构相匹配**：
   - BERT → BertNormalizer + BertPreTokenizer + WordPiece
   - GPT-2 → NFC + ByteLevel + BPE
   - T5 → NFKC + Metaspace + Unigram

2. **使用示例输入测试处理流程**：
   - 检查标准化处理是否过度处理
   - 验证预分词操作能否正确拆分文本
   - 确保解码过程能够还原原始文本

3. **为后续任务保留对齐信息**：
   - 在标准化模块中使用 `trim_offsets` 而非直接删除内容
   - 对示例文本片段测试 `char_to_token()` 函数

4. **记录处理流程的详细信息**：
   - 保存完整的分词器配置文件
   - 记录所有特殊标记的用途
   - 注明任何自定义组件及其功能
