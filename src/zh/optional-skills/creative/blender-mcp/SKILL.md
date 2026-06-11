---
name: blender-mcp
description: Control Blender directly from Hermes via socket connection to the blender-mcp addon. Create 3D objects, materials, animations, and run arbitrary Blender Python (bpy) code. Use when user wants to create or modify anything in Blender.
version: 1.0.0
requires: Blender 4.3+ (desktop instance required, headless not supported)
author: alireza78a
tags: [blender, 3d, animation, modeling, bpy, mcp]
platforms: [linux, macos, windows]
---

# Blender MCP

通过 TCP 端口 9876 上的套接字，从 Hermes 控制正在运行的 Blender 实例。

## 设置（只需执行一次）

### 1. 安装 Blender 插件

    curl -sL https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py -o ~/Desktop/blender_mcp_addon.py

在 Blender 中操作：
    编辑 > 首选项 > 插件 > 安装 > 选择 blender_mcp_addon.py
    勾选“接口：Blender MCP”

### 2. 在 Blender 中启动套接字服务器

在 Blender 视口按 N 键打开侧边栏。
找到 “BlenderMCP” 选项卡并点击 “启动服务器”。

### 3. 验证连接状态

    nc -z -w2 localhost 9876 && echo "OPEN" || echo "CLOSED"

## 协议规范

基于 TCP 的纯 UTF-8 JSON 格式——无需长度前缀。

发送内容：     {"type": "<command>", "params": {<kwargs>}}
接收内容：  {"status": "success", "result": <value>}
          {"status": "error",   "message": "<reason>"}

## 可用命令

| 类型                    | 参数              | 描述                     |
|-------------------------|-------------------|---------------------------------|
| execute_code            | code (str)        | 运行任意的 bpy Python 代码   |
| get_scene_info          | (无)             | 列出场景中的所有对象       |
| get_object_info         | object_name (str) | 获取特定对象的详细信息    |
| get_viewport_screenshot | (无)             | 截取当前视口的屏幕截图   |

## Python 辅助函数

可在 `execute_code` 函数调用中使用以下代码：

    import socket, json

    def blender_exec(code: str, host="localhost", port=9876, timeout=15):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(timeout)
        payload = json.dumps({"type": "execute_code", "params": {"code": code}})
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

## 常用的 bpy 编程模式

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

### 导出为文件
    bpy.context.scene.render.filepath = "/tmp/render.png"
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)

## 常见问题与注意事项

- 运行前必须确认套接字处于开放状态（可使用 `nc -z localhost 9876` 检查）
- 每次使用 Blender 时都需在内部启动插件服务器（通过 N 面板 > BlenderMCP > Connect 操作）
- 为避免超时，应将复杂的操作拆分为多个独立的 `execute_code` 调用
- 渲染输出路径必须是绝对路径（如 `/tmp/...`），而非相对路径
- 使用 `shade_smooth()` 函数时，对象必须处于选中状态且处于对象模式
