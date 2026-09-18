# TouchDesigner 操作符参考手册

## 操作符家族概览

TouchDesigner 共包含 6 种操作符家族。每种家族负责处理特定类型的数据，并在用户界面中以不同颜色标识。操作符仅能与其他相同家族的操作符相连（可通过跨家族转换器作为桥梁）。

## TOPs — 纹理操作符（紫色）

在 GPU 上对 2D 图像/纹理进行处理，是实现视觉输出的核心工具。

### 生成器（从无到有创建图像）

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Noise TOP | `noiseTop` | `type`（0-6）、`monochrome`、`seed`、`period`、`harmonics`、`exponent`、`amp`、`offset`、`resolutionw/h` | 用于生成程序化噪声纹理——如Perlin、Simplex、Sparse等，是生成艺术的基础。 |
| Constant TOP | `constantTop` | `colorr/g/b/a`、`resolutionw/h` | 生成纯色纹理，可用作背景或混合输入。 |
| Text TOP | `textTop` | `text`、`fontsizex`、`fontfile`、`alignx/y`、`colorr/g/b` | 将文本渲染为纹理，支持多行显示及自动换行功能。 |
| Ramp TOP | `rampTop` | `type`（0=水平，1=垂直，2=径向，3=圆形）、`phase`、`period` | 用于生成渐变纹理，可实现遮罩效果或颜色映射。 |
| Circle TOP | `circleTop` | `radiusx/y`、`centerx/y`、`width` | 生成圆形、环状或椭圆形纹理。 |
| Rectangle TOP | `rectangleTop` | `sizex/y`、`centerx/y`、`softness` | 生成矩形，可选参数可控制边缘柔和度。 |
| GLSL TOP | `glslTop` | `dat`（指向着色器DAT文件）、`resolutionw/h`、`outputformat`、自定义uniforms | 支持自定义片段着色器，是实现定制化视觉效果最强大的操作符。 |
| GLSL Multi TOP | `glslmultiTop` | `dat`、`numinputs`、`numoutputs`、`numcomputepasses` | 基于计算着色器的多遍GLSL编程，功能较为高级。 |
| Render TOP | `renderTop` | `camera`、`geometry`、`lights`、`resolutionw/h` | 用于渲染3D场景（包括SOP节点、MAT节点以及相机/光源COMPs）。 |

### 过滤器（用于修改单个输入值）

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Level TOP | `levelTop` | `opacity`, `brightness1/2`, `gamma1/2`, `contrast`, `invert`, `blacklevel/whitelevel` | 调整亮度、对比度、伽马值及灰度等级，实现基础的颜色校正功能。 |
| Blur TOP | `blurTop` | `sizex/y`, `type` (0=高斯模糊，1=盒形模糊，2=Bartlett模糊) | 支持高斯模糊与盒形模糊效果。 |
| Transform TOP | `transformTop` | `tx/ty`, `sx/sy`, `rz`, `pivotx/y`, `extend` (0=保持原位，1=归零，2=重复，3=镜像) | 可对纹理进行平移、缩放及旋转操作。 |
| HSV Adjust TOP | `hsvadjustTop` | `hueoffset`, `saturationmult`, `valuemult` | 对HSV颜色空间参数进行调节。 |
| Lookup TOP | `lookupTop` | (输入：纹理 + 查找表) | 通过查找表纹理实现颜色重映射。 |
| Edge TOP | `edgeTop` | `type` (0=索贝尔边缘检测，1=Frei-Chen边缘检测) | 用于执行边缘检测功能。 |
| Displace TOP | `displaceTop` | `scalex/y` | 利用第二个输入作为位移图来实现像素位移效果。 |
| Flip TOP | `flipTop` | `flipx`, `flipy`, `flop` (对角线翻转) | 可对纹理进行镜像或翻转操作。 |
| Crop TOP | `cropTop` | `cropleft/right/top/bottom` | 用于裁剪纹理的特定区域。 |
| Resolution TOP | `resolutionTop` | `resolutionw/h`, `outputresolution` | 调整纹理的分辨率大小。 |
| Null TOP | `nullTop` | (无重要参数) | 具有透传功能，可用于结构组织、引用处理及延迟反馈。 |
| Cache TOP | `cacheTop` | `length`, `step` | 用于存储N帧的历史数据，非常适合实现轨迹效果或时间相关特效。 |

### 合成器（用于合并多个输入）

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Composite TOP | `compositeTop` | `operand`（0-31：叠加、相加、相乘、遮罩等） | 使用标准合成模式将两种纹理混合在一起。 |
| Over TOP | `overTop` | （简单阿尔法通道合成） | 基于阿尔法通道进行图层叠加，比Composite操作更简单。 |
| Add TOP | `addTop` | （加法混合） | 采用加法混合模式，非常适合制作光晕及光线效果。 |
| Multiply TOP | `multiplyTop` | （乘法混合） | 使用乘法混合模式，适用于遮罩处理及变暗效果。 |
| Switch TOP | `switchTop` | `index`（基于0的索引） | 根据索引在多个输入源之间切换。 |
| Cross TOP | `crossTop` | `cross`（0.0-1.0） | 在两个输入源之间实现渐变过渡。 |

