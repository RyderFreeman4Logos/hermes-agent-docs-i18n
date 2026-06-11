# 故障排除

## “未找到 `HeadlessExperimental.beginFrame`”（首要检查项）

**症状：** 运行 `npx hyperframes render` 时出现以下错误：

```
✗ Render failed
Protocol error (HeadlessExperimental.beginFrame):
'HeadlessExperimental.beginFrame' wasn't found
```

**原因：** Chromium 147 及更高版本已移除 `HeadlessExperimental.beginFrame` CDP 命令。这会影响那些将现代版 Chromium 作为系统浏览器使用的沙箱环境（例如 OpenClaw 以及某些容器化的 Agent 主机）。详情请参阅 [hyperframes#294](https://github.com/heygen-com/hyperframes/issues/294)。

**永久性解决方案（推荐）：** 进行升级。

```bash
npx hyperframes upgrade -y
# or
npm install -g hyperframes@latest
```

`hyperframes >= 0.4.2` 版本能够自动检测所使用的浏览器是否支持 `beginFrame` 功能（通过检查二进制路径中是否存在 `chrome-headless-shell` 来判断），若不支持则自动切换为截图模式。2026年3月发布的 [`4c72ba4`](https://github.com/heygen-com/hyperframes/commit/4c72ba4a36ec2bd6733f7b9cb2a9e63f9fb234b9) 代码提交实现了这一自动检测功能。

**临时解决方案（适用于无法升级的情况）：**

```bash
export PRODUCER_FORCE_SCREENSHOT=true
npx hyperframes render
```

无论使用何种二进制文件，此设置都会强制启用截图模式。虽然截图模式的处理速度稍慢，但输出效果与正常模式完全一致。

**修复方案（推荐）：** 安装 `chrome-headless-shell`，这样引擎便可走更高效的 BeginFrame 路径：

```bash
npx puppeteer browsers install chrome-headless-shell
# or let the CLI do it
npx hyperframes browser --install
```

`scripts/setup.sh` 会自动执行该操作。

## `npx hyperframes render` 停滞120秒后超时

**原因：** 实际使用的浏览器为系统自带的 Chrome（例如 `/usr/bin/google-chrome`），它不支持 BeginFrame 接口，而旧版本的 `hyperframes` 也未能自动检测到这一点。

**解决方案：**
1. 查看正在使用的二进制文件：`npx hyperframes browser --path`
2. 如果是系统 Chrome，可采取以下任一措施：
   - 安装 `chrome-headless-shell`：`npx hyperframes browser --install`，或者
   - 设置临时绕过选项：`export PRODUCER_FORCE_SCREENSHOT=true`，或者
   - 升级版本：`npx hyperframes upgrade -y`

## `ffmpeg: command not found`

请通过系统包管理器安装 FFmpeg：

| 操作系统/发行版 | 安装命令                             |
| --------------- | ----------------------------------- |
| Ubuntu / Debian | `sudo apt-get install -y ffmpeg`    |
| Fedora / RHEL   | `sudo dnf install -y ffmpeg`        |
| Arch            | `sudo pacman -S ffmpeg`             |
| macOS           | `brew install ffmpeg`               |
| Windows         | `winget install Gyan.FFmpeg`        |

安装完成后请验证：`ffmpeg -version`。

## `Node version X is not supported`

HyperFrames 要求使用 Node.js 22 及以上版本。可通过 `node --version` 查看当前版本。

- **nvm：** `nvm install 22 && nvm use 22`
- **Homebrew（macOS）：** `brew install node@22 && brew link --overwrite node@22`
- **apt：** 可参考 [nodesource](https://github.com/nodesource/distributions) 获取 Node 22 LTS 安装方式。

## 渲染过程中出现 `ENOSPC: no space left on device` 或内存不足导致进程被终止

渲染任务对内存和磁盘资源消耗较大。最低要求如下：

- **RAM：** 需至少4 GB空闲内存（若需60fps帧率或使用 `--quality high` 参数，建议至少8 GB）。
- **磁盘：** 需至少2 GB空闲空间——渲染过程中帧数据会暂存于 `/tmp` 目录。

**缓解措施：**
- 降低质量：使用 `--quality draft`。
- 降低帧率：使用 `--fps 24`。
- 减少工作线程数量：使用 `--workers 1`。
- 将 `TMPDIR` 设置为空间更大的磁盘分区：`export TMPDIR=/mnt/scratch`。

## 代码检查通过，但渲染结果为空或全是黑屏

请查看 `preview` 模式下的浏览器控制台，常见问题包括：
- 使用了错误的键来注册时间轴（例如使用了 `__timelines["typo"]` 而非 `__timelines["root"]`）。
- 根级合成内容被包裹在 `<template>` 标签中（实际上只有子合成内容才需使用该标签）。
- 有脚本标签未能成功加载——可查看预览模式下的网络标签页。

运行 `npx hyperframes lint --verbose` 可查看详细的问题提示。

## `hyperframes validate` 报出对比度警告

```
⚠ WCAG AA contrast warnings (3):
  · .subtitle "secondary text" — 2.67:1 (need 4.5:1, t=5.3s)
```

- **深色背景**：将颜色亮度提高，直至对比度达到 4.5:1（普通文本）或 3:1（大号文本——字体大小为 24px 及以上或加粗后为 19px 及以上）。  
- **浅色背景**：降低颜色亮度。  
- 需在现有配色方案范围内调整，不得自行创建新颜色，仅可修改现有颜色。  
- 若需快速迭代，可使用 `--no-contrast` 临时跳过对比度检查，但在最终交付前必须取消该选项。  

## “编译器不支持字体族 ‘X’”

编译器内置了一组经过筛选的、兼容网页且为开源的字体。如果遇到不支持的字体，可采取以下任一措施：  
- 更换为警告信息中推荐的可用字体；  
- 通过 `@font-face` 指向项目目录中的 `.woff2` 文件来注册自定义字体（编译器会嵌入所引用的 `@font-face` 文件）。  

## 视频播放时静音或无声音

请检查以下事项：  
- `<video>` 元素是否设置了 `muted playsinline` 属性（这是浏览器自动播放策略的强制要求）；  
- 音频是否通过独立的 `<audio>` 元素呈现，而非嵌入在视频元素中；  
- 是否设置了音频的 `data-volume` 属性（默认值为 1）；  
- 音频文件是否位于正确路径——组件会根据其所在目录相对路径进行加载。  

## 在使用无根 Docker 的 Linux 环境下 Docker 渲染失败

请添加 `--privileged` 参数，或传递 `--cap-add=SYS_ADMIN` 参数：

```bash
npx hyperframes render --docker --docker-args "--cap-add=SYS_ADMIN"
```

无头浏览器在运行沙箱环境时需要命名空间权限。  

## 错误报告

请附上 `npx hyperframes info` 的输出结果以及完整的错误日志。相关报告可提交至 [github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/issues) 。
