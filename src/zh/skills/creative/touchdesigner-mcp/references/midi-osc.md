# MIDI / OSC 参考手册

外部控制器输入与输出——包括 MIDI 硬件、TouchOSC 移动界面，以及通过网络进行的 OSC 路由。

对于基于音频生成的 MIDI 模式（通过频谱分析触发音轨），请另请参阅 `audio-reactive.md`。

---

## MIDI 输入 —— 硬件控制器

### 设备检测

首先列出已连接的 MIDI 设备。可使用 `midiinDAT` 工具进行枚举：

```python
mdat = root.create(midiinDAT, 'mid_devices')
# Read available device names from the DAT after one cook
```

或者直接通过 Python 实现：

```python
# In td_execute_python
import td
devices = [d for d in op.MIDI.devices]   # verify with td_get_docs('midi')
```

由于不同版本的 TD 其 API 接口可能有所差异，请使用 `td_get_docs(topic='midi')` 命令来验证相关接口。

### MIDI 输入的 CHOP 功能

标准模式：

```python
midi_in = root.create(midiinCHOP, 'midi_in')
midi_in.par.device = 0               # device index from discovery
midi_in.par.activechan = True
```

输出通道遵循 `chCcN` 和 `chCnN` 这一命名规则：
- `ch1c74` — 第1个通道，传入74个抄送者
- `ch1n60` — 第1个通道，传入60（中央C）——对应值为力度值，范围为0-127

**将抄送者数量映射为参数：**

```python
op('/project1/bloom1').par.threshold.mode = ParMode.EXPRESSION
op('/project1/bloom1').par.threshold.expr = "op('midi_in')['ch1c74'][0] / 127.0"
```

**将音符映射为触发信号：**

`midiinCHOP` 输出的音符在按住时具有相应的速度值，松开时则为 0。可使用 `triggerCHOP` 将按住的音符转换为脉冲信号：

```python
trig = root.create(triggerCHOP, 'note_trig')
trig.par.threshold = 1
trig.par.triggeron = 'increase'
trig.inputConnectors[0].connect(op('midi_in'))
# Filter to a single channel via a selectCHOP if desired
```

### MIDI 学习模式

在无法提前知晓控制器 CC 布局时，可使用该模式创建可重复使用的学习方案：

1. 在其后面添加 `midiinCHOP` 和 `selectCHOP`。
2. 用户转动控制器旋钮。
3. 通过 `td_read_chop` 函数读取 `midiinCHOP` 的数据，确定哪个通道的数值不为零——该通道即为当前激活的 CC。
4. 将 `selectCHOP.par.channames` 的值设置为该通道名称。
5. 将映射关系保存到 `tableDAT` 文件中，以便在不同会话间保持一致。

---

## MIDI 输出

```python
midi_out = root.create(midioutCHOP, 'midi_out')
midi_out.par.device = 0
midi_out.par.outputformat = 'continuous'    # 'continuous' | 'event'

# Drive an output: send out a CC mapped from any 0-1 source
src = root.create(constantCHOP, 'cc_src')
src.par.name0 = 'ch1c20'
src.par.value0 = 0.5
midi_out.inputConnectors[0].connect(src)
```

针对注释事件，应使用 `event` 模式，并通过 `pulseCHOP` 或 `triggerCHOP` 来触发该值的发送。

---

## OSC 输入 — 网络控制

OSC 是比 MIDI 更具灵活性的通信协议。它被广泛用于以下场景：
- TouchOSC / Lemur 移动控制台
- 展示控制系统（QLab、Watchout）
- 应用程序间同步（通过 Max for Live 连接 Ableton，以及 Resolume 等）

### OSC 输入断续发送功能

```python
osc_in = root.create(oscinCHOP, 'osc_in')
osc_in.par.port = 7000             # listen on UDP 7000
osc_in.par.localaddress = ''       # empty = all interfaces
osc_in.par.queued = False          # immediate vs. queued processing
```

每个接收到的 OSC 地址都会对应一个通道。例如，`/scene/1/intensity` 会生成名为 `scene_1_intensity` 的通道（TD 会将斜杠自动替换为下划线）。

**常见注意事项：** TD 仅会在该地址接收到第一条消息后才会创建对应的通道。因此，在设置过程中请从控制器发送一条“hello”消息，或手动预先指定通道名称。

### 用于原始事件的 OSC In DAT 格式

当需要完全访问消息内容时（如包含多个类型化的参数、带有括号或正则表达式的地址），可使用 `oscinDAT` 格式。

```python
osc_dat = root.create(oscinDAT, 'osc_events')
osc_dat.par.port = 7001
# Each row: timestamp, address, type tags, args...
```

通过监听 `oscinDAT` 的 `datExecuteDAT` 来驱动逻辑执行：

