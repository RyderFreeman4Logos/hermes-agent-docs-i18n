---
title: "Lambda Labs Gpu Cloud — Reserved and on-demand GPU cloud instances for ML training and inference"
sidebar_label: "Lambda Labs Gpu Cloud"
description: "Reserved and on-demand GPU cloud instances for ML training and inference"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Lambda Labs GPU 云服务

专为机器学习训练与推理场景提供的预留型及按需型 GPU 云实例。当您需要具备简单 SSH 访问权限的专用 GPU 实例、持久化文件系统，或用于大规模训练的高性能多节点集群时，可选用此服务。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/mlops/lambda-labs` 安装 |
| 路径 | `optional-skills/mlops/lambda-labs` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `lambda-cloud-client>=1.0.0` |
| 支持平台 | linux、macos、windows |
| 标签 | `基础设施`、`GPU 云服务`、`训练`、`推理`、`Lambda Labs` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，代理程序会将此内容视为操作指令。
:::

# Lambda Labs GPU 云服务

关于如何在 Lambda Labs GPU 云服务上运行机器学习工作负载的全面指南，涵盖按需实例及一键集群功能。

## 何时选择 Lambda Labs

**以下情况建议使用 Lambda Labs：**
- 需要具备完整 SSH 访问权限的专用 GPU 实例
- 需要运行时长为数小时至数天的长时间训练任务
- 希望享受无出口流量费且定价简单的服务
- 需要在不同会话之间保持数据持久化
- 需要高性能多节点集群（16–512 个 GPU）
- 希望使用预安装的机器学习套件（包含 PyTorch、CUDA、NCCL 的 Lambda Stack）

**核心功能：**
- **多种 GPU 选择**：B200、H100、GH200、A100、A10、A6000、V100
- **Lambda Stack**：预安装 PyTorch、TensorFlow、CUDA、cuDNN、NCCL
- **持久化文件系统**：确保数据在实例重启后依然保留
- **一键集群功能**：支持 16–512 个 GPU 的 Slurm 集群，并配备 InfiniBand 网络
- **简单定价模式**：按分钟计费，无出口流量费
- **全球覆盖**：在全球 12 个以上地区提供服务

**其他可选方案：**
- **Modal**：适用于无服务器、自动扩展型工作负载
- **SkyPilot**：用于多云编排与成本优化
- **RunPod**：提供更便宜的按需实例及无服务器端点
- **Vast.ai**：拥有价格最低的 GPU 市场平台

## 快速入门

### 账户设置

1. 访问 https://lambda.ai 创建账户
2. 添加支付方式
3. 从控制面板生成 API 密钥
4. 添加 SSH 密钥（启动实例前必需）

### 通过控制台启动实例

1. 访问 https://cloud.lambda.ai/instances
2. 点击“启动实例”
3. 选择 GPU 类型及区域
4. 选择 SSH 密钥
5. 可选：附加文件系统
6. 启动实例，等待 3–15 分钟

### 通过 SSH 连接

```bash
# Get instance IP from console
ssh ubuntu@<INSTANCE-IP>

# Or with specific key
ssh -i ~/.ssh/lambda_key ubuntu@<INSTANCE-IP>
```

## GPU实例

### 可用GPU型号

| GPU | 显存容量 | 每小时价格 | 最佳适用场景 |
|-----|----------|--------------|----------|
| B200 SXM6 | 180 GB | $4.99 | 大型模型训练，追求最快训练速度 |
| H100 SXM | 80 GB | $2.99-3.29 | 大型模型训练 |
| H100 PCIe | 80 GB | $2.49 | 性价比高的H100选项 |
| GH200 | 96 GB | $1.49 | 单GPU驱动的大型模型训练 |
| A100 80GB | 80 GB | $1.79 | 生产环境训练 |
| A100 40GB | 40 GB | $1.29 | 标准训练任务 |
| A10 | 24 GB | $0.75 | 推理与微调任务 |
| A6000 | 48 GB | $0.80 | 显存容量与价格比优异 |
| V100 | 16 GB | $0.55 | 预算有限的训练场景 |

### 实例配置选项

```
8x GPU: Best for distributed training (DDP, FSDP)
4x GPU: Large models, multi-GPU training
2x GPU: Medium workloads
1x GPU: Fine-tuning, inference, development
```

### 启动时间

- 单 GPU：3-5 分钟
- 多 GPU：10-15 分钟

## Lambda Stack

所有实例均预装了 Lambda Stack：

```bash
# Included software
- Ubuntu 22.04 LTS
- NVIDIA drivers (latest)
- CUDA 12.x
- cuDNN 8.x
- NCCL (for multi-GPU)
- PyTorch (latest)
- TensorFlow (latest)
- JAX
- JupyterLab
```

### 验证安装情况

```bash
# Check GPU
nvidia-smi

# Check PyTorch
python -c "import torch; print(torch.cuda.is_available())"

# Check CUDA version
nvcc --version
```

## Python API

### 安装指南

```bash
pip install lambda-cloud-client
```

### 认证

```python
import os
import lambda_cloud_client

