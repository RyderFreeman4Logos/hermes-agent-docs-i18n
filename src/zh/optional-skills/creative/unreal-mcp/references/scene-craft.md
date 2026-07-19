# Unreal MCP — 场景构建速查指南

这些数值与规范能让场景呈现出“真实感”，而不仅仅是简单存在。数据来源包括：物理/摄影标准（稳定值）、UE规范（稳定值），以及实际制作中的常用范围（用≈标注）。不同UE版本的默认值可能会发生变化；当实时架构或编辑器设置与本指南不一致时，请以编辑器为准，并相应修正本指南。

## 单位与规范（需牢记的基础知识）

| 项目 | 规范 |
|---|---|
| 距离 | 1个Unreal单位 = **1厘米** |
| 轴向 | **Z轴向上**，X轴向前进，Y轴向右（左撇子视角） |
| 旋转 | 以**度**为单位：滚转（绕X轴）、俯仰（绕Y轴）、偏航（绕Z轴） |
| 颜色 | 线性RGBA格式，每个通道取值范围为0–1（`FLinearColor`类型） |
| 光源颜色 | 建议优先使用`use_temperature`与开尔文温度值，而非直接调整RGB色调 |
| 缩放 | 各轴的缩放系数（1,1,1表示原始尺寸） |

定向光的方向控制：**旋转角度**决定光源方向。俯仰角为−90°时相当于正午阳光直射；−5°至−15°时为黄金时刻，阳光接近地平线；偏航角则决定光源照射的方位。

### 人体尺度参考（所有场景布局都应以此校验）

| 参考对象 | 尺寸（厘米） |
|---|---|
| 站立时眼睛高度 | 160–175 |
| 门 | 高200–210厘米 × 宽80–90厘米 |
| 住宅天花板高度 | 240–300厘米 |
| 单层建筑高度 | 300–400厘米 |
| 柜台/桌子高度 | 75–110厘米 |
| 椅子座椅高度 | 45厘米 |
| 楼梯踏步高度 | 约18厘米，台阶宽度约28厘米 |
| UE默认人体模型高度 | 约180厘米 |
| 汽车长度 | 约450厘米 × 宽度180厘米 × 高度145厘米 |

如果“房屋”门的高度达到400厘米，场景就会显得像玩具世界或巨型场景。务必尽早放置一个人体尺度物体作为参考基准。

## 内容路径

| 路径 | 含义 |
|---|---|
| `/Game/...` | 项目内容（Content/文件夹） |
| `/Engine/...` | 引擎自带的通用内容，所有项目均包含 |
| `/Script/Module.Class` | 自定义类（例如 `/Script/Engine.PointLight`） |

完整包名格式：`/Game/Props/SM_Chair.SM_Chair`（package.object格式）。

始终可用的引擎基础元素（在加载真实资产前用于构建场景结构）：

    /Engine/BasicShapes/Cube.Cube          （比例1时尺寸为100×100×100厘米）
    /Engine/BasicShapes/Sphere.Sphere      （直径100厘米）
    /Engine/BasicShapes/Cylinder.Cylinder  （直径100厘米 × 高度100厘米）
    /Engine/BasicShapes/Cone.Cone
    /Engine/BasicShapes/Plane.Plane        （尺寸100×100厘米，单面）

它们的默认材质为纯灰色；如需美观效果，请为这些元素分配MaterialInstance。如果项目包含Starter Content，相关资源位于`/Game/StarterContent/`目录下（包括Props、材质如`M_Basic_Wall`、`M_Wood_Pine`、`M_Metal_Steel`，以及粒子效果）。在假设Starter Content存在之前，请先进行查询。

常用的生成Actor类包括：`StaticMeshActor`、`PointLight`、`SpotLight`、`RectLight`、`DirectionalLight`、`SkyLight`、`ExponentialHeightFog`、`SkyAtmosphere`、`VolumetricCloud`、`PostProcessVolume`、`CameraActor`、`CineCameraActor`、`PlayerStart`。

## 照明 —— 基于物理原理的数值设置

UE5中的光源默认使用物理单位：定向光以勒克斯为单位，点光源/聚光灯以坎德拉或流明为单位，曝光值以EV100表示。请使用真实世界的数值，这样它们才能与曝光值正确配合，而非相互冲突。

