# Unreal MCP — 工具接口参考文档

Epic 将编辑器内置的 MCP 服务器如何组织、展示并执行工具，以及当现有工具不足时如何扩展该接口。所有内容均基于 UE 5.8 的实验性插件（ID 为 `ModelContextProtocol`）；不同引擎版本之间可能存在差异——实时生成的 `describe_toolset` 架构始终优先于此文件。

## 一句话架构概述

**Unreal MCP** 插件在编辑器进程内部运行 HTTP 服务器（默认地址为 `http://127.0.0.1:8000/mcp`，仅支持回环连接，无身份验证，仅使用 HTTP + SSE 协议——不支持标准输入/输出或 WebSocket）。该插件实现了 MCP 协议，但本身不提供任何工具。工具实际上来自 **Toolset**——即派生自 `UToolsetDefinition`（C++）或 `unreal.ToolsetDefinition`（Python）的类——这些 Toolset 会在启动时由 **Toolset Registry** 子系统收集（该子系统为独立插件，会自动启用；但注册表本身也不包含任何 Toolset）。已发布的工具存储在 `Engine/Plugins/Experimental/Toolsets/` 目录下的各领域专用插件中——其中最常用的是 **EditorToolset**（处理核心编辑器工具，支持 Python 和 C++）——而 **AllToolsets** 则是一个单选框形式的聚合插件，可整合约 21 个 Toolset（信息来自 5.8 版本的 `AllToolsets.uplugin`）：AIModule、AnimationAssistant、AutomationTest、ConfigSettings、Conversation、DataRegistry、DataflowAgent、Editor、GameFeatures、GameplayTags、GAS、MCPClient、Niagara、PCG、Physics、Plugin、SemanticSearch、SlateInspector、StateTree、UMG、WorldConditions。项目专用插件和游戏功能插件还可提供更多工具。Unreal MCP 会将每个已注册的工具调用封装为 MCP Tool。执行过程是**串行化到游戏线程上**的——每次仅处理一个工具调用，且每个调用执行期间都会阻塞编辑器界面。

## 工具搜索模式（默认模式）

当 `Enable Tool Search` 开启时（默认状态），`tools/list` 会展示三种元工具：

| 元工具 | 参数 | 返回值 |
|---|---|---|
| `list_toolsets` | — | 已注册的 Toolset 名称及描述 |
| `describe_toolset` | Toolset 名称 | 该 Toolset 中每个工具的 JSON 架构 |
| `call_tool` | Toolset/工具名称 + 参数对象 | 该工具的返回结果，与调用同一次响应返回 |

使用规范：

- `list_toolsets` 每个会话仅调用一次；仅在执行 `RefreshTools`、插件更新或重新连接后需再次调用。
- 使用任何 Toolset 前需先调用 `describe_toolset`。参数名称、类型及必填字段均来自架构定义——绝不能依赖内存或此文件中的信息。
- 返回结果：原始结果会以 `{"result": ...}` 的格式返回（CVar `ModelContextProtocol.WrapPODToolResultsInObject` 默认值为 true）。结构化结果则会按照字段级别的架构进行序列化。
- 错误信息会以工具调用错误的形式返回，并附带引擎端的错误消息——请仔细阅读这些信息，其中通常会指出出问题的参数或缺失的资产。

在“即时模式”下（即 `Enable Tool Search` 关闭），每个工具都会被单独展示。在 Hermes 环境中，这意味着在会话开始时每个工具都会变为 `mcp_unreal_engine_<tool_name>` 的形式，而 `hermes mcp configure unreal-engine` 命令可用于精简该列表。随着更多 Toolset 的注册，架构数据量也会随之增加，因此工具开发者不应依赖即时模式展示工具——除非确实需要非常有限的固定工具集，否则应始终使用工具搜索模式。

## `call_tool` 调度规则（基于 5.8 版本实测）

这些规则是基于正在运行的 5.8 版服务器验证的；许多简单的客户端往往因不了解这些规则而出错：

