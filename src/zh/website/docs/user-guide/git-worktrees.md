---
sidebar_position: 3
sidebar_label: "Git Worktrees"
title: "Git Worktrees"
description: "Run multiple Hermes agents safely on the same repository using git worktrees and isolated checkouts"
---

# Git 工作树

Hermes Agent 常用于规模庞大且长期维护的代码仓库中。当您需要：

- 在同一个项目中**并行运行多个 Agent**，或
- 将实验性重构与主分支隔离开来，

此时使用 Git **工作树**便是最安全的方式——它能让每个 Agent 都拥有独立的检出版本，而无需复制整个仓库。

本页面将介绍如何将工作树与 Hermes 结合使用，从而为每个会话创建干净、隔离的工作目录。

## 为何要在 Hermes 中使用工作树？

Hermes 将**当前工作目录**视为项目根目录：

- CLI：运行 `hermes` 或 `hermes chat` 命令的目录
- 消息网关：由 `~/.hermes/config.yaml` 中的 `terminal.cwd` 所指定的目录

如果在**同一检出版本**下运行多个 Agent，它们的修改可能会相互干扰：

- 一个 Agent 可能会删除或重写另一个 Agent 正在使用的文件。
- 这样就很难分辨哪些修改属于哪个实验。

而通过工作树，每个 Agent 都可以拥有：

- 自己的**独立分支和工作目录**
- 用于 `/rollback` 操作的专属 Checkpoint Manager 历史记录

另请参阅：[Checkpoints 和 /rollback](./checkpoints-and-rollback.md)。

## 快速入门：创建工作树

### 在会话中操作：`/worktree new`

这是最快捷的方法（灵感来自 Copilot CLI 的 `/worktree new`）：在交互式 CLI 会话中，执行

```
/worktree new my-experiment
```

Hermes 会在仓库中创建 `.worktrees/my-experiment/` 目录（分支名为 `hermes/my-experiment`，除非设置了 `worktree_sync: false`，否则该分支会基于最新拉取的远程代码顶端），并将会话中的终端及文件工具重定向至该目录——无需重启。若不指定名称，则会自动生成一个随机命名的 `hermes-<id>` 工作树。单独输入 `/worktree` 可查看当前活跃的工作树，而 `/worktree list` 则可列出所有工作树。与 `hermes -w` 的行为一致，只有包含未推送提交的工工作树在退出后才会被保留。

### 使用 git 手动操作

从包含 `.git/` 文件的主仓库中，为某个功能分支创建一个新的工作树：

```bash
# From the main repo root
cd /path/to/your/repo

# Create a new branch and worktree in ../repo-feature
git worktree add ../repo-feature feature/hermes-experiment
```

这将创建：

- 一个新目录：`../repo-feature`
- 一个新分支：`feature/hermes-experiment`，并会在该目录中检出该分支

现在你可以进入这个新的工作区，然后在其中运行 Hermes：

```bash
cd ../repo-feature

# Start Hermes in the worktree
hermes
```

Hermes 将会：

- 将 `../repo-feature` 视为项目根目录。
- 使用该目录来存放上下文文件、代码修改内容以及相关工具。
- 为属于该工作树的 `/rollback` 操作保留**独立的检查点历史记录**。

## 并行运行多个 Agent

您可以创建多个工作树，每个工作树均可拥有自己的分支：

```bash
cd /path/to/your/repo

git worktree add ../repo-experiment-a feature/hermes-a
git worktree add ../repo-experiment-b feature/hermes-b
```

在各自的终端中：

```bash
# Terminal 1
cd ../repo-experiment-a
hermes

# Terminal 2
cd ../repo-experiment-b
hermes
```

每个 Hermes 进程均遵循以下规则：

- 在独立的分支上运行（例如 `feature/hermes-a` 和 `feature/hermes-b`）。
- 根据工作树路径生成不同的镜像仓库哈希值，以此来保存检查点。
- 可以独立使用 `/rollback` 命令，而不会影响其他进程。

以下情况尤其需要这种设计：

- 执行批量重构任务时。
- 对同一任务尝试不同解决方案时。
- 同时使用 CLI 和网关会话操作同一个上游仓库时。

## 安全地清理工作树

完成实验后，请按以下步骤操作：

1. 决定是保留还是丢弃该实验成果。
2. 如果选择保留：
   - 按常规方式将该分支合并到主分支中。
3. 删除该工作树。

```bash
cd /path/to/your/repo

# Remove the worktree directory and its reference
git worktree remove ../repo-feature
```

备注：

- 若工作树中存在未提交的更改，`git worktree remove` 命令会拒绝删除该工作树，除非您强制执行。
- 删除工作树**不会**自动删除对应分支；您仍可使用常规的 `git branch` 命令来决定是保留还是删除该分支。
- 当您删除工作树时，位于 `~/.hermes/checkpoints/` 下的 Hermes 检查点数据不会被自动清理，不过这些数据的体积通常很小。

## 最佳实践

- **每个 Hermes 实验使用一个工作树**
  - 对于每一项重大修改，都应创建专门的分支或工作树。
  - 这样可以确保代码差异集中，PR 文件规模较小且便于审查。
- **以实验名称为分支命名**
  - 例如：`feature/hermes-checkpoints-docs`、`feature/hermes-refactor-tests`。
- **频繁提交代码**
  - 使用 Git 提交来标记重要的里程碑。
  - 对于中间阶段由工具自动完成的修改，可借助[检查点与回滚功能](./checkpoints-and-rollback.md)作为安全保障。
- **使用工作树时避免从裸仓库根目录运行 Hermes**
  - 建议直接在对应的工作树目录中运行，这样每个 Agent 的工作范围会更清晰。

## 使用 `hermes -w`（自动工作树模式）

Hermes 内置了 `-w` 参数，该参数可以**自动创建一个带有独立分支的临时 Git 工作树**。您无需手动设置工作树——只需进入项目目录后运行相应命令即可：

```bash
cd /path/to/your/repo
hermes -w
```

Hermes 将会：

- 在您仓库的 `.worktrees/` 目录下创建一个临时工作树。
- 拉取一个独立的分支（例如 `hermes/hermes-<hash>`）。
- 在该工作树中运行完整的 CLI 会话。

这是实现工作树隔离的最简单方法。您也可以将其与单次查询结合使用：

```bash
hermes -w -z "Fix issue #123"
```

对于并行运行的 Agent，可打开多个终端并在每个终端中执行 `hermes -w` 命令——每次调用都会自动创建独立的工作树和分支。

## 整合运用这些机制

- 使用 **git worktrees** 为每个 Hermes 会话创建独立的代码检出环境。
- 利用 **分支** 记录实验的整体历史脉络。
- 通过 **检查点 + `/rollback`** 功能，在每个工作树内快速恢复因错误操作造成的损失。

这样的组合能够带来以下优势：

- 确保不同的 Agent 和实验互不干扰。
- 实现快速的迭代循环，并能轻松修复错误的修改。
- 生成整洁、便于审查的 Pull Request。

## 跨工作树开发用户界面

TypeScript 相关代码（位于 `ui-tui/`、`apps/desktop/` 等目录）各自都需要一个 `node_modules` 目录，而每次在工作树中执行 `npm ci` 都会重复创建这些目录，导致所有分支之间都存在重复内容。如果您需要从多个工作树同时对 TUI 或桌面应用进行修改，请参考 [从工作树调用 TUI 和桌面应用](../developer-guide/worktree-ui-dev.md)，了解如何通过符号链接实现单一安装的 `htui` / `hgui` 辅助工具。
