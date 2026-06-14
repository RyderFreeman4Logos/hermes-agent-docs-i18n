---
name: pytorch-fsdp
description: Expert guidance for Fully Sharded Data Parallel training with PyTorch FSDP - parameter sharding, mixed precision, CPU offloading, FSDP2
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [torch>=2.0, transformers]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Distributed Training, PyTorch, FSDP, Data Parallel, Sharding, Mixed Precision, CPU Offloading, FSDP2, Large-Scale Training]

---

# Pytorch-Fsdp 技能

基于官方文档生成的、针对 pytorch-fsdp 开发的全面辅助功能。

## 何时使用此技能

在以下情况下可触发此技能：
- 处理 pytorch-fsdp 相关问题
- 查询 pytorch-fsdp 的功能或 API 信息
- 实现 pytorch-fsdp 解决方案
- 调试 pytorch-fsdp 代码
- 学习 pytorch-fsdp 的最佳实践

## 快速参考

### 常见模式

**模式 1：通用连接上下文管理器**  
# 创建时间：2025年6月6日 | 最后更新时间：2025年6月6日  
该通用连接上下文管理器可用于处理输入规模不一致时的分布式训练。本页面介绍了相关类（Join、Joinable 和 JoinHook）的 API 信息。相关教程请参阅《使用连接上下文管理器实现不均衡输入的分布式训练》。  

```python
class torch.distributed.algorithms.Join(
    joinables, 
    enable=True, 
    throw_on_early_termination=False, 
    **kwargs
):
```
# 该类定义了通用连接上下文管理器，可在进程加入后调用自定义钩子函数。这些钩子函数需替代未加入进程的集合通信操作，以避免程序挂起或出现错误，并确保算法的正确性。有关钩子函数定义的详细信息，请参阅 JoinHook。  

**警告**：该上下文管理器要求每个参与的 Joinable 对象在其每次迭代前的集合通信之前调用 `notify_join_context()` 方法，以确保计算正确性。  

**警告**：该上下文管理器要求所有 JoinHook 对象中的 process_group 属性必须一致。如果存在多个 JoinHook 对象，则以第一个对象的设备作为默认值。进程组与设备信息会被用于检测未加入的进程；若启用了 `throw_on_early_termination`，还会通过全量归约操作通知相关进程抛出异常。  

**参数**：
- `joinables`（List[Joinable]）：参与连接的对象列表，其钩子函数将按给定顺序依次被调用。
- `enable`（bool）：用于检测输入是否不均衡的标志；设置为 `False` 会禁用该上下文管理器的功能，仅应在用户确定输入规模一致时使用（默认值为 `True`）。
- `throw_on_early_termination`（bool）：当检测到输入不均衡时是否抛出异常的标志（默认值为 `False`）。  

**示例**：
```python
>>> import os
>>> import torch
>>> import torch.distributed as dist
>>> import torch.multiprocessing as mp
>>> import torch.nn.parallel.DistributedDataParallel as DDP
>>> import torch.distributed.optim.ZeroRedundancyOptimizer as ZeRO
>>> from torch.distributed.algorithms.join import Join

>>> # 在每个子进程中
>>> def worker(rank):
>>>     dist.init_process_group("nccl", rank=rank, world_size=2)
>>>     model = DDP(torch.nn.Linear(1, 1).to(rank), device_ids=[rank])
>>>     optim = ZeRO(model.parameters(), torch.optim.Adam, lr=0.01)
>>>     # 第1个进程的输入数量比第0个多一个
>>>     inputs = [torch.tensor([1.]).to(rank) for _ in range(10 + rank)]
>>>     with Join([model, optim]):
>>>         for input in inputs:
>>>             loss = model(input).sum()
>>>             loss.backward()
>>>             optim.step()
>>> # 所有进程均可正常执行到此处，不会挂起或出错
```

```python
static notify_join_context(joinable):
```
# 该函数用于通知连接上下文管理器：调用该函数的进程尚未加入。如果启用了 `throw_on_early_termination`，则会检查是否检测到输入不均衡（即是否有进程已提前加入），若存在此类情况则抛出异常。此方法应在 Joinable 对象每次迭代前的集合通信之前调用。例如，在 DistributedDataParallel 的前向传播开始时即可调用此方法。只有传递给上下文管理器的第一个 Joinable 对象会执行该函数中的集合通信操作，其余对象则无需执行任何操作。  

**参数**：
- `joinable`（Joinable）：调用此方法的 Joinable 对象。  

**返回值**：
- 若 `joinable` 是第一个传递给上下文管理器的对象，则返回一个用于全量归约的异步任务句柄，用以通知上下文管理器该进程尚未加入；否则返回 `None`。  

```python
class torch.distributed.algorithms.Joinable:
```
# 该类定义了 Joinable 对象的抽象基类。继承自该类的 Joinable 对象除了需要实现返回设备信息的 `join_device()` 方法和返回进程组信息的 `join_process_group()` 方法外，还必须实现 `join_hook()` 方法，该方法需返回一个 JoinHook 实例。  

**抽象属性**：
- `join_device`：device  
  返回用于执行连接上下文管理器所需集合通信操作的设备。  

**抽象方法**：
- `join_hook(**kwargs)`  
  为指定的 Joinable 对象返回一个 JoinHook 实例。  
  **参数**：
  - `kwargs`（dict）：包含用于在运行时修改钩子函数行为的任意关键字参数；所有共享同一连接上下文管理器的 Joinable 实例将接收相同的 `kwargs` 值。  
  **返回类型**：JoinHook  
  **抽象属性**：
- `join_process_group`：Any  
  返回连接上下文管理器自身所需集合通信操作的进程组信息。  

```python
class torch.distributed.algorithms.JoinHook:
```
# 该类定义了连接钩子函数，为连接上下文管理器提供了两个执行入口。这两个入口分别为：主钩子函数——在存在未加入进程时会被反复调用；以及后钩子函数——在所有进程都加入后仅被调用一次。若要为通用连接上下文管理器实现自定义钩子函数，需定义一个继承自 JoinHook 的类，并根据需要重写 `main_hook()` 和 `post_hook()` 方法。  

**方法**：
- `main_hook()`  
  # 在存在未加入进程时调用此钩子函数，用于替代训练迭代中的集合通信操作。这里的“训练迭代”指的是一次前向传播、一次反向传播以及一次优化器更新步骤。  

- `post_hook(is_last_joiner)`  
  # 在所有进程都加入后调用此钩子函数。该方法会接收一个额外的布尔参数 `is_last_joiner`，用于指示当前进程是否属于最后加入的进程之一。  
  **参数**：
  - `is_last_joiner`（bool）：若当前进程是最后加入的进程之一，则值为 `True`；否则为 `False`。

```
Join
```

**模式 2：** 分布式通信包 - torch.distributed# 创建时间：2017年7月12日 | 最后更新时间：2025年9月4日 备注：如需了解与分布式训练相关的所有功能的简要介绍，请参阅 PyTorch 分布式训练概述。后端支持# torch.distributed 支持四种内置后端，每种后端具有不同的功能。下表列出了每种后端在 CPU 或 GPU 上可使用的功能。对于 NCCL，GPU 指 CUDA GPU；而对于 XCCL，则指 XPU GPU。只有当用于构建 PyTorch 的实现支持时，MPI 才能使用 CUDA。后端 gloo mpi nccl xccl 设备 CPU GPU CPU GPU CPU GPU CPU GPU 发送 ✓ ✘ ✓ ? ✘ ✓ ✘ ✓ 接收 ✓ ✘ ✓ ? ✘ ✓ ✘ ✓ 广播 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 全局归约 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 归约 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 全部收集 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 收集 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 分散 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 分散归约 ✓ ✓ ✘ ✘ ✘ ✓ ✘ ✓ 全部到全部 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 障碍 ✓ ✘ ✓ ? ✘ ✓ ✘ ✓ PyTorch 自带的后端# PyTorch distributed 包支持 Linux（稳定版）、MacOS（稳定版）以及 Windows（原型版）。在 Linux 环境下，默认已内置 Gloo 和 NCCL 后端（使用 CUDA 构建时才会包含 NCCL）。MPI 是一个可选后端，只有通过源代码构建 PyTorch 时才能启用（例如在已安装 MPI 的主机上构建 PyTorch）。备注：从 PyTorch v1.8 开始，Windows 支持所有集合通信后端，但 NCCL 除外。如果 init_process_group() 的 init_method 参数指向文件，则该文件必须遵循以下格式：本地文件系统，init_method="file:///d:/tmp/some_file" 共享文件系统，init_method="file://////{machine_name}/{share_folder_name}/some_file" 与 Linux 平台类似，您还可以通过设置环境变量 MASTER_ADDR 和 MASTER_PORT 来启用 TcpStore。应使用哪种后端？# 过去我们经常被问到：“我应该使用哪种后端？”经验法则：使用 NCCL 后端进行 CUDA GPU 的分布式训练；使用 XCCL 后端进行 XPU GPU 的分布式训练；使用 Gloo 后端进行 CPU 的分布式训练。具有 InfiniBand 互连的 GPU 主机：建议使用 NCCL，因为它是目前唯一同时支持 InfiniBand 和 GPUDirect 的后端。具有以太网互连的 GPU 主机：同样建议使用 NCCL，因为它在当前能提供最佳的分布式 GPU 训练性能，尤其适用于单节点或多节点的多进程分布式训练。如果遇到 NCCL 相关问题，可考虑将 Gloo 作为备用选项。（注意：目前 Gloo 在 GPU 上的运行速度慢于 NCCL。）具有 InfiniBand 互连的 CPU 主机：如果您的 InfiniBand 已启用 IP over IB，则使用 Gloo；否则请使用 MPI。我们计划在未来的版本中为 Gloo 添加对 InfiniBand 的支持。具有以太网互连的 CPU 主机：建议使用 Gloo，除非您有特殊理由需要使用 MPI。常用环境变量# 选择要使用的网络接口# 默认情况下，NCCL 和 Gloo 后端都会尝试自动查找合适的网络接口。如果自动检测到的接口不正确，您可以使用以下环境变量进行覆盖（适用于对应的后端）：NCCL_SOCKET_IFNAME，例如 export NCCL_SOCKET_IFNAME=eth0 GLOO_SOCKET_IFNAME，例如 export GLOO_SOCKET_IFNAME=eth0 如果您使用的是 Gloo 后端，可以通过逗号分隔指定多个接口，例如：export GLOO_SOCKET_IFNAME=eth0,eth1,eth2,eth3。后端会以轮询方式在这些接口之间分配操作。所有进程必须在此变量中指定相同数量的接口，这一点至关重要。其他 NCCL 环境变量# 调试——如果出现 NCCL 错误，您可以设置 NCCL_DEBUG=INFO，以便打印明确的警告信息以及基本的 NCCL 初始化信息。您还可以使用 NCCL_DEBUG_SUBSYS 来获取有关 NCCL 某一特定方面的更多详细信息。例如，设置 NCCL_DEBUG_SUBSYS=COLL 可以打印集合调用的日志，这在调试卡顿问题时非常有用，尤其是那些由集合类型或消息大小不匹配引起的卡顿。如果拓扑检测失败，设置 NCCL_DEBUG_SUBSYS=GRAPH 可以查看详细的检测结果，以便在需要 NCCL 团队进一步帮助时作为参考。性能调优——NCCL 会根据其拓扑检测结果自动进行调优，从而节省用户的调优工作量。在某些基于套接字的系统上，用户仍可以尝试调整 NCCL_SOCKET_NTHREADS 和 NCCL_NSOCKS_PERTHREAD 这两个环境变量，以提升套接字网络带宽。对于 AWS 或 GCP 等一些云服务提供商，NCCL 已经预先调优了这两个环境变量。如需查看完整的 NCCL 环境变量列表，请参阅 NVIDIA NCCL 的官方文档。您还可以通过 torch.distributed.ProcessGroupNCCL.NCCLConfig 和 torch.distributed.ProcessGroupNCCL.Options 对 NCCL 通信器进行进一步调优。可在解释器中使用 help（例如 help(torch.distributed.ProcessGroupNCCL.NCCLConfig)）来了解更多相关信息。基础知识# torch.distributed 包为运行在多台机器上的多个计算节点之间的多进程并行计算提供了 PyTorch 支持及通信原语。torch.nn.parallel.DistributedDataParallel() 类则基于这些功能，为任何 PyTorch 模型提供同步分布式训练功能。它与 torch.multiprocessing 和 torch.nn.DataParallel() 所提供的并行性有所不同，因为它支持多台网络连接的机器，且用户必须为每个进程单独启动一份主训练脚本。在单机同步场景下，torch.distributed 或 torch.nn.parallel.DistributedDataParallel() 包装器仍可能比其他数据并行方法（包括 torch.nn.DataParallel()）更具优势：每个进程都拥有自己的优化器，并在每次迭代中执行完整的优化步骤。虽然这看似有些多余，因为梯度早已在各个进程之间被收集并平均，因此所有进程的梯度都是相同的，但这意味着无需进行参数广播操作，从而减少了节点间传输张量所耗费的时间。此外，每个进程都包含独立的 Python 解释器，消除了由单个 Python 进程驱动多个执行线程、模型副本或 GPU 所带来的额外解释器开销及“GIL 冲突”问题。这对于那些大量使用 Python 运行时的模型尤为重要，尤其是那些包含循环层或众多小型组件的模型。初始化# 在调用其他方法之前，需要先使用 torch.distributed.init_process_group() 或 torch.distributed.device_mesh.init_device_mesh() 函数对该包进行初始化。这两个函数都会阻塞，直到所有进程都加入为止。警告：初始化操作不是线程安全的。进程组的创建应在单个线程中执行，以避免各进程之间的“UUID”分配不一致，以及避免在初始化过程中出现可能导致程序卡住的竞争条件。torch.distributed.is_available()[来源]# 如果分布式包可用，则返回 True；否则，torch.distributed 不会暴露任何其他 API。目前，torch.distributed 在 Linux、MacOS 和 Windows 上均可使用。在从源代码构建 PyTorch 时，可将 USE_DISTRIBUTED 设为 1 以启用该功能。目前，Linux 和 Windows 的默认值为 USE_DISTRIBUTED=1，而 MacOS 的默认值为 USE_DISTRIBUTED=0。返回类型：bool torch.distributed.init_process_group(backend=None, init_method=None, timeout=None, world_size=-1, rank=-1, store=None, group_name='', pg_options=None, device_id=None)[来源]# 初始化默认的分布式进程组。这也会同时初始化分布式包。初始化进程组主要有两种方式：明确指定存储位置、进程排名和总进程数；或者指定 init_method（一个 URL 字符串），该字符串指示如何/在何处发现其他节点。也可以选择性地指定进程排名和总进程数，或者将所有必需的参数编码到 URL 中并省略这些参数。如果两者均未指定，则默认认为 init_method 为 “env://”。参数 backend（str 或 Backend，可选）——要使用的后端。根据构建时的配置，有效值包括 mpi、gloo、nccl、ucc、xccl，或第三方插件注册的后端。从版本 2.6 开始，如果未指定 backend，则 c10d 会使用 device_id 参数（如果提供）所指示的设备类型对应的已注册后端。目前已知的默认注册关系为：cuda 对应 nccl，cpu 对应 gloo，xpu 对应 xccl。如果既未指定 backend 也未指定 device_id，则 c10d 会在运行时检测主机上的加速器，并使用该检测到的加速器（或 CPU）对应的已注册后端。此字段可以作为小写字符串给出（例如 “gloo”），也可以通过 Backend 属性访问（例如 Backend.GLOO）。如果使用 NCCL 后端且每台机器上运行多个进程，则每个进程必须对其使用的每个 GPU 拥有独占访问权，因为进程间共享 GPU 可能会导致死锁或 NCCL 使用错误。ucc 后端仍处于实验阶段。可通过 get_default_backend_for_device() 查询设备的默认后端。init_method（str，可选）——指定如何初始化进程组的 URL。如果未指定 init_method 或 store，则默认值为 “env://”。该参数与 store 互斥。world_size（int，可选）——参与任务的进程数量。如果指定了 store，则此参数为必填项。rank（int，可选）——当前进程的排名（应为 0 到 world_size-1 之间的数字）。如果指定了 store，则此参数为必填项。store（Store，可选）——所有工作进程均可访问的键值存储，用于交换连接/地址信息。该参数与 init_method 互斥。timeout（timedelta，可选）——针对进程组执行的操作的超时时间。NCCL 的默认超时时间为 10 分钟，其他后端的默认超时时间为 30 分钟。达到此超时时间后，集合操作将异步中止，进程也会崩溃。之所以如此处理，是因为 CUDA 执行是异步的，一旦出现失败的异步 NCCL 操作，后续的 CUDA 操作就可能在损坏的数据上执行，继续执行用户代码已不再安全。当设置 TORCH_NCCL_BLOCKING_WAIT 时，进程将会阻塞并等待超时时间结束。group_name（str，可选，已弃用）——组名称。此参数会被忽略。pg_options（ProcessGroupOptions，可选）——进程组选项，用于指定在构建特定进程组时需要传递的额外选项。截至目前，我们仅支持针对 nccl 后端的 ProcessGroupNCCL.Options 选项，其中可指定 is_high_priority_stream，以便在存在待处理的计算内核时让 nccl 后端优先处理高优先级的 CUDA 流。如需了解可用于配置 nccl 的其他选项，请参阅 https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-t。

device_id（torch.device | int，可选）——指定该进程将要使用的特定设备，从而实现针对不同后端的优化。目前该选项在 NCCL 环境下仅有两种作用：一是立即建立通信器（直接调用 ncclCommInit* 而非常规的延迟调用方式）；二是子组在可能的情况下会使用 ncclCommSplit，以避免创建组所带来的不必要的开销。若希望提前获取 NCCL 初始化错误信息，也可使用此字段。若传入整数，则 API 会假定在编译时所指定的加速器类型将被使用。

注意：若要启用 Backend.MPI 后端，需在支持 MPI 的系统上从源代码构建 PyTorch。另外，对多后端的支持仍处于实验阶段。当前若未指定后端，则会同时创建 gloo 和 nccl 两种后端：使用 gloo 后端处理包含 CPU 张量的集合操作，而使用 nccl 后端处理包含 CUDA 张量的集合操作。也可通过传入格式为“<设备类型>:<后端名称>,<设备类型>:<后端名称>”的字符串来指定自定义后端，例如“cpu:gloo,cuda:custom_backend”。

torch.distributed.device_mesh.init_device_mesh(device_type, mesh_shape, *, mesh_dim_names=None, backend_override=None)  
# 根据 device_type、mesh_shape 和 mesh_dim_names 参数初始化 DeviceMesh。这将创建一个具有 n 维数组布局的 DeviceMesh，其中 n 即为 mesh_shape 的长度。若提供了 mesh_dim_names，则每个维度会对应 mesh_dim_names[i] 所指定的名称。注意，init_device_mesh 遵循 SPMD 编程模型，即同一个 PyTorch Python 程序会在集群中的所有进程/节点上运行。需确保所有节点上的 mesh_shape（描述设备布局的 nD 数组的维度）完全一致，否则可能会导致程序挂起。注意：若未找到进程组，init_device_mesh 会后台自动初始化分布式通信所需的进程组。

