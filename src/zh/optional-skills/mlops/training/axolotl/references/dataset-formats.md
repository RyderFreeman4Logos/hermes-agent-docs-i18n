# Axolotl - 数据集格式

**页数：** 9

---

## 自定义预分词数据集

**网址：** https://docs.axolotl.ai/docs/dataset-formats/tokenized.html

**目录：**
- 自定义预分词数据集

**示例：**

示例 1（yaml格式）：
```yaml
datasets:
  - path: /path/to/your/file.jsonl
    ds_type: json
    type:
```

示例 2（JSON格式）：
```json
{"input_ids":[271,299,99],"attention_mask":[1,1,1],"labels":[271,-100,99]}
{"input_ids":[87,227,8383,12],"attention_mask":[1,1,1,1],"labels":[87,227,8383,12]}
```

## 数据集格式

**网址：** https://docs.axolotl.ai/docs/dataset-formats/index.html

**内容：**
- 数据集格式
- 预训练
  - 基于 Hugging Face 仓库中的数据集进行预训练
  - 基于本地数据集文件进行预训练
  - 不使用流式处理进行预训练
  - 预训练数据集配置技巧
    - 设置 max_steps 参数
    - 使用 Group_by_length 功能
  - 参考资料
- 监督微调（SFT）

Axolotl 是一个训练框架，通过让用户只需传递一个 YAML 配置文件，即可让训练过程既便捷又灵活。

由于 Axolotl 提供了大量选项，本指南旨在简化用户选择合适配置的过程。

Axolotl 支持三种训练方式：预训练、监督微调以及基于偏好的后续训练（如 DPO、ORPO、PRMs）。每种方式都有对应的数据集格式，具体说明如下。

本指南将以 JSONL 格式作为介绍示例。如需了解如何从其他来源加载数据集，请参阅数据集加载相关文档。

关于 pretraining_dataset 的具体内容，请参考“预训练”部分。

当需要处理大规模文本数据集时，预训练是最佳选择。由于这类数据集体积庞大，若在开始训练前就下载完整数据集，将会耗费大量时间。Axolotl 支持流式处理，只需一次性将分批数据加载到内存中。

预训练数据集的示例格式如下：

通常建议将数据集保存为 .jsonl 格式，因其兼具灵活性与简洁性。

Axolotl 支持从 Hugging Face 仓库或本地文件加载数据集。

例如，若要使用 Hugging Face 中名为 hf_org/name 的数据集进行训练，可传递如下配置：

若有 A.jsonl、B.jsonl 和 C.jsonl 三个数据文件，相应的配置文件内容如下所示：

虽然我们推荐使用 .jsonl 格式，但您也可以使用 Dataset.load_dataset 支持的其他格式（如 csv、parquet、arrow、SQL、Webdataset）。

如果数据集规模较小且可以完整加载到内存中，另一种预训练方法是采用完整分词格式。这意味着整个数据集会提前进行分词处理，而非通过流式方式按需分词。

这样做的好处在于，可以先在仅配备 CPU 的机器上完成分词工作，再将处理结果传输到 GPU 机器上进行训练，从而节省成本。

对于仅使用完整分词格式的情况，如果文本超出上下文长度，Axolotl 会将其拆分为多个较小的提示语。如果您也希望 pretraining_dataset 支持此功能，请告知我们或协助提交 Pull Request！

在使用流式处理大规模数据集时，Axolotl 无法提前知晓数据集的具体规模，也无法确定何时停止处理。

因此，在预训练配置中必须设置 max_steps：int 参数，以便 Axolotl 知道何时结束训练。

一个训练步骤所对应的 token 数量为 sequence_len * micro_batch_size * gradient_accumulation_steps * total_num_gpus。

如果从 Hugging Face 仓库下载数据集，建议不设置该参数，因为这样会下载整个数据集，而其体积可能非常大。

详情请参阅相关文档。

监督微调是指训练模型以响应指令或聊天输入的过程。

由于存在多种多样的数据集格式，Axolotl 力求支持公共数据集中最常见的格式。

Axolotl 提供了四种数据集加载方式，不过更简便的方法是根据现有数据集反向判断应使用哪种方式。

决策流程图如下：

您的数据集是否已经过分词处理？如果是，请查看“预分词数据集”部分。

您是否希望自行格式化数据集，并手动选择需要遮掩的字段？如果是，请查看“无模板数据集”部分。

您的数据集是否为“对话”格式，即包含 list[messages] 结构？如果是，请查看“对话数据集”部分。

您的数据集是否为“指令”格式，即包含 { instruction, response } 结构？如果是，请查看“指令数据集”部分。

如果您按照流程图检查后仍找不到匹配的类型，建议将数据集预处理为上述某种格式，或是在 Github Discussion 中发起讨论。

您可以在同一方法或不同方法之间灵活组合，以便使用多种数据集训练模型。

当您希望使用自己已分词处理的数据集时，我们推荐采用此方法。

Axolotl 要求数据集包含三个键值：

请务必在提示语中添加 BOS/EOS 令牌，并进行适当的遮掩处理。

相应的配置文件示例如下：

参考资料：预分词数据集文档。

当您希望对提示语格式、特殊令牌及遮掩处理进行精细控制，同时让 Axolotl 负责分词工作时，我们推荐采用此方法。如果您的数据集中包含因样本不同而各不相同的独特提示语，且单一通用模板无法满足需求，此方法尤为实用。

在下面的示例中，可以看到该数据集没有固定的结构。不过它的灵活性很高，因为对提示语的格式没有任何限制。