```python
def onTableChange(dat):
    last = dat[dat.numRows - 1, 'message']
    parsed = last.val.split()
    addr = parsed[0]
    args = parsed[1:]
    if addr == '/scene/trigger':
        op('/project1/scene_switcher').par.index = int(args[0])
    return
```

## OSC 输出——发送至外部应用

```python
osc_out = root.create(oscoutCHOP, 'osc_out')
osc_out.par.netaddress = '127.0.0.1'    # destination IP
osc_out.par.port = 9000

# Channel names become OSC addresses
src = root.create(constantCHOP, 'send')
src.par.name0 = 'scene/intensity'        # → /scene/intensity
src.par.value0 = 0.7
osc_out.inputConnectors[0].connect(src)
```

**频道与地址的映射：** TD 会自动在地址前添加 `/` 符号。若需在频道名称中实现嵌套结构，也可直接使用 `/`。

对于一次性发送的字符串或已定义类型的消息，可使用 `oscoutDAT` 并调用 `.sendOSC(address, args)` 方法：

```python
op('osc_out_dat').sendOSC('/scene/trigger', [1, 'fade'])
```

## TouchOSC / 移动端用户界面模式

通过手机或平板电脑实现实时视觉特效控制的常用配置步骤：

1. **配置 TouchOSC 布局** — 为每个控制功能分配对应的 OSC 地址，例如 `/vj/master`、`/vj/scene/1` 等。
2. **确定设备的局域网 IP 地址** — TouchOSC 需要指向该地址才能正常工作。
3. **TD 在 `oscinCHOP.par.port = 8000`（或其他指定端口）上监听信号**。
4. **通过表达式将通道映射到相应参数**：

```python
op('/project1/master_level').par.opacity.mode = ParMode.EXPRESSION
op('/project1/master_level').par.opacity.expr = "op('osc_in')['vj_master']"
```

5. 通过 `oscoutCHOP` 向控制器**发送反馈**——这有助于在多台设备之间同步状态。

---

## 网络 / 多机器架构

局域网环境下的 OSC 功能可即插即用。对于多 TD 实例的同步（例如投影集群）：

- 一个 TD 担任**主节点**，通过 OSC 广播 `/sync/...` 消息；
- 其他工作 TD 运行 `oscinCHOP`，并在相同端口上监听；
- 在主节点的 `oscoutCHOP.par.netaddress` 中设置 UDP **广播地址**（例如 `192.168.1.255`），从而将消息发送给所有节点。

若需要在广域网环境中保证稳定性，建议使用 `webserverDAT` 或 `websocketDAT` 并结合外部中继——因为 UDP 的数据丢失往往难以察觉。

---

## 常见问题与注意事项

1. **MIDI 设备索引**——设备编号 `0` 对应 TD 首次枚举到的那个设备。若重新排序设备，其编号可能会发生变化。尽可能通过设备名称来指定参数。
2. **OSC 通道名称**——TD 会在接收到第一条消息后才会创建相应通道。新通道的出现会导致之前已生成的依赖关系失效，从而引发一帧的延迟。
3. **OSC 队列模式**——设置 `par.queued = True` 可将处理任务延迟到每帧批量处理时再执行。虽然这样能降低延迟，但同一帧内到达的消息会被合并为最后一个值。触发器建议关闭此选项，而连续控制的旋钮则可开启。
4. **MIDI 时钟与传输协议**——`midiinCHOP` 会在有可用时钟信号时报告其频率。若您的 TD 版本支持，可使用 `midisyncCHOP`；否则也可通过计算时钟脉冲的频率来获取 BPM（每个四分音符对应 24 次脉冲）。
5. **延迟问题**——有线 MIDI 的延迟约为 1-3 毫秒；而 WiFi OSC 的延迟则在 10-30 毫秒之间，且还存在抖动现象。对于需要精确同步的场景，建议使用有线连接。
6. **端口冲突**——在大多数操作系统中，一个 UDP 端口只能被一个进程绑定。如果 `oscinCHOP` 显示没有数据传输，可检查是否有其他应用程序（如 Max、Ableton 等）正在占用该端口。

---

## 快速应用方案

| 目标 | 操作链 |
|---|---|
| 旋钮控制模糊效果强度 | `midiinCHOP` → 控制 `bloom.par.threshold` 的表达式参数 |
| 音符触发场景切换 | `midiinCHOP` → `triggerCHOP` → `selectCHOP` → 控制 `switchTOP.par.index` |
| 手机滑块控制主音量 | TouchOSC 的 `/master` 信号 → `oscinCHOP` → 控制输出参数 `level.par.opacity` 的表达式 |
| TD 触发 Resolume 场景 | `oscoutCHOP` 的通道 `composition/layers/1/clips/1/connect` → Resolume 在 7000 端口监听该信号 |
| 多投影仪同步 | 主 TD 的 `oscoutCHOP` 广播信号 → 各工作 TD 的 `oscinCHOP` 接收信号 |
