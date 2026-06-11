# 网站

本网站采用现代化的静态网站生成器 [Docusaurus](https://docusaurus.io/) 构建而成。  

## 安装

```bash
yarn
```

## 本地开发

```bash
yarn start
```

该命令会启动一个本地开发服务器并打开一个浏览器窗口。大多数更改都会实时反映出来，无需重新启动服务器即可看到效果。

## 构建

```bash
yarn build
```

该命令会将静态内容生成到 `build` 目录中，随后可通过任何静态内容托管服务来提供这些内容。

## 部署方式

通过 SSH：

```bash
USE_SSH=true yarn deploy
```

未使用 SSH：

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

如果您使用 GitHub Pages 作为托管平台，该命令是构建网站并将其推送到 `gh-pages` 分支的便捷方式。

## 图表格式检查

在持续集成流程中，系统会运行 `ascii-guard` 工具来检查文档中的 ASCII 方框图格式。为避免集成失败，请使用 Mermaid（````mermaid````）语法或普通的列表/表格，而非 ASCII 方框图。
