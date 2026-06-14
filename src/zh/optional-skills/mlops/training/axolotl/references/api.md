# Axolotl - API

**页面数：** 150

---

## cli.cloud.modal_

**网址：** https://docs.axolotl.ai/docs/api/cli.cloud.modal_.html

**内容概要：**
- cli.cloud.modal_
- 类
  - ModalCloud
- 函数
  - run_cmd

通过 CLI 使用 Modal Cloud 功能

Modal Cloud 的实现方式。

在指定文件夹内运行命令，成功前会重新加载 Modal Volume，完成后进行提交。

**示例：**

示例 1（Python）：
```python
cli.cloud.modal_.ModalCloud(config, app=None)
```

示例 2（Python）：
```python
cli.cloud.modal_.run_cmd(cmd, run_folder, volumes=None)
```

## core.trainers.base

**URL:** https://docs.axolotl.ai/docs/api/core.trainers.base.html

**内容：**
- core.trainers.base
- 类
  - AxolotlTrainer
    - 方法
      - log
        - 参数
      - push_to_hub
      - store_metrics
        - 参数

用于自定义训练器的模块

扩展基础 Trainer 以添加 axolotl 相关功能

记录与训练相关的各类对象信息，包括存储的指标数据。

如需在将模型推送到 Hub 时强制添加标签，可重写 push_to_hub 方法。详情请参阅 ~transformers.Trainer.push_to_hub。

以指定的聚合类型存储指标数据。

**示例：**

示例 1（Python）：
```python
core.trainers.base.AxolotlTrainer(
    *_args,
    bench_data_collator=None,
    eval_data_collator=None,
    dataset_tags=None,
    **kwargs,
)
```

示例 2（Python）：
```python
core.trainers.base.AxolotlTrainer.log(logs, start_time=None)
```

示例 3（Python）：
```python
core.trainers.base.AxolotlTrainer.push_to_hub(*args, **kwargs)
```

示例 4（Python）：
```python
core.trainers.base.AxolotlTrainer.store_metrics(
    metrics,
    train_eval='train',
    reduction='mean',
)
```

## prompt_strategies.input_output

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.input_output.html

**内容：**
- prompt_strategies.input_output
- 类
  - RawInputOutputPrompter
  - RawInputOutputStrategy

prompt_strategies.input_output

用于处理纯输入/输出提示对的模块

用于原始输入/输出数据的提示器

用于输入/输出对的处理策略类

**示例：**

示例 1（Python）：
```python
prompt_strategies.input_output.RawInputOutputPrompter()
```

示例 2（Python）：
```python
prompt_strategies.input_output.RawInputOutputStrategy(
    *args,
    eos_token=None,
    **kwargs,
)
```

## prompt_strategies.completion

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.completion.html

**内容：**
- prompt_strategies.completion
- 类
  - CompletionPromptTokenizingStrategy
  - CompletionPrompter

prompt_strategies.completion

基础补全文本

用于处理补全提示的分词策略。

用于实现补全功能的提示生成器

**示例：**

示例 1（Python）：
```python
prompt_strategies.completion.CompletionPromptTokenizingStrategy(
    *args,
    max_length=None,
    **kwargs,
)
```

示例 2（Python）：
```python
prompt_strategies.completion.CompletionPrompter()
```

---

## utils.collators.core

**URL:** https://docs.axolotl.ai/docs/api/utils.collators.core.html

**内容：**
- utils.collators.core

基础共享的合并器常量

---

## monkeypatch.data.batch_dataset_fetcher

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.data.batch_dataset_fetcher.html

**内容：**
- monkeypatch.data.batch_dataset_fetcher
- 函数
  - apply_multipack_dataloader_patch
  - patch_fetchers
  - patched_worker_loop
  - remove_multipack_dataloader_patch

monkeypatch.data.batch_dataset_fetcher

用于对数据集获取器进行猴子补丁处理，以便处理批量打包的索引数据。该补丁能够让DataLoader正确处理包含多个打包序列分组的批次数据。它会对PyTorch的DataLoader组件应用补丁，并通过工作进程循环确保补丁得以生效。最后可移除该猴子补丁，恢复PyTorch DataLoader的原有行为。

**示例：**

示例 1（Python）：
```python
monkeypatch.data.batch_dataset_fetcher.apply_multipack_dataloader_patch()
```

示例 2（Python）：
```python
monkeypatch.data.batch_dataset_fetcher.patch_fetchers()
```

示例 3（Python）：
```python
monkeypatch.data.batch_dataset_fetcher.patched_worker_loop(*args, **kwargs)
```

示例 4（Python）：
```python
monkeypatch.data.batch_dataset_fetcher.remove_multipack_dataloader_patch()
```

## core.datasets.chat

**网址：** https://docs.axolotl.ai/docs/api/core.datasets.chat.html

**内容概要：**
- core.datasets.chat
- 类别
  - TokenizedChatDataset

分词后的聊天数据集

**示例：**

示例 1（Python）：
```python
core.datasets.chat.TokenizedChatDataset(
    data,
    model_transform,
    *args,
    message_transform=None,
    formatter=None,
    process_count=None,
    keep_in_memory=False,
    **kwargs,
)
```

## utils.freeze

**URL:** https://docs.axolotl.ai/docs/api/utils.freeze.html

**目录：**
- utils.freeze
- 类
  - LayerNamePattern
    - 方法
      - match
- 函数
  - freeze_layers_except

用于按名称冻结/解冻参数的模块

表示层名称的正则表达式模式，可能包含参数索引范围。

用于检查给定的层名称是否与正则表达式模式匹配。

参数：  
- name (str)：要检查的层名称。

返回值：  
- bool：如果层名称与模式匹配，则返回 True，否则返回 False。

该函数会冻结给定模型中的所有层，但会保留与指定正则表达式模式匹配的层。模式中的句点被视为字面符号，而非通配符。

参数：  
- model (nn.Module)：需要修改的 PyTorch 模型。  
- regex_patterns (str 列表)：用于指定要保持未冻结状态的层名称的正则表达式模式列表。请注意，不能在模式中使用句点作为通配符，因为该符号专用于分隔层名称。此外，若要匹配整个层名称，模式应以 “^” 开头并以 “\)” 结尾，否则它将仅匹配层名称的任意部分。范围模式是可选的，且不会被编译为真正的正则表达式，因此如果想要匹配整个层名称，必须在范围模式前加上 “\”)。例如：["^model.embed_tokens.weight\([:32000]", "layers.2[0-9]+.block_sparse_moe.gate.[a-z]+\]"]

返回值：无；模型会在原地进行修改。

**示例：**

示例 1（Python）：
```python
utils.freeze.LayerNamePattern(pattern)
```

示例 2（Python）：
```python
utils.freeze.LayerNamePattern.match(name)
```

示例 3（Python）：
```python
utils.freeze.freeze_layers_except(model, regex_patterns)
```

## monkeypatch.unsloth_

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.unsloth_.html

**内容：**
- monkeypatch.unsloth_
用于应用 unsloth 优化技术的补丁模块

---

## utils.schemas.datasets

**URL:** https://docs.axolotl.ai/docs/api/utils.schemas.datasets.html

**内容：**
- utils.schemas.datasets
- 类
  - DPODataset
  - KTODataset
  - PretrainingDataset
  - SFTDataset
    - 方法
      - handle_legacy_message_fields
  - StepwiseSupervisedDataset
  - UserDefinedDPOType

utils.schemas.datasets

用于数据集相关配置的 Pydantic 模型

DPO 配置子集

KTO 配置子集

预训练数据集配置子集

SFT 配置子集

处理旧版消息字段映射与新版属性映射系统之间的兼容性问题。

逐步监督学习数据集配置子集

用户自定义的 DPO 类型定义

用户自定义的 KTO 类型定义

用户自定义提示类型的结构

**示例：**

示例 1（Python）：
```python
utils.schemas.datasets.DPODataset()
```

示例 2（Python）：
```python
utils.schemas.datasets.KTODataset()
```

示例 3（Python）：
```python
utils.schemas.datasets.PretrainingDataset()
```

示例 4（Python）：
```python
utils.schemas.datasets.SFTDataset()
```

## core.chat.format.llama3x

**网址：** https://docs.axolotl.ai/docs/api/core.chat.format.llama3x.html

**内容：**
- core.chat.format.llama3x

core.chat.format.llama3x

用于处理 MessageContents 的 Llama 3.x 对话格式化功能

---

## datasets

**网址：** https://docs.axolotl.ai/docs/api/datasets.html

**内容：**
- datasets
- 类别
  - TokenizedPromptDataset
    - 参数

包含数据集相关功能的模块。

我们希望将其作为已加载现有数据集的封装层。可以借助中间件的概念来对每个数据集进行封装，之后再使用拼接器来统一填充这些数据集。

从一系列文本文件中提取标记化提示词的数据集。

**示例：**

示例 1（Python）：
```python
datasets.TokenizedPromptDataset(
    prompt_tokenizer,
    dataset,
    process_count=None,
    keep_in_memory=False,
    **kwargs,
)
```

## prompt_strategies.bradley_terry.llama3

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.bradley_terry.llama3.html

**内容：**
- prompt_strategies.bradley_terry.llama3
- 函数
  - icr

prompt_strategies.bradley_terry.llama3

用于包含 system、input、chosen、rejected 字段的数据集的 chatml 转换功能，旨在使其符合 llama3 对话模板格式。

适用于包含 system、input、chosen、rejected 字段的数据集的 chatml 转换示例，参见：https://huggingface.co/datasets/argilla/distilabel-intel-orca-dpo-pairs

**示例：**

示例 1（Python）：
```python
prompt_strategies.bradley_terry.llama3.icr(cfg, **kwargs)
```

## common.datasets

**网址：** https://docs.axolotl.ai/docs/api/common.datasets.html

**内容：**
- common.datasets
- 类
  - TrainDatasetMeta
- 函数
  - load_datasets
    - 参数
    - 返回值
  - load_preference_datasets
    - 参数
    - 返回值

用于加载数据集的工具函数。

该数据类包含用于存储训练集、验证集及其元数据的字段。

通过调用 axolotl.utils.data.prepare_datasets 函数来加载一个或多个训练集或评估集。可选地，会输出调试信息。

通过调用 axolotl.utils.data.rl.prepare_preference_datasets 函数来加载用于强化学习训练的配对偏好数据对应的训练集或评估集。可选地，会输出调试信息。

从数据集中随机有放回地抽取 num_samples 个样本。

**示例：**

示例 1（Python）：
```python
common.datasets.TrainDatasetMeta(
    train_dataset,
    eval_dataset=None,
    total_num_steps=None,
)
```

示例 2（Python）：
```python
common.datasets.load_datasets(cfg, cli_args=None, debug=False)
```

示例 3（Python）：
```python
common.datasets.load_preference_datasets(cfg, cli_args=None)
```

示例 4（Python）：
```python
common.datasets.sample_dataset(dataset, num_samples)
```

## cli.train

**URL:** https://docs.axolotl.ai/docs/api/cli.train.html

**内容：**
- cli.train
- 函数
  - do_cli
    - 参数
  - do_train
    - 参数

用于对模型进行训练的 CLI 工具。

该工具会解析 axolotl 配置文件及 CLI 参数，随后调用 do_train 函数。其工作流程为：首先加载 axolotl 配置中指定的数据集，然后调用 axolotl.train.train 方法来训练 transformers 模型。在训练完成后，还会启动插件管理器的 post_train_unload 功能。

**示例：**

示例 1（Python）：
```python
cli.train.do_cli(config=Path('examples/'), **kwargs)
```

示例 2（Python）：
```python
cli.train.do_train(cfg, cli_args)
```

## cli.utils.fetch

**网址：** https://docs.axolotl.ai/docs/api/cli.utils.fetch.html

**目录结构：**
- cli.utils.fetch
- 函数
  - fetch_from_github
    - 参数

用于 axolotl fetch CLI 命令的实用工具。

从 GitHub 仓库中的指定目录同步文件，仅下载本地不存在或已更改的文件。

**示例：**

示例 1（Python）：
```python
cli.utils.fetch.fetch_from_github(dir_prefix, dest_dir=None, max_workers=5)
```

## utils.tokenization

**网址：** https://docs.axolotl.ai/docs/api/utils.tokenization.html

**目录：**
- utils.tokenization
- 函数
  - color_token_for_rl_debug
  - process_tokens_for_rl_debug

用于token化操作的工具模块

根据token类型为其着色的辅助函数。

用于处理并着色token的辅助函数。

**示例：**

示例 1（Python）：
```python
utils.tokenization.color_token_for_rl_debug(
    decoded_token,
    encoded_token,
    color,
    text_only,
)
```

示例 2（Python）：
```python
utils.tokenization.process_tokens_for_rl_debug(
    tokens,
    color,
    tokenizer,
    text_only,
)
```

## core.trainers.grpo.sampler

**URL:** https://docs.axolotl.ai/docs/api/core.trainers.grpo.sampler.html

**内容：**
- core.trainers.grpo.sampler
- 类
  - SequenceParallelRepeatRandomSampler
    - 参数
    - 方法
      - set_epoch
        - 参数

core.trainers.grpo.sampler

重复随机采样器（与 https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py 中实现的版本类似），增加了序列并行功能；即在同一序列并行组内的各节点之间复制数据。

用于支持序列并行结构的 GRPO 训练的采样器。

该采样器可确保：- 同一序列并行（SP）组中的各个节点接收相同的数据。- 每个索引会被重复多次，以便生成不同的输出结果。- 整个批次会被重复使用，以便在多次迭代中加以利用。- 数据能够在各 SP 组之间得到合理分配。

下表中的数值代表数据集索引。每个 SP 组包含 context_parallel_size = 2 块 GPU，共同处理相同的数据。总共有 2 个 SP 组（SP0 和 SP1），整体 GPU 数量为 world_size = 4。

grad_accum=2 ▲ ▲ 0 0 [0 0 0 1 1 1] [2 2 2 3 3 3] <- 各 SP 组获取不同数据 ▼ | 0 1 [0 0 0 1 1 1] [2 2 2 3 3 3] <- 每个 SP 组的 GPU 获取相同数据 | | 1 2 [0 0 0 1 1 1] [2 2 2 3 3 3] <- 在 num_iterations=2 次迭代中重复使用相同索引 ▼ 1 3 [0 0 0 1 1 1] [2 2 2 3 3 3] <- 使用梯度累积时的情况

用于设置该采样器的训练轮数。

**示例：**

示例 1（Python）：
```python
core.trainers.grpo.sampler.SequenceParallelRepeatRandomSampler(
    dataset,
    mini_repeat_count,
    world_size,
    rank,
    batch_size=1,
    repeat_count=1,
    context_parallel_size=1,
    shuffle=True,
    seed=0,
    drop_last=False,
)
```

示例 2（未知情况）：
```unknown
Sequence Parallel Groups
                                |       SP0        |       SP1        |
                                |  GPU 0  |  GPU 1 |  GPU 2  |  GPU 3 |
            global_step  step    <---> mini_repeat_count=3
                                    <----------> batch_size=2 per SP group
```

示例 3（未知情况）：
```unknown
2       4         [4 4 4  5 5 5]     [6 6 6  7 7 7]   <- New batch of data indices
                 2       5         [4 4 4  5 5 5]     [6 6 6  7 7 7]
                                    ...
```

示例 4（Python）：
```python
core.trainers.grpo.sampler.SequenceParallelRepeatRandomSampler.set_epoch(epoch)
```

## evaluate

**URL:** https://docs.axolotl.ai/docs/api/evaluate.html

**目录:**
- evaluate
- 函数
  - evaluate
    - 参数
    - 返回值
  - evaluate_dataset
    - 参数
    - 返回值

用于评估模型的模块。

可在训练集和验证集上对模型进行评估。

用于评估单个数据集的辅助函数。

**示例:**

示例 1（Python）：
```python
evaluate.evaluate(cfg, dataset_meta)
```

示例 2（Python）：
```python
evaluate.evaluate_dataset(trainer, dataset, dataset_type, flash_optimum=False)
```

