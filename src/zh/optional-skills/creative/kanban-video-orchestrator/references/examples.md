# 实际应用案例

共包含六个针对不同视频风格的典型工作流示例。每个案例均展示了团队构成、任务流程图，以及调度器为完成相应任务所选择的技能与工具。**这些仅为示例，并非模板**——需根据实际需求进行调整。

## 示例 1 — 叙事短片（文本生成图像 → 图像生成视频 → 剪辑）

**任务描述：** 制作一部时长90秒的黑色电影风格短片。内容为一名侦探在雨中的城市中行走，配有旁白，所有视觉内容均由AI生成。

**团队成员：**
- `director` — 负责整体构思、任务拆分与最终审核
- `writer` — 撰写剧本及旁白文案（调用 `humanizer` 工具以实现自然语音效果）
- `storyboarder` — 制作逐镜分镜表（使用 `excalidraw` 工具）
- `image-generator` — 通过本地的ComfyUI工作流为每帧生成静态图像（依赖 `comfyui` 工具）
- `image-to-video-generator` — 将每帧静态图像转化为动态视频（可使用Runway/Kling工具，或通过 `comfyui` 调用AnimateDiff/WAN工作流）
- `voice-talent` — 通过ElevenLabs提供旁白配音
- `audio-mixer` — 混合旁白音轨与背景音效
- `editor` — 负责视频剪辑与转场处理
- `reviewer` — 进行最终质量检查

**任务流程图：**
```
T0  director         decompose
T1  writer           script + voiceover.md                    (parent: T0)
T2  storyboarder     shot list with framing per beat          (parent: T1)
T3  image-generator  one still per shot (~12 shots)           (parent: T2)
T4  image-to-video   animate each still                       (parent: T3)
T5  voice-talent     generate narration audio                 (parent: T1)
T6  audio-mixer      mix VO + ambient                         (parent: T5)
T7  editor           cut + transitions + audio mux            (parents: T4, T6)
T8  reviewer         final QA                                 (parent: T7)
```

**关键选择：**  
为控制成本与提升管理效率，优先使用通过 `comfyui` 技能实现的本地 ComfyUI，而非外部 API；但如果未安装 ComfyUI，使用外部 API 也是可行的。  
`editor` 模式仅依赖 ffmpeg，无需 Hermes 技能（每个工作节点会自动注入看板任务指引）。  
Storyboarder 会在生成 Markdown 文件的同时输出 `storyboard.excalidraw` 格式的画面。  

## 示例 2 — 产品/营销预告片  

**简述：** 为一款开发者工具制作30秒长的预告片。内容包含代码、终端界面及UI操作录屏，搭配旁白，结尾设有行动号召。视频比例为1:1正方形。  

**团队成员：**  
- `director` — 整体策划  
- `copywriter` — 撰写标语、旁白脚本及行动号召语（会调用 `humanizer` 工具）  
- `concept-artist` — 设计风格参考帧（UI原型设计会调用 `claude-design` 工具）  
- `renderer-motion-graphics` — 制作动态UI序列（使用 Remotion CLI 工具）  
- `renderer-ascii` — 制作终端风格的演示场景（使用 `ascii-video` 工具）  
- `voice-talent` — 通过 ElevenLabs 提供旁白配音  
- `editor` — 视频剪辑及品牌色彩统一处理  
- `audio-mixer` — 混音旁白音轨与背景音乐  
- `captioner` — 为静音自动播放平台添加字幕  
- `masterer` — 输出1:1、9:16及16:9三种比例的最终视频文件  

**任务流程图：**
```
T0  director              decompose
T1  copywriter            copy.md + cta + vo script               (parent: T0)
T2  concept-artist        visual-spec.md + style frames           (parent: T1)
T3a renderer-motion-graphics  scene 1: UI sequence                (parent: T2)
T3b renderer-ascii        scene 2: terminal demo                  (parent: T2)
T3c renderer-motion-graphics  scene 3: feature highlight          (parent: T2)
T3d renderer-motion-graphics  scene 4: CTA card                   (parent: T2)
T4  voice-talent          narration                                (parent: T1)
T5  audio-mixer           VO + music bed                          (parent: T4)
T6  editor                cut + transitions                        (parents: T3*, T5)
T7  captioner             SRT + burned subtitles                  (parent: T6)
T8  masterer              1:1, 9:16, 16:9 variants                (parent: T7)
```

