# p5.js 技能

基于 [p5.js](https://p5js.org/) 的交互式与生成型视觉艺术制作流程。

## 功能说明

该技能能够根据文本提示创建基于浏览器的视觉艺术作品。智能体可处理整个创作流程：创意构思、代码生成、预览、导出以及迭代优化。最终输出为一个独立的 HTML 文件，可在任何浏览器中直接运行——无需构建步骤，无需服务器，仅需通过 CDN 引入脚本文件即可。

生成的并非教程练习内容，而是真正的交互式艺术作品。它融合了生成系统、粒子物理效果、噪声场、着色器特效以及动态排版等技术，并通过精心设计的色彩搭配、分层构图与视觉层次感来呈现艺术效果。

## 模式

| 模式 | 输入 | 输出 |
|------|-------|--------|
| **生成型艺术** | 种子值/参数 | 迭代生成的视觉作品 |
| **数据可视化** | 数据集/API | 交互式图表与自定义数据展示 |
| **交互式体验** | 无（由用户操作） | 鼠标/键盘/触摸控制的绘图功能 |
| **动画/动态图形** | 时间轴/故事板 | 带时间序列的动态效果与动态排版 |
| **3D 场景** | 概念描述 | WebGL 格式的几何体、光照与着色器 |
| **图像处理** | 图像文件 | 像素操作、滤镜效果与点彩风格处理 |
| **音频响应式** | 音频文件/麦克风输入 | 基于声音信号的生成型视觉效果 |

## 导出格式

| 格式 | 导出方法 |
|------|----------|
| **HTML** | 生成独立文件，可在任意浏览器中打开 |
| **PNG** | 使用 `saveCanvas()` 函数——按 ‘s’ 键即可保存 |
| **GIF** | 使用 `saveGif()` 函数——按 ‘g’ 键即可保存 |
| **MP4** | 通过 `scripts/render.sh` 脚本结合帧序列与 ffmpeg 工具导出 |
| **SVG** | 通过 p5.js-svg 渲染器实现矢量格式导出 |

## 先决条件

只需一台现代浏览器即可满足基础使用需求。

如需无界面导出功能，则需要 Node.js、Puppeteer 以及 ffmpeg 工具。

```bash
bash skills/creative/p5js/scripts/setup.sh
```

## 文件结构

```
├── SKILL.md                      # Modes, workflow, creative direction, critical notes
├── README.md                     # This file
├── references/
│   ├── core-api.md              # Canvas, draw loop, transforms, offscreen buffers, math
│   ├── shapes-and-geometry.md   # Primitives, vertices, curves, vectors, SDFs, clipping
│   ├── visual-effects.md        # Noise, flow fields, particles, pixels, textures, feedback
│   ├── animation.md             # Easing, springs, state machines, timelines, transitions
│   ├── typography.md            # Fonts, textToPoints, kinetic text, text masks
│   ├── color-systems.md         # HSB/RGB, palettes, gradients, blend modes, curated colors
│   ├── webgl-and-3d.md          # 3D primitives, camera, lighting, shaders, framebuffers
│   ├── interaction.md           # Mouse, keyboard, touch, DOM, audio, scroll
│   ├── export-pipeline.md       # PNG, GIF, MP4, SVG, headless, tiling, batch export
│   └── troubleshooting.md       # Performance, common mistakes, browser issues, debugging
└── scripts/
    ├── setup.sh                 # Dependency verification
    ├── serve.sh                 # Local dev server (for loading local assets)
    ├── render.sh                # Headless render pipeline (HTML → frames → MP4)
    └── export-frames.js         # Puppeteer frame capture (Node.js)
```
