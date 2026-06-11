# 已删除内容的恢复方法

## 核心原理：GitHub从不会彻底删除强制推送的提交记录

虽然强制推送的提交记录会被从分支历史中移除，但它们仍会保留在GitHub的服务器上，直到垃圾回收机制启动（这一过程可能需要数周甚至数月）。这正是恢复已删除提交记录的依据。

---

## 方法1：直接使用GitHub链接（最快——无需身份验证）

如果您拥有该提交的SHA值，即便它已被从分支中强制推送，依然可以直接访问该提交内容：

```bash
# View commit metadata
curl -s "https://github.com/OWNER/REPO/commit/SHA"

# Download as patch (includes full diff)
curl -s "https://github.com/OWNER/REPO/commit/SHA.patch" > recovered_commit.patch

# Download as diff
curl -s "https://github.com/OWNER/REPO/commit/SHA.diff" > recovered_commit.diff

# Example (Istio credential leak - real incident):
curl -s "https://github.com/istio/istio/commit/FORCE_PUSHED_SHA.patch"
```

**适用场景**：已知对象的 SHA 值（可通过 GitHub 存档、Wayback Machine 或 `git fsck` 获取）  
**失败场景**：GitHub 已对该对象进行垃圾回收处理（较为罕见，通常发生在强制推送后的 30–90 天内）  

---

## 方法 2：GitHub REST API

```bash
# Works for commits force-pushed off branches but still on server
# Note: /commits/SHA may 404, but /git/commits/SHA often succeeds for orphaned commits
curl -s "https://api.github.com/repos/OWNER/REPO/git/commits/SHA" | jq .

# Get the tree (file listing) of a force-pushed commit
curl -s "https://api.github.com/repos/OWNER/REPO/git/trees/SHA?recursive=1" | jq .

# Get a specific file from a force-pushed commit
curl -s "https://api.github.com/repos/OWNER/REPO/contents/PATH?ref=SHA" | jq .content | base64 -d
```

## 方法 3：通过 SHA 值获取 Git 内容（本地操作——需先克隆）

```bash
# Fetch an orphaned commit directly by SHA into local repo
cd target_repo
git fetch origin SHA
git log FETCH_HEAD -1   # view the commit
git diff FETCH_HEAD~1 FETCH_HEAD  # view the diff

# If the SHA was recently force-pushed it will still be fetchable
# This stops working once GitHub GC runs
```

## 方法 4：使用 git fsck 检测悬空提交

```bash
cd target_repo

# Find all unreachable objects (includes force-pushed commits)
git fsck --unreachable --no-reflogs 2>&1 | grep "unreachable commit" | awk '{print $3}' > dangling_shas.txt

# For each dangling commit, get its metadata
while read sha; do
  echo "=== $sha ===" >> dangling_details.txt
  git show --stat "$sha" >> dangling_details.txt 2>&1
done < dangling_shas.txt

# Note: dangling objects only exist in LOCAL clone — not the same as GitHub's copies
# GitHub's copies are accessible via Methods 1-3 until GC runs
```

## 恢复已删除的 GitHub 问题与 Pull Request

### 通过 Wayback Machine CDX API 实现

```bash
# Find all archived snapshots of a specific issue
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/issues/NUMBER&output=json&limit=50&fl=timestamp,statuscode,original" | python3 -m json.tool

# Fetch the best snapshot
# Use the timestamp from the CDX result:
# https://web.archive.org/web/TIMESTAMP/https://github.com/OWNER/REPO/issues/NUMBER
curl -s "https://web.archive.org/web/TIMESTAMP/https://github.com/OWNER/REPO/issues/NUMBER" > issue_NUMBER_archived.html

# Find all snapshots of the repo in a date range
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO*&output=json&from=20240101&to=20240201&limit=200&fl=timestamp,urlkey,statuscode" | python3 -m json.tool
```

### 通过 GitHub API（功能受限——仅支持未删除的内容）

```bash
# Closed issues (not deleted) are retrievable
curl -s "https://api.github.com/repos/OWNER/REPO/issues?state=closed&per_page=100" | jq '.[].number'

# Note: DELETED issues/PRs do NOT appear in the API. Use Wayback Machine or GH Archive for those.
```

### 通过 GitHub 存档查看（仅适用于事件历史记录，而非内容本身）

```sql
-- Find all IssueEvents for a repo in a date range
SELECT created_at, actor.login, payload.action, payload.issue.number, payload.issue.title
FROM `githubarchive.day.*`
WHERE _TABLE_SUFFIX BETWEEN '20240101' AND '20240201'
  AND type = 'IssuesEvent'
  AND repo.name = 'OWNER/REPO'
ORDER BY created_at
```

## 从已知的提交记录中恢复被删除的文件

```bash
# If you have the commit SHA (even force-pushed):
git show SHA:path/to/file.py > recovered_file.py

# Or via API (base64 encoded content):
curl -s "https://api.github.com/repos/OWNER/REPO/contents/path/to/file.py?ref=SHA" | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
print(base64.b64decode(d['content']).decode())
"
```

## 证据记录

在恢复任何被删除的内容后，应立即对其进行记录：

```bash
python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json add \
  --source "git fetch origin FORCE_PUSHED_SHA" \
  --content "Recovered commit: FORCE_PUSHED_SHA | Author: attacker@example.com | Date: 2024-01-15 | Added file: malicious.sh" \
  --type git \
  --actor "attacker-handle" \
  --url "https://github.com/OWNER/REPO/commit/FORCE_PUSHED_SHA.patch" \
  --timestamp "2024-01-15T00:00:00Z" \
  --verification single_source \
  --notes "Commit force-pushed off main branch on 2024-01-16. Recovered via direct fetch."
```

## 恢复失败模式

| 失败情况 | 原因 | 解决方案 |
|---------|-------|----------|
| `git fetch origin SHA` 返回 “not our ref” | GitHub 已执行垃圾回收操作 | 尝试方法 1/2，或通过互联网档案馆进行查询 |
| `github.com/OWNER/REPO/commit/SHA` 返回 404 错误 | 已执行垃圾回收或 SHA 值有误 | 通过 GH Archive 验证 SHA 值；尝试使用部分 SHA 值进行搜索 |
| 互联网档案馆中没有相关快照 | 该页面从未被互联网爬虫抓取过 | 查看 `commoncrawl.org`，或查询 Google 缓存 |
| BigQuery 显示事件记录但无实际内容 | GH Archive 仅存储事件元数据，而非文件内容 | 恢复操作仅能证明该事件曾发生，无法显示具体内容 |
