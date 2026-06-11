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
        {"id": "moonshotai/kimi-k2.6", "description": "recommended", "metadata": {}},
        {"id": "openai/gpt-5.4",       "description": ""}
      ]
    },
    "nous": {
      "metadata": {},
      "models": [
        {"id": "anthropic/claude-opus-4.7"},
        {"id": "moonshotai/kimi-k2.6"}
      ]
    }
  }
}
```

字段说明：

- **`version`** — 整数类型的架构版本号。后续架构更新时会提升此版本号；Hermes 会拒绝解析其不识别的版本号的清单文件，并回退到硬编码的快照版本。
- **`metadata`** — 位于清单文件、提供方及模型层级的结构化字典，支持任意键名。Hermes 会忽略未知字段，因此您可以直接为对应条目添加注释（如 `"tier": "paid"`、`"tags": [...]` 等），而无需协调架构变更。
- **`description`** — 仅适用于 OpenRouter。该字段用于确定选择器标签的显示文本（如 `"recommended"`、`"free"` 或留空）。Nous Portal 不使用此字段——免费套餐的权限判定是直接从 Portal 的定价接口动态获取的。
- **定价信息与上下文长度** 不包含在清单文件中，这些数据会在数据获取时从提供方的实时 API（如 `/v1/models` 接口、models.dev）中获取。

## 数据获取行为

| 触发场景 | 行为表现 |
|---|---|
| 调用 `/model` 或 `hermes model` 命令 | 若磁盘缓存已过期则重新获取数据，否则直接使用缓存 |
| 磁盘缓存为最新状态（未超过有效期限） | 不进行网络请求 |
| 缓存存在但网络连接失败 | 无声回退至缓存，并仅记录一条日志信息 |
| 网络连接失败且无缓存 | 无声回退至仓库内的快照版本 |
| 清单文件通过架构验证失败 | 视为无法访问 |

缓存存储路径：`~/.hermes/cache/model_catalog.json`。

## 配置选项

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

覆盖版清单只需填写其关心的提供程序模块即可，其他提供程序则仍会依据主地址进行解析。

## 更新清单

维护者：

```bash
# Re-generate from the in-repo hardcoded lists (keeps manifest in sync after
# editing OPENROUTER_MODELS or _PROVIDER_MODELS["nous"] in hermes_cli/models.py).
python scripts/build_model_catalog.py
```

随后，将修改后的内容通过 Pull Request 提交到 `main` 分支中的 `website/static/api/model-catalog.json` 文件。文档站点会在合并操作完成后自动部署，新的配置文件也将在几分钟内生效。

对于那些不适合通过仓库快照来处理的细粒度元数据更改，您也可以直接手动编辑 JSON 文件——生成脚本仅作为便利工具，并非唯一的真实数据来源。
