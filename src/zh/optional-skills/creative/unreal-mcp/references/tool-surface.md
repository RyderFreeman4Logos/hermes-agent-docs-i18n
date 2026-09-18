# Unreal MCP — 工具界面参考手册

本文将详细介绍 Epic 所开发的嵌入编辑器中的 MCP 服务器是如何组织、展示及执行各类工具的，以及当内置工具不足时该如何扩展该界面。所有内容均基于 UE 5.8 的实验性插件（标识符为 `ModelContextProtocol`）编写；请注意不同引擎版本之间可能存在差异——实时生成的 `describe_toolset` 结构规范始终具有优先级。  

## 一句话概括架构

**Unreal MCP**插件在编辑器进程内部运行HTTP服务器（默认地址为`http://127.0.0.1:8000/mcp`，仅支持本地回环访问，无身份验证，仅使用HTTP与SSE协议——不支持标准输入/输出或WebSocket）。该插件虽实现了相应协议，但并未自带任何工具。这些工具来自**工具集**——即继承自`UToolsetDefinition`（C++）或`unreal.ToolsetDefinition`（Python）的类——它们会在启动时由**工具集注册表**子系统（与之关联的插件，会自动启用；该注册表本身也不包含任何工具集）进行收集。实际使用的工具存放在`Engine/Plugins/Experimental/Toolsets/`目录下的各领域专用插件中——其中最常用的的是**EditorToolset**（用于核心编辑器功能，支持Python与C++语言）——而**AllToolsets**则是一个单选框式的聚合插件，依赖于约21个工具集（数据来自5.8版本的`AllToolsets.uplugin`）：AIModule、AnimationAssistant、AutomationTest、ConfigSettings、Conversation、DataRegistry、DataflowAgent、Editor、GameFeatures、GameplayTags、GAS、MCPClient、Niagara、PCG、Physics、Plugin、SemanticSearch、SlateInspector、StateTree、UMG、WorldConditions。项目专用插件及游戏功能插件还可提供更多工具。Unreal MCP会将每个已注册的工具调用封装为一个个MCP工具。其执行过程是**串行化地在游戏线程上完成**的——每次仅处理一个工具调用，且在每个调用执行期间都会阻塞编辑器界面。

## 工具搜索模式（默认契约）

当“启用工具搜索”功能处于开启状态时（默认如此），`tools/list`命令会列出恰好三种元工具：

| 元工具 | 参数 | 返回值 |
|---|---|---|
| `list_toolsets` | — | 已注册的工具集名称及描述 |
| `describe_toolset` | 工具集名称 | 该工具集中每个工具的 JSON 模式 |
| `call_tool` | 工具集/工具名称 + 参数对象 | 同一轮次中该工具的返回结果 |

使用规范：

- `list_toolsets` 在每个会话中仅调用一次；仅在执行 `RefreshTools`、插件变更或重新连接后需再次调用。
- `describe_toolset` 需在首次使用任何工具集之前调用。参数名称、类型及必填字段均来自 JSON 模式，绝不能依赖记忆或本文档中的内容。
- 返回结果：原始结果会以 `{"result": ...}` 的格式返回（由 CVar `ModelContextProtocol.WrapPODToolResultsInObject` 控制，默认值为 true）。结构化结果则会根据字段级别的模式进行序列化。
- 错误信息会以工具调用错误的形式返回，并附带引擎端的错误提示——请仔细查看这些信息，它们通常会指出出问题的参数或缺失的资源。

在“即时展示模式”（即关闭“启用工具搜索”选项）下，每个工具都会被单独列出。在 Hermes 环境中，这意味着在会话开始时每个工具都会呈现为 `mcp_unreal_engine_<tool_name>` 的形式，而 `hermes mcp configure unreal-engine` 命令可用于筛选列表。随着注册工具集数量的增加，JSON 模式的数据量也会随之增长，因此工具开发者不应依赖即时展示模式——除非确实只需要展示极少的固定工具，否则应保持工具搜索模式。

