# TouchDesigner 网络模式

涵盖常见创意编程任务的完整网络配方。每种模式都会展示操作符链、用于构建该模式的MCP工具调用方式以及关键参数设置。

## 基于音频的视觉效果

### 模式1：音频频谱 -> 噪声位移

利用音频信号控制噪声参数，从而生成富有动态感且能响应音乐的纹理效果。

```
Audio File In CHOP -> Audio Spectrum CHOP -> Math CHOP (scale)
                                                |
                                                v (export to noise params)
                          Noise TOP -> Level TOP -> Feedback TOP -> Composite TOP -> Null TOP (out)
                                                        ^                |
                                                        |________________|
```

**MCP 构建流程：**

```
1. td_create_operator(parent="/project1", type="audiofileinChop", name="audio_in")
2. td_create_operator(parent="/project1", type="audiospectrumChop", name="spectrum")
3. td_create_operator(parent="/project1", type="mathChop", name="spectrum_scale")
4. td_create_operator(parent="/project1", type="noiseTop", name="noise1")
5. td_create_operator(parent="/project1", type="levelTop", name="level1")
6. td_create_operator(parent="/project1", type="feedbackTop", name="feedback1")
7. td_create_operator(parent="/project1", type="compositeTop", name="comp1")
8. td_create_operator(parent="/project1", type="nullTop", name="out")

9. td_set_operator_pars(path="/project1/audio_in",
     properties={"file": "/path/to/music.wav", "play": true})
10. td_set_operator_pars(path="/project1/spectrum",
     properties={"size": 512})
11. td_set_operator_pars(path="/project1/spectrum_scale",
     properties={"gain": 2.0, "postoff": 0.0})
12. td_set_operator_pars(path="/project1/noise1",
     properties={"type": 1, "monochrome": false, "resolutionw": 1280, "resolutionh": 720,
                  "period": 4.0, "harmonics": 3, "amp": 1.0})
13. td_set_operator_pars(path="/project1/level1",
     properties={"opacity": 0.95, "gamma1": 0.75})
14. td_set_operator_pars(path="/project1/feedback1",
     properties={"top": "/project1/comp1"})
15. td_set_operator_pars(path="/project1/comp1",
     properties={"operand": 0})

16. td_execute_python: """
op('/project1/audio_in').outputConnectors[0].connect(op('/project1/spectrum'))
op('/project1/spectrum').outputConnectors[0].connect(op('/project1/spectrum_scale'))
op('/project1/noise1').outputConnectors[0].connect(op('/project1/level1'))
op('/project1/level1').outputConnectors[0].connect(op('/project1/comp1').inputConnectors[0])
op('/project1/feedback1').outputConnectors[0].connect(op('/project1/comp1').inputConnectors[1])
op('/project1/comp1').outputConnectors[0].connect(op('/project1/out'))
"""

17. td_execute_python: """
# Export spectrum values to drive noise parameters
# This makes the noise react to audio frequencies
op('/project1/noise1').par.seed.expr = "op('/project1/spectrum_scale')['chan1']"
op('/project1/noise1').par.period.expr = "tdu.remap(op('/project1/spectrum_scale')['chan1'].eval(), 0, 1, 1, 8)"
"""
```

### 模式 2：节拍检测 -> 视觉脉冲

从音频中识别节拍，并触发相应的视觉效果。

```
Audio Device In CHOP -> Audio Spectrum CHOP -> Math CHOP (isolate bass)
                                                    |
                                              Trigger CHOP (envelope)
                                                    |
                                              [export to visual params]
```

**关键参数设置：**

```
# Isolate bass frequencies (20-200 Hz)
Math CHOP: chanop=1 (Add channels), range1low=0, range1high=10
           (first 10 FFT bins = bass frequencies with 512 FFT at 44100Hz)

# ADSR envelope on each beat
Trigger CHOP: attack=0.02, peak=1.0, decay=0.3, sustain=0.0, release=0.1

# Export to visual: Scale, brightness, or color intensity
td_execute_python: "op('/project1/level1').par.brightness1.expr = \"1.0 + op('/project1/trigger1')['chan1'] * 0.5\""
```

### 模式 3：多频段音频 → 多层可视化效果

将音频拆分为不同的频段，针对每个频段生成独立的可视化层次。

```
Audio In -> Spectrum -> Audio Band EQ (3 bands: bass, mid, treble)
                              |
                    +---------+---------+
                    |         |         |
                 Bass      Mids     Treble
                  |          |         |
           Noise TOP   Circle TOP  Text TOP
           (slow,dark) (mid,warm)  (fast,bright)
                  |          |         |
                  +-----+----+----+----+
                        |         |
                   Composite  Composite
                        |
                       Out
```

### 模式 3b：音频响应型 GLSL 分形（经过验证的方案）

