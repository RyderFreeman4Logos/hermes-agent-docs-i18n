---
name: nemo-curator
description: "Curate LLM training data: dedupe, filter, PII redaction."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [nemo-curator, cudf, dask, rapids]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Data Processing, NeMo Curator, Data Curation, GPU Acceleration, Deduplication, Quality Filtering, NVIDIA, RAPIDS, PII Redaction, Multimodal, LLM Training Data]

---

# NeMo Curator——基于GPU的数据整理工具

NVIDIA专为LLM准备高质量训练数据而打造的工具包。

## 何时使用NeMo Curator

**以下情况建议使用NeMo Curator：**
- 从网络爬取数据（如Common Crawl）来准备LLM训练数据
- 需要快速进行数据去重处理（速度是CPU的16倍）
- 对多模态数据集（文本、图像、视频、音频）进行整理
- 过滤低质量或有害内容
- 在GPU集群上扩展数据处理规模

**性能优势：**
- 模糊去重速度提升16倍（处理8TB的RedPajama v2数据）
- 相较于CPU方案，总体拥有成本降低40%
- 在多个GPU节点之间可实现近乎线性的性能扩展

**可选替代方案：**
- **datatrove**：基于CPU的开源数据处理工具
- **dolma**：Allen AI提供的数据处理工具包
- **Ray Data**：通用的机器学习数据处理工具（不侧重数据整理功能）

## 快速入门

### 安装指南

```bash
# Text curation (CUDA 12)
uv pip install "nemo-curator[text_cuda12]"

# All modalities
uv pip install "nemo-curator[all_cuda12]"

# CPU-only (slower)
uv pip install "nemo-curator[cpu]"
```

### 基础文本整理流程

```python
from nemo_curator import ScoreFilter, Modify
from nemo_curator.datasets import DocumentDataset
import pandas as pd

# Load data
df = pd.DataFrame({"text": ["Good document", "Bad doc", "Excellent text"]})
dataset = DocumentDataset(df)

# Quality filtering
def quality_score(doc):
    return len(doc["text"].split()) > 5  # Filter short docs

filtered = ScoreFilter(quality_score)(dataset)

# Deduplication
from nemo_curator.modules import ExactDuplicates
deduped = ExactDuplicates()(filtered)

# Save
deduped.to_parquet("curated_data/")
```

## 数据筛选流程

### 第一阶段：质量过滤

```python
from nemo_curator.filters import (
    WordCountFilter,
    RepeatedLinesFilter,
    UrlRatioFilter,
    NonAlphaNumericFilter
)

# Apply 30+ heuristic filters
from nemo_curator import ScoreFilter

# Word count filter
dataset = dataset.filter(WordCountFilter(min_words=50, max_words=100000))

# Remove repetitive content
dataset = dataset.filter(RepeatedLinesFilter(max_repeated_line_fraction=0.3))

# URL ratio filter
dataset = dataset.filter(UrlRatioFilter(max_url_ratio=0.2))
```

### 第二阶段：去重处理

**精确去重**：
```python
from nemo_curator.modules import ExactDuplicates

# Remove exact duplicates
deduped = ExactDuplicates(id_field="id", text_field="text")(dataset)
```

**模糊去重功能**（在 GPU 上的处理速度提升 16 倍）：
```python
from nemo_curator.modules import FuzzyDuplicates

# MinHash + LSH deduplication
fuzzy_dedup = FuzzyDuplicates(
    id_field="id",
    text_field="text",
    num_hashes=260,      # MinHash parameters
    num_buckets=20,
    hash_method="md5"
)

deduped = fuzzy_dedup(dataset)
```

**语义去重**：
```python
from nemo_curator.modules import SemanticDuplicates

# Embedding-based deduplication
semantic_dedup = SemanticDuplicates(
    id_field="id",
    text_field="text",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    threshold=0.8  # Cosine similarity threshold
)

deduped = semantic_dedup(dataset)
```

### 第三阶段：个人身份信息脱敏处理

```python
from nemo_curator.modules import Modify
from nemo_curator.modifiers import PIIRedactor

# Redact personally identifiable information
pii_redactor = PIIRedactor(
    supported_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "LOCATION"],
    anonymize_action="replace"  # or "redact"
)

redacted = Modify(pii_redactor)(dataset)
```

### 第4阶段：分类器过滤

```python
from nemo_curator.classifiers import QualityClassifier

# Quality classification
quality_clf = QualityClassifier(
    model_path="nvidia/quality-classifier-deberta",
    batch_size=256,
    device="cuda"
)

# Filter low-quality documents
high_quality = dataset.filter(lambda doc: quality_clf(doc["text"]) > 0.5)
```

## GPU加速功能

### GPU与CPU的性能对比

| 操作任务 | CPU（16核） | GPU（A100） | 加速倍数 |
|---------|----------------|------------|---------|
| 模糊去重（8TB） | 120小时 | 7.5小时 | 16倍 |
| 精确去重（1TB） | 8小时 | 0.5小时 | 16倍 |
| 质量过滤 | 2小时 | 0.2小时 | 10倍 |

### 多GPU扩展方案

```python
from nemo_curator import get_client
import dask_cuda

# Initialize GPU cluster
client = get_client(cluster_type="gpu", n_workers=8)

# Process with 8 GPUs
deduped = FuzzyDuplicates(...)(dataset)
```

