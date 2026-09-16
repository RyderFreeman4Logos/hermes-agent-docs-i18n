---
sidebar_position: 15
title: "CLI Internals"
description: "How hermes_cli is shaped: slash dispatch, config loaders, the skin engine, the transactional update pipeline, and process-identity rules"
---

# CLI 内部机制

作为 `hermes_cli/AGENTS.md`（规则说明）的补充，本页面提供了更为详尽的解释。

## 更新流程

分阶段的执行流程（`计划 → 快照 → 应用 → 按类型重启 → 验证 → 报告`）以及各阶段需防范的字段错误情况均记录在 `hermes_cli/AGENTS.md` 中；面向用户的功能表现（确认信息、`--plan` 参数、快照模式等）则详见 [更新操作](../getting-started/updating.md)。

systemd的强制重启回退机制会等待该单元的`TimeoutStopUSec`与`TimeoutStartUSec`时间之和，再加上15秒的客户端缓冲时间。它会读取与重启处于同一管理器作用域内的目标单元；无论是首次尝试还是重试，都会使用这一时间预算，包括在更新被中断后的补救性重启。而在平稳关闭之后进行的启动，则仅会消耗启动时间预算及相应的缓冲时间。如果某个阶段的限制值缺失、无法解析或为无限大，该阶段的时间将被回退为90秒，从而确保无人监控的更新过程不会超出控制范围。即使`systemctl`客户端超时，也不会取消管理器的事务处理。自定义的多命令停止序列或`EXTEND_TIMEOUT_USEC`设置仍可能让操作持续时间超过此预估值；真正的超时仍属于未完成的重启状态，而那些执行成功的命令仍需经过现有的服务健康状况及集群版本验证。原始的数字形式`*USec`值代表微秒，而格式化后的值则使用systemd规定的固定单位，包括天、周、月和年。总的超时时间会被限制在原生32位有符号毫秒级轮询上限之下（并留有四舍五入的余量），因此即便单元的限制值异常长，也不会导致子进程轮询出现溢出现象。对于为零、未知或为无限大的阶段限制，则会采用上述受限回退机制。此设置不会改变当前正在进行的资源消耗相关参数。 

## 进程标识：切勿通过argv参数的子串来推断

约10个fleet更新问题背后的错误类型（#90778、#87594、#78089、#76129、#91964等）：
这些问题的根源在于根据命令行中的“serve”字样或其他类似特征对进程进行分类。`kanban --preserve-cache`命令中就包含“serve”；某些标志值实际上可以对应某个子命令（如`-m dashboard serve`）；而被截断的命令行则会隐藏真实的子命令。相关规则如下：

- 应使用标准匹配器：`gateway.status.looks_like_gateway_command_line`（用于检测gateway运行状态），以及`hermes_cli.update_cmd._hermes_holder_subcommand`（用于识别Hermes命令行参数中的顶层子命令）。切勿自行实现令牌扫描逻辑。
- 标志集必须通过解析器生成（`_holder_value_flags()`函数会调用`build_top_level_parser()`函数），绝不能手动编写列表——否则会导致匹配规则出现偏差。
- 在进程扫描过程中，切勿完全排除其上层进程：当 `/update`命令作为gateway的子进程运行时，其上级gateway进程必须仍能被暂停机制识别到（参见#87594）。应排除交互式进程的上层关系，仅筛选出与gateway相关的上层进程。
- 匹配时应使用完整的命令行内容，仅在显示时才进行截断处理（参见#78089）。
- 在添加任何新的扫描规则之前，请先阅读#92091文档——目前gateway控制套接字已取代扫描机制成为主要的协调手段，而扫描功能仅作为旧进程或崩溃进程的备用方案。

## Skin引擎——皮肤可定制的内容

| 元素 | 皮肤键值 | 使用模块 |
|---|---|---|
| 横幅面板边框/标题/板块标题/暗色背景/内容区域 | `colors.banner_border`, `banner_title`, `banner_accent`, `banner_dim`, `banner_text` | `banner.py` |
| 响应框边框 | `colors.response_border` | `cli.py` |
| 旋转加载图标（等待状态/思考状态） | `spinner.waiting_faces`, `spinner.thinking_faces` | `display.py` |
| 旋转加载图标上的文字/翅膀（可选） | `spinner.thinking_verbs`, `spinner.wings` | `display.py` |
| 工具输出前缀/各工具专用表情符号 | `tool_prefix`, `tool_emojis` | `display.py` → `get_tool_emoji()` |
| 智能体名称/欢迎语/响应标签/提示符符号 | `branding.agent_name`, `welcome`, `response_label`, `prompt_symbol` | `banner.py`, `cli.py` |

内置皮肤（位于 `hermes_cli/skin_engine.py` 中的 `_BUILTIN_SKINS`）包括：`default`（经典金色/可爱风格）、`ares`（深红色/青铜色，配有自定义翅膀的旋转加载图标）、`mono`（灰度风格）以及 `slate`（冷蓝色风格）。可将内置皮肤以字典形式添加，格式为 `{"name", "description", "colors", "spinner", "branding", "tool_prefix"}`。用户自定义皮肤则保存在 `~/.hermes/skins/<名称>.yaml` 文件中，结构与内置皮肤相同，可通过 `/skin <名称>` 或 `display.skin: <名称>` 命令启用；完整的 YAML 模板可在 [皮肤与主题](../user-guide/features/skins.md) 用户指南中查看。

## 配置文件：多实例支持

Hermes 支持配置文件功能——即完全隔离的实例，每个实例都拥有独立的 `HERMES_HOME` 环境（用于存储配置、API 密钥、内存数据、会话信息、技能模块以及网关相关设置）。在 `hermes_cli/main.py` 中，`_apply_profile_override()` 函数会在任何模块被导入之前设定 `HERMES_HOME` 的值，因此所有调用 `get_hermes_home()` 的操作都会指向当前激活的配置文件。配置文件相关的操作均以 `HERMES_HOME` 为基准路径（`_get_profiles_root()` 函数返回的路径为 `Path.home() / ".hermes" / "profiles"`，而非 `get_hermes_home() / "profiles"`），正因如此，无论当前激活的是哪个配置文件，执行 `hermes -p coder profile list` 命令都能查看所有配置文件——这正是设计初衷。与配置文件使用相关的编码规范可见根目录下的 `AGENTS.md` 文件，而与密钥管理相关的多重规则则记载于 `gateway/AGENTS.md` 中。