参数：  
device_type（str）——网格的设备类型。目前支持“cpu”、“cuda/cuda-like”和“xpu”。不允许传入包含 GPU 索引的设备类型，如“cuda:0”。  
mesh_shape（Tuple[int]）——定义描述设备布局的多维数组各维度大小的元组。  
mesh_dim_names（Tuple[str]，可选）——用于为描述设备布局的多维数组的每个维度指定名称的元组，其长度必须与 mesh_shape 相同，且每个字符串都必须唯一。  
backend_override（Dict[int | str, tuple[str, Options] | str | Options]，可选）——用于覆盖为每个网格维度将要创建的部分或全部进程组的配置。每个键可以是维度的索引，也可以是其名称（若提供了 mesh_dim_names）。每个值可以是一个包含后端名称及其选项的元组，或者仅包含这两个组件中的一个（此时另一个组件将被设置为默认值）。

返回值：表示设备布局的 DeviceMesh 对象。  
返回类型：DeviceMesh  

示例：  
>>> from torch.distributed.device_mesh import init_device_mesh  
>>> mesh_1d = init_device_mesh("cuda", mesh_shape=(8,))  
>>> mesh_2d = init_device_mesh("cuda", mesh_shape=(2, 8), mesh_dim_names=("dp", "tp"))

torch.distributed.is_initialized()  
# 检查默认进程组是否已初始化。  
返回类型：bool  

torch.distributed.is_mpi_available()  
# 检查 MPI 后端是否可用。  
返回类型：bool  

torch.distributed.is_nccl_available()  
# 检查 NCCL 后端是否可用。  
返回类型：bool  

torch.distributed.is_gloo_available()  
# 检查 Gloo 后端是否可用。  
返回类型：bool  

torch.distributed.distributed_c10d.is_xccl_available()  
# 检查 XCCL 后端是否可用。  
返回类型：bool  

torch.distributed.is_torchelastic_launched()  
# 检查当前进程是否是通过 torch.distributed.elastic（即 torchelastic）启动的。该方法通过 TORCHELASTIC_RUN_ID 环境变量的存在来判定当前进程是否由 torchelastic 启动，这一变量始终为非空值，可用于实现节点发现功能。  
返回类型：bool  

torch.distributed.get_default_backend_for_device(device)  
# 返回指定设备的默认后端。  
参数：  
device（Union[str, torch.device]）——需要获取默认后端的设备。  
返回值：指定设备的默认后端，以小写字符串形式返回。  
返回类型：str  

目前支持三种初始化方式：  

TCP 初始化  
# 使用 TCP 进行初始化有两种方法，均要求所有进程都能访问某个网络地址，并且需指定 world_size 值。第一种方法需要指定属于 rank 0 进程的地址。此初始化方式要求所有进程都需手动指定自己的 rank 值。注意，在最新的分布式包中已不再支持多播地址，group_name 也已废弃。  

示例：  
import torch.distributed as dist  
# 使用某台机器的地址  
dist.init_process_group(backend, init_method='tcp://10.1.1.20:23456', rank=args.rank, world_size=4)  

共享文件系统初始化  
# 另一种初始化方式是利用群组中所有机器都能访问的共享文件系统，同时还需指定 world_size 值。URL 应以 file:// 开头，并包含共享文件系统中某个现有目录下并不存在的文件路径。文件系统初始化会在该文件不存在时自动创建它，但不会删除该文件。因此，你有责任在下次使用相同路径/名称调用 init_process_group() 之前清理该文件。注意，在最新的分布式包中已不再支持自动分配 rank 值，group_name 也已废弃。  

警告：此方法假定文件系统支持使用 fcntl 进行锁定——大多数本地系统及 NFS 都支持该功能。  
警告：此方法会始终创建该文件，并会在程序结束时尽力清理并删除它。换言之，每次使用文件初始化方式时都需要一个全新的空文件才能确保初始化成功。如果再次使用上一次初始化所使用的文件（而该文件未被清理），就会出现异常行为，往往会导致死锁和故障。因此，尽管此方法会尽力清理文件，但如果自动删除失败，你仍有责任在训练结束时确保删除该文件，以避免下次再次使用同一个文件。如果你计划多次使用相同的文件名调用 init_process_group()，这一点尤为重要。换句话说，如果文件未被删除/清理，而你又对该文件再次调用 init_process_group()，则很可能会出现故障。经验法则是：每次调用 init_process_group() 时，都必须确保该文件不存在或为空。  

示例：  
import torch.distributed as dist  
# 必须始终指定 rank 值  
dist.init_process_group(backend, init_method='file:///mnt/nfs/sharedfile', world_size=4, rank=args.rank)  

环境变量初始化  
# 此方法会从环境变量中读取配置，从而允许用户完全自定义信息的获取方式。需要设置的变量包括：  
MASTER_PORT——必填；必须是 rank 0 所在机器上的空闲端口。  
MASTER_ADDR——必填（rank 0 除外）；rank 0 节点的地址。  
WORLD_SIZE——必填；可在此处设置，也可通过调用 init 函数来设置。  
RANK——必填；可在此处设置，也可通过调用 init 函数来设置。  
rank 0 所在的机器将用于建立所有连接。这是默认的初始化方式，因此无需指定 init_method（或可设置为 env://）。  

优化初始化时间  
TORCH_GLOO_LAZY_INIT——按需建立连接，而非构建完整的网格结构，这能显著缩短非 all2all 操作的初始化时间。  

初始化后  
# 在调用 torch.distributed.init_process_group() 之后，就可以使用以下函数。若要检查进程组是否已初始化，可使用 torch.distributed.is_initialized()。  

class torch.distributed.Backend(name)  
# 用于表示后端的类，类似枚举类型。可用后端包括：GLOO、NCCL、UCC、MPI、XCCL 以及其他已注册的后端。该类的值均为小写字符串，例如“gloo”，可通过属性形式访问，如 Backend.NCCL。也可直接调用该类来解析字符串，例如 Backend(backend_str) 会检查 backend_str 是否有效，若有效则返回解析后的小写字符串。该类也支持大写字符串，例如 Backend("GLOO") 会返回“gloo”。注意：虽然存在 Backend.UNDEFINED 这一项，但它仅用作某些字段的初始值，用户既不应直接使用它，也不应假定其存在。  

classmethod register_backend(name, func, extended_api=False, devices=None)  
# 使用给定的名称和实例化函数注册新的后端。此类方法被第三方 ProcessGroup 扩展用于注册新后端。  

参数：  
name（str）——ProcessGroup 扩展的后端名称，必须与 init_process_group() 中的名称一致。  
func（function）——用于实例化后端的函数处理程序，该函数需在后台扩展中实现，且需接受四个参数：store、rank、world_size 和 timeout。  
extended_api（bool，可选）——该后端是否支持扩展参数结构，默认值为 False。若设置为 True，则该后端将获得一个 c10d::DistributedBackendOptions 的实例，以及由后台实现定义的进程组选项对象。  
devices（str 或 str 列表，可选）——该后端支持的设备类型，例如“cpu”、“cuda”等。若为 None，则默认同时支持“cpu”和“cuda”。  

注意：对第三方后端的支持仍处于实验阶段，可能会发生变化。  

torch.distributed.get_backend(group=None)  
# 返回指定进程组对应的后端。  

参数：  
group（ProcessGroup，可选）——要查询的进程组，默认为主进程组。若指定了其他特定进程组，则调用该函数的进程必须属于该进程组。  

返回值：指定进程组的后端，以小写字符串形式返回。返回类型：`Backend torch.distributed.get_rank(group=None)[source]`  
# 返回当前进程在指定进程组中的排名，若未指定则使用默认值。排名是分配给分布式进程组中每个进程的唯一标识符，其值为从0到`world_size`的连续整数。  
参数：  
`group`（`ProcessGroup`，可选）——要操作的进程组。如果为`None`，则使用默认进程组。  
返回值：  
进程组的排名；若当前进程不属于该组，则返回`-1`。  

返回类型：`int torch.distributed.get_world_size(group=None)[source]`  
# 返回当前进程组中的进程数量。  
参数：  
`group`（`ProcessGroup`，可选）——要操作的进程组。如果为`None`，则使用默认进程组。  
返回值：  
进程组的总规模；若当前进程不属于该组，则返回`-1`。  

关闭操作  
# 在程序退出时，务必通过调用`destroy_process_group()`来释放资源。最简单的做法是在训练脚本中不再需要进程间通信时（通常在`main()`函数接近结尾处），使用默认参数`group=None`调用`destroy_process_group()`来销毁所有进程组及后端。该操作应在每个训练进程上执行一次，而非在最外层的进程启动层执行。  
如果某个进程组内的所有进程未能在超时时间内调用`destroy_process_group()`，尤其是在应用程序中存在多个进程组（如用于N维并行计算）的情况下，程序退出时可能会出现挂起现象。这是因为`ProcessGroupNCCL`的销毁函数会调用`ncclCommAbort`，而该调用必须由所有进程共同执行；但由于Python垃圾回收机制的不确定性，`ProcessGroupNCCL`的销毁函数调用顺序可能无法保证一致。调用`destroy_process_group()`可以确保所有进程以统一顺序调用`ncclCommAbort`，同时避免在`ProcessGroupNCCL`的销毁函数执行期间调用该函数，从而避免挂起问题。  

重新初始化  
# `destroy_process_group()`也可用于销毁单个进程组。一个应用场景是容错训练，即在运行过程中可能需要销毁某个进程组并重新创建新的进程组。在这种情况下，必须在调用`destroy`之后、后续重新初始化之前，通过其他方式（而非`torch.distributed`原语）对所有训练进程进行同步。由于实现此类同步较为困难，目前该功能尚不支持且未经测试，被视为已知问题。如果此需求正在阻碍你的工作，请在GitHub上提交问题或提案。  

进程组  
# 默认情况下，集合操作是在默认进程组（也称为“全局进程组”）上进行的，要求所有进程都进入分布式函数调用。不过，某些工作负载可能需要更细粒度的通信，这时就需要使用分布式进程组。可通过`new_group()`函数创建新的进程组，这些新组可由所有进程中的任意子集构成。该函数会返回一个不可见的进程组句柄，可将其作为参数传递给所有集合操作函数（集合操作函数是用于在特定编程模式中交换信息的分布式函数）。  
函数原型：  
`torch.distributed.new_group(ranks=None, timeout=None, backend=None, pg_options=None, use_local_synchronization=False, group_desc=None, device_id=None)[source]`  
# 创建一个新的分布式进程组。该函数要求主进程组中的所有进程（即属于该分布式任务的所有进程）都进入此函数，即便它们后续不会成为该进程组的成员。此外，所有进程创建进程组的顺序也必须保持一致。  
警告：安全并发使用  
当使用NCCL后端并同时启用多个进程组时，用户必须确保所有进程对集合操作的执行顺序在全局范围内保持一致。如果一个进程内的多个线程同时发起集合操作，则需要通过显式同步来保证执行顺序的一致性。  
当使用`torch.distributed`通信 API的异步版本时，函数会返回一个工作对象，通信内核会被放入独立的CUDA流中处理，从而实现通信与计算的并行执行。一旦在一个进程组上启动了一个或多个异步操作，在使用另一个进程组之前，必须通过调用`work.wait()`来与其他CUDA流进行同步。更多详情请参阅《同时使用多个NCCL通信器》<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html#using-multiple-nccl-communicators-concurrently>。  
参数：  
`ranks`（`list[int]`）——进程组成员的排名列表。如果为`None`，则默认使用所有进程的排名。默认值为`None`。  
`timeout`（`timedelta`，可选）——详情及默认值请参见`init_process_group`函数。  
`backend`（`str`或`Backend`，可选）——要使用的后端。根据构建时的配置，有效值为`gloo`和`nccl`。默认使用与全局进程组相同的后端。该参数应作为小写字符串传递（例如“gloo”），也可通过`Backend`属性访问（例如`Backend.GLOO`）。如果未指定该参数，则使用默认进程组对应的后端。默认值为`None`。  
`pg_options`（`ProcessGroupOptions`，可选）——进程组选项，用于指定在构建特定进程组时需要传递的额外参数。例如对于NCCL后端，可指定`is_high_priority_stream`，以便进程组能够使用高优先级的CUDA流。关于配置NCCL的其他可用选项，请参阅https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-tuse_local_synchronization  
`use_local_synchronization`（`bool`，可选）：在进程组创建完成后执行组内屏障操作。不同之处在于，非成员进程无需调用该API，也不会参与屏障操作。  
`group_desc`（`str`，可选）——用于描述进程组的字符串。  
`device_id`（`torch.device`，可选）——指定要绑定当前进程的特定设备。如果提供了此参数，`new_group`函数会立即为该设备初始化通信后端。  
返回值：  
分布式进程组的句柄，可将其传递给集合操作函数；如果当前进程的排名不在`ranks`列表中，则返回`GroupMember.NON_GROUP_MEMBER`。注意：`use_local_synchronization`在MPI环境下不可用。注意：虽然当集群规模较大且进程组规模较小时，设置`use_local_synchronization=True`可显著提升性能，但需谨慎使用，因为它会改变集群的行为——非成员进程不会参与组屏障操作。注意：如果每个进程都创建多个重叠的进程组，设置`use_local_synchronization=True`可能会导致死锁。为避免此问题，需确保所有进程遵循相同的全局创建顺序。  

进程排名转换  
`torch.distributed.get_group_rank(group, global_rank)[source]`  
# 将全局排名转换为进程组排名。`global_rank`必须属于`group`，否则会引发`RuntimeError`异常。  
参数：  
`group`（`ProcessGroup`）——用于查找相对排名的进程组。  
`global_rank`（`int`）——要查询的全局排名。  
返回值：  
`global_rank`相对于`group`的进程组排名。  
返回类型：`int`  
注意：在默认进程组上调用此函数会返回自身值。  

`torch.distributed.get_global_rank(group, group_rank)[source]`  
# 将进程组排名转换为全局排名。`group_rank`必须属于`group`，否则会引发`RuntimeError`异常。  
参数：  
`group`（`ProcessGroup`）——用于查找对应全局排名的进程组。  
`group_rank`（`int`）——要查询的进程组排名。  
返回值：  
`group_rank`相对于`group`的全局排名。  
返回类型：`int`  
注意：在默认进程组上调用此函数会返回自身值。  

获取进程组中的所有排名  
`torch.distributed.get_process_group_ranks(group)[source]`  
# 获取与指定进程组相关的所有排名。  
参数：  
`group`（`Optional[ProcessGroup]`）——要获取其所有排名的进程组。如果为`None`，则使用默认进程组。  
返回值：  
按进程组排名排序的全局排名列表。  
返回类型：`list[int]`  

DeviceMesh  
# DeviceMesh是一种更高级的抽象层，用于管理进程组（或NCCL通信器）。它允许用户轻松创建节点间及节点内的进程组，而无需担心如何为不同的子进程组正确设置排名，同时也有助于更好地管理这些分布式进程组。可通过`init_device_mesh()`函数创建新的DeviceMesh，该函数需要一个描述设备拓扑结构的网格形状参数。  
类定义：  
`class torch.distributed.device_mesh.DeviceMesh(device_type, mesh, *, mesh_dim_names=None, backend_override=None, _init_backend=True)[source]`  
# DeviceMesh表示一个设备网格，设备的布局可以用n维数组表示，该数组的每个值都是默认进程组排名的全局ID。DeviceMesh可用于在集群中建立N维设备连接，并管理N维并行计算所需的进程组。通信可以在DeviceMesh的每个维度上独立进行。DeviceMesh会尊重用户已选择的设备（即如果用户在初始化DeviceMesh之前调用了`torch.cuda.set_device`），如果用户未提前指定设备，它也会为当前进程选择/设置设备。请注意，手动选择设备必须在初始化DeviceMesh之前完成。当与DTensor API一起使用时，DeviceMesh也可作为上下文管理器使用。需注意，DeviceMesh遵循SPMD编程模型，这意味着集群中的所有进程/排名都在运行相同的PyTorch Python程序。因此，用户必须确保描述设备布局的网格数组在所有进程中保持一致。如果网格不一致，可能会导致程序无声挂起。  
参数：  
`device_type`（`str`）——网格的设备类型。目前支持“cpu”和“cuda/cuda-like”。  
`mesh`（`ndarray`）——描述设备布局的多维数组或整数张量，其中的值均为默认进程组排名的全局ID。  
返回值：  
表示设备布局的DeviceMesh对象。  
返回类型：`DeviceMesh`  

以下程序以SPMD方式在每个进程/排名上运行。在此示例中，有2台主机，每台主机上有4块GPU。对网格的第一维度进行归约操作时，会在列（0, 4）……（3, 7）之间进行；对网格的第二维度进行归约操作时，则会在行（0, 1, 2, 3）和（4, 5, 6, 7）之间进行。  
示例：  
```python
>>> from torch.distributed.device_mesh import DeviceMesh
>>> >>> # 初始化设备网格为(2, 4)，表示跨主机（维度0）和主机内部（维度1）的拓扑结构
>>> mesh = DeviceMesh(device_type="cuda", mesh=[[0, 1, 2, 3], [4, 5, 6, 7]])
```  

从现有进程组构建DeviceMesh  
`static from_group(group, device_type, mesh=None, *, mesh_dim_names=None)[source]`  
# 根据现有的一个或多个ProcessGroup，使用指定的`device_type`构建一个DeviceMesh。所创建的DeviceMesh的维度数等于传入的进程组数量。例如，如果只传入一个进程组，则生成的DeviceMesh为1D网格。如果传入2个进程组列表，则生成的DeviceMesh为二维网格结构。若传入的进程组数量超过2个，则必须同时指定mesh和mesh_dim_names参数。进程组的输入顺序决定了网格的拓扑结构——例如，第一个进程组将对应DeviceMesh的第0维。传入的网格张量维度数必须与进程组数量一致，且各维的顺序也需与进程组顺序相符。

**参数**
- group（ProcessGroup或list[ProcessGroup]）：现有的进程组或进程组列表。
- device_type（str）：网格的设备类型，目前支持“cpu”和“cuda/cuda-like”。不允许传入包含GPU索引的设备类型，如“cuda:0”。
- mesh（torch.Tensor或ArrayLike，可选）：描述设备布局的多维数组或整数张量，其中的ID为默认进程组的全局ID。默认值为None。
- mesh_dim_names（tuple[str]，可选）：用于为描述设备布局的多维数组的各维度指定名称的元组，其长度必须与mesh_shape相同，且每个名称都必须唯一。默认值为None。

**返回值**
- DeviceMesh对象：表示设备布局。
- get_all_groups()：返回所有网格维度的ProcessGroup列表，返回类型为list[torch.distributed.distributed_c10d.ProcessGroup]。
- get_coordinate()：返回当前节点相对于网格各维度的相对索引；若当前节点不属于该网格，则返回None，返回类型为Optional[list[int]]。
- get_group(mesh_dim=None)：返回由mesh_dim指定的单个ProcessGroup；若未指定mesh_dim且DeviceMesh为一维结构，则返回网格中唯一的ProcessGroup。
- get_local_rank(mesh_dim=None)：返回DeviceMesh中指定mesh_dim的本地排名，返回类型为int。