这是一个功能完备的完整方案。它首先播放 MP3 文件，随后进行 FFT 分析，将得到的频谱数据作为纹理传递给 GLSL 着色器——其中内部分形结构会对低音作出响应，而外部分形结构则会对高音作出响应。

**网络：**
```
AudioFileIn CHOP → AudioSpectrum CHOP (FFT=512, outlength=256)
    → Math CHOP (gain=10) → CHOP To TOP (256x2 spectrum texture, dataformat=r)
                                                                   ↓
Constant TOP (time, rgba32float) → GLSL TOP (input 0=time, input 1=spectrum) → Null → MovieFileOut
                                                                                        ↓
AudioFileIn CHOP → Audio Device Out CHOP                                          Record to .mov
```

**通过 td_execute_python 进行构建（为确保稳定性，每一步仅执行一次调用）：**

```python
# Step 1: Audio chain
# td_execute_python script:
td_execute_python(code="""
root = op('/project1')
audio = root.create(audiofileinCHOP, 'audio_in')
audio.par.file = '/path/to/music.mp3'
audio.par.playmode = 0  # Locked to timeline
audio.par.volume = 0.5

spec = root.create(audiospectrumCHOP, 'spectrum')
audio.outputConnectors[0].connect(spec.inputConnectors[0])

math_n = root.create(mathCHOP, 'math_norm')
spec.outputConnectors[0].connect(math_n.inputConnectors[0])
math_n.par.gain = 5  # boost signal

resamp = root.create(resampleCHOP, 'resample_spec')
math_n.outputConnectors[0].connect(resamp.inputConnectors[0])
resamp.par.timeslice = True
resamp.par.rate = 256

chop2top = root.create(choptoTOP, 'spectrum_tex')
chop2top.par.chop = resamp  # CHOP To TOP has NO input connectors — use par.chop reference

# Audio output (hear the music)
aout = root.create(audiodeviceoutCHOP, 'audio_out')
audio.outputConnectors[0].connect(aout.inputConnectors[0])
result = 'audio chain ok'
""")

# Step 2: Time driver (MUST be rgba32float — see pitfalls #6)
# td_execute_python script:
td_execute_python(code="""
root = op('/project1')
td = root.create(constantTOP, 'time_driver')
td.par.format = 'rgba32float'
td.par.outputresolution = 'custom'
td.par.resolutionw = 1
td.par.resolutionh = 1
td.par.colorr.expr = "absTime.seconds % 1000.0"
td.par.colorg.expr = "int(absTime.seconds / 1000.0)"
result = 'time ok'
""")

# Step 3: GLSL shader (write to /tmp, load from file)
# td_execute_python script:
td_execute_python(code="""
root = op('/project1')
glsl = root.create(glslTOP, 'audio_shader')
glsl.par.outputresolution = 'custom'
glsl.par.resolutionw = 1280
glsl.par.resolutionh = 720

sd = root.create(textDAT, 'shader_code')
sd.text = open('/tmp/my_shader.glsl').read()
glsl.par.pixeldat = sd

# Wire: input 0 = time, input 1 = spectrum texture
op('/project1/time_driver').outputConnectors[0].connect(glsl.inputConnectors[0])
op('/project1/spectrum_tex').outputConnectors[0].connect(glsl.inputConnectors[1])
result = 'glsl ok'
""")

# Step 4: Output + recorder
# td_execute_python script:
td_execute_python(code="""
root = op('/project1')
out = root.create(nullTOP, 'output')
op('/project1/audio_shader').outputConnectors[0].connect(out.inputConnectors[0])

rec = root.create(moviefileoutTOP, 'recorder')
out.outputConnectors[0].connect(rec.inputConnectors[0])
rec.par.type = 'movie'
rec.par.file = '/tmp/output.mov'
rec.par.videocodec = 'mjpa'
result = 'output ok'
""")
```

**GLSL着色器模式（音频响应分形）：**
```glsl
out vec4 fragColor;

vec3 palette(float t) {
    vec3 a = vec3(0.5); vec3 b = vec3(0.5);
    vec3 c = vec3(1.0); vec3 d = vec3(0.263, 0.416, 0.557);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    // Input 0 = time (1x1 rgba32float constant)
    // Input 1 = audio spectrum (256x2 CHOP To TOP, stereo — sample at y=0.25 for first channel)
    vec4 td = texture(sTD2DInputs[0], vec2(0.5));
    float t = td.r + td.g * 1000.0;

    vec2 res = uTDOutputInfo.res.zw;
    vec2 uv = (gl_FragCoord.xy * 2.0 - res) / min(res.x, res.y);
    vec2 uv0 = uv;
    vec3 finalColor = vec3(0.0);

    float bass = texture(sTD2DInputs[1], vec2(0.05, 0.25)).r;
    float mids = texture(sTD2DInputs[1], vec2(0.25, 0.25)).r;

    for (float i = 0.0; i < 4.0; i++) {
        uv = fract(uv * (1.4 + bass * 0.3)) - 0.5;
        float d = length(uv) * exp(-length(uv0));

        // Sample spectrum at distance: inner=bass, outer=treble
        float freq = texture(sTD2DInputs[1], vec2(clamp(d * 0.5, 0.0, 1.0), 0.25)).r;

        vec3 col = palette(length(uv0) + i * 0.4 + t * 0.35);
        d = sin(d * (7.0 + bass * 4.0) + t * 1.5) / 8.0;
        d = abs(d);
        d = pow(0.012 / d, 1.2 + freq * 0.8 + bass * 0.5);
        finalColor += col * d;
    }

    // Tone mapping
    finalColor = finalColor / (finalColor + vec3(1.0));
    fragColor = TDOutputSwizzle(vec4(finalColor, 1.0));
}
```

