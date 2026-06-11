# 发现应用

## 列出所有应用

```bash
infsh app list
```

## 分页功能

```bash
infsh app list --page 2
```

## 按类别筛选

```bash
infsh app list --category image
infsh app list --category video
infsh app list --category audio
infsh app list --category text
infsh app list --category other
```

## 搜索

```bash
infsh app search "flux"
infsh app search "video generation"
infsh app search "tts" -l
infsh app search "image" --category image
```

或者使用标志形式：

```bash
infsh app list --search "flux"
infsh app list --search "video generation"
infsh app list --search "tts"
```

## 热门应用

```bash
infsh app list --featured
```

## 最新内容优先显示

```bash
infsh app list --new
```

## 详细视图

```bash
infsh app list -l
```

显示包含应用名称、类别、描述以及是否为推荐应用的表格。

## 保存到文件

```bash
infsh app list --save apps.json
```

## 您的应用程序

列出您已部署的应用程序：

```bash
infsh app my
infsh app my -l  # detailed
```

## 查看应用详情

```bash
infsh app get falai/flux-dev-lora
infsh app get falai/flux-dev-lora --json
```

显示包括输入/输出架构在内的完整应用信息。

## 按类别分类的热门应用

### 图像生成
- `falai/flux-dev-lora` - FLUX.2 Dev（高画质）
- `falai/flux-2-klein-lora` - FLUX.2 Klein（最快速度）
- `infsh/sdxl` - Stable Diffusion XL
- `google/gemini-3-pro-image-preview` - Gemini 3 Pro
- `xai/grok-imagine-image` - Grok图像生成功能

### 视频生成
- `google/veo-3-1-fast` - Veo 3.1 Fast版本
- `google/veo-3` - Veo 3版本
- `bytedance/seedance-1-5-pro` - Seedance 1.5 Pro版本
- `infsh/ltx-video-2` - 支持音频的LTX Video 2
- `bytedance/omnihuman-1-5` - OmniHuman虚拟形象生成

### 音频处理
- `infsh/dia-tts` - 对话式文本转语音
- `infsh/kokoro-tts` - Kokoro文本转语音
- `infsh/fast-whisper-large-v3` - 快速语音转写工具
- `infsh/diffrythm` - 音乐生成功能

## 文档指南

- [浏览应用列表](https://inference.sh/docs/apps/browsing-grid) - 可视化方式浏览应用
- [应用概览](https://inference.sh/docs/apps/overview) - 了解各类应用
- [运行应用](https://inference.sh/docs/apps/running) - 应用运行指南
