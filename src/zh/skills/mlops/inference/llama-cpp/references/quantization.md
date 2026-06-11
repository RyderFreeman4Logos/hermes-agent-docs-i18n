# GGUF量化指南

关于GGUF量化格式及模型转换的完整指南。

## 基于Hub的量化选择方式

在参考通用表格之前，请先使用以下方式打开模型仓库：

```text
https://huggingface.co/<repo>?local-app=llama.cpp
```

请优先使用从获取的 `?local-app=llama.cpp` 页面文本或 HTML 中“硬件兼容性”部分所显示的精确数量标签及尺寸。随后在以下位置确认对应的文件名：

```text
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

请先使用中心页面，仅当仓库页面未提供明确推荐时，再采用以下的通用规则。

## 量化概述

**GGUF**（GPT生成的统一格式）—— llama.cpp 模型的标准格式。

### 格式对比

| 格式 | 混乱度 | 文件大小（7B模型） | 每秒处理token数 | 备注 |
|------|--------|------------------|----------------|-------|
| FP16 | 5.9565（基准值） | 13.0 GB | 15 tok/s | 保持原始质量 |
| Q8_0 | 5.9584（上升0.03%） | 7.0 GB | 25 tok/s | 几乎无损失 |
| **Q6_K** | 5.9642（上升0.13%） | 5.5 GB | 30 tok/s | 最佳质量与体积比 |
| **Q5_K_M** | 5.9796（上升0.39%） | 4.8 GB | 35 tok/s | 性能与质量平衡 |
| **Q4_K_M** | 6.0565（上升1.68%） | 4.1 GB | 40 tok/s | **推荐使用** |
| Q4_K_S | 6.1125（上升2.62%） | 3.9 GB | 42 tok/s | 速度更快，但质量较低 |
| Q3_K_M | 6.3184（上升6.07%） | 3.3 GB | 45 tok/s | 仅适用于小型模型 |
| Q2_K | 6.8673（上升15.3%） | 2.7 GB | 50 tok/s | 不推荐使用 |

**建议**：如需在质量与速度之间取得最佳平衡，建议使用 **Q4_K_M** 格式。

## 模型转换

### 从 Hugging Face 转换为 GGUF

```bash
# 1. Download Hugging Face model
hf download meta-llama/Llama-2-7b-chat-hf \
    --local-dir models/llama-2-7b-chat/

# 2. Convert to FP16 GGUF
python convert_hf_to_gguf.py \
    models/llama-2-7b-chat/ \
    --outtype f16 \
    --outfile models/llama-2-7b-chat-f16.gguf

# 3. Quantize to Q4_K_M
./llama-quantize \
    models/llama-2-7b-chat-f16.gguf \
    models/llama-2-7b-chat-Q4_K_M.gguf \
    Q4_K_M
```

### 批量量化

```bash
# Quantize to multiple formats
for quant in Q4_K_M Q5_K_M Q6_K Q8_0; do
    ./llama-quantize \
        model-f16.gguf \
        model-${quant}.gguf \
        $quant
done
```

## K-量化方法

**K-quants**采用混合精度格式以提高质量：
- 注意力权重：更高精度
- 前馈网络权重：较低精度

**不同版本**：
- `_S`（小型）：速度更快，但质量较低
- `_M`（中型）：均衡型（推荐）
- `_L`（大型）：质量更高，但文件体积更大

**示例**：`Q4_K_M`
- `Q4`：4位量化
- `K`：混合精度方法
- `M`：中等质量

## 质量检测

```bash
# Calculate perplexity (quality metric)
./llama-perplexity \
    -m model.gguf \
    -f wikitext-2-raw/wiki.test.raw \
    -c 512

# Lower perplexity = better quality
# Baseline (FP16): ~5.96
# Q4_K_M: ~6.06 (+1.7%)
# Q2_K: ~6.87 (+15.3% - too much degradation)
```

## 使用场景指南

### 通用场景（聊天机器人、智能助手）
```
Q4_K_M - Best balance
Q5_K_M - If you have extra RAM
```

### 代码生成
```
Q5_K_M or Q6_K - Higher precision helps with code
```

### 创意写作
```
Q4_K_M - Sufficient quality
Q3_K_M - Acceptable for draft generation
```

### 技术/医疗领域
```
Q6_K or Q8_0 - Maximum accuracy
```

### 边缘设备（树莓派）
```
Q2_K or Q3_K_S - Fit in limited RAM
```

## 模型参数规模调整

### 70亿参数模型

| 格式 | 大小 | 所需内存 |
|------|------|----------|
| Q2_K | 26 GB | 32 GB |
| Q3_K_M | 32 GB | 40 GB |
| Q4_K_M | 41 GB | 48 GB |
| Q4_K_S | 39 GB | 46 GB |
| Q5_K_M | 48 GB | 56 GB |

**针对70亿参数模型的建议**：为适配普通消费级硬件，建议选用Q3_K_M或Q4_K_S格式。

## 查找预量化模型

可通过Hub搜索功能，并结合llama.cpp应用过滤器进行查找：

```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
```

如需查看某个特定代码库的相关信息，请打开：

```text
https://huggingface.co/<repo>?local-app=llama.cpp
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

随后无需借助额外的 Hub 工具，即可直接从 Hub 启动：

```bash
llama-cli -hf <repo>:Q4_K_M
llama-server -hf <repo>:Q4_K_M
```

如果您需要从 tree API 获取精确的文件名：

```bash
llama-server --hf-repo <repo> --hf-file <filename.gguf>
```

## 重要性矩阵（imatrix）

**定义**：用于提升量化质量的校准数据。

**优势**：
- 使用 Q4 格式时，困惑度可降低 10-20%
- 对于 Q3 及更低精度格式而言不可或缺

**使用方法**：
```bash
# 1. Generate importance matrix
./llama-imatrix \
    -m model-f16.gguf \
    -f calibration-data.txt \
    -o model.imatrix

# 2. Quantize with imatrix
./llama-quantize \
    --imatrix model.imatrix \
    model-f16.gguf \
    model-Q4_K_M.gguf \
    Q4_K_M
```

**校准数据**：
- 使用领域特定的文本（例如代码模型需使用代码）
- 约100MB的代表性文本
- 数据质量越高，量化效果越好

## 故障排除

**模型输出乱码**：
- 量化程度过激（Q2_K）
- 尝试使用Q4_K_M或Q5_K_M
- 确认模型已正确转换

**内存不足**：
- 使用较低的量化级别（改用Q4_K_S而非Q5_K_M）
- 减少迁移到GPU的层数（`-ngl`参数）
- 使用更小的上下文长度（`-c 2048`）

**推理速度过慢**：
- 较高的量化级别会消耗更多计算资源
- Q8_0的推理速度远低于Q4_K_M
- 需权衡速度与质量之间的关系