- `list_toolsets` 返回的是**完全限定形式的** Toolset 名称——Python 代码中为 `editor_toolset.toolsets.scene.SceneTools`；C++ 代码中为 `EditorToolset.EditorAppToolset`。Epic 的文档中使用的是“SceneTools”这样的简写形式，但注册表中则使用完全限定的名称。在 `describe_toolset` 以及 `call_tool` 的 `toolset_name` 参数中，必须直接使用这些完全限定的名称。
- `tool_name` 必须是**简写形式**的名称（如 `get_current_level`、`CaptureViewport`）。即使 `describe_toolset` 显示的是完全限定的名称，若传入完整形式的工具名称，也会因“未知工具”而失败。
- `call_tool` 的参数格式为 `{"toolset_name": ..., "tool_name": ..., "arguments": {...}}`；结果会在同一响应轮次中返回（HTTP 响应会一直阻塞，直到游戏线程完成该调用）。
- **`TOptional` 类型的参数必须明确以 `null` 的形式传递**——若省略这些参数，系统会报错，提示“输入参数 ‘X’ 需要默认值”。例如，`CaptureViewport` 的最小调用格式为 `{"captureTransform": null, "annotations": null, "bShowUI": false}`。
- **架构定义中的 `required` 字段为严格必填**。`find_actors` 函数虽然从语义上来看某些字段是可选的，但它仍会将 `name`、`tag`、`collision_channels` 标记为必填项——若需表示“任意值”，则应传入 `""` 或 `[]`。
- 在此反射层中，属性名称采用驼峰命名法，且保留 UE 的 `b` 前缀：如 `bUseTemperature`、`bAtmosphereSunLight`、`fogDensity`、`bRealTimeCapture`、`mobility`。若使用 `useTemperature` 这种形式命名，调用不会出错——响应中会列出所有无法设置的属性（采用与架构错误类似的格式；请仔细阅读错误信息，其中会明确列出所有失败项及完整的输入架构）。
- 对象引用在任何地方都会以 `{"refPath": "<软对象路径>"}` 的格式传递（适用于角色、类、组件等）。类引用使用 `/Script/Module.Class` 的格式（例如 `/Script/Engine.PointLight`）；角色引用则为完整路径（如 `/Temp/Untitled_1.Untitled_1:PersistentLevel.DirectionalLight_UAID_...`）。生成或查找工具时都会返回 refPath，可将其捕获并重复使用。
- `ObjectTools.set_properties` 方法的 `values` 参数应为 JSON *字符串* 形式，而非对象格式：正确格式为 `{"instance": {"refPath": ...}, "values": "{\"intensity": 10.0}"}`。`get_properties` 方法同样会在 `returnValue` 中返回 JSON 字符串。因此需要进行双重编码/解码操作。
- 原始结果会以 `{"returnValue": ...}` 的格式包含在文本内容块中。

### HTTP 数据传输行为（适用于原始客户端/调试场景）

- `initialize` 请求的响应为纯 JSON 格式，同时包含一个 `Mcp-Session-Id` 标头，后续所有请求都必须重复该标头；`notifications/initialized` 请求的响应为 202 状态码且内容为空；`tools/call` 请求的响应格式为 **`text/event-stream`**：只有当游戏线程完成调用后，才会以 `event: message` + `data: <jsonrpc>` 的格式返回结果。若将响应视为纯 JSON 格式处理的客户端，会读取到空内容。请始终在请求头中设置 `Accept: application/json, text/event-stream`。

## 已发布的 Toolset 列表

Toolset 的列表取决于具体项目；实时服务器上提供的 `describe_toolset` 输出是架构定义的唯一权威来源。以下列出的核心工具集已基于 5.8 版本中的 EditorToolset 源代码进行验证（Python 代码位于 `.../EditorToolset/Content/Python/editor_toolset/toolsets/`，C++ 代码位于 `EditorAppToolset.h`）。

