# 高级工作流（已在 UE 5.8 上实测验证）

除明确标注为“架构验证通过”外，此处所有内容均在正在运行的 5.8 版编辑器环境中执行。若实际行为与 Epic 的官方文档存在差异，本文件将记录服务器的实际运行情况。

## ProgrammaticToolset —— 在遵循串行规则的前提下实现批量操作

`editor_toolset.toolsets.programmatic.ProgrammaticToolset` 是在单次 MCP 请求中执行多项操作的官方推荐方式。由于仅涉及游戏线程上的**一次工具调用**，因此串行调用规则依然得到保障；实际上只是允许脚本在服务器端发起这些子调用。

验证通过的规范如下：

1. 在第一个脚本执行之前，每个会话仅需调用一次 `get_execution_environment`。该函数会返回 `instructions`（请务必仔细阅读，因其具有权威性）、`supported_modules` 以及 `language` 等信息。
2. `execute_tool_script` 函数的参数格式为 `{"script": "<python>"}`。脚本中必须定义 `run() -> Dict[str, Any]` 这一函数。
3. 在脚本内部，`execute_tool(tool_name, json_input)` 用于调用任何已注册的工具。`tool_name` 需要包含完整的工具路径（例如 `"editor_toolset.toolsets.primitive.PrimitiveTools.add_cube"`）——与顶层的 `call_tool` 不同，此处无需区分工具集和具体工具。`json_input` 应为 JSON **字符串**格式，需使用 `json.dumps` 函数生成。
4. `execute_tool` 函数会返回一个类似字典的对象，可通过 `["returnValue"]` 提取结果。若操作失败，该函数会抛出 `RuntimeError` 异常，无需手动进行错误检查。
5. 5.8 版本允许导入的模块仅为 `json`、`math`、`datetime`、`copy`、`re`、`time` 六个；其他任何模块均不可使用，包括 `unreal`、`os` 以及各类文件 I/O 相关模块。
6. 整个脚本的返回值会以 JSON 字符串的形式存储在 `returnValue` 中。

实测案例（已验证有效：可生成12列柱廊结构，包含36个组件，仅需1次请求即可完成，而按传统串行方式则需要37次调用）：

```python
import json, math

def add_cylinder(actor_ref, name, radius, height, x, y, z):
    return execute_tool(
        "editor_toolset.toolsets.primitive.PrimitiveTools.add_cylinder",
        json.dumps({"actor": actor_ref, "name": name, "radius": radius,
                    "height": height,
                    "local_transform": {"location": {"x": x, "y": y, "z": z}}}))

def run():
    spawn = execute_tool(
        "editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_class",
        json.dumps({"actor_type": {"refPath": "/Script/Engine.Actor"},
                    "name": "Colonnade",
                    "xform": {"location": {"x": 75800, "y": 84900, "z": 44300}}}))
    host = spawn["returnValue"]
    n, ring_r = 12, 900.0
    for i in range(n):
        a = 2.0 * math.pi * i / n
        add_cylinder(host, "Shaft_%02d" % i, 40, 360,
                     ring_r * math.cos(a), ring_r * math.sin(a), 210)
    return {"colonnade": host["refPath"], "columns": n}
```

## 何时使用该方案：当需要执行5次及以上相同类型的操作时（如放置环、网格散布、批量重命名、批量属性修改等）。**何时不宜使用**：在需要查看中间结果才能决定下一步操作的场景中——因为脚本无法在运行过程中向用户提问。

**可能出错的情况**：`print()`函数会将输出写入UE日志而非MCP返回值，此时应通过结果字典获取诊断信息。若脚本发生异常，则会以回溯信息作为工具错误提示。

## Blueprint编写——DSL循环

`editor_toolset.toolsets.blueprint.BlueprintTools`（包含53个工具）用于创建真正的Blueprint。其图结构采用s-expression DSL形式，与实时服务器交互后的工作流程如下：