### 输入/输出

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Movie File In TOP | `moviefileinTop` | `file`、`speed`、`trim`、`index` | 加载视频文件及图像序列。 |
| Movie File Out TOP | `moviefileoutTop` | `file`、`type`（编码格式）、`record`（开关） | 录制/导出视频文件。 |
| NDI In TOP | `ndiinTop` | `sourcename` | 接收NDI视频流。 |
| NDI Out TOP | `ndioutTop` | `sourcename` | 发送NDI视频流。 |
| Syphon Spout In/Out TOP | `syphonspoutinTop` / `syphonspoutoutTop` | `servername` | 实现应用间的纹理共享。 |
| Video Device In TOP | `videodeviceinTop` | `device` | 通过网络摄像头或捕获卡获取输入信号。 |
| Feedback TOP | `feedbackTop` | `top`（需要反馈的TOP路径） | 实现单帧延迟反馈，对于递归效果至关重要。 |
### 转换器

| 操作符 | 类型名称 | 数据流向 | 用途 |
|----------|-----------|-----------|-----|
| CHOP 转 TOP | `choptopTop` | CHOP -> TOP | 将通道数据以纹理形式可视化（波形、频谱显示）。 |
| TOP 转 CHOP | `topchopChop` | TOP -> CHOP | 将纹理像素采样为通道数据。 |

## CHOPs — 通道操作符（绿色）

时变数值数据：音频、动画曲线、传感器数据、控制信号。

### 生成器

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| 常量 CHOP | `constantChop` | `name0/value0`, `name1/value1`... | 静态命名通道。提供参数控制面板。 |
| LFO CHOP | `lfoChop` | `frequency`（频率）、`type`（类型，0=正弦波，1=三角波，2=方波，3=渐变波，4=脉冲波）、`amp`（振幅）、`offset`（偏移量）、`phase`（相位） | 低频振荡器。用于驱动动画。 |
| 噪声 CHOP | `noiseChop` | `type`（类型）、`roughness`（粗糙度）、`period`（周期）、`amp`（振幅）、`seed`（种子值）、`channels`（通道数） | 产生平滑的随机运动。适用于自然风格的动画。 |
| 模式 CHOP | `patternChop` | `type`（类型，0=正弦波，1=三角波，...）、`length`（长度）、`cycles`（循环次数） | 生成波形模式。 |
| 计时器 CHOP | `timerChop` | `length`（时长）、`play`（播放）、`cue`（提示点）、`cycles`（循环次数） | 具有提示点的倒计时/倒数计时器。 |
| 计数 CHOP | `countChop` | `threshold`（阈值）、`limittype`（限制类型）、`limitmin/max`（最小/最大限制值） | 具有循环或限幅功能的事件计数器。 |

### 音频

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| CHOP模块的音频文件输入 | `audiofileinChop` | `file`、`volume`、`play`、`speed`、`trim` | 播放音频文件。 |
| CHOP模块的音频设备输入 | `audiodeviceinChop` | `device`、`channels` | 实时麦克风/线路输入。 |
| 音频频谱CHOP模块 | `audiospectrumChop` | `size`（FFT尺寸）、`outputformat`（0=功率值，1=幅值） | 进行FFT频率分析。 |
| 音频频段均衡CHOP模块 | `audiobandeqChop` | `bands`、各频段的`gaindb` | 实现特定频段的隔离处理。 |
| CHOP模块的音频设备输出 | `audiodeviceoutChop` | `device` | 音频播放输出。 |

### 数学/逻辑运算

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Math CHOP | `mathChop` | `preoff`、`gain`、`postoff`、`chanop`（0=关闭，1=相加，2=相减，3=相乘……） | 对音频通道执行数学运算，堪称多功能工具。 |
| Logic CHOP | `logicChop` | `preop`（0=关闭，1=与，2=或，3=异或，4=与非），`convert` | 对音频通道执行布尔逻辑运算。 |
| Filter CHOP | `filterChop` | `type`（0=低通，1=带通，2=高通，3=陷波），`cutofffreq`、`filterwidth` | 用于平滑处理、抑制信号或对信号进行滤波。 |
| Lag CHOP | `lagChop` | `lag1/2`、`overshoot1/2` | 实现带有过冲效果的平滑过渡。 |
| Limit CHOP | `limitChop` | `type`（0=限制在固定值，1=循环，2=之字形变化），`min/max` | 对音频通道的值进行限制或循环处理。 |
| Speed CHOP | `speedChop` | （无重要参数） | 对数值进行积分运算（将速度转换为位置，将加速度转换为速度）。 |
| Trigger CHOP | `triggerChop` | `attack`、`peak`、`decay`、`sustain`、`release` | 基于触发事件生成ADSR包络曲线。 |
| Select CHOP | `selectChop` | `chop`（路径）、`channames` | 引用其他CHOP模块中的音频通道。 |
| Merge CHOP | `mergeChop` | `align`（0=扩展，1=裁剪至最短，2=裁剪至最长） | 合并多个CHOP模块产生的音频通道。 |
| Null CHOP | `nullChop` | （无重要参数） | 用于组织音频流及作为引用节点。 |

