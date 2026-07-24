---
sidebar_position: 2.5
title: "Platform Support"
description: "Which operating systems, distribution methods, and features Hermes Agent supports."
---

# 平台支持情况

Hermes Agent 支持多种平台和分发方式，但无法覆盖所有可能的安装方法。

---

## 第一层级平台

我们会竭力确保这些平台的安装与更新过程不受影响。针对第一层级平台出现的问题和功能退化，我们将优先处理，其优先级高于其他平台。

| 操作系统/架构                                                             | 安装方法                                                                                                           | 备注                                                                                                                                                     |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **macOS**（Apple Silicon 芯片）                                                     | [Hermes Desktop](https://hermes-agent.nousresearch.com/)，[`install.sh`](./installation.md#linux--macos--wsl2--android-termux) |
| [**Windows 10 / 11**](../user-guide/windows-native.md)（x86_64、aarch64）      | [Hermes Desktop](https://hermes-agent.nousresearch.com/)，[`install.ps1`](./installation.md#windows-native)                    | 部分功能[暂不支持](../user-guide/windows-native.md#feature-matrix)。                                                                       |
| **Linux / [WSL2](../user-guide/windows-wsl-quickstart.md)**（x86_64、aarch64） | [`install.sh`](./installation.md#linux--macos--wsl2--android-termux)                                                           | 我们已在最新版本的 Ubuntu 和 WSL2 上进行过测试。只要您的发行版包含 glibc、systemd 且遵循文件系统层级标准，通常都能正常运行。 |
| [**Docker 容器**](../user-guide/docker.md#quick-start)（x86_64、aarch64） | [`docker pull`](../user-guide/docker.md#quick-start)                                                                           | 通过 Docker 安装的版本不支持 `hermes update` 命令，如需更新需重新拉取新的镜像。                                                                  |

---

## 第二层级平台

这些平台仅作为临时方案在项目中得到支持。
新版本发布时可能会影响其正常运行，且我们无法保证出现问题后能立即修复。

虽然我们会接受用于修复这些平台问题的 Pull Request，但其处理优先级低于第一层级平台的问题。

| 操作系统/架构              | 安装方法                                                 | 备注                                                                        |
| ------------------------------ | -------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Android（Termux）**（aarch64） | [`install.sh`](./installation.md#linux--macos--wsl2--android-termux) | 部分功能[暂不支持](./termux.md#known-limitations-on-phones)。 |
| **Nix**（MacOS、Linux、NixOS）  | [`install.sh`](./nix-setup.md)                                       | 由于 node.js 打包问题，该平台经常出现兼容性问题，祝好运~! <3             |

## 不支持的平台

以下平台和分发方式**不受支持**。
我们建议您迁移到受支持的平台或分发方式。
这些平台目前可能已存在问题，未来也可能会出现更多故障。
针对它们的修复 Pull Request 将不会被接受，任何为保持其与系统兼容而编写的代码也可能会随时被移除。

- 通过 AUR 安装的方式（如果有助于解决问题，我们可能会提交补丁 <3）
- 使用 x86（Intel）处理器的 macOS 系统
- 通过 `pypi` 安装的方式（例如 `uv tool install hermes-agent`、`pip install hermes-agent` 等）
- 通过 `brew` 安装的方式（`brew install hermes-agent`）如果您使用的是不受支持的发行方式，请阅读[安装指南](./installation.md)，了解如何切换为受支持的发行方式。
