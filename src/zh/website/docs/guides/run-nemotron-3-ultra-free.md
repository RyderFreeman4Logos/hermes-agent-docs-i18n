---
sidebar_position: 0
title: "Run Nemotron 3 Ultra free in Hermes Agent"
description: "Try NVIDIA Nemotron 3 Ultra on Nous Portal — free June 4–18 — with day 0 support in Hermes Agent"
---

# 在 Hermes Agent 中免费运行 Nemotron 3 Ultra

Nous Research 已加入由多家顶尖 AI 实验室组成的 **Nemotron 联盟**，该联盟与 **NVIDIA** 携手致力于推进开源基础模型的发展。为庆祝这一成就，我们与 **Nebius** 合作，在 [Nous Portal](https://portal.nousresearch.com) 上提供 **Nemotron 3 Ultra** 的免费试用服务，时长为两周（**6月4日 – 6月18日**）。请按照以下步骤立即在您的 Hermes Agent 中体验该模型。

:::info 限时优惠
`nvidia/nemotron-3-ultra:free` 版本仅在 **6月4日至6月18日**期间提供。正是 `:free` 标签让它属于免费套餐——请务必选择此版本。
:::

根据您的需求选择合适的安装方式。**桌面应用**最为简单——无需终端即可使用。如果您习惯使用终端，下方也提供了**命令行**安装选项。

## 方案 A — 桌面应用（推荐）

这是最简单的途径：只需一键安装，随后通过引导式操作完成设置，完全不需要终端。

### 1. 下载并安装

从此处下载适用于 macOS 或 Windows 的 **Hermes Desktop 安装程序**：[https://hermes-agent.nousresearch.com/](https://hermes-agent.nousresearch.com/)，然后打开它。首次启动时，系统会自动完成设置（通常不到一分钟）。

### 2. 连接 Nous Portal

打开应用后，您会看到“让我们帮您完成设置”的界面。点击标有 **推荐** 字样的 **Nous Portal**。您的浏览器将会打开——请创建一个 [Nous Portal](https://portal.nousresearch.com) 账户（或登录现有账户），选择 **免费** 套餐，并授权 Hermes。应用会自动建立连接。

### 3. 选择免费的 Nemotron 3 Ultra 模型

连接成功后，应用会显示一张 **默认模型** 卡片。点击 **更改**，搜索 **nemotron 3 ultra**，然后选择标记有 **免费套餐** 的版本即可：

```
nvidia/nemotron-3-ultra:free
```

`:free` 标签正是使其保持免费 tier 的关键——请选择该版本。

### 4. 开始聊天

点击 **Start chatting** 即可。就这样——您已能免费与 Nemotron 3 Ultra 进行对话了。

## 选项 B — 命令行

更喜欢终端界面？

### 1. 安装 Hermes Agent

在 macOS/Linux/WSL2/Android 系统上，运行相应命令即可。

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

在 Windows 系统上，请运行：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

希望先查看代码吗？可以下载 [`install.sh`](https://hermes-agent.nousresearch.com/install.sh) 文件，仔细检查后再执行它。

执行完成后，请重新加载您的 Shell 环境：

```bash
source ~/.bashrc   # or source ~/.zshrc
```

### 2. 执行快速设置

```bash
hermes setup
```

选择**快速设置**。Hermes会打开一个浏览器标签页，并等待您完成后续步骤。

### 3. 创建 Nous Portal 账户

在浏览器中创建一个 [Nous Portal](https://portal.nousresearch.com) 账户（或登录），然后选择**免费**套餐。

### 4. 连接您的账户

当系统提示将您的账户连接到 Hermes Agent 时，点击**连接**。账户成功关联后您会看到确认信息。

### 5. 选择免费的 Nemotron 3 Ultra 模型

返回终端界面。在模型列表中选择相应的模型：

```
nvidia/nemotron-3-ultra:free
```

`:free` 标签正是使其保持在免费级别的关键，因此请务必选择该版本。

### 6. 开始聊天

完成剩余的快速设置提示后，再运行以下命令：

```bash
hermes
```

就这样——您现在正在使用免费的 Nemotron 3 Ultra。

## 后续切换使用

已经配置了其他模型？

- **桌面应用**：打开模型选择器，搜索 **nemotron 3 ultra**，然后选择 **免费版**。
- **CLI / TUI**：可在会话中随时通过 `/model nvidia/nemotron-3-ultra:free` 进行切换，或运行 `/model` 打开选择器并从列表中挑选。

## 故障排除

- **列表中看不到该模型？** 请确认已完成与 Nous Portal 的连接，并且当前使用的是 **免费计划**。在 CLI 中，执行 `hermes portal info` 可确认您已登录且数据正通过 Nous 传输。
- **选错了版本？** 请重新选择 `nvidia/nemotron-3-ultra:free`——必须加上 `:free` 后缀才能保持免费使用。
- **浏览器无法打开 / 您在远程主机上（CLI环境）？** 请参阅 [通过 SSH/远程主机进行 OAuth 认证](/guides/oauth-over-ssh)，了解端口转发及手动粘贴的解决方案。

## 相关内容

- **[桌面应用](/user-guide/desktop)** —— 原生的一键式应用（支持 macOS、Windows、Linux）
- **[通过 Nous Portal 运行 Hermes Agent](/guides/run-hermes-with-nous-portal)** —— 完整的 Portal 使用指南：模型管理、工具网关及验证流程
- **[Nous Portal 集成](/integrations/nous-portal)** —— 订阅方案包含的功能
- **[快速入门](/getting-started/quickstart)** —— 5分钟内完成安装并开始使用