每个提示语都必须包含一个名为 segments 的键，该键是一个包含 { text, label } 元组的列表。

参考资料：无模板文档。

对话消息是一组消息的列表，通常包含 role 和 content 两个键值。

有趣的是：由于 FastChat 在创建 chat_templates 之前，曾使用“对话消息”这一术语来构建一种广泛应用的聊天消息格式化方法，因此 Axolotl 也用“对话消息”来指代“聊天消息”。

目前最常用且最便捷的推理方法是使用 chat_templates 来格式化提示语。Axolotl 也支持在训练过程中使用 chat_templates，以确保模型在训练环境与推理环境中的表现一致。

以下是关于 chat_template 的简要说明：chat_template 是一种 Jinja2 模板，用于将一组消息格式化为一个提示语。

下面是一个按照名为 ChatML 的常用模板格式化后的提示语示例：

格式化后的单个提示语（美观展示）：

ChatML 模板的结构如下：

将上述提示语按照该模板格式化后，结果如下：

通过使用分隔符 <|im_start|> 和 <|im_end|>，提示语可以区分不同的发言者，从而帮助模型识别各部分属于哪一方。

那些采用以下格式的旧版对话数据集，通常被称为 sharegpt 数据集。

较新的对话数据集则通常遵循 OpenAI 格式。

Axolotl 同时支持这两种格式，并允许用户自定义各类键值。

要正确使用此方法，需要明确三件事：

您将使用哪种 chat_template？

您的数据集中包含哪些键值，可能的角色有哪些？例如，在 OpenAI 格式中，键值分别为 messages、role 和 content，而可能的角色包括 system、user 和 assistant。

您希望遮掩哪些内容？例如，仅遮掩 assistant 的消息、仅遮掩最后一条消息，或不进行任何遮掩。

目前存在大量不同的 chat_template。Axolotl 支持常见的几种模板：已支持的 chat template。例如，若要使用 ChatML 模板，需设置 chat_template: chatml。

不过，也可以通过指定 chat_template: tokenizer_default，在分词器中直接使用已配置好的模板。如果您希望有备用方案（以防某些分词器未预配置该模板），可以设置 chat_template: tokenizer_default_fallback_chatml，这样在找不到对应模板时就会自动回退到 ChatML 模板。

最后还有一种非常强大的方法，那就是自行创建模板。可通过以下方式设置：

我们目前默认使用 OpenAI 格式作为数据集键值，因此如果您的数据集已经是该格式，则无需做任何调整。

如果您的数据集格式不同，以下是需要检查的键值及其默认值：

在某些 chat_template 中（例如 Gemma），角色被硬编码为 user 和 assistant。因此，您可能需要对数据集中的角色进行映射，使其与上述角色对应。我们目前提供了一些适用于常见数据集的默认映射规则，但如果出现 KeyError 错误，则需要为您的角色添加自定义映射。示例如下：

在上面的示例中，所有的 gpt 和 model 值都会被转换为 assistant，所有 human 值则会被转换为 user。

chat_template 的常见应用场景是处理聊天消息，因此通常会遮掩所有非 assistant 类型的消息。assistant 消息指的是您希望模型学习的机器人回复内容。

若要使用所有 assistant 消息进行训练，需设置以下配置。

train_on_eos 参数表示会遮掩非 assistant 轮次中的所有 EOS 令牌。其他可选值包括 all 和 last，用于指定要用于训练的 EOS 令牌类型。

如果您希望同时使用 assistant 和 narrator 角色进行训练，只需在 roles_to_train 列表中添加 narrator 即可。同时还需要在上面的角色映射表中添加该角色。

由于 chat_template 可能会使用与分词器默认 EOS 令牌不同的硬编码 EOS/EOT 令牌，因此强烈建议手动设置这些令牌。例如，ChatML 使用 <|im_end|> 作为轮次结束标记。

完成以上所有步骤后，您可以将这些配置组合起来，为自定义数据集创建专属的配置文件。

如果将此配置应用于上面的示例数据集，输出结果如下（可通过命令 axolotl preprocess config.yaml --debug 查看）：

第一个数字代表标签值，第二个数字代表 token_id。例如，-100 表示非 assistant 部分的标签，意味着这些部分会在处理过程中被遮掩；而对于 assistant 部分，标签值与 token_id 相同。

如果在预处理过程中出现大量“无法找到 content __ boundary”的警告，请查阅 chat_template 相关的常见问题解答。

详情请参阅相关文档。

指令数据集用于训练遵循指令的模型，每个数据集包含一个包含指令的提示语以及一个对应的回复。与可能包含多轮对话的聊天数据集不同，指令数据集通常为单轮结构。

下面是一个名为 Alpaca 的常见格式示例：

利用这些键值，即可构建相应的提示语。

其配置方式如下：

Axolotl 支持多种类型的指令数据集。所有类型的详细信息及其对应的类型和样本行格式，均可在“指令数据集文档”中找到。

由于指令格式存在多种可能性，Axolotl 允许用户无需直接修改代码，即可自定义指令格式。

在下面的示例中，展示了一个按照 mistral_v1 格式输出的样本行。该配置将 field_instruction 的实际名称设置为 input，而 field_input 保持为空，因为在本示例中并未提供输入内容。通常而言，instruction 可以被视为向模型提出的问题，input 则是补充信息，最终输出即为模型的回答。实际上，并非必须要有输入或系统。归根结底，最重要的是明确你希望输出的内容格式，以及如何根据具体需求对其进行定制。