**测试中的关键发现：**
- `spectrum_tex`（CHOP To TOP）可生成256x2大小的纹理——x轴坐标表示频率，第一个通道的y值为0.25
- 在`vec2(0.05, 0.0)`位置采样可获得低音效果，在`vec2(0.65, 0.0)`位置采样则可获得高音效果
- 根据像素距离（`d * 0.5`）进行采样，可使内部分形对低音作出反应，外部分形则对高音作出反应
- 在`fract()`缩放功能中加入`bass * 0.3`的参数，能让分形随着低音节奏而“呼吸”
- 由于原始频谱数值非常小，因此需要将Math CHOP的增益设置为5

## 生成艺术

### 模式4：带变换功能的反馈循环

这是一种经典的生成艺术技术——通过递归变换使纹理不断演变。

```
Noise TOP -> Composite TOP -> Level TOP -> Null TOP (out)
                  ^      |
                  |      v
            Transform TOP <- Feedback TOP
```

**MCP 构建流程：**

```
1. td_create_operator(parent="/project1", type="noiseTop", name="seed_noise")
2. td_create_operator(parent="/project1", type="compositeTop", name="mix")
3. td_create_operator(parent="/project1", type="transformTop", name="evolve")
4. td_create_operator(parent="/project1", type="feedbackTop", name="fb")
5. td_create_operator(parent="/project1", type="levelTop", name="color_correct")
6. td_create_operator(parent="/project1", type="nullTop", name="out")

7. td_set_operator_pars(path="/project1/seed_noise",
     properties={"type": 1, "monochrome": false, "period": 2.0, "amp": 0.3,
                  "resolutionw": 1280, "resolutionh": 720})
8. td_set_operator_pars(path="/project1/mix",
     properties={"operand": 27})  # 27 = Screen blend
9. td_set_operator_pars(path="/project1/evolve",
     properties={"sx": 1.003, "sy": 1.003, "rz": 0.5, "extend": 2})  # slight zoom + rotate, repeat edges
10. td_set_operator_pars(path="/project1/fb",
     properties={"top": "/project1/mix"})
11. td_set_operator_pars(path="/project1/color_correct",
     properties={"opacity": 0.98, "gamma1": 0.85})

12. td_execute_python: """
op('/project1/seed_noise').outputConnectors[0].connect(op('/project1/mix').inputConnectors[0])
op('/project1/fb').outputConnectors[0].connect(op('/project1/evolve'))
op('/project1/evolve').outputConnectors[0].connect(op('/project1/mix').inputConnectors[1])
op('/project1/mix').outputConnectors[0].connect(op('/project1/color_correct'))
op('/project1/color_correct').outputConnectors[0].connect(op('/project1/out'))
"""
```

**变化选项：**
- 变换类型更改：`rz`（旋转）、`sx/sy`（缩放）、`tx/ty`（平移）
- 复合运算符更改：屏幕发光、叠加（增亮）、混合（变暗）
- 在反馈循环中加入HSV色调调节，以实现颜色动态变化
- 添加模糊效果，营造梦幻般的柔和感
- 用GLSL TOP函数替代噪声效果，以生成自定义的种子图案

### 模式5：实例化（类粒子系统）

基于CHOP数据或DAT文件，渲染数千个几何体副本，每个副本都具有由这些数据驱动的唯一位置、旋转和缩放参数。

```
Table DAT (instance data) -> DAT to CHOP -> Geometry COMP (instancing on) -> Render TOP
                                              + Sphere SOP (template geometry)
                                              + Constant MAT (material)
                                              + Camera COMP
                                              + Light COMP
```

**MCP 构建流程：**

