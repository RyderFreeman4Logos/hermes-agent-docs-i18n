---
name: touchdesigner-mcp
description: Control TouchDesigner via twozero MCP.
version: 1.1.0
author: kshitijk4poor
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [TouchDesigner, MCP, twozero, creative-coding, real-time-visuals, generative-art, audio-reactive, VJ, installation, GLSL]
    related_skills: [ascii-video, manim-video]

---

# TouchDesigner 集成（twozero MCP）

## 重要规则

1. **绝不要猜测参数名称。** 首先调用 `td_get_par_info` 获取操作类型的参数信息。您所使用的训练数据已不适用于 TD 2025.32 版本。
2. **如果出现 `tdAttributeError` 异常，请立即停止。** 在继续操作之前，先对出错的节点调用 `td_get_operator_info`。
3. **切勿在脚本回调中硬编码绝对路径。** 应使用 `me.parent()` / `scriptOp.parent()` 来获取路径。
4. **优先使用原生 MCP 工具，而非 `td_execute_python`。** 请使用 `td_create_operator`、`td_set_operator_pars`、`td_get_errors` 等函数。仅在需要处理复杂的多步骤逻辑时才考虑使用 `td_execute_python`。
5. **在构建相关内容之前，先调用 `td_get_hints`。** 该函数会返回与您正在处理的操作类型相关的特定提示信息。

## 架构

```
Hermes Agent -> MCP (Streamable HTTP) -> twozero.tox (port 40404) -> TD Python
```

36种原生工具。免费插件（无需付费或许可证——截至2026年4月已确认）。
具备上下文感知能力（能识别选定的操作及当前网络环境）。
中心节点健康检查：执行`GET http://localhost:40404/mcp`命令，即可获取包含实例PID、项目名称以及TD版本的JSON数据。

## 设置（自动化方式）

运行设置脚本即可自动完成所有配置：

```bash
bash "${HERMES_HOME:-$HOME/.hermes}/skills/creative/touchdesigner-mcp/scripts/setup.sh"
```

该脚本将执行以下操作：
1. 检查TD是否正在运行
2. 若未缓存则下载twozero.tox文件
3. （如缺失）在Hermes配置中添加`twozero_td` MCP服务器
4. 测试端口40404上的MCP连接
5. 显示剩余的手动操作步骤（将.tox文件拖入TD、启用MCP开关）

### 手动操作步骤（需手动执行，无法自动化）

1. **将`~/Downloads/twozero.tox`文件拖入TD网络编辑器** → 点击“安装”
2. **启用MCP功能**：点击twozero图标 → 设置 → MCP → 选择“自动启动MCP” → 确定
3. **重启Hermes会话**以加载新的MCP服务器

设置完成后，请进行验证：
```bash
nc -z 127.0.0.1 40404 && echo "twozero MCP: READY"
```

## 环境说明

- **非商业用途的TD版本**将分辨率上限限制在1280×1280。此时需使用`outputresolution = 'custom'`并明确指定宽高数值。
- **编码格式**：首选`prores`（在macOS上表现最佳），若不可用则可选用`mjpa`作为替代方案。而H.264/H.265/AV1格式则需持有商业许可证才能使用。
- 在设置参数之前，务必先调用`td_get_par_info`函数——不同版本的TD该函数的参数名称可能有所不同（详见重要规则#1）。

## 工作流程

### 第0步：探测（在构建任何内容之前）

```
Call td_get_par_info with op_type for each type you plan to use.
Call td_get_hints with the topic you're building (e.g. "glsl", "audio reactive", "feedback").
Call td_get_focus to see where the user is and what's selected.
Call td_get_network to see what already exists.
```

无需临时节点，也无需进行清理操作。这完全取代了以往的节点发现流程。

### 第一步：清理 + 构建

**重要提示：请将清理操作与创建操作分开，通过独立的 MCP 调用来完成。** 若在同一个 `td_execute_python` 脚本中同时销毁并重新创建同名节点，将会引发“无效的操作对象”错误。详情请参阅问题 #11b。

对于每个节点，请使用 `td_create_operator` 函数（该函数会自动处理视口定位问题）：

```
td_create_operator(type="noiseTOP", parent="/project1", name="bg", parameters={"resolutionw": 1280, "resolutionh": 720})
td_create_operator(type="levelTOP", parent="/project1", name="brightness")
td_create_operator(type="nullTOP", parent="/project1", name="out")
```

如需批量创建或配置连接，可使用 `td_execute_python` 命令：

```python
# td_execute_python script:
root = op('/project1')
nodes = []
for name, optype in [('bg', noiseTOP), ('fx', levelTOP), ('out', nullTOP)]:
    n = root.create(optype, name)
    nodes.append(n.path)
# Wire chain
for i in range(len(nodes)-1):
    op(nodes[i]).outputConnectors[0].connect(op(nodes[i+1]).inputConnectors[0])
result = {'created': nodes}
```