### 太阳光（定向光，单位：勒克斯）

**首先进行校准验证（基于实时数据）：**模板场景通常会将太阳光强度设置为10，并根据该值自动调整曝光——若使用过低的物理勒克斯值，会导致场景整体过白。请先查看现有太阳光的强度；如果数值仅为个位数或两位数，那么请根据该值相对调整整体氛围（正午时对应模板值，黄金时刻约为其0.5–0.7倍，阴天约为0.3倍，夜晚约为0.01倍），并依靠温度与俯仰角来营造氛围。只有当你完全掌控整个曝光流程时（手动设置EV100并统一使用物理单位），才能直接参考下表：

| 场景条件 | 光强（勒克斯） | 俯仰角 | 温度（开尔文） |
|---|---|---|---|
| 正午，晴朗 | 75,000–120,000 | −60°至−90° | 5,500–6,000 K |
| 下午 | 40,000–75,000 | −30°至−50° | 5,000–5,500 K |
| 黄金时刻 | 5,000–20,000 | −5°至−15° | 2,800–3,500 K |
| 阴天 | 5,000–20,000（光线柔和） | −45°左右 | 6,500–7,500 K |
| 蓝调时刻/黄昏 | 10–100 | −2°至+5° | 8,000–12,000 K |
| 满月之夜 | 0.05–0.3 | −30°至−60° | 4,000–4,500 K（冷蓝色色调由曝光值与色调分级共同决定） |

阴天时：还应降低定向光的阴影对比度（通过增大光源角度使阴影更柔和），让天空光线占据主导。

### 天空光

每个场景层级应设置一个SkyLight；若使用SkyAtmosphere，则需启用实时捕获功能（SLS Captured Scene），这样天空光会自动跟随太阳移动。不要叠加多个天空光；在大幅调整光照后，也不要保留过时的静态捕获版本（非实时场景需重新捕获）。

### 局部光源（点光源/聚光灯/矩形光）

以流明为单位估算的光源强度（对于点光源，坎德拉值约等于流明值除以4π）：

| 光源类型 | 流明值 |
|---|---|
| 蜡烛火焰 | 10–15（约1,850 K） |
| 等效40瓦白炽灯 | 450（2,700 K） |
| 等效60瓦白炽灯 | 800（2,700–3,000 K） |
| 等效100瓦白炽灯 | 1,600（3,000 K） |
| 明亮的天花板灯具 | 2,000–4,000（3,000–4,000 K） |
| 荧光灯管/办公室照明 | 2,500–5,000（4,000–5,000 K） |
| 钠灯路灯 | 5,000–15,000（约2,000 K，橙色光） |
| 汽车前灯 | 每侧1,000–1,500流明（4,300–6,000 K） |
| 营地篝火 | 100–300流明，光线会闪烁（1,700–2,000 K） |

聚光灯的光锥角度：内圈20–35°，外圈40–60°，以形成自然的渐变效果。衰减半径：实际制作中应保持较小值（几百厘米即可）——过大的半径会降低性能并使场景显得扁平。如仅需均匀补光，则可关闭阴影功能。

### 色温术语表（开尔文）

1,700–1,900 K对应蜡烛光；2,700 K对应暖色灯泡光；3,200 K对应钨丝灯工作室照明；3,500 K对应黄金时刻光线；4,300 K对应月光效果；5,600 K对应日光/闪光灯光；6,500 K对应阴天光线；7,500–10,000 K对应阴影/蓝调时刻光线。将暖色调的主体与冷色调的环境光结合，是让画面看起来“有光感”而非“平淡”的最简单方法。

### 曝光控制（PostProcessVolume —— 解决“画面过黑/过白”问题的核心工具）

自动曝光功能会干扰基于确定性光照的计算结果。在需要由AI代理驱动的场景中，建议在PPV中使用**手动曝光**：

1. 生成或定位一个PostProcessVolume，将**Infinite Extent (Unbound) = true**设置为开启。
2. 将计量模式设为Manual，然后将曝光补偿值设为约0，EV100值根据场景实际光线强度调整：

