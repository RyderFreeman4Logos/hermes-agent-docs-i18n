# 安装 ast-grep

该技能提供了 `install.sh`（适用于 POSIX 系统）和 `install.ps1`（适用于 Windows 系统）这两个安装脚本，它们会按优先级尝试所有可行的安装方法，最后才作为兜底方案通过 GitHub 仓库下载版本进行安装。**通常您无需阅读此页面。** 直接运行安装脚本即可：

```bash
bash install.sh                        # macOS / Linux / WSL / Git Bash
pwsh -File install.ps1                 # Windows PowerShell
```

本页面适用于安装程序无法找到可行安装方法时的（罕见）情况，或者您希望手动安装 ast-grep 时使用。

---

## 各操作系统的安装命令（原文照录，可直接复制粘贴）

### macOS

```bash
brew install ast-grep                  # Homebrew - the primary path
sudo port install ast-grep             # MacPorts
npm install -g @ast-grep/cli           # if you have Node already
cargo install ast-grep --locked        # if you have Rust already
```

### Linux系统

```bash
# Universal (works on every distro)
npm install -g @ast-grep/cli
cargo install ast-grep --locked
pip install ast-grep-cli

# Distro-specific
nix-env -iA nixpkgs.ast-grep           # NixOS / Nix
brew install ast-grep                  # Linuxbrew

# NixOS shell.nix
nix-shell -p ast-grep
```

> **Linux 特有问题**：该二进制文件的名称为 `sg`，但在大多数 Linux 系统中，`sg` 也是 `util-linux` 包中的 **`setgroups` 命令**。shell 会优先识别 `setgroups`，从而忽略 `ast-grep`。有以下两种解决方案：
>
> 1. 始终使用完整名称 `ast-grep` 来调用该命令。
> 2. 在 `~/.bashrc` 或 `~/.zshrc` 文件中添加别名：`alias sg=ast-grep`。
>
> `scripts/` 目录下的 `ast_grep_helper.py` 脚本已解决了此问题——当在 Linux 的 PATH 环境变量中检测到 `sg` 时，它会先运行 `--version` 命令，若确认该文件并非 `ast-grep`，则会拒绝执行。

### Windows

```powershell
scoop install main/ast-grep            # Scoop (most common on dev machines)
winget install --id ast-grep.ast-grep  # Winget (Microsoft built-in)
choco install ast-grep                 # Chocolatey
npm install -g @ast-grep/cli           # any OS with Node
cargo install ast-grep --locked        # any OS with Rust
```

### Windows 上的 WSL / Git Bash

可将其视为 Linux 环境。可使用 `npm`、`cargo`、`pip` 或 `bash install.sh` 进行安装。

---

## 跨平台/跨语言生态系统安装方式

这些方法适用于所有操作系统：

| 安装方式 | 命令 | 优点 | 缺点 |
|---|---|---|---|
| **npm** | `npm install -g @ast-grep/cli` | 安装速度快，提供预编译的二进制文件 | 需要 Node 18 及以上版本 |
| **cargo** | `cargo install ast-grep --locked` | 始终从源代码编译最新版本 | 编译速度较慢（约 3-5 分钟） |
| **cargo binstall** | `cargo binstall ast-grep` | 安装速度快（直接下载已发布的二进制文件） | 需要先安装 `cargo-binstall` 工具 |
| **pip** | `pip install ast-grep-cli` | 可在任何 Python 虚拟环境中使用 | 需要 Python 3.8 及以上版本 |
| **pipx** | `pipx install ast-grep-cli` | 实现独立安装，避免版本冲突 | 需要安装 pipx 工具 |
| **mise** | `mise use -g ast-grep` | 是 asdf 的继任者，支持版本锁定功能 | 需要安装 mise 工具 |
| **GitHub 发布版** | 手动下载 | 为纯二进制文件，无需依赖工具链 | 需要手动配置 PATH 环境变量 |

---

## 通过 GitHub 发布版手动安装

当所有包管理器都无法使用时：

```bash
# 1. Pick the right asset for your OS+arch from the latest release:
#    https://github.com/ast-grep/ast-grep/releases/latest
#
#    Naming pattern:
#      app-aarch64-apple-darwin.zip          macOS Apple Silicon
#      app-x86_64-apple-darwin.zip           macOS Intel
#      app-aarch64-unknown-linux-gnu.zip     Linux ARM64 (glibc)
#      app-x86_64-unknown-linux-gnu.zip      Linux x86_64 (glibc)
#      app-x86_64-pc-windows-msvc.zip        Windows x86_64
#      app-aarch64-pc-windows-msvc.zip       Windows ARM64

# 2. Download and extract:
VERSION=0.45.0
TRIPLE=aarch64-apple-darwin
curl -fsSL "https://github.com/ast-grep/ast-grep/releases/download/${VERSION}/app-${TRIPLE}.zip" -o /tmp/ast-grep.zip
unzip /tmp/ast-grep.zip -d /tmp/ast-grep
sudo mv /tmp/ast-grep/ast-grep /usr/local/bin/sg
sudo chmod +x /usr/local/bin/sg

# 3. Verify:
sg --version
```

该技能的 `install.sh` 脚本会自动完成第1至3步操作，并将二进制文件放置到 `<skill_root>/bin/sg` 目录中，这样您无需使用 sudo 权限即可直接使用它。

---

## 从源代码构建

```bash
git clone https://github.com/ast-grep/ast-grep.git
cd ast-grep
cargo install --path ./crates/cli --locked
```

需要 Rust 1.74+ 版本。这是速度最慢的安装方式；仅在你需要某个特定的代码提交版本或尚未发布的修复补丁时才有用。

---

## 验证安装情况

```bash
ast-grep --version            # or `sg --version`
# ast-grep 0.45.0
```

接下来，对一个真实的查询进行合理性检查：

```bash
echo 'console.log("hello")' | sg run -p 'console.log($MSG)' --lang js --stdin
```

预期结果：仅匹配到一条包含 `console.log("hello")` 调用的记录，并将其高亮显示。

---

## 编辑器集成

安装 CLI 后，请按以下步骤配置您的编辑器：

- **VS Code**：安装 [`ast-grep`](https://marketplace.visualstudio.com/items?itemName=ast-grep.ast-grep-vscode) 扩展。如需实时诊断功能，还需在项目根目录下创建 `sgconfig.yml` 文件。
- **Neovim**：通过 `nvim-lspconfig` 配置 `ast_grep` 服务器，或直接安装 [`telescope-ast-grep.nvim`](https://github.com/ray-x/telescope-ast-grep.nvim)。
- **Helix**：在 `languages.toml` 文件中将 `ast-grep lsp` 添加为语言服务器。
- **Emacs**：安装 [`ast-grep.el`](https://github.com/SunskyXH/ast-grep.el) 文件。

有关 `ast-grep lsp` 的各选项信息，请参阅 `references/cli.md` 文档。

---

## 卸载

| 方式 | 命令 |
|---|---|
| brew | `brew uninstall ast-grep` |
| npm | `npm uninstall -g @ast-grep/cli` |
| cargo | `cargo uninstall ast-grep` |
| pip | `pip uninstall ast-grep-cli` |
| pipx | `pipx uninstall ast-grep-cli` |
| scoop | `scoop uninstall ast-grep` |
| winget | `winget uninstall --id ast-grep.ast-grep` |
| choco | `choco uninstall ast-grep` |
| GitHub二进制包 | `rm <skill_root>/bin/sg` |