### 第2步：设置参数

建议使用原生工具（可验证参数有效性，且不会导致程序崩溃）：

```
td_set_operator_pars(path="/project1/bg", parameters={"roughness": 0.6, "monochrome": true})
```

对于表达式或特定模式，可使用 `td_execute_python`：

```python
op('/project1/time_driver').par.colorr.expr = "absTime.seconds % 1000.0"
```

### 第 3 步：数据传输

请使用 `td_execute_python` 命令——目前尚无内置的数据传输工具：

```python
op('/project1/bg').outputConnectors[0].connect(op('/project1/fx').inputConnectors[0])
```

### 第4步：验证

```
td_get_errors(path="/project1", recursive=true)
td_get_perf()
td_get_operator_info(path="/project1/out", detail="full")
```

### 第 5 步：显示 / 捕获

```
td_get_screenshot(path="/project1/out")
```

或者通过脚本打开一个窗口：

```python
win = op('/project1').create(windowCOMP, 'display')
win.par.winop = op('/project1/out').path
win.par.winw = 1280; win.par.winh = 720
win.par.winopen.pulse()
```

## MCP 工具快速参考

**核心工具（最常用）：**
| 工具 | 功能 |
|------|------|
| `td_execute_python` | 在 TD 中运行任意 Python 代码，拥有完整的 API 访问权限。 |
| `td_create_operator` | 创建带有参数及自动定位功能的节点。 |
| `td_set_operator_pars` | 安全地设置参数（会进行验证，避免程序崩溃）。 |
| `td_get_operator_info` | 检查单个节点：连接关系、参数及错误信息。 |
| `td_get_operators_info` | 一次性检查多个节点的信息。 |
| `td_get_network` | 查看指定路径下的网络结构。 |
| `td_get_errors` | 递归查找错误与警告信息。 |
| `td_get_par_info` | 获取某类操作节点的参数名称（可替代自动发现功能）。 |
| `td_get_hints` | 在构建之前获取相关模式与提示。 |
| `td_get_focus` | 查看当前处于活动状态的网络及已选中的元素。 |

**读/写工具：**
| 工具 | 功能 |
|------|------|
| `td_read_dat` | 读取 DAT 文件的文本内容。 |
| `td_write_dat` | 写入或修改 DAT 文件的内容。 |
| `td_read_chop` | 读取 CHOP 通道的值。 |
| `td_read_textport` | 读取 TD 控制台的输出内容。 |

**可视化工具：**
| 工具 | 功能 |
|------|------|
| `td_get_screenshot` | 将某个操作节点的视图截取并保存为文件。 |
| `td_get_screenshots` | 同时截取多个操作节点的视图。 |
| `td_get_screen_screenshot` | 通过 TD 截取实际屏幕画面。 |
| `td_navigate_to` | 在网络编辑器中跳转到指定的操作节点。 |

**搜索工具：**
| 工具 | 功能 |
|------|------|
| `td_find_op` | 按名称或类型在整个项目中查找操作节点。 |
| `td_search` | 搜索代码、表达式及字符串参数。 |

**系统工具：**
| 工具 | 功能 |
|------|------|
| `td_get_perf` | 性能分析（帧率、慢操作） |
| `td_list_instances` | 列出所有正在运行的 TD 实例 |
| `td_get_docs` | 获取关于特定 TD 主题的详细文档 |
| `td_agents_md` | 读取/写入针对各 COMP 的 Markdown 文档 |
| `td_reinit_extension` | 修改代码后重新加载扩展模块 |
| `td_clear_textport` | 调试会话开始前清空控制台 |

**输入自动化：**
| 工具 | 功能 |
|------|------|
| `td_input_execute` | 向 TD 发送鼠标/键盘操作指令 |
| `td_input_status` | 查询输入队列状态 |
| `td_input_clear` | 停止输入自动化操作 |
| `td_op_screen_rect` | 获取节点在屏幕上的坐标 |
| `td_click_screen_point` | 点击截图中的指定位置 |
| `td_screen_point_to_global` | 将截图像素坐标转换为绝对屏幕坐标 |

上表列出了典型创意工作流中使用的 32 种工具。其余 4 种工具（`td_project_quit`、`td_test_session`、`td_dev_log`、`td_clear_dev_log`）为管理/开发模式下的实用工具——如需包含完整参数规范的 36 种工具参考列表，请参阅 `references/mcp-tools.md`。

## 关键实现规则

**GLSL 时间处理：** GLSL 顶点着色器中不得使用 `uTDCurrentTime`。应通过“值”页面来获取时间信息：
```python
# Call td_get_par_info(op_type="glslTOP") first to confirm param names
td_set_operator_pars(path="/project1/shader", parameters={"value0name": "uTime"})
# Then set expression via script:
# op('/project1/shader').par.value0.expr = "absTime.seconds"
# In GLSL: uniform float uTime;
```