### 输入设备

| 操作符 | 类型名称 | 用途 |
|----------|-----------|-----|
| CHOP中的鼠标输入 | `mouseinChop` | 鼠标位置、按钮状态及滚轮信息。 |
| CHOP中的键盘输入 | `keyboardinChop` | 键盘按键状态。 |
| CHOP中的MIDI输入 | `midiinChop` | MIDI音符/控制码输入。 |
| CHOP中的OSC输入 | `oscinChop` | OSC消息输入（网络传输）。 |

## SOPs — 曲面操作符（蓝色）

3D几何体：点、多边形、NURBS曲线、网格。

### 生成器

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| 网格SOP | `gridSop` | `rows`（行数）、`cols`（列数）、`sizex/y`（尺寸）、`type`（0=多边形，1=网格，2=NURBS） | 生成平面网格。可用于位移效果及实例化操作的基础。 |
| 球体SOP | `sphereSop` | `type`（类型）、`rows`、`cols`、`radius`（半径） | 生成球形几何体。 |
| 长方体SOP | `boxSop` | `sizex/y/z`（尺寸） | 生成长方体几何体。 |
| 环面SOP | `torusSop` | `radiusx/y`（半径）、`rows`、`cols` | 生成环面形状。 |
| 圆形SOP | `circleSop` | `type`（类型）、`radius`（半径）、`divs`（分段数） | 生成圆形/环形几何体。 |
| 线条SOP | `lineSop` | `dist`（距离）、`points`（点坐标） | 生成线段。 |
| 文本SOP | `textSop` | `text`（文本内容）、`fontsizex`（字体大小）、`fontfile`（字体文件）、`extrude`（挤出高度） | 生成3D文本几何体。 |

### 修改器

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| 变换 SOP | `transformSop` | `tx/ty/tz`, `rx/ry/rz`, `sx/sy/sz` | 对几何体进行变换（平移、旋转、缩放）。 |
| 噪声 SOP | `noiseSop` | `type`, `amp`, `period`, `roughness` | 通过噪声效果使几何体发生变形。 |
| 排序 SOP | `sortSop` | `ptsort`, `primsort` | 对点或图元进行重新排序。 |
| 拓扑优化 SOP | `facetSop` | `unique`, `consolidate`, `computenormals` | 计算法线、合并重复点以及优化拓扑结构。 |
| 合并 SOP | `mergeSop` | （无重要参数） | 将多个几何体输入合并在一起。 |
| 透明 SOP | `nullSop` | （无重要参数） | 实现透明传输效果。 |

## DATs — 数据操作符（白色）

文本、表格、脚本、网络数据。

### 核心类型

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| 表格 DAT | `tableDat` | （可直接编辑内容） | 类似电子表格的数据结构。 |
| 文本 DAT | `textDat` | （可直接编辑内容） | 用于存储任意文本内容，如着色器代码、配置文件及脚本。 |
| 脚本 DAT | `scriptDat` | `language`（0=Python，1=C++） | 用于实现自定义回调函数及处理 DAT 数据。 |
| CHOP 执行 DAT | `chopexecDat` | `chop`（需监控的路径）、回调函数 | 当 CHOP 变量值发生变化时触发 Python 代码执行。 |
| DAT 执行 DAT | `datexecDat` | `dat`（需监控的路径） | 当 DAT 内容发生变化时触发 Python 代码执行。 |
| 面板执行 DAT | `panelexecDat` | `panel` | 当 UI 面板发生事件时触发 Python 代码执行。 |

### 输入/输出

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Web DAT | `webDat` | `url`, `fetchmethod`（0=GET，1=POST） | 发送HTTP请求，实现API集成。 |
| TCP/IP DAT | `tcpipDat` | `address`, `port`, `mode` | 支持TCP网络通信。 |
| OSC输入DAT | `oscinDat` | `port` | 以文本消息形式接收OSC信号。 |
| 串口DAT | `serialDat` | `port`, `baudrate` | 支持串口通信（如Arduino等设备）。 |
| 文件输入DAT | `fileinDat` | `file` | 读取文本文件内容。 |
| 文件输出DAT | `fileoutDat` | `file`, `write` | 写入文本文件内容。 |