**核心设计选择：**  
- 同时使用多种专业渲染器（动态图形 + ASCII艺术）  
- 由于社交平台普遍采用静音自动播放模式，因此内置字幕生成功能  
- 使用 `claude-design` 技能进行界面原型设计，可直接对应产品视频的呈现风格  

## 示例 3 — 音乐视频（与提供的曲目同步）

**任务描述：** 根据给定的低保真嘻哈曲目制作一段3分钟长的音乐视频。视觉效果需随节奏起伏变化，采用生成式内容与ASCII艺术相结合的形式，最终输出为9:16比例的竖屏视频。  

**团队分工：**  
- `director` — 总导演  
- `music-supervisor` — 分析曲目并生成 `audio/beats.json` 文件（需使用 `songsee` 工具）  
- `storyboarder` — 按节奏编排镜头列表（需使用 `excalidraw` 工具）  
- `renderer-ascii` — 生成与低音节拍同步的ASCII场景（需使用 `ascii-video` 工具）  
- `renderer-p5js` — 生成与高音部分同步的粒子效果场景（需使用 `p5js` 工具）  
- `editor` — 基于 `beats.json` 文件进行片段剪辑与合成  
- `reviewer` — 负责同步质量检查  

**任务流程图：**
```
T0  director              decompose
T1  music-supervisor      analyze track → beats.json + spectrogram  (parent: T0)
T2  storyboarder          shot list aligned to beats                (parents: T1, T0)
T3a renderer-ascii        scene 1: bass-driven ASCII                (parent: T2)
T3b renderer-p5js         scene 2: high-end particle field          (parent: T2)
... (more scenes)
T4  editor                cut to beats + mux track                  (parents: T3*, T1)
T5  reviewer              sync QA + final approval                  (parent: T4)
```

**核心选择：**
- 首先运行 `music-supervisor`——通过 `beats.json` 控制渲染器的启动
- `editor` 直接使用 `beats.json` 将剪辑内容与贝斯鼓点对齐
- 无需语音演员——音乐本身即为核心音频
- 使用两种专用渲染器（`ascii-video` 和 `p5js`）以实现视觉效果多样化

## 示例 4 — 数学/算法讲解视频

**简介：** 一段时长为2分钟的算法讲解视频，采用3Blue1Brown的风格，包含动画图表、数学公式以及旁白，画面比例为1:1正方形。

**团队角色：**
- `director`——项目统筹
- `writer`——撰写旁白脚本（需调用 `humanizer` 工具）
- `cinematographer`——确定视觉设计规范（需调用 `manim-video` 工具）
- `renderer-manim`——负责所有动画场景的渲染（需调用 `manim-video` 工具）
- `voice-talent`——通过ElevenLabs提供旁白配音
- `editor`——负责视频片段拼接及音频混合
- `captioner`——为视频添加字幕

**任务流程图：**
```
T0  director           decompose
T1  writer             script + narration                  (parent: T0)
T2  cinematographer    visual spec for all scenes           (parent: T1)
T3a-Tn renderer-manim  scenes 1..N                          (parents: T2)
T4  voice-talent       narration audio                      (parent: T1)
T5  editor             cut + mux                            (parents: T3*, T4)
T6  captioner          SRT + burn                           (parent: T5)
```

**核心选择：**  
- `manim-video` 技能同时负责视觉呈现（即电影摄影师的角色）与场景渲染（即实际场景的生成）。  
- 当需要时，`manim-video` 技能的相关参考文档（包括动画设计思路、场景规划、公式等内容）会通过渲染器中的固定技能自动加载。  

## 示例 5 — 仅包含音乐轨道的 ASCII 视频

**简介：** 一段时长为60秒的纯ASCII视频，会根据现有的音乐轨道实时生成内容。无需旁白，也不需要其他工具，视频比例为1:1的正方形。  

