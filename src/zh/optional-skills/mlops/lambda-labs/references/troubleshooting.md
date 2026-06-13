# Lambda Labs 故障排除指南

## 实例启动问题

### 无可用实例

**错误提示**：显示“暂无可用容量”或该实例类型未被列出

**解决方案**：
```bash
# Check availability via API
curl -u $LAMBDA_API_KEY: \
  https://cloud.lambdalabs.com/api/v1/instance-types | jq '.data | to_entries[] | select(.value.regions_with_capacity_available | length > 0) | .key'

# Try different regions
# US regions: us-west-1, us-east-1, us-south-1
# International: eu-west-1, asia-northeast-1, etc.

# Try alternative GPU types
# H100 not available? Try A100
# A100 not available? Try A10 or A6000
```

### 实例启动卡住

**问题**：实例显示“正在启动”状态已超过20分钟

**解决方案**：
```bash
# Single-GPU: Should be ready in 3-5 minutes
# Multi-GPU (8x): May take 10-15 minutes

# If stuck longer:
# 1. Terminate the instance
# 2. Try a different region
# 3. Try a different instance type
# 4. Contact Lambda support if persistent
```

### API身份验证失败

**错误信息**：`401 Unauthorized` 或 `403 Forbidden`

**解决方案**：
```bash
# Verify API key format (should start with specific prefix)
echo $LAMBDA_API_KEY

# Test API key
curl -u $LAMBDA_API_KEY: \
  https://cloud.lambdalabs.com/api/v1/instance-types

# Generate new API key from Lambda console if needed
# Settings > API keys > Generate
```

### 配额限制已达到

**错误信息**： “实例数量已达上限”或“配额超出限制”

**解决方案**：
- 在控制台查看当前正在运行的实例
- 终止未使用的实例
- 联系 Lambda 支持团队申请增加配额
- 对于大规模需求，可使用一键集群功能

## SSH 连接问题

### 被拒绝连接

**错误信息**： `ssh: connect to host <IP> port 22: Connection refused`

**解决方案**：
```bash
# Wait for instance to fully initialize
# Single-GPU: 3-5 minutes
# Multi-GPU: 10-15 minutes

# Check instance status in console (should be "active")

# Verify correct IP address
curl -u $LAMBDA_API_KEY: \
  https://cloud.lambdalabs.com/api/v1/instances | jq '.data[].ip'
```

### 权限被拒绝

**错误信息**：`权限被拒绝（公钥）`

**解决方案**：
```bash
# Verify SSH key matches
ssh -v -i ~/.ssh/lambda_key ubuntu@<IP>

# Check key permissions
chmod 600 ~/.ssh/lambda_key
chmod 644 ~/.ssh/lambda_key.pub

# Verify key was added to Lambda console before launch
# Keys must be added BEFORE launching instance

# Check authorized_keys on instance (if you have another way in)
cat ~/.ssh/authorized_keys
```

### 主机密钥验证失败

**错误信息**：`警告：远程主机标识已发生变化！`

**解决方案**：
```bash
# This happens when IP is reused by different instance
# Remove old key
ssh-keygen -R <IP>

# Then connect again
ssh ubuntu@<IP>
```

### SSH 连接超时

**错误信息**：`ssh: connect to host <IP> port 22: Operation timed out`

**解决方案**：
```bash
# Check if instance is in "active" state

# Verify firewall allows SSH (port 22)
# Lambda console > Firewall

# Check your local network allows outbound SSH

# Try from different network/VPN
```

## GPU 相关问题

### 未检测到 GPU

**错误提示**：出现 `nvidia-smi: command not found` 的信息，或未显示任何 GPU。

**解决方案**：
```bash
# Reboot instance
sudo reboot

# Reinstall NVIDIA drivers (if needed)
wget -nv -O- https://lambdalabs.com/install-lambda-stack.sh | sh -
sudo reboot

# Check driver status
nvidia-smi
lsmod | grep nvidia
```

### CUDA 内存不足

**错误信息**：`torch.cuda.OutOfMemoryError: CUDA 内存不足`

**解决方案**：
```python
# Check GPU memory
import torch
print(torch.cuda.get_device_properties(0).total_memory / 1e9, "GB")

# Clear cache
torch.cuda.empty_cache()

# Reduce batch size
batch_size = batch_size // 2

# Enable gradient checkpointing
model.gradient_checkpointing_enable()

# Use mixed precision
from torch.cuda.amp import autocast
with autocast():
    outputs = model(**inputs)

# Use larger GPU instance
# A100-40GB → A100-80GB → H100
```

