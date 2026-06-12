---
title: "Pixel Art — Pixel art w/ era palettes (NES, Game Boy, PICO-8)"
sidebar_label: "Pixel Art"
description: "Pixel art w/ era palettes (NES, Game Boy, PICO-8)"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 像素艺术

支持使用特定时代的调色板（NES、Game Boy、PICO-8）进行像素艺术创作。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/pixel-art` 安装 |
| 路径 | `optional-skills/creative/pixel-art` |
| 版本 | `2.0.0` |
| 开发者 | dodo-reach |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `creative`、`pixel-art`、`arcade`、`snes`、`nes`、`gameboy`、`retro`、`image`、`video` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行操作。
:::

# 像素艺术

可将任意图像转换为复古风格的像素艺术，还可根据需求将其制作成带有时代特色特效（雨景、萤火虫、雪花、余烬等）的短 MP4 或 GIF 动画。

该技能附带两个脚本：

- `scripts/pixel_art.py` — 将照片转换为像素艺术 PNG 格式（采用 Floyd-Steinberg 点阵算法）
- `scripts/pixel_art_video.py` — 将像素艺术 PNG 转换为动画 MP4 格式（也可生成 GIF）

这两个脚本均可直接导入或运行。若需符合特定时代风格的色彩（如 NES、Game Boy、PICO-8 等），可使用预设值匹配对应硬件的调色板；若希望呈现街机或 SNES 风格，则可选用自适应的 N 色量化功能。

## 适用场景

- 用户希望从原始图像生成复古像素艺术
- 用户要求采用 NES / Game Boy / PICO-8 / C64 / 街机 / SNES 风格
- 用户需要短循环动画（如雨景、夜空、雪景等）
- 海报、专辑封面、社交媒体帖子、精灵图、角色设计、头像制作

## 工作流程

在生成之前，需先与用户确认风格。不同的预设会产生截然不同的输出结果，重新生成则会造成较大成本。

### 第一步 — 提供风格选项

调用 `clarify` 函数并提供 4 个具有代表性的预设选项。根据用户的实际需求选择合适的预设组合，无需一次性展示全部 14 个选项。

当用户的需求不明确时，系统会显示默认菜单：

```python
clarify(
    question="Which pixel-art style do you want?",
    choices=[
        "arcade — bold, chunky 80s cabinet feel (16 colors, 8px)",
        "nes — Nintendo 8-bit hardware palette (54 colors, 8px)",
        "gameboy — 4-shade green Game Boy DMG",
        "snes — cleaner 16-bit look (32 colors, 4px)",
    ],
)
```

如果用户已为该主题指定了特定名称（例如“80年代街机游戏”“Gameboy”），则无需进行`clarify`确认，可直接使用对应的预设。

### 第2步 — 提供动画选项（可选）

若用户要求生成视频/GIF，或认为添加动态效果能提升输出质量，可询问用户希望选择哪个场景：

```python
clarify(
    question="Want to animate it? Pick a scene or skip.",
    choices=[
        "night — stars + fireflies + leaves",
        "urban — rain + neon pulse",
        "snow — falling snowflakes",
        "skip — just the image",
    ],
)
```

请勿连续调用 `clarify` 函数超过两次。若需设定风格，则调用一次；若涉及动画效果，则还需为场景调用一次。如果用户在请求中已明确指定了具体的风格和场景，则无需再使用 `clarify` 函数。

### 第三步 — 生成图像

首先运行 `pixel_art()` 函数；如果用户要求生成动画，可在其输出结果的基础上继续调用 `pixel_art_video()` 函数。

## 预设选项目录

| 预设名称 | 所属时代 | 调色板 | 块尺寸 | 最适合用于 |
|--------|---------|---------|-------|----------|
| `arcade` | 80年代街机游戏 | 自适应16色 | 8像素 | 强烈视觉冲击的海报、角色形象 |
| `snes` | 16位游戏机 | 自适应32色 | 4像素 | 角色设计、细节丰富的场景 |
| `nes` | 8位游戏机 | NES标准色系（54色） | 8像素 | 恢复NES原貌的图像 |
| `gameboy` | DMG掌上游戏机 | 4种绿色色调 | 8像素 | 单色版Game Boy风格 |
| `gameboy_pocket` | 口袋型掌上游戏机 | 4种灰色色调 | 8像素 | 单色版GB Pocket风格 |
| `pico8` | PICO-8游戏机 | 固定16色 | 6像素 | 奇幻风格的复古游戏机外观 |
| `c64` | Commodore 64电脑 | 固定16色 | 8像素 | 8位家用电脑风格 |
| `apple2` | Apple II高分辨率模式 | 固定6色 | 10像素 | 极具复古感、仅6种颜色的风格 |
| `teletext` | BBC文字电视服务 | 纯色8色 | 10像素 | 鲜艳的大色块设计 |
| `mspaint` | Windows画图程序 | 固定24色 | 8像素 | 充满怀旧感的桌面风格 |
| `mono_green` | CRT荧光屏效果 | 2种绿色色调 | 6像素 | 终端/CRT显示器风格 |
| `mono_amber` | CRT琥珀色效果 | 2种琥珀色色调 | 6像素 | 琥珀色显示器外观 |
| `neon` | 霓虹都市风格 | 10种霓虹色 | 6像素 | 气泡波/赛博朋克风格 |
| `pastel` | 柔和淡彩风格 | 10种淡彩色调 | 6像素 | 可爱柔和的视觉效果 |

所有预设的调色板信息均存储在 `scripts/palettes.py` 文件中（完整列表请参阅 `references/palettes.md`，目前共有28种预设调色板）。任何预设选项均可被自定义修改。

```python
pixel_art("in.png", "out.png", preset="snes", palette="PICO_8", block=6)
```

## 场景目录（适用于视频）

| 场景 | 效果 |
|-------|------|
| `night` | 闪烁的星星 + 萤火虫 + 飘落的树叶 |
| `dusk` | 萤火虫 + 闪光粒子 |
| `tavern` | 灰尘微粒 + 温暖的闪光效果 |
| `indoor` | 灰尘微粒 |
| `urban` | 雨水 + 霓虹灯脉动光效 |
| `nature` | 树叶 + 萤火虫 |
| `magic` | 闪光粒子 + 萤火虫 |
| `storm` | 雨水 + 闪电 |
| `underwater` | 气泡 + 微弱闪光 |
| `fire` | 烈焰余烬 + 闪光粒子 |
| `snow` | 雪花 + 闪光粒子 |
| `desert` | 热浪光晕 + 灰尘 |

## 调用方式

### Python（导入方式）

```python
import sys
sys.path.insert(0, "/home/teknium/.hermes/skills/creative/pixel-art/scripts")
from pixel_art import pixel_art
from pixel_art_video import pixel_art_video

