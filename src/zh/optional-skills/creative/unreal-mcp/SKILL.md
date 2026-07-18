---
name: unreal-mcp
description: "Use when the user wants to do anything in Unreal Engine through Epic's official editor-embedded MCP server (catalog entry: unreal-engine) — build/light/populate scenes, place and transform actors, author Blueprints, animate with Sequencer, create material instances, frame cameras, take screenshots, render, import assets, run PIE test sessions and automation tests, or automate the editor end-to-end from plain-English prompts with no Unreal knowledge required. Covers the tool-search discovery walk (list_toolsets/describe_toolset/call_tool), serial game-thread call discipline, ProgrammaticToolset batching, the Blueprint graph DSL loop, scene-craft numbers (physical light units, exposure, scale conventions), complete build recipes, save/undo hygiene, and extending the tool surface with custom Python toolsets."
version: 1.0.0
requires: Unreal Editor 5.8+ with the Unreal MCP plugin enabled and its server running
author: Hermes Agent
license: MIT
tags: [unreal, unreal-engine, ue5, 3d, mcp, scenes, cinematics, lighting, gamedev]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [unreal, unreal-engine, ue5, 3d, mcp, scenes, cinematics, lighting, gamedev]
    related_skills: [blender-mcp]
---

# Unreal Engine MCP 技能

这是 Hermes MCP 目录中 `unreal-engine` 条目对应的配套技能。MCP 服务器（Epic 官方开发的实验性“Unreal MCP”插件，内部编号为 `ModelContextProtocol`）在 Unreal Editor 进程内部运行，将编辑器功能以类型化工具的形式呈现出来。本技能旨在指导用户如何高效地使用该服务器：包括探索可用的工具界面、安全地顺序调用工具、将通俗的描述转化为实际效果出色的场景，以及通过视觉方式验证成果。用户只需启动编辑器，便无需再直接操作编辑器本身。

## 适用场景

当用户需要在 Unreal Engine 中完成各类任务时即可使用此技能：构建或设计关卡、生成/移动/删除游戏对象、设置光照与氛围、创建或调整材质实例、构图拍摄、截取屏幕截图或渲染图像、导入资源、查看场景或界面、运行自动化测试，或是为编辑器编写脚本。它既适用于单一操作（如“将太阳设置为黄金时刻效果”），也适用于复杂的多步骤项目（如“为我创建一个带有营火的氛围浓郁的森林空地，并渲染一张图片”）。

**不适用于**：DCC 风格的网格建模/雕刻（请使用 `blender-mcp` 并导入结果），也不适用于编辑 Unreal C++ 项目源代码（那是常规的代码编写工作——请使用终端；本技能针对的是实时编辑器环境）。

## 先决条件

需按以下顺序完成两部分的准备：在 Hermes 连接之前，必须先启动编辑器端。

### 编辑器端的一次性设置

1. 使用 **Unreal Editor 5.8+** 版本，并打开一个项目。（macOS 系统需完整安装 Xcode 并接受其许可协议——若未安装，编辑器首次启动时会退出；详见注意事项。）
2. 进入 **编辑 > 插件**，启用 **Unreal MCP**（其依赖的 Toolset Registry 会自动被启用）。系统提示时请重启编辑器。
3. 类型化工具集与服务器是分开提供的：请在同一个插件管理界面中启用 **AllToolsets** 插件。Unreal MCP 本身并不包含任何工具——AllToolsets 才提供了已打包的工具集（如 SceneTools、ActorTools、MaterialInstanceTools、ObjectTools 等）；若跳过此步骤，虽然服务器可以连接，但智能体将没有可调用的工具。
4. 进入 **编辑 > 编辑器偏好设置 > 常规 > Model Context Protocol**，启用 **自动启动服务器**。默认绑定地址为 `http://127.0.0.1:8000/mcp`（端口/路径可在同一界面中配置；服务器名称为 `unreal-mcp`）。如需手动启动，则在编辑器控制台中输入 `ModelContextProtocol.StartServer`（使用反引号键）。

### Hermes 端的一次性设置

执行命令：`hermes mcp install unreal-engine`

该命令会创建一个指向 `http://127.0.0.1:8000/mcp` 的 `mcp_servers.unreal-engine` HTTP 条目，并向实时运行的服务器查询其提供的工具。请在编辑器与服务器均处于运行状态时执行此命令，以确保查询能够获取到真实的工具列表。如果用户在编辑器偏好设置中更改了端口或路径，则需在 `~/.hermes/config.yaml` 文件的 `mcp_servers.unreal-engine` 部分修改对应的 `url` 值以保持一致。

