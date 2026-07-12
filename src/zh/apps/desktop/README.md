# Hermes Desktop ☤

<p align="center">
  <a href="https://github.com/NousResearch/hermes-agent/releases"><img src="https://img.shields.io/badge/Download-macOS%20%C2%B7%20Windows%20%C2%B7%20Linux-FFD700?style=for-the-badge" alt="下载"></a>
  <a href="https://hermes-agent.nousresearch.com/docs/"><img src="https://img.shields.io/badge/文档-hermes--agent.nousresearch.com-FFD700?style=for-the-badge" alt="文档"></a>
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://github.com/NousResearch/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/许可证-MIT-green?style=for-the-badge" alt="许可证：MIT"></a>
</p>

**这是 [Hermes Agent](../../README.md) 的原生桌面应用程序——由 [Nous Research](https://nousresearch.com) 开发的具备自我提升能力的 AI 智能体。** 它拥有与 CLI 版本及网关版本相同的智能体能力、技能和记忆功能，但以精美的原生窗口形式呈现——支持实时聊天、工具输出流式展示、并排预览、文件浏览器、语音交互以及设置功能，无需终端即可使用。该应用适用于 **macOS、Windows 和 Linux** 系统。

<table>
<tr><td><b>与完整智能体进行聊天</b></td><td>可查看实时响应、工具运行状态、结构化的工具总结，以及与其他 Hermes 使用界面相同的对话历史记录。</td></tr>
<tr><td><b>并排预览功能</b></td><td>在继续聊天的同时，可在右侧面板中查看网页、文件和工具的输出结果。</td></tr>
<tr><td><b>文件浏览器</b></td><td>无需离开应用程序即可浏览和工作目录中的文件，并进行预览。</td></tr>
<tr><td><b>语音交互</b></td><td>可直接与 Hermes 进行语音对话。</td></tr>
<tr><td><b>设置与引导</b></td><td>可通过直观的界面管理提供商、模型、工具及凭证。首次使用时，只需几秒钟即可完成设置并开始发送消息。</td></tr>
<tr><td><b>自动更新</b></td><td>内置更新功能可自动获取最新版本的智能体，并在本地完成应用重新构建。</td></tr>
</table>

---

## 安装

### 使用 Hermes 安装（推荐）

已拥有 Hermes CLI？只需运行：

```bash
hermes desktop
```

它会在您现有的安装基础上构建并启动 GUI——配置、密钥、会话以及技能均保持不变。首次启动时，Hermes 会引导您选择提供商和模型，无需再进行其他配置。

### 预制安装程序

预制安装程序是通过 [Hermes Desktop 网站](https://hermes-agent.nousresearch.com/) 构建并分发的。

---

## 更新

该应用会在后台检查更新，一旦有新版本可用便会提供一键更新功能。您也可以随时通过 CLI 进行更新：

```bash
hermes update
```

## 系统要求

安装程序会为您处理所有必要条件（Python 3.11+、可移植版 Git 以及 ripgrep）。  

## 开发指南

想要直接修改应用程序代码？只需从仓库根目录安装一次开发依赖，然后在此目录下启动开发服务器即可：

```bash
npm install          # from repo root — links apps/desktop, web, apps/shared
cd apps/desktop
npm run dev          # Vite renderer + Electron, which boots the Python backend
```

可将该应用指向特定的源代码检出位置，或将其隔离在沙箱环境中，从而与真实的配置环境分开。

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

安装程序需手动构建并上传至 GitHub Releases。当环境中存在相应的凭证（macOS 为 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 为 `WIN_CSC_*`）时， macOS/Windows 版本的签名与公证操作会自动完成。

### 工作原理

该打包应用包含了 Electron shell 以及原生 React 构建的聊天界面。首次启动时，它会按照与 CLI 安装相同的流程，将 Hermes Agent 运行时安装到 `HERMES_HOME` 目录中（macOS 下为 `~/.hermes`，Windows 下为 `%LOCALAPPDATA%\hermes`）。

该应用由三个独立模块构成：

- **Electron** 模块负责查找并验证可运行的后端，掌控原生文件系统、Git 操作及窗口管理功能，并提供一个受限的预加载桥接接口。
- **React** 模块负责处理桌面路由、界面分区、交互状态以及 `@assistant-ui/react` 相关的对话记录。
- **Hermes Agent** 以无头模式作为 `hermes serve` 进程运行，提供 `tui_gateway` JSON-RPC/WebSocket API 接口。前端渲染层通过 [`apps/shared`](../shared/) 与该后端连接，该路径同样被浏览器控制台所使用。

后端查找遵循以下优先级顺序：

1. `HERMES_DESKTOP_HERMES_ROOT`
2. 开发时的当前代码检出版本
3. 已完成的托管式安装版本
4. `HERMES_DESKTOP_HERMES` 或 `PATH` 环境变量中的 `hermes` 命令
5. 能够导入 Hermes 运行时的系统 Python 版本
6. 首次启动时使用的引导安装程序

在正式使用前，系统会逐一检测这些候选后端；仅凭现有的模拟模块或解释器是不够的。若某运行时版本早于 `serve` 版本，则会回退到无头模式的 `dashboard --no-open` 运行方式。此功能仅保障后端命令的兼容性，不会启动或嵌入控制台界面。

Electron 层的协调入口为 `electron/main.ts`；而纯粹的查找逻辑、检测机制、安全加固措施以及平台相关策略则分别位于其旁的专用模块中。前端渲染层代码存放在 `src/` 目录下，共享的底层组件位于 `src/store`，传输层及原生适配器则位于 `src/lib`。

在修改应用代码之前，请先阅读以下文档：

- [`AGENTS.md`](./AGENTS.md)：涵盖架构设计、状态管理机制、查找逻辑与回退策略、传输协议、性能优化以及测试规范。
- [`DESIGN.md`](./DESIGN.md)：涉及视觉系统设计、信息架构、动画效果、直接操作交互以及键盘操作规则。

### 连接、项目与模式切换

桌面端支持托管式本地后端、显式的远程网关以及 Hermes Cloud 连接。远程模式和云模式使用相同的远程功能路径，二者仅在认证机制和发现流程上存在差异，前端功能模型保持一致。

“项目”是工作空间的抽象概念。一个项目可以包含多个文件夹、代码仓库、工作树以及会话记录；除非用户选择某个项目或设置默认项目目录，否则新建的空白聊天窗口将处于独立状态。建议使用项目管理界面，而非为每个会话单独添加文件夹选择步骤。

切换配置文件或连接模式属于温和的工作空间切换方式，无需像完全重启那样重新加载所有组件。在清除与当前网关关联的纳米存储数据、使基于查询的数据失效，并用新连接的数据重新填充结构框架的同时，Shell 界面及当前管理层会继续保持运行状态。这样一来，就能避免上一个网关中的记录或对话内容泄露到下一个网关中。

### 验证

在提交 Pull Request 之前请先运行此验证步骤（虽然代码检查工具可能会显示一些已存在的警告，但程序本身必须能正常退出）：

```bash
npm run fix
npm run typecheck
npm run lint
npm run test:ui
npm run test:desktop:platforms
```

如需执行安装、启动、更新、打包或其他与发布流程相关的操作，请运行 `npm run test:desktop:all`。

### 故障排除

启动日志会保存在 `HERMES_HOME/logs/desktop.log` 文件中（其中包含后端输出信息及最近的 Python 错误追踪信息）——若应用程序报告启动失败，建议首先查看该文件。

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

> 在 Windows 系统上，Hermes 的默认安装路径为 `%LOCALAPPDATA%\hermes`。如果您更改了该路径，请设置 `HERMES_HOME` 环境变量。

---

## 社区

- 💬 [Discord](https://discord.gg/NousResearch)
- 📖 [文档](https://hermes-agent.nousresearch.com/docs/)
- 🐛 [问题反馈](https://github.com/NousResearch/hermes-agent/issues)

---

## 许可证

采用 MIT 许可证 — 详情请参阅 [LICENSE](../../LICENSE)。

由 [Nous Research](https://nousresearch.com) 开发。