**团队成员：**  
- `director`（导演）  
- `music-supervisor`（音乐监督）——负责音乐轨道分析（会加载 `songsee` 工具）  
- `renderer-ascii`（ASCII渲染器）——负责所有视觉内容的生成（会加载 `ascii-video` 工具）  
- `editor`（编辑人员）——负责视频的拼接及音频混合处理  

**任务流程图：**
```
T0  director           decompose
T1  music-supervisor   analyze track                       (parent: T0)
T2a renderer-ascii     scene 1                             (parents: T1, T0)
T2b renderer-ascii     scene 2                             (parents: T1, T0)
T2c renderer-ascii     scene 3                             (parents: T1, T0)
T3  editor             stitch + mux audio                  (parents: T2*)
```

**核心决策：**  
- 针对专注于单一工具的项目，采用最小化团队配置（4个角色）；  
- 无需审核员——由于属于短期实验性作品，由项目负责人直接审批；  
- 所有场景均通过同一个`renderer-ascii`角色处理，因为`ascii-video`技能已能满足所有需求。  

该示例体现了“**避免过度拆分**”的原则：通过一个渲染器处理三个场景即可，无需创建三个独立的渲染器角色。  

## 示例6 — 实时艺术/装置艺术  

**简介：** 为美术馆展览设计的2分钟音频驱动视觉作品。基于音频输入信号运行，采用TouchDesigner制作，分辨率为16:9 4K。  

**团队成员：**  
- `director`（项目负责人）  
- `cinematographer`（视觉风格设计师）——负责制定视觉语言规范（加载`touchdesigner-mcp`）  
- `renderer-touchdesigner`（TouchDesigner渲染师）——负责所有视觉效果呈现及内容导出至磁盘（加载`touchdesigner-mcp`）  
- `audio-mixer`（音频混音师）——对录制的音频进行最终音量调整（若音频已预先混合则可选）  
- `editor`（剪辑师）——从TouchDesigner的录制文件中整合最终视频片段  
- `reviewer`（视觉质量审核员）——负责视觉效果的质量检查  

**任务流程图：**
```
T0  director                decompose
T1  cinematographer         TD operator graph spec           (parent: T0)
T2  renderer-touchdesigner  build TD network + record output (parent: T1)
T3  editor                  trim + audio mux                 (parent: T2)
T4  reviewer                final QA                         (parent: T3)
```

**核心选择：**
- `touchdesigner-mcp`用于控制正在运行的TouchDesigner实例——由摄影师设计操作节点图，再由渲染器将其执行
- 输出的是来自运行中的TD网络的实时录像，而非先渲染为帧再处理的结果；剪辑人员主要负责对视频进行裁剪

## 模式识别

当用户描述某段视频时，需通过以下特征来匹配对应的示例类型：

- **剧情、角色、剧本对话** → 示例1（叙事类）
- **特定产品、行动号召、品牌色彩、旁白** → 示例2（营销类）
- **提供音轨文件且“与音乐同步”** → 示例3（音乐视频类）
- **“解释X的工作原理”、数学/算法/概念讲解** → 示例4（动画演示类）
- **终端风格、ASCII字符、复古像素风** → 示例5（ASCII艺术类）
- **“音频驱动”、“实时处理”、“装置艺术”** → 示例6（TouchDesigner相关）
- **漫画风格的叙事** → 使用`renderer-comic`（`baoyu-comic`技能）
- **复古游戏/像素艺术风格** → 使用`renderer-pixel`（`pixel-art`技能）
- **3D场景、逼真照片级环境** → 使用`renderer-3d`（通过`blender -b`脚本调用Blender）
- **生成艺术、粒子系统、着色器效果** → 使用`renderer-p5js`（`p5js`库）
- **AI生成的逼真静态图片+动画** → 使用`renderer-comfyui`（`comfyui`库），既可用于处理静态图片，也可实现图像转视频
- **“介绍系统工作原理的视频”、递归演示** → 可由上述任意一种方式组合实现；此处所说的递归指的是渲染技术，而非风格表现形式
具体的团队构成应依据具体的项目需求来确定——这些示例仅作为参考起点，而非最终定论。