```
1. td_create_operator(parent="/project1", type="tableDat", name="instance_data")
2. td_create_operator(parent="/project1", type="geometryComp", name="geo1")
3. td_create_operator(parent="/project1/geo1", type="sphereSop", name="sphere")
4. td_create_operator(parent="/project1", type="constMat", name="mat1")
5. td_create_operator(parent="/project1", type="cameraComp", name="cam1")
6. td_create_operator(parent="/project1", type="lightComp", name="light1")
7. td_create_operator(parent="/project1", type="renderTop", name="render1")

8. td_execute_python: """
import random, math
dat = op('/project1/instance_data')
dat.clear()
dat.appendRow(['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'cr', 'cg', 'cb'])
for i in range(500):
    angle = i * 0.1
    r = 2 + i * 0.01
    dat.appendRow([
        str(math.cos(angle) * r),
        str(math.sin(angle) * r),
        str((i - 250) * 0.02),
        '0.05', '0.05', '0.05',
        str(random.random()),
        str(random.random()),
        str(random.random())
    ])
"""

9. td_set_operator_pars(path="/project1/geo1",
     properties={"instancing": true, "instancechop": "",
                  "instancedat": "/project1/instance_data",
                  "material": "/project1/mat1"})
10. td_set_operator_pars(path="/project1/render1",
     properties={"camera": "/project1/cam1", "geometry": "/project1/geo1",
                  "light": "/project1/light1",
                  "resolutionw": 1280, "resolutionh": 720})
11. td_set_operator_pars(path="/project1/cam1",
     properties={"tz": 10})
```

### 模式 6：反应-扩散模型（GLSL）

在 GPU 上运行的经典 Gray-Scott 反应-扩散系统。

```
Text DAT (GLSL code) -> GLSL TOP (resolution, dat reference) -> Feedback TOP
                              ^                                       |
                              |_______________________________________|
                         Level TOP (out)
```

**关键 GLSL 代码（通过 td_execute_python 写入 Text DAT）：**

```glsl
// Gray-Scott reaction-diffusion
uniform float feed;    // 0.037
uniform float kill;    // 0.06
uniform float dA;      // 1.0
uniform float dB;      // 0.5

layout(location = 0) out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec2 texel = 1.0 / uTDOutputInfo.res.zw;

    vec4 c = texture(sTD2DInputs[0], uv);
    float a = c.r;
    float b = c.g;

    // Laplacian (9-point stencil)
    float lA = 0.0, lB = 0.0;
    for(int dx = -1; dx <= 1; dx++) {
        for(int dy = -1; dy <= 1; dy++) {
            float w = (dx == 0 && dy == 0) ? -1.0 : (abs(dx) + abs(dy) == 1 ? 0.2 : 0.05);
            vec4 s = texture(sTD2DInputs[0], uv + vec2(dx, dy) * texel);
            lA += s.r * w;
            lB += s.g * w;
        }
    }

    float reaction = a * b * b;
    float newA = a + (dA * lA - reaction + feed * (1.0 - a));
    float newB = b + (dB * lB + reaction - (kill + feed) * b);

    fragColor = vec4(clamp(newA, 0.0, 1.0), clamp(newB, 0.0, 1.0), 0.0, 1.0);
}
```

## 视频处理

### 模式 7：视频效果链

为视频文件应用一系列连续的效果。

```
Movie File In TOP -> HSV Adjust TOP -> Level TOP -> Blur TOP -> Composite TOP -> Null TOP (out)
                                                                      ^
                                                          Text TOP ---+
```

**MCP 构建流程：**

```
1. td_create_operator(parent="/project1", type="moviefileinTop", name="video_in")
2. td_create_operator(parent="/project1", type="hsvadjustTop", name="color")
3. td_create_operator(parent="/project1", type="levelTop", name="levels")
4. td_create_operator(parent="/project1", type="blurTop", name="blur")
5. td_create_operator(parent="/project1", type="compositeTop", name="overlay")
6. td_create_operator(parent="/project1", type="textTop", name="title")
7. td_create_operator(parent="/project1", type="nullTop", name="out")

8. td_set_operator_pars(path="/project1/video_in",
     properties={"file": "/path/to/video.mp4", "play": true})
9. td_set_operator_pars(path="/project1/color",
     properties={"hueoffset": 0.1, "saturationmult": 1.3})
10. td_set_operator_pars(path="/project1/levels",
     properties={"brightness1": 1.1, "contrast": 1.2, "gamma1": 0.9})
11. td_set_operator_pars(path="/project1/blur",
     properties={"sizex": 2, "sizey": 2})
12. td_set_operator_pars(path="/project1/title",
     properties={"text": "My Video", "fontsizex": 48, "alignx": 1, "aligny": 1})

13. td_execute_python: """
chain = ['video_in', 'color', 'levels', 'blur']
for i in range(len(chain) - 1):
    op(f'/project1/{chain[i]}').outputConnectors[0].connect(op(f'/project1/{chain[i+1]}'))
op('/project1/blur').outputConnectors[0].connect(op('/project1/overlay').inputConnectors[0])
op('/project1/title').outputConnectors[0].connect(op('/project1/overlay').inputConnectors[1])
op('/project1/overlay').outputConnectors[0].connect(op('/project1/out'))
"""
```