**请勿**对 Hermes 使用 `ModelContextProtocol.GenerateClientConfig`——该命令是为 Claude Code/Cursor 等工具生成 `.mcp.json` 格式的配置文件。Hermes 会通过 `config.yaml` 中的目录条目进行连接。

### 每次会话前的准备

1. 启动 Unreal Editor，等待项目加载完成；确认服务器已启动（输出日志中会显示绑定地址，或可手动执行 `ModelContextProtocol.StartServer`）。
2. 启动 Hermes 会话。工具将以 `mcp_unreal_engine_*` 的形式注册。如果找不到这些工具，说明编辑器未先启动——请先启动编辑器，然后再打开新的 Hermes 会话。
3. 进行合理性检查：调用 `mcp_unreal_engine_list_toolsets`，确认能获取到工具集列表。

## 工具界面：动态发现，而非固定列表

默认情况下，该插件以**工具搜索模式**运行：`tools/list` 只会返回三个元工具，所有实际工具都需要通过这些元工具来访问。通过 Hermes，这些工具会以如下形式呈现：

| Hermes 工具 | 功能 |
|---|---|
| `mcp_unreal_engine_list_toolsets` | 列出所有已注册工具集的名称与描述 |
| `mcp_unreal_engine_describe_toolset` | 提供某个指定工具集下所有工具的完整 JSON 规范 |
| `mcp_unreal_engine_call_tool` | 带参数调用指定工具，并获取执行结果 |

工具发现的过程始终遵循以下顺序：

1. 调用 `list_toolsets`，查看该项目实际具备哪些功能能力（工具界面取决于项目配置：已启用的插件、游戏功能插件以及任何自定义工具集都会影响工具列表）。返回的名称均为全限定形式（如 `editor_toolset.toolsets.scene.SceneTools`、`EditorToolset.EditorAppToolset`），可直接将其作为 `toolset_name` 使用。
2. 对所需的功能组调用 `describe_toolset`，读取实际的参数规范。切勿自行猜测参数名称——参数规范才是官方定义的契约。
3. 使用全限定的工具集名称、简写的工具名称（如 `find_actors`，而非带点分隔的形式），以及符合规范参数的值，调用 `call_tool`。

请将本次会话中获取的信息缓存起来；只有在编辑器端发生变更时（如启用了新插件、创建了新工具集、执行了 `RefreshTools` 命令）才需要重新列出工具列表。

另一种称为“快速模式”的选项（在编辑器偏好设置中关闭“启用工具搜索”即可）会将每个工具作为独立的 `mcp_unreal_engine_<tool>` 条目显示。此时工具发现会在执行 `hermes mcp install`/`configure` 命令时进行。默认模式为工具搜索模式，本技能也以此为前提；此外，该模式还能避免在每次 API 调用中包含额外的规范标识符，因此更推荐使用。

有关已打包的工具集目录、自定义工具集的创建方法以及完整的插件配置/控制台命令参考，可参阅 `references/tool-surface.md` 文件。

## 工作流程循环

所有 Unreal 相关操作都遵循相同的循环流程：