## utils.optimizers.adopt

**网址：** https://docs.axolotl.ai/docs/api/utils.optimizers.adopt.html

**目录：**
- utils.optimizers.adopt
- 函数
  - adopt

utils.optimizers.adopt

复制自 https://github.com/iShohei220/adopt

ADOPT：基于改良的Adam算法，可利用任意β2值以最优速率收敛（2024），作者包括Taniguchi, Shohei、Harada, Keno、Minegishi, Gouki、Oshima, Yuta、Jeong, Seong Cheol、Nagahara, Go、Iiyama, Tomoshi、Suzuki, Masahiro、Iwasawa, Yusuke以及Matsuo, Yutaka

用于执行ADOPT算法计算的功能接口。

**示例：**

示例1（Python）：
```python
utils.optimizers.adopt.adopt(
    params,
    grads,
    exp_avgs,
    exp_avg_sqs,
    state_steps,
    foreach=None,
    capturable=False,
    differentiable=False,
    fused=None,
    grad_scale=None,
    found_inf=None,
    has_complex=False,
    *,
    beta1,
    beta2,
    lr,
    clip_lambda,
    weight_decay,
    decouple,
    eps,
    maximize,
)
```

## prompt_tokenizers

**网址：** https://docs.axolotl.ai/docs/api/prompt_tokenizers.html

**内容：**
- prompt_tokenizers
- 类
  - AlpacaMultipleChoicePromptTokenizingStrategy
  - AlpacaPromptTokenizingStrategy
  - AlpacaReflectionPTStrategy
  - DatasetWrappingStrategy
  - GPTeacherPromptTokenizingStrategy
  - InstructionPromptTokenizingStrategy
  - InvalidDataException
  - JeopardyPromptTokenizingStrategy

包含 PromptTokenizingStrategy 和 Prompter 类的模块

用于处理 Alpaca 多项选择式提示的分词策略。

用于处理 Alpaca 提示的分词策略。

用于处理 Alpaca 反思型提示的分词策略。

用于为聊天消息封装数据集的抽象类

用于处理 GPTeacher 提示的分词策略。

用于处理基于指令的提示的分词策略。

当数据无效时抛出的异常

用于处理 Jeopardy 类型提示的分词策略。

用于处理 NomicGPT4All 类型提示的分词策略。

用于处理 OpenAssistant 类型提示的分词策略。

分词策略的抽象类

用于处理反思型提示的分词策略。

用于处理总结型提示的分词策略。

解析已分词的提示，并将对应的分词后的 input_ids、attention_mask 和标签添加到结果中

返回提示分词函数的默认值

**示例：**

示例 1（Python）：
```python
prompt_tokenizers.AlpacaMultipleChoicePromptTokenizingStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

示例 2（Python）：
```python
prompt_tokenizers.AlpacaPromptTokenizingStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

示例 3（Python）：
```python
prompt_tokenizers.AlpacaReflectionPTStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

示例 4（Python）：
```python
prompt_tokenizers.DatasetWrappingStrategy()
```

## cli.art

**网址：** https://docs.axolotl.ai/docs/api/cli.art.html

**内容：**
- cli.art
- 函数
  - print_axolotl_text_art

Axolotl ASCII 徽标相关工具。

用于打印 Axolotl 的 ASCII 图形。

**示例：**

示例 1（Python）：
```python
cli.art.print_axolotl_text_art()
```

## utils.callbacks.perplexity

**URL:** https://docs.axolotl.ai/docs/api/utils.callbacks.perplexity.html

**目录:**
- utils.callbacks.perplexity
- 类
  - Perplexity
    - 方法
      - compute

utils.callbacks.perplexity

用于计算困惑度这一评估指标的回调函数。

该函数按照 https://huggingface.co/docs/transformers/en/perplexity 中的定义来计算困惑度。这是一个自定义版本，无需对输入进行重新分词处理，也无需重新加载模型。

会在序列上以固定长度的滑动窗口方式计算困惑度。

**示例:**

示例 1（Python）：
```python
utils.callbacks.perplexity.Perplexity(tokenizer, max_seq_len, stride=512)
```

示例 2（Python）：
```python
utils.callbacks.perplexity.Perplexity.compute(model, references=None)
```

## cli.utils.train

**网址：** https://docs.axolotl.ai/docs/api/cli.utils.train.html

**目录结构：**
- cli.utils.train
- 函数
  - build_command
    - 参数
    - 返回值
  - generate_config_files
    - 参数
  - launch_training

用于 axolotl train CLI 命令的实用工具。

根据基础命令和选项生成命令列表。

生成需要处理的配置文件列表。每次迭代会返回一个元组，包含配置文件名称以及一个布尔值，该值指示该文件是否属于一组配置（即参数扫描组合）。

使用指定的配置执行训练任务。

**示例：**

示例 1（Python）：
```python
cli.utils.train.build_command(base_cmd, options)
```

示例 2（Python）：
```python
cli.utils.train.generate_config_files(config, sweep)
```

示例 3（Python）：
```python
cli.utils.train.launch_training(
    cfg_file,
    launcher,
    cloud,
    kwargs,
    launcher_args=None,
    use_exec=False,
)
```

## cli.vllm_serve

**网址：** https://docs.axolotl.ai/docs/api/cli.vllm_serve.html

**目录结构：**
- cli.vllm_serve
- 类
  - AxolotlScriptArguments
- 函数
  - do_vllm_serve
    - 返回值

用于启动用于在线强化学习的 VLLM 服务器的命令行工具。

VLLM 服务器的额外参数

用于启动用于服务在线强化学习中使用的 LLM 模型的 VLLM 服务器。

参数：
:param cfg: 解析后的 YAML 配置文档
:param cli_args: 类型为 VllmServeCliArgs 的额外命令行参数字典

**示例：**

示例 1（Python）：
```python
cli.vllm_serve.AxolotlScriptArguments(
    reasoning_parser='',
    enable_reasoning=None,
)
```

示例 2（Python）：
```python
cli.vllm_serve.do_vllm_serve(config, cli_args)
```

## convert

**URL:** https://docs.axolotl.ai/docs/api/convert.html

**目录：**
- convert
- 类
  - FileReader
  - FileWriter
  - JsonParser
  - JsonToJsonlConverter
  - JsonlSerializer
  - StdoutWriter

该模块包含 File Reader、File Writer、Json Parser 以及 Jsonl Serializer 等类。

读取文件并将其内容作为字符串返回。

将字符串写入文件。

将字符串解析为 JSON 格式并返回解析结果。

将 JSON 文件转换为 JSONL 格式。

将一组 JSON 对象序列化为 JSONL 字符串。

将字符串输出到标准输出。

**示例：**

示例 1（Python）：
```python
convert.FileReader()
```

示例 2（Python）：
```python
convert.FileWriter(file_path)
```

示例 3（Python）：
```python
convert.JsonParser()
```

示例 4（Python）：
```python
convert.JsonToJsonlConverter(
    file_reader,
    file_writer,
    json_parser,
    jsonl_serializer,
)
```

## monkeypatch.utils

**网址：** https://docs.axolotl.ai/docs/api/monkeypatch.utils.html

**目录：**
- monkeypatch.utils
- 函数
  - get_cu_seqlens
  - get_cu_seqlens_from_pos_ids
  - mask_2d_to_4d

用于 monkeypatches 的共享工具函数

使用注意力掩码为闪存注意力机制生成累积序列长度掩码

使用位置编号为闪存注意力机制生成累积序列长度掩码

该函数将 attention_mask 从 [bsz, seq_len] 格式扩展为 [bsz, 1, tgt_seq_len, src_seq_len] 格式。这种扩展方式能够处理打包后的序列，使得同一序列内的不同元素在相互关注时共享相同的注意力掩码整数值。此外，该函数还会将掩码转换为下三角矩阵形式，从而防止后续的“窥视”行为。

**示例：**

示例 1（Python）：
```python
monkeypatch.utils.get_cu_seqlens(attn_mask)
```

示例 2（Python）：
```python
monkeypatch.utils.get_cu_seqlens_from_pos_ids(position_ids)
```

示例 3（Python）：
```python
monkeypatch.utils.mask_2d_to_4d(mask, dtype, tgt_len=None)
```

## prompt_strategies.pygmalion

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.pygmalion.html

**内容概览：**
- prompt_strategies.pygmalion
- 类
  - PygmalionPromptTokenizingStrategy
  - PygmalionPrompter

prompt_strategies.pygmalion

包含 PygmalionPromptTokenizingStrategy 和 PygmalionPrompter 类的模块

用于 Pygmalion 模型的分词策略。

用于 Pygmalion 模型的提示词生成器。

**示例：**

示例 1（Python）：
```python
prompt_strategies.pygmalion.PygmalionPromptTokenizingStrategy(
    prompter,
    tokenizer,
    *args,
    **kwargs,
)
```

示例 2（Python）：
```python
prompt_strategies.pygmalion.PygmalionPrompter(*args, **kwargs)
```

## utils.callbacks.mlflow_

**网址：** https://docs.axolotl.ai/docs/api/utils.callbacks.mlflow_.html

**目录结构：**
- utils.callbacks.mlflow_
- 类
  - SaveAxolotlConfigtoMlflowCallback

utils.callbacks.mlflow_

用于训练器回调功能的 MLFlow 模块

用于将 Axolotl 配置保存到 MLFlow 的回调功能

**示例：**

示例 1（Python）：
```python
utils.callbacks.mlflow_.SaveAxolotlConfigtoMlflowCallback(axolotl_config_path)
```

## loaders.adapter

**网址：** https://docs.axolotl.ai/docs/api/loaders.adapter.html

**目录：**
- loaders.adapter
- 函数
  - setup_quantized_meta_for_peft
  - setup_quantized_peft_meta_for_training

该模块提供适配器加载功能，包括 LoRA / QLoRA 及相关辅助工具。

它会用一个虚拟函数替换 quant_state.to，以防止 PEFT 将 quant_state 移动到元设备上；随后再将该虚拟函数替换为原始函数，从而让训练能够继续进行。

**示例：**

示例 1（Python）：
```python
loaders.adapter.setup_quantized_meta_for_peft(model)
```

示例 2（Python）：
```python
loaders.adapter.setup_quantized_peft_meta_for_training(model)
```

## cli.cloud.base

**网址：** https://docs.axolotl.ai/docs/api/cli.cloud.base.html

**目录：**
- cli.cloud.base
- 类
  - Cloud

来自 CLI 的云平台基类。

云平台的抽象基类。

**示例：**

示例 1（Python）：
```python
cli.cloud.base.Cloud()
```

## monkeypatch.llama_attn_hijack_flash

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.llama_attn_hijack_flash.html

**内容：**
- monkeypatch.llama_attn_hijack_flash
- 函数
  - flashattn_forward_with_s2attn

monkeypatch.llama_attn_hijack_flash

用于 llama 模型的闪存注意力机制补丁

输入形状：Batch x Time x Channel

来源：https://github.com/dvlab-research/LongLoRA/blob/main/llama_attn_replace.py

attention_mask: [bsz, q_len]

如果提供了 cu_seqlens，则会忽略该参数；如果提供了 max_seqlen，也会被忽略。

**示例：**

示例 1（Python）：
```python
monkeypatch.llama_attn_hijack_flash.flashattn_forward_with_s2attn(
    self,
    hidden_states,
    attention_mask=None,
    position_ids=None,
    past_key_value=None,
    output_attentions=False,
    use_cache=False,
    padding_mask=None,
    cu_seqlens=None,
    max_seqlen=None,
)
```

## monkeypatch.llama_patch_multipack

**网址：** https://docs.axolotl.ai/docs/api/monkeypatch.llama_patch_multipack.html

**内容：**
- monkeypatch.llama_patch_multipack

monkeypatch.llama_patch_multipack

对该函数进行修补，使其使用 torch.nn.functional.scaled_dot_product_attention 算法。

---

## cli.inference

**网址：** https://docs.axolotl.ai/docs/api/cli.inference.html

**内容：**
- cli.inference
- 函数
  - do_cli
    - 参数
  - do_inference
    - 参数
  - do_inference_gradio
    - 参数
  - get_multi_line_input
    - 返回值

用于对已训练模型执行推理的命令行工具。

该工具会解析 axolotl 配置文件及命令行参数，随后调用 do_inference 或 do_inference_gradio 函数来执行推理。

在命令行界面中以循环方式运行推理过程：首先接收用户输入，（可选地）应用聊天模板，然后根据默认的生成配置，使用 axolotl 配置中指定的模型来生成回复内容。

在 Gradio 界面中执行推理。同样会接收用户输入，（可选地）应用聊天模板，之后依据默认的生成配置，利用 axolotl 配置中指定的模型来生成回复内容。

从终端获取多行输入。

**示例：**

示例 1（Python）：
```python
cli.inference.do_cli(config=Path('examples/'), gradio=False, **kwargs)
```

示例 2（Python）：
```python
cli.inference.do_inference(cfg, cli_args)
```

示例 3（Python）：
```python
cli.inference.do_inference_gradio(cfg, cli_args)
```

示例 4（Python）：
```python
cli.inference.get_multi_line_input()
```

## loaders.tokenizer

**URL:** https://docs.axolotl.ai/docs/api/loaders.tokenizer.html

**目录:**
- loaders.tokenizer
- 函数
  - load_tokenizer
  - modify_tokenizer_files
    - 参数
    - 返回值

用于加载分词器及相关工具函数

根据提供的配置加载并配置分词器。

修改分词器文件以替换其中的 added_tokens 字符串，将其保存到指定输出目录，并返回已修改分词器的路径。

该功能仅适用于添加到分词器中的预留标记，而不适用于已存在于词汇表中的标记。

参考链接：https://github.com/huggingface/transformers/issues/27974#issuecomment-1854188941

**示例:**

示例 1（Python）：
```python
loaders.tokenizer.load_tokenizer(cfg)
```

示例 2（Python）：
```python
loaders.tokenizer.modify_tokenizer_files(
    tokenizer_path,
    token_mappings,
    output_dir,
)
```

## cli.utils.sweeps

**网址：** https://docs.axolotl.ai/docs/api/cli.utils.sweeps.html

**目录：**
- cli.utils.sweeps
- 函数
  - generate_sweep_configs
    - 参数
    - 返回值
    - 示例

用于处理 axolotl 训练 CLI 命令中配置参数遍历的实用工具。

通过对基础配置应用参数遍历，递归生成所有可能的配置组合。

sweeps_config = { ‘learning_rate’: [0.1, 0.01], ’_’: [ {‘load_in_8bit’: True, ‘adapter’: ‘lora’}, {‘load_in_4bit’: True, ‘adapter’: ‘qlora’} ] }

**示例：**

示例 1（Python）：
```python
cli.utils.sweeps.generate_sweep_configs(base_config, sweeps_config)
```

## prompt_strategies.dpo.chatml

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.dpo.chatml.html

**内容概览：**
- prompt_strategies.dpo.chatml
- 函数
  - argilla_chat
  - icr
  - intel
  - ultra

prompt_strategies.dpo.chatml

用于 chatml 的 DPO 策略

适用于 argilla/dpo-mix-7k 对话场景

针对包含系统信息、输入内容、选定选项及拒绝选项的数据集的 chatml 转换方式，示例地址：https://huggingface.co/datasets/argilla/distilabel-intel-orca-dpo-pairs

用于 Intel Orca DPO Pairs 数据集

适用于 ultrafeedback 二值化对话场景

**示例：**

示例 1（Python）：
```python
prompt_strategies.dpo.chatml.argilla_chat(cfg, **kwargs)
```

示例 2（Python）：
```python
prompt_strategies.dpo.chatml.icr(cfg, **kwargs)
```

示例 3（Python）：
```python
prompt_strategies.dpo.chatml.intel(cfg, **kwargs)
```

示例 4（Python）：
```python
prompt_strategies.dpo.chatml.ultra(cfg, **kwargs)
```

## cli.quantize

**网址：** https://docs.axolotl.ai/docs/api/cli.quantize.html

**目录：**
- cli.quantize
- 函数
  - do_quantize
    - 参数

用于通过 torchao 对训练后的模型进行量化处理的命令行工具。

可对模型的权重进行量化处理。

**示例：**

示例 1（Python）：
```python
cli.quantize.do_quantize(config, cli_args)
```

## utils.dict

**URL:** https://docs.axolotl.ai/docs/api/utils.dict.html

**内容：**
- utils.dict
- 类
  - DictDefault
- 函数
  - remove_none_values

该模块包含 DictDefault 类，当键不存在时，它会返回 None 而非空字典。

用于从类似字典的对象或列表中移除 null 值。这些值可能因数据集加载过程中模式合并而产生。详情请参见 https://github.com/axolotl-ai-cloud/axolotl/pull/2909

**示例：**

示例 1（Python）：
```python
utils.dict.DictDefault()
```

示例 2（Python）：
```python
utils.dict.remove_none_values(obj)
```

## API 参考文档

**网址：** https://docs.axolotl.ai/docs/api/

**目录结构：**
- API 参考文档
- 核心功能模块
- 命令行界面
- 训练相关功能
- 模型加载与修补功能
- 混合类
- 上下文管理器
- 提示词格式化策略
- 内核函数
- 动态修补功能

涵盖模型训练的核心功能、命令行接口、训练实现方式，以及模型、分词器等组件的加载与修补功能。同时提供用于增强训练器的混合类、用于调整训练器行为的上下文管理器、提示词格式化策略，以及底层性能优化功能。此外还包括用于模型优化的运行时修补功能、Axolotl 配置的 Pydantic 数据模型、第三方集成与扩展功能，以及通用工具和共享功能，还支持自定义模型实现与数据处理工具。

---

## monkeypatch.lora_kernels

**网址：** https://docs.axolotl.ai/docs/api/monkeypatch.lora_kernels.html

**目录结构：**
- monkeypatch.lora_kernels
- 类
  - FakeMLP
- 函数
  - apply_lora_kernel_patches
    - 参数说明
    - 返回值
    - 异常情况
    - 备注
  - get_attention_cls_from_config

monkeypatch.lora_kernels

用于修补自定义 LoRA Triton 内核及 torch.autograd 函数的模块。

用于 Triton 修补的占位 MLP 结构

将优化后的 Triton 内核修补应用到 PEFT 模型中。

为 PEFT 模型提供经过优化的 MLP 和注意力计算实现，这些优化包括针对激活函数的自定义 Triton 内核，以及专为 LoRA 计算设计的专用自动求导函数。

此类优化要求 LoRA 适配器不包含丢弃层和偏置项；若不满足这些条件，该函数将跳过修补操作。

通过检查模型配置来获取合适的注意力类。采用动态导入机制，可支持遵循标准 transformers 命名规范的各类模型架构。

用于获取模型的各层结构，同时支持纯文本模型与多模态模型。

未经优化的输出投影功能原始实现。

未经优化的 QKV 投影功能原始实现。

给定 Axolotl 模型配置后，该函数会用优化后的 LoRA 实现替换推理过程中的注意力类前向传播逻辑。

它会修改注意力类，使其使用优化后的 QKV 和输出投影功能；同时保留原始实现，必要时可恢复使用。

**示例：**

示例 1（Python）：
```python
monkeypatch.lora_kernels.FakeMLP(gate_proj, up_proj, down_proj)
```

示例 2（Python）：
```python
monkeypatch.lora_kernels.apply_lora_kernel_patches(model, cfg)
```

示例 3（Python）：
```python
monkeypatch.lora_kernels.get_attention_cls_from_config(cfg)
```

示例 4（Python）：
```python
monkeypatch.lora_kernels.get_layers(model)
```

## monkeypatch.stablelm_attn_hijack_flash

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.stablelm_attn_hijack_flash.html

**内容：**
- monkeypatch.stablelm_attn_hijack_flash
- 函数
  - repeat_kv
  - rotate_half

monkeypatch.stablelm_attn_hijack_flash

PyTorch StableLM Epoch 模型。

该功能相当于 torch.repeat_interleave(x, dim=1, repeats=n_rep)。其作用是将隐藏状态从 (batch, num_key_value_heads, seqlen, head_dim) 格式转换为 (batch, num_attention_heads, seqlen, head_dim) 格式，并对输入中的部分隐藏维度进行旋转处理。

**示例：**

示例 1（Python）：
```python
monkeypatch.stablelm_attn_hijack_flash.repeat_kv(hidden_states, n_rep)
```

示例 2（Python）：
```python
monkeypatch.stablelm_attn_hijack_flash.rotate_half(x)
```

## core.trainers.mixins.rng_state_loader

**网址：** https://docs.axolotl.ai/docs/api/core.trainers.mixins.rng_state_loader.html

**内容：**
- core.trainers.mixins.rng_state_loader
- 类
  - RngLoaderMixin

core.trainers.mixins.rng_state_loader

用于修复从检查点恢复时出现的错误的临时解决方案/替代方案

请参阅 https://github.com/huggingface/transformers/pull/37162

待办事项：当上游项目提交正式版本更新后予以移除

用于重写方法以从检查点加载随机数状态的混合类

**示例：**

示例 1（Python）：
```python
core.trainers.mixins.rng_state_loader.RngLoaderMixin()
```

## core.trainers.utils

**网址：** https://docs.axolotl.ai/docs/api/core.trainers.utils.html

**内容：**
- core.trainers.utils

用于 Axolotl 训练器的工具函数

---

## core.training_args

**网址：** https://docs.axolotl.ai/docs/api/core.training_args.html

**内容：**
- core.training_args
- 类
  - AxolotlCPOConfig
  - AxolotlKTOConfig
  - AxolotlORPOConfig
  - AxolotlPRMConfig
  - AxolotlRewardConfig
  - AxolotlTrainingArguments

其他针对 Axolotl 的特定训练参数

用于 CPO 训练的配置

用于 KTO 训练的配置

用于 ORPO 训练的配置

用于 PRM 训练的配置

用于奖励函数训练的配置

用于因果训练器的训练参数

由于 HF 的 TrainingArguments 未为 output_dir 设置默认值，该代码被重复编写，因此无法作为混合类使用。

**示例：**

示例 1（Python）：
```python
core.training_args.AxolotlCPOConfig(simpo_gamma=None)
```

示例 2（Python）：
```python
core.training_args.AxolotlKTOConfig()
```

示例 3（Python）：
```python
core.training_args.AxolotlORPOConfig()
```

示例 4（Python）：
```python
core.training_args.AxolotlPRMConfig()
```

---

## monkeypatch.btlm_attn_hijack_flash

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.btlm_attn_hijack_flash.html

**内容：**
- monkeypatch.btlm_attn_hijack_flash

monkeypatch.btlm_attn_hijack_flash

用于 cerebras btlm 模型的 Flash Attention 动态补丁

---

## prompt_strategies.dpo.passthrough

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.dpo.passthrough.html

**内容：**
- prompt_strategies.dpo.passthrough

prompt_strategies.dpo.passthrough

DPO 提示策略的直接传递/零处理策略

---

## kernels.swiglu

**URL:** https://docs.axolotl.ai/docs/api/kernels.swiglu.html

**内容：**
- kernels.swiglu
- 函数
  - swiglu_backward
    - 参数
    - 返回值
  - swiglu_forward
    - 参数
    - 返回值

用于定义 SwiGLU Triton 核心的模块。

参考论文《GLU 变体提升 Transformer 性能》（https://arxiv.org/abs/2002.05202）。

此实现的灵感来源于 unsloth（https://unsloth.ai/）。

使用原地操作实现 SwiGLU 的反向传播。

实现 SwiGLU 的正向传播，计算 SwiGLU 激活值：x * sigmoid(x) * up，其中 x 为门控张量。

**示例：**

示例 1（Python）：
```python
kernels.swiglu.swiglu_backward(grad_output, gate, up)
```

示例 2（Python）：
```python
kernels.swiglu.swiglu_forward(gate, up)
```

## core.trainers.grpo.trainer

**URL:** https://docs.axolotl.ai/docs/api/core.trainers.grpo.trainer.html

**内容：**
- core.trainers.grpo.trainer
- 类
  - AxolotlGRPOSequenceParallelTrainer
    - 方法
      - get_train_dataloader
  - AxolotlGRPOTrainer

core.trainers.grpo.trainer

Axolotl GRPO训练器（支持及不支持序列并行处理）

扩展基础GRPOTrainer以实现序列并行处理功能

获取用于训练的数据加载器

扩展基础GRPOTrainer以集成Axolotl相关辅助功能

**示例：**

示例1（Python）：
```python
core.trainers.grpo.trainer.AxolotlGRPOSequenceParallelTrainer(
    model,
    reward_funcs,
    args=None,
    train_dataset=None,
    eval_dataset=None,
    processing_class=None,
    reward_processing_classes=None,
    callbacks=None,
    optimizers=(None, None),
    peft_config=None,
    optimizer_cls_and_kwargs=None,
)
```

示例 2（Python）：
```python
core.trainers.grpo.trainer.AxolotlGRPOSequenceParallelTrainer.get_train_dataloader(
)
```

示例 3（Python）：
```python
core.trainers.grpo.trainer.AxolotlGRPOTrainer(*args, **kwargs)
```

## prompt_strategies.user_defined

**文档地址：** https://docs.axolotl.ai/docs/api/prompt_strategies.user_defined.html

**内容概要：**
- prompt_strategies.user_defined
- 类别
  - UserDefinedDatasetConfig
  - UserDefinedPromptTokenizationStrategy

prompt_strategies.user_defined

通过 YML 配置文件定义的自定义提示词

用于表示自定义数据集类型的 dataclass 配置

针对自定义提示词的提示词分词策略

**示例：**

示例 1（Python）：
```python
prompt_strategies.user_defined.UserDefinedDatasetConfig(
    system_prompt='',
    field_system='system',
    field_instruction='instruction',
    field_input='input',
    field_output='output',
    format='{instruction} {input} ',
    no_input_format='{instruction} ',
    system_format='{system}',
)
```

示例 2（Python）：
```python
prompt_strategies.user_defined.UserDefinedPromptTokenizationStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

