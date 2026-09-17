---
name: ascii-art
description: "ASCII art: pyfiglet, cowsay, boxes, image-to-ascii."
version: 4.0.0
author: 0xbyt4, Hermes Agent
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ASCII, Art, Banners, Creative, Unicode, Text-Art, pyfiglet, figlet, cowsay, boxes]
    related_skills: [excalidraw]

---

# ASCII艺术生成技能

针对不同的ASCII艺术需求，提供了多种工具。所有工具均为本地CLI程序或免费的REST API——无需API密钥。

## 工具1：文本横幅（pyfiglet — 本地版）

可将文本转换为大型ASCII艺术横幅。内置571种字体。

### 设置方式

```bash
pip install pyfiglet --break-system-packages -q
```

### 使用方法

```bash
python -m pyfiglet "YOUR TEXT" -f slant
python -m pyfiglet "TEXT" -f doom -w 80    # Set width
python -m pyfiglet --list_fonts             # List all 571 fonts
```

### 推荐字体

| 风格 | 字体 | 最佳适用场景 |
|-------|------|------------|
| 简洁现代 | `slant` | 项目名称、页眉 |
| 粗体方正 | `doom` | 标题、标志 |
| 大号易读 | `big` | 横幅文字 |
| 经典横幅 | `banner3` | 宽屏显示 |
| 紧凑型 | `small` | 字幕 |
| 科技风 | `cyberlarge` | 科技主题内容 |
| 3D效果 | `3-d` | 启动画面 |
| 哥特风 | `gothic` | 强烈视觉冲击的文本 |

### 小贴士

- 提供2-3种字体供预览，让用户自行选择最喜欢的风格
- 短文本（1-8个字符）搭配`doom`或`block`等细节丰富的字体效果最佳
- 长文本则更适合使用`small`或`mini`这类紧凑型字体

## 工具2：文本横幅（ASCII化API — 远程调用，无需安装）

这是一个免费的REST API，可将文本转换为ASCII艺术。提供250多种FIGlet字体，直接返回纯文本，无需额外解析。当未安装pyfiglet或需要快速替代方案时，可使用此工具。

### 使用方法（通过终端的curl命令）

```bash
# Basic text banner (default font)
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello+World"

# With a specific font
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Slant"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Doom"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Star+Wars"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=3-D"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Banner3"

# List all available fonts (returns JSON array)
curl -s "https://asciified.thelicato.io/api/v2/fonts"
```

### 小贴士

- 在文本参数中，需将空格用 `+` 进行 URL 编码  
- 返回结果为纯文本形式的 ASCII 艺术图——无需 JSON 包装，可直接显示  
- 字体名称区分大小写；请使用字体查询接口获取准确名称  
- 只要终端支持 curl 即可使用——无需 Python 或 pip  

## 工具 3：Cowsay（消息艺术图）

这款经典工具能够将文本包裹在由 ASCII 字符构成的对话气泡中。  

### 设置步骤

```bash
sudo apt install cowsay -y    # Debian/Ubuntu
# brew install cowsay         # macOS
```

### 使用方法

```bash
cowsay "Hello World"
cowsay -f tux "Linux rules"       # Tux the penguin
cowsay -f dragon "Rawr!"          # Dragon
cowsay -f stegosaurus "Roar!"     # Stegosaurus
cowthink "Hmm..."                  # Thought bubble
cowsay -l                          # List all characters
```

### 可用角色（50个以上）

`beavis.zen`、`bong`、`bunny`、`cheese`、`daemon`、`default`、`dragon`、
`dragon-and-cow`、`elephant`、`eyes`、`flaming-skull`、`ghostbusters`、
`hellokitty`、`kiss`、`kitty`、`koala`、`luke-koala`、`mech-and-cow`、
`meow`、`moofasa`、`moose`、`ren`、`sheep`、`skeleton`、`small`、
`stegosaurus`、`stimpy`、`supermilker`、`surgery`、`three-eyes`、
`turkey`、`turtle`、`tux`、`udder`、`vader`、`vader-koala`、`www`

### 眼睛/舌头修饰符

