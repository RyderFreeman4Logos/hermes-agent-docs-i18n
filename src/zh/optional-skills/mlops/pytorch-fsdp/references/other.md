# Pytorch-Fsdp - 其他内容

**页数：** 15

---

## 分布式数据并行#

**URL：** https://pytorch.org/docs/stable/notes/ddp.html

**目录：**
- 分布式数据并行#
- 示例#
- 内部设计#
- 实现方式#
  - ProcessGroup#
  - DistributedDataParallel#
  - TorchDynamo DDPOptimizer#

创建时间：2020年1月15日 | 最后更新时间：2024年1月25日

torch.nn.parallel.DistributedDataParallel的实现会随着时间不断演进。本设计文档基于v1.4版本的状态编写。

torch.nn.parallel.DistributedDataParallel（简称DDP）能够以透明方式实现分布式数据并行训练。本页面将介绍其工作原理，并揭示相关的实现细节。

我们先从一个简单的torch.nn.parallel.DistributedDataParallel示例开始。该示例使用torch.nn.Linear作为本地模型，将其用DDP封装后，对该模型执行一次前向传播、一次反向传播以及一次优化器更新操作。之后，本地模型中的参数将会被更新，且不同进程中的所有模型状态应完全一致。

DDP可与TorchDynamo配合使用。在使用TorchDynamo时，需在编译模型之前先应用DDP模型封装器，这样TorchDynamo就能根据DDP的桶大小应用DDPOptimizer（用于图结构优化）。（更多信息请参见TorchDynamo DDPOptimizer。）

本节将通过详细分析单次迭代中的每一步，揭示torch.nn.parallel.DistributedDataParallel背后的工作原理。

前置条件：DDP依赖c10d ProcessGroup进行通信。因此，在构建DDP之前，应用程序必须先创建ProcessGroup实例。

构建过程：DDP的构造函数会接收本地模块的引用，然后将秩为0的进程中的state_dict()数据广播给组内的所有其他进程，以确保所有模型副本都从完全相同的状态开始运行。随后，每个DDP进程都会创建一个本地Reducer，该Reducer负责在反向传播过程中同步梯度。为提升通信效率，Reducer会将参数梯度分组到不同的“桶”中，并逐个处理这些桶。可以通过在DDP构造函数中设置bucket_cap_mb参数来配置桶的大小。参数梯度与桶的对应关系是在构建阶段根据桶大小限制和参数大小确定的。模型参数会按照（大致）与模型中的Model.parameters()相反的顺序被分配到各个桶中。采用相反顺序的原因是，DDP期望在反向传播过程中，梯度能以大致相同的顺序准备好。下图展示了一个示例。注意，grad0和grad1位于bucket1中，而另外两个梯度则位于bucket0中。当然，这一假设并不总是成立，一旦出现这种情况，就可能会降低DDP的反向传播速度，因为Reducer无法尽早启动通信。除了分组之外，Reducer在构建过程中还会为每个参数注册自动求导钩子。当梯度准备好时，这些钩子会在反向传播过程中被触发。

前向传播：DDP会接收输入并将其传递给本地模型，如果设置了find_unused_parameters为True，它还会分析本地模型的输出。该模式允许对模型的子图进行反向传播，DDP会从模型输出开始遍历自动求导图，找出参与反向传播的参数，并将所有未使用的参数标记为可进行梯度归约。在反向传播过程中，Reducer只会等待那些尚未准备好的参数，但仍会处理所有桶中的数据。目前，将参数梯度标记为已准备好并不能让DDP跳过某些桶，但可以避免其在反向传播过程中无限期地等待缺失的梯度。需要注意的是，遍历自动求导图会增加额外的开销，因此应用程序应仅在必要时将find_unused_parameters设置为True。

反向传播：反向传播操作是直接在损失张量上调用的，而损失张量不在DDP的控制范围内。DDP会利用构建阶段注册的自动求导钩子来触发梯度同步。当某个梯度准备好后，该梯度对应的累加器上的DDP钩子就会被触发，DDP随后会将该参数梯度标记为可进行归约。当一个桶中的所有梯度都准备好后，Reducer会启动针对该桶的异步allreduce操作，计算所有进程中这些梯度的平均值。当所有桶都准备好后，Reducer会暂停执行，等待所有的allreduce操作完成。完成后，平均后的梯度会被写入所有参数的param.grad字段。因此，在反向传播之后，不同DDP进程中对应参数的grad字段值应保持一致。

优化器更新步骤：从优化器的角度来看，它是在优化一个本地模型。由于所有DDP进程中的模型副本都从相同的状态开始，并且在每次迭代中都具有相同的平均梯度，因此它们能够保持同步。

DDP要求所有进程中的Reducer实例以完全相同的顺序调用allreduce操作，为此它会始终按照桶的索引顺序而非实际准备就绪的顺序来执行allreduce操作。如果不同进程之间的allreduce顺序不一致，可能会导致错误结果或使DDP的反向传播过程卡住。

以下是DDP实现各组件的链接。堆叠图展示了代码的结构。

ProcessGroup.hpp：包含所有进程组实现的抽象API。c10d库预置了3种实现，分别是ProcessGroupGloo、ProcessGroupNCCL和ProcessGroupMPI。DistributedDataParallel在初始化时会使用ProcessGroup::broadcast()将模型状态从秩为0的进程发送给其他进程，同时使用ProcessGroup::allreduce()来求和梯度。

Store.hpp：为进程组实例之间的通信对齐服务提供支持。

distributed.py：是DDP的Python入口文件。它实现了nn.parallel.DistributedDataParallel模块的初始化步骤和前向传播函数，这些函数会调用C++库。其_sync_param函数用于在某个DDP进程在多个设备上运行时实现进程内的参数同步，同时还会将模型缓冲区从秩为0的进程广播给其他所有进程。进程间的参数同步则由Reducer.cpp负责处理。

comm.h：实现了合并广播辅助函数，该函数会在初始化时用于广播模型状态，在前向传播之前用于同步模型缓冲区。

reducer.h：提供了反向传播过程中梯度同步的核心实现。它包含三个入口函数：

Reducer：其构造函数在distributed.py中被调用，该函数会将Reducer::autograd_hook()注册到梯度累加器中。

autograd_hook()函数会在梯度准备好时由自动求导引擎触发。

prepare_for_backward()函数在distributed.py中的DDP前向传播结束后被调用。如果DDP构造函数中设置了find_unused_parameters为True，该函数会遍历自动求导图，找出未使用的参数。

DDP的性能优势在于能够在反向传播过程中的计算任务与allreduce操作之间实现重叠。当使用TorchDynamo编译完整的正向和反向图时，AotAutograd会阻止这种重叠，因为allreduce操作会在整个优化后的反向计算完成后，由自动求导钩子来触发。

TorchDynamo的DDPOptimizer则通过在反向传播过程中，在DDP allreduce操作的逻辑边界处拆分正向图来发挥作用。注意：其目标是在反向传播过程中拆分图结构，最简单的实现方式是先拆分正向图，然后对每个部分分别应用AotAutograd并进行编译。这样就能让DDP在反向传播的各个阶段之间触发allreduce钩子，从而安排通信操作与计算操作重叠。

如需更深入的解释和实验结果，请参阅相关博客文章，或查看torch/_dynamo/optimizations/distributed.py中的文档和代码。

若要调试DDPOptimizer，可设置TORCH_LOGS=’ddp_graphs’以获取完整的图结构输出。若只需不含图结构的日志，可在TORCH_LOGS中添加‘dynamo’、‘distributed’或‘dist_ddp’中的任意一个选项（用于获取关于桶边界的简要信息）。如需禁用DDPOptimizer，可设置torch._dynamo.config.optimize_ddp=False。即使不使用DDPOptimizer，DDP和TorchDynamo仍能正常工作，但性能会有所下降。

---

## PyTorch文档#

**URL：** https://pytorch.org/docs/stable/

**目录：**
- PyTorch文档#
- 索引与表格#

PyTorch是一个针对深度学习优化的张量库，支持GPU和CPU运算。

本文档中介绍的功能会根据其发布状态分为不同类别：

稳定版（API-Stable）：这类功能将长期得到维护，通常不存在重大的性能问题或文档缺失情况。我们也会努力保持向后兼容性（不过也可能会出现破坏性变更，届时会提前一个版本发布通知）。

不稳定版（API-Unstable）：这类功能正处于开发阶段，其API可能会根据用户反馈、性能提升需求或操作符覆盖范围的完整性要求而发生变化。这些功能的API和性能特性都可能发生改变。

---

## 通用连接上下文管理器#

**URL：** https://pytorch.org/docs/stable/distributed.algorithms.join.html

**目录：**
- 通用连接上下文管理器#

创建时间：2025年6月6日 | 最后更新时间：2025年6月6日

通用连接上下文管理器可用于在输入数据不均匀的情况下进行分布式训练。本页面介绍了相关类（Join、Joinable和JoinHook）的API。相关教程请参阅《使用连接上下文管理器对不均匀输入数据进行分布式训练》。

该类定义了通用连接上下文管理器，它允许在进程完成连接后调用自定义钩子函数。

这些钩子函数的作用是屏蔽未连接进程的集体通信操作，从而避免程序卡住或出现错误，并确保算法的正确性。有关钩子定义的详细信息，请参阅JoinHook文档。

该上下文管理器要求每个参与的Joinable在自身进行每次迭代前的集体通信之前，先调用notify_join_context()方法，以确保计算正确性。

该上下文管理器还要求所有JoinHook对象中的process_group属性必须一致。如果存在多个JoinHook对象，则以第一个对象的设备作为默认设备。进程组和设备信息会被用于检测未连接的进程，同时如果在throw_on_early_termination选项被启用，还会通过all_reduce操作通知相关进程抛出异常。

joinables（List[Joinable]）—— 一个包含所有参与连接的Joinable对象的列表，其钩子会按照给定的顺序依次被遍历。enable (bool) – 用于启用不均匀输入检测的标志；将其设置为 False 可禁用上下文管理器的相应功能，仅应在用户确定输入不会不均匀时使用（默认值为 True）。

throw_on_early_termination (bool) – 用于控制在检测到不均匀输入时是否抛出异常的标志（默认值为 False）。

该函数会通知 join 上下文管理器：调用进程尚未加入。

随后，如果 throw_on_early_termination=True，则会检查是否已检测到不均匀输入（即是否有进程已加入），若有则抛出异常。

此方法应在可加入进程的对象（Joinable）执行每次迭代前的集合通信之前被调用。例如，在 DistributedDataParallel 的前向传播开始时即可调用此方法。

只有传递给上下文管理器的第一个可加入进程对象会在此方法中执行集合通信，对于其他对象而言，此方法不会执行任何操作。

joinable (Joinable) – 调用此方法的可加入进程对象。

一个用于全量聚合操作的异步工作句柄，若该对象是第一个传递给上下文管理器的可加入进程，则用于通知上下文管理器进程尚未加入；否则为 None。

这为可加入进程类定义了一个抽象基类。

从 Joinable 继承的可加入进程类除了需要实现返回设备信息的 join_device() 和返回进程组信息的 join_process_group() 方法外，还必须实现 join_hook() 方法，该方法需返回一个 JoinHook 实例。

返回用于执行 join 上下文管理器所需集合通信的设备。

为指定的可加入进程对象返回一个 JoinHook 实例。

kwargs (dict) – 一个包含用于在运行时修改连接钩子行为的任意关键字参数的字典；所有共享同一 join 上下文管理器的可加入进程对象都会接收到相同的 kwargs 值。

返回 join 上下文管理器自身所需集合通信的进程组。

这定义了一个连接钩子，它在 join 上下文管理器中提供了两个入口点。

入口点包括：主钩子，在存在尚未加入的进程时会被反复调用；以及后钩子，在所有进程都加入后仅被调用一次。

若要为通用的 join 上下文管理器实现连接钩子，需定义一个继承自 JoinHook 的类，并根据需要重写 main_hook() 和 post_hook() 方法。

在训练迭代中，当存在尚未加入的进程时调用此钩子，以此替代原有的集合通信操作。

训练迭代指的是一次前向传播、一次反向传播以及一个优化器步骤。

在所有进程都加入后调用该钩子。

该方法还会接收一个额外的布尔参数 is_last_joiner，用于指示当前进程是否属于最后加入的进程之一。

is_last_joiner (bool) – 若当前进程属于最后加入的进程之一，则为 True；否则为 False。该功能会对该进程组中所有进程的输入张量进行归约与散布操作。

更多详细信息请参阅 torch.distributed.reduce_scatter()。

该功能会对该进程组中所有进程的输入张量进行归约与散布操作。

更多详细信息请参阅 torch.distributed.reduce_scatter()。

scatter(self: torch._C._distributed_c10d.ProcessGroup, output_tensors: collections.abc.Sequence[torch.Tensor], input_tensors: collections.abc.Sequence[collections.abc.Sequence[torch.Tensor]], opts: torch._C._distributed_c10d.ScatterOptions = <torch._C._distributed_c10d.ScatterOptions object at 0x7f0162b879f0>) -> c10d::Work

该功能会将该进程组中所有进程的输入张量进行散布操作。

更多详细信息请参阅 torch.distributed.scatter()。

scatter(self: torch._C._distributed_c10d.ProcessGroup, output_tensor: torch.Tensor, input_tensors: collections.abc.Sequence[torch.Tensor], root: typing.SupportsInt, timeout: datetime.timedelta | None = None) -> c10d::Work

该功能会将该进程组中所有进程的输入张量进行散布操作。

更多详细信息请参阅 torch.distributed.scatter()。

该功能会将张量发送到指定的进程序号。

更多详细信息请参阅 torch.distributed.send()。

该功能可设置所有后续操作的默认超时时间。

该功能用于关闭进程组。

该功能用于获取当前进程组的大小。

该功能用于定义进程组创建器所遵循的协议。

该功能用于获取当前的进程组。为线程本地方法。

该参数表示当前的进程组。

该功能用于使用指定的后端和选项创建一个新的进程组。此类进程组是独立的，不会被全局注册，因此无法通过标准的 torch.distributed.* API 使用。

backend (str) – 用于构建进程组的后端类型。

timeout (timedelta) – 集群操作的超时时间。

device (Union[str, device]) – 用于构建进程组的设备。

**kwargs (object) – 其余所有参数都会被传递给对应的后端构造函数。具体详情请参阅各后端的具体文档。**

该功能为进程组提供上下文管理器。为线程本地方法。

pg (ProcessGroup) – 需要使用的进程组对象。

Generator[None, None, None]

该功能用于注册新的进程组后端。

name (str) – 后端的名称。

func (ProcessGroupFactory) – 用于创建进程组的函数。

---

## torch.distributed.fsdp.fully_shard#

**URL:** https://pytorch.org/docs/stable/distributed.fsdp.fully_shard.html

**Contents:**
- torch.distributed.fsdp.fully_shard#
- PyTorch FSDP2 (fully_shard)#

创建时间：2024年12月4日 | 最后更新时间：2025年6月16日

PyTorch FSDP2（RFC版本）提供了一种完全分片式的数据并行实现方案，旨在在保持高性能的即时模式的同时，通过参数级分片提升使用便捷性。

更多相关信息请参阅《FSDP2入门指南》。

如果您目前使用的是FSDP1，建议参考我们的迁移指南将系统升级到FSDP2。

fully_shard(model) 的用户使用约定如下：

在模型初始化阶段，fully_shard会直接将model.parameters()中的普通torch.Tensor转换为DTensor。这些参数会根据设备网格被分配到相应的设备上。

在前向和反向传播之前，预前向/预反向钩子会负责将所有参数收集起来，并将model.parameters()从DTensor转换回普通的torch.Tensor。

在前向和反向传播之后，后前向/后反向钩子会释放那些未被分片的参数（无需进行通信操作），并将model.parameters()从普通torch.Tensor重新转换为DTensor。

对于优化器而言，必须使用DTensor类型的model.parameters()来初始化它，且优化器的更新操作也应在DTensor参数上执行。

若要触发预前向钩子以收集参数，请调用model(input)而非model.forward(input)。若要让model.forward(input)能够正常工作，用户要么显式调用model.unshard()，要么使用register_fsdp_forward_method(model, "forward")来注册相应的前向方法以便被钩子调用。

fully_shard会将参数分组，以便通过一次操作完成全部收集。建议以自底向上的方式应用此功能。例如，在Transformer模型中，应先对每一层应用fully_shard，然后再对整个根模型应用该功能。当对根模型应用fully_shard时，它会排除各层中的参数，将剩余的参数（如嵌入层参数、输出投影参数等）汇总为一个整体，以便一次性收集。

type(model)会直接与FSDPModule“联合”在一起。例如，如果模型原本的类型是nn.Linear，那么fully_shard会直接将其类型从nn.Linear改为FSDPLinear。FSDPLinear既是nn.Linear的实例，也是FSDPModule的实例。它既保留了nn.Linear的所有方法，还通过FSDPModule提供了FSDP2特有的API，如reshard()和unshard()。

参数的完全限定名保持不变。如果我们调用model.state_dict()，在应用fully_shard之前和之后，这些完全限定名都是相同的。这是因为fully_shard并不会对模块进行包装，而只是向原始模块注册钩子而已。

与PyTorch FSDP1（FullyShardedDataParallel）相比：

FSDP2采用基于DTensor的、沿第0维的参数级分片方式，相比FSDP1的扁平参数分片结构，其分片表示更为简洁，同时仍能保持相近的性能水平。具体而言，FSDP2会通过torch.chunk(dim=0)函数，将每个参数沿第0维分割到不同的数据并行工作节点上；而FSDP1则是先将多张张量展平、拼接，再整体分割，这使得理解各工作节点上存储的数据情况以及重新进行分片操作变得更为复杂。参数级分片能够为用户提供更直观的操作体验，放宽对冻结参数的限制，还能实现无需通信的分片状态字——而在FSDP1中这类状态字则必须通过全部收集操作来获取。

FSDP2采用了不同的内存管理方式来处理多流使用场景，无需使用torch.Tensor.record_stream功能。这种方式能够确保内存使用量具有确定性且符合预期，同时也不像FSDP1的limit_all_gathers=True设置那样会导致CPU阻塞。

FSDP2提供了用于手动控制预取操作和集群调度时间的API，便于高级用户进行自定义设置。具体详情请参阅下文中的FSDPModule相关方法。

FSDP2简化了部分API接口：例如，它不直接支持完整的状态字。相反，用户可以使用DTensor的API（如DTensor.full_tensor()），或PyTorch分布式检查点机制中的状态字相关API，将包含DTensor的分片状态字重新整合为完整状态字。此外，还有一些参数已被移除，具体详情请参阅相关说明。

其前端API为fully_shard，可直接在模块上调用：

该功能会将完全分片式数据并行（FSDP）应用于指定模块。FSDP会将模块的参数、梯度以及优化器状态分片到不同的数据并行工作节点上，从而在牺牲一定通信开销的前提下节省内存。

在初始化阶段，FSDP会根据指定的设备网格，将模块的参数分片到各个数据并行工作节点上。在前向传播之前，FSDP会从这些工作节点上收集所有分片的参数，得到未分片的参数以便进行前向计算。如果设置了reshard_after_forward为True，那么FSDP会在前向传播后释放这些未分片的参数，在反向传播之前再次将它们收集起来，以便进行梯度计算。在梯度计算完成后，FSDP会释放这些未分片的参数，并将未分片的梯度在各个数据并行工作节点之间进行归约与散布操作。

在这种实现方式中，分片后的参数会被表示为沿第0维分片的DTensor，而未分片的参数则保持与模块中原始参数相同的形式（例如，如果原始参数是torch.Tensor，那么未分片参数也是torch.Tensor）。模块的前向预钩子会负责收集参数，而后向钩子则会在需要时释放这些参数。类似地，后向钩子会先收集参数，随后释放参数，并对梯度进行归约与散布操作。

由于将多个张量组合在一起以便一次性进行通信操作对于提升通信效率至关重要，因此该实现将这种分组操作视为核心功能。在模块上调用fully_shard()时，会创建一个分组，其中包含module.parameters()中的所有参数，但不包括之前对子模块调用fully_shard()时已分配到其他分组的参数。这意味着应在模型的自底向上层次结构中依次调用fully_shard()。每个分组中的参数会在一次通信操作中全部收集起来，其梯度也将在另一次通信操作中完成归约与散布。将模型划分为多个分组（即“逐层划分”），可以实现最大的内存节省效果，并让通信操作与计算操作相互重叠。通常情况下，不应仅在最顶层的根模块上调用fully_shard()。

module (Union[nn.Module, List[nn.Module]]) – 需要使用FSDP进行分片处理，并将参数组合在一起以便通信的模块。

mesh (Optional[DeviceMesh]) – 该数据并行网格用于定义参数的分片方式及对应的设备。如果为1维结构，参数会在1维网格上被完全分片（即FSDP模式），参数的放置方式为(Shard(0),)。如果是2维结构，参数会先沿第一维进行分片，然后在第二维上复制（即HSDP模式），参数的放置方式为(Replicate(), Shard(0))。网格的设备类型决定了用于通信的设备类型；如果为CUDA或类似CUDA类型的设备，那么就会使用当前的设备。

reshard_after_forward (Optional[Union[bool, int]]) – 该参数用于控制前向传播后的参数处理方式，可在内存使用与通信开销之间进行权衡：如果设置为True，那么前向传播后会重新分片参数，然后在反向传播时再次将它们收集起来。如果设置为False，那么前向传播后参数会保留在内存中，反向传播时则无需进行全部收集操作。为获得最佳性能，通常建议对根模块将此参数设置为False，因为反向传播开始时通常需要立即使用根模块的参数。如果该参数为None，那么非根模块将默认设置为True，根模块则默认设置为False。如果其为整数，表示前向传播后参数应重新分片到的世界大小。该数值必须是网格分片维度大小的合法除数（即不能为1，也不能等于分片维度大小本身）。一个可行的选择是节点内部的大小（例如torch.cuda.device_count()）。这样虽然会导致反向传播时的全部收集操作在更小的世界范围内进行，从而带来更高的内存使用成本，但依然能够实现更好的性能。前向传播后，注册到模块上的参数类型取决于此参数的取值：如果设置为True，注册的参数为分片后的参数；如果设置为False，注册的参数为未分片的参数；否则，注册的参数为重新分片到较小网格后的参数。若要在前向和反向传播之间修改参数，注册的参数必须为分片后的参数。对于设置为False或整数的情况，可以通过手动调用reshard()函数来重新分片参数。

该参数用于控制前向传播后的参数处理方式，可在内存使用与通信开销之间进行权衡：

如果设置为True，那么前向传播后会重新分片参数，然后在反向传播时再次将它们收集起来。若该值为 False，则在前向传播后会将未分片参数保留在内存中，从而避免在反向传播时进行全收集操作。为获得最佳性能，通常会将根模块的此参数设置为 False，因为反向传播开始时往往需要立即使用根模块的参数。

若该值为 None，则非根模块的此参数默认为 True，而根模块的此参数默认为 False。

若该值为整数，则表示前向传播后需重新分片的参数所在的世界大小。该值应是网格分片维度大小的真因数（即不能为 1 或该维度大小本身）。可选择的一个数值是节点内部大小（例如 torch.cuda.device_count()）。这样虽会导致反向传播时的全收集操作在更小的世界范围内进行，从而增加内存占用，但能提升性能。

前向传播后，注册到该模块的参数取决于此参数的取值：若值为 True，则为分片参数；若为 False，则为未分片参数；否则为重新分片到较小网格结构中的参数。若要在前向与反向传播之间修改参数，注册的参数必须为分片参数。对于值为 False 或整数的情况，可通过手动调用 reshard() 函数来实现重新分片。

shard_placement_fn（可选的 Callable[[nn.Parameter], Optional[Shard]]）——该可调用对象可用于覆盖参数的分片策略，使参数在除 dim-0 之外的其他维度上分片。若该可调用对象返回一个 Shard placement 对象（非 None），则 FSDP 将按照该放置策略进行分片（例如 Shard(1)）。若在非零维度上进行分片，目前要求采用偶数分片，即该维度上的张量尺寸必须能被 FSDP 的分片网格大小整除。

mp_policy（MixedPrecisionPolicy）——用于控制混合精度策略，即为该模块提供参数/归约操作的混合精度处理。详情请参见 MixedPrecisionPolicy。

offload_policy（OffloadPolicy）——用于控制卸载策略，即为参数/梯度/优化器状态提供卸载功能。详情请参见 OffloadPolicy 及其子类。

ignored_params（可选的 set[nn.Parameter]）——可选的参数集合：表示 FSDP 应忽略的参数。这些参数既不会被分片，初始化时也不会被移动到指定设备，反向传播时其梯度也不会被归约。

对已应用 FSDP 的模块进行就地处理。

该方法会重新分片该模块的参数：若存在未分片参数则会释放它们，并将分片后的参数注册到该模块。此方法不是递归的。

hook（Callable[[torch.Tensor], None]）——用户自定义的全收集钩子函数，其预期签名应为 hook(reduce_output: torch.Tensor) -> None，其中 reduce_output 在仅使用 FSDP 时为归约-散布操作的输出，在使用原生 HSDP 时则为全收集操作的输出。

stream（可选的 torch.cuda.Stream）——用于运行全收集钩子函数的流。仅当不使用原生 HSDP 时才需设置此参数。若使用原生 HSDP，钩子函数将在原生 HSDP 全收集操作所使用的内部定义流中运行。

决定用于在集合通信中发送和接收数据的临时缓冲区是否应使用 ProcessGroup 自身提供的自定义优化分配器（如有）进行分配。这可能有助于提升 ProcessGroup 的效率。例如，在使用 NCCL 时，此设置可使其利用 SHARP 机制实现针对 NVLink 和/或 InfiniBand 的零拷贝传输。

此选项不能与 set_custom_all_gather() 或 set_custom_reduce_scatter() 同时使用，因为那些 API 能对每种通信操作进行更细粒度的控制，而此方法无法指定它们的缓冲区分配策略。

enable（bool）——是否启用 ProcessGroup 分配机制。

用于覆盖默认的全收集通信行为，从而更精细地控制通信过程及内存使用情况。详情请参见 Comm 和 ReduceScatter。

comm（AllGather）——自定义全收集通信操作。

用于覆盖默认的归约-散布通信行为，从而更精细地控制通信过程及内存使用情况。详情请参见 Comm 和 ReduceScatter。

comm（ReduceScatter）——自定义归约-散布通信操作。

决定是否要求低级集合通信原语仅使用“求和”类型的归约操作，即便这可能需要额外的预缩放或后缩放操作。例如，因为 NCCL 目前仅支持此类集合操作进行零拷贝传输，所以需要此设置。

注意：对于多线程 GPU 设备，此功能始终默认处于启用状态。

注意：如果在 FSDP 配置中使用 set_all_reduce_hook，调用者需确保跨 FSDP 单元的自定义全收集操作也遵循相同策略，因为 FSDP 无法再自动处理此类操作。

enable（bool）——是否始终仅使用 ReduceOp.SUM 进行通信操作。

为梯度归约设置自定义的除数。这可能涉及使用 NCCL 的 PreMulSum 自定义归约操作，即在归约之前先乘以该除数。

factor（float）——自定义除数。

决定下一次反向传播是否为最后一次反向传播。在最后一次反向传播时，FSDP 会等待待处理的梯度归约操作完成，并清空内部数据结构以便进行反向传播的预取操作。这对于微批次训练非常有用。

指定哪些 FSDP 模块需要该 FSDP 模块在反向传播时显式地预取全收集操作。这将覆盖默认的预取机制——后者会根据逆向前向顺序预取下一个 FSDP 模块的对应操作。传递包含上一个 FSDP 模块的单一列表可实现与默认重叠行为相同的全收集操作重叠效果；若需更强的重叠效果，则需传递长度至少为 2 的列表，但这会占用更多内存。

modules（List[FSDPModule]）——需要预取的 FSDP 模块列表。

指定哪些 FSDP 模块需要该 FSDP 模块在正向传播时显式地预取全收集操作。预取操作会在该模块完成全收集数据复制之后执行。传递包含下一个 FSDP 模块的单一列表可实现与默认重叠行为相同的重叠效果，只是预取的全收集操作会从 CPU 端更早发起。若需更强的重叠效果，则需传递长度至少为 2 的列表，但这会占用更多内存。

modules（List[FSDPModule]）——需要预取的 FSDP 模块列表。

为根级 FSDP 模块设置一个优化器步骤后的事件，以便该模块等待全收集操作完成。默认情况下，根级 FSDP 模块会在当前流上等待全收集操作完成，以确保优化器步骤先于全收集操作结束。但如果优化器步骤之后还有其他无关计算，这可能会引入虚假依赖关系。此 API 允许用户指定自己要等待的事件。根级模块等待该事件完成后，该事件即会被丢弃，因此每次迭代都应传入新的事件。

event（torch.Event）——在优化器步骤之后记录的事件，用于等待全收集操作完成。

建议改用 set_gradient_divide_factor()。

决定该模块是否需要进行梯度的全收集操作。这可用于在 HSDP 中仅通过归约-散布操作而非全收集操作来实现梯度累积。

决定该模块是否需要同步梯度。这可用于在不进行通信的情况下实现梯度累积。对于 HSDP，此参数同时控制归约-散布操作和全收集操作。其功能相当于 FSDP1 中的 no_sync 参数。

requires_gradient_sync（bool）——是否需要对该模块的参数进行梯度归约。

recurse（bool）——是仅为传入的模块设置该参数，还是为所有 FSDP 子模块都设置。

决定该模块是否需要在反向传播后重新分片参数。这可在梯度累积过程中使用，通过牺牲部分内存来减少通信量，因为无需在下次前向传播之前再次对未分片参数进行全收集操作。

reshard_after_backward（bool）——是否在反向传播后重新分片参数。

recurse（bool）——是仅为传入的模块设置该参数，还是为所有 FSDP 子模块都设置。

决定该模块是否需要在前向传播后重新分片参数。这可用于在运行时更改 reshard_after_forward 参数的值。例如，可将 FSDP 根模块的此参数设置为 True（因为它默认被特殊设置为 False），或为某个 FSDP 模块设置 False 以在评估模式下运行，训练时再改回 True。

reshard_after_forward（bool）——是否在前向传播后重新分片参数。

recurse（bool）——是仅为传入的模块设置该参数，还是为所有 FSDP 子模块都设置。

决定该 FSDP 模块的参数在反向传播时是否需要取消分片。这适用于某些特殊场景，即用户知道该 FSDP 模块参数组中的所有参数在反向传播时都不需要使用（例如嵌入层参数）。

通过分配内存并对参数进行全收集操作，来取消该模块参数的分片状态。此方法不是递归的。取消分片操作会遵循 MixedPrecisionPolicy 的规则，因此如果设置了 param_dtype，就会按照该数据类型进行全收集操作。

async_op（bool）——若为 True，则会返回一个 UnshardHandle 对象，该对象包含一个 wait() 方法，可用于等待取消分片操作完成。若为 False，则直接返回 None，且操作会在当前函数内部等待。

可选的 UnshardHandle 对象。

若 async_op 设置为 True，则 FSDP 会在该模块的前向传播准备阶段为用户等待待处理的取消分片操作。只有当需要在前向传播之前就进行等待时，用户才需显式调用 wait() 方法。

用于等待 FSDPModule.unshard() 操作的句柄。

用于等待取消分片操作完成。这可确保当前流能够使用已注册到模块中的取消分片参数。

在模块上注册一个方法，使其被视为 FSDP 的前向传播方法。

FSDP 会在前向传播之前对参数进行全收集操作，根据 reshard_after_forward 的设置，还可能在后向传播之后释放参数。默认情况下，FSDP 只知道对 nn.Module.forward() 方法执行此操作。此函数会替换用户指定的方法，在该方法执行前后分别运行预/后向钩子函数。如果该模块不是 FSDPModule 类型，则此操作无任何效果。

module（nn.Module）——要为其注册前向传播方法的模块。

method_name（str）——前向传播方法的名称。

用于配置 FSDP 的混合精度设置。与 autocast 不同，此功能是在模块级别而非操作级别应用混合精度，这意味着低精度激活值会被保留以供反向传播使用，而高精度到低精度的转换仅发生在模块边界处。

由于 FSDP 本身就会将高精度分片参数保留在内存中，因此它与模块级别的混合精度设置配合得很好。换句话说，FSDP 不需要额外的内存来为优化器步骤保存参数的高精度副本。

param_dtype（可选的 torch.dtype）——指定未分片参数的数据类型，进而决定前向/反向传播操作以及参数全收集操作所使用的数据类型。若该值为 None，则未分片参数将使用原有的数据类型。优化器步骤则使用分片参数的原始数据类型。（默认值：None）reduce_dtype（可选，类型为torch.dtype）——用于指定梯度归约（即reduce-scatter或all-reduce操作）所使用的数据类型。如果该参数为None而param_dtype不为None，则归约操作将使用compute dtype。这一功能可用于在计算时采用低精度，同时以全精度进行梯度归约。如果通过set_requires_gradient_sync()禁用了梯度归约，FSDP仍会使用reduce_dtype来累积梯度。（默认值：None）

output_dtype（可选，类型为torch.dtype）——用于指定将浮点型前向输出转换为特定数据类型时的目标类型。这一功能有助于实现不同模块采用不同混合精度策略的场景。（默认值：None）

cast_forward_inputs（布尔值）——用于指定FSDP是否应将前向传播中的浮点型输入张量转换为param_dtype类型。

该基类代表不进行参数卸载的策略，仅作为offload_policy参数的默认值使用。

此卸载策略会将参数、梯度以及优化器状态卸载到CPU上。在all-gather操作之前，分片后的参数会从主机复制到设备上；根据reshard_after_forward的设置，这些聚合后的参数会被释放。在反向传播过程中，分片后的梯度会从设备复制回主机，而优化器操作则会在CPU上使用对应的CPU优化器状态进行。

pin_memory（布尔值）——用于指定是否固定分片后参数和梯度所在内存的位置。固定内存位置可以提高H2D/D2H数据拷贝的效率，并使拷贝操作与计算操作并行执行。不过，被固定的内存无法被其他进程使用。如果CPU内存不足，请将此参数设置为False。（默认值：True）

---

## 分布式通信包 - torch.distributed#

**网址：** https://pytorch.org/docs/stable/distributed.html

**目录结构：**
- 分布式通信包 - torch.distributed#
- 后端支持#
  - PyTorch自带的后端#
  - 应该选择哪种后端？#
  - 常见环境变量#
    - 如何选择要使用的网络接口#
    - 其他NCCL相关环境变量#
- 基础知识#
- 初始化#
  - TCP初始化#

创建时间：2017年7月12日 | 最后更新时间：2025年9月4日

如需了解与分布式训练相关的所有功能概述，请参阅PyTorch分布式训练概览。

