---
title: "Songsee — Audio spectrograms/features (mel, chroma, MFCC) via CLI"
sidebar_label: "Songsee"
description: "Audio spectrograms/features (mel, chroma, MFCC) via CLI"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Songsee

通过 CLI 工具生成音频频谱图及各种音频特征（如梅尔频谱、色度图、MFCC 等）。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/media/songsee` |
| 版本 | `1.0.0` |
| 开发者 | 社区用户 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `音频`、`可视化`、`频谱图`、`音乐`、`分析` |

## 参考：完整的 SKILL.md 文件

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当技能处于激活状态时，智能体所看到的指令即为此内容。
:::

# songsee

从音频文件中生成频谱图及多面板音频特征可视化图表。

## 先决条件

需要安装 [Go](https://go.dev/doc/install)：
```bash
go install github.com/steipete/songsee/cmd/songsee@latest
```

可选：对于 WAV/MP3 以外的格式，可使用 `ffmpeg` 工具。

## 快速入门

对完整的输入内容进行翻译，切勿提前终止。

```bash
# Basic spectrogram
songsee track.mp3

# Save to specific file
songsee track.mp3 -o spectrogram.png

# Multi-panel visualization grid
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux

# Time slice (start at 12.5s, 8s duration)
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg

# From stdin
cat track.mp3 | songsee - --format png -o out.png
```

## 可视化类型

使用带逗号分隔值的 `--viz` 参数指定：

| 类型 | 描述 |
|------|-------------|
| `spectrogram` | 标准频率频谱图 |
| `mel` | Mel刻度频谱图 |
| `chroma` | 音高类别分布图 |
| `hpss` | 和声/打击乐分离图 |
| `selfsim` | 自相似性矩阵图 |
| `loudness` | 随时间变化的响度图 |
| `tempogram` | 节拍估计图 |
| `mfcc` | Mel频率倒谱系数图 |
| `flux` | 频谱通量图（用于起始点检测） |

多个 `--viz` 类型可合并显示在一张图像的网格中。

## 常用参数

| 参数 | 描述 |
|------|-------------|
| `--viz` | 可视化类型（以逗号分隔） |
| `--style` | 颜色方案：`classic`、`magma`、`inferno`、`viridis`、`gray` |
| `--width` / `--height` | 输出图像的尺寸 |
| `--window` / `--hop` | FFT窗口大小和步长 |
| `--min-freq` / `--max-freq` | 频率范围过滤 |
| `--start` / `--duration` | 音频的时间片段 |
| `--format` | 输出格式：`jpg` 或 `png` |
| `-o` | 输出文件路径 |

## 备注

- WAV和MP3格式可直接解码；其他格式需要借助`ffmpeg`。
- 可使用`vision_analyze`工具查看输出图像，以实现自动化音频分析。
- 该功能适用于比较不同音频输出结果、调试合成过程，或记录音频处理流程。