### 模式 8：视频录制

将输出内容录制到文件中。**H.264/H.265 格式需要商业许可**——在非商业用途中请使用运动JPEG（`mjpa`）格式。

```
[any TOP chain] -> Null TOP -> Movie File Out TOP
```

```python
# Build via td_execute_python:
root = op('/project1')

# Always put a Null TOP before the recorder
null_out = root.op('out')  # or create one
rec = root.create(moviefileoutTOP, 'recorder')
null_out.outputConnectors[0].connect(rec.inputConnectors[0])

rec.par.type = 'movie'
rec.par.file = '/tmp/output.mov'
rec.par.videocodec = 'mjpa'  # Motion JPEG — works on Non-Commercial

# Start recording (par.record is a toggle — .record() method may not exist)
rec.par.record = True
# ... let TD run for desired duration ...
rec.par.record = False

# For image sequences:
# rec.par.type = 'imagesequence'
# rec.par.imagefiletype = 'png'
# rec.par.file.expr = "'/tmp/frames/out' + me.fileSuffix"  # fileSuffix REQUIRED
```

**常见陷阱：**
- 在同一脚本中同时设置 `par.file` 和 `par.record = True` 可能会导致竞争条件——请使用 `run("...", delayFrames=2)` 来解决。
- 过度频繁调用 `TOP.save()` 总是会捕获到同一帧——对于动画处理，建议使用 MovieFileOut。
- 详情请参阅 `pitfalls.md` 中的第 25-27 条。

### 模式 8b：TD → 外部处理流程（FFmpeg / Python / 后期处理）

将 TD 生成的视觉内容导出，以便在其他工具中进一步使用（如 ffmpeg、Python、ASCII 艺术等）。当需要将 TD 的输出结果与外部处理流程结合时（如 ASCII 转换、Python 渲染链、机器学习推理等），这就是标准的工作流程。

**第一步：在 TD 中录制为视频**

```python
# Preferred: ProRes on macOS (lossless, Non-Commercial OK, ~55MB/s at 1280x720)
rec.par.videocodec = 'prores'
# Fallback for non-macOS: mjpa (Motion JPEG)
# rec.par.videocodec = 'mjpa'
rec.par.record = True
# ... wait N seconds ...
rec.par.record = False
```

**步骤 2：使用 ffmpeg 提取帧**

```bash
# Extract all frames at 30fps
ffmpeg -y -i /tmp/output.mov -vf 'fps=30' /tmp/frames/frame_%06d.png

# Or extract a specific duration
ffmpeg -y -i /tmp/output.mov -t 25 -vf 'fps=30' /tmp/frames/frame_%06d.png

# Or extract specific frame range
ffmpeg -y -i /tmp/output.mov -vf 'select=between(n\,0\,749)' -vsync vfr /tmp/frames/frame_%06d.png
```

**步骤 3：使用 Python 处理帧数据**

```python
from PIL import Image
import os

frames_dir = '/tmp/frames'
output_dir = '/tmp/processed'
os.makedirs(output_dir, exist_ok=True)

for fname in sorted(os.listdir(frames_dir)):
    if not fname.endswith('.png'):
        continue
    img = Image.open(os.path.join(frames_dir, fname))
    # ... apply your processing ...
    img.save(os.path.join(output_dir, fname))
```

**第4步：将处理后的帧与音频重新合并**

```bash
# Create video from processed frames + audio with fade-out
ffmpeg -y \
  -framerate 30 -i /tmp/processed/frame_%06d.png \
  -i /tmp/audio.mp3 \
  -c:v libx264 -pix_fmt yuv420p -crf 18 \
  -c:a aac -b:a 192k \
  -shortest \
  -af 'afade=t=out:st=23:d=2' \
  /tmp/final_output.mp4
```

**重要注意事项：**
- 在时间码录制阶段请使用 ProRes 格式，以避免在合成过程中出现质量损失
- 应以目标输出帧率进行提取（而非时间码的渲染帧率）
- 对于需要音频同步的内容，需使用 Python（scipy FFT）单独分析音频文件，提取每帧的特征数据（如均方根值、频谱带信息、拍频等），以此来调整合成参数
- 在开始录制之前，请务必确认时间码帧率大于 0（参见故障案例 #37、#38）

## 数据可视化

### 模式 9：通过实例化将表格数据转换为柱状图

将表格数据可视化为 3D 柱状图。

```
Table DAT (data) -> Script DAT (transform to instance format) -> DAT to CHOP
                                                                      |
Box SOP -> Geometry COMP (instancing from CHOP) -> Render TOP -> Null TOP (out)
           + PBR MAT
           + Camera COMP
           + Light COMP
```

