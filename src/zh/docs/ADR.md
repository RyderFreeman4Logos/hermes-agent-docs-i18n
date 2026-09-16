# 架构决策记录

## 2026-07-13：按 Hermes 主目录/配置文件划分插件管理器状态（键值缓存机制）

状态：已通过

背景说明：
Hermes 支持通过不同的 Hermes 主目录来管理多个配置文件。
在运行中的进程中，主目录的切换有两种方式：一种是通过 `HERMES_HOME` 环境变量实现（适用于单配置文件的 CLI/网关进程）；另一种则是通过上下文级的 `set_hermes_home_override()` 函数实现（位于 `hermes_constants.py` 文件中）。多路复用网关工作进程（`gateway/run.py` 中的 `_profile_scope`）以及子代理/嵌入式调用方会使用这种方式，让单个长生命周期进程能够为多个配置文件提供服务。该覆盖功能基于 `ContextVar` 实现，且刻意**不会**修改 `os.environ`，因为那样做会导致某个配置文件的主目录信息泄露给同一进程中的其他所有并发任务。

此前的插件管理器是一个全局单实例结构（即 `_plugin_manager`）。用户安装的插件会通过 `get_hermes_home() / "plugins"` 路径被发现，而上下文引擎插件（如 `hermes-lcm`）则会在注册时捕获与特定配置文件相关的状态信息——例如 LCM 数据库路径。采用单实例缓存机制意味着：

1. 通过 `set_hermes_home_override()` 更改 Hermes 配置路径的操作，无法被简单的“`HERMES_HOME` 是否发生变化”检测机制所识别。因此，单例模式会持续为进程中的其他所有配置文件 silently 提供第一个配置文件的插件管理器。

2. 即使为新配置路径创建了全新的 `PluginManager`，插件模块仍会通过 `_load_directory_module` 以 `hermes_plugins.<slug>` 的形式被导入到 `sys.modules` 中，且实际上只有这个顶层模块会被替换。同名称插件的 *相对导入*（如 `from . import state`）则会单独缓存于 `hermes_plugins.<slug>.<submodule>` 下，而 Python 的导入机制会优先从 `sys.modules` 中查找这些模块——因此，在切换配置文件时，系统可能会继续使用旧配置文件中已导入的子模块代码或状态，而不会重新执行新配置文件的插件逻辑。

**解决方案：**
将基于单槽的单例模式替换为以*最终确定的* Hermes 配置路径为键的缓存结构（`_plugin_managers_by_home: Dict[Path, PluginManager]`）。`get_plugin_manager()` 函数会通过 `get_hermes_home()` 来确定当前配置路径（该函数本身在查询 `os.environ` 之前就会先检查 `get_hermes_home_override()`），从而能够统一处理环境变量设置和上下文级别的配置覆盖情况。
- `_plugin_manager`（旧的单槽名称）仍被保留下来，作为一个简单的“最后返回的管理器”指针，仅用于向后兼容那些通过 `monkeypatch.setattr(plugins_mod, "_plugin_manager", some_manager)` 进行操作的现有测试代码。当该名称被替换为缓存中不存在的管理器时，`get_plugin_manager()` 会将其视为显式注入的内容，并将其纳入当前已确定的插件目录下的缓存中，而不会直接丢弃它。
- 无论是 `PluginManager._load_directory_module` 方法（在相同插件目录下进行初始加载或当 `force=True` 时强制重新加载），还是通用的 `_clear_plugin_submodules` 辅助函数（用于切换配置文件或测试结束后清理），都会在重新导入某个插件之前，先从 `sys.modules[module_name]` 中移除该模块**以及所有以 `module_name + "."` 开头的名称**，因此通过相对导入生成的子模块在重新加载或切换插件目录后将无法保留。
- 测试隔离机制（通过 `tests/conftest.py` 中的 `_hermetic_environment` 固定装置实现）会调用一个新的 `_reset_plugin_managers_for_tests()` 辅助函数，该函数会在每次测试之间清空整个基于键的缓存，并从 `sys.modules` 中彻底移除所有插件子模块，而不仅仅是重置那个单槽指针。

后果：
- 每个配置文件对应的 LCM 实例（以及任何其他上下文引擎插件）都会使用各自的 `{home}/lcm.db` 文件，无论配置文件切换是通过 `HERMES_HOME` 还是 `set_hermes_home_override()` 方法实现的。  
- 为保障正常性能，插件发现功能会在每个配置文件中缓存相关数据；当重新加载之前使用过的配置文件时，系统会直接复用已缓存的插件管理器，而无需从头开始构建。  
- 无论是顺序切换还是交错切换配置文件——包括在测试环境、网关多路复用工作进程，或是通过上下文级覆盖机制调用的嵌入式应用中——都不再会出现上下文引擎状态、插件模块状态或过期的相对导入子模块在不同配置文件之间泄漏的问题。  
- 回归测试会模拟真实的生产环境切换方式（即使用 `set_hermes_home_override()` 方法），而不仅限于通过环境变量进行切换；此外还专门设计了针对相对导入泄漏问题的测试用例。
