---
sidebar_position: 9
title: "Secret Source Plugins"
description: "How to build a secret-manager backend plugin for Hermes Agent"
---

# 构建 Secret Source 插件

Secret Source 会在进程启动时——即在加载 `~/.hermes/.env` 之后、Hermes 读取凭证之前——从外部密钥管理器（如密码保险箱、密码管理器、操作系统密钥库或自定义脚本）中获取提供程序的凭证，并将其转换为环境变量。Bitwarden 和 1Password 已内置于 Hermes 中；**其他所有后端均需通过插件实现**。本指南将介绍如何构建此类插件。

:::tip
默认提供的插件集是封闭的，其策略与 [内存提供程序](/developer-guide/memory-provider-plugin) 相同：任何试图在 `agent/secret_sources/` 目录下添加新密码保险箱后端的 Pull Request 都会以指向本指南的链接作为拒绝理由。建议将您开发的后端发布为独立的插件仓库，并在 Nous Research 的 Discord 频道（`#plugins-skills-and-skins`）中分享。
:::

## 框架负责的内容与开发者需要处理的内容

协调器函数（`agent.secret_sources.registry.apply_all`）负责所有涉及安全性及优先级处理的任务，因此后端无需自行处理这些复杂逻辑：

| 框架负责 | 开发者负责 |
|---|---|
| 数据源的排序规则以及映射型与批量型的优先级处理 | 从自身后端获取数据值 |
| “先声明者胜”的冲突处理机制及相关警告提示 | 验证所使用的引用格式是否正确 |
| `override_existing` 的语义规则（禁止跨数据源覆盖） | 与自身的命令行工具/SDK/API 进行交互 |
| 受保护的启动令牌 | 指定哪个环境变量为启动令牌 |
| 每个数据源的固定超时时间设置 | 确保 `fetch()` 函数的响应速度合理 |
| 每个环境变量的来源信息及 `(来自 X)` 标签 | 生成便于人类阅读的标签 |
| 对 `os.environ` 的写入操作 | 无需处理——开发者不得直接修改系统环境变量 |

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

### 合同规则（强制执行，非建议性要求）

- **`fetch()` 永不抛出异常。** 错误信息会存储在 `result.error` 和 `result.error_kind` 中。若 `fetch()` 抛出异常，将由调度器捕获并标记为 `INTERNAL` 状态——这属于合同违规行为，而非正常功能表现。
- **`fetch()` 永不进行提示。** 应用启动会在非 TTY 环境中执行（如网关、cron 任务或 Docker 容器）。`run_secret_cli()` 会关闭标准输入，从而避免提示功能被触发。交互式认证应纳入您的 CLI 配置流程中，而非启动阶段。
- **在预算范围内同步数据。** 调度器会设置硬性时间限制（默认为 120 秒，用户可通过 `secrets.<name>.timeout_seconds` 自行调整）。若超过该时间限制，系统将返回 `TIMEOUT` 错误，相关结果将被丢弃。
- **由您负责数据获取，调度器负责应用处理。** 请返回您希望提交的映射数据。切勿直接操作 `os.environ`——否则会绕过优先级规则、冲突检测机制以及数据来源追溯功能。
- **API 版本控制。** `SecretSource.api_version` 的默认值为当前的 `SECRET_SOURCE_API_VERSION`。注册表在遇到基于不同版本构建的源时，会发出警告并跳过该源，而不会导致启动失败。

### 选择数据结构类型

- `mapped` — 用户明确将环境变量名称与配置中的引用项绑定（类似 1Password 的 `env:` 映射方式）。此类型意图最为明确：在变量值存在冲突时，`mapped` 类型的声明优先于 `bulk` 类型。
- `bulk` — 您以隐式方式注入整个项目或文件夹中的所有密钥（类似 Bitwarden BSM 的实现方式）。此类方式的优先级低于 `mapped` 类型。

### 可选钩子函数