## utils.schemas.training

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.training.html

**内容：**
- utils.schemas.training
- 类
  - HyperparametersConfig
  - JaggedLRConfig
  - LrGroup

utils.schemas.training

用于配置训练超参数的 Pydantic 模型

训练超参数的配置子集

JaggedLR 配置子集，可用于 ReLoRA 训练

自定义学习率分组配置

**示例：**

示例 1（Python）：
```python
utils.schemas.training.HyperparametersConfig()
```

示例 2（Python）：
```python
utils.schemas.training.JaggedLRConfig()
```

示例 3（Python）：
```python
utils.schemas.training.LrGroup()
```

## utils.quantization

**URL:** https://docs.axolotl.ai/docs/api/utils.quantization.html

**目录:**
- utils.quantization
- 函数
  - convert_qat_model
  - get_quantization_config
    - 参数
    - 返回值
    - 异常
  - prepare_model_for_qat
    - 参数
    - 异常

这些工具用于基于torchao实现QAT和PTQ等量化操作。

该函数可将包含伪量化层的QAT模型转换回原始模型。

该函数用于生成训练后的量化配置。

该函数通过将模型中的线性层替换为伪量化的线性层，可选地还将嵌入权重替换为伪量化的嵌入权重，从而为QAT准备模型。

该函数用于对模型进行量化操作。

**示例:**

示例 1（Python）：
```python
utils.quantization.convert_qat_model(model, quantize_embedding=False)
```

示例 2（Python）：
```python
utils.quantization.get_quantization_config(
    weight_dtype,
    activation_dtype=None,
    group_size=None,
)
```

示例 3（Python）：
```python
utils.quantization.prepare_model_for_qat(
    model,
    weight_dtype,
    group_size=None,
    activation_dtype=None,
    quantize_embedding=False,
)
```

示例 4（Python）：
```python
utils.quantization.quantize_model(
    model,
    weight_dtype,
    group_size=None,
    activation_dtype=None,
    quantize_embedding=None,
)
```

## logging_config

**URL:** https://docs.axolotl.ai/docs/api/logging_config.html

**内容：**
- logging_config
- 类
  - AxolotlLogger
  - AxolotlOrWarnErrorFilter
  - ColorfulFormatter
- 函数
  - configure_logging

Axolotl 的通用日志模块。

会对非 Axolotl 日志记录应用过滤规则的日志器。

默认允许所有 WARNING 级别及以上的日志（除非被 LOG_LEVEL 覆盖）；允许所有 axolotl.* 开头的日志在 INFO 级别及以上（除非被 AXOLOTL_LOG_LEVEL 覆盖）；默认会忽略所有其他类型的日志记录（即非 axolotl.INFO、DEBUG 等级别）。

根据日志类型为日志消息添加颜色格式化的功能。

可使用默认日志配置进行设置。

**示例：**

示例 1（Python）：
```python
logging_config.AxolotlLogger(name, level=logging.NOTSET)
```

示例 2（Python）：
```python
logging_config.AxolotlOrWarnErrorFilter(**kwargs)
```

示例 3（Python）：
```python
logging_config.ColorfulFormatter()
```

示例 4（Python）：
```python
logging_config.configure_logging()
```

## prompt_strategies.stepwise_supervised

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.stepwise_supervised.html

**内容概要：**
- prompt_strategies.stepwise_supervised
- 类别
  - StepwiseSupervisedPromptTokenizingStrategy

prompt_strategies.stepwise_supervised

用于处理分步数据集的模块，这类数据集通常包含提示语、推理过程记录，以及（可选的）用于奖励建模的每一步或每个提示-推理记录对应的标签。

这是一种针对有监督分步数据集的分词策略，常用于COT推理任务。此类数据集应包含以下列：  
- prompt：提示语文本  
- completions：n个补全步骤的列表  
- labels：表示每个步骤“正确性”的n个标签列表  

**示例：**

示例 1（Python）：
```python
prompt_strategies.stepwise_supervised.StepwiseSupervisedPromptTokenizingStrategy(
    tokenizer,
    sequence_len=2048,
    step_separator='\n',
    max_completion_length=None,
    train_on_last_step_only=False,
)
```

## utils.schemas.model

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.model.html

**内容：**
- utils.schemas.model
- 类
  - ModelInputConfig
  - ModelOutputConfig
  - SpecialTokensConfig

用于模型输入/输出等配置的 Pydantic 模型

模型配置子集

模型保存配置子集

特殊标记配置子集

**示例：**

示例 1（Python）：
```python
utils.schemas.model.ModelInputConfig()
```

示例 2（Python）：
```python
utils.schemas.model.ModelOutputConfig()
```

示例 3（Python）：
```python
utils.schemas.model.SpecialTokensConfig()
```

## utils.schemas.enums

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.enums.html

**内容概览：**
- utils.schemas.enums
- 类别
  - ChatTemplate
  - CustomSupportedOptimizers
  - RLType
  - RingAttnFunc

用于 Axolotl 输入配置的枚举类型

聊天模板相关配置子集

支持的自定义优化器列表

强化学习训练器类型配置子集

支持的环状注意力实现相关枚举类

**示例：**

示例 1（Python）：
```python
utils.schemas.enums.ChatTemplate()
```

示例 2（Python）：
```python
utils.schemas.enums.CustomSupportedOptimizers()
```

示例 3（Python）：
```python
utils.schemas.enums.RLType()
```

示例 4（Python）：
```python
utils.schemas.enums.RingAttnFunc()
```

## core.trainers.trl

**URL:** https://docs.axolotl.ai/docs/api/core.trainers.trl.html

**内容：**
- core.trainers.trl
- 类
  - AxolotlCPOTrainer
  - AxolotlKTOTrainer
  - AxolotlORPOTrainer
  - AxolotlPRMTrainer
  - AxolotlRewardTrainer

用于 TRL 强化学习训练器的模块

为 axolotl 工具扩展基础 CPOTrainer