torch.distributed支持四种内置后端，每种后端具有不同的功能特性。下表列出了每种后端在CPU或GPU上可用的功能。对于NCCL而言，GPU指的是CUDA GPU；而对于XCCL而言，则指XPU GPU。

只有用于构建PyTorch的实现版本支持CUDA时，MPI才能在PyTorch中运行。

PyTorch分布式包目前支持Linux（稳定版）、MacOS（稳定版）以及Windows（原型版）。对于Linux系统，默认情况下已内置Gloo和NCCL后端（使用CUDA构建时才会包含NCCL）。MPI是一种可选的后端，只有通过源代码方式构建PyTorch时才能启用（例如在已安装MPI的主机上构建PyTorch）。

从PyTorch v1.8版本开始，Windows系统支持所有的集合通信后端，但NCCL除外。如果init_process_group()函数的init_method参数指向的是文件，那么该文件必须遵循以下格式：

本地文件系统：init_method="file:///d:/tmp/some_file"

共享文件系统：init_method="file://////{machine_name}/{share_folder_name}/some_file"

与Linux平台类似，也可以通过设置MASTER_ADDR和MASTER_PORT环境变量来启用TcpStore功能。

过去，人们经常询问：“我应该使用哪种后端？”

- 若使用CUDA GPU进行分布式训练，请选择NCCL后端。
- 若使用XPU GPU进行分布式训练，请选择XCCL后端。
- 若使用CPU进行分布式训练，请选择Gloo后端。

**配备InfiniBand互连的GPU主机：**
建议使用NCCL，因为它是目前唯一同时支持InfiniBand和GPUDirect技术的后端。

**配备以太网互连的GPU主机：**
建议使用NCCL，因为它目前能提供最佳的分布式GPU训练性能，尤其适用于单节点或多节点的多进程分布式训练。如果遇到NCCL相关问题，可考虑将Gloo作为备用选项。（需要注意的是，目前Gloo在GPU上的运行速度慢于NCCL。）

**配备InfiniBand互连的CPU主机：**
如果您的InfiniBand支持IP over IB功能，则使用Gloo；否则请使用MPI。我们计划在未来的版本中为Gloo添加对InfiniBand的支持。

**配备以太网互连的CPU主机：**
建议使用Gloo，除非有特殊原因需要使用MPI。

默认情况下，NCCL和Gloo两种后端都会尝试自动查找合适的网络接口。如果自动检测到的接口不正确，可以通过以下环境变量来手动指定（这些变量适用于对应的前端）：

- NCCL_SOCKET_IFNAME，例如：export NCCL_SOCKET_IFNAME=eth0
- GLOO_SOCKET_IFNAME，例如：export GLOO_SOCKET_IFNAME=eth0

如果使用Gloo后端，可以通过逗号分隔的方式指定多个接口，例如：export GLOO_SOCKET_IFNAME=eth0,eth1,eth2,eth3。后端会以轮询方式在这些接口之间分配任务。所有进程必须在此变量中指定相同数量的接口。

**调试：** 如果遇到NCCL相关故障，可以设置NCCL_DEBUG=INFO，以便输出明确的警告信息以及NCCL的初始化相关信息。

您还可以使用NCCL_DEBUG_SUBSYS来获取关于NCCL某一特定方面的更多详细信息。例如，设置NCCL_DEBUG_SUBSYS=COLL可以打印出集合通信操作的日志，这在调试程序卡死问题时非常有用，尤其是那些由集合通信类型或消息大小不匹配引起的卡死问题。如果遇到拓扑检测失败的情况，设置NCCL_DEBUG_SUBSYS=GRAPH可以查看详细的检测结果，以便在需要NCCL团队进一步协助时作为参考。

**性能调优：** NCCL会根据其拓扑检测结果自动进行调优，从而节省用户的调优工作量。在某些基于套接字的系统中，用户仍可以尝试调整NCCL_SOCKET_NTHREADS和NCCL_NSOCKS_PERTHREAD这两个环境变量，以提升套接字网络带宽。对于AWS或GCP等一些云服务提供商，NCCL已经预先针对这些环境变量进行了优化。

如需查看完整的NCCL环境变量列表，请参阅NVIDIA NCCL的官方文档。

您还可以通过torch.distributed.ProcessGroupNCCL.NCCLConfig和torch.distributed.ProcessGroupNCCL.Options进一步调整NCCL通信器的参数。可以在解释器中使用help命令（例如help(torch.distributed.ProcessGroupNCCL.NCCLConfig)）来了解相关用法。

torch.distributed包为运行在多台机器上的多个计算节点之间的多进程并行计算提供了PyTorch相关的支持与通信原语。torch.nn.parallel.DistributedDataParallel()类则基于这些功能，为任意PyTorch模型提供了一个同步分布式训练的封装接口。它与torch.multiprocessing包以及torch.nn.DataParallel()所提供的并行机制不同，因为它支持多个通过网络相连的机器，而且用户必须为每个进程单独启动一份主训练脚本。

在单机同步训练场景下，与torch.nn.DataParallel()等其他数据并行实现方式相比，torch.distributed或torch.nn.parallel.DistributedDataParallel()封装依然具有优势，具体体现在：

- 每个进程都拥有自己的优化器，并在每次迭代中执行完整的优化步骤。虽然这看似有些多余，因为梯度早已在所有进程之间被聚合并平均，因此每个进程获得的梯度都是相同的，但这种方式无需进行参数广播操作，从而减少了节点间张量传输所耗费的时间。
- 每个进程都拥有独立的Python解释器，避免了从单个Python进程驱动多个执行线程、模型副本或GPU时所产生的额外解释器开销以及“GIL锁竞争”问题。这对于那些大量依赖Python运行时的模型尤为重要，尤其是那些包含循环层或众多小型组件的模型。

在调用其他方法之前，必须先使用torch.distributed.init_process_group()或torch.distributed.device_mesh.init_device_mesh()函数对包进行初始化。这两个函数都会阻塞执行，直到所有进程都加入进程组为止。

初始化操作不是线程安全的。进程组的创建应在单个线程中完成，这样可以避免不同进程之间的“UUID”分配出现不一致，同时也能防止初始化过程中出现竞争条件从而导致程序卡死。

如果系统支持分布式训练功能，则返回True；否则，torch.distributed不会提供其他任何API接口。目前，torch.distributed在Linux、MacOS和Windows系统上均可用。如果在从源代码构建PyTorch时希望启用该功能，可将USE_DISTRIBUTED设置为1。当前，默认值为：Linux和Windows系统为USE_DISTRIBUTED=1，MacOS系统为USE_DISTRIBUTED=0。

用于初始化默认的分布式进程组。此操作同时也会启动torch.distributed包的功能。

用于明确指定存储位置、当前进程的排名以及整个进程组的总进程数。

用于指定init_method（一个URL字符串），该字符串指示了发现其他进程的位置及方式。也可以选择性地指定排名和总进程数，或者将所有必要参数都编码到URL中而省略这些显式参数。

如果未指定这两项内容，则默认认为init_method为“env://”。

backend（字符串或Backend类型，可选）——用于指定要使用的后端。根据构建时的配置不同，有效的值包括mpi、gloo、nccl、ucc、xccl，或是第三方插件注册的其他后端。从版本2.6开始，如果未指定backend参数，c10d会自动使用device_id参数（如果提供）所指定的设备类型对应的已注册后端。目前已知的默认映射关系为：cuda设备对应NCCL后端，CPU设备对应gloo后端，XPU设备对应xccl后端。如果既未指定backend也未指定device_id，c10d会在运行时自动检测主机上的加速器，并使用与该加速器（或CPU）对应的已注册后端。该参数也可以以小写字符串的形式给出（例如“gloo”），同时也可以通过Backend属性来访问（例如Backend.GLOO）。如果在使用NCCL后端且每台机器上运行多个进程时，每个进程必须对其使用的每块GPU拥有独占访问权，因为进程间共享GPU可能会导致死锁或NCCL使用错误。ucc后端目前仍处于实验阶段。可以通过get_default_backend_for_device()函数查询该设备的默认后端。

init_method（字符串，可选）——用于指定如何初始化进程组的URL地址。如果未指定init_method或store参数，则默认值为“env://”。该参数与store参数互斥。

world_size（整数，可选）——参与当前任务的进程总数。如果指定了store参数，则此参数为必填项。

rank（整数，可选）——当前进程的排名（其值应在0到world_size-1之间）。如果指定了store参数，则此参数为必填项。store（存储，可选）——所有工作进程均可访问的键值存储，用于交换连接/地址信息。该参数与init_method互斥。

timeout（超时时间，timedelta类型，可选）——针对进程组执行的操作设定的超时时间。NCCL后端的默认值为10分钟，其他后端为30分钟。超过此时间后，集合操作将异步终止，进程也会崩溃。这是因为CUDA执行是异步的，一旦出现失败的异步NCCL操作，后续的CUDA操作可能会在损坏的数据上运行，继续执行用户代码已不再安全。当设置了TORCH_NCCL_BLOCKING_WAIT时，进程将会阻塞并等待超时发生。

group_name（组名，str类型，已弃用）——用于指定组名称。此参数当前会被忽略。

pg_options（进程组选项，ProcessGroupOptions类型，可选）——用于指定在构建特定进程组时需要传递的额外选项。目前仅支持NCCL后端的ProcessGroupNCCL.Options选项；还可以指定is_high_priority_stream，以便在有计算内核等待时让NCCL后端优先处理高优先级的CUDA流。如需了解NCCL的其他可用配置选项，请参阅https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-t。

device_id（设备ID，torch.device或int类型，可选）——指定该进程将要使用的特定设备，从而实现针对不同后端的优化。目前此功能仅在NCCL环境下有效：它会立即创建通信器（直接调用ncclCommInit*而非常规的延迟调用），并且子组会在可能的情况下使用ncclCommSplit来避免创建组所带来的不必要的开销。如果您希望尽早得知NCCL初始化错误，也可以使用该字段。如果传入的是整数，API会假设在编译时指定的加速器类型即为目标设备。

若要启用Backend.MPI后端，需在支持MPI的系统中从源代码构建PyTorch。

对多个后端的支持仍处于实验阶段。目前如果没有指定后端，系统会同时创建gloo和NCCL两种后端：包含CPU张量的集合操作将使用gloo后端，而包含CUDA张量的集合操作则使用NCCL后端。也可以通过传入格式为“<设备类型>:<后端名称>,<设备类型>:<后端名称>”的字符串来指定自定义后端，例如“cpu:gloo,cuda:custom_backend”。

根据device_type、mesh_shape和mesh_dim_names参数初始化DeviceMesh结构。

该方法会创建一个具有n维数组布局的DeviceMesh，其中n为mesh_shape的长度。如果提供了mesh_dim_names，则每个维度都会被标记为mesh_dim_names[i]。

init_device_mesh遵循SPMD编程模型，即同一个PyTorch Python程序会在集群中的所有进程/节点上运行。请确保所有节点上的mesh_shape（描述设备布局的n维数组的维度）完全一致，否则可能会导致程序挂起。

如果未找到进程组，init_device_mesh会后台自动初始化分布式通信所需的分布式进程组。

device_type（str类型）——网格的设备类型。目前支持“cpu”、“cuda/cuda-like”和“xpu”。不允许传入包含GPU索引的设备类型，例如“cuda:0”。

mesh_shape（Tuple[int]类型）——用于定义描述设备布局的多维数组各维度的元组。

mesh_dim_names（Tuple[str]类型，可选）——用于为描述设备布局的多维数组的每个维度指定名称的元组。其长度必须与mesh_shape的长度一致，且mesh_dim_names中的每个字符串都必须唯一。

backend_override（Dict[int | str, tuple[str, Options] | str | Options]类型，可选）——用于覆盖为每个网格维度将要创建的某些或所有进程组的配置。每个键可以是维度的索引，也可以是其名称（前提是已提供mesh_dim_names）。每个值可以是一个包含后端名称及其选项的元组，或者仅包含这两个组成部分中的一个（此时另一个部分将自动设置为默认值）。

表示设备布局的DeviceMesh对象。

检查默认进程组是否已被初始化。

检查MPI后端是否可用。

检查NCCL后端是否可用。

检查Gloo后端是否可用。

检查XCCL后端是否可用。

检查当前进程是否是通过torch.distributed.elastic（即torchelastic）启动的。系统会通过TORCHELASTIC_RUN_ID环境变量的存在与否来判断当前进程是否由torchelastic启动。这是一个合理的判断依据，因为TORCHELASTIC_RUN_ID对应于会面ID，该值始终非空，可用于节点发现。

返回指定设备的默认后端。

device（Union[str, torch.device]类型）——用于获取默认后端的设备。

以小写字符串形式返回指定设备的默认后端。

目前支持三种初始化方法：

通过TCP进行初始化有两种方式，这两种方式都需要一个所有进程都能访问的网络地址以及指定的world_size值。第一种方式需要指定属于rank 0进程的地址。这种初始化方法要求所有进程都需手动指定自己的排名。

请注意，在最新的分布式包中已不再支持多播地址，group_name参数也已弃用。

另一种初始化方式是利用一组所有节点都能访问的共享文件系统，同时还需指定world_size值。URL应以file://开头，并指向共享文件系统中某个现有目录下并不存在的文件路径。文件系统初始化会在文件不存在时自动创建它，但不会删除该文件。因此，您有责任在下次使用相同路径/名称调用init_process_group()之前将文件清理干净。

请注意，在最新的分布式包中已不再支持自动分配排名，group_name参数也已弃用。

此方法假设文件系统支持使用fcntl进行锁定——大多数本地系统及NFS都支持该功能。

此方法会始终创建该文件，并会在程序结束时尽力清理并删除它。换句话说，每次使用文件初始化方式时，都需要一个全新的空文件才能确保初始化成功。如果再次使用上一次初始化所使用的文件（而该文件未被清理），就会出现异常行为，往往会导致死锁和故障。因此，尽管此方法会尽力清理文件，但如果自动删除失败，您仍有责任在训练结束时确保将该文件移除，以避免下次再次使用同一个文件。如果您计划多次使用相同的文件名调用init_process_group()，这一点尤为重要。换言之，如果文件未被删除/清理，而您又对该文件再次调用init_process_group()，则很可能会出现故障。这里的经验法则是：每次调用init_process_group()时，都必须确保该文件不存在或为空。

此方法会从环境变量中读取配置，从而允许用户完全自定义信息的获取方式。需要设置的变量包括：

MASTER_PORT——必填项；必须是rank 0所在机器上的空闲端口。

MASTER_ADDR——除rank 0外均为必填项；表示rank 0节点的地址。

WORLD_SIZE——必填项；可以在此处设置，也可以在调用init函数时设置。

RANK——必填项；可以在此处设置，也可以在调用init函数时设置。

rank 0所在的机器将用于建立所有连接。

这是默认的初始化方法，意味着无需指定init_method（或者可以设置为env://）。

TORCH_GLOO_LAZY_INIT——采用按需建立连接的方式，而非构建完整的网格结构，这能显著缩短非all2all操作的初始化时间。

一旦调用了torch.distributed.init_process_group()，就可以使用以下函数。要检查进程组是否已初始化，可使用torch.distributed.is_initialized()函数。

表示后端的枚举类。

支持的后端包括：GLOO、NCCL、UCC、MPI、XCCL以及其他已注册的后端。

该类的值均为小写字符串，例如“gloo”。这些值可以作为属性访问，例如Backend.NCCL。

可以直接调用该类来解析字符串，例如Backend(backend_str)会检查backend_str是否有效，如果有效则返回解析后的小写字符串。该类也支持大写字符串，例如Backend("GLOO")会返回“gloo”。

虽然存在Backend.UNDEFINED这个枚举值，但它仅用作某些字段的初始值。用户既不应直接使用它，也不应假设其存在。

使用给定的名称和实例化函数注册新的后端。

此类方法被第三方ProcessGroup扩展用于注册新的后端。

name（str类型）——ProcessGroup扩展的后端名称，必须与init_process_group()中指定的名称一致。

func（function类型）——用于实例化后端的函数处理程序。该函数需在后台扩展中实现，且需接受四个参数，包括store、rank、world_size和timeout。

extended_api（bool类型，可选）——表示该后端是否支持扩展的参数结构。默认值为False。如果设置为True，该后端将获得一个c10d::DistributedBackendOptions实例，以及一个由该后端实现定义的进程组选项对象。

device（str或list of str类型，可选）——该后端支持的设备类型，例如“cpu”、“cuda”等。如果为None，则默认同时支持“cpu”和“cuda”两种设备。

对第三方后端的支持仍处于实验阶段，可能会发生变化。

返回指定进程组的后端。

group（ProcessGroup类型，可选）——要操作的进程组。默认为通用的主进程组。如果指定了其他特定组，调用进程必须属于该组。

以小写字符串形式返回指定进程组的后端。

默认情况下返回当前进程在所屬进程组中的排名。排名是分配给分布式进程组中每个进程的唯一标识符，其值始终是从0到world_size的连续整数。

group（ProcessGroup类型，可选）——要操作的进程组。如果为None，则使用默认的进程组。

如果当前进程不属于该进程组，则返回-1作为其排名。

返回当前进程组中的进程数量。

group（ProcessGroup类型，可选）——要操作的进程组。如果为None，则使用默认的进程组。若进程不属于某个进程组，则该进程所在的世界大小为 -1。

在程序退出时，务必通过调用 destroy_process_group() 来释放资源。

最简单的处理方式是在训练脚本中不再需要进程间通信时——通常是在 main() 函数接近结尾处——使用 group 参数设置为默认值 None，进而调用 destroy_process_group() 来销毁所有的进程组及后端。该操作应在每个训练进程上执行一次，而非在最外层的进程启动层执行。

如果在超时时间内，并非进程组中的所有节点都调用了 destroy_process_group()，尤其是在应用程序中存在多个进程组（例如用于 N 维并行计算）的情况下，程序退出时可能会出现挂起现象。这是因为 ProcessGroupNCCL 的销毁函数会调用 ncclCommAbort，而该调用必须由所有节点共同执行；但由于 Python 的垃圾回收机制决定了 ProcessGroupNCCL 销毁函数的调用顺序并不确定，因此就有可能出现问题。调用 destroy_process_group() 可以确保所有节点以一致的顺序调用 ncclCommAbort，同时避免在 ProcessGroupNCCL 的销毁函数执行期间调用该函数，从而解决这一问题。

destroy_process_group() 也可用于销毁单个进程组。一个应用场景是容错训练，即在运行过程中某个进程组可能被销毁并重新创建新的进程组。在这种情况下，在调用 destroy() 之后、随后初始化新进程组之前，必须通过其他方式（而非 torch.distributed 的原生接口）对所有训练进程进行同步。由于实现此类同步存在难度，目前该功能尚不支持且未经测试，已被视为一个已知问题。如果此需求正在阻碍您的开发工作，请在 GitHub 上提交问题或提案。

默认情况下，集合操作是在默认进程组（也称为世界进程组）上进行的，要求所有进程都进入分布式函数调用状态。不过，某些工作负载可能需要更细粒度的通信机制，这时分布式进程组便派上了用场。可以使用 new_group() 函数来创建新的进程组，这些新组可以包含所有进程中的任意子集。该函数会返回一个不可见的进程组句柄，可将其作为参数传递给所有的集合操作函数（集合操作函数是一类用于在特定编程模式中交换信息的分布式函数）。

创建一个新的分布式进程组。

该函数要求主进程组中的所有进程——即所有参与分布式任务的进程——都必须进入此函数，即便它们日后不会成为该组的成员。此外，所有进程创建进程组的顺序也必须保持一致。

安全并发使用：当使用 NCCL 后端并启用多个进程组时，用户必须确保所有节点上的集合操作能够按照全局一致的顺序执行。

如果一个进程内的多个线程同时发起集合操作，则必须进行显式同步，以确保操作顺序的一致性。

在使用 torch.distributed 通信 API 的异步版本时，函数会返回一个工作对象，通信内核会被放入独立的 CUDA 流中处理，从而实现通信与计算的并行执行。一旦在一个进程组上启动了一个或多个异步操作，就必须通过调用 work.wait() 来与其他 CUDA 流进行同步，之后才能使用另一个进程组。

更多详细信息请参阅《同时使用多个 NCCL 通信器》<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html#using-multiple-nccl-communicators-concurrently>。

ranks (list[int]) – 进程组成员的排名列表。如果为 None，则表示包含所有排名。默认值为 None。

timeout (timedelta, optional) – 详细信息及默认值请参见 init_process_group 函数。

backend (str or Backend, optional) – 要使用的后端类型。根据构建时的配置，有效值包括 gloo 和 nccl。默认情况下会使用与全局进程组相同的后端。该参数应作为小写字符串输入（例如 “gloo”），也可通过 Backend 属性访问（例如 Backend.GLOO）。如果未指定该参数，则会使用默认进程组对应的后端。默认值为 None。

pg_options (ProcessGroupOptions, optional) – 进程组选项，用于指定在构建特定进程组时需要传递的额外参数。例如，对于 NCCL 后端，可以指定 is_high_priority_stream，以便进程组能够使用优先级更高的 CUDA 流。关于可用于配置 NCCL 的其他选项，请参阅 https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-tuse_local_synchronization。

(tuse_local_synchronization, bool, optional)：在进程组创建完成后执行组内屏障操作。需要注意的是，非成员节点无需调用该 API，也不会参与该屏障操作。

group_desc (str, optional) – 用于描述进程组的字符串。

device_id (torch.device, optional) – 用于将当前进程“绑定”到的特定设备。如果指定了该参数，new_group 函数会立即尝试为该设备初始化通信后端。

一个分布式进程组句柄，可将其传递给集合操作函数；如果当前节点不属于进程组成员，则该参数值为 GroupMember.NON_GROUP_MEMBER。

注意：use_local_synchronization 与 MPI 不兼容。

注意：虽然当集群规模较大且进程组规模较小时，设置 use_local_synchronization=True 可显著提升性能，但需谨慎使用，因为它会改变集群的行为——非成员节点不会参与 group barrier() 操作。

注意：如果每个节点都创建多个重叠的进程组，设置 use_local_synchronization=True 可能会导致死锁。为避免这种情况，请确保所有节点遵循相同的全局创建顺序。

将全局排名转换为进程组排名。

global_rank 必须属于该进程组，否则会引发 RuntimeError 异常。

group (ProcessGroup) – 用于确定相对排名的进程组对象。

global_rank (int) – 需要查询的全局排名。

global_rank 在该进程组中的排名。

注意：在默认进程组上调用此函数时，返回值为自身。

将进程组排名转换为全局排名。

group_rank 必须属于该进程组，否则会引发 RuntimeError 异常。

group (ProcessGroup) – 用于确定对应全局排名的进程组对象。

group_rank (int) – 需要查询的进程组排名。

group_rank 在该进程组中的全局排名。

注意：在默认进程组上调用此函数时，返回值为自身。

获取与指定进程组相关的所有节点排名。

group (Optional[ProcessGroup]) – 用于获取所有节点排名的进程组对象。如果为 None，则使用默认进程组。

按进程组排名排序后的全局排名列表。

DeviceMesh 是一种更高级的抽象层，用于管理进程组（或 NCCL 通信器）。它让用户能够轻松创建节点间及节点内的进程组，而无需担心如何为不同的子进程组正确设置节点排名，同时也有助于更好地管理这些分布式进程组。可以使用 init_device_mesh() 函数来创建新的 DeviceMesh，该函数需要一个描述设备拓扑结构的网格形状参数。

DeviceMesh 表示一种设备网格结构，设备的布局可以用 n 维数组表示，该数组中的每个值对应默认进程组节点的全局编号。

DeviceMesh 可用于在集群中建立 N 维设备连接，并管理用于 N 维并行计算的进程组。通信可以在 DeviceMesh 的每个维度上独立进行。DeviceMesh 会尊重用户预先选择的设备——即如果用户在初始化 DeviceMesh 之前已经调用了 torch.cuda.set_device，则会使用该设备；如果用户未预先指定设备，它也会为当前进程选择/设置设备。请注意，手动选择设备必须在初始化 DeviceMesh 之前完成。

当与 DTensor API 一起使用时，DeviceMesh 还可以用作上下文管理器。

DeviceMesh 遵循 SPMD 编程模型，这意味着集群中的所有进程/节点都在运行相同的 PyTorch Python 程序。因此，用户必须确保描述设备布局的网格数组在所有节点上保持一致。如果网格结构不一致，程序可能会无声挂起。

device_type (str) – 网格的设备类型。目前支持 “cpu” 和 “cuda/cuda-like” 两种类型。不允许传入包含 GPU 索引的设备类型，例如 “cuda:0”。

mesh (ndarray) – 用于描述设备布局的多维数组或整数张量，其中的数值为默认进程组节点的全局编号。

一个表示设备布局的 DeviceMesh 对象。

以下程序以 SPMD 方式在每个进程/节点上运行。在这个示例中，共有 2 台主机，每台主机配备 4 架 GPU。对网格第一维的聚合操作会在列方向（0, 4），...，(3, 7) 上进行；而对网格第二维的聚合操作则会在行方向（0, 1, 2, 3）和（4, 5, 6, 7）上执行。

根据现有的 ProcessGroup 或 ProcessGroup 列表，使用 device_type 参数构建一个 DeviceMesh。

所构建的 DeviceMesh 的维度数量与传入的进程组数量相同。例如，如果只传入一个进程组，则生成的 DeviceMesh 为 1 维网格；如果传入 2 个进程组，则生成 2 维网格。

如果传入多个进程组，则必须同时提供 mesh 和 mesh_dim_names 参数。传入的进程组顺序决定了网格的拓扑结构。例如，第一个传入的进程组将成为 DeviceMesh 的第 0 维。传入的网格张量必须具有与进程组数量相同的维度数，且各维的顺序也必须与进程组的顺序一致。

group (ProcessGroup or list[ProcessGroup]) – 现有的 ProcessGroup 对象或 ProcessGroup 列表。

device_type (str) – 网格的设备类型。目前支持 “cpu” 和 “cuda/cuda-like” 两种类型。不允许传入包含 GPU 索引的设备类型，例如 “cuda:0”。

mesh (torch.Tensor or ArrayLike, optional) – 用于描述设备布局的多维数组或整数张量，其中的数值为默认进程组节点的全局编号。默认值为 None。

mesh_dim_names (tuple[str], optional) – 一个元组，包含用于为描述设备布局的多维数组的各维度命名的字符串。该元组的长度必须与 mesh_shape 的长度相同，且每个字符串都必须唯一。默认值为 None。

一个表示设备布局的 DeviceMesh 对象。

返回一个列表，其中包含所有网格维度的 ProcessGroup 对象。

一个 ProcessGroup 对象列表。

list[torch.distributed.distributed_c10d.ProcessGroup]

返回当前节点在网格各维度上的相对索引。如果当前节点不属于该网格，则返回 None。

根据 mesh_dim 参数返回对应的单个 ProcessGroup 对象；如果未指定 mesh_dim 且 DeviceMesh 为 1 维，则返回网格中唯一的 ProcessGroup 对象。mesh_dim（str/python:int，可选）——可以是网格维度的名称或索引。

该参数的默认值为None，表示使用ProcessGroup对象。

返回DeviceMesh中指定mesh_dim的本地秩值。

mesh_dim（str/python:int，可选）——可以是网格维度的名称或索引。

该参数的默认值为None，此时整数表示对应的本地秩值。

以下程序以SPMD方式在每个进程/秩上运行。在此示例中，共有2台主机，每台主机配备4张GPU。在秩为0、1、2、3的进程中调用mesh_2d.get_local_rank(mesh_dim=0)会返回0；在秩为4、5、6、7的进程中调用该函数则返回1。在秩为0、4的进程中调用mesh_2d.get_local_rank(mesh_dim=1)会返回0；在秩为1、5的进程中调用该函数返回1；在秩为2、6的进程中调用返回2；在秩为3、7的进程中调用返回3。

返回当前的全局秩值。

同步发送张量。

NCCL后端不支持tag参数。

tensor（Tensor）——要发送的张量。

dst（int）——全局进程组中的目标秩值（与group参数无关）。目标秩值不能与当前进程的秩值相同。

group（ProcessGroup，可选）——要操作的进程组。若为None，则使用默认进程组。

tag（int，可选）——用于将发送操作与远程接收操作匹配的标签。

group_dst（int，可选）——进程组内的目标秩值。不能同时指定dst和group_dst。

同步接收张量。

NCCL后端不支持tag参数。

tensor（Tensor）——用于存储接收到的数据的张量。

src（int，可选）——全局进程组中的源秩值（与group参数无关）。若未指定，则会从任意进程接收数据。

group（ProcessGroup，可选）——要操作的进程组。若为None，则使用默认进程组。

tag（int，可选）——用于将接收操作与远程发送操作匹配的标签。

group_src（int，可选）——进程组内的目标秩值。不能同时指定src和group_src。

若当前进程不属于该进程组，则发送方秩值为-1。

isend()和irecv()在调用时会返回分布式请求对象。通常这类对象的类型并未明确规定，因为用户不应手动创建它们，但可以确定的是它们都支持两种方法：

is_completed()——如果操作已完成则返回True。

wait()——会阻塞当前进程，直到操作完成。一旦is_completed()返回True，wait()也会立即返回True。

异步发送张量。

在请求完成之前修改张量会导致行为不可预测。

NCCL后端不支持tag参数。

与同步发送不同，异步发送允许src等于dst，即向自身发送数据。

tensor（Tensor）——要发送的张量。

dst（int）——全局进程组中的目标秩值（与group参数无关）。

group（ProcessGroup，可选）——要操作的进程组。若为None，则使用默认进程组。

tag（int，可选）——用于将发送操作与远程接收操作匹配的标签。

group_dst（int，可选）——进程组内的目标秩值。不能同时指定dst和group_dst。

返回一个分布式请求对象。若当前进程不属于该进程组，则返回None。

异步接收张量。

与同步接收不同，异步接收允许src等于dst，即从自身接收数据。

tensor（Tensor）——用于存储接收到的数据的张量。

src（int，可选）——全局进程组中的源秩值（与group参数无关）。若未指定，则会从任意进程接收数据。

group（ProcessGroup，可选）——要操作的进程组。若为None，则使用默认进程组。

tag（int，可选）——用于将接收操作与远程发送操作匹配的标签。

group_src（int，可选）——进程组内的目标秩值。不能同时指定src和group_src。

返回一个分布式请求对象。若当前进程不属于该进程组，则返回None。

同步发送object_list中的可序列化对象。

该功能与send()类似，但可以传递Python对象。需要注意的是，object_list中的所有对象都必须是可序列化的才能被发送。接收方也需要提供大小相同的对象列表。

object_list（List[Any]）——要发送的输入对象列表。每个对象都必须是可序列化的。

dst（int）——目标秩值，即要将object_list发送到的进程的秩值。该秩值基于全局进程组（与group参数无关）。

group（Optional[ProcessGroup]）——（ProcessGroup，可选）：要操作的进程组。若为None，则使用默认进程组。默认值为None。

device（torch.device，可选）——如果该参数不为None，那么对象会被序列化并转换为张量，然后再被移动到指定设备上之后发送。默认值为None。

group_dst（int，可选）——进程组内的目标秩值。必须只指定dst或group_dst其中之一，不能同时指定。

use_batch（bool，可选）——如果设置为True，则使用批量点对点操作而非常规的发送操作。这样无需初始化仅包含2个节点的通信器，而是直接使用整个进程组的通信器。具体用法和前提条件请参见batch_isend_irecv。默认值为False。

对于基于NCCL的进程组，对象的内部张量表示形式必须在通信开始之前被移动到GPU设备上。此时使用的设备由torch.cuda.current_device()指定，用户有责任通过torch.cuda.set_device()确保每个秩值都能使用独立的GPU。

对象集合操作存在诸多严重的性能和可扩展性限制。详情请参见“对象集合操作”相关章节。

send_object_list()会隐式使用pickle模块，而该模块存在安全风险。因为有可能构造出恶意的pickle数据，在反序列化时执行任意代码。因此仅建议使用可信的数据调用此函数。

使用GPU张量调用send_object_list()功能支持不佳且效率低下，因为需要先将张量序列化为字节流，从而导致GPU与CPU之间的数据传输。建议优先使用send()函数。

同步接收object_list中的可序列化对象。

该功能与recv()类似，但可以接收Python对象。

object_list（List[Any]）——用于接收数据的对象列表。接收方需要提供与发送方列表大小相同的对象列表。

src（int，可选）——接收object_list的源秩值。该秩值基于全局进程组（与group参数无关）。若设置为None，则会从任意秩值接收数据。默认值为None。

group（Optional[ProcessGroup]）——（ProcessGroup，可选）：要操作的进程组。若为None，则使用默认进程组。默认值为None。

device（torch.device，可选）——如果该参数不为None，那么将在指定设备上接收数据。默认值为None。

group_src（int，可选）——进程组内的目标秩值。不能同时指定src和group_src。

use_batch（bool，可选）——如果设置为True，则使用批量点对点操作而非常规的发送操作。这样无需初始化仅包含2个节点的通信器，而是直接使用整个进程组的通信器。具体用法和前提条件请参见batch_isend_irecv。默认值为False。

发送方秩值：如果当前进程不属于该进程组，则为-1。如果属于该进程组，object_list中则包含来自源秩值的对象。

对于基于NCCL的进程组，对象的内部张量表示形式必须在通信开始之前被移动到GPU设备上。此时使用的设备由torch.cuda.current_device()指定，用户有责任通过torch.cuda.set_device()确保每个秩值都能使用独立的GPU。

对象集合操作存在诸多严重的性能和可扩展性限制。详情请参见“对象集合操作”相关章节。

recv_object_list()会隐式使用pickle模块，而该模块存在安全风险。因为有可能构造出恶意的pickle数据，在反序列化时执行任意代码。因此仅建议使用可信的数据调用此函数。

使用GPU张量调用recv_object_list()功能支持不佳且效率低下，因为需要先将张量序列化为字节流，从而导致GPU与CPU之间的数据传输。建议优先使用recv()函数。

异步发送或接收一批张量，并返回对应的请求列表。

依次处理p2p_op_list中的每个操作，然后返回相应的请求。目前支持NCCL、Gloo和UCC后端。

p2p_op_list（list[torch.distributed.distributed_c10d.P2POp]）——一个点对点操作列表，其中每个操作的类型均为torch.distributed.P2POp。列表中isend/irecv的顺序很重要，必须与远程端的对应操作顺序一致。

返回一个列表，其中包含调用op_list中相应操作后得到的分布式请求对象。

list[torch.distributed.distributed_c10d.Work]

需要注意的是，当此API与NCCL进程组后端一起使用时，用户必须通过torch.cuda.set_device设置当前的GPU设备，否则可能会导致程序意外挂起。