```python
# Script DAT code to transform data to instance positions
td_execute_python: """
source = op('/project1/data_table')
instance = op('/project1/instance_transform')
instance.clear()
instance.appendRow(['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'cr', 'cg', 'cb'])

for i in range(1, source.numRows):
    value = float(source[i, 'value'])
    name = source[i, 'name']
    instance.appendRow([
        str(i * 1.5),          # x position (spread bars)
        str(value / 2),        # y position (center bar vertically)
        '0',                   # z position
        '1', str(value), '1',  # scale (height = data value)
        '0.2', '0.6', '1.0'   # color (blue)
    ])
"""
```

### 模式 9b：音频响应型 GLSL 分形（经验证的方案）

音频频谱会通过频谱纹理输入直接驱动 GLSL 分形着色器。低频会使内部分形线条更加粗壮，中频则会改变其旋转方式，而高频则能让外部边缘更显明亮。**在使用这些方案中的任何参数名称之前，请务必先执行探索步骤（SKILL.md 第 0 步）——不同版本的 Hermes Agent 中这些参数名称可能会有所差异。**

```
Audio File In CHOP → Audio Spectrum CHOP (FFT=512, outlength=256)
    → Math CHOP (gain=10)
    → CHOP To TOP (spectrum texture, 256x2, dataformat=r)
                                          ↓ (input 1)
Constant TOP (rgba32float, time) → GLSL TOP (audio-reactive shader) → Null TOP
        (input 0)                    ↑
                              Text DAT (shader code)
```

**通过 td_execute_python 进行构建（完整可运行的脚本）：**

```python
# td_execute_python script:
td_execute_python(code="""
import os
root = op('/project1')

# Audio input
audio = root.create(audiofileinCHOP, 'audio_in')
audio.par.file = '/path/to/music.mp3'
audio.par.playmode = 0  # Locked to timeline

# FFT analysis (output length manually set to 256 bins)
spectrum = root.create(audiospectrumCHOP, 'spectrum')
audio.outputConnectors[0].connect(spectrum.inputConnectors[0])
spectrum.par.fftsize = '512'
spectrum.par.outputmenu = 'setmanually'
spectrum.par.outlength = 256

# THEN boost gain on the raw spectrum (NO Lag CHOP — see pitfall #34)
math = root.create(mathCHOP, 'math_norm')
spectrum.outputConnectors[0].connect(math.inputConnectors[0])
math.par.gain = 10

# Spectrum → texture (256x2 image — stereo, sample at y=0.25 for first channel)
# NOTE: choptoTOP has NO input connectors — use par.chop reference!
spec_tex = root.create(choptoTOP, 'spectrum_tex')
spec_tex.par.chop = math
spec_tex.par.dataformat = 'r'
spec_tex.par.layout = 'rowscropped'

# Time driver (rgba32float to avoid 0-1 clamping!)
time_drv = root.create(constantTOP, 'time_driver')
time_drv.par.format = 'rgba32float'
time_drv.par.outputresolution = 'custom'
time_drv.par.resolutionw = 1
time_drv.par.resolutionh = 1
time_drv.par.colorr.expr = "absTime.seconds % 1000.0"
time_drv.par.colorg.expr = "int(absTime.seconds / 1000.0)"

# GLSL shader
glsl = root.create(glslTOP, 'audio_shader')
glsl.par.outputresolution = 'custom'
glsl.par.resolutionw = 1280; glsl.par.resolutionh = 720

shader_dat = root.create(textDAT, 'shader_code')
shader_dat.text = open('/tmp/shader.glsl').read()
glsl.par.pixeldat = shader_dat

# Wire: input 0=time, input 1=spectrum
time_drv.outputConnectors[0].connect(glsl.inputConnectors[0])
spec_tex.outputConnectors[0].connect(glsl.inputConnectors[1])

# Output + audio playback
out = root.create(nullTOP, 'output')
glsl.outputConnectors[0].connect(out.inputConnectors[0])
audio_out = root.create(audiodeviceoutCHOP, 'audio_out')
audio.outputConnectors[0].connect(audio_out.inputConnectors[0])

result = 'network built'
""")
```

**GLSL着色器（从输入纹理1中读取光谱数据）：**