为 axolotl 工具扩展基础 KTOTrainer

为 axolotl 工具扩展基础 ORPOTrainer

为 axolotl 工具扩展基础 trl.PRMTrainer

为 axolotl 工具扩展基础 RewardTrainer

**示例：**

示例 1（Python）：
```python
core.trainers.trl.AxolotlCPOTrainer(*args, **kwargs)
```

示例 2（Python）：
```python
core.trainers.trl.AxolotlKTOTrainer(*args, **kwargs)
```

示例 3（Python）：
```python
core.trainers.trl.AxolotlORPOTrainer(*args, **kwargs)
```

示例 4（Python）：
```python
core.trainers.trl.AxolotlPRMTrainer(*args, **kwargs)
```

## utils.schedulers

**URL:** https://docs.axolotl.ai/docs/api/utils.schedulers.html

**目录:**
- utils.schedulers
- 类
  - InterpolatingLogScheduler
  - JaggedLRRestartScheduler
  - RexLR
    - 参数
- 函数
  - get_cosine_schedule_with_min_lr
    - 用于创建学习率调度方案
  - get_cosine_schedule_with_quadratic_warmup

用于自定义 LRScheduler 类的模块

以对数方式插值调整学习率的调度器

用于在每个 LoRA 重启时应用学习率预热功能的调度器。

反射指数型（REX）学习率调度器。

该调度器会按照余弦函数的数值逐步降低学习率，从优化器中设置的初始学习率开始，经过线性上升的预热阶段后降至 0；也可根据特定参数设置从初始学习率降至 min_lr_ratio，持续到 num_training_steps * constant_lr_ratio 步之后，随后保持恒定的 min_rate 值。

基于 torch.optim.lr_scheduler.LambdaLR 并结合相应调度方案的实现。

参考文献：《大型语言模型的持续预训练：如何为模型进行（重新）预热？》（https://arxiv.org/pdf/2308.04014.pdf）。该调度器会按照余弦函数的数值逐步降低学习率，从优化器中设置的初始学习率开始，降至 min_lr_ratio，持续到 num_training_steps * constant_lr_ratio 步之后，随后保持恒定的 constant_lr 值；在预热阶段，学习率会从 0 线性上升至优化器中设置的初始学习率。

基于 torch.optim.lr_scheduler.LambdaLR 并结合相应调度方案的实现。

**示例:**

示例 1（Python）：
```python
utils.schedulers.InterpolatingLogScheduler(
    optimizer,
    num_steps,
    min_lr,
    max_lr,
    last_epoch=-1,
)
```

示例 2（Python）：
```python
utils.schedulers.JaggedLRRestartScheduler(
    optimizer,
    inner_schedule,
    jagged_restart_steps,
    jagged_restart_warmup_steps,
    jagged_restart_anneal_steps=1,
    min_lr_scale=0.001,
)
```

示例 3（Python）：
```python
utils.schedulers.RexLR(
    optimizer,
    max_lr,
    min_lr,
    total_steps=0,
    num_warmup_steps=0,
    last_step=0,
)
```

示例 4（Python）：
```python
utils.schedulers.get_cosine_schedule_with_min_lr(
    optimizer,
    num_warmup_steps,
    num_training_steps,
    min_lr_ratio=0.0,
)
```

## cli.merge_lora

**URL:** https://docs.axolotl.ai/docs/api/cli.merge_lora.html

**目录:**
- cli.merge_lora
- 函数
  - do_cli
    - 参数
    - 异常情况
  - do_merge_lora
    - 参数

用于将训练好的 LoRA 模块合并到基础模型中的 CLI 工具。

该工具会解析 axolotl 配置文件及 CLI 参数，随后调用 do_merge_lora 函数。为确保 LoRA 合并功能正常运行，部分配置值会被自动覆盖（如 load_in_8bit=False、load_in4bit=False、flash_attention=False 等）。

该工具会基于 axolotl 配置文件中指定的模型以及 LoRA 适配器，调用 transformers 库中的 merge_and_unload 函数，将它们整合为一个新的基础模型。

**示例:**

示例 1（Python）：
```python
cli.merge_lora.do_cli(config=Path('examples/'), **kwargs)
```

示例 2（Python）：
```python
cli.merge_lora.do_merge_lora(cfg)
```

## prompt_strategies.alpaca_w_system

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.alpaca_w_system.html

**内容：**
- prompt_strategies.alpaca_w_system
- 类别
  - InstructionWSystemPromptTokenizingStrategy
  - OpenOrcaPromptTokenizingStrategy
  - OpenOrcaSystemDataPrompter
  - SystemDataPrompter

prompt_strategies.alpaca_w_system

用于包含系统提示的 Alpaca 指令数据集的提示策略加载器。

针对基于指令的提示的分词策略。

针对 OpenOrca 数据集的分词策略。

一种使用数据集中的系统提示并结合 OpenOrca 提示的 Alpaca 风格提示器。

一种仅使用数据集中的系统提示的 Alpaca 风格提示器。

**示例：**

示例 1（Python）：
```python
prompt_strategies.alpaca_w_system.InstructionWSystemPromptTokenizingStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

示例 2（Python）：
```python
prompt_strategies.alpaca_w_system.OpenOrcaPromptTokenizingStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

示例 3（Python）：
```python
prompt_strategies.alpaca_w_system.OpenOrcaSystemDataPrompter(
    prompt_style=PromptStyle.INSTRUCT.value,
)
```

示例 4（Python）：
```python
prompt_strategies.alpaca_w_system.SystemDataPrompter(
    prompt_style=PromptStyle.INSTRUCT.value,
)
```

## loaders.patch_manager

**URL:** https://docs.axolotl.ai/docs/api/loaders.patch_manager.html

**内容：**
- loaders.patch_manager
- 类
  - PatchManager
    - 属性
    - 方法
      - apply_post_model_load_patches
      - apply_post_plugin_pre_model_load_patches
      - apply_pre_model_load_patches

loaders.patch_manager

用于补充 axolotl.loaders.ModelLoader 功能的补丁管理器类实现。

可应用模型加载前后的补丁，以实现各类修复与优化功能。

负责在模型加载过程中管理补丁的应用。

应用需要模型实例才能生效的补丁。

根据配置应用插件加载前模型加载阶段的补丁。

根据配置应用模型加载前的补丁。

**示例：**

示例 1（Python）：
```python
loaders.patch_manager.PatchManager(cfg, model_config, inference=False)
```

示例 2（Python）：
```python
loaders.patch_manager.PatchManager.apply_post_model_load_patches(model)
```

示例 3（Python）：
```python
loaders.patch_manager.PatchManager.apply_post_plugin_pre_model_load_patches()
```

示例 4（Python）：
```python
loaders.patch_manager.PatchManager.apply_pre_model_load_patches()
```

## utils.schemas.peft

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.peft.html

**目录结构：**
- utils.schemas.peft
- 类
  - LoftQConfig
  - LoraConfig
  - PeftConfig
  - ReLoRAConfig

用于 PEFT 相关配置的 Pydantic 模型

LoftQ 配置子集

Peft / LoRA 配置子集

peftq 配置子集

ReLoRA 配置子集

**示例：**

示例 1（Python）：
```python
utils.schemas.peft.LoftQConfig()
```

示例 2（Python）：
```python
utils.schemas.peft.LoraConfig()
```

示例 3（Python）：
```python
utils.schemas.peft.PeftConfig()
```

示例 4（Python）：
```python
utils.schemas.peft.ReLoRAConfig()
```

## common.const

**网址：** https://docs.axolotl.ai/docs/api/common.const.html

**内容：**
- common.const

各类共享的常量

---

## prompt_strategies.kto.user_defined

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.kto.user_defined.html

**内容：**
- prompt_strategies.kto.user_defined

prompt_strategies.kto.user_defined

用户自定义的KTO策略

---

## prompt_strategies.base

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.base.html

**内容：**
- prompt_strategies.base

prompt_strategies.base

用于基础数据集转换策略的模块

---

## cli.delinearize_llama4

**网址：** https://docs.axolotl.ai/docs/api/cli.delinearize_llama4.html

**内容：**
- cli.delinearize_llama4
- 函数
  - do_cli
    - 参数

cli.delinearize_llama4

用于将量化/线性化的Llama-4模型反线性化的CLI工具。

可将经过特殊处理的HF格式Llama4模型（投影部分已分离）转换回原始的HF格式（投影部分已合并）。

**示例：**

示例1（Python）：
```python
cli.delinearize_llama4.do_cli(model, output)
```

## integrations.base

**URL:** https://docs.axolotl.ai/docs/api/integrations.base.html

**Contents:**
- integrations.base
- 类
  - BaseOptimizerFactory
    - 方法
      - get_decay_parameter_names
  - BasePlugin
    - 备注
    - 方法
      - add_callbacks_post_trainer
        - 参数

所有插件的基类。

插件是一种可重用、模块化且独立的代码片段，用于扩展 Axolotl 的功能。插件可用于集成第三方模型、修改训练流程或添加新功能。

要创建新的插件，需要继承 BasePlugin 类并实现所需的方法。

用于创建自定义优化器的工厂基类

获取所有将应用权重衰减的参数名称。

该函数通过两种方式筛选参数：1. 按层类型筛选（属于 ALL_LAYERNORM_LAYERS 中指定的层类型）；2. 按参数名称模式筛选（包含“bias”或“norm”的变体形式）。

所有插件的基类，定义了插件方法的接口。

插件是一种可重用、模块化且独立的代码片段，用于扩展 Axolotl 的功能。插件可用于集成第三方模型、修改训练流程或添加新功能。

要创建新的插件，需要继承 BasePlugin 类并实现所需的方法。

插件方法包括：- register(cfg)：使用给定的配置注册插件。- load_datasets(cfg)：加载并预处理用于训练的数据集。- pre_model_load(cfg)：在模型加载之前执行操作。- post_model_build(cfg, model)：在模型加载后、应用 LoRA 适配器之前执行操作。- pre_lora_load(cfg, model)：在加载 LoRA 权重之前执行操作。- post_lora_load(cfg, model)：在加载 LoRA 权重之后执行操作。- post_model_load(cfg, model)：在模型加载完成后执行操作，包括所有适配器。- post_trainer_create(cfg, trainer)：在创建训练器之后执行操作。- create_optimizer(cfg, trainer)：创建并返回用于训练的优化器。- create_lr_scheduler(cfg, trainer, optimizer, num_training_steps)：创建并返回学习率调度器。- add_callbacks_pre_trainer(cfg, model)：在训练开始前为训练器添加回调函数。- add_callbacks_post_trainer(cfg, trainer)：在训练结束后为训练器添加回调函数。

在创建训练器之后为其添加回调函数。这对于那些需要访问模型或训练器的回调函数非常有用。

在创建训练器之前设置回调函数。

创建并返回学习率调度器。

创建并返回用于训练的优化器。

返回用于数据收集器的自定义类。

返回表示插件输入参数的 Pydantic 模型。

返回用于训练器的自定义类。

返回可用于设置 TrainingArgs 的自定义训练参数。

返回表示插件训练参数的数据类模型。

加载并预处理用于训练的数据集。

在加载 LoRA 权重之后执行操作。

在模型构建/加载完成后、应用任何适配器之前执行操作。

在模型加载完成后执行操作。

在训练完成后执行操作。

在训练完成且模型已卸载后执行操作。

在创建训练器之后执行操作。

在加载 LoRA 权重之前执行操作。

在模型加载之前执行操作。

以未解析字典的形式，使用给定的配置注册插件。

PluginManager 类负责加载和管理插件。它应作为单例存在，以便从代码库的任何位置访问。

主要方法包括：- get_instance()：用于获取 PluginManager 单例实例的静态方法。- register(plugin_name: str)：根据插件名称注册新插件。- pre_model_load(cfg)：调用所有已注册插件的 pre_model_load 方法。

调用所有已注册插件的 add_callbacks_post_trainer 方法。

调用所有已注册插件的 add_callbacks_pre_trainer 方法。

调用所有已注册插件的 create_lr_scheduler 方法，并返回第一个非空调度器。

调用所有已注册插件的 create_optimizer 方法，并返回第一个非空优化器。

调用所有已注册插件的 get_collator_cls_and_kwargs 方法，并返回第一个非空的收集器类。

参数：cfg (dict)：插件的配置。is_eval (bool)：是否为评估阶段。

返回值：object：收集器类，如果未找到则返回 None。

返回所有已注册插件输入参数的 Pydantic 类列表。

返回 PluginManager 的单例实例。如果该实例不存在，则创建一个新实例。

调用所有已注册插件的 get_trainer_cls 方法，并返回第一个非空的训练器类。

调用所有已注册插件的 get_training_args 方法，并返回合并后的训练参数。

参数：cfg (dict)：插件的配置。

返回值：object：训练参数

返回所有已注册插件训练参数混合类的数据类列表。

返回值：list[str]：数据类列表

调用每个已注册插件的 load_datasets 方法。

调用所有已注册插件的 post_lora_load 方法。

在模型构建/加载完成后、应用任何适配器之前，调用所有已注册插件的 post_model_build 方法。

在模型加载完成后（包括所有适配器）调用所有已注册插件的 post_model_load 方法。

调用所有已注册插件的 post_train 方法。

调用所有已注册插件的 post_train_unload 方法。

调用所有已注册插件的 post_trainer_create 方法。

调用所有已注册插件的 pre_lora_load 方法。

调用所有已注册插件的 pre_model_load 方法。

根据插件名称注册新插件。

根据给定的插件名称加载插件。插件名称应采用“module_name.class_name”的格式。该函数会将插件名称拆分为模块名和类名，导入对应模块，从模块中获取类，然后创建该类的实例。

**示例：**

示例 1（Python）：
```python
integrations.base.BaseOptimizerFactory()
```

示例 2（Python）：
```python
integrations.base.BaseOptimizerFactory.get_decay_parameter_names(model)
```

示例 3（Python）：
```python
integrations.base.BasePlugin()
```

示例 4（Python）：
```python
integrations.base.BasePlugin.add_callbacks_post_trainer(cfg, trainer)
```

## prompt_strategies.chat_template

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.chat_template.html

**内容：**
- prompt_strategies.chat_template
- 类
  - ChatTemplatePrompter
    - 方法
      - build_prompt
        - 参数
  - ChatTemplateStrategy
    - 方法
      - find_first_eot_token
      - find_turn

prompt_strategies.chat_template

HF聊天模板提示策略

用于处理HF聊天模板的提示生成器

根据对话内容构建提示。

针对基于指令的提示的分词策略。

从start_idx位置开始，在input_ids中查找第一个结束标记token。

确定对话中指定轮次的起始和结束索引。

可同时处理单个提示或批量提示的公共方法。

Mistral聊天模板提示生成器。

Mistral聊天模板策略。

从start_idx位置开始，在input_ids中查找第一个结束标记token。

根据配置加载聊天模板策略。

**示例：**

示例1（Python）：
```python
prompt_strategies.chat_template.ChatTemplatePrompter(
    tokenizer,
    chat_template,
    processor=None,
    max_length=2048,
    message_property_mappings=None,
    message_field_training=None,
    message_field_training_detail=None,
    field_messages='messages',
    field_system='system',
    field_tools='tools',
    field_thinking='reasoning_content',
    roles=None,
    template_thinking_key='reasoning_content',
    chat_template_kwargs=None,
    drop_system_message=False,
)
```

示例 2（Python）：
```python
prompt_strategies.chat_template.ChatTemplatePrompter.build_prompt(
    conversation,
    add_generation_prompt=False,
    images=None,
    tools=None,
)
```

示例 3（Python）：
```python
prompt_strategies.chat_template.ChatTemplateStrategy(
    prompter,
    tokenizer,
    train_on_inputs,
    sequence_len,
    roles_to_train=None,
    train_on_eos=None,
    train_on_eot=None,
    eot_tokens=None,
    split_thinking=False,
)
```

示例 4（Python）：
```python
prompt_strategies.chat_template.ChatTemplateStrategy.find_first_eot_token(
    input_ids,
    start_idx,
)
```