# Configure with API key
configuration = lambda_cloud_client.Configuration(
    host="https://cloud.lambdalabs.com/api/v1",
    access_token=os.environ["LAMBDA_API_KEY"]
)
```

### 列出可用实例

```python
with lambda_cloud_client.ApiClient(configuration) as api_client:
    api = lambda_cloud_client.DefaultApi(api_client)

    # Get available instance types
    types = api.instance_types()
    for name, info in types.data.items():
        print(f"{name}: {info.instance_type.description}")
```

### 启动实例

```python
from lambda_cloud_client.models import LaunchInstanceRequest

request = LaunchInstanceRequest(
    region_name="us-west-1",
    instance_type_name="gpu_1x_h100_sxm5",
    ssh_key_names=["my-ssh-key"],
    file_system_names=["my-filesystem"],  # Optional
    name="training-job"
)

response = api.launch_instance(request)
instance_id = response.data.instance_ids[0]
print(f"Launched: {instance_id}")
```

### 列出正在运行的实例

```python
instances = api.list_instances()
for instance in instances.data:
    print(f"{instance.name}: {instance.ip} ({instance.status})")
```

### 终止实例

```python
from lambda_cloud_client.models import TerminateInstanceRequest

request = TerminateInstanceRequest(
    instance_ids=[instance_id]
)
api.terminate_instance(request)
```

### SSH密钥管理

```python
from lambda_cloud_client.models import AddSshKeyRequest

# Add SSH key
request = AddSshKeyRequest(
    name="my-key",
    public_key="ssh-rsa AAAA..."
)
api.add_ssh_key(request)

# List keys
keys = api.list_ssh_keys()

# Delete key
api.delete_ssh_key(key_id)
```

## 使用 curl 的 CLI

### 列出实例类型

```bash
curl -u $LAMBDA_API_KEY: \
  https://cloud.lambdalabs.com/api/v1/instance-types | jq
```

### 启动实例

```bash
curl -u $LAMBDA_API_KEY: \
  -X POST https://cloud.lambdalabs.com/api/v1/instance-operations/launch \
  -H "Content-Type: application/json" \
  -d '{
    "region_name": "us-west-1",
    "instance_type_name": "gpu_1x_h100_sxm5",
    "ssh_key_names": ["my-key"]
  }' | jq
```

### 终止实例

```bash
curl -u $LAMBDA_API_KEY: \
  -X POST https://cloud.lambdalabs.com/api/v1/instance-operations/terminate \
  -H "Content-Type: application/json" \
  -d '{"instance_ids": ["<INSTANCE-ID>"]}' | jq
```

## 持久存储

### 文件系统

文件系统能够在实例重启后依然保留数据：

```bash
# Mount location
/lambda/nfs/<FILESYSTEM_NAME>

# Example: save checkpoints
python train.py --checkpoint-dir /lambda/nfs/my-storage/checkpoints
```

### 创建文件系统

1. 进入 Lambda 控制台的存储管理页面。
2. 点击“创建文件系统”。
3. 选择区域（必须与实例所在区域一致）。
4. 命名并创建。

### 连接到实例

文件系统必须在实例启动时进行绑定：
- 通过控制台操作：在启动实例时选择相应的文件系统。
- 通过 API 操作：在启动请求中包含 `file_system_names` 参数。

### 最佳实践

<!-- ascii-guard-ignore -->
```bash
# Store on filesystem (persists)
/lambda/nfs/storage/
  ├── datasets/
  ├── checkpoints/
  ├── models/
  └── outputs/

# Local SSD (faster, ephemeral)
/home/ubuntu/
  └── working/  # Temporary files
```
## SSH 配置

### 添加 SSH 密钥

```bash
# Generate key locally
ssh-keygen -t ed25519 -f ~/.ssh/lambda_key

# Add public key to Lambda console
# Or via API
```

### 多个密钥

```bash
# On instance, add more keys
echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys
```

### 从 GitHub 导入

```bash
# On instance
ssh-import-id gh:username
```

### SSH 隧道功能

```bash
# Forward Jupyter
ssh -L 8888:localhost:8888 ubuntu@<IP>

# Forward TensorBoard
ssh -L 6006:localhost:6006 ubuntu@<IP>

# Multiple ports
ssh -L 8888:localhost:8888 -L 6006:localhost:6006 ubuntu@<IP>
```

## JupyterLab

### 通过控制台启动

1. 进入“实例”页面
2. 点击“云 IDE”列中的“启动”按钮
3. JupyterLab即会在浏览器中打开

### 手动访问

```bash
# On instance
jupyter lab --ip=0.0.0.0 --port=8888

# From local machine with tunnel
ssh -L 8888:localhost:8888 ubuntu@<IP>
# Open http://localhost:8888
```

## 训练工作流

### 单 GPU 训练

```bash
# SSH to instance
ssh ubuntu@<IP>

# Clone repo
git clone https://github.com/user/project
cd project

# Install dependencies
pip install -r requirements.txt

