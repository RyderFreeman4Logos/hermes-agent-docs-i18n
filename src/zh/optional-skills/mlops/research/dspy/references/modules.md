# DSPy 模块

关于用于语言模型编程的 DSPy 内置模块的完整指南。

## 模块基础

DSPy 模块是受 PyTorch 神经网络模块启发的可组合构建单元：
- 包含可学习参数（提示词、少样本示例）
- 可通过 Python 控制流进行组合
- 具有通用性，可处理任意函数签名
- 可使用 DSPy 优化器进行优化

### 基础模块模式

```python
import dspy

class CustomModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # Initialize sub-modules
        self.predictor = dspy.Predict("input -> output")

    def forward(self, input):
        # Module logic
        result = self.predictor(input=input)
        return result
```

## 核心模块

### dspy.Predict

**基础预测模块**——直接调用语言模型，无需进行推理步骤。

```python
# Inline signature
qa = dspy.Predict("question -> answer")
result = qa(question="What is 2+2?")

# Class signature
class QA(dspy.Signature):
    """Answer questions concisely."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="short, factual answer")

qa = dspy.Predict(QA)
result = qa(question="What is the capital of France?")
print(result.answer)  # "Paris"
```

**适用场景：**
- 需要简单直接的预测结果
- 不需要推理步骤
- 要求快速响应

### dspy.ChainOfThought

**逐步推理**——在给出答案之前先生成推理过程。

**参数：**
- `signature`：任务签名
- `rationale_field`：自定义推理字段（可选）
- `rationale_field_type`：推理内容的类型（默认值为 `str`）

```python
# Basic usage
cot = dspy.ChainOfThought("question -> answer")
result = cot(question="If I have 5 apples and give away 2, how many remain?")
print(result.rationale)  # "Let's think step by step..."
print(result.answer)     # "3"

# Custom rationale field
cot = dspy.ChainOfThought(
    signature="problem -> solution",
    rationale_field=dspy.OutputField(
        prefix="Reasoning: Let's break this down step by step to"
    )
)
```

**适用场景：**
- 复杂推理任务
- 数学应用题
- 逻辑演绎
- 更注重准确性而非速度

**性能表现：**
- 性能约为 Predict 的两倍慢
- 在推理任务中的准确率显著更高

### dspy.ProgramOfThought

**基于代码的推理**——用于生成并执行 Python 代码。

```python
pot = dspy.ProgramOfThought("question -> answer")

result = pot(question="What is 15% of 240?")
# Internally generates: answer = 240 * 0.15
# Executes code and returns result
print(result.answer)  # 36.0

result = pot(question="If a train travels 60 mph for 2.5 hours, how far does it go?")
# Generates: distance = 60 * 2.5
print(result.answer)  # 150.0
```

**适用场景：**
- 算术运算
- 符号数学计算
- 数据转换
- 确定性计算

**优势：**
- 比基于文本的数学计算更可靠
- 能处理复杂计算任务
- 具有透明度（可查看生成的代码）

### dspy.ReAct

**推理与执行**——一种能够迭代使用工具的智能体。

```python
from dspy.predict import ReAct

# Define tools
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information."""
    # Your search implementation
    return search_results

def calculate(expression: str) -> float:
    """Evaluate a mathematical expression."""
    return eval(expression)

# Create ReAct agent
class ResearchQA(dspy.Signature):
    """Answer questions using available tools."""
    question = dspy.InputField()
    answer = dspy.OutputField()

react = ReAct(ResearchQA, tools=[search_wikipedia, calculate])

# Agent decides which tools to use
result = react(question="How old was Einstein when he published special relativity?")
# Internally:
# 1. Thinks: "Need birth year and publication year"
# 2. Acts: search_wikipedia("Albert Einstein")
# 3. Acts: search_wikipedia("Special relativity 1905")
# 4. Acts: calculate("1905 - 1879")
# 5. Returns: "26 years old"
```

**适用场景：**
- 多步骤研究任务
- 需使用工具的智能体
- 复杂的信息检索
- 需要多次调用 API 的任务

**最佳实践：**
- 确保工具描述清晰且具体
- 工具数量控制在 5-7 个以内（过多会导致混淆）
- 在文档字符串中提供工具使用示例

### dspy.MultiChainComparison

**生成多个输出并加以比较**——基于自我一致性模式。

```python
mcc = dspy.MultiChainComparison("question -> answer", M=5)

result = mcc(question="What is the capital of France?")
# Generates 5 candidate answers
# Compares and selects most consistent
print(result.answer)  # "Paris"
print(result.candidates)  # All 5 generated answers
```

**参数：**
- `M`：需生成的候选答案数量（默认值：5）
- `temperature`：用于控制结果多样性的采样温度

**适用场景：**
- 需要做出重要决策的情况
- 存在歧义的问题
- 单一答案可能不可靠的情形

**权衡因素：**
- 执行速度较慢（需进行 M 次并行调用）
- 在处理含糊不清的任务时能提升准确性

### dspy.majority

**基于多重预测结果的多数投票机制。**

```python
from dspy.primitives import majority

# Generate multiple predictions
predictor = dspy.Predict("question -> answer")
predictions = [predictor(question="What is 2+2?") for _ in range(5)]

# Take majority vote
answer = majority([p.answer for p in predictions])
print(answer)  # "4"
```

**适用场景：**
- 综合多个模型的输出结果
- 降低预测结果的方差
- 采用集成学习方法

## 高级模块

### dspy.TypedPredictor

**利用 Pydantic 模型实现结构化输出。**

