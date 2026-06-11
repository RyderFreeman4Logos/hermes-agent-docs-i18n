# 基于音频的响应式参考方案

用于根据音频驱动视觉效果的模式——频谱分析、节拍检测、包络跟踪。

## 音频输入

```python
# Live input from audio interface
audio_in = root.create(audiodeviceinCHOP, 'audio_in')
audio_in.par.rate = 44100

# OR: from audio file (for testing)
audio_file = root.create(audiofileinCHOP, 'audio_in')
audio_file.par.file = '/path/to/track.wav'
audio_file.par.play = True
audio_file.par.repeat = 'on'       # NOT par.loop
audio_file.par.playmode = 'locked'
```

## 音频频段提取（已验证版本 TD 2025.32460）

请使用 `audiofilterCHOP` 功能进行频段分离（切勿使用按通道索引指定的 `selectCHOP`）：

```python
# Audio input
af = root.create(audiofileinCHOP, 'audio_in')
af.par.file = path
af.par.play = True
af.par.repeat = 'on'
af.par.playmode = 'locked'

# Low band: lowpass @ 250Hz
flt_low = root.create(audiofilterCHOP, 'flt_low')
flt_low.par.filter = 'lowpass'
flt_low.par.cutofffrequency = 250
flt_low.par.rolloff = 2
flt_low.inputConnectors[0].connect(af)

# Mid band: highpass@250 → lowpass@4000
flt_mid_hp = root.create(audiofilterCHOP, 'flt_mid_hp')
flt_mid_hp.par.filter = 'highpass'
flt_mid_hp.par.cutofffrequency = 250
flt_mid_hp.par.rolloff = 2
flt_mid_hp.inputConnectors[0].connect(af)

flt_mid_lp = root.create(audiofilterCHOP, 'flt_mid_lp')
flt_mid_lp.par.filter = 'lowpass'
flt_mid_lp.par.cutofffrequency = 4000
flt_mid_lp.par.rolloff = 2
flt_mid_lp.inputConnectors[0].connect(flt_mid_hp)

# High band: highpass @ 4000Hz
flt_high = root.create(audiofilterCHOP, 'flt_high')
flt_high.par.filter = 'highpass'
flt_high.par.cutofffrequency = 4000
flt_high.par.rolloff = 2
flt_high.inputConnectors[0].connect(af)

# Per-band: RMS → lag → gain → clamp
for name, filt in [('low', flt_low), ('mid', flt_mid_lp), ('high', flt_high)]:
    rms = root.create(analyzeCHOP, f'rms_{name}')
    rms.par.function = 'rmspower'  # NOT 'rms'
    rms.inputConnectors[0].connect(filt)

    lag = root.create(lagCHOP, f'lag_{name}')
    lag.par.lag1 = 0.05   # attack (NOT par.lagin)
    lag.par.lag2 = 0.25   # release (NOT par.lagout)
    lag.inputConnectors[0].connect(rms)

    math = root.create(mathCHOP, f'scale_{name}')
    math.par.gain = 8.0
    math.inputConnectors[0].connect(lag)

    # mathCHOP has NO par.clamp — use limitCHOP
    lim = root.create(limitCHOP, f'clamp_{name}')
    lim.par.type = 'clamp'
    lim.par.min = 0.0
    lim.par.max = 1.0
    lim.inputConnectors[0].connect(math)

    null = root.create(nullCHOP, f'out_{name}')
    null.inputConnectors[0].connect(lim)
    null.viewer = True
```

**2025年关键技术文档更正内容：**
- `analyzeCHOP.par.function` 的值应为 `'rmspower'`，而非 `'rms'`
- `lagCHOP.par.lag1` / `par.lag2` 的写法应为 `par.lag1` / `par.lag2`，而非 `par.lagin` / `par.lagout`
- `mathCHOP` 中不存在 `par.clamp` 参数——需使用独立的 `limitCHOP` 参数

---

## 节拍/起音检测

### 踢鼓检测（基于斜率变化触发）

```python
slope = root.create(slopeCHOP, 'kick_slope')
slope.inputConnectors[0].connect(op('out_low'))

trig = root.create(triggerCHOP, 'kick_trig')
trig.par.threshold = 0.12
trig.par.attack = 0.005    # NOT par.attacktime
trig.par.decay = 0.15       # NOT par.decaytime
trig.par.triggeron = 'increase'
trig.inputConnectors[0].connect(slope)

kick_out = root.create(nullCHOP, 'out_kick')
kick_out.inputConnectors[0].connect(trig)
```

## 将音频传递给 GLSL

```python
glsl.par.vec0name = 'uLow'
glsl.par.vec0valuex.expr = "op('out_low')['chan1']"
glsl.par.vec0valuex.mode = ParMode.EXPRESSION

glsl.par.vec1name = 'uKick'
glsl.par.vec1valuex.expr = "op('out_kick')['chan1']"
glsl.par.vec1valuex.mode = ParMode.EXPRESSION
```

```glsl
uniform float uLow;
uniform float uKick;
float scale = 1.0 + uKick * 0.4 + uLow * 0.2;
```

## 标准音频总线架构

推荐结构：

```
audiodeviceinCHOP (audio_in)
        ↓
  [null_audio_in]
        ├──→ audiofilterCHOP (lowpass@250) → analyzeCHOP → lagCHOP → mathCHOP → limitCHOP → null
        ├──→ audiofilterCHOP (bandpass@250-4k) → analyzeCHOP → lagCHOP → mathCHOP → limitCHOP → null
        ├──→ audiofilterCHOP (highpass@4k) → analyzeCHOP → lagCHOP → mathCHOP → limitCHOP → null
        │
        └──→ slopeCHOP → triggerCHOP (beat_trigger)
```

请将整个音频总线置于 `baseCOMP`（例如 `audio_bus`）之中，并通过可视化网络中的路径来引用它。  

---

## MIDI输入

```python
midi_in = root.create(midiinCHOP, 'midi_in')
midi_in.par.device = 0  # Check midiinDAT for device index
# Outputs channels named by MIDI note/CC: 'ch1n60', 'ch1c74', etc.

# Map CC to a parameter
op('bloom1').par.threshold.mode = ParMode.EXPRESSION
op('bloom1').par.threshold.expr = "op('midi_in')['ch1c74'][0]"
```

## 重要提示：切勿使用 Lag CHOP 进行频谱平滑处理

在时间切片模式下，Lag CHOP 会将 256 个样本的频谱扩展至 1600–2400 个样本，并将所有数值平均到接近零的水平（约 1e-06）。这样一来，着色器将无法获得任何可用数据。建议直接使用 `mathCHOP(gain=8)`，或通过带有反馈纹理的时间插值技术在 GLSL 中实现平滑处理。

实测结果：
- 未使用 Lag CHOP 时：低频段数值为 5.0–5.4（信号强劲，可正常使用）
- 使用 Lag CHOP 后：所有频段数值均为 0.000001（信号完全消失）