此外，如果这是传递给dist.P2POp的组中的第一个集合操作，那么该组的所有秩值都必须参与此次调用；否则其行为是未定义的。如果这不是组中的第一个集合操作，那么允许仅让组中的一部分秩值参与批量点对点操作。

用于为batch_isend_irecv构建点对点操作的类。

该类用于构建点对点操作的类型、通信缓冲区、对端秩值、进程组以及标签。此类实例会被传递给batch_isend_irecv，用于实现点对点通信。

op（Callable）——一个用于向对端进程发送数据或从对端进程接收数据的函数。该函数的类型只能是torch.distributed.isend或torch.distributed.irecv。

tensor（Tensor）——要发送或接收的张量。

peer（int，可选）——目标秩值或源秩值。

group（ProcessGroup，可选）——要操作的进程组。若为None，则使用默认进程组。

tag（int，可选）——用于将发送操作与接收操作匹配的标签。

group_peer（int，可选）——目标秩值或源秩值。

根据传递给集合操作的async_op参数的设置，所有的集合操作函数都支持以下两种操作类型：

同步操作——默认模式，即当async_op设置为False时的模式。一旦函数返回，就可以确定集合操作已经完成。对于CUDA操作而言，虽然无法保证CUDA操作本身已经完成，因为CUDA操作是异步的。但对于CPU集合操作，后续使用该集合操作结果的函数调用将会按预期工作。对于CUDA集合操作，只要在同一个CUDA流上使用该操作结果，函数调用也会按预期工作。如果在不同的CUDA流下运行，用户需要自行处理同步问题。关于CUDA语义（如流同步）的详细信息，请参见“CUDA语义”相关章节。下面的脚本展示了CPU操作与CUDA操作在这些语义方面的差异示例。异步操作——当 async_op 设为 True 时启用。此类集合操作函数会返回一个分布式请求对象。通常无需手动创建该对象，且它必定支持以下两种方法：

is_completed()——对于 CPU 集合操作，若操作已完成则返回 True；对于 CUDA 操作，则在操作已成功提交到 CUDA 流且其输出可在默认流上直接使用而无需进一步同步时返回 True。

wait()——对于 CPU 集合操作，会阻塞进程直至操作完成；对于 CUDA 集合操作，则会阻塞当前正在运行的 CUDA 流直至操作完成（但不会阻塞 CPU）。

get_future()——返回 torch._C.Future 对象。该功能支持 NCCL，同时也支持 GLOO 和 MPI 上的大多数操作，但对点对点操作不支持。注意：随着我们不断采用 Future 并整合 API，get_future() 函数可能会逐渐被废弃。

以下代码可作为使用分布式集合操作时处理 CUDA 操作语义的参考。它展示了在不同 CUDA 流上使用集合操作输出时进行同步的必要性：

将张量广播到整个进程组。

参与集合操作的所有进程中，该张量的元素数量必须相同。

tensor（Tensor）——若 src 参数为当前进程的排名，则为此要发送的数据；否则则为用于存储接收到的数据。

src（int）——全局进程组中的源进程排名（与 group 参数无关）。

group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认进程组。

async_op（bool，可选）——该操作是否应为异步操作。

group_src（int）——进程组内的源进程排名。必须指定 group_src 或 src 中的一个，不可同时指定。

若 async_op 设为 True，则为异步工作句柄；否则或当前进程不属于该进程组时，此值为 None。

将 object_list 中的可序列化对象广播到整个进程组。

与 broadcast() 类似，但可传入 Python 对象。注意，object_list 中的所有对象都必须是可序列化的才能被广播。

object_list（List[Any]）——要广播的输入对象列表。每个对象都必须是可序列化的。只有源进程排名对应的对象会被广播，但每个进程都需要提供大小相同的对象列表。

src（int）——用于广播 object_list 的源进程排名。源进程排名基于全局进程组（与 group 参数无关）。

group（Optional[ProcessGroup]）——（ProcessGroup，可选）：要操作的进程组。若未指定，则使用默认进程组。默认值为 None。

device（torch.device，可选）——若非 None，则会先将对象序列化并转换为张量，然后再将这些张量移动到指定设备上再进行广播。默认值为 None。

group_src（int）——进程组内的源进程排名。必须指定 group_src 或 src 中的一个，不可同时指定。

若当前进程属于该进程组，则此值为 None。此时 object_list 将包含来自源进程排名的广播对象。

对于基于 NCCL 的进程组，必须在通信开始之前将对象的内部张量表示形式移动到 GPU 设备上。此时所使用的设备由 torch.cuda.current_device() 指定，用户有责任通过 torch.cuda.set_device() 确保每个进程都有独立的 GPU。

需要注意的是，此 API 与 broadcast() 集合操作略有不同，因为它不提供 async_op 句柄，因此属于阻塞式调用。

对象集合操作存在诸多严重的性能和可扩展性限制。详情请参阅“对象集合操作”相关章节。

broadcast_object_list() 函数会隐式使用 pickle 模块，而该模块存在安全风险。有人可能构造出恶意的 pickle 数据，在反序列化时执行任意代码。因此，请仅使用您信任的数据调用此函数。

使用 GPU 张量调用 broadcast_object_list() 的功能支持不佳且效率低下，因为需要先将张量序列化，从而导致 GPU 与 CPU 之间的数据传输。建议改用 broadcast() 函数。

该操作会将所有机器上的张量数据进行归约，从而使所有机器都获得最终结果。

调用此函数后，所有进程中的张量在位上将完全一致。

支持复杂张量。

tensor（Tensor）——集合操作的输入和输出。该函数为就地操作。

op（可选）——torch.distributed.ReduceOp 枚举中的某个值，用于指定用于逐元素归约的操作。

group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认进程组。

async_op（bool，可选）——该操作是否应为异步操作。

若 async_op 设为 True，则为异步工作句柄；否则或当前进程不属于该进程组时，此值为 None。

该操作会在所有机器上对张量数据进行归约。

只有 dst 排名的进程会收到最终结果。

tensor（Tensor）——集合操作的输入和输出。该函数为就地操作。

dst（int）——全局进程组中的目标进程排名（与 group 参数无关）。

op（可选）——torch.distributed.ReduceOp 枚举中的某个值，用于指定用于逐元素归约的操作。

group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认进程组。

async_op（bool，可选）——该操作是否应为异步操作。

group_dst（int）——进程组内的目标进程排名。必须指定 group_dst 或 dst 中的一个，不可同时指定。

若 async_op 设为 True，则为异步工作句柄；否则或当前进程不属于该进程组时，此值为 None。

该操作会将整个进程组中的张量收集到一个列表中。

支持复杂且大小不规则的张量。

tensor_list（list[Tensor]）——输出列表。其中应包含大小合适的张量，以便作为集合操作的输出。允许存在大小不规则的张量。

tensor（Tensor）——当前进程要广播的张量。

group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认进程组。

async_op（bool，可选）——该操作是否应为异步操作。

若 async_op 设为 True，则为异步工作句柄；否则或当前进程不属于该进程组时，此值为 None。

该操作会从所有进程收集张量，并将它们放入一个输出张量中。

此函数要求每个进程上的所有张量大小必须相同。

output_tensor（Tensor）——用于存储来自所有进程张量元素的输出张量。其大小必须合适，且需满足以下形式之一：(i) 沿主维度将所有输入张量连接起来；关于“连接”的定义，请参见 torch.cat()；(ii) 沿主维度将所有输入张量堆叠起来；关于“堆叠”的定义，请参见 torch.stack()。下面的示例能更好地说明所支持的输出形式。

input_tensor（Tensor）——当前进程要收集的张量。与 all_gather API 不同，此 API 中的所有输入张量在各个进程上的大小必须相同。

group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认进程组。

async_op（bool，可选）——该操作是否应为异步操作。

若 async_op 设为 True，则为异步工作句柄；否则或当前进程不属于该进程组时，此值为 None。

该操作会将整个进程组中的可序列化对象收集到一个列表中。

与 all_gather() 类似，但可传入 Python 对象。注意，只有可序列化的对象才能被收集。

object_list（list[Any]）——输出列表。其大小必须与当前集合操作所涉及的进程组大小一致，并将包含收集到的结果。

obj（Any）——当前进程要广播的可序列化 Python 对象。

group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认进程组。默认值为 None。

若调用该函数的进程属于该进程组，则集合操作的输出将被填充到输入的 object_list 中；若调用进程不属于该进程组，则传入的 object_list 将保持不变。

需要注意的是，此 API 与 all_gather() 集合操作略有不同，因为它不提供 async_op 句柄，因此属于阻塞式调用。

对于基于 NCCL 的进程组，必须在通信开始之前将对象的内部张量表示形式移动到 GPU 设备上。此时所使用的设备由 torch.cuda.current_device() 指定，用户有责任通过 torch.cuda.set_device() 确保每个进程都有独立的 GPU。

对象集合操作存在诸多严重的性能和可扩展性限制。详情请参阅“对象集合操作”相关章节。

all_gather_object() 函数会隐式使用 pickle 模块，而该模块存在安全风险。有人可能构造出恶意的 pickle 数据，在反序列化时执行任意代码。因此，请仅使用您信任的数据调用此函数。

使用 GPU 张量调用 all_gather_object() 的功能支持不佳且效率低下，因为需要先将张量序列化，从而导致 GPU 与 CPU 之间的数据传输。建议改用 all_gather() 函数。

该操作会在单个进程中收集一组张量。

此函数要求每个进程上的所有张量大小必须相同。

tensor（Tensor）——输入张量。

gather_list（list[Tensor]，可选）——用于存储收集后数据的、大小相同的张量列表（默认值为 None，必须在目标进程排名处指定）。

dst（int，可选）——全局进程组中的目标进程排名（与 group 参数无关）。若 dst 和 group_dst 均为 None，则默认为目标进程排名 0。

group（ProcessGroup，可选）——要操作的进程组。若未指定，则使用默认进程组。

async_op（bool，可选）——该操作是否应为异步操作。

group_dst（int，可选）——进程组内的目标进程排名。不能同时指定 dst 和 group_dst。

若 async_op 设为 True，则为异步工作句柄；否则或当前进程不属于该进程组时，此值为 None。

注意，gather_list 中的所有张量大小必须相同。

该操作会在单个进程中将整个进程组中的可序列化对象收集起来。

与 gather() 类似，但可传入 Python 对象。注意，只有可序列化的对象才能被收集。

obj（Any）——输入对象。必须是可序列化的。

object_gather_list（list[Any]）——输出列表。在目标进程排名处，其大小必须与当前集合操作所涉及的进程组大小一致，并将包含收集到的结果。在非目标进程排名处，此值必须为 None。（默认值为 None）

dst（int，可选）——全局进程组中的目标进程排名（与 group 参数无关）。若 dst 和 group_dst 均为 None，则默认为目标进程排名 0。

group（Optional[ProcessGroup]）——（ProcessGroup，可选）：要操作的进程组。若未指定，则使用默认进程组。默认值为 None。

group_dst（int，可选）——进程组内的目标进程排名。不能同时指定 dst 和 group_dst。无。在目标节点上，object_gather_list 将包含集合操作的输出结果。

需注意，该 API 与 gather collective 略有不同，因为它不提供 async_op 接口，因此属于阻塞式调用。

对于基于 NCCL 的处理组，在进行通信之前，对象的内部张量表示必须先被移至 GPU 设备上。此时所使用的设备可通过 torch.cuda.current_device() 获取，用户有责任通过 torch.cuda.set_device() 确保每个节点都拥有独立的 GPU。

对象集合操作存在诸多严重的性能与可扩展性限制，详情请参阅“对象集合操作”相关内容。

gather_object() 会隐式使用 pickle 模块，而该模块存在安全风险——有人可能构造恶意的 pickle 数据，在反序列化时执行任意代码。请仅使用您信任的数据调用此函数。

使用 GPU 张量调用 gather_object() 的支持不佳且效率低下，因为需要先将张量序列化为字节流，从而导致 GPU 与 CPU 之间的数据传输。建议改用 gather() 函数。

将该组中的所有进程都分散一张张张量。

每个进程将恰好收到一个张量，并将其数据存储在对应的张量参数中。

支持复杂张量。

tensor（Tensor）——输出张量。

scatter_list（list[Tensor]）——需要分散的张量列表（默认值为 None，必须在源节点上指定）。

src（int）——全局进程组中的源节点编号（与 group 参数无关）。若同时设置 src 和 group_src 为 None，则默认使用全局编号 0 的节点。

group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认的进程组。

async_op（bool，可选）——该操作是否应为异步操作。

group_src（int，可选）——进程组内的源节点编号。不可同时指定 src 和 group_src。

若 async_op 设为 True，则为异步操作的处理句柄；否则或不属于该进程组时则为 None。

需注意，scatter_list 中的所有张量尺寸必须相同。

将 scatter_object_input_list 中的可序列化对象分散到整个进程组中。

与 scatter() 类似，但可以传递 Python 对象。在每个节点上，分散后的对象将作为 scatter_object_output_list 的第一个元素存储。需注意，scatter_object_input_list 中的所有对象都必须可序列化才能被分散。

scatter_object_output_list（List[Any]）——非空列表，其第一个元素将存储分散到该节点的对象。

scatter_object_input_list（List[Any]，可选）——需要分散的输入对象列表。每个对象都必须可序列化。仅源节点上的对象会被分散，非源节点对应的参数可设置为 None。

src（int）——用于分散 scatter_object_input_list 的源节点编号。源节点编号基于全局进程组（与 group 参数无关）。若同时设置 src 和 group_src 为 None，则默认使用全局编号 0 的节点。

group（Optional[ProcessGroup]）——（ProcessGroup，可选）：要操作的进程组。若为 None，则使用默认的进程组。默认值为 None。

group_src（int，可选）——进程组内的源节点编号。不可同时指定 src 和 group_src。

无。如果当前节点属于该进程组，则 scatter_object_output_list 的第一个元素将为该节点的分散对象。

需注意，该 API 与 scatter collective 略有不同，因为它不提供 async_op 接口，因此属于阻塞式调用。

对象集合操作存在诸多严重的性能与可扩展性限制，详情请参阅“对象集合操作”相关内容。

scatter_object_list() 会隐式使用 pickle 模块，而该模块存在安全风险——有人可能构造恶意的 pickle 数据，在反序列化时执行任意代码。请仅使用您信任的数据调用此函数。

使用 GPU 张量调用 scatter_object_list() 的支持不佳且效率低下，因为需要先将张量序列化为字节流，从而导致 GPU 与 CPU 之间的数据传输。建议改用 scatter() 函数。

先对一张张量列表进行求和操作，再将结果分散到该组中的所有进程。

output（Tensor）——输出张量。

input_list（list[Tensor]）——需要先求和再分散的张量列表。

op（可选）——torch.distributed.ReduceOp 枚举中的值之一，用于指定逐元素求和的操作类型。

group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认的进程组。

async_op（bool，可选）——该操作是否应为异步操作。

若 async_op 设为 True，则为异步操作的处理句柄；否则或不属于该进程组时则为 None。

先对一个张量进行求和操作，再将结果分散到该组中的所有节点。

output（Tensor）——输出张量。其在所有节点上的尺寸必须相同。

input（Tensor）——需要求和后再分散的输入张量。其尺寸应为输出张量尺寸乘以世界大小。输入张量的形状可以是以下两种之一：(i) 沿主维度对多个输出张量进行连接；或 (ii) 沿主维度对多个输出张量进行堆叠。“连接”的定义可参考 torch.cat()，“堆叠”的定义可参考 torch.stack()。

group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认的进程组。

async_op（bool，可选）——该操作是否应为异步操作。

若 async_op 设为 True，则为异步操作的处理句柄；否则或不属于该进程组时则为 None。

先将输入张量拆分，再将拆分后的列表分散到该组中的所有进程。

之后，会将该组中所有进程接收到的张量重新连接起来，作为一个单个的输出张量返回。

支持复杂张量。

output（Tensor）——拼接后的汇总输出张量。

input（Tensor）——需要分散的输入张量。

output_split_sizes——（list[Int]，可选）：如果未指定或为空，则为输出张量第 0 维度的拆分大小。该维度大小必须能被世界大小整除。

input_split_sizes——（list[Int]，可选）：如果未指定或为空，则为输入张量第 0 维度的拆分大小。该维度大小必须能被世界大小整除。

group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认的进程组。

async_op（bool，可选）——该操作是否应为异步操作。

若 async_op 设为 True，则为异步操作的处理句柄；否则或不属于该进程组时则为 None。

all_to_all_single 为实验性功能，可能会发生变化。

将该组中的所有输入张量分散到每个进程，然后在输出列表中返回汇总后的张量列表。

支持复杂张量。

output_tensor_list（list[Tensor]）——每个节点需要汇总一个的张量列表。

input_tensor_list（list[Tensor]）——每个节点需要分散一个的张量列表。

group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认的进程组。

async_op（bool，可选）——该操作是否应为异步操作。

若 async_op 设为 True，则为异步操作的处理句柄；否则或不属于该进程组时则为 None。

all_to_all 为实验性功能，可能会发生变化。

同步所有进程。

此集合操作会阻塞进程，直到整个进程组都进入该函数；或者当 async_op 设为 False 时，也会一直阻塞；又或者当在 wait() 方法上调用异步处理句柄时，同样会保持阻塞状态。

group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认的进程组。

async_op（bool，可选）——该操作是否应为异步操作。

device_ids（[int]，可选）——设备/GPU 编号列表。预期仅包含一个编号。

若 async_op 设为 True，则为异步操作的处理句柄；否则或不属于该进程组时则为 None。

ProcessGroupNCCL 会阻塞 CPU 线程，直到屏障集合操作完成。

ProcessGroupNCCL 将屏障操作实现为对一个仅含 1 个元素的张量进行 all_reduce 操作。必须为该张量的分配选择一个设备。设备选择顺序如下：(1) 若 barrier 函数的 device_ids 参数非空，则优先使用该参数指定的第一个设备；(2) 若 init_process_group 参数非空，则使用该参数指定的设备；(3) 如果之前已经执行过其他需要张量输入的集合操作，则使用首次使用该进程组时的设备；(4) 最后根据全局节点编号对本地设备数量取模得到的索引来选择设备。

类似于 torch.distributed.barrier，但增加了可配置的超时时间。

它能够报告在指定超时时间内未能通过该屏障的节点。具体而言，对于非零编号的节点，会一直阻塞，直到收到来自编号 0 的发送/接收操作；而编号 0 的节点则会一直阻塞，直到处理完所有其他节点的发送/接收操作，并会为那些未能及时响应的节点报告失败。需注意，如果某个节点无法到达 monitored_barrier（例如因程序挂起），那么所有其他节点在 monitored_barrier 处也会失败。

此集合操作会阻塞该组中的所有进程/节点，直到整个进程组成功退出该函数，因此非常适合用于调试和同步操作。不过它可能会影响性能，仅建议在调试或需要在主机端实现完全同步的场景中使用。出于调试目的，可以在应用程序的集合操作之前插入此屏障，以检查是否有节点不同步。

需注意，此集合操作仅支持 GLOO 后端。

group（ProcessGroup，可选）——要操作的进程组。若为 None，则使用默认的进程组。

timeout（datetime.timedelta，可选）——monitored_barrier 的超时时间。如果未指定，则使用默认的进程组超时时间。

wait_all_ranks（bool，可选）——是否需要收集所有失败的节点。默认值为 False，此时编号 0 上的 monitored_barrier 会在遇到第一个失败的节点时就抛出异常，以实现快速失败。若将 wait_all_ranks 设为 True，则 monitored_barrier 会收集所有失败的节点，并抛出一个包含所有失败节点信息的错误。

Work 对象代表 PyTorch 分布式包中待处理的异步操作的句柄。它由非阻塞型集合操作返回，例如 dist.all_reduce(tensor, async_op=True)。

它会阻塞当前正在运行的 GPU 流程，直到操作完成。对于基于 GPU 的集合操作，这相当于同步操作；而对于由 CPU 发起的集合操作（如使用 Gloo），则会阻塞 CUDA 流程，直到操作完成。

在所有情况下，此函数都会立即返回结果。

要检查操作是否成功，应通过异步方式查询 Work 对象的结果。

它是一个与操作完成相关的 torch.futures.Future 对象。例如，可以通过 fut = process_group.allreduce(tensors).get_future() 来获取该 Future 对象。

以下是一个简单的 DDP 通信示例，演示了如何使用 get_future API 获取与 allreduce 操作完成相关的 Future 对象。`get_future` API支持NCCL后端，同时也部分支持GLOO和MPI后端（但不支持如send/recv之类的点对点操作），并且会返回一个`torch.futures.Future`对象。

在上面的示例中，`allreduce`操作将在GPU上通过NCCL后端执行。`fut.wait()`会在将相应的NCCL数据流与PyTorch当前设备的数据流同步之后才返回，这样就能实现异步的CUDA执行，而无需等待GPU上的整个操作完成。需要注意的是，`CUDAFuture`不支持`TORCH_NCCL_BLOCKING_WAIT`标志或NCCL的屏障函数`barrier()`。此外，如果通过`fut.then()`添加了回调函数，它将一直等待直到WorkNCLL的NCCL数据流与ProcessGroupNCCL的专用回调数据流同步，然后在回调数据流上运行该回调函数后直接调用它。`fut.then()`会返回另一个`CUDAFuture`对象，其中包含回调函数的返回值以及记录了回调数据流的`CUDAEvent`对象。

对于CPU上的操作，当任务完成且`value()`张量准备就绪时，`fut.done()`会返回`True`。

对于GPU上的操作，只有当操作已被提交后，`fut.done()`才会返回`True`。

对于混合CPU-GPU操作（例如通过GLOO发送GPU张量），当张量到达各个节点时，`fut.done()`会返回`True`，但它们未必已在各自的GPU上完成同步（这与GPU操作的情况类似）。

该类会返回一个整数类型的`torch.futures.Future`对象，该对象对应于`WorkResult`枚举类型。例如，可以通过`fut = process_group.allreduce(tensor).get_future_result()`来获取这个未来对象。

用户可以使用`fut.wait()`来阻塞式等待任务完成，并通过`fut.value()`获取`WorkResult`结果。此外，用户还可以使用`fut.then(call_back_func)`来注册一个回调函数，在任务完成后自动调用，而不会阻塞当前线程。

`get_future_result` API支持NCCL后端。

在正常情况下，用户无需设置超时时间。调用`wait()`与调用`synchronize()`效果相同——即让当前数据流在NCCL操作完成时阻塞等待。但如果设置了超时时间，它将阻塞CPU线程，直到NCCL操作完成或达到超时时间，否则会抛出异常。

这是一个表示可用归约操作的类似枚举的类：`SUM`、`PRODUCT`、`MIN`、`MAX`、`BAND`、`BOR`、`BXOR`以及`PREMUL_SUM`。

使用NCCL后端时，`BAND`、`BOR`和`BXOR`这些归约操作是不可用的。

`AVG`操作会在对各个节点的值求和之前先将其除以全局节点总数。该操作仅支持NCCL后端，且要求NCCL版本为2.10或更高。

`PREMUL_SUM`操作会在归约之前在本地将输入值与给定的标量相乘。该操作同样仅支持NCCL后端，且要求NCCL版本为2.11或更高。用户应使用`torch.distributed._make_nccl_premul_sum`函数来实现该功能。

另外，`MAX`、`MIN`和`PRODUCT`操作不支持复杂张量。

该类中的各个值可以作为属性来访问，例如`ReduceOp.SUM`。它们被用于指定归约集合操作的策略，比如`reduce()`函数。

该类不支持`__members__`属性。

这是一个已过时的、类似枚举的归约操作类：`SUM`、`PRODUCT`、`MIN`和`MAX`。建议使用`ReduceOp`类来替代它们。

`torch.distributed`模块内置了一个分布式键值存储系统，可用于在进程组内的各个进程之间共享信息，同时也可用于在`torch.distributed.init_process_group()`函数中初始化该分布式系统（此时可以通过显式创建存储对象来替代指定`init_method`参数）。该键值存储系统共有三种类型：`TCPStore`、`FileStore`和`HashStore`。

这是所有存储实现类的基类，例如PyTorch分布式系统中提供的那三种存储：`TCPStore`、`FileStore`和`HashStore`。

首次对某个给定键调用`add()`方法时，会在存储中为该键创建一个计数器，其初始值为`amount`。后续再次对该键调用`add()`方法时，计数器值将按指定量递增。如果试图对已经被`set()`方法在存储中设置过的键再次调用`add()`方法，则会引发异常。

- `key`（str）：存储中要对其计数器进行递增的键。
- `amount`（int）：计数器要递增的数值。

根据指定的键和值将键值对添加到存储中。如果该键在存储中尚不存在，系统会自动创建它。

- `key`（str）：要添加到存储中的键。
- `value`（str）：要与该键关联并添加到存储中的值。

用于检查给定的键列表中是否有对应的值存储在存储中。在正常情况下，此方法会立即返回结果，但在某些边缘情况下仍可能引发死锁，例如在`TCPStore`已被销毁后仍尝试调用`check()`方法。该方法接受一个键列表，用于查询这些键是否存储在存储中。

- `keys`（list[str]）：要查询是否存储在存储中的键列表。

复制存储对象并返回一个新的对象，该新对象指向与原对象相同的底层存储。返回的这个存储对象可以与原对象同时使用。这样做的目的是通过为每个线程克隆一个存储对象，为多线程安全地使用存储提供保障。

根据指定的键将键值对插入存储中，并在插入之前比较`expected_value`和`desired_value`的值。只有当该键在存储中已存在对应的`expected_value`，或者`expected_value`为空字符串时，才会设置`desired_value`。

- `key`（str）：要在存储中检查的键。
- `expected_value`（str）：插入前要检查的与该键关联的值。
- `desired_value`（str）：要添加到存储中的与该键关联的值。

从存储中删除与指定键关联的键值对。如果删除成功则返回`True`，否则返回`False`。

`delete_key` API仅支持`TCPStore`和`HashStore`类型。在`FileStore`上使用此API会引发异常。

- `key`（str）：要从存储中删除的键。

如果键已被删除则返回`True`，否则返回`False`。

从存储中获取与指定键关联的值。如果该键不存在于存储中，函数将会等待存储初始化时设定的超时时间，之后才会抛出异常。

- `key`（str）：函数将返回与该键关联的值。

如果键存在于存储中，则返回与该键关联的值。

如果存储支持扩展操作，则返回`True`。

从存储中检索所有指定键对应的值。如果`keys`列表中的某个键不存在于存储中，函数将会等待超时时间。

- `keys`（List[str]）：要从存储中检索的键列表。

根据指定的键和值将一系列键值对插入存储中。

- `keys`（List[str]）：要插入的键列表。
- `values`（List[str]）：要插入的值列表。

返回存储中已设置的键的数量。需要注意的是，这个数值通常会比通过`set()`和`add()`方法添加的键的数量多1，因为需要一个额外的键来协调所有使用该存储的进程。

当与`TCPStore`一起使用时，`num_keys`返回的是写入底层文件的键的数量。如果存储被销毁，然后使用同一个文件创建了新的存储对象，原有的键信息将会被保留。

返回存储中现有的键的数量。

返回指定队列的长度。如果队列不存在，则返回0。更多详细信息请参见`queue_push`函数。

- `key`（str）：用于获取队列长度的键。

从指定的队列中取出一个值；如果队列为空，则会等待超时时间。更多详细信息请参见`queue_push`函数。

如果`block`参数设置为`False`，且队列为空，则会引发`dist.QueueEmptyError`异常。

- `key`（str）：要从其中取值的队列的键。
- `block`（bool）：是否阻塞等待该键的值，还是立即返回。

将一个值插入到指定的队列中。

如果队列操作和设置/获取操作使用相同的键，可能会导致不可预期的行为。

队列支持`wait`/`check`操作。

对队列调用`wait`方法时，只会唤醒一个正在等待的进程，而不是所有进程。

- `key`（str）：要向其中插入值的队列的键。
- `value`（str）：要插入队列中的值。

根据指定的键和值将键值对插入存储中。如果该键已经存在于存储中，新的值将会覆盖原有的值。

- `key`（str）：要添加到存储中的键。
- `value`（str）：要与该键关联并添加到存储中的值。

设置存储的默认超时时间。此超时时间会在存储初始化期间以及`wait()`和`get()`方法中被使用。

- `timeout`（timedelta）：要在存储中设置的超时时间。

获取存储的当前超时时间。

```python
wait(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str]) -> None
```

等待`keys`列表中的每个键都被添加到存储中。如果在存储初始化时设定的超时时间到期之前，并非所有键都已被设置，那么`wait()`方法将会抛出异常。

- `keys`（list）：需要等待其被添加到存储中的键列表。

```python
wait(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str], arg1: datetime.timedelta) -> None
```

等待`keys`列表中的每个键都被添加到存储中。如果到指定的超时时间为止，这些键仍未被设置，该方法将会抛出异常。

- `keys`（list）：需要等待其被添加到存储中的键列表。
- `timeout`（timedelta）：等待这些键被添加到存储中的最大时间，超过该时间后将抛出异常。

这是一种基于TCP的分布式键值存储实现方式。服务器存储负责保存数据，而客户端存储可以通过TCP连接到服务器存储，进而执行各种操作，如使用`set()`方法插入键值对、使用`get()`方法检索键值对等。由于客户端存储会等待服务器建立连接，因此系统中始终应有一个已初始化的服务器存储。

- `host_name`（str）：服务器存储应运行的主机名或IP地址。
- `port`（int）：服务器存储用于监听传入请求的端口号。
- `world_size`（int，可选）：存储用户的总数（客户端数量加上服务器本身，共1个）。默认值为`None`（表示存储用户数量不是固定值）。
- `is_master`（bool，可选）：初始化服务器存储时为`True`，客户端存储则为`False`。默认值为`False`。
- `timeout`（timedelta，可选）：存储在初始化期间以及`get()`和`wait()`等方法中使用的超时时间。默认值为`timedelta(seconds=300)`。
- `wait_for_workers`（bool，可选）：是否等待所有工作进程与服务器存储建立连接。此选项仅在`world_size`为固定值时适用。默认值为`True`。
- `multi_tenant`（bool，可选）：如果设置为`True`，则当前进程中所有使用相同主机/端口的`TCPStore`实例将会共享同一个底层TCPServer。默认值为`False`。master_listen_fd（整数，可选）——若指定该参数，底层的TCPServer将在此文件描述符上监听，该描述符必须是一个已绑定到端口的套接字。如需绑定临时端口，建议将端口设置为0并通过其他方式获取端口值。默认值为None（表示服务器会创建一个新套接字并尝试将其绑定到某个端口）。

use_libuv（布尔值，可选）——若设置为True，则使用libuv作为TCPServer的后端。默认值为True。

创建一个新的TCPStore。

获取该存储用于接收请求的主机名。

如果正在使用libuv后端，则返回True。

获取该存储用于接收请求的端口号。

这是一种基于哈希表实现的线程安全存储方式。该存储可在同一进程内被其他线程使用，但无法在跨进程环境中使用。

创建一个新的HashStore。

一种通过文件来存储键值对的存储实现方式。

file_name（字符串）——用于存储键值对的文件路径。

world_size（整数，可选）——使用该存储的进程总数。默认值为-1（负数值表示存储使用者的数量并非固定）。

创建一个新的FileStore。

获取FileStore用于存储键值对的文件路径。

这是一种对TCPStore、FileStore和HashStore这三种键值存储中的任意一种进行封装的类，它会在插入存储的每个键前添加一个前缀。

prefix（字符串）——在将键插入存储之前需添加的前缀字符串。

store（torch.distributed.store）——构成底层键值存储的存储对象。

创建一个新的PrefixStore。

获取PrefixStore所封装的底层存储对象。

需要注意的是，您可以使用torch.profiler（推荐，仅适用于1.8.1版本之后）或torch.autograd.profiler来对文中提到的集合通信和点对点通信API进行性能分析。所有开箱即用的后端（gloo、nccl、mpi）都受到支持，集合通信的使用情况也会如预期般显示在性能分析结果或追踪数据中。对代码进行性能分析的方法与普通torch操作相同：

如需了解性能分析工具的所有功能，请参阅相关文档。

多GPU函数（即每个CPU线程对应多个GPU的功能）已被弃用。目前，PyTorch Distributed推荐的编程模型是每个线程对应一个设备，本文档中的API即为该模型的示例。如果您是后端开发人员且希望支持每个线程对应多个设备，请联系PyTorch Distributed的维护者。

对象集合通信存在诸多严重限制。请继续阅读以判断其在您的应用场景中是否安全可用。

对象集合通信是一组类似集合操作的机制，只要Python对象可以被序列化，就可以对其使用这些操作。虽然实现了多种集合操作模式（如广播、全收集等），但它们大致都遵循以下流程：

将输入对象转换为pickle格式的原始字节，然后将其放入一个字节张量中；

首先向其他节点传递该字节张量的大小信息（即第一阶段的集合操作）；

为执行实际的集合操作而分配大小合适的张量；

接着传递对象数据本身（即第二阶段的集合操作）；

最后将原始数据重新转换为Python对象（即反序列化）。

对象集合通信有时会表现出出乎意料的性能或内存特性，从而导致运行时间过长或内存不足，因此应谨慎使用。以下是一些常见的问题。

序列化/反序列化时间不对称——根据对象的数量、类型和大小不同，对象的序列化操作可能会比较耗时。当通信为“入射型”模式（如gather_object）时，接收节点需要反序列化的对象数量是发送节点序列化对象数量的N倍，这可能导致其他节点在后续的集合通信中超时。

张量通信效率低下——张量应通过常规的集合通信API进行传输，而非对象集合通信API。虽然也可以通过对象集合通信API传输张量，但这样做需要对张量进行序列化和反序列化处理（对于非CPU张量，还需进行CPU同步以及设备到主机的数据复制），除用于代码调试或故障排查外，在几乎所有情况下，都建议重新编写代码以使用常规的集合通信方式。

张量所在的设备意外变化——如果您仍想通过对象集合通信传输张量，那么对于cuda（以及其他可能的加速器）张量还存在一个特殊问题。如果对当前位于cuda:3设备上的张量进行序列化后再反序列化，无论您处于哪个进程，也无论该进程的“默认”CUDA设备是什么，反序列化后的张量仍将位于cuda:3设备上。而使用常规的张量集合通信API时，“输出张量”始终会位于同一个本地设备上，这通常也是人们所期望的结果。

如果这是进程首次使用GPU，反序列化张量时会隐式激活CUDA上下文，从而导致大量GPU内存被占用。为避免这一问题，应在将张量作为对象集合通信的输入之前先将其移至CPU上。

除了内置的GLOO/MPI/NCCL后端外，PyTorch Distributed还通过运行时注册机制支持第三方后端。关于如何通过C++扩展开发第三方后端的参考信息，请参阅“教程——自定义C++和CUDA扩展”以及test/cpp_extensions/cpp_c10d_extension.cpp文件。第三方后端的功能由其自身的实现方式决定。