```python
from pydantic import BaseModel, Field

class PersonInfo(BaseModel):
    name: str = Field(description="Full name")
    age: int = Field(description="Age in years")
    occupation: str = Field(description="Current job")

class ExtractPerson(dspy.Signature):
    """Extract person information from text."""
    text = dspy.InputField()
    person: PersonInfo = dspy.OutputField()

extractor = dspy.TypedPredictor(ExtractPerson)
result = extractor(text="John Doe is a 35-year-old software engineer.")

print(result.person.name)       # "John Doe"
print(result.person.age)        # 35
print(result.person.occupation) # "software engineer"
```

**优势：**  
- 类型安全  
- 自动验证  
- JSON模式生成  
- IDE自动补全  

### dspy.Retry  

**支持在验证的同时实现自动重试。**

```python
from dspy.primitives import Retry

def validate_number(example, pred, trace=None):
    """Validate output is a number."""
    try:
        float(pred.answer)
        return True
    except ValueError:
        return False

# Retry up to 3 times if validation fails
qa = Retry(
    dspy.ChainOfThought("question -> answer"),
    validate=validate_number,
    max_retries=3
)

result = qa(question="What is 15% of 80?")
# If first attempt returns non-numeric, retries automatically
```

### dspy.Assert

**基于断言的优化。**

```python
import dspy
from dspy.primitives.assertions import assert_transform_module, backtrack_handler

class ValidatedQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.qa = dspy.ChainOfThought("question -> answer: float")

    def forward(self, question):
        answer = self.qa(question=question).answer

        # Assert answer is numeric
        dspy.Assert(
            isinstance(float(answer), float),
            "Answer must be a number",
            backtrack=backtrack_handler
        )

        return dspy.Prediction(answer=answer)
```

**优势：**  
- 能在优化过程中及时捕获错误  
- 引导大型语言模型生成有效输出  
- 效果优于事后的过滤处理  

## 模块构成

### 顺序流水线

```python
class Pipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.stage1 = dspy.Predict("input -> intermediate")
        self.stage2 = dspy.ChainOfThought("intermediate -> output")

    def forward(self, input):
        intermediate = self.stage1(input=input).intermediate
        output = self.stage2(intermediate=intermediate).output
        return dspy.Prediction(output=output)
```

### 条件逻辑

```python
class ConditionalModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.router = dspy.Predict("question -> category: str")
        self.simple_qa = dspy.Predict("question -> answer")
        self.complex_qa = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        category = self.router(question=question).category

        if category == "simple":
            return self.simple_qa(question=question)
        else:
            return self.complex_qa(question=question)
```

### 并行执行

```python
class ParallelModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.approach1 = dspy.ChainOfThought("question -> answer")
        self.approach2 = dspy.ProgramOfThought("question -> answer")

    def forward(self, question):
        # Run both approaches
        answer1 = self.approach1(question=question).answer
        answer2 = self.approach2(question=question).answer

        # Compare or combine results
        if answer1 == answer2:
            return dspy.Prediction(answer=answer1, confidence="high")
        else:
            return dspy.Prediction(answer=answer1, confidence="low")
```

## 批量处理

为提升效率，所有模块均支持批量处理功能：

```python
cot = dspy.ChainOfThought("question -> answer")

questions = [
    "What is 2+2?",
    "What is 3+3?",
    "What is 4+4?"
]

# Process all at once
results = cot.batch([{"question": q} for q in questions])

for result in results:
    print(result.answer)
```

## 保存与加载

```python
# Save module
qa = dspy.ChainOfThought("question -> answer")
qa.save("models/qa_v1.json")

# Load module
loaded_qa = dspy.ChainOfThought("question -> answer")
loaded_qa.load("models/qa_v1.json")
```

**会被保存的内容：**
- 少样本示例
- 提示词指令
- 模块配置

**不会被保存的内容：**
- 模型权重（DSPy默认不会进行微调）
- 大语言模型提供方配置

## 模块选择指南

| 任务类型 | 推荐模块 | 原因 |
|----------|----------|------|
| 简单分类 | Predict | 速度快且操作直接 |
| 数学应用题 | ProgramOfThought | 计算结果更可靠 |
| 逻辑推理 | ChainOfThought | 更适合分步思考 |
| 多步骤研究 | ReAct | 支持工具使用 |
| 关键决策 | MultiChainComparison | 提高自我一致性 |
| 结构化信息提取 | TypedPredictor | 具有类型安全性 |
| 模糊问题 | MultiChainComparison | 能从多角度分析 |

## 性能优化建议

1. **先使用Predict模块**，仅在必要时添加推理功能
2. **对于多个输入内容**，采用批量处理方式
3. **对重复查询的结果进行缓存**
4. 使用 `track_usage=True` 参数来监控令牌使用情况
5. 在完成原型设计后，通过提示词优化进一步提升性能

## 常见使用模式

### 模式：检索 + 生成

```python
class RAG(dspy.Module):
    def __init__(self, k=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=k)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)
```

### 模式：验证循环

```python
class VerifiedQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.answer = dspy.ChainOfThought("question -> answer")
        self.verify = dspy.Predict("question, answer -> is_correct: bool")

    def forward(self, question, max_attempts=3):
        for _ in range(max_attempts):
            answer = self.answer(question=question).answer
            is_correct = self.verify(question=question, answer=answer).is_correct

            if is_correct:
                return dspy.Prediction(answer=answer)

        return dspy.Prediction(answer="Unable to verify answer")
```

### 模式：多轮对话

```python
class DialogAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.respond = dspy.Predict("history, user_message -> assistant_message")
        self.history = []

    def forward(self, user_message):
        history_str = "\n".join(self.history)
        response = self.respond(history=history_str, user_message=user_message)

        self.history.append(f"User: {user_message}")
        self.history.append(f"Assistant: {response.assistant_message}")

        return response
```
