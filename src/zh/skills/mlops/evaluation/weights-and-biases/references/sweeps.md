# 全面超参数扫描指南

使用 W&B Sweeps 进行超参数优化的完整指南。

## 目录
- 扫描配置
- 搜索策略
- 参数分布
- 提前终止
- 并行执行
- 高级模式
- 实际应用案例

## 扫描配置

### 基本扫描配置

```python
sweep_config = {
    'method': 'bayes',  # Search strategy
    'metric': {
        'name': 'val/accuracy',
        'goal': 'maximize'  # or 'minimize'
    },
    'parameters': {
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-5,
            'max': 1e-1
        },
        'batch_size': {
            'values': [16, 32, 64, 128]
        }
    }
}

# Initialize sweep
sweep_id = wandb.sweep(sweep_config, project="my-project")
```

### 完整配置示例

```python
sweep_config = {
    # Required: Search method
    'method': 'bayes',

    # Required: Optimization metric
    'metric': {
        'name': 'val/f1_score',
        'goal': 'maximize'
    },

    # Required: Parameters to search
    'parameters': {
        # Continuous parameter
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-5,
            'max': 1e-1
        },

        # Discrete values
        'batch_size': {
            'values': [16, 32, 64, 128]
        },

        # Categorical
        'optimizer': {
            'values': ['adam', 'sgd', 'rmsprop', 'adamw']
        },

        # Uniform distribution
        'dropout': {
            'distribution': 'uniform',
            'min': 0.1,
            'max': 0.5
        },

        # Integer range
        'num_layers': {
            'distribution': 'int_uniform',
            'min': 2,
            'max': 10
        },

        # Fixed value (constant across runs)
        'epochs': {
            'value': 50
        }
    },

    # Optional: Early termination
    'early_terminate': {
        'type': 'hyperband',
        'min_iter': 5,
        's': 2,
        'eta': 3,
        'max_iter': 27
    }
}
```

## 搜索策略

### 1. 网格搜索

遍历所有可能的组合进行彻底搜索。

```python
sweep_config = {
    'method': 'grid',
    'parameters': {
        'learning_rate': {
            'values': [0.001, 0.01, 0.1]
        },
        'batch_size': {
            'values': [16, 32, 64]
        },
        'optimizer': {
            'values': ['adam', 'sgd']
        }
    }
}

# Total runs: 3 × 3 × 2 = 18 runs
```

**优点：**  
- 全面搜索能力  
- 结果可重复  
- 无随机性  

**缺点：**  
- 参数数量增加时性能呈指数级下降  
- 对连续型参数处理效率低下  
- 参数数量超过3-4个时无法扩展  

**适用场景：**  
- 参数数量较少（< 4个）  
- 所有参数均为离散值  
- 需要实现全面覆盖  

### 2. 随机搜索  

随机选取参数组合进行搜索。

```python
sweep_config = {
    'method': 'random',
    'parameters': {
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-5,
            'max': 1e-1
        },
        'batch_size': {
            'values': [16, 32, 64, 128, 256]
        },
        'dropout': {
            'distribution': 'uniform',
            'min': 0.0,
            'max': 0.5
        },
        'num_layers': {
            'distribution': 'int_uniform',
            'min': 2,
            'max': 8
        }
    }
}

# Run 100 random trials
wandb.agent(sweep_id, function=train, count=100)
```

**优点：**  
- 能够处理大量参数  
- 可持续运行无需中断  
- 通常能快速找到优质解  

**缺点：**  
- 无法从过往运行中学习  
- 可能会错过最优解区域  
- 结果会因随机种子不同而有所差异  

**适用场景：**  
- 参数数量较多（> 4个）  
- 需要快速探索解决方案  
- 计算资源有限的情况  

### 3. 贝叶斯优化（推荐方案）  
通过学习以往的试验结果，筛选出具有潜力的解空间。

```python
sweep_config = {
    'method': 'bayes',
    'metric': {
        'name': 'val/loss',
        'goal': 'minimize'
    },
    'parameters': {
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-5,
            'max': 1e-1
        },
        'weight_decay': {
            'distribution': 'log_uniform',
            'min': 1e-6,
            'max': 1e-2
        },
        'dropout': {
            'distribution': 'uniform',
            'min': 0.1,
            'max': 0.5
        },
        'num_layers': {
            'values': [2, 3, 4, 5, 6]
        }
    }
}
```

