---
title: "Blender Mcp — Control Blender directly from Hermes via socket connection to the blender-mcp addon"
sidebar_label: "Blender Mcp"
description: "Control Blender directly from Hermes via socket connection to the blender-mcp addon"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Blender Mcp

通过连接到 blender-mcp 插件的套接字，从 Hermes 直接控制 Blender。可创建 3D 对象、材质与动画，还能运行任意的 Blender Python (bpy) 代码。适用于用户需要在 Blender 中创建或修改内容的场景。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/creative/blender-mcp` 安装 |
| 路径 | `optional-skills/creative/blender-mcp` |
| 版本 | `1.0.0` |
| 开发者 | alireza78a |
| 支持平台 | linux、macos、windows |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能激活后，Agent 就会看到这些指令作为操作指南。
:::

# Blender MCP

通过 TCP 端口 9876 上的套接字，从 Hermes 控制正在运行的 Blender 实例。

## 设置（只需执行一次）

### 1. 安装 Blender 插件

    curl -sL https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py -o ~/Desktop/blender_mcp_addon.py

在 Blender 中操作：
    编辑 > 首选项 > 插件 > 安装 > 选择 blender_mcp_addon.py
    勾选“界面：Blender MCP”

### 2. 在 Blender 中启动套接字服务器

在 Blender 视口按 N 键打开侧边栏。
找到 “BlenderMCP” 选项卡，然后点击 “启动服务器”。

### 3. 验证连接状态

    nc -z -w2 localhost 9876 && echo "OPEN" || echo "CLOSED"

## 协议规范

基于 TCP 的纯 UTF-8 JSON 格式 —— 不包含长度前缀。

发送内容：     &#123;"type": "&lt;command>", "params": &#123;&lt;kwargs>&#125;&#125;
接收内容：  &#123;"status": "success", "result": &lt;value>&#125;
          &#123;"status": "error",   "message": "&lt;reason>"&#125;

## 可用命令

| 类型                    | 参数              | 描述                         |
|-------------------------|-------------------|------------------------------|
| execute_code            | code (str)        | 运行任意的 bpy Python 代码     |
| get_scene_info          | (无)             | 列出场景中的所有对象         |
| get_object_info         | object_name (str) | 获取特定对象的详细信息       |
| get_viewport_screenshot | (无)             | 截取当前视口的屏幕截图     |

## Python 辅助函数

可在调用 execute_code 功能时使用此函数：

    import socket, json

    def blender_exec(code: str, host="localhost", port=9876, timeout=15):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(timeout)
        payload = json.dumps(&#123;"type": "execute_code", "params": &#123;"code": code&#125;&#125;)
        s.sendall(payload.encode("utf-8"))
        buf = b""
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                try:
                    json.loads(buf.decode("utf-8"))
                    break
                except json.JSONDecodeError:
                    continue
            except socket.timeout:
                break
        s.close()
        return json.loads(buf.decode("utf-8"))

## 常用的 bpy 编程示例

### 清空场景
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

### 添加网格对象
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
    bpy.ops.mesh.primitive_cube_add(size=2, location=(3, 0, 0))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(-3, 0, 0))

### 创建并分配材质
    mat = bpy.data.materials.new(name="MyMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (R, G, B, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Metallic"].default_value = 0.0
    obj.data.materials.append(mat)

### 设置关键帧动画
    obj.location = (0, 0, 0)
    obj.keyframe_insert(data_path="location", frame=1)
    obj.location = (0, 0, 3)
    obj.keyframe_insert(data_path="location", frame=60)

### 导出渲染结果为文件
    bpy.context.scene.render.filepath = "/tmp/render.png"
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)

## 常见问题与注意事项

- 运行命令前必须先确认套接字处于开放状态（可使用 nc -z localhost 9876 检查）
- 每次使用前都需在 Blender 内启动插件服务器（通过 N 面板 > BlenderMCP > Connect 操作）
- 为避免超时，应将复杂的操作拆分成多个独立的 execute_code 调用
- 渲染输出路径必须是绝对路径（如 /tmp/...），而非相对路径
- 使用 shade_smooth() 函数时，对象必须处于选中状态且处于对象模式
