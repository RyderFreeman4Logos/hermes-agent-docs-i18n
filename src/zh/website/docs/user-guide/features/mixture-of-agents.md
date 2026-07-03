---
sidebar_position: 7
title: "Mixture of Agents"
description: "Create named MoA presets that appear as selectable models under the Mixture of Agents provider"
---

# 多智能体混合模型

多智能体混合模型是一种虚拟模型提供方。每个已命名的MoA预设都会作为`moa`提供方下的可选模型呈现。

当选中某个MoA预设后，该预设中的聚合器将成为实际运行的模型，负责生成助手回复并发起工具调用。参考模型会先被运行，为聚合器提供分析结果以供其使用。

当某个复杂任务需要从多个模型的视角进行分析，但又仍需保留Hermes传统的智能体工作流程——包括工具调用、后续迭代、中断处理、对话记录持久化以及与其他消息相同的会话上下文时，可使用多智能体混合模型。

## 选择MoA预设作为您的模型

您可以通过常规的模型选择界面来挑选所需的预设：

```bash
/model default --provider moa
/model review --provider moa
```

由于 MoA 是模型系统中的常规提供者，因此**所有 Hermes 界面**都支持选择 MoA 预设：

- **CLI / gateway / TUI 的 `/model` 命令** —— 可使用 `/model <preset> --provider moa` 指定预设，若使用默认预设则可直接输入 `/model --provider moa`。当预设名称与已配置的预设完全一致时，仅输入 `/model <preset>` 也可生效。
- **`hermes model` 命令**以及**控制面板中的模型选择器** —— 会显示一行“多智能体混合”提供者选项，其中列出了各预设名称对应的模型。
- **桌面 GUI 应用** —— 模型下拉菜单中会设有“MoA 预设”板块；选中某个预设（如“MoA: <preset>”）即可将当前激活模型切换为该预设。桌面设置面板还可用于创建和编辑预设。

因此，只要是在可以选择其他模型的地方，就能看到已配置的预设选项。

## 斜杠命令快捷方式

`/moa` 是一个便捷的一键命令。它会使用**默认**的 MoA 预设处理当前输入的提示词，处理完成后会自动恢复到你之前的模型状态。

```bash
/moa design and implement a migration plan for this flaky test cluster
```

在那一轮中，Hermes会暂时切换为默认的MoA预设来处理请求，发送完提示词后便会恢复到你之前使用的模型。整个流程的核心就是该提示词——此时`/moa`指令已不再将其视为预设名称。

```bash
/moa
```

直接输入 `/moa`（不附带提示语）仅会显示使用说明。

若要在当前会话的剩余时间内**切换**到某种 MoA 预设，可从模型选择器中挑选对应预设——所有模型选择界面中的“混合智能体”提供者下都会列出这些预设（见上文）。刻意将 `/moa` 设计为非模型切换指令，因此普通提示语绝不会意外改变所使用的模型。

## 在智能体循环中的工作原理

每当选择 `moa` 作为提供者并调用主模型时，Hermes 会执行以下操作：

1. 按名称查找选定的预设；
2. 运行已配置的参考模型，但不传递工具结构信息（这些模型仅接收对话中的用户/助手文本，而不会收到 Hermes 系统提示语或工具调用记录），从而确保参考模型的调用成本较低，且不会因严格的要求而被拒绝）；
3. 将参考模型的输出作为私有上下文附加到聚合器中；
4. 使用标准的 Hermes 工具结构信息调用已配置的聚合器；
5. 将聚合器的响应视为真正的模型响应；
6. 如果聚合器需要调用工具，Hermes 会正常执行这些工具；
7. 在下一次模型迭代时，会基于更新后的对话内容再次运行相同的 MoA 处理流程，其中已包含工具的调用结果。

由于 MoA 是通过常规模型系统选择的，因此它可以自动与 `/goal`、网关会话、TUI 会话以及桌面端聊天功能协同工作。

## 配置预设

您可以通过以下方式配置带名称的 MoA 预设：

- 仪表板 → 模型 → 模型设置 → 混合智能体
- 桌面应用 → 设置 → 模型 → 混合智能体
- `hermes moa configure [name]`
- `config.yaml`

配置文件中存储了明确的提供者/模型对应关系，因此您可以混合使用不同的提供者，或从同一提供者中选用多个模型：

```yaml
moa:
  default_preset: default
  presets:
    default:
      reference_models:
        - provider: openai-codex
          model: gpt-5.5
        - provider: openrouter
          model: deepseek/deepseek-v4-pro
      aggregator:
        provider: openrouter
        model: anthropic/claude-opus-4.8
      # Optional: pin sampling temperatures. When omitted (the default),
      # temperature is NOT sent and each model uses its provider default —
      # the same behavior as a single-model Hermes agent.
      # reference_temperature: 0.6
      # aggregator_temperature: 0.4
      max_tokens: 4096
      enabled: true
```

默认预设：

