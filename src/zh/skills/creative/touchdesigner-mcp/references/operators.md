# TouchDesigner 操作符参考手册

## 操作符家族概览

TouchDesigner 共包含 6 种操作符家族。每种家族负责处理特定类型的数据，并在界面中以不同颜色标识。操作符之间只能连接同一家族的成员，如需跨家族连接，则需借助转换器作为桥梁。

## TOPs — 纹理操作符（紫色）

在 GPU 上对 2D 图像/纹理进行处理，是实现视觉输出的核心工具。

### 生成器（从无到有创建图像）

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Noise TOP | `noiseTop` | `type`（0-6）、`monochrome`、`seed`、`period`、`harmonics`、`exponent`、`amp`、`offset`、`resolutionw/h` | 生成程序化噪声纹理——如 Perlin、Simplex、Sparse 等，是生成艺术的基础。 |
| Constant TOP | `constantTop` | `colorr/g/b/a`、`resolutionw/h` | 固定颜色，可用作背景或混合输入。 |
| Text TOP | `textTop` | `text`、`fontsizex`、`fontfile`、`alignx/y`、`colorr/g/b` | 将文本渲染为纹理，支持多行显示和自动换行。 |
| Ramp TOP | `rampTop` | `type`（0=水平，1=垂直，2=辐射状，3=圆形）、`phase`、`period` | 生成用于遮罩、颜色映射的渐变纹理。 |
| Circle TOP | `circleTop` | `radiusx/y`、`centerx/y`、`width` | 生成圆形、环形、椭圆形。 |
| Rectangle TOP | `rectangleTop` | `sizex/y`、`centerx/y`、`softness` | 生成矩形，可选是否添加柔和过渡效果。 |
| GLSL TOP | `glslTop` | `dat`（指向着色器 DAT 文件）、`resolutionw/h`、`outputformat`、自定义统一变量 | 自定义片段着色器，是最强大的自定义视觉效果工具。 |
| GLSL Multi TOP | `glslmultiTop` | `dat`、`numinputs`、`numoutputs`、`numcomputepasses` | 基于计算着色器的多遍 GLSL 处理，功能较为高级。 |
| Render TOP | `renderTop` | `camera`、`geometry`、`lights`、`resolutionw/h` | 渲染 3D 场景（包括 SOP、MAT 以及相机/灯光节点）。 |

### 滤镜（修改单个输入）

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Level TOP | `levelTop` | `opacity`、`brightness1/2`、`gamma1/2`、`contrast`、`invert`、`blacklevel/whitelevel` | 调整亮度、对比度、伽马值及灰度级别，是色彩校正的核心工具。 |
| Blur TOP | `blurTop` | `sizex/y`、`type`（0=高斯模糊，1=盒形模糊，2=Bartlett 模糊） | 实现高斯模糊或盒形模糊效果。 |
| Transform TOP | `transformTop` | `tx/ty`、`sx/sy`、`rz`、`pivotx/y`、`extend`（0=保持原位，1=归零，2=重复，3=镜像） | 对纹理进行平移、缩放和旋转操作。 |
| HSV Adjust TOP | `hsvadjustTop` | `hueoffset`、`saturationmult`、`valuemult` | 调整 HSV 颜色参数。 |
| Lookup TOP | `lookupTop` | （输入：纹理 + 查表） | 通过查表纹理实现颜色重映射。 |
| Edge TOP | `edgeTop` | `type`（0=Sobel 滤波，1=Frei-Chen 滤波） | 进行边缘检测。 |
| Displace TOP | `displaceTop` | `scalex/y` | 使用第二个输入作为位移贴图来实现像素位移。 |
| Flip TOP | `flipTop` | `flipx`、`flipy`、`flop`（对角线翻转） | 对纹理进行镜像或翻转操作。 |
| Crop TOP | `cropTop` | `cropleft/right/top/bottom` | 裁剪纹理的特定区域。 |
| Resolution TOP | `resolutionTop` | `resolutionw/h`、`outputresolution` | 调整纹理的分辨率大小。 |
| Null TOP | `nullTop` | （无重要参数） | 透明传递节点，用于结构组织、引用或实现反馈延迟。 |
| Cache TOP | `cacheTop` | `length`、`step` | 存储 N 帧的历史数据，常用于轨迹效果或时间相关特效。 |

