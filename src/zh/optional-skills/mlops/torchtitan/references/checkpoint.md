# TorchTitan中的检查点机制

TorchTitan采用PyTorch分布式检查点（DCP）技术，以实现具备容错能力且可互操作的检查点功能。

## 基本配置

```toml
[checkpoint]
enable = true
folder = "checkpoint"
interval = 500
```

## 仅保存模型（更小的检查点）

排除优化器状态及训练元数据：

```toml
[checkpoint]
enable = true
last_save_model_only = true
export_dtype = "bfloat16"  # Optional: export in lower precision
```

## 排除需加载的密钥

针对已修改的设置进行部分检查点加载：

```toml
[checkpoint]
enable = true
exclude_from_loading = ["data_loader", "lr_scheduler"]
```

CLI 对应命令：
```bash
--checkpoint.exclude_from_loading data_loader,lr_scheduler
```

## 创建种子检查点

为确保流水线并行处理时的初始化一致性，此步骤是必需的：

```bash
NGPU=1 CONFIG_FILE=<path_to_config> ./run_train.sh \
  --checkpoint.enable \
  --checkpoint.create_seed_checkpoint \
  --parallelism.data_parallel_replicate_degree 1 \
  --parallelism.data_parallel_shard_degree 1 \
  --parallelism.tensor_parallel_degree 1 \
  --parallelism.pipeline_parallel_degree 1 \
  --parallelism.context_parallel_degree 1 \
  --parallelism.expert_parallel_degree 1
```

该功能在单核CPU上即可完成初始化，从而确保在任意数量的GPU环境下都能获得一致的初始化结果。

## 异步检查点机制

通过异步写入降低检查点的开销：

```toml
[checkpoint]
enable = true
async_mode = "async"  # Options: "disabled", "async", "async_with_pinned_mem"
```

## HuggingFace格式转换

### 训练期间

直接以HuggingFace格式保存：

```toml
[checkpoint]
last_save_in_hf = true
last_save_model_only = true
```

从 HuggingFace 加载：

```toml
[checkpoint]
initial_load_in_hf = true

[model]
hf_assets_path = "./path/to/hf/checkpoint"
```

### 离线转换

无需运行训练即可进行转换：

```bash
# HuggingFace -> TorchTitan
python ./scripts/checkpoint_conversion/convert_from_hf.py \
  <input_dir> <output_dir> \
  --model_name llama3 \
  --model_flavor 8B

# TorchTitan -> HuggingFace
python ./scripts/checkpoint_conversion/convert_to_hf.py \
  <input_dir> <output_dir> \
  --hf_assets_path ./assets/hf/Llama3.1-8B \
  --model_name llama3 \
  --model_flavor 8B
```

### 示例

```bash
python ./scripts/convert_from_hf.py \
  ~/.cache/huggingface/hub/models--meta-llama--Meta-Llama-3-8B/snapshots/8cde5ca8380496c9a6cc7ef3a8b46a0372a1d920/ \
  ./initial_load_path/ \
  --model_name llama3 \
  --model_flavor 8B
```

## 转换为单个.pt文件

将DCP分片检查点转换为单个PyTorch文件：

```bash
python -m torch.distributed.checkpoint.format_utils \
  dcp_to_torch \
  torchtitan/outputs/checkpoint/step-1000 \
  checkpoint.pt
```

## 检查点结构

DCP会保存分片后的检查点，这些检查点可针对不同的并行配置进行重新分片：

```
checkpoint/
├── step-500/
│   ├── .metadata
│   ├── __0_0.distcp
│   ├── __0_1.distcp
│   └── ...
└── step-1000/
    └── ...
```

## 恢复训练

从配置文件夹中的最新检查点继续自动训练。如需从特定步骤恢复训练：

```toml
[checkpoint]
load_step = 500  # Resume from step 500
```

## 与 TorchTune 的互操作性

使用 `last_save_model_only = true` 保存的检查点可直接导入 [torchtune](https://github.com/pytorch/torchtune) 中，以便进行微调。

## 完整配置示例

```toml
[checkpoint]
enable = true
folder = "checkpoint"
interval = 500
load_step = -1  # -1 = latest, or specify step number
last_save_model_only = true
export_dtype = "bfloat16"
async_mode = "async"
exclude_from_loading = []
last_save_in_hf = false
initial_load_in_hf = false
create_seed_checkpoint = false
```

## 最佳实践

1. **大型模型**：使用 `async_mode = "async"`，以便在训练过程中同步进行检查点保存操作。
2. **微调结果导出**：启用 `last_save_model_only` 选项并设置 `export_dtype = "bfloat16"`，以获得更小的文件体积。
3. **流水线并行处理**：务必先创建初始种子检查点。
4. **调试**：在开发阶段应频繁保存检查点，而在生产环境中则可适当减少保存频率。
5. **HF格式互操作**：对于离线转换，可使用转换脚本；而在训练工作流中，则可直接进行保存与加载操作。
