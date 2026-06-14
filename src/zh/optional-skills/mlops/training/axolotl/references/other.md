# Axolotl - 其他内容

**页数：** 26

---

## 混合精度训练

**URL：** https://docs.axolotl.ai/docs/mixed_precision.html

**目录：**
- 混合精度训练
- 1 FP16混合精度
  - 1.1 概述
  - 1.2 配置
  - 1.3 FP16的注意事项
- 2 BF16混合精度
  - 2.1 概述
  - 2.2 配置
- 3 FP8混合精度
  - 3.1 什么是FP8？

混合精度训练通过使用精度较低的数据类型，在保持模型质量的同时降低内存占用并提升训练速度。Axolotl支持多种混合精度格式：

FP16是传统的半精度格式，老款GPU也支持该格式，但其数值稳定性可能低于BF16。

BF16（Brain Float 16）的数值稳定性优于FP16，是现代GPU推荐的混合精度格式。它在占用一半内存的情况下，仍能提供与FP32相同的动态范围。

FP8功能目前仍处于试验阶段，需要兼容的硬件（如H100、H200）以及支持TorchAO的最新PyTorch版本。

与FP16/BF16相比，FP8（8位浮点数）能够在保持训练稳定性的同时显著节省时间。Axolotl的实现采用了PyTorch的TorchAO库，并结合“张量级”缩放策略。

在YAML配置文件中添加以下内容：

`torch.compile`对提升FP8性能至关重要

若要获得明显的速度提升，FP8训练必须设置`torch_compile: true`。如果不进行编译，FP8的实际运行速度可能会比FP16/BF16更慢，且内存占用也会更高。

对于FSDP（完全分片数据并行）训练：

务必验证您的混合精度配置：

可参考examples/llama-3/3b-fp8-fsdp2.yaml中的优化配置示例。对于参数量相对较小的模型（30亿参数），启用FP8混合精度加上FP8全收集训练，其每秒迭代速度可比BF16快约10%。

如需了解更多关于多GPU训练的信息，请参阅我们的多GPU指南。

**示例：**

示例1（YAML格式）：
```yaml
# Automatic BF16 detection (recommended)
bf16: auto

# Or explicitly enable
bf16: true

# For evaluation with BF16
bf16: full  # Equivalent to bf16_full_eval in the HF trainer
```

示例 2（yaml 格式）：
```yaml
# Enable FP8 mixed precision
fp8: true

# Optional: Enable FP8 for FSDP all-gather operations
fp8_enable_fsdp_float8_all_gather: true

# Enable torch.compile (almost always necessary for FP8 speedups)
torch_compile: true
```

示例 3（yaml 格式）：
```yaml
fp8: true
fp8_enable_fsdp_float8_all_gather: true

torch_compile: true

# FSDP configuration
fsdp_version: 2
fsdp_config:
  offload_params: false
  cpu_ram_efficient_loading: true
  auto_wrap_policy: TRANSFORMER_BASED_WRAP
  transformer_layer_cls_to_wrap: LlamaDecoderLayer
  state_dict_type: FULL_STATE_DICT
  reshard_after_forward: true
```

## 常见问题解答

**网址：** https://docs.axolotl.ai/docs/faq.html

**目录：**
- 常见问题解答
  - 通用问题
  - 聊天模板相关问题

问：训练过程已停止数分钟，没有进展。

答：这通常是 GPU 之间通信出现问题的表现。请参阅 NCCL 相关文档。

答：这种情况通常发生在系统内存不足时。

问：使用 deepspeed 时出现 exitcode: -7 的错误。

答：尝试通过 `pip install -U deepspeed` 升级 deepspeed。

问：出现 AttributeError: ‘DummyOptim’ object has no attribute ‘step’ 的错误。

问：使用 deepspeed 且仅配备单个 GPU 时出现 ModuleNotFoundError: No module named ‘mpi4py’ 的错误。

答：您可能正在单 GPU 环境下使用 deepspeed。请删除 YAML 文件中的 deepspeed 配置部分，或取消使用 --deepspeed CLI 参数。

问：代码在保存预处理后的数据集时卡住了。

答：这通常是 GPU 问题导致的。可以通过设置操作系统环境变量 CUDA_VISIBLE_DEVICES=0 来解决。如果您在 RunPod 平台上运行，问题则出在虚拟节点上，启动新的虚拟节点通常可以解决问题。

问：在合并适配器或加载适配器时出现错误，提示检查点的 torch.Size 与模型不匹配。

答：这很可能是词汇表大小不一致导致的。默认情况下，如果分词器的标记数量多于模型本身的嵌入维度，Axolotl 会自动扩展模型的嵌入向量。请使用 axolotl merge-lora 命令来合并适配器，而非自行编写脚本。

另一方面，如果模型的标记数量多于分词器，除非在配置中设置了 shrink_embeddings: true，否则 Axolotl 不会缩小模型的嵌入向量。

问：如何通过自定义 Python 脚本调用 Axolotl？

答：由于 Axolotl 本质上是基于 Python 开发的，您可以查看 src/axolotl/cli/main.py 文件，了解各命令的调用方式。

问：如何确定 fsdp_transformer_layer_cls_to_wrap 应设置的值？

答：该参数表示需要用 FSDP 包装的 Transformer 层的类名。例如，对于 LlamaForCausalLM，对应的值为 LlamaDecoderLayer。要确定特定模型的对应值，请查看该模型的 PreTrainedModel 定义，并在 transformers 库中的 modeling_<model_name>.py 文件中查找 _no_split_modules 变量。

问：出现 ValueError: Asking to pad but the tokenizer does not have a padding token. Please select a token to use as pad_token 的错误。

答：这是因为分词器中没有填充标记。请通过相应方式向分词器中添加填充标记。

问：使用 preprocess CLI 时出现 IterableDataset 错误或 KeyError: 'input_ids' 的错误。

答：这可能是由于您在调用 preprocess CLI 时同时设置了 pretraining_dataset: 参数或 skip_prepare_dataset: true 参数导致的。建议直接使用 axolotl train CLI 命令，因为这些数据集是按需准备的。

问：vLLM 与 Axolotl 不兼容。

答：目前我们推荐使用 torch 2.6.0 版本搭配 vllm。请确保使用正确的版本。在 Docker 环境下，请使用 main-py3.11-cu124-2.6.0 标签版。

问：在 CUDA 12.4 环境下使用 FA2 2.8.0 时出现未定义符号的运行时错误。

答：这似乎是 FA2 2.8.0 在 CUDA 12.4 环境下的 wheel 包存在问题。建议尝试使用 CUDA 12.6 版本，或降级到 FA2 2.7.4 版本。相关问题可参考上游仓库的记录：https://github.com/Dao-AILab/flash-attention/issues/1717。

问：在 VLM 训练中能否混合使用文本数据集和文本+图像数据集？

答：可以，对于较新的 VLM 架构而言这是可行的。不过 LLaVA / Pixtral 架构则不支持此功能。如果您发现某些架构无法正常工作，请及时告知我们！

问：为什么显示的内存/最大内存值与 nvidia-smi 的显示不一致？

答：我们是通过 torch API 获取这些信息的。更多相关信息可查看 https://docs.pytorch.org/docs/stable/notes/cuda.html#cuda-memory-management。

问：出现 jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'content' / 'role' / ____ 的错误。

答：这意味着在构建聊天模板提示时，所指定的属性对应的映射配置并不存在。例如，如果缺少 content 属性，请检查是否已在 message_property_mappings 中为 content 添加了正确的映射配置。

问：第 ___ 轮生成的模板为空。

答：表示该轮的对话内容为空。

问：无法检测到第 __ 轮的内容起始/结束边界。

答：未能识别出该特定轮次的起始和结束位置。请确保在聊天模板中设置了 eos_token。否则，可能是该聊天模板没有为每一轮（包括系统消息轮次）设置正确的边界。极少数情况下，也请检查您的内容是否为 [[dummy_message]] 格式。如有此类问题，请及时告知我们。

问：第 ___ 轮的内容结束边界位于起始边界之前。

答：这是一种本不应出现的异常情况。如果遇到此问题，请创建工单反馈。

问：第 __ 轮的内容结束边界与起始边界重合。这很可能是空轮次。

答：这很可能是空轮次导致的。

问：EOS 标记被错误地屏蔽了，或者根本没有被屏蔽，/ 聊天模板中找不到 EOS 标记 __。

答：出现这种情况可能有两个原因：

问：“chat_template 选项设置为 tokenizer_default，但分词器的 chat_template 为 null。请在分词器配置中添加聊天模板。”

答：这是因为分词器中没有配置聊天模板。请在分词器配置中添加聊天模板，详情可参考 chat_template 相关说明。

问：EOT 标记被错误地屏蔽了，或者根本没有被屏蔽，/ 聊天模板中找不到 EOT 标记 __。

答：出现这种情况可能有两个原因：

问：EOT 标记的编码失败。请检查该标记是否有效且可被编码。

答：可能是分词器或 Unicode 编码存在问题。请附上导致问题的 EOT 标记及分词器的示例，然后提交工单反馈。

问：EOT 标记 __ 被编码成了多个独立的标记。

答：这是因为 EOT 标记被拆分为多个标记，从而导致异常行为。建议将其添加到 tokens: 配置项中，或者（更推荐的方式）通过 added_tokens_overrides: 参数覆盖那些未被使用的额外标记。

问：train_on_eos 与 train_on_eot 参数之间存在冲突。eos_token 被包含在 eot_tokens 中，且 train_on_eos 的值与 train_on_eot 不一致。

答：这是由于 EOS 标记被列入了 eot_tokens: 列表中，同时 train_on_eos: 与 train_on_eot: 的设置不一致，导致其中一个参数会覆盖另一个。请确保 train_on_eos: 与 train_on_eot: 的值保持一致，或者从 eot_tokens: 中移除 EOS 标记。

问：如果未提供 eot_tokens: 参数，会发生什么？

答：如果未指定 eot_tokens: 参数，其默认行为与之前相同。用于分隔各轮对话的 EOS 标记是否被屏蔽，将取决于该轮对话是否需要参与训练。

在内部实现中，eot_tokens: 对应 tokenizer.eos_token，而 train_on_eot: 对应 train_on_eos（默认值为 turn）。这样的命名方式有助于更清晰地理解 EOT/EOS 标记的用途及行为逻辑。

问：数据处理时出现错误：CAS 服务故障。

答：可以尝试通过 export HF_HUB_DISABLE_XET=1 的命令禁用 XET 功能。

问：出现 torch._inductor.exc.LoweringException: NoValidChoicesError: No choices to select 的错误。请考虑在 torch/_inductor/config.py 文件中定义的 max_autotune_gemm_backends 配置中添加 ATEN，以便至少保留一个可选的后端。

答：根据所使用的 torch 版本不同，您可能需要在 YAML 配置文件中加入相关设置：

**问：出现 ValueError("Backward pass should have cleared tracker of all tensors") 的错误。**

答：这可能是由于在 CUDA 流中使用现代的 OffloadActivations 上下文管理器时出现了异常情况。如果遇到此错误，您可以尝试在 YAML 配置文件中启用 legacy 模式的 offload_activations: 参数，使用较为基础的实现方式。

**问：出现 Error parsing tool_calls arguments as JSON 的错误。**

答：这是将字符串形式的参数解析为字典时出现的错误。请检查您的数据集及错误信息以获取更多详情。

**示例：**

示例 1（yaml 格式）：
```yaml
special_tokens:
  # str. If you're not sure, set to same as `eos_token`.
  pad_token: "..."
```

示例 2（yaml 格式）：
```yaml
flex_attn_compile_kwargs:
  dynamic: false
  mode: max-autotune-no-cudagraphs
```

## 安装指南

**网址：** https://docs.axolotl.ai/docs/installation.html

**目录结构：**
- 安装
- 1 预备要求
- 2 安装方法
  - 2.1 通过 PyPI 安装（推荐）
  - 2.2 使用 uv 安装
  - 2.3 Edge/开发版本构建
  - 2.4 Docker 安装
- 3 云环境部署
  - 3.1 云端 GPU 提供商
  - 3.2 Google Colab

本指南涵盖了在各种环境中安装并配置 Axolotl 的所有方法。

请确保在本地环境安装 Axolotl 之前已安装 PyTorch。相关安装说明请参阅：https://pytorch.org/get-started/locally/。对于 Blackwell 系列 GPU，需使用 PyTorch 2.7.0 和 CUDA 12.8 版本。

我们使用 `--no-build-isolation` 参数来检测已安装的 PyTorch 版本（如果存在），以避免覆盖原有版本，并据此选择与特定 PyTorch 版本或其他已安装依赖项相匹配的正确依赖包。

uv 是一款基于 Rust 开发的快速、可靠的 Python 包安装与管理工具。相比 pip，它具有更出色的性能表现和更完善的依赖解析能力，非常适合用于复杂的开发环境。如未安装，请先安装 uv。

选择要与 PyTorch 配合使用的 CUDA 版本（例如 cu124、cu126、cu128），随后创建虚拟环境并激活它。

安装 PyTorch——推荐使用版本 2.6.0。

通过 PyPI 安装 axolotl。

如需获取版本发布间的最新功能更新：

如需使用 Docker 进行开发：

对于 Blackwell 系列 GPU，建议使用 `axolotlai/axolotl:main-py3.11-cu128-2.7.0` 版本，或云环境专用版本 `axolotlai/axolotl-cloud:main-py3.11-cu128-2.7.0`。有关可用 Docker 镜像的更多信息，请参阅 Docker 文档。

对于支持 Docker 的服务提供商：

关于 Mac 系统特有的问题，请参阅第 6 节内容。

我们推荐使用 WSL2（Windows 子系统 Linux）或 Docker 进行安装。

PyTorch 安装地址：https://pytorch.org/get-started/locally/

（可选）登录 Hugging Face 账户：

如果遇到安装问题，可查阅我们的常见问题解答及调试指南。

**示例：**

示例 1（bash 命令行）：
```bash
pip3 install -U packaging setuptools wheel ninja
pip3 install --no-build-isolation axolotl[flash-attn,deepspeed]
```

示例 2（bash）：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

示例 3（bash）：
```bash
export UV_TORCH_BACKEND=cu126
uv venv --no-project --relocatable
source .venv/bin/activate
```

示例 4（bash）：
```bash
uv pip install packaging setuptools wheel
uv pip install torch==2.6.0
uv pip install awscli pydantic
```

## 数据集预处理

**URL:** https://docs.axolotl.ai/docs/dataset_preprocessing.html

**目录:**
- 数据集预处理
- 概述
  - 预处理有哪些优势？
  - 存在哪些边缘情况？

数据集预处理是 Axolotl 根据您配置的每个数据集以及数据集格式和提示词策略来执行的步骤：

数据集的处理可以通过两种方式进行：

在交互式训练或批量训练时（例如您频繁重启训练器），数据集的处理速度往往慢得令人沮丧。预处理功能会根据相关训练参数的哈希值对已分词/格式化的数据集进行缓存，从而在可能的情况下智能地从缓存中调取数据。

缓存路径由 `dataset_prepared_path` 控制：在示例 YAML 文件中该参数通常留空，因为这样能实现更可靠的解决方案，避免意外重复使用缓存数据。

如果未设置 `dataset_prepared_path`，则在训练过程中处理后的数据集将缓存在默认路径 `./last_run_prepared/` 中，同时会忽略该路径中已存在的缓存数据。若明确将 `dataset_prepared_path` 设置为 `./last_run_prepared`，训练器就会使用缓存中的预处理数据。

假设您正在编写自定义的提示词策略或使用用户定义的提示词模板。由于训练器无法轻易检测到这些变化，因此我们无法更改预处理数据集的哈希值。

如果您已设置了 `dataset_prepared_path`，但随后更改了提示词模板逻辑，训练器可能无法识别这些变更，从而导致继续使用旧版本的提示词进行训练。

---

## 推理与合并

**URL:** https://docs.axolotl.ai/docs/inference.html

**目录:**
- 推理与合并
- 1 快速入门
  - 1.1 基本推理
- 2 进阶用法
  - 2.1 Gradio 界面
  - 2.2 基于文件的提示词
  - 2.3 内存优化
- 3 合并 LoRA 权重
  - 3.1 合并时的内存管理
- 4 分词处理

本指南介绍了如何使用已训练好的模型进行推理，内容包括模型加载、交互式测试、适配器合并以及常见的故障排查方法。

在推理/合并操作中，请使用与训练时相同的配置。

启动交互式网页界面：

从文本文件处理提示词：

针对大型模型或内存受限的情况：

将 LoRA 适配器与基础模型合并：

训练阶段与推理阶段的分词方式不一致是常见问题之一。

在将数据输入模型之前，通过解码令牌来验证推理阶段的分词情况

比较训练阶段与推理阶段的令牌 ID

在 YAML 文件中配置特殊令牌：

更多详情请参阅我们的调试指南。

**示例:**

示例 1（bash）：
```bash
axolotl inference your_config.yml --lora-model-dir="./lora-output-dir"
```

示例 2（bash）：
```bash
axolotl inference your_config.yml --base-model="./completed-model"
```

示例 3（bash）：
```bash
axolotl inference your_config.yml --gradio
```

示例 4（bash）：
```bash
cat /tmp/prompt.txt | axolotl inference your_config.yml \
  --base-model="./completed-model" --prompter=None
```

## 多模态/视觉语言模型（测试版）

**网址：** https://docs.axolotl.ai/docs/multimodal.html

