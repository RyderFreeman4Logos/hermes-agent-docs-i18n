---
sidebar_position: 7
title: "Mixture of Agents"
description: "Create named MoA presets that appear as selectable models under the Mixture of Agents provider"
---

# 多智能体混合模型

多智能体混合模型是一种虚拟模型提供方。每个已命名的MoA预设都会作为`moa`提供方下的可选模型呈现。

当您选择某个MoA预设时，该预设中的聚合器即为实际运行的模型。它负责生成助手的回复并发起工具调用。参考模型会首先运行，为聚合器提供分析结果以供其使用。

当某项复杂任务能够从多种模型的视角中受益，但同时仍需要保留Hermes标准的智能体工作流程——包括工具调用、后续迭代、中断处理、对话记录持久化以及与其他消息相同的会话上下文时，可使用多智能体混合模型。

## 选择MoA预设作为您的模型

您可以通过常规的模型选择界面来挑选所需的预设：

```bash
/model default --provider moa
/model review --provider moa
```

由于 MoA 是模型系统中的普通提供者，因此**所有 Hermes 界面**都支持选择 MoA 预设：

- **CLI / gateway / TUI 的 `/model` 命令** —— 可使用 `/model <preset> --provider moa` 指定预设，若使用默认预设则可直接输入 `/model --provider moa`。当预设名称与已配置的预设完全一致时，仅输入 `/model <preset>` 也能生效。
- **`hermes model` 命令**以及**控制面板中的模型选择器** —— 会显示一个“Agent 混合体”提供者选项行，其中列出了各预设名称对应的模型。
- **桌面 GUI 应用** —— 模型下拉菜单中会设有“MoA 预设”板块；选中某个预设（如 `MoA: <preset>`）即可将当前活动模型切换为该预设。桌面设置面板还可用于创建和编辑预设。

因此，只要是在可选择其他模型的地方，都能看到已配置的预设。

## 斜杠命令快捷方式

`/moa` 是一个便捷的一键命令。它会通过**默认**的 MoA 预设处理当前提示词，处理完成后会恢复到你之前的模型状态：

```bash
/moa design and implement a migration plan for this flaky test cluster
```

在那一轮中，Hermes会暂时切换为默认的MoA预设来处理请求，发送完提示词后会立即恢复到你之前使用的模型。整个流程的核心就是该提示词——此时`/moa`指令已不再将其视为预设名称。

```bash
/moa
```

直接输入 `/moa`（不输入提示语）仅会显示使用说明。

若要在当前会话的剩余时间内**切换**到某种 MoA 预设，可从模型选择器中挑选该预设——所有模型选择界面中的“混合智能体”提供者下方都会显示这些预设（见上文）。刻意将 `/moa` 设计为非模型切换指令，因此普通提示语绝不会意外改变所使用的模型。

## 在智能体循环中的工作原理

每当选择 `moa` 作为提供者并调用主模型时，Hermes 会执行以下步骤：

1. 根据名称查找选定的预设；
2. 运行已配置的参考模型，且不附带工具架构（这些模型仅接收对话中的用户/助手文本，而非 Hermes 系统提示语或工具调用记录），从而降低运行成本并避免因严格遵循提供者规则而导致的拒绝）；
3. 将参考模型的输出作为私有上下文附加到聚合器中；
4. 使用标准的 Hermes 工具架构调用已配置的聚合器；
5. 将聚合器的响应视为真正的模型响应；
6. 如果聚合器需要调用工具，Hermes 会正常执行这些工具；
7. 在下一次模型迭代时，会基于更新后的对话内容再次运行相同的 MoA 处理流程，包括工具的运行结果。

由于 MoA 是通过常规模型系统选择的，因此它能自动与 `/goal`、网关会话、TUI 会话以及桌面端聊天功能协同工作。

## 配置预设

您可以通过以下方式配置命名的 MoA 预设：

- 仪表板 → 模型 → 模型设置 → 混合智能体
- 桌面应用 → 设置 → 模型 → 混合智能体
- `hermes moa configure [名称]`
- `config.yaml`
配置文件中存储了明确的提供者与模型对应关系，因此你可以混合使用不同的提供者，并从同一个提供者处调用多个模型。

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

      enabled: true
