# GitHub REST API 快速参考手册

基础网址：`https://api.github.com`

所有请求均需添加以下头部信息：`-H "Authorization: token $GITHUB_TOKEN"`

可使用 `gh-env.sh` 辅助工具自动设置 `$GITHUB_TOKEN`、`$
```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
```

## 仓库

| 操作 | 方法 | 接口地址 |
|------|------|----------|
| 获取仓库信息 | GET | `/repos/{owner}/{repo}` |
| 创建用户仓库 | POST | `/user/repos` |
| 创建组织仓库 | POST | `/orgs/{org}/repos` |
| 更新仓库 | PATCH | `/repos/{owner}/{repo}` |
| 删除仓库 | DELETE | `/repos/{owner}/{repo}` |
| 列出个人仓库 | GET | `/user/repos?per_page=30&sort=updated` |
| 列出组织仓库 | GET | `/orgs/{org}/repos` |
| 复制仓库 | POST | `/repos/{owner}/{repo}/forks` |
| 根据模板创建仓库 | POST | `/repos/{owner}/{template}/generate` |
| 获取标签 | GET | `/repos/{owner}/{repo}/topics` |
| 设置标签 | PUT | `/repos/{owner}/{repo}/topics` |

## 合并请求

| 操作 | 方法 | 接口地址 |
|------|------|----------|
| 列出合并请求 | GET | `/repos/{owner}/{repo}/pulls?state=open` |
| 创建合并请求 | POST | `/repos/{owner}/{repo}/pulls` |
| 获取合并请求详情 | GET | `/repos/{owner}/{repo}/pulls/{number}` |
| 更新合并请求 | PATCH | `/repos/{owner}/{repo}/pulls/{number}` |
| 列出合并请求中的文件 | GET | `/repos/{owner}/{repo}/pulls/{number}/files` |
| 合并合并请求 | PUT | `/repos/{owner}/{repo}/pulls/{number}/merge` |
| 请求审阅者 | POST | `/repos/{owner}/{repo}/pulls/{number}/requested_reviewers` |
| 创建审阅记录 | POST | `/repos/{owner}/{repo}/pulls/{number}/reviews` |
| 线上评论 | POST | `/repos/{owner}/{repo}/pulls/{number}/comments` |

### 合并请求合并内容

```json
{"merge_method": "squash", "commit_title": "feat: description (#N)"}
```

合并方式：`"merge"`、`"squash"`、`"rebase"`

### PR 审核事件

`"APPROVE"`、`"REQUEST_CHANGES"`、`"COMMENT"`

## 问题

| 操作 | 方法 | 接口地址 |
|------|------|----------|
| 列出问题 | GET | `/repos/{owner}/{repo}/issues?state=open` |
| 创建问题 | POST | `/repos/{owner}/{repo}/issues` |
| 获取问题详情 | GET | `/repos/{owner}/{repo}/issues/{number}` |
| 更新问题 | PATCH | `/repos/{owner}/{repo}/issues/{number}` |
| 添加评论 | POST | `/repos/{owner}/{repo}/issues/{number}/comments` |
| 添加标签 | POST | `/repos/{owner}/{repo}/issues/{number}/labels` |
| 删除标签 | DELETE | `/repos/{owner}/{repo}/issues/{number}/labels/{name}` |
| 添加负责人 | POST | `/repos/{owner}/{repo}/issues/{number}/assignees` |
| 列出标签 | GET | `/repos/{owner}/{repo}/labels` |
| 搜索问题 | GET | `/search/issues?q={query}+repo:{owner}/{repo}` |

注意：Issues API 也会返回 PR。解析数据时请使用 `"pull_request" not in item` 进行过滤。

## CI / GitHub Actions

| 操作 | 方法 | 接口地址 |
|------|------|----------|
| 列出工作流 | GET | `/repos/{owner}/{repo}/actions/workflows` |
| 列出运行记录 | GET | `/repos/{owner}/{repo}/actions/runs?per_page=10` |
| 按分支列出运行记录 | GET | `/repos/{owner}/{repo}/actions/runs?branch={branch}` |
| 获取运行记录详情 | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}` |
| 下载日志 | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/logs` |
| 重新运行 | POST | `/repos/{owner}/{repo}/actions/runs/{run_id}/rerun` |
| 重新运行失败的作业 | POST | `/repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs` |
| 触发工作流执行 | POST | `/repos/{owner}/{repo}/actions/workflows/{id}/dispatches` |
| 获取提交状态 | GET | `/repos/{owner}/{repo}/commits/{sha}/status` |
| 检查运行结果 | GET | `/repos/{owner}/{repo}/commits/{sha}/check-runs` |

## 发布版本

| 操作 | 方法 | 接口地址 |
|------|------|----------|
| 列出发布版本 | GET | `/repos/{owner}/{repo}/releases` |
| 创建发布版本 | POST | `/repos/{owner}/{repo}/releases` |
| 获取发布版本详情 | GET | `/repos/{owner}/{repo}/releases/{id}` |
| 删除发布版本 | DELETE | `/repos/{owner}/{repo}/releases/{id}` |
| 上传资源文件 | POST | `https://uploads.github.com/repos/{owner}/{repo}/releases/{id}/assets?name={filename}` |

## 密钥

| 操作 | 方法 | 接口地址 |
|------|------|----------|
| 列出密钥 | GET | `/repos/{owner}/{repo}/actions/secrets` |
| 获取公钥 | GET | `/repos/{owner}/{repo}/actions/secrets/public-key` |
| 设置密钥 | PUT | `/repos/{owner}/{repo}/actions/secrets/{name}` |
| 删除密钥 | DELETE | `/repos/{owner}/{repo}/actions/secrets/{name}` |

## 分支保护规则

| 操作 | 方法 | 接口地址 |
|------|------|----------|
| 获取分支保护规则 | GET | `/repos/{owner}/{repo}/branches/{branch}/protection` |
| 设置分支保护规则 | PUT | `/repos/{owner}/{repo}/branches/{branch}/protection` |
| 删除分支保护规则 | DELETE | `/repos/{owner}/{repo}/branches/{branch}/protection` |

## 用户/认证

| 操作 | 方法 | 接口地址 |
|------|------|----------|
| 获取当前用户信息 | GET | `/user` |
| 列出用户的所有仓库 | GET | `/user/repos` |
| 列出用户的 Gist 内容 | GET | `/gists` |
| 创建 Gist | POST | `/gists` |
| 搜索仓库 | GET | `/search/repositories?q={query}` |

## 分页说明

大多数列表接口支持以下分页参数：
- `?per_page=100`（最多显示 100 条记录）
- `?page=2` 用于跳转至下一页
| 可通过查看 `Link` 请求头中的 `rel="next"` 字段获取下一页地址 |

## 请求频率限制

- 已认证用户：每小时 5,000 次请求
- 查询剩余请求次数：`curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit`

## 常用的 curl 请求格式

```bash
# GET
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO

# POST with JSON body
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues \
  -d '{"title": "...", "body": "..."}'

# PATCH (update)
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues/42 \
  -d '{"state": "closed"}'

# DELETE
curl -s -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues/42/labels/bug

# Parse JSON response with python3
curl -s ... | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['field'])"
```