**目录结构：**
- 多模态/视觉语言模型（测试版）
- 支持的模型
- 使用方法
  - Mllama
  - Llama4
  - Pixtral
  - Llava-1.5
  - Mistral-Small-3.1
  - Magistral-Small-2509
  - Voxtral

目前多模态功能尚处于有限支持阶段，功能完整性尚未达到完整版本的标准。

以下是微调多模态模型时所需的超参数。完整的配置文件可在示例文件夹中查看。

我们已对部分聊天模板进行了扩展，以支持更多类型的数据集。此举不会影响现有配置的正常使用。

目前系统不会根据序列长度截断或丢弃样本，因为不同架构处理非文本令牌的方式各不相同。我们正在寻求相关帮助。

请务必通过以下命令安装视觉处理库：`pip install 'mistral-common[opencv]==1.8.5'`

请务必通过以下命令安装音频处理库：`pip3 install librosa==0.11.0 'mistral_common[audio]==1.8.3'`

Gemma3-1B模型为纯文本模型，因此需按常规文本模型方式进行训练。

对于4B/12B/27B规模的多模态模型，请使用以下配置文件：

模型初始的损失值和梯度范数会非常高，我们推测这是由于视觉层中的卷积操作所致。

请务必通过以下命令安装Timm库：`pip3 install timm==1.0.17`

请务必通过以下命令安装num2words库：`pip3 install num2words==0.5.14`

请通过以下命令卸载causal-conv1d库：`pip3 uninstall -y causal-conv1d`

对于多模态数据集，我们采用了类似OpenAI Message格式的扩展版聊天模板。

为保持向后兼容性：

在加载图像时，可在content字段中除了添加"type": "image"之外，再使用以下键值：

在加载音频时，可在content字段中除了添加"type": "audio"之外，再使用以下键值：

您可能需要通过以下命令安装librosa库：`pip3 install librosa==0.11.0`

该功能目前尚未经过充分测试，欢迎有能力的用户参与完善！

在加载视频时，可在content字段中除了添加"type": "video"之外，再使用以下键值：

以下是一个多模态数据集的示例：

PIL工具使用requests库尝试从指定网址获取文件时失败。请检查网址是否存在拼写错误，另一种可能是请求被服务器拦截了。

**示例：**

示例1（yaml格式）：
```yaml
processor_type: AutoProcessor

skip_prepare_dataset: true
remove_unused_columns: false  # leave columns in place as they are needed to handle image embeddings during training
sample_packing: false  # not yet supported with multimodal

chat_template:  # see in next section if specified

# example dataset
datasets:
  - path: HuggingFaceH4/llava-instruct-mix-vsft
    type: chat_template
    split: train[:1%]

# (optional) if doing lora, only finetune the Language model,
# leave the vision model and vision tower frozen
# load_in_8bit: true
adapter: lora
lora_target_modules: 'model.language_model.layers.[\d]+.(mlp|cross_attn|self_attn).(up|down|gate|q|k|v|o)_proj'

# (optional) if you want to resize images to a set size
image_size: 512
image_resize_algorithm: bilinear
```

示例 2（yaml 格式）：
```yaml
base_model: meta-llama/Llama-3.2-11B-Vision-Instruct

chat_template: llama3_2_vision
```

示例 3（yaml 格式）：
```yaml
base_model: meta-llama/Llama-4-Scout-17B-16E-Instruct

chat_template: llama4
```

示例 4（yaml 格式）：
```yaml
base_model: mistralai/Pixtral-12B-2409

chat_template: pixtral
```

## 奖励建模

**URL:** https://docs.axolotl.ai/docs/reward_modelling.html

**目录:**
- 奖励建模
  - 概述
  - 结果型奖励模型
  - 过程型奖励模型（PRM）

奖励建模是一种用于训练模型以预测给定输入的奖励或价值的技术。在强化学习场景中，当模型需要评估自身行为或预测的质量时，该技术尤为有用。我们支持 trl 所提供的所有奖励建模技术。

结果型奖励模型是使用包含用户与模型之间整个交互过程偏好标注的数据进行训练的（而非针对单次轮次或单步数据）。为提升训练稳定性，您可以使用 `center_rewards_coefficient` 参数来促使奖励输出的平均值为零（详见 TRL 文档）。

Bradley-Terry 聊天模板要求采用以下格式的单轮对话：

欢迎阅读我们的 PRM 博客文章。

过程型奖励模型则是使用包含一系列交互中每一步偏好标注的数据进行训练的。通常，PRM 会被训练为在推理过程的每一步提供奖励信号，进而用于后续的强化学习任务。

有关数据集格式的更多详细信息，请参阅 `stepwise_supervised` 部分。

**示例:**

示例 1（yaml 格式）：
```yaml
base_model: google/gemma-2-2b
model_type: AutoModelForSequenceClassification
num_labels: 1
tokenizer_type: AutoTokenizer

reward_model: true
chat_template: gemma
datasets:
  - path: argilla/distilabel-intel-orca-dpo-pairs
    type: bradley_terry.chat_template

val_set_size: 0.1
eval_steps: 100
```

示例 2（JSON格式）：
```json
{
    "system": "...", // optional
    "input": "...",
    "chosen": "...",
    "rejected": "..."
}
```

示例 3（yaml 格式）：
```yaml
base_model: Qwen/Qwen2.5-3B
model_type: AutoModelForTokenClassification
num_labels: 2

process_reward_model: true
datasets:
  - path: trl-lib/math_shepherd
    type: stepwise_supervised
    split: train

val_set_size: 0.1
eval_steps: 100
```

## RLHF（测试版）

**URL:** https://docs.axolotl.ai/docs/rlhf.html

**目录:**
- RLHF（测试版）
- 概述
- 使用 Axolotl 进行 RLHF
  - DPO
    - chatml.argilla
    - chatml.argilla_chat
    - chatml.icr
    - chatml.intel
    - chatml.prompt_pairs
    - chatml.ultra

基于人类反馈的强化学习是一种利用人类反馈对语言模型进行优化的技术。其实现方法多种多样，包括但不限于：

此为测试版功能，许多特性尚未完全实现。我们鼓励大家提交新的 Pull Request 以进一步完善该功能的集成度与性能。

我们在实现各类 RL 训练方法时依赖 TRL 库，并通过封装将其集成到 axolotl 中。每种方法都有各自支持的数据集加载方式及提示词格式。

您可以通过访问 src/axolotl/prompt_strategies/{method} 查看每种方法支持的功能，其中 {method} 表示我们支持的某一种方法。具体类型信息可通过 {method}.{function_name} 获取。

DPO 支持以下类型，并采用相应的数据集格式：

对于自定义行为，

输入格式为简单的 JSON 格式，可根据上述配置自定义字段内容。

由于 IPO 仅是具有不同损失函数的 DPO，因此 DPO 所支持的所有数据集格式也适用于 IPO。

相关论文：https://arxiv.org/abs/2403.07691

ORPO 支持以下类型，并采用相应的数据集格式：

KTO 支持以下类型，并采用相应的数据集格式：

对于自定义行为，

输入格式为简单的 JSON 格式，可根据上述配置自定义字段内容。

欢迎查阅我们的 GRPO 实现指南。

在最新的 GRPO 实现版本中，我们使用了 vLLM 来显著加快训练过程中的轨迹生成速度。在此示例中，我们使用了 4 块 GPU——2 块用于训练，2 块用于运行 vLLM：

请确保在安装 axolotl 时通过附加参数的方式安装正确版本的 vLLM，例如：pip install axolotl[vllm]。

此时您的 vLLM 实例将会开始启动，接下来就可以利用剩余的 2 块 GPU 开始训练了。在另一个终端中执行相应命令：

由于 TRL 是基于 vLLM 实现的，因此 vLLM 实例必须使用最后 N 块 GPU，而非最前面的 N 块 GPU。这就是为什么在上面的示例中，我们为 vLLM 实例设置了 CUDA_VISIBLE_DEVICES=2,3。

GRPO 需要使用自定义的奖励函数及转换逻辑，请确保这些文件已提前准备好。

例如，要加载 OpenAI 的 GSM8K 数据集并使用随机奖励来评估完成度：

如需查看更多自定义奖励函数的示例，请参阅 TRL GRPO 文档。

所有配置信息请参见 TRLConfig。

DAPO 论文以及后续的 Dr. GRPO 论文提出了另一种损失函数，用于解决 GRPO 在生成较长回复时出现的惩罚问题。

更多详情请参阅 GRPO 文档。

SimPO 采用 CPOTrainer，但使用了不同的损失函数。

该方法的数据集格式与 DPO 相同。

TRL 支持针对那些依赖参考模型的 RL 训练范式自动解包 PEFT 模型。这样一来无需加载额外的参考模型，从而大大降低了内存压力；同时通过禁用 PEFT 适配器即可获取参考模型的对数概率，该功能默认处于开启状态。如需关闭该功能，请传递以下配置参数：

**示例:**

示例 1（yaml 格式）：
```yaml
rl: dpo
datasets:
  - path: Intel/orca_dpo_pairs
    split: train
    type: chatml.intel
  - path: argilla/ultrafeedback-binarized-preferences
    split: train
    type: chatml
```

示例 2（JSON格式）：
```json
{
    "system": "...", // optional
    "instruction": "...",
    "chosen_response": "...",
    "rejected_response": "..."
}
```

示例 3（JSON格式）：
```json
{
    "chosen": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ],
    "rejected": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}
```

示例 4（JSON格式）：
```json
{
    "system": "...", // optional
    "input": "...",
    "chosen": "...",
    "rejected": "..."
}
```

## LoRA 优化方案

**网址：** https://docs.axolotl.ai/docs/lora_optims.html

**目录：**
- LoRA 优化方案
- 使用方法
- 系统要求
- 实现细节
  - 自定义自动求导函数
  - Triton 核函数
  - 集成方式
- 后续计划

受 Unsloth 的启发，我们为 LoRA 和 QLoRA 微调实现了两项优化，支持单 GPU 以及多 GPU（包括 DDP、DeepSpeed 和 FSDP2 模式）训练环境。这些优化包括：(1) SwiGLU 和 GEGLU 激活函数的 Triton 核函数，以及 (2) LoRA MLP 和注意力层的自定义自动求导函数。我们的目标是通过操作符融合和张量复用，在计算的前向和反向传播过程中提升速度并降低内存占用。

目前我们支持多种常见的模型架构，包括但不限于：

由于受注意力块拼接策略的限制，我们目前支持的模型范围仍较为有限。该策略要求查询/键/值及输出投影部分使用特定的代码模块，具体实现见 `axolotl.kernels.lora` 模块中的 `apply_qkv` 和 `apply_o` 函数。我们欢迎大家测试其他模型架构，或提交 Pull Request 以扩展拼接逻辑，使其能支持更多模型架构。

欢迎阅读我们的 LoRA 优化方案相关博客文章。

您可以在 Axolotl 的配置 YAML 文件中启用这些优化功能。`lora_mlp_kernel` 选项用于启用优化的 MLP 计算路径，而 `lora_qkv_kernel` 和 `lora_o_kernel` 分别用于启用融合后的查询-键-值投影功能以及优化的输出投影功能。

目前，LoRA 核函数仅支持 SFT 训练，不支持 RLHF 训练。

那些已预置了 LoRA 适配器、但使用了 Dropout 或偏置项的模型，若要正常使用，可能需要先移除这些特性后再进行微调。

LoRA MLP 自动求导函数会对整个 MLP 计算路径进行优化。它将 LoRA 权重与基础权重 的计算过程合并在一起，从而为整个 MLP 块提供高效的单次反向传播计算。

对于注意力组件，我们也通过专门的函数实现了类似的优化——一个函数负责处理查询、键和值投影，另一个函数负责处理输出投影。这些函数通过一定的代码修改机制，与现有的 Transformer 注意力实现相互配合。

我们还为 SwiGLU 和 GeGLU 两种激活函数实现了 Triton 核函数，以此提升计算速度和内存效率。这些核函数同时支持前向传播和反向传播的计算。

自定义自动求导函数与 Triton 核函数是协同工作的。自动求导函数负责管理高级计算流程和梯度追踪，同时调用 Triton 核函数来执行激活函数计算。在反向传播过程中，核函数会同时计算激活函数输出值及所需的梯度，随后自动求导函数会利用这些梯度来计算整个计算路径的最终梯度。

**示例：**

示例 1（Python）：
```python
ORIGINAL_QKV_CODE = """
    query_states = self.q_proj(hidden_states).view(hidden_shape).transpose(1, 2)
    key_states = self.k_proj(hidden_states).view(hidden_shape).transpose(1, 2)
    value_states = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)
""".lstrip(
    "\n"
)

ORIGINAL_O_CODE = """
    attn_output = self.o_proj(attn_output)
""".lstrip(
    "\n"
)
```

示例 2（Python）：
```python
PATCHED_QKV_CODE = """
    query_states, key_states, value_states = self.apply_qkv(hidden_states)
    query_states = query_states.view(hidden_shape).transpose(1, 2)
    key_states = key_states.view(hidden_shape).transpose(1, 2)
    value_states = value_states.view(hidden_shape).transpose(1, 2)
""".lstrip(
    "\n"
)

PATCHED_O_CODE = """
    attn_output = self.apply_o(attn_output)
""".lstrip(
    "\n"
)
```

示例 3（yaml 格式）：
```yaml
lora_mlp_kernel: true
lora_qkv_kernel: true
lora_o_kernel: true
```

## 使用 torchao 进行量化

**URL:** https://docs.axolotl.ai/docs/quantize.html

**目录:**
- 使用 torchao 进行量化
- 在 Axolotl 中配置量化

量化是一种用于降低模型内存占用的技术，但可能会以牺牲精度或模型性能为代价。我们支持使用 torchao 库对模型进行量化。目前，该功能既支持训练后的量化（PTQ），也支持量化感知训练（QAT）。

目前我们暂不支持 GGUF/GPTQ、EXL2 等量化技术。

量化配置是通过配置文件中的量化密钥来实现的。

量化完成后，量化的模型将保存在 {output_dir}/quantized 目录下。

对于通过 QAT 训练得到的模型，您也可以使用 `quantize` 命令对其进行量化——只需使用训练该模型时所用的现有 QAT 配置文件即可：

这样就能确保使用与训练时完全相同的量化配置来处理模型。

如果您已通过 `hub_model_id` 配置了将模型推送到模型中心的功能，那么您的模型中心名称将会附加量化标识，例如：axolotl-ai-cloud/qat-nvfp4-llama3B 会变为 axolotl-ai-cloud/qat-nvfp4-llama3B-nvfp4w

**示例:**

示例 1（yaml 格式）：
```yaml
base_model: # The path to the model to quantize.
quantization:
  activation_dtype: # Optional[str] = "int8". Fake quantization layout to use for activation quantization. Valid options are "int4", "int8", "float8"
  weight_dtype: # Optional[str] = "int8". Fake quantization layout to use for weight quantization. Valid options are "int4", "fp8", and "nvfp4".
  group_size: # Optional[int] = 32. The number of elements in each group for per-group fake quantization
  quantize_embedding: # Optional[bool] = False. Whether to quantize the embedding layer.

output_dir:  # The path to the output directory.
```

示例 2（yaml 格式）：
```yaml
# qat.yml
qat:
  activation_dtype: int8
  weight_dtype: int4
  group_size: 256

output_dir: # The path to the output directory used during training where the final checkpoint has been saved.
```

示例 3（bash）：
```bash
axolotl quantize qat.yml
```

## NCCL

**URL:** https://docs.axolotl.ai/docs/nccl.html

**目录:**
- NCCL

NVIDIA NCCL 是一个用于实现并优化多 GPU 间通信操作的库，这些操作包括广播、全收集、归约、全归约等。总体而言，NCCL 的配置高度依赖于具体环境，需通过多个环境变量来进行设置。一个常见的 NCCL 相关问题是长时间运行的操作会超时，从而导致训练过程中断。

通常，这种超时会在 30 分钟（默认设置）后发生。在出现错误之前，GPU 的利用率接近 100%，但功耗却低于正常水平。如果系统支持，Nvidia 建议关闭 PCI 访问控制服务（ACS）作为解决方案之一。

强制通过 NVLink 进行跨 GPU 通信可能有助于避免超时现象。要确认配置是否使用了 NVLink，可运行以下命令：

若要强制 NCCL 使用 NVLink，只需在环境变量中设置相应值即可：

如果您的环境中没有 NVLink，下表提供了其他可选的 NCCL_P2P_LEVEL 设置值：

为验证训练任务的数据传输速度是否达到预期，运行 NCCL 测试有助于找出瓶颈，例如：

在调试 NCCL 通信超时问题时，在 PyTorch 和 NCCL 中启用更详细的日志记录会很有帮助：

最后，如果您认为训练任务需要更多时间，可以通过在 Axolotl 配置中设置 ddp_timeout 值来将超时时间延长至 30 分钟以上。有关该参数的详细说明，请参阅 PyTorch 的 init_process_group 文档。

**示例:**

示例 1（未知）：
```unknown
Watchdog caught collective operation timeout: WorkNCCL(SeqNum=42, OpType=ALLGATHER, Timeout(ms)=1800000) ran for 1806948 milliseconds before timing out.
```

示例 2（bash）：
```bash
nvidia-smi nvlink --status
```

示例 3（bash）：
```bash
export NCCL_P2P_LEVEL=NVL
```

示例 4（bash）：
```bash
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 3
```

## 多节点训练

**URL:** https://docs.axolotl.ai/docs/multi-node.html

