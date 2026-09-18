# PyTorch FSDP — 常见模式（完整参考）

### 常见模式

**模式 1：通用连接上下文管理器**  
# 创建时间：2025年6月6日 | 最后更新时间：2025年6月6日  
该通用连接上下文管理器可用于对结构不均匀的输入数据进行分布式训练。本页面介绍了相关类（Join、Joinable 和 JoinHook）的 API 接口。如需教程，请参阅《使用连接上下文管理器对结构不均匀的输入进行分布式训练》。  

```python
class torch.distributed.algorithms.Join(joinables, enable=True, throw_on_early_termination=False, **kwargs)
```
[来源]  
该类定义了通用连接上下文管理器，可在进程完成连接后调用自定义钩子函数。这些钩子函数应替代未参与连接的进程所执行的集合通信操作，从而避免程序挂起或出现错误，并确保算法的正确性。有关钩子函数定义的详细信息，请参阅 JoinHook 文档。  

**警告**：为保证正确性，该上下文管理器要求每个参与连接的对象在执行各自的迭代级集合通信之前，先调用 `notify_join_context()` 方法。  

**警告**：该上下文管理器要求所有 JoinHook 对象中的进程组属性必须一致。如果存在多个 JoinHook 对象，则以第一个对象的设备作为默认设备。进程组及设备信息会被用于检测未参与的进程；同时，在启用了 `throw_on_early_termination` 参数时，还会通过全量求和操作通知相关进程抛出异常。可连接的参数（List[Joinable]）——即参与连接的各个对象列表，其对应的钩子函数会按照给定的顺序依次被调用。enable（bool）——用于启用非均匀输入检测的标志位；将其设置为False可关闭上下文管理器的该功能，仅应在用户确定输入不会是非均匀结构时使用（默认值为True）。throw_on_early_termination（bool）——用于控制在检测到非均匀输入时是否抛出异常的标志位（默认值为False）。示例：>>> import os >>> import torch >>> import torch.distributed as dist >>> import torch.multiprocessing as mp >>> import torch.nn.parallel.DistributedDataParallel as DDP >>> import torch.distributed.optim.ZeroRedundancyOptimizer as ZeRO >>> from torch.distributed.algorithms.join import Join >>> >>> # 在每个生成的工作进程中 >>> def worker(rank): >>> dist.init_process_group("nccl", rank=rank, world_size=2) >>> model = DDP(torch.nn.Linear(1, 1).to(rank), device_ids=[rank]) >>> optim = ZeRO(model.parameters(), torch.optim.Adam, lr=0.01) >>> # 号码为1的工作进程比编号为0的多了一个输入 >>> inputs = [torch.tensor([1.]).to(rank) for _ in range(10 + rank)] >>> with Join([model, optim]): >>> for input in inputs: >>> loss = model(input).sum() >>> loss.backward() >>> optim.step() >>> # 所有工作进程均能正常执行到这里，不会出现挂起或错误情况 static notify_join_context(joinable)[source]# 用于通知连接上下文管理器：调用该函数的进程尚未完成连接。如果设置 throw_on_early_termination=True，该方法会检查是否检测到输入不均衡的情况（即是否存在某个进程已提前加入），一旦发现此类情况就会抛出异常。该函数应在可加入对象执行每次迭代前的集合通信之前被调用。例如，在 DistributedDataParallel 的前向传播开始时即可调用此函数。只有最先被传入上下文管理器的可加入对象会执行该函数中的集合通信操作，而对于其他对象而言，此函数则不会执行任何操作。参数：joinable（Joinable）——调用此函数的可加入对象。返回值：如果该可加入对象是首个被传入上下文管理器的对象，则返回一个用于全量归约的异步任务句柄，用以通知上下文管理器该进程尚未加入；否则返回 None。类 torch.distributed.algorithms.Joinable [来源] # 这是一个为可加入类定义的抽象基类。继承自 Joinable 的可加入类除了需要实现用于返回设备信息的 join_device() 和用于返回进程组信息的 join_process_group() 方法外，还必须实现用于返回 JoinHook 实例的 join_hook() 方法。抽象属性：join_device：device # 返回用于执行上下文管理器所需的集合通信操作的设备。抽象方法：join_hook(**kwargs) [来源] # 为给定的可加入对象返回一个 JoinHook 实例。参数 kwargs（dict）——一个包含任意关键字参数的字典，用于在运行时修改连接钩子的行为；所有共享相同连接上下文管理器的 Joinable 实例都会接收到相同的 kwargs 值。返回类型：JoinHook 抽象属性 join_process_group：Any# 返回连接上下文管理器本身所需的集体通信所使用的进程组。类 torch.distributed.algorithms.JoinHook[来源]# 该类定义了连接钩子，为连接上下文管理器提供了两个入口点。这两个入口点分别是：主钩子，在仍有未连接的进程存在时会被反复调用；以及后钩子，在所有进程都连接完成后仅被调用一次。若要为通用的连接上下文管理器实现连接钩子，需定义一个继承自 JoinHook 的类，并根据需要重写 main_hook() 和 post_hook() 方法。main_hook()[来源]# 在仍有未连接的进程存在时调用此钩子，以便在训练迭代过程中对集体通信进行拦截。训练迭代指的是一次前向传播、反向传播以及优化器更新步骤。post_hook(is_last_joiner)[来源]# 在所有进程都连接完成后调用此钩子。该方法会接收一个额外的布尔参数 is_last_joiner，用于指示当前进程是否属于最后连接的进程之一。参数 is_last_joiner（bool）——如果当前进程是最后连接的进程之一，则值为 True；否则为 False。

```
Join
```

**模式 2：** 分布式通信包 - torch.distributed# 创建时间：2017年7月12日 | 最后更新时间：2025年9月4日 备注：如需了解与分布式训练相关的所有功能的简要介绍，请参阅《PyTorch分布式训练概述》。后端支持# torch.distributed支持四种内置后端，每种后端具有不同的功能特性。下表列出了每种后端在CPU或GPU环境下可使用的功能。对于NCCL而言，GPU指的是CUDA GPU；而对于XCCL，则指XPU GPU。只有当用于构建PyTorch的实现版本支持时，MPI才支持CUDA。后端 gloo mpi nccl xccl 设备 CPU GPU CPU GPU CPU GPU CPU GPU 发送 ✓ ✘ ✓ ? ✘ ✓ ✘ ✓ 接收 ✓ ✘ ✓ ? ✘ ✓ ✘ ✓ 广播 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 全局归约 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 归约 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 全部收集 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 收集 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 分散发送 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 分散归约 ✓ ✓ ✘ ✘ ✘ ✓ ✘ ✓ 全向通信 ✓ ✓ ✓ ? ✘ ✓ ✘ ✓ 障碍指令 ✓ ✘ ✓ ? ✘ ✓ ✘ ✓ PyTorch自带的后端# PyTorch分布式包支持Linux（稳定版）、MacOS（稳定版）以及Windows（原型版）。在Linux系统中，默认情况下，Gloo和NCCL后端已被内置到PyTorch分布式模块中（仅在使用CUDA构建时才会包含NCCL）。MPI则是一种可选的后端，只有通过源代码方式构建PyTorch时才能将其纳入（例如，在已安装MPI的主机上构建PyTorch）。注意：从 PyTorch v1.8 版本开始，Windows 系统支持所有的集合通信后端，但 NCCL 除外。如果 init_process_group() 函数中的 init_method 参数指向文件，该文件必须遵循以下格式：本地文件系统，init_method="file:///d:/tmp/some_file"；共享文件系统，init_method="file://////{machine_name}/{share_folder_name}/some_file"。与 Linux 平台相同，您也可以通过设置 MASTER_ADDR 和 MASTER_PORT 环境变量来启用 TcpStore。那么该使用哪种后端呢？过去我们经常被问到“我应该选择哪种后端？”。以下是一般性建议：对于使用 CUDA GPU 进行的分布式训练，建议使用 NCCL 后端；对于使用 XPU GPU 的分布式训练，建议使用 XCCL 后端；而对于使用 CPU 的分布式训练，则建议使用 Gloo 后端。配备 InfiniBand 互连的 GPU 主机应选择 NCCL，因为它是目前唯一同时支持 InfiniBand 和 GPUDirect 的后端。配备以太网互连的 GPU 主机同样推荐使用 NCCL，因为它目前在分布式 GPU 训练方面表现最佳，尤其适用于单节点多进程或多节点分布式训练场景。如果您在使用 NCCL 时遇到问题，可以尝试将 Gloo 作为备选方案（需要注意的是，目前 Gloo 在 GPU 上的运行速度稍慢于 NCCL）。配备 InfiniBand 互连的 CPU 主机，如果其 InfiniBand 环境已启用 IP over IB 功能，则建议使用 Gloo，否则请使用 MPI。我们计划在后续版本中为 Gloo 添加对 InfiniBand 的支持。配备以太网互连的 CPU 主机则建议使用 Gloo，除非您有特殊理由必须使用 MPI。常用环境变量# 选择要使用的网络接口# 默认情况下，NCCL和Gloo两种后端都会尝试自动查找合适的网络接口。如果自动检测到的接口有误，您可以通过以下环境变量来手动指定（这些变量分别适用于对应的后端）：NCCL_SOCKET_IFNAME，例如 export NCCL_SOCKET_IFNAME=eth0；GLOO_SOCKET_IFNAME，例如 export GLOO_SOCKET_IFNAME=eth0。如果您使用的是Gloo后端，还可以用逗号分隔多个接口，示例如下：export GLOO_SOCKET_IFNAME=eth0,eth1,eth2,eth3。此时后端会以轮询方式在这些接口之间分配任务。所有进程必须在此变量中指定相同数量的接口，这一点至关重要。其他NCCL环境变量# 调试——当NCCL出现故障时，您可以设置NCCL_DEBUG=INFO，以便输出明确的警告信息以及基本的NCCL初始化信息。您还可以使用NCCL_DEBUG_SUBSYS来获取有关NCCL特定方面的更多详细信息。例如，设置NCCL_DEBUG_SUBSYS=COLL即可打印集合操作的相关日志，这在调试程序卡死问题时非常有用，尤其是那些由集合操作类型或消息大小不匹配引起的故障。如果拓扑检测失败，设置NCCL_DEBUG_SUBSYS=GRAPH则有助于查看详细的检测结果，以便在需要NCCL团队进一步协助时作为参考。性能调优——NCCL会基于拓扑检测自动进行调优，从而节省用户的调优工作量。在某些基于套接字的系统中，用户仍可尝试调整NCCL_SOCKET_NTHREADS和NCCL_NSOCKS_PERTHREAD这两个参数，以提升套接字网络带宽。对于AWS或GCP等部分云服务提供商，NCCL已预先针对这些参数进行了优化。如需查看完整的NCCL环境变量列表，请参阅NVIDIA NCCL的官方文档。此外，用户还可以通过torch.distributed.ProcessGroupNCCL.NCCLConfig和torch.distributed.ProcessGroupNCCL.Options进一步调整NCCL通信相关设置。可通过解释器中的help命令（例如help(torch.distributed.ProcessGroupNCCL.NCCLConfig)）了解更多相关信息。基础知识部分指出，torch.distributed模块为运行在多台机器上的多个计算节点之间的多进程并行计算提供了PyTorch支持及相应的通信机制。torch.nn.parallel.DistributedDataParallel()类则在此基础上构建，可作为任意PyTorch模型的封装层，实现同步分布式训练功能。这与torch.multiprocessing模块以及torch.nn.DataParallel()所提供的并行处理方式不同，因为它支持多台网络相连的机器，且用户必须为每个进程单独启动一份主训练脚本。在单机同步场景下，与包括torch.nn.DataParallel在内的其他数据并行实现方式相比，torch.distributed或torch.nn.parallel.DistributedDataParallel()封装依然具有优势：每个进程都会维护自己的优化器，并在每次迭代中执行完整的优化步骤。虽然这看似有些多余，因为梯度早已被收集并在各进程间平均，所有进程的梯度值本应相同，但这样一来就无需进行参数广播操作，从而减少了节点间张量传输所耗费的时间。此外，每个进程都拥有独立的Python解释器，避免了通过单个Python进程来驱动多个执行线程、模型副本或GPU所带来的额外解释器开销以及“GIL锁竞争”问题。这对于那些大量依赖Python运行时的模型尤为重要，尤其是那些包含循环层或众多小型组件的模型。初始化# 在调用其他任何方法之前，必须先使用torch.distributed.init_process_group()或torch.distributed.device_mesh.init_device_mesh()函数对相关包进行初始化。这两个函数会阻塞执行，直到所有进程都加入为止。注意：初始化操作并非线程安全。创建进程组时应通过单个线程来完成，这样可以避免不同节点之间出现不一致的“UUID”分配问题，同时也能防止初始化过程中发生竞态条件从而导致程序挂起。torch.distributed.is_available()[来源]# 若分布式模块可用则返回True，否则torch.distributed不会提供其他任何API。目前，torch.distributed已在Linux、MacOS和Windows系统上可用。若需从源代码构建PyTorch，则需将USE_DISTRIBUTED设置为1以启用该功能。当前，Linux和Windows的默认值为USE_DISTRIBUTED=1，而MacOS的默认值为USE_DISTRIBUTED=0。返回类型：bool。torch.distributed.init_process_group(backend=None, init_method=None, timeout=None, world_size=-1, rank=-1, store=None, group_name='', pg_options=None, device_id=None)[来源]# 初始化默认的分布式进程组，此操作同时也会初始化分布式模块。初始化进程组主要有两种方式：一种是明确指定存储位置、节点编号以及总节点数；另一种是指定init_method（一个URL字符串），用于指示从何处及如何发现其他节点。也可以选择性地指定节点编号和总节点数，或者将所有必需参数编码到URL中而省略这些参数。如果两者均未指定，则默认认为init_method为“env://”。参数：backend（str或Backend类型，可选）——要使用的后端类型。根据构建时的配置，有效的值包括mpi、gloo、nccl、ucc、xccl，或是第三方插件所注册的其他后端类型。自 2.6 版本起，如果未指定后端，c10d 将使用为 device_id 参数所指定的设备类型预先注册的后端（如有提供）。目前已知的默认注册对应关系为：cuda 使用 nccl，cpu 使用 gloo，xpu 使用 xccl。若既未指定后端也未指定 device_id，c10d 会在运行时自动检测机器上的加速器，并使用为该加速器（或 CPU）注册的后端。此字段可以小写字符串形式提供（例如“gloo”），也可通过 Backend 属性访问（例如 Backend.GLOO）。当使用 nccl 后端且每台机器上运行多个进程时，每个进程必须对其使用的所有 GPU 拥有独占访问权，因为进程间共享 GPU 可能会导致死锁或 NCCL 使用错误。ucc 后端仍处于实验阶段。可通过 get_default_backend_for_device() 函数查询该设备的默认后端。init_method（字符串，可选）——用于指定进程组初始化方式的 URL。如果未指定 init_method 或 store，则默认值为“env://”。该参数与 store 参数互斥。world_size（整数，可选）——参与任务的进程数量。若指定了 store，则此参数为必填项。rank（整数，可选）——当前进程的序号（应为 0 到 world_size-1 之间的数值）。若指定了 store，则此参数为必填项。store（存储对象，可选）——所有工作进程均可访问的键值存储，用于交换连接/地址信息。该参数与 init_method 参数互斥。timeout（定时器对象，可选）——针对进程组执行的操作所设置的超时时间。NCCL的默认值为10分钟，其他后端的默认值为30分钟。此时长为集体操作将被异步终止且进程崩溃的时间点。设置这样的机制是因为CUDA执行是异步的，一旦NCCL操作失败，后续的CUDA操作可能会在损坏的数据上运行，继续执行用户代码已不再安全。当设置了TORCH_NCCL_BLOCKING_WAIT时，进程将会阻塞并等待达到该超时时间。

group_name（字符串，可选，已过时）——组名称。该参数目前会被忽略。

pg_options（ProcessGroupOptions，可选）——进程组选项，用于指定在构建特定进程组时需要传递的额外选项。目前我们仅支持NCCL后端的ProcessGroupNCCL.Options选项；还可以指定is_high_priority_stream，以便在有计算内核等待时让NCCL后端优先处理高优先级的CUDA流。如需了解NCCL的其他可用配置选项，请参阅https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-t。

device_id（torch.device | int，可选）——指定该进程将要使用的特定设备，从而实现针对不同后端的优化。目前这一选项仅在NCCL环境下有效：它会立即创建通信器（直接调用ncclCommInit*而非常规的延迟调用），并且子组会在可能的情况下使用ncclCommSplit来避免不必要的组创建开销。如果您希望尽早发现 NCCL 初始化错误，也可以使用此字段。如果输入的是整数，API 会假定在编译时所指定的加速器类型将被使用。注意：若要启用 backend == Backend.MPI，需在支持 MPI 的系统上从源代码构建 PyTorch。另外，对多种后端的支持仍处于实验阶段。目前，若未指定后端，则会同时创建 gloo 和 nccl 两种后端——对于包含 CPU 张量的集合操作，将使用 gloo 后端；而对于包含 CUDA 张量的集合操作，则使用 nccl 后端。您也可以通过传入格式为“<设备类型>:<后端名称>,<设备类型>:<后端名称>”的字符串来指定自定义后端，例如“cpu:gloo,cuda:custom_backend”。torch.distributed.device_mesh.init_device_mesh(device_type, mesh_shape, *, mesh_dim_names=None, backend_override=None) [来源] # 根据 device_type、mesh_shape 以及 mesh_dim_names 参数初始化 DeviceMesh。这样会创建一个具有 n 维数组布局的 DeviceMesh，其中 n 即为 mesh_shape 的长度。如果提供了 mesh_dim_names，那么每个维度将会被标记为 mesh_dim_names[i]。注意：init_device_mesh 遵循 SPMD 编程模型，即同一个 PyTorch Python 程序会在集群中的所有进程/节点上运行。因此，请确保所有节点上的 mesh_shape（用于描述设备布局的 nD 数组的维度）完全一致，否则可能会导致程序挂起。注意：如果未找到进程组，init_device_mesh会后台自动初始化分布式通信所需的分布式进程组。参数如下：device_type（str）——网格中的设备类型。目前支持“cpu”、“cuda/cuda-like”和“xpu”三种类型。不允许传入包含GPU索引的设备类型，例如“cuda:0”。mesh_shape（Tuple[int]）——用于定义描述设备布局的多维数组各维度的元组。mesh_dim_names（Tuple[str]，可选）——用于为描述设备布局的多维数组的每一维度指定名称的元组。其长度必须与mesh_shape的长度一致，且mesh_dim_names中的每个字符串都必须唯一。backend_override（Dict[int | str, tuple[str, Options] | str | Options]，可选）——用于覆盖为每个网格维度创建的部分或全部进程组的配置。每个键可以是维度的索引，也可以是该维度的名称（前提是已提供mesh_dim_names）。每个值可以是一个包含后端名称及其选项的元组，或者仅包含这两个组件中的一个（此时另一个组件将自动设置为默认值）。返回值：一个表示设备布局的DeviceMesh对象。返回类型：DeviceMesh  
示例：  
>>> from torch.distributed.device_mesh import init_device_mesh  
>>> >>> mesh_1d = init_device_mesh("cuda", mesh_shape=(8,))  
>>> mesh_2d = init_device_mesh("cuda", mesh_shape=(2, 8), mesh_dim_names=("dp", "tp"))  