- 参考模型：`openai-codex:gpt-5.5`
- 参考模型：`openrouter:deepseek/deepseek-v4-pro`
- 聚合/执行模型：`openrouter:anthropic/claude-opus-4.8`

### 使用 `reference_max_tokens` 调整建议生成速度

在每轮对话中，MoA 会并行运行参考模型（即建议生成器），随后再由聚合模型进行处理。建议生成是导致单轮延迟的主要因素——每轮的耗时与建议生成器输出的token数量密切相关，因为系统需要等待最慢的那个建议生成器完成输出。默认情况下，建议生成器的输出没有限制（即未设置 `reference_max_tokens`），因此它们可能会生成冗长、类似文章长度的建议。

可以通过为预设设置 `reference_max_tokens` 来限制建议生成器的输出长度，从而获得更为简练的建议。由于聚合模型只需了解每个建议生成器的核心观点，设定一个上限（例如 `600`）即可显著缩短单轮耗时，且对建议质量的影响极小。该参数仅限制**建议生成器**的输出，而用户可见的最终答案——即聚合模型的输出，则不会受到任何限制。

```yaml
moa:
  presets:
    fast:
      reference_models:
        - provider: openrouter
          model: anthropic/claude-opus-4.8
        - provider: openrouter
          model: openai/gpt-5.5
      aggregator:
        provider: openrouter
        model: anthropic/claude-opus-4.8
      reference_max_tokens: 600   # concise advice → faster turns
```

如需保持原有的无上限运行模式，可将其保留为空值（或 `0`/空白）。 

## 终端预设管理

```bash
hermes moa list
hermes moa configure              # update the default preset
hermes moa configure review       # create or update a named preset
hermes moa delete review
```

## 性能基准测试

在HermesBench的测试中，采用双模型模块化架构的预设——即以`gpt-5.5`作为参考模型并整合其能力的`claude-opus-4.8`——其测试得分远高于单独运行任一模型时的成绩：

| 模型 | HermesBench得分 |
|---|---|
| **Opus整合模型（opus-4.8 + gpt-5.5参考模型）——模块化架构** | **0.8202** |
| `anthropic/claude-opus-4.8` | 0.7607 |
| `openai/gpt-5.5` | 0.7412 |

该模块化架构的得分比其中最强大的单个组件（opus-4.8）高出约6分，这充分证明了在复杂任务中，整合多种模型视角确实能提升性能，而不仅仅是简单地对两种模型的输出求平均。

## 提示词缓存机制

模块化架构的设计确保**主对话的提示词缓存始终不会被破坏**。选择某种模块化预设就如同选择普通模型一样：它不会修改之前的对话上下文，也不会更换工具集或在中途重新生成系统提示词。用户的对话历史、系统提示词以及工具结构都会保持完整不变，因此其他模型所依赖的缓存前缀内容也会与使用普通模型时完全一致。切换到或从模块化预设切换回来时，所需的缓存失效操作与其他通过`/model`指令切换模型时的操作量相同——没有更多额外开销。

两种类型的内部调用都能正常进行缓存：
- **参考模型**会接收到经过筛选的、结构固定的对话内容（系统提示词和工具相关内容已被移除，详见上文说明）。由于这些内容是基于稳定的对话历史生成的，因此参考模型的提示词前缀在多次迭代中保持不变，从而能够正常缓存。这类调用属于简短的咨询性质，不涉及任何工具使用。
- **整合模型**则是实际执行任务的主体。它会将参考模型的输出作为私有指导信息附加到最新用户消息的**末尾**。由于这些内容位于整个稳定前缀（系统提示词+之前的对话历史）之后，因此不会导致任何缓存前缀失效：整合模型可以正常获取前面所有内容的缓存结果，只有新附加的尾部内容才是新鲜的。这其实与普通对话的处理方式完全相同——每条新的用户消息也都属于未缓存的尾部内容。

由此可见，模块化架构并未牺牲任何一种调用类型的提示词缓存功能。它唯一的实际成本在于每次迭代都需要额外的参考模型调用次数——你为的是获得多种模型的视角，而非承担缓存失效带来的代价。同时，该架构与Hermes系统的其他部分共享的长期对话前缀也完好无损。

## 备注事项

- 模块化架构已不再列在`hermes tools`目录下，也不需要再启用名为`moa`的工具集。
- 若为某个预设设置`enabled: false`，则该预设的参考模型调用功能将被禁用：此时整合模型将独立工作，效果就如同直接选择了该普通模型一样。这正是控制面板和桌面设置中提供的针对单个预设的开关功能。
- 一个预设的整合模型不能是另一个模块化架构预设。系统刻意禁止了递归式的模块化架构结构。
- 若某个参考模型出现身份验证失败，也不会导致当前对话中断。Hermes会将该失败信息纳入参考上下文中，然后继续使用其他正常响应的模型来处理对话。
- 模块化架构会增加模型调用次数。一次模型迭代可能涉及多次参考模型调用以及一次整合模型调用。
