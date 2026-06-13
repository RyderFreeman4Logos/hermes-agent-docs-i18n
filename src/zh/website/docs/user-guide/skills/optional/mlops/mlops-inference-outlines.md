---
title: "Outlines — Outlines: structured JSON/regex/Pydantic LLM generation"
sidebar_label: "Outlines"
description: "Outlines: structured JSON/regex/Pydantic LLM generation"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据该技能的 SKILL.md 自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Outlines

Outlines：基于结构化的 JSON/正则表达式/Pydantic 的大语言模型生成功能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/outlines` 安装 |
| 路径 | `optional-skills/mlops/inference/outlines` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `outlines`、`transformers`、`vllm`、`pydantic` |
| 支持平台 | linux、macos、windows |
| 标签 | `提示词工程`、`Outlines`、`结构化生成`、`JSON Schema`、`Pydantic`、`本地模型`、`基于语法的生成`、`vLLM`、`Transformers`、`类型安全` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当该技能处于激活状态时，智能体看到的指令即为此内容。
:::

# Outlines：结构化文本生成

## 何时使用此技能

在以下情况下可使用 Outlines：
- **需要在生成过程中确保输出为有效的 JSON/XML/代码结构**
- **希望利用 Pydantic 模型实现类型安全的输出结果**
- **需要支持本地模型**（如 Transformers、llama.cpp、vLLM）
- **希望通过无额外开销的结构化生成方式提升推理速度**
- **需要自动依据 JSON Schema 进行生成**
- **希望在语法层面控制令牌采样过程**

**GitHub 星标数**：8,000+ | **来源**：dottxt.ai（原 .txt）

## 安装方法

```bash
# Base installation
pip install outlines

# With specific backends
pip install outlines transformers  # Hugging Face models
pip install outlines llama-cpp-python  # llama.cpp
pip install outlines vllm  # vLLM for high-throughput
```

## 快速入门

### 基本示例：分类任务

```python
import outlines
from typing import Literal

# Load model
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Generate with type constraint
prompt = "Sentiment of 'This product is amazing!': "
generator = outlines.generate.choice(model, ["positive", "negative", "neutral"])
sentiment = generator(prompt)

print(sentiment)  # "positive" (guaranteed one of these)
```

### 使用 Pydantic 模型

```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Generate structured output
prompt = "Extract user: John Doe, 30 years old, john@example.com"
generator = outlines.generate.json(model, User)
user = generator(prompt)

print(user.name)   # "John Doe"
print(user.age)    # 30
print(user.email)  # "john@example.com"
```

## 核心概念

### 1. 受限令牌采样

Outlines通过有限状态机（FSM）在逻辑层面对令牌生成过程进行约束。

**工作原理：**
1. 将模式（JSON/Pydantic/正则表达式）转换为上下文无关文法（CFG）
2. 将CFG进一步转化为有限状态机（FSM）
3. 在生成过程的每一步过滤无效令牌
4. 当仅存在一个有效令牌时直接跳转

**优势：**
- **零额外开销**：过滤操作在令牌层面直接执行
- **提升速度**：可通过确定性路径快速跳转
- **保证有效性**：杜绝无效输出的产生

```python
import outlines

# Pydantic model -> JSON schema -> CFG -> FSM
class Person(BaseModel):
    name: str
    age: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Behind the scenes:
# 1. Person -> JSON schema
# 2. JSON schema -> CFG
# 3. CFG -> FSM
# 4. FSM filters tokens during generation

generator = outlines.generate.json(model, Person)
result = generator("Generate person: Alice, 25")
```

### 2. 结构化生成器

Outlines 提供了针对不同输出类型的专用生成器。

#### 选择生成器

```python
# Multiple choice selection
generator = outlines.generate.choice(
    model,
    ["positive", "negative", "neutral"]
)

sentiment = generator("Review: This is great!")
# Result: One of the three choices
```

#### JSON生成器

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

# Generate valid JSON matching schema
generator = outlines.generate.json(model, Product)
product = generator("Extract: iPhone 15, $999, available")

# Guaranteed valid Product instance
print(type(product))  # <class '__main__.Product'>
```

#### 正则表达式生成器

```python
# Generate text matching regex
generator = outlines.generate.regex(
    model,
    r"[0-9]{3}-[0-9]{3}-[0-9]{4}"  # Phone number pattern
)

phone = generator("Generate phone number:")
# Result: "555-123-4567" (guaranteed to match pattern)
```

#### 整数/浮点数生成器

```python
# Generate specific numeric types
int_generator = outlines.generate.integer(model)
age = int_generator("Person's age:")  # Guaranteed integer

float_generator = outlines.generate.float(model)
price = float_generator("Product price:")  # Guaranteed float
```

### 3. 模型后端

Outlines 支持多种本地及基于 API 的后端。

#### Transformers（Hugging Face）