torch.distributed.is_initialized()[source]  
# 检查默认进程组是否已初始化。返回类型：bool  

torch.distributed.is_mpi_available()[source]  
# 检查是否支持 MPI 后端。返回类型：bool  

torch.distributed.is_nccl_available()[source]  
# 检查是否支持 NCCL 后端。返回类型：bool  

torch.distributed.is_gloo_available()[source]  
# 检查是否支持 Gloo 后端。返回类型：bool  

torch.distributed.distributed_c10d.is_xccl_available()[source]  
# 检查是否支持 XCCL 后端。返回类型：bool  

torch.distributed.is_torchelastic_launched()[source]  
# 检查当前进程是否是通过 torch.distributed.elastic（即 torchelastic）启动的。该函数通过 TORCHELASTIC_RUN_ID 环境变量的存在来间接判断当前进程是否由 torchelastic 启动。这一判断方式是合理的，因为 TORCHELASTIC_RUN_ID 会映射到寻址 ID，而该值始终非空，可用于识别进程身份以实现节点发现功能。返回类型：bool  

torch.distributed.get_default_backend_for_device(device)[source]  
# 返回指定设备的默认后端。参数：device（Union[str, torch.device]）——需要获取其默认后端的设备。该函数会以小写字符串的形式返回指定设备的默认后端。返回类型为字符串。目前支持三种初始化方式：TCP初始化——通过TCP进行初始化有两种方法，这两种方法都需要一个所有进程均可访问的网络地址以及指定的世界大小。第一种方法需要指定属于等级0进程的地址；此初始化方式要求所有进程都需手动指定各自的等级。请注意，在最新的分布式包中已不再支持多播地址，同时group_name也已过时。示例代码如下：import torch.distributed as dist # 使用某台机器的地址 dist.init_process_group(backend, init_method='tcp://10.1.1.20:23456', rank=args.rank, world_size=4) 共享文件系统初始化——另一种初始化方式是利用一组中所有机器均可访问的共享文件系统，再结合指定的世界大小。对应的URL应以file://开头，并指向共享文件系统中某个现有目录下并不存在的文件路径。如果该文件尚不存在，文件系统初始化会自动创建它，但不会删除该文件。因此，您有责任确保在再次调用init_process_group()使用相同的文件路径/名称之前，先清理该文件。同样需要注意的是，在最新的分布式包中已不再支持自动分配进程等级，group_name也已过时。警告：此方法假定文件系统支持使用 fcntl 进行锁定——大多数本地系统及 NFS 都具备该功能。另请注意，此方法会始终创建文件，并会在程序结束时尽力清理并删除该文件。换言之，每次通过文件初始化方法进行初始化时，都需要一个全新的空文件才能确保初始化成功。如果再次使用上一次初始化所使用的同一文件（而该文件未能被及时清理），就会出现异常行为，进而常常引发死锁和故障。因此，尽管此方法会尽力清理文件，但如果自动删除操作未能成功，您仍有责任在训练结束时确保该文件被移除，以避免其在下次被重复使用。如果您打算对同一个文件名多次调用 init_process_group()，这一点尤为重要。也就是说，如果该文件未被移除或清理，而您又对该文件再次调用 init_process_group()，则很可能会出现故障。一般而言，每次调用 init_process_group() 时，都应确保该文件不存在或为空。  
import torch.distributed as dist  
# 必须始终指定 rank  
dist.init_process_group(backend, init_method='file:///mnt/nfs/sharedfile', world_size=4, rank=args.rank)  

环境变量初始化  
# 此方法会从环境变量中读取配置，从而让用户能够完全自定义信息的获取方式。需要设置的变量包括：  
MASTER_PORT – 必需；必须是 rank 为 0 的机器上尚未被占用的端口  
MASTER_ADDR – 必需（rank 为 0 的机器除外）；rank 为 0 的节点地址  
WORLD_SIZE – 必需；既可在此处设置，也可通过调用 init 函数来设置  
RANK – 必需；既可在此处设置，也可通过调用 init 函数来设置  
rank 为 0 的机器将用于建立所有连接。这是默认方法，因此无需指定 init_method（或可设置为 env://）。  

缩短初始化时间  
# TORCH_GLOO_LAZY_INIT – 按需建立连接，而非采用全网状结构，这能显著提升非 all2all 操作的初始化速度。  

初始化后操作  
# 一旦执行了 torch.distributed.init_process_group()，就可以使用以下函数。若要检查进程组是否已初始化，可使用 torch.distributed.is_initialized()。  

class torch.distributed.Backend(name)[source]  
# 用于表示后端的类，类似枚举类型。可选的后端包括：GLOO、NCCL、UCC、MPI、XCCL 以及其他已注册的后端。该类的值均为小写字符串，例如“gloo”。这些值可作为属性来访问，比如Backend.NCCL。也可直接调用该类来解析字符串，例如Backend(backend_str)会检查backend_str是否有效，若有效则返回解析后的小写字符串。该类也支持大写字符串，例如Backend("GLOO")会返回“gloo”。需要注意的是，虽然存在Backend.UNDEFINED这一项，但它仅用作某些字段的初始值。用户既不应直接使用它，也不应假定其存在。

classmethod register_backend(name, func, extended_api=False, devices=None)[source]
# 使用给定的名称和实例化函数注册新的后端。此类方法被第三方ProcessGroup扩展用于注册新的后端。
参数：
name (str) – ProcessGroup扩展的后端名称，需与init_process_group()中的名称一致。
func (function) – 用于实例化后端的函数处理程序。该函数需在后台扩展中实现，并接受四个参数，即store、rank、world_size和timeout。
extended_api (bool, optional) – 该后端是否支持扩展参数结构。默认值为False。如果将该参数设置为 True，后端将获得一个 c10d::DistributedBackendOptions 的实例，以及由后端实现定义的进程组选项对象。device（字符串或字符串列表，可选）——该后端支持的设备类型，例如“cpu”、“cuda”等。若该参数为 None，则默认支持“cpu”和“cuda”两种类型。注意：对第三方后端的此项支持仍处于实验阶段，可能会发生变化。

torch.distributed.get_backend(group=None)[来源] # 返回指定进程组对应的后端。参数 group（ProcessGroup，可选）——要操作的进程组。默认值为主进程组。如果指定了其他特定进程组，则调用进程必须属于该进程组。返回值 以小写字符串形式返回指定进程组对应的后端。返回类型 Backend

torch.distributed.get_rank(group=None)[来源] # 返回当前进程在指定进程组中的排名，若未指定则使用默认值。排名是分配给分布式进程组中每个进程的唯一标识符，始终为从 0 到 world_size 的连续整数。参数 group（ProcessGroup，可选）——要操作的进程组。如果为 None，则使用默认进程组。返回值 进程组的排名；如果当前进程不属于该进程组，则返回 -1。返回类型 int

torch.distributed.get_world_size(group=None)[来源] # 返回当前进程组中的进程数量。参数 group（ProcessGroup，可选）——要操作的进程组。如果为 None，则使用默认进程组。返回值：若进程不属于该进程组，则返回世界大小 -1；返回类型为整数。关闭操作：在程序退出时，务必通过调用 destroy_process_group() 来释放资源。最简单的处理方式是在训练脚本中不再需要进程间通信的阶段——通常位于 main() 函数接近结尾处——使用 group 参数设为默认值 None，调用 destroy_process_group() 来销毁所有的进程组及后端。该操作应在每个训练进程内部执行，而非在最外层的进程启动层进行。如果某个进程组内的所有进程未能在指定超时时间内调用 destroy_process_group()，尤其是在应用程序中存在多个进程组（例如用于 N-D 并行计算）的情况下，程序退出时可能会出现挂起现象。这是因为 ProcessGroupNCCL 的销毁函数会调用 ncclCommAbort，而该调用必须由所有进程共同执行；但若通过 Python 的垃圾回收机制触发 ProcessGroupNCCL 的销毁函数，其调用顺序并不确定。调用 destroy_process_group() 可以确保所有进程以一致的顺序调用 ncclCommAbort，同时避免在 ProcessGroupNCCL 的销毁函数执行期间调用该函数，从而有效防止程序挂起。重新初始化：destroy_process_group() 也可用于销毁单个进程组。一个典型应用场景是容错训练，即在运行过程中可先销毁某个进程组，再重新初始化一个新的进程组。在这种情况下，至关重要的是在调用 `destroy` 方法之后、随后进行初始化之前，通过除 `torch.distributed` 原语之外的其他方式来同步各训练进程。由于实现此类同步存在较大难度，目前该功能既不受支持也未经过测试，因此被视为一个已知问题。如果这一使用场景给您带来了困扰，请在 GitHub 上提交问题或 RFC。  

**Groups**：默认情况下，集合操作会在默认群组（也称为“世界群组”）上执行，要求所有进程都进入分布式函数调用状态。不过，某些工作负载可以从更细粒度的通信中受益，这时就需要用到分布式群组。可以使用 `new_group()` 函数来创建新的群组，这些群组可包含所有进程中的任意子集。该函数会返回一个不可见的群组句柄，可将其作为参数传递给所有的集合操作函数（集合操作函数属于分布式函数，用于在某些常见的编程模式中交换信息）。  
参考文档：`torch.distributed.new_group(ranks=None, timeout=None, backend=None, pg_options=None, use_local_synchronization=False, group_desc=None, device_id=None)`  
**功能说明**：用于创建一个新的分布式群组。该函数要求主群组中的所有进程（即属于该分布式任务的所有进程）都必须调用此函数，即便它们日后不会成为该群组的成员。此外，所有进程创建群组的顺序也必须保持一致。警告：安全并发使用方式。当使用 NCCL 后端并启用多个进程组时，用户必须确保所有节点上集合操作的执行顺序保持全局一致。若某个进程内的多个线程同时发起集合操作，则需要通过显式同步机制来保证执行顺序的统一性。而使用 `torch.distributed` 通信 API 的异步版本时，系统会返回一个工作对象，并将通信内核调度到独立的 CUDA 流中处理，从而实现通信与计算操作的并行执行。一旦某个进程组已启动了一个或多个异步操作，在使用另一个进程组之前，必须先通过调用 `work.wait()` 方法将其与其他 CUDA 流同步。更多详细信息请参阅《同时使用多个 NCCL 通信器》<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html#using-multiple-nccl-communicators-concurrently>。  

参数：  
- `ranks`（`list[int]`）：进程组成员的节点编号列表。若未指定，则默认使用所有节点。默认值为 `None`。  
- `timeout`（`timedelta`，可选）：具体细节及默认值请参见 `init_process_group` 的说明。  
- `backend`（`str` 或 `Backend`，可选）：要使用的后端类型。根据构建时的配置，有效值为 `gloo` 和 `nccl`。默认情况下会使用与全局进程组相同的后端。该参数应以小写字符串形式指定（例如 `"gloo"`），也可通过 `Backend` 属性访问（例如 `Backend.GLOO`）。若未指定该参数，则会使用默认进程组对应的后端。默认值为 None。pg_options（ProcessGroupOptions，可选）——用于指定在构建特定进程组时需要传递的附加选项。例如，对于 nccl 后端，可以指定 is_high_priority_stream，从而使进程组能够使用高优先级的 CUDA 流。有关配置 nccl 的其他可用选项，请参阅 https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-tuse_local_synchronization。use_local_synchronization（bool，可选）：在进程组创建完成后执行组内本地屏障操作。不同之处在于，非成员节点无需调用该 API，也不会参与屏障操作。group_desc（str，可选）——用于描述进程组的字符串。device_id（torch.device，可选）——用于将此进程“绑定”到的单个特定设备。如果提供了该字段，new_group 函数会立即尝试为该设备初始化通信后端。返回值：一个分布式组句柄，可用于集体操作；如果当前节点不属于该进程组，则返回 GroupMember.NON_GROUP_MEMBER。注意：use_local_synchronization 不适用于 MPI。注意：虽然当集群规模较大且进程组规模较小时，设置 use_local_synchronization=True 可显著提升性能，但由于非成员节点不会参与 group barrier() 操作，因此会改变集群的行为，使用时需格外谨慎。注意：如果每个节点都创建多个重叠的进程组，设置 use_local_synchronization=True 可能会导致死锁。为避免出现此类问题，请确保所有进程的创建顺序遵循相同的全局顺序。torch.distributed.get_group_rank(group, global_rank)[source]# 将全局序号转换为组内序号。global_rank必须属于该组，否则将引发RuntimeError异常。参数：group（ProcessGroup）——用于确定相对序号的进程组；global_rank（int）——需要查询的全局序号。返回值：该global_rank在对应组中的组内序号。返回类型：int。注意：在默认进程组上调用此函数会返回其自身的序号。torch.distributed.get_global_rank(group, group_rank)[source]# 将组内序号转换为全局序号。group_rank必须属于该组，否则将引发RuntimeError异常。参数：group（ProcessGroup）——用于确定全局序号的进程组；group_rank（int）——需要查询的组内序号。返回值：该group_rank在对应组中的全局序号。返回类型：int。注意：在默认进程组上调用此函数会返回其自身的序号。torch.distributed.get_process_group_ranks(group)[source]# 获取与指定进程组相关的所有序号。参数：group（Optional[ProcessGroup]）——用于获取所有序号的进程组；若未指定，则使用默认进程组。返回值：按组内序号排序的全局序号列表。返回类型：list[int]。DeviceMesh# DeviceMesh是一种更高级别的抽象层，用于管理进程组（或NCCL通信组件）。该功能让用户能够轻松创建节点间及节点内的进程组，而无需担心如何为不同的子进程组正确设置进程等级，同时还能帮助用户便捷地管理这些分布式进程组。可通过 init_device_mesh() 函数来创建新的 DeviceMesh，该函数需要一个描述设备拓扑结构的网格结构作为参数。其函数定义为：class torch.distributed.device_mesh.DeviceMesh(device_type, mesh, *, mesh_dim_names=None, backend_override=None, _init_backend=True)[source]# DeviceMesh 表示由设备构成的网格结构，设备的布局可以用 n 维数组来表示，该数组中的每个值对应默认进程组中各个进程的全球编号。DeviceMesh 可用于在集群中建立 N 维设备连接，并管理支持 N 维并行计算的进程组。通信可以在 DeviceMesh 的各个维度上独立进行。如果用户在初始化 DeviceMesh 之前已通过 torch.cuda.set_device 指定了设备，那么 DeviceMesh 会尊重这一选择；若用户未提前指定设备，它则会自动为当前进程选择/设置设备。需要注意的是，手动选择设备必须在初始化 DeviceMesh 之前完成。此外，当与 DTensor API 结合使用时，DeviceMesh 还可以用作上下文管理器。需注意，DeviceMesh 遵循 SPMD 编程模型，这意味着集群中的所有进程/等级上运行的都是相同的 PyTorch Python 程序。因此，用户需确保用于描述设备布局的网格数组在所有节点上保持一致。若网格结构不一致，将导致程序无声挂起。参数说明：device_type（str）——网格中的设备类型，目前支持“cpu”和“cuda/cuda-like”。mesh（ndarray）——用于描述设备布局的多维数组或整数张量，其中的编号为默认进程组的全局编号。返回值：表示设备布局的DeviceMesh对象。返回类型为DeviceMesh。以下程序以SPMD方式在每个进程/节点上运行。在本例中，共有2台主机，每台主机配备4块GPU。对网格的第一维度进行聚合操作时，会在列（0, 4）、……以及（3, 7）之间进行计算；而对网格的第二维度进行聚合操作时，则会在行（0, 1, 2, 3）和（4, 5, 6, 7）之间进行计算。示例代码如下：>>> from torch.distributed.device_mesh import DeviceMesh >>> >>> # 将设备网格初始化为(2, 4)的格式，以表示跨主机（维度0）及主机内部（维度1）的拓扑结构。 >>> mesh = DeviceMesh(device_type="cuda", mesh=[[0, 1, 2, 3],[4, 5, 6, 7]]) static from_group(group, device_type, mesh=None, *, mesh_dim_names=None)[source]# 根据现有的ProcessGroup或ProcessGroup列表，利用device_type参数构建DeviceMesh对象。所生成的设备网格的维度数与传入的组数相同。例如，若仅传入一个进程组，则生成的DeviceMesh为1维网格。如果传入2个进程组列表，生成的DeviceMesh将为二维网格结构。若传入的进程组数量超过2个，则必须同时指定mesh和mesh_dim_names参数。进程组的传递顺序决定了网格的拓扑结构——例如，第一个进程组将对应DeviceMesh的第0维。传入的网格张量维度数必须与进程组数量一致，且其各维的顺序也需与进程组的传递顺序相匹配。参数说明：group（ProcessGroup或list[ProcessGroup]）——现有的进程组或现有进程组的列表；device_type（str）——网格对应的设备类型，目前支持“cpu”和“cuda/cuda-like”两种类型，不允许传入包含GPU索引的类型，如“cuda:0”；mesh（torch.Tensor或ArrayLike，可选）——用于描述设备布局的多维数组或整数张量，其中的ID为默认进程组的全局ID，默认值为None；mesh_dim_names（tuple[str]，可选）——用于为描述设备布局的多维数组的各维指定名称的元组，其长度必须与mesh_shape的长度一致，且元组中的字符串需唯一，默认值为None。返回值：表示设备布局的DeviceMesh对象。返回类型为DeviceMesh；get_all_groups()——返回所有网格维度对应的进程组列表。[source]#该方法会返回一个ProcessGroup对象列表。返回类型为list[torch.distributed.distributed_c10d.ProcessGroup]。get_coordinate()【来源】# 返回当前进程节点相对于网格各维度的相对索引。如果该进程节点不属于该网格，则返回None。返回类型为Optional[list[int]]。get_group(mesh_dim=None)【来源】# 返回由mesh_dim指定的那个ProcessGroup；如果未指定mesh_dim且DeviceMesh为一维结构，则返回网格中的唯一ProcessGroup。参数：mesh_dim（str/python:int，可选）——可以是网格维度的名称或索引，默认值为None。返回类型为ProcessGroup。get_local_rank(mesh_dim=None)【来源】# 返回DeviceMesh中指定mesh_dim对应的本地进程排名。参数：mesh_dim（str/python:int，可选）——可以是网格维度的名称或索引，默认值为None。返回类型为int，表示对应的本地进程排名。以下程序以SPMD方式在每个进程/节点上运行。在此示例中，共有2台主机，每台主机配备4块GPU。在进程排名0、1、2、3上调用mesh_2d.get_local_rank(mesh_dim=0)时会返回0；在进程排名4、5、6、7上调用该函数则会返回1。在进程排名0、4上调用mesh_2d.get_local_rank(mesh_dim=1)时会返回0；在进程排名1、5上调用该函数则会返回1；在进程排名2、6上调用该函数则会返回2。在排名为 3 和 7 的节点上调用 mesh_2d.get_local_rank(mesh_dim=1) 函数时，其返回值均为 3。示例如下：>>> from torch.distributed.device_mesh import DeviceMesh >>> >>> # 将设备网格初始化为 (2, 4) 的结构，用以表示跨主机（维度 0）以及主机内部（维度 1）的拓扑结构。 >>> mesh = DeviceMesh(device_type="cuda", mesh=[[0, 1, 2, 3],[4, 5, 6, 7]]) get_rank()[source]# 返回当前的全局排名。返回类型为整数。点对点通信# torch.distributed.send(tensor, dst=None, group=None, tag=0, group_dst=None)[source]# 同步发送一个张量。注意：NCCL 后端不支持使用 tag 参数。参数说明：tensor（Tensor）——需发送的张量；dst（int）——全局进程组中的目标排名（忽略 group 参数）。目标排名不能与当前进程的排名相同；group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认的进程组；tag（int，可选）——用于将发送操作与远程接收操作匹配的标签；group_dst（int，可选）——所在进程组中的目标排名。不能同时指定 dst 和 group_dst。torch.distributed.recv(tensor, src=None, group=None, tag=0, group_src=None)[source]# 同步接收一个张量。注意：NCCL 后端不支持使用 tag 参数。参数说明：tensor（Tensor）——用于存储接收到的数据的张量；src（int，可选）——全局进程组中的源排名（忽略 group 参数）。若未指定，则会从任意进程接收数据；group（ProcessGroup，可选）——要操作的进程组。如果未指定，则使用默认的进程组。tag（整数，可选）——用于将发送操作与远程接收操作进行匹配的标签；group_src（整数，可选）——所在进程组中的目标节点编号。不能同时指定src和group_src。若当前节点不属于该进程组，则返回-1作为发送节点的编号。返回类型：isend()和irecv()在被调用时会返回分布式请求对象。通常情况下，这类对象的类型并未明确规定，因为它们绝不应被手动创建，但可以确定的是它们都支持两个方法：is_completed()——若操作已完成则返回True；wait()——会阻塞当前进程，直到操作完成。一旦is_completed()返回结果，就必然会返回True。torch.distributed.isend(tensor, dst=None, group=None, tag=0, group_dst=None)[来源]# 异步发送张量。警告：在请求完成之前修改张量会导致行为不可预测。警告：NCCL后端不支持tag参数。与会阻塞操作的send不同，isend允许src等于dst节点编号，即向自身发送数据。参数：tensor（Tensor）——要发送的张量；dst（整数）——全局进程组中的目标节点编号（与group参数无关）；group（ProcessGroup，可选）——要操作的进程组。如果未指定，则使用默认的进程组；tag（整数，可选）——用于将发送操作与远程接收操作进行匹配的标签；group_dst（整数，可选）——所在进程组中的目标节点编号。不能同时指定dst和group_dst。返回值：一个分布式请求对象。如果不属于该进程组，则返回 None。返回类型：Optional[Work]  
torch.distributed.irecv(tensor, src=None, group=None, tag=0, group_src=None)[来源]  
# 异步接收张量。警告：NCCL 后端不支持 tag 参数。与阻塞式的 recv 不同，irecv 允许 src 等于 dst 的进程编号，即从自身接收数据。  
参数：  
tensor（Tensor）——用于存储接收到的数据的张量。  
src（int，可选）——全局进程组中的源进程编号（忽略 group 参数）。若未指定，则从任意进程接收数据。  
group（ProcessGroup，可选）——要操作的进程组。如果为 None，则使用默认的进程组。  
tag（int，可选）——用于与远程发送方进行匹配的标签。  
group_src（int，可选）——目标进程组中的目标进程编号。不能同时指定 src 和 group_src。  
返回值：一个分布式请求对象；如果不属于该进程组，则返回 None。  

