# DSPy优化器（提示词辅助工具）

全面了解DSPy的优化算法，助力提升提示词质量与模型权重表现。

## 什么是优化器？

DSPy优化器（被称为“提示词辅助工具”）可通过以下方式自动优化您的模块：
- **从训练数据中合成少样本示例**
- **通过搜索提出更优的指令**
- **微调模型权重**（可选）

**核心理念**：无需手动调整提示词，只需定义评估指标，让DSPy自动完成优化。

## 优化器选择指南

| 优化器 | 最佳适用场景 | 速度 | 质量 | 所需数据量 |
|-------|------------|------|------|------------|
| BootstrapFewShot | 多场景通用优化 | 快 | 良好 | 10-50个示例 |
| MIPRO | 指令微调 | 中等 | 优秀 | 50-200个示例 |
| BootstrapFinetune | 模型深度微调 | 慢 | 优秀 | 100个以上示例 |
| COPRO | 提示词优化 | 中等 | 良好 | 20-100个示例 |
| KNNFewShot | 快速基准测试 | 非常快 | 一般 | 10个以上示例 |

## 核心优化器

### BootstrapFewShot

**最受欢迎的优化器**——从训练数据中生成少样本演示案例。

**工作原理：**
1. 获取您的训练样本
2. 利用您的模块生成预测结果
3. 根据评估指标筛选高质量预测
4. 将这些预测作为后续提示词中的少样本示例

**参数设置：**
- `metric`：用于评估预测结果的函数（必填）
- `max_bootstrapped_demos`：最多生成的演示案例数量（默认值：4）
- `max_labeled_demos`：最多可使用的带标签示例数量（默认值：16）
- `max_rounds`：优化迭代次数（默认值：1）
- `metric_threshold`：可接受的最低分数阈值（可选）

```python
import dspy
from dspy.teleprompt import BootstrapFewShot

# Define metric
def validate_answer(example, pred, trace=None):
    """Return True if prediction matches gold answer."""
    return example.answer.lower() == pred.answer.lower()

# Training data
trainset = [
    dspy.Example(question="What is 2+2?", answer="4").with_inputs("question"),
    dspy.Example(question="What is 3+5?", answer="8").with_inputs("question"),
    dspy.Example(question="What is 10-3?", answer="7").with_inputs("question"),
]

# Create module
qa = dspy.ChainOfThought("question -> answer")

# Optimize
optimizer = BootstrapFewShot(
    metric=validate_answer,
    max_bootstrapped_demos=3,
    max_rounds=2
)

optimized_qa = optimizer.compile(qa, trainset=trainset)

# Now optimized_qa has learned few-shot examples!
result = optimized_qa(question="What is 5+7?")
```

**最佳实践：**
- 从 10 到 50 个训练样本开始
- 使用涵盖边缘情况的多样化样本
- 对于大多数任务，将 `max_bootstrapped_demos` 设置为 3-5
- 若希望提升质量，可提高 `max_rounds` 的数值至 2-3

**适用场景：**
- 首选尝试的优化器
- 您拥有 10 个及以上已标注的样本
- 希望快速获得改进效果
- 用于通用任务

### MIPRO（最重要的提示词优化工具）

**最先进的优化器**——通过迭代方式不断寻找更优的指令。

**工作原理：**
1. 生成候选指令
2. 在验证集上测试每个候选指令
3. 选择表现最佳的指令
4. 重复迭代以进一步优化

**参数设置：**
- `metric`：评估指标（必填）
- `num_candidates`：每次迭代需尝试的指令数量（默认值：10）
- `init_temperature`：采样温度（默认值：1.0）
- `verbose`：是否显示进度信息（默认值：False）