```python
import outlines

# Load from Hugging Face
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda"  # Or "cpu"
)

# Use with any generator
generator = outlines.generate.json(model, YourModel)
```

#### llama.cpp

```python
# Load GGUF model
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)

generator = outlines.generate.json(model, YourModel)
```

#### vLLM（高吞吐模式）

```python
# For production deployments
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=2  # Multi-GPU
)

generator = outlines.generate.json(model, YourModel)
```

#### OpenAI（支持有限）

```python
# Basic OpenAI support
model = outlines.models.openai(
    "gpt-4o-mini",
    api_key="your-api-key"
)

# Note: Some features limited with API models
generator = outlines.generate.json(model, YourModel)
```

### 4. Pydantic 集成

Outlines 提供一流的 Pydantic 支持，可实现自动模式转换功能。

#### 基本模型

```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="Article title")
    author: str = Field(description="Author name")
    word_count: int = Field(description="Number of words", gt=0)
    tags: list[str] = Field(description="List of tags")

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, Article)

article = generator("Generate article about AI")
print(article.title)
print(article.word_count)  # Guaranteed > 0
```

#### 嵌套模型

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int
    address: Address  # Nested model

generator = outlines.generate.json(model, Person)
person = generator("Generate person in New York")

print(person.address.city)  # "New York"
```

#### 枚举与字面量

```python
from enum import Enum
from typing import Literal

class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    applicant: str
    status: Status  # Must be one of enum values
    priority: Literal["low", "medium", "high"]  # Must be one of literals

generator = outlines.generate.json(model, Application)
app = generator("Generate application")

print(app.status)  # Status.PENDING (or APPROVED/REJECTED)
```

## 常见模式

### 模式 1：数据提取

```python
from pydantic import BaseModel
import outlines

class CompanyInfo(BaseModel):
    name: str
    founded_year: int
    industry: str
    employees: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, CompanyInfo)

text = """
Apple Inc. was founded in 1976 in the technology industry.
The company employs approximately 164,000 people worldwide.
"""

prompt = f"Extract company information:\n{text}\n\nCompany:"
company = generator(prompt)

print(f"Name: {company.name}")
print(f"Founded: {company.founded_year}")
print(f"Industry: {company.industry}")
print(f"Employees: {company.employees}")
```

### 模式 2：分类任务

```python
from typing import Literal
import outlines

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Binary classification
generator = outlines.generate.choice(model, ["spam", "not_spam"])
result = generator("Email: Buy now! 50% off!")

# Multi-class classification
categories = ["technology", "business", "sports", "entertainment"]
category_gen = outlines.generate.choice(model, categories)
category = category_gen("Article: Apple announces new iPhone...")

# With confidence
class Classification(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float

classifier = outlines.generate.json(model, Classification)
result = classifier("Review: This product is okay, nothing special")
```

### 模式 3：结构化表单

```python
class UserProfile(BaseModel):
    full_name: str
    age: int
    email: str
    phone: str
    country: str
    interests: list[str]

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, UserProfile)

prompt = """
Extract user profile from:
Name: Alice Johnson
Age: 28
Email: alice@example.com
Phone: 555-0123
Country: USA
Interests: hiking, photography, cooking
"""

profile = generator(prompt)
print(profile.full_name)
print(profile.interests)  # ["hiking", "photography", "cooking"]
```

### 模式4：多实体提取

```python
class Entity(BaseModel):
    name: str
    type: Literal["PERSON", "ORGANIZATION", "LOCATION"]

class DocumentEntities(BaseModel):
    entities: list[Entity]

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, DocumentEntities)

text = "Tim Cook met with Satya Nadella at Microsoft headquarters in Redmond."
prompt = f"Extract entities from: {text}"

result = generator(prompt)
for entity in result.entities:
    print(f"{entity.name} ({entity.type})")
```

### 模式 5：代码生成

```python
class PythonFunction(BaseModel):
    function_name: str
    parameters: list[str]
    docstring: str
    body: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, PythonFunction)

prompt = "Generate a Python function to calculate factorial"
func = generator(prompt)

print(f"def {func.function_name}({', '.join(func.parameters)}):")
print(f'    """{func.docstring}"""')
print(f"    {func.body}")
```

### 模式 6：批量处理

```python
def batch_extract(texts: list[str], schema: type[BaseModel]):
    """Extract structured data from multiple texts."""
    model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
    generator = outlines.generate.json(model, schema)

    results = []
    for text in texts:
        result = generator(f"Extract from: {text}")
        results.append(result)

    return results

class Person(BaseModel):
    name: str
    age: int

texts = [
    "John is 30 years old",
    "Alice is 25 years old",
    "Bob is 40 years old"
]

people = batch_extract(texts, Person)
for person in people:
    print(f"{person.name}: {person.age}")
```

## 后端配置

### 转换器

```python
import outlines