以下程序以SPMD方式在每个进程/节点上运行。示例中包含2台主机，每台主机配备4个GPU：在排名0、1、2、3的节点上调用mesh_2d.get_local_rank(mesh_dim=0)将返回0；在排名4、5、6、7的节点上调用则返回1。在排名0、4的节点上调用mesh_2d.get_local_rank(mesh_dim=1)将返回0；在排名1、5的节点上返回1；在排名2、6的节点上返回2；在排名3、7的节点上返回3。

**示例：**
```python
>>> from torch.distributed.device_mesh import DeviceMesh
>>> mesh = DeviceMesh(device_type="cuda", mesh=[[0, 1, 2, 3], [4, 5, 6, 7]])
```

**get_rank()**：返回当前的全球排名，返回类型为int。

### 点对点通信
- **torch.distributed.send(tensor, dst=None, group=None, tag=0, group_dst=None)**：同步发送张量。警告：NCCL后端不支持tag参数。
  - 参数：
    - tensor：要发送的张量。
    - dst：全局进程组中的目标排名（忽略group参数），且不能与当前进程的排名相同。
    - group：要操作的进程组，若为None则使用默认进程组。
    - tag：用于与远程接收端的匹配标签。
    - group_dst：组内的目标排名。同时指定dst和group_dst是无效的。

- **torch.distributed.recv(tensor, src=None, group=None, tag=0, group_src=None)**：同步接收张量。警告：NCCL后端不支持tag参数。
  - 参数：
    - tensor：用于存储接收数据的张量。
    - src：全局进程组中的源排名（忽略group参数），若未指定则可从任意进程接收数据。
    - group：要操作的进程组，若为None则使用默认进程组。
    - tag：用于与远程发送端的匹配标签。
    - group_src：组内的源排名。同时指定src和group_src是无效的。
  - 返回值：发送方排名；若当前节点不属于该组则返回-1，返回类型为int。

**isend()**和**irecv()**在调用时会返回分布式请求对象。通常不应手动创建此类对象，但它们必定支持两个方法：
- is_completed()：操作完成后返回True。
- wait()：使进程阻塞直至操作完成。一旦该方法返回，is_completed()必定返回True。

- **torch.distributed.isend(tensor, dst=None, group=None, tag=0, group_dst=None)**：异步发送张量。警告：在请求完成前修改张量会导致行为未定义；NCCL后端不支持tag参数。与同步的send不同，isend允许src等于dst（即向自身发送）。
  - 参数：
    - tensor：要发送的张量。
    - dst：全局进程组中的目标排名（忽略group参数）。
    - group：要操作的进程组，若为None则使用默认进程组。
    - tag：用于与远程接收端的匹配标签。
    - group_dst：组内的目标排名。同时指定dst和group_dst是无效的。
  - 返回值：分布式请求对象；若当前节点不属于该组则返回None，返回类型为Optional[Work]。

- **torch.distributed.irecv(tensor, src=None, group=None, tag=0, group_src=None)**：异步接收张量。警告：NCCL后端不支持tag参数。与同步的recv不同，irecv允许src等于dst（即从自身接收）。
  - 参数：
    - tensor：用于存储接收数据的张量。
    - src：全局进程组中的源排名（忽略group参数），若未指定则可从任意进程接收数据。
    - group：要操作的进程组，若为None则使用默认进程组。
    - tag：用于与远程发送端的匹配标签。
    - group_src：组内的源排名。同时指定src和group_src是无效的。
  - 返回值：分布式请求对象；若当前节点不属于该组则返回None，返回类型为Optional[Work]。

- **torch.distributed.send_object_list(object_list, dst=None, group=None, device=None, group_dst=None, use_batch=False)**：同步发送object_list中的可序列化对象。与send()类似，但可传入Python对象。注意，object_list中的所有对象都必须可序列化才能被发送。
  - 参数：
    - object_list：要发送的输入对象列表，每个对象都必须可序列化。接收方需提供大小相同的对应列表。
    - dst：目标排名，基于全局进程组（忽略group参数）。
    - group：要操作的进程组，若为None则使用默认进程组，默认值为None。
    - device：若非None，则对象会被序列化为张量并转移到指定设备后再发送，默认值为None。
    - group_dst：组内的目标排名。必须仅指定dst或group_dst之一，不能同时指定。
    - use_batch：若为True，则使用批量点对点操作而非常规发送操作，这样可以避免初始化双节点通信器，直接使用整个组的通信器。具体用法和前提条件请参见batch_isend_irecv，默认值为False。
  - 返回值：None。

**注意**：对于基于NCCL的进程组，对象的内部张量表示必须在通信开始前转移到GPU设备上。此时使用的设备由torch.cuda.current_device()指定，用户有责任通过torch.cuda.set_device()确保每个节点都有独立的GPU。

**警告**：对象集合操作存在严重的性能和可扩展性限制，详情请参见“对象集合操作”相关内容。send_object_list()会隐式使用pickle模块，而该模块存在安全风险——恶意构造的pickle数据在反序列化时可能会执行任意代码。仅建议对可信数据使用此函数。另外，使用GPU张量调用send_object_list()支持不佳且效率低下，因为需要先将张量序列化为字节流再传输到CPU，建议改用send()函数。

**示例：**
```python
>>> import torch.distributed as dist
>>> device = torch.device("cpu")
>>> if dist.get_rank() == 0:
>>>     objects = ["foo", 12, {1: 2}]  # 任意可序列化对象
>>>     dist.send_object_list(objects, dst=1, device=device)
>>> else:
>>>     objects = [None, None, None]
>>>     dist.recv_object_list(objects, src=0, device=device)
>>> objects  # 输出：['foo', 12, {1: 2}]
```

- **torch.distributed.recv_object_list(object_list, src=None, group=None, device=None, group_src=None, use_batch=False)**：同步接收object_list中的可序列化对象。与recv()类似，但可接收Python对象。
  - 参数：
    - object_list：要接收到的对象列表，接收方需提供大小相同的对应列表。
    - src：接收object_list的源排名，基于全局进程组（忽略group参数），若设为None则可从任意节点接收数据，默认值为None。
    - group：要操作的进程组，若为None则使用默认进程组，默认值为None。
    - device：若非None，则在此设备上接收数据，默认值为None。
    - group_src：组内的源排名。同时指定src和group_src是无效的。
    - use_batch：若为True，则使用批量点对点操作而非常规接收操作，具体用法和前提条件请参见batch_isend_irecv，默认值为False。
  - 返回值：发送方排名；若当前节点不属于该组则返回-1，若属于该组，则object_list中包含来自源节点的发送对象。**注意：对于基于 NCCL 的进程组，必须在通信开始之前将对象的内部张量表示移至 GPU 设备上。此时所使用的设备由 `torch.cuda.current_device()` 指定，用户有责任通过 `torch.cuda.set_device()` 确保每个节点都拥有独立的 GPU。**  
**警告：对象集合操作存在诸多严重的性能与可扩展性限制，详情请参阅“对象集合操作”部分。**  
**警告：`recv_object_list()` 会隐式使用 pickle 模块，而该模块存在安全风险——有人可能构造恶意 pickle 数据，在反序列化时执行任意代码。因此仅可使用可信的数据调用此函数。**  
**警告：使用 GPU 张量调用 `recv_object_list()` 的支持不佳且效率低下，因为需要先将张量序列化为 pickle 格式，从而引发 GPU 到 CPU 的数据传输。建议改用 `recv()` 函数。**  

**示例：**  
```python
>>> # 注意：此处省略了每个节点上的进程组初始化。
>>> import torch.distributed as dist
>>> # 假设后端不是 NCCL
>>> device = torch.device("cpu")
>>> if dist.get_rank() == 0:
>>>     # 假设世界大小为 2
>>>     objects = ["foo", 12, {1: 2}]  # 任何可 pickle 的对象
>>>     dist.send_object_list(objects, dst=1, device=device)
>>> else:
>>>     objects = [None, None, None]
>>>     dist.recv_object_list(objects, src=0, device=device)
>>> objects
['foo', 12, {1: 2}]
```

---

### `torch.distributed.batch_isend_irecv(p2p_op_list)`

**功能：** 异步发送或接收一批张量，并返回相应的请求列表。该方法会依次处理 `p2p_op_list` 中的每个操作，然后返回对应的请求对象。目前支持 NCCL、Gloo 和 UCC 后端。

**参数：**  
- `p2p_op_list`（`list[torch.distributed.distributed_c10d.P2POp]`）：点对点操作列表，每个操作的类型为 `torch.distributed.P2POp`。列表中 `isend/irecv` 的顺序很重要，必须与远程端的对应顺序一致。

**返回值：**  
一个由 `op_list` 中对应操作调用的分布式请求对象组成的列表，返回类型为 `list[torch.distributed.distributed_c10d.Work]`。

**示例：**  
```python
>>> send_tensor = torch.arange(2, dtype=torch.float32) + 2 * rank
>>> recv_tensor = torch.randn(2, dtype=torch.float32)
>>> send_op = dist.P2POp(dist.isend, send_tensor, (rank + 1) % world_size)
>>> recv_op = dist.P2POp(
...     dist.irecv, recv_tensor, (rank - 1 + world_size) % world_size
... )
>>> reqs = batch_isend_irecv([send_op, recv_op])
>>> for req in reqs:
>>>     req.wait()
>>> recv_tensor
tensor([2, 3])  # 号码为 0 的节点
tensor([0, 1])  # 号码为 1 的节点
```

**注意：**  
- 当此 API 与 NCCL 进程组后端一起使用时，用户必须通过 `torch.cuda.set_device()` 设置当前 GPU 设备，否则可能导致程序意外挂起。  
- 如果该 API 是传递给 `dist.P2POp` 的组中的第一个集合操作，则组内的所有节点都必须参与此次调用；否则行为未定义。  
- 若该 API 不是组中的第一个集合操作，则允许仅对部分节点执行批量点对点操作。

---

### `torch.distributed.P2POp(op, tensor, peer=None, group=None, tag=0, group_peer=None)`

**功能：** 用于构建 `batch_isend_irecv` 所需的点对点操作。该类负责定义点对点操作的类型、通信缓冲区、对端节点编号、进程组以及标签。此类实例会被传递给 `batch_isend_irecv` 以进行点对点通信。

**参数：**  
- `op`（可调用的函数）：用于向对端进程发送数据或从对端接收数据的函数，其类型为 `torch.distributed.isend` 或 `torch.distributed.irecv`。  
- `tensor`（张量）：要发送或接收的张量。  
- `peer`（整数，可选）：目标节点编号或源节点编号。  
- `group`（`ProcessGroup`，可选）：要操作的进程组；若为 `None`，则使用默认进程组。  
- `tag`（整数，可选）：用于匹配发送与接收的标签。  
- `group_peer`（整数，可选）：目标节点编号或源节点编号。

---

## 同步与异步集合操作

每个集合操作函数都支持以下两种操作模式，具体取决于传入的 `async_op` 标志设置：

### 1. 同步操作
- **默认模式**，当 `async_op` 设置为 `False` 时。函数返回时即表示集合操作已执行完成。  
- 对于 CUDA 操作，由于 CUDA 操作本身是异步的，因此无法保证 CUDA 操作已经完成。但对于 CPU 集合操作，后续使用该集合操作结果的函数调用将按预期工作；对于 CUDA 集合操作，若在同一个 CUDA 流上使用结果，同样会按预期工作。在不同流环境下运行时，用户需自行处理同步问题。关于 CUDA 语义（如流同步）的详细信息，请参阅“CUDA 语义”。下面的代码示例展示了 CPU 与 CUDA 操作在这些语义上的差异。

### 2. 异步操作
- 当 `async_op` 设置为 `True` 时。集合操作函数会返回一个分布式请求对象。通常无需手动创建该对象，且该对象必定支持以下两种方法：  
  - `is_completed()`：对于 CPU 集合操作，若操作已完成则返回 `True`；对于 CUDA 操作，若操作已成功放入 CUDA 流中且其输出可在默认流上直接使用而无需进一步同步，则返回 `True`。  
  - `wait()`：对于 CPU 集合操作，会阻塞当前进程直到操作完成；对于 CUDA 集合操作，会阻塞当前正在运行的 CUDA 流直到操作完成（但不会阻塞 CPU）。  
  - `get_future()`：返回 `torch._C.Future` 对象。该功能支持 NCCL，也支持 GLOO 和 MPI 的大多数操作，但对点对点操作不支持。**注意：** 随着未来函数（Futures）的逐步采用及 API 的合并，`get_future()` 调用可能会变得多余。

**示例：**  
以下代码展示了在使用分布式集合操作时 CUDA 操作的语义特点，同时也说明了在不同 CUDA 流上使用集合操作结果时需要显式进行同步的情况：

```python
# 该代码在每个节点上运行。
dist.init_process_group("nccl", rank=rank, world_size=2)
output = torch.tensor([rank]).cuda(rank)
s = torch.cuda.Stream()
handle = dist.all_reduce(output, async_op=True)
# wait() 确保操作已被放入队列，但不一定已经完成。
handle.wait()
# 在非默认流上使用结果。
with torch.cuda.stream(s):
    s.wait_stream(torch.cuda.default_stream())
output.add_(100)
if rank == 0:
    # 如果省略了显式的 wait_stream 调用，下面的输出值将是 1 或 101，
    # 具体取决于 all_reduce 是否在 add 操作完成后覆盖了原有值。
    print(output)
```

---

## 集合函数

### `torch.distributed.broadcast(tensor, src=None, group=None, async_op=False, group_src=None)`

**功能：** 将张量广播到整个进程组。参与集合操作的各个进程中的张量元素数量必须相同。

**参数：**  
- `tensor`（张量）：要发送的数据；若 `src` 指定的是当前节点的编号，则该张量为输入数据，否则用于存储接收到的数据。  
- `src`（整数）：全局进程组中的源节点编号（与 `group` 参数无关）。  
- `group`（`ProcessGroup`，可选）：要操作的进程组；若为 `None`，则使用默认进程组。  
- `async_op`（布尔值，可选）：指定该操作是否为异步操作。  
- `group_src`（整数）：组内的源节点编号。必须仅指定 `group_src` 或 `src` 中的一个，不能同时指定。

**返回值：**  
- 若 `async_op` 设置为 `True`，则返回异步工作句柄；否则返回 `None`。

---

### `torch.distributed.broadcast_object_list(object_list, src=None, group=None, device=None, group_src=None)`

**功能：** 将 `object_list` 中的可 pickle 对象广播到整个进程组。该函数与 `broadcast()` 类似，但允许传递 Python 对象。注意，只有所有对象都是可 pickle 的才能被广播。

**参数：**  
- `object_list`（`List[Any]`）：要广播的输入对象列表，每个对象都必须是可 pickle 的。仅源节点上的对象会被广播，但每个节点需提供长度相同的对象列表。  
- `src`（整数）：用于广播 `object_list` 的源节点编号，该编号基于全局进程组（与 `group` 参数无关）。  
- `group`（`ProcessGroup`，可选）：要操作的进程组；若为 `None`，则使用默认进程组，默认值为 `None`。  
- `device`（`torch.device`，可选）：若非 `None`，则会对对象进行序列化并转换为张量，随后将这些张量移动到指定设备后再进行广播，默认值为 `None`。  
- `group_src`（整数）：组内的源节点编号。必须仅指定 `group_src` 或 `src` 中的一个，不能同时指定。

**返回值：** `None`。如果当前节点属于该进程组，则 `object_list` 将包含来自源节点的广播对象。

**注意：**  
- 对于基于 NCCL 的进程组，必须在通信开始之前将对象的内部张量表示移至 GPU 设备上。此时所使用的设备由 `torch.cuda.current_device()` 指定，用户有责任通过 `torch.cuda.set_device()` 确保每个节点都拥有独立的 GPU。  
- **注意：** 该 API 与 `broadcast()` 集合操作略有不同，因为它不提供异步操作句柄，因此属于阻塞调用。  
- **警告：** 对象集合操作存在诸多严重的性能与可扩展性限制，详情请参阅“对象集合操作”部分。  
- **警告：** `broadcast_object_list()` 会隐式使用 pickle 模块，而该模块存在安全风险——有人可能构造恶意 pickle 数据，在反序列化时执行任意代码。因此仅可使用可信的数据调用此函数。  
- **警告：** 使用 GPU 张量调用 `broadcast_object_list()` 的支持不佳且效率低下，因为需要先将张量序列化为 pickle 格式，从而引发 GPU 到 CPU 的数据传输。建议改用 `broadcast()` 函数。

**示例：**  
```python
>>> # 注意：此处省略了每个节点上的进程组初始化。
>>> import torch.distributed as dist
>>> if dist.get_rank() == 0:
>>>     # 假设世界大小为 3
>>>     objects = ["foo", 12, {1: 2}]  # 任何可 pickle 的对象
>>> else:
>>>     objects = [None, None, None]
>>>     # 假设后端不是 NCCL
>>>     device = torch.device("cpu")
>>>     dist.broadcast_object_list(objects, src=0, device=device)
>>> objects
['foo', 12, {1: 2}]
```

---

### `torch.distributed.all_reduce(tensor, op=<RedOpType.SUM: 0>, group=None, async_op=False)`

**功能：** 在所有节点上对张量数据进行归约，使得所有节点最终都获得相同的结果。调用完成后，所有进程中的张量在位上将完全相同。该函数支持复杂张量。

