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

控制面板、TUI以及桌面模型选择器中也会显示“混合智能体”提供者这一行。其对应的模型即为您所配置的预设名称。

## 斜杠命令快捷键

`/moa` 是针对模型选择的便捷命令形式：

```bash
/moa
```

将当前会话切换为默认的 MoA 预设。

```bash
/moa review
```

如果 `review` 与预置名称完全匹配，则会将当前会话切换至提供商 `moa` 和模型 `review`。

```bash
/moa design and implement a migration plan for this flaky test cluster
```

如果输入文本与预设名称并不完全匹配，Hermes会将其视为一次性提示。此时它会暂时切换到该轮对话的默认MoA预设来处理提示，发送完成后再恢复之前的模型设置。

预设匹配采用严格匹配机制。Hermes不会对预设名称进行模糊匹配，因此普通提示不会意外导致模型切换。

## 在智能体循环中的工作流程

当选择`moa`作为提供者时，对于每次主模型调用，Hermes会执行以下操作：

1. 根据名称查找选定的预设；
2. 运行已配置的参考模型，且不包含工具结构体（这些模型仅接收对话中的用户/助手文本，而非Hermes系统提示或工具调用记录），从而降低处理成本并避免因严格匹配规则而被提供者拒绝；
3. 将参考模型的输出作为私有上下文传递给聚合器；
4. 使用标准的Hermes工具结构体调用已配置的聚合器；
5. 将聚合器的响应视为真正的模型响应；
6. 如果聚合器需要调用工具，Hermes会正常执行这些工具；
7. 在下一次模型迭代中，系统会基于更新后的对话内容再次运行相同的MoA处理流程，包括工具的返回结果。

由于MoA是通过常规模型系统选择的，因此它可以自动与`/goal`、网关会话、TUI会话以及桌面端聊天功能集成使用。

## 配置预设

您可以通过以下方式配置带名称的MoA预设：

- 仪表板 → 模型 → 模型设置 → 智能体混合模式
- 桌面应用 → 设置 → 模型 → 智能体混合模式
- `hermes moa configure [名称]`
- `config.yaml` 文件

配置文件中会存储明确的提供者/模型对应关系，因此您可以混合使用不同的提供者，或从同一提供者处选择多个模型：

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
      reference_temperature: 0.6
      aggregator_temperature: 0.4
      max_tokens: 4096
      enabled: true
```

默认预设：

- 参考模型：`openai-codex:gpt-5.5`
- 参考模型：`openrouter:deepseek/deepseek-v4-pro`
- 聚合模型/执行模型：`openrouter:anthropic/claude-opus-4.8`

## 终端预设管理

```bash
hermes moa list
hermes moa configure              # update the default preset
hermes moa configure review       # create or update a named preset
hermes moa delete review
```

## 备注

- MoA 已不再列在 `hermes tools` 下，也没有可供启用的 `moa` 工具集。
- 若为某个预设设置 `enabled: false`，则该预设的引用扩展功能将被禁用：此时聚合器将独立工作，其行为就如同将该预设视为普通模型一样。这正是控制面板及桌面设置中所显示的针对单个预设的开关功能。
- 预设的聚合器不能是另一个 MoA 预设。系统会刻意阻止递归的 MoA 树结构。
- 若某个参考模型出现凭证验证失败，也不会导致当前轮次中断。Hermes 会将该错误信息纳入参考上下文中，并继续使用其他可用的模型进行处理。
- 使用 MoA 会增加模型调用次数。单次模型迭代可能涉及多次引用调用以及一次聚合器调用。
