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

安装程序是手动构建并上传到 GitHub Releases 的。当环境中存在相应的凭据（macOS 为 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 为 `WIN_CSC_*`）时，macOS/Windows 版本的签名与公证操作会自动完成。

### 工作原理

该打包应用包含了 Electron 框架以及基于原生 React 开发的聊天界面。首次启动时，它会将 Hermes Agent 运行时安装到 `HERMES_HOME` 目录中（即 macOS 系统的 `~/.hermes`，Windows 系统的 `%LOCALAPPDATA%\hermes`）——这一路径与 CLI 安装所使用的路径相同，因此两者可以互相替代。后端检测会首先优先查找 `HERMES_DESKTOP_HERMES_ROOT` 指定的路径，其次是已完成的管理式安装路径，接着是 `PATH` 环境变量中可找到的 `hermes` 命令（除非设置了 `HERMES_DESKTOP_IGNORE_EXISTING=1`），最后则是为打包工具或故障排查而设置的显式 `HERMES_DESKTOP_HERMES` 命令覆盖值。前端界面（位于 `src/` 目录中的 React 组件）通过 `tui_gateway`/dashboard API 与 `hermes dashboard` 后端进行通信，它复用已安装的 Agent 运行时，而非直接嵌入 `hermes --tui` 命令。与安装、后端检测及自动更新相关的逻辑均存在于 `electron/main.cjs` 文件中。

### 验证步骤

在提交 Pull Request 之前请先运行此验证步骤（虽然代码检查工具可能会显示一些现有的警告，但程序本身应能正常退出）：

```bash
npm run fix
npm run typecheck
npm run lint
npm run test:desktop:all
```

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