**备用方案：** 使用 `rgba32float` 格式的固定 TOP 值（8 位数据会被限制在 0-1 范围内，从而导致着色器无法正常运行）。

**反馈 TOP 值设置：** 应使用 `top` 参数引用，而非直接输入数据线。“源数据不足”的问题在首次处理后会得到解决，出现“处理依赖循环”警告属于正常现象。

**分辨率限制：** 非商业用途的分辨率上限为 1280×1280，此时需设置 `outputresolution = 'custom'`。

**大型着色器处理：** 先将 GLSL 代码写入 `/tmp/file.glsl` 文件，再通过 `td_write_dat` 或 `td_execute_python` 命令来加载该文件。

**顶点/点数据访问（TD 2025.32 版本）：** 应使用 `point.P[0]`、`point.P[1]`、`point.P[2]` 这种格式，而非 `.x`、`.y`、`.z`。

**扩展功能：** 在 CONSTANT 模式下，`ext0object` 格式的写法为 `"op('./datName').module.ClassName(me)"`。使用 `td_write_dat` 编辑完扩展代码后，需调用 `td_reinit_extension` 函数以重新初始化扩展功能。

**脚本回调函数：** 始终通过 `me.parent()` 或 `scriptOp.parent()` 方法来使用相对路径。

**节点清理操作：** 在遍历节点之前，务必先执行 `list(root.children)` 来获取所有子节点列表，并同时检查每个节点的 `valid` 状态。

```python
# via td_execute_python:
root = op('/project1')
rec = root.create(moviefileoutTOP, 'recorder')
op('/project1/out').outputConnectors[0].connect(rec.inputConnectors[0])
rec.par.type = 'movie'
rec.par.file = '/tmp/output.mov'
rec.par.videocodec = 'prores'  # Apple ProRes — NOT license-restricted on macOS
rec.par.record = True   # start
# rec.par.record = False  # stop (call separately later)
```

H.264/H.265/AV1编码需要商业许可证。在Mac系统中可使用`prores`格式，或作为备选方案使用`mjpa`格式。  
提取帧的命令为：`ffmpeg -i /tmp/output.mov -vframes 120 /tmp/frames/frame_%06d.png`  

**TOP.save()函数不适用于动画处理**——它每次都会捕获相同的GPU纹理，应始终使用MovieFileOut格式。  

### 开始录制前的检查清单

1. 通过`td_get_perf`功能确认帧率大于0。若帧率为0，则录制的视频将为空文件。相关问题可参考故障排除指南中的#38-39条。  
2. 通过`td_get_screenshot`功能检查着色器输出是否为黑色。出现黑色输出说明存在着色器错误或输入数据缺失，相关问题可参考故障排除指南中的#8、#40条。  
3. 若需录制音频，请先让音频开始播放，然后再延迟3帧开始录制。相关问题可参考故障排除指南中的#19条。  
4. 必须在开始录制之前设定输出路径——若在同一个脚本中同时设置这两个参数，可能会导致竞态条件。  

## 基于音频信号的GLSL实现方案（经验证有效）

### 正确的信号处理流程（2026年4月测试通过）

```
AudioFileIn CHOP (playmode=sequential)
  → AudioSpectrum CHOP (FFT=512, outputmenu=setmanually, outlength=256, timeslice=ON)
  → Math CHOP (gain=10)
  → CHOP to TOP (dataformat=r, layout=rowscropped)
  → GLSL TOP input 1 (spectrum texture, 256x2)

Constant TOP (rgba32float, time) → GLSL TOP input 0
GLSL TOP → Null TOP → MovieFileOut
```

### 关键的音频响应规则（经实测验证）

1. **TimeSlice 必须保持开启状态**，才能用于 AudioSpectrum 功能。若关闭，则会处理整个音频文件——即超过 24000 个采样点——从而导致数据被截断并出现顶部溢出现象。
2. 需通过 `outputmenu='setmanually'` 和 `outlength=256` 参数**手动将输出长度设置为 256**。默认输出长度为 22050 个采样点。
3. **切勿使用 Lag CHOP 方法来平滑频谱数据**。Lag CHOP 在时间切片模式下运行，会将 256 个采样点扩展到 2400 多个采样点，并将所有数值平均至接近零的水平（约 1e-06）。这样一来，着色器将无法接收到可用数据。这在测试中是导致音频同步故障的最主要原因。
4. **同样也不建议使用 Filter CHOP**——它也会引发与频谱数据相同的时间切片扩展问题。
5. 如有需要，可通过在 GLSL 着色器中使用带反馈纹理的时间插值功能来实现平滑处理：`mix(prevValue, newValue, 0.3)`。此方法可实现完美帧同步，且不会产生任何管线延迟。
6. **CHOP to TOP 的数据格式为 'r'，布局方式为 'rowscropped'**。频谱输出的尺寸为 256×2（立体声）。第一个声道的采样点位于 y=0.25 处。
7. **数学增益值应为 10（而非 5）**。原始频谱数据在低频段的数值约为 0.19，经过 10 倍的增益处理后，着色器可获得的可用数值约为 5.0。
8. **无需使用 Resample CHOP**。可直接通过 AudioSpectrum 的 `outlength` 参数来控制输出大小。

