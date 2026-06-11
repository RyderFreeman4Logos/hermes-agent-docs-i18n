---
title: "Huggingface Hub — HuggingFace hf CLI: search/download/upload models, datasets"
sidebar_label: "Huggingface Hub"
description: "HuggingFace hf CLI: search/download/upload models, datasets"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Huggingface Hub

HuggingFace hf CLI：用于搜索、下载及上传模型与数据集。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/mlops/huggingface-hub` |
| 版本 | `1.0.0` |
| 开发者 | Hugging Face |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为此内容。
:::

# Hugging Face CLI (`hf`) 参考指南

`hf` 命令是用于与 Hugging Face Hub 进行交互的现代化命令行界面，可提供管理仓库、模型、数据集以及 Spaces 的各类工具。

> **重要提示：** `hf` 命令已取代现已过时的 `huggingface-cli` 命令。

## 快速入门
*   **安装：** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **帮助信息：** 使用 `hf --help` 查看所有可用功能及实际应用示例。
*   **身份认证：** 建议通过 `HF_TOKEN` 环境变量或 `--token` 参数进行认证。

---

## 核心命令

### 基本操作
*   `hf download REPO_ID`：从 Hub 下载文件。
*   `hf upload REPO_ID`：上传文件或文件夹（适用于单次提交场景）。
*   `hf upload-large-folder REPO_ID LOCAL_PATH`：适用于大目录的分段上传。
*   `hf sync`：在本地目录与存储桶之间同步文件。
*   `hf env` / `hf version`：查看环境信息及版本详情。

### 身份认证 (`hf auth`)
*   `login` / `logout`：使用来自 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 的令牌管理会话。
*   `list` / `switch`：管理与切换多个已存储的访问令牌。
*   `whoami`：查看当前登录的账户信息。

### 仓库管理 (`hf repos`)
*   `create` / `delete`：创建或永久删除仓库。
*   `duplicate`：将模型、数据集或 Space 克隆到新的标识符下。
*   `move`：在不同的命名空间之间转移仓库。
*   `branch` / `tag`：管理类似 Git 的引用。
*   `delete-files`：根据模式删除特定文件。

---

## 针对 Hub 的高级操作

### 数据集与模型
*   **数据集：** `hf datasets list`、`info` 以及 `parquet`（列出 Parquet 格式文件的地址）。
*   **SQL 查询：** `hf datasets sql SQL` —— 通过 DuckDB 对数据集的 Parquet 文件地址执行原始 SQL 查询。
*   **模型：** `hf models list` 和 `info`。
*   **论文：** `hf papers list` —— 查看每日推荐的论文。

### 讨论区与拉取请求 (`hf discussions`)
*   管理 Hub 贡献内容的整个生命周期：`list`、`create`、`info`、`comment`、`close`、`reopen` 以及 `rename`。
*   `diff`：查看拉取请求中的更改内容。
*   `merge`：完成拉取请求的合并。

### 基础设施与计算功能
*   **推理端点：** 部署并管理推理端点（`deploy`、`pause`、`resume`、`scale-to-zero`、`catalog`）。
*   **任务处理：** 在 Hugging Face 的基础设施上运行计算任务。包括用于运行带内联依赖项的 Python 脚本的 `hf jobs uv`，以及用于资源监控的 `stats` 工具。
*   **Spaces：** 管理交互式应用。支持为 Python 文件启用 `dev-mode` 模式及 `hot-reload` 功能，从而无需完全重启即可进行开发。

### 存储与自动化功能
*   **存储桶：** 支持类似 S3 的完整存储桶管理功能（`create`、`cp`、`mv`、`rm`、`sync`）。
*   **缓存：** 通过 `list`、`prune`（删除已分离的版本）以及 `verify`（校验校验和）等功能管理本地存储。
*   **Webhook：** 通过管理 Hub 的 Webhook 实现工作流自动化（`create`、`watch`、`enable`/`disable`）。
*   **集合：** 将 Hub 中的各类项目组织到集合中（`add-item`、`update`、`list`）。

---

## 高级用法与技巧

### 全局参数
*   `--format json`：生成机器可读的输出格式，便于自动化处理。
*   `-q` / `--quiet`：仅输出标识符信息，减少输出量。

### 扩展功能与技能
*   **扩展插件：** 通过 `hf extensions install REPO_ID`，利用 GitHub 仓库扩展 CLI 的功能。
*   **智能体技能：** 使用 `hf skills add` 命令管理 AI 助手技能。