## `call_tool` 调度机制（经 5.8 版实机验证）

这些内容是基于正在运行的 5.8 版服务器进行验证的；许多简单的客户端往往正是因为没有理解这些细节而出错。

- `list_toolsets` 函数返回的是**完整限定形式**的工具集名称——Python语言为 `editor_toolset.toolsets.scene.SceneTools`；C++语言则为 `EditorToolset.EditorAppToolset`。Epic的文档中使用的是“SceneTools”这一简写名，而注册表中存储的则是完整限定形式的名称。在 `describe_toolset` 函数以及 `call_tool` 函数的 `toolset_name` 参数中，必须原样使用这些完整限定名称。
- `tool_name` 参数必须为**简写形式**的名称（如 `get_current_level`、`CaptureViewport`）。即便 `describe_toolset` 函数能够显示完整限定形式的名称，若传入完整形式的工具名，仍会因“未知工具”而失败。
- `call_tool` 函数的参数格式为 `{"toolset_name": ..., "tool_name": ..., "arguments": {...}}`，函数会在同一轮处理中返回结果（HTTP响应会一直处于阻塞状态，直到游戏线程完成该调用）。
- **可选参数必须明确以 `null` 的形式传递**——若省略这些参数，将会出现“输入参数‘X’需要默认值”的错误。例如，`CaptureViewport` 函数的最简调用格式为 `{"captureTransform": null, "annotations": null, "bShowUI": false}`。
- **Schema中的 `required` 字段为严格限定**。尽管从语义上来看，`find_actors` 函数的 `name`、`tag`、`collision_channels` 参数是可选的，但该函数仍将其标记为必填项——若需表示“任意值”，可传入 `""` 或 `[]`。
- 在该反射层中，**属性名称采用驼峰式命名，并保留UE特有的`b`前缀**，例如：`bUseTemperature`、`bAtmosphereSunLight`、`fogDensity`、`bRealTimeCapture`、`mobility`。即便写成`useTemperature`也不会导致整个调用出错——系统会列出所有无法设置的属性名称（采用类似模式校验错误的方式；请仔细阅读错误信息，其中会明确指出具体的失败项以及完整的输入结构）。
- **对象引用在任何地方都以`{"refPath": "<软对象路径>"}`的形式传递**，无论是演员、类还是组件。类的引用格式为`/Script/Module.Class`（例如`/Script/Engine.PointLight`）；而演员的引用则是完整路径（如`/Temp/Untitled_1.Untitled_1:PersistentLevel.DirectionalLight_UAID_...`）。生成/查找工具会返回这些引用路径——可将其保存并重复使用。
- **`ObjectTools.set_properties`函数接收的是JSON格式的*字符串*作为`values`参数**，而非对象：正确格式为`{"instance": {"refPath": ...}, "values": "{\"intensity\": 10.0}"}`。`get_properties`函数同样会在`returnValue`中返回JSON字符串，需进行相应的双重编码/解码操作。
- 原始类型的返回结果会以`{"returnValue": ...}`的形式包裹在文本内容块中。

### HTTP数据传输行为（适用于原始客户端/调试场景）

- `initialize` → 返回纯 JSON 响应，并附带必须在其后的每个请求中都原样返回的 `Mcp-Session-Id` 标头；`notifications/initialized` → 返回状态码 202 且内容为空；`tools/call` → **`text/event-stream`**：只有在游戏线程处理完成之后，结果才会以 `event: message` + `data: <jsonrpc>` 的格式出现。若客户端将响应视为纯 JSON，则会读取到空内容。请始终发送 `Accept: application/json, text/event-stream`。

## 已发布的工具集

工具集列表取决于具体项目；实时服务器上的 `describe_toolset` 功能是获取架构信息的唯一权威来源。以下列出的核心工具集均基于 5.8 版本中的 EditorToolset 源代码进行验证（Python：`.../EditorToolset/Content/Python/editor_toolset/toolsets/`；C++：`EditorAppToolset.h`）。