### CUDA版本不匹配

**错误提示**：`当前CUDA驱动程序版本低于所使用的CUDA运行时版本`

**解决方案**：
```bash
# Check versions
nvidia-smi  # Shows driver CUDA version
nvcc --version  # Shows toolkit version

# Lambda Stack should have compatible versions
# If mismatch, reinstall Lambda Stack
wget -nv -O- https://lambdalabs.com/install-lambda-stack.sh | sh -
sudo reboot

# Or install specific PyTorch version
pip install torch==2.1.0+cu121 -f https://download.pytorch.org/whl/torch_stable.html
```

### 多 GPU 功能无法使用

**错误提示**：仅使用了单个 GPU

**解决方案**：
```python
# Check all GPUs visible
import torch
print(f"GPUs available: {torch.cuda.device_count()}")

# Verify CUDA_VISIBLE_DEVICES not set restrictively
import os
print(os.environ.get("CUDA_VISIBLE_DEVICES", "not set"))

# Use DataParallel or DistributedDataParallel
model = torch.nn.DataParallel(model)
# or
model = torch.nn.parallel.DistributedDataParallel(model)
```

## 文件系统问题

### 文件系统未挂载

**错误提示**：/lambda/nfs/<名称> 不存在

**解决方案**：
```bash
# Filesystem must be attached at launch time
# Cannot attach to running instance

# Verify filesystem was selected during launch

# Check mount points
df -h | grep lambda

# If missing, terminate and relaunch with filesystem
```

### 文件系统性能低下

**问题**：对文件系统的读写操作速度缓慢

**解决方案**：
```bash
# Use local SSD for temporary/intermediate files
# /home/ubuntu has fast NVMe storage

# Copy frequently accessed data to local storage
cp -r /lambda/nfs/storage/dataset /home/ubuntu/dataset

# Use filesystem for checkpoints and final outputs only

# Check network bandwidth
iperf3 -c <filesystem_server>
```

### 终止后数据丢失问题

**问题**：实例终止后文件消失

**解决方案**：
```bash
# Root volume (/home/ubuntu) is EPHEMERAL
# Data there is lost on termination

# ALWAYS use filesystem for persistent data
/lambda/nfs/<filesystem_name>/

# Sync important local files before terminating
rsync -av /home/ubuntu/outputs/ /lambda/nfs/storage/outputs/
```

### 文件系统已满

**错误提示**：`设备上没有剩余空间`

**解决方案**：
```bash
# Check filesystem usage
df -h /lambda/nfs/storage

# Find large files
du -sh /lambda/nfs/storage/* | sort -h

# Clean up old checkpoints
find /lambda/nfs/storage/checkpoints -mtime +7 -delete

# Increase filesystem size in Lambda console
# (may require support request)
```

## 网络问题

### 端口无法访问

**错误提示**：无法连接到相关服务（如 TensorBoard、Jupyter 等）

**解决方案**：
```bash
# Lambda default: Only port 22 is open
# Configure firewall in Lambda console

# Or use SSH tunneling (recommended)
ssh -L 6006:localhost:6006 ubuntu@<IP>
# Access at http://localhost:6006

# For Jupyter
ssh -L 8888:localhost:8888 ubuntu@<IP>
```

### 数据下载速度过慢

**问题**：数据集的下载速度较慢

**解决方案**：
```bash
# Check available bandwidth
speedtest-cli

# Use multi-threaded download
aria2c -x 16 <URL>

# For HuggingFace models
export HF_HUB_ENABLE_HF_TRANSFER=1
pip install hf_transfer

# For S3, use parallel transfer
aws s3 sync s3://bucket/data /local/data --quiet
```

### 节点间通信失败

**错误提示**：分布式训练无法在各个节点之间建立连接

**解决方案**：
```bash
# Verify nodes in same region (required)

# Check private IPs can communicate
ping <other_node_private_ip>

# Verify NCCL settings
export NCCL_DEBUG=INFO
export NCCL_IB_DISABLE=0  # Enable InfiniBand if available

# Check firewall allows distributed ports
# Need: 29500 (PyTorch), or configured MASTER_PORT
```

## 软件问题

### 包安装失败

