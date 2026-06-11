# GitHub 存档查询指南（BigQuery）

GitHub 存档将 GitHub 上的每一项公开事件以不可更改的 JSON 格式记录下来。这些数据可通过 Google BigQuery 访问，是进行取证分析最可靠的来源——一旦记录，这些事件便无法被删除或修改。

## 公开数据集

- **项目名称**：`githubarchive`
- **表格名称**：`day.YYYYMMDD`、`month.YYYYMM`、`year.YYYY`
- **成本**：每扫描 1 TiB 数据需支付 6.25 美元。建议始终先进行测试查询。
- **访问要求**：需要拥有已启用 BigQuery 功能的 Google Cloud 账户。免费套餐每月允许 1 TiB 的查询量。

---

## 12 种 GitHub 事件类型

| 事件类型 | 记录内容 | 取证价值 |
|----------|----------|----------|
| `PushEvent` | 推送到分支的提交记录 | 检测强制推送行为、确定提交时间线、识别提交者 |
| `PullRequestEvent` | PR 的创建、关闭、合并及重新打开操作 | 恢复已删除的 PR、追踪审查时间线 |
| `IssuesEvent` | 问题的创建、关闭、重新打开及标记操作 | 恢复已删除的问题、追踪社会工程学攻击痕迹 |
| `IssueCommentEvent` | 对问题及 PR 的评论记录 | 恢复已删除的评论、分析沟通模式 |
| `CreateEvent` | 分支、标签或仓库的创建记录 | 发现可疑的分支创建行为、判断标签创建时间 |
| `DeleteEvent` | 分支或标签的删除记录 | 作为账户被攻破后进行清理操作的证明 |
| `MemberEvent` | 合作成员的添加或移除记录 | 推断权限变更情况、识别访问权限升级行为 |
| `PublicEvent` | 仓库被设为公开状态 | 发现私有仓库意外泄露的情况 |
| `WatchEvent` | 用户将仓库加入关注列表的操作 | 分析攻击者的侦察行为模式 |
| `ForkEvent` | 仓库被 fork 的操作 | 发现攻击者在清理前窃取代码的行为 |
| `ReleaseEvent` | 版本的发布、编辑或删除记录 | 检测恶意版本注入行为、恢复已删除的版本 |
| `WorkflowRunEvent` | GitHub Actions 工作流的触发记录 | 识别 CI/CD 系统被滥用或未经授权的工作流运行情况 |

---

## 查询模板

### 基础模板：获取某个仓库的所有事件

```sql
SELECT
  created_at,
  type,
  actor.login,
  repo.name,
  payload
FROM
  `githubarchive.day.20240101`  -- Adjust date
WHERE
  repo.name = 'owner/repo'
  AND type IN ('PushEvent', 'DeleteEvent', 'MemberEvent')
ORDER BY
  created_at ASC
```

### 强制推送检测

强制推送会生成用于覆盖提交记录的PushEvent。关键识别指标如下：
- 当 `payload.distinct_size = 0` 且 `payload.size > 0` 时，说明提交记录已被删除
- `payload.before` 中包含重写前的SHA值（可据此恢复数据）

```sql
SELECT
  created_at,
  actor.login,
  JSON_EXTRACT_SCALAR(payload, '$.before') AS before_sha,
  JSON_EXTRACT_SCALAR(payload, '$.head') AS after_sha,
  JSON_EXTRACT_SCALAR(payload, '$.size') AS total_commits,
  JSON_EXTRACT_SCALAR(payload, '$.distinct_size') AS distinct_commits,
  JSON_EXTRACT_SCALAR(payload, '$.ref') AS branch_ref
FROM
  `githubarchive.month.*`
WHERE
  _TABLE_SUFFIX BETWEEN '202401' AND '202403'
  AND type = 'PushEvent'
  AND repo.name = 'owner/repo'
  AND CAST(JSON_EXTRACT_SCALAR(payload, '$.distinct_size') AS INT64) = 0
ORDER BY
  created_at ASC
```

### 已删除分支/标签检测

