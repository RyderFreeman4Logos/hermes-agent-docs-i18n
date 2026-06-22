# 实际案例解析

这里展示了六个涵盖不同视频风格的具体工作流示例。每个案例都展示了针对特定需求，任务协调器会选择的团队构成、任务流程图以及所使用的技能与工具。**这些仅为示例，并非模板**——需根据实际需求进行调整。

## 示例 1 — 叙事短片（文本生成图像 → 图像生成视频 → 剪辑）

**需求描述：** 一部时长为90秒的黑色电影风格短片。内容为一个侦探在雨中的城市中行走，配有旁白，所有视觉效果均由AI生成。

**团队成员：**
- `director` — 负责整体构思、任务拆分与最终审核
- `writer` — 撰写剧本及旁白文案（会使用`humanizer`工具让语音更自然）
- `storyboarder` — 制作逐镜分镜表（会使用`excalidraw`工具）
- `image-generator` — 通过本地的ComfyUI工作流为每帧生成静态图像（会使用`comfyui`工具）
- `image-to-video-generator` — 为每帧静态图像添加动画效果（可使用Runway/Kling工具，或通过`comfyui`中的AnimateDiff/WAN工作流实现）
- `voice-talent` — 通过ElevenLabs提供旁白配音
- `audio-mixer` — 负责混合旁白音轨与背景音效
- `editor` — 负责视频剪辑及转场处理
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
- 为控制成本及便于管理，建议优先使用通过 `comfyui` 技能实现的本地 ComfyUI，而非外部 API；但如果未安装 ComfyUI，使用外部 API 也是可行的。
- `editor` 模式仅支持 ffmpeg，无需 Hermes 技能（看板任务指南会自动注入到每个看板工作节点中）。
- Storyboarder 会在生成 Markdown 文件的同时，一并输出 `storyboard.excalidraw` 文件。

## 示例 2 — 产品/营销预告片

**需求简述：** 为某款开发者工具制作一段30秒的产品预告片。内容需包含代码、终端界面及UI界面录屏，搭配旁白，结尾设置行动号召。画面比例为1:1正方形。

**团队分工：**
- `director` — 整体策划
- `copywriter` — 撰写标语、旁白脚本及行动号召语句（会调用 `humanizer` 工具）
- `concept-artist` — 设计风格参考帧（UI原型设计会调用 `claude-design` 工具）
- `renderer-motion-graphics` — 制作动画化的UI序列（使用 Remotion CLI 工具）
- `renderer-ascii` — 制作终端风格的演示场景（使用 `ascii-video` 工具）
- `voice-talent` — 通过 ElevenLabs 提供旁白配音
- `editor` — 合成视频并统一品牌色调
- `audio-mixer` — 混音旁白音轨及背景音乐
- `captioner` — 为无法开启声音自动播放的平台添加字幕
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
- 支持多种专业渲染器共存（动态图形渲染 + ASCII渲染）  
- 由于社交平台普遍采用静音自动播放模式，因此内置字幕生成功能  
- 使用 `claude-design` 技能制作界面原型，可直接对应产品视频的呈现风格  

## 示例 3 — 音乐视频（与指定曲目同步）

**任务描述：** 根据提供的低保真嘻哈曲目制作一段3分钟长的音乐视频。视觉效果需随节奏律动，采用生成式内容与ASCII艺术相结合的方式，分辨率采用垂直9:16比例。  

**团队分工：**  
- `director` — 总导演  
- `music-supervisor` — 分析曲目，输出 `audio/beats.json` 文件（需调用 `songsee` 工具）  
- `storyboarder` — 按节奏编制分镜列表（需使用 `excalidraw` 工具）  
- `renderer-ascii` — 根据低音节拍生成ASCII风格场景（需调用 `ascii-video` 工具）  
- `renderer-p5js` — 根据高音部分生成动态粒子效果场景（需使用 `p5js` 工具）  
- `editor` — 基于 `beats.json` 文件进行片段剪辑与合成  
- `reviewer` — 负责同步质量检测工作  

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
- 首先运行 `music-supervisor`——通过 `beats.json` 控制渲染器的使用
- `editor` 直接读取 `beats.json`，以便将剪辑内容与贝斯鼓点对齐
- 不需要语音演员——音乐本身即为音频内容
- 使用两种专用渲染器（`ascii-video` 和 `p5js`）以实现多样的视觉效果

## 示例 4 — 数学/算法讲解视频

**简介：** 一段时长为2分钟的算法讲解视频，风格类似3Blue1Brown，包含动画图表、数学公式以及旁白，画面比例为1:1正方形。