1. **`create`** — `{"folder_path": "/Game/Blueprints", "asset_name": "BP_Spinner", "asset_type": {"refPath": "/Script/Engine.Actor"}}` → 返回Blueprint的引用路径（如`/Game/Blueprints/BP_Spinner.BP_Spinner`）。
2. **`list_graphs`** — 以冒号分隔的形式返回图结构的引用路径：`...BP_Spinner.BP_Spinner:EventGraph`, `...BP_Spinner.BP_Spinner:UserConstructionScript`。
3. **`get_graph_dsl_docs`** — 从实时服务器获取约9千字符的语法文档。在编写DSL之前应先阅读该文档，其中涵盖了`event`/`fn`、`bind`、`if`/`for`/`while`/`switch`、多执行延续块（如`(:then ...`)`、`(:CastFailed ...)`）、数据输出引脚自动生成的下划线变量以及带引号的引脚名称等内容。
4. **在编写DSL之前，先用`find_node_types`确定所有节点ID** — `{"graph": {"refPath": "<graph>"}, "type_id_filter": "MakeRotator", "context_pins": []}` → 可得到精确的节点ID。节点ID为用竖线分隔的类别路径，必须与实时注册表中的内容完全一致。经验证的常见错误包括：
   - 引擎事件使用K2显示名称：`EventTick`（带有`DeltaSeconds`参数）、`EventBeginPlay` — 若使用`(event Tick ...)`则会报错“AddEvent|Tick does not exist”。
   - 应使用`Math|Rotator|MakeRotator`，而非简写的`MakeRotator`。
   - 应使用`Utilities|Operators|Multiply`（通配符运算符），而非`Multiply_FloatFloat`。
   - 应使用`Transformation|AddActorLocalRotation`，而非`Utilities|Transformation|AddActorLocalRotation` — 文档示例中的类别前缀可能与实时注册表不一致，应以注册表为准。
   - 不存在`(self)`节点；目标对象是隐式的 — 对所属Actor的调用可直接省略`:self`。
5. **`write_graph_dsl`** — `{"graph": {"refPath": "<EventGraph>"}, "code": "<dsl>"}`。成功时返回`null`。若失败，则会抛出`AssertionError`，明确指出出错的节点及其所属结构 — 应逐个修复节点后再重新运行，否则错误会转移到下一个问题。
6. **`compile_blueprint`** — `{"blueprint": {"refPath": ...}, "warnings_as_errors": false}`。成功时返回`null`。
7. **生成实例** — 使用`SceneTools.add_to_scene_from_asset`，传入参数`{"asset_path": "/Game/Blueprints/BP_Spinner.BP_Spinner", ...}`。注意：该工具将`asset_path`视为普通字符串，而非`asset`引用路径对象 — 错误信息格式可作为判断依据（详见下文）。生成的Actor类名为`BP_Spinner_C`（即引用路径中显示的带下划线后缀的生成类名）。

经验证的端到端流程为：创建`BP_Spinner`，编写一个使Actor以90°/秒速度旋转的Tick处理函数（如`(event EventTick (DeltaSeconds) (Transformation|AddActorLocalRotation :DeltaRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (Utilities|Operators|Multiply DeltaSeconds 90.0))))`），成功编译后生成实例，最后通过`PrimitiveTools.add_cube`为该实例添加可见网格模型。

**变量、函数与调度器**：包括`add_variable`（传入`type_name`字符串）、`add_object_variable`/`add_struct_variable`、`add_function_graph` + `add_function_param`、`add_event_dispatcher`、`set_variable_replication` — 均遵循相同的引用路径规则。`read_graph_dsl`功能可将现有图结构转换回DSL格式，以便查看或编辑。

## 错误中包含架构信息是一流的发现机制

当某个调用缺少参数或参数输入错误时，服务器会在错误信息中返回该工具的完整输入架构。这种方式比重新运行`describe_toolset`更高效，且能准确反映用户实际调用的功能。已有两个经验证的案例表明该机制能有效解决问题：
- `add_to_scene_from_asset` — 概念上被定义为接受资产引用，但实际架构要求传入字符串类型的`asset_path`。
- `StartPIE` — 若传入空对象`{}`会失败，此时错误信息会提供完整的`PIESessionOptions`架构。

**规则**：遇到参数错误时，应首先阅读错误信息中的架构描述。

## PIE会话（基于架构验证）

`EditorAppToolset.StartPIE`需要一个`options`对象（类型为`FPIESessionOptions`）：
- `bSimulate`（必填）：`true`表示在编辑器内模拟运行 — 世界会进行帧更新，物理与AI系统也会运行，但不会生成玩家 Pawn；`false`表示标准 PIE 模式，会有玩家控制。
- `playMode`（必填）：可选值包括`PlayMode_InViewPort`、`PlayMode_InEditorFloating`、`PlayMode_Simulate`等。跨进程模式（如NewProcess、MobilePreview、VR、QuickLaunch）会自动降级为视口内模式 — 因为该工具需要进程内 PIE 模式才能实现基于委托的完成度跟踪。
- `warmupSeconds`（必填）：在引擎触发`PostPIEStarted`事件（即`BeginPlay`已执行）后，等待的额外稳定时间，之后才会返回结果。值为`0`表示 PIE 一启动就立即返回。
- `startTransform`（可选）：允许在特定变换位置而非PlayerStart点生成 Pawn或引用对象。

`IsPIERunning`函数仅返回布尔值。在 PIE 运行期间可通过检查运行状态（如Actor变换更新情况、使用LogsToolset读取日志）以及调用`StopPIE`来完成整个循环：启动模拟 → 检查状态/日志 → 停止 → 评估结果。

该机制支持的测试循环为：编译Blueprint → 启动 PIE 模拟 → 每几秒采样一次Actor的变换状态 → 确认Tick逻辑确实正在运行 → 停止 PIE。请记住注意事项15：PIE会修改世界状态，因此应在 PIE 会话开始前或结束后进行编辑器内的世界状态测量，而非在会话进行过程中。

## 序列器——支持140个工具的定向控制方案

`animation_toolset.toolsets.sequencer.SequencerTools`是规模最大的工具集（包含140个工具），采用“开放序列+隐式目标”模型：首先通过`create_level_sequence`/`open_sequence`/`get_focused_sequence`创建序列，之后大多数操作都针对当前聚焦的序列进行。

**功能映射表**（名称已通过`describe`函数验证，按前缀分组）：
- **结构管理**：`add_actors`（用于可控制的对象）、`add_spawnable_from_class` / `add_spawnable_from_instance`、`create_camera`（返回可直接使用的摄像机切换绑定），以及与绑定相关的创建、读取、删除操作（如`get_bindings`、`find_binding_by_name`、`remove_binding`、`rebind_component`、`fix_actor_references`）。
- **轨道/片段管理**：`add_track_to_binding` / `add_track_to_sequence`、`add_section`、`set_section_range`/`set_section_blend_type`及过渡效果设置、`set_camera_cut_binding`。
- **时间控制**：`set_playback_range`、`set_display_rate`、`set_tick_resolution`、`set_work_range`以及标记关键帧。
- **播放控制**：`play`、`pause`、`play_to`、`set_playhead_frame`、`force_evaluate`、`set_playback_speed`。
- **关键帧设置**功能位于对应的兄弟工具集`animation_toolset.toolsets.keyframing.SequencerKeyframingTools`中（包含22个工具）：从`get_channel_names`开始，到`add_key_float`/`add_key_bool`等关键帧添加函数，再到`get_keys`、`set_default_value`、`bake_channel_keys`以及曲线编辑控制功能。
- **烘焙/导入导出**：`bake_transform`、对应的兄弟工具集用于FBX等格式的导入导出、`copy_tracks`/`paste_tracks`。
- **运行时条件/自定义绑定/ControlRig**：还有专门的兄弟工具集分别处理这些功能（如`SequencerConditionTools`、`SequencerCustomBindingTools`、`SequencerControlRigTools`、`ControlRigTools`）。

最基础的影视制作流程框架为：`create_level_sequence` → `create_camera` → 为场景中的对象添加`add_actors` → 在帧A和帧B处为摄像机变换通道设置关键帧 → `set_playback_range` → `play` → 最后进行捕获与效果评估。

## 使用LogsToolset实现编辑器自我调试

`EditorToolset.LogsToolset`提供以下功能：`GetLogCategories`、`Get/SetVerbosity`、`GetLogEntries`。在任何操作失败或出现异常沉默时，无需猜测，可直接查看过滤到相应类别（如`LogBlueprint`、`LogNiagara`、`LogModelContextProtocol`等）的最近日志记录。此外，该工具还能用于查看ProgrammaticToolset脚本以及Python工具集内部代码产生的`print()`输出。

## 自动化测试

`AutomationTestToolset.AutomationTestToolset`提供以下功能：`DiscoverTests` / `ListTests` → `RunTests`或`RunTestsByFilter` → `GetTestStatus`（通过轮询方式获取状态 — 编辑器中的测试为异步执行） → `GetTestResults` → 如有必要则调用`StopTests`。这一流程类似持续集成流程，可用于在实时编辑器会话中“进行修改并验证是否出现问题”。

## 资产智能功能

- `SemanticSearchToolset`：提供`Search`功能（结合向量搜索与BM25算法对项目中的资产进行检索）以及`FindSimilar`功能 — 适用于“帮我找到类似生锈金属材质的资产”这类需求，无需再依赖`AssetTools.find_assets`的名称匹配功能。
- `StaticMeshTools`：提供`import_file`功能（用于导入外部网格模型）、`set_nanite_enabled`、`generate_lods`/`set_lod_thresholds`、`generate_convex_collisions`、`get_triangle_count`/`get_bounds`等功能 — 这些都是在导入资产后进行的优化处理。
- `ConfigSettingsToolset`：提供`ListContainers`/`ListCategories`/`ListSections` → `GetSectionSchema` → `SetSectionProperties`（可将设置保存到配置文件中）等功能。该工具可让用户无需手动编辑ini文件，即可访问项目设置与编辑器偏好设置中的渲染默认值、曝光默认值以及自动启动标志等配置。
- `ToolsetRegistry.AgentSkillToolset`：提供`ListSkills`/`GetSkills`/`CreateSkill`/`UpdateSkill`等功能 — 这些是嵌入在项目中的智能体技能，随.uproject文件一同交付。如果项目中存在此类技能，应首先列出它们；因为它们包含了项目特有的规则，其优先级高于此文档中的通用指导。

## 策略选择——决策表

| 场景 | 推荐方案 |
|---|---|
| 需要执行5次及以上相同类型的操作（如散布、批量编辑等） | 使用ProgrammaticToolset脚本 |
| 需处理游戏行为或事件逻辑 | 使用BlueprintTools DSL循环 |
| 需实现摄像机移动或随时间变化的动画 | 使用SequencerTools + KeyframingTools |
| 需确认功能在运行时是否正常工作 | 启动PIE模拟模式，再通过变换与日志采样进行验证 |
| 需查找类似X的资产 | 先使用SemanticSearch，再结合AssetTools搜索 |
| 导入的网格模型体积较大 | 使用StaticMeshTools的nanite/LOD/碰撞优化功能 |
| 需修改编辑器或项目设置 | 使用ConfigSettingsToolset |
| 出现任何静默失败的错误 | 使用LogsToolset的GetLogEntries功能查看日志 |
| 项目拥有自定义智能体技能 | 先使用AgentSkillToolset检查 |