**EditorToolset 插件（核心部分）、Python 工具集**（已在 5.8 版本上通过实时验证；其合格的前缀格式为 `editor_toolset.toolsets.<module>.<Class>`）：

| Toolset | Verified tools (subset) |
|---|---|
| `scene.SceneTools` | `load_level`, `get_current_level`, `find_actors` (by name/type/tag/bounds), `add_to_scene_from_class`, `add_to_scene_from_asset`, `remove_from_scene`, `save_actor`, `create_level_instance`, folders |
| `actor.ActorTools` | `get_label`/`set_label`, tags, `get_actor_transform`/`set_actor_transform` (`xform` fields optional = "don't change"), parenting, components |
| `primitive.PrimitiveTools` | `add_cube` (dimensions), `add_sphere` (radius), `add_cylinder`/`add_cone` (radius+height) — adds StaticMeshComponents with `local_transform` to a host actor: spawn `/Script/Engine.Actor`, then compose. The fastest blocking path, zero asset dependencies |
| `object.ObjectTools` | `list_properties` (returns full JSON schema of every property), `get_properties`/`set_properties` (JSON-string `values`), `reset_properties` (restore defaults — also your rollback), `get_class`, `search_subclasses` |
| `material_instance.MaterialInstanceTools` | `create`, `list_parameters`, `get/set_scalar_parameter`, `get/set_vector_parameter` |
| `asset.AssetTools` | `find_assets`, `load_asset`, `exists`, `save_assets`, `is_dirty`, `get_dependencies`/`get_referencers` (check before delete!), `delete`, `move`, `duplicate`, folders, `read_file`/`write_file` (project-scoped) |
| `blueprint.BlueprintTools` (+ dsl/layout/node) | Blueprint authoring |
| `material.MaterialTools`, `static_mesh.StaticMeshTools`, `texture.TextureTools`, `data_table.DataTableTools`, … | per-asset-type operations |
| `programmatic.ProgrammaticToolset` | **the batching escape hatch** — see below |

**`EditorToolset.EditorAppToolset`（C++，使用相同插件）——即智能体的“眼睛”**
（完整功能列表）：`CaptureViewport`、`CaptureEditorImage`、`CaptureAssetImage`、`GetCameraTransform`/`SetCameraTransform`、`GetSelectedActors`/`SelectActors`/`FocusOnActors`/`GetVisibleActors`、`WorldPosToScreenCoords`/`ScreenCoordsToWorld`、`GetSelectedAssets`/`SelectAssets`、`GetContentBrowserPath`/`SetContentBrowserPath`、`OpenEditorForAsset`、`GetOpenAssets`、`SearchCVars`、`StartPIE`/`StopPIE`/`IsPIERunning`。

`CaptureViewport`的详细参数（已验证）：参数为`{"captureTransform": <变换值或null>, "annotations": <配置值或null>, "bShowUI": false}`。该功能会返回Base64编码的PNG图像（需自行解码并保存），同时提供相机的位置、旋转角度及视野范围信息。`captureTransform`允许以任意视角进行拍摄，且无需移动用户的视图窗口——可将其视为虚拟相机使用。注释配置`{"gridSpacingCm": 500, "gridExtentCm": 3000, "gridHeight": <地面Z坐标>, "labelActors": true}`可用于叠加投影的地面网格及角色标记；**网格坐标单位为米**（世界坐标厘米值除以100）。建议在定位工作时使用带注释的截图，而在检查视觉效果时则使用无注释的清晰截图。