**参数：**  
- `tensor`（张量）：集合操作的输入与输出，函数会直接在原张量上操作。  
- `op`（可选）：来自 `torch.distributed.ReduceOp` 枚举的值之一，用于指定逐元素归约的操作类型。  
- `group`（`ProcessGroup`，可选）：要操作的进程组。若未指定，则将使用默认的进程组。async_op（布尔值，可选）——该操作是否应为异步操作。如果将 async_op 设置为 True，则返回异步任务处理句柄；否则若不是异步操作或不属于当前进程组，则返回 None。示例：>>> # 下方所有的张量均为 torch.int64 类型。>>> # 我们有 2 个进程组、2 个节点。>>> device = torch.device(f"cuda:{rank}") >>> tensor = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank >>> tensor tensor([1, 2], device='cuda:0') # 节点 0 tensor([3, 4], device='cuda:1') # 节点 1 >>> dist.all_reduce(tensor, op=ReduceOp.SUM) >>> tensor tensor([4, 6], device='cuda:0') # 节点 0 tensor([4, 6], device='cuda:1') # 节点 1 >>> # 下方所有的张量均为 torch.cfloat 类型。>>> # 我们有 2 个进程组、2 个节点。>>> tensor = torch.tensor( ... [1 + 1j, 2 + 2j], dtype=torch.cfloat, device=device ... ) + 2 * rank * (1 + 1j) >>> tensor tensor([1.+1.j, 2.+2.j], device='cuda:0') # 节点 0 tensor([3.+3.j, 4.+4.j], device='cuda:1') # 节点 1 >>> dist.all_reduce(tensor, op=ReduceOp.SUM) >>> tensor tensor([4.+4.j, 6.+6.j], device='cuda:0') # 节点 0 tensor([4.+4.j, 6.+6.j], device='cuda:1') # 节点 1 torch.distributed.reduce(tensor, dst=None, op=<RedOpType.SUM: 0>, group=None, async_op=False, group_dst=None)[source]# 在所有机器上对张量数据进行归约操作。只有目标节点为 dst 的进程会接收到最终结果。参数：tensor（Tensor）——集合操作的输入与输出，该函数为就地操作。dst（整数）——全局进程组中的目标节点编号（与 group 参数无关）。op（可选）——torch.distributed.ReduceOp 枚举中的值之一，用于指定用于逐元素归约的操作类型。group（ProcessGroup，可选）——要操作的进程组。若未指定，则将使用默认的进程组。async_op（布尔值，可选）——该操作是否应为异步操作。group_dst（整数）——所在进程组中的目标节点编号。必须指定 group_dst 或 dst 中的一个，但不能同时指定两个。如果将 async_op 设置为 True，则返回异步任务处理句柄；否则若不是异步操作或不属于当前进程组，则返回 None。torch.distributed.all_gather(tensor_list, tensor, group=None, async_op=False)[source]# 从整个进程组中收集张量并放入列表中，支持复杂形状及大小不规则的张量。参数：tensor_list（list[Tensor]）——输出列表，其中应包含尺寸合适的张量以用于集合操作的输出，也支持大小不规则的张量。tensor（Tensor）——当前节点要广播的张量。group（ProcessGroup，可选）——要操作的进程组。若未指定，则将使用默认的进程组。async_op（布尔值，可选）——该操作是否应为异步操作。如果将 async_op 设置为 True，则返回异步任务处理句柄；否则若不是异步操作或不属于当前进程组，则返回 None。示例：>>> # 下方所有的张量均为 torch.int64 数据类型。>>> # 我们有 2 个进程组、2 个节点。>>> device = torch.device(f"cuda:{rank}") >>> tensor_list = [ ... torch.zeros(2, dtype=torch.int64, device=device) for _ in range(2) ... ] >>> tensor_list [tensor([0, 0], device='cuda:0'), tensor([0, 0], device='cuda:0')] # 节点 0 [tensor([0, 0], device='cuda:1'), tensor([0, 0], device='cuda:1')] # 节点 1 >>> tensor = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank >>> tensor tensor([1, 2], device='cuda:0') # 节点 0 tensor([3, 4], device='cuda:1') # 节点 1 >>> dist.all_gather(tensor_list, tensor) >>> tensor_list [tensor([1, 2], device='cuda:0'), tensor([3, 4], device='cuda:0')] # 节点 0 [tensor([1, 2], device='cuda:1'), tensor([3, 4], device='cuda:1')] # 节点 1 >>> # 下方所有的张量均为 torch.cfloat 数据类型。>>> # 我们有 2 个进程组、2 个节点。>>> tensor_list = [ ... torch.zeros(2, dtype=torch.cfloat, device=device) for _ in range(2) ... ] >>> tensor_list [tensor([0.+0.j, 0.+0.j], device='cuda:0'), tensor([0.+0.j, 0.+0.j], device='cuda:0')] # 节点 0 [tensor([0.+0.j, 0.+0.j], device='cuda:1'), tensor([0.+0.j, 0.+0.j], device='cuda:1')] # 节点 1 >>> tensor = torch.tensor( ... [1 + 1j, 2 + 2j], dtype=torch.cfloat, device=device ... ) + 2 * rank * (1 + 1j) >>> tensor tensor([1.+1.j, 2.+2.j], device='cuda:0') # 节点 0 tensor([3.+3.j, 4.+4.j], device='cuda:1') # 节点 1 >>> dist.all_gather(tensor_list, tensor) >>> tensor_list [tensor([1.+1.j, 2.+2.j], device='cuda:0'), tensor([3.+3.j, 4.+4.j], device='cuda:0')] # 节点 0 [tensor([1.+1.j, 2.+2.j], device='cuda:1'), tensor([3.+3.j, 4.+4.j], device='cuda:1')] # 节点 1 torch.distributed.all_gather_into_tensor(output_tensor, input_tensor, group=None, async_op=False)[source]# 从所有节点收集张量并将它们放入一个输出张量中。该函数要求每个节点上的所有张量尺寸相同。参数：output_tensor（Tensor）——用于存储来自所有节点的张量元素的输出张量，其尺寸必须符合以下形式之一：(i) 沿主维度将所有输入张量连接起来；关于“连接”的定义，请参见 torch.cat()；(ii) 沿主维度将所有输入张量堆叠起来；关于“堆叠”的定义，请参见 torch.stack()。下面的示例能更好地说明所支持的输出形式。input_tensor（Tensor）——当前节点要收集的张量。与 all_gather API 不同，该 API 中的所有输入张量在各个节点上的尺寸必须相同。group（ProcessGroup，可选）——要操作的进程组。若未指定，则将使用默认的进程组。async_op（布尔值，可选）——该操作是否应为异步操作。如果将 async_op 设置为 True，则返回异步任务处理句柄；否则若不是异步操作或不属于当前进程组，则返回 None。示例：>>> # 下方所有的张量均为 torch.int64 数据类型且位于 CUDA 设备上。>>> # 我们有 2 个节点。>>> device = torch.device(f"cuda:{rank}") >>> tensor_in = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank >>> tensor_in tensor([1, 2], device='cuda:0') # 节点 0 tensor([3, 4], device='cuda:1') # 节点 1 >>> # 以连接形式输出 >>> tensor_out = torch.zeros(world_size * 2, dtype=torch.int64, device=device) >>> dist.all_gather_into_tensor(tensor_out, tensor_in) >>> tensor_out tensor([1, 2, 3, 4], device='cuda:0') # 节点 0 tensor([1, 2, 3, 4], device='cuda:1') # 节点 1 >>> # 以堆叠形式输出 >>> tensor_out2 = torch.zeros(world_size, 2, dtype=torch.int64, device=device) >>> dist.all_gather_into_tensor(tensor_out2, tensor_in) >>> tensor_out2 tensor([[1, 2], [3, 4]], device='cuda:0') # 节点 0 tensor([[1, 2], [3, 4]], device='cuda:1') # 节点 1 torch.distributed.all_gather_object(object_list, obj, group=None)[source]# 从整个进程组中收集可序列化的对象并放入列表中。该功能与 all_gather() 类似，但可以传入 Python 对象。需要注意的是，只有可序列化的对象才能被收集。参数：object_list（list[Any]）——输出列表，其大小应与本次集合操作所涉及的进程组大小相同，并将包含收集到的结果。obj（Any）——当前节点要广播的可序列化 Python 对象。group（ProcessGroup，可选）——要操作的进程组。若未指定，则将使用默认的进程组，默认值为 None。返回值：None。如果调用节点属于该进程组，则集合操作的结果将被填充到输入的 object_list 中；如果调用节点不属于该进程组，则传入的 object_list 将保持不变。注意：该 API 与 all_gather() 集合操作略有不同，因为它不提供 async_op 句柄，因此属于阻塞式调用。注意：对于基于 NCCL 的进程组，在进行通信之前，对象的内部张量表示必须先被移动到 GPU 设备上。此时使用的设备由 torch.cuda.current_device() 指定，用户有责任通过 torch.cuda.set_device() 确保每个节点都拥有独立的 GPU。警告：对象集合操作存在诸多严重的性能和可扩展性限制，详情请参阅“对象集合操作”相关内容。警告：all_gather_object() 会隐式使用 pickle 模块，而该模块存在安全风险，因为有人可能构造出恶意 pickle 数据，在反序列化时执行任意代码。因此，请仅使用您信任的数据调用此函数。警告：使用 GPU 张量调用 all_gather_object() 的支持程度较低且效率低下，因为需要先将张量序列化再进行 GPU 到 CPU 的传输，建议您考虑使用 all_gather() 代替。示例：>>> # 注意：此处省略了每个节点上的进程组初始化步骤。>>> import torch.distributed as dist >>> # 假设 world_size 的值为 3。>>> gather_objects = ["foo", 12, {1: 2}] # 任何可序列化的对象 >>> output = [None for _ in gather_objects] >>> dist.all_gather_object(output, gather_objects[dist.get_rank()]) >>> output ['foo', 12, {1: 2}] torch.distributed.gather(tensor, gather_list=None, dst=None, group=None, async_op=False, group_dst=None)[source]# 在单个进程中收集一组张量。该函数要求每个节点上的所有张量尺寸相同。参数：tensor（Tensor）——输入张量。gather_list（list[Tensor]，可选）——用于收集数据的、尺寸相同的张量列表（默认值为 None，必须在目标节点上指定）。dst（整数，可选）——全局进程组中的目标节点编号（与 group 参数无关）。如果 dst 和 group_dst 都为 None，则默认为目标全局节点编号 0。group（ProcessGroup，可选）——要操作的进程组。若未指定，则将使用默认的进程组。async_op（布尔值，可选）——该操作是否应为异步操作。group_dst（整数，可选）——所在进程组中的目标节点编号。不能同时指定 dst 和 group_dst。如果将 async_op 设置为 True，则返回异步任务处理句柄；否则若不是异步操作或不属于当前进程组，则返回 None。注意：gather_list 中的所有张量尺寸必须相同。示例：>>> # 我们有 2 个进程组、2 个节点。>>> tensor_size = 2 >>> device = torch.device(f'cuda:{rank}') >>> tensor = torch.ones(tensor_size, device=device) + rank >>> if dist.get_rank() == 0: >>> gather_list = [torch.zeros_like(tensor, device=device) for i in range(2)] >>> else: >>> gather_list = None >>> dist.gather(tensor, gather_list, dst=0) >>> # 节点 0 会收到收集到的数据。>>> gather_list [tensor([1., 1.], device='cuda:0'), tensor([2., 2.], device='cuda:0')] # 节点 0 None # 节点 1 torch.distributed.gather_object(obj, object_gather_list=None, dst=None, group=None, group_dst=None)[source]# 从整个进程组中收集可序列化的对象并放入单个进程中。该功能与 gather() 类似，但可以传入 Python 对象。需要注意的是，只有可序列化的对象才能被收集。参数：obj（Any）——输入对象，必须是可以被序列化的。object_gather_list（list[Any]）——输出列表，在目标节点上，其大小应与本次集合操作所涉及的进程组大小相同，并将包含收集到的结果。在非 DST 排序等级上，该参数必须为 None（默认值即为 None）。  
dst（整数，可选）——全局进程组中的目标排序等级（与 group 参数无关）。若同时指定 dst 和 group_dst 为 None，则默认使用全局等级 0。  
group（可选[ProcessGroup]）——要操作的进程组。若为 None，则使用默认进程组。默认值为 None。  
group_dst（整数，可选）——所在进程组中的目标排序等级。同时指定 dst 和 group_dst 是无效的，函数将返回 None。在 dst 排序等级上，object_gather_list 将包含集合操作的输出结果。  

**注意**：此 API 与 gather collective 略有不同，因为它不提供 async_op 接口，因此属于阻塞调用。  
**注意**：对于基于 NCCL 的进程组，在进行通信之前，对象的内部张量表示必须先被移动到 GPU 设备上。此时使用的设备由 torch.cuda.current_device() 指定，用户有责任通过 torch.cuda.set_device() 确保每个排序等级都拥有独立的 GPU。  
**警告**：对象集合操作存在诸多严重的性能和可扩展性限制，详情请参阅“对象集合操作”相关内容。  
**警告**：gather_object() 隐式使用了 pickle 模块，而该模块存在安全风险——有人可能构造恶意的 pickle 数据，在反序列化时执行任意代码。仅建议使用可信的数据调用此函数。  
**警告**：使用 GPU 张量调用 gather_object() 的支持不佳且效率低下，因为需要先将张量序列化为字节流，从而导致 GPU 与 CPU 之间的数据传输。建议改用 gather() 函数。  

**示例**：  
```python
>>> # 注意：此处省略了每个排序等级上的进程组初始化代码。
>>> import torch.distributed as dist
>>> # 假设世界大小为 3。
>>> gather_objects = ["foo", 12, {1: 2}]  # 任何可序列化的对象
>>> output = [None for _ in gather_objects]
>>> dist.gather_object(
...     gather_objects[dist.get_rank()],
...     output if dist.get_rank() == 0 else None,
...     dst=0
... )
>>> # 在等级 0 上
>>> output  # 输出：['foo', 12, {1: 2}]
```

---

`torch.distributed.scatter(tensor, scatter_list=None, src=None, group=None, async_op=False, group_src=None)`  
【来源】# 将一组张量分散到进程组中的所有进程。每个进程将恰好收到一个张量，并将其数据存储在对应的张量参数中。支持复杂张量。  
**参数**：  
- tensor（Tensor）——输出张量。  
- scatter_list（list[Tensor]）——需要分散的张量列表（默认值为 None，必须在源排序等级上指定）。  
- src（整数）——全局进程组中的源排序等级（与 group 参数无关）。若同时指定 src 和 group_src 为 None，则默认使用全局等级 0。  
- group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认进程组。  
- async_op（布尔值，可选）——该操作是否应为异步操作。  
- group_src（整数，可选）——所在进程组中的源排序等级。同时指定 src 和 group_src 是无效的。  
**返回值**：若 async_op 设为 True，则返回异步任务句柄；否则若该排序等级不属于目标进程组，则返回 None。  

**注意**：scatter_list 中的所有张量必须具有相同的尺寸。  

**示例**：  
```python
>>> # 注意：此处省略了每个排序等级上的进程组初始化代码。
>>> import torch.distributed as dist
>>> tensor_size = 2
>>> device = torch.device(f'cuda:{rank}')
>>> output_tensor = torch.zeros(tensor_size, device=device)
>>> if dist.get_rank() == 0:
>>>     # 假设世界大小为 2。所有张量必须尺寸相同。
>>>     t_ones = torch.ones(tensor_size, device=device)
>>>     t_fives = torch.ones(tensor_size, device=device) * 5
>>>     scatter_list = [t_ones, t_fives]
>>> else:
>>>     scatter_list = None
>>> dist.scatter(output_tensor, scatter_list, src=0)
>>> # 等级 i 将收到 scatter_list[i]。
>>> output_tensor  # 等级 0：tensor([1., 1.], device='cuda:0')
>>>               # 等级 1：tensor([5., 5.], device='cuda:1')
```

---

`torch.distributed.scatter_object_list(scatter_object_output_list, scatter_object_input_list=None, src=None, group=None, group_src=None)`  
【来源】# 将 scatter_object_input_list 中的可序列化对象分散到整个进程组。该功能与 scatter() 类似，但允许传递 Python 对象。在每个排序等级上，分散后的对象将作为 scatter_object_output_list 的第一个元素存储。注意，只有可序列化的对象才能被分散。  
**参数**：  
- scatter_object_output_list（List[Any]）——非空列表，其第一个元素将存储分配给该排序等级的对象。  
- scatter_object_input_list（List[Any]，可选）——需要分散的输入对象列表。每个对象都必须可序列化。仅源排序等级上的对象会被分散，非源排序等级的该参数可为 None。  
- src（整数）——用于分散 scatter_object_input_list 的源排序等级。源排序等级基于全局进程组（与 group 参数无关）。若同时指定 src 和 group_src 为 None，则默认使用全局等级 0。  
- group（可选[ProcessGroup]）——要操作的进程组。若为 None，则使用默认进程组。默认值为 None。  
- group_src（整数，可选）——所在进程组中的源排序等级。同时指定 src 和 group_src 是无效的。  
**返回值**：若该排序等级属于目标进程组，则 scatter_object_output_list 的第一个元素将被设置为对应的分散对象；否则返回 None。  

**注意**：此 API 与 scatter collective 略有不同，因为它不提供 async_op 接口，因此属于阻塞调用。  
**注意**：scatter_object_list() 隐式使用了 pickle 模块，而该模块存在安全风险——有人可能构造恶意的 pickle 数据，在反序列化时执行任意代码。仅建议使用可信的数据调用此函数。  
**警告**：使用 GPU 张量调用 scatter_object_list() 的支持不佳且效率低下，因为需要先将张量序列化为字节流，从而导致 GPU 与 CPU 之间的数据传输。建议改用 scatter() 函数。  

**示例**：  
```python
>>> # 注意：此处省略了每个排序等级上的进程组初始化代码。
>>> import torch.distributed as dist
>>> if dist.get_rank() == 0:
>>>     # 假设世界大小为 3。
>>>     objects = ["foo", 12, {1: 2}]  # 任何可序列化的对象
>>> else:
>>>     # 非源排序等级上可以是任意列表，其元素不会被使用。
>>>     objects = [None, None, None]
>>> output_list = [None]
>>> dist.scatter_object_list(output_list, objects, src=0)
>>> # 等级 i 将收到 objects[i]。例如，在等级 2 上：
>>> output_list  # 输出：[{1: 2}]
```

---

`torch.distributed.reduce_scatter(output, input_list, op=<RedOpType.SUM: 0>, group=None, async_op=False)`  
【来源】# 先对一组张量进行元素级聚合，再将聚合后的结果分散到进程组中的所有进程。  
**参数**：  
- output（Tensor）——输出张量。  
- input_list（list[Tensor]）——需要先聚合再分散的张量列表。  
- op（可选）——torch.distributed.ReduceOp 枚举中的值之一，用于指定元素级聚合的操作类型。  
- group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认进程组。  
- async_op（布尔值，可选）——该操作是否应为异步操作。若 async_op 设为 True，则返回异步任务句柄；否则若该排序等级不属于目标进程组，则返回 None。  

---

`torch.distributed.reduce_scatter_tensor(output, input, op=<RedOpType.SUM: 0>, group=None, async_op=False)`  
【来源】# 先对一个张量进行元素级聚合，再将聚合后的结果分散到进程组中的所有排序等级。  
**参数**：  
- output（Tensor）——输出张量。所有排序等级上的该张量尺寸必须相同。  
- input（Tensor）——需要先聚合再分散的输入张量。其尺寸应为输出张量尺寸乘以世界大小。输入张量可以具有以下形状之一：(i) 沿主维度对多个输出张量进行连接，或 (ii) 沿主维度将多个输出张量堆叠。关于“连接”的定义，请参阅 torch.cat()；关于“堆叠”的定义，请参阅 torch.stack()。  
- group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认进程组。  
- async_op（布尔值，可选）——该操作是否应为异步操作。若 async_op 设为 True，则返回异步任务句柄；否则若该排序等级不属于目标进程组，则返回 None。  

**示例**：  
```python
>>> # 下方所有张量均为 torch.int64 数据类型，且位于 CUDA 设备上。
>>> # 假设有两个排序等级。
>>> device = torch.device(f"cuda:{rank}")
>>> tensor_out = torch.zeros(2, dtype=torch.int64, device=device)
>>> # 以连接形式给出的输入
>>> tensor_in = torch.arange(world_size * 2, dtype=torch.int64, device=device)
>>> tensor_in  # 等级 0：tensor([0, 1, 2, 3], device='cuda:0')
>>>               # 等级 1：tensor([0, 1, 2, 3], device='cuda:1')
>>> dist.reduce_scatter_tensor(tensor_out, tensor_in)
>>> tensor_out  # 等级 0：tensor([0, 2], device='cuda:0')
>>>               # 等级 1：tensor([4, 6], device='cuda:1')
>>> # 以堆叠形式给出的输入
>>> tensor_in = torch.reshape(tensor_in, (world_size, 2))
>>> tensor_in  # 等级 0：tensor([[0, 1], [2, 3]], device='cuda:0')
>>>               # 等级 1：tensor([[0, 1], [2, 3]], device='cuda:1')
>>> dist.reduce_scatter_tensor(tensor_out, tensor_in)
>>> tensor_out  # 等级 0：tensor([0, 2], device='cuda:0')
>>>               # 等级 1：tensor([4, 6], device='cuda:1')
```