| 函数名 | 默认值 | 何时需要覆盖 |
|---|---|---|
| `is_enabled(cfg)` | `cfg.get("enabled")` | 需要自定义激活逻辑时 |
| `override_existing(cfg)` | `cfg.get("override_existing", False)` | 希望使用不同的默认值时（所有内置源的轮换功能默认值为 `True`） |
| `protected_env_vars(cfg)` | 空列表 | 拥有引导令牌时（几乎所有场景下都应如此） |
| `fetch_timeout_seconds(cfg)` | 120 秒 | 后端需要不同的时间限制时 |
| `config_schema()` | `{}` | 需要声明用于配置界面的键值时 |

## 子进程安全：请使用 `run_secret_cli()`

如果您的后端需要调用 CLI 工具，建议使用该共享辅助函数，而非直接调用 `subprocess.run`。它可免费为您提供安全保障：仅允许传递命令行参数（禁止使用 `shell=True`），为子进程设置**极简的允许列表环境**（在源代码执行时，`os.environ` 中已包含 Hermes 所知晓的所有凭证——切勿将这些凭证传递给子进程），同时禁用颜色输出并过滤 ANSI 格式的错误信息，还会关闭标准输入，并在超时时抛出干净的 `RuntimeError` 异常。请将用户提供的引用字符串通过 `--` 分隔符添加到命令行参数中，这样它们就永远不会被误解析为命令标志。

## 注册流程

```python
# __init__.py
def register(ctx):
    ctx.register_secret_source(MyVaultSource())
```

对于以下情况，注册会被拒绝（仅会生成日志警告而不会导致程序崩溃）：实例类型不是 `SecretSource`、名称无效或重复、所使用的 `scheme` 已被其他数据源占用、`api_version` 设置错误，或是 `shape` 不属于 `mapped`/`bulk` 类型。

:::note 时间顺序
插件发现机制在启动过程的后期才会执行，晚于首次调用 `load_hermes_dotenv()` 的时间，因此最初加载环境变量的进程不会去查询该插件数据源。不过，之后启动的每一个 Hermes 进程（如网关子进程、定时任务会话以及子代理）都会对其进行检查。预内置的数据源则可满足第一个进程的初始化需求。
:::

## 用户可像配置其他数据源一样对其进行设置

```yaml
secrets:
  sources: [myvault, bitwarden]   # optional ordering
  myvault:
    enabled: true
    # ... your config_schema keys
```

多源优先级判定、冲突警告以及 `(from My Vault)` 这类来源标识都会自动生效——有关优先级规则的具体说明，请参阅[面向用户的机密信息文档](/user-guide/secrets/)。

## 使用合规性测试套件进行验证

在您插件的测试代码中，从 Hermes 仓库中导入该测试套件（位于 `tests/secret_sources/conformance.py`）即可：

```python
import pytest
from tests.secret_sources.conformance import SecretSourceConformance

class TestMyVaultConformance(SecretSourceConformance):
    @pytest.fixture
    def source(self):
        return MyVaultSource()
```

该工具会检查一旦被违反就会对他人造成影响的规则，包括：配置格式错误时不得触发异常、必须使用机器可读的错误类型、默认处于禁用状态、需设置合理的超时时间、受保护的变量名称必须有效，以及必须完成完整的 `apply_all()` 循环调用。若显示绿色，则表示该操作符合后端合约规范。

## ErrorKind 参考表

| 类型 | 含义 |
|---|---|
| `NOT_CONFIGURED` | 功能已启用，但缺少令牌/项目/映射配置 |
| `BINARY_MISSING` | 辅助 CLI 文件不存在或无法执行 |
| `AUTH_FAILED` / `AUTH_EXPIRED` | 凭据无效或已过期 |
| `REF_INVALID` | 密钥引用未通过验证 |
| `NETWORK` | 传输层故障 |
| `EMPTY_VALUE` | 后端针对该引用未返回任何数据——绝不能在有效凭证上使用 `""` |
| `TIMEOUT` | 数据获取超时 |
| `INTERNAL` | 其他所有情况（如错误、异常数据格式等） |