**团队角色：**
- `director` — 总导演
- `writer` — 撰写旁白脚本（需调用 `humanizer` 工具）
- `cinematographer` — 视觉设计规范制定（需调用 `manim-video` 工具）
- `renderer-manim` — 负责所有动画场景的渲染（需调用 `manim-video` 工具）
- `voice-talent` — 通过ElevenLabs提供旁白配音
- `editor` — 负责视频剪辑与音频混音
- `captioner` — 添加字幕

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
- `manim-video` 技能同时负责视觉呈现（导演层面）与场景渲染（实际制作层面）。  
- 当需要时，该技能的参考文档（包括动画设计思路、场景规划及公式相关内容）会通过渲染器的固定技能自动加载。  

## 示例 5 — 仅音乐轨道的 ASCII 视频  

**简介：** 一段时长为60秒的纯ASCII视频，能随现有音乐轨道实时变化。无需旁白，也不使用其他工具，画面比例为1:1正方形。  

**团队成员：**  
- `director` — 导演  
- `music-supervisor` — 音乐轨道分析（调用 `songsee` 工具）  
- `renderer-ascii` — 负责所有视觉效果生成（调用 `ascii-video` 工具）  
- `editor` — 负责视频剪辑及音频混合  

**任务流程图：**
```
T0  director           decompose
T1  music-supervisor   analyze track                       (parent: T0)
T2a renderer-ascii     scene 1                             (parents: T1, T0)
T2b renderer-ascii     scene 2                             (parents: T1, T0)
T2c renderer-ascii     scene 3                             (parents: T1, T0)
T3  editor             stitch + mux audio                  (parents: T2*)
```

**关键决策：**  
- 针对专注于单一工具的项目，采用最精简的团队配置（4个角色）；  
- 无需审核员——由于是短期实验性作品，由项目负责人直接审批；  
- 所有场景均使用同一个 `renderer-ascii` 角色，因为 `ascii-video` 技能已能满足所有需求。  

此示例体现了“**避免过度拆分**”的原则：通过一个渲染器处理三个场景即可，无需创建三个独立的渲染器角色。  

## 示例6 — 实时艺术/装置艺术  

**简介：** 为一场画廊展览设计的2分钟音频驱动视觉作品。基于音频输入信号运行，采用TouchDesigner制作，分辨率为16:9 4K。  

**团队成员：**  
- `director`（项目负责人）  
- `cinematographer`（视觉风格设计师）——负责制定视觉规范（加载 `touchdesigner-mcp`）  
- `renderer-touchdesigner`（渲染师）——负责所有视觉内容的生成及输出到磁盘（加载 `touchdesigner-mcp`）  
- `audio-mixer`（音频混音师）——对录制的音频进行最终音量调整（若音频已预先混合则可选）  
- `editor`（剪辑师）——从TouchDesigner的录制文件中整理出最终视频片段  
- `reviewer`（质量审核员）——负责视觉效果的质量检查  

**任务流程图：**
```
T0  director                decompose
T1  cinematographer         TD operator graph spec           (parent: T0)
T2  renderer-touchdesigner  build TD network + record output (parent: T1)
T3  editor                  trim + audio mux                 (parent: T2)
T4  reviewer                final QA                         (parent: T3)
```

**核心选择：**
- `touchdesigner-mcp`用于控制正在运行的TouchDesigner实例——摄影师负责设计操作图，而渲染器则负责将其执行
- 输出结果为来自运行中TD网络的实时录制内容，而非先渲染为帧再处理的结果；剪辑人员主要的工作就是对素材进行裁剪

## 模式识别

当用户描述某段视频时，需通过以下特征将其匹配到相应的示例类型：

- **剧情、角色、剧本对话** → 示例1（叙事类）
- **特定产品、行动号召、品牌色彩、旁白** → 示例2（营销类）
- **提供音轨文件，且内容“与音乐同步”** → 示例3（音乐视频类）
- **“解释X的工作原理”，涉及数学/算法/概念的讲解** → 示例4（Manim动画讲解类）
- **终端风格、ASCII字符、复古像素风** → 示例5（ASCII艺术类）
- **“音频驱动”、“实时生成”、“装置艺术”相关描述** → 示例6（TouchDesigner类）
- **漫画风格的叙事** → 使用`renderer-comic`（`baoyu-comic`技能）
- **复古游戏/像素艺术风格** → 使用`renderer-pixel`（`pixel-art`技能）
- **3D场景、真实感极强的环境** → 使用`renderer-3d`（`blender-mcp`）
- **生成艺术、粒子系统、着色器效果** → 使用`renderer-p5js`（`p5js`）
- **AI生成的真实感静态图像及动画** → 使用`renderer-comfyui`（`comfyui`），既可用于处理静态图像，也可实现图像转视频功能
- **“介绍系统工作原理的视频”，递归演示类型** → 可由上述任意一种方式组合实现；这里的递归属于渲染技术范畴，而非风格特征

具体的适用方案需根据实际需求来确定——这些示例仅作为参考起点，而非最终标准。