返回类型：Optional[Work]  
torch.distributed.send_object_list(object_list, dst=None, group=None, device=None, group_dst=None, use_batch=False)[来源]  
# 同步发送 object_list 中的可序列化对象。与 send() 类似，但可以传递 Python 对象。注意，要发送的对象列表中的所有对象都必须是可序列化的。  
参数：  
object_list（List[Any]）——需要发送的输入对象列表。每个对象都必须是可序列化的。接收方需提供大小相同的对象列表。  
dst（int）——目标进程编号，即要将 object_list 发送到的进程。目标等级是根据全局进程组来确定的（与 group 参数无关）。group（可选[ProcessGroup]）——(ProcessGroup，可选)：需要操作的进程组。若未指定，则使用默认的进程组，其值为 None。device（torch.device，可选）——若非 None，则会将对象序列化并转换为张量，然后在发送前将其移至指定设备上。默认值为 None。group_dst（int，可选）——该进程组在目标等级中的位置。必须仅指定 dst 或 group_dst 中的一个，不可同时指定。use_batch（bool，可选）——若为 True，则使用批量点对点操作而非常规的发送操作。这样无需初始化二级通信器，而是直接利用现有的整个进程组通信器。具体用法及相关要求请参见 batch_isend_irecv。默认值为 False。该函数返回 None。注意：对于基于 NCCL 的进程组，必须在通信开始之前将对象的内部张量表示移至 GPU 设备上。此时所使用的设备由 torch.cuda.current_device() 提供，用户有责任通过 torch.cuda.set_device() 确保每个等级都能拥有独立的 GPU。警告：对象集合操作存在诸多严重的性能与可扩展性限制，详情请参阅“对象集合操作”相关内容。警告：send_object_list() 函数会隐式使用 pickle 模块，而该模块存在安全风险。恶意构造的 pickle 数据在反序列化时可能会执行任意代码，因此仅建议对可信的数据使用此函数。警告：使用 GPU 张量调用 send_object_list() 的功能支持不佳且效率低下，因为张量在传递过程中需要先被序列化（pickled），从而导致 GPU 与 CPU 之间的数据传输。建议改用 send() 函数。示例如下：

>>> # 注意：此处省略了每个进程节点的进程组初始化步骤。
>>> import torch.distributed as dist
>>> # 假设后端不是 NCCL
>>> device = torch.device("cpu")
>>> if dist.get_rank() == 0:
>>>     # 假设全局进程组大小为 2
>>>     objects = ["foo", 12, {1: 2}]  # 任何可序列化的对象
>>>     dist.send_object_list(objects, dst=1, device=device)
>>> else:
>>>     objects = [None, None, None]
>>>     dist.recv_object_list(objects, src=0, device=device)
>>> 
>>> objects
['foo', 12, {1: 2}]

torch.distributed.recv_object_list(object_list, src=None, group=None, device=None, group_src=None, use_batch=False)
[来源]：该函数可同步接收 object_list 中的可序列化对象。其功能与 recv() 类似，但能够接收 Python 对象。参数说明：
- object_list（List[Any]）：需接收的对象列表。必须提供一个长度与待发送列表相同的大小列表。
- src（int，可选）：用于接收 object_list 的源进程节点编号。该编号基于全局进程组确定（与 group 参数无关）；若设置为 None，则可从任意进程节点接收数据。默认值为 None。
- group（Optional[ProcessGroup]）：可选的进程组对象。若为 None，则使用默认进程组。默认值为 None。
- device（torch.device，可选）：若非 None，则在该设备上接收数据。默认值为 None。group_src（整数，可选）——表示在组中的目标等级。不能同时指定 src 和 group_src。use_batch（布尔值，可选）——若设置为 True，则使用批量点对点操作而非常规发送操作。这样无需初始化二级通信器，而是直接使用整个组的通信器。有关用法及前提条件，请参阅 batch_isend_irecv。默认值为 False。函数返回发送方等级；若该等级不属于该组，则返回 -1。若属于该组，则 object_list 将包含来自发送方等级的已发送对象。注意：对于基于 NCCL 的进程组，必须在通信开始前将对象的内部张量表示移至 GPU 设备上。此时所使用的设备由 torch.cuda.current_device() 指定，用户有责任通过 torch.cuda.set_device() 确保每个等级都拥有独立的 GPU。警告：对象集合操作存在诸多严重的性能与可扩展性限制，详情请参阅“对象集合操作”相关内容。警告：recv_object_list() 会隐式使用 pickle 模块，而该模块存在安全风险——恶意构造的 pickle 数据在反序列化时可能会执行任意代码。仅可使用可信的数据调用此函数。警告：使用 GPU 张量调用 recv_object_list() 的支持程度较低且效率低下，因为需要先将张量序列化为字节流以实现 GPU 与 CPU 之间的数据传输。建议改用 recv() 函数。示例::>>> # 注意：此处未展示每个进程节点上的进程组初始化步骤。 >>> import torch.distributed as dist >>> # 假设后端不是NCCL >>> device = torch.device("cpu") >>> if dist.get_rank() == 0: >>> # 假设节点总数为2。 >>> objects = ["foo", 12, {1: 2}] # 任何可序列化的对象 >>> dist.send_object_list(objects, dst=1, device=device) >>> else: >>> objects = [None, None, None] >>> dist.recv_object_list(objects, src=0, device=device) >>> objects ['foo', 12, {1: 2}] torch.distributed.batch_isend_irecv(p2p_op_list)[source]# 异步发送或接收一批张量，并返回相应的请求列表。该函数会依次处理p2p_op_list中的每个操作，然后返回对应的请求对象。目前支持NCCL、Gloo和UCC后端。参数 p2p_op_list (list[torch.distributed.distributed_c10d.P2POp]) – 一个包含点对点操作类型的列表（每个操作的类型均为torch.distributed.P2POp）。列表中isend/irecv操作的顺序很重要，必须与远程端的对应操作顺序保持一致。返回值 通过调用op_list中的相应操作所返回的分布式请求对象列表。返回类型列表：[torch.distributed.distributed_c10d.Work]  
示例：  
>>> send_tensor = torch.arange(2, dtype=torch.float32) + 2 * rank  
>>> recv_tensor = torch.randn(2, dtype=torch.float32)  
>>> send_op = dist.P2POp(dist.isend, send_tensor, (rank + 1) % world_size)  
>>> recv_op = dist.P2POp(  
...     dist.irecv, recv_tensor, (rank - 1 + world_size) % world_size  
...)  
>>> reqs = batch_isend_irecv([send_op, recv_op])  
>>> for req in reqs:  
>>>     req.wait()  
>>>   
>>> recv_tensor  
tensor([2, 3])  # 号码为 0 的节点  
tensor([0, 1])  # 号码为 1 的节点  

注意：当此 API 与 NCCL PG 后端一起使用时，用户必须使用 torch.cuda.set_device 设置当前 GPU 设备，否则可能会导致程序意外挂起。此外，如果该 API 是传递给 dist.P2POp 的组中的第一个集合调用，则组内的所有节点都必须参与此次调用；否则其行为是未定义的。若该 API 调用并非组中的第一个集合调用，则允许仅对组中部分节点执行批量 P2P 操作。  

类定义：  
torch.distributed.P2POp(op, tensor, peer=None, group=None, tag=0, group_peer=None)  
[来源]  
# 用于为 batch_isend_irecv 构建点对点通信操作的类。该类用于确定 P2P 操作的类型、通信缓冲区、对端节点编号、进程组以及标签。此类实例会被传递给 batch_isend_irecv 以实现点对点通信。  
参数：  
op (Callable) – 用于向对端进程发送数据或从其对端进程接收数据的函数。该操作类型只能是 torch.distributed.isend 或 torch.distributed.irecv。tensor（Tensor）——需要发送或接收的张量。peer（int，可选）——目标节点或源节点的排名。group（ProcessGroup，可选）——要操作的进程组；若未指定，则使用默认进程组。tag（int，可选）——用于将发送操作与接收操作关联的标签。group_peer（int，可选）——目标节点或源节点的排名。同步与异步集合操作# 根据传递给集合操作函数的 async_op 参数设置，每个集合操作函数都支持以下两种操作模式：同步操作——默认模式，即当 async_op 设为 False 时。此时函数返回时，可确保集合操作已经完成。对于 CUDA 操作而言，由于其为异步操作，因此无法保证 CUDA 操作一定已完成。而对于 CPU 集合操作，后续使用该集合操作结果的函数调用仍会按预期工作。对于 CUDA 集合操作，同一 CUDA 流上的函数调用也会按预期运行；但在不同流环境下运行时，用户需自行处理同步问题。有关 CUDA 语义（如流同步）的详细信息，请参阅“CUDA 语义”章节。可通过以下脚本查看 CPU 操作与 CUDA 操作在这些语义方面的差异示例。异步操作——当 async_op 设为 True 时。此时集合操作函数会返回一个分布式请求对象。通常情况下，无需手动创建此类对象，它必定支持两种方法：is_completed()——针对CPU集合操作，若操作已完成则返回True；而对于CUDA操作，则在操作已成功提交至CUDA流且其输出可在默认流上直接使用而无需进一步同步时返回True。wait()——对于CPU集合操作，该函数会阻塞进程直至操作完成；而对于CUDA集合操作，则会阻塞当前正在运行的CUDA流直至操作完成（但不会阻塞CPU）。get_future()——返回torch._C.Future对象。该功能支持NCCL，同时也适用于GLOO和MPI上的大多数操作，但对点对点操作除外。注意：随着我们不断采用Future机制并整合相关API，get_future()函数可能会逐渐被废弃。示例：以下代码可作为使用分布式集合操作时理解CUDA操作语义的参考。当在不同 CUDA 流上使用集合输出功能时，显然需要同步操作：# 代码在每个进程上独立运行。dist.init_process_group("nccl", rank=rank, world_size=2) output = torch.tensor([rank]).cuda(rank) s = torch.cuda.Stream() handle = dist.all_reduce(output, async_op=True) # 调用 wait 可确保操作被放入队列，但并不一定意味着操作已经完成。handle.wait() # 在非默认流上使用结果。with torch.cuda.stream(s): s.wait_stream(torch.cuda.default_stream()) output.add_(100) if rank == 0: # 如果省略了显式的 wait_stream 调用，那么下面的输出结果将会是 1 或 101，具体数值取决于在加法操作完成后，all_reduce 操作是否已经修改了该值。print(output) 集合函数# torch.distributed.broadcast(tensor, src=None, group=None, async_op=False, group_src=None)[来源]# 将张量广播到整个进程组。参与集合操作的所有进程中的张量元素数量必须相同。参数 tensor (Tensor) – 要发送的数据；如果 src 指定的是当前进程的排名，则该参数为要发送的数据，否则用于存储接收到的数据。src (int) – 全局进程组中的源进程排名（与 group 参数无关）。group (ProcessGroup, 可选) – 需要操作的进程组。如果未指定，则使用默认进程组。async_op (bool, 可选) – 该操作是否为异步操作。group_src (int) – 所属进程组中的源进程排名。必须仅指定 group_src 或 src 中的一个，不能同时指定两个。如果 async_op 设为 True，则返回异步任务处理标识符；否则返回 None。函数 torch.distributed.broadcast_object_list(object_list, src=None, group=None, device=None, group_src=None)[source] 的功能是将 object_list 中的可序列化对象广播到整个进程组。该函数与 broadcast() 类似，但允许传递 Python 对象。需要注意的是，只有可序列化的对象才能被广播。参数说明：object_list（List[Any]）——需广播的输入对象列表，所有对象都必须支持序列化。仅源节点上的对象会被广播，但各节点提供的列表长度必须一致。src（int）——用于广播 object_list 的源节点编号，该编号基于全局进程组确定（与 group 参数无关）。group（Optional[ProcessGroup]）——可选的进程组对象，指定要操作的进程组；若为 None，则使用默认进程组，默认值为 None。device（torch.device，可选）——若非 None，系统会将对象序列化并转换为张量，然后再将其移动到指定设备上之后进行广播，默认值为 None。group_src（int）——进程组内的源节点编号。不得同时指定 group_src 和 src，只能选择其一。若当前节点属于该进程组，则 object_list 中将包含来自源节点的广播对象。注意：对于基于 NCCL 的进程组，对象的内部张量表示形式必须在通信开始前被移动到 GPU 设备上。在此情况下，所使用的设备可通过 torch.cuda.current_device() 获取。用户有责任通过 torch.cuda.set_device() 确保每个进程都能分配到独立的 GPU。需要注意的是，该 API 与 broadcast() 这一集合操作略有不同，因为它不提供异步操作句柄，因此属于阻塞调用。警告：对象集合操作存在诸多严重的性能与可扩展性限制，详情请参阅相关文档。警告：broadcast_object_list() 会隐式使用 pickle 模块，而该模块存在安全风险——有人可能构造出恶意 pickle 数据，在反序列化时执行任意代码。因此，请仅对可信的数据调用此函数。警告：若使用 GPU 张量调用 broadcast_object_list()，由于需要先将张量序列化为字节流再进行 CPU -> GPU 的数据传输，该操作不仅支持不佳且效率低下。建议优先使用 broadcast() 函数。示例::>>> # 注意：此处省略了每个进程组的初始化步骤。 >>> import torch.distributed as dist >>> if dist.get_rank() == 0: >>> # 假设世界大小为3。 >>> objects = ["foo", 12, {1: 2}] # 任何可序列化的对象 >>> else: >>> objects = [None, None, None] >>> # 假设后端不是NCCL >>> device = torch.device("cpu") >>> dist.broadcast_object_list(objects, src=0, device=device) >>> objects ['foo', 12, {1: 2}] torch.distributed.all_reduce(tensor, op=<RedOpType.SUM: 0>, group=None, async_op=False)[source]# 该函数会将张量数据在所有机器上汇总，使得所有进程最终都能获得相同的结果。调用此函数后，所有进程中的张量数据将完全一致。该功能支持复杂的张量类型。参数 tensor（Tensor）——集合操作的输入与输出。该函数会原地执行操作。op（可选）——来自torch.distributed.ReduceOp枚举的值之一，用于指定用于逐元素求和的操作类型。group（ProcessGroup，可选）——要操作的进程组。如果为None，则使用默认的进程组。async_op（bool，可选）——该操作是否为异步操作。若将async_op设置为True，则会返回一个异步操作处理对象。如果既不是异步操作，也不属于某个进程组，则无需执行任何操作。示例 >>> # 下面的所有张量均为 torch.int64 类型。 >>> # 我们有 2 个进程组，共 2 个节点。 >>> device = torch.device(f"cuda:{rank}") >>> tensor = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank >>> tensor tensor([1, 2], device='cuda:0') # 节点 0 的张量 tensor([3, 4], device='cuda:1') # 节点 1 的张量 >>> dist.all_reduce(tensor, op=ReduceOp.SUM) >>> tensor tensor([4, 6], device='cuda:0') # 节点 0 的张量 tensor([4, 6], device='cuda:1') # 节点 1 的张量 >>> # 下面的所有张量均为 torch.cfloat 类型。 >>> # 我们有 2 个进程组，共 2 个节点。 >>> tensor = torch.tensor( ... [1 + 1j, 2 + 2j], dtype=torch.cfloat, device=device ... ) + 2 * rank * (1 + 1j) >>> tensor tensor([1.+1.j, 2.+2.j], device='cuda:0') # 节点 0 的张量 tensor([3.+3.j, 4.+4.j], device='cuda:1') # 节点 1 的张量 >>> dist.all_reduce(tensor, op=ReduceOp.SUM) >>> tensor tensor([4.+4.j, 6.+6.j], device='cuda:0') # 节点 0 的张量 tensor([4.+4.j, 6.+6.j], device='cuda:1') # 节点 1 的张量 torch.distributed.reduce(tensor, dst=None, op=<RedOpType.SUM: 0>, group=None, async_op=False, group_dst=None)[source]该函数用于在所有机器上对张量数据进行聚合操作。最终结果仅会由全局进程组中指定为 dst 的节点接收。参数 tensor（Tensor）——集合操作的输入与输出，该函数支持就地操作。dst（int）——全局进程组中的目标节点编号（与 group 参数无关）。op（可选）——来自 torch.distributed.ReduceOp 枚举的值之一。指定用于元素级求和的运算方式。group（ProcessGroup，可选）——要操作的进程组。如果为None，则使用默认的进程组。async_op（bool，可选）——该运算是否应为异步运算。group_dst（int）——所在进程组中的目标秩。必须指定group_dst和dst中的一个，但不能同时指定两个。如果async_op设置为True，则返回异步任务处理对象；否则返回None。参考torch.distributed.all_gather(tensor_list, tensor, group=None, async_op=False)【来源】# 从整个进程组中收集张量并放入列表中。支持复杂形状及大小不等的张量。参数tensor_list（list[Tensor]）——输出列表，其中应包含尺寸合适的张量，以便用于集体运算的输出；也支持大小不等的张量。tensor（Tensor）——当前进程要广播的张量。group（ProcessGroup，可选）——要操作的进程组。如果为None，则使用默认的进程组。async_op（bool，可选）——该运算是否应为异步运算。如果async_op设置为True，则返回异步任务处理对象；否则返回None。示例>>> # 下面的所有张量均为torch.int64数据类型。>>> # 我们有2个进程组，共2个秩。>>> device = torch.device(f"cuda:{rank}") >>> tensor_list = [ ... torch.zeros(2, dtype=torch.int64, device=device) for _ in range(2) ... ] >>> tensor_list [tensor([0, 0], device='cuda:0'), tensor([0, 0], device='cuda:0')] # 秩为0的节点 [tensor([0, 0], device='cuda:1'), tensor([0, 0],device='cuda:1')] # 排序为 1 >>> tensor = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank >>> tensor
tensor([1, 2], device='cuda:0') # 排序为 0
tensor([3, 4], device='cuda:1') # 排序为 1
>>> dist.all_gather(tensor_list, tensor)
>>> tensor_list
[tensor([1, 2], device='cuda:0'), tensor([3, 4], device='cuda:0')] # 排序为 0
[tensor([1, 2], device='cuda:1'), tensor([3, 4], device='cuda:1')] # 排序为 1
>>> # 下方所有的张量均为 torch.cfloat 数据类型。
>>> # 当前系统共有 2 个进程组、2 个排序节点。
>>> tensor_list = [ ... torch.zeros(2, dtype=torch.cfloat, device=device) for _ in range(2) ... ]
>>> tensor_list
[tensor([0.+0.j, 0.+0.j], device='cuda:0'), tensor([0.+0.j, 0.+0.j], device='cuda:0')] # 排序为 0
[tensor([0.+0.j, 0.+0.j], device='cuda:1'), tensor([0.+0.j, 0.+0.j], device='cuda:1')] # 排序为 1
>>> tensor = torch.tensor( ... [1 + 1j, 2 + 2j], dtype=torch.cfloat, device=device ... ) + 2 * rank * (1 + 1j) >>> tensor
tensor([1.+1.j, 2.+2.j], device='cuda:0') # 排序为 0
tensor([3.+3.j, 4.+4.j], device='cuda:1') # 排序为 1
>>> dist.all_gather(tensor_list, tensor)
>>> tensor_list
[tensor([1.+1.j, 2.+2.j], device='cuda:0'), tensor([3.+3.j, 4.+4.j], device='cuda:0')] # 排序为 0
[tensor([1.+1.j, 2.+2.j], device='cuda:1'), tensor([3.+3.j, 4.+4.j], device='cuda:1')] # 排序为 1
torch.distributed.all_gather_into_tensor(output_tensor, input_tensor, group=None, async_op=False)
[来源]# 从所有排序节点收集张量，并将它们整合到一个输出张量中。该函数要求每个进程中的所有张量尺寸必须相同。parameters  
output_tensor（Tensor）——用于存储所有节点对应的张量元素的输出张量。其尺寸必须符合以下形式之一：(i) 沿主维度将所有输入张量进行拼接；关于“拼接”的定义，请参阅torch.cat()函数；(ii) 沿主维度将所有输入张量进行堆叠；关于“堆叠”的定义，请参阅torch.stack()函数。以下的示例可更直观地说明所支持的输出形式。  

