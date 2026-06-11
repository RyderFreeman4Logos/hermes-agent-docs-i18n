---
sidebar_position: 3
title: "Android / Termux"
description: "Run Hermes Agent directly on an Android phone with Termux"
---

# 使用 Termux 在 Android 上运行 Hermes

这是通过 [Termux](https://termux.dev/) 直接在 Android 手机上运行 Hermes Agent 的经过验证的方案。该方案可在手机上提供可正常使用的本地 CLI，同时还包含目前已知可在 Android 上顺利安装的所有核心功能。

## 该验证方案支持哪些功能？

经过测试的 Termux 安装包包含以下功能：
- Hermes CLI
- cron 定时任务支持
- PTY/后台终端支持
- Telegram 网关支持（手动触发/尽力而为式后台运行）
- MCP 支持
- Honcho 内存管理支持
- ACP 支持

具体对应的功能如下：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

## 哪些功能尚未纳入测试范围？

目前仍有部分功能需要桌面/服务器端的依赖项，而这些依赖在 Android 平台上尚未发布，或尚未在手机上经过验证：

- 当前 Android 平台不支持 `.[all]` 选项
- `voice` 额外功能被 `faster-whisper -> ctranslate2` 拦截，且 `ctranslate2` 未提供 Android 版预编译包
- Termux 安装程序会跳过自动浏览器/Playwright 启动流程
- Termux 内部不支持基于 Docker 的终端隔离功能
- Android 系统仍可能暂停 Termux 的后台任务，因此网关数据的持久化属于尽力而为的机制，而非标准的管理服务体验

尽管如此，Hermes 依然可以作为一款专为手机设计的 CLI 智能体正常运行——只是其推荐的移动端安装方案在功能范围上刻意比桌面/服务器端版本更为精简。

---

## 方案一：单行安装程序

Hermes 现已提供兼容 Termux 的安装程序路径：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

在 Termux 环境中，安装程序会自动执行以下操作：
- 使用 `pkg` 命令来安装系统软件包；
- 通过 `python -m venv` 创建虚拟环境；
- 首先尝试使用范围更广的 `.[termux-all]` 插件集，若失败则回退到范围较小的 `.[termux]` 插件集（最后再进行基础安装）——curl 安装工具会自动遵循这一顺序；
- 将 `hermes` 程序链接到 `$PREFIX/bin` 目录中，以确保其始终位于 Termux 的路径搜索范围内；
- 跳过尚未经过测试的浏览器及 WhatsApp 启动程序。

如果您需要具体的命令或想要调试安装失败的问题，请使用下方的手动安装路径。

---

## 方案 2：手动安装（完全明确指定步骤）

### 1. 更新 Termux 并安装系统软件包

```bash
pkg update
pkg install -y git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
```

为何选择这些软件包？
- `python` — 提供运行时环境及虚拟环境支持
- `git` — 用于克隆或更新代码仓库
- `clang`、`rust`、`make`、`pkg-config`、`libffi`、`openssl` — 用于在 Android 上构建部分 Python 依赖项
- `nodejs` — 作为可选的 Node 运行时环境，用于测试核心路径之外的其他功能实验
- `ripgrep` — 快速文件搜索工具
- `ffmpeg` — 用于媒体文件处理及文本转语音操作

### 2. 克隆 Hermes

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

### 3. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
```

对于基于 Rust 和 maturin 开发的包（如 `jiter`），`ANDROID_API_LEVEL` 是一个非常重要的参数。 

### 4. 安装已测试过的 Termux 包络文件

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

如果您只需最基础的核心智能体，采用这种方式也同样可行：

```bash
python -m pip install -e '.' -c constraints-termux.txt
```

### 5. 将 `hermes` 添加到 Termux 的 PATH 环境变量中

```bash
ln -sf "$PWD/venv/bin/hermes" "$PREFIX/bin/hermes"
```

在 Termux 中，`$

```bash
hermes version
hermes doctor
```

### 7. 启动 Hermes Agent

```bash
hermes
```

## 推荐的后续配置步骤

### 配置模型

```bash
hermes model
```

或者直接在 `~/.hermes/.env` 文件中设置这些键值。

### 日后可重新运行完整的交互式设置向导

```bash
hermes setup
```

### 手动安装可选的 Node 依赖项

经过测试的 Termux 路径刻意跳过了 Node/浏览器的初始化流程。如果您日后想尝试使用浏览器相关工具，可按此操作：

```bash
pkg install nodejs-lts
npm install
```

浏览器工具会自动将 Termux 目录（`/data/data/com.termux/files/usr/bin`）纳入 PATH 搜索路径，因此无需进行额外的 PATH 配置，即可识别出 `agent-browser` 和 `npx` 命令。

在另有说明之前，应将 Android 系统上的浏览器/WhatsApp 相关工具视为试验性功能。

---

## 故障排除

### 安装 `.[all]` 时出现“未找到解决方案”错误

请改用经过测试的 Termux 包：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

目前造成问题的核心是 `voice` 这一附加组件：
- `voice` 会调用 `faster-whisper`；
- `faster-whisper` 又依赖于 `ctranslate2`；
- 而 `ctranslate2` 并不提供适用于 Android 的预编译包。

### 在 Android 设备上使用 `uv pip install` 会失败

请改用 Termux 环境下的标准库虚拟环境搭配 `pip` 来执行安装：

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `jiter` / `maturin` 会针对 `ANDROID_API_LEVEL` 发出警告

请在安装之前明确指定 API 级别：

```bash
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `hermes doctor`提示缺少ripgrep或Node工具

可通过Termux包进行安装：

```bash
pkg install ripgrep nodejs
```

### 安装 Python 包时出现构建失败

请确保已安装构建工具链：

```bash
pkg install clang rust make pkg-config libffi openssl
```

然后重新尝试：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

## 手机设备上的已知限制

- 不支持 Docker 后端
- 在测试环境中无法通过 `faster-whisper` 进行本地语音转录
- 安装程序会刻意跳过浏览器自动化相关配置
- 部分可选插件或功能可能可用，但目前仅有 `.[termux]` 和 `.[termux-all]` 被记录为经过测试的 Android 版本包

如果您遇到新的与 Android 相关的问题，请在 GitHub 上创建问题报告，并附上以下信息：
- 您的 Android 系统版本
- `termux-info` 的输出结果
- `python --version` 的输出结果
- `hermes doctor` 的输出结果
- 完整的安装命令及全部错误信息
