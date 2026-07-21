---
sidebar_position: 11
title: Model Catalog
description: Remotely-hosted manifest driving curated model picker lists for OpenRouter and Nous Portal.
---

# 模型目录

Hermes 会从文档站点旁置的 JSON 配置文件中获取 **OpenRouter** 和 **Nous Portal** 的精选模型列表。这样一来，维护人员无需发布新的 `hermes-agent` 版本，即可更新模型选择列表。

当该配置文件无法访问时（如处于离线状态、网络被屏蔽或托管服务出现故障），Hermes 会自动回退到随 CLI 一同提供的仓库内快照。配置文件的异常不会影响模型选择功能——在最坏情况下，用户看到的仍将是其安装版本中自带的模型列表。

## 实时配置文件地址

```
https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
```

该文档会通过现有的 `deploy-site.yml` GitHub Pages 流水线，在每次合并到 `main` 分支时自动发布。其权威版本存储在仓库中的 `website/static/api/model-catalog.json` 文件中。

## 结构说明

```json
{
  "version": 1,
  "updated_at": "2026-04-25T22:00:00Z",
  "metadata": {},
  "providers": {
    "openrouter": {
      "metadata": {},
      "models": [
        {"id": "z-ai/glm-5.2",         "description": "default", "default": true},
        {"id": "moonshotai/kimi-k3",   "description": "recommended", "metadata": {}},
        {"id": "openai/gpt-5.4",       "description": ""}
      ]
    },
    "nous": {
      "metadata": {},
      "models": [
        {"id": "z-ai/glm-5.2", "default": true},
        {"id": "anthropic/claude-opus-4.7"},
        {"id": "moonshotai/kimi-k3"}
      ]
    }
  }
}
```

字段说明：

- **`version`** — 整数类型的架构版本号。后续架构更新时会提升此版本；Hermes 会拒绝解析其不认识的版本号，转而使用硬编码的快照版本。
- **`metadata`** — 位于清单、提供方及模型层面的结构化字典，支持任意键值对。Hermes 会忽略未知字段，因此您无需协调架构变更即可添加注释（如 `"tier": "paid"`、`"tags": [...]` 等）。
- **`description`** — 仅适用于 OpenRouter。该字段用于确定选择器标签的显示文本（如 `"recommended"`、`"free"`、`"default"` 或留空）。Nous Portal 不使用此字段——免费套餐的判定是通过 Portal 的定价接口实时完成的。
- **`default`** — 每个提供方最多只能有一个条目设置为 `"default": true"`。该模型即为**默认默选模型**：当用户未选择任何模型时，Hermes 会自动选用它（如 GUI 入门确认界面、未指定模型的提供方配置、`model.default` 为空的情况）。该模型在运行时仅通过只读缓存读取（通过 `get_default_model_from_cache` 函数），因此无需访问网络；若缓存中不存在对应清单，Hermes 会回退到仓库中的 `PREFERRED_SILENT_DEFAULT_MODEL` 常量值，该值必须与标记的默认模型一致。这一设计使得维护人员无需发布新版本即可更换默认默选模型。此类模型通常为性能良好且成本较低的型号，绝非最昂贵的旗舰产品。
- **定价信息及上下文长度**并不包含在清单中，这些数据会在获取时从提供方的实时 API（如 `/v1/models` 接口、models.dev）中获取。

## 获取行为

| 触发场景 | 行为说明 |
|---|---|
| 调用 `/model` 或 `hermes model` | 若磁盘缓存已过期则重新获取数据，否则直接使用缓存 |
| 磁盘缓存为最新状态（未超过有效期） | 不进行网络请求 |
| 缓存存在但网络连接失败 | 无声地回退到缓存，并仅记录一条日志 |
| 网络连接失败且无缓存 | 无声地回退到仓库中的快照版本 |
| 清单的架构验证失败 | 视为无法访问 |

缓存存储路径：`~/.hermes/cache/model_catalog.json`。

## 配置项

```yaml
model_catalog:
  enabled: true
  url: https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
  ttl_hours: 1
  providers: {}
```

将 `enabled: false` 设为该值即可完全禁用远程数据获取，始终使用仓库内的快照。

### 每个提供者的自定义覆盖地址

第三方可以使用相同的架构自行托管其精选列表。只需将相应提供者指向自定义地址即可：

```yaml
model_catalog:
  providers:
    openrouter:
      url: https://example.com/my-openrouter-curation.json
```

覆盖性的清单文件仅需填写其所需关注的提供者模块即可。其他提供者则将继续依据主地址进行解析。

### 隐藏选择器中的提供者

通过 `excluded_providers` 可以在存在有效凭证的情况下，将特定的提供者从 `/model` 选择器中隐藏起来。这对于那些因历史原因或测试用途而存在的、不应在正常使用中出现の提供者尤为有用（例如仍缓存在 `auth.json` 中，或通过 `gh` CLI 找到的旧版 Copilot 或 OpenRouter 凭证）。

```yaml
model_catalog:
  excluded_providers:
    - copilot
    - openrouter
    - openai
```

该排除规则会以不区分大小写的方式，与提供方所能展示的各个键进行匹配——包括内置映射提供方的 Hermes ID 和 models.dev ID、叠加提供方的 overlay PID 与解析后的 Hermes slug，以及规范提供方的规范 slug——因此，像 `copilot` 这样的单一条目即可隐藏对应提供方，而无需考虑其出自哪个分类。所有 `/model` 选择器都会遵循此规则，包括网关的交互式/文本选择器、TUI 选择器，以及交互式的 `hermes model` CLI 选择器。空列表（或省略该键）则不会产生任何影响。

## 更新清单文件

维护者：

```bash
# Re-generate from the in-repo hardcoded lists (keeps manifest in sync after
# editing OPENROUTER_MODELS or _PROVIDER_MODELS["nous"] in hermes_cli/models.py).
python scripts/build_model_catalog.py
```

随后，将修改后的内容通过 Pull Request 提交到 `main` 分支中的 `website/static/api/model-catalog.json` 文件。文档站点会在合并操作完成后自动部署，新的配置文件也将在几分钟内生效。

对于那些不适合通过仓库快照来处理的细粒度元数据更改，您也可以直接手动编辑 JSON 文件——生成脚本仅作为便利工具，并非唯一的真实数据来源。
