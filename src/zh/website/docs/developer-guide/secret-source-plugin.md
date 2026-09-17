---
sidebar_position: 9
title: "Secret Source Plugins"
description: "How to build a secret-manager backend plugin for Hermes Agent"
---

# 构建 Secret Source 插件

Secret Source 会在进程启动时——即在加载 `~/.hermes/.env` 文件之后、Hermes 读取凭证之前——从外部密钥管理器（如密码库、密码管理器、操作系统密钥存储库或自定义脚本）中获取提供程序的凭证，并将其转换为环境变量。Bitwarden、1Password 以及通用的命令辅助源已内置在系统中；**其他所有后端均需通过插件实现**。本指南将介绍如何构建此类插件。

:::tip
默认情况下，内置的插件集合是封闭的，其政策与[内存提供程序](/developer-guide/memory-provider-plugin)相同：任何试图在 `agent/secret_sources/` 目录下添加新密码库后端的 Pull Request 都会以指向本指南的链接作为拒绝理由。建议您将自己的后端作为独立的插件仓库发布，并在 Nous Research 的 Discord 频道（`#plugins-skills-and-skins`）中分享。
:::

## 第一个进程的启动时序

`load_hermes_dotenv()` 函数通常在导入阶段运行，即**插件注册之前**。之后，当有任何已启用的插件 Secret Source 被配置时，Hermes 会在发现插件后重新获取这些凭证。插件的启用机制遵循该源的 `is_enabled(cfg)` 接口规范；标准格式为 `secrets.<name>.enabled: true`，同时也支持自定义的激活方式。这样一来，就能解决“用我自己的密码库替代 Bitwarden”这一第一个进程启动阶段存在的问题（#64177）。

- 重新拉取操作是幂等的，并采用“失败即开放”机制（绝不会阻塞启动过程）。  
- 数据源仅能通过调度器提供环境变量；除了自身配置允许的范围外，**不存在**用于导出其他插件或用户全部密钥存储的插件 API。  
- 任何进程内代码都可以在加载后读取 `os.environ`——信任边界依然遵循“已启用的插件以代理权限运行”的原则。  

## 框架负责的内容与用户负责的内容

调度器（`agent.secret_sources.registry.apply_all`）负责所有涉及安全性和优先级控制的事项，因此后端绝不会出错：

| 框架负责 | 用户负责 |
|---|---|
| 数据源的排序以及映射型与批量型的优先级处理 | 从后端获取数值 |
| 首个请求优先的冲突处理机制及相关警告提示 | 校验参考格式的合法性 |
| `override_existing` 的语义规则（禁止跨数据源覆盖） | 与自身的 CLI/SDK/API 进行交互 |
| 受保护的启动令牌 | 明确指定哪个环境变量为启动令牌 |
| 每个数据源的硬性超时时间设置 | 确保 `fetch()` 操作的响应速度合理 |
| 每个变量的来源信息及 `(来自 X)` 标签 | 提供易于理解的标签内容 |
| 对 `os.environ` 的写入操作 | 无需处理——用户绝不能直接修改环境变量 |

## 目录结构

```
~/.hermes/plugins/my-vault/
├── plugin.yaml      # name, description
└── __init__.py      # SecretSource subclass + register(ctx)
```

## SecretSource ABC 概述

需实现 `agent.secret_sources.base.SecretSource` 接口。该接口至少需要定义一个方法：