1. **先进行预览。** 在执行任何操作之前，先列出工具集，再查询场景/关卡的当前状态。切勿假设关卡始终为空或处于默认状态。在不太熟悉的项目中，还需检查项目中是否注册了智能体技能（通过调用 `call_tool` 后再执行 `AgentSkillToolset.ListSkills`）：与项目需求匹配的智能体技能指令会覆盖此技能的通用默认设置。
2. **采用小步、单一目标的调用方式。** 每次 `call_tool` 操作仅对应一个逻辑步骤。服务器会在游戏线程上**串行执行**这些工具——如果执行大型复杂操作，编辑器界面将会被冻结直到操作完成，同时还可能引发客户端超时问题。例外情况是：对于包含 5 次及以上相同类型操作的循环，可使用一次 `ProgrammaticToolset.execute_tool_script` 调用来在服务器端批量处理这些操作，而不会违反串行执行规则（详见 `references/advanced-workflows.md`）。
3. **绝不允许同时发起重叠的调用。** 请勿在单次操作中批量发送多个 `mcp_unreal_engine_*` 类型的调用——Hermes 虽然可以并发处理批量调用，但对游戏线程的并行调用会导致死锁或失败。必须严格遵循“一次调用、等待结果、再执行下一次调用”的原则，这一规则优先于一般关于并行工具调用的建议。
4. **务必读取所有返回结果。** 许多工具（如蓝图编译、材质编辑、控件创建等）会在响应体中报告操作是否成功，而不会在协议层抛出异常。只要结果并非明确表示成功，就应立即停止并进行分析，而非直接忽略。在修改属性后，请务必重新读取该属性的值——某些属性的写入路径可能会静默地无效化（详见注意事项）。
5. **通过视觉与结构层面进行验证。** 在每个关键步骤完成后，通过查询已修改的游戏对象或属性来确认状态；如果场景的构图很重要，还需截取视口截图（截图选项详见 `references/tool-surface.md`），并使用 `vision_analyze` 工具对图片进行分析——你才是艺术总监，需亲自判断效果。
6. **频繁保存。** 编辑器中的修改仅在保存为包或关卡后才会持久化；如果编辑器崩溃，自上次保存之后的所有更改都会丢失，而且 MCP 方式的修改通常也不支持可靠撤销。因此，请在每次进行大规模修改之前和之后，以及每个关键步骤完成后都及时保存。
7. **提供具体的反馈信息。** 请明确说明游戏对象的标签、资源路径（如 `/Game/...`）、截图或渲染文件的存储位置等信息。

在工作过程中需遵循以下规则：

- 单位为**厘米**；坐标轴中 Z 轴向上，X 轴向前；旋转角度以度为单位（旋转器中：X 轴方向为滚转，Y 轴方向为俯仰，Z 轴方向为偏航）。人类眼睛的高度约为 165 厘米，一扇门的大小约为 210×90 厘米。更详细的参数表请参见 `references/scene-craft.md`。
- 内容路径使用完整的包名：项目内的内容路径格式为 `/Game/Folder/Asset.Asset`，引擎内置的几何体路径格式为 `/Engine/BasicShapes/Cube.Cube`。
- 游戏对象的**标签**（在对象列表中显示，可设置，非唯一）与对象的**名称**（内部使用，唯一）是不同的概念。建议优先通过标签或类查询来定位游戏对象，然后再保留工具返回的标识符。
- 相比于随意设定的亮度数值，建议使用符合物理规律的光照参数（如勒克斯、坎德拉、开尔文单位）——但首先需读取当前场景中太阳的光强值，以了解该场景的校准规则；模板世界通常将光强设置为 10，而物理参数的值往往会超出这一范围（具体数值见 `references/scene-craft.md`，校准规则见 `references/pitfalls.md` #12b）。

## 从通俗描述到实际场景

用户提供的是需求描述，而非详细技术规格。在开始构建之前，请先进行翻译与转化：

1. **提炼核心需求。** 明确主题、氛围、时间时段、场景类型（室内/室外）、风格要求以及最终交付物形式（截图？渲染图？可运行的关卡？）。最多询问一轮以澄清疑问，之后即可确定方案——你才是技术总监，无需将 Unreal 相关的专业术语原封不动地抛回给用户。
2. **规划构建顺序。** 选择最合理的构建顺序：先搭建关卡/环境框架 → 完成主要几何体或网格的放置 → 设置光照与氛围 → 创建材质 → 添加装饰细节 → 安排摄像机位置 → 最后进行截图或渲染。对于多步骤项目，可将此计划以待办列表的形式记录下来。
3. **按照上述流程逐步构建**，每完成一个关键步骤就截取一次屏幕截图。
4. **亲自把控艺术效果**。将每次截取的截图与需求描述进行对比：轮廓是否清晰可辨？光线方向和强度是否合理？地平线是否不在正中央？与人类身高作为参考的物体比例是否正确？在继续下一步之前，务必先修正这些问题。
5. **完成交付**。将截图或渲染文件以 `MEDIA:` 路径的形式提供，同时附上一份简短的总结，说明关卡中包含的内容及其保存位置。

`references/recipes.md` 文件中提供了完整的实际构建案例（包括室外日光场景、氛围浓郁的室内场景、黄金时刻风格的影视级场景及对应渲染图、资源导入与放置等），其中详细列出了相应的调用顺序与参数值。

## 参考文件