```sql
SELECT
  created_at,
  actor.login,
  JSON_EXTRACT_SCALAR(payload, '$.ref') AS deleted_ref,
  JSON_EXTRACT_SCALAR(payload, '$.ref_type') AS ref_type
FROM
  `githubarchive.month.*`
WHERE
  _TABLE_SUFFIX BETWEEN '202401' AND '202403'
  AND type = 'DeleteEvent'
  AND repo.name = 'owner/repo'
ORDER BY
  created_at ASC
```

### 合作伙伴权限变更

```sql
SELECT
  created_at,
  actor.login,
  JSON_EXTRACT_SCALAR(payload, '$.action') AS action,
  JSON_EXTRACT_SCALAR(payload, '$.member.login') AS member
FROM
  `githubarchive.month.*`
WHERE
  _TABLE_SUFFIX BETWEEN '202401' AND '202403'
  AND type = 'MemberEvent'
  AND repo.name = 'owner/repo'
ORDER BY
  created_at ASC
```

### CI/CD 工作流活动

```sql
SELECT
  created_at,
  actor.login,
  JSON_EXTRACT_SCALAR(payload, '$.action') AS action,
  JSON_EXTRACT_SCALAR(payload, '$.workflow_run.name') AS workflow_name,
  JSON_EXTRACT_SCALAR(payload, '$.workflow_run.conclusion') AS conclusion,
  JSON_EXTRACT_SCALAR(payload, '$.workflow_run.head_sha') AS head_sha
FROM
  `githubarchive.month.*`
WHERE
  _TABLE_SUFFIX BETWEEN '202401' AND '202403'
  AND type = 'WorkflowRunEvent'
  AND repo.name = 'owner/repo'
ORDER BY
  created_at ASC
```

### 演员行为分析

```sql
SELECT
  type,
  COUNT(*) AS event_count,
  MIN(created_at) AS first_event,
  MAX(created_at) AS last_event
FROM
  `githubarchive.month.*`
WHERE
  _TABLE_SUFFIX BETWEEN '202301' AND '202412'
  AND actor.login = 'suspicious-username'
GROUP BY type
ORDER BY event_count DESC
```

## 成本优化（强制要求）

1. **始终先进行试运行**：在执行 `bq query` 命令时添加 `--dry_run` 参数，以便在执行前查看预计的扫描字节数。
2. **使用 `_TABLE_SUFFIX`**：尽可能缩小时间范围。对于较短的时间段，`day.*` 类型的表成本最低；而对于较长的时间跨度，则适合使用 `month.*` 类型的表。
3. **仅选择所需列**：避免使用 `SELECT *`。`payload` 列体积较大，应仅选择特定的 JSON 路径。
4. **添加 LIMIT 限制**：在探索性查询时使用 `LIMIT 1000`。仅在最终需要执行全面查询时才移除该限制。
5. **在 WHERE 子句中进行列过滤**：在提取 `payload` 数据之前，先对已建立索引的列（如 `type`、`repo.name`、`actor.login`）进行过滤。

**成本估算**：未经压缩的 GH Archive 数据中，一个月的数据量约为 1-2 TiB。使用 `_TABLE_SUFFIX` 查询特定的仓库及事件类型时，通常的扫描数据量为 1-10 GiB，对应费用为 0.006 美元至 0.06 美元。

---

## 通过 Hermes 进行访问

**选项 A：BigQuery CLI**（前提是已安装 `gcloud`）
```bash
bq query --use_legacy_sql=false --format=json "YOUR QUERY"
```

**选项 B：Python**（通过 `execute_code` 实现）
```python
from google.cloud import bigquery
client = bigquery.Client()
query = "YOUR QUERY"
results = client.query(query).result()
for row in results:
    print(dict(row))
```

**选项 C：无 GCP 凭证可用**  
如果无法使用 BigQuery，请在报告中记录此限制。此时可选用其他 4 种调查工具（Git、GitHub API、Wayback Machine 以及 IOC 信息丰富工具）——即便没有 BigQuery，这些工具也能满足大部分调查需求。