**优点：**  
- 样本利用率最高  
- 能从过往试验中学习  
- 专注于具有潜力的区域  

**缺点：**  
- 需要初始随机探索阶段  
- 可能陷入局部最优解  
- 每次迭代的速度较慢  

**适用场景：**  
- 训练成本较高的情况  
- 需要最佳性能时  
- 计算资源有限的情形  

## 参数分布  

### 连续分布

```python
# Log-uniform: Good for learning rates, regularization
'learning_rate': {
    'distribution': 'log_uniform',
    'min': 1e-6,
    'max': 1e-1
}

# Uniform: Good for dropout, momentum
'dropout': {
    'distribution': 'uniform',
    'min': 0.0,
    'max': 0.5
}

# Normal distribution
'parameter': {
    'distribution': 'normal',
    'mu': 0.5,
    'sigma': 0.1
}

# Log-normal distribution
'parameter': {
    'distribution': 'log_normal',
    'mu': 0.0,
    'sigma': 1.0
}
```

### 离散分布

```python
# Fixed values
'batch_size': {
    'values': [16, 32, 64, 128, 256]
}

# Integer uniform
'num_layers': {
    'distribution': 'int_uniform',
    'min': 2,
    'max': 10
}

# Quantized uniform (step size)
'layer_size': {
    'distribution': 'q_uniform',
    'min': 32,
    'max': 512,
    'q': 32  # Step by 32: 32, 64, 96, 128...
}

# Quantized log-uniform
'hidden_size': {
    'distribution': 'q_log_uniform',
    'min': 32,
    'max': 1024,
    'q': 32
}
```

### 分类参数

```python
# Optimizers
'optimizer': {
    'values': ['adam', 'sgd', 'rmsprop', 'adamw']
}

# Model architectures
'model': {
    'values': ['resnet18', 'resnet34', 'resnet50', 'efficientnet_b0']
}

# Activation functions
'activation': {
    'values': ['relu', 'gelu', 'silu', 'leaky_relu']
}
```

## 提前终止

提前停止表现不佳的运行任务，以节省计算资源。

### Hyperband算法

```python
sweep_config = {
    'method': 'bayes',
    'metric': {'name': 'val/accuracy', 'goal': 'maximize'},
    'parameters': {...},

    # Hyperband early termination
    'early_terminate': {
        'type': 'hyperband',
        'min_iter': 3,      # Minimum iterations before termination
        's': 2,             # Bracket count
        'eta': 3,           # Downsampling rate
        'max_iter': 27      # Maximum iterations
    }
}
```

**工作原理：**
- 在括号内进行试验运行
- 每轮保留表现最佳的 1 名/或按预定比例的参与者
- 提前淘汰表现最差的参与者

### 自定义终止机制

```python
def train():
    run = wandb.init()

    for epoch in range(MAX_EPOCHS):
        loss = train_epoch()
        val_acc = validate()

        wandb.log({'val/accuracy': val_acc, 'epoch': epoch})

        # Custom early stopping
        if epoch > 5 and val_acc < 0.5:
            print("Early stop: Poor performance")
            break

        if epoch > 10 and val_acc > best_acc - 0.01:
            print("Early stop: No improvement")
            break
```

## 训练功能

### 基本模板

```python
def train():
    # Initialize W&B run
    run = wandb.init()

    # Get hyperparameters
    config = wandb.config

    # Build model with config
    model = build_model(
        hidden_size=config.hidden_size,
        num_layers=config.num_layers,
        dropout=config.dropout
    )

    # Create optimizer
    optimizer = create_optimizer(
        model.parameters(),
        name=config.optimizer,
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )

    # Training loop
    for epoch in range(config.epochs):
        # Train
        train_loss, train_acc = train_epoch(
            model, optimizer, train_loader, config.batch_size
        )

        # Validate
        val_loss, val_acc = validate(model, val_loader)

        # Log metrics
        wandb.log({
            'train/loss': train_loss,
            'train/accuracy': train_acc,
            'val/loss': val_loss,
            'val/accuracy': val_acc,
            'epoch': epoch
        })

    # Log final model
    torch.save(model.state_dict(), 'model.pth')
    wandb.save('model.pth')

    # Finish run
    wandb.finish()
```

