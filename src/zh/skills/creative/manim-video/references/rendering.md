# 渲染参考文档

## 先决条件

```bash
manim --version       # Manim CE
pdflatex --version    # LaTeX
ffmpeg -version       # ffmpeg
```

## CLI 参考手册

```bash
manim -ql script.py Scene1 Scene2    # draft (480p 15fps)
manim -qm script.py Scene1           # medium (720p 30fps)
manim -qh script.py Scene1           # production (1080p 60fps)
manim -ql --format=png -s script.py Scene1  # preview still (last frame)
manim -ql --format=gif script.py Scene1     # GIF output
```

## 质量预设

| 标志 | 分辨率 | 帧率 | 使用场景 |
|------|-----------|-----|----------|
| `-ql` | 854x480 | 15 | 草稿迭代（布局与时间轴调整） |
| `-qm` | 1280x720 | 30 | 预览（适用于文字较多的场景） |
| `-qh` | 1920x1080 | 60 | 最终输出 |

**文本渲染质量：** 使用 `-ql`（480p15）时，文本的排版间距与可读性会明显较差。对于包含大量文字的场景，建议使用 `-qm` 进行预览，以便发现480p分辨率下无法察觉的问题。仅建议在测试布局和动画时间轴时使用 `-ql`。

## 输出结构

```
media/videos/script/480p15/Scene1_Intro.mp4
media/images/script/Scene1_Intro.png  (from -s flag)
```

## 使用 ffmpeg 进行内容拼接

```bash
cat > concat.txt << 'EOF'
file 'media/videos/script/480p15/Scene1_Intro.mp4'
file 'media/videos/script/480p15/Scene2_Core.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

## 添加旁白功能

```bash
# Mux narration
ffmpeg -y -i final.mp4 -i narration.mp3 -c:v copy -c:a aac -b:a 192k -shortest final_narrated.mp4

# Concat per-scene audio first
cat > audio_concat.txt << 'EOF'
file 'audio/scene1.mp3'
file 'audio/scene2.mp3'
EOF
ffmpeg -y -f concat -safe 0 -i audio_concat.txt -c copy full_narration.mp3
```

## 添加背景音乐

```bash
ffmpeg -y -i final.mp4 -i music.mp3 \
  -filter_complex "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=shortest" \
  -c:v copy final_with_music.mp4
```

## GIF导出

```bash
ffmpeg -y -i scene.mp4 \
  -vf "fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  output.gif
```

## 宽高比设置

```bash
manim -ql --resolution 1080,1920 script.py Scene  # 9:16 vertical
manim -ql --resolution 1080,1080 script.py Scene  # 1:1 square
```

## 渲染工作流程

1. 使用 `-ql` 参数批量预览所有场景的渲染结果。
2. 通过 `-s` 参数查看关键节点处的静态帧预览。
3. 仅修复有问题的场景并重新渲染。
4. 使用 ffmpeg 对处理后的片段进行拼接。
5. 检查拼接完成的输出文件。
6. 使用 `-qh` 参数进行最终成品级渲染。
7. 重新拼接并添加音频文件。

## manim.cfg — 项目配置

在项目目录中创建 `manim.cfg` 文件，以便为每个项目设置默认参数：

```ini
[CLI]
quality = low_quality
preview = True
media_dir = ./media

[renderer]
background_color = #0D1117

[tex]
tex_template_file = custom_template.tex
```

这样一来，便无需在每个场景中重复使用相同的 CLI 参数以及 `self.camera.background_color` 了。

## 分节——章节标记

通过为场景中的不同部分添加标记，从而实现有序的输出：

```python
class LongVideo(Scene):
    def construct(self):
        self.next_section("Introduction")
        # ... intro content ...

        self.next_section("Main Concept")
        # ... main content ...

        self.next_section("Conclusion")
        # ... closing ...
```

单独渲染各部分：`manim --save_sections script.py LongVideo`  
该命令会为每个部分生成独立的视频文件——对于较长的视频而言，若只需重新渲染其中某一部分，此方法十分实用。

## manim-voiceover 插件（适用于带旁白的视频）

官方的 `manim-voiceover` 插件可将文本转语音功能直接集成到场景代码中，并自动使动画时长与旁白长度保持同步。相比前述手动使用 ffmpeg 进行合并的方法，这种方式要简洁得多。

### 安装方式

```bash
pip install "manim-voiceover[elevenlabs]"
# Or for free/local TTS:
pip install "manim-voiceover[gtts]"    # Google TTS (free, lower quality)
pip install "manim-voiceover[azure]"   # Azure Cognitive Services
```

### 使用方法

```python
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.elevenlabs import ElevenLabsService

class NarratedScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(ElevenLabsService(
            voice_name="Alice",
            model_id="eleven_multilingual_v2"
        ))

        # Voiceover auto-controls scene duration
        with self.voiceover(text="Here is a circle being drawn.") as tracker:
            self.play(Create(Circle()), run_time=tracker.duration)

        with self.voiceover(text="Now let's transform it into a square.") as tracker:
            self.play(Transform(circle, Square()), run_time=tracker.duration)
```

### 核心功能

- `tracker.duration` — 语音播报的总时长（以秒为单位）
- `tracker.time_until_bookmark("mark1")` — 将特定动画与特定文字同步
- 自动生成字幕 `.srt` 文件
- 在本地缓存音频——重新渲染时无需重新生成文本转语音内容
- 支持的接口包括：ElevenLabs、Azure、Google TTS、pyttsx3（离线模式）以及自定义服务

### 实现精准同步的书签功能

```python
with self.voiceover(text='This is a <bookmark mark="circle"/>circle.') as tracker:
    self.wait_until_bookmark("circle")
    self.play(Create(Circle()), run_time=tracker.time_until_bookmark("circle", limit=1))
```

对于任何带有旁白的视频，这都是推荐的处理方式。而上述手动使用 ffmpeg 进行多路复用的方法，依然适用于添加背景音乐或进行后期音频混音。