参考文档：自定义指令提示格式指南。

由于存在多种具有不同数据集要求的 RLHF 方法，详情请参阅 RLHF 相关文档。

**示例：**

示例 1（json 格式）：
```json
{"text": "first row"}
{"text": "second row"}
...
```

示例 2（yaml 格式）：
```yaml
pretraining_dataset: hf_org/name
```

示例 3（yaml 格式）：
```yaml
pretraining_dataset:
  - path: json
    data_files:
      - A.jsonl
      - B.jsonl
      - C.jsonl
```

示例 4（yaml 格式）：
```yaml
datasets:
  - path: hf_org/name
    type: completion
```

## 对话格式

**URL:** https://docs.axolotl.ai/docs/dataset-formats/conversation.html

**目录:**
- 对话格式
- 聊天模板
  - 从 ShareGPT 迁移
  - 示例
    - 基于最后一条消息进行训练
    - 覆盖默认聊天模板
    - 使用带备用方案的默认聊天模板
    - 自定义 Jinja 模板
    - 使用区分 EOT 和 EOS 标识的模板
    - 使用工具功能

聊天模板策略会使用 Jinja2 模板将消息列表转换为提示词。支持使用分词器的模板、官方支持的模板或自定义的 Jinja2 模板。

完整的配置及支持的模板信息请参阅相关文档。

大多数配置均可按以下方式调整：

我们建议参考以下示例以了解其他应用场景。

（旧版本）在 OpenAI 消息格式的 tokenizer_config.json 中使用默认聊天模板，仅基于最后一条消息进行训练。

如果出现“chat_template 选项为 tokenizer_default，但分词器的 chat_template 为 null”之类的错误，说明该分词器没有默认聊天模板。请参考以下示例来设置自定义聊天模板。

使用 gemma 聊天模板覆盖 OpenAI 消息格式的 tokenizer_config.json 中的聊天模板，对所有助手消息进行训练。

若想使用内置聊天模板，可设置 chat_template: tokenizer_default（此为默认值）。

在 OpenAI 消息格式下，如果 tokenizer_config.json 中的聊天模板不存在，则使用其对应的 chatml 模板作为备用，对所有助手消息进行训练。

在 OpenAI 消息格式下，使用自定义 Jinja 模板，对所有助手消息进行训练。

请确保您的 tokenizer.eos_token 与模板中的 EOS（序列结束）标记一致。否则，请在 special_tokens 下设置 eos_token。

关于针对不同标记进行训练时的 “turn”、“last” 和 “all” 选项的详细说明，请参阅配置文档。

若使用 eot_tokens，聊天模板中的每个标记都必须在分词器中对应为一个独立的标记。否则，分词器会对这些标记进行拆分，从而导致异常行为。

您可以将这些标记作为新标记添加到 tokens: 下，或者（推荐做法）通过 added_tokens_overrides: 覆盖那些未被使用的额外标记。更多详情请参阅配置文档。

如果 EOS 标记仅出现在提示词的末尾，那么 train_on_eos: last 与 train_on_eos: turn 的效果相同。因此，通常可直接保留默认设置而不必更改。

除了通过系统提示词传递工具信息外，另一种方法是将工具信息放在单独的列中，并通过聊天模板动态加载，从而让模板自行构建这些工具信息。

工具信息需遵循 JSON 规范。

如果您的工具参数名称相同但数据类型不同（例如 “time”: string 和 “time”: number），请将参数值以 JSON 字符串的形式保存，以避免数据集中出现类型转换问题。

以下是 Llama4 的示例配置：

请查看您正在使用的聊天模板，确认其是否支持工具功能，以及工具回复应采用何种角色。在上面的示例中，Llama4 模板要求工具回复使用 tool 或 ipython 角色。

（高级用法）通过对标记和对话轮次进行精细控制，在对话场景中进行训练

对于如下格式的数据样本：

对应的配置如下：

无需同时设置 message_field_training 和 message_field_training_detail 两个参数。

（仅适用于 Qwen3 模板）可启用推理分离功能，即将推理内容与主体内容分开，并作为单独字段传递给模板。

例如，原始内容可能为：

分离后的格式将为：

ShareGPT 已过时！请参阅聊天模板相关章节。

**示例：**

示例 1（JSON 格式）：
```json
{"messages": [{"role": "...", "content": "..."}, {"role": "...", "content": "..."}, ...]}
```

示例 2（yaml 格式）：
```yaml
# old
chat_template: chatml
datasets:
  - path: ...
    type: sharegpt
    conversation: chatml

# new (if using tokenizer's chat_template)
datasets:
  - path: ...
    type: chat_template

    field_messages: conversations
    message_property_mappings:
      role: from
      content: value

# new (if setting a new chat_template like chatml, gemma, etc)
chat_template: chatml
datasets:
  - path: ...
    type: chat_template

    field_messages: conversations
    message_property_mappings:
      role: from
      content: value
```

示例 3（yaml 格式）：
```yaml
datasets:
  - path: ...
    type: chat_template
    roles_to_train:
    train_on_eos:
```

示例 4（yaml 格式）：
```yaml
chat_template: gemma # this overwrites the tokenizer's chat_template
datasets:
  - path: ...
    type: chat_template
    roles_to_train: ["assistant"]  # default value
```

## 预训练

**网址：** https://docs.axolotl.ai/docs/dataset-formats/pretraining.html

**内容：**
- 预训练