## kernels.quantize

**URL:** https://docs.axolotl.ai/docs/api/kernels.quantize.html

**目录:**
- kernels.quantize
- 函数
  - dequantize
    - 参数
    - 返回值
    - 异常
    - 备注

用于与 bitsandbytes 集成的反量化工具。

基于 bitsandbytes 的 CUDA 核心实现快速 NF4 反量化功能。

利用 bitsandbytes 优化的 CUDA 实现，高效地对 NF4 格式的权重进行反量化处理。同时支持旧版的列表格式以及新版的 QuantState 格式。

在较新的 bitsandbytes 版本（>0.43.3）中，可通过 CUDA 流提升性能。

**示例:**

示例 1（Python）：
```python
kernels.quantize.dequantize(W, quant_state=None, out=None)
```

## integrations.spectrum.args

**网址：** https://docs.axolotl.ai/docs/api/integrations.spectrum.args.html

**内容：**
- integrations.spectrum.args
- 类
  - SpectrumArgs

integrations.spectrum.args

用于处理 Spectrum 输入参数的模块。

Spectrum 的输入参数。

**示例：**

示例 1（Python）：
```python
integrations.spectrum.args.SpectrumArgs()
```

## prompt_strategies.alpaca_chat

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.alpaca_chat.html

**内容：**
- prompt_strategies.alpaca_chat
- 类
  - AlpacaChatPrompter
  - AlpacaConcisePrompter
  - AlpacaQAPromptTokenizingStrategy
  - CamelAIPromptTokenizingStrategy
  - NoSystemPrompter

prompt_strategies.alpaca_chat

用于 Alpaca 提示策略类的模块

Alpaca Chat Prompter：通过扩展系统提示词来生成对话式指令回复

Alpaca Prompter：通过扩展系统提示词来获取简洁的对话式指令回复

AlpacaQA 的分词策略

CamelAI 数据集的分词策略

不包含任何系统提示词的空提示器

**示例：**

示例 1（Python）：
```python
prompt_strategies.alpaca_chat.AlpacaChatPrompter()
```

示例 2（Python）：
```python
prompt_strategies.alpaca_chat.AlpacaConcisePrompter(
    prompt_style=PromptStyle.INSTRUCT.value,
)
```

示例 3（Python）：
```python
prompt_strategies.alpaca_chat.AlpacaQAPromptTokenizingStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

示例 4（Python）：
```python
prompt_strategies.alpaca_chat.CamelAIPromptTokenizingStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

## utils.collators.mamba

**网址：** https://docs.axolotl.ai/docs/api/utils.collators.mamba.html

**目录结构：**
- utils.collators.mamba
- 类
  - MambaDataCollator

utils.collators.mamba

用于状态空间模型（Mamba）的整理工具

**示例：**

示例 1（Python）：
```python
utils.collators.mamba.MambaDataCollator(tokenizer)
```

## prompt_strategies.messages.chat

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.messages.chat.html

**内容：**
- prompt_strategies.messages.chat
- 类
  - ChatMessageDatasetWrappingStrategy

prompt_strategies.messages.chat

用于新内部消息表示形式的聊天数据集封装策略

用于新内部消息表示形式的聊天数据集封装策略

**示例：**

示例 1（Python）：
```python
prompt_strategies.messages.chat.ChatMessageDatasetWrappingStrategy(
    processor,
    message_transform=None,
    formatter=None,
    **kwargs,
)
```

## 训练模型

**URL:** https://docs.axolotl.ai/docs/api/train.html

**内容:**
- train
- 函数
  - create_model_card
    - 参数
  - execute_training
    - 参数
  - handle_untrained_tokens_fix
    - 参数
  - save_initial_configs
    - 参数

在数据集上准备并训练模型。也可从现有模型进行推理或合并 LoRA 模块。

如需，可为训练完成的模型创建模型卡片。

使用合适的 SDP 内核配置执行训练过程。

如已配置，可对未训练的标记应用修复措施。

在训练前保存初始配置。

根据配置和训练设置保存训练好的模型。

根据配置加载分词器、处理器（用于多模态模型）以及模型本身。

加载模型、分词器、训练器等组件。该辅助函数用于整合完整的训练器设置。

如可用，可设置 Axolotl 标识，并将 Axolotl 配置添加到模型卡片中。

如需，可设置用于强化学习训练的参考模型。

设置信号处理程序以实现优雅终止。

在给定的数据集上训练模型。

**示例:**

示例 1（Python）：
```python
train.create_model_card(cfg, trainer)
```

示例 2（Python）：
```python
train.execute_training(cfg, trainer, resume_from_checkpoint)
```

示例 3（Python）：
```python
train.handle_untrained_tokens_fix(
    cfg,
    model,
    tokenizer,
    train_dataset,
    safe_serialization,
)
```

示例 4（Python）：
```python
train.save_initial_configs(cfg, tokenizer, model, peft_config, processor)
```

---

## cli.utils.load

**网址：** https://docs.axolotl.ai/docs/api/cli.utils.load.html

**目录：**
- cli.utils.load
- 函数
  - load_model_and_tokenizer
    - 参数
    - 返回值

用于加载模型、分词器等资源的工具函数。

该辅助函数可用于根据指定的 Axolotl 配置文件来加载模型、分词器及处理器。

**示例：**

示例 1（Python）：
```python
cli.utils.load.load_model_and_tokenizer(cfg, inference=False)
```

## loaders.model

**URL:** https://docs.axolotl.ai/docs/api/loaders.model.html

**内容：**
- loaders.model
- 类
  - ModelLoader
    - 加载流程包括
    - 属性
    - 方法
      - load
        - 返回值

用于加载、配置及应用各类模型的模型加载器类实现。

负责管理模型配置、初始化以及加载过程中的补丁应用。

该类统筹处理从配置读取到最终模型准备的全部加载流程，涵盖设备映射、量化处理、注意力机制、适配器集成以及多种优化技术。

可加载模型并应用所有配置与补丁以完成模型准备。

**示例：**

示例 1（Python）：
```python
loaders.model.ModelLoader(
    cfg,
    tokenizer,
    *,
    inference=False,
    reference_model=False,
    **kwargs,
)
```

示例 2（Python）：
```python
loaders.model.ModelLoader.load()
```

## utils.distributed

**网址：** https://docs.axolotl.ai/docs/api/utils.distributed.html

**目录：**
- utils.distributed
- 函数
  - barrier
  - cleanup_distributed
  - compute_and_broadcast
  - gather_from_all_ranks
  - gather_scalar_from_all_ranks
  - is_distributed
  - is_main_process
    - 返回值

用于实现分布式功能的工具函数。

充当屏障，使所有进程等待。这样可以确保所有进程都到达屏障后再继续执行后续操作。

如果已初始化 torch distributed，则销毁进程组。该函数会在训练提前终止或训练成功完成时被调用。

仅在指定的进程 rank（默认为 0）上使用函数 ‘fn’ 计算值，然后将该值广播到所有其他进程。

参数：
- fn（可调用对象）：用于计算值的函数。该函数不应产生任何副作用。
- rank（整数，可选）：用于计算值的进程 rank。默认值为 0。

返回值：
- 计算得到的值（整数或浮点数）。

在所有进程上运行可调用对象 ‘fn’，并在指定的进程 rank 上收集结果。

参数：
- fn（可调用对象）：用于计算值的函数。该函数不应产生任何副作用。
- rank（整数，可选）：用于收集值的进程 rank。默认值为 0。
- world_size（整数，可选）：当前分布式环境中的总进程数。

返回值：
- 如果在收集结果的进程上，则返回所有进程的计算结果列表；否则返回 None。

在所有进程上运行可调用对象 ‘fn’，并在指定的进程 rank 上收集结果。

参数：
- fn（可调用对象）：用于计算值的函数。该函数不应产生任何副作用。
- rank（整数，可选）：用于收集值的进程 rank。默认值为 0。
- world_size（整数，可选）：当前分布式环境中的总进程数。

返回值：
- 如果在收集结果的进程上，则返回所有进程的计算结果列表；否则返回 None。

检查是否已初始化分布式训练。

检查当前进程是否为主进程。如果未处于分布式模式，则始终返回 True。

当尚未初始化分布式状态时，我们会采用更简单的逻辑：仅在第 0 个本地进程 rank 上进行日志记录。

在所有进程上运行可调用对象 ‘fn1’，收集结果后使用 ‘fn2’ 对其进行聚合运算，最后将聚合后的结果广播到所有进程。

参数：
- fn1（可调用对象）：在每个进程上计算值的函数。
- fn2（可调用对象）：聚合函数，用于接收一组值并返回一个单一值。
- world_size（整数，可选）：当前分布式环境中的总进程数。

返回值：
- 经过聚合并广播后的值。

让包装后的上下文按顺序运行，确保第 0 个进程在其他进程之前执行。

**示例：**

示例 1（Python）：
```python
utils.distributed.barrier()
```

示例 2（Python）：
```python
utils.distributed.cleanup_distributed()
```

示例 3（Python）：
```python
utils.distributed.compute_and_broadcast(fn)
```

示例 4（Python）：
```python
utils.distributed.gather_from_all_ranks(fn, world_size=1)
```

## cli.config

**网址：** https://docs.axolotl.ai/docs/api/cli.config.html

**内容：**
- cli.config
- 函数
  - check_remote_config
    - 参数
    - 返回值
    - 异常
  - choose_config
    - 参数
    - 返回值
    - 异常

用于配置的加载与处理。

首先判断传入的配置是否为有效的 HTTPS 地址。随后尝试获取该地址并解析其内容，先以 JSON 格式解析，再尝试以 YAML 格式解析（优先选择 YAML 格式）。最后，将解析后的内容写入本地文件，并返回该文件的路径。

这是一个用于选择 axolotl 配置 YAML 文件的辅助方法（仅考虑以 .yml 或 .yaml 结尾的文件）。如果在指定路径下存在多个配置文件，系统会提示用户从中选择一个。

用于加载存储在指定路径下的 axolotl 配置，对其进行验证，并执行各种初始化设置。

会根据给定的配置注册相应的插件。

**示例：**

示例 1（Python）：
```python
cli.config.check_remote_config(config)
```

示例 2（Python）：
```python
cli.config.choose_config(path)
```

示例 3（Python）：
```python
cli.config.load_cfg(config=Path('examples/'), **kwargs)
```

示例 4（Python）：
```python
cli.config.prepare_plugins(cfg)
```

## cli.checks

**网址：** https://docs.axolotl.ai/docs/api/cli.checks.html

**内容：**
- cli.checks
- 函数
  - check_accelerate_default_config
  - check_user_token
    - 返回值
    - 异常情况

针对 Axolotl CLI 的各类检查功能。

若未找到 accelerate 配置文件，将输出警告级日志。

用于检查 HF 用户信息。当 HF_HUB_OFFLINE=1 时，此检查将被跳过。

**示例：**

示例 1（Python）：
```python
cli.checks.check_accelerate_default_config()
```

示例 2（Python）：
```python
cli.checks.check_user_token()
```

## prompt_strategies.llama2_chat

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.llama2_chat.html

**内容：**
- prompt_strategies.llama2_chat
- 类
  - LLama2ChatTokenizingStrategy
  - Llama2ChatConversation
    - 方法
      - append_message
      - get_prompt
  - Llama2ChatPrompter

prompt_strategies.llama2_chat

用于微调 Llama2 对话模型的提示策略。如需参考实现，可查看 https://github.com/facebookresearch/llama/blob/6c7fe276574e78057f917549435a2554000a876d/llama/generation.py#L213。

该实现基于 Vicuna PR 和 fastchat 仓库，更多信息请参阅：https://github.com/lm-sys/FastChat/blob/cdd7730686cb1bf9ae2b768ee171bdf7d1ff04f3/fastchat/conversation.py#L847。

若要在 config.yml 中使用此提示风格，请将数据集类型设置为“llama2_chat”。

例如，在 config.yml 中：

数据集本身应如下所示（存储在 jsonl 文件中）：第一条消息应由人类发送，第二条由 GPT 发送。对于自定义系统消息，第一个“from”字段可设为“system”，之后依次为“human”和“gpt”的轮次。

重要提示：如果您不确定自己在做什么，请勿在 config.yml 中使用“special_tokens:”！

用于对 Llama2 提示进行分词处理的策略，改编自 https://github.com/lm-sys/FastChat/blob/main/fastchat/train/train.py。

一个用于管理提示模板并保存所有对话历史的类，复制自 https://github.com/lm-sys/FastChat/blob/main/fastchat/conversation.py。

添加新消息。

获取用于生成的提示。

为 Llama2 模型生成提示的提示器。

**示例：**

示例 1（未知）：
```unknown
datasets:
  - path: llama_finetune_train.jsonl
    type: llama2_chat
```

示例 2（未知情况）：
```unknown
{'conversations':[{"from": "human", "value": "Who are you?"}, {"from": "gpt", "value": "I am Vicuna"},...]}
```

示例 3（Python）：
```python
prompt_strategies.llama2_chat.LLama2ChatTokenizingStrategy(*args, **kwargs)
```

示例 4（Python）：
```python
prompt_strategies.llama2_chat.Llama2ChatConversation(
    name='llama2',
    system="[INST] <<SYS>>\nYou are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\n<</SYS>>\n\n",
    roles=('[INST]', '[/INST]'),
    messages=list(),
    offset=0,
)
```

## cli.utils

**网址：** https://docs.axolotl.ai/docs/api/cli.utils.html

**内容：**
- cli.utils

用于初始化 axolotl.cli.utils 模块。

---

## cli.utils.args

**网址：** https://docs.axolotl.ai/docs/api/cli.utils.args.html

**内容：**
- cli.utils.args
- 函数
  - add_options_from_config
    - 参数
    - 返回值
  - add_options_from_dataclass
    - 参数
    - 返回值
  - filter_none_kwargs
    - 参数

用于处理 axolotl CLI 参数的实用工具。

从 Pydantic 模型的字段中生成 Click 选项。

从 dataclass 的字段中生成 Click 选项。

用于封装函数，以移除值为 None 的关键字参数。

**示例：**

示例 1（Python）：
```python
cli.utils.args.add_options_from_config(config_class)
```

示例 2（Python）：
```python
cli.utils.args.add_options_from_dataclass(config_class)
```

示例 3（Python）：
```python
cli.utils.args.filter_none_kwargs(func)
```

## integrations.grokfast.optimizer

**网址：** https://docs.axolotl.ai/docs/api/integrations.grokfast.optimizer.html

**内容：**
- integrations.grokfast.optimizer

integrations.grokfast.optimizer

---

## core.builders.causal

**网址：** https://docs.axolotl.ai/docs/api/core.builders.causal.html

**内容：**
- corebuilders.causal
- 类别
  - HFCausalTrainerBuilder

用于构建因果模型及基于TRL的奖励模型的HuggingFace训练参数/训练器。

**示例：**

示例 1（Python）：
```python
core.builders.causal.HFCausalTrainerBuilder(
    cfg,
    model,
    tokenizer,
    processor=None,
)
```

## prompt_strategies.dpo.user_defined

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.dpo.user_defined.html

**内容：**
- prompt_strategies.dpo.user_defined

prompt_strategies.dpo.user_defined

用户自定义的 DPO 策略

---

## cli.evaluate

**网址：** https://docs.axolotl.ai/docs/api/cli.evaluate.html

**内容：**
- cli.evaluate
- 函数
  - do_cli
    - 参数
  - do_evaluate
    - 参数

用于对模型进行评估的命令行工具。

该工具会解析 axolotl 配置文件及命令行参数，随后调用 do_evaluate 函数。其工作流程为：首先加载 axolotl 配置中指定的数据集，再调用 axolotl.evaluate.evaluate 函数，该函数会对指定数据集计算评估指标，并将结果保存到磁盘。

**示例：**

示例 1（Python）：
```python
cli.evaluate.do_cli(config=Path('examples/'), **kwargs)
```