```

默认预设：

- 参考模型：`openai-codex:gpt-5.5`
- 参考模型：`openrouter:deepseek/deepseek-v4-pro`
- 聚合/执行模型：`openrouter:anthropic/claude-opus-4.8`

### 顾问输出机制

MoA采用由提供商设定的输出限制。系统不再支持预设的或针对每个对话槽位的输出Token上限设置。不同提供商的默认值各不相同，未明确指定数值并不一定代表模型的最大输出限制。那些需要设置输出限制的原生协议会从Hermes获取内部设定的数值。

### 使用`fanout`时的顾问运行频率

默认情况下，顾问会在**每个用户轮次中运行一次**（`fanout: user_turn`）——即在轮次的第一个消息中生成计划层面的建议，之后则由执行聚合器独立处理该轮次剩余的工具调用。这是成本最低的运行模式，因为顾问的处理成本不会随单次轮次中的工具调用次数而增加。还有两种替代运行模式，它们在成本与建议新鲜度之间进行权衡：

- `fanout: per_iteration` — 顾问会在**每次工具调用迭代**时都重新运行，因此其给出的建议始终能反映最新的工具处理结果——但代价是会使顾问的延迟及计算开销随单次轮次中的工具调用次数成倍增加。  
- `fanout: every_n:3` — 这是一种折中方案：顾问会在每个用户轮次的**第一次**迭代以及之后的每**第3次**工具调用迭代时运行。中间的迭代则会复用上一次顾问运行时生成的缓存建议，这样聚合器仍能在每一步获得建议——只不过建议是每隔N步更新一次，而非每步都更新。计数器会在每个新的用户消息到达时重置，因此每个轮次都会从最新的建议开始。`fanout: {mode: every_n, n: 3}` 这种映射格式也被接受，且会自动转换为字符串格式。

```yaml
moa:
  presets:
    fresh:
      reference_models:
        - provider: openrouter
          model: anthropic/claude-opus-4.8
      aggregator:
        provider: openrouter
        model: openai/gpt-5.5
      fanout: per_iteration   # advisors refresh on every tool iteration
```

当遇到未知或格式错误的值时，系统将回退至 `user_turn` 模式。

:::注意：默认设置的变化
在2026年7月之前，默认的更新频率为 `per_iteration`。如今，其默认值为 `user_turn`——这是一种成本最低、影响最小的更新频率——除非针对特定模式的测试结果表明需要采用更高成本的默认设置。那些希望实现每步提示功能的预设会明确将 `fanout` 设置为 `per_iteration`。
:::

### 辅助系统输出的内容隐私过滤机制

辅助系统的输出可能会将对话中的敏感数据——如电子邮件、格式化的电话号码、API密钥、JWT令牌等——泄露到界面中显示的参考信息块、保存的MoA跟踪记录以及聚合提示中。`moa.privacy_filter`（默认为关闭状态）可用来屏蔽这些敏感信息的暴露。

```yaml
moa:
  privacy_filter: display   # or: full
```

- `display` — 仅遮蔽**用户可见的内容**：即 UI 中显示的带标签的参考内容，以及通过 `save_traces` 写入的记录。聚合器仍会收到原始的顾问文本，因此答案质量不会受到影响。
- `full` — 此外还会遮蔽注入到聚合器提示语中的顾问文本（以及单次请求的 `/moa` 合成输入）。

凭证信息（API密钥前缀、JWT、私钥、数据库连接字符串等）会由 Hermes 的集中式机密遮蔽工具进行处理；而 MoA 过滤器则会进一步对电子邮件和格式规范的电话号码进行遮蔽。针对代码审查类建议，相关匹配规则被设定得较为保守：连续的数字序列、行号、时间戳、Git SHA 值以及 IP 地址均不会被处理——仅会匹配如 `(555) 123-4567` 或 `555-123-4567` 这类有分隔符的电话号码格式。

### 每个槽位的推理强度设置

参考内容槽位和聚合器槽位也可设置 `reasoning_effort` 参数。当您希望同一模型以不同深度参与推理，或要求聚合器比参考建议进行更深入的思考时，可使用此参数。其有效值与 Hermes 的常规推理控制选项一致：`none`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max` 和 `ultra`。

