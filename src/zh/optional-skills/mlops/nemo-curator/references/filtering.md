# 质量过滤指南

全面介绍 NeMo Curator 的 30 多种质量过滤功能。

## 基于文本的过滤规则

### 单词数量限制

```python
from nemo_curator.filters import WordCountFilter

# Filter by word count
dataset = dataset.filter(WordCountFilter(min_words=50, max_words=100000))
```

### 重复内容

```python
from nemo_curator.filters import RepeatedLinesFilter

# Remove documents with >30% repeated lines
dataset = dataset.filter(RepeatedLinesFilter(max_repeated_line_fraction=0.3))
```

### 符号比例

```python
from nemo_curator.filters import SymbolToWordRatioFilter

# Remove documents with too many symbols
dataset = dataset.filter(SymbolToWordRatioFilter(max_symbol_to_word_ratio=0.3))
```

### URL比例

```python
from nemo_curator.filters import UrlRatioFilter

# Remove documents with many URLs
dataset = dataset.filter(UrlRatioFilter(max_url_ratio=0.2))
```

## 语言过滤

```python
from nemo_curator.filters import LanguageIdentificationFilter

# Keep only English documents
dataset = dataset.filter(LanguageIdentificationFilter(target_languages=["en"]))

# Multiple languages
dataset = dataset.filter(LanguageIdentificationFilter(target_languages=["en", "es", "fr"]))
```

## 基于分类器的过滤机制

### 质量分类器

```python
from nemo_curator.classifiers import QualityClassifier

quality_clf = QualityClassifier(
    model_path="nvidia/quality-classifier-deberta",
    batch_size=256,
    device="cuda"
)

# Filter low-quality (threshold > 0.5 = high quality)
dataset = dataset.filter(lambda doc: quality_clf(doc["text"]) > 0.5)
```

### 不适宜工作场所内容分类器

```python
from nemo_curator.classifiers import NSFWClassifier

nsfw_clf = NSFWClassifier(threshold=0.9, device="cuda")

# Remove NSFW content
dataset = dataset.filter(lambda doc: nsfw_clf(doc["text"]) < 0.9)
```

## 启发式过滤器

30多种过滤器的完整列表：
- WordCountFilter
- RepeatedLinesFilter
- UrlRatioFilter
- SymbolToWordRatioFilter
- NonAlphaNumericFilter
- BulletsFilter
- WhiteSpaceFilter
- ParenthesesFilter
- LongWordFilter
- 以及20多种其他过滤器……

## 最佳实践

1. **优先使用低成本过滤器**——先进行字数统计，再使用GPU分类器
2. **根据样本调整阈值**——在全面运行前，先用1万份文档进行测试
3. **谨慎使用GPU分类器**——虽然成本高昂，但效果显著
4. **高效地串联过滤器**——按成本从低到高排序使用