```bash
cowsay -b "Borg"       # =_= eyes
cowsay -d "Dead"       # x_x eyes
cowsay -g "Greedy"     # $_$ eyes
cowsay -p "Paranoid"   # @_@ eyes
cowsay -s "Stoned"     # *_* eyes
cowsay -w "Wired"      # O_O eyes
cowsay -e "OO" "Msg"   # Custom eyes
cowsay -T "U " "Msg"   # Custom tongue
```

## 工具 4：Boxes（装饰性边框）

可在任意文本周围绘制美观的 ASCII 艺术边框/框架，内置超过 70 种设计模板。

### 设置

```bash
sudo apt install boxes -y    # Debian/Ubuntu
# brew install boxes         # macOS
```

### 使用方法

```bash
echo "Hello World" | boxes                    # Default box
echo "Hello World" | boxes -d stone           # Stone border
echo "Hello World" | boxes -d parchment       # Parchment scroll
echo "Hello World" | boxes -d cat             # Cat border
echo "Hello World" | boxes -d dog             # Dog border
echo "Hello World" | boxes -d unicornsay      # Unicorn
echo "Hello World" | boxes -d diamonds        # Diamond pattern
echo "Hello World" | boxes -d c-cmt           # C-style comment
echo "Hello World" | boxes -d html-cmt        # HTML comment
echo "Hello World" | boxes -a c               # Center text
boxes -l                                       # List all 70+ designs
```

### 可与 pyfiglet 或 asciified 结合使用

```bash
python -m pyfiglet "HERMES" -f slant | boxes -d stone
# Or without pyfiglet installed:
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=HERMES&font=Slant" | boxes -d stone
```

## 工具 5：TOIlet（彩色文本艺术）

类似于 pyfiglet，但具备 ANSI 颜色效果与视觉滤镜功能，非常适合为终端界面增添美观效果。

### 设置

```bash
sudo apt install toilet toilet-fonts -y    # Debian/Ubuntu
# brew install toilet                      # macOS
```

### 使用方法

```bash
toilet "Hello World"                    # Basic text art
toilet -f bigmono12 "Hello"            # Specific font
toilet --gay "Rainbow!"                 # Rainbow coloring
toilet --metal "Metal!"                 # Metallic effect
toilet -F border "Bordered"             # Add border
toilet -F border --gay "Fancy!"         # Combined effects
toilet -f pagga "Block"                 # Block-style font (unique to toilet)
toilet -F list                          # List available filters
```

### 过滤器

`crop`、`gay`（彩虹效果）、`metal`、`flip`、`flop`、`180`、`left`、`right`、`border`

**注意**：toilet工具会输出用于设置颜色的ANSI转义码——在终端中可以正常显示，但在某些环境中可能无法正确呈现（例如纯文本文件、某些聊天平台）。 

## 工具6：图像转ASCII艺术

将图片（PNG、JPEG、GIF、WEBP格式）转换为ASCII艺术。

### 方案A：ascii-image-converter（推荐，现代版本）

```bash
# Install
sudo snap install ascii-image-converter
# OR: go install github.com/TheZoraiz/ascii-image-converter@latest
```

```bash
ascii-image-converter image.png                  # Basic
ascii-image-converter image.png -C               # Color output
ascii-image-converter image.png -d 60,30         # Set dimensions
ascii-image-converter image.png -b               # Braille characters
ascii-image-converter image.png -n               # Negative/inverted
ascii-image-converter https://url/image.jpg      # Direct URL
ascii-image-converter image.png --save-txt out   # Save as text
```

### 选项 B：jp2a（轻量级，仅支持 JPEG 格式）

```bash
sudo apt install jp2a -y
jp2a --width=80 image.jpg
jp2a --colors image.jpg              # Colorized
```

## 工具 7：搜索现成 ASCII 艺术作品

用于搜索网络上精心筛选的 ASCII 艺术作品。可结合 `terminal` 和 `curl` 使用。

### 来源 A：ascii.co.uk（推荐用于获取现成作品）

该网站拥有按主题分类的大量经典 ASCII 艺术作品，这些作品均嵌在 HTML 的 `<pre>` 标签中。可通过 `curl` 获取页面内容，再利用一段简短的 Python 代码提取其中的艺术作品。

**URL 模式：** `https://ascii.co.uk/art/{subject}`

**步骤 1 — 获取页面内容：**