```yaml
moa:
  presets:
    deep_review:
      reference_models:
        - provider: openai-codex
          model: gpt-5.6-sol
          reasoning_effort: low
        - provider: openai-codex
          model: gpt-5.6-sol
          reasoning_effort: xhigh
        - provider: xai-oauth
          model: grok-4.5
      aggregator:
        provider: openai-codex
        model: gpt-5.6-sol
        reasoning_effort: high
```

若要使用该参数对应的提供者或Hermes默认值，可省略`reasoning_effort`字段。

## 终端预设管理

```bash
hermes moa list
hermes moa configure              # update the default preset
hermes moa configure review       # create or update a named preset
hermes moa delete review
```

## 性能基准测试

在HermesBench上的测试中，采用双模型MoA架构的预设——即以`gpt-5.5`作为参考模型并对`claude-opus-4.8`进行整合——其测试得分远高于单独运行任一模型时的成绩：

| 模型 | HermesBench得分 |
|---|---|
| **Opus整合模型（opus-4.8 + gpt-5.5参考模型）— MoA架构** | **0.8202** |
| `anthropic/claude-opus-4.8` | 0.7607 |
| `openai/gpt-5.5` | 0.7412 |

该MoA架构的得分比其中表现最佳的组件（opus-4.8）高出约6分，这证明了在复杂任务中，整合多种模型视角确实能提升性能，而不仅仅是简单地对两种模型的输出求平均。

## 提示词缓存机制

MoA架构的设计确保**主对话的提示词缓存始终不会被破坏**。选择MoA预设就如同选择普通模型一样：它不会修改历史对话内容、更换工具集，也不会在对话进行过程中重新生成系统提示词。用户的对话历史、系统提示词以及工具结构都会保持完整不变，因此其他模型所依赖的缓存内容也能与使用普通模型时完全一致地被保留下来。切换到或从MoA预设切换回来时，所需的缓存失效操作与其他任何 `/model` 切换操作相同——没有更多额外操作。

所有类型的内部调用都能正常进行缓存。

- **参考模型**会接收经过筛选的、结构固定的对话视图（系统提示和工具响应内容已被移除——详见上文循环说明）。由于该视图是由稳定的对话历史决定的，因此参考模型的提示前缀在多次迭代中保持一致，也能正常被缓存。这类参考调用属于简短的咨询性质，不涉及任何工具的使用。
- **聚合模型**则是实际执行任务的模型。参考模型的输出会被附加到最新用户消息的*末尾*，作为私有指导信息。由于这些内容位于整个稳定前缀（系统提示+历史对话）的尾部，因此不会导致任何已缓存的前缀失效：聚合模型能够命中注入内容之前的所有缓存数据，只有新追加的尾部内容是新鲜的。这正是普通对话的处理方式——每条新的用户消息同样属于未缓存的尾部内容。

由此可见，MoA架构在两种调用类型中均未牺牲提示词缓存机制。其唯一的实际成本在于每次迭代需要额外的参考调用——您支付的是多种模型视角带来的收益，而非因缓存失效造成的损失。与Hermes其他组件共享的长期对话前缀则依然保持完整无损。

## 备注

- MoA 已不再列在 `hermes tools` 下，也不再提供可启用的 `moa` 工具集。  
- 若为某个预设设置 `enabled: false`，则该预设的引用扩展功能将被禁用：此时聚合器将独立运行，其行为就如同将该预设视为普通模型一样。这正是控制面板及桌面设置中所显示的针对单个预设的开关功能。  
- 预设的聚合器不能是另一个 MoA 预设。系统刻意禁止了递归的 MoA 树结构。  
- 若某个参考模型出现凭证验证失败，也不会导致当前轮次中断。Hermes 会将该错误信息纳入参考上下文中，并继续使用其他可用的模型进行处理。  
- MoA 会增加模型调用次数。单次模型迭代可能涉及多次引用调用以及一次聚合器调用。