```python
from dspy.teleprompt import MIPRO

# Define metric with more nuance
def answer_quality(example, pred, trace=None):
    """Score answer quality 0-1."""
    if example.answer.lower() in pred.answer.lower():
        return 1.0
    # Partial credit for similar answers
    return 0.5 if len(set(example.answer.split()) & set(pred.answer.split())) > 0 else 0.0

# Larger training set (MIPRO benefits from more data)
trainset = [...]  # 50-200 examples
valset = [...]    # 20-50 examples

# Create module
qa = dspy.ChainOfThought("question -> answer")

# Optimize with MIPRO
optimizer = MIPRO(
    metric=answer_quality,
    num_candidates=10,
    init_temperature=1.0,
    verbose=True
)

optimized_qa = optimizer.compile(
    student=qa,
    trainset=trainset,
    valset=valset,  # MIPRO uses separate validation set
    num_trials=100   # More trials = better quality
)
```

**最佳实践：**
- 使用 50–200 个训练样本
- 设置独立的验证集（20–50 个样本）
- 为获得最佳效果，建议运行 100–200 次迭代
- 典型处理时间约为 10–30 分钟

**适用场景：**
- 您拥有 50 个以上已标注的样本
- 希望获得最先进的模型性能
- 愿意等待模型优化完成
- 需要处理复杂的推理任务

### BootstrapFinetune

**微调模型权重**——用于生成用于微调的训练数据集。

**工作原理：**
1. 生成合成训练数据
2. 以微调所需的格式导出数据
3. 您可单独对模型进行微调
4. 将微调后的模型重新加载

**参数：**
- `metric`：评估指标（必填）
- `max_bootstrapped_demos`：需生成的示例数量（默认值：4）
- `max_rounds`：数据生成轮数（默认值：1）

```python
from dspy.teleprompt import BootstrapFinetune

# Training data
trainset = [...]  # 100+ examples recommended

# Define metric
def validate(example, pred, trace=None):
    return example.answer == pred.answer

# Create module
qa = dspy.ChainOfThought("question -> answer")

# Generate fine-tuning data
optimizer = BootstrapFinetune(metric=validate)
optimized_qa = optimizer.compile(qa, trainset=trainset)

# Exports training data to file
# You then fine-tune using your LM provider's API

# After fine-tuning, load your model:
finetuned_lm = dspy.OpenAI(model="ft:gpt-3.5-turbo:your-model-id")
dspy.settings.configure(lm=finetuned_lm)
```

**最佳实践：**
- 使用100个以上的训练样本
- 在保留的测试集上进行验证
- 监控过拟合现象
- 首先与基于提示词的方法进行比较

**适用场景：**
- 您拥有100个以上的样本
- 延迟是关键考量因素（微调后的模型响应更快）
- 任务范围明确且具体
- 仅通过优化提示词无法达到理想效果

### COPRO（坐标式提示词优化）

**通过无梯度搜索来优化提示词。**

**工作原理：**
1. 生成不同的提示词变体
2. 评估每个变体的效果
3. 选择最优的提示词
4. 通过迭代不断优化

```python
from dspy.teleprompt import COPRO

# Training data
trainset = [...]

# Define metric
def metric(example, pred, trace=None):
    return example.answer == pred.answer

# Create module
qa = dspy.ChainOfThought("question -> answer")

# Optimize with COPRO
optimizer = COPRO(
    metric=metric,
    breadth=10,  # Candidates per iteration
    depth=3      # Optimization rounds
)

optimized_qa = optimizer.compile(qa, trainset=trainset)
```

**适用场景：**
- 需要优化提示词效果
- 已拥有20至100个示例
- MIPRO运行速度过慢

### KNNFewShot

**简单k近邻算法**——为每个查询挑选相似的示例。

**工作原理：**
1. 对所有训练示例进行嵌入处理
2. 针对每个查询，找出最相似的k个示例
3. 将这些示例作为少样本示范数据使用

```python
from dspy.teleprompt import KNNFewShot

trainset = [...]

# No metric needed - just selects similar examples
optimizer = KNNFewShot(k=3)
optimized_qa = optimizer.compile(qa, trainset=trainset)

# For each query, uses 3 most similar examples from trainset
```

**适用场景：**
- 快速获取基准结果
- 拥有多样化的训练样本
- 相似度可作为衡量实用性的有效替代指标