### 组合器（合并多个输入）

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Composite TOP | `compositeTop` | `operand`（0-31：叠加、相加、相乘、屏幕混合等） | 使用标准混合模式将两个纹理进行合成。 |
| Over TOP | `overTop` | （简单的阿尔法混合） | 带有阿尔法通道的图层叠加，比 Composite 更简单。 |
| Add TOP | `addTop` | （加法混合） | 实现加法混合效果，非常适合制作光晕或灯光特效。 |
| Multiply TOP | `multiplyTop` | （乘法混合） | 实现乘法混合效果，常用于遮罩或变暗处理。 |
| Switch TOP | `switchTop` | `index`（基于索引的编号） | 根据索引在多个输入之间切换。 |
| Cross TOP | `crossTop` | `cross`（0.0-1.0 的过渡值） | 在两个输入之间实现交叉淡入淡出效果。 |

### 输入/输出

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Movie File In TOP | `moviefileinTop` | `file`、`speed`、`trim`、`index` | 加载视频文件或图像序列。 |
| Movie File Out TOP | `moviefileoutTop` | `file`、`type`（编码格式）、`record`（切换录制状态） | 录制或导出视频文件。 |
| NDI In TOP | `ndiinTop` | `sourcename` | 接收 NDI 视频流。 |
| NDI Out TOP | `ndioutTop` | `sourcename` | 发送 NDI 视频流。 |
| Syphon Spout In/Out TOP | `syphonspoutinTop` / `syphonspoutoutTop` | `servername` | 实现不同应用程序之间的纹理共享。 |
| Video Device In TOP | `videodeviceinTop` | `device` | 连接网络摄像头或采集卡作为输入源。 |
| Feedback TOP | `feedbackTop` | `top`（需要反馈的目标操作符路径） | 实现单帧延迟反馈，是递归效果的核心组件。 |

### 转换器

| 操作符 | 类型名称 | 数据流向 | 用途 |
|--------|----------|----------|------|
| CHOP to TOP | `choptopTop` | CHOP -> TOP | 将通道数据可视化為纹理，如波形图或频谱图。 |
| TOP to CHOP | `topchopChop` | TOP -> CHOP | 采样纹理像素作为通道数据使用。 |

## CHOPs — 通道操作符（绿色）

用于处理随时间变化的数值数据：音频、动画曲线、传感器数据、控制信号等。

### 生成器

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Constant CHOP | `constantChop` | `name0/value0`、`name1/value1`... | 创建静态的命名通道，可搭配控制面板调整参数。 |
| LFO CHOP | `lfoChop` | `frequency`（频率）、`type`（0=正弦波，1=三角波，2=方波，3=渐变波，4=脉冲波）、`amp`、`offset`、`phase` | 低频振荡器，可作为动画驱动源。 |
| Noise CHOP | `noiseChop` | `type`、`roughness`、`period`、`amp`、`seed`、`channels` | 生成平滑的随机运动，适合创建自然风格的动画效果。 |
| Pattern CHOP | `patternChop` | `type`（0=正弦波，1=三角波，...）、`length`（周期长度）、`cycles`（循环次数） | 生成各种波形模式。 |
| Timer CHOP | `timerChop` | `length`（时长）、`play`（播放状态）、`cue`（触发点）、`cycles`（循环次数） | 实现带触发点的倒计时或计时功能。 |
| Count CHOP | `countChop` | `threshold`（阈值）、`limittype`（限制类型）、`limitmin/max`（最小/最大限制值） | 用于计数，并支持数值环绕或限制在特定范围内。 |

