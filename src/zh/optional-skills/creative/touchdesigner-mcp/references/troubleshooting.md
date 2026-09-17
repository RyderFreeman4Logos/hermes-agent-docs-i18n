# TouchDesigner 故障排除（twozero MCP）

> 详细的经验教训汇总请参阅 `references/pitfalls.md` 文件。

## 1. 连接问题

### 端口 40404 无响应

请按以下顺序进行检查：

1. TouchDesigner 是否正在运行？
   ```bash
   pgrep TouchDesigner
   ```

1b. 快速中心节点健康检查（无需使用 JSON-RPC）：
   通过向 MCP 地址发送普通的 GET 请求，即可获取实例信息：
   ```
   curl -s http://localhost:40404/mcp
   ```
返回值格式为：`{"hub": true, "pid": ..., "instances": {"127.0.0.1_PID": {"project": "...", "tdVersion": "...", ...}}}`  
如果返回的是 JSON 格式但 `instances` 字段为空，说明 TD 已在运行，但 twozero 尚未完成注册。

2. TD 中是否已安装 twozero？  
打开 TD Palette Browser，应能看到 twozero 的列表。若未显示，则需进行安装。

3. twozero 的设置中是否启用了 MCP？  
在 TD 中打开 twozero 的偏好设置，确认 MCP 服务器开关处于开启状态。

4. 直接测试端口连接：
   ```bash
   nc -z 127.0.0.1 40404
   ```

5. 测试 MCP 接口：
   ```bash
   curl -s http://localhost:40404/mcp
   ```
应返回包含 hub 信息的 JSON 数据。若能返回，则说明服务器正在运行。

### Hub 已响应但无 TD 实例

twozero MCP hub 正在运行，但 TD 尚未注册。可能原因包括：
- TD 项目尚未加载（仍处于启动界面）
- 当前项目中未初始化 twozero COMP
- twozero 版本不匹配

解决方法：打开或重新加载包含 twozero COMP 的 TD 项目。可使用 `td_list_instances` 查看已注册的 TD 实例。

### 多实例配置

twozero 会自动为多个 TD 实例分配端口：
- 第一个实例：40404
- 第二个实例：40405
- 第三个实例：40406
- 以此类推

可使用 `td_list_instances` 查看所有正在运行的实例及其对应的端口。

## 2. MCP 工具错误

### td_execute_python 返回错误

td_execute_python 返回的错误信息通常包含 Python 的堆栈跟踪信息。
若信息不够清晰，可使用 `td_read_textport` 查看完整的 TD 控制台输出——Python 异常信息总会显示在那里。

常见原因包括：
- 脚本中存在语法错误
- 引用了不存在的节点（op() 返回 None，随后又尝试对 None 调用 .par 方法）
- 使用了错误的参数名称（详见 pitfalls.md）

### td_set_operator_pars 失败

参数名称不匹配是导致该问题的首要原因。该工具会验证参数名称并返回明确的错误提示，但必须使用完全正确的名称。

解决方法：务必先调用 `td_get_par_info` 来获取真实的参数名称：
```
td_get_par_info(op_type='glslTOP')
td_get_par_info(op_type='noiseTOP')
```

### td_create_operator 类型名称错误规范

操作符类型名称应采用带后缀的驼峰式命名法：
- 正确示例：noiseTOP、glslTOP、levelTOP、compositeTOP、audiospectrumCHOP
- 错误示例：NoiseTOP、noise_top、NOISE TOP、Noise

### 通过 td_get_operator_info 进行深度查看

若对操作符的任何方面（参数、输入、输出、状态）存在疑问：
```
td_get_operator_info(path='/project1/noise1', detail='full')
```

## 3. 参数识别

重要提示：务必使用 `td_get_par_info` 功能来获取参数名称。

该智能体的大语言模型训练数据中包含错误的 TouchDesigner 参数名称，切勿轻信这些信息。常见的错误参数对包括 `dat` 与 `pixeldat`、`colora` 与 `alpha`、`sizex` 与 `size` 等，完整列表请参阅 `pitfalls.md` 文件。

操作流程：
1. `td_get_par_info(op_type='glslTOP')` —— 获取某一类型的全部参数
2. `td_get_operator_info(path='/project1/mynode', detail='full')` —— 获取特定实例的参数
3. 仅使用这些工具返回的参数名称

## 4. 性能优化

### 排查性能缓慢问题

可使用 `td_get_perf` 功能查看哪些运算符会导致性能下降。重点关注处理时间——若每帧的处理时间超过 1 毫秒，就需要进一步排查。

常见原因包括：
- 分辨率过高（尤其是在非商业许可版本中）
- 复杂的 GLSL 着色器
- 过多的 TOP 到 CHOP 或 CHOP 到 TOP 的数据传输（即 GPU 与 CPU 之间的内存复制操作）
- 无衰减机制的反馈循环（数值会不断累积，导致内存占用持续增加）