在预训练过程中无需使用提示词模板或角色设定。唯一需要填写的字段就是文本内容：

Axolotl通常会将整个数据集加载到内存中。对于规模较大的数据集而言，这种方式会带来较大挑战。建议使用以下配置来实现流式处理：

**示例：**

示例 1（json格式）：
```json
{"text": "first row"}
{"text": "second row"}
...
```

示例 2（yaml 格式）：
```yaml
pretraining_dataset:
  - name:
    path:
    split:
    text_column: # column in dataset with the data, usually `text`
    type: pretrain
    trust_remote_code:
    skip: # number of rows of data to skip over from the beginning
```

## 无模板模式

**URL:** https://docs.axolotl.ai/docs/dataset-formats/template_free.html

**目录:**
- 无模板模式
- 背景知识
  - 输入遮蔽
  - 为何可能不需要提示词模板
  - input_output格式
- 使用方法
  - 1. 准备数据
  - 2. 使用type: input_output
  - 3. 检查提示词

Axolotl最受欢迎的功能之一便是支持设置以下配置值：

当您声明如alpaca或chatml之类的数据集格式时，Axolotl会自动区分输入（即人类输入）与输出（即助手生成的内容），并会对输入部分进行遮蔽处理，从而让模型专注于预测输出结果。

不过，在许多情况下，您可能并不希望使用这些预设格式或模板。因为它们可能会带来以下问题：

您可以通过使用input_output格式来构建无需模板的提示词，具体操作是在配置文件中设置`type: input_output`，示例如下：

虽然`type: completion`同样属于无模板模式，但`type: input_output`还允许您对文本的特定部分进行遮蔽处理。其工作原理的更多细节将在下文介绍。

以下是使用input_output格式的具体步骤：

要使用该格式，请将数据按如下结构收集到jsonl文件中（下方为output.jsonl文件的第一行，已进行格式美化）：

若希望遮蔽某段文本，使其不参与模型训练，请将对应标签设置为`false`。需注意以下几点：

[!IMPORTANT] 1. EOS、BOS、空格、换行符等符号完全由您自行决定。Axolotl会原样拼接所有片段，分词器不会添加任何额外内容。请注意，是我自己添加了空格、换行符、<s>（BOS）和</s>（EOS）这些符号。2. 请务必查看生成后的输出结果，确认提示词已按预期组合。

我们可以通过在Axolotl配置中设置`type: input_output`，利用output.jsonl文件来生成实际数据：

您可以使用以下命令来处理数据。添加`--debug`参数后，系统会同时显示标记符及其标签，便于您确认是否有正确的元素被忽略：

数据的格式为`decoded_token(label, token_id)`，例如：<s>(1, 1)表示该标记符为<s>，标签值为1，标记符编号为1。若标签值为-100，则该标记符将在训练过程中被忽略。

还有另一种方法可以检查生成后的输出：

我们可以通过对比每个标记符的标签值，确认是否有正确的标记符被忽略：

查看输入数据后，上表的结果似乎是正确的！（下方重复列出jsonl格式的内容以供参考）：

**示例：**

示例1（yaml格式）：
```yaml
train_on_inputs: false
```

示例 2（yaml 格式）：
```yaml
train_on_inputs: false # Mask segments of your data
datasets:
  - path: output.jsonl
    type: input_output  # use template free prompt construction
```

示例 3（bash）：
```bash
$ head -n1 output.jsonl | python -m json.tool
```

示例 4（未知情况）：
```unknown
{
    "segments": [
        {
            "label": true,
            "text": "<s>Hello\n"
        },
        {
            "label": true,
            "text": "hi there!. "
        },
        {
            "label": false,
            "text": "goodbye "
        },
        {
            "label": true,
            "text": "farewell</s>"
        }
    ]
}
```

## 数据集格式

**网址：** https://docs.axolotl.ai/docs/dataset-formats/

**内容：**
- 数据集格式
- 预训练
  - 基于 Hugging Face 数据集库进行预训练
  - 基于本地数据集文件进行预训练
  - 不使用流式处理的预训练
  - 预训练数据集配置技巧
    - 设置 max_steps 参数
    - 使用 Group_by_length 功能
  - 参考资料
- 监督微调（SFT）

Axolotl 是一个训练框架，通过让用户只需传递一个配置 YAML 文件，即可让训练过程既便捷又灵活。

由于 Axolotl 提供了大量选项，本指南旨在简化用户选择合适选项的过程。

Axolotl 支持三种训练方式：预训练、监督微调以及基于偏好的后续训练（如 DPO、ORPO、PRMs）。每种方式都有对应的数据集格式，具体如下所述。

本指南将以 JSONL 格式作为介绍示例。如需了解如何从其他来源加载数据集，请参阅数据集加载相关文档。

关于 pretraining_dataset 的具体内容，请参考“预训练”部分。

当需要处理大规模文本数据集时，预训练是最佳选择。由于这类数据集体积庞大，若在开始训练前就下载完整数据集，将耗费大量时间。Axolotl 支持流式处理，可一次仅将批次数据加载到内存中。

预训练数据集的示例格式如下：

通常建议将数据集保存为 .jsonl 格式，因其具有灵活性和简洁性。

Axolotl 支持从 Hugging Face 数据库仓库或本地文件加载数据集。

例如，若要使用 Hugging Face 中名为 hf_org/name 的数据集进行训练，可传递如下配置：

若有 A.jsonl、B.jsonl 和 C.jsonl 三个数据文件，相应的配置文件格式如下所示：