新的后端继承自c10d::ProcessGroup，在被导入时会通过torch.distributed.Backend.register_backend()方法注册后端名称及实例化接口。

当手动导入该后端，并使用对应的后端名称调用torch.distributed.init_process_group()时，torch.distributed模块就会在新的后端上运行。

目前对第三方后端的支持仍处于实验阶段，可能会发生变化。

torch.distributed模块还提供了一个名为torch.distributed.launch的启动工具。该辅助工具可用于在每个节点上启动多个进程，从而实现分布式训练。

torch.distributed.launch模块。

torch.distributed.launch是一个可在每个训练节点上启动多个分布式训练进程的模块。

该模块即将被torchrun取代。

该工具可用于单节点分布式训练，即在一个节点上启动一个或多个进程。它既支持CPU训练，也支持GPU训练。若用于GPU训练，每个分布式进程将在单个GPU上运行，这有助于显著提升单节点训练性能。此外，它也可用于多节点分布式训练，通过在每个节点上启动多个进程来进一步提升多节点训练的性能。对于那些拥有多个支持直接GPU连接的Infiniband接口的系统而言，这种方式尤其有益，因为所有接口都可以被用于提升通信带宽。

无论是单节点分布式训练还是多节点分布式训练，该工具都会按照--nproc-per-node参数指定的数量在每个节点上启动相应数量的进程。若用于GPU训练，此数值必须小于或等于当前系统上的GPU数量（即nproc_per_node），并且每个进程将在从GPU 0到GPU (nproc_per_node - 1)中的某个单个GPU上运行。

如何使用该模块：

单节点多进程分布式训练

多节点多进程分布式训练：例如两个节点的场景

节点1：IP地址为192.168.1.1，可用端口为1234

要查看该模块提供的可选参数，请注意以下几点：

1. 目前，该工具以及多进程分布式（单节点或多节点）GPU训练在使用NCCL分布式后端时才能获得最佳性能。因此，建议在GPU训练中使用NCCL后端。

2. 在您的训练程序中，必须解析命令行参数--local-rank=LOCAL_PROCESS_RANK，该参数会由该工具提供。如果您的训练程序使用了GPU，应确保代码仅在LOCAL_PROCESS_RANK对应的GPU设备上运行。实现方式如下：

解析local_rank参数

将设备设置为对应的本地进程排名

版本2.0.0中的变更：启动器会将--local-rank=<rank>参数传递给您的脚本。从PyTorch 2.0.0版本开始，推荐使用带连字符的--local-rank格式，而非之前使用的带下划线的形式。

为保持向后兼容性，用户可能需要在参数解析代码中同时处理这两种格式，即在参数解析器中同时包含"--local_rank"和"--local_rank"两种写法。如果仅提供"--local_rank"，启动器将会报错：“error: unrecognized arguments: –local-rank=<rank>”。对于仅支持PyTorch 2.0.0及以上版本的训练代码，只需包含"--local-rank"即可。

3. 在训练程序中，应在开头调用以下函数来启动分布式后端。强烈建议使用init_method=env://。虽然其他初始化方式（如tcp://）也可能可行，但env://是该模块官方支持的初始化方式。

4. 在训练程序中，您既可以使用常规的分布式功能，也可以使用torch.nn.parallel.DistributedDataParallel()模块。如果您的训练程序使用了GPU，并且希望使用torch.nn.parallel.DistributedDataParallel()模块，可参考以下配置方法。

请确保device_ids参数被设置为代码将要运行的唯一GPU设备编号，通常该编号即为进程的本地进程排名。换句话说，为了使用该工具，device_ids必须为[args.local_rank]，output_device也应为args.local_rank。

5. 另一种将local_rank传递给子进程的方法是通过环境变量LOCAL_RANK。当您使用--use-env=True参数启动脚本时，就会启用此功能。此时需要修改上述子进程示例，将args.local_rank替换为os.environ['LOCAL_RANK']；因为设置了该标志后，启动器就不会再传递--local-rank参数。

需要注意的是，local_rank并非全局唯一的：它仅在机器上的每个进程中是唯一的。因此，不要用它来决定是否要向网络文件系统写入数据等操作。关于不正确处理此问题可能导致的后果，可参考pytorch/pytorch#12042中的示例。

torch.multiprocessing模块——torch.multiprocessing模块也提供了torch.multiprocessing.spawn()函数。该辅助函数可用于启动多个进程，其工作原理是传入您希望运行的函数，然后生成N个进程来执行该函数。这一功能也可用于多进程分布式训练。

关于如何使用该函数的参考信息，请参阅PyTorch示例——ImageNet实现方案。

需要注意的是，该函数要求使用Python 3.4或更高版本。由于难以理解的程序挂起、崩溃或各节点行为不一致，调试分布式应用往往颇具挑战。torch.distributed 提供了一套工具，可帮助用户以自助方式调试训练应用程序：

在分布式环境中使用 Python 的调试器极为方便，但由于其并非开箱即用，许多人根本不会使用它。PyTorch 为 pdb 提供了定制化的封装，简化了这一流程。

torch.distributed.breakpoint 让这一过程更加简单。它在内部通过两种方式定制 pdb 的断点行为，其余功能则与普通 pdb 完全相同。

- 仅在用户指定的某个节点上设置调试器。
- 通过调用 torch.distributed.barrier() 确保所有其他节点暂停执行，一旦被调试的节点发出 continue 命令，该屏障才会解除。
- 重新路由子进程的 stdin，使其连接到用户的终端。

使用方法非常简单：在所有节点上分别调用 torch.distributed.breakpoint(rank)，每个节点的 rank 值需保持一致。

从 v1.10 版本起，torch.distributed.monitored_barrier() 成为 torch.distributed.barrier() 的替代方案。后者在发生崩溃时无法正常工作，但会提供有用信息，指示可能是哪个节点出现了故障——即在规定时间内没有所有节点调用 torch.distributed.monitored_barrier()。该函数通过类似确认机制的发送/接收通信原语实现主机端的屏障功能，从而使节点 0 能够报告哪些节点未能及时响应屏障信号。例如，假设存在如下场景：节点 1 未调用 torch.distributed.monitored_barrier()（实际原因可能是应用程序漏洞或之前的集体操作导致程序挂起），则节点 0 会生成如下错误信息，帮助用户判断是哪个节点出现了问题并进一步排查。

通过设置环境变量 TORCH_DISTRIBUTED_DEBUG，结合 TORCH_CPP_LOG_LEVEL=INFO，可以触发更多有用的日志记录，并进行集体同步检查，以确保所有节点都能正确同步。TORCH_DISTRIBUTED_DEBUG 可根据所需的调试详细程度设置为 OFF（默认值）、INFO 或 DETAIL。需要注意的是，最详细的 DETAIL 模式可能会影响应用程序性能，因此仅应在调试问题时使用。

设置 TORCH_DISTRIBUTED_DEBUG=INFO 后，在使用 torch.nn.parallel.DistributedDataParallel() 训练的模型被初始化时会生成额外的调试日志；而设置 TORCH_DISTRIBUTED_DEBUG=DETAIL 则会在部分迭代过程中额外记录运行时性能统计信息，这些统计信息包括前向传播时间、反向传播时间、梯度通信时间等数据。例如，在如下应用程序中：

- 初始化时会输出相应的日志。
- 当设置 TORCH_DISTRIBUTED_DEBUG=DETAIL 时，运行期间也会生成日志。

此外，TORCH_DISTRIBUTED_DEBUG=INFO 还能增强对因模型中存在未使用参数而导致的 DistributedDataParallel() 崩溃的日志记录能力。目前，如果模型在前向传播过程中可能存在未使用的参数，就必须在使用 torch.nn.parallel.DistributedDataParallel() 初始化时设置 find_unused_parameters=True；而从 v1.10 版本起，由于该模块不支持在反向传播中使用未使用参数，所有模型输出都必须被用于损失计算。这些限制对大型模型而言尤为棘手，因此当发生崩溃时，DistributedDataParallel() 会记录所有未使用参数的完整名称。例如，在上述应用程序中，如果将损失函数修改为 loss = output[1]，那么 TwoLinLayerNet.a 在反向传播过程中将无法接收到梯度，从而导致 DDP 失败。在崩溃时，系统会提供有关未使用参数的信息，对于大型模型而言，手动查找这些参数可能十分困难。

设置 TORCH_DISTRIBUTED_DEBUG=DETAIL 后，无论用户是直接还是间接地发起任何集体操作（如 DDP allreduce），系统都会进行额外的一致性和同步性检查。这是通过创建一个包装进程组来实现的，该包装进程组会包裹 torch.distributed.init_process_group() 和 torch.distributed.new_group() 接口返回的所有进程组。这样一来，这些接口返回的将是一个包装进程组，其使用方式与普通进程组完全相同，但在将集体操作派发到底层进程组之前会先进行一致性检查。目前，这些检查包括调用 torch.distributed.monitored_barrier()，以确保所有节点都完成尚未处理的集体操作，并标识出那些卡住的节点。随后，还会对集体操作本身进行一致性检查，确保所有集体函数匹配且传入的张量形状一致。如果出现不一致，应用程序崩溃时会生成详细的错误报告，而非仅显示程序挂起或模糊的错误信息。例如，假设存在如下函数，在调用 torch.distributed.all_reduce() 时传入了形状不匹配的参数：

在使用 NCCL 后端时，此类应用程序很可能会导致程序挂起，在复杂场景下很难定位根本原因。如果用户启用 TORCH_DISTRIBUTED_DEBUG=DETAIL 并重新运行应用程序，以下的错误信息就能帮助揭示根本原因。

为了在运行时更精细地控制调试级别，还可以使用 torch.distributed.set_debug_level()、torch.distributed.set_debug_level_from_env() 和 torch.distributed.get_debug_level() 这些函数。

此外，当检测到集体操作出现不同步现象时，可将 TORCH_DISTRIBUTED_DEBUG=DETAIL 与 TORCH_SHOW_CPP_STACKTRACES=1 结合使用，以记录完整的调用栈。这些集体操作不同步检查适用于所有使用由 torch.distributed.init_process_group() 和 torch.distributed.new_group() 接口创建的进程组，并依赖 c10d 集体操作的应用程序。

除了通过 torch.distributed.monitored_barrier() 和 TORCH_DISTRIBUTED_DEBUG 提供的显式调试支持外，torch.distributed 的底层 C++ 库还会输出不同级别的日志信息。这些日志有助于了解分布式训练任务的执行状态，以及排查网络连接故障等问题。下表展示了如何通过组合使用 TORCH_CPP_LOG_LEVEL 和 TORCH_DISTRIBUTED_DEBUG 环境变量来调整日志级别。

| TORCH_DISTRIBUTED_DEBUG 设置 | 日志级别说明 |
|--------------------------|--------------|
| 默认值 OFF                | 不输出额外调试日志 |
| INFO                     | 输出基础调试日志 |
| DETAIL                  | 输出最详细的调试日志 |

在分布式环境中发生错误时抛出的异常类型：

- torch.distributed.DistError：所有分布式异常的基类。
- torch.distributed.DistBackendError：当后端出现特定错误时抛出，例如使用 NCCL 后端时用户尝试使用 NCCL 库无法访问的 GPU。
- torch.distributed.DistNetworkError：当网络库出现错误时抛出，例如“连接被对端断开”。
- torch.distributed.DistStoreError：当存储模块出现错误时抛出，例如“TCPStore 超时”。

---

## DistributedDataParallel#

**网址：** https://pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html

**内容概述：**
- DistributedDataParallel#

在模块级别基于 torch.distributed 实现分布式数据并行处理。

该模块通过同步各模型副本之间的梯度来实现数据并行。需要同步的设备由输入进程组指定，默认情况下即为整个系统。需要注意的是，DistributedDataParallel 并不会对输入数据进行分块或拆分到不同的 GPU 上；用户需自行定义分片方式，例如可以通过使用 DistributedSampler 来实现。

另请参阅：基础知识及使用建议。建议优先使用 nn.parallel.DistributedDataParallel，而非 multiprocessing 或 nn.DataParallel。其对输入数据的约束与 torch.nn.DataParallel 相同。

要创建该类，必须先通过调用 torch.distributed.init_process_group() 初始化 torch.distributed。

实践证明，对于单节点多 GPU 的数据并行训练，DistributedDataParallel 的性能显著优于 torch.nn.DataParallel。

要在拥有 N 个 GPU 的主机上使用 DistributedDataParallel，需要启动 N 个进程，确保每个进程仅使用 0 到 N-1 之间的某个 GPU。实现方式可以是为每个进程设置 CUDA_VISIBLE_DEVICES 环境变量，或者调用针对 GPU 的相应 API，亦或是调用通用的加速器初始化 API（其中 i 的取值范围为 0 到 N-1）。在每个进程中，应参考相关文档来构建该模块，或者直接使用最新的初始化 API。

若要在单个节点上启动多个进程，可以使用 torch.distributed.launch 或 torch.multiprocessing.spawn。

有关分布式训练所有功能的简要介绍，请参阅 PyTorch 分布式训练概述文档。

DistributedDataParallel 可与 torch.distributed.optim.ZeroRedundancyOptimizer 结合使用，以减少每个节点的优化器状态所占内存。更多详细信息请参阅 ZeroRedundancyOptimizer 的相关说明。

目前，NCCL 后端是使用 GPU 时的最快且最推荐的后端，这一结论既适用于单节点训练，也适用于多节点分布式训练。

该模块还支持混合精度分布式训练。这意味着模型中的参数可以是不同类型，例如同时包含 fp16 和 fp32 类型的参数，对于这类混合类型的参数，梯度聚合功能依然可以正常工作。

如果在某个进程中使用 torch.save 保存模型检查点，而在其他进程中使用 torch.load 加载该模型，请确保为每个进程正确配置 map_location 参数。如果不设置 map_location，torch.load 会将模型恢复到最初保存它的设备上。当模型在 M 个节点上以批量大小 N 进行训练时，如果对批次中的各个实例的损失值进行求和（而非通常的求平均，因为不同节点间的梯度会被平均），则该模型的梯度将会是仅在单个节点上以批量大小 M*N 训练时梯度的 1/M 倍。若希望获得与本地训练在数学上等价的训练过程，就需要考虑这一因素。但在大多数情况下，可将被 DistributedDataParallel 包装的模型、被 DataParallel 包装的模型以及运行在单个 GPU 上的普通模型视为等同（例如，可通过使用相同的学习率来保证批量大小一致）。

参数永远不会在进程之间进行广播。该模块会对梯度执行全量归约操作，并假设所有进程中的优化器会以相同方式修改这些梯度。缓冲区（如 BatchNorm 的统计量）则会在每一轮迭代中，从秩为 0 的进程中的模块处广播到系统中的所有其他副本。

如果同时使用 DistributedDataParallel 和分布式 RPC 框架，计算梯度时应始终使用 torch.distributed.autograd.backward()，而参数优化则需使用 torch.distributed.optim.DistributedOptimizer。

目前，DistributedDataParallel 对结合 torch.utils.checkpoint() 实现的梯度检查点功能的支持较为有限。若以 use_reentrant=False（推荐）的方式创建检查点，DDP 将能正常工作且不会出现任何限制。但如果使用 use_reentrant=True（默认值）创建检查点，并且模型中没有未使用的参数，且每个层最多只被检查点一次（请确保未向 DDP 传递 find_unused_parameters=True 参数），则 DDP 仍可正常运行。目前我们不支持某个层被多次检查点，或检查点后的模型中存在未使用参数的情况。

若要让非 DDP 模型从 DDP 模型加载状态字典，需先调用 consume_prefix_in_state_dict_if_present() 函数，去除 DDP 状态字典中的 “module” 前缀，然后再进行加载。

该模块的构造函数、前向传播方法以及输出值（或该模块输出值的某种函数）的梯度计算都是分布式同步点。鉴于不同进程可能会执行不同的代码，需特别留意这一点。

该模块假设在创建时所有参数都已注册到模型中。之后不得再添加或删除任何参数，缓冲区同样如此。

该模块还要求所有分布式进程中的参数注册顺序保持一致。模块本身会按照模型中参数的逆序执行梯度全量归约操作。换言之，确保每个分布式进程拥有完全相同的模型结构以及一致的参数注册顺序是用户的责任。

该模块允许参数具有非行主序连续的步长。例如，模型中可能有些参数的 torch.memory_format 为 torch.contiguous_format，而另一些则为 torch.channels_last 格式，但不同进程中的对应参数必须具有相同的步长。

该模块不支持与 torch.autograd.grad() 搭配使用（即仅当梯度需累积到参数的 .grad 属性中时才有效）。

如果计划将此模块与 nccl 后端或基于 Infiniband 的 gloo 后端一起使用，并且搭配使用多个工作进程的 DataLoader，那么请将多进程启动方式更改为 forkserver（仅适用于 Python 3）或 spawn。遗憾的是，基于 Infiniband 的 Gloo 和 NCCL2 都不具备分叉安全性，如果不更改此设置，很可能会出现死锁现象。

在用 DistributedDataParallel 对模型进行封装后，绝不应尝试修改模型的参数。因为在封装时，DistributedDataParallel 的构造函数会在模型创建时就为所有参数注册额外的梯度归约函数。若之后修改了模型参数，这些梯度归约函数将不再与当前的参数集合匹配。

目前，将 DistributedDataParallel 与分布式 RPC 框架结合使用仍处于实验阶段，功能可能会发生变化。skip_all_reduce_unused_params – 当设置为 True 时，DDP 将跳过对未使用参数的归约操作。这要求在整个训练过程中，所有节点上的未使用参数保持不变。若不满足此条件，可能会导致不同节点之间的同步失效，进而引发训练进程挂起。

module（模块）– 需要被并行化的模块。

用于在 DDP 中处理各节点输入规模不一致时的训练上下文管理器。

该上下文管理器会记录已加入的 DDP 进程，并通过插入集合通信操作来“模拟”前向与反向传播过程，使其与未加入进程所执行的操作相匹配。这样一来，每个集合通信操作都会对应已加入进程的相应操作，从而避免因节点输入不均而导致的训练挂起或错误。另外，如果设置了 throw_on_early_termination 为 True，则一旦某个节点的输入耗尽，所有训练进程都会抛出异常，便于根据应用逻辑捕获并处理这些错误。

当所有 DDP 进程都加入后，该上下文管理器会将最后一个加入的进程对应的模型副本广播给所有进程，以确保所有进程中的模型一致（这一点由 DDP 本身保证）。

若要利用该机制实现节点输入不均时的训练，只需将此上下文管理器包裹在训练循环中即可，无需对模型或数据加载部分进行额外修改。

如果被该上下文管理器包裹的模型或训练循环还包含其他分布式集合操作，例如模型前向传播中的 SyncBatchNorm，那么必须启用 throw_on_early_termination 标志。这是因为该上下文管理器并不了解非 DDP 类型的集合通信操作。启用该标志后，一旦某个节点的输入耗尽，所有节点都会抛出异常，从而便于整体恢复训练。

divide_by_initial_world_size（布尔值）– 若设置为 True，则梯度将按 DDP 启动时的初始世界大小进行划分；若设置为 False，则会在 allreduce 操作中根据当前有效世界大小（即尚未耗尽输入的节点数量）来划分梯度。将 divide_by_initial_world_size 设置为 True 可确保所有输入样本，包括那些输入规模不均的样本，在对全局梯度的贡献上具有相同的权重。即便遇到输入不均的情况，也会始终按初始世界大小来划分梯度，从而实现这一点。若将其设置为 False，则梯度将按剩余节点数量进行划分。虽然这样能保证与在较小世界大小下训练时的一致性，但也会导致输入不均的样本对全局梯度的贡献更大。通常，在训练数据中最后几批样本的规模不均时，建议将此参数设置为 True；而在输入数量差异极大的极端情况下，设置为 False 可能能获得更好的训练效果。

enable（布尔值）– 是否启用输入不均检测功能。若已知所有参与训练的节点输入规模均相同，可将其设置为 False 以禁用该功能。默认值为 True。

throw_on_early_termination（布尔值）– 当至少有一个节点的输入耗尽时，是抛出错误还是继续训练。若设置为 True，则一旦有节点的数据用完就会立即抛出异常；若设置为 False，则会以较小的有效世界大小继续训练，直到所有节点都加入为止。需要注意的是，一旦设置了此标志，divide_by_initial_world_size 标志将被忽略。默认值为 False。

DDP join hook 通过镜像前向与反向传播过程中的通信操作，实现了对输入不均情况的训练支持。

kwargs（字典）– 一个包含用于在运行时修改 join hook 行为的键值参数的字典；所有使用相同 join 上下文管理器的 Joinable 实例都会收到相同的 kwargs 值。

若该参数设置为 True，则梯度将按 DDP 启动时的初始世界大小进行划分；若设置为 False，则梯度将按有效世界大小（即未加入的进程数量）进行划分，这意味着输入不均的样本会对全局梯度产生更大的影响。通常情况下，当输入不均程度较小时应将其设置为 True，但在极端情况下也可设置为 False 以期望获得更好的训练效果。默认值为 True。

用于禁用 DDP 进程间梯度同步的上下文管理器。

在该上下文内部，梯度将累积在模块变量中，随后会在离开该上下文的第一次前向-反向传播过程中进行同步。

必须将前向传播操作置于该上下文管理器内部，否则梯度仍会进行同步。

用于为用户自定义的多节点梯度聚合算法注册通信钩子。

此类钩子对研究人员尝试新算法非常有用。例如，可以利用它来实现 GossipGrad 和梯度压缩等算法，这些算法在运行分布式数据并行训练时采用了不同的参数同步通信策略。

state（对象）– 传递给钩子，用于在训练过程中保存各种状态信息。例如梯度压缩中的错误反馈、GossipGrad 算法中需要后续通信的节点信息等。该状态由每个工作节点本地存储，并在节点上的所有梯度张量之间共享。

同样传递给钩子，用于在训练过程中保存状态信息。例如梯度压缩中的错误反馈、GossipGrad 算法中需要后续通信的节点信息等。

该状态由每个工作节点本地存储，并在节点上的所有梯度张量之间共享。

hook（可调用的函数）– 其签名如下：hook(state: object, bucket: dist.GradBucket) -> torch.futures.Future[torch.Tensor]：此函数会在 bucket 准备就绪后被调用。钩子可执行所需的任何处理操作，并返回一个 Future 对象，表示异步操作（如 allreduce）已完成。即便钩子没有执行任何通信操作，也必须返回一个表示操作已完成的 Future 对象。该 Future 对象应包含梯度桶中张量的新值。一旦 bucket 准备就绪，c10d reducer 会调用此钩子，并使用 Future 返回的张量将梯度复制到各个参数中。需注意，Future 的返回类型必须为单个张量。我们还提供了一个名为 get_future 的 API，用于获取与 c10d.ProcessGroup.Work 完成相关的 Future 对象。目前 get_future 支持 NCCL，也支持 GLOO 和 MPI 的大多数操作，但点对点操作（如 send/recv）除外。

其签名如下：hook(state: object, bucket: dist.GradBucket) -> torch.futures.Future[torch.Tensor]：

此函数会在 bucket 准备就绪后被调用。钩子可执行所需的任何处理操作，并返回一个 Future 对象，表示异步操作（如 allreduce）已完成。即便钩子没有执行任何通信操作，也必须返回一个表示操作已完成的 Future 对象。该 Future 对象应包含梯度桶中张量的新值。一旦 bucket 准备就绪，c10d reducer 会调用此钩子，并使用 Future 返回的张量将梯度复制到各个参数中。需注意，Future 的返回类型必须为单个张量。

我们还提供了一个名为 get_future 的 API，用于获取与 c10d.ProcessGroup.Work 完成相关的 Future 对象。目前 get_future 支持 NCCL，也支持 GLOO 和 MPI 的大多数操作，但点对点操作（如 send/recv）除外。

梯度桶中的张量不会预先按世界大小进行划分。用户需在需要执行 allreduce 等操作时自行完成按世界大小的分割。

DDP 通信钩子只能注册一次，且应在调用 backward 方法之前完成注册。

钩子返回的 Future 对象应包含一个与梯度桶中张量形状相同的单个张量。

get_future API 支持 NCCL，以及部分 GLOO 和 MPI 后端（不支持点对点操作，如 send/recv），并会返回一个 torch.futures.Future 对象。

以下是一个返回相同张量的 noop 钩子示例。

以下是一个 Parallel SGD 算法的示例，在该算法中，梯度会在 allreduce 之前被编码，之后再解码。

---

## DDP 通信钩子#

**网址：** https://pytorch.org/docs/stable/ddp_comm_hooks.html

**目录：**
- DDP 通信钩子#
- 如何使用通信钩子？#
- 通信钩子作用于哪些内容？#
- 默认通信钩子#
- PowerSGD 通信钩子#
  - PowerSGD 状态#
  - PowerSGD 钩子#
- 调试通信钩子#
- 通信钩子的检查点保存#
- 致谢#

创建时间：2025年6月6日 | 最后更新时间：2025年6月6日

DDP 通信钩子是一种通用接口，通过覆盖 DistributedDataParallel 中的默认 allreduce 操作，允许用户自定义节点间梯度传递的方式。系统提供了若干内置的通信钩子，用户可轻松选用这些钩子来优化通信效率；此外，该接口还支持用户自定义通信策略，以应对更复杂的应用场景。

要使用通信钩子，用户只需在训练循环之前让 DDP 模型注册该钩子，示例如下：

torch.nn.parallel.DistributedDataParallel.register_comm_hook()

通信钩子为梯度的全局归约提供了灵活的实现方式。因此，它主要在 allreduce 操作之前对每个副本上的梯度进行处理，通过将梯度分桶来增加通信与计算之间的重叠度。其中，torch.distributed.GradBucket 代表了一组需要被全局归约的梯度张量。

该类主要用于将经过 flatten 处理后的梯度张量（由 buffer() 方法返回）传递给 DDP 通信钩子。该张量还可进一步分解为该桶中每个参数对应的张量列表（通过 get_per_parameter_tensors() 方法获取），以便对模型各层分别进行操作。

由于在第一次迭代之后桶的结构会被重新构建，因此不应依赖训练初期的索引信息。

存储若干连续层梯度所在的桶的索引。所有梯度都会被分桶处理。

一个扁平化的 1D torch.Tensor 缓冲区，可进一步分解为该桶中每个参数对应的张量列表。

一个 torch.Tensor 列表。列表中的每个张量对应一个梯度值。

指示当前桶是否为某次迭代中最后一次进行全局归约的桶。这也意味着该桶对应的是前几层的数据。

用于用输入张量缓冲区替换桶中的张量。

一个 torch.Tensor 列表。列表中的每个张量对应一个模型参数。

默认的通信钩子都是简单无状态的结构，因此 register_comm_hook 方法的输入 state 要么是一个进程组对象，要么为 None。而输入的 bucket 对象则为 torch.distributed.GradBucket 类型。使用 GradBucket 张量调用 allreduce 操作。

当所有工作节点上的梯度张量被聚合后，后续的回调函数会计算这些张量的均值并返回结果。

如果用户注册了此 DDP 通信钩子，其输出结果应与未注册该钩子时的结果一致。因此，这不会改变 DDP 的原有行为，用户可将其作为参考，或修改该钩子以记录有用信息，或用于其他目的，而不会影响 DDP 的正常运行。

通过将 GradBucket 转换为 torch.float16 并除以进程组大小来实现压缩。

此 DDP 通信钩子采用了一种简单的梯度压缩方法：先将 GradBucket 张量转换为半精度浮点格式（torch.float16），再将其除以进程组大小，从而对那些 float16 格式的梯度张量进行 allreduce 操作。在完成压缩后的梯度张量 allreduce 后，后续的链式回调函数会将其解压并转换回原始数据类型（如 float32）。

警告：该 API 尚处于实验阶段，且需要 NCCL 版本高于 2.9.6。

此 DDP 通信钩子采用另一种简单的梯度压缩方法：先将 GradBucket 张量转换为半精度 Brain 浮点格式（torch.bfloat16），再将其除以进程组大小，从而对那些 bfloat16 格式的梯度张量进行 allreduce 操作。在完成压缩后的梯度张量 allreduce 后，后续的链式回调函数会将其解压并转换回原始数据类型（如 float32）。

此外，还提供了一个通信钩子封装函数，可用于封装 fp16_compress_hook() 或 bf16_compress_hook()，使其能够与其他通信钩子一起使用。

将输入张量转换为 torch.float16，再将钩子处理后的结果转换回原始数据类型。

该封装函数会将指定 DDP 通信钩子的输入梯度张量转换为半精度浮点格式（torch.float16），随后再将该钩子处理后的输出张量转换回原始数据类型，如 float32。因此，fp16_compress_hook 实际上等同于 fp16_compress_wrapper(allreduce_hook)。

Callable[[Any, GradBucket], Future[Tensor]]

警告：该 API 尚处于实验阶段，且需要 NCCL 版本高于 2.9.6。

该封装函数会将指定 DDP 通信钩子的输入梯度张量转换为半精度 Brain 浮点格式（torch.bfloat16），随后再将该钩子处理后的输出张量转换回原始数据类型，如 float32。

因此，bf16_compress_hook 实际上等同于 bf16_compress_wrapper(allreduce_hook)。

Callable[[Any, GradBucket], Future[Tensor]]

PowerSGD（Vogels 等人，NeurIPS 2019）是一种梯度压缩算法，能够实现极高的压缩率，并加速受带宽限制的分布式训练过程。该算法需要维护一些超参数以及内部状态，因此 PowerSGD 通信钩子属于有状态钩子，用户需按照以下要求提供状态对象。

在训练过程中，为所有梯度同时存储该算法的超参数与内部状态。

其中，matrix_approximation_rank 和 start_powerSGD_iter 是用户需要调整的主要超参数。为提升性能，建议始终启用 binary 超参数 use_error_feedback 和 warm_start。

matrix_approximation_rank 控制压缩后低秩张量的大小，进而决定压缩率。秩值越低，压缩效果越好。

1.1 如果 matrix_approximation_rank 设置得过低，模型将需要更多的训练步数才能达到理想精度，甚至根本无法达到，从而导致精度下降。

1.2 提高 matrix_approximation_rank 可能会显著增加压缩的计算成本，且当其超过某个阈值后，模型的精度可能不会再有提升。

建议从 1 开始调整 matrix_approximation_rank，以 2 为步长逐步递增（可采用指数网格搜索法，即 1、2、4……），直到获得满意的精度为止。通常情况下，该值取 1-4 即可。对于某些自然语言处理任务（如原论文附录 D 中所示），该值可提升至 32。

start_powerSGD_iter 用于将 PowerSGD 压缩操作延迟到 start_powerSGD_iter 步之后进行，在此之前仍会执行常规的 allreduce 操作。这种“常规 allreduce + PowerSGD”的混合方案即便使用相对较低的 matrix_approximation_rank，也能有效提升模型精度。这是因为训练初期对梯度精度极为敏感，过早压缩梯度可能会使训练很快进入次优路径，从而对精度造成不可逆转的损害。

建议从总训练步数的 10% 开始调整 start_powerSGD_iter，逐步增加直至达到满意精度。如果训练过程中存在热身阶段，start_powerSGD_iter 的值通常不应低于热身阶段的步数。

min_compression_rate 是对层进行压缩时所需的最低压缩率。由于压缩会带来一定的计算开销，只有当能够节省足够的带宽时，才值得对张量进行压缩，即需满足 (num_rows + num_cols) * matrix_approximation_rank * min_compression_rate < num_rows * num_cols。如果无法达到指定的压缩率阈值，该张量将直接进行 allreduce 操作而不会被压缩。

一旦开始 PowerSGD 压缩，就会按照 compression_stats_logging_frequency 的间隔频率记录压缩统计信息。

orthogonalization_epsilon 是一个非常小的数值（例如 1e-8），可在正交化步骤中添加到每个归一化的矩阵列中，以防止某个列全为 0 时出现除零错误。如果通过其他方式（如批量归一化）已能避免此类问题，为保证精度，建议将此参数设置为 0。

batch_tensors_with_same_shape 用于控制是否对批量操作中形状相同的张量进行压缩与解压，以此提升并行度。需要注意的是，还应增大桶大小（即 DDP 构造函数中的 bucket_cap_mb 参数），以便让更多形状相同的张量被归入同一个桶中。不过这样做可能会降低计算与通信之间的重叠程度，并因堆叠相同形状的张量而增加内存占用。当压缩/解压操作成为性能瓶颈时，可将该参数设置为 True。

如果启用了错误反馈或热身功能，DDP 中允许的 start_powerSGD_iter 最小值为 2。这是因为 DDP 在第 1 次迭代时会进行一次内部优化，重新构建桶结构，而此操作可能会与重建之前的任何张量数据产生冲突。

PowerSGD 通常需要与模型梯度大小相同的额外内存，用于实现错误反馈功能，以此弥补压缩通信中的偏差，进而提升精度。

PowerSGD 钩子可能与 Apex 自动混合精度包发生冲突。建议改用 PyTorch 原生的自动混合精度包。

实现 PowerSGD 算法。

此 DDP 通信钩子实现了论文中描述的 PowerSGD 梯度压缩算法。当所有工作节点上的梯度张量被聚合后，该钩子会按以下方式执行压缩操作：

将输入的扁平化一维梯度张量视为由各参数对应的张量组成的列表，并将这些张量分为两组：

1.1 需要在 allreduce 操作之前进行压缩的张量，因为此时压缩能够带来显著的带宽节省。

1.2 其余张量将直接进行 allreduce 操作而不会被压缩，其中包括所有表示偏置的向量张量。

处理未压缩的张量：

2.1 为这些未压缩的张量分配连续内存，然后以批量形式对其进行 allreduce 操作，且不进行压缩。

2.2 将这些未压缩的张量从连续内存中复制回输入张量中。

处理需要通过 PowerSGD 进行压缩的张量：

3.1 对每个张量 M，生成两个低秩张量 P 和 Q 用于分解 M，满足关系式 M = PQ^T，其中 Q 是从标准正态分布中初始化并经过正交化处理的。

3.2 计算每个 P 的值，其结果等于 MQ。

3.3 将这些 P 张量作为一个批量进行 allreduce 操作。

3.4 对这些 P 张量分别进行正交化处理。

3.5 计算每个 Q 的值，其结果近似等于 M^TP。

3.6 将这些 Q 张量作为一个批量进行 allreduce 操作。

3.7 从所有已压缩的张量中重新计算出每个 M 的值，其结果近似等于 PQ^T。

需要注意的是，该通信钩子在前 state.start_powerSGD_iter 次迭代中会强制使用常规的 allreduce 操作。这不仅能让用户更好地掌控加速效果与精度之间的权衡，还能为后续的通信钩子开发者简化 DDP 内部优化的复杂性。

