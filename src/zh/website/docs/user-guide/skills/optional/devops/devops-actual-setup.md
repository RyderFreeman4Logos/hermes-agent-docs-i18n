---
title: "Actual Setup — Set up Actual Computer (actual.inc) inference in Hermes"
sidebar_label: "Actual Setup"
description: "Set up Actual Computer (actual.inc) inference in Hermes"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Actual Computer 的配置

在 Hermes 中配置 [actual.inc](https://actual.inc)（Actual Computer）作为推理提供者。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/devops/actual-setup` 命令安装 |
| 路径 | `optional-skills/devops\actual-setup` |
| 版本 | `2.0.0` |
| 开发者 | shl0ms + Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `actual`、`actual-inc`、`provider`、`local-inference`、`relay`、`gguf`、`setup` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，Agent 就会看到这些指令。
:::

# Actual Computer 配置技能

该技能用于将 [actual.inc](https://actual.inc)（Actual Computer）配置为 Hermes 的推理提供者。Actual 能够将用户的自有硬件转换为私有的推理集群，并通过两种方式提供兼容 OpenAI 的 API：一种是位于 `https://api.actual.inc` 的端到端加密中转服务（需使用 `ac_` 密钥进行身份验证）；另一种则是位于 `http://127.0.0.1:8080` 的本地设备守护进程（在本地回环通信时无需身份验证）。该技能不会自动为用户安装 Actual 守护进程——设备授权需要用户通过浏览器进行操作。

## 适用场景

- 用户希望将 actual.inc 添加为推理提供者（云端中转或本地模式）。
- 用户拥有 `ac_` 密钥，希望让 Hermes 通过其 Actual 集群进行请求路由。
- 用户希望借助 Actual 守护进程实现完全本地的设备端推理。
- 故障排除：Actual 请求因神秘的 400 错误或空流数据而失败。

## 先决条件

- Hermes 已提供对 **first-class `actual` 提供者的支持**（提供者标识为 `actual`，别名包括 `actual-computer`、`actualcomputer`、`aci`）。请勿在当前版本的 Hermes 中将 Actual 配置为 `custom_providers` 或 `providers.actual.*` 类型的条目——内置提供者已占用该名称，并自动处理基础 URL 标准化、响应传输以及本地无认证功能。
- 中转模式：需拥有一个 Actual 账户，以及从 https://actual.inc/user/keys 获取的 `ac_` 推理密钥。
- 本地模式：用户需先安装守护进程（执行命令 `curl -fsSL "https://actual.inc/install" | bash`），并通过运行一次 `actual` 命令并打开浏览器中生成的 `https://actual.inc/device?code=...` 链接来完成设备授权。只需将该链接转发给用户并等待即可——切勿伪造邮箱或代其进行授权。授权码有效期为 5 分钟，如需重新获取请再次运行 `actual` 命令。

## 运行方法

### 中转/API 模式

1. 将密钥放入 `.env` 文件中（仅存储敏感信息，切勿放入 config.yaml）：
   在 `~/.hermes/.env` 文件末尾添加 `ACTUAL_API_KEY=ac_...`。
2. 使用 `terminal` 工具验证密钥并查找可用模型：
   ```bash
   curl -s https://api.actual.inc/v1/models -H "Authorization: Bearer $ACTUAL_API_KEY"
   ```
3. 选择提供商与模型：
   ```bash
   hermes config set model.provider actual
   hermes config set model.default "MODEL_ID_FROM_DISCOVERY"
   ```
4. 验证端到端流程：
   ```bash
   hermes chat -Q -q "Reply with exactly: ACTUAL_OK" --provider actual -m MODEL_ID
   ```

### 本地模式

1. 用户已安装并授权了守护进程（详见前提条件）。
2. 下载并加载模型（授权后只需执行一次该操作即可）。
   ```bash
   actual models search "qwen2.5 0.5b instruct gguf" --limit 8 --no-prompt
   # Downloads REQUIRE an explicit quantization (409 ambiguous_model_download otherwise):
   actual models download "Qwen/Qwen2.5-0.5B-Instruct-GGUF/Q4_K_M"
   actual models list        # note the INSTALLED name (differs from download id)
   actual models load "qwen2.5-0.5b-instruct-q4_k_m"   # load by installed name
   ```
3. 将 Hermes 指向该守护进程。若将 `ACTUAL_BASE_URL` 设置为回环主机地址，系统会自动将内置提供程序切换至本地无需认证的模式——无需任何密钥：只需在 `~/.hermes/.env` 文件中添加 `ACTUAL_BASE_URL=http://127.0.0.1:8080`，随后即可。
   ```bash
   hermes config set model.provider actual
   hermes config set model.default "INSTALLED_MODEL_NAME"
   ```
4. 验证（工具集已精简——详情参见下文的上下文窗口相关问题）：
   ```bash
   hermes chat -Q -q "Reply with exactly: LOCAL_OK" --provider actual -m INSTALLED_NAME -t file,web
   ```

## 快速参考

| 项目 | 值 |
|---|---|
| 托管中继 | `https://api.actual.inc/v1`（会自动从原始主机地址进行标准化处理） |
| 本地守护进程 | `http://127.0.0.1:8080/v1`（回环地址无需身份验证） |
| 密钥环境变量 | `ACTUAL_API_KEY`（格式为 `ac_...`） |
| 基础URL环境变量 | `ACTUAL_BASE_URL`（使用回环主机时即进入本地无认证模式） |
| 提供商标识/别名 | `actual` / `actual-computer`、`actualcomputer`、`aci` |
| 传输协议 | 响应API (`codex_responses`)——为内置功能，不可被覆盖 |
| 集群绑定 | 通过 config.yaml 中的 `providers.actual.extra_headers` 设置 `X-Cluster-ID` 请求头 |
| 模型大小参考 | 0.5B Q4_K_M 级模型约 470MB（小型模型），7-8B Q4_K_M 级模型约 4.5GB（常用型），32B 模型约 20GB |

## 常见问题

1. **推理强度设置陷阱（作为一级供应商，Hermes 已自动处理此问题。）**
   Actual 的 SGLang/vLLM 后端仅支持 `none/low/medium/high/max` 这些数值；
   若使用 `xhigh`/`ultra` 设置，将会返回含义模糊的错误信息：
   `Expecting value: line 1 column 1 (char 0)`（实际上为封装后的 HTTP 400 错误）。内置供应商会在传输过程中将 `xhigh` 自动转换为 `high`，将 `ultra` 转换为 `max`。如果在旧版本 Hermes 上仍会出现 400 错误，可在 config.yaml 中为特定模型设置上限：
   `agent.reasoning_overrides.<model>: high`
2. **小型本地模型导致的上下文窗口溢出问题。** Hermes的默认工具集包含约26k个令牌的架构信息以及约9k个令符的系统提示词。当加载上下文长度为32k的模型时，会在第一轮对话之前就出现溢出现象，此时llama.cpp系列服务器会仅返回`data: [DONE]`，而Hermes则会报告“Provider returned an empty stream with no finish_reason”。这并非SSE协议的缺陷。解决方案包括：限制可用工具（使用`-t file,web`选项）、为模型设置更大的`n_ctx`值，或选择上下文长度≥64k的模型以使用完整工具集。相关问题追踪链接：#51448（请勿新建问题，可在该链接处附上证据）。另有类似但不同的问题：#65631（HTTP-200状态码下返回400错误的SSE流），#56516（仅输出推理过程的流）。

3. **下载标识与已安装名称的差异。** `actual models download`功能在未指定量化格式时会尝试访问`repo/QUANT`目录并触发409冲突错误；而`actual models load`功能则会根据“实际模型列表”中的已安装名称来加载模型。

4. **推理模型返回空内容的问题。** GLM/Qwen系列的推理版本会将思考过程输出到单独的`reasoning`字段中，这可能导致少量的输出预算被完全用于推理过程。在判定系统故障之前，请先检查服务器端的默认输出设置。

5. **请勿创建名为“actual”的自定义提供者。** 在早期版本的安装指南中（在内置提供者功能正式支持之前），曾出现过`providers.actual.*`这样的配置块。在当前版本的Hermes中，内置提供者的名称具有优先级，过时的自定义配置块将被忽略或引发冲突。建议删除这些旧配置块，改用上述的环境变量与`model.provider`设置方式。

## 验证

```bash
# Relay:
hermes chat -Q -q "Reply with exactly: ACTUAL_OK" --provider actual -m MODEL
# Local (small model — reduced toolset):
hermes chat -Q -q "Reply with exactly: LOCAL_OK" --provider actual -m MODEL -t file,web
# Provider status (local no-auth shows key_source=local-offline):
hermes status
```

对于其他兼容 OpenAI 的客户端（例如 OpenCode），请参阅 `references/opencode.md`。
