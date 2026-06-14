# 配置文件构建器 —— 原生仪表板式、功能完备的配置创建工具

状态：设计提案（尚未实现）  
作者：为 Teknium 撰写  
替代方案：PR #31781（prompt_toolkit 的 `hermes profile wizard`）

## 为何选择此方案而非 CLI 向导

PR #31781 在终端中添加了基于键盘操作的 `hermes profile wizard`。
但团队决定**不在 CLI 中实现**配置创建功能。  
仪表板已为配置所需的每个元素提供了成熟且独立的页面，而配置文件本质上就是一个 HERMES_HOME 目录——因此仪表板才是构建功能完备工具的理想平台，它还能复用现有的一切资源。

一个配置文件 = 一个完整的 `~/.hermes/profiles/<name>/` 目录，其中包含：
- `config.yaml` —— 存储 `model`/`provider`、`mcp_servers` 以及已启用的技能
- `skills/` —— 实际的 SKILL.md 文件（内置示例 + 可选技能 + 通过 hub 安装的技能）
- `.env` —— 密钥信息
- `SOUL.md` / `USER.md` —— 身份信息

因此，模型、MCP 和技能的按配置文件隔离功能是**原生支持的**——无需修改数据模型。目前的不足仅在于用户体验：当前的创建流程只是一个简单的模态窗口（包含名称、克隆选项、模型信息及描述），且只能在新配置文件创建完成后，通过访问其他页面并手动指定相关设置来添加技能/MCP。

## 现有资源（直接复用，无需重复开发）

| 元素 | 现有页面 | 现有 API | 是否支持按配置文件隔离？ |
|---|---|---|---|
| 名称/描述 | ProfilesPage 的创建模态窗口 | `POST /api/profiles` (`create_profile`) | 是（通过参数传递） |
| 模型+提供方 | ModelsPage | `_write_profile_model(profile_dir, …)` | 是 —— 支持覆盖 HERMES_HOME 设置，且已集成到创建接口中 |
| MCP | McpPage | `mcp_config._save_mcp_server` + `/api/mcp/catalog` | 是 —— 可通过覆盖 HERMES_HOME 设置实现隔离 |
| 技能（内置/可选） | SkillsPage | `GET /api/skills`, `/api/skills/toggle` | 是 —— 可通过配置文件写入设置 |
| 技能（hub 安装） | SkillsPage | `/api/skills/hub/search`, `/api/skills/hub/install` | **仅能通过子进程实现** —— 见缺陷 #1 |

## 在设计过程中发现的两个架构层面的问题

这些问题会直接影响实现方式，而不仅仅是界面优化。

### 缺陷 #1 —— hub 安装的技能无法使用 HERMES_HOME 覆盖设置

`tools/skills_hub.py` 在**模块导入阶段**就设置了 `SKILLS_DIR = HERMES_HOME / "skills"`。而上下文相关的 `set_hermes_home_override()` 函数仅能改变当前作用域内的设置，无法回溯修改已导入模块中的全局变量。因此，若试图为 hub 安装功能添加数据层封装，其写入操作将会针对仪表板*当前活跃的*配置文件，而非新创建的配置文件。

正确的解决方案是沿用现有的子进程机制：`_spawn_hermes_action` 函数会执行 `python -m hermes_cli.main <subcommand>`，而 `_apply_profile_override()` 函数则会在新的子进程导入时重新读取 `sys.argv` 参数。只需在命令前添加 `-p <profile>` 即可实现目标。

```python
_spawn_hermes_action(["-p", profile, "skills", "install", identifier], "skills-install")
```

一个新的子进程会从一开始就重新导入已绑定对应 `HERMES_HOME` 值的 `skills_hub`，因此 `SKILLS_DIR` 的路径将为 `<profile>/skills/`。这是该设计固有的特性。

### 第二个衔接点——hub 安装为异步操作，因此“创建”流程无法做到完全原子化

内置/可选技能的启用操作以及 MCP 配置写入属于**同步配置操作**，可包含在“创建”调用中。而 hub 安装则是通过分离式进程执行的长时间 git fetch 操作（`_spawn_hermes_action` 会立即返回进程 ID）。因此，“创建”流程如下：