```python
from pathlib import Path

from agent.secret_sources.base import (
    ErrorKind,
    FetchResult,
    SecretSource,
    run_secret_cli,
)


class MyVaultSource(SecretSource):
    name = "myvault"          # config section key: secrets.myvault
    label = "My Vault"        # used in startup lines + provenance labels
    shape = "mapped"          # "mapped" (explicit VAR→ref map) or "bulk" (project dump)
    scheme = "mv"             # optional: unique URI scheme you own (mv://...)

    def fetch(self, cfg: dict, home_path: Path) -> FetchResult:
        """Resolve secrets. MUST NOT raise. MUST NOT prompt."""
        result = FetchResult()
        token = os.environ.get("MYVAULT_TOKEN", "").strip()
        if not token:
            result.error = "secrets.myvault.enabled is true but MYVAULT_TOKEN is not set."
            result.error_kind = ErrorKind.NOT_CONFIGURED
            return result

        try:
            proc = run_secret_cli(
                ["myvault-cli", "export", "--json"],
                allow_env=["MYVAULT_TOKEN"],   # ONLY your auth vars — never full os.environ
                timeout=30,
            )
        except RuntimeError as exc:           # spawn failure / timeout
            result.error = str(exc)
            result.error_kind = ErrorKind.BINARY_MISSING
            return result

        if proc.returncode != 0:
            result.error = f"myvault-cli exited {proc.returncode}: {proc.stderr[:200]}"
            result.error_kind = ErrorKind.AUTH_FAILED
            return result

        result.secrets = parse_your_output(proc.stdout)  # {ENV_VAR: value}
        return result

    def protected_env_vars(self, cfg: dict):
        # Your bootstrap token — no source (including yours) may ever overwrite it.
        return frozenset({"MYVAULT_TOKEN"})
```

### 合同规则（强制执行，而非建议）

- **`fetch()` 永不抛出异常。** 错误信息会存储在 `result.error` 和 `result.error_kind` 中。若 `fetch()` 抛出异常，调度器会将其捕获并标记为 `INTERNAL` 状态——这属于合同违规行为，而非正常功能表现。
- **`fetch()` 永不进行提示。** 应用会在非 TTY 环境中启动（如网关、cron 任务或 Docker 容器）。`run_secret_cli()` 会关闭标准输入，因此提示相关功能会立即失效。交互式认证应集成到 CLI 配置流程中，而非启动阶段。
- **在预算范围内同步数据。** 调度器会设置一个硬性时间限制（默认为 120 秒，用户可通过 `secrets.<name>.timeout_seconds` 自行调整）。若超过该时间限制，系统将返回 `TIMEOUT` 错误，相关结果会被丢弃。
- **由你负责数据获取，调度器负责应用处理。** 请返回你打算提供的映射数据。切勿直接操作 `os.environ`——这样会绕过优先级规则、冲突检测机制以及数据来源追踪功能。
- **API 版本控制。** `SecretSource.api_version` 的默认值为当前的 `SECRET_SOURCE_API_VERSION`。注册表在遇到基于不同版本构建的源时，会发出警告并跳过该源，而不会导致启动失败。

### 选择数据结构格式

- `mapped` — 用户明确将环境变量名与配置中的引用项绑定（类似 1Password 的 `env:` 映射方式）。这是最明确的指定方式：在变量值存在冲突时，`mapped` 格式的声明具有更高优先级。
- `bulk` — 以隐式方式注入整个项目或文件夹中的所有密钥（类似 Bitwarden BSM 的处理方式）。此类格式的优先级低于 `mapped` 格式。

### 可选钩子功能

| 方法 | 默认值 | 何时需要覆盖 |
|---|---|---|
| `is_enabled(cfg)` | `cfg.get("enabled")` | 需要自定义激活逻辑时 |
| `override_existing(cfg)` | `cfg.get("override_existing", False)` | 希望使用不同的默认值时（所有内置数据源的轮换功能默认值为 `True`） |
| `protected_env_vars(cfg)` | 空列表 | 拥有引导令牌时（您几乎肯定拥有该令牌） |
| `fetch_timeout_seconds(cfg)` | 120秒 | 后端需要不同的超时时间时 |
| `config_schema()` | `{}` | 需要为配置界面声明配置键时 |
| `remediation(kind, cfg)` | 按 `ErrorKind` 类型提供的通用提示信息 | 希望将错误警告指向用户自定义的修复命令时（例如，内置数据源在遇到 `AUTH_FAILED` 错误时会返回 `Run hermes secrets <name> token…`）。该函数必须是纯粹的类型到字符串的映射：不进行任何 I/O 操作，也不会抛出异常。如需屏蔽提示信息，可返回 `""`。 |