虽然我们推荐使用 .jsonl 格式，但您也可以使用 Dataset.load_dataset 支持的其他格式（如 csv、parquet、arrow、SQL、Webdataset）。

如果数据集规模较小且可完全加载到内存中，另一种预训练方法是采用完整格式。这意味着整个数据集会先被预分词，而非通过流式处理按需分词。

这样做的一个优点是，可以先在仅配备 CPU 的机器上完成分词工作，再将结果传输到 GPU 机器上进行训练，从而节省成本。

对于仅使用完整格式的情况，如果文本超过上下文长度，Axolotl 会将其拆分为多个较短的提示语。如果您也希望 pretraining_dataset 支持此功能，请告知我们或协助提交改进请求！

在使用流式处理大规模数据集时，Axolotl 无法提前知晓数据集的具体规模，也无法确定何时停止处理。

因此，在预训练配置中必须设置 max_steps：int 参数，以便 Axolotl 知道何时结束训练。

一个“步骤”相当于 sequence_len * micro_batch_size * gradient_accumulation_steps * total_num_gpus tokens 的数值。

如果从 Hugging Face 数据库下载数据集，建议不设置该参数，因为这样会下载整个数据集，而其体积可能非常大。

详情请参阅相关文档。

监督微调是指训练模型以响应指令或聊天输入的过程。

由于存在多种多样的数据集格式，Axolotl 力求支持公共数据集中常见的绝大多数格式。

Axolotl 提供了四种数据集加载方式，不过，从您现有的数据集出发反向判断使用哪种方式会更为简便。

具体流程如下：

您的数据集已经过分词处理了吗？如果是，请查看“预分词数据集”部分。

您希望自行格式化数据集，并手动选择需要遮蔽的各部分内容吗？如果是，请查看“无模板数据集”部分。

您的数据集是否采用“对话”格式，即包含一个 list[messages] 结构？如果是，请查看“对话数据集”部分。

您的数据集是否采用“指令”格式，即包含 { instruction, response } 结构？如果是，请查看“指令数据集”部分。

如果您按照上述流程检查后仍找不到匹配的类型，建议将数据集预处理为上述某一种格式，或是在 Github 讨论区发起讨论。

您可以在每种方法内部或跨方法混合使用，从而利用多种数据集训练模型。

当您希望使用自行分词的数据集时，我们推荐采用此方法。

Axolotl 要求数据集包含三个键值：

请务必在提示语中添加 BOS/EOS 令牌，并进行适当的遮蔽处理。

相应的配置文件格式如下：

参考资料：预分词数据集文档。

当您希望对提示语的格式、特殊令牌及遮蔽处理进行精细控制，同时让 Axolotl 负责分词工作时，我们推荐采用此方法。如果您的数据集中包含因样本不同而各不相同的独特提示语，且单一通用模板无法满足需求，此方法尤为实用。

在下面的示例中，可以看到该数据集没有固定的结构。但同时它的灵活性也很高，因为对提示语的格式没有任何限制。

每个提示语都必须包含一个名为 segments 的键，该键是一个包含 { text, label } 元组的列表。

参考资料：无模板文档。

对话消息通常是一个包含 role 和 content 键的列表。

有趣的是：由于 FastChat 在创建 chat_templates 之前，最初就是使用“对话消息”这一术语来构建一种广泛应用的聊天消息格式化方法，因此 Axolotl 也用“对话消息”来指代“聊天消息”。

目前最流行且最便捷的推理方法是使用 chat_templates 来格式化提示语。Axolotl 也支持在训练过程中使用 chat_templates，以确保模型在训练环境与推理环境中的表现一致。

以下是关于 chat_template 的简要说明：chat_template 是一种 Jinja2 模板，用于将一系列消息格式化为一个提示语。

下面是一个按照名为 ChatML 的流行模板格式化后的提示语示例：

格式化后的单个提示语（美观展示版）：

ChatML 模板的结构如下：

将上述提示语按照该模板格式化后，结果如下：

通过使用分隔符 <|im_start|> 和 <|im_end|>，提示语可以区分不同的发言者，从而帮助模型识别各部分内容属于谁。

采用以下格式的较旧对话数据集，通常被称为 sharegpt 数据集。

较新的对话数据集则通常遵循 OpenAI 格式。

Axolotl 同时支持这两种格式，并允许自定义各类键值。

要正确使用此方法，需要明确三件事：

您将使用哪种 chat_template？

您的数据集中有哪些键值？可能的角色有哪些？例如，在 OpenAI 格式中，键值分别为 messages、role 和 content，而可能的角色包括 system、user 和 assistant。

您希望遮蔽哪些内容？例如，仅遮蔽助手消息、仅遮蔽最后一条消息，或不进行任何遮蔽。

目前存在许多不同的 chat_template。Axolotl 支持常见的模板：已支持的 chat templates。例如，若要使用 ChatML，可设置 chat_template: chatml。

不过，也可以通过指定 chat_template: tokenizer_default，在分词器中直接使用已配置好的模板。如果您希望有备用方案（以防某些分词器未预配置该模板），则可以设置 chat_template: tokenizer_default_fallback_chatml，以便在找不到对应模板时自动回退到 ChatML 模板。

最后还有一种非常强大的方法，即自行创建模板。可通过以下方式设置：

我们目前默认使用 OpenAI 格式作为数据集键值，因此如果您的数据集已采用该格式，则无需做任何调整。

如果您的数据集格式不同，以下是需要检查的键值及其默认值：

