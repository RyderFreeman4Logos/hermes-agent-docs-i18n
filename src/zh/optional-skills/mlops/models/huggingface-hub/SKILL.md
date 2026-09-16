---
name: huggingface-hub
description: "HuggingFace hf CLI: search/download/upload models, datasets."
version: 1.0.1
author: Hugging Face
license: MIT
tags: [huggingface, hf, models, datasets, hub, mlops]
platforms: [linux, macos, windows]
---

# Hugging Face CLI (`hf`) 参考指南

`hf` 命令是用于与 Hugging Face Hub 进行交互的现代化命令行界面，提供了管理仓库、模型、数据集以及 Spaces 的各类工具。

> **重要提示：** `hf` 命令已取代现已过时的 `huggingface-cli` 命令。

## 快速入门
*   **安装：** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **帮助：** 使用 `hf --help` 查看所有可用功能及实际应用示例。
*   **身份认证：** 建议通过 `HF_TOKEN` 环境变量或 `--token` 参数进行认证。

---

## 核心命令

### 基本操作
*   `hf download REPO_ID`：从 Hub 下载文件。
*   `hf upload REPO_ID`：上传文件/文件夹（推荐用于单次提交；同时支持大目录的分段上传）。
*   `hf upload-large-folder REPO_ID LOCAL_PATH`：**[已过时]** — 请改用 `hf upload` 命令。
*   `hf sync`：在本地目录与存储桶之间同步文件。
*   `hf env` / `hf version`：查看环境配置及版本信息。

### 身份认证 (`hf auth`)
*   `login` / `logout`：通过 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 中的令牌来管理登录会话。
*   `list` / `switch`：管理和切换多个已存储的访问令牌。
*   `whoami`：查看当前登录的账户信息。

### 仓库管理 (`hf repos`)
*   `create` / `delete`：创建仓库或永久删除仓库。
*   `duplicate`：将模型、数据集或 Space 克隆为新的标识符。
*   `move`：在不同的命名空间之间转移仓库。
*   `branch` / `tag`：管理类似 Git 的引用。
*   `delete-files`：根据模式删除特定文件。

---

## 专用 Hub 操作

### 数据集与模型
*   **数据集**：`hf datasets list`、`info` 以及 `parquet`（列出 Parquet 格式文件的地址）。
*   **SQL 查询**：`hf datasets sql SQL` —— 通过 DuckDB 对数据集的 Parquet 文件地址执行原始 SQL 查询。
*   **模型**：`hf models list` 和 `info`。
*   **论文**：`hf papers ls` —— 查看每日推荐的论文。

### 讨论区与拉取请求（`hf discussions`）
*   管理 Hub 贡献内容的生命周期：`list`、`create`、`info`、`comment`、`close`、`reopen` 以及 `rename`。
*   `diff`：查看拉取请求中的更改内容。
*   `merge`：完成拉取请求的合并。

### 基础设施与计算
*   **端点**：部署和管理推理端点（`deploy`、`pause`、`resume`、`scale-to-zero`、`catalog`）。
*   **任务**：在 HF 的基础设施上运行计算任务。其中包括用于运行带有内联依赖项的 Python 脚本的 `hf jobs uv`，以及用于资源监控的 `stats` 工具。
*   **Space**：管理交互式应用。支持为 Python 文件启用 `dev-mode` 模式及热重载功能，从而无需完全重启即可进行开发。

### 存储与自动化
*   **存储桶**：提供类似 S3 的完整存储桶管理功能（如 `create`、`cp`、`mv`、`rm`、`sync`）。
*   **缓存**：可通过 `list`、`prune`（移除独立的版本）以及 `verify`（校验校验和）等功能来管理本地存储。
*   **Webhook**：通过管理 Hub 的 Webhook（如 `create`、`watch`、`enable`/`disable`）来实现工作流的自动化。
*   **集合**：可将 Hub 中的项整理到各个集合中（如 `add-item`、`update`、`list`）。

---

## 高级用法与技巧

### 全局参数
*   `--format json`：生成机器可读的输出，便于自动化处理。
*   `-q` / `--quiet`：仅输出 ID 信息，减少输出量。

### 扩展功能与技能
*   **扩展功能**：可通过 `hf extensions install REPO_ID` 命令，利用 GitHub 仓库来扩展 CLI 的功能。
*   **AI 技能**：可使用 `hf skills add` 命令来管理 AI 助手的技能。