**目录:**
- 多节点训练
- Accelerate
- Raytrain
- Torchrun
  - 方案1：使用带启动参数的新版 Axolotl CLI（推荐）
  - 方案2：直接使用 torchrun（旧版本）

以下是在 Axolotl 中进行多节点训练的三种方法。

每台机器都需要安装一份 Axolotl，建议使用相同的代码版本以确保兼容性。

此外，每台机器上的模型配置文件也需保持一致。

需确保其他机器能够访问主机器。

您需要为 Accelerate 创建配置，要么按照相关说明使用 Accelerate 的配置文件，要么直接使用以下预置配置之一：

~/.cache/huggingface/accelerate/default_config.yaml

在 Axolotl 的 YAML 配置中设置模型使用 FSDP。例如：

现在您只需像平常一样在每台机器上通过 Accelerate 启动程序，一旦所有机器上的 Accelerate 都启动完毕，训练进程就会开始。

关于 Raytrain 的更多信息，请参阅此处文档。

如果您使用的是 Infiniband 网络，建议使用 torchrun 以充分利用带宽。

设置以下环境变量（请根据您的系统调整 buffersize 和 socketname）：

在每台节点上运行以下命令：

请务必替换掉占位符变量。

推荐使用新的 CLI 方案（方案1），因为它能实现一致的参数处理方式，并且能与 Axolotl CLI 的其他功能无缝配合。

有关可用配置的更多信息，可查看 Pytorch 的官方文档。

**示例:**

示例1（YAML格式）：
```yaml
compute_environment: LOCAL_MACHINE
debug: false
distributed_type: FSDP
downcast_bf16: 'no'
machine_rank: 0 # Set to 0 for the main machine, increment by one for other machines
main_process_ip: 10.0.0.4 # Set to main machine's IP
main_process_port: 5000
main_training_function: main
mixed_precision: bf16
num_machines: 2 # Change to the number of machines
num_processes: 4 # That's the total number of GPUs, (for example: if you have 2 machines with 4 GPU, put 8)
rdzv_backend: static
same_network: true
tpu_env: []
tpu_use_cluster: false
tpu_use_sudo: false
use_cpu: false
```

示例 2（yaml 格式）：
```yaml
fsdp_version: 2
fsdp_config:
  offload_params: true
  state_dict_type: FULL_STATE_DICT
  auto_wrap_policy: TRANSFORMER_BASED_WRAP
  transformer_layer_cls_to_wrap: LlamaDecoderLayer
  reshard_after_forward: true
```

示例 3（bash）：
```bash
export NCCL_IB_DISABLE=0
export NCCL_SOCKET_IFNAME="eth0,en,eth,em,bond"
export NCCL_BUFFSIZE=2097152
```

示例 4（bash）：
```bash
axolotl train config.yaml --launcher torchrun -- --nnodes $num_nodes --nproc_per_node $gpu_per_node --rdzv_id $rdzv_id --rdzv_backend c10d --rdzv_endpoint "$head_node_ip:$head_node_port"
```

## 数据集加载

**URL:** https://docs.axolotl.ai/docs/dataset_loading.html

**目录结构：**
- 数据集加载
- 概述
- 加载数据集
  - 本地数据集
    - 文件
    - 目录
      - 加载整个目录
      - 加载目录中的特定文件
  - HuggingFace Hub
    - 上传的文件夹

根据数据集的保存方式（文件扩展名）及存储位置，可通过多种不同的方式加载数据集。

我们使用 `datasets` 库来加载数据集，并结合 `load_dataset` 和 `load_from_disk` 函数来实现加载功能。

您可能会注意到 `load_dataset` 与配置文件中的 `datasets` 部分存在名称相似的配置项。无需被这些众多的选项吓到，其中很多都是可选的。实际上，最常用的配置仅为 `path`，有时还会用到 `data_files`。

该配置方式与 `datasets.load_dataset` 的 API 相一致，因此如果您熟悉该 API，使用起来会得心应手。

关于 HuggingFace 中不同类型数据集的加载指南，请点击此处查看。

有关配置的详细信息，请参阅 `config-reference.qmd` 文件。

您可以在配置文件中的 `datasets` 下设置多个数据集条目。

要加载 JSON 文件，可按如下方式操作：

对应的配置如下所示：

从上面的示例可以看出，只需指定文件或目录的路径以及 `ds_type` 即可加载数据集。此方法适用于 CSV、JSON、Parquet 和 Arrow 格式的文件。

如果路径指向的是文件且未指定 `ds_type`，系统会自动根据文件扩展名推断数据集类型，因此您也可以省略 `ds_type`。

如果要加载整个目录，只需指定该目录的路径即可。此时您有两大选择：

无需添加任何额外的配置项。系统将按以下顺序尝试加载：
- 使用 `datasets.save_to_disk` 保存的数据集
- 加载整个文件目录（例如包含 Parquet/Arrow 文件的目录）

如需加载多个文件，可在 `data_files` 中指定文件列表。

选择哪种方法加载数据集取决于数据集的创建方式，即是通过直接上传文件夹还是通过 `datasets.push_to_hub` 将 HuggingFace 数据集推送到 Hub 上。

如果您使用的是私有数据集，则需要在配置文件的顶层启用 `hf_use_auth_token` 标志。这意味着数据集是上传到 Hub 的单个文件或多个文件。

这表示数据集是以 HuggingFace 数据集的形式创建，并通过 `datasets.push_to_hub` 推送到 Hub 上。根据数据集的不同，可能还需要其他配置项，如 `name`、`split`、`revision`、`trust_remote_code` 等。

通过 `load_dataset` 中的 `storage_options` 配置，您可以从 S3、GCS、Azure 和 OCI 等远程文件系统加载数据集。此功能目前仍处于实验阶段，如有问题请及时告知我们！

不同存储提供商的唯一区别在于需要在其路径前加上相应的协议前缀。对于目录类型，我们通过 `load_from_disk` 函数进行加载。

对于 S3 存储，需在路径前加上 `s3://` 前缀。系统会按以下顺序加载凭证：
我们假设您已配置好凭证且未使用匿名访问方式。如果您希望使用匿名访问，请告知我们，我们可能需要为此开放相应的配置选项。
其他可设置的环境变量详见 boto3 文档。

对于 GCS 存储，需在路径前加上 `gs://` 或 `gcs://` 前缀。系统会按以下顺序加载凭证：

对于 ADLS 存储，需在路径前加上 `adl://` 前缀。请确保已设置以下环境变量：

对于 ABFS 存储，需在路径前加上 `abfs://` 或 `az://` 前缀。请确保已设置以下环境变量：
其他可设置的环境变量详见 adlfs 文档。

对于 OCI 存储，需在路径前加上 `oci://` 前缀。系统会按以下顺序尝试读取数据：
其他相关环境变量请参阅 ocifs 文档。

路径必须以 `https://` 开头，且该资源必须可公开访问。

现在您已经了解了如何加载数据集，如需了解如何将特定格式的数据集转换为目标输出格式，可查看数据集格式相关文档。

**示例：**

示例 1（yaml 格式）：
```yaml
datasets:
  - path:
    name:
    data_files:
    split:
    revision:
    trust_remote_code:
```

示例 2（yaml 格式）：
```yaml
datasets:
  - path: /path/to/your/dataset
  - path: /path/to/your/other/dataset
```

示例 3（Python）：
```python
from datasets import load_dataset

dataset = load_dataset("json", data_files="data.json")
```

示例 4（yaml 格式）：
```yaml
datasets:
  - path: data.json
    ds_type: json
```

## 多 GPU

**URL:** https://docs.axolotl.ai/docs/multi-gpu.html

**目录:**
- 多 GPU
- 1 概述
- 2 DeepSpeed
  - 2.1 配置
  - 2.2 使用方法
  - 2.3 ZeRO 分阶段策略
- 3 完全分片数据并行（FSDP）
  - 3.1 从 FSDP1 迁移至 FSDP2
    - 3.1.1 配置映射
  - 3.2 FSDP1（已废弃）

本指南介绍了使用 Axolotl 进行多 GPU 设置时的高级训练配置。

Axolotl 支持多种多 GPU 训练方法：

在您的 YAML 配置文件中添加相应设置：

我们提供了以下默认配置：

请选择能在保证最佳性能的同时，将最少数据加载到内存中的配置。

建议按照阶段 1 -> 阶段 2 -> 阶段 3 的顺序进行设置。对于新用户，推荐使用 FSDP2；FSDP1 已废弃，将在未来的 Axolotl 版本中移除。

若要将配置从 FSDP1 迁移至 FSDP2，需使用 `fsdp_version` 这一顶层配置字段来指定 FSDP 版本，并根据下方的配置字段映射表修改字段名称。

更多详细信息，请参阅 torchtitan 仓库中的迁移指南。在 Axolotl 中，如果您原本使用的是以下 FSDP1 配置：

则可迁移到以下的 FSDP2 配置：

目前，通过 `fsdp` 参数来配置 FSDP 的方式已废弃，也将在未来的 Axolotl 版本中移除。请改用上述的 `fsdp_config` 方式。

我们通过 ring-flash-attention 项目支持序列并行（SP）技术。该技术允许将序列分配到不同的 GPU 上，这样在模型训练过程中若单个序列导致内存不足错误时，便可有效避免问题。

更多相关信息，请参阅我们的专用指南。

关于将 FSDP 与 QLoRA 结合使用的方法，也请参阅我们的专用指南。

更多详情，请查阅相关文档。

对于与 NCCL 相关的问题，可参考我们的 NCCL 故障排除指南。

如需更详细的故障排查方法，可参阅我们的调试指南。

**示例:**

示例 1（YAML 格式）：
```yaml
deepspeed: deepspeed_configs/zero1.json
```

示例 2（bash）：
```bash
# Fetch deepspeed configs (if not already present)
axolotl fetch deepspeed_configs

# Passing arg via config
axolotl train config.yml

# Passing arg via cli
axolotl train config.yml --deepspeed deepspeed_configs/zero1.json
```

示例 3（yaml 格式）：
```yaml
fsdp_version: 1
fsdp_config:
  fsdp_offload_params: false
  fsdp_cpu_ram_efficient_loading: true
  fsdp_auto_wrap_policy: TRANSFORMER_BASED_WRAP
  fsdp_transformer_layer_cls_to_wrap: Qwen3DecoderLayer
  fsdp_state_dict_type: FULL_STATE_DICT
  fsdp_sharding_strategy: FULL_SHARD
```

示例 4（yaml 格式）：
```yaml
fsdp_version: 2
fsdp_config:
  offload_params: false
  cpu_ram_efficient_loading: true
  auto_wrap_policy: TRANSFORMER_BASED_WRAP
  transformer_layer_cls_to_wrap: Qwen3DecoderLayer
  state_dict_type: FULL_STATE_DICT
  reshard_after_forward: true
```

## Ray Train

**网址：** https://docs.axolotl.ai/docs/ray-integration.html

**目录：**
- Ray Train
- Ray 集群配置
- 健康检查
- 使用 Ray Train 配置训练
- 启动训练

Axolotl 支持使用 Ray 作为替代方案来加速训练任务的编排。这对于多节点训练尤为有用，因为您只需在单个节点上配置代码和依赖项，即可像使用单节点一样启动训练。

通过使用 --use-ray CLI 参数，Axolotl 将利用 Ray Train 的 TorchTrainer 来执行训练任务。

要使用 Ray Train 集成，首先需要在目标节点上搭建一个 Ray 集群。关于如何搭建 Ray 集群的详细指南，请参阅官方 Ray 文档。

每个 Ray 集群都包含一个头节点以及一组工作节点。头节点与其他工作节点功能类似，但它还会运行与调度和编排相关的特殊进程。支持 Ray 的脚本会在头节点上运行，根据它们申请的资源（CPU 数量、GPU 数量等），这些脚本会被调度到相应的工作节点上执行任务。如需了解 Ray 集群背后的核心概念，可参考相关文档。

要在头节点上检查 Ray 集群是否配置正确，可执行以下命令：

输出结果应包含关于您 Ray 集群的概要信息——包括集群中的所有节点列表、CPU 和 GPU 的数量等。例如，如果您有一个包含 1 个仅配备 CPU 的头节点以及 2 个 4xL40S 型号工作节点的集群，输出可能如下所示：

您也可以在 Ray 控制面板上查看相同的信息。

示例配置文件位于 configs/llama-3/lora-1b-ray.yaml 中。此处需要重点关注的参数包括：

您只需在头节点上运行以下命令即可：

该命令将在头节点上启动训练，Ray Train 会自动将任务调度到合适的首节点或工作节点上执行。

您还可以在 Ray 控制面板上监控训练进度。

以包含 1 个头节点和 2 个 4xL40S 型号工作节点的集群为例，假设您想使用全部 8 枚 GPU，只需将 ray_num_workers 设置为 8，然后运行之前的命令即可。集群选项卡将显示如下内容：

**示例：**

示例 1（未知）：
```unknown
Node status
---------------------------------------------------------------
Active:
 1 head
Idle:
 2 4xL40S:48CPU-384GB
Pending:
 (no pending nodes)
Recent failures:
 (no failures)

Resources
---------------------------------------------------------------
Usage:
 0.0/96.0 CPU
 0.0/8.0 GPU
 0B/800.00GiB memory
 0B/229.57GiB object_store_memory

Demands:
 (no resource demands)
```

示例 2（yaml 格式）：
```yaml
use_ray: true
ray_num_workers: 4
# optional
resources_per_worker:
    GPU: 1
```

示例 3（yaml 格式）：
```yaml
resources_per_worker:
    accelerator_type:L40S: 0.001
```

示例 4（bash）：
```bash
axolotl train examples/llama-3/lora-1b-ray.yml --use-ray
```

## 序列并行处理

**URL:** https://docs.axolotl.ai/docs/sequence_parallelism.html

**目录:**
- 序列并行处理
- 何时使用序列并行处理
- 配置设置
- 实现细节
- 要求条件
- 局限性
- 示例
- 使用序列并行处理进行样本打包
- 对批量大小的影响

序列并行处理是一种将序列分配到多个 GPU 上的技术，使得您能够训练那些无法容纳在单个 GPU 中的极长序列。每个 GPU 处理序列的不同部分，随后通过环形通信机制汇总各部分的结果。

以下情况适合使用序列并行处理：

若要启用序列并行处理，请在配置文件中添加以下内容：

`context_parallel_size` 的值必须是 GPU 总数的因数。例如：

启用序列并行处理后：

要使用序列并行处理，您需要满足以下条件：

这样即可使用 8K 上下文长度训练 Llama 3 8B 模型，此时每个序列会被拆分为两个长度为 4096 的子序列，分别分配到两个 GPU 上处理。

序列并行处理与 Axolotl 的样本打包功能兼容。同时使用这两种功能时：

在使用序列并行处理时，您的有效全局批量大小会除以 `context_parallel_size`。出现这种情况的原因是：

例如：  
- 使用 8 个 GPU 且不启用序列并行处理时：每步可处理 8 个不同的批次  
- 使用 8 个 GPU 且 `context_parallel_size=4` 时：每步仅能处理 2 个不同的批次（每个批次分布在 4 个 GPU 上）  
- 如果每个 GPU 的微批量大小为 2，则全局批量大小会从 16 减少到 4

**示例：**

示例 1（yaml 格式）：
```yaml
# Set to a divisor (> 1) of the number of GPUs available
context_parallel_size: 4  # Split sequences across 4 GPUs
# Optional; strides across the key dimension. Larger values use more memory but should make training faster.
heads_k_stride: 1
# Optional; one of "varlen_llama3" or "batch_ring". Defaults to
# "varlen_llama3" when `sample_packing: true`, and "batch_ring" otherwise.
ring_attn_func:
```

示例 2（yaml 格式）：
```yaml
base_model: meta-llama/Llama-3-8B-Instruct
sequence_len: 8192

...

context_parallel_size: 4  # Split each sequence into 4 parts, one per GPU
# Optional; strides across the key dimension. Larger values use more memory but should make training faster.
heads_k_stride: 1
# Optional; one of "varlen_llama3" or "batch_ring". Defaults to
# "varlen_llama3" when `sample_packing: true`, and "batch_ring" otherwise.
ring_attn_func:

...
```

## 量化感知训练（QAT）

**网址：** https://docs.axolotl.ai/docs/qat.html

**目录：**
- 量化感知训练（QAT）
- 概述
- 在 Axolotl 中配置 QAT

量化感知训练（QAT）是一种提升模型精度的技术，它通过在训练过程中对模型的权重（以及可选的激活值）应用“虚拟”量化操作来实现这一点。这种虚拟量化能让模型适应量化带来的噪声，从而在最终对模型进行实际量化时将精度损失降至最低。在 Axolotl 中，我们借助 torchao 库中的量化技术来支持 QAT 以及训练后的量化处理（PTQ）。

如需了解更多详细信息，建议您查阅 torchtune 库中出色的 QAT 教程以及 torchao 库中的相关文档。

若要在 Axolotl 中启用 QAT，请在配置文件中添加以下内容：

我们支持以下量化方案：

完成训练后，必须使用与训练时相同的量化配置对模型进行量化处理。您可以使用 `quantize` 命令来完成此操作。

**示例：**

示例 1（yaml 格式）：
```yaml
qat:
  activation_dtype: # Optional[str] = "int8". Fake quantization layout to use for activation quantization. Valid options are "int4", "int8", "float8"
  weight_dtype: # Optional[str] = "int8". Fake quantization layout to use for weight quantization. Valid options are "int4", "fp8", and "nvfp4".
  group_size: # Optional[int] = 32. The number of elements in each group for per-group fake quantization
  fake_quant_after_n_steps: # Optional[int] = None. The number of steps to apply fake quantization after
```