在某些 chat_template 中（如 Gemma），角色被硬编码为 user 和 assistant。因此，您可能需要对数据集中的角色进行映射，使其对应上述角色。我们目前提供了一些适用于常见数据集的默认映射规则，但如果出现 KeyError 错误，则需要为您的角色添加自定义映射。示例如下：

在上面的示例中，所有 gpt 和 model 类型的值都会被转换为 assistant，所有人类相关的值则会被转换为 user。

chat_template 的常见应用场景是处理聊天消息，因此通常会遮蔽所有非助手消息。助手消息指的是您希望模型学习的机器人回复内容。

若要针对所有助手消息进行训练，可设置以下配置。

train_on_eos 配置意味着会遮蔽非助手轮次中的所有 EOS 令牌。其他可选值为 all 和 last，用于指定要基于哪种 EOS 令牌进行训练。

也许您希望同时针对助手角色和叙述者角色进行训练，只需在 roles_to_train 列表中添加 narrator 即可。同时还需要在上面的角色映射表中加入该角色。

由于 chat_template 可能使用与分词器默认 EOS 令牌不同的硬编码 EOS/EOT 令牌，因此强烈建议手动设置这些令牌。例如，ChatML 使用 <|im_end|> 作为轮次结束标记。

完成以上所有步骤后，您可以将这些配置组合起来，为您的定制数据集生成专属配置。

如果将此配置应用于上面的示例数据集，输出结果如下（可通过 axolotl preprocess config.yaml --debug 命令查看）：

第一个数字代表标签值，第二个数字代表 token_id。例如，-100 标签出现在非助手内容部分，表示这些内容会被遮蔽；而在助手内容部分，标签值与 token_id 相同。

如果在预处理过程中出现大量“无法找到 content __ boundary”的警告，请查阅 chat_templates 相关的常见问题解答。

详情请参阅相关文档。

指令数据集用于训练指令遵循模型，每个数据集包含一个包含指令的提示语以及一个对应的回复。与可能包含多轮对话的聊天数据集不同，指令数据集通常为单轮结构。

下面是一个名为 Alpaca 的常见格式示例：

利用这些键值，即可构建相应的提示语。

其配置方式如下：

Axolotl 支持多种类型的指令数据集。所有类型的详细信息及其对应的类型和样本行格式，均可在指令数据集文档中找到。

由于指令格式存在诸多可能性，Axolotl 允许用户无需直接修改代码，即可自定义指令格式。

在下面的示例中，展示了一个按照 mistral_v1 格式输出的样本行。该配置将 field_instruction 的实际名称设置为 input，而 field_input 保持为空，因为在本示例中并未提供输入内容。通常而言，instruction 可以视为向模型提出的问题，input 则是补充信息，最终输出即为模型的响应。实际上，并非必须要有输入或系统支持。归根结底，最重要的是明确你希望输出的内容格式，以及如何根据具体需求对其进行定制。

参考文档：自定义指令提示格式指南。

由于存在多种具有不同数据集要求的 RLHF 方法，详情请参阅 RLHF 相关文档。

**示例：**

示例 1（json 格式）：
```json
{"text": "first row"}
{"text": "second row"}
...
```

示例 2（yaml 格式）：
```yaml
pretraining_dataset: hf_org/name
```

示例 3（yaml 格式）：
```yaml
pretraining_dataset:
  - path: json
    data_files:
      - A.jsonl
      - B.jsonl
      - C.jsonl
```

示例 4（yaml 格式）：
```yaml
datasets:
  - path: hf_org/name
    type: completion
```

## 数据集格式

**网址：** https://docs.axolotl.ai/docs/dataset-formats

**内容：**
- 数据集格式
- 预训练
  - 基于 Hugging Face 数据集库进行预训练
  - 基于本地数据集文件进行预训练
  - 不使用流式处理进行预训练
  - 预训练数据集配置技巧
    - 设置 max_steps
    - Group_by_length
  - 参考资料
- 监督微调（SFT）

Axolotl 是一个训练框架，用户只需传递一个配置 YAML 文件，即可让训练过程既便捷又灵活。

由于 Axolotl 提供了大量可选选项，本指南旨在简化用户选择合适配置的过程。

Axolotl 支持三种训练方式：预训练、监督微调以及基于偏好的后续训练（如 DPO、ORPO、PRMs）。每种方式都有对应的数据集格式，具体如下所述。

本指南将以 JSONL 格式作为介绍示例。如需了解如何从其他来源加载数据集，请参阅数据集加载相关文档。

关于 pretraining_dataset 的具体内容，请参阅“预训练”部分。

当需要处理大规模文本数据集时，预训练是最佳选择。由于这类数据集体积庞大，若在开始训练前就下载完整数据集，将耗费大量时间。Axolotl 支持流式处理，只需一次性将少量数据加载到内存中。

预训练数据集的示例格式如下：

通常建议将数据集保存为 .jsonl 格式，因其兼具灵活性与简洁性。

Axolotl 支持从 Hugging Face 数据库仓库或本地文件加载数据集。

例如，若要使用 Hugging Face 中的 hf_org/name 数据集进行训练，可传递如下配置：

若有 A.jsonl、B.jsonl 和 C.jsonl 三个数据文件，相应的配置如下所示：

虽然我们推荐使用 .jsonl 格式，但您也可以使用 Dataset.load_dataset 支持的其他格式（如 csv、parquet、arrow、SQL、Webdataset）。