这些文件可根据需要随时加载；在整个使用过程中，请始终牢记 SKILL.md 文件中规定的规则。| 参考文档 | 内容说明 |
|---|---|
| `references/tool-surface.md` | 已发布的工具集目录、发现协议详解、插件控制台命令/CVars/标志参数、截图与捕获路径、MCP Inspector调试方法，以及如何通过自定义Python/C++工具集进行扩展 |
| `references/advanced-workflows.md` | 复杂工作流相关内容，包含经过实测验证的方案：ProgrammaticToolset批量处理、Blueprint DSL编写流程（创建→DSL编写→编译→启动）、PIE测试环节、140种工具的序列化使用方式、LogsToolset自我调试功能、自动化测试方法、语义化资产搜索功能、配置设置，以及针对不同场景的决策表 |
| `references/scene-craft.md` | 数值参考表：物理光照强度、色温、曝光度/EV100值、雾气密度、不同场景（正午/黄金时刻/阴天/夜晚/室内）的配色方案、比例参考表，以及内容路径规范 |
| `references/recipes.md` | 完整的端到端构建案例，包含精确的操作调用顺序 |
| `references/pitfalls.md` | 设置、运行时及工作流中可能出现的常见问题及解决方案——在首次使用前以及遇到异常时请务必查阅 |

## 常见问题（重点提示，完整列表见 `references/pitfalls.md`）

- **启动顺序很重要。** 首先需启动编辑器与服务器，之后再开启Hermes会话。若缺少`mcp_unreal_engine_*`工具，说明启动顺序有误。
- **每次只能发起一次调用。** 由于游戏线程为串行处理模式，因此不支持批量调用，也无法同时进行多轮调用。
- **每次调用时编辑器界面都会冻结。** 这是出于设计考虑（需在游戏线程中执行操作）。对于耗时较长的操作，应向用户发出提示，并尽量缩短单次调用的时间。
- **模态对话框会阻塞所有操作。** 若某个工具调用引发了模态编辑器对话框，或与该对话框发生冲突，系统将会暂停直到用户手动关闭对话框为止。如果某次调用长时间无响应，应提示用户检查编辑器中是否存在未关闭的对话框。
- **长时间操作可能会触发超时。** Hermes默认的单次调用时间为120秒，而资产导入、大型关卡保存及渲染操作的时间可能超过此限制。对于需要大量进行渲染或导入操作的场景，可在`~/.hermes/config.yaml`文件中调整`mcp_servers.unreal-engine.timeout`的值。
- **工具架构信息可能会过时。** 在编写或热加载工具集，或启用某个插件之后，需在编辑器控制台中运行`ModelContextProtocol.RefreshTools`命令，然后重新执行`list_toolsets`操作。若添加了新的C++ `UFUNCTION`函数，必须重启编辑器——Live Coding功能无法显示这些新函数。
- **该插件仍处于测试阶段。** 不同引擎版本之间的API和工具结构可能会发生变化；因此应以`describe_toolset`提供的信息为准，而非仅依赖内存中的数据，包括本技能提供的示例内容。当文档描述与实时生成的架构信息不一致时，以实时架构信息为准。
- **服务器不应允许从本地主机以外的地址访问。** 出于设计考虑，服务器仅支持本地回环访问，且不支持身份验证功能。切勿建议将其开放为更广范围的访问地址。
- **许可说明。** 服务器在启动时会记录相关信息：通过插件传输至连接的LLM服务的数据属于UE最终用户许可协议（§6(e)）所规定的受许可技术——用户有责任确保其使用的LLM服务提供商不会利用这些数据进行训练。如果用户询问数据处理相关问题，应向其说明这一点。

## 验证清单

- [ ] 会话启动时`list_toolsets`能返回工具集列表（说明连接正常）
- [ ] 在进行首次编辑之前先查询场景状态（切勿默认场景为空）
- [ ] 每完成一个阶段后：需重新查询已更改的演员/属性信息，并根据需求检查截图内容
- [ ] 每完成一个阶段以及项目结束时，都要保存关卡文件及临时数据包
- [ ] 所有交付成果都应保存在磁盘上（确认截图/渲染文件的存储路径），并使用完整路径告知用户具体位置
- [ ] 确保编辑器处于干净状态：没有未关闭的模态对话框，也没有未保存的意外更改，同时需向用户明确说明已创建或修改了哪些内容以及具体位置