## 指标编写

指标是用于对预测结果进行评分的函数，对于优化过程而言至关重要。

### 二元指标

```python
def exact_match(example, pred, trace=None):
    """Return True if prediction exactly matches gold."""
    return example.answer == pred.answer

def contains_answer(example, pred, trace=None):
    """Return True if prediction contains gold answer."""
    return example.answer.lower() in pred.answer.lower()
```

### 持续指标采集

```python
def f1_score(example, pred, trace=None):
    """F1 score between prediction and gold."""
    pred_tokens = set(pred.answer.lower().split())
    gold_tokens = set(example.answer.lower().split())

    if not pred_tokens:
        return 0.0

    precision = len(pred_tokens & gold_tokens) / len(pred_tokens)
    recall = len(pred_tokens & gold_tokens) / len(gold_tokens)

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)

def semantic_similarity(example, pred, trace=None):
    """Embedding similarity between prediction and gold."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')

    emb1 = model.encode(example.answer)
    emb2 = model.encode(pred.answer)

    similarity = cosine_similarity(emb1, emb2)
    return similarity
```

### 多维度指标

```python
def comprehensive_metric(example, pred, trace=None):
    """Combine multiple factors."""
    score = 0.0

    # Correctness (50%)
    if example.answer.lower() in pred.answer.lower():
        score += 0.5

    # Conciseness (25%)
    if len(pred.answer.split()) <= 20:
        score += 0.25

    # Citation (25%)
    if "source:" in pred.answer.lower():
        score += 0.25

    return score
```

### 使用 Trace 进行调试

```python
def metric_with_trace(example, pred, trace=None):
    """Metric that uses trace for debugging."""
    is_correct = example.answer == pred.answer

    if trace is not None and not is_correct:
        # Log failures for analysis
        print(f"Failed on: {example.question}")
        print(f"Expected: {example.answer}")
        print(f"Got: {pred.answer}")

    return is_correct
```

## 评估最佳实践

### 训练集/验证集/测试集划分

```python
# Split data
trainset = data[:100]   # 70%
valset = data[100:120]  # 15%
testset = data[120:]    # 15%

# Optimize on train
optimized = optimizer.compile(module, trainset=trainset)

# Validate during optimization (for MIPRO)
optimized = optimizer.compile(module, trainset=trainset, valset=valset)

# Evaluate on test
from dspy.evaluate import Evaluate
evaluator = Evaluate(devset=testset, metric=metric)
score = evaluator(optimized)
```

### 交叉验证

```python
from sklearn.model_selection import KFold

kfold = KFold(n_splits=5)
scores = []

for train_idx, val_idx in kfold.split(data):
    trainset = [data[i] for i in train_idx]
    valset = [data[i] for i in val_idx]

    optimized = optimizer.compile(module, trainset=trainset)
    score = evaluator(optimized, devset=valset)
    scores.append(score)

print(f"Average score: {sum(scores) / len(scores):.2f}")
```

### 优化器对比

```python
results = {}

for opt_name, optimizer in [
    ("baseline", None),
    ("fewshot", BootstrapFewShot(metric=metric)),
    ("mipro", MIPRO(metric=metric)),
]:
    if optimizer is None:
        module_opt = module
    else:
        module_opt = optimizer.compile(module, trainset=trainset)

    score = evaluator(module_opt, devset=testset)
    results[opt_name] = score

print(results)
# {'baseline': 0.65, 'fewshot': 0.78, 'mipro': 0.85}
```

## 高级模式

### 自定义优化器

```python
from dspy.teleprompt import Teleprompter

class CustomOptimizer(Teleprompter):
    def __init__(self, metric):
        self.metric = metric

    def compile(self, student, trainset, **kwargs):
        # Your optimization logic here
        # Return optimized student module
        return student
```

### 多阶段优化