**EditorToolset 插件（核心部分），以及 Python 版 Toolset**（已在 5.8 版本上通过实测验证；其命名格式为 `editor_toolset.toolsets.<模块>.<类>`）：

| Toolset | 已验证的工具（子集） |
|---|---|
| `scene.SceneTools` | `load_level`、`get_current_level`、`find_actors`（可按名称/类型/标签/边界查找）、`add_to_scene_from_class`、`add_to_scene_from_asset`、`remove_from_scene`、`save_actor`、`create_level_instance`，以及相关文件夹功能 |
| `actor.ActorTools` | `get_label`/`set_label`、标签管理、`get_actor_transform`/`set_actor_transform`（`xform` 字段若设置为该值则表示“无需修改”）、父子关系设置、组件管理功能 |
| `primitive.PrimitiveTools` | `add_cube`（可指定尺寸）、`add_sphere`（可指定半径）、`add_cylinder`/`add_cone`（可指定半径和高度）——这些函数会将带有 `local_transform` 属性的 StaticMeshComponents 添加到宿主角色上：首先创建 `/Script/Engine.Actor` 对象，然后再组合相关组件。这是最快的调用方式，且不依赖任何资产文件 |
| `object.ObjectTools` | `list_properties`（返回所有属性的完整 JSON 架构）、`get_properties`/`set_properties`（参数为 JSON 字符串格式）、`reset_properties`（恢复默认值，也可用于回滚操作）、`get_class`、`search_subclasses` 功能 |
| `material_instance.MaterialInstanceTools` | `create`、`list_parameters`、`get/set_scalar_parameter`、`get/set_vector_parameter` 功能 |
| `asset.AssetTools` | `find_assets`、`load_asset`、`exists`、`save_assets`、`is_dirty`、`get_dependencies`/`get_referencers`（删除资产前请先检查依赖关系！）、`delete`、`move`、`duplicate` 功能，以及相关文件夹功能；还包括 `read_file`/`write_file` 功能（仅限项目内部文件操作） |
| `blueprint.BlueprintTools`（还包含 DSL/布局/节点相关功能） | 用于蓝图编写 |
| `material.MaterialTools`、`static_mesh.StaticMeshTools`、`texture.TextureTools`、`data_table.DataTableTools` 等 | 针对不同资产类型的操作功能 |
| `programmatic.ProgrammaticToolset` | **批量操作的解决方案**——详情见下文 |

**EditorToolset.EditorAppToolset**（C++ 语言，属于同一插件）——即代理程序可使用的所有工具的完整列表：`CaptureViewport`、`CaptureEditorImage`、`CaptureAssetImage`、`GetCameraTransform`/`SetCameraTransform`、`GetSelectedActors`/`SelectActors`/`FocusOnActors`/`GetVisibleActors`、`WorldPosToScreenCoords`/`ScreenCoordsToWorld`、`GetSelectedAssets`/`SelectAssets`、`GetContentBrowserPath`/`SetContentBrowserPath`、`OpenEditorForAsset`、`GetOpenAssets`、`SearchCVars`、`StartPIE`/`StopPIE`/`IsPIERunning`。

`CaptureViewport` 的具体参数格式（已通过实测验证）为：参数对象 `{ "captureTransform": <变换矩阵或 null> , "annotations": <配置对象或 null> , "bShowUI": false }`。该函数会返回编码后的 PNG 图像文件（需自行解码并保存），同时还会提供相机的位置、旋转角度和视野范围信息。`captureTransform` 功能允许在不移动用户视口的情况下从任意角度进行拍摄——非常适合用作虚拟摄像机。注释配置对象 `{ "gridSpacingCm": 500, "gridExtentCm": 3000, "gridHeight": <地面高度值> , "labelActors": true }` 可用于在拍摄画面中叠加投影的地面网格以及角色标记；**网格坐标单位为米**（即世界坐标厘米值除以 100）。建议使用带有注释的拍摄结果进行场景定位，而使用无注释的结果则可用于最终效果检查。