## FSDP + QLoRA

**URL:** https://docs.axolotl.ai/docs/fsdp_qlora.html

**目录：**
- FSDP + QLoRA
- 背景介绍
- 使用方法
- 为 FSDP2 启用交换内存
- 示例配置文件
- 参考资料
- 脚注

在消费级 GPU 上微调参数量较大的（700亿以上）大语言模型时，使用 FSDP 结合 QLoRA 是必不可少的手段。例如，你可以利用 FSDP + QLoRA 在两块 24GB 的 GPU 上训练 700 亿参数的模型1。

下文将介绍如何在 Axolotl 中使用该功能。

若要为 FSDP 启用 QLoRA，需按照以下步骤操作：

![提示] 请在阅读本指南的同时参考示例配置文件。

即使使用了 FSDP 的 CPU 卸载功能后内存仍不足，你还可以在 FSDP 配置中将 `cpu_offload_pin_memory` 设置为 `false`，同时将 `offload_params` 设置为 `true`，从而启用交换内存使用。

这样即可取消内存固定绑定，让 FSDP 能够以磁盘交换空间作为备用。虽然取消内存固定绑定本身会带来一定的性能开销，而实际使用交换内存还会进一步降低性能，但这或许能让那些在资源受限的系统上否则会因内存不足而无法训练的更大模型得以训练。

`examples/llama-2/qlora-fsdp.yml` 文件中提供了在 Axolotl 中启用 QLoRA + FSDP 的示例。

这一功能得益于 Answer.AI 团队的研究成果。↩︎

---

## 自定义集成

**URL:** https://docs.axolotl.ai/docs/custom_integrations.html

**目录：**
- 自定义集成
- Cut Cross Entropy
  - 需求条件
  - 安装方法
  - 使用方式
  - 支持的模型
  - 参考文献
- DenseMixer
- Axolotl 的扩散语言模型训练插件
  - 概述

Axolotl 通过集成功能来添加自定义特性，这些集成文件位于 `src/axolotl/integrations` 目录下。

如需启用这些功能，请查阅相应的文档说明。

Cut Cross Entropy（CCE）通过在损失计算过程中的交叉熵运算上进行优化，从而减少 VRAM 的使用量。

更多信息请参见 https://github.com/apple/ml-cross-entropy

如果你尚未安装 `cut_cross_entropy[transformers]`，可运行以下命令进行安装。

相关参考资料请见此处

只需在你的 Axolotl YAML 配置文件中添加以下内容即可：

相关参考资料请见此处

该插件允许在 Axolotl 中采用受 LLaDA（大型语言扩散模型）启发的方法来训练扩散语言模型。

LLaDA 是一种基于扩散机制的语言模型训练方法，其特点包括：- 在训练过程中使用随机令牌掩码而非预测下一个令牌 - 采用双向注意力机制，使模型能够关注完整上下文 - 根据掩码概率进行重要性加权，以实现稳定训练

这种方法能够培养出更具鲁棒性、对双向上下文理解能力更强的语言模型。

该插件已包含在 Axolotl 中，具体安装方法请参阅我们的文档。

可使用示例配置文件（Llama‑3.2 1B）进行训练：- 预训练：`axolotl train examples/llama-3/diffusion-3.2-1b-pretrain.yaml` - 微调：`axolotl train examples/llama-3/diffusion-3.2-1b-sft.yaml`

你也可以修改现有的配置文件，以启用或自定义扩散训练功能。

在 Axolotl 配置文件中添加以下内容：

此外，还需配置嵌套的扩散模块（默认设置如下）：

任何支持 4D 注意力掩码的模型均可直接使用。如果不支持，请提交问题或打开 Pull Request！

在训练过程中，会随机对令牌进行掩码处理：- 从 [0, 1] 范围内均匀采样时间步长 t - 计算掩码概率：p = (1 - eps) * t + eps - 按照概率 p 随机对令牌进行掩码

损失仅针对被掩码的令牌进行计算，并可（可选地）应用重要性加权：

当设置 `diffusion.generate_samples: true` 时，该插件会在训练过程中生成样本：

样本会被记录到控制台以及 WandB（如已启用）中。

扩散推理功能已集成到标准的 Axolotl CLI 中。只需使用训练时相同的配置文件，然后运行命令即可：

如需，可添加 `--gradio` 参数以使用简单的网页界面。

支持交互式控制（在提示词前加上相应命令）：- `:complete N` → 进入完成模式，会在原有内容后追加 N 个新的被掩码令牌（默认为 64 个）- `:mask R` → 进入随机掩码模式，目标掩码比例为 [0.0, 1.0] 范围内的 R 值

该插件会添加（或修改）若干指标，用于监控扩散训练的进展：

相关参考资料请见此处

更多信息请参见 https://github.com/ironjr/grokfast

示例数据集可在此处找到：`axolotl-ai-co/evolkit-logprobs-pipeline-75k-v2-sample`

相关参考资料请见此处

你可以使用 Neural Magic 的 LLMCompressor 在 Axolotl 中对稀疏化后的模型进行微调。

该集成功能允许在 Axolotl 训练框架内，对使用 LLMCompressor 进行稀疏化处理的模型进行微调。通过结合 LLMCompressor 的模型压缩能力与 Axolotl 的分布式训练流程，用户能够高效地大规模微调稀疏模型。

它利用 Axolotl 的插件系统接入微调流程，同时在整个训练过程中保持模型的稀疏性。

包含 llmcompressor extras 的 Axolotl：

要求使用版本不低于 0.5.1 的 llmcompressor

该功能会安装所有必要的依赖项，以便通过该集成对稀疏化模型进行微调。

若要使用此集成实现稀疏微调，需在 Axolotl 配置文件中加入该插件：

请注意，该插件本身并不执行剪枝或稀疏化操作——它专为已经过稀疏化处理的模型设计。

预稀疏化的检查点可以是：- 使用 LLMCompressor 生成的 - 从 Neural Magic 的 Hugging Face 页面下载的 - 你自己创建的、具有兼容稀疏结构的自定义大语言模型

如需了解更多关于编写和自定义 LLMCompressor 配置的信息，请参阅官方文档：https://github.com/vllm-project/llm-compressor/blob/main/README.md

在配置文件中设置 `save_compressed: true` 可以让模型以压缩格式保存，这样做的好处包括：- 减少约 40% 的磁盘空间占用 - 保持与 vLLM 的兼容性，从而实现更快速的推理速度 - 保持与 llmcompressor 的兼容性，便于进一步优化（例如量化处理）

在处理稀疏模型时，强烈建议使用此选项，以充分发挥模型压缩的优势。

完整示例请参见 `examples/llama-3/sparse-finetuning.yaml`。

微调完稀疏模型后，你可以利用 vLLM 实现高效的推理。此外，你还可以在推理前使用 LLMCompressor 对微调后的稀疏模型进行进一步量化处理，从而获得更高的性能提升。

如需了解 vLLM 的更多功能及高级配置选项，请参阅官方 vLLM 文档。

关于可用的稀疏化和量化方案、微调配置以及使用示例的详细信息，请访问官方 LLMCompressor 仓库：

https://github.com/vllm-project/llm-compressor

相关参考资料请见此处

可使用流行的 `lm-evaluation-harness` 库对模型进行评估。

更多信息请参见 https://github.com/EleutherAI/lm-evaluation-harness

相关参考资料请见此处

Liger Kernel 为大语言模型训练提供了高效的 Triton 核心，其优势包括：

更多信息请参见 https://github.com/linkedin/Liger-Kernel

相关参考资料请见此处

作者：Eric Hartford, Lucas Atkins, Fernando Fernandes, David Golchinfar

该插件包含用于根据信噪比（SNR）冻结模型中底部部分模块的代码。

更多信息请参见 https://github.com/cognitivecomputations/spectrum

Spectrum 是一款用于扫描和评估大型语言模型各层信噪比（SNR）的工具。通过识别出 SNR 最高的前 n% 的层，你可以提升训练效率。

相关参考资料请见此处

插件可通过钩子功能来定制训练流程的行为。具体可用的钩子功能请参阅 `axolotl.integrations.BasePlugin`。

如需添加新的集成功能，请按照以下步骤操作：

最简单的集成示例请参见 `src/axolotl/integrations/cut_cross_entropy`。

如果无法加载某个集成功能，请确保你是以“可编辑模式”通过 pip 进行安装的，并且在配置文件中正确拼写了集成功能的名称。

集成功能并不一定需要放在 `integrations` 目录下，只要它能作为 Python 环境中的包被安装，即可放置在任何位置。

示例项目请参见此仓库：https://github.com/axolotl-ai-cloud/diff-transformer

**示例：**

示例 1（bash）：
```bash
python scripts/cutcrossentropy_install.py | sh
```

示例 2（bash）：
```bash
pip3 uninstall -y cut-cross-entropy && pip3 install "cut-cross-entropy[transformers] @ git+https://github.com/axolotl-ai-cloud/ml-cross-entropy.git@8a1a0ec"
```

示例 3（yaml 格式）：
```yaml
plugins:
  - axolotl.integrations.cut_cross_entropy.CutCrossEntropyPlugin
```

示例 4（未知情况）：
```unknown
@article{wijmans2024cut,
  author       = {Erik Wijmans and
                  Brody Huval and
                  Alexander Hertzberg and
                  Vladlen Koltun and
                  Philipp Kr\"ahenb\"uhl},
  title        = {Cut Your Losses in Large-Vocabulary Language Models},
  journal      = {arXiv},
  year         = {2024},
  url          = {https://arxiv.org/abs/2411.09009},
}
```

## 配置参考

**网址：** https://docs.axolotl.ai/docs/config-reference.html

**目录：**
- 配置参考

**示例：**

示例 1（yaml 格式）：
```yaml
# Allow overwrite yml config using from cli
strict: bool | None = False
# Resume from a specific checkpoint dir
resume_from_checkpoint: str | None
# If resume_from_checkpoint isn't set and you simply want it to start where it left off.
# Be careful with this being turned on between different models.
auto_resume_from_checkpoints: bool | None
# Resize the model embeddings when new tokens are added to multiples of 32. This is
# reported to improve training speed on some models
resize_token_embeddings_to_32x: bool | None
mean_resizing_embeddings: bool | None = False

# Whether to shrink the embeddings to len(tokenizer). By default, we won't shrink.
shrink_embeddings: bool | None
# Don't upcast the embeddings to float32 when using PEFT. Useful for low-VRAM GPUs
embeddings_skip_upcast: bool | None
# Reinitialize model weights randomly instead of loading pretrained weights
reinit_weights: bool | None

# module to custom trainer class to use for training
trainer_cls: str | None

# Use RL training: 'dpo', 'ipo', 'kto', 'simpo', 'orpo', 'grpo'
rl: RLType | None

trl: TRLConfig | None
  # For TRLConfig:
  # Beta parameter for the RL training. Same as `rl_beta`. Use
  beta: float | None
  # Maximum length of the completion for RL training.
  max_completion_length: int | None

  # Whether to use VLLM for RL training.
  use_vllm: bool = False
  # VLLM mode to use, one of 'server' or 'colocate'
  vllm_mode: Literal['server', 'colocate'] | None
  # Host of the vLLM server to connect to.
  vllm_server_host: str | None = 0.0.0.0
  # Port of the vLLM server to connect to.
  vllm_server_port: int | None = 8000
  # Total timeout (in seconds) to wait for the vLLM server to respond.
  vllm_server_timeout: int | None
  # Regex for vLLM guided decoding.
  vllm_guided_decoding_regex: str | None

  # List of reward functions to load. Paths must be importable from current dir.
  reward_funcs: list[str] | None
  # List of reward weights for the reward functions.
  reward_weights: list[float] | None
  # Number of generations to sample.
  num_generations: int | None
  # Whether to log completions.
  log_completions: bool | None = False
  # Number of completions to print when log_completions is True.
  num_completions_to_print: int | None
  # Controls whether importance sampling ratios are computed at the `'token'` or
  # `'sequence'` level. For GSPO, use `sequence`, default is None which corresponds to
  # the original GRPO paper.
  importance_sampling_level: Literal['sequence', 'token'] | None

  # Whether to sync the reference model.
  sync_ref_model: bool | None = False
  # Mixup alpha for the reference model.
  ref_model_mixup_alpha: float | None = 0.9
  # Sync steps for the reference model.
  ref_model_sync_steps: int | None = 64
  # Whether to scale rewards by their standard deviation.
  scale_rewards: bool = True

  # Sampling temperature for the GRPO policy.
  temperature: float | None
  # Top-p sampling probability for the generation policy.
  top_p: float | None
  # Top-k sampling for the generation policy.
  top_k: int | None
  # Minimum probability for the generation policy.
  min_p: float | None
  # Penalty for tokens that appear in prompt and generated text.
  repetition_penalty: float | None
  # Number of iterations per batch (μ) for GRPO.
  num_iterations: int | None
  # Epsilon value for clipping in the GRPO algorithm.
  epsilon: float | None
  # Upper-bound epsilon value for clipping in the GRPO algorithm.
  epsilon_high: float | None
  # Whether to use Liger loss for GRPO.
  use_liger_loss: bool | None
  # Loss formulation to use. Supported values: grpo, bnpo, dr_grpo.
  loss_type: str | None
  # Whether to exclude truncated completions from loss calculation.
  mask_truncated_completions: bool = False
  # Enable sleep mode for vLLM to offload VRAM when idle
  vllm_enable_sleep_mode: bool | None

vllm: VllmConfig | None
  # For VllmConfig:
  # Device to use for VLLM
  device: str | None = auto
  # Tensor parallel size for VLLM
  tensor_parallel_size: int | None
  # Data parallel size for VLLM
  data_parallel_size: int | None
  # GPU memory utilization for VLLM
  gpu_memory_utilization: float | None = 0.9
  # Data type for VLLM
  dtype: str | None = auto
  # Maximum length of the model context for VLLM
  max_model_len: int | None
  # Enable prefix caching for VLLM
  enable_prefix_caching: bool | None
  # Host for the vLLM server to start on
  host: str | None = 0.0.0.0
  # Port of the vLLM server to start on
  port: int | None = 8000

  # Enable reasoning for VLLM
  enable_reasoning: bool | None
  # Reasoning parser for VLLM
  reasoning_parser: str | None

qat: QATConfig | None
  # For QATConfig:
  # Fake quantization layout to use for activation quantization.
  activation_dtype: TorchAOQuantDType | None
  # Fake quantization layout to use for weight quantization.
  weight_dtype: TorchAOQuantDType = TorchAOQuantDType.int8
  # Quantize embedding
  quantize_embedding: bool | None = False
  # The number of elements in each group for per-group fake quantization
  group_size: int | None = 32
  # The number of steps to apply fake quantization after
  fake_quant_after_n_steps: int | None

quantization: PTQConfig | None
  # For PTQConfig:
  # Fake quantization layout to use for weight quantization.
  weight_dtype: TorchAOQuantDType = TorchAOQuantDType.int8
  # Fake quantization layout to use for activation quantization.
  activation_dtype: TorchAOQuantDType | None
  # Whether to quantize the embedding layer.
  quantize_embedding: bool | None
  # The number of elements in each group for per-group fake quantization
  group_size: int | None = 32

# Reward modelling: `True` or `False`
reward_model: bool | None
# Process reward modelling: `True` or `False`
process_reward_model: bool | None
# Coefficient to incentivize the reward model to output mean-zero rewards (proposed by
# https://huggingface.co/papers/2312.09244, Eq. 2). Recommended value: `0.01`.
center_rewards_coefficient: float | None
num_labels: int | None

# Whether to perform weighting in DPO trainer
dpo_use_weighting: bool | None
dpo_use_logits_to_keep: bool | None
dpo_label_smoothing: float | None
dpo_norm_loss: bool | None
dpo_padding_free: bool | None
dpo_generate_during_eval: bool | None

# A list of one or more datasets to finetune the model with
datasets: Annotated[list[SFTDataset | DPODataset | KTODataset | StepwiseSupervisedDataset], MinLen(1)] | None
  # For SFTDataset:
  # HuggingFace dataset repo | s3:// | gs:// | path to local file or directory
  path: str | None
  # name of dataset split to load from
  split: str | None
  # The type of prompt to use for training. [alpaca, gpteacher, oasst, reflection]
  type: str | UserDefinedPrompterType | None
    # For UserDefinedPrompterType:
    # Custom user instruction prompt
    system_prompt: str | None
    # Use {system} as key to be replaced
    system_format: str | None
    field_system: str | None
    field_instruction: str | None
    field_input: str | None
    field_output: str | None

    # Customizable to be single line or multi-line. Use {instruction}/{input} as key to
    # be replaced. 'format' can include {input}
    format: str | None
    # 'no_input_format' cannot include {input}
    no_input_format: str | None
  input_transform: str | None
  # split dataset into N pieces (use with shards_idx)
  shards: int | None
  # the index of sharded dataset to use
  shards_idx: int | None
  # process dataset in N sequential chunks for memory efficiency (exclusive with
  # `shards`)
  preprocess_shards: int | None
  conversation: str | None

  # The name of the chat template to use for training, following values are supported:
  # tokenizer_default: Uses the chat template that is available in the
  # tokenizer_config.json. If the chat template is not available in the tokenizer, it
  # will raise an error. This is the default.
  # alpaca/inst/chatml/gemma/cohere/llama3/phi_3/deepseek_v2/jamba: These chat templates
  # are available in the axolotl codebase at src/axolotl/utils/chat_templates.py.
  # tokenizer_default_fallback_*: where * is the name of the chat template to fallback
  # to if the tokenizer does not have a chat template else default to tokenizer. E.g.
  # tokenizer_default_fallback_chatml. jinja: Uses a custom jinja template for the chat
  # template. The custom jinja template should be provided in the chat_template_jinja
  # field.
  chat_template: ChatTemplate | str | None
  # Custom jinja chat template or path to jinja file. Used only if `chat_template:
  # jinja` or empty.
  chat_template_jinja: str | None
  # path to source data files
  data_files: str | list[str] | None
  input_format: str | None
  # name of dataset configuration to load
  name: str | None
  # defines the datatype when path is a file
  ds_type: str | None
  # For `completion` datasets only, uses the provided field instead of `text` column
  field: str | None
  field_human: str | None
  field_model: str | None
  # Key containing the messages (default: "messages")
  field_messages: str | None
  # Key containing the tools (default: "tools"). Must be a list[dict] and follow [JSON
  # schema](https://json-schema.org/learn/getting-started-step-by-step).
  field_tools: str | None
  # Key containing the reasoning trace (default: "reasoning_content").
  field_thinking: str | None
  # The key the chat template expects that indicates the reasoning trace.
  template_thinking_key: str | None

  message_field_role: str | None

  message_field_content: str | None
  # Mapping of properties from the input dataset to the chat template. (default:
  # message_property_mappings={'role':'role', 'content':'content'}) If a property exists
  # in the template but not in this mapping, the system will attempt to load it directly
  # from the message using the property name as the key. Example: In the mapping below,
  # 'from' is loaded from input dataset and used as 'role', while 'value' is loaded and
  # used as 'content' in the chat template.
  message_property_mappings: dict[str, str] | None
  # The key in the message turn that indicates via boolean whether tokens of a turn
  # should be considered for training. Useful to selectively train on certain turns
  # besides the `roles_to_train`.
  message_field_training: str | None
  # The key in the message turn that contains the training details. Useful to
  # selectively train on certain tokens in a turn. The value of the key is a List[Dict]
  # containing `begin_offset` (start character index in content), `end_offset` (end
  # character index in content), and `train` (boolean whether to train).
  message_field_training_detail: str | None
  # (for Qwen3 template only) Whether to split the assistant content based on a
  # reasoning trace inside delimited tags
  split_thinking: bool | None
  logprobs_field: str | None
  temperature: float | None
  # Roles to train on. The tokens from these roles will be considered for the loss.
  roles_to_train: list[str] | None
  # Which EOS tokens to train on in the conversation. Possible values are: all: train on
  # all EOS tokens, turn (default): train on the EOS token at the end of each trainable
  # turn, last: train on the last EOS token in the conversation
  train_on_eos: Literal['all', 'turn', 'last'] | None
  # Roles mapping in the messages. The format is {target_role: [source_roles]}. All
  # source roles will be mapped to the target role. The default is: user: ["human",
  # "user"], assistant: ["gpt", "assistant"], system: ["system"], tool: ["tool"]
  roles: dict[str, list[str]] | None
  # Whether to drop the system turn from the dataset. Only works with chat_template.
  # This does not drop the default system message from chat_template if it exists. If
  # you wish to, we recommend using a custom jinja template with the default system
  # message removed or adding a system turn with empty content.
  drop_system_message: bool | None
  # Trust remote code for untrusted source
  trust_remote_code: bool | None = False
  # The specific revision of the dataset to use when loading from the Hugging Face Hub.
  # This can be a commit hash, tag, or branch name. If not specified, the latest version
  # will be used. This parameter is ignored for local datasets.
  revision: str | None

  # For DPODataset:
  path: str | None
  split: str | None
  type: UserDefinedDPOType | str | None
    # For UserDefinedDPOType:
    field_system: str | None
    field_prompt: str | None
    field_chosen: str | None
    field_rejected: str | None
    prompt_format: str | None
    chosen_format: str | None
    rejected_format: str | None
  data_files: list[str] | None
  revision: str | None
  field_messages: str | None

  # For KTODataset:
  path: str | None
  split: str | None
  type: UserDefinedKTOType | str | None
    # For UserDefinedKTOType:
    field_system: str | None
    field_prompt: str | None
    field_completion: str | None
    field_label: bool | None
    prompt_format: str | None
    completion_format: str | None
  data_files: list[str] | None
  trust_remote_code: bool | None = False
  revision: str | None

  # For StepwiseSupervisedDataset:
  path: str | None
  split: str | None
  data_files: list[str] | None
  revision: str | None
  step_separator: str | None
  max_completion_length: int | None
  train_on_last_step_only: bool | None