经实测确认可用的工具集包括：`ToolsetRegistry.AgentSkillToolset`、`EditorToolset.LogsToolset`（用于读取输出日志并设置详细程度——便于自我调试）、`SemanticSearchToolset`（支持向量搜索与BM25算法相结合的资产检索方式）、五个`NiagaraToolsets.NiagaraToolset_*`系列工具集、`PCGToolset`（含空间功能）、`UMGToolSet`、三个`GASToolsets.*`系列工具集、`AutomationTestToolset`、`ConfigSettingsToolset`（可根据预设架构读取/写入项目设置及编辑器偏好设置——用于访问默认路径、渲染设置等信息）、`SlateInspectorToolset`、`PluginToolset`，以及`animation_toolset.toolsets.sequencer.SequencerTools`及其相关的关键帧设置/控制绑定/大纲视图功能、`aimodule_toolset`中的行为树工具、`state_tree_toolset`中的状态树工具等。在已启用所有工具集的空白项目中，共计有67个工具集可用。

目前存在的缺陷是：没有用于网格建模的工具——可以生成/放置/实例化现有网格，但无法创建新的几何体。目前支持参数化几何体的方式是通过自定义Python工具集来调用**Geometry Script**功能（例如在`UDynamicMesh`中添加立方体/圆柱体/球体、执行布尔运算，之后通过“从网格创建新的静态网格资产”功能将结果导出为`SM_`格式的资产）。对于有机形状或雕刻过的网格，则需在Blender中建模后再导入。

首次使用时的操作建议：先调用`list_toolsets`列出所有工具集，接着针对计划使用的每个工具集调用`describe_toolset`获取其相关信息，并将这些配置信息保留在工作内存中，以便在当前会话中使用。

## ProgrammaticToolset——官方支持的批量处理方案

由于必须逐次调用接口，多步骤编辑操作在网络传输过程中会变得十分缓慢。为此，官方提供了`ProgrammaticToolset`解决方案（相关实现可在`programmatic.py`文件中查看）。

1. `get_execution_environment` — **必须首先调用的函数**（该工具的文档明确要求如此）；它会返回允许使用的模块、脚本限制以及使用说明。  
2. `execute_tool_script(script)` — 用于运行一个**沙箱隔离**的 Python 脚本，该脚本需定义 `run() -> dict` 函数。在脚本内部，可通过编程方式调用其他已注册的工具，并用逻辑将它们组合起来——整个循环只需一次 MCP 请求即可完成（例如：根据计算出的变换规则生成 20 个实体）。

关于沙箱的限制（来自官方文档）：仅允许导入 `json`、`math`、`datetime`、`copy`、`re`、`time` 这些模块；`open()` 函数只能用于项目内的路径；脚本在编辑器中以**事务范围**运行，便于撤销操作；这属于工具编排功能，而非通用 Python 代码——任意 `unreal.*` 相关的调用均不在其功能范围内。数据通过 `run()` 函数返回的字典形式提供。

当某个处理流程中的同类调用超过约 5 次时，应使用此函数；而对于一次性编辑操作，则建议直接使用 `call_tool` 函数。

## 项目智能体技能（AgentSkillToolset）

项目和插件可以注册**智能体技能**——即针对项目特定规范和工作流程设计的命名指令集（包括命名规则、文件夹结构以及标准的多步骤流程）。这类技能不会在 `list_toolsets` 的列表中显示，需通过 `call_tool` 函数来调用。

1. `AgentSkillToolset.ListSkills` → 已注册技能的名称与描述。  
2. 若有匹配的任务，可使用 `AgentSkillToolset.GetSkills` 获取完整操作指南，并严格遵循这些指南——项目专用技能的存在正是由于该项目的处理方式与常规方法不同，因此其优先级高于该技能的通用默认设置。  
在任何项目开始执行陌生任务时都应进行检查，而非仅一次即可。  

## 查看工作成果：截图与捕获图像  