### 集成 PyTorch 技术

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import wandb

def train():
    run = wandb.init()
    config = wandb.config

    # Data
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True
    )

    # Model
    model = ResNet(
        num_classes=config.num_classes,
        dropout=config.dropout
    ).to(device)

    # Optimizer
    if config.optimizer == 'adam':
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
    elif config.optimizer == 'sgd':
        optimizer = torch.optim.SGD(
            model.parameters(),
            lr=config.learning_rate,
            momentum=config.momentum,
            weight_decay=config.weight_decay
        )

    # Scheduler
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config.epochs
    )

    # Training
    for epoch in range(config.epochs):
        model.train()
        train_loss = 0.0

        for data, target in train_loader:
            data, target = data.to(device), target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = nn.CrossEntropyLoss()(output, target)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss, val_acc = validate(model, val_loader)

        # Step scheduler
        scheduler.step()

        # Log
        wandb.log({
            'train/loss': train_loss / len(train_loader),
            'val/loss': val_loss,
            'val/accuracy': val_acc,
            'learning_rate': scheduler.get_last_lr()[0],
            'epoch': epoch
        })
```

## 并行执行

### 多个智能体

并行运行扫描智能体，从而加快搜索速度。

```python
# Initialize sweep once
sweep_id = wandb.sweep(sweep_config, project="my-project")

# Run multiple agents in parallel
# Agent 1 (Terminal 1)
wandb.agent(sweep_id, function=train, count=20)

# Agent 2 (Terminal 2)
wandb.agent(sweep_id, function=train, count=20)

# Agent 3 (Terminal 3)
wandb.agent(sweep_id, function=train, count=20)

# Total: 60 runs across 3 agents
```

### 多 GPU 执行

```python
import os

def train():
    # Get available GPU
    gpu_id = os.environ.get('CUDA_VISIBLE_DEVICES', '0')

    run = wandb.init()
    config = wandb.config

    # Train on specific GPU
    device = torch.device(f'cuda:{gpu_id}')
    model = model.to(device)

    # ... rest of training ...

# Run agents on different GPUs
# Terminal 1
# CUDA_VISIBLE_DEVICES=0 wandb agent sweep_id

# Terminal 2
# CUDA_VISIBLE_DEVICES=1 wandb agent sweep_id

# Terminal 3
# CUDA_VISIBLE_DEVICES=2 wandb agent sweep_id
```

## 高级模式

### 嵌套参数

```python
sweep_config = {
    'method': 'bayes',
    'metric': {'name': 'val/accuracy', 'goal': 'maximize'},
    'parameters': {
        'model': {
            'parameters': {
                'type': {
                    'values': ['resnet', 'efficientnet']
                },
                'size': {
                    'values': ['small', 'medium', 'large']
                }
            }
        },
        'optimizer': {
            'parameters': {
                'type': {
                    'values': ['adam', 'sgd']
                },
                'lr': {
                    'distribution': 'log_uniform',
                    'min': 1e-5,
                    'max': 1e-1
                }
            }
        }
    }
}

# Access nested config
def train():
    run = wandb.init()
    model_type = wandb.config.model.type
    model_size = wandb.config.model.size
    opt_type = wandb.config.optimizer.type
    lr = wandb.config.optimizer.lr
```

### 条件参数

```python
sweep_config = {
    'method': 'bayes',
    'parameters': {
        'optimizer': {
            'values': ['adam', 'sgd']
        },
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-5,
            'max': 1e-1
        },
        # Only used if optimizer == 'sgd'
        'momentum': {
            'distribution': 'uniform',
            'min': 0.5,
            'max': 0.99
        }
    }
}

def train():
    run = wandb.init()
    config = wandb.config

    if config.optimizer == 'adam':
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=config.learning_rate
        )
    elif config.optimizer == 'sgd':
        optimizer = torch.optim.SGD(
            model.parameters(),
            lr=config.learning_rate,
            momentum=config.momentum  # Conditional parameter
        )