# 1. Convert to pixel art
pixel_art("/path/to/photo.jpg", "/tmp/pixel.png", preset="nes")

# 2. Animate (optional)
pixel_art_video(
    "/tmp/pixel.png",
    "/tmp/pixel.mp4",
    scene="night",
    duration=6,
    fps=15,
    seed=42,
    export_gif=True,
)
```

### 命令行界面

```bash
cd /home/teknium/.hermes/skills/creative/pixel-art/scripts

python pixel_art.py in.jpg out.png --preset gameboy
python pixel_art.py in.jpg out.png --preset snes --palette PICO_8 --block 6

python pixel_art_video.py out.png out.mp4 --scene night --duration 6 --gif
```

## 流处理原理

**像素转换流程：**
1. 提升对比度、色彩饱和度及清晰度（针对色彩数量较少的调色板效果更显著）
2. 在量化处理前将图像转为点阵化风格，以简化色调区域
3. 使用 `Image.NEAREST` 方法按“块”进行缩小处理（采用硬像素处理方式，不进行插值）
4. 采用 Floyd-Steinberg 算法进行量化处理，此时可选择自适应的 N 色调色板或预设的硬件色调色板
5. 再次使用 `Image.NEAREST` 方法将图像放大回原始尺寸

在缩小处理后再进行量化，可确保抖动效果与最终的像素网格保持一致；若先量化，则会在那些即将消失的细节上浪费误差扩散资源。

**视频叠加流程：**
- 每帧复制基础帧画面（用于静态背景）
- 根据不同效果为每一帧添加无状态粒子效果（每个效果对应一个函数）
- 通过 ffmpeg 使用 `libx264 -pix_fmt yuv420p -crf 18` 进行编码
- 如需生成 GIF 格式文件，可使用 `palettegen` 和 `paletteuse` 工具

## 依赖项

- Python 3.9 及以上版本
- Pillow 库（可通过 `pip install Pillow` 安装）
- PATH 环境变量中需包含 ffmpeg（仅视频处理需要，Hermes 会自动安装该软件）

## 常见问题与注意事项

- 调色板键名是区分大小写的（如 `"NES"`、`"PICO_8"`、`"GAMEBOY_ORIGINAL"`）。
- 非常小的图像源（宽度小于 100px）在经过 8-10px 的块处理后会变得过于粗糙。如果图像尺寸过小，建议先对其进行放大处理。
- 块大小或调色板数量若为非整数，则会导致量化处理失败——请确保这些数值均为正整数。
- 动画中的粒子数量是根据约 640x480 的图像尺寸设定的。对于超大尺寸的图像，可能需要使用不同的种子值进行二次处理，以调整粒子密度。
- `mono_green` / `mono_amber` 参数会强制将颜色饱和度设为 0.0（即去饱和处理）。如果尝试覆盖此设置并保留色度信息，双色调色板可能会在平滑区域产生条纹现象。
- `clarify` 处理循环：每轮最多调用两次（先处理风格，再处理场景）。避免向用户频繁提出过多选择。

## 验证方法

- 检查输出路径下是否生成了 PNG 格式的文件
- 在预设的块大小下，是否能看到清晰的方形像素块
- 颜色数量是否与预设值一致（可通过肉眼观察图像或使用 `Image.open(p).getcolors()` 函数查看）
- 视频文件应为有效的 MP4 格式（可使用 `ffprobe` 工具打开），且文件大小大于零

## 出处说明

预设的硬件色调色板以及 `pixel_art_video.py` 文件中的程序化动画循环，均源自 [pixel-art-studio](https://github.com/Synero/pixel-art-studio)（采用 MIT 许可协议）。详细信息请参阅该技能目录下的 `ATTRIBUTION.md` 文件。