```bash
curl -s 'https://ascii.co.uk/art/cat' -o /tmp/ascii_art.html
```

**第 2 步——从预置标签中提取艺术内容：**

```python
import re, html
with open('/tmp/ascii_art.html') as f:
    text = f.read()
arts = re.findall(r'<pre[^>]*>(.*?)</pre>', text, re.DOTALL)
for art in arts:
    clean = re.sub(r'<[^>]+>', '', art)
    clean = html.unescape(clean).strip()
    if len(clean) > 30:
        print(clean)
        print('\n---\n')
```

**可用主题**（用作 URL 路径）：
- 动物：`cat`、`dog`、`horse`、`bird`、`fish`、`dragon`、`snake`、`rabbit`、`elephant`、`dolphin`、`butterfly`、`owl`、`wolf`、`bear`、`penguin`、`turtle`
- 物品：`car`、`ship`、`airplane`、`rocket`、`guitar`、`computer`、`coffee`、`beer`、`cake`、`house`、`castle`、`sword`、`crown`、`key`
- 自然元素：`tree`、`flower`、`sun`、`moon`、`star`、`mountain`、`ocean`、`rainbow`
- 角色形象：`skull`、`robot`、`angel`、`wizard`、`pirate`、`ninja`、`alien`
- 节日：`christmas`、`halloween`、`valentine`

**使用提示：**
- 请保留艺术家的签名或首字母——这是重要的礼仪要求
- 每页可展示多幅作品——为用户挑选最出色的一幅
- 支持通过 curl 稳定调用，无需 JavaScript

### 来源 B：GitHub Octocat API（有趣的彩蛋）

随机返回一只会说哲理语录的 GitHub Octocat。无需身份验证。

```bash
curl -s https://api.github.com/octocat
```

## 工具 8：有趣的 ASCII 实用工具（通过 curl 使用）

这些免费服务可直接生成 ASCII 艺术作品，非常适合用于增添趣味性。

### 将二维码转换为 ASCII 艺术作品

```bash
curl -s "qrenco.de/Hello+World"
curl -s "qrenco.de/https://example.com"
```

### 以 ASCII 艺术字呈现天气信息

```bash
curl -s "wttr.in/London"          # Full weather report with ASCII graphics
curl -s "wttr.in/Moon"            # Moon phase in ASCII art
curl -s "v2.wttr.in/London"       # Detailed version
```

## 工具 9：LLM 生成的定制艺术（备用方案）

当上述工具无法满足需求时，可使用以下 Unicode 字符直接生成 ASCII 艺术作品：

### 字符调色板

**矩形绘制：** `╔ ╗ ╚ ╝ ║ ═ ╠ ╣ ╦ ╩ ╬ ┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ┼ ╭ ╮ ╰ ╯`

**块状元素：** `░ ▒ ▓ █ ▄ ▀ ▌ ▐ ▖ ▗ ▘ ▝ ▚ ▞`

**几何图形与符号：** `◆ ◇ ◈ ● ○ ◉ ■ □ ▲ △ ▼ ▽ ★ ☆ ✦ ✧ ◀ ▶ ◁ ▷ ⬡ ⬢ ⌂`

### 规则

- 最大宽度：每行不超过 60 个字符（符合终端显示要求）
- 最高高度：横幅为 15 行，场景图为 25 行
- 仅限等宽字体：输出内容必须在等宽字体中正确显示

## 决策流程

1. **将文本作为横幅** → 若已安装 pyfiglet，则使用该工具；否则通过 curl 调用 asciified API
2. **用有趣的字符艺术包裹消息** → 使用 cowsay 工具
3. **添加装饰性边框/框架** → 使用矩形字符（可与 pyfiglet/asciified 结合使用）
4. **生成特定主题的图案**（如猫、火箭、龙等）→ 通过 curl 调用 ascii.co.uk 并解析结果
5. **将图片转换为 ASCII 图像** → 使用 ascii-image-converter 或 jp2a 工具
6. **生成二维码** → 通过 curl 调用 qrenco.de 工具
7. **天气/月亮主题图案** → 通过 curl 调用 wttr.in 工具
8. **自定义或创意内容** → 使用 Unicode 字符调色板让 LLM 生成艺术作品
9. **任何未安装的工具** → 先安装该工具，否则选择下一个备用方案