### GLSL 频谱采样方式

```glsl
// Input 0 = time (1x1 rgba32float), Input 1 = spectrum (256x2)
float iTime = texture(sTD2DInputs[0], vec2(0.5)).r;

// Sample multiple points per band and average for stability:
// NOTE: y=0.25 for first channel (stereo texture is 256x2, first row center is 0.25)
float bass = (texture(sTD2DInputs[1], vec2(0.02, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.05, 0.25)).r) / 2.0;
float mid  = (texture(sTD2DInputs[1], vec2(0.2, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.35, 0.25)).r) / 2.0;
float hi   = (texture(sTD2DInputs[1], vec2(0.6, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.8, 0.25)).r) / 2.0;
```

完整的构建脚本及着色器代码请参阅 `references/network-patterns.md`。

## 操作符快速参考

| 类别 | 颜色 | Python类名 / MCP类型 | 后缀 |
|------|------|-------------------|------|
| TOP | 紫色 | noiseTOP、glslTOP、compositeTOP、levelTop、blurTOP、textTOP、nullTOP | TOP |
| CHOP | 绿色 | audiofileinCHOP、audiospectrumCHOP、mathCHOP、lfoCHOP、constantCHOP | CHOP |
| SOP | 蓝色 | gridSOP、sphereSOP、transformSOP、noiseSOP | SOP |
| DAT | 白色 | textDAT、tableDAT、scriptDAT、webserverDAT | DAT |
| MAT | 黄色 | phongMAT、pbrMAT、glslMAT、constMAT | MAT |
| COMP | 灰色 | geometryCOMP、containerCOMP、cameraCOMP、lightCOMP、windowCOMP | COMP |

## 安全注意事项

- MCP仅能在本地主机运行（端口40404），且不支持身份验证——任何本地进程均可发送命令。
- `td_execute_python` 以TD进程用户的身份拥有对TD Python环境及文件系统的完全访问权限。
- `setup.sh`会从官方的404zero.com地址下载twozero.tox文件。如有疑虑，请自行核对下载内容。
- 该技能绝不会将数据发送到本地主机之外，所有MCP通信均在本地完成。

## 参考资料

| File | What |
|------|------|
| `references/pitfalls.md` | Hard-won lessons from real sessions |
| `references/operators.md` | All operator families with params and use cases |
| `references/network-patterns.md` | Recipes: audio-reactive, generative, GLSL, instancing |
| `references/mcp-tools.md` | Full twozero MCP tool parameter schemas |
| `references/python-api.md` | TD Python: op(), scripting, extensions |
| `references/troubleshooting.md` | Connection diagnostics, debugging |
| `references/glsl.md` | GLSL uniforms, built-in functions, shader templates |
| `references/postfx.md` | Post-FX: bloom, CRT, chromatic aberration, feedback glow |
| `references/layout-compositor.md` | HUD layout patterns, panel grids, BSP-style layouts |
| `references/operator-tips.md` | Wireframe rendering, feedback TOP setup |
| `references/geometry-comp.md` | Geometry COMP: instancing, POP vs SOP, morphing |
| `references/audio-reactive.md` | Audio band extraction, beat detection, envelope following |
| `references/animation.md` | LFOs, timers, keyframes, easing, expression-driven motion |
| `references/midi-osc.md` | MIDI/OSC controllers, TouchOSC, multi-machine sync |
| `references/particles.md` | POPs and legacy particleSOP — emission, forces, collisions |
| `references/projection-mapping.md` | Multi-window output, corner pin, mesh warp, edge blending |
| `references/external-data.md` | HTTP, WebSocket, MQTT, Serial, TCP, webserverDAT |
| `references/panel-ui.md` | Custom params, panel COMPs, button/slider/field, panelExecuteDAT |
| `references/replicator.md` | replicatorCOMP — data-driven cloning, layouts, callbacks |
| `references/dat-scripting.md` | Execute DAT family — chop/dat/parameter/panel/op/executeDAT |
| `references/3d-scene.md` | Lighting rigs, shadows, IBL/cubemaps, multi-camera, PBR |
| `scripts/setup.sh` | Automated setup script |

> 你并非在编写代码，而是在引导流程。
