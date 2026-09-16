# 终端环境提供者插件

Hermes 通过一组可插拔的**终端后端**来执行 Shell 命令。内置的后端（本地、Docker、Singularity、Modal、Daytona、Vercel Sandbox、SSH）位于核心代码库的 `tools/environments/` 目录下。而第三方沙箱服务则通过**插件**的形式集成——这些独立的插件仓库会被安装到 `~/.hermes/plugins/` 目录中，用户可以通过 `config.yaml` 文件中的 `terminal.backend` 选项来注册这些插件，其使用方式与内置后端完全相同。

本页面的内容与 [浏览器提供者插件](/developer-guide/browser-provider-plugin) 文档相对应——注册流程和作用域语义均保持一致。

## 提供者能控制哪些功能

已注册的后端会自动参与所有核心功能模块：

| 功能模块 | 控制依据 |
|---|---|
| 命令分发（`terminal`、`execute_code`、文件工具） | `create_environment()` |
| `hermes setup` 后端选择器 | `display_name`、`description`、`setup_instructions()`、`post_setup()` |
| 仪表板终端后端选择器（用于检测状态） | `probe()` |
| `hermes status` / `hermes doctor` 功能 | `doctor_checks()` |
| 系统提示中的环境信息显示 | `is_remote`、`env_description` |
| 跳过危险命令的审批流程 | `skip_container_guards` |
| 容器路径/工作目录处理 | `is_container` |
| 同步缓存文件的路径转换 | `cache_path_base` |
| 从子进程中移除敏感信息 | `strip_env_keys` |
| 每会话独立的沙箱隔离（`container_persistent: false`） | `session_isolated_when_nonpersistent` |
在 Provider 中声明这些标志即可彻底解决经典的“新后端缺失分类站点 N”问题——系统会从每个站点的注册表中查询信息，而不再依赖硬编码的站点名称列表。

## 最简版 Provider

```python title="~/.hermes/plugins/acmebox/__init__.py"
from agent.terminal_env_provider import TerminalEnvironmentProvider


class AcmeBoxEnvironment:
    """Must satisfy the BaseEnvironment duck-typed contract."""

    def __init__(self, cwd, timeout, task_id):
        self.cwd, self.timeout, self.task_id = cwd, timeout, task_id

    def execute(self, command, timeout=None, **kwargs):
        ...  # run the command in the sandbox
        return {"output": "...", "exit_code": 0}

    def cleanup(self):
        ...  # tear down / detach


class AcmeBoxProvider(TerminalEnvironmentProvider):
    name = "acmebox"
    display_name = "AcmeBox"
    is_remote = True          # commands don't run on the host
    is_container = True       # container-style path/cwd semantics

    @property
    def description(self):
        return "Run commands in an AcmeBox cloud sandbox."

    @property
    def cache_path_base(self):
        return "~/.hermes"    # where synced cache files land, or None

    @property
    def strip_env_keys(self):
        return frozenset({"ACMEBOX_TOKEN"})

    def is_available(self):
        import importlib.util, os
        return (
            importlib.util.find_spec("acmebox") is not None
            and bool(os.getenv("ACMEBOX_TOKEN"))
        )

    def create_environment(self, *, cwd, timeout, task_id="default",
                           image=None, container_config=None, **kwargs):
        return AcmeBoxEnvironment(cwd, timeout, task_id)


def register(ctx):
    ctx.register_terminal_environment_provider(AcmeBoxProvider())
```

```yaml title="~/.hermes/plugins/acmebox/plugin.yaml"
name: acmebox
version: 0.1.0
description: AcmeBox cloud sandbox terminal backend
kind: backend
```

启用该功能，选中它，然后运行：

```bash
hermes plugins enable acmebox
hermes config set terminal.backend acmebox
```

## 规则

- **保留名称**。与内置后端名称（`local`、`docker`、`singularity`、`modal`、`managed_modal`、`daytona`、`vercel_sandbox`、`ssh`）冲突的注册将被拒绝。插件仅用于扩展后端列表，绝不能替代内置后端。
- **`create_environment` 必须支持 `**kwargs` 参数**，并对未知键值忽略不计——这种前向兼容机制使得函数签名可以演变，而不会影响旧版插件。
- **`is_available()` / `probe()` 方法必须高效**。禁止进行任何网络调用，因为这些方法会在需求检查及界面渲染阶段执行。
- **处处采用软失败机制**。若某个提供者属性抛出异常，核心系统会将其视为默认行为（例如，抛出异常的 `skip_container_guards` 仍会保持审批功能开启状态）。请勿依赖异常来实现控制流逻辑。
- **机密信息应放入 `strip_env_keys` 中**。您的供应商令牌绝不能被模型生成的Shell命令读取；通过该机制，令牌会无条件地从所有启动的子进程中移除，其处理方式与内置的 `MODAL_*` / `DAYTONA_API_KEY` 类似。

## 环境对象契约

`create_environment()` 方法返回的对象需遵循与 `tools.environments.base.BaseEnvironment` 相同的鸭子型接口规范：

- `execute(command, timeout=None, ...)` → `{"output": str, "exit_code": int}`
- `cleanup()` —— 用于释放资源，会在会话终止或空闲状态回收时被调用
- 可选功能：类似内置云后端的持久化钩子机制
建议继承 `BaseEnvironment` 类（这样即可复用通用的文件同步及后台进程机制），但并非强制要求。

## 会话隔离机制

如果您的沙箱是通过名称来**恢复的**（即后端重新连接到一个持久化的虚拟机），请将 `session_isolated_when_nonpersistent` 设置为 `True`。在同时设置 `terminal.container_persistent: false` 的情况下，每个会话都将拥有独立的沙箱标识，而不会共享同一个沙箱——否则，两个独立的临时运行实例可能会同时连接同一个正在运行的虚拟机，从而导致该虚拟机被意外删除。