示例 2（Python）：
```python
cli.evaluate.do_evaluate(cfg, cli_args)
```

## utils.schemas.utils

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.utils.html

**内容：**
- utils.schemas.utils
- 函数
  - handle_legacy_message_fields_logic
    - 参数
    - 返回值
    - 异常

用于 Axolotl Pydantic 模型的工具函数

用于处理旧版消息字段映射方式与新版属性映射系统之间的兼容性问题。

此前，配置仅支持通过专用选项来映射“role”和“content”字段：  
- message_field_role：映射到 role 字段  
- message_field_content：映射到 content 字段  

而新系统则通过 message_property_mappings 来实现任意字段的映射：  
message_property_mappings:  
  role: source_role_field  
  content: source_content_field  
  additional_field: source_field  

**示例：**

示例 1（Python）：
```python
utils.schemas.utils.handle_legacy_message_fields_logic(data)
```

## prompt_strategies.alpaca_instruct

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.alpaca_instruct.html

**内容：**
- prompt_strategies.alpaca_instruct

prompt_strategies.alpaca_instruct

用于加载 AlpacaInstructPromptTokenizingStrategy 类的模块

---

## utils.callbacks.lisa

**URL:** https://docs.axolotl.ai/docs/api/utils.callbacks.lisa.html

**内容：**
- utils.callbacks.lisa

该功能基于 https://github.com/OptimalScale/LMFlow/pull/701 进行优化，适用于 HF transformers 以及 Axolotl 框架。相关论文地址：Arxiv: https://arxiv.org/abs/2403.17919，许可证类型为 Apache 2.0

---

## models.mamba.modeling_mamba

**URL:** https://docs.axolotl.ai/docs/api/models.mamba.modeling_mamba.html

**内容：**
- models.mamba.modeling_mamba

models.mamba.modeling_mamba

---

## prompt_strategies.metharme

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.metharme.html

**内容：**
- prompt_strategies.metharme
- 类
  - MetharmePromptTokenizingStrategy
  - MetharmePrompter

prompt_strategies.metharme

包含 MetharmenPromptTokenizingStrategy 和 MetharmePrompter 类的模块

用于 Metharme 模型的分词策略

用于 Metharme 模型的提示词生成器。

**示例：**

示例 1（Python）：
```python
prompt_strategies.metharme.MetharmePromptTokenizingStrategy(
    prompter,
    tokenizer,
    train_on_inputs=False,
    sequence_len=2048,
)
```

示例 2（Python）：
```python
prompt_strategies.metharme.MetharmePrompter(*args, **kwargs)
```

## core.trainers.mamba

**URL:** https://docs.axolotl.ai/docs/api/core.trainers.mamba.html

**目录:**
- core.trainers.mamba
- 类
  - AxolotlMambaTrainer

用于 Mamba 训练器的模块

专为 Mamba 设计的训练器，用于处理损失计算

**示例:**

示例 1（Python）：
```python
core.trainers.mamba.AxolotlMambaTrainer(
    *_args,
    bench_data_collator=None,
    eval_data_collator=None,
    dataset_tags=None,
    **kwargs,
)
```

## utils.ctx_managers.sequence_parallel

**URL:** https://docs.axolotl.ai/docs/api/utils.ctx_managers.sequence_parallel.html

**目录:**
- utils.ctx_managers.sequence_parallel
- 类
  - AllGatherWithGrad
    - 方法
      - backward
        - 参数
        - 返回值
      - forward
        - 参数
        - 返回值

utils.ctx_managers.sequence_parallel

用于 Axolotl 训练器中的序列并行管理及相关工具的模块。

专为全收集操作设计的自定义自动求导函数，用于保留梯度信息。

处理全收集操作的反向传播过程。

从完整的梯度张量中提取与当前节点原始输入相对应的梯度片段。

针对具有序列维度的数据实现全收集操作的正向传播。

用于序列并行操作的上下文管理器。

该类通过预正向钩子在模型正向传播时自动应用序列并行机制，并通过后正向钩子汇总来自序列并行组各节点的输出。

对批量数据应用序列并行切片功能。

对于整数类型的 logits_to_keep 参数有特殊处理逻辑，该参数用于指定在生成过程中仅保留序列中的最后 N 个标记。

**示例:**

示例 1（Python）：
```python
utils.ctx_managers.sequence_parallel.AllGatherWithGrad()
```

示例 2（Python）：
```python
utils.ctx_managers.sequence_parallel.AllGatherWithGrad.backward(
    ctx,
    grad_output,
)
```

示例 3（Python）：
```python
utils.ctx_managers.sequence_parallel.AllGatherWithGrad.forward(
    ctx,
    input_tensor,
    group,
)
```

示例 4（Python）：
```python
utils.ctx_managers.sequence_parallel.SequenceParallelContextManager(
    models,
    context_parallel_size,
    gradient_accumulation_steps,
    ring_attn_func,
    heads_k_stride,
    gather_outputs,
    device_mesh=None,
)
```

## utils.callbacks.qat

**URL:** https://docs.axolotl.ai/docs/api/utils.callbacks.qat.html

**目录结构：**
- utils.callbacks.qat
- 类
  - QATCallback
- 函数
  - toggle_fake_quant
    - 参数

HF Causal Trainer 的 QAT 回调功能

用于切换模型中的虚拟量化状态。

可切换模型中所有经过虚拟量化的线性层或嵌入层的量化状态。

**示例：**

示例 1（Python）：
```python
utils.callbacks.qat.QATCallback(cfg)
```

示例 2（Python）：
```python
utils.callbacks.qat.toggle_fake_quant(mod, enable)
```

## prompt_strategies.dpo.zephyr

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.dpo.zephyr.html

**内容：**
- prompt_strategies.dpo.zephyr

prompt_strategies.dpo.zephyr

适用于 Zephyr 的 DPO 策略

---

## kernels.utils

**网址：** https://docs.axolotl.ai/docs/api/kernels.utils.html

**内容：**
- kernels.utils

用于 axolotl.kernels 子模块的实用工具

---

## monkeypatch.multipack

**网址：** https://docs.axolotl.ai/docs/api/monkeypatch.multipack.html

**内容：**
- monkeypatch.multipack

monkeypatch.multipack

针对样本打包 v2 版本的 multipack 补丁功能

---

## cli.main

**网址：** https://docs.axolotl.ai/docs/api/cli.main.html

**内容：**
- cli.main
- 函数
  - cli
  - evaluate
    - 参数
  - fetch
    - 参数
  - inference
    - 参数
  - merge_lora

点击即可查看各类 axolotl 命令的 CLI 定义。

Axolotl CLI —— 大语言模型的训练与微调

用于获取示例配置或其他资源。

可用目录：- examples：示例配置文件 - deepspeed_configs：DeepSpeed 配置文件

使用已训练的模型进行推理。

将训练好的 LoRA 适配器合并到基础模型中。

合并分片后的 FSDP 模型权重。

在训练前对数据集进行预处理。

对模型进行训练或微调。

**示例：**

示例 1（Python）：
```python
cli.main.cli()
```

示例 2（Python）：
```python
cli.main.evaluate(ctx, config, launcher, **kwargs)
```

示例 3（Python）：
```python
cli.main.fetch(directory, dest)
```

示例 4（Python）：
```python
cli.main.inference(ctx, config, launcher, gradio, **kwargs)
```

## core.trainers.mixins.optimizer

**网址：** https://docs.axolotl.ai/docs/api/core.trainers.mixins.optimizer.html

**内容概要：**
- core.trainers.mixins.optimizer
- 类
  - OptimizerInitMixin
  - OptimizerMixin

core.trainers.mixins.optimizer

用于 Axolotl 训练器优化器混入模块的组件

该混入类用于处理那些在构造函数中不接受 `optimizer_cls_and_kwargs` 作为参数的训练器（主要是 TRL 框架中的训练器）所共有的优化器初始化逻辑。

用于统一处理自定义优化器构建的混入类

**示例：**

示例 1（Python）：
```python
core.trainers.mixins.optimizer.OptimizerInitMixin(*args, **kwargs)
```

示例 2（Python）：
```python
core.trainers.mixins.optimizer.OptimizerMixin()
```

## integrations.kd.trainer

**URL:** https://docs.axolotl.ai/docs/api/integrations.kd.trainer.html

**内容：**
- integrations.kd.trainer
- 类
  - AxolotlKDTrainer
    - 方法
      - compute_loss

integrations.kd.trainer

用于知识蒸馏（KD）的定制训练器子类

该训练器用于计算损失值。默认情况下，所有模型都会在第一个元素中返回损失值。

可通过子类化并重写相关方法来实现自定义功能。

**示例：**

示例 1（Python）：
```python
integrations.kd.trainer.AxolotlKDTrainer(*args, **kwargs)
```

示例 2（Python）：
```python
integrations.kd.trainer.AxolotlKDTrainer.compute_loss(
    model,
    inputs,
    return_outputs=False,
    num_items_in_batch=None,
)
```

## integrations.lm_eval.args

**网址：** https://docs.axolotl.ai/docs/api/integrations.lm_eval.args.html

**内容概要：**
- integrations.lm_eval.args
- 类
  - LMEvalArgs

integrations.lm_eval.args

用于处理 LM 评估工具包输入参数的模块。

LM 评估工具包的输入参数

**示例：**

示例 1（Python）：
```python
integrations.lm_eval.args.LMEvalArgs()
```

## integrations.cut_cross_entropy.args

**网址：** https://docs.axolotl.ai/docs/api/integrations.cut_cross_entropy.args.html

**内容：**
- integrations.cut_cross_entropy.args
- 类
  - CutCrossEntropyArgs

integrations.cut_cross_entropy.args

用于处理割裂交叉熵输入参数的模块。

割裂交叉熵的输入参数。

**示例：**

示例 1（Python）：
```python
integrations.cut_cross_entropy.args.CutCrossEntropyArgs()
```

---

## monkeypatch.mistral_attn_hijack_flash

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.mistral_attn_hijack_flash.html

**内容：**
- monkeypatch.mistral_attn_hijack_flash

用于 Mistral 模型的 Flash Attention 动态补丁功能

---

## loaders.constants

**URL:** https://docs.axolotl.ai/docs/api/loaders.constants.html

**内容：**
- loaders.constants

axolotl.loaders 模块所使用的共享常量

---

## utils.bench

**URL:** https://docs.axolotl.ai/docs/api/utils.bench.html

**内容：**
- utils.bench
- 函数
  - check_cuda_device

用于性能测试与测量的实用工具

若未检测到 CUDA 设备或设备处于自动选择状态，该工具会包裹对应函数并直接返回默认值，而不会实际执行该函数。  
:param default_value: :return:

**示例：**

示例 1（Python）：
```python
utils.bench.check_cuda_device(default_value)
```

## utils.trainer

**URL:** https://docs.axolotl.ai/docs/api/utils.trainer.html

**内容：**
- utils.trainer
- 函数
  - add_pose_position_ids
  - add_position_ids
  - drop_long_seq
  - setup_trainer
    - 参数
    - 返回值

该模块包含Trainer类及相关函数，可通过PoSE技术通过随机跳过上下文中的部分位置来扩展上下文长度。我们仅需要跳过split_on_token_ids列表中标记的位置之前的内容。虽然应尝试随机分布跳过位置，但并不要求最终的position_ids恰好等于完整的context_len。由于上下文中可能包含多个对话轮次，因此需确保考虑每个样本中最多可进行的跳过次数。

该模块同时支持单个样本和批量数据处理：- 单个样本时，sample[‘input_ids’]为list[int]类型；- 批量数据时，sample[‘input_ids’]为list[list[int]]类型。

用于过滤掉序列长度过长（> sequence_len）或过短（< min_sequence_len）的样本，同时支持单个样本（list[int]）和批量数据（list[list[int]]）的处理。

这是一个用于实例化并构建（因果型或RLHF型）训练器的辅助方法。

**示例：**

示例1（Python）：
```python
utils.trainer.add_pose_position_ids(
    sample,
    max_context_len=32768,
    split_on_token_ids=None,
    chunks=2,
)
```

示例 2（Python）：
```python
utils.trainer.add_position_ids(sample)
```

示例 3（Python）：
```python
utils.trainer.drop_long_seq(sample, sequence_len=2048, min_sequence_len=2)
```

示例 4（Python）：
```python
utils.trainer.setup_trainer(
    cfg,
    train_dataset,
    eval_dataset,
    model,
    tokenizer,
    processor,
    total_num_steps,
    model_ref=None,
    peft_config=None,
)
```

## utils.schemas.config

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.config.html

**内容概览：**
- utils.schemas.config
- 类
  - AxolotlConfigWCapabilities
  - AxolotlInputConfig

用于配置的 Pydantic 模型模块。

用于根据配置选项验证 GPU 功能的封装类。

所有配置选项的统一封装类。

**示例：**

示例 1（Python）：
```python
utils.schemas.config.AxolotlConfigWCapabilities()
```

示例 2（Python）：
```python
utils.schemas.config.AxolotlInputConfig()
```

## cli.args

**网址：** https://docs.axolotl.ai/docs/api/cli.args.html

**目录结构：**
- cli.args
- 类
  - EvaluateCliArgs
  - InferenceCliArgs
  - PreprocessCliArgs
  - QuantizeCliArgs
  - TrainerCliArgs
  - VllmServeCliArgs

用于处理 axolotl CLI 命令参数的模块。

包含 axolotl evaluate 命令所需 CLI 参数的数据类。

包含 axolotl inference 命令所需 CLI 参数的数据类。

包含 axolotl preprocess 命令所需 CLI 参数的数据类。

包含 axolotl quantize 命令所需 CLI 参数的数据类。

包含 axolotl train 命令所需 CLI 参数的数据类。

包含 axolotl vllm-serve 命令所需 CLI 参数的数据类。

**示例：**

示例 1（Python）：
```python
cli.args.EvaluateCliArgs(
    debug=False,
    debug_text_only=False,
    debug_num_examples=0,
)
```

示例 2（Python）：
```python
cli.args.InferenceCliArgs(prompter=None)
```

示例 3（Python）：
```python
cli.args.PreprocessCliArgs(
    debug=False,
    debug_text_only=False,
    debug_num_examples=1,
    prompter=None,
    download=True,
    iterable=False,
)
```

示例 4（Python）：
```python
cli.args.QuantizeCliArgs(
    base_model=None,
    weight_dtype=None,
    activation_dtype=None,
    quantize_embedding=None,
    group_size=None,
    output_dir=None,
    hub_model_id=None,
)
```

## 常见架构

**URL:** https://docs.axolotl.ai/docs/api/common.architectures.html

**内容:**
- common.architectures

常见架构相关的常量

---

## cli.merge_sharded_fsdp_weights

**URL:** https://docs.axolotl.ai/docs/api/cli.merge_sharded_fsdp_weights.html

**内容:**
- cli.merge_sharded_fsdp_weights
- 类
  - BFloat16CastPlanner
- 函数
  - do_cli
    - 参数
  - merge_fsdp_weights
    - 参数
    - 异常处理

cli.merge_sharded_fsdp_weights

用于将分片后的 FSDP 模型检查点合并为单个整合检查点的 CLI 工具。

该工具包含一个自定义规划器，可在加载过程中动态将张量转换为 bfloat16 格式。它还会解析 axolotl 配置文件及 CLI 参数，随后调用 merge_fsdp_weights 函数来执行合并操作。此功能适用于使用了 SHARDED_STATE_DICT 保存模型的情况，会将分片后的权重合并为单个检查点。若采用安全序列化方式，权重将保存至 {output_path}/model.safetensors 文件中；否则则保存为 pytorch_model.bin 文件。

注意：该操作属于 CPU 密集型任务。

**示例:**

示例 1（Python）：
```python
cli.merge_sharded_fsdp_weights.BFloat16CastPlanner()
```

示例 2（Python）：
```python
cli.merge_sharded_fsdp_weights.do_cli(config=Path('examples/'), **kwargs)
```