| 场景类型 | EV100值 |
|---|---|
| 阳光充足的室外场景 | 14–16 |
| 阴天的室外场景 | 11–13 |
| 黄金时刻 | 10–12 |
| 明亮的室内场景（白天，有窗户） | 7–9 |
| 光线较暗的室内场景 | 4–6 |
| 夜间街道 | 2–4 |
| 月光下的室外场景 | −2至0 |

如果仍使用自动曝光功能（计量模式设为Auto Histogram），则需对其加以限制：将EV100的最小值与最大值控制在目标值的±2范围内，避免其波动过大。常见问题对应表如下：场景中有光源但渲染结果为黑色 → 光线强度对应的EV100值过高；场景过白 → EV100值过低。

### 全局光照与反射

UE5的默认设置是使用**Lumen**全局光照系统及Lumen反射效果，无需进行光度贴图烘焙——光照是实时计算的，只需保持“Allow Static Lighting”选项的默认设置即可。**重要提示：Lumen全局光照仅考虑具有Movable移动性的光源。**若直接生成的光源默认设置为Stationary/Static类型，则不会对全局光照产生任何贡献——因此，请为每个放置的光源明确设置Mobility = Movable属性，且当发现“全局光照效果不佳”时，首先检查光源的移动性设置。金属或镜面表面只有在有可反射的对象存在时才能正确显示效果：在评估材质之前，先为场景添加天空背景及周围环境。

### 雾效与氛围

- **SkyAtmosphere**可用于创建符合物理规律的天空效果（包括太阳光盘、地平线渐变等）；若使用定向光，则需将“Atmosphere Sun Light”设置为true。
- **ExponentialHeightFog**：默认密度为0.02。实际应用中的常用范围如下：0.005–0.015可营造微妙的深度感；0.02–0.05适合打造氛围感或晨间效果；0.05–0.2则适用于强烈的雾效。若希望光线能穿透雾层，可为该雾效启用**Volumetric Fog**功能，然后为关键光源调整“Volumetric Scattering Intensity”值（范围1–10）。
- **VolumetricCloud**可用于模拟真实的天空云层效果（仅适用于室外场景，会占用较多GPU资源）。
- 夜间场景：降低雾效密度，添加微弱的冷色调补光（如低强度的天空光），这样阴影就不会呈现纯黑色。

## 氛围营造方案（简版）

| 氛围类型 | 太阳光/关键光源 | 天空效果 | 雾效 | EV100值 | 色调调整建议 |
|---|---|---|---|---|---|
| 清新正午 | 10万勒克斯，俯仰角−70°，温度5,800 K | 实时捕获的天空 | 密度0.005 | 15 | 保持中性色调 |
| 黄金时刻 | 1万勒克斯，俯仰角−8°，温度3,200 K | 实时捕获的天空 | 密度0.02 + 启用体积雾效 | 11 | 关键光源采用暖色调，阴影较长：通过调整偏航角制造边缘光或侧光 |
| 阴天 | 1万勒克斯柔和光线，温度7,000 K | 天空占主导 | 密度0.01 | 12 | 对比度较低，依靠饱和度来体现色彩 |
| 月光下的夜晚 | 0.25勒克斯，温度4,300 K，辅以实际光源约800流明、2,700 K | 光线极弱 | 密度0.015 | −1至1 | 冷色调环境光与暖色调实际光源形成对比 |
| 恐怖风格室内场景 | 无太阳光；仅1–2个实际光源，阴影明显 | 雾效较重 | 密度0.03–0.06的体积雾效 | 4–5 | 使用单一有动机的关键光源，营造深色背景 |
| 科幻风格走廊 | 矩形光，亮度2,000流明，温度6,500–8,000 K，搭配彩色点缀光源 | 无特殊天空效果 | 密度0.02的体积雾效 | 6 | 使用互补色搭配作为点缀（如青色与橙色） |

## 相机与构图（使用CineCameraActor）

对于需要具备电影感的场景，请使用CineCameraActor而非普通Camera，因为它拥有真实的胶片模拟、镜头效果及景深控制功能。

