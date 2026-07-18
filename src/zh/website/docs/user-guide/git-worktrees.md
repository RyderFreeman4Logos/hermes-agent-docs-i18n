---
sidebar_position: 3
sidebar_label: "Git Worktrees"
title: "Git Worktrees"
description: "Run multiple Hermes agents safely on the same repository using git worktrees and isolated checkouts"
---

# Git 工作树

Hermes Agent 常用于大型且长期维护的代码仓库中。当您需要：

- 在同一个项目中**并行运行多个 Agent**，或
- 将实验性重构代码与主分支隔离开来，

此时使用 Git **工作树**便是最安全的方式——它能让每个 Agent 都拥有独立的检出目录，而无需复制整个仓库。

本页将介绍如何将工作树与 Hermes 结合使用，从而为每个会话创建干净、隔离的工作目录。

## 为何要在 Hermes 中使用工作树？

Hermes 将**当前工作目录**视为项目根目录：

- CLI：运行 `hermes` 或 `hermes chat` 命令的目录
- 消息网关：由 `~/.hermes/config.yaml` 中的 `terminal.cwd` 所指定的目录

如果在**同一个检出目录**下运行多个 Agent，它们的修改可能会相互干扰：

- 一个 Agent 可能会删除或覆盖另一个 Agent 正在使用的文件。
- 这也会让人们难以区分哪些修改属于哪个实验。

而通过工作树，每个 Agent 都能拥有：

- 自己的**独立分支和工作目录**
- 用于 `/rollback` 操作的专属 Checkpoint Manager 历史记录

另请参阅：[检查点与 /rollback](./checkpoints-and-rollback.md)。

## 快速入门：创建工作树

在包含 `.git/` 文件夹的主仓库中，为某个功能分支创建一个新的工作树：

```bash
# From the main repo root
cd /path/to/your/repo

# Create a new branch and worktree in ../repo-feature
git worktree add ../repo-feature feature/hermes-experiment
```

这将创建：

- 一个新目录：`../repo-feature`
- 一个新分支：`feature/hermes-experiment`，并会在该目录中检出

现在你可以进入这个新的工作区，然后在其中运行 Hermes：

```bash
cd ../repo-feature

# Start Hermes in the worktree
hermes
```

Hermes 将会：

- 将 `../repo-feature` 视为项目根目录。
- 使用该目录来存放上下文文件、代码修改内容以及相关工具。
- 为属于该工作树的 `/rollback` 操作启用**独立的检查点历史记录**。

## 并行运行多个 Agent

您可以创建多个工作树，每个工作树均可拥有自己的分支：

```bash
cd /path/to/your/repo

git worktree add ../repo-experiment-a feature/hermes-a
git worktree add ../repo-experiment-b feature/hermes-b
```

在独立的终端中：

```bash
# Terminal 1
cd ../repo-experiment-a
hermes

# Terminal 2
cd ../repo-experiment-b
hermes
```

每个 Hermes 进程均遵循以下规则：

- 在独立的分支上运行（如 `feature/hermes-a` 和 `feature/hermes-b`）。
- 根据工作树路径生成不同的镜像仓库哈希值，以此来保存检查点。
- 可以独立使用 `/rollback` 命令，而不会影响其他进程。

以下情况尤其需要这种设计：

- 执行批量重构时。
- 对同一任务尝试不同解决方案时。
- 同时使用 CLI 和网关会话处理同一个上游仓库时。

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
  - 对每一项重大更改都创建专门的分支或工作树。
  - 这样可以使代码差异更集中，PR 的规模更小，便于审核。
- **以实验名称为分支命名**
  - 例如：`feature/hermes-checkpoints-docs`、`feature/hermes-refactor-tests`。
- **频繁提交代码**
  - 使用 Git 提交来标记重要的里程碑。
  - 对于其间通过工具进行的修改，可借助[检查点与回滚功能](./checkpoints-and-rollback.md)作为安全保障。
- **使用工作树时避免从裸仓库根目录运行 Hermes**
  - 建议直接在对应的工作树目录中运行，这样每个 Agent 的职责范围会更明确。

## 使用 `hermes -w`（自动工作树模式）

Hermes 内置了 `-w` 参数，可**自动创建一个带独立分支的临时 Git 工作树**。您无需手动设置工作树——只需进入项目目录后运行相应命令即可：

```bash
cd /path/to/your/repo
hermes -w
```

Hermes将会执行以下操作：

- 在您仓库的`.worktrees/`目录下创建一个临时工作树。
- 拉取一个独立的分支（例如`hermes/hermes-<hash>`）。
- 在该工作树中运行完整的CLI会话。

这是实现工作树隔离的最简单方法。您也可以将其与单次查询结合使用：

```bash
hermes -w -z "Fix issue #123"
```

对于并行运行的 Agent，可打开多个终端并在每个终端中执行 `hermes -w` —— 每次调用都会自动创建独立的 worktree 和分支。

## 综合运用这些机制

- 使用 **git worktrees** 为每个 Hermes 会话创建独立的代码检出环境。
- 使用 **分支** 记录实验的整体历史脉络。
- 在每个 worktree 内部利用 **检查点 + `/rollback`** 功能来纠正错误。

通过这种组合方式，您将获得：

- 强大的保障，确保不同的 Agent 和实验互不干扰。
- 快速的迭代周期，并能轻松恢复因错误修改带来的问题。
- 清晰、便于审查的 pull request。

## 在不同 worktree 之间开发 UI 界面

TypeScript 相关模块（如 `ui-tui/`、`apps/desktop/`）各自都需要一个 `node_modules` 目录，而每次在新的 worktree 中执行 `npm ci` 都会重复生成该目录，导致所有分支中的内容一致。如果您需要在多个 worktree 中同时修改 TUI 或桌面应用，可参考 [从 Worktree 开发 TUI 和桌面应用](../developer-guide/worktree-ui-dev.md)，了解如何通过符号链接实现仅安装一次的 `htui` / `hgui` 助手。
