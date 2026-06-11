# TorchTitan中的FSDP2

## 为何选择FSDP2？

FSDP2是对PyTorch全分片数据并行（FSDP）API的重新实现，它去掉了`FlatParameter`抽象层，从而提升了代码的可组合性并简化了实现过程。

### 相较于FSDP1的显著改进

- **基于DTensor的分片机制**：分片后的参数在维度0上表现为`DTensor`类型，便于操作且无需进行通信即可处理分片后的状态字典
- **更优的内存管理**：通过避免使用`recordStream`，实现了确定性的内存分配方式，并降低了GPU内存占用（减少了7%）
- **简化的API设计**：参数数量更少，且无需额外的包装类

### 性能表现

在配备8张H100显卡的Llama-7B模型上，FSDP2在保持相同损失曲线的前提下，能够实现更高的MFU值，同时峰值内存占用比FSDP1低7%。

## API参考文档

```python
from torch.distributed._composable.fsdp import fully_shard, MixedPrecisionPolicy, OffloadPolicy

@contract(state_cls=FSDPState)
def fully_shard(
    module: nn.Module,
    *,
    mesh: Optional[DeviceMesh] = None,
    reshard_after_forward: Union[bool, int] = True,
    mp_policy: MixedPrecisionPolicy = MixedPrecisionPolicy(),
    offload_policy: OffloadPolicy = OffloadPolicy(),
) -> nn.Module:
```

## 分片策略（ZeRO 对应方案）

| FSDP2 配置 | FSDP1 对应方案 | DeepSpeed |
|---------------------|------------------|-----------|
| 1D 网格结构 + `reshard_after_forward=True` | FULL_SHARD | ZeRO-3 |
| 1D 网格结构 + `reshard_after_forward=False` | SHARD_GRAD_OP | ZeRO-2 |
| 2D 网格结构 + `reshard_after_forward=True` | HYBRID_SHARD | MiCS |
| 1D/2D 网格结构 + `reshard_after_forward=8`（整数） | - | ZeRO++ hpZ |

## 元设备初始化

FSDP2 支持在分片完成后将张量加载到 GPU 上：

```python
# Initialize on meta device (no memory)
with torch.device("meta"):
    model = Transformer()

# Apply FSDP2 sharding
for module in model.modules():
    if isinstance(module, TransformerBlock):
        fully_shard(module)
fully_shard(model)

# Parameters still on meta device
for tensor in itertools.chain(model.parameters(), model.buffers()):
    assert tensor.device == torch.device("meta")

# Allocate sharded parameters on GPU
model.to_empty(device="cuda")

# Initialize weights
model.init_weights()
```

## 状态字典差异

| 操作 | FSDP1 | FSDP2 |
|-----------|-------|-------|
| `model.state_dict()` | 完整状态字典 | 分片状态字典（无需通信） |
| `optim.state_dict()` | 本地状态字典 | 分片状态字典（无需通信） |
| `summon_full_params()` | 支持 | 应使用 `DTensor` 相关 API，如 `full_tensor()` |
| 梯度裁剪 | `FSDP.clip_grad_norm_()` | `nn.utils.clip_grad_norm_()` |

## 混合精度训练

```python
from torch.distributed._composable.fsdp import MixedPrecisionPolicy

mp_policy = MixedPrecisionPolicy(
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.float32,
    output_dtype=torch.bfloat16,
    cast_forward_inputs=True,
)

fully_shard(model, mp_policy=mp_policy)
```

## HSDP（混合分片数据并行）

一种结合复制与分片技术的二维并行架构：

```python
from torch.distributed.device_mesh import init_device_mesh

# Replicate across 4 groups, shard within 8 GPUs each
mesh = init_device_mesh("cuda", (4, 8), mesh_dim_names=("replicate", "shard"))

fully_shard(model, mesh=mesh)
```

## TorchTitan中的配置设置

```toml
[parallelism]
# FSDP sharding degree (-1 = auto, use all available GPUs)
data_parallel_shard_degree = -1

# HSDP replication degree (1 = pure FSDP, >1 = HSDP)
data_parallel_replicate_degree = 1
```

## 已从 FSDP1 中移除的参数

以下 FSDP1 参数已不再需要：

- `auto_wrap_policy`：直接对模块应用 `fully_shard` 策略  
- `backward_prefetch`：始终使用 BACKWARD_PRE 模式  
- `param_init_fn`：改用元设备初始化方式  
- `device_id`：自动使用网格架构中的对应设备  
- `sync_module_states`：配合 DTensor 使用时已无需此参数  
- `limit_all_gathers`：新的内存管理机制已不再需要该参数  
- `use_orig_params`：始终设置为 true（因为已不存在 FlatParameter）