### 音频相关

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Audio File In CHOP | `audiofileinChop` | `file`、`volume`（音量）、`play`（播放状态）、`speed`（速度）、`trim`（裁剪） | 播放音频文件。 |
| Audio Device In CHOP | `audiodeviceinChop` | `device`（设备）、`channels`（通道数） | 连接实时麦克风或线路输入设备。 |
| Audio Spectrum CHOP | `audiospectrumChop` | `size`（FFT 分辨率）、`outputformat`（0=功率谱，1=幅值谱） | 通过 FFT 进行频率分析。 |
| Audio Band EQ CHOP | `audiobandeqChop` | `bands`（频段数量）、`gaindb`（每频段的增益值） | 对特定频段进行隔离或调整。 |
| Audio Device Out CHOP | `audiodeviceoutChop` | `device` | 作为音频输出节点。 |

### 数学/逻辑运算

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Math CHOP | `mathChop` | `preoff`、`gain`、`postoff`、`chanop`（0=关闭，1=相加，2=相减，3=相乘...） | 对通道数据进行数学运算，功能极为强大。 |
| Logic CHOP | `logicChop` | `preop`（0=关闭，1=与运算，2=或运算，3=异或运算，4=与非运算）、`convert` | 对通道数据执行布尔逻辑运算。 |
| Filter CHOP | `filterChop` | `type`（0=低通滤波，1=带通滤波，2=高通滤波，3=陷波滤波）、`cutofffreq`（截止频率）、`filterwidth`（滤波器宽度） | 用于平滑信号、衰减信号或过滤特定频率成分。 |
| Lag CHOP | `lagChop` | `lag1/2`（延迟时间1/2）、`overshoot1/2`（超调量1/2） | 实现带有超调效果的平滑过渡。 |
| Limit CHOP | `limitChop` | `type`（0=限制在范围，1=循环，2=锯齿波形）、`min/max`（最小/最大值限制） | 对通道数值进行限制或循环处理。 |
| Speed CHOP | `speedChop` | （无重要参数） | 对数值进行积分运算，例如将速度转换为位置，或将加速度转换为速度。 |
| Trigger CHOP | `triggerChop` | `attack`、`peak`、`decay`、`sustain`、`release` | 基于触发事件生成 ADSR 曲线。 |
| Select CHOP | `selectChop` | `chop`（目标操作符路径）、`channames`（通道名称列表） | 从另一个 CHOP 中引用指定通道。 |
| Merge CHOP | `mergeChop` | `align`（0=扩展，1=裁剪至最短长度，2=裁剪至第一个匹配长度） | 合并多个 CHOP 产生的通道数据。 |
| Null CHOP | `nullChop` | （无重要参数） | 透明传递节点，用于结构组织和引用。 |

### 输入设备相关

| 操作符 | 类型名称 | 用途 |
|--------|----------|------|
| Mouse In CHOP | `mouseinChop` | 获取鼠标位置、按钮状态及滚轮信息。 |
| Keyboard In CHOP | `keyboardinChop` | 获取键盘按键状态。 |
| MIDI In CHOP | `midiinChop` | 接收 MIDI 音符或控制信号。 |
| OSC In CHOP | `oscinChop` | 接收 OSC 消息（支持网络传输）。 |

## SOPs — 曲面操作符（蓝色）

用于处理 3D 几何数据：点、多边形、NURBS 曲面、网格等。

