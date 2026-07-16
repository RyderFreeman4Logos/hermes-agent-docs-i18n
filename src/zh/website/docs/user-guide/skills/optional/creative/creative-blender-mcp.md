---
title: "Blender Mcp — Drive Blender via the catalog blender MCP, with bpy recipes"
sidebar_label: "Blender Mcp"
description: "Drive Blender via the catalog blender MCP, with bpy recipes"
---

{{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。*/}}

# Blender Mcp

通过 blender MCP 目录及 bpy 脚本来操控 Blender。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/blender-mcp` 安装 |
| 路径 | `optional-skills/creative/blender-mcp` |
| 版本 | `2.1.0` |
| 开发者 | alireza78a + kshitijk4poor + Hermes Agent |
| 支持平台 | linux、macos、windows |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能激活后，Agent 就会依据这些内容执行操作。
:::

# Blender MCP 技能

Hermes MCP 目录中 `blender` 条目对应的配套技能。MCP 服务器负责建立与 Blender 的连接；该技能则教授用于高效操控 Blender 的 bpy 用法及常见陷阱。它不涉及 Blender 的 UI 工作流程——所有操作均通过 MCP 工具在正在运行的 Blender 会话中完成。

## 适用场景

当用户需要在正在运行的 Blender 实例中创建或修改内容时使用，例如网格、材质、动画、光照及渲染结果等。使用时需已安装 blender MCP 服务器，并且 Blender 桌面会话已加载对应插件。

## 先决条件

1. 从 Nous 目录安装 MCP 服务器（只需一次）：

       hermes mcp install blender

   此操作会配置已筛选好的工具集，包括固定的 `blender-mcp` 标准输入输出服务器，以及以下工具：`get_scene_info`、`get_object_info`、`get_viewport_screenshot`、`execute_blender_code`。

2. 在 Blender 内部安装插件（只需一次——目录条目的安装后说明中也提到了此步骤）：
   - 下载 https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py
   - 打开 Blender > 编辑 > 首选项 > 插件 > 安装... > 选择 addon.py，然后勾选“接口：Blender MCP”。

3. 每次使用前：首先启动 Blender，在视口中按下 N 键，打开“BlenderMCP”标签页，点击“连接到 Claude”（这将启动本地的桥接套接字）。之后再启动 Hermes 会话，这样 MCP 工具就会被加载。
   该插件无法在 `blender -b`（后台模式）下运行。在没有显示器的机器上，需通过虚拟显示器运行 Blender：`xvfb-run blender`。Xvfb 环境下 GPU 渲染功能可正常使用。

## 快速参考

| MCP 工具                  | 用途                                     |
|---------------------------|------------------------------------------|
| `get_scene_info`          | 在操作场景前列出其中的对象                 |
| `get_object_info`         | 检查单个对象的信息（变换、材质等）         |
| `get_viewport_screenshot` | 可视化查看已创建的内容                     |
| `execute_blender_code`    | 其他所有操作——可执行任意的 bpy Python 代码   |

更详细的用法说明见参考文件（按需加载）：

| 参考文件 | 内容概述 |
|-----------|----------|
| `references/bpy-api.md` | 关键的 bpy 操作：建模、材质、修改器、渲染等 |
| `references/recipes.md` | 完整的可运行场景示例：低多边形地形、玻璃球体、HDRI 光照、转盘动画等 |
| `references/pitfalls.md` | 经验总结：空代码在 5.x 版本中的后果、操作对象与数据对象的 API 区别、不同版本引擎的名称等 |

可选的资产服务工具（PolyHaven、Sketchfab、Hyper3D、Hunyuan3D）默认处于禁用状态。如果用户在插件面板中启用了某项服务，可通过 `hermes mcp configure blender` 来启用其对应工具。

## 操作步骤

1. 首先调用 `get_scene_info`——切勿假设场景为空。
2. 使用 `execute_blender_code` 进行构建，每次调用应聚焦于一个具体步骤（比如先添加对象，再添加材质，最后添加动画）。过大的单一脚本会导致桥接超时。
3. 在执行关键步骤之间，通过 `get_viewport_screenshot` 进行可视化确认。
4. 将渲染结果保存到绝对路径的文件中，并告知用户文件位置。

### 常用的 bpy 操作模式

清空场景：

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

添加网格对象：

    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
    bpy.ops.mesh.primitive_cube_add(size=2, location=(3, 0, 0))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(-3, 0, 0))

创建并分配材质：

    mat = bpy.data.materials.new(name="MyMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (R, G, B, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Metallic"].default_value = 0.0
    obj.data.materials.append(mat)

设置关键帧动画：

    obj.location = (0, 0, 0)
    obj.keyframe_insert(data_path="location", frame=1)
    obj.location = (0, 0, 3)
    obj.keyframe_insert(data_path="location", frame=60)

将场景渲染为文件：

    bpy.context.scene.render.filepath = "/tmp/render.png"
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)

## 常见问题与注意事项

- 只有在安装了 MCP 服务器，并且在安装后启动了 Blender 会话，才能使用这些工具。如果找不到相关工具，请运行 `hermes mcp install blender` 并重新启动会话。
- 每次使用 Blender 时，都需在 Blender 内部重新连接插件桥接（N 面板 > BlenderMCP > 连接）。如果工具提示“连接被拒绝”，说明 Blender 未运行或插件未连接——请先解决该问题，不要重复尝试。
- 为避免桥接超时，应将复杂的场景拆分成多个较小的 `execute_blender_code` 调用。
- 渲染输出路径必须是绝对路径（如 `/tmp/render.png`），而非相对路径——路径会在 BLENDER 运行所在的文件系统中解析，因此当 Hermes 和 Blender 运行在不同机器上时这一点尤为重要。
- `shade_smooth()` 函数要求对象已被选中且处于对象模式。
- `execute_blender_code` 会在 Blender 内部直接运行任意的 Python 代码，且没有沙箱保护——其安全性与 `terminal` 工具相当。切勿向其中粘贴不可信的代码。
- 请勿通过 `execute_code` 手动将原始 TCP JSON 数据发送到端口 9876——这是该技能在 MCP 出现之前的临时解决方案。这种方式会绕过目录的版本限制和工具筛选机制。目前应使用 MCP 工具作为标准方式。

## 验证方法

- 每次完成构建步骤后，`get_scene_info` 应返回预期的对象列表。
- `get_viewport_screenshot` 显示的内容应与预期一致。
- 渲染完成后，确认输出文件存在，并将它的绝对路径告知用户。