# A list of one or more datasets to eval the model with. You can use either
# test_datasets, or val_set_size, but not both.
test_datasets: Annotated[list[SFTDataset | DPODataset | KTODataset | StepwiseSupervisedDataset], MinLen(1)] | None
  # For SFTDataset:
  # HuggingFace dataset repo | s3:// | gs:// | path to local file or directory
  path: str | None
  # name of dataset split to load from
  split: str | None
  # The type of prompt to use for training. [alpaca, gpteacher, oasst, reflection]
  type: str | UserDefinedPrompterType | None
    # For UserDefinedPrompterType:
    # Custom user instruction prompt
    system_prompt: str | None
    # Use {system} as key to be replaced
    system_format: str | None
    field_system: str | None
    field_instruction: str | None
    field_input: str | None
    field_output: str | None

    # Customizable to be single line or multi-line. Use {instruction}/{input} as key to
    # be replaced. 'format' can include {input}
    format: str | None
    # 'no_input_format' cannot include {input}
    no_input_format: str | None
  input_transform: str | None
  # split dataset into N pieces (use with shards_idx)
  shards: int | None
  # the index of sharded dataset to use
  shards_idx: int | None
  # process dataset in N sequential chunks for memory efficiency (exclusive with
  # `shards`)
  preprocess_shards: int | None
  conversation: str | None

  # The name of the chat template to use for training, following values are supported:
  # tokenizer_default: Uses the chat template that is available in the
  # tokenizer_config.json. If the chat template is not available in the tokenizer, it
  # will raise an error. This is the default.
  # alpaca/inst/chatml/gemma/cohere/llama3/phi_3/deepseek_v2/jamba: These chat templates
  # are available in the axolotl codebase at src/axolotl/utils/chat_templates.py.
  # tokenizer_default_fallback_*: where * is the name of the chat template to fallback
  # to if the tokenizer does not have a chat template else default to tokenizer. E.g.
  # tokenizer_default_fallback_chatml. jinja: Uses a custom jinja template for the chat
  # template. The custom jinja template should be provided in the chat_template_jinja
  # field.
  chat_template: ChatTemplate | str | None
  # Custom jinja chat template or path to jinja file. Used only if `chat_template:
  # jinja` or empty.
  chat_template_jinja: str | None
  # path to source data files
  data_files: str | list[str] | None
  input_format: str | None
  # name of dataset configuration to load
  name: str | None
  # defines the datatype when path is a file
  ds_type: str | None
  # For `completion` datasets only, uses the provided field instead of `text` column
  field: str | None
  field_human: str | None
  field_model: str | None
  # Key containing the messages (default: "messages")
  field_messages: str | None
  # Key containing the tools (default: "tools"). Must be a list[dict] and follow [JSON
  # schema](https://json-schema.org/learn/getting-started-step-by-step).
  field_tools: str | None
  # Key containing the reasoning trace (default: "reasoning_content").
  field_thinking: str | None
  # The key the chat template expects that indicates the reasoning trace.
  template_thinking_key: str | None

  message_field_role: str | None

  message_field_content: str | None
  # Mapping of properties from the input dataset to the chat template. (default:
  # message_property_mappings={'role':'role', 'content':'content'}) If a property exists
  # in the template but not in this mapping, the system will attempt to load it directly
  # from the message using the property name as the key. Example: In the mapping below,
  # 'from' is loaded from input dataset and used as 'role', while 'value' is loaded and
  # used as 'content' in the chat template.
  message_property_mappings: dict[str, str] | None
  # The key in the message turn that indicates via boolean whether tokens of a turn
  # should be considered for training. Useful to selectively train on certain turns
  # besides the `roles_to_train`.
  message_field_training: str | None
  # The key in the message turn that contains the training details. Useful to
  # selectively train on certain tokens in a turn. The value of the key is a List[Dict]
  # containing `begin_offset` (start character index in content), `end_offset` (end
  # character index in content), and `train` (boolean whether to train).
  message_field_training_detail: str | None
  # (for Qwen3 template only) Whether to split the assistant content based on a
  # reasoning trace inside delimited tags
  split_thinking: bool | None
  logprobs_field: str | None
  temperature: float | None
  # Roles to train on. The tokens from these roles will be considered for the loss.
  roles_to_train: list[str] | None
  # Which EOS tokens to train on in the conversation. Possible values are: all: train on
  # all EOS tokens, turn (default): train on the EOS token at the end of each trainable
  # turn, last: train on the last EOS token in the conversation
  train_on_eos: Literal['all', 'turn', 'last'] | None
  # Roles mapping in the messages. The format is {target_role: [source_roles]}. All
  # source roles will be mapped to the target role. The default is: user: ["human",
  # "user"], assistant: ["gpt", "assistant"], system: ["system"], tool: ["tool"]
  roles: dict[str, list[str]] | None
  # Whether to drop the system turn from the dataset. Only works with chat_template.
  # This does not drop the default system message from chat_template if it exists. If
  # you wish to, we recommend using a custom jinja template with the default system
  # message removed or adding a system turn with empty content.
  drop_system_message: bool | None
  # Trust remote code for untrusted source
  trust_remote_code: bool | None = False
  # The specific revision of the dataset to use when loading from the Hugging Face Hub.
  # This can be a commit hash, tag, or branch name. If not specified, the latest version
  # will be used. This parameter is ignored for local datasets.
  revision: str | None

  # For DPODataset:
  path: str | None
  split: str | None
  type: UserDefinedDPOType | str | None
    # For UserDefinedDPOType:
    field_system: str | None
    field_prompt: str | None
    field_chosen: str | None
    field_rejected: str | None
    prompt_format: str | None
    chosen_format: str | None
    rejected_format: str | None
  data_files: list[str] | None
  revision: str | None
  field_messages: str | None

  # For KTODataset:
  path: str | None
  split: str | None
  type: UserDefinedKTOType | str | None
    # For UserDefinedKTOType:
    field_system: str | None
    field_prompt: str | None
    field_completion: str | None
    field_label: bool | None
    prompt_format: str | None
    completion_format: str | None
  data_files: list[str] | None
  trust_remote_code: bool | None = False
  revision: str | None

  # For StepwiseSupervisedDataset:
  path: str | None
  split: str | None
  data_files: list[str] | None
  revision: str | None
  step_separator: str | None
  max_completion_length: int | None
  train_on_last_step_only: bool | None

# If false, the datasets will not be shuffled and will keep their original order in
# `datasets`. The same applies to the `test_datasets` option and the
# `pretraining_dataset` option. Default is true.
shuffle_merged_datasets: bool | None = True
# If true, each dataset in `datasets` will be shuffled before merging. This allows
# curriculum learning strategies to be applied at the dataset level. Default is false.
shuffle_before_merging_datasets: bool | None = False
# Axolotl attempts to save the dataset as an arrow after packing the data together so
# subsequent training attempts load faster, relative path
dataset_prepared_path: str | None
# Num shards for whole dataset
dataset_shard_num: int | None
# Index of shard to use for whole dataset
dataset_shard_idx: int | None
skip_prepare_dataset: bool | None = False
# Number of shards to save the prepared dataset
num_dataset_shards_to_save: int | None

# Set to HF dataset for type: 'completion' for streaming instead of pre-tokenize
pretraining_dataset: Annotated[list[PretrainingDataset | SFTDataset], MinLen(1)] | None
  # For PretrainingDataset:
  name: str | None
  path: str | None
  split: str | None = train
  text_column: str | None = text
  type: str | None = pretrain
  trust_remote_code: bool | None = False
  data_files: str | None
  skip: int | None

  # For SFTDataset:
  # HuggingFace dataset repo | s3:// | gs:// | path to local file or directory
  path: str | None
  # name of dataset split to load from
  split: str | None
  # The type of prompt to use for training. [alpaca, gpteacher, oasst, reflection]
  type: str | UserDefinedPrompterType | None
    # For UserDefinedPrompterType:
    # Custom user instruction prompt
    system_prompt: str | None
    # Use {system} as key to be replaced
    system_format: str | None
    field_system: str | None
    field_instruction: str | None
    field_input: str | None
    field_output: str | None

    # Customizable to be single line or multi-line. Use {instruction}/{input} as key to
    # be replaced. 'format' can include {input}
    format: str | None
    # 'no_input_format' cannot include {input}
    no_input_format: str | None
  input_transform: str | None
  # split dataset into N pieces (use with shards_idx)
  shards: int | None
  # the index of sharded dataset to use
  shards_idx: int | None
  # process dataset in N sequential chunks for memory efficiency (exclusive with
  # `shards`)
  preprocess_shards: int | None
  conversation: str | None

  # The name of the chat template to use for training, following values are supported:
  # tokenizer_default: Uses the chat template that is available in the
  # tokenizer_config.json. If the chat template is not available in the tokenizer, it
  # will raise an error. This is the default.
  # alpaca/inst/chatml/gemma/cohere/llama3/phi_3/deepseek_v2/jamba: These chat templates
  # are available in the axolotl codebase at src/axolotl/utils/chat_templates.py.
  # tokenizer_default_fallback_*: where * is the name of the chat template to fallback
  # to if the tokenizer does not have a chat template else default to tokenizer. E.g.
  # tokenizer_default_fallback_chatml. jinja: Uses a custom jinja template for the chat
  # template. The custom jinja template should be provided in the chat_template_jinja
  # field.
  chat_template: ChatTemplate | str | None
  # Custom jinja chat template or path to jinja file. Used only if `chat_template:
  # jinja` or empty.
  chat_template_jinja: str | None
  # path to source data files
  data_files: str | list[str] | None
  input_format: str | None
  # name of dataset configuration to load
  name: str | None
  # defines the datatype when path is a file
  ds_type: str | None
  # For `completion` datasets only, uses the provided field instead of `text` column
  field: str | None
  field_human: str | None
  field_model: str | None
  # Key containing the messages (default: "messages")
  field_messages: str | None
  # Key containing the tools (default: "tools"). Must be a list[dict] and follow [JSON
  # schema](https://json-schema.org/learn/getting-started-step-by-step).
  field_tools: str | None
  # Key containing the reasoning trace (default: "reasoning_content").
  field_thinking: str | None
  # The key the chat template expects that indicates the reasoning trace.
  template_thinking_key: str | None

  message_field_role: str | None

  message_field_content: str | None
  # Mapping of properties from the input dataset to the chat template. (default:
  # message_property_mappings={'role':'role', 'content':'content'}) If a property exists
  # in the template but not in this mapping, the system will attempt to load it directly
  # from the message using the property name as the key. Example: In the mapping below,
  # 'from' is loaded from input dataset and used as 'role', while 'value' is loaded and
  # used as 'content' in the chat template.
  message_property_mappings: dict[str, str] | None
  # The key in the message turn that indicates via boolean whether tokens of a turn
  # should be considered for training. Useful to selectively train on certain turns
  # besides the `roles_to_train`.
  message_field_training: str | None
  # The key in the message turn that contains the training details. Useful to
  # selectively train on certain tokens in a turn. The value of the key is a List[Dict]
  # containing `begin_offset` (start character index in content), `end_offset` (end
  # character index in content), and `train` (boolean whether to train).
  message_field_training_detail: str | None
  # (for Qwen3 template only) Whether to split the assistant content based on a
  # reasoning trace inside delimited tags
  split_thinking: bool | None
  logprobs_field: str | None
  temperature: float | None
  # Roles to train on. The tokens from these roles will be considered for the loss.
  roles_to_train: list[str] | None
  # Which EOS tokens to train on in the conversation. Possible values are: all: train on
  # all EOS tokens, turn (default): train on the EOS token at the end of each trainable
  # turn, last: train on the last EOS token in the conversation
  train_on_eos: Literal['all', 'turn', 'last'] | None
  # Roles mapping in the messages. The format is {target_role: [source_roles]}. All
  # source roles will be mapped to the target role. The default is: user: ["human",
  # "user"], assistant: ["gpt", "assistant"], system: ["system"], tool: ["tool"]
  roles: dict[str, list[str]] | None
  # Whether to drop the system turn from the dataset. Only works with chat_template.
  # This does not drop the default system message from chat_template if it exists. If
  # you wish to, we recommend using a custom jinja template with the default system
  # message removed or adding a system turn with empty content.
  drop_system_message: bool | None
  # Trust remote code for untrusted source
  trust_remote_code: bool | None = False
  # The specific revision of the dataset to use when loading from the Hugging Face Hub.
  # This can be a commit hash, tag, or branch name. If not specified, the latest version
  # will be used. This parameter is ignored for local datasets.
  revision: str | None