## 子进程安全：请使用 `run_secret_cli()`

如果您的后端需要调用 CLI 工具，建议使用此共享辅助函数而非直接调用 `subprocess.run`。它无需额外成本即可提供强大的安全性保障：仅允许传递命令行参数（禁止使用 `shell=True`），仅为子进程设置**极简的允许环境变量列表**（在数据源开始运行时，`os.environ` 中已包含 Hermes 所知晓的所有凭证——绝不可将这些凭证传递给子进程），同时会禁用颜色显示并过滤 ANSI 格式的错误输出，还会关闭标准输入，并在超时时引发标准的 `RuntimeError` 异常。用户提供的引用字符串应通过命令行参数中的 `--` 符号后传递，这样它们就绝不可能被误解析为命令标志。

## 注册方式

```python
# __init__.py
def register(ctx):
    ctx.register_secret_source(MyVaultSource())
```

以下情况会导致注册被拒绝（仅会生成日志警告而不会导致程序崩溃）：实例类型并非 `SecretSource`、名称无效或重复、所使用的 `scheme` 已被其他数据源占用、`api_version` 设置错误，或是 `shape` 不属于 `mapped`/`bulk` 类型。

:::note 时间顺序
插件发现操作在启动过程中会晚于第一次调用 `load_hermes_dotenv()` 的时间执行。在发现插件之后，Hermes 会立即重新加载已启用的插件密钥源（通过 `reset_secret_source_cache()` 和 `load_hermes_dotenv()` 实现），因此插件发现流程确实能够检测到这些密钥源——详情请参见上文中的[首个进程启动时间顺序](#first-process-bootstrap-timing)（#64177）。此重新加载操作采用“失败即继续”策略，若没有启用任何插件源则直接跳过该步骤。在插件模块导入或 `register(ctx)` 被调用期间读取 `os.environ` 的代码仍会在重新加载之前执行，因此无法依赖同一数据源提供的凭证；涉及凭证处理的逻辑应放在 `fetch()` 函数内部。网关进程、定时任务进程以及子代理进程也会执行相同的发现/重新加载流程。
:::

## 用户可像配置其他数据源一样对其进行设置

```yaml
secrets:
  sources: [myvault, bitwarden]   # optional ordering
  myvault:
    enabled: true
    # ... your config_schema keys
```

多源优先级判定、冲突警告以及 `(from My Vault)` 之类的来源标签均可自动生效——有关优先级规则的具体说明，请参阅[面向用户的机密信息文档](/user-guide/secrets/)。

## 使用合规性检测工具进行验证

在您插件的测试代码中，从 Hermes 仓库中导入该检测工具（位于 `tests/secret_sources/conformance.py`）并对其进行子类化即可：

```python
import pytest
from tests.secret_sources.conformance import SecretSourceConformance

class TestMyVaultConformance(SecretSourceConformance):
    @pytest.fixture
    def source(self):
        return MyVaultSource()
```

该工具会检查一旦被违反就会对他人造成影响的规则，包括：配置格式错误时不得触发警告、错误类型需具备机器可读性、默认处于禁用状态、超时时间必须为正数、受保护的变量名称必须有效，以及需完成一次完整的`apply_all()`往返操作。若显示绿色，则表示已通过验证，可安全调用符合合约要求的后端服务。

## ErrorKind参考

| 类型 | 含义 |
|---|---|
| `NOT_CONFIGURED` | 功能已启用，但缺少令牌/项目/映射配置 |
| `BINARY_MISSING` | 辅助CLI命令不存在或无法执行 |
| `AUTH_FAILED` / `AUTH_EXPIRED` | 凭证无效或已过期 |
| `REF_INVALID` | 密钥引用未能通过验证 |
| `NETWORK` | 传输层故障 |
| `EMPTY_VALUE` | 后端针对该引用未返回任何数据——绝不可对有效的凭证使用`""`值 |
| `TIMEOUT` | 数据获取操作超时 |
| `INTERNAL` | 其他各类问题（如漏洞、意外格式等） |