```

## 实际应用案例

### 图像分类

```python
sweep_config = {
    'method': 'bayes',
    'metric': {
        'name': 'val/top1_accuracy',
        'goal': 'maximize'
    },
    'parameters': {
        # Model
        'architecture': {
            'values': ['resnet50', 'resnet101', 'efficientnet_b0', 'efficientnet_b3']
        },
        'pretrained': {
            'values': [True, False]
        },

        # Training
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-5,
            'max': 1e-2
        },
        'batch_size': {
            'values': [16, 32, 64, 128]
        },
        'optimizer': {
            'values': ['adam', 'sgd', 'adamw']
        },
        'weight_decay': {
            'distribution': 'log_uniform',
            'min': 1e-6,
            'max': 1e-2
        },

        # Regularization
        'dropout': {
            'distribution': 'uniform',
            'min': 0.0,
            'max': 0.5
        },
        'label_smoothing': {
            'distribution': 'uniform',
            'min': 0.0,
            'max': 0.2
        },

        # Data augmentation
        'mixup_alpha': {
            'distribution': 'uniform',
            'min': 0.0,
            'max': 1.0
        },
        'cutmix_alpha': {
            'distribution': 'uniform',
            'min': 0.0,
            'max': 1.0
        }
    },
    'early_terminate': {
        'type': 'hyperband',
        'min_iter': 5
    }
}
```

### 自然语言处理微调

```python
sweep_config = {
    'method': 'bayes',
    'metric': {'name': 'eval/f1', 'goal': 'maximize'},
    'parameters': {
        # Model
        'model_name': {
            'values': ['bert-base-uncased', 'roberta-base', 'distilbert-base-uncased']
        },

        # Training
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-6,
            'max': 1e-4
        },
        'per_device_train_batch_size': {
            'values': [8, 16, 32]
        },
        'num_train_epochs': {
            'values': [3, 4, 5]
        },
        'warmup_ratio': {
            'distribution': 'uniform',
            'min': 0.0,
            'max': 0.1
        },
        'weight_decay': {
            'distribution': 'log_uniform',
            'min': 1e-4,
            'max': 1e-1
        },

        # Optimizer
        'adam_beta1': {
            'distribution': 'uniform',
            'min': 0.8,
            'max': 0.95
        },
        'adam_beta2': {
            'distribution': 'uniform',
            'min': 0.95,
            'max': 0.999
        }
    }
}
```

## 最佳实践

### 1. 从小规模开始

```python
# Initial exploration: Random search, 20 runs
sweep_config_v1 = {
    'method': 'random',
    'parameters': {...}
}
wandb.agent(sweep_id_v1, train, count=20)

# Refined search: Bayes, narrow ranges
sweep_config_v2 = {
    'method': 'bayes',
    'parameters': {
        'learning_rate': {
            'min': 5e-5,  # Narrowed from 1e-6 to 1e-4
            'max': 1e-4
        }
    }
}
```

### 2. 使用日志刻度

```python
# ✅ Good: Log scale for learning rate
'learning_rate': {
    'distribution': 'log_uniform',
    'min': 1e-6,
    'max': 1e-2
}

# ❌ Bad: Linear scale
'learning_rate': {
    'distribution': 'uniform',
    'min': 0.000001,
    'max': 0.01
}
```

### 3. 设置合理范围

```python
# Base ranges on prior knowledge
'learning_rate': {'min': 1e-5, 'max': 1e-3},  # Typical for Adam
'batch_size': {'values': [16, 32, 64]},       # GPU memory limits
'dropout': {'min': 0.1, 'max': 0.5}           # Too high hurts training
```

### 4. 监控资源使用情况

```python
def train():
    run = wandb.init()

    # Log system metrics
    wandb.log({
        'system/gpu_memory_allocated': torch.cuda.memory_allocated(),
        'system/gpu_memory_reserved': torch.cuda.memory_reserved()
    })
```

### 5. 保存最佳模型

```python
def train():
    run = wandb.init()
    best_acc = 0.0

    for epoch in range(config.epochs):
        val_acc = validate(model)

        if val_acc > best_acc:
            best_acc = val_acc
            # Save best checkpoint
            torch.save(model.state_dict(), 'best_model.pth')
            wandb.save('best_model.pth')
```

## 资源

- **Sweeps 文档**：https://docs.wandb.ai/guides/sweeps
- **配置参考**：https://docs.wandb.ai/guides/sweeps/configuration
- **示例代码**：https://github.com/wandb/examples/tree/master/examples/wandb-sweeps