# The maximum number of processes to use while preprocessing your input dataset. This
# defaults to `os.cpu_count()` if not set. For Runpod VMs, it will default to number of
# vCPUs via RUNPOD_CPU_COUNT.
dataset_processes: int | None
# The maximum number of processes to use while preprocessing your input dataset. This
# defaults to `os.cpu_count()` if not set. For Runpod VMs, it will default to number of
# vCPUs via RUNPOD_CPU_COUNT.
dataset_num_proc: int | None

# Deduplicates datasets and test_datasets with identical entries
dataset_exact_deduplication: bool | None
# Keep dataset in memory while preprocessing. Only needed if cached dataset is taking
# too much storage
dataset_keep_in_memory: bool | None
dataloader_pin_memory: bool | None
dataloader_num_workers: int | None
dataloader_prefetch_factor: int | None
dataloader_drop_last: bool | None

accelerator_config: dict[str, Any] | None

remove_unused_columns: bool | None

# Push prepared dataset to hub - repo_org/repo_name
push_dataset_to_hub: str | None
# Whether to use hf `use_auth_token` for loading datasets. Useful for fetching private
# datasets. Required to be true when used in combination with `push_dataset_to_hub`
hf_use_auth_token: bool | None

device: Any | None
# Passed through to transformers when loading the model when launched without
# accelerate. Use `sequential` when training w/ model parallelism to limit memory
device_map: Any | None
world_size: int | None
# Don't mess with this, it's here for accelerate and torchrun
local_rank: int | None
ddp: bool | None

# Seed for reproducibility
seed: int | None
# Advanced DDP Arguments - timeout
ddp_timeout: int | None
# Advanced DDP Arguments - bucket cap in MB
ddp_bucket_cap_mb: int | None
# Advanced DDP Arguments - broadcast buffers
ddp_broadcast_buffers: bool | None
ddp_find_unused_parameters: bool | None

# Approximate number of predictions sent to wandb depending on batch size. Enabled above
# 0. Default is 0
eval_table_size: int | None
# Total number of tokens generated for predictions sent to wandb. Default is 128
eval_max_new_tokens: int | None
# Whether to run causal language model evaluation for metrics in
# `eval_causal_lm_metrics`
do_causal_lm_eval: bool | None
# HF evaluate metrics used during evaluation. Default is ['sacrebleu', 'comet', 'ter',
# 'chrf', 'perplexity']
eval_causal_lm_metrics: list[str] | None
do_bench_eval: bool | None
bench_dataset: str | None
bench_split: str | None
metric_for_best_model: str | None
greater_is_better: bool | None

# High loss value, indicating the learning has broken down (a good estimate is ~2 times
# the loss at the start of training)
loss_watchdog_threshold: float | None
# Number of high-loss steps in a row before the trainer aborts (default: 3)
loss_watchdog_patience: int | None

# Run garbage collection every `gc_steps` steps. -1 will run on epoch end and before
# evaluations. Default is 0 (disabled).
gc_steps: int | None

# Use CUDA bf16. bool or 'full' for `bf16_full_eval`, or 'auto' for automatic detection.
# require >=ampere
bf16: Literal['auto'] | bool | None = auto
# Use CUDA fp16
fp16: bool | None
# Enable FP8 mixed precision training using TorchAO. Best used in combination with
# torch.compile.
fp8: bool | None
# Enable FSDP float8 all-gather optimization for FP8 training. Can improve training
# speed by 10-15% when FSDP is enabled.
fp8_enable_fsdp_float8_all_gather: bool | None
# No AMP (automatic mixed precision) - require >=ampere
bfloat16: bool | None
# No AMP (automatic mixed precision)
float16: bool | None
# Use CUDA tf32 - require >=ampere
tf32: bool | None
float32: bool | None

# Whether to use gradient checkpointing. Available options are: true, false, 'offload',
# 'offload_disk'.
# https://huggingface.co/docs/transformers/v4.18.0/en/performance#gradient-checkpointing
gradient_checkpointing: Literal['offload', 'offload_disk'] | bool | None = False
# Additional kwargs to pass to the trainer for gradient checkpointing
gradient_checkpointing_kwargs: dict[str, Any] | None
# Whether to offload activations. Available options are: true, false, 'legacy', 'disk'.
activation_offloading: Literal['legacy', 'disk'] | bool | None = False

unfrozen_parameters: list[str] | None

# The maximum length of an input to train with, this should typically be less than 2048
# as most models have a token/context limit of 2048
sequence_len: int = 512
# What to do when a tokenized row exceeds sequence_len. 'drop' removes the row;
# 'truncate' slices tensors to sequence_len. Defaults to 'drop' for backward
# compatibility.
excess_length_strategy: Literal['drop', 'truncate'] | None
# The maximum length of an input for evaluation. If not specified, defaults to
# sequence_len
eval_sequence_len: int | None
min_sample_len: int | None
# maximum prompt length for RL training
max_prompt_len: int | None
# Use efficient multi-packing with block diagonal attention and per sequence
# position_ids. Recommend set to 'true'
sample_packing: bool | None
# The number of samples packed at a time. Increasing the following values helps with
# packing, but usually only slightly (<%1.)
sample_packing_group_size: int | None = 100000
# The number of samples which can be packed into one sequence. Increase if using a large
# sequence_len with many short samples.
sample_packing_bin_size: int | None = 200
# Whether to pack samples sequentially
sample_packing_sequentially: bool | None
# The multiprocessing start method to use for packing. Should be 'fork', 'spawn' or
# 'forkserver'
sample_packing_mp_start_method: str | None
# Set to 'false' if getting errors during eval with sample_packing on
eval_sample_packing: bool | None
# Pad inputs so each step uses constant sized buffers. This will reduce memory
# fragmentation and may prevent OOMs, by re-using memory more efficiently. Defaults to
# True if `sample_packing` enabled
pad_to_sequence_len: bool | None
# Whether to use sequential sampling for curriculum learning
curriculum_sampling: bool | None
multipack_real_batches: bool | None

# Use batch flattening for speedups when not using sample_packing
batch_flattening: Literal['auto'] | bool | None

use_pose: bool | None
pose_split_on_token_ids: list[int] | None
pose_max_context_len: int | None
pose_num_chunks: int | None

pretrain_multipack_buffer_size: int | None
# whether to prevent cross attention for packed sequences during pretraining
pretrain_multipack_attn: bool | None = True
# whether to concatenate samples during pretraining
pretraining_sample_concatenation: bool | None

# Use streaming mode for loading datasets
streaming: bool | None
# Buffer size for multipack streaming datasets
streaming_multipack_buffer_size: int | None = 10000

# Whether to use xformers attention patch https://github.com/facebookresearch/xformers
xformers_attention: bool | None
# Whether to use scaled-dot-product attention https://pytorch.org/docs/stable/generated/
# torch.nn.functional.scaled_dot_product_attention.html
sdp_attention: bool | None
# Shifted-sparse attention (only llama) - https://arxiv.org/pdf/2309.12307.pdf
s2_attention: bool | None
flex_attention: bool | None
flex_attn_compile_kwargs: dict[str, Any] | None
# Whether to use flash attention patch https://github.com/Dao-AILab/flash-attention
flash_attention: bool | None
# Whether to use flash-attention cross entropy implementation - advanced use only
flash_attn_cross_entropy: bool | None
# Whether to use flash-attention rms norm implementation - advanced use only
flash_attn_rms_norm: bool | None
# Whether to fuse part of the MLP into a single operation
flash_attn_fuse_mlp: bool | None
# Whether to use bettertransformers
flash_optimum: bool | None

eager_attention: bool | None

# Specify a custom attention implementation, used mostly for kernels.
attn_implementation: str | None

unsloth_cross_entropy_loss: bool | None
unsloth_lora_mlp: bool | None
unsloth_lora_qkv: bool | None
unsloth_lora_o: bool | None
unsloth_rms_norm: bool | None
unsloth_rope: bool | None

# Apply custom LoRA autograd functions and activation function Triton kernels for speed
# and memory savings. See: https://docs.axolotl.ai/docs/lora_optims.html
lora_mlp_kernel: bool | None
# Apply custom LoRA autograd functions and activation function Triton kernels for speed
# and memory savings. See: https://docs.axolotl.ai/docs/lora_optims.html
lora_qkv_kernel: bool | None
# Apply custom LoRA autograd functions and activation function Triton kernels for speed
# and memory savings. See: https://docs.axolotl.ai/docs/lora_optims.html
lora_o_kernel: bool | None

# Whether to use chunked cross entropy loss for memory efficiency
chunked_cross_entropy: bool | None
# Number of chunks to use for chunked cross entropy loss
chunked_cross_entropy_num_chunks: int | None

# Whether to use ALST tiled mlp for memory efficient long context
tiled_mlp: bool | None

# Number of shards to use for ALST tiled mlp. If unset, it will be set based on
# seqlen/hidden_size
tiled_mlp_num_shards: int | None

# Whether to use original mlp for ALST tiled mlp. Otherwise uses a generic MLP based on
# llama.
tiled_mlp_use_original_mlp: bool | None = True

llama4_linearized_experts: bool | None

# Deepspeed config path. e.g., deepspeed_configs/zero3.json
deepspeed: str | dict[str, Any] | None
# Whether to use deepcompile for faster training with deepspeed
deepcompile: bool | None
# FSDP configuration
fsdp: list[str] | None

# FSDP configuration options
fsdp_config: FSDPConfig | None
  # For FSDPConfig:
  # Enable activation checkpointing to reduce memory usage during forward passes
  activation_checkpointing: bool | None
  # Offload parameters to CPU to reduce GPU memory usage
  offload_params: bool | None
  # Synchronize module states across all processes
  sync_module_states: bool | None
  # Enable CPU RAM efficient loading to reduce memory usage during model loading
  cpu_ram_efficient_loading: bool | None
  # Disabling this enables swap memory usage for resource-constrained setups when
  # offload_params is enabled.
  cpu_offload_pin_memory: bool | None
  # Use original parameters instead of flattened parameters
  use_orig_params: bool | None

  # Type of state dict to use for saving/loading checkpoints
  state_dict_type: Literal['FULL_STATE_DICT', 'LOCAL_STATE_DICT', 'SHARDED_STATE_DICT'] | None
  # Final state dict type to use after training completion
  final_state_dict_type: Literal['FULL_STATE_DICT', 'LOCAL_STATE_DICT', 'SHARDED_STATE_DICT'] | None

  # Policy for automatically wrapping modules with FSDP
  auto_wrap_policy: Literal['TRANSFORMER_BASED_WRAP', 'SIZE_BASED_WRAP'] | None
  # Class name of transformer layers to wrap (e.g., 'LlamaDecoderLayer')
  transformer_layer_cls_to_wrap: str | None

  # Reshard parameters after forward pass to save memory
  reshard_after_forward: bool | None
  # Mixed precision policy for FSDP (e.g., 'fp16', 'bf16')
  mixed_precision_policy: str | None

# FSDP version
fsdp_version: int | None
fsdp_final_state_dict_type: Literal['FULL_STATE_DICT', 'LOCAL_STATE_DICT', 'SHARDED_STATE_DICT'] | None

# How much of the dataset to set aside as evaluation. 1 = 100%, 0.50 = 50%, etc. 0 for
# no eval.
val_set_size: float | None = 0.0

# Number of devices to shard across. If not set, will use all available devices.
dp_shard_size: int | None
# Number of devices to replicate across.
dp_replicate_size: int | None
# Deprecated: use `context_parallel_size` instead
sequence_parallel_degree: int | None
# Set to a divisor of the number of GPUs available to split sequences into chunks of
# equal size. Use in long context training to prevent OOM when sequences cannot fit into
# a single GPU's VRAM. E.g., if 4 GPUs are available, set this value to 2 to split each
# sequence into two equal-sized subsequences, or set to 4 to split into four equal-sized
# subsequences. See https://docs.axolotl.ai/docs/sequence_parallelism.html for more
# details.
context_parallel_size: int | None
# Optional; strides across the key dimension. Larger values use more memory but should
# make training faster. Must evenly divide the number of KV heads in your model.
heads_k_stride: int | None
# One of 'varlen_llama3', 'batch_ring', 'batch_zigzag', 'batch_stripe'. Defaults to
# 'varlen_llama3' in the sample packing case, and 'batch_ring' in the non-sample packing
# case.
ring_attn_func: RingAttnFunc | None
# Number of tensor parallel processes in TP group. Only supported with DeepSpeed AutoTP.
tensor_parallel_size: int | None

# Add or change special tokens. If you add tokens here, you don't need to add them to
# the `tokens` list.
special_tokens: SpecialTokensConfig | None
  # For SpecialTokensConfig:
  bos_token: str | None
  eos_token: str | None
  pad_token: str | None
  unk_token: str | None
  additional_special_tokens: list[str] | None

# Add extra tokens to the tokenizer
tokens: list[str] | None
# Mapping token_id to new_token_string to override reserved added_tokens in the
# tokenizer. Only works for tokens that are not part of the base vocab (aka are
# added_tokens). Can be checked if they exist in tokenizer.json added_tokens.
added_tokens_overrides: dict[int, str] | None

# Whether to use torch.compile and which backend to use. setting to `auto` will enable
# torch compile when torch>=2.6.0
torch_compile: Literal['auto'] | bool | None
# Backend to use for torch.compile
torch_compile_backend: str | None
torch_compile_mode: Literal['default', 'reduce-overhead', 'max-autotune'] | None

# Maximum number of iterations to train for. It precedes num_epochs which means that if
# both are set, num_epochs will not be guaranteed. e.g., when 1 epoch is 1000 steps =>
# `num_epochs: 2` and `max_steps: 100` will train for 100 steps
max_steps: int | None
# Number of warmup steps. Cannot use with warmup_ratio
warmup_steps: int | None
# Warmup ratio. Cannot use with warmup_steps
warmup_ratio: float | None
# Leave empty to eval at each epoch, integer for every N steps. float for fraction of
# total steps
eval_steps: int | float | None
# Number of times per epoch to run evals, mutually exclusive with eval_steps
evals_per_epoch: int | None
# Set to `no` to skip evaluation, `epoch` at end of each epoch, leave empty to infer
# from `eval_steps`
eval_strategy: str | None

# Leave empty to save at each epoch, integer for every N steps. float for fraction of
# total steps
save_steps: int | float | None
# Number of times per epoch to save a checkpoint, mutually exclusive with save_steps
saves_per_epoch: int | None
# Set to `no` to skip checkpoint saves, `epoch` at end of each epoch, `best` when better
# result is achieved, leave empty to infer from `save_steps`
save_strategy: str | None
# Checkpoints saved at a time
save_total_limit: int | None
# Whether to checkpoint a model after the first step of training. Defaults to False.
save_first_step: bool | None

# Logging frequency
logging_steps: int | None
# Stop training after this many evaluation losses have increased in a row. https://huggi
# ngface.co/transformers/v4.2.2/_modules/transformers/trainer_callback.html#EarlyStoppin
# gCallback
early_stopping_patience: int | None
load_best_model_at_end: bool | None = False
# Save only the model weights, skipping the optimizer. Using this means you can't resume
# from checkpoints.
save_only_model: bool | None = False
# Use tensorboard for logging
use_tensorboard: bool | None
# Enable the pytorch profiler to capture the first N steps of training to the
# output_dir. see https://pytorch.org/blog/understanding-gpu-memory-1/ for more
# information. Snapshots can be visualized @ https://pytorch.org/memory_viz
profiler_steps: int | None
# Which step to start the profiler at. Useful for only capturing a few steps mid-run.
profiler_steps_start: int | None = 0
# bool of whether to report tokens per second at the end of training. This is not
# supported with pre-training datasets.
include_tokens_per_second: bool | None
# bool of whether to report tokens per second per-gpu during training by measuring
# throughput of non-padding tokens.
include_tkps: bool | None = True
# NEFT https://arxiv.org/abs/2310.05914, set this to a number (paper default is 5) to
# add noise to embeddings. Currently only supported on Llama and Mistral
neftune_noise_alpha: float | None

# Parameter controlling the relative ratio loss weight in the ORPO loss. Passed to
# `beta` in `ORPOConfig` due to trl mapping.
orpo_alpha: float | None
# Weighting of NLL term in loss from RPO paper
rpo_alpha: float | None
# Target reward margin for the SimPO loss
simpo_gamma: float | None
# Weight of the BC regularizer
cpo_alpha: float | None

# Factor for desirable loss term in KTO loss
kto_desirable_weight: float | None
# Factor for undesirable loss term in KTO loss
kto_undesirable_weight: float | None
# The beta parameter for the RL training
rl_beta: float | None

# Defines the max memory usage per gpu on the system. Passed through to transformers
# when loading the model.
max_memory: dict[int | Literal['cpu', 'disk'], int | str] | None
# Limit the memory for all available GPUs to this amount (if an integer, expressed in
# gigabytes); default: unset
gpu_memory_limit: int | str | None
# Whether to use low_cpu_mem_usage
low_cpu_mem_usage: bool | None

