# 工件与模型注册表指南

使用 W&B 工件功能实现数据版本控制与模型管理的完整指南。

## 目录
- 什么是工件
- 创建工件
- 使用工件
- 模型注册表
- 版本控制与数据血缘追踪
- 最佳实践

## 什么是工件

工件是指经过版本控制、并带有数据血缘追踪功能的数据集、模型或文件。

**核心特性：**
- 自动版本编号（v0、v1、v2...）
- 数据血缘追踪（记录哪些流程生成/使用了这些工件）
- 高效存储（去重功能）
- 协同工作（支持团队成员访问）
- 别名功能（最新版、最佳版本、生产环境版本）

**常见应用场景：**
- 数据集版本管理
- 模型检查点
- 预处理后的数据
- 评估结果
- 配置文件

## 创建工件

### 基本数据集工件

```python
import wandb

run = wandb.init(project="my-project")

# Create artifact
dataset = wandb.Artifact(
    name='training-data',
    type='dataset',
    description='ImageNet training split with augmentations',
    metadata={
        'size': '1.2M images',
        'format': 'JPEG',
        'resolution': '224x224'
    }
)

# Add files
dataset.add_file('data/train.csv')        # Single file
dataset.add_dir('data/images')            # Entire directory
dataset.add_reference('s3://bucket/data') # Cloud reference

# Log artifact
run.log_artifact(dataset)
wandb.finish()
```

### 模型工件

```python
import torch
import wandb

run = wandb.init(project="my-project")

# Train model
model = train_model()

# Save model
torch.save(model.state_dict(), 'model.pth')

# Create model artifact
model_artifact = wandb.Artifact(
    name='resnet50-classifier',
    type='model',
    description='ResNet50 trained on ImageNet',
    metadata={
        'architecture': 'ResNet50',
        'accuracy': 0.95,
        'loss': 0.15,
        'epochs': 50,
        'framework': 'PyTorch'
    }
)

# Add model file
model_artifact.add_file('model.pth')

# Add config
model_artifact.add_file('config.yaml')

# Log with aliases
run.log_artifact(model_artifact, aliases=['latest', 'best'])

wandb.finish()
```

### 预处理数据工件

```python
import pandas as pd
import wandb

run = wandb.init(project="nlp-project")

# Preprocess data
df = pd.read_csv('raw_data.csv')
df_processed = preprocess(df)
df_processed.to_csv('processed_data.csv', index=False)

# Create artifact
processed_data = wandb.Artifact(
    name='processed-text-data',
    type='dataset',
    metadata={
        'rows': len(df_processed),
        'columns': list(df_processed.columns),
        'preprocessing_steps': ['lowercase', 'remove_stopwords', 'tokenize']
    }
)

processed_data.add_file('processed_data.csv')

# Log artifact
run.log_artifact(processed_data)
```

## 使用 Artifact

### 下载与使用

```python
import wandb

run = wandb.init(project="my-project")

# Download artifact
artifact = run.use_artifact('training-data:latest')
artifact_dir = artifact.download()

# Use files
import pandas as pd
df = pd.read_csv(f'{artifact_dir}/train.csv')

# Train with artifact data
model = train_model(df)
```

### 使用特定版本

```python
# Use specific version
artifact_v2 = run.use_artifact('training-data:v2')

# Use alias
artifact_best = run.use_artifact('model:best')
artifact_prod = run.use_artifact('model:production')

# Use from another project
artifact = run.use_artifact('team/other-project/model:latest')
```

### 查看工件元数据

```python
artifact = run.use_artifact('training-data:latest')

# Access metadata
print(artifact.metadata)
print(f"Size: {artifact.metadata['size']}")

# Access version info
print(f"Version: {artifact.version}")
print(f"Created at: {artifact.created_at}")
print(f"Digest: {artifact.digest}")
```

## 模型注册表

将模型关联至中央注册表，以实现统一的管理与部署。

### 创建模型注册表

```python
# In W&B UI:
# 1. Go to "Registry" tab
# 2. Create new registry: "production-models"
# 3. Define stages: development, staging, production
```

### 将模型关联至注册表

```python
import wandb

run = wandb.init(project="training")

# Create model artifact
model_artifact = wandb.Artifact(
    name='sentiment-classifier',
    type='model',
    metadata={'accuracy': 0.94, 'f1': 0.92}
)

model_artifact.add_file('model.pth')

# Log artifact
run.log_artifact(model_artifact)

# Link to registry
run.link_artifact(
    model_artifact,
    'model-registry/production-models',
    aliases=['staging']  # Deploy to staging
)

wandb.finish()
```

### 在注册表中推广模型

