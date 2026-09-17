# Hermes Desktop ☤

<p align="center">
  <a href="https://github.com/NousResearch/hermes-agent/releases"><img src="https://img.shields.io/badge/Download-macOS%20%C2%B7%20Windows%20%C2%B7%20Linux-FFD700?style=for-the-badge" alt="下载"></a>
  <a href="https://hermes-agent.nousresearch.com/docs/"><img src="https://img.shields.io/badge/Docs-hermes--agent.nousresearch.com-FFD700?style=for-the-badge" alt="文档"></a>
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord社区"></a>
  <a href="https://github.com/NousResearch/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="许可证：MIT协议"></a>
</p>

**这是专为 [Hermes Agent](../../README.md) 打造的原生桌面应用——由 [Nous Research](https://nousresearch.com) 开发的具备自我进化能力的 AI 智能体。** 它拥有与命令行界面及网关版本相同的智能体能力、技能和记忆功能，但以更加精致的原生窗口形式呈现：支持实时聊天、工具输出流式显示、并列预览、文件浏览器、语音交互以及设置功能，无需终端即可使用。该应用现已在 **macOS、Windows 和 Linux** 系统上推出。

<table>
<tr><td><b>与完整智能体对话</b></td><td>支持实时响应流、工具运行状态展示、结构化工具摘要，以及与其他Hermes界面相同的对话历史记录。</td></tr>
<tr><td><b>并排预览功能</b></td><td>在继续对话的同时，可在右侧面板中查看网页、文件及工具输出结果。</td></tr>
<tr><td><b>文件浏览器</b></td><td>无需离开应用即可浏览和预览当前工作目录中的内容。</td></tr>
<tr><td><b>语音功能</b></td><td>可直接与Hermes进行语音交流并获取回应。</td></tr>
<tr><td><b>设置与引导</b></td><td>通过直观的界面管理各种服务提供者、模型、工具及认证信息。首次使用只需几秒钟即可开始发送消息。</td></tr>
<tr><td><b>自动更新</b></td><td>内置更新功能可自动获取最新版本的智能体，并在本地完成应用重建。</td></tr>
</table>

---

## 安装

### 使用Hermes进行安装（推荐）

已拥有Hermes CLI？只需运行以下命令即可：

```bash
hermes desktop
```

它会在您现有的安装基础上构建并启动 GUI——配置、密钥、会话以及智能体技能均保持不变。如果 Hermes Desktop 无法找到可用的运行时环境或已保存的远程连接，首次启动时会引导您连接到现有的 Hermes 网关或在本地安装 Hermes。随后，系统会逐步指导您选择服务提供商和模型。

### 预构建安装程序

预构建安装程序是通过 [Hermes Desktop 官网](https://hermes-agent.nousresearch.com/) 构建并分发的。

---

## 更新

该应用会在后台检查更新情况，一旦有可用更新便会提供一键更新功能。您也可以随时通过 CLI 进行更新：

```bash
hermes update
```

## 系统要求

安装程序会为您处理所有相关事项（Python 3.11+、便携版 Git 以及 ripgrep）。  

## 开发指南

想要直接修改应用程序代码？只需从仓库根目录安装一次开发依赖，然后在此目录下启动开发服务器即可：

```bash
npm install          # from repo root — links apps/desktop, web, apps/shared
cd apps/desktop
npm run dev          # Vite renderer + Electron, which boots the Python backend
```

可将该应用指向特定的源代码检查点，或将其隔离在沙箱环境中，从而与真实的配置环境分开。

```bash
# throwaway HERMES_HOME, separate Electron userData, distinct app name to avoid the single-instance lock
../scripts/dev-sandbox.sh npm run dev
HERMES_DESKTOP_HERMES_ROOT=/path/to/clone npm run dev
HERMES_HOME=/tmp/throwaway npm run dev
npm run dev:fake-boot   # exercise the startup overlay with deterministic delays
```

### 构建安装程序

```bash
npm run dist:mac     # DMG + zip
npm run dist:win     # NSIS + MSI
npm run dist:linux   # AppImage + deb + rpm
npm run pack         # unpacked app under release/ (no installer)
```

安装程序是手动构建并上传到 GitHub Releases 页面的。当环境中存在相应的凭据（macOS 下为 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 下为 `WIN_CSC_*`）时，macOS/Windows 版本的签名与公证流程会自动完成。

### 工作原理

该打包应用包含了 Electron 应用壳层以及原生 React 构建的聊天界面。首次启动时，它会按照与 CLI 安装相同的流程，将 Hermes Agent 运行时安装到 `HERMES_HOME` 目录中（macOS 下为 `~/.hermes`，Windows 下为 `%LOCALAPPDATA%\hermes`）。

该应用由三个独立模块组成：

- **Electron** 模块负责查找并验证可运行的后端程序，掌控原生文件系统、Git 操作及窗口管理功能，并提供一个受限的预加载桥接接口。
- **React** 模块负责处理桌面界面路由、面板布局、交互状态以及 `@assistant-ui/react` 相关的对话记录功能。
- **Hermes Agent** 以无界面的 `hermes serve` 进程形式运行，提供 `tui_gateway` JSON-RPC/WebSocket 接口。前端渲染进程则通过 [`apps/shared`](../shared/) 进行连接，该路径同样被浏览器控制台所使用。

后端程序的查找遵循以下层级顺序：

1. `HERMES_DESKTOP_HERMES_ROOT`
2. 开发阶段当前检出的代码版本
3. 已完成的托管安装包
4. `HERMES_DESKTOP_HERMES`，或 `PATH` 环境变量中指定的 `hermes` 命令
5. 能够导入 Hermes 运行时的系统 Python 版本
6. 首次启动时使用的引导安装程序
在投入使用之前，候选组件会经过严格检测；仅靠现有的桥接模块或解释器是远远不够的。若运行时版本早于 `serve`，系统则会回退到无界面模式，通过 `dashboard --no-open` 命令启动。这种机制仅旨在确保后端命令的兼容性，并不会实际加载或嵌入仪表板用户界面。

Electron 框架的调度入口点为 `electron/main.ts`；而纯粹的解析逻辑、组件检测功能、安全加固措施以及平台策略则分别存在于该文件旁的专用模块中。渲染层代码位于 `src/` 目录下，共享数据结构存放在 `src/store` 中，而传输层及原生适配器则位于 `src/lib` 目录中。

在修改应用程序之前，请先阅读以下文档：
- [`AGENTS.md`](./AGENTS.md)：介绍架构设计、状态管理机制、解析/回退策略、传输方式、性能优化以及测试规范。
- [`DESIGN.md`](./DESIGN.md)：阐述视觉系统、信息架构、动画效果、直接操作功能以及键盘交互行为。

### 连接、项目与切换

桌面端支持托管式本地后端、显式的远程网关以及 Hermes Cloud 连接。无论是远程模式还是云模式，其使用的远程功能路径是相同的；不同之处仅在于身份验证和资源发现机制，而非渲染层的功能模型。

当不存在可用的本地运行时环境或已保存的远程连接时，首次启动时会先出现**连接到现有Hermes实例**的选项，之后才会开始安装本地程序。Desktop会探测网关以确定是否需要令牌或OAuth认证，并要求完成HTTP和WebSocket连接的测试，最终使用与设置界面中相同的加密配置来保存该连接。后续启动时，若已有已保存的远程连接，则无需再选择此选项。常规版本的Desktop仍然包含本地安装选项；但这其实是一种远程运行模式，而非独立的仅客户端应用程序。

在远程模式下，网关主机即为执行边界：所有代理工具、终端命令以及文件操作都将在远程Hermes主机上执行，而非在显示Desktop用户界面的电脑上运行。

位于访问代理之后的远程网关可能要求在每个HTTP和WebSocket请求中添加额外的头部信息。您可以在“设置”→“连接”（额外网关头部）中为每个连接单独配置这些信息，或者直接在Desktop的Electron `userData/connection.json`文件中的remote字段里添加一个`headers`对象：

```json
{
  "mode": "remote",
  "remote": {
    "url": "https://hermes.example.com",
    "authMode": "token",
    "token": { "encoding": "safeStorage", "value": "..." },
    "headers": {
      "CF-Access-Client-Id": { "encoding": "safeStorage", "value": "..." },
      "CF-Access-Client-Secret": { "encoding": "safeStorage", "value": "..." }
    }
  }
}
```

`profiles[name].headers` 下的各配置文件对应的远程请求头均采用相同的格式。桌面端仅将这些请求头应用于匹配的远程网关请求，将 `https` 和 `wss` 视为 WebSocket 升级时的同一网关来源，并忽略由传输层或 Hermes 管理的请求头，如 `Authorization`、`Cookie`、`Host`、`Origin`、`Referer` 以及 `X-Hermes-Session-Token`。

项目是对工作空间的抽象概念。一个项目可以包含多个文件夹、仓库、工作树和会话；除非用户选择某个项目或配置默认项目目录，否则新建的聊天窗口将保持独立状态。建议使用项目界面，而非为每个会话单独添加文件夹选择流程。

切换配置文件或连接模式属于温和的工作空间切换方式，而非彻底重启。在清除与网关关联的纳米存储、使基于查询的数据失效以及用新连接重新填充结构框架的同时，Shell 和当前管理层仍会保持运行状态。这样可避免上一个网关的记录或转录内容混入下一个网关。切换仅会改变当前显示的内容和请求路径：它不会取消对话轮次或停止后台服务，同时保留的背景套接字会继续接收正在运行的任务发送的事件。

### 验证

在提交 Pull Request 之前运行此命令（虽然代码检查工具可能会显示已有警告，但该命令本身应能正常退出）：

```bash
npm run fix
npm run typecheck
npm run lint
npm run test:ui
npm run test:desktop:platforms
```

如需执行安装、启动、更新、打包或其他与发布流程相关的操作，请运行 `npm run test:desktop:all`。

### 故障排除

启动日志会保存在 `HERMES_HOME/logs/desktop.log` 文件中（其中包含后端输出信息以及最近的 Python 错误追踪信息）——如果应用程序报告启动失败，建议首先查看该文件。

**macOS / Linux：**

```bash
# Force a clean first-launch setup
rm "$HOME/.hermes/hermes-agent/.hermes-bootstrap-complete"
# Rebuild a broken Python venv
rm -rf "$HOME/.hermes/hermes-agent/venv"
# Reset a stuck macOS microphone prompt (macOS only)
tccutil reset Microphone com.nousresearch.hermes
```

**Windows（PowerShell）：**

```powershell
# Force a clean first-launch setup
Remove-Item "$env:LOCALAPPDATA\hermes\hermes-agent\.hermes-bootstrap-complete"
# Rebuild a broken Python venv
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes\hermes-agent\venv"
```

> 在 Windows 系统上，Hermes 的默认安装路径为 `%LOCALAPPDATA%\hermes`。如果您已更改了该路径，请设置 `HERMES_HOME` 环境变量。

---

## 社区

- 💬 [Discord](https://discord.gg/NousResearch)
- 📖 [文档](https://hermes-agent.nousresearch.com/docs/)
- 🐛 [问题反馈](https://github.com/NousResearch/hermes-agent/issues)

---

## 许可证

采用 MIT 许可证 — 详情请参见 [LICENSE](../../LICENSE)。

由 [Nous Research](https://nousresearch.com) 开发。