此外，经实测确认还存在以下 Toolset：`ToolsetRegistry.AgentSkillToolset`、`EditorToolset.LogsToolset`（可用于读取输出日志并设置日志详细程度——非常便于自我调试）、`SemanticSearchToolset`（支持向量搜索与 BM25 算法相结合的资产搜索功能）、五个 `NiagaraToolsets.NiagaraToolset_*` 组、`PCGToolset`（还包含 Spatial 相关功能）、`UMGToolSet`、三个 `GASToolsets.*` 组、`AutomationTestToolset`、`ConfigSettingsToolset`（可根据架构定义读取/写入项目设置及编辑器偏好设置——这些设置决定了各种参数的默认值、渲染设置等）、`SlateInspectorToolset`、`PluginToolset`、`animation_toolset.toolsets.sequencer.SequencerTools` 及其关键帧设置/控制绑定/大纲视图相关功能、`aimodule_toolset` 的 BehaviorTreeTools 功能、`state_tree_toolset` 的 StateTreeTools 功能，等等——在启用了 AllToolsets 的空白项目中，总共有 67 个 Toolset。

目前已知的一个缺失点是：该系统不支持网格建模工具——可以生成/放置/实例化现有的网格模型，但无法用于创建新的几何体。目前支持的参数化几何体创建方式是使用自定义的 Python Toolset，该 Toolset 会调用 **Geometry Script** 函数（针对 `UDynamicMesh` 对象，可通过该函数添加立方体、圆柱体、球体等几何体，或执行布尔运算操作，之后再通过“Create New Static Mesh Asset from Mesh”函数将结果烘焙为 SM_格式的资产）。对于有机形状或手工雕刻的网格模型，则需要在 Blender 中进行建模（可通过 `blender-mcp` 技能实现），然后再导入到项目中。

首次使用该系统时的建议操作流程为：先调用 `list_toolsets` 查看所有 Toolset，然后针对计划使用的每个 Toolset 调用 `describe_toolset` 获取其架构定义，并将这些架构信息保留在内存中，以便在当前会话中使用。

## ProgrammaticToolset —— 官方支持的批量操作方案

由于必须逐个调用工具的规则，多步骤编辑操作在网络传输过程中会显得效率极低。为此，官方提供了 `ProgrammaticToolset` 作为解决方案（其相关实现位于 `programmatic.py` 文件中）：1. `get_execution_environment` — **必须首先调用的函数**（工具本身的文档也要求如此）；它会返回允许使用的模块、脚本约束以及使用说明。  
2. `execute_tool_script(script)` — 运行一个**沙箱隔离**的 Python 脚本，该脚本需定义 `run() -> dict` 函数。在脚本内部，可以通过编程方式调用其他已注册的工具，并用逻辑将它们整合起来——整个循环仅需一次 MCP 请求即可完成（例如：生成 20 个带有计算后变换参数的智能体）。

关于沙箱的限制（来自官方文档）：仅允许导入 `json`、`math`、`datetime`、`copy`、`re`、`time` 这些模块；`open()` 函数只能用于项目内的路径；脚本在编辑器中以**事务范围**形式运行，便于撤销操作；这属于工具编排功能，而非通用 Python 环境——任意 `unreal.*` 相关的调用均不在功能规范之内。数据通过 `run()` 函数返回的字典形式给出。

当某个处理流程中的同类调用超过约 5 次时，应使用此方法；而一次性简单编辑则仍建议直接使用 `call_tool` 函数。

## 项目专用技能（AgentSkillToolset）

项目和插件可以注册**项目专用技能**——即针对特定项目规范和工作流程（如命名规则、文件夹结构、标准的多步骤流程）设计的指令集合。这类技能不会在 `list_toolsets` 的列表中显示，需通过 `call_tool` 函数来调用：

1. `AgentSkillToolset.ListSkills` → 显示已注册技能的名称及描述。  
2. 若有匹配当前任务的技能，则调用 `AgentSkillToolset.GetSkills` 获取完整的操作指南，随后严格遵循这些指南执行——项目专用技能的存在正是为了弥补项目流程与常规流程的差异，其优先级高于通用技能的默认设置。