# The name of the chat template to use for training, following values are supported:
# tokenizer_default: Uses the chat template that is available in the
# tokenizer_config.json. If the chat template is not available in the tokenizer, it will
# raise an error. This is the default value.
# alpaca/inst/chatml/gemma/cohere/llama3/phi_3/deepseek_v2/jamba: These chat templates
# are available in the axolotl codebase at src/axolotl/utils/chat_templates.py.
# tokenizer_default_fallback_*: where * is the name of the chat template to fallback to.
# E.g. tokenizer_default_fallback_chatml. This is useful when the chat template is not
# available in the tokenizer. jinja: Uses a custom jinja template for the chat template.
# The custom jinja template should be provided in the chat_template_jinja field. The
# selected chat template will be saved to the tokenizer_config.json for easier
# inferencing
chat_template: ChatTemplate | Annotated[str, StringConstraints(pattern='^tokenizer_default_fallback_')] | None
# Custom jinja template or path to jinja file for chat template. This will be only used
# if chat_template is set to `jinja` or `null` (in which case chat_template is
# automatically set to `jinja`). Default is null.
chat_template_jinja: str | None
# Additional kwargs to pass to the chat template. This is useful for customizing the
# chat template. For example, you can pass `thinking=False` to add a generation prompt
# to the chat template.
chat_template_kwargs: dict[str, Any] | None
# Custom EOT (End-of-Turn) tokens to mask/unmask during training. These tokens mark the
# boundaries between conversation turns. For example: ['/INST', '</s>',
# '[/SYSTEM_PROMPT]']. If not specified, defaults to just the model's eos_token. This is
# useful for templates that use multiple delimiter tokens.
eot_tokens: list[str] | None
# Changes the default system message. Currently only supports chatml.
default_system_message: str | None

# Token index or indices to adjust embedding weights to the mean of the other tokens.
# This is useful when the model has untrained embeddings.
fix_untrained_tokens: int | list[int] | None

is_preprocess: bool | None
preprocess_iterable: bool | None

# Total number of tokens - internal use
total_num_tokens: int | None
total_supervised_tokens: int | None
# You can set these packing optimizations AFTER starting a training at least once. The
# trainer will provide recommended values for these values.
sample_packing_eff_est: float | None
axolotl_config_path: str | None

# Internal use only - Used to identify which the model is based on
is_falcon_derived_model: bool | None
# Internal use only - Used to identify which the model is based on
is_llama_derived_model: bool | None
# Internal use only - Used to identify which the model is based on. Please note that if
# you set this to true, `padding_side` will be set to 'left' by default
is_mistral_derived_model: bool | None
# Internal use only - Used to identify which the model is based on
is_qwen_derived_model: bool | None

# Add plugins to extend the pipeline. See `src/axolotl/integrations` for the available
# plugins or doc below for more details.
# https://docs.axolotl.ai/docs/custom_integrations.html
plugins: list[str] | None

# This is the huggingface model that contains *.pt, *.safetensors, or *.bin files. This
# can also be a relative path to a model on disk
base_model: str (required)
# If the base_model repo on hf hub doesn't include configuration .json files, You can
# set that here, or leave this empty to default to base_model
base_model_config: str | None
cls_model_config: str | None
# Optional tokenizer configuration path in case you want to use a different tokenizer
# than the one defined in the base model
tokenizer_config: str | None
# use_fast option for tokenizer loading from_pretrained, default to True
tokenizer_use_fast: bool | None
# Whether to use the legacy tokenizer setting, defaults to True
tokenizer_legacy: bool | None
# Whether to use mistral-common tokenizer. If set to True, it will use the mistral-
# common tokenizer.
tokenizer_use_mistral_common: bool | None
# Corresponding tokenizer for the model AutoTokenizer is a good choice
tokenizer_type: str | None
# transformers processor class
processor_type: str | None
# Whether to save jinja files for tokenizer, transformers default is True
tokenizer_save_jinja_files: bool | None = True
# Trust remote code for untrusted source
trust_remote_code: bool | None

# Don't move the model to the device before sharding. Set to `false` to revert to legacy
# behavior.
experimental_skip_move_to_device: bool | None = True

# Use custom kernels, e.g. MegaBlocks.
use_kernels: bool | None

# Model loading quantization config
model_quantization_config: Literal['Mxfp4Config'] | None
# kwargs for model quantization config
model_quantization_config_kwargs: dict[str, Any] | None

# Where to save the full-finetuned model to
output_dir: str = ./model-out
# push checkpoints to hub
hub_model_id: str | None
# how to push checkpoints to hub
hub_strategy: str | None
# Save model as safetensors (require safetensors package). Default True
save_safetensors: bool | None = True

# This will attempt to quantize the model down to 8 bits and use adam 8 bit optimizer
load_in_8bit: bool | None = False
# Use bitsandbytes 4 bit
load_in_4bit: bool | None = False

# If you want to use 'lora' or 'qlora' or leave blank to train all parameters in
# original model
adapter: str | None
# If you already have a lora model trained that you want to load, put that here. This
# means after training, if you want to test the model, you should set this to the value
# of `output_dir`. Note that if you merge an adapter to the base model, a new
# subdirectory `merged` will be created under the `output_dir`.
lora_model_dir: str | None
lora_r: int | None
lora_alpha: int | None
lora_fan_in_fan_out: bool | None
lora_target_modules: str | list[str] | None
lora_target_parameters: str | list[str] | None
# If true, will target all linear modules
lora_target_linear: bool | None
# If you added new tokens to the tokenizer, you may need to save some LoRA modules
# because they need to know the new tokens. For LLaMA and Mistral, you need to save
# `embed_tokens` and `lm_head`. It may vary for other models. `embed_tokens` converts
# tokens to embeddings, and `lm_head` converts embeddings to token probabilities.
lora_modules_to_save: list[str] | None
lora_dropout: float | None = 0.0
# The layer indices to transform, otherwise, apply to all layers
peft_layers_to_transform: list[int] | None
peft_layers_pattern: list[str] | None

peft: PeftConfig | None
  # For PeftConfig:
  # Configuration options for loftq initialization for LoRA
  loftq_config: LoftQConfig | None
    # For LoftQConfig:
    # typically 4 bits
    loftq_bits: int = 4

# Whether to use DoRA.
peft_use_dora: bool | None
# Whether to use RSLoRA.
peft_use_rslora: bool | None
# List of layer indices to replicate.
peft_layer_replication: list[tuple[int, int]] | None
# How to initialize LoRA weights. Default to True which is MS original implementation.
peft_init_lora_weights: bool | str | None
# A list of token indices to fine-tune on the `embed_tokens` layer. Otherwise, a dict
# mapping an embedding layer name to its trainable token indices. See
# https://huggingface.co/docs/peft/v0.17.0/en/developer_guides/lora#efficiently-train-
# tokens-alongside-lora
peft_trainable_token_indices: list[int] | dict[str, list[int]] | None

# load qlora model in sharded format for FSDP using answer.ai technique.
qlora_sharded_model_loading: bool | None = False
# Do the LoRA/PEFT loading on CPU -- this is required if the base model is so large it
# takes up most or all of the available GPU VRAM, e.g. during a model and LoRA merge
lora_on_cpu: bool | None
# Whether you are training a 4-bit GPTQ quantized model
gptq: bool | None
# optional overrides to the bnb 4bit quantization configuration
bnb_config_kwargs: dict[str, Any] | None

# loraplus learning rate ratio lr_B / lr_A. Recommended value is 2^4.
loraplus_lr_ratio: float | None
# loraplus learning rate for lora embedding layers. Default value is 1e-6.
loraplus_lr_embedding: float | None = 1e-06

merge_lora: bool | None

# Whether to use ReLoRA. Use with jagged_restart_*steps options.
relora: bool | None
# threshold for optimizer magnitude when pruning
relora_prune_ratio: float | None
# True to perform lora weight merges on cpu during restarts, for modest gpu memory
# savings
relora_cpu_offload: bool | None

# how often to reset for jagged restarts
jagged_restart_steps: int | None
# how many warmup steps to take after reset for jagged restarts
jagged_restart_warmup_steps: int | None
# how many anneal steps to take before reset for jagged restarts
jagged_restart_anneal_steps: int | None

# If greater than 1, backpropagation will be skipped and the gradients will be
# accumulated for the given number of steps.
gradient_accumulation_steps: int | None = 1
# The number of samples to include in each batch. This is the number of samples sent to
# each GPU. Batch size per gpu = micro_batch_size * gradient_accumulation_steps
micro_batch_size: int | None = 1
# Total batch size, we do not recommended setting this manually
batch_size: int | None
# per gpu micro batch size for evals, defaults to value of micro_batch_size
eval_batch_size: int | None

# whether to find batch size that fits in memory. Passed to underlying transformers
# Trainer
auto_find_batch_size: bool | None

# Whether to mask out or include the human's prompt from the training labels
train_on_inputs: bool | None = False
# Group similarly sized data to minimize padding. May be slower to start, as it must
# download and sort the entire dataset. Note that training loss may have an oscillating
# pattern with this enabled.
group_by_length: bool | None

learning_rate: str | float (required)
embedding_lr: float | None
embedding_lr_scale: float | None
# Specify weight decay
weight_decay: float | None = 0.0
# Specify optimizer
optimizer: OptimizerNames | CustomSupportedOptimizers | None = OptimizerNames.ADAMW_TORCH_FUSED
# Dictionary of arguments to pass to the optimizer
optim_args: str | dict[str, Any] | None
# The target modules to optimize, i.e. the module names that you would like to train,
# right now this is used only for GaLore algorithm
optim_target_modules: list[str] | Literal['all_linear'] | None
# Path to torch distx for optim 'adamw_anyprecision'
torchdistx_path: str | None
lr_scheduler: SchedulerType | Literal['one_cycle'] | Literal['rex'] | None = SchedulerType.COSINE
# Specify a scheduler and kwargs to use with the optimizer
lr_scheduler_kwargs: dict[str, Any] | None
lr_quadratic_warmup: bool | None
# decay lr to some percentage of the peak lr, e.g. cosine_min_lr_ratio=0.1 for 10% of
# peak lr
cosine_min_lr_ratio: float | None
# freeze lr at some percentage of the step, e.g. cosine_constant_lr_ratio=0.8 means
# start cosine_min_lr at 80% of training step
cosine_constant_lr_ratio: float | None
# Learning rate div factor
lr_div_factor: float | None

lr_groups: list[LrGroup] | None
  # For LrGroup:
  name: str (required)
  modules: list[str] (required)
  lr: float (required)

# adamw hyperparams
adam_epsilon: float | None
# only used for CAME Optimizer
adam_epsilon2: float | None
# adamw hyperparams
adam_beta1: float | None
# adamw hyperparams
adam_beta2: float | None
# only used for CAME Optimizer
adam_beta3: float | None

# Dion Optimizer learning rate
dion_lr: float | None
# Dion Optimizer momentum
dion_momentum: float | None
# Dion Optimizer: r/d fraction for low-rank approximation. Used to compute the low-rank
# dimension.
dion_rank_fraction: float | None = 1.0
# Dion Optimizer: Round up the low-rank dimension to a multiple of this number. This may
# be useful to ensure even sharding.
dion_rank_multiple_of: int | None = 1

# Gradient clipping max norm
max_grad_norm: float | None
num_epochs: float = 1.0

use_wandb: bool | None
# Set the name of your wandb run
wandb_name: str | None
# Set the ID of your wandb run
wandb_run_id: str | None
# "offline" to save run metadata locally and not sync to the server, "disabled" to turn
# off wandb
wandb_mode: str | None
# Your wandb project name
wandb_project: str | None
# A wandb Team name if using a Team
wandb_entity: str | None
wandb_watch: str | None
# "checkpoint" to log model to wandb Artifacts every `save_steps` or "end" to log only
# at the end of training
wandb_log_model: str | None

use_mlflow: bool | None
# URI to mlflow
mlflow_tracking_uri: str | None
# Your experiment name
mlflow_experiment_name: str | None
# Your run name
mlflow_run_name: str | None
# set to true to copy each saved checkpoint on each save to mlflow artifact registry
hf_mlflow_log_artifacts: bool | None

# Enable or disable Comet integration.
use_comet: bool | None
# API key for Comet. Recommended to set via `comet login`.
comet_api_key: str | None
# Workspace name in Comet. Defaults to the user's default workspace.
comet_workspace: str | None
# Project name in Comet. Defaults to Uncategorized.
comet_project_name: str | None
# Identifier for the experiment. Used to append data to an existing experiment or
# control the key of new experiments. Default to a random key.
comet_experiment_key: str | None
# Create a new experiment ("create") or log to an existing one ("get"). Default
# ("get_or_create") auto-selects based on configuration.
comet_mode: str | None
# Set to True to log data to Comet server, or False for offline storage. Default is
# True.
comet_online: bool | None
# Dictionary for additional configuration settings, see the doc for more details.
comet_experiment_config: dict[str, Any] | None

# Enable OpenTelemetry metrics collection and Prometheus export
use_otel_metrics: bool | None = False
# Host to bind the OpenTelemetry metrics server to
otel_metrics_host: str | None = localhost
# Port for the Prometheus metrics HTTP server
otel_metrics_port: int | None = 8000

# the number of activate layers in LISA
lisa_n_layers: int | None
# how often to switch layers in LISA
lisa_step_interval: int | None
# path under the model to access the layers
lisa_layers_attribute: str | None = model.layers

gradio_title: str | None
gradio_share: bool | None
gradio_server_name: str | None
gradio_server_port: int | None
gradio_max_new_tokens: int | None
gradio_temperature: float | None

use_ray: bool = False
ray_run_name: str | None
ray_num_workers: int = 1
resources_per_worker: dict

# The size of the image to resize to. It can be an integer (resized into padded-square
# image) or a tuple (width, height).If not provided, we will attempt to load from
# preprocessor.size, otherwise, images won't be resized.
image_size: int | tuple[int, int] | None
# The resampling algorithm to use for image resizing. Default is bilinear. Please refer
# to PIL.Image.Resampling for more details.
image_resize_algorithm: Literal['bilinear', 'bicubic', 'lanczos'] | Resampling | None

# optional overrides to the base model configuration
overrides_of_model_config: dict[str, Any] | None
# optional overrides the base model loading from_pretrained
overrides_of_model_kwargs: dict[str, Any] | None
# If you want to specify the type of model to load, AutoModelForCausalLM is a good
# choice too
type_of_model: str | None
# You can specify to choose a specific model revision from huggingface hub
revision_of_model: str | None

max_packed_sequence_len: int | None
rope_scaling: Any | None
noisy_embedding_alpha: float | None
dpo_beta: float | None
evaluation_strategy: str | None
```

---

## 

**网址：** https://docs.axolotl.ai

**目录：**
- 🎉 最新动态
- ✨ 概述
- 🚀 快速入门——几分钟内完成大语言模型微调
  - Google Colab
  - 安装指南
    - 使用 pip
    - 使用 Docker
    - 云服务提供商
  - 第一次微调体验
- 📚 文档资料

一个免费且开源的大语言模型微调框架

Axolotl 是一款免费开源的工具，旨在简化最新大型语言模型（LLM）的训练后处理及微调流程。

通过 Docker 进行安装相比在本地环境安装更少出现错误。

其他安装方式请参见此处说明。

就这些！如需更详细的操作指引，请查看我们的入门指南。

欢迎贡献代码！详情请参阅我们的贡献指南。

有意赞助？请通过 [email protected] 与我们联系。

若在您的研究或项目中使用了 Axolotl，敬请按以下方式注明出处：

本项目采用 Apache 2.0 许可证授权——详细信息请参见 LICENSE 文件。

**示例：**

示例 1（bash）：
```bash
pip3 install -U packaging==23.2 setuptools==75.8.0 wheel ninja
pip3 install --no-build-isolation axolotl[flash-attn,deepspeed]

# Download example axolotl configs, deepspeed configs
axolotl fetch examples
axolotl fetch deepspeed_configs  # OPTIONAL
```

示例 2（bash）：
```bash
docker run --gpus '"all"' --rm -it axolotlai/axolotl:main-latest
```

示例 3（bash）：
```bash
# Fetch axolotl examples
axolotl fetch examples

# Or, specify a custom path
axolotl fetch examples --dest path/to/folder