---

`torch.distributed.all_to_all_single(output, input, output_split_sizes=None, input_split_sizes=None, group=None, async_op=False)`  
【来源】# 先将输入张量分割，再将分割后的列表分散到进程组中的所有进程。之后，从进程组中的所有进程收集这些张量，并将它们连接起来作为单个输出张量返回。支持复杂张量。  
**参数**：  
- output（Tensor）——聚合后的连接输出张量。  
- input（Tensor）——需要分散的输入张量。  
- output_split_sizes——（list[Int]，可选）：若指定，则为输出张量第 0 维的分割大小。若为 None 或空列表，则要求输出张量的第 0 维尺寸能被世界大小整除。  
- input_split_sizes——（list[Int]，可选）：若指定，则为输入张量第 0 维的分割大小。若为 None 或空列表，则要求输入张量的第 0 维尺寸能被世界大小整除。  
- group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认进程组。  
- async_op（布尔值，可选）——该操作是否应为异步操作。若 async_op 设为 True，则返回异步任务句柄；否则若该排序等级不属于目标进程组，则返回 None。  
**警告**：all_to_all_single 目前仍处于实验阶段，可能会发生变化。示例 >>> input = torch.arange(4) + rank * 4 >>> input tensor([0, 1, 2, 3]) # Rank 0 tensor([4, 5, 6, 7]) # Rank 1 tensor([8, 9, 10, 11]) # Rank 2 tensor([12, 13, 14, 15]) # Rank 3 >>> output = torch.empty([4], dtype=torch.int64) >>> dist.all_to_all_single(output, input) >>> output tensor([0, 4, 8, 12]) # Rank 0 tensor([1, 5, 9, 13]) # Rank 1 tensor([2, 6, 10, 14]) # Rank 2 tensor([3, 7, 11, 15]) # Rank 3 >>> # 实质上，该操作与以下代码类似： >>> scatter_list = list(input.chunk(world_size)) >>> gather_list = list(output.chunk(world_size)) >>> for i in range(world_size): >>> dist.scatter(gather_list[i], scatter_list if i == rank else [], src = i) >>> # 另一个数据分割不均匀的示例 >>> input tensor([0, 1, 2, 3, 4, 5]) # Rank 0 tensor([10, 11, 12, 13, 14, 15, 16, 17, 18]) # Rank 1 tensor([20, 21, 22, 23, 24]) # Rank 2 tensor([30, 31, 32, 33, 34, 35, 36]) # Rank 3 >>> input_splits [2, 2, 1, 1] # Rank 0 [3, 2, 2, 2] # Rank 1 [2, 1, 1, 1] # Rank 2 [2, 2, 2, 1] # Rank 3 >>> output_splits [2, 3, 2, 2] # Rank 0 [2, 2, 1, 2] # Rank 1 [1, 2, 1, 2] # Rank 2 [1, 2, 1, 1] # Rank 3 >>> output = ... >>> dist.all_to_all_single(output, input, output_splits, input_splits) >>> output tensor([ 0, 1, 10, 11, 12, 20, 21, 30, 31]) # Rank 0 tensor([ 2, 3, 13, 14, 22, 32, 33]) # Rank 1 tensor([ 4, 15, 16, 23, 34, 35]) # Rank 2 tensor([ 5, 17, 18, 24, 36]) # Rank 3 >>> # 另一个使用 torch.cfloat 类型张量的示例。 >>> input = torch.tensor( ... [1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j], dtype=torch.cfloat ... ) + 4 * rank * (1 + 1j) >>> input tensor([1+1j, 2+2j, 3+3j, 4+4j]) # Rank 0 tensor([5+5j, 6+6j, 7+7j, 8+8j]) # Rank 1 tensor([9+9j, 10+10j, 11+11j, 12+12j]) # Rank 2 tensor([13+13j, 14+14j, 15+15j, 16+16j]) # Rank 3 >>> output = torch.empty([4], dtype=torch.int64) >>> dist.all_to_all_single(output, input) >>> output tensor([1+1j, 5+5j, 9+9j, 13+13j]) # Rank 0 tensor([2+2j, 6+6j, 10+10j, 14+14j]) # Rank 1 tensor([3+3j, 7+7j, 11+11j, 15+15j]) # Rank 2 tensor([4+4j, 8+8j, 12+12j, 16+16j]) # Rank 3

torch.distributed.all_to_all(output_tensor_list, input_tensor_list, group=None, async_op=False)
[来源]# 将输入张量列表分散到组中的所有进程，并在输出列表中返回收集后的张量列表。支持复数型张量。参数：
output_tensor_list (list[Tensor]) – 每个等级需要收集的一个张量列表。
input_tensor_list (list[Tensor]) – 每个等级需要分散的一个张量列表。
group (ProcessGroup, 可选) – 要操作的进程组。若为 None，则使用默认进程组。
async_op (bool, 可选) – 是否将此操作设为异步操作。若设置为 True，则返回异步任务句柄；否则或不属于该组时返回 None。

警告：all_to_all 为实验性功能，可能会发生变化。

示例 >>> input = torch.arange(4) + rank * 4 >>> input = list(input.chunk(4)) >>> input [tensor([0]), tensor([1]), tensor([2]), tensor([3])] # Rank 0 [tensor([4]), tensor([5]), tensor([6]), tensor([7])] # Rank 1 [tensor([8]), tensor([9]), tensor([10]), tensor([11])] # Rank 2 [tensor([12]), tensor([13]), tensor([14]), tensor([15])] # Rank 3 >>> output = list(torch.empty([4], dtype=torch.int64).chunk(4)) >>> dist.all_to_all(output, input) >>> output [tensor([0]), tensor([4]), tensor([8]), tensor([12])] # Rank 0 [tensor([1]), tensor([5]), tensor([9]), tensor([13])] # Rank 1 [tensor([2]), tensor([6]), tensor([10]), tensor([14])] # Rank 2 [tensor([3]), tensor([7]), tensor([11]), tensor([15])] # Rank 3 >>> # 实质上，该操作与以下代码类似： >>> scatter_list = input >>> gather_list = output >>> for i in range(world_size): >>> dist.scatter(gather_list[i], scatter_list if i == rank else [], src=i) >>> input tensor([0, 1, 2, 3, 4, 5]) # Rank 0 tensor([10, 11, 12, 13, 14, 15, 16, 17, 18]) # Rank 1 tensor([20, 21, 22, 23, 24]) # Rank 2 tensor([30, 31, 32, 33, 34, 35, 36]) # Rank 3 >>> input_splits [2, 2, 1, 1] # Rank 0 [3, 2, 2, 2] # Rank 1 [2, 1, 1, 1] # Rank 2 [2, 2, 2, 1] # Rank 3 >>> output_splits [2, 3, 2, 2] # Rank 0 [2, 2, 1, 2] # Rank 1 [1, 2, 1, 2] # Rank 2 [1, 2, 1, 1] # Rank 3 >>> input = list(input.split(input_splits)) >>> input [tensor([0, 1]), tensor([2, 3]), tensor([4]), tensor([5])] # Rank 0 [tensor([10, 11, 12]), tensor([13, 14]), tensor([15, 16]), tensor([17, 18])] # Rank 1 [tensor([20, 21]), tensor([22]), tensor([23]), tensor([24])] # Rank 2 [tensor([30, 31]), tensor([32, 33]), tensor([34, 35]), tensor([36])] # Rank 3 >>> output = ... >>> dist.all_to_all(output, input) >>> output [tensor([0, 1]), tensor([10, 11, 12]), tensor([20, 21]), tensor([30, 31])] # Rank 0 [tensor([2, 3]), tensor([13, 14]), tensor([22]), tensor([32, 33])] # Rank 1 [tensor([4]), tensor([15, 16]), tensor([23]), tensor([34, 35])] # Rank 2 [tensor([5]), tensor([17, 18]), tensor([24]), tensor([36])] # Rank 3 >>> # 另一个使用 torch.cfloat 类型张量的示例。 >>> input = torch.tensor( ... [1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j], dtype=torch.cfloat ... ) + 4 * rank * (1 + 1j) >>> input = list(input.chunk(4)) >>> input [tensor([1+1j]), tensor([2+2j]), tensor([3+3j]), tensor([4+4j])] # Rank 0 [tensor([5+5j]), tensor([6+6j]), tensor([7+7j]), tensor([8+8j])] # Rank 1 [tensor([9+9j]), tensor([10+10j]), tensor([11+11j]), tensor([12+12j])] # Rank 2 [tensor([13+13j]), tensor([14+14j]), tensor([15+15j]), tensor([16+16j])] # Rank 3 >>> output = list(torch.empty([4], dtype=torch.int64).chunk(4)) >>> dist.all_to_all(output, input) >>> output [tensor([1+1j]), tensor([5+5j]), tensor([9+9j]), tensor([13+13j])] # Rank 0 [tensor([2+2j]), tensor([6+6j]), tensor([10+10j]), tensor([14+14j])] # Rank 1 [tensor([3+3j]), tensor([7+7j]), tensor([11+11j]), tensor([15+15j])] # Rank 2 [tensor([4+4j]), tensor([8+8j]), tensor([12+12j]), tensor([16+16j])] # Rank 3

torch.distributed.barrier(group=None, async_op=False, device_ids=None)
[来源]# 同步所有进程。若 async_op 为 False，或在对 wait() 调用异步任务句柄时，此集体操作会阻塞进程，直到整个组都进入该函数。

参数：
group (ProcessGroup, 可选) – 要操作的进程组。若为 None，则使用默认进程组。
async_op (bool, 可选) – 是否将此操作设为异步操作。
device_ids ([int], 可选) – 设备/GPU ID 列表。通常只需一个 ID。

返回值：若 async_op 设为 True，则返回异步任务句柄；否则或不属于该组时返回 None。

注意：ProcessGroupNCCL 会阻塞 CPU 线程，直到屏障集体操作完成。ProcessGroupNCCL 将屏障实现为对一个元素张量的 all_reduce 操作。必须为该张量选择设备。设备选择顺序如下：(1) 若 barrier 的 device_ids 参数非空，则优先使用其中的第一个设备；(2) 若 init_process_group 的参数非空，则使用该设备；(3) 若之前已执行过带有张量输入的其它集体操作，则使用首次使用的设备；(4) 使用全局等级对本地设备数量取模后的结果作为设备索引。

torch.distributed.monitored_barrier(group=None, timeout=None, wait_all_ranks=False)
[来源]# 与 torch.distributed.barrier 类似，可同步进程，但支持可配置的超时时间。它能报告在指定超时时间内未能通过该屏障的等级。具体而言，对于非零等级，会阻塞直到收到来自等级 0 的发送/接收操作；等级 0 则会阻塞直到处理完所有其他等级的发送/接收操作，并会为未能及时响应的等级报告失败。需要注意的是，如果有一个等级无法到达 monitored_barrier（例如因挂起），则所有其他等级在 monitored_barrier 中也会失败。此集体操作会阻塞组中的所有进程/等级，直到整个组成功退出该函数，因此适用于调试和同步。不过，它可能会影响性能，仅建议在调试或需要在主机端实现完全同步的场景中使用。出于调试目的，可在应用程序的集体操作之前插入此屏障，以检查是否有等级不同步。

注意：此集体操作仅支持 GLOO 后端。

参数：
group (ProcessGroup, 可选) – 要操作的进程组。若为 None，则使用默认进程组。
timeout (datetime.timedelta, 可选) – monitored_barrier 的超时时间。若为 None，则使用默认的超时时间。
wait_all_ranks (bool, 可选) – 是否收集所有失败的等级。默认值为 False，此时等级 0 的 monitored_barrier 会在遇到第一个失败等级时就抛出异常，以实现快速失败。若将 wait_all_ranks 设置为 True，则 monitored_barrier 会收集所有失败的等级，并抛出一个包含所有失败等级信息的错误。

返回值：None。

示例：
>>> # 注意：此处省略了每个等级的进程组初始化。 >>> import torch.distributed as dist >>> if dist.get_rank() != 1: >>> dist.monitored_barrier() # 会抛出异常，表明 >>> # 等级 1 未调用 monitored_barrier。 >>> # 设置 wait_all_ranks=True 的示例 >>> if dist.get_rank() == 0: >>> dist.monitored_barrier(wait_all_ranks=True) # 会抛出异常 >>> # 表明等级 1、2……world_size - 1 未调用 >>> # monitored_barrier。

class torch.distributed.Work
# Work 对象表示 PyTorch 分布式包中待处理的异步操作的句柄。它由非阻塞集体操作（如 dist.all_reduce(tensor, async_op=True)）返回。

block_current_stream(self: torch._C._distributed_c10d.Work) → None
# 阻塞当前正在运行的 GPU 流，以等待操作完成。对于基于 GPU 的集体操作，这相当于调用 synchronize。对于由 CPU 启动的集体操作（如使用 Gloo），这将阻塞 CUDA 流，直到操作完成。在所有情况下都会立即返回。要检查操作是否成功，应异步地检查 Work 对象的结果。

boxed(self: torch._C._distributed_c10d.Work) → object
exception(self: torch._C._distributed_c10d.Work) → std::__exception_ptr::exception_ptr
get_future(self: torch._C._distributed_c10d.Work) → torch.Future
# 返回与 Work 完成相关的 torch.futures.Future 对象。例如，可通过 fut = process_group.allreduce(tensors).get_future() 获取该未来对象。示例：以下是一个简单的 allreduce DDP 通信钩子的示例，该钩子使用 get_future API 来获取与 allreduce 操作完成相关的 Future 对象。  
>>> def allreduce(process_group: dist.ProcessGroup, bucket: dist.GradBucket): -> torch.futures.Future  
>>> group_to_use = process_group if process_group is not None else torch.distributed.group.WORLD  
>>> tensor = bucket.buffer().div_(group_to_use.size())  
>>> return torch.distributed.all_reduce(tensor, group=group_to_use, async_op=True).get_future()  
>>> ddp_model.register_comm_hook(state=None, hook=allreduce)  

警告：get_future API 支持 NCCL，以及部分 GLOO 和 MPI 后端（不支持如 send/recv 这样的点对点操作），并且会返回一个 torch.futures.Future 对象。在上面的示例中，allreduce 操作将在 GPU 上通过 NCCL 后端执行；fut.wait() 会在将相应的 NCCL 流与 PyTorch 当前设备流同步后返回结果，这样就能实现异步 CUDA 执行，而无需等待 GPU 上的整个操作完成。需要注意的是，CUDAFuture 不支持 TORCH_NCCL_BLOCKING_WAIT 标志或 NCCL 的 barrier() 函数。此外，如果通过 fut.then() 添加了回调函数，它将一直等待直到 WorkNCCL 的 NCCL 流与 ProcessGroupNCCL 的专用回调流同步，并在回调流上运行回调函数后直接调用该回调。fut.then() 会返回另一个 CUDAFuture 对象，其中包含回调函数的返回值以及记录回调流的 CUDAEvent 对象。对于 CPU 操作，当任务完成且 value() 张量已准备好时，fut.done() 会返回 true；而对于 GPU 操作，只有当操作已被放入队列时，fut.done() 才会返回 true。在混合 CPU-GPU 操作中（例如使用 GLOO 发送 GPU 张量），当张量到达相应节点后，fut.done() 会返回 true，但它们未必已在相应 GPU 上完成同步（这与 GPU 操作的情况类似）。  

get_future_result(self: torch._C._distributed_c10d.Work) → torch.Future  
# 返回一个类型为 int 的 torch.futures.Future 对象，该对象与 WorkResult 枚举类型相对应。例如，可以通过 fut = process_group.allreduce(tensor).get_future_result() 来获取该 Future 对象。  

示例：用户可以使用 fut.wait() 以阻塞方式等待任务完成，并通过 fut.value() 获取 WorkResult。此外，用户还可以使用 fut.then(call_back_func) 注册一个回调函数，在任务完成后自动调用，而不会阻塞当前线程。  

警告：get_future_result API 仅支持 NCCL。  

is_completed(self: torch._C._distributed_c10d.Work) → bool  
# 检查指定任务是否已完成。  

is_success(self: torch._C._distributed_c10d.Work) → bool  
# 检查指定任务的执行是否成功。  

result(self: torch._C._distributed_c10d.Work) → list[torch.Tensor]  
# 返回与指定任务相关的所有张量列表。  

source_rank(self: torch._C._distributed_c10d.Work) → int  
# 返回执行该任务的进程编号。  

synchronize(self: torch._C._distributed_c10d.Work) → None  
# 使当前流在 NCCL 任务完成时阻塞等待。  

static unbox(arg0: object) → torch._C._distributed_c10d.Work  
# 静态解包操作，用于将对象转换为对应的 Work 对象。  

wait(self: torch._C._distributed_c10d.Work, timeout: datetime.timedelta = datetime.timedelta(0)) → bool  
# 等待指定任务完成，可设置超时时间。返回 true 或 false。示例：  
try:  
    work.wait(timeout)  
except:  
    # 进行其他处理  

警告：在正常情况下，用户无需设置超时时间。调用 wait() 与调用 synchronize() 效果相同，都会使当前流在 NCCL 任务完成时阻塞。但如果设置了超时时间，它会阻塞 CPU 线程，直到 NCCL 任务完成或超时为止；如果超时，则会抛出异常。  

class torch.distributed.ReduceOp  
# 用于表示可用归约操作的枚举类，包括 SUM、PRODUCT、MIN、MAX、BAND、BOR、BXOR 和 PREMUL_SUM。使用 NCCL 后端时，BAND、BOR 和 BXOR 这三种归约操作是不可用的。AVG 会在对所有进程求和之前先将数值除以全局进程数；AVG 仅支持 NCCL 后端，且要求 NCCL 版本为 2.10 或更高。PREMUL_SUM 会在归约之前在本地将输入值与给定标量相乘；PREMUL_SUM 也仅支持 NCCL 后端，且要求 NCCL 版本为 2.11 或更高。建议用户使用 torch.distributed._make_nccl_premul_sum。另外，MAX、MIN 和 PRODUCT 操作不支持复杂张量。该类中的各个值可作为属性访问，例如 ReduceOp.SUM，它们被用于指定归约集合操作（如 reduce()）的策略。该类不支持 __members__ 属性。  

class torch.distributed.reduce_op  
# 一种已过时的归约操作枚举类，支持的操作包括 SUM、PRODUCT、MIN 和 MAX。建议使用 ReduceOp 代替。  

Distributed Key-Value Store  
# torch.distributed 包中包含一个分布式键值存储系统，可用于在进程组内的进程之间共享信息，也可用于在 torch.distributed.init_process_group() 中初始化该分布式系统（通过显式创建存储对象来替代指定 init_method）。该键值存储系统共有三种类型：TCPStore、FileStore 和 HashStore。  

class torch.distributed.Store  
# 所有存储实现类的基类，包括 PyTorch distributed 提供的三种存储类型：(TCPStore、FileStore 和 HashStore)。  
__init__(self: torch._C._distributed_c10d.Store) → None  
# 初始化存储对象。  