input_tensor（Tensor）——需要从当前节点收集的张量。与all_gather API不同，该API中的所有输入张量在各个节点上的尺寸必须完全相同。  

group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认的进程组。  

async_op（bool，可选）——该操作是否为异步操作。若将async_op设置为True，则会返回一个异步操作处理对象。如果既不是异步操作，也不属于某个进程组，则无需执行任何操作。示例 >>> # 下述所有张量均为 torch.int64 数据类型，且位于 CUDA 设备上。 >>> # 我们有两组进程。 >>> device = torch.device(f"cuda:{rank}") >>> tensor_in = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank >>> tensor_in tensor([1, 2], device='cuda:0') # 第 0 组进程 tensor([3, 4], device='cuda:1') # 第 1 组进程 >>> # 以拼接形式输出 >>> tensor_out = torch.zeros(world_size * 2, dtype=torch.int64, device=device) >>> dist.all_gather_into_tensor(tensor_out, tensor_in) >>> tensor_out tensor([1, 2, 3, 4], device='cuda:0') # 第 0 组进程 tensor([1, 2, 3, 4], device='cuda:1') # 第 1 组进程 >>> # 以堆叠形式输出 >>> tensor_out2 = torch.zeros(world_size, 2, dtype=torch.int64, device=device) >>> dist.all_gather_into_tensor(tensor_out2, tensor_in) >>> tensor_out2 tensor([[1, 2], [3, 4]], device='cuda:0') # 第 0 组进程 tensor([[1, 2], [3, 4]], device='cuda:1') # 第 1 组进程 torch.distributed.all_gather_object(object_list, obj, group=None)[来源]# 从整个进程组中收集可序列化的对象并放入列表中。该函数与 all_gather() 类似，但可以传入 Python 对象。需要注意的是，被收集的对象必须是可序列化的。参数 object_list (list[Any]) – 输出列表。其大小应与本次集合操作所涉及的进程组规模一致，并将包含收集到的结果。obj (Any) – 需要从当前进程广播的可序列化 Python 对象。group (ProcessGroup, 可选) – 要操作的进程组。如果未指定，则使用默认的进程组。默认值为 None，函数也会返回 None。如果调用进程属于该组，则集体操作的结果将会被写入输入的 object_list 中；若调用进程不属于该组，则传入的 object_list 将保持不变。注意：此 API 与 all_gather() 集体操作略有不同，因为它不提供异步操作接口，因此属于阻塞式调用。注意：对于基于 NCCL 的处理组，在进行通信之前，对象的内部张量表示必须先被移至 GPU 设备上。此时所使用的设备可通过 torch.cuda.current_device() 获取，用户有责任通过 torch.cuda.set_device() 确保每个进程都能使用独立的 GPU。警告：对象集体操作存在诸多严重的性能与可扩展性限制，详情请参阅“对象集体操作”相关内容。警告：all_gather_object() 会隐式使用 pickle 模块，而该模块存在安全风险——恶意构造的 pickle 数据在反序列化时可能会执行任意代码。请仅对可信的数据调用此函数。警告：使用 GPU 张量调用 all_gather_object() 的兼容性较差且效率低下，因为需要先将张量序列化为 pickle 格式再进行 CPU 与 GPU 之间的数据传输。建议优先使用 all_gather()。示例::>>> # 注意：此处省略了每个进程内的进程组初始化步骤。 >>> import torch.distributed as dist >>> # 假设全局进程数为3。 >>> gather_objects = ["foo", 12, {1: 2}] # 任何可序列化的对象 >>> output = [None for _ in gather_objects] >>> dist.all_gather_object(output, gather_objects[dist.get_rank()]) >>> output ['foo', 12, {1: 2}] torch.distributed.gather(tensor, gather_list=None, dst=None, group=None, async_op=False, group_dst=None)[来源]# 在单个进程中收集一系列张量。该函数要求所有进程中的张量尺寸必须相同。 参数 tensor (Tensor) – 输入张量。 gather_list (list[Tensor], 可选) – 用于收集数据的、尺寸相同的张量列表（默认值为None，必须在目标进程上指定）。 dst (int, 可选) – 全局进程组中的目标进程序号（与group参数无关）。若同时指定dst和group_dst则为无效值，此时默认为目标进程序号0。 group (ProcessGroup, 可选) – 需要操作的进程组。若未指定，则使用默认的进程组。 async_op (bool, 可选) – 是否将此操作设为异步操作。 group_dst (int, 可选) – 进程组内的目标进程序号。同时指定dst和group_dst是无效的。 返回值 若async_op设置为True，则返回异步操作处理对象；若非异步操作或不属于该进程组，则返回None。 注意 请注意，gather_list中的所有张量尺寸必须一致。示例::>>> # 我们有2个进程组，每个进程组包含2个进程。 >>> tensor_size = 2 >>> device = torch.device(f'cuda:{rank}') >>> tensor = torch.ones(tensor_size, device=device) + rank >>> if dist.get_rank() == 0: >>> gather_list = [torch.zeros_like(tensor, device=device) for i in range(2)] >>> else: >>> gather_list = None >>> dist.gather(tensor, gather_list, dst=0) >>> # 号码为0的进程将获得聚合后的数据。 >>> gather_list [tensor([1., 1.], device='cuda:0'), tensor([2., 2.], device='cuda:0')] # 号码为0的进程：None # 号码为1的进程：torch.distributed.gather_object(obj, object_gather_list=None, dst=None, group=None, group_dst=None)[来源]# 在单个进程中从整个进程组中聚合可序列化的对象。该函数与gather()类似，但可以传入Python对象。需要注意的是，被聚合的对象必须是可序列化的。参数 obj (Any) – 输入对象，必须为可序列化类型。object_gather_list (list[Any]) – 输出列表。在目标进程上，其大小应与本次聚合操作涉及的进程组大小一致，并包含聚合结果；非目标进程上的该参数应为None（默认值为None）。dst (int, 可选) – 全局进程组中的目标进程编号（与group参数无关）。如果同时指定dst和group_dst，则默认使用全局进程编号0。group (Optional[ProcessGroup]) – （可选）要操作的进程组。如果未指定，则使用默认的进程组，默认值为None。group_dst (int, 可选) – 所属进程组中的目标进程编号。不能同时指定dst和group_dst。返回值：None。在目标节点上，object_gather_list 将包含集体操作的输出结果。需要注意的是，该 API 与 gather collective 略有不同——它不提供异步操作句柄，因此属于阻塞式调用。另外，对于基于 NCCL 的处理组，在进行通信之前必须先将对象的内部张量表示移至 GPU 设备上。此时所使用的设备可通过 torch.cuda.current_device() 获取，用户有责任通过 torch.cuda.set_device() 确保每个节点都能拥有独立的 GPU。警告：对象集体操作存在诸多严重的性能与可扩展性限制，详情请参阅“对象集体操作”相关章节。警告：gather_object() 会隐式使用 pickle 模块，而该模块存在安全风险——恶意构造的 pickle 数据在反序列化时可能会执行任意代码。因此，请仅对可信的数据调用此函数。警告：使用 GPU 张量调用 gather_object() 的兼容性较差且效率低下，因为该操作需要先将张量序列化为 pickle 格式，从而导致 GPU 与 CPU 之间的数据传输。建议优先使用 gather() 函数。示例::>>> # 注意：此处省略了每个进程节点上的进程组初始化步骤。 >>> import torch.distributed as dist >>> # 假设世界大小为 3。 >>> gather_objects = ["foo", 12, {1: 2}] # 任何可序列化的对象 >>> output = [None for _ in gather_objects] >>> dist.gather_object( ... gather_objects[dist.get_rank()], ... output if dist.get_rank() == 0 else None, ... dst=0 ... ) >>> # 在进程节点 0 上 >>> output ['foo', 12, {1: 2}] torch.distributed.scatter(tensor, scatter_list=None, src=None, group=None, async_op=False, group_src=None)[source]# 将一组张量分发到进程组中的所有进程。每个进程将恰好接收一个张量，并将其数据存储在该张量参数中。该函数支持复杂张量。 参数 tensor (Tensor) – 输出张量。 scatter_list (list[Tensor]) – 需要分发的张量列表（默认值为 None，必须在源进程节点上指定）。 src (int) – 全局进程组中的源进程节点编号（与 group 参数无关）。如果同时指定 src 和 group_src，则以全局编号 0 为默认值。 group (ProcessGroup, 可选) – 需要操作的进程组。如果未指定，则使用默认的进程组。 async_op (bool, 可选) – 是否将此操作设为异步操作。 group_src (int, 可选) – 进程组中的源进程节点编号。同时指定 src 和 group_src 是无效的。 返回值 如果设置 async_op 为 True，则返回异步操作处理对象；如果未设置异步操作或当前进程不属于该进程组，则返回 None。 注意 注意：scatter_list 中的所有张量尺寸必须相同。示例::>>> # 注意：此处省略了各节点上的进程组初始化步骤。 >>> import torch.distributed as dist >>> tensor_size = 2 >>> device = torch.device(f'cuda:{rank}') >>> output_tensor = torch.zeros(tensor_size, device=device) >>> if dist.get_rank() == 0: >>> # 假设世界大小为2。>>> # 只能使用张量，且所有张量的尺寸必须相同。>>> t_ones = torch.ones(tensor_size, device=device) >>> t_fives = torch.ones(tensor_size, device=device) * 5 >>> scatter_list = [t_ones, t_fives] >>> else: >>> scatter_list = None >>> dist.scatter(output_tensor, scatter_list, src=0) >>> # 第i个节点将获得scatter_list[i]中的数据。 >>> output_tensor tensor([1., 1.], device='cuda:0') # 第0个节点 tensor([5., 5.], device='cuda:1') # 第1个节点 torch.distributed.scatter_object_list(scatter_object_output_list, scatter_object_input_list=None, src=None, group=None, group_src=None)[source]# 该函数用于将scatter_object_input_list中的可序列化对象分发到整个进程组。其功能与scatter()类似，但允许传递Python对象。在每个节点上，被分发的对象将作为scatter_object_output_list的第一个元素存储。需注意，只有所有对象都是可序列化的，才能成功进行分发。参数 scatter_object_output_list（List[Any]）——非空列表，其第一个元素将存储分配给该节点的对象。scatter_object_input_list（List[Any]，可选）——需要分发的输入对象列表，其中的每个对象都必须是可序列化的。仅源等级（src rank）上的对象会被散布，对于非源等级，该参数可设置为 None。  
src（整数）——用于散布 scatter_object_input_list 的源等级。此源等级是基于全局进程组来确定的（与 group 参数无关）。若同时指定 src 和 group_src 为 None，则默认使用全局等级 0。  
group（可选 [ProcessGroup]）——（ProcessGroup，可选）：要操作的进程组。若未指定，则使用默认的进程组。默认值为 None。  
group_src（整数，可选）——所在进程组中的源等级。不能同时指定 src 和 group_src。若调用此函数返回 None。如果当前等级属于某个进程组，那么 scatter_object_output_list 的第一个元素将被设置为该等级对应的散布对象。  
注意：该 API 与 scatter collective 略有不同，因为它不提供 async_op 接口，因此属于阻塞式调用。  
警告：对象集合操作存在诸多严重的性能和可扩展性限制，详情请参阅“对象集合操作”相关内容。  
警告：scatter_object_list() 函数会隐式使用 pickle 模块，而该模块存在安全风险。恶意构造的 pickle 数据在反序列化时可能会执行任意代码，因此仅建议对可信数据使用此函数。  
警告：使用 GPU 张量调用 scatter_object_list() 的兼容性较差且效率低下，因为需要先将张量序列化为字节流再进行 CPU 与 GPU 之间的传输。建议优先使用 scatter() 函数。示例::>>> # 注意：此处省略了每个进程节点上的进程组初始化步骤。 >>> import torch.distributed as dist >>> if dist.get_rank() == 0: >>> # 假设世界大小为3。 >>> objects = ["foo", 12, {1: 2}] # 任何可序列化的对象 >>> else: >>> # 在非源节点上可以是任意列表，其元素不会被使用。 >>> objects = [None, None, None] >>> output_list = [None] >>> dist.scatter_object_list(output_list, objects, src=0) >>> # 第i个进程节点将获得objects[i]。例如，在第2个进程节点上： >>> output_list 为 [{1: 2}] torch.distributed.reduce_scatter(output, input_list, op=<RedOpType.SUM: 0>, group=None, async_op=False)[来源]# 先对张量列表进行聚合操作，再将结果分散到进程组中的所有进程节点。参数：output（Tensor）——输出张量；input_list（list[Tensor]）——需要聚合并分散的张量列表；op（可选）——来自torch.distributed.ReduceOp枚举的值之一，用于指定逐元素聚合的操作类型；group（ProcessGroup，可选）——要操作的进程组。若为None，则使用默认的进程组；async_op（bool，可选）——该操作是否为异步操作。若async_op设置为True，则返回异步操作处理对象；否则或不属于该进程组时返回None。torch.distributed.reduce_scatter_tensor(output, input, op=<RedOpType.SUM: 0>, group=None, async_op=False)[来源]# 先对单个张量进行聚合操作，再将结果分散到进程组中的所有进程节点。参数：output（Tensor）——输出张量。该张量在所有等级中的尺寸应保持一致。input（Tensor）——需要被压缩并分散的输入张量，其尺寸应为输出张量尺寸乘以世界大小。输入张量可具有以下两种形状之一：(i) 沿主维度对多个输出张量进行连接；或 (ii) 沿主维度将多个输出张量堆叠起来。关于“连接”的定义，请参考 torch.cat()；关于“堆叠”的定义，请参考 torch.stack()。group（ProcessGroup，可选）——用于处理的进程组。若未指定，则使用默认的进程组。async_op（bool，可选）——该操作是否为异步操作。若将 async_op 设置为 True，则返回异步任务处理对象；若不是异步操作或不属于该进程组，则返回 None。示例 >>> # 下方所有的张量均为 torch.int64 数据类型，且位于 CUDA 设备上。>>> # 系统中共有两个节点。>>> device = torch.device(f"cuda:{rank}") >>> tensor_out = torch.zeros(2, dtype=torch.int64, device=device) >>> # 以拼接形式输入的数值 >>> tensor_in = torch.arange(world_size * 2, dtype=torch.int64, device=device) >>> tensor_in tensor([0, 1, 2, 3], device='cuda:0') # 节点 0 的张量 tensor([0, 1, 2, 3], device='cuda:1') # 节点 1 的张量 >>> dist.reduce_scatter_tensor(tensor_out, tensor_in) >>> tensor_out tensor([0, 2], device='cuda:0') # 节点 0 的结果 tensor([4, 6], device='cuda:1') # 节点 1 的结果 >>> # 以堆叠形式输入的数值 >>> tensor_in = torch.reshape(tensor_in, (world_size, 2)) >>> tensor_in tensor([[0, 1], [2, 3]], device='cuda:0') # 节点 0 的张量 tensor([[0, 1], [2, 3]], device='cuda:1') # 节点 1 的张量 >>> dist.reduce_scatter_tensor(tensor_out, tensor_in) >>> tensor_out tensor([0, 2], device='cuda:0') # 节点 0 的结果 tensor([4, 6], device='cuda:1') # 节点 1 的结果 torch.distributed.all_to_all_single(output, input, output_split_sizes=None, input_split_sizes=None, group=None, async_op=False) [来源]# 先将输入张量拆分，再将拆分后的各部分散布到集群中的所有进程。随后，从这些进程处收集得到的张量会被重新拼接，最终作为单个输出张量返回。该函数支持复杂的张量结构。参数输出（Tensor）——汇总后的连接输出张量。输入（Tensor）——需要执行散布操作的输入张量。output_split_sizes——（list[Int]，可选）：若指定该参数，则用于定义输出张量第0维的分片大小；若为None或空列表，则要求输出张量的第0维大小能被world_size整除。input_split_sizes——（list[Int]，可选）：若指定该参数，则用于定义输入张量第0维的分片大小；若为None或空列表，则要求输入张量的第0维大小能被world_size整除。group（ProcessGroup，可选）——需要操作的进程组。若未指定，则使用默认的进程组。async_op（bool，可选）——指示该操作是否应为异步操作。若async_op设置为True，则返回异步操作处理句柄；否则或不属于该进程组时则返回None。警告：all_to_all_single功能仍处于实验阶段，可能会发生变化。示例：>>> input = torch.arange(4) + rank * 4 >>> input tensor([0, 1, 2, 3]) # 排名0的元素为tensor([4, 5, 6, 7]) # 排名1的元素为tensor([8, 9, 10, 11]) # 排名2的元素为tensor([12, 13, 14, 15]) # 排名3的元素为>>> output = torch.empty([4], dtype=torch.int64) >>> dist.all_to_all_single(output, input) >>> output tensor([0, 4, 8, 12]) # 排名0的元素为tensor([1, 5, 9, 13]) # 排名1的元素为tensor([2, 6, 10, 14]) # 排名2的元素为tensor([3, 7, 11, 15]) # 排名3的元素为>>> # 实际上，该功能与以下操作类似：>>> scatter_list = list(input.chunk(world_size)) >>> gather_list = list(output.chunk(world_size)) >>> for i in range(world_size): >>> dist.scatter(gather_list[i], scatter_list if i == rank else [], src = i) >>> # 另一个涉及不均匀分片的示例 >>> input tensor([0, 1, 2, 3, 4,5]) # 0阶张量：tensor([10, 11, 12, 13, 14, 15, 16, 17, 18]) # 1阶张量：tensor([20, 21, 22, 23, 24]) # 2阶张量：tensor([30, 31, 32, 33, 34, 35, 36]) # 3阶张量 >>> input_splits [2, 2, 1, 1] # 0阶对应的分割方式 [3, 2, 2, 2] # 1阶对应的分割方式 [2, 1, 1, 1] # 2阶对应的分割方式 [2, 2, 2, 1] # 3阶对应的分割方式 >>> output_splits [2, 3, 2, 2] # 0阶输出的分割方式 [2, 2, 1, 2] # 1阶输出的分割方式 [1, 2, 1, 2] # 2阶输出的分割方式 [1, 2, 1, 1] # 3阶输出的分割方式 >>> output = ... >>> dist.all_to_all_single(output, input, output_splits, input_splits) >>> 输出结果：# 0阶张量：tensor([ 0, 1, 10, 11, 12, 20, 21, 30, 31]) # 1阶张量：tensor([ 2, 3, 13, 14, 22, 32, 33]) # 2阶张量：tensor([ 4, 15, 16, 23, 34, 35]) # 3阶张量：tensor([ 5, 17, 18, 24, 36]) >>> # 另一个使用torch.cfloat类型张量的示例。>>> input = torch.tensor( ... [1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j], dtype=torch.cfloat ... ) + 4 * rank * (1 + 1j) >>> 输入结果：# 0阶张量：tensor([1+1j, 2+2j, 3+3j, 4+4j]) # 1阶张量：tensor([5+5j, 6+6j, 7+7j, 8+8j]) # 2阶张量：tensor([9+9j, 10+10j, 11+11j, 12+12j]) # 3阶张量：tensor([13+13j, 14+14j, 15+15j, 16+16j]) >>> output = torch.empty([4], dtype=torch.int64) >>> dist.all_to_all_single(output, input) >>> 输出结果：# 0阶张量：tensor([1+1j, 5+5j, 9+9j, 13+13j]) # 1阶张量：tensor([2+2j, 6+6j, 10+10j, 14+14j]) # 2阶张量：tensor([3+3j, 7+7j, 11+11j, 15+15j]) # 3阶张量：tensor([4+4j, 8+8j, 12+12j, 16+16j]) torch.distributed.all_to_all(output_tensor_list, input_tensor_list, group=None, async_op=False)[来源]# 将输入张量列表分发到群组中的所有进程，然后返回收集到的张量列表作为输出。该函数支持复数型张量。参数  
output_tensor_list（list[Tensor]）——需按每个进程节点收集的张量列表。  
input_tensor_list（list[Tensor]）——需按每个进程节点散发的张量列表。  
group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认的进程组。  
async_op（bool，可选）——该操作是否应为异步操作。若设置为 True，则返回异步操作处理对象；否则若非异步操作或不属于该进程组，则返回 None。  