示例 3（Python）：
```python
cli.merge_sharded_fsdp_weights.merge_fsdp_weights(
    checkpoint_dir,
    output_path,
    safe_serialization=False,
    remove_checkpoint_dir=False,
)
```

---

## utils.data.streaming

**网址：** https://docs.axolotl.ai/docs/api/utils.data.streaming.html

**内容：**
- utils.data.streaming

针对流式数据集的特殊数据处理功能。

---

## core.chat.format.chatml

**网址：** https://docs.axolotl.ai/docs/api/core.chat.format.chatml.html

**内容：**
- core.chat.format.chatml

core.chat.format.chatml

用于处理 MessageContents 的 ChatML 转换函数。

---

## prompt_strategies.kto.chatml

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.kto.chatml.html

**内容：**
- prompt_strategies.kto.chatml
- 函数
  - argilla_chat
  - intel
  - ultra

prompt_strategies.kto.chatml

用于 ChatML 的 KTO 策略

适用于 argilla/kto-mix-15k 类型的对话场景

适用于 Intel Orca KTO，例如：argilla/distilabel-intel-orca-kto

适用于 ultrafeedback 二值化对话场景，例如：argilla/ultrafeedback-binarized-preferences-cleaned-kto

**示例：**

示例 1（Python）：
```python
prompt_strategies.kto.chatml.argilla_chat(cfg, **kwargs)
```

示例 2（Python）：
```python
prompt_strategies.kto.chatml.intel(cfg, **kwargs)
```

示例 3（Python）：
```python
prompt_strategies.kto.chatml.ultra(cfg, **kwargs)
```

## utils.schemas.trl

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.trl.html

**内容：**
- utils.schemas.trl
- 类
  - TRLConfig

用于配置 TRL 训练器的 Pydantic 模型

**示例：**

示例 1（Python）：
```python
utils.schemas.trl.TRLConfig()
```

---

## monkeypatch.llama_attn_hijack_xformers

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.llama_attn_hijack_xformers.html

**内容:**
- monkeypatch.llama_attn_hijack_xformers

monkeypatch.llama_attn_hijack_xformers

该模块直接复制了来自 https://raw.githubusercontent.com/oobabooga/text-generation-webui/main/modules/llama_attn_hijack.py 的代码，并对其进行了部分调整。

---

## kernels.geglu

**URL:** https://docs.axolotl.ai/docs/api/kernels.geglu.html

**内容:**
- kernels.geglu
- 函数
  - geglu_backward
    - 参数
    - 返回值
    - 备注
  - geglu_forward
    - 参数
    - 返回值

用于定义 GEGLU Triton 核心的模块。

相关参考文献：《GLU 变体提升 Transformer 性能》（https://arxiv.org/abs/2002.05202）。

此实现的灵感来源于 unsloth（https://unsloth.ai/），特此致谢。

该实现通过原地操作来完成 GEGLU 的反向传播过程。

该函数会直接在输入张量上修改数据以存储计算结果。

**示例:**

示例 1（Python）：
```python
kernels.geglu.geglu_backward(grad_output, gate, up)
```

示例 2（Python）：
```python
kernels.geglu.geglu_forward(gate, up)
```

## utils.callbacks.profiler

**网址：** https://docs.axolotl.ai/docs/api/utils.callbacks.profiler.html

**目录：**
- utils.callbacks.profiler
- 类
  - PytorchProfilerCallback

utils.callbacks.profiler

用于生成 PyTorch 性能分析快照的 HF Trainer 回调函数

该 PyTorch Profiler 回调函数可在指定步骤处生成 GPU 内存使用情况的快照。

**示例：**

示例 1（Python）：
```python
utils.callbacks.profiler.PytorchProfilerCallback(
    steps_to_profile=5,
    profiler_steps_start=0,
)
```

## kernels.lora

**URL:** https://docs.axolotl.ai/docs/api/kernels.lora.html

**目录：**
- kernels.lora
- 类
  - LoRA_MLP
    - 方法
      - backward
        - 参数
        - 返回值
      - forward
        - 参数
        - 返回值

用于定义低秩自适应（LoRA）Triton内核的模块。

相关理论可参考“LoRA：大型语言模型的低秩自适应”（https://arxiv.org/abs/2106.09685）。

此实现的灵感来源于 unsloth（https://unsloth.ai/），特此致谢。

经过优化的 LoRA MLP 实现，用于执行 LoRA MLP 的反向传播计算。

用于执行 LoRA MLP 的正向传播计算。

针对输出投影优化过的 LoRA 实现，用于计算 LoRA 输出投影的梯度。

结合 LoRA 执行输出投影的正向传播计算。

具备量化功能的优化型 LoRA QKV 实现，可高效计算带有量化及内存优化支持的查询、键、值投影。

用于计算 LoRA QKV 的梯度。

结合 LoRA 计算查询、键、值的投影。

将 LoRA 应用于具有 GEGLU 激活函数的 MLP 层。

将 LoRA 应用于具有 SwiGLU 激活函数的 MLP 层。

将 LoRA 应用于输出投影层。

应用 LoRA 来计算查询、键、值的投影。

从投影模块中获取 LoRA 参数。

高效的融合矩阵乘法与 LoRA 计算方式。

**示例：**

示例 1（Python）：
```python
kernels.lora.LoRA_MLP()
```

示例 2（Python）：
```python
kernels.lora.LoRA_MLP.backward(ctx, grad_output)
```

示例 3（Python）：
```python
kernels.lora.LoRA_MLP.forward(
    ctx,
    X,
    gate_weight,
    gate_bias,
    gate_quant,
    gate_A,
    gate_B,
    gate_scale,
    up_weight,
    up_bias,
    up_quant,
    up_A,
    up_B,
    up_scale,
    down_weight,
    down_bias,
    down_quant,
    down_A,
    down_B,
    down_scale,
    activation_fn,
    activation_fn_backward,
    inplace=True,
)
```

示例 4（Python）：
```python
kernels.lora.LoRA_O()
```

## monkeypatch.trainer_fsdp_optim

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.trainer_fsdp_optim.html

**内容：**
- monkeypatch.trainer_fsdp_optim
- 函数
  - patch_training_loop_for_fsdp

monkeypatch.trainer_fsdp_optim

针对 4.47.0 版本中训练器中 FSDP 优化器保存问题进行的修复

用于修复包含优化器保存功能的 FSDP 训练循环的补丁

**示例：**

示例 1（Python）：
```python
monkeypatch.trainer_fsdp_optim.patch_training_loop_for_fsdp()
```

## utils.schemas.multimodal

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.multimodal.html

**目录：**
- utils.schemas.multimodal
- 类
  - MultiModalConfig
    - 方法
      - convert_image_resize_algorithm

utils.schemas.multimodal

用于多模态相关配置的 Pydantic 模型

多模态配置子集

将图像缩放算法转换为 PIL.Image.Resampling 枚举类型。

**示例：**

示例 1（Python）：
```python
utils.schemas.multimodal.MultiModalConfig()
```

示例 2（Python）：
```python
utils.schemas.multimodal.MultiModalConfig.convert_image_resize_algorithm(
    image_resize_algorithm,
)
```

## prompt_strategies.dpo.llama3

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.dpo.llama3.html

**内容：**
- prompt_strategies.dpo.llama3
- 函数
  - argilla_chat
  - icr
  - intel
  - ultra

prompt_strategies.dpo.llama3

适用于 llama-3 聊天模板的 DPO 策略

用于 argilla/dpo-mix-7k 对话场景

针对包含系统信息、输入内容、选定选项及拒绝选项的数据集的 ChatML 转换，例如：https://huggingface.co/datasets/argilla/distilabel-intel-orca-dpo-pairs

适用于 Intel Orca DPO Pairs 场景

用于 ultrafeedback 二值化对话场景

**示例：**

示例 1（Python）：
```python
prompt_strategies.dpo.llama3.argilla_chat(cfg, **kwargs)
```

示例 2（Python）：
```python
prompt_strategies.dpo.llama3.icr(cfg, **kwargs)
```

示例 3（Python）：
```python
prompt_strategies.dpo.llama3.intel(cfg, **kwargs)
```

示例 4（Python）：
```python
prompt_strategies.dpo.llama3.ultra(cfg, **kwargs)
```

## core.chat.format.shared

**网址：** https://docs.axolotl.ai/docs/api/core.chat.format.shared.html

**内容：**
- core.chat.format.shared

core.chat.format.shared

用于格式转换的共享函数

---

## monkeypatch.llama_expand_mask

**网址：** https://docs.axolotl.ai/docs/api/monkeypatch.llama_expand_mask.html

**内容：**
- monkeypatch.llama_expand_mask

monkeypatch.llama_expand_mask

根据 https://arxiv.org/pdf/2107.02027.pdf 中的 3.2.2 要求扩展二进制注意力掩码

---

## core.chat.messages

**网址：** https://docs.axolotl.ai/docs/api/core.chat.messages.html

**内容：**
- core.chat.messages
- 类
  - ChatFormattedChats
  - Chats
  - MessageContentTypes
  - MessageContents
  - MessageRoles
  - Messages
  - PreferenceChats
  - SpecialToken

聊天消息的内部表示形式

使用格式化器处理聊天内容，可选择基于输入进行训练

聊天对话的顶层数据结构

文本、图片、音频、工具调用及工具响应等消息的内容类型

包含类型、值、元数据、权重、换行符以及内容结束标记的消息内容

系统、用户、助手和工具对应的消息角色

包含角色、内容、元数据、权重以及聊天格式化的消息

用于存储聊天偏好设置的数据结构

表示字符串开头和结尾的特殊标记

包含描述、功能及参数的工具

包含名称、参数以及可选标识符的工具调用内容

包含名称和参数的工具调用功能

包含名称、内容以及可选标识符的工具响应内容

**示例：**

示例 1（Python）：
```python
core.chat.messages.ChatFormattedChats()
```

示例 2（Python）：
```python
core.chat.messages.Chats()
```

示例 3（Python）：
```python
core.chat.messages.MessageContentTypes()
```

示例 4（Python）：
```python
core.chat.messages.MessageContents()
```

## core.datasets.transforms.chat_builder

**网址：** https://docs.axolotl.ai/docs/api/core.datasets.transforms.chat_builder.html

**目录：**
- core.datasets.transforms.chat_builder
- 函数
  - chat_message_transform_builder
    - 参数
    - 返回值

core.datasets.transforms.chat_builder

该模块包含一个用于构建转换函数的工具，该函数可获取数据集中的某一行数据，并将其转换为 Chat 对象。

用于构建能够获取数据集中的某一行数据并将其转换为 Chat 对象的转换函数

**示例：**

示例 1（Python）：
```python
core.datasets.transforms.chat_builder.chat_message_transform_builder(
    train_on_inputs=False,
    conversations_field='messages',
    message_field_role=None,
    message_field_content=None,
    message_field_training=None,
)
```

---

## utils.chat_templates

**URL:** https://docs.axolotl.ai/docs/api/utils.chat_templates.html

**内容：**
- utils.chat_templates

该模块提供了根据用户选择来挑选聊天模板的功能。这些模板用于格式化对话中的消息。

---

## core.trainers.dpo.trainer

**URL:** https://docs.axolotl.ai/docs/api/core.trainers.dpo.trainer.html

**内容：**
- core.trainers.dpo.trainer
- 类
  - AxolotlDPOTrainer
    - 方法
      - push_to_hub

core.trainers.dpo.trainer

用于 axolotl 的 DPO 训练器

该类是对 axolotl 专用辅助类的基础 DPOTrainer 的扩展。如需在将模型上传至 Hub 时强制添加标签，可覆盖 push_to_hub 方法。更多详细信息请参考 ~transformers.Trainer.push_to_hub。

**示例：**

示例 1（Python）：
```python
core.trainers.dpo.trainer.AxolotlDPOTrainer(*args, dataset_tags=None, **kwargs)
```

示例 2（Python）：
```python
core.trainers.dpo.trainer.AxolotlDPOTrainer.push_to_hub(*args, **kwargs)
```

## monkeypatch.gradient_checkpointing.offload_disk

**网址：** https://docs.axolotl.ai/docs/api/monkeypatch.gradient_checkpointing.offload_disk.html

**目录结构：**
- monkeypatch.gradient_checkpointing.offload_disk
- 类
  - Disco
    - 方法
      - backward
      - forward
      - get_instance
  - DiskOffloadManager
    - 方法
      - cleanup

monkeypatch.gradient_checkpointing.offload_disk

DISCO —— 基于磁盘的存储与检查点机制，并具备优化后的预取功能

Disco：基于磁盘的存储与检查点系统，带有优化的预取功能。这是一种高级的基于磁盘的梯度检查点工具，支持预取操作。

- 在反向传播过程中，通过预取功能从磁盘加载激活值
- 在正向传播过程中，将激活值异步卸载到磁盘
- 获取或创建卸载管理器
  - 该管理器负责处理已卸载的张量，并在单独的线程中执行预取操作
  - 同时通过同步机制避免竞态条件发生
- 清理所有临时文件，并在适当同步的前提下停止预取线程
- 在特定张量文件被使用完毕后进行清理
- 在适当同步的前提下，从磁盘或预取缓存中加载张量
- 以线程安全的方式异步将张量保存到磁盘，并返回文件路径
- 在适当同步的前提下，触发对接下来N个张量的预取操作
- 等待某个张量被成功保存到磁盘

**示例：**

示例1（Python）：
```python
monkeypatch.gradient_checkpointing.offload_disk.Disco()
```

示例 2（Python）：
```python
monkeypatch.gradient_checkpointing.offload_disk.Disco.backward(
    ctx,
    *grad_outputs,
)
```

示例 3（Python）：
```python
monkeypatch.gradient_checkpointing.offload_disk.Disco.forward(
    ctx,
    forward_function,
    hidden_states,
    *args,
    prefetch_size=1,
    prefetch_to_gpu=True,
    save_workers=4,
)
```

示例 4（Python）：
```python
monkeypatch.gradient_checkpointing.offload_disk.Disco.get_instance(
    prefetch_size=1,
    prefetch_to_gpu=True,
    save_workers=4,
)
```

## utils.samplers.multipack

**URL:** https://docs.axolotl.ai/docs/api/utils.samplers.multipack.html

**目录:**
- utils.samplers.multipack
- 类
  - MultipackBatchSampler
    - 方法
      - efficiency
      - gather_efficiency
        - 返回值
      - gather_len_batches
      - generate_batches
        - 参数

utils.samplers.multipack

Multipack Batch Sampler——一种高效的批量采样器，用于将不同长度的序列打包到固定容量的批次中，从而优化内存使用和训练效率。

用于高效打包不同长度序列的批量采样器类

该采样器通过将序列打包到固定容量的容器（批次）中，并减少填充数据，从而最大化GPU内存利用率和训练效率。

它同时支持并行打包（采用FFD算法）和顺序打包（保持原始序列顺序）两种方式。

计算打包效率（实际使用的标记数与总标记槽位数的比率）。数值越高越好——1.0表示完美打包，无任何空间浪费。

收集并同步所有分布式节点的打包效率估算值。

收集并同步所有分布式节点的批次数量，返回任意节点上可用的最小批次数。

生成用于训练的已打包批次。

设置训练轮次编号，以便在各轮次之间实现可重复的随机排序。

保持样本顺序的顺序分配器。

首次适应递减装箱算法检测。

检测指定长度的序列是否能够装入指定数量的容器中。

使用首次适应递减算法将一组序列打包到容器中。

通过并行处理将序列打包到容器中。

返回值：容器列表，每个容器包含分配给它的序列索引。

**示例:**

示例1（Python）：
```python
utils.samplers.multipack.MultipackBatchSampler(
    sampler,
    batch_size,
    batch_max_len,
    lengths,
    packing_efficiency_estimate=1.0,
    drop_last=True,
    num_count_samples=4,
    sequential=False,
    group_size=100000,
    bin_size=200,
    num_processes=None,
    safe_mode=True,
    mp_start_method='fork',
    **kwargs,
)
```

示例 2（Python）：
```python
utils.samplers.multipack.MultipackBatchSampler.efficiency()
```