add(self: torch._C._distributed_c10d.Store, arg0: str, arg1: SupportsInt) → int  
# 为给定键在存储中创建一个计数器，初始值为 arg1 指定的数量。后续使用相同键的 add() 调用会将计数器值增加 arg1 指定的量。如果该键已被 set() 方法设置过，则调用 add() 会引发异常。  
参数：  
key (str) – 要为其增加计数的存储键。  
amount (int) – 计数器要增加的数值。  

示例：  
>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> # 以 TCPStore 为例，其他存储类型也可使用  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.add("first_key", 1)  
>>> store.add("first_key", 6)  
>>> # 应返回 7  
>>> store.get("first_key")  

append(self: torch._C._distributed_c10d.Store, arg0: str, arg1: str) → None  
# 根据指定的键和值将键值对追加到存储中。如果该键在存储中不存在，则会创建该键。  
参数：  
key (str) – 要追加到存储中的键。  
value (str) – 与键关联的值，将被添加到存储中。  

示例：  
>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.append("first_key", "po")  
>>> store.append("first_key", "tato")  
>>> # 应返回 "potato"  
>>> store.get("first_key")  

check(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str]) → bool  
# 检查存储中是否包含指定键列表对应的值。在正常情况下会立即返回结果，但在某些边缘情况下可能会出现死锁，例如在 TCPStore 被销毁后仍调用 check()。该函数接受一个键列表，用于查询这些键是否存储在存储中。  
参数：  
keys (list[str]) – 要查询是否存储在存储中的键列表。  

示例：  
>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> # 以 TCPStore 为例，其他存储类型也可使用  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.add("first_key", 1)  
>>> # 应返回 7  
>>> store.check(["first_key"])  

clone(self: torch._C._distributed_c10d.Store) → torch._C._distributed_c10d.Store  
# 克隆存储对象，返回一个指向同一底层存储的新对象。该新对象可以与原始对象同时使用，旨在为多线程安全地使用存储提供支持——即每个线程都拥有自己的存储副本。  

compare_set(self: torch._C._distributed_c10d.Store, arg0: str, arg1: str, arg2: str) → bytes  
# 根据指定的键将键值对插入存储中，并在插入前比较 expected_value 和 desired_value 的值。只有当该键在存储中已存在对应的 expected_value，或者 expected_value 为空字符串时，才会设置 desired_value。  
参数：  
key (str) – 要在存储中检查的键。  
expected_value (str) – 插入前要检查的键对应的值。  
desired_value (str) – 要添加到存储中的键对应的值。  

示例：  
>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.set("key", "first_value")  
>>> store.compare_set("key", "first_value", "second_value")  
>>> # 应返回 "second_value"  
>>> store.get("key")  

delete_key(self: torch._C._distributed_c10d.Store, arg0: str) → bool  
# 从存储中删除与指定键关联的键值对。如果删除成功则返回 true，否则返回 false。  
警告：delete_key API 仅支持 TCPStore 和 HashStore，使用该 API 于 FileStore 会引发异常。  
参数：  
key (str) – 要从存储中删除的键。  
返回值：如果键被删除则返回 True，否则返回 False。  

示例：  
>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> # 以 TCPStore 为例，HashStore 也可使用  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.set("first_key")  
>>> # 应返回 true  
>>> store.delete_key("first_key")  
>>> # 应返回 false  
>>> store.delete_key("bad_key")  

get(self: torch._C._distributed_c10d.Store, arg0: str) → bytes  
# 从存储中获取与指定键关联的值。如果该键不存在于存储中，函数会等待存储初始化时设定的超时时间，之后才会抛出异常。  
参数：  
key (str) – 函数将返回与该键关联的值。  
返回值：如果键存在于存储中，则返回该键对应的值。  

示例：  
>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.set("first_key", "first_value")  
>>> # 应返回 "first_value"  
>>> store.get("first_key")  

has_extended_api(self: torch._C._distributed_c10d.Store) → bool  
# 检查存储是否支持扩展操作。  

multi_get(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str]) → list[bytes]  
# 获取所有指定键对应的值。如果这些键中有任何一个不存在于存储中，函数会等待超时时间。  
参数：  
keys (List[str]) – 要从存储中获取值的键列表。示例：>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.set("first_key", "po")  
>>> store.set("second_key", "tato")  
>>> # 应返回 [b"po", b"tato"]  
>>> store.multi_get(["first_key", "second_key"])  

multi_set(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str], arg1: collections.abc.Sequence[str]) → None  
# 根据指定的键和值将键值对列表插入存储中  
参数：  
keys (List[str]) – 要插入的键。  
values (List[str]) – 要插入的值。  

示例：>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.multi_set(["first_key", "second_key"], ["po", "tato"])  
>>> # 应返回 b"po"  
>>> store.get("first_key")  

num_keys(self: torch._C._distributed_c10d.Store) → int  
# 返回存储中已设置的键的数量。需要注意的是，该数值通常会比通过 set() 和 add() 添加的键数多 1，因为需用一个键来协调所有使用该存储的节点。  

警告：当与 TCPStore 一起使用时，num_keys 返回的是写入底层文件的键的数量。如果该存储被销毁后使用同一文件创建了新的存储，原有的键仍会被保留。  

返回值：存储中存在的键的数量。  

示例：>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> # 以 TCPStore 为例，其他类型的存储也可使用  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.set("first_key", "first_value")  
>>> # 应返回 2  
>>> store.num_keys()  

queue_len(self: torch._C._distributed_c10d.Store, arg0: str) → int  
# 返回指定队列的长度。如果队列不存在，则返回 0。更多详情请参见 queue_push。  

参数：  
key (str) – 要获取其长度的队列键。  

queue_pop(self: torch._C._distributed_c10d.Store, key: str, block: bool = True) → bytes  
# 从指定队列中取出一个值；如果队列为空，则会等待超时。更多详情请参见 queue_push。如果 block 设置为 False，且队列为空时将抛出 dist.QueueEmptyError 异常。  

参数：  
key (str) – 要从中取值的队列键。  
block (bool) – 是否阻塞等待该键值，还是立即返回。  

queue_push(self: torch._C._distributed_c10d.Store, arg0: str, arg1: str) → None  
# 将一个值推入指定队列。若队列与 set/get 操作使用相同的键，则可能导致异常行为。队列支持 wait/check 操作，且使用 wait 时只会唤醒一个正在等待的节点，而非全部节点。  

参数：  
key (str) – 要推入的队列键。  
value (str) – 要推入队列的值。  

set(self: torch._C._distributed_c10d.Store, arg0: str, arg1: str) → None  
# 根据指定的键和值将键值对插入存储中。如果该键已存在于存储中，将会用新提供的值覆盖旧值。  

参数：  
key (str) – 要添加到存储中的键。  
value (str) – 与键关联、要添加到存储中的值。  

示例：>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.set("first_key", "first_value")  
>>> # 应返回 "first_value"  
>>> store.get("first_key")  

set_timeout(self: torch._C._distributed_c10d.Store, arg0: datetime.timedelta) → None  
# 设置存储的默认超时时间。该超时时间会在初始化期间以及 wait() 和 get() 方法中被使用。  

参数：  
timeout (timedelta) – 要在存储中设置的超时时间。  

示例：>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> # 以 TCPStore 为例，其他类型的存储也可使用  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> store.set_timeout(timedelta(seconds=10))  
>>> # 10 秒后将会抛出异常  
>>> store.wait(["bad_key"])  

属性：  
timeout  
# 获取存储的超时时间。  

方法：  
wait(*args, **kwargs)  
# 重载函数。  
wait(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str]) → None  
# 等待 keys 中的每个键都被添加到存储中。如果在存储初始化时设定的超时时间之前，并非所有键都已被设置，wait 方法将抛出异常。  

参数：  
keys (list) – 需要等待其被添加到存储中的键列表。  

示例：>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> # 以 TCPStore 为例，其他类型的存储也可使用  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> # 30 秒后将会抛出异常  
>>> store.wait(["bad_key"])  

wait(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str], arg1: datetime.timedelta) → None  
# 等待 keys 中的每个键都被添加到存储中；如果在指定的超时时间之前这些键仍未被设置，则抛出异常。  

参数：  
keys (list) – 需要等待其被添加到存储中的键列表。  
timeout (timedelta) – 在抛出异常之前，等待键被添加的时间长度。  

示例：>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> # 以 TCPStore 为例，其他类型的存储也可使用  
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))  
>>> # 10 秒后将会抛出异常  
>>> store.wait(["bad_key"], timedelta(seconds=10))  

类：torch.distributed.TCPStore  
# 基于 TCP 的分布式键值存储实现。服务器端存储负责保存数据，而客户端存储可通过 TCP 连接到服务器端存储，并执行诸如 set() 以插入键值对、get() 以检索键值对等操作。由于客户端存储会等待服务器建立连接，因此始终应初始化一个服务器端存储。  

参数：  
host_name (str) – 服务器端存储应运行的主机名或 IP 地址。  
port (int) – 服务器端存储用于监听请求的端口。  
world_size (int, 可选) – 存储用户的总数（客户端数量 + 服务器，即 1）。默认值为 None（表示存储用户数量不确定）。  
is_master (bool, 可选) – 初始化服务器端存储时为 True，客户端存储为 False。默认值为 False。  
timeout (timedelta, 可选) – 存储在初始化期间以及 get() 和 wait() 等方法中使用的超时时间。默认值为 timedelta(seconds=300)。  
wait_for_workers (bool, 可选) – 是否等待所有工作节点与服务器端存储建立连接。仅当 world_size 为固定值时适用。默认值为 True。  
multi_tenant (bool, 可选) – 如果设置为 True，则当前进程中具有相同主机/端口的所有 TCPStore 实例将共享同一个底层 TCPServer。默认值为 False。  
master_listen_fd (int, 可选) – 如果指定了该值，底层 TCPServer 将在该文件描述符上监听，该描述符必须是一个已绑定到端口的套接字。若要绑定临时端口，建议将端口设置为 0 并通过 .port 获取端口值。默认值为 None（表示服务器会创建一个新的套接字并尝试将其绑定到端口）。  
use_libuv (bool, 可选) – 如果设置为 True，则使用 libuv 作为 TCPServer 的后端。默认值为 True。  

示例：>>> import torch.distributed as dist  
>>> from datetime import timedelta  
>>> # 在进程 1（服务器）上运行  
>>> server_store = dist.TCPStore("127.0.0.1", 1234, 2, True, timedelta(seconds=30))  
>>> # 在进程 2（客户端）上运行  
>>> client_store = dist.TCPStore("127.0.0.1", 1234, 2, False)  
>>> # 初始化后，可从服务器或客户端调用任何存储方法  
>>> server_store.set("first_key", "first_value")  
>>> client_store.get("first_key")  

构造函数：__init__(self: torch._C._distributed_c10d.TCPStore, host_name: str, port: SupportsInt, world_size: SupportsInt | None = None, is_master: bool = False, timeout: datetime.timedelta = datetime.timedelta(seconds=300), wait_for_workers: bool = True, multi_tenant: bool = False, master_listen_fd: SupportsInt | None = None, use_libuv: bool = True) → None  
# 创建一个新的 TCPStore。  

属性：  
host  
# 获取存储用于监听请求的主机名。  

属性：  
libuvBackend  
# 如果使用 libuv 作为后端，则返回 True。  

属性：  
port  
# 获取存储用于监听请求的端口号。  

类：torch.distributed.HashStore  
# 基于底层哈希表的线程安全存储实现。该存储可在同一进程内使用（例如由其他线程使用），但无法在跨进程环境中使用。  

示例：>>> import torch.distributed as dist  
>>> store = dist.HashStore()  
>>> # 可以从其他线程中使用该存储  
>>> # 初始化后，可使用任何存储方法  
>>> store.set("first_key", "first_value")  

构造函数：__init__(self: torch._C._distributed_c10d.HashStore) → None  
# 创建一个新的 HashStore。  

类：torch.distributed.FileStore  
# 一种利用文件来存储底层键值对的存储实现。  

参数：  
file_name (str) – 用于存储键值对的文件路径。  
world_size (int, 可选) – 使用该存储的进程总数。默认值为 -1（负数值表示存储用户数量不确定）。  

示例：>>> import torch.distributed as dist  
>>> store1 = dist.FileStore("/tmp/filestore", 2)  
>>> store2 = dist.FileStore("/tmp/filestore", 2)  
>>> # 初始化后，可从服务器或客户端调用任何存储方法  
>>> store1.set("first_key", "first_value")  
>>> store2.get("first_key")  

构造函数：__init__(self: torch._C._distributed_c10d.FileStore, file_name: str, world_size: SupportsInt = -1) → None  
# 创建一个新的 FileStore。  

属性：  
path  
# 获取 FileStore 用于存储键值对的文件路径。  

类：torch.distributed.PrefixStore  
# 一种对三种键值存储（TCPStore、FileStore 和 HashStore）的封装类，它会在插入存储的每个键前添加一个前缀。  

参数：  
prefix (str) – 在将键插入存储之前要添加到该键前面的前缀字符串。  
store (torch.distributed.store) – 构成底层键值存储的存储对象。  

构造函数：__init__(self: torch._C._distributed_c10d.PrefixStore, prefix: str, store: torch._C._distributed_c10d.Store) → None  
# 创建一个新的 PrefixStore。  

属性：  
underlying_store  
# 获取被 PrefixStore 封装的底层存储对象。  

性能分析：集合通信  
# 可以使用 torch.profiler（推荐，仅 1.8.1 及更高版本可用）或 torch.autograd.profiler 来对这里提到的集合通信和点对点通信 API 进行性能分析。所有开箱即用的后端（gloo、nccl、mpi）都受支持，集合通信的使用情况将在性能分析的输出/跟踪结果中如实显示。对代码进行性能分析的方法与使用常规的 Torch 操作符完全相同：只需导入相应的库并使用 `torch.profiler()` 即可。示例代码如下：

```python
import torch
import torch.distributed as dist

with torch.profiler():
    tensor = torch.randn(20, 10)
    dist.all_reduce(tensor)
```

如需了解 `profiler` 的全部功能，请参阅其官方文档。

### 多 GPU 集群操作函数
**警告**：多 GPU 函数（即每个 CPU 线程对应多个 GPU 的模式）现已被弃用。目前，PyTorch Distributed 推荐的编程模型是每个线程仅使用一个设备，本文档中的 API 即为此模式的示例。如果您是后端开发人员且希望支持每个线程使用多个设备，请联系 PyTorch Distributed 的维护者。

### 对象级集群操作
**警告**：对象级集群操作存在诸多严重限制。在使用前请仔细评估其是否适用于您的具体场景。对象级集群操作是一组类似集群操作的函数，可用于处理任何可被序列化的 Python 对象。虽然实现了多种集群模式（如广播、全收集等），但它们大致都遵循以下流程：

1. 将输入对象转换为 pickle 格式的原始字节；
2. 将该字节数据放入字节张量中；
3. 向其他节点传递该字节张量的大小信息（第一次集群操作）；
4. 为每个节点分配大小合适的张量以执行实际的集群通信；
5. 传输对象数据本身（第二次集群操作）；
6. 将原始数据重新转换为 Python 对象。

对象级集群操作有时会表现出意外的性能或内存特性，从而导致运行时间过长或内存不足，因此应谨慎使用。以下是常见的问题：

- **序列化/反序列化时间不对称**：根据对象的数量、类型和大小不同，对象序列化过程可能十分耗时。当采用“入度式”集群操作（如 `gather_object`）时，接收节点需要反序列化的对象数量是发送节点序列化对象数量的 N 倍，这可能导致其他节点在后续的集群操作中超时。
- **张量通信效率低下**：张量应通过常规的集群 API 传输，而非对象级集群 API。虽然也可以通过对象级 API 传输张量，但该过程需要先进行序列化与反序列化（对于非 CPU 张量，还需进行 CPU 同步及设备到主机的数据复制），在除调试或故障排查之外的几乎所有场景下，重新编写代码使用常规集群 API 都更为高效。
- **张量所在的设备不可预期**：如果仍想通过对象级集群操作传输张量，还需注意与 CUDA（以及可能的其他加速器）相关的特殊问题。如果对当前位于 `cuda:3` 设备上的张量进行序列化后再反序列化，无论当前进程处于哪个节点，或者该进程的“默认” CUDA 设备是什么，反序列化后的张量仍会位于 `cuda:3` 设备上。而使用常规张量集群 API 时，“输出张量”始终位于同一本地设备上，这更符合人们的预期。此外，如果这是进程首次使用 GPU，反序列化操作会隐式激活 CUDA 上下文，从而浪费大量 GPU 内存。为避免此问题，应在将张量作为对象级集群操作的输入之前先将其移至 CPU。

### 第三方后端
除了内置的 GLOO/MPI/NCCL 后端外，PyTorch Distributed 还通过运行时注册机制支持第三方后端。关于如何通过 C++ 扩展开发第三方后端的参考资料，请参阅《教程——自定义 C++ 和 CUDA 扩展》以及 `test/cpp_extensions/cpp_c10d_extension.cpp` 文件。第三方后端的功能由其自身的实现方式决定。新的后端需继承自 `c10d::ProcessGroup`，并在导入时通过 `torch.distributed.Backend.register_backend()` 函数注册后端名称及实例化接口。如果手动导入该后端并使用对应的后端名称调用 `torch.distributed.init_process_group()`，则 `torch.distributed` 包将在该新后端上运行。

**警告**：第三方后端的支持仍处于实验阶段，可能会随时发生变化。

### 启动工具
`torch.distributed` 包还提供了一个名为 `torch.distributed.launch` 的启动工具。该辅助工具可用于在每个节点上启动多个进程，从而实现分布式训练。相关模块为 `torch.distributed.launch`。`torch.distributed.launch` 能够在每个训练节点上启动多个分布式训练进程。

**警告**：该模块即将被弃用，未来将由 `torchrun` 取代。该工具可用于单节点分布式训练，即在一个节点上启动一个或多个进程。它既支持 CPU 训练，也支持 GPU 训练。若用于 GPU 训练，每个分布式进程将在单独的 GPU 上运行，从而显著提升单节点训练性能。此外，它也可用于多节点分布式训练，通过在每个节点上启动多个进程来进一步提升多节点训练的性能。对于那些拥有多个支持直接 GPU 通信的 InfiniBand 接口的系统而言，这种方式尤为有益，因为所有接口都可以被用于提升集群通信带宽。无论是单节点还是多节点分布式训练，该工具都会按照指定的参数在每个节点上启动相应数量的进程（`--nproc-per-node` 参数）。若用于 GPU 训练，此数值必须小于或等于当前系统中的 GPU 数量（即 `nproc_per_node`），并且每个进程将在从 GPU 0 到 GPU `(nproc_per_node - 1)` 的某个 GPU 上运行。

**使用方法如下：**

- **单节点多进程分布式训练**：
  ```bash
  python -m torch.distributed.launch --nproc-per-node=NUM_GPUS_YOU_have YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3 和训练脚本中的其他参数)
  ```