警告：all_to_all 功能仍处于实验阶段，可能会发生变化。  

示例  
>>> input = torch.arange(4) + rank * 4  
>>> input = list(input.chunk(4))  
>>> input  
[tensor([0]), tensor([1]), tensor([2]), tensor([3])]  # 进程节点 0  
[tensor([4]), tensor([5]), tensor([6]), tensor([7])]  # 进程节点 1  
[tensor([8]), tensor([9]), tensor([10]), tensor[11])]  # 进程节点 2  
[tensor([12]), tensor([13]), tensor([14]), tensor[15])]  # 进程节点 3  

>>> output = list(torch.empty([4], dtype=torch.int64).chunk(4))  
>>> dist.all_to_all(output, input)  
>>> output  
[tensor([0]), tensor([4]), tensor[8]), tensor[12]]  # 进程节点 0  
[tensor[1]), tensor[5]), tensor[9]), tensor[13]]  # 进程节点 1  
[tensor[2]), tensor[6]), tensor[10]), tensor[14]]  # 进程节点 2  
[tensor[3]), tensor[7]), tensor[11]), tensor[15]]  # 进程节点 3  

>>> # 本质上，该操作与以下操作类似：  
>>> scatter_list = input  
>>> gather_list = output  
>>> for i in range(world_size):  
>>>     dist.scatter(gather_list[i], scatter_list if i == rank else [], src=i)  
>>> input  
tensor([0, 1, 2, 3, 4, 5])  # 进程节点 0  
tensor([10, 11, 12, 13, 14, 15, 16, 17])  # 进程节点 318]) # 1阶张量：[20, 21, 22, 23, 24] # 2阶张量：[30, 31, 32, 33, 34, 35, 36] # 3阶张量 >>> input_splits [2, 2, 1, 1] # 0阶 [3, 2, 2, 2] # 1阶 [2, 1, 1, 1] # 2阶 [2, 2, 2, 1] # 3阶 >>> output_splits [2, 3, 2, 2] # 0阶 [2, 2, 1, 2] # 1阶 [1, 2, 1, 2] # 2阶 [1, 2, 1, 1] # 3阶 >>> input = list(input.split(input_splits)) >>> input [tensor([0, 1]), tensor([2, 3]), tensor([4]), tensor([5])] # 0阶 [tensor([10, 11, 12]), tensor([13, 14]), tensor([15, 16]), tensor([17, 18])] # 1阶 [tensor([20, 21]), tensor([22]), tensor([23]), tensor([24])] # 2阶 [tensor([30, 31]), tensor([32, 33]), tensor([34, 35]), tensor([36])] # 3阶 >>> output = ... >>> dist.all_to_all(output, input) >>> output [tensor([0, 1]), tensor([10, 11, 12]), tensor([20, 21]), tensor([30, 31])] # 0阶 [tensor([2, 3]), tensor([13, 14]), tensor([22]), tensor([32, 33])] # 1阶 [tensor([4]), tensor([15, 16]), tensor([23]), tensor([34, 35])] # 2阶 [tensor([5]), tensor([17, 18]), tensor([24]), tensor([36])] # 3阶 >>> # 另一个使用torch.cfloat类型张量的示例。 >>> input = torch.tensor( ... [1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j], dtype=torch.cfloat ... ) + 4 * rank * (1 + 1j) >>> input = list(input.chunk(4)) >>> input [tensor([1+1j]), tensor([2+2j]), tensor([3+3j]), tensor([4+4j])] # 0阶 [tensor([5+5j]), tensor([6+6j]), tensor([7+7j]), tensor([8+8j])] # 1阶 [tensor([9+9j]), tensor([10+10j]), tensor([11+11j]), tensor([12+12j])] # 2阶 [tensor([13+13j]), tensor([14+14j]), tensor([15+15j]),tensor([16+16j])] # 阶数为3 >>> output = list(torch.empty([4], dtype=torch.int64).chunk(4)) >>> dist.all_to_all(output, input) >>> output [tensor([1+1j]), tensor([5+5j]), tensor([9+9j]), tensor([13+13j])] # 阶数为0 [tensor([2+2j]), tensor([6+6j]), tensor([10+10j]), tensor([14+14j])] # 阶数为1 [tensor([3+3j]), tensor([7+7j]), tensor([11+11j]), tensor([15+15j])] # 阶数为2 [tensor([4+4j]), tensor([8+8j]), tensor([12+12j]), tensor([16+16j])] # 阶数为3 torch.distributed.barrier(group=None, async_op=False, device_ids=None)[source]# 用于同步所有进程。当 async_op 设为 False 或在 wait() 上调用了异步操作处理函数时，该集合操作会阻塞进程，直到整个进程组都进入此函数。参数 group（ProcessGroup，可选）——要操作的进程组。如果未指定，则使用默认的进程组。async_op（bool，可选）——该操作是否为异步操作。device_ids（[int]，可选）——设备/GPU ID 列表。通常只需提供一个 ID。如果 async_op 设为 True，则返回异步操作处理函数；否则若不是异步操作或不属于该进程组，则返回 None。注意：ProcessGroupNCCL 会阻塞 CPU 线程，直到屏障集合操作完成。另外，ProcessGroupNCCL 是通过对一个包含 1 个元素的张量执行 all_reduce 操作来实现屏障功能的，因此必须为该张量的分配指定一个设备。设备的选择是按照以下顺序依次确定的：(1) 若参数 `device_ids` 不为 `None`，则优先使用传递给该参数的第一个设备；(2) 若参数 `init_process_group` 不为 `None`，则使用其指定的设备；(3) 如果之前已执行过涉及张量输入的集体操作，则选择首次与该进程组一起使用的设备；(4) 最后通过全局排名除以本地设备数量取余得到的设备索引。  
`torch.distributed.monitored_barrier(group=None, timeout=None, wait_all_ranks=False)` [来源]  
该函数与 `torch.distributed.barrier` 类似，用于实现进程同步，但增加了可配置的超时机制。它能够报告在指定超时时间内未能通过同步屏障的进程排名。具体而言，对于非零排名的进程，会一直阻塞直到收到来自排名 0 的发送/接收操作；而排名 0 的进程则会一直阻塞，直到处理完所有其他进程的发送/接收操作，并会对未能及时响应的进程报告失败。需要注意的是，如果某个进程无法到达同步屏障（例如因程序挂起），则所有其他进程在尝试使用 `monitored_barrier` 时也会失败。此集体操作会阻塞组内的所有进程/排名，直到整个组成功退出该函数，因此非常适用于调试和同步操作。不过，它可能会对性能产生影响，仅建议在调试或需要在主机端实现完全同步的场景中使用。出于调试目的，可在应用程序的集体操作之前调用此函数，以检查是否有进程出现不同步情况。注意：此功能仅支持在 GLOO 后端上使用。parameters group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认的进程组。timeout（datetime.timedelta，可选）—— monitored_barrier 的超时时间。若未指定，则使用默认的进程组超时时间。wait_all_ranks（bool，可选）——是否需要收集所有出现故障的节点。默认值为 False，在这种情况下，位于节点 0 的 monitored_barrier 会在遇到第一个故障节点时立即抛出异常以实现快速失败。若将 wait_all_ranks 设置为 True，则 monitored_barrier 会收集所有故障节点，并抛出一个包含这些节点相关信息的错误。该函数返回 None。示例：>>> # 注意：此处省略了每个节点上的进程组初始化步骤。 >>> import torch.distributed as dist >>> if dist.get_rank() != 1: >>> dist.monitored_barrier() # 会抛出异常，表明 >>> # 节点 1 未调用 monitored_barrier。 >>> # 设置 wait_all_ranks=True 的示例 >>> if dist.get_rank() == 0: >>> dist.monitored_barrier(wait_all_ranks=True) # 会抛出异常 >>> # 表明节点 1、2……world_size - 1 均未调用 >>> # monitored_barrier。class torch.distributed.Work# Work 对象代表了 PyTorch 分布式模块中待处理的异步操作的句柄。该值由非阻塞式集合操作返回，例如 dist.all_reduce(tensor, async_op=True)。block_current_stream(self: torch._C._distributed_c10d.Work) → None：会阻塞当前正在执行的 GPU 流以等待操作完成。对于基于 GPU 的集合操作，此功能等同于同步操作；而对于由 CPU 发起的集合操作（如使用 Gloo），则会阻塞 CUDA 流直至操作完成。在所有情况下，该方法都会立即返回结果。若要检查操作是否成功，应通过异步方式查询 Work 对象的结果。boxed(self: torch._C._distributed_c10d.Work) → object：用于对结果进行封装。exception(self: torch._C._distributed_c10d.Work) → std::__exception_ptr::exception_ptr：用于获取操作过程中抛出的异常信息。get_future(self: torch._C._distributed_c10d.Work) → torch.Future：返回与 Work 对象完成状态相关的 torch.futures.Future 对象。例如，可通过 fut = process_group.allreduce(tensors).get_future() 来获取该 Future 对象。示例：以下是一个简单的 allreduce DDP 通信钩子的示例，该钩子使用 get_future API 来获取与 allreduce 操作完成相关的 Future 对象。  
>>> def allreduce(process_group: dist.ProcessGroup, bucket: dist.GradBucket): -> torch.futures.Future  
>>> group_to_use = process_group if process_group is not None else torch.distributed.group.WORLD  
>>> tensor = bucket.buffer().div_(group_to_use.size())  
>>> return torch.distributed.all_reduce(tensor, group=group_to_use, async_op=True).get_future()  
>>> ddp_model.register_comm_hook(state=None, hook=allreduce)  