### 转换功能

| 操作符 | 类型名称 | 转换方向 | 用途 |
|----------|-----------|-----------|-----|
| DAT转CHOP | `dattochopChop` | DAT -> CHOP | 将表格数据转换为通道数据。 |
| CHOP转DAT | `choptodatDat` | CHOP -> DAT | 将通道数据转换为表格行数据。 |
| SOP转DAT | `soptodatDat` | SOP -> DAT | 以表格形式提取几何数据。 |

## MATs — 材质操作符（黄色）

用于在Render TOP / Geometry COMP中实现3D渲染的材质操作符。

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Phong MAT | `phongMat` | `diff_colorr/g/b`, `spec_colorr/g/b`, `shininess`, `colormap`, `normalmap` | 经典的Phong着色方式。简单且高效。 |
| PBR MAT | `pbrMat` | `basecolorr/g/b`, `metallic`, `roughness`, `normalmap`, `emitcolorr/g/b` | 基于物理的渲染技术。可呈现逼真的材质效果。 |
| GLSL MAT | `glslMat` | `dat`（着色器DAT文件），自定义统一变量 | 用于3D场景的自定义顶点着色器与片段着色器。 |
| Constant MAT | `constMat` | `colorr/g/b`, `colormap` | 仅显示固定的颜色或纹理，无任何着色效果。 |
| Point Sprite MAT | `pointspriteMat` | `colormap`, `scale` | 将点对象渲染为面向相机的精灵图，非常适合用于粒子效果。 |
| Wireframe MAT | `wireframeMat` | `colorr/g/b`, `width` | 线框渲染模式。 |
| Depth MAT | `depthMat` | `near`, `far` | 将深度缓冲区渲染为灰度图像。 |

## COMPs — 组件操作符（灰度模式）

用于容器、3D场景元素及UI组件。

### 3D场景 |

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Geometry COMP | `geometryComp` | `material`（路径）、`instancechop`（路径）、`instancing`（开关） | 带材质渲染几何体，同时支持实例化功能。 |
| Camera COMP | `cameraComp` | `tx/ty/tz`、`rx/ry/rz`、`fov`、`near/far` | 用于 Render TOP 模式的相机。 |
| Light COMP | `lightComp` | `lighttype`（0=点光源，1=定向光，2=聚光灯，3=锥形光）、`dimmer`、`colorr/g/b` | 为 3D 场景提供照明效果。 |
| Ambient Light COMP | `ambientlightComp` | `dimmer`、`colorr/g/b` | 提供环境光照明。 |
| Environment Light COMP | `envlightComp` | `envmap` | 基于图像的照明技术（IBL）。 |

### 容器

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Container COMP | `containerComp` | `w`、`h`、`bgcolor1/2/3` | UI 容器，用于在面板布局中容纳其他 COMPs。 |
| Base COMP | `baseComp` | （无重要参数） | 通用容器，可用于实现网络中的嵌套结构。 |
| Replicator COMP | `replicatorComp` | `template`、`operatorsdat` | 根据表格内容将某个模板操作符复制 N 次。 |

### 工具类组件

| 操作符 | 类型名称 | 关键参数 | 用途 |
|----------|-----------|---------------|-----|
| Window COMP | `windowComp` | `winw/h`、`winoffsetx/y`、`monitor`、`borders` | 用于显示或投影的输出窗口。 |
| Select COMP | `selectComp` | `rowcol`、`panel` | 从其他位置选择并显示内容。 |
| Engine COMP | `engineComp` | `tox`、`externaltox` | 加载外部 .tox 组件，实现子进程隔离。 |
## 不同数据类型转换器概览

| 输入类型 | 输出类型 | 操作符 | 类型名称 |
|----------|----------|--------|-----------|
| CHOP | TOP | 从 CHOP 转换为 TOP | `choptopTop` |
| TOP | CHOP | 从 TOP 转换为 CHOP | `topchopChop` |
| DAT | CHOP | 从 DAT 转换为 CHOP | `dattochopChop` |
| CHOP | DAT | 从 CHOP 转换为 DAT | `choptodatDat` |
| SOP | CHOP | 从 SOP 转换为 CHOP | `soptochopChop` |
| CHOP | SOP | 从 CHOP 转换为 SOP | `choptosopSop` |
| SOP | DAT | 从 SOP 转换为 DAT | `soptodatDat` |
| DAT | SOP | 从 DAT 转换为 SOP | `dattosopSop` |
| SOP | TOP | （需结合 Render TOP 与 Geometry COMP 使用） | — |
| TOP | SOP | 从 TOP 转换为 SOP | `toptosopSop` |