- **多节点多进程分布式训练**（例如两个节点）：
  - **节点 1**（IP：192.168.1.1，可用端口：1234）：
    ```bash
    python -m torch.distributed.launch --nproc-per-node=NUM_GPUS_YOU_have --nnodes=2 --node-rank=0 --master-addr="192.168.1.1" --master-port=1234 YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3 和训练脚本中的其他参数)
    ```
  - **节点 2**：
    ```bash
    python -m torch.distributed.launch --nproc-per-node=NUM_GPUS_YOU_have --nnodes=2 --node-rank=1 --master-addr="192.168.1.1" --master-port=1234 YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3 和训练脚本中的其他参数)
    ```

要查看该模块提供的可选参数，可运行：
```bash
python -m torch.distributed.launch --help
```

**重要提示：**
1. 目前，该工具以及多进程分布式（单节点或多节点）GPU 训练仅在使用 NCCL 集群后端时才能获得最佳性能。因此，建议在 GPU 训练中使用 NCCL 后端。
2. 在训练程序中，必须解析该工具提供的命令行参数 `--local-rank=LOCAL_PROCESS_RANK`。如果训练程序使用了 GPU，应确保代码仅在 `LOCAL_PROCESS_RANK` 对应的 GPU 设备上运行。实现方式如下：
   - 解析 `local_rank` 参数：
     ```python
     >>> import argparse
     >>> parser = argparse.ArgumentParser()
     >>> parser.add_argument("--local-rank", type=int)
     >>> args = parser.parse_args()
     ```
   - 使用解析后的 `local_rank` 设置设备：
     ```python
     >>> torch.cuda.set_device(args.local_rank)  # 在代码运行之前设置
     # 或者
     >>> with torch.cuda.device(args.local_rank):
     >>>     # 运行你的代码
     >>> ...
     ```
   **版本 2.0.0 的变更**：从 PyTorch 2.0.0 开始，启动工具会将 `--local-rank=<rank>` 参数传递给脚本。相比之前使用的下划线形式 `--local_rank`，破折号形式的参数更为推荐。为保持向后兼容性，用户可能需要在参数解析代码中同时处理这两种格式，即在参数解析器中同时包含 `--local_rank` 和 `--local_rank` 两种写法。如果仅提供 `--local_rank`，启动工具会报错：“error: unrecognized arguments: –local-rank=<rank>”。对于仅支持 PyTorch 2.0.0 及更高版本的训练代码，只需包含 `--local-rank` 即可。
3. 在训练程序中，应在开头调用以下函数来初始化分布式后端。强烈建议使用 `init_method=env://`。虽然其他初始化方法（如 `tcp://`）也可能可行，但 `env://` 是该模块官方支持的初始化方式。
   ```python
   >>> torch.distributed.init_process_group(backend='YOUR BACKEND', init_method='env://')
   ```
4. 在训练程序中，既可以使用常规的分布式函数，也可以使用 `torch.nn.parallel.DistributedDataParallel()` 模块。如果训练程序使用了 GPU，并且希望使用该模块，配置方法如下：
   ```python
   >>> model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[args.local_rank], output_device=args.local_rank)
   ```
   请确保 `device_ids` 参数设置为代码将要运行的唯一 GPU 设备编号，通常即为进程的本地排名。换句话说，要使用该工具，`device_ids` 必须为 `[args.local_rank]`，`output_device` 也必须为 `args.local_rank`。
5. 另一种将 `local_rank` 通过环境变量 `LOCAL_RANK` 传递给子进程的方法是，在启动脚本时添加 `--use-env=True` 参数。此时需要修改上述子进程的示例代码，将 `args.local_rank` 替换为 `os.environ['LOCAL_RANK']`；因为设置了该参数，启动工具就不会再传递 `--local-rank` 参数。**警告**：`local_rank` 并非全局唯一的——它仅在机器上的每个进程内是唯一的。因此，不要用它来决定是否要向网络文件系统写入数据。关于未正确处理该问题可能导致的错误示例，可参考 `pytorch/pytorch#12042`。

### 子进程启动工具
`Multiprocessing` 包中的 `torch.multiprocessing.spawn()` 函数也提供了一种子进程启动功能。该辅助函数可用于启动多个进程，其工作原理是传入需要运行的函数，然后生成 N 个进程来执行该函数。它同样可以用于多进程分布式训练。关于使用方法的参考资料，请参阅 PyTorch 示例——ImageNet 实现。需要注意的是，该函数要求 Python 版本至少为 3.4。

### 调试 `torch.distributed` 应用程序
由于分布式系统中经常会出现难以理解的挂起、崩溃或节点间行为不一致的问题，因此调试分布式应用程序颇具挑战性。`torch.distributed` 提供了一套工具，可帮助用户以自助方式调试训练应用程序。

#### Python 断点功能
在分布式环境中使用 Python 的调试器极为方便，但由于其并非开箱即用，很多人根本不会使用它。PyTorch 为 `pdb` 提供了定制化的封装，简化了这一流程。`torch.distributed.breakpoint` 函数让这一过程变得更加简单。在内部实现上，该功能通过两种方式自定义了pdb的断点行为，其余功能则与普通pdb一致。它仅在被用户指定的一个进程等级上附加调试器，并通过调用torch.distributed.barrier()确保所有其他进程等级都暂停执行——一旦被调试的进程等级发出继续指令，该屏障便会释放。此外，它还会重新路由子进程的标准输入，使其连接到用户的终端。要使用此功能，只需在所有进程等级上调用torch.distributed.breakpoint(rank)，且每个等级的rank值需保持一致。

**监控型屏障#**  
从v1.10版本起，引入了torch.distributed.monitored_barrier()作为torch.distributed.barrier()的替代方案。后者在发生崩溃时会输出有用信息，指出可能是哪个进程等级出现了故障（即未能在指定超时时间内调用torch.distributed.monitored_barrier()）。torch.distributed.monitored_barrier()通过类似确认机制的发送/接收通信原语实现主机级屏障，从而使rank 0能够报告哪些进程等级未能及时响应屏障信号。例如，考虑以下代码：rank 1未能调用torch.distributed.monitored_barrier()（实际可能是由于应用程序错误或之前集体操作中的挂起导致）：

```python
import os
from datetime import timedelta
import torch
import torch.distributed as dist
import torch.multiprocessing as mp

def worker(rank):
    dist.init_process_group("nccl", rank=rank, world_size=2)
    # 监控型屏障需要gloo进程组来实现主机级同步。
    group_gloo = dist.new_group(backend="gloo")
    if rank not in [1]:
        dist.monitored_barrier(group=group_gloo, timeout=timedelta(seconds=2))

if __name__ == "__main__":
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29501"
    mp.spawn(worker, nprocs=2, args=())
```

此时，rank 0会输出如下错误信息，帮助用户判断是哪个进程等级出现了故障并进一步排查：

```
RuntimeError: Rank 1 failed to pass monitoredBarrier in 2000 ms
Original exception: [gloo/transport/tcp/pair.cc:598] Connection closed by peer [2401:db00:eef0:1100:3560:0:1c05:25d]:8594
```

**TORCH_DISTRIBUTED_DEBUG#**  
通过设置环境变量TORCH_DISTRIBUTED_DEBUG，可在TORCH_CPP_LOG_LEVEL=INFO的情况下触发更多有用的日志记录，并进行集体同步检查，以确保所有进程等级都能正确同步。该变量的取值可根据调试需求设置为OFF（默认值）、INFO或DETAIL。需注意，最详细的DETAIL级别可能会影响应用程序性能，因此仅建议在调试问题时使用。将TORCH_DISTRIBUTED_DEBUG设置为INFO时，使用torch.nn.parallel.DistributedDataParallel()训练的模型在初始化时会输出更多调试日志；而设置为DETAIL时，还会在部分迭代过程中记录运行时性能统计信息，包括前向传播时间、反向传播时间、梯度通信时间等数据。例如，在以下应用程序中：

```python
import os
import torch
import torch.distributed as dist
import torch.multiprocessing as mp

class TwoLinLayerNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.a = torch.nn.Linear(10, 10, bias=False)
        self.b = torch.nn.Linear(10, 1, bias=False)

    def forward(self, x):
        a = self.a(x)
        b = self.b(x)
        return (a, b)

def worker(rank):
    dist.init_process_group("nccl", rank=rank, world_size=2)
    torch.cuda.set_device(rank)
    print("init model")
    model = TwoLinLayerNet().cuda()
    print("init ddp")
    ddp_model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[rank])
    inp = torch.randn(10, 10).cuda()
    print("train")
    for _ in range(20):
        output = ddp_model(inp)
        loss = output[0] + output[1]
        loss.sum().backward()

if __name__ == "__main__":
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29501"
    os.environ["TORCH_CPP_LOG_LEVEL"] = "INFO"
    os.environ["TORCH_DISTRIBUTED_DEBUG"] = "DETAIL"  # 设置为DETAIL以进行运行时日志记录。
    mp.spawn(worker, nprocs=2, args=())
```

在初始化阶段会输出如下日志：

```
I0607 16:10:35.739390 515217 logger.cpp:173] [Rank 0]: DDP Initialized with:
    broadcast_buffers: 1
    bucket_cap_bytes: 26214400
    find_unused_parameters: 0
    gradient_as_bucket_view: 0
    is_multi_device_module: 0
    iteration: 0
    num_parameter_tensors: 2
    output_device: 0
    rank: 0
    total_parameter_size_bytes: 440
    world_size: 2
    backend_name: nccl
    bucket_sizes: 440
    cuda_visible_devices: N/A
    device_ids: 0
    dtypes: float
    master_addr: localhost
    master_port: 29501
    module_name: TwoLinLayerNet
    nccl_async_error_handling: N/A
    nccl_blocking_wait: N/A
    nccl_debug: WARN
    nccl_ib_timeout: N/A
    nccl_nthreads: N/A
    nccl_socket_ifname: N/A
    torch_distributed_debug: INFO
```

在运行时（当TORCH_DISTRIBUTED_DEBUG设置为DETAIL时），还会输出如下日志：

```
I0607 16:18:58.085681 544067 logger.cpp:344] [Rank 1 / 2] Training TwoLinLayerNet
    unused_parameter_size=0
    Avg forward compute time: 40838608
    Avg backward compute time: 5983335
    Avg backward comm. time: 4326421
    Avg backward comm/comp overlap time: 4207652

I0607 16:18:58.085693 544066 logger.cpp:344] [Rank 0 / 2] Training TwoLinLayerNet
    unused_parameter_size=0
    Avg forward compute time: 42850427
    Avg backward compute time: 3885553
    Avg backward comm. time: 2357981
    Avg backward comm/comp overlap time: 2234674
```

此外，TORCH_DISTRIBUTED_DEBUG=INFO还能增强torch.nn.parallel.DistributedDataParallel()在模型中存在未使用参数时的崩溃日志记录。目前，如果模型在前向传播中可能存在未使用的参数，必须在初始化时将find_unused_parameters=True传递给该模块；而从v1.10版本起，由于DistributedDataParallel()不支持反向传播中的未使用参数，所有模型输出都必须参与损失计算。这些约束对大型模型尤为棘手，因此当发生崩溃时，该模块会记录所有未使用参数的完整名称。例如，在上述应用程序中，若将损失函数修改为loss = output[1]，则TwoLinLayerNet.a在反向传播中将无法接收到梯度，从而导致DistributedDataParallel()失败。此时，系统会向用户提供关于未使用参数的信息，而对于大型模型而言，手动查找这些参数可能十分困难：

```
RuntimeError: Expected to have finished reduction in the prior iteration before starting a new one.
此错误表明您的模块中存在未用于计算损失的参数。
您可以通过向torch.nn.parallel.DistributedDataParallel传递关键字参数find_unused_parameters=True来启用未使用参数检测，并确保所有forward函数的输出都参与损失计算。如果已做到以上两点，但分布式数据并行模块仍无法找到模块forward函数返回值中的输出张量，请在报告问题时提供损失函数以及模块forward函数返回值的结构（如列表、字典或可迭代对象）。
    未为rank 0接收到梯度的参数：a.weight
    未为rank 0接收到梯度的参数索引：0
```

将TORCH_DISTRIBUTED_DEBUG设置为DETAIL还会在用户直接或间接发起的每一个集体操作（如DDP allreduce）之前，进行额外的一致性和同步性检查。这是通过创建一个包装进程组来实现的，该包装进程组会包裹torch.distributed.init_process_group()和torch.distributed.new_group()接口返回的所有进程组。这样一来，这些接口返回的将是一个包装进程组，其使用方式与普通进程组相同，但在将集体操作派发到底层进程组之前会先进行一致性检查。目前的检查包括调用torch.distributed.monitored_barrier()，以确保所有进程等级都完成未处理的集体操作，并报告出卡住的进程等级。随后，还会对集体操作本身进行一致性检查，确保所有集体函数匹配且使用一致的张量形状。如果出现不一致，应用程序崩溃时会生成详细的错误报告，而非仅显示挂起状态或无意义的错误信息。例如，考虑以下代码：在torch.distributed.all_reduce()中使用了不匹配的输入形状：

```python
import torch
import torch.distributed as dist
import torch.multiprocessing as mp

def worker(rank):
    dist.init_process_group("nccl", rank=rank, world_size=2)
    torch.cuda.set_device(rank)
    tensor = torch.randn(10 if rank == 0 else 20).cuda()
    dist.all_reduce(tensor)
    torch.cuda.synchronize(device=rank)

if __name__ == "__main__":
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29501"
    os.environ["TORCH_CPP_LOG_LEVEL"] = "INFO"
    os.environ["TORCH_DISTRIBUTED_DEBUG"] = "DETAIL"
    mp.spawn(worker, nprocs=2, args=())
```

使用NCCL后端时，此类应用程序很可能会挂起，而在复杂场景下定位根本原因十分困难。但如果用户启用TORCH_DISTRIBUTED_DEBUG=DETAIL并重新运行程序，以下错误信息就能揭示问题根源：

```
work = default_pg.allreduce([tensor], opts)
RuntimeError: Error when verifying shape tensors for collective ALLREDUCE on rank 0.
这很可能表明各进程等级输入到集体操作中的形状不一致。
获取到的形状为：10 [ torch.LongTensor{1} ]
```

**日志记录#**  
除了通过torch.distributed.monitored_barrier()和TORCH_DISTRIBUTED_DEBUG提供明确的调试支持外，torch.distributed的底层C++库还会以不同级别输出日志信息。这些日志有助于了解分布式训练任务的执行状态，以及排查网络连接故障等问题。下表展示了如何通过组合使用TORCH_CPP_LOG_LEVEL和TORCH_DISTRIBUTED_DEBUG环境变量来调整日志级别。TORCH_CPP_LOG_LEVEL TORCH_DISTRIBUTED_DEBUG：有效的日志级别。ERROR级日志会被忽略；WARNING级日志也会被忽略；INFO级日志同样会被忽略。日志输出格式为：INFO、INFO、INFO、Debug、INFO、DETAIL、Trace（亦即全部级别）。在分布式环境中，相关组件会抛出基于RuntimeError派生的自定义异常类型：torch.distributed.DistError——这是所有分布式异常的基类；torch.distributed.DistBackendError——当后端出现特定错误时会被抛出，例如在使用NCCL后端时，用户尝试使用NCCL库无法访问的GPU；torch.distributed.DistNetworkError——当网络相关库出现错误时会被抛出，比如“对端主动断开连接”；torch.distributed.DistStoreError——当存储模块出现错误时会被抛出，例如“TCP存储超时”。具体分类如下：class torch.distributed.DistError# 当分布式库中出现错误时抛出的异常；class torch.distributed.DistBackendError# 当分布式组件中的后端出现错误时抛出的异常；class torch.distributed.DistNetworkError# 当分布式组件中的网络连接出现错误时抛出的异常；class torch.distributed.DistStoreError# 当分布式存储模块出现错误时抛出的异常。如果您正在进行单节点训练，可以通过交互式方式在脚本中设置断点，这会非常方便。我们提供了专门用于在单个节点上设置断点的方法：torch.distributed.breakpoint(rank=0, skip=0, timeout_s=3600)。[source]# 仅在单个节点上设置断点，其他所有节点都会等待您完成断点操作后再继续执行。参数说明：rank（整数）——指定要在哪个节点上设置断点；默认值为0；skip（整数）——跳过前几次对该断点的触发操作；默认值为0。

```
torch.distributed
```

**模式 3：初始化**  
在调用其他任何方法之前，必须先使用 `torch.distributed.init_process_group()` 或 `torch.distributed.device_mesh.init_device_mesh()` 函数对程序包进行初始化。这两种函数都会阻塞，直到所有进程都加入进程组为止。**注意**：初始化操作并非线程安全。为避免各进程之间的“UUID”分配不一致，以及防止初始化过程中的竞态条件导致程序挂起，进程组的创建应在单个线程中执行。  

`torch.distributed.is_available()`  
# 如果分布式功能可用，则返回 True；否则，torch.distributed 不会暴露任何其他 API。目前，torch.distributed 已在 Linux、MacOS 和 Windows 系统上可用。若需从源代码构建 PyTorch，可设置 `USE_DISTRIBUTED=1` 来启用该功能。当前默认值为：Linux 和 Windows 下为 `USE_DISTRIBUTED=1`，MacOS 下为 `USE_DISTRIBUTED=0`。  
返回类型：`bool`  

`torch.distributed.init_process_group(backend=None, init_method=None, timeout=None, world_size=-1, rank=-1, store=None, group_name='', pg_options=None, device_id=None)`  
# 初始化默认的分布式进程组，同时也会初始化整个分布式功能包。初始化进程组主要有两种方式：  
1. 显式指定 `store`、`rank` 和 `world_size`；  
2. 指定 `init_method`（一个 URL 字符串），用于指定发现节点的位置及方式。也可选择性地指定 `rank` 和 `world_size`，或将所有必需参数编码到 URL 中而省略这些参数。如果两者均未指定，则默认 `init_method` 为 “env://”。  