注意：get_future API 支持 NCCL 以及部分 GLOO 和 MPI 后端（不支持诸如 send/recv 这样的点对点操作），并且会返回一个 torch.futures.Future 对象。在上面的示例中，allreduce 操作将通过 NCCL 后端在 GPU 上执行；fut.wait() 会在将相应的 NCCL 流与 PyTorch 当前设备流同步之后才返回结果，这样可以实现异步 CUDA 执行，而无需等待 GPU 上的所有操作完全完成。需注意的是，CUDAFuture 不支持 TORCH_NCCL_BLOCKING_WAIT 标志或 NCCL 的 barrier() 函数。此外，如果通过 fut.then() 添加了回调函数，它将一直等待 WorkNCCL 的 NCCL 流与 ProcessGroupNCCL 的专用回调流同步，然后在回调流上运行回调函数后直接调用该回调。fut.then() 会返回另一个 CUDAFuture 对象，其中包含回调函数的返回值以及记录了回调流状态的 CUDAEvent 对象。在 CPU 计算中，当任务完成且对应的 value() 张量已准备好时，fut.done() 会返回 true。而对于 GPU 计算，fut.done() 仅在操作被放入队列后才会返回 true。对于混合 CPU-GPU 计算场景（例如通过 GLOO 传输 GPU 张量），fut.done() 会在张量到达相应节点时返回 true，但它们未必已在对应的 GPU 上完成同步（这与 GPU 计算的情况类似）。get_future_result(self: torch._C._distributed_c10d.Work) → torch.Future：该方法会返回一个类型为 int 的 torch.futures.Future 对象，该对象与 WorkResult 枚举类型相对应。例如，可通过 fut = process_group.allreduce(tensor).get_future_result() 来获取该未来对象。用户可以使用 fut.wait() 以阻塞方式等待任务完成，并通过 fut.value() 获取 WorkResult。此外，用户还可以使用 fut.then(call_back_func) 注册回调函数，在任务完成后自动执行，而不会阻塞当前线程。注意：get_future_result API 支持 NCCL。其他相关方法包括 is_completed(self: torch._C._distributed_c10d.Work) → bool、is_success(self: torch._C._distributed_c10d.Work) → bool、result(self: torch._C._distributed_c10d.Work) → list[torch.Tensor]、source_rank(self: torch._C._distributed_c10d.Work) → int、synchronize(self: torch._C._distributed_c10d.Work) → None 以及 static unbox(arg0: object) → torch._C._distributed_c10d.Work。wait(self: torch._C._distributed_c10d.Work, timeout: datetime.timedelta = datetime.timedelta(0)) → bool：该方法返回 true 或 false 值。示例：try: work.wait(timeout) except: # 进行相应处理 警告：在正常情况下，用户无需设置超时时间。调用 wait() 与调用 synchronize() 效果相同，即让当前线程在 NCCL 计算完成时保持阻塞状态。但如果设置了超时时间，该线程将会一直阻塞，直到 NCCL 计算完成或达到超时时间，此时会抛出异常。  
class torch.distributed.ReduceOp：一个用于表示各种归约操作的枚举类，支持的运算包括 SUM、PRODUCT、MIN、MAX、BAND、BOR、BXOR 以及 PREMUL_SUM。在使用 NCCL 后端时，BAND、BOR 和 BXOR 这三种归约操作是不可用的。AVG 操作会在对所有节点的值求和之前先将其除以节点总数；该操作仅支持 NCCL 后端，且要求 NCCL 版本为 2.10 或更高。PREMUL_SUM 操作则会在归约之前在本地将输入值与给定的标量相乘；该操作同样仅支持 NCCL 后端，且要求 NCCL 版本为 2.11 或更高。用户应使用 torch.distributed._make_nccl_premul_sum 函数来实现此功能。此外，MAX、MIN 和 PRODUCT 操作不支持复杂张量。该类中的各个操作类型可作为属性访问，例如 ReduceOp.SUM；它们被用于指定归约操作的策略，比如 reduce() 函数。该类不支持 __members__ 属性。  
class torch.distributed.reduce_op：一个已过时的归约操作枚举类，支持的运算为 SUM、PRODUCT、MIN 和 MAX。建议使用 ReduceOp 类来替代它。分布式键值存储# 该分布式包内置了分布式键值存储功能，可用于在集群中的各个进程之间共享信息，同时也可用于在torch.distributed.init_process_group()中初始化分布式包（通过显式创建存储对象来替代指定init_method参数）。键值存储共有三种选择：TCPStore、FileStore和HashStore。class torch.distributed.Store# 所有存储实现类的基类，例如PyTorch分布式框架提供的三种存储类型：(TCPStore、FileStore和HashStore)。__init__(self: torch._C._distributed_c10d.Store) → None# add(self: torch._C._distributed_c10d.Store, arg0: str, arg1: SupportsInt) → int# 对于给定的键，首次调用add方法时会在存储中为该键创建一个计数器，并将其初始化为arg1指定的值。后续使用相同键再次调用add方法时，计数器将按arg1指定的数值递增。如果尝试对已通过set()方法在存储中设置过的键调用add()方法，则会引发异常。参数 key (str) – 需要对其计数器进行递增的存储键。amount (int) – 计数器递增的数值。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> # 以TCPStore为例，其他存储类型也可使用 >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.add("first_key", 1) >>> store.add("first_key", 6) >>> # 应返回7 >>> store.get("first_key")  
append(self: torch._C._distributed_c10d.Store, arg0: str, arg1: str) → None  
根据指定的键和值将键值对添加到存储中。如果存储中不存在该键，则会创建该键。参数：  
key (str) – 要添加到存储中的键。  
value (str) – 与键关联并要添加到存储中的值。  

示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.append("first_key", "po") >>> store.append("first_key", "tato") >>> # 应返回"potato" >>> store.get("first_key")  

check(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str]) → bool  
用于检查给定的键列表中是否有对应的值存储在存储中。通常情况下该函数会立即返回结果，但在某些边界情况或死锁场景下仍可能出现问题，例如在TCPStore已被销毁后调用check()。该函数接受一个键列表，用于查询这些键是否存储在存储中。参数：  
keys (list[str]) – 要查询是否存储在存储中的键列表。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> # 以TCPStore为例，其他存储类型也可使用 >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.add("first_key", 1) >>> # 应返回7 >>> store.check(["first_key"])  
clone(self: torch._C._distributed_c10d.Store) → torch._C._distributed_c10d.Store  
# 克隆该存储对象，并返回一个指向相同底层存储的新对象。返回的存储对象可与原始对象同时使用。此功能的目的是通过为每个线程克隆一个存储对象，为多线程安全地使用存储提供保障。  

compare_set(self: torch._C._distributed_c10d.Store, arg0: str, arg1: str, arg2: str) → bytes  
# 根据提供的键将键值对插入存储中，并在插入前对比期望值与目标值。仅当存储中已存在该键的期望值，或期望值为空字符串时，才会设置目标值。  
参数：  
key (str) – 需要在存储中检查的键。  
expected_value (str) – 在插入前需检查的键所对应的值。  
desired_value (str) – 将要添加到存储中的键所对应的值。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.set("key", "first_value") >>> store.compare_set("key", "first_value", "second_value") >>> # 应返回 "second_value" >>> store.get("key")

delete_key(self: torch._C._distributed_c10d.Store, arg0: str) → bool  
# 从存储中删除与指定键关联的键值对。如果删除成功则返回 True，否则返回 False。  
警告：该 delete_key 接口仅支持 TCPStore 和 HashStore。若在 FileStore 上使用此接口将会引发异常。  
参数：  
key (str) – 需要从存储中删除的键  
返回值：如果键被成功删除则返回 True，否则返回 False。

示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> # 以 TCPStore 为例，HashStore 也可使用 >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.set("first_key") >>> # 此操作应返回 True >>> store.delete_key("first_key") >>> # 此操作应返回 False >>> store.delete_key("bad_key")

get(self: torch._C._distributed_c10d.Store, arg0: str) → bytes  
# 获取存储中与指定键关联的值。如果该键不存在于存储中，函数会等待存储初始化时设定的超时时间，之后才会抛出异常。  
参数：  
key (str) – 函数将返回与该键关联的值。如果键存在于存储中，则返回与该键关联的值。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.set("first_key", "first_value") >>> # 应返回 "first_value" >>> store.get("first_key") has_extended_api(self: torch._C._distributed_c10d.Store) → bool# 如果存储支持扩展操作，则返回 true。multi_get(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str]) → list[bytes]# 获取所有键对应的值。如果指定的键中有任何键不存在于存储中，函数将等待超时时间。参数：keys (List[str]) – 需要从存储中获取的键。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.set("first_key", "po") >>> store.set("second_key", "tato") >>> # 应返回 [b"po", b"tato"] >>> store.multi_get(["first_key", "second_key"]) multi_set(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str], arg1: collections.abc.Sequence[str]) → None# 根据提供的键和值将键值对列表插入存储中。参数：keys (List[str]) – 要插入的键。values (List[str]) – 要插入的值。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.multi_set(["first_key", "second_key"], ["po", "tato"]) >>> # 应返回 b"po" >>> store.get("first_key")  
num_keys(self: torch._C._distributed_c10d.Store) → int  
# 返回存储中已设置的键的数量。需要注意的是，该数值通常会比通过 set() 和 add() 添加的键数多 1，因为会有一個键用于协调所有使用该存储的 Worker。  
警告：当与 TCPStore 一起使用时，num_keys 返回的是写入底层文件的键的数量。如果该存储被销毁后又使用同一文件创建了新的存储，原有的键将会保留下来。  
返回值：存储中现有的键的数量。  

示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> # 以 TCPStore 为例，其他类型的存储也可使用 >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.set("first_key", "first_value") >>> # 此时应返回 2 >>> store.num_keys()  
queue_len(self: torch._C._distributed_c10d.Store, arg0: str) → int  
# 返回指定队列的长度。如果该队列不存在，则返回 0。更多详细信息请参见 queue_push。参数 key（str）——用于获取队列长度的键。queue_pop(self: torch._C._distributed_c10d.Store, key: str, block: bool = True) → bytes # 从指定队列中取出一个值；如果队列为空，则会等待直至超时。更多详情请参见 queue_push。若设置 block 为 False，且队列为空时将引发 dist.QueueEmptyError 异常。参数 key（str）——要从中取值的队列键。block（bool）——是否阻塞等待该键值，还是立即返回。queue_push(self: torch._C._distributed_c10d.Store, arg0: str, arg1: str) → None # 将一个值推入指定队列。若对队列与设置/获取操作使用相同的键，则可能导致意外行为。队列支持等待/检查操作，且使用该操作仅会唤醒一个正在等待的工作者，而非全部。参数 key（str）——要向其中推送值的队列键。value（str）——要推入队列的值。set(self: torch._C._distributed_c10d.Store, arg0: str, arg1: str) → None # 根据提供的键和值将键值对插入存储中。如果存储中已存在该键，则会用新提供的值覆盖旧值。参数 key（str）——要添加到存储中的键。value（str）——要与该键一同添加到存储中的值。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.set("first_key", "first_value") >>> # 应返回 "first_value" >>> store.get("first_key")  
set_timeout(self: torch._C._distributed_c10d.Store, arg0: datetime.timedelta) → None  
# 设置存储对象的默认超时时间。该超时时间会在初始化过程中以及 wait() 和 get() 方法中被使用。  
参数：  
timeout (timedelta) – 要为存储对象设置的超时时间。  

示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> # 以 TCPStore 为例，其他类型的存储对象也可使用此方法 >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> store.set_timeout(timedelta(seconds=10)) >>> # 10 秒后将会抛出异常 >>> store.wait(["bad_key"])  

属性：  
timeout  
# 获取存储对象的超时时间。  

方法：  
wait(*args, **kwargs)  
# 重载函数。  
wait(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str]) → None  
# 等待 keys 参数中指定的所有键被添加到存储对象中。如果在存储对象初始化时设定的超时时间之前，并非所有键都已被设置，那么 wait() 方法将会抛出异常。  
参数：  
keys (list) – 需要等待其被添加到存储对象中的键的列表。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> # 以TCPStore为例，也可使用其他类型的存储 >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> # 30秒后将会抛出异常 >>> store.wait(["bad_key"])  
函数签名：wait(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str], arg1: datetime.timedelta) -> None  
该函数会等待指定键被添加到存储中，若在设定的超时时间内这些键仍未被设置，则会抛出异常。  
参数：  
keys（列表）——需要等待其被添加到存储中的键的列表。  
timeout（timedelta）——在抛出异常之前，等待键被添加的时间长度。  

示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> # 以TCPStore为例，也可使用其他类型的存储 >>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30)) >>> # 10秒后将会抛出异常 >>> store.wait(["bad_key"], timedelta(seconds=10))  

class torch.distributed.TCPStore  
基于TCP协议的分布式键值存储实现。服务器端存储负责保存数据，而客户端存储则可通过TCP连接到服务器端存储，并执行诸如set()（插入键值对）和get()（检索键值对）等操作。由于客户端存储会等待服务器建立连接，因此系统中始终应有一个已初始化的服务器端存储。参数说明：  
host_name（str）——服务器存储需运行的主机名或IP地址。  
port（int）——服务器存储用于监听传入请求的端口号。  
world_size（int，可选）——存储用户总数（客户端数量加上1个服务器）。默认值为None（表示存储用户数量不确定）。  
is_master（bool，可选）——初始化服务器存储时为True，客户端存储则为False。默认值为False。  
timeout（timedelta，可选）——存储在初始化过程以及get()和wait()等方法执行时所使用的超时时间。默认值为timedelta(seconds=300)。  
wait_for_workers（bool，可选）——是否等待所有工作进程与服务器存储建立连接。此参数仅在world_size为固定值时适用。默认值为True。  
multi_tenant（bool，可选）——若设置为True，则当前进程中具有相同主机名/端口号的所有TCPStore实例将共享同一个底层TCPServer。默认值为False。  
master_listen_fd（int，可选）——如果指定了该值，底层TCPServer将在该文件描述符上监听，该描述符必须是一个已绑定到特定端口的套接字。若需绑定临时端口，建议将端口号设置为0并通过其他方式获取端口值。默认值为None（表示服务器会创建一个新的套接字并尝试将其绑定到指定端口）。  
use_libuv（bool，可选）——若设置为True，则使用libuv作为TCPServer的后端引擎。默认值为True。示例：>>> import torch.distributed as dist >>> from datetime import timedelta >>> # 在进程1（服务器）上运行 >>> server_store = dist.TCPStore("127.0.0.1", 1234, 2, True, timedelta(seconds=30)) >>> # 在进程2（客户端）上运行 >>> client_store = dist.TCPStore("127.0.0.1", 1234, 2, False) >>> # 初始化完成后，可在服务器或客户端上调用该存储对象的任意方法 >>> server_store.set("first_key", "first_value") >>> client_store.get("first_key") 

构造函数：  
`__init__(self: torch._C._distributed_c10d.TCPStore, host_name: str, port: SupportsInt, world_size: SupportsInt | None = None, is_master: bool = False, timeout: datetime.timedelta = datetime.timedelta(seconds=300), wait_for_workers: bool = True, multi_tenant: bool = False, master_listen_fd: SupportsInt | None = None, use_libuv: bool = True) → None`  
用于创建一个新的TCPStore对象。

属性：  
- `host`：获取存储对象监听请求的主机名。  
- `libuvBackend`：如果使用libuv后端，则返回True。  
- `port`：获取存储对象监听请求的端口号。  

类：`torch.distributed.HashStore`  
基于底层哈希表实现的线程安全存储类。该存储可在同一进程内（例如由其他线程）使用，但无法在不同进程间使用。示例：>>> import torch.distributed as dist >>> store = dist.HashStore() >>> # 其他线程也可使用该存储对象 >>> # 初始化后可调用其任意存储方法 >>> store.set("first_key", "first_value")  
__init__(self: torch._C._distributed_c10d.HashStore) → None  
# 创建一个新的 HashStore 对象。  

class torch.distributed.FileStore  
# 一种通过文件来存储键值对的存储实现方式。  
参数：  
file_name (str) – 用于存储键值对的文件路径  
world_size (int, 可选) – 使用该存储的对象总数。默认值为 -1（负数值表示存储使用者的数量不是固定值）。  

示例：>>> import torch.distributed as dist >>> store1 = dist.FileStore("/tmp/filestore", 2) >>> store2 = dist.FileStore("/tmp/filestore", 2) >>> # 初始化后，客户端或服务器均可调用其任意存储方法 >>> store1.set("first_key", "first_value") >>> store2.get("first_key")  
__init__(self: torch._C._distributed_c10d.FileStore, file_name: str, world_size: SupportsInt = -1) → None  
# 创建一个新的 FileStore 对象。  

property path  
# 获取 FileStore 用于存储键值对的文件路径。  

class torch.distributed.PrefixStore  
# 一种对 TCPStore、FileStore 和 HashStore 这三种键值存储方式进行封装的类，它会在插入存储中的每个键前添加前缀。参数 prefix（str）——在将键值对存储到存储系统中之前，会先在其前添加的前缀字符串。store（torch.distributed.store）——构成底层键值存储结构的存储对象。__init__(self: torch._C._distributed_c10d.PrefixStore, prefix: str, store: torch._C._distributed_c10d.Store) → None # 创建一个新的 PrefixStore 对象。property underlying_store # 获取被 PrefixStore 包装着的底层存储对象。性能分析：集合通信# 请注意，您可以使用 torch.profiler（推荐使用，仅适用于 1.8.1 及更高版本）或 torch.autograd.profiler 来对本文中提到的集合通信及点对点通信 API 进行性能分析。所有开箱即用的后端（gloo、nccl、mpi）均受支持，集合通信的使用情况会如预期般显示在性能分析结果/跟踪数据中。对代码进行性能分析的方法与普通 torch 操作完全相同：import torch import torch.distributed as dist with torch.profiler(): tensor = torch.randn(20, 10) dist.all_reduce(tensor) 如需了解 profiler 的全部功能，请参阅其相关文档。多 GPU 集合函数# 警告：多 GPU 函数（即每个 CPU 线程对应多个 GPU）现已过时。目前，PyTorch Distributed 推荐的编程模型是每个线程使用一个设备，本文中的 API 即为此模式的示例。如果您是后端开发人员且希望支持每个线程使用多个设备，请联系 PyTorch Distributed 的维护团队。对象集合# 警告 对象集合存在诸多严重限制。请继续阅读以判断其在您的应用场景中是否安全可用。对象集合是一组类似集合的操作，可用于对任何可被序列化的 Python 对象进行处理。虽然实现了多种集合模式（如广播、全收集等），但它们大致都遵循以下流程：将输入对象转换为 pickle 格式的原始字节，然后将其放入字节张量中；向其他节点传递该字节张量的大小信息（即第一阶段集合操作）；为实际的数据收集分配大小合适的张量；传输对象数据本身（即第二阶段集合操作）；最后再将原始数据转换回 Python 对象格式。对象集合有时会表现出出乎意料的性能或内存特性，从而导致运行时间过长或内存溢出，因此应谨慎使用。以下是一些常见问题：序列化/反序列化时间不对称——根据对象的数量、类型及大小不同，对象的序列化过程可能会比较缓慢。当采用有入度的集合操作时（例如 gather_object），接收节点需要反序列化的对象数量是发送节点序列化对象数量的 N 倍，这可能导致其他节点在后续的集合操作中超时；张量通信效率低下——应通过常规的集合 API 传输张量，而非使用对象集合 API。虽然可以通过对象集合 API 来传输张量，但这些张量在传输过程中需要进行序列化与反序列化处理（对于非 CPU 张量而言，还需进行 CPU 同步以及设备到主机的复制操作）。除用于代码调试或故障排查之外，在几乎所有情况下，都值得费力重构代码，转而使用非对象集合机制来传输张量。关于异常的张量设备：如果仍坚持要通过对象集合 API 传输张量，那么对于运行在 CUDA（以及其他加速器上）上的张量还存在一个特殊问题。如果对当前位于 cuda:3 设备上的张量进行序列化后再反序列化，无论当前进程处于哪个节点，也无论该进程的“默认” CUDA 设备是什么，反序列化后得到的张量仍将位于 cuda:3 设备上。而使用常规的张量集合 API 时，“输出张量”始终会位于同一本地设备上，这通常也是人们所期望的结果。如果进程首次使用 GPU，反序列化张量时会隐式激活一个 CUDA 上下文，这可能会浪费大量 GPU 内存。为避免这一问题，可在将张量作为输入传递给对象集合之前，先将其移至 CPU 上。第三方后端：除了内置的 GLOO/MPI/NCCL 后端之外，PyTorch 分布式版本还支持通过运行时注册机制引入第三方后端。如需了解如何通过 C++ 扩展开发第三方后端的相关资料，请参阅《教程——自定义 C++ 和 CUDA 扩展》以及 test/cpp_extensions/cpp_c10d_extension.cpp 文件。第三方后端的功能由其自身的实现方式决定。新的后端基于c10d::ProcessGroup开发，在被导入时会通过torch.distributed.Backend.register_backend()方法注册后端名称及对应的实例化接口。若手动导入该后端，并使用相应的后端名称调用torch.distributed.init_process_group()，则torch.distributed包将在该新后端上运行。**警告**：第三方后端的支持目前仍处于试验阶段，可能会发生变动。