1. `create_profile()` — 创建目录（同步操作）
2. 写入模型文件（同步操作，同时覆盖 `HERMES_HOME` 设置）
3. 写入选定的 MCP 服务器配置（同步操作，同时覆盖 `HERMES_HOME` 设置）
4. 启用/加载选定的内置及可选技能（同步操作）
5. 为每个 hub 技能启动 `hermes -p <profile> skills install <id>` 命令（异步操作，返回进程 ID）

在返回响应之前，步骤 1–4 的操作已被提交；步骤 5 会返回一系列操作进程 ID，界面会定期轮询这些 ID（其机制与当前 SkillsPage 的 hub 安装流程相同）。构建器中的“审核 → 创建”功能会返回 `{ok, name, path, hub_installs: [{id, pid}]}` 格式的数据，最终界面则会实时显示 hub 技能的安装进度。

## 建议的后端修改方案（规模较小，遵循现有设计模式）

对 `ProfileCreate` 函数及创建接口进行扩展——无需新增接口，也无需重写现有代码：

```python
class ProfileCreate(BaseModel):
    name: str
    clone_from: Optional[str] = None
    # Backward compatibility for older dashboard/desktop clients.
    clone_from_default: bool = False
    clone_all: bool = False
    no_skills: bool = False
    description: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    # NEW — all optional, all best-effort post-create (profile already exists)
    mcp_servers: List[MCPServerCreate] = []      # synchronous, HERMES_HOME override
    builtin_skills: List[str] = []               # synchronous enable/seed
    hub_skills: List[str] = []                   # async spawn, returns PIDs
```

该端点在创建完成后已会执行尽力而为的后续操作（如`seed_profile_skills`、`_write_profile_model`）。建议以相同方式再添加两个尽力而为的模块（MCP写入操作以及Hub技能生成操作）——由于配置目录已经存在，且用户之后可通过相应页面进行修复，因此这些操作中的任何一次失败都不应导致创建流程返回500错误。对于MCP写入操作，可参照`_write_profile_model`中的HERMES_HOME覆盖机制来实现（即使用`_write_profile_mcp_servers(profile_dir, servers)`）。

## 建议的前端实现——专用构建页面 `/profiles/new`

采用完整页面形式（而非狭小的模态框），分步骤进行操作，每一步均复用现有页面的组件与API，专门用于创建新配置文件：

```
① Identity   Name + Description (+ optional clone-from existing profile)
② Model      Provider + model picker  (reuse ModelsPage picker)
③ Skills     Tabs: Built-in · Optional · Hub-search
             multi-select; "Start from default bundle" preset button
④ MCPs       Tabs: Catalog browse · Manual add  (reuse McpPage form)
⑤ Review     Blueprint preview → Create
             → progress screen for async hub installs
```

在⑤之前，不会有任何数据被写入磁盘。

## 产品功能决策（需 Teknium 支持）

1. **技能默认值设置。** 新创建的配置文件会自动加载默认技能包。
   在配置构建器中，应让技能设置**替换**现有技能包（允许用户精确选择所需技能；
   同时提供“从默认技能包开始”的预设选项），还是仅用于**扩展**现有技能包？
   建议：采用替换模式，并设置预设按钮。

2. **独立页面与增强型模态框。** 是创建专用的 `/profiles/new` 页面
  （未来可进一步扩展功能，如 SOUL 编辑、多智能体集群管理），还是在 ProfilesPage 上使用更大的创建模态框？
   建议：使用专用页面——这更符合“功能全面/选项更多”的设计理念。

## 验证计划（开发完成后）

- 使用隔离的 HERMES_HOME 环境进行后端端到端测试：发送完整的创建请求数据
 （包括名称、模型、2 个 MCP 服务、3 个内置技能以及 1 个中心技能），并验证新配置文件的 config.yaml 文件中是否包含该模型信息与两个 MCP 服务配置，内置技能是否已启用，以及中心技能对应的进程 ID 是否已生成。若测试数据存在问题，不应导致创建操作返回 500 错误。
- 执行 `cd web && npm run build` 命令（注意 web/ 目录下暂未配置 JS 测试套件）。
- 执行针对性测试：`pytest tests/<web_server profile tests> -k profile_create`。