示例 3（Python）：
```python
utils.samplers.multipack.MultipackBatchSampler.gather_efficiency()
```

示例 4（Python）：
```python
utils.samplers.multipack.MultipackBatchSampler.gather_len_batches(num)
```

## core.trainers.mixins.scheduler

**URL:** https://docs.axolotl.ai/docs/api/core.trainers.mixins.scheduler.html

**内容：**
- core.trainers.mixins.scheduler
- 类
  - SchedulerMixin
    - 方法
      - create_scheduler
        - 参数

core.trainers.mixins.scheduler

用于 Axolotl 训练器调度器混入模块的组件

在 CausalTrainer 中用于配置调度器的混入类。

用于设置调度器。在此方法被调用之前，必须已配置好训练器的优化器，或者将其作为参数传入。

**示例：**

示例 1（Python）：
```python
core.trainers.mixins.scheduler.SchedulerMixin()
```

示例 2（Python）：
```python
core.trainers.mixins.scheduler.SchedulerMixin.create_scheduler(
    num_training_steps,
    optimizer=None,
)
```

## utils.collators.batching

**URL:** https://docs.axolotl.ai/docs/api/utils.collators.batching.html

**目录:**
- utils.collators.batching
- 类
  - BatchSamplerDataCollatorForSeq2Seq
  - DataCollatorForSeq2Seq
    - 参数
  - PretrainingBatchSamplerDataCollatorForSeq2Seq
  - V2BatchSamplerDataCollatorForSeq2Seq

utils.collators.batching

用于为打包后的序列填充标签和位置标识的数据整理工具

专为配合 BatchSampler 使用的多包处理专用数据整理工具

能够动态填充接收到的输入数据以及对应的标签和位置标识的数据整理工具

专为配合 BatchSampler 使用的多包处理专用数据整理工具

专为配合 BatchSampler 使用的多包处理专用数据整理工具

**示例:**

示例 1（Python）：
```python
utils.collators.batching.BatchSamplerDataCollatorForSeq2Seq(
    tokenizer,
    model=None,
    padding=True,
    max_length=None,
    pad_to_multiple_of=None,
    label_pad_token_id=-100,
    position_pad_token_id=0,
    return_tensors='pt',
)
```

示例 2（Python）：
```python
utils.collators.batching.DataCollatorForSeq2Seq(
    tokenizer,
    model=None,
    padding=True,
    max_length=None,
    pad_to_multiple_of=None,
    label_pad_token_id=-100,
    position_pad_token_id=0,
    return_tensors='pt',
)
```

示例 3（Python）：
```python
utils.collators.batching.PretrainingBatchSamplerDataCollatorForSeq2Seq(
    *args,
    multipack_attn=True,
    **kwargs,
)
```

示例 4（Python）：
```python
utils.collators.batching.V2BatchSamplerDataCollatorForSeq2Seq(
    tokenizer,
    model=None,
    padding=True,
    max_length=None,
    pad_to_multiple_of=None,
    label_pad_token_id=-100,
    position_pad_token_id=0,
    return_tensors='pt',
    squash_position_ids=False,
)
```

## prompt_strategies.orcamini

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.orcamini.html

**内容：**
- prompt_strategies.orcamini
- 类别
  - OrcaMiniPrompter

prompt_strategies.orcamini

用于微调 Orca Mini (v2) 模型的提示策略，更多信息请参阅 https://huggingface.co/psmathur/orca_mini_v2_7b。

在 config.yml 中使用 `orcamini` 作为数据集类型即可采用此提示风格。

与 alpaca_w_system.open_orca 数据集类型相比，该类型会通过“### System:”来指定系统提示语。

未经进一步调整，不适用于多轮对话场景。

为 Orca Mini (v2) 数据集优化的提示器

**示例：**

示例 1（Python）：
```python
prompt_strategies.orcamini.OrcaMiniPrompter(
    prompt_style=PromptStyle.INSTRUCT.value,
)
```

## prompt_strategies.dpo.chat_template

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.dpo.chat_template.html

**内容：**
- prompt_strategies.dpo.chat_template
- 函数
  - argilla_chat
    - 参数
    - 返回值
    - 数据集格式

prompt_strategies.dpo.chat_template

用于基于分词器聊天模板的DPO提示策略。

专为argilla风格数据集设计的聊天模板策略。

针对那些“选中”/“拒绝”结果为完整对话而非单条回复消息的argilla风格数据集，该策略会从指定字段中提取对话历史，并使用配置好的聊天模板来格式化“选中”/“拒绝”对应的回复内容。

{ “chosen”: [ {“角色”: “用户”, “内容”: “…”}, {“角色”: “助手”, “内容”: “…”} ], “rejected”: [ {“角色”: “用户”, “内容”: “…”}, {“角色”: “助手”, “内容”: “…”} ] }

**示例：**

示例1（Python）：
```python
prompt_strategies.dpo.chat_template.argilla_chat(cfg, dataset_idx=0, **kwargs)
```

## monkeypatch.relora

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.relora.html

**目录:**
- monkeypatch.relora
- 类
  - ReLoRACallback

该模块实现了源自 https://arxiv.org/abs/2307.05695 的 ReLoRA 训练流程，但不包括最初的完整微调步骤。它作为一个回调函数，用于将 LoRA 权重合并到基础模型中，并保存完整权重的检查点。

**示例:**

示例 1（Python）：
```python
monkeypatch.relora.ReLoRACallback(cfg)
```

## monkeypatch.transformers_fa_utils

**网址：** https://docs.axolotl.ai/docs/api/monkeypatch.transformers_fa_utils.html

**目录：**
- monkeypatch.transformers_fa_utils
- 函数
  - fixed_fa_peft_integration_check
    - 参数

monkeypatch.transformers_fa_utils

详见：https://github.com/huggingface/transformers/pull/35834

出于训练稳定性的考虑，PEFT通常会将层归一化参数转换为浮点数32位格式，因此输入的隐藏状态也会被隐式地转换为浮点数32位格式。为确保一切按预期运行，我们需要将这些数据重新转换为浮点数16位或bfloat16格式。不过这可能会降低训练和推理的速度，因此建议不要对层归一化参数进行类型转换！

**示例：**

示例 1（Python）：
```python
monkeypatch.transformers_fa_utils.fixed_fa_peft_integration_check(
    query,
    key,
    value,
    target_dtype=None,
    preferred_dtype=None,
)
```

## utils.collators.mm_chat

**网址：** https://docs.axolotl.ai/docs/api/utils.collators.mm_chat.html

**目录：**
- utils.collators.mm_chat
- 类
  - MultiModalChatDataCollator

utils.collators.mm_chat

用于多模态聊天消息的处理与整合的工具类

多模态聊天消息专用整合工具类

**示例：**

示例 1（Python）：
```python
utils.collators.mm_chat.MultiModalChatDataCollator(
    tokenizer,
    processing_strategy,
    packing=False,
    return_tensors='pt',
    padding=True,
    pad_to_multiple_of=None,
)
```

## utils.lora

**网址：** https://docs.axolotl.ai/docs/api/utils.lora.html

**目录：**
- utils.lora
- 函数
  - get_lora_merged_state_dict
    - 参数
    - 返回值

用于获取已合并 LoRA 模型的状态字典的模块

该模块会创建一个新的状态字典，将 LoRA 微调参数合并到基础模型的权重中，而不会直接修改原始模型。

**示例：**

示例 1（Python）：
```python
utils.lora.get_lora_merged_state_dict(model)
```

## utils.model_shard_quant

**URL:** https://docs.axolotl.ai/docs/api/utils.model_shard_quant.html

**目录:**
- utils.model_shard_quant
- 函数
  - load_and_quantize

utils.model_shard_quant

该模块用于为 FSDP 在 CPU 或 Meta 设备上加载模型。
它将值张量加载到模块的子模块中，可选择跳过指定的 skip_names 并转换数据类型。
随后在设备上对参数进行 Params4bit 量化处理；若设置 to_cpu=True，则将量化后的参数放置到 “cpu” 设备上；若设置 to_meta=True，则放置到 “meta” 设备上。

**示例:**

示例 1（Python）：
```python
utils.model_shard_quant.load_and_quantize(
    module,
    name,
    value,
    device=None,
    dtype=None,
    skip_names=None,
    to_cpu=False,
    to_meta=False,
    verbose=False,
    quant_method='bnb',
)
```

## monkeypatch.gradient_checkpointing.offload_cpu

**网址：** https://docs.axolotl.ai/docs/api/monkeypatch.gradient_checkpointing.offload_cpu.html

**目录：**
- monkeypatch.gradient_checkpointing.offload_cpu
- 类
  - CPU_Offloaded_Gradient_Checkpointer

monkeypatch.gradient_checkpointing.offload_cpu

CPU卸载式检查点机制

通过智能地将计算任务卸载到RAM中，从而节省VRAM资源。由于采用非阻塞调用方式来隐藏该过程，因此对性能的影响极小。

**示例：**

示例1（Python）：
```python
monkeypatch.gradient_checkpointing.offload_cpu.CPU_Offloaded_Gradient_Checkpointer(
)
```

## core.builders.base

**URL:** https://docs.axolotl.ai/docs/api/core.builders.base.html

**内容：**
- corebuilders.base
- 类
  - TrainerBuilderBase
    - 方法
      - get_post_trainer_create_callbacks

训练器构建器的基类

用于构建训练器的基础类。这些回调函数会在训练器创建之后被添加，通常是因为它们需要访问该训练器。

**示例：**

示例 1（Python）：
```python
core.builders.base.TrainerBuilderBase(cfg, model, tokenizer, processor=None)
```

示例 2（Python）：
```python
core.builders.base.TrainerBuilderBase.get_post_trainer_create_callbacks(trainer)
```

## core.builders.rl

**网址：** https://docs.axolotl.ai/docs/api/core.builders.rl.html

**目录：**
- core.builders.rl
- 类
  - HFRLTrainerBuilder

用于 RLHF 训练器的构建器

基于 TRL 的 RLHF 训练器（如 DPO）的训练器工厂类

**示例：**

示例 1（Python）：
```python
core.builders.rl.HFRLTrainerBuilder(cfg, model, tokenizer, processor=None)
```

## utils.schemas.integrations

**网址：** https://docs.axolotl.ai/docs/api/utils.schemas.integrations.html

**目录结构：**
- utils.schemas.integrations
- 类
  - CometConfig
  - GradioConfig
  - LISAConfig
  - MLFlowConfig
  - OpenTelemetryConfig
  - RayConfig
  - WandbConfig

utils.schemas.integrations

用于 Axolotl 集成的 Pydantic 模型

Comet 配置子集

Gradio 配置子集

LISA 配置子集

MLFlow 配置子集

OpenTelemetry 配置子集

Ray 启动器配置子集

Wandb 配置子集

**示例：**

示例 1（Python）：
```python
utils.schemas.integrations.CometConfig()
```

示例 2（Python）：
```python
utils.schemas.integrations.GradioConfig()
```

示例 3（Python）：
```python
utils.schemas.integrations.LISAConfig()
```

示例 4（Python）：
```python
utils.schemas.integrations.MLFlowConfig()
```

## utils.data.sft

**网址：** https://docs.axolotl.ai/docs/api/utils.data.sft.html

**内容概览：**
- utils.data.sft
- 函数
  - prepare_datasets
    - 参数
    - 返回值

专为 SFT 场景设计的数据处理功能。

根据配置自动生成训练集与评估集。

**示例：**

示例 1（Python）：
```python
utils.data.sft.prepare_datasets(cfg, tokenizer, processor=None)
```

## integrations.liger.args

**网址：** https://docs.axolotl.ai/docs/api/integrations.liger.args.html

**内容：**
- integrations.liger.args
- 类
  - LigerArgs

integrations.liger.args

用于处理 LIGER 输入参数的模块。

LIGER 的输入参数。

**示例：**

示例 1（Python）：
```python
integrations.liger.args.LigerArgs()
```

---

## monkeypatch.mixtral

**URL:** https://docs.axolotl.ai/docs/api/monkeypatch.mixtral.html

**内容：**
- monkeypatch.mixtral

用于为 mixtral 提供多模型打包支持的补丁。

---

## cli.preprocess

**URL:** https://docs.axolotl.ai/docs/api/cli.preprocess.html

**内容：**
- cli.preprocess
- 函数
  - do_cli
    - 参数
  - do_preprocess
    - 参数

用于对数据集执行预处理操作的命令行工具。

该工具会解析 axolotl 配置及命令行参数，随后调用 do_preprocess 函数，对 axolotl 配置中指定的数据集进行预处理。

**示例：**

示例 1（Python）：
```python
cli.preprocess.do_cli(config=Path('examples/'), **kwargs)
```

示例 2（Python）：
```python
cli.preprocess.do_preprocess(cfg, cli_args)
```

## prompt_strategies.kto.llama3

**网址：** https://docs.axolotl.ai/docs/api/prompt_strategies.kto.llama3.html

**内容概览：**
- prompt_strategies.kto.llama3
- 函数
  - argilla_chat
  - intel
  - ultra

prompt_strategies.kto.llama3

适用于 llama-3 聊天模板的 KTO 策略

用于 argilla/kto-mix-15k 类型的对话场景

适用于 Intel Orca KTO 的版本：argilla/distilabel-intel-orca-kto

适用于 ultrafeedback 二值化对话场景的版本：argilla/ultrafeedback-binarized-preferences-cleaned-kto

**示例：**

示例 1（Python）：
```python
prompt_strategies.kto.llama3.argilla_chat(cfg, **kwargs)
```

示例 2（Python）：
```python
prompt_strategies.kto.llama3.intel(cfg, **kwargs)
```

示例 3（Python）：
```python
prompt_strategies.kto.llama3.ultra(cfg, **kwargs)
```

## prompt_strategies.orpo.chat_template

**URL:** https://docs.axolotl.ai/docs/api/prompt_strategies.orpo.chat_template.html

**内容:**
- prompt_strategies.orpo.chat_template
- 类
  - Message
  - MessageList
  - ORPODatasetParsingStrategy
    - 方法
      - get_chosen_conversation_thread
      - get_prompt
      - get_rejected_conversation_thread
  - ORPOPrompter

prompt_strategies.orpo.chat_template

用于 ORPO 的 chatml 提示词分词策略

用于将选中的数据集与被拒绝的数据集解析为消息列表的策略

数据集结构映射

用于提取截至上一轮的所有数据的映射规则

数据集结构映射

ORPO 的单轮提示词生成器

rejected_input_ids input_ids rejected_attention_mask attention_mask rejected_labels labels

针对包含系统信息、输入内容、选定数据及被拒绝数据的 数据集所适用的 chatml 转换功能

**示例:**

示例 1（Python）：
```python
prompt_strategies.orpo.chat_template.Message()
```

示例 2（Python）：
```python
prompt_strategies.orpo.chat_template.MessageList()
```

示例 3（Python）：
```python
prompt_strategies.orpo.chat_template.ORPODatasetParsingStrategy()
```

示例 4（Python）：
```python
prompt_strategies.orpo.chat_template.ORPODatasetParsingStrategy.get_chosen_conversation_thread(
    prompt,
)
```

## loaders.processor

**网址：** https://docs.axolotl.ai/docs/api/loaders.processor.html

**内容：**
- loaders.processor

用于多模态模型的处理器加载功能

---

## utils.callbacks.comet_

**网址：** https://docs.axolotl.ai/docs/api/utils.callbacks.comet_.html

**内容：**
- utils.callbacks.comet_
- 类
  - SaveAxolotlConfigtoCometCallback

utils.callbacks.comet_

用于训练器回调的 Comet 模块

用于将 Axolotl 配置保存到 Comet 的回调功能

**示例：**

示例 1（Python）：
```python
utils.callbacks.comet_.SaveAxolotlConfigtoCometCallback(axolotl_config_path)
```

---
Hermes Agent的技术文档、CLI使用指南、智能体功能、插件、服务提供商相关内容以及开发者指南。