**错误提示**：`pip install` 错误

**解决方案**：
```bash
# Use virtual environment (don't modify system Python)
python -m venv ~/myenv
source ~/myenv/bin/activate
pip install <package>

# For CUDA packages, match CUDA version
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Clear pip cache if corrupted
pip cache purge
```

### Python版本问题

**错误提示**：该软件包需要特定版本的Python

**解决方案**：
```bash
# Install alternate Python (don't replace system Python)
sudo apt install python3.11 python3.11-venv python3.11-dev

# Create venv with specific Python
python3.11 -m venv ~/py311env
source ~/py311env/bin/activate
```

### ImportError 或 ModuleNotFoundError

**错误提示**：尽管已安装，但无法找到该模块

**解决方案**：
```bash
# Verify correct Python environment
which python
pip list | grep <module>

# Ensure virtual environment is activated
source ~/myenv/bin/activate

# Reinstall in correct environment
pip uninstall <package>
pip install <package>
```

## 训练问题

### 训练进程卡住

**问题**：训练进度停止，无输出结果

**解决方案**：
```bash
# Check GPU utilization
watch -n 1 nvidia-smi

# If GPUs at 0%, likely data loading bottleneck
# Increase num_workers in DataLoader

# Check for deadlocks in distributed training
export NCCL_DEBUG=INFO

# Add timeouts
dist.init_process_group(..., timeout=timedelta(minutes=30))
```

### 检查点损坏

**错误信息**：`RuntimeError: storage has wrong size` 或类似错误

**解决方案**：
```python
# Use safe saving pattern
checkpoint_path = "/lambda/nfs/storage/checkpoint.pt"
temp_path = checkpoint_path + ".tmp"

# Save to temp first
torch.save(state_dict, temp_path)
# Then atomic rename
os.rename(temp_path, checkpoint_path)

# For loading corrupted checkpoint
try:
    state = torch.load(checkpoint_path)
except:
    # Fall back to previous checkpoint
    state = torch.load(checkpoint_path + ".backup")
```

### 内存泄漏

**问题**：内存使用量随时间逐渐增加

**解决方案**：
```python
# Clear CUDA cache periodically
torch.cuda.empty_cache()

# Detach tensors when logging
loss_value = loss.detach().cpu().item()

# Don't accumulate gradients unintentionally
optimizer.zero_grad(set_to_none=True)

# Use gradient accumulation properly
if (step + 1) % accumulation_steps == 0:
    optimizer.step()
    optimizer.zero_grad()
```

## 账单问题

### 意外收费

**问题**：账单金额高于预期

**解决方案**：
```bash
# Check for forgotten running instances
curl -u $LAMBDA_API_KEY: \
  https://cloud.lambdalabs.com/api/v1/instances | jq '.data[].id'

# Terminate all instances
# Lambda console > Instances > Terminate all

# Lambda charges by the minute
# No charge for stopped instances (but no "stop" feature - only terminate)
```

### 实例意外终止

**问题**：实例在未手动终止的情况下消失。

**可能原因**：
- 支付问题（卡片被拒）
- 账户被暂停
- 实例健康检查失败

**解决方案**：
- 查看邮箱中的 Lambda 通知
- 在控制台确认支付方式
- 联系 Lambda 客服
- 始终将数据写入文件系统

## 常见错误信息

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| `No capacity available` | 所选区域或 GPU 已耗尽 | 尝试其他区域或 GPU 类型 |
| `Permission denied (publickey)` | SSH 密钥不匹配 | 重新添加密钥并检查权限 |
| `CUDA out of memory` | 模型过大 | 减小批次大小或使用更强大的 GPU |
| `No space left on device` | 磁盘空间不足 | 清理数据或使用文件系统 |
| `Connection refused` | 实例尚未启动完成 | 等待 3-15 分钟直至实例启动 |
| `Module not found` | Python 环境配置错误 | 激活正确的虚拟环境 |

## 获取帮助

1. **文档**：https://docs.lambda.ai
2. **客服支持**：https://support.lambdalabs.com
3. **邮箱**：support@lambdalabs.com
4. **服务状态**：访问 Lambda 状态页面查看服务中断情况

### 需提供的信息

联系客服时，请提供以下信息：
- 实例 ID
- 所在区域
- 实例类型
- 错误信息（完整堆栈跟踪）
| 复现步骤 |
|---------|
| 发生时间 |