**启动工具**：torch.distributed包还提供了torch.distributed.launch这一启动工具。该辅助工具可用于在每个节点上启动多个进程，从而实现分布式训练。它属于torch.distributed.launch模块。torch.distributed.launch会在每个训练节点上启动多个分布式训练进程。**警告**：该模块即将被弃用，未来将由torchrun取代。该工具同样适用于单节点分布式训练，可在每个节点上生成一个或多个进程。无论进行CPU训练还是GPU训练均可使用该工具；若用于GPU训练，每个分布式进程都将运行在独立的GPU上，从而显著提升单节点训练性能。此外，它也可用于多节点分布式训练，通过在每个节点上启动多个进程来进一步提升多节点训练的效率。对于那些拥有多个支持直接GPU连接的InfiniBand接口的系统而言，这一功能尤为实用，因为所有这些接口都可以被用于提升通信带宽。无论是在单节点分布式训练还是多节点分布式训练场景下，该工具都会在每个节点上启动指定数量的任务进程（--nproc-per-node参数）。若用于GPU训练，此数值必须小于或等于当前系统中的GPU数量（即nproc_per_node），并且每个进程将仅使用从GPU 0到GPU (nproc_per_node - 1)中的某一个GPU。该模块的使用方法如下：单节点多进程分布式训练：python -m torch.distributed.launch --nproc-per-node=您拥有的GPU数量 YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3以及训练脚本中的其他所有参数)；多节点多进程分布式训练（例如两个节点）：节点1：(IP地址：192.168.1.1，可用端口：1234) python -m torch.distributed.launch --nproc-per-node=您拥有的GPU数量 --nnodes=2 --node-rank=0 --master-addr="192.168.1.1" --master-port=1234 YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3以及训练脚本中的其他所有参数)；节点2：python -m torch.distributed.launch --nproc-per-node=您拥有的GPU数量 --nnodes=2 --node-rank=1 --master-addr="192.168.1.1" --master-port=1234 YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3以及训练脚本中的其他所有参数)。如需查看该模块提供的可选参数，可执行：python -m torch.distributed.launch --help 重要注意事项：1.目前，该工具以及多进程分布式（单节点或多节点）GPU训练仅在采用NCCL分布式后端时才能实现最佳性能。因此，NCCL后端是进行GPU训练的推荐选择。2. 在您的训练程序中，必须解析由该模块提供的命令行参数——--local-rank=LOCAL_PROCESS_RANK。如果您的训练程序使用了GPU，需确保代码仅在LOCAL_PROCESS_RANK对应的GPU设备上运行。实现方式如下：解析local_rank参数 >>> import argparse >>> parser = argparse.ArgumentParser() >>> parser.add_argument("--local-rank", type=int) >>> args = parser.parse_args() 然后通过以下任一方式将设备设置为对应编号的GPU >>> torch.cuda.set_device(args.local_rank) # 在代码运行之前执行 或者 >>> with torch.cuda.device(args.local_rank): >>> # 这里编写要运行的代码 >>> ... 2.0.0版本中的变更：启动器会将--local-rank=<rank>参数传递给您的脚本。从PyTorch 2.0.0版本开始，推荐使用带连字符的--local-rank格式，而非之前使用的带下划线的格式。为保持向后兼容性，用户可能需要在参数解析代码中同时处理这两种格式，即在参数解析器中同时包含"--local-rank"和"--local_rank"两种写法。如果仅提供"--local_rank"，启动器将会抛出错误：“error: unrecognized arguments: –local-rank=<rank>”。对于仅支持 PyTorch 2.0.0+ 版本的训练代码，使用包含 “--local-rank” 参数的配置通常就已足够。3. 在您的训练程序中，需在开头调用以下函数以启动分布式后端。强烈建议使用 init_method=env://。虽然其他初始化方式（如 tcp://）也可能可行，但 env:// 是该模块官方支持的格式。>>> torch.distributed.init_process_group(backend='YOUR BACKEND', >>> init_method='env://') 4. 在训练程序中，您既可以使用常规的分布式函数，也可以使用 torch.nn.parallel.DistributedDataParallel() 模块。如果您的训练程序依赖 GPU 进行训练，并希望使用该模块，配置方法如下：>>> model = torch.nn.parallel.DistributedDataParallel(model, >>> device_ids=[args.local_rank], >>> output_device=args.local_rank) 请确保 device_ids 参数被设置为代码将要运行的唯一 GPU 设备编号，该编号通常即为进程的本地排名。换言之，要使用此功能，device_ids 必须为 [args.local_rank]，output_device 则应为 args.local_rank。5. 另一种通过环境变量 LOCAL_RANK 将本地排名传递给子进程的方法是：在启动脚本时加上 --use-env=True 参数即可启用此功能。此时需将上述子进程示例中的 args.local_rank 替换为 os.environ['LOCAL_RANK']；因为设置了该标志后，启动器不会再传递 --local-rank 参数。警告：local_rank并非全局唯一值，它仅在机器上的每个进程内是唯一的。因此，请勿使用它来决定是否要向网络文件系统写入数据。关于未能正确处理该问题可能导致的后果，可参考pytorch/pytorch#12042中的示例。spawn工具函数——torch.multiprocessing包还提供了torch.multiprocessing.spawn()中的spawn函数。此辅助函数可用于启动多个进程，其工作原理是传入需运行的函数，然后生成N个进程来执行该函数，这一功能也可用于多进程分布式训练。关于使用方法的参考资料，请参阅PyTorch的ImageNet实现示例。需要注意的是，该函数要求Python 3.4或更高版本。调试torch.distributed应用程序——由于难以理解的程序挂起、崩溃现象以及不同进程间的行为不一致，调试分布式应用程序颇具挑战性。torch.distributed提供了一套工具，可帮助以自助方式调试训练应用程序：Python断点功能——在分布式环境中使用Python的调试器极为方便，但由于其并非开箱即用，许多人根本不会使用它。PyTorch为pdb提供了定制化的封装，简化了这一流程。torch.distributed.breakpoint让这一操作更加简单。在内部，它通过两种方式定制了pdb的断点行为，除此之外其行为与普通pdb相同。该功能仅在用户指定的某一节点上挂载调试器，同时通过调用torch.distributed.barrier()确保所有其他节点暂停执行。一旦被调试的节点发出继续执行的指令，该屏障便会解除。此外，它还会重新路由子进程的标准输入，使其连接到用户的终端。若要使用此功能，只需在所有节点上分别调用torch.distributed.breakpoint(rank)函数，且每个节点的rank参数值需保持一致。监控型屏障——从v1.10版本起，torch.distributed.monitored_barrier()作为torch.distributed.barrier()的替代方案出现。当系统崩溃时，后者会提供有用的信息，指出可能是哪个节点出现了故障，即未能在指定时间内调用torch.distributed.monitored_barrier()的所有节点。torch.distributed.monitored_barrier()通过类似确认机制的发送/接收通信原语实现主机端的屏障功能，从而使编号为0的节点能够报告哪些节点未能及时响应该屏障。例如，考虑以下代码：其中编号为 1 的进程未能调用 torch.distributed.monitored_barrier() 函数（实际上，这可能是由于应用程序存在缺陷，或是之前的集体操作导致了程序挂起）。代码如下：

```python
import os
from datetime import timedelta
import torch
import torch.distributed as dist
import torch.multiprocessing as mp

def worker(rank):
    dist.init_process_group("nccl", rank=rank, world_size=2)
    # monitored_barrier 需要 gloo 进程组来实现主机端的同步操作。
    group_gloo = dist.new_group(backend="gloo")
    if rank not in [1]:
        dist.monitored_barrier(group=group_gloo, timeout=timedelta(seconds=2))

if __name__ == "__main__":
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29501"
    mp.spawn(worker, nprocs=2, args=())
```

在编号为 0 的进程上会输出如下错误信息，帮助用户判断是哪个（哪些）进程出现了问题，并进一步排查原因：

```
RuntimeError: Rank 1 failed to pass monitoredBarrier in 2000 ms
Original exception: [gloo/transport/tcp/pair.cc:598] Connection closed by peer [2401:db00:eef0:1100:3560:0:1c05:25d]:8594
TORCH_DISTRIBUTED_DEBUG#
```

通过设置环境变量 TORCH_DISTRIBUTED_DEBUG，并将其值设为 INFO，即可启用更详细的日志记录以及集体同步检查功能，从而确保所有进程都能正确完成同步。该变量的取值可以根据调试需求设置为 OFF（默认值）、INFO 或 DETAIL。请注意，最详细的选项“DETAIL”可能会影响应用程序的性能，因此仅建议在调试问题时使用。将 TORCH_DISTRIBUTED_DEBUG 设置为 INFO 时，使用 torch.nn.parallel.DistributedDataParallel() 训练的模型在初始化时会生成额外的调试日志；而将其设置为 DETAIL，则会在部分迭代过程中额外记录运行时的性能统计信息。这些性能统计数据包括前向传播时间、反向传播时间、梯度通信时间等。例如，在以下代码中：import os import torch import torch.distributed as dist import torch.multiprocessing as mp class TwoLinLayerNet(torch.nn.Module): def __init__(self): super().__init__() self.a = torch.nn.Linear(10, 10, bias=False) self.b = torch.nn.Linear(10, 1, bias=False) def forward(self, x): a = self.a(x) b = self.b(x) return (a, b) def worker(rank): dist.init_process_group("nccl", rank=rank, world_size=2) torch.cuda.set_device(rank) print("init model") model = TwoLinLayerNet().cuda() print("init ddp") ddp_model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[rank]) inp = torch.randn(10, 10).cuda() print("train") for _ in range(20): output = ddp_model(inp) loss = output[0] + output[1] loss.sum().backward() if __name__ == "__main__":os.environ["MASTER_ADDR"] = "localhost"  
os.environ["MASTER_PORT"] = "29501"  
os.environ["TORCH_CPP_LOG_LEVEL"] = "INFO"  
os.environ["TORCH_DISTRIBUTED_DEBUG"] = "DETAIL"  # 设置为DETAIL可获取运行时日志。  
mp.spawn(worker, nprocs=2, args=())  

在初始化阶段会输出以下日志：  
I0607 16:10:35.739390 515217 logger.cpp:173] [Rank 0]: DDP已初始化，相关参数如下：  
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

TORCH_DISTRIBUTED_DEBUG设置为INFO时，运行期间会输出以下日志：  
I0607 16:18:58.085681 544067 logger.cpp:344] [Rank 1 / 2] 正在训练TwoLinLayerNet模型，未使用参数大小为0：  
平均前向计算时间：40838608  
平均反向计算时间：5983335  
平均反向通信时间：4326421  
平均反向通信与计算重叠时间：4207652  

I0607 16:18:58.085693 544066 logger.cpp:344] [Rank 0 / 2] 正在训练TwoLinLayerNet模型，未使用参数大小为0：  
平均前向计算时间：42850427  
平均反向计算时间：3885553  
平均反向通信时间：2357981  
平均反向通信与计算重叠时间：2234674 此外，设置 TORCH_DISTRIBUTED_DEBUG=INFO 可以增强 torch.nn.parallel.DistributedDataParallel() 在遇到模型中存在未使用参数时的崩溃日志记录功能。目前，如果模型中的某些参数在前向传播过程中可能不会被使用，就必须在初始化 torch.nn.parallel.DistributedDataParallel() 时设置 find_unused_parameters=True；而从 v1.10 版本开始，由于该模块在反向传播时不支持未使用的参数，因此所有模型输出都必须被用于损失计算。对于较大的模型而言，这些限制尤为具有挑战性。因此，当发生崩溃错误时，torch.nn.parallel.DistributedDataParallel() 会记录下所有未被使用参数的完整名称。例如，在上述应用中，如果我们将损失函数改为 loss = output[1]，那么 TwoLinLayerNet.a 在反向传播过程中就不会收到梯度，从而导致 DDP 模块失效。在发生崩溃时，系统会向用户提供有关未使用参数的信息，而对于大型模型来说，手动查找这些参数可能会相当困难：RuntimeError: Expected to have finished reduction in the prior iteration before starting a new one。该错误表明您的模块中存在未被用于计算损失的参数。您可以通过向 torch.nn.parallel.DistributedDataParallel() 传递关键字参数 `find_unused_parameters=True` 来启用未使用参数检测，并确保所有 `forward` 函数的输出都能参与损失计算。如果您已经完成了上述操作，那么分布式数据并行模块仍无法在您所定义模块的 `forward` 函数返回值中找到输出张量。在报告此问题时，请同时提供损失函数以及该模块 `forward` 函数返回值的结构（例如列表、字典或可迭代对象）。对于 rank 0 而言，未获取梯度的相关参数为：a.weight；未获取梯度的参数索引为：0。将环境变量 TORCH_DISTRIBUTED_DEBUG 设定为 DETAIL 后，系统会对用户直接或间接发起的每一个集合操作调用（如 DDP allreduce）进行额外的一致性和同步性检查。实现这一功能的方式是创建一个包装进程组，该组会封装由 torch.distributed.init_process_group() 和 torch.distributed.new_group() 接口返回的所有进程组。这样一来，这些接口返回的将是一个包装进程组，其使用方式与普通进程组完全相同，但在将集合操作下发给底层进程组之前会先执行一致性检查。目前，这些检查包括使用 torch.distributed.monitored_barrier() 确保所有节点都完成尚未处理的集合操作，并标识出那些陷入停滞的节点。随后，系统还会对集合操作本身进行一致性验证，确保所有集合函数均匹配且以一致的张量形状被调用。若未能满足这些条件，应用程序崩溃时将会生成详细的错误报告，而不会出现程序挂起或仅显示无用错误信息的情况。例如，考虑以下在调用 `torch.distributed.all_reduce()` 时输入张量形状不匹配的函数：  
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
使用 NCCL 后端时，此类程序很可能会导致程序挂起，在较为复杂的场景下很难定位根本原因。如果用户将 `TORCH_DISTRIBUTED_DEBUG` 设置为 `DETAIL` 并重新运行程序，会出现如下错误信息，从而揭示问题根源：  
`RuntimeError: Error when verifying shape tensors for collective ALLREDUCE on rank 0. This likely indicates that input shapes into the collective are mismatched across ranks. Got shapes: 10 [ torch.LongTensor{1} ]`  
**注意**：若需在运行时更精细地控制调试级别，还可以使用 `torch.distributed.set_debug_level()`、`torch.distributed.set_debug_level_from_env()` 和 `torch.distributed.get_debug_level()` 这些函数。此外，当检测到集体同步异常时，可将 TORCH_DISTRIBUTED_DEBUG=DETAIL 与 TORCH_SHOW_CPP_STACKTRACES=1 结合使用，从而记录完整的调用栈信息。这类集体同步异常检测功能适用于所有基于 torch.distributed.init_process_group() 和 torch.distributed.new_group() API 创建的进程组，并采用 c10d 集体调用机制的应用程序。在通过 torch.distributed.monitored_barrier() 以及 TORCH_DISTRIBUTED_DEBUG 提供显式调试支持之外，torch.distributed 的底层 C++ 库还会输出不同级别的日志信息。这些日志有助于了解分布式训练任务的执行状态，以及排查网络连接故障等问题。下表展示了如何通过组合使用 TORCH_CPP_LOG_LEVEL 和 TORCH_DISTRIBUTED_DEBUG 环境变量来调整日志级别：| TORCH_CPP_LOG_LEVEL | TORCH_DISTRIBUTED_DEBUG | 实际生效的日志级别 | | --- | --- | --- | | ERROR | 忽略 | Error | | WARNING | 忽略 | Warning | | INFO | 忽略 | Info | | INFO | Info | INFO | | Debug | Info | Debug | | DETAIL | Info | DETAIL | | Trace（即全部级别） | 分布式组件会抛出源自 RuntimeError 的自定义异常类型：torch.distributed.DistError——这是所有分布式异常的基类；torch.distributed.DistBackendError——当发生与后端相关的错误时，就会抛出此异常。例如，当使用 NCCL 后端时，如果用户试图使用 NCCL 库无法识别的 GPU，就会抛出异常。torch.distributed.DistNetworkError：当网络库出现错误时（如“对端已重置连接”）会触发此异常。torch.distributed.DistStoreError：当存储模块发生错误时（如“TCPStore 超时”）会触发此异常。class torch.distributed.DistError# 当分布式库中出现错误时引发的异常。class torch.distributed.DistBackendError# 当分布式模块的后端出现错误时引发的异常。class torch.distributed.DistNetworkError# 当分布式模块的网络连接出现错误时引发的异常。class torch.distributed.DistStoreError# 当分布式存储模块出现错误时引发的异常。如果您正在进行单节点训练，可以通过交互式方式在脚本中设置断点，这会非常方便。我们提供了专门用于在单个节点上设置断点的方法：torch.distributed.breakpoint(rank=0, skip=0, timeout_s=3600) [source]# 仅在一个节点上设置断点，其他所有节点将会等待您完成断点操作后再继续运行。参数：rank（整数）——指定要在哪个节点上设置断点。默认值为 0；skip（整数）——跳过前几次对该断点的触发请求。默认值为 0。

```
torch.distributed
```