```python
# Stage 1: Bootstrap few-shot
stage1 = BootstrapFewShot(metric=metric, max_bootstrapped_demos=3)
optimized1 = stage1.compile(module, trainset=trainset)

# Stage 2: Instruction tuning
stage2 = MIPRO(metric=metric, num_candidates=10)
optimized2 = stage2.compile(optimized1, trainset=trainset, valset=valset)

# Final optimized module
final_module = optimized2
```

### 集群优化

```python
class EnsembleModule(dspy.Module):
    def __init__(self, modules):
        super().__init__()
        self.modules = modules

    def forward(self, question):
        predictions = [m(question=question).answer for m in self.modules]
        # Vote or average
        return dspy.Prediction(answer=max(set(predictions), key=predictions.count))

# Optimize multiple modules
opt1 = BootstrapFewShot(metric=metric).compile(module, trainset=trainset)
opt2 = MIPRO(metric=metric).compile(module, trainset=trainset)
opt3 = COPRO(metric=metric).compile(module, trainset=trainset)

# Ensemble
ensemble = EnsembleModule([opt1, opt2, opt3])
```

## 优化工作流程

### 1. 从基准值开始

```python
# No optimization
baseline = dspy.ChainOfThought("question -> answer")
baseline_score = evaluator(baseline, devset=testset)
print(f"Baseline: {baseline_score}")
```

### 2. 尝试使用 BootstrapFewShot

```python
# Quick optimization
fewshot = BootstrapFewShot(metric=metric, max_bootstrapped_demos=3)
optimized = fewshot.compile(baseline, trainset=trainset)
fewshot_score = evaluator(optimized, devset=testset)
print(f"Few-shot: {fewshot_score} (+{fewshot_score - baseline_score:.2f})")
```

### 3. 若有更多数据可用，可尝试使用 MIPRO

```python
# State-of-the-art optimization
mipro = MIPRO(metric=metric, num_candidates=10)
optimized_mipro = mipro.compile(baseline, trainset=trainset, valset=valset)
mipro_score = evaluator(optimized_mipro, devset=testset)
print(f"MIPRO: {mipro_score} (+{mipro_score - baseline_score:.2f})")
```

### 4. 保存最佳模型

```python
if mipro_score > fewshot_score:
    optimized_mipro.save("models/best_model.json")
else:
    optimized.save("models/best_model.json")
```

## 常见问题

### 1. 对训练数据过度拟合

```python
# ❌ Bad: Too many demos
optimizer = BootstrapFewShot(max_bootstrapped_demos=20)  # Overfits!

# ✅ Good: Moderate demos
optimizer = BootstrapFewShot(max_bootstrapped_demos=3-5)
```

### 2. 指标与任务不匹配

```python
# ❌ Bad: Binary metric for nuanced task
def bad_metric(example, pred, trace=None):
    return example.answer == pred.answer  # Too strict!

# ✅ Good: Graded metric
def good_metric(example, pred, trace=None):
    return f1_score(example.answer, pred.answer)  # Allows partial credit
```

### 3. 训练数据不足

```python
# ❌ Bad: Too little data
trainset = data[:5]  # Not enough!

# ✅ Good: Sufficient data
trainset = data[:50]  # Better
```

### 4. 无验证集

```python
# ❌ Bad: Optimizing on test set
optimizer.compile(module, trainset=testset)  # Cheating!

# ✅ Good: Proper splits
optimizer.compile(module, trainset=trainset, valset=valset)
evaluator(optimized, devset=testset)
```

## 性能优化建议

1. **从简单开始**：先使用 BootstrapFewShot 
2. **使用具有代表性的数据**：覆盖各种边界情况
3. **监控过拟合现象**：在保留的测试集上进行验证
4. **持续评估指标**：根据测试结果不断优化
5. **保存检查点**：避免丢失训练进度
6. **与基准模型对比**：衡量改进程度
7. **测试多种优化器**：找到最佳方案

## 相关资源

- **论文**：《DSPy：将声明式语言模型调用转化为自我优化流程》
- **GitHub 仓库**：https://github.com/stanfordnlp/dspy
- **Discord 社群**：https://discord.gg/XCGy2WDCQB