无法查看视口的智能体就如同在黑暗中摸索。按推荐顺序如下：  
1. **`EditorAppToolset.CaptureViewport`**（已正式发布）——通过 MCP 以带相机元数据的 Base64 PNG 格式返回图像；支持在不干扰用户视图的前提下从任意视角进行捕获，同时还提供可选的标注层（世界空间坐标网格及角色标识），非常适合需要进行空间定位的工作。这是默认的验证工具。  
2. 当需要高于视口分辨率的图像时，可使用**控制台中的 `HighResShot` 功能或任何命令行工具**：执行 `HighResShot 3840x2160` 命令后，图像将保存至编辑器主机文件系统中的 `<Project>/Saved/Screenshots/<Platform>/` 目录；可通过 `vision_analyze` 在同一台机器上读取该文件。  
3. 对于其他特殊需求（例如使用 MRQ 质量设置进行带相机视角的角色框选捕获），可使用**自定义工具集**作为替代方案。  

在宣布某个里程碑已完成之前，务必先使用 `vision_analyze` 对捕获的图像进行分析，并根据任务要求进行最终审核。  

## 插件配置参考  

编辑器偏好设置 > 常规 > 模型上下文协议：

| 属性 | 默认值 | 备注 |
|---|---|---|
| 自动启动服务器 | `false` | 开启后可实现无缝会话体验 |
| 服务器端端口编号 | `8000` | 若存在冲突需进行修改；该数值也会同步出现在Hermes配置地址中 |
| 服务器URL路径 | `/mcp` | 规则相同 |
| 启用工具搜索功能 | `true` | 建议保持开启状态（详见上文） |

控制台命令（编辑器控制台，使用反引号输入）：

| 命令 | 功能 |
|---|---|
| `ModelContextProtocol.StartServer [端口]` | 启动服务器（可指定自定义端口） |
| `ModelContextProtocol.StopServer` | 停止服务器并关闭所有会话 |
| `ModelContextProtocol.RefreshTools` | 重新获取工具集提供方信息——可在编写代码/热重载/启用新游戏功能后执行 |
| `ModelContextProtocol.GenerateClientConfig <Client\|All>` | 生成客户端配置文件（适用于ClaudeCode/Cursor/VSCode/Gemini/Codex）——Hermes版本不使用此功能 |

用于预先配置编辑器启动参数的命令行标志：
`-ModelContextProtocolStartServer`（忽略用户设置，强制启动服务器），
`-ModelContextProtocolPort=N`。

控制台变量：

| CVar | 默认值 | 备注 |
|---|---|---|
| `ModelContextProtocol.WrapPODToolResultsInObject` | `true` | 原始结果会被封装为`{"result": ...}`格式 |
| `ModelContextProtocol.AudioResultOggFormat` | `false` | 音频结果将以OGG格式而非WAV格式输出 |
| `ModelContextProtocol.ProgressIntervalSeconds` | `1.0` | 进度状态更新的最小间隔时间（秒） |
| `ModelContextProtocol.PaginationPageSize` | `0` | 数值为0时表示不对列表结果进行分页处理 |
| `ModelContextProtocol.EnableAnalytics` | `true` | 启用Epic平台的性能监控功能 |
## 调试连接问题

- 在编辑器启动时，**输出日志**会记录绑定地址/端口/路径等信息——当服务器似乎不可用时，这是首要排查点。端口被占用或依赖项缺失等问题也会在此处显现。
- **日志详细程度**：可在编辑器控制台中输入 `Log LogModelContextProtocol Verbose`。
- **MCP Inspector**（通过命令 `npx @modelcontextprotocol/inspector` 运行，访问地址 `http://127.0.0.1:8000/mcp`，传输协议选择“Streamable HTTP”）会列出所有已声明的工具及其结构定义，并提供表单式调用方式——有助于区分是“服务器故障”还是“智能体调用方式有误”。
- **实时编码/创建内容之后**：已连接的客户端可能会保留过时的结构定义。此时可调用 `ModelContextProtocol.RefreshTools` 函数，如果结构定义仍显旧，则需要重新连接（开启新的 Hermes 会话）。

## 扩展功能：自定义工具集

若现有工具无法实现某项操作，正确的解决方案是创建自定义项目工具集——而非试图通过无关工具嵌入任意代码。Python 工具集具有优先级且支持热加载，因此建议优先使用。

### Python 工具集（推荐）