state（PowerSGDState）——用于配置压缩率以及支持错误反馈、热身启动等功能的状态信息。要调整压缩参数，主要需要调整 matrix_approximation_rank、start_powerSGD_iter 和 min_compression_rate 这三个参数。

bucket（dist.GradBucket）——用于存储扁平化一维梯度张量的桶结构，该张量将多个对应不同参数的张量汇总在一起。需要注意的是，由于 DDP 通信钩子仅支持单进程单设备模式，因此该桶中最多只能存储一个张量。

用于处理通信操作的 Future 对象，可对梯度进行就地更新。

实现简化版的 PowerSGD 算法。

此 DDP 通信钩子实现了论文中描述的简化版 PowerSGD 梯度压缩算法。与原始版本不同，该简化版并非逐层压缩梯度，而是直接对汇总了所有梯度的扁平化输入张量进行压缩。因此，它的运行速度比 powerSGD_hook() 更快，但除非 matrix_approximation_rank 设为 1，否则其精度通常会显著降低。

在此版本中，提高 matrix_approximation_rank 不一定能提升精度，因为若不对各参数张量进行行列对齐就直接进行批量处理，可能会破坏低秩结构。因此，用户应首先考虑使用 powerSGD_hook()，只有当 matrix_approximation_rank 设为 1 时仍无法获得满意精度时，才考虑使用此简化版本。

当所有工作节点上的梯度张量被聚合后，该钩子会按以下方式执行压缩操作：

将输入的扁平化一维梯度张量视为一个带有 0 填充的方形张量 M。

生成两个低秩张量 P 和 Q 用于分解 M，满足关系式 M = PQ^T，其中 Q 是从标准正态分布中初始化并经过正交化处理的。

计算 P 的值，其结果等于 MQ。

计算 Q 的值，其结果近似等于 M^TP。

最终计算出 M 的值，其结果近似等于 PQ^T。

将输入张量截断回其原始长度。需注意，此通信钩子在前 `start_powerSGD_iter` 次迭代中会强制使用基础版的 allreduce 算法。这不仅能让用户更灵活地权衡加速效果与精度之间的平衡，还能为后续的通信钩子开发者简化 DDP 内部优化相关的复杂逻辑。

**state（PowerSGDState）**——用于配置压缩率并支持错误反馈、热启动等功能的状态信息。要调整压缩配置，主要需修改 `matrix_approximation_rank` 和 `start_powerSGD_iter` 这两个参数。

**bucket（dist.GradBucket）**——用于存储已展平为一维的梯度张量的容器，该张量会将多个针对不同变量的梯度张量进行批量处理。需要注意的是，由于 DDP 的通信钩子仅支持单进程单设备模式，因此此容器中最多只能存储一个张量。

该组件负责处理后续的通信操作，并直接在原位置更新梯度值。

顾名思义，调试用通信钩子仅用于调试及性能优化目的。其输出结果未必是准确的。

该函数会返回一个包裹了输入参数的 Future 对象，因此实际上相当于一个不会产生任何通信开销的空操作。

此钩子仅应用于分析 allreduce 优化的潜力，而非用于常规的梯度同步。例如，若在注册该钩子后训练时间的加速效果不足 10%，通常说明在这种情况下 allreduce 并非性能瓶颈。当无法轻易获取 GPU 跟踪信息，或存在 allreduce 操作与计算任务重叠、各节点间不同步等复杂因素导致跟踪分析困难时，这类调试工具尤为有用。

带状态功能的通信钩子可被保存为模型检查点的一部分，从而支持训练器的重新启动。若要让此类钩子具备序列化能力，需实现 `__setstate__` 和 `__getstate__` 方法。

`__getstate__` 方法应从返回的字典中排除那些不可序列化的属性。

`__setstate__` 方法则需正确初始化那些在提供的状态信息中被排除的不可序列化属性。

`PowerSGDState` 已实现了 `__setstate__` 和 `__getstate__` 方法，可作为参考实现。

该函数会返回一个 `Dict[str, Any]` 类型的对象，该对象随后会被序列化并保存。

`process_group` 对象不可序列化，因此不会被包含在返回的状态信息中。

该方法会使用输入的状态信息来初始化当前的 `PowerSGDState` 实例。

此时 `process_group` 会默认设置为相应的值。

以下是一个关于保存和重新加载 PowerSGD 状态及钩子的简单端到端示例。

特别感谢《PowerSGD》论文的作者 Thijs Vogels 对 PowerSGD 通信钩子进行了代码审查，并通过对比实验证明了该钩子的性能与原论文中的实现水平相当。

---

## 分布式检查点 - torch.distributed.checkpoint#

**网址：** https://pytorch.org/docs/stable/distributed.checkpoint.html

**目录：**
- 分布式检查点 - torch.distributed.checkpoint#
- 其他资源：#

创建时间：2022年11月16日 | 最后更新时间：2025年9月4日

分布式检查点（DCP）功能支持从多个节点并行加载和保存模型。它还具备运行时的重分片功能，使得模型可以在一种集群拓扑结构下保存，而在另一种拓扑结构下加载。

DCP 在多个重要方面不同于 `torch.save` 和 `torch.load`：

- 每个检查点会生成多个文件，每个节点至少对应一个文件。
- 它采用原位操作方式，即模型需先自行分配存储空间，DCP 便会直接使用这些已分配的空间来保存数据。

用于加载和保存检查点的入口函数如下：

- 分布式检查点（DCP）入门
- 使用分布式检查点（DCP）进行异步保存
- TorchTitan 检查点相关文档
- TorchTitan DCP 实现方案

该枚举用于指定异步检查点的类型。

此类对象包含用于表示数据预处理与上传操作完成状态的 Future 对象，由 `async_save()` 函数返回。`staging_completion` 是一个 Future 对象，用于指示本地 `state_dict` 的预处理操作是否已完成；`upload_completion` 则用于指示整个检查点的保存操作是否已经结束。

以 SPMD 模式保存分布式模型。

该函数与 `torch.save()` 不同之处在于，它能够处理 `ShardedTensor` 和 `DTensor` 类型的数据，因为每个节点只需保存自己负责的那部分数据片段即可。

对于所有同时拥有 `state_dict` 和 `load_state_dict` 方法的“带状态对象”，该函数在进行序列化之前会先调用 `state_dict` 方法。

需注意，不同版本的 PyTorch 对已保存的 `state_dict` 的兼容性并无保证。

如果使用了 `process_group` 参数，请确保只有属于该进程组的节点才会调用 `save_state_dict` 方法，且 `state_dict` 中的所有数据都应属于该进程组。

当为 FSDP 的 `ShardingStrategy.HYBRID_SHARD` 模式保存检查点时，只能由 `shard_group` 中的一个节点调用 `save_state_dict` 方法，同时还需传入对应的 `process_group` 对象。

本地进程中的 `state_dict`。

**state_dict（Dict[str, Any]）**——需要保存的 `state_dict` 对象。

**checkpoint_id（Union[str, os.PathLike, None]）**——该检查点实例的标识符。其具体含义取决于存储方式：它可以是文件夹或文件的路径；如果是键值存储系统，则可以是一个键值。（默认值：None）

**storage_writer（Optional[StorageWriter]）**——用于执行写入操作的 `StorageWriter` 实例。如果未指定此参数，DCP 会根据 `checkpoint_id` 自动推断出对应的写入器；若 `checkpoint_id` 也为 None，则会引发异常。（默认值：None）

**planner（Optional[SavePlanner]）**——`SavePlanner` 实例。如果未指定此参数，将使用默认的规划器。（默认值：None）

**process_group（Optional[ProcessGroup]）**——用于实现节点间同步的 `ProcessGroup` 对象。（默认值：None）

**no_dist（bool）**——若设置为 True，该函数将假定用户意图是在单个节点/进程中加载检查点。（默认值：False）

**use_collectives（bool）**——若设置为 False，该函数将假定用户意图是在不进行节点间同步的情况下保存检查点。（默认值：True）此配置仍处于实验阶段，使用时需谨慎，因为它会改变保存后检查点的格式，且可能存在向后兼容性问题。

用于存储已保存检查点元数据的对象。

`save_state_dict` 函数会利用集体通信机制来协调各个节点间的写入操作。对于基于 NCCL 的进程组，相关对象的内部张量表示形式必须在开始通信之前被移至 GPU 设备上。此时使用的设备由 `torch.cuda.current_device()` 指定，用户有责任通过 `torch.cuda.set_device()` 确保每个节点都拥有独立的 GPU。

`save` 函数的异步版本。该版本首先会将 `state_dict` 数据预处理并暂存到临时存储空间中（默认为 CPU 内存），然后在另一个线程中执行实际的保存操作。

此功能仍处于实验阶段，可能会发生变化。**在最后一个检查点保存完成后，必须调用 CLOSE 方法。**

**state_dict（Dict[str, Any]）**——需要保存的 `state_dict` 对象。

**checkpoint_id（Union[str, os.PathLike, None]）**——该检查点实例的标识符。其具体含义取决于存储方式：它可以是文件夹或文件的路径；如果是键值存储系统，则可以是一个键值。（默认值：None）

**storage_writer（Optional[StorageWriter]）**——用于执行数据预处理和保存操作的 `StorageWriter` 实例。如果未指定此参数，DCP 会根据 `checkpoint_id` 自动推断出对应的写入器；若 `checkpoint_id` 也为 None，则会引发异常。（默认值：None）

**planner（Optional[SavePlanner]）**——`SavePlanner` 实例。如果未指定此参数，将使用默认的规划器。（默认值：None）

**process_group（Optional[ProcessGroup]）**——用于实现节点间同步的 `ProcessGroup` 对象。（默认值：None）

**async_checkpointer_type（AsyncCheckpointerType）**——指定是在单独的线程中还是进程中进行检查点操作（默认值：AsyncCheckpointerType.THREAD）。

**async_stager（AsyncStager）**——提供数据预处理功能的实现类。如果 `storage_writer` 已实现了 `AsyncStager` 接口，且用户指定了 `async_stager`，则将使用该实现类来进行数据预处理。

**no_dist（bool）**——若设置为 True，该函数将假定用户意图是在单个节点/进程中保存检查点。（默认值：False）

**use_collectives（bool）**——若设置为 False，将在不进行节点间协调的情况下保存检查点。（默认值：True）此配置仍处于实验阶段，使用时需谨慎，因为它会改变保存后检查点的格式，且可能存在向后兼容性问题。

一个用于存储 `save` 操作所生成元数据对象的 Future 对象。

此方法已过时，建议改用 `save` 函数。

以 SPMD 模式将检查点加载到分布式 `state_dict` 中。

每个节点提供给该接口的 `state_dict` 必须包含相同的键名。如果键名不一致，可能会导致程序挂起或出现错误。如有疑问，可使用 `utils._assert_same_keys` 函数进行验证（但该操作可能会产生通信开销）。

每个节点都会尽可能仅读取完成目标 `state_dict` 构建所需的最少数据量。在加载 `ShardedTensor` 或 `DTensor` 类型的对象时，每个节点仅会读取自己负责的那部分数据片段。

对于所有同时拥有 `state_dict` 和 `load_state_dict` 方法的“带状态对象”，该函数在尝试进行序列化之前会先调用 `state_dict` 方法，而在序列化完成后则调用 `load_state_dict` 方法。对于那些没有上述方法的“非带状态对象”，函数会直接对其进行序列化，然后将序列化后的对象替换到 `state_dict` 中。

在调用此函数之前，`state_dict` 中的所有张量都必须在目标设备上完成内存分配。

所有非张量类型的数据则通过 `torch.load()` 函数进行加载，然后直接在 `state_dict` 中进行修改。

用户必须在根模块上调用 `load_state_dict` 方法，以确保状态加载和非张量数据的处理能够正确传递。

**state_dict（Dict[str, Any]）**——用于将检查点加载到的 `state_dict` 对象。

**checkpoint_id（Union[str, os.PathLike, None]）**——该检查点实例的标识符。其具体含义取决于存储方式：它可以是文件夹或文件的路径；如果是键值存储系统，则可以是一个键值。（默认值：None）

**storage_reader（Optional[StorageReader]）**——用于执行读取操作的 `StorageReader` 实例。如果未指定此参数，DCP 会根据 `checkpoint_id` 自动推断出对应的读取器；若 `checkpoint_id` 也为 None，则会引发异常。（默认值：None）

**planner（Optional[LoadPlanner]）**——`LoadPlanner` 实例。如果未指定此参数，将使用默认的规划器。（默认值：None）

**process_group（Optional[ProcessGroup]）**——用于实现节点间同步的 `ProcessGroup` 对象。（默认值：None）

**no_dist（bool）**——若设置为 True，该函数将假定用户意图是在不进行节点间同步的情况下加载检查点。（默认值：False）`load_state_dict`函数会利用collectives机制来协调各节点间的数据读取操作。对于基于NCCL的进程组，必须在通信开始之前将对象的内部张量表示形式复制到GPU设备上。此时所使用的设备可通过`torch.cuda.current_device()`获取，而确保通过`torch.cuda.set_device()`为每个节点分配独立的GPU则是用户的责任。

该函数已被弃用，请改用`load`函数。

以下模块也可用于进一步自定义用于异步检查点保存的预处理机制（`torch.distributed.checkpoint.async_save`）：

该协议旨在为`dcp.async_save`提供自定义与扩展功能，允许用户在并行执行常规的`dcp.save`流程之前，自定义数据的预处理方式。具体的操作顺序（在`torch.distributed.state_dict_saver.async_save`中有明确定义）如下：

此调用会赋予`AsyncStager`机会对状态字典进行“预处理”。在此上下文中，预处理的目的是生成一个“适合训练使用的”状态字典版本，即确保在预处理完成后，对模块数据的任何修改都不会反映在该函数返回的状态字典中。例如，在默认情况下，会在CPU内存中创建整个状态字典的副本并返回，这样用户就可以继续训练，而无需担心正在被序列化的数据发生变动。

用于将状态字典序列化并写入存储介质。

在`dcp.async_save`返回之前，序列化线程就会启动。如果将该参数设置为`False`，则意味着用户已定义了自定义的同步点，旨在进一步优化训练循环中的保存延迟（例如通过让预处理与前向/反向传播操作重叠），此时用户有责任在适当时机调用`AsyncStager.synchronize_staging`。

清理预处理器所使用的所有资源。

在完成预处理后是否进行同步。

返回一个“已预处理”的状态字典副本。该副本的要求是，其中不应包含预处理调用完成后发生的任何更新内容。

类型为`Union[Future[dict[str, Union[~StatefulT, Any]]], dict[str, Union[~StatefulT, Any]]]`

如果预处理是异步进行的，应调用此方法以确保预处理已完成，且可以安全地开始修改原始状态字典。

`DefaultStager`提供了一个功能完备的预处理实现，它结合了多种优化技术，可高效地准备检查点数据。

预处理流程如下：1. 提交状态字典进行预处理（同步或异步）；2. 将张量从GPU复制到经过优化的CPU存储空间中；3. 如果使用了非阻塞复制方式，则会对CUDA操作进行同步；4. 返回已预处理的状态字典，或通过`Future`对象提供访问。

# 同步预处理
```python
stager = DefaultStager(StagingOptions(use_async_staging=False))
staged_dict = stager.stage(state_dict)
stager.close()
```

# 异步预处理
```python
stager = DefaultStager(StagingOptions(use_async_staging=True))
future = stager.stage(state_dict)  # … 执行其他操作 …
staged_dict = future.result()
stager.close()
```

# 推荐的上下文管理器模式
```python
stager = DefaultStager(config)
with stager:
    result = stager.stage(state_dict)
```

当模型计算可以与预处理操作重叠时，异步预处理能带来最佳性能。

固定内存可提升CPU与GPU之间的数据传输速度，但会占用更多内存。

共享内存有助于提高检查点处理过程中的进程间通信效率。

非阻塞复制可在数据传输期间减少GPU的空闲时间。

`DefaultStager`并非线程安全函数。每个线程应使用各自的实例，或需实现外部同步机制。

清理`DefaultStager`所使用的所有资源。它会关闭用于异步预处理操作的`ThreadPoolExecutor`，并清除`StateDictStager`内部缓存的存储数据。当不再需要该预处理器时，应调用此方法以避免资源泄漏，尤其是在长时间运行的应用程序中。调用`close()`之后，不得再使用该预处理器进行进一步的预处理操作。

```python
stager = DefaultStager(StagingOptions(use_async_staging=True))
future = stager.stage(state_dict)
result = future.result()
stager.close()  # 清理所有资源
```

此函数负责对状态字典进行预处理。有关预处理的更多详细信息，请参阅类文档。如果`use_async_staging`为`True`，它将返回一个`Future`对象，待预处理完成后该对象才会被完成。如果`use_async_staging`为`False`，则直接返回已完全预处理的状态字典。

参数：`state_dict`（类型为`STATE_DICT_TYPE`）—— 需要预处理的状态字典。

返回值类型为`Union[dict[str, Union[~StatefulT, Any]], Future[dict[str, Union[~StatefulT, Any]]]]`

当`use_async_staging`为`True`时，此方法会一直等待预处理完成。如果为`False`，则此方法不执行任何操作。

用于配置检查点预处理行为的选项。

- `use_pinned_memory`（布尔值）—— 启用固定内存分配，以加快CPU与GPU之间的数据传输速度。需要CUDA支持。默认值为`True`。
- `use_shared_memory`（布尔值）—— 在多进程场景下启用共享内存。当多个进程需要访问相同的预处理数据时非常有用。默认值为`True`。
- `use_async_staging`（布尔值）—— 使用后台线程池启用异步预处理，允许计算操作与预处理操作并行进行。需要CUDA支持。默认值为`True`。
- `use_non_blocking_copy`（布尔值）—— 使用带流同步的非阻塞设备内存复制方式，通过在GPU传输期间让CPU继续工作来提升性能。默认值为`True`。

如果未安装CUDA，依赖CUDA的功能将会抛出异常。

这是一种`AsyncStager`的实现方式，它会在CPU内存中对状态字典进行预处理，并在复制完成前保持阻塞状态。该实现还提供了使用固定内存来优化预处理延迟的选项。

注意：在这种情况下，`synchronize_staging`方法不执行任何操作。

在CPU上返回状态字典的副本。

类型为`dict[str, Union[~StatefulT, Any]]`

由于预处理是阻塞式的，因此这是一个无实际作用的函数。

除了上述接口之外，如下所述的“有状态对象”还提供了在保存/加载过程中的额外自定义功能。

用于可被检查点保存和恢复的对象的协议。

从提供的状态字典中恢复对象的状态。

参数：`state_dict`（类型为`dict[str, Any]》—— 需要从中恢复状态的字典。

对象应将其状态字典表示形式以字典的形式返回。该函数的输出会被序列化为检查点，随后在`load_state_dict()`函数中被恢复。

由于恢复检查点属于就地操作，因此`torch.distributed.checkpoint.load`函数也会调用此函数。

对象的状态字典

此示例展示了如何使用PyTorch分布式检查点功能来保存FSDP模型。

以下类型定义了检查点处理过程中使用的IO接口：

`load_state_dict`函数用于从存储介质中读取数据的接口。

在分布式检查点系统中，一个`StorageReader`实例同时充当协调节点和从属节点的角色。在初始化阶段，每个实例都会被指定其角色。

子类应预期`load_state_dict`会按以下顺序调用相应方法：

- （所有节点）如果用户提供了有效的`checkpoint_id`，则设置该值。
- （所有节点）调用`read_metadata()`。
- （所有节点）调用`set_up_storage_reader()`。
- （所有节点）调用`prepare_local_plan()`。
- （协调节点）调用`prepare_global_plan()`。
- （所有节点）调用`read_data()`。

用于对存储加载进行集中规划。

此方法仅在协调节点实例上被调用。

虽然该方法可能生成完全不同的计划，但更推荐的做法是将与存储相关的具体数据存储在`LoadPlan::storage_data`中。

参数：`plans`（类型为`list[torch.distributed.checkpoint.planner.LoadPlan]`）—— 一个包含多个`LoadPlan`实例的列表，每个节点对应一个实例。

参数：`plans`—— 存储全局规划完成后经过转换的`LoadPlan`列表。

类型为`list[torch.distributed.checkpoint.planner.LoadPlan]`

用于执行针对特定存储的本地规划。

虽然该方法可能生成完全不同的计划，但推荐的做法仍是将与存储相关的具体数据存储在`LoadPlan::storage_data`中。

参数：`plan`（类型为`LoadPlan`）—— 当前正在使用的`LoadPlan`中的本地计划。

参数：`plan`—— 存储本地规划完成后经过转换的`LoadPlan`。

通过规划器从计划中读取所有数据项以完成数据解析。

子类应调用`LoadPlanner::load_bytes`方法，将`BytesIO`对象反序列化到合适的位置。

子类应调用`LoadPlanner::resolve_tensor`方法，以便获取需要用于加载数据的张量。

正确安排任何必要的跨设备数据复制操作是`StorageLayer`的责任。

参数：`plan`（类型为`LoadPlan`）—— 需要执行的本地计划。

参数：`planner`（类型为`LoadPlanner`）—— 用于解析数据项的规划器对象。

一个在未来所有读取操作完成后才会被完成的`Future`对象。

用于读取检查点元数据。

与正在被加载的检查点相关的元数据对象。

该调用表示即将开始读取全新的检查点。如果用户为此次检查点读取指定了`checkpoint_id`，则该参数也会出现。`checkpoint_id`的含义取决于存储方式：它可以是文件夹/文件的路径，也可以是键值存储系统中的键。

参数：`checkpoint_id`（类型为`Union[str, os.PathLike, None]`）—— 该检查点实例的标识符。其含义取决于存储方式：可以是文件夹或文件的路径，如果是键值存储，则可以是键。（默认值为`None`）

用于初始化该实例。

参数：`metadata`（类型为`Metadata`）—— 需要使用的元数据架构。

参数：`is_coordinator`（布尔值）—— 该实例是否负责协调检查点操作。

用于检查给定的`checkpoint_id`是否被存储系统支持。这有助于实现自动存储选择功能。

`save_state_dict`函数用于向存储介质写入数据的接口。

在分布式检查点系统中，一个`StorageWriter`实例同时充当协调节点和从属节点的角色。在初始化阶段，每个实例都会被指定其角色。

子类应预期`load_state_dict`会按以下顺序调用相应方法：

- （所有节点）如果用户提供了有效的`checkpoint_id`，则设置该值。
- （所有节点）调用`set_up_storage_writer()`。
- （所有节点）调用`prepare_local_plan()`。
- （协调节点）调用`prepare_global_plan()`。
- （所有节点）调用`write_data()`。
- （协调节点）调用`finish()`。

用于写入元数据，并将当前检查点标记为已成功保存。

用于序列化元数据的实际格式/架构属于实现细节。唯一的要求是，这些元数据必须能够被还原为相同的对象结构。

参数：`metadata`（类型为`Metadata`）—— 新检查点的元数据。

参数：`results`（类型为`list[list[torch.distributed.checkpoint.storage.WriteResult]]`）—— 包含所有节点的`WriteResults`对象的列表。

用于对存储进行集中规划。

此方法仅在协调节点实例上被调用。

虽然该方法可能生成完全不同的计划，但更推荐的做法是将与存储相关的具体数据存储在`SavePlan::storage_data`中。plans（list[torch.distributed.checkpoint.planner.SavePlan]）——一个SavePlan实例的列表，每个节点对应一个实例。

经过存储层全局规划后的转换后SavePlan列表

list[torch.distributed.checkpoint.planner.SavePlan]

执行针对特定存储方式的本地规划。虽然此方法可能会生成完全不同的规划方案，但推荐的做法是将与存储相关的额外数据存储在SavePlan::storage_data中。

plan（SavePlan）——当前正在使用的SavePlanner生成的本地规划方案。

经过存储层本地规划后的转换后SavePlan

该调用表示即将执行全新的检查点写入操作。如果用户为此次写入指定了checkpoint_id，则该参数也会出现。checkpoint_id的具体含义取决于所使用的存储方式：它可以是文件夹或文件的路径，也可以是键值存储系统中的键。（默认值为None）

用于初始化该实例。

is_coordinator（bool）——该实例是否负责协调检查点的生成。

用于返回与存储相关的元数据。这些元数据可用于在检查点中存储对实现请求级可观测性有帮助的附加信息。在执行保存操作时，这些StorageMeta信息会被传递给SavePlanner。默认返回值为None。

示例：

```python
from torch.distributed.checkpoint.storage import StorageMeta

class CustomStorageBackend:
    def get_storage_metadata(self):
        # Return storage-specific metadata that will be stored with the checkpoint
        return StorageMeta()