如果数据集规模较小且可以完全加载到内存中，另一种预训练方法是采用完整格式。这意味着整个数据集会先被预分词，而非通过流式处理按需分词。

这样做的一个优点是，可以先在仅配备 CPU 的机器上完成分词工作，再将结果传输到 GPU 机器上进行训练，从而节省成本。

对于仅使用完整格式的情况，如果文本超出上下文长度，Axolotl 会将其拆分为多个较小的提示词。如果您也希望 pretraining_dataset 支持此功能，请告知我们或协助提交 Pull Request！

在使用流式处理大规模数据集时，Axolotl 无法提前知晓数据集的具体规模，也无法确定何时停止处理。

因此，在预训练配置中必须设置 max_steps：int 参数，以便 Axolotl 知道何时终止训练。

一个训练步骤所对应的token数量为 sequence_len * micro_batch_size * gradient_accumulation_steps * total_num_gpus tokens。

如果从 Hugging Face 数据库下载数据集，建议不设置此参数，因为这样会下载整个数据集，而其体积可能非常大。

详情请参阅相关文档。

监督微调是指训练模型以响应指令或聊天输入的过程。

由于存在多种多样的数据集格式，Axolotl 力求支持公共数据集中最常见的格式。

Axolotl 提供了四种数据集加载方式，不过更简单的方法是根据现有数据集反向判断应使用哪种方式。

决策流程图如下：

您的数据集已经过分词处理了吗？如果是，请查看“预分词数据集”部分。

您希望自行格式化数据集，并手动选择需要掩码的字段吗？如果是，请查看“无模板数据集”部分。

您的数据集是否为“对话”格式，即包含 list[messages] 结构？如果是，请查看“对话数据集”部分。

您的数据集是否为“指令”格式，即包含 { instruction, response } 结构？如果是，请查看“指令数据集”部分。

如果您按照流程图检查后仍找不到匹配的类型，建议将数据集预处理为上述某一种格式，或是在 Github 讨论区发起讨论。

您可以在同一方法或不同方法之间混合搭配，从而利用多种数据集训练模型。

当您希望使用自己已分词的数据集时，我们推荐采用此方法。

Axolotl 要求数据集包含三个键：

请务必在提示词中添加 BOS/EOS 令牌，并进行适当的掩码处理。

相应的配置如下所示：

参考资料：预分词数据集文档。

当您希望对提示词格式、特殊令牌及掩码处理进行精细控制，同时让 Axolotl 负责分词工作时，我们推荐采用此方法。如果您的数据集中包含因样本不同而各不相同的独特提示词，且单一通用模板无法满足需求，此方法尤为实用。

在下面的示例中，可以看到该数据集没有固定的结构。不过它的灵活性很高，因为对提示词的形式没有任何限制。

每个提示词都必须包含一个名为 segments 的键，该键是一个包含 { text, label } 元组的列表。

参考资料：无模板文档。

对话消息是一组消息的列表，通常包含 role 和 content 两个键。

小知识：由于 FastChat 在创建 chat_templates 之前，曾使用“conversation messages”这一术语来构建一种广泛应用的聊天消息格式化方法，因此 Axolotl 也用“chat”消息来指代“conversation messages”。

目前最流行且最便捷的推理方法是使用 chat_templates 来格式化提示词。Axolotl 也支持在训练过程中使用 chat_templates，以确保模型在训练环境与推理环境中的表现一致。

以下是关于 chat_template 的简要说明：chat_template 是一种 Jinja2 模板，用于将一组消息格式化为一个提示词。

下面是一个按照名为 ChatML 的流行模板格式化后的提示词示例（已美化显示）：

ChatML 模板的结构如下：

将上述提示词按此模板格式化后，结果如下：

通过使用分隔符 <|im_start|> 和 <|im_end|>，提示词可以区分不同的说话者，从而帮助模型识别每部分内容属于谁。

采用以下格式的较旧对话数据集，通常被称为 sharegpt 数据集。

较新的对话数据集则通常遵循 OpenAI 格式。

Axolotl 同时支持这两种格式，并允许自定义各类键。

要正确使用此方法，需要明确三件事：

您打算使用哪种 chat_template？

您的数据集中有哪些键，可能的角色有哪些？例如，在 OpenAI 格式中，键分别为 messages、role 和 content，而可能的角色包括 system、user 和 assistant。

您希望掩码哪些内容？例如，仅掩码 assistant 的消息、仅掩码最后一条消息，或不进行任何掩码处理。

目前存在大量 chat_template。Axolotl 支持常见的那些模板：已支持的 chat templates。例如，要使用 ChatML，可设置 chat_template: chatml。

不过，也可以通过指定 chat_template: tokenizer_default，在分词器中直接使用已配置好的模板。如果您希望有备用方案（以防某些分词器未预配置该模板），可以设置 chat_template: tokenizer_default_fallback_chatml，以便在找不到对应模板时自动回退到 ChatML 模板。

最后还有一种非常强大的方法，即自行创建模板。可通过以下方式设置：

我们目前默认使用 OpenAI 格式作为数据集键，因此如果您的数据集已采用该格式，则无需做任何修改。

如果您的数据集格式不同，以下是需要检查的键及其默认值：

在某些 chat_template 中（例如 Gemma），角色被硬编码为 user 和 assistant。因此，您可能需要对数据集中的角色进行映射，使其与上述角色对应。我们目前提供了一些适用于常见数据集的默认映射，但如果出现 KeyError，就需要为您的角色添加自定义映射。示例如下：