任何已启用的插件的 `Content/Python/` 目录（或项目自身的该目录）均可存放工具集模块；系统会在启动时自动发现这些模块。其结构形式与 Epic 公开的 `ActorTools` 类似：

```python
import unreal
import toolset_registry

@unreal.uclass()
class MySceneTools(unreal.ToolsetDefinition):
    """One-line toolset description — surfaces to the agent in list_toolsets."""

    @toolset_registry.tool_call
    @staticmethod
    def take_viewport_screenshot(filename: str, width: int, height: int) -> str:
        """Capture the active viewport to Saved/Screenshots.

        Args:
            filename: Base filename without extension.
            width: Output width in pixels.
            height: Output height in pixels.

        Returns:
            Absolute path the screenshot will be written to.
        """
        ...
```

重要的规范（这些规范决定了智能体所看到的架构）：

- 类上需添加 `@unreal.uclass()` 注解，并继承 `unreal.ToolsetDefinition`。
- 类的文档字符串即为工具集描述，需为智能体用户撰写。
- 每个需要公开的功能都需加上 `@toolset_registry.tool_call` 和 `@staticmethod` 注解；未加注解的函数将保持私有状态。
- 类型提示（如 `str`、`bool`、`list[str]`、`unreal.Actor` 以及数据类）用于生成 JSON Schema，而类似 Google 风格的文档字符串（包含 `Args:`/`Returns:` 格式）则用作参数描述，撰写时需充分考虑 API 的使用场景。
- 相较于返回文本形式的庞大工具，那些结构化、职责单一且具有明确返回类型的工具更为理想。数据应通过函数的返回值传递出去——`print()` 或 stdout 输出的内容应记录到 UE 日志中，而非通过 MCP 传回。

编写完成后，可在编辑器控制台中调用 `ModelContextProtocol.RefreshTools`，然后让 Hermes 重新执行 `list_toolsets` 操作。使用 Claude Code 的用户可以通过 Epic 提供的 `unreal-mcp` 插件包中的 `create-toolset` 功能快速搭建工具框架，上述规范同样适用。

### C++ 工具集

此类工具应基于`UToolsetDefinition`进行定义，将类标记为`UCLASS(BlueprintType, Hidden)`，并暴露带有`meta = (AICallable)`属性的静态`UFUNCTION`方法；相应的文档注释会同步反映到架构中。仅当Python无法访问相关API、需要反射出`USTRUCT`的结构信息，或函数调用的开销较为重要时才应使用此方式。若需忽略某个函数，可为其添加`meta = (AIIgnore)`属性。虽然“实时编码”功能能够同步更新已修改的函数体，但新增的`UFUNCTION`则需要重启整个编辑器才能生效。对于需要在运行时动态注册的工具，还存在直接注册的途径（即通过`IModelContextProtocolTool`与`IModelContextProtocolModule::AddTool()`实现）；此时由调用方负责后续的注销操作。

## 运行时构建与编译后构建

默认情况下，该服务器由编辑器托管，但并不局限于编辑器环境：通过`IModelContextProtocolModule::StartServer()`，运行时模块也可在编译后的构建环境中托管该服务器。不过，“工具集注册适配器”以及三个用于搜索工具的元工具仅能在编辑器环境中使用；而编译后构建中的工具则必须通过`AddTool()`方法显式注册，并且会立即被加载使用。目前没有任何正式发布的工具集会主动推送MCP资源与提示信息。

## 已知限制（5.8版本，实验性功能）

- 仅支持HTTP + SSE传输协议；监听器仅限回环地址使用；拒绝非回环地址的`Origin`请求头；不支持身份验证机制，因此无法在本地机器之外安全使用。
- 采用串行游戏线程执行模式：不支持并发调用，且每次调用都会阻塞编辑器界面。
- 按照Epic自身的分类，该功能尚处于开发阶段，相关API及数据格式可能会在未经通知的情况下发生变更。
- “实时编码”功能无法同步更新新定义的`UFUNCTION`。