# Train a model using LoRA
axolotl train examples/llama-3/lora-1b.yml
```

示例 4（未知情况）：
```unknown
@software{axolotl,
  title = {Axolotl: Open Source LLM Post-Training},
  author = {{Axolotl maintainers and contributors}},
  url = {https://github.com/axolotl-ai-cloud/axolotl},
  license = {Apache-2.0},
  year = {2023}
}
```

## 快速入门

**网址：** https://docs.axolotl.ai/docs/getting-started.html

**目录结构：**
- 快速入门
- 1 简单示例
- 2 理解训练流程
  - 2.1 配置文件
  - 2.2 训练过程
- 3 第一次自定义训练
- 4 常见任务
  - 4.1 测试模型
  - 4.2 使用用户界面
  - 4.3 数据预处理

本指南将带领您完成使用 Axolotl 进行的首个模型微调项目。我们首先会使用 LoRA 技术对一个小语言模型进行微调。该示例选用了参数量为 10 亿的模型，以确保能在大多数 GPU 上运行。请确保已安装 Axolotl（如未安装，请参阅我们的安装指南）。

就是这样！接下来让我们来了解刚刚发生了什么。

YAML 配置文件负责控制训练过程中的所有参数。以下是我们示例配置文件的部分内容：

```yaml
load_in_8bit: true
adapter: lora
```

这些设置分别用于启用 LoRA 适配器微调功能。如需了解更多详细信息，请参阅我们的配置选项说明。

当您运行 `axolotl train` 命令时，Axolotl 会开始执行相应的训练任务。接下来，让我们修改示例以适配您自己的数据：

此配置专门用于使用 alpaca 数据集格式的指令微调数据对模型进行 LoRA 微调，该数据集的格式如下所示：

如需了解更多数据集格式及格式化方法，请参阅我们的数据集格式指南。

同样的 YAML 文件既可用于训练，也可用于推理和模型合并操作。

训练完成后，请对模型进行测试：

更多详细信息请参阅推理相关章节。

启动 Gradio 用户界面：

对于大型数据集，建议先进行数据预处理：

请务必在配置文件中设置 `dataset_prepared_path` 参数，指定已处理数据集的保存路径。

更多详细信息请参阅数据集预处理指南。

若要将 LoRA 权重合并回基础模型，请运行相应命令：

合并后的模型将保存在 `{output_dir}/merged` 目录下。

更多详细信息请参阅 LoRA 权重合并指南。

掌握了这些基础知识后，您或许还想进一步了解以下内容：

如需了解这些主题的更多细节，请查看我们的其他指南：

**示例：**

示例 1（bash 命令行）：
```bash
axolotl fetch examples
```

示例 2（bash）：
```bash
axolotl train examples/llama-3/lora-1b.yml
```

示例 3（yaml 格式）：
```yaml
base_model: NousResearch/Llama-3.2-1B

load_in_8bit: true
adapter: lora

datasets:
  - path: teknium/GPT4-LLM-Cleaned
    type: alpaca
dataset_prepared_path: last_run_prepared
val_set_size: 0.1
output_dir: ./outputs/lora-out
```

示例 4（yaml 格式）：
```yaml
base_model: NousResearch/Nous-Hermes-llama-1b-v1

load_in_8bit: true
adapter: lora

# Training settings
micro_batch_size: 2
num_epochs: 3
learning_rate: 0.0003

# Your dataset
datasets:
  - path: my_data.jsonl        # Your local data file
    type: alpaca               # Or other format
```

## 多序列打包（样本打包）

**URL:** https://docs.axolotl.ai/docs/multipack.html

**目录:**
- 多序列打包（样本打包）
- 使用 Flash Attention 进行多序列打包可视化
- 不使用 Flash Attention 的多序列打包

由于 Flash Attention 会直接忽略注意力掩码，因此我们无需构建 4 维注意力掩码。只需将多个序列拼接为一个批次，并告知 Flash Attention 每个新序列的起始位置即可。

上下文长度为 4k，批次大小 bsz = 4，每个字符对应 256 个令牌，X 表示填充令牌。在每一步中，都会根据最长输入长度进行填充。

打包后的参数如下（注意：每步的有效令牌数保持不变，但实际批次大小为 1）：
cu_seqlens: [[ 0, 11, 17, 24, 28, 36, 41, 44, 48, 51, 55, 60, 64]]

即便不使用 Flash Attention，依然可以实现多序列打包，但由于缺乏 Flash Attention 的上下文长度限制，我们无法将多个批次合并为一个批次，因此打包效率会较低。此时我们可以选择使用 Pytorch 的缩放点积注意力实现，或结合原生 Pytorch 注意力实现及 4 维注意力掩码来对序列进行打包，从而避免跨序列注意力计算。

**示例:**

示例 1（未知）：
```unknown
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
[[ A A A A A A A A A A A ]
   B B B B B B ]
   C C C C C C C ]
   D D D D ]]

[[ E E E E E E E E ]
 [ F F F F ]
 [ G G G ]
 [ H H H H ]]

[[ I I I ]
 [ J J J ]
 [ K K K K K]
 [ L L L ]]
```

示例 2（未知情况）：
```unknown
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
[[ A A A A A A A A A A A ]
   B B B B B B X X X X X X ]
   C C C C C C C X X X X ]
   D D D D X X X X X X X ]]

[[ E E E E E E E E ]
 [ F F F F X X X X ]
 [ G G G X X X X X ]
 [ H H H H X X X X ]]

[[ I I I X X ]
 [ J J J X X ]
 [ K K K K K ]
 [ L L L X X ]]
```

示例 3（未知情况）：
```unknown
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
[[ A A A A A A A A A A A B B B B B
   B C C C C C C C D D D D E E E E
   E E E E F F F F F G G G H H H H
   I I I J J J J K K K K K L L L X ]]
```

## 批量大小与梯度累积

**URL:** https://docs.axolotl.ai/docs/batch_vs_grad.html

**目录:**
- 批量大小与梯度累积

梯度累积是指在多个小批量中累积梯度，之后再更新模型权重。当每个批次中的样本具有多样性时，该技术不会对学习过程产生显著影响。

通过这种方法，无需相应增加内存容量，即可实现更大有效批量大小的训练效果。原因如下：

批量大小对内存消耗的影响：增加批量大小会占用更多内存，主要原因是中间激活值的存储需求。当将一个批次的数据向前传递到网络中时，必须为批次中每个样本的每一层都存储激活值，因为这些激活值会在反向传播过程中用于计算梯度。因此，更大的批次意味着更多的激活值，从而导致更高的GPU内存消耗。

梯度累积：通过梯度累积，可以通过在多个较小批次（或微批次）中累积梯度，从而有效模拟出更大的批量大小。不过，在任何给定时间点，实际上只会对一个微批次进行前向和反向传播。这意味着只需存储该微批次的激活值，而无需存储整个累积后的批次。因此，无需承担存储大批次激活值所带来的内存开销，即可实现类似大批次的效果。

示例 1：微批次大小：3，梯度累积步数：2，GPU数量：3，总批量大小 = 3 * 2 * 3 = 18

示例 2：微批次大小：2，梯度累积步数：1，GPU数量：3，总批量大小 = 2 * 1 * 3 = 6

**示例：**

示例 1（信息缺失）：
```unknown
| GPU 1          | GPU 2          | GPU 3          |
|----------------|----------------|----------------|
| S1, S2, S3     | S4, S5, S6     | S7, S8, S9     |
| e1, e2, e3     | e4, e5, e6     | e7, e8, e9     |
|----------------|----------------|----------------|
| → (accumulate) | → (accumulate) | → (accumulate) |
|----------------|----------------|----------------|
| S10, S11, S12  | S13, S14, S15  | S16, S17, S18  |
| e10, e11, e12  | e13, e14, e15  | e16, e17, e18  |
|----------------|----------------|----------------|
| → (apply)      | → (apply)      | → (apply)      |

Accumulated gradient for the weight w1 after the second iteration (considering all GPUs):
Total gradient for w1 = e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15 + e16 + e17 + e18

Weight update for w1:
w1_new = w1_old - learning rate x (Total gradient for w1 / 18)
```

示例 2（未知情况）：
```unknown
| GPU 1     | GPU 2     | GPU 3     |
|-----------|-----------|-----------|
| S1, S2    | S3, S4    | S5, S6    |
| e1, e2    | e3, e4    | e5, e6    |
|-----------|-----------|-----------|
| → (apply) | → (apply) | → (apply) |

Accumulated gradient for the weight w1 (considering all GPUs):
Total gradient for w1 = e1 + e2 + e3 + e4 + e5 + e6

Weight update for w1:
w1_new = w1_old - learning rate × (Total gradient for w1 / 6)
```

## 调试

**URL:** https://docs.axolotl.ai/docs/debugging.html

**目录:**
- 调试
- 目录结构
- 通用技巧
- 使用 VSCode 进行调试
  - 背景介绍
  - 设置
    - 远程主机
  - 配置
  - 自定义调试器
  - 视频教程

本文档提供了针对 Axolotl 的一些调试技巧与方法，同时还给出了使用 VSCode 进行调试的示例配置。完善的调试环境对于理解 Axolotl 代码的运行机制至关重要。

在调试过程中，尽可能简化测试场景会很有帮助。以下是一些相关建议：

[!重要] 所有这些技巧均已融入下方的 VSCode 调试示例配置中。

确保使用最新版本的 axolotl：该项目更新频繁，漏洞也会很快得到修复。请检查您的 git 分支，确认已从 main 分支拉取最新代码。

消除并发问题：在训练和数据预处理阶段，都将进程数量限制为 1。

使用小型数据集：自行构建或使用来自 HF Hub 的小型数据集。使用小型数据集时，通常需要将 `sample_packing: False` 和 `eval_sample_packing: False`，以避免出现错误。如果您时间紧迫，无法构建小型数据集但又想从 HF Hub 获取数据，可以对数据进行分片处理（这样仍会对整个数据集进行分词，但仅使用其中一部分用于训练。例如，若要将数据集分为 20 份，在 axolotl 配置中添加以下内容即可）。

使用小型模型：TinyLlama/TinyLlama-1.1B-Chat-v1.0 就是小型模型的典型代表。

缩短迭代时间：通过调整相关设置，确保训练循环能尽快完成。

清除缓存：Axolotl 会缓存某些步骤，底层的 HuggingFace 训练器也会如此。在调试时，您可能需要清除部分缓存。

以下示例展示了如何配置 VSCode，以便对 chat_template 格式的数据预处理过程进行调试。当您的 axolotl 配置中使用该格式时，就需要进行此类调试。[!重要] 如果您已经熟悉 VSCode 的高级调试功能，可直接跳过以下说明，查看 `.vscode/launch.json` 和 `.vscode/tasks.json` 文件中的示例配置。

[!提示] 如果您更喜欢观看视频而非阅读文字，可以直接跳转到下方的视频教程（不过建议两者都看）。

确保您安装的是可编辑版本的 Axolotl，这样才能确保对代码所做的修改能在运行时得到体现。请从该项目的根目录运行以下命令：

如果您在远程主机上进行开发，可以轻松使用 VSCode 进行远程调试。为此，需要遵循此远程 SSH 教程。您还可以观看下方关于 Docker 和远程 SSH 调试的视频。

最简单的入门方式是修改该项目中的 `.vscode/launch.json` 文件。这只是一个示例配置，您可能需要根据自身需求对其进行修改或复制。

例如，要模拟命令 `cd devtools && CUDA_VISIBLE_DEVICES=0 accelerate launch -m axolotl.cli.train dev_chat_template.yml` 的效果，可使用以下配置1。请注意，我们添加了额外的参数来覆盖 axolotl 的默认配置，并应用了上述技巧（详见注释）。同时，我们将工作目录设置为 `devtools`，并将环境变量 `HF_HOME` 设置为一个临时文件夹，之后会部分删除该文件夹。这是因为我们希望在每次运行前都删除 HF 数据集缓存，从而确保数据预处理代码能从头开始执行。

关于此配置的补充说明：

[!提示] 您可能并不想删除这些文件夹。例如，如果您是在调试模型训练而非数据预处理，就很可能不需要删除缓存或输出文件夹。根据您的具体使用场景，还可能需要在 `tasks.json` 文件中添加其他任务。

以下是定义 `cleanup-for-dataprep` 任务的 `.vscode/tasks.json` 文件。当您使用上述配置时，该任务会在每次调试会话开始前执行。请注意，这里有两个用于删除上述两个文件夹的任务。第三个任务 `cleanup-for-dataprep` 是一个复合任务，由这两个任务组合而成。之所以需要复合任务，是因为 VSCode 不允许在 `launch.json` 文件的 `preLaunchTask` 参数中指定多个任务。

您的调试场景可能与上述示例不同。最简单的方法是将自己的 axolotl 配置放入 `devtools` 文件夹中，然后修改 `launch.json` 文件以使用该配置。您还可以根据需求修改 `preLaunchTask`，决定删除哪些文件夹或完全不删除任何文件夹。

以下视频教程将详细介绍上述配置，并演示如何使用 VSCode 进行调试（点击下方图片即可观看）：

使用官方的 Axolotl Docker 镜像是调试代码的绝佳方式，也是目前使用 Axolotl 的常见方法。要将 VSCode 连接到 Docker 环境，则需要多一步操作。

在运行 axolotl 的主机上（例如，如果您使用的是远程主机），请克隆 axolotl 仓库，并将当前目录切换到项目根目录：

[!提示] 如果您的主机上已经克隆了 axolotl，请确保已获取最新代码，并切换到项目根目录。

接下来，运行所需的 Docker 镜像，并挂载当前目录。以下是可用于实现此操作的 docker 命令2：

[!提示] 要了解有哪些容器可用，请查看 README 中的 Docker 部分以及 DockerHub 仓库的相关内容。关于 Docker 容器构建方式的详细信息，可参阅 axolotl 的 Docker CI 构建文档。

此时您就已经进入容器中了。接下来，对 Axolotl 进行可编辑安装：

之后，如果您使用的是远程主机，请通过 VSCode 远程连接到该主机。如果是在本地主机上运行，则可以跳过此步骤。

接着，在 VSCode 中通过命令面板（CMD + SHIFT + P）选择“Dev Containers: Attach to Running Container...”。系统会提示您选择要连接的容器，请选择刚刚创建的容器。此时您就会进入容器中，工作目录为项目根目录。您对代码所做的任何修改都会同时反映在容器和主机上。

现在，您就可以按照上述方法进行调试了（详见“使用 VSCode 进行调试”部分）。

以下是一个简短的视频，演示了如何连接到远程主机上的 Docker 容器：

该配置实际上模拟了命令 `CUDA_VISIBLE_DEVICES=0 python -m accelerate.commands.launch -m axolotl.cli.train devtools/chat_template.yml` 的效果，但功能是完全相同的。↩︎

下面的许多参数都是 Nvidia 推荐的在使用 nvidia-container-toolkit 时的最佳实践。您可以在此处了解更多关于这些参数的信息。↩︎

**示例：**

示例 1（yaml 格式）：
```yaml
datasets:
    ...
    shards: 20
```

示例 2（yaml 格式）：
```yaml
datasets:
  - path: <path to your chat_template formatted dataset> # example on HF Hub: fozziethebeat/alpaca_messages_2k_test
    type: chat_template
```

示例 3（bash）：
```bash
pip3 install packaging
pip3 install --no-build-isolation -e '.[flash-attn,deepspeed]'
```

示例 4（JSON格式）：
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug axolotl prompt - chat_template",
            "type": "python",
            "module": "accelerate.commands.launch",
            "request": "launch",
            "args": [
                "-m", "axolotl.cli.train", "dev_chat_template.yml",
                // The flags below simplify debugging by overriding the axolotl config
                // with the debugging tips above.  Modify as needed.
                "--dataset_num_proc=1",      // limits data preprocessing to one process
                "--max_steps=1",              // limits training to just one step
                "--batch_size=1",             // minimizes batch size
                "--micro_batch_size=1",       // minimizes batch size
                "--val_set_size=0",           // disables validation
                "--sample_packing=False",     // disables sample packing which is necessary for small datasets
                "--eval_sample_packing=False",// disables sample packing on eval set
                "--dataset_prepared_path=temp_debug/axolotl_outputs/data", // send data outputs to a temp folder
                "--output_dir=temp_debug/axolotl_outputs/model" // send model outputs to a temp folder
                ],
            "console": "integratedTerminal",      // show output in the integrated terminal
            "cwd": "${workspaceFolder}/devtools", // set working directory to devtools from the root of the project
            "justMyCode": true,                   // step through only axolotl code
            "env": {"CUDA_VISIBLE_DEVICES": "0",  // Since we aren't doing distributed training, we need to limit to one GPU
                    "HF_HOME": "${workspaceFolder}/devtools/temp_debug/.hf-cache"}, // send HF cache to a temp folder
            "preLaunchTask": "cleanup-for-dataprep", // delete temp folders (see below)
        }
    ]
}
```

## Docker

**URL:** https://docs.axolotl.ai/docs/docker.html

**目录结构：**
- Docker
- 基础镜像
    - 镜像
    - 标签格式
- 主镜像
    - 镜像
    - 标签格式
- 云环境镜像
    - 镜像
    - 标签格式

本章节介绍了 AxolotlAI 在 Docker Hub 上发布的各类 Docker 镜像。

对于 Blackwell GPU，建议使用搭配 PyTorch 2.7.1 和 CUDA 12.8 的标签。

基础镜像是能够安装 Axolotl 的最精简版本，它基于 nvidia/cuda 镜像构建，预装了 python、torch、git、git-lfs、awscli、pydantic 等组件。

主镜像则是用于运行 Axolotl 的镜像，它基于 axolotlai/axolotl-base 镜像打造，包含了 Axolotl 的代码库及各类依赖项。

部分镜像还会附加额外的标签，例如 -vllm，用于安装特定软件包。

云环境镜像专为在云端运行 Axolotl 设计，它同样基于 axolotlai/axolotl 镜像，并会根据不同的云服务提供商设置相应的环境变量，如用于卷挂载的 HuggingFace 缓存目录、tmux 等配置。

该镜像默认会启动 Jupyter lab，若需禁用它，可在环境变量中设置 JUPYTER_DISABLE=1。

此镜像使用的标签与主镜像相同。

为确保数据持久化，建议将数据存储路径挂载到 /workspace/data 目录；而 /workspace/axolotl 目录仅存放源代码，属于临时性存储空间。

该镜像与云环境镜像功能相同，但不包含 tmux 组件。

由于其名称末尾带有 -term，可能会让人产生些许困惑。

此镜像使用的标签与云环境镜像一致。

**示例：**

示例 1（未知）：
```unknown
axolotlai/axolotl-base
```

示例 2（bash）：
```bash
main-base-py{python_version}-cu{cuda_version}-{pytorch_version}
```

示例 3（未知情况）：
```unknown
axolotlai/axolotl
```

示例 4（bash）：
```bash
# on push to main
main-py{python_version}-cu{cuda_version}-{pytorch_version}

# latest main (currently torch 2.6.0, python 3.11, cuda 12.4)
main-latest

# nightly build
{branch}-{date_in_YYYYMMDD}-py{python_version}-cu{cuda_version}-{pytorch_version}

# tagged release
{version}
```

---
Hermes Agent的技术文档、CLI使用指南、智能体功能、插件、服务提供商相关内容以及开发者指南。