```glsl
out vec4 fragColor;

vec3 palette(float t) {
    vec3 a = vec3(0.5); vec3 b = vec3(0.5);
    vec3 c = vec3(1.0); vec3 d = vec3(0.263, 0.416, 0.557);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    vec4 td = texture(sTD2DInputs[0], vec2(0.5));
    float t = td.r + td.g * 1000.0;

    vec2 res = uTDOutputInfo.res.zw;
    vec2 uv = (gl_FragCoord.xy * 2.0 - res) / min(res.x, res.y);
    vec2 uv0 = uv;
    vec3 finalColor = vec3(0.0);

    float bass = texture(sTD2DInputs[1], vec2(0.05, 0.25)).r;
    float mids = texture(sTD2DInputs[1], vec2(0.25, 0.25)).r;
    float highs = texture(sTD2DInputs[1], vec2(0.65, 0.25)).r;

    float ca = cos(t * (0.15 + mids * 0.3));
    float sa = sin(t * (0.15 + mids * 0.3));
    uv = mat2(ca, -sa, sa, ca) * uv;

    for (float i = 0.0; i < 4.0; i++) {
        uv = fract(uv * (1.4 + bass * 0.3)) - 0.5;
        float d = length(uv) * exp(-length(uv0));
        float freq = texture(sTD2DInputs[1], vec2(clamp(d*0.5, 0.0, 1.0), 0.25)).r;
        vec3 col = palette(length(uv0) + i * 0.4 + t * 0.35);
        d = sin(d * (7.0 + bass * 4.0) + t * 1.5) / 8.0;
        d = abs(d);
        d = pow(0.012 / d, 1.2 + freq * 0.8 + bass * 0.5);
        finalColor += col * d;
    }

    float glow = (0.03 + bass * 0.05) / (length(uv0) + 0.03);
    finalColor += vec3(0.4, 0.1, 0.7) * glow * (0.6 + 0.4 * sin(t * 2.5));

    float ring = abs(length(uv0) - 0.4 - mids * 0.3);
    finalColor += vec3(0.1, 0.6, 0.8) * (0.005 / ring) * (0.2 + highs * 0.5);

    finalColor *= smoothstep(0.0, 1.0, 1.0 - dot(uv0*0.55, uv0*0.55));
    finalColor = finalColor / (finalColor + vec3(1.0));

    fragColor = TDOutputSwizzle(vec4(finalColor, 1.0));
}
```

**频谱采样如何驱动视觉效果：**
- `texture(sTD2DInputs[1], vec2(x, 0.0)).r` — x坐标表示频率（0=低音，1=高音）
- 内层分形迭代采样较低的x值——从而对低音做出响应
- 外层迭代采样较高的x值——从而对高音做出响应
- 对`fract()`结果应用`bass * 0.3`的缩放系数——使分形缩放效果随低音强度波动
- 对正弦频率应用`bass * 4.0`的系数——使线条密度随低音强度波动
- 对旋转速度应用`mids * 0.3`的系数——在人声或中频段落时让螺旋结构旋转得更快
- 对环状元素的透明度应用`highs * 0.5`的系数——在外环处产生高频闪烁效果

**输出录制方式：** 使用带有`mjpa`编码器的MovieFileOut TOP功能（H.264编码需要商业许可证）。请参阅相关注意事项#25-27。

## GLSL着色器

### 模式10：自定义片段着色器

可通过编写GLSL片段着色器来实现自定义视觉效果。

```
Text DAT (shader code) -> GLSL TOP -> Level TOP -> Null TOP (out)
                           + optional input TOPs for texture sampling
```

**TouchDesigner 中可用的常见 GLSL 统一变量：**

```glsl
// Automatically provided by TD
uniform vec4 uTDOutputInfo;  // .res.zw = resolution

// NOTE: uTDCurrentTime does NOT exist in TD 099!
// Feed time via a 1x1 Constant TOP (format=rgba32float):
//   t.par.colorr.expr = "absTime.seconds % 1000.0"
//   t.par.colorg.expr = "int(absTime.seconds / 1000.0)"
// Then read in GLSL:
//   vec4 td = texture(sTD2DInputs[0], vec2(0.5));
//   float t = td.r + td.g * 1000.0;

// Input textures (from connected TOP inputs)
uniform sampler2D sTD2DInputs[1];  // array of input samplers

// From vertex shader
in vec3 vUV;  // UV coordinates (0-1 range)
```

**示例：Plasma着色器（利用输入纹理中的时间值）**

```glsl
layout(location = 0) out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    // Read time from Constant TOP input 0 (rgba32float format)
    vec4 td = texture(sTD2DInputs[0], vec2(0.5));
    float t = td.r + td.g * 1000.0;

    float v1 = sin(uv.x * 10.0 + t);
    float v2 = sin(uv.y * 10.0 + t * 0.7);
    float v3 = sin((uv.x + uv.y) * 10.0 + t * 1.3);
    float v4 = sin(length(uv - 0.5) * 20.0 - t * 2.0);

    float v = (v1 + v2 + v3 + v4) * 0.25;

    vec3 color = vec3(
        sin(v * 3.14159 + 0.0) * 0.5 + 0.5,
        sin(v * 3.14159 + 2.094) * 0.5 + 0.5,
        sin(v * 3.14159 + 4.189) * 0.5 + 0.5
    );

    fragColor = vec4(color, 1.0);
}
```

### 模式 11：多遍 GLSL（乒乓式处理）

对于需要在多帧之间保持状态的效果（如粒子效果、流体效果、元胞自动机效果），可使用支持多遍处理的 GLSL Multi TOP，或采用反馈 TOP 循环来实现。