# Basic usage
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# GPU configuration
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda",
    model_kwargs={"torch_dtype": "float16"}
)

# Popular models
model = outlines.models.transformers("meta-llama/Llama-3.1-8B-Instruct")
model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.3")
model = outlines.models.transformers("Qwen/Qwen2.5-7B-Instruct")
```

### llama.cpp

```python
# Load GGUF model
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b.Q4_K_M.gguf",
    n_ctx=4096,         # Context window
    n_gpu_layers=35,    # GPU layers
    n_threads=8         # CPU threads
)

# Full GPU offload
model = outlines.models.llamacpp(
    "./models/model.gguf",
    n_gpu_layers=-1  # All layers on GPU
)
```

### vLLM（生产环境版）

```python
# Single GPU
model = outlines.models.vllm("meta-llama/Llama-3.1-8B-Instruct")

# Multi-GPU
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4  # 4 GPUs
)

# With quantization
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization="awq"  # Or "gptq"
)
```

## 最佳实践

### 1. 使用特定类型

```python
# ✅ Good: Specific types
class Product(BaseModel):
    name: str
    price: float  # Not str
    quantity: int  # Not str
    in_stock: bool  # Not str

# ❌ Bad: Everything as string
class Product(BaseModel):
    name: str
    price: str  # Should be float
    quantity: str  # Should be int
```

### 2. 添加约束条件

```python
from pydantic import Field

# ✅ Good: With constraints
class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=120)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

# ❌ Bad: No constraints
class User(BaseModel):
    name: str
    age: int
    email: str
```

### 3. 使用枚举类型定义分类

```python
# ✅ Good: Enum for fixed set
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority

# ❌ Bad: Free-form string
class Task(BaseModel):
    title: str
    priority: str  # Can be anything
```

### 4. 在提示词中提供上下文信息

```python
# ✅ Good: Clear context
prompt = """
Extract product information from the following text.
Text: iPhone 15 Pro costs $999 and is currently in stock.
Product:
"""

# ❌ Bad: Minimal context
prompt = "iPhone 15 Pro costs $999 and is currently in stock."
```

### 5. 处理可选字段

```python
from typing import Optional

# ✅ Good: Optional fields for incomplete data
class Article(BaseModel):
    title: str  # Required
    author: Optional[str] = None  # Optional
    date: Optional[str] = None  # Optional
    tags: list[str] = []  # Default empty list

# Can succeed even if author/date missing
```

## 与其他方案的对比

| 功能特性 | Outlines | Instructor | Guidance | LMQL |
|---------|----------|------------|----------|------|
| Pydantic 支持 | ✅ 原生支持 | ✅ 原生支持 | ❌ 不支持 | ❌ 不支持 |
| JSON Schema 支持 | ✅ 支持 | ✅ 支持 | ⚠️ 有限支持 | ✅ 支持 |
| 正则表达式限制 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | ✅ 支持 |
| 本地模型支持 | ✅ 完全支持 | ⚠️ 有限支持 | ✅ 完全支持 | ✅ 完全支持 |
| API 模型支持 | ⚠️ 有限支持 | ✅ 完全支持 | ✅ 完全支持 | ✅ 完全支持 |
| 零开销生成 | ✅ 支持 | ❌ 不支持 | ⚠️ 部分支持 | ✅ 支持 |
| 自动重试功能 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| 学习曲线 | 较低 | 较低 | 较低 | 较高 |

**何时选择 Outlines：**
- 使用本地模型（如 Transformers、llama.cpp、vLLM）
- 需要最高的推理速度
- 需要 Pydantic 模型支持
- 需要零开销的结构化生成
- 需要自行控制令牌采样过程

**何时选择其他方案：**
- Instructor：需要具备自动重试功能的 API 模型
- Guidance：需要令牌修复功能及复杂工作流支持
- LMQL：偏好声明式查询语法

## 性能特点

**速度：**
- **零开销**：结构化生成的速度与无限制生成相当
- **快进优化**：可跳过已确定的令牌
- 相比生成后的验证方式，速度提升 **1.2–2 倍**

**内存占用：**
- 每个模式仅编译一次 FSM 并进行缓存
- 运行时开销极低
- 结合 vLLM 使用时可实现高吞吐量处理

**准确性：**
- **100% 合法输出**（由 FSM 保证）
- 无需重复尝试
- 具有确定性的令牌过滤机制

## 资源链接

- **文档**：https://outlines-dev.github.io/outlines
- **GitHub 仓库**：https://github.com/outlines-dev/outlines（拥有 8k 多个星标）
- **Discord 社区**：https://discord.gg/R9DSu34mGd
- **博客**：https://blog.dottxt.co

## 相关文档

- `references/json_generation.md` - 关于 JSON 和 Pydantic 的完整用法示例
- `references/backends.md` - 各后端的具体配置说明
- `references/examples.md` - 可直接用于生产环境的示例代码
