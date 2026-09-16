# 故障排除

## “未找到 `HeadlessExperimental.beginFrame`”（首要检查项）

**症状：** 运行 `npx hyperframes render` 时出现以下错误：

```
✗ Render failed
Protocol error (HeadlessExperimental.beginFrame):
'HeadlessExperimental.beginFrame' wasn't found
```

**原因：** Chromium 147 及更高版本已移除 `HeadlessExperimental.beginFrame` CDP 命令。这会影响那些将现代版 Chromium 作为系统浏览器使用的沙箱环境（例如 OpenClaw、某些容器化的 Agent 主机）。详情请参见 [hyperframes#294](https://github.com/heygen-com/hyperframes/issues/294)。

**永久性解决方案（推荐）：** 进行升级。

```bash
npx hyperframes upgrade -y
# or
npm install -g hyperframes@latest
```

`hyperframes >= 0.4.2` 版本能够自动检测所使用的浏览器是否支持 `beginFrame` 功能（通过检查二进制路径中是否存在 `chrome-headless-shell` 来判断），若不支持则自动切换为截图捕获模式。2026年3月发布的 [`4c72ba4`](https://github.com/heygen-com/hyperframes/commit/4c72ba4a36ec2bd6733f7b9cb2a9e63f9fb234b9) 任务便实现了这一自动检测功能。

**临时解决方案（适用于无法升级的情况）：**

```bash
export PRODUCER_FORCE_SCREENSHOT=true
npx hyperframes render
```

无论使用何种二进制文件，此设置都会强制启用截图模式。虽然截图模式的处理速度稍慢，但输出效果与正常模式完全一致。

**修复方案（推荐）：** 安装 `chrome-headless-shell`，以便引擎能够通过更高效的 BeginFrame 路径来工作：

```bash
npx puppeteer browsers install chrome-headless-shell
# or let the CLI do it
npx hyperframes browser --install
```

`scripts/setup.sh` 会自动执行该操作。

## `npx hyperframes render` 停滞120秒后超时

**原因：** 实际使用的浏览器为系统自带的 Chrome（例如 `/usr/bin/google-chrome`），它不支持 BeginFrame 接口，而旧版本的 `hyperframes` 也未能自动检测到这一点。

**解决方案：**
1. 查看当前使用的二进制文件：`npx hyperframes browser --path`
2. 如果是系统 Chrome，则可以：
   - 安装 `chrome-headless-shell`：`npx hyperframes browser --install`，或者
   - 设置临时绕过方案：`export PRODUCER_FORCE_SCREENSHOT=true`，或者
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

HyperFrames 要求使用 Node.js 版本 >= 22。可通过 `node --version` 查看当前版本。

- **nvm：** `nvm install 22 && nvm use 22`
- **Homebrew（macOS）：** `brew install node@22 && brew link --overwrite node@22`
- **apt：** 可参考 [nodesource](https://github.com/nodesource/distributions) 获取 Node 22 LTS 安装指南。

## 在渲染过程中出现 `ENOSPC: no space left on device` 或内存不足导致的进程终止错误

渲染过程会消耗大量内存和磁盘空间。最低配置要求如下：

- **RAM：** 需预留 4 GB 空闲内存（若需 60fps 渲染或使用 `--quality high` 参数，建议预留 8 GB）。
- **磁盘：** 需预留 2 GB 空闲空间——在捕获视频时，帧数据会暂存于 `/tmp` 目录中。

可采取的优化措施：
- 降低质量：使用 `--quality draft` 参数。
- 降低帧率：使用 `--fps 24` 参数。
- 减少工作进程数量：使用 `--workers 1` 参数。
- 将 `TMPDIR` 设置为磁盘空间更大的路径：`export TMPDIR=/mnt/scratch`。

## Lint 检查通过，但渲染结果为空或全是黑帧

请查看 `preview` 模式下的浏览器控制台，常见原因包括：
- 时间轴使用了错误的键名（例如使用了 `__timelines["typo"]` 而非 `__timelines["root"]`）。
- 根级合成内容被包裹在 `<template>` 标签中（实际上只有子合成内容才需使用该标签）。
- 存在脚本加载失败的情况——可查看 `preview` 模式下的网络标签页。

如需查看详细错误信息，可运行 `npx hyperframes lint --verbose` 命令。

## `hyperframes validate` 报出对比度警告

```
⚠ WCAG AA contrast warnings (3):
  · .subtitle "secondary text" — 2.67:1 (need 4.5:1, t=5.3s)
```

- **深色背景**：将颜色亮度提高，直至对比度达到 4.5:1（普通文本）或 3:1（大号文本——字体大小为 24px 及以上或加粗后为 19px 及以上）。  
- **浅色背景**：降低颜色亮度。  
- 需在现有色彩方案范围内调整，不得自行创建新颜色。  
- 若需快速迭代，可使用 `--no-contrast` 临时跳过对比度检查，但在最终交付前必须取消该选项。  

## “编译器不支持字体系列 ‘X’”

编译器内置了一组经过筛选的、符合网页安全标准且为开源的字体。如果遇到不受支持的字体，可采取以下措施之一：  
- 更换为警告信息中推荐的可用字体；  
- 通过 `@font-face` 注册自定义字体，路径指向项目目录中的 `.woff2` 文件（编译器会嵌入所引用的 `@font-face` 文件）。  

## 视频播放时静音或无声音

请检查以下内容：  
- `<video>` 元素是否设置了 `muted playsinline` 属性（这是浏览器自动播放策略的强制要求）；  
- 音频是否为独立的 `<audio>` 元素，而非嵌入在视频元素中；  
- 是否设置了音频的 `data-volume` 属性（默认值为 1）；  
- 音频文件是否位于正确路径——组件会相对于其所在目录进行加载。  

## 在基于 rootless Docker 的 Linux 环境下 Docker 渲染失败

请添加 `--privileged` 参数，或传递 `--cap-add=SYS_ADMIN` 参数：

```bash
npx hyperframes render --docker --docker-args "--cap-add=SYS_ADMIN"
```

无头浏览器需要命名空间权限才能实现沙箱隔离。

## 由残留的预览工作进程导致的CPU占用过高问题

**症状：** 系统负载平均值持续居高不下；通过 `top` 命令可看到多个 `chrome-headless-shell --type=gpu-process` 进程，每个进程的CPU占用率均在300%以上，并且会在数小时甚至数天内一直处于运行状态，即便此时并未进行任何渲染操作。

**原因：** `npx hyperframes preview` 会启动一个长期运行的服务器，从而使Chrome渲染工作进程持续驻留。在没有真正GPU的系统中（如WSL、容器以及大多数CI环境），每个空闲的工作进程都会回退到软件级WebGL引擎（`swiftshader`），而该引擎的GPU处理线程会持续占用CPU核心。如果某个预览窗口保持打开状态，或者随着时间推移开启了多个预览窗口，这些问题就会叠加在一起。

**诊断方法：**

```bash
pgrep -af chrome-headless-shell        # list the workers + their parent flags
pgrep -af "hyperframes.*preview"       # the preview server(s) holding them open
uptime                                 # confirm elevated load average
```

**修复方法：** 停止预览服务器及其工作进程（详见 [SKILL.md#cleanup](../SKILL.md)）：

```bash
pkill -f "hyperframes.*preview"
pkill -f chrome-headless-shell         # only if no other tool uses it — check pgrep first
```

**注意事项：** 审核完成后切勿让 `preview` 模式继续运行；请使用 `render`（一次性执行且会自动清理）功能来生成输出。在无共享资源或无 GPU 的主机上，建议将 `--workers` 的数值设置得较低。

## 错误报告

请附上 `npx hyperframes info` 的输出结果以及完整的错误日志。可将报告提交至 [github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/issues) 。
