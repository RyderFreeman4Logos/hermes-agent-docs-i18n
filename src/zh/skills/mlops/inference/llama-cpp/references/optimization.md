# 性能优化指南

提升 llama.cpp 的推理速度与效率。

## CPU 优化

### 线程调优
```bash
# Set threads (default: physical cores)
./llama-cli -m model.gguf -t 8

# For AMD Ryzen 9 7950X (16 cores, 32 threads)
-t 16  # Best: physical cores

# Avoid hyperthreading (slower for matrix ops)
```

### BLAS加速功能
```bash
# OpenBLAS (faster matrix ops)
make LLAMA_OPENBLAS=1

# BLAS gives 2-3× speedup
```

## GPU卸载功能

### 层级卸载
```bash
# Offload 35 layers to GPU (hybrid mode)
./llama-cli -m model.gguf -ngl 35

# Offload all layers
./llama-cli -m model.gguf -ngl 999

# Find optimal value:
# Start with -ngl 999
# If OOM, reduce by 5 until fits
```

### 内存使用情况
```bash
# Check VRAM usage
nvidia-smi dmon

# Reduce context if needed
./llama-cli -m model.gguf -c 2048  # 2K context instead of 4K
```

## 批量处理

```bash
# Increase batch size for throughput
./llama-cli -m model.gguf -b 512  # Default: 512

# Physical batch (GPU)
--ubatch 128  # Process 128 tokens at once
```

## 上下文管理

```bash
# Default context (512 tokens)
-c 512

# Longer context (slower, more memory)
-c 4096

# Very long context (if model supports)
-c 32768
```

## 性能基准测试

### CPU性能（Llama 2-7B Q4_K_M）

| 硬件配置 | 处理速度 | 备注 |
|-------|-------|------|
| Apple M3 Max | 50 tok/s | 采用Metal加速技术 |
| AMD 7950X（16核） | 35 tok/s | 使用OpenBLAS算法 |
| Intel i9-13900K | 30 tok/s | 支持AVX2指令集 |

### GPU卸载性能（RTX 4090）

| 处理层级 | GPU处理速度 | 显存需求 |
|------------|-------|------|
| 0层（仅CPU处理） | 30 tok/s | 0 GB |
| 20层（混合模式） | 80 tok/s | 8 GB |
| 35层（全GPU处理） | 120 tok/s | 12 GB |