```python
# Retrieve model from registry
api = wandb.Api()
artifact = api.artifact('model-registry/production-models/sentiment-classifier:staging')

# Promote to production
artifact.link('model-registry/production-models', aliases=['production'])

# Demote from production
artifact.aliases = ['archived']
artifact.save()
```

### 使用注册表中的模型

```python
import wandb

run = wandb.init()

# Download production model
model_artifact = run.use_artifact(
    'model-registry/production-models/sentiment-classifier:production'
)

model_dir = model_artifact.download()

# Load and use
import torch
model = torch.load(f'{model_dir}/model.pth')
model.eval()
```

## 版本控制与版本溯源

### 自动版本管理

```python
# First log: creates v0
run1 = wandb.init(project="my-project")
dataset_v0 = wandb.Artifact('my-dataset', type='dataset')
dataset_v0.add_file('data_v1.csv')
run1.log_artifact(dataset_v0)

# Second log with same name: creates v1
run2 = wandb.init(project="my-project")
dataset_v1 = wandb.Artifact('my-dataset', type='dataset')
dataset_v1.add_file('data_v2.csv')  # Different content
run2.log_artifact(dataset_v1)

# Third log with SAME content as v1: references v1 (no new version)
run3 = wandb.init(project="my-project")
dataset_v1_again = wandb.Artifact('my-dataset', type='dataset')
dataset_v1_again.add_file('data_v2.csv')  # Same content as v1
run3.log_artifact(dataset_v1_again)  # Still v1, no v2 created
```

### 追踪代码血统

```python
# Training run
run = wandb.init(project="my-project")

# Use dataset (input)
dataset = run.use_artifact('training-data:v3')
data = load_data(dataset.download())

# Train model
model = train(data)

# Save model (output)
model_artifact = wandb.Artifact('trained-model', type='model')
torch.save(model.state_dict(), 'model.pth')
model_artifact.add_file('model.pth')
run.log_artifact(model_artifact)

# Lineage automatically tracked:
# training-data:v3 --> [run] --> trained-model:v0
```

### 查看谱系图

```python
# In W&B UI:
# Artifacts → Select artifact → Lineage tab
# Shows:
# - Which runs produced this artifact
# - Which runs used this artifact
# - Parent/child artifacts
```

## 工件类型

### 数据集工件

```python
# Raw data
raw_data = wandb.Artifact('raw-data', type='dataset')
raw_data.add_dir('raw/')

# Processed data
processed_data = wandb.Artifact('processed-data', type='dataset')
processed_data.add_dir('processed/')

# Train/val/test splits
train_split = wandb.Artifact('train-split', type='dataset')
train_split.add_file('train.csv')

val_split = wandb.Artifact('val-split', type='dataset')
val_split.add_file('val.csv')
```

### 模型输出结果

```python
# Checkpoint during training
checkpoint = wandb.Artifact('checkpoint-epoch-10', type='model')
checkpoint.add_file('checkpoint_epoch_10.pth')

# Final model
final_model = wandb.Artifact('final-model', type='model')
final_model.add_file('model.pth')
final_model.add_file('tokenizer.json')

# Quantized model
quantized = wandb.Artifact('quantized-model', type='model')
quantized.add_file('model_int8.onnx')
```

### 结果输出文件

```python
# Predictions
predictions = wandb.Artifact('test-predictions', type='predictions')
predictions.add_file('predictions.csv')

# Evaluation metrics
eval_results = wandb.Artifact('evaluation', type='evaluation')
eval_results.add_file('metrics.json')
eval_results.add_file('confusion_matrix.png')
```

## 高级模式

### 分批上传工件

无需重新上传即可逐步添加文件。

```python
run = wandb.init(project="my-project")

# Create artifact
dataset = wandb.Artifact('incremental-dataset', type='dataset')

# Add files incrementally
for i in range(100):
    filename = f'batch_{i}.csv'
    process_batch(i, filename)
    dataset.add_file(filename)

    # Log progress
    if (i + 1) % 10 == 0:
        print(f"Added {i + 1}/100 batches")

# Log complete artifact
run.log_artifact(dataset)
```

### 结构化数据表

利用 W&B Tables 对结构化数据进行追踪与管理。

```python
import wandb

run = wandb.init(project="my-project")

# Create table
table = wandb.Table(columns=["id", "image", "label", "prediction"])

for idx, (img, label, pred) in enumerate(zip(images, labels, predictions)):
    table.add_data(
        idx,
        wandb.Image(img),
        label,
        pred
    )

# Log as artifact
artifact = wandb.Artifact('predictions-table', type='predictions')
artifact.add(table, "predictions")
run.log_artifact(artifact)
```

### 工件引用

无需复制即可引用外部数据。