### 生成器

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Grid SOP | `gridSop` | `rows`（行数）、`cols`（列数）、`sizex/y`（尺寸）、`type`（0=多边形网格，1=普通网格，2=NURBS 曲面） | 生成平面网格，是实现位移效果或实例化的基础。 |
| Sphere SOP | `sphereSop` | `type`、`rows`、`cols`、`radius`（半径） | 生成球形几何体。 |
| Box SOP | `boxSop` | `sizex/y/z`（尺寸） | 生成立方体几何体。 |
| Torus SOP | `torusSop` | `radiusx/y`（X/Y 方向半径）、`rows`、`cols` | 生成环形面结构。 |
| Circle SOP | `circleSop` | `type`、`radius`（半径）、`divs`（细分程度） | 生成圆形或环形几何体。 |
| Line SOP | `lineSop` | `dist`（距离）、`points`（点坐标列表） | 生成线段。 |
| Text SOP | `textSop` | `text`、`fontsizex`、`fontfile`（字体文件）、`extrude`（挤出高度） | 生成 3D 文本几何体。 |

### 修改器

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Transform SOP | `transformSop` | `tx/ty/tz`（平移坐标）、`rx/ry/rz`（旋转坐标）、`sx/sy/sz`（缩放坐标） | 对几何体进行平移、旋转和缩放操作。 |
| Noise SOP | `noiseSop` | `type`、`amp`、`period`、`roughness` | 利用噪声来变形几何体。 |
| Sort SOP | `sortSop` | `ptsort`（点排序）、`primsort`（图元排序） | 对点或图元进行重新排序。 |
| Facet SOP | `facetSop` | `unique`（去重）、`consolidate`（合并相邻顶点）、`computenormals`（计算法线） | 用于生成法线、合并相邻顶点以及确保顶点唯一。 |
| Merge SOP | `mergeSop` | （无重要参数） | 合并多个几何体输入源的数据。 |
| Null SOP | `nullSop` | （无重要参数） | 透明传递节点，用于结构组织。 |

## DATs — 数据操作符（白色）

用于处理文本、表格、脚本以及网络数据等。

### 核心功能

| 操作符 | 类型名称 | 关键参数 | 用途 |
|--------|----------|-----------|------|
| Table DAT | `tableDat` | （可直接编辑内容） | 类似电子表格的数据表结构。 |
| Text DAT | `textDat` | （可直接编辑内容） | 存储任意文本内容，常用于存放着色器代码、配置文件或脚本。 |
| Script DAT | `scriptDat` | `language`（0=Python，1=C++） | 支持自定义回调函数及 DAT 文件处理逻辑。 |
| CHOP Execute DAT | `chopexecDat` | `chop`（需要监控的 CHOP 路径）、回调函数 | 当 CHOP 的数值发生变化时触发 Python 代码执行。 |
| DAT Execute DAT | `datexecDat` | `dat`（需要监控的 DAT 文件路径） | 当 DAT 文件内容发生变化时触发 Python 代码执行。 |
| Panel Execute DAT | `panelexecDat` | `panel`（UI 面板名称） | 当 UI 面板发生相应事件时触发 Python 代码执行。 |

### 输入/输出功能 || 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Web DAT | `webDat` | `url`、`fetchmethod`（0=GET，1=POST） | 发送HTTP请求，实现API集成。 |
| TCP/IP DAT | `tcpipDat` | `address`、`port`、`mode` | 支持TCP网络通信。 |
| OSC输入DAT | `oscinDat` | `port` | 以文本消息形式接收OSC数据。 |
| 串行DAT | `serialDat` | `port`、`baudrate` | 用于串行端口通信（如Arduino等设备）。 |
| 文件输入DAT | `fileinDat` | `file` | 读取文本文件内容。 |
| 文件输出DAT | `fileoutDat` | `file`、`write` | 写入文本文件内容。 |

### 转换操作

| 操作符 | 类型名称 | 转换方向 | 用途 |
|----------|-----------|-----------|-----|
| DAT转CHOP | `dattochopChop` | DAT -> CHOP | 将表格数据转换为通道数据。 |
| CHOP转DAT | `choptodatDat` | CHOP -> DAT | 将通道数据转换为表格行数据。 |
| SOP转DAT | `soptodatDat` | SOP -> DAT | 以表格形式提取几何数据。 |