```

该示例展示了存储后端如何返回`StorageMeta`，以便为检查点附加额外的元数据。

可选[StorageMeta]

用于判断给定的checkpoint_id是否被该存储系统支持。这有助于实现自动存储选择功能。

通过规划器处理计划中的所有项，从而解析出相应数据。

子类应针对计划中的每个项调用SavePlanner::resolve_data方法，以便获取可用于写入的底层对象。

由于该方法可能会占用内存，子类应采用延迟调用的方式。对于张量而言，需注意以下情况：

它们可能位于任意设备上，甚至可能与WriteItem::tensor_data中指定的设备不同；

它们可能是视图结构，且不一定连续存储。此时只需保存其投影数据即可。

plan（SavePlan）——待执行的保存计划。

planner（SavePlanner）——用于将各项解析为数据的规划器对象。

一个未来值对象，最终会返回一个WriteResult列表

Future[list[torch.distributed.checkpoint.storage.WriteResult]]

以下类型定义了在检查点处理过程中所使用的规划器接口：

定义了load_state_dict用于规划加载过程的协议的一种抽象类。

LoadPlanner是具有状态的对象，可用于自定义整个加载过程。

LoadPlanner充当state_dict的访问代理，因此对其进行的任何操作都会在整个流程中可见。

在load_state_dict执行期间，规划器子类可以预期会出现以下调用顺序：

标记开始加载检查点。

处理state_dict并生成一个LoadPlan，该计划将被发送以进行全局规划。

收集所有节点上的LoadPlan，并做出全局决策。

对于state_dict中的每个非张量值，此操作会被调用一次。

而对于state_dict中的每个张量值，则会成对调用此操作。

建议用户直接扩展DefaultLoadPlanner而非直接使用该接口，因为大多数修改都可以通过修改单个方法来实现。

常见的扩展方式有两种：

重写state_dict。这是扩展加载过程的最简单方式，因为无需深入了解LoadPlan的工作原理。由于加载是在原位置进行的，因此我们需要保留对原始state_dict的引用，从而实现原位加载。

修改resolve_tensor和commit_tensor方法，以便在加载时对数据进行转换。

在StorageReader完成将数据加载到张量中后调用此方法。

此处传入的张量与调用resolve_tensor时返回的张量相同。仅当该LoadPlanner需要在将张量复制回state_dict之前对其进行后处理时，才需要此方法。

张量的内容将遵循其所在设备的同步规则。

计算全局加载计划，并为每个节点返回相应的计划。

注意：此操作仅在协调节点上执行

list[torch.distributed.checkpoint.planner.LoadPlan]

根据state_dict以及set_up_planner提供的元数据来创建一个LoadPlan。

注意：此操作在每个节点上都会执行。

接收来自协调节点的计划，并返回最终的LoadPlan。

加载由read_item和value所描述的项。

该方法应直接对底层state_dict进行原位修改。

value的内容由用于生成正在被加载的检查点的SavePlanner决定。

返回一个BytesIO对象，供StorageReader用来加载read_item。

该BytesIO对象应与底层state_dict中的对应对象别名关联，因为StorageReader会替换其内容。

返回由read_item描述的张量，供StorageReader用来加载read_item。

该张量也应与底层state_dict中的对应张量别名关联，因为StorageReader会替换其内容。如果因某种原因无法实现别名关联，规划器可以使用commit_tensor方法将数据复制回state_dict中。

初始化此实例，以便将数据加载到state_dict中。

注意：此操作在每个节点上都会执行。

定义了save_state_dict用于规划保存过程的协议的一种抽象类。

SavePlanners是具有状态的对象，可用于自定义整个保存过程。

SavePlanner充当state_dict的访问代理，因此对其进行的任何操作都会在整个流程中可见。

在save_state_dict执行期间，规划器子类可以预期会出现以下调用顺序：

标记开始保存检查点。

处理state_dict并生成一个SavePlan，该计划将被发送以进行全局规划。

收集所有节点上的SavePlan，并做出全局决策。

这为每个节点提供了根据全局规划结果进行调整的机会。

在state_dict中查找对应值，以便存储层进行写入操作。

建议用户直接扩展DefaultSavePlanner而非直接使用该接口，因为大多数修改都可以通过修改单个方法来实现。

常见的扩展方式有三种：

重写state_dict。这是扩展保存过程的最简单方式，因为无需深入了解SavePlan的工作原理。

同时修改本地计划和查找逻辑。当需要精细控制数据保存方式时，此方法十分有用。

利用全局规划步骤来做出各个节点无法单独做出的全局性决策。

此外，某些规划器需要在检查点中保存额外的元数据，此时可通过让每个节点在本地计划中提交相应的数据项，再由全局规划器将这些数据项汇总起来实现：

计算全局检查点计划，并为每个节点返回相应的本地计划。

此操作仅在协调节点上执行。

tuple[list[torch.distributed.checkpoint.planner.SavePlan], torch.distributed.checkpoint.metadata.Metadata]

为当前节点计算保存计划。

该计划将被汇总后传递给create_global_plan方法。规划器特定的数据可通过SavePlan::planner_data传递。

此操作在所有节点上都会执行。

合并由create_local_plan生成的计划与create_global_plan的计算结果。

此操作在所有节点上都会执行。

从state_dict中转换并准备write_item以便存储，同时确保操作的幂等性和线程安全性。

在存储层使用该数据之前，先在state_dict中查找与write_item关联的对象，并对其应用任何必要的转换（如序列化处理）。

在最终SavePlan中的每个WriteItem对应的情况下，此方法会在每个节点上被多次调用，至少一次。

该方法应具备幂等性和线程安全性。StorageWriter的实现可以根据需要频繁调用它。

任何会占用内存的转换操作都应在该方法被调用时以延迟方式执行，从而降低检查点处理过程中所需的内存峰值。

当返回张量时，它们可以位于任意设备或采用任意格式，甚至可以是视图结构。如何保存这些数据则是存储层的职责。

Union[Tensor, BytesIO]

初始化此规划器，以便保存state_dict。

实现类应保存这些值，因为它们在后续的保存过程中不会再次提供。

此操作在所有节点上都会执行。

一个数据类，用于存储关于需要写入存储的内容的信息。

用于计算底层张量的存储大小；如果并非张量写入操作，则返回None。

可选[int]：如果存在底层张量，则为其存储大小，单位为字节。

我们提供了基于文件系统的存储层：

返回用于加载检查点的checkpoint_id。

一种使用文件I/O实现的StorageWriter基础实现。

该实现基于以下假设和简化处理：

检查点路径是一个空目录或不存在的目录。

文件创建操作是原子的。

如果启用了节点协调功能，检查点由每个写入请求对应的一个文件，以及一个包含序列化元数据的全局.metadata文件组成；如果未启用节点协调功能，则每个节点会拥有一个包含序列化元数据的本地__{rank}.metadata文件。

重写AsyncStager.stage方法

dict[str, Union[~StatefulT, Any]]

我们还提供了其他类型的存储层，包括那些可以与HuggingFace safetensors交互的存储层：

.. autoclass:: torch.distributed.checkpoint.HuggingFaceStorageReader :members:

.. autoclass:: torch.distributed.checkpoint.HuggingFaceStorageWriter :members:

.. autoclass:: torch.distributed.checkpoint.QuantizedHuggingFaceStorageReader :members:

我们提供了LoadPlanner和SavePlanner的默认实现，这些实现能够处理torch.distributed中的各种结构，如FSDP、DDP、ShardedTensor和DistributedTensor。

通过扩展规划器接口，使得默认规划器更易于扩展。

通过扩展规划器接口，使得默认规划器更易于扩展。

在LoadPlanner基础上添加了多种功能的DefaultLoadPlanner。

具体而言，它新增了以下功能：

flatten_state_dict：用于处理包含嵌套字典的state_dict。

flatten_sharded_tensors：针对处于2D并行模式下的FSDP场景。

allow_partial_load：如果设置为False，则当state_dict中存在某个键，但检查点中不存在该键时，会引发运行时错误。

通过扩展规划器接口，使得默认规划器更易于扩展。

通过扩展规划器接口，使得默认规划器更易于扩展。

由于历史设计原因，即使原始的非并行模型完全相同，FSDP和DDP的state_dict也可能拥有不同的键或完全限定的名称（例如layer1.weight）。此外，FSDP还支持多种类型的模型状态字典，如完整状态字典和分片状态字典。另外，优化器状态字典则使用参数ID而非完全限定的名称来标识参数，这在使用并行机制（如流水线并行）时可能会引发问题。

为了解决这些难题，我们提供了一系列API，帮助用户更轻松地管理state_dicts。get_model_state_dict()返回的模型状态字典的键与未并行化模型状态字典的键保持一致。同样，get_optimizer_state_dict()提供的优化器状态字典的键在所有并行模式下都保持统一。为确保这种一致性，get_optimizer_state_dict()会将参数ID转换为与未并行化模型状态字典中完全相同的完全限定名称。

需要注意的是，这些API返回的结果可以直接用于torch.distributed.checkpoint.save()和torch.distributed.checkpoint.load()方法，无需进行任何额外的转换。

set_model_state_dict()和set_optimizer_state_dict()用于加载由其对应的getter API生成的模型和优化器状态字典。

需要注意的是，set_optimizer_state_dict()只能在调用优化器的backward()方法之前或step()方法之后调用。

请注意，此功能仍处于实验阶段，未来的API接口格式可能会发生变化。

返回模型状态字典和优化器状态字典。`get_state_dict` 能够处理通过 PyTorch FSDP/fully_shard、DDP/replicate、tensor_parallel/parallelize_module 以及这些并行化技术任意组合实现的并行模块。其主要功能包括：1）返回可用于在不同数量训练器或不同并行架构下重新分片处理的模型与优化器状态字典；2）隐藏与特定并行架构相关的状态字典接口，用户无需直接调用这些接口；3）对生成的状态字典进行完整性校验。

最终状态字典的键为规范化的完全限定名（FQN）。规范化 FQN 指的是基于参数在 `nn.Module` 层级结构中位置确定的名称。更具体而言，当模块未被任何并行技术拆分时，`module.named_parameters()` 或 `module.named_buffers()` 返回的名称即为该参数的规范化 FQN。由于优化器内部使用参数 ID 来标识参数，因此在调用相关接口时，需将参数 ID 转换为规范化 FQN。

`get_state_dict` 也能处理未进行并行处理的模块。在这种情况下，它仅执行一项功能——将优化器的参数 ID 转换为规范化 FQN。

**参数说明：**
- `model (nn.Module)` – 所需模型的 `nn.Module` 对象。
- `optimizers (Union[None, Optimizer, Iterable[Optimizer]])` – 用于优化模型的优化器对象。
- `submodules (deprecated)` – 可选参数，类型为 `set[nn.Module]`：仅返回属于子模块的模型参数。
- `options (StateDictOptions)` – 用于控制模型状态字典与优化器状态字典返回方式的选项，详情请参见 `StateDictOptions`。

**返回值：**
包含模型状态字典与优化器状态字典的元组，类型为 `Tuple[Dict[str, ValueType], OptimizerStateType]`。

**获取模型的状态字典。**
详细用法请参阅 `get_state_dict` 的文档。

**参数说明：**
- `model (nn.Module)` – 所需模型的 `nn.Module` 对象。
- `submodules (deprecated)` – 可选参数，类型为 `set[nn.Module]`：仅返回属于子模块的模型参数。
- `options (StateDictOptions)` – 用于控制模型状态字典与优化器状态字典返回方式的选项，详情请参见 `StateDictOptions`。

**返回值：**
模型的状态字典。

**返回优化器的合并状态字典。**
详细用法请参阅 `get_state_dict` 的文档。

**参数说明：**
- `model (nn.Module)` – 所需模型的 `nn.Module` 对象。
- `optimizers (Union[None, Optimizer, Iterable[Optimizer]])` – 用于优化模型的优化器对象。
- `submodules (deprecated)` – 可选参数，类型为 `set[nn.Module]`：仅返回属于子模块的模型参数。
- `options (StateDictOptions)` – 用于控制模型状态字典与优化器状态字典返回方式的选项，详情请参见 `StateDictOptions`。

**返回值：**
优化器的状态字典。

**加载模型的状态字典与优化器的状态字典。**
该函数是 `get_state_dict` 的对应操作，用于将状态字典重新设置到模型与优化器中。传入的 `model_state_dict` 与 `optim_state_dict` 不一定由 `get_state_dict` 生成，但必须满足以下要求：1）所有 FQN 均为 `get_state_dict` 中定义的规范化 FQN；2）若张量已被分片，则必须是 `ShardedTensor` 或 `DTensor` 类型；3）优化器状态字典中不得包含参数 ID，键必须为规范化 FQN。

**注意事项：**
必须对优化器调用 `step()` 方法，否则优化器状态将无法正确初始化。

**参数说明：**
- `model (nn.Module)` – 所需模型的 `nn.Module` 对象。
- `optimizers (Union[Optimizer, Iterable[Optimizer]])` – 用于优化模型的优化器对象。
- `model_state_dict (Dict[str, ValueType])` – （类型为 `Union[Dict[nn.Module, Dict[str, ValueType]], Dict[str, ValueType]]`）：需加载的模型状态字典。若该字典的键为 `nn.Module` 对象，则表示该键对应模型的子模块，其值应为该子模块的状态字典。加载状态字典时，子模块的前缀会被附加到状态字典键中。
- `optim_state_dict (OptimizerStateType)` – 优化器状态字典的类型。
- `options (StateDictOptions)` – 用于控制模型状态字典与优化器状态字典加载方式的选项，详情请参见 `StateDictOptions`。

**返回值：**
- `missing_keys`：包含模型状态字典中缺失键名的字符串列表。
- `unexpected_keys`：包含模型状态字典中意外出现的键名的字符串列表。

**参数说明：**
包含 `missing_keys` 与 `unexpected_keys` 字段的命名元组。

**加载模型的状态字典。**
该函数是 `get_model_state_dict` 的对应操作，用于将状态字典设置到模型中。详细用法请参阅 `set_state_dict` 的文档。

**参数说明：**
- `model (nn.Module)` – 所需模型的 `nn.Module` 对象。
- `model_state_dict (Dict[str, ValueType])` – （类型为 `Dict[str, ValueType]`）：需加载的模型状态字典。若该字典的键为 `nn.Module` 对象，则表示该键对应模型的子模块，其值应为该子模块的状态字典。加载状态字典时，子模块的前缀会被附加到状态字典键中。
- `options (StateDictOptions)` – 用于控制模型状态字典与优化器状态字典加载方式的选项，详情请参见 `StateDictOptions`。

**返回值：**
- `missing_keys`：包含模型状态字典中缺失键名的字符串列表。
- `unexpected_keys`：包含模型状态字典中意外出现的键名的字符串列表。

**参数说明：**
包含 `missing_keys` 与 `unexpected_keys` 字段的命名元组。

**加载优化器的状态字典。**
该函数是 `get_optimizer_state_dict` 的对应操作，用于将状态字典设置到优化器中。详细用法请参阅 `set_state_dict` 的文档。

**注意事项：**
必须对优化器调用 `step()` 方法，否则优化器状态将无法正确初始化。

**参数说明：**
- `model (nn.Module)` – 所需模型的 `nn.Module` 对象。
- `optimizers (Union[Optimizer, Iterable[Optimizer]])` – 用于优化模型的优化器对象。
- `optim_state_dict (OptimizerStateType)` – 优化器状态字典的类型。
- `options (StateDictOptions)` – 用于控制模型状态字典与优化器状态字典加载方式的选项，详情请参见 `StateDictOptions`。

**说明：**
此数据类用于指定 `get_state_dict`/`set_state_dict` 的具体行为。

- `full_state_dict`：若设置为 `True`，则返回的状态字典中的所有张量都会被聚合在一起，状态字典中不会包含 `ShardedTensor` 或 `DTensor` 类型。
- `cpu_offload`：将所有张量卸载到 CPU 上。为避免内存溢出，若同时设置了 `full_state_dict`，则仅 rank 0 会收到完整状态字典，其余 rank 将收到空状态字典。
- `ignore_frozen_params`：若该值为 `True`，返回的状态字典中将不包含任何冻结参数（即 `requires_grad` 为 `False`）。默认值为 `False`。
- `keep_submodule_prefixes (deprecated)`：当 `submodules` 参数非空时，该选项用于指定是否保留状态字典键中的子模块前缀。例如，若子模块名为 `module.pretrain`，且该参数的完整 FQN 为 `pretrain.layer1.weight`，则当此选项为 `True` 时，返回状态字典中该参数的键将为 `pretrain.layer1.weight`；若为 `False`，键则为 `layer1.weight`。需注意，若 `keep_submodule_prefixes` 设为 `False`，可能会出现 FQN 冲突，因此 `submodules` 参数中应仅包含一个子模块。
- `strict`：当使用 `set_state_dict` 调用 `model.load_state_dict()` 时的严格模式选项。

**完整状态字典模式：**
该模式下，状态字典/优化器状态字典中的张量会逐一广播到其他 rank，其他 rank 接收后会根据自身模型与优化器中的分片结构进行相应处理。使用此选项时必须将 `full_state_dict` 设置为 `True`。目前该选项仅支持 `DTensor`，不支持旧版的 `ShardedTensor`。

对于习惯使用 torch.save 格式保存和加载模型的用户，还提供了以下离线工具函数，用于实现不同格式之间的转换。

给定包含 DCP 检查点的目录，此函数可将该检查点转换为 Torch save 文件。
- `dcp_checkpoint_dir (Union[str, PathLike])` – 包含 DCP 检查点的目录。
- `torch_save_path (Union[str, PathLike])` – 用于存储转换后 Torch save 文件的文件名。

为避免内存溢出，建议仅在单个 rank 上运行此函数。

给定 Torch save 文件的位置，将其转换为 DCP 检查点。
- `torch_save_path (Union[str, PathLike])` – Torch save 文件的文件名。
- `dcp_checkpoint_dir (Union[str, PathLike])` – 用于存储 DCP 检查点的目录。

为避免内存溢出，建议仅在单个 rank 上运行此函数。

此外，还可以利用以下类从 Torch save 格式在线加载模型并重新分片处理。

- `StorageReader`：用于读取 Torch Save 文件。该读取器会在协调节点上完整读取整个检查点，之后再将每个张量广播并分片到所有节点。**注意：** 该类设计为与 `DynamicMetaLoadPlanner` 搭配使用。
  - 当前实现仅支持加载 Tensor 类型数据。

- `StorageReader` 方法的实现：类型为 `list[torch.distributed.checkpoint.planner.LoadPlan]`。

- `StorageReader` 方法的实现：在协调节点上读取 Torch save 数据，之后进行广播操作——这会带来通信开销，但无需在每个节点上都加载整个检查点，从而有助于避免内存溢出问题。

- 扩展自默认的 `StorageReader`，用于构建元数据文件。
  - `StorageReader` 方法的实现：有多个实现版本。

- 扩展自默认的 `DefaultLoadPlanner`，根据传入的状态字典创建新的元数据对象，从而无需从磁盘读取元数据。这对于那些没有独立元数据文件的格式（如 Torch Save 文件）非常有用。**注意：** 该类设计为与 `BroadcastingTorchSaveReader` 搭配使用。
  - 当前实现仅支持加载 Tensor 类型数据。

- 规划器的配置，通过根据状态字典创建元数据对象来扩展默认行为。

为提升生产环境中的可观测性，还提供了以下实验性接口：

---

## torch.distributed.tensor#

**网址：** https://pytorch.org/docs/stable/distributed.tensor.html

**内容概要：**
- torch.distributed.tensor#
- PyTorch DTensor（分布式张量）#
  - DTensor 类的 API#
  - 作为分布式通信机制的 DeviceMesh#
  - DTensor 的放置类型#
- 创建 DTensor 的多种方式#
  - 从普通的 torch.Tensor 创建 DTensor#
  - DTensor 工厂函数#
  - 随机操作#
- 调试功能#

**创建时间：** 2025年6月13日 | **最后更新时间：** 2025年8月23日

目前 `torch.distributed.tensor` 处于测试阶段，仍在开发中。我们已为文档中列出的大部分 API 确保向后兼容性，但如有必要，仍可能对部分 API 进行调整。PyTorch DTensor提供了简单且灵活的张量分片操作接口，能够以透明方式处理分布式逻辑，包括跨设备/主机的分片存储、运算符计算以及集合通信。它可用于构建各种并行化解决方案，并在实现多维分片时支持分片后的state_dict表示形式。

以下是基于DTensor构建的PyTorch原生并行化解决方案示例：

DTensor遵循SPMD（单程序、多数据）编程模型，让用户能够像编写单设备程序一样编写分布式程序，同时保持相同的收敛特性。它通过指定DeviceMesh和Placement来定义统一的张量分片布局（DTensor Layout）：

- **DeviceMesh**：使用n维数组表示集群的设备拓扑结构以及通信节点。
- **Placement**：描述逻辑张量在DeviceMesh上的分片布局。DTensor支持三种类型的Placement：Shard、Replicate和Partial。

DTensor是torch.Tensor的子类。这意味着一旦创建了DTensor，就可以像使用torch.Tensor一样对其进行操作，包括像在单设备上一样运行各类PyTorch运算符，从而实现正确的分布式计算。

除了现有的torch.Tensor方法外，DTensor还提供了一组额外的方法，用于与torch.Tensor交互、将DTensor Layout重新分配到新的DTensor中、获取所有设备上的完整张量内容等。

DTensor（分布式张量）是torch.Tensor的子类，为基于多设备环境的torch.Tensor编程提供了类似单设备的抽象接口。它通过DeviceMesh以及以下几类Placement来描述分布式张量的分片布局：

- **Shard**：在DeviceMesh对应维度上，沿张量维度dim对张量进行分片。
- **Replicate**：在DeviceMesh对应维度上的各设备上复制张量。
- **Partial**：在DeviceMesh对应维度上的各设备上对张量执行求和操作。

当调用PyTorch运算符时，DTensor会重写这些运算符，从而在需要时执行分片计算并发起通信。在完成运算符计算的同时，DTensor还会根据运算符本身的语义正确地转换或传递Placement（DTensor Layout），并生成新的DTensor输出结果。

为确保在调用PyTorch运算符时DTensor的分片计算具有数值正确性，DTensor要求运算符的所有张量参数都必须是DTensor类型。

直接使用Tensor子类的构造函数来创建DTensor并非推荐方式（因为这种方式无法正确处理自动求导功能，因此不属于官方API）。有关如何创建DTensor的详细信息，请参阅相关创建指南。

返回一个ChunkStorageMetadata列表，该数据类用于描述当前节点上本地分片/副本的大小及偏移量。对于DTensor而言，每个节点仅包含一个本地分片/副本，因此返回的列表通常只包含一个元素。

此双下划线方法主要用于分布式检查点功能。

表示当前节点上分片大小/偏移量的List[ChunkStorageMetadata]对象。

根据指定的device_mesh和Placement，在每个节点上的本地torch.Tensor基础上创建一个DTensor。

- **local_tensor**（torch.Tensor）：每个节点上的本地torch.Tensor。
- **device_mesh**（DeviceMesh，可选）：用于放置张量的DeviceMesh；如果未指定，则必须在DeviceMesh上下文管理器中调用该函数，默认值为None。
- **placements**（List[Placement]，可选）：描述如何将本地torch.Tensor放置在DeviceMesh上的布局，其元素数量必须与device_mesh.ndim相同。
- **run_check**（bool，可选）：虽然会增加通信开销，但可通过跨节点执行合理性检查，验证每个本地张量的元数据是否正确。如果Placement中包含Replicate类型，则会将设备网格维度第一个节点上的数据广播到其他节点，默认值为False。
- **shape**（torch.Size，可选）：一个整数列表，用于指定基于local_tensor构建的DTensor的大小。如果各节点上local_tensor的形状不同，则必须提供此参数；否则将假设分布式张量在各个节点上均匀分片，从而自动计算形状，默认值为None。
- **stride**（tuple，可选）：一个整数列表，用于指定DTensor的步长。如果未提供，则将假设分布式张量在各个节点上均匀分片，从而自动计算步长，默认值为None。

当设置run_check=False时，用户有责任确保传入的本地张量在各个节点上是正确的（即对于Shard(dim)类型的Placement，张量已正确分片；对于Replicate()类型的Placement，张量已正确复制）。否则，所创建DTensor的行为将无法预测。

由于from_local是可微分的，因此所创建DTensor对象的requires_grad属性将取决于local_tensor是否需要求导。

返回该DTensor的完整张量版本。此操作会执行必要的集合通信操作，从DeviceMesh中的其他节点收集本地张量并将其拼接在一起。实际上，这等价于以下代码的语法简化形式：

dtensor.redistribute(placements=[Replicate()] * mesh.ndim).to_local()

**grad_placements**（List[Placement]，可选）：描述从该函数返回的完整张量的梯度布局未来将采用的形式。full_tensor会将DTensor转换为完整的torch.Tensor，而返回的torch.Tensor在后续代码中可能不会保持与原始复制版相同的布局。此参数可作为用户给自动求导系统的提示，以便在返回张量的梯度布局与原始复制版不一致时进行相应处理。如果未指定，则默认假设完整张量的梯度布局为复制型。

表示该DTensor的完整张量的torch.Tensor对象。

full_tensor是可微分的。

**redistribute**方法会执行必要的集合操作，将当前的DTensor从现有的Placement布局转换为新的布局，或从当前的DeviceMesh转换为新的DeviceMesh。例如，通过为DeviceMesh的每个维度指定Replicate类型的Placement，就可以将分片式的DTensor转换为复制式的DTensor。

当在某个设备网格维度上从当前布局转换为新布局时，该方法会执行以下操作，包括集合通信或本地操作：

- Shard(dim) -> Replicate()：使用all_gather操作。
- Shard(src_dim) -> Shard(dst_dim)：使用all_to_all操作。
- Replicate() -> Shard(dim)：通过本地分块操作（即torch.chunk）实现。
- Partial() -> Replicate()：使用all_reduce操作。
- Partial() -> Shard(dim)：使用reduce_scatter操作。

无论DTensor是在一维还是多维DeviceMesh上创建的，redistribute方法都能自动确定所需的转换步骤。

- **device_mesh**（DeviceMesh，可选）：用于放置DTensor的DeviceMesh；如果未指定，则会使用当前DTensor对应的DeviceMesh，默认值为None。
- **placements**（List[Placement]，可选）：描述如何将DTensor放置在DeviceMesh中的新布局，其元素数量必须与device_mesh.ndim相同。默认情况下，所有网格维度均采用复制型布局。
- **async_op**（bool，可选）：是否以异步方式执行DTensor的重新分配操作，默认值为False。
- **forward_dtype**（torch.dtype，可选）：在向前传播过程中重新分配本地张量之前，可将本地张量的数据类型转换为forward_dtype；生成的DTensor将采用该数据类型，默认值为None。
- **backward_dtype**（torch.dtype，可选）：在向后传播过程中重新分配本地张量之前，可将本地张量的数据类型转换为backward_dtype；生成的DTensor梯度将再转换回当前DTensor的数据类型，默认值为None。

由于redistribute方法是可微分的，因此用户无需担心该操作的反向传播公式问题。

目前redistribute方法仅支持在同一DeviceMesh上重新分配DTensor。如果需要将DTensor重新分配到不同的DeviceMesh上，请提交问题报告。

获取该DTensor在当前节点上的本地张量。对于分片式布局，该方法会返回逻辑张量的一个本地分片视图；对于复制式布局，则返回当前节点上的副本张量。

**grad_placements**（List[Placement]，可选）：描述从该函数返回的张量的梯度布局未来将采用的形式。to_local方法会将DTensor转换为本地张量，而返回的本地张量在后续代码中可能不会保持与原始DTensor相同的布局。此参数可作为用户给自动求导系统的提示，以便在返回张量的梯度布局与原始DTensor不一致时进行相应处理。如果未指定，则默认假设梯度布局与原始DTensor相同，从而以此作为梯度计算的依据。

返回一个torch.Tensor或AsyncCollectiveTensor对象，表示当前节点上的本地张量。如果返回的是AsyncCollectiveTensor对象，说明本地张量尚未准备就绪（即通信尚未完成），此时用户需要调用wait方法等待本地张量准备好。

to_local方法是可微分的，因此返回的本地张量的requires_grad属性将取决于DTensor是否需要求导。

与该DTensor对象关联的DeviceMesh属性。

device_mesh是只读属性，无法被修改。

该DTensor的placements属性用于描述该DTensor在DeviceMesh上的布局。

placements也是只读属性，无法被修改。

DeviceMesh是基于DTensor构建的抽象概念，用于描述集群的设备拓扑结构，并表示多维通信节点（建立在ProcessGroup之上）。如需了解如何创建/使用DeviceMesh的详细信息，请参阅相关文档。

DTensor在每个设备网格维度上支持以下几种Placement类型：

- **Shard(dim)**布局：表示在DeviceMesh对应维度上，沿张量维度dim对DTensor进行分片。此时，DeviceMesh对应维度上的每个节点仅持有全局张量的一部分。Shard(dim)布局遵循torch.chunk(dim)的逻辑，当张量维度在DeviceMesh维度上无法被均匀分割时，DeviceMesh维度上的最后几部分可能为空。所有DTensor API（如distribute_tensor、from_local等）都支持使用Shard布局。

  - **dim**（int）：表示DTensor在其对应的DeviceMesh维度上进行分片的张量维度。

  需要说明的是，当张量维度在某个设备网格维度上的大小无法被均匀分割时，在该维度上进行的张量分片操作目前仍处于实验阶段，未来可能会发生变化。`Replicate()`放置方式表示DTensor在对应的DeviceMesh维度上被复制，其中DeviceMesh维度上的每个节点都保存着全局Tensor的一个副本。所有DTensor API（如distribute_tensor、DTensor.from_local等）均支持这种放置方式。

`Partial(reduce_op)`放置方式则表示在指定的DeviceMesh维度上正在等待求和操作的DTensor，该维度上的每个节点都保存着全局Tensor的局部值。用户可通过reallocate函数将此类Partial DTensor重新分配到指定DeviceMesh维度上的Replicate或Shard(dim)放置方式，这将触发底层必要的通信操作（如allreduce、reduce_scatter）。

`reduce_op`（字符串，可选）——用于对Partial DTensor进行操作以生成Replicated/Sharded DTensor的求和运算类型。仅支持逐元素求和运算，包括：“sum”、“avg”、“product”、“max”、“min”，默认值为“sum”。

`Partial`放置方式可能是由DTensor运算产生的，且仅能被DTensor.from_local API使用。

`Placement`类型的基类，用于描述DTensor如何部署在DeviceMesh上。`Placement`与DeviceMesh共同决定了DTensor的布局结构。它是三种主要DTensor放置方式——Shard、Replicate和Partial的基类。

该类并不建议直接使用，主要用于类型标注目的。

`distribute_tensor()`函数会根据每个节点上的逻辑或“全局”torch.Tensor创建一个DTensor。此方法可用于对叶级torch.Tensor（即模型参数/缓冲区及输入数据）进行分片处理。

`DTensor.from_local()`函数则基于每个节点上的本地torch.Tensor创建DTensor，可用于从非叶级torch.Tensor（即前向/反向传播过程中的中间激活张量）构建DTensor。

DTensor提供了专门的张量生成函数（如empty()、ones()、randn()等），允许通过直接指定DeviceMesh和Placement的方式来创建不同的DTensor。与distribute_tensor()相比，这些函数可以直接在设备上生成分片后的内存，而无需在初始化逻辑张量内存后再进行分片操作。

torch.distributed中的SPMD（单程序多数据）编程模型通过torchrun启动多个进程来执行同一程序，这意味着程序中的模型会首先在不同的进程中被初始化（即模型可能在CPU、元设备上初始化，或者如果有足够内存则直接在GPU上初始化）。

DTensor提供了distribute_tensor() API，可将模型权重或张量分片为多个DTensor，即在每个进程中从“逻辑”张量创建相应的DTensor。这样一来，生成的DTensor就能符合单设备语义，这对于保证数值计算的正确性至关重要。

根据指定的放置方式将叶级torch.Tensor（即nn.Parameter/缓冲区）分配到device_mesh中。device_mesh的节点数与放置方式的元素数量必须一致。需要分配的张量是逻辑或“全局”张量，该API会以DeviceMesh维度中第一个节点上的张量为真实值来源，以此保持单设备语义。如果在自动微分计算过程中想要构建DTensor，请改用DTensor.from_local()。

`tensor`（torch.Tensor）——需分配的torch.Tensor。需要注意的是，如果要在某个维度上对张量进行分片，而该维度的节点数无法被设备数量整除，系统会采用torch.chunk机制对张量进行分片并散布各片段。这种非均匀分片功能目前仍处于实验阶段，可能会发生变化。

`device_mesh`（DeviceMesh，可选）——用于分配张量的DeviceMesh对象；如果未指定，则必须在DeviceMesh上下文管理器中调用该函数，默认值为None。

`placements`（List[Placement]，可选）——描述如何将张量部署在DeviceMesh上的放置方式列表，其元素数量必须与device_mesh.ndim相同。如果未指定，默认会从device_mesh中每个维度的第一个节点开始复制张量。

`src_data_rank`（整数，可选）——逻辑/全局张量的源数据所在节点编号，distribute_tensor()函数会利用该值将分片/副本散布到其他节点。默认情况下，系统会以每个DeviceMesh维度中的group_rank=0节点作为源数据，以保持单设备语义。如果明确传入None，distribute_tensor()将直接使用本地数据，而不会尝试通过散布操作来维持单设备语义。默认值为0。

一个DTensor或XLAShardedTensor对象。

当使用xla device_type初始化DeviceMesh时，distribute_tensor()会返回XLAShardedTensor。更多详情请参阅相关问题记录。XLA集成功能目前仍处于实验阶段，可能会发生变化。

除了distribute_tensor()之外，DTensor还提供了distribute_module() API，便于在nn.Module层级进行更简单的分片处理。

该函数提供了三个函数来控制模块的参数/输入/输出：

1. 通过指定partition_fn，在运行时之前对模块进行分片处理（即允许用户根据指定的partition_fn将模块参数转换为DTensor参数）。
2. 通过指定input_fn和output_fn，在运行时控制模块的输入或输出（即将输入转换为DTensor，再将输出转换回torch.Tensor）。

`module`（nn.Module）——需要被分片的用户自定义模块。

`device_mesh`（DeviceMesh）——用于放置该模块的设备网格。

`partition_fn`（Callable）——用于对参数进行分片的函数（即在设备网格上对某些参数进行分片处理）。如果未指定partition_fn，默认会将模块的所有参数在整个网格中复制。

`input_fn`（Callable）——用于指定输入的分片方式，即控制模块输入如何被分片。input_fn会被作为模块的forward_pre_hook（前向钩子）注册。

`output_fn`（Callable）——用于指定输出的分片方式，即控制输出如何被分片，或将其转换回torch.Tensor。output_fn会被作为模块的forward_hook（后向钩子）注册。

一个所有参数/缓冲区均为DTensor的模块。

当使用xla device_type初始化DeviceMesh时，distribute_module()会返回带有PyTorch/XLA SPMD标注参数的nn.Module。更多详情请参阅相关问题记录。XLA集成功能目前仍处于实验阶段，可能会发生变化。

DTensor还提供了专门的张量生成函数，允许用户像使用torch.ones、torch.empty等常规工厂函数一样直接创建DTensor，只需额外指定所创建DTensor的DeviceMesh和Placement信息即可：

返回一个填充有标量值0的DTensor。

`size`（整数序列）——用于定义输出DTensor形状的一组整数。可以是任意数量的参数，也可以是列表或元组等集合形式。例如：zeros(1,2,3..)或zeros([1,2,3..])或zeros((1,2,3..))。

`requires_grad`（布尔值，可选）——是否让自动微分系统记录对返回的DTensor进行的操作。默认值为False。

`dtype`（torch.dtype，可选）——返回的DTensor所需的数据类型。如果未指定，则使用全局默认值（参见torch.set_default_dtype()）。

`layout`（torch.layout，可选）——返回的DTensor所需的布局类型。默认值为torch.strided。

`device_mesh`——DeviceMesh类型，包含各节点的网格信息。

`placements`——一系列Placement类型，包括Shard、Replicate。

每个节点上都有一个DTensor对象。

返回一个填充有标量值1的DTensor，其形状由可变参数size定义。

`size`（整数序列）——用于定义输出DTensor形状的一组整数。可以是任意数量的参数，也可以是列表或元组等集合形式。例如：ones(1,2,3..)或ones([1,2,3..])或ones((1,2,3..))。

`dtype`（torch.dtype，可选）——返回的DTensor所需的数据类型。如果未指定，则使用全局默认值（参见torch.set_default_dtype()）。

`layout`（torch.layout，可选）——返回的DTensor所需的布局类型。默认值为torch.strided。

`requires_grad`（布尔值，可选）——是否让自动微分系统记录对返回的DTensor进行的操作。默认值为False。

`device_mesh`——DeviceMesh类型，包含各节点的网格信息。

`placements`——一系列Placement类型，包括Shard、Replicate。

每个节点上都有一个DTensor对象。

返回一个包含未初始化数据的DTensor，其形状由可变参数size定义。

`size`（整数序列）——用于定义输出DTensor形状的一组整数。可以是任意数量的参数，也可以是列表或元组等集合形式。例如：empty(1,2,3..)或empty([1,2,3..])或empty((1,2,3..))。

`dtype`（torch.dtype，可选）——返回的DTensor所需的数据类型。如果未指定，则使用全局默认值（参见torch.set_default_dtype()）。

`layout`（torch.layout，可选）——返回的DTensor所需的布局类型。默认值为torch.strided。

`requires_grad`（布尔值，可选）——是否让自动微分系统记录对返回的DTensor进行的操作。默认值为False。

`device_mesh`——DeviceMesh类型，包含各节点的网格信息。

`placements`——一系列Placement类型，包括Shard、Replicate。

每个节点上都有一个DTensor对象。

根据device_mesh和placements的指定，返回一个填充有fill_value值的DTensor，其形状由参数size定义。

`size`（整数序列）——用于定义输出DTensor形状的一组整数。可以是任意数量的参数，也可以是列表或元组等集合形式。例如：ones(1,2,3..)或ones([1,2,3..])或ones((1,2,3..))。

`fill_value`（标量值）——用于填充输出张量的值。

`dtype`（torch.dtype，可选）——返回的DTensor所需的数据类型。如果未指定，则使用全局默认值（参见torch.set_default_dtype()）。

`layout`（torch.layout，可选）——返回的DTensor所需的布局类型。默认值为torch.strided。

`requires_grad`（布尔值，可选）——是否让自动微分系统记录对返回的DTensor进行的操作。默认值为False。

`device_mesh`——DeviceMesh类型，包含各节点的网格信息。

`placements`——一系列Placement类型，包括Shard、Replicate。

每个节点上都有一个DTensor对象。

返回一个包含在区间[0, 1)内均匀分布的随机数的DTensor，其形状由可变参数size定义。

`size`（整数序列）——用于定义输出DTensor形状的一组整数。可以是任意数量的参数，也可以是列表或元组等集合形式。例如：ones(1,2,3..)或ones([1,2,3..])或ones((1,2,3..))。

`dtype`（torch.dtype，可选）——返回的DTensor所需的数据类型。如果未指定，则使用全局默认值（参见torch.set_default_dtype()）。layout（torch.layout，可选）——返回的DTensor所需的布局。默认值：torch.strided。

requires_grad（bool，可选）——是否让自动求导系统记录对返回的DTensor执行的操作。默认值：False。

device_mesh——DeviceMesh类型，包含各节点的网格信息。

placements——Placement类型的序列：Shard、Replicate

每个节点上都有一个DTensor对象

该函数会返回一个填充有来自正态分布的随机数的DTensor，其均值為0，方差為1。张量的形状由可变参数size决定。

size（int...）——定义输出DTensor形状的整数序列。可以是任意数量的参数，也可以是列表或元组等集合形式。例如：ones(1,2,3..)或ones([1,2,3..])或ones((1,2,3..))。

dtype（torch.dtype，可选）——返回的DTensor所需的数据类型。默认值：如果未指定，则使用全局默认值（参见torch.set_default_dtype()）。

layout（torch.layout，可选）——返回的DTensor所需的布局。默认值：torch.strided。

requires_grad（bool，可选）——是否让自动求导系统记录对返回的DTensor执行的操作。默认值：False。

device_mesh——DeviceMesh类型，包含各节点的网格信息。

placements——Placement类型的序列：Shard、Replicate

每个节点上都有一个DTensor对象

DTensor提供了分布式随机数生成功能，可确保对分片张量进行的随机操作能生成唯一值，而对复制张量进行的随机操作则能生成相同值。该系统要求所有参与操作的节点（如SPMD节点）在每次执行DTensor随机操作之前都使用相同的生成器状态；只要满足这一条件，每次操作完成后所有节点的状态都会保持一致。在随机操作过程中无需进行通信来同步随机数生成器状态。

那些接受生成器参数的运算符会使用用户指定的生成器（如果提供了的话），否则则使用对应设备的默认生成器。无论使用哪种生成器，都将在DTensor操作之后将其状态向前推进。虽然可以在DTensor操作和非DTensor操作中使用同一个生成器，但若如此，就必须确保非DTensor操作能在所有节点上以相同的方式推进生成器状态。

当将DTensor与流水线并行技术一起使用时，每个流水线阶段的节点应使用不同的种子，而同一流水线阶段内的节点则应使用相同的种子。

DTensor的随机数生成基础设施基于philox算法，支持所有基于philox的后端（如cuda及各类类似cuda的设备），但目前还不支持CPU后端。

在运行程序时，可以通过torch._logging中的TORCH_LOGS环境变量开启更多日志记录功能：

TORCH_LOGS=+dtensor：显示DEBUG级别及以上的日志信息。

TORCH_LOGS=dtensor：显示INFO级别及以上的日志信息。

TORCH_LOGS=-dtensor：显示WARNING级别及以上的日志信息。

为调试使用了DTensor的程序，并更深入地了解底层发生的集合操作，DTensor提供了CommDebugMode功能：

CommDebugMode是一种上下文管理器，可在其作用范围内统计功能性集合操作的数量。它通过TorchDispatchMode来实现这一功能。

目前并非所有的集合操作都受支持。

生成详细的表格，展示模块级别的操作信息及集合操作追踪信息。信息量取决于noise_level参数的值。

打印模块级别的集合操作计数。

打印不属于简单操作的DTensor操作以及模块相关信息。

打印不属于简单操作的普通操作。

打印所有操作。

创建用于生成浏览器可视化图表的json文件。1. 打印模块级别的集合操作计数；2. 打印不属于简单操作的DTensor操作；3. 打印不属于简单操作的普通操作；4. 打印所有操作。

以字典形式返回通信操作计数。

通信操作计数以字典形式返回。

dict[str, dict[str, Any]]

dict[str, dict[str, Any]]

作为控制台输出的替代方案，可将结果写入用户指定的文件中。

为可视化维度小于3的DTensor的分片情况，DTensor提供了visualize_sharding()函数：

该函数可用于在终端中可视化1维或2维DTensor的分片结构。

使用时需要tabulate包，或者rich和matplotlib库。空张量则不会显示任何分片信息。

DTensor还提供了一组实验性功能。这些功能要么仍处于原型阶段，要么核心功能已经实现但仍在收集用户反馈。如果您对这些功能有意见，可向PyTorch提交问题报告。

context_parallel是一个用于启用上下文并行（CP）的实验性API。该API会执行两项操作：1）用支持CP版本的函数替换SDPA（torch.nn.functional.scaled_dot_product_attention）；2）沿序列维度对缓冲区进行分片，每个节点会根据网格信息保留对应的分片。

mesh（DeviceMesh）——上下文并行所使用的设备网格。

buffers（可选[List[torch.Tensor]]）——那些依赖序列维度的缓冲区。例如输入批次、标签和位置嵌入缓冲区等。为保证计算精度，这些缓冲区必须沿序列维度进行分片。分片操作会在原地进行，缓冲区的形状会在上下文作用期间发生变化。上下文结束后，这些缓冲区将会被恢复。可以使用no_restore_buffers参数指定哪些缓冲区无需恢复。请注意，缓冲区中不应包含任何nn.Parameter类型的对象。

buffer_seq_dims（可选[List[int]]）——缓冲区的序列维度。

no_restore_buffers（可选[Set[torch.Tensor]]）——位于此集合中的缓冲区在上下文结束后不会被恢复。该集合必须是buffers的子集。如果某些缓冲区在上下文结束后不再使用，可以将其放入此列表中，以避免额外的恢复操作。

Generator[None, None, None]

torch.distributed.tensor.experimental.context_parallel是PyTorch中的一个原型功能，该API可能会发生变化。

local_map()是一个实验性API，允许用户将DTensor传递给原本为torch.Tensor设计的函数。实现方式是提取DTensor的本地组件，调用该函数，然后根据out_placements参数将输出结果重新封装为DTensor。

func（Callable）——要应用于DTensor s每个本地分片的函数。

out_placements（Union[PlacementType, Tuple[PlacementType, …]]）——函数func的扁平化输出中DTensor s应占据的位置。如果扁平化输出只有一个值，那么out_placements应为PlacementType类型；否则，如果扁平化输出有多个值，out_placements则应为与扁平化输出一一对应的PlacementType值构成的元组。对于张量类型的输出，其位置由PlacementType类型表示（即Tuple[Placement]类型）；而对于非张量类型的输出，PlacementType应为None。唯一的例外是当没有传递DTensor参数时。在这种情况下，即使out_placements不为None，结果函数也应忽略这些指定位置，因为该函数并非在处理DTensor。

in_placements（Tuple[PlacementType, …]，可选）——函数func的扁平化输入中DTensor s必须占据的位置。如果指定了in_placements，local_map()会检查每个DTensor参数的位置是否与指定位置相同。如果位置不同且redistribute_inputs为False，则会抛出异常。否则，如果redistribute_inputs为True，那么在将本地张量传递给函数之前，会先将其重新分配到指定的分片位置。唯一的例外是当指定位置不为None且参数为torch.Tensor时。在这种情况下，将跳过位置检查，直接将该参数传递给函数。如果in_placements为None，则不会进行位置检查。默认值：None。

in_grad_placements（Tuple[PlacementType, …]，可选）——指示DTensor s的梯度在扁平化输入DTensor中所对应位置的提示信息。这是用户可以提供给to_local()的提示，用于处理本地张量输入的梯度布局与其DTensor输入布局不一致的情况。如果未指定此参数，我们将假设本地张量输入的梯度布局与原始DTensor输入的布局相同，并以此进行梯度计算。默认值：None。

device_mesh（DeviceMesh，可选）——输出DTensor s所在的设备网格。如果未指定，将会根据第一个输入DTensor的设备网格来推断。默认值：None。

redistribute_inputs（bool，可选）——布尔值，指示当输入DTensor的位置与所需的输入位置不同时，是否需要重新对它们进行分片。如果此值为False，而某个DTensor输入的位置不同，则会抛出异常。默认值：False。

一个Callable对象，它会对输入DTensor的每个本地分片应用func函数，并返回一个由func函数返回值构成的DTensor。

AssertionError——对于任何非张量类型的输出，我们要求其在out_placements中的对应输出位置为None。如果不符合此要求，将会抛出AssertionError异常。

ValueError——如果redistribute_inputs设置为False，但根据in_placements的要求需要对输入DTensor进行重新分配。

该API目前仍处于实验阶段，可能会发生变化。

register_sharding()是一个实验性API，允许用户在张量的输入和输出均为DTensor时，为某个运算符注册自定义的分片策略。以下情况时使用此功能较为有用：（1）该运算符没有默认的分片策略，例如它是DTensor不支持的定制运算符；（2）用户希望覆盖现有运算符的默认分片策略。

op（Union[OpOverload, List[OpOverload]]）——要注册自定义分片函数的运算符，或运算符列表。

一种函数装饰器，可用于封装定义运算符op的分片策略的函数。所定义的分片策略将被注册到DTensor中，如果DTensor已经实现了该运算符，此自定义策略将覆盖默认的分片策略。自定义分片函数接受的输入与原始运算符相同（不过如果某个参数是torch.Tensor类型，它会被替换为DTensor内部使用的类似张量的对象）。该函数应返回一系列2元组，每个元组指定一个可接受的输出位置及其对应的输入位置。

该API目前仍处于实验阶段，可能会发生变化。

---

## FullyShardedDataParallel#

**网址：** https://pytorch.org/docs/stable/fsdp.html

**内容：**
- FullyShardedDataParallel#

创建时间：2022年2月2日 | 最后更新时间：2025年6月11日用于将模块参数在数据并行工作进程之间进行分片的封装工具。

该设计的灵感来源于Xu等人的研究以及DeepSpeed的ZeRO Stage 3技术。FullyShardedDataParallel通常被缩写为FSDP。

使用FSDP时，需要先对目标模块进行封装，之后再初始化优化器。这是因为FSDP会修改参数变量，因此必须如此操作。

在配置FSDP时，需考虑目标CUDA设备的选择。如果该设备有编号（dev_id），则有以下三种选择：

1. 将模块直接放置在该设备上；
2. 使用torch.cuda.set_device(dev_id)指定目标设备；
3. 将dev_id作为参数传递给device_id构造函数。

这样可确保FSDP实例的计算设备为指定的目标设备。对于选项1和3，FSDP的初始化始终在GPU上完成；而选项2中，初始化则在模块当前所在的设备上执行，该设备可能是CPU。

如果使用了sync_module_states=True标志，则必须确保模块位于GPU上，或者通过device_id参数指定一个CUDA设备，以便在FSDP构造函数中将模块移至该设备。这是因为sync_module_states=True需要依赖GPU间的通信操作。

FSDP还会自动将前向传播过程中所需的输入张量移至GPU计算设备，因此无需手动从CPU转移这些张量。

当设置use_orig_params=True时，与ShardingStrategy.FULL_SHARD不同，ShardingStrategy.SHARD_GRAD_OP会暴露未分片的参数，而非前向传播后的分片参数。若需查看梯度，可使用with_grads=True参数调用summon_full_params方法。

若启用limit_all_gathers=True，在FSDP的前向传播准备阶段可能会观察到CPU线程暂时不发送任何计算内核的现象。这是有意为之，用于体现速率限制机制的作用。通过这种方式同步CPU线程，可避免为后续的全收集操作过度分配内存，且实际上不会延迟GPU内核的执行。

出于自动求导的需求，FSDP在前后向计算过程中会将管理型模块的参数替换为torch.Tensor视图。如果某个模块的前向传播依赖对参数的已保存引用，而非在每次迭代中重新获取这些引用，那么该模块将无法看到FSDP创建的新视图，从而导致自动求导功能无法正常工作。

最后，当使用sharding_strategy=ShardingStrategy.HYBRID_SHARD，且分片进程组为节点内配置、复制进程组为节点间配置时，设置NCCL_CROSS_NIC=1有助于在某些集群环境中缩短复制进程组的全收集耗时。

使用FSDP时需注意以下几项限制：

1. 当启用CPU卸载功能时，FSDP目前不支持在no_sync()之外进行梯度累积。这是因为FSDP会直接使用已缩减后的梯度，而不会将其与现有梯度累积，这可能导致错误结果。
2. FSDP不支持对包含在其内部的子模块执行前向传播。因为子模块的参数虽会被分片，但子模块本身并非FSDP实例，因此其前向传播无法正确地收集所有参数。
3. 由于FSDP注册后向钩子的机制，它不支持双次反向传播。
4. 在冻结参数方面，FSDP也有一些限制。当设置use_orig_params=False时，每个FSDP实例管理的参数必须全部处于冻结状态或全部未冻结状态。而当设置use_orig_params=True时，FSDP允许混合冻结与未冻结的参数，但为避免梯度内存占用超出预期，建议避免这种做法。

从PyTorch 1.12版本开始，FSDP对共享参数提供了有限的支持。如果您的应用场景需要更强大的共享参数支持，请在此问题中提出反馈。

请避免在前后向传播之间直接修改参数，除非使用了summon_full_params上下文，否则这些修改可能不会被保留。一个类型为 Callable[torch.nn.Module] -> None 的函数，用于指定如何将当前位于元设备上的模块初始化到实际设备上。从 v1.12 版本开始，FSDP 会通过 is_meta 方法识别出那些在元设备上拥有参数或缓冲区的模块；如果指定了 param_init_fn，则会调用该函数进行初始化，否则会调用 nn.Module.reset_parameters()。在这两种情况下，实现逻辑都应仅初始化模块自身的参数/缓冲区，而无需处理其子模块的相应元素，以避免重复初始化。此外，FSDP 还支持通过 torchdistX 的 deferred_init() API 实现延迟初始化：若指定了 param_init_fn，则会调用该函数进行初始化；否则会使用 torchdistX 默认的 materialize_module() 函数。由于 param_init_fn 会被应用于所有位于元设备上的模块，因此其实现应考虑模块类型的差异。FSDP 会在参数展平与分片处理之前调用该初始化函数。

device_id（可选，类型为 Union[int, torch.device]）——一个整数或 torch.device 对象，指定 FSDP 初始化所使用的 CUDA 设备，包括必要的模块初始化及参数分片操作。如果模块运行在 CPU 上，指定此参数可提升初始化速度。若已设置了默认的 CUDA 设备（例如通过 torch.cuda.set_device 设置），则用户也可传入 torch.cuda.current_device 作为该参数的值。（默认值：None）

sync_module_states（布尔值）——若设置为 True，则每个 FSDP 模块都会将模块参数和缓冲区从 rank 0 广播出去，以确保这些参数在所有节点间被复制（这会增加该构造函数的通信开销）。这种方式有助于通过 load_state_dict 以更高效的方式加载状态字checkpoint。相关示例可参考 FullStateDictConfig。（默认值：False）

forward_prefetch（布尔值）——若设置为 True，则 FSDP 会在当前前向计算之前，预先获取下一次前向传播所需的全收集操作数据。该功能仅对受 CPU 约束的工作负载有用，因为在这些场景中提前执行全收集操作有助于提高任务重叠度。由于预取操作会遵循第一次迭代的执行顺序，因此仅适用于静态图模型。（默认值：False）

limit_all_gathers（布尔值）——若设置为 True，则 FSDP 会强制同步 CPU 线程，确保 GPU 内存的使用仅限于两个连续的 FSDP 实例（即正在执行计算的当前实例以及其全收集操作已被预取的下一个实例）。若设置为 False，则 FSDP 允许 CPU 线程在不进行额外同步的情况下发起全收集操作。（默认值：True）我们通常将此功能称为“速率限制器”。仅在对内存压力较低且受 CPU 约束的工作负载中，才应将此标志设置为 False，因为在这种情况下 CPU 线程可以无需顾虑 GPU 内存使用情况而频繁发起各种操作。

use_orig_params（布尔值）——将其设置为 True 时，FSDP 会使用模块的原始参数。FSDP 会通过 nn.Module.named_parameters() 向用户暴露这些原始参数，而非其内部的 FlatParameter 对象。这意味着优化器步骤将在原始参数上执行，从而支持针对每个原始参数设置不同的超参数。FSDP 会保留原始参数变量，并在未分片与已分片形式之间转换这些参数的数据，而这两种形式实际上都是对底层未分片或已分片 FlatParameter 的视图。根据当前算法，已分片形式的参数始终为一维结构，从而丢失了原有的张量结构。对于某个特定节点而言，一个原始参数可能全部、部分或完全没有对应数据；若没有数据，则其表现形式为一个大小为 0 的空张量。用户不应编写依赖原始参数在分片形式下是否存在数据的程序。若要使用 torch.compile()，则必须将此参数设置为 True。将其设置为 False 时，FSDP 会通过 nn.Module.named_parameters() 向用户暴露其内部的 FlatParameter 对象。（默认值：False）

ignored_states（可选，类型为 Iterable[torch.nn.Parameter] 或 Iterable[torch.nn.Module]）——指定将被该 FSDP 实例忽略的参数或模块，即这些参数不会被分片处理，其梯度也不会在各个节点间进行归约。此参数已与现有的 ignored_modules 参数合并，我们可能会很快废弃 ignored_modules。为保持向后兼容性，我们仍保留了 ignored_states 和 ignored_modules 两个参数，但 FSDP 只允许其中之一被设置为非 None 值。

device_mesh（可选，类型为 DeviceMesh）——DeviceMesh 可作为 process_group 的替代方案使用。当传入 device_mesh 参数时，FSDP 会使用底层的进程组来执行全收集及归约-散布等集合通信操作。因此，这两个参数不能同时被使用。对于诸如 ShardingStrategy.HYBRID_SHARD 这样的混合分片策略，用户可以传入一个二维 DeviceMesh 对象，而非进程组元组。对于 2D FSDP + TP 的组合，用户则必须传入 device_mesh 而非 process_group。如需了解更多关于 DeviceMesh 的信息，请访问：https://pytorch.org/tutorials/recipes/distributed_device_mesh.html

递归地将该函数应用于所有子模块（通过 .children() 方法获取）以及当前模块本身。

典型用途包括初始化模型的参数（也可参考 torch.nn.init 相关功能）。

与 torch.nn.Module.apply 相比，此版本会在调用函数之前先收集所有参数。该函数不应在另一个 summon_full_params 上下文环境中被调用。

fn（模块 -> None）——要应用于每个子模块的函数。

检查当前实例是否为根级 FSDP 模块。

限制所有参数的梯度范数。

该范数是针对所有参数的梯度作为一个向量来计算的，且梯度会直接在原地进行修改。

max_norm（浮点数或整数）——梯度的最大范数。

norm_type（浮点数或整数）——所使用的 p-范数类型。可设置为 'inf' 表示无穷范数。

参数的总范数（被视为一个向量）。

如果所有 FSDP 实例都使用 NO_SHARD 策略，即不进行参数分片，那么可以直接使用 torch.nn.utils.clip_grad_norm_() 函数。

如果至少有一些 FSDP 实例采用了分片策略（即非 NO_SHARD 类型），则应使用此函数而非 torch.nn.utils.clip_grad_norm_()，因为该函数能够处理参数在节点间被分片的情况。

返回的总范数会采用 PyTorch 的类型提升规则，使用所有参数/梯度中“最大”精度的数据类型。例如，如果所有参数/梯度都使用低精度数据类型，那么返回的范数也会采用该低精度类型；但如果存在至少一个参数/梯度使用 FP32 精度，那么返回的范数就会采用 FP32 类型。

由于该操作需要使用集合通信，因此必须在所有节点上执行。

将已分片的优化器状态字展平。

该 API 与 shard_full_optim_state_dict() 类似，唯一的不同在于输入参数 sharded_optim_state_dict 应该由 shard_full_optim_state_dict() 函数返回。因此，每个节点都需要进行全收集操作来获取各个 ShardedTensor 对象。

sharded_optim_state_dict（类型为 Dict[str, Any]）——对应于未展平参数的优化器状态字，其中存储了已分片的优化器状态。

model（类型为 torch.nn.Module）——参考 shard_full_optim_state_dict() 的说明。

optim（类型为 torch.optim.Optimizer）——用于处理模型参数的优化器。参考 shard_full_optim_state_dict() 的说明。

为被包装的模块执行前向传播，同时插入 FSDP 特有的前后分片逻辑。

返回所有嵌套的 FSDP 实例。

这些实例可能包括模块本身；如果设置 root_only=True，则仅返回 FSDP 根级模块。

module（类型为 torch.nn.Module）——根级模块，它可能是 FSDP 模块，也可能不是。

root_only（布尔值）——是否仅返回 FSDP 根级模块。（默认值：False）

嵌套在输入模块中的 FSDP 模块。

类型为 List[FullyShardedDataParallel]。

返回完整的优化器状态字。

该函数会在 rank 0 上整合所有的优化器状态，然后按照 torch.optim.Optimizer.state_dict() 的约定以字典形式返回，其中包含 “state” 和 “param_groups” 两个键。模型中 FSDP 模块内的展平参数会被映射回其未展平的原始参数形式。

由于该操作需要使用集合通信，因此必须在所有节点上执行。不过，如果设置 rank0_only=True，则状态字仅会在 rank 0 上生成，其余节点返回的空字典中不包含任何内容。

与 torch.optim.Optimizer.state_dict() 不同，此方法使用完整的参数名称作为键，而非参数编号。

与 torch.optim.Optimizer.state_dict() 一样，优化器状态字中的张量不会被复制，因此可能会出现别名冲突的情况。为遵循最佳实践，建议立即保存返回的优化器状态字，例如可以使用 torch.save() 函数。

model（类型为 torch.nn.Module）——根级模块（它可能是 FullyShardedDataParallel 实例，也可能不是），其参数已被传递给优化器 optim。

optim（类型为 torch.optim.Optimizer）——用于处理模型参数的优化器。

optim_input（可选，类型为 Union[List[Dict[str, Any]], Iterable[torch.nn.Parameter]]）——传递给优化器 optim 的输入，可以是参数组列表或参数迭代器；如果该参数为 None，则默认认为输入为 model.parameters()。此参数已被废弃，无需再传入。（默认值：None）

rank0_only（布尔值）——若设置为 True，则仅在 rank 0 上保存已生成的字典；若设置为 False，则在所有节点上保存。（默认值：True）

group（类型为 dist.ProcessGroup）——模型的进程组，如果使用默认进程组则该参数为 None。（默认值：None）

一个字典，其中包含模型原始未展平参数的优化器状态，且按照 torch.optim.Optimizer.state_dict() 的约定包含 “state” 和 “param_groups” 两个键。如果设置 rank0_only=True，则非 rank 0 的节点将返回空字典。

获取以该模块为根级的所有 FSDP 模块的 state_dict_type 及相应的配置信息。

目标模块不一定是 FSDP 模块。

一个 StateDictSettings 对象，其中包含当前的 state_dict_type 以及 state_dict 和 optim_state_dict 的配置信息。

如果不同 FSDP 子模块的 StateDictSettings 不一致，则会引发 AssertionError 异常。

返回被包装的模块。

生成一个迭代器，遍历模块中的所有缓冲区，每次迭代都会同时返回缓冲区的名称及其本身的内容。

在 summon_full_params() 上下文管理器内部，该函数会截取缓冲区名称，并删除其中所有带有 FSDP 特有展平缓冲区前缀的字符串。

迭代器类型为 Iterator[tuple[str, torch.Tensor]]。

生成一个迭代器，遍历模块中的所有参数，每次迭代都会同时返回参数的名称及其本身的内容。

在 summon_full_params() 上下文管理器内部，该函数会截取参数名称，并删除其中所有带有 FSDP 特有展平参数前缀的字符串。

迭代器类型为 Iterator[tuple[str, torch.nn.parameter.Parameter]]。

禁用不同 FSDP 实例之间的梯度同步。在此机制下，梯度会累积在模块变量中，随后在离开该上下文后的首次前向-反向传播过程中进行同步。此功能仅适用于根级的 FSDP 实例，并会递归地应用于所有子级 FSDP 实例。

由于 FSDP 会一直累积完整的模型梯度（而非梯度分片），直至最终同步，因此这可能会增加内存使用量。

当与 CPU 卸载功能一起使用时，在上下文管理器内部，梯度不会被卸载到 CPU 上，而仅会在最终同步完成后才进行卸载。

将对应于分片模型的优化器状态字典进行转换。

给定的状态字典可转换为三种类型之一：1）完整的优化器状态字典；2）分片后的优化器状态字典；3）本地优化器状态字典。

对于完整的优化器状态字典，所有状态均保持未展平状态且未被分片。为避免内存溢出，可通过 state_dict_type() 指定仅使用 Rank0 或仅使用 CPU。

对于分片后的优化器状态字典，所有状态虽未展平但已被分片。为进一步节省内存，可通过 state_dict_type() 指定仅使用 CPU。

对于本地状态字典，则不会进行任何转换，但相关状态会从 nn.Tensor 转换为 ShardedTensor，以体现其分片特性（目前此功能暂不支持）。

model (torch.nn.Module) – 根模块（可能是也可能不是 FullyShardedDataParallel 实例），其参数会被传递给优化器 optim。

optim (torch.optim.Optimizer) – 用于处理模型参数的优化器。

optim_state_dict (Dict[str, Any]) – 需要转换的目标优化器状态字典。如果该值为 None，则会使用 optim.state_dict()。（默认值：None）

group (dist.ProcessGroup) – 参数被分片所涉及的模型进程组；若使用默认进程组，则该参数为 None。（默认值：None）

一个包含模型优化器状态的字典。优化器状态的分片方式由 state_dict_type 决定。

将优化器状态字典转换为适合加载到 FSDP 模型对应优化器中的格式。

对于通过 optim_state_dict() 转换后的 optim_state_dict，它会被转换为可加载到模型优化器 optim 中的展平后优化器状态字典。此时模型必须已通过 FullyShardedDataParallel 进行分片。

model (torch.nn.Module) – 根模块（可能是也可能不是 FullyShardedDataParallel 实例），其参数会被传递给优化器 optim。

optim (torch.optim.Optimizer) – 用于处理模型参数的优化器。

optim_state_dict (Dict[str, Any]) – 需要加载的优化器状态。

is_named_optimizer (bool) – 该优化器是否为 NamedOptimizer 或 KeyedOptimizer。仅当 optim 为 TorchRec 的 KeyedOptimizer 或 torch.distributed 的 NamedOptimizer 时，才将此参数设置为 True。

load_directly (bool) – 若设置为 True，该接口在返回结果之前还会调用 optim.load_state_dict(result)。否则，需由用户自行调用 optim.load_state_dict()。（默认值：False）

group (dist.ProcessGroup) – 参数被分片所涉及的模型进程组；若使用默认进程组，则该参数为 None。（默认值：None）

注册通信钩子。

这是一项增强功能，为用户提供了灵活的钩子机制，允许他们指定 FSDP 如何在多个工作节点之间聚合梯度。该钩子可用于实现诸如 GossipGrad 和梯度压缩等算法，这些算法在使用 FullyShardedDataParallel 进行训练时需要不同的参数同步通信策略。

FSDP 通信钩子需在首次前向传播之前且仅注册一次。

state (object) – 传递给钩子，用于在训练过程中保存各种状态信息。例如梯度压缩中的错误反馈、GossipGrad 中需要通信的相邻节点等信息。该数据由每个工作节点本地存储，并在节点内的所有梯度张量之间共享。

hook (Callable) – 可调用对象，其签名需符合以下之一：1）hook: Callable[torch.Tensor] -> None：该函数接收一个 Python 张量，表示针对该 FSDP 单元所封装的模型中所有未被其他 FSDP 子单元封装的变量、经过展平且未分片的完整梯度。函数会对该梯度执行必要的处理后返回 None；2）hook: Callable[torch.Tensor, torch.Tensor] -> None：该函数接收两个 Python 张量，第一个张量表示针对该 FSDP 单元所封装的模型中所有未被其他 FSDP 子单元封装的变量、经过展平且未分片的完整梯度，第二个张量则是用于存储归约后某部分分片梯度的预分配张量。在这两种情况下，可调用对象都会执行必要的处理后返回 None。签名为 1 的可调用对象用于处理无分片情况的梯度通信，而签名为 2 的则用于处理有分片情况的梯度通信。

使用 optim_state_key_type 指定的键类型，对优化器状态字典 optim_state_dict 进行重新键值映射。

此功能可用于实现带有 FSDP 实例的模型与没有 FSDP 实例的模型之间的优化器状态字典兼容性。

将 FSDP 的完整优化器状态字典（即从 full_optim_state_dict() 获得的）重新键值映射为参数 ID，以便加载到未被封装的模型中：

将非封装模型中的普通优化器状态字典重新键值映射，以便加载到已被封装的模型中：

使用 optim_state_key_type 指定的参数键对优化器状态字典进行重新键值映射。

将完整的优化器状态字典从 Rank 0 分发到所有其他 Rank。

返回每个 Rank 上的分片后的优化器状态字典。其返回值与 shard_full_optim_state_dict() 相同，且在 Rank 0 上，第一个参数应为 full_optim_state_dict() 的返回值。

shard_full_optim_state_dict() 和 scatter_full_optim_state_dict() 均可用于获取待加载的分片优化器状态字典。假设完整的优化器状态字典存储在 CPU 内存中，前者要求每个 Rank 的 CPU 内存中都存有完整字典，各 Rank 在无需通信的情况下分别对字典进行分片；而后者仅要求 Rank 0 的 CPU 内存中存有完整字典，Rank 0 会将每个分片移至 GPU 内存（通过 NCCL）并传递给相应的 Rank。因此，前者的总体 CPU 内存成本更高，而后者的通信成本则更高。

full_optim_state_dict (Optional[Dict[str, Any]]) – 对应于未展平参数的优化器状态字典；若位于 Rank 0，则其中包含完整的、未分片的优化器状态；在非零 Rank 上，该参数将被忽略。

model (torch.nn.Module) – 根模块（可能是也可能不是 FullyShardedDataParallel 实例），其参数与 full_optim_state_dict 中的优化器状态相对应。

optim_input (Optional[Union[List[Dict[str, Any]], Iterable[torch.nn.Parameter]]]) – 传递给优化器的输入，表现为参数组列表或参数的可迭代对象；如果为 None，则该方法假定输入为 model.parameters()。该参数已过时，无需再传递。（默认值：None）

optim (Optional[torch.optim.Optimizer]) – 用于加载该方法返回的状态字典的优化器。相比 optim_input，此参数是更推荐的使用方式。（默认值：None）

group (dist.ProcessGroup) – 模型的进程组；若使用默认进程组，则该参数为 None。（默认值：None）

将完整的优化器状态字典重新映射为展平后的参数，且仅包含当前 Rank 对应的优化器状态部分。

设置目标模块所有子级 FSDP 模块的 state_dict_type。

同时还可接受（可选的）针对模型和优化器状态字典的配置。目标模块不一定是 FSDP 模块；如果目标是 FSDP 模块，其 state_dict_type 也会随之改变。

此接口仅应针对顶层（根级）模块调用。

当根级 FSDP 模块被其他 nn.Module 封装时，此接口允许用户透明地使用传统的 state_dict API 来保存模型检查点。例如，以下方式可确保在所有非 FSDP 实例上调用 state_dict 方法，而对于 FSDP 实例则自动调用 sharded_state_dict 的实现：

module (torch.nn.Module) – 根模块。

state_dict_type (StateDictType) – 需要设置的期望状态字典类型。

state_dict_config (Optional[StateDictConfig]) – 目标状态字典类型的配置参数。

optim_state_dict_config (Optional[OptimStateDictConfig]) – 优化器状态字典的配置参数。

一个包含模块先前状态字典类型及配置信息的 StateDictSettings 对象。

对完整的优化器状态字典进行分片。

将 full_optim_state_dict 中的状态重新映射为展平后的参数，且仅包含当前 Rank 对应的优化器状态部分。第一个参数应为 full_optim_state_dict() 的返回值。

shard_full_optim_state_dict() 和 scatter_full_optim_state_dict() 均可用于获取待加载的分片优化器状态字典。假设完整的优化器状态字典存储在 CPU 内存中，前者要求每个 Rank 的 CPU 内存中都存有完整字典，各 Rank 在无需通信的情况下分别对字典进行分片；而后者仅要求 Rank 0 的 CPU 内存中存有完整字典，Rank 0 会将每个分片移至 GPU 内存（通过 NCCL）并传递给相应的 Rank。因此，前者的总体 CPU 内存成本更高，而后者的通信成本则更高。

full_optim_state_dict (Dict[str, Any]) – 对应于未展平参数的优化器状态字典，包含完整的、未分片的优化器状态。

model (torch.nn.Module) – 根模块（可能是也可能不是 FullyShardedDataParallel 实例），其参数与 full_optim_state_dict 中的优化器状态相对应。

optim_input (Optional[Union[List[Dict[str, Any]], Iterable[torch.nn.Parameter]]]) – 传递给优化器的输入，表现为参数组列表或参数的可迭代对象；如果为 None，则该方法假定输入为 model.parameters()。该参数已过时，无需再传递。（默认值：None）

optim (Optional[torch.optim.Optimizer]) – 用于加载该方法返回的状态字典的优化器。相比 optim_input，此参数是更推荐的使用方式。（默认值：None）当前，完整的优化器状态字典已被重新映射为扁平化参数，而非未扁平化的参数，并且仅包含该等级对应的优化器状态部分。

以分片形式返回优化器状态字典。

该接口与full_optim_state_dict()类似，但会将所有非零维度的状态转换为ShardedTensor格式，以此节省内存。仅当模型状态字典是通过带有state_dict_type(SHARDED_STATE_DICT)参数的上下文管理器生成的时，才应使用此接口。

如需详细用法，请参考full_optim_state_dict()的文档。

返回的状态字典中包含ShardedTensor，无法直接被常规的optim.load_state_dict函数使用。

设置目标模块所有下游FSDP模块的状态字典类型。

该上下文管理器具有与set_state_dict_type()相同的功能。详情请参阅set_state_dict_type()的文档。

module（torch.nn.Module）——根模块。
state_dict_type（StateDictType）——需设置的期望状态字典类型。
state_dict_config（可选[StateDictConfig]）——针对目标状态字典类型所需的模型状态字典配置。
optim_state_dict_config（可选[OptimStateDictConfig]）——针对目标状态字典类型所需的优化器状态字典配置。

通过该上下文管理器为FSDP实例暴露完整参数。

在模型的前向/反向传播之后，此功能可用于获取参数以进行进一步处理或检查。它既可以作用于非FSDP模块，也可根据recurse参数的值，递归获取所有包含的FSDP模块及其子模块的完整参数。

该功能可应用于嵌套的FSDP实例中。

不可在前向或反向传播过程中使用，也不可从该上下文内部启动前向或反向传播。

当上下文管理器退出后，参数将恢复为各自的本地分片，其存储行为与前向传播时相同。

虽然可以修改完整参数，但仅与本地参数分片对应的部分会在上下文管理器退出后保留（除非设置writeback=False，此时修改内容将被丢弃）。若FSDP未对参数进行分片——目前仅在世界大小为1或配置了NO_SHARD时才会如此——则无论是否设置writeback，修改内容都会被保留。

该方法适用于本身并非FSDP但可能包含多个独立FSDP单元的模块。在这种情况下，所提供的参数将应用于所有包含的FSDP单元。

请注意，目前不支持同时设置rank0_only=True和writeback=True，否则会引发错误。这是因为在上下文内部，不同等级的模型参数形状可能有所不同，对其进行写入会导致上下文退出后各等级之间的参数不一致。

还需注意的是，若设置offload_to_cpu且rank0_only=False，则同一台机器上的GPU所对应的完整参数会被冗余地复制到CPU内存中，这有可能导致CPU内存不足。建议结合使用offload_to_cpu和rank0_only=True。

recurse（布尔值，可选）——递归获取嵌套FSDP实例的所有参数（默认值为True）。
writeback（布尔值，可选）——若设置为False，则在上下文管理器退出后，对参数的修改将被丢弃；禁用此选项可略微提升效率（默认值为True）。
rank0_only（布尔值，可选）——若设置为True，则仅在全球等级0上生成完整参数。这意味着在上下文内部，只有等级0拥有完整参数，其他等级则拥有分片参数。请注意，同时设置rank0_only=True和writeback=True是不支持的，因为上下文内部不同等级的模型参数形状可能不同，对其进行写入会导致上下文退出后各等级之间的参数不一致。
offload_to_cpu（布尔值，可选）——若设置为True，则将完整参数卸载到CPU上。需注意，目前仅当参数已被分片时才会进行此操作（仅在世界大小为1或配置了NO_SHARD时参数不会被分片）。建议结合使用offload_to_cpu和rank0_only=True，以避免模型参数被冗余地复制到同一块CPU内存中。
with_grads（布尔值，可选）——若设置为True，则梯度也会与参数一同进行去分片处理。目前，仅当在创建FSDP实例时设置use_orig_params=True，且在此方法中设置offload_to_cpu=False时，才支持此功能。（默认值为False）

该选项用于配置显式的反向传播预取功能，通过让反向传播过程中的通信与计算重叠来提升吞吐量，但代价是会增加一定的内存使用量。

BACKWARD_PRE：可实现最大的重叠度，但也会导致最高的内存消耗。它会在当前参数组的梯度计算之前，预先加载下一组参数。这样就能使后续的all-gather操作与当前的梯度计算相互重叠，最多时可同时将当前参数组、下一组参数以及当前的梯度存储在内存中。

BACKWARD_POST：可实现较少的重叠度，但内存占用更低。它会在当前参数组的梯度计算之后，再加载下一组参数。这样就能使当前的reduce-scatter操作与后续的梯度计算相互重叠，并且在为下一组参数分配内存之前释放当前参数组，最多时仅将下一组参数和当前的梯度存储在内存中。

FSDP的backward_prefetch参数接受None值，表示完全禁用反向传播预取功能。此时没有重叠，也不会增加内存使用量。通常我们不推荐此设置，因为它可能会显著降低吞吐量。

更多技术背景说明：对于使用NCCL后端的单进程组，即使来自不同流的集合操作也会竞争同一个设备级的NCCL流，因此这些操作的执行顺序会影响是否能够实现重叠。两种反向传播预取模式对应不同的操作顺序。

该选项用于指定FullySharedDataParallel在分布式训练中采用的分片策略。

FULL_SHARD：对参数、梯度以及优化器状态都进行分片处理。对于参数，该策略会在前向传播之前通过all-gather操作将它们合并为完整形式，前向传播之后再重新分片；在反向传播计算之前再次去分片，计算之后再重新分片。对于梯度，则在反向传播计算之后通过reduce-scatter操作对它们进行同步并分片处理。分片后的优化器状态则由各等级在本地更新。

SHARD_GRAD_OP：在计算过程中对梯度及优化器状态进行分片，同时还在计算之外对参数进行分片。对于参数，该策略会在前向传播之前去分片，前向传播之后不再重新分片，仅在反向传播计算之后才重新分片。分片后的优化器状态仍由各等级在本地更新。在no_sync()函数内部，反向传播计算之后参数也不会被重新分片。

NO_SHARD：不对参数、梯度及优化器状态进行分片，而是像PyTorch的DistributedDataParallel API那样在各个等级之间复制这些数据。对于梯度，该策略会在反向传播计算之后通过all-reduce操作对它们进行同步。未分片的优化器状态则由各等级在本地更新。

HYBRID_SHARD：在单个节点内部采用FULL_SHARD策略，而在节点之间复制参数。由于昂贵的all-gather和reduce-scatter操作仅在节点内部执行，因此可以减少通信量，对于中等规模的模型而言性能更佳。

_HYBRID_SHARD_ZERO2：在单个节点内部采用SHARD_GRAD_OP策略，而在节点之间复制参数。该方式与HYBRID_SHARD类似，但由于前向传播之后未释放未分片的参数，从而避免了预反向传播阶段的all-gather操作，因此可能实现更高的吞吐量。

该选项用于配置FSDP原生的混合精度训练功能。

param_dtype（可选[torch.dtype]）——指定模型参数在前向和反向传播过程中的数据类型，进而决定相关计算的精度。在前向和反向传播之外，分片后的参数会以全精度形式保留（例如在优化器更新步骤中）；在保存模型检查点时，参数始终以全精度保存。（默认值为None）

reduce_dtype（可选[torch.dtype]）——指定梯度归约操作（即reduce-scatter或all-reduce）所使用的数据类型。如果该参数为None而param_dtype不为None，则reduce_dtype将采用param_dtype的值，此时仍以低精度进行梯度归约。该参数允许与param_dtype不同，例如用于强制梯度归约以全精度执行。（默认值为None）

buffer_dtype（可选[torch.dtype]）——指定缓冲区的数据类型。FSDP不会对缓冲区进行分片，而是在第一次前向传播时将它们转换为buffer_dtype类型，之后一直保持该数据类型。在保存模型检查点时，除LOCAL_STATE_DICT外的缓冲区均以全精度保存。（默认值为None）

keep_low_precision_grads（布尔值）——若设置为False，则FSDP会在反向传播之后将梯度升级为全精度，以便后续的优化器更新步骤使用。若设置为True，则FSDP会保持梯度在用于梯度归约的精度格式，如果使用的是支持低精度运行的自定义优化器，这种方式可以节省内存。（默认值为False）

cast_forward_inputs（布尔值）——若设置为True，则该FSDP模块会将自身的前向传播参数和关键字参数转换为param_dtype类型。这是为了确保许多操作所需的参数类型与输入类型一致。当仅对部分而非所有FSDP模块应用混合精度时，可能需要将此选项设置为True，因为这种情况下需要让混合精度的FSDP子模块重新转换其输入参数类型。（默认值为False）

cast_root_forward_inputs（布尔值）——若设置为True，则根级FSDP模块会将自身的前向传播参数和关键字参数转换为param_dtype类型，此设置会覆盖cast_forward_inputs的默认值。对于非根级的FSDP模块，此选项则不会产生任何影响。（默认值为True）

_module_classes_to_ignore（collections.abc.Sequence[type[torch.nn.modules.module.Module]]）——（Sequence[Type[nn.Module]]）：当使用auto_wrap_policy时，该选项用于指定在混合精度处理时应忽略的模块类别。属于这些类别的模块将单独应用FSDP，且混合精度功能将被禁用（这意味着最终的FSDP构建方式将与指定的策略有所不同）。如果未指定auto_wrap_policy，则此选项不起任何作用。该接口仍处于实验阶段，可能会发生变化。（默认值为(_BatchNorm,))

该接口为实验性质，未来可能会发生变化。

仅浮点型张量会被转换为指定的数据类型。

在summon_full_params函数中，参数会被强制转换为全精度，但缓冲区则不会。即使输入为浮点16或bfloat16等低精度格式，层归一化与批量归一化操作仍会以浮点32格式进行累积。仅针对这些归一化模块禁用FSDP的混合精度功能，仅意味着其仿射参数会保持为浮点32格式。但这会导致这些归一化模块需要单独执行全收集与缩减散布操作，可能降低效率；因此，在工作负载允许的情况下，用户仍建议为这些模块应用混合精度功能。

默认情况下，若用户传入包含任何_BatchNorm模块的模型并指定了_auto_wrap_policy参数，则这些批量归一化模块将会被单独应用FSDP，且混合精度功能会被禁用。具体可参考_module_classes_to_ignore参数。

MixedPrecision的默认值为_cast_root_forward_inputs=True而_cast_forward_inputs=False。对于根级FSDP实例，其_cast_root_forward_inputs参数的优先级高于_cast_forward_inputs参数；而非根级FSDP实例的_cast_root_forward_inputs值则会被忽略。在典型场景下——即每个FSDP实例都采用相同的MixedPrecision配置，且仅需在模型前向传播开始时将输入转换为param_dtype格式——默认设置已足够使用。

对于具有不同MixedPrecision配置的嵌套FSDP实例，我们建议为每个实例的前向传播之前单独设置_cast_forward_inputs值，以决定是否对输入进行类型转换。在这种情况下，由于类型转换会在每个FSDP实例的前向传播之前执行，父级FSDP实例应让其非FSDP子模块先于FSDP子模块运行，以避免因混合精度配置不同而导致激活值的类型发生改变。

以上内容为一个可行示例。反之，若将model[1]替换为model[0]，即让采用不同MixedPrecision配置的子模块先执行前向传播，那么model[1]将错误地获取到浮点16格式的激活值，而非bfloat16格式的值。

此部分用于配置CPU卸载功能。

offload_params（布尔值）——指定当参数未被用于计算时是否将其卸载到CPU上。若设置为True，则梯度也会被卸载到CPU，这意味着优化器步骤将在CPU上执行。

StateDictConfig是所有状态字典配置类的基类。用户应创建其子类（如FullStateDictConfig），以便为FSDP支持的对应状态字典类型配置相关参数。

offload_to_cpu（布尔值）——若设置为True，则FSDP会将状态字典的值卸载到CPU；若设置为False，则FSDP会将其保留在GPU上。（默认值：False）

FullStateDictConfig是一个专为StateDictType.FULL_STATE_DICT设计的配置类。为节省GPU内存与CPU内存，我们建议在保存完整状态字典时同时将offload_to_cpu设置为True，将rank0_only设置为True。该配置类应通过state_dict_type()上下文管理器来使用，具体如下：

rank0_only（布尔值）——若设置为True，则仅rank 0会保存完整状态字典，而非零rank则保存空字典；若设置为False，则所有rank都会保存完整状态字典。（默认值：False）

ShardedStateDictConfig是一个专为StateDictType.SHARDED_STATE_DICT设计的配置类。

_use_dtensor（布尔值）——若设置为True，则FSDP会将状态字典的值以DTensor格式保存；若设置为False，则以ShardedTensor格式保存。（默认值：False）

_use_dtensor是ShardedStateDictConfig的私有字段，由FSDP用于确定状态字典值的类型。用户不应手动修改此字段。

OptimStateDictConfig是所有优化器状态字典配置类的基类。用户应创建其子类（如FullOptimStateDictConfig），以便为FSDP支持的对应优化器状态字典类型配置相关参数。

offload_to_cpu（布尔值）——若设置为True，则FSDP会将状态字典中的张量值卸载到CPU；若设置为False，则FSDP会将其保留在原始设备上（除非启用了参数CPU卸载功能，否则为GPU）。（默认值：True）

rank0_only（布尔值）——若设置为True，则仅rank 0会保存完整状态字典，而非零rank则保存空字典；若设置为False，则所有rank都会保存完整状态字典。（默认值：False）

ShardedOptimStateDictConfig是一个专为StateDictType.SHARDED_STATE_DICT设计的配置类。

_use_dtensor（布尔值）——若设置为True，则FSDP会将状态字典的值以DTensor格式保存；若设置为False，则以ShardedTensor格式保存。（默认值：False）

_use_dtensor是ShardedOptimStateDictConfig的私有字段，由FSDP用于确定状态字典值的类型。用户不应手动修改此字段。

---

## 分布式优化器#

**网址：** https://pytorch.org/docs/stable/distributed.optim.html

**内容：**
- 分布式优化器#

创建时间：2021年3月1日 | 最后更新时间：2025年6月16日

当前使用CUDA张量时不支持分布式优化器功能。

torch.distributed.optim提供了DistributedOptimizer类，该类接收一组远程参数（RRef）的引用，并在参数所在的工作节点上本地运行优化器。分布式优化器可使用任何本地优化器的基类，在各工作节点上分别应用梯度更新。

DistributedOptimizer会获取分散在各个工作节点上的参数的远程引用，然后针对每个参数在本地应用指定的优化器。

该类通过get_gradients()方法来获取特定参数的梯度值。

无论来自同一客户端还是不同客户端，对step()方法的并发调用都将在每个工作节点上被串行处理——因为每个工作节点的优化器一次只能处理一组梯度。不过，并不能保证每次都只为一个客户端执行完整的前向传播-反向传播-优化器更新流程。这意味着所应用的梯度可能并非对应于某个工作节点上最新执行的前向传播结果。此外，不同工作节点之间的执行顺序也无法得到保证。

DistributedOptimizer默认会以启用TorchScript的模式创建本地优化器，这样在多线程训练场景下（例如分布式模型并行训练），优化器的更新就不会被Python全局解释器锁（GIL）所阻塞。目前大多数优化器都支持此功能。用户也可按照PyTorch教程中的方法，为自己的自定义优化器启用TorchScript支持。

optimizer_class（optim.Optimizer）——即要在每个工作节点上实例化的优化器类。

params_rref（list[RRef]）——需要优化的本地或远程参数的RRef引用列表。

args——要传递给每个工作节点上优化器构造函数的参数。

kwargs——要传递给每个工作节点上优化器构造函数的额外参数。

执行单次优化步骤。

该方法会在所有包含需优化参数的工作节点上调用torch.optim.Optimizer.step()方法，并会一直阻塞直到所有节点返回结果。所提供的context_id将用于获取包含需应用到参数上的梯度的对应上下文。

context_id——即应在此上下文中执行优化器步骤的自动求导上下文ID。

用于包装任意的torch.optim.Optimizer，并在本地SGD之后执行后续操作。该优化器会在每一步都运行本地优化器；在预热阶段结束后，它会在应用本地优化器之后定期对参数进行平均处理。

optim（Optimizer）——即本地优化器。

averager（ModelAverager）——用于在本地SGD之后运行模型平均化算法的实例。

此功能与torch.optim.Optimizer的load_state_dict()方法类似，但还会将模型平均化器的步进值恢复为保存在提供的状态字典中的数值。如果状态字典中不存在“step”键，则会发出警告，并将模型平均化器的步进值初始化为0。

此功能与torch.optim.Optimizer的state_dict()方法类似，但会在检查点中额外添加一条记录，用于存储模型平均化器的步进值，从而避免重新加载时再次进行不必要的预热操作。

执行单次优化步骤（参数更新）。

用于包装任意的optim.Optimizer，并将其状态在集群中的各个rank之间进行分片处理。这种分片方式遵循ZeRO机制实现。每个rank中的本地优化器实例仅需负责更新大约1/world_size个参数，因此也只需保存1/world_size个优化器状态。在本地完成参数更新后，每个rank会将自己的参数广播给其他所有节点，以确保所有模型副本处于相同状态。ZeroRedundancyOptimizer可与torch.nn.parallel.DistributedDataParallel结合使用，以降低每个rank的峰值内存占用。

ZeroRedundancyOptimizer采用排序贪心算法在每个rank中对参数进行打包处理。每个参数仅属于一个rank，不会在各个rank之间分配。这种划分方式是任意的，可能与其参数的注册顺序或使用顺序不一致。

params（Iterable）——包含所有需分片处理的torch.Tensor或dict的迭代对象。

optimizer_class（torch.nn.Optimizer）——即本地优化器的类。

process_group（ProcessGroup，可选）——即torch.distributed.ProcessGroup对象（默认值为由torch.distributed.init_process_group()初始化的dist.group.WORLD）。

parameters_as_bucket_view（布尔值，可选）——若设置为True，则参数会被打包到多个桶中以加快通信速度，此时param.data字段会指向不同偏移量处的桶视图；若设置为False，则每个参数都会单独进行通信，且每个params.data的值保持不变。（默认值：False）

overlap_with_ddp（布尔值，可选）——若设置为True，则step()操作会与DistributedDataParallel的梯度同步步骤重叠执行；这要求（1）optimizer_class参数对应的优化器必须是函数形式，或具有等效的函数形式；（2）需注册一个通过ddp_zero_hook.py中的函数生成的DDP通信钩子；此时参数会被打包到与DistributedDataParallel相同的桶结构中，因此parameters_as_bucket_view参数将被忽略。若设置为False，则step()操作会在反向传播之后独立执行（即按常规方式执行）。（默认值：False）

**defaults——任何后续传递的参数，这些参数会被直接传递给本地优化器。**

目前，ZeroRedundancyOptimizer要求所有传入的参数都必须属于同一密集型数据类型。如果将overlap_with_ddp设置为True，则需注意以下情况：根据当前实现方式，当与DistributedDataParallel重叠使用时，在前两到三次训练迭代中，优化器步骤不会执行参数更新——具体取决于static_graph是否设置为False或True。这是因为该优化器需要了解DistributedDataParallel所采用的梯度分桶策略，而这一策略在static_graph为False时需等到第二次前向传播才能确定，在static_graph为True时则需等到第三次前向传播。为解决这一问题，一种方法是在输入数据前添加虚拟参数。

ZeroRedundancyOptimizer目前仍处于实验阶段，功能可能会发生变化。

向优化器的param_groups中添加一个参数组。在微调预训练模型时，这一功能非常有用，因为随着训练的进行，原本被冻结的层可以被设为可训练状态，并加入优化器中。

param_group（dict）——指定需要优化的参数以及针对特定组的优化选项。

该方法负责更新所有分区上的分片数据，但必须在所有节点上调用。如果在部分节点上调用此方法，训练将会挂起，因为通信操作依赖于被管理的参数，并期望所有节点都参与对同一组参数的运算。

在目标节点上合并来自各节点的state_dict列表（每个节点一个）。

to（int）——接收优化器状态的节点编号（默认值为0）。

RuntimeError——如果设置overlap_with_ddp=True，且在该ZeroRedundancyOptimizer实例完全初始化之前就调用了此方法，而初始化通常发生在DistributedDataParallel的梯度桶被重新构建之后。

此方法必须在所有节点上调用。

返回默认设备。

返回ZeRO合并钩子。

该钩子通过屏蔽优化器步骤中的集合通信操作，使得在输入数据不均匀的情况下仍能进行训练。

在调用此钩子之前，必须先正确设置梯度。

kwargs（dict）——一个包含用于在运行时修改合并钩子行为的任意关键字参数的字典；所有共享相同合并上下文管理器的Joinable实例都会接收到相同的kwargs值。

该钩子不支持任何关键字参数，即kwargs会被忽略。

返回进程组。

从输入的state_dict中加载与指定节点相关的状态，并根据需要更新本地优化器。

state_dict（dict）——优化器状态；应为调用state_dict()函数后返回的对象。

RuntimeError——如果设置overlap_with_ddp=True，且在该ZeroRedundancyOptimizer实例完全初始化之前就调用了此方法，而初始化通常发生在DistributedDataParallel的梯度桶被重新构建之后；或者在没有先调用consolidate_state_dict()的情况下直接调用此方法。

执行一次优化器步骤，并在所有节点之间同步参数。

closure（Callable）——一个用于重新评估模型并返回损失值的闭包函数；大多数优化器可选项用。

根据底层本地优化器的不同，损失值可能是可选的。

任何额外的参数都会原封不动地传递给基础优化器。在正向传播中，子模块的执行顺序  
子模块之间的激活流  
子模块之间是否存在函数运算符（例如，relu或加法操作不会被Module.children()捕获）。  

相比之下，pipeline API能够确保真正保留正向传播的行为。它还能捕捉各分区之间的激活流，从而帮助分布式运行时在无需人工干预的情况下进行正确的发送/接收操作。  

pipeline API的另一个优点是，分割点可以位于模型层级结构的任意位置。在分割后的分区中，与该分区相关的原始模型层级结构会自动重建，且不会给您带来任何成本。因此，指向子模块或参数的全限定名（FQN）依然有效，那些依赖FQN的服务（如FSDP、TP或检查点机制）几乎无需修改代码即可继续在已分区的模块上运行。  

您可以通过扩展以下两个类之一来实现自定义的管道调度：  
PipelineScheduleSingle  
PipelineScheduleMulti  

PipelineScheduleSingle适用于为每个进程分配仅一个阶段的调度方案；而PipelineScheduleMulti则适用于为每个进程分配多个阶段的调度方案。  

例如，ScheduleGPipe和Schedule1F1B是PipelineScheduleSingle的子类；而ScheduleInterleaved1F1B、ScheduleLoopedBFS、ScheduleInterleavedZeroBubble以及ScheduleZBVZeroBubble则是PipelineScheduleMulti的子类。  

您可以使用torch._logging中的TORCH_LOGS环境变量来开启更详细的日志记录：  
TORCH_LOGS=+pp：显示DEBUG级别及以上的所有日志信息。  
TORCH_LOGS=pp：显示INFO级别及以上的日志信息。  
TORCH_LOGS=-pp：显示WARNING级别及以上的日志信息。  

以下是一组可将模型转换为管道表示形式的API：  

一个枚举类型，用于表示子模块执行过程中可能进行分割的点：  
:ivar BEGINNING：表示在正向传播函数中某个子模块执行之前添加分割点。  
:ivar END：表示在正向传播函数中某个子模块执行之后添加分割点。  

根据指定规则对模块进行分割。  
更多详情请参阅Pipe相关文档。  

module (Module) – 需要被分割的模块。  
mb_args (tuple[Any, ...]) – 以微批次形式给出的位置参数示例。  
mb_kwargs (Optional[dict[str, Any]]) – 以微批次形式给出的关键字参数示例。（默认值：None）  
split_spec (Optional[dict[str, torch.distributed.pipelining._IR.SplitPoint]]) – 以子模块名称作为分割标记的字典。（默认值：None）  
split_policy (Optional[Callable[[GraphModule], GraphModule]]) – 用于分割模块的策略。（默认值：None）  

Pipe类对应的管道表示形式。  

pipe_split是一种特殊运算符，用于标记模块中各阶段之间的边界，进而将模块分割成多个阶段。如果以即时模式运行已添加该标记的模块，则该运算符不会产生任何实际效果。  

上述示例将被分割为两个阶段。  

用于指定输入分块的类  

给定一系列位置参数和关键字参数，根据各自的分块规则将其分割成多个块。  
args (tuple[Any, ...]) – 位置参数的元组形式。  
kwargs (Optional[dict[str, Any]]) – 关键字参数的字典形式。  
chunks (int) – 需要将位置参数和关键字参数分割成的块数。  
args_chunk_spec (Optional[tuple[torch.distributed.pipelining.microbatch.TensorChunkSpec, ...]]) – 与args形状相同的参数分块规则。  
kwargs_chunk_spec (Optional[dict[str, torch.distributed.pipelining.microbatch.TensorChunkSpec]]) – 与kwargs形状相同的参数分块规则。  

sharded_args kwargs_split：已分割后的关键字参数列表。  

给定一系列块，根据分块规则将它们合并为一个整体值。  
chunks (list[Any]) – 块的列表形式。  
chunk_spec – 块的分块规则。  

表示管道并行架构中某个管道阶段的类。  

PipelineStage假设模型是按顺序分块的，即模型被分割成多个块，一个块的输出会作为下一个块的输入，且不存在跳过连接。  

PipelineStage会通过按线性顺序将stage0的输出传递给stage1，以此类推，自动执行运行时的形状/类型推断。若要绕过形状推断，可直接为每个PipelineStage实例传入input_args和output_args参数。  

submodule (nn.Module) – 该阶段所包装的PyTorch模块。  
stage_index (int) – 该阶段的编号。  
num_stages (int) – 总阶段数。  
device (torch.device) – 该阶段所在的设备。  
input_args (Union[torch.Tensor, Tuple[torch.tensor]], optional) – 子模块的输入参数。  
output_args (Union[torch.Tensor, Tuple[torch.tensor]], optional) – 子模块的输出参数。  
group (dist.ProcessGroup, optional) – 用于分布式训练的进程组。若为None，则使用默认进程组。  
dw_builder (Optional[Callable[[], Callable[..., None]])] – 如果提供了此函数，dw_builder将构建一个新的dw_runner函数，用于在F、I、W（正向传播、输入、权重）零气泡调度中处理权重操作。  

根据需要被包装的阶段模块以及管道相关信息，创建一个管道阶段。  
stage_module (torch.nn.Module) – 需要被该阶段包装的模块。  
stage_index (int) – 该阶段在管道中的编号。  
pipe_info (PipeInfo) – 关于管道的信息，可通过pipe.info()获取。  
device (torch.device) – 该阶段将使用的设备。  
group (Optional[dist.ProcessGroup]) – 该阶段将使用的进程组。  

一种可与PipelineSchedules一起使用的管道阶段。  

GPipe调度方案：以“填充-排空”方式处理所有微批次。  
1F1B调度方案：在稳定状态下对微批次分别执行一次正向传播和一次反向传播。  
Interleaved 1F1B调度方案：更多详情请参见https://arxiv.org/pdf/2104.04473。该方案在稳定状态下对微批次分别执行一次正向传播和一次反向传播，并且允许每个进程拥有多个阶段。当多个微批次同时准备好进入多个本地阶段时，Interleaved 1F1B会优先处理较早的微批次（也称为“深度优先”策略）。  

该调度方案与原始论文中的方案十分相似，不同之处在于它放宽了“num_microbatch % pp_size == 0”这一要求。通过flex_pp调度方案，我们有num_rounds = max(1, n_microbatches // pp_group_size)，只要n_microbatches % num_rounds为0，该方案即可正常工作。以下是几个示例：  
pp_group_size = 4，n_microbatches = 10：此时num_rounds = 2，且10 % 2 = 0。  
pp_group_size = 4，n_microbatches = 3：此时num_rounds = 1，且3 % 1 = 0。  

广度优先管道并行方案：更多详情请参见https://arxiv.org/abs/2211.05953。与Interleaved 1F1B类似，Looped BFS也支持每个进程拥有多个阶段。不同之处在于，当多个微批次同时准备好进入多个本地阶段时，Loops BFS会优先处理较早的阶段，并一次性处理所有可用的微批次。  

Interleaved Zero Bubble调度方案：更多详情请参见https://arxiv.org/pdf/2401.10241。该方案在稳定状态下对微批次的输入分别执行一次正向传播和一次反向传播，且允许每个进程拥有多个阶段。它通过权重方面的反向传播来填补管道中的“空洞”。实际上，这正是论文中提出的ZB1P调度方案的具体实现方式。  

Zero Bubble调度方案（ZBV变体）：更多详情请参见https://arxiv.org/pdf/2401.10241的第6节。该调度方案要求每个进程恰好拥有两个阶段。  

该方案在稳定状态下对微批次的输入分别执行一次正向传播和一次反向传播，且允许每个进程拥有多个阶段。它通过权重的反向传播来填补管道中的“空洞”。  

只有当“正向传播时间 == 反向传播时间 且 输入时间 == 反向传播时间 且 权重时间 == 反向传播时间”时，这种ZB-V调度方案才具备“零气泡”特性。在实际模型中，这种情况很少出现，因此也可以为时间不一致的情况实现一种贪婪调度策略。  

DualPipeV调度方案：这是一种基于DeepSeek在https://arxiv.org/pdf/2412.19437中提出的DualPipe方案的更高效变体。该方案基于deepseek-ai/DualPipe项目的开源代码实现。  

单阶段调度方案的基础类，实现了step方法。派生类则需实现_step_microbatches方法。  

根据scale_grads参数的值，梯度会按num_microbatches的倍数进行缩放，默认值为True。此设置应与损失函数loss_fn的配置保持一致——损失函数可能采用平均损失计算方式（scale_grads=True），也可能采用求和损失计算方式（scale_grads=False）。  

使用全批次输入运行一次管道调度方案的迭代过程。该过程会自动将输入分割成微批次，然后根据调度方案的要求依次处理这些微批次。  
args：模型所需的位置参数（与非管道模式相同）。  
kwargs：模型所需的关键字参数（与非管道模式相同）。  
target：损失函数的目标值。  
losses：用于存储每个微批次对应损失值的列表。  

多阶段调度方案的基础类，实现了step方法。  

根据scale_grads参数的值，梯度会按num_microbatches的倍数进行缩放，默认值为True。此设置应与损失函数loss_fn的配置保持一致——损失函数可能采用平均损失计算方式（scale_grads=True），也可能采用求和损失计算方式（scale_grads=False）。  

使用全批次输入运行一次管道调度方案的迭代过程。该过程会自动将输入分割成微批次，然后根据调度方案的要求依次处理这些微批次。  
args：模型所需的位置参数（与非管道模式相同）。  
kwargs：模型所需的关键字参数（与非管道模式相同）。  
target：损失函数的目标值。  
losses：用于存储每个微批次对应损失值的列表。  

---  

## 张量并行 - torch.distributed.tensor.parallel#  

**网址：** https://pytorch.org/docs/stable/distributed.tensor.parallel.html  

**内容：**  
- 张量并行 - torch.distributed.tensor.parallel#  

创建时间：2025年6月13日 | 最后更新时间：2025年6月13日  

张量并行（TP）建立在PyTorch分布式张量（DTensor）[https://github.com/pytorch/pytorch/blob/main/torch/distributed/tensor/README.md]之上，提供了多种并行化风格：列向并行、行向并行以及序列并行。  

张量并行相关的API目前仍处于实验阶段，可能会发生变动。  

使用张量并行对nn.Module进行并行化的入口函数为：  

通过基于用户指定的计划来并行化模块或子模块，从而在PyTorch中实现张量并行。  

我们会根据parallelize_plan来并行化模块或子模块。parallelize_plan中包含ParallelStyle字段，用于指示用户希望如何对模块或子模块进行并行化处理。  

用户还可以为每个模块的全限定名（FQN）指定不同的并行化风格。请注意，parallelize_module仅支持一维的DeviceMesh结构。如果您的DeviceMesh为二维或更高维度，需先将其切分为一维的子DeviceMesh，再传递给该API（即device_mesh["tp"]）。

module（nn.Module）——需要被并行化的模块。

device_mesh（DeviceMesh，可选）——用于描述DTensor对应设备拓扑结构的对象。若未指定，则调用操作必须在DeviceMesh上下文中进行。

parallelize_plan（ParallelStyle或其字典形式，可选）——用于定义模块并行化策略的参数。它可以是包含张量并行化输入/输出处理方式的ParallelStyle对象，也可以是模块全限定名与其对应ParallelStyle对象的字典。若未指定，则当前该操作不会执行任何操作。

src_data_rank（int，可选）——逻辑/全局张量的源数据所在rank，distribute_tensor()函数会利用该参数将数据分片或广播到其他rank。默认情况下，我们会以每个DeviceMesh维度上的group_rank=0作为源数据，以此保留单设备处理的语义。若明确传入None，则parallelize_module()将直接使用本地数据，而不会尝试通过分片/广播来维持单设备语义。默认值为0。

一个已被并行化的nn.Module对象。

对于Attention、MLP层等结构较为复杂的模块，建议将不同的ParallelStyle组合使用（如ColwiseParallel和RowwiseParallel），并将其作为parallelize_plan传递，从而实现所需的计算分片。

Tensor Parallelism支持以下并行化风格：

以列方向对兼容的nn.Module进行分片。目前仅支持nn.Linear和nn.Embedding类型。用户可将其与RowwiseParallel结合使用，以实现更复杂模块（如MLP、Attention）的分片处理。

input_layouts（Placement，可选）——用于指定nn.Module输入张量的DTensor布局，该参数用于将输入张量标记为DTensor类型。若未指定，则默认认为输入张量为已分片形式。

output_layouts（Placement，可选）——用于指定nn.Module输出结果的DTensor布局，旨在确保输出具有用户期望的格式。若未指定，则输出张量将在最后一个维度上被分片。

use_local_output（bool，可选）——是否使用本地的torch.Tensor作为模块输出，而非DTensor。默认值为True。

一种表示对nn.Module按列方向进行分片的ParallelStyle对象。

默认情况下，若未指定output_layouts，ColwiseParallel类型的输出也将在最后一个维度上被分片。对于那些需要特定张量形状的操作（例如在RowwiseParallel之前），需注意：由于输出已被分片，相关操作可能需要进行适配以匹配分片后的尺寸。

以行方向对兼容的nn.Module进行分片。目前仅支持nn.Linear和nn.Embedding类型。用户可将其与ColwiseParallel结合使用，以实现更复杂模块（如MLP、Attention）的分片处理。

input_layouts（Placement，可选）——用于指定nn.Module输入张量的DTensor布局，该参数用于将输入张量标记为DTensor类型。若未指定，则默认认为输入张量将在最后一个维度上被分片。

output_layouts（Placement，可选）——用于指定nn.Module输出结果的DTensor布局，旨在确保输出具有用户期望的格式。若未指定，则输出张量将被复制。

use_local_output（bool，可选）——是否使用本地的torch.Tensor作为模块输出，而非DTensor。默认值为True。

一种表示对nn.Module按行方向进行分片的ParallelStyle对象。

SequenceParallel会复制兼容nn.Module的参数，并在序列维度上对输入数据进行分片后执行并行计算。目前仅支持nn.LayerNorm、nn.Dropout以及RMSNorm的Python实现版本。

该风格实现了论文《Reducing Activation Recomputation in Large Transformer Models》中描述的操作逻辑。

若传入该nn.Module的输入为torch.Tensor，它会假设输入已在序列维度上被分片，随后将其转换为在序列维度上分片的DTensor。而如果输入已经是DTTensor但未在序列维度上分片，该风格会自动重新分配数据，使其在序列维度上完成分片。

该nn.Module的输出也将在序列维度上被分片。

sequence_dim（int，可选）——用于指定nn.Module输入张量的序列维度，该参数用于将输入张量标记为在序列维度上分片的DTensor。默认值为1。

use_local_output（bool，可选）——是否使用本地的torch.Tensor作为模块输出，而非DTensor。默认值为False。

一种表示对nn.Module进行序列并行处理的ParallelStyle对象。

SequenceParallel风格要求，若nn.Module中包含权重参数（如nn.LayerNorm或RMSNorm，这类模块默认采用ones初始化），则必须使用ones初始化方式。如果您为这些模块的权重设置了自定义初始化值，那么在并行化前后需要对这些权重进行广播操作，以确保其被正确复制。

如果您希望仅通过配置nn.Module的输入和输出的DTensor布局，并在必要时重新分配布局，而无需将模块参数转换为DTTensor，可在调用parallelize_module时，在parallelize_plan中使用以下ParallelStyle：

该风格用于根据input_layouts在运行时将nn.Module的输入张量转换为DTTensor，并根据desired_input_layouts进行布局重新分配。

input_layouts（Placement或其元组形式）——用于指定nn.Module输入张量的DTensor布局，该参数用于将输入张量转换为DTTensor类型。如果某些输入并非torch.Tensor或无需转换，可使用None作为占位符。默认值为None。

desired_input_layouts（Placement或其元组形式）——用于指定期望的nn模块输入张量的DTensor布局，旨在确保输入具有所需的格式。该参数的长度必须与input_layouts一致。默认值为None。

input_kwarg_layouts（Dict[str, Placement]）——用于指定nn.Module输入关键字参数的DTensor布局，该参数用于将输入关键字参数张量转换为DTTensor。默认值为None。

desired_input_kwarg_layouts（Dict[str, Placement]）——用于指定期望的nn模块输入关键字参数的DTTensor布局，旨在确保输入关键字参数具有所需的格式。默认值为None。

use_local_output（bool，可选）——是否使用本地的torch.Tensor作为模块输入，而非DTTensor。默认值为False。

一种用于准备nn.Module输入分片布局的ParallelStyle对象。

该风格用于根据output_layouts在运行时将nn.Module的输出张量转换为DTTensor，若输入张量本身已是torch.Tensor则直接转换。如果某些输出并非torch.Tensor或无需转换，可使用None作为占位符。

desired_output_layouts（Placement或其元组形式）——用于指定期望的nn模块输出张量的DTensor布局，旨在确保输出具有所需的格式。

use_local_output（bool，可选）——是否使用本地的torch.Tensor作为模块输出，而非DTTensor。默认值为True。

一种用于准备nn.Module输出分片布局的ParallelStyle对象。

该风格用于根据input_layouts（输入张量布局）和output_layouts（输出张量布局）在运行时将nn.Module的输入张量（及输出张量）转换为DTTensor，随后再根据desired_input_layouts（期望的输入布局）和desired_output_layouts（期望的输出布局）进行布局重新分配。这实际上是PrepareModuleInput与PrepareModuleOutput两种功能的组合。

input_layouts（Placement或其元组形式）——用于指定nn.Module输入张量的DTensor布局，该参数用于将输入张量转换为DTTensor类型。如果某些输入并非torch.Tensor或无需转换，可使用None作为占位符。默认值为None。

desired_input_layouts（Placement或其元组形式）——用于指定期望的nn模块输入张量的DTensor布局，旨在确保输入具有所需的格式。该参数的长度必须与input_layouts一致。默认值为None。

input_kwarg_layouts（Dict[str, Placement]）——用于指定nn.Module输入关键字参数的DTensor布局，该参数用于将输入关键字参数张量转换为DTTensor。默认值为None。

desired_input_kwarg_layouts（Dict[str, Placement]）——用于指定期望的nn模块输入关键字参数的DTensor布局，旨在确保输入关键字参数具有所需的格式。默认值为None。

use_local_input（bool，可选）——是否使用本地的torch.Tensor作为模块输入，而非DTTensor。默认值为False。

output_layouts（Placement或其元组形式）——用于指定nn.Module输出张量的DTensor布局，该参数用于将输入张量转换为DTTensor类型（仅当输入为torch.Tensor时生效）。如果某些输出并非torch.Tensor或无需转换，可使用None作为占位符。

desired_output_layouts（Placement或其元组形式）——用于指定期望的nn模块输出张量的DTTensor布局，旨在确保输出具有所需的格式。

use_local_output（bool，可选）——是否使用本地的torch.Tensor作为模块输出，而非DTTensor。默认值为True。

一种用于准备nn.Module输入和输出分片布局的ParallelStyle对象。

当上述ParallelStyle使用Shard(dim)作为输入/输出布局时，系统会假设输入/输出激活张量已在TP操作的DeviceMesh的dim维度上均匀分片。例如，由于RowwiseParallel期望接收已在最后一个维度上分片的输入，因此它假定输入张量已在该维度上完成均匀分片。对于未均匀分片的激活张量，用户可以直接将DTTensor传递给已分片的模块，并将use_local_output设置为False，这样在每个ParallelStyle处理后仍能保留DTTensor，而DTTensor可用来记录分片的不均匀信息。对于 Transformer 等模型，我们建议用户在 parallelize_plan 中同时使用 ColwiseParallel 和 RowwiseParallel，从而实现整个模型（即 Attention 层和 MLP 层）的理想分片。

通过以下上下文管理器可支持损失函数的并行计算（即损失并行性）：

该上下文管理器能够实现损失并行性，当输入在类别维度上被分片后，即可高效地执行并行损失计算。目前仅支持交叉熵损失函数。

在该上下文管理器内部，用户可以像平常一样使用 cross_entropy() 或 CrossEntropyLoss 函数，但需满足以下关于输入参数的要求。相应的 backward() 调用（如有）也必须在同一上下文管理器内部执行。

- input (DTensor) – 输入的对数概率值。要求已在类别维度上被分片。
- target (Union[torch.Tensor, DTensor]) – 必须为真实类别索引（目前不支持类别概率）。要求已在 DeviceMesh 中复制。
- weight (Union[torch.Tensor, DTensor], optional) – 若提供此参数，则要求其在 DeviceMesh 中被复制。
- label_smoothing – 目前不支持。

此外，还需要一个已被复制的 DTensor。此处手动创建了一个分片后的 DTensor 以演示其用法；在实际应用中，它通常是由 TP 模块生成的输出。
