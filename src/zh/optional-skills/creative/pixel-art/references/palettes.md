# 命名调色板

`pixel_art()` 函数提供了 28 种既符合硬件特性又富有艺术风格的调色板。这些调色板的数值源自 `pixel-art-studio`（MIT 许可协议）——详情请参阅该技能目录下的 ATTRIBUTION.md 文件。

使用方法：可通过 `palette=` 参数指定调色板名称，或让预设自动选择。

```python
pixel_art("in.png", "out.png", preset="nes")           # preset selects NES
pixel_art("in.png", "out.png", preset="custom", palette="PICO_8", block=6)
```

## 硬件色调板

| 名称 | 颜色数量 | 来源 |
|------|----------|------|
| `NES` | 54 | Nintendo NES游戏机 |
| `C64` | 16 | Commodore 64游戏机 |
| `COMMODORE_64` | 16 | Commodore 64（另一种写法） |
| `ZX_SPECTRUM` | 8 | Sinclair ZX Spectrum游戏机 |
| `APPLE_II_LO` | 16 | Apple II低分辨率模式 |
| `APPLE_II_HI` | 6 | Apple II高分辨率模式 |
| `GAMEBOY_ORIGINAL` | 4 | Game Boy原始版本（绿色） |
| `GAMEBOY_POCKET` | 4 | Game Boy Pocket版本（灰色） |
| `GAMEBOY_VIRTUALBOY` | 4 | Virtual Boy虚拟现实游戏机（红色） |
| `PICO_8` | 16 | PICO-8幻想游戏机 |
| `TELETEXT` | 8 | BBC Teletext文字电视服务 |
| `CGA_MODE4_PAL1` | 4 | IBM CGA图形模式 |
| `MSX` | 15 | MSX游戏机 |
| `MICROSOFT_WINDOWS_16` | 16 | Windows 3.x系统默认色调 |
| `MICROSOFT_WINDOWS_PAINT` | 24 | MS Paint经典版本 |
| `MONO_BW` | 2 | 黑白色调 |
| `MONO_AMBER` | 2 | 棕黄色单色色调 |
| `MONO_GREEN` | 2 | 绿色单色色调 |

## 艺术风格色调板

| 名称 | 颜色数量 | 风格特点 |
|------|----------|----------|
| `PASTEL_DREAM` | 10 | 柔和的粉彩色调 |
| `NEON_CYBER` | 10 | 海盗版风格霓虹色调 |
| `RETRO_WARM` | 10 | 70年代风格的温暖色调 |
| `OCEAN_DEEP` | 10 | 蓝色渐变色调 |
| `FOREST_MOSS` | 10 | 自然的绿色调 |
| `SUNSET_FIRE` | 10 | 从红色到黄色的渐变色调 |
| `ARCTIC_ICE` | 10 | 冷色调的蓝色与白色 |
| `VINTAGE_ROSE` | 10 | 玫瑰紫色调 |
| `EARTH_CLAY` | 10 | 赤陶色的棕色调 |
| `ELECTRIC_VIOLET` | 10 | 紫色渐变色调 |