**模式 3：初始化**# 在调用其他任何方法之前，必须先使用 `torch.distributed.init_process_group()` 或 `torch.distributed.device_mesh.init_device_mesh()` 函数对相关包进行初始化。这两个函数会阻塞执行，直到所有进程都加入进程组为止。注意：初始化操作并非线程安全操作。为避免各进程之间的“UUID”分配出现不一致，以及防止初始化过程中的竞态条件导致程序挂起，进程组的创建应在单个线程中完成。`torch.distributed.is_available()`[来源]# 如果支持分布式功能，则返回 `True`；否则，`torch.distributed` 不会提供其他任何 API。目前，`torch.distributed` 已在 Linux、MacOS 和 Windows 系统上可用。若要从源代码构建 PyTorch，可设置 `USE_DISTRIBUTED=1` 来启用该功能。当前，Linux 和 Windows 的默认值为 `USE_DISTRIBUTED=1`，而 MacOS 的默认值为 `USE_DISTRIBUTED=0`。返回类型：`bool`。`torch.distributed.init_process_group(backend=None, init_method=None, timeout=None, world_size=-1, rank=-1, store=None, group_name='', pg_options=None, device_id=None)`[来源]# 初始化默认的分布式进程组，此操作同时也会初始化分布式功能模块。初始化进程组主要有两种方式：一是明确指定存储位置、进程编号以及进程总数；二是指定 `init_method`（一个 URL 字符串），用以指示从何处及如何发现其他节点。也可选择性地指定进程编号和进程总数，或者将所有必要参数编码到 URL 中而省略这些参数。如果两者均未指定，则默认认为 `init_method` 为 “env://”。parameters backend（字符串或Backend类型，可选）——需使用的后端类型。根据构建时的配置，有效值包括mpi、gloo、nccl、ucc、xccl，或是第三方插件注册的其他后端。自2.6版本起，若未指定backend，则c10d会使用由device_id参数（如有提供）所指定的设备类型对应的已注册后端。目前已知的默认映射关系为：cuda对应nccl，cpu对应gloo，xpu对应xccl。如果既未指定backend也未指定device_id，c10d会在运行时自动检测机器上的加速器，并使用该加速器（或CPU）对应的已注册后端。此字段也可以小写字符串形式指定（例如“gloo”），同时可通过Backend属性访问（如Backend.GLOO）。当使用nccl后端且每台机器上运行多个进程时，每个进程必须对其使用的所有GPU拥有独占访问权，因为进程间共享GPU可能会导致死锁或NCCL使用异常。ucc后端仍处于实验阶段。可通过get_default_backend_for_device()函数查询该设备的默认后端。init_method（字符串，可选）——用于指定进程组初始化方式的URL。若未指定init_method或store，则默认值为“env://”。该参数与store为互斥关系。world_size（整数，可选）——参与任务的进程数量。若指定了store，则此参数为必填项。rank（整数，可选）——当前进程的排名（数值范围应为0到world_size-1之间）。若指定了存储地址，则此参数为必填项。  
store（存储地址，可选）——所有工作进程均可访问的键值存储，用于交换连接信息及地址信息。该参数与init_method参数互斥。  
timeout（超时时间，timedelta类型，可选）——针对进程组执行的操作设定的超时时间。对于NCCL后端，默认值为10分钟；其他后端默认值为30分钟。达到此超时时间后，集体操作将异步终止，相关进程也会崩溃。之所以如此设置，是因为CUDA执行是异步的，一旦NCCL异步操作失败，后续的CUDA操作可能会在损坏的数据上运行，继续执行用户代码已不再安全。当设置了TORCH_NCCL_BLOCKING_WAIT时，进程将会阻塞并等待超时发生。  
group_name（组名，str类型，可选，已废弃）——进程组的名称。此参数当前会被忽略。  
pg_options（进程组选项，ProcessGroupOptions类型，可选）——用于指定在构建特定进程组时需要传递的额外选项。目前，我们仅支持NCCL后端的ProcessGroupNCCL.Options选项；还可指定is_high_priority_stream，以便在有计算内核等待时让NCCL后端优先处理高优先级的CUDA流。如需了解NCCL的其他配置选项，请参阅https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-t。  
device_id（torch.device类型 | int类型，可选）——指定该进程将要使用的特定设备，从而实现针对不同后端的优化。目前该参数具有两种作用，且仅在 NCCL 环境下生效：其一为会立即创建通信器（直接调用 ncclCommInit* 而非常规的延迟调用方式）；其二为子群组会在可能的情况下使用 ncclCommSplit，从而避免不必要的群组创建开销。如果您希望尽早获知 NCCL 初始化错误，也可使用该参数。若传入整数值，API 会假定在编译时所指定的加速器类型将被采用。注意：若要启用 Backend.MPI 后端，需在支持 MPI 的系统上从源代码构建 PyTorch。另外，对多后端的支持仍处于实验阶段。当前若未指定后端，则会同时创建 gloo 和 nccl 两种后端——对于使用 CPU 张量的集合操作，将采用 gloo 后端；而对于使用 CUDA 张量的集合操作，则会使用 nccl 后端。用户可通过传入格式为“<设备类型>:<后端名称>,<设备类型>:<后端名称>”的字符串来指定自定义后端，例如“cpu:gloo,cuda:custom_backend”。torch.distributed.device_mesh.init_device_mesh(device_type, mesh_shape, *, mesh_dim_names=None, backend_override=None) [来源]：该函数会根据 device_type、mesh_shape 以及 mesh_dim_names 参数来初始化 DeviceMesh。它所创建的 DeviceMesh 具有 n 维数组结构，其中 n 即为 mesh_shape 的长度。若提供了 mesh_dim_names，则每个维度会对应 mesh_dim_names[i] 所指定的名称。需要注意的是，init_device_mesh 遵循 SPMD 编程模型，即同一个 PyTorch Python 程序会在集群中的所有进程/节点上运行。请确保所有节点上的 `mesh_shape`（用于描述设备布局的 nD 数组的维度）完全一致。如果 `mesh_shape` 不同，可能会导致程序挂起。注意：如果未检测到进程组，`init_device_mesh` 会自动在后台初始化分布式通信所需的进程组。参数如下：`device_type`（字符串）——网格中的设备类型。目前支持 “cpu”、“cuda/cuda-like” 和 “xpu” 这几种类型。不允许传入包含 GPU 索引的设备类型，例如 “cuda:0”。`mesh_shape`（`Tuple[int]`）——用于定义描述设备布局的多维数组各维度大小的元组。`mesh_dim_names`（`Tuple[str]`，可选）——用于为描述设备布局的多维数组的每个维度指定名称的元组。其长度必须与 `mesh_shape` 的长度相同，且 `mesh_dim_names` 中的每个字符串都需唯一。`backend_override`（`Dict[int | str, tuple[str, Options] | str | Options]`，可选）——用于覆盖为每个网格维度所创建的某些或全部进程组的配置。每个键可以是维度的索引，也可以是其名称（前提是已提供 `mesh_dim_names`）。每个值可以是一个包含后端名称及其选项的元组，或者仅包含这两者之一（此时另一项将自动设置为默认值）。返回值：一个表示设备布局的 `DeviceMesh` 对象。返回类型：DeviceMesh  
示例：  
>>> from torch.distributed.device_mesh import init_device_mesh  
>>> >>> mesh_1d = init_device_mesh("cuda", mesh_shape=(8,))  
>>> mesh_2d = init_device_mesh("cuda", mesh_shape=(2, 8), mesh_dim_names=("dp", "tp"))  

torch.distributed.is_initialized()[source]  
# 检查默认进程组是否已初始化。返回类型：bool  

torch.distributed.is_mpi_available()[source]  
# 检查是否支持 MPI 后端。返回类型：bool  

torch.distributed.is_nccl_available()[source]  
# 检查是否支持 NCCL 后端。返回类型：bool  

torch.distributed.is_gloo_available()[source]  
# 检查是否支持 Gloo 后端。返回类型：bool  

torch.distributed.distributed_c10d.is_xccl_available()[source]  
# 检查是否支持 XCCL 后端。返回类型：bool  

torch.distributed.is_torchelastic_launched()[source]  
# 检查当前进程是否是通过 torch.distributed.elastic（又称 torchelastic）启动的。该函数通过检查 TORCHELASTIC_RUN_ID 环境变量的存在来推断当前进程是否由 torchelastic 启动。这一判断方式是合理的，因为 TORCHELASTIC_RUN_ID 会映射到寻址 ID，而该值始终非空，可用于识别进程身份以实现节点发现功能。返回类型：bool  

torch.distributed.get_default_backend_for_device(device)[source]  
# 返回指定设备的默认后端。参数：device（Union[str, torch.device]）——需要获取其默认后端的设备。该方法会以小写字符串的形式返回指定设备的默认后端。返回类型为字符串。目前支持三种初始化方式：TCP初始化——通过TCP进行初始化有两种方法，这两种方法都需要一个所有进程都能访问的网络地址以及指定的世界大小。第一种方法需要指定属于等级0进程的地址；此外，这种初始化方式要求所有进程都必须手动指定各自的等级。需要注意的是，在最新的分布式包中已不再支持多播地址，同时group_name也已过时。示例代码如下：import torch.distributed as dist # 使用某台机器的地址 dist.init_process_group(backend, init_method='tcp://10.1.1.20:23456', rank=args.rank, world_size=4) 共享文件系统初始化——另一种初始化方式是利用组内所有机器都能访问的共享文件系统，再结合指定的世界大小。对应的URL必须以file://开头，并指向共享文件系统中某个现有目录下并不存在的文件路径。如果该文件尚不存在，文件系统初始化会自动创建它，但不会删除该文件。因此，你有责任确保在再次调用init_process_group()使用相同的文件路径/名称之前，先清理掉该文件。同样需要注意的是，在最新的分布式包中已不再支持自动分配进程等级，group_name也已过时。警告：此方法假定文件系统支持使用 fcntl 进行锁定——大多数本地系统及 NFS 都具备该功能。另请注意，此方法总会创建文件，并会在程序执行结束后尽力清理并删除该文件。换言之，每次通过文件初始化方法进行初始化时，都需要一个全新的空文件才能确保初始化成功。如果再次使用上一次初始化所使用的同一文件（而该文件未能被及时清理），就会引发异常行为，进而常常导致死锁和故障。因此，尽管此方法会尽力清理文件，但如果自动删除操作未能成功，您仍有责任在训练结束时确保将该文件移除，以避免其在下次被重复使用。如果您计划对同一个文件名多次调用 init_process_group()，这一点尤为重要。也就是说，如果该文件未被移除或清理，而您又再次对该文件调用 init_process_group()，则很可能会出现故障。一个通用的原则是：每次调用 init_process_group() 时，都必须确保该文件不存在或为空。import torch.distributed as dist # 必须始终指定 rank 值 dist.init_process_group(backend, init_method='file:///mnt/nfs/sharedfile', world_size=4, rank=args.rank) 环境变量初始化# 此方法会从环境变量中读取配置，从而让用户能够完全自定义信息的获取方式。需要设置的变量包括：MASTER_PORT - 必填；必须是编号为 0 的节点上可用的端口 MASTER_ADDR - 必填（编号为 0 的节点除外）；编号为 0 的节点的地址 WORLD_SIZE - 必填；既可以在此处设置，也可以在调用 init 函数时设置 RANK - 必填；既可以在此处设置，也可以在调用 init 函数时设置 编号为 0 的节点将用于建立所有连接。这是默认方法，因此无需指定 init_method（或者可以设置为 env://）。缩短初始化时间# TORCH_GLOO_LAZY_INIT - 采用按需建立连接的方式，而非使用全网格结构，这能有效缩短非 all2all 操作的初始化时间。

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

**模式 5：分组**# 默认情况下，集合操作会在默认分组（也称为世界）中执行，要求所有进程都参与分布式函数调用。不过，某些工作负载能够从更细粒度的通信中受益，这时就需要用到分布式分组了。可以使用 `new_group()` 函数来创建新的分组，这些分组可以包含所有进程中的任意子集。该函数会返回一个不可见的分组句柄，可作为参数传递给所有的集合操作函数（集合操作函数是用于在某些常见编程模式中进行信息交换的分布式函数）。参考代码：`torch.distributed.new_group(ranks=None, timeout=None, backend=None, pg_options=None, use_local_synchronization=False, group_desc=None, device_id=None)` [来源]# 创建一个新的分布式分组。该函数要求主分组中的所有进程（即属于该分布式任务的所有进程）都必须调用此函数，即便它们日后不会成为该分组的成员。此外，所有进程创建分组的顺序也必须保持一致。警告：安全并发使用注意事项——当使用 NCCL 后端同时运行多个进程组时，用户必须确保各进程之间集合操作的执行顺序具有全局一致性。如果一个进程内的多个线程发起集合操作，则需要通过显式同步机制来保证执行顺序的一致性。在使用 `torch.distributed` 通信 API 的异步版本时，系统会返回一个工作对象，同时将通信操作放入独立的 CUDA 流中处理，从而实现通信与计算的同时进行。在一个进程组中发起一个或多个异步操作后，在使用另一个进程组之前，必须先通过调用 `work.wait()` 方法将这些操作与其他 CUDA 流同步。更多详细信息请参阅《同时使用多个 NCCL 通信器》<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html#using-multiple-nccl-communicators-concurrently>。

**参数说明：**
- `ranks`（`list[int]`）——进程组成员的等级列表。若未指定，则默认为所有等级。默认值为 `None`。
- `timeout`（`timedelta`，可选）——详细信息及默认值请参见 `init_process_group` 的文档。
- `backend`（`str` 或 `Backend`，可选）——要使用的后端类型。根据构建时的配置，有效值为 `gloo` 和 `nccl`。默认情况下会使用与全局进程组相同的后端。该参数应以小写字符串形式指定（例如 `"gloo"`），也可通过 `Backend` 属性访问（例如 `Backend.GLOO`）。若未指定，则会使用默认进程组对应的后端。默认值为 `None`。
- `pg_options`（`ProcessGroupOptions`，可选）——进程组选项，用于指定在构建特定进程组时需要传递的额外参数。例如，在使用 NCCL 后端时，可以指定 `is_high_priority_stream`，从而使该进程组能够使用优先级较高的 CUDA 流。如需了解配置 nccl 的其他可用选项，请参阅 https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-tuse_local_synchronization。该参数为布尔类型，可选：在进程组创建完成后执行组内本地屏障同步。其特点在于，非组成员无需调用相关 API，也不会参与该屏障同步操作。group_desc（字符串，可选）：用于描述进程组的字符串。device_id（torch.device 类型，可选）：指定要将该进程“绑定”到的单个特定设备；如果提供了此参数，new_group 函数会立即尝试为该设备初始化通信后端。函数返回值为一个分布式组句柄，可用于集体调用操作；若当前进程不属于该组，则返回 GroupMember.NON_GROUP_MEMBER。注意：use_local_synchronization 参数不支持 MPI 模式。注意：虽然当集群规模较大且进程组规模较小时，设置 use_local_synchronization=True 可显著提升性能，但由于非组成员不会参与 group barrier() 操作，这会改变整个集群的行为，因此使用时需格外谨慎。注意：如果每个进程都创建多个重叠的进程组，设置 use_local_synchronization=True 可能会导致死锁。为避免这种情况，请确保所有进程遵循相同的全局创建顺序。torch.distributed.get_group_rank(group, global_rank) [来源]：将全局进程序号转换为组内进程序号；若 global_rank 不属于该组，则会引发 RuntimeError 错误。参数 group (ProcessGroup) – 用于确定相对排名的进程组。global_rank (int) – 需要查询的全局排名。返回该全局排名在对应进程组中的排名。返回类型：int。注意：在默认进程组上调用此函数将返回恒等值。torch.distributed.get_global_rank(group, group_rank)[来源]# 将进程组内的排名转换为全局排名。group_rank 必须属于该进程组，否则会引发 RuntimeError。参数 group (ProcessGroup) – 用于确定全局排名的进程组。group_rank (int) – 需要查询的进程组内排名。返回该进程组内排名对应的全局排名。返回类型：int。注意：在默认进程组上调用此函数将返回恒等值。torch.distributed.get_process_group_ranks(group)[来源]# 获取与指定进程组相关的所有排名。参数 group (Optional[ProcessGroup]) – 用于获取所有排名的进程组。如果未指定，则使用默认进程组。返回按进程组内排名顺序排列的全局排名列表。返回类型：list[int]

```
new_group()
```

**模式 6：** 警告：安全并发使用注意事项。当使用 NCCL 后端时，若涉及多个进程组，用户必须确保所有节点上集合操作的执行顺序保持全局一致。如果一个进程内的多个线程同时发起集合操作，则需要通过显式同步机制来保证执行顺序的统一。而使用 `torch.distributed` 通信 API 的异步版本时，系统会返回一个工作对象，并将通信内核任务放入独立的 CUDA 流中处理，从而实现通信与计算操作的并行执行。一旦某个进程组已发起一个或多个异步操作，在使用其他进程组之前，必须先通过调用 `work.wait()` 方法将其与其他 CUDA 流同步。更多详细信息请参阅《同时使用多个 NCCL 通信器》<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html#using-multiple-nccl-communicators-concurrently>。

```
NCCL
```

**模式 7：** 注意，如果您同时使用 DistributedDataParallel 与分布式 RPC 框架，那么计算梯度时应始终使用 `torch.distributed.autograd.backward()`，而参数优化则应通过 `torch.distributed.optim.DistributedOptimizer` 来实现。示例如下：>>> import torch.distributed.autograd as dist_autograd >>> from torch.nn.parallel import DistributedDataParallel as DDP >>> import torch >>> from torch import optim >>> from torch.distributed.optim import DistributedOptimizer >>> import torch.distributed.rpc as rpc >>> from torch.distributed.rpc import RRef >>> >>> t1 = torch.rand((3, 3), requires_grad=True) >>> t2 = torch.rand((3, 3), requires_grad=True) >>> rref = rpc.remote("worker1", torch.add, args=(t1, t2)) >>> ddp_model = DDP(my_model) >>> >>> # 设置优化器 >>> optimizer_params = [rref] >>> for param in ddp_model.parameters(): >>> optimizer_params.append(RRef(param)) >>> >>> dist_optim = DistributedOptimizer( >>> optim.SGD, >>> optimizer_params, >>> lr=0.05, >>> ) >>> >>> with dist_autograd.context() as context_id: >>> pred = ddp_model(rref.to_here()) >>> loss = loss_func(pred, target) >>> dist_autograd.backward(context_id, [loss]) >>> dist_optim.step(context_id)

```
torch.distributed.autograd.backward()
```

**模式 8：** static_graph（布尔值）——当该参数设置为 True 时，DDP 会识别出训练好的模型图是静态的。所谓静态图，意味着：1）在整个训练过程中，已使用和未使用的参数集合不会发生变化；在这种情况下，无论用户是否将 find_unused_parameters 设置为 True 都没有影响。2）模型的训练方式在整个训练过程中也不会改变（即不存在随迭代次数变化的控制流）。当 static_graph 设为 True 时，DDP 能够支持以往无法处理的情况，包括：1）递归反向传播；2）多次进行激活值检查点保存；3）在模型存在未使用参数时进行激活值检查点保存；4）前向函数之外存在模型参数。此外，由于当 static_graph 设为 True 时 DDP 不会在每次迭代中都搜索图结构以检测未使用的参数，因此有可能提升性能。要判断是否可以将 static_graph 设置为 True，一种方法是可以查看之前模型训练结束时的 DDP 日志数据，如果 ddp_logging_data.get("can_set_static_graph") 的值为 True，通常就可以将 static_graph 设为 True。示例：>>> model_DDP = torch.nn.parallel.DistributedDataParallel(model) >>> # 训练循环 >>> ... >>> ddp_logging_data = model_DDP._get_ddp_logging_data() >>> static_graph = ddp_logging_data.get("can_set_static_graph")

```
True
```