在任何项目中开始处理不熟悉的任务时，都应先检查这些技能，而不仅仅是一次性查看。

## 查看工作成果：截图与抓图

如果智能体无法查看视图窗口，就如同在盲中操作。推荐按以下顺序选择方法：

1. **`EditorAppToolset.CaptureViewport`**（已确认可用）——通过 MCP 以 Base64 PNG 格式返回包含相机元数据的图像；支持在不干扰用户视图窗口的情况下，从任意视角进行抓图；同时还提供可选的标注功能（世界空间坐标网格及智能体标识），便于进行空间定位相关的操作。这是默认的验证工具。  
2. 当需要高于视图窗口分辨率的图像时，可使用**控制台中的 `HighResShot` 命令**（通过任意控制台/执行工具调用）：`HighResShot 3840x2160` 会将图像保存到编辑器主机文件系统中的 `<Project>/Saved/Screenshots/<Platform>/` 目录下；可通过 `vision_analyze` 命令在同一台机器上读取该文件。  
3. 对于其他特殊需求（例如使用 MRQ 质量设置进行带有相机视角的智能体抓图），可使用**自定义工具集**作为解决方案。

在宣布某个任务已完成之前，务必先使用 `vision_analyze` 对抓取的图像进行审核，并根据需求进行艺术指导调整。

## 插件配置参考

编辑器偏好设置 > 常规 > Model Context Protocol：

| 属性 | 默认值 | 备注 |
|---|---|---|
| Auto Start Server | `false` | 开启后可实现更流畅的会话体验 |
| Server Port Number | `8000` | 若出现端口冲突可更改此值；Hermes 配置地址中也需同步修改 |
| Server URL Path | `/mcp` | 与上述路径相同 |
| Enable Tool Search | `true` | 建议保持开启状态（见上文） |

控制台命令（编辑器控制台，使用反引号输入）：

| 命令 | 功能 |
|---|---|
| `ModelContextProtocol.StartServer [port]` | 启动服务器（可指定端口） |
| `ModelContextProtocol.StopServer` | 停止服务器并关闭所有会话 |
| `ModelContextProtocol.RefreshTools` | 重新查询工具集提供方——可在编写代码、热重载或激活游戏功能后执行 |
| `ModelContextProtocol.GenerateClientConfig <Client\|All>` | 生成客户端配置文件（ClaudeCode/Cursor/VSCode/Gemini/Codex 等格式）——Hermes 不使用此功能 |

用于预先配置编辑器启动参数的命令行标志：`-ModelContextProtocolStartServer`（忽略偏好设置强制启动），`-ModelContextProtocolPort=N`。

控制台变量：

| CVar | 默认值 | 备注 |
|---|---|---|
| `ModelContextProtocol.WrapPODToolResultsInObject` | `true` | 将原始结果封装在 `{"result": ...}` 对象中 |
| `ModelContextProtocol.AudioResultOggFormat` | `false` | 音频结果以 OGG 格式而非 WAV 格式输出 |
| `ModelContextProtocol.ProgressIntervalSeconds` | `1.0` | 进度更新的最小间隔时间（秒） |
| `ModelContextProtocol.PaginationPageSize` | `0` | 0 表示不对列表结果进行分页处理 |
| `ModelContextProtocol.EnableAnalytics` | `true` | 启用 Epic 的遥测功能 |

## 调试连接问题

- 编辑器启动时的**输出日志**会记录服务器的地址、端口和路径——当服务器似乎不可用时，首先应查看此处；端口被占用或依赖项缺失等问题也会在此处显示。  
- **日志详细程度**：可在编辑器控制台输入 `Log LogModelContextProtocol Verbose` 来调整。  
- **MCP Inspector**（通过命令 `npx @modelcontextprotocol/inspector`，访问地址 `http://127.0.0.1:8000/mcp`，传输协议选择“Streamable HTTP”）可以列出所有已公布的工具及其结构定义，并提供基于表单的调用方式——有助于区分是“服务器故障”还是“智能体调用方式有误”。  
- **在实时编码/编写代码之后**：已连接的客户端可能会持有过时的工具结构定义。此时可先执行 `ModelContextProtocol.RefreshTools`，如果结构定义仍显旧，则需要重新连接（开启新的 Hermes 会话）。