# Train
python train.py --epochs 100 --checkpoint-dir /lambda/nfs/storage/checkpoints
```

### 多 GPU 训练（单节点）

```python
# train_ddp.py
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def main():
    dist.init_process_group("nccl")
    rank = dist.get_rank()
    device = rank % torch.cuda.device_count()

    model = MyModel().to(device)
    model = DDP(model, device_ids=[device])

    # Training loop...

if __name__ == "__main__":
    main()
```

```bash
# Launch with torchrun (8 GPUs)
torchrun --nproc_per_node=8 train_ddp.py
```

### 将检查点保存至文件系统

```python
import os

checkpoint_dir = "/lambda/nfs/my-storage/checkpoints"
os.makedirs(checkpoint_dir, exist_ok=True)

# Save checkpoint
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}, f"{checkpoint_dir}/checkpoint_{epoch}.pt")
```

## 一键式集群

### 概述

高性能 Slurm 集群，具备以下配置：
- 16 至 512 块 NVIDIA H100 或 B200 GPU
- NVIDIA Quantum-2 400 Gb/s InfiniBand 网络
- 3200 Gb/s 高速的 GPUDirect RDMA 技术
- 预装好的分布式机器学习框架套件

### 包含的软件

- Ubuntu 22.04 LTS 操作系统 + Lambda 框架套件
- NCCL、Open MPI 工具
- 支持 DDP 和 FSDP 模式的 PyTorch
- TensorFlow 框架
- OFED 驱动程序

### 存储方案

- 每个计算节点配备 24 TB NVMe 存储（临时数据存储）
- 使用 Lambda 文件系统用于持久化数据存储

### 多节点训练功能

```bash
# On Slurm cluster
srun --nodes=4 --ntasks-per-node=8 --gpus-per-node=8 \
  torchrun --nnodes=4 --nproc_per_node=8 \
  --rdzv_backend=c10d --rdzv_endpoint=$MASTER_ADDR:29500 \
  train.py
```

## 网络连接

### 带宽

- 实例间通信（同一区域）：最高可达 200 Gbps
- 接入互联网的出站带宽：最高为 20 Gbps

### 防火墙设置

- 默认情况下：仅开放端口 22（SSH）
- 可在 Lambda 控制台配置其他端口
- 默认允许 ICMP 流量

### 私有 IP 地址

```bash
# Find private IP
ip addr show | grep 'inet '
```

## 常见工作流程

### 工作流程 1：大语言模型微调

```bash
# 1. Launch 8x H100 instance with filesystem

# 2. SSH and setup
ssh ubuntu@<IP>
pip install transformers accelerate peft

# 3. Download model to filesystem
python -c "
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-2-7b-hf')
model.save_pretrained('/lambda/nfs/storage/models/llama-2-7b')
"

# 4. Fine-tune with checkpoints on filesystem
accelerate launch --num_processes 8 train.py \
  --model_path /lambda/nfs/storage/models/llama-2-7b \
  --output_dir /lambda/nfs/storage/outputs \
  --checkpoint_dir /lambda/nfs/storage/checkpoints
```

### 工作流 2：批量推理

```bash
# 1. Launch A10 instance (cost-effective for inference)

# 2. Run inference
python inference.py \
  --model /lambda/nfs/storage/models/fine-tuned \
  --input /lambda/nfs/storage/data/inputs.jsonl \
  --output /lambda/nfs/storage/data/outputs.jsonl
```

## 成本优化

### 选择合适的 GPU

| 任务 | 推荐 GPU |
|------|----------|
| 大语言模型微调（70亿参数） | A100 40GB |
| 大语言模型微调（700亿参数） | 8块 H100 |
| 模型推理 | A10、A6000 |
| 开发测试 | V100、A10 |
| 最高性能需求 | B200 |

### 降低成本

1. **使用文件系统**：避免重复下载数据
2. **频繁保存检查点**：可从中断处继续训练
3. **合理配置资源**：避免过度分配 GPU 资源
4. **手动终止空闲实例**：无需自动停止，手动操作即可

### 监控使用情况

- 控制面板可实时显示 GPU 使用率
- 提供 API 用于程序化监控

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 实例无法启动 | 检查所在区域是否可用，尝试更换其他 GPU |
| SSH 连接被拒绝 | 等待实例完成初始化（3-15分钟） |
| 终止实例后数据丢失 | 使用持久化文件系统 |
| 数据传输速度慢 | 使用同一区域的文件系统 |
| 无法检测到 GPU | 重启实例，检查驱动程序 |

## 参考资料

- **[高级用法](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/lambda-labs/references/advanced-usage.md)** - 多节点训练、API 自动化
- **[故障排查](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/lambda-labs/references/troubleshooting.md)** - 常见问题及解决方案

## 资源链接

- **文档**：https://docs.lambda.ai
- **控制台**：https://cloud.lambda.ai
- **价格信息**：https://lambda.ai/instances
- **技术支持**：https://support.lambdalabs.com
- **博客**：https://lambda.ai/blog
