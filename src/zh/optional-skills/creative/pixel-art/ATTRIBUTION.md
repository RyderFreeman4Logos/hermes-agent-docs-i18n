# 出处说明

该技能集整合了从第三方 MIT 许可项目移植而来的代码。所有引用内容均在此处标注出处。

## pixel-art-studio（Synero 开发）

- 源码地址：https://github.com/Synero/pixel-art-studio  
- 许可协议：MIT  
- 版权所有：© Synero 及采用 MIT 许可的贡献者  

### 已移植的内容

**`scripts/palettes.py`** — 包含 23 组命名 RGB 调色板的 `PALETTES` 字典（涵盖硬件相关及艺术风格调色板）。其内容直接复制自 pixel-art-studio 的 `scripts/pixelart.py` 文件。

**`scripts/pixel_art_video.py`** — 包含 12 组用于生成程序化动画的初始化/绘制函数对（如 `stars`、`fireflies`、`leaves`、`dust_motes`、`sparkles`、`rain`、`lightning`、`bubbles`、`embers`、`snowflakes`、`neon_pulse`、`heat_shimmer`），以及 `SCENES` 到图层的映射关系。该文件从 `scripts/pixelart_video.py` 移植而来，并进行了少量优化：
- 为私有辅助函数添加了下划线前缀（如 `_px`、`_pixel_cross`）
- 将 `SCENE_ANIMATIONS` 重命名为 `SCENES`，并重新设计结构，用于存储图层名称（字符串类型），而非通过 `globals()` 查找的函数名字符串
- 对 `generate_video()` 函数进行了拆分：去掉了基于 Pollinations 的文本转图像功能（Hermes 自有 `image_generate` 和 `pixel_art()` 流水线可用于生成基础帧），仅保留叠加效果及 FFmpeg 编码步骤
- 帧文件存储路径改为使用 `tempfile.TemporaryDirectory` 管理，无需手动清理
- 出于安全性考虑，将调用 FFmpeg 的方式从 `os.system` 改为 `subprocess.run(check=True)`

### 未移植的内容

- Wu 的颜色量化算法（PIL 内置的 `quantize` 函数已足够使用）
- 基于 Sobel 算法的边缘感知降采样功能（需要 scipy 库，添加依赖不值得）
- Bayer/Atkinson 随机抖动算法（需重新实现 numpy 相关功能，为控制项目规模未纳入）
- Pollinations 文本转图像生成功能（对应 `pixelart_image.py` 及 `pixelart_video.py` 中的 `generate_base()` 函数）——Hermes 已具备 `image_generate` 功能

### 许可协议兼容性

pixel-art-studio 采用 MIT 许可协议，允许在注明出处的情况下重新分发。本技能在当前文件及 SKILL.md 的致谢部分均保留了原始版权声明，未对任何代码进行重新许可。

---

## pixel-art 技能本身

- 许可协议：MIT（继承自 hermes-agent 项目仓库）  
- 技能框架的初始创建者：dodo-reach  
- 调色板及视频功能的扩展：由 Hermes Agent 的贡献者们完成
