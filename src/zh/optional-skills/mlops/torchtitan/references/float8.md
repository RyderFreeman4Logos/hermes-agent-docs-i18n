# TorchTitan中的Float8训练

对于那些矩阵乘法运算规模较大、FP8 Tensor Core带来的性能提升足以抵消动态量化开销的模型，采用Float8训练方式能够显著提升训练速度。

## 硬件要求

- 配备FP8 Tensor Core的NVIDIA H100或更新型号的GPU
- 进行MXFP8训练则需Blackwell架构的GPU

## 安装指南

```bash
USE_CPP=0 pip install git+https://github.com/pytorch/ao.git
```

## 使用方式：张量级缩放

采用标准浮点8位格式，并通过张量级动态缩放技术实现：

```bash
CONFIG_FILE="./torchtitan/models/llama3/train_configs/llama3_8b.toml" ./run_train.sh \
  --model.converters="quantize.linear.float8" \
  --quantize.linear.float8.enable_fsdp_float8_all_gather \
  --quantize.linear.float8.precompute_float8_dynamic_scale_for_fsdp \
  --compile.enable
```

### 关键参数

| 参数 | 描述 |
|------|------|
| `--model.converters="quantize.linear.float8"` | 将 `nn.Linear` 替换为 `Float8Linear` |
| `--quantize.linear.float8.enable_fsdp_float8_all_gather` | 以 float8 格式进行通信，从而节省带宽 |
| `--quantize.linear.float8.precompute_float8_dynamic_scale_for_fsdp` | 对所有 AMAX 操作及缩放因子执行单次全量归约 |
| `--compile.enable` | 必需参数——用于合并 float8 缩放/类型转换内核 |

## 使用方式：按行缩放

相比逐张量缩放，其精度更高：

```bash
CONFIG_FILE="./torchtitan/models/llama3/train_configs/llama3_8b.toml" ./run_train.sh \
  --model.converters="quantize.linear.float8" \
  --quantize.linear.float8.recipe_name rowwise \
  --compile.enable
```

## 过滤层

并非所有层都能从 Float8 格式中受益。建议对较小的层进行过滤：

```bash
--quantize.linear.float8.filter_fqns="attention.wk,attention.wv,output"
```

### 自动过滤

自动跳过那些过小而无法带来实际收益的层级：

```bash
--quantize.linear.float8.filter_fqns="auto_filter_small_kn"
```

基于 H100 微基准测试设定的阈值，要求加速比大于开销比例。  

## TOML 配置文件

```toml
[model]
converters = ["quantize.linear.float8"]

[quantize.linear.float8]
enable_fsdp_float8_all_gather = true
precompute_float8_dynamic_scale_for_fsdp = true
filter_fqns = ["output", "auto_filter_small_kn"]

[compile]
enable = true
components = ["model", "loss"]
```

## Float8在分布式训练中的工作原理

### 单设备场景

在调用`torch._scaled_mm`之前，需先将前向传播过程中的输入数据和权重转换为float8格式：

```python
# Float8 matmul requires scales
torch._scaled_mm(input_fp8, weight_fp8, scale_a=scale_input, scale_b=scale_weight)
```

### FSDP + Float8

1. 将分片后的高精度权重（每个节点为 1/N）转换为 float8 格式。
2. 执行 float8 全收集操作（相比 bf16/fp32 能节省带宽）。
3. 在各节点之间传递 `max(abs)` 值以用于缩放因子计算。
4. 在前向传播开始时，准备好未分片化的 float8 权重。

**总体优势**：在节点数量和消息大小一定的情况下，float8 全收集操作结合 amax 通信方式，其性能可优于 bf16/fp32 的全收集操作。

### TP + Float8

- **输入数据**：将分片后的输入数据转换为 float8 格式，并进行 float8 全收集。
- **权重数据**：针对分片后的权重，在节点间传递 `max(abs)` 值以确定缩放因子。
- **矩阵乘法**：使用未分片化的 float8 输入数据与分片化的 float8 权重进行运算，并应用全局缩放因子。

## 缩放策略

| 策略 | 当前状态 | 描述 |
|------|----------|------|
| 按张量动态缩放 | 已稳定 | 每个张量使用独立的缩放因子 |
| 按行动态缩放 | 测试中 | 每行使用独立缩放因子，精度更高 |

## 性能提升效果

基于 H100 上的测试结果：

| 配置方案 | TPS/每 GPU | 相比基准值提升幅度 |
|----------|-----------|-------------------|
| 仅使用 FSDP | 5,762 | - |
| FSDP + 编译优化 | 6,667 | +16% |
| FSDP + 编译优化 + Float8 | 8,532 | +48% |

## 判断 Float8 的优势

可查看 [torchao 微基准测试](https://github.com/pytorch/ao/tree/main/torchao/float8#performance)，了解在不同 M、N、K 大小下，“层归一化 => 线性变换 => Sigmoid 激活”这一流程的前向与反向传播速度提升情况。

经验法则：当矩阵维度 K、N 大于 4096 时，使用 Float8 通常能带来显著性能提升。

## MXFP8 训练（Blackwell 架构）

针对 NVIDIA Blackwell 架构的 GPU，TorchTitan 支持在密集型模型和 MoE 模型中均使用 MXFP8（微缩放 FP8）格式。详细信息请参阅 [docs/mxfp8.md](https://github.com/pytorch/torchtitan/blob/main/docs/mxfp8.md)。
