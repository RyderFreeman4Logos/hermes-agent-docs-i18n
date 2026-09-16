---
title: "Github — GitHub via gh CLI: PRs, issues, reviews, repos, auth"
sidebar_label: "Github"
description: "GitHub via gh CLI: PRs, issues, reviews, repos, auth"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# GitHub

通过 gh CLI 操作 GitHub：处理 Pull Request、问题报告、代码审查、仓库管理以及身份认证等功能。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/software-development\github` |
| 版本 | `2.0.0` |
| 开发者 | Ben Barclay (benbarclay)，Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `github`、`gh`、`git`、`pull-requests`、`issues`、`code-review`、`repos`、`auth`、`ci` |
| 相关技能 | [`codebase-inspection`](/docs/user-guide/skills/bundled/software-development/software-development-codebase-inspection)、[`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，Agent 就会依据这些内容来执行操作。
:::

# GitHub

使用 `gh` CLI 对 GitHub 进行端到端操作（必要时会采用 REST 接口作为备用）：包括身份认证、问题处理、Pull Request 全生命周期管理、问题转接为 Pull Request、代码审查以及仓库管理等功能。该技能整合了之前的六个独立技能；每个工作流程的完整说明都保存在对应的参考文件中——在开始执行某个工作流程之前，请务必先阅读相应的参考文件，下方的内容仅用于路由引导。

## 路由规则

| 任务 | 首先阅读的文档 |
|---|---|
| 认证失败 / 新机器设置 / 令牌或SSH配置 / gh登录 | `references/auth.md` |
| 创建、分类、标记、分配及关闭问题 | `references/issues.md` |
| 分支管理、提交代码、创建PR、监控CI流程、合并代码 | `references/pr-workflow.md` |
| 将问题转化为已验证的PR（完整交付流程） | `references/issue-to-pr.md` |
| 审核他人的PR：代码差异对比、内联评论及审核结论 | `references/code-review.md` |
| 克隆/创建/复制仓库、远程仓库及版本发布 | `references/repo-management.md` |

辅助资源包括：`scripts/gh-env.sh` 和 `scripts/git-credential-token.py`（认证辅助工具）、`templates/` 目录中的PR正文模板、错误报告模板及功能请求模板，以及 `references/ci-troubleshooting.md`、`references/conventional-commits.md`、`references/github-api-cheatsheet.md`、`references.review-output-template.md`。

## 核心规范（适用于所有工作流程）

- 每次会话开始前先执行一次预检：`gh auth status` —— 若检测失败，请首先查阅 `references/auth.md`。
- 尽量使用 `gh` 命令而非原始REST接口；仅在没有对应命令时才使用 `gh api`，相关接口列表可在速查手册中找到。
- 未经亲自检查 `gh pr checks` 的结果，切勿声称CI测试已通过；未核实 `state,mergedAt` 状态，也切勿宣称PR已被合并。
- 写作前务必了解完整背景信息：使用 `gh issue view --comments` / `gh pr view --comments` 查看相关讨论——决策内容通常体现在回复中，而非标题里。
- 在创建任何内容之前，先检查是否存在重复项：使用 `gh pr list --search` / `gh issue list --search` 进行检索。

## 验证流程

- 工作流自身的参考文件决定了该任务的完成状态。  
- 跨领域应用：所有关于远程状态（CI、合并、发布以及问题状态）的判断均基于最新的 `gh` 数据读取结果，而非内存中的旧数据。
