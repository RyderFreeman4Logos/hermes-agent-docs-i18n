# Blender MCP — 常见问题与经验总结

所有交互均通过Blender MCP工具实现（`hermes mcp install blender`），包括：`get_scene_info`、`get_object_info`、`get_viewport_screenshot`，以及用于执行任意bpy Python代码的`execute_blender_code`。

## 设置与连接

### 1. 必须先启动插件桥接，工具才能正常工作

只有当您在BlenderMCP侧边栏标签页（N面板）中点击“连接到Claude”时，Blender MCP插件才会打开其本地桥接套接字。如果MCP工具出现“连接被拒绝”的错误，说明插件尚未建立连接——请在Blender中解决该问题，而非重复尝试使用工具。

**验证桥接是否已启动：** `lsof -i :9876 -P -n | grep LISTEN`

### 2. 端口9876为插件默认端口——需检查是否存在冲突

其他服务可能已在使用端口9876。如果工具无法正常运行，但Blender已启动且插件也已加载，请使用lsof命令进行检查。该端口可在BlenderMCP插件界面面板中进行配置。

### 3. 安装插件需要用户手动操作

Blender插件的安装需通过图形界面完成：编辑 > 首选项 > 插件 > 安装。智能体无法自动执行此操作，需由用户提供addon.py文件的路径并手动进行安装。

## Python代码执行（`execute_blender_code`）

### 4. 命名空间中仅包含bpy和math模块

代码在仅包含`bpy`和`math`两个模块的命名空间中运行。如果需要使用os、json、bmesh、mathutils等其他模块，需在代码内部进行导入：

```python
import bmesh
bm = bmesh.new()
...
```

### 5. 在 Blender 5.x 中代码执行结果始终为空

该插件会对所有代码返回 `{"executed": true, "result": ""}` 的格式——因为在 Blender 5.x 中无法捕获代码的评估结果。若需获取实际值，请：
- 使用 `get_scene_info` 或 `get_object_info` 进行查询；
- 将结果写入临时文件后再读取回来。

```python
import json
open('/tmp/result.json', 'w').write(json.dumps([o.name for o in bpy.data.objects]))
```

### 6. 错误会以错误字符串形式返回——务必检查

该插件会捕获异常，并将其作为错误文本返回，而不会导致程序崩溃。在认定代码已正常运行之前，请先检查工具输出中是否存在错误。

### 7. bpy.ops需要正确的上下文环境

许多 `bpy.ops` 函数要求具备恰当的 UI 上下文环境，而通过桥接器执行时这一环境可能会有所不同。建议优先采用直接的数据操作方式：

```python
# Prefer data API over ops
bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True)
```

## 物体与场景

### 8. 默认场景包含立方体、光源和相机

新的Blender文件会以位于(0,0,0)位置的立方体、一个光源以及一个相机作为起始内容。在开始构建之前请先清除这些元素。

### 9. 物体名称必须唯一——Blender会自动为重复名称重命名

如果已存在名为“Cube”的物体，再次创建该名称的物体时，其名称将变为“Cube.001”。建议始终通过`get_scene_info`函数来查看物体的实际名称。

### 10. 度与弧度

该插件自身的物体创建命令接受度值并在内部进行转换，但`execute_blender_code`中的Bpy代码则使用弧度值。请注意两者之间的区别。

## 材质

### 11. 默认着色器为Principled BSDF

该插件创建的材质均使用Principled BSDF作为着色器。对于其他类型的着色器，则需在`execute_blender_code`函数中手动构建节点树。

### 12. 颜色为0-1范围的RGBA格式，而非0-255范围的RGB格式

材质颜色采用0.0-1.0范围内的浮点型RGBA格式。

## 渲染

### 13. 渲染会阻塞操作流程——请做好长时间等待的准备

渲染是同步操作，直到渲染完成之前，工具调用都不会返回结果。因此，渲染所需的时间通常会比其他操作长得多。

### 14. 不同版本的Blender对应不同的渲染引擎名称

在Blender 5.x版本中，EEVEE引擎的名称为“'BLENDER_EEVEE'”（而非Blender 4.x版本中的“'BLENDER_EEVEE_NEXT'”）。可在运行时查询可用的渲染引擎列表：

```python
import json
open('/tmp/engines.json', 'w').write(json.dumps(
    list(bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys())))
```

已知的引擎名称：`BLENDER_EEVEE`、`BLENDER_WORKBENCH`、`CYCLES`

### 15. 在 macOS 上进行 GPU 渲染需要手动配置

Apple Silicon 平台应使用 METAL 计算设备类型，而 NVIDIA 平台则需使用 CUDA 或 OPTIX。

## 可靠性

### 16. 所有状态均存储在 Blender 的场景数据中

每次工具调用都是独立的——桥接器中不存在会话状态。后续所需的任何内容都必须存在于场景中（或您自行保存的文件中）。

### 17. 若 Blender 崩溃，桥接器将失效

如果 Blender 崩溃，请重新启动它，再次启用该插件，然后点击“连接到 Claude”。请频繁保存文件（使用 `bpy.ops.wm.save_mainfile()`）。