```python
# S3 reference
dataset = wandb.Artifact('s3-dataset', type='dataset')
dataset.add_reference('s3://my-bucket/data/', name='train')
dataset.add_reference('s3://my-bucket/labels/', name='labels')

# GCS reference
dataset.add_reference('gs://my-bucket/data/')

# HTTP reference
dataset.add_reference('https://example.com/data.zip')

# Local filesystem reference (for shared storage)
dataset.add_reference('file:///mnt/shared/data')
```

## 协作模式

### 团队数据集共享

```python
# Data engineer creates dataset
run = wandb.init(project="data-eng", entity="my-team")
dataset = wandb.Artifact('shared-dataset', type='dataset')
dataset.add_dir('data/')
run.log_artifact(dataset, aliases=['latest', 'production'])

# ML engineer uses dataset
run = wandb.init(project="ml-training", entity="my-team")
dataset = run.use_artifact('my-team/data-eng/shared-dataset:production')
data = load_data(dataset.download())
```

### 模型交接

```python
# Training team
train_run = wandb.init(project="model-training", entity="ml-team")
model = train_model()
model_artifact = wandb.Artifact('nlp-model', type='model')
model_artifact.add_file('model.pth')
train_run.log_artifact(model_artifact)
train_run.link_artifact(model_artifact, 'model-registry/nlp-models', aliases=['candidate'])

# Evaluation team
eval_run = wandb.init(project="model-eval", entity="ml-team")
model_artifact = eval_run.use_artifact('model-registry/nlp-models/nlp-model:candidate')
metrics = evaluate_model(model_artifact)

if metrics['f1'] > 0.9:
    # Promote to production
    model_artifact.link('model-registry/nlp-models', aliases=['production'])
```

## 最佳实践

### 1. 使用描述性名称

```python
# ✅ Good: Descriptive names
wandb.Artifact('imagenet-train-augmented-v2', type='dataset')
wandb.Artifact('bert-base-sentiment-finetuned', type='model')

# ❌ Bad: Generic names
wandb.Artifact('dataset1', type='dataset')
wandb.Artifact('model', type='model')
```

### 2. 添加完整元数据

```python
model_artifact = wandb.Artifact(
    'production-model',
    type='model',
    description='ResNet50 classifier for product categorization',
    metadata={
        # Model info
        'architecture': 'ResNet50',
        'framework': 'PyTorch 2.0',
        'pretrained': True,

        # Performance
        'accuracy': 0.95,
        'f1_score': 0.93,
        'inference_time_ms': 15,

        # Training
        'epochs': 50,
        'dataset': 'imagenet',
        'num_samples': 1200000,

        # Business context
        'use_case': 'e-commerce product classification',
        'owner': 'ml-team@company.com',
        'approved_by': 'data-science-lead'
    }
)
```

### 3. 使用别名指定部署阶段

```python
# Development
run.log_artifact(model, aliases=['dev', 'latest'])

# Staging
run.log_artifact(model, aliases=['staging'])

# Production
run.log_artifact(model, aliases=['production', 'v1.2.0'])

# Archive old versions
old_artifact = api.artifact('model:production')
old_artifact.aliases = ['archived-v1.1.0']
old_artifact.save()
```

### 4. 跟踪数据血缘关系

```python
def create_training_pipeline():
    run = wandb.init(project="pipeline")

    # 1. Load raw data
    raw_data = run.use_artifact('raw-data:latest')

    # 2. Preprocess
    processed = preprocess(raw_data)
    processed_artifact = wandb.Artifact('processed-data', type='dataset')
    processed_artifact.add_file('processed.csv')
    run.log_artifact(processed_artifact)

    # 3. Train model
    model = train(processed)
    model_artifact = wandb.Artifact('trained-model', type='model')
    model_artifact.add_file('model.pth')
    run.log_artifact(model_artifact)

    # Lineage: raw-data → processed-data → trained-model
```

### 5. 高效存储

```python
# ✅ Good: Reference large files
large_dataset = wandb.Artifact('large-dataset', type='dataset')
large_dataset.add_reference('s3://bucket/huge-file.tar.gz')

# ❌ Bad: Upload giant files
# large_dataset.add_file('huge-file.tar.gz')  # Don't do this

# ✅ Good: Upload only metadata
metadata_artifact = wandb.Artifact('dataset-metadata', type='dataset')
metadata_artifact.add_file('metadata.json')  # Small file
```

## 资源参考

- **工件文档**：https://docs.wandb.ai/guides/artifacts
- **模型注册表**：https://docs.wandb.ai/guides/model-registry
- **最佳实践指南**：https://wandb.ai/site/articles/versioning-data-and-models-in-ml