```
GLSL Multi TOP (pass 0: simulation, pass 1: rendering)
   + Text DAT (simulation shader)
   + Text DAT (render shader)
   -> Level TOP -> Null TOP (out)
      ^
      |__ Feedback TOP (feeds simulation state back)
```

## 交互式安装方式

### 模式 12：鼠标/触摸操作 -> 视觉反馈

```
Mouse In CHOP -> Math CHOP (normalize to 0-1) -> [export to visual params]

# Or for touch/multi-touch:
Multi Touch In DAT -> Script CHOP (parse touches) -> [export to visual params]
```

```python
# Normalize mouse position to 0-1 range
td_execute_python: """
op('/project1/noise1').par.offsetx.expr = "op('/project1/mouse_norm')['tx']"
op('/project1/noise1').par.offsety.expr = "op('/project1/mouse_norm')['ty']"
"""
```

### 模式 13：OSC 控制（通过外部软件实现）

```
OSC In CHOP (port 7000) -> Select CHOP (pick channels) -> [export to visual params]
```

```
1. td_create_operator(parent="/project1", type="oscinChop", name="osc_in")
2. td_set_operator_pars(path="/project1/osc_in", properties={"port": 7000})

# OSC messages like /frequency 440 will appear as channel "frequency" with value 440
# Export to any parameter:
3. td_execute_python: "op('/project1/noise1').par.period.expr = \"op('/project1/osc_in')['frequency']\""
```

### 模式 14：MIDI 控制（DJ/VJ）

```
MIDI In CHOP (device) -> Select CHOP -> [export channels to visual params]
```

常见的 MIDI 映射方式：
- CC 通道（旋钮/推子）：连续值范围为 0-127，可映射为浮点型参数
- 音符开启/关闭：二进制触发信号，可映射为用于控制包络的 Trigger CHOP 参数
- 拨弦力度：用于控制强度/亮度

## 现场演出

### 模式 15：多源视频混音设置

```
Source A (generative) ----+
Source B (video) ---------+-- Switch/Cross TOP -- Level TOP -- Window COMP (output)
Source C (camera) --------+
                           ^
                    MIDI/OSC control selects active source and crossfade
```

```python
# MIDI CC1 controls which source is active (0-127 -> 0-2)
td_execute_python: """
op('/project1/switch1').par.index.expr = "int(op('/project1/midi_in')['cc1'] / 42)"
"""

# MIDI CC2 controls crossfade between current and next
td_execute_python: """
op('/project1/cross1').par.cross.expr = "op('/project1/midi_in')['cc2'] / 127.0"
"""
```

### 模式 16：投影映射

```
Content TOPs ----+
                 |
Stoner TOP (UV mapping) -> Composite TOP -> Window COMP (projector output)
   or
Kantan Mapper COMP (external .tox)
```

在投影映射应用中，关键步骤如下：
1. 将视觉内容制作成标准的TOP格式；
2. 使用Stoner TOP或第三方映射工具，将内容进行UV映射到实际表面；
3. 通过Window COMP将输出数据传输至投影仪。

### 模式17：提示系统

```
Table DAT (cue list: cue_number, scene_name, duration, transition_type)
    |
Script CHOP (cue state: current_cue, progress, next_cue_trigger)
    |
[export to Switch/Cross TOPs to transition between scenes]
```

```python
td_execute_python: """
# Simple cue system
cue_table = op('/project1/cue_list')
cue_state = op('/project1/cue_state')

def advance_cue():
    current = int(cue_state.par.value0.val)
    next_cue = min(current + 1, cue_table.numRows - 1)
    cue_state.par.value0.val = next_cue
    
    scene = cue_table[next_cue, 'scene']
    duration = float(cue_table[next_cue, 'duration'])
    
    # Set crossfade target and duration
    op('/project1/cross1').par.cross.val = 0
    # Animate cross to 1.0 over duration seconds
    # (use a Timer CHOP or LFO CHOP for smooth animation)
"""
```

## 网络通信

### 模式 18：OSC 服务器/客户端

```
# Sending OSC
OSC Out CHOP -> (network) -> external application

# Receiving OSC  
(network) -> OSC In CHOP -> Select CHOP -> [use values]
```

### 模式 19：NDI 视频流传输

```
# Send video over network
[any TOP chain] -> NDI Out TOP (source name)

# Receive video from network
NDI In TOP (select source) -> [process as normal TOP]
```

### 模式 20：WebSocket通信

```
WebSocket DAT -> Script DAT (parse JSON messages) -> [update visuals]
```

```python
td_execute_python: """
ws = op('/project1/websocket1')
ws.par.address = 'ws://localhost:8080'
ws.par.active = True

# In a DAT Execute callback (Script DAT watching WebSocket DAT):
# def onTableChange(dat):
#     import json
#     msg = json.loads(dat.text)
#     op('/project1/noise1').par.seed.val = msg.get('seed', 0)
"""
```