## 多模态内容精选

### 图片内容精选

```python
from nemo_curator.image import (
    AestheticFilter,
    NSFWFilter,
    CLIPEmbedder
)

# Aesthetic scoring
aesthetic_filter = AestheticFilter(threshold=5.0)
filtered_images = aesthetic_filter(image_dataset)

# NSFW detection
nsfw_filter = NSFWFilter(threshold=0.9)
safe_images = nsfw_filter(filtered_images)

# Generate CLIP embeddings
clip_embedder = CLIPEmbedder(model="openai/clip-vit-base-patch32")
image_embeddings = clip_embedder(safe_images)
```

### 视频精选

```python
from nemo_curator.video import (
    SceneDetector,
    ClipExtractor,
    InternVideo2Embedder
)

# Detect scenes
scene_detector = SceneDetector(threshold=27.0)
scenes = scene_detector(video_dataset)

# Extract clips
clip_extractor = ClipExtractor(min_duration=2.0, max_duration=10.0)
clips = clip_extractor(scenes)

# Generate embeddings
video_embedder = InternVideo2Embedder()
video_embeddings = video_embedder(clips)
```

### 音频内容精选

```python
from nemo_curator.audio import (
    ASRInference,
    WERFilter,
    DurationFilter
)

# ASR transcription
asr = ASRInference(model="nvidia/stt_en_fastconformer_hybrid_large_pc")
transcribed = asr(audio_dataset)

# Filter by WER (word error rate)
wer_filter = WERFilter(max_wer=0.3)
high_quality_audio = wer_filter(transcribed)

# Duration filtering
duration_filter = DurationFilter(min_duration=1.0, max_duration=30.0)
filtered_audio = duration_filter(high_quality_audio)
```

## 常见模式

### 网页抓取整理（Common Crawl）

```python
from nemo_curator import ScoreFilter, Modify
from nemo_curator.filters import *
from nemo_curator.modules import *
from nemo_curator.datasets import DocumentDataset

# Load Common Crawl data
dataset = DocumentDataset.read_parquet("common_crawl/*.parquet")

# Pipeline
pipeline = [
    # 1. Quality filtering
    WordCountFilter(min_words=100, max_words=50000),
    RepeatedLinesFilter(max_repeated_line_fraction=0.2),
    SymbolToWordRatioFilter(max_symbol_to_word_ratio=0.3),
    UrlRatioFilter(max_url_ratio=0.3),

    # 2. Language filtering
    LanguageIdentificationFilter(target_languages=["en"]),

    # 3. Deduplication
    ExactDuplicates(id_field="id", text_field="text"),
    FuzzyDuplicates(id_field="id", text_field="text", num_hashes=260),

    # 4. PII redaction
    PIIRedactor(),

    # 5. NSFW filtering
    NSFWClassifier(threshold=0.8)
]

# Execute
for stage in pipeline:
    dataset = stage(dataset)

# Save
dataset.to_parquet("curated_common_crawl/")
```

### 分布式处理

```python
from nemo_curator import get_client
from dask_cuda import LocalCUDACluster

# Multi-GPU cluster
cluster = LocalCUDACluster(n_workers=8)
client = get_client(cluster=cluster)

# Process large dataset
dataset = DocumentDataset.read_parquet("s3://large_dataset/*.parquet")
deduped = FuzzyDuplicates(...)(dataset)

# Cleanup
client.close()
cluster.close()
```

## 性能基准测试

### 模糊去重处理（8TB RedPajama v2）

- **CPU（256核）**：120小时
- **GPU（8× A100）**：7.5小时
- **加速比**：16倍

### 精确去重处理（1TB）

- **CPU（64核）**：8小时
- **GPU（4× A100）**：0.5小时
- **加速比**：16倍

### 质量过滤（100GB）

- **CPU（32核）**：2小时
- **GPU（2× A100）**：0.2小时
- **加速比**：10倍

## 成本对比

**基于CPU的处理方式**（AWS c5.18xlarge × 10台）：
- 成本：3.60美元/小时 × 10 = 36美元/小时
- 处理8TB数据所需时间：120小时
- **总成本**：4,320美元

**基于GPU的处理方式**（AWS p4d.24xlarge × 2台）：
- 成本：32.77美元/小时 × 2 = 65.54美元/小时
- 处理8TB数据所需时间：7.5小时
- **总成本**：491.55美元

**节省费用**：成本降低89%，可节省3,828美元

## 支持的数据格式

- **输入格式**：Parquet、JSONL、CSV
- **输出格式**：Parquet（推荐）、JSONL
- **WebDataset**：用于多模态数据的TAR压缩包

## 应用场景

**生产环境部署**：
- NVIDIA曾使用NeMo Curator来准备Nemotron-4的训练数据
- 已整理的开源数据集包括：RedPajama v2、The Pile

## 参考资料

- **[过滤指南](references/filtering.md)** – 提供30多种质量过滤规则与算法建议
- **[去重指南](references/deduplication.md)** – 介绍精确去重、模糊去重及语义去重方法

## 相关资源

- **GitHub仓库**：https://github.com/NVIDIA/NeMo-Curator ⭐ 500+星标
- **文档页面**：https://docs.nvidia.com/nemo-framework/user-guide/latest/datacuration/
- **当前版本**：0.4.0及以上
- **许可证**：Apache 2.0