## MATs — 材质操作符（黄色）

用于在Render TOP / Geometry COMP中实现3D渲染的材质操作符。

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Phong材质 | `phongMat` | `diff_colorr/g/b`、`spec_colorr/g/b`、`shininess`、`colormap`、`normalmap` | 传统Phong着色模型，实现简单且速度较快。 |
| PBR材质 | `pbrMat` | `basecolorr/g/b`、`metallic`、`roughness`、`normalmap`、`emitcolorr/g/b` | 基于物理的渲染方式，可生成逼真材质效果。 |
| GLSL材质 | `glslMat` | `dat`（着色器DAT）、自定义uniform变量 | 支持自定义3D顶点着色器与片段着色器。 |
| 常量材质 | `constMat` | `colorr/g/b`、`colormap` | 仅提供固定颜色/纹理，无任何着色效果。 |
| 点精灵材质 | `pointspriteMat` | `colormap`、`scale` | 将点对象渲染为面向相机的精灵图像，非常适合用于粒子效果。 |
| 线框材质 | `wireframeMat` | `colorr/g/b`、`width` | 用于实现线框渲染效果。 |
| 深度材质 | `depthMat` | `near`、`far` | 将深度缓冲区渲染为灰度图像。 |

## COMPs — 组件操作符（灰色）

用于构建容器、3D场景元素及UI组件的操作符。

### 3D场景相关

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| 几何体组件 | `geometryComp` | `material`（路径）、`instancechop`（路径）、`instancing`（开关） | 为几何体应用材质并支持实例化渲染。 |
| 相机组件 | `cameraComp` | `tx/ty/tz`、`rx/ry/rz`、`fov`、`near/far` | 用于Render TOP中的相机控制。 |
| 光源组件 | `lightComp` | `lighttype`（0=点光源，1=定向光，2=聚光灯，3=锥形光）、`dimmer`、`colorr/g/b` | 为3D场景提供照明效果。 |
| 环境光组件 | `ambientlightComp` | `dimmer`、`colorr/g/b` | 提供环境照明效果。 |
| 环境贴图光源组件 | `envlightComp` | `envmap` | 基于图像的环境光照技术（IBL）。 |

### 容器相关

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| 容器组件 | `containerComp` | `w`、`h`、`bgcolor1/2/3` | 用于构建UI容器，可容纳其他组件以实现面板布局。 |
| 基础容器组件 | `baseComp` | （无重要参数） | 通用型容器，可用于多层嵌套结构。 |
| 复制器组件 | `replicatorComp` | `template`、`operatorsdat` | 根据表格数据将模板操作符复制N次。 |

### 工具类组件

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| 窗口组件 | `windowComp` | `winw/h`、`winoffsetx/y`、`monitor`、`borders` | 用于输出显示或投影用的窗口。 |
| 选择组件 | `selectComp` | `rowcol`、`panel` | 用于从其他位置选择并显示内容。 |
| 引擎组件 | `engineComp` | `tox`、`externaltox` | 用于加载外部.tox格式的组件，实现子进程隔离。 |

## 跨系列转换器汇总

| 输入类型 | 输出类型 | 操作符 | 类型名称 |
|----------|----------|----------|-----------|
| CHOP | TOP | CHOP转TOP | `choptopTop` |
| TOP | CHOP | TOP转CHOP | `topchopChop` |
| DAT | CHOP | DAT转CHOP | `dattochopChop` |
| CHOP | DAT | CHOP转DAT | `choptodatDat` |
| SOP | CHOP | SOP转CHOP | `soptochopChop` |
| CHOP | SOP | CHOP转SOP | `choptosopSop` |
| SOP | DAT | SOP转DAT | `soptodatDat` |
| DAT | SOP | DAT转SOP | `dattosopSop` |
| SOP | TOP | （需结合Render TOP与Geometry COMP使用） | — |
| TOP | SOP | TOP转SOP | `toptosopSop` |