在上面的示例中，所有的 gpt 和 model 值都被转换为 assistant，所有 human 值则被转换为 user。

chat_template 的常见应用场景是处理聊天消息，因此通常会掩码所有非 assistant 的消息。assistant 消息指的是您希望模型学习的机器人消息。

若要使用所有 assistant 消息进行训练，需设置以下配置。

train_on_eos 配置意味着会掩码非 assistant 轮次中的所有 EOS 令牌。其他选项包括 all 和 last，用于选择要用于训练的 EOS 令牌。

也许您希望同时使用 assistant 和 narrator 角色进行训练，只需在 roles_to_train 列表中添加 narrator 即可。同时还需要在上面的角色映射表中添加该角色。

由于 chat_template 可能使用与分词器中的 EOS 不同的硬编码 EOS/EOT 令牌，因此强烈建议手动设置这些令牌。例如，ChatML 使用 <|im_end|> 来标记轮次结束。

完成以上所有步骤后，您可以将这些配置组合起来，为您的定制数据集生成专属配置。

如果将此配置应用于上面的示例数据集，输出结果如下（可通过 axolotl preprocess config.yaml --debug 查看）：

第一个数字代表标签，第二个数字代表 token_id。例如，-100 标签出现在非 assistant 部分，表示这些部分会被掩码；而在 assistant 部分，标签与 token_id 相同。

如果在预处理过程中出现大量“无法找到 content __ boundary”的警告，请查看 chat_templates 相关的常见问题解答。

详情请参阅相关文档。

指令数据集用于训练指令遵循模型，每个数据集包含一个包含指令的提示词以及一个对应的响应。与可能为多轮对话的聊天数据集不同，指令数据集通常为单轮结构。

下面是一个名为 Alpaca 的常见格式示例：

利用这些键，就可以构建相应的提示词。

其配置方式如下：

Axolotl 支持多种类型的指令数据集。所有类型及其对应的类型说明和样本行格式均可在“指令数据集文档”中找到。

由于指令格式存在多种可能性，Axolotl 允许用户在不直接修改代码的情况下自定义指令格式。

在下面的示例中，使用了一个样本行来展示 mistral_v1 格式的输出。该配置将 field_instruction 的实际名称设置为 input，而 field_input 则保持为空，因为在本示例中并无输入内容。通常而言，instruction 可以视为向模型提出的问题，input 则是补充信息，最终输出即为模型的响应。实际上，并非必须要有输入或系统支持。归根结底，最重要的是明确你希望其呈现的格式，以及如何根据具体需求对其进行定制。

参考资料：自定义指令提示格式文档。

由于存在多种具有不同数据集要求的 RLHF 方法，详情请参阅 RLHF 文档。

**示例：**

示例 1（json 格式）：
```json
{"text": "first row"}
{"text": "second row"}
...
```

示例 2（yaml 格式）：
```yaml
pretraining_dataset: hf_org/name
```

示例 3（yaml 格式）：
```yaml
pretraining_dataset:
  - path: json
    data_files:
      - A.jsonl
      - B.jsonl
      - C.jsonl
```

示例 4（yaml 格式）：
```yaml
datasets:
  - path: hf_org/name
    type: completion
```

## 指令微调

**URL:** https://docs.axolotl.ai/docs/dataset-formats/inst_tune.html

**内容：**
- 指令微调
- alpaca
- jeopardy
- oasst
- gpteacher
- reflection
- explainchoice
- concisechoice
- summarizetldr
- alpaca_chat

instruction; input（可选）

instruction; input（可选）

包含reflect指令的instruction；input（可选）

问题、选项、（答案或解释）

问题、选项、（答案或解释）

alpaca chat的基本指令格式

alpaca chat的问答对

用于获取简短答案的alpaca chat问答对

用于load_camel_ai的alpaca chat问答对

支持包含系统提示语和指令的open orca数据集

基于文章的上下文问答

另一种上下文问答方式

基于文章的上下文问答，当无法从上下文中找到答案时使用默认回复

指令与修改

instruction，添加额外的EOS标记

对于已为指令微调而预处理过的数据集：

您可以在YAML配置文件中使用此示例：

完整的配置选项请参见此处。

**示例：**

示例1（json格式）：
```json
{"instruction": "...", "input": "...", "output": "..."}
```

示例 2（JSON格式）：
```json
{"question": "...", "category": "...", "answer": "..."}
```

示例 3（JSON格式）：
```json
{"INSTRUCTION": "...", "RESPONSE": "..."}
```

示例 4（JSON格式）：
```json
{"instruction": "...", "input": "...", "response": "..."}
```

## 分步监督格式

**URL:** https://docs.axolotl.ai/docs/dataset-formats/stepwise_supervised.html

**目录:**
- 分步监督格式
- 分步监督
  - 示例

分步监督格式专为需要链式思维（COT）推理的数据集设计，此类数据集中的每个示例都包含多个完成步骤，以及针对每个步骤的偏好标签。

以下是一个简单的分步监督数据集条目示例：

**示例:**

示例 1（json格式）：
```json
{
  "prompt": "Which number is larger, 9.8 or 9.11?",
  "completions": [
    "The fractional part of 9.8 is 0.8, while the fractional part of 9.11 is 0.11.",
    "Since 0.11 is greater than 0.8, the number 9.11 is larger than 9.8."
  ],
  "labels": [true, false]
}
```

---
Hermes Agent的技术文档、CLI使用指南、智能体功能、插件、服务提供商相关内容以及开发者指南。