### 非商业许可的限制

- 分辨率上限：1280x1280。即使将分辨率设置为 1920，实际也会被强制限制在 1280。
- H.264/H.265/AV1 编码需要商业许可，建议使用 ProRes 或 Hap 格式。
- 禁止将生成内容用于商业用途。

在完成创作后，请务必检查实际的有效分辨率。
```python
n.cook(force=True)
actual = str(n.width) + 'x' + str(n.height)
```

## 5. Hermes 配置

### 配置文件位置

` $HERMES_HOME/config.yaml`（若未设置 `HERMES_HOME`，则默认为 `~/.hermes/config.yaml`）

### MCP 条目格式

twozero TD 条目的格式应如下所示：
```yaml
mcpServers:
  twozero_td:
    url: http://localhost:40404/mcp
```

### 配置更改后

若要使更改生效，需重新启动 Hermes 会话。MCP 连接是在会话启动时建立的。

### 验证 MCP 工具是否可用

重启后，会话日志应显示已注册 twozero MCP 工具。如果工具显示已注册但无法调用，请检查以下内容：
- twozero MCP hub 是否仍在运行（可使用上述 curl 命令进行测试）
- TD 是否仍在运行且已加载项目
- 无防火墙阻止 localhost:40404 的访问

## 6. 节点创建问题

### “未找到节点类型”错误

节点类型字符串有误。应使用带系列后缀的驼峰命名法：
- 错误示例：NoiseTop、noise_top、NOISE TOP
- 正确示例：noiseTOP

### 节点已创建但不可见

请检查 parentPath 参数——应使用如 /project1 这样的绝对路径。默认的项目根目录为 /project1。系统节点位于 /、/ui、/sys、/local、/perform 目录下。请勿在 /project1 之外创建用户节点。

### 无法在非 COMP 内部创建节点

只有 COMP 类型操作符（如 Container、Base、Geometry 等）才能包含子节点。不得在 TOP、CHOP、SOP、DAT 或 MAT 类型中创建节点。

## 7. 连接问题

### 不同系列间的连接

TOP 只能连接到 TOP，CHOP 只能连接到 CHOP，SOP 只能连接到 SOP，DAT 只能连接到 DAT。如需实现跨类型连接，可使用转换操作符进行桥接，例如 choptoTOP、topToCHOP、soptoDAT 等。

注意：choptoTOP 没有输入连接器，应改用 par.chop 引用方式。
```python
spec_tex.par.chop = resample_node  # correct
# NOT: resample.outputConnectors[0].connect(spec_tex.inputConnectors[0])
```

### 反馈循环

切勿直接创建 A -> B -> A 的结构。应使用反馈 TOP：
```python
fb = root.create(feedbackTOP, 'fb')
fb.par.top = comp.path          # reference only, no wire to fb input
fb.outputConnectors[0].connect(next_node)
```
在链式中出现“检测到Cook依赖循环”警告属于正常现象，且是正确的。

## 8. GLSL相关问题

### 着色器编译错误不会产生任何提示

GLSL TOP会在用户界面中显示黄色警告，但node.errors()函数可能返回空值。同时请检查node.warnings()函数。如需查看完整的编译输出，可创建一个指向GLSL TOP的Info DAT文件。

### TD GLSL的特定要求

- 使用GLSL 4.60版本（Vulkan后端）。GLSL 3.30及更早版本已不再支持。
- UV坐标：使用vUV.st（而非gl_FragCoord）。
- 输入纹理：sTD2DInputs[0]。
- 输出格式：layout(location = 0) out vec4 fragColor。
- macOS系统的重要注意事项：务必使用TDOutputSwizzle(color)函数对输出结果进行封装处理。
- 不存在内置的时间统一变量。需通过GLSL TOP Values页面或Constant TOP来传递时间值。

## 9. 录制相关问题

### H.264/H.265/AV1编码格式需要商业许可证

在MacOS系统上建议使用Apple ProRes编码格式（支持硬件加速，且无需许可证限制）：
```python
rec.par.videocodec = 'prores'  # Preferred on macOS — lossless, Non-Commercial OK
# rec.par.videocodec = 'mjpa'  # Fallback — lossy, works everywhere
```

### MovieFileOut 类没有 .record() 方法

请使用 toggle 参数：
```python
rec.par.record = True   # start
rec.par.record = False  # stop
```

### 所有导出的帧完全一致

若频繁调用TOP.save()，则捕获的帧会保持相同。如需进行实时录制，请使用MovieFileOut。若希望获得精确到单帧的输出结果，请将project.realTime设置为False。
