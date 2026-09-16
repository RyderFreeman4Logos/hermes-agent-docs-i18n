---
sidebar_position: 13
sidebar_label: "Plugin Catalog"
title: "Plugin Catalog"
description: "Browse and install reviewed, SHA-pinned Hermes plugins from the curated catalog"
---

# 插件目录

插件目录是一个经过精心筛选并经过人工审核的 Hermes 插件列表，您只需通过命令输入插件名称即可完成安装：

```bash
hermes plugins install <name>
```

您可以在 **[/docs/plugins](/plugins)** 页面以可视化方式浏览这些插件——支持搜索、层级筛选（官方版/社区版）、功能标签查看，以及复制每款插件的安装命令。

该目录是对现有[插件系统](plugins.md)的补充，而非替代。从目录中安装的任何插件本质上都属于普通插件；目录仅为其增加了发现功能和审核机制。

## 插件条目的构成

每个插件条目都是 hermes-agent 仓库 [`plugin-catalog/`](https://github.com/NousResearch/hermes-agent/tree/main/plugin-catalog) 目录下的一个小型 YAML 文件，其中包含以下信息：

| 字段 | 含义 |
|---|---|
| `name` | 传递给 `hermes plugins install` 命令的目录键 |
| `repo` | 插件的公共 Git 仓库地址 |
| `sha` | 经过审核的**精确 40 位十六进制提交哈希值**——安装时需使用该固定版本，而非分支的最新代码 |
| `tier` | `official`（由 NousResearch 维护）或 `community` |
| `maintainer` | 插件的维护者 |
| `capabilities` | 明确列出的工具、钩子、中间件及所需的环境变量 |
| `requires_hermes` | 最低 Hermes 版本要求，例如 `>=0.19`（可选） |
| `platforms` | 操作系统限制，留空表示兼容所有系统（可选） |
| `docs_url` | 外部文档链接（可选） |

## 信任机制

该目录的设计旨在让使用者清晰了解自己正在安装的内容：

- **人工审核的收录流程。** 每个条目（以及每一次固定版本更新）都必须通过维护人员审核的拉取请求才能被纳入。没有任何内容会自动进入目录。
- **精确的 SHA 固定版本。** 条目固定的是特定的提交版本，而非分支。插件开发者向其仓库推送新代码时，不会改变目录中的安装内容——若需更新固定版本，必须再次提交经过审核的拉取请求。
- **能力声明机制。** 条目会明确说明插件提供的工具、钩子及中间件，以及它所需的环境变量（如 API 密钥等），这样你便能在安装前了解其可能产生的影响范围。
- **已移除列表。** 从目录中移除的插件（例如在发生安全事件后）会被记录在 `plugin-catalog/removed.yaml` 文件中，其中会注明移除原因和日期。安装程序会拒绝安装列表中的任何插件。
- **已安装 ≠ 已启用。** 将目录中的插件安装到磁盘上仅代表其已被存储；与普通插件一样，它仍需在加载前被启用。详情请参阅 [插件 → 启用与禁用](plugins.md)。

:::warning 目录审核仅为特定时间点的检查
目录条目仅表示相关固定版本已由人工审核，能力声明也已过检查，且该仓库满足提交标准。这并非安全审计，也无法反映同一仓库中的其他提交内容。请务必仔细审查任何被授予权限的代码。
:::

## 从目录安装插件

```bash
# Install a reviewed catalog entry by name (checks out the pinned SHA)
hermes plugins install <name>

# Then enable it, as with any plugin
hermes plugins enable <name>
```

在开始克隆任何内容之前，安装提示会先显示该条目的功能概要——包括已声明的工具、钩子以及所需的环境变量。

### 更新目录中的插件安装

对于通过目录安装的插件，`hermes plugins update <name>` 命令不会执行 `git pull` 操作。它会将您已安装的版本号与当前目录中的版本号进行比对；如果目录内容因经过审核的 Pull Request 而发生变更，该命令会使用新的 SHA 值强制重新安装插件。同时，您之前设置的启用/禁用状态也会被保留。`hermes plugins list` 命令会将目录中的插件显示为 `catalog:<tier>@<sha>` 的格式，从而让您一目了然地了解其来源。

### 未收录在目录中的插件名称

如果仅提供并非目录条目的纯名称，则会引发错误——因为不存在第二个未经审核的名称索引。对于此类插件，您可以通过 `owner/repo` 格式或 Git 地址来安装（即自定义源码，详见下文），或者将其提交到目录中。

### 实时更新机制

文档构建过程会将目录内容以单个 JSON 文件的形式发布出来（地址为 `https://hermes-agent.nousresearch.com/docs/api/plugin-catalog.json`）。`search`/`install`/`update` 命令最多每六小时获取一次该文件，并将其缓存于 `~/.hermes/cache/` 目录下。这样一来，即使目录中有新条目添加或旧条目删除，也不需要更新 Hermes 本身，已安装的客户端就能及时获得最新信息。在离线状态下，则会使用随项目一起下载的缓存副本。无论是在内置列表中还是实时列表中，条目的删除操作都会被严格执行。

### 自定义 Git 地址的情况

虽然 `hermes plugins install <git-url>` 仍然适用于任何仓库，但它会完全绕过目录系统。

- **无审核模式**——您将直接获取分支尖端上的代码，而非经过审核的固定版本。  
- 系统会显示警告标识，以明确提示该代码尚未经过验证。  
- 虽然已移除，但相关列表仍会被查询（若为已知有问题的仓库，将通过 URL 直接拒绝访问）。

对于您自己信任的插件和仓库，请使用 git URL 路径；而用于搜索发现的插件则应通过目录来查找。

## 向插件目录提交插件

提交方式是通过拉取请求添加一个 `plugin-catalog/<名称>.yaml` 文件。完整的检查清单可见于
[plugin-catalog README](https://github.com/NousResearch/hermes-agent/tree/main/plugin-catalog)；简而言之，一个有效的条目需满足以下条件：

1. **由所有者提交**——拉取请求的发起者拥有或负责维护该插件仓库。  
2. **为公开仓库**——其 `repo` URL 可被公开克隆。  
3. **已发布版本**——该仓库存在实际的发布版本/标签，而不仅仅是默认分支。  
4. **通过验证**——PR 上的目录验证 GitHub Action 指示为绿色（即格式、SHA 格式及可访问性均符合要求）。  
5. **固定为稳定代码**——被固定的 SHA 值至少已有**2周历史**，这样目录就不会指向刚刚在审核前推送的代码。

更新固定版本（即将 `sha` 更改为更新的提交版本）也需遵循相同的 PR + 审核流程。

## 相关内容

- [插件](plugins.md)——插件系统本身：清单格式、启用方式及配置选项  
- [内置插件](built-in-plugins.md)——Hermes 自带的插件  
- [构建 Hermes 插件](/developer-guide/plugins)——自行编写插件  
- [插件目录页面](/plugins)——可浏览的插件目录