## 扩展功能：自定义工具集

当现有工具无法满足某些操作需求时，正确的做法是创建项目专用工具集——而非试图通过无关工具来嵌入任意代码。Python 工具集具有优先级且支持热加载，因此建议优先使用此类工具集。

### Python 工具集（推荐）

任何已启用的插件的 `Content/Python/` 目录（或项目自身的该目录）都可以存放工具集模块；系统会在启动时自动发现这些模块。其结构与 Epic 提供的 `ActorTools` 类似：

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

**关键规范（这些规范决定了代理所看到的架构）：**

- 在类上使用 `@unreal.uclass()`，并继承 `unreal.ToolsetDefinition`。
- 类的文档字符串即为工具集描述，需为代理使用者撰写。
- 每个需要公开的函数需加上 `@toolset_registry.tool_call` 和 `@staticmethod` 标签；未加装饰器的函数将保持私有状态。
- 类型提示（如 `str`、`bool`、`list[str]`、`unreal.Actor`、dataclasses）用于生成 JSON Schema，而类似 Google 风格的文档字符串（`Args:`/`Returns:`）则用作参数描述，撰写时需充分考虑 API 的使用场景。
- 相较于返回文本的大型工具，那些结构化返回值、职责单一的小型工具更为理想。数据应通过函数的 RETURN VALUE 传递出去——`print()` 或 stdout 的输出会进入 UE 日志系统，而非通过 MCP 传回。

编写完成后，可在编辑器控制台中调用 `ModelContextProtocol.RefreshTools`，然后让 Hermes 重新执行 `list_toolsets` 操作。使用 Claude Code 的用户可通过 Epic 提供的 `unreal-mcp` 插件包中的 `create-toolset` 技能快速搭建工具框架，上述规范同样适用。

### C++ 工具集

此类工具需基于 `UToolsetDefinition` 继承，将类标记为 `UCLASS(BlueprintType, Hidden)`，并公开带有 `meta = (AICallable)` 标签的静态 `UFUNCTION` 方法；文档注释会同步反映到架构中。仅在 Python 无法访问该 API、需要反射生成的 `USTRUCT` 签名，或 Python 边界处理成本过高时才使用此方式。若需隐藏某个函数，可使用 `meta = (AIIgnore)` 标签。Live Coding 能够即时同步已修改的函数体，但新增的 `UFUNCTION` 需要重启整个编辑器。对于需要在运行时动态注册的工具，还存在直接注册路径（`IModelContextProtocolTool` + `IModelContextProtocolModule::AddTool()`），由调用方负责后续的注销操作。

## 运行时与编译后构建

默认情况下，服务器由编辑器托管，但并不局限于编辑器环境：运行时模块可通过 `IModelContextProtocolModule::StartServer()` 在编译后的构建中运行服务器。不过，工具集注册适配器以及三个用于搜索工具的元工具仅能在编辑器中使用；编译后的工具必须通过 `AddTool()` 显式注册，并会被主动公开。目前没有任何正式发布的工具集会公开 MCP 资源和提示信息。

## 已知限制（5.8 版，实验性功能）

- 仅支持 HTTP + SSE 传输方式；监听器仅限回环地址使用，非回环地址的 `Origin` 头部会被拒绝；没有认证层，因此无法在本地机器之外安全使用。
- 采用串行游戏线程执行模式：不支持并发调用，每次调用都会阻塞编辑器界面。
- 根据 Epic 的自身评估，该功能尚不完整；相关 API 和数据格式可能会在未经通知的情况下发生变化。
- Live Coding 无法同步新增的 `UFUNCTION` 声明。
