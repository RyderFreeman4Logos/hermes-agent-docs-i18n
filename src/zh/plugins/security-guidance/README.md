# 安全指导功能

针对智能体生成的代码，该功能会通过模式匹配机制发出安全警告。当智能体使用符合已知危险代码模式的内容调用 `write_file`、`patch` 或 `skill_manage` 等函数时（例如 `eval`、`pickle.load`、`yaml.load`、`os.system`、带有 `shell=True` 参数的 `subprocess`、`dangerouslySetInnerHTML`、`verify=False` 设置、ECB 加密模式、GitHub Actions 中的 `${{ github.event.* }}` 注入攻击、未设置 `weights_only=True` 的 `torch.load` 等），插件会向工具的输出结果中添加警告信息。文件仍会被正常写入；模型在后续交互中会看到该警告，从而能够修正代码或简要说明为何该代码结构是安全的。

这是 Anthropic 的 `security-guidance` 插件设计的第 1 层——一种在本地快速运行的初步检测机制，无需消耗任何大语言模型令牌。第 2 层和第 3 层功能（如每轮交互结束后的 LLM 差异审查、智能体驱动的代码提交审查）并未被移植到该插件中；不过智能体仍可通过 `delegate_task` 功能按需执行这类审查操作。

## 覆盖范围（25 条规则）

这些模式规则直接从 Anthropic 的 `claude-plugins-official` 项目下按 Apache-2.0 许可协议复制而来。具体分类如下：

| 类别 | 规则 |
|---|---|
| 不安全反序列化操作 | `pickle.load`、`cPickle/cloudpickle/dill.load`、`marshal.loads`、`shelve.open`、`yaml.load`、`yaml.unsafe_load`、未设置 `weights_only=True` 的 `torch.load`、`joblib.load`、`pandas.read_pickle`、`numpy.load(allow_pickle=True)` |
| 命令注入攻击 | `os.system`、`subprocess(..., shell=True)`、JavaScript 中的 `child_process.exec`、Go 语言中的 `exec.Command("sh"...)` |
| 代码注入攻击 | `eval(`、JavaScript 中的 `new Function(...)` |
| XSS 漏洞点 | `.innerHTML =`、`.outerHTML =`、`.insertAdjacentHTML(`、`document.write`、React 框架中的 `dangerouslySetInnerHTML` |
| 加密安全缺陷 | AES ECB 加密模式、Node.js 中未设置初始化向量（IV）的 `crypto.createCipher` 函数、TLS 验证被禁用（`verify=False`、`rejectUnauthorized: false`、`InsecureSkipVerify: true` 等） |
| XXE 攻击 | 未使用 `defusedxml` 的 `xml.etree`、`minidom`、`xml.sax` 库 |
| 供应链安全问题 | 缺少 `integrity=` SRI 哈希值的 `<script src="https://..."` 标签 |
| CI/CD 流水线注入攻击 | GitHub Actions 工作流文件中在 `run:` 部分使用 `${{ github.event.* }}` 的写法 |

该模式匹配机制基于 Python 正则表达式及字面字符串匹配技术实现。每条规则都对应一个针对特定文件扩展名的 `path_filter` 函数——仅适用于 Python 的规则会忽略 `.js` 文件，仅适用于 JavaScript 的规则会忽略 `.py` 文件，所有规则都会忽略 `.md/.txt/.rst/.json/.yaml` 文件。此外，正则表达式还通过后顾断言机制排除方法调用情况（因此 `model.eval()` 和 `redis.eval()` 不会触发 `eval(` 规则）。该插件的误报率虽处于中等水平，但仍在可接受范围内；正因如此，它默认采用“先警告再处理”的策略。

## 启用方式

该插件为可选功能。您只需将其添加到允许列表中即可启用。

```bash
hermes plugins enable security-guidance
# or edit ~/.hermes/config.yaml manually:
plugins:
  enabled:
    - security-guidance
```

## 模式

| 环境变量 | 默认值 | 效果 |
|---|---|---|
| (无) | warn | 在工具输出结果中追加一个 `⚠️ 安全指南` 区块，并将文件保存下来。 |
| `SECURITY_GUIDANCE_BLOCK=1` | 未设置 | 完全拒绝写入操作，同时给出警告作为原因。适用于要求更为严格的环境。 |
| `SECURITY_GUIDANCE_DISABLE=1` | 未设置 | 禁用开关——插件虽会被加载，但不会执行任何操作。 |

## 目前尚不支持的功能

* **不支持大语言模型差异审查。** Anthropic 的第二层架构会在每个涉及文件操作的智能体轮次中触发一次辅助大语言模型的调用。在 hermes 中，默认情况下这些调用会通过主模型处理（`auxiliary_client._resolve_auto()` 优先使用主模型），这会消耗大量的推理模型算力。未来可通过单独的拉取请求，让第二层架构在用户明确选择的情况下使用成本更低的辅助模型。
* **不支持智能体提交审查功能。** Anthropic 的第三层架构会生成一个具备 `Read`/`Grep`/`Glob` 功能的 SDK 子智能体，用于追踪 `git commit` 操作中的数据流。这项功能属于后续开发内容，将基于 `delegate_task` 机制实现。
* **不支持项目级规则文件。** Anthropic 的 `.claude/claude-security-guidance.md` 文件是由其第二层/第三层大语言模型提示词读取的，而非模式扫描器。待第二层架构稳定后，我们可以添加类似的 `.hermes/security-guidance.md` 文件。

## 局限性

这是一个尽力提供辅助功能的工具。模式匹配可能会遗漏某些漏洞，也可能产生误报。请将警告视为建议，而非代码审查、静态应用安全测试、依赖项扫描或渗透测试的替代方案。

## 出处说明与许可协议

* `patterns.py` 文件直接复制自
  [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance/hooks)
 （提交记录 `0bde168`，2026年5月26日），遵循
  [Apache License 2.0](./LICENSE) 许可协议。完整的出处说明请参见 [NOTICE](./NOTICE) 文件。
* `__init__.py`、`plugin.yaml`、`README.md` 及相关测试代码均为 NousResearch 的原创成果，与 hermes-agent 的其他部分一同采用 MIT 许可协议发布。
