---
sidebar_position: 3
title: "Android / Termux"
description: "Run Hermes Agent directly on an Android phone with Termux"
---

# 使用 Termux 在 Android 上运行 Hermes

:::warning 二级平台
Termux（Android）属于[二级平台](./platform-support.md#tier-2)。此处的安装脚本和文档仅以尽力维护的方式提供。对 `main` 分支的任何修改都可能随时导致这些软件包出现故障。
:::

通过 [Termux](https://termux.dev/)，Hermes Agent 可直接在 Android 手机上运行。

它不仅能在手机上提供可用的本地 CLI，还包含目前已知可在 Android 上顺利安装的所有核心功能。

## 已测试的配置支持哪些功能？

经过测试的 Termux 包会安装以下组件：
- Hermes CLI
- cron 定时任务支持
- PTY/后台终端支持
- Telegram 网关支持（手动启动/尽力保障后台运行）
- MCP 支持
- Honcho 内存管理支持
- ACP 支持

具体对应功能如下：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

## 哪些功能尚未纳入测试范围？

目前仍有部分功能需要桌面/服务器版本的依赖项，而这些依赖项尚未为 Android 平台提供，或尚未在手机上经过验证：

- 当前 Android 版本不支持 `.[all]` 选项；
- `voice` 额外功能被 `faster-whisper -> ctranslate2` 拦截，且 `ctranslate2` 并未发布适用于 Android 的安装包；
- Termux 安装程序会跳过自动浏览器/Playwright 启动流程；
- Termux 内部不支持基于 Docker 的终端隔离功能；
- Android 系统仍可能暂停 Termux 的后台任务，因此网关数据的持久化仅能做到尽力保障，而非像常规托管服务那样稳定可靠。

尽管如此，Hermes 作为一款专为手机设计的 CLI 智能体依然能够正常运行——只是其推荐的移动端安装方案在功能范围上刻意比桌面/服务器版本更为有限。

---

## 由社区维护的原生 `pkg` 安装选项

:::caution 由贡献者运营的发行版
该 APT 仓库**由 `@adybag14-cyber` 所维护，并非 NousResearch 的官方发行版**。NousResearch 不会构建、签名、托管这些软件包，也不会对其进行检查。启用该仓库意味着用户需信任该贡献者运营的仓库及其签名密钥。Termux 本身仍属于二级/尽力保障级别的平台。
:::

对于那些更倾向于使用原生包管理器进行安装，而非在手机上手动编译 Python/Rust 依赖项的用户，社区维护的 APT 仓库可供使用。该仓库的引导文件及打包源代码发布在 [`adybag14-cyber/termux-python`](https://github.com/adybag14-cyber/termux-python) 中，而 Hermes 包的编译代码则位于 [`adybag14-cyber/termux-hermes`](https://github.com/adybag14-cyber/termux-hermes) 。可通过以下命令安装该仓库密钥/源码以及 Hermes：

```bash
curl -fsSL https://raw.githubusercontent.com/adybag14-cyber/termux-python/main/scripts/setup_apt_repo.sh | bash
pkg install hermes-agent
```

目前社区发行版中记录的仓库签名密钥指纹为：

```text
EAD24A2124EFA7393A78B7B14699F966313F7A6B
```

通过 APT 安装的 Hermes 实例会标记为 `apt` 安装方式。因此，Hermes 不会对这些由包管理的文件运行其 Git 自动更新功能；此时应使用包管理器来执行相关操作。

```bash
pkg update
pkg upgrade hermes-agent
```

与该选项相关的打包、仓库及签名问题，请向上述社区打包仓库反馈。Hermes 运行时出现的错误仍可在此处报告，需注意 Android/Termux 的支持为尽力而为模式。

---

## 选项 1：单行安装程序

Hermes 现已提供兼容 Termux 的安装程序路径：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

在 Termux 环境中，安装程序会自动执行以下操作：

- 使用 `pkg` 命令来安装系统软件包；
- 通过 `python -m venv` 创建虚拟环境；
- 首先尝试使用内容更丰富的 `.[termux-all]` 插件集，若失败则回退到规模较小的 `.[termux]` 插件集（最后再进行基础安装）——curl 安装工具会自动遵循这一顺序；
- 将 `hermes` 命令链接至 `$PREFIX/bin` 目录，从而确保其始终位于 Termux 的路径搜索范围内；
- 跳过尚未经过测试的浏览器及 WhatsApp 启动程序。

如果您需要具体的命令或想要调试安装失败的问题，可参考下方的手动操作步骤。

---

## 方案 2：手动安装（完全明确指定步骤）

### 1. 更新 Termux 并安装系统软件包

```bash
pkg update
pkg install -y git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
```

为何选择这些软件包？

- `python` — 运行时环境及虚拟环境支持

:::warning 支持的 Python 版本范围
Hermes 要求使用 **Python >=3.11 且 <3.14** 的版本。当前 Termux 自带的 `python` 为 3.14.x 版本，超出了该范围——安装程序会检测到这一点，并会自动尝试从 [Termux 用户仓库（TUR）](https://github.com/termux-user-repository/tur) 中查找兼容的解释器。如需手动安装，请自行获取合适的版本：

```bash
pkg install tur-repo
pkg install python3.13
```

请在以下命令中将 `python` 替换为 `python3.13`
（例如：`python3.13 -m venv venv`）。
:::

- `git` — 克隆/更新代码仓库
- `clang`、`rust`、`make`、`pkg-config`、`libffi`、`openssl` — 用于在 Android 上构建部分 Python 依赖项
- `nodejs` — 用于测试范围之外的实验，属于可选的 Node 运行时环境
- `ripgrep` — 快速文件搜索工具
- `ffmpeg` — 用于媒体文件及文本转语音处理

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

### 4. 安装已测试过的 Termux 套件

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

在 Termux 中，`$/PREFIX/bin` 已经被添加到 PATH 环境变量中，因此这样一来，无需每次都重新激活虚拟环境，`hermes` 命令即可在新的终端会话中持续正常使用。

### 6. 验证安装情况

```bash
hermes --version
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

经过测试的 Termux 版本刻意跳过了 Node/浏览器的初始化步骤。如果您日后想尝试使用浏览器相关工具，所需依赖取决于您所使用的后端类型：

- **云浏览器服务提供商**（如 Browserbase、Browser Use、Firecrawl）会自行托管 Chromium，因此仅需 Node.js 即可——`agent-browser` 会在首次使用时通过 `npx agent-browser` 延迟加载。

  ```bash
  pkg install nodejs-lts
  ```

在 Termux 中进行**本地浏览器自动化**操作时，必须安装完整的 `agent-browser` 版本——由于纯通过 npx 方式调用的方案稳定性较差，无法被视为可用方案，因此在本地模式下会被明确拒绝使用。

  ```bash
  pkg install nodejs-lts
  npm install -g agent-browser && agent-browser install
  ```

浏览器工具会自动将 Termux 的目录（`/data/data/com.termux/files/usr/bin`）纳入 PATH 搜索路径，因此无需进行额外的 PATH 配置，即可识别出 `agent-browser` 和 `npx` 工具。

在另有说明之前，建议将 Android 系统上的浏览器/WhatsApp 相关工具视为实验性功能使用。

---

## 故障排除

### 安装 `.[all]` 时出现“未找到解决方案”

请改用经过测试的 Termux 包：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

目前造成问题的组件是 `voice` 插件：

- `voice` 会调用 `faster-whisper`；
- `faster-whisper` 又依赖于 `ctranslate2`；
- 而 `ctranslate2` 并不提供适用于 Android 的预编译包。

### 在 Android 设备上使用 `uv pip install` 会失败

请改用 Termux 环境下的 stdlib venv 配合 `pip` 进行安装：

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `jiter` / `maturin` 会针对 `ANDROID_API_LEVEL` 发出警告

在安装之前，请明确指定 API 级别：

```bash
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `hermes doctor` 报告缺少 ripgrep 或 Node

可通过 Termux 包进行安装：

```bash
pkg install ripgrep nodejs
```

### 安装 Python 包时出现构建失败问题

请确保已安装构建工具链：

```bash
pkg install clang rust make pkg-config libffi openssl
```

然后重新尝试：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

## 手机端已知的限制

- 不支持 Docker 后端
- 在测试环境中无法通过 `faster-whisper` 进行本地语音转录
- 安装程序会刻意跳过浏览器自动化相关的配置步骤
- 虽然部分附加组件可能仍能正常使用，但目前仅有 `.[termux]` 和 `.[termux-all]` 被列为经过测试的 Android 版本包

如果您遇到新的与 Android 系统相关的问题，请在 GitHub 上创建一个问题报告，并附上以下信息：

- 您的 Android 系统版本
- `termux-info` 的输出结果
- `python --version` 的输出结果
- `hermes doctor` 的检测结果
- 完整的安装命令及错误日志
