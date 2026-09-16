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
| 来源 | 可选 —— 通过 `hermes skills install official/mlops/huggingface-hub` 进行安装 |
| 路径 | `optional-skills/mlops/models\huggingface-hub` |
| 版本 | `1.0.1` |
| 开发者 | Hugging Face |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为内容。
:::

# Hugging Face CLI (`hf`) 参考指南

`hf` 命令是用于与 Hugging Face Hub 进行交互的现代命令行界面，提供了管理仓库、模型、数据集以及 Spaces 的各类工具。

> **重要提示：** `hf` 命令已取代现已过时的 `huggingface-cli` 命令。

## 快速入门
*   **安装：** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **帮助：** 使用 `hf --help` 查看所有可用功能及实际应用示例。
*   **身份验证：** 建议通过 `HF_TOKEN` 环境变量或 `--token` 参数来进行认证。

---

## 核心命令

### 基础操作
*   `hf download REPO_ID`：从 Hub 下载文件。
*   `hf upload REPO_ID`：上传文件或文件夹（推荐用于单次提交操作；同时支持大目录的分段上传）。
*   `hf upload-large-folder REPO_ID LOCAL_PATH`：**[已废弃]** — 请改用 `hf upload` 命令。
*   `hf sync`：在本地目录与存储桶之间同步文件。
*   `hf env` / `hf version`：查看环境信息及版本详情。

### 认证 (`hf auth`)
*   `login` / `logout`：使用来自 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 的令牌来管理会话。
*   `list` / `switch`：管理与切换多个已存储的访问令牌。
*   `whoami`：查看当前登录的账户信息。

### 仓库管理 (`hf repos`)
*   `create` / `delete`：创建新仓库或永久删除仓库。
*   `duplicate`：将模型、数据集或 Space 克隆到新的标识符下。
*   `move`：在不同的命名空间之间移动仓库。
*   `branch` / `tag`：管理类似 Git 的引用。
*   `delete-files`：根据模式删除特定文件。

---

## 针对 Hub 的专用操作

### 数据集与模型
*   **数据集**：`hf datasets list`、`info` 以及 `parquet`（列出 Parquet 格式文件的地址）。
*   **SQL 查询**：`hf datasets sql SQL` — 通过 DuckDB 对数据集的 Parquet 文件地址执行原始 SQL 查询。
*   **模型**：`hf models list` 和 `info`。
*   **论文**：`hf papers ls` — 查看每日推荐的论文。

### 讨论区与拉取请求 (`hf discussions`)
*   管理 Hub 贡献的完整生命周期：包括 `list`、`create`、`info`、`comment`、`close`、`reopen` 以及 `rename` 操作。
*   `diff`：查看 Pull Request 中的变更内容。
*   `merge`：完成 Pull Request 的合并。

### 基础设施与计算
*   **端点管理**：部署并管理推理端点，支持 `deploy`、`pause`、`resume`、`scale-to-zero`、`catalog` 等操作。
*   **任务执行**：在 HF 基础设施上运行计算任务。其中包括用于执行带有内联依赖项的 Python 脚本的 `hf jobs uv`，以及用于资源监控的 `stats` 工具。
*   **空间管理**：管理交互式应用。支持为 Python 文件启用 `dev-mode` 模式及 `hot-reload` 功能，从而无需完全重启即可进行开发。

### 存储与自动化
*   **存储桶管理**：提供类似 S3 的完整存储桶功能，包括 `create`、`cp`、`mv`、`rm`、`sync` 等操作。
*   **缓存管理**：通过 `list`、`prune`（移除已断开的版本）以及 `verify`（校验校验和）等命令来管理本地存储。
*   **Webhook 管理**：通过创建、监控以及启用/禁用 Hub Webhook 来实现工作流的自动化。
*   **集合管理**：将 Hub 中的各类项目整理到不同的集合中，支持 `add-item`、`update`、`list` 等操作。

---

## 高级用法与技巧

### 全局参数
*   `--format json`：生成机器可读的输出格式，便于自动化处理。
*   `-q` / `--quiet`：仅输出编号信息，减少输出量。

### 扩展功能与技能
*   **扩展插件**：通过 `hf extensions install REPO_ID` 命令，利用 GitHub 仓库来扩展 CLI 的功能。
*   **AI 助手技能**：使用 `hf skills add` 命令来管理 AI 助手的各项技能。
