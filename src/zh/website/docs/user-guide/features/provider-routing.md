---
title: Provider Routing
description: Configure OpenRouter or Nous Portal provider preferences to optimize for cost, speed, or quality.
sidebar_label: Provider Routing
sidebar_position: 7
---

# 提供商路由功能

当您将 [OpenRouter](https://openrouter.ai) 或 [Nous Portal](/integrations/nous-portal) 作为 LLM 提供商时，Hermes Agent 支持**提供商路由功能**——可实现对处理请求的底层 AI 提供商进行精细控制，并设定相应的优先级。

OpenRouter 会将请求分发至多个提供商（例如 Anthropic、Google、AWS Bedrock、Together AI）。通过提供商路由功能，您可以根据成本、速度或质量需求进行优化，或强制指定使用特定的提供商。

:::提示
通过 Nous Portal 转发的请求也会遵循相同的提供商偏好设置——此外，Portal 的订阅用户在使用按令牌计费的提供商时还能享受 10% 的折扣。
:::

## 配置方法

在您的 `~/.hermes/config.yaml` 文件中添加 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "price"           # How to rank providers
  only: []                # Whitelist: only use these providers
  ignore: []              # Blacklist: never use these providers
  order: []               # Explicit provider priority order
  require_parameters: false  # Only use providers that support all parameters
  data_collection: null   # Control data collection ("allow" or "deny")
```

:::info  
提供方路由功能仅在使用 OpenRouter 或 Nous Portal 时生效。对于直接连接提供方的场景（例如直接调用 Anthropic API），该功能则不起作用。  
:::

## 选项

### `sort`

用于控制 OpenRouter 如何为你的请求对可用提供方进行排序。

| 值 | 描述 |
|-------|-------------|
| `"price"` | 按价格从低到高排序 |
| `"throughput"` | 按每秒处理速度从快到快排序 |
| `"latency"` | 按首次响应时间从短到短排序 |

```yaml
provider_routing:
  sort: "price"
```

### `only`

提供商标识符的白名单。设置该参数后，**仅**会使用列在白名单中的提供商，其余所有提供商均会被排除。请使用 OpenRouter 显示的每个提供商的小写标识符。

```yaml
provider_routing:
  only:
    - "anthropic"
    - "google"
```

### `ignore`

提供商名称的黑名单。即便这些提供商能给出最便宜或最快的服务选项，也**绝不会**被使用。

```yaml
provider_routing:
  ignore:
    - "together"
    - "deepinfra"
```

### `order`

明确的优先级顺序。首先列出的提供方将被优先选用，未列出的提供方则作为备用选项使用。

```yaml
provider_routing:
  order:
    - "anthropic"
    - "google"
    - "amazon-bedrock"
```

### `require_parameters`

当该参数设置为 `true` 时，OpenRouter 仅会将请求路由至那些能够支持您请求中**所有**参数（如 `temperature`、`top_p`、`tools` 等）的提供方。这样即可避免出现参数被隐式省略的情况。

```yaml
provider_routing:
  require_parameters: true
```

### `data_collection`

用于控制提供商是否可以使用您的提示语进行模型训练。可选值为 `"allow"` 或 `"deny"`。

```yaml
provider_routing:
  data_collection: "deny"
```

## 实际应用示例

### 优化成本

将请求路由至价格最低的可用服务提供商。非常适合高流量使用场景及开发测试环境：

```yaml
provider_routing:
  sort: "price"
```

### 优化速度表现

在交互式使用场景中，优先选择低延迟的提供者：

```yaml
provider_routing:
  sort: "latency"
```

### 优化吞吐量表现

非常适合对每秒生成token数有较高要求的长文本生成场景：

```yaml
provider_routing:
  sort: "throughput"
```

### 固定使用特定提供商

为确保一致性，需让所有请求均通过指定的提供商处理：

```yaml
provider_routing:
  only:
    - "anthropic"
```

### 避免使用特定提供方

排除您不想使用的提供方（例如出于数据隐私考虑）：

```yaml
provider_routing:
  ignore:
    - "together"
    - "lepton"
  data_collection: "deny"
```

### 优先顺序与备用方案

首先尝试您首选的提供方，若无法使用则再切换至其他提供方：

```yaml
provider_routing:
  order:
    - "anthropic"
    - "google"
  require_parameters: true
```

## 工作原理

在代理的聊天请求及迭代次数统计信息中，提供程序路由偏好会通过 `extra_body.provider` 字段传递给 OpenRouter 或 Nous Portal。（`extra_body` 是 OpenAI Python SDK 的参数，在 JSON 请求中会作为顶层的 `provider` 对象出现。）诸如压缩和标题生成之类的辅助任务，则通过 `auxiliary.<task>.extra_body` 进行独立配置。

- **CLI 模式** — 在 `~/.hermes/config.yaml` 中进行配置，系统启动时加载
- **Gateway 模式** — 使用相同的配置文件，在网关启动时加载

路由配置会从 `config.yaml` 中读取，并在创建 `AIAgent` 对象时作为参数传递。

```
providers_allowed  ← from provider_routing.only
providers_ignored  ← from provider_routing.ignore
providers_order    ← from provider_routing.order
provider_sort      ← from provider_routing.sort
provider_require_parameters ← from provider_routing.require_parameters
provider_data_collection    ← from provider_routing.data_collection
```

:::提示  
您可以同时组合多个选项。例如，按价格排序，同时排除某些提供商，并要求特定的参数支持：

```yaml
provider_routing:
  sort: "price"
  ignore: ["together"]
  require_parameters: true
  data_collection: "deny"
```
:::

## 默认行为

在未配置 `provider_routing` 部分时（即默认情况），聚合器会使用其内置的默认路由逻辑，该逻辑通常能够自动在成本与可用性之间实现平衡。

:::提示 提供商路由与回退机制的区别
供应商路由用于决定由 **OpenRouter 或 Nous Portal 后端的哪些子提供商** 来处理您的请求。若希望在主服务发生故障时自动切换到完全不同的提供商，请参阅[回退提供商](/user-guide/features/fallback-providers)。
:::
