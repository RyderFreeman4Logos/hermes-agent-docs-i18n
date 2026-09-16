---
title: Provider Routing
description: Configure OpenRouter provider preferences to optimize for cost, speed, or quality.
sidebar_label: Provider Routing
sidebar_position: 7
---

# 提供商路由功能

当您将 [OpenRouter](https://openrouter.ai) 作为LLM提供商时，Hermes Agent支持**提供商路由功能**——可实现对处理请求的底层AI提供商进行精细控制，并设定相应的优先级。

OpenRouter会将请求分发至多个提供商（例如Anthropic、Google、AWS Bedrock、Together AI等）。通过提供商路由功能，您可以根据成本、速度、质量等需求进行优化，或强制指定使用特定的提供商。

:::note
[Nous Portal](/integrations/nous-portal)会按模型统一决定请求的路由路径，不接受用户指定的提供商偏好；由于Hermes从未向Portal发送`provider`对象，因此该处的`provider_routing`功能会被直接忽略。
:::

## 配置方法

在您的`~/.hermes/config.yaml`文件中添加`provider_routing`部分即可：

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
提供者路由功能仅在使用 OpenRouter 时生效。对于 Nous Portal 或直接连接提供者的方式（例如直接调用 Anthropic API），该功能不会产生任何影响。  
:::

## 选项

### `sort`

用于控制 OpenRouter 如何为你的请求对可用提供者进行排序。

| 值 | 描述 |
|-------|-------------|
| `"price"` | 按价格从低到高排序 |
| `"throughput"` | 按每秒处理令牌数从高到低排序 |
| `"latency"` | 按首次获取令牌的时间从短到长排序 |

```yaml
provider_routing:
  sort: "price"
```

### `only`

提供商标识符的白名单。一旦设置此参数，系统将**仅**使用列在白名单中的提供商，其余所有提供商均会被排除。请使用 OpenRouter 显示的每个提供商的小写标识符。

```yaml
provider_routing:
  only:
    - "anthropic"
    - "google"
```

### `ignore`

提供商名称的黑名单。即使这些提供商的方案价格最低或速度最快，也**绝不会**被使用。

```yaml
provider_routing:
  ignore:
    - "together"
    - "deepinfra"
```

### `order`

明确的优先级顺序。首先列出的提供方将优先被选用，未列出的提供方则作为备用选项使用。

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

用于控制提供商是否可以使用您的提示语进行模型训练。可选值为 `"allow"`（允许）或 `"deny"`（拒绝）。

```yaml
provider_routing:
  data_collection: "deny"
```

### 每个模型的自定义设置（`models`）

可为每个模型指定不同的提供者集合。`models` 下的键为模型编号；每个条目均使用相同的 `sort` / `only` / `ignore` / `order` / `require_parameters` / `data_collection` 键，但仅会覆盖该模型的默认值。未针对特定模型进行设置的选项将沿用统一的默认设置。

```yaml
provider_routing:
  sort: "price"                      # applies to every model
  models:
    "openai/gpt-6-astra":
      only: ["openai"]               # never let a reseller serve this one
    "anthropic/claude-fable-5.1":
      only: ["anthropic"]
    "moonshotai/kimi-k2.6":
      order: ["moonshotai", "together"]
      sort: "throughput"
```

匹配功能对拼写具有容错性，例如 `agent.reasoning_overrides`（`claude-fable-5.1` / `claude-fable-5-1`，无论是否带有 `openrouter/` 前缀均可）。该覆盖设置会跟随智能体*当前*所使用的模型，因此 `/model` 切换、备用模型激活、定时任务以及切换到其他模型的委托子智能体，都会拥有各自的配置项。如需直接编辑这些键值，请修改 `config.yaml` 文件：由于模型编号中包含点号，`hermes config set` 会将其视为路径分隔符。

## 实际应用示例

### 优化成本

将请求路由至最便宜的可用服务提供商。非常适合高频率使用场景及开发测试。

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

### 优化吞吐量性能

非常适合对每秒生成Token数量有较高要求的长时间内容生成场景：

```yaml
provider_routing:
  sort: "throughput"
```

### 固定使用特定 Provider

为确保一致性，需让所有请求都通过指定的 Provider 处理：

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

### 带有备用方案的优先顺序

首先尝试您首选的提供方，若无法使用则再转而使用其他提供方：

```yaml
provider_routing:
  order:
    - "anthropic"
    - "google"
  require_parameters: true
```

## 工作原理

在代理的聊天请求以及迭代次数汇总信息中，提供程序路由偏好会通过 `extra_body.provider` 字段传递给 OpenRouter。（`extra_body` 是 OpenAI Python SDK 的参数，在 JSON 请求中会作为顶层的 `provider` 对象出现。）诸如压缩和标题生成之类的辅助任务，则会在 `auxiliary.<task>.extra_body` 下单独进行配置。

- **CLI 模式** — 在 `~/.hermes/config.yaml` 中进行配置，系统启动时加载
- **Gateway 模式** — 使用相同的配置文件，当网关启动时加载

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
您可以同时组合多个选项。例如，按价格排序，同时排除特定的服务提供商，并要求相关参数必须支持：

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
供应商路由用于决定由 OpenRouter 后端的哪些**子提供商**来处理您的请求。若希望在主服务出现故障时自动切换到完全不同的提供商，请参阅[回退提供商](/user-guide/features/fallback-providers)。
:::