**参数**：  
- `backend`（字符串或 `Backend` 类型，可选）：要使用的后端类型。根据构建时的配置，有效值包括 `mpi`、`gloo`、`nccl`、`ucc`、`xccl`，或是第三方插件注册的其他后端。从版本 2.6 开始，如果未指定 `backend`，c10d 会自动使用由 `device_id` 参数（如提供）所指示的设备类型对应的已注册后端。目前已知的默认映射关系为：cuda 对应 `nccl`，cpu 对应 `gloo`，xpu 对应 `xccl`。如果既未指定 `backend` 也未指定 `device_id`，c10d 会在运行时自动检测机器上的加速器，并使用对应该加速器（或 cpu）的已注册后端。此参数也可以小写字符串形式提供（如 “gloo”），并通过 `Backend` 属性访问（如 `Backend.GLOO`）。若使用 nccl 后端且每台机器上运行多个进程，则每个进程必须对其使用的每块 GPU 拥有独占访问权，因为进程间共享 GPU 可能会导致死锁或 NCCL 使用错误。`ucc` 后端仍处于实验阶段。可通过 `get_default_backend_for_device()` 查询设备的默认后端。  
- `init_method`（字符串，可选）：指定如何初始化进程组的 URL。如果未指定 `init_method` 或 `store`，则默认值为 “env://”。该参数与 `store` 互斥。  
- `world_size`（整数，可选）：参与任务的进程总数。如果指定了 `store`，则此参数为必填项。  
- `rank`（整数，可选）：当前进程的排名（应为 0 到 `world_size-1` 之间的数字）。如果指定了 `store`，则此参数为必填项。  
- `store`（`Store` 类型，可选）：所有工作进程均可访问的键值存储，用于交换连接/地址信息。该参数与 `init_method` 互斥。  
- `timeout`（`timedelta` 类型，可选）：对进程组执行的操作设置的超时时间。NCCL 后端的默认超时时间为 10 分钟，其他后端为 30 分钟。超过此时间后，集合操作将异步中止，进程也会崩溃。之所以如此，是因为 CUDA 执行是异步的，一旦出现失败的 NCCL 异步操作，后续的 CUDA 操作可能会在损坏的数据上执行，继续运行已不再安全。如果设置了 `TORCH_NCCL_BLOCKING_WAIT`，进程将会阻塞并等待超时发生。  
- `group_name`（字符串，可选，已弃用）：进程组名称。此参数会被忽略。  
- `pg_options`（`ProcessGroupOptions` 类型，可选）：进程组选项，用于指定在构建特定进程组时需要传递的额外参数。目前仅支持 nccl 后端的 `ProcessGroupNCCL.Options`；可指定 `is_high_priority_stream`，以便在存在计算内核等待时，让 nccl 后端优先处理高优先级的 cuda 流。如需了解 nccl 的其他配置选项，请参阅 https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-t  
- `device_id`（`torch.device` 或整数类型，可选）：指定当前进程将要使用的特定设备，以便针对该设备进行后端优化。目前仅在 NCCL 模式下有效：通信模块会立即被创建（直接调用 `ncclCommInit*` 而非常规的延迟调用），并且子组会在可能的情况下使用 `ncclCommSplit` 来避免不必要的组创建开销。若希望提前检测 NCCL 初始化错误，也可使用此参数。如果提供整数值，API 会假定在编译时确定的加速器类型将被使用。  

**注意**：若要启用 `Backend.MPI` 后端，需在支持 MPI 的系统上从源代码构建 PyTorch。目前对多个后端的支持仍处于实验阶段。若未指定后端，系统会同时创建 `gloo` 和 `nccl` 两种后端：使用 CPU 张量的集合操作会通过 `gloo` 后端处理，而使用 CUDA 张量的集合操作则通过 `nccl` 后端处理。也可通过传递格式为 “<设备类型>:<后端名称>,<设备类型>:<后端名称>” 的字符串来指定自定义后端，例如 “cpu:gloo,cuda:custom_backend”。  

`torch.distributed.device_mesh.init_device_mesh(device_type, mesh_shape, *, mesh_dim_names=None, backend_override=None)`  
# 根据 `device_type`、`mesh_shape` 和 `mesh_dim_names` 参数初始化一个 DeviceMesh。这将创建一个具有 n 维数组布局的 DeviceMesh，其中 n 即为 `mesh_shape` 的长度。如果提供了 `mesh_dim_names`，则每个维度将分别用 `mesh_dim_names[i]` 命名。**注意**：`init_device_mesh` 遵循 SPMD 编程模型，即同一个 PyTorch Python 程序会在集群中的所有进程/排名上运行。因此必须确保所有进程的 `mesh_shape`（描述设备布局的 n 维数组的维度）完全一致，否则可能导致程序挂起。**注意**：如果未找到任何进程组，`init_device_mesh` 会后台自动初始化分布式通信所需的进程组。  

**参数**：  
- `device_type`（字符串）：网格的设备类型。目前支持 “cpu”、“cuda/cuda-like”、“xpu”。不允许传入包含 GPU 索引的设备类型，如 “cuda:0”。  
- `mesh_shape`（元组，整数类型）：定义描述设备布局的多维数组各维度的元组。  
- `mesh_dim_names`（元组，字符串类型，可选）：用于为描述设备布局的多维数组的每个维度指定名称的元组。其长度必须与 `mesh_shape` 相同，且 `mesh_dim_names` 中的每个字符串都必须唯一。  
- `backend_override`（字典，整数/字符串类型或元组类型，可选）：用于覆盖为每个网格维度要创建的某些或所有进程组的设置。每个键可以是维度的索引，也可以是其名称（若提供了 `mesh_dim_names`）。每个值可以是一个包含后端名称及其选项的元组，或者仅包含这两者之一（此时另一项将自动设置为默认值）。  

**返回值**：表示设备布局的 `DeviceMesh` 对象。  
返回类型：`DeviceMesh`  

**示例**：  
```python
>>> from torch.distributed.device_mesh import init_device_mesh
>>> mesh_1d = init_device_mesh("cuda", mesh_shape=(8,))
>>> mesh_2d = init_device_mesh("cuda", mesh_shape=(2, 8), mesh_dim_names=("dp", "tp"))
```  

`torch.distributed.is_initialized()`  
# 检查默认进程组是否已初始化。  
返回类型：`bool`  

`torch.distributed.is_mpi_available()`  
# 检查 MPI 后端是否可用。  
返回类型：`bool`  

`torch.distributed.is_nccl_available()`  
# 检查 NCCL 后端是否可用。  
返回类型：`bool`  

`torch.distributed.is_gloo_available()`  
# 检查 Gloo 后端是否可用。  
返回类型：`bool`  

`torch.distributed.distributed_c10d.is_xccl_available()`  
# 检查 XCCL 后端是否可用。  
返回类型：`bool`  

`torch.distributed.is_torchelastic_launched()`  
# 检查当前进程是否是通过 `torch.distributed.elastic`（即 torchelastic）启动的。系统会通过是否存在 `TORCHELASTIC_RUN_ID` 环境变量来判断当前进程是否由 torchelastic 启动。这是一个合理的判断依据，因为 `TORCHELASTIC_RUN_ID` 会映射到用于节点发现的 rendezvous id，该值始终非空。  
返回类型：`bool`  

`torch.distributed.get_default_backend_for_device(device)`  
# 返回指定设备的默认后端。  
**参数**：  
- `device`（字符串或 `torch.device` 类型）：需要获取默认后端的设备。  

**返回值**：指定设备的默认后端，以小写字符串形式返回。  
返回类型：`str`  

目前支持三种初始化方式：  

**TCP 初始化**  
# 使用 TCP 进行初始化有两种方法，均要求所有进程都能访问某个网络地址，并且需要指定期望的 `world_size`。第一种方法需要指定属于排名 0 的进程的地址。此初始化方法要求所有进程都必须手动指定自己的排名。**注意**：最新的分布式包已不再支持多播地址，`group_name` 也已弃用。  
```python
import torch.distributed as dist
# 使用某台机器的地址
dist.init_process_group(backend, init_method='tcp://10.1.1.20:23456', rank=args.rank, world_size=4)
```  

**共享文件系统初始化**  
# 另一种初始化方法利用群组中所有机器都能访问的共享文件系统，同时需要指定期望的 `world_size`。URL 应以 `file://` 开头，并包含共享文件系统中某个现有目录下并不存在的文件路径。文件系统初始化会在该文件不存在时自动创建它，但不会删除该文件。因此，你有责任在下次对相同路径/名称调用 `init_process_group()` 之前清理该文件。**注意**：最新的分布式包已不再支持自动分配排名，`group_name` 也已弃用。  
**警告**：此方法假定文件系统支持使用 `fcntl` 进行锁定——大多数本地系统及 NFS 都支持该功能。  
**警告**：此方法会始终创建该文件，并会在程序结束时尽力清理并删除它。换句话说，每次使用文件初始化方法时，都需要一个全新的空文件才能使初始化成功。如果再次使用上一次初始化时留下的文件（而该文件并未被及时清理），这将属于异常行为，往往会导致死锁和程序故障。因此，尽管该机制会尽力清理此类文件，但若自动删除操作未能成功，就有责任在训练结束后确保将该文件移除，以避免其在后续过程中被重复使用。尤其是当您计划对同一文件名多次调用 init_process_group() 时，这一点尤为重要。换言之，如果文件未被移除或清理，而您又对该文件再次调用 init_process_group()，则很可能会出现故障。这里的通用原则是：每次调用 init_process_group() 时，都必须确保该文件不存在或为空。  
import torch.distributed as dist  
# 必须始终指定 rank  
dist.init_process_group(backend, init_method='file:///mnt/nfs/sharedfile', world_size=4, rank=args.rank)  

环境变量初始化  
# 该方法会从环境变量中读取配置，从而让用户能够完全自定义信息的获取方式。需要设置的变量包括：  
MASTER_PORT – 必填；必须是 rank 为 0 的机器上尚未被占用的端口  
MASTER_ADDR – 必填（rank 为 0 的节点除外）；rank 为 0 的节点的地址  
WORLD_SIZE – 必填；可在此处设置，也可通过调用 init 函数来设置  
RANK – 必填；可在此处设置，也可通过调用 init 函数来设置  
系统会将 rank 为 0 的机器用作建立所有连接的起点。这是默认方式，意味着无需指定 init_method（或可设置为 env://）。  

缩短初始化时间  
# TORCH_GLOO_LAZY_INIT – 采用按需建立连接的方式，而非使用全网状结构，从而显著降低非 all2all 操作的初始化时间。

```
torch.distributed.init_process_group()
```

**模式 4：** 示例：

```
>>> from torch.distributed.device_mesh import init_device_mesh
>>>
>>> mesh_1d = init_device_mesh("cuda", mesh_shape=(8,))
>>> mesh_2d = init_device_mesh("cuda", mesh_shape=(2, 8), mesh_dim_names=("dp", "tp"))
```

**模式 5：分组** # 默认情况下，集合操作会在默认分组（也称为世界组）上执行，要求所有进程都参与分布式函数调用。不过，某些工作负载可以从更细粒度的通信中受益，这时就需要用到分布式分组。可以使用 `new_group()` 函数来创建新的分组，这些分组可以包含所有进程中的任意子集。该函数会返回一个不可见的组句柄，可作为参数传递给所有的集合操作函数（集合操作函数是用于在某些常见编程模式中进行信息交换的分布式函数）。  
`torch.distributed.new_group(ranks=None, timeout=None, backend=None, pg_options=None, use_local_synchronization=False, group_desc=None, device_id=None)` [来源]  
# 创建一个新的分布式分组。该函数要求主分组中的所有进程（即属于该分布式任务的所有进程）都调用此函数，即便它们日后不会成为该分组的成员。此外，所有进程创建分组的顺序也必须保持一致。  

**警告：安全并发使用**：当使用 NCCL 后端同时运行多个进程组时，用户必须确保所有进程的集合操作按全局一致的顺序执行。如果一个进程内的多个线程发起集合操作，则需要通过显式同步来保证执行顺序的一致性。当使用 `torch.distributed` 通信 API 的异步版本时，函数会返回一个工作对象，通信内核会被放入独立的 CUDA 流中处理，从而实现通信与计算的并行。一旦在一个进程组上启动了一个或多个异步操作，在使用另一个进程组之前，必须通过调用 `work.wait()` 来与其他 CUDA 流进行同步。更多详细信息请参阅《同时使用多个 NCCL 通信器》<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html#using-multiple-nccl-communicators-concurrently>。  

**参数**  
- `ranks`（`list[int]`）：分组成员的进程序号列表。如果为 `None`，则默认使用所有进程序号。默认值为 `None`。  
- `timeout`（`timedelta`，可选）：详细信息及默认值请参见 `init_process_group`。  
- `backend`（`str` 或 `Backend`，可选）：要使用的后端。根据构建时的配置，有效值为 `gloo` 和 `nccl`。默认使用与全局分组相同的后端。该参数应以小写字符串形式提供（例如 `"gloo"`），也可以通过 `Backend` 属性访问（例如 `Backend.GLOO`）。如果未指定该参数，则使用默认进程组对应的后端。默认值为 `None`。  
- `pg_options`（`ProcessGroupOptions`，可选）：进程组选项，用于指定在构建特定进程组时需要传递的额外参数。例如对于 NCCL 后端，可以指定 `is_high_priority_stream`，以便进程组能够使用高优先级的 CUDA 流。关于 NCCL 的其他可用配置选项，请参阅 https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-tuse_local_synchronization。  
- `use_local_synchronization`（`bool`，可选）：在进程组创建完成后执行组内屏障操作。不同之处在于，非成员进程序号无需调用该 API，也不会参与屏障操作。  
- `group_desc`（`str`，可选）：用于描述该进程组的字符串。  
- `device_id`（`torch.device`，可选）：指定要将该进程“绑定”到的特定设备。如果提供了此参数，`new_group` 函数会立即尝试为该设备初始化通信后端。  

**返回值**  
返回一个分布式分组的句柄，可用于传递给集合操作函数；如果当前进程序号不在 `ranks` 列表中，则返回 `GroupMember.NON_GROUP_MEMBER`。注意：`use_local_synchronization` 选项不适用于 MPI。另外，虽然当 `use_local_synchronization=True` 且在集群规模较大、进程组规模较小时能显著提升性能，但需谨慎使用，因为它会改变集群的行为——非成员进程序号不会参与 `group_barrier()` 操作。此外，如果每个进程序号都创建多个重叠的进程组，该选项还可能导致死锁。为避免这种情况，务必确保所有进程序号遵循相同的全局创建顺序。  

`torch.distributed.get_group_rank(group, global_rank)` [来源]  
# 将全局进程序号转换为分组内的相对进程序号。如果 `global_rank` 不属于该分组，则会引发 `RuntimeError`。  
**参数**  
- `group`（`ProcessGroup`）：用于查找相对进程序号的进程组。  
- `global_rank`（`int`）：要查询的全局进程序号。  

**返回值**  
`global_rank` 在该分组内的相对进程序号。  
**返回类型**：`int`  
注意：在默认进程组上调用此函数会返回自身值。  

`torch.distributed.get_global_rank(group, group_rank)` [来源]  
# 将分组内的相对进程序号转换为全局进程序号。如果 `group_rank` 不属于该分组，则会引发 `RuntimeError`。  
**参数**  
- `group`（`ProcessGroup`）：用于查找对应全局进程序号的进程组。  
- `group_rank`（`int`）：要查询的分组内相对进程序号。  

**返回值**  
`group_rank` 在该分组内的全局进程序号。  
**返回类型**：`int`  
注意：在默认进程组上调用此函数会返回自身值。  

`torch.distributed.get_process_group_ranks(group)` [来源]  
# 获取与该分组相关的所有进程序号。  
**参数**  
- `group`（`Optional[ProcessGroup]`）：用于获取进程序号的进程组。如果为 `None`，则使用默认进程组。  

**返回值**  
按分组内相对进程序号排序的全局进程序号列表。  
**返回类型**：`list[int]`

```
new_group()
```

**模式 6：** 警告：安全并发使用。当使用 NCCL 后端搭配多个进程组时，用户必须确保所有节点上集合操作的执行顺序保持全局一致。如果一个进程内的多个线程同时发起集合操作，则需要通过显式同步机制来保证执行顺序的统一。而使用 `torch.distributed` 通信 API 的异步版本时，系统会返回一个工作对象，并将通信内核调度到独立的 CUDA 流中处理，从而实现通信与计算的并行执行。一旦某个进程组已发起一个或多个异步操作，在使用其他进程组之前，必须先通过调用 `work.wait()` 方法将其与其他 CUDA 流同步。更多详细信息请参阅《同时使用多个 NCCL 通信器》<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html#using-multiple-nccl-communicators-concurrently>。

```
NCCL
```

**模式 7：** 注意，如果您同时使用 DistributedDataParallel 和分布式 RPC 框架，那么计算梯度时应始终使用 torch.distributed.autograd.backward()，而参数优化则需借助 torch.distributed.optim.DistributedOptimizer。示例如下：>>> import torch.distributed.autograd as dist_autograd >>> from torch.nn.parallel import DistributedDataParallel as DDP >>> import torch >>> from torch import optim >>> from torch.distributed.optim import DistributedOptimizer >>> import torch.distributed.rpc as rpc >>> from torch.distributed.rpc import RRef >>> >>> t1 = torch.rand((3, 3), requires_grad=True) >>> t2 = torch.rand((3, 3), requires_grad=True) >>> rref = rpc.remote("worker1", torch.add, args=(t1, t2)) >>> ddp_model = DDP(my_model) >>> >>> # 设置优化器 >>> optimizer_params = [rref] >>> for param in ddp_model.parameters(): >>> optimizer_params.append(RRef(param)) >>> >>> dist_optim = DistributedOptimizer( >>> optim.SGD, >>> optimizer_params, >>> lr=0.05, >>> ) >>> >>> with dist_autograd.context() as context_id: >>> pred = ddp_model(rref.to_here()) >>> loss = loss_func(pred, target) >>> dist_autograd.backward(context_id, [loss]) >>> dist_optim.step(context_id)

```
torch.distributed.autograd.backward()
```

**模式 8：** static_graph（布尔值）——当该参数设置为 True 时，DDP 就会识别出所训练的模型图是静态的。所谓静态图，意味着：1）在整个训练过程中，已使用和未使用的参数集合不会发生变化；在这种情况下，无论用户是否将 find_unused_parameters 设置为 True 都无关紧要。2）模型的训练方式在整个训练过程中也不会改变（即不存在随迭代次数变化的控制流）。当 static_graph 设为 True 时，DDP 能够支持以往无法处理的情况，包括：1）递归反向传播；2）多次进行激活值检查点保存；3）在模型存在未使用参数时进行激活值检查点保存；4）前向函数之外还存在模型参数。此外，由于当 static_graph 设为 True 时 DDP 不会在每次迭代中都搜索图结构以检测未使用的参数，因此还有可能提升性能。要判断是否可以将 static_graph 设置为 True，一种方法是在之前的模型训练结束后查看 DDP 的日志数据，如果 ddp_logging_data.get("can_set_static_graph") 的值为 True，那么通常也可以将 static_graph 设为 True。示例：>>> model_DDP = torch.nn.parallel.DistributedDataParallel(model) >>> # 训练循环 >>> ... >>> ddp_logging_data = model_DDP._get_ddp_logging_data() >>> static_graph = ddp_logging_data.get("can_set_static_graph")

```
True
```

## 参考文档

该技能在 `references/` 目录中提供了详尽的文档资料：

- **other.md** - 其他相关文档

当需要详细信息时，可使用 `view` 命令来读取特定的参考文件。

## 使用该技能的指南

### 对于初学者
建议先阅读 `getting_started` 或教程类参考文件，以掌握基础概念。

### 针对特定功能
如需详细信息，请查阅对应类别的参考文件（如 API 文档、使用指南等）。

### 代码示例
上方的快速参考部分汇总了从官方文档中提取的常见代码模式。

## 资源目录

### references/
此处整理了从官方来源提取的文档资料，包含以下内容：
- 详细说明
- 带有语言注释的代码示例
- 对应原始文档的链接
- 便于快速导航的目录结构

### scripts/
可在此处添加用于常见自动化任务的辅助脚本。

### assets/
可用于存放模板、基础代码框架或示例项目。

## 备注事项

- 该技能是根据官方文档自动生成的。
- 参考文档保留了原始文档的结构与示例内容。
- 代码示例中包含语言检测功能，可实现更出色的语法高亮显示。
- 快速参考模式是从文档中的常见使用案例中提取而来的。

## 更新说明

如需用最新文档更新此技能：
1. 使用相同的配置重新运行抓取工具。
2. 该技能将基于最新信息被重新生成。