| 拍摄意图 | 焦距 | 光圈值 |
|---|---|---|
| 宏观场景/室内广角拍摄 | 18–28毫米 | f/5.6–8 |
| 中性“人眼视角” | 35–50毫米 | f/4 |
| 特写/突出主体 | 85–135毫米 | f/1.4–2.8 |
| 背景压缩效果（营造层次感） | 100–200毫米 | f/2.8–5.6 |

- **胶片模拟设置**：默认的16:9数字胶片格式（约23.76 × 13.365毫米）即可，无需更改。
- **对焦设置**：手动对焦距离等于相机到拍摄主体的距离（单位为厘米）；若需浅景深效果，则需要使用长焦镜头、大光圈，并确保主体与背景保持一定距离。
- **相机位置**：中性视角的拍摄高度约为155–170厘米；低于此高度约100厘米时，画面更具英雄感或压迫感；过高角度则会使画面显得矮小。避免将地平线置于正中央，应将主体放置在画面的三分线位置上。对于室内场景，略微下倾相机角度（−2°至−8°）通常比完全水平更佳。
- **宽高比与视觉效果**：可启用相机的“Constrain Aspect Ratio”功能，以获得整洁的方框形静态图像。

## 捕获与渲染

- **视图窗口截图**：在控制台输入`HighResShot 1`（当前视图分辨率）、`HighResShot 2`（2倍分辨率），或`HighResShot 3840x2160`。截图将保存至`<项目路径>/Saved/Screenshots/<平台>/`目录中，文件名会自动递增（例如`HighresScreenshot00000.png`）。
- 若要通过相机进行构图拍摄：在调用HighResShot之前，先操控或占用CineCamera相机（或将视图窗口切换为该相机的视角），并先以1倍分辨率截图进行预览。
- **电影渲染队列**（MRQ）是用于最终输出或序列化场景的高质量渲染方式：需要使用带有绑定相机的关卡序列（即包含Camera Cut轨道的序列）；该功能可输出带有抗锯齿处理的PNG/EXR格式序列或静态图像，且支持自定义分辨率及时间采样次数。打开项目后的首次渲染会因着色器编译而暂停——此时应向用户提示，而非直接判定为渲染失败。
- 判断渲染结果时，可回放生成的文件，并使用`vision_analyze`工具对照初始需求对每张截图进行评估。

## 编辑器Python快速参考

自定义工具集以及任何已打包的Python脚本均使用`unreal`模块。以下为标准入口函数（请根据实际编辑器版本核对函数名称——Epic会不断将相关库迁移到新的子系统中）：

```python
import unreal

# Actors (EditorActorSubsystem supersedes EditorLevelLibrary for these)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
actor  = eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(0, 0, 200))
mesh_a = eas.spawn_actor_from_object(
    unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube"),
    unreal.Vector(0, 0, 50))
actor.set_actor_label("Key Light")
actor.set_actor_location(unreal.Vector(100, 0, 250), False, True)
actor.set_actor_rotation(unreal.Rotator(0, -30, 45), True)   # roll, pitch, yaw
eas.destroy_actor(actor)

# Assets
unreal.EditorAssetLibrary.does_asset_exist("/Game/Props/SM_Chair")
unreal.EditorAssetLibrary.list_assets("/Game/Props", recursive=True)
unreal.EditorAssetLibrary.save_directory("/Game", only_if_is_dirty=True)

# Level save
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()

# Undo-friendly mutation
with unreal.ScopedEditorTransaction("Agent: dress set") as trans:
    ...  # property edits inside are one undo step

# Import (FBX/textures)
task = unreal.AssetImportTask()
task.filename = "/abs/path/model.fbx"
task.destination_path = "/Game/Imported"
task.automated = True      # suppresses the import dialog — critical for MCP
task.save = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

# Editor property access works on anything reflected
light_comp = actor.get_component_by_class(unreal.PointLightComponent)
light_comp.set_editor_property("intensity", 800.0)
light_comp.set_editor_property("use_temperature", True)
light_comp.set_editor_property("temperature", 2700.0)
```

当不存在专用的设置函数时，采用下划线命名方式的 `set_editor_property`/`get_editor_property` 函数便是通用的替代方案——其属性名称与“详细信息”面板中显示的内容一致（已去除空格）。
